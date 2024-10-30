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
        color("blue") difference()
        {
            translate([ -length / 4, 0, 0 ])
                Make3dStripedGrid(width = length, length = length / 2, height = height, spacing = 1.5);
            translate([ 0, 0, -0.5 ]) CrossBit(height + 2);
        }
    }
    color("yellow") CrossBit(height);
}

module PortugeseFlag(length, height, background = true, border = 0)
{
    width = length * 2 / 3;
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

    module BlueDotsShield(length, height, blue_dot_height)
    {
        width_shield = length / 20;
        length_shield = length * 7 / 120;
        // blue
        color("#003399") translate([ 0, -(length_shield - width_shield) / 2, 0 ])
        {
            cuboid([ width_shield, length_shield / 2, height ], anchor = BOTTOM + FRONT);
            cyl(d = width_shield, h = height, anchor = BOTTOM);
        }
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
            Shield(length * 4 / 7, height);
        }
    }
}