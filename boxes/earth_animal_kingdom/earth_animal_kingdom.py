#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth Animal Kingdom insert — pyboxbuilder port of `examples/earth_animal_kingdom.scad`.

Every dimension is derived with the same formula as the original, and every box
sits where `BoxLayout()` puts it, so the two inserts describe the same object.

The animal slots are not solved for here. The original ships a precomputed
partition of the 37 animals across two boxes in `lib/animal_kingdom_items_layout.scad`,
and that partition is reproduced verbatim below — slot for slot, position for
position. Re-deriving it with the packer would give a different (and no better)
answer, and the point of this example is to match the original.

Usage:
    cd /path/to/openscad_boardgame_toolkit
    python3 boxes/earth_animal_kingdom/earth_animal_kingdom.py
"""

import sys
from pathlib import Path

# Repo root on sys.path, robust to __file__ being undefined (Jupyter / exec).
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

from pyboxbuilder import (  # noqa: E402
    BoxType, Color, LabelMode, LidBuilder, PatternBuilder, PatternType, Project,
    columns, stack,
)

# ── Game box and material constants (examples/earth_animal_kingdom.scad) ──
BOX_WIDTH = 288.0
BOX_LENGTH = 158.0
BOX_HEIGHT = 47.0

WALL = 2.0
FLOOR = 2.0
LID = 2.0

ANIMAL_TOKEN_THICKNESS = 8.0
ANIMAL_CARD_WIDTH = 72.0
ANIMAL_CARD_LENGTH = 123.0
ANIMAL_CARD_NUM = 36
SINGLE_CARD_THICKNESS = 6.0 / 10

# ── Derived box dimensions ────────────────────────────────────────────────
CARD_BOX_WIDTH = WALL * 2 + ANIMAL_CARD_WIDTH                       # 76.0
CARD_BOX_LENGTH = BOX_LENGTH - 2                                    # 156.0
CARD_BOX_HEIGHT = SINGLE_CARD_THICKNESS * ANIMAL_CARD_NUM + 2       # 23.6

SPROUT_BOX_WIDTH = CARD_BOX_WIDTH                                   # 76.0
SPROUT_BOX_LENGTH = BOX_LENGTH                                      # 158.0
SPROUT_BOX_HEIGHT = BOX_HEIGHT - CARD_BOX_HEIGHT - 1                # 22.4

CANOPY_BOX_WIDTH = 38.0
CANOPY_BOX_LENGTH = BOX_LENGTH                                      # 158.0
CANOPY_BOX_HEIGHT = BOX_HEIGHT - 1                                  # 46.0

ANIMAL_BOX_WIDTH = BOX_WIDTH - CARD_BOX_WIDTH - CANOPY_BOX_WIDTH    # 174.0
ANIMAL_BOX_LENGTH = BOX_LENGTH                                      # 158.0
ANIMAL_BOX_HEIGHT = FLOOR + LID + ANIMAL_TOKEN_THICKNESS + 0.5      # 12.5
ANIMAL_WALL = 1.5
ANIMAL_FOOT = 4.0

SPACER_BOX_WIDTH = ANIMAL_BOX_WIDTH                                 # 174.0
SPACER_BOX_LENGTH = ANIMAL_BOX_LENGTH                               # 158.0
SPACER_BOX_HEIGHT = BOX_HEIGHT - ANIMAL_BOX_HEIGHT * 2 - 1          # 21.0

# Interiors
ANIMAL_INNER_W = ANIMAL_BOX_WIDTH - 2 * ANIMAL_WALL                 # 171.0
ANIMAL_INNER_L = ANIMAL_BOX_LENGTH - 2 * ANIMAL_WALL                # 155.0
ANIMAL_INNER_H = ANIMAL_BOX_HEIGHT - FLOOR - LID                    # 8.5

#: AnimalBox1 — 26 slots from Layout_container0.
ANIMAL_LAYOUT_1: tuple[tuple[str, float, float, float, float], ...] = (
    ("capybara_2_1", 40.75, 22.5, 16.5, 32.0),
    ("capybara_2_2", 40.75, 57.5, 16.5, 32.0),
    ("capybara_2_3", 40.75, 92.5, 16.5, 32.0),
    ("cow", 58.75, 85.25, 47.5, 36.5),
    ("crocodile", 21.25, 39.75, 16.0, 85.0),
    ("deer", 58.75, 123.25, 47.0, 25.5),
    ("elephant", 58.75, 2.25, 54.0, 43.5),
    ("fly", 151.75, 138.75, 11.0, 11.0),
    ("fox", 114.25, 67.75, 35.0, 16.0),
    ("goat", 2.25, 2.25, 37.0, 36.0),
    ("gopher_1", 2.25, 45.75, 17.5, 17.0),
    ("gopher_2", 2.25, 65.75, 17.5, 17.0),
    ("gopher_3", 2.25, 85.75, 17.5, 17.0),
    ("gopher_4", 2.25, 105.75, 17.5, 17.0),
    ("gopher_5", 2.25, 125.75, 17.5, 17.0),
    ("hoopoe", 21.25, 126.25, 17.0, 16.0),
    ("jay", 138.25, 125.75, 12.0, 12.5),
    ("monkey", 107.75, 125.75, 29.0, 24.0),
    ("ornyx", 107.75, 85.25, 40.0, 39.0),
    ("pangolin_1", 151.75, 11.25, 16.0, 21.0),
    ("pangolin_2", 151.75, 35.25, 16.0, 21.0),
    ("pangolin_3", 151.75, 59.25, 16.0, 21.0),
    ("pangolin_4", 151.75, 83.25, 16.0, 21.0),
    ("pangolin_5", 151.75, 107.25, 16.0, 21.0),
    ("polar_bear", 58.75, 47.25, 53.0, 36.5),
    ("rhino", 114.25, 2.25, 36.0, 64.0),
)

#: AnimalBox2 — 30 slots from Layout_container1.
ANIMAL_LAYOUT_2: tuple[tuple[str, float, float, float, float], ...] = (
    ("beaver", 54.25, 131.75, 35.0, 15.5),
    ("capybara_1", 129.75, 49.5, 16.5, 32.0),
    ("capybara_2", 129.75, 84.5, 16.5, 32.0),
    ("chipmunk", 61.75, 112.75, 15.0, 14.0),
    ("eagle", 85.25, 27.75, 43.0, 31.0),
    ("gazelle", 42.75, 27.75, 41.0, 35.0),
    ("goanna", 33.75, 79.75, 30.0, 25.0),
    ("goose", 80.25, 90.25, 25.0, 21.0),
    ("jaguar", 147.75, 27.75, 20.0, 49.0),
    ("kangaroo", 2.25, 27.75, 39.0, 37.0),
    ("lemur", 30.25, 108.25, 30.0, 22.0),
    ("loon", 106.75, 90.25, 13.0, 26.5),
    ("peacock", 2.25, 79.75, 30.0, 27.0),
    ("pig", 80.25, 64.25, 35.0, 24.5),
    ("platypus", 2.25, 134.75, 25.0, 14.5),
    ("quokka", 28.75, 134.75, 24.0, 15.0),
    ("rabbit", 147.75, 121.25, 18.5, 21.0),
    ("snake", 147.75, 78.25, 14.0, 41.5),
    ("spider_monkey", 2.25, 108.25, 26.5, 25.0),
    ("tarsier", 65.25, 79.75, 12.5, 29.0),
    ("termite_1", 4.5, 66.25, 12.0, 12.0),
    ("termite_2", 19.5, 66.25, 12.0, 12.0),
    ("termite_3", 34.5, 66.25, 12.0, 12.0),
    ("termite_4", 49.5, 66.25, 12.0, 12.0),
    ("termite_5", 64.5, 66.25, 12.0, 12.0),
    ("turkey_1", 14.25, 2.25, 25.0, 24.0),
    ("turkey_2", 42.25, 2.25, 25.0, 24.0),
    ("turkey_3", 70.25, 2.25, 25.0, 24.0),
    ("turkey_4", 98.25, 2.25, 25.0, 24.0),
    ("turkey_5", 126.25, 2.25, 25.0, 24.0),
)

# ── Project ───────────────────────────────────────────────────────────────
project = Project(
    "EarthAnimalKingdom",
    game_box_size=(BOX_WIDTH, BOX_LENGTH, BOX_HEIGHT),
    wall_thickness=WALL,
    floor_thickness=FLOOR,
    lid_thickness=LID,
    clearance_slack=0.0,
    # Every box below is hand-positioned to match BoxLayout(), so there is no
    # leftover volume for the packer to find — the original's SpacerBox is
    # declared explicitly, exactly as the .scad does.
    generate_spacers=False,
)

BIRD_LID = PatternBuilder(type=PatternType.BIRD, spacing=20.0)

# ── 1. Animal cards box ───────────────────────────────────────────────────
card_box = project.box(
    BoxType.SLIDING,
    "AnimalCardsBox",
    size=(CARD_BOX_WIDTH, CARD_BOX_LENGTH, CARD_BOX_HEIGHT),
    expandable=False,
    lid=LidBuilder(
        text="Animal Cards",
        label_mode=LabelMode.FRAMED,
        pattern=BIRD_LID,
        text_color=Color("white"),
        frame_color=Color("maroon"),
    ),
)
card_box.compartment(
    "Cards",
    size=(ANIMAL_CARD_WIDTH, ANIMAL_CARD_LENGTH),
    depth=CARD_BOX_HEIGHT - FLOOR - LID,
    position=(0.0, 0.0),
    finger_scoop=True,
)

# ── 2. Sprout box ─────────────────────────────────────────────────────────
SPROUT_INNER_W = SPROUT_BOX_WIDTH - 2 * WALL
SPROUT_INNER_L = SPROUT_BOX_LENGTH - 2 * WALL

sprout_box = project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(SPROUT_BOX_WIDTH, SPROUT_BOX_LENGTH, SPROUT_BOX_HEIGHT),
    expandable=False,
    lid=LidBuilder(
        text="Sprouts",
        label_mode=LabelMode.FRAMED,
        pattern=BIRD_LID,
        text_color=Color("white"),
        frame_color=Color("green"),
    ),
)
# RoundedBoxAllSides inset 1mm from the interior walls, radius 5.
sprout_box.compartment(
    "Sprouts",
    size=(SPROUT_INNER_W - 2, SPROUT_INNER_L - 2),
    depth=SPROUT_BOX_HEIGHT - FLOOR - LID,
    position=(1.0, 1.0),
    rounded_corners=5.0,
)

# ── 3. Canopy box ─────────────────────────────────────────────────────────
CANOPY_INNER_W = CANOPY_BOX_WIDTH - 2 * WALL
CANOPY_INNER_L = CANOPY_BOX_LENGTH - 2 * WALL

canopy_box = project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(CANOPY_BOX_WIDTH, CANOPY_BOX_LENGTH, CANOPY_BOX_HEIGHT),
    expandable=False,
    lid=LidBuilder(
        text="Canopies",
        label_mode=LabelMode.FRAMED,
        pattern=BIRD_LID,
        text_color=Color("black"),
        frame_color=Color("cornsilk"),
    ),
)
canopy_box.compartment(
    "Canopies",
    size=(CANOPY_INNER_W - 2, CANOPY_INNER_L - 2),
    depth=CANOPY_BOX_HEIGHT - FLOOR - LID,
    position=(1.0, 1.0),
    rounded_corners=5.0,
)

# ── 4. Animal boxes ───────────────────────────────────────────────────────
def add_animal_box(label: str, slots):
    """One slipover box holding one container's worth of animal tokens."""
    box = project.box(
        BoxType.SLIPOVER,
        label,
        size=(ANIMAL_BOX_WIDTH, ANIMAL_BOX_LENGTH, ANIMAL_BOX_HEIGHT),
        expandable=False,
        wall_thickness=ANIMAL_WALL,
        foot=ANIMAL_FOOT,
        lid=LidBuilder(
            text="Animals",
            label_mode=LabelMode.FRAMED,
            pattern=BIRD_LID,
            text_color=Color("white"),
            frame_color=Color("saddlebrown"),
        ),
    )
    # A shallow pan over the whole interior, so a fingertip can get under the
    # tokens — the original's RoundedBoxAllSides at $inner_height - thickness/2.
    box.compartment(
        "Access",
        size=(ANIMAL_INNER_W - 2, ANIMAL_INNER_L - 2),
        depth=ANIMAL_TOKEN_THICKNESS / 2,
        position=(1.0, 1.0),
        rounded_corners=3.0,
    )
    # One slot per token, at the position the precomputed layout gives it.
    for name, x, y, width, length in slots:
        box.compartment(
            name,
            size=(width, length),
            depth=ANIMAL_TOKEN_THICKNESS + 0.5,
            position=(x, y),
            rounded_corners=1.0,
        )
    return box


add_animal_box("AnimalBox1", ANIMAL_LAYOUT_1)
add_animal_box("AnimalBox2", ANIMAL_LAYOUT_2)

# ── 5. Spacer ─────────────────────────────────────────────────────────────
project.box(
    BoxType.NO_LID,
    "SpacerBox",
    size=(SPACER_BOX_WIDTH, SPACER_BOX_LENGTH, SPACER_BOX_HEIGHT),
    expandable=False,
)

# ── 6. Arrangement ────────────────────────────────────────────────────────
# Three columns across the game box, as BoxLayout() lays them out: the cards
# and sprouts on the left, the animal trays stacked in the middle with the
# spacer on top, and the canopies down the right-hand side.
project.arrange(columns(
    stack("AnimalCardsBox", "SproutBox"),
    stack("AnimalBox1", "AnimalBox2", "SpacerBox"),
    "CanopyBox",
))


# ── Export ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = project.export("output/")
    print(f"Exported {result.total_files} files ({len(result.written)} written, "
          f"{len(result.skipped)} unchanged)")
    for bounds in project.piece_bounds:
        if bounds.mode == "mmu":
            print(f"    {bounds}")
