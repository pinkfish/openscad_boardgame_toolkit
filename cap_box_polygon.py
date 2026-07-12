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

# LibFile: cap_box_polygon.py
#    Cap box pieces for the cap boxes with polygon outline.
#
# FileSummary: Cap box pieces for the cap boxes with polygon outline.
# FileGroup: Boxes

from __future__ import annotations
import copy
import math

import numpy as np
import types

from openscad import hull, polygon
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import numpy as np
import bosl2.shapes3d
from bosl2 import paths as b2paths
from bosl2 import rounding as b2rounding
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, IsDenseShapeType, DenseShapeEdges, default_lid_catch_type
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from cap_box import CapBoxDefaultCapHeight, CapBoxDefaultFingerHoldHeight, CapBoxDefaultLidFingerHoldRounding, CapBoxDefaultLidWallThickness


def _segment_angle(normal: "np.ndarray | list[list[float]]") -> float:
    if normal[0][0] == 0:
        return 90 if normal[0][1] > 0 else -90
    return math.degrees(math.atan(normal[0][1] / normal[0][0]))


def FingerHoleSegmentCutout(
    path: list[list[float]], radius: float, height: float, wall_thickness: float
) -> PyOpenSCAD | None:
    """Makes a single segment for use in the cap-box wall.

    Makes the rounded finger holes on the side of the cap box at the
    correct direction and length; returns None if the segment is too short.

    Usage::

        FingerHoleSegmentCutout([[0, 0], [50, 50]], radius=5, height=7, wall_thickness=2)

    Args:
        path:   the path to generate for (exactly 2 points / one line segment)
        radius: the radius of the rounding on the finger hole
        height: the height of the finger hole
        wall_thickness: the thickness of the walls
    """
    assert len(path) == 2, f"Path must be exactly 2 elements long path_length={len(path)}"
    split_length = b2paths.path_length(path)
    normal = b2paths.path_normals(path)
    calc_len = split_length / 5
    calc_radius = wall_thickness + 0.1 if wall_thickness >= radius else radius

    if not (split_length > calc_radius * 2):
        return None

    angle = _segment_angle(normal)

    if calc_len + radius > calc_len * 4 - radius:
        pts = b2paths.path_cut_points(path, [split_length / 2])
        return bosl2.shapes3d.xcyl(h=wall_thickness * 2, r=radius).rotate([0, 0, angle]).translate(
            [float(pts[0][0][0]), float(pts[0][0][1]), 0.0]
        ).shape

    pts = b2paths.path_cut_points(
        path,
        [calc_len + wall_thickness, calc_len + calc_radius, calc_len * 4 - calc_radius, calc_len * 4 - wall_thickness],
    )
    # .shape unwraps each Bosl2Solid: native hull() only takes raw solids.
    c1 = bosl2.shapes3d.xcyl(h=wall_thickness * 2, r=radius).rotate([0, 0, angle]).translate([float(pts[1][0][0]), float(pts[1][0][1]), height - calc_radius]).shape
    c2 = bosl2.shapes3d.xcyl(h=wall_thickness * 2, r=radius).rotate([0, 0, angle]).translate([float(pts[2][0][0]), float(pts[2][0][1]), height - calc_radius]).shape
    c3 = bosl2.shapes3d.cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2]).rotate([0, 0, angle]).translate(
        [float(pts[0][0][0]), float(pts[0][0][1]), calc_radius - height]
    ).shape
    c4 = bosl2.shapes3d.cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2]).rotate([0, 0, angle]).translate(
        [float(pts[3][0][0]), float(pts[3][0][1]), calc_radius - height]
    ).shape
    return hull(c1, c2, c3, c4)


def PolygonBoxLidCatch(
    path: list[list[float]], wall_thickness: float, offset: float, delta: float, lid_catch: CatchType | None = None
) -> PyOpenSCAD | None:
    """The catch under the lid for the polygon box.

    A small wedge that follows the specified line segment, only generated
    when the segment is long enough and matches *lid_catch*.

    Usage::

        PolygonBoxLidCatch(path=[[0, 0], [50, 50]], offset=5, wall_thickness=2, delta=0)
        PolygonBoxLidCatch(path=[[0, 0], [50, 50]], offset=5, wall_thickness=2, delta=2)

    Args:
        path:   the path to generate for (exactly 2 points / one line segment)
        wall_thickness: the thickness of the walls
        offset: the offset of the rounding on the finger hole
        delta:  how much to offset the segment by
        lid_catch: the type of catch to use
    """
    assert len(path) == 2, f"Path must be exactly 2 elements. path_length={len(path)}"
    assert delta is not None, "delta None in PolygonBoxLidCatch."
    split_length = b2paths.path_length(path)
    calc_len = split_length / 5

    if not (
        calc_len * 4 - offset - wall_thickness + delta - (calc_len + wall_thickness + offset - delta) > 5
        and lid_catch != CatchType.NONE
    ):
        return None

    vec_m = abs(path[0][0] - path[1][0]) / abs(path[0][1] - path[1][1]) if path[0][1] != path[1][1] else float("inf")
    qualifies = (
        lid_catch == CatchType.ALL
        or (lid_catch == CatchType.LONG and vec_m > 1000000)
        or (lid_catch == CatchType.SHORT and vec_m < 0.01)
    )
    if not qualifies:
        return None

    pts = b2paths.path_cut_points(
        path, [calc_len + wall_thickness + offset - delta, calc_len * 4 - wall_thickness - offset + delta]
    )
    p1 = [pts[0][0][0], pts[0][0][1]]
    p2 = [pts[1][0][0], pts[1][0][1]]
    # The old _bosl2.path_sweep of the triangle profile along the 2-point segment is a
    # triangular prism: extrude the profile (centered along Z), stand it up (profile y -> Z,
    # extrusion axis -> the segment direction, profile x -> the LEFT of travel, matching
    # path_sweep's 2-D frame), and move it onto the segment midpoint.
    seg_angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    return (
        polygon([[delta, delta], [-wall_thickness * 3 / 4 - delta, delta], [delta, wall_thickness * 3 / 4 + delta]])
        .linear_extrude(height=math.dist(p1, p2), center=True)
        .rotate([90, 0, 0])
        .rotate([0, 0, seg_angle + 90])
        .translate([float((p1[0] + p2[0]) / 2), float((p1[1] + p2[1]) / 2), 0.0])
    )


def MakePathBoxWithCapLid(
    path: list[list[float]],
    height: float,
    children: "list | None" = None,
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_wall_thickness: float | None = None,
    finger_hold_height: float = 5,
    floor_thickness: float | None = None,
    material_colour: str | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Makes a polygon-outline box with a cap lid.

    *children* is a list of solids (or callables(inner_path, inner_width,
    inner_length, inner_height)) carved into the box interior.

    Usage::

        MakePathBoxWithCapLid(path=[[0,0], [0,100], [100,100]], height=20)

    Args:
        path:            the polygon outline path of the box (>= 3 points)
        height:          outside height of the box
        children:        list of solids/callables to carve inside the box
        cap_height:      cap height (default auto)
        lid_thickness:   lid thickness (default default_lid_thickness)
        wall_thickness:  wall thickness (default default_wall_thickness)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_wall_thickness: thickness of the walls in the lid (default wall_thickness/2)
        finger_hold_height: finger hold height (default 5)
        floor_thickness: floor thickness (default default_floor_thickness)
        material_colour: colour (default default_material_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        lid_catch:       catch style (default default_lid_catch_type)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
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

    calc_lid_wall_thickness = lid_wall_thickness if lid_wall_thickness is not None else CapBoxDefaultLidWallThickness(wall_thickness)
    calc_floor_thickness = floor_thickness if floor_thickness is not None else wall_thickness
    calc_cap_height = cap_height if cap_height is not None else CapBoxDefaultCapHeight(height)
    calc_finger_hold_height = finger_hold_height if finger_hold_height is not None else CapBoxDefaultFingerHoldHeight(height)
    calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height)
    calc_path = np.asarray(b2rounding.round_corners(path, radius=wall_thickness))
    # Plain lists for the native polygon() calls below: raw ndarrays across the native
    # boundary raise (and poison the interpreter) -- see the numpy interop convention.
    calc_path_native = calc_path.tolist()
    # The old _bosl2.offset(path, r=-wall) inner path only ever fed this bounding-box
    # bookkeeping -- the wall-inset bbox is the bbox shrunk by a wall on each side.
    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    calc_width = max(x_arr) - min(x_arr) - 2 * wall_thickness
    calc_length = max(y_arr) - min(y_arr) - 2 * wall_thickness

    body = polygon(calc_path_native).linear_extrude(height=height - lid_thickness - size_spacing).color(material_colour)

    lid_outer = polygon(calc_path_native).offset(size_spacing).linear_extrude(height=height).color(material_colour)
    lid_inner = polygon(calc_path_native).offset(-calc_lid_wall_thickness - size_spacing).linear_extrude(height + 1).color(
        material_colour
    ).translate([0, 0, -0.5])
    body = body - (lid_outer - lid_inner).translate([0, 0, height - calc_cap_height])

    finger_outer = polygon(calc_path_native).offset(size_spacing).linear_extrude(height=height).color(material_colour)
    finger_inner = polygon(calc_path_native).offset(-calc_lid_wall_thickness - size_spacing).linear_extrude(height=height).color(
        material_colour
    )
    finger_cut = finger_outer - finger_inner
    n = len(calc_path)
    for i in range(n - 1):
        seg = FingerHoleSegmentCutout(
            path=[calc_path[i], calc_path[i + 1]], height=calc_finger_hold_height, radius=calc_finger_hole_rounding,
            wall_thickness=wall_thickness,
        )
        if seg is not None:
            finger_cut = finger_cut - seg
    seg = FingerHoleSegmentCutout(
        path=[calc_path[n - 1], calc_path[0]], height=calc_finger_hold_height, radius=calc_finger_hole_rounding,
        wall_thickness=wall_thickness,
    )
    if seg is not None:
        finger_cut = finger_cut - seg
    body = body - finger_cut.translate([0, 0, height - calc_cap_height - calc_finger_hold_height])

    catches = None
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_path[i], calc_path[i + 1]], offset=calc_finger_hole_rounding, wall_thickness=wall_thickness,
            delta=size_spacing, lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_path[n - 1], calc_path[0]], offset=calc_finger_hole_rounding, wall_thickness=wall_thickness,
        delta=size_spacing, lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        body = body - catches.translate([0, 0, height - calc_cap_height])

    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []

    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece: Any = c(calc_path, calc_width, calc_length, inner_height) if callable(c) else c
            body = body - piece.translate([wall_thickness, wall_thickness, calc_floor_thickness])

    result = body

    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            # Path-box children take (path, width, length, height) -- ResolveChild() is the
            # 3-argument box form and this call passed 5 arguments (a latent TypeError in the
            # never-exercised positive-children branch); resolve inline like the branch above.
            resolved: Any = (
                kids[i](calc_path, calc_width, calc_length, inner_height) if callable(kids[i]) else kids[i]
            )
            piece = resolved.translate([wall_thickness, wall_thickness, floor_thickness])
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result


def CapPathBoxLid(
    path: list[list[float]],
    height: float,
    children: list[PyOpenSCAD] | None = None,
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_wall_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    offset_sweep_options: types.SimpleNamespace | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Lid for a polygon cap box, with finger cutouts.

    Usage::

        CapPathBoxLid(path=[[0,0], [0,100], [100,100]], height=30)

    Args:
        path:    the polygon outline path of the box (>= 3 points)
        height:  outside height of the box
        children: list of label/decoration solids placed on top of the lid
        cap_height: cap height (default auto)
        lid_thickness: lid thickness (default default_lid_thickness)
        wall_thickness: wall thickness (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_wall_thickness: thickness of the walls in the lid (default wall_thickness/2)
        lid_rounding/lid_inner_rounding: rounding values
        material_colour: colour (default default_material_colour)
        offset_sweep_options: namespace(offset=, check_valid=, quality=, steps=)
        lid_catch: catch style (default default_lid_catch_type). Note: the
                   original SCAD module never threaded this through to its
                   catch geometry (a bug); it's wired up correctly here.
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    calc_lid_wall_thickness = lid_wall_thickness if lid_wall_thickness is not None else wall_thickness / 2
    calc_cap_height = cap_height if cap_height is not None else CapBoxDefaultCapHeight(height)
    calc_path = np.asarray(b2rounding.round_corners(path, radius=wall_thickness, _fn=16))
    calc_path_native = calc_path.tolist()  # plain lists for the native polygon() calls
    calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height)

    y_arr = [p[1] for p in path]
    calc_length = max(y_arr) - min(y_arr)

    # The old offset_sweep with an os_smooth(joint=wall/2) top is a straight extrusion of
    # the rounded outline with an eased top rim -- polygon_prism's circular roundover of the
    # same joint size is a near-identical profile.
    top = PolygonPrism(
        calc_path, h=lid_thickness, rounding_top=min(wall_thickness / 2, lid_thickness * 0.49)
    ).color(material_colour)

    kids = list(children) if children else []
    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=[top] + kids, size_spacing=size_spacing)
    lid_stack = lid_stack.translate([0, 0, calc_cap_height - lid_thickness])

    base_outer = polygon(calc_path_native).linear_extrude(height=calc_cap_height - lid_thickness / 2).color(material_colour)
    base_inner = polygon(calc_path_native).offset(-wall_thickness + size_spacing).linear_extrude(
        height=calc_cap_height - lid_thickness / 2 + 1
    ).color(material_colour).translate([0, 0, -0.5])
    base = base_outer - base_inner

    catches = None
    n = len(calc_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_path[i], calc_path[i + 1]], offset=calc_finger_hole_rounding, wall_thickness=wall_thickness,
            delta=0, lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_path[n - 1], calc_path[0]], offset=calc_finger_hole_rounding, wall_thickness=wall_thickness,
        delta=0, lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c

    main = lid_stack | base
    if catches is not None:
        main = main | catches.color(material_colour)

    return main.translate([0, calc_length, calc_cap_height]).rotate([180, 0, 0])


def CapPathBoxLidWithLabelAndCustomShape(
    path: list[list[float]],
    height: float,
    text_str: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    lid_wall_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    label_background_colour: str | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a polygon cap box, with a repeating pattern and a label.

    Usage::

        CapPathBoxLidWithLabelAndCustomShape(path=[[0,0], [0,100], [100,100]],
            height=30, text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        path:       the polygon outline path of the box (>= 3 points)
        height:     outside height of the box
        text_str:   label text
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        wall_thickness: wall thickness (default default_wall_thickness)
        cap_height: cap height (default auto)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: lid thickness (default default_lid_thickness)
        lid_wall_thickness: thickness of the walls in the lid (default wall_thickness/2)
        aspect_ratio: dy scale factor (default 1.0)
        lid_rounding/lid_inner_rounding: rounding values
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour: colour (default default_material_colour)
        label_background_colour: unused, kept for API compatibility
        pattern_inner_control: inner control mode
        label_options: :class:`~labels.LabelOptions`
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour

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
        material_colour=material_colour,
        inner_control=pattern_inner_control,
        children=pattern_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_shape = MakeLidLabel(size=[calc_width, calc_length], text_str=text_str, lid_thickness=lid_thickness, options=label_opts)

    lid_children = [mesh, label_shape] + (list(extra_children) if extra_children else [])

    return CapPathBoxLid(
        path=path,
        height=height,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        lid_wall_thickness=lid_wall_thickness,
        size_spacing=m_piece_wiggle_room,
        lid_rounding=lid_rounding,
        lid_inner_rounding=lid_inner_rounding,
        material_colour=material_colour,
        children=lid_children,
    )


def CapPathBoxLidWithLabel(
    path: list[list[float]],
    height: float,
    text_str: str,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    lid_wall_thickness: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Lid for a polygon cap box with an automatic label and shape pattern.

    Usage::

        CapPathBoxLidWithLabel(path=[[0,0], [0,100], [100,100]], height=30, text_str="Frog")

    Args:
        path:    the polygon outline path of the box (>= 3 points)
        height:  outside height of the box
        text_str: label text
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        wall_thickness: wall thickness (default default_wall_thickness)
        cap_height: cap height (default auto)
        layout_width: pattern repeat width (default default_lid_layout_width)
        aspect_ratio: dy scale factor (default default_lid_aspect_ratio)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: lid thickness (default default_lid_thickness)
        lid_wall_thickness: thickness of the walls in the lid
        lid_inner_rounding: inner rounding
        material_colour: colour (default default_material_colour)
        label_options: :class:`~labels.LabelOptions`
        shape_options: :class:`~shape_type.ShapeObject`
    """
    if material_colour is None:
        material_colour = default_material_colour
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"
    assert text_str is not None, "text_str must be set"

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return CapPathBoxLidWithLabelAndCustomShape(
        path=path,
        height=height,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        lid_wall_thickness=lid_wall_thickness,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        label_options=calc_label_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )
