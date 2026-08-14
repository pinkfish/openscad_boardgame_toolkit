# Tasks: Board Game Box Library

**Input**: Design documents from `/specs/001-board-game-box-library/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test-first per constitution Principle IV — fast pure-Python tests included for all implementation phases.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Package initialization and foundational types

- [x] T001 Create `pyboxbuilder/` package directory with `__init__.py` and `py.typed` marker
- [x] T002 [P] Implement enums (`BoxType`, `LabelMode`, `PatternType`, `ScoopSide`) in `pyboxbuilder/enums.py`
- [x] T003 [P] Implement `Color` dataclass with named presets in `pyboxbuilder/color.py` *(superseded: removed — use `pybosl2.Color` directly, no Color class)*
- [x] T004 [P] Create `pyboxbuilder/__init__.py` package entry point re-exporting the public surface (no separate root shim — the package itself is the import)
- [x] T005 [P] Write test for enums validation in `tests/test_pyboxbuilder/test_enums.py`
- [x] T006 [P] Write test for Color in `tests/test_pyboxbuilder/test_color.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement `BoxBuilder` base frozen dataclass with common fields including `box_id` (unique instance identifier) and `final_size` (resolved by 3D packer) in `pyboxbuilder/builders/_base.py`
- [x] T008 [P] Implement `CompartmentBuilder` frozen dataclass in `pyboxbuilder/compartments/builder.py`
- [x] T009 [P] Implement `LidBuilder` and `PatternBuilder` frozen dataclasses in `pyboxbuilder/lid/builder.py`
- [x] T010 Implement `BoxProtocol` abstract base and `Interior` dataclass in `pyboxbuilder/box/base.py`
- [x] T011 Implement `Project` class skeleton (constructor, `box()` factory with `@overload` signatures, empty `export()`) in `pyboxbuilder/project.py`
- [x] T011a [P] Implement default clearance gap constant for 3D printing tolerances in `pyboxbuilder/compartments/builder.py`
- [x] T012 [P] Write test for BoxBuilder instantiation/validation including `box_id` uniqueness and `final_size` in `tests/test_pyboxbuilder/test_builders.py`
- [x] T013 [P] Write test for CompartmentBuilder in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T014 [P] Write test for LidBuilder/PatternBuilder in `tests/test_pyboxbuilder/test_lid_builder.py`
- [x] T015 [P] Write test for Project constructor and basic box registration in `tests/test_pyboxbuilder/test_project.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Basic Box with Interior Compartments (Priority: P1) 🎯 MVP

**Goal**: User can create a `Project`, add one box with compartments, and get a generated box body with compartments carved into the interior.

**Independent Test**: Create a box of 200x150x60mm with 3 compartments, verify compartments fit within the interior without overlaps.

### Tests for User Story 1

- [x] T016 [P] [US1] Write render test: single box with 3 compartments, verify interior dimensions in `tests/test_pyboxbuilder/render/test_box_render.py`
- [x] T017 [P] [US1] Write unit test: compartment layout fits interior bounds in `tests/test_pyboxbuilder/test_compartments.py`

### Implementation for User Story 1

- [x] T018 [US1] Implement `SlidingBoxBuilder` (extends BoxBuilder, adds `two_layer` etc., `size` defaults to `None` for auto-compute from compartments) in `pyboxbuilder/builders/sliding.py`
- [x] T019 [US1] Implement `SlidingBox` class (body + lid geometry) using pybosl2 in `pyboxbuilder/box/types/sliding.py`
- [x] T020 [US1] Implement box type registry (`BoxType` → class mapping) in `pyboxbuilder/box/registry.py`
- [x] T021 [US1] Implement interior computation and hollowing in `pyboxbuilder/box/interior.py`
- [x] T022 [US1] Implement compartment auto-layout with 90-degree rotation support (2D shelf-based packing) in `pyboxbuilder/compartments/layout.py`
- [x] T022a [US1] Implement `project.share_compartments()` shared compartment auto-packing API in `pyboxbuilder/project.py`
- [x] T023 [US1] Wire `Project.box()` → builder → BoxSpec → box construction in `pyboxbuilder/project.py`

**Checkpoint**: User Story 1 fully functional — one box type with compartments

---

## Phase 4: User Story 2 - Choose Among Different Box Lid Types (Priority: P1)

**Goal**: All 14 box types are implemented and selectable via `BoxType` enum. Each type produces correct mating lid geometry.

**Independent Test**: Generate a sliding box and a cap box; verify each lid fits its body and opens/closes correctly.

### Tests for User Story 2

- [x] T024 [P] [US2] Write render test: all 14 box types produce valid geometry in `tests/test_pyboxbuilder/render/test_box_render.py`
- [x] T025 [P] [US2] Write unit test: registry returns correct class per BoxType in `tests/test_pyboxbuilder/test_builders.py`

### Implementation for User Story 2

- [x] T026 [P] [US2] Implement remaining box type builders (cap, hinge, filament_hinge, magnetic) in `pyboxbuilder/builders/`
- [x] T027 [P] [US2] Implement remaining box type builders (inset, sliding_catch, slipover, slipover_path) in `pyboxbuilder/builders/`
- [x] T028 [P] [US2] Implement remaining box type builders (cap_path, no_lid, path, card_library) in `pyboxbuilder/builders/` *(path builder added 2026-08-13 — `pyboxbuilder/builders/path.py` had never been written)*
- [x] T029 [P] [US2] Implement box types: CapBox, HingeBox, FilamentHingeBox in `pyboxbuilder/box/types/`
- [x] T030 [P] [US2] Implement box types: MagneticBox, InsetBox, SlidingCatchBox in `pyboxbuilder/box/types/`
- [x] T031 [P] [US2] Implement box types: SlipoverBox, SlipoverPathBox, CapPathBox in `pyboxbuilder/box/types/`
- [x] T032 [P] [US2] Implement box types: NoLidBox, PathBox, CardLibraryBox in `pyboxbuilder/box/types/` *(PathBox added 2026-08-13 — polygon footprint, lidless, `LIDLESS_BOX_TYPES` in the registry)*
- [x] T033 [US2] Wire all box types into registry and verify `Project.box(BoxType.X, ...)` dispatches correctly in `pyboxbuilder/box/registry.py`

**Checkpoint**: All 14 box types functional — any type selectable via enum

---

## Phase 5: User Story 9 - Decorate Lids with Labels, Patterns, and Print-Optimized Color Layers (Priority: P2)

**Goal**: Lids get auto-sized labels (framed/frameless/diagonal), through-hole patterns (hex, grid, voronoi), three accent colors per lid. Min text height guard skips illegible labels.

**Independent Test**: Create a lid with "Animals" text, hex-grid through-holes, and framed diagonal label; verify correct color assignments in 3MF.

### Tests for User Story 9

- [x] T034 [P] [US9] Write unit test: label auto-sizing fills lid minus margin in `tests/test_pyboxbuilder/test_lid_label.py`
- [x] T035 [P] [US9] Write unit test: min text height guard skips labels < 4mm in `tests/test_pyboxbuilder/test_lid_label.py`
- [x] T036 [P] [US9] Write render test: lid with framed label + hex pattern + colors in `tests/test_pyboxbuilder/render/test_lid_render.py`

### Implementation for User Story 9

- [x] T037 [US9] Implement label generation: framed (rect frame + diagonal hatching + outer border) in `pyboxbuilder/lid/label.py`
- [x] T038 [US9] Implement label generation: frameless (text only) in `pyboxbuilder/lid/label.py`
- [x] T039 [US9] Implement corner-to-corner diagonal text orientation in `pyboxbuilder/lid/label.py`
- [x] T040 [US9] Implement min text height guard (default 4mm, settable) in `pyboxbuilder/lid/label.py`
- [x] T041 [US9] Implement pattern fill functions (hex grid, grid) as through-holes in `pyboxbuilder/lid/pattern.py`
- [x] T042 [US9] Implement pattern fill function (voronoi) — borrow tessellation from existing codebase in `pyboxbuilder/lid/pattern.py`
- [x] T043 [US9] Implement color layer assignment (3 independent accent colors, per-material 3MF mapping) in `pyboxbuilder/lid/color_layers.py`
- [x] T044 [US9] Wire `LidBuilder` → label + pattern + color layers → lid geometry in `pyboxbuilder/lid/builder.py`

**Checkpoint**: Lid decoration fully functional — labels, patterns, colors

---

## Phase 6: User Story 3 - Finger Cutouts for Easy Piece Removal (Priority: P2)

**Goal**: Compartments can have finger scoops on any side wall or floor notch for shallow compartments.

**Independent Test**: Compartment with front finger scoop admits a 14mm radius sphere at the scoop cutout.

### Tests for User Story 3

- [x] T045 [P] [US3] Write unit test: scoop dimensions match specification in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T046 [P] [US3] Write render test: compartment with scoop on all 4 sides in `tests/test_pyboxbuilder/render/test_box_render.py`

### Implementation for User Story 3

- [x] T047 [US3] Implement wall finger scoop (notch) geometry in `pyboxbuilder/compartments/finger_hole.py`
- [x] T048 [US3] Implement floor finger scoop geometry with shallow-depth fallback to wall notch in `pyboxbuilder/compartments/finger_hole.py`
- [x] T049 [US3] Wire `CompartmentBuilder.finger_scoop` and `ScoopSide` to compartment construction in `pyboxbuilder/compartments/builder.py`

**Checkpoint**: Finger scoops functional on all 4 sides, auto-fallback for shallow compartments

---

## Phase 7: User Story 4 - Automatic Compartment Layout (Priority: P2)

**Goal**: Compartments auto-arrange in rows without manual positioning. Grouped compartments stay together.

**Independent Test**: 10 compartments of varying sizes automatically arranged within a box interior without overlaps.

### Tests for User Story 4

- [x] T050 [P] [US4] Write unit test: auto-layout places 10 compartments without overlap in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T051 [P] [US4] Write unit test: grouped compartments stay adjacent in `tests/test_pyboxbuilder/test_compartments.py`

### Implementation for User Story 4

- [x] T052 [US4] Enhance shelf-based 2D bin packing with row-first placement in `pyboxbuilder/compartments/layout.py`
- [x] T052a [US4] Implement compartment row-width distribution (size compartments to fill row width) in `pyboxbuilder/compartments/sizing.py` *(written 2026-08-13 — the module had never been created)*
- [x] T053 [US4] Implement compartment grouping (grouped items packed together) in `pyboxbuilder/compartments/layout.py`
- [x] T054 [US4] Implement overflow detection with descriptive error messages in `pyboxbuilder/compartments/layout.py`
- [x] T054a [US4] Implement compartment clipping to non-rectangular polygon interior regions (FR-018) in `pyboxbuilder/compartments/layout.py`
- [x] T054b [US4] Support bin-packing for non-rectangular compartments (hexagons, circular slots, custom shapes like Emberleaf species) using their rectangular bounding boxes in `pyboxbuilder/compartments/layout.py`

**Checkpoint**: Compartments auto-laid-out in rows, grouped compartments stay adjacent

---

## Phase 8: User Story 7 - Auto-Size Sub-Boxes and Fill Gaps with Spacers (Priority: P2)

**Goal**: Sub-boxes with minimum dimensions auto-expand to fill rows. Row lengths align. Gaps > 10mm produce hollow spacer trays. Gaps < 10mm absorbed by adjacent boxes.

**Independent Test**: 4 sub-boxes in a 300x200mm game box produce rows with common lengths and spacers for gaps > 10mm.

### Tests for User Story 7

- [x] T055 [P] [US7] Write unit test: auto-sizing expands boxes to fill rows in `tests/test_pyboxbuilder/test_packing.py`
- [x] T056 [P] [US7] Write unit test: row lengths match longest box in row in `tests/test_pyboxbuilder/test_packing.py`
- [x] T057 [P] [US7] Write unit test: gaps > 10mm produce spacers, gaps < 10mm absorbed, and `final_size` correctly propagated to builders in `tests/test_pyboxbuilder/test_packing.py`
- [x] T058 [P] [US7] Write render test: 4-box game with spacers in `tests/test_pyboxbuilder/render/test_box_render.py`

### Implementation for User Story 7

- [x] T059 [US7] Implement 3D box packing into game box interior using a 3D packing solver with dynamic dimension expansion in `pyboxbuilder/packing/layout.py`
- [x] T060 [US7] Implement auto-sizing expansion (fill-to-fit rows, common length per row) and propagate resolved sizes back to builders via `final_size` attribute in `pyboxbuilder/packing/layout.py`
- [x] T061 [US7] Implement spacer tray generation from gap dimensions (NoLidBox hollow trays) in `pyboxbuilder/packing/spacer.py`
- [x] T062 [US7] Implement gap threshold logic (absorb < 10mm, spacer if ≥ 15mm, absorb 10-15mm) in `pyboxbuilder/packing/spacer.py`
- [x] T063 [US7] Wire `Project.export()` → packing solver → auto-sizing with `final_size` propagation → spacer generation in `pyboxbuilder/project.py`

**Checkpoint**: Multi-box games with auto-sizing and spacers fully functional

---

## Phase 9: User Story 8 - Export 3MF Files with Content-Based Caching (Priority: P2)

**Goal**: `Project.export()` produces organized 3MF files in `{out_dir}/{game}/mmu/` and `{out_dir}/{game}/single/`. Hausdorff comparison skips unchanged files. Two-level cache (memory + disk JSON with SHA-256 hash) speeds repeated renders.

**Independent Test**: Export a 2-box project twice; first writes files, second skips all. Modify one box; only that box's files are rewritten.

### Tests for User Story 8

- [x] T064 [P] [US8] Write unit test: ExportResult file counts match expectations in `tests/test_pyboxbuilder/test_export.py`
- [x] T065 [P] [US8] Write unit test: cache hit/miss based on SHA-256 hash using `.layout_cache.json` in `tests/test_pyboxbuilder/test_packing.py`
- [x] T066 [P] [US8] Write render test: second export writes 0 files (Hausdorff skip) in `tests/test_pyboxbuilder/render/test_export_render.py`
- [x] T067 [P] [US8] Write render test: partial change exports only modified files in `tests/test_pyboxbuilder/render/test_export_render.py`

### Implementation for User Story 8

- [x] T068 [P] [US8] Implement `ExportResult` frozen dataclass in `pyboxbuilder/export/result.py`
- [x] T068a [US8] Implement MMU color-copy logic (positive inserts in different material/color from body) in `pyboxbuilder/export/exporter.py` *(written 2026-08-13 — `BoxExporter._compose` keeps inserts as distinct objects in mmu, fuses them in single)*
- [x] T068b [US8] Implement bounding-box reporting for each exported piece (FR-027) in `pyboxbuilder/export/exporter.py` *(written 2026-08-13 — `PieceBounds`, surfaced as `Project.piece_bounds`)*
- [x] T069 [P] [US8] Implement two-level layout cache (in-memory dict + disk `pyboxbuilder/.layout_cache.json`, SHA-256 key, version invalidation) to store 3D box packing layouts and bypass solver on subsequent runs in `pyboxbuilder/packing/cache.py`
- [x] T070 [US8] Implement `BoxExporter` with per-box/per-spacer 3MF file writing in `pyboxbuilder/export/exporter.py` *(written 2026-08-13 — `Project.export` used to `touch()` empty files; it now exports real 3MF geometry through the `openscad` module)*
- [x] T071 [US8] Implement Hausdorff conditional write (pymeshlab compare, skip if distance < 0.001mm) in `pyboxbuilder/export/hausdorff.py` *(written 2026-08-13 — falls back to a `<mesh>`-only digest when pymeshlab is absent, because 3MF stamps a timestamp and fresh UUIDs on every write and so never matches byte for byte)*
- [x] T072 [US8] Implement organized output directory structure (`mmu/` + `single/`, `_body.3mf` / `_lid.3mf` naming) in `pyboxbuilder/export/exporter.py` *(moved out of `project.py` into `BoxExporter` 2026-08-13)*
- [x] T073 [US8] Wire full `Project.export()` pipeline: pack with dynamic dimension expansion → auto-size with `final_size` propagation → spacers → build → export in `pyboxbuilder/project.py`

**Checkpoint**: Full export pipeline functional — cached, Hausdorff-gated, organized output

---

## Phase 10: User Story 5 + User Story 6 - Nested Boxes & Manual Positioning (Priority: P3)

**Goal**: Nested sub-boxes inside a game box with validation. Manual compartment positioning overrides auto-layout.

**Independent Test**: Outer box 300x300x80mm with 4 sub-boxes fits without overlap. Manual (x,y) positions applied correctly.

### Tests for User Story 5/6

- [x] T074 [P] [US5] Write unit test: 4 sub-boxes fit in 300x300x80mm outer box in `tests/test_pyboxbuilder/test_packing.py`
- [x] T075 [P] [US6] Write unit test: manual positions override auto-layout in `tests/test_pyboxbuilder/test_compartments.py`

### Implementation for User Story 5/6

- [x] T076 [US5] Implement validation: sub-boxes fit within outer interior (footprint + height) with descriptive errors in `pyboxbuilder/packing/layout.py`
- [x] T077 [US6] Implement manual compartment positioning (explicit x, y coordinates) in `pyboxbuilder/compartments/layout.py`
- [x] T078 [US6] Implement overlap detection and error reporting for manually positioned compartments in `pyboxbuilder/compartments/layout.py`

**Checkpoint**: Nested box validation and manual positioning functional

---

## Phase 10b: User Story 10 - Generate Packing Layout PDF Guide (Priority: P3)

**Goal**: `project.export()` produces a `layout.pdf` in the output directory containing multiple pages representing distinct stacking layers (e.g. Base Layer, Middle Layer, Top Layer). On each page, the boxes belonging to that layer are drawn in full color, while already-placed boxes are drawn in light gray. Boxes are labeled, colored, and numbered in packing order. PDF is cached: only regenerated when layout or library version changes.

**Independent Test**: Export a 4-box game, verify `layout.pdf` exists showing 4 labeled boxes at correct positions across one or more pages.

### Tests for User Story 10

- [x] T078a [P] [US10] Write unit test: PDF file exists in output directory after export in `tests/test_pyboxbuilder/test_export.py`
- [x] T078b [P] [US10] Write unit test: PDF skipped on re-export when layout unchanged in `tests/test_pyboxbuilder/test_export.py`

### Implementation for User Story 10

- [x] T078c [US10] Implement 3D oblique projection packing layout renderer (outlines, labels, dimensions, spacer markers) in `pyboxbuilder/export/layout_pdf.py`
- [x] T078d [US10] Implement packing order numbering, colored 3D shaded boxes, vertical exploded displacement, and dashed alignment lines in `pyboxbuilder/export/layout_pdf.py`
- [x] T078e [US10] Implement PDF caching with SHA-256 layout hash (skip regeneration if unchanged) in `pyboxbuilder/export/layout_pdf.py`
- [x] T078f [US10] Wire PDF generation into `Project.export()` pipeline and add `layout.pdf` to `ExportResult` in `pyboxbuilder/project.py`

**Checkpoint**: Packing layout PDF generated and cached alongside 3MF exports

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Reference example, documentation, final integration

- [x] T079 [P] Create `boxes/` directory with `_template/` for new game projects
- [x] T080 [P] Create Earth Animal Kingdom reference example using full pyboxbuilder API in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T081 [P] Create Earth Animal Kingdom README in `boxes/earth_animal_kingdom/README.md`
- [x] T082 Run `npx pyright pyboxbuilder/` — fix any type errors
- [x] T083 Run `python3 tests/run_fast.py test_pyboxbuilder/` — all fast tests pass
- [x] T084 Run full render suite: `python3 -m unittest discover -s tests/test_pyboxbuilder/render` — all render tests pass
- [x] T085 Validate quickstart.md scenarios against implemented API
- [x] T086 [P] Implement ratio-based compartment sizing (`width_ratio`, `length_ratio`, `resolve_size`) in `pyboxbuilder/compartments/builder.py`
- [x] T087 [P] Validate compartment ratio sums ≤ 1.0 per row at export time in `pyboxbuilder/project.py`
- [x] T088 [P] Enforce 0.1mm precision floor on all dimensional output (no rounding to whole mm) in `pyboxbuilder/compartments/builder.py`
- [x] T089 Wire 3D bin-packing solver from `pyboxbuilder/packing/layout.py` to distribute 37 animal entries across two AnimalBox containers in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T090 [P] Generate labeled compartment floors — 0.2mm extruded animal name text per compartment in `pyboxbuilder/compartments/labels.py`
- [x] T091 Verify all 7 Earth Animal Kingdom boxes pack within 288×158mm game box interior using auto-sizing solver in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T092 [P] Write test: ratio-based compartments resolve correctly against interior dimensions in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T093 [P] Write test: ratio overflow validation rejects sum > 1.0 in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T094 [P] Write test: 0.1mm precision maintained in compartment resolution in `tests/test_pyboxbuilder/test_compartments.py`
- [x] T095 [P] Add `mmu_label` and `single_label` optional LidBuilder fields for per-export-mode label overrides in `pyboxbuilder/lid/builder.py`
- [x] T096 [P] Implement per-mode label resolution — `mmu_label`/`single_label` override parent when set, fall back otherwise — in `pyboxbuilder/lid/builder.py`
- [x] T097 Implement compartment label mode switching: engraved 0.2mm cutout for single-color, raised 0.2mm second-color text for MMU via `mode` parameter in `pyboxbuilder/compartments/labels.py`
- [x] T098 Wire per-mode label resolution into `Project.export()` — resolve MMU label for `mmu/` pass, single label for `single/` pass — in `pyboxbuilder/project.py`
- [x] T099 [P] Write test: LidBuilder per-mode override fallback logic in `tests/test_pyboxbuilder/test_lid_builder.py`
- [x] T100 [P] Write test: compartment label mode switching (cutout for single, raised for MMU) in `tests/test_pyboxbuilder/test_lid_label.py`
- [x] T101 [P] Write test: PDF is valid and boxes rendered at correct packed positions (SC-019) in `tests/test_pyboxbuilder/test_export.py`
- [x] T102 [P] Implement standalone box export path — `project.box(...)` exported directly with no game box, no packing, no PDF — in `pyboxbuilder/project.py`
- [x] T103 [P] Implement stackable inside/outside rim generation for no-lid boxes in `pyboxbuilder/box/types/no_lid.py`
- [x] T104 [P] Implement round and rectangular magnet slots on opposing sides in `pyboxbuilder/box/types/no_lid.py`
- [x] T105 Create `boxes/irish_gauge/irish_gauge.py` — 5 company boxes, money box, auto-generated spacers, box sizes derived from game box dimensions
- [x] T106 [P] Auto-generate spacer boxes (rectangular + polygon-path) from leftover space in `pyboxbuilder/packing/spacer.py`
- [x] T107 Write test: Irish Gauge box sizes derived correctly + spacers auto-generated in `tests/test_pyboxbuilder/test_irish_gauge.py`
- [x] T108 [P] Implement `no_rotate` flag propagation through `pack_boxes` → `pack_3d_boxes` orientation selection (FR-013c) in `pyboxbuilder/packing/layout.py` + `compartments.py`
- [x] T109 [P] Implement box-rotation → compartment re-layout: when a placement is `rotated`, re-run `layout_compartments` against the swapped interior dimensions (FR-013b) in `pyboxbuilder/project.py`
- [x] T110 Create `boxes/stackable_hexes/stackable_hexes.py` — 8 hex box variants (1–4 divisions × round/rect magnets) with stackable rims in `boxes/stackable_hexes/`
- [x] T111 [P] Write test: no_rotate boxes are never rotated + rotated boxes re-lay-out compartments (FR-013b/FR-013c) in `tests/test_pyboxbuilder/test_packing.py`
- [x] T112 [P] Expand `PatternType` enum to the full catalog (42 members) — dense/lattice shapes, pentagon tilings R1–R15, and all tessellations — in `pyboxbuilder/enums.py`
- [x] T113 [P] Implement dense/lattice shape fills (DENSE_HEX, DENSE_TRIANGLE, CIRCLE, HEX, OCTOGON, TRIANGLE, SQUARE, SUPERSHAPE, HILBERT, CLOUD) as through-hole functions in `pyboxbuilder/lid/pattern.py`
- [x] T114 [P] Implement pentagon tiling fills (PENTAGON_R1–R15) by wrapping `pentagon_tilings.py` in `pyboxbuilder/lid/pattern.py`
- [x] T115 [P] Implement tessellation fills (LIZARD, VORONOI, LEAF, LEAF_VEINS, DROP, DELTOID_TRIHEXAGONAL, DELTOID_TRIHEXAGONAL_KITE, HALF_REGULAR_HEXAGON, RHOMBI_TRI_HEXAGONAL, PENROSE_TILING_5, PENROSE_TILING_7, PEGASUS, GOOSE, CHICKEN, SHEEP, BIRD, HEX_TESSELATION, KITE_TESSELATION, QUAD_TESSELATION) by wrapping `tesselations/` modules in `pyboxbuilder/lid/pattern.py`
- [x] T116 [P] Update `build_pattern` dispatch to cover every `PatternType` member (no fallback-to-grid) in `pyboxbuilder/lid/pattern.py`
- [x] T117 [P] Write test: every `PatternType` member resolves to a fill function without fallback in `tests/test_pyboxbuilder/test_lid_pattern.py`
- [x] T118 [P] Implement hex-grid compartment layout — `HexGridWithCutouts` port (rows × cols hexagonal cutouts from `tile_width`, deriving circumradius as `tile_width/2/cos(30°)`) in `pyboxbuilder/compartments/hex_grid.py`
- [x] T119 [P] Implement hex-cell push block — raised central hexagonal pillar via `push_block_height` (FR-041) in `pyboxbuilder/compartments/hex_grid.py`
- [x] T120 [P] Implement hex-cell floor finger hole — circular cutout through the cell floor, offset from the pillar when both are enabled (FR-042) in `pyboxbuilder/compartments/hex_grid.py`
- [x] T121 Create `boxes/1835/1835.py` — hex boxes (3×5 hex grid ×4 stacked), money boxes (8 denominations), share boxes (8 companies), middle box (tokens/trains), first-player box, spacer in `boxes/1835/`
- [x] T122 [P] Write test: hex grid derives circumradius + rows/cols layout correctly in `tests/test_pyboxbuilder/test_hex_grid.py`
- [x] T123 [P] Write test: push block + finger hole are mutually offset (never intersect) in `tests/test_pyboxbuilder/test_hex_grid.py`
- [x] T124 [P] Add `board_thickness` field to `Project` — reserved board space at the box bottom, not a spacer gap — in `pyboxbuilder/project.py`
- [x] T125 [P] Exclude the board area from spacer generation by using `game_box_height - board_thickness` as the effective container height in `pyboxbuilder/project.py`
- [x] T126 [P] Implement `_delete_stale_spacers()` — delete orphaned `spacer_*` 3MF files no longer generated — in `pyboxbuilder/project.py` *(now delegates to `BoxExporter.delete_stale`)*
- [x] T127 [P] Write test: `board_thickness` excludes the board area from spacer generation (no spacer for reserved board space) in `tests/test_pyboxbuilder/test_packing.py`
- [x] T128 [P] Write test: `_delete_stale_spacers()` removes orphaned spacer files when re-export produces fewer spacers in `tests/test_pyboxbuilder/test_export.py`
- [x] T129 [P] Write test: 1835 example produces exactly one spacer (matching the original `SpacerBox`) in `tests/test_pyboxbuilder/test_irish_gauge.py`
- [x] T130 [P] Create pyboxbuilder render test helper — shell out to the full PythonSCAD binary and report geometry (`render_pyboxbuilder.py` reusing `tests/render_app.py`'s `render_python`/`render_script`) in `tests/test_pyboxbuilder/render/`
- [x] T131 [P] Create golden-image render tests for box bodies/lids (sliding, cap, hinge, no-lid, stackable, magnetic) using `compare_images` against `tests/test_pyboxbuilder/golden/` in `tests/test_pyboxbuilder/render/test_boxes_golden.py`
- [x] T132 [P] Create golden-image render tests for lid patterns (hex grid, voronoi, a pentagon tiling, a tessellation) in `tests/test_pyboxbuilder/render/test_patterns_golden.py`
- [x] T133 [P] Create golden-image render tests for hex-grid compartments (push block + finger hole) in `tests/test_pyboxbuilder/render/test_hex_grid_golden.py`
- [x] T134 [P] Create golden-image generator script that renders every golden case to `tests/test_pyboxbuilder/golden/` in `tests/test_pyboxbuilder/generate_golden.py`
- [x] T135 [P] Create GitHub Actions test workflow (fast pytest + pyright) in `.github/workflows/test.yml`
- [x] T136 [P] Create GitHub Actions render workflow (PythonSCAD golden-image verification) in `.github/workflows/render.yml`
- [x] T137 [P] Create GitHub Actions docs workflow (dev docs on checkin, release docs on tag) in `.github/workflows/docs.yml`

---

## Phase 12: Element Packing & Emberleaf (FR-004a / FR-004b)

**Purpose**: Individual per-piece slots inside a compartment, and the Emberleaf reference example that exercises them.

**Goal**: A compartment can hold many individually-placed silhouettes — a slot per worker meeple, per hero standee, per hex tile — each at its own offset, rotation and depth, with the pack's bounding box packing like an ordinary rectangle. `boxes/emberleaf/emberleaf.py` reproduces `examples/emberleaf.scad`.

**Independent Test**: Load the Emberleaf example and verify five separate slots exist per worker species, each with its own SVG silhouette, none overlapping the hero or breaking a wall.

### Element packing

- [x] T138 [P] Implement `CompartmentElement` with per-element shape, offset, rotation, depth and z-offset in `pyboxbuilder/compartments/element.py`
- [x] T139 [P] Implement `ElementShape` enum (SVG, RECT, ROUNDED_RECT, CIRCLE, HEXAGON, SPHERE_SCOOP) in `pyboxbuilder/enums.py`
- [x] T140 [P] Implement shape-aware footprints — exact rotated hexagon extent, rotation-invariant discs — in `pyboxbuilder/compartments/element.py`
- [x] T141 [P] Implement element-pack helpers (`grid_pack`, `normalize_elements`, `elements_footprint`, `elements_overlap`) in `pyboxbuilder/compartments/element.py`
- [x] T142 [US4] Derive a compartment's size from its element pack's bounding box (FR-004b) in `pyboxbuilder/compartments/builder.py`
- [x] T143 [P] Implement SVG silhouette extrusion with a parse cache (`svg_solid`) in `pyboxbuilder/compartments/element.py`
- [x] T144 [P] Write test: element footprints, packs, overlap detection and pack-derived sizing in `tests/test_pyboxbuilder/test_elements.py`

### Carving compartments into bodies

- [x] T145 [US1] Implement `build_contents` — turn compartment placements into the solid subtracted from a body — in `pyboxbuilder/compartments/carve.py`
- [x] T146 [US1] Hollow a box wholesale only when it has no compartments; otherwise the compartments are the cavities. `pyboxbuilder/box/shell.py` + `Project.export`
- [x] T147 [US1] Clip compartment wells to the interior footprint so none breaks through a side wall (FR-018), while finger scoops stay unclipped because piercing a wall is their job, in `pyboxbuilder/compartments/carve.py`
- [x] T148 [US3] Rewrite the finger scoops for correct anchoring, with an automatic wall-notch → floor-bowl fallback for shallow compartments, in `pyboxbuilder/compartments/finger_hole.py`

### Geometry anchoring correction

- [x] T149 Extract the shared `build_shell` / `block` / `corner` placement helpers in `pyboxbuilder/box/shell.py`, replacing the copy of `outer - inner` in all 13 box types
- [x] T150 Correct every box type for pybosl2's **centre**-anchored primitives — bodies were being cut off-centre, leaving boxes with two walls instead of four — in `pyboxbuilder/box/types/`
- [x] T151 Rebuild the CapBox and SlipoverBox lids as real skirted caps rather than flat plates in `pyboxbuilder/box/types/`
- [x] T152 Regenerate the golden images, which had captured the off-centre bodies, and align `generate_golden.py`'s dimensions with the test's in `tests/test_pyboxbuilder/`

### Emberleaf reference example

- [x] T153 Rewrite `boxes/emberleaf/emberleaf.py` to derive every dimension with the same formula as `examples/emberleaf.scad`
- [x] T154 Place all 21 boxes at the positions `BoxLayout()` uses, with no overlaps and nothing overhanging the game box
- [x] T155 Give each of the five owl / rabbit / frog / rat workers its own silhouette slot at the original's pitch, plus the per-colour hero, in `boxes/emberleaf/emberleaf.py`
- [x] T156 Reproduce the marker pockets, victory-token stack, hex tiles and pull-out depressions at their individual depths in `boxes/emberleaf/emberleaf.py`
- [x] T157 Reproduce the CommonBox hex grid, trophy well and trophy marker in `boxes/emberleaf/emberleaf.py`
- [x] T158 [P] Write test: Emberleaf dimensions, layout, per-worker slots and export match the original in `tests/test_pyboxbuilder/test_emberleaf.py`
- [x] T159 [P] Write test: BoxExporter, mesh-equivalence gating, row sizing and PathBox in `tests/test_pyboxbuilder/test_exporter.py`
- [x] T160 Fix `should_regenerate_layout` writing its hash only on the second run, which rebuilt an already-current PDF, in `pyboxbuilder/export/layout_pdf.py`

**Checkpoint**: Element packs functional; Emberleaf exports real 3MF files plus a layout PDF, and a re-export rewrites nothing.

---

## Phase 13: Fewest-Possible Spacers (FR-014a/b/c)

**Purpose**: The leftover space should produce as few trays as it can, and they should be liftable.

**Goal**: Spacer count depends only on the shape of the empty space, not on how many boxes the layout contains. Emberleaf gets its three spacers from the packer instead of declaring them.

**Independent Test**: Export Emberleaf and verify exactly three spacers, at the corners of the original's `SpacerPlayer`, `SpacerSide` and `SpacerFront`.

- [x] T164 Move the 3D sweep out of `Project.export` into `pyboxbuilder/packing/spacer.py` as `sweep_free_space`
- [x] T165 Take the largest available box at each sweep step instead of scanning in index order, so a sliver cannot claim cells out of a big void and fragment it (FR-014a)
- [x] T166 Implement `merge_voids` — fuse any two voids whose union is a box, to a fixed point, in canonical order (FR-014b)
- [x] T167 Implement `apply_clearance` — inset a tray's footprint by the project's `clearance_slack` so it can be lifted out (FR-014c)
- [x] T168 Add `Project.min_spacer_height` and wire `Project.export` to `generate_spacer_placements` (sweep → merge → shrink → filter)
- [x] T169 Turn on `generate_spacers` for Emberleaf and delete its three hand-declared spacers in `boxes/emberleaf/emberleaf.py`
- [x] T170 [P] Write test: merge fuses on every axis, is idempotent, is order-independent, and leaves an L-shape at two (SC-010b) in `tests/test_pyboxbuilder/test_spacer_merge.py`
- [x] T171 [P] Write test: swept voids never overlap each other or a placed box, and a sliver does not fragment its neighbour (FR-014a) in `tests/test_pyboxbuilder/test_spacer_merge.py`
- [x] T172 [P] Write test: Emberleaf produces exactly three spacers at the original's corners (SC-010a) in `tests/test_pyboxbuilder/test_emberleaf.py`

**Checkpoint**: Emberleaf's spacers are derived, not declared — three trays, down from the four the un-merged sweep produced. 1835 still produces exactly one.

### Rectilinear merge — L/T/U leftovers as one polygon tray (FR-014d/e)

- [x] T174 Add `pyboxbuilder/paths.py` — rectilinear polygon helpers (`polygon_area`, `is_rectilinear`, `inset_rectilinear`, `bounds`) shared by the spacer pass and `PathBox`
- [x] T175 Implement `union_outline` — trace the boundary of a union of footprints by edge cancellation, collapsing collinear runs, in `pyboxbuilder/packing/spacer.py`
- [x] T176 Implement `merge_rectilinear` — group coplanar voids into connected clusters and emit one polygon-footprint `Void` per cluster (FR-014d)
- [x] T177 Refuse to fuse voids at different heights, which would replace two flat trays with one overhanging part (FR-014e)
- [x] T178 Add `Placement.path` and build polygon spacers through `BoxType.PATH` in `Project.export`
- [x] T179 Replace `PathBox._inset_path`'s centroid scale with the exact rectilinear inset, which a centroid scale gets wrong on any reflex corner
- [x] T180 [P] Write test: L/T/U/plus outlines trace correctly, polygon area is preserved, stacked voids stay apart, and an inset L stays rectilinear on all six sides in `tests/test_pyboxbuilder/test_spacer_merge.py`

**Checkpoint**: A corner box in an otherwise empty layer yields one six-point L tray instead of two rectangles, and it builds as a real hollow `PathBox`.

### Packing correctness — found while evaluating auto-packing for Emberleaf

- [x] T181 Fix `expandable=False` not disabling expansion. `Project.export` OR'd the master switch with `expandable_width`/`expandable_length`, which default to `True`, so every box was expandable and boxes declared fixed were silently stretched — Earth Animal Kingdom's `CanopyBox` was being grown 46 → 47mm and `SproutBox` 20.4 → 21.4mm against their declared sizes.
- [x] T182 Wire the per-axis expansion flags through to the solver: `expandable` alone gives the sub-3mm height absorb (FR-012), `expandable_width` adds the fill-to-fit width growth, in `pyboxbuilder/packing/layout.py`.
- [x] T183 Stop the packer from using the board's space. `Project.export` passed the full `game_box_size[2]` as the container height while the spacer pass used `height - board_thickness`, so auto-placed boxes could climb into the region reserved for the game board (FR-012, board-on-top).
- [x] T184 Raise `PackingError` instead of returning an empty packing. A solver failure was swallowed, so `export()` reported success having written no boxes at all. The message now names boxes taller than the container, or reports the fill ratio.
- [x] T185 [P] Write test: expansion respects the master switch, packing failures raise and explain themselves, in `tests/test_pyboxbuilder/test_packing.py` and `test_project_coverage.py`

**Checkpoint**: Declared-fixed boxes keep their size, nothing intrudes on the board space, and a layout that cannot be packed says so.

### Auto-packing Emberleaf — evaluated, not adopted

Emberleaf's 18 boxes fill **77%** of the usable volume (3296 cm³ of 4264 cm³ in 285 × 285 × 52.5mm). The original `.scad` layout achieves this because the box sizes were designed to tile exactly in three columns — 98 + 98 + 90 = 286 across, 142.5 × 2 = 285 deep, 13.125 × 4 = 52.5 tall.

The extreme-point First-Fit-Decreasing solver cannot find that arrangement. Measured: five sort strategies (footprint area, height, volume, height-then-volume, max dimension) all fail; twelve variants crossing those with three extreme-point orderings, best-fit selection and corner extreme-point generation all fail; 266,000 random permutations of the plain solver and 60,000 of the strongest variant produce no successful packing. The failure is in the placement rule, not the ordering — greedy extreme-point placement fragments the space rather than aligning columns.

Emberleaf therefore keeps explicit positions. Note this is not a statement that a better solver could not do it — a layout demonstrably exists.

**Update (T187): a better solver does do it.** The guillotine packer finds a valid Emberleaf arrangement in 3,237 nodes, about 30ms. Emberleaf still keeps its declarative `arrange()` — that expresses intent, which a solver cannot — but auto-packing is no longer the reason.

- [x] T186 Declarative column/stack layout — see Phase 15.
- [x] T187 Stronger 3D packing for high-fill layouts — see Phase 17.

---

## Phase 14: Earth Animal Kingdom fidelity, and lid decoration

### Earth Animal Kingdom — matched to the original

The port had drifted from `examples/earth_animal_kingdom.scad` on nearly every dimension.

- [x] T188 Derive every dimension with the original's formula. Corrected: card box height 25.6 → **23.6** (36 cards at 0.6mm + 2), sprout box (76, 156, 20.4) → **(76, 158, 22.4)**, animal boxes (174, 156, 12.1) → **(174, 158, 12.5)**.
- [x] T189 Correct the animal box type: `MakeBoxWithSlipoverLid` is `BoxType.SLIPOVER`, not `FILAMENT_HINGE`, with its own 1.5mm wall and a 4mm foot.
- [x] T190 Add `foot` and `slip` to `SlipoverBoxBuilder` and build a sleeve that stops at the foot in `pyboxbuilder/box/types/slipover.py`.
- [x] T191 Replace the invented `Boards` box with the original's `SpacerBox` (174 × 158 × 21).
- [x] T192 Position all six boxes to match `BoxLayout()`, which the port had left to the packer.
- [x] T193 Reproduce the precomputed animal partition from `lib/animal_kingdom_items_layout.scad` verbatim — 26 slots in AnimalBox1, 30 in AnimalBox2, 56 in total across 37 species — replacing the `share_compartments` solver, which produced a different split.
- [x] T194 Add the access pan each animal box carries over its slots (`RoundedBoxAllSides` at half the token thickness).
- [x] T195 [P] Write test: dimensions, box types, layout positions, and that every slot fits its interior with no two overlapping, in `tests/test_pyboxbuilder/test_earth_animal_kingdom.py`

### Lid decoration (T161)

- [x] T196 Implement `pyboxbuilder/lid/decorate.py` — apply a `LidBuilder`'s pattern and label to any box type's lid, deriving the decoratable face from the lid's own bounding box so no type has to declare one.
- [x] T197 Wire decoration into `Project.export` per colour mode: mmu keeps the label as separate coloured inserts, single engraves it into the lid.
- [x] T198 Fix `build_label` never extruding its text (`pybosl2.text` returns a 2-D shape) and mis-anchoring its frame and hatching.
- [x] T199 Size label text by measurement instead of by character count. The old estimate put **102mm of text on a 100mm lid**; text is now set at a nominal size, measured, and scaled to the label area.
- [x] T200 Shrink a framed label's backing plate to hug its text, so a lid can carry both a frame and a through-hole pattern — a plate the size of the label area covered the pattern entirely.
- [x] T201 Fix the pattern leaving a skin: it was placed by assumption rather than by its bounding box, so the holes stopped 0.7mm short of the top face and nothing showed. Also trimmed to the label area so it cannot eat the border.
- [x] T202 Degrade a framed label to engraved text in single-colour mode. A frame is a colour feature, and keeping it lifted the text 0.4mm clear of the face so the engraving cut nothing at all.
- [x] T203 [P] Write test: label sizing stays inside the margin, mmu yields separate inserts, single engraves, patterns cut through, and a decorated lid differs between the two modes, in `tests/test_pyboxbuilder/test_lid_decorate.py`

**Checkpoint**: Lids carry their labels and patterns. A plain sliding lid goes from 8 vertices to 1631 with a framed label and hex pattern; the single-colour variant is engraved instead of raised.

### Known gaps
- [x] T162 `InsetBox`, `SlidingCatchBox`, `CapPathBox`, `SlipoverPathBox`, `CardLibraryBox` and `FilamentHingeBox` still return a plain plate from `build_lid`; only sliding, cap and slipover produce their real mating geometry.
- [x] T163 `HingeBox` knuckles are a placeholder — no matching lid knuckles and no pin channel, so the hinge does not yet articulate.
- [x] T173 *(resolved, and the original diagnosis was wrong.)* Irish Gauge yields four spacers where the plan calls for two, and I recorded the extra pair as a footprint L that polygon-path spacers would close. It is not: `spacer_3` and `spacer_4` share a Y span and form an L in the **x-z** plane — a vertical step above `CompanyBox2`. Fusing it would give one part whose upper arm floats, replacing two trays that each sit flat with a single overhanging one. Rectilinear merging now handles genuine footprint L/T/U shapes (T174–T180), and vertical steps stay separate by design (FR-014e), so Irish Gauge stays at four spacers and that is the correct answer.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational — can parallel with US1
- **US9 (Phase 5)**: Depends on US2 (needs lid geometry from box types)
- **US3 (Phase 6)**: Depends on US1 (needs compartment construction)
- **US4 (Phase 7)**: Depends on US1 (needs layout engine)
- **US7 (Phase 8)**: Depends on US4 (needs row layout), US1 (needs box construction)
- **US8 (Phase 9)**: Depends on US7 (needs full packing + spacers), US9 (needs color layers)
- **US5/US6 (Phase 10)**: Depends on US7 (needs nested packing framework)
- **US10 (Phase 10b)**: Depends on US8 (needs full export pipeline + packing layout)
- **Polish (Phase 11)**: Depends on all implemented stories

### User Story Dependencies

```
Phase 2 (Foundational)
  ├── Phase 3 (US1) ──── Phase 6 (US3)
  ├── Phase 4 (US2) ──── Phase 5 (US9) ──────────────────┐
  ├── Phase 3 (US1) ──── Phase 7 (US4) ── Phase 8 (US7) ─┤
  │                                                       ├── Phase 9 (US8) ── Phase 10b (US10)
  │                             Phase 10 (US5/US6) ────────┘
  └── Phase 11 (Polish)
```

### Within Each User Story

- Tests written first (fail before implementation)
- Models/builders before implementations
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004 all [P] in Setup
- T008, T009 [P] in Foundational
- T012–T015 all [P] tests in Foundational
- T026–T028 all [P] (builder groups) in US2
- T029–T032 all [P] (box type groups) in US2
- T034–T036 all [P] tests in US9
- T068, T069 [P] in US8
- US1 and US2 can proceed in parallel after Foundational

---

## Parallel Example: User Story 2

```bash
# Launch all builder tasks together:
Task: "Implement cap, hinge, filament_hinge, magnetic builders"
Task: "Implement inset, sliding_catch, slipover, slipover_path builders"
Task: "Implement cap_path, no_lid, path, card_library builders"

# Launch all box type tasks together:
Task: "Implement CapBox, HingeBox, FilamentHingeBox"
Task: "Implement MagneticBox, InsetBox, SlidingCatchBox"
Task: "Implement SlipoverBox, SlipoverPathBox, CapPathBox"
Task: "Implement NoLidBox, PathBox, CardLibraryBox"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (sliding box + compartments)
4. **STOP and VALIDATE**: Run `project.export()` for a single box with 3 compartments
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Single box with compartments (MVP)
3. US2 → All box types selectable
4. US9 → Lids decorated with labels, patterns, colors
5. US3 + US4 → Finger cutouts + auto-layout
6. US7 + US8 → Auto-sizing + spacers + 3MF export
7. US5 + US6 → Nested boxes + manual positioning
8. Each phase adds value without breaking previous phases

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done — parallel:
   - Developer A: US1 (box + compartments)
   - Developer B: US2 (all box types)
3. After US1+2 done — parallel:
   - Developer A: US9 (lid decoration)
   - Developer B: US3 + US4 (finger cutouts + auto-layout)
4. After US4+9 done — sequential:
   - Developer A: US7 (auto-sizing)
   - Developer B: US8 (export)
5. Finally: US5+6 (nested + manual), then Polish

---

## Phase 15: Declarative Layout (T186)

**Purpose**: Close the gap between hand-typed coordinates and free-form packing.

**Goal**: An insert states its *structure* — three columns, each a set of rows, each row a stack — and the coordinates fall out of the box sizes. Densely packed inserts (above the ~70% fill where the packer gives up) stop needing hand-maintained numbers.

**Independent Test**: Convert an example that had explicit positions and verify every derived position equals the coordinate it used to be given.

- [x] T204 Implement `pyboxbuilder/layout.py` — `columns`/`rows`/`stack` groups that nest freely, `measure` (sum along the group's axis, max on the others), and `arrange` (each child starts where the previous ended)
- [x] T205 Add `Project.arrange(layout, origin=...)` — resolve the tree, set every builder's position, and reject an arrangement that does not fit the game box
- [x] T206 Export `columns`/`rows`/`stack` from the package's public surface
- [x] T207 Convert `boxes/emberleaf/emberleaf.py` — 21 hand-typed coordinates replaced by one nested `columns(...)` expression
- [x] T208 Convert `boxes/earth_animal_kingdom/earth_animal_kingdom.py` to `columns(stack(...), stack(...), "CanopyBox")`
- [x] T209 [P] Write test: measurement and placement on each axis, nesting, gaps, duplicate and unknown-box errors, container-fit rejection, in `tests/test_pyboxbuilder/test_layout.py`
- [x] T210 [P] Write test: Emberleaf's derived positions equal the original's hand-typed coordinates

**Checkpoint**: Both converted examples pass their existing position assertions unchanged — the derived coordinates are identical to the ones they replaced, including the three spacers the packer finds in the leftover space.

### Hausdorff comparison — found while running the converted examples

- [x] T211 Fix `hausdorff_distance` reporting 0.0 for meshes that differ. Two causes, both of which alone make the exporter skip writing changed geometry:
  1. **Vertex-only sampling.** pymeshlab defaults to `samplevert` at `samplenum=8`. Every vertex of a 10x10x5 box lies exactly on a side face of a 10x10x6 one, so the measured distance was zero for boxes differing by 0.5mm. Now samples faces and edges too, at 10,000 samples.
  2. **One-sided measurement.** Hausdorff is the larger of the two directions and they are not equal — in that example A→B is 0.0 while B→A is 0.5. Both directions are now measured.
- [x] T212 [P] Write a deterministic test for the Hausdorff branch. It had been exercised only by accident: pymeshlab lives in the project venv, which reaches `sys.path` only once some unrelated test module imports `tests/venv_path.py`, so whether the branch ran at all depended on test ordering. The test now loads pymeshlab from the venv itself and skips only if it is genuinely absent.

---

## Phase 16: Real Mating Lid Geometry (T162, T163)

**Purpose**: Six box types returned a flat plate where their closure should be.

**Goal**: Every lidded type produces a lid that mates with its body — and the body carries the matching half of the same feature.

**Independent Test**: For each of the eleven lidded types, the closed lid and its body share no volume.

- [x] T213 Implement `pyboxbuilder/box/features.py` — the closure features, each returning both halves from one function so they cannot drift apart: `rabbet`, `sliding_track`, `sliding_catch`, `filament_hinge`, and the polygon-footprint `path_cap` / `path_sleeve`
- [x] T214 `InsetBox`: a ledge cut into the top rim and a plate that drops into it flush, so the box still stacks
- [x] T215 `SlidingCatchBox`: sliding grooves plus a detent — a bump on the lid dropping into a slightly larger dimple, so it clicks rather than jams
- [x] T216 `CardLibraryBox`: the same sliding channel with a heavier latch
- [x] T217 `CapPathBox` and `SlipoverPathBox`: cap and sleeve whose skirts follow a polygon footprint, falling back to the rectangular closure when no path is given
- [x] T218 `FilamentHingeBox` (T163): interleaved knuckles along the back edge bored for a filament pin, each leaf webbed to its own half
- [x] T219 Fix the hinge geometry so the two halves are genuinely separate parts. Three defects, each of which fuses lid to body: the lid's plate sat at the rim where the walls already were (1408mm³ of overlap); the pin axis was sunk into the back wall, burying the lid's knuckles in it (154mm³); and the lid's web stood 0.2mm proud of the closed lid.
- [x] T220 [P] Write test: no lid overlaps its body, for every lidded type; plus per-feature properties — the rabbet is flush, a groove never cuts through its wall, the catch dimple is larger than its bump, the hinge leaves never touch at 3/5/9 knuckles — in `tests/test_pyboxbuilder/test_closures.py`
- [x] T221 `HingeBox` (T163): the same knuckle hinge with a printed pin. Its body already had knuckles but the lid was a bare plate, so nothing could turn — both halves now interleave on one pin axis.
- [x] T222 [P] Write test: the hinge lid reaches past the back wall, both halves meet the same pin axis, and the part of the lid over the box footprint is flush at the stated height — the barrel is allowed to stand proud behind the box, as real hinges do
- [x] T223 Regenerate the golden images for the changed inset, hinge and filament-hinge bodies

**Checkpoint**: All eleven lidded types close with **0.00mm³** of body/lid intersection, measured.

---

## Phase 17: A packer for densely-filled inserts (T187)

The extreme-point solver places boxes at corner points, which fragments the free space. Above roughly 70% fill it cannot find arrangements that demonstrably exist, and it has a second, quieter fault: it floats boxes. A box resting one corner on another counted as placed, so a "successful" packing could contain a tray suspended in mid-air.

Adding a support check to that solver is not the fix — measured, it made the Emberleaf search 3000x more expensive (132 nodes to 300,000+, 0.08s to 306s) and it still found nothing. The corner-point space is the wrong space to search.

`pyboxbuilder/packing/guillotine.py` searches free *regions* instead, and gets three properties the corner-point search cannot have:

- **Support is structural.** Space is only ever opened above a box's own top face, or above a layer flagged `full` — one that must be filled solid. No overhang is representable, so none has to be checked for.
- **Feasibility depends on region sizes alone.** Regions are disjoint, so their positions cannot affect what fits. The memo key is therefore position-free, which is what keeps the state count searchable.
- **Smallest region first.** Fail-first: the most constrained region has the fewest options. This is the single biggest lever — measured on Emberleaf, largest-region-first finds nothing in 1,000,000 nodes; smallest-region-first solves it in 3,237.

- [x] T224 Implement `pyboxbuilder/packing/guillotine.py` — region-based guillotine search with class deduplication (five identical player boxes cost no more than one), volume bounds, and a memo keyed on region sizes
- [x] T225 Add the layer cut. Cutting only at a placed box's own faces cannot express a box bridging two boxes below it, which is how real inserts stack; on random instances built by cutting a container up — so a packing is known to exist — that gap cost 6 of 20. The layer cut spans the whole region and marks the rest of that layer `full`, so a bridge always spans solid material. 20 of 20 after.
- [x] T226 Prefer the unrotated orientation on ties. A lone 100×80×40 box in a 300×200×80 container came back turned to 80×100×40 — legal, but it changes the printed part's orientation for nothing.
- [x] T227 Make the guillotine solver primary in `pack_boxes`, keeping the extreme-point solver as a fallback (it searches a different, non-guillotine space) and porting the FR-012 expansion passes across
- [x] T228 Make the fallback's legacy `compartments` import lazy and optional, so its absence raises `PackingError` like any other packing failure instead of an `ImportError`
- [x] T229 [P] Write test: every reported packing is validated as buildable — inside the container, no two boxes overlapping, every box fully supported — plus Emberleaf packs, 285mm is correctly refused, no-rotate is honoured, bridging works over a solid layer and not over a gap, and 20 instances known to tile exactly all solve, in `tests/test_pyboxbuilder/test_guillotine.py`

**Checkpoint**: Emberleaf's 18 boxes at 77% fill pack in **0.05s** through `pack_boxes`, fully supported and validated. Emberleaf keeps its declarative `arrange()`, which states intent a solver cannot infer.

---

## Phase 18: A closed box is the size it says it is

Found by comparing the Emberleaf player box against `examples/emberleaf.scad` directly — slicing both at matched heights and measuring, rather than eyeballing renders.

**A box's declared size is the outside of the CLOSED box.** That is the space the packer reserves, the space `arrange()` allots, and the space the spacers fill around. Seven of the eleven lidded types broke it, by building a full-size body and hanging the lid off the outside of it:

| type | declared | actually built |
|---|---|---|
| `cap`, `cap_path` | 100 × 80 × 40 | 104.4 × 84.4 × 42 |
| `slipover`, `slipover_path` | 100 × 80 × 40 | 103.2 × 83.2 × 42 |
| `magnetic` | 100 × 80 × 40 | 100 × 80 × 42 |
| `card_library` | 100 × 80 × 40 | 100 × 80 × 40.04 |
| `hinge` | 100 × 80 × 40 | 100 × 86.25 × 41 |

For Emberleaf this is not cosmetic. Each cap-lid player box declared 98 × 142.5 × 13.125 and actually measured **104.4 × 148.9 × 15.125**: five of them need 75.6mm of a 52.5mm column and are 6.4mm too wide for it. The insert could not have been assembled. The original's body measures 10.93mm tall against the port's 13.125 — `body_height = height - lid_thickness - m_piece_wiggle_room`, which is where the convention was read from.

The T220 tests missed it because "no lid overlaps its body" is satisfied perfectly by a lid sitting entirely outside the box.

- [x] T230 Add the shared closure metrics to `pyboxbuilder/box/features.py` — `cap_metrics`/`cap_body`/`cap_lid`, `slipover_metrics`, `path_body_metrics` — so a body and the lid that wraps it derive from one set of numbers and cannot drift
- [x] T231 `CapBox` / `CapPathBox`: body stops a lid thickness short and steps its top band in by the lid's wall thickness; the cap's outer face is the declared footprint and its top the declared height
- [x] T232 `SlipoverBox` / `SlipoverPathBox`: body inset all round and stopped short, sleeve back out to the declared outline; `foot` keeps the full footprint at the bottom for the sleeve to seat on
- [x] T233 `MagneticBox`: body stops a lid thickness short so the plate closes flush at the declared height
- [x] T234 `sliding_catch`: trim the lid's catch bump to the box envelope. It engages sideways in the groove, so losing its crown costs nothing, and leaving it proud made `card_library` 0.04mm too tall
- [x] T235 Fix `path_cap` / `path_sleeve`, which grew the declared outline outward (`offset_footprint` by a negative distance) instead of insetting the body
- [x] T236 [P] Write test: every closed box measures exactly its declared size **over its declared footprint**, and nothing but a hinge barrel has any material outside that footprint — in `tests/test_pyboxbuilder/test_closures.py`. Measuring over the footprint is what makes the hinge expressible as a bounded exception rather than a blanket one.
- [x] T237 Regenerate the cap and magnetic goldens. Note they did **not** fail: the renders use `--viewall`, so a uniformly shorter box looks almost identical and the 2.31 / 1.68 measured difference sits under the 12.0 tolerance. Image goldens cannot police dimensions; T236 can.
- [x] T238 Give `boxes/earth/earth.py` the sys.path bootstrap every other example carries — without it it fails with a bare `No module named 'pybosl2'` unless the caller has already set the path up

**Checkpoint**: All 13 box types build a closed box exactly the size they were asked for. Emberleaf's player box body is **10.925mm** against the original's 10.93, closing to the declared 98 × 142.5 × 13.125. All six examples export.

### Remaining fidelity gaps (not defects, but not matched either)

Measured against the original, the player box still carries 72,813mm³ of material to the original's 63,815mm³. Three known causes, all cosmetic:

1. The original rounds the body's outer vertical corners and bottom edge (`rounding=` on the `cuboid`); the port's are square.
2. The pull-out recess is `RoundedBoxAllSides` in the original — a dish with a rounded bottom hulled up to a full-size flat top. The port cuts a straight-walled prism with rounded vertical corners only.
3. The marker grip notches are `cyl(d=13, rounding=6)` in the original — nearly a lens — against the port's plain cylinders, so the port's read as one fused blob rather than separate notches.

---

## Phase 19: Interactive preview — `Project.show()` (plan §Make vs. Interactive)

**Purpose**: `show()` exists but only unions bodies at their packed positions. The plan asks it to be a readable preview.

**Goal**: A viewer can tell one box from another, see through a lid, look under a layer, and see the spacers that fill the dead space.

**Independent Test**: Show a 4-box project with `remove_layers=1` and verify the top layer's boxes are absent from the rendered solid while every lower box is present.

- [ ] T239 Add `remove_layers: int = 0` to `Project.show()` — omit the top N vertical layers of the packed layout (a box is in a removed layer when its top surface sits above the N-th slice), revealing what is underneath, in `pyboxbuilder/project.py`
- [ ] T240 [P] Assign each box a stable colour for preview: its own body colour when set, otherwise a deterministic pseudo-random hue hashed from its label. View-time only — it must not reach the exported geometry or its material, in `pyboxbuilder/project.py`
- [ ] T241 [P] Render spacer placements in `show()` too, always in a variant of grey drawn from outside the per-box palette, so dead fill is instantly distinguishable from a real box
- [ ] T242 [P] Render a shown lid semi-transparent (50% alpha) in a slightly lighter shade of its box's colour, so the lid reads as a separate piece and the box stays visible through it
- [ ] T243 [P] Write test: `remove_layers` drops exactly the boxes above each slice (0 → all, N → none of the top layer), colours are stable across runs and unique per label, spacers are grey and lids lighter-and-transparent, and `show()` writes no files, in `tests/test_pyboxbuilder/test_show.py`

**Checkpoint**: `project.show()` is a usable layout preview, not a monolithic union.

---

## Phase 20: Curve precision — `fn` / `fa` / `fs` (plan §Curve precision)

**Purpose**: Every curve currently renders at whatever default the call site happened to get; nothing is overridable.

**Goal**: One precision setting on `export()`/`show()` reaches every curved feature, and no geometry call hardcodes a facet count the caller cannot override.

**Independent Test**: Export the same box at `fn=8` and `fn=64` and verify the cylinder-derived features change facet count while the box's measured bounding box does not.

- [ ] T244 Add optional `fn`, `fa`, `fs` parameters to `Project.export()` and `Project.show()` and thread them through a single render-context object rather than a parameter on every call, in `pyboxbuilder/project.py`
- [ ] T245 Consume the context in every geometry call that renders a curve — cylinders/spheres, `cuboid(rounding=)`, fillets and chamfers, finger-scoop and finger-hole profiles, hex and tessellation edges, and lid-pattern curves — in `pyboxbuilder/box/`, `pyboxbuilder/compartments/`, `pyboxbuilder/lid/`
- [ ] T246 [P] Write test: defaults are `fa=12, fs=2`; an explicit `fn` reaches a scoop, a hex cell and a lid pattern; and no module hardcodes a facet count (grep-style assertion over `pyboxbuilder/`), in `tests/test_pyboxbuilder/test_precision.py`

**Checkpoint**: Precision is one knob, from fast preview to print quality.

---

## Phase 21: Edge smoothing and silhouette fidelity (FR-043, FR-044, FR-045)

**Purpose**: The plan requires that nothing a finger or a card touches be a sharp 90° edge — but no box body is rounded today and `rounding` exists only inside `compartments/carve.py`.

**Goal**: Structural edges are filleted at a configurable small radius; piece silhouettes are untouched.

**Independent Test**: Slice a box body at its top rim and at the wall/floor junction and verify a filleted profile at both, then verify an SVG element's outline is vertex-for-vertex what was parsed.

- [ ] T247 Add a configurable `rounding` (default 1.0mm) to `Project` and `BoxBuilder`, and round the box body's outer vertical corners, top rim and bottom base edge via `cuboid(rounding=)` in `pyboxbuilder/box/shell.py` (FR-044)
- [ ] T248 Rebuild the card finger scoop as one continuous filleted profile running top rim → floor: the top opening curves into the wall, the bottom blends into the floor, deep enough to reach below the lowest card without breaching the floor from outside, in `pyboxbuilder/compartments/finger_hole.py` (FR-043)
- [ ] T249 Sliding boxes: apply the chamfer/rounding to the **lower** lid-track wall, not the higher one, so it cannot foul the dovetail. Rotate the lid section to the opposite side when that puts the smooth edge on the non-track side, and skip the rotation when the box's length/width ratio makes it wasteful (a long narrow card box), in `pyboxbuilder/box/types/sliding.py` + `box/features.py`
- [ ] T250 [P] Fillet the remaining touched edges — compartment top rim, wall/floor junction, and finger-hole walls — at the same configurable radius, in `pyboxbuilder/compartments/carve.py`
- [ ] T251 [P] Enforce silhouette fidelity (FR-045): no smoothing/rounding pass may run over `CompartmentElement` shape geometry or a parsed SVG path, even where the outline is hard to print, in `pyboxbuilder/compartments/element.py`
- [ ] T252 [P] Write test: body rim/corner/base edges are filleted at the configured radius and the radius is overridable; the card scoop is continuous from rim to floor and does not breach the floor; the sliding chamfer lands on the low track wall; an SVG element's outline is unchanged by any smoothing setting — in `tests/test_pyboxbuilder/test_smoothing.py`
- [ ] T253 Regenerate the golden images the rounded bodies change, in `tests/test_pyboxbuilder/golden/`

**Checkpoint**: Nothing a hand touches is a sharp edge, and nothing a piece defines has been softened.

---

## Phase 22: Validation, errors and warnings (plan §Validation)

**Purpose**: `pyboxbuilder` raises 16 `ValueError`s and emits **zero** warnings; the spec's edge-case table asks for both.

**Goal**: Every rejected configuration names its offender, and every degraded-but-legal configuration says so without stopping the export.

**Independent Test**: Run the table — each error row raises with the offender named, each warning row completes the export and emits exactly one warning.

- [ ] T254 Add `pyboxbuilder/errors.py` — `PackingError` plus a single `warn()` helper (stdlib `warnings`, project-specific category) so warnings are filterable and testable with `assertWarns`
- [ ] T255 Implement the missing rejections: hex grid `rows`/`cols` ≤ 0; a hex tile leaving zero cells fitting the interior; a magnet slot count exceeding the available straight-wall length (slots must never cross a corner, FR-039); a spacer whose computed height is ≤ 0; a box with neither compartments nor an explicit `size` — each naming the box/compartment and the offending value
- [ ] T256 Implement the missing warnings: `LidBuilder` set on a lidless box type (warn + drop the decoration); an empty exported mesh (warn + do **not** write the file); body colour equal to all three accent colours (warn — degenerates to one material); overlapping finger cutouts; and an empty project returning an empty `ExportResult` with no PDF and no error
- [ ] T257 Confirm the documented non-errors stay non-errors: `expandable=True` on a standalone box is ignored silently, a corrupt `.layout_cache.json` is a cache miss, and zero-thickness walls between adjacent compartments merge into one cavity
- [ ] T258 [P] Write test: one case per row of both tables in the plan's *Validation, Errors and Warnings*, asserting the exact message for errors and `assertWarns` for warnings, in `tests/test_pyboxbuilder/test_validation.py`

**Checkpoint**: Invalid input is rejected with an explanation; degraded input is flagged and still builds.

---

## Phase 23: Typed options — no bare strings (plan §Typed Options)

**Purpose**: `BoxBuilder.stackable` and `.magnet_type` are `str | None`, which the constitution's "enums for all type selections, no bare strings" forbids.

**Independent Test**: A bare string in either field is a type error under pyright and a `TypeError` at runtime.

- [ ] T259 Add `StackableMode` (`INSIDE`, `OUTSIDE`) and `MagnetType` (`ROUND`, `RECT`, `NONE`) to `pyboxbuilder/enums.py`, and give `ScoopSide` a real default member instead of `None`
- [ ] T260 Migrate `BoxBuilder`, `box/types/no_lid.py`, the registry and all six example projects that set them; reject a bare string at construction rather than coercing it
- [ ] T261 [P] Write test: enum members round-trip through builder → box type → geometry, a bare string raises, and `boxes/stackable_hexes` still produces its 8 variants unchanged, in `tests/test_pyboxbuilder/test_enums.py`

---

## Phase 24: Documentation, dual-run examples, and traceability

**Purpose**: Three standing policies in the plan have no task: the docstring rules, the run-in-both-environments rule for examples, and the coverage map.

**Independent Test**: Every `boxes/*` project both imports cleanly (building its `Project`, writing nothing) and exports when run as `__main__` with `FROM_MAKE=1`.

- [ ] T262 Audit every public class/method/function/enum/dataclass field in `pyboxbuilder/` against the plan's *Documentation Policy* — mandatory `Args:`/`Returns:` sections, documented dataclass fields, no one-liners on public API — and fill the gaps
- [ ] T263 [P] Add a docs check to `.github/workflows/docs.yml` that fails the build on a public symbol with no docstring or a missing `Args:`/`Returns:` section, so `pdoc pyboxbuilder` cannot silently drift from the policy
- [ ] T264 [P] Write test: every project under `boxes/` imports without `__file__`, builds its `Project` without exporting, and exports under `FROM_MAKE=1` — parameterised over the directory listing so a new example is covered the day it lands, in `tests/test_pyboxbuilder/test_examples_dual_run.py`
- [ ] T265 [P] Give the five undocumented examples (`arkham_horror`, `dominion`, `first_class`, `magical_athlete`, `nippon`) a README each stating the game box size and what the port demonstrates, matching `boxes/earth_animal_kingdom/README.md`
- [ ] T266 [P] Write test: the plan's *Requirements Coverage Map* stays honest — every SC row names a test module that exists, in `tests/test_pyboxbuilder/test_coverage_map.py`

**Checkpoint**: The policies the plan states are enforced by CI rather than by memory.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All geometry uses pybosl2 only — no native pythonscad imports
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
