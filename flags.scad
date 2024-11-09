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
// FileGroup: Flags

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
//    background= generate the background (default true)
//    border = size of border to generate (default 0)
module FlagBackgroundAndBorder(background_color, background = true, border = 0)
{
    if (border > 0)
    {
        difference()
        {
            cuboid([ length + border, length / 2 + border, height ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ]) cuboid([ length - 0.02, length / 2 - 0.02, height + 1 ], anchor = BOTTOM);
        }
    }
    if (background)
    {
        color(background_color) difference()
        {
            translate([ -length / 4, 0, 0 ])
                Make3dStripedGrid(width = length, length = length / 2, height = height, spacing = 1.5);
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
// Topics: Flags
// Example:
//   AustralianFlag(100, 5, 4);
// Example:
//   AustralianFlag(100, 5, 4, border = 1);
// Example:
//   AustralianFlag(100, 5, 4, background = false);
module AustralianFlag(length, white_height, red_height, border = 0, background = true)
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
            cuboid([ length + border, length / 2 + border, max(white_height, red_height) ], anchor = BOTTOM);
            translate([ 0, 0, -0.5 ])
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
                    translate([ -length / 4, 0, 0 ]) Make3dStripedGrid(
                        width = length, length = length / 2, height = max(red_height, white_height), spacing = 1.5);
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
module SwedenFlag(length, height, background = true, border = 0)
{
    width = length * 5 / 8;
    line_horiz = width * 2 / 10;
    line_vert = length * 2 / 16;
    module CrossBit(height)
    {
        cuboid([ length, line_horiz, height ], anchor = BOTTOM);
        translate([ -length * 3 / 16, 0, 0 ]) cuboid([ line_vert, width, height ], anchor = BOTTOM);
    }
    FlagBackgroundAndBorder("blue", background = background, border = border)
    {
        CrossBit(height + 2);
        color("yellow") CrossBit(height);
    }
}

module UnitedStatesFlag(length, white_height, red_height, background = true, border = 0)
{
    width = length / 1.9;
    top_bit_width = width * 7 / 16;
    top_bit_length = length * 2 / 5;
    star_offset_width = top_bit_width / 10;
    star_offset_length = top_bit_length / 12;
    stripe = width / 13;
    star = stripe * 4 / 5;
    module StarSection(white_height)
    {
        for (i = [0:1:4])
        {
            for (j = [0:1:8])
            {
                color("white") translate(
                    [ star_offset_width * j, star_offset_length * i + (j % 2 == 1 ? star_offset_length : 0), 0 ])
                    linear_extrude(height = white_height) star(5, star / 2);
            }
        }
        for (j = [0:1:8])
        {
            if (j % 2 == 0)
            {
                color("white") translate([ star_offset_width * j, star_offset_length * 5, 0 ])
                    linear_extrude(height = white_height) star(5, star / 2);
            }
        }
    }
    module Stripes(white_height, red_height)
    {
        difference()
        {
            union()
            {
                for (i = [0:1:5])
                {
                    translate([ stripe * 2 * i, 0, 0 ]) color("red")
                        cuboid([ stripe, length, red_height ], anchor = BOTTOM);
                    translate([ stripe * 2 * i + stripe, 0, 0 ]) color("white")
                        cuboid([ stripe, length, white_height ], anchor = BOTTOM);
                }
                translate([ stripe * 2 * 6, 0, 0 ]) color("red")
                    cuboid([ stripe, length, red_height ], anchor = BOTTOM);
            }
            translate([ 0, 0, -1 ]) cuboid(
                [ top_bit_width + 0.01, top_bit_length + 0.01, max(white_height, red_height) + 2 ], anchor = BOTTOM);
        }
    }
    module MainFlag(white_height, red_height)
    {
        Stripes(white_height = white_height, red_height = red_height);
        StarSection(white_height = white_height);
    }
    FlagBackgroundAndBorder("blue", background = background, border = border)
    {
        CrossBit(height + 2);
        color("yellow") CrossBit(height);
    }
}

module PortugeseFlag(length, height, background = true, border = 0)
{
    width = length * 2 / 3;

    module Quina()
    {
        import("svg/portugal.svg", id = "quina");
    }
    module Shield(length, height)
    {
        width_shield = length / 5;
        length_shield = length * 7 / 30;
        translate([ 0, -(length_shield - width_shield) / 2, 0 ])
        {
            cuboid([ width_shield, length_shield / 2, height ], anchor = BOTTOM + FRONT);
            cyl(d = width_shield, h = height, anchor = BOTTOM);
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
                        cuboid([ width_shield, length_shield / 2, height ], anchor = BOTTOM + FRONT);
                        cyl(d = width_shield, h = height, anchor = BOTTOM);
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
        inner_layout = outer_shield * 3 / 4;
        shield_width = length / 40;
        BlueDotsShield(shield_width, height, white_dot_height);
        translate([ inner_layout / 2, 0, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ -inner_layout / 2, 0, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ 0, inner_layout / 2, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
        translate([ 0, -inner_layout / 2, 0 ]) BlueDotsShield(shield_width, height, white_dot_height);
    }

    module Castle()
    {
        portugal_castle_width = 18.744;
        portugal_castle_length = 20.264;
        resize(portugal_castle_width, portugal_castle_length) import("svg/portugal_castle.svg");
        //        bezpath_curve(MakePath(190.19,154.43,[[0.13493,5.521],[4.0524-6.828],[4.0806-6.8474],[0.0282-0.0185],[4.2314,1.4076],[4.2173,6.8986],
        //        [-8.2978-0.0512]]));
        /*
                    <path
               d="m186.81,147.69-0.68172,6.3447,4.1406,0.009c0.0397-5.2493,3.9739-6.1225,4.0691-6.1031,0.0891-0.005,3.9889,1.1606,4.0929,6.1031h4.1511l-0.74962-6.3932-15.022,0.0379v0.002z"/>
                    <path
               d="m185.85,154.06h16.946c0.35717,0,0.64908,0.35277,0.64908,0.78404,0,0.43039-0.29191,0.78141-0.64908,0.78141h-16.946c-0.35717,0-0.64908-0.35102-0.64908-0.78141,0-0.43127,0.29191-0.78404,0.64908-0.78404z"/>
                    <path
               d="m192.01,154.03c0.0185-3.3126,2.2621-4.2501,2.2736-4.2483,0.00088,0,2.3423,0.96661,2.3609,4.2483h-4.6344"/>
                    <path
               d="m186.21,145.05h16.245c0.34218,0,0.62263,0.31839,0.62263,0.70468,0,0.38717-0.28045,0.70467-0.62263,0.70467h-16.245c-0.34218,0-0.62263-0.31573-0.62263-0.70467,0-0.38629,0.28045-0.70468,0.62263-0.70468z"/>
                    <path
               d="m186.55,146.47h15.538c0.32719,0,0.59529,0.31662,0.59529,0.70379,0,0.38805-0.2681,0.70467-0.59529,0.70467h-15.538c-0.32719,0-0.59529-0.31662-0.59529-0.70467,0-0.38717,0.2681-0.70379,0.59529-0.70379z"/>
                    <path
               d="m191.57,135.88,1.2267,0.002v0.87136h0.89513v-0.89076l1.2567,0.004v0.88723h0.89778v-0.89076h1.2576l-0.002,2.0117c0,0.31574-0.25398,0.52035-0.54854,0.52035h-4.4113c-0.29633,0-0.56972-0.23724-0.5706-0.52652l-0.003-1.9879h0.00088z"/>
                    <path d="m196.19,138.57,0.27691,6.4514-4.3028-0.0159,0.28486-6.4523,3.741,0.0168"/>
                    <path id="cp1" d="m190.94,141.56,0.13141,3.4775-4.1256,0.002,0.11641-3.4793h3.8786-0.00089z"/>
                    <use xlink:href="#cp1" x="10.609"/>
                    <path id="cp2"
               d="m186.3,139.04,1.1994,0.003v0.87224h0.8775v-0.89253l1.2294,0.004v0.889h0.87926v-0.89253l1.2302,0.002-0.002,2.0117c0,0.31398-0.2487,0.51859-0.5362,0.51859h-4.3169c-0.28926,0-0.55824-0.23548-0.55913-0.52564l-0.003-1.9888h0.00088z"/>
                    <use xlink:href="#cp2" x="10.609"/>
                    <path fill="#000" stroke="none"
               d="m193.9,140.61c-0.0265-0.62706,0.87661-0.63411,0.86603,0v1.5364h-0.866v-1.536"/> <path id="cp3"
           fill="#000" stroke="none" d="m188.57,142.84c-0.003-0.6059,0.83693-0.61824,0.82635,0v1.1871h-0.826v-1.187"/>
           <use xlink:href="#cp3" x="10.641"/>*/
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
        color("white") difference()
        {
            Shield(length, height);
            translate([ 0, 0, -0.5 ]) Shield(length * 19 / 20, height + 1);
        }
        color("#FF0000") difference()
        {
            Shield(length * 19 / 20, height);
            translate([ 0, 0, -0.5 ]) Shield(length / 2, height + 1);
        }
        color("white")
        {
            difference()
            {
                Shield(length * 4 / 7, height);
                translate([ 0, 0, -0.5 ]) AllBlueShields(length, height + 1, height + 4);
            }
        }
        AllBlueShields(length, height, height);
        Castle();
    }
}