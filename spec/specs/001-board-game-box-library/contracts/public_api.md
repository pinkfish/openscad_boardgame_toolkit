# Contracts: Board Game Box Library

**Hard constraint**: All geometry uses `pybosl2.shapes3d` / `pybosl2.shapes2d`. Native `pythonscad` or OpenSCAD built-ins MUST NOT be imported in `spec_driven/`.

Package: `spec_driven/` | Import: `from spec_driven import Project, BoxType, ...`

## Import Contract

```python
from spec_driven import (
    Project,                        # Top-level entry point
    BoxType,                        # Enum: SLIDING, CAP, HINGE, ...
    LabelMode,                      # Enum: FRAMED, FRAMELESS
    PatternType,                    # Enum: HEX_GRID, GRID, VORONOI
    ScoopSide,                      # Enum: FRONT, BACK, LEFT, RIGHT
    Color,                          # RGBA dataclass with named presets
    LidBuilder,                     # Lid decoration builder
    PatternBuilder,                 # Through-hole pattern builder
    ExportResult,                   # Result of Project.export()
)
```

## Project (`spec_driven/project.py`)

```
Project(
    name: str,
    *,
    game_box_size: tuple[float, float, float],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
)
```

### `.box(box_type, label, *, size, ...)` → Typed Builder

`@overload` signatures (12 total) — return type depends on `box_type`:

| box_type | Returns | Type-specific kwargs |
|----------|---------|---------------------|
| `BoxType.SLIDING` | `SlidingBoxBuilder` | `two_layer`, `two_layer_top_lid_ratio`, `two_layer_vee_shape` |
| `BoxType.CAP` | `CapBoxBuilder` | `cap_height`, `finger_hold_height`, `finger_hold_len`, `lid_wall_thickness` |
| `BoxType.HINGE` | `HingeBoxBuilder` | (type-specific fields) |
| `BoxType.FILAMENT_HINGE` | `FilamentHingeBoxBuilder` | ... |
| `BoxType.MAGNETIC` | `MagneticBoxBuilder` | `magnet_diameter`, `magnet_height`, `magnet_count_*` |
| `BoxType.INSET` | `InsetBoxBuilder` | ... |
| `BoxType.SLIDING_CATCH` | `SlidingCatchBoxBuilder` | ... |
| `BoxType.SLIPOVER` | `SlipoverBoxBuilder` | ... |
| `BoxType.SLIPOVER_PATH` | `SlipoverPathBoxBuilder` | ... |
| `BoxType.CAP_PATH` | `CapPathBoxBuilder` | ... |
| `BoxType.NO_LID` | `NoLidBoxBuilder` | ... |
| `BoxType.CARD_LIBRARY` | `CardLibraryBoxBuilder` | ... |

All builders share these base kwargs: `size: tuple[float, float, float] | None = None` (auto-computed from compartments if omitted), `expandable: bool = True`, `expandable_width: bool = True`, `expandable_length: bool = True`, `wall_thickness: float | None = None`, `floor_thickness: float | None = None`, `lid_thickness: float | None = None`, `lid: LidBuilder | None = None`.

### `.export(out_dir: str | Path) -> ExportResult`

Builds all geometry, packs boxes, generates spacers, writes 3MF files. Cached layout (SHA-256 hash). Hausdorff-gated file writes.

## LidBuilder (`spec_driven/lid/builder.py`) — Fresh Design

```
LidBuilder(
    text: str | None = None,
    label_mode: LabelMode = LabelMode.FRAMED,
    diagonal: bool = False,
    text_color: Color | None = None,
    frame_color: Color | None = None,
    pattern: PatternBuilder | None = None,
    pattern_color: Color | None = None,
    min_text_height_mm: float = 4.0,
    border_margin_mm: float = 5.0,
    mmu_label: LidBuilder | None = None,      # Override for MMU export mode
    single_label: LidBuilder | None = None,    # Override for single-color export mode
)
```

**Per-mode overrides**: `mmu_label` and `single_label` allow different label specifications per export mode. When set, their fields override the parent LidBuilder for that mode. The common use case is `label_mode=LabelMode.FRAMED` (default) with `mmu_label=LidBuilder(label_mode=LabelMode.FRAMELESS)` — single-color uses a framed recessed label, MMU uses a frameless text-only label. Unset modes fall back to the parent fields.

**Fresh design** — not constrained by legacy `LidPlate`/`build_lid()`.

Default colors when `None`: `text_color` → `Color.WHITE()`, `frame_color` → contrasting hue from body, `pattern_color` → third contrasting hue.

**Compartment labels per mode**: Single-color exports use engraved 0.2mm recessed cutout text (visible by depth contrast). MMU exports use 0.2mm raised second-color text (visible by material color contrast). This is controlled by a `mode` parameter in `build_floor_label()`.

## PatternBuilder (`spec_driven/lid/builder.py`)

```
PatternBuilder(
    type: PatternType = PatternType.HEX_GRID,
    colors: tuple[Color, ...] = (),
    spacing: float | None = None,
)
```

Pattern fills are `Callable[[float, float, float], Bosl2Solid]` — functions from (width, length, thickness) to through-hole cutout solid. Tessellation generators (penrose, pentagon, voronoi) are borrowed from the existing codebase. Multiple `colors` assign different elements within the pattern.

## CompartmentBuilder (`spec_driven/compartments/builder.py`)

```
CompartmentBuilder(
    label: str,
    size: tuple[float, float],
    depth: float,
    rounded_corners: float = 0.0,
    finger_scoop: bool = False,
    scoop_side: ScoopSide = ScoopSide.FRONT,
)
```

## Color (`spec_driven/color.py`)

```
Color(r: float, g: float, b: float, a: float = 1.0)
Color.WHITE()  → Color(1, 1, 1)
Color.BLACK()  → Color(0, 0, 0)
Color.RED()    → Color(1, 0, 0)
# ... additional presets
```

## File Naming

```
{out_dir}/{project.name}/mmu/{label}_body.3mf
{out_dir}/{project.name}/mmu/{label}_lid.3mf
{out_dir}/{project.name}/mmu/spacer_{N}.3mf
{out_dir}/{project.name}/single/{label}_body_single.3mf
{out_dir}/{project.name}/single/{label}_lid_single.3mf
{out_dir}/{project.name}/single/spacer_{N}_single.3mf
```

No-lid box types skip `_lid` files.

## Error Contract

| Condition | Error | Message includes |
|-----------|-------|-----------------|
| Invalid BoxType | `ValueError` | Valid enum values |
| Unknown type-specific kwarg | `TypeError` | Builder name, valid field names |
| Duplicate box label | `ValueError` | The duplicate label |
| Compartment depth > interior | `ValueError` | Label, depth, max allowed |
| Boxes overflow container | `ValueError` | Which boxes overflow, by how much |
| Empty mesh (0 facets) | Warning (not error) | Box label, skipped |
