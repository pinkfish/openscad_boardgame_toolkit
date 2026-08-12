# Feature Specification: Board Game Box Library

**Feature Branch**: `001-board-game-box-library`

**Created**: 2026-08-11

**Status**: Draft

**Input**: User description: "Build a library that will help create boxes with special emphasis on board game boxes. Handle multiple different types of boxes, from hinged boxes to sliding lid boxes. Allow the indents inside the box to be laid out either automatically or at specific locations. Make sure the pieces have finger cut outs and other elements to make it easy to remove the pieces from the boxes and setup a 3d box shape making sure all of the sub boxes can fit inside the overall game box."

## Clarifications

### Session 2026-08-11

- Q: How is unused space distributed among expandable sub-boxes? → A: Fill-to-fit: boxes expand only to fill the row/column they share, aligning and matching sizes of other boxes in the same row/column. Leftover space goes to spacer boxes unless the gap is below the auto-fill threshold (default 10mm), in which case the adjacent box absorbs it.
- Q: What is the gap-to-expand threshold? → A: 10mm default; gaps smaller than this are absorbed by the adjacent expandable box instead of creating a spacer.
- Q: Spacer boxes: solid blocks or hollow trays? → A: Hollow trays (walls + floor matching the gap's footprint and height), constructed like any regular box for material efficiency.
- Q: Do boxes expand in both dimensions or one axis only? → A: Both dimensions expand. Boxes in the same row share a common length so every box in one row has the same length, making them easier to place and remove.
- Q: How are row widths determined when sub-boxes occupy multiple rows? → A: Variable width per row, sized to fit the widest box in that row -- rows are not forced to equal widths.
- Q: Multi-color 3MF: one file per box or per material? → A: One 3MF per box body and one per lid (separate files), each containing all colors/materials in a single 3MF.
- Q: Where do spacer trays go in 3MF exports? → A: Each spacer tray gets its own independent 3MF file.
- Q: How is "model differs" determined for content-based caching? → A: 3D-Hausdorff-Distance-Calculator comparing exported mesh geometry -- file is only rewritten if the geometric distance exceeds a tolerance.
- Q: Single-color vs multi-color export: toggle or always both? → A: Always generate both a multi-color 3MF and a single-color 3MF for every box body and every lid.
- Q: How do the three label layout modes (framed, frameless, diagonal) differ? → A: Diagonal is a text orientation (corner-to-corner of the lid, 45° only for square boxes), available in both framed and frameless modes. Framed mode adds a rectangular frame with diagonal hatching/webbing behind the text for bed adhesion plus a small outer border.
- Q: Lid pattern "spaces" for filament saving: holes, recesses, or lattice? → A: Through-holes cut completely through the lid at pattern lines -- maximum filament savings.
- Q: How many accent colors for lid decorations? → A: Three independently settable colors: one for label text, one for the frame (top layer), one for the pattern top layer. Patterns support multiple colors.
- Q: How does label auto-sizing determine dimensions? → A: Label fills available lid area minus a configurable border margin. If the computed text size is below a minimum (default 4mm, settable), the label is skipped entirely rather than printed illegibly.
- Q: How are box minimum dimensions computed from compartments? → A: `size` is auto-computed from compartment dimensions if not explicitly set. If `size` IS set, it is used as-is and compartments must fit within. Box expansion happens during the Project packing phase where sub-boxes are fitted into the main game box.
- Q: Should the packing layout PDF show a 2D top-down or 3D angle view? → A: 3D angle view with packing steps, showing how interior hidden boxes stack into the game box. Visualizes the packing order and interior box arrangement.
- Q: Is the PDF generated automatically or on-demand? → A: Automatic with every `project.export()`, but cached — only regenerates if the box layout or library version has changed since the last export.

## User Scenarios & Testing

### User Story 1 - Create a Basic Box with Interior Compartments (Priority: P1)

A board game designer wants to create a box to store game pieces. They specify the outer dimensions, wall thickness, and describe what compartments they need (e.g., "one large well for cards, two small wells for tokens"). The library generates a 3D-printable box with compartments laid out to fit the interior.

**Why this priority**: This is the core value proposition -- turning a description of storage needs into a printable box. Without compartments, there is no board game storage solution.

**Independent Test**: Can be fully tested by creating a box with 3 compartments of specified sizes, verifying they all fit within the box interior without overlapping, and exporting a printable 3D model.

**Acceptance Scenarios**:

1. **Given** a box outer size of 200x150x60mm and 3 compartments of specified dimensions, **When** the user generates the box, **Then** all compartments are placed within the interior, each separated by walls of the specified thickness, and no compartment overlaps another or breaches the box walls.
2. **Given** a box with compartments that exceed the available interior space, **When** the layout is computed, **Then** the library reports a clear error explaining which compartment or group cannot fit.
3. **Given** compartments with different depths (e.g., a shallow well for tokens and a deep well for cards), **When** the box is generated, **Then** each compartment carves to its specified depth and shared walls respect the deeper cavity.

---

### User Story 2 - Choose Among Different Box Lid Types (Priority: P1)

The designer needs different lid mechanisms for different use cases: a sliding lid for a box that sits on a shelf, a hinged lid for a box that opens like a book, a cap lid (friction-fit) for quick access, and a magnetic lid for premium feel. They select the box type and the library generates the correct geometry.

**Why this priority**: Lid type is the primary structural decision for a box. Without it, closures are not functional. Equal priority with compartments because both are needed for a complete usable box.

**Independent Test**: Each box type can be tested independently by generating a box and its matching lid, verifying the lid fits the box body, opens and closes as intended, and does not collide with interior contents.

**Acceptance Scenarios**:

1. **Given** the user selects a sliding lid box type with dimensions 100x80x40mm, **When** the box and lid are generated, **Then** the lid slides into dovetail grooves in the box walls and can be removed by sliding.
2. **Given** the user selects a hinged lid box type, **When** the box and lid are generated, **Then** the lid pivots on an integrated hinge at the back, opens to at least 180 degrees, and stays attached.
3. **Given** the user selects a cap lid box type, **When** the box and lid are generated, **Then** the lid fits over the box walls with a friction-fit tolerance and can be removed by lifting.
4. **Given** the user selects a magnetic lid box type, **When** the box and lid are generated, **Then** cavities for magnets are placed in the lid and box walls at matching positions.
5. **Given** a sliding lid box, **When** compartments are also specified, **Then** the compartments do not interfere with the lid's sliding track.

---

### User Story 3 - Finger Cutouts for Easy Piece Removal (Priority: P2)

The designer wants pieces inside each compartment to be easy to remove. They specify finger cutouts -- either scooped into the compartment wall/floor or placed on the box side walls. The library places these cutouts at the specified locations relative to each compartment or box side.

**Why this priority**: Finger cutouts are essential for usability but the box is functional without them (pieces can be tipped out). Depends on compartments/box being generated first.

**Independent Test**: Can be tested by generating a compartment with a finger scoop, measuring the cutout dimensions, and verifying it provides sufficient finger clearance (a sphere of 14mm radius can intersect the scoop).

**Acceptance Scenarios**:

1. **Given** a compartment with a finger scoop specified on its front wall, **When** the box is generated, **Then** a rounded cutout appears at the top of that compartment wall, sized to admit a fingertip.
2. **Given** finger holes specified on the box exterior (e.g., left and right sides), **When** the box is generated, **Then** semicircular cutouts appear in the specified walls at half the box height.
3. **Given** a shallow compartment (under 8mm deep), **When** a finger cutout is requested, **Then** the library automatically uses a wall-notch cutout instead of a floor scoop, since a floor scoop would breach the floor.

---

### User Story 4 - Automatic Compartment Layout (Priority: P2)

The designer provides a list of compartments with sizes but no positions. The library automatically arranges them to fill the box interior, respecting padding between compartments, grouping related compartments together, and maximizing space utilization.

**Why this priority**: Manual layout is tedious for many compartments. Automation saves significant design time. Can be tested independently of lid types.

**Independent Test**: Give the library 10 compartments of varying sizes and verify all are placed within the interior without overlaps, with consistent wall spacing, and the layout is deterministic.

**Acceptance Scenarios**:

1. **Given** 5 compartments with specified sizes and no positions, **When** the box is generated with automatic layout, **Then** all 5 compartments are arranged in rows within the interior, separated by walls of the correct thickness, and no manual coordinates were required.
2. **Given** compartments marked as a group (e.g., "card slot + token well must stay together"), **When** automatic layout runs, **Then** grouped compartments are placed adjacent to each other before other compartments fill remaining space.
3. **Given** compartments totaling more interior area than the box provides, **When** automatic layout runs, **Then** the library reports which compartment group overflows and by how much.

---

### User Story 5 - Nested Boxes: Sub-Boxes Inside a Game Box (Priority: P3)

The designer wants multiple sub-boxes (tuck boxes, card boxes) to nest inside a larger game box. They specify the outer game box dimensions and a list of sub-box specifications. The library computes whether the sub-boxes fit inside the outer box and generates all the pieces.

**Why this priority**: This is an advanced orchestration feature. A designer can manually check fit and place sub-boxes, but automation makes it practical for complex inserts.

**Independent Test**: Define an outer box and 4 sub-boxes of known dimensions; verify the generated sub-boxes all fit within the outer box interior without overlapping each other or the walls.

**Acceptance Scenarios**:

1. **Given** an outer box of 300x300x80mm and 4 sub-box specs (two card boxes 100x70x70mm, two token boxes 80x80x30mm), **When** nesting is computed, **Then** all 4 sub-boxes are arranged within the outer interior, and all can be lifted out by their finger cutouts.
2. **Given** sub-boxes that cannot all fit in the outer box, **When** nesting is computed, **Then** the library reports which sub-boxes cannot fit and by how much area or height they exceed the available space.
3. **Given** sub-boxes that must stand upright (height constraint), **When** nested layout is computed, **Then** all sub-boxes are placed with their openings facing upward, never on their sides.

---

### User Story 7 - Auto-Size Sub-Boxes and Fill Gaps with Spacers (Priority: P2)

The designer specifies multiple sub-boxes to go inside a game box, each with minimum dimensions. The library automatically expands boxes to fill their rows, aligns box lengths within each row, and fills any remaining empty space with hollow spacer trays. If a gap is smaller than 10mm, the adjacent box absorbs it rather than creating a tiny spacer.

**Why this priority**: Auto-sizing eliminates manual trial-and-error fitting of sub-boxes into a game box. Combined with the row-alignment behavior, it produces a clean, modular insert that is easy to load and unload. Depends on the nesting framework (FR-010).

**Independent Test**: Define an outer box of 300x200x80mm and 4 sub-boxes with minimum sizes; verify all boxes are expanded to fill their rows, boxes in each row share the same length, and any leftover gaps under 10mm are absorbed. Verify that gaps larger than 10mm produce spacer trays.

**Acceptance Scenarios**:

1. **Given** an outer box 300x200x80mm with 3 sub-boxes (min 90x80mm) that fit in one row, **When** auto-sizing runs, **Then** each box expands to fill the row width, all share the same length, and no spacer boxes are generated because the row is fully filled.
2. **Given** sub-boxes arranged in two rows where the second row leaves a 25mm-wide gap after expansion, **When** auto-sizing runs, **Then** a hollow spacer tray of 25mm width and matching height is generated to fill the gap.
3. **Given** a 7mm leftover gap in a row (below the 10mm threshold), **When** auto-sizing runs, **Then** the gap is absorbed by the nearest expandable box in that row rather than generating a spacer tray.
4. **Given** a spacer tray that would be less than 15mm in width or length, **When** auto-sizing checks the spacer, **Then** the space is instead absorbed by adjacent boxes since spacers cannot be smaller than 15mm in width or length.
5. **Given** sub-boxes of varying heights within a row, **When** the row's common length is computed, **Then** the height of shorter boxes does not affect the row length -- only the 2D footprint matters for alignment.

---

### User Story 8 - Export 3MF Files with Content-Based Caching (Priority: P2)

The designer generates a complete board game insert and needs printable 3MF files for their slicer. The library exports each box body and each lid as separate 3MF files -- both multi-color (with per-material assignments for MMU printers) and single-color (for single-extruder printers). For game boxes with nested sub-boxes, all sub-boxes and spacers are also exported. Unchanged files are not rewritten to disk -- only models whose geometry actually changed are updated, using a 3D Hausdorff distance comparison.

**Why this priority**: 3MF is the standard slicer interchange format for multi-material prints. Without export, the library only exists in-memory. Content-based caching prevents unnecessary file churn when iterating on unrelated parts of a layout.

**Independent Test**: Generate a BoxKit with 2 sub-boxes, export all files, modify only one sub-box, and verify that only the changed box's 3MF files are rewritten while unchanged files keep their original timestamps.

**Acceptance Scenarios**:

1. **Given** a single box with MMU inserts (different colored compartments), **When** exported, **Then** two 3MF files are produced: `<label>_body.3mf` and `<label>_lid.3mf`, each containing all materials/colors embedded in a single file. Additionally, single-color variants `<label>_body_single.3mf` and `<label>_lid_single.3mf` are produced.
2. **Given** a BoxKit with 3 sub-boxes and 2 spacer trays, **When** exported, **Then** the outer box produces body+lid 3MF files, each sub-box produces body+lid 3MF files, and each spacer tray produces its own 3MF file -- all in both multi-color and single-color variants.
3. **Given** a previously exported box whose geometry has not changed, **When** re-exported, **Then** the 3MF file on disk is NOT overwritten -- the Hausdorff distance between old and new mesh is below the tolerance threshold.
4. **Given** a box whose compartment layout changed (different sizes), **When** re-exported, **Then** the 3MF file IS rewritten because the Hausdorff distance exceeds the tolerance.

---

### User Story 9 - Decorate Lids with Labels, Patterns, and Print-Optimized Color Layers (Priority: P2)

The designer wants each box lid to look polished and be easy to print. They set a label text that auto-sizes to fill the lid face. The label can be framed (with a rectangular border, diagonal hatching behind the text for bed adhesion, and a color-accented top layer) or frameless (just the text). Text can be oriented corner-to-corner across the lid. A surface pattern (hex grid, grid, Voronoi, or tessellation) cuts through the lid as decorative through-holes, saving filament. Three independently settable accent colors control the label text, the frame top layer, and the pattern top layer. If the computed text height falls below a configurable minimum (default 4mm), the label is skipped.

**Why this priority**: Lids are the most visible part of a board game insert. Decoration makes the output presentable. The color-layer architecture and minimum-text-size guard prevent print failures and wasted filament. Depends on lid geometry generation (P1).

**Independent Test**: Create a box with lid text "Animals", a hex-grid lid pattern with through-holes, a framed label with diagonal hatching, and verify the 3MF contains exactly the expected color assignments and the text auto-sizes to fill the lid.

**Acceptance Scenarios**:

1. **Given** a lid of 100x70mm with label text "Cards", **When** the lid is generated with auto-sizing, **Then** the text is scaled to fill the lid area minus a 5mm border margin, and the computed text height is ≥ 4mm.
2. **Given** a lid of 40x30mm with label text "Tokens", **When** the auto-sized text height computes to 3mm (below the 4mm minimum), **Then** the label is skipped and the lid prints as a plain decorated lid with no text.
3. **Given** a framed label with accent frame color set to gold and label text color set to white, **When** the lid is exported as multi-color 3MF, **Then** the frame top layer is assigned the gold material and the text is assigned the white material.
4. **Given** a lid with a hex-grid pattern, **When** the lid is generated, **Then** hexagonal through-holes are cut through the lid surface following the pattern grid, saving filament in the open areas.
5. **Given** a lid with corner-to-corner diagonal text orientation on a non-square lid, **When** the text is placed, **Then** the text runs from one corner of the lid to the opposite corner at the natural angle (not forced to 45°).
6. **Given** a framed diagonal label, **When** the lid is generated, **Then** diagonal hatching lines fill the rectangular frame behind the text to provide bed adhesion support for text islands, and a small outer border surrounds the frame.

---

### User Story 10 - Generate Packing Layout PDF Guide (Priority: P3)

After generating all box pieces, the designer needs a visual guide showing exactly where each box goes inside the game box. The system produces a PDF packing guide on exactly one page. It MUST NOT use a flat top-down or side view. Instead, it MUST use a 3D isometric/oblique angle view (looking slightly from above and to the side of the box) so the interior depth and vertical layers are clearly visible. The guide MUST show a step-by-step breakdown of how the box is filled up, pulling the top-level stacked boxes out of the project box (using vertical Z-displacement and arrows) to reveal the lower-level boxes at the base, progressing step-by-step or showing a clear exploded assembly view on the single page. The PDF is generated automatically on export but only regenerated if the layout changed (cached by SHA-256 hash of the layout + library version).

**Why this priority**: A packing guide is essential documentation for anyone assembling the insert — they need to know which box goes where, in what order. Cached regeneration avoids unnecessary PDF rebuilds during iterative development. Depends on the full packing/export pipeline being complete (P2).

**Independent Test**: Export a 4-box game, verify a PDF exists in the output directory, verify it shows 4 labeled boxes in correct positions with packing order numbered.

**Acceptance Scenarios**:

1. **Given** a Project with 4 sub-boxes packed into a 300x200mm game box, **When** `project.export()` runs, **Then** a PDF is produced in `{out_dir}/{project.name}/layout.pdf` on exactly one page, showing the game box outline in a 3D oblique/isometric projection, each sub-box at its packed position with label and dimensions, and spacer trays marked.
2. **Given** a multi-layer stacked layout, **When** the PDF is viewed, **Then** it shows a 3D exploded view with stacked upper boxes pulled upward along the Z-axis with dashed lines/arrows showing their placement positions, clearly revealing the lower-level boxes at the base.
3. **Given** a previously exported layout with no changes, **When** `project.export()` runs again, **Then** the PDF is NOT regenerated — it is skipped along with unchanged 3MF files.
4. **Given** a layout change (different box sizes or positions), **When** `project.export()` runs, **Then** the PDF IS regenerated to reflect the new layout.

---

### User Story 6 - Custom Compartment Layout (Manual Positioning) (Priority: P3)

The designer wants precise control over compartment placement. They specify exact X, Y coordinates for each compartment within the box interior, overriding automatic layout.

**Why this priority**: Power users need manual control for bespoke designs. Automatic layout (P2) handles the common case; manual positioning handles the edge cases.

**Independent Test**: Specify compartment positions explicitly and verify generated compartments appear at those coordinates relative to the box origin.

**Acceptance Scenarios**:

1. **Given** compartments with explicit (x, y) positions in the interior frame, **When** the box is generated, **Then** each compartment is placed at its specified position, and no automatic repositioning occurs.
2. **Given** a compartment manually positioned to overlap another, **When** the box is generated, **Then** the library warns or errors about the overlap rather than silently producing invalid geometry.

---

### Edge Cases

- What happens when a compartment depth exceeds the box interior height? The library must reject the configuration with a clear error.
- What happens when finger cutouts intersect each other or a compartment corner? The library must detect and warn about overlapping cutouts.
- How does the system handle zero-thickness walls (open compartments sharing a boundary)? The compartments merge into a single cavity.
- What happens when a nested sub-box has its own lid that increases its effective height? The lid thickness must be included in the nesting height check.
- How does the library handle non-rectangular box outlines (polygon-shaped boxes)? Compartments and sub-boxes must fit within the polygonal interior boundary.
- What happens with a hinged box that has compartments extending into the hinge area? The hinge knuckles must clear the compartment walls.
- What happens when all sub-boxes have minimum dimensions that collectively exceed the outer box interior? The library must reject the configuration at spec time with a descriptive error listing each over-constrained box.
- What happens when a row's gap is large enough for a spacer (>10mm) but the spacer width would be under 15mm? The gap is absorbed by the adjacent box -- spacer minimum dimensions (15mm W/L) take precedence over the gap threshold.
- What happens when one box in a row has a fixed (non-expandable) dimension that is shorter than the row's common length? The box keeps its fixed dimension; the row length still matches the longest box, leaving a gap for spacers beside the shorter box.
- What happens when spacer trays have a height under 5mm? They are permitted -- spacer trays can be shorter than 5mm in height (unlike width/length which has a 15mm minimum).
- What happens when a 3MF file already exists on disk but the exported mesh is empty (no geometry)? The file is NOT written; a warning is emitted.
- What happens when the Hausdorff distance tolerance is too tight and floating-point noise triggers unnecessary rewrites? The tolerance defaults to a value large enough to absorb FP jitter (e.g., 0.001mm) but is user-configurable.
- What happens when the Hausdorff comparison file or `.layout_cache.json` is corrupted or unreadable? The corrupted file is treated as a cache miss — silently overwritten with regenerated data.
- What happens when exporting a box with no lid (a no-lid box type)? Only a body 3MF is produced; no lid 3MF is generated. If a `LidBuilder` is configured on a no-lid type, a warning is emitted and the lid decoration is silently dropped.
- What happens when the Project has no sub-boxes (empty)? No files are produced; `ExportResult` returns empty written/skipped lists and no PDF is generated.
- What happens when a box has no compartments AND no explicit `size`? A `ValueError` is raised — either compartments or an explicit size is required.
- What happens when a spacer tray's computed height is zero or negative due to a packing error? A `ValueError` is raised during spacer generation.
- What happens when min text height threshold is set to 0mm? All labels print regardless of computed size — a threshold of 0 disables the size guard.
- What happens when compartment width ratios sum to > 1.0 (e.g., three compartments each requesting 0.5 width ratio)? The system MUST reject the configuration with a descriptive error listing the over-allocated compartments and their individual ratios.
- What happens when `mmu_label` is specified but `single_label` is not (or vice versa)? The unspecified mode defaults to the parent `LidBuilder` configuration — per-mode overrides are optional, not required.
- What happens when lid text auto-sizes below 4mm on a large lid but the text string is very short (e.g., "A")? The text is scaled until the character height hits the minimum; if it can't reach 4mm while fitting the lid, the label is skipped.
- What happens when a through-hole pattern intersects the label frame or text area? Through-holes are clipped to avoid the label area -- the label text and frame take precedence and pattern holes stop at the label boundary.
- What happens when the box body color and all three accent colors are set to the same value? The multi-color 3MF degenerates to a single material; it is still valid but the user gets a warning that no visible color contrast exists.
- What happens when the game box has no sub-boxes (empty Project)? No PDF is generated — the layout is trivially empty and there is nothing to pack.

## Requirements

### Functional Requirements

- **FR-001**: The library MUST accept outer box dimensions (width, length, height) and generate a 3D model of a closed box with a user-selected lid type.
- **FR-002**: The library MUST support at least these lid types: sliding lid, cap lid (friction-fit), hinged lid, and filament-hinge lid, each producing correct mating geometry between lid and body.
- **FR-003**: The library MUST allow users to define interior compartments by specifying dimensions (width, length, depth) either as absolute values (e.g., `size=(50.5, 70.2)`) or as ratios of the box interior dimensions (e.g., `width_ratio=0.5` takes 50% of the interior width). All dimensions MUST maintain 0.1mm precision — no rounding to whole millimetres.
- **FR-003a**: When any compartment uses ratio-based sizing, the sum of all compartment width ratios in a row MUST NOT exceed 1.0, and the sum of length ratios MUST NOT exceed the available length per row. The library MUST validate this at specification time and reject configurations where ratios overflow.
- **FR-004**: The library MUST provide automatic compartment layout that arranges compartments in the interior without overlaps, respecting wall thickness between adjacent compartments and between compartments and box walls. The layout engine MUST support rotating compartments by 90 degrees during bin-packing to optimize space utilization.
- **FR-005**: The library MUST allow manual positioning of compartments by specifying explicit coordinates within the interior frame.
- **FR-006**: The library MUST support finger cutouts on compartment walls (notches) and compartment floors (scoops), as well as finger holes on box exterior walls.
- **FR-007**: The library MUST reject invalid configurations at specification time: compartments deeper than the interior height, compartments that cannot fit in the interior, overlapping manually positioned compartments.
- **FR-008**: The library MUST support grouping compartments so they are packed together during automatic layout, and support packing bins (best-fit, next-fit, with rotation) for arrangement strategy.
- **FR-008a**: The library MUST support sharing a list of compartments across multiple boxes using `project.share_compartments(boxes, compartments)`. The library MUST automatically partition and bin-pack these compartments across the specified boxes during export.
- **FR-009**: The library MUST generate all pieces as output -- box body, lid, and any separate sub-boxes -- with consistent material colouring and the same coordinate frame so they align when assembled.
- **FR-010**: The library MUST support nested sub-boxes: an outer box specification containing inner sub-box specifications, with the nesting layout automatically packed into the outer box interior.
- **FR-011**: The library MUST validate that all nested sub-boxes fit within the outer box interior (both footprint and height) before accepting the specification.
- **FR-012**: The library MUST support declaring minimum dimensions for each nested sub-box, allowing the box to auto-expand to fill available space in its row or column up to the outer box interior bounds. Box expansion MUST prioritize the X and Y axes. For the Z (height) axis, the library MUST prefer generating spacer boxes/trays to fill the empty space rather than expanding the box's height, unless the remaining height difference is less than a 3mm threshold.
- **FR-013**: The library MUST align sub-boxes into rows where every box in the same row shares a common length (the length of the longest box in that row), so rows are uniform and boxes are easy to place and remove.
- **FR-013a**: For the main Earth box layout, card boxes and player boxes MUST share an identical footprint of 68.0 x 99.0 mm, with primary card boxes fixed at 55.2mm in height to fit cleanly under the player boards. Smaller card and player boxes MUST stack exactly to 55.2mm to form uniform columns.
- **FR-014**: The library MUST generate hollow spacer boxes/trays to fill all open spaces and gaps in the 3D packing layout. Spacer boxes/trays MUST NOT be thinner than 5mm in any dimension (width, length, or height). For vertical gaps along the Z-axis, a spacer box MUST be generated if the gap height is >= 3mm (subject to the 5mm minimum thickness rule). If the gap height is < 3mm, the adjacent box's height MUST expand to absorb the gap. Spacer boxes MUST be shown in the layout PDF.
- **FR-015**: The library MUST absorb horizontal gaps (X and Y axes) smaller than the auto-fill threshold (default 10mm) into adjacent expandable boxes rather than generating spacer trays. Gaps exactly equal to the threshold generate spacer trays.
- **FR-016**: The library MUST use variable row widths: each row's width is determined by the widest box in that row after expansion, and rows are not forced to equal widths.
- **FR-017**: The library MUST allow each sub-box to declare which dimensions are expandable (both width and length by default, and height if explicitly enabled). Non-expandable dimensions stay at their minimum specified value.
- **FR-018**: The library MUST support non-rectangular box outlines derived from 2D polygon paths, allowing compartments and contents to be clipped to the polygonal interior boundary.
- **FR-019**: The library MUST apply configurable clearance gaps between nested boxes and between compartments to account for 3D printing tolerances. The library MUST apply 1-2mm of clearance slack in the X and Y directions around nested sub-boxes relative to the game box walls or adjacent boxes to allow them to be easily added to and removed from the game box.
- **FR-020**: The library MUST allow lids to be decorated with text labels that auto-size to fill the lid area minus a configurable border margin. If the computed text height is below a configurable threshold (default 4mm), the label MUST be skipped.
- **FR-021**: The library MUST support two label layout modes: framed (rectangular frame with diagonal hatching behind text for bed adhesion, plus a small outer border) and frameless (text only). Both modes SHALL support corner-to-corner diagonal text orientation.
- **FR-022**: The library MUST support three independently settable accent colors on lids: label text color, frame top layer color, and pattern top layer color. Each defaults to a distinct color from the box body.
- **FR-023**: The library MUST support through-hole surface patterns (hex grid, grid, Voronoi, tessellations) that cut completely through the lid, saving filament in non-structural areas.
- **FR-024**: The library MUST support patterns with multiple colors, where different pattern elements can be assigned different accent colors.
- **FR-025**: The library MUST support multi-material (MMU) printing: positive inserts printed in a different colour/material from the box body.
- **FR-026**: The library MUST expose a fluent builder API so users chain calls to define a box.
- **FR-027**: The library MUST report dimensioned requirements for the 3D printer bed: the bounding box of each generated piece.
- **FR-028**: [DEFERRED] The library MUST allow boxes to be split/sliced for printing on smaller beds by dividing parts along user-specified cut planes. Deferred to future release — not in v1 scope.
- **FR-029**: The library MUST export each box body and each lid as separate 3MF files containing all material/color assignments (multi-color 3MF), and also export single-color 3MF variants for single-extruder printers.
- **FR-030**: The library MUST export a BoxKit by producing 3MF files for the outer box (body + lid), every nested sub-box (body + lid), and every spacer tray (one file each) -- all in both multi-color and single-color variants.
- **FR-031**: The library MUST use a 3D Hausdorff distance comparison to determine whether an exported mesh differs from the file already on disk; if the distance is below the tolerance threshold, the file MUST NOT be rewritten.
- **FR-032**: The library MUST report which files were written and which were skipped during export, so the user knows what changed.
- **FR-033**: The library MUST generate a valid PDF packing guide — a standards-compliant PDF file that renders correctly in any PDF viewer — showing a scaled top-down 2D layout of the game box interior. Each sub-box MUST be drawn as a labeled rectangle at its exact packed position with dimensions and packing order number, and spacer trays MUST be marked. The PDF MUST include a layered exploded breakdown: each row of boxes is rendered as a separate step where the top layer is pulled off vertically to reveal the boxes below, with arrows connecting the displaced box to its original packed position.
- **FR-034**: The library MUST cache the PDF output — regenerating only when the box layout or library version has changed since the last export (same SHA-256 hash gate as 3MF files).
- **FR-035**: The library MUST allow MMU (multi-color) and single-color exports to use different label specifications per box. For example, a lid can use a frameless label for MMU printing (text only, no frame) and a framed label for single-color printing (frame + text cutout).
- **FR-036**: For single-color export, compartment labels MUST render as single-layer cutouts engraved into the compartment floor (0.2mm deep) so they are visible as recessed text without a second material. For MMU export, compartment labels MUST render as raised text in a second color extruded 0.2mm above the floor.

### Key Entities

- **BoxSpec**: The complete configuration of a single box -- outer dimensions (explicit or auto-computed from compartments), wall/floor/lid thicknesses, lid type, compartments, finger holes, labelling decorations, material colours, print positioning, and auto-expand behaviour (expandable axes). Immutable once built. If `size` is omitted, dimensions are derived from compartment layout during packing.
- **BoxType**: Abstracts the lid mechanism -- defines how the body is constructed (e.g., with dovetail grooves for sliding, with overhangs for caps) and what lid geometry mates with it.
- **Compartment**: A single well inside a box interior, defined by its 2D footprint (width x length, or a polygon path), depth, rounding radius, and optional finger cutout specification. Can emit both a negative cavity and a positive insert.
- **Compartment Group**: A collection of compartments that must stay together during layout, with a packing algorithm directive.
- **Lid**: The closure for a box. Includes a decoration specification with: label text (auto-sized, with framed or frameless mode and optional corner-to-corner diagonal orientation), through-hole surface pattern (hex, grid, Voronoi, tessellation), fingernail lift cutout, and three independently settable accent colors (text color, frame top color, pattern top color). Minimum text height threshold (default 4mm) suppresses labels that would print illegibly. Supports per-export-mode label overrides: MMU and single-color exports can use different label specifications (e.g., frameless for MMU, framed for single) via `mmu_label` and `single_label` sub-configurations.
- **Finger Cutout**: A scoop or notch at a specific location on a box wall or compartment wall/floor, defined by radius, depth, and position offset.
- **Interior**: The usable volume inside a box, computed from outer dimensions minus wall/floor/lid thicknesses. Bounds all compartment and sub-box placement.
- **Project**: The top-level game insert description. A collection of multiple related boxes (e.g., an outer game box plus its nested sub-boxes) that orchestrates nesting layout and generates all pieces together. The public API surface; internally maps to BoxKit during export.
- **Spacer Box**: A hollow tray auto-generated to fill a gap in the nested layout. Has the same wall/floor construction as regular boxes but no compartments or lid. Minimum dimensions: 15mm width, 15mm length; may be shorter than 5mm in height.
- **3MF Export**: The output of a box or BoxKit -- a set of 3MF files written to disk, each containing embedded geometry with per-object material/color assignments (multi-color) or a single material (single-color). File naming follows `<label>_body.3mf` / `<label>_lid.3mf` conventions with `_single` suffix for single-color variants. Content-based caching via Hausdorff distance comparison prevents unnecessary file rewrites.
- **Layout PDF**: A packing guide generated alongside 3MF exports. Shows the game box interior from a 3D angle view. Includes layered exploded breakdowns: each row of boxes is rendered as a separate step where the top layer is displaced vertically to reveal boxes underneath, with arrows connecting displaced boxes back to their original positions. Boxes are labeled at their packed positions and numbered in packing order. Regenerated only when layout or library version changes.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can generate a complete box (body + lid + compartments) in under 10 lines of builder API code.
- **SC-002**: Automatic compartment layout (supporting 90-degree rotations of compartments) completes for 20 compartments in under 1 second.
- **SC-003**: All box lid types (sliding, cap, hinged, filament-hinge) produce geometry that mates correctly -- the lid and body can be assembled without modification.
- **SC-004**: 100% of invalid compartment configurations (overflow, excessive depth) are rejected at specification time with a descriptive error rather than producing broken geometry.
- **SC-005**: A nested box layout with 5 sub-boxes in a parent box produces valid, non-overlapping placements where the parent box can close with its lid on.
- **SC-006**: Finger cutouts on all four sides of a compartment can be specified and correctly carved without self-intersection.
- **SC-007**: Non-rectangular (polygon-path) boxes correctly clip all compartments and sub-boxes to the interior outline.
- **SC-008**: An auto-size layout with 6 sub-boxes (each with minimum dimensions) arranged into 2 rows completes in under 2 seconds and produces rows where every box in a row shares the same length.
- **SC-009**: After auto-sizing, any gap larger than 10mm between the expanded boxes and outer box walls is filled with a hollow spacer tray.
- **SC-010**: 100% of gap-fill scenarios with a gap under the 10mm threshold result in zero spacer trays -- the gap is absorbed by adjacent boxes.
- **SC-011**: Exporting a BoxKit with 3 sub-boxes and 2 spacer trays produces the correct number of 3MF files: (1 outer + 3 sub-boxes) x 2 (body + lid) x 2 (multi + single) + 2 spacers x 2 = 20 files total.
- **SC-012**: Re-exporting a BoxKit with zero geometry changes writes zero files to disk -- all files are skipped via Hausdorff distance comparison.
- **SC-013**: Changing one sub-box in a BoxKit and re-exporting rewrites only the affected files (that sub-box's body + lid 3MFs, multi and single color = 4 files) while all other files are skipped.
- **SC-014**: A lid with label text "Cards" auto-sized on a 100x70mm lid produces text with height ≥ 4mm and fills the lid area minus a 5mm border margin.
- **SC-015**: A lid with label text "A" on a 30x20mm lid produces zero label geometry (skipped because text height < 4mm) and no 3MF color assignments for the label.
- **SC-016**: A framed label exported as multi-color 3MF produces exactly the expected material assignments: body color for the lid slab, text color for the label text, frame top color for the frame border top layer.
- **SC-017**: A 4-box Project exported produces `layout.pdf` in the game output directory on exactly one page showing all 4 boxes at their packed positions with correct labels and dimensions.
- **SC-018**: Re-exporting an unchanged Project skips `layout.pdf` regeneration (same as 3MF files — zero writes if layout hash matches).
- **SC-019**: The generated `layout.pdf` MUST be a valid PDF file that renders correctly in any PDF viewer on exactly one page. It MUST NOT use flat top-down or side views; instead, it MUST draw the game box and packed sub-boxes in a 3D oblique or isometric projection (viewed from above and to the side). To show stacked layers clearly, upper boxes MUST be displaced vertically along the Z-axis (exploded view) with dashed alignment lines showing their slots, revealing the boxes underneath. The text labels on the boxes in the layout PDF MUST be visible, larger, and highly readable. If a label is hidden/blocked because another box sits directly on top of it, the label text MUST be shifted to the side. The text label MUST only display the label of the box (and not display the size/dimensions of the box).

## Assumptions

- The target fabrication method is FDM 3D printing with a minimum nozzle diameter of 0.4mm, so wall thicknesses below 1.2mm are not expected.
- The primary geometry engine is PythonSCAD (pybosl2), generating CSG solids consumed by OpenSCAD.
- Users have basic familiarity with 3D modeling concepts -- dimensions in millimetres, the coordinate frame (X=width, Y=length, Z=height), and the concept of subtracting cavities from a solid.
- Compartments are open-topped wells carved into the box floor; lids are not provided per-compartment (the box lid covers all).
- Boxes are right-rectangular by default; polygonal outlines are a secondary option.
- Labels on lids are single-line text with configurable font, size, and depth; multi-line labels are out of scope.
- The automatic layout algorithm uses a shelf-based 2D bin-packing strategy, not 3D packing (all compartments share the same floor level but may have different depths).
- Finger cutout dimensions default to adult fingertip sizing (14mm radius scoop, 6mm wall depth) but are configurable.
- Nested sub-box packing is 2.5D (footprint + height): sub-boxes are placed upright and packed by footprint, then checked for height fit within the outer box interior height.
- Auto-sizing distributes space using a fill-to-fit row strategy: boxes in the same row share a common length (the longest in that row), and row widths are variable -- determined by the widest box in each row, not forced equal across rows.
- The auto-fill gap threshold defaults to 10mm: gaps smaller than this are absorbed by adjacent expandable boxes instead of generating spacer trays.
- Spacer boxes are hollow trays (walls + floor, no compartments, no lid) with a minimum footprint of 15mm x 15mm; they may be shorter than 5mm in height.
- 3MF files are written to a user-specified output directory. File naming follows `<label>_body.3mf` / `<label>_lid.3mf` for multi-color, with `_single` suffix for single-color variants. Box types without lids (no-lid, path-box) only produce body files.
- The Hausdorff distance tolerance for content-based caching defaults to 0.001mm to absorb floating-point jitter while detecting real geometric changes.
- Label text auto-sizes to fill the available lid area minus a configurable border margin (default 5mm per side). The minimum text height threshold defaults to 4mm -- labels that cannot render at this size are skipped.
- Lid decoration accent colors default to distinct values from the body color: label text defaults to white, frame top layer defaults to a contrasting hue, and pattern top layer defaults to a third contrasting hue.
- Through-hole patterns stop at the label boundary -- the label text and frame take visual precedence over decorative holes.
- Diagonal text orientation follows the lid's natural corner-to-corner angle (not forced to 45°) for non-square lids.
- Framed labels include diagonal hatching lines behind the text at a spacing that allows the text to bridge without supports.
- Through-hole patterns clip at all lid boundaries — partial holes at lid edges are truncated (same as label intersection clipping).
- PDF packing guide renders boxes as solid shaded models from an isometric camera angle (30° above horizontal, 45° rotated) with semi-transparent walls to reveal hidden interior boxes.
- Performance baselines assume Apple Silicon or equivalent x86-64 hardware. Cached regeneration targets < 1s for compartment layout and < 2s for auto-sizing. Uncached first-run packing may take 30s–5min depending on box count; no upper bound is guaranteed.
- `.layout_cache.json` is expected to remain < 1MB for typical projects (< 50 boxes).
- Missing pybosl2 or pymeshlab dependencies at import time produce a clear error message naming the missing package and minimum required version (pymeshlab ≥ 0.2.0).
- SC-003 (assemblability without modification) is verified via render tests checking mating geometry dimensions; physical print validation is deferred to the user.
- Borrowed tessellation files are assumed to be stable; if they are refactored, pattern fill functions under `spec_driven/lid/pattern.py` must be updated accordingly.
