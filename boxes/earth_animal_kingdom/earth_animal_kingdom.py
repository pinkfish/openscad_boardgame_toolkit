#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth Animal Kingdom board game insert."""

import sys
from pathlib import Path

# Add repo root to path so spec_driven can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from spec_driven import (
    Project, BoxType, LabelMode, Color,
    LidBuilder, PatternBuilder, PatternType, ScoopSide,
)

project = Project(
    "EarthAnimalKingdom",
    game_box_size=(288, 158, 47),
    wall_thickness=2.0,
    floor_thickness=1.6,
    lid_thickness=2.0,
    gap_threshold=10.0,
    min_spacer_dim=15.0,
)

# ── Animal Cards Box ──────────────────────────────────────────────
animal_cards = project.box(
    BoxType.SLIDING,
    "AnimalCards",
    size=(110, 80, 40),  # Larger to fit both compartments
    lid=LidBuilder(
        text="Animal Cards",
        label_mode=LabelMode.FRAMED,
        text_color=Color.WHITE(),
        frame_color=Color(0.2, 0.6, 0.3),
        pattern=PatternBuilder(type=PatternType.HEX_GRID),
        pattern_color=Color(0.3, 0.7, 0.4),
    ),
)
animal_cards.compartment(
    "Deck", size=(50, 70), depth=36, finger_scoop=True,
)
animal_cards.compartment(
    "Discard", size=(50, 70), depth=36,
)

# ── Animal Token Boxes (x2) ───────────────────────────────────────
for i in range(2):
    animal_box = project.box(
        BoxType.FILAMENT_HINGE,
        f"Animals{i + 1}",
        size=(75, 55, 30),
        lid=LidBuilder(
            text=f"Animals {i + 1}",
            label_mode=LabelMode.FRAMED,
            text_color=Color.WHITE(),
            frame_color=Color(0.8, 0.4, 0.1),
        ),
    )
    animal_box.compartment(
        "Tokens", size=(60, 45), depth=26, finger_scoop=True,
    )

# ── Board Storage (no lid) ────────────────────────────────────────
project.box(
    BoxType.NO_LID,
    "Boards",
    size=(70, 150, 15),
    expandable=False,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files:")
    print(f"  Written: {len(result.written)}")
    for f in result.written:
        print(f"    ✓ {f}")
    if result.skipped:
        print(f"  Skipped: {len(result.skipped)}")
    if result.cached_from:
        print(f"  Cache: {result.cached_from[:12]}...")
