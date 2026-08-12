# Earth Animal Kingdom Board Game Insert

Generates 3MF printable files for organizing the Earth board game box.

## Boxes

| Box | Type | Dimensions | Contents |
|-----|------|------------|----------|
| AnimalCards | Sliding | 110×80×40mm | Deck + Discard with finger scoops |
| Animals1 | Filament Hinge | 130×55×30mm | Lion, Elephant, Eagle, Bear — per-animal compartments with finger scoops |
| Animals2 | Filament Hinge | 130×55×30mm | Wolf, Fox, Owl, Hawk — per-animal compartments with finger scoops |
| Boards | No Lid | 70×150×15mm | Board storage |

## Usage

```sh
cd /path/to/openscad_boardgame_toolkit
python3 boxes/earth_animal_kingdom/earth_animal_kingdom.py
```

Output files land in `output/EarthAnimalKingdom/mmu/` and `output/EarthAnimalKingdom/single/`.
