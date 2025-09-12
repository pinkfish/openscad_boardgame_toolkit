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
include <lib/brink.scad>

default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_label_font = "Impact";

ambassador_card_box_width = box_width / 2 - 1;
ambassador_card_box_length = small_card_length + default_wall_thickness * 2;
ambassador_card_box_height = single_card_thickness * 25 + default_floor_thickness + default_lid_thickness + 0.5;
faction_card_box_height = single_card_thickness * 5 + default_floor_thickness + default_lid_thickness + 0.5;
rival_card_box_height = single_card_thickness * 4 + default_floor_thickness + default_lid_thickness + 0.5;
bonus_card_box_height = single_card_thickness * (5 + 10) + default_floor_thickness + default_lid_thickness + 0.5;

action_card_box_width = ambassador_card_box_width;
action_card_box_length = small_card_length + default_wall_thickness * 2;
action_card_box_height = single_card_thickness * 52 / 2 + default_floor_thickness + default_lid_thickness;
rider_card_box_height = single_card_thickness * 20 / 2 + default_floor_thickness + default_lid_thickness;

player_box_width = box_width - 2;
player_box_length = default_wall_thickness * 2 + class_ii_ship_length + voting_board_width + 32;
player_box_height = (box_height - board_thickness - cardboard_token_thickness - 0.5) / 5;

hex_box_width = box_width - 2;
hex_box_length = default_wall_thickness * 2 + hex_width * 3 / 2 + 6;
hex_box_height = ceil(25 / 3) * cardboard_token_thickness + default_floor_thickness + default_lid_thickness;
hex_bonus_box_height = ceil(8 / 3) * cardboard_token_thickness + default_floor_thickness + default_lid_thickness;

middle_height = box_height - board_thickness - hex_box_height - hex_bonus_box_height - 0.5 - cardboard_token_thickness - upgrade_thickness * 5;

faction_box_width = hex_box_width;
faction_box_length = hex_box_length;
faction_box_height = default_floor_thickness + default_lid_thickness + marker_cube_width + 1;

upgrade_board_box_width = default_wall_thickness * 2 + upgrade_width;
upgrade_board_box_length = hex_box_length;
upgrade_board_box_height = middle_height;

resource_box_length = hex_box_length;
resource_box_width = (box_width - upgrade_board_box_width - 1) / 2;
resource_box_height = middle_height / 2;

resource_box_2_length = ambassador_card_box_length;
resource_box_2_width = (ambassador_card_box_width) / 2;
resource_box_2_height = box_height - ambassador_card_box_height - faction_card_box_height - rival_card_box_height - bonus_card_box_height * 2 - 1;

spacer_card_width = ambassador_card_box_width;
spacer_card_length = ambassador_card_box_length;
spacer_card_back_height = box_height - action_card_box_height - rider_card_box_height - 1;

spacer_hexes_width = hex_box_width - upgrade_board_box_width;
spacer_hexes_length = hex_box_length;
spacer_hexes_height = upgrade_board_box_height;

echo([upgrade_board_box_height, cargo_thickness + round_nub_thickness + upgrade_thickness, player_box_height]);

module AmbassadorCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length,
    height=ambassador_card_box_height,
    lid_on_length=true
  ) {
    translate([0, (small_card_length - card_width) / 2, 0])
      cube([card_length, card_width, ambassador_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=15, height=ambassador_card_box_height);
  }
}

module AmbassadorCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length,
    lid_on_length=true, text_str="Ambassador"
  );
}

module FactionCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length, height=faction_card_box_height,
    lid_on_length=true
  ) {
    translate([0, (small_card_length - card_width) / 2, 0])
      cube([card_length, card_width, ambassador_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=15, height=faction_card_box_height);
  }
}

module FactionCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length,
    lid_on_length=true, text_str="Faction"
  );
}

module RivalCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length, height=rival_card_box_height,
    lid_on_length=true
  ) {
    translate([0, (small_card_length - card_width) / 2, 0])
      cube([card_length, card_width, ambassador_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=15, height=rival_card_box_height);
  }
}

module RivalCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length,
    lid_on_length=true, text_str="Rival"
  );
}

module ActionCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=action_card_box_width,
    length=action_card_box_length, height=action_card_box_height,
  ) {
    cube([small_card_width, small_card_length, action_card_box_height]);
    translate([small_card_width + 4.5, 0, 0])
      cube([small_card_width, small_card_length, action_card_box_height]);
    translate([small_card_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=10, height=action_card_box_height);
    translate([$inner_width - small_card_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=10, height=action_card_box_height);
  }
}

module ActionCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=action_card_box_width,
    length=action_card_box_length,
    text_str="Actions"
  );
}

module RiderCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=action_card_box_width,
    length=action_card_box_length, height=rider_card_box_height,
  ) {
    cube([small_card_width, small_card_length, action_card_box_height]);
    translate([small_card_width + 4.5, 0, 0])
      cube([small_card_width, small_card_length, action_card_box_height]);
    translate([small_card_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=10, height=action_card_box_height);
    translate([$inner_width - small_card_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=10, height=action_card_box_height);
  }
}

module RiderCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=action_card_box_width,
    length=action_card_box_length,
    text_str="Riders"
  );
}

module BonusCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=ambassador_card_box_width,
    length=ambassador_card_box_length, height=bonus_card_box_height,
    lid_on_length=true
  ) {
    translate([0, (small_card_length - card_width) / 2, $inner_height - 10 * single_card_thickness])
      cube([card_length, card_width, ambassador_card_box_height]);
    translate([0, ($inner_length - small_card_width) / 2, $inner_height - 15 * single_card_thickness])
      cube([small_card_length, small_card_width, ambassador_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=15, height=ambassador_card_box_height);
  }
}

module BonusCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=action_card_box_width,
    length=action_card_box_length,
    text_str="Community"
  );
}

module HoloBonusCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=action_card_box_width,
    length=action_card_box_length,
    text_str="Holo"
  );
}

module HexBox() // `make` me
{
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=hex_box_height, material_colour="lightgrey") {
    translate([PolygonRadiusFromApothem(hex_width, shape_edges=6) + 1, hex_width / 2 + 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, -PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }

    translate([$inner_width - PolygonRadiusFromApothem(hex_width, shape_edges=6) - 1, hex_width / 2 + 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, -PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }

    translate([$inner_width / 2, $inner_length - hex_width / 2 - 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }
  }
}

module HexBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=hex_box_width, length=hex_box_length, height=hex_box_height,
    text_str="Hexes"
  );
}

module HexBonusBox() // `make` me
{
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=hex_bonus_box_height, material_colour="lightgrey") {
    translate([PolygonRadiusFromApothem(hex_width, shape_edges=6) + 1, hex_width / 2 + 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, -PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }

    translate([$inner_width - PolygonRadiusFromApothem(hex_width, shape_edges=6) - 1, hex_width / 2 + 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, -PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }

    translate([$inner_width / 2, $inner_length - hex_width / 2 - 1, 0]) {
      RegularPolygon(shape_edges=6, width=hex_width, height=hex_box_height);
      translate([0, PolygonRadiusFromApothem(hex_width, shape_edges=6), 0])
        cuboid([25, 20, hex_box_height + 20], rounding=10, anchor=BOTTOM);
    }
  }
}

module HexBoxBonusLid() // `make` me
{
  CapBoxLidWithLabel(
    width=hex_box_width, length=hex_box_length, height=hex_box_height,
    text_str="Bonus"
  );
}

module PlayerBox(colour = "green") // `make` me
{
  MakeBoxWithCapLid(width=player_box_width, length=player_box_length, height=player_box_height, material_colour=colour) {
    // class i ship
    translate(
      [
        class_i_ship_diameter / 2 + 5,
        $inner_length - class_i_ship_diameter / 2 - 10,
        $inner_height - class_i_ship_thickness,
      ]
    )
      ClassIShip(player_box_height);

    // class ii ship
    translate(
      [
        class_ii_ship_width / 2 + class_i_ship_diameter + 7,
        $inner_length - class_ii_ship_length / 2 - 5,
        $inner_height - class_iii_ship_thickness,
      ]
    ) {
      ClassIIShip(player_box_height);
    }

    // class iii ship
    translate(
      [
        class_i_ship_diameter + class_ii_ship_width + class_iii_ship_radius,
        $inner_length - class_iii_ship_edge_length / 2 - 5,
        $inner_height - class_ii_ship_thickness,
      ]
    )
      ClassIIIShip(player_box_height);

    // indent for the ships.
    hull() {
      translate(
        [
          class_i_ship_diameter + class_ii_ship_width + class_iii_ship_radius * 2,
          $inner_length - class_iii_ship_edge_length / 2 - 5,
          $inner_height - class_ii_ship_thickness + 2,
        ]
      )
        sphere(r=class_ii_ship_thickness, anchor=BOTTOM);

      translate(
        [
          class_i_ship_diameter + class_ii_ship_width + 10,
          $inner_length - class_ii_ship_thickness,
          $inner_height - class_ii_ship_thickness + 2,
        ]
      )
        sphere(r=class_ii_ship_thickness, anchor=BOTTOM);
      translate(
        [
          class_i_ship_diameter + class_ii_ship_width + 10,
          $inner_length - class_ii_ship_length - 2,
          $inner_height - class_ii_ship_thickness + 2,
        ]
      )
        sphere(r=class_ii_ship_thickness, anchor=BOTTOM);
      translate(
        [
          class_ii_ship_thickness,
          $inner_length - class_ii_ship_length - 2,
          $inner_height - class_ii_ship_thickness + 2,
        ]
      )
        sphere(r=class_ii_ship_thickness, anchor=BOTTOM);
      translate(
        [
          class_ii_ship_thickness,
          $inner_length - class_ii_ship_thickness,
          $inner_height - class_ii_ship_thickness + 2,
        ]
      )
        sphere(r=class_ii_ship_thickness, anchor=BOTTOM);
    }

    // voting bit.
    translate(
      [
        $inner_width / 2,
        voting_board_width / 2 + 18,
        $inner_height - cardboard_token_thickness - 1,
      ]
    ) {
      cuboid([voting_board_length, voting_board_width, player_box_height], anchor=BOTTOM);
    }

    translate(
      [
        $inner_width / 2,
        cardboard_token_thickness / 2 + 0.5 + voting_board_width + 20,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      cuboid([screen_length, cardboard_token_thickness + 1, player_box_height], anchor=BOTTOM);
    }
    translate(
      [
        $inner_width / 2 - screen_length / 2,
        voting_board_width / 2 + 3.5,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      cuboid([cardboard_token_thickness + 2, voting_board_width * 2, player_box_height], anchor=BOTTOM);
    }
    translate(
      [
        $inner_width / 2 + screen_length / 2,
        voting_board_width / 2 + 3.5,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      cuboid([cardboard_token_thickness + 2, voting_board_width * 2, player_box_height], anchor=BOTTOM);
    }

    box_section = ( (voting_board_length + 1) / 5) - 1.5;
    for (i = [0:4]) {
      translate([($inner_width - voting_board_length) / 2 + (box_section + 1.5) * i, -1, 0]) {
        RoundedBoxAllSides(length=voting_board_width + 17, width=(voting_board_length / 5) - 1, height=player_box_height, radius=5);
      }
    }

    // Cargo stuff
    translate([$inner_width - cargo_width / 2 - 5, $inner_length - cargo_width / 2 - 3, $inner_height - cargo_thickness]) {
      CuboidWithIndentsBottom(size=[cargo_width, cargo_width, player_box_height], finger_holes=[0], finger_hole_radius=5);
      translate([0, 0, -round_nub_thickness])
        cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
    }
    translate([$inner_width - cargo_width / 2 - 5, $inner_length - cargo_width * 3 / 2 - 5, $inner_height - cargo_thickness]) {
      CuboidWithIndentsBottom(size=[cargo_width, cargo_width, player_box_height], finger_holes=[0], finger_hole_radius=5);
      translate([0, 0, -round_nub_thickness])
        cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
    }
    translate([$inner_width - cargo_width / 2 - 5, $inner_length - cargo_width * 5 / 2 - 7, $inner_height - cargo_thickness]) {
      CuboidWithIndentsBottom(size=[cargo_width, cargo_width, player_box_height]);
      translate([0, 0, -round_nub_thickness])
        cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
    }

    // Railgun stuff.
    for (i = [0:2]) {
      translate(
        [
          $inner_width - cargo_width * 3 / 2 - railgun_length / 2,
          $inner_length - railgun_width / 2 - 4 - (railgun_width + 5) * i,
          $inner_height - railgun_thickness,
        ]
      ) {
        CuboidWithIndentsBottom(size=[railgun_length, railgun_width, player_box_height], finger_holes=[2], finger_hole_radius=7);
        translate([railgun_length / 2 - railgun_nub_offset, 0, -round_nub_thickness])
          cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
      }
    }
    // Indent for all the upgrades.
    translate(
      [
        $inner_width - cargo_width - railgun_length - 10,
        $inner_length - railgun_width * 5 + 1,
        $inner_height - railgun_thickness + 1.5,
      ]
    ) {
      RoundedBoxAllSides(width=railgun_length + cargo_width + 10, length=cargo_width * 3 + 9, height=player_box_height, radius=5);
    }

    // PLayer tokens
    translate(
      [
        $inner_width / 2 - 7,
        $inner_length - class_ii_ship_length / 2 - 4,
        $inner_height - cardboard_token_thickness * 2 - 1,
      ]
    ) {
      CylinderWithIndents(player_token_diameter / 2, height=player_box_height, finger_holes=[90, 270], finger_hole_radius=10);
    }
    // Storage for stuff.
    translate(
      [
        $inner_width - cargo_width - railgun_length - 65,
        $inner_length - railgun_width * 5 + 4,
        0,
      ]
    ) {
      RoundedBoxAllSides(width=50, length=cargo_width * 3 + 7, height=player_box_height, radius=10);
    }
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_height,
    text_str="Player",
    text_scale=0.4
  );
}

module ResourceBox(colour = "green") // `make` me
{
  MakeBoxWithCapLid(width=resource_box_width, length=resource_box_length, height=resource_box_height, material_colour=colour) {
    color(colour)
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
  }
}

module Resource2Box(colour = "green") // `make` me
{
  MakeBoxWithCapLid(width=resource_box_2_width, length=resource_box_2_length, height=resource_box_2_height, material_colour=colour) {
    color(colour)
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_2_height, radius=5);
  }
}

module ResourceBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height,
    text_str="Resource",
    text_scale=0.4
  );
}

module UABoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height,
    text_str="UA",
    text_scale=0.4
  );
}
module StartTile(thickness) {
  translate([PolygonRadiusFromApothem(hex_width, shape_edges=6) * 1.5, hex_width / 2, 0]) {
    RegularPolygon(shape_edges=6, width=hex_width, height=thickness);
  }
  translate([PolygonRadiusFromApothem(hex_width, shape_edges=6) * 1.5, -hex_width / 2, 0]) {
    RegularPolygon(shape_edges=6, width=hex_width, height=thickness);
  }
  RegularPolygon(shape_edges=6, width=hex_width, height=thickness);
  translate([-PolygonRadiusFromApothem(hex_width, shape_edges=6) * 1.5, hex_width / 2, 0]) {
    RegularPolygon(shape_edges=6, width=hex_width, height=thickness);
  }
  translate([-PolygonRadiusFromApothem(hex_width, shape_edges=6) * 1.5, -hex_width / 2, 0]) {
    RegularPolygon(shape_edges=6, width=hex_width, height=thickness);
  }
}

module SpacerCardFront() // `make` me
{
  MakeBoxWithNoLid(length=spacer_card_length, width=spacer_card_width, height=spacer_card_front_height, hollow=true);
}

module UpgradeBoardsBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=upgrade_board_box_width,
    length=upgrade_board_box_length,
    height=upgrade_board_box_height
  ) {
    translate([0, 0, $inner_height - upgrade_thickness * 5 - 1])
      cube([upgrade_width, upgrade_length, upgrade_board_box_height]);
    translate([$inner_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=15, height=upgrade_board_box_height);

    // tokens
    translate([$inner_width / 2, $inner_length / 2 - favor_token_diameter - 3, $inner_height - upgrade_thickness * 5 - 1 - cardboard_token_thickness - 0.5])
      CylinderWithIndents(
        radius=favor_token_diameter / 2,
        height=upgrade_board_box_height, finger_hole_radius=10, finger_holes=[0, 180]
      );
    translate([$inner_width / 2, $inner_length / 2, $inner_height - upgrade_thickness * 5 - 1 - cardboard_token_thickness - 0.5])
      CylinderWithIndents(
        radius=favor_token_diameter / 2,
        height=upgrade_board_box_height, finger_hole_radius=10, finger_holes=[0, 180]
      );
    translate([$inner_width / 2, $inner_length / 2 + favor_token_diameter + 3, $inner_height - upgrade_thickness * 5 - 1 - cardboard_token_thickness - 0.5])
      CylinderWithIndents(
        radius=favor_token_diameter / 2,
        height=upgrade_board_box_height, finger_hole_radius=10, finger_holes=[0, 180]
      );
  }
}

module UpgradeBoardsBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=upgrade_board_box_width,
    length=upgrade_board_box_length,
    text_str="Upgrades"
  );
}

module SpacerCardBack() // `make` me
{
  MakeBoxWithNoLid(width=spacer_card_width, length=spacer_card_length, height=spacer_card_back_height, hollow=true);
}

module SpacerCardHexes() // `make` me
{
  MakeBoxWithNoLid(width=spacer_hexes_width, length=spacer_hexes_length, height=spacer_hexes_height, hollow=true);
}

module BoxLayout() {
  cube([1, box_length, box_height]);
  translate([0, ambassador_card_box_length, 0])
    cube([board_width, board_length, board_thickness]);
  AmbassadorCardBox();
  translate([0, 0, ambassador_card_box_height])
    FactionCardBox();
  translate([0, 0, ambassador_card_box_height + faction_card_box_height])
    RivalCardBox();
  translate([0, 0, ambassador_card_box_height + faction_card_box_height + rival_card_box_height])
    BonusCardBox();
  translate([0, 0, ambassador_card_box_height + faction_card_box_height + rival_card_box_height + bonus_card_box_height])
    BonusCardBox();
  translate([0, 0, ambassador_card_box_height + faction_card_box_height + rival_card_box_height + bonus_card_box_height * 2])
    Resource2Box(colour="lightgreen");
  translate([resource_box_2_width, 0, ambassador_card_box_height + faction_card_box_height + rival_card_box_height + bonus_card_box_height * 2])
    Resource2Box(colour="red");
  translate([ambassador_card_box_width, 0, 0])
    ActionCardBox();
  translate([ambassador_card_box_width, 0, action_card_box_height])
    RiderCardBox();
  translate([ambassador_card_box_width, 0, action_card_box_height + rider_card_box_height])
    SpacerCardBack();
  for (i = [0:4]) {
    translate([0, ambassador_card_box_length, player_box_height * i + board_thickness])
      PlayerBox(colour=["yellow", "orange", "purple", "blue", "green"][i]);
  }
  translate([0, 0, upgrade_thickness * 5]) {
    translate([0, ambassador_card_box_length + player_box_length, board_thickness])
      HexBox();
    translate([0, ambassador_card_box_length + player_box_length, hex_box_height + board_thickness])
      HexBonusBox();

    for (j = [0:1]) {
      for (i = [0:1]) {
        translate([i * resource_box_width + upgrade_board_box_width, ambassador_card_box_length + player_box_length, hex_box_height + board_thickness + hex_bonus_box_height + j * resource_box_height])
          ResourceBox(colour=["orange", "yellow", "pink", "lightblue"][i + j * 2]);
      }
    }

    translate([0, ambassador_card_box_length + player_box_length, hex_box_height + board_thickness + hex_bonus_box_height])
      UpgradeBoardsBox();
  }

  translate([0, ambassador_card_box_length + player_box_length, board_thickness])
    cube([screen_length, screen_width, upgrade_thickness * 5]);
}

module TestLayout() {
  difference() {
    cube([100, 40, 5]);
    translate([0, 0, 2]) {
      translate([20, 18, 0])
        ClassIIIShip(thickness=10);
      translate([55, 20, 0])
        rotate(90)
          ClassIIShip(10);
      translate([80, 20, 0])
        ClassIShip(10);
    }
  }
}

if (FROM_MAKE != 1) {
  EscherLizardSingle(20);
}
