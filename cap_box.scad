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

// Section: CapLid
// Description:
//    Cap lid to go on insets, this is a smaller lid that fits onto the top of the box. It only covers
//    the top few mms and has some cut outs on the side to make removal easier.

// Function: CapBoxDefaultCapHeight()
// Description:
//   Works out the default value for the cap box height.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultCapHeight(height) = min(10, height / 2);

// Function: CapBoxDefaultFingerHoldHeight()
// Description:
//   Works out the default value for the cap box finger hold height.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultFingerHoldHeight(height) = min(5, height / 4);

// Function: CapBoxDefaultFingerHoldLen()
// Description:
//   Works out the default value for the cap box finger hold length.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultFingerHoldLen(width, length) = min(width, length) / 5;

// Function: CapBoxDefaultLidWallThickness()
// Description:
//   Works out the default value for the cap box wall thickness.
// Arguments:
//   wall_thickness = the wall thickness of the box.
function CapBoxDefaultLidWallThickness(wall_thickness) = wall_thickness / 2;

// Function:CapBoxDefaultLidFingerHoldRounding()
// Description:
//   Works out the default value for the cap box rounding piece on the edge.
// Arguments:
//   cap_height = the current cap height
function CapBoxDefaultLidFingerHoldRounding(cap_height) = min(3, cap_height / 2);

// Module: MakeBoxWithCapLid()
// Topics: CapLid
// Arguments:
//   width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    lid_finger_hold_len = length of the finger hold sections to cut out (default min(width,lenght)/5)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
// Usage: MakeBoxWithCapLid(100, 50, 20);
// Example:
//    MakeBoxWithCapLid(100, 50, 20);
// Example:
//    MakeBoxWithCapLid(100, 50, 10, lid_finger_hold_len = 4);
// Example:
//    MakeBoxWithCapLid(100, 50, 5, cap_height = 2, finger_hold_height = 1);
module MakeBoxWithCapLid(width, length, height, cap_height = undef, lid_thickness = default_lid_thickness,
                         wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room,
                         lid_wall_thickness = undef, lid_finger_hold_len = undef, finger_hold_height = 5,
                         floor_thickness = default_floor_thickness)
{
    calc_lid_wall_thickness =
        lid_wall_thickness == undef ? CapBoxDefaultLidWallThickness(wall_thickness) : lid_wall_thickness;
    calc_lid_finger_hold_len =
        lid_finger_hold_len == undef ? CapBoxDefaultFingerHoldLen(width, length) : lid_finger_hold_len;
    calc_floor_thickness = floor_thickness == undef ? wall_thickness : floor_thickness;
    calc_cap_height = cap_height == undef ? CapBoxDefaultCapHeight(height) : cap_height;
    calc_finger_hold_height = finger_hold_height == undef ? CapBoxDefaultFingerHoldHeight(height) : finger_hold_height;
    calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height);
    difference()
    {

        cuboid([ width, length, height - lid_thickness - size_spacing ], anchor = BOTTOM + FRONT + LEFT,
               rounding = wall_thickness, edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        // lid diff.
        translate([ 0, 0, height - calc_cap_height ]) difference()
        {
            translate([ -size_spacing, -size_spacing, 0 ])
                cuboid([ width + size_spacing * 2, length + size_spacing * 2, calc_cap_height ],
                       anchor = BOTTOM + FRONT + LEFT);
            translate([ calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0 ]) cuboid(
                [
                    width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                    length - calc_lid_wall_thickness * 2 - size_spacing * 2,
                    calc_cap_height
                ],
                anchor = BOTTOM + FRONT + LEFT, rounding = calc_lid_wall_thickness,
                edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
        }
        // finger cutouts.
        translate([ 0, 0, height - calc_cap_height - calc_finger_hold_height ]) difference()
        {
            difference()
            {
                translate([ -size_spacing, -size_spacing, 0 ])
                    cuboid([ width + size_spacing * 2, length + size_spacing * 2, calc_finger_hold_height + 1 ],
                           anchor = BOTTOM + FRONT + LEFT);

                translate([ calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0 ]) cuboid(
                    [
                        width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                        length - calc_lid_wall_thickness * 2 - size_spacing * 2, calc_finger_hold_height + 2
                    ],
                    anchor = BOTTOM + FRONT + LEFT, rounding = calc_lid_wall_thickness,
                    edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
            }
            translate([ calc_lid_finger_hold_len, 0, -0.1 ]) cuboid(
                [
                    width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness - calc_lid_wall_thickness,
                    calc_finger_hold_height + 0.2
                ],
                rounding = calc_finger_hole_rounding, edges = [ TOP + LEFT, TOP + RIGHT ],
                anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ calc_lid_finger_hold_len, length - calc_lid_wall_thickness, -0.1 ]) cuboid(
                [
                    width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness - calc_lid_wall_thickness,
                    calc_finger_hold_height + 0.2
                ],
                rounding = calc_finger_hole_rounding, edges = [ TOP + LEFT, TOP + RIGHT ],
                anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ 0, calc_lid_finger_hold_len, -0.1 ]) cuboid(
                [
                    wall_thickness - calc_lid_wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1,
                    calc_finger_hold_height + 0.2
                ],
                rounding = calc_finger_hole_rounding, edges = [ TOP + FRONT, TOP + BACK ],
                anchor = BOTTOM + LEFT + FRONT, $fn = 32);
            translate([ width - calc_lid_wall_thickness, calc_lid_finger_hold_len, -0.1 ]) cuboid(
                [
                    wall_thickness - calc_lid_wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1,
                    calc_finger_hold_height + 0.2
                ],
                rounding = calc_finger_hole_rounding, edges = [ TOP + FRONT, TOP + BACK ],
                anchor = BOTTOM + LEFT + FRONT, $fn = 32);
        }
        // Put the children in the box.
        translate([ wall_thickness, wall_thickness, calc_floor_thickness ]) children();
    }
}

// Module: CapBoxLid()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
// Usage: CapBoxLid(100, 50, 20);
// Example:
//    CapBoxLid(100, 50, 30);
// Example:
//    CapBoxLid(100, 50, 10);
// Example:
//    CapBoxLid(100, 50, 10, cap_height = 3);
module CapBoxLid(width, length, height, cap_height = undef, lid_thickness = default_lid_thickness,
                 wall_thickness = default_wall_thickness, size_spacing = m_piece_wiggle_room,
                 lid_wall_thickness = undef)
{
    calc_lid_wall_thickness = lid_wall_thickness == undef ? wall_thickness / 2 : lid_wall_thickness;
    calc_cap_height = cap_height == undef ? CapBoxDefaultCapHeight(height) : cap_height;
    translate([ 0, length, calc_cap_height ]) rotate([ 180, 0, 0 ])
    {
        union()
        {
            translate([ 0, 0, calc_cap_height - lid_thickness ])
                internal_build_lid(width, length, lid_thickness, wall_thickness)
            {
                difference()
                {
                    // Top piece
                    cuboid([ width, length, lid_thickness ], anchor = BOTTOM + FRONT + LEFT,
                           rounding = wall_thickness / 2,
                           edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
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
                cuboid([ width, length, calc_cap_height ], anchor = BOTTOM + FRONT + LEFT,
                       rounding = calc_lid_wall_thickness / 2,
                       edges = [ LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK ]);
                translate([ calc_lid_wall_thickness, calc_lid_wall_thickness, -0.5 ]) cube(
                    [ width - calc_lid_wall_thickness * 2, length - calc_lid_wall_thickness * 2, calc_cap_height + 1 ]);
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
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
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
// Usage: CapBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabel(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog");
module CapBoxLidWithLabel(width, length, height, text_width, text_height, text_str, lid_boundary = 10,
                          wall_thickness = default_wall_thickness, label_radius = 12, border = 2, offset = 4, label_rotated = false,
                          cap_height = undef, layout_width = undef, shape_width = undef, shape_type = undef,
                          shape_thickness = undef, size_spacing = m_piece_wiggle_room, lid_thickness = default_lid_thickness,
                          lid_wall_thickness = undef, aspect_ratio = 1.0)
{
    CapBoxLid(width = width, length = length, height = height, cap_height = cap_height, wall_thickness = wall_thickness,
              lid_thickness = lid_thickness, lid_wall_thickness = lid_wall_thickness,
              size_spacing = m_piece_wiggle_room)
    {
        echo([shape_width]);
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