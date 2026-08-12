# SPDX-License-Identifier: Apache-2.0
"""Pattern fill — hex grid, grid, voronoi through-hole generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_driven.enums import PatternType

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


def build_pattern(
    width: float,
    length: float,
    thickness: float,
    pattern_type: PatternType,
    spacing: float | None = None,
) -> "Bosl2Solid":
    """Build a through-hole pattern solid for a lid.

    Args:
        width: Lid width in mm.
        length: Lid length in mm.
        thickness: Lid thickness (controls hole depth).
        pattern_type: Hex grid, grid, or voronoi.
        spacing: Distance between pattern elements. Auto-calculated if None.

    Returns:
        A Bosl2Solid representing the through-hole cutouts.
    """
    if spacing is None:
        spacing = max(min(width, length) / 8, 5.0)

    if pattern_type == PatternType.HEX_GRID:
        return _hex_grid_fill(width, length, thickness, spacing)
    elif pattern_type == PatternType.GRID:
        return _grid_fill(width, length, thickness, spacing)
    elif pattern_type == PatternType.VORONOI:
        return _voronoi_fill(width, length, thickness, spacing)
    else:
        return _grid_fill(width, length, thickness, spacing)


def _hex_grid_fill(
    width: float, length: float, thickness: float, spacing: float
) -> "Bosl2Solid":
    """Hexagonal grid through-holes."""
    from bosl2 import prismoid, cube as native_cube

    try:
        from bosl2 import cuboid
    except ImportError:
        from bosl2 import cube as cuboid

    holes = None
    hex_r = spacing / 2
    row_h = hex_r * 1.5

    x_count = int(width / spacing) + 2
    y_count = int(length / row_h) + 2

    for xi in range(x_count):
        x_offset = 0 if xi % 2 == 0 else spacing / 2
        for yi in range(y_count):
            cx = xi * spacing
            cy = yi * row_h + x_offset
            if cx < 0 or cx > width or cy < 0 or cy > length:
                continue
            # Simple cube as hex approximation
            hole = cuboid([hex_r, hex_r, thickness * 1.2])
            hole = hole.translate([cx, cy, -0.1])
            if holes is None:
                holes = hole
            else:
                holes = holes + hole

    return holes or cuboid([1, 1, 1])


def _grid_fill(
    width: float, length: float, thickness: float, spacing: float
) -> "Bosl2Solid":
    """Grid (square) through-holes."""
    from bosl2 import cuboid

    holes = None
    hole_size = spacing * 0.4
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1

    for xi in range(x_count):
        cx = xi * spacing
        if cx + hole_size > width:
            continue
        for yi in range(y_count):
            cy = yi * spacing
            if cy + hole_size > length:
                continue
            hole = cuboid([hole_size, hole_size, thickness * 1.2])
            hole = hole.translate([cx, cy, -0.1])
            if holes is None:
                holes = hole
            else:
                holes = holes + hole

    return holes or cuboid([1, 1, 1])


def _voronoi_fill(
    width: float, length: float, thickness: float, spacing: float
) -> "Bosl2Solid":
    """Voronoi cell through-holes — approximated as irregular polygons."""
    # Simplified: random offset grid gives voronoi-like appearance
    from bosl2 import cuboid
    import random

    holes = None
    rng = random.Random(42)  # deterministic seed
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    hole_size = spacing * 0.35

    for xi in range(x_count):
        for yi in range(y_count):
            cx = xi * spacing + rng.uniform(-spacing * 0.2, spacing * 0.2)
            cy = yi * spacing + rng.uniform(-spacing * 0.2, spacing * 0.2)
            if cx < 0 or cx + hole_size > width:
                continue
            if cy < 0 or cy + hole_size > length:
                continue
            hole = cuboid([hole_size, hole_size, thickness * 1.2])
            hole = hole.translate([cx, cy, -0.1])
            if holes is None:
                holes = hole
            else:
                holes = holes + hole

    return holes or cuboid([1, 1, 1])
