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

// LibFile: cap_box.scad
//    This file has all the modules needed to generate a cap box.

// FileSummary: Cap box pieces for the cap boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

assert(version_num() >= 20190500, "boardgame_toolkit requires OpenSCAD version 2019.05 or later.");

include <BOSL2/rounding.scad>
include <BOSL2/std.scad>
include <base_bgtk.scad>
include <components.scad>
include <labels.scad>
include <lids_base.scad>

// Section: CapLid
// Description:
//    Cap lid to go on insets, this is a smaller lid that fits onto the top of the box. It only covers
//    the top few mms and has some cut outs on the side to make removal easier.

// Module: MakeCapLidBox()
// Topics: CapLid
// Arguments:
//   width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default 1)
//    wall_thickness = thickness of the walls (default 2)
//    floor_thickness = thickness of the floor (default 2)
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    lid_finger_hold_len = length of the finger hold sections to cut out (default min(width,lenght)/5)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
// Usage: MakeBoxWithCapLid(100, 50, 20);
// Example:
//    MakeBoxWithCapLid(100, 50, 20);
module MakeBoxWithCapLid(width, length, height, cap_height = 10, lid_thickness = 1, wall_thickness = 2,
                         size_spacing = m_piece_wiggle_room, lid_wall_thickness = undef, lid_finger_hold_len = undef,
                         finger_hold_height = 5, floor_thickness = 2)
{
    calc_lid_wall_thickness = lid_wall_thickness == undef ? wall_thickness / 2 : lid_wall_thickness;
    calc_lid_finger_hold_len = lid_finger_hold_len == undef ? min(width, length) / 5 : lid_finger_hold_len;
    calc_floor_thickness = floor_thickness == undef ? wall_thickness : floor_thickness;
    difference()
    {

        cube([ width, length, height - lid_thickness - size_spacing ]);
        // lid diff.
        translate([ 0, 0, height - cap_height ]) difference()
        {
            translate([ -size_spacing, -size_spacing, 0 ])
                cube([ width + size_spacing * 2, length + size_spacing * 2, cap_height ]);
            translate([ calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0 ]) cube([
                width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                length - calc_lid_wall_thickness * 2 - size_spacing * 2,
                cap_height
            ]);
        }
        // finger cutouts.
        translate([ 0, 0, height - cap_height - finger_hold_height ]) difference()
        {
            difference()
            {
                translate([ -size_spacing, -size_spacing, 0 ])
                    cube([ width + size_spacing * 2, length + size_spacing * 2, finger_hold_height + 1 ]);

                translate([ calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0 ]) cube([
                    width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                    length - calc_lid_wall_thickness * 2 - size_spacing * 2, finger_hold_height + 2
                ]);
            }
            translate([ calc_lid_finger_hold_len, 0, -0.1 ]) cuboid(
                [
                    width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness - calc_lid_wall_thickness,
                    finger_hold_height + 0.2
                ],
                rounding = 3, edges = [ TOP + LEFT, TOP + RIGHT ], anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ calc_lid_finger_hold_len, length - calc_lid_wall_thickness, -0.1 ]) cuboid(
                [
                    width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness - calc_lid_wall_thickness,
                    finger_hold_height + 0.2
                ],
                rounding = 3, edges = [ TOP + LEFT, TOP + RIGHT ], anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ 0, calc_lid_finger_hold_len, -0.1 ]) cuboid(
                [
                    wall_thickness - calc_lid_wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1,
                    finger_hold_height + 0.2
                ],
                rounding = 3, edges = [ TOP + FRONT, TOP + BACK ], anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ width - calc_lid_wall_thickness, calc_lid_finger_hold_len, -0.1 ]) cuboid(
                [
                    wall_thickness - calc_lid_wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1,
                    finger_hold_height + 0.2
                ],
                rounding = 3, edges = [ TOP + FRONT, TOP + BACK ], anchor = BOTTOM + LEFT + FRONT, $fn = 32);
        }
        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        intersection()
        {
            translate([ wall_thickness, wall_thickness, calc_floor_thickness ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 2 ]);
            translate([ wall_thickness, wall_thickness, calc_floor_thickness ]) children();
        }
    }
}

// Module: CapBoxLid()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//   width = outside width of the box
//    length = inside width of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default 1)
//    wall_thickness = thickness of the walls (default 2)
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
// Usage: CapBoxLid(100, 50, 20);
// Example:
//    CapBoxLid(100, 50, 20);
module CapBoxLid(width, length, cap_height = 10, lid_thickness = 1, wall_thickness = 2,
                 size_spacing = m_piece_wiggle_room, lid_wall_thickness = undef)
{
    calc_lid_wall_thickness = lid_wall_thickness == undef ? wall_thickness / 2 : lid_wall_thickness;
    translate([ 0, length, cap_height ]) rotate([ 180, 0, 0 ])
    {
        union()
        {
            translate([ 0, 0, cap_height - lid_thickness ])
                internal_build_lid(width, length, lid_thickness, wall_thickness)
            {
                difference()
                {
                    // Top piece
                    cube([ width, length, lid_thickness ]);
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
            difference()
            {
                cube([ width, length, cap_height ]);
                translate([ calc_lid_wall_thickness, calc_lid_wall_thickness, -0.5 ])
                    cube([ width - calc_lid_wall_thickness * 2, length - calc_lid_wall_thickness * 2, cap_height + 1 ]);
            }
        }
    }
}

// Module: CapBoxLidWithLabel()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//   width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default 1)
//    wall_thickness = thickness of the walls (default 2)
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    label_radius = radius of the label corners (default 12)
//    border= border of the item (default 2)
//    offset = offset in from the edge for the label (default 4)
//    label_rotated = if the label is rotated (default false)
//    layout_width = the width of the layout pieces (default 12)
//    shape_width = width of the shape (default layout_width)
//    shape_thickness = how wide the pieces are (default 2)
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
// Usage: CapBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
module CapBoxLidWithLabel(width, length, text_width, text_height, text_str, lid_boundary = 10, wall_thickness = 2,
                          label_radius = 12, border = 2, offset = 4, label_rotated = false, cap_height = 10,
                          layout_width = 12, shape_width = 12, shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2,
                          size_spacing = m_piece_wiggle_room, lid_thickness = 1, lid_wall_thickness = undef)
{
    CapBoxLid(width = width, length = length, cap_height = cap_height, wall_thickness = wall_thickness,
              lid_thickness = lid_thickness, lid_wall_thickness = lid_wall_thickness,
              size_spacing = m_piece_wiggle_room)
    {
        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
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