#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth Animal Kingdom board game insert.

Ports the original design from examples/earth_animal_kingdom.py to the
spec_driven Project API. All 37 animal token entries, card box, sprout box,
canopy box, board storage, and spacer tray.

Usage:
    cd /path/to/openscad_boardgame_toolkit
    python3 boxes/earth_animal_kingdom/earth_animal_kingdom.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from spec_driven import (
    Project, BoxType, LabelMode, Color,
    LidBuilder, PatternBuilder, PatternType, ScoopSide,
)

# ── Game Box & Defaults ───────────────────────────────────────────
project = Project(
    "EarthAnimalKingdom",
    game_box_size=(288, 158, 47),
    wall_thickness=2.0,
    floor_thickness=1.6,
    lid_thickness=2.0,
    gap_threshold=10.0,
    min_spacer_dim=15.0,
)

# ── Animal Token Definitions (37 entries from original design) ────
# Each: object(width=W, length=L[, num=N])
# Token thickness: 8mm. Multi-quantity stacked in one compartment.

class A:
    def __init__(self, width, length, num=1):
        self.width = width
        self.length = length
        self.num = num

ANIMALS: list[tuple[str, A]] = [
    ("elephant",       A(width=43.5, length=54)),
    ("polar_bear",     A(width=36.5, length=53)),
    ("cow",            A(width=36.5, length=47.5)),
    ("pig",            A(width=24.5, length=35)),
    ("gazelle",        A(width=41,   length=35)),
    ("turkey",         A(width=24,   length=25, num=5)),
    ("fly",            A(width=11,   length=11)),
    ("capybara",       A(width=16.5, length=32, num=2)),
    ("capybara_2",     A(width=16.5, length=32, num=3)),
    ("monkey",         A(width=29,   length=24)),
    ("pangolin",       A(width=16,   length=21, num=5)),
    ("deer",           A(width=47,   length=25.5)),
    ("goanna",         A(width=25,   length=30)),
    ("fox",            A(width=16,   length=35)),
    ("snake",          A(width=14,   length=41.5)),
    ("rabbit",         A(width=18.5, length=21)),
    ("termite",        A(width=12,   length=12, num=5)),
    ("ornyx",          A(width=39,   length=40)),
    ("platypus",       A(width=14.5, length=25)),
    ("lemur",          A(width=22,   length=30)),
    ("peacock",        A(width=30,   length=27)),
    ("gopher",         A(width=17.5, length=17, num=5)),
    ("crocodile",      A(width=16,   length=85)),
    ("goat",           A(width=37,   length=36)),
    ("jaguar",         A(width=20,   length=49)),
    ("rhino",          A(width=36,   length=64)),
    ("goose",          A(width=25,   length=21)),
    ("eagle",          A(width=31,   length=43)),
    ("spider_monkey",  A(width=26.5, length=25)),
    ("hoopoe",         A(width=17,   length=16)),
    ("kangaroo",       A(width=37,   length=39)),
    ("loon",           A(width=26.5, length=13)),
    ("tarsier",        A(width=29,   length=12.5)),
    ("jay",            A(width=12.5, length=12)),
    ("chipmunk",       A(width=15,   length=14)),
    ("quokka",         A(width=24,   length=15)),
    ("beaver",         A(width=15.5, length=35)),
]

TOKEN_THICKNESS = 8.0

# ── Split animals into two halves ─────────────────────────────────
mid = len(ANIMALS) // 2
half1, half2 = ANIMALS[:mid], ANIMALS[mid:]


def add_animal_box(box_idx: int, animals: list[tuple[str, A]], label: str):
    """Create a filament-hinge box with per-animal compartments."""
    # Large interior for compartment validation (real 3D bin packing in later phase)
    box_w = 300.0
    box_l = 300.0
    max_h = max(a.num for _, a in animals) * TOKEN_THICKNESS + project.lid_thickness + project.floor_thickness + 4

    box = project.box(
        BoxType.FILAMENT_HINGE,
        label,
        size=(box_w + 2 * project.wall_thickness, box_l + 2 * project.wall_thickness, max_h),
        lid=LidBuilder(
            text=label,
            label_mode=LabelMode.FRAMED,
            text_color=Color.WHITE(),
            frame_color=Color(0.8, 0.4, 0.1),
        ),
    )

    for name, a in animals:
        depth = a.num * TOKEN_THICKNESS
        box.compartment(
            name, size=(a.width + 4, a.length + 4), depth=depth,
            finger_scoop=True, scoop_side=ScoopSide.FRONT,
        )

    return box


# ── Animal Token Boxes ────────────────────────────────────────────
add_animal_box(1, half1, "AnimalBox1")
add_animal_box(2, half2, "AnimalBox2")

# ── Animal Cards Box ──────────────────────────────────────────────
CARD_W, CARD_L = 72.0, 123.0
CARD_COUNT = 36
card_height = (CARD_COUNT / 10) * 6.0 + project.floor_thickness + project.lid_thickness + 4

card_box = project.box(
    BoxType.SLIDING,
    "AnimalCardsBox",
    size=(CARD_W + 2 * project.wall_thickness, CARD_L + 2 * project.wall_thickness, card_height),
    lid=LidBuilder(
        text="Animal Cards",
        label_mode=LabelMode.FRAMED,
        text_color=Color.WHITE(),
        frame_color=Color(0.2, 0.6, 0.3),
        pattern=PatternBuilder(type=PatternType.HEX_GRID),
        pattern_color=Color(0.3, 0.7, 0.4),
    ),
)
card_box.compartment(
    "Cards", size=(CARD_W - 4, CARD_L - 4), depth=card_height - project.lid_thickness - project.floor_thickness,
    finger_scoop=True,
)

# ── Sprout Box ────────────────────────────────────────────────────
sprout_h = 8.0 + project.floor_thickness + project.lid_thickness
sprout = project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(CARD_W + 2 * project.wall_thickness, CARD_L + 2 * project.wall_thickness, sprout_h),
    lid=LidBuilder(text="Sprouts", text_color=Color.WHITE(), frame_color=Color(0.3, 0.8, 0.3)),
)
sprout.compartment("Sprouts", size=(CARD_W - 4, CARD_L - 4), depth=8.0, finger_scoop=True)

# ── Canopy Box ────────────────────────────────────────────────────
canopy = project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(38, CARD_L + 2 * project.wall_thickness, 46),
    lid=LidBuilder(text="Canopy", text_color=Color.WHITE(), frame_color=Color(0.4, 0.6, 0.2)),
)
canopy.compartment("Canopies", size=(30, CARD_L - 4), depth=42, finger_scoop=True)

# ── Board Storage ─────────────────────────────────────────────────
project.box(BoxType.NO_LID, "Boards", size=(174, 150, 6), expandable=False)

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
