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

box_length = 208;
box_width = 154;
box_height = 44;
board_thickness = 6;

default_lid_thickness = 2;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_SQUARE;
default_lid_shape_thickness = 1.5;
default_lid_shape_rounding = 2;
default_lid_shape_width = 15;
default_lid_layout_width = 10;

card_width = 61;
card_length = 93;

card_box_width = default_wall_thickness * 2 + card_length;
card_box_length = box_width - 1;
card_box_height = box_height - board_thickness;

token_box_width = box_length - card_box_width - 1;
token_box_length = box_width - 1;
token_box_height = card_box_height;

module CardBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = card_box_width, length = card_box_length, height = card_box_height)
    {
        inner_length = card_box_length - default_wall_thickness * 2;
        inner_width = card_box_width - default_wall_thickness * 2;
        cube([ card_length, card_width, card_box_height ]);
        translate([ 0, inner_length - card_width, 0 ]) cube([ card_length, card_width, card_box_height ]);
        translate([ 0, card_width / 2, -default_floor_thickness - 0.5 ])
            FingerHoleBase(radius = 15, height = card_box_height);
        translate([ 0, inner_length - card_width / 2, -default_floor_thickness - 0.5 ])
            FingerHoleBase(radius = 15, height = card_box_height);
    }
    if (generate_lid)
    {
        translate([ card_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = card_box_width, length = card_box_length, height = card_box_height,
                               text_width = 70, text_height = 20, text_str = "Tokens", label_rotated = true);
    }
}

module TokensBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = token_box_width, length = token_box_length, height = token_box_height)
    {
        inner_length = token_box_length - default_wall_thickness * 2;
        inner_width = token_box_width - default_wall_thickness * 2;
        RoundedBoxAllSides(width = inner_width, length = inner_length, height = token_box_height, radius = 15);
    }
    if (generate_lid)
    {
        translate([ token_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = token_box_width, length = token_box_length, height = token_box_height,
                               text_width = 70, text_height = 20, text_str = "Tokens", label_rotated = true);
    }
}

TokensBox();