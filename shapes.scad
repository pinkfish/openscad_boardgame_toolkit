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

// LibFile: shapes.scad
//    This file has all the modules needed to make various shapes.

// FileSummary: Shapes for all sorts of things.
// FileGroup: Shapes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Shapes
//    Shapes to use in boxes and stuff.

// Module: DifferenceWithOffset()
// Description:
//   Helper function that does an offset with the size inside the difference of the object
//   makes it easier for constructing outlines.
// Arguments:
//   offset = how much of an offset, -ve is inside the shape, +ve is outside the shape.
module DifferenceWithOffset(offset)
{
    difference()
    {
        children();
        offset(delta = offset) children();
    }
}

// Module: Sword2d()
// Description:
//    2d shape of a sword.
// Arguments:
//    length = length of the sword
//    width = width of the sword
//    blade_width = width of the blade (default width / 3)
//    hilt_length = length of the hilt (default length / 15)
//    hilt_pos = position on the blade where the hilt starts (default length / 7)
//    blade_rounding = how much rounding on the end of the blade (default 1)
//    hilt_rounding = how much rounding on the hilt (default 1)
// Example:
//    Sword2d(100, 20);
module Sword2d(length, width, blade_width = undef, hilt_length = undef, hilt_pos = undef, hilt_rounding = 1,
               blade_rounding = 1)
{
    calc_hilt_length = DefaultValue(hilt_length, length / 15);
    calc_hilt_pos = DefaultValue(hilt_pos, length / 7);
    calc_blade_width = DefaultValue(blade_width, width / 3);
    union()
    {
        difference()
        {
            rect([ length, calc_blade_width ], rounding = [ 0, blade_rounding, blade_rounding, 0 ]);
            translate([ length / 2, width / 2 ]) right_triangle([ length / 3, width / 2 ], spin = 180);
            mirror([ 0, 1 ]) translate([ length / 2, width / 2 ]) right_triangle([ length / 3, width / 2 ], spin = 180);
        }
        translate([ -length / 2 + calc_hilt_pos + calc_hilt_length / 2, 0 ])
            rect([ calc_hilt_length, width ], rounding = hilt_rounding);
    }
}
// Module: Sword2dOutline()
// Description:
//    2d outline of a sword.
// Arguments:
//    length = length of the sword
//    width = width of the sword
//    blade_width = width of the blade (default width / 3)
//    hilt_length = length of the hilt (default length / 15)
//    hilt_pos = position on the blade where the hilt starts (default length / 7)
//    blade_rounding = how much rounding on the end of the blade (default 1)
//    hilt_rounding = how much rounding on the hilt (default 1)
//    line_width = how wide the line is (default 1)
// Example:
//    Sword2dOutline(100, 20);
module Sword2dOutline(length, width, blade_width = undef, hilt_length = undef, hilt_pos = undef, hilt_rounding = 1,
                      blade_rounding = 1, line_width = 1)
{
    calc_hilt_length = DefaultValue(hilt_length, length / 15);
    calc_hilt_pos = DefaultValue(hilt_pos, length / 7);
    calc_blade_width = DefaultValue(blade_width, width / 3);
    union()
    {
        DifferenceWithOffset(offset = -line_width)
            Sword2d(length, width, blade_width = calc_blade_width, hilt_length = calc_hilt_length,
                    hilt_pos = calc_hilt_pos, hilt_rounding = hilt_rounding, blade_rounding = blade_rounding);
        translate([ -length / 2 + calc_hilt_pos + calc_hilt_length / 2, 0 ]) DifferenceWithOffset(offset = -line_width)
            rect([ calc_hilt_length, width ], rounding = hilt_rounding);
        difference()
        {
            translate(
                [ -length / 2 + calc_hilt_pos + (length - calc_hilt_pos - calc_hilt_length) / 2 + calc_hilt_length, 0 ])
                rect([ length - calc_hilt_pos - calc_hilt_length, line_width ]);
            translate([ length / 2, width / 2 ]) right_triangle([ length / 3, width / 2 ], spin = 180);
            mirror([ 0, 1 ]) translate([ length / 2, width / 2 ]) right_triangle([ length / 3, width / 2 ], spin = 180);
        }
    }
}

// Module: Crossbow2d()
// Description:
//    A 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/8)
//    bow_width = width of the bow section of the bow (default width/4)
//    outer_circle = how big of a circle with the crossbow to draw (default width*2)
// Example:
//    Crossbow2d(70, 50);
module Crossbow2d(length, width, handle_width = undef, bow_width = undef, outer_circle = undef)
{
    calc_handle_width = DefaultValue(handle_width, width / 8);
    calc_outer_circle = DefaultValue(outer_circle, width * 2);
    calc_bow_width = DefaultValue(bow_width, width / 4);
    intersection()
    {
        rect([ width, length ]);
        union()
        {
            translate([ 0, calc_outer_circle / 2 - length / 2 ]) difference()
            {
                circle(d = calc_outer_circle);
                circle(d = calc_outer_circle - calc_bow_width);
                translate([ calc_outer_circle / 2, 0 ]) square(calc_outer_circle);
            }
            rect([ calc_handle_width, length ]);
        }
    }
}

// Module: Crossbow2dOutline()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/8)
//    bow_width = width of the bow section of the bow (default width/4)
//    outer_circle = how big of a circle with the crossbow to draw (default width*2)
//    line_width = width of the line to display (default 1)
// Example:
//    Crossbow2dOutline(70, 50);
module Crossbow2dOutline(length, width, handle_width = undef, bow_width = undef, outer_circle = undef, line_width = 1)
{
    calc_handle_width = DefaultValue(handle_width, width / 8);

    DifferenceWithOffset(offset = -line_width)
        Crossbow2d(length = length, width = width, handle_width = calc_handle_width, bow_width = bow_width,
                   outer_circle = outer_circle);
    DifferenceWithOffset(offset = -line_width) rect([ calc_handle_width, length ]);
}

// Module: Sledgehammer2d()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/4)
//    head_lenght = length of the head (default length/3.5)
//    rounding_head = rounding amoubnt on the head (default 2)
//    rounding_handle = rounding amount on the handle (default 1)
// Example:
//    Sledgehammer2d(70, 50);
module Sledgehammer2d(length, width, handle_width = undef, head_length = undef, rounding_head = 2, rounding_handle = 1)
{
    calc_hammer_handle_width = DefaultValue(handle_width, width / 4);
    calc_hammer_head_length = DefaultValue(head_length, length / 3.5);
    rect([ calc_hammer_handle_width, length ], rounding = rounding_handle);
    translate([ 0, length / 2 - calc_hammer_head_length / 2 ])
        rect([ width, calc_hammer_head_length ], rounding = rounding_head);
}

// Module: Sledgehammer2dOutline()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/4)
//    head_lenght = length of the head (default length/3.5)
//    rounding_head = rounding amoubnt on the head (default 2)
//    rounding_handle = rounding amount on the handle (default 1)
//    line_width = width of the lione (default 1)
//    strap_width = width of the strap outline(default line_width*4)
// Example:
//    Sledgehammer2dOutline(70, 50);
module Sledgehammer2dOutline(length, width, handle_width = undef, head_length = undef, rounding_head = 2,
                             rounding_handle = 1, line_width = 1, strap_width = undef)
{
    calc_hammer_handle_width = DefaultValue(handle_width, width / 4);
    calc_hammer_head_length = DefaultValue(head_length, length / 3.5);
    calc_strap_width = DefaultValue(strap_width, line_width * 4);
    DifferenceWithOffset(offset = -line_width) Sledgehammer2d(
        length = length, width = width, handle_width = calc_hammer_handle_width, head_length = calc_hammer_head_length);
    translate([ 0, length / 2 - calc_hammer_head_length / 2 ]) DifferenceWithOffset(offset = -line_width)
        rect([ width, calc_hammer_head_length ], rounding = rounding_head);
    DifferenceWithOffset(offset = -line_width) polygon([
        [ calc_hammer_handle_width / 2, length / 2 - calc_hammer_head_length ],
        [ calc_hammer_handle_width / 2 + calc_strap_width, length / 2 - calc_hammer_head_length ],
        [ -calc_hammer_handle_width / 2, length / 2 ],
        [ -calc_hammer_handle_width / 2 - calc_strap_width, length / 2 ],
    ]);
    DifferenceWithOffset(offset = -line_width) mirror([ 1, 0 ]) polygon([
        [ calc_hammer_handle_width / 2, length / 2 - calc_hammer_head_length ],
        [ calc_hammer_handle_width / 2 + calc_strap_width, length / 2 - calc_hammer_head_length ],
        [ -calc_hammer_handle_width / 2, length / 2 ],
        [ -calc_hammer_handle_width / 2 - calc_strap_width, length / 2 ],
    ]);
}

module Shoe2d()
{
}

module Shoe2dOutline()
{
}