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

# LibFile: hinge_box.py
#    Hinge box pieces for the hinge boxes.
#
# FileSummary: Hinge box pieces for the hinge boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import bosl2.shapes3d
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, IsDenseShapeType, DenseShapeEdges, MakeLidTab
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl

# ---------------------------------------------------------------------------
# Section: Hinges
# ---------------------------------------------------------------------------


def HingeCone(r: float, offset: float) -> "PyOpenSCAD":
    """Makes the hinge cone for use in hinges.

    A 45-degree cone with an inner/outer that can be joined with other
    pieces to make a hinge.

    Usage::

        HingeCone(6, 0.5)

    Args:
        r:      radius of the cone
        offset: how far inside the cone to leave space
    """
    outer = bosl2.shapes3d.cylinder(h=r, r1=r, r2=0, center=False)
    inner = bosl2.shapes3d.cylinder(h=r - offset, r1=r - offset, r2=0, center=False).translate([0, 0, -0.01])
    return (outer - inner).shape


def HingeLineWithSpacingAndNum(
    diameter: float, num: float, spacing: float, offset: float, spin: float = 90
) -> "PyOpenSCAD":
    """Makes a hinge setup in a straight line, given an explicit spacing and count.

    Usage::

        HingeLineWithSpacingAndNum(num=10, spacing=6, diameter=6, offset=0.5)

    Args:
        diameter: diameter of the hinge itself
        num:      number of hinge locations
        spacing:  spacing between hinge spots
        offset:   how much of a space to leave on the conical holes for the hinge
        spin:     how much to rotate one of the legs (default 90)
    """
    num = int(num)
    length = num * diameter

    cyl = bosl2.shapes3d.cylinder(r=diameter / 2, h=length, center=False)
    for i in range(1, num + 1):
        cone = HingeCone(diameter / 2 - 0.01, offset)
        if i % 2 == 1:
            cone = cone.mirror([0, 0, 1])
        cyl = cyl - cone.translate([0, 0, spacing * i])
        if i % 2 == 1:
            ring_outer = bosl2.shapes3d.cylinder(r=diameter, h=diameter + 0.04, center=False).translate(
                [0, 0, spacing * i - 0.02]
            )
            ring_inner = bosl2.shapes3d.cylinder(r=diameter / 2 - offset, h=diameter + 0.06, center=False).translate(
                [0, 0, spacing * i - 0.03]
            )
            cyl = cyl - (ring_outer - ring_inner)

    legs = None
    for i in range(0, num + 1):
        if i % 2 == 1:
            knuckle = (
                bosl2.shapes3d.prismoid(
                    size1=[diameter - offset, diameter],
                    size2=[diameter - offset, diameter],
                    h=diameter / 2 + offset * 2 + 0.01,
                )
                .rotate([0, 90, 0])
                .translate([0, 0, spacing * i + diameter / 2])
                | bosl2.shapes3d.cylinder(r=diameter / 2, h=diameter - offset, center=False).translate(
                    [0, 0, spacing * i + offset / 2]
                )
            ).rotate([0, 0, spin])

            arm_outer = bosl2.shapes3d.cuboid([1 + diameter / 2, diameter, diameter + offset * 3], edges=[TOP + RIGHT, BOTTOM + RIGHT])
            cut_a = bosl2.shapes3d.cylinder(r=diameter / 2 + offset, h=length, center=False).translate(
                [diameter / 4 + offset, 0, -(spacing / 4 + diameter / 2)]
            )
            cut_b = bosl2.shapes3d.cuboid(
                [1 + diameter / 2, diameter, diameter + offset * 3], edges=[TOP + RIGHT, BOTTOM + RIGHT]
            ).translate([offset * 3 / 2, diameter / 2, 0])
            arm = (arm_outer - cut_a - cut_b).translate([-diameter / 4 - offset * 3 / 2, 0, spacing * i + diameter / 2])

            piece = knuckle | arm
        else:
            block_a = bosl2.shapes3d.cuboid(
                [1, diameter, diameter + offset * 3], chamfer=offset * 2, edges=[TOP + RIGHT, BOTTOM + RIGHT]
            ).translate([-diameter / 2 - offset * 3 / 2, 0, spacing * i + diameter / 2])

            box_outer = bosl2.shapes3d.cuboid(
                [diameter / 2 + offset, diameter, diameter], anchor=BOTTOM + FRONT + LEFT
            ).translate([-diameter / 2 - offset, -diameter / 2, spacing * i])
            hole = bosl2.shapes3d.cylinder(d=diameter - 0.02, h=diameter * 4, center=False).translate(
                [0, 0, spacing * i + (i % 2) * (diameter / 2) - offset * 2]
            )
            block_b = box_outer - hole

            piece = block_a | block_b
        legs = piece if legs is None else legs | piece

    combined = (legs | cyl) if legs is not None else cyl
    combined = combined.translate([0, 0, -length / 2])

    bound = bosl2.shapes3d.cuboid([diameter * 2, diameter * 2, length])
    return (bound & combined).rotate([0, 270, 0]).shape


def HingeLine(length: float, diameter: float, offset: float, spin: float = 90) -> "PyOpenSCAD":
    """Makes a hinge setup in a straight line.

    Has pieces that stick out each side wide enough to hook onto edges
    within 0.5 of the side.

    Usage::

        HingeLine(length=60, diameter=6, offset=0.5)

    Args:
        length:   length of the line to hinge
        diameter: diameter of the hinge itself
        offset:   how much of a space to leave on the conical holes for the hinge
        spin:     how much to rotate one of the legs (default 0)
    """
    num = length / diameter
    spacing = length / num
    return HingeLineWithSpacingAndNum(diameter=diameter, offset=offset, spin=spin, num=num, spacing=spacing)


def InsetHinge(length: float, width: float, diameter: float, offset: float) -> PyOpenSCAD:
    """Create a hinge that works and moves in the middle.

    Centers the pieces back on the line with the middle being length/2,
    width/2 and diameter/2; the legs stick down a little to make it easier
    to join onto other parts of the system.

    Usage::

        InsetHinge(length=100, width=20, diameter=6, offset=0.5)

    Args:
        length:   length of the hinge (outside)
        width:    width of the middle piece (outside)
        diameter: diameter of the round piece in the middle
        offset:   how much to offset the middle sections (0.5 is usually good)
    """
    num = length / diameter
    spacing = length / num

    middle = bosl2.shapes3d.cuboid([length, width - diameter * 2 - offset / 2, diameter]).translate([0, width / 2, 0])
    line1 = HingeLineWithSpacingAndNum(diameter=diameter, offset=offset, spin=90, num=num, spacing=spacing).translate(
        [0, diameter / 2, 0]
    )
    line2 = (
        HingeLineWithSpacingAndNum(diameter=diameter, offset=offset, spin=90, num=num, spacing=spacing)
        .mirror([0, 1, 0])
        .translate([0, width - diameter / 2, 0])
    )

    return (middle | line1 | line2).translate([0, -width / 2, 0]).shape


def HingeBoxLidLabel(
    text_str: str,
    inner_width: float,
    inner_length: float,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    size_spacing: float | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Makes a lid for one side of a hinge box with a label and pattern.

    *inner_width*/*inner_length* replace the original SCAD module's
    $inner_width/$inner_length special variables (normally set by the
    enclosing MakeBoxAndLidWithInsetHinge call).

    Usage::

        HingeBoxLidLabel(text_str="Cards", inner_width=100, inner_length=50)

    Args:
        text_str:     the string to use for the label
        inner_width:  interior width available for the lid
        inner_length: interior length available for the lid
        lid_boundary: boundary around the outside for the lid (default 10)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        cap_height:   unused, kept for API compatibility
        layout_width: pattern repeat width (default default_lid_layout_width)
        aspect_ratio: dy scale factor (default 1.0)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        lid_rounding/lid_inner_rounding: unused, kept for API compatibility
        material_colour: colour (default default_material_colour)
        size_spacing: spacing between pieces (default default_slicing_layer_height)
        label_options: :class:`~labels.LabelOptions`
        shape_options: :class:`~shape_type.ShapeObject`
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if size_spacing is None:
        size_spacing = default_slicing_layer_height

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(
        material_colour=material_colour, full_height=True
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    top = bosl2.shapes3d.cuboid(
        [inner_width, inner_length, lid_thickness],
        anchor=BOTTOM + FRONT + LEFT,
    ).color(material_colour)

    _hinge_mesh_raw = ShapeByType(options=calc_shape_options)
    assert _hinge_mesh_raw is not None, "shape_options must not be ShapeType.NONE here"
    _hinge_mesh_shape = _hinge_mesh_raw.color(material_colour)
    mesh = LidMeshBasic(
        size=[inner_width, inner_length],
        lid_thickness=lid_thickness,
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        dense=IsDenseShapeType(calc_shape_options.shape_type),
        dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        children=_hinge_mesh_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_raw = MakeLidLabel(size=[inner_width, inner_length], lid_thickness=lid_thickness, text_str=text_str, options=label_opts)
    assert label_raw is not None, "label did not generate"
    label = label_raw.translate([-inner_width, 0, -lid_thickness]).rotate([0, 180, 0])

    return internal_build_lid(lid_thickness=lid_thickness, children=[top, mesh, label], size_spacing=size_spacing)


def MakeBoxAndLidWithInsetHinge(
    size: list[float],
    children: "list | None" = None,
    hinge_diameter: float = 6,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    hinge_offset: float = 0.3,
    gap: float = 1,
    side_gap: float = 3,
    print_layer_height: float = 0.2,
    lid_thickness: float | None = None,
    prism_width: float = 0.75,
    tab_offset: float = 0.2,
    tab_length: float = 10,
    tab_height: float = 6,
    material_colour: str | None = None,
    print_in_place_offset: float | None = None,
) -> PyOpenSCAD:
    """Makes a box with an inset hinge on the side.

    This is a print-in-place box with a hinge that makes the lid hinge onto
    the top; it is the same height on both sides. *children* is a list of
    up to 4 entries:

        children[0]: carved into the base interior
        children[1]: carved into the lid interior
        children[2]: added on top of the base (not carved)
        children[3]: added on top of the lid (not carved); also punches a
                     matching hole through the lid floor so the piece can
                     pass through it

    Each entry may be a plain solid or a callable(inner_width, inner_length,
    inner_height).

    Usage::

        MakeBoxAndLidWithInsetHinge(size=[100, 50, 20])

    Args:
        size:           outside size of the box [width, length, height]
        children:       list of up to 4 solids/callables (see above)
        hinge_diameter: diameter of the hinge (default 6)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        hinge_offset:   offset for the hinge mechanism (default 0.3)
        gap:            gap between the two box halves (default 1)
        side_gap:       gap on the sides of the hinge (default 3)
        print_layer_height: height of the print layers (default 0.2)
        lid_thickness:  thickness of the lid (default default_lid_thickness)
        prism_width:    width of the prism for the tab (default 0.75)
        tab_offset:     offset for the tab (default 0.2)
        tab_length:     length of the tab (default 10)
        tab_height:     height of the tab (default 6)
        material_colour: colour (default default_material_colour)
        print_in_place_offset: wiggle room between moving parts (default default_print_in_place_offset)
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

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size

    hinge_width = hinge_diameter * 2 + gap
    hinge_length = length - side_gap * 2

    kids = list(children) if children else []

    # --- Base half ---
    base_body = bosl2.shapes3d.cuboid(
        [width, length, height / 2],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)
    latch = (
        MakeLidTab(length=tab_length, height=tab_height, lid_thickness=lid_thickness, prism_width=prism_width, wall_thickness=wall_thickness)
        .color(material_colour)
        .mirror([0, 0, 1])
        .rotate([0, 0, 270])
        .translate([0, length / 2 + tab_length / 2, height / 2 - lid_thickness])
    )
    base_body = base_body | latch

    rim_outer = bosl2.shapes3d.cuboid(
        [width - wall_thickness, length - wall_thickness, wall_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate([wall_thickness / 2, wall_thickness / 2, height / 2 - wall_thickness / 2])
    rim_inner = bosl2.shapes3d.cuboid(
        [
            width - wall_thickness * 2 - print_in_place_offset * 2,
            length - wall_thickness * 2 - print_in_place_offset * 2,
            wall_thickness,
        ],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate([wall_thickness + print_in_place_offset, wall_thickness + print_in_place_offset, height / 2 - wall_thickness / 2])
    base_body = base_body - (rim_outer - rim_inner).color(material_colour)

    base_inner_width = width - wall_thickness - hinge_width
    base_inner_height = height / 2 - floor_thickness
    base_inner_length = length - wall_thickness * 2
    if len(kids) > 0 and kids[0] is not None:
        c0 = ResolveChild(kids[0], base_inner_width, base_inner_length, base_inner_height)
        base_body = base_body - c0.translate([wall_thickness, wall_thickness, floor_thickness])

    if len(kids) > 2 and kids[2] is not None:
        c2 = ResolveChild(kids[2], width - wall_thickness * 2, length - wall_thickness * 2, base_inner_height)
        base_body = base_body | c2.translate([wall_thickness, wall_thickness, -0.01])

    # --- Lid half ---
    lid_body = bosl2.shapes3d.cuboid(
        [width, length, height / 2],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)

    lid_rim_outer = bosl2.shapes3d.cuboid(
        [width - wall_thickness, length - wall_thickness, wall_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP + BACK, TOP + FRONT, TOP + LEFT, TOP + RIGHT],
    ).translate([wall_thickness / 2, wall_thickness / 2, height / 2])
    lid_rim_inner = bosl2.shapes3d.cuboid(
        [
            width - wall_thickness * 2 - print_in_place_offset * 2,
            length - wall_thickness * 2 - print_in_place_offset * 2,
            wall_thickness * 4,
        ],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate([wall_thickness + print_in_place_offset, wall_thickness + print_in_place_offset, height / 2 - wall_thickness])
    lid_body = lid_body | (lid_rim_outer - lid_rim_inner).color(material_colour)

    catch_cutter = (
        minkowski(
            cube(tab_offset * 2).color(material_colour).translate([-tab_offset, -tab_offset, -tab_offset]),
            MakeLidTab(length=tab_length, height=tab_height, lid_thickness=lid_thickness, prism_width=prism_width, wall_thickness=wall_thickness),
        )
        .mirror([0, 1, 0])
        .rotate([0, 0, 270])
        .translate([width + gap - wall_thickness / 2, length / 2 + tab_length / 2, height / 2 + lid_thickness])
        .color(material_colour)
    )
    lid_body = lid_body - catch_cutter

    lid_inner_width = width - wall_thickness - hinge_width
    lid_inner_height = height / 2 - lid_thickness
    lid_inner_length = length - wall_thickness * 2
    if len(kids) > 1 and kids[1] is not None:
        c1 = ResolveChild(kids[1], lid_inner_width, lid_inner_length, lid_inner_height)
        lid_body = lid_body - c1.translate([hinge_width, wall_thickness, lid_thickness])

    if len(kids) > 3 and kids[3] is not None:
        hole = bosl2.shapes3d.cuboid(
            [width - wall_thickness * 2, length - wall_thickness * 2, lid_thickness + 1], anchor=BOTTOM + FRONT + LEFT
        ).translate([wall_thickness, wall_thickness, -1]).color(material_colour)
        lid_body = lid_body - hole

        c3 = ResolveChild(kids[3], width - wall_thickness * 2, length - wall_thickness * 2, lid_inner_height)
        lid_body = lid_body | c3.translate([wall_thickness, wall_thickness, -0.01])

    lid_assembly = lid_body.translate([width + gap, 0, 0])

    combined = base_body | lid_assembly

    hinge_pocket = (
        cube([hinge_width + print_in_place_offset * 2 + 0.02, hinge_length + print_in_place_offset * 2, hinge_diameter + 5 + hinge_offset + 1])
        .color(material_colour)
        .translate(
            [
                width - hinge_diameter - 0.01 - print_in_place_offset,
                side_gap - print_in_place_offset,
                height / 2 - hinge_diameter - print_layer_height - hinge_offset,
            ]
        )
    )
    combined = combined - hinge_pocket

    hinge = (
        InsetHinge(length=hinge_length, width=hinge_width, offset=hinge_offset, diameter=hinge_diameter)
        .color(material_colour)
        .rotate([0, 0, 90])
        .translate([width + gap / 2, hinge_length / 2 + side_gap, height / 2 - hinge_diameter / 2 - hinge_offset])
    )

    return combined | hinge
