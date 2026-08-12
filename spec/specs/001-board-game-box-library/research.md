# Research: Board Game Box Library

**Date**: 2026-08-11 | **Feature**: specs/001-board-game-box-library

## 1. Package Location: `spec_driven/`

### Decision: New `spec_driven/` package at repo root, additive to existing code

The new library lives under `spec_driven/` as a greenfield package. It does NOT import from or wrap the existing `box_base.py` pipeline. It does NOT replace the existing code — both coexist. A single `spec_driven.py` at the repo root is the public import.

**Rationale**: The existing pipeline has hard-won constraints (frep handle reuse segfaults, the `LidPlate` contract, `Body` return type, MMU colour copy logic) that were designed around a different architecture. Starting fresh under a separate package avoids inheriting these constraints while still being able to borrow pure algorithm code (tessellations, shapes).

**Alternatives considered**:
- Replace existing code in-place: Huge migration risk. 50+ test files, 40+ example projects would need updating. Existing users' code breaks.
- Subpackage under existing root: Still inherits import coupling and naming conflicts.
- Separate repository: Overkill for a codebase that shares tessellation and shape libraries.

### Decision: `spec_driven.py` root module for single import

```python
# spec_driven.py at repo root:
from spec_driven.project import Project
from spec_driven.enums import BoxType, LabelMode, PatternType, ScoopSide
from spec_driven.color import Color
from spec_driven.lid.builder import LidBuilder, PatternBuilder
from spec_driven.export.result import ExportResult

__all__ = [
    "Project", "BoxType", "LabelMode", "PatternType", "ScoopSide",
    "Color", "LidBuilder", "PatternBuilder", "ExportResult",
]
```

Users write: `from spec_driven import Project, BoxType, LabelMode, Color, LidBuilder`

**Rationale**: One import, discoverable at the repo root, follows the pattern of major Python libraries (`from flask import Flask`, `from fastapi import FastAPI`).

## 2. Enum-Driven Type Selection (unchanged from prior plan)

`BoxType`, `LabelMode`, `PatternType`, `ScoopSide` as Python `Enum` classes. No bare strings in public API. See prior research.md for full rationale.

## 3. Typed Per-Box Builders (unchanged core decision, updated paths)

One frozen dataclass builder per box type in `spec_driven/builders/`. See prior research.md for full design.

## 4. Fresh Lid Decoration Pipeline

### Decision: New lid pipeline under `spec_driven/lid/`, not wrapping `lids_base.py`

The existing `lids_base.py` uses a `LidPlate` contract where a box type hands a flat slab + shell + overlays, and `build_lid()` stacks decorations onto it. This contract constrains:
- The plate must be a flat slab at z=0..thickness
- Overlays are assembled at origin then translated
- The label/pipeline/fingernail all go through one stack

The new lid pipeline under `spec_driven/lid/` is designed around the clarified requirements directly:
- Through-hole patterns that cut completely through the lid
- Framed labels with diagonal hatching
- Corner-to-corner diagonal text orientation
- Three independent accent colors (text, frame top, pattern top)
- Minimum text height guard

**Borrowed**: Tessellation generators (penrose, pentagon, voronoi) and 2D shapes for space-filling.
**Fresh**: Label generation, pattern filling, color layer assignment, lid-body mating geometry.

### Decision: Lid pattern is a `Callable[[width, length, thickness], Bosl2Solid]` fill function

Each pattern type (hex grid, grid, voronoi) is implemented as a fill function that, given the lid's footprint and thickness, returns the through-hole cutout solid. This is a simpler contract than the existing `Pattern`/`PatternArea`/`LidFit` abstraction — just a function from dimensions to a solid.

```python
def hex_grid_fill(width: float, length: float, thickness: float, spacing: float) -> Bosl2Solid:
    """Return through-holes as hexagonal cutouts filling the lid area."""
    ...

def voronoi_fill(width: float, length: float, thickness: float, seed: int) -> Bosl2Solid:
    """Return through-holes as Voronoi cell cutouts."""

PATTERN_FILLS: dict[PatternType, Callable] = {
    PatternType.HEX_GRID: hex_grid_fill,
    PatternType.GRID: grid_fill,
    PatternType.VORONOI: voronoi_fill,
}
```

**Rationale**: Simpler than the existing pattern abstraction (no `PatternArea`, no `TiledPattern`/`TilingPattern`/`AreaPattern` classification). Patterns are just fill functions.

### Decision: Label generation is separate from lid body generation

The label (text + frame + hatching) is built independently and placed on the lid. The lid body (slab with through-holes) is built separately. They are colored independently and joined at export time. This decoupling means:
- The label can be tested without building a full lid
- Color assignments happen once at export, not during geometry construction
- The "skip if text < 4mm" check is a simple early return in the label builder

## 5. Fresh Box Construction Pipeline

### Decision: New box types under `spec_driven/box/types/`, not wrapping existing classes

Each box type implements a simple protocol:
```python
class BoxProtocol(Protocol):
    def build_body(self, spec: BoxSpec) -> Bosl2Solid: ...
    def build_lid(self, spec: BoxSpec, decoration: LidDecoration) -> Bosl2Solid: ...
    def interior(self, spec: BoxSpec) -> Interior: ...
```

This is simpler than the existing `BoxBaseType` pipeline (no `Body` with `hollowed`/`carved` flags, no `LidPlate` contract). Each type builds its geometry directly from the spec plus the pre-built lid decoration.

**Rationale**: The existing `Body` return type with `hollowed`/`carved` booleans exists because the pipeline needs to know whether the subclass already did the work. In the new design, the pipeline is simpler: build body, hollow, carve contents, add finger holes, position. No legacy geometry that "already hollows itself."

### Decision: Box type registry maps `BoxType` enum → factory function

```python
BOX_TYPE_REGISTRY: dict[BoxType, type[BoxProtocol]] = {
    BoxType.SLIDING: SlidingBox,
    BoxType.CAP: CapBox,
    ...
}
```

Constructed by `Project.export()` internally.

## 6. Fresh Compartment Layout (unchanged algorithm, new implementation)

Same shelf-based 2D bin packing algorithm; implemented fresh under `spec_driven/compartments/` with the row-alignment and common-length features.

## 7. Fresh Export & Caching (unchanged approach, new implementation)

Same SHA-256 hash cache and Hausdorff conditional writes; implemented fresh under `spec_driven/export/` and `spec_driven/packing/`.

## 8. Borrowed Components

| Component | Source | Usage |
|-----------|--------|-------|
| Penrose tiling | `penrose_tiling.py` | Lid pattern fill (through-holes) |
| Pentagon tiling families | `pentagon_tilings.py` | Lid pattern fill |
| Voronoi tesselation | `tesselations/voronoi.py` | Lid pattern fill |
| 2D shapes (coin, hexagon, rounded rect) | `shapes.py` | Compartment floor shapes, label frame corner rounding |
| pybosl2 CSG primitives | `pybosl2` | All 3D geometry |

## 9. Auto-Computed Box Dimensions

### Decision: `size` is optional on BoxBuilder — `None` means compute from compartments

If the user does not specify a box `size`, the system computes the minimum dimensions from the compartment layout. Each compartment contributes its footprint plus wall spacing, and the box dimensions are the bounding rectangle that fits all compartments. The height is derived from the deepest compartment plus floor thickness.

If `size` IS explicitly set, it is used as-is, and compartments must fit within the box interior (validated at spec time).

Box expansion (auto-sizing during `Project.export()`) applies regardless: if a box has `size=None`, the computed minimum is the starting point and the box can expand during packing to fill rows.

**Rationale**: Card boxes and component trays have known minimum content dimensions (card W×L, token diameter). The user should not need to manually compute box dimensions from compartment sizes. The packing phase handles expansion to fill the game box.

**Implementation**: In `Project.export()`, before packing, iterate over boxes with `size=None`. For each, compute bounding box of all compartments + wall/floor thicknesses. Set `final_size` to this computed minimum. The packing solver then treats this as the minimum and may expand it.

**Alternatives considered**:
- Always require explicit size: Violates Principle I (Developer Experience First) — users retype compartment dimensions as box dimensions.
- Compute size at BoxBuilder construction time: Compartments may be added after the box() call; computation must happen after all boxes+compartments are defined.

### Decision: Compartment dimensions drive minimum; packing phase drives maximum

The computed minimum from compartments is the floor — the box cannot be smaller. The packing phase determines the ceiling — the box may expand to fill available space. Between them, the packing solver chooses the size.

## 10. Ratio-Based Compartment Sizing

### Decision: Compartments can be sized by ratio of box interior instead of absolute mm

`CompartmentBuilder` accepts either `size=(w, l)` for absolute dimensions or `width_ratio=X, length_ratio=Y` (0 < X, Y ≤ 1.0) for percentage-of-interior sizing. Both modes resolve at export time once the box interior is known. This is critical for boxes that auto-size from compartments — the compartment says "I need 50% of whatever width this box ends up being."

**Rationale**: When a box's size is auto-computed from compartments, compartment dimensions shouldn't be hardcoded. A card compartment in a sliding box should say "take 100% of available width" rather than "72mm" — the latter ties the compartment to a specific box size and defeats auto-sizing.

**Validation**: The sum of width_ratios across compartments in the same row MUST NOT exceed 1.0. This is validated at export time once row assignment is known. Individual ratios must be in (0.0, 1.0] and are validated at `CompartmentBuilder` construction.

**Alternatives considered**:
- Only absolute sizing: Forces users to recompute compartment dimensions when box size changes.
- Only ratio sizing: Can't express fixed-size compartments (e.g., a coin cell slot that must be exactly 20mm).
- Combined with min/max: Adds complexity; the user can already specify absolute size as a floor and ratios as a ceiling.

### Decision: 0.1mm minimum precision, no rounding to whole mm

All dimensional values maintain 0.1mm precision. The `round()` in `resolve_size` uses 1 decimal place, and `compute_min_box_size` returns `float` values (not `int`). This matches FDM 3D printing tolerances where 0.1mm is the practical minimum layer resolution difference.

## 11. Per-Mode Label Overrides (MMU vs Single-Color)

### Decision: `LidBuilder` supports optional `mmu_label` and `single_label` sub-configurations

When specified, these override the parent label configuration for their respective export mode. If omitted, the parent `LidBuilder` settings apply to both modes.

```python
lid = LidBuilder(
    text="Cards",
    label_mode=LabelMode.FRAMED,  # default for both modes
    mmu_label=LidBuilder(text="Cards", label_mode=LabelMode.FRAMELESS),
    # single_color uses parent FRAMED setting since single_label is unset
)
```

**Rationale**: Single-color prints rely on recessed/engraved text for visibility, while MMU prints achieve readability through color contrast. A frameless label works well in MMU (white text on dark lid), but a framed label with a recessed frame border is more visible in single-color. The override mechanism avoids requiring the user to create two separate LidBuilders.

**Alternatives considered**:
- Two completely separate LidBuilder objects: Redundant; 90% of the config (text, colors, pattern) is shared.
- Boolean toggle "dual_mode": Insufficient — the user may want different text, label modes, or colors per mode.
- Automatic inference based on mode: Too magical; user intent varies per game and printer setup.

### Decision: Compartment labels switch between engraved cutout (single) and raised MMU text

For single-color export, compartment floor labels render as recessed text engraved 0.2mm into the floor surface — visible as shadows in the print. For MMU export, the same labels render as raised text extruded 0.2mm above the floor in a second material color. The `build_floor_label` function in `spec_driven/compartments/labels.py` accepts a `mode` parameter (`"mmu"` or `"single"`) to switch behavior.

**Rationale**: Single-color prints cannot distinguish text by color; recessed text provides legibility through depth contrast. MMU prints achieve text legibility through color change at a single layer height (0.2mm), matching the "one extra layer" MMU color swap constraint.

### Decision: Per-mode label export at `export()` time

The `Project.export()` method resolves which label configuration to use for each mode when generating 3MF files. For the `mmu/` pass, it checks `builder.lid.mmu_label` and falls back to `builder.lid`. Same for `single/`.

## 12. Geometry Source Constraint

### Decision: Only pybosl2 — never import pythonscad directly

Every geometric solid and 2D shape/path in `spec_driven/` MUST be constructed through pybosl2. The `pythonscad` module and native OpenSCAD built-ins (`cube`, `sphere`, `cylinder`, `polygon`, `square`, `circle`, `text`, `minkowski`, `textmetrics`) are NEVER imported directly in library code.

**Rationale**: pybosl2 provides a pure-Python, numpy-backed API that wraps the native solids with additional metadata (bounds, anchor points, size tracking) and avoids the native handle reuse segfault. The existing codebase has already eliminated wildcard imports of native built-ins (only 8 native functions remain at 16 sites across the legacy code). `spec_driven/` goes further: zero native imports.

**Enforcement**: Code review rule — any `import pythonscad` or `from pythonscad import ...` in `spec_driven/` is rejected. All geometry comes from `pybosl2.shapes3d` (solids) and `pybosl2.shapes2d` (paths). Transforms use `pybosl2.transforms`. Measurement uses `pybosl2`'s bounding box support.

### Decision: Prefer bosl2 basic pieces over higher-level generators

Where bosl2's basic primitives (`cube`, `cylinder`, `sphere`, `linear_extrude`, `rotate_extrude`) suffice, use them directly. Avoid higher-level shape generators (e.g., `coin`, `hexagon`, rounded rects from `shapes.py`) unless the shape cannot be expressed as a simple composition of basic pieces. This keeps the code minimal and reduces maintenance of borrowed shape code.

**Rationale**: bosl2's basic pieces are well-tested, fast, and have consistent APIs. Higher-level generators add indirection and potential for drift. The borrowed shape generators from the existing codebase (`shapes.py`) should only be used for complex shapes (e.g., hex grids, voronoi fills) that cannot be trivially expressed as basic booleans.

### Decision: Use pybosl2's built-in Color type — do not reimplement

`spec_driven/color.py` must be replaced with a thin re-export of pybosl2's built-in `Color` type. The custom `Color` dataclass (with named presets like `WHITE()`, `BLACK()`, `GOLD()`) is an unnecessary reimplementation. pybosl2's `Color` provides the same RGBA representation and integrates directly with the CSG pipeline without conversion.

**Rationale**: Maintaining a parallel Color type creates impedance mismatch — every color value must be converted between `spec_driven.Color` and `pybosl2.Color` at geometry construction boundaries. Using pybosl2's Color natively eliminates this conversion layer. The named preset constructors (`Color.WHITE()`, etc.) can be preserved as module-level constants or simple functions that return pybosl2 Color instances.

**Alternatives considered**:
- Keep custom Color: Adds conversion overhead at every geometry boundary.
- Use plain tuples: Loses type safety and named semantics.
- Use `colorsys` + raw floats: Reimplements what pybosl2 already provides.
