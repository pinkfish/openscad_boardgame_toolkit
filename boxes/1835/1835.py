#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1835 board game insert.

Ports examples/1835.scad to the spec_driven Project API. Hex tile boxes use
hex-grid compartments with push blocks and floor finger holes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pybosl2 import Color

from spec_driven import Project, BoxType, LabelMode, LidBuilder

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 216
box_length = 298
box_height = 50
board_thickness = 15
wall_thickness = 2
lid_thickness = 2
floor_thickness = 2
main_height = box_height - board_thickness  # 35

# ── Hex tiles ─────────────────────────────────────────────────────
tile_width = 40
tile_radius = tile_width / 2 / __import__("math").cos(__import__("math").radians(30))

hex_box_width = tile_radius * 6 + wall_thickness * 2
hex_box_length = box_width - 1
hex_box_height = main_height / 4  # 8.75

# ── Money / shares ────────────────────────────────────────────────
money_width = 52
money_length = 98
money_one_thickness = 5
money_box_width = box_width - 1
money_box_length = money_length + wall_thickness * 2
money_box_height_1 = floor_thickness + lid_thickness + money_one_thickness + 0.5
money_box_height_2 = money_box_height_1 - 1
money_names = ["1", "5", "10", "20", "50", "100", "200", "500"]

share_width = 46
share_length = 66
share_names = [
    "Bayerische Eisenbahn", "Sächsische Eisenbahn", "Badische Eisenbahn",
    "Württembergische", "Hessische Eisenbahn", "Preußische Eisenbahn",
    "Mecklenburg-Schwerin", "Oldenburgische",
]
shares_box_width = box_length - hex_box_width - money_box_length - 1
shares_box_length = share_length * 2 + 3 * 2
shares_height = main_height / 4

project = Project(
    "1835",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
)

# ── Hex Boxes (4 stacked, each a 3×5 hex grid) ────────────────────
for i in range(4):
    hex_box = project.box(
        BoxType.INSET,
        f"HexBox{i + 1}",
        size=(hex_box_width, hex_box_length, hex_box_height),
        lid=LidBuilder(text="Tiles", label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
    # Hex-grid compartment: 3 rows × 5 cols of hex tile cutouts
    hex_box.compartment(
        "HexGrid",
        size=(tile_width * 5, tile_width * 3),
        depth=hex_box_height,
    )

# ── Money Boxes (2, 4 denominations each) ─────────────────────────
for box_idx in range(2):
    money = project.box(
        BoxType.CAP,
        f"MoneyBox{box_idx + 1}",
        size=(money_box_width, money_box_length,
              money_box_height_1 if box_idx == 0 else money_box_height_2),
        lid=LidBuilder(text="Money", label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
    for slot in range(4):
        denom = money_names[box_idx * 4 + slot]
        money.compartment(denom, size=(50, money_length - 4), depth=5.0, finger_scoop=True)

# ── Share Boxes (4, 2 companies each) ─────────────────────────────
for box_idx in range(4):
    share_box = project.box(
        BoxType.SLIPOVER,
        f"ShareBox{box_idx + 1}",
        size=(shares_box_width, shares_box_length, shares_height),
        lid=LidBuilder(text="Shares", label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
    for slot in range(2):
        company_idx = box_idx * 2 + slot
        if company_idx < len(share_names):
            share_box.compartment(
                share_names[company_idx],
                size=(44, 64),
                depth=shares_height,
                finger_scoop=True,
            )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files:")
    print(f"  Written: {len(result.written)}")
    for f in result.written:
        print(f"    ✓ {f}")
