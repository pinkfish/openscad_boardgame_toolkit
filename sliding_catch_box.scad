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

// LibFile: sliding_catch_box.scad
//    This file has all the modules needed to generate a sliding catch box.

// FileSummary: Sliding catch box pieces for the sliding catch boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlidingCatch
// Description:
//    A lid that slides into a groove on the top and the front to catch, a bit harder
//    to stack but makes a nice simple box and fairly sturdy rather than a sliding lid.
//    The lid is thicker than a sliding lid box.

// Module: MakeBoxWithSlidingCatchLid()
// Topics: SlidingCatch
// Description:
//   Creates a box with a sliding catch lid on the top.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Arguments:
//   width = outside width of the box
//   length = inside width of the box
//   height = outside height of the box
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//   top_thickness = the thickness of the all above the catch (default 2)
// Usage: MakeBoxWithSlidingCatchLid(100, 50, 20);
// Example:
//    MakeBoxWithSlidingCatchLid(100, 50, 20);
module MakeBoxWithSlidingCatchLid(width, length, height, lid_thickness = default_lid_thickness,
                                  wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room,
                                  top_thickness = 2, floor_thickness = default_floor_thickness)
{
    calc_sliding_len = (length - wall_thickness) / 6;
    difference()
    {

        cuboid([ width, length, height ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
               edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        // middle diff.
        translate([ wall_thickness, wall_thickness, floor_thickness ])
            cube([ width - wall_thickness * 2, length - wall_thickness * 2, height ]);

        // Sliding cutouts.
        translate([ -0.5, wall_thickness + calc_sliding_len, height - lid_thickness - top_thickness ])
            cuboid([ width + 1, calc_sliding_len + 1, lid_thickness + size_spacing ], anchor = FRONT + LEFT + BOTTOM,
                   rounding = lid_thickness / 2, edges = [BACK + BOTTOM]);
        translate(
            [ -0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - lid_thickness - top_thickness ])
            cuboid([ width + 1, calc_sliding_len + size_spacing * 2, lid_thickness + top_thickness + size_spacing ],
                   anchor = FRONT + LEFT + BOTTOM, rounding = lid_thickness / 2, edges = [BACK + BOTTOM]);
        // Rounding corners.
        translate([ -0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - top_thickness + size_spacing ])
            cuboid([ width + 1, calc_sliding_len + size_spacing * 2, top_thickness - size_spacing ],
                   anchor = FRONT + LEFT + BOTTOM, rounding = -top_thickness / 2,
                   edges = [ FRONT + BOTTOM, FRONT + TOP, TOP + BACK ], $fn = 32);

        // Second cutout.
        translate([
            -0.5, wall_thickness + length - calc_sliding_len * 2 - size_spacing * 2, height - lid_thickness -
            top_thickness
        ]) cuboid([ width + 1, calc_sliding_len + 1, lid_thickness + size_spacing ], rounding = lid_thickness,
                  anchor = FRONT + LEFT + BOTTOM, edges = [BACK + TOP]);
        translate([ -0.5, length - calc_sliding_len - size_spacing * 2, height - lid_thickness - top_thickness ])
            cuboid([ width + 1, calc_sliding_len + size_spacing * 2 + 1, lid_thickness + top_thickness + size_spacing ],
                   anchor = FRONT + LEFT + BOTTOM, rounding = lid_thickness / 2, edges = [BACK + BOTTOM]);
        // Rounding corners.
        translate([
            -0.5, wall_thickness + length - calc_sliding_len - wall_thickness - size_spacing * 2,
            height - top_thickness +
            size_spacing
        ]) cuboid([ width + 1, wall_thickness + calc_sliding_len + size_spacing * 2, top_thickness - size_spacing ],
                  anchor = FRONT + LEFT + BOTTOM, rounding = -top_thickness / 2,
                  edges = [ FRONT + BOTTOM, FRONT + TOP, TOP + BACK ], $fn = 32);

        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        $inner_width = width - wall_thickness * 2;
        $inner_length = length - wall_thickness * 2;
        $inner_height = height - lid_thickness - floor_thickness;
        intersection()
        {
            translate([ wall_thickness, wall_thickness, floor_thickness ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 2 ]);
            translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
        }
    }
}

// Module: SlidingCatchBoxLid()
// Topics: SlidingCatch
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    top_thickness = the thickness of the all above the catch (default 2)
// Usage: MakeBoxWithSlidingCatchLid(100, 50, 20);
// Example:
//    MakeBoxWithSlidingCatchLid(100, 50, 20);
module SlidingCatchBoxLid(width, length, cap_height = 10, lid_thickness = default_lid_thickness,
                          wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room,
                          top_thickness = 2, fill_middle = true)
{
    calc_sliding_len = (length - wall_thickness) / 6;
    calc_lid_thickness = fill_middle ? lid_thickness + top_thickness : lid_thickness;

    internal_build_lid(width, length, calc_lid_thickness, wall_thickness)
    {
        difference()
        {
            union()
            {
                cube([ width, length - wall_thickness, lid_thickness - size_spacing ]);
                if (fill_middle)
                {
                    translate([ wall_thickness, 0, lid_thickness - 0.1 ])
                        cuboid([ width - wall_thickness * 2 - size_spacing * 2, length, top_thickness + 0.1 ],
                               anchor = FRONT + LEFT + BOTTOM, rounding = top_thickness / 2, edges = TOP, $fn = 32);
                }
            }
            // Front piece.
            translate([ -1, -1, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1 ]);
            translate([ width - wall_thickness - size_spacing, -1, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1 ]);
            // Middle piece.
            translate([ -1, calc_sliding_len * 2, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len * 2, lid_thickness + 1 ]);
            translate([ width - wall_thickness - size_spacing, calc_sliding_len * 2, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len * 2, lid_thickness + 1 ]);

            // End piece.
            translate([ -1, calc_sliding_len * 5, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1 ]);
            translate([ width - wall_thickness - size_spacing, calc_sliding_len * 5, -0.5 ])
                cube([ wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1 ]);
        }
        if ($children > 0)
        {
            translate([ wall_thickness, 0, 0 ]) children(0);
        }
        if ($children > 1)
        {
            translate([ wall_thickness, 0, 0 ]) children(1);
        }
        if ($children > 2)
        {
            translate([ wall_thickness, 0, 0 ]) children(2);
        }
        if ($children > 3)
        {
            translate([ wall_thickness, 0, 0 ]) children(3);
        }
        if ($children > 4)
        {
            translate([ wall_thickness, 0, 0 ]) children(4);
        }
        if ($children > 5)
        {
            translate([ wall_thickness, 0, 0 ]) children(5);
        }
    }
}

// Module: SlidingCatchBoxLidWithLabel()
// Topics: SlidingCatch
// Description:
//    Lid for a sliding catch with a label on top of it.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    top_thickness = thickness of the top above the lid (default 1)
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    label_radius = radius of the label corners (default 12)
//    border= border of the item (default 2)
//    offset = offset in from the edge for the label (default 4)
//    label_rotated = if the label is rotated (default false)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
// Usage: SlidingCatchBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    SlidingCatchBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
module SlidingCatchBoxLidWithLabel(width, length, text_width, text_height, text_str, lid_boundary = 10,
                                   wall_thickness = default_wall_thickness, label_radius = 12, border = 2, offset = 4,
                                   label_rotated = false, layout_width = undef, shape_width = undef, shape_type = undef,
                                   shape_thickness = undef, aspect_ratio = undef, size_spacing = m_piece_wiggle_room,
                                   lid_thickness = default_lid_thickness, top_thickness = 2, fill_middle = true)
{
    calc_lid_thickness = fill_middle ? lid_thickness + top_thickness : lid_thickness;

    SlidingCatchBoxLid(width = width, length = length, top_thickness = top_thickness, wall_thickness = wall_thickness,
                       lid_thickness = lid_thickness, size_spacing = m_piece_wiggle_room)
    {
        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width - wall_thickness * 2 - size_spacing * 2, length = length - wall_thickness,
                         lid_thickness = calc_lid_thickness, boundary = lid_boundary, layout_width = layout_width,
                         shape_type = shape_type, shape_width = shape_width, shape_thickness = shape_thickness,
                         aspect_ratio = aspect_ratio);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = calc_lid_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = calc_lid_thickness,
                                    label = text_str, border = border, offset = offset);
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