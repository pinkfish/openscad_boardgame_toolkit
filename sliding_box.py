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

# LibFile: sliding_box.py
#    Sliding box pieces for the sliding boxes.
#
# FileSummary: Sliding box pieces for the sliding boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy
import types

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import numpy as np
import bosl2.masking
import bosl2.shapes3d
import bosl2.transforms
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, SlidingLidFingernail, IsDenseShapeType, DenseShapeEdges
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


def MakeSlidingLidOptions(
    two_layer: bool = False, two_layer_top_lid_ratio: float = 0.5, two_layer_vee_shape: bool = False
) -> types.SimpleNamespace:
    """Make the sliding lid options object.

    Args:
        two_layer: if the lid has a cap layer, a second layer on top (default False)
        two_layer_top_lid_ratio: ratio of the top bit to the sliding bit (default 0.5)
        two_layer_vee_shape: if the two-layer lid should use a vee slide (default False)
    """
    return types.SimpleNamespace(
        two_layer=two_layer, two_layer_top_lid_ratio=two_layer_top_lid_ratio, two_layer_vee_shape=two_layer_vee_shape
    )


def SlidingLid(
    size: list[float],
    children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Creates a sliding lid for a sliding lid box.

    *children* are inserted into the lid. This does all the right things on
    the edges, uses some wiggle room to add in a buffer and also does a
    small amount of angling on the ends to make them easier to insert.
    Entries may be a callable(inner_width, inner_length).

    Usage::

        SlidingLid(size=[10, 30], lid_thickness=3, wall_thickness=2, size_spacing=0.2)

    Args:
        size: [width, length] the size of the box itself
        children: list of solids/callables to insert into the lid
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        size_spacing: how much offset to use generating the slide spacing (default m_piece_wiggle_room)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]

    calc_wall_thickness = wall_thickness
    if calc_wall_thickness is None:
        calc_wall_thickness = default_wall_thickness
    calc_lid_thickness = lid_thickness
    if calc_lid_thickness is None:
        calc_lid_thickness = default_lid_thickness
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = calc_wall_thickness / 2
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()

    chamfer = (
        0
        if calc_sliding_lid_options.two_layer
        else (
            calc_wall_thickness / 2
            if calc_wall_thickness / 2 > calc_lid_thickness - size_spacing
            else calc_lid_thickness - size_spacing
        )
    )
    lid_width = width if calc_sliding_lid_options.two_layer else width - 2 * calc_wall_thickness + chamfer * 2 + size_spacing
    lid_length = length if calc_sliding_lid_options.two_layer else length - calc_wall_thickness + chamfer - size_spacing
    top_cover = calc_sliding_lid_options.two_layer_top_lid_ratio * calc_lid_thickness
    lid_under_cover = calc_lid_thickness - top_cover
    middle_chamfer = lid_under_cover / 2 if calc_wall_thickness > lid_under_cover else calc_wall_thickness / 2
    two_layer_chamfer = (
        middle_chamfer
        if calc_sliding_lid_options.two_layer_vee_shape
        else (calc_wall_thickness / 2 if calc_wall_thickness / 2 < lid_under_cover else lid_under_cover)
    )

    def mask_2sliding_lid() -> list[list[float]]:
        if calc_sliding_lid_options.two_layer_vee_shape:
            path = [
                [0, 0],
                [calc_wall_thickness / 2 + size_spacing, 0],
                [calc_wall_thickness / 2 + middle_chamfer + size_spacing, middle_chamfer],
                [calc_wall_thickness / 2 + size_spacing, lid_under_cover],
                [0, lid_under_cover],
            ]
        else:
            path = [
                [0, 0],
                [size_spacing, 0],
                [calc_wall_thickness - two_layer_chamfer, 0],
                [calc_wall_thickness, lid_under_cover],
                [size_spacing, lid_under_cover],
                [0, lid_under_cover],
            ]
        return path

    edges = (
        [LEFT + TOP, RIGHT + TOP, TOP + FRONT, LEFT + BOTTOM, RIGHT + BOTTOM, BOTTOM + FRONT]
        if calc_sliding_lid_options.two_layer
        else [LEFT + TOP, RIGHT + TOP, TOP + FRONT]
    )
    main = bosl2.shapes3d.cuboid(
        [lid_width, lid_length, calc_lid_thickness], anchor=BOTTOM + FRONT + LEFT, chamfer=chamfer + size_spacing, edges=edges
    )
    main = main.edge_mask(
        [LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        children=bosl2.masking.rounding_edge_mask(
            r=calc_wall_thickness if calc_sliding_lid_options.two_layer else calc_lid_rounding,
            l=calc_lid_thickness + size_spacing,
        ),
    )
    top_edges = [TOP] if calc_sliding_lid_options.two_layer else [TOP + BACK]
    main = main.edge_mask(
        top_edges,
        children=bosl2.masking.rounding_edge_mask(
            r=top_cover if calc_sliding_lid_options.two_layer else calc_lid_rounding / 2,
            l=max(lid_length, lid_width),
        ),
    )

    if calc_sliding_lid_options.two_layer:
        # A custom (non-round/chamfer) profile cut along the BOTTOM+LEFT/BOTTOM+RIGHT edges --
        # the profile is swept along each edge's own run axis (Y here) by hand with an explicit
        # rotate()/translate(), the same per-edge orientation BOSL2's edge_profile_asym()
        # computes internally: a mirror (BOTTOM+LEFT) or a pure rotation (BOTTOM+RIGHT)
        # composed with a 180-degree turn around the (Y+Z) diagonal -- verified by rendering
        # both against the original edge_profile_asym()-based cross-section and comparing
        # pixel-for-pixel.
        profile = np.asarray(mask_2sliding_lid(), dtype=float)
        mirrored_profile = profile * np.array([-1.0, 1.0])
        run_length = lid_length + 0.1
        cutter_left = (
            polygon([[float(u), float(v)] for u, v in mirrored_profile])
            .linear_extrude(height=run_length, center=True)
            .rotate(180, [0, 1, 1])
            .translate([0, lid_length / 2, 0])
        )
        cutter_right = (
            polygon([[float(u), float(v)] for u, v in profile])
            .linear_extrude(height=run_length, center=True)
            .rotate(180, [0, 1, 1])
            .translate([lid_width, lid_length / 2, 0])
        )
        main = main - cutter_left - cutter_right

    if calc_sliding_lid_options.two_layer:
        front_cut = bosl2.shapes3d.cuboid(
            [lid_width, calc_wall_thickness, lid_under_cover + size_spacing], anchor=BOTTOM + FRONT + LEFT
        ).translate([0, 0, -size_spacing])
        main = main - front_cut
        # rounding_edge_mask() sweeps centered on Z (unlike the manual, non-centered
        # linear_extrude(calc_lid_thickness) this replaces), so its Z placement is shifted up
        # by half the swept length to land on the same absolute span.
        round_a = bosl2.masking.rounding_edge_mask(l=calc_lid_thickness, r=calc_lid_rounding).translate(
            [calc_wall_thickness - two_layer_chamfer, calc_wall_thickness, -top_cover + calc_lid_thickness / 2]
        )
        round_b = (
            bosl2.masking.rounding_edge_mask(l=calc_lid_thickness, r=calc_lid_rounding)
            .rotate([0, 180, 0])  # mirrors the +X-opening cutter to open toward -X instead
            .translate([lid_width - calc_wall_thickness + two_layer_chamfer, calc_wall_thickness, -top_cover + calc_lid_thickness / 2])
        )
        main = main - round_a - round_b
    else:
        # right_triangle([w, l])'s default anchor puts the right-angle corner at the origin,
        # legs along +X (w) and +Y (l) -- reproduced directly as polygon points rather than
        # reorienting wedge() (whose own triangular cross-section/extrusion axes don't match
        # right_triangle()'s convention). The centered linear_extrude matches the SDF-era
        # polygon_extrude() convention: shift the Z translate by +height/2.
        tri_h = calc_lid_thickness + 10
        tri_z = -calc_lid_thickness / 2 + tri_h / 2
        tri_a = (
            polygon([[calc_wall_thickness / 2, 0], [0, 0], [0, 15]])
            .linear_extrude(height=tri_h, center=True)
            .translate([-size_spacing / 20, -size_spacing, tri_z])
        )
        tri_b = (
            polygon([[-calc_wall_thickness / 2, 0], [0, 0], [0, 15]])
            .linear_extrude(height=tri_h, center=True)
            .translate([lid_width + size_spacing / 20, -size_spacing, tri_z])
        )
        main = main - tri_a - tri_b

    main = main.color(material_colour)

    inner_width = width - calc_wall_thickness
    inner_length = length - calc_wall_thickness / 2
    kids = list(children) if children else []
    resolved_kids = [(c(inner_width, inner_length) if callable(c) else c) for c in kids]

    lid_stack = internal_build_lid(lid_thickness=calc_lid_thickness, children=[main] + resolved_kids, size_spacing=size_spacing)

    if calc_sliding_lid_options.two_layer:
        lid_stack = lid_stack.rotate([180, 0, 0]).translate([0, lid_length, calc_lid_thickness])

    return lid_stack


def SlidingBoxLidWithCustomShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    wall_thickness: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
) -> PyOpenSCAD:
    """Lid for a sliding lid box.

    Uses *shape_child* as the shape for repeating on the lid and
    *extra_children* as additional children for the lid.

    Usage::

        SlidingBoxLidWithCustomShape([100, 50],
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size: [width, length] outside size of the lid
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        aspect_ratio: dy scale factor (default 1.0)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour: colour (default default_material_colour)
        pattern_inner_control: inner control mode
    """
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    calc_lid_thickness = lid_thickness
    if calc_lid_thickness is None:
        calc_lid_thickness = default_lid_thickness
    calc_wall_thickness = wall_thickness
    if calc_wall_thickness is None:
        calc_wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=[width - calc_wall_thickness, length - calc_wall_thickness / 2],
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

    fingernail = bosl2.shapes3d.cuboid(
        [width - calc_wall_thickness, length - calc_wall_thickness, calc_lid_thickness], anchor=BOTTOM + FRONT + LEFT
    ).color(material_colour) & SlidingLidFingernail(calc_lid_thickness, material_colour=material_colour).translate(
        [width / 2 - calc_wall_thickness / 2, length - calc_wall_thickness - 3, 0]
    ).shape

    extra = list(extra_children) if extra_children else []
    # fingernail stays FIRST: the ordering dates from the SDF (frep) era, when a second
    # .projection() on the same frep node crashed the app. All-native geometry no longer
    # needs it, but internal_build_lid()'s carve-then-union is order-independent, so keeping
    # the order costs nothing and keeps the diff history readable.
    lid_children = [fingernail, mesh] + extra

    return SlidingLid(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        material_colour=material_colour,
        sliding_lid_options=calc_sliding_lid_options,
        children=lid_children,
    )


def SlidingBoxLidWithLabelAndCustomShape(
    size: list[float],
    text_str: str,
    shape_child: PyOpenSCAD,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    wall_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a sliding lid box, with a repeating pattern and a label.

    Usage::

        SlidingBoxLidWithLabelAndCustomShape(size=[100, 50], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        shape_child: 2-D shape solid to tile on the lid (required)
        extra_children: additional children (list of solids)
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        aspect_ratio: dy scale factor (default 1.0)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour: colour (default default_material_colour)
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

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)

    assert shape_child is not None, "Must specify shape_child for the pattern"
    assert width > 0 and length > 0, f"Need width,length > 0 width={width} length={length}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert text_str is not None, "Need to specify a label, text_str == None"

    calc_wall_thickness = wall_thickness
    if calc_wall_thickness is None:
        calc_wall_thickness = default_wall_thickness
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = calc_sliding_lid_options.two_layer
    label_shape_raw = MakeLidLabel(
        size=[width - calc_wall_thickness * 2, length - calc_wall_thickness * 2], lid_thickness=lid_thickness,
        text_str=text_str, options=label_opts,
    )
    # A lid too narrow for the label yields None (labels.py warns "ignoring label"); match the
    # .scad and just build the lid without a label rather than failing.
    _base = list(extra_children) if extra_children else []
    if label_shape_raw is not None:
        lid_extra = [label_shape_raw.translate([calc_wall_thickness / 2, calc_wall_thickness / 2, 0])] + _base
    else:
        lid_extra = _base

    return SlidingBoxLidWithCustomShape(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        material_colour=material_colour,
        lid_boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=lid_pattern_dense,
        lid_dense_shape_edges=lid_dense_shape_edges,
        pattern_inner_control=pattern_inner_control,
        sliding_lid_options=calc_sliding_lid_options,
        shape_child=shape_child,
        extra_children=lid_extra,
    )


def SlidingBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_thickness: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Composite lid: a sliding lid box with a label and a pattern (e.g. hex grid).

    Usage::

        SlidingBoxLidWithLabel(size=[100, 100], lid_thickness=3, text_str="Trains")

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        extra_children: additional children (list of solids)
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
        lid_thickness: thickness of the lid (default default_lid_thickness)
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        aspect_ratio: dy scale factor (default default_lid_aspect_ratio)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
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

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()

    assert width > 0 and length > 0, f"Need width,length > 0 width={width} length={length}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert text_str is not None, "Need to specify a label, text_str == None"

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour).translate([lid_boundary, lid_boundary, 0])

    return SlidingBoxLidWithLabelAndCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_boundary=lid_boundary,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        label_options=calc_label_options,
        sliding_lid_options=calc_sliding_lid_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )


def SlidingBoxLidWithShape(
    size: list[float],
    extra_children: "list | None" = None,
    lid_thickness: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    wall_thickness: float | None = None,
    aspect_ratio: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    shape_options: ShapeObject | None = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
) -> PyOpenSCAD:
    """Composite lid: a sliding lid box with an automatic pattern (e.g. hex grid).

    Usage::

        SlidingBoxLidWithShape(size=[100, 100], lid_thickness=3)

    Args:
        size: [width, length] outside size of the lid
        extra_children: additional children (list of solids)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        aspect_ratio: dy scale factor (default default_lid_aspect_ratio)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
        shape_options: :class:`~shape_type.ShapeObject`
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    assert width > 0 and length > 0, f"Need width,length > 0 width={width} length={length}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"

    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour).translate([lid_boundary, lid_boundary, 0])

    return SlidingBoxLidWithCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_boundary=lid_boundary,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        sliding_lid_options=calc_sliding_lid_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )


def MakeBoxWithSlidingLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    floor_thickness: float | None = None,
    size_spacing: float | None = None,
    material_colour: str | None = None,
    positive_colour: str | None = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    spin: float = 0,
    anchor: list[int] | None = None,
    orient: list[float] | None = None,
) -> PyOpenSCAD:
    """Makes a box with a sliding lid -- the box itself with cutouts for the sliding lid pieces.

    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior, starting from the edge
    inside the wall width and up from the floor.

    Usage::

        MakeBoxWithSlidingLid([50, 100, 20])

    Args:
        size:    [width, length, height] outside size of the box
        children: list of solids/callables to carve inside the box
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        material_colour: colour (default default_material_colour)
        positive_colour: colour of positive pieces (default default_positive_colour)
        sliding_lid_options: :func:`MakeSlidingLidOptions` result
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        spin/anchor/orient: BOSL2 positioning
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour
    if positive_colour is None:
        positive_colour = default_positive_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []
    if anchor is None:
        anchor = BOTTOM + FRONT + LEFT
    if orient is None:
        orient = TOP

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    calc_sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()
    calc_wall_thickness = wall_thickness
    if calc_wall_thickness is None:
        calc_wall_thickness = default_wall_thickness

    top_cover = calc_sliding_lid_options.two_layer_top_lid_ratio * lid_thickness
    lid_cutout = (lid_thickness - top_cover) if calc_sliding_lid_options.two_layer else lid_thickness
    middle_chamfer = lid_cutout / 2 if wall_thickness > lid_cutout else wall_thickness / 2
    calc_height = (height - top_cover - size_spacing) if calc_sliding_lid_options.two_layer else height

    tmat = bosl2.transforms.reorient(anchor=anchor, spin=spin, orient=orient, size=[width, length, calc_height])

    body = bosl2.shapes3d.cuboid(
        [width, length, calc_height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    )
    if not calc_sliding_lid_options.two_layer:
        body = body.edge_mask(
            [TOP], children=bosl2.masking.rounding_edge_mask(r=wall_thickness / 2, l=max(length, width))
        )

    rounding_offset = 0.01
    mid_cut = bosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness + size_spacing + rounding_offset, lid_cutout + size_spacing / 2],
        anchor=BOTTOM + FRONT + LEFT,
    ).translate([wall_thickness, -rounding_offset, calc_height - lid_cutout])
    body = body - mid_cut

    if calc_sliding_lid_options.two_layer:
        if calc_sliding_lid_options.two_layer_vee_shape:
            lid_cut = bosl2.shapes3d.cuboid(
                [width - wall_thickness * 2 + middle_chamfer * 2 + size_spacing, length - wall_thickness, lid_cutout],
                anchor=BOTTOM + FRONT + LEFT,
                chamfer=middle_chamfer,
                edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + LEFT, BOTTOM + RIGHT],
            ).translate([wall_thickness - middle_chamfer - size_spacing / 2, 0, calc_height - lid_cutout])
        else:
            chamfer2 = wall_thickness / 2 if wall_thickness / 2 < lid_cutout else lid_cutout
            lid_cut = bosl2.shapes3d.cuboid(
                [width - wall_thickness * 2 + chamfer2 * 2 + size_spacing, length - wall_thickness, lid_cutout],
                anchor=BOTTOM + FRONT + LEFT,
                chamfer=chamfer2,
                edges=[TOP + LEFT, TOP + RIGHT],
            ).translate([wall_thickness - chamfer2 - size_spacing / 2, 0, calc_height - lid_cutout])
    else:
        chamfer2 = wall_thickness / 2 if wall_thickness / 2 < lid_cutout else lid_cutout
        lid_cut = bosl2.shapes3d.cuboid(
            [width - wall_thickness * 2 + chamfer2 * 2, length - wall_thickness + chamfer2, lid_cutout],
            anchor=BOTTOM + FRONT + LEFT,
            chamfer=chamfer2,
            edges=[TOP + LEFT, TOP + RIGHT, TOP + BACK],
        ).translate([wall_thickness - chamfer2, 0, calc_height - lid_cutout])
    body = body - lid_cut

    # Note: the original .scad passed `height=` here (a BOSL2 alias); the port's
    # rounding_edge_mask() takes `l=`/`h=`.
    edge_round = (
        bosl2.masking.rounding_edge_mask(r=wall_thickness / 4, h=length - wall_thickness * 2)
        .rotate([0, 90, 0])
        .translate([width / 2, 0, calc_height - lid_cutout])
    )
    body = body - edge_round

    body = body.color(material_colour)

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            body = body - piece.translate([wall_thickness, wall_thickness, floor_thickness])

    result = body.translate([-width / 2, -length / 2, -height / 2]).multmatrix(tmat)

    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            piece = (
                ResolveChild(kids[i], inner_width, inner_length, inner_height)
                .color(positive_colour)
                .translate([wall_thickness, wall_thickness, floor_thickness])
            )
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result
