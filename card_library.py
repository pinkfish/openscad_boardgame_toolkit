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

# LibFile: card_library.py
#    A special card library box for card heavy games.
#
# FileSummary: A special card library box for card heavy games.
# FileGroup: CardLibrary

from __future__ import annotations
import copy
import math
import types

from pythonscad import *
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.masking
import pybosl2.shapes3d
import pybosl2.shapes2d
from pybosl2._sdf import joiners as _sdf_joiners
from lids_base import internal_build_lid, MakeLidLabel, LidMeshBasic, IsDenseShapeType, DenseShapeEdges
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from box_base import BoxBaseType, BoxSpec
from dataclasses import dataclass, field

from typing import Callable


def MakeCardSize(
    width: float, length: float, single_card_thickness: float, sleeve_wall_thickness: float | None = None
) -> types.SimpleNamespace:
    """Creates a card size object.

    Usage::

        MakeCardSize(93, 62, 0.1)

    Args:
        width: width of the cards
        length: length of the cards
        single_card_thickness: thickness of a single card
        sleeve_wall_thickness: thickness of the sleeve (default default_wall_thickness*0.75)
    """
    if sleeve_wall_thickness is None:
        sleeve_wall_thickness = default_wall_thickness * 0.75
    return types.SimpleNamespace(
        length=length,
        width=width,
        single_card_thickness=single_card_thickness,
        sleeve_wall_thickness=sleeve_wall_thickness,
    )


def sumVec(vec: list[float]) -> float:
    """Sums all the values in a vector."""
    return sum(vec)


def TotalCards(num_cards: int | list[int]) -> int:
    """Calculates the total number of cards, whether a single number or an array."""
    return sum(num_cards) if isinstance(num_cards, (list, tuple)) else num_cards


def sumCardsTo(cards: list[int], end_index: int) -> int:
    """Sums the first end_index cards in an array."""
    return sum(cards[:end_index])


def InternalBarriers(num_cards: int | list[int]) -> int:
    """Calculates the number of internal barriers needed for an array of cards."""
    return len(num_cards) - 1 if isinstance(num_cards, (list, tuple)) and len(num_cards) > 0 else 0


def SleeveSizeWidth(
    num_cards: int | list[int], card_size: types.SimpleNamespace, wall_thickness: float | None = None
) -> float:
    """Calculates the width of a card sleeve."""
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    return card_size.single_card_thickness * TotalCards(num_cards) + card_size.sleeve_wall_thickness * (
        2 + InternalBarriers(num_cards)
    )


def SleeveSize(
    num_cards: int | list[int], card_size: types.SimpleNamespace, wall_thickness: float | None = None
) -> list[float]:
    """Calculates the [length, width, height] size of a card sleeve."""
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    return [
        card_size.length + card_size.sleeve_wall_thickness * 2,
        SleeveSizeWidth(num_cards, card_size, wall_thickness),
        card_size.width + wall_thickness,
    ]


def CardLibrarySize(
    array: list,
    card_size: types.SimpleNamespace,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    floor_thickness: float | None = None,
    extra_width: float = 0.5,
) -> list[float]:
    """Calculates the size of a card library box.

    Usage::

        CardLibrarySize([["Card 1", 10], ["Card 2", 20]], card_size)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    return [
        card_size.length + wall_thickness * 4,
        sum(SleeveSizeWidth(x[1], card_size, wall_thickness) for x in array) + wall_thickness * 2 + extra_width,
        card_size.width + wall_thickness * 2 + lid_thickness + floor_thickness,
    ]


CARD_LIBRARY_LATCH_SLIDING = "sliding"
CARD_LIBRARY_LATCH_CLIP = "clip"
CARD_LIBRARY_LATCH_NONE = "none"


def MakeCardLibraryBox(
    size: list[float],
    children: "list | None" = None,
    floor_thickness: float | None = None,
    wall_thickness: float | None = None,
    lip_size: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str = "magenta",
    latch: str = CARD_LIBRARY_LATCH_SLIDING,
    hinge_hole_diameter: float | None = None,
    print_in_place_offset: float | None = None,
) -> PyOpenSCAD:
    """Makes a card library box with the specified latch type.

    Usage::

        MakeCardLibraryBox([100, 50, 20])

    Args:
        size:    [width, length, height]
        children: list of solids/callables to carve inside the box
        floor_thickness: thickness of the floor (default default_floor_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lip_size: size of the lip (default default_floor_thickness*3)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        material_colour: colour (default "magenta")
        latch:   CARD_LIBRARY_LATCH_* (default CARD_LIBRARY_LATCH_SLIDING)
        hinge_hole_diameter: diameter of the hinge hole (default default_hinge_hole_diameter)
        print_in_place_offset: wiggle room (default default_print_in_place_offset)
    """
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lip_size is None:
        lip_size = default_floor_thickness * 3
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if hinge_hole_diameter is None:
        hinge_hole_diameter = default_hinge_hole_diameter
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset

    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert floor_thickness > 0, f"Need floor thickness > 0, floor_thickness={floor_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert lip_size > 0, f"Need lip size > 0, lip_size={lip_size}"
    assert hinge_hole_diameter > 0, f"Need hinge hole diameter > 0, hinge_hole_diameter={hinge_hole_diameter}"

    height_without_hinge = height - lid_thickness
    hinge_seg = max(math.floor(length / 20), 5)

    main = (
        pybosl2.shapes3d.cuboid(
            [width, length, height_without_hinge],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        .edge_profile(
            [TOP + FRONT, TOP + BACK, TOP + RIGHT], children=pybosl2.masking.mask2d_roundover(wall_thickness / 4)
        )
        # (bottom face_profile + corner_profile dropped: corner_profile is broken in
        # pybosl2 0.6.5 and the cuboid's rounding= already rounds the vertical edges.)
        .color(material_colour)
    )

    inside_cut = (
        pybosl2.shapes3d.cuboid(
            [width, length - wall_thickness * 2, height_without_hinge],
            rounding=wall_thickness / 4,
            anchor=BOTTOM + LEFT + FRONT,
        )
        .color(material_colour)
        .translate([wall_thickness, wall_thickness, floor_thickness])
    )
    main = main - inside_cut

    if latch == CARD_LIBRARY_LATCH_SLIDING:
        main = main - pybosl2.shapes3d.cuboid(
            [wall_thickness * 4.5, wall_thickness + 0.02, wall_thickness], anchor=TOP + FRONT + LEFT
        ).translate(
            [
                width * 3 / 4 - wall_thickness + wall_thickness / 4,
                -0.01,
                height_without_hinge + lid_thickness - wall_thickness,
            ]
        )
        main = main - pybosl2.shapes3d.cuboid(
            [wall_thickness * 4.5, wall_thickness + 0.02, wall_thickness], anchor=TOP + BACK + LEFT
        ).translate(
            [
                width * 3 / 4 - wall_thickness + wall_thickness / 4,
                length + 0.01,
                height_without_hinge + lid_thickness - wall_thickness,
            ]
        )

    hinge_space_cut = pybosl2.shapes3d.cuboid(
        [wall_thickness * 2 + 0.02, length - wall_thickness * 2, wall_thickness + 0.01],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=-wall_thickness,
        edges=[TOP + RIGHT],
    ).translate([-0.01, wall_thickness, height_without_hinge - default_wall_thickness])
    main = main - hinge_space_cut

    filament_hole = pybosl2.shapes3d.ycyl(diameter=hinge_hole_diameter, height=length + 5, anchor=FRONT).translate(
        [wall_thickness, 1, height - wall_thickness]
    )
    main = main - filament_hole

    hinge_support = (
        pybosl2.shapes3d.cuboid(
            [wall_thickness * 2, length - wall_thickness * 2 + 0.02, height_without_hinge / 6],
            anchor=TOP + FRONT + LEFT,
            chamfer=wall_thickness,
            edges=[BOTTOM + RIGHT],
        )
        .color(material_colour)
        .translate([0, wall_thickness - 0.01, height_without_hinge - wall_thickness])
    )
    back_support = (
        pybosl2.shapes3d.cuboid(
            [wall_thickness * 2, length - wall_thickness * 2 + 0.02, wall_thickness * 3],
            anchor=BOTTOM + FRONT + LEFT,
            chamfer=wall_thickness,
            edges=[TOP + RIGHT],
        )
        .color(material_colour)
        .translate([0, wall_thickness - 0.01, default_floor_thickness - 0.01])
    )

    body = main | hinge_support | back_support

    if latch == CARD_LIBRARY_LATCH_CLIP:
        clip_a = pybosl2.shapes3d.cuboid(
            [wall_thickness * 3, wall_thickness, lid_thickness * 2],
            rounding=wall_thickness / 4,
            anchor=TOP + FRONT + LEFT,
            edges=[LEFT + FRONT, RIGHT + FRONT, TOP + FRONT],
        )
        clip_a_cut = pybosl2.shapes3d.cuboid(
            [wall_thickness * 2, wall_thickness / 2, wall_thickness / 2],
            chamfer=wall_thickness / 2,
            anchor=TOP + FRONT + LEFT,
            edges=[BOTTOM + FRONT],
        ).translate([wall_thickness / 2, wall_thickness / 2 + 0.01, -wall_thickness / 2])
        body = body | (clip_a - clip_a_cut).color(material_colour).translate(
            [width * 3 / 4, 0, height_without_hinge + lid_thickness]
        )

        clip_b = pybosl2.shapes3d.cuboid(
            [wall_thickness * 3, wall_thickness, lid_thickness * 2],
            rounding=wall_thickness / 4,
            anchor=TOP + BACK + LEFT,
            edges=[RIGHT + BACK, LEFT + BACK, TOP + BACK],
        )
        clip_b_cut = pybosl2.shapes3d.cuboid(
            [wall_thickness * 2, wall_thickness / 2, wall_thickness / 2],
            chamfer=wall_thickness / 2,
            anchor=TOP + BACK + LEFT,
            edges=[BOTTOM + BACK],
        ).translate([wall_thickness / 2, -wall_thickness / 2 - 0.01, -wall_thickness / 2])
        body = body | (clip_b - clip_b_cut).color(material_colour).translate(
            [width * 3 / 4, length, height_without_hinge + lid_thickness]
        )

    if latch == CARD_LIBRARY_LATCH_SLIDING:
        latch_a = pybosl2.shapes3d.cuboid(
            [wall_thickness * 5, wall_thickness, lid_thickness * 2],
            rounding=wall_thickness / 4,
            anchor=TOP + FRONT + LEFT,
            edges=[LEFT + FRONT, RIGHT + FRONT, TOP + FRONT],
        )
        latch_a_cut = pybosl2.shapes3d.prismoid(
            size1=[wall_thickness + print_in_place_offset * 2, wall_thickness + print_in_place_offset],
            size2=[wall_thickness * 3 + print_in_place_offset * 3, wall_thickness + print_in_place_offset],
            height=wall_thickness + 0.02,
            shift=[0, 0],
            anchor=TOP + FRONT,
        ).translate([wall_thickness * 2.5, -0.01, -wall_thickness])
        body = body | (latch_a - latch_a_cut).color(material_colour).translate(
            [width * 3 / 4 - wall_thickness - print_in_place_offset, 0, height_without_hinge + lid_thickness]
        )

        latch_b = pybosl2.shapes3d.cuboid(
            [wall_thickness * 5, wall_thickness, lid_thickness * 2],
            rounding=wall_thickness / 4,
            anchor=TOP + BACK + LEFT,
            edges=[RIGHT + BACK, LEFT + BACK, TOP + BACK],
        )
        latch_b_cut = pybosl2.shapes3d.prismoid(
            size1=[wall_thickness + print_in_place_offset * 2, wall_thickness + print_in_place_offset],
            size2=[wall_thickness * 3 + print_in_place_offset * 3, wall_thickness + print_in_place_offset],
            height=wall_thickness + 0.02,
            shift=[0, 0],
            anchor=TOP + BACK,
        ).translate([wall_thickness * 2.5, 0.01, -wall_thickness])
        body = body | (latch_b - latch_b_cut).color(material_colour).translate(
            [width * 3 / 4 - wall_thickness - print_in_place_offset, length, height_without_hinge + lid_thickness]
        )

    front_lip = pybosl2.shapes3d.cuboid(
        [wall_thickness, length - wall_thickness * 2 + 0.02, lip_size],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness / 2,
        edges=[TOP + RIGHT],
    ).color(material_colour)
    front_lip_chamfer = (
        pybosl2.shapes3d.cuboid(
            [wall_thickness, length - wall_thickness * 2 + 0.02, wall_thickness],
            anchor=BOTTOM + FRONT + LEFT,
            chamfer=wall_thickness / 3,
            edges=[BOTTOM + LEFT, TOP + LEFT, TOP + RIGHT],
        )
        .color(material_colour)
        .translate([-wall_thickness / 2, 0, lip_size - wall_thickness])
    )
    body = body | (front_lip | front_lip_chamfer).translate(
        [width - wall_thickness, wall_thickness + 0.01, floor_thickness - 0.01]
    )

    back_hinge = (
        _sdf_joiners.knuckle_hinge(
            length=length - wall_thickness * 2 - print_in_place_offset * 2,
            segs=hinge_seg,
            offset=wall_thickness + lid_thickness,
            knuckle_diam=wall_thickness + lid_thickness,
            arm_height=0,
            arm_angle=90,
            clear_top=False,
            inner=True,
            spin=90,
            pin_diam=hinge_hole_diameter,
            orient=list(TOP),
            anchor=BOTTOM + BACK + LEFT,
        )
        .to_csg()
        .color(material_colour)
        .translate([0, wall_thickness + print_in_place_offset, height_without_hinge - wall_thickness - lid_thickness])
    )
    body = body | back_hinge

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - floor_thickness
    if children:
        kids_shape = None
        for c in children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            kids_shape = piece if kids_shape is None else kids_shape | piece
        if kids_shape is not None:
            body = body - kids_shape.translate([wall_thickness, wall_thickness, floor_thickness])

    return body


def SlidingChannel(size: list[float], wall_thickness: float) -> "PyOpenSCAD":
    """Creates a sliding channel for the card library latch.

    Args:
        size: [width, length, height]
        wall_thickness: thickness of the walls
    """
    width, length, height = size

    ab_size = [height * 2, length, height + 0.1]
    ab_anchor = BOTTOM + FRONT + LEFT

    a = pybosl2.shapes3d.cuboid(ab_size, anchor=ab_anchor, chamfer=height, edges=[BOTTOM + RIGHT])
    a = a.edge_profile([TOP + LEFT], children=pybosl2.masking.mask2d_roundover(height / 2)).translate([-height, 0, -0.1])

    b = pybosl2.shapes3d.cuboid(ab_size, anchor=ab_anchor, chamfer=height, edges=[BOTTOM + LEFT])
    b = b.edge_profile([TOP + RIGHT], children=pybosl2.masking.mask2d_roundover(height / 2)).translate(
        [width - height, 0, -0.1]
    )

    return (a | b).shape


def SlidingLatch(
    size: list[float], print_in_place_offset: float, lid_thickness: float, wall_thickness: float
) -> "PyOpenSCAD":
    """Creates a sliding latch for the card library box lid.

    Args:
        size: [width, length, height]
        print_in_place_offset: wiggle room for moving parts
        lid_thickness: thickness of the lid
        wall_thickness: thickness of the walls
    """
    width, length, height = size

    a = pybosl2.shapes3d.prismoid(
        size1=[width - print_in_place_offset * 2, length - wall_thickness * 1.3 + print_in_place_offset],
        size2=[width - wall_thickness * 2, length - wall_thickness * 1.3 + print_in_place_offset],
        height=wall_thickness - print_in_place_offset * 1.5,
        anchor=BOTTOM + FRONT + LEFT,
    ).translate([0, 0, lid_thickness + print_in_place_offset * 1.5])

    b = pybosl2.shapes3d.cuboid(
        [width - print_in_place_offset * 2, wall_thickness, lid_thickness + print_in_place_offset * 2],
        anchor=BOTTOM + BACK + LEFT,
    ).translate([print_in_place_offset * 0.25, length - wall_thickness * 1.75 - print_in_place_offset, 0])

    c = pybosl2.shapes3d.cuboid(
        [width - print_in_place_offset * 2, wall_thickness * 2.5 - print_in_place_offset * 3, lid_thickness],
        anchor=BOTTOM + BACK + LEFT,
    ).translate([print_in_place_offset * 0.25, length - wall_thickness * 2.75 - print_in_place_offset * 2, 0])

    return (a | b | c).shape


def CardLibraryBoxLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    lip_size: float | None = None,
    lid_boundary: float = 10,
    latch: str = CARD_LIBRARY_LATCH_SLIDING,
    material_colour: str = "magenta",
    hinge_hole_diameter: float | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
) -> PyOpenSCAD:
    """Creates a basic lid for the card library box.

    Usage::

        CardLibraryBoxLid([100, 50, 20])

    Args:
        size: [width, length, height]
        children: list of up to 5 solids placed in/on the lid
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        lip_size: size of the lip (default default_lid_thickness*3)
        lid_boundary: unused, kept for API compatibility
        latch:   CARD_LIBRARY_LATCH_* (default CARD_LIBRARY_LATCH_SLIDING)
        material_colour: colour (default "magenta")
        hinge_hole_diameter: diameter of the hinge hole (default default_hinge_hole_diameter)
        print_in_place_offset: wiggle room (default default_print_in_place_offset)
        size_spacing: wiggle room between pieces (default m_piece_wiggle_room)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if lip_size is None:
        lip_size = default_lid_thickness * 3
    if hinge_hole_diameter is None:
        hinge_hole_diameter = default_hinge_hole_diameter
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room

    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert lid_thickness > 0, f"Need lid thickness > 0, lid_thickness={lid_thickness}"
    assert lip_size > 0, f"Need lip size > 0, lip_size={lip_size}"
    assert hinge_hole_diameter > 0, f"Need hinge hole diameter > 0, hinge_hole_diameter={hinge_hole_diameter}"

    edge_size = max(length / 6, 25)
    sliding_latch_size = [wall_thickness * 3, edge_size, wall_thickness]
    hinge_seg = max(math.floor(length / 20), 5)

    base_plate = (
        pybosl2.shapes3d.cuboid(
            [width - wall_thickness * 2, length, lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness / 2,
            edges=[BOTTOM],
        )
        .color(material_colour)
        .translate([wall_thickness * 2, 0, 0])
    )

    back_hinge = (
        _sdf_joiners.knuckle_hinge(
            length=length - wall_thickness * 2 - print_in_place_offset * 2,
            segs=hinge_seg,
            offset=wall_thickness + lid_thickness,
            knuckle_diam=wall_thickness + lid_thickness,
            pin_diam=hinge_hole_diameter,
            arm_height=0,
            arm_angle=90,
            clear_top=False,
            spin=90,
            orient=list(LEFT),
            anchor=TOP + BACK + LEFT,
        )
        .to_csg()
        .color(material_colour)
        .translate([0, wall_thickness + print_in_place_offset, 0])
    )

    back_holder = (
        pybosl2.shapes3d.cuboid(
            [
                wall_thickness * 2,
                length - wall_thickness * 2 - print_in_place_offset * 2,
                wall_thickness + lid_thickness,
            ],
            anchor=BOTTOM + FRONT + LEFT,
        )
        .color(material_colour)
        .translate([wall_thickness * 1.5, wall_thickness + print_in_place_offset, 0])
    )

    front_lip = (
        pybosl2.shapes3d.cuboid(
            [wall_thickness, length - wall_thickness * 2 - 1, lid_thickness + lip_size],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness / 2,
            edges=[TOP + LEFT, TOP + RIGHT],
        )
        .color(material_colour)
        .translate([width - wall_thickness, wall_thickness + 0.5, 0])
    )

    base = base_plate | back_hinge | back_holder | front_lip

    if latch == CARD_LIBRARY_LATCH_SLIDING:
        base = base - pybosl2.shapes3d.cuboid(
            [wall_thickness * 5 + print_in_place_offset * 2, wall_thickness + 0.02, lid_thickness * 2],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([width * 3 / 4 - print_in_place_offset - wall_thickness, -0.01, -0.01])
        base = base - pybosl2.shapes3d.cuboid(
            [wall_thickness * 3 + print_in_place_offset * 2, wall_thickness + 0.02, lid_thickness * 2],
            anchor=BOTTOM + BACK + LEFT,
        ).translate([width * 3 / 4 - print_in_place_offset, length + 0.01, -0.01])

    kids = list(children) if children else []
    extra = kids[0:2]

    if latch == CARD_LIBRARY_LATCH_SLIDING:
        slide_support_a = (
            cube([wall_thickness * 5 + print_in_place_offset * 2, edge_size, lid_thickness])
            .color(material_colour)
            .translate([width * 3 / 4 - print_in_place_offset - wall_thickness, wall_thickness, 0])
        )
        slide_support_b = (
            cube([wall_thickness * 5 + print_in_place_offset * 2, edge_size, lid_thickness])
            .color(material_colour)
            .translate([width * 3 / 4 - print_in_place_offset - wall_thickness, length - edge_size - wall_thickness, 0])
        )
        slide_supports = slide_support_a | slide_support_b
        # Plain unrounded boxes as native cubes (translated to match the old TOP+BACK+LEFT /
        # TOP+FRONT+LEFT anchors): slide_supports gets masked several times inside
        # internal_build_lid(), and PythonSCAD segfaults when frep()-meshed nodes appear in
        # a tree that is referenced from more than one CSG branch.
        _hc_size = [wall_thickness * 3, wall_thickness * 3.5 + 0.02, lid_thickness + 1]
        handle_cut_a = (
            cube(_hc_size)
            .translate([0, -_hc_size[1], -_hc_size[2]])
            .translate(
                [
                    width * 3 / 4 - print_in_place_offset * 0.5,
                    sliding_latch_size[1] - wall_thickness * 0.75,
                    lid_thickness + 0.01,
                ]
            )
        )
        handle_cut_b = (
            cube(_hc_size)
            .translate([0, 0, -_hc_size[2]])
            .translate(
                [
                    width * 3 / 4 - print_in_place_offset * 0.5,
                    length - sliding_latch_size[1] + wall_thickness * 0.75,
                    lid_thickness + 0.01,
                ]
            )
        )
        slide_supports = slide_supports - handle_cut_a - handle_cut_b
        extra = extra + [slide_supports]

    extra = extra + kids[2:5]

    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=[base] + extra, size_spacing=size_spacing)
    body = lid_stack

    if latch == CARD_LIBRARY_LATCH_SLIDING:
        body = body | SlidingChannel(
            [sliding_latch_size[0] + print_in_place_offset * 2, sliding_latch_size[1], sliding_latch_size[2]],
            wall_thickness=wall_thickness,
        ).color(material_colour).translate([width * 3 / 4 - print_in_place_offset * 2, wall_thickness, lid_thickness])

        body = body | pybosl2.shapes3d.cuboid(
            [wall_thickness * 3 + 0.5, wall_thickness, wall_thickness + 0.1], anchor=BOTTOM + FRONT + LEFT
        ).color(material_colour).translate([width * 3 / 4 - print_in_place_offset, edge_size, lid_thickness - 0.1])

        body = body | SlidingLatch(
            size=sliding_latch_size,
            print_in_place_offset=print_in_place_offset,
            lid_thickness=lid_thickness,
            wall_thickness=wall_thickness,
        ).color(material_colour).translate([width * 3 / 4, wall_thickness, 0])

        body = body | SlidingChannel(
            [sliding_latch_size[0] + print_in_place_offset * 2, sliding_latch_size[1], sliding_latch_size[2]],
            wall_thickness=wall_thickness,
        ).color(material_colour).translate(
            [width * 3 / 4 - print_in_place_offset, length - edge_size - wall_thickness, lid_thickness]
        )

        body = body | pybosl2.shapes3d.cuboid(
            [wall_thickness * 3 + print_in_place_offset * 2, wall_thickness, wall_thickness + 0.1],
            anchor=BOTTOM + FRONT + LEFT,
        ).color(material_colour).translate(
            [width * 3 / 4 - print_in_place_offset, length - edge_size - wall_thickness, lid_thickness - 0.1]
        )

        body = body | SlidingLatch(
            size=sliding_latch_size,
            print_in_place_offset=print_in_place_offset,
            lid_thickness=lid_thickness,
            wall_thickness=wall_thickness,
        ).rotate([0, 0, 180]).color(material_colour).translate(
            [width * 3 / 4 + wall_thickness * 3 - print_in_place_offset, length - wall_thickness, 0]
        )

    return body


def CardLibraryBoxLidWithCustomShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    lip_size: float | None = None,
    latch: str = CARD_LIBRARY_LATCH_SLIDING,
    material_colour: str = "magenta",
    hinge_hole_diameter: float | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    aspect_ratio: float | None = 1.0,
    pattern_inner_control: int = False,
    lid_boundary: float = 10,
    layout_width: float | None = None,
) -> PyOpenSCAD:
    """Creates a lid for the card library box configured for custom shapes.

    Args:
        size: [width, length, height]
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        (other args, see :func:`CardLibraryBoxLid` and :func:`~lids_base.LidMeshBasic`)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=[size[0] - wall_thickness, size[1] - wall_thickness],
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

    return CardLibraryBoxLid(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        lip_size=lip_size,
        latch=latch,
        material_colour=material_colour,
        hinge_hole_diameter=hinge_hole_diameter,
        print_in_place_offset=print_in_place_offset,
        lid_boundary=lid_boundary,
        size_spacing=size_spacing,
        children=lid_children,
    )


def CardLibraryBoxLidWithShape(
    size: list[float],
    extra_children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    lip_size: float | None = None,
    latch: str = CARD_LIBRARY_LATCH_SLIDING,
    material_colour: str = "magenta",
    hinge_hole_diameter: float | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    pattern_inner_control: int = False,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Creates a lid for the card library box using standard shapes.

    Args:
        size: [width, length, height]
        extra_children: additional children (list of solids)
        shape_options: :class:`~shape_type.ShapeObject`
        (other args, see :func:`CardLibraryBoxLidWithCustomShape`)
    """
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return CardLibraryBoxLidWithCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        lip_size=lip_size,
        latch=latch,
        hinge_hole_diameter=hinge_hole_diameter,
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        lid_boundary=lid_boundary,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        shape_child=shape_piece,
        extra_children=extra_children,
    )


def CardLibraryBoxLidWithLabel(
    size: list[float],
    label: str,
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    label_options: LabelOptions | None = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    lip_size: float | None = None,
    latch: str = CARD_LIBRARY_LATCH_SLIDING,
    material_colour: str = "magenta",
    hinge_hole_diameter: float | None = None,
    print_in_place_offset: float | None = None,
    size_spacing: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Creates a lid for a card library box with a shape pattern and a label.

    Usage::

        CardLibraryBoxLidWithLabel([100, 50, 20], "Cards")

    Args:
        size:  [width, length, height]
        label: the string to use for the label
        shape_child: optional explicit 2-D pattern shape (overrides shape_options if given)
        extra_children: additional children (list of solids)
        label_options: :class:`~labels.LabelOptions`
        shape_options: :class:`~shape_type.ShapeObject`
        (other args, see :func:`CardLibraryBoxLidWithCustomShape`)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = "magenta"
    calc_label_options = (
        label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
    width, length = size[0], size[1]

    if shape_child is not None:
        pattern_shape = shape_child
    else:
        piece = ShapeByType(options=calc_shape_options)
        assert piece is not None, "shape_options must not be ShapeType.NONE here"
        pattern_shape = piece.color(material_colour)

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    half_w = (width - lid_boundary * 2) / 2
    half_l = (length - lid_boundary * 2) / 2
    label_shape_raw = MakeLidLabel(
        size=[width - lid_boundary * 2, length - lid_boundary * 2],
        options=label_opts,
        lid_thickness=lid_thickness,
        text_str=label,
    )
    assert label_shape_raw is not None, "label did not generate"
    label_shape = (
        label_shape_raw.translate([-half_w, -half_l, 0])
        .rotate([0, 180, 0])
        .translate([half_w, half_l, lid_thickness])
        .translate([lid_boundary, lid_boundary, 0])
    )

    lid_children = [label_shape] + (list(extra_children) if extra_children else [])

    return CardLibraryBoxLidWithCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        lip_size=lip_size,
        latch=latch,
        hinge_hole_diameter=hinge_hole_diameter,
        print_in_place_offset=print_in_place_offset,
        size_spacing=size_spacing,
        lid_boundary=lid_boundary,
        aspect_ratio=aspect_ratio,
        layout_width=layout_width,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        shape_child=pattern_shape,
        extra_children=lid_children,
    )


def CardSleeveForLibrary(
    num_cards: int,
    card_size: types.SimpleNamespace,
    children: "PyOpenSCAD | list[PyOpenSCAD | Callable[..., PyOpenSCAD]] | Callable[..., PyOpenSCAD] | None" = None,
    wall_thickness: float | None = None,
    lip_size: float | None = None,
    material_colour: str = "magenta",
    font: str | None = None,
    label_colour: str | None = None,
    label: str = "",
    add_positive: bool = False,
    emboss_text: float = 0.2,
    text_length_offset: float | None = None,
    min_text_height: float = 3,
    print_in_place_offset: float | None = None,
) -> PyOpenSCAD:
    """Creates a card sleeve configured for the library.

    *children*, if given, may be a plain solid or a list of solids, or a
    callable(inner_width, inner_length) -- inner_width corresponds to the
    sleeve height, inner_length to the sleeve length (matching the original
    SCAD module's $inner_width/$inner_length special variables).

    Usage::

        CardSleeveForLibrary(num_cards=60, card_size=MakeCardSize(90, 72, 0.1))

    Args:
        num_cards: number of cards, or a list of per-compartment counts
        card_size: a :func:`MakeCardSize` object
        children: solid(s) to carve as a finger-hole (see above)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        lip_size: size of the catch lip (default default_floor_thickness*3)
        material_colour: colour (default "magenta")
        font: font to use for the label (default default_label_font)
        label_colour: colour of the label (default default_label_colour)
        label: the string to use for the label
        add_positive: also render a free-standing positive copy of children + text (default False)
        emboss_text: amount of text embossing (default 0.2)
        text_length_offset: text offset along the length (default default_wall_thickness*3)
        min_text_height: minimum text height to bother rendering (default 3)
        print_in_place_offset: wiggle room (default default_print_in_place_offset)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lip_size is None:
        lip_size = default_floor_thickness * 3
    if font is None:
        font = default_label_font
    if label_colour is None:
        label_colour = default_label_colour
    if text_length_offset is None:
        text_length_offset = default_wall_thickness * 3
    if print_in_place_offset is None:
        print_in_place_offset = default_print_in_place_offset

    assert TotalCards(num_cards) > 0, f"num cards must be > 0 {num_cards}"

    size = SleeveSize(num_cards, card_size, wall_thickness)
    width, length, height = size

    calc_font = font if font is not None else default_label_font
    # textmetrics() returns a dict, not an object -- metrics["size"], same as the working
    # labels.py call sites (and font must be a real string).
    text_length = height - text_length_offset - wall_thickness
    text_width = length - wall_thickness
    metrics = textmetrics(label, font=calc_font) if label else None
    if metrics and metrics["size"][0] > 0:
        text_aspect = metrics["size"][1] / metrics["size"][0]
        text_use_length = text_width / text_aspect > text_length
        text_new_width = text_length * text_aspect if text_use_length else text_width
        text_new_length = text_length if text_use_length else text_width / text_aspect
    else:
        # No label -> no text on the sleeve (has_text below becomes False).
        text_new_width = 0.0
        text_new_length = 0.0

    body = pybosl2.shapes3d.cuboid(size, anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness / 4).color(material_colour)

    cards_array = list(num_cards) if isinstance(num_cards, (list, tuple)) else [num_cards]
    num_compartments = len(cards_array) if isinstance(num_cards, (list, tuple)) else 1
    for i in range(num_compartments):
        comp_y_size = cards_array[i] * card_size.single_card_thickness
        comp_y_offset = (
            card_size.sleeve_wall_thickness
            + sumCardsTo(cards_array, i) * card_size.single_card_thickness
            + i * card_size.sleeve_wall_thickness
        )
        body = body - pybosl2.shapes3d.cuboid(
            [width - wall_thickness - card_size.sleeve_wall_thickness, comp_y_size, height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=min(
                wall_thickness / 4, comp_y_size / 2, (width - wall_thickness - card_size.sleeve_wall_thickness) / 2
            ),
        ).color(material_colour).translate([wall_thickness, comp_y_offset, wall_thickness])

        body = body - pybosl2.shapes3d.cuboid(
            [width, comp_y_size, height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=min(wall_thickness / 4, width / 2, comp_y_size / 2),
        ).color(material_colour).translate([wall_thickness, comp_y_offset, wall_thickness * 3])

    rounding = -min(wall_thickness, length / 2, width / 2)
    # The old offset_sweep(round_corners(rect), top/bottom os_circle(-r)) -- a rounded-rect
    # column with flared ends. The rounded rect is a native offset() of a shrunk sharp rect;
    # OffsetSweep() adds the flared rims.
    rr = wall_thickness * 2
    rect_profile = pybosl2.shapes2d.square([width - rr * 2, height - rr * 2], center=True).offset(radius=rr)
    side_round = (
        OffsetSweep(rect_profile, height=length + 0.02, rounding_top=rounding, rounding_bottom=rounding)
        .color(material_colour)
        .rotate([90, 0, 0])
        .translate([width / 2 + wall_thickness * 5, length + 0.01, height / 2 + wall_thickness * 5])
    )
    body = body - side_round

    radius = wall_thickness * math.sqrt(3) / 2
    catch_cut = (
        pybosl2.shapes3d.cuboid(
            [wall_thickness, length + 0.02, wall_thickness + print_in_place_offset],
            anchor=FRONT,
            chamfer=wall_thickness / 3,
            edges=[FRONT + TOP, FRONT + BOTTOM],
        )
        .color(material_colour)
        .rotate([0, 45, 0])
        .translate([-radius / 2, -0.01, lip_size + print_in_place_offset / 2 - wall_thickness / 2])
    )
    body = body - catch_cut

    has_text = text_new_width > min_text_height
    text_piece = None
    if has_text:
        text_piece = (
            text(label, font=calc_font, valign="center", halign="center")
            .resize([text_new_length, text_new_width, 0])
            .linear_extrude(0.3 + emboss_text)
            .color(label_colour)
            .rotate([180, 90, 0])
            .translate([0.3 if emboss_text else 0.5, length / 2, text_length / 2 + text_length_offset])
        )
        body = body - text_piece

    inner_width = height
    inner_length = length
    kids_shape = None
    if children:
        # duck-typed children: plain solids or callable(inner_width, inner_length) factories
        kids: list[Any] = list(children) if isinstance(children, (list, tuple)) else [children]
        for c in kids:
            # pyright narrows a callable() Any to `(...) -> object`; keep the duck typing
            piece: Any = c(inner_width, inner_length) if callable(c) else c
            kids_shape = piece if kids_shape is None else kids_shape | piece
    if kids_shape is not None:
        body = body - kids_shape.rotate([180, 270, 0]).translate([0, length, 0])

    result = body

    if kids_shape is not None and add_positive:
        result = result | kids_shape.rotate([180, 270, 0]).translate([0, length, 0])

    if has_text and (add_positive or emboss_text > 0):
        result = result | text_piece

    return result.translate([width, length, 0]).rotate([0, 0, 180])


def MakeAllSleeves(
    card_array: list,
    children: "Callable | None" = None,
    spacing: float = 2,
    card_size: types.SimpleNamespace | None = None,
    wall_thickness: float | None = None,
) -> PyOpenSCAD:
    """Makes all the sleeves for a card array.

    *children*, if given, is a callable(index, card_entry) -> solid|None,
    where card_entry is the [name, count, svg_filename] entry for that
    sleeve -- used as a finger-hole cutout, replacing the original SCAD
    module's $inner_2d special variable.

    Usage::

        core_player_cards = [
            ["Agnes Baker", 34, "per_investigator"],
            ["Level 0", 15, "s_level_0"],
        ]
        MakeAllSleeves(core_player_cards, spacing=2, card_size=MakeCardSize(63.5, 88, 0.3))

    Args:
        card_array: array of [name, count, svg_filename] entries
        children: callable(index, card_entry) -> solid|None (see above)
        spacing: spacing between sleeves (default 2)
        card_size: a :func:`MakeCardSize` object
        wall_thickness: thickness of the walls (default default_wall_thickness)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    assert card_size is not None, "MakeAllSleeves(): card_size must be given"

    sleeve_sizes = [SleeveSize(x[1], card_size, wall_thickness=wall_thickness) for x in card_array]

    shape = None
    for i in range(len(card_array)):
        y_offset = sum(sleeve_sizes[x][1] + spacing for x in range(i))
        child = children(i, card_array[i]) if callable(children) else None
        sleeve = CardSleeveForLibrary(
            num_cards=card_array[i][1],
            card_size=card_size,
            label=card_array[i][0],
            add_positive=True,
            text_length_offset=18,
            emboss_text=0.3,
            children=child,
        ).translate([0, y_offset, 0])
        shape = sleeve if shape is None else shape | sleeve
    assert shape is not None, "MakeAllSleeves(): card_array is empty"
    return shape


# ---------------------------------------------------------------------------
# Dataclass input model + CardLibraryBox on the new box system
# ---------------------------------------------------------------------------


@dataclass
class CardSize:
    """The cards this library holds. ``single_card_thickness`` is a sleeved card's
    thickness; ``sleeve_wall_thickness`` defaults to ``default_wall_thickness * 0.75``."""

    width: float
    length: float
    single_card_thickness: float
    sleeve_wall_thickness: float | None = None


@dataclass
class CardGroup:
    """One group of cards -- a named stack that gets its own sleeve."""

    name: str
    count: int


@dataclass
class CardLibrarySpec:
    """Declarative input for a :class:`CardLibraryBox`. The box SIZE is computed from
    the cards, so you describe the cards, not the dimensions."""

    card_size: CardSize
    groups: list[CardGroup]
    label: str = "CardLibrary"
    wall_thickness: float | None = None
    lid_thickness: float | None = None
    floor_thickness: float | None = None
    material_colour: str = "magenta"
    latch: str = CARD_LIBRARY_LATCH_SLIDING


def _card_ns(cs: CardSize) -> types.SimpleNamespace:
    return MakeCardSize(cs.width, cs.length, cs.single_card_thickness, cs.sleeve_wall_thickness)


class CardLibraryBox(BoxBaseType):
    """A card-library box on the new box system: a box + lid sized to hold a set of
    card groups, each group in its own sleeve.

    Takes a :class:`CardLibrarySpec` (a dataclass); the box dimensions are computed
    from the cards. Beyond :meth:`make_box` / :meth:`make_lid`, it adds
    :meth:`make_sleeves` (all sleeves) and :meth:`make_sleeve` (one group's sleeve).

    Usage::

        from card_library import CardLibraryBox, CardLibrarySpec, CardSize, CardGroup

        box = CardLibraryBox(CardLibrarySpec(
            card_size=CardSize(width=63, length=88, single_card_thickness=0.5),
            groups=[CardGroup("Reds", 20), CardGroup("Blues", 30)],
        ))
        box.make_box().show()
        box.make_lid().show()
        box.make_sleeves().show()      # all sleeves; or box.make_sleeve(0)
    """

    def __init__(self, spec: CardLibrarySpec) -> None:
        assert isinstance(spec, CardLibrarySpec), (
            f"CardLibraryBox expects a CardLibrarySpec, got {type(spec).__name__}"
        )
        self._card = spec
        cs = _card_ns(spec.card_size)
        array = [[g.name, g.count] for g in spec.groups]
        wt = spec.wall_thickness if spec.wall_thickness is not None else default_wall_thickness
        lt = spec.lid_thickness if spec.lid_thickness is not None else default_lid_thickness
        ft = spec.floor_thickness if spec.floor_thickness is not None else default_floor_thickness
        size = CardLibrarySize(array, cs, wall_thickness=wt, lid_thickness=lt, floor_thickness=ft)
        super().__init__(BoxSpec(
            size=[float(x) for x in size], label=spec.label,
            wall_thickness=wt, lid_thickness=lt, floor_thickness=ft, material_colour=spec.material_colour,
        ))

    def _box_size(self) -> list[float]:
        return [self.width, self.length, self.height]

    def make_box(self, *, contents=None, finger_holes=None):
        if contents is None:
            contents = self._spec.contents
        children = [io.value for io in self._resolve_contents(contents)] or None
        return MakeCardLibraryBox(
            size=self._box_size(), children=children, wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness, lid_thickness=self.lid_thickness,
            material_colour=self.material_colour, latch=self._card.latch,
        )

    def make_lid(self, lid=None):
        return CardLibraryBoxLid(
            size=self._box_size(), wall_thickness=self.wall_thickness, lid_thickness=self.lid_thickness,
            latch=self._card.latch, material_colour=self.material_colour,
        )

    def make_sleeves(self):
        """All the card sleeves (one per group), laid out for printing."""
        array = [[g.name, g.count] for g in self._card.groups]
        return MakeAllSleeves(array, card_size=_card_ns(self._card.card_size), wall_thickness=self.wall_thickness)

    def make_sleeve(self, index: int):
        """The sleeve for group *index* (labelled with the group's name)."""
        g = self._card.groups[index]
        return CardSleeveForLibrary(
            g.count, _card_ns(self._card.card_size), label=g.name,
            wall_thickness=self.wall_thickness, material_colour=self.material_colour,
        )

    def _build_box_body(self):
        raise NotImplementedError("CardLibraryBox builds its body in make_box()")
