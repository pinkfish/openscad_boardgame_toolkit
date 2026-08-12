#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Stackable hexes — hexagonal stackable boxes with side magnets.

Ports examples/stackable_hexes.py to the spec_driven Project API.
Standalone stackable boxes (no game box) with round or rectangular magnets
in the side walls and 1–4 internal divisions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pybosl2 import Color

from spec_driven import Project, BoxType, LabelMode, LidBuilder

# ── Stackable Hex Parameters ──────────────────────────────────────
stackable_width = 100
stackable_height = 24
wall_thickness = 4

# Magnet defaults: round = [diameter, depth], rect = [width, length, depth]
ROUND_MAGNET_SIZE = (stackable_height / 2 - 1, 7, 2.9)
RECT_MAGNET_SIZE = (12, 6, 1.65)


def stackable_hex(
    project: Project,
    label: str,
    divisions: int,
    magnet_type: str,
    magnet_size: tuple,
) -> None:
    """Create a standalone stackable hex box."""
    box = project.box(
        BoxType.NO_LID,
        label,
        size=(stackable_width, stackable_width, stackable_height),
        wall_thickness=wall_thickness,
        stackable="inside",            # interlocking rim (FR-038)
        stackable_thickness=2.0,
        magnet_type=magnet_type,       # round or rect (FR-039)
        magnet_size=magnet_size,
        no_rotate=True,                # hex is rotationally symmetric
    )
    if divisions > 1:
        # Partition the hex into N equal compartments
        sector = (stackable_width - wall_thickness * 2.5) / divisions
        for i in range(divisions):
            box.compartment(
                f"div{i + 1}",
                size=(sector, sector),
                depth=stackable_height - wall_thickness,
            )


# Standalone project (no game box → each box exports independently)
project = Project(
    "StackableHexes",
    game_box_size=None,   # standalone: no enclosing game box (FR-037)
    wall_thickness=wall_thickness,
    floor_thickness=wall_thickness,
)

# 8 variants: 1–4 divisions × round/rect magnets
round_variants = [
    (1, "HexBoxSingle6x3RoundMagnet"),
    (2, "HexBoxSingle6x3RoundMagnetWithTwoPartitions"),
    (3, "HexBoxSingle6x3RoundMagnetWithThreePartitions"),
    (4, "HexBoxSingle6x3RoundMagnetWithFourPartitions"),
]
rect_variants = [
    (1, "HexBoxSingle10x5x2RectMagnet"),
    (2, "HexBoxSingle10x5x2RectMagnetWithTwoPartitions"),
    (3, "HexBoxSingle10x5x2RectMagnetWithThreePartitions"),
    (4, "HexBoxSingle10x5x2RectMagnetWithFourPartitions"),
]

for divisions, label in round_variants:
    stackable_hex(project, label, divisions, "round", ROUND_MAGNET_SIZE)
for divisions, label in rect_variants:
    stackable_hex(project, label, divisions, "rect", RECT_MAGNET_SIZE)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files:")
    print(f"  Written: {len(result.written)}")
    for f in result.written:
        print(f"    ✓ {f}")
