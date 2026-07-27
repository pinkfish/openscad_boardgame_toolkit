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

# LibFile: components.py
#    This file has all the modules needed to generate various inserts
#    for board games.  It makes the generation of the inserts simpler by
#    creating a number of useful base modules for making boxes and lids
#    of various types specific to board game inserts.  Specifically it
#    makes tabbed lids and sliding lids easily.
#
# FileSummary: Various modules to generate board game inserts.
# FileGroup: Basics

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from pythonscad import *
from bosl2.shapes3d import Bosl2Solid
from bosl2.shapes2d import Bosl2Shape2D
from base_bgtk import *
from bosl2 import shapes3d
from bosl2 import shapes2d
from bosl2 import transforms
from bosl2.paths import Path
from bosl2 import geometry
from bosl2 import masking

import math


# TODO: _bosl2 osuse handle is no longer used once HexBoxDivisions is fully migrated.
# It can be removed once confirmed no other callers remain in the codebase.
_bosl2 = osuse(BOSL2_STD_PATH)

# Magnet-slot-type constants
MAGNET_SLOT_TYPE_NONE = 0
MAGNET_SLOT_TYPE_ROUND = 1
MAGNET_SLOT_TYPE_RECT = 2

# ---------------------------------------------------------------------------
# Helper / utility functions
# ---------------------------------------------------------------------------


def PolygonRadiusFromApothem(apothem: float, shape_edges: int) -> float:
    """Find the radius of the polygon from apothem."""
    return apothem / math.cos(math.radians(180 / shape_edges)) / 2


def PolygonApothemFromRadius(radius: float, shape_edges: int) -> float:
    """Find the apothem of the polygon from radius."""
    return radius * math.cos(math.radians(180 / shape_edges)) * 2


def HoleToPosition(pos: int) -> list[float]:
    """Map an integer position index to a BOSL2-style anchor vector.

    Position map:
        0 -> FRONT
        1 -> FRONT + RIGHT
        2 -> RIGHT
        3 -> RIGHT + BACK
        4 -> BACK
        5 -> BACK + LEFT
        6 -> LEFT
        7 -> LEFT + FRONT
    """
    positions = {
        0: FRONT,
        1: [a + b for a, b in zip(FRONT, RIGHT)],
        2: RIGHT,
        3: [a + b for a, b in zip(RIGHT, BACK)],
        4: BACK,
        5: [a + b for a, b in zip(BACK, LEFT)],
        6: LEFT,
        7: [a + b for a, b in zip(LEFT, FRONT)],
    }
    return positions.get(pos, FRONT)


# ---------------------------------------------------------------------------
# Section: Components
# ---------------------------------------------------------------------------


def HexBoxDivisions(
    width: float,
    height: float,
    divisions: int = 2,
    num_sides: int = 6,
    wall_thickness: float | None = None,
    bottom_radius: float | None = None,
) -> PyOpenSCAD:
    """Creates a box with divisions inside for hex shaped tiles.

    Usage:
        HexBoxDivisions(width=100, num_sides=6, height=10, divisions=2)

    Args:
        width:          width of the box
        height:         height of the box
        divisions:      number of divisions to make (default 2)
        num_sides:      number of sides of the polygon (default 6)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        bottom_radius:  optional override for the bottom rounding radius
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness

    # NOTE: shapes2d._regular_ngon_path is a private helper; if it disappears
    # replace with: shapes2d.regular_ngon(n=num_sides, r=width/2) path call.
    hex_path = shapes2d._regular_ngon_path(num_sides, width / 2)
    hex_shape = shapes2d.polygon([[float(x), float(y)] for x, y in hex_path])

    w_div = wall_thickness / 2
    ang = 360 / divisions
    calc_bottom_radius = (
        bottom_radius
        if bottom_radius is not None
        else min(height * 3 / 4, (width - wall_thickness) / (divisions * 2))
    )

    shape = None
    for i in range(divisions):
        # Build the wedge as a native 2-D shape and shrink it by half wall-thickness.
        # Was: wedge_path / thinned_wedge point-lists fed into _bosl2.intersection().
        wedge_pts = [[0.0, 0.0]] + list(shapes2d.arc(radius=width * 2, start=i * ang, angle=ang))
        wedge_shape = shapes2d.polygon([[float(x), float(y)] for x, y in wedge_pts])
        thinned_wedge_shape = wedge_shape.offset(delta=-w_div / 2)

        # Native 2-D boolean intersection replaces _bosl2.intersection([hex_path], [thinned_wedge]).
        clipped = hex_shape & thinned_wedge_shape

        # OffsetSweep() replaces _bosl2.vnf_polyhedron(_bosl2.offset_sweep(..., bottom=_bosl2.os_circle(r))).
        # _bosl2.os_circle(r) -> rounding_bottom=r in OffsetSweep.
        piece = OffsetSweep(
            clipped,
            height=height,
            rounding_bottom=calc_bottom_radius,
        )
        shape = piece if shape is None else shape | piece

    assert shape is not None
    return shape.translate([0, 0, 2])


def RoundedBoxOnLength(size: list[float], radius: float) -> PyOpenSCAD:
    """Creates a rounded box with a nice radius on two sides (length side).

    Usage:
        RoundedBoxOnLength([30, 20, 10], 7)

    Args:
        size:   [width, length, height] of the cube
        radius: radius of the curve on the edges
    """
    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be an array of size 3, size={size}"
    width, length, height = size
    assert width > 0, f"Need width > 0 width={width}"
    assert length > 0, f"Need length > 0 length={length}"
    assert height > 0, f"Need height > 0 height={height}"
    assert radius > 0, f"Need radius > 0 radius={radius}"

    half = (length - radius * 2) / 2
    rounded = shapes3d.xcyl(length=width, radius=radius).translate([0, -half, 0]).hull(
        shapes3d.xcyl(length=width, radius=radius).translate([0, half, 0])
    ).translate([width / 2, length / 2, radius])
    cut = shapes3d.cuboid([width + 1, length + 1, radius + 1], anchor=FRONT + LEFT + BOTTOM).translate([-0.5, -0.5, radius])
    top = shapes3d.cuboid([width, length, 1], anchor=FRONT + LEFT + BOTTOM).translate([0, 0, height - 1])
    return (rounded - cut).hull( top)


def RoundedBoxAllSides(size: list[float], radius: float) -> PyOpenSCAD:
    """Creates a rounded box with all sides rounded.

    Usage:
        RoundedBoxAllSides([30, 30, 10], radius=5)

    Args:
        size:   [width, length, height] of the cube
        radius: radius of the curve on the edges
    """
    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be an array of size 3, size={size}"
    width_i, length_i, height_i = size
    assert width_i > 0, f"Need width > 0 width={width_i}"
    assert length_i > 0, f"Need length > 0 length={length_i}"
    assert height_i > 0, f"Need height > 0 height={height_i}"
    assert radius > 0, f"Need radius > 0 radius={radius}"

    corners = shapes3d.sphere(radius).translate([radius, radius, radius]).hull(
        shapes3d.sphere(radius).translate([width_i - radius, radius, radius]),
        shapes3d.sphere(radius).translate([radius, length_i - radius, radius]),
        shapes3d.sphere(radius).translate([width_i - radius, length_i - radius, radius])
    )
    
    cut = shapes3d.cuboid([width_i + 1, length_i + 1, radius + 1], anchor=FRONT + LEFT + BOTTOM).translate([-0.5, -0.5, radius])
    top = shapes3d.cuboid([width_i, length_i, 1], anchor=FRONT + LEFT + BOTTOM).translate([0, 0, height_i - 1])
    return (corners - cut).hull(top)


def RoundedBoxGrid(
    size: list[float], radius: float, rows: int, cols: int, spacing: float = 2, all_sides: bool = False
) -> PyOpenSCAD:
    """Create a grid of rounded boxes for inserting inside a box.

    Usage:
        RoundedBoxGrid([30, 20, 10], 7, rows=2, cols=1)

    Args:
        size:      [width, length, height] of the total space
        radius:    radius of the curve on the edges
        rows:      number of rows
        cols:      number of columns
        spacing:   mm between spaces (default 2)
        all_sides: round all sides (default False)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be an array of size 3, size={size}"
    width, length, height = size
    assert rows > 0, f"rows must be > 0 rows={rows}"
    assert cols > 0, f"cols must be > 0 cols={cols}"

    row_length = (width - spacing * (rows - 1)) / rows
    col_length = (length - spacing * (cols - 1)) / cols

    shape = None
    for x in range(rows):
        for y in range(cols):
            if all_sides:
                piece = RoundedBoxAllSides([row_length, col_length, height], radius=radius)
            else:
                piece = RoundedBoxOnLength([row_length, col_length, height], radius=radius)
            piece = piece.translate([x * (row_length + spacing), y * (col_length + spacing), 0])
            shape = piece if shape is None else shape | piece
    assert shape is not None
    return shape


def RegularPolygon(
    width: float,
    height: float,
    shape_edges: int,
    finger_holes: list[int] | None = None,
    finger_hole_height: float = 0,
    finger_hole_radius: float | None = None,
    rounding: float = 0,
    radius: float | None = None,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Creates a regular polygon with specific height/width and number of edges.

    Usage:
        RegularPolygon(10, 5, shape_edges=6)
        RegularPolygon(10, 5, shape_edges=6, finger_holes=[0, 3])

    Args:
        width:               total width (apothem * 2)
        height:              extrusion height
        shape_edges:         number of polygon edges
        finger_holes:        list of edge indices to add finger holes (default [])
        finger_hole_height:  z-offset for finger holes (default 0)
        finger_hole_radius:  radius of finger holes (default auto)
        rounding:            edge rounding (default 0)
        radius:              explicit radius override (default None)
        children:            optional child solid(s) to append
    """
    if finger_holes is None:
        finger_holes = []

    assert width > 0, f"width must be > 0 width={width}"
    assert height > 0, f"height must be > 0 height={height}"
    assert shape_edges > 0, f"shape_edges must be > 0 shape_edges={shape_edges}"

    rotate_deg = (180 / shape_edges + 90) if (shape_edges % 2) == 1 else (45 if shape_edges == 4 else 0)

    calc_radius = radius
    if calc_radius is None:
        calc_radius = PolygonRadiusFromApothem(width, shape_edges)
    calc_width = width
    if calc_width is None:
        calc_width = PolygonApothemFromRadius(calc_radius, shape_edges)
    side_length = width * math.tan(math.radians(180 / shape_edges)) / 2
    calc_finger_hole_radius = finger_hole_radius
    if calc_finger_hole_radius is None:
        calc_finger_hole_radius = side_length * 9 / 10

    poly2d = shapes2d.regular_ngon(sides=shape_edges, outer_radius=calc_radius, rounding=rounding)
    shape = poly2d.linear_extrude(height=height).rotate([0, 0, rotate_deg])

    degree = 360 / shape_edges
    for fh in finger_holes:
        x = calc_width / 2 * math.cos(math.radians(degree * fh + rotate_deg + degree / 2))
        y = calc_width / 2 * math.sin(math.radians(degree * fh + rotate_deg + degree / 2))
        hole = shapes3d.cyl(
            radius=calc_finger_hole_radius,
            height=max(height + calc_finger_hole_radius, calc_finger_hole_radius * 2),
            rounding=calc_finger_hole_radius,
            anchor=BOTTOM,
        ).translate([x, y, finger_hole_height])
        shape = shape | hole.shape

    if children is not None:
        shape = shape | children
    return shape


def CylinderWithIndents(
    radius: float | None,
    height: float | None,
    d: float | None = None,
    r: float | None = None,
    h: float | None = None,
    finger_holes: list[float] | None = None,
    finger_hole_height: float = 0,
    finger_hole_radius: float | None = None,
    cyl_fn: int | None = None,
    anchor: list[int] | None = None,
    children: PyOpenSCAD | None = None,
) -> "PyOpenSCAD | shapes3d.Bosl2Solid":
    """Makes a cylinder with optional finger-hole indents at specified angles.

    Usage:
        CylinderWithIndents(15, 10, finger_holes=[30, 210])

    Args:
        radius:             radius of the cylinder
        height:             height of the cylinder
        d:                  diameter (alternative to radius)
        r:                  radius alias
        h:                  height alias
        finger_holes:       list of angles for finger holes (default [])
        finger_hole_height: z-offset from bottom (default 0)
        finger_hole_radius: radius of the finger holes (default auto)
        cyl_fn:             $fn value for the cylinder (default None)
        anchor:             BOSL2 anchor (default BOTTOM)
        children:           optional child solid(s) to append
    """
    if finger_holes is None:
        finger_holes = []
    if anchor is None:
        anchor = BOTTOM

    assert (radius is not None and radius > 0) or (d is not None and d > 0) or (r is not None and r > 0), (
        f"radius must be != None && > 0. radius={radius} r={r} d={d} h={h}"
    )
    assert (height is not None and height > 0) or (h is not None and h > 0), f"height must be > 0. height={height}"

    calc_height = height if (height is not None and height > 0) else h
    calc_radius = radius if (radius is not None and radius > 0) else (d / 2 if (d is not None and d > 0) else r)
    assert calc_height is not None and calc_radius is not None  # enforced by the asserts above

    if cyl_fn is not None:
        shape = shapes3d.cyl(radius=calc_radius, height=calc_height, anchor=anchor, fn=cyl_fn)
    else:
        shape = shapes3d.cyl(radius=calc_radius, height=calc_height, anchor=anchor)

    if children is not None:
        shape = shape | children

    calc_finger_hole_radius = finger_hole_radius
    if calc_finger_hole_radius is None:
        calc_finger_hole_radius = calc_radius / 3
    for fh in finger_holes:
        x = calc_radius * math.cos(math.radians(fh))
        y = calc_radius * math.sin(math.radians(fh))
        hole = shapes3d.cyl(
            radius=calc_finger_hole_radius,
            height=calc_height + calc_finger_hole_radius * 2,
            anchor=BOTTOM,
            rounding=calc_finger_hole_radius,
        ).translate([x, y, finger_hole_height])
        shape = shape | hole

    return shape


def CuboidWithIndentsBottom(
    size: list[float],
    finger_holes: list[int] | None = None,
    finger_positions: list[list[float]] | None = None,
    finger_hole_height: float = 0,
    finger_hole_radius: float | None = None,
    rounding: float | None = None,
    chamfer: float | None = None,
    edges: list | None = None,
    anchor: list[int] | None = None,
    children: PyOpenSCAD | None = None,
) -> "PyOpenSCAD | shapes3d.Bosl2Solid":
    """Makes a cuboid with finger-hole indents on specified sides, anchored at the bottom.

    Usage:
        CuboidWithIndentsBottom([15, 10, 10], finger_holes=[1, 5], finger_hole_radius=3)
        CuboidWithIndentsBottom([15, 10, 10], finger_holes=[0, 4], finger_hole_radius=3)
        CuboidWithIndentsBottom([15, 10, 10], finger_holes=[0, 4], rounding=2,
                                finger_hole_radius=3, edges=["FRONT+RIGHT", "FRONT+LEFT"])

    Position map for finger_holes:
        0=FRONT, 1=FRONT+RIGHT, 2=RIGHT, 3=RIGHT+BACK,
        4=BACK,  5=BACK+LEFT,   6=LEFT,  7=LEFT+FRONT

    Args:
        size:               [x, y, z] size of the cuboid
        finger_holes:       list of position indices (default [])
        finger_positions:   explicit BOSL2 positions (overrides finger_holes)
        finger_hole_height: z-offset from bottom (default 0)
        finger_hole_radius: radius of the finger holes (default auto)
        rounding:           rounding on cuboid edges
        chamfer:            chamfer on cuboid edges
        edges:              which edges to apply rounding/chamfer to
        anchor:             BOSL2 anchor (default BOTTOM)
        children:           optional child solid(s) to append at every indent position
    """
    if finger_holes is None:
        finger_holes = []
    if finger_positions is None:
        finger_positions = []
    if anchor is None:
        anchor = BOTTOM

    assert len(size) == 3, f"len of size must be 3 len(size)={len(size)}"
    assert size[0] > 0, f"size[0] must be > 0 size={size}"
    assert size[1] > 0, f"size[1] must be > 0 size={size}"
    assert size[2] > 0, f"size[2] must be > 0 size={size}"
    assert (chamfer is None or chamfer == 0 or rounding is None or rounding == 0) or edges is not None, (
        f"edges must be set if chamfer or rounding > 0 chamfer={chamfer} rounding={rounding} edges={edges}"
    )

    calc_finger_hole_radius = finger_hole_radius
    if calc_finger_hole_radius is None:
        calc_finger_hole_radius = min(size[0], size[1]) * 3 / 4
    poses = finger_positions if len(finger_positions) > 0 else [HoleToPosition(x) for x in finger_holes]
    calc_edges = edges if edges is not None else "ALL"

    shape = shapes3d.cuboid(size, anchor=anchor, rounding=rounding, edges=calc_edges, chamfer=chamfer)
    # BOSL2 cuboid anchors are bounding-box points regardless of rounding, so the
    # anchor point in the cuboid's own (possibly already-anchored) frame is
    # (pos - anchor) * size / 2 component-wise.
    for pos in poses:
        anchor_point = [(pos[i] - anchor[i]) * size[i] / 2 for i in range(3)]
        bump = shapes3d.cyl(
            radius=calc_finger_hole_radius,
            height=size[2] + calc_finger_hole_radius * 2,
            anchor=BOTTOM,
            rounding=calc_finger_hole_radius,
        ).translate(
            [
                anchor_point[0],
                anchor_point[1],
                anchor_point[2] + finger_hole_height - size[2] / 2,
            ]
        )
        shape = shape | bump
        if children is not None:
            shape = shape | children
    return shape


def RegularPolygonGrid(
    width: float,
    rows: float,
    cols: float,
    spacing: float = 2,
    shape_edges: int = 6,
    aspect_ratio: float = 1.0,
    inner_control: int = 0,
    space_width: float | None = None,
    space_length: float | None = None,
    children: Bosl2Shape2D | Callable | None = None,
) -> Bosl2Shape2D:
    """Lays out a grid of polygons, handling spacing.  Children supply the actual shape.

    Usage:
        RegularPolygonGrid(width=10, rows=2, cols=1, spacing=2,
            children=RegularPolygon(width=10, height=5, shape_edges=6))

    Note: the original SCAD module supports a client-controlled layout mode
    driven by the $polygon_x/$polygon_y special variables. Since Python has
    no equivalent dynamic-scoping mechanism, *children* must be a callable
    when inner_control is 1 or 2 instead of a plain solid:
        inner_control == 1: children(polygon_x, polygon_y, grid_cols, grid_rows)
        inner_control == 2: children(polygon_width, polygon_length, grid_cols, grid_rows)
    For inner_control == 0 (the default), children may be a plain solid or a
    callable(polygon_x, polygon_y).

    Args:
        width:         apothem * 2 of the polygon
        rows:          number of rows
        cols:          number of columns
        spacing:       spacing between shapes (default 2)
        shape_edges:   polygon edge count (default 6)
        aspect_ratio:  dy scale factor (default 1.0)
        inner_control: 0=auto layout, 1=client uses polygon_x/polygon_y,
                       2=client uses space_width/space_length
        space_width:   used when inner_control==2
        space_length:  used when inner_control==2
        children:      solid(s) (or callable, see above) to place at each grid position
    """
    assert children is not None, "children must be given"
    assert rows > 0, "rows must be > 0"
    assert cols > 0, "cols must be > 0"
    assert width > 0, "width must be > 0"

    apothem = width / 2
    radius = apothem / math.cos(math.radians(180 / shape_edges))

    dx = (apothem + radius + spacing) if (shape_edges % 2) == 1 else (apothem * 2 + spacing)
    if (shape_edges % 2) == 0:
        dy = (radius * 2 + spacing) if ((shape_edges // 2) % 2) == 1 else (apothem * 2 + spacing)
    else:
        dy = abs(2 * apothem * math.sin(math.radians(((shape_edges - 1) / (shape_edges * 2)) * 360))) * 2 + spacing
    dy *= aspect_ratio
    dx_y = 0
    offset_y = (apothem + radius) / 2 if (shape_edges % 2) == 1 else apothem
    if (shape_edges % 2) == 0:
        offset_x = radius if ((shape_edges // 2) % 2) == 1 else apothem
    else:
        offset_x = abs(2 * apothem * math.sin(math.radians(((shape_edges - 1) / (shape_edges * 2)) * 360)))

    if inner_control == 2:
        assert callable(children), (
            "children must be callable(space_width, space_length, cols, rows) when inner_control == 2"
        )
        return children(space_width, space_length, cols, rows)

    shape = None
    for i in range(int(rows)):
        for j in range(int(cols)):
            if inner_control == 1:
                assert callable(children), (
                    "children must be callable(polygon_x, polygon_y, cols, rows) when inner_control == 1"
                )
                piece = children(i, j, cols, rows)
            else:
                piece = children(i, j) if callable(children) else children
                piece = piece.translate([i * dy + offset_x - radius, j * dx + i * dx_y + offset_y - radius, 0])
            shape = piece if shape is None else shape | piece
    assert shape is not None
    return shape


def RegularPolygonGridDense(
    radius: float,
    rows: float,
    cols: float,
    shape_edges: int = 6,
    inner_control: int | bool = False,
    children: Bosl2Shape2D| Callable | None = None,
) ->  Bosl2Shape2D:
    """Lays out a dense (space-filling) grid for triangles and hexagons.

    Usage:
        RegularPolygonGridDense(radius=10, rows=3, cols=2,
            children=RegularPolygon(width=10, height=5, shape_edges=6))

    Note: like RegularPolygonGrid, when inner_control is True, *children*
    must be a callable(polygon_x, polygon_y) instead of a plain solid.

    Args:
        radius:        radius of each polygon (center to edge)
        rows:          number of rows
        cols:          number of columns
        shape_edges:   polygon edge count (default 6; supports 3 or 6)
        inner_control: if True, client controls layout via a children callable
        children:      solid(s) (or callable, see above) to place at each grid position
    """
    assert children is not None, "children must be given"
    assert rows > 0, f"rows must be > 0, rows={rows}"
    assert cols > 0, f"cols must be > 0, cols={cols}"
    assert radius > 0, f"radius must be > 0, radius={radius}"

    shape = None

    if shape_edges == 6:
        apothem = radius * math.cos(math.radians(180 / shape_edges))
        dx = apothem
        dy = 0.75 * (radius + radius)
        for i in range(int(rows)):
            for j in range(int(cols)):
                if inner_control:
                    assert callable(children), (
                        "children must be callable(polygon_x, polygon_y) when inner_control is True"
                    )
                    piece = children(i, j)
                else:
                    piece = children() if callable(children) else children
                    x = i * dy - radius
                    y = ((j * 2 + 1) * dx if (i % 2) == 0 else j * 2 * dx) - radius
                    piece = piece.translate([x, y, 0])
                shape = piece if shape is None else shape | piece
    elif shape_edges == 3:
        side_length = radius * math.sqrt(3)
        triangle_height = math.sqrt(3) * side_length / 2
        dx = side_length
        dy = triangle_height
        for i in range(int(rows)):
            for j in range(int(cols)):
                if inner_control:
                    assert callable(children), (
                        "children must be callable(polygon_x, polygon_y) when inner_control is True"
                    )
                    piece = children(i, j)
                else:
                    piece = children() if callable(children) else children
                    piece = piece.translate([i * dy - radius, j * dx - radius, 0])
                shape = piece if shape is None else shape | piece
    assert shape is not None
    return shape


def HexGridWithCutouts(
    rows: int,
    cols: int,
    height: float,
    spacing: float,
    tile_width: float,
    push_block_height: float = 0,
    wall_thickness: float = 2,
    inner_control: bool = False,
) -> Bosl2Shape2D:
    """Creates a hex grid with cutouts for fitting hex tiles inside a box.

    Usage:
        HexGridWithCutouts(rows=4, cols=3, height=10, spacing=0,
                           push_block_height=1, tile_width=29)

    Args:
        rows:              rows in the grid
        cols:              columns in the grid
        height:            height of the grid
        spacing:           space between tiles
        tile_width:        width of each tile
        push_block_height: height of push-block (default 0)
        wall_thickness:    wall thickness (default 2)
        inner_control:     client-controlled layout (default False)
    """
    assert rows > 0, f"rows must be > 0, rows={rows}"
    assert cols > 0, f"cols must be > 0 cols={cols}"
    assert spacing >= 0, f"spacing must be >= 0 spacing={spacing}"
    assert height > 0, f"height must be > 0 height={height}"
    assert tile_width > 0, f"tile_width must be > 0 tile_width={tile_width}"

    width = tile_width
    apothem = width / 2
    radius = apothem / math.cos(math.radians(180 / 6))

    bound = shapes2d.rect(
        [rows * (radius * 2 + spacing), cols * (apothem * 2 + spacing)], anchor=FRONT + LEFT
    ).translate([0, 0])

    cell = RegularPolygon(width=width, height=10 + height, shape_edges=6)
    if push_block_height > 0:
        cell = cell - RegularPolygon(width=15, height=push_block_height, shape_edges=6)

    cell = cell | shapes3d.cuboid([radius, 10, 35], anchor=BOT).translate([0, apothem, 0])
    for sx, sy in ((1, -1), (1, 1), (-1, -1), (-1, 1)):
        cell = cell | shapes3d.cuboid([radius + wall_thickness, 15, radius * 2], anchor=BOT, rounding=3).translate(
            [sx * radius + 1, sy * apothem, -6]
        )

    grid = RegularPolygonGrid(
        width=width,
        rows=rows,
        cols=cols,
        spacing=0,
        shape_edges=6,
        inner_control=inner_control,
        children=cell,
    ).translate([radius, tile_width / 2, 0])

    return bound & grid


def FingerHoleWall(
    radius: float,
    height: float,
    depth_of_hole: float = 6,
    rounding_radius: float = 3,
    orient: list[float] | None = None,
    spin: float = 0,
    material_colour: str | None = None,
    rounding_edge: float = 0,
    round_front: bool = True,
    round_back: bool = True,
) -> Bosl2Solid:
    """Creates a finger-hole cutout with rounded edges for a wall.

    Usage:
        FingerHoleWall(10, 20)
        FingerHoleWall(10, 9)

    Args:
        radius:          radius of the finger hole
        height:          height of the finger hole
        depth_of_hole:   depth of the cut through the wall (default 6)
        rounding_radius: rounding at the top of the wall (default 3)
        orient:          BOSL2 orientation (default UP)
        spin:            BOSL2 spin (default 0)
        material_colour: colour of the material (default default_material_colour, unused
                          directly here -- kept for API compatibility with callers)
        rounding_edge:   rounding at the wall edge (default 0)
        round_front:     round the front edge (default True)
        round_back:      round the back edge (default True)
    """
    if orient is None:
        orient = TOP
    if material_colour is None:
        material_colour = default_material_colour

    assert radius > 0, f"Radius must be > 0, radius={radius}"
    assert height > 0, f"Height must be > 0, height={height}"
    assert rounding_edge >= 0, f"rounding_edge must be >= 0, rounding_edge={rounding_edge}"

    tmat = transforms.reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1])

    if height >= radius + rounding_radius:
        top_height = radius * 2 - height
        middle_height = radius - top_height
        # Native 2-D booleans (clipper-backed, effectively free) composing the same profile
        # the old interpreted-BOSL2 region math built in ~2.6s, then OffsetSweep() (Manifold
        # CSG) in place of the interpreted offset_sweep() -- same geometry, seconds faster
        # per call. Anchor math is inlined: square(center=True) centers both axes, so
        # anchor=TOP becomes a -h/2 shift, circle anchors become a -+r shift.
        slot = shapes2d.square([radius * 2, middle_height], center=True).translate([0, height / 2 - middle_height / 2])
        shoulders = (
            shapes2d.square([radius * 2 + rounding_radius * 2, rounding_radius], center=True).translate(
                [0, rounding_radius / 2]
            )
            - shapes2d.circle(radius=rounding_radius, fn=32).translate([radius + rounding_radius, rounding_radius])
            - shapes2d.circle(radius=rounding_radius, fn=32).translate([-radius - rounding_radius, rounding_radius])
        )
        profile = slot | shoulders | shapes2d.circle(radius=radius, fn=64).translate([0, radius])
        shape = (
            OffsetSweep(
                profile,
                height=depth_of_hole,
                rounding_bottom=-rounding_edge if round_front else 0,
                rounding_top=-rounding_edge if round_back else 0,
            )
            .rotate([270, 0, 0])
            .translate([0, -depth_of_hole / 2, height])
        )
    else:
        tangents = geometry.circle_circle_tangents(
            rounding_radius,
            [radius + rounding_radius, -rounding_radius],
            radius,
            [0, -height + radius],
        )
        top_polygon = [
            tangents[3][1],
            tangents[3][0],
            [tangents[3][0][0] + 0.1, 0],
            [tangents[3][1][0], 0],
        ]

        # Native 2-D booleans in place of the interpreted-BOSL2 region math (see the `if`
        # branch above). Point-list pieces (the tangent quads) become native polygon()s;
        # hull_region becomes a native 2-D hull(); mirrors across the Y axis are native
        # mirror([1, 0, 0]) on the built 2-D geometry.
        def _poly(pts) -> Bosl2Shape2D:
            return shapes2d.polygon([[float(u), float(v)] for u, v in pts])

        top_shape = _poly(top_polygon).hull(_poly(Path(top_polygon).mirror([1, 0])))
        side_shape = (
            (
                shapes2d.square([rounding_radius, rounding_radius], center=True).translate(
                    [-rounding_radius / 2, rounding_radius / 2]
                )
                - shapes2d.circle(radius=rounding_radius, fn=64)
            ).translate([radius + rounding_radius, -rounding_radius])
        ) - _poly(
            [
                tangents[3][1],
                tangents[3][0],
                [tangents[3][0][0], height - radius * 2],
                [tangents[3][1][0], height - radius * 2],
            ]
        )
        middle_shape = shapes2d.circle(radius=radius, fn=32).translate([0, -height + radius])
        profile = shapes2d.square([radius * 2 + rounding_radius * 2, height], center=True).translate([0, -height / 2]) & (
            top_shape | middle_shape | side_shape | side_shape.mirror([1, 0, 0])
        )
        shape = (
            OffsetSweep(
                profile,
                height=depth_of_hole,
                rounding_bottom=-rounding_edge if round_front else 0,
                rounding_top=-rounding_edge if round_back else 0,
            )
            .rotate([90, 0, 0])
            .translate([0, depth_of_hole / 2, height])
        )

    return Bosl2Solid(shape.multmatrix(tmat))


def CornerCatch(
    radius: float,
    height: float,
    depth_of_hole: float = 6,
    rounding_radius: float = 3,
    orient: list[float] | None = None,
    spin: float = 0,
    material_colour: str | None = None,
    rounding_edge: float = 0,
    round_front: bool = True,
    round_back: bool = True,
    round_corner_back: bool = True,
) -> Bosl2Solid:
    """Round-over on the corner for a catch, making it smooth.

    Usage:
        CornerCatch(radius=2, height=5)
        CornerCatch(radius=2, height=5, rounding_edge=1)

    Args:
        radius:           radius of the hole
        height:           height of the wall
        depth_of_hole:    depth of the cut through the wall (default 6)
        rounding_radius:  rounding at the top (default 3)
        orient:           BOSL2 orientation (default UP)
        spin:             BOSL2 spin (default 0)
        material_colour:  colour (default default_material_colour)
        rounding_edge:    edge rounding amount (default 0)
        round_front:      round the front edge (default True)
        round_back:       round the back edge (default True)
        round_corner_back: round the back corner (default True)
    """
    if orient is None:
        orient = TOP
    if material_colour is None:
        material_colour = default_material_colour

    tmat = transforms.reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1])

    wall_a = (
        FingerHoleWall(
            radius=radius,
            height=height,
            depth_of_hole=depth_of_hole,
            rounding_edge=rounding_edge,
            round_front=round_back,
            round_back=round_front,
        )
        .color(material_colour)
        .mirror([0, 0, 1])
        .translate([rounding_radius / 2, 0, 0])
    )
    wall_b = (
        FingerHoleWall(
            radius=radius,
            height=height,
            depth_of_hole=depth_of_hole,
            rounding_edge=rounding_edge,
            round_front=round_front,
            round_back=round_back,
            spin=90,
        )
        .color(material_colour)
        .mirror([0, 0, 1])
        .translate([0, rounding_radius / 2, 0])
    )
    cutter = shapes3d.cuboid([depth_of_hole, depth_of_hole, height]).color(material_colour).shape
    notch = ((wall_a | wall_b) - cutter).multmatrix(tmat)

    base = shapes3d.cuboid([depth_of_hole, depth_of_hole, height], anchor=BOTTOM)
    if round_corner_back and rounding_edge > 0:
        base = base.edge_profile(
            [BOTTOM + FRONT, BOTTOM + LEFT], children=Path(masking.mask2d_roundover(rounding_edge)).yflip()
        )
        base = base.corner_profile([BOTTOM + FRONT + LEFT], r=depth_of_hole / 2)
    elif rounding_edge > 0:
        base = base.edge_profile(
            [BOTTOM + BACK, BOTTOM + RIGHT], children=Path(masking.mask2d_roundover(rounding_edge)).yflip()
        )
        base = base.corner_profile([BOTTOM + BACK + RIGHT], r=depth_of_hole / 2)
    base = base.color(material_colour).mirror([0, 0, 1])

    return notch | base.shape


def FingerHoleBase(
    radius: float,
    height: float,
    rounding_radius: float = 3,
    wall_thickness: float | None = None,
    orient: list[float] | None = None,
    spin: float = 0,
) -> Bosl2Solid:
    """Creates a hole in the floor of a box with rounding for picking up cards/pieces.

    Usage:
        FingerHoleBase(10, 20)
        FingerHoleBase(10, 20, rounding_radius=7)

    Args:
        radius:          radius of the hole
        height:          height of the wall
        rounding_radius: rounding at the top of the hole (default 3)
        wall_thickness:  offset inward from wall (default default_wall_thickness)
        orient:          BOSL2 orientation (default UP)
        spin:            BOSL2 spin (default 0)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if orient is None:
        orient = TOP

    assert height > 0, f"Need height > 0, height={height}"
    assert radius > 0, f"Need radius > 0, radius={radius}"

    tmat = transforms.reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1])

    cyl_part = shapes3d.cyl(radius=radius, height=height, anchor=TOP + LEFT, fn=64).translate([0, wall_thickness / 2, 0])

    path = shapes2d.rect_path(
        [radius * 2, wall_thickness + 1],
        rounding=[-rounding_radius, -rounding_radius, 0, 0],
        anchor=TOP + LEFT,
    )
    sweep_part = (
        PolygonPrism(path, h=wall_thickness + 0.02, rounding_top=-wall_thickness / 2)
        .rotate([90, 0, 0])
        .translate([0, wall_thickness / 2 + 0.01, 0])
    )

    cuboid_part = (
        shapes3d.cuboid(
            [height, radius * 2, wall_thickness],
            rounding=-wall_thickness / 2,
            anchor=TOP + LEFT,
            fn=32,
            edges=[FRONT + TOP, TOP + BACK],
        )
        .rotate([90, 90, 0])
        .translate([radius, -wall_thickness / 2 - 0.01, 0])
    )

    group = (cyl_part | sweep_part | cuboid_part).translate([-radius, -wall_thickness / 2, height])
    return group.multmatrix(tmat)


# ---------------------------------------------------------------------------
# Section: Curves  — space-filling curves for lids and decorative surfaces
# ---------------------------------------------------------------------------


def HilbertCurve(order: int, size: float, line_thickness: float = 20, smoothness: int = 32) -> PyOpenSCAD:
    """Generates a 2-D Hilbert curve for use on lids and other surfaces.

    Usage:
        HilbertCurve(3, 100)

    Args:
        order:          recursion depth (3 is a reasonable default)
        size:           bounding square size
        line_thickness: thickness of the curve lines (default 20)
        smoothness:     smoothness / $fn of the curve (default 32)
    """
    assert order > 0, f"Need order > 0, order={order}"
    assert size > 0, f"Need size > 0, size={size}"

    def topline(n: int) -> PyOpenSCAD:
        if n > 0:
            return topline(n - 1).scale([0.5, 0.5])
        return hull(
            shapes2d.circle(diameter=line_thickness).translate([-size / 2, size / 2]),
            shapes2d.circle(diameter=line_thickness).translate([size / 2, size / 2]),
        )

    def leftline(n: int) -> PyOpenSCAD:
        if n > 0:
            return leftline(n - 1).translate([-size, 0]).scale([0.5, 0.5])
        return hull(
            shapes2d.circle(diameter=line_thickness).translate([-size / 2, size / 2]),
            shapes2d.circle(diameter=line_thickness).translate([-size / 2, -size / 2]),
        )

    def rightline(n: int) -> PyOpenSCAD:
        if n > 0:
            return rightline(n - 1).translate([size, 0]).scale([0.5, 0.5])
        return hull(
            shapes2d.circle(diameter=line_thickness).translate([size / 2, size / 2]),
            shapes2d.circle(diameter=line_thickness).translate([size / 2, -size / 2]),
        )

    def hilbert(n: int) -> PyOpenSCAD:
        if n > 0:
            return (
                hilbert(n - 1).scale([0.5, 0.5]).translate([size / 2, size / 2])
                | hilbert(n - 1).scale([0.5, 0.5]).translate([-size / 2, size / 2])
                | hilbert(n - 1).scale([0.5, 0.5]).rotate([0, 0, 90]).translate([size / 2, -size / 2])
                | hilbert(n - 1).scale([0.5, 0.5]).rotate([0, 0, -90]).translate([-size / 2, -size / 2])
                | topline(n)
                | leftline(n)
                | rightline(n)
            )
        return (
            hull(
                shapes2d.circle(diameter=line_thickness).translate([size / 2, size / 2]),
                shapes2d.circle(diameter=line_thickness).translate([size / 2, -size / 2]),
            )
            | hull(
                shapes2d.circle(diameter=line_thickness).translate([-size / 2, size / 2]),
                shapes2d.circle(diameter=line_thickness).translate([-size / 2, -size / 2]),
            )
            | hull(
                shapes2d.circle(diameter=line_thickness).translate([-size / 2, size / 2]),
                shapes2d.circle(diameter=line_thickness).translate([size / 2, size / 2]),
            )
        )

    return hilbert(order)


# ---------------------------------------------------------------------------
# Section: Magnets — slots for embedding magnets into prints
# ---------------------------------------------------------------------------


def MagnetSlot(
    size: list[float],
    magnet_type: int,
    spin: float = 0,
    orient: list[float] | None = None,
    anchor: list[int] | None = None,
) -> "PyOpenSCAD | shapes3d.Bosl2Solid":
    """Creates a slot for a magnet of a given size and type.

    Usage:
        MagnetSlot(size=[10, 10, 2], magnet_type=MAGNET_SLOT_TYPE_ROUND)
        MagnetSlot(size=[10, 10, 2], magnet_type=MAGNET_SLOT_TYPE_RECT)

    Args:
        size:        [width, length, height] of the magnet
        magnet_type: MAGNET_SLOT_TYPE_ROUND or MAGNET_SLOT_TYPE_RECT
        spin:        BOSL2 spin (default 0)
        orient:      BOSL2 orientation (default UP)
        anchor:      BOSL2 anchor (default CENTER)
    """
    if orient is None:
        orient = TOP
    if anchor is None:
        anchor = CENTER

    assert magnet_type in (MAGNET_SLOT_TYPE_ROUND, MAGNET_SLOT_TYPE_RECT), (
        f"Invalid magnet type, magnet_type={magnet_type}"
    )
    assert isinstance(size, (list, tuple)) and len(size) == 3 and size[0] > 0 and size[1] > 0 and size[2] > 0, (
        f"Invalid magnet size, size={size}"
    )

    if magnet_type == MAGNET_SLOT_TYPE_ROUND:
        shape = (
            shapes3d.cyl(diameter=size[1], height=size[2])
            | shapes3d.cuboid([size[0] - size[1] / 2, size[1], size[2]]).translate([-(size[0] / 2 - size[1] / 4), 0, 0])
        ).translate([size[0] / 2 - size[1] / 2, 0, 0])
    else:
        shape = shapes3d.cuboid(size)

    tmat = transforms.reorient(anchor=anchor, spin=spin, orient=orient, size=size)
    return shape.multmatrix(tmat)
