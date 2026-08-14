#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1835 board game insert.

Ports examples/1835.scad to the pyboxbuilder Project API. Hex tile boxes use
hex-grid compartments with push blocks and floor finger holes.
"""

import sys
from pathlib import Path

if "__file__" in globals():
    ROOT = Path(__file__).resolve().parents[2]
else:
    ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python — relative to
# ROOT, no absolute paths, no hardcoded version.
for _sp in ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pybosl2 import Color

from pyboxbuilder import Project, BoxType, LabelMode, LidBuilder

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
    board_thickness=board_thickness,
)

# ── Hex Boxes (4 stacked, each a 3×5 hex grid) ────────────────────
# Rotated 90° in the layout: (142.56 × 215) becomes (215 × 142.56)
for i in range(4):
    hex_box = project.box(
        BoxType.INSET,
        f"HexBox{i + 1}",
        size=(hex_box_length, hex_box_width, hex_box_height),
        no_rotate=True,
        position=(0, money_box_length, i * hex_box_height),
        lid=LidBuilder(text="Tiles", label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
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
        no_rotate=True,
        position=(0, 0, box_idx * money_box_height_1),
        lid=LidBuilder(text="Money", label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
    for slot in range(4):
        denom = money_names[box_idx * 4 + slot]
        money.compartment(denom, size=(50, money_length - 4), depth=5.0, finger_scoop=True, no_rotate=True)

# ── Share Boxes (4, 2 companies each) ─────────────────────────────
for box_idx in range(4):
    share_box = project.box(
        BoxType.SLIPOVER,
        f"ShareBox{box_idx + 1}",
        size=(shares_box_length, shares_box_width, shares_height),
        no_rotate=True,
        position=(0, money_box_length + hex_box_width, box_idx * shares_height),
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

# ── Middle Box (tokens / trains / private company cards) ──────────
# Rotated 90°: (102 × 215) becomes (215 × 102). Floats above the money boxes.
middle_width = money_box_length          # 102
middle_length = money_box_width          # 215
middle_height = main_height - money_box_height_1 - money_box_height_2  # 17

token_depths = [1, 1, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 4, 4]
token_labels = ["White", "Wheel", "1-3", "4-6", "L", "A", "E", "T", "S", "X", "Y", "Y", "R", "R"]
token_diameter = 6
token_thickness = 2

middle = project.box(
    BoxType.CAP,
    "MiddleBox",
    size=(middle_length, middle_width, middle_height),
    no_rotate=True,
    position=(0, 0, money_box_height_1 + money_box_height_2),
    lid=LidBuilder(text="Tokens/Trains", label_mode=LabelMode.FRAMED, text_color=Color("white")),
)
for i, depth_count in enumerate(token_depths):
    middle.compartment(
        token_labels[i],
        size=(token_diameter * (depth_count + 1), token_diameter * 2),
        depth=middle_height - lid_thickness - floor_thickness,
        finger_scoop=True,
    )
middle.compartment("Trains", size=(44, 64), depth=middle_height)
middle.compartment("Private", size=(44, 64), depth=middle_height)

# ── First Player Box (large markers) ──────────────────────────────
large_marker_diameter = 20
large_marker_length = 41

first_player_box_width = shares_box_width      # 52.45
first_player_box_length = box_width - shares_box_length - 1  # 77
first_player_box_height = large_marker_diameter + 4  # 24

first_player = project.box(
    BoxType.SLIPOVER,
    "FirstPlayer",
    size=(first_player_box_length, first_player_box_width, first_player_box_height),
    no_rotate=True,
    position=(shares_box_length, money_box_length + hex_box_width, 0),
    lid=LidBuilder(text="First", label_mode=LabelMode.FRAMED, text_color=Color("white")),
)
first_player.compartment(
    "LargeMarkers",
    size=(large_marker_diameter, large_marker_length - 8),
    depth=first_player_box_height - lid_thickness - floor_thickness,
    finger_scoop=True,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    if os.environ.get("FROM_MAKE") == "1":
        result = project.export("output/")
        print(f"Exported {result.total_files} files:")
        print(f"  Written: {len(result.written)}")
        for f in result.written:
            print(f"    ✓ {f}")

    else:
        project.show()
