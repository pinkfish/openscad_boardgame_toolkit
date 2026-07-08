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

# LibFile: slipover_path_box.py
#    Slipover box pieces for the slipover boxes with polygon outline.
#
# FileSummary: Slipover box pieces for the slipover boxes with polygon outline.
# FileGroup: Boxes

from __future__ import annotations
import copy
import types

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from components import FingerHoleWall
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, IsDenseShapeType, DenseShapeEdges
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from cap_box_polygon import PolygonBoxLidCatch, _segment_angle
from bosl2 import paths
from bosl2 import rounding


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse("BOSL2/std.scad")


def FingerHoleWallSegmentCutout(
    path: list[list[float]], height: float, radius: float, depth: float, finger_catch: CatchType
) -> PyOpenSCAD | None:
    """Makes a single finger-hole segment for use in the slipover box wall.

    Usage::

        FingerHoleWallSegmentCutout([[0, 0], [50, 50]], radius=5, height=7, depth=6, finger_catch=CatchType.ALL)

    Args:
        path:    the path to generate for (exactly 2 points / one line segment)
        height:  the height of the finger hole
        radius:  the radius of the rounding on the finger hole
        depth:   the thickness of the walls
        finger_catch: the type of catch to use and where to put them
    """
    assert len(path) == 2, f"Path must be exactly 2 elements long path_length={len(path)}"
    split_length = paths.path_length(path)
    normal = paths.path_normals(path)
    vec_m = abs(path[0][0] - path[1][0]) / abs(path[0][1] - path[1][1]) if path[0][1] != path[1][1] else float("inf")

    qualifies = (
        finger_catch == CatchType.ALL
        or (finger_catch == CatchType.LONG and vec_m > 1000000)
        or (finger_catch == CatchType.SHORT and vec_m < 0.01)
    )
    if not (qualifies and split_length > radius * 3):
        return None

    pts = paths.path_cut_points(path=path, cutdist=[split_length / 2])
    angle = _segment_angle(normal)
    return (
        FingerHoleWall(radius=radius, height=height, depth_of_hole=depth)
        .rotate([0, 0, angle])
        .rotate([0, 180, 90])
        .translate([pts[0][0][0], pts[0][0][1], height - 0.01])
    )


def MakePathBoxWithSlipoverLid(
    path: list[list[float]],
    height: float,
    children: "list | None" = None,
    wall_thickness: float | None = None,
    foot: float = 0,
    size_spacing: float | None = None,
    wall_height: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Makes the inside of a polygon slipover box.

    This will take a second lid that slides over the outside of the box.
    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakePathBoxWithSlipoverLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10)

    Args:
        path:           the path for the bottom of the box (>= 3 points)
        height:         outside height of the box
        children:       list of solids/callables to carve inside the box
        wall_thickness: wall thickness (default default_wall_thickness)
        foot:           how big the foot around the bottom should be (default 0)
        size_spacing:   wiggle room (default m_piece_wiggle_room)
        wall_height:    explicit wall height (default height - lid_thickness - size_spacing)
        floor_thickness: floor thickness (default default_floor_thickness)
        lid_thickness:  lid thickness (default default_lid_thickness)
        material_colour: colour (default default_material_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        lid_catch:      catch style (default default_lid_catch_type)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    inner_path = _bosl2.offset(path, r=-wall_thickness - size_spacing)
    calc_inner_path = rounding.round_corners(inner_path, radius=wall_thickness / 2)
    calc_path = rounding.round_corners(path, radius=wall_thickness)

    x_arr = [p[0] for p in inner_path]
    y_arr = [p[1] for p in inner_path]
    calc_width = max(x_arr) - min(x_arr)
    calc_length = max(y_arr) - min(y_arr)

    body = polygon(calc_inner_path).linear_extrude(height=height - lid_thickness - size_spacing).color(material_colour)
    if foot > 0:
        body = body | polygon(calc_path).linear_extrude(height=foot).color(material_colour)

    catches = None
    n = len(calc_inner_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_inner_path[i], calc_inner_path[i + 1]], wall_thickness=wall_thickness, delta=size_spacing,
            offset=0, lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_inner_path[n - 1], calc_inner_path[0]], wall_thickness=wall_thickness, delta=size_spacing,
        offset=0, lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        body = body - catches.translate([0, 0, foot])

    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = c(calc_width, calc_length, inner_height) if callable(c) else c
            body = body - piece.translate([wall_thickness * 2, wall_thickness * 2, floor_thickness])

    result = body
    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            piece = (kids[i](calc_width, calc_length, inner_height) if callable(kids[i]) else kids[i]).translate(
                [wall_thickness * 2, wall_thickness * 2, floor_thickness]
            )
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result


def SlipoverPathBoxLid(
    path: list[list[float]],
    height: float,
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    foot: float = 0,
    finger_catch: CatchType | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    offset_sweep_options: types.SimpleNamespace | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Make a box with a slip lid, a lid that slips over the outside of a box.

    Usage::

        SlipoverPathBoxLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10)

    Args:
        path:    the path of the box outline (>= 3 points)
        height:  height of the lid (outside height)
        children: list of label/decoration solids placed on top of the lid
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        foot:    size of the foot on the box
        finger_catch: where to put the catches (default CatchType.SHORT)
        lid_rounding: rounding on the lid (default wall_thickness)
        material_colour: colour (default default_material_colour)
        offset_sweep_options: namespace(offset=, check_valid=, quality=, steps=)
        lid_catch: catch style (default default_lid_catch_type)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if finger_catch is None:
        finger_catch = CatchType.SHORT
    if material_colour is None:
        material_colour = default_material_colour
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    foot_offset = foot + size_spacing if foot > 0 else 0
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness

    inner_path = _bosl2.offset(path, r=-wall_thickness + size_spacing)
    calc_inner_path = rounding.round_corners(inner_path, radius=wall_thickness / 2)
    calc_path = rounding.round_corners(path, radius=calc_lid_rounding)

    x_arr = [p[0] for p in inner_path]
    y_arr = [p[1] for p in inner_path]
    calc_length = max(y_arr) - min(y_arr)

    outer = polygon(calc_path).linear_extrude(lid_thickness).color(material_colour)
    smooth = _bosl2.offset_sweep(
        calc_path,
        height=lid_thickness,
        top=_bosl2.os_smooth(joint=lid_thickness / 2),
        offset=offset_sweep_options.offset,
        check_valid=offset_sweep_options.check_valid,
        quality=offset_sweep_options.quality,
        steps=offset_sweep_options.steps,
    ).color(material_colour)
    top = outer & smooth

    kids = list(children) if children else []
    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=[top] + kids, size_spacing=size_spacing)
    lid_stack = lid_stack.translate([0, 0, height - foot_offset - lid_thickness])

    finger_height = min(20, (height - foot_offset - lid_thickness) / 2)

    wall_outer = polygon(calc_path).linear_extrude(height - foot_offset - lid_thickness / 2).color(material_colour)
    wall_inner = polygon(calc_inner_path).linear_extrude(height + 1).color(material_colour).translate([0, 0, -0.5])
    wall = wall_outer - wall_inner

    catches = None
    n = len(calc_inner_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_inner_path[i], calc_inner_path[i + 1]], wall_thickness=wall_thickness, delta=0, offset=0,
            lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_inner_path[n - 1], calc_inner_path[0]], wall_thickness=wall_thickness, delta=0, offset=0,
        lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        wall = wall | catches.color(material_colour)

    for i in range(n - 1):
        seg = FingerHoleWallSegmentCutout(
            path=[calc_inner_path[i], calc_inner_path[i + 1]], depth=wall_thickness * 5, height=finger_height,
            radius=max(finger_height, 7), finger_catch=finger_catch,
        )
        if seg is not None:
            wall = wall - seg.color(material_colour)
    seg = FingerHoleWallSegmentCutout(
        path=[calc_inner_path[n - 1], calc_inner_path[0]], depth=wall_thickness * 5, height=finger_height,
        radius=max(finger_height, 7), finger_catch=finger_catch,
    )
    if seg is not None:
        wall = wall - seg.color(material_colour)

    body = lid_stack | wall
    return body.translate([0, calc_length, height - foot]).rotate([180, 0, 0])


def SlipoverPathBoxLidWithLabelAndCustomShape(
    path: list[list[float]],
    height: float,
    text_str: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float = 1.0,
    lid_rounding: float | None = None,
    wall_thickness: float | None = None,
    foot: float = 0,
    finger_catch: CatchType | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a polygon slipover box, with a repeating pattern and a label.

    Usage::

        SlipoverPathBoxLidWithLabelAndCustomShape(
            path=[[0,0],[0,100],[50,100],[50,0]], height=10, text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        path:    the path of the box outline (>= 3 points)
        height:  outside height of the box
        text_str: label text
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: lid thickness (default default_lid_thickness)
        aspect_ratio: dy scale factor (default 1.0)
        lid_rounding: lid edge rounding (default wall_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        foot:    size of the foot on the box
        finger_catch: where to put the catches (default CatchType.SHORT)
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour: colour (default default_material_colour)
        lid_catch: catch style (default default_lid_catch_type)
        pattern_inner_control: inner control mode
        label_options: :class:`~labels.LabelOptions`
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if finger_catch is None:
        finger_catch = CatchType.SHORT
    if material_colour is None:
        material_colour = default_material_colour
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"
    assert text_str is not None, "text_str must be set"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    calc_width = max(x_arr) - min(x_arr)
    calc_length = max(y_arr) - min(y_arr)

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        path=path,
        lid_thickness=lid_thickness,
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        dense=lid_pattern_dense,
        dense_shape_edges=lid_dense_shape_edges,
        inner_control=pattern_inner_control,
        children=pattern_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_shape = MakeLidLabel(size=[calc_width, calc_length], lid_thickness=lid_thickness, text_str=text_str, options=label_opts)

    lid_children = [mesh, label_shape] + (list(extra_children) if extra_children else [])

    return SlipoverPathBoxLid(
        path=path,
        height=height,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        foot=foot,
        finger_catch=finger_catch,
        material_colour=material_colour,
        lid_catch=lid_catch,
        children=lid_children,
    )


def SlipoverPathBoxLidWithLabel(
    path: list[list[float]],
    height: float,
    text_str: str,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    foot: float = 0,
    aspect_ratio: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Lid for a polygon slipover box with an automatic label and shape pattern.

    Usage::

        SlipoverPathBoxLidWithLabel(path=[[0,0],[0,100],[50,100],[50,0]], height=10, text_str="Marmoset")

    Args:
        path:    the path of the box outline (>= 3 points)
        height:  outside height of the box
        text_str: label text
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        foot:    size of the foot on the box
        aspect_ratio: dy scale factor (default default_lid_aspect_ratio)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        lid_rounding: rounding on the lid (default wall_thickness)
        material_colour: colour (default default_material_colour)
        lid_catch: catch style (default default_lid_catch_type)
        label_options: :class:`~labels.LabelOptions`
        shape_options: :class:`~shape_type.ShapeObject`
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"
    assert text_str is not None, "text_str must be set"

    shape_piece = ShapeByType(options=calc_shape_options).color(material_colour)

    return SlipoverPathBoxLidWithLabelAndCustomShape(
        path=path,
        height=height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_boundary=lid_boundary,
        foot=foot,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        lid_catch=lid_catch,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        shape_child=shape_piece,
        extra_children=extra_children,
    )
