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

# LibFile: lids_base.py
#    Shared lid building-blocks for all box types.
#
# FileSummary: Shared lid pieces for making lids.
# FileGroup: Basics

from __future__ import annotations
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2 import shapes3d
from bosl2 import shapes2d
from labels import LabelOptions, MakeLabelOptions, MakeFramedLidLabel, MakeFramelessLidLabel
from components import RegularPolygonGridDense, RegularPolygonGrid

import math
import types


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse("BOSL2/std.scad")

# ---------------------------------------------------------------------------
# Lid defaults (can be overridden at the file level by the user)
# ---------------------------------------------------------------------------

default_lid_shape_width = 12
default_lid_layout_width = 12
default_lid_aspect_ratio = 1.0
default_lid_shape_thickness = 2
default_lid_shape_rounding = 0
default_lid_shape_type = ShapeType.DENSE_HEX
default_lid_supershape_m1 = 4
default_lid_supershape_m2 = 4
default_lid_supershape_n1 = 1
default_lid_supershape_n2 = 1
default_lid_supershape_n3 = 1
default_lid_supershape_a = 1
default_lid_supershape_b = 1
default_lid_catch_type = CatchType.BUMPS_SHORT

# ---------------------------------------------------------------------------
# Helper functions (pure Python equivalents of SCAD functions)
# ---------------------------------------------------------------------------


def IsDenseShapeType(shape_type: ShapeType | None = None) -> bool:
    """Return True if *shape_type* is a 'dense' layout type."""
    t = shape_type if shape_type is not None else default_lid_shape_type
    return t in (
        ShapeType.DENSE_HEX,
        ShapeType.DENSE_TRIANGLE,
        ShapeType.DELTOID_TRIHEXAGONAL_KITE,
        ShapeType.DELTOID_TRIHEXAGONAL,
    )


def DenseShapeEdges(shape_type: ShapeType) -> int:
    """Return the number of edges on the given dense shape type."""
    return 3 if shape_type == ShapeType.DENSE_TRIANGLE else 6


# ---------------------------------------------------------------------------
# Lid mesh modules
# ---------------------------------------------------------------------------


def LidMeshDense(
    path: list[list[float]],
    lid_thickness: float,
    boundary: float,
    radius: float,
    shape_edges: int = 6,
    material_colour: str | None = None,
    inner_control: int | bool = False,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Make a dense hex/triangle mesh for a lid.

    Usage::

        LidMeshDense(path=[[0,0],[100,0],[100,50],[0,50]],
                     lid_thickness=3, boundary=10, radius=5, shape_edges=6)

    Args:
        path:           2-D path defining the mesh boundary
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        radius:         polygon radius
        shape_edges:    edges per polygon (default 6)
        material_colour: colour (default default_material_colour, unused directly
                         here -- kept for API compatibility with callers)
        inner_control:  if True, layout is driven by a children callable
                        (see RegularPolygonGridDense)
        children:       the shape to tile (e.g. ShapeByType(...)), or a
                        callable(polygon_x, polygon_y) when inner_control is True
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    width = max(x_arr) - min(x_arr)
    length = max(y_arr) - min(y_arr)

    cell_width = math.cos(math.radians(180 / shape_edges)) * radius
    rows = width / cell_width + 2
    cols = length / cell_width + 2

    grid = RegularPolygonGridDense(
        radius=radius, rows=rows, cols=cols, shape_edges=shape_edges, inner_control=inner_control, children=children
    )
    return grid.linear_extrude(height=lid_thickness + 1).translate([0, 0, -0.5])


def LidMeshHex(
    size: list[float],
    lid_thickness: float,
    boundary: float,
    radius: float,
    shape_thickness: float = 2,
    inner_control: int | bool = False,
) -> PyOpenSCAD:
    """Make a hex mesh for a lid.

    Usage::

        LidMeshHex(size=[100, 50], lid_thickness=3, boundary=10, radius=5)

    Args:
        size:           [width, length] (or [width, length, height]) of the mesh area
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        radius:         hex polygon radius
        shape_thickness: gap between hexes (default 2)
        inner_control:  driven by a children callable (default False)
    """
    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be [width, length], got {size}"
    width, length = size[0], size[1]
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    def shape_for(polygon_width: float) -> PyOpenSCAD:
        from shape_type import MakeShapeObject, ShapeByType

        return ShapeByType(MakeShapeObject(shape_type=ShapeType.DENSE_HEX, shape_width=polygon_width))

    children = (lambda i, j: shape_for(radius * 2)) if inner_control else shape_for(radius * 2)

    return LidMeshDense(
        path=square([width, length]),
        lid_thickness=lid_thickness,
        boundary=boundary,
        radius=radius,
        shape_edges=6,
        inner_control=inner_control,
        children=children,
    )


def LidMeshRepeating(
    path: list[list[float]],
    lid_thickness: float,
    boundary: float,
    layout_width: float,
    aspect_ratio: float = 1.0,
    shape_edges: int = 4,
    material_colour: str | None = None,
    inner_control: int = 0,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Make a repeating-shape mesh for a lid.

    Usage::

        LidMeshRepeating([[0,0],[50,0],[50,20],[0,20]],
                         lid_thickness=3, boundary=5, layout_width=10)

    Args:
        path:           2-D path defining the mesh boundary
        lid_thickness:  height of the lid
        boundary:       edge boundary width
        layout_width:   spacing between pattern repeats
        aspect_ratio:   dy scale factor (default 1.0)
        shape_edges:    polygon edges for layout (default 4)
        material_colour: colour (default default_material_colour, unused directly
                         here -- kept for API compatibility with callers)
        inner_control:  0=auto, 1=children callable(polygon_x, polygon_y, cols, rows),
                        2=children callable(polygon_width, polygon_length, cols, rows)
        children:       shape solid(s) to tile, or a callable per inner_control above
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    width = max(x_arr) - min(x_arr)
    length = max(y_arr) - min(y_arr)

    rows = width / layout_width + 2
    cols = length / layout_width * aspect_ratio + 2

    grid = RegularPolygonGrid(
        width=layout_width,
        rows=rows + (11 if inner_control else 1),
        cols=cols + (11 if inner_control else 1),
        spacing=0,
        shape_edges=shape_edges,
        aspect_ratio=aspect_ratio,
        inner_control=inner_control,
        space_width=width,
        space_length=length,
        children=children,
    )
    return grid.linear_extrude(height=lid_thickness + 1).translate([0, 0, -0.5])


def LidMeshBasic(
    lid_thickness: float,
    boundary: float,
    layout_width: float,
    size: list[float] | None = None,
    path: list[list[float]] | None = None,
    aspect_ratio: float = 1.0,
    dense: bool = False,
    dense_shape_edges: int = 6,
    material_colour: str | None = None,
    inner_control: int | bool = False,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Make a lid mesh using one of the known shape types.

    Provide either *size* or *path* (but not both).

    Usage::

        LidMeshBasic(size=[100, 50], lid_thickness=2, boundary=10,
                     layout_width=10, dense=True,
                     children=ShapeByType(MakeShapeObject(
                         shape_type=ShapeType.DENSE_HEX,
                         shape_thickness=2,
                         shape_width=10)))

    Args:
        lid_thickness:    height of the lid
        boundary:         edge boundary width
        layout_width:     spacing between pattern repeats
        size:             [width, length] or [width, length, height]
        path:             explicit 2-D path (alternative to size)
        aspect_ratio:     dy scale factor (default 1.0)
        dense:            use dense layout (default False)
        dense_shape_edges: edges per dense polygon (default 6)
        material_colour:  colour (default default_material_colour)
        inner_control:    layout control mode (default False/0)
        children:         tiling shape solid(s), or callable (see LidMeshDense/LidMeshRepeating)
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert size is not None or path is not None, "Must provide either size or path to LidMeshBasic"
    assert path is not None or (
        isinstance(size, (list, tuple)) and len(size) in (2, 3)
    ), f"Invalid size in LidMeshBasic, size={size}"
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    calc_layout_width = layout_width
    if calc_layout_width is None:
        calc_layout_width = default_lid_layout_width
    calc_aspect_ratio = aspect_ratio
    if calc_aspect_ratio is None:
        calc_aspect_ratio = default_lid_aspect_ratio
    # calc_path must match the classic (corner-anchored, center=false) square()'s point
    # convention -- [0,0] to [width,length] -- since the mesh grid below (RegularPolygonGrid/
    # RegularPolygonGridDense) always lays its tiles out starting near the origin regardless of
    # calc_path, and needs to line up with it. shapes2d._rect_path() is BOSL2-style (centered on
    # the origin) and would leave half the boundary untiled if used here instead.
    calc_path = [[0, 0], [size[0], 0], [size[0], size[1]], [0, size[1]]] if size is not None else path

    if dense:
        mesh = LidMeshDense(
            path=calc_path,
            lid_thickness=lid_thickness,
            boundary=boundary,
            radius=calc_layout_width / 2,
            shape_edges=dense_shape_edges,
            material_colour=material_colour,
            inner_control=inner_control,
            children=children,
        )
    else:
        mesh = LidMeshRepeating(
            path=calc_path,
            lid_thickness=lid_thickness,
            boundary=boundary,
            layout_width=calc_layout_width,
            shape_edges=4,
            aspect_ratio=calc_aspect_ratio,
            material_colour=material_colour,
            inner_control=inner_control,
            children=children,
        )

    # offset() is a 2-D op: it must run on the flat polygon before linear_extrude() lifts it to
    # 3-D, not after (calling offset() on an already-extruded solid silently yields nothing).
    border = (
        color(polygon(calc_path).offset(-boundary).linear_extrude(lid_thickness), material_colour)
        - color(polygon(calc_path).offset(-boundary - 0.02).linear_extrude(lid_thickness + 1), material_colour).translate(
            [0, 0, -0.5]
        )
    )

    bound = color(polygon(calc_path).offset(-boundary).linear_extrude(lid_thickness), material_colour)
    return (mesh | border) & bound


def internal_build_lid(lid_thickness: float, children: list, size_spacing: float | None = None) -> PyOpenSCAD:
    """Builds a lid out of a stack of pieces, carving holes so each merges cleanly.

    Unlike the original SCAD module (which used a variable children() block),
    *children* here must be a Python list: children[0] is the base lid shape
    and children[1:] are extra pieces overlaid on top of it.

    Args:
        lid_thickness: thickness of the lid
        children:      list of solids; children[0] is the base shape
        size_spacing:  spacing between pieces (default m_piece_wiggle_room)
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"
    assert isinstance(children, (list, tuple)) and len(children) >= 1, "children must be a non-empty list"

    def mask(piece: PyOpenSCAD) -> PyOpenSCAD:
        return (
            fill(piece.projection(cut=False))
            .offset(r=-size_spacing)
            .linear_extrude(height=lid_thickness + 1)
            .color("darkslategrey")
            .translate([0, 0, -0.5])
        )

    n = len(children)
    base = children[0]
    for i in range(1, n):
        base = base - mask(children[i])

    extras = None
    for i in range(1, n):
        piece = children[i]
        for j in range(i + 1, n):
            piece = piece - mask(children[j])
        extras = piece if extras is None else extras | piece

    return base if extras is None else base | extras


# ---------------------------------------------------------------------------
# Lid construction helpers
# ---------------------------------------------------------------------------


def SlidingLidFingernail(
    lid_thickness: float,
    radius: float = 6,
    finger_gap: float = 1.5,
    sphere: float = 12,
    finger_length: float = 10,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Creates a finger-nail recess for lifting a sliding lid.

    Usage::

        SlidingLidFingernail(3)

    Args:
        lid_thickness:  height of the lid
        radius:         radius of the fingernail circle (default 6)
        finger_gap:     gap for the finger (default 1.5)
        sphere:         sphere inset size (default 12)
        finger_length:  length of the finger section (default 10)
        material_colour: colour (default default_material_colour)
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    cyl_part = shapes3d.cyl(h=lid_thickness, r=radius).color(material_colour).translate([0, 0, lid_thickness / 2])

    # "sphere" is also this function's parameter name (matching the original
    # SCAD module signature), so the builtin is looked up explicitly here to
    # avoid the local-variable shadow.
    _sphere_primitive = globals()["sphere"]
    cut_box = cube([finger_length, finger_length, finger_gap]).color(material_colour).translate(
        [-finger_length / 2, -finger_length, -finger_length]
    )
    cut_sphere = _sphere_primitive(r=finger_length).color(material_colour)
    cutter = (cut_box & cut_sphere).translate([0, 0, finger_length + lid_thickness - finger_gap + 0.1])

    return cyl_part - cutter


def MakeLidTab(
    length: float, height: float, lid_thickness: float | None = None, prism_width: float = 0.75, wall_thickness: float = 2
) -> PyOpenSCAD:
    """Makes a single lid tab (for tabbed boxes).

    Usage::

        MakeLidTab(length=5, height=10, lid_thickness=2)

    Args:
        length:         length of the tab
        height:         height of the tab
        lid_thickness:  thickness of the lid (default default_lid_thickness)
        prism_width:    prism width factor (default 0.75)
        wall_thickness: wall thickness (default 2)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    base = cube([length, wall_thickness, lid_thickness])

    stalk = cube([length, wall_thickness / 2, height - wall_thickness + 0.1])
    wedge = hull(
        shapes3d.xcyl(h=length, r=0.1).translate([length / 2, wall_thickness * prism_width - 0.1, height - wall_thickness + 0.1]).shape,
        cube([length, 0.1, 0.1]).translate([0, 0, height - wall_thickness]),
        shapes3d.xcyl(h=length, r=0.1).translate([length / 2, 0.1, height - 0.1]).shape,
    )

    return (base | stalk | wedge).mirror([0, 0, 1])


def MakeTabs(
    size: list[float],
    lid_thickness: float | None = None,
    tab_length: float = 10,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Layout tabs for a tabbed box lid.

    Usage::

        MakeTabs([50, 100],
                 children=MakeLidTab(length=10, height=6))

    Args:
        size:           [width, length] (or [width, length, height]) of the box
        lid_thickness:  lid height (default default_lid_thickness)
        tab_length:     tab length (default 10)
        make_tab_width: add tabs on the width sides (default False)
        make_tab_length: add tabs on the length sides (default True)
        children:       tab geometry to place (typically MakeLidTab(...))
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), (
        f"size must be [width, length] or [width, length, height], got {size}"
    )
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"
    assert children is not None, "Must specify children (e.g. MakeLidTab(...))"

    box_width, box_length = size[0], size[1]

    shape = None

    def add(piece: PyOpenSCAD) -> None:
        nonlocal shape
        shape = piece if shape is None else shape | piece

    if make_tab_length:
        add(children.rotate([0, 0, 270]).translate([0, (box_length + tab_length) / 2, lid_thickness]))
        add(children.rotate([0, 0, 90]).translate([box_width, (box_length - tab_length) / 2, lid_thickness]))

    if make_tab_width:
        add(children.translate([(box_width - tab_length) / 2, 0, lid_thickness]))
        add(children.rotate([0, 0, 180]).translate([(box_width + tab_length) / 2, box_length, lid_thickness]))

    return shape


def MakeLidLabel(size: list[float], lid_thickness: float, text_str: str, options: LabelOptions) -> PyOpenSCAD | None:
    """Places a label on a lid at the correct position and rotation.

    Usage::

        MakeLidLabel([100, 20], lid_thickness=2, text_str="Frog",
                     options=MakeLabelOptions(text_length=50, text_scale=1.0,
                                              border=2, offset=4, radius=2,
                                              label_type=LabelType.FRAMED,
                                              full_height=True))

    Args:
        size:          [width, length] (or [width, length, height]) of the lid interior
        lid_thickness: thickness of the lid
        text_str:      text to display
        options:       :class:`~labels.LabelOptions` (from :func:`~labels.MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), (
        f"size must be [width, length] or [width, length, height], got {size}"
    )
    assert text_str is not None, "Must specify text_str"
    assert options is not None, "Must specify label options"
    assert lid_thickness > 0, f"lid_thickness must be > 0 lid_thickness={lid_thickness}"

    calc_label_type = options.label_type
    if calc_label_type is None:
        calc_label_type = default_label_type
    if calc_label_type in (
        LabelType.FRAMED,
        LabelType.FRAMED_SHORT,
        LabelType.FRAMED_SHORT_SOLID,
        LabelType.FRAMED_SOLID,
    ):
        return MakeFramedLidLabel(size=size, lid_thickness=lid_thickness, label=text_str, options=options)
    elif calc_label_type in (LabelType.FRAMELESS_ANGLE, LabelType.FRAMELESS, LabelType.FRAMELESS_SHORT):
        return MakeFramelessLidLabel(size=size, label=text_str, lid_thickness=lid_thickness, options=options)
    return None
