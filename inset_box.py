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

# LibFile: inset_box.py
#    Inset / tabbed box pieces, including rabbit-clip lids.
#
# FileSummary: Various modules to generate board game inserts.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.shapes3d
import pysolidfive
from lids_base import (
    internal_build_lid,
    MakeLidLabel,
    LidMeshBasic,
    MakeLidTab,
    MakeTabs,
    IsDenseShapeType,
    DenseShapeEdges,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


def InsetLid(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    inset: float = 1,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Make a lid inset into the box with tabs on the side to close the box.

    This just does the insets around the top. Entries in *children* may be
    a callable(inner_width, inner_length).

    Usage::

        InsetLid([50, 100])

    Args:
        size: [width, length] outside size of the lid
        children: list of solids/callables placed in the lid
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        inset: how far the side is inset from the edge of the box (default 1)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
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
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness / 2

    inner_width = width - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2
    inner_length = length - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2

    top = (
        pybosl2.shapes3d.cuboid(
            [inner_width, inner_length, lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=calc_lid_rounding,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        .color(material_colour)
        .translate([wall_thickness - inset + m_piece_wiggle_room, wall_thickness - inset + m_piece_wiggle_room, 0])
    )

    kids = list(children) if children else []
    resolved_kids = [(c(inner_width, inner_length) if callable(c) else c) for c in kids]
    return internal_build_lid(lid_thickness=lid_thickness, children=[top] + resolved_kids, size_spacing=size_spacing)


def InsetLidTabbed(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    inset: float = 1,
    size_spacing: float | None = None,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    prism_width: float = 0.75,
    tab_length: float = 10,
    tab_height: float = 8,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Makes an inset lid with tabs on the side.

    Usage::

        InsetLidTabbed([30, 100])

    Args:
        size: [width, length] outside size of the lid
        children: list of solids/callables placed in the lid
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        inset: how far to inset the lid (default 1)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        make_tab_width: makes tabs on the width (default False)
        make_tab_length: makes tabs on the length (default True)
        prism_width: width of the prism in the tab (default 0.75)
        tab_length: length of the tab (default 10)
        tab_height: height of the tab (default 8)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]

    lid = InsetLid(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        inset=inset,
        size_spacing=size_spacing,
        lid_rounding=lid_rounding,
        material_colour=material_colour,
        children=children,
    )

    tab = MakeLidTab(
        length=tab_length,
        height=tab_height,
        lid_thickness=lid_thickness,
        prism_width=prism_width,
        wall_thickness=wall_thickness,
    )
    tabs = MakeTabs(
        size=[width, length],
        lid_thickness=lid_thickness,
        make_tab_width=make_tab_width,
        make_tab_length=make_tab_length,
        children=tab,
    ).color(material_colour)

    return (lid | tabs).rotate([180, 0, 0]).translate([0, length, lid_thickness])


def InsetLidTabbedWithLabelAndCustomShape(
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
    tab_length: float = 10,
    tab_height: float = 8,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    prism_width: float = 0.75,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int | bool = False,
    pattern_inner_control: int = False,
) -> PyOpenSCAD:
    """Lid for an inset tabbed box, with a repeating pattern and a label.

    Usage::

        InsetLidTabbedWithLabelAndCustomShape(size=[100, 50], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        (other args, see :func:`InsetLidTabbed` and :func:`~lids_base.LidMeshBasic`)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=size,
        lid_thickness=lid_thickness,
        boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        inner_control=pattern_inner_control,
        dense=lid_pattern_dense,
        dense_shape_edges=lid_dense_shape_edges,
        children=pattern_shape,
    )

    label_opts = copy.copy(calc_label_options)
    label_opts.full_height = True
    label_shape = MakeLidLabel(size=[width, length], options=label_opts, lid_thickness=lid_thickness, text_str=text_str)

    lid_children = [mesh, label_shape] + (list(extra_children) if extra_children else [])

    return InsetLidTabbed(
        size=size,
        lid_thickness=lid_thickness,
        tab_length=tab_length,
        tab_height=tab_height,
        lid_rounding=lid_rounding,
        prism_width=prism_width,
        make_tab_length=make_tab_length,
        make_tab_width=make_tab_width,
        size_spacing=size_spacing,
        material_colour=material_colour,
        children=lid_children,
    )


def InsetLidTabbedWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    lid_thickness: float | None = None,
    lid_boundary: float = 10,
    tab_length: float = 10,
    tab_height: float = 8,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    prism_width: float = 0.75,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    lid_rounding: float | None = None,
    size_spacing: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Composite lid: an inset tabbed lid with a label and a pattern.

    Usage::

        InsetLidTabbedWithLabel(size=[100, 100], lid_thickness=3, text_str="Trains")

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        extra_children: additional children (list of solids)
        (other args, see :func:`InsetLidTabbedWithLabelAndCustomShape`)
    """
    if material_colour is None:
        material_colour = default_material_colour
    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return InsetLidTabbedWithLabelAndCustomShape(
        size=size,
        lid_thickness=lid_thickness,
        tab_length=tab_length,
        prism_width=prism_width,
        tab_height=tab_height,
        make_tab_width=make_tab_width,
        make_tab_length=make_tab_length,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        material_colour=material_colour,
        lid_rounding=lid_rounding,
        label_options=calc_label_options,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        shape_child=shape_piece,
        extra_children=extra_children,
    )


def MakeBoxWithInsetLidTabbed(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    tab_height: float = 8,
    inset: float = 1,
    make_tab_width: bool = False,
    make_tab_length: bool = True,
    prism_width: float = 0.75,
    tab_length: float = 10,
    stackable: bool = False,
    size_spacing: float | None = None,
    floor_thickness: float | None = None,
    tab_offset: float = 0.45,
    material_colour: str | None = None,
    positive_colour: str | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
) -> PyOpenSCAD:
    """Makes a box with an inset lid, with all the pieces for tabs.

    Cutouts are only inside the box and in the floor. The 0,0,0 origin for
    *children* is the bottom inside of the box. *children* entries may be
    a callable(inner_width, inner_length, inner_height).

    Usage::

        MakeBoxWithInsetLidTabbed(size=[30, 100, 20])

    Args:
        size:    [width, length, height] outside size of the box
        children: list of solids/callables to carve inside the box
        wall_thickness: how thick the walls are (default default_wall_thickness)
        lid_thickness: how high the lid is (default default_lid_thickness)
        tab_height: how high to make the tabs (default 8)
        inset:   how far to inset the lid (default 1)
        make_tab_width/make_tab_length: tab placement (default False/True)
        prism_width: width of the prism (default 0.75)
        tab_length: how long the tab is (default 10)
        stackable: pull a piece out the bottom to let this stack (default False)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        tab_offset: offset for the tab cutout (default 0.45)
        material_colour: colour (default default_material_colour)
        positive_colour: colour of positive pieces (default default_positive_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if positive_colour is None:
        positive_colour = default_positive_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size

    body = pybosl2.shapes3d.cuboid(
        [width, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)

    lid_cut = (
        cube([width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1])
        .color(material_colour)
        .translate([wall_thickness - inset, wall_thickness - inset, height - lid_thickness])
    )
    body = body - lid_cut

    tab_cutter = minkowski(
        cube(tab_offset * 2).color(material_colour).translate([-tab_offset, -tab_offset, -tab_offset]),
        MakeLidTab(
            length=tab_length,
            height=tab_height,
            lid_thickness=lid_thickness,
            prism_width=prism_width,
            wall_thickness=wall_thickness,
        ),
    ).color(material_colour)
    tabs_cut = (
        MakeTabs(
            size=[width, length],
            lid_thickness=lid_thickness,
            tab_length=tab_length,
            make_tab_length=make_tab_length,
            make_tab_width=make_tab_width,
            children=tab_cutter,
        )
        .color(material_colour)
        .translate([0, 0, height - lid_thickness])
    )
    body = body - tabs_cut

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            body = body - piece.translate([wall_thickness, wall_thickness, floor_thickness])

    if stackable:
        outer = (
            cube([width + 1, length + 1, wall_thickness + 0.5 - size_spacing])
            .color(material_colour)
            .translate([-0.5, -0.5, -0.5])
        )
        inner_cut = (
            cube(
                [
                    width - (wall_thickness - inset + size_spacing) * 2,
                    length - (wall_thickness - inset + size_spacing) * 2,
                    wall_thickness + 2,
                ]
            )
            .color(material_colour)
            .translate([wall_thickness - inset + size_spacing, wall_thickness - inset + size_spacing, -1])
        )
        body = body - (outer - inner_cut)

    result = body
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


def InsetLidRabbitClip(
    size: list[float],
    children: "list | None" = None,
    lid_thickness: float = 2,
    wall_thickness: float = 2,
    inset: float = 1,
    size_spacing: float | None = None,
    make_rabbit_width: bool = False,
    make_rabbit_length: bool = True,
    rabbit_width: float = 7,
    rabbit_length: float = 6,
    rabbit_lock: bool = False,
    rabbit_compression: float = 0.1,
    rabbit_thickness: float = 0.8,
    rabbit_snap: float = 0.25,
    rabbit_offset: float = 3,
    rabbit_depth: float = 1.5,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Makes an inset lid with rabbit clips on the side.

    Usage::

        InsetLidRabbitClip(size=[30, 100])

    Args:
        size: [width, length] outside size of the lid
        children: list of solids/callables placed in the lid
        lid_thickness: height of the lid (default 2)
        wall_thickness: thickness of the walls (default 2)
        inset: how far to inset the lid (default 1)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        make_rabbit_width/make_rabbit_length: rabbit placement (default False/True)
        rabbit_width/rabbit_length: rabbit dimensions (default 7/6)
        rabbit_lock: if the rabbit should have a locking piece (default False)
        rabbit_compression: sideways give on the rabbit (default 0.1)
        rabbit_thickness: thickness of the rabbit (default 0.8)
        rabbit_snap: depth of the snap curve (default 0.25)
        rabbit_offset: offset on each side of the rabbit (default 3)
        rabbit_depth: extrusion depth of the rabbit (default 1.5)
        lid_rounding: rounding on the edge of the lid (default wall_thickness/2)
        material_colour: colour (default default_material_colour)
    """
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]

    lid = InsetLid(
        size=size,
        lid_thickness=lid_thickness,
        wall_thickness=wall_thickness,
        inset=inset,
        size_spacing=size_spacing,
        lid_rounding=lid_rounding,
        material_colour=material_colour,
        children=children,
    )

    base = pysolidfive.cuboid([rabbit_length + rabbit_offset, wall_thickness, lid_thickness]).translate(
        [(rabbit_length + rabbit_offset) / 2, wall_thickness / 2, -lid_thickness / 2]
    )
    clip = pysolidfive.rabbit_clip(
        type="pin",
        length=rabbit_length,
        width=rabbit_width,
        snap=rabbit_snap,
        thickness=rabbit_thickness,
        depth=rabbit_depth,
        compression=rabbit_compression,
        lock=rabbit_lock,
    ).translate([(rabbit_length + rabbit_offset) / 2, wall_thickness / 2, lid_thickness / 2])
    # A factory, not a pre-meshed solid: PythonSCAD segfaults when one frep()-meshed handle
    # is transformed in more than one CSG branch, and MakeTabs places the tab several times.
    tab = lambda: (base | clip).mesh()  # noqa: E731

    tabs = MakeTabs(
        size=[width, length],
        lid_thickness=lid_thickness,
        make_tab_width=make_rabbit_width,
        make_tab_length=make_rabbit_length,
        children=tab,
    ).color(material_colour)

    return (lid | tabs).rotate([180, 0, 0]).translate([0, length, lid_thickness])


def InsetLidRabbitClipWithLabelAndCustomShape(
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
    make_rabbit_width: bool = False,
    make_rabbit_length: bool = True,
    rabbit_width: float = 7,
    rabbit_length: float = 6,
    rabbit_lock: bool = False,
    rabbit_compression: float = 0.1,
    rabbit_thickness: float = 0.8,
    rabbit_snap: float = 0.25,
    rabbit_offset: float = 3,
    rabbit_depth: float = 1.5,
    pattern_inner_control: int = False,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    """Lid for an inset rabbit-clip box, with a repeating pattern and a label.

    Usage::

        InsetLidRabbitClipWithLabelAndCustomShape(size=[100, 50], text_str="Frog",
            shape_child=ShapeByType(MakeShapeObject(
                shape_type=ShapeType.SUPERSHAPE, shape_thickness=2,
                supershape_m1=12, supershape_m2=12, supershape_n1=1,
                supershape_b=1.5, shape_width=15)))

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        shape_child: 2-D shape solid to tile on the lid
        extra_children: additional children (list of solids)
        (other args, see :func:`InsetLidRabbitClip`)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y], size={size}"
    width, length = size[0], size[1]
    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )

    pattern_shape = shape_child if shape_child is not None else square([10, 10]).color(material_colour)
    mesh = LidMeshBasic(
        size=size,
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
    label_shape = MakeLidLabel(size=[width, length], options=label_opts, lid_thickness=lid_thickness, text_str=text_str)

    lid_children = [mesh, label_shape] + (list(extra_children) if extra_children else [])

    return InsetLidRabbitClip(
        size=size,
        lid_thickness=lid_thickness,
        make_rabbit_length=make_rabbit_length,
        make_rabbit_width=make_rabbit_width,
        rabbit_width=rabbit_width,
        rabbit_length=rabbit_length,
        rabbit_lock=rabbit_lock,
        rabbit_offset=rabbit_offset,
        rabbit_thickness=rabbit_thickness,
        rabbit_compression=rabbit_compression,
        rabbit_depth=rabbit_depth,
        lid_rounding=lid_rounding,
        size_spacing=size_spacing,
        material_colour=material_colour,
        children=lid_children,
    )


def InsetLidRabbitClipWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    lid_thickness: float = 3,
    lid_boundary: float = 10,
    make_rabbit_width: bool = False,
    make_rabbit_length: bool = True,
    aspect_ratio: float | None = 1.0,
    rabbit_width: float = 7,
    rabbit_length: float = 6,
    rabbit_lock: bool = False,
    rabbit_compression: float = 0.1,
    rabbit_thickness: float = 0.8,
    rabbit_snap: float = 0.25,
    rabbit_offset: float = 3,
    layout_width: float | None = None,
    rabbit_depth: float = 1.5,
    lid_rounding: float | None = None,
    size_spacing: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    """Composite lid: an inset rabbit-clip lid with a label and a pattern.

    Usage::

        InsetLidRabbitClipWithLabel(size=[100, 100], lid_thickness=3, text_str="Trains")

    Args:
        size: [width, length] outside size of the lid
        text_str: label text
        extra_children: additional children (list of solids)
        (other args, see :func:`InsetLidRabbitClipWithLabelAndCustomShape`)
    """
    if material_colour is None:
        material_colour = default_material_colour
    calc_label_options = (
        label_options
        if label_options is not None
        else MakeLabelOptions(material_colour=material_colour, full_height=True)
    )
    calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()

    shape_piece_raw = ShapeByType(options=calc_shape_options)
    assert shape_piece_raw is not None, "shape_options must not be ShapeType.NONE here"
    shape_piece = shape_piece_raw.color(material_colour)

    return InsetLidRabbitClipWithLabelAndCustomShape(
        size=size,
        lid_thickness=lid_thickness,
        make_rabbit_length=make_rabbit_length,
        make_rabbit_width=make_rabbit_width,
        rabbit_width=rabbit_width,
        rabbit_length=rabbit_length,
        rabbit_lock=rabbit_lock,
        rabbit_offset=rabbit_offset,
        rabbit_thickness=rabbit_thickness,
        rabbit_compression=rabbit_compression,
        rabbit_depth=rabbit_depth,
        lid_rounding=lid_rounding,
        text_str=text_str,
        layout_width=layout_width,
        size_spacing=size_spacing,
        aspect_ratio=aspect_ratio,
        lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
        lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
        pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
        material_colour=material_colour,
        label_options=calc_label_options,
        shape_child=shape_piece,
        extra_children=extra_children,
    )


def MakeBoxWithInsetLidRabbitClip(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    tab_height: float = 8,
    floor_thickness: float | None = None,
    inset: float = 1,
    make_rabbit_width: bool = False,
    make_rabbit_length: bool = True,
    rabbit_width: float = 6,
    rabbit_length: float = 7,
    rabbit_offset: float = 3,
    rabbit_lock: bool = False,
    rabbit_compression: float = 0.1,
    rabbit_thickness: float = 0.8,
    rabbit_snap: float = 0.25,
    size_spacing: float | None = None,
    rabbit_depth: float = 1.5,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    positive_colour: str | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    """Makes a box with an inset lid using rabbit clips.

    The 0,0,0 origin for *children* is the bottom inside of the box.
    *children* entries may be a callable(inner_width, inner_length, inner_height).

    Usage::

        MakeBoxWithInsetLidRabbitClip(size=[30, 100, 20])

    Args:
        size:    [width, length, height] outside size of the box
        children: list of solids/callables to carve inside the box
        wall_thickness: how thick the walls are (default default_wall_thickness)
        lid_thickness: how high the lid is (default default_lid_thickness)
        tab_height: unused, kept for API compatibility
        floor_thickness: thickness of the floor (default default_floor_thickness)
        inset:   how far to inset the lid (default 1)
        make_rabbit_width/make_rabbit_length: rabbit placement (default False/True)
        rabbit_width/rabbit_length: rabbit dimensions (default 6/7)
        rabbit_offset: offset on each side of the rabbit (default 3)
        rabbit_lock/rabbit_compression/rabbit_thickness/rabbit_snap/rabbit_depth: rabbit-clip parameters
        size_spacing: wiggle room (default m_piece_wiggle_room)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        positive_colour: colour of positive pieces (default default_positive_colour)
        material_colour: colour (default default_material_colour)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []
    if positive_colour is None:
        positive_colour = default_positive_colour
    if material_colour is None:
        material_colour = default_material_colour

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"size must be set to [x,y,z], size={size}"
    width, length, height = size

    body = pybosl2.shapes3d.cuboid(
        [width, length, height - lid_thickness - size_spacing],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
    ).color(material_colour)

    lid_cut = (
        cube([width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1])
        .color(material_colour)
        .translate([wall_thickness - inset, wall_thickness - inset, height - lid_thickness])
    )
    body = body - lid_cut

    socket_box = pysolidfive.cuboid(
        [rabbit_length + rabbit_offset + size_spacing * 2, wall_thickness + 0.01, lid_thickness + 0.01]
    ).translate([(rabbit_length + rabbit_offset + size_spacing * 2) / 2, wall_thickness / 2 - 0.01, -lid_thickness / 2])
    socket_clip = pysolidfive.rabbit_clip(
        type="socket",
        length=rabbit_length,
        width=rabbit_width,
        snap=rabbit_snap,
        thickness=rabbit_thickness,
        depth=rabbit_depth + 0.01,
        compression=rabbit_compression,
        lock=rabbit_lock,
    ).translate([(rabbit_length + rabbit_offset + size_spacing * 2) / 2, wall_thickness / 2 - 0.01, -lid_thickness])
    # A factory for the same frep-handle-reuse reason as the pin tab above.
    socket = lambda: (socket_box | socket_clip).color(material_colour)  # noqa: E731

    tabs_cut = (
        MakeTabs(
            size=[width, length],
            lid_thickness=lid_thickness,
            tab_length=rabbit_length + rabbit_offset,
            make_tab_length=make_rabbit_length,
            make_tab_width=make_rabbit_width,
            children=socket,
        )
        .color(material_colour)
        .translate([0, 0, height - lid_thickness])
    )
    body = body - tabs_cut

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            body = body - piece.translate([wall_thickness, wall_thickness, floor_thickness])

    result = body
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
