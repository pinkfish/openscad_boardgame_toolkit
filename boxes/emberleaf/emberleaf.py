# SPDX-License-Identifier: Apache-2.0
"""Emberleaf insert — pyboxbuilder port of `examples/emberleaf.scad`.

Every dimension below is derived with the same formula the original OpenSCAD
file uses, and every box sits at the position `BoxLayout()` puts it at, so the
two inserts describe the same physical object.

The player box is the interesting one: rather than one big well, each game piece
gets its own slot. The five owl, rabbit, frog and rat workers are individual
silhouette cutouts at the pitch the original stamps them at, the hero standee
gets its own outline in the player's colour, and the wooden markers, victory
tokens and hex tiles each get their own pocket at their own depth. Two shallow
rounded depressions run over the top so the pieces can be lifted out.
"""

import sys
from pathlib import Path

# Repo root on sys.path, robust to __file__ being undefined (Jupyter / exec).
if "__file__" in globals():
    REPO_ROOT = Path(__file__).resolve().parents[2]
else:
    REPO_ROOT = Path.cwd()
sys.path.insert(0, str(REPO_ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python — relative to
# REPO_ROOT, no absolute paths, no hardcoded version.
for _sp in REPO_ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in REPO_ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (  # noqa: E402
    BoxType, Color, LabelMode, LidBuilder, PatternBuilder, PatternType, Project,
    columns, rows, stack,
)
from pyboxbuilder.compartments import CompartmentElement, grid_pack  # noqa: E402
from pyboxbuilder.enums import ElementShape  # noqa: E402

#: SVG silhouettes live beside this example (boxes/emberleaf/svg), so the
#: example is self-contained and builds the same from any directory.
SVG = str(REPO_ROOT / "boxes" / "emberleaf" / "svg")

# ── Game box and material constants (examples/emberleaf.scad) ─────────────
BOX_WIDTH = 287.0
BOX_LENGTH = 287.0
BOX_HEIGHT = 79.0
BOARD_THICKNESS = 26.5

WALL = 3.0
LID = 2.0
FLOOR = 2.0

HEX_SIZE = 38.5
TROPHY_WIDTH = 26.0
TROPHY_LENGTH = 36.0
WOOD_TOKEN_DIAMETER = 16.5
WOOD_TOKEN_THICKNESS = 4.0

CARD_LENGTH = 91.0
CARD_WIDTH = 66.0
CARDBOARD_TOKEN_THICKNESS = 2.0
SMALL_VICTORY_WIDTH = 20.5
SMALL_VICTORY_LENGTH = 17.5
TOKEN_THICKNESS = 9.0

# ── Derived box dimensions ────────────────────────────────────────────────
PLAYER_BOX_HEIGHT = (BOX_HEIGHT - BOARD_THICKNESS) / 4          # 13.125
PLAYER_BOX_LENGTH = (BOX_LENGTH - 2) / 2                        # 142.5
PLAYER_BOX_WIDTH = CARD_LENGTH + WALL * 2 + 1                   # 98.0

MATERIAL_BOX_WIDTH = PLAYER_BOX_WIDTH
MATERIAL_BOX_HEIGHT = PLAYER_BOX_HEIGHT
MATERIAL_BOX_LENGTH = PLAYER_BOX_LENGTH / 2                     # 71.25

CARD_BOX_WIDTH = PLAYER_BOX_WIDTH
CARD_BOX_LENGTH = CARD_WIDTH + WALL * 2 + 1                     # 73.0
CARD_BOX_HEIGHT = BOX_HEIGHT - BOARD_THICKNESS                  # 52.5

PLAYER_CARD_BOX_WIDTH = BOX_WIDTH - PLAYER_BOX_WIDTH - CARD_BOX_WIDTH - 1   # 90.0
PLAYER_CARD_BOX_LENGTH = CARD_LENGTH + WALL * 2 + 1                          # 98.0
PLAYER_CARD_BOX_HEIGHT = (BOX_HEIGHT - BOARD_THICKNESS) / 5                  # 10.5

COMMON_BOX_WIDTH = PLAYER_CARD_BOX_WIDTH
COMMON_BOX_LENGTH = BOX_LENGTH - PLAYER_CARD_BOX_LENGTH - 1                  # 188.0
COMMON_BOX_HEIGHT = LID + FLOOR + CARDBOARD_TOKEN_THICKNESS * 10 + 1         # 25.0

SPACER_FRONT_HEIGHT = BOX_HEIGHT - BOARD_THICKNESS - 1 - COMMON_BOX_HEIGHT   # 26.5
SPACER_SIDE_LENGTH = BOX_LENGTH - CARD_BOX_LENGTH * 3 - 1                    # 67.0

# Interiors
PLAYER_INNER_W = PLAYER_BOX_WIDTH - 2 * WALL                    # 92.0
PLAYER_INNER_L = PLAYER_BOX_LENGTH - 2 * WALL                   # 136.5
PLAYER_INNER_H = PLAYER_BOX_HEIGHT - LID - FLOOR                # 9.125

COMMON_INNER_W = COMMON_BOX_WIDTH - 2 * WALL                    # 84.0
COMMON_INNER_L = COMMON_BOX_LENGTH - 2 * WALL                   # 182.0
COMMON_INNER_H = COMMON_BOX_HEIGHT - LID - FLOOR                # 21.0

OVERSHOOT = 0.5
"""Extra height on every cutout so it breaks cleanly through the box rim."""


def pocket(inner_height: float, depth_from_top: float) -> dict:
    """Element depth/z for a pocket `depth_from_top` mm below the interior ceiling.

    The original places contents with `$inner_height - <stack of pieces>`, i.e.
    everything is measured down from the rim so shallow pieces stay in reach.
    """
    z = max(0.0, inner_height - depth_from_top)
    return {"z_offset": z, "depth": inner_height - z + OVERSHOOT}


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    rotation: float = 0.0,
    label: str | None = None,
    **pocket_kwargs,
) -> CompartmentElement:
    """An element positioned by its centre, the way the OpenSCAD modules are.

    Every shape in `examples/lib/emberleaf.scad` self-centres on its translate
    point; `CompartmentElement.offset` is a lower-left corner, so convert here
    once instead of at each of the fifty call sites.
    """
    proto = CompartmentElement(
        shape_file=shape_file,
        offset=(0.0, 0.0),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        **pocket_kwargs,
    )
    fw, fl = proto.footprint
    return CompartmentElement(
        shape_file=shape_file,
        offset=(center[0] - fw / 2, center[1] - fl / 2),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        **pocket_kwargs,
    )


# ── Project ───────────────────────────────────────────────────────────────
project = Project(
    "Emberleaf",
    game_box_size=(BOX_WIDTH, BOX_LENGTH, BOX_HEIGHT),
    wall_thickness=WALL,
    floor_thickness=FLOOR,
    lid_thickness=LID,
    # Every box below is hand-positioned, so nothing goes through the packer and
    # the slack only reaches the spacers — where it is what makes them liftable.
    clearance_slack=0.5,
    board_thickness=BOARD_THICKNESS,
    # The original names three spacers by hand. We let the packer find them:
    # the leftover space is the same, and it stays right if a box ever moves.
    generate_spacers=True,
)

LEAF_LID = PatternBuilder(type=PatternType.LEAF, spacing=10.0)


def player_box_elements(colour: str) -> tuple[CompartmentElement, ...]:
    """Every piece that lives in one player's box, each in its own slot.

    Mirrors `PlayerBoxInside` plus the per-colour hero from `examples/emberleaf.scad`.
    """
    full = pocket(PLAYER_INNER_H, TOKEN_THICKNESS + 0.5)

    # Workers — five of each species in a column, at the original's pitch.
    # Rabbits and rats alternate 180 degrees so the silhouettes nest.
    owls = grid_pack(
        centered(f"{SVG}/owl worker.svg", (12.0, 8.0), (23.0, 12.0), label="owl", **full),
        5, origin=(0.5, 2.0), pitch=(0.0, 12.0),
    )
    rabbits = grid_pack(
        centered(f"{SVG}/rabbit worker.svg", (36.0, 8.0), (23.0, 14.0), label="rabbit", **full),
        5, origin=(24.5, 1.0), pitch=(0.0, 12.0), alternate_rotation=180.0,
    )
    frogs = grid_pack(
        centered(f"{SVG}/frog worker.svg", (57.5, 9.0), (17.0, 16.0), label="frog", **full),
        5, origin=(49.0, 1.0), pitch=(0.0, 14.5),
    )
    rats = grid_pack(
        centered(f"{SVG}/rat worker.svg", (77.0, 9.0), (21.0, 15.0), label="rat", **full),
        5, origin=(66.5, 1.5), pitch=(0.0, 15.0), alternate_rotation=180.0,
    )

    hero_center, hero_size, hero_rotation = HERO_PLACEMENT[colour]
    hero = centered(
        f"{SVG}/{colour.lower()} leader.svg",
        hero_center, hero_size, rotation=hero_rotation, label="hero", **full,
    )

    # Wooden markers: a token-sized disc, each with its own set of grip notches.
    # The notch directions differ per marker so none of them breaks the wall —
    # the right-hand marker sits against it, so its notches face left and down.
    marker_deep = pocket(PLAYER_INNER_H, WOOD_TOKEN_THICKNESS * 2 + 0.5)
    marker_shallow = pocket(PLAYER_INNER_H, WOOD_TOKEN_THICKNESS + 0.5)
    d, r = WOOD_TOKEN_DIAMETER, WOOD_TOKEN_DIAMETER / 2
    markers: list[CompartmentElement] = []
    for cx, cy, depth, grips in (
        (PLAYER_INNER_W - r, 89.0, marker_deep, ((-r, 0.0), (0.0, -r))),
        (PLAYER_INNER_W - r * 3 - 5, 89.0, marker_deep, ((r, 0.0), (0.0, -r))),
        (PLAYER_INNER_W / 2, 102.0, marker_shallow, ((r, 0.0),)),
    ):
        markers.append(
            centered(None, (cx, cy), (d, d), shape=ElementShape.CIRCLE, label="marker", **depth)
        )
        markers.extend(
            centered(
                None, (cx + gx, cy + gy), (13.0, 13.0),
                shape=ElementShape.CIRCLE, label="grip", **depth,
            )
            for gx, gy in grips
        )

    # Victory tokens, stacked under the hex tiles at the back of the box.
    victory_y = PLAYER_INNER_L - HEX_SIZE / 2
    victory = [
        centered(
            f"{SVG}/victory.svg", (HEX_SIZE / 2, victory_y), (23.0, 27.0), label="victory",
            **pocket(PLAYER_INNER_H, 0.3 + CARDBOARD_TOKEN_THICKNESS * 2 + 0.5),
        ),
        centered(
            None, (HEX_SIZE / 2 - SMALL_VICTORY_LENGTH / 2, victory_y), (20.0, 20.0),
            shape=ElementShape.SPHERE_SCOOP, label="victory_grip",
            **pocket(PLAYER_INNER_H, 0.3 + CARDBOARD_TOKEN_THICKNESS * 2 + 0.5),
        ),
        centered(
            f"{SVG}/victory.svg", (HEX_SIZE / 2 + 2, victory_y),
            (SMALL_VICTORY_LENGTH, SMALL_VICTORY_WIDTH), label="victory_small",
            **pocket(PLAYER_INNER_H, 0.3 + CARDBOARD_TOKEN_THICKNESS * 3 + 0.8),
        ),
    ]

    # Hex tiles: one shallow (sits on the victory tokens), one full depth.
    hexes = [
        centered(
            None, (HEX_SIZE / 2 + 2.5, victory_y), (HEX_SIZE, HEX_SIZE),
            shape=ElementShape.HEXAGON, label="hex_left",
            **pocket(PLAYER_INNER_H, 0.3 + CARDBOARD_TOKEN_THICKNESS),
        ),
        centered(
            None, (PLAYER_INNER_W - HEX_SIZE / 2 - 2.5, victory_y), (HEX_SIZE, HEX_SIZE),
            shape=ElementShape.HEXAGON, label="hex_right",
            **pocket(PLAYER_INNER_H, 0.3 + CARDBOARD_TOKEN_THICKNESS * 5),
        ),
    ]

    # Two shallow rounded depressions so the pieces can be pulled out.
    scoops = [
        CompartmentElement(
            offset=(0.0, 0.0), size=(PLAYER_INNER_W, 80.0), shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0, label="pull_out_wide",
            **pocket(PLAYER_INNER_H, TOKEN_THICKNESS / 2),
        ),
        CompartmentElement(
            offset=(0.0, 0.0), size=(50.0, 96.0), shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0, label="pull_out_tall",
            **pocket(PLAYER_INNER_H, TOKEN_THICKNESS / 2),
        ),
    ]

    return (*owls, *rabbits, *frogs, *rats, hero, *markers, *victory, *hexes, *scoops)


#: Hero standee placement per player colour — (centre, size, rotation), read off
#: the `translate(...)` in each `*PlayerBox` module and the shape's own extent.
HERO_PLACEMENT: dict[str, tuple[tuple[float, float], tuple[float, float], float]] = {
    "Black": ((27.0, 78.0), (33.0, 28.0), 0.0),
    "Red": ((25.0, 78.0), (34.0, 25.0), 0.0),
    "Yellow": ((25.0, 77.0), (32.0, 26.0), 0.0),
    "Blue": ((25.0, 80.0), (30.0, 23.0), 0.0),
    "Grey": ((25.0, 76.5), (27.0, 33.0), 90.0),
}

# ── 1. Player boxes ───────────────────────────────────────────────────────
PLAYER_COLOURS = ["Black", "Red", "Yellow", "Blue", "Grey"]

for colour in PLAYER_COLOURS:
    player_box = project.box(
        BoxType.CAP,
        f"PlayerBox{colour}",
        size=(PLAYER_BOX_WIDTH, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT),
        expandable=False,
        lid=LidBuilder(
            text="Player",
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
            pattern=LEAF_LID,
            text_color=Color("white"),
        ),
    )
    # One compartment spanning the interior, whose elements are the piece slots.
    player_box.compartment(
        "Pieces",
        size=(PLAYER_INNER_W, PLAYER_INNER_L),
        depth=PLAYER_INNER_H,
        position=(0.0, 0.0),
        elements=player_box_elements(colour),
    )

# ── 2. Material boxes ─────────────────────────────────────────────────────
# The layout places four material boxes by colour; the original prints one lid
# per material, so each box is named for the material it holds.
MATERIAL_BOXES = [
    ("Food", "red"),
    ("Stone", "grey"),
    ("Honey", "yellow"),
    ("Wood", "brown"),
]

MATERIAL_INNER_W = MATERIAL_BOX_WIDTH - 2 * WALL
MATERIAL_INNER_L = MATERIAL_BOX_LENGTH - 2 * WALL
MATERIAL_INNER_H = MATERIAL_BOX_HEIGHT - LID - FLOOR

for material, colour in MATERIAL_BOXES:
    material_box = project.box(
        BoxType.CAP,
        f"MaterialBox{material}",
        size=(MATERIAL_BOX_WIDTH, MATERIAL_BOX_LENGTH, MATERIAL_BOX_HEIGHT),
        expandable=False,
        lid=LidBuilder(
            text=material,
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
            pattern=LEAF_LID,
            text_color=Color(colour),
        ),
    )
    # A single rounded well filling the interior (RoundedBoxAllSides).
    material_box.compartment(
        "Materials",
        size=(MATERIAL_INNER_W, MATERIAL_INNER_L),
        depth=MATERIAL_INNER_H,
        position=(0.0, 0.0),
        rounded_corners=MATERIAL_INNER_H - 2,
    )

# ── 3. Card boxes ─────────────────────────────────────────────────────────
# Declared in the layout frame: the original spins the printed box 90 degrees,
# so its [73, 98] footprint sits in the box as [98, 73].
CARD_INNER_W = CARD_BOX_WIDTH - 2 * WALL
CARD_INNER_L = CARD_BOX_LENGTH - 2 * WALL
CARD_INNER_H = CARD_BOX_HEIGHT - LID - FLOOR

CARD_BOXES = [
    ("Favor", "Favors"),
    ("Hero", "Heros"),
    ("Solo", "Solo"),
]

for card_type, lid_text in CARD_BOXES:
    card_box = project.box(
        BoxType.SLIDING,
        f"CardBox{card_type}",
        size=(CARD_BOX_WIDTH, CARD_BOX_LENGTH, CARD_BOX_HEIGHT),
        expandable=False,
        no_rotate=True,
        lid=LidBuilder(
            text=lid_text,
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
            pattern=LEAF_LID,
            text_color=Color("white"),
        ),
    )
    card_box.compartment(
        "Cards",
        size=(CARD_LENGTH + 1, CARD_WIDTH + 1),
        depth=CARD_INNER_H,
        position=(0.0, 0.0),
        finger_scoop=True,
    )

# ── 4. Player card boxes ──────────────────────────────────────────────────
PLAYER_CARD_INNER_W = PLAYER_CARD_BOX_WIDTH - 2 * WALL
PLAYER_CARD_INNER_L = PLAYER_CARD_BOX_LENGTH - 2 * WALL
PLAYER_CARD_INNER_H = PLAYER_CARD_BOX_HEIGHT - LID - FLOOR

PLAYER_CARD_COLOURS = ["Black", "Blue", "Yellow", "Grey", "Red"]

for colour in PLAYER_CARD_COLOURS:
    player_card_box = project.box(
        BoxType.SLIDING,
        f"CardBoxPlayer{colour}",
        size=(PLAYER_CARD_BOX_WIDTH, PLAYER_CARD_BOX_LENGTH, PLAYER_CARD_BOX_HEIGHT),
        expandable=False,
        no_rotate=True,
        lid=LidBuilder(
            text="Player",
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
            pattern=LEAF_LID,
            text_color=Color(colour.lower()),
        ),
    )
    player_card_box.compartment(
        "Cards",
        size=(CARD_WIDTH + 1, CARD_LENGTH + 1),
        depth=PLAYER_CARD_INNER_H,
        position=((PLAYER_CARD_INNER_W - CARD_WIDTH) / 2, 0.0),
        finger_scoop=True,
    )

# ── 5. Common box ─────────────────────────────────────────────────────────
common_box = project.box(
    BoxType.CAP,
    "CommonBox",
    size=(COMMON_BOX_WIDTH, COMMON_BOX_LENGTH, COMMON_BOX_HEIGHT),
    expandable=False,
    lid=LidBuilder(
        text="Trophy",
        label_mode=LabelMode.FRAMELESS,
        diagonal=True,
        pattern=LEAF_LID,
        text_color=Color("white"),
    ),
)


def common_box_elements() -> tuple[CompartmentElement, ...]:
    """Hex tile stacks, the trophy well and the trophy marker (`CommonBox`)."""
    import math

    # PolygonApothemFromRadius(radius, 6) == radius * cos(30) * 2 in components.scad.
    hex_apothem = HEX_SIZE / 2 * math.cos(math.radians(30)) * 2
    hex_pocket = pocket(COMMON_INNER_H, CARDBOARD_TOKEN_THICKNESS * 10 - 0.5)

    hexes = []
    for i in range(2):
        for j in range(3):
            if i == 1 and j == 2:
                continue  # the original leaves this cell out
            hexes.append(
                centered(
                    None,
                    (
                        (hex_apothem / 2 + 4.5) * (1 + i * 2),
                        HEX_SIZE / 2 + 10 + (HEX_SIZE + 10) * j,
                    ),
                    (HEX_SIZE, HEX_SIZE),
                    shape=ElementShape.HEXAGON,
                    rotation=30.0,
                    label=f"hex_{i}_{j}",
                    **hex_pocket,
                )
            )

    trophy_pocket = pocket(COMMON_INNER_H, CARDBOARD_TOKEN_THICKNESS * 6 - 0.5)
    trophy_y = COMMON_INNER_L - (TROPHY_WIDTH / 2 + 2)
    trophies = [
        centered(
            None, (COMMON_INNER_W / 2, trophy_y), (TROPHY_LENGTH, TROPHY_WIDTH),
            shape=ElementShape.RECT, label="trophies", **trophy_pocket,
        ),
        centered(
            None, (COMMON_INNER_W / 2 + TROPHY_LENGTH / 2, trophy_y), (30.0, 30.0),
            shape=ElementShape.SPHERE_SCOOP, label="trophy_grip_right", **trophy_pocket,
        ),
        centered(
            None, (COMMON_INNER_W / 2 - TROPHY_LENGTH / 2, trophy_y), (30.0, 30.0),
            shape=ElementShape.SPHERE_SCOOP, label="trophy_grip_left", **trophy_pocket,
        ),
    ]

    marker_pocket = pocket(COMMON_INNER_H, WOOD_TOKEN_THICKNESS + 0.5)
    marker_x = COMMON_INNER_W * 3 / 4
    marker_y = COMMON_INNER_L - WOOD_TOKEN_DIAMETER / 2 - 7 - HEX_SIZE
    marker = [
        centered(
            None, (marker_x, marker_y), (WOOD_TOKEN_DIAMETER, WOOD_TOKEN_DIAMETER),
            shape=ElementShape.CIRCLE, label="trophy_marker", **marker_pocket,
        ),
        centered(
            None, (marker_x + WOOD_TOKEN_DIAMETER / 2, marker_y), (20.0, 20.0),
            shape=ElementShape.SPHERE_SCOOP, label="marker_grip_right", **marker_pocket,
        ),
        centered(
            None, (marker_x - WOOD_TOKEN_DIAMETER / 2, marker_y), (20.0, 20.0),
            shape=ElementShape.SPHERE_SCOOP, label="marker_grip_left", **marker_pocket,
        ),
    ]

    return (*hexes, *trophies, *marker)


common_box.compartment(
    "Contents",
    size=(COMMON_INNER_W, COMMON_INNER_L),
    depth=COMMON_INNER_H,
    position=(0.0, 0.0),
    elements=common_box_elements(),
)

# ── 6. Arrangement ────────────────────────────────────────────────────────
# The original hand-types 21 sets of coordinates. Here the structure is written
# down instead and the positions fall out of the box sizes: three columns, each
# a set of rows, each row a stack. Change a box's size and everything downstream
# of it moves on its own.
project.arrange(columns(
    # Left column — player boxes two deep, with the material boxes on top.
    rows(
        stack("PlayerBoxBlack", "PlayerBoxYellow", "PlayerBoxGrey",
              rows("MaterialBoxHoney", "MaterialBoxWood")),
        stack("PlayerBoxRed", "PlayerBoxBlue",
              rows("MaterialBoxFood", "MaterialBoxStone")),
    ),
    # Middle column — the three shared card decks, full height.
    rows("CardBoxFavor", "CardBoxHero", "CardBoxSolo"),
    # Right column — the player card decks stacked five high, then the
    # common box behind them.
    rows(
        stack(*(f"CardBoxPlayer{colour}" for colour in PLAYER_CARD_COLOURS)),
        "CommonBox",
    ),
))

# ── 7. Spacers ────────────────────────────────────────────────────────────
# Not declared. `generate_spacers=True` sweeps the leftover volume, merges the
# pieces that fuse into one box, and emits three trays at the same corners as
# the original's SpacerPlayer, SpacerSide and SpacerFront — see the expected
# footprints asserted in tests/test_pyboxbuilder/test_emberleaf.py.


if __name__ == "__main__":
    import os
    if os.environ.get("FROM_MAKE") == "1":
        result = project.export("output/")
        print(f"Exported {result.total_files} files ({len(result.written)} written, "
              f"{len(result.skipped)} unchanged):")
        for file in result.written:
            print(f"  + {file}")
        for bounds in project.piece_bounds:
            print(f"    {bounds}")

    else:
        project.show()
