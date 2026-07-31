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
import math
import types
from dataclasses import dataclass

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.masking
import pybosl2.shapes3d
from pybosl2._sdf import joiners as _sdf_joiners
from pybosl2._sdf import shapes3d as _sdf_shapes3d
from box_base import BoxBaseType, BoxSpec, BoxTypeOptions, LidPlate


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


@dataclass
class FilamentHingeBoxOptions(BoxTypeOptions):
    """Filament-hinge options; pass via ``BoxSpec(type_options=FilamentHingeBoxOptions(...))``.

    Attributes:
        thickness:     thickness of the hinge (default default_hinge_thickness)
        hole_diameter: diameter of the hinge hole (default default_hinge_hole_diameter)
        num_segments:  number of hinge segments (default auto, from the box length)
        pin_slop:      extra diameter slop for the hinge pin (default default_hinge_pin_slop)
    """

    thickness: float | None = None
    hole_diameter: float | None = None
    num_segments: int | None = None
    pin_slop: float | None = None

    def __post_init__(self) -> None:
        if self.thickness is None:
            self.thickness = default_hinge_thickness
        if self.hole_diameter is None:
            self.hole_diameter = default_hinge_hole_diameter
        if self.pin_slop is None:
            self.pin_slop = default_hinge_pin_slop


def HingeOptions(**kwargs) -> FilamentHingeBoxOptions:
    """The hinge options the module's internal geometry functions default to."""
    return FilamentHingeBoxOptions(**kwargs)


def _make_box_with_filament_hinge_lid(
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

        _make_box_with_filament_hinge_lid(size=[100, 50, 20])

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
        calc_hinge_options.num_segments
        if calc_hinge_options.num_segments is not None
        else max(math.floor(length / 20), 5)
    )
    lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness)
    lip_length = max(length / 4, 15)

    main = pybosl2.shapes3d.cuboid(
        [width, length, height - lid_thickness - print_in_place_offset],
        rounding=wall_thickness / 2,
        anchor=BOTTOM + FRONT + LEFT,
        edges=[BOTTOM, FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT],
    )
    main = main.edge_mask(
        [TOP + FRONT, TOP + BACK], children=pybosl2.masking.rounding_edge_mask(length=width, radius=wall_thickness / 4)
    )
    main = main.edge_mask([TOP + RIGHT], children=pybosl2.masking.rounding_edge_mask(length=length, radius=wall_thickness / 4))
    main = main.color(material_colour)

    ramp = (
        pybosl2.shapes3d.cuboid(
            [
                calc_hinge_options.thickness * 1.25 + print_in_place_offset,
                length,
                wall_thickness + print_in_place_offset,
            ],
            anchor=BOTTOM + LEFT + FRONT,
            rounding=-wall_thickness,
            edges=TOP + RIGHT,
        )
        .color(material_colour)
        .translate([0, 0, height - lid_thickness - wall_thickness - print_in_place_offset * 2])
    )
    main = main - ramp

    hinge_cut = pybosl2.shapes3d.cuboid(
        [calc_hinge_options.thickness + print_in_place_offset * 4, length, lid_thickness + wall_thickness],
        anchor=TOP + FRONT,
        rounding=calc_hinge_options.thickness / 2,
        edges=[BOTTOM + RIGHT],
    ).translate([calc_hinge_options.thickness / 2 + print_in_place_offset * 2, 0, height - lid_thickness])
    main = main - hinge_cut

    catch_box = pybosl2.shapes3d.cuboid(
        [wall_thickness / 2, lip_length + print_in_place_offset * 2, lip_height],
        anchor=BOTTOM + RIGHT,
        rounding=wall_thickness / 4,
        edges=[BOTTOM + LEFT],
    )
    catch_sphere_a = pybosl2.shapes3d.sphere(diameter=wall_thickness, anchor=RIGHT).translate(
        [0, lip_length / 4, lip_height / 2]
    )
    catch_sphere_b = pybosl2.shapes3d.sphere(diameter=wall_thickness, anchor=RIGHT).translate(
        [0, -lip_length / 4, lip_height / 2]
    )
    catch = (
        (catch_box | catch_sphere_a | catch_sphere_b)
        .color(material_colour)
        .translate([width, length / 2, height - lid_thickness - lip_height - print_in_place_offset])
        .shape
    )
    main = main - catch

    knuckle = (
        _sdf_joiners.knuckle_hinge(
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
        .to_csg()               # SDF knuckle -> CSG so it composes with the CSG box
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


def _filament_box_inside_mask(
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

        _filament_box_inside_mask([100, 20, 10])

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

    body = pybosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - floor_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=rounding,
        edges=[BOTTOM, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )

    cut1 = pybosl2.shapes3d.cuboid(
        [support_width + print_in_place_offset + 0.5, length + 1, support_height + 1],
        anchor=BOTTOM + FRONT + LEFT,
        chamfer=support_width,
        edges=[BOTTOM + RIGHT],
    ).translate([-0.5, -0.5, height - lid_thickness - support_height - floor_thickness])
    body = body - cut1

    cut2 = pybosl2.shapes3d.ycyl(
        diameter=calc_hinge_options.thickness + print_in_place_offset, length=length + 1, anchor=FRONT + LEFT + TOP
    ).translate([0, 0.5, height])
    body = body - cut2

    # Unwrapped: the native intersection at the call sites needs a raw solid.
    return body.shape


def _filament_lid_parts(
    size: list[float],
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
    """The pieces of a filament-hinge lid: ``(top_plate, shell, plate_origin, pin_hole)``.

    Split into pieces (rather than returning a finished lid) so the ONE lid pipeline in
    :class:`~box_base.BoxBaseType` can decorate the top plate -- see
    :class:`FilamentHingeBox`.

    Usage::

        _filament_lid_parts([100, 20, 6])

    Args:
        size:           [width, length, height] of the box
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
        calc_hinge_options.num_segments
        if calc_hinge_options.num_segments is not None
        else max(math.floor(length / 20), 5)
    )
    lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness)
    lip_length = max(length / 4, 15)

    top = (
        pybosl2.shapes3d.cuboid(
            [width - wall_thickness * 2.5, length, lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=lid_thickness / 2,
            edges=BOTTOM,
        )
        .color(material_colour)
        .translate([wall_thickness * 2.5, 0, 0])
    )

    knuckle = _sdf_joiners.knuckle_hinge(
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
    edge_round = _sdf_shapes3d.rounding_edge_mask(length=width, radius=wall_thickness / 2)
    knuckle = knuckle - edge_round.translate([0, 0, kd / 2])
    knuckle = knuckle - edge_round.rotate([0, 0, 90]).translate([kd * 1.5, 0, kd / 2])
    knuckle = knuckle.to_csg().color(material_colour)   # SDF -> CSG for the CSG lid

    catch_box = pybosl2.shapes3d.cuboid(
        [wall_thickness / 2, lip_length, lip_height + print_in_place_offset],
        anchor=BOTTOM + RIGHT,
        rounding=wall_thickness / 4,
        edges=[TOP + LEFT],
    )
    catch_sphere_a = pybosl2.shapes3d.sphere(diameter=wall_thickness * 5 / 6, anchor=RIGHT).translate(
        [0, lip_length / 4, lip_height / 2]
    )
    catch_sphere_b = pybosl2.shapes3d.sphere(diameter=wall_thickness * 5 / 6, anchor=RIGHT).translate(
        [0, -lip_length / 4, lip_height / 2]
    )
    catch = (
        (catch_box | catch_sphere_a | catch_sphere_b)
        .color(material_colour)
        .translate([width, length / 2, lid_thickness - print_in_place_offset])
        .shape
    )

    hole = (
        pybosl2.shapes3d.ycyl(height=length + 1, diameter=calc_hinge_options.hole_diameter + print_in_place_offset, anchor=FRONT)
        .color(material_colour)
        .translate([wall_thickness, 0.5, wall_thickness])
        .shape
    )
    return top, knuckle | catch, [wall_thickness * 2.5, 0.0], hole


class FilamentHingeBox(BoxBaseType):
    """A box whose lid is joined by a filament hinge (knuckles on the box and lid, a
    piece of filament threaded through them), on the new box system.

    Box and lid are SEPARATE prints (joined by filament after printing), so
    :meth:`make_box` and :meth:`make_lid` both work. ``contents`` entries are carved
    into the box interior in order (the underlying geometry places them itself, hence
    ``body_carves_contents``). Hinge parameters come from
    ``BoxSpec(type_options=FilamentHingeBoxOptions(thickness=..., hole_diameter=...))``.

    Usage::

        from box_base import BoxSpec
        from filament_hinge_box import FilamentHingeBox

        box = FilamentHingeBox(BoxSpec(size=[100, 50, 20], label="fil"))
        box.make_box().show()
        box.make_lid().show()
    """

    options_class = FilamentHingeBoxOptions
    body_hollows_itself = True
    body_carves_contents = True

    def _build_box_body(self, contents):
        # Thread the InnerObject types into the underlying function's index lists so the
        # full content model works here: POSITIVE -> add only, POSITIVE_NEGATIVE -> carve
        # AND (under MAKE_MMU) re-emit coloured (the Irish-Gauge engraved-label pattern).
        children = [io.value for io in contents] or None
        pos_only = [i for i, io in enumerate(contents) if io.type == ObjectType.POSITIVE]
        pos_neg = [i for i, io in enumerate(contents) if io.type == ObjectType.POSITIVE_NEGATIVE]
        return _make_box_with_filament_hinge_lid(
            size=[self.width, self.length, self.height],
            children=children,
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            lid_thickness=self.lid_thickness,
            material_colour=self.material_colour,
            hinge_options=self.options,
            positive_only_children=pos_only,
            positive_negative_children=pos_neg,
        )

    def _lid_plate(self, lid) -> LidPlate:
        """The lid's flat top (the decorated plate) plus the hinge knuckles and the catch
        lip (the shell); the filament pin hole is a cutout through the finished lid."""
        top, shell, origin, pin_hole = _filament_lid_parts(
            size=[self.width, self.length, self.height],
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            lid_thickness=lid.lid_thickness,
            material_colour=self.material_colour,
            hinge_options=self.options,
        )
        return LidPlate(
            plate=top,
            size=[self.width - origin[0], self.length],
            thickness=lid.lid_thickness,
            origin=origin,
            shell=shell,
            cutouts=[pin_hole],
        )
