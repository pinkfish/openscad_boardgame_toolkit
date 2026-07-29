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

# LibFile: cap_box.py
#    Cap-style box and lid generators.
#
# FileSummary: Cap box pieces for the cap boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes3d
from pybosl2 import transforms
from pybosl2 import masking
from lids_base import (
    default_lid_catch_type,
    internal_build_lid,
    IsDenseShapeType,
    DenseShapeEdges,
    MakeLidLabel,
    LidMeshBasic,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl

from typing import Callable


# ---------------------------------------------------------------------------
# Helper functions (pure Python equivalents)
# ---------------------------------------------------------------------------


def CapBoxDefaultCapHeight(height: float) -> float:
    """Default cap height for a box of given *height*."""
    return min(10, height / 2)


def CapBoxDefaultFingerHoldHeight(height: float) -> float:
    """Default finger hold height for a box of given *height*."""
    return min(5, height / 4)


def CapBoxDefaultFingerHoldLen(width: float, length: float) -> float:
    """Default finger hold length for a box of given *width* and *length*."""
    return min(width, length) / 5


def CapBoxDefaultLidWallThickness(wall_thickness: float) -> float:
    """Default lid wall thickness derived from *wall_thickness*."""
    return wall_thickness / 2


def CapBoxDefaultLidFingerHoldRounding(cap_height: float) -> float:
    """Default rounding on the lid finger hold."""
    return min(3, cap_height / 2)


def _resolve_child(c: PyOpenSCAD, inner_width: float, inner_length: float, inner_height: float) -> PyOpenSCAD:
    """Resolve a child entry: a plain solid, or a callable(inner_width, inner_length, inner_height)."""
    return c(inner_width, inner_length, inner_height) if callable(c) else c


def _catch_bump(wall_thickness: float, radius: float, anchor_dir: list[int]) -> PyOpenSCAD:
    """A rounded catch nub: a sphere clipped to a small cube on one face."""
    box = wall_thickness * 6 / 4
    # Bosl2Solid on the left so its __and__ (not sphere()'s native __and__) handles the mixed operand.
    return shapes3d.cuboid([box, box, box], anchor=anchor_dir) & sphere(r=radius)


# ---------------------------------------------------------------------------
# Box and lid modules
# ---------------------------------------------------------------------------


def MakeBoxWithCapLid(
    size: list[float],
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_finger_hold_len: float | None = None,
    finger_hold_height: float = 5,
    material_colour: str | None = None,
    positive_colour: str | None = None,
    children: Callable[[InnerSize], list[InnerObject]] | None = None,
    lid_catch: CatchType | None = None,
    top_rounding: float | None = None,
    bottom_rounding: float | None = None,
    corner_rounding: float | None = None,
    spin: float = 0,
    anchor: list[int] | None = None,
    orient: list[float] | None = None,
) -> PyOpenSCAD:
    """Makes a box with a cap lid.

    *children* is a list of solids placed inside the box (subtracted from the
    body, i.e. carved out as compartments). Entries may also be a
    callable(inner_width, inner_length, inner_height) for content that needs
    to know the box's interior size.

    Usage::

        MakeBoxWithCapLid([100, 50, 20])
        MakeBoxWithCapLid([50, 50, 10], cap_height=2, finger_hold_height=1)

    Args:
        size:                   [width, length, height] outer size
        children:               list of solids (or callables) to carve inside the box
        cap_height:             cap height (default auto)
        lid_thickness:          lid thickness (default default_lid_thickness)
        wall_thickness:         wall thickness (default default_wall_thickness)
        floor_thickness:        floor thickness (default default_floor_thickness)
        size_spacing:           wiggle room (default m_piece_wiggle_room)
        lid_finger_hold_len:    finger hold length (default auto)
        finger_hold_height:     finger hold height (default 5)
        material_colour:        colour (default default_material_colour)
        positive_colour:        colour for positive-only pieces
        lid_catch:              catch style (default default_lid_catch_type)
        top_rounding:           top edge rounding
        bottom_rounding:        bottom edge rounding
        corner_rounding:        corner rounding
        spin/anchor/orient:     BOSL2 positioning
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour
    if lid_catch is None:
        lid_catch = default_lid_catch_type
    if anchor is None:
        anchor = BOTTOM + FRONT + LEFT
    if orient is None:
        orient = TOP

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert floor_thickness > 0, f"Need floor_thickness > 0, floor_thickness={floor_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    calc_lid_wall_thickness = CapBoxDefaultLidWallThickness(wall_thickness)
    calc_lid_finger_hold_len = (
        lid_finger_hold_len if lid_finger_hold_len is not None else CapBoxDefaultFingerHoldLen(width, length)
    )
    calc_floor_thickness = floor_thickness if floor_thickness is not None else wall_thickness
    calc_cap_height = cap_height if cap_height is not None else CapBoxDefaultCapHeight(height)
    calc_finger_hold_height = (
        finger_hold_height if finger_hold_height is not None else CapBoxDefaultFingerHoldHeight(height)
    )
    calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height)
    calc_bottom_rounding = bottom_rounding
    if calc_bottom_rounding is None:
        calc_bottom_rounding = wall_thickness / 2
    calc_top_rounding = top_rounding
    if calc_top_rounding is None:
        calc_top_rounding = wall_thickness / 4
    calc_corner_rounding = corner_rounding
    if calc_corner_rounding is None:
        calc_corner_rounding = wall_thickness

    assert calc_bottom_rounding >= 0
    assert calc_top_rounding >= 0
    assert calc_corner_rounding >= 0

    box_height = height - lid_thickness - size_spacing
    tmat = transforms.reorient(anchor=anchor, spin=spin, orient=orient, size=[width, length, box_height])

    body = shapes3d.cuboid(
        [width, length, box_height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=calc_corner_rounding,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    )
    body = body.face_profile(BOTTOM, r=calc_bottom_rounding)
    body = body.corner_profile(BOTTOM, r=calc_bottom_rounding)
    body = body.color(material_colour)

    # Cut out the lid recess at the top of the box.
    lid_cut_outer = (
        shapes3d.cuboid(
            [width + size_spacing * 2, length + size_spacing * 2, calc_cap_height], anchor=BOTTOM + FRONT + LEFT
        )
        .color(material_colour)
        .translate([-size_spacing, -size_spacing, 0])
    )
    lid_cut_inner = (
        shapes3d.cuboid(
            [
                width - calc_lid_wall_thickness * 2 - size_spacing * 1.5,
                length - calc_lid_wall_thickness * 2 - size_spacing * 1.5,
                calc_cap_height,
            ],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=calc_corner_rounding,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        .color(material_colour)
        .translate([calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0])
    )
    body = body - (lid_cut_outer - lid_cut_inner).translate([0, 0, height - calc_cap_height])

    # Round over the top edge.
    top_z = height - lid_thickness - size_spacing
    body = body - masking.rounding_edge_mask(r=calc_top_rounding, l=width).rotate([0, 90, 0]).translate(
        [width / 2, calc_lid_wall_thickness + size_spacing, top_z]
    )
    body = body - masking.rounding_edge_mask(r=calc_top_rounding, l=width).rotate([0, 90, 180]).translate(
        [width / 2, length - calc_lid_wall_thickness - size_spacing / 2, top_z]
    )
    body = body - masking.rounding_edge_mask(r=calc_top_rounding, l=length).rotate([90, 90, 0]).translate(
        [calc_lid_wall_thickness + size_spacing, length / 2, top_z]
    )
    body = body - masking.rounding_edge_mask(r=calc_top_rounding, l=length).rotate([270, 90, 0]).translate(
        [width - calc_lid_wall_thickness - size_spacing / 2, length / 2, top_z]
    )

    # Lid catches (cut into the box wall so the lid's matching catch nubs/wedges click in).
    catches = None

    def add_catch(piece: "PyOpenSCAD | shapes3d.Bosl2Solid") -> None:
        nonlocal catches
        catches = piece if catches is None else catches | piece

    if (
        (lid_catch == CatchType.SHORT and width < length)
        or (lid_catch == CatchType.LONG and width > length)
        or lid_catch == CatchType.ALL
    ):
        catch_width = width - wall_thickness * 2
        add_catch(
            shapes3d.wedge([catch_width * 2 / 4, wall_thickness, wall_thickness])
            .color(material_colour)
            .translate([(catch_width * 2 / 8) + wall_thickness, 0, 0])
        )
        add_catch(
            shapes3d.wedge([catch_width * 2 / 4, wall_thickness, wall_thickness])
            .rotate([0, 0, 180])
            .color(material_colour)
            .translate([(catch_width * 6 / 8) + wall_thickness, length, 0])
        )
    if (
        (lid_catch == CatchType.SHORT and length < width)
        or (lid_catch == CatchType.LONG and length < width)
        or lid_catch == CatchType.ALL
    ):
        catch_length = length - wall_thickness * 2
        add_catch(
            shapes3d.wedge([catch_length * 2 / 4, wall_thickness, wall_thickness])
            .rotate([0, 0, 90])
            .color(material_colour)
            .translate([width, catch_length * 2 / 8 + wall_thickness, 0])
        )
        add_catch(
            shapes3d.wedge([catch_length * 2 / 4, wall_thickness, wall_thickness])
            .rotate([0, 0, 270])
            .color(material_colour)
            .translate([0, catch_length * 6 / 8 + wall_thickness, 0])
        )
    if (lid_catch == CatchType.BUMPS_SHORT and width <= length) or (
        lid_catch == CatchType.BUMPS_LONG and width > length
    ):
        catch_offset = width - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            x = (catch_offset * frac) + wall_thickness
            bump_front = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, FRONT).color(
                material_colour
            )
            bump_back = (
                _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, BACK)
                .color(material_colour)
                .translate([0, length, 0])
            )
            add_catch((bump_front | bump_back).translate([x, 0, wall_thickness]))
    if (lid_catch == CatchType.BUMPS_SHORT and length < width) or (
        lid_catch == CatchType.BUMPS_LONG and length > width
    ):
        catch_offset = length - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            y = (catch_offset * frac) + wall_thickness
            bump_left = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, LEFT).color(material_colour)
            bump_right = (
                _catch_bump(wall_thickness, wall_thickness * 5 / 6 + m_piece_wiggle_room, RIGHT)
                .color(material_colour)
                .translate([width, 0, 0])
            )
            add_catch((bump_left | bump_right).translate([0, y, wall_thickness]))

    if catches is not None:
        body = body - catches.translate([0, 0, height - calc_cap_height])

    # Finger cutouts.
    finger_outer = (
        shapes3d.cuboid(
            [width + size_spacing * 2, length + size_spacing * 2, calc_finger_hold_height + 1],
            anchor=BOTTOM + FRONT + LEFT,
        )
        .color(material_colour)
        .translate([-size_spacing, -size_spacing, 0])
    )
    finger_inner = (
        shapes3d.cuboid(
            [
                width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                length - calc_lid_wall_thickness * 2 - size_spacing * 2,
                calc_finger_hold_height + 2,
            ],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=calc_corner_rounding,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        .color(material_colour)
        .translate([calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0])
    )
    finger_cut = finger_outer - finger_inner

    hole_a = (
        shapes3d.cuboid(
            [width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness + 1, calc_finger_hold_height + 0.2],
            rounding=calc_finger_hole_rounding,
            edges=[TOP + LEFT, TOP + RIGHT],
            anchor=BOTTOM + LEFT + FRONT,
            _fn=32,
        )
        .color(material_colour)
        .translate([calc_lid_finger_hold_len, 0, -0.2])
    )
    hole_b = (
        shapes3d.cuboid(
            [width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness + 1, calc_finger_hold_height + 0.2],
            rounding=calc_finger_hole_rounding,
            edges=[TOP + LEFT, TOP + RIGHT],
            anchor=BOTTOM + LEFT + FRONT,
            _fn=32,
        )
        .color(material_colour)
        .translate([calc_lid_finger_hold_len, length - calc_lid_wall_thickness - size_spacing, -0.2])
    )
    hole_c = (
        shapes3d.cuboid(
            [wall_thickness + 1, length - calc_lid_finger_hold_len * 2 + 0.1, calc_finger_hold_height + 0.2],
            rounding=calc_finger_hole_rounding,
            edges=[TOP + FRONT, TOP + BACK],
            anchor=BOTTOM + LEFT + FRONT,
            _fn=32,
        )
        .color(material_colour)
        .translate([0, calc_lid_finger_hold_len, -0.2])
    )
    hole_d = (
        shapes3d.cuboid(
            [wall_thickness + 1, length - calc_lid_finger_hold_len * 2 + 0.1, calc_finger_hold_height + 0.2],
            rounding=calc_finger_hole_rounding,
            edges=[TOP + FRONT, TOP + BACK],
            anchor=BOTTOM + LEFT + FRONT,
            _fn=32,
        )
        .color(material_colour)
        .translate([width - calc_lid_wall_thickness - size_spacing, calc_lid_finger_hold_len, -0.2])
    )

    finger_cut = finger_cut - hole_a - hole_b - hole_c - hole_d
    body = body - finger_cut.translate([0, 0, height - calc_cap_height - calc_finger_hold_height])

    # Put the children in the box (subtract everything except positive_only_children).
    inner_size = InnerSize(
        width=width - wall_thickness * 2,
        length=length - wall_thickness * 2,
        height=height - lid_thickness - floor_thickness,
    )

    all_children: list[InnerObject] = []
    if children != None:
        all_children = children(inner_size)

    positive_children = [
        i for i in all_children if (i.type == ObjectType.POSTIVE or i.type == ObjectType.POSTIVE_NEGATIVE)
    ]
    negative_children = [
        i.value for i in all_children if (i.type == ObjectType.NEGATIVE or i.type == ObjectType.POSTIVE_NEGATIVE)
    ]

    for i in negative_children:
        body = body - i.translate([wall_thickness, wall_thickness, calc_floor_thickness])

    result = body.translate([-width / 2, -length / 2, -box_height / 2]).multmatrix(tmat)

    # Positive-only / positive-negative children are rendered as separate
    # solid (non-carved) copies in the original, un-reoriented coordinate frame.
    for i in positive_children:
        piece = i.value.translate([wall_thickness, wall_thickness, floor_thickness])
        if i.color != None:
            piece = piece.color(i.color)
        result = result | piece
    return result


def CapBoxLid(
    size: list[float],
    children: "list | None" = None,
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Plain cap lid for a cap box.

    Usage::

        CapBoxLid([100, 50, 30])
        CapBoxLid([100, 50, 10], cap_height=3)

    Args:
        size:              [width, length, height] outer size
        children:          list of label/decoration solids placed on top of the lid
        cap_height:        cap height (default auto)
        lid_thickness:     lid thickness (default default_lid_thickness)
        wall_thickness:    wall thickness (default default_wall_thickness)
        size_spacing:      wiggle room (default m_piece_wiggle_room)
        lid_rounding:      lid edge rounding
        lid_inner_rounding: inner rounding
        material_colour:   colour (default default_material_colour)
        lid_catch:         catch style (default default_lid_catch_type)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be [width, length, height], got {size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    calc_lid_wall_thickness = wall_thickness / 2
    calc_cap_height = cap_height if cap_height is not None else CapBoxDefaultCapHeight(height)
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness / 2

    top_piece = shapes3d.cuboid(
        [width, length, lid_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=calc_lid_rounding,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )
    top_piece = top_piece.face_profile(TOP, r=wall_thickness / 2)
    top_piece = top_piece.color(material_colour)

    lid_children = [top_piece] + (list(children) if children else [])
    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=lid_children, size_spacing=size_spacing)
    lid_stack = lid_stack.translate([0, 0, calc_cap_height - lid_thickness])

    base_outer = shapes3d.cuboid(
        [width, length, calc_cap_height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=calc_lid_wall_thickness / 2,
        edges=[
            LEFT + FRONT,
            RIGHT + FRONT,
            LEFT + BACK,
            RIGHT + BACK,
            TOP + FRONT,
            TOP + BACK,
            TOP + LEFT,
            TOP + RIGHT,
        ],
    ).color(material_colour)
    base_inner = (
        shapes3d.cuboid(
            [width - calc_lid_wall_thickness * 2, length - calc_lid_wall_thickness * 2, calc_cap_height + 1],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=calc_lid_wall_thickness / 4,
            edges=[
                LEFT + FRONT,
                RIGHT + FRONT,
                LEFT + BACK,
                RIGHT + BACK,
                TOP + FRONT,
                TOP + BACK,
                TOP + LEFT,
                TOP + RIGHT,
            ],
        )
        .color(material_colour)
        .translate([calc_lid_wall_thickness, calc_lid_wall_thickness, -0.5])
    )
    base = base_outer - base_inner

    main = lid_stack | base

    # lid catches (protrude from the lid; positioned in the original,
    # un-rotated coordinate frame to match the box's recessed catches --
    # merged into `main` below, before the shared translate+rotate, so they
    # end up in the same final frame as the rest of the lid).
    catches = None

    def add_catch(piece: "PyOpenSCAD | shapes3d.Bosl2Solid") -> None:
        nonlocal catches
        catches = piece if catches is None else catches | piece

    if (
        (lid_catch == CatchType.SHORT and width < length)
        or (lid_catch == CatchType.LONG and width > length)
        or lid_catch == CatchType.ALL
    ):
        catch_width = width - wall_thickness * 2
        add_catch(
            shapes3d.wedge(
                [catch_width * 2 / 4 - size_spacing * 2, wall_thickness * 5 / 8, calc_lid_wall_thickness * 5 / 8]
            )
            .rotate([0, 180, 0])
            .color(material_colour)
            .translate([(catch_width * 6 / 8) + wall_thickness, 0, 0])
        )
        add_catch(
            shapes3d.wedge([catch_width * 2 / 4 - size_spacing * 2, wall_thickness * 5 / 8, wall_thickness * 5 / 8])
            .rotate([0, 0, 180])
            .rotate([0, 180, 0])
            .color(material_colour)
            .translate([(catch_width * 2 / 8) + wall_thickness, length, 0])
        )
    if (
        (lid_catch == CatchType.SHORT and length < width)
        or (lid_catch == CatchType.LONG and length < width)
        or lid_catch == CatchType.ALL
    ):
        catch_length = length - wall_thickness * 2
        # Unlike the width-direction wedges above (a plain Y-180 flip), these need a Z rotation
        # to run along the length-direction wall instead -- adding a *second* Y-180 on top (as
        # this used to) flips the wedge's depth axis back to point outward, away from the box,
        # instead of inward against the wall, and the boundry ends up outside the lid's own
        # footprint. A single Z rotation alone already gets the depth (flush-to-wall) and
        # along-wall axes right (verified via --summary bounding-box); only the rim-height axis
        # ends up on the wrong side of z=0 as a result, fixed by shifting it down by the wedge's
        # own height instead of another rotation (no single rotation flips just one axis).
        add_catch(
            shapes3d.wedge([catch_length * 2 / 4 - size_spacing * 2, wall_thickness * 5 / 8, wall_thickness * 5 / 8])
            .rotate([0, 0, 90])
            .color(material_colour)
            .translate([width, catch_length * 2 / 8 + wall_thickness + size_spacing, -wall_thickness * 5 / 8])
        )
        add_catch(
            shapes3d.wedge([catch_length * 2 / 4 - size_spacing * 2, wall_thickness * 5 / 8, wall_thickness * 5 / 8])
            .rotate([0, 0, 270])
            .color(material_colour)
            .translate([0, catch_length * 6 / 8 + wall_thickness + size_spacing, -wall_thickness * 5 / 8])
        )
    if (lid_catch == CatchType.BUMPS_SHORT and width <= length) or (
        lid_catch == CatchType.BUMPS_LONG and width > length
    ):
        catch_offset = width - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            x = (catch_offset * frac) + wall_thickness
            bump_front = _catch_bump(wall_thickness, wall_thickness * 9 / 12, FRONT).color(material_colour)
            bump_back = (
                _catch_bump(wall_thickness, wall_thickness * 9 / 12, BACK)
                .color(material_colour)
                .translate([0, length, 0])
            )
            add_catch((bump_front | bump_back).translate([x, 0, -wall_thickness]))
    if (lid_catch == CatchType.BUMPS_SHORT and length < width) or (
        lid_catch == CatchType.BUMPS_LONG and length > width
    ):
        catch_offset = length - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            y = (catch_offset * frac) + wall_thickness
            bump_left = _catch_bump(wall_thickness, wall_thickness * 9 / 12, LEFT).color(material_colour)
            bump_right = (
                _catch_bump(wall_thickness, wall_thickness * 9 / 12, RIGHT)
                .color(material_colour)
                .translate([width, 0, 0])
            )
            add_catch((bump_left | bump_right).translate([0, y, -wall_thickness]))

    if catches is not None:
        main = main | catches.translate([0, 0, calc_cap_height])

    return main.translate([0, length, calc_cap_height]).rotate([180, 0, 0])


def CapBoxLidWithCustomShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Cap lid with a custom repeating pattern.

    Usage::

        CapBoxLidWithCustomShape([100, 50, 30],
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size:               [width, length, height] outer size
        shape_child:        2-D shape solid to tile on the lid
        extra_children:     additional label/decoration children (list)
        lid_boundary:       boundary around the lid edge (default 10)
        wall_thickness:     wall thickness (default default_wall_thickness)
        cap_height:         cap height (default auto)
        layout_width:       pattern repeat width (default default_lid_layout_width)
        size_spacing:       wiggle room (default m_piece_wiggle_room)
        lid_thickness:      lid thickness (default default_lid_thickness)
        aspect_ratio:       dy scale factor (default 1.0)
        lid_rounding:       lid edge rounding
        lid_inner_rounding: inner rounding
        lid_pattern_dense:  use dense layout (default False)
        lid_dense_shape_edges: dense edge count (default 6)
        material_colour:    colour (default default_material_colour)
        pattern_inner_control: inner control mode (default False)
        lid_catch:          catch style (default default_lid_catch_type)
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

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    assert size[0] > 0 and size[1] > 0 and size[2] > 0, f"Need width,length,height > 0 size={size}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=size,
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

    return CapBoxLid(
        size=size,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=m_piece_wiggle_room,
        lid_rounding=lid_rounding,
        lid_inner_rounding=lid_inner_rounding,
        material_colour=material_colour,
        lid_catch=lid_catch,
        children=lid_children,
    )


def CapBoxLidWithLabelAndCustomShape(
    size: list[float],
    text_str: str,
    label_options: LabelOptions | None = None,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_boundary: float = 10,
    cap_height: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    label_background_colour: str | None = None,
    pattern_inner_control: int = False,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Cap lid with both a label and a custom repeating shape.

    Usage::

        CapBoxLidWithLabelAndCustomShape([100, 50, 30], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size:               [width, length, height] outer size
        text_str:           label text
        label_options:      :class:`~labels.LabelOptions`
        shape_child:        2-D shape to tile on the lid
        extra_children:     additional children (list)
        wall_thickness:     wall thickness (default default_wall_thickness)
        lid_boundary:       lid border (default 10)
        cap_height:         cap height (default auto)
        layout_width:       pattern repeat width
        size_spacing:       wiggle room (default m_piece_wiggle_room)
        lid_thickness:      lid thickness (default default_lid_thickness)
        aspect_ratio:       dy scale factor (default 1.0)
        lid_rounding/lid_inner_rounding: rounding values
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour:    colour (default default_material_colour)
        label_background_colour: label background colour (unused -- bake it
                                  into label_options instead, kept for API compatibility)
        pattern_inner_control: inner control mode
        lid_catch:          catch style (default default_lid_catch_type)
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

    calc_label_options = (
        label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    )

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert text_str is not None, "text_str must not be None"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_shape_raw = MakeLidLabel(
        size=[width - lid_boundary * 2, length - lid_boundary * 2],
        options=label_opts,
        lid_thickness=lid_thickness,
        text_str=text_str,
    )
    # A lid too narrow for the label yields None (labels.py warns "ignoring label"); match the
    # .scad behaviour and just build the lid without a label rather than failing.
    base_extra = list(extra_children) if extra_children else []
    if label_shape_raw is not None:
        all_extra = [label_shape_raw.translate([lid_boundary, lid_boundary, 0])] + base_extra
    else:
        all_extra = base_extra

    return CapBoxLidWithCustomShape(
        size=size,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=m_piece_wiggle_room,
        lid_rounding=lid_rounding,
        lid_inner_rounding=lid_inner_rounding,
        lid_catch=lid_catch,
        aspect_ratio=aspect_ratio,
        lid_dense_shape_edges=lid_dense_shape_edges,
        material_colour=material_colour,
        lid_pattern_dense=lid_pattern_dense,
        pattern_inner_control=pattern_inner_control,
        shape_child=pattern_shape,
        extra_children=all_extra,
    )


def CapBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    aspect_ratio: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Cap lid with an automatic label and shape pattern.

    Usage::

        CapBoxLidWithLabel([100, 50, 30], text_str="Frog")
        CapBoxLidWithLabel([100, 50, 30], text_str="Frog",
                           material_colour="lightblue",
                           label_options=MakeLabelOptions(label_colour="black"))

    Args:
        size:            [width, length, height] outer size
        text_str:        label text
        extra_children:  additional children (list of solids)
        lid_boundary:    lid border in mm (default 10)
        wall_thickness:  wall thickness (default default_wall_thickness)
        aspect_ratio:    dy scale factor (default default_lid_aspect_ratio)
        cap_height:      cap height (default auto)
        layout_width:    pattern repeat width (default default_lid_layout_width)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_thickness:   lid thickness (default default_lid_thickness)
        lid_rounding:    lid edge rounding
        lid_inner_rounding: inner rounding
        material_colour: colour (default default_material_colour)
        lid_catch:       catch style (default default_lid_catch_type)
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
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    calc_label_options = (
        label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert text_str is not None, "text_str must not be None"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return CapBoxLidWithLabelAndCustomShape(
        size=size,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        text_str=text_str,
        label_options=calc_label_options,
        shape_child=shape_piece,
        extra_children=extra_children,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        lid_catch=lid_catch,
    )


def CapBoxLidWithShape(
    size: list[float],
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    cap_height: float | None = None,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float = 1.0,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    shape_options: ShapeObject | None = None,
    label_options: LabelOptions | None = None,
    extra_children: "list | None" = None,
) -> PyOpenSCAD:
    """Cap lid with a repeating shape pattern but no label.

    Usage::

        CapBoxLidWithShape([100, 50, 30])
        CapBoxLidWithShape([100, 50, 30], material_colour="lightblue")

    Args:
        size:            [width, length, height] outer size
        lid_boundary:    lid border in mm (default 10)
        wall_thickness:  wall thickness (default default_wall_thickness)
        cap_height:      cap height (default auto)
        layout_width:    pattern repeat width (default default_lid_layout_width)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_thickness:   lid thickness (default default_lid_thickness)
        aspect_ratio:    dy scale factor (default 1.0)
        lid_rounding/lid_inner_rounding: rounding values
        material_colour: colour (default default_material_colour)
        lid_catch:       catch style (default default_lid_catch_type)
        shape_options:   :class:`~shape_type.ShapeObject`
        label_options:   unused, kept for API compatibility
        extra_children:  additional children (list of solids)
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

    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert size_spacing > 0, f"Need size_spacing > 0, size_spacing={size_spacing}"
    assert cap_height is None or cap_height > 0, f"Need cap height None or > 0 {cap_height}"

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return CapBoxLidWithCustomShape(
        size=size,
        cap_height=cap_height,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        lid_catch=lid_catch,
        shape_child=shape_piece,
        extra_children=extra_children,
    )
