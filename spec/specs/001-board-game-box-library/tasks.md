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
- [x] T003 [P] Implement `Color` dataclass with named presets in `spec_driven/color.py`
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
- [x] T022 [US1] Implement compartment auto-layout (2D shelf-based, no row alignment yet) in `spec_driven/compartments/layout.py`
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
- [x] T028 [P] [US2] Implement remaining box type builders (cap_path, no_lid, path, card_library) in `spec_driven/builders/`
- [x] T029 [P] [US2] Implement box types: CapBox, HingeBox, FilamentHingeBox in `spec_driven/box/types/`
- [x] T030 [P] [US2] Implement box types: MagneticBox, InsetBox, SlidingCatchBox in `spec_driven/box/types/`
- [x] T031 [P] [US2] Implement box types: SlipoverBox, SlipoverPathBox, CapPathBox in `spec_driven/box/types/`
- [x] T032 [P] [US2] Implement box types: NoLidBox, PathBox, CardLibraryBox in `spec_driven/box/types/`
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
- [x] T052a [US4] Implement compartment row-width distribution (size compartments to fill row width) in `spec_driven/compartments/sizing.py`
- [x] T053 [US4] Implement compartment grouping (grouped items packed together) in `spec_driven/compartments/layout.py`
- [x] T054 [US4] Implement overflow detection with descriptive error messages in `spec_driven/compartments/layout.py`
- [x] T054a [US4] Implement compartment clipping to non-rectangular polygon interior regions (FR-018) in `spec_driven/compartments/layout.py`

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
- [x] T068a [US8] Implement MMU color-copy logic (positive inserts in different material/color from body) in `spec_driven/export/exporter.py`
- [x] T068b [US8] Implement bounding-box reporting for each exported piece (FR-027) in `spec_driven/export/exporter.py`
- [x] T069 [P] [US8] Implement two-level layout cache (in-memory dict + disk `spec_driven/.layout_cache.json`, SHA-256 key, version invalidation) to store 3D box packing layouts and bypass solver on subsequent runs in `spec_driven/packing/cache.py`
- [x] T070 [US8] Implement `BoxExporter` with per-box/per-spacer 3MF file writing in `spec_driven/export/exporter.py`
- [x] T071 [US8] Implement Hausdorff conditional write (pymeshlab compare, skip if distance < 0.001mm) in `spec_driven/export/hausdorff.py`
- [x] T072 [US8] Implement organized output directory structure (`mmu/` + `single/`, `_body.3mf` / `_lid.3mf` naming) in `spec_driven/export/exporter.py`
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

**Goal**: `project.export()` produces a `layout.pdf` in the output directory. The PDF shows a 3D-angle view of the game box interior with sub-boxes labeled at packed positions, numbered in packing order, and hidden boxes visible through transparency. PDF is cached: only regenerated when layout or library version changes.

**Independent Test**: Export a 4-box game, verify `layout.pdf` exists showing 4 labeled boxes at correct positions.

### Tests for User Story 10

- [x] T078a [P] [US10] Write unit test: PDF file exists in output directory after export in `tests/test_spec_driven/test_export.py`
- [x] T078b [P] [US10] Write unit test: PDF skipped on re-export when layout unchanged in `tests/test_spec_driven/test_export.py`

### Implementation for User Story 10

- [x] T078c [US10] Implement 3D angle view packing layout renderer (box outlines, labels, dimensions, spacer markers) in `spec_driven/export/layout_pdf.py`
- [x] T078d [US10] Implement packing order numbering and hidden-box transparency visualization in `spec_driven/export/layout_pdf.py`
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
