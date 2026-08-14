# SPDX-License-Identifier: Apache-2.0
"""The walled shell every box type starts from, and how solids get placed.

Each box type used to carry its own copy of `outer - inner`, which meant the
hollowing rule lived in thirteen places. It lives here instead, and it takes one
decision with it: a box is only hollowed out wholesale when nothing else is
going to define its cavities. As soon as a box has compartments, the interior
stays solid and the compartments are what get carved out of it — otherwise the
individual wells (a slot per worker, say) would be lost inside one big void.

`block` and `corner` live here too. Every pybosl2 primitive is **centre**-
anchored — `cuboid([10, 20, 5])` spans -5..5 by -10..10 by -2.5..2.5 — while box
geometry is naturally written in corner coordinates ("the floor is `ft` thick,
so the interior starts at z = ft"). These two helpers do that conversion once,
so no caller has to remember to add half a size.
"""

from __future__ import annotations

from typing import Sequence, TYPE_CHECKING

from pyboxbuilder.compartments.finger_hole import (
    DEFAULT_MOUTH_ROUNDING_MM as DEFAULT_MOUTH_ROUNDING,
)
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import (
    default_rounding,
    round_edges,
    vertical_and_bottom_edges,
)

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def corner(
    solid: "Bosl2Solid",
    size: Sequence[float],
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> "Bosl2Solid":
    """Place a centre-anchored solid so its minimum corner sits at `at`.

    Args:
        solid: A centre-anchored solid, as every pybosl2 primitive is.
        size: The solid's (width, length, height).
        at: Where its minimum corner should end up.
    """
    return solid.translate([
        at[0] + size[0] / 2,
        at[1] + size[1] / 2,
        at[2] + size[2] / 2,
    ])


def block(
    size: Sequence[float], at: Sequence[float] = (0.0, 0.0, 0.0)
) -> "Bosl2Solid":
    """A cuboid of `size` whose minimum corner sits at `at`."""
    from pybosl2 import cuboid

    return corner(cuboid(list(size)), size, at)


def build_shell(spec: dict) -> "Bosl2Solid":
    """Outer block, hollowed to the interior unless `spec["hollow"]` is False.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `floor_thickness` and `hollow` (default True).

    Returns:
        The box body before any type-specific lid features are added.
    """
    size = [spec["width"], spec["length"], spec["height"]]
    outer = block(size)

    # Round what a hand grips: the vertical corners and the base always, and the
    # top rim too when nothing has to mate with it. On a lidded box the rim is a
    # sealing surface, so its rounding lives on the lid instead — the closed box
    # still reads as rounded top, sides and bottom (FR-043/FR-044).
    radius = body_rounding(spec)
    if radius > 0:
        edges = vertical_and_bottom_edges()
        if spec.get("rim_free"):
            edges = edges + [_top_anchor()]
        outer = round_edges(outer, size, radius, edges)

    if spec.get("hollow", True):
        outer = outer - interior_block(spec)
    return apply_finger_holes(outer, spec)


def body_rounding(spec: dict) -> float:
    """The edge radius for this box body.

    Args:
        spec: Reads `rounding`; falls back to half the wall thickness.

    Returns:
        The radius in mm. ``0`` disables rounding entirely.
    """
    explicit = spec.get("rounding")
    if explicit is not None:
        return max(0.0, float(explicit))
    return default_rounding(spec.get("wall_thickness", 2.0))


def _top_anchor():
    """The TOP anchor, imported lazily so this module has no import-time pybosl2."""
    from pybosl2 import Anchor

    return Anchor.TOP


def apply_finger_holes(body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
    """Cut any exterior finger holes out of a box body (FR-006).

    A hole on the outside of a box is the same cut as a compartment's wall
    scoop — a bore with a mouth flared into the rim and a fillet where it
    emerges on each face — so it goes through the same builder rather than a
    second implementation that could drift from it.

    Following the original (``no_lid.scad``), each hole hangs from the top of
    the **interior** rather than rising from the floor, and its height is
    capped at the interior depth so the cut cannot reach the box's base.

    Args:
        body: The box body to cut.
        spec: Reads `finger_holes` (a sequence of finger-hole builders), plus
              `width`, `length`, `height`, `wall_thickness`, `floor_thickness`.

    Returns:
        The body with every hole subtracted; unchanged when there are none.
    """
    holes = spec.get("finger_holes") or ()
    if not holes:
        return body

    from pyboxbuilder.compartments.finger_hole import build_wall_scoop

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    inner_width = spec["width"] - 2 * wt
    inner_length = spec["length"] - 2 * wt

    # Align to the top of the *inside*, not the outer rim. On a lidded box the
    # lid (or its track) occupies the band above the interior, so a hole hung
    # from the rim starts inside solid material and reads as a nick in the top
    # edge rather than as a cut into the well. A type whose body is already
    # shortened for its lid — cap, slipover — says so with `interior_top`.
    interior_top = spec.get("interior_top")
    if interior_top is None:
        lid_band = 0.0 if spec.get("rim_free") else spec.get("lid_thickness", 0.0)
        interior_top = spec["height"] - lid_band
    interior_height = interior_top - ft

    for hole in holes:
        radius = getattr(hole, "radius", 14.0)
        # The cut's height follows the finger unless told otherwise, and never
        # reaches deeper than the interior.
        reach = min(getattr(hole, "depth", None) or radius, interior_height)
        scoop = build_wall_scoop(
            inner_width, inner_length, reach, hole.side,
            radius=radius,
            wall_thickness=wt,
            rounding_radius=getattr(hole, "rounding_radius", None)
            if getattr(hole, "rounding_radius", None) is not None
            else DEFAULT_MOUTH_ROUNDING,
            rounding_edge=getattr(hole, "rounding_edge", None),
        )
        offset = getattr(hole, "offset", 0.0) or 0.0
        along_x = hole.side in (ScoopSide.FRONT, ScoopSide.BACK)
        body = body - scoop.translate([
            wt + (offset if along_x else 0.0),
            wt + (0.0 if along_x else offset),
            interior_top - reach,
        ])

    return body


def interior_block(spec: dict) -> "Bosl2Solid":
    """The solid that `build_shell` removes — the box's full interior volume.

    The void's **bottom edges are rounded**, which is what leaves a fillet
    inside the box: a void slightly smaller where it meets the floor means the
    wall rises from the floor on a curve rather than a right angle, so nothing
    snags and nothing has to be dug out of a square internal corner (FR-043).

    The void's vertical corners deliberately stay square. Rounding them too is
    tempting — it is one more `edges=` entry — but the resulting fillets run the
    **full height** of the box, including the band where a sliding lid seats,
    and they add material exactly where the plate needs to pass: measured, it
    put 0.59mm³ of body into the lid on all three sliding types, which is a lid
    that jams. The top likewise stays square: it is the opening.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `floor_thickness` and `rounding`.

    Returns:
        The interior volume, positioned in the box frame.
    """
    from pybosl2 import Anchor, cuboid

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    size = [spec["width"] - 2 * wt, spec["length"] - 2 * wt, spec["height"] - ft]

    radius = body_rounding(spec)
    if radius <= 0 or radius >= min(size) / 2:
        return block(size, at=(wt, wt, ft))

    return corner(
        cuboid(size, rounding=radius, edges=Anchor.BOTTOM, **precision_kwargs()),
        size,
        (wt, wt, ft),
    )
