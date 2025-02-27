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

// LibFile: flags.scad
//    This file has all the modules needed to make some fun flags.

// FileSummary: Flags for a selection of countries.
// FileGroup: Shapes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Flags
// Description:
//    Flags of the world to use where all good flags are used in openscad.

// Module: FlagBackgroundAndBorder()
// Description:
//    Makes a background to the flag with the specified border.  The first child is used to subtract
//    from the background while the second child renders the inside of the flag.
// Arguments:
// .  length = length of the background
//    width = width of background (default length/2)
//    height = height of the background
//    background_color = color of the background
//    background= generate the background (default true)
//    border = size of border to generate (default 0)
module FlagBackgroundAndBorder(length, height, background_color, width = undef, background = true, border = 0,
                               solid_background = false, grid_spacing = 1.5)
{
    calc_width = DefaultValue(width, length / 2);
    if (border > 0)
    {
        difference()
        {
            color(default_material_colour) cuboid([ length + border, calc_width + border, height ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) color(default_material_colour)
                cuboid([ length - 0.02, calc_width - 0.02, height + 1 ], anchor = BOTTOM);
        }
    }
    if (background)
    {
        color(background_color) difference()
        {
            if (solid_background)
            {
                cuboid([ length, calc_width, height ], anchor = BOTTOM);
            }
            else
            {
                intersection()
                {
                    cuboid([ length, calc_width, height ], anchor = BOTTOM);
                    translate([ -length * 5.5 / 4, -calc_width / 2, 0 ])
                        Make3dStripedGrid(width = length, length = calc_width, height = height, spacing = grid_spacing);
                }
            }
            translate([ 0, 0, -0.5 ]) children(0);
        }
    }
    children(1);
}

// Module: StAndrewsCross()
// Description:
//   Flag of the St Andrews Cross to use for anything.
// Arguments:
//   length = length of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// Topics: Flags
// Example:
//   StAndrewsCross(100, 4);
// Example:
//   StAndrewsCross(100, 4);
// Example:
//   StAndrewsCross(100, 4);
module StAndrewsCross(length, height)
{
    rotate([ 0, 0, 22.5 ]) color("white") cuboid([ length * 2, length / 2 / 5, height ], anchor = BOTTOM);
    rotate([ 0, 0, -22.5 ]) color("white") cuboid([ length * 2, length / 2 / 5, height ], anchor = BOTTOM);
}

// Module: StPatricksCross()
// Description:
//   Flag of the St Patricks Cross to use for anything.
// Arguments:
//   length = length of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// Topics: Flags
// Example:
//   StPatricksCross(100, 5);
// Example:
//   StPatricksCross(100, 4);
// Example:
//   StPatricksCross(100, 4);
module StPatricksCross(length, height)
{
    rotate([ 0, 0, 22.5 ]) color("red") cuboid([ length * 2, length / 2 / 15, height ], anchor = BOTTOM + FRONT + LEFT);
    rotate([ 0, 0, -22.5 ]) color("red")
        cuboid([ length * 2, length / 2 / 15, height ], anchor = BOTTOM + FRONT + RIGHT);
    rotate([ 0, 0, 22.5 ]) color("red") cuboid([ length * 2, length / 2 / 15, height ], anchor = BOTTOM + BACK + RIGHT);
    rotate([ 0, 0, -22.5 ]) color("red") cuboid([ length * 2, length / 2 / 15, height ], anchor = BOTTOM + BACK + LEFT);
}

// Module: StGeorgesCross()
// Description:
//   Flag of the St Georges Cross to use for anything.
// Arguments:
//   length = lenght of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// Topics: Flags
// Example:
//   StGeorgesCross(100, 5, 4);
// Example:
//   StGeorgesCross(100, 5, 4);
// Example:
//   StGeorgesCross(100, 5, 4);
module StGeorgesCross(length, white_height, red_height)
{
    module RedBit(height)
    {
        cuboid([ length, length / 15, height ], anchor = BOTTOM);
        rotate([ 0, 0, 90 ]) cuboid([ length, length / 15, height ], anchor = BOTTOM);
    }

    fimbration = length / 15 / 2;
    difference()
    {
        union()
        {
            color("white") cuboid([ length, length / 15 + fimbration, white_height ], anchor = BOTTOM);
            color("white") rotate([ 0, 0, 90 ])
                cuboid([ length, length / 15 + fimbration, white_height ], anchor = BOTTOM);
        }
        RedBit(white_height + 1);
    }
    color("red") RedBit(red_height);
}

// Module: UnionJack()
// Description:
//   Flag of Great Britan to use for anything.
// Arguments:
//   length = length of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// . border = border to put on the flag (this goes outside the length) (default 0)
//   background = put in a blue background with stripes (default true)
// Topics: Flags
// Example:
//   UnionJack(100, 5, 4);
// Example:
//   UnionJack(100, 5, 4, border = 1);
// Example:
//   UnionJack(100, 5, 4, background = false);
module UnionJack(length, white_height, red_height, background = true, border = 0)
{
    if (border > 0)
    {
        difference()
        {
            cuboid([ length + border, length / 2 + border, max(white_height, red_height) ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ])
                cuboid([ length - 0.02, length / 2 - 0.02, max(white_height, red_height) + 1 ], anchor = BOTTOM);
        }
    }

    intersection()
    {
        translate([ 0, 0, -0.5 ]) cuboid([ length, length / 2, max(white_height, red_height) + 1 ], anchor = BOTTOM);

        union()
        {
            if (background)
            {
                difference()
                {
                    color("blue") translate([ -length * 5 / 4, -length / 4, 0 ]) Make3dStripedGrid(
                        width = length, length = length, height = max(red_height, white_height), spacing = 1.5);
                    translate([ 0, 0, -0.5 ]) StGeorgesCross(length, white_height + 1, white_height + 1);
                    translate([ 0, 0, -0.5 ]) StPatricksCross(length, white_height + 1);
                }
            }
            // st andrews Cross.
            difference()
            {
                union()
                {
                    difference()
                    {
                        StAndrewsCross(length, white_height);
                        translate([ 0, 0, -0.5 ]) StPatricksCross(length, white_height + 1);
                    }
                    StPatricksCross(length, red_height);
                }
                translate([ 0, 0, -0.5 ]) StGeorgesCross(length, white_height + 1, white_height + 1);
            }

            StGeorgesCross(length = length, white_height = white_height, red_height = red_height);
        }
    }
}

// Module: AustralianFlag()
// Description:
//   Flag of Australia to use for anything.
// Arguments:
//   length = lenght of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// . border = border to put on the flag (this goes outside the length) (default 0)
//   background = put in a blue background with stripes (default true)
//   solid_background = generate the flag for an mmu, solid background (default false)
// Topics: Flags
// Example:
//   AustralianFlag(100, 5, 4, 1);
// Example:
//   AustralianFlag(100, 5, 4, 1, border = 1);
// Example:
//   AustralianFlag(100, 5, 4, 1, background = false);
// Example:
//   AustralianFlag(100, 5, 4, 1, border = 1, solid_background = true);
module AustralianFlag(length, white_height, red_height, blue_height, border = 0, background = true,
                      solid_background = false)
{
    module Star5(d)
    {
        star(n = 5, r = d / 2, ir = d * 4 / 9 / 2);
    }

    module Star7(d)
    {
        rotate(180 / 14 + 180) star(n = 7, r = d / 2, ir = d * 4 / 9 / 2);
    }

    flag_len = 450;
    flag_width = 225;

    if (border > 0)
    {
        difference()
        {
            color(default_material_colour)
                cuboid([ length + border, length / 2 + border, max(white_height, red_height) ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) color(default_material_colour)
                cuboid([ length - 0.02, length / 2 - 0.02, max(white_height, red_height) + 1 ], anchor = BOTTOM);
        }
    }

    translate([ -length / 2, -length / 4, 0 ]) intersection()
    {
        scale([ length / flag_len, length / flag_len, 1 ]) cube([ 450, 225, 30 ]);
        union()
        {
            if (background)
            {
                color("blue") difference()
                {
                    if (solid_background)
                    {
                        translate([ length / 2, length / 4, 0 ])
                            cuboid([ length, length / 2, blue_height ], anchor = BOTTOM);
                    }
                    else
                    {
                        translate([ -length / 4, 0, 0 ])
                            Make3dStripedGrid(width = length, length = length / 2, height = blue_height, spacing = 1.5);
                    }
                    intersection()
                    {
                        translate([ 0, length / 2, -0.5 ])
                            cuboid([ length / 2 - 0.01, length / 4 - 0.01, max(white_height, red_height) + 1 ],
                                   anchor = BOTTOM + BACK + LEFT);
                        translate([ length / 4, length * 3 / 8, 0 ])
                            UnionJack(length = length / 2, white_height = max(white_height, red_height) + 1,
                                      red_height = max(white_height, red_height) + 1, background = false);
                    }
                }
            }
            union()
            {
                scale_div = 22;
                star_scale = 0.05;

                //    Alpha Crucis – 7-pointed star, straight below centre fly 1⁄6 up from bottom edge.
                color("white") translate([ length * 3 / 4, length / 12, 0 ]) linear_extrude(height = white_height)
                    Star7(length / 14);
                // Beta Crucis – 7-pointed star, 1⁄4 of the way left and 1⁄16 up from the centre fly.
                color("white") translate([ length * 5 / 8, length / 2 * 9 / 16, 0 ])
                    linear_extrude(height = white_height) Star7(length / 14);
                // Gamma Crucis – 7-pointed star, straight above centre fly 1⁄6 down from top edge.
                color("white") translate([ length * 3 / 4, length / 2 * 5 / 6, 0 ])
                    linear_extrude(height = white_height) Star7(length / 14);
                // Delta Crucis – 7-pointed star, 2⁄9 of the way right and 31⁄240 up from the centre fly.
                color("white") translate([ length * 31 / 36, length / 2 * 151 / 240, 0 ])
                    linear_extrude(height = white_height) Star7(length / 14);
                // Epsilon Crucis – 5-pointed star, 1⁄10 of the way right and 1⁄24 down from the centre fly.
                color("white") translate([ length * 4 / 5, length / 2 * 11 / 24, 0 ])
                    linear_extrude(height = white_height) Star7(length / 24);
                // Commonwealth star
                color("white") translate([ length / 4, length / 8, 0 ]) linear_extrude(height = white_height)
                    Star5(length * 3 / 20);

                translate([ length / 4, length * 3 / 8, 0 ]) UnionJack(length = length / 2, white_height = white_height,
                                                                       red_height = red_height, background = false);
            }
        }
    }
}

// Module: SwedenFlag()
// Description:
//   Flag of Sweden to use for anything.
// Arguments:
//   length = length of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// . border = border to put on the flag (this goes outside the length) (default 0)
//   background = put in a blue background with stripes (default true)
// Topics: Flags
// Example:
//   SwedenFlag(100, 4);
// Example:
//   SwedenFlag(100, 4, border = 1);
// Example:
//   SwedenFlag(100, 4, background = false);
module SwedenFlag(length, height, background = true, border = 0, solid_background = 0,
                  layer_thickness = default_slicing_layer_height)
{
    width = length * 5 / 8;
    line_horiz = width * 2 / 10;
    line_vert = length * 2 / 16;
    module CrossBit(height)
    {
        cuboid([ length, line_horiz, height ], anchor = TOP);
        translate([ -length * 3 / 16, 0, 0 ]) cuboid([ line_vert, width, height ], anchor = TOP);
    }
    background_height = solid_background ? height - layer_thickness * 2 : height * 3 / 4;
    FlagBackgroundAndBorder(length, background_height, width = width,
                            background_color = solid_background ? default_material_colour : "blue",
                            background = background, border = border, solid_background = solid_background)
    {
        translate([ 0, 0, height ])
        {
            color("yellow") CrossBit(solid_background ? layer_thickness : height);
        }
        translate([ 0, 0, height ])
        {
            color("yellow") CrossBit(solid_background ? layer_thickness : height);
        }
    }
    if (solid_background)
    {
        translate([ 0, 0, height - layer_thickness * 2 ]) color("blue")
            cuboid([ length, width, layer_thickness ], anchor = BOTTOM);
    }
}

// Module: UnitedStatesFlag()
// Description:
//   Flag of the united states to use for anything.
// Arguments:
//   length = length of the flag
//   white_height = height of the white parts
//   red_height = height of the red parts
// . border = border to put on the flag (this goes outside the length) (default 0)
//   background = put in a blue background with stripes (default true)
//   solid_background = a solid background (setup for mmu)
// Topics: Flags
// Example:
//   UnitedStatesFlag(100, 4, 2, 1);
// Example:
//   UnitedStatesFlag(100, 4, 2, 1, border = 1);
// Example:
//   UnitedStatesFlag(100, 4, 2, 1, background = false);
module UnitedStatesFlag(length, white_height, red_height, blue_height, background = true, border = 0,
                        solid_background = false, layer_thickness = default_slicing_layer_height)
{
    width = length / 1.9;
    top_bit_width = width * 7 / 13;
    top_bit_length = length * 2 / 5;
    star_offset_width = top_bit_length / 10;
    star_offset_length = top_bit_width / 5.5;
    stripe = width / 13;
    star_size = stripe * 4 / 5;
    background_material_thickness = min(red_height, white_height) - layer_thickness;
    background_stars_material_thickness = solid_background ? blue_height - layer_thickness : blue_height;
    module Stars()
    {
        for (i = [0:1:4])
        {
            for (j = [0:1:9])
            {
                color("white") translate([
                    -top_bit_width / 2 + star_offset_length / 2 + star_offset_length * i +
                        (j % 2 == 1 ? star_offset_length / 2 : 0),
                    -top_bit_length / 2 + star_offset_width / 2 + star_offset_width * j,
                    blue_height
                ]) linear_extrude(height = white_height - blue_height)
                    star(5, or = star_size / 2, ir = star_size / 4, spin = 180 / 5);
            }
        }
    }
    module StarSection(white_height)
    {
        FlagBackgroundAndBorder(length = top_bit_width, height = background_stars_material_thickness,
                                background_color = solid_background ? default_material_colour : "blue",
                                width = top_bit_length, background = background, border = 0,
                                grid_spacing = min(star_offset_width / 4, star_offset_length / 4),
                                solid_background = solid_background)
        {
            union()
            {
                Stars();
            }
            union()
            {
                Stars();
            }
        }
        if (solid_background)
        {
            translate([ 0, 0, background_stars_material_thickness ]) color("blue")
                cuboid([ top_bit_width, top_bit_length, layer_thickness ], anchor = BOTTOM);
        }
    }
    module Stripes(white_height, red_height)
    {
        difference()
        {
            union()
            {
                color(default_material_colour)
                    cuboid([ width, length, background_material_thickness ], anchor = BOTTOM + LEFT);
                translate([ 0, 0, background_material_thickness ])
                {
                    for (i = [0:1:5])
                    {
                        translate([ stripe * 2 * i, 0, 0 ]) color("red") cuboid(
                            [ stripe, length, red_height - background_material_thickness ], anchor = BOTTOM + LEFT);
                        translate([ stripe * 2 * i + stripe, 0, 0 ]) color("white") cuboid(
                            [ stripe, length, white_height - background_material_thickness ], anchor = BOTTOM + LEFT);
                    }
                    translate([ stripe * 2 * 6, 0, 0 ]) color("red")
                        cuboid([ stripe, length, red_height - background_material_thickness ], anchor = BOTTOM + LEFT);
                }
            }
            translate([ -width / 2 + stripe * 6.5, -length / 2 + top_bit_length / 2, -1 ])
                cuboid([ top_bit_width + 0.01, top_bit_length + 0.01, max(white_height, red_height) + 2 ],
                       anchor = BOTTOM + LEFT);
        }
    }
    module MainFlag(white_height, red_height)
    {
        translate([ -width / 2, 0, 0 ]) Stripes(white_height = white_height, red_height = red_height);
        translate([ -width / 2 + top_bit_width / 2, -length / 2 + top_bit_length / 2, 0 ])
            StarSection(white_height = white_height);
    }
    MainFlag(white_height = white_height, red_height = red_height);
    if (border > 0)
    {
        difference()
        {
            color(default_material_colour)
                cuboid([ width + border, length + border, max(white_height, red_height) ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) color(default_material_colour)
                cuboid([ width - 0.02, length - 0.02, max(white_height, red_height) + 1 ], anchor = BOTTOM);
        }
    }
}

module PortugeseFlag(length, height, background = true, border = 0)
{
    width = length * 2 / 3;

    module Quina(width, height)
    {
        calc_len = 247.6548 - 232.636;
        calc_width = 236.2621 - 217.4357;
        mult = width / calc_width;
        linear_extrude(height = height) resize([ calc_len * mult, width ])
            translate([ -232.636 - calc_len / 2, -236.2621 + calc_width / 2 ])
        {

            bez = [
                [ 232.636, 228.19 ],
                [ 232.636, 228.19 ],
                [ 232.636, 228.195 ],
                [ 232.636, 228.195 ],
                [ 232.636, 230.4069 ],
                [ 233.48526999999999, 232.4222 ],
                [ 234.8478, 233.8844 ],
                [ 236.213, 235.3511 ],
                [ 238.0932, 236.2621 ],
                [ 240.1498, 236.2621 ],
                [ 242.217, 236.2621 ],
                [ 244.0937, 235.35723000000002 ],
                [ 245.4527, 233.8967 ],
                [ 246.8108, 232.43800000000002 ],
                [ 247.6548, 230.42451 ],
                [ 247.6548, 228.2037 ],
                [ 247.6548, 228.2037 ],
                [ 247.6548, 217.4357 ],
                [ 247.6548, 217.4357 ],
                [ 247.6548, 217.4357 ],
                [ 232.6628, 217.4234 ],
                [ 232.6628, 217.4234 ],
                [ 232.6628, 217.4234 ],
                [ 232.6355, 228.18939999999998 ],
                [ 232.6355, 228.18939999999998 ],
            ];
            path = bezpath_curve(bez);
            polygon(path);
        }
    }

    module MiddleScrollsYellow(height, width)
    {
        len_min = 139.67299999999997;
        len_max = 340.11996;
        width_min = 99.546;
        width_max = 300.796;
        calc_len = len_max - len_min;
        calc_width = width_max - width_min;
        mult = width / calc_width;

        color("yellow") linear_extrude(height = height) resize([ mult * calc_len, width ])
            translate([ -len_max + (len_max - len_min) / 2, -width_max + (width_max - width_min) / 2 ])
        {
            polygon(bezpath_curve([
                [ 318.24, 262.04 ],
                [ 288.03000000000003, 261.13 ],
                [ 149.5, 174.66000000000003 ],
                [ 148.55, 160.89000000000001 ],
                [ 148.55, 160.89000000000001 ],
                [ 156.1996, 148.133 ],
                [ 156.1996, 148.133 ],
                [ 169.94060000000002, 168.09900000000002 ],
                [ 311.55960000000005, 252.193 ],
                [ 325.4696, 249.21300000000002 ],
                [ 325.4696, 249.21300000000002 ],
                [ 318.2397, 262.036 ],
                [ 318.2397, 262.036 ],
            ]));
            polygon(bezpath_curve([
                [ 240.17, 169.23 ],
                [ 270.407, 168.99098999999998 ],
                [ 307.71999999999997, 165.0981 ],
                [ 329.193, 156.54 ],
                [ 329.193, 156.54 ],
                [ 324.56649999999996, 149.0232 ],
                [ 324.56649999999996, 149.0232 ],
                [ 311.87449999999995, 156.0479 ],
                [ 274.3565, 160.6672 ],
                [ 239.91449999999998, 161.3582 ],
                [ 199.17849999999999, 160.98337 ],
                [ 170.42449999999997, 157.1901 ],
                [ 156.01749999999998, 147.5232 ],
                [ 156.01749999999998, 147.5232 ],
                [ 151.6503, 155.5277 ],
                [ 151.6503, 155.5277 ],
                [ 178.1343, 166.7347 ],
                [ 205.27329999999998, 169.1147 ],
                [ 240.1703, 169.2307 ],
            ]));
            polygon(bezpath_curve([
                [ 140.88, 205.66 ],
                [ 159.478, 215.663 ],
                [ 200.785, 220.704 ],
                [ 239.874, 221.051 ],
                [ 275.465, 221.10739999999998 ],
                [ 321.832, 215.5494 ],
                [ 339.171, 206.361 ],
                [ 339.171, 206.361 ],
                [ 338.69388, 196.349 ],
                [ 338.69388, 196.349 ],
                [ 333.26928, 204.8263 ],
                [ 283.58088, 212.958 ],
                [ 239.48787999999996, 212.625 ],
                [ 195.39487999999994, 212.2925 ],
                [ 154.44987999999995, 205.4821 ],
                [ 140.80087999999995, 196.666 ],
                [ 140.80087999999995, 196.666 ],
                [ 140.88027999999994, 205.6574 ],
                [ 140.88027999999994, 205.6574 ],
            ]));
            polygon(bezpath_curve([
                [ 327.58, 247.38 ],   [ 327.58, 247.38 ], [ 320.201, 258.829 ], [ 320.201, 258.829 ],
                [ 320.201, 258.829 ], [ 299.0, 240.0 ],   [ 299.0, 240.0 ],     [ 299.0, 240.0 ],
                [ 244.0, 203.0 ],     [ 244.0, 203.0 ],   [ 244.0, 203.0 ],     [ 182.0, 169.0 ],
                [ 182.0, 169.0 ],     [ 182.0, 169.0 ],   [ 149.81, 157.99 ],   [ 149.81, 157.99 ],
                [ 149.81, 157.99 ],   [ 156.67, 145.27 ], [ 156.67, 145.27 ],   [ 156.67, 145.27 ],
                [ 159.0, 144.0 ],     [ 159.0, 144.0 ],   [ 159.0, 144.0 ],     [ 179.0, 149.0 ],
                [ 179.0, 149.0 ],     [ 179.0, 149.0 ],   [ 245.0, 183.0 ],     [ 245.0, 183.0 ],
                [ 245.0, 183.0 ],     [ 283.0, 207.0 ],   [ 283.0, 207.0 ],     [ 283.0, 207.0 ],
                [ 315.0, 230.0 ],     [ 315.0, 230.0 ],   [ 315.0, 230.0 ],     [ 328.0, 245.0 ],
                [ 328.0, 245.0 ],
            ]));
            polygon(bezpath_curve([
                [ 239.79, 260.32 ],
                [ 197.018, 260.06511 ],
                [ 160.36899999999997, 248.661 ],
                [ 152.63, 246.77599999999998 ],
                [ 152.63, 246.77599999999998 ],
                [ 158.2733, 255.61039999999997 ],
                [ 158.2733, 255.61039999999997 ],
                [ 171.9433, 261.36069999999995 ],
                [ 207.6973, 269.93039999999996 ],
                [ 240.20030000000003, 268.98139999999995 ],
                [ 272.70430000000005, 268.03331 ],
                [ 301.11030000000005, 265.51539999999994 ],
                [ 321.1283, 255.77039999999994 ],
                [ 321.1283, 255.77039999999994 ],
                [ 326.91450000000003, 246.61489999999995 ],
                [ 326.91450000000003, 246.61489999999995 ],
                [ 313.27250000000004, 253.03989999999996 ],
                [ 266.84650000000005, 260.25389999999993 ],
                [ 239.78950000000003, 260.31989999999996 ],
            ]));
            polygon(bezpath_curve([
                [ 243.98, 100.68 ],
                [ 243.98, 100.68 ],
                [ 235.49455, 100.68 ],
                [ 235.49455, 100.68 ],
                [ 235.49455, 100.68 ],
                [ 235.50455, 299.64 ],
                [ 235.50455, 299.64 ],
                [ 235.50455, 299.64 ],
                [ 244.01909999999998, 299.64 ],
                [ 244.01909999999998, 299.64 ],
            ]));
            polygon(bezpath_curve([
                [ 338.99, 203.935 ],  [ 338.99, 203.935 ],  [ 338.99, 196.5796 ], [ 338.99, 196.5796 ],
                [ 338.99, 196.5796 ], [ 333.0, 190.9996 ],  [ 333.0, 190.9996 ],  [ 333.0, 190.9996 ],
                [ 299.0, 181.9996 ],  [ 299.0, 181.9996 ],  [ 299.0, 181.9996 ],  [ 250.0, 176.9996 ],
                [ 250.0, 176.9996 ],  [ 250.0, 176.9996 ],  [ 191.0, 179.9996 ],  [ 191.0, 179.9996 ],
                [ 191.0, 179.9996 ],  [ 149.0, 189.9996 ],  [ 149.0, 189.9996 ],  [ 149.0, 189.9996 ],
                [ 140.52, 196.2796 ], [ 140.52, 196.2796 ], [ 140.52, 196.2796 ], [ 140.52, 203.6368 ],
                [ 140.52, 203.6368 ], [ 140.52, 203.6368 ], [ 162.0, 193.9998 ],  [ 162.0, 193.9998 ],
                [ 162.0, 193.9998 ],  [ 213.0, 185.9998 ],  [ 213.0, 185.9998 ],  [ 213.0, 185.9998 ],
                [ 262.0, 185.9998 ],  [ 262.0, 185.9998 ],  [ 262.0, 185.9998 ],  [ 298.0, 189.9998 ],
                [ 298.0, 189.9998 ],  [ 298.0, 189.9998 ],  [ 323.0, 195.9998 ],  [ 323.0, 195.9998 ],
            ]));
            polygon(bezpath_curve([
                [ 239.48, 132.96 ],
                [ 276.329, 132.77567000000002 ],
                [ 308.46999999999997, 138.1123 ],
                [ 323.17499999999995, 145.645 ],
                [ 323.17499999999995, 145.645 ],
                [ 328.5388, 154.924 ],
                [ 328.5388, 154.924 ],
                [ 315.7578, 148.036 ],
                [ 281.08279999999996, 140.874 ],
                [ 239.53379999999999, 141.945 ],
                [ 205.6798, 142.15313999999998 ],
                [ 169.5068, 145.6721 ],
                [ 151.3578, 155.355 ],
                [ 151.3578, 155.355 ],
                [ 157.7613, 144.646 ],
                [ 157.7613, 144.646 ],
                [ 172.65630000000002, 136.9219 ],
                [ 207.7833, 133.003 ],
                [ 239.4813, 132.962 ],
            ]));
            polygon(bezpath_curve([
                [ 289.15, 241.26 ],
                [ 270.93199999999996, 237.8592 ],
                [ 252.68099999999998, 237.3653 ],
                [ 239.933, 237.5153 ],
                [ 178.526, 238.23497 ],
                [ 158.689, 250.1243 ],
                [ 156.26799999999997, 253.7243 ],
                [ 156.26799999999997, 253.7243 ],
                [ 151.67859999999996, 246.2428 ],
                [ 151.67859999999996, 246.2428 ],
                [ 167.31259999999997, 234.9108 ],
                [ 200.75159999999997, 228.55579999999998 ],
                [ 240.26559999999995, 229.20579999999998 ],
                [ 260.7836, 229.54181999999997 ],
                [ 278.48959999999994, 230.90439999999998 ],
                [ 293.3846, 233.78929999999997 ],
                [ 293.3846, 233.78929999999997 ],
                [ 289.1488, 241.26199999999997 ],
                [ 289.1488, 241.26199999999997 ],
            ]));
        }
    }

    module MiddleScrollsBlack(height, width)
    {
        len_min = 139.67299999999997;
        len_max = 340.11996;
        width_min = 99.546;
        width_max = 300.796;
        calc_len = len_max - len_min;
        calc_width = width_max - width_min;
        mult = width / calc_width;

        color("black") linear_extrude(height = height) resize([ mult * calc_len, width ])
            translate([ -len_max + (len_max - len_min) / 2, -width_max + (width_max - width_min) / 2 ])
        {

            polygon(bezpath_curve([
                [ 154.59, 146.4 ],
                [ 151.8799, 153.6937 ],
                [ 190.739, 177.71800000000002 ],
                [ 237.493, 206.154 ],
                [ 284.245, 234.588 ],
                [ 324.558, 252.16 ],
                [ 327.546, 249.64 ],
                [ 327.72856, 249.31456 ],
                [ 329.0161, 247.0991 ],
                [ 328.89799999999997, 247.11679999999998 ],
                [ 328.33799, 247.96081999999998 ],
                [ 326.97459999999995, 248.22719999999998 ],
                [ 324.8474, 247.61420999999999 ],
                [ 312.2164, 243.97090999999998 ],
                [ 279.2724, 228.84920999999997 ],
                [ 238.4734, 204.10820999999999 ],
                [ 197.6754, 179.36521 ],
                [ 162.1794, 156.56421 ],
                [ 156.6624, 146.87621 ],
                [ 156.27876999999998, 146.20505 ],
                [ 156.00538, 144.98001 ],
                [ 156.06094, 144.02750999999998 ],
                [ 156.06094, 144.02750999999998 ],
                [ 155.92689, 144.02550999999997 ],
                [ 155.92689, 144.02550999999997 ],
                [ 155.92689, 144.02550999999997 ],
                [ 154.75218999999998, 146.07870999999997 ],
                [ 154.75218999999998, 146.07870999999997 ],
                [ 154.75218999999998, 146.07870999999997 ],
                [ 154.59079999999997, 146.40061999999998 ],
                [ 154.59079999999997, 146.40061999999998 ],
                [ 154.59079999999997, 146.40061999999998 ],
                [ 154.58991999999998, 146.40061999999998 ],
                [ 154.58991999999998, 146.40061999999998 ],
            ]));
            polygon(bezpath_curve([
                [ 318.43762000000004, 263.36957 ], [ 318.43762000000004, 263.36957 ], [ 317.4825000000001, 263.40044 ],
                [ 315.6684, 263.20112 ],           [ 304.3684, 261.95052 ],           [ 270.0794, 245.27612 ],
                [ 229.5064, 220.98812 ],           [ 182.2964, 192.72812000000002 ],  [ 143.3064, 166.97812000000002 ],
                [ 147.53640000000001, 160.24812 ], [ 147.53640000000001, 160.24812 ], [ 148.68730000000002, 158.21352 ],
                [ 148.68730000000002, 158.21352 ], [ 148.68730000000002, 158.21352 ], [ 148.91395000000003, 158.28412 ],
                [ 148.91395000000003, 158.28412 ], [ 145.11025000000004, 169.68912 ], [ 225.86195000000004, 215.86212 ],
                [ 230.61595000000003, 218.80612 ], [ 277.33995000000004, 247.75312 ], [ 316.73095, 264.65711999999996 ],
                [ 320.21695, 260.26412 ],          [ 320.21695, 260.26412 ],          [ 318.94875, 262.44512 ],
                [ 318.94875, 262.44512 ],          [ 318.94875, 262.44512 ],          [ 318.94875, 262.44311999999996 ],
                [ 318.94875, 262.44311999999996 ],

            ]));
            polygon(bezpath_curve([
                [ 330.44, 156.71 ],
                [ 329.70096, 157.89180000000002 ],
                [ 315.697, 162.7213 ],
                [ 295.067, 166.2853 ],
                [ 281.079, 168.4178 ],
                [ 262.833, 170.2408 ],
                [ 240.06300000000002, 170.2629 ],
                [ 218.43, 170.2832 ],
                [ 200.758, 168.7433 ],
                [ 187.37900000000002, 166.93 ],
                [ 165.723, 163.5345 ],
                [ 154.54600000000002, 158.8099 ],
                [ 150.41400000000002, 157.1404 ],
                [ 150.80909000000003, 156.35459 ],
                [ 151.06308, 155.8034 ],
                [ 151.44410000000002, 155.0696 ],
                [ 163.33910000000003, 159.8056 ],
                [ 174.56810000000002, 162.66140000000001 ],
                [ 187.72310000000002, 164.68540000000002 ],
                [ 201.0141, 166.48540000000003 ],
                [ 218.47310000000002, 168.0474 ],
                [ 239.99910000000003, 168.02710000000002 ],
                [ 262.66310000000004, 168.00420000000003 ],
                [ 280.70810000000006, 166.04270000000002 ],
                [ 294.61510000000004, 163.9737 ],
                [ 315.77010000000007, 160.5615 ],
                [ 327.32610000000005, 156.1703 ],
                [ 328.94910000000004, 154.1312 ],
                [ 328.94910000000004, 154.1312 ],
                [ 330.4431000000001, 156.71 ],
                [ 330.4431000000001, 156.71 ],
                [ 330.4431000000001, 156.71 ],
                [ 330.44110000000006, 156.71 ],
                [ 330.44110000000006, 156.71 ],
            ]));
            polygon(bezpath_curve([
                [ 324.0867, 150.9289 ], [ 324.0867, 150.9289 ],           [ 312.6617, 154.9806 ],
                [ 292.5607, 158.1908 ], [ 279.1457, 160.11339999999998 ], [ 262.0887, 161.8341 ],
                [ 240.2957, 161.8553 ], [ 219.5917, 161.8756 ],           [ 202.6767, 160.4803 ],
                [ 189.8107, 158.6062 ], [ 169.3967, 155.9401 ],           [ 158.5317, 151.1308 ],
                [ 154.6147, 149.7286 ], [ 155.0045, 149.05479 ],          [ 155.40136, 148.3863 ],
                [ 155.8088, 147.7151 ], [ 158.8567, 149.24970000000002 ], [ 169.34179999999998, 153.506 ],
                [ 190.0348, 156.4375 ], [ 202.7548, 158.2411 ],           [ 219.6958, 159.5852 ],
                [ 240.2968, 159.564 ],  [ 261.9868, 159.5419 ],           [ 278.84979999999996, 157.7878 ],
                [ 292.1798, 155.8757 ], [ 312.3848, 153.0958 ],           [ 323.2568, 147.92849999999999 ],
                [ 324.9078, 146.6347 ], [ 324.9078, 146.6347 ],           [ 326.3806, 149.0856 ],
                [ 326.3806, 149.0856 ], [ 326.3806, 149.0856 ],           [ 326.3806, 149.0876 ],
                [ 326.3806, 149.0876 ],
            ]));
            polygon(bezpath_curve([
                [ 340.12, 204.22 ],
                [ 340.12, 204.22 ],
                [ 340.12088, 206.6074 ],
                [ 340.12088, 206.6074 ],
                [ 337.51488, 209.72330000000002 ],
                [ 321.17488, 214.43290000000002 ],
                [ 300.68388, 217.7494 ],
                [ 285.08887999999996, 220.1404 ],
                [ 264.75687999999997, 221.9439 ],
                [ 239.42188, 221.9439 ],
                [ 215.35288, 221.9439 ],
                [ 196.15887999999998, 220.22760000000002 ],
                [ 181.27388, 217.94250000000002 ],
                [ 157.74488, 214.51610000000002 ],
                [ 142.69487999999998, 208.51630000000003 ],
                [ 139.67388, 206.7255 ],
                [ 139.67388, 206.7255 ],
                [ 139.68708, 203.9403 ],
                [ 139.68708, 203.9403 ],
                [ 148.76188000000002, 209.9737 ],
                [ 173.34808, 214.3873 ],
                [ 181.60408, 215.7383 ],
                [ 196.39208000000002, 218.00840000000002 ],
                [ 215.47208, 219.7115 ],
                [ 239.42108000000002, 219.7115 ],
                [ 264.63708, 219.7115 ],
                [ 284.85508000000004, 217.9203 ],
                [ 300.35208, 215.5452 ],
                [ 315.05308, 213.42149999999998 ],
                [ 335.99608, 207.8987 ],
                [ 340.11908, 204.22119999999998 ],
                [ 340.11908, 204.22119999999998 ],
                [ 340.11996, 204.22119999999998 ],
                [ 340.11996, 204.22119999999998 ],
            ]));
            polygon(bezpath_curve([
                [ 340.13, 195.7278 ],
                [ 340.13, 195.7278 ],
                [ 340.13088, 198.11520000000002 ],
                [ 340.13088, 198.11520000000002 ],
                [ 337.52488, 201.22940000000003 ],
                [ 321.18487999999996, 205.93890000000002 ],
                [ 300.69388, 209.2552 ],
                [ 285.09887999999995, 211.6462 ],
                [ 264.76687999999996, 213.4497 ],
                [ 239.43187999999998, 213.4497 ],
                [ 215.36288, 213.4497 ],
                [ 196.16887999999997, 211.73520000000002 ],
                [ 181.28387999999998, 209.44830000000002 ],
                [ 157.75487999999999, 206.02370000000002 ],
                [ 142.70487999999997, 200.02380000000002 ],
                [ 139.68388, 198.2323 ],
                [ 139.68388, 198.2323 ],
                [ 139.69708, 195.4471 ],
                [ 139.69708, 195.4471 ],
                [ 148.77188, 201.4796 ],
                [ 173.35808, 205.8941 ],
                [ 181.61408, 207.2431 ],
                [ 196.40208, 209.515 ],
                [ 215.48208, 211.2189 ],
                [ 239.43108, 211.2189 ],
                [ 264.64708, 211.2189 ],
                [ 284.86508000000003, 209.4268 ],
                [ 300.36208, 207.04989999999998 ],
                [ 315.06308, 204.92619999999997 ],
                [ 336.00608, 199.40339999999998 ],
                [ 340.12908, 195.72589999999997 ],
                [ 340.12908, 195.72589999999997 ],
                [ 340.12996, 195.72789999999998 ],
                [ 340.12996, 195.72789999999998 ],
            ]));
            polygon(bezpath_curve([
                [ 323.3, 253.72 ],
                [ 322.44984, 255.0191 ],
                [ 321.5829, 256.3023 ],
                [ 320.7037, 257.5494 ],
                [ 311.262, 260.8787 ],
                [ 296.3847, 264.3739 ],
                [ 290.10670000000005, 265.3934 ],
                [ 277.28270000000003, 268.03569999999996 ],
                [ 257.4417, 269.9874 ],
                [ 239.83270000000005, 269.99629999999996 ],
                [ 201.94270000000006, 269.44156 ],
                [ 170.92770000000004, 262.02439999999996 ],
                [ 156.33670000000006, 255.69729999999996 ],
                [ 156.33670000000006, 255.69729999999996 ],
                [ 155.15940000000006, 253.67319999999995 ],
                [ 155.15940000000006, 253.67319999999995 ],
                [ 155.15940000000006, 253.67319999999995 ],
                [ 155.35165000000006, 253.36892999999995 ],
                [ 155.35165000000006, 253.36892999999995 ],
                [ 155.35165000000006, 253.36892999999995 ],
                [ 157.34825000000006, 254.14327999999995 ],
                [ 157.34825000000006, 254.14327999999995 ],
                [ 183.29625000000007, 263.4266799999999 ],
                [ 212.43925000000007, 267.13027999999997 ],
                [ 240.04625000000004, 267.79527999999993 ],
                [ 257.58425000000005, 267.8569799999999 ],
                [ 275.14125, 265.78527999999994 ],
                [ 289.33825, 263.2461799999999 ],
                [ 311.10925000000003, 258.8840799999999 ],
                [ 319.91225000000003, 255.59617999999992 ],
                [ 322.61325, 254.10567999999992 ],
                [ 322.61325, 254.10567999999992 ],
                [ 323.30026, 253.7202699999999 ],
                [ 323.30026, 253.7202699999999 ],
                [ 323.30026, 253.7202699999999 ],
                [ 323.29938, 253.7202699999999 ],
                [ 323.29938, 253.7202699999999 ],
                [ 328.3392, 245.4703 ],
                [ 328.3613, 245.495 ],
                [ 328.3825, 245.5223 ],
                [ 327.74665, 246.5956 ],
                [ 327.0914, 247.6875 ],
                [ 326.4203, 248.7846 ],
                [ 321.3846, 250.58460000000002 ],
                [ 307.7183, 254.5834 ],
                [ 287.7613, 257.3739 ],
                [ 274.6123, 259.1651 ],
                [ 266.4393, 260.8999 ],
                [ 240.28230000000002, 261.4079 ],
                [ 191.26730000000003, 260.1608 ],
                [ 159.53230000000002, 250.5769 ],
                [ 151.99330000000003, 248.2129 ],
                [ 151.99330000000003, 248.2129 ],
                [ 150.87590000000003, 246.0698 ],
                [ 150.87590000000003, 246.0698 ],
                [ 179.28190000000004, 253.4852 ],
                [ 208.29790000000003, 258.66179999999997 ],
                [ 240.28390000000002, 259.19079999999997 ],
                [ 264.2149, 258.68103999999994 ],
                [ 274.39590000000004, 256.91889999999995 ],
                [ 287.4359, 255.14089999999996 ],
                [ 310.7069, 251.52229999999997 ],
                [ 322.4319, 247.69109999999995 ],
                [ 325.9509, 246.58509999999995 ],
                [ 325.9068, 246.52159999999995 ],
                [ 325.8548, 246.45456999999996 ],
                [ 325.79657, 246.38577999999995 ],
                [ 325.79657, 246.38577999999995 ],
                [ 328.31967, 245.44297999999995 ],
                [ 328.31967, 245.44297999999995 ],
                [ 328.31967, 245.44297999999995 ],
                [ 328.31766999999996, 245.44497999999996 ],
                [ 328.31766999999996, 245.44497999999996 ],
            ]));
            polygon(bezpath_curve([
                [ 243.13, 99.546 ],
                [ 243.13, 99.546 ],
                [ 245.28979999999999, 99.546 ],
                [ 245.28979999999999, 99.546 ],
                [ 245.28979999999999, 99.546 ],
                [ 245.30829999999997, 300.796 ],
                [ 245.30829999999997, 300.796 ],
                [ 245.30829999999997, 300.796 ],
                [ 243.14669999999998, 300.796 ],
                [ 243.14669999999998, 300.796 ],
                [ 243.14669999999998, 300.796 ],
                [ 243.1308, 99.54599999999999 ],
                [ 243.1308, 99.54599999999999 ],
                [ 234.7087, 99.54780000000001 ],
                [ 236.8853, 99.54780000000001 ],
                [ 236.8853, 99.54780000000001 ],
                [ 236.8853, 99.54780000000001 ],
                [ 236.8883, 300.7978 ],
                [ 236.8883, 300.7978 ],
                [ 236.8883, 300.7978 ],
                [ 234.70999999999998, 300.7978 ],
                [ 234.70999999999998, 300.7978 ],
                [ 234.70999999999998, 300.7978 ],
                [ 234.70999999999998, 99.5478 ],
                [ 234.70999999999998, 99.5478 ],
            ]));
            polygon(bezpath_curve([
                [ 239.95, 184.77 ],
                [ 263.33299999999997, 184.7268 ],
                [ 286.02, 186.9854 ],
                [ 304.015, 190.48940000000002 ],
                [ 322.584, 194.2015 ],
                [ 335.652, 198.84500000000003 ],
                [ 340.12, 204.06040000000002 ],
                [ 340.12, 204.06040000000002 ],
                [ 340.115, 206.64270000000002 ],
                [ 340.115, 206.64270000000002 ],
                [ 334.7266, 200.15250000000003 ],
                [ 317.142, 195.39470000000003 ],
                [ 303.597, 192.67470000000003 ],
                [ 285.739, 189.20070000000004 ],
                [ 263.20399999999995, 186.95790000000002 ],
                [ 239.95, 187.00110000000004 ],
                [ 215.41199999999998, 187.04700000000003 ],
                [ 192.563, 189.37090000000003 ],
                [ 174.966, 192.80430000000004 ],
                [ 160.846, 195.60620000000003 ],
                [ 142.01500000000001, 201.17220000000003 ],
                [ 139.66400000000002, 206.66230000000004 ],
                [ 139.66400000000002, 206.66230000000004 ],
                [ 139.66400000000002, 203.97330000000005 ],
                [ 139.66400000000002, 203.97330000000005 ],
                [ 140.95510000000002, 200.17300000000006 ],
                [ 154.977, 194.49410000000006 ],
                [ 174.64800000000002, 190.55630000000005 ],
                [ 192.377, 187.09910000000005 ],
                [ 215.26800000000003, 184.81480000000005 ],
                [ 239.95000000000005, 184.76990000000006 ],
                [ 263.34299999999996, 176.2355 ],
                [ 286.03, 178.495 ],
                [ 304.025, 181.99720000000002 ],
                [ 322.594, 185.71110000000002 ],
                [ 335.662, 190.35280000000003 ],
                [ 340.13, 195.56820000000002 ],
                [ 340.13, 195.56820000000002 ],
                [ 340.125, 198.15050000000002 ],
                [ 340.125, 198.15050000000002 ],
                [ 334.7366, 191.66200000000003 ],
                [ 317.152, 186.9035 ],
                [ 303.60699999999997, 184.1845 ],
                [ 285.74899999999997, 180.70880000000002 ],
                [ 263.21399999999994, 178.466 ],
                [ 239.95999999999998, 178.51090000000002 ],
                [ 215.42199999999997, 178.555 ],
                [ 192.68399999999997, 180.88070000000002 ],
                [ 175.08499999999998, 184.31230000000002 ],
                [ 161.45899999999997, 186.89550000000003 ],
                [ 141.85899999999998, 192.6819 ],
                [ 139.67299999999997, 198.1723 ],
                [ 139.67299999999997, 198.1723 ],
                [ 139.67299999999997, 195.4815 ],
                [ 139.67299999999997, 195.4815 ],
                [ 140.96409999999997, 191.7227 ],
                [ 155.26999999999998, 185.8401 ],
                [ 174.65799999999996, 182.0645 ],
                [ 192.38699999999994, 178.6073 ],
                [ 215.27799999999996, 176.3248 ],
                [ 239.95999999999998, 176.2781 ],
            ]));
            polygon(bezpath_curve([
                [ 239.97, 140.62 ],
                [ 260.987, 140.5644 ],
                [ 281.295, 141.7498 ],
                [ 297.446, 144.6637 ],
                [ 312.487, 147.463 ],
                [ 326.831, 151.6646 ],
                [ 328.882, 153.9241 ],
                [ 328.882, 153.9241 ],
                [ 330.4721, 156.734 ],
                [ 330.4721, 156.734 ],
                [ 325.48400000000004, 153.477 ],
                [ 313.0711, 149.8504 ],
                [ 297.1331, 146.828 ],
                [ 281.12710000000004, 143.8197 ],
                [ 260.8331, 142.8231 ],
                [ 239.93310000000002, 142.8778 ],
                [ 216.21110000000002, 142.79670000000002 ],
                [ 197.78110000000004, 144.049 ],
                [ 181.96410000000003, 146.8069 ],
                [ 165.23610000000002, 149.9369 ],
                [ 153.63010000000003, 154.4084 ],
                [ 150.76710000000003, 156.53300000000002 ],
                [ 150.76710000000003, 156.53300000000002 ],
                [ 152.32540000000003, 153.5626 ],
                [ 152.32540000000003, 153.5626 ],
                [ 157.88850000000002, 150.7245 ],
                [ 166.71540000000005, 147.3034 ],
                [ 181.54840000000002, 144.6329 ],
                [ 197.90540000000001, 141.6449 ],
                [ 216.53140000000002, 140.74880000000002 ],
                [ 239.97140000000002, 140.6201 ],
                [ 239.97140000000002, 140.6201 ],
                [ 239.97052000000002, 140.6201 ],
                [ 239.97052000000002, 140.6201 ],
                [ 260.074, 132.08280000000002 ],
                [ 279.933, 133.20370000000003 ],
                [ 295.413, 135.98630000000003 ],
                [ 307.622, 138.36310000000003 ],
                [ 319.696, 142.07350000000002 ],
                [ 324.117, 145.37550000000002 ],
                [ 324.117, 145.37550000000002 ],
                [ 326.4426, 149.07090000000002 ],
                [ 326.4426, 149.07090000000002 ],
                [ 322.48900000000003, 144.67620000000002 ],
                [ 307.6066, 140.51160000000002 ],
                [ 294.46860000000004, 138.17890000000003 ],
                [ 279.10760000000005, 135.52950000000004 ],
                [ 260.07360000000006, 134.48090000000002 ],
                [ 239.96060000000003, 134.31330000000003 ],
                [ 218.85260000000002, 134.37240000000003 ],
                [ 199.34560000000002, 135.66530000000003 ],
                [ 184.20860000000002, 138.42140000000003 ],
                [ 169.76760000000002, 141.16950000000003 ],
                [ 160.44860000000003, 144.42300000000003 ],
                [ 156.50560000000002, 146.96390000000002 ],
                [ 156.50560000000002, 146.96390000000002 ],
                [ 158.5507, 143.8771 ],
                [ 158.5507, 143.8771 ],
                [ 163.9921, 141.01250000000002 ],
                [ 172.7827, 138.38170000000002 ],
                [ 183.8537, 136.2306 ],
                [ 199.1027, 133.45420000000001 ],
                [ 218.7297, 132.19480000000001 ],
                [ 239.9617, 132.1357 ],
            ]));
            polygon(bezpath_curve([
                [ 239.58, 236.46 ],
                [ 256.66200000000003, 236.71488 ],
                [ 273.42900000000003, 237.42044 ],
                [ 289.613, 240.4384 ],
                [ 289.613, 240.4384 ],
                [ 288.441, 242.5074 ],
                [ 288.441, 242.5074 ],
                [ 273.40999999999997, 239.7328 ],
                [ 257.38599999999997, 238.6709 ],
                [ 239.63799999999998, 238.7574 ],
                [ 216.97499999999997, 238.58013 ],
                [ 194.05299999999997, 240.6968 ],
                [ 174.09699999999998, 246.42419999999998 ],
                [ 167.8002, 248.17659999999998 ],
                [ 157.37599999999998, 252.2248 ],
                [ 156.313, 255.57 ],
                [ 156.313, 255.57 ],
                [ 155.1471, 253.6474 ],
                [ 155.1471, 253.6474 ],
                [ 155.48310999999998, 251.6701 ],
                [ 161.7834, 247.56640000000002 ],
                [ 173.5611, 244.25730000000001 ],
                [ 196.41910000000001, 237.7115 ],
                [ 217.80010000000001, 236.6082 ],
                [ 239.58010000000002, 236.4583 ],
                [ 239.58010000000002, 236.4583 ],
                [ 239.58010000000002, 236.46030000000002 ],
                [ 239.58010000000002, 236.46030000000002 ],
            ]));
            polygon(bezpath_curve([
                [ 258.05319000000003, 228.19442999999998 ],
                [ 258.05319000000003, 228.19442999999998 ],
                [ 276.33019, 229.0129 ],
                [ 294.09519, 232.5318 ],
                [ 294.09519, 232.5318 ],
                [ 292.87459, 234.6855 ],
                [ 292.87459, 234.6855 ],
                [ 276.83259, 231.5008 ],
                [ 261.50559, 230.4389 ],
                [ 240.45959000000002, 230.1153 ],
                [ 217.72459000000003, 230.1567 ],
                [ 193.60859000000002, 231.77779999999998 ],
                [ 171.68159000000003, 238.1525 ],
                [ 164.60249000000002, 240.21450000000002 ],
                [ 152.38459000000003, 244.6727 ],
                [ 151.97759000000002, 248.20250000000001 ],
                [ 151.97759000000002, 248.20250000000001 ],
                [ 150.81169000000003, 246.137 ],
                [ 150.81169000000003, 246.137 ],
                [ 151.07714, 242.9311 ],
                [ 161.65369000000004, 238.749 ],
                [ 171.16969000000003, 235.981 ],
                [ 193.26569000000003, 229.55689999999998 ],
                [ 217.44469000000004, 227.905 ],
                [ 240.35569000000004, 227.8636 ],
            ]));

            polygon(bezpath_curve([
                [ 148.65, 158.29 ],
                [ 154.296, 154.4606 ],
                [ 195.78900000000002, 172.945 ],
                [ 239.205, 199.124 ],
                [ 282.50600000000003, 225.378 ],
                [ 323.882, 255.045 ],
                [ 320.147, 260.597 ],
                [ 320.147, 260.597 ],
                [ 318.9185, 262.5293 ],
                [ 318.9185, 262.5293 ],
                [ 318.9185, 262.5293 ],
                [ 318.35496, 262.9738 ],
                [ 318.35496, 262.9738 ],
                [ 318.47579, 262.88739999999996 ],
                [ 319.09841, 262.12624999999997 ],
                [ 318.29406, 260.0678 ],
                [ 316.44916, 253.99739999999997 ],
                [ 287.09906, 230.5768 ],
                [ 238.40006, 201.17279999999997 ],
                [ 190.92506, 172.86379999999997 ],
                [ 151.35906, 155.80179999999996 ],
                [ 147.40305999999998, 160.67879999999997 ],
                [ 147.40305999999998, 160.67879999999997 ],
                [ 148.65006, 158.28959999999998 ],
                [ 148.65006, 158.28959999999998 ],
                [ 148.65006, 158.28959999999998 ],
                [ 148.64917, 158.28959999999998 ],
                [ 148.64917, 158.28959999999998 ],
            ]));
            polygon(bezpath_curve([
                [ 329.08979, 247.21568 ],
                [ 332.66, 240.165 ],
                [ 294.17400000000004, 211.173 ],
                [ 246.45800000000003, 182.945 ],
                [ 197.64500000000004, 155.279 ],
                [ 162.46400000000003, 138.994 ],
                [ 156.038, 143.85 ],
                [ 156.038, 143.85 ],
                [ 154.61020000000002, 146.4491 ],
                [ 154.61020000000002, 146.4491 ],
                [ 154.5978, 146.59196999999998 ],
                [ 154.6622, 146.27183 ],
                [ 154.96384000000003, 146.039 ],
                [ 156.13234000000003, 145.0195 ],
                [ 158.06904000000003, 145.08826 ],
                [ 158.94304000000002, 145.07237999999998 ],
                [ 170.00804000000002, 145.23818999999997 ],
                [ 201.61004000000003, 159.78137999999998 ],
                [ 245.94904000000002, 185.20038 ],
                [ 265.37704, 196.51538 ],
                [ 328.02004, 236.69137999999998 ],
                [ 327.78104, 247.98937999999998 ],
                [ 327.79784, 248.9604 ],
                [ 327.86134000000004, 249.16057999999998 ],
                [ 327.49619, 249.64128 ],
                [ 327.49619, 249.64128 ],
                [ 329.08979, 247.21768 ],
                [ 329.08979, 247.21768 ],
                [ 329.08979, 247.21768 ],
                [ 329.08979, 247.21568 ],
                [ 329.08979, 247.21568 ],
            ]));
        }
    }

    module MiddleScrolls(height, width)
    {
        mirror([ 0, 1, 0 ])
        {
            difference()
            {
                MiddleScrollsYellow(height = height, width = width);
                MiddleScrollsBlack(height = height, width = width);
            }
           // MiddleScrollsBlack(height = height, width = width);
             MiddleScrollsBlack(height = height, width = width);
        }
    }

    module WhiteDots(length, height)
    {
        cyl(d = length / 5, h = height, anchor = BOTTOM);
        translate([ length / 2, length / 2, 0 ]) cyl(d = length / 5, h = height, anchor = BOTTOM);
        translate([ -length / 2, length / 2, 0 ]) cyl(d = length / 5, h = height, anchor = BOTTOM);
        translate([ length / 2, -length / 2, 0 ]) cyl(d = length / 5, h = height, anchor = BOTTOM);
        translate([ -length / 2, -length / 2, 0 ]) cyl(d = length / 5, h = height, anchor = BOTTOM);
    }

    module BlueDotsShield(width, height, white_dot_height)
    {
        width_shield = width;
        length_shield = width * 7 / 6;
        translate([ 0, -(length_shield - width_shield) / 2, 0 ])
        {
            // blue
            color("#003399")
            {
                difference()
                {
                    union()
                    {
                        Quina(width = width_shield, height);
                    }
                    translate([ 0, 0, -0.5 ]) WhiteDots(width_shield / 2, height + 1);
                }
            }
            color("white") WhiteDots(width_shield / 2, white_dot_height);
        }
    }

    module AllBlueShields(length, height, white_dot_height)
    {
        outer_shield = length / 10;
        inner_layout = outer_shield * 5 / 8;
        shield_width = length / 40;
        BlueDotsShield(shield_width, height, white_dot_height);
        translate([ inner_layout / 2, 0, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ -inner_layout / 2, 0, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ 0, inner_layout / 2, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ 0, -inner_layout / 2, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
    }

    module CastleAndOutline(stroke_width, width)
    {
        color("yellow") linear_extrude(height = height) fill()
            PortugalCastle(stroke_width = stroke_width / 2, width = width);
        color("black") linear_extrude(height = height) PortugalCastle(stroke_width = stroke_width, width = width);
    }

    module AllCastles(length, height)
    {
        outer_shield = length / 5;
        castle_width = length / 40;
        CastleAndOutline(width = castle_width, stroke = 0.2);
    }

    if (border > 0)
    {
        difference()
        {
            cuboid([ length + border, width + border, height ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) cuboid([ length - 0.02, width - 0.02, height + 1 ], anchor = BOTTOM);
        }
    }
    if (background)
    {
        // dark green
        color("#006600") difference()
        {
            translate([ -length / 2, 0, 0 ]) intersection()
            {
                cuboid([ length * 2 / 5, width, height ], anchor = BOTTOM + LEFT);
                translate([ -length / 2, width / 2, 0 ]) mirror([ 0, 1, 0 ])
                    Make3dStripedGrid(width = length, length = width, height = height, spacing = 1.5);
            }
        }
        // red
        color("#FF0000") difference()
        {
            translate([ -length / 10, 0, 0 ]) intersection()
            {
                cuboid([ length * 3 / 5, width, height ], anchor = BOTTOM + LEFT);
                translate([ -length / 2 - 1, -width / 2, 0 ])
                    Make3dStripedGrid(width = length, length = width, height = height, spacing = 1.5);
            }
        }
    }
    translate([ length * 2 / 5 - length / 2, 0, 0 ])
    {
        color("#FFFF00") difference()
        {
            cyl(d = width / 2, h = height, anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) cyl(d = width / 2 - width / 12, h = height + 1, anchor = BOTTOM);
        }
        difference()
        {
            MiddleScrolls(height = height, width = width / 2 + width / 150);
            translate([ 0, 0, -0.5 ]) Quina(length / 5, height + 1);
        }
        color("white") difference()
        {
            Quina(length / 5, height);
            translate([ 0, 0, -0.5 ]) Quina(length / 5 * 19 / 20, height + 1);
        }
        color("#FF0000") difference()
        {
            Quina(length / 5 * 19 / 20, height);
            translate([ 0, 0, -0.5 ]) Quina(length / 5 * 4 / 7, height + 1);
        }
        color("white")
        {
            difference()
            {
                Quina(length / 5 * 4 / 7, height);
                translate([ 0, 0, -0.5 ]) AllBlueShields(length, height + 1, height + 4);
            }
        }
        AllBlueShields(length, height, height);
    }
}