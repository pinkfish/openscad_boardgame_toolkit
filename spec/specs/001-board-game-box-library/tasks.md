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

- [x] T001 Create `spec_driven/` package directory with `__init__.py` and `py.typed` marker
- [x] T002 [P] Implement enums (`BoxType`, `LabelMode`, `PatternType`, `ScoopSide`) in `spec_driven/enums.py`
- [x] T003 [P] Implement `Color` dataclass with named presets in `spec_driven/color.py` *(superseded: removed — use `pybosl2.Color` directly, no Color class)*
- [x] T004 [P] Create `spec_driven.py` root import module re-exporting public surface
- [x] T005 [P] Write test for enums validation in `tests/test_spec_driven/test_enums.py`
- [x] T006 [P] Write test for Color in `tests/test_spec_driven/test_color.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Implement `BoxBuilder` base frozen dataclass with common fields including `box_id` (unique instance identifier) and `final_size` (resolved by 3D packer) in `spec_driven/builders/_base.py`
- [x] T008 [P] Implement `CompartmentBuilder` frozen dataclass in `spec_driven/compartments/builder.py`
- [x] T009 [P] Implement `LidBuilder` and `PatternBuilder` frozen dataclasses in `spec_driven/lid/builder.py`
- [x] T010 Implement `BoxProtocol` abstract base and `Interior` dataclass in `spec_driven/box/base.py`
- [x] T011 Implement `Project` class skeleton (constructor, `box()` factory with `@overload` signatures, empty `export()`) in `spec_driven/project.py`
- [x] T011a [P] Implement default clearance gap constant for 3D printing tolerances in `spec_driven/compartments/builder.py`
- [x] T012 [P] Write test for BoxBuilder instantiation/validation including `box_id` uniqueness and `final_size` in `tests/test_spec_driven/test_builders.py`
- [x] T013 [P] Write test for CompartmentBuilder in `tests/test_spec_driven/test_compartments.py`
- [x] T014 [P] Write test for LidBuilder/PatternBuilder in `tests/test_spec_driven/test_lid_builder.py`
- [x] T015 [P] Write test for Project constructor and basic box registration in `tests/test_spec_driven/test_project.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Basic Box with Interior Compartments (Priority: P1) 🎯 MVP

**Goal**: User can create a `Project`, add one box with compartments, and get a generated box body with compartments carved into the interior.

**Independent Test**: Create a box of 200x150x60mm with 3 compartments, verify compartments fit within the interior without overlaps.

### Tests for User Story 1

- [x] T016 [P] [US1] Write render test: single box with 3 compartments, verify interior dimensions in `tests/test_spec_driven/render/test_box_render.py`
- [x] T017 [P] [US1] Write unit test: compartment layout fits interior bounds in `tests/test_spec_driven/test_compartments.py`

### Implementation for User Story 1

- [x] T018 [US1] Implement `SlidingBoxBuilder` (extends BoxBuilder, adds `two_layer` etc., `size` defaults to `None` for auto-compute from compartments) in `spec_driven/builders/sliding.py`
- [x] T019 [US1] Implement `SlidingBox` class (body + lid geometry) using pybosl2 in `spec_driven/box/types/sliding.py`
- [x] T020 [US1] Implement box type registry (`BoxType` → class mapping) in `spec_driven/box/registry.py`
- [x] T021 [US1] Implement interior computation and hollowing in `spec_driven/box/interior.py`
- [x] T022 [US1] Implement compartment auto-layout with 90-degree rotation support (2D shelf-based packing) in `spec_driven/compartments/layout.py`
- [x] T022a [US1] Implement `project.share_compartments()` shared compartment auto-packing API in `spec_driven/project.py`
- [x] T023 [US1] Wire `Project.box()` → builder → BoxSpec → box construction in `spec_driven/project.py`

**Checkpoint**: User Story 1 fully functional — one box type with compartments

---

## Phase 4: User Story 2 - Choose Among Different Box Lid Types (Priority: P1)

**Goal**: All 14 box types are implemented and selectable via `BoxType` enum. Each type produces correct mating lid geometry.

**Independent Test**: Generate a sliding box and a cap box; verify each lid fits its body and opens/closes correctly.

### Tests for User Story 2

- [x] T024 [P] [US2] Write render test: all 14 box types produce valid geometry in `tests/test_spec_driven/render/test_box_render.py`
- [x] T025 [P] [US2] Write unit test: registry returns correct class per BoxType in `tests/test_spec_driven/test_builders.py`

### Implementation for User Story 2

- [x] T026 [P] [US2] Implement remaining box type builders (cap, hinge, filament_hinge, magnetic) in `spec_driven/builders/`
- [x] T027 [P] [US2] Implement remaining box type builders (inset, sliding_catch, slipover, slipover_path) in `spec_driven/builders/`
- [x] T028 [P] [US2] Implement remaining box type builders (cap_path, no_lid, path, card_library) in `spec_driven/builders/` *(path builder added 2026-08-13 — `spec_driven/builders/path.py` had never been written)*
- [x] T029 [P] [US2] Implement box types: CapBox, HingeBox, FilamentHingeBox in `spec_driven/box/types/`
- [x] T030 [P] [US2] Implement box types: MagneticBox, InsetBox, SlidingCatchBox in `spec_driven/box/types/`
- [x] T031 [P] [US2] Implement box types: SlipoverBox, SlipoverPathBox, CapPathBox in `spec_driven/box/types/`
- [x] T032 [P] [US2] Implement box types: NoLidBox, PathBox, CardLibraryBox in `spec_driven/box/types/` *(PathBox added 2026-08-13 — polygon footprint, lidless, `LIDLESS_BOX_TYPES` in the registry)*
- [x] T033 [US2] Wire all box types into registry and verify `Project.box(BoxType.X, ...)` dispatches correctly in `spec_driven/box/registry.py`

**Checkpoint**: All 14 box types functional — any type selectable via enum

---

## Phase 5: User Story 9 - Decorate Lids with Labels, Patterns, and Print-Optimized Color Layers (Priority: P2)

**Goal**: Lids get auto-sized labels (framed/frameless/diagonal), through-hole patterns (hex, grid, voronoi), three accent colors per lid. Min text height guard skips illegible labels.

**Independent Test**: Create a lid with "Animals" text, hex-grid through-holes, and framed diagonal label; verify correct color assignments in 3MF.

### Tests for User Story 9

- [x] T034 [P] [US9] Write unit test: label auto-sizing fills lid minus margin in `tests/test_spec_driven/test_lid_label.py`
- [x] T035 [P] [US9] Write unit test: min text height guard skips labels < 4mm in `tests/test_spec_driven/test_lid_label.py`
- [x] T036 [P] [US9] Write render test: lid with framed label + hex pattern + colors in `tests/test_spec_driven/render/test_lid_render.py`

### Implementation for User Story 9

- [x] T037 [US9] Implement label generation: framed (rect frame + diagonal hatching + outer border) in `spec_driven/lid/label.py`
- [x] T038 [US9] Implement label generation: frameless (text only) in `spec_driven/lid/label.py`
- [x] T039 [US9] Implement corner-to-corner diagonal text orientation in `spec_driven/lid/label.py`
- [x] T040 [US9] Implement min text height guard (default 4mm, settable) in `spec_driven/lid/label.py`
- [x] T041 [US9] Implement pattern fill functions (hex grid, grid) as through-holes in `spec_driven/lid/pattern.py`
- [x] T042 [US9] Implement pattern fill function (voronoi) — borrow tessellation from existing codebase in `spec_driven/lid/pattern.py`
- [x] T043 [US9] Implement color layer assignment (3 independent accent colors, per-material 3MF mapping) in `spec_driven/lid/color_layers.py`
- [x] T044 [US9] Wire `LidBuilder` → label + pattern + color layers → lid geometry in `spec_driven/lid/builder.py`

**Checkpoint**: Lid decoration fully functional — labels, patterns, colors

---

## Phase 6: User Story 3 - Finger Cutouts for Easy Piece Removal (Priority: P2)

**Goal**: Compartments can have finger scoops on any side wall or floor notch for shallow compartments.

**Independent Test**: Compartment with front finger scoop admits a 14mm radius sphere at the scoop cutout.

### Tests for User Story 3

- [x] T045 [P] [US3] Write unit test: scoop dimensions match specification in `tests/test_spec_driven/test_compartments.py`
- [x] T046 [P] [US3] Write render test: compartment with scoop on all 4 sides in `tests/test_spec_driven/render/test_box_render.py`

### Implementation for User Story 3

- [x] T047 [US3] Implement wall finger scoop (notch) geometry in `spec_driven/compartments/finger_hole.py`
- [x] T048 [US3] Implement floor finger scoop geometry with shallow-depth fallback to wall notch in `spec_driven/compartments/finger_hole.py`
- [x] T049 [US3] Wire `CompartmentBuilder.finger_scoop` and `ScoopSide` to compartment construction in `spec_driven/compartments/builder.py`

**Checkpoint**: Finger scoops functional on all 4 sides, auto-fallback for shallow compartments

---

## Phase 7: User Story 4 - Automatic Compartment Layout (Priority: P2)

**Goal**: Compartments auto-arrange in rows without manual positioning. Grouped compartments stay together.

**Independent Test**: 10 compartments of varying sizes automatically arranged within a box interior without overlaps.

### Tests for User Story 4

- [x] T050 [P] [US4] Write unit test: auto-layout places 10 compartments without overlap in `tests/test_spec_driven/test_compartments.py`
- [x] T051 [P] [US4] Write unit test: grouped compartments stay adjacent in `tests/test_spec_driven/test_compartments.py`

### Implementation for User Story 4

- [x] T052 [US4] Enhance shelf-based 2D bin packing with row-first placement in `spec_driven/compartments/layout.py`
- [x] T052a [US4] Implement compartment row-width distribution (size compartments to fill row width) in `spec_driven/compartments/sizing.py` *(written 2026-08-13 — the module had never been created)*
- [x] T053 [US4] Implement compartment grouping (grouped items packed together) in `spec_driven/compartments/layout.py`
- [x] T054 [US4] Implement overflow detection with descriptive error messages in `spec_driven/compartments/layout.py`
- [x] T054a [US4] Implement compartment clipping to non-rectangular polygon interior regions (FR-018) in `spec_driven/compartments/layout.py`
- [x] T054b [US4] Support bin-packing for non-rectangular compartments (hexagons, circular slots, custom shapes like Emberleaf species) using their rectangular bounding boxes in `spec_driven/compartments/layout.py`

**Checkpoint**: Compartments auto-laid-out in rows, grouped compartments stay adjacent

---

## Phase 8: User Story 7 - Auto-Size Sub-Boxes and Fill Gaps with Spacers (Priority: P2)

**Goal**: Sub-boxes with minimum dimensions auto-expand to fill rows. Row lengths align. Gaps > 10mm produce hollow spacer trays. Gaps < 10mm absorbed by adjacent boxes.

**Independent Test**: 4 sub-boxes in a 300x200mm game box produce rows with common lengths and spacers for gaps > 10mm.

### Tests for User Story 7

- [x] T055 [P] [US7] Write unit test: auto-sizing expands boxes to fill rows in `tests/test_spec_driven/test_packing.py`
- [x] T056 [P] [US7] Write unit test: row lengths match longest box in row in `tests/test_spec_driven/test_packing.py`
- [x] T057 [P] [US7] Write unit test: gaps > 10mm produce spacers, gaps < 10mm absorbed, and `final_size` correctly propagated to builders in `tests/test_spec_driven/test_packing.py`
- [x] T058 [P] [US7] Write render test: 4-box game with spacers in `tests/test_spec_driven/render/test_box_render.py`

### Implementation for User Story 7

- [x] T059 [US7] Implement 3D box packing into game box interior using a 3D packing solver with dynamic dimension expansion in `spec_driven/packing/layout.py`
- [x] T060 [US7] Implement auto-sizing expansion (fill-to-fit rows, common length per row) and propagate resolved sizes back to builders via `final_size` attribute in `spec_driven/packing/layout.py`
- [x] T061 [US7] Implement spacer tray generation from gap dimensions (NoLidBox hollow trays) in `spec_driven/packing/spacer.py`
- [x] T062 [US7] Implement gap threshold logic (absorb < 10mm, spacer if ≥ 15mm, absorb 10-15mm) in `spec_driven/packing/spacer.py`
- [x] T063 [US7] Wire `Project.export()` → packing solver → auto-sizing with `final_size` propagation → spacer generation in `spec_driven/project.py`

**Checkpoint**: Multi-box games with auto-sizing and spacers fully functional

---

## Phase 9: User Story 8 - Export 3MF Files with Content-Based Caching (Priority: P2)

**Goal**: `Project.export()` produces organized 3MF files in `{out_dir}/{game}/mmu/` and `{out_dir}/{game}/single/`. Hausdorff comparison skips unchanged files. Two-level cache (memory + disk JSON with SHA-256 hash) speeds repeated renders.

**Independent Test**: Export a 2-box project twice; first writes files, second skips all. Modify one box; only that box's files are rewritten.

### Tests for User Story 8

- [x] T064 [P] [US8] Write unit test: ExportResult file counts match expectations in `tests/test_spec_driven/test_export.py`
- [x] T065 [P] [US8] Write unit test: cache hit/miss based on SHA-256 hash using `.layout_cache.json` in `tests/test_spec_driven/test_packing.py`
- [x] T066 [P] [US8] Write render test: second export writes 0 files (Hausdorff skip) in `tests/test_spec_driven/render/test_export_render.py`
- [x] T067 [P] [US8] Write render test: partial change exports only modified files in `tests/test_spec_driven/render/test_export_render.py`

### Implementation for User Story 8

- [x] T068 [P] [US8] Implement `ExportResult` frozen dataclass in `spec_driven/export/result.py`
- [x] T068a [US8] Implement MMU color-copy logic (positive inserts in different material/color from body) in `spec_driven/export/exporter.py` *(written 2026-08-13 — `BoxExporter._compose` keeps inserts as distinct objects in mmu, fuses them in single)*
- [x] T068b [US8] Implement bounding-box reporting for each exported piece (FR-027) in `spec_driven/export/exporter.py` *(written 2026-08-13 — `PieceBounds`, surfaced as `Project.piece_bounds`)*
- [x] T069 [P] [US8] Implement two-level layout cache (in-memory dict + disk `spec_driven/.layout_cache.json`, SHA-256 key, version invalidation) to store 3D box packing layouts and bypass solver on subsequent runs in `spec_driven/packing/cache.py`
- [x] T070 [US8] Implement `BoxExporter` with per-box/per-spacer 3MF file writing in `spec_driven/export/exporter.py` *(written 2026-08-13 — `Project.export` used to `touch()` empty files; it now exports real 3MF geometry through the `openscad` module)*
- [x] T071 [US8] Implement Hausdorff conditional write (pymeshlab compare, skip if distance < 0.001mm) in `spec_driven/export/hausdorff.py` *(written 2026-08-13 — falls back to a `<mesh>`-only digest when pymeshlab is absent, because 3MF stamps a timestamp and fresh UUIDs on every write and so never matches byte for byte)*
- [x] T072 [US8] Implement organized output directory structure (`mmu/` + `single/`, `_body.3mf` / `_lid.3mf` naming) in `spec_driven/export/exporter.py` *(moved out of `project.py` into `BoxExporter` 2026-08-13)*
- [x] T073 [US8] Wire full `Project.export()` pipeline: pack with dynamic dimension expansion → auto-size with `final_size` propagation → spacers → build → export in `spec_driven/project.py`

**Checkpoint**: Full export pipeline functional — cached, Hausdorff-gated, organized output

---

## Phase 10: User Story 5 + User Story 6 - Nested Boxes & Manual Positioning (Priority: P3)

**Goal**: Nested sub-boxes inside a game box with validation. Manual compartment positioning overrides auto-layout.

**Independent Test**: Outer box 300x300x80mm with 4 sub-boxes fits without overlap. Manual (x,y) positions applied correctly.

### Tests for User Story 5/6

- [x] T074 [P] [US5] Write unit test: 4 sub-boxes fit in 300x300x80mm outer box in `tests/test_spec_driven/test_packing.py`
- [x] T075 [P] [US6] Write unit test: manual positions override auto-layout in `tests/test_spec_driven/test_compartments.py`

### Implementation for User Story 5/6

- [x] T076 [US5] Implement validation: sub-boxes fit within outer interior (footprint + height) with descriptive errors in `spec_driven/packing/layout.py`
- [x] T077 [US6] Implement manual compartment positioning (explicit x, y coordinates) in `spec_driven/compartments/layout.py`
- [x] T078 [US6] Implement overlap detection and error reporting for manually positioned compartments in `spec_driven/compartments/layout.py`

**Checkpoint**: Nested box validation and manual positioning functional

---

## Phase 10b: User Story 10 - Generate Packing Layout PDF Guide (Priority: P3)

**Goal**: `project.export()` produces a `layout.pdf` in the output directory containing multiple pages representing distinct stacking layers (e.g. Base Layer, Middle Layer, Top Layer). On each page, the boxes belonging to that layer are drawn in full color, while already-placed boxes are drawn in light gray. Boxes are labeled, colored, and numbered in packing order. PDF is cached: only regenerated when layout or library version changes.

**Independent Test**: Export a 4-box game, verify `layout.pdf` exists showing 4 labeled boxes at correct positions across one or more pages.

### Tests for User Story 10

- [x] T078a [P] [US10] Write unit test: PDF file exists in output directory after export in `tests/test_spec_driven/test_export.py`
- [x] T078b [P] [US10] Write unit test: PDF skipped on re-export when layout unchanged in `tests/test_spec_driven/test_export.py`

### Implementation for User Story 10

- [x] T078c [US10] Implement 3D oblique projection packing layout renderer (outlines, labels, dimensions, spacer markers) in `spec_driven/export/layout_pdf.py`
- [x] T078d [US10] Implement packing order numbering, colored 3D shaded boxes, vertical exploded displacement, and dashed alignment lines in `spec_driven/export/layout_pdf.py`
- [x] T078e [US10] Implement PDF caching with SHA-256 layout hash (skip regeneration if unchanged) in `spec_driven/export/layout_pdf.py`
- [x] T078f [US10] Wire PDF generation into `Project.export()` pipeline and add `layout.pdf` to `ExportResult` in `spec_driven/project.py`

**Checkpoint**: Packing layout PDF generated and cached alongside 3MF exports

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Reference example, documentation, final integration

- [x] T079 [P] Create `boxes/` directory with `_template/` for new game projects
- [x] T080 [P] Create Earth Animal Kingdom reference example using full spec_driven API in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T081 [P] Create Earth Animal Kingdom README in `boxes/earth_animal_kingdom/README.md`
- [x] T082 Run `npx pyright spec_driven/` — fix any type errors
- [x] T083 Run `python3 tests/run_fast.py test_spec_driven/` — all fast tests pass
- [x] T084 Run full render suite: `python3 -m unittest discover -s tests/test_spec_driven/render` — all render tests pass
- [x] T085 Validate quickstart.md scenarios against implemented API
- [x] T086 [P] Implement ratio-based compartment sizing (`width_ratio`, `length_ratio`, `resolve_size`) in `spec_driven/compartments/builder.py`
- [x] T087 [P] Validate compartment ratio sums ≤ 1.0 per row at export time in `spec_driven/project.py`
- [x] T088 [P] Enforce 0.1mm precision floor on all dimensional output (no rounding to whole mm) in `spec_driven/compartments/builder.py`
- [x] T089 Wire 3D bin-packing solver from `spec_driven/packing/layout.py` to distribute 37 animal entries across two AnimalBox containers in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T090 [P] Generate labeled compartment floors — 0.2mm extruded animal name text per compartment in `spec_driven/compartments/labels.py`
- [x] T091 Verify all 7 Earth Animal Kingdom boxes pack within 288×158mm game box interior using auto-sizing solver in `boxes/earth_animal_kingdom/earth_animal_kingdom.py`
- [x] T092 [P] Write test: ratio-based compartments resolve correctly against interior dimensions in `tests/test_spec_driven/test_compartments.py`
- [x] T093 [P] Write test: ratio overflow validation rejects sum > 1.0 in `tests/test_spec_driven/test_compartments.py`
- [x] T094 [P] Write test: 0.1mm precision maintained in compartment resolution in `tests/test_spec_driven/test_compartments.py`
- [x] T095 [P] Add `mmu_label` and `single_label` optional LidBuilder fields for per-export-mode label overrides in `spec_driven/lid/builder.py`
- [x] T096 [P] Implement per-mode label resolution — `mmu_label`/`single_label` override parent when set, fall back otherwise — in `spec_driven/lid/builder.py`
- [x] T097 Implement compartment label mode switching: engraved 0.2mm cutout for single-color, raised 0.2mm second-color text for MMU via `mode` parameter in `spec_driven/compartments/labels.py`
- [x] T098 Wire per-mode label resolution into `Project.export()` — resolve MMU label for `mmu/` pass, single label for `single/` pass — in `spec_driven/project.py`
- [x] T099 [P] Write test: LidBuilder per-mode override fallback logic in `tests/test_spec_driven/test_lid_builder.py`
- [x] T100 [P] Write test: compartment label mode switching (cutout for single, raised for MMU) in `tests/test_spec_driven/test_lid_label.py`
- [x] T101 [P] Write test: PDF is valid and boxes rendered at correct packed positions (SC-019) in `tests/test_spec_driven/test_export.py`
- [x] T102 [P] Implement standalone box export path — `project.box(...)` exported directly with no game box, no packing, no PDF — in `spec_driven/project.py`
- [x] T103 [P] Implement stackable inside/outside rim generation for no-lid boxes in `spec_driven/box/types/no_lid.py`
- [x] T104 [P] Implement round and rectangular magnet slots on opposing sides in `spec_driven/box/types/no_lid.py`
- [x] T105 Create `boxes/irish_gauge/irish_gauge.py` — 5 company boxes, money box, auto-generated spacers, box sizes derived from game box dimensions
- [x] T106 [P] Auto-generate spacer boxes (rectangular + polygon-path) from leftover space in `spec_driven/packing/spacer.py`
- [x] T107 Write test: Irish Gauge box sizes derived correctly + spacers auto-generated in `tests/test_spec_driven/test_irish_gauge.py`
- [x] T108 [P] Implement `no_rotate` flag propagation through `pack_boxes` → `pack_3d_boxes` orientation selection (FR-013c) in `spec_driven/packing/layout.py` + `compartments.py`
- [x] T109 [P] Implement box-rotation → compartment re-layout: when a placement is `rotated`, re-run `layout_compartments` against the swapped interior dimensions (FR-013b) in `spec_driven/project.py`
- [x] T110 Create `boxes/stackable_hexes/stackable_hexes.py` — 8 hex box variants (1–4 divisions × round/rect magnets) with stackable rims in `boxes/stackable_hexes/`
- [x] T111 [P] Write test: no_rotate boxes are never rotated + rotated boxes re-lay-out compartments (FR-013b/FR-013c) in `tests/test_spec_driven/test_packing.py`
- [x] T112 [P] Expand `PatternType` enum to the full catalog (42 members) — dense/lattice shapes, pentagon tilings R1–R15, and all tessellations — in `spec_driven/enums.py`
- [x] T113 [P] Implement dense/lattice shape fills (DENSE_HEX, DENSE_TRIANGLE, CIRCLE, HEX, OCTOGON, TRIANGLE, SQUARE, SUPERSHAPE, HILBERT, CLOUD) as through-hole functions in `spec_driven/lid/pattern.py`
- [x] T114 [P] Implement pentagon tiling fills (PENTAGON_R1–R15) by wrapping `pentagon_tilings.py` in `spec_driven/lid/pattern.py`
- [x] T115 [P] Implement tessellation fills (LIZARD, VORONOI, LEAF, LEAF_VEINS, DROP, DELTOID_TRIHEXAGONAL, DELTOID_TRIHEXAGONAL_KITE, HALF_REGULAR_HEXAGON, RHOMBI_TRI_HEXAGONAL, PENROSE_TILING_5, PENROSE_TILING_7, PEGASUS, GOOSE, CHICKEN, SHEEP, BIRD, HEX_TESSELATION, KITE_TESSELATION, QUAD_TESSELATION) by wrapping `tesselations/` modules in `spec_driven/lid/pattern.py`
- [x] T116 [P] Update `build_pattern` dispatch to cover every `PatternType` member (no fallback-to-grid) in `spec_driven/lid/pattern.py`
- [x] T117 [P] Write test: every `PatternType` member resolves to a fill function without fallback in `tests/test_spec_driven/test_lid_pattern.py`
- [x] T118 [P] Implement hex-grid compartment layout — `HexGridWithCutouts` port (rows × cols hexagonal cutouts from `tile_width`, deriving circumradius as `tile_width/2/cos(30°)`) in `spec_driven/compartments/hex_grid.py`
- [x] T119 [P] Implement hex-cell push block — raised central hexagonal pillar via `push_block_height` (FR-041) in `spec_driven/compartments/hex_grid.py`
- [x] T120 [P] Implement hex-cell floor finger hole — circular cutout through the cell floor, offset from the pillar when both are enabled (FR-042) in `spec_driven/compartments/hex_grid.py`
- [x] T121 Create `boxes/1835/1835.py` — hex boxes (3×5 hex grid ×4 stacked), money boxes (8 denominations), share boxes (8 companies), middle box (tokens/trains), first-player box, spacer in `boxes/1835/`
- [x] T122 [P] Write test: hex grid derives circumradius + rows/cols layout correctly in `tests/test_spec_driven/test_hex_grid.py`
- [x] T123 [P] Write test: push block + finger hole are mutually offset (never intersect) in `tests/test_spec_driven/test_hex_grid.py`
- [x] T124 [P] Add `board_thickness` field to `Project` — reserved board space at the box bottom, not a spacer gap — in `spec_driven/project.py`
- [x] T125 [P] Exclude the board area from spacer generation by using `game_box_height - board_thickness` as the effective container height in `spec_driven/project.py`
- [x] T126 [P] Implement `_delete_stale_spacers()` — delete orphaned `spacer_*` 3MF files no longer generated — in `spec_driven/project.py` *(now delegates to `BoxExporter.delete_stale`)*
- [x] T127 [P] Write test: `board_thickness` excludes the board area from spacer generation (no spacer for reserved board space) in `tests/test_spec_driven/test_packing.py`
- [x] T128 [P] Write test: `_delete_stale_spacers()` removes orphaned spacer files when re-export produces fewer spacers in `tests/test_spec_driven/test_export.py`
- [x] T129 [P] Write test: 1835 example produces exactly one spacer (matching the original `SpacerBox`) in `tests/test_spec_driven/test_irish_gauge.py`
- [x] T130 [P] Create spec_driven render test helper — shell out to the full PythonSCAD binary and report geometry (`render_spec_driven.py` reusing `tests/render_app.py`'s `render_python`/`render_script`) in `tests/test_spec_driven/render/`
- [x] T131 [P] Create golden-image render tests for box bodies/lids (sliding, cap, hinge, no-lid, stackable, magnetic) using `compare_images` against `tests/test_spec_driven/golden/` in `tests/test_spec_driven/render/test_boxes_golden.py`
- [x] T132 [P] Create golden-image render tests for lid patterns (hex grid, voronoi, a pentagon tiling, a tessellation) in `tests/test_spec_driven/render/test_patterns_golden.py`
- [x] T133 [P] Create golden-image render tests for hex-grid compartments (push block + finger hole) in `tests/test_spec_driven/render/test_hex_grid_golden.py`
- [x] T134 [P] Create golden-image generator script that renders every golden case to `tests/test_spec_driven/golden/` in `tests/test_spec_driven/generate_golden.py`
- [x] T135 [P] Create GitHub Actions test workflow (fast pytest + pyright) in `.github/workflows/test.yml`
- [x] T136 [P] Create GitHub Actions render workflow (PythonSCAD golden-image verification) in `.github/workflows/render.yml`
- [x] T137 [P] Create GitHub Actions docs workflow (dev docs on checkin, release docs on tag) in `.github/workflows/docs.yml`

---

## Phase 12: Element Packing & Emberleaf (FR-004a / FR-004b)

**Purpose**: Individual per-piece slots inside a compartment, and the Emberleaf reference example that exercises them.

**Goal**: A compartment can hold many individually-placed silhouettes — a slot per worker meeple, per hero standee, per hex tile — each at its own offset, rotation and depth, with the pack's bounding box packing like an ordinary rectangle. `boxes/emberleaf/emberleaf.py` reproduces `examples/emberleaf.scad`.

**Independent Test**: Load the Emberleaf example and verify five separate slots exist per worker species, each with its own SVG silhouette, none overlapping the hero or breaking a wall.

### Element packing

- [x] T138 [P] Implement `CompartmentElement` with per-element shape, offset, rotation, depth and z-offset in `spec_driven/compartments/element.py`
- [x] T139 [P] Implement `ElementShape` enum (SVG, RECT, ROUNDED_RECT, CIRCLE, HEXAGON, SPHERE_SCOOP) in `spec_driven/enums.py`
- [x] T140 [P] Implement shape-aware footprints — exact rotated hexagon extent, rotation-invariant discs — in `spec_driven/compartments/element.py`
- [x] T141 [P] Implement element-pack helpers (`grid_pack`, `normalize_elements`, `elements_footprint`, `elements_overlap`) in `spec_driven/compartments/element.py`
- [x] T142 [US4] Derive a compartment's size from its element pack's bounding box (FR-004b) in `spec_driven/compartments/builder.py`
- [x] T143 [P] Implement SVG silhouette extrusion with a parse cache (`svg_solid`) in `spec_driven/compartments/element.py`
- [x] T144 [P] Write test: element footprints, packs, overlap detection and pack-derived sizing in `tests/test_spec_driven/test_elements.py`

### Carving compartments into bodies

- [x] T145 [US1] Implement `build_contents` — turn compartment placements into the solid subtracted from a body — in `spec_driven/compartments/carve.py`
- [x] T146 [US1] Hollow a box wholesale only when it has no compartments; otherwise the compartments are the cavities. `spec_driven/box/shell.py` + `Project.export`
- [x] T147 [US1] Clip compartment wells to the interior footprint so none breaks through a side wall (FR-018), while finger scoops stay unclipped because piercing a wall is their job, in `spec_driven/compartments/carve.py`
- [x] T148 [US3] Rewrite the finger scoops for correct anchoring, with an automatic wall-notch → floor-bowl fallback for shallow compartments, in `spec_driven/compartments/finger_hole.py`

### Geometry anchoring correction

- [x] T149 Extract the shared `build_shell` / `block` / `corner` placement helpers in `spec_driven/box/shell.py`, replacing the copy of `outer - inner` in all 13 box types
- [x] T150 Correct every box type for pybosl2's **centre**-anchored primitives — bodies were being cut off-centre, leaving boxes with two walls instead of four — in `spec_driven/box/types/`
- [x] T151 Rebuild the CapBox and SlipoverBox lids as real skirted caps rather than flat plates in `spec_driven/box/types/`
- [x] T152 Regenerate the golden images, which had captured the off-centre bodies, and align `generate_golden.py`'s dimensions with the test's in `tests/test_spec_driven/`

### Emberleaf reference example

- [x] T153 Rewrite `boxes/emberleaf/emberleaf.py` to derive every dimension with the same formula as `examples/emberleaf.scad`
- [x] T154 Place all 21 boxes at the positions `BoxLayout()` uses, with no overlaps and nothing overhanging the game box
- [x] T155 Give each of the five owl / rabbit / frog / rat workers its own silhouette slot at the original's pitch, plus the per-colour hero, in `boxes/emberleaf/emberleaf.py`
- [x] T156 Reproduce the marker pockets, victory-token stack, hex tiles and pull-out depressions at their individual depths in `boxes/emberleaf/emberleaf.py`
- [x] T157 Reproduce the CommonBox hex grid, trophy well and trophy marker in `boxes/emberleaf/emberleaf.py`
- [x] T158 [P] Write test: Emberleaf dimensions, layout, per-worker slots and export match the original in `tests/test_spec_driven/test_emberleaf.py`
- [x] T159 [P] Write test: BoxExporter, mesh-equivalence gating, row sizing and PathBox in `tests/test_spec_driven/test_exporter.py`
- [x] T160 Fix `should_regenerate_layout` writing its hash only on the second run, which rebuilt an already-current PDF, in `spec_driven/export/layout_pdf.py`

**Checkpoint**: Element packs functional; Emberleaf exports real 3MF files plus a layout PDF, and a re-export rewrites nothing.

---

## Phase 13: Fewest-Possible Spacers (FR-014a/b/c)

**Purpose**: The leftover space should produce as few trays as it can, and they should be liftable.

**Goal**: Spacer count depends only on the shape of the empty space, not on how many boxes the layout contains. Emberleaf gets its three spacers from the packer instead of declaring them.

**Independent Test**: Export Emberleaf and verify exactly three spacers, at the corners of the original's `SpacerPlayer`, `SpacerSide` and `SpacerFront`.

- [x] T164 Move the 3D sweep out of `Project.export` into `spec_driven/packing/spacer.py` as `sweep_free_space`
- [x] T165 Take the largest available box at each sweep step instead of scanning in index order, so a sliver cannot claim cells out of a big void and fragment it (FR-014a)
- [x] T166 Implement `merge_voids` — fuse any two voids whose union is a box, to a fixed point, in canonical order (FR-014b)
- [x] T167 Implement `apply_clearance` — inset a tray's footprint by the project's `clearance_slack` so it can be lifted out (FR-014c)
- [x] T168 Add `Project.min_spacer_height` and wire `Project.export` to `generate_spacer_placements` (sweep → merge → shrink → filter)
- [x] T169 Turn on `generate_spacers` for Emberleaf and delete its three hand-declared spacers in `boxes/emberleaf/emberleaf.py`
- [x] T170 [P] Write test: merge fuses on every axis, is idempotent, is order-independent, and leaves an L-shape at two (SC-010b) in `tests/test_spec_driven/test_spacer_merge.py`
- [x] T171 [P] Write test: swept voids never overlap each other or a placed box, and a sliver does not fragment its neighbour (FR-014a) in `tests/test_spec_driven/test_spacer_merge.py`
- [x] T172 [P] Write test: Emberleaf produces exactly three spacers at the original's corners (SC-010a) in `tests/test_spec_driven/test_emberleaf.py`

**Checkpoint**: Emberleaf's spacers are derived, not declared — three trays, down from the four the un-merged sweep produced. 1835 still produces exactly one.

### Rectilinear merge — L/T/U leftovers as one polygon tray (FR-014d/e)

- [x] T174 Add `spec_driven/paths.py` — rectilinear polygon helpers (`polygon_area`, `is_rectilinear`, `inset_rectilinear`, `bounds`) shared by the spacer pass and `PathBox`
- [x] T175 Implement `union_outline` — trace the boundary of a union of footprints by edge cancellation, collapsing collinear runs, in `spec_driven/packing/spacer.py`
- [x] T176 Implement `merge_rectilinear` — group coplanar voids into connected clusters and emit one polygon-footprint `Void` per cluster (FR-014d)
- [x] T177 Refuse to fuse voids at different heights, which would replace two flat trays with one overhanging part (FR-014e)
- [x] T178 Add `Placement.path` and build polygon spacers through `BoxType.PATH` in `Project.export`
- [x] T179 Replace `PathBox._inset_path`'s centroid scale with the exact rectilinear inset, which a centroid scale gets wrong on any reflex corner
- [x] T180 [P] Write test: L/T/U/plus outlines trace correctly, polygon area is preserved, stacked voids stay apart, and an inset L stays rectilinear on all six sides in `tests/test_spec_driven/test_spacer_merge.py`

**Checkpoint**: A corner box in an otherwise empty layer yields one six-point L tray instead of two rectangles, and it builds as a real hollow `PathBox`.

### Packing correctness — found while evaluating auto-packing for Emberleaf

- [x] T181 Fix `expandable=False` not disabling expansion. `Project.export` OR'd the master switch with `expandable_width`/`expandable_length`, which default to `True`, so every box was expandable and boxes declared fixed were silently stretched — Earth Animal Kingdom's `CanopyBox` was being grown 46 → 47mm and `SproutBox` 20.4 → 21.4mm against their declared sizes.
- [x] T182 Wire the per-axis expansion flags through to the solver: `expandable` alone gives the sub-3mm height absorb (FR-012), `expandable_width` adds the fill-to-fit width growth, in `spec_driven/packing/layout.py`.
- [x] T183 Stop the packer from using the board's space. `Project.export` passed the full `game_box_size[2]` as the container height while the spacer pass used `height - board_thickness`, so auto-placed boxes could climb into the region reserved for the game board (FR-012, board-on-top).
- [x] T184 Raise `PackingError` instead of returning an empty packing. A solver failure was swallowed, so `export()` reported success having written no boxes at all. The message now names boxes taller than the container, or reports the fill ratio.
- [x] T185 [P] Write test: expansion respects the master switch, packing failures raise and explain themselves, in `tests/test_spec_driven/test_packing.py` and `test_project_coverage.py`

**Checkpoint**: Declared-fixed boxes keep their size, nothing intrudes on the board space, and a layout that cannot be packed says so.

### Auto-packing Emberleaf — evaluated, not adopted

Emberleaf's 18 boxes fill **77%** of the usable volume (3296 cm³ of 4264 cm³ in 285 × 285 × 52.5mm). The original `.scad` layout achieves this because the box sizes were designed to tile exactly in three columns — 98 + 98 + 90 = 286 across, 142.5 × 2 = 285 deep, 13.125 × 4 = 52.5 tall.

The extreme-point First-Fit-Decreasing solver cannot find that arrangement. Measured: five sort strategies (footprint area, height, volume, height-then-volume, max dimension) all fail; twelve variants crossing those with three extreme-point orderings, best-fit selection and corner extreme-point generation all fail; 266,000 random permutations of the plain solver and 60,000 of the strongest variant produce no successful packing. The failure is in the placement rule, not the ordering — greedy extreme-point placement fragments the space rather than aligning columns.

Emberleaf therefore keeps explicit positions. Note this is not a statement that a better solver could not do it — a layout demonstrably exists.

- [ ] T186 Declarative column/stack layout — let a project express "these boxes form a column at this x, stacked in this order" and have the library compute the coordinates. This is the missing middle ground between hand-typed positions and free-form packing: it keeps the structure that makes a 77%-fill layout possible while removing the hand-typed numbers, and would let Emberleaf, 1835 and Irish Gauge drop their explicit positions.
- [ ] T187 Stronger 3D packing for high-fill layouts (guillotine/skyline with column alignment, or a proper exact solver on the axis-aligned tiling sub-problem), so free-form auto-packing can handle inserts above roughly 70% fill.

---

## Phase 14: Earth Animal Kingdom fidelity, and lid decoration

### Earth Animal Kingdom — matched to the original

The port had drifted from `examples/earth_animal_kingdom.scad` on nearly every dimension.

- [x] T188 Derive every dimension with the original's formula. Corrected: card box height 25.6 → **23.6** (36 cards at 0.6mm + 2), sprout box (76, 156, 20.4) → **(76, 158, 22.4)**, animal boxes (174, 156, 12.1) → **(174, 158, 12.5)**.
- [x] T189 Correct the animal box type: `MakeBoxWithSlipoverLid` is `BoxType.SLIPOVER`, not `FILAMENT_HINGE`, with its own 1.5mm wall and a 4mm foot.
- [x] T190 Add `foot` and `slip` to `SlipoverBoxBuilder` and build a sleeve that stops at the foot in `spec_driven/box/types/slipover.py`.
- [x] T191 Replace the invented `Boards` box with the original's `SpacerBox` (174 × 158 × 21).
- [x] T192 Position all six boxes to match `BoxLayout()`, which the port had left to the packer.
- [x] T193 Reproduce the precomputed animal partition from `lib/animal_kingdom_items_layout.scad` verbatim — 26 slots in AnimalBox1, 30 in AnimalBox2, 56 in total across 37 species — replacing the `share_compartments` solver, which produced a different split.
- [x] T194 Add the access pan each animal box carries over its slots (`RoundedBoxAllSides` at half the token thickness).
- [x] T195 [P] Write test: dimensions, box types, layout positions, and that every slot fits its interior with no two overlapping, in `tests/test_spec_driven/test_earth_animal_kingdom.py`

### Lid decoration (T161)

- [x] T196 Implement `spec_driven/lid/decorate.py` — apply a `LidBuilder`'s pattern and label to any box type's lid, deriving the decoratable face from the lid's own bounding box so no type has to declare one.
- [x] T197 Wire decoration into `Project.export` per colour mode: mmu keeps the label as separate coloured inserts, single engraves it into the lid.
- [x] T198 Fix `build_label` never extruding its text (`pybosl2.text` returns a 2-D shape) and mis-anchoring its frame and hatching.
- [x] T199 Size label text by measurement instead of by character count. The old estimate put **102mm of text on a 100mm lid**; text is now set at a nominal size, measured, and scaled to the label area.
- [x] T200 Shrink a framed label's backing plate to hug its text, so a lid can carry both a frame and a through-hole pattern — a plate the size of the label area covered the pattern entirely.
- [x] T201 Fix the pattern leaving a skin: it was placed by assumption rather than by its bounding box, so the holes stopped 0.7mm short of the top face and nothing showed. Also trimmed to the label area so it cannot eat the border.
- [x] T202 Degrade a framed label to engraved text in single-colour mode. A frame is a colour feature, and keeping it lifted the text 0.4mm clear of the face so the engraving cut nothing at all.
- [x] T203 [P] Write test: label sizing stays inside the margin, mmu yields separate inserts, single engraves, patterns cut through, and a decorated lid differs between the two modes, in `tests/test_spec_driven/test_lid_decorate.py`

**Checkpoint**: Lids carry their labels and patterns. A plain sliding lid goes from 8 vertices to 1631 with a framed label and hex pattern; the single-colour variant is engraved instead of raised.

### Known gaps
- [ ] T162 `InsetBox`, `SlidingCatchBox`, `CapPathBox`, `SlipoverPathBox`, `CardLibraryBox` and `FilamentHingeBox` still return a plain plate from `build_lid`; only sliding, cap and slipover produce their real mating geometry.
- [ ] T163 `HingeBox` knuckles are a placeholder — no matching lid knuckles and no pin channel, so the hinge does not yet articulate.
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

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All geometry uses pybosl2 only — no native pythonscad imports
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
