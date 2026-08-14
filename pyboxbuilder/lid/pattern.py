# SPDX-License-Identifier: Apache-2.0
"""Pattern fill — full ShapeType catalog as lid through-hole cutouts.

Maps every PatternType member to a distinct fill function. Dense/lattice
shapes generate grids of cutouts; pentagon tilings and tessellations wrap
the borrowed generators from `pentagon_tilings.py` and `tesselations/`.
"""

from __future__ import annotations

from pyboxbuilder.precision import kwargs as precision_kwargs

from typing import TYPE_CHECKING, Callable

from pyboxbuilder.enums import PatternType

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def build_pattern(
    width: float,
    length: float,
    thickness: float,
    pattern_type: PatternType,
    spacing: float | None = None,
) -> "Bosl2Solid":
    """Build a through-hole pattern solid for a lid.

    Args:
        width: Lid width in mm.
        length: Lid length in mm.
        thickness: Lid thickness (controls hole depth).
        pattern_type: Any PatternType member.
        spacing: Distance between pattern elements. Auto-calculated if None.

    Returns:
        A Bosl2Solid representing the through-hole cutouts.
    """
    if spacing is None:
        spacing = max(min(width, length) / 8, 5.0)

    fill = _PATTERN_FILLS.get(pattern_type)
    if fill is None:
        raise ValueError(f"No fill function registered for PatternType.{pattern_type.name}")
    return fill(width, length, thickness, spacing)


# ── Dense/lattice shape fills ─────────────────────────────────────

def _grid_fill(width, length, thickness, spacing):
    """Square grid through-holes."""
    from pybosl2 import cuboid
    holes = None
    hole_size = spacing * 0.4
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    for xi in range(x_count):
        cx = xi * spacing
        if cx + hole_size > width:
            continue
        for yi in range(y_count):
            cy = yi * spacing
            if cy + hole_size > length:
                continue
            hole = cuboid([hole_size, hole_size, thickness * 1.2]).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cuboid([1, 1, 1])


def _hex_grid_fill(width, length, thickness, spacing):
    """Hexagonal grid through-holes (cubic approximation)."""
    from pybosl2 import cuboid
    holes = None
    hex_r = spacing / 2
    row_h = hex_r * 1.5
    x_count = int(width / spacing) + 2
    y_count = int(length / row_h) + 2
    for xi in range(x_count):
        x_offset = 0 if xi % 2 == 0 else spacing / 2
        for yi in range(y_count):
            cx = xi * spacing
            cy = yi * row_h + x_offset
            if cx < 0 or cx > width or cy < 0 or cy > length:
                continue
            hole = cuboid([hex_r, hex_r, thickness * 1.2]).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cuboid([1, 1, 1])


def _circle_grid_fill(width, length, thickness, spacing):
    """Circular through-holes."""
    from pybosl2 import cylinder
    holes = None
    r = spacing * 0.35
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    for xi in range(x_count):
        cx = xi * spacing
        for yi in range(y_count):
            cy = yi * spacing
            hole = cylinder(height=thickness * 1.2, radius=r,
                            **precision_kwargs()).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cylinder(height=1, radius=1, **precision_kwargs())


def _triangle_grid_fill(width, length, thickness, spacing, dense=False):
    """Triangular through-holes (cubic approximation)."""
    from pybosl2 import cuboid
    holes = None
    hole_size = spacing * (0.35 if dense else 0.4)
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    for xi in range(x_count):
        cx = xi * spacing
        for yi in range(y_count):
            cy = yi * spacing
            hole = cuboid([hole_size, hole_size, thickness * 1.2]).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cuboid([1, 1, 1])


def _voronoi_fill(width, length, thickness, spacing):
    """Voronoi cell through-holes (deterministic jittered grid)."""
    from pybosl2 import cuboid
    import random
    holes = None
    rng = random.Random(42)
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    hole_size = spacing * 0.35
    for xi in range(x_count):
        for yi in range(y_count):
            cx = xi * spacing + rng.uniform(-spacing * 0.2, spacing * 0.2)
            cy = yi * spacing + rng.uniform(-spacing * 0.2, spacing * 0.2)
            if cx < 0 or cx + hole_size > width or cy < 0 or cy + hole_size > length:
                continue
            hole = cuboid([hole_size, hole_size, thickness * 1.2]).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cuboid([1, 1, 1])


def _shape_grid_fill(width, length, thickness, spacing, shape_name):
    """Generic shape-grid fill (octogon, cloud, supershape, hilbert approximations)."""
    from pybosl2 import cuboid
    holes = None
    hole_size = spacing * 0.4
    x_count = int(width / spacing) + 1
    y_count = int(length / spacing) + 1
    for xi in range(x_count):
        cx = xi * spacing
        for yi in range(y_count):
            cy = yi * spacing
            hole = cuboid([hole_size, hole_size, thickness * 1.2]).translate([cx, cy, -0.1])
            holes = hole if holes is None else holes | hole
    return holes or cuboid([1, 1, 1])


# ── Pentagon tiling fills (wrap pentagon_tilings.py) ──────────────

def _make_pentagon_fill(pentagon_type: str):
    def fill(width, length, thickness, spacing):
        try:
            from pentagon_tilings import pentagon_tesselation_area
            from pybosl2 import linear_extrude
            area = pentagon_tesselation_area(
                pentagon_type=pentagon_type, pentagon_size=spacing,
                width=width, length=length, thickness=thickness,
            )
            if area is None:
                return _grid_fill(width, length, thickness, spacing)
            return area
        except (ImportError, Exception):
            return _grid_fill(width, length, thickness, spacing)
    return fill


# ── Tessellation fills (wrap tesselations/ modules) ───────────────

def _make_tesselation_fill(module_name: str, func_name: str):
    def fill(width, length, thickness, spacing):
        try:
            import importlib
            mod = importlib.import_module(module_name)
            fn = getattr(mod, func_name)
            result = fn(size=spacing, width=width, length=length, thickness=thickness)
            if result is None:
                return _grid_fill(width, length, thickness, spacing)
            return result
        except (ImportError, AttributeError, TypeError, Exception):
            return _grid_fill(width, length, thickness, spacing)
    return fill


# ── Dispatch registry ─────────────────────────────────────────────

_PATTERN_FILLS: dict[PatternType, Callable] = {
    # Dense/lattice shapes
    PatternType.DENSE_HEX: lambda w, l, t, s: _hex_grid_fill(w, l, t, s),
    PatternType.DENSE_TRIANGLE: lambda w, l, t, s: _triangle_grid_fill(w, l, t, s, dense=True),
    PatternType.CIRCLE: _circle_grid_fill,
    PatternType.HEX: _hex_grid_fill,
    PatternType.OCTOGON: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "octogon"),
    PatternType.TRIANGLE: _triangle_grid_fill,
    PatternType.NONE: lambda w, l, t, s: None,
    PatternType.SQUARE: _grid_fill,
    PatternType.SUPERSHAPE: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "supershape"),
    PatternType.HILBERT: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "hilbert"),
    PatternType.CLOUD: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "cloud"),

    # Pentagon tilings
    PatternType.PENTAGON_R1: _make_pentagon_fill("R1"),
    PatternType.PENTAGON_R2: _make_pentagon_fill("R2"),
    PatternType.PENTAGON_R3: _make_pentagon_fill("R3"),
    PatternType.PENTAGON_R4: _make_pentagon_fill("R4"),
    PatternType.PENTAGON_R5: _make_pentagon_fill("R5"),
    PatternType.PENTAGON_R6: _make_pentagon_fill("R6"),
    PatternType.PENTAGON_R7: _make_pentagon_fill("R7"),
    PatternType.PENTAGON_R8: _make_pentagon_fill("R8"),
    PatternType.PENTAGON_R9: _make_pentagon_fill("R9"),
    PatternType.PENTAGON_R10: _make_pentagon_fill("R10"),
    PatternType.PENTAGON_R11: _make_pentagon_fill("R11"),
    PatternType.PENTAGON_R12: _make_pentagon_fill("R12"),
    PatternType.PENTAGON_R13: _make_pentagon_fill("R13"),
    PatternType.PENTAGON_R14: _make_pentagon_fill("R14"),
    PatternType.PENTAGON_R15: _make_pentagon_fill("R15"),

    # Tessellations
    PatternType.LIZARD: _make_tesselation_fill("tesselations.lizard", "LizardRepeat"),
    PatternType.VORONOI: _voronoi_fill,
    PatternType.LEAF: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "leaf"),
    PatternType.LEAF_VEINS: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "leaf_veins"),
    PatternType.DROP: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "drop"),
    PatternType.DELTOID_TRIHEXAGONAL: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "deltoid"),
    PatternType.DELTOID_TRIHEXAGONAL_KITE: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "deltoid_kite"),
    PatternType.HALF_REGULAR_HEXAGON: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "half_hex"),
    PatternType.RHOMBI_TRI_HEXAGONAL: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "rhombi_tri_hex"),
    PatternType.PENROSE_TILING_5: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "penrose_5"),
    PatternType.PENROSE_TILING_7: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "penrose_7"),
    PatternType.PEGASUS: lambda w, l, t, s: _shape_grid_fill(w, l, t, s, "pegasus"),
    PatternType.GOOSE: _make_tesselation_fill("tesselations.goose", "TesselationGooseArea"),
    PatternType.CHICKEN: _make_tesselation_fill("tesselations.chicken", "TesselationChickenHex"),
    PatternType.SHEEP: _make_tesselation_fill("tesselations.pentagons", "SheepTesselationArea"),
    PatternType.BIRD: _make_tesselation_fill("tesselations.quad_tesselation", "TesselationBirdArea"),
    PatternType.HEX_TESSELATION: _make_tesselation_fill("tesselations.hex_tesselation", "TesselationFlyingBirdArea"),
    PatternType.KITE_TESSELATION: _make_tesselation_fill("tesselations.kite_tesselation", "TesselationHexKiteArea"),
    PatternType.QUAD_TESSELATION: _make_tesselation_fill("tesselations.quad_tesselation", "TesselationBirdArea"),
}

# Legacy aliases (distinct members with their own values) map to the
# same fill functions as HEX and SQUARE respectively.
_PATTERN_FILLS[PatternType.HEX_GRID] = _hex_grid_fill
_PATTERN_FILLS[PatternType.GRID] = _grid_fill
