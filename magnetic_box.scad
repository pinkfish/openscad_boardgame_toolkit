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

// LibFile: magnetic_box.scad
//    This file has all the modules needed to generate a magnetic box.

// FileSummary: Magnetic box pieces for the magnetic boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: MagneticLid
// Description:
//   Lid using magnets to hold the top and bottom together.

// Module: MakeBoxWithMagneticLid
// Description:
//   Makes a box with holes for the round magnets in the corners.
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    magnet_diameter = diameter of the magnet
//    magnet_thickness = thickness of the magnet
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1);
module MakeBoxWithMagneticLid(width, length, height, magnet_diameter, magnet_thickness,
                              lid_thickness = default_lid_thickness, magnet_border = 1.5,
                              wall_thickness = default_wall_thickness, floor_thickness = default_floor_thickness)
{
    difference()
    {
        cuboid([ width, length, height - lid_thickness ], anchor = BOTTOM + FRONT + LEFT, rounding = wall_thickness,
               edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        translate([
            magnet_diameter / 2 + magnet_border, magnet_diameter / 2 + magnet_border, height - lid_thickness -
            magnet_thickness
        ]) cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
        translate([
            width - magnet_diameter / 2 - magnet_border, magnet_diameter / 2 + magnet_border, height - lid_thickness -
            magnet_thickness
        ]) cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
        translate([
            width - magnet_diameter / 2 - magnet_border, length - magnet_diameter / 2 - magnet_border,
            height - lid_thickness -
            magnet_thickness
        ]) cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
        translate([
            magnet_diameter / 2 + magnet_border, length - magnet_diameter / 2 - magnet_border, height - lid_thickness -
            magnet_thickness
        ]) cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
        translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
    }
}

// Module: MakeBoxWithMagneticLidInsideSpace()
// Description:
//   Makes the inside space template for the box so that it can used to intersect to pull out the corners
//   for the magnet safely.
// Usage: MakeBoxWithMagneticLidInsideSpace(100, 20, 20, 4, 1);
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    magnet_diameter = diameter of the magnet
//    magnet_thickness = thickness of the magnet
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    full_height = if the cyclinder should be the full height of the box (default true)
//    magnet_border = how far around the edges of the magnet the space should be (default 1.5)
// Example:
//    MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness =
//    1);
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1)
//      MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness =
//      1);
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1)
//      MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5,
//      magnet_thickness = 1, full_height = false);
module MakeBoxWithMagneticLidInsideSpace(width, length, height, magnet_diameter, magnet_thickness,
                                         lid_thickness = default_lid_thickness, magnet_border = 1.5,
                                         wall_thickness = default_wall_thickness,
                                         floor_thickness = default_floor_thickness, full_height = false)
{
    module make_side_cylinder(box_size)
    {
        union()
        {
            actual_height = full_height ? height - lid_thickness - floor_thickness : box_size;
            if (full_height)
            {
                offset = wall_thickness;
                translate([
                    -offset + box_size / 2, -offset + box_size / 2, height - lid_thickness - floor_thickness -
                    actual_height
                ]) cyl(h = actual_height, d = box_size, anchor = BOTTOM, $fn = 32);
            }
            else
            {
                offset = wall_thickness + box_size / 2 - wall_thickness;
                translate([
                    -wall_thickness + box_size / 2, -wall_thickness + box_size / 2,
                    height - lid_thickness - floor_thickness - magnet_thickness * 1.5
                ]) cyl(h = magnet_thickness * 1.5, d = box_size, anchor = BOTTOM, $fn = 32);
                translate([
                    -offset + box_size / 2, -offset + box_size / 2,
                    height - lid_thickness - floor_thickness - actual_height - magnet_thickness * 1.5
                ]) cyl(h = actual_height + 0.01, d2 = box_size, d1 = full_height ? box_size : 0, anchor = BOTTOM,
                       $fn = 32, shift = [ box_size / 2 - wall_thickness, box_size / 2 - wall_thickness ]);
            }
            side_radius = box_size / 2 - wall_thickness;
            echo(side_radius);
            if (side_radius > 0 && full_height)
            {
                difference()
                {

                    translate([
                        -wall_thickness + box_size, -wall_thickness + box_size / 2 - side_radius,
                        height - lid_thickness - floor_thickness -
                        actual_height
                    ]) prismoid(size1 = [ side_radius * 2, side_radius * 2 ],
                                size2 = [ side_radius * 2, side_radius * 2 ], h = actual_height, anchor = BOTTOM);
                    translate([
                        -wall_thickness + box_size + side_radius, -wall_thickness + box_size / 2,
                        height - lid_thickness - floor_thickness -
                        actual_height
                    ]) cyl(r = side_radius, h = actual_height + 1, anchor = BOTTOM, $fn = 32);
                }
                difference()
                {
                    translate([
                        -wall_thickness + box_size / 2 - side_radius, -wall_thickness + box_size,
                        height - lid_thickness - floor_thickness -
                        actual_height
                    ]) prismoid(size1 = [ side_radius * 2, side_radius * 2 ],
                                size2 = [ side_radius * 2, side_radius * 2 ], h = actual_height, anchor = BOTTOM);
                    translate([
                        -wall_thickness + box_size / 2, -wall_thickness + box_size + side_radius,
                        height - lid_thickness - floor_thickness -
                        actual_height
                    ]) cyl(r = side_radius, h = actual_height + 1, anchor = BOTTOM, $fn = 32);
                }
            }
        }
    }

    difference()
    {
        cube([
            width - wall_thickness * 2, length - wall_thickness * 2, height - lid_thickness - floor_thickness + 0.1
        ]);
        box_size = magnet_diameter + magnet_border * 2;
        make_side_cylinder(box_size);
        translate([ width - wall_thickness * 2, 0, 0 ]) rotate([ 0, 0, 90 ]) make_side_cylinder(box_size);
        translate([ width - wall_thickness * 2, length - wall_thickness * 2, 0 ]) rotate([ 0, 0, 180 ])
            make_side_cylinder(box_size);
        translate([ 0, length - wall_thickness * 2, 0 ]) rotate([ 0, 0, 270 ]) make_side_cylinder(box_size);
    }
}

// Module: MagneticBoxLid()
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    top_thickness = the thickness of the all above the catch (default 2)
// Usage: MagneticBoxLid(100, 50, 5, 1);
// Example:
//    MagneticBoxLid(100, 50, 5,1);
module MagneticBoxLid(width, length, magnet_diameter, magnet_thickness, magnet_border = 1.5,
                      lid_thickness = default_lid_thickness, wall_thickness = default_wall_thickness, top_thickness = 2)
{

    internal_build_lid(width, length, lid_thickness, wall_thickness)
    {
        difference()
        {
            cube([ width, length, lid_thickness ]);
            translate([ magnet_diameter / 2 + magnet_border, magnet_diameter / 2 + magnet_border, -1 ])
                cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
            translate([ width - magnet_diameter / 2 - magnet_border, magnet_diameter / 2 + magnet_border, -1 ])
                cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
            translate([ width - magnet_diameter / 2 - magnet_border, length - magnet_diameter / 2 - magnet_border, -1 ])
                cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
            translate([ magnet_diameter / 2 + magnet_border, length - magnet_diameter / 2 - magnet_border, -1 ])
                cyl(d = magnet_diameter, h = magnet_thickness + 1, anchor = BOTTOM, $fn = 32);
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

// Module: MagneticBoxLidWithLabel()
// Topics: SlidingCatch
// Description:
//    Lid for a sliding catch with a label on top of it.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
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
// Usage: MagneticBoxLidWithLabel(100, 50, 5, 1, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    MagneticBoxLidWithLabel(100, 50, 5, 1, text_width = 70, text_height = 20, text_str = "Frog");
module MagneticBoxLidWithLabel(width, length, magnet_diameter, magnet_thickness, text_width, text_height, text_str,
                               magnet_border = 1.5, lid_boundary = 10, label_radius = 12, border = 2, offset = 4,
                               label_rotated = false, layout_width = undef, shape_width = undef, shape_type = undef,
                               shape_thickness = undef, aspect_ratio = undef, lid_thickness = default_lid_thickness)
{
    MagneticBoxLid(width = width, length = length, magnet_diameter = magnet_diameter,
                   magnet_thickness = magnet_thickness, magnet_border = magnet_border, lid_thickness = lid_thickness)
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