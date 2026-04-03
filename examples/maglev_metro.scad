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

player_board_width = 221;
player_board_length = 245;
player_board_thickness = 2.2;

game_board_width = 207;
game_board_length = 281;
game_board_thickness = 4.2;

game_board_base_width = 241;
game_board_base_length = 272;
game_board_base_thickness = 4.2;

factory_hex_width = 56;
factory_hex_thickness = 7.5;
factory_hex_radius = PolygonRadiusFromApothem(factory_hex_width, 6);

player_overlay_hex_width = 55.5;
player_overlay_hex_radius = PolygonRadiusFromApothem(player_overlay_hex_width, 6);
player_overlay_hex_thickness = 1.5;
player_overlay_hex_per_player = 18;

robot_width = 8.5;
robot_length = 18.5;
robot_thickness = 7;

start_token_diameter = 45.5;
start_token_thickness = 4;

train_width = 14;
train_length = 41.5;
train_thickness = 10;

card_width = 67;
card_length = 90;

card_box_width = default_wall_thickness * 2 + card_width;
card_box_length = default_wall_thickness * 2 + card_length;
card_box_height = box_height - game_board_base_thickness * 2 - player_board_thickness * 4;

robot_box_width = card_box_width - 10;
robot_box_length = box_length - card_box_length * 2;
robot_box_height = card_box_height / 4;

commuter_box_width = robot_box_width;
commuter_box_length = robot_box_length / 2;
commuter_box_height = robot_box_height;

commuter_box_small_width = box_width - game_board_base_width;
commuter_box_small_length = default_wall_thickness * 2 + robot_width * 6 + 2;
commuter_box_small_height = box_height - card_box_height;

start_token_box_width = 10;
start_token_box_length = robot_box_length;
start_token_box_height = box_height;

player_box_width = default_wall_thickness * 2 + player_overlay_hex_width;
player_box_length = box_width / 2;
player_box_height = (box_height - game_board_base_thickness * 2 - player_board_thickness * 4 - game_board_thickness * 2) / 2;

factory_tile_box_width = (box_width - card_box_width - player_box_width) / 2;
factory_tile_box_length = box_width / 4;
factory_tile_box_height = player_box_height;

metro_box_width = box_width - card_box_width - player_box_width;
metro_box_length = box_length - factory_tile_box_length * 2;
metro_box_height = default_wall_thickness + default_floor_thickness + factory_hex_thickness * 2;

spacer_box_width = metro_box_width;
spacer_box_length = metro_box_length;
spacer_box_height = factory_tile_box_height * 2 - metro_box_height;

spacer_box_top_height = commuter_box_small_height;

module MetroTile(thickness = 2) {
  for (i = [0:2]) {
    rotate([0, 0, i * 120])
      translate([factory_hex_radius, 0, 0])
        RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
  }
}

module CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, card_box_height]
  ) {
    cube([$inner_width, $inner_length, box_height]);
  }
}

module CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, card_box_height], text_str="Cards"
  );
}

module FactoryTileBox(colour = "yellow") // `make` me
{
  MakeBoxWithSlidingLid(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - factory_hex_thickness * 2])
      rotate(90)
        RegularPolygon(width=factory_hex_width, height=factory_tile_box_height, shape_edges=6);

    translate([0, $inner_length / 2, 0])
      FingerHoleWall(
        radius=17,
        height=factory_tile_box_height - default_lid_thickness - default_floor_thickness,
        spin=90
      );
  }
}

module FactoryTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Factories"
  );
}

module FactoryTileBoxLidWarehouse() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Warehouses"
  );
}

module FactoryTileBoxLidLabs() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Labs"
  );
}

module FactoryTileBoxLidOffices() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Offices"
  );
}

module FactoryTileBoxLidStores() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Stores"
  );
}

module FactoryTileBoxLidEmbassies() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[factory_tile_box_width, factory_tile_box_length, factory_tile_box_height],
    lid_on_length=true, text_str="Embassies"
  );
}

module PlayerBox(colour = "green") // `make` me
{
  MakeBoxWithSlidingLid(
    size=[player_box_width, player_box_length, player_box_height],
    material_colour=colour, lid_on_length=true
  ) {
    translate([player_overlay_hex_width / 2, player_overlay_hex_radius, $inner_height - player_overlay_hex_per_player * player_overlay_hex_thickness / 2 - 1])
      rotate(90)
        RegularPolygon(width=player_overlay_hex_width, height=player_box_height, shape_edges=6);

    translate([player_overlay_hex_width / 2, $inner_length - player_overlay_hex_radius, $inner_height - player_overlay_hex_per_player * player_overlay_hex_thickness / 2 - 1])
      rotate(90)
        RegularPolygon(width=player_overlay_hex_width, height=player_box_height, shape_edges=6);

    translate([0, player_overlay_hex_radius, 0])
      FingerHoleWall(radius=17, height=player_box_height - default_lid_thickness - default_floor_thickness, spin=90);

    translate([0, $inner_length - player_overlay_hex_radius, 0])
      FingerHoleWall(radius=17, height=player_box_height - default_lid_thickness - default_floor_thickness, spin=90);

    translate([$inner_width / 2, $inner_length / 2, $inner_height - train_thickness])
      CuboidWithIndentsBottom(
        [train_length, train_width, train_thickness + 1], anchor=BOTTOM,
        finger_holes=[], finger_hole_radius=10, rounding=2, edges=[
          FRONT + LEFT,
          FRONT + RIGHT,
          BACK + LEFT,
          BACK + RIGHT,
          BOTTOM + LEFT,
          BOTTOM + RIGHT,
        ]
      );

    translate([$inner_width / 2, $inner_length / 2, $inner_height - train_thickness])
      cuboid(
        [20, train_length, train_thickness + 1], anchor=BOTTOM, rounding=10,
        edges=[BOTTOM + LEFT, BOTTOM + RIGHT]
      );
  }
}

module PlayerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[player_box_width, player_box_length, player_box_height],
    lid_on_length=true, text_str="Player"
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
    translate([$inner_width / 2, $inner_length / 2, $inner_height - robot_thickness])
      cuboid([robot_length * 3, robot_width * 5, robot_thickness + 1], anchor=BOTTOM);
  }
}

module CommuterBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[commuter_box_width, commuter_box_length, commuter_box_height], text_str="Commuter"
  );
}

module CommuterBoxSmall(colour) // `make` me
{
  MakeBoxWithCapLid(
    size=[commuter_box_small_width, commuter_box_small_length, commuter_box_small_height],
    material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - robot_thickness])
      cuboid([robot_length * 2, robot_width * 6, robot_thickness + 1], anchor=BOTTOM);
  }
}

module CommuterBoxSmallLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[commuter_box_small_width, commuter_box_small_length, commuter_box_small_height], text_str="Commuter"
  );
}

module MetroTileBox(colour = "yellow") // `make` me
{
  MakeBoxWithSlidingLid(
    size=[metro_box_width, metro_box_length, metro_box_height],
    lid_on_length=true, material_colour=colour
  ) {
    translate([factory_hex_width, factory_hex_radius * 3 / 2, $inner_height - factory_hex_thickness])
      rotate(90)
        MetroTile(thickness=factory_hex_thickness + 1);
    translate([$inner_width - factory_hex_width / 2, $inner_length - factory_hex_radius, $inner_height - factory_hex_thickness * 2])
      rotate(90)

        RegularPolygon(width=factory_hex_width, height=metro_box_height, shape_edges=6);
  }
}

module MetroTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[metro_box_width, metro_box_length, metro_box_height],
    lid_on_length=true, text_str="Metro & Studios"
  );
}

module StartTokenBox() // `make` me 
{
  MakeBoxWithNoLid(
    size=[start_token_box_width, start_token_box_length, start_token_box_height],
    finger_hole_size=20
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - start_token_diameter])
      cuboid(
        [start_token_thickness, start_token_diameter, start_token_diameter + 1], anchor=BOTTOM,
        rounding=start_token_diameter / 2, edges=[FRONT + BOTTOM, BACK + BOTTOM]
      );
  }
}

module SpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    size=[spacer_box_width, spacer_box_length, spacer_box_height],
    hollow=true
  ){}
}

module SpacerTop() // `make` me
{
  length = box_length - commuter_box_small_length * 2;
  small_width = start_token_box_width + 1;
  start_length = length - start_token_box_length - 1;
  path = [
    [0, 0],
    [commuter_box_small_width, 0],
    [commuter_box_small_width, length],
    [small_width, length],
    [small_width, start_length],
    [0, start_length],
  ];
  MakePathBoxWithNoLid(
    path=path, height=spacer_box_top_height, hollow=true,
    offset_sweep_options=object(offset="delta", check_valid=true, quality=1, steps=16)
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([box_width, 1, box_height]);
  }
  if (layout < 2) {
    translate([box_width - game_board_base_width, 0, box_height - game_board_base_thickness * 2])
      color("darkblue")
        cube([game_board_base_width, game_board_base_length, game_board_base_thickness * 2]);
    translate([box_width - player_board_width, 0, box_height - game_board_base_thickness * 2 - player_board_thickness * 4]) {
      for (i = [0:3]) {
        translate([0, 0, player_board_thickness * i])
          color(["green", "orange", "blue", "yellow"][i])
            cube([player_board_width, player_board_length, player_board_thickness]);
      }
    }
    translate([box_width - game_board_width, 0, box_height - game_board_base_thickness * 2 - player_board_thickness * 4 - game_board_thickness * 2]) {
      color("darkblue")
        cube([game_board_width, game_board_length, game_board_thickness * 2]);
    }
  }

  translate([0, 0, 0])
    CardBox();
  translate([0, card_box_length, 0])
    CardBox();
  factpory_colours = ["silver", "gold", "orange", "pink", "aqua", "coral", "purple"];

  for (i = [0:2])
    if (layout < 3 || i == 0) {
      translate([start_token_box_width, card_box_length * 2, i * robot_box_height])
        RobotBox(colour=factpory_colours[i]);
    }
  if (layout < 3) {
    for (i = [0:1]) {
      translate([start_token_box_width, card_box_length * 2 + commuter_box_length * i, robot_box_height * 3])
        CommuterBox(colour=factpory_colours[i + 3]);
    }
  }
  if (layout < 3) {
    translate([0, commuter_box_small_length, card_box_height])
      CommuterBoxSmall(colour=factpory_colours[5]);
    translate([0, 0, card_box_height])
      CommuterBoxSmall(colour=factpory_colours[6]);
    translate([0, commuter_box_small_length * 2, card_box_height])
      SpacerTop();
  }
  translate([0, card_box_length * 2, 0])
    StartTokenBox();

  for (j = [0:1]) {
    for (i = [0:1]) {
      if (layout < 3 || j == 0) {
        translate([card_box_width, player_box_length * i, j * player_box_height])
          PlayerBox(colour=["green", "orange", "blue", "yellow"][i + j * 2]);
      }
    }
  }

  for (i = [0:1]) {
    for (k = [0:1]) {
      for (j = [0:1]) {
        if (layout < 3 || i == 0) {
          translate([card_box_width + player_box_width + factory_tile_box_width * k, factory_tile_box_length * j, factory_tile_box_height * i])
            FactoryTileBox(colour=factpory_colours[i + j * 2 + k * 4]);
        }
      }
    }
  }
  translate([card_box_width + player_box_width, factory_tile_box_length * 2, 0])
    MetroTileBox(colour=factpory_colours[6]);
  if (layout < 3) {
    translate([card_box_width + player_box_width, factory_tile_box_length * 2, metro_box_height]) {
      SpacerBox();
    }
  }
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
  SpacerTop();
}
