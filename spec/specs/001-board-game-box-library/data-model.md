# Data Model: Board Game Box Library

**Date**: 2026-08-11 | **Feature**: specs/001-board-game-box-library

**Package**: `spec_driven/` (greenfield, additive to existing codebase)

## Entity Relationship

```
Project (1) ──> BoxBuilder (N)          # Per-box typed builders
BoxBuilder (1) ──> LidBuilder (0..1)    # Lid decoration (fresh design)
LidBuilder (1) ──> PatternBuilder (0..1)# Surface pattern fill
BoxBuilder (1) ──> CompartmentBuilder (0..N) # Interior compartments
Project.export() ──> ExportResult (1)   # Export outcome
```

Internal mapping (fresh, no legacy pipeline dependency):
```
Project.export()
  └─> BoxBuilder → BoxSpec (internal)
  └─> BoxSpec → BoxType → box class (registry dispatch)
  └─> BoxPacking (auto-size + spacer)
  └─> BoxExporter → 3MF files
```

## Public Enums (`spec_driven/enums.py`)

| Enum | Members | Purpose |
|------|---------|---------|
| `BoxType` | SLIDING, CAP, HINGE, FILAMENT_HINGE, MAGNETIC, INSET, SLIDING_CATCH, SLIPOVER, SLIPOVER_PATH, CAP_PATH, NO_LID, CARD_LIBRARY | Box lid mechanism selection |
| `LabelMode` | FRAMED, FRAMELESS | Label decoration style |
| `PatternType` | HEX_GRID, GRID, VORONOI | Lid through-hole pattern |
| `ScoopSide` | FRONT, BACK, LEFT, RIGHT | Finger scoop placement |

## Color (`pybosl2.Color`, re-exported from `spec_driven`)

Use `pybosl2.Color` directly — no custom Color class. Supports webcolor names (`Color("darkgreen")`, `Color("gold")`) and list/tuple construction (`Color([1, 0, 0])`). RGBA values 0.0–1.0.

## Project (`spec_driven/project.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Game name for output subdirectory |
| `game_box_size` | `tuple[float, float, float]` | required | Outer game box [W, L, H] mm |
| `wall_thickness` | `float` | 2.0 | Default wall thickness |
| `floor_thickness` | `float` | 1.6 | Default floor thickness |
| `lid_thickness` | `float` | 2.0 | Default lid thickness |
| `gap_threshold` | `float` | 10.0 | Gap absorb threshold |
| `min_spacer_dim` | `float` | 15.0 | Min spacer dimension |

**Methods**:
- `box(box_type: BoxType, label: str, *, size: ..., **type_opts) -> <TypedBuilder>` — Factory with `@overload` per BoxType
- `export(out_dir: str | Path) -> ExportResult`

## BoxBuilder Base (`spec_driven/builders/_base.py`)

| Field | Type | Default |
|-------|------|---------|
| `box_type` | `ClassVar[BoxType]` | Set by subclass |
| `label` | `str` | required |
| `box_id` | `str \| None` | None (defaults to label) |
| `size` | `tuple[float, float, float] \| None` | None (computed from compartments) |
| `position` | `tuple[float, float, float] \| None` | None (manual packing position override) |
| `final_size` | `tuple[float, float, float] \| None` | None (resolved by 3D packer, set-once frozen after export) |
| `expandable` | `bool` | True |
| `expandable_width` | `bool` | True |
| `expandable_length` | `bool` | True |
| `no_rotate` | `bool` | False (prevents 3D packer from rotating the box; FR-013c) |
| `stackable` | `str \| None` | None ('inside' or 'outside' for no-lid boxes; FR-038) |
| `stackable_thickness` | `float \| None` | None (interlocking rim thickness) |
| `magnet_type` | `str \| None` | None ('round' or 'rect'; FR-039) |
| `magnet_size` | `tuple[float, float, float] \| None` | None (magnet slot dimensions) |
| `wall_thickness` | `float \| None` | None (project default) |
| `floor_thickness` | `float \| None` | None |
| `lid_thickness` | `float \| None` | None |
| `lid` | `LidBuilder \| None` | None |
| `finger_holes` | `tuple[FingerHoleBuilder, ...]` | () |
| `compartments` | `tuple[CompartmentBuilder, ...]` | () |

**Methods**: `compartment(label, *, size, depth, ...) -> CompartmentBuilder`

## Per-Type Builders (`spec_driven/builders/`)

Each builder extends `BoxBuilder` with type-specific typed fields. See prior data-model.md for the full field list per type. All frozen dataclasses.

## LidBuilder (`spec_driven/lid/builder.py`) — Fresh Design

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str \| None` | None | Label text (default for both modes) |
| `label_mode` | `LabelMode` | FRAMED | Framed or frameless (default for both modes) |
| `diagonal` | `bool` | False | Corner-to-corner text orientation |
| `text_color` | `Color \| None` | None | Auto-contrast default |
| `frame_color` | `Color \| None` | None | Auto-contrast default |
| `pattern` | `PatternBuilder \| None` | None | Through-hole pattern |
| `pattern_color` | `Color \| None` | None | Auto-contrast default |
| `min_text_height_mm` | `float` | 4.0 | Min text height before skip |
| `border_margin_mm` | `float` | 5.0 | Label border margin |
| `mmu_label` | `LidBuilder \| None` | None | Override for MMU export mode |
| `single_label` | `LidBuilder \| None` | None | Override for single-color export mode |

Per-mode override resolution: when `mmu_label` is set, its fields override the parent for MMU exports. When `single_label` is set, its fields override the parent for single-color exports. Unset modes fall back to the parent fields. Default colors when `None`: `text_color` → `Color.WHITE()`, `frame_color` → contrasting hue from body, `pattern_color` → third contrasting hue.

## PatternBuilder (`spec_driven/lid/builder.py`)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `PatternType` | HEX_GRID | Pattern fill type |
| `colors` | `tuple[Color, ...]` | () | Per-element colors (multiple supported) |
| `spacing` | `float \| None` | None | Auto-calculated from lid size |

Pattern fills are `Callable[[width, length, thickness], Bosl2Solid]` functions that produce through-hole cutouts. Borrowed tessellation generators provide the fill geometry.

## CompartmentBuilder (`spec_driven/compartments/builder.py`)

| Field | Type | Default |
|-------|------|---------|
| `label` | `str` | required |
| `size` | `tuple[float, float] \| None` | None (required if `width_ratio`/`length_ratio` not set) |
| `width_ratio` | `float \| None` | None |
| `length_ratio` | `float \| None` | None |
| `depth` | `float` | required |
| `rounded_corners` | `float` | 0.0 |
| `finger_scoop` | `bool` | False |
| `scoop_side` | `ScoopSide` | FRONT |

## ExportResult (`spec_driven/export/result.py`)

| Field | Type |
|-------|------|
| `written` | `tuple[str, ...]` |
| `skipped` | `tuple[str, ...]` |
| `total_files` | `int` |
| `cached_from` | `str \| None` |

## Box Protocol (`spec_driven/box/base.py`) — Fresh Design

```python
class BoxProtocol(Protocol):
    def build_body(self, spec: BoxSpec) -> Bosl2Solid: ...
    def build_lid(self, spec: BoxSpec, decoration: LidDecoration) -> Bosl2Solid: ...
    def interior(self, spec: BoxSpec) -> Interior: ...
```

Simpler than legacy `BoxBaseType`. No `Body` return type with `hollowed`/`carved` flags. No `LidPlate` contract. Each type directly builds its geometry.

## Standalone Box (FR-037)

A box exported directly without any enclosing game box. Built from a single `BoxSpec` and exported as body (+ lid if applicable), with no nesting layout, no auto-sizing, no packing phase, no layout PDF, and no spacer generation. Implemented by allowing `Project.box(...)` to be exported without a game box (`position` unset, no container packing).

## Stackable Box (FR-038)

A no-lid box with an interlocking rim. Fields: `stackable` (`"inside"` — recess on the top rim nests into the box above; `"outside"` — ridge around the outside mates with the box below), `stackable_thickness`, `stackable_fit_offset`.

## Magnet Slot (FR-039)

A cavity in a box side wall for an embedded magnet. Fields: `magnet_type` (`"round"` cylindrical cavity, or `"rect"` box cavity), `magnet_size` (diameter_or_width, length, depth), placed on opposing sides so adjacent stacked boxes attract.

## Hex Grid (FR-040)

A rectangular compartment region filled with a `rows × cols` array of hexagonal tile cutouts. Parameters:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rows` | `int` | required | Number of hex cell rows |
| `cols` | `int` | required | Number of hex cell columns |
| `tile_width` | `float` | required | Apothem-to-apothem width of each hex tile (mm) |
| `height` | `float` | required | Depth of the hex cell cutouts (mm) |
| `spacing` | `float` | 0.0 | Gap between adjacent hex cells (mm) |
| `push_block_height` | `float` | 0.0 | Height of the raised central pillar; 0 = flat floor (FR-041) |
| `push_block_width` | `float` | 15.0 | Width of the raised pillar (mm) |
| `finger_hole_diameter` | `float` | 0.0 | Diameter of the floor finger hole; 0 = no hole (FR-042) |

**Derived properties**: `apothem = tile_width / 2`, `circumradius = apothem / cos(30°)`.

## Hex Cell (FR-040–042)

A single hexagonal cutout within a Hex Grid, sized to hold one hex tile.

| Feature | Field | Behavior |
|---------|-------|----------|
| Push block | `push_block_height` | A smaller hexagon is subtracted from the cell center, leaving a raised central post so the tile rests elevated for easy grasping (FR-041) |
| Finger hole | `finger_hole_diameter` | A circular cutout through the cell floor so a finger pushes the tile up (FR-042). Offset to the cell edge (`0.4 × circumradius`) when a push block is present so the two never intersect |

**Implementation**: `spec_driven/compartments/hex_grid.py` — `HexGridSpec`, `HexCell`, `compute_hex_layout()`, `hex_grid_bounds()`, `build_hex_grid()`.

## Internal Cache (`spec_driven/packing/cache.py`)

Two-level: in-memory dict + `spec_driven/.layout_cache.json`. SHA-256 hash key from serialized input. Version-keyed invalidation.

## File Output

```
{out_dir}/{project.name}/mmu/{label}_body.3mf
{out_dir}/{project.name}/mmu/{label}_lid.3mf
{out_dir}/{project.name}/mmu/spacer_{N}.3mf
{out_dir}/{project.name}/single/{label}_body_single.3mf
{out_dir}/{project.name}/single/{label}_lid_single.3mf
{out_dir}/{project.name}/single/spacer_{N}_single.3mf
```
