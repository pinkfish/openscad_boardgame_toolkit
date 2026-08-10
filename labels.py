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

# LibFile: labels.py
#    Shared label pieces — framed and frameless label generators.
#
# FileSummary: Shared label pieces.
# FileGroup: Basics

from base_bgtk import (
    BOTTOM,
    FRONT,
    LEFT,
    Color,
    LabelType,
    default_label_background_colour,
    default_label_colour,
    default_label_font,
    default_label_solid_background,
    default_label_type,
    default_material_colour,
    default_slicing_layer_height,
    native_colour,
    union_all_2d,
)
from pythonscad import textmetrics
from pybosl2 import Anchor
from pybosl2 import shapes3d
from pybosl2 import shapes2d
from pybosl2.shapes3d import Bosl2Solid
from pybosl2.shapes2d import Bosl2Shape2D

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Annotation-only: the native handle type has no runtime object to import.
    from openscad import PyOpenSCAD  # noqa: F401


# ---------------------------------------------------------------------------
# Section: Labels
# ---------------------------------------------------------------------------


@dataclass
class LabelOptions:
    """Container for all label-styling options.

    Create one with :func:`MakeLabelOptions` and pass it to any
    label-making function.

    Args:
        text_scale:              font scale factor (default 1.0)
        text_length:             length of the text area (default auto)
        angle:                   text rotation angle (default auto)
        label_colour:            text colour (default default_label_colour)
        label_background_colour: background colour (default default_label_background_colour)
        short_length:            use the short dimension for layout (default False)
        label_diff:              [dx, dy] positional offset (default [0, 0])
        border:                  border width in mm (default 2)
        offset:                  text margin in mm (default 4)
        radius:                  corner radius (default 5)
        font:                    font string (default default_label_font)
        full_height:             if True the label fills the full lid thickness (default False)
        finger_hole_size:        diameter of optional finger holes (default 10)
        material_colour:         material colour (default default_material_colour)
        label_type:              one of the :class:`LabelType` enum values (default default_label_type)
    """

    text_scale: float = 1.0
    text_length: float | None = None
    angle: float | None = 0
    label_colour: Color = default_label_colour
    label_background_colour: Color = default_label_background_colour
    short_length: bool = False
    label_diff: list[float] = field(default_factory=lambda: [0, 0])
    border: float = 2
    offset: float = 4
    radius: float = 5
    font: str = default_label_font
    full_height: bool = False
    finger_hole_size: float | None = 10
    material_colour: Color = default_material_colour
    label_type: LabelType = default_label_type
    solid_background: bool = default_label_solid_background


def MakeLabelOptions(**kwargs) -> LabelOptions:
    """Constructs a :class:`LabelOptions`, the options container passed to
    every label-making function in this file.

    Usage::

        MakeLabelOptions(material_colour=Color("yellow"))
        MakeLabelOptions(font="Stencil Std:style=Bold", label_type=LabelType.FRAMELESS)

    Args:
        **kwargs: any field of :class:`LabelOptions`; omitted fields fall back
            to their dataclass defaults.
    """
    return LabelOptions(**kwargs)


def MakeStripedGrid(size: list[float], bar_width: float = 1) -> "Bosl2Shape2D":
    """Creates a 2-D striped background grid for labels.

    Usage::

        MakeStripedGrid([20, 50])

    Args:
        size:      [width, length] of the grid area
        bar_width: width of each stripe (default 1)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2, f"size must be set to [x,y], size={size}"
    width, length = size
    assert width > 0 and length > 0, f"width and length must be > 0 width={width} length={length}"

    dx = bar_width * 2
    x_count = (width + length) / (bar_width + dx)

    pieces: list[PyOpenSCAD] = []
    for j in range(math.floor(x_count) + 1):
        bar = shapes2d.square([bar_width, length * 2], anchor=FRONT + LEFT).rotate([0, 0, 45]).translate(
            [j * (bar_width + dx), -bar_width]
        )
        piece = shapes2d.square([width, length], anchor=FRONT + LEFT) & bar
        pieces.append(piece)
    # pybosl2 2-D shapes union via the | operator (native union() can't consume Bosl2Shape2D).
    result = pieces[0]
    for p in pieces[1:]:
        result = result | p
    return result


def Make3dStripedGrid(
    size: list[float],
    height: float,
    bar_width_top: float = 1,
    bar_width_bottom: float | None = None,
    spacing: float = 0,
) -> PyOpenSCAD:
    """Creates a 3-D striped background grid for labels.

    Usage::

        Make3dStripedGrid(size=[20, 50], height=1)
        Make3dStripedGrid(size=[20, 50], height=0.2, bar_width_bottom=1)

    Args:
        size:             [width, length] of the grid
        height:           extrusion height
        bar_width_top:    top face stripe width (default 1)
        bar_width_bottom: bottom face stripe width (default bar_width_top)
        spacing:          gap between stripes (default 0)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2, f"size must be set to [x,y], size={size}"
    width, length = size
    assert width > 0 and length > 0, f"width and length must be > 0 width={width} length={length}"

    calc_bar_width_bottom = bar_width_bottom if bar_width_bottom is not None else bar_width_top
    bar_width = max(bar_width_top, calc_bar_width_bottom)

    dx = bar_width * 2 + spacing
    x_count = (width + length) / (bar_width + dx)

    pieces: list[PyOpenSCAD] = []
    for j in range(math.floor(x_count) + 1):
        piece = (
            shapes3d.prismoid(
                size1=[calc_bar_width_bottom, length * 2],
                size2=[bar_width_top, length * 2],
                height=height,
                anchor=BOTTOM + LEFT,
            )
            .rotate([0, 0, 45])
            .translate([j * (bar_width + dx), length / 2, 0])
        )
        pieces.append(piece)
    # union_all_2d keeps the result a pybosl2 wrapper. That matters beyond tidiness: the NATIVE
    # __sub__ RAISES "invalid argument left to operator" instead of returning NotImplemented,
    # so Python never falls back to the wrapper's __rsub__ -- a native left operand with a
    # wrapper on the right is a hard error, which is what broke UnionJack.
    shape = union_all_2d(pieces)  # dimension-agnostic: it just balances the | tree
    assert shape is not None
    return shape


def MakeMainLidLabelSolid(size: list[float], lid_thickness: float, label: str, options: LabelOptions) -> PyOpenSCAD:
    """Makes a label in a solid-background frame for use on lids.

    Usage::

        MakeMainLidLabelSolid(size=[20, 80], lid_thickness=2,
                              label="Australia", options=MakeLabelOptions())

    Args:
        size:          [width, length] of the label section
        lid_thickness: height of the lid
        label:         text string to display
        options:       :class:`LabelOptions` (from :func:`MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2, f"size must be set to [x,y], size={size}"
    width, length = size
    assert width > options.border * 2, (
        f"Width must be wider than double the offset width={width} offset={options.offset} border={options.border}"
    )
    assert length > options.border * 2, (
        f"Length must be wider than double the offset length={length} offset={options.offset} border={options.border}"
    )
    assert label is not None, "Must specify a label"
    assert options is not None, "Must speify label options"

    def TextShape(calc_font: str, text_height: float = lid_thickness, edge_offset: float = 0) -> PyOpenSCAD:
        # Scale the text uniformly (preserving its aspect ratio) to fit within the available
        # box, rather than resize()-ing each axis independently to fill it exactly -- native
        # resize() has no `auto=` support in this PythonSCAD build to do that for us, so the
        # fit-within-bounds scale factor is computed by hand from the text's own metrics.
        #
        # Also auto-rotate the text 90 degrees to read along whichever axis has more room --
        # text always renders reading along local +X, so on a label that's narrower than it is
        # long (the common case for a lid label), leaving it unrotated means it's constrained by
        # the short axis and comes out tiny with most of the long axis sitting empty.
        avail_w = width - options.offset * 2.5
        avail_l = length - options.offset * 2
        metrics = textmetrics(str(label), font=calc_font, size=10)
        raw_w, raw_l = metrics["size"][0], metrics["size"][1]
        rotate_text = avail_l > avail_w
        if rotate_text:
            scale = min(avail_l / raw_w, avail_w / raw_l)
        else:
            scale = min(avail_w / raw_w, avail_l / raw_l)
        text_shape = shapes2d.text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom").resize(
            [raw_w * scale, raw_l * scale, 0]
        )
        if rotate_text:
            shape = (
                text_shape.rotate([0, 0, 90])
                .translate([options.offset + raw_l * scale, options.offset, 0])
                .offset(radius=edge_offset)
            )
        else:
            shape = text_shape.translate([options.offset, options.offset, 0]).offset(radius=edge_offset)
        return shape.linear_extrude(text_height)

    full_h = options.full_height
    h_half = (
        (lid_thickness - default_slicing_layer_height) if full_h else (lid_thickness / 2 - default_slicing_layer_height)
    )
    calc_font = options.font
    if calc_font is None:
        calc_font = default_label_font
    calc_label_colour = options.label_colour
    if calc_label_colour is None:
        calc_label_colour = default_label_colour

    result = (
        TextShape(text_height=default_slicing_layer_height + 0.01, calc_font=calc_font)
        .color(native_colour(calc_label_colour))
        .translate([0, 0, h_half])
    )

    rounding = options.radius if options.radius * 2 <= min(width, length) else min(width, length) / 2
    result = (
        result
        | shapes3d.cuboid([width, length, h_half], rounding=rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM)
        .color(options.material_colour)
        .shape
    )

    calc_background_colour = options.label_background_colour
    if calc_background_colour is None:
        calc_background_colour = default_label_background_colour

    bg_height = lid_thickness if (full_h or options.border > 0) else lid_thickness / 2
    bg_box = shapes3d.cuboid(
        [width, length, bg_height], rounding=rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM
    ).color(options.material_colour)
    cut_z = (
        (lid_thickness + default_slicing_layer_height if full_h else lid_thickness / 2 + default_slicing_layer_height)
        if options.solid_background
        else -0.5
    )
    w_cut = width - options.border * 2
    l_cut = length - options.border * 2
    cut_rounding = options.radius if options.radius * 2 <= min(w_cut, l_cut) else min(w_cut, l_cut) / 2
    cut_box = (
        shapes3d.cuboid(
            [w_cut, l_cut, lid_thickness + 1], rounding=cut_rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM
        )
        .color(options.material_colour)
        .translate([options.border, options.border, cut_z])
    )
    result = result | (bg_box - cut_box).shape

    inner_w = width - options.border * 2 - 0.02
    inner_l = length - options.border * 2 - 0.02
    inner_rounding = options.radius if options.radius * 2 < min(inner_w, inner_l) else min(inner_w, inner_l) / 2
    inner_box = (
        shapes3d.cuboid(
            [inner_w, inner_l, default_slicing_layer_height],
            rounding=inner_rounding,
            edges=Anchor.Z,
            anchor=FRONT + LEFT + BOTTOM,
        )
        .color(calc_background_colour)
        .translate([options.border + 0.01, options.border + 0.01, 0])
    )
    text_cut = (
        TextShape(text_height=default_slicing_layer_height + 21, calc_font=calc_font)
        .color(native_colour(calc_background_colour))
        .translate([0, 0, -1])
    )
    result = result | (inner_box - text_cut).translate([0, 0, h_half]).shape

    return result.translate([-width / 2 + options.label_diff[0], -length / 2 + options.label_diff[1], 0])


def MakeMainLidLabelStriped(size: list[float], lid_thickness: float, label: str, options: LabelOptions) -> "Bosl2Solid":
    """Makes a label in a striped-background frame for use on lids.

    Usage::

        MakeMainLidLabelStriped(size=[20, 80], lid_thickness=2,
                                label="Australia", options=MakeLabelOptions())

    Args:
        size:          [width, length] of the label section
        lid_thickness: height of the lid
        label:         text string to display
        options:       :class:`LabelOptions` (from :func:`MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2, f"size must be set to [x,y], size={size}"
    width, length = size
    assert width > options.border * 2, (
        f"Width must be wider than double the border width={width} offset={options.offset} border={options.border}"
    )
    assert length > options.border * 2, (
        f"Length must be wider than double the border length={length} offset={options.offset} border={options.border}"
    )
    assert label is not None, "Must specify a label"
    assert options is not None, "Must speify label options"

    full_h = options.full_height
    h_half = (
        (lid_thickness - default_slicing_layer_height) if full_h else (lid_thickness / 2 - default_slicing_layer_height)
    )

    def TextShape(calc_font: str, text_thickness: float = lid_thickness, edge_offset: float = 0) -> PyOpenSCAD:
        # See MakeMainLidLabelSolid's TextShape: resize() has no aspect-preserving `auto=`
        # support here, so the fit-within-bounds scale is computed by hand from the text
        # metrics, and the text is auto-rotated 90 degrees to read along whichever axis has
        # more room (otherwise a narrow-and-long label leaves it tiny and mostly empty).
        avail_w = width - options.offset * 2.5
        avail_l = length - options.offset * 2
        metrics = textmetrics(str(label), font=calc_font, size=10)
        raw_w, raw_l = metrics["size"][0], metrics["size"][1]
        rotate_text = avail_l > avail_w
        if rotate_text:
            scale = min(avail_l / raw_w, avail_w / raw_l)
        else:
            scale = min(avail_w / raw_w, avail_l / raw_l)
        text_shape = shapes2d.text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom").resize(
            [raw_w * scale, raw_l * scale, 0]
        )
        if rotate_text:
            shape = (
                text_shape.rotate([0, 0, 90])
                .translate([options.offset + raw_l * scale, options.offset, 0])
                .offset(radius=edge_offset)
            )
        else:
            shape = text_shape.translate([options.offset, options.offset, 0]).offset(radius=edge_offset)
        return shape.linear_extrude(text_thickness)

    def StripedBackground(calc_background_color: Color) -> "Bosl2Solid":
        w = width - options.border * 2
        l = length - options.border * 2
        rounding = options.radius if options.radius * 2 <= min(w, l) else min(w, l) / 2

        # Intersection (masking the box down to just the stripe bars), not union -- a union
        # here covers the whole footprint solidly, hiding the differently-colored striped
        # `bottom` layer beneath it entirely (this was rendering as a plain flat background).
        top = (
            shapes3d.cuboid(
                [w, l, default_slicing_layer_height], rounding=rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM
            )
            .color(calc_background_color)
            .translate([options.border + 0.01, options.border + 0.01, 0])
            & MakeStripedGrid(size=[width, length])
            .linear_extrude(height=default_slicing_layer_height * 2)
            .color(calc_background_color)
            .translate([0, 0, -default_slicing_layer_height / 2])
        ).translate([0, 0, h_half])

        box_part = (
            shapes3d.cuboid([w, l, h_half], rounding=rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM)
            .color(options.material_colour)
            .translate([options.border, options.border, 0])
        )
        stripes_part = (
            MakeStripedGrid([width, length]).linear_extrude(height=lid_thickness).color(options.material_colour)
        )
        bottom = box_part & stripes_part

        return top | bottom

    calc_font = options.font
    if calc_font is None:
        calc_font = default_label_font
    calc_background_color = options.label_background_colour
    if calc_background_color is None:
        calc_background_color = default_label_background_colour

    z = lid_thickness if (full_h or options.border > 0) else lid_thickness / 2
    rounding = options.radius if options.radius * 2 <= min(width, length) else min(width, length) / 2
    outer = shapes3d.cuboid([width, length, z], rounding=rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM).color(
        options.material_colour
    )
    w_cut = width - options.border * 2
    l_cut = length - options.border * 2
    cut_rounding = options.radius if options.radius * 2 <= min(w_cut, l_cut) else min(w_cut, l_cut) / 2
    cutter = (
        shapes3d.cuboid(
            [w_cut, l_cut, lid_thickness + 1], rounding=cut_rounding, edges=Anchor.Z, anchor=FRONT + LEFT + BOTTOM
        )
        .color(options.material_colour)
        .translate([options.border, options.border, -0.5])
    )
    result = outer - cutter

    result = result | TextShape(
        calc_font=calc_font,
        text_thickness=(lid_thickness - default_slicing_layer_height) if full_h else lid_thickness / 2,
        edge_offset=0.01,
    ).color(options.material_colour)

    label_z = (lid_thickness - default_slicing_layer_height) if full_h else (lid_thickness / 2)
    result = result | TextShape(
        calc_font=calc_font,
        text_thickness=default_slicing_layer_height if full_h else default_slicing_layer_height * 2,
        edge_offset=0.01,
    ).color(native_colour(options.label_colour)).translate([0, 0, label_z])

    result = result | TextShape(
        calc_font=calc_font,
        text_thickness=(lid_thickness - default_slicing_layer_height) if full_h else (default_slicing_layer_height * 2),
        edge_offset=0.01,
    ).color(options.material_colour)
    # Note: the original SCAD z-translate here is `full_height ? 0 : 0`, a
    # no-op in both branches, so nothing is applied — kept faithful to source.

    striped = StripedBackground(calc_background_color=calc_background_color)
    cut2 = (
        TextShape(calc_font=calc_font, text_thickness=lid_thickness * 4, edge_offset=0.01)
        .color(native_colour(options.material_colour))
        .translate([0, 0, (-lid_thickness / 2) if full_h else (lid_thickness / 2 - default_slicing_layer_height * 2)])
    )
    result = result | (striped - cut2)

    # `result` has been a Bosl2Solid ever since `outer - cutter` above (every later `|`/`-`
    # rewraps it, regardless of the other operand's type) -- unwrap to the native/mesh type
    # before returning, since callers combine this with plain native shapes (e.g.
    # sliding_box.py's build_lid() unions several lid children together, and a
    # Bosl2Solid mixed in among native ones breaks the native `|` operator).
    return result.translate([-width / 2 + options.label_diff[0], -length / 2 + options.label_diff[1], 0])


def MakeFramedLidLabel(size: list[float], lid_thickness: float, label: str, options: LabelOptions) -> "Bosl2Solid | None":
    """Makes a framed (solid or striped) label for a lid.

    Usage::

        MakeFramedLidLabel(size=[20, 80], lid_thickness=2,
                           label="Australia", options=MakeLabelOptions())

    Args:
        size:          [width, length] (or [width, length, height]) of the label area
        lid_thickness: height of the lid
        label:         text string to display
        options:       :class:`LabelOptions` (from :func:`MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) in (2, 3), f"size must be set to [x,y,z], size={size}"
    assert label is not None, "Must specify a label"
    assert options is not None, "Must speify label options"
    width, length = size[0], size[1]

    metrics = textmetrics(label, font=options.font)
    long_first = (length > width and not options.short_length) or (options.short_length and length < width)
    max_width = (width if long_first else length) - options.offset * 2
    max_length = (length if long_first else width) * 3 / 4 - options.offset * 2
    temp_calc_text_length = options.text_length
    if temp_calc_text_length is None:
        temp_calc_text_length = max_length
    temp_calc_text_width = (
        metrics["size"][1] / metrics["size"][0] * temp_calc_text_length * options.text_scale + options.offset * 2
    )
    calc_text_width = temp_calc_text_width if temp_calc_text_width <= max_width else max_width
    calc_text_length = (
        temp_calc_text_length
        if temp_calc_text_width <= max_width
        else temp_calc_text_length * max_width / temp_calc_text_width
    )
    calc_finger_hole_size = options.finger_hole_size
    if calc_finger_hole_size is None:
        calc_finger_hole_size = (
            10
            if (min(length, width) if options.short_length else max(length, width)) - calc_text_length - 10 > 0
            else 0
        )
    calc_radius = options.radius
    if calc_radius is None:
        calc_radius = min(5, calc_text_width / 4)

    if not (calc_text_width > 10 and calc_text_length > 1):
        print("WARNING: Lid too narrow for a label (ignoring label)")
        return None

    long_rotate = (width > length and not options.short_length) or (options.short_length and width < length)
    rotate_angle = 90 if long_rotate else 0

    result = None

    def add(piece: "PyOpenSCAD | shapes3d.Bosl2Solid") -> None:
        nonlocal result
        result = piece if result is None else result | piece

    if (
        calc_finger_hole_size > 0
        and calc_text_width + calc_finger_hole_size * 2 < width
        and calc_text_width + calc_finger_hole_size * 2 < length
    ):
        hole_a = (
            shapes3d.cyl(radius=calc_finger_hole_size, height=lid_thickness, anchor=BOTTOM)
            - shapes3d.cyl(radius=calc_finger_hole_size - options.border, height=lid_thickness + 1, anchor=BOTTOM).translate(
                [0, 0, -0.5]
            )
        ).translate([options.label_diff[0], -calc_text_width / 2 + options.label_diff[1], 0])
        hole_b = (
            shapes3d.cyl(radius=calc_finger_hole_size, height=lid_thickness, anchor=BOTTOM)
            - shapes3d.cyl(radius=calc_finger_hole_size - options.border, height=lid_thickness + 1, anchor=BOTTOM).translate(
                [0, 0, -0.5]
            )
        ).translate([options.label_diff[0], calc_text_width / 2 + options.label_diff[1], 0])
        cut = shapes3d.cuboid([calc_text_length, calc_text_width, lid_thickness + 1], anchor=BOTTOM).translate(
            [options.label_diff[0], options.label_diff[1], -0.5]
        )
        add(((hole_a | hole_b) - cut).color(options.material_colour))

    if options.solid_background:
        add(
            MakeMainLidLabelSolid(
                size=[calc_text_length, calc_text_width], lid_thickness=lid_thickness, label=label, options=options
            )
        )
    else:
        add(
            MakeMainLidLabelStriped(
                size=[calc_text_length, calc_text_width], lid_thickness=lid_thickness, label=label, options=options
            )
        )

    assert result is not None, "label produced no geometry"
    result = result.rotate([0, 0, rotate_angle])
    # `result` is a Bosl2Solid here whenever the finger-hole cutout applies (its `.color()`
    # rewraps it above), otherwise native from MakeMainLidLabelSolid()/MakeMainLidLabelStriped()
    # -- unwrap either way so callers always get a consistent, native, type (see those two
    # functions' own returns for the same reasoning).
    result = result.translate([length / 2, -width / 2, 0]).rotate([0, 0, 90])
    return result.shape if isinstance(result, Bosl2Solid) else result


def MakeFramelessLidLabel(size: list[float], lid_thickness: float, label: str, options: LabelOptions) -> PyOpenSCAD:
    """Makes a frameless (text only) label for a lid.

    Usage::

        MakeFramelessLidLabel(size=[40, 80], lid_thickness=2,
            label="Australia",
            options=MakeLabelOptions(font="Stencil Std:style=Bold",
                                     label_type=LabelType.FRAMELESS))

    Args:
        size:          [width, length] of the label area
        lid_thickness: height of the lid
        label:         text string to display
        options:       :class:`LabelOptions` (from :func:`MakeLabelOptions`)
    """
    assert isinstance(size, (list, tuple)) and len(size) == 2, f"size must be set to [x,y], size={size}"
    width, length = size
    assert width > 0 and length > 0, f"width and length must be > 0 width={width} length={length}"

    cross_angle = math.degrees(math.asin(min(width, length) / math.sqrt(width * width + length * length)))
    metrics = textmetrics(label, font=options.font)
    calc_text_length_start = options.text_length
    if calc_text_length_start is None:
        calc_text_length_start = length * 3 / 4 if length > width else width * 3 / 4
    temp_text_width = metrics["size"][1] / metrics["size"][0] * calc_text_length_start * options.text_scale
    if length < width:
        temp_text_length = (
            calc_text_length_start * (length * 3 / 4) / temp_text_width
            if temp_text_width > length * 3 / 4
            else calc_text_length_start
        )
    else:
        temp_text_length = (
            calc_text_length_start * (width * 3 / 4) / temp_text_width
            if temp_text_width > width * 3 / 4
            else calc_text_length_start
        )
    calc_text_length = min(temp_text_length, calc_text_length_start)

    if options.angle is not None:
        angle = options.angle
    elif options.label_type == LabelType.FRAMELESS_ANGLE:
        angle = (90 - cross_angle) if length > width else cross_angle
    else:
        angle = 90 if length > width else 0

    text_size = metrics["size"][1] / metrics["size"][0] * calc_text_length * options.text_scale
    pos = [
        width / 2 + math.sin(math.radians(angle)) * metrics["descent"] / 2 + options.label_diff[0],
        length / 2 + math.cos(math.radians(angle)) * metrics["descent"] / 2 + options.label_diff[1],
        0,
    ]

    calc_label_background_colour = options.label_background_colour
    if calc_label_background_colour is None:
        calc_label_background_colour = default_label_background_colour
    calc_label_colour = options.label_colour
    if calc_label_colour is None:
        calc_label_colour = default_label_colour

    bg_text = (
        shapes2d.text(label, font=options.font, halign="center", valign="center")
        .resize([calc_text_length, text_size, 0])
        .rotate([0, 0, angle])
        .linear_extrude(lid_thickness - default_slicing_layer_height)
        .color(calc_label_background_colour)
        .translate(pos)
    )

    fg_text = (
        shapes2d.text(label, font=options.font, halign="center", valign="center")
        .resize([calc_text_length, text_size, 0])
        .rotate([0, 0, angle])
        .linear_extrude(default_slicing_layer_height + 0.01)
        .color(calc_label_colour)
        .translate([pos[0], pos[1], lid_thickness - default_slicing_layer_height])
    )

    return bg_text | fg_text
