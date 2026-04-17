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

box_height = 65;
box_width = 286;
box_length = 286;

default_lid_thickness = 3;

player_board_width = 145;
player_board_length = 162;
player_board_thickness = 2.5;

game_board_width = 280;
game_board_length = 281;
game_board_thickness = 17;

game_board_base_width = 242;
game_board_base_length = 272;
game_board_base_thickness = 17;

factory_hex_width = 56;
factory_hex_thickness = 7.5;
factory_hex_radius = PolygonRadiusFromApothem(factory_hex_width, 6);

outback_tile_thickness = 3.25;

robot_width = 8.5;
robot_length = 18.5;
robot_thickness = 8;

card_width = 67;
card_length = 90;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

card_box_width = default_wall_thickness * 2 + card_width;
card_box_length = default_wall_thickness * 2 + card_length;
card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * 8;

robot_box_width = card_box_width - 10;
robot_box_length = box_length - card_box_length * 2;
robot_box_height = card_box_height / 2;

commuter_box_width = box_width - game_board_base_width;
commuter_box_length = box_length / 4;
commuter_box_height = game_board_base_thickness;

module OutbackSmallTile(thickness = 2) {
  for (i = [0:2]) {
    rotate([0, 0, i * 120])
      translate([factory_hex_radius, 0, 0])
        RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
  }
}

module GhostAndOutbackTiles(thickness = 2) {
  translate([-factory_hex_radius, -factory_hex_width * 1.5, 0]) {
    for (i = [0:3]) {
      translate([0, factory_hex_width * i, 0])
        RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
    }
    for (i = [0:2]) {
      translate([factory_hex_radius * 3 / 2, factory_hex_width * i + factory_hex_width / 2, 0])
        RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
    }
  }
}

module CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, card_box_height],
    lid_thickness=4
  ) {
    cube([$inner_width, $inner_length, box_height]);
    translate([$inner_width / 2.0, 0, -default_floor_thickness])
      FingerHoleBase(
        radius=20,
        height=card_box_height - default_lid_thickness
      );
  }
}

module CardBoxLidDirectConnection() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, card_box_height],
    text_str="Maps 2",
    lid_thickness=4
  );
}

module RobotBox(colour) // `make` me
{
  MakeBoxWithCapLid(
    size=[robot_box_width, robot_box_length, robot_box_height],
    material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - robot_thickness])
      cuboid([robot_length * 3, robot_width * 18 / 3, robot_thickness + 1], anchor=BOTTOM);
  }
}

module RobotBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[robot_box_width, robot_box_length, robot_box_height], text_str="Robots"
  );
}

module CommuterBox(colour) // `make` me
{
  MakeBoxWithCapLid(
    size=[commuter_box_width, commuter_box_length, commuter_box_height],
    material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - robot_thickness - 0.5])
      cuboid([$inner_width - 1, $inner_length - 1, robot_thickness + 1], anchor=BOTTOM);
  }
}

module CommuterBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[commuter_box_width, commuter_box_length, commuter_box_height], text_str="Commuter"
  );
}

module BoxLayout(layout = 0) {
  factory_colours = ["silver", "gold", "orange", "pink", "aqua", "coral", "purple"];
  player_colours = ["green", "orange", "blue", "yellow"];

  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([box_width, 1, box_height]);
  }
  if (layout < 2) {
    translate([box_width - game_board_width, 0, box_height - game_board_thickness])
      color("darkblue")
        cube([game_board_width, game_board_length, game_board_thickness]);
    translate([box_width - game_board_base_width, 0, box_height - game_board_thickness - game_board_base_thickness]) {
      color("darkgreen")
        cube([game_board_base_width, game_board_base_length, game_board_base_thickness]);
    }
    for (i = [0:3])
      translate(
        [
          0,
          0,
          box_height - game_board_thickness - game_board_base_thickness - player_board_thickness * (i + 1),
        ]
      )

        color(player_colours[i])
          cube([player_board_width, player_board_length, player_board_thickness]);
  }

  for (i = [0:3]) {
    translate([0, commuter_box_length * i, box_height - game_board_thickness - game_board_base_thickness])
      CommuterBox(colour=factory_colours[i + 3]);
  }
  CardBox();
  translate([box_width - factory_hex_radius * 8 / 4, factory_hex_width * 2, 0])
    rotate(180)
      GhostAndOutbackTiles(thickness=outback_tile_thickness * 8);
}

module BoxLayoutA() // `document` me
{
  BoxLayout(layout=1);
}

module BoxLayoutB() // `document` me
{
  BoxLayout(layout=2);
}

module BoxLayoutC() // `document` me
{
  BoxLayout(layout=3);
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
