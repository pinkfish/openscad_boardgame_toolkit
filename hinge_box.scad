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

// LibFile: hinge_box.scad
//    This file has all the modules needed to generate a hinge box.

// FileSummary: Hinge box pieces for the hinge boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Hinges
// Description:
//    Types of hinges to make.

// Module: HingeCone()
// Description:
//   Makes the hinge cone for use in hinges, this makes a 45 degree cone with an inner/outer that
//   can be joined with other pieces to make a hinge.
// Topics: Hinges
// Usage: HingeCone(6, 0.5)
// Arguments:
//   r = radius of the cone
//   offset = how far inside the cone to leave space
// Example:
//   HingeCone(6, 0.5);
module HingeCone(r, offset)
{
    difference()
    {
        cylinder(h = r, r1 = r, r2 = 0);
        translate([ 0, 0, -0.01 ]) cylinder(h = r - offset, r1 = r - offset, r2 = 0);
    }
}

// Module: HingeLine()
// Description:
//    Makes a hinge setup in a straight line, has pieces that stick out each side wide enough to hook onto
//    edges within 0.5 of the side.
// Topics: Hinges
// Arguments:
//    length = length of the line to hinge
//    diameter = diameter of the hinge itself
//    offset = how much of a space to leave on the conical holes for the hinge
//    spin = how much to rotate one of the legs (default 0)
// Example:
//    HingeLine(length = 60, diameter = 6, offset = 0.5);
module HingeLine(length, diameter, offset, spin = 90)
{
    num = length / diameter;
    spacing = length / num;

    HingeLineWithSpacingAndNum(diameter = diameter, offset = offset, spin = spin, num = num, spacing = spacing);
}

// Module: HingeLineWithSpacingAndNum()
// Description:
//    Makes a hinge setup in a straight line, has pieces that stick out each side wide enough to hook onto
//    edges within 0.5 of the side.
// Topics: Hinges
// Arguments:
//    num = number of hinge locations
//    spacing = spacing between hinge spots
//    diameter = diameter of the hinge itself
//    offset = how much of a space to leave on the conical holes for the hinge
//    spin = how much to rotate one of the legs (default 0)
// Example:
//    HingeLineWithSpacingAndNum(num = 10, spacing = 6, diameter = 6, offset = 0.5);
module HingeLineWithSpacingAndNum(diameter, num, spacing, offset, spin = 90)
{
    length = num * diameter;
    rotate([ 0, 270, 0 ]) translate([ 0, 0, -length / 2 ])
    {
        difference()
        {
            cylinder(r = diameter / 2, h = length, $fn = 32);
            for (i = [1:1:num - 1])
            {
                translate([ 0, 0, spacing * i ]) mirror([ 0, 0, i % 2 ])
                    HingeCone(diameter / 2 - 0.01, offset, $fn = 32);
                if (i % 2 == 1)
                {
                    difference()
                    {
                        translate([ 0, 0, spacing * i + diameter - diameter - 0.02 ])
                            cylinder(r = diameter, h = diameter + 0.04, $fn = 32);
                        translate([ 0, 0, spacing * i + diameter - diameter - 0.03 ])
                            cylinder(r = diameter / 2 - offset, h = diameter + 0.06, $fn = 32);
                    }
                }
            }
        }
        for (i = [0:1:num - 1])
        {
            if (i % 2 == 1)
            {
                rotate([ 0, 0, spin ]) union()
                {
                    translate([ 0, 0, spacing * i + offset / 2 ]) cylinder(r = diameter / 2, h = diameter - offset);
                    translate([ 0, 0, spacing * i + diameter - diameter / 2 ]) union()
                    {

                        rotate([ 0, 90, 0 ])
                            prismoid(size1 = [ diameter - offset, diameter ], size2 = [ diameter - offset, diameter ],
                                     h = diameter / 2 + offset * 2 + 0.01);
                        translate([ diameter / 2 + offset, 0, 0 ])
                            cuboid([ offset * 2, diameter, diameter + offset * 3 ], chamfer = offset * 2,
                                   edges = [ TOP + LEFT, BOTTOM + LEFT ]);
                    }
                }
            }
            else
            {
                union()
                {
                    translate([ -diameter / 2 - offset * 3 / 2, 0, spacing * i + diameter / 2 ])
                        cuboid([ 1, diameter, diameter + offset * 3 ], chamfer = offset * 2,
                               edges = [ TOP + RIGHT, BOTTOM + RIGHT ]);
                    difference()
                    {
                        translate([ -diameter / 2 - offset, -diameter / 2, spacing * i ])
                            cube([ diameter / 2 + offset, diameter, diameter ]);
                        translate([ 0, 0, spacing * i + (i % 2) * (diameter / 2) - offset * 2 ])
                            cylinder(d = diameter - 0.02, h = diameter * 4, $fn = 32);
                    }
                }
            }
        }
    }
}

// Module: InsetHinge()
// Description:
//   Create a hinge that works and moves in the middle.  Centers the pices back on the line with the
//   middle being the length/2, width2/2 and the diameter/2, the legs stick down a little to make it
//   easier to join onto other parts of the system.
// Topics: Hinges
// Arguments:
//   length = length of the hinge (outside)
//   width = width of the middle pice (outside)
//   diameter = diameter of the round piece in the middle.
//   offset = how much to offset the middle sections, 0.5 is usually good for this
// Usage: InsetHinge(100, 20, 6, 0.5);
// Example:
//   InsetHinge(length = 100, width = 20, diameter = 6, offset = 0.5);
module InsetHinge(length, width, diameter, offset)
{
    num = length / diameter;
    spacing = length / num;

    translate([ 0, -width / 2, 0 ]) difference()
    {
        union()
        {
            translate([ 0, width / 2, 0 ]) cuboid([ length, width - diameter * 2 - offset / 2, diameter ]);
            translate([ 0, diameter / 2, 0 ]) HingeLineWithSpacingAndNum(diameter = diameter, offset = offset,
                                                                         spin = 90, num = num, spacing = spacing);
            translate([ 0, width - diameter / 2, 0 ]) mirror([ 0, 1, 0 ]) HingeLineWithSpacingAndNum(
                diameter = diameter, offset = offset, spin = 90, num = num, spacing = spacing);
        }
        // Make sure the middle bits are supported by cutting out a 45 degree slice in them.
        for (i = [0:1:num - 1])
        {
            rotate([ 0, 270, 0 ]) translate([ -diameter, width / 2, -length / 2 ])
            {
                rotate([ 0, 0, 90 ]) union()
                {
                    translate([ 0, 0, spacing * i + offset / 2 + spacing / 2 ])
                        cuboid([ diameter * 2, diameter * 2, width - diameter * 2 - 0.05 ], spin = 45, orient = LEFT);
                    if (i == 0)
                    {
                        translate([ 0, -diameter, spacing * i + offset / 2 - spacing / 2 ]) cuboid([
                            width - diameter * 2 - 0.05,
                            diameter * 2,
                            diameter * 2,
                        ]);
                    }
                    if (i == num - 1 && num % 2 == 1)
                    {
                        translate([ 0, -diameter, spacing * i + offset / 2 + spacing * 3 / 2 ]) cuboid([
                            width - diameter * 2 - 0.05,
                            diameter * 2,
                            diameter * 2,
                        ]);
                    }
                }
            }
        }
    }
}

// Module: MakeBoxWithInsetHinge()
// Description:
//   Makes a box with an inset hinge on the side, this is a print in place box with a hinge that will
//   make lid hinge onto the top, it is the same height on both sides, child 1 is in the base, child 2
//   is in the lid and child 3+ are lid pieces.
// Usage: MakeBoxAndLidWithInsetHinge(100, 50, 20);
// Topics: Hinges, HingeBox
// Arguments:
//   width = outside with of the box
//   length = outside length of the box
//   height = outside height of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
// Examples:
//   MakeBoxAndLidWithInsetHinge(100, 50, 20);
module MakeBoxAndLidWithInsetHinge(width, length, height, hinge_diameter = 6, wall_thickness = default_wall_thickness,
                                   floor_thickness = default_floor_thickness, hinge_offset = 0.5, gap = 1, side_gap = 3,
                                   print_layer_height = 0.2, lid_thickness = default_lid_thickness)
{
    hinge_width = hinge_diameter * 2 + gap;
    hinge_length = length - side_gap * 2;
    difference()
    {
        union()
        {
            difference()
            {
                cuboid([ width, length, height / 2 ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
                       edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                if ($children > 0)
                {
                    translate([ wall_thickness, wall_thickness, floor_thickness ]) children(0);
                }
            }

            translate([ width + gap, 0, 0 ]) difference()
            {
                cuboid([ width, length, height / 2 ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
                       edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                if ($children > 1)
                {
                    translate([ hinge_diameter, wall_thickness, lid_thickness ]) children(0);
                }
            }
        }
        translate([ width - hinge_diameter - 0.01, side_gap, height / 2 - hinge_diameter - print_layer_height ])
            cube([ hinge_width + 0.02, hinge_length, hinge_diameter + 5 ]);
    }
    translate([ width + gap / 2, hinge_length / 2 + side_gap, height / 2 - hinge_diameter / 2 ]) rotate([ 0, 0, 90 ])
        InsetHinge(length = hinge_length, width = hinge_diameter * 2 + gap, offset = hinge_offset,
                   diameter = hinge_diameter);
}