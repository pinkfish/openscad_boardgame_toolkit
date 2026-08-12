# Comprehensive Requirements Quality Checklist: Board Game Box Library

**Purpose**: Validate completeness, clarity, consistency, and measurability of all 34 functional requirements across 10 user stories before implementation.

**Created**: 2026-08-11

**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md) | [tasks.md](../tasks.md)

---

## Requirement Completeness

- [x] CHK001 Are acceptance criteria specified for all 10 user stories? [Completeness, Spec §User Scenarios]
- [x] CHK002 Are all 34 functional requirements (FR-001–FR-034) traceable to at least one user story? [Completeness] — **FIXED: FR-028 marked [DEFERRED], deferred to future release**
- [x] CHK003 Are output file naming conventions fully specified for multi-color, single-color, body, lid, and spacer variants? [Completeness, Spec §FR-029–FR-030]
- [x] CHK004 Are requirements defined for what happens when a box has compartments but no explicitly set `size` — is the auto-compute flow documented end-to-end? [Completeness, Spec §FR-012]
- [x] CHK005 Are material/color requirements specified for all decorative elements (text, frame, pattern, pattern elements)? [Completeness, Spec §FR-022, FR-024]
- [x] CHK006 Are packing order and hidden-box transparency visualization requirements for the PDF layout explicitly documented? [Completeness, Spec §FR-033] — **FIXED: solid shaded isometric (30° above, 45° rotated), semi-transparent walls for hidden boxes**

## Requirement Clarity

- [x] CHK007 Is "auto-sizing" defined with precise mathematical behavior — how row widths are computed, how expansion distributes space, and when absorption occurs? [Clarity, Spec §FR-012–FR-016]
- [x] CHK008 Is the gap threshold behavior unambiguous — what happens when a gap is exactly 10mm? What about 15mm spacer minimum vs 10mm absorption? [Clarity, Spec §FR-014–FR-015] — **FIXED: ≥ 10mm generates spacer, < 10mm absorbed, exactly 10mm → spacer**
- [x] CHK009 Is the Hausdorff distance tolerance value (0.001mm) justified with a rationale for why this specific threshold absorbs FP jitter without suppressing real changes? [Clarity, Spec §FR-031, Assumptions]
- [x] CHK010 Is the "3D angle view" for the packing layout PDF specified with enough detail — camera angle, whether boxes are rendered as wireframe or solid, label placement? [Clarity, Spec §FR-033] — **FIXED: isometric 30°/45°, solid shaded, semi-transparent walls**
- [x] CHK011 Are the three label layout modes (framed, frameless, diagonal) defined with sufficient precision — frame border thickness, hatching line spacing, corner-to-corner angle calculation? [Clarity, Spec §FR-021]
- [x] CHK012 Is "through-hole" pattern behavior specified when holes would intersect lid edges — are partial holes at edges clipped or omitted? [Clarity, Spec §FR-023] — **FIXED: truncated at lid boundaries (same as label clipping)**

## Requirement Consistency

- [x] CHK013 Do the FR-012 (minimum dimensions from compartments) and FR-017 (expandable axes) requirements align — can a box with auto-computed size also declare non-expandable axes? [Consistency, Spec §FR-012, FR-017]
- [x] CHK014 Are the spec's "BoxKit" entity and plan's "Project" entity description consistent after the terminology normalization? [Consistency, Spec §Key Entities, Plan §Summary]
- [x] CHK015 Do the PDF caching requirements (FR-034, SC-018) use the same SHA-256 hash mechanism as the 3MF caching (FR-031, SC-012) or are they independent? [Consistency, Spec §FR-031, FR-034]
- [x] CHK016 Are finger cutout requirements (FR-006, US3) consistent with compartment builder fields (finger_scoop, scoop_side) — do all four sides have equivalent specification? [Consistency, Spec §FR-006, Data Model §CompartmentBuilder] — **FIXED: `finger_holes` field added to BoxBuilder base**
- [x] CHK017 Do the row alignment requirements (FR-013, FR-016) remain consistent when boxes have different expandable axis settings — what defines a "row" when some boxes can't expand in one dimension? [Consistency, Spec §FR-013, FR-016, FR-017]

## Acceptance Criteria Quality

- [x] CHK018 Can SC-001 ("under 10 lines of builder API code") be objectively measured — what counts as a "line" and are comments/imports included? [Measurability, Spec §SC-001]
- [x] CHK019 Can SC-003 ("lid and body can be assembled without modification") be objectively verified without a physical print? [Measurability, Spec §SC-003] — **FIXED: verified via render tests checking mating geometry dimensions; physical print deferred to user**
- [x] CHK020 Can SC-008 ("every box in a row shares the same length") be measured programmatically from the packed layout output? [Measurability, Spec §SC-008]
- [x] CHK021 Can SC-016 ("exactly the expected material assignments") be verified — is the expected assignment explicitly listed in the spec? [Measurability, Spec §SC-016]
- [x] CHK022 Are SC-017 and SC-018 (PDF output and cache skip) measurable without opening the PDF file — is file existence and modification timestamp sufficient? [Measurability, Spec §SC-017–SC-018]

## Scenario Coverage

- [x] CHK023 Are requirements defined for the "empty Project" case — no sub-boxes, no compartments? [Coverage, Spec §Edge Cases] — **FIXED: empty Project produces no files, empty ExportResult, no PDF**
- [x] CHK024 Are requirements defined for a Project with boxes but no compartments — how is size computed when no compartments drive the minimum? [Coverage, Gap] — **FIXED: ValueError raised — either compartments or explicit size required**
- [x] CHK025 Are requirements defined for spacer trays when ALL gaps are under 10mm — does the system produce zero spacer files correctly? [Coverage, Spec §SC-010]
- [x] CHK026 Are requirements defined for the case where two sub-boxes have the same label — is duplicate detection at `project.box()` time sufficient? [Coverage, Gap]
- [x] CHK027 Are requirements specified for lid decoration on box types that have no lid (NoLidBox) — is the `LidBuilder` silently ignored or rejected? [Coverage, Spec §Edge Cases] — **FIXED: warning emitted, lid decoration silently dropped**
- [x] CHK028 Are requirements defined for the interaction between through-hole patterns and framed labels — what happens when the pattern intersects the frame border? [Coverage, Spec §Edge Cases]

## Edge Case Coverage

- [x] CHK029 Is the behavior specified when a spacer tray's height would be negative (impossible) due to a computation error? [Edge Case, Gap] — **FIXED: ValueError raised during spacer generation**
- [x] CHK030 Is the behavior specified when the Hausdorff comparison file is corrupted or unreadable — does it silently overwrite or raise an error? [Edge Case, Spec §FR-031] — **FIXED: silent overwrite (treated as cache miss)**
- [x] CHK031 Is the behavior specified when the layout cache file (.layout_cache.json) is corrupted or contains stale hash entries? [Edge Case, Gap] — **FIXED: silent overwrite (treated as cache miss)**
- [x] CHK032 Is the behavior specified when compartment depth exceeds the auto-computed box height — does it error before or during export? [Edge Case, Spec §FR-007]
- [x] CHK033 Is the behavior specified for polygon-path boxes (FR-018) when a compartment extends beyond the polygon boundary — is it clipped or rejected? [Edge Case, Spec §FR-018]
- [x] CHK034 Is the behavior specified when the minimum text height threshold (4mm) is changed to 0mm — does it print all labels regardless of size or reject the configuration? [Edge Case, Spec §FR-020] — **FIXED: threshold=0 disables guard, all labels print**

## Non-Functional Requirements

- [x] CHK035 Are performance requirements (SC-002, SC-008) tied to a specific hardware baseline — what CPU/memory is assumed for "under 1 second"? [Non-Functional, Spec §SC-002] — **FIXED: Apple Silicon or equivalent x86-64 specified**
- [x] CHK036 Are performance goals for uncached (first-run) bin packing specified — the plan states "may take longer" but "longer" is unquantified? [Non-Functional, Plan §Performance Goals] — **FIXED: 30s–5min depending on box count, no upper bound guaranteed**
- [x] CHK037 Are memory constraints specified for caching — how large can .layout_cache.json grow before it impacts performance? [Non-Functional, Gap] — **FIXED: < 1MB for typical projects (< 50 boxes)**
- [x] CHK038 Are printability requirements (minimum wall thickness, overhang angles, bridging distances) specified or deferred to the slicer? [Non-Functional, Spec §Assumptions]
- [x] CHK039 Are requirements specified for what happens when pybosl2 or pymeshlab dependencies are missing at import time — does the system produce a clear install message? [Non-Functional, Gap] — **FIXED: clear error naming missing package and minimum version**

## Dependencies & Assumptions

- [x] CHK040 Are all assumptions in the spec's Assumptions section validated against actual constraints — e.g., is "FDM 3D printing with 0.4mm nozzle" a hard constraint or a guideline? [Assumptions, Spec §Assumptions]
- [x] CHK041 Is the assumption that "users have basic familiarity with 3D modeling concepts" sufficient — do error messages provide enough context for a non-expert? [Assumptions, Spec §Assumptions]
- [x] CHK042 Is the dependency on pymeshlab (Hausdorff comparison) documented with a minimum version requirement? [Dependencies, Gap] — **FIXED: pymeshlab ≥ 0.2.0 pinned**
- [x] CHK043 Are the borrowed tessellation algorithms (penrose, pentagon, voronoi) documented with version/compatibility notes — what happens if the source files are refactored? [Dependencies, Plan §Borrowed vs Fresh] — **FIXED: assumed stable; pattern functions updated if refactored**
- [x] CHK044 Is the assumption that "boxes are right-rectangular by default" consistent with FR-018 (polygon-path support) — is polygon-path a first-class feature or secondary? [Assumptions, Spec §FR-018, Assumptions]

## Ambiguities & Conflicts

- [x] CHK045 Is the term "shelf-based 2D bin packing" (Assumptions) distinct from "3D box packing" (Research §4) — do these use the same algorithm family with different dimensionality? [Ambiguity, Spec §Assumptions, Research §4]
- [x] CHK046 Does the plan's "fresh design" for nested box packing conflict with the research decision to use "same SHA-256 approach, new cache file" — is the cache file format novel or derivative? [Conflict, Plan §Borrowed vs Fresh, Research §7]
- [x] CHK047 Is the `final_size` attribute on BoxBuilder (data-model) fully defined — is it set before export, after packing, and is it read-only after being set? [Ambiguity, Data Model §BoxBuilder] — **FIXED: set-once frozen after export resolves it**
- [x] CHK048 Are there conflicting requirements around color defaults — FR-022 says "each defaults to a distinct color" while Assumptions say specific defaults (white for text, contrasting hue for frame)? [Ambiguity, Spec §FR-022, Assumptions]
- [x] CHK049 Does FR-024 (patterns with multiple colors) conflict with FR-023 (through-hole patterns) — are multi-colored through-holes physically printable as separate material assignments? [Conflict, Spec §FR-023, FR-024]
- [x] CHK050 Is the "corner-to-corner diagonal text at natural angle" requirement implementable for all aspect ratios — what angle is "natural" for a 100x20mm lid? [Ambiguity, Spec §FR-021]
