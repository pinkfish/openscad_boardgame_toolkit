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

box_width = 215;
box_length = 307;
box_height = 96;

card_length = 91;
card_width = 66;
card_10_thickness = 8;
single_card_thickness = card_10_thickness / 10;

small_card_width = 48.5;
small_card_length = 71.5;

hex_width = 72;

board_thickness = 18;
board_width = box_width;
board_length = 231;

cardboard_token_thickness = 2;

voting_board_width = 40;
voting_board_length = 196;

upgrade_width = 86;
upgrade_length = 102;
upgrade_thickness = 3.5;

favor_token_diameter = 20;

player_token_diameter = 14.5;

screen_length = 204;
screen_width = 102;

class_i_ship_diameter = 24;
class_i_ship_thickness = 10;

class_iii_ship_edge_length = 43;
class_iii_ship_thickness = 10;
class_iii_ship_radius = class_iii_ship_edge_length / sqrt(3);
class_iii_ship_apothem = class_iii_ship_edge_length * sqrt(3) / 6;

class_ii_ship_length = 38;
class_ii_ship_width = 19;
class_ii_ship_thickness = 8;

marker_cube_width = 11;

railgun_length = 19;
railgun_width = 10;
railgun_thickness = 8;
railgun_nub_offset = 4;

round_nub = 4.5;
round_nub_thickness = 3;

cargo_width = 13.5;
cargo_thickness = 8.5;

module ClassIIIShip(thickness) {
  linear_extrude(height=thickness) {
    polygon(
      round_corners(
        [
          [class_iii_ship_edge_length / 2, class_iii_ship_apothem * 1.5],
          [0, -class_iii_ship_apothem * 1.5],
          [-class_iii_ship_edge_length / 2, class_iii_ship_apothem * 1.5],
        ],
        radius=3
      )
    );
  }
}

module ClassIIShip(thickness) {
  CuboidWithIndentsBottom(
    size=[class_ii_ship_length, class_ii_ship_width, thickness],
    rounding=2,
    edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT],
    finger_holes=[0]
  );
}

module ClassIShip(thickness) {
  CylinderWithIndents(
    radius=class_i_ship_diameter / 2, height=thickness, finger_holes=[0], finger_hole_radius=12
  );
}
