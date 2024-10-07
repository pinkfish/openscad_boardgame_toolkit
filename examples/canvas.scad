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

canvas_piece_box_width = 41.5;
canvas_piece_box_length = 73;
canvas_piece_box_height = 29;
wall_thickness = 2;

divider_middle_width = 40;
divider_thickness = 1;
divider_length = 124;
divider_height = 30;
divider_total_width = 73 + 40 + 73;
divider_upright_length = 45;
divider_upright_diff = 73;

module PiecesBox()
{
    module MakeLid(str)
    {
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length,
                               text_width = len(str) * 10 + 5, text_length = 15, text_str = str, label_rotated = true);
    }
    MakeBoxWithSlidingLid(width = canvas_piece_box_width, length = canvas_piece_box_length,
                          height = canvas_piece_box_height)
        RoundedBoxAllSides(width = canvas_piece_box_width - wall_thickness * 2,
                           length = canvas_piece_box_length - wall_thickness * 2, height = canvas_piece_box_height,
                           radius = 5);
    translate([ 0, canvas_piece_box_length + 10, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Red", label_rotated = true);
    translate([ 0, (canvas_piece_box_length + 10) * 2, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Green", label_rotated = true);
    translate([ 0, (canvas_piece_box_length + 10) * 3, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Grey", label_rotated = true);
    translate([ 0, (canvas_piece_box_length + 10) * 4, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Blue", label_rotated = true);
    translate([ 0, (canvas_piece_box_length + 10) * 5, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Purple", label_rotated = true);
    translate([ 0, (canvas_piece_box_length + 10) * 6, 0 ])
        SlidingBoxLidWithLabel(width = canvas_piece_box_width, length = canvas_piece_box_length, text_width = 30,
                               text_length = 15, text_str = "Palette", label_rotated = true);
}

module DividerPiece()
{
    union()
    {
        difference()
        {
            cuboid([ divider_total_width, divider_length, divider_thickness ], rounding = 5,
                   edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8, divider_length / 8, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 6 / 16, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8, divider_length * 9 / 16, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 3 / 8, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length / 8, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 6 / 16, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
            translate([ divider_upright_diff / 8+ divider_upright_diff + divider_middle_width, divider_length * 9 / 16, -0.5 ]) cuboid(
                [ divider_upright_diff * 3 / 4, divider_length * 3 / 8, divider_thickness + 1 ], rounding = 5,
                edges = [ FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT ], anchor = BOTTOM + LEFT + FRONT);
        }
        translate([ divider_upright_diff, 0, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff + divider_middle_width, 0, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff, divider_length - divider_upright_length, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
        translate([ divider_upright_diff + divider_middle_width, divider_length - divider_upright_length, 0 ])
            cuboid([ 2, divider_upright_length, divider_height ], anchor = BOTTOM + LEFT + FRONT, rounding = 3,
                   edges = [ TOP + FRONT, TOP + BACK ]);
    }
}

PiecesBox();

translate([ canvas_piece_box_width + 10, 0, 0 ]) DividerPiece();