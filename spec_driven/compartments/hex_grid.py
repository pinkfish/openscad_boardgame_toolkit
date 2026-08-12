# SPDX-License-Identifier: Apache-2.0
"""Hex-grid compartment layout — hexagonal tile cutouts with push block and finger hole.

Ports the `HexGridWithCutouts` behaviour from the original toolkit. Layout math
is pure Python; geometry generation delegates to pybosl2.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

COS_30 = math.cos(math.radians(30))


@dataclass(frozen=True)
class HexGridSpec:
    """Configuration for a hex-grid compartment (FR-040)."""

    rows: int
    """Number of rows of hex cells."""
    cols: int
    """Number of columns of hex cells."""
    tile_width: float
    """Apothem-to-apothem width of each hex tile (mm)."""
    height: float
    """Depth of the hex cell cutouts (mm)."""
    spacing: float = 0.0
    """Gap between adjacent hex cells (mm)."""
    push_block_height: float = 0.0
    """Height of the raised central pillar; 0 = flat floor (FR-041)."""
    push_block_width: float = 15.0
    """Width of the raised pillar (apothem-to-apothem, mm)."""
    finger_hole_diameter: float = 0.0
    """Diameter of the floor finger hole; 0 = no finger hole (FR-042)."""

    @property
    def apothem(self) -> float:
        return self.tile_width / 2

    @property
    def circumradius(self) -> float:
        """Hex circumradius derived from the apothem (FR-040)."""
        return self.apothem / COS_30

    def __post_init__(self) -> None:
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError(
                f"HexGrid rows and cols must be positive; got rows={self.rows} cols={self.cols}"
            )
        if self.tile_width <= 0:
            raise ValueError(f"tile_width must be > 0; got {self.tile_width}")


@dataclass
class HexCell:
    """Position of a single hex cell within a grid."""

    row: int
    col: int
    center: tuple[float, float]
    """(x, y) center of the hex cell."""


def compute_hex_layout(spec: HexGridSpec) -> list[HexCell]:
    """Compute the (x, y) center of every hex cell in a rows×cols grid.

    Hex grids use a staggered (pointy-top) layout: odd rows are offset
    horizontally by half a cell width.

    Args:
        spec: The hex grid specification.

    Returns:
        List of HexCell with computed center coordinates.
    """
    cells: list[HexCell] = []
    r = spec.circumradius
    ap = spec.apothem
    spacing = spec.spacing

    # Horizontal distance between adjacent cells in a row (pointy-top hexes)
    dx = 2 * r + spacing
    # Vertical distance between rows
    dy = ap * 2 + spacing

    for row in range(spec.rows):
        x_offset = 0.0 if row % 2 == 0 else r + spacing / 2
        for col in range(spec.cols):
            cx = x_offset + col * dx
            cy = row * dy
            cells.append(HexCell(row=row, col=col, center=(cx, cy)))

    return cells


def hex_grid_bounds(spec: HexGridSpec) -> tuple[float, float]:
    """Compute the bounding (width, length) of a hex grid.

    Args:
        spec: The hex grid specification.

    Returns:
        (width, length) of the full grid footprint in mm.
    """
    if spec.rows == 0 or spec.cols == 0:
        return (0.0, 0.0)

    r = spec.circumradius
    ap = spec.apothem
    spacing = spec.spacing
    dx = 2 * r + spacing
    dy = ap * 2 + spacing

    # Width: cols cells wide, plus the offset of the last (odd) row
    width = (spec.cols - 1) * dx + 2 * r
    # Account for the staggered offset on odd rows
    width += (r + spacing / 2) if spec.rows > 1 else 0

    length = (spec.rows - 1) * dy + 2 * ap

    return (width, length)


def build_hex_grid(spec: HexGridSpec) -> "Bosl2Solid":
    """Build the hexagonal cutout solid for a hex-grid compartment.

    Args:
        spec: The hex grid specification.

    Returns:
        A Bosl2Solid of all hex cell cutouts (positive geometry to subtract
        from the box floor), or None if pybosl2 is unavailable.
    """
    try:
        from pybosl2 import regular_prism, cylinder
    except ImportError:
        return None

    cells = compute_hex_layout(spec)
    cutouts = None

    for cell in cells:
        cx, cy = cell.center

        # Hexagonal prism cutout for the tile (diameter = apothem-to-apothem width)
        hex_cutout = regular_prism(
            sides=6, height=spec.height + 10, diameter=spec.tile_width,
        )

        # Push block: subtract a smaller hexagon from the cell center,
        # leaving a raised central pillar (FR-041)
        if spec.push_block_height > 0:
            push = regular_prism(
                sides=6, height=spec.push_block_height, diameter=spec.push_block_width,
            )
            hex_cutout = hex_cutout - push

        # Finger hole: circular cutout through the floor (FR-042).
        # Offset from the pillar to the cell edge when both are present.
        if spec.finger_hole_diameter > 0:
            hole = cylinder(height=spec.height + 1, radius=spec.finger_hole_diameter / 2)
            offset_x = spec.circumradius * 0.4 if spec.push_block_height > 0 else 0.0
            hole = hole.translate([offset_x, 0, -0.5])
            hex_cutout = hex_cutout - hole

        hex_cutout = hex_cutout.translate([cx, cy, 0])
        cutouts = hex_cutout if cutouts is None else cutouts | hex_cutout

    return cutouts
