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

# LibFile: filament_hinge_box.py
#    Filament hinge box pieces for the hinge boxes.
#
# FileSummary: Filament hinge box pieces for the hinge boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy
import math
import types

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import bosl2.masking
import bosl2.shapes3d
import pysolidfive
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, IsDenseShapeType, DenseShapeEdges
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


# The six axis orientations BOSL2 orient= takes at these call sites, as native Euler
# rotations of UP toward the axis (used by _apply_reorient below).
_ORIENT_EULER = {
    (0, 0, 1): None,
    (0, 0, -1): [180, 0, 0],
    (-1, 0, 0): [0, -90, 0],
    (1, 0, 0): [0, 90, 0],
    (0, -1, 0): [90, 0, 0],
    (0, 1, 0): [-90, 0, 0],
}


def _apply_reorient(shape, anchor, spin, orient, size):
    """BOSL2 reorient() emulation for a native shape already centered at the origin: move
    the anchor point to the origin, spin around Z, then rotate UP toward `orient` -- replaces
    the old `_bosl2.reorient(...)` + `.multmatrix(tmat)` (which never worked here anyway;
    this whole file's knuckle-hinge paths raised before reaching it)."""
    a = [int(v) for v in anchor]
    if any(a):
        shape = shape.translate([-a[0] * size[0] / 2, -a[1] * size[1] / 2, -a[2] * size[2] / 2])
    if spin:
        shape = shape.rotate([0, 0, spin])
    key = (int(orient[0]), int(orient[1]), int(orient[2]))
    assert key in _ORIENT_EULER, f"orient must be one of the six axis directions, got {orient}"
    euler = _ORIENT_EULER[key]
    if euler is not None:
        shape = shape.rotate(euler)
    return shape


def HingeOptions(
    thickness: float | None = None,
    hole_diameter: float | None = None,
    num_segments: int | None = None,
    pin_slop: float | None = None,
) -> types.SimpleNamespace:
    """Returns an object containing the hinge options.

    Args:
        thickness:     thickness of the hinge (default default_hinge_thickness)
        hole_diameter: diameter of the hinge hole (default default_hinge_hole_diameter)
        num_segments:  number of hinge segments (default auto)
        pin_slop:      extra diameter slop for the hinge pin (default default_hinge_pin_slop)
    """
    if thickness is None:
        thickness = default_hinge_thickness
    if hole_diameter is None:
        hole_diameter = default_hinge_hole_diameter
    if pin_slop is None:
        pin_slop = default_hinge_pin_slop
    return types.SimpleNamespace(thickness=thickness, hole_diameter=hole_diameter, num_segments=num_segments, pin_slop=pin_slop)


def MakeBoxWithFilamentHingeLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    spin: float = 0,
    anchor: list[int] | None = None,
    orient: list[float] | None = None,
    positive_colour: str | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
) -> PyOpenSCAD:
    """Makes a box with a filament hinge on the top.

    The hole for the filament is specified as an argument to the system.
    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakeBoxWithFilamentHingeLid(size=[100, 50, 20])

    Args:
        size:           outside size of the box [width, length, height]
        children:       list of solids/callables to carve inside the box
        wall_thickness: thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        lid_thickness:  thickness of the lid (default default_lid_thickness)
        material_colour: colour (default default_material_colour)
        filament_thickness: thickness of the filament in the hinge (default 2.2)
        hinge_options:  :func:`HingeOptions` result
        print_in_place_offset: wiggle room (default default_print_in_place_offset)
        spin/anchor/orient: BOSL2 positioning
        positive_colour: colour of positive pieces (default default_positive_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset
    if anchor is None:
        anchor = BOTTOM + FRONT + LEFT
    if orient is None:
        orient = TOP
    if positive_colour is None:
        positive_colour = default_positive_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size

    calc_hinge_options = hinge_options if hinge_options is not None else HingeOptions()
    hinge_seg = (
        calc_hinge_options.num_segments if calc_hinge_options.num_segments is not None else max(math.floor(length / 20), 5)
    )
    lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness)
    lip_length = max(length / 4, 15)

    main = bosl2.shapes3d.cuboid(
        [width, length, height - lid_thickness - print_in_place_offset],
        rounding=wall_thickness / 2,
        anchor=BOTTOM + FRONT + LEFT,
        edges=[BOTTOM, FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT],
    )
    main = main.edge_mask(
        [TOP + FRONT, TOP + BACK], children=bosl2.masking.rounding_edge_mask(l=width, r=wall_thickness / 4)
    )
    main = main.edge_mask(
        [TOP + RIGHT], children=bosl2.masking.rounding_edge_mask(l=length, r=wall_thickness / 4)
    )
    main = main.color(material_colour)

    ramp = (
        bosl2.shapes3d.cuboid(
            [calc_hinge_options.thickness * 1.25 + print_in_place_offset, length, wall_thickness + print_in_place_offset],
            anchor=BOTTOM + LEFT + FRONT,
            rounding=-wall_thickness,
            edges=TOP + RIGHT,
        )
        .color(material_colour)
        .translate([0, 0, height - lid_thickness - wall_thickness - print_in_place_offset * 2])
    )
    main = main - ramp

    hinge_cut = bosl2.shapes3d.cuboid(
        [calc_hinge_options.thickness + print_in_place_offset * 4, length, lid_thickness + wall_thickness],
        anchor=TOP + FRONT,
        rounding=calc_hinge_options.thickness / 2,
        edges=[BOTTOM + RIGHT],
    ).translate([calc_hinge_options.thickness / 2 + print_in_place_offset * 2, 0, height - lid_thickness])
    main = main - hinge_cut

    catch_box = bosl2.shapes3d.cuboid(
        [wall_thickness / 2, lip_length + print_in_place_offset * 2, lip_height],
        anchor=BOTTOM + RIGHT,
        rounding=wall_thickness / 4,
        edges=[BOTTOM + LEFT],
    )
    catch_sphere_a = bosl2.shapes3d.sphere(d=wall_thickness, anchor=RIGHT).translate([0, lip_length / 4, lip_height / 2])
    catch_sphere_b = bosl2.shapes3d.sphere(d=wall_thickness, anchor=RIGHT).translate([0, -lip_length / 4, lip_height / 2])
    catch = (catch_box | catch_sphere_a | catch_sphere_b).color(material_colour).translate(
        [width, length / 2, height - lid_thickness - lip_height - print_in_place_offset]
    ).shape
    main = main - catch

    knuckle = (
        pysolidfive.knuckle_hinge(
            length=length,
            segs=hinge_seg,
            offset=calc_hinge_options.thickness,
            knuckle_diam=calc_hinge_options.thickness,
            arm_height=0,
            arm_angle=90,
            clear_top=False,
            inner=True,
            spin=90,
            pin_diam=calc_hinge_options.hole_diameter + calc_hinge_options.pin_slop,
            orient=list(TOP),
            anchor=TOP + BACK + LEFT,
        )
        .color(material_colour)
        .translate([0, 0, height])
    )

    body = main | knuckle

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            body = body - piece.translate([wall_thickness, wall_thickness, floor_thickness])

    result = _apply_reorient(
        body.translate([-width / 2, -length / 2, -height / 2]), anchor, spin, orient, [width, length, height]
    )

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


def FilamentBoxInsideMask(
    size: list[float],
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    print_in_place_offset: float | None = None,
    hinge_options: types.SimpleNamespace | None = None,
) -> PyOpenSCAD:
    """The inside mask to intersect against, so inside cuts don't disturb the hinges.

    Usage::

        FilamentBoxInsideMask([100, 20, 10])

    Args:
        size:           [width, length, height] of the box
        wall_thickness: wall thickness of the box
        floor_thickness: floor thickness of the box
        lid_thickness:  lid thickness of the box
        filament_thickness: filament thickness of the box
        rounding:       rounding of the box
        print_in_place_offset: wiggle room
        hinge_options:  :func:`HingeOptions` result
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    calc_hinge_options = hinge_options if hinge_options is not None else HingeOptions()
    support_width = calc_hinge_options.thickness * 1.25 - wall_thickness
    support_height = support_width + calc_hinge_options.thickness

    body = bosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - floor_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=rounding,
        edges=[BOTTOM, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )

    cut1 = bosl2.shapes3d.cuboid(
        [support_width + print_in_place_offset + 0.5, length + 1, support_height + 1],
        anchor=BOTTOM + FRONT + LEFT,
        chamfer=support_width,
        edges=[BOTTOM + RIGHT],
    ).translate([-0.5, -0.5, height - lid_thickness - support_height - floor_thickness])
    body = body - cut1

    cut2 = bosl2.shapes3d.ycyl(d=calc_hinge_options.thickness + print_in_place_offset, l=length + 1, anchor=FRONT + LEFT + TOP).translate(
        [0, 0.5, height]
    )
    body = body - cut2

    # Unwrapped: the native intersection at the call sites needs a raw solid.
    return body.shape


def MakeLidForFilamentBox(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
) -> PyOpenSCAD:
    """Makes a lid for a box with a filament-based hinge.

    Usage::

        MakeLidForFilamentBox([100, 20, 6])

    Args:
        size:           [width, length, height] of the box
        children:       list of decoration solids placed on top of the lid
        wall_thickness: wall thickness of the box
        floor_thickness: floor thickness of the box
        lid_thickness:  lid thickness of the box
        material_colour: material colour of the box
        filament_thickness: filament thickness of the box
        rounding:       rounding of the box
        hinge_options:  :func:`HingeOptions` result
        print_in_place_offset: wiggle room
        size_spacing:   spacing between pieces (default m_piece_wiggle_room)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room

    width, length, height = size
    calc_hinge_options = hinge_options if hinge_options is not None else HingeOptions()
    hinge_seg = (
        calc_hinge_options.num_segments if calc_hinge_options.num_segments is not None else max(math.floor(length / 20), 5)
    )
    lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness)
    lip_length = max(length / 4, 15)

    top = (
        bosl2.shapes3d.cuboid(
            [width - wall_thickness * 2.5, length, lid_thickness], anchor=BOTTOM + FRONT + LEFT, rounding=lid_thickness / 2, edges=BOTTOM
        )
        .color(material_colour)
        .translate([wall_thickness * 2.5, 0, 0])
    )

    kids = list(children) if children else []
    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=[top] + kids, size_spacing=size_spacing)

    knuckle = pysolidfive.knuckle_hinge(
        length=length,
        segs=hinge_seg,
        offset=calc_hinge_options.thickness,
        knuckle_diam=calc_hinge_options.thickness,
        pin_diam=calc_hinge_options.hole_diameter + calc_hinge_options.pin_slop,
        arm_height=0,
        arm_angle=90,
        clear_top=True,
        spin=270,
        orient=list(LEFT),
        anchor=TOP + FRONT + RIGHT,
    )
    # After anchor=TOP+FRONT+RIGHT, spin=270, orient=LEFT the hinge's declared box lands at
    # x in [0, 1.5*thickness], y in [0, length], z in [0, thickness] -- round its two front
    # vertical edges, which is what the original positioned with _bosl2.edge_mask() (that
    # call never worked; knuckle_hinge had no FFI function form).
    kd = calc_hinge_options.thickness
    edge_round = pysolidfive.rounding_edge_mask(l=width, r=wall_thickness / 2)
    knuckle = knuckle - edge_round.translate([0, 0, kd / 2])
    knuckle = knuckle - edge_round.rotate([0, 0, 90]).translate([kd * 1.5, 0, kd / 2])
    knuckle = knuckle.color(material_colour)

    catch_box = bosl2.shapes3d.cuboid(
        [wall_thickness / 2, lip_length, lip_height + print_in_place_offset], anchor=BOTTOM + RIGHT, rounding=wall_thickness / 4, edges=[TOP + LEFT]
    )
    catch_sphere_a = bosl2.shapes3d.sphere(d=wall_thickness * 5 / 6, anchor=RIGHT).translate([0, lip_length / 4, lip_height / 2])
    catch_sphere_b = bosl2.shapes3d.sphere(d=wall_thickness * 5 / 6, anchor=RIGHT).translate([0, -lip_length / 4, lip_height / 2])
    catch = (catch_box | catch_sphere_a | catch_sphere_b).color(material_colour).translate(
        [width, length / 2, lid_thickness - print_in_place_offset]
    ).shape

    body = lid_stack | knuckle | catch

    hole = bosl2.shapes3d.ycyl(h=length + 1, d=calc_hinge_options.hole_diameter + print_in_place_offset, anchor=FRONT).color(
        material_colour
    ).translate([wall_thickness, 0.5, wall_thickness]).shape
    body = body - hole

    return body


def FilamentHingeBoxLidWithCustomShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    aspect_ratio: float | None = 1.0,
    pattern_inner_control: int = False,
    lid_boundary: float = 10,
    layout_width: float | None = None,
) -> PyOpenSCAD:
    """Makes a lid for a filament-hinge box with a custom repeating pattern.

    Usage::

        FilamentHingeBoxLidWithCustomShape([100, 20, 6], shape_child=circle(r=5))

    Args:
        size:    [width, length, height] of the box
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        wall_thickness/floor_thickness/lid_thickness/material_colour/filament_thickness/rounding/hinge_options/print_in_place_offset/size_spacing: see :func:`MakeLidForFilamentBox`
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        aspect_ratio: dy scale factor (default 1.0)
        pattern_inner_control: inner control mode
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
    """
    if material_colour is None:
        material_colour = default_material_colour
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=[size[0], size[1]],
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

    lid_children = [mesh] + (list(extra_children) if extra_children else [])

    return MakeLidForFilamentBox(
        size=size,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        material_colour=material_colour,
        filament_thickness=filament_thickness,
        rounding=rounding,
        hinge_options=hinge_options,
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        children=lid_children,
    )


def FilamentHingeBoxLidWithShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Makes a lid for a filament-hinge box with a pre-defined shape pattern.

    Usage::

        FilamentHingeBoxLidWithShape([100, 20, 6], shape_options=MakeShapeObject())

    Args:
        size:    [width, length, height] of the box
        shape_child: optional explicit 2-D shape solid (overrides shape_options if given)
        extra_children: additional children (list of solids)
        shape_options: :class:`~shape_type.ShapeObject` (default MakeShapeObject())
        (other args, see :func:`FilamentHingeBoxLidWithCustomShape`)
    """
    if material_colour is None:
        material_colour = default_material_colour

    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    if shape_child is not None:
        pattern_shape = shape_child
    else:
        _shape_raw = ShapeByType(options=calc_shape_options)
        assert _shape_raw is not None, "shape_options must not be ShapeType.NONE here"
        pattern_shape = _shape_raw.color(material_colour)

    return FilamentHingeBoxLidWithCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        material_colour=material_colour,
        filament_thickness=filament_thickness,
        rounding=rounding,
        hinge_options=hinge_options,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        lid_boundary=lid_boundary,
        aspect_ratio=aspect_ratio,
        layout_width=layout_width,
        shape_child=pattern_shape,
        extra_children=extra_children,
    )


def FilamentHingeBoxLidWithLabelAndCustomShape(
    size: list[float],
    text_str: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    label_options: LabelOptions | None = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Makes a lid for a filament-hinge box with a text label and a custom shape.

    Usage::

        FilamentHingeBoxLidWithLabelAndCustomShape([100, 20, 6], "Label", shape_child=circle(r=5))

    Args:
        size:     [width, length, height] of the box
        text_str: the string to use for the label
        shape_child: optional explicit 2-D shape solid for the pattern
        extra_children: additional children (list of solids)
        label_options: :class:`~labels.LabelOptions`
        (other args, see :func:`FilamentHingeBoxLidWithCustomShape`)
    """
    if material_colour is None:
        material_colour = default_material_colour
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    width, length = size[0], size[1]
    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    _label_raw = MakeLidLabel(
            size=[width - wall_thickness - lid_boundary * 2, length - lid_boundary * 2],
            options=label_opts,
            lid_thickness=lid_thickness,
            text_str=text_str,
        )
    assert _label_raw is not None, "label did not generate"
    label_shape = (
        _label_raw
        .mirror([1, 0, 0])
        .mirror([0, 0, 1])
        .translate([width - lid_boundary, lid_boundary, lid_thickness])
    )

    lid_children = [label_shape] + (list(extra_children) if extra_children else [])

    return FilamentHingeBoxLidWithShape(
        size=size,
        shape_child=shape_child,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        material_colour=material_colour,
        filament_thickness=filament_thickness,
        rounding=rounding,
        hinge_options=hinge_options,
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        lid_boundary=lid_boundary,
        aspect_ratio=aspect_ratio,
        layout_width=layout_width,
        shape_options=calc_shape_options,
        extra_children=lid_children,
    )


def FilamentHingeBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    label_options: LabelOptions | None = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    filament_thickness: float = 2.2,
    rounding: float = 0,
    hinge_options: types.SimpleNamespace | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Makes a lid for a filament-hinge box with a text label and an automatic shape.

    Usage::

        FilamentHingeBoxLidWithLabel([100, 20, 6], "Label")

    Args:
        size:     [width, length, height] of the box
        text_str: the string to use for the label
        extra_children: additional children (list of solids)
        label_options: :class:`~labels.LabelOptions`
        shape_options: :class:`~shape_type.ShapeObject`
        (other args, see :func:`FilamentHingeBoxLidWithCustomShape`)
    """
    if material_colour is None:
        material_colour = default_material_colour

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return FilamentHingeBoxLidWithLabelAndCustomShape(
        size=size,
        text_str=text_str,
        label_options=calc_label_options,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        material_colour=material_colour,
        filament_thickness=filament_thickness,
        rounding=rounding,
        hinge_options=hinge_options,
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        lid_boundary=lid_boundary,
        aspect_ratio=aspect_ratio,
        layout_width=layout_width,
        shape_options=calc_shape_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )
