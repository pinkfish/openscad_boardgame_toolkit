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

# LibFile: slipover_box.py
#    Slipover box pieces for the slipover boxes.
#
# FileSummary: Slipover box pieces for the slipover boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.masking
import pybosl2.shapes3d
from components import CornerCatch
from lids_base import (
    default_lid_catch_type,
    internal_build_lid,
    MakeLidLabel,
    LidMeshBasic,
    IsDenseShapeType,
    DenseShapeEdges,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


def _catch_bump(wall_thickness: float, radius: float, anchor_dir: list[int]) -> "PyOpenSCAD":
    box = wall_thickness * 6 / 4
    return (pybosl2.shapes3d.cuboid([box, box, box], anchor=anchor_dir) & pybosl2.shapes3d.sphere(r=radius)).shape


def MakeBoxWithSlipoverLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    foot: float = 0,
    size_spacing: float | None = None,
    wall_height: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: str | None = None,
    positive_colour: str | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Makes the inside of a slip box.

    This will take a second lid that slides over the outside of the box.
    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakeBoxWithSlipoverLid([100, 50, 10])

    Args:
        size:    [width, length, height] outside size of the box
        children: list of solids/callables to carve inside the box
        wall_thickness: thickness of the walls (default default_wall_thickness)
        foot:    how big the foot around the bottom should be (default 0)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        wall_height: explicit wall height (default height - lid_thickness - size_spacing)
        floor_thickness: floor thickness (default default_floor_thickness)
        lid_thickness: lid thickness (default default_lid_thickness)
        material_colour: colour (default default_material_colour)
        positive_colour: colour of positive pieces (default default_positive_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        lid_catch: catch style (default default_lid_catch_type)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if positive_colour is None:
        positive_colour = default_positive_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )

    wall_height_calc = wall_height if wall_height is not None else height - lid_thickness - size_spacing

    # Direct pybosl2/Manifold CSG throughout -- the same construction as the .scad original.
    inner = pybosl2.shapes3d.cuboid(
        [
            width - wall_thickness * 2 - size_spacing * 2,
            length - wall_thickness * 2 - size_spacing * 2,
            wall_height_calc,
        ],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )
    inner = inner.edge_mask(
        [TOP], children=pybosl2.masking.rounding_edge_mask(r=wall_thickness / 4, l=max(length, width))
    )
    body = inner.translate([wall_thickness + size_spacing, wall_thickness + size_spacing, 0])

    if foot > 0:
        foot_piece = pybosl2.shapes3d.cuboid(
            [width, length, foot],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=min(wall_thickness / 2, foot / 2),
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        body = body | foot_piece

    if (
        (lid_catch == CatchType.SHORT and width < length)
        or (lid_catch == CatchType.LONG and width > length)
        or lid_catch == CatchType.ALL
    ):
        catch_width = width - wall_thickness * 2
        body = body - pybosl2.shapes3d.wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]).translate(
            [(catch_width * 2 / 8) + wall_thickness, wall_thickness, foot]
        )
        body = body - pybosl2.shapes3d.wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]).rotate(
            [0, 0, 180]
        ).translate([(catch_width * 6 / 8) + wall_thickness, length - wall_thickness, foot])
    if (
        (lid_catch == CatchType.SHORT and length < width)
        or (lid_catch == CatchType.LONG and length < width)
        or lid_catch == CatchType.ALL
    ):
        catch_length = length - wall_thickness * 2
        body = body - pybosl2.shapes3d.wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]).rotate(
            [0, 0, 90]
        ).translate([width - wall_thickness, catch_length * 2 / 8 + wall_thickness, foot])
        body = body - pybosl2.shapes3d.wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]).rotate(
            [0, 0, 270]
        ).translate([wall_thickness, catch_length * 6 / 8 + wall_thickness, foot])
    if (lid_catch == CatchType.BUMPS_SHORT and width < length) or (
        lid_catch == CatchType.BUMPS_LONG and width > length
    ):
        catch_offset = width - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            x = (catch_offset * frac) + wall_thickness
            bump_a = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, FRONT)
            bump_b = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, BACK).translate(
                [0, length - wall_thickness * 2, 0]
            )
            body = body - (bump_a | bump_b).translate([x, wall_thickness, wall_thickness + foot])
    if (lid_catch == CatchType.BUMPS_SHORT and length <= width) or (
        lid_catch == CatchType.BUMPS_LONG and length > width
    ):
        catch_offset = length - wall_thickness * 2
        y1 = (catch_offset * 6 / 8) + wall_thickness
        bump_a1 = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, LEFT)
        bump_b1 = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + m_piece_wiggle_room, RIGHT).translate(
            [width - wall_thickness * 2, 0, 0]
        )
        body = body - (bump_a1 | bump_b1).translate([wall_thickness, y1, wall_thickness + foot])

        y2 = (catch_offset * 2 / 8) + wall_thickness
        bump_a2 = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, LEFT)
        bump_b2 = _catch_bump(wall_thickness, wall_thickness * 5 / 6 + size_spacing, RIGHT).translate(
            [width - wall_thickness * 2, 0, 0]
        )
        body = body - (bump_a2 | bump_b2).translate([wall_thickness, y2, wall_thickness + foot])

    body = body.color(material_colour)

    inner_width = width - wall_thickness * 4
    inner_length = length - wall_thickness * 4
    inner_height = wall_height_calc - default_floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            body = body - piece.translate([wall_thickness * 2, wall_thickness * 2, floor_thickness])

    result = body.shape
    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            piece = (
                ResolveChild(kids[i], inner_width, inner_length, inner_height)
                .color(positive_colour)
                .translate([wall_thickness * 2, wall_thickness * 2, floor_thickness])
            )
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result


def SlipoverBoxLid(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    foot: float = 0,
    finger_hole_length: bool = False,
    finger_hole_width: bool = True,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Make a box with a slip lid, a lid that slips over the outside of a box.

    Usage::

        SlipoverBoxLid([100, 50, 10])

    Args:
        size: [width, length, height] outside size of the lid
        children: list of label/decoration solids placed on top of the lid
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        foot:    size of the foot on the box
        finger_hole_length/finger_hole_width: unused, kept for API compatibility
        lid_rounding: rounding on the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
        lid_catch: catch style (default default_lid_catch_type)
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

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )

    foot_offset = foot + size_spacing if foot > 0 else 0
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness / 2

    top = (
        pybosl2.shapes3d.cuboid(
            [width - wall_thickness * 10 / 6, length - wall_thickness * 10 / 6, lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
        )
        .color(material_colour)
        .translate([wall_thickness * 5 / 6, wall_thickness * 5 / 6, 0])
    )

    kids = list(children) if children else []
    lid_stack = internal_build_lid(lid_thickness=lid_thickness, children=[top] + kids, size_spacing=size_spacing)
    lid_stack = lid_stack.translate([0, 0, height - foot_offset - lid_thickness])

    finger_height = min(20, (height - foot_offset - lid_thickness) / 2)

    shell = pybosl2.shapes3d.cuboid(
        [width, length, height - foot_offset],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=calc_lid_rounding,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP],
    )
    shell = shell.edge_mask(
        [BOT], children=pybosl2.masking.rounding_edge_mask(r=max(calc_lid_rounding / 4, 0.5), l=max(width, length))
    )

    cut1 = pybosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, lid_thickness + 1], anchor=BOTTOM + FRONT + LEFT
    ).translate([wall_thickness, wall_thickness, height - foot_offset - lid_thickness - 0.01])
    shell = shell - cut1

    cut2 = pybosl2.shapes3d.cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - foot_offset + 1],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=calc_lid_rounding / 2,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP],
    ).translate([wall_thickness, wall_thickness, -1 - lid_thickness])
    shell = shell - cut2

    cube1 = pybosl2.shapes3d.cuboid([wall_thickness, wall_thickness, height], anchor=TOP).translate(
        [wall_thickness * 3 / 2, wall_thickness * 3 / 2, height - finger_height - lid_thickness - foot_offset]
    )
    shell = shell - cube1
    cube2 = pybosl2.shapes3d.cuboid([wall_thickness, wall_thickness, height], anchor=TOP).translate(
        [
            width - wall_thickness * 3 / 2,
            length - wall_thickness * 3 / 2,
            height - finger_height - lid_thickness - wall_thickness / 4 - foot_offset,
        ]
    )
    shell = shell - cube2

    shell = shell.color(material_colour)

    radius = max(finger_height, 7)

    # depth_of_hole spans THREE wall thicknesses (centered on the wall) rather than barely one:
    # FingerHoleWall's rounded-lip flare (os_circle(-rounding_edge)) makes the cutter narrower
    # in the middle of its sweep than at its end faces, so a cutter only fractionally deeper
    # than the wall leaves a thin mid-wall fin standing inside the scallop -- the wall must sit
    # entirely within the sweep's straight middle section to be cleared across its full width.
    # The extra depth is harmless: it hangs outside the shell on one side and into the already
    # hollowed interior on the other.
    corner1 = CornerCatch(
        radius=radius,
        height=finger_height,
        depth_of_hole=wall_thickness * 3,
        rounding_edge=wall_thickness / 4,
        round_back=False,
    ).translate([wall_thickness / 2, wall_thickness / 2, height - finger_height - lid_thickness - foot_offset])
    shell = shell - corner1

    corner2 = CornerCatch(
        radius=radius,
        height=finger_height,
        depth_of_hole=wall_thickness * 3,
        rounding_edge=wall_thickness / 4,
        round_back=False,
        round_corner_back=False,
        spin=180,
    ).translate(
        [width - wall_thickness / 2, length - wall_thickness / 2, height - finger_height - lid_thickness - foot_offset]
    )
    shell = shell - corner2

    catches = None

    def add_catch(piece: PyOpenSCAD) -> None:
        nonlocal catches
        catches = piece if catches is None else catches | piece

    if (
        (lid_catch == CatchType.SHORT and width < length)
        or (lid_catch == CatchType.LONG and width > length)
        or lid_catch == CatchType.ALL
    ):
        catch_width = width - wall_thickness * 2
        add_catch(
            pybosl2.shapes3d.wedge(
                [catch_width * 2 / 4 - size_spacing * 2, lid_thickness - size_spacing, lid_thickness - size_spacing]
            )
            .translate([(catch_width * 2 / 8) + size_spacing + wall_thickness, wall_thickness, 0])
            .color(material_colour)
            .shape
        )
        add_catch(
            pybosl2.shapes3d.wedge(
                [catch_width * 2 / 4 - size_spacing * 2, lid_thickness - size_spacing, lid_thickness - size_spacing]
            )
            .rotate([0, 0, 180])
            .translate([(catch_width * 6 / 8) + size_spacing + wall_thickness, length - wall_thickness, 0])
            .color(material_colour)
            .shape
        )
    if (
        (lid_catch == CatchType.SHORT and length < width)
        or (lid_catch == CatchType.LONG and length < width)
        or lid_catch == CatchType.ALL
    ):
        catch_length = length - wall_thickness * 2
        add_catch(
            pybosl2.shapes3d.wedge(
                [catch_length * 2 / 4 - size_spacing * 2, lid_thickness - size_spacing, lid_thickness - size_spacing]
            )
            .rotate([0, 0, 90])
            .translate([width - wall_thickness, catch_length * 2 / 8 + size_spacing + wall_thickness, 0])
            .color(material_colour)
            .shape
        )
        add_catch(
            pybosl2.shapes3d.wedge(
                [catch_length * 2 / 4 - size_spacing * 2, lid_thickness - size_spacing, lid_thickness - size_spacing]
            )
            .rotate([0, 0, 270])
            .translate([wall_thickness, catch_length * 6 / 8 + size_spacing + wall_thickness, 0])
            .color(material_colour)
            .shape
        )
    if (lid_catch == CatchType.BUMPS_SHORT and width <= length) or (
        lid_catch == CatchType.BUMPS_LONG and width > length
    ):
        catch_offset = width - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            x = (catch_offset * frac) + wall_thickness
            bump_a = _catch_bump(wall_thickness, wall_thickness * 4 / 6, FRONT)
            bump_b = _catch_bump(wall_thickness, wall_thickness * 4 / 6, BACK).translate(
                [0, length - wall_thickness * 10 / 8, 0]
            )
            add_catch(
                (bump_a | bump_b)
                .translate([x, wall_thickness * 5 / 8, wall_thickness + wall_thickness / 8])
                .color(material_colour)
            )
    if (lid_catch == CatchType.BUMPS_SHORT and length < width) or (
        lid_catch == CatchType.BUMPS_LONG and length > width
    ):
        catch_offset = length - wall_thickness * 2
        for frac in (6 / 8, 2 / 8):
            y = (catch_offset * frac) + wall_thickness
            bump_a = _catch_bump(wall_thickness, wall_thickness * 4 / 6, LEFT)
            bump_b = _catch_bump(wall_thickness, wall_thickness * 4 / 6, RIGHT).translate(
                [width - wall_thickness * 10 / 8, 0, 0]
            )
            add_catch(
                (bump_a | bump_b)
                .translate([wall_thickness * 5 / 8, y, wall_thickness + wall_thickness / 8])
                .color(material_colour)
            )

    body = lid_stack | shell
    if catches is not None:
        body = body | catches

    # Returned label-face-up (construction orientation), matching SlidingLid's convention: the
    # lid's decorated top -- the mesh pattern and any label -- is what shows in renders and is
    # the face an MMU print colors in its final layers. The original SCAD module flipped the
    # lid upside-down here (opening up, label buried against the build plate), which is why
    # labeled slipover lids appeared to have no label in the output.
    return body


def SlipoverBoxLidWithLabelAndCustomShape(
    size: list[float],
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
    foot: float = 0,
    finger_hole_length: bool = False,
    finger_hole_width: bool = True,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for a slipover box, with a repeating pattern and a label.

    Usage::

        SlipoverBoxLidWithLabelAndCustomShape([100, 50, 20], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size: [width, length, height] outside size of the lid
        text_str: label text
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        layout_width: pattern repeat width (default default_lid_layout_width)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        aspect_ratio: dy scale factor (default 1.0)
        lid_rounding: lid edge rounding (default wall_thickness/2)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        foot:    size of the foot on the box
        finger_hole_length/finger_hole_width: unused, kept for API compatibility
        lid_pattern_dense/lid_dense_shape_edges: dense layout options
        material_colour: colour (default default_material_colour)
        lid_catch: catch style (default default_lid_catch_type)
        pattern_inner_control: inner control mode
        label_options: :class:`~labels.LabelOptions`
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    calc_label_options = (
        label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    )
    assert size[0] > 0 and size[1] > 0 and size[2] > 0, f"Need width, length, height > 0 size={size}"
    assert text_str is not None, "text_str must not be None"

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=[size[0], size[1]],
        lid_thickness=lid_thickness,
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        dense=lid_pattern_dense,
        dense_shape_edges=lid_dense_shape_edges,
        inner_control=pattern_inner_control,
        children=pattern_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_shape = MakeLidLabel(
        size=[size[0], size[1]], lid_thickness=lid_thickness, options=label_opts, text_str=text_str
    )

    lid_children = [mesh, label_shape] + (list(extra_children) if extra_children else [])

    return SlipoverBoxLid(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        foot=foot,
        finger_hole_length=finger_hole_length,
        finger_hole_width=finger_hole_width,
        material_colour=material_colour,
        lid_catch=lid_catch,
        children=lid_children,
    )


def SlipoverBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    lid_boundary: float = 10,
    wall_thickness: float | None = None,
    foot: float = 0,
    layout_width: float | None = None,
    aspect_ratio: float | None = 1.0,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    finger_hole_length: bool = False,
    finger_hole_width: bool = True,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    lid_catch: CatchType | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Lid for a slipover box with an automatic label and shape pattern.

    Usage::

        SlipoverBoxLidWithLabel(size=[20, 100, 10], text_str="Marmoset",
            shape_options=MakeShapeObject(shape_type=ShapeType.CIRCLE, shape_width=14), layout_width=10)

    Args:
        size: [width, length, height] outside size of the lid
        text_str: label text
        extra_children: additional children (list of solids)
        lid_boundary: boundary around the lid edge (default 10)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        foot:    size of the foot on the box
        layout_width: pattern repeat width (default default_lid_layout_width)
        aspect_ratio: dy scale factor (default 1.0)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        finger_hole_length/finger_hole_width: unused, kept for API compatibility
        lid_rounding: rounding on the lid (default wall_thickness)
        material_colour: colour (default default_material_colour)
        lid_catch: catch style (default default_lid_catch_type)
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
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size
    calc_label_options = (
        label_options if label_options is not None else MakeLabelOptions(material_colour=material_colour)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    assert width > 0 and length > 0 and height > 0, (
        f"Need width, length, height > 0 width={width} length={length} height={height}"
    )
    assert text_str is not None, "text_str must not be None"

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return SlipoverBoxLidWithLabelAndCustomShape(
        size=size,
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_boundary=lid_boundary,
        finger_hole_length=finger_hole_length,
        finger_hole_width=finger_hole_width,
        foot=foot,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        material_colour=material_colour,
        lid_catch=lid_catch,
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        shape_child=shape_piece,
        extra_children=extra_children,
    )
