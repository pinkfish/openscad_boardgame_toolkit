/**
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
 */

// LibFile: dividers.scad
//    This file has all the modules needed to generate dividers.

// FileSummary: Divider pieces for the dividers.
// FileGroup: Dividers

// Includes:
//   include <boardgame_toolkit.scad>

assert(version_num() >= 20190500, "boardgame_toolkit requires OpenSCAD version 2019.05 or later.");

include <BOSL2/rounding.scad>
include <BOSL2/std.scad>
include <base_bgtk.scad>
// Section: Dividers
// Description:
//    Dividers for putting in between cards or other things where you want to divide up a set of items into
//    various groups.

// Module: MakeDividerTab()
// Description:
//   Makes a divider tab tab section with nice curves in and out of the tab.  Any children to this are
//   diffed out of the tab.
// Usage: MakeDividerTab(10, 20, 1);
// See also: MakeDivider(), MakeDividerWithText()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
// Example:
//   MakeDividerTab(10, 20, 1);
// Example:
//   // Divider tab with a svg image in it.
//   MakeDividerTab(10, 20, 1)  translate([ 6, 5, -2 ]) mirror([ 0, 1, 0 ])
//       linear_extrude(height = 4) offset(delta = 0.001) scale(0.04) import("svg/australia.svg");
module MakeDividerTab(tab_height, tab_length, thickness, tab_radius = 2)
{
    difference()
    {
        translate([ 0, tab_height, 0 ]) union()
        {
            cuboid([ tab_length, tab_height, thickness ], rounding = tab_radius,
                   edges = [ FRONT + LEFT, FRONT + RIGHT ], anchor = BACK + LEFT + BOTTOM, $fn = 20);
            translate([ -tab_radius, 0, 0 ]) difference()
            {
                cuboid([ tab_length + tab_radius * 2, tab_radius, thickness ], anchor = BACK + LEFT + BOTTOM);
                translate([ 0, -tab_radius, 0.5 ]) cyl(r = tab_radius, h = thickness + 1, $fn = 20);
                translate([ tab_length + tab_radius * 2, -tab_radius, 0.5 ])
                    cyl(r = tab_radius, h = thickness + 1, $fn = 20);
            }
        }
        children();
    }
}

// Module: MakeDivider()
// Description:
//   Makes a divider with a tab section up the top.  First child is a diff to the tab, the rest is a diff to
//   the main body of the tab.
// Usage: MakeDivider(10, 20, 1, 5, 3, 0);
// See also: MakeDividerTab(), MakeDividerWithText()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
//   num_tabs = number of tabs across the top
//   tab_position = the position number of the tab, 0..num_tabs-1
// Example:
//   MakeDivider(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 0, tab_radius
//   = 2);
// Example:
//   MakeDivider(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1, tab_radius
//   = 2);
// Example:
//   MakeDivider(width = 80, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1, tab_radius
//   = 2);
// Example:
//   // Divider with a svg image in it.
//   MakeDivider(70, 50, 1, tab_height = 5, tab_position = 0, num_tabs = 3)  translate([ 6, 5, -2 ]) mirror([ 0, 1,
//   0 ])
//       linear_extrude(height = 4) offset(delta = 0.001) scale(0.04) import("svg/australia.svg");
module MakeDivider(width, length, thickness, tab_height, num_tabs, tab_position, tab_radius = 2, num_tabs = 3,
                   tab_length = undef, hole_offset = 6)
{
    assert(tab_position >= 0 && tab_position < num_tabs, "Tab position must be lower than num_tabs");
    tab_length_calc = tab_length == undef ? (width - tab_radius * num_tabs) / num_tabs : tab_length;
    spacing = (width - tab_length_calc) / (num_tabs - 1);
    assert(tab_length_calc > 0, "tab_length_calc must be > 0");
    hole_width = width > 40 ? (width - 4 * hole_offset) / 3 : (width - 3 * hole_offset) / 2;
    hole_height = length - tab_height - hole_offset * 2;
    num_holes = width > 40 ? 3 : 2;
    intersection()
    {
        cube([ width, length, thickness ]);
        union()
        {
            translate([ spacing * tab_position, 0, 0 ])
            {
                MakeDividerTab(tab_height = tab_height, tab_length = tab_length_calc, thickness = thickness,
                               tab_radius = tab_radius) if ($children == 1)
                {
                    children();
                }
                else if ($children > 1) children(0);
            }
            difference()
            {
                cube([ width, length, thickness ]);
                translate([ -0.5, -1, -0.5 ]) cube([ width + 1, tab_height + 1, thickness + 1 ]);

                // Cut out holes in the middle.
                for (i = [0:1:num_holes - 1])
                    translate([ hole_offset + (hole_width + hole_offset) * i, length - hole_offset, -0.5 ])
                        cuboid([ hole_width, hole_height, thickness + 1 ], rounding = tab_radius,
                               edges = [ FRONT + LEFT, FRONT + RIGHT ], anchor = BACK + LEFT + BOTTOM, $fn = 20);
                if ($children > 2)
                {
                    for (i = [1:$children - 1])
                    {
                        children(i);
                    }
                }
            }
        }
    }
}

// Module: MakeDividerWithText()
// Description:
//   Makes a divider with a tab section up the top.  First child is a diff to the tab, the rest is a diff to
//   the main body of the tab.
// Usage: MakeDividerWithText(10, 20, 1, 5, 3, 0);
// See also: MakeDivider(), MakeDividerTab()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
//   num_tabs = number of tabs across the top
//   tab_position = the position number of the tab, 0..num_tabs-1
//   text_str = the text string to use
//   text_offset = how far from the sides of the tab to put the text
//   text_height = how hight the text is, (default tab_height - text_offset)
//   font = the font to use (default "Stencil Std:style=Bold")
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 0,
//   text_str = "Frog");
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1,
//   text_str = "Bing");
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 2,
//   text_str = "Croak", text_depth=0.5);
module MakeDividerWithText(width, length, thickness, tab_height, text_str, num_tabs, tab_position, tab_radius = 2,
                           num_tabs = 3, tab_length = undef, text_offset = 2, text_height = undef, text_depth = undef,
                           font = "Stencil Std:style=Bold")
{
    assert(tab_position >= 0 && tab_position < num_tabs, "Tab position must be lower than num_tabs");
    tab_length_calc = tab_length == undef ? (width - tab_radius * num_tabs) / num_tabs : tab_length;
    text_width = tab_length_calc - text_offset * 2;
    text_height_calc = text_height == undef ? tab_height - text_offset : text_height;
    text_depth_calc = text_depth == undef ? thickness + 1 : text_depth;
    MakeDivider(width = width, length = length, thickness = thickness, tab_height = tab_height, tab_length = tab_length,
                num_tabs = num_tabs, tab_position = tab_position, tab_radius = tab_radius)
    {
        union()
        {
            translate([ text_offset, tab_height - text_offset * 1 / 4, thickness - text_depth_calc ])
                linear_extrude(height = text_depth_calc + 0.5) resize([ text_width, text_height_calc, 0 ], auto = true)
                    text(text = str(text_str), font = font, size = 10, spacing = 1, halign = "right", valign = "bottom",
                         spin = 180);
            if ($children > 0)
            {
                children(0);
            }
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}
