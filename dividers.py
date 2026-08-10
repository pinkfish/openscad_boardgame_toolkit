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

# LibFile: dividers.py
#    Modules for generating card and component dividers.
#
# FileSummary: Divider pieces for the dividers.
# FileGroup: Dividers

from __future__ import annotations
from base_bgtk import BACK, BOTTOM, FRONT, LEFT, RIGHT, default_label_font
from pythonscad import text
import pybosl2.shapes3d
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401

# ---------------------------------------------------------------------------
# Section: Dividers
# ---------------------------------------------------------------------------


def MakeDividerTab(
    tab_height: float, tab_length: float, thickness: float, tab_radius: float = 2, children: PyOpenSCAD | None = None
) -> "Bosl2Solid":
    """Makes a single divider tab with nice curved transitions.

    Any *children* solid is differenced out of the tab (e.g., an SVG icon).

    Usage::

        MakeDividerTab(10, 20, 1)

    Args:
        tab_height:  height of the tab
        tab_length:  length of the tab
        thickness:   thickness (z-height) of the tab
        tab_radius:  corner curve radius (default 2)
        children:    optional solid to subtract from the tab
    """
    top = pybosl2.shapes3d.cuboid(
        [tab_length, tab_height, thickness],
        rounding=tab_radius,
        edges=[FRONT + LEFT, FRONT + RIGHT],
        anchor=BACK + LEFT + BOTTOM,
    )
    base = pybosl2.shapes3d.cuboid([tab_length + tab_radius * 2, tab_radius, thickness], anchor=BACK + LEFT + BOTTOM)
    cut_a = pybosl2.shapes3d.cyl(radius=tab_radius, height=thickness + 1).translate([0, -tab_radius, 0.5])
    cut_b = pybosl2.shapes3d.cyl(radius=tab_radius, height=thickness + 1).translate([tab_length + tab_radius * 2, -tab_radius, 0.5])
    base_shape = (base - cut_a - cut_b).translate([-tab_radius, 0, 0])

    tab = (top | base_shape).translate([0, tab_height, 0])
    if children is not None:
        tab = tab - children
    return tab


def MakeDivider(
    size: list[float],
    tab_height: float,
    num_tabs: int,
    tab_position: int,
    tab_radius: float = 2,
    tab_length: float | None = None,
    hole_offset: float = 6,
    children: list[PyOpenSCAD] | None = None,
) -> "Bosl2Solid":
    """Makes a divider card with a tab at the top.

    Usage::

        MakeDivider(size=[40, 70, 1], tab_height=10, num_tabs=3, tab_position=0, tab_radius=2)

    Args:
        size:         [width, length, thickness] of the divider
        tab_height:   height of the tab
        num_tabs:     total number of tab positions across the width
        tab_position: which tab slot to use (0-indexed, 0..num_tabs-1)
        tab_radius:   corner curve radius (default 2)
        tab_length:   explicit tab length (default auto-calculated)
        hole_offset:  offset for the lightening holes (default 6)
        children:     list of up to 6 optional child solids:
                      children[0] -> differenced from the tab
                      children[1:] -> differenced from the body
    """
    assert isinstance(size, (list, tuple)) and len(size) == 3, f"Must specify size as [x, y, z], got {size}"
    width, length, thickness = size
    assert width > 0, f"Width must be > 0, width={width}"
    assert length > 0, f"Length must be > 0, length={length}"
    assert thickness > 0, f"Thickness must be > 0, thickness={thickness}"
    assert num_tabs > 0, f"num_tabs must be > 0, num_tabs={num_tabs}"
    assert 0 <= tab_position < num_tabs, "tab_position must be < num_tabs"

    tab_length_calc = tab_length if tab_length is not None else (width - tab_radius * num_tabs) / num_tabs
    spacing = (width - tab_length_calc) / (num_tabs - 1) if num_tabs > 1 else 0
    assert tab_length_calc > 0, "tab_length_calc must be > 0"
    hole_width = (width - 4 * hole_offset) / 3 if width > 40 else (width - 3 * hole_offset) / 2
    hole_height = length - tab_height - hole_offset * 2
    num_holes = 3 if width > 40 else 2

    kids = list(children) if children else []

    tab = MakeDividerTab(
        tab_height=tab_height,
        tab_length=tab_length_calc,
        thickness=thickness,
        tab_radius=tab_radius,
        children=kids[0] if len(kids) >= 1 else None,
    ).translate([spacing * tab_position, 0, 0])

    body = pybosl2.shapes3d.cuboid([width, length, thickness], anchor=BOTTOM + FRONT + LEFT) - pybosl2.shapes3d.cuboid(
        [width + 1, tab_height + 1, thickness + 1], anchor=BOTTOM + FRONT + LEFT
    ).translate([-0.5, -1, -0.5])

    for i in range(num_holes):
        hole = pybosl2.shapes3d.cuboid(
            [hole_width, hole_height, thickness + 1],
            rounding=tab_radius,
            edges=[FRONT + LEFT, FRONT + RIGHT],
            anchor=BACK + LEFT + BOTTOM,
        ).translate([hole_offset + (hole_width + hole_offset) * i, length - hole_offset, -0.5])
        body = body - hole

    for extra in kids[1:]:
        body = body - extra

    # cuboid(anchor=BOTTOM+FRONT+LEFT) is the pybosl2 spelling of the native cube()'s
    # corner-at-origin box, so the whole chain stays on the wrapper API.
    clip = pybosl2.shapes3d.cuboid([width, length, thickness], anchor=BOTTOM + FRONT + LEFT)
    return (tab | body) & clip


def MakeDividerWithText(
    size: list[float],
    tab_height: float,
    text_str: str,
    num_tabs: int,
    tab_position: int,
    tab_radius: float = 2,
    tab_length: float | None = None,
    text_offset: float = 2,
    text_height: float | None = None,
    text_depth: float | None = None,
    font: str | None = None,
    children: list[PyOpenSCAD] | None = None,
) -> "Bosl2Solid":
    """Makes a divider with text printed in the tab.

    Usage::

        MakeDividerWithText(size=[40, 70, 1], tab_height=10, num_tabs=3,
                            tab_position=0, text_str="Frog")

    Args:
        size:         [width, length, thickness] of the divider
        tab_height:   height of the tab
        text_str:     text to display in the tab
        num_tabs:     total number of tab positions
        tab_position: which tab slot to use (0-indexed)
        tab_radius:   corner curve radius (default 2)
        tab_length:   explicit tab length (default auto-calculated)
        text_offset:  margin inside tab for text (default 2)
        text_height:  height of the text area (default tab_height - text_offset)
        text_depth:   depth to cut the text (default thickness + 1)
        font:         font to use (default default_label_font)
        children:     optional list of child solids (see MakeDivider for layout)
    """
    if font is None:
        font = default_label_font

    assert isinstance(size, (list, tuple)) and len(size) == 3, f"Must specify size as [x, y, z], got {size}"
    width, length, thickness = size
    assert width > 0, f"Width needs to be set {width}"
    assert length > 0, f"Length needs to be set {length}"
    assert thickness > 0, f"Thickness needs to be set {thickness}"
    assert num_tabs > 0, f"num_tabs needs to be set {num_tabs}"
    assert text_str is not None and isinstance(text_str, str), f"text_str must be a string, got {text_str}"
    assert 0 <= tab_position < num_tabs, "Tab position must be lower than num_tabs"

    tab_length_calc = tab_length if tab_length is not None else (width - tab_radius * num_tabs) / num_tabs
    text_width = tab_length_calc - text_offset * 2
    text_height_calc = text_height if text_height is not None else tab_height - text_offset
    text_depth_calc = text_depth if text_depth is not None else thickness + 1

    calc_font = font if font is not None else default_label_font
    # Native text() has no spin= (that was a pybosl2-ism in the port) -- rotate the shape
    # instead, which is what the working labels.py call sites do.
    text_cut = (
        text(text=str(text_str), font=calc_font, size=10, spacing=1, halign="right", valign="bottom")
        .rotate([0, 0, 180])
        .resize([text_width, text_height_calc, 0])
        .linear_extrude(height=text_depth_calc + 0.5)
        .translate([text_offset, tab_height - text_offset * 1 / 4, thickness - text_depth_calc])
    )

    kids = list(children) if children else []
    tab_child = (text_cut | kids[0]) if len(kids) >= 1 else text_cut
    new_children = [tab_child] + kids[1:6]

    return MakeDivider(
        size=size,
        tab_height=tab_height,
        tab_length=tab_length,
        num_tabs=num_tabs,
        tab_position=tab_position,
        tab_radius=tab_radius,
        children=new_children,
    )
