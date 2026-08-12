# Implementation Plan: Board Game Box Library

**Branch**: `001-board-game-box-library` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-board-game-box-library/spec.md`

## Summary

Build a new strictly-typed PythonSCAD library under `spec_driven/` with a single-import API. The design is fresh — not wrapping the existing box pipeline. Borrowed from the existing codebase: tessellation algorithms (penrose, pentagon families, voronoi), 2D shape generators (coin, hexagon, rounded rects), and pybosl2 CSG primitives. Everything else — the box construction pipeline, lid decoration pipeline, builder API, compartment layout, export, and caching — is designed from scratch to avoid constraints inherited from the legacy codebase.

## Technical Context

**Language/Version**: Python 3.12+ with strict type annotations (`py.typed` marker)

**Primary Dependencies**: pybosl2 >= 0.7.8 (CSG geometry), numpy, pymeshlab >= 0.2.0 (Hausdorff mesh comparison)

**Borrowed from existing code**: Tessellation generators (`penrose_tiling.py`, `pentagon_tilings.py`, `tesselations/`), shape generators (`shapes.py` coin/hex/etc.), and pybosl2's `cuboid()`/`cylinder()`/boolean CSG. These are algorithm libraries, not architecture constraints.

**Storage**: Disk JSON cache (`spec_driven/.layout_cache.json`), 3MF files + `layout.pdf` in `{out_dir}/{game}/mmu/`, `{out_dir}/{game}/single/`, and `{out_dir}/{game}/layout.pdf`

**Testing**: `unittest` two-tier: fast pure-Python and full PythonSCAD render. `pyright` strict mode for type checking.

**Target Platform**: macOS (PythonSCAD.app), cross-platform Python

**Project Type**: Greenfield Python library inside `spec_driven/`, single-import strictly-typed API

**Performance Goals**: Full bin-packing may take longer on first run (complex layouts). Once cached (SHA-256 hit), regeneration completes in: 20-compartment layout < 1s, 6-sub-box auto-size < 2s, Hausdorff-based 3MF write-if-changed. Cached re-exports with zero geometry changes complete in < 0.5s.

**Constraints**: Enums for all type selections, no bare strings, no dict parameter objects, typed builders per box type, no import of existing `box_base.py`/`lids_base.py` architecture, CSG over SDF, Apache-2.0 header. **ALL geometry MUST use pybosl2 solids (`cuboid`, `cylinder`, `sphere`, `prismoid`, etc.) and pybosl2 2D shapes/paths — never import `pythonscad` or any native OpenSCAD built-in directly.**

**Scale/Scope**: 14 box types (new implementations), 12 typed builders, 4 public enums, single public import surface

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Developer Experience First | PASS | Single `from spec_driven import Project, BoxType, ...`; enums prevent typos; typed builders give IDE autocomplete; fresh lid design not constrained by legacy |
| II. Single Source of Truth | PASS | Each box type's config lives on its typed builder; `BoxSpec` equivalent is frozen; lid decoration is one `LidBuilder` |
| III. Performance by Design | PASS | Layout cache with SHA-256 hash, Hausdorff skip-if-unchanged, CSG over SDF |
| IV. Test-First | PASS | All new code tested; measurement-based geometry assertions; regression tests |
| V. Documented by Default | PASS | All enums/builders/functions fully docstringed; Earth Animal Kingdom is reference |

**Gate Result**: All pass.

## Project Structure

### Source Code (repository root)

```text
spec_driven/                    # NEW: Greenfield package
├── __init__.py                 # Re-exports public surface
├── py.typed                    # PEP 561 marker for downstream type checking
├── enums.py                    # BoxType, LabelMode, PatternType, ScoopSide
├── color.py                    # Color dataclass with named presets
├── project.py                  # Project class (top-level API)
├── builders/                   # Typed per-box-type builders
│   ├── _base.py                # BoxBuilder base
│   ├── sliding.py              # SlidingBoxBuilder
│   ├── cap.py                  # CapBoxBuilder
│   ├── hinge.py                # HingeBoxBuilder
│   ├── filament_hinge.py       # FilamentHingeBoxBuilder
│   ├── magnetic.py             # MagneticBoxBuilder
│   ├── inset.py                # InsetBoxBuilder
│   ├── sliding_catch.py        # SlidingCatchBoxBuilder
│   ├── slipover.py             # SlipoverBoxBuilder
│   ├── slipover_path.py        # SlipoverPathBoxBuilder
│   ├── cap_path.py             # CapPathBoxBuilder
│   ├── no_lid.py               # NoLidBoxBuilder, PathBoxBuilder
│   └── card_library.py         # CardLibraryBoxBuilder
├── lid/                        # NEW: Fresh lid decoration pipeline
│   ├── builder.py              # LidBuilder, PatternBuilder
│   ├── label.py                # Label generation (framed, frameless, diagonal)
│   ├── pattern.py              # Pattern fill: hex grid, grid, voronoi through-holes
│   └── color_layers.py         # Color layer assignment for MMU
├── box/                        # NEW: Fresh box construction pipeline
│   ├── base.py                 # Abstract box type definition
│   ├── registry.py             # BoxType enum → box class dispatch
│   ├── types/                  # 14 box type implementations
│   │   ├── sliding.py, cap.py, hinge.py, ...
│   └── interior.py             # Interior frame and hollowing
├── compartments/               # NEW: Fresh compartment layout
│   ├── builder.py              # CompartmentBuilder
│   ├── finger_hole.py          # Finger scoop/notch geometry
│   ├── layout.py               # 2D shelf-based auto-layout
│   └── sizing.py               # Auto-sizing expansion logic
├── packing/                    # NEW: Fresh nested box packing
│   ├── layout.py               # 3D box packing into game box
│   ├── spacer.py               # Spacer tray generation
│   └── cache.py                # Two-level cache (memory + disk JSON)
├── export/                     # NEW: Fresh 3MF export
│   ├── exporter.py             # BoxExporter
│   ├── result.py               # ExportResult
│   ├── hausdorff.py            # pymeshlab-based conditional write
│   └── layout_pdf.py           # PDF packing guide generation
├── shapes/                     # BORROWED: Existing shape generators
│   └── (coin, hexagon, rounded rect, etc. from shapes.py)
└── tesselations/               # BORROWED: Existing tessellation generators
    └── (penrose, pentagon, voronoi, etc.)

spec_driven.py                  # SINGLE IMPORT at repo root:
                                #   from spec_driven import Project, BoxType, ...

boxes/                          # Per-game insert projects
├── earth_animal_kingdom/
│   └── earth_animal_kingdom.py

tests/
├── test_spec_driven/           # NEW: Tests for spec_driven
│   ├── test_enums.py
│   ├── test_builders.py
│   ├── test_project.py
│   ├── test_lid_label.py
│   ├── test_lid_pattern.py
│   ├── test_compartments.py
│   ├── test_packing.py
│   ├── test_export.py
│   └── render/
│       ├── test_box_render.py
│       ├── test_lid_render.py
│       └── test_export_render.py
```

**Structure Decision**: `spec_driven/` is a greenfield package sharing the repo with the existing codebase. It borrows tessellation and shape algorithms but defines its own box pipeline, lid pipeline, builders, packing, and export. `spec_driven.py` at the repo root is the single public import. The existing root `.py` files remain untouched — they continue to work for existing users. This is an additive package, not a replacement.

## Borrowed vs. Fresh

| Component | Status | Rationale |
|-----------|--------|-----------|
| Tessellations (penrose, pentagon, voronoi) | Borrowed | Pure algorithms, no pipeline coupling |
| 2D shape generators (coin, hex, rounded rect) | Borrowed | Pure geometry functions |
| pybosl2 CSG (cuboid, cylinder, boolean ops) | Dependency | External library, not our code |
| Box construction pipeline | **Fresh** | New base class, new builder→geometry mapping |
| Lid decoration pipeline | **Fresh** | Not constrained by `LidPlate`/`build_lid()` contract |
| Compartment layout | **Fresh** | New auto-layout with row alignment |
| Nested box packing | **Fresh** | Fill-to-fit rows, spacer generation. Integrates dynamic dimension expansion based on 3D packing solvers, and propagates resolved sizes back to builders using a `final_size` attribute. |
| 3MF export | **Fresh** | New exporter, same pymeshlab backend |
| Typed builder API | **Fresh** | Enums, typed dataclasses, `@overload` dispatch. Adds a unique `box_id` field to distinguish duplicate instances. |
| Caching strategy | **Fresh** | Same SHA-256 approach, new cache file. Stores 3D box packing layouts in `.layout_cache.json` to bypass solver on subsequent runs. |
| PDF packing guide | **Fresh** | 3D angle view of packed layout with box labels, dimensions, packing order. Cached regeneration. |

## Earth Animal Kingdom Example Migration

The reference example under `boxes/earth_animal_kingdom/` must faithfully port the original design (`examples/earth_animal_kingdom.py` / `.scad`) to the new `spec_driven` Project API. The original design is more complex than the initial simplified port and must include all components.

### Game Box

- **Retail box**: 288mm × 158mm × 47mm (W × L × H)
- **Defaults**: wall_thickness=2.0, floor_thickness=1.6, lid_thickness=2.0, gap_threshold=10.0, min_spacer_dim=15.0

### Boxes (7 total)

| Box | Type | Dimensions (mm) | Contents |
|-----|------|-----------------|----------|
| AnimalCardsBox | Sliding | ~76 × box_length × ~24 | 36 animal cards (72×123mm each, stacked 6mm per 10 cards = 21.6mm total) |
| SproutBox | Filament Hinge | ~76 × box_length × ~13 | 50 sprout cubes (8mm³ each) |
| CanopyBox | Filament Hinge | ~38 × box_length × ~46 | 20 canopy tokens |
| AnimalBox | Slipover | fills remaining width × box_length × ~13 | 3D bin-packed animal tokens (half) — custom-shaped compartments with 0.2mm raised floor labels per animal |
| AnimalBox2 | Slipover | same as AnimalBox | 3D bin-packed animal tokens (other half) — custom-shaped compartments with raised floor labels |
| SpacerBox | No Lid | matches AnimalBox × 1.0 | Hollow spacer tray |
| Boards | No Lid | 174 × 150 × 6 | Board stack |

### Animal Token Inventory (37 entries, 31 unique species)

Ported from `ANIMAL_PIECES` in `examples/earth_animal_kingdom.py`. Each entry: `object(width=W, length=L[, num=N])`. Tokens are 8mm thick. Species with `num > 1` share a single compartment sized to fit all copies.

```python
elephant       = object(width=43.5, length=54)
polar_bear     = object(width=36.5, length=53)
cow            = object(width=36.5, length=47.5)
pig            = object(width=24.5, length=35)
gazelle        = object(width=41,   length=35)
turkey         = object(width=24,   length=25, num=5)
fly            = object(width=11,   length=11)
capybara       = object(width=16.5, length=32, num=2)
capybara_2     = object(width=16.5, length=32, num=3)
monkey         = object(width=29,   length=24)
pangolin       = object(width=16,   length=21, num=5)
deer           = object(width=47,   length=25.5)
goanna         = object(width=25,   length=30)
fox            = object(width=16,   length=35)
snake          = object(width=14,   length=41.5)
rabbit         = object(width=18.5, length=21)
termite        = object(width=12,   length=12, num=5)
ornyx          = object(width=39,   length=40)
platypus       = object(width=14.5, length=25)
lemur          = object(width=22,   length=30)
peacock        = object(width=30,   length=27)
gopher         = object(width=17.5, length=17, num=5)
crocodile      = object(width=16,   length=85)
goat           = object(width=37,   length=36)
jaguar         = object(width=20,   length=49)
rhino          = object(width=36,   length=64)
goose          = object(width=25,   length=21)
eagle          = object(width=31,   length=43)
spider_monkey  = object(width=26.5, length=25)
hoopoe         = object(width=17,   length=16)
kangaroo       = object(width=37,   length=39)
loon           = object(width=26.5, length=13)
tarsier        = object(width=29,   length=12.5)
jay            = object(width=12.5, length=12)
chipmunk       = object(width=15,   length=14)
quokka         = object(width=24,   length=15)
beaver         = object(width=15.5, length=35)
```

### Animal Bin-Packing Strategy

Animal tokens are split into two halves via a best-fit-decreasing 2D bin-packing pass over the two `AnimalBox` containers (each ~165×150mm usable). Within each container, compartments are arranged with 3mm spacing. Multi-quantity species (qty > 1) are stacked in a single compartment whose depth = quantity × 8mm (token thickness). Each compartment floor has the animal name extruded as a 0.2mm raised label. Finger scoops are placed on all compartment front walls.

### Migration Checklist

- [ ] Port all 37 animal entries from `ANIMAL_PIECES` into the `earth_animal_kingdom.py` data list
- [ ] Implement multi-quantity compartment stacking (same W×L, depth = qty × 8mm)
- [ ] Wire the 3D bin-packing solver (`packing/layout.py`) to distribute animals across the two AnimalBox containers
- [ ] Generate labeled compartment floors (0.2mm extruded text per animal name)
- [ ] Port the card box with correct 36-card count and finger hole scoop
- [ ] Port the sprout box (50 cubes) and canopy box (20 tokens)
- [ ] Verify all 7 boxes pack within the 288×158mm game box interior
- [ ] Export all files and verify against original `examples/release/earth_animal_kingdom/` output

## Complexity Tracking

> No violations.
