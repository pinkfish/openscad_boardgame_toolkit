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

## Color (`spec_driven/color.py`)

Immutable RGBA dataclass. Named presets: `Color.WHITE()`, `Color.BLACK()`, etc. Values 0.0–1.0.

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
| `final_size` | `tuple[float, float, float] \| None` | None (resolved by 3D packer) |
| `expandable` | `bool` | True |
| `expandable_width` | `bool` | True |
| `expandable_length` | `bool` | True |
| `wall_thickness` | `float \| None` | None (project default) |
| `floor_thickness` | `float \| None` | None |
| `lid_thickness` | `float \| None` | None |
| `lid` | `LidBuilder \| None` | None |
| `finger_holes` | `tuple[FingerHoleBuilder, ...]` | () |
| `compartments` | `tuple[CompartmentBuilder, ...]` | () |
| `final_size` | `tuple[float, float, float] \| None` | None (resolved by 3D packer, set-once frozen after export) |

**Methods**: `compartment(label, *, size, depth, ...) -> CompartmentBuilder`

## Per-Type Builders (`spec_driven/builders/`)

Each builder extends `BoxBuilder` with type-specific typed fields. See prior data-model.md for the full field list per type. All frozen dataclasses.

## LidBuilder (`spec_driven/lid/builder.py`) — Fresh Design

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str \| None` | None | Label text |
| `label_mode` | `LabelMode` | FRAMED | Framed or frameless |
| `diagonal` | `bool` | False | Corner-to-corner text orientation |
| `text_color` | `Color \| None` | None | Auto-contrast default |
| `frame_color` | `Color \| None` | None | Auto-contrast default |
| `pattern` | `PatternBuilder \| None` | None | Through-hole pattern |
| `pattern_color` | `Color \| None` | None | Auto-contrast default |
| `min_text_height_mm` | `float` | 4.0 | Min text height before skip |
| `border_margin_mm` | `float` | 5.0 | Label border margin |

Fresh design — no dependency on `lids_base.py` `LidPlate`/`build_lid()`.

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
| `size` | `tuple[float, float]` | required |
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
