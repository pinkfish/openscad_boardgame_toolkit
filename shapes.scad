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

// Module: Shoe2d()
// Description:
//    An nice 2d shoe shape.
// Arguments:
//    size = size of the shoe
//    leg_length = length of the leg bit of the shoe (default size/3)
//    sole_height = height of the sole base of the shoe (default size/20)
//    base_width = height of the base part of the shoe (default size/3)
// Example:
//    Shoe2d(50);
module Shoe2d(size, leg_length = undef, base_width = undef, sole_height = undef)
{
    calc_leg_length = DefaultValue(leg_length, size / 3);
    calc_base_width = DefaultValue(base_width, size / 3);
    calc_sole_height = DefaultValue(sole_height, size / 20);
    union()
    {
        translate([ 0, -size / 2 + calc_leg_length / 2 ]) rect([ size, calc_leg_length ]);
        translate([ size / 2 - calc_base_width / 2 - calc_sole_height, 0 ])
            rect([ calc_base_width, size ], rounding = [ 0, calc_base_width * 3 / 4, 0, 0 ]);
        hull()
        {
            translate([ size / 2 - calc_sole_height, (size * 3 / 5) / 2 ]) circle(r = calc_sole_height);
            translate([ size / 2 - calc_sole_height * 2, -size / 2 + calc_leg_length ]) circle(r = calc_sole_height);
            translate([ size / 2 - calc_sole_height / 2, size / 2 - calc_sole_height / 2 ])
                circle(r = calc_sole_height / 2);
            translate([ size / 2 - calc_sole_height * 2, size / 2 - calc_sole_height / 2 ])
                circle(r = calc_sole_height / 2);
        }
    }
}

// Module: Shoe2dOutline()
// Description:
//    An nice 2d shoe outline shape.
// Arguments:
//    size = size of the shoe
//    leg_length = length of the leg bit of the shoe (default size/3)
//    sole_height = height of the sole base of the shoe (default size/20)
//    base_width = height of the base part of the shoe (default size/3)
//    line_width = width of the outline line (default 1)
// Example:
//    Shoe2dOutline(50);
module Shoe2dOutline(size, leg_length = undef, base_width = undef, sole_height = undef, line_width = 1)
{
    DifferenceWithOffset(offset = -line_width)
        Shoe2d(size, leg_length = leg_length, base_width = base_width, sole_height = sole_height);
}

// Module: Bag2d()
// Description:
//    An nice 2d bag shape.
// Arguments:
//    size = size of the bag
//    base_round_diameter = round diameter of the base circles (default size/4)
//    main_round_diameter = round diameter of the middle bulge bit (default size/2)
//    neck_width = width of the neck of the bag (default size/6)
//    rope_length = length of the rope (default size/4)
// Example:
//    Bag2d(50);
module Bag2d(size, base_round_diameter = undef, main_round_diameter = undef, neck_width = undef, rope_length = undef)
{
    calc_base_round = DefaultValue(base_round_diameter, size / 4);
    calc_main_round = DefaultValue(main_round_diameter, size / 2);
    calc_neck_width = DefaultValue(neck_width, size / 6);
    calc_rope_length = DefaultValue(rope_length, size / 4);
    union()
    {
        // Bag bit
        hull()
        {
            translate([ size / 2 - calc_base_round / 2, size / 2 - calc_base_round / 2 ]) circle(d = calc_base_round);
            translate([ size / 2 - calc_base_round / 2, -size / 2 + calc_base_round / 2 ]) circle(d = calc_base_round);
            translate([ size / 2 - calc_base_round / 2, -size / 2 + calc_base_round / 2 ]) circle(d = calc_base_round);
            translate([ size / 2 - calc_base_round, -size / 2 + calc_base_round / 2 ]) circle(d = calc_base_round);
            translate([ -size / 2 + calc_base_round, size / 2 - calc_base_round / 2 ]) circle(d = calc_base_round);
            translate([ -size / 2 + calc_base_round + calc_main_round / 2, -calc_main_round / 4 ])
                circle(d = calc_main_round);
        }
        // Top bit.
        polygon([
            [ -size / 2, size / 2 - calc_neck_width * 5 / 8 - calc_neck_width / 4 - calc_neck_width ],
            [ -size / 2, size / 2 - calc_neck_width * 5 / 8 - calc_neck_width / 4 ], [ 0, calc_neck_width ],
            [ 0, calc_neck_width / 2 ]
        ]);
        // Rope
        DifferenceWithOffset(offset = -calc_rope_length / 10)
            translate([ -size / 2 + calc_rope_length / 6 * 2, size / 2 - calc_rope_length / 2 - calc_neck_width * 1.8 ])
                rotate(90)
                    egg(calc_rope_length, calc_rope_length / 3, calc_rope_length / 8, calc_rope_length, $fn = 180);
    }
}

// Module: Bag2dOutline()
// Description:
//    An nice 2d bag outline shape.
// Arguments:
//    size = size of the bag
//    base_round_diameter = round diameter of the base circles (default size/4)
//    main_round_diameter = round diameter of the middle bulge bit (default size/2)
//    neck_width = width of the neck of the bag (default size/6)
//    line_width = width of the line to use for the outline
// Example:
//    Bag2d(50);
module Bag2dOutline(size, base_round_diameter = undef, main_round_diameter = undef, neck_width = undef,
                    rope_length = undef, line_width = 1)
{
    DifferenceWithOffset(offset = -line_width)
        Bag2d(size, base_round_diameter = base_round_diameter, main_round_diameter = main_round_diameter,
              neck_width = neck_width, rope_length = rope_length);
}

// Module: Torch2d()
// Description:
//    An nice 2d torch shape.
// Arguments:
//    size = size of the torch
//    handle_width = the width of the handle (default width/2)
//    head_length = length of the head (default length/7)
// Example:
//    Torch2d(100, 20);
module Torch2d(length, width, handle_width = undef, head_length = undef)
{
    calc_handle_width = DefaultValue(handle_width, width / 2);
    calc_head_length = DefaultValue(head_length, length / 7);
    rect([ length, calc_handle_width ], rounding = width / 6);
    hull()
    {
        translate([ length / 2 - width / 4, width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4 - calc_head_length, width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4, -width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4 - calc_head_length, -width / 4 ]) circle(d = width / 2);
    }
}

// Module: Torch2dOutline()
// Description:
//    An nice 2d torch outline shape.
// Arguments:
//    size = size of the torch
//    handle_width = the width of the handle (default width/2)
//    head_length = length of the head (default length/7)
//    line_width = width of the line (default 1)
// Example:
//    Torch2dOutline(100, 20);
module Torch2dOutline(length, width, handle_width = undef, head_length = undef, line_width = 1)
{
    calc_handle_width = DefaultValue(handle_width, width / 2);
    calc_head_length = DefaultValue(head_length, length / 7);
    DifferenceWithOffset(offset = -line_width)
        Torch2d(length = length, width = width, handle_width = calc_handle_width, head_length = calc_head_length);
    DifferenceWithOffset(offset = -line_width) hull()
    {
        translate([ length / 2 - width / 4, width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4 - calc_head_length, width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4, -width / 4 ]) circle(d = width / 2);
        translate([ length / 2 - width / 4 - calc_head_length, -width / 4 ]) circle(d = width / 2);
    }
}

// Module: Teapot2d()
// Description:
//    An nice 2d teapor shape.
// Arguments:
//    length = length of the teapot
//    width = width of the teapot
//    top_width = top width of the teapot (default width*6/10)
//    top_length = length to the top part of the teapot.
//    top_circle_diameter = circle of the top part of the teapot
//    handle_rounding = rounding amount to use int he top handle
//    handle_width = width of the top handle
//    spout_length = length of the spout
//    side_handle_length = length of the side handle
//    side_handle_rounding = rounding of the bottom part of the handle
// Example:
//    Teapot2d(100, 70);
module Teapot2d(length, width, top_width = undef, top_length = undef, top_circle_diameter = undef,
                handle_rounding = undef, handle_width = undef, spout_length = undef, side_handle_length = undef,
                side_handle_rounding = undef)
{
    calc_top_width = DefaultValue(top_width, width * 6 / 10);
    calc_top_length = DefaultValue(top_length, length * 7 / 10);
    calc_top_circle_diameter = DefaultValue(top_circle_diameter, calc_top_width * 8 / 10);
    calc_handle_rounding = DefaultValue(handle_rounding, width / 15);
    calc_handle_width = DefaultValue(handle_width, width / 30);
    calc_spout_length = DefaultValue(spout_length, length / 5);
    calc_side_handle_length = DefaultValue(side_handle_length, length / 3);
    calc_side_handle_rounding = DefaultValue(side_handle_rounding, width * 4 / 10);
    union()
    {
        // Base
        polygon([
            [ length / 2, width / 2 ],
            [ length / 2 - calc_top_length, calc_top_width / 2 ],
            [ length / 2 - calc_top_length, -calc_top_width / 2 ],
            [ length / 2, -width / 2 ],
        ]);
        // Spout
        polygon([
            [ length / 2 - calc_top_length, calc_top_width / 2 ],
            [ length / 2 - calc_top_length, width / 2 ],
            [ length / 2 - calc_top_length + calc_spout_length, calc_top_width / 2 ],

        ]);
        // Top bit
        translate([ length / 2 - calc_top_length, 0 ]) circle(d = calc_top_circle_diameter);
        diff_top = length - calc_top_length - calc_top_circle_diameter / 2;
        // Handle
        translate([ -length / 2 + diff_top, 0 ])
        {
            DifferenceWithOffset(offset = -calc_handle_width)
                rect([ diff_top * 2, diff_top * 2 ], rounding = calc_handle_rounding);
        }
        // Back Handle.
        DifferenceWithOffset(offset = -calc_handle_width) hull()
        {
            side_diameter = width / 20;
            translate([ side_diameter / 2, side_diameter / 2 ])
            {
                translate([ length / 2 - calc_top_length, -calc_top_width / 2 ]) circle(d = side_diameter);
                translate([ length / 2 - calc_top_length, -width / 2 ]) circle(d = side_diameter);
            }
            translate([ -calc_side_handle_rounding / 2, calc_side_handle_rounding / 2 ])
                translate([ length / 2 - calc_top_length + calc_side_handle_length, -width / 2 ])
                    circle(d = calc_side_handle_rounding);
        }
    }
}

// Constant: australia_map_length
// Description: The length of the australian svg map
australia_map_length = 365.040;
// Constant: australia_map_width
// Description: The width of the australian svg map
australia_map_width = 340.160;

// Function: AustraliaMapWidth()
// Description: Works out the width of the map from the length.
function AustraliaMapWidth(length) = length * (australia_map_width / australia_map_length);

// Module: AustraliaMap2d()
// Description:
//    a map of australia
// Arguments:
//    length = length of the map
// Example:
//    AustraliaMap2d(100);
module AustraliaMap2d(length)
{
    resize([ length, AustraliaMapWidth(length) ]) import("svg/australia.svg");
}