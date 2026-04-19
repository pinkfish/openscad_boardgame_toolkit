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

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

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

loop_tile_thickness = 7.5;

metro_ticket_diameter = 25;
metro_ticket_thickness = 2;
metro_ticket_num = 20;

summon_width = 31;
summon_length = 74;
summon_top_width = 18;
summon_bottom_width = 24;
summon_top_offset = 14;
summon_thickness = 4;
summon_base_thickness = 2;
summon_base_person_width = 19;
summon_base_person_length = 26;
summon_base_top_offset = 28.5;

upgrade_width = 25;
upgrade_length = 42;
upgrade_thickness = 3.5;
upgrade_base_thickness = 1.5;
upgrade_base_person_width = 19;
upgrade_base_person_length = 26;
upgrade_base_top_offset = 2.5;

nanobot_diameter = 11;
nanobot_thickness = 10.5;

robot_width = 8.5;
robot_length = 18.5;
robot_thickness = 8;

card_width = 67;
card_length = 90;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

commuter_box_width = box_width - game_board_base_width;
commuter_box_length = box_length / 4;
commuter_box_height = game_board_base_thickness;

extra_hex_boxes_width = box_width - factory_hex_radius * 3.5 - default_wall_thickness * 2;
extra_hex_boxes_length = default_wall_thickness * 2 + factory_hex_width * 2 + 4;
extra_hex_boxes_height = box_height - player_board_thickness * 4 - game_board_thickness - game_board_base_thickness;

card_box_width = default_wall_thickness * 2 + card_width;
card_box_length = default_wall_thickness * 2 + card_length;
card_box_height = default_floor_thickness + default_lid_thickness + upgrade_thickness * 3 - upgrade_base_thickness;

upgrade_tile_box_width = card_box_width;
upgrade_tile_box_length = upgrade_length * 3;
upgrade_tile_box_height = card_box_height;

summon_box_width = extra_hex_boxes_width;
summon_box_length = default_wall_thickness * 2 + box_length - extra_hex_boxes_length - upgrade_tile_box_length;
summon_box_thickness = upgrade_tile_box_height;

outback_ghost_tiles_box_width = default_wall_thickness + factory_hex_radius * 3.5;
outback_ghost_tiles_box_length = default_wall_thickness + factory_hex_width * 4;
outback_ghost_tiles_box_height = box_height - game_board_thickness - game_board_base_thickness;

metro_token_box_width = outback_ghost_tiles_box_width;
metro_token_box_length = box_length - outback_ghost_tiles_box_length - 1;
metro_token_box_height = outback_ghost_tiles_box_height;

robot_box_width = extra_hex_boxes_width / 3;
robot_box_length = robot_length * 3.2 + 1 + default_wall_thickness * 2;
robot_box_height = box_height - card_box_height - commuter_box_height - game_board_base_thickness;

nanobot_box_width = robot_box_width;
nanobot_box_length = box_length - player_board_length - robot_box_length;
nanobot_box_height = robot_box_height;

player_board_spacer_width = extra_hex_boxes_width;
player_board_spacer_length = player_board_length - extra_hex_boxes_length - 1;
player_board_spacer_height = extra_hex_boxes_height - card_box_height;

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

module UpgradeTile() {
  translate([0, 0, upgrade_base_thickness])
    cuboid(
      [upgrade_width, upgrade_length, upgrade_thickness - upgrade_base_thickness],
      anchor=BOTTOM,
      rounding=0.5,
      edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
    );
  translate([0, upgrade_length / 2 - upgrade_base_person_length / 2 - upgrade_base_top_offset, 0])
    cuboid(
      [upgrade_base_person_width, upgrade_base_person_length, upgrade_base_thickness + 0.1],
      anchor=BOTTOM,
      rounding=1,
      edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
    );
}

module SummonTile(thickness = 2) {
  up(summon_base_thickness)
    linear_extrude(thickness - summon_base_thickness) {
      polygon(
        round_corners(
          [
            [summon_top_width / 2, summon_length / 2],
            [-summon_top_width / 2, summon_length / 2],
            [-summon_width / 2, summon_length / 2 - summon_top_offset],
            [-summon_bottom_width / 2, -summon_length / 2],
            [summon_bottom_width / 2, -summon_length / 2],
            [summon_width / 2, summon_length / 2 - summon_top_offset],
          ],
          radius=0.5
        )
      );
    }

  back(summon_length / 2 - summon_top_offset)
    cuboid(
      [summon_base_person_width, summon_base_person_length, summon_base_thickness + 0.1],
      anchor=BOTTOM + BACK,
      rounding=1,
      edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
    );
}

module LoopTiles(thickness = 2) {
  translate([0, -factory_hex_width * 0.5, 0]) {
    for (i = [0:1]) {
      translate([0, factory_hex_width * i, 0])
        RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
    }
    translate([factory_hex_radius * 3 / 2, factory_hex_width / 2, 0])
      RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
    translate([-factory_hex_radius * 3 / 2, factory_hex_width / 2, 0])
      RegularPolygon(factory_hex_width, height=thickness, shape_edges=6);
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

module UpgradeBox() // `make` me
{
  offset = upgrade_length - upgrade_base_person_length - upgrade_base_top_offset;
  module UpgradeHole() {
    translate([0, 0, 0])
      rotate(180)
        UpgradeTile();
    translate([0, offset / 2, upgrade_thickness - 0.01])
      cuboid(
        [upgrade_width, upgrade_length + offset, upgrade_thickness * 1.5],
        anchor=BOTTOM,
        rounding=0.5,
        edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
      );
    translate([0, upgrade_length / 2, upgrade_base_thickness])
      sphere(r=12, anchor=BOTTOM);
    translate([0, upgrade_length / 2 + offset, upgrade_thickness])
      sphere(r=12, anchor=BOTTOM);
  }
  MakeBoxWithCapLid(
    size=[upgrade_tile_box_width, upgrade_tile_box_length, upgrade_tile_box_height],
    material_colour="green"
  ) {
    translate([upgrade_width / 2 + 1, upgrade_length / 2 + 1, $inner_height - upgrade_thickness * 2 - upgrade_base_thickness + 0.5]) {
      UpgradeHole();
    }
    translate([$inner_width - upgrade_width / 2 - 1, upgrade_length / 2 + 1, $inner_height - upgrade_thickness * 2 - upgrade_base_thickness + 0.5]) {
      UpgradeHole();
    }

    translate([upgrade_width / 2, $inner_length - upgrade_length / 2 - 1, $inner_height - upgrade_thickness]) {
      UpgradeTile();
      translate([0, -upgrade_length / 2, upgrade_base_thickness])
        sphere(r=20, anchor=BOTTOM);
    }
    translate([$inner_width - upgrade_width / 2 - 1, $inner_length - upgrade_length / 2 - 1, $inner_height - upgrade_thickness * 2 - upgrade_base_thickness + 0.5]) {
      rotate(180)
        UpgradeHole();
    }
  }
}

module UpgradeBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[upgrade_tile_box_width, upgrade_tile_box_length, upgrade_tile_box_height], text_str="Upgrades"
  );
}

module ExtraTilesBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[extra_hex_boxes_width, extra_hex_boxes_length, extra_hex_boxes_height],
    positive_negative_children=[1],
    material_colour="orange"
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - loop_tile_thickness]) {
      {
        LoopTiles(thickness=loop_tile_thickness + 1);
        translate([factory_hex_radius, factory_hex_width / 2, -outback_tile_thickness])
          sphere(r=20, anchor=BOTTOM);
        translate([-factory_hex_radius, -factory_hex_width / 2, -outback_tile_thickness])
          sphere(r=20, anchor=BOTTOM);
      }
      translate([factory_hex_radius / 2, 0, -outback_tile_thickness - 0.25]) {
        OutbackSmallTile(thickness=outback_tile_thickness + 1);
      }
    }
    translate([$inner_width / 2, $inner_length / 2, $inner_height - loop_tile_thickness]) {
      translate([factory_hex_radius / 2, 0, -outback_tile_thickness - 0.46]) {
        text("Outback", valign="center", halign="center", size=10);
      }
      translate([-factory_hex_radius * 3 / 2, 0, -0.20]) {
        text("Loop", valign="center", halign="center", size=10);
      }
    }
  }
}

module ExtraTilesBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[extra_hex_boxes_width, extra_hex_boxes_length, extra_hex_boxes_height], text_str="Tiles"
  );
}

module SummonBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[summon_box_width, summon_box_length, summon_box_thickness],
    material_colour="purple"
  ) {
    translate([summon_length / 2 + 1, $inner_length / 2, $inner_height - summon_thickness * 2]) {
      rotate(90)
        SummonTile(thickness=summon_thickness * 2);
      translate([summon_length / 2, 0, summon_base_thickness])
        sphere(r=20, anchor=BOTTOM);
    }
    translate([$inner_width - summon_length / 2 - 1, $inner_length / 2, $inner_height - summon_thickness * 2]) {
      rotate(270)
        SummonTile(thickness=summon_thickness * 2);
      translate([-summon_length / 2, 0, summon_base_thickness])
        sphere(r=20, anchor=BOTTOM);
    }
  }
}

module SummonBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[summon_box_width, summon_box_length, summon_box_thickness], text_str="Summons"
  );
}

module MetroTokensBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[metro_token_box_width, metro_token_box_length, metro_token_box_height],
    material_colour="blue"
  ) {
    translate([1, 1, 0])
      RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, metro_token_box_height], radius=10);
  }
}

module MetroTokensBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[metro_token_box_width, metro_token_box_length, metro_token_box_height], text_str="Metro"
  );
}

module NanobotBox(colour) // `make` me
{
  MakeBoxWithCapLid(
    size=[nanobot_box_width, nanobot_box_length, nanobot_box_height],
    material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - nanobot_thickness])
      cuboid([nanobot_diameter * 4.3, nanobot_diameter * 4.1, nanobot_thickness + 1], anchor=BOTTOM);
  }
}

module NanobotBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[nanobot_box_width, nanobot_box_length, nanobot_box_height], text_str="Nanobots"
  );
}

module RobotBox(colour) // `make` me
{
  MakeBoxWithCapLid(
    size=[robot_box_width, robot_box_length, robot_box_height],
    material_colour=colour
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - robot_thickness])
      cuboid([robot_width * 6, robot_length * 3.2, robot_thickness + 1], anchor=BOTTOM);
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

module GhostBox() // `make` me
{
  MakeBoxWithNoLid(size=[outback_ghost_tiles_box_width, outback_ghost_tiles_box_length, outback_ghost_tiles_box_height]) {
    translate([$inner_width / 2 - factory_hex_radius * 1 / 4 + default_wall_thickness, $inner_length / 2 - default_wall_thickness, $inner_height - outback_tile_thickness * 8 - 1]) {
      rotate(180)
        GhostAndOutbackTiles(thickness=outback_tile_thickness * 8 + 2);
      translate([$inner_width / 2, 0, 0])
        cuboid([factory_hex_width / 2, outback_ghost_tiles_box_length, outback_tile_thickness * 8 + 2], anchor=BOTTOM);
    }
  }
}

module PlayerBoxSpacer() // `make` me
{
  MakeBoxWithNoLid(
    size=[player_board_spacer_width, player_board_spacer_length, player_board_spacer_height],
    hollow=true
  ){}
}

module MiddleBoxSpacer() // `make` me
{
  outside_width = extra_hex_boxes_width - upgrade_tile_box_width - 2;
  outside_length = upgrade_tile_box_length - 2;
  path = [
    [outside_width, 0],
    [outside_width, outside_length],
    [0, outside_length],
    [0, card_box_length],
    [card_box_width, card_box_length],
    [card_box_width, 0],
  ];
  MakePathBoxWithNoLid(
    path=path, height=card_box_height, hollow=true,
    offset_sweep_options=object(offset="delta", check_valid=true, quality=1, steps=16)
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
  }
  if (layout < 3) {
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
  if (layout < 3) {
    for (i = [0:3]) {
      translate([0, commuter_box_length * i, box_height - game_board_thickness - game_board_base_thickness])
        CommuterBox(colour=factory_colours[i + 3]);
    }
  }
  if (layout < 4) {
    for (i = [0:2]) {

      translate([robot_box_width * i, player_board_length, card_box_height])
        RobotBox(colour=factory_colours[i]);
      translate([robot_box_width * i, player_board_length + robot_box_length, card_box_height])
        RobotBox(colour=factory_colours[i]);
    }
  }
  if (layout < 4) {
    translate([0, extra_hex_boxes_length, card_box_height])
      PlayerBoxSpacer();
  }
  translate([upgrade_tile_box_width, extra_hex_boxes_length, 0])
    MiddleBoxSpacer();
  translate([0, extra_hex_boxes_length, 0])
    UpgradeBox();
  translate([0, 0, 0])
    ExtraTilesBox();
  translate([upgrade_tile_box_width, extra_hex_boxes_length, 0])
    CardBox();
  translate([0, extra_hex_boxes_length + upgrade_tile_box_length, 0])
    SummonBox();
  translate([extra_hex_boxes_width, 0, 0]) {
    GhostBox();
    if (layout < 3) {
      translate([factory_hex_radius * 6 / 4 + default_wall_thickness, factory_hex_width * 2 - default_wall_thickness, default_floor_thickness])
        rotate(180)
          GhostAndOutbackTiles(thickness=outback_tile_thickness * 8);
    }
  }
  translate([extra_hex_boxes_width, outback_ghost_tiles_box_length, 0])
    MetroTokensBox();
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

module BoxLayoutD() // `document` me
{
  BoxLayout(layout=4);
}

if (FROM_MAKE != 1) {
  SummonBox();
}
