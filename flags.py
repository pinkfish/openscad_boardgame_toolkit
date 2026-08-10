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
_FLAG_SVG_DIR = _SVG_DIR / "flags"
from pybosl2 import Region
from pybosl2 import shapes3d
from pybosl2.shapes3d import Bosl2Solid
from labels import Make3dStripedGrid


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


# ---------------------------------------------------------------------------
# Flags, from their drawings
# ---------------------------------------------------------------------------
#
# Every flag below is its real drawing, loaded from svg/flags/ -- see the README there. They
# used to be built by hand out of stroked beziers and composed crosses, which is why this file
# was 1464 lines and why the Portuguese one alone carried ~800 lines of traced coordinates.
#
# Region.from_svg resolves a drawing's colours into DISJOINT regions in SVG paint order, so a
# flag comes out as one multi-colour solid with no overlapping colour bodies -- which is what
# MMU needs. Region.geometry() then colours each region individually.

#: The flag-icons drawing (svg/flags/<code>.svg) behind each flag.
_FLAG_CODES = {
    "australia": "au",
    "portugal": "pt",
    "sweden": "se",
    "united_states": "us",
    "union_jack": "gb",
    "st_georges_cross": "gb-eng",
    "st_andrews_cross": "gb-sct",
    "st_patricks_cross": "st-patrick",
}

#: flag-icons' 4x3 drawings all declare viewBox="0 0 640 480".
_FLAG_VIEWBOX = (640.0, 480.0)


def flag_aspect_height(length: float) -> float:
    """The height a flag of *length* has at the drawings' 4:3 aspect."""
    view_w, view_h = _FLAG_VIEWBOX
    return length * view_h / view_w


def flag_from_svg(
    code: str,
    length: float,
    height: float | None = None,
    thickness: float = 2,
    border: float = 0,
) -> "Bosl2Solid":
    """Build a flag from its drawing in ``svg/flags/``.

    The one place a flag becomes geometry. Every named flag below is a call to this.

    Usage::

        flag_from_svg("au", 60)
        flag_from_svg("pt", 60, thickness=3, border=2)

    Args:
        code: the drawing's basename in ``svg/flags/`` (an ISO code for the flag-icons ones)
        length: length of the flag
        height: height of the flag (default: the drawing's own 4:3 aspect)
        thickness: how thick to extrude it
        border: if > 0, put a frame of this width around the flag

    Returns:
        One multi-colour solid, corner at the origin, extending +x/+y and 0..*thickness* in z.
    """
    assert length > 0, f"length must be > 0, got {length}"
    assert thickness > 0, f"thickness must be > 0, got {thickness}"
    view_w, view_h = _FLAG_VIEWBOX
    calc_height = flag_aspect_height(length) if height is None else height

    shape = Region.from_svg(str(_FLAG_SVG_DIR / f"{code}.svg")).geometry()
    # Some drawings overhang their viewBox -- Scotland's saltire by 6%, the US flag by 2%.
    # A renderer clips that; without clipping, the resize below shrinks the whole flag to fit
    # the overhang inside the requested size.
    shape = shape & shapes2d.rect([view_w, view_h]).translate([view_w / 2, -view_h / 2])

    flag = (
        shape.resize([length, calc_height, 0])
        .linear_extrude(height=thickness)
        .translate([0, calc_height, 0])
    )
    if border > 0:
        frame = shapes3d.cuboid(
            [length + border * 2, calc_height + border * 2, thickness], anchor=BOTTOM + FRONT + LEFT
        ) - shapes3d.cuboid(
            [length, calc_height, thickness + 1], anchor=BOTTOM + FRONT + LEFT
        ).translate([border, border, -0.5])
        flag = flag.translate([border, border, 0]) | frame.color(default_material_colour)
    return flag


def StAndrewsCross(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Scotland -- the white saltire of St Andrew on blue.

    Usage::

        StAndrewsCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_andrews_cross"], length, height, thickness, border)


def StPatricksCross(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """St Patrick's Saltire -- the red saltire on white.

    Usage::

        StPatricksCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_patricks_cross"], length, height, thickness, border)


def StGeorgesCross(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of England -- the red cross of St George on white.

    Usage::

        StGeorgesCross(60)
    """
    return flag_from_svg(_FLAG_CODES["st_georges_cross"], length, height, thickness, border)


def UnionJack(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of the United Kingdom.

    Usage::

        UnionJack(60)
        UnionJack(60, border=2)
    """
    return flag_from_svg(_FLAG_CODES["union_jack"], length, height, thickness, border)


def AustralianFlag(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Australia.

    Usage::

        AustralianFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["australia"], length, height, thickness, border)


def SwedenFlag(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Sweden.

    Usage::

        SwedenFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["sweden"], length, height, thickness, border)


def UnitedStatesFlag(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of the United States.

    Usage::

        UnitedStatesFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["united_states"], length, height, thickness, border)


def PortugeseFlag(length: float, height: float | None = None, thickness: float = 2, border: float = 0):
    """Flag of Portugal.

    Usage::

        PortugeseFlag(60)
    """
    return flag_from_svg(_FLAG_CODES["portugal"], length, height, thickness, border)
