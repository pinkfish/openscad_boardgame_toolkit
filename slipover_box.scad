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
//   lid_rounding = how much to round the lid (default wall_thickness)
// Example:
//   SlipoverBoxLid(100, 50, 10);
module SlipoverBoxLid(width, length, height, lid_thickness = default_lid_thickness,
                      wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room, foot = 0,
                      finger_hole_length = false, finger_hole_width = true, lid_rounding = undef)
{
    foot_offset = foot > 0 ? foot + size_spacing : 0;
    calc_lid_rounding = DefaultValue(lid_rounding, wall_thickness);
    translate([ 0, length, height - foot ]) rotate([ 180, 0, 0 ])
    {
        union()
        {
            translate([ 0, 0, height - foot_offset - lid_thickness ])
            {
                internal_build_lid(width, length, lid_thickness, wall_thickness, size_spacing = size_spacing)
                {
                    // Top piece
                    cuboid([ width, length, lid_thickness ], anchor = BOTTOM + FRONT + LEFT,
                           rounding = calc_lid_rounding,
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
                       rounding = calc_lid_rounding,
                       edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
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

// Module: SlipoverLidWithLabelAndCustomShape()
// Topics: SlipoverBox
// Description:
//    Lid for a slipover box.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    width = outside width of the box
//    length = outside length of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    label_radius = radius of the label corners (default 5)
//    label_border = border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    label_rotated = if the label is rotated (default false)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
// Usage: SlipoverLidWithLabelAndCustomShape(100, 50, 20, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    SlipoverLidWithLabelAndCustomShape(100, 50, 20, text_width = 70, text_height = 20, text_str = "Frog") {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module SlipoverLidWithLabelAndCustomShape(width, length, height, text_width, text_height, text_str, lid_boundary = 10,
                                          label_radius = 5, label_border = 2, label_offset = 4, label_rotated = false,
                                          layout_width = undef, size_spacing = m_piece_wiggle_room,
                                          lid_thickness = default_lid_thickness, aspect_ratio = 1.0, font = undef,
                                          lid_rounding = undef, wall_thickness = default_wall_thickness, foot = 0,
                                          finger_hole_length = false, finger_hole_width = true,
                                          lid_pattern_dense = false, lid_dense_shape_edges = 6)
{
    SlipoverBoxLid(width, length, height, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
                   lid_rounding = lid_rounding, size_spacing = size_spacing, foot = foot,
                   finger_hole_length = finger_hole_length, finger_hole_width = finger_hole_width)
    {
        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, aspect_ratio = aspect_ratio, dense = lid_pattern_dense,
                         dense_shape_edges = lid_dense_shape_edges)
        {
            if ($children > 0)
            {
                children(0);
            }
            else
            {
                square([ 10, 10 ]);
            }
        }
        MakeLidLabel(width = width, length = length, text_width = text_width, text_height = text_height,
                     lid_thickness = lid_thickness, border = label_border, offset = label_offset, full_height = true,
                     font = font, label_rotated = label_rotated, text_str = text_str, label_radius = label_radius);

        // Fingernail pull
        intersection()
        {
            cube([ width - label_border, length - label_border, lid_thickness ]);
            translate([ (width) / 2, length - label_border - 3, 0 ]) SlidingLidFingernail(lid_thickness);
        }

        // Don't include the first child since is it used for the lid shape.
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
        if ($children > 6)
        {
            children(6);
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
//   label_radius = radius of the label corners (default 5)
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
                            wall_thickness = default_wall_thickness, label_radius = 5, label_border = 2,
                            label_offset = 4, label_rotated = false, foot = 0, layout_width = undef,
                            shape_width = undef, shape_type = undef, shape_thickness = undef, aspect_ratio = undef,
                            size_spacing = m_piece_wiggle_room, lid_thickness = default_lid_thickness,
                            finger_hole_length = false, finger_hole_width = true, font = undef, lid_rounding = undef,
                            shape_rounding = default_lid_shape_rounding)
{
    SlipoverLidWithLabelAndCustomShape(
        width = width, length = length, height = height, wall_thickness = wall_thickness, lid_thickness = lid_thickness,
        font = font, text_str = text_str, text_width = text_width, text_height = text_height,
        label_radius = label_radius, label_rotated = label_rotated, layout_width = layout_width,
        size_spacing = size_spacing, aspect_ratio = aspect_ratio, lid_rounding = lid_rounding,
        lid_boundary = lid_boundary, label_border = label_border, label_offset = label_offset,
        finger_hole_length = finger_hole_length, finger_hole_width = finger_hole_width, foot = foot,
        lid_pattern_dense = IsDenseShapeType(shape_type), lid_dense_shape_edges = DenseShapeEdges(shape_type))
    {
        ShapeByType(shape_type = shape_type, shape_width = shape_width, shape_thickness = shape_thickness,
                    shape_aspect_ratio = aspect_ratio, rounding = shape_rounding);

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
        if ($children > 6)
        {
            children(6);
        }
    }
}