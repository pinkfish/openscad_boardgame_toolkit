# SPDX-License-Identifier: Apache-2.0
"""Finger scoop and notch geometry for compartment walls and floors.

Both helpers return cutouts in the compartment's own frame: (0, 0, 0) is the
compartment's lower-left corner at its floor, and the footprint runs out to
(comp_width, comp_length). pybosl2 primitives are centre-anchored, so the
translations below place a shape's centre.
"""

from __future__ import annotations

from pyboxbuilder.precision import kwargs as precision_kwargs

from typing import TYPE_CHECKING

from pyboxbuilder.enums import ScoopSide

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

MIN_WALL_SCOOP_DEPTH_MM = 8.0
"""Below this a wall notch has nothing to grip, so the floor scoop is used."""


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
) -> "Bosl2Solid":
    """Build a finger notch through a compartment wall.

    A vertical cylinder centred on the chosen edge, running from below the
    compartment floor to above its rim, so it cuts a rounded scallop through the
    wall and into the well — the same shape as the original `FingerHoleBase`.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth.
        side: Which wall to notch.
        radius: Notch radius in mm, capped so it cannot swallow the compartment.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.
    """
    from pybosl2 import cylinder

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    radius = min(radius, span / 2)

    # Run past both ends so the boolean leaves no skin at the floor or the rim.
    height = comp_depth + 2.0
    scoop = cylinder(height=height, radius=radius, **precision_kwargs())

    centre = {
        ScoopSide.FRONT: (comp_width / 2, 0.0),
        ScoopSide.BACK: (comp_width / 2, comp_length),
        ScoopSide.LEFT: (0.0, comp_length / 2),
        ScoopSide.RIGHT: (comp_width, comp_length / 2),
    }[side]

    return scoop.translate([centre[0], centre[1], comp_depth / 2])


def build_floor_scoop(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 14.0,
) -> "Bosl2Solid":
    """Build a bowl at the compartment floor, level with the chosen edge.

    Used where a wall notch would have nothing to bite into — a compartment only
    a few millimetres deep. The sphere rests *on* the floor rather than sinking
    below it, so the bowl scallops the wall and the edge of the well without ever
    breaching the box's base. This is the `sphere(r=..., anchor=BOTTOM)` idiom
    the original toolkit uses next to shallow tokens.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which edge the bowl sits against.
        radius: Sphere radius in mm, capped to half the compartment's span.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.
    """
    from pybosl2 import sphere

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    radius = min(radius, span / 2)

    centre = {
        ScoopSide.FRONT: (comp_width / 2, 0.0),
        ScoopSide.BACK: (comp_width / 2, comp_length),
        ScoopSide.LEFT: (0.0, comp_length / 2),
        ScoopSide.RIGHT: (comp_width, comp_length / 2),
    }[side]

    dish = sphere(radius=radius, **precision_kwargs())
    return dish.translate([centre[0], centre[1], radius])


def build_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
) -> "Bosl2Solid":
    """Pick the right scoop for the compartment's depth.

    Deep compartments get a wall notch; shallow ones fall back to a floor dish,
    because a notch in a 4 mm wall is not something a finger can use.
    """
    if comp_depth >= MIN_WALL_SCOOP_DEPTH_MM:
        return build_wall_scoop(comp_width, comp_length, comp_depth, side, radius)
    return build_floor_scoop(comp_width, comp_length, side, radius)
