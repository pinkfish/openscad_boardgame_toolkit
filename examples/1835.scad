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

box_length = 298;
box_width = 216;
box_height = 50;

wall_thickness = 3;
inner_wall = 1;

share_width = 46;
share_length = 66;
share_thickness_ten = 4;
money_width = 52;
money_length = 98;
money_one_thickness = 5;
money_total = 22;
company_card_bmb_lenght = 151;
company_card_bmb_width = 106;
company_card_bmb_thickness_six = 2.5;
company_card_length = 200;
company_card_lenght = 131;
token_diameter = 6;
token_thickness = 2;
large_marker_diamter = 20;
large_marker_length = 41;
tile_width = 40;
train_tile_thickness_10 = 6;
board_thickness = 15;

money_box_width = (money_width + inner_wall) * 8 + wall_thickness * 2;
money_box_length = money_length + wall_thickness;

module MoneyBox()
{
    MakeBoxWithCapLid(width = canvas_piece_box_width, length = canvas_piece_box_length,
                      height = canvas_piece_box_height, wall_thickness = wall_thickness, lid_height = 2,
                      lid_finger_hold_len = 14)
                      for (i = [0:1:7]) {
                        translate([(money_width+inner_wall)*i,0,0])
                        cube([money_width, money_lenght, money_one_thickness]);
                      }

}