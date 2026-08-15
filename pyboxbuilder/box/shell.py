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
    return solid.translate(
        [
            at[0] + size[0] / 2,
            at[1] + size[1] / 2,
            at[2] + size[2] / 2,
        ]
    )


def block(size: Sequence[float], at: Sequence[float] = (0.0, 0.0, 0.0)) -> "Bosl2Solid":
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
    from pyboxbuilder.box.base import wall_top

    for hole in holes:
        # Per side: the four walls need not end level, and a hole aligned to
        # the wrong one either floats above its wall or cuts into a lid feature.
        interior_top = wall_top(spec, hole.side)
        interior_height = interior_top - ft
        radius = getattr(hole, "radius", 14.0)
        # The cut's height follows the finger unless told otherwise, and never
        # reaches deeper than the interior.
        reach = min(getattr(hole, "depth", None) or radius, interior_height)
        scoop = build_wall_scoop(
            inner_width,
            inner_length,
            reach,
            hole.side,
            radius=radius,
            wall_thickness=wt,
            # None lets r1 derive from the throat rather than pinning 3mm.
            rounding_radius=getattr(hole, "rounding_radius", None),
            rounding_edge=getattr(hole, "rounding_edge", None),
            # Anything above the interior — a lid band, a sliding track — is
            # material the hole must not cut into, so the outline's rim
            # overshoot is trimmed off there.
            top_limit=reach if interior_top < spec["height"] - 1e-9 else None,
        )
        offset = getattr(hole, "offset", 0.0) or 0.0
        along_x = hole.side in (ScoopSide.FRONT, ScoopSide.BACK)
        body = body - scoop.translate(
            [
                wt + (offset if along_x else 0.0),
                wt + (0.0 if along_x else offset),
                interior_top - reach,
            ]
        )

    return body


def no_lid_finger_holes(spec: dict):
    """The finger holes a no-lid box cuts into its longer walls (FR-047).

    An open tray is lifted by the rim, so the original (`no_lid.scad`) puts a
    finger dip into each wall of the longer dimension. The sizing is a formula
    on the spec, not a constant:

    - radius = `min(20, min(length, width) / 4, height - floor_thickness + 1)`;
    - height = `min(radius, height - default_floor_thickness + 1)` (2mm floor);
    - mouth rounding = 3mm.

    A wall too short for the hole's mouth is skipped: a finger hole wider than
    the wall it is cut through breaks into the adjoining walls, so the tray goes
    out with **no** hole rather than a broken one. That is what keeps a path box
    with a short side sound.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness` and
            `floor_thickness`.

    Returns:
        A tuple of `FingerHoleBuilder`s — one per longer wall — or an empty
        tuple when the holes would not fit.
    """
    from pyboxbuilder.builders._base import FingerHoleBuilder

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    width = spec["width"]
    length = spec["length"]
    height = spec["height"]

    radius = min(20.0, min(length, width) / 4.0, height - ft + 1.0)
    hole_height = max(min(radius, height - ft - wt - 1.0), 2)
    rounding_radius = 3.0

    if length >= width:
        sides = (ScoopSide.LEFT, ScoopSide.RIGHT)
        span = length - 2 * wt
    else:
        sides = (ScoopSide.FRONT, ScoopSide.BACK)
        span = width - 2 * wt

    # The mouth is `radius + rounding_radius` wide on each side of centre; the
    # two of them have to fit inside the wall the hole is cut through.
    if 2.0 * (radius + rounding_radius) > span:
        return ()

    return tuple(
        FingerHoleBuilder(
            side=side,
            radius=radius,
            depth=hole_height,
            rounding_radius=rounding_radius,
        )
        for side in sides
    )


def add_no_lid_finger_holes(spec: dict) -> None:
    """Give a no-lid spec its default finger holes, unless it already has some.

    Idempotent on the ``finger_holes`` key: an explicit ``finger_hole(side)``
    call on the builder wins, and a second call to this is a no-op. A spec that
    sets ``auto_finger_holes`` to ``False`` opts out entirely.
    """
    if spec.get("auto_finger_holes", True) and not spec.get("finger_holes"):
        spec["finger_holes"] = no_lid_finger_holes(spec)


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
