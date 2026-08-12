#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Irish Gauge board game insert.

Ports examples/irish_gauge.scad to the spec_driven Project API.
Box sizes are derived from game box dimensions; spacer boxes are
auto-generated from leftover space.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pybosl2 import Color

from spec_driven import Project, BoxType, LabelMode, LidBuilder

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 214
box_length = 302
box_height = 39
board_thickness = 10.5
wall_thickness = 3
lid_thickness = 3

card_width = 49
card_length = 71
card_20_thickness = 14
single_card_thickness = card_20_thickness / 20  # 0.7mm per card

train_width = 7.75
train_length = 5.5
train_height = 8
num_trains_per_company = 19

dividend_marker_diameter = 7.5
dividend_marker_thickness = 3

# ── Companies ──────────────────────────────────────────────────────
companies = [
    {"shares": 2, "color": "orange", "name": ["Belfast and", "County Down", "Railway"], "lid": "Belfast"},
    {"shares": 3, "color": "yellow", "name": ["Cork Bandon", "& South Coast", "Railway"], "lid": "Cork"},
    {"shares": 3, "color": "red",    "name": ["Midland", "Great Western", "Railway"], "lid": "Midland"},
    {"shares": 4, "color": "purple", "name": ["Waterford", "Limerick", "& Western", "Railway"], "lid": "Waterford"},
    {"shares": 4, "color": "blue",   "name": ["Great Southern", "& Western", "Railway"], "lid": "Great Southern"},
]

# ── Derived Box Sizes (pulled from the original layout) ────────────
company_box_width = box_width / 4                    # 53.5
company_box_length = card_length * 1.8 + wall_thickness * 2  # 133.8
company_box_height = (box_height - board_thickness) / 2       # 14.25

money_box_width = box_width                            # 214
money_box_length = card_length + wall_thickness * 2    # 77
money_box_height = box_height - board_thickness        # 28.5

project = Project(
    "IrishGauge",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    lid_thickness=lid_thickness,
)

# ── Money Box (filament hinge, 3 card slots) ──────────────────────
money = project.box(
    BoxType.FILAMENT_HINGE,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    no_rotate=True,  # card slots are directional (3 across the width)
    position=(0, 0, 0),
    lid=LidBuilder(text="Bank", label_mode=LabelMode.FRAMED, text_color=Color("white")),
)
for i, denomination in enumerate(["1", "5", "10"]):
    money.compartment(
        denomination, size=(card_width, card_length - 4), depth=money_box_height,
        finger_scoop=True,
    )

# ── Company Boxes (5, shared footprint, distinct contents) ────────
for i, company in enumerate(companies):
    lid_text = company["lid"]
    # Manual positions matching the original BoxLayout:
    #   Companies 0-2 in a row at y=money_box_length, x = company_box_width * i
    #   Companies 3-4 stacked above companies 0-1 (z = company_box_height)
    if i < 3:
        position = (company_box_width * i, money_box_length, 0)
    else:
        position = (company_box_width * (i - 3), money_box_length, company_box_height)

    box = project.box(
        BoxType.SLIDING,
        f"CompanyBox{i}",
        size=(company_box_width, company_box_length, company_box_height),
        no_rotate=True,
        position=position,
        lid=LidBuilder(text=lid_text, label_mode=LabelMode.FRAMED, text_color=Color("white")),
    )
    # Share cards stacked per company's share count (sized to fit 47.5mm interior width)
    share_depth = single_card_thickness * company["shares"] + 1
    box.compartment(
        "Shares", size=(43, card_length), depth=share_depth,
        finger_scoop=True,
    )
    # Trains well (19 trains, ~6x4 grid)
    box.compartment(
        "Trains", size=(train_length * 6, train_width * 4), depth=train_height,
        finger_scoop=True,
    )
    # Dividend marker slot
    box.compartment(
        "Dividend", size=(dividend_marker_diameter, dividend_marker_diameter),
        depth=dividend_marker_thickness,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files:")
    print(f"  Written: {len(result.written)}")
    for f in result.written:
        print(f"    ✓ {f}")
