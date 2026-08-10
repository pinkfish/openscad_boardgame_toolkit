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

# LibFile: flags.py
#    This file has all the modules needed to make some fun flags.

from __future__ import annotations
from base_bgtk import (
    BACK,
    BOTTOM,
    FRONT,
    LEFT,
    RIGHT,
    TOP,
    Color,
    default_material_colour,
    default_slicing_layer_height,
    union_all_2d,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from pybosl2 import shapes2d
_SVG_DIR = __import__("pathlib").Path(__file__).resolve().parent / "svg"
from pybosl2.svg import svg_outlines
from pybosl2 import shapes3d
from pybosl2.shapes3d import Bosl2Solid
from labels import Make3dStripedGrid


# portugal_castle is imported lazily below since shapes is a large sibling
# module converted separately.


def FlagBackgroundAndBorder(
    length: float,
    height: float,
    background_color: Color,
    width: float | None = None,
    background: bool = True,
    border: float = 0,
    solid_background: bool = False,
    grid_spacing: float = 1.5,
    children: list | None = None,
) -> PyOpenSCAD:
    """Makes a background to the flag with the specified border.

    The first entry of ``children`` is used to subtract from the background while the
    second entry renders the inside of the flag.

    Usage::

        FlagBackgroundAndBorder(100, 4, "blue", children=[cutout, inside])

    Args:
        length: length of the background
        height: height of the background
        background_color: color of the background
        width: width of background (default length/2)
        background: generate the background (default True)
        border: size of border to generate (default 0)
        solid_background: generate a solid background for MMU (default False)
        grid_spacing: spacing for the striped grid (default 1.5)
        children: [cutout, inside] pair of shapes
    """
    calc_width = width
    assert children is not None and len(children) >= 2, (
        "FlagBackgroundAndBorder(): children[0] (cutout) and children[1] (face) are required"
    )
    if calc_width is None:
        calc_width = length / 2
    shape = None
    if border > 0:
        piece = shapes3d.cuboid([length + border, calc_width + border, height], anchor=BOTTOM) - shapes3d.cuboid(
            [length - 0.02, calc_width - 0.02, height + 1], anchor=BOTTOM
        ).translate([0, 0, -0.5])
        shape = piece.color(default_material_colour)
    if background:
        if solid_background:
            base = shapes3d.cuboid([length, calc_width, height], anchor=BOTTOM)
        else:
            base = shapes3d.cuboid([length, calc_width, height], anchor=BOTTOM) & Make3dStripedGrid(
                size=[length, calc_width], height=height, spacing=grid_spacing
            ).translate([-length * 5.5 / 4, -calc_width / 2, 0])
        piece = (base - children[0].translate([0, 0, -0.5])).color(background_color)
        shape = piece if shape is None else shape | piece
    piece = children[1]
    return piece if shape is None else shape | piece


def StAndrewsCross(length: float, height: float) -> "Bosl2Solid":
    """Flag of the St Andrews Cross to use for anything.

    Usage::

        StAndrewsCross(100, 4)

    Args:
        length: length of the flag
        height: height of the cross
    """
    a = shapes3d.cuboid([length * 2, length / 2 / 5, height], anchor=BOTTOM).rotate([0, 0, 22.5]).color(Color("white"))
    b = shapes3d.cuboid([length * 2, length / 2 / 5, height], anchor=BOTTOM).rotate([0, 0, -22.5]).color(Color("white"))
    return (a | b)


def StPatricksCross(length: float, height: float) -> "Bosl2Solid":
    """Flag of the St Patricks Cross to use for anything.

    Usage::

        StPatricksCross(100, 5)

    Args:
        length: length of the flag
        height: height of the cross
    """
    a = (
        shapes3d.cuboid([length * 2, length / 2 / 15, height], anchor=BOTTOM + FRONT + LEFT)
        .rotate([0, 0, 22.5])
        .color(Color("red"))
    )
    b = (
        shapes3d.cuboid([length * 2, length / 2 / 15, height], anchor=BOTTOM + FRONT + RIGHT)
        .rotate([0, 0, -22.5])
        .color(Color("red"))
    )
    c = (
        shapes3d.cuboid([length * 2, length / 2 / 15, height], anchor=BOTTOM + BACK + RIGHT)
        .rotate([0, 0, 22.5])
        .color(Color("red"))
    )
    d = (
        shapes3d.cuboid([length * 2, length / 2 / 15, height], anchor=BOTTOM + BACK + LEFT)
        .rotate([0, 0, -22.5])
        .color(Color("red"))
    )
    return (a | b | c | d)


def StGeorgesCross(length: float, white_height: float, red_height: float) -> PyOpenSCAD:
    """Flag of the St Georges Cross to use for anything.

    Usage::

        StGeorgesCross(100, 5, 4)

    Args:
        length: length of the flag
        white_height: height of the white parts
        red_height: height of the red parts
    """

    def RedBit(height: float) -> "Bosl2Solid":
        a = shapes3d.cuboid([length, length / 15, height], anchor=BOTTOM)
        b = shapes3d.cuboid([length, length / 15, height], anchor=BOTTOM).rotate([0, 0, 90])
        return (a | b)

    fimbration = length / 15 / 2
    white = shapes3d.cuboid([length, length / 15 + fimbration, white_height], anchor=BOTTOM).color(
        Color("white")
    ) | shapes3d.cuboid([length, length / 15 + fimbration, white_height], anchor=BOTTOM).rotate([0, 0, 90]).color(
        Color("white")
    )
    shape = white - RedBit(white_height + 1)
    return shape | RedBit(red_height).color("red")


def UnionJack(
    length: float, white_height: float, red_height: float, background: bool = True, border: float = 0
) -> PyOpenSCAD:
    """Flag of Great Britan to use for anything.

    Usage::

        UnionJack(100, 5, 4)
        UnionJack(100, 5, 4, border=1)
        UnionJack(100, 5, 4, background=False)

    Args:
        length: length of the flag
        white_height: height of the white parts
        red_height: height of the red parts
        background: put in a blue background with stripes (default True)
        border: border to put on the flag (this goes outside the length) (default 0)
    """
    shape = None
    if border > 0:
        shape = shapes3d.cuboid(
            [length + border, length / 2 + border, max(white_height, red_height)], anchor=BOTTOM
        ) - shapes3d.cuboid(
            [length - 0.02, length / 2 - 0.02, max(white_height, red_height) + 1], anchor=BOTTOM
        ).translate([0, 0, -0.5])

    pieces = None
    if background:
        bg = (
            Make3dStripedGrid(size=[length, length], height=max(red_height, white_height), spacing=1.5)
            .translate([-length * 5 / 4, -length / 4, 0])
            .color("blue")
            - StGeorgesCross(length, white_height + 1, white_height + 1).translate([0, 0, -0.5])
            - StPatricksCross(length, white_height + 1).translate([0, 0, -0.5])
        )
        pieces = bg

    andrews = StAndrewsCross(length, white_height) - StPatricksCross(length, white_height + 1).translate([0, 0, -0.5])
    andrews = andrews | StPatricksCross(length, red_height)
    andrews = andrews - StGeorgesCross(length, white_height + 1, white_height + 1).translate([0, 0, -0.5])

    union_all = andrews | StGeorgesCross(length=length, white_height=white_height, red_height=red_height)
    union_all = union_all if pieces is None else pieces | union_all

    bound = shapes3d.cuboid([length, length / 2, max(white_height, red_height) + 1], anchor=BOTTOM).translate(
        [0, 0, -0.5]
    )
    piece = bound & union_all
    return piece if shape is None else shape | piece


def AustralianFlag(
    length: float,
    white_height: float,
    red_height: float,
    blue_height: float,
    border: float = 0,
    background: bool = True,
    solid_background: bool = False,
) -> PyOpenSCAD:
    """Flag of Australia to use for anything.

    Usage::

        AustralianFlag(100, 5, 4, 1)
        AustralianFlag(100, 5, 4, 1, border=1)
        AustralianFlag(100, 5, 4, 1, background=False)
        AustralianFlag(100, 5, 4, 1, border=1, solid_background=True)

    Args:
        length: length of the flag
        white_height: height of the white parts
        red_height: height of the red parts
        blue_height: height of the blue parts
        border: border to put on the flag (this goes outside the length) (default 0)
        background: put in a blue background with stripes (default True)
        solid_background: generate the flag for an mmu, solid background (default False)
    """

    def Star5(d: float) -> PyOpenSCAD:
        return shapes2d.star(tips=5, radius=d / 2, inner_radius=d * 4 / 9 / 2)

    def Star7(d: float) -> PyOpenSCAD:
        return shapes2d.star(tips=7, radius=d / 2, inner_radius=d * 4 / 9 / 2).rotate([0, 0, 180 / 14 + 180])

    flag_len = 450
    flag_width = 225

    shape = None
    if border > 0:
        shape = (
            shapes3d.cuboid([length + border, length / 2 + border, max(white_height, red_height)], anchor=BOTTOM)
            - shapes3d.cuboid(
                [length - 0.02, length / 2 - 0.02, max(white_height, red_height) + 1], anchor=BOTTOM
            ).translate([0, 0, -0.5])
        ).color(default_material_colour)

    bg_union = None
    if background:
        if solid_background:
            blue_base = shapes3d.cuboid([length, length / 2, blue_height], anchor=BOTTOM).translate(
                [length / 2, length / 4, 0]
            )
        else:
            blue_base = Make3dStripedGrid(size=[length, length / 2], height=blue_height, spacing=1.5).translate(
                [-length / 4, 0, 0]
            )
        blue_bound = shapes3d.cuboid(
            [length / 2 - 0.01, length / 4 - 0.01, max(white_height, red_height) + 1], anchor=BOTTOM + BACK + LEFT
        ).translate([0, length / 2, -0.5])
        union_jack = UnionJack(
            length=length / 2,
            white_height=max(white_height, red_height) + 1,
            red_height=max(white_height, red_height) + 1,
            background=False,
        ).translate([length / 4, length * 3 / 8, 0])
        bg_union = (blue_base - (blue_bound & union_jack)).color("blue")

    stars = None
    # Alpha Crucis - 7-pointed star, straight below centre fly 1/6 up from bottom edge.
    stars = (
        Star7(length / 14)
        .linear_extrude(height=white_height)
        .translate([length * 3 / 4, length / 12, 0])
        .color("white")
    )
    # Beta Crucis - 7-pointed star, 1/4 of the way left and 1/16 up from the centre fly.
    stars = stars | Star7(length / 14).linear_extrude(height=white_height).translate(
        [length * 5 / 8, length / 2 * 9 / 16, 0]
    ).color("white")
    # Gamma Crucis - 7-pointed star, straight above centre fly 1/6 down from top edge.
    stars = stars | Star7(length / 14).linear_extrude(height=white_height).translate(
        [length * 3 / 4, length / 2 * 5 / 6, 0]
    ).color("white")
    # Delta Crucis - 7-pointed star, 2/9 of the way right and 31/240 up from the centre fly.
    stars = stars | Star7(length / 14).linear_extrude(height=white_height).translate(
        [length * 31 / 36, length / 2 * 151 / 240, 0]
    ).color("white")
    # Epsilon Crucis - 5-pointed star, 1/10 of the way right and 1/24 down from the centre fly.
    stars = stars | Star7(length / 24).linear_extrude(height=white_height).translate(
        [length * 4 / 5, length / 2 * 11 / 24, 0]
    ).color("white")
    # Commonwealth star
    stars = stars | Star5(length * 3 / 20).linear_extrude(height=white_height).translate(
        [length / 4, length / 8, 0]
    ).color("white")

    stars = stars | UnionJack(
        length=length / 2, white_height=white_height, red_height=red_height, background=False
    ).translate([length / 4, length * 3 / 8, 0])

    union_all = stars if bg_union is None else bg_union | stars
    # cuboid(anchor=BOTTOM+FRONT+LEFT) is the pybosl2 spelling of native cube()'s
    # corner-at-origin box. It has to be a wrapper: the native & below would get a
    # wrapper on the right and raise 'invalid argument left to operator'.
    bound = shapes3d.cuboid([450, 225, 30], anchor=BOTTOM + FRONT + LEFT).scale(
        [length / flag_len, length / flag_len, 1]
    )
    piece = (bound & union_all).translate([-length / 2, -length / 4, 0])
    return piece if shape is None else shape | piece


def SwedenFlag(
    length: float,
    height: float,
    background: bool = True,
    border: float = 0,
    solid_background: bool = False,
    layer_thickness: float = default_slicing_layer_height,
) -> PyOpenSCAD:
    """Flag of Sweden to use for anything.

    Usage::

        SwedenFlag(100, 4)
        SwedenFlag(100, 4, border=1)
        SwedenFlag(100, 4, background=False)

    Args:
        length: length of the flag
        height: height of the flag
        background: put in a blue background with stripes (default True)
        border: border to put on the flag (this goes outside the length) (default 0)
        solid_background: generate a solid background for MMU (default 0)
        layer_thickness: thickness of layers for MMU (default default_slicing_layer_height)
    """
    width = length * 5 / 8
    line_horiz = width * 2 / 10
    line_vert = length * 2 / 16

    def CrossBit(height: float) -> "Bosl2Solid":
        a = shapes3d.cuboid([length, line_horiz, height], anchor=TOP)
        b = shapes3d.cuboid([line_vert, width, height], anchor=TOP).translate([-length * 3 / 16, 0, 0])
        return a | b

    background_height = height - layer_thickness * 2 if solid_background else height * 3 / 4
    cross_height = layer_thickness if solid_background else height
    cross1 = CrossBit(cross_height).translate([0, 0, height]).color(Color("yellow"))
    cross2 = CrossBit(cross_height).translate([0, 0, height]).color(Color("yellow"))
    shape = FlagBackgroundAndBorder(
        length,
        background_height,
        width=width,
        background_color=default_material_colour if solid_background else "blue",
        background=background,
        border=border,
        solid_background=solid_background,
        children=[cross1, cross2],
    )
    if solid_background:
        shape = shape | shapes3d.cuboid([length, width, layer_thickness], anchor=BOTTOM).translate(
            [0, 0, height - layer_thickness * 2]
        ).color(Color("blue"))
    return shape


def UnitedStatesFlag(
    length: float,
    white_height: float,
    red_height: float,
    blue_height: float,
    background: bool = True,
    border: float = 0,
    solid_background: bool = False,
    layer_thickness: float = default_slicing_layer_height,
) -> PyOpenSCAD:
    """Flag of the united states to use for anything.

    Usage::

        UnitedStatesFlag(100, 4, 2, 1)
        UnitedStatesFlag(100, 4, 2, 1, border=1)
        UnitedStatesFlag(100, 4, 2, 1, background=False)

    Args:
        length: length of the flag
        white_height: height of the white parts
        red_height: height of the red parts
        blue_height: height of the blue parts
        background: put in a blue background with stripes (default True)
        border: border to put on the flag (this goes outside the length) (default 0)
        solid_background: a solid background (setup for mmu)
        layer_thickness: thickness of layers for MMU (default default_slicing_layer_height)
    """
    width = length / 1.9
    top_bit_width = width * 7 / 13
    top_bit_length = length * 2 / 5
    star_offset_width = top_bit_length / 10
    star_offset_length = top_bit_width / 5.5
    stripe = width / 13
    star_size = stripe * 4 / 5
    background_material_thickness = min(red_height, white_height) - layer_thickness
    background_stars_material_thickness = blue_height - layer_thickness if solid_background else blue_height

    def Stars() -> PyOpenSCAD:
        shape = None
        for i in range(5):
            for j in range(10):
                x = (
                    -top_bit_width / 2
                    + star_offset_length / 2
                    + star_offset_length * i
                    + (star_offset_length / 2 if j % 2 == 1 else 0)
                )
                y = -top_bit_length / 2 + star_offset_width / 2 + star_offset_width * j
                # `or` is a Python keyword and can't be passed as a kwarg name; BOSL2's
                piece = (
                    shapes2d.star(5, radius=star_size / 2, inner_radius=star_size / 4, spin=180 / 5)
                    .linear_extrude(height=white_height - blue_height)
                    .translate([x, y, blue_height])
                    .color("white")
                )
                shape = piece if shape is None else shape | piece
        assert shape is not None
        return shape

    def StarSection(white_height: float) -> "Bosl2Solid":
        section = FlagBackgroundAndBorder(
            length=top_bit_width,
            height=background_stars_material_thickness,
            background_color=default_material_colour if solid_background else "blue",
            width=top_bit_length,
            background=background,
            border=0,
            grid_spacing=min(star_offset_width / 4, star_offset_length / 4),
            solid_background=solid_background,
            children=[Stars(), Stars()],
        )
        if solid_background:
            section = section | shapes3d.cuboid(
                [top_bit_width, top_bit_length, layer_thickness], anchor=BOTTOM
            ).translate([0, 0, background_stars_material_thickness]).color(Color("blue"))
        return section

    def Stripes(white_height: float, red_height: float) -> PyOpenSCAD:
        base = shapes3d.cuboid([width, length, background_material_thickness], anchor=BOTTOM + LEFT).color(
            default_material_colour
        )
        stripes = None
        for i in range(6):
            red = (
                shapes3d.cuboid([stripe, length, red_height - background_material_thickness], anchor=BOTTOM + LEFT)
                .translate([stripe * 2 * i, 0, background_material_thickness])
                .color(Color("red"))
            )
            white = (
                shapes3d.cuboid([stripe, length, white_height - background_material_thickness], anchor=BOTTOM + LEFT)
                .translate([stripe * 2 * i + stripe, 0, background_material_thickness])
                .color(Color("white"))
            )
            stripes = red | white if stripes is None else stripes | red | white
        stripes = stripes | shapes3d.cuboid(
            [stripe, length, red_height - background_material_thickness], anchor=BOTTOM + LEFT
        ).translate([stripe * 2 * 6, 0, background_material_thickness]).color(Color("red"))
        whole = base | stripes
        cutout = shapes3d.cuboid(
            [top_bit_width + 0.01, top_bit_length + 0.01, max(white_height, red_height) + 2], anchor=BOTTOM + LEFT
        ).translate([-width / 2 + stripe * 6.5, -length / 2 + top_bit_length / 2, -1])
        return (whole - cutout)

    def MainFlag(white_height: float, red_height: float) -> PyOpenSCAD:
        a = Stripes(white_height=white_height, red_height=red_height).translate([-width / 2, 0, 0])
        b = StarSection(white_height=white_height).translate(
            [-width / 2 + top_bit_width / 2, -length / 2 + top_bit_length / 2, 0]
        )
        return a | b

    shape = MainFlag(white_height=white_height, red_height=red_height)
    if border > 0:
        shape = shape | (
            shapes3d.cuboid([width + border, length + border, max(white_height, red_height)], anchor=BOTTOM)
            - shapes3d.cuboid(
                [width - 0.02, length - 0.02, max(white_height, red_height) + 1], anchor=BOTTOM
            ).translate([0, 0, -0.5])
        ).color(default_material_colour)
    return shape


def PortugeseFlag(length: float, height: float, background: bool = True, border: float = 0) -> PyOpenSCAD:
    """Flag of Portugal to use for anything.

    Usage::

        PortugeseFlag(100, 5)

    Args:
        length: length of the flag
        height: height of the flag
        background: put in a green/red background with stripes (default True)
        border: border to put on the flag (this goes outside the length) (default 0)
    """
    from shapes import portugal_castle

    width = length * 2 / 3

    def Quina(width: float, height: float) -> "Bosl2Solid":
        """One quina -- the small shields on the Portuguese flag's escutcheon.

        The outline lives in svg/portugal_quina.svg, generated from this function's own
        Bezier(...).path_curve() output (129 points, max deviation 5e-7), so it is the same
        curve rather than a re-trace. The magic numbers below are the drawing's own extents,
        kept because the resize/translate still places it from them.
        """
        calc_len = 247.6548 - 232.636
        calc_width = 236.2621 - 217.4357
        mult = width / calc_width
        # svg_outlines, not Region.from_svg: a single ring with no nesting to resolve.
        (ring,) = svg_outlines(str(_SVG_DIR / "portugal_quina.svg"))
        return (
            shapes2d.polygon(ring)
            .resize([calc_len * mult, width, 0])
            .translate([-232.636 - calc_len / 2, -236.2621 + calc_width / 2])
            .linear_extrude(height=height)
        )

    def MiddleScrollsYellow(height: float, width: float) -> "Bosl2Solid":
        """The yellow scroll-work behind the shield, loaded from its traced SVG."""
        len_min = 139.67299999999997
        len_max = 340.11996
        width_min = 99.546
        width_max = 300.796
        calc_len = len_max - len_min
        calc_width = width_max - width_min
        mult = width / calc_width

        # svg_outlines + union, NOT Region.from_svg: from_svg resolves nesting with the
        # even-odd rule, and one of these rings sits inside another. Even-odd would punch it
        # out as a hole; the artwork means it to be absorbed, which is what a union does.
        shape = union_all_2d(
            [shapes2d.polygon(ring) for ring in svg_outlines(str(_SVG_DIR / "portugal_scrolls_yellow.svg"))]
        )
        assert shape is not None
        return (
            shape.resize([mult * calc_len, width, 0])
            .translate([-len_max + (len_max - len_min) / 2, -width_max + (width_max - width_min) / 2])
            .linear_extrude(height=height)
            .color(Color("yellow"))
        )

    def MiddleScrollsBlack(height: float, width: float) -> "Bosl2Solid":
        """The black scroll-work outline, loaded from its traced SVG."""
        len_min = 139.67299999999997
        len_max = 340.11996
        width_min = 99.546
        width_max = 300.796
        calc_len = len_max - len_min
        calc_width = width_max - width_min
        mult = width / calc_width

        # See MiddleScrollsYellow: these outlines are UNIONED, not even-odd.
        shape = union_all_2d(
            [shapes2d.polygon(ring) for ring in svg_outlines(str(_SVG_DIR / "portugal_scrolls_black.svg"))]
        )
        assert shape is not None
        return (
            shape.resize([mult * calc_len, width, 0])
            .translate([-len_max + (len_max - len_min) / 2, -width_max + (width_max - width_min) / 2])
            .linear_extrude(height=height)
            .color(Color("black"))
        )

    def MiddleScrolls(height: float, width: float) -> PyOpenSCAD:
        yellow_minus_black = MiddleScrollsYellow(height=height, width=width) - MiddleScrollsBlack(
            height=height, width=width
        )
        shape = yellow_minus_black | MiddleScrollsBlack(height=height, width=width)
        return shape.mirror([0, 1, 0])

    def WhiteDots(length: float, height: float) -> "Bosl2Solid":
        a = shapes3d.cyl(diameter=length / 5, height=height, anchor=BOTTOM)
        b = shapes3d.cyl(diameter=length / 5, height=height, anchor=BOTTOM).translate([length / 2, length / 2, 0])
        c = shapes3d.cyl(diameter=length / 5, height=height, anchor=BOTTOM).translate([-length / 2, length / 2, 0])
        d = shapes3d.cyl(diameter=length / 5, height=height, anchor=BOTTOM).translate([length / 2, -length / 2, 0])
        e = shapes3d.cyl(diameter=length / 5, height=height, anchor=BOTTOM).translate([-length / 2, -length / 2, 0])
        return (a | b | c | d | e)

    def BlueDotsShield(width: float, height: float, white_dot_height: float) -> PyOpenSCAD:
        width_shield = width
        length_shield = width * 7 / 6
        blue = (
            Quina(width=width_shield, height=height) - WhiteDots(width_shield / 2, height + 1).translate([0, 0, -0.5])
        ).color("#003399")
        white = WhiteDots(width_shield / 2, white_dot_height).color("white")
        return (blue | white).translate([0, -(length_shield - width_shield) / 2, 0])

    def AllBlueShields(length: float, height: float, white_dot_height: float) -> "Bosl2Solid":
        outer_shield = length / 10
        inner_layout = outer_shield * 5 / 8
        shield_width = length / 40
        a = BlueDotsShield(shield_width, height, white_dot_height)
        b = BlueDotsShield(shield_width, height, white_dot_height).translate([inner_layout / 2, 0, 0])
        c = BlueDotsShield(shield_width, height, white_dot_height).translate([-inner_layout / 2, 0, 0])
        d = BlueDotsShield(shield_width, height, white_dot_height).translate([0, inner_layout / 2, 0])
        e = BlueDotsShield(shield_width, height, white_dot_height).translate([0, -inner_layout / 2, 0])
        return (a | b | c | d | e)

    shape = None
    if border > 0:
        shape = shapes3d.cuboid([length + border, width + border, height], anchor=BOTTOM) - shapes3d.cuboid(
            [length - 0.02, width - 0.02, height + 1], anchor=BOTTOM
        ).translate([0, 0, -0.5])

    bg = None
    if background:
        green = (
            (
                shapes3d.cuboid([length * 2 / 5, width, height], anchor=BOTTOM + LEFT)
                & Make3dStripedGrid(size=[length, width], height=height, spacing=1.5)
                .mirror([0, 1, 0])
                .translate([-length / 2, width / 2, 0])
            ).translate([-length / 2, 0, 0])
        ).color("#006600")
        red = (
            (
                shapes3d.cuboid([length * 3 / 5, width, height], anchor=BOTTOM + LEFT)
                & Make3dStripedGrid(size=[length, width], height=height, spacing=1.5).translate(
                    [-length / 2 - 1, -width / 2, 0]
                )
            ).translate([-length / 10, 0, 0])
        ).color("#FF0000")
        bg = green | red

    coin = (
        shapes3d.cyl(diameter=width / 2, height=height, anchor=BOTTOM)
        - shapes3d.cyl(diameter=width / 2 - width / 12, height=height + 1, anchor=BOTTOM).translate([0, 0, -0.5])
    ).color(Color("#FFFF00"))
    scrolls = MiddleScrolls(height=height, width=width / 2 + width / 150) - Quina(length / 5, height).translate(
        [0, 0, -0.5]
    )
    white_quina = (Quina(length / 5, height) - Quina(length / 5 * 19 / 20, height).translate([0, 0, -0.5])).color(
        "white"
    )
    red_quina = (Quina(length / 5 * 19 / 20, height) - Quina(length / 5 * 4 / 7, height).translate([0, 0, -0.5])).color(
        "#FF0000"
    )
    white_shields = (
        Quina(length / 5 * 4 / 7, height) - AllBlueShields(length, height + 1, height + 4).translate([0, 0, -0.5])
    ).color("white")
    blue_shields = AllBlueShields(length, height, height)

    medallion = coin | scrolls | white_quina | red_quina | white_shields | blue_shields
    medallion = medallion.translate([length * 2 / 5 - length / 2, 0, 0])

    pieces = medallion if bg is None else bg | medallion
    return pieces if shape is None else shape | pieces
