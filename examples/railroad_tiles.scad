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

box_width = 230;
box_length = 230;
box_height = 63;

railroad_tile = 46;

railroad_tile_clock_diameter = 32;
railroad_tile_two_player = 29;

cardboard_thickness = 1.5;

player_marker_width = 13;
player_marker_height = 14;
player_marker_head_height = 10;
player_marker_head_width = 9;
player_marker_hat_wicdth = 12;
player_marker_middle_width = 11.5;
player_marker_head_base = 4;
player_marker_hat_height = 6;
player_marker_thickness = 7;
player_marker_total_height = player_marker_height + player_marker_hat_height;

player_box_width = (box_width - 2) / 2;
player_box_length = railroad_tile_clock_diameter + default_wall_thickness * 2;
player_box_height = default_floor_thickness + default_lid_thickness + player_marker_thickness + 1;

starting_box_width = (box_width - 2) / 2;
starting_box_length = player_box_length;
starting_box_height = player_box_height;

tokens_box_width = (box_width - 2) / 4;
tokens_box_length = player_box_length;
tokens_box_height = (box_height - cardboard_thickness - 1 - player_box_height) / 2;

objective_box_height = (box_height - cardboard_thickness - 1) / 5;
objective_box_width = player_box_width;
objective_box_length = default_wall_thickness * 2 + railroad_tile;

spacer_box_width = box_width - 2;
spacer_box_length = box_length - 2 - objective_box_length - tokens_box_length;
spacer_box_height = box_height - cardboard_thickness - 1;

module TokensBox() {
  MakeBoxWithCapLid(width=tokens_box_width, length=tokens_box_length, height=tokens_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=tokens_box_height, radius=5);
  }
}

module PlayerBox() {
  MakeBoxWithCapLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    for (i = [0:3]) {
      translate(
        [
          player_marker_width / 2 + (player_marker_width + 2) * i,
          $inner_length / 2,
          $inner_height - player_marker_thickness - 1,
        ]
      ) {
        PlayerMarker(player_box_height);
      }
    }
    translate([$inner_width - player_box_height - 10, $inner_length / 2, $inner_height - cardboard_thickness - 1]) {
      translate([railroad_tile_two_player / 2, 0, 0])
        sphere(d=20, anchor=BOTTOM);
      cuboid(
        [railroad_tile_two_player, railroad_tile_two_player, player_box_height], anchor=BOTTOM,
        rounding=1, edges=[FRONT + LEFT, BACK + RIGHT, FRONT + RIGHT, BACK + LEFT]
      );
      translate([-railroad_tile_two_player / 2, 0, 0])
        sphere(d=20, anchor=BOTTOM);
    }
  }
}

module StartingBox() {
  MakeBoxWithCapLid(width=starting_box_width, length=starting_box_length, height=starting_box_height) {
    for (i = [0:2]) {
      translate(
        [
          $inner_width - railroad_tile_clock_diameter / 2 - (railroad_tile_clock_diameter + 2) * i - 4,
          $inner_length / 2,
          $inner_height - cardboard_thickness * (i == 0 ? 3 : 2) - 1,
        ]
      ) {
        CylinderWithIndents(
          radius=railroad_tile_clock_diameter / 2, height=starting_box_height, finger_holes=[0, 180],
          finger_hole_radius=10
        );
      }
    }
  }
}

module ObjectiveBox() {
  MakeBoxWithCapLid(width=objective_box_width, length=objective_box_length, height=objective_box_height) {
    translate([railroad_tile / 2, $inner_length / 2, 0]) {
      CuboidWithIndentsBottom(
        [railroad_tile, railroad_tile, objective_box_height],
        finger_holes=[2]
      );
    }
    translate([railroad_tile / 2 + (railroad_tile + 18), $inner_length / 2, 0]) {
      CuboidWithIndentsBottom(
        [railroad_tile, railroad_tile, objective_box_height],
        finger_holes=[6]
      );
    }
  }
}

module SpacerBox() {
  MakeBoxWithNoLid(width=spacer_box_width, length=spacer_box_length, height=spacer_box_height, hollow=true);
}

module PlayerMarker(thickness = 1) {
  translate([0, -(player_marker_height - player_marker_hat_height) / 4, 0])
    union() {
      hull() {
        translate([player_marker_width / 2 - 0.5, player_marker_height - 0.5, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=1, $fn=32);
        }
        translate([-player_marker_width / 2 + 0.5, player_marker_height - 0.5, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=1, $fn=32);
        }

        // Shoulders
        diff = (player_marker_middle_width - player_marker_head_base);
        translate([-player_marker_middle_width / 2 + diff / 2, diff / 2, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=diff, $fn=64);
        }
        translate([player_marker_middle_width / 2 - diff / 2, diff / 2, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=diff, $fn=64);
        }
      }
      translate([0, -player_marker_head_height / 2 + 1, 0]) {
        resize([player_marker_head_width, player_marker_head_height + 2, thickness]) {
          cyl(h=thickness, anchor=BOTTOM, d=player_marker_head_height, $fn=64);
        }
      }
      hull() {
        translate([player_marker_hat_wicdth / 2 - 1.25, -player_marker_hat_height, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=2.5, $fn=32);
        }
        translate([-player_marker_hat_wicdth / 2 + 1.25, -player_marker_hat_height, 0]) {
          cyl(h=thickness, anchor=BOTTOM, d=2.5, $fn=32);
        }
      }
    }
}

module BoxLayout() {
  cube([box_width, box_length, cardboard_thickness + 1]);
  cube([box_width, 1, box_height]);
  translate([0, 0, cardboard_thickness + 1]) {
    for (i = [0:3]) {
      translate([tokens_box_width * i, 0, 0])
        TokensBox();
      translate([tokens_box_width * i, 0, tokens_box_height])
        TokensBox();
    }
    translate([0, 0, tokens_box_height * 2])
      PlayerBox();
    translate([player_box_width, 0, tokens_box_height * 2])
      StartingBox();
    for (i = [0:4]) {
      translate([0, tokens_box_length, objective_box_height * i]) {
        ObjectiveBox();
      }
      translate([objective_box_width, tokens_box_length, objective_box_height * i]) {
        ObjectiveBox();
      }
    }
    translate([0, tokens_box_length + objective_box_length, 0]) {
      SpacerBox();
    }
  }
}

BoxLayout();
