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

# LibFile: sliding_catch_box.py
#    Sliding catch box and lid generators.
#
# FileSummary: Sliding catch box pieces for the sliding catch boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pysolidfive
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, SlidingLidFingernail
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


def MakeBoxWithSlidingCatchLid(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    top_thickness: float = 2,
    floor_thickness: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Creates a box with a sliding catch lid on the top.

    A lid that slides into a groove on the top and the front to catch -- a
    bit harder to stack but makes a nice simple, sturdy box. The lid is
    thicker than a sliding lid box.

    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakeBoxWithSlidingCatchLid([100, 50, 20])

    Args:
        size:            [width, length, height] of the box
        children:        list of solids to carve inside the box
        lid_thickness:   thickness of the lid (default default_lid_thickness)
        wall_thickness:  thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        top_thickness:   thickness above the catch (default 2)
        material_colour: colour (default default_material_colour)
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

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size

    calc_sliding_len = (length - wall_thickness) / 6

    body = pysolidfive.cuboid(
        [width, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    )

    middle = pysolidfive.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height], anchor=BOTTOM + FRONT + LEFT
    ).translate([wall_thickness, wall_thickness, floor_thickness])
    body = body - middle

    body = body - pysolidfive.cuboid(
        [width + 1, calc_sliding_len + 1, lid_thickness + size_spacing],
        anchor=FRONT + LEFT + BOTTOM,
        rounding=lid_thickness / 2,
        edges=[BACK + BOTTOM],
    ).translate([-0.5, wall_thickness + calc_sliding_len, height - lid_thickness - top_thickness])

    body = body - pysolidfive.cuboid(
        [width + 1, calc_sliding_len + size_spacing * 2, lid_thickness + top_thickness + size_spacing],
        anchor=FRONT + LEFT + BOTTOM,
        rounding=lid_thickness / 2,
        edges=[BACK + BOTTOM],
    ).translate(
        [-0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - lid_thickness - top_thickness]
    )

    body = body - pysolidfive.cuboid(
        [width + 1, calc_sliding_len + size_spacing * 2, top_thickness - size_spacing],
        anchor=FRONT + LEFT + BOTTOM,
        rounding=-top_thickness / 2,
        edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK],
    ).translate(
        [-0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - top_thickness + size_spacing]
    )

    body = body - pysolidfive.cuboid(
        [width + 1, calc_sliding_len + 1, lid_thickness + size_spacing],
        rounding=lid_thickness,
        anchor=FRONT + LEFT + BOTTOM,
        edges=[BACK + TOP],
    ).translate(
        [-0.5, wall_thickness + length - calc_sliding_len * 2 - size_spacing * 2, height - lid_thickness - top_thickness]
    )

    body = body - pysolidfive.cuboid(
        [width + 1, calc_sliding_len + size_spacing * 2 + 1, lid_thickness + top_thickness + size_spacing],
        anchor=FRONT + LEFT + BOTTOM,
        rounding=lid_thickness / 2,
        edges=[BACK + BOTTOM],
    ).translate([-0.5, length - calc_sliding_len - size_spacing * 2, height - lid_thickness - top_thickness])

    body = body - pysolidfive.cuboid(
        [width + 1, wall_thickness + calc_sliding_len + size_spacing * 2, top_thickness - size_spacing],
        anchor=FRONT + LEFT + BOTTOM,
        rounding=-top_thickness / 2,
        edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK],
    ).translate(
        [
            -0.5,
            wall_thickness + length - calc_sliding_len - wall_thickness - size_spacing * 2,
            height - top_thickness + size_spacing,
        ]
    )

    # Everything above is one symbolic SDF; .color() meshes it once, so the native child
    # subtractions below get a plain solid.
    body = body.color(material_colour)

    # Children are only carved in the interior area (not the walls).
    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    if children:
        bound = cube([inner_width, inner_length, height + 2]).color(material_colour)
        kids_shape = None
        for c in children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            kids_shape = piece if kids_shape is None else kids_shape | piece
        if kids_shape is not None:
            body = body - (bound & kids_shape).translate([wall_thickness, wall_thickness, floor_thickness])

    return body


def SlidingCatchBoxLid(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    top_thickness: float = 2,
    fill_middle: bool = True,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """The sliding catch lid for a box.

    Usage::

        SlidingCatchBoxLid([100, 50])

    Args:
        size:            [width, length] of the lid
        children:        list of label/decoration solids placed on top of the lid
        lid_thickness:   thickness of the lid (default default_lid_thickness)
        wall_thickness:  thickness of the walls (default default_wall_thickness)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        top_thickness:   thickness above the catch (default 2)
        fill_middle:     if the middle of the lid should be filled (default True)
        lid_rounding:    rounding on the edge of the lid (default top_thickness/2)
        material_colour: colour (default default_material_colour)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]

    calc_sliding_len = (length - wall_thickness) / 6
    calc_lid_thickness = lid_thickness + top_thickness if fill_middle else lid_thickness
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = top_thickness / 2

    base = pysolidfive.cuboid(
        [width, length - wall_thickness, lid_thickness - size_spacing], anchor=BOTTOM + FRONT + LEFT
    )
    if fill_middle:
        fill = pysolidfive.cuboid(
            [width - wall_thickness * 2 - size_spacing * 2, length, top_thickness + 0.1],
            anchor=FRONT + LEFT + BOTTOM,
            rounding=calc_lid_rounding,
            edges=TOP,
        ).translate([wall_thickness, 0, lid_thickness - 0.1])
        base = fill | base

    def _cut(size_y: float, tx: float, ty: float) -> "pysolidfive.PyShape":
        cut_w = wall_thickness + size_spacing + 1
        return pysolidfive.cuboid(
            [cut_w, size_y, lid_thickness + 1], anchor=BOTTOM + FRONT + LEFT
        ).translate([tx, ty, -0.5])

    front_a = _cut(wall_thickness + calc_sliding_len + 1, -1, -1)
    front_b = _cut(wall_thickness + calc_sliding_len + 1, width - wall_thickness - size_spacing, -1)
    mid_a = _cut(wall_thickness + calc_sliding_len * 2, -1, calc_sliding_len * 2)
    mid_b = _cut(wall_thickness + calc_sliding_len * 2, width - wall_thickness - size_spacing, calc_sliding_len * 2)
    end_a = _cut(wall_thickness + calc_sliding_len + 1, -1, calc_sliding_len * 5)
    end_b = _cut(wall_thickness + calc_sliding_len + 1, width - wall_thickness - size_spacing, calc_sliding_len * 5)

    # One symbolic SDF for the whole finger layout; .color() meshes it once for
    # internal_build_lid()'s native union with the label/pattern children.
    lid_top = (base - front_a - front_b - mid_a - mid_b - end_a - end_b).color(material_colour)

    kids = list(children) if children else []
    lid_children = [lid_top] + [c.translate([wall_thickness, 0, 0]) for c in kids]

    return internal_build_lid(lid_thickness=calc_lid_thickness, children=lid_children, size_spacing=size_spacing)


def SlidingCatchBoxLidWithLabelAndCustomShape(
    size: list[float],
    text_str: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float = 1.0,
    font: str | None = None,
    lid_rounding: float | None = None,
    wall_thickness: float | None = None,
    top_thickness: float = 2,
    fill_middle: bool = True,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a sliding catch box, with a repeating pattern and a label.

    Usage::

        SlidingCatchBoxLidWithLabelAndCustomShape([100, 50], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size:            [width, length] of the lid
        text_str:        label text
        shape_child:     2-D shape solid to tile on the lid
        extra_children:  additional children (list of solids)
        lid_boundary:    boundary around the outside for the lid (default 10)
        layout_width:    pattern repeat width (default default_lid_layout_width)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_thickness:   thickness of the lid (default default_lid_thickness)
        aspect_ratio:    dy scale factor (default 1.0)
        font:            unused, kept for API compatibility (set via label_options instead)
        lid_rounding:    rounding on the edge of the lid (default wall_thickness/2)
        wall_thickness:  thickness of the walls (default default_wall_thickness)
        top_thickness:   thickness above the catch (default 2)
        fill_middle:     if the middle of the lid should be filled (default True)
        material_colour: colour (default default_material_colour)
        pattern_inner_control: inner control mode (default False)
        label_options:   :class:`~labels.LabelOptions`
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]

    calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=size,
        lid_thickness=lid_thickness,
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        inner_control=pattern_inner_control,
        children=pattern_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = False
    label_shape = MakeLidLabel(size=[width, length], lid_thickness=lid_thickness, text_str=text_str, options=label_opts)

    fingernail = cube(
        [width - calc_label_options.border, length - calc_label_options.border, lid_thickness]
    ).color(material_colour) & SlidingLidFingernail(lid_thickness).color(material_colour).translate(
        [width / 2, length - calc_label_options.border - 3, 0]
    ).shape

    lid_children = [mesh, label_shape, fingernail] + (list(extra_children) if extra_children else [])

    return SlidingCatchBoxLid(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        top_thickness=top_thickness,
        fill_middle=fill_middle,
        material_colour=material_colour,
        children=lid_children,
    )


def SlidingCatchBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    top_thickness: float = 2,
    fill_middle: bool = True,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Lid for a sliding catch box with an automatic label and shape pattern.

    Usage::

        SlidingCatchBoxLidWithLabel([100, 50], text_str="Frog")

    Args:
        size:            [width, length] of the lid
        text_str:        label text
        extra_children:  additional children (list of solids)
        lid_boundary:    boundary around the outside for the lid (default 10)
        wall_thickness:  thickness of the walls (default default_wall_thickness)
        layout_width:    pattern repeat width (default default_lid_layout_width)
        aspect_ratio:    dy scale factor (default default_lid_aspect_ratio)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_thickness:   thickness of the lid (default default_lid_thickness)
        top_thickness:   thickness above the catch (default 2)
        fill_middle:     if the middle of the lid should be filled (default True)
        lid_rounding:    rounding on the edge of the lid
        material_colour: colour (default default_material_colour)
        label_options:   :class:`~labels.LabelOptions`
        shape_options:   :class:`~shape_type.ShapeObject`
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
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    calc_lid_thickness = lid_thickness + top_thickness if fill_middle else lid_thickness

    shape_piece = ShapeByType(options=calc_shape_options).color(material_colour)

    return SlidingCatchBoxLidWithLabelAndCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=calc_lid_thickness,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_boundary=lid_boundary,
        top_thickness=top_thickness,
        fill_middle=fill_middle,
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        label_options=calc_label_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )
