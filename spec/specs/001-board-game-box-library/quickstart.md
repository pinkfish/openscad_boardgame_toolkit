# Quickstart: Board Game Box Library

**Date**: 2026-08-11 | **Feature**: specs/001-board-game-box-library

**Package**: `spec_driven/` | **Import**: `from spec_driven import ...`

## Prerequisites

- Python 3.12+ (strict typing)
- PythonSCAD dev build
- pybosl2 >= 0.7.8, numpy, pymeshlab
- pyright (type checking)

```sh
cd /path/to/openscad_boardgame_toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install pybosl2 numpy pymeshlab
```

## The Single Import

```python
from spec_driven import (
    Project,
    BoxType, LabelMode, PatternType, ScoopSide,
    Color, LidBuilder, PatternBuilder,
)
```

## Validation Scenario 1: Type-Safe Box with Lid Decoration

```python
from spec_driven import Project, BoxType, LabelMode, Color, LidBuilder

project = Project("CardGame", game_box_size=(200, 150, 60))

# BoxType.SLIDING → returns SlidingBoxBuilder
cards = project.box(
    BoxType.SLIDING, "Cards",
    size=(180, 70, 50),
    two_layer=True,                    # SlidingBoxBuilder only
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        text_color=Color.WHITE(),
        frame_color=Color(0.9, 0.7, 0.1),
    ),
)

# Type error caught by pyright:
# project.box(BoxType.SLIDING, "Bad", size=(100, 80, 40), cap_height=8.0)
#                       ^^^^^^^^^ SlidingBoxBuilder has no 'cap_height'

project.export("output/")
```

## Validation Scenario 2: Lid with Through-Hole Pattern + Diagonal Text

```python
from spec_driven import Project, BoxType, LabelMode, PatternType, Color, LidBuilder, PatternBuilder

project = Project("FancyGame", game_box_size=(200, 150, 60))

box = project.box(
    BoxType.SLIDING, "Treasure",
    size=(180, 70, 50),
    lid=LidBuilder(
        text="TREASURE",
        label_mode=LabelMode.FRAMED,
        diagonal=True,                 # Corner-to-corner
        text_color=Color.WHITE(),
        frame_color=Color(0.9, 0.7, 0.1),
        pattern=PatternBuilder(
            type=PatternType.HEX_GRID,
            colors=(Color(0.2, 0.6, 0.9),),
        ),
        pattern_color=Color(0.2, 0.6, 0.9),
    ),
)

project.export("output/")
```

**Expected**: Through-holes cut lid. Framed diagonal text with gold frame, white text, blue pattern. 3 accent colors in multi-color 3MF.

## Validation Scenario 3: Multi-Box Game with Auto-Sizing

```python
from spec_driven import Project, BoxType, LidBuilder

project = Project("BigGame", game_box_size=(300, 200, 80))

project.box(BoxType.SLIDING, "CardBox", size=(110, 75, 50))
project.box(BoxType.CAP, "TokenBox", size=(60, 50, 30))
project.box(BoxType.CAP, "DiceBox", size=(60, 50, 30))
project.box(BoxType.FILAMENT_HINGE, "BitBox", size=(80, 60, 40))

result = project.export("output/")
assert len(result.written) > 0

# Second export (unchanged) → all skipped
result2 = project.export("output/")
assert len(result2.written) == 0
```

## Validation Scenario 4: Min Text Height Guard

```python
from spec_driven import Project, BoxType, LabelMode, Color, LidBuilder

project = Project("TinyGame", game_box_size=(100, 80, 30))
box = project.box(
    BoxType.SLIDING, "Tiny",
    size=(30, 20, 20),
    lid=LidBuilder(text="A", min_text_height_mm=4.0),
)

result = project.export("output/")
# Lid exports without text — "A" @ 30x20mm lid = < 4mm text height → skipped
```

## Validation Scenario 5: Auto-Computed Box Size from Compartments

```python
from spec_driven import Project, BoxType, ScoopSide

project = Project("ComputedBox", game_box_size=(200, 150, 60))

# No `size=` specified — computed from compartments
cards = project.box(BoxType.SLIDING, "CardBox")

# These compartments drive the minimum box size
cards.compartment("Deck", size=(90, 65), depth=45)
cards.compartment("SideSlot", size=(55, 45), depth=25)

# The box minimum = 90+55+walls+spacing wide × 65+walls long
# Depth drives height = 45+floor+lid

result = project.export("output/")
# Box auto-sized to fit its compartments, then expanded to fill the game box row
```

**Expected**: CardBox minimum dimensions computed from Deck + SideSlot compartments. Box expands during packing. If `size` were explicitly set, compartments would be validated against it instead.

## Validation Scenario 6: Earth Animal Kingdom

```python
from spec_driven import (
    Project, BoxType, LabelMode, Color,
    LidBuilder, PatternBuilder, PatternType, ScoopSide,
)

project = Project("EarthAnimalKingdom", game_box_size=(288, 158, 47))

cards = project.box(
    BoxType.SLIDING, "AnimalCards",
    size=(100, 70, 40),
    lid=LidBuilder(text="Animal Cards", label_mode=LabelMode.FRAMED),
)
cards.compartment("Deck", size=(90, 65), depth=36, finger_scoop=True)

for i in range(2):
    b = project.box(
        BoxType.FILAMENT_HINGE, f"AnimalBox{i+1}",
        size=(70, 55, 30),
        lid=LidBuilder(text=f"Animals {i+1}"),
    )
    b.compartment("Tokens", size=(65, 50), depth=26, finger_scoop=True)

project.box(BoxType.NO_LID, "Boards", size=(70, 150, 15), expandable=False)

project.export("output/")
```

## Type Checking

```sh
npx pyright spec_driven/enums.py spec_driven/builders/
npx pyright boxes/earth_animal_kingdom/earth_animal_kingdom.py
```

## Running Tests

```sh
python3 tests/run_fast.py test_spec_driven
python3 -m unittest discover -s tests -p "test_*.py"
```
