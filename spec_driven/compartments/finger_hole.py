# SPDX-License-Identifier: Apache-2.0
"""Finger scoop and notch geometry for compartment walls and floors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_driven.enums import ScoopSide

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
) -> "Bosl2Solid":
    """Build a finger scoop (notch) on a compartment wall.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth.
        side: Which wall to cut the scoop into.
        radius: Scoop radius in mm.

    Returns:
        Bosl2Solid cutout to subtract from the compartment.
    """
    from pybosl2 import cuboid, cylinder

    scoop_depth = radius * 0.7  # How deep into the wall

    if side == ScoopSide.FRONT:
        scoop = cylinder(height=comp_width * 0.4, radius=radius)
        scoop = scoop.rotate([90, 0, 0])
        scoop = scoop.translate([
            comp_width * 0.3, -scoop_depth, comp_depth - radius * 0.8,
        ])
    elif side == ScoopSide.BACK:
        scoop = cylinder(height=comp_width * 0.4, radius=radius)
        scoop = scoop.rotate([90, 0, 0])
        scoop = scoop.translate([
            comp_width * 0.3, comp_length + scoop_depth - radius,
            comp_depth - radius * 0.8,
        ])
    elif side == ScoopSide.LEFT:
        scoop = cylinder(height=comp_length * 0.4, radius=radius)
        scoop = scoop.rotate([0, 90, 0])
        scoop = scoop.translate([
            -scoop_depth, comp_length * 0.3, comp_depth - radius * 0.8,
        ])
    elif side == ScoopSide.RIGHT:
        scoop = cylinder(height=comp_length * 0.4, radius=radius)
        scoop = scoop.rotate([0, 90, 0])
        scoop = scoop.translate([
            comp_width + scoop_depth - radius,
            comp_length * 0.3,
            comp_depth - radius * 0.8,
        ])
    else:
        scoop = cuboid([1, 1, 1])

    return scoop


def build_floor_scoop(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 14.0,
) -> "Bosl2Solid":
    """Build a floor finger scoop for shallow compartments.

    Falls back to a wall notch if the compartment is too shallow.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which side the scoop is on.
        radius: Scoop radius.

    Returns:
        Bosl2Solid cutout.
    """
    from pybosl2 import cylinder, cuboid

    depth = 4.0  # Shallow floor scoop
    if side == ScoopSide.FRONT:
        scoop = cylinder(height=comp_width * 0.3, radius=radius)
        scoop = scoop.rotate([90, 0, 0])
        scoop = scoop.translate([
            comp_width * 0.35, comp_length * 0.15, -0.1,
        ])
    elif side == ScoopSide.BACK:
        scoop = cylinder(height=comp_width * 0.3, radius=radius)
        scoop = scoop.rotate([90, 0, 0])
        scoop = scoop.translate([
            comp_width * 0.35, comp_length * 0.85, -0.1,
        ])
    elif side == ScoopSide.LEFT:
        scoop = cylinder(height=comp_length * 0.3, radius=radius)
        scoop = scoop.rotate([0, 90, 0])
        scoop = scoop.translate([
            comp_width * 0.15, comp_length * 0.35, -0.1,
        ])
    else:
        scoop = cylinder(height=comp_length * 0.3, radius=radius)
        scoop = scoop.rotate([0, 90, 0])
        scoop = scoop.translate([
            comp_width * 0.85, comp_length * 0.35, -0.1,
        ])

    return scoop
