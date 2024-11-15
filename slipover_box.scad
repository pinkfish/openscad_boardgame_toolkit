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

// LibFile: slipover_box.scad
//    This file has all the modules needed to generate a slipover box.

// FileSummary: Slipover box pieces for the slipover boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlipBox
// Description:
//    A box that slips over the outside of an inner box.

// Module: MakeBoxWithSlipoverLid()
// Topics: SlipoverBox
// Description:
//   Makes the inside of the slip box, this will take a second lid that slides over the outside of the box.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Usage: MakeBoxWithSlipoverLid(100, 50, 10);
// Arguments:
//    width = outside width of the box
//    height = outside height of the box
//    foot = how big the foot should be around the bottom of the box (default 0)
//    size_spacing = amount of wiggle room to put into the model when making it (default {{m_piece_wiggle_room}})
//    wall_height = height of the wall if not set (default height - wall_thickness*2 - size_spacing*2)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
// Example:
//   MakeBoxWithSlipoverLid(100, 50, 10);
module MakeBoxWithSlipoverLid(width, length, height, wall_thickness = default_wall_thickness, foot = 0,
                              size_spacing = m_piece_wiggle_room, wall_height = undef,
                              floor_thickness = default_floor_thickness, lid_thickness = default_lid_thickness)
{
    wall_height_calc = wall_height == undef ? height - lid_thickness - size_spacing : wall_height;
    difference()
    {
        union()
        {
            translate([ wall_thickness + size_spacing, wall_thickness + size_spacing, 0 ]) cuboid(
                [
                    width - wall_thickness * 2 - size_spacing * 2, length - wall_thickness * 2 - size_spacing * 2,
                    wall_height_calc
                ],
                anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
                edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
            if (foot > 0)
            {
                cuboid([ width, length, foot ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
                       edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
            }
        }

        $inner_width = width - wall_thickness * 4;
        $inner_length = length - wall_thickness * 4;
        $inner_height = height - lid_thickness - floor_thickness;
        translate([ wall_thickness * 2, wall_thickness * 2, floor_thickness ]) children();
    }
}

// Module: SlipoverBoxLid()
// Topics: SlipoverBox
// Description:
//   Make a box with a slip lid, a lid that slips over the outside of a box.
// Usage: SlipBoxLid(100, 50, 10);
// Arguments:
//   width = width of the lid (outside width)
//   length = of the lid (outside length)
//   height = height of the lid (outside height)
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
// Example:
//   SlipoverBoxLid(100, 50, 10);
module SlipoverBoxLid(width, length, height, lid_thickness = default_lid_thickness,
                      wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room, foot = 0,
                      finger_hole_length = false, finger_hole_width = true)
{
    foot_offset = foot > 0 ? foot + size_spacing : 0;
    translate([ 0, length, height - foot ]) rotate([ 180, 0, 0 ])
    {
        union()
        {
            translate([ 0, 0, height - foot_offset - lid_thickness ])
            {
                internal_build_lid(width, length, wall_thickness, wall_thickness)
                {
                    // Top piece
                    cuboid([ width, length, lid_thickness ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
                           edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                    if ($children > 0)
                    {
                        children(0);
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
            finger_height = min(10, (height - foot_offset - lid_thickness) / 2);
            difference()
            {
                cuboid([ width, length, height - foot_offset ], anchor = BOTTOM + FRONT + LEFT,
                       rounding = wall_thickness, edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                translate([ wall_thickness, wall_thickness, -0.5 ])
                    cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 1 ]);
                if (finger_hole_length)
                {
                    translate([ width / 2, 0, finger_height - 0.01 ]) mirror([ 0, 0, 1 ])
                        FingerHoleWall(radius = 7, height = finger_height);
                    translate([ width / 2, length, finger_height - 0.01 ]) mirror([ 0, 0, 1 ])
                        FingerHoleWall(radius = 7, height = finger_height);
                }
                if (finger_hole_width)
                {
                    translate([ 0, length / 2, finger_height - 0.01 ]) mirror([ 0, 0, 1 ]) rotate([ 0, 0, 90 ])
                        FingerHoleWall(radius = 7, height = finger_height);
                    translate([ width, length / 2, finger_height - 0.01 ]) mirror([ 0, 0, 1 ]) rotate([ 0, 0, 90 ])
                        FingerHoleWall(radius = 7, height = finger_height);
                }
            }
        }
    }
}

// Module: SlipoverLidWithLabel()
// Topics: SlipoverBox
// Usage: SlipoverLidWithLabel(20, 100, 10, text_width = 50, text_height = 20, text_str = "Marmoset", shape_type =
// SHAPE_TYPE_CIRCLE, layout_width = 10, shape_width = 14) Arguments:
//   width = width of the lid (outside width)
//   length = of the lid (outside length)
//   height = height of the lid (outside height)
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
//   label_radius = radius of the label corners (default 12)
//   border= border of the item (default 2)
//   offset = offset in from the edge for the label (default 4)
//   label_rotated = if the label is rotated (default false)
//   layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//   shape_width = width of the shape (default {{default_lid_shape_width}})
//   shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//   aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
// Example:
//   SlipoverLidWithLabel(20, 100, 10, text_width = 50, text_height = 20, text_str = "Marmoset",
//      shape_type = SHAPE_TYPE_CIRCLE, layout_width = 10, shape_width = 14, label_rotated = true);
module SlipoverLidWithLabel(width, length, height, text_width, text_height, text_str, lid_boundary = 10,
                            wall_thickness = default_wall_thickness, label_radius = 12, border = 2, offset = 4,
                            label_rotated = false, foot = 0, layout_width = undef, shape_width = undef,
                            shape_type = undef, shape_thickness = undef, aspect_ratio = undef,
                            size_spacing = m_piece_wiggle_room, lid_thickness = default_lid_thickness,
                            finger_hole_length = false, finger_hole_width = true)
{
    SlipoverBoxLid(width = width, length = length, height = height, wall_thickness = wall_thickness, foot = foot,
                   lid_thickness = lid_thickness, finger_hole_length = finger_hole_length,
                   finger_hole_width = finger_hole_width)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness, aspect_ratio = aspect_ratio);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        if ($children > 0)
        {
            children(0);
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