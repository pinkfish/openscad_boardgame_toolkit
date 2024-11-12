











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
//   SlidingLid(width=10, length=30, lid_thickness=3, wall_thickness = 2, lid_size_spacing = 0.2);
// Arguments:
//   width = the width of the box itself
//   length = the length of the box itself
//   lid_thickness = the height of the lid (defaults to 3)
//   wall_thickness = how wide the side walls are (defaults to 2)
//   lid_size_spacing = how much of an offset to use in generate the slides spacing on all four sides defaults to
//   {{m_piece_wiggle_room}}
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLid(width=100, length=100, lid_thickness=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(width = 100, length = 100, lid_thickness = 3, boundary = 10, radius = 12);
module SlidingLid(width, length, lid_thickness = 3, wall_thickness = 2, lid_size_spacing = m_piece_wiggle_room)
{
    internal_build_lid(width, length, lid_thickness, wall_thickness)
    {
        difference()
        {
            // Lip and raised bit
            union()
            {
                difference()
                {
                    translate([ wall_thickness / 2, wall_thickness / 2, 0 ]) cuboid(
                        [ width - 2 * (wall_thickness + lid_size_spacing), length - wall_thickness, lid_thickness ],
                        anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness / 2,
                        edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                    // Top edge easing.
                    translate([
                        wall_thickness / 2 - lid_size_spacing, wall_thickness / 2 - lid_size_spacing,
                        lid_thickness / 2 -
                        lid_size_spacing
                    ]) linear_extrude(height = lid_thickness + 10) right_triangle([ lid_size_spacing * 2, 15 ]);
                    translate([
                        width - wall_thickness * 2 + lid_size_spacing * 3.2, wall_thickness / 2 - lid_size_spacing,
                        lid_thickness / 2 -
                        lid_size_spacing
                    ]) linear_extrude(height = lid_thickness + 10) xflip() right_triangle([ lid_size_spacing * 2, 15 ]);
                }
                // bottom layer.
                translate([ 0, 0, 0 ]) cuboid(
                    [
                        width - wall_thickness - lid_size_spacing, length - wall_thickness / 2, lid_thickness / 2 -
                        lid_size_spacing
                    ],
                    anchor = BOTTOM + FRONT + LEFT, chamfer = lid_thickness / 6,
                    edges = [ TOP + LEFT, TOP + RIGHT, TOP + FRONT, FRONT + LEFT, FRONT + RIGHT ]);
            }

            // Edge easing.
            translate([ -lid_size_spacing / 20, -lid_size_spacing, -lid_thickness / 2 ])
                linear_extrude(height = lid_thickness + 10) right_triangle([ lid_size_spacing * 2, 15 ]);
            translate([ width - wall_thickness - lid_size_spacing / 1.1, -lid_size_spacing, -lid_thickness / 2 ])
                linear_extrude(height = lid_thickness + 10) xflip() right_triangle([ lid_size_spacing * 2, 15 ]);
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
//    lid_thickness = height of the lid (default 3)
//    wall_thickness = thickness of the walls (default 2)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (default 4)
//    label_rotated = if the label should be rotated (default false)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    lid_size_spacing = how much of an offset to use in generate the slides spacing on all four sides defaults to
//    {{m_piece_wiggle_room}}
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithLabel(
//        width = 100, length = 100, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module SlidingBoxLidWithLabel(width, length, text_width, text_height, text_str, lid_thickness = 3, lid_boundary = 10,
                              shape_width = undef, border = 2, offset = 4, label_rotated = false, layout_width = undef,
                              shape_type = undef, shape_thickness = undef, wall_thickness = 2, aspect_ratio = undef,
                              lid_size_spacing = m_piece_wiggle_room)
{
    SlidingLid(width, length, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
               lid_size_spacing = lid_size_spacing)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness, aspect_ratio = aspect_ratio);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_thickness ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_thickness);
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

// Module: MakeHexBoxWithSlidingLid()
// Description:
//   Creates a box with a specific number of hex spaces given the rows/cols and width of the pieces.  Useful
//   for making 18xx style boxes quickly.  Children to this are the same as children to the
//   {{MakeBoxWithSlidingLid()}}.
//   .
//   This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.
//   .
// See also: SlidingLidForHexBox(), SlidingLidWithLabelForHexBox()
// Usage:
//   MakeHexBoxWithSlidingLid(5, 7, 19, 1, 29);
// Arguments:
//   rows = number of rows to generate
//   cols = number of cols to generate
//   height = height of the box itsdle (outside height)
//   push_block_height = height of the raised bit in the middle to make removing easier
//   lid_thickness = height of the lid (defaults to 3)
//   wall_thickness = thickness of the walls (defaults to 2)
//   spacing = spacing between the hexes
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//   MakeHexBoxWithSlidingLid(rows = 5, cols = 2, height = 10, push_block_height = 0.75, tile_width = 29);
module MakeHexBoxWithSlidingLid(rows, cols, height, push_block_height, tile_width, lid_thickness = 3,
                                wall_thickness = 2, spacing = 0)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(rows * radius * 2 + wall_thickness * 2, cols * apothem * 2 + wall_thickness * 2, height,
                          lid_thickness = lid_thickness)
    {
        HexGridWithCutouts(rows = rows, cols = cols, height = height, tile_width = tile_width, spacing = spacing,
                           wall_thickness = wall_thickness);
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

// Module: SlidingLidForHexBox()
// Description:
//   Creates a sliding lid for use with a hex box, sets up the sizes correctly to match the
//   the hex row/col set.
// See also: MakeHexBoxWithSlidingLid(), SlidingLidWithLabelForHexBox()
// Usage:
//   SlidingLidForHexBox(5, 7, 29);
// Arguments:
//   rows = number of rows to generate
//   cols = number of cols to generate
//   tile_width = width of the tiles
//   lid_thickness = height of the lid (defaults to 3)
//   wall_thickness = thickness of the walls (defaults to 2)
//   spacing = spacing between the hexes
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//   SlidingLidForHexBox(rows = 5, cols = 2, tile_width = 29);
module SlidingLidForHexBox(rows, cols, tile_width, lid_thickness = 3, wall_thickness = 2, spacing = 0)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    SlidingLid(width = rows * radius * 2 + wall_thickness * 2, length = cols * apothem * 2 + wall_thickness * 2,
               lid_thickness = lid_thickness)
    {
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

// Module: SlidingLidWithLabelForHexBox()
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
//   .
// See also: MakeHexBoxWithSlidingLid()
// Usage:
//    SlidingLidWithLabelForHexBox(rows = 3, cols = 4, tile_width = 29, lid_thickness = 3, text_width = 60, text_height
//    = 30, text_str = "Trains", label_rotated = false);
// Arguments:
//    rows = number of rows to generate
//    cols = number of cols to generate
//    tile_width = width of the tiles
//    lid_thickness = height of the lid (defaults to 3)
//    wall_thickness = thickness of the walls (defaults to 2)
//    spacing = spacing between the hexes
//    text_width = width of the text section
//    text_height = length of the text section
//    text_str = The string to write
//    lid_thickness = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (degault 4)
//    label_rotated = if the label should be rotated (default false)
//    wall_thickness = how wide the walls are (default 2)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//    SlidingLidWithLabelForHexBox(
//        cols = 3, rows = 4, tile_width = 29, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module SlidingLidWithLabelForHexBox(rows, cols, tile_width, text_width, text_height, text_str, lid_thickness = 3,
                                    lid_boundary = 10, label_radius = 12, border = 2, offset = 4, label_rotated = false,
                                    wall_thickness = 2, layout_width = undef, shape_width = undef, shape_type = undef,
                                    shape_thickness = undef, aspect_ratio = undef)
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);
    width = rows * radius * 2 + wall_thickness * 2;
    length = cols * apothem * 2 + wall_thickness * 2;

    SlidingLid(width, length, lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness, aspect_ratio = undef);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_thickness ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_thickness);
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

// Module: MakeBoxWithSlidingLid()
// Description:
//   Makes a box with a sliding lid, this just creates the box itself with the cutouts for the
//   sliding lid pieces.  The children to this will be removed from inside the box and how to add
//   in the cutouts.
//   .
//   The children all start from the edge inside the wall width and up from the floor in the box.
// Usage:
//   MakeBoxWithSlidingLid(50,100,20);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = thickness of the walls (default 2)
//   lid_thickness = height of the lid (default 3)
//   floor_thickness = thickness of the floor (default 2)
// Topics: SlidingBox
// Example:
//   MakeBoxWithSlidingLid(50, 100, 20);
module MakeBoxWithSlidingLid(width, length, height, wall_thickness = 2, lid_thickness = 3, floor_thickness = 2,
                             lid_size_spacing = m_piece_wiggle_room)
{
    difference()
    {
        cuboid([ width, length, height ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
               edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        translate([ wall_thickness, -lid_size_spacing / 2, height - lid_thickness ]) cuboid(
            [
                width - wall_thickness * 2, length - wall_thickness + lid_size_spacing,
                lid_thickness + lid_size_spacing / 2
            ],
            anchor = BOTTOM + FRONT + LEFT, );
        translate([ wall_thickness / 2, -lid_size_spacing / 2, height - lid_thickness ])
            cuboid([ width - wall_thickness, length - wall_thickness / 2 + lid_size_spacing * 2, lid_thickness / 2 ],
                   anchor = BOTTOM + FRONT + LEFT, chamfer = lid_thickness / 6,
                   edges = [ TOP + LEFT, TOP + RIGHT, TOP + BACK ]);

        // Make everything start from the bottom corner of the box.
        translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
    }
}