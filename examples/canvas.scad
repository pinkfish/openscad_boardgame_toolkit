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

module MakeLid(str)
{
    CapBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length,
                       height = canvas_piece_box_height, text_width = len(str) * 9 + 5, text_height = 15,
                       text_str = str, label_rotated = true, wall_thickness = wall_thickness, lid_thickness = 2,
                       lid_boundary = 5, layout_width = 5, shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 1.5,
                       shape_width = 7, label_colour = "black");
}

module PiecesBox() // `make` me
{
    MakeBoxWithCapLid(width = canvas_piece_box_width, length = canvas_piece_box_length,
                      height = canvas_piece_box_height, wall_thickness = wall_thickness, lid_thickness = 2,
                      lid_finger_hold_len = 14)
        RoundedBoxAllSides(width = canvas_piece_box_width - wall_thickness * 2,
                           length = canvas_piece_box_length - wall_thickness * 2, height = canvas_piece_box_height,
                           radius = 5);
}

module PiecesBoxLidRed() // `make` me
{
    translate([ 0, canvas_piece_box_length + 10, 0 ]) MakeLid("Red");
}
module PiecesBoxLidGreen() // `make` me
{

    translate([ 0, (canvas_piece_box_length + 10) * 2, 0 ]) MakeLid("Green");
}
module PiecesBoxLidGrey() // `make` me
{
    translate([ 0, (canvas_piece_box_length + 10) * 3, 0 ]) MakeLid("Grey");
}
module PiecesBoxLidBlue() // `make` me
{
    translate([ 0, (canvas_piece_box_length + 10) * 4, 0 ]) MakeLid("Blue");
}
module PiecesBoxLidPurple() // `make` me
{
    translate([ 0, (canvas_piece_box_length + 10) * 5, 0 ]) MakeLid("Purple");
}
module PiecesBoxLidPalette() // `make` me
{
    translate([ 0, (canvas_piece_box_length + 10) * 6, 0 ]) MakeLid("Palette");
}

module DividerPiece() // `make` me
{
    union()
    {
        difference()
        {
            color(default_material_colour) cuboid(
                [ divider_total_width, divider_length, divider_thickness ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            // left
            translate([ divider_upright_diff / 8, divider_length / 16, -0.5 ]) color(default_material_colour) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8, divider_length * 8 / 16, -0.5 ]) color(default_material_colour)
                cuboid([ divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1 ], rounding = 5,
                       edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                       anchor = BOTTOM + LEFT + FRONT);
            // right
            translate(
                [ divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length / 16, -0.5 ])
                color(default_material_colour)
                    cuboid([ divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1 ],
                           rounding = 5, edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                           anchor = BOTTOM + LEFT + FRONT);
            translate([
                divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length * 8 / 16, -0.5
            ]) color(default_material_colour)
                cuboid([ divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1 ], rounding = 5,
                       edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                       anchor = BOTTOM + LEFT + FRONT);
            // middle
            translate([ divider_upright_diff / 8 + divider_upright_diff - 2, divider_length / 8, -0.5 ])
                color(default_material_colour)
                    cuboid([ divider_middle_width * 3 / 4 - 2, divider_length * 12 / 16, divider_thickness + 1 ],
                           rounding = 5, edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ],
                           anchor = BOTTOM + LEFT + FRONT);
        }
        // left
        translate([ divider_upright_diff, 0, 0 ]) color(default_material_colour)
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff, divider_length - divider_upright_length, 0 ]) color(default_material_colour)
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        // right
        translate([ divider_upright_diff + divider_middle_width - 2, 0, 0 ]) color(default_material_colour)
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff + divider_middle_width - 2, divider_length - divider_upright_length - 2, 0 ])
            color(default_material_colour)
                cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                       edges = [ TOP + FRONT, TOP + BACK ]);
    }
}

if (FROM_MAKE != 1)
{
    PiecesBox();

    translate([ canvas_piece_box_width + 10, 0, 0 ]) DividerPiece();
}