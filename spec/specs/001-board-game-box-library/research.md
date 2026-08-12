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

## 9. Geometry Source Constraint

### Decision: Only pybosl2 — never import pythonscad directly

Every geometric solid and 2D shape/path in `spec_driven/` MUST be constructed through pybosl2. The `pythonscad` module and native OpenSCAD built-ins (`cube`, `sphere`, `cylinder`, `polygon`, `square`, `circle`, `text`, `minkowski`, `textmetrics`) are NEVER imported directly in library code.

**Rationale**: pybosl2 provides a pure-Python, numpy-backed API that wraps the native solids with additional metadata (bounds, anchor points, size tracking) and avoids the native handle reuse segfault. The existing codebase has already eliminated wildcard imports of native built-ins (only 8 native functions remain at 16 sites across the legacy code). `spec_driven/` goes further: zero native imports.

**Enforcement**: Code review rule — any `import pythonscad` or `from pythonscad import ...` in `spec_driven/` is rejected. All geometry comes from `pybosl2.shapes3d` (solids) and `pybosl2.shapes2d` (paths). Transforms use `pybosl2.transforms`. Measurement uses `pybosl2`'s bounding box support.
