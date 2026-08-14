import math
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
# ROOT, no absolute paths, no hardcoded version. Every other example carries
# this; without it this one only builds when the caller has already set the
# path up, and fails with a bare "No module named 'pybosl2'" when run directly.
for _sp in ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (  # noqa: E402
    Project, BoxType, ScoopSide, LabelMode, PatternType, LidBuilder, PatternBuilder, Color,
)

# Create project with 288 x 288 x 72 game box size
project = Project(
    "Earth",
    game_box_size=(288.0, 288.0, 72.0),
    wall_thickness=2.0,
    floor_thickness=1.6,
    lid_thickness=2.0,
    clearance_slack=0.0,
    generate_spacers=False,
)

# ── Card Size Constants ───────────────────────────────────────────
CARD_W, CARD_L = 62.0, 93.0
card_height_10 = 6.0
single_card_thickness = card_height_10 / 10.0  # 0.6mm per card

# Card counts
flora_cards = 179
terrain_cards = 66
event_cards = 38
earth_cards = flora_cards + terrain_cards + event_cards  # 283 cards

ecosystem_cards = 32
fauna_cards = 23
island_cards = 10
climate_cards = 10
solo_cards = 6
season_cards = 12
abundance_other_cards = 10

# ── 1. Earth Card Boxes (4 identical columns/bins) ────────────────
# 3 full-height Earth Card Boxes, 1 smaller Earth Card Box, and 1 Compost Box stacked on top.
# In the original, card_box_width=68, length=99. Let's make them size=(68, 99, None) and expandable.
for i in range(4):
    box = project.box(
        BoxType.SLIDING,
        f"EarthCardBox{i+1}",
        size=(68.0, 99.0, 55.2),
        position=(i * 68.0, 0.0, 0.0),
        expandable=False,
        wall_thickness=3.0,
        lid=LidBuilder(
            text="Earth",
            label_mode=LabelMode.FRAMED,
            text_color=Color("white"),
            frame_color=Color("darkgreen"),
        ),
    )
    box.compartment("Cards", size=(CARD_W, CARD_L), depth=51.6, finger_scoop=True)

# Small Earth Card Box (height is small, 1/3 of the full column height)
small_card = project.box(
    BoxType.SLIDING,
    "EarthCardBoxSmall",
    size=(68.0, 99.0, 18.4),
    position=(0.0, 99.0, 0.0),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(
        text="Earth",
        label_mode=LabelMode.FRAMED,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
    ),
)
small_card.compartment("Cards", size=(CARD_W, CARD_L), depth=14.8, finger_scoop=True)

# Compost Box (stacked on top of the small Earth box)
compost = project.box(
    BoxType.FILAMENT_HINGE,
    "CompostBox",
    size=(68.0, 99.0, 36.8),
    position=(0.0, 99.0, 18.4),
    expandable=False,
    lid=LidBuilder(
        text="Compost",
        text_color=Color("white"),
        frame_color=Color("brown"),
    ),
)
compost.compartment("Compost", size=(60.0, 91.0), depth=33.2, finger_scoop=True)

# ── 2. Small Card Boxes (Ecosystem, Fauna, Island stack) ─────────
# Ecosystem
ecosystem_h = project.floor_thickness + project.lid_thickness + single_card_thickness * ecosystem_cards + 1.0  # ~23.8
ecosystem = project.box(
    BoxType.SLIDING,
    "EcosystemCardBox",
    size=(68.0, 99.0, ecosystem_h),
    position=(68.0, 99.0, 0.0),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Ecosystem", text_color=Color("white"), frame_color=Color("gold")),
)
ecosystem.compartment("Cards", size=(CARD_W, CARD_L), depth=ecosystem_h - 3.6, finger_scoop=True)

# Fauna
fauna_h = project.floor_thickness + project.lid_thickness + single_card_thickness * fauna_cards + 1.0  # ~18.4
fauna = project.box(
    BoxType.SLIDING,
    "FaunaCardBox",
    size=(68.0, 99.0, fauna_h),
    position=(68.0, 99.0, 23.8),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Fauna", text_color=Color("white"), frame_color=Color("gold")),
)
fauna.compartment("Cards", size=(CARD_W, CARD_L), depth=fauna_h - 3.6, finger_scoop=True)

# Island (two_layer lid!)
island_h = 13.0
island = project.box(
    BoxType.SLIDING,
    "IslandCardBox",
    size=(68.0, 99.0, island_h),
    position=(68.0, 99.0, 42.2),
    expandable=False,
    wall_thickness=3.0,
    two_layer=True,
    lid=LidBuilder(text="Island", text_color=Color("white"), frame_color=Color("gold")),
)
island.compartment("Cards", size=(CARD_W, CARD_L), depth=island_h - 3.6, finger_scoop=True)

# ── 3. Start & Climate/Solo/Season Stack ─────────────────────────
climate_h = project.floor_thickness + project.lid_thickness + single_card_thickness * climate_cards + 1.0  # ~10.6
climate = project.box(
    BoxType.SLIDING,
    "ClimateCardBox",
    size=(68.0, 99.0, climate_h),
    position=(136.0, 99.0, 0.0),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Climate", text_color=Color("white"), frame_color=Color("teal")),
)
climate.compartment("Cards", size=(CARD_W, CARD_L), depth=climate_h - 3.6, finger_scoop=True)

solo_h = project.floor_thickness + project.lid_thickness + single_card_thickness * solo_cards + 1.0  # ~8.2
solo = project.box(
    BoxType.SLIDING,
    "SoloCardBox",
    size=(68.0, 99.0, solo_h),
    position=(136.0, 99.0, 10.6),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Solo", text_color=Color("white"), frame_color=Color("teal")),
)
solo.compartment("Cards", size=(CARD_W, CARD_L), depth=solo_h - 3.6, finger_scoop=True)

season_h = project.floor_thickness + project.lid_thickness + single_card_thickness * season_cards + 1.0  # ~11.8
season = project.box(
    BoxType.SLIDING,
    "SeasonCardBox",
    size=(68.0, 99.0, season_h),
    position=(136.0, 99.0, 18.8),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Season", text_color=Color("white"), frame_color=Color("teal")),
)
season.compartment("Cards", size=(CARD_W, CARD_L), depth=season_h - 3.6, finger_scoop=True)

abundance_h = project.floor_thickness + project.lid_thickness + single_card_thickness * abundance_other_cards + 1.0  # ~10.6
abundance = project.box(
    BoxType.SLIDING,
    "AbundanceOtherCardBox",
    size=(68.0, 99.0, abundance_h),
    position=(136.0, 99.0, 30.6),
    expandable=False,
    wall_thickness=3.0,
    lid=LidBuilder(text="Abundance", text_color=Color("white"), frame_color=Color("teal")),
)
abundance.compartment("Cards", size=(CARD_W, CARD_L), depth=abundance_h - 3.6, finger_scoop=True)

start_h = 14.0
start_box = project.box(
    BoxType.CAP,
    "StartBox",
    size=(68.0, 99.0, start_h),
    position=(136.0, 99.0, 41.2),
    expandable=False,
    lid=LidBuilder(text="Start", text_color=Color("white"), frame_color=Color("gold")),
)
start_box.compartment("Start", size=(60.0, 91.0), depth=start_h - 3.6, finger_scoop=True)

# ── 4. Player Boxes (6 color slipover lids) ───────────────────────
player_colours = ["red", "green", "yellow", "blue", "purple", "pink"]
for idx, col in enumerate(player_colours):
    pbox = project.box(
        BoxType.SLIPOVER,
        f"PlayerBox{col.capitalize()}",
        size=(68.0, 99.0, 9.2),
        position=(204.0, 99.0, idx * 9.2),
        expandable=False,
        lid=LidBuilder(text="Player", text_color=Color("white")),
    )
    pbox.compartment("PlayerComponents", size=(60.0, 91.0), depth=5.6, finger_scoop=True)

# ── 5. Canopy Box ─────────────────────────────────────────────────
canopy = project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(168.0, 89.0, 55.2),
    position=(0.0, 198.0, 0.0),
    expandable=False,
    lid=LidBuilder(text="Canopy", text_color=Color("white"), frame_color=Color("olive")),
)
canopy.compartment("Canopies", size=(160.0, 81.0), depth=45.0, finger_scoop=True)

# ── 6. Sprouts & Score Pad Stack ──────────────────────────────────
score_pad = project.box(
    BoxType.NO_LID,
    "ScorePadBox",
    size=(107.0, 89.0, 6.6),
    position=(168.0, 198.0, 0.0),
    expandable=False,
)
score_pad.compartment("Pad", size=(99.0, 81.0), depth=5.0)

sprout = project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(107.0, 89.0, 48.6),
    position=(168.0, 198.0, 6.6),
    expandable=False,
    lid=LidBuilder(text="Sprouts", text_color=Color("white"), frame_color=Color("green")),
)
sprout.compartment("Sprouts", size=(99.0, 81.0), depth=35.0, finger_scoop=True)

# ── 7. Seed Box ───────────────────────────────────────────────────
# Fits vertically on the side
seed = project.box(
    BoxType.FILAMENT_HINGE,
    "SeedBox",
    size=(16.0, 46.0, 72.0),
    position=(272.0, 0.0, 0.0),
    expandable=False,
    lid=LidBuilder(text="Seeds", text_color=Color("white"), frame_color=Color("brown")),
)
seed.compartment("Seeds", size=(8.0, 38.0), depth=68.4)

# ── 8. Player Boards (Flat addition to pack alongside boxes) ──────
# Player boards block: width 242, length 288, height 16.8 (6 boards + 1 middle board + 1 abundance board)
project.box(
    BoxType.NO_LID,
    "PlayerBoards",
    size=(242.0, 288.0, 16.8),
    position=(0.0, 0.0, 55.2),
    expandable=False,
)

# ── 9. Abundance Boards (Vertical stack on right side) ───────────
project.box(
    BoxType.NO_LID,
    "AbundanceBoards",
    size=(12.6, 241.0, 57.0),
    position=(275.4, 46.0, 0.0),
    expandable=False,
)

# ── 10. Top Spaced Box (Hollow spacer next to abundance boards) ──
project.box(
    BoxType.NO_LID,
    "TopSpacedBox",
    size=(46.0, 241.0, 15.0),
    position=(242.0, 46.0, 57.0),
    expandable=False,
)

if __name__ == "__main__":
    import os
    if os.environ.get("FROM_MAKE") == "1":
        result = project.export("output/")
        print(f"Exported {result.total_files} files:")
        for file in result.written:
            print(f"  ✓ {file}")

    else:
        project.show()
