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

include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

canvas_piece_box_width = 41;
canvas_piece_box_length = 73;
canvas_piece_box_height = 29;
wall_thickness = 3;

divider_middle_width = 50;
divider_thickness = 1;
divider_length = 124;
divider_height = 30;
divider_total_width = 73 + 50 + 73;
divider_upright_length = 45;
divider_upright_diff = 73;

module PiecesBox()
{
    module MakeLid(str)
    {
        CapBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length,
                           text_width = len(str) * 10 + 5, text_length = 15, text_str = str, label_rotated = true,
                           wall_thickness = wall_thickness, lid_height = 2, lid_boundary = 5, layout_width = 5,
                           shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 1.5, shape_width = 7);
    }
    MakeBoxWithCapLid(width = canvas_piece_box_width, length = canvas_piece_box_length,
                      height = canvas_piece_box_height, wall_thickness = wall_thickness, lid_height = 2,
                      lid_finger_hold_len = 14)
        RoundedBoxAllSides(width = canvas_piece_box_width - wall_thickness * 2,
                           length = canvas_piece_box_length - wall_thickness * 2, height = canvas_piece_box_height,
                           radius = 5);
    translate([ 0, canvas_piece_box_length + 10, 0 ]) MakeLid("Red");
    translate([ 0, (canvas_piece_box_length + 10) * 2, 0 ]) MakeLid("Green");
    translate([ 0, (canvas_piece_box_length + 10) * 3, 0 ]) MakeLid("Grey");
    translate([ 0, (canvas_piece_box_length + 10) * 4, 0 ]) MakeLid("Blue");
    translate([ 0, (canvas_piece_box_length + 10) * 5, 0 ]) MakeLid("Purple");
    translate([ 0, (canvas_piece_box_length + 10) * 6, 0 ]) MakeLid("Palette");
}

module DividerPiece()
{
    union()
    {
        difference()
        {
            cuboid([ divider_total_width, divider_length, divider_thickness ], rounding = 5,
                   edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            // left
            translate([ divider_upright_diff / 8, divider_length / 16, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8, divider_length * 8 / 16, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            // right
            translate(
                [ divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length / 16, -0.5 ])
                cuboid([ divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1 ], rounding = 5,
                       edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                       anchor = BOTTOM + LEFT + FRONT);
            translate([
                divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length * 8 / 16, -0.5
            ]) cuboid([ divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1 ], rounding = 5,
                      edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                      anchor = BOTTOM + LEFT + FRONT);
            // middle
            translate([ divider_upright_diff / 8 + divider_upright_diff - 2, divider_length / 8, -0.5 ]) cuboid(
                [ divider_middle_width * 3 / 4 - 2, divider_length * 12 / 16, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
        }
        // left
        translate([ divider_upright_diff, 0, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff, divider_length - divider_upright_length, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        // right
        translate([ divider_upright_diff + divider_middle_width - 2, 0, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff + divider_middle_width - 2, divider_length - divider_upright_length - 2, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
    }
}

PiecesBox();

translate([ canvas_piece_box_width + 10, 0, 0 ]) DividerPiece();

/*
MakeBoxWithCapLid(canvas_piece_box_width, canvas_piece_box_length, canvas_piece_box_height);

translate([ canvas_piece_box_width + 10, 0, 0 ])
    CapBoxLidWithLabel(canvas_piece_box_width, canvas_piece_box_length, text_length = 15, text_width = 50,
                       text_str = "Frog", label_rotated = true);

/*
calc_lid_wall_thickness = 1;
size_spacing = 0.2;
width = 100;
length = 200;
height = 20;
finger_hold_height = 5;
calc_lid_finger_hold_len = 20;
cap_height = 10;

difference()
{
    cube([ width, length, finger_hold_height ]);
    translate([ calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0 ]) cube([
        width - calc_lid_wall_thickness * 2 - size_spacing * 2, length - calc_lid_wall_thickness * 2 - size_spacing * 2,
        cap_height
    ]);
    difference()
    {
        for (i = [0:1:1])
        {
            for (j = [0:1:1])
            {
                translate([ (width - calc_lid_finger_hold_len-0.1) * i, (length - calc_lid_finger_hold_len-0.1) * j,
-0.5 ]) cube([ calc_lid_finger_hold_len + 0.1, calc_lid_finger_hold_len+0.1, finger_hold_height + 1 ]);
            }
        }
    }
}
*/