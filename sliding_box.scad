



















































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

// LibFile: sliding_box.scad
//    This file has all the modules needed to generate a sliding box.

// FileSummary: Sliding box pieces for the sliding boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlidingBox
//   All the pieces for making sliding lids and different types of sliding lids/boxes.

// Module: SlidingLid()
// Description:
//   Creates a sliding lid for a sliding lid box, the children to this module are inserted into the lid.
//   This does all the right things on the edges, uses some
//   wiggle room to add in a buffer and also does a small amount of angling on the ends to make them easier
//   to insert.
// Usage:
//   SlidingLid(width=10, length=30, lid_thickness=3, wall_thickness = 2, size_spacing = 0.2);
// Arguments:
//   width = the width of the box itself
//   length = the length of the box itself
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   size_spacing = how much of an offset to use in generate the slides spacing on all four sides defaults to
//   {{m_piece_wiggle_room}}
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLid(width=100, length=100, lid_thickness=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(width = 100, length = 100, lid_thickness = 3, boundary = 10, radius = 12);
module SlidingLid(width, length, lid_thickness = undef, wall_thickness = undef, size_spacing = m_piece_wiggle_room,
                  lid_rounding = undef, lid_chamfer = undef)
{
    calc_lid_thickness = DefaultValue(lid_thickness, default_lid_thickness);
    calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);
    calc_lid_rounding = DefaultValue(lid_rounding, calc_wall_thickness / 2);
    calc_lid_chamfer = DefaultValue(lid_chamfer, calc_wall_thickness / 6);
    internal_build_lid(width, length, calc_lid_thickness, calc_wall_thickness)
    {
        difference()
        {
            // Lip and raised bit
            union()
            {
                difference()
                {
                    translate([ calc_wall_thickness / 2, calc_wall_thickness / 2, 0 ]) cuboid(
                        [
                            width - 2 * (calc_wall_thickness + size_spacing), length - calc_wall_thickness,
                            calc_lid_thickness
                        ],
                        anchor = BOTTOM + FRONT + LEFT, rounding = calc_lid_rounding,
                        edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                    // Top edge easing.
                    translate([
                        calc_wall_thickness / 2 - size_spacing, calc_wall_thickness / 2 - size_spacing,
                        calc_lid_thickness / 2 -
                        size_spacing
                    ]) linear_extrude(height = calc_lid_thickness + 10) right_triangle([ size_spacing * 2, 15 ]);
                    translate([
                        width - calc_wall_thickness * 2 + size_spacing * 3.2, calc_wall_thickness / 2 - size_spacing,
                        calc_lid_thickness / 2 -
                        size_spacing
                    ]) linear_extrude(height = calc_lid_thickness + 10) xflip()
                        right_triangle([ size_spacing * 2, 15 ]);
                }
                // bottom layer.
                translate([ 0, 0, 0 ]) cuboid(
                    [
                        width - calc_wall_thickness - size_spacing, length - calc_wall_thickness / 2,
                        calc_lid_thickness / 2 -
                        size_spacing
                    ],
                    anchor = BOTTOM + FRONT + LEFT, chamfer = calc_lid_chamfer,
                    edges = [ TOP + LEFT, TOP + RIGHT, TOP + FRONT, FRONT + LEFT, FRONT + RIGHT ]);
            }

            // Edge easing.
            translate([ -size_spacing / 20, -size_spacing, -calc_lid_thickness / 2 ])
                linear_extrude(height = calc_lid_thickness + 10) right_triangle([ size_spacing * 2, 15 ]);
            translate([ width - calc_wall_thickness - size_spacing / 1.1, -size_spacing, -calc_lid_thickness / 2 ])
                linear_extrude(height = calc_lid_thickness + 10) xflip() right_triangle([ size_spacing * 2, 15 ]);
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

// Module: SlidingBoxLidWithLabelAndCustomShape()
// Topics: SlidingBox, SlidingLid
// Description:
//    Lid for a sliding lid box.  This uses the first
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
// Usage: SlidingBoxLidWithLabelAndCustomShape(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    SlidingBoxLidWithLabelAndCustomShape(100, 50, text_width = 70, text_height = 20, text_str = "Frog") {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module SlidingBoxLidWithLabelAndCustomShape(width, length, text_width, text_height, text_str, lid_boundary = 10,
                                            label_radius = 5, label_border = 2, label_offset = 4, label_rotated = false,
                                            layout_width = undef, size_spacing = m_piece_wiggle_room,
                                            lid_thickness = default_lid_thickness, aspect_ratio = 1.0, font = undef,
                                            lid_rounding = undef, wall_thickness = undef, lid_chamfer = undef)
{
    SlidingLid(width, length, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
               lid_rounding = lid_rounding, size_spacing = size_spacing, lid_chamfer = lid_chamfer)
    {
        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, aspect_ratio = aspect_ratio)
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

// Module: SlidingBoxLidWithLabel
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
// Usage:
//    SlidingBoxLidWithLabel(width = 100, length = 100, lid_thickness = 3, text_width = 60, text_height = 30, text_str
//    = "Trains", label_rotated = false);
// Arguments:
//    width = width of the box (outside dimension)
//    length = length of the box (outside dimension)
//    text_width = width of the text section
//    text_height = length of the text section
//    text_str = The string to write
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    label_border = how wide the border strip on the label should be (default 2)
//    label_offset = how far inside the border the label should be (default 4)
//    label_rotated = if the label should be rotated (default false)
//    label_radius = radius of the label bit (default 5)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = how much of an offset to use in generate the slides spacing on all four sides defaults to
//    {{m_piece_wiggle_room}}
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithLabel(
//        width = 100, length = 100, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module SlidingBoxLidWithLabel(width, length, text_width, text_height, text_str, lid_thickness = default_lid_thickness,
                              lid_boundary = 10, shape_width = undef, label_border = 2, label_offset = 4,
                              label_rotated = false, layout_width = undef, shape_type = undef, shape_thickness = undef,
                              wall_thickness = undef, aspect_ratio = undef, size_spacing = m_piece_wiggle_room,
                              lid_chamfer = undef, lid_rounding = undef, font = undef, label_radius = 5,
                              shape_rounding = undef)
{
    SlidingBoxLidWithLabelAndCustomShape(
        width = width, length = length, wall_thickness = wall_thickness, lid_thickness = lid_thickness, font = font,
        text_str = text_str, text_width = text_width, text_height = text_height, label_radius = label_radius,
        label_rotated = label_rotated, layout_width = layout_width, size_spacing = size_spacing,
        aspect_ratio = aspect_ratio, lid_chamfer = lid_chamfer, lid_rounding = lid_rounding,
        lid_boundary = lid_boundary, label_border = label_border, label_offset = label_offset)
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

// Module: MakeBoxWithSlidingLid()
// Description:
//   Makes a box with a sliding lid, this just creates the box itself with the cutouts for the
//   sliding lid pieces.  The children to this will be removed from inside the box and how to add
//   in the cutouts.
//   .
//   The children all start from the edge inside the wall width and up from the floor in the box.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Usage:
//   MakeBoxWithSlidingLid(50,100,20);
// Arguments:
//    width = width of the box (outside width)
//    length = length of the box (outside length)
//    height = height of the box (outside height)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
// Topics: SlidingBox
// Example:
//   MakeBoxWithSlidingLid(50, 100, 20);
module MakeBoxWithSlidingLid(width, length, height, wall_thickness = default_wall_thickness,
                             lid_thickness = default_lid_thickness, floor_thickness = default_floor_thickness,
                             size_spacing = m_piece_wiggle_room)
{
    difference()
    {
        cuboid([ width, length, height ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
               edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        translate([ wall_thickness, -size_spacing / 2, height - lid_thickness ]) cuboid(
            [ width - wall_thickness * 2, length - wall_thickness + size_spacing, lid_thickness + size_spacing / 2 ],
            anchor = BOTTOM + FRONT + LEFT, );
        translate([ wall_thickness / 2, -size_spacing / 2, height - lid_thickness ])
            cuboid([ width - wall_thickness, length - wall_thickness / 2 + size_spacing * 2, lid_thickness / 2 ],
                   anchor = BOTTOM + FRONT + LEFT, chamfer = lid_thickness / 6,
                   edges = [ TOP + LEFT, TOP + RIGHT, TOP + BACK ]);

        // Make everything start from the bottom corner of the box.
        $inner_width = width - wall_thickness * 2;
        $inner_length = length - wall_thickness * 2;
        $inner_height = height - lid_thickness - floor_thickness;
        translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
    }
}