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
    outer = block([spec["width"], spec["length"], spec["height"]])
    if not spec.get("hollow", True):
        return outer
    return outer - interior_block(spec)


def interior_block(spec: dict) -> "Bosl2Solid":
    """The solid that `build_shell` removes — the box's full interior volume."""
    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    return block(
        [spec["width"] - 2 * wt, spec["length"] - 2 * wt, spec["height"] - ft],
        at=(wt, wt, ft),
    )
