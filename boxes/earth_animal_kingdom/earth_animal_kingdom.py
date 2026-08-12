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
    clearance_slack=0.0,
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

# ── Define Animal Token Boxes ─────────────────────────────────────
def add_animal_box(label: str):
    """Create a empty filament-hinge box whose compartments are populated via share_compartments."""
    return project.box(
        BoxType.FILAMENT_HINGE,
        label,
        size=(174.0, 156.0, 12.1),
        lid=LidBuilder(
            text=label,
            label_mode=LabelMode.FRAMED,
            text_color=Color("white"),
            frame_color=Color("gold"),
        ),
    )


# ── Animal Cards Box ──────────────────────────────────────────────
CARD_W, CARD_L = 72.0, 123.0
CARD_COUNT = 36
card_height = 25.6

card_box = project.box(
    BoxType.SLIDING,
    "AnimalCardsBox",
    size=(76, 156, card_height),
    expandable=False,
    lid=LidBuilder(
        text="Animal Cards",
        label_mode=LabelMode.FRAMED,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
        pattern=PatternBuilder(type=PatternType.HEX_GRID),
        pattern_color=Color([0.3, 0.7, 0.4]),
    ),
)
card_box.compartment(
    "Cards", size=(CARD_W, CARD_L), depth=22.0,
    finger_scoop=True,
)

# ── Sprout Box ────────────────────────────────────────────────────
sprout = project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(76, 156, 20.4),
    expandable=False,
    lid=LidBuilder(text="Sprouts", text_color=Color("white"), frame_color=Color("lightgreen")),
)
sprout.compartment("Sprouts", size=(64, 150), depth=16.8, finger_scoop=True)

# ── Canopy Box ────────────────────────────────────────────────────
canopy = project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(38, 158, 46.0),
    expandable=False,
    lid=LidBuilder(text="Canopy", text_color=Color("white"), frame_color=Color("olive")),
)
canopy.compartment("Canopies", size=(30, CARD_L), depth=42.4, finger_scoop=True)

# ── Board Storage ─────────────────────────────────────────────────
project.box(BoxType.NO_LID, "Boards", size=(174, 150, 6), expandable=False)

# ── Define Animal Token Boxes ─────────────────────────────────────
add_animal_box("AnimalBox1")
add_animal_box("AnimalBox2")

# ── Register Shared Animal Compartments ────────────────────────────
comps = [(name, a.width + 1.5, a.length + 1.5, a.num * TOKEN_THICKNESS) for name, a in ANIMALS]
project.share_compartments(["AnimalBox1", "AnimalBox2"], comps)

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
