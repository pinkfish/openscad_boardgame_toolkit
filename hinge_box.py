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
import pybosl2.shapes3d
from lids_base import MakeLidTab
from box_base import BoxBaseType, BoxSpec, BoxTypeOptions
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Section: Hinges
# ---------------------------------------------------------------------------


def _hinge_cone(r: float, offset: float) -> "PyOpenSCAD":
    """Makes the hinge cone for use in hinges.

    A 45-degree cone with an inner/outer that can be joined with other
    pieces to make a hinge.

    Usage::

        _hinge_cone(6, 0.5)

    Args:
        r:      radius of the cone
        offset: how far inside the cone to leave space
    """
    outer = pybosl2.shapes3d.cylinder(height=r, radius1=r, radius2=0, center=False)
    inner = pybosl2.shapes3d.cylinder(height=r - offset, radius1=r - offset, radius2=0, center=False).translate([0, 0, -0.01])
    return (outer - inner).shape


def _hinge_line_with_spacing_and_num(
    diameter: float, num: float, spacing: float, offset: float, spin: float = 90
) -> "PyOpenSCAD":
    """Makes a hinge setup in a straight line, given an explicit spacing and count.

    Usage::

        _hinge_line_with_spacing_and_num(num=10, spacing=6, diameter=6, offset=0.5)

    Args:
        diameter: diameter of the hinge itself
        num:      number of hinge locations
        spacing:  spacing between hinge spots
        offset:   how much of a space to leave on the conical holes for the hinge
        spin:     how much to rotate one of the legs (default 90)
    """
    num = int(num)
    length = num * diameter

    cyl = pybosl2.shapes3d.cylinder(radius=diameter / 2, height=length, center=False)
    for i in range(1, num + 1):
        cone = _hinge_cone(diameter / 2 - 0.01, offset)
        if i % 2 == 1:
            cone = cone.mirror([0, 0, 1])
        cyl = cyl - cone.translate([0, 0, spacing * i])
        if i % 2 == 1:
            ring_outer = pybosl2.shapes3d.cylinder(radius=diameter, height=diameter + 0.04, center=False).translate(
                [0, 0, spacing * i - 0.02]
            )
            ring_inner = pybosl2.shapes3d.cylinder(radius=diameter / 2 - offset, height=diameter + 0.06, center=False).translate(
                [0, 0, spacing * i - 0.03]
            )
            cyl = cyl - (ring_outer - ring_inner)

    legs = None
    for i in range(0, num + 1):
        if i % 2 == 1:
            knuckle = (
                pybosl2.shapes3d.prismoid(
                    size1=[diameter - offset, diameter],
                    size2=[diameter - offset, diameter],
                    height=diameter / 2 + offset * 2 + 0.01,
                )
                .rotate([0, 90, 0])
                .translate([0, 0, spacing * i + diameter / 2])
                | pybosl2.shapes3d.cylinder(radius=diameter / 2, height=diameter - offset, center=False).translate(
                    [0, 0, spacing * i + offset / 2]
                )
            ).rotate([0, 0, spin])

            arm_outer = pybosl2.shapes3d.cuboid(
                [1 + diameter / 2, diameter, diameter + offset * 3], edges=[TOP + RIGHT, BOTTOM + RIGHT]
            )
            cut_a = pybosl2.shapes3d.cylinder(radius=diameter / 2 + offset, height=length, center=False).translate(
                [diameter / 4 + offset, 0, -(spacing / 4 + diameter / 2)]
            )
            cut_b = pybosl2.shapes3d.cuboid(
                [1 + diameter / 2, diameter, diameter + offset * 3], edges=[TOP + RIGHT, BOTTOM + RIGHT]
            ).translate([offset * 3 / 2, diameter / 2, 0])
            arm = (arm_outer - cut_a - cut_b).translate([-diameter / 4 - offset * 3 / 2, 0, spacing * i + diameter / 2])

            piece = knuckle | arm
        else:
            block_a = pybosl2.shapes3d.cuboid(
                [1, diameter, diameter + offset * 3], chamfer=offset * 2, edges=[TOP + RIGHT, BOTTOM + RIGHT]
            ).translate([-diameter / 2 - offset * 3 / 2, 0, spacing * i + diameter / 2])

            box_outer = pybosl2.shapes3d.cuboid(
                [diameter / 2 + offset, diameter, diameter], anchor=BOTTOM + FRONT + LEFT
            ).translate([-diameter / 2 - offset, -diameter / 2, spacing * i])
            hole = pybosl2.shapes3d.cylinder(diameter=diameter - 0.02, height=diameter * 4, center=False).translate(
                [0, 0, spacing * i + (i % 2) * (diameter / 2) - offset * 2]
            )
            block_b = box_outer - hole

            piece = block_a | block_b
        legs = piece if legs is None else legs | piece

    combined = (legs | cyl) if legs is not None else cyl
    combined = combined.translate([0, 0, -length / 2])

    bound = pybosl2.shapes3d.cuboid([diameter * 2, diameter * 2, length])
    return (bound & combined).rotate([0, 270, 0]).shape


def _hinge_line(length: float, diameter: float, offset: float, spin: float = 90) -> "PyOpenSCAD":
    """Makes a hinge setup in a straight line.

    Has pieces that stick out each side wide enough to hook onto edges
    within 0.5 of the side.

    Usage::

        _hinge_line(length=60, diameter=6, offset=0.5)

    Args:
        length:   length of the line to hinge
        diameter: diameter of the hinge itself
        offset:   how much of a space to leave on the conical holes for the hinge
        spin:     how much to rotate one of the legs (default 0)
    """
    num = length / diameter
    spacing = length / num
    return _hinge_line_with_spacing_and_num(diameter=diameter, offset=offset, spin=spin, num=num, spacing=spacing)


def _inset_hinge(length: float, width: float, diameter: float, offset: float) -> PyOpenSCAD:
    """Create a hinge that works and moves in the middle.

    Centers the pieces back on the line with the middle being length/2,
    width/2 and diameter/2; the legs stick down a little to make it easier
    to join onto other parts of the system.

    Usage::

        _inset_hinge(length=100, width=20, diameter=6, offset=0.5)

    Args:
        length:   length of the hinge (outside)
        width:    width of the middle piece (outside)
        diameter: diameter of the round piece in the middle
        offset:   how much to offset the middle sections (0.5 is usually good)
    """
    num = length / diameter
    spacing = length / num

    middle = pybosl2.shapes3d.cuboid([length, width - diameter * 2 - offset / 2, diameter]).translate([0, width / 2, 0])
    line1 = _hinge_line_with_spacing_and_num(diameter=diameter, offset=offset, spin=90, num=num, spacing=spacing).translate(
        [0, diameter / 2, 0]
    )
    line2 = (
        _hinge_line_with_spacing_and_num(diameter=diameter, offset=offset, spin=90, num=num, spacing=spacing)
        .mirror([0, 1, 0])
        .translate([0, width - diameter / 2, 0])
    )

    return (middle | line1 | line2).translate([0, -width / 2, 0]).shape


def _make_box_and_lid_with_inset_hinge(
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

        _make_box_and_lid_with_inset_hinge(size=[100, 50, 20])

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
    base_body = pybosl2.shapes3d.cuboid(
        [width, length, height / 2],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)
    latch = (
        MakeLidTab(
            length=tab_length,
            height=tab_height,
            lid_thickness=lid_thickness,
            prism_width=prism_width,
            wall_thickness=wall_thickness,
        )
        .color(material_colour)
        .mirror([0, 0, 1])
        .rotate([0, 0, 270])
        .translate([0, length / 2 + tab_length / 2, height / 2 - lid_thickness])
    )
    base_body = base_body | latch

    rim_outer = pybosl2.shapes3d.cuboid(
        [width - wall_thickness, length - wall_thickness, wall_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate([wall_thickness / 2, wall_thickness / 2, height / 2 - wall_thickness / 2])
    rim_inner = pybosl2.shapes3d.cuboid(
        [
            width - wall_thickness * 2 - print_in_place_offset * 2,
            length - wall_thickness * 2 - print_in_place_offset * 2,
            wall_thickness,
        ],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate(
        [
            wall_thickness + print_in_place_offset,
            wall_thickness + print_in_place_offset,
            height / 2 - wall_thickness / 2,
        ]
    )
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
    lid_body = pybosl2.shapes3d.cuboid(
        [width, length, height / 2],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)

    lid_rim_outer = pybosl2.shapes3d.cuboid(
        [width - wall_thickness, length - wall_thickness, wall_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[
            LEFT + FRONT,
            RIGHT + FRONT,
            LEFT + BACK,
            RIGHT + BACK,
            TOP + BACK,
            TOP + FRONT,
            TOP + LEFT,
            TOP + RIGHT,
        ],
    ).translate([wall_thickness / 2, wall_thickness / 2, height / 2])
    lid_rim_inner = pybosl2.shapes3d.cuboid(
        [
            width - wall_thickness * 2 - print_in_place_offset * 2,
            length - wall_thickness * 2 - print_in_place_offset * 2,
            wall_thickness * 4,
        ],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    ).translate(
        [wall_thickness + print_in_place_offset, wall_thickness + print_in_place_offset, height / 2 - wall_thickness]
    )
    lid_body = lid_body | (lid_rim_outer - lid_rim_inner).color(material_colour)

    catch_cutter = (
        # NATIVE-BOUNDARY (bosl2 gap): pybosl2 has no minkowski(); keep native + native handles
        # (.shape). FIX IN BOSL2: add a minkowski op so this can be pure pybosl2.
        minkowski(
            pybosl2.shapes3d.cuboid([tab_offset * 2, tab_offset * 2, tab_offset * 2]).color(material_colour).shape,
            MakeLidTab(
                length=tab_length,
                height=tab_height,
                lid_thickness=lid_thickness,
                prism_width=prism_width,
                wall_thickness=wall_thickness,
            ).shape,
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
        hole = (
            pybosl2.shapes3d.cuboid(
                [width - wall_thickness * 2, length - wall_thickness * 2, lid_thickness + 1],
                anchor=BOTTOM + FRONT + LEFT,
            )
            .translate([wall_thickness, wall_thickness, -1])
            .color(material_colour)
        )
        lid_body = lid_body - hole

        c3 = ResolveChild(kids[3], width - wall_thickness * 2, length - wall_thickness * 2, lid_inner_height)
        lid_body = lid_body | c3.translate([wall_thickness, wall_thickness, -0.01])

    lid_assembly = lid_body.translate([width + gap, 0, 0])

    combined = base_body | lid_assembly

    hinge_pocket = (
        pybosl2.shapes3d.cuboid(
            [
                hinge_width + print_in_place_offset * 2 + 0.02,
                hinge_length + print_in_place_offset * 2,
                hinge_diameter + 5 + hinge_offset + 1,
            ],
            anchor=BOTTOM + FRONT + LEFT,
        )
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
        _inset_hinge(length=hinge_length, width=hinge_width, offset=hinge_offset, diameter=hinge_diameter)
        .color(material_colour)
        .rotate([0, 0, 90])
        .translate([width + gap / 2, hinge_length / 2 + side_gap, height / 2 - hinge_diameter / 2 - hinge_offset])
    )

    return combined | hinge


@dataclass
class HingeBoxOptions(BoxTypeOptions):
    """Hinge-box-specific options; pass via ``BoxSpec(type_options=HingeBoxOptions(...))``."""

    hinge_diameter: float = 6
    hinge_offset: float = 0.3
    gap: float = 1
    side_gap: float = 3
    tab_length: float = 10
    tab_height: float = 6
    tab_offset: float = 0.2
    prism_width: float = 0.75


class HingeBox(BoxBaseType):
    """A print-in-place box whose lid is joined to the base by an inset side hinge, on
    the new box system.

    Because the base + lid + hinge print as ONE piece, :meth:`make_box` returns the
    whole assembly and there is no separate lid (:meth:`make_lid` raises). ``contents``
    entries are carved into the hinge box's four slots, in order (base interior, lid
    interior, on top of the base, on top of the lid); their ``InnerObject`` type is not
    used (the hinge geometry defines each slot), which is why this type declares
    ``body_carves_contents``. Hinge parameters come from
    ``BoxSpec(type_options=HingeBoxOptions(hinge_diameter=6, ...))``.

    Usage::

        from box_base import BoxSpec
        from hinge_box import HingeBox

        HingeBox(BoxSpec(size=[100, 50, 20], label="hinge")).make_box().show()
    """

    options_class = HingeBoxOptions
    has_lid = False
    body_hollows_itself = True
    body_carves_contents = True

    def _build_box_body(self, contents):
        children = [io.value for io in contents] or None   # raw solids into the hinge box's slots
        o = self.options
        return _make_box_and_lid_with_inset_hinge(
            size=[self.width, self.length, self.height],
            children=children,
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            lid_thickness=self.lid_thickness,
            material_colour=self.material_colour,
            hinge_diameter=o.hinge_diameter,
            hinge_offset=o.hinge_offset,
            gap=o.gap,
            side_gap=o.side_gap,
            tab_length=o.tab_length,
            tab_height=o.tab_height,
            tab_offset=o.tab_offset,
            prism_width=o.prism_width,
        )
