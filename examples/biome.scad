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

box_length = 285;
box_width = 285;
box_height = 73;

board_thickness = 20;
board_width = 255;

spinner = 132;

card_width = 66;
card_length = 91;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

nest_width = 45;
nest_total_length = 180;

player_cube = 8;
player_token_diameter = 10;

player_box_width = default_wall_thickness * 4 + player_cube * 4 + 2;
player_box_length = (box_length - 2) / 4;
player_box_height = box_height - board_thickness;

module PlayerBox()
{
    MakeBoxWithSlipoverLid(width = player_box_width, length = player_box_length, height = player_box_height)
    {
        RoundedBoxAllSides(width = $inner_width, length = $inner_length, height = player_box_height, radius = 5);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        PlayerBox();
    }
}

if (FROM_MAKE != 1)
{
    BoxLayout();
}