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

# LibFile: magnetic_box.py
#    Magnetic box and lid generators.
#
# FileSummary: Magnetic box pieces for the magnetic boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.shapes3d
from lids_base import (
    internal_build_lid,
    MakeLidLabel,
    LidMeshBasic,
    build_lid_overlays,
    SlidingLidFingernail,
    IsDenseShapeType,
    DenseShapeEdges,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from box_base import BoxBaseType, BoxSpec
from dataclasses import dataclass


def MakeBoxWithMagneticLid(
    size: list[float],
    magnet_diameter: float,
    magnet_thickness: float,
    children: "list | None" = None,
    lid_thickness: float | None = None,
    magnet_border: float = 1.5,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Makes a box with holes for round magnets in the corners.

    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakeBoxWithMagneticLid(size=[100, 50, 20], magnet_diameter=5, magnet_thickness=1)

    Args:
        size:              [width, length, height] outside size of the box
        magnet_diameter:   diameter of the magnet
        magnet_thickness:  thickness of the magnet
        children:          list of solids to carve inside the box
        lid_thickness:     thickness of the lid (default default_lid_thickness)
        magnet_border:     space around the edges of the magnet (default 1.5)
        wall_thickness:    thickness of the walls (default default_wall_thickness)
        floor_thickness:   thickness of the floor (default default_floor_thickness)
        material_colour:   colour (default default_material_colour)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert magnet_diameter is not None and magnet_diameter > 0, f"Magnet diameter needs to be set {magnet_diameter}"
    assert magnet_thickness is not None and magnet_thickness > 0, f"Magnet thickness needs to be set {magnet_thickness}"
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert height > 0, f"Height needs to be set {height}"

    body = pybosl2.shapes3d.cuboid(
        [width, length, height - lid_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    )

    z = height - lid_thickness - magnet_thickness
    for cx, cy in (
        (magnet_diameter / 2 + magnet_border, magnet_diameter / 2 + magnet_border),
        (width - magnet_diameter / 2 - magnet_border, magnet_diameter / 2 + magnet_border),
        (width - magnet_diameter / 2 - magnet_border, length - magnet_diameter / 2 - magnet_border),
        (magnet_diameter / 2 + magnet_border, length - magnet_diameter / 2 - magnet_border),
    ):
        hole = pybosl2.shapes3d.cyl(diameter=magnet_diameter, height=magnet_thickness + 1, anchor=BOTTOM).translate([cx, cy, z])
        body = body - hole

    body = body.color(material_colour)

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    if children:
        kids_shape = None
        for c in children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            kids_shape = piece if kids_shape is None else kids_shape | piece
        if kids_shape is not None:
            body = body - kids_shape.translate([wall_thickness, wall_thickness, floor_thickness])

    return body.shape


def MakeBoxWithMagneticLidInsideSpace(
    size: list[float],
    magnet_diameter: float,
    magnet_thickness: float,
    lid_thickness: float | None = None,
    magnet_border: float = 1.5,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    full_height: bool = False,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Makes the inside-space template for a magnetic box.

    Used to intersect against to pull the corners safely out of the way of
    the magnet holes.

    Usage::

        MakeBoxWithMagneticLidInsideSpace(size=[100, 50, 20], magnet_diameter=5, magnet_thickness=1)

    Args:
        size:              [width, length, height] outside size of the box
        magnet_diameter:   diameter of the magnet
        magnet_thickness:  thickness of the magnet
        lid_thickness:     thickness of the lid (default default_lid_thickness)
        magnet_border:     space around the edges of the magnet (default 1.5)
        wall_thickness:    thickness of the walls (default default_wall_thickness)
        floor_thickness:   thickness of the floor (default default_floor_thickness)
        full_height:       if the cylinder should be the full height of the box (default False)
        material_colour:   colour (default default_material_colour)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert height > 0, f"Height needs to be set {height}"
    assert magnet_diameter is not None and magnet_diameter > 0, f"Magnet diameter needs to be set {magnet_diameter}"
    assert magnet_thickness is not None and magnet_thickness > 0, f"Magnet thickness needs to be set {magnet_thickness}"

    def make_side_cylinder(box_size: float) -> "PyOpenSCAD":
        actual_height = (height - lid_thickness - floor_thickness) if full_height else box_size
        shape = None

        if full_height:
            offset = wall_thickness
            piece = pybosl2.shapes3d.cyl(height=actual_height, diameter=box_size, anchor=BOTTOM).translate(
                [
                    -offset + box_size / 2,
                    -offset + box_size / 2,
                    height - lid_thickness - floor_thickness - actual_height,
                ]
            )
            shape = piece
        else:
            piece1 = pybosl2.shapes3d.cyl(height=magnet_thickness * 1.5, diameter=box_size, anchor=BOTTOM).translate(
                [
                    -wall_thickness + box_size / 2,
                    -wall_thickness + box_size / 2,
                    height - lid_thickness - floor_thickness - magnet_thickness * 1.5,
                ]
            )
            offset = wall_thickness + box_size / 2 - wall_thickness
            piece2 = pybosl2.shapes3d.cyl(
                height=actual_height + 0.01,
                diameter2=box_size,
                diameter1=0,
                anchor=BOTTOM,
                shift=[box_size / 2 - wall_thickness, box_size / 2 - wall_thickness],
            ).translate(
                [
                    -offset + box_size / 2,
                    -offset + box_size / 2,
                    height - lid_thickness - floor_thickness - actual_height - magnet_thickness * 1.5,
                ]
            )
            shape = piece1 | piece2

        side_radius = box_size / 2 - wall_thickness
        if side_radius > 0 and full_height:
            wedge_a = pybosl2.shapes3d.prismoid(
                size1=[side_radius * 2, side_radius * 2],
                size2=[side_radius * 2, side_radius * 2],
                height=actual_height,
                anchor=BOTTOM,
            ).translate(
                [
                    -wall_thickness + box_size,
                    -wall_thickness + box_size / 2 - side_radius,
                    height - lid_thickness - floor_thickness - actual_height,
                ]
            )
            cut_a = pybosl2.shapes3d.cyl(radius=side_radius, height=actual_height + 1, anchor=BOTTOM).translate(
                [
                    -wall_thickness + box_size + side_radius,
                    -wall_thickness + box_size / 2,
                    height - lid_thickness - floor_thickness - actual_height,
                ]
            )
            shape = shape | (wedge_a - cut_a)

            wedge_b = pybosl2.shapes3d.prismoid(
                size1=[side_radius * 2, side_radius * 2],
                size2=[side_radius * 2, side_radius * 2],
                height=actual_height,
                anchor=BOTTOM,
            ).translate(
                [
                    -wall_thickness + box_size / 2 - side_radius,
                    -wall_thickness + box_size,
                    height - lid_thickness - floor_thickness - actual_height,
                ]
            )
            cut_b = pybosl2.shapes3d.cyl(radius=side_radius, height=actual_height + 1, anchor=BOTTOM).translate(
                [
                    -wall_thickness + box_size / 2,
                    -wall_thickness + box_size + side_radius,
                    height - lid_thickness - floor_thickness - actual_height,
                ]
            )
            shape = shape | (wedge_b - cut_b)

        assert shape is not None
        return shape.shape

    box_size = magnet_diameter + magnet_border * 2
    base = pybosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - lid_thickness - floor_thickness + 0.1],
        anchor=BOTTOM + FRONT + LEFT,
    )

    base = base - make_side_cylinder(box_size)
    base = base - make_side_cylinder(box_size).rotate([0, 0, 90]).translate([width - wall_thickness * 2, 0, 0])
    base = base - make_side_cylinder(box_size).rotate([0, 0, 180]).translate(
        [width - wall_thickness * 2, length - wall_thickness * 2, 0]
    )
    base = base - make_side_cylinder(box_size).rotate([0, 0, 270]).translate([0, length - wall_thickness * 2, 0])

    # One symbolic SDF; .color() meshes it for the native intersection at the call sites.
    return base.color(material_colour)


def MagneticBoxLid(
    size: list[float],
    magnet_diameter: float,
    magnet_thickness: float,
    children: "list | None" = None,
    magnet_border: float = 1.5,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    lid_rounding: float | None = None,
    size_spacing: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """The magnetic-lid lid.

    Usage::

        MagneticBoxLid([100, 50], 5, 1)

    Args:
        size:              [width, length] of the lid
        magnet_diameter:   diameter of the magnet
        magnet_thickness:  thickness of the magnet
        children:          list of label/decoration solids placed on top of the lid
        magnet_border:     space around the edges of the magnet (default 1.5)
        lid_thickness:     thickness of the lid (default default_lid_thickness)
        wall_thickness:    thickness of the walls (default default_wall_thickness)
        lid_rounding:      rounding on the edge of the lid (default wall_thickness)
        size_spacing:      wiggle room (default m_piece_wiggle_room)
        material_colour:   colour (default default_material_colour)
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
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert magnet_diameter is not None and magnet_diameter > 0, f"Magnet diameter needs to be set {magnet_diameter}"
    assert magnet_thickness is not None and magnet_thickness > 0, f"Magnet thickness needs to be set {magnet_thickness}"

    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness

    top = pybosl2.shapes3d.cuboid(
        [width, length, lid_thickness],
        rounding=calc_lid_rounding,
        anchor=BOTTOM + FRONT + LEFT,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    )

    for cx, cy in (
        (magnet_diameter / 2 + magnet_border, magnet_diameter / 2 + magnet_border),
        (width - magnet_diameter / 2 - magnet_border, magnet_diameter / 2 + magnet_border),
        (width - magnet_diameter / 2 - magnet_border, length - magnet_diameter / 2 - magnet_border),
        (magnet_diameter / 2 + magnet_border, length - magnet_diameter / 2 - magnet_border),
    ):
        hole = pybosl2.shapes3d.cyl(diameter=magnet_diameter, height=magnet_thickness + 1, anchor=BOTTOM).translate([cx, cy, -1])
        top = top - hole

    # Meshed once here so internal_build_lid()'s native union gets a plain solid.
    top = top.color(material_colour)

    kids = list(children) if children else []
    lid_children = [top] + [c.translate([wall_thickness, 0, 0]) for c in kids]

    return internal_build_lid(lid_thickness=lid_thickness, children=lid_children, size_spacing=size_spacing)


def MagneticBoxLidWithLabelAndCustomShape(
    size: list[float],
    magnet_diameter: float,
    magnet_thickness: float,
    text_str: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    wall_thickness: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    pattern_inner_control: int = False,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a magnetic box with a repeating pattern and a label.

    Usage::

        MagneticBoxLidWithLabelAndCustomShape([100, 50], 5, 1, text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size:              [width, length] of the lid
        magnet_diameter:   diameter of the magnet
        magnet_thickness:  thickness of the magnet
        text_str:          label text
        shape_child:       2-D shape solid to tile on the lid
        extra_children:    additional children (list of solids)
        lid_boundary:      boundary around the lid edge (default 10)
        layout_width:      pattern repeat width (default default_lid_layout_width)
        size_spacing:      wiggle room (default m_piece_wiggle_room)
        lid_thickness:     thickness of the lid (default default_lid_thickness)
        aspect_ratio:      dy scale factor (default 1.0)
        lid_rounding:      rounding on the edge of the lid
        wall_thickness:    thickness of the walls (default default_wall_thickness)
        lid_pattern_dense: use dense layout (default False)
        lid_dense_shape_edges: dense edge count (default 6)
        pattern_inner_control: inner control mode (default False)
        material_colour:   colour (default default_material_colour)
        label_options:     :class:`~labels.LabelOptions`
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
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert magnet_diameter is not None and magnet_diameter > 0, f"Magnet diameter needs to be set {magnet_diameter}"
    assert magnet_thickness is not None and magnet_thickness > 0, f"Magnet thickness needs to be set {magnet_thickness}"
    assert text_str is not None, f"Text string needs to be set {text_str}"

    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )

    fingernail = pybosl2.shapes3d.cuboid(
        [width - calc_label_options.border, length - calc_label_options.border, lid_thickness],
        anchor=BOTTOM + FRONT + LEFT,
    ).color(material_colour) & SlidingLidFingernail(lid_thickness).color(material_colour).translate(
        [width / 2, length - calc_label_options.border - 3, 0]
    )

    lid_children = build_lid_overlays(
        lid_thickness=lid_thickness,
        size=size,
        label_size=[width, length],
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        shape_child=shape_child,
        dense=lid_pattern_dense,
        dense_shape_edges=lid_dense_shape_edges,
        inner_control=pattern_inner_control,
        text_str=text_str,
        label_options=calc_label_options,
        extra_children=[fingernail] + (list(extra_children) if extra_children else []),
        material_colour=material_colour,
    )

    return MagneticBoxLid(
        size=size,
        magnet_diameter=magnet_diameter,
        magnet_thickness=magnet_thickness,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        material_colour=material_colour,
        children=lid_children,
    )


def MagneticBoxLidWithLabel(
    size: list[float],
    magnet_diameter: float,
    magnet_thickness: float,
    text_str: str,
    magnet_border: float = 1.5,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
    extra_children: "list | None" = None,
) -> PyOpenSCAD:
    """Lid for a magnetic box with an automatic label and shape pattern.

    Usage::

        MagneticBoxLidWithLabel([100, 50], 5, 1, text_str="Frog")

    Args:
        size:              [width, length] of the lid
        magnet_diameter:   diameter of the magnet
        magnet_thickness:  thickness of the magnet
        text_str:          label text
        magnet_border:     space around the edges of the magnet (default 1.5)
        lid_boundary:      boundary around the lid edge (default 10)
        layout_width:      pattern repeat width (default default_lid_layout_width)
        aspect_ratio:      dy scale factor (default default_lid_aspect_ratio)
        lid_thickness:     thickness of the lid (default default_lid_thickness)
        wall_thickness:    thickness of the walls (default default_wall_thickness)
        size_spacing:      wiggle room (default m_piece_wiggle_room)
        lid_rounding:      rounding on the edge of the lid
        material_colour:   colour (default default_material_colour)
        label_options:     :class:`~labels.LabelOptions`
        shape_options:     :class:`~shape_type.ShapeObject`
        extra_children:    additional children (list of solids)
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
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert magnet_diameter is not None and magnet_diameter > 0, f"Magnet diameter needs to be set {magnet_diameter}"
    assert magnet_thickness is not None and magnet_thickness > 0, f"Magnet thickness needs to be set {magnet_thickness}"
    assert text_str is not None, f"Text string needs to be set {text_str}"

    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return MagneticBoxLidWithLabelAndCustomShape(
        size=size,
        magnet_diameter=magnet_diameter,
        magnet_thickness=magnet_thickness,
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
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        material_colour=material_colour,
        label_options=calc_label_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )


@dataclass
class MagneticBoxOptions:
    """Magnetic-box options; pass via ``BoxSpec(type_options=MakeMagneticBoxOptions(...))``."""

    magnet_diameter: float = 5
    magnet_thickness: float = 2
    magnet_border: float = 1.5


def MakeMagneticBoxOptions(**kwargs) -> MagneticBoxOptions:
    return MagneticBoxOptions(**kwargs)


class MagneticBox(BoxBaseType):
    """A box whose lid is held on by magnets set into the corners, on the new box
    system. Box and lid are separate prints; magnets are glued into both.

    Magnet size comes from ``BoxSpec(type_options=MakeMagneticBoxOptions(
    magnet_diameter=5, magnet_thickness=2))``. ``contents`` are carved into the box.

    Usage::

        from box_base import BoxSpec
        from magnetic_box import MagneticBox, MakeMagneticBoxOptions

        box = MagneticBox(BoxSpec(size=[100, 50, 20], label="mag",
                                  type_options=MakeMagneticBoxOptions(magnet_diameter=6, magnet_thickness=2)))
        box.make_box().show()
        box.make_lid().show()
    """

    def _opts(self) -> MagneticBoxOptions:
        o = self._spec.type_options
        return o if isinstance(o, MagneticBoxOptions) else MagneticBoxOptions()

    def _children(self, contents):
        if contents is None:
            contents = self._spec.contents
        return [io.value for io in self._resolve_contents(contents)] or None

    def make_box(self, *, contents=None, finger_holes=None):
        o = self._opts()
        return MakeBoxWithMagneticLid(
            size=[self.width, self.length, self.height],
            magnet_diameter=o.magnet_diameter,
            magnet_thickness=o.magnet_thickness,
            children=self._children(contents),
            lid_thickness=self.lid_thickness,
            magnet_border=o.magnet_border,
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            material_colour=self.material_colour,
        )

    def make_lid(self, lid=None):
        o = self._opts()
        return MagneticBoxLid(
            size=[self.width, self.length, self.height],
            magnet_diameter=o.magnet_diameter,
            magnet_thickness=o.magnet_thickness,
            lid_thickness=self.lid_thickness,
            magnet_border=o.magnet_border,
            wall_thickness=self.wall_thickness,
            material_colour=self.material_colour,
        )

    def _build_box_body(self):
        raise NotImplementedError("MagneticBox builds its body in make_box()")
