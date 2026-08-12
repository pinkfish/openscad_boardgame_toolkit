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

**Constraints**: Enums for all type selections, no bare strings, no dict parameter objects, typed builders per box type, no import of existing `box_base.py`/`lids_base.py` architecture, CSG over SDF, Apache-2.0 header. **Do not reinvent the wheel — use classes that already exist in pybosl2 wherever possible.** ALL geometry MUST use pybosl2 solids (`cuboid`, `cylinder`, `sphere`, `prismoid`, etc.) and pybosl2 2D shapes/paths — never import `pythonscad` or any native OpenSCAD built-in directly. Use bosl2 basic pieces (`cube`, `cylinder`, `sphere`, `linear_extrude`, etc.) wherever possible instead of higher-level shape generators. **Do NOT implement a Color class. Use `pybosl2.Color` directly.** No wrapper, no custom implementation, no fallback. pybosl2's Color supports webcolor names: use names like `Color("darkgreen")`, `Color("gold")` instead of hardcoding RGB values. **Do NOT define preset constants** (no `WHITE`, `BLACK`, etc.) — just use `Color("white")`, `Color("black")` directly at the call site. The `spec_driven/color.py` file must not exist. Minimum dimensional precision is 0.1mm — no rounding to whole millimetres. Compartments support ratio-based sizing (`width_ratio`, `length_ratio`) as an alternative to absolute dimensions; ratios are validated to sum ≤ 1.0 per row. Lid labels support per-export-mode overrides: `mmu_label` and `single_label` sub-configurations enable different label styles per material mode (e.g., frameless for MMU, framed for single). Compartment labels render as single-layer engraved cutouts for single-color and raised MMU second-color text for multi-color. Boxes support a `no_rotate` flag (default `False`) so directionally-constrained boxes opt out of packer rotation (FR-013c). When the packer rotates a box, its compartments are re-laid-out in the rotated interior frame (FR-013b). Standalone boxes export without a game box/packing (FR-037). No-lid boxes support stackable rims (inside/outside, FR-038) and round/rectangular side magnet slots (FR-039).

**Scale/Scope**: 14 box types (new implementations), 12 typed builders, 4 public enums, single public import surface, 3 reference examples (Earth Animal Kingdom, Stackable Hexes, Irish Gauge)

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
│   ├── pattern.py              # Pattern fill: full ShapeType catalog (dense/lattice shapes, pentagon tilings, tessellations) as through-holes
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
| Tessellations (penrose, pentagon R1–R15, voronoi, lizard, goose, chicken, kite, hex, quad) | Borrowed | Pure algorithms, no pipeline coupling. Ported from `tesselations/`, `pentagon_tilings.py`, and `patterns.py` `ShapeType` enum (42 members) |
| 2D shape generators (coin, hex, rounded rect) | Borrowed | Pure geometry functions |
| pybosl2 CSG (cuboid, cylinder, boolean ops) | Dependency | External library, not our code |
| Box construction pipeline | **Fresh** | New base class, new builder→geometry mapping |
| Lid decoration pipeline | **Fresh** | Not constrained by `LidPlate`/`build_lid()` contract |
| Compartment layout | **Fresh** | New auto-layout with row alignment |
| Nested box packing | **Fresh** | Fill-to-fit rows, spacer generation. Integrates dynamic dimension expansion based on 3D packing solvers, and propagates resolved sizes back to builders using a `final_size` attribute. |
| 3MF export | **Fresh** | New exporter, same pymeshlab backend |
| Typed builder API | **Fresh** | Enums, typed dataclasses, `@overload` dispatch. Adds a unique `box_id` field to distinguish duplicate instances. |
| Caching strategy | **Fresh** | Same SHA-256 approach, new cache file. Stores 3D box packing layouts in `.layout_cache.json` to bypass solver on subsequent runs. |
| PDF packing guide | **Fresh** | Standards-compliant valid PDF with scaled 2D top-down box layout, labels, dimensions, packing order numbers. Layered exploded breakdown with arrow connectors. Cached regeneration via SHA-256 layout hash. |

## Earth Animal Kingdom Example Migration

The reference example under `boxes/earth_animal_kingdom/` must faithfully port the original design (`examples/earth_animal_kingdom.py` / `.scad`) to the new `spec_driven` Project API. The original design is more complex than the initial simplified port and must include all components.

### Game Box

- **Retail box**: 288mm × 158mm × 47mm (W × L × H)
- **Defaults**: wall_thickness=2.0, floor_thickness=1.6, lid_thickness=2.0, gap_threshold=10.0, min_spacer_dim=15.0
- **Design principle**: All box dimensions are **generated** from the game box size and content constraints — no fixed sizes. The example demonstrates the `size=None` auto-compute pattern: each box's minimum is derived from its compartments, and the packing solver expands boxes to fill available space within the 288×158mm game box interior.

```python
box_width  = 288
box_length = 158
box_height = 47

# Additional items that share the game box interior
score_pad_width     = 81
score_pad_length    = 99
score_pad_thickness = 5
score_pad_number    = 1

# Card dimensions (computed from card count, not hardcoded box size)
animal_card_num = 36
card_10_thickness = 6
single_card_thickness = card_10_thickness / 10
animal_card_size = MakeCardSize(
    length=123,
    width=72,
    single_card_thickness=single_card_thickness
)
# Box auto-sized: card box height = animal_card_num × single_card_thickness + clearance
#                  card box width  = animal_card_size.width + 2 × wall_thickness + clearance
#                  card box length = animal_card_size.length + 2 × wall_thickness + clearance
```

### Boxes (7 total, all sizes generated — no hardcoded dimensions)

Each box uses a distinct body color so they can be told apart at a glance during unpacking and assembly.

| Box | Type | Color | Sizing Strategy | Contents |
|-----|------|-------|-----------------|----------|
| AnimalCardsBox | Sliding | `Color("darkgreen")` | Width = card width + 2×wt + tolerance. Length = card length + 2×wt + tolerance. Height = card_stack + floor + lid + finger clearance | 36 animal cards |
| SproutBox | Filament Hinge | `Color("lightgreen")` | Min width = 72, min length = 158. Height = sprout height + floor + lid | 50 sprout cubes (8mm³) |
| CanopyBox | Filament Hinge | `Color("olive")` | Width = canopy footprint + 2×wt. Length = card length + 2×wt. Height = canopy stack + floor + lid | 20 canopy tokens |
| AnimalBox1 | Slipover | `Color("gold")` | Width, length, height **generated by 3D bin-packing solver** from half of ANIMAL_PIECES list | 18–19 animal token compartments |
| AnimalBox2 | Slipover | `Color("orange")` | Same as AnimalBox1 — second half of animals, different color for distinction | 18–19 animal token compartments |
| SpacerBox | No Lid | `Color("lightgrey")` | Auto-generated by packing solver to fill remaining game box gaps | Hollow tray |
| Boards | No Lid | `Color("darkgrey")` | Width = 174, length = 150, height = score_pad_thickness × score_pad_number | Score pad + board stack |

**Color specification**: pybosl2's `Color` supports webcolor names (e.g., `Color("darkgreen")`, `Color("gold")`, `Color("orange")`). Do NOT hardcode RGB numbers in project files — use webcolor names. See pybosl2's color table for supported names.

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

### 3D Oblique Exploded PDF Guide Layout
To satisfy the layout guide requirements, `layout_pdf.py` renders the game box and nested sub-boxes in a 3D Cabinet Oblique Projection across multiple pages representing distinct stacking layers:
* **Projection Math**: 
  * `X` maps to `x + y * cos(30) * 0.45`
  * `Y` (Z-axis height / layers) maps to `-z - y * sin(30) * 0.45`
  * This projects coordinates from 3D space onto the 2D PDF plane looking slightly from above and to the side.
* **Layer-by-Layer Stacking Breakdown**:
  * Placements are grouped dynamically into three primary layers:
    1. **Base Layer** (`z < 0.1` mm): Boxes sitting directly on the box floor.
    2. **Middle Layer** (`0.1 <= z < H * 0.7` mm): Stacked middle boxes.
    3. **Top Layer** (`z >= H * 0.7` mm): Top-level boards and cards.
  * For each layer, a separate page is generated in the PDF guide:
    * The boxes and spacers belonging to the active layer are drawn in full color.
    * The boxes belonging to the lower layers (already packed in previous steps) are drawn in light gray to provide background context.
    * Boxes belonging to upper layers are hidden.
  * Each box is drawn as a 3D-shaded block, complete with a label and packing order index.
  * The text labels on the boxes in the layout PDF must be visible, larger, and highly readable. If a label is blocked/hidden because another box is stacked on top of it, the label text must be shifted to the side. The text label must only display the box's label, and not display its size/dimensions.
  * Hollow spacer boxes (which can be non-rectangular using 2D polygon paths) are generated to fill all open spaces/gaps, making the insert layout complete to the full extent of the game box. Spacer boxes/trays cannot be thinner than 5mm in any dimension (width, length, or height) to prevent printing extremely fragile slivers. For vertical gaps along the Z-axis, a spacer box is generated if the gap height is >= 3mm (subject to the 5mm minimum thickness rule). If the gap height is < 3mm, the adjacent box's height expands to absorb the gap, prioritizing expansion on the X and Y axes over the Z-axis. Spacer boxes must also be rendered in the layout PDF.
  * A clearance slack of 1-2mm is applied in the X and Y directions around nested sub-boxes relative to the game box walls or neighboring boxes to ensure they can be easily placed and removed from the game box.
  * The animal boxes inside the Earth Animal Kingdom layout must have heights matching exactly the token thickness (8mm) plus the floor and lid thicknesses, plus 0.5mm slack (yielding 12.1mm outer height), with spacer boxes generated on top to fill the remaining height.


### Compartment Auto-Layout with Rotation
To ensure dense packing of compartments (like the animal compartments in `AnimalBox1` and `AnimalBox2`), `layout_compartments` implements a shelf-packing algorithm with 90-degree rotation support:
* **Sorting Heuristic**: Compartments are sorted by their maximum dimension (width or length) in descending order to establish a clean starting baseline.
* **Rotation Evaluation**: For each compartment, the engine evaluates both the original orientation `(w, l)` and the rotated orientation `(l, w)`. It prefers the orientation that fits in the current row while minimizing row height increase. If neither fits in the current row, it wraps to a new row and evaluates both orientations there.

### Box Rotation Propagation to Compartments
When the 3D box packer rotates a sub-box by 90 degrees (swapping width and length), the compartment layout MUST be re-generated in the rotated interior frame:
* **Post-Rotation Interior**: `Project.export()` uses the placement's `rotation` flag and final (possibly swapped) `final_size` to compute the interior, then re-runs `layout_compartments` against that rotated interior.
* **Content Alignment**: Compartments are laid out using the box's post-rotation width/length so contents stay aligned with the actual printed box walls.
* **`no_rotate` Opt-Out**: A box whose contents are directionally constrained (e.g., the Irish Gauge money box, whose 3 card slots span the width) sets `no_rotate=True`. The packer then only considers the original orientation for that box, and the compartment layout always matches its natural direction.

### Multi-Bin Compartment Packing API
To allow compartments to be dynamically partitioned across multiple boxes (like the two animal boxes), the `Project` class implements `project.share_compartments(boxes, compartments)`:
* **Boxes Registration**: Registers a list of box labels (e.g. `["AnimalBox1", "AnimalBox2"]`) and a shared list of compartments.
* **Auto-Partitioning during Export**: During `Project.export()`, the engine automatically computes the interior sizes of these boxes, runs the multi-bin backtracking shelf-packer solver to partition the shared compartments across the boxes, and populates the compartments of each box builder before geometry generation!

### Main Earth Insert Sizing Rules
To match the original layout in the main game box:
* **Card Boxes Footprint**: All card boxes (both Earth and non-Earth/small card boxes) and player boxes MUST have a fixed, identical footprint of `(68.0, 99.0)`.
* **Full Height Card Boxes**: The primary card boxes (`EarthCardBox1`, `EarthCardBox2`, `EarthCardBox3`, and `EarthCardBox4`/`EarthCardBox` in the second row) MUST have a fixed height of exactly `55.2` mm to sit directly under the player boards (which occupy the remaining `16.8` mm height).
* **Non-Earth Card Boxes Stack**: The non-Earth card boxes (Ecosystem, Fauna, Island, Climate, Solo, Season, Abundance, and Start) MUST declare their exact minimum heights based on card counts, plus floor and lid thicknesses. The layout engine will stack them into columns that sum to exactly `55.2` mm.
* **Player Boxes Stack**: The 6 player boxes MUST also have a footprint of `(68.0, 99.0)`. Their heights MUST be flexible (defaulting to `9.2` mm each) so they stack exactly 6-high to sum to the `55.2` mm column height.

### Height Constraints & Packing Tradeoffs
Since the game box height is `47.0` mm, raising the sprout box height to `30.0` mm and locking the card box to `29.2` mm makes it impossible to stack the two `12.5` mm animal boxes on top of the sprout box (`12.5 + 12.5 + 34.1 = 59.1` mm). The system must be configured to place these boxes side-by-side or adjust heights/footprints accordingly.

### Migration Checklist

- [x] Port all 37 animal entries from `ANIMAL_PIECES` into the `earth_animal_kingdom.py` data list using `object(width=, length=, num=)` format
- [x] Implement multi-quantity compartment stacking (same W×L, depth = qty × 8mm)
- [ ] Wire the 3D bin-packing solver (`packing/layout.py`) to distribute animals across the two AnimalBox containers
- [ ] Generate labeled compartment floors (0.2mm extruded text per animal name)
- [x] Port the card box with correct 36-card count and finger hole scoop
- [x] Port the sprout box (50 cubes) and canopy box (20 tokens)
- [ ] Verify all 7 boxes pack within the 288×158mm game box interior
- [x] Export all files and verify against original `examples/release/earth_animal_kingdom/` output

## Stackable Hexes Example

The `boxes/stackable_hexes/` example ports `examples/stackable_hexes.py` to the new `spec_driven` Project API. It demonstrates three new features: standalone boxes, stackable no-lid boxes, and side magnets.

### Reference (from `examples/stackable_hexes.py`)

The original design creates hexagonal boxes (`PathBox.regular_polygon(sides=6)`) that are:
- **Standalone** — each box is a single `PathBox` generated independently via `@make_box`, with no game box and no packing phase.
- **Stackable** — `stackable=STACKABLE_TYPE_INSIDE` (recess on the top rim nests into the box above; outside-fit `STACKABLE_TYPE_OUTSIDE` also available).
- **Magnetic** — round magnets (default 6×3mm) or rectangular magnets (default 10×5×2mm) in the side walls via `magnet=SimpleNamespace(type=..., size=[...])`.
- **Divisible** — `HexBoxDivisions` partitions the interior into 1–4 equal hex-sectors with a configurable `bottom_radius`.
- **Hollow or divided** — `hollow(divisions <= 1)`: a single-compartment hex is hollow; multi-compartment hexes use divisions.

### Box Configuration Matrix

| Box | Divisions | Magnet Type | Magnet Size | bottom_radius |
|-----|-----------|-------------|-------------|---------------|
| HexBoxSingle6x3RoundMagnet | 1 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle6x3RoundMagnetWithTwoPartitions | 2 | round | [h/2-1, 7, 2.9] | 5 |
| HexBoxSingle6x3RoundMagnetWithThreePartitions | 3 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle6x3RoundMagnetWithFourPartitions | 4 | round | [h/2-1, 7, 2.9] | — |
| HexBoxSingle10x5x2RectMagnet | 1 | rect | [12, 6, 1.65] | — |
| HexBoxSingle10x5x2RectMagnetWithTwoPartitions | 2 | rect | [12, 6, 1.65] | 10 |
| HexBoxSingle10x5x2RectMagnetWithThreePartitions | 3 | rect | [12, 6, 1.65] | 10 |
| HexBoxSingle10x5x2RectMagnetWithFourPartitions | 4 | rect | [12, 6, 1.65] | 10 |

### Key Parameters

- `stackable_width = 100`, `stackable_height = 24`, `wall_thickness = 4`
- Hexagon: `regular_polygon(sides=6)`, no finger cutouts (`make_finger_x=False`, `make_finger_y=False`)
- Hollow radius: top=2, bottom=stackable_height × 3/4, radius=2
- Magnet slot types: `MAGNET_SLOT_TYPE_ROUND`, `MAGNET_SLOT_TYPE_RECT` (plus `MAGNET_SLOT_TYPE_NONE`)

### spec_driven Migration

- **Standalone boxes**: `Project` must allow a standalone mode where `project.box(...)` is exported directly without a game box. A standalone box skips packing, auto-sizing, layout PDF, and spacer generation (FR-037).
- **Stackable no-lid boxes**: `BoxType.NO_LID` (or a path-box variant) gains `stackable` (inside/outside) with configurable `stackable_thickness` and `stackable_fit_offset` (FR-038).
- **Magnets**: builders gain a `magnet` sub-configuration with `type` (round/rect), `size`, and `count`, placed on opposing sides (FR-039).
- **Hex/polygon path boxes**: `BoxType.SLIPOVER_PATH` / `BoxType.CAP_PATH` / path-box support `regular_polygon(sides=N)` — this is already covered by the non-rectangular box outline support (FR-018).
- **Divisions**: `HexBoxDivisions` maps to `box.compartment(...)` × N where N partitions divide the hexagon into equal sectors.

### Migration Checklist

- [ ] Create `boxes/stackable_hexes/stackable_hexes.py` with all 8 hex box variants from the matrix
- [ ] Implement standalone box export path (no game box, no packing) in `spec_driven/project.py`
- [ ] Implement stackable inside/outside rim generation for no-lid boxes
- [ ] Implement round and rectangular magnet slots on opposing sides
- [ ] Verify hex boxes stack, magnets align, and divisions clip to the hex interior

## Irish Rails (Irish Gauge) Example

The `boxes/irish_gauge/` example ports `examples/irish_gauge.scad` to the new `spec_driven` Project API. This is a game-box insert with mixed box types and hand-placed spacer boxes. The port demonstrates: mixed lid types in one game box, company boxes with shared footprint but different contents, and spacer boxes derived from the leftover space.

### Game Box

- **Retail box**: 214 × 302 × 39mm (W × L × H)
- **Defaults**: wall_thickness=3, lid_thickness=3, board_thickness=10.5

### Box Sizes (pulled from the original layout, computed from game box dimensions)

| Box | Type | Width | Length | Height | Count | Color |
|-----|------|-------|--------|--------|-------|-------|
| CompanyBox | Sliding lid | `box_width / 4` = 53.5 | `card_length * 1.8 + 2*wt` = 133.8 | `(box_height - board_thickness) / 2` = 14.25 | 5 | orange, yellow, red, purple, blue |
| MoneyBox | Filament hinge | `box_width` = 214 | `card_length + 2*wt` = 77 | `box_height - board_thickness` = 28.5 | 1 | — |
| SpacerBoxBack | No-lid path | fills back area | fills back area | `box_height - board_thickness` | 1 | — |
| SpacerBoxCompany | No-lid | `box_width/4` | `company_box_length` | `company_box_height` | 1 | — |

### Company Boxes (5, shared footprint, distinct contents and colors)

Each company box has the same footprint (`53.5 × 133.8 × 14.25`) but different contents driven by its `shares` count:

| Company | Lid label | Color | Shares |
|---------|-----------|-------|--------|
| Belfast and County Down Railway | Belfast | orange | 2 |
| Cork Bandon & South Coast Railway | Cork | yellow | 3 |
| Midland Great Western Railway | Midland | red | 3 |
| Waterford Limerick & Western Railway | Waterford | purple | 4 |
| Great Southern & Western Railway | Great Southern | blue | 4 |

Each company box holds:
- **Share cards**: 49 × 71mm cards, stacked `shares` high (single card thickness = 14/20 = 0.7mm)
- **Dividend markers**: 7.5mm diameter × 3mm thick, in a `CylinderWithIndents` slot with finger holes
- **Trains**: 19 trains per company, each 7.75 × 5.5 × 8mm, in a 6×4 grid well
- **Company name label**: 3-line text (font size 7.75) extruded 0.2mm on the floor

### Money Box

- Filament-hinge lid, 214 × 77 × 28.5mm
- Three card slots (49 × 71mm each) labeled "1", "5", "10" for money denominations (25 cards total)
- "Irish" / "Gauge" text labels extruded on the floor

### Spacer Boxes — automatic definitions (not hand-coded paths)

The original `.scad` hard-codes the `SpacerBoxBack` polygon path and `SpacerBoxCompany` size. In the port, spacer definitions MUST be automatic:

- **SpacerBoxCompany**: generated by the packing solver to fill the vertical gap above the company box columns (a simple rectangular no-lid tray).
- **SpacerBoxBack**: generated automatically by the packing solver as the remaining free area in the game box after the MoneyBox and CompanyBox columns are placed — no hand-written polygon path. The solver derives the polygonal outline from the game box interior minus the placed boxes.

This means `Project.export()` must emit spacer trays (both rectangular and polygon-path) from the leftover space, matching FR-014/FR-030 (hollow spacer trays) and FR-018 (polygon-path clipping).

### Migration Checklist

- [ ] Create `boxes/irish_gauge/irish_gauge.py` porting the 5 company boxes, money box, and spacers
- [ ] Derive all box sizes from `box_width`, `box_length`, `box_height`, `board_thickness`, `card_length`, `wall_thickness` — no hardcoded absolute sizes
- [ ] Implement company box contents: share-card stack, dividend-marker cylinder with indents, 6×4 train grid well, 3-line name label
- [ ] Implement money box: 3 card slots with "1"/"5"/"10" labels + "Irish Gauge" floor text
- [ ] Auto-generate SpacerBoxBack (polygon path) and SpacerBoxCompany (rectangular) from leftover space
- [ ] Verify all boxes + spacers pack within 214 × 302mm interior

## 1835 Example (Hex Tiles)

The `boxes/1835/` example ports `examples/1835.scad` to the new `spec_driven` Project API. This is the reference for hex-grid tile compartments with finger holes and raised pillars.

### Game Box

- **Retail box**: 216 × 298 × 50mm (W × L × H)
- **Defaults**: wall_thickness=2, lid_thickness=2, floor_thickness=2, board_thickness=15
- `main_height = box_height - board_thickness` = 35mm

### Hex Box

The `HexBox` is a box with an inset tabbed lid holding hexagonal train tiles:

- **Tile**: `tile_width = 40` (apothem-to-apothem), `tile_radius = tile_width / 2 / cos(30°)` ≈ 23.09
- **Hex box size**: `hex_box_width = tile_radius * 6 + 2*wt`, `hex_box_length = box_width - 1`, `hex_box_height = main_height / 4`
- **Hex grid**: `HexGridWithCutouts(rows=3, cols=5, height=hex_box_height, spacing=0, push_block_height=0, tile_width=40)` — a 3×5 array of 15 hexagonal cutouts per box
- **Four stacked HexBoxes**: placed at `z = hex_box_height * 0..3`, giving 60 hex tiles total

### Hex Cell Features (FR-040/041/042)

The `HexGridWithCutouts` cell is a hexagonal prism cutout. Optional features:
- **Push block (raised pillar)**: when `push_block_height > 0`, a smaller hexagon (`width=15`) is subtracted from the cell center, leaving a raised central post so the tile rests elevated for easy grasping.
- **Finger hole in the floor**: a circular cutout through the cell floor (configurable diameter) so a finger can push the tile up from underneath. When combined with a push block, the finger hole is offset to the cell edge.

### spec_driven Migration

- **Hex grid compartment**: `box.compartment(...)` gains a `hex_grid` mode with `rows`, `cols`, `tile_width`, `spacing`, `push_block_height`, and `finger_hole_diameter` parameters (FR-040–FR-042).
- **Hex cell geometry**: borrowed `HexGridWithCutouts` / `RegularPolygonGrid` from `components.py` for the hexagonal cutout layout.
- **Box types**: `HexBox` uses inset-tabbed lid (`BoxType.INSET` with tabbing) — maps to the existing inset box type with tabs.

### Migration Checklist

- [ ] Create `boxes/1835/1835.py` with hex box, money boxes, share boxes, middle box, first-player box, spacer
- [ ] Implement hex-grid compartment layout (`HexGridWithCutouts` port) in `spec_driven/compartments/`
- [ ] Implement push block (raised central pillar) in hex cells
- [ ] Implement hex-cell floor finger holes (offset from pillar when both present)
- [ ] Port the money box (8 denominations), share box (8 companies), middle box (tokens/trains), first-player box
- [ ] Verify all boxes + 4 stacked hex boxes pack within 216 × 298mm interior

## Complexity Tracking

> No violations.
