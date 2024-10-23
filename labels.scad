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

// LibFile: labels.scad
//    This file has all the shared label pieces for the system.

// FileSummary: Shared label pieces.
// FileGroup: Basic

// Includes:
//   include <boardgame_toolkit.scad>

assert(version_num() >= 20190500, "boardgame_toolkit requires OpenSCAD version 2019.05 or later.");

include <BOSL2/rounding.scad>
include <BOSL2/std.scad>
include <base_bgtk.scad>

// Section: Labels
//   Building blocks for making labels.

// Module: MakeStripedGrid()
// Description:
//   Creates a background striped grid, this is used in the label space generation.
// Usage:
//   MakeStripedGrid(20,50);
// Arguments:
//   width = width of the grid space
//   length = length of the grid space
//   bar_width = width of the bars (default 1)
// Topics: Label
// Example:
//   MakeStripedGrid(20, 50);
module MakeStripedGrid(width, length, bar_width = 1)
{
    dx = bar_width * 2;
    x_count = (width + length) / (bar_width + dx);

    intersection()
    {
        square([ width, length ]);
        for (j = [0:x_count])
        {

            translate([ j * (bar_width + dx), 0 ]) rotate([ 0, 0, 45 ]) square([ bar_width, length * 2 ]);
        }
    }
}

// Module: Make3dStripedGrid()
// Description:
//   Creates a background striped grid, this is used in the label space generation.
// Usage:
//   Make3dStripedGrid(20,50);
// Arguments:
//   width = width of the grid space
//   length = length of the grid space
//   bar_width_top = width of the bars (default 1)
//   bar_width_bottom = height of the bar (default bar_width_top)
// Topics: Label
// Example:
//   Make3dStripedGrid(width = 20, length = 50, height = 1);
// Example:
//   Make3dStripedGrid(width = 20, length = 50, height = 0.2, bar_width_bottom = 1);
module Make3dStripedGrid(width, length, height, bar_width_top = 1, bar_width_bottom = undef)
{
    calc_bar_width_bottom = bar_width_bottom == undef ? bar_width_top : bar_width_bottom;
    bar_width = max(bar_width_top, calc_bar_width_bottom);

    dx = bar_width * 2;
    x_count = (width + length) / (bar_width + dx);

    for (j = [0:x_count])
    {

        translate([ j * (bar_width + dx), length / 2, 0 ]) rotate([ 0, 0, 45 ])
            prismoid(size1 = [ calc_bar_width_bottom, length * 2 ], size2 = [ bar_width_top, length * 2 ],
                     height = height, anchor = BOTTOM + LEFT);
    }
}

// Module: MakeStripedLidLabel()
// Description:
//   Makes a label inside a striped grid to use in the lid.  It makes a label with a border and a striped
//   grid in the background to keep the label in plave.
// Usage:
//   MakeStripedLidLabel(20, 80, 2, label="Australia", border = 2, offset = 4);
// Arguments:
//   width = width of the label section
//   length = length of the label section
//   lid_thickness = height of the lid/label
//   label = the text of the label
//   border = how wide the border is around the label (default 2)
//   offset = how far in from the sides the text should be (default 4)
//   font = the font to use for the text (default "Stencil Std:style=Bold")
//   radius = the radius of the corners on the label section (default 5)
//   full_height = full height of the lid (default false)
// Topics: Label
// Example:
//   MakeStripedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia");
// Example:
//   MakeStripedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia", full_height = true);
module MakeStripedLidLabel(width, length, lid_thickness, label, border = 2, offset = 4, font = "Stencil Std:style=Bold",
                           radius = 5, full_height = false)
{
    intersection()
    {
        cuboid(size = [ width, length, lid_thickness ], rounding = radius, edges = "Z", anchor = FRONT + LEFT + BOTTOM);
        union()
        {
            difference()
            {
                cuboid(size = [ width, length, lid_thickness ], rounding = radius, edges = "Z",
                       anchor = FRONT + LEFT + BOTTOM);

                translate([ border, border, -0.5 ])
                    cuboid(size = [ width - border * 2, length - border * 2, lid_thickness + 1 ], rounding = radius,
                           edges = "Z", anchor = FRONT + LEFT + BOTTOM);
            }
            linear_extrude(height = lid_thickness) union()
            {
                // Edge box.
                translate([ offset, offset, 0 ]) resize([ width - offset * 2, length - offset * 2, 0 ], auto = true)
                {
                    text(text = str(label), font = font, size = 10, spacing = 1, halign = "left", valign = "bottom");
                }
            }
            if (full_height)
            {
                Make3dStripedGrid(width = width, length = length, height = lid_thickness, bar_width_bottom = 1,
                                  bar_width_top = 0.2);
            }
            else
            {
                linear_extrude(height = lid_thickness / 2) MakeStripedGrid(width = width, length = length);
            }
        }
    }
}

// Module FingerHoleWall()
// Description:
//   Creater a finger hole cutout with nice rounded edges at the top and a cylinder of the
//   specified radius at the bottom.
// Arguments:
//   radius = radius of the finger hole
//   height = height of the finger hole
//   anchor = anchor for the hole (default CENTER)
//   depth_of_hole = how deep to make the cut through the wall (default 6)
//   rounding_radious = how round to make the top in the wall (default 3)
// Example:
//   FingerHoleWall(10, 20)
// Example:
//   FingerHoleWall(10, 9)
module FingerHoleWall(radius, height, depth_of_hole = 6, rounding_radius = 3, orient = UP, spin = 0)
{
    tmat = reorient(anchor = CENTER, spin = spin, orient = orient, size = [ 1, 1, 1 ]);
    multmatrix(m = tmat) union()
    {
        if (height >= radius + rounding_radius)
        {
            top_height = radius * 2 - height;
            middle_height = radius - top_height;
            translate([ 0, 0, height ])
                cuboid([ radius * 2, depth_of_hole, middle_height ], rounding = -rounding_radius,
                       edges = [ TOP + LEFT, TOP + RIGHT ], $fn = 16, anchor = TOP);
            translate([ 0, 0, 0 ]) ycyl(r = radius, h = depth_of_hole, $fn = 64, anchor = BOTTOM);
        }
        else
        {
            translate([ 0, 0, height ]) rotate([ 90, 0, 0 ]) intersection()
            {
                translate([ 0, -height / 2, 0 ])
                    cuboid([ radius * 2 + rounding_radius * 2, height, depth_of_hole ], anchor = CENTER);
                union()
                {
                    tangents = circle_circle_tangents(rounding_radius,
                                                      [
                                                          radius + rounding_radius,
                                                          -rounding_radius,
                                                      ],
                                                      radius, [ 0, -height + radius ]);
                    for (i = [0:1:1])
                    {
                        mirror([ i, 0, 0 ]) union()
                        {
                            translate([ 0, 0, -depth_of_hole / 2 ]) linear_extrude(height = depth_of_hole) polygon([
                                tangents[3][1], tangents[3][0], [ tangents[3][0][0] + 0.1, 0 ], [ tangents[3][1][0], 0 ]
                            ]);

                            difference()
                            {
                                translate([ radius + rounding_radius, -rounding_radius, -depth_of_hole / 2 - 0.5 ])
                                    difference()
                                {
                                    cuboid([ rounding_radius, rounding_radius, depth_of_hole + 1 ],
                                           anchor = BOTTOM + FRONT + RIGHT);
                                    cyl(r = rounding_radius, h = depth_of_hole + 1, $fn = 32, anchor = BOTTOM);
                                }

                                translate([ 0, 0, -depth_of_hole / 2 - 0.5 ]) linear_extrude(height = depth_of_hole + 1)
                                    polygon([
                                        tangents[3][1], tangents[3][0], [ tangents[3][0][0], height - radius * 2 ],
                                        [ tangents[3][1][0], height - radius * 2 ]
                                    ]);
                            }
                        }
                    }
                    translate([ 0, -height + radius, 0 ]) cyl(r = radius, h = depth_of_hole, $fn = 64);
                }
            }
        }
    }
}

// Module: FingerHoleBase()
// Description:
//    Creates a hole in the floor of the box with a rounding over at the top to allow for picking up of cards
//    and other things.  Center on the side of the wall and the radius of the main section is the offset to the
//    middle.
// Usage: FingerHoldBase(10, 20);
// Arguments:
//    radius = radius of the hole
//    height = height of the wall
//    wall_thickness = this is used as an offset to move in from the wall by this amount to cut through it (default 2)
//    rounding_radius = rounding radius at the top of the hole (default 3)
//    orient = orintation of the hole, from BSOL2 (default UP)
//    spin = spin of the hole, from BSOL2 (default 0)
//    anchor = location to anchor everything (from BSOL2)
// Example:
//    FingerHoleBase(10, 20);
// Example:
//    FingerHoleBase(10, 20, rounding_radius = 7);
module FingerHoleBase(radius, height, rounding_radius = 3, wall_thickness = 2, floor_thickness = 2, orient = UP,
                      spin = 0)
{
    tmat = reorient(anchor = CENTER, spin = spin, orient = orient, size = [ 1, 1, 1 ]);
    multmatrix(m = tmat) union()
    {
        translate([ -rounding_radius, -wall_thickness / 2, height ])
        {
            translate([ 0, wall_thickness / 2, 0 ])
                cyl(r = radius, h = height + floor_thickness * 2, anchor = TOP + LEFT, $fn = 64);
            cuboid([ radius * 2, wall_thickness + 1, height + floor_thickness * 2 ], rounding = -rounding_radius,
                   edges = [ TOP + LEFT, TOP + RIGHT ], anchor = TOP + LEFT, $fn = 32);
            translate([ radius, -wall_thickness / 2 - 0.01, 0 ]) rotate([ 90, 90, 0 ])
                cuboid([ height + floor_thickness * 2, radius * 2, wall_thickness ], rounding = -wall_thickness / 2,
                       anchor = TOP + LEFT, $fn = 32, edges = [ FRONT + TOP, TOP + BACK ]);
        }
    }
}