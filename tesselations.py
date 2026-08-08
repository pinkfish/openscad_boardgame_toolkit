# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: tesselations.py
#    Shared tesselation building blocks (grids, polygon outline distortion,
#    leaf/hex/deltoid/rhombi/pegasus pattern generators).
#
# FileSummary: Various functions to make a variety of tesselations.
# FileGroup: Shapes

from __future__ import annotations

from collections.abc import Sequence
import math

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes2d
from pybosl2 import Path2D, Region


# No osuse() here any more: every region operation this file used to make through the
# BOSL2 FFI (offset_stroke / union / intersection / difference) is direct 2-D CSG now.
# That is not just tidiness -- a failing assert inside an osuse'd .scad function ABORTS THE
# PROCESS instead of raising, which is what made the leaf tilings unusable and unfixable
# from Python. See tests/repro_osuse_assert_aborts.py.

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TESSELATION_LINE_NORMAL = 0
TESSELATION_LINE_FLIPPED = 1
TESSELATION_LINE_SYMETRIC = 2
TESSELATION_LINE_REVERSE = 3
TESSELATION_LINE_FLIPPED_REVERSE = 4


# ---------------------------------------------------------------------------
# Grid repeaters
# ---------------------------------------------------------------------------


def hexagon_tesselation_repeat_at_location(x: int, y: int, size: float, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Places *children* at a specific spot in a hexagonal-tesselation grid.

    Usage::

        hexagon_tesselation_repeat_at_location(x=0, y=0, size=20, children=LizardTriangle(size=20, thickness=1))

    Args:
        x: the x location to generate at (int)
        y: the y location to generate at (int)
        size: the size of the hex
        children: solid to place
    """
    assert size > 0, f"Need to have a size specified size={size}"
    assert isinstance(x, int), f"Need to have a x int specified x={x}"
    assert isinstance(y, int), f"Need to have a y int specified y={y}"
    radius = size / 2
    side_length = radius * math.sqrt(3)
    apothem = math.sqrt(3) / 2 * side_length
    dx = apothem * 2
    dy = radius * 4 + apothem * 0.8
    assert children is not None, "children must be given"
    return children.translate([x / 2 * dy, y * dx + ((x + 1) % 2) * (dx / 2), 0])


def hexagon_tesselation_repeat(rows: int, cols: int, size: float, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Tiles *children* across a hexagonal-tesselation grid.

    Usage::

        hexagon_tesselation_repeat(rows=4, cols=4, size=20, children=LizardTriangle(size=20, thickness=1))

    Args:
        rows: number of rows to generate
        cols: number of columns to generate
        size: the size of the tesselation
        children: solid to repeat
    """
    assert size > 0, f"Need to have a size specified size={size}"
    assert rows > 0, f"Need to have a rows specified rows={rows}"
    assert cols > 0, f"Need to have a cols specified cols={cols}"
    radius = size / 2
    side_length = radius * math.sqrt(3)
    apothem = math.sqrt(3) / 2 * side_length
    dx = apothem * 2
    dy = radius * 4 + apothem * 0.8

    assert children is not None, "children must be given"
    pieces = [
        children.translate([i / 2 * dy, j * dx + ((i + 1) % 2) * (dx / 2), 0])
        for i in range(rows)
        for j in range(cols)
    ]
    # Balanced union: PythonSCAD builds the tree lazily, so a left fold is free to
    # assemble and then makes Manifold re-boolean the whole accumulated tiling once
    # per cell at MESH time -- quadratic in the cell count.
    shape = union_all_2d(pieces)
    assert shape is not None
    return shape


def triangle_tesselation_repeat_at_location(x: int, y: int, size: float, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Places *children* at a specific spot in a triangle-tesselation grid.

    Usage::

        triangle_tesselation_repeat_at_location(x=0, y=0, size=20, children=LizardTriangle(size=20, thickness=1))

    Args:
        x: the x location to generate at (int)
        y: the y location to generate at (int)
        size: the size of the triangle
        children: solid to place
    """
    assert size != 0, "Need to have a size specified"
    assert isinstance(x, int), f"Need to have a x int specified x={x}"
    assert isinstance(y, int), f"Need to have a y int specified y={y}"
    side_length = size * math.sin(math.radians(60))
    height = side_length * (math.sqrt(3) / 2)
    assert children is not None, "children must be given"
    return children.rotate([0, 0, 60 * (x % 2)]).translate(
        [side_length / 2 * x, height * y + (size - height) * (x % 2), 0]
    )


def triangle_tesselation_repeat(rows: int, cols: int, size: float, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Tiles *children* across a triangle-tesselation grid.

    Usage::

        triangle_tesselation_repeat(rows=4, cols=4, size=20, children=half_regular_hexagon(20))

    Args:
        rows: number of rows to generate
        cols: number of columns to generate
        size: the size of the tesselation
        children: solid to repeat
    """
    assert size > 0, f"Need to have a size specified size={size}"
    assert rows > 0, f"Need to have a rows specified rows={rows}"
    assert cols > 0, f"Need to have a cols specified cols={cols}"
    side_length = size * math.sin(math.radians(60))
    height = side_length * (math.sqrt(3) / 2)

    assert children is not None, "children must be given"
    pieces = [
        children.rotate([0, 0, 60 * (i % 2)]).translate(
            [side_length / 2 * i, height * j + (size - height) * (i % 2), 0]
        )
        for i in range(rows)
        for j in range(cols)
    ]
    # Balanced union: PythonSCAD builds the tree lazily, so a left fold is free to
    # assemble and then makes Manifold re-boolean the whole accumulated tiling once
    # per cell at MESH time -- quadratic in the cell count.
    shape = union_all_2d(pieces)
    assert shape is not None
    return shape


# ---------------------------------------------------------------------------
# Hex / square outline distortion
# ---------------------------------------------------------------------------


def hexagonal_tesselation_generate_edge(pts: list[list[float]], side_length: float) -> list[list[float]]:
    """Scales a normalized edge-profile path by *side_length*."""
    return [[p[0] * side_length, p[1] * side_length] for p in pts]


def hexagonal_tesselation(points: list[list[list[float]]], radius: float = 10) -> list[list[float]]:
    """Makes a hex outline path, distorting each side using the given profiles.

    Each profile line runs from x=-0.5 to x=0.5.

    Usage::

        hexagonal_tesselation(points=[
            [[-0.5, 0], [0, 0.2], [0.5, 0]],
            [[-0.5, 0], [0, -0.2], [0.5, 0]],
            [[-0.5, 0], [0.3, 0.2], [0.5, 0]],
        ])

    Args:
        points: set of three lines to use as points on the hex
        radius: the radius of the hex (default 10)
    """
    assert len(points) == 3, f"points must have three arrays, points={points}"
    for c in points:
        assert len(c) > 1, f"Each array must have more than two elements, c={c}"

    side_length = 2 * radius * math.sin(math.radians(30))
    apothem = math.sqrt(3) / 2 * side_length

    poly = []
    for i in range(6):
        center_pt = Path2D([[apothem, 0]]).rot(60 * i)[0]
        side_idx = (i // 2) % 3
        if i % 2 == 0:
            edge_pts = list(reversed(Path2D(points[side_idx]).rot(180)))
        else:
            edge_pts = points[side_idx]
        edge = hexagonal_tesselation_generate_edge(pts=edge_pts, side_length=side_length)
        rotated_edge = Path2D(edge).rot(60 * i + 90)
        # native_points, not the bare rows: iterating a Path2D yields numpy arrays, and the
        # declared return type here is plain point data that callers hand straight to the
        # native polygon()/region() -- which answers a raw ndarray with "SystemError:
        # <built-in function polygon> returned a result with an exception set".
        poly.extend(native_points(rotated_edge.move(center_pt)))
    return poly


def square_tesselation_generate_edge(pts: list[list[float]], side_length: float) -> list[list[float]]:
    """Scales a normalized edge-profile path by *side_length*."""
    return [[p[0] * side_length, p[1] * side_length] for p in pts]


def square_tesselation(
    points: list[list[list[float]]], size: list[float], thickness: float = 0, outer_offset: float = 0
) -> list[list[float]]:
    """Makes a square outline region, distorting each side using the given profiles.

    Only needs two side profiles (the other two sides mirror them). Each
    profile line runs from x=-0.5 to x=0.5.

    Usage::

        square_tesselation(
            points=[
                [[-0.5, 0], [0, 0.2], [0.5, 0]],
                [[-0.5, 0], [0, -0.2], [0.5, 0]],
            ],
            size=[20, 20],
        )

    Args:
        points: set of two lines to use as points on the square
        size: the size of the square [width, length]
        thickness: thickness of the outline, if non-0 adds an outline (default 0)
        outer_offset: extra outward offset for layout (default 0)
    Returns:
        raw region data (use ``region(...)`` to render)
    """
    assert size != 0, "Need to have a size specified"
    assert len(points) == 2, f"Input points must be of size 2, points={points}"
    assert len(size) == 2, f"Input size must be of form [x,y], size={size}"

    width, length = size[0], size[1]
    length_line = square_tesselation_generate_edge(points[0], length)
    width_line = square_tesselation_generate_edge(points[1], width)

    # pybosl2's numpy Path2D has no `+` concat -- join the point lists instead. NB `to_list` is
    # a PROPERTY, not a method: calling it raised "'list' object is not callable", which is
    # what broke every square tesselation (DROP, PEGASUS).
    poly = (
        Path2D(width_line).rot(90).reverse().move([-width / 2, 0]).to_list
        + Path2D(length_line).rot(0).move([0, -length / 2]).to_list
        + Path2D(width_line).rot(90).move([width / 2, 0]).to_list
        + Path2D(length_line).rot(0).reverse().move([0, length / 2]).to_list
    )
    poly = Path2D._deduplicate(poly, closed=True)

    outer = Path2D(poly).offset(delta=outer_offset, chamfer=True) if outer_offset != 0 else poly
    outer = outer.to_list if hasattr(outer, "to_list") else list(outer)
    if thickness == 0:
        return [outer]

    inner = Path2D._deduplicate(Path2D(poly).offset(delta=-thickness, chamfer=True), closed=True)
    # The two offsets are CONCENTRIC, so the inner one lies strictly inside the outer: the
    # difference needs no polygon clipping, it is just "outline plus hole", which is exactly
    # how a region is represented (the same reasoning as base_bgtk.DifferenceWithOffset).
    # The osuse BOSL2 difference() this replaces ABORTS THE PROCESS on these inputs, which is
    # what stopped DROP and PEGASUS being usable as lid patterns.
    return [outer, inner]


# ---------------------------------------------------------------------------
# Side-line / polygon distortion
# ---------------------------------------------------------------------------


def tesselation_side_line(
    path: list[list[float]], side: list[list[float]], flip: int = TESSELATION_LINE_NORMAL
) -> list[list[float]]:
    """Distorts one polygon side using a profile line.

    Args:
        path: 2-point path naming the side to point along
        side: the profile pattern for the side
        flip: one of the TESSELATION_LINE_* constants (default TESSELATION_LINE_NORMAL)
    """
    assert len(path) == 2, f"Input path must be of size 2 path={path}"
    assert len(path[0]) == 2 and len(path[1]) == 2, (
        f"Input path[0],[1] must be of size 2 path[0]={path[0]} path[1]={path[1]}"
    )
    assert len(side) >= 2, f"Input side must at least than size 2 side={side}"

    x = path[1][0] - path[0][0]
    y = path[1][1] - path[0][1]
    split_length = math.sqrt(x * x + y * y)
    angle = math.degrees(math.atan2(y, x))

    if flip in (TESSELATION_LINE_FLIPPED_REVERSE, TESSELATION_LINE_REVERSE):
        cur_side = list(reversed([[1 - i[0], i[1]] for i in side]))
    else:
        cur_side = side

    side_flipped = [
        [i[0], -i[1] if flip in (TESSELATION_LINE_FLIPPED, TESSELATION_LINE_FLIPPED_REVERSE) else i[1]]
        for i in cur_side
    ]

    if flip == TESSELATION_LINE_SYMETRIC:
        half = [[p[0] * 0.5, p[1] * 0.5] for p in side]
        result_path = half + list(reversed([[p[0], -p[1]] for p in half]))
    else:
        scaled = [[p[0] * split_length, p[1] * split_length] for p in side_flipped]
        result_path = Path2D(scaled).rot(angle)

    return Path2D(result_path).move(path[0])


def tesselation_polygon(path, side_indexes: "Sequence[int]", sides, flips: "Sequence[int]") -> list[list[float]]:
    """Distorts every side of a polygon using profile lines and indexes.

    Args:
        path: the polygon path
        side_indexes: which profile (index into *sides*) to use per polygon side
        sides: list of profile lines
        flips: list of TESSELATION_LINE_* flags, one per polygon side
    """
    assert len(path) > 2, f"Input path must be of size > 2, path={path}"
    assert len(side_indexes) == len(path), (
        f"side indexes and paths must be the same size path={len(path)} side_indexes={len(side_indexes)}"
    )

    each_line = []
    for i in range(len(side_indexes)):
        each_line.extend(
            tesselation_side_line(path=[path[i], path[(i + 1) % len(path)]], side=sides[side_indexes[i]], flip=flips[i])
        )
    return Path2D._deduplicate(each_line, closed=True)


def tesselation_drop(
    size: list[float], thickness: float = 0, outer_offset: float = 0, arc_offset: float = 0.2, arc_points: int = 10
) -> PyOpenSCAD:
    """Creates a drop tesselation.

    Usage::

        tesselation_drop(size=[20, 20])

    Args:
        size: the size of the drop [x, y]
        thickness: the thickness of the wall (default 0)
        outer_offset: extra outward offset for layout (default 0)
        arc_offset: how wide the arc should be (default 0.2)
        arc_points: how many points on the arc (default 10)
    """
    assert size != 0, "Need to have a size specified"
    arc1 = shapes2d.arc(count=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]])
    arc2 = shapes2d.arc(count=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]])
    data = square_tesselation(points=[arc1, arc2], size=size, thickness=thickness, outer_offset=outer_offset)
    return region(data)


def tesselation_leaf(size: float) -> PyOpenSCAD:
    """A solid leaf for use with tesselations.

    Usage::

        tesselation_leaf(40)

    Args:
        size: size of the leaf
    """
    assert size != 0, "Need to have a size specified"
    section = size / 4
    section_height = section * math.sqrt(3) / 2
    return polygon(
        [
            [section_height * 2, 0],
            [0, section * 1],
            [0, section * 2],
            [-section_height * 2, section],
            [-section_height * 2, -section],
            [0, -section * 2],
            [0, -section * 1],
        ]
    )


def tesselation_leaf_outline_make_polygon(section_height: float, section: float) -> list[list[float]]:
    """Internal boundary path for the leaf outline."""
    return Path2D._deduplicate(
        [
            [section_height * 2, 0],
            [0, section * 1],
            [0, section * 2],
            [-section_height * 2, section],
            [-section_height * 2, -section],
            [0, -section * 2],
            [0, -section * 1],
        ],
        closed=True,
    )


def tesselation_leaf_outline_make_veins(
    calc_thickness: float, section_height: float, section: float, calc_vein_thickness: float
):
    """Internal: the leaf's veins as 2-D geometry, clipped to the leaf outline.

    Direct CSG throughout. This used to be osuse'd BOSL2 region algebra
    (offset_stroke/union/intersection), which is fatal: a failing assert inside an osuse'd
    function ABORTS THE PROCESS rather than raising, and this construction tripped one --
    see tests/repro_osuse_assert_aborts.py. stroke_path() is the native stand-in for
    offset_stroke(), and the region booleans are just `|` and `&` on shapes.
    """
    vein_base_x = -section_height * 2 + calc_thickness
    vein_side_x = calc_vein_thickness / 2
    vein_side_y = section * 2 - calc_vein_thickness
    vein_spacing = section_height * 3 / 2 / 3
    line_m = (vein_side_x - vein_base_x) / vein_side_y
    line_angle = math.degrees(math.atan(line_m))
    len_bottom_vein = math.sqrt((vein_base_x - vein_side_x) ** 2 + vein_side_y**2)
    mini_seg = len_bottom_vein / 7

    def vein(p1: list[float], p2: list[float], width: float = calc_vein_thickness):
        return stroke_path([p1, p2], width=width)

    def twig(end: list[float], angle: float):
        """One little side twig, drawn along the bottom vein then swung into place."""
        return stroke_path(
            [[mini_seg * (i + 1.2), -calc_vein_thickness / 4], end], width=calc_vein_thickness
        ).rotate(angle).translate([vein_base_x, 0])

    pieces = [
        vein([vein_base_x, 0], [section_height * 2 - calc_thickness, 0]),   # main stem
        vein([vein_base_x, 0], [vein_side_x, vein_side_y]),                 # side a
        vein([vein_base_x, 0], [-vein_side_x, -vein_side_y]),               # side b
    ]

    for i in range(4):
        x0 = section_height - section_height * 4 / 2 + vein_spacing * i
        x1 = section_height - section_height * 3 / 2 + 20 + vein_spacing * i
        pieces.append(vein([x0, 0], [x1, 15]))
        pieces.append(vein([x0, 0], [x1, -15]))

        run = mini_seg * (i + 2) + mini_seg * 3
        pieces.append(twig([run, -mini_seg * 2.5 - calc_vein_thickness / 4], 90 - line_angle))
        pieces.append(twig([run, mini_seg * 2 + calc_vein_thickness / 4], 90 - line_angle))
        pieces.append(twig([run, -mini_seg * 2], -(90 - line_angle)))
        pieces.append(twig([run, mini_seg * 2.5 + calc_vein_thickness / 4], -(90 - line_angle)))

    boundary = shapes2d.polygon(
        tesselation_leaf_outline_make_polygon(section_height=section_height, section=section)
    )
    return union_all_2d(pieces) & boundary


def tesselation_leaf_outline(
    size: float, thickness: float | None = None, with_veins: bool = False, vein_thickness: float | None = None
) -> list[list[float]]:
    """A leaf outline (region data) for use with tesselations.

    Args:
        size: size of the leaf
        thickness: thickness of the sides (default size/30)
        with_veins: include veins (default False)
        vein_thickness: how thick to make the veins (default thickness/2)
    """
    calc_thickness = thickness
    if calc_thickness is None:
        calc_thickness = size / 30
    calc_vein_thickness = vein_thickness
    if calc_vein_thickness is None:
        calc_vein_thickness = calc_thickness / 2
    section = size / 4
    section_height = section * math.sqrt(3) / 2

    outline = tesselation_leaf_outline_make_polygon(section=section, section_height=section_height)
    shape = shapes2d.polygon(outline)
    ring = shape - shapes2d.polygon(outline).offset(delta=-calc_thickness)

    if not with_veins:
        return ring

    return ring | tesselation_leaf_outline_make_veins(
        calc_thickness=calc_thickness,
        section_height=section_height,
        section=section,
        calc_vein_thickness=calc_vein_thickness,
    )


def tesselation_leaf_outline_three(
    size: float, thickness: float | None = None, with_veins: bool = False, vein_thickness: float | None = None
) -> PyOpenSCAD:
    """A leaf outline, grouped into three to make layout easier.

    Usage::

        tesselation_leaf_outline_three(40)
        tesselation_leaf_outline_three(40, with_veins=True)

    Args:
        size: size of the leaf
        thickness: thickness of the sides (default size/30)
        with_veins: include veins (default False)
        vein_thickness: how thick the veins are (default thickness/2)
    """
    assert size != 0, "Need to have a size specified"
    section = size / 4
    section_height = section * math.sqrt(3) / 2

    # `leaf` is 2-D GEOMETRY now, not ragged region data, so the three copies are three
    # ordinary transforms instead of a per-outline rebuild.
    def leaf():
        return tesselation_leaf_outline(
            size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
        )

    return (
        leaf().translate([0, -section * 3 / 2])
        | leaf().rotate(180).translate([-section_height * 2, section * 3 / 2])
        | leaf().translate([section_height * 2, section / 2])
    )


# ---------------------------------------------------------------------------
# Deltoid / half-hex / rhombi-tri-hexagonal / pegasus tilings
# ---------------------------------------------------------------------------


def deltoid_trihexagonal_tiling_get_points(pts: list[list[float]], i: int, kite: bool = False) -> list[list[float]]:
    """Internal: gets the points for one wedge of the deltoid tiling."""
    if kite:
        p_next = pts[(i + 1) % 6]
        p_prev = pts[(i + 5) % 6]
        return [
            pts[i],
            [(p_next[0] + pts[i][0]) / 2, (p_next[1] + pts[i][1]) / 2],
            [0, 0],
            [(p_prev[0] + pts[i][0]) / 2, (p_prev[1] + pts[i][1]) / 2],
        ]
    return [pts[i], pts[(i + 1) % 6], [0, 0]]


def deltoid_trihexagonal_tiling_inner_parts(pts: list[list[float]], thickness: float, kite: bool = False) -> "PyOpenSCAD":
    """Internal: native 2-D geometry for the deltoid tiling's inner wedges."""
    # Each wedge is a concentric ring (outer offset minus inner offset -- no clipping, see
    # Region.with_holes); the wedges overlap, so their union is real 2-D CSG done natively.
    geom = None
    for i in range(6):
        p = deltoid_trihexagonal_tiling_get_points(pts, i, kite)
        ring = Region.with_holes(Path2D(p).offset(delta=thickness / 10), Path2D(p).offset(delta=-thickness)).geometry()
        geom = ring if geom is None else geom | ring
    return geom


def deltoid_trihexagonal_tiling(
    size: float, thickness: float = 1, outer_offset: float = 0, kite: bool = False
) -> PyOpenSCAD:
    """A tesselation to make a nice triangle-layout hex pattern.

    Usage::

        deltoid_trihexagonal_tiling(20)
        deltoid_trihexagonal_tiling(20, kite=True)

    Args:
        size: size of the hex
        thickness: thickness of the sides (default 1)
        outer_offset: extra outward offset (default 0)
        kite: do a kite tiling (default False)
    """
    assert size != 0, "Need to have a size specified"
    width = size / 2
    height = math.sqrt(3) * width
    pts = [
        [width * 0.5, height / 2],
        [width, 0],
        [width * 0.5, -height / 2],
        [width * -0.5, -height / 2],
        [-width, 0],
        [width * -0.5, height / 2],
    ]
    outer_ring = Region.with_holes(Path2D(pts).offset(delta=outer_offset), Path2D(pts).offset(delta=-thickness)).geometry()
    inner = (
        deltoid_trihexagonal_tiling_inner_parts(pts, thickness, kite) & Path2D(pts).offset(delta=-thickness + 0.1).polygon()
    )
    return outer_ring | inner


def half_regular_hexagon(size: float, thickness: float = 1, outer_offset: float = 0) -> PyOpenSCAD:
    """A half regular hexagon for layout, based on a triangle tesselation with rotations.

    Usage::

        half_regular_hexagon(20)

    Args:
        size: size of the hex
        thickness: thickness of the sides (default 1)
        outer_offset: extra outward offset (default 0)
    """
    assert size != 0, "Need to have a size specified"
    side_length = size * math.sin(math.radians(60))
    height = side_length * (math.sqrt(3) / 2)
    pts = [[0, size / 2], [side_length / 2, size / 2 - height], [-side_length / 2, size / 2 - height]]

    # Three concentric-ring wedges that overlap at the centre; union them in native 2-D CSG.
    geom = None
    for i in range(3):
        p_i = pts[i]
        p_next = pts[(i + 1) % 3]
        p_prev = pts[(i + 2) % 3]
        poly = Path2D._deduplicate(
            [
                p_i,
                [(p_i[0] + p_next[0] * 2) / 3, (p_i[1] + p_next[1] * 2) / 3],
                [0, 0],
                [(p_i[0] * 2 + p_prev[0]) / 3, (p_i[1] * 2 + p_prev[1]) / 3],
                p_i,
            ],
            closed=True,
        )
        outer = Path2D._deduplicate(Path2D(poly).offset(delta=outer_offset))
        inner = Path2D(poly).offset(delta=-thickness)
        ring = Region.with_holes(outer, inner).geometry()
        geom = ring if geom is None else geom | ring
    return geom


def rhombi_tri_hexagonal(size: float, thickness: float = 1, outer_offset: float = 0.1) -> PyOpenSCAD:
    """A rhombitrihexagon layout tesselation, based on a triangle tesselation with rotations.

    Usage::

        rhombi_tri_hexagonal(20)

    Args:
        size: size of the hex
        thickness: thickness of the sides (default 1)
        outer_offset: extra outward offset (default 0.1)
    """
    assert size > 0, "Need to have a size specified"
    calc_size = size * 0.8
    radius = calc_size / 2
    apothem = math.cos(math.radians(30)) * radius
    inner_side_length = apothem * math.sqrt(3) / 2

    ring = circle(d=inner_side_length * 2, fn=6).offset(outer_offset) - circle(d=inner_side_length * 2, fn=6).offset(
        -thickness
    )

    petals = ring
    for i in range(6):
        outer_sq = (
            square([inner_side_length, inner_side_length + thickness], center=True)
            .translate([calc_size / 2, 0, 0])
            .rotate([0, 0, 60 * i - 30])
            .offset(outer_offset)
        )
        inner_sq = (
            square([inner_side_length, inner_side_length], center=True)
            .translate([calc_size / 2, 0, 0])
            .rotate([0, 0, 60 * i - 30])
            .offset(-thickness)
        )
        petals = petals | (outer_sq - inner_sq)

    return circle(d=size, fn=6) & petals


def tesselation_pegasus(size: list[float], thickness: float = 0, outer_offset: float = 0) -> PyOpenSCAD:
    """Pegasus tesselation to use on lids.

    Usage::

        tesselation_pegasus(size=[20, 20])
        tesselation_pegasus(size=[30, 20], thickness=0.5)

    Args:
        size: [width, length]
        thickness: thickness of the sides (default 0)
        outer_offset: extra outward offset (default 0)
    """
    assert len(size) == 2, "Need to have a size specified as two element array"
    assert size[0] > 0 and size[1] > 0, "Need to have a size specified > 0"
    assert thickness >= 0, "Need to have thickness specified"
    assert outer_offset >= 0, "Need to have outer_offset specified"

    pts_a = [
        [i[0], -i[1]]
        for i in [
            [-0.5, -0],
            [-0.131497, 0.189891],
            [-0.111942, 0.23038],
            [-0.101048, 0.273655],
            [-0.0887842, 0.316685],
            [-0.0365644, 0.30475],
            [0.0156516, 0.292797],
            [0.0678689, 0.280851],
            [0.0172526, 0.161771],
            [-0.036603, 0.0942535],
            [-0.104924, 0.0332333],
            [-0.166696, -0.0188206],
            [-0.172123, -0.107408],
            [-0.118787, -0.210899],
            [-0.121088, -0.235661],
            [-0.123389, -0.260423],
            [-0.12569, -0.285184],
            [-0.0345562, -0.301811],
            [0.0625798, -0.319535],
            [0.141772, -0.333985],
            [0.172519, -0.4],
            [0.193835, -0.333349],
            [0.493345, -0.21837],
            [0.491797, -0.170607],
            [0.469955, -0.158724],
            [0.465464, -0.119576],
            [0.443623, -0.107693],
            [0.46217, -0.0703219],
            [0.480717, -0.0329511],
            [0.499265, 0.00441975],
            [0.499512, 0.00494432],
            [0.5, 0],
        ]
    ]
    pts_b = [
        [-i[0], i[1]]
        for i in [
            [0.5, -0.0],
            [0.456143, -0.0789084],
            [0.406509, -0.123072],
            [0.365506, -0.158244],
            [0.29841, -0.12978],
            [0.27285, -0.0853574],
            [0.205624, -0.0572037],
            [0.165011, 0.0314834],
            [0.06979, 0.117951],
            [-0.0974454, 0.0612218],
            [-0.093908, -0.0578449],
            [-0.0255355, -0.0900762],
            [-0.00708426, -0.0756784],
            [0.0252447, -0.0474022],
            [0.0436957, -0.0330041],
            [0.110764, -0.115447],
            [0.0767458, -0.148258],
            [0.0311628, -0.16719],
            [-0.00285616, -0.2],
            [-0.0599237, -0.179476],
            [-0.116194, -0.156928],
            [-0.172503, -0.134443],
            [-0.178267, 0.0363945],
            [-0.178267, 0.0363945],
            [-0.325784, 0.11531],
            [-0.394859, 0.166938],
            [-0.498287, 0.220646],
            [-0.5, 0.221534],
            [-0.498991, 0.13894],
            [-0.497203, 0.131818],
            [-0.458524, -0.0222559],
            [-0.456539, -0.0],
        ]
    ]

    data = square_tesselation(points=[pts_a, pts_b], size=size, thickness=thickness, outer_offset=outer_offset)
    return region(data)
