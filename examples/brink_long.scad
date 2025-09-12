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

long_player_box_gap = 30;
long_player_box_upgrade_buffer = 5;
long_player_box_length = box_length - 2;
long_player_box_width = (box_width - 2 - long_player_box_gap) / 2 + long_player_box_gap;
long_player_box_height = default_floor_thickness + default_lid_thickness + cargo_thickness + round_nub_thickness + upgrade_thickness + 0.0;

ambassador_card_box_width = box_width / 2 - 1;
ambassador_card_box_length = small_card_length + default_wall_thickness * 2;
ambassador_card_box_height = single_card_thickness * 25 + default_floor_thickness + default_lid_thickness + 0.5;
faction_card_box_height = long_player_box_height / 2;
rival_card_box_height = long_player_box_height / 2;
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
hex_box_height = box_height - long_player_box_height * 3 - 1 - board_thickness;
hex_bonus_box_height = ceil(8 / 3) * cardboard_token_thickness + default_floor_thickness + default_lid_thickness;

middle_height = box_height - board_thickness - hex_box_height - hex_bonus_box_height - 0.5 - cardboard_token_thickness - upgrade_thickness * 5;

faction_box_width = hex_box_width;
faction_box_length = hex_box_length;
faction_box_height = default_floor_thickness + default_lid_thickness + marker_cube_width + 1;

spacer_card_back_width = ambassador_card_box_width;
spacer_card_back_length = ambassador_card_box_length;
spacer_card_back_height = box_height - ambassador_card_box_height - faction_card_box_height - rival_card_box_height - bonus_card_box_height * 2 - 1;

upgrade_board_box_width = default_wall_thickness * 2 + upgrade_width;
upgrade_board_box_length = hex_box_length;
upgrade_board_box_height = middle_height;

resource_box_length = hex_box_length;
resource_box_width = (box_width - upgrade_board_box_width - 1) / 3;
resource_box_height = middle_height / 2;

spacer_card_back = box_height - action_card_box_height - rider_card_box_height - 1;

spacer_hexes_width = hex_box_width - upgrade_board_box_width;
spacer_hexes_length = hex_box_length;
spacer_hexes_height = upgrade_board_box_height;

long_resource_box_length = (box_length - 2 - action_card_box_width) / 5;
long_resource_box_width = box_width - long_player_box_width - 2;
long_resource_box_height = long_player_box_height;

long_resource_box_2_length = box_length - hex_box_length - action_card_box_length - 2;
long_resource_box_2_width = (box_width - 2) / 3;
long_resource_box_2_height = box_height - long_player_box_height * 3 - 1 - board_thickness;

spacer_middle_length = box_length - hex_box_length - action_card_box_length - 2;
spacer_middle_width = box_width - 2;
spacer_middle_height = box_height - long_player_box_height * 3 - 1 - board_thickness;

ur_box_length = upgrade_width - long_player_box_upgrade_buffer;
ur_box_width = box_width - (long_player_box_width - long_player_box_gap) * 2 - 2;
ur_box_height = long_player_box_height;

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
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=hex_box_height) {
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


module LongPlayerBox(colour = "green") // 'make' me
{
  MakePathBoxWithCapLid(
    path=[
      [0, 0],
      [0, long_player_box_length],
      [long_player_box_width, long_player_box_length],
      [long_player_box_width, long_player_box_length - default_wall_thickness * 2 - upgrade_width - long_player_box_upgrade_buffer],
      [long_player_box_width - long_player_box_gap, default_wall_thickness * 2 + upgrade_width + long_player_box_upgrade_buffer + 2],
      [long_player_box_width - long_player_box_gap, 0],
    ],
    height=long_player_box_height,
    material_colour=colour,
  ) {

    // Upgrade bit.
    translate(
      [
        10,
        $inner_length - upgrade_width - 2,
        0,
      ]
    ) {
      color(colour) translate([0, 0, $inner_height - upgrade_thickness - 0.5]) {
          cuboid([upgrade_length, upgrade_width, long_player_box_height], anchor=BOTTOM + LEFT + FRONT);
        }

      // Railgun stuff.
      for (i = [0:2]) {
        translate(
          [
            railgun_length / 2 + 18,
            railgun_width / 2 + 20 + (railgun_width + 9) * i,
            $inner_height - upgrade_thickness - 1 - railgun_thickness,
          ]
        ) {
          color(colour) CuboidWithIndentsBottom(size=[railgun_length, railgun_width, player_box_height], finger_holes=[2, 6], finger_hole_radius=7);
          color(colour) translate([railgun_length / 2 - railgun_nub_offset, 0, -round_nub_thickness])
              cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
        }
        translate(
          [
            railgun_length + cargo_width / 2 + 32,
            cargo_width / 2 + 15 + (cargo_width + 9) * i,
            $inner_height - upgrade_thickness - cargo_thickness,
          ]
        ) {
          color(colour)
            CuboidWithIndentsBottom(size=[cargo_width, cargo_width, player_box_height], finger_holes=[2, 6], finger_hole_radius=5);
          color(colour) translate([0, 0, -round_nub_thickness])
              cyl(d=round_nub, h=cargo_thickness, rounding=1, anchor=BOTTOM);
        }
      }

      // PLayer tokens
      translate(
        [
          railgun_length + cargo_width + 50 + player_token_diameter / 2,
          cargo_width / 2 + 38,
          $inner_height - upgrade_thickness - cardboard_token_thickness * 2 - 1,
        ]
      ) {
        color(colour)
          CylinderWithIndents(
            player_token_diameter / 2,
            height=player_box_height, finger_holes=[90, 270], finger_hole_radius=7
          );
      }

      // space for under stuff
      translate([3, 3, $inner_height - upgrade_thickness - 1 - class_ii_ship_thickness / 2]) {
        color(colour)
          RoundedBoxAllSides(width=upgrade_length - 26, length=upgrade_width - 6, height=player_box_height, radius=5);
      }
    }

    // class i ship
    translate(
      [
        $inner_width - class_ii_ship_length / 2 - 16,
        $inner_length - upgrade_width - 20 - class_iii_ship_apothem * 3 - class_ii_ship_length,
        $inner_height - upgrade_thickness - 1 - class_i_ship_thickness,
      ]
    ) color(colour)
        ClassIShip(player_box_height);

    // class ii ship
    translate(
      [
        $inner_width - class_ii_ship_length / 2 - 17,
        $inner_length - upgrade_width - 25 - class_iii_ship_apothem * 3,
        $inner_height - upgrade_thickness - 1 - class_ii_ship_thickness,
      ]
    ) {
      color(colour)
        rotate(90)
          ClassIIShip(player_box_height);
    }

    // class iii ship
    translate(
      [
        $inner_width - class_iii_ship_radius / 2 - 15,
        $inner_length - upgrade_width - 25,
        $inner_height - upgrade_thickness - 1 - class_iii_ship_thickness,
      ]
    ) {
      color(colour)
        sphere(r=20, anchor=BOTTOM);
      color(colour)
        ClassIIIShip(thickness=player_box_height);
    }

    // voting bit.
    translate(
      [
        voting_board_width / 2 + 25,
        voting_board_length / 2 + 8,
        $inner_height - cardboard_token_thickness - 1,
      ]
    ) {
      color(colour)
        cuboid([voting_board_width, voting_board_length, long_player_box_height], anchor=BOTTOM);
    }

    // Back of screen.
    translate(
      [
        cardboard_token_thickness / 2 + 0.5 + voting_board_width + 27,
        screen_length / 2 + (screen_length - voting_board_length) / 2,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      color(colour)
        cuboid([cardboard_token_thickness + 1, screen_length, long_player_box_height], anchor=BOTTOM);
    }

    translate(
      [
        voting_board_width / 2 + 10.5,
        (screen_length - voting_board_length) / 2,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      color(colour)
        cuboid([voting_board_width * 2, cardboard_token_thickness + 2, long_player_box_height], anchor=BOTTOM);
    }

    translate(
      [
        voting_board_width / 2 + 10.5,
        screen_length + 3,
        $inner_height - cardboard_token_thickness - 5,
      ]
    ) {
      color(colour)
        cuboid([voting_board_width * 2, cardboard_token_thickness + 2, player_box_height], anchor=BOTTOM);
    }

    box_section = ( (voting_board_length + 1) / 5) - 1.5;
    for (i = [0:4]) {
      color(colour) {
        translate([-1, (box_section + 1.5) * i + 8, 0]) {
          RoundedBoxAllSides(length=(voting_board_length / 5) - 1, width=voting_board_width + 25, height=player_box_height, radius=5);
        }
      }
    }
  }
}



module LongResourceBox(colour = "lightblue") // `make` me
{
  MakeBoxWithCapLid(width=long_resource_box_width, length=long_resource_box_length, height=long_resource_box_height, material_colour=colour) {
    color(colour)
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=long_resource_box_height, radius=5);
  }
}

module LongResource2Box(colour = "lightblue") // `make` me
{
  MakeBoxWithCapLid(width=long_resource_box_2_width, length=long_resource_box_2_length, height=long_resource_box_2_height, material_colour=colour) {
    color(colour)
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=long_resource_box_2_height, radius=5);
  }
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


module SpacerMiddle() // `make` me
{
  MakeBoxWithNoLid(length=spacer_middle_length, width=spacer_middle_width, height=spacer_middle_height, hollow=true);
}

module UrResourceBox() // `make` me
{
  MakeBoxWithCapLid(length=ur_box_length, width=ur_box_width, height=ur_box_height, material_colour="red") {
    translate([favor_token_diameter / 2 + 3, favor_token_diameter / 2 + 2, $inner_height - cardboard_token_thickness * 5])
      color("red")
        CylinderWithIndents(
          radius=favor_token_diameter / 2,
          height=upgrade_board_box_height, finger_hole_radius=10, finger_holes=[0, 180]
        );
    translate([0, favor_token_diameter + 5, 0])
      color("red")
        RoundedBoxAllSides(width=$inner_width, length=$inner_length - favor_token_diameter - 5, height=ur_box_height, radius=6);
  }
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

module BoxLayoutLong() {
  cube([1, box_length, box_height]);
  cube([box_width, box_length, 1]);
  translate([0, 0, box_height - board_thickness])
    cube([board_width, board_length, board_thickness]);

  player_colour = ["yellow", "orange", "purple", "blue", "green"];
  for (i = [0:2]) {
    translate([0, 0, long_player_box_height * i])
      LongPlayerBox(player_colour[0 + i * 2]);
    if (i != 2) {
      translate(
        [
          long_player_box_width + long_player_box_width - long_player_box_gap,
          long_player_box_length,
          long_player_box_height * i,
        ]
      )
        rotate(180)
          LongPlayerBox(player_colour[1 + i * 2]);
    }
  }
  for (i = [0:2]) {
    translate([box_width - long_resource_box_width, long_resource_box_length * i, long_player_box_height * 2])
      LongResourceBox(colour=["orange", "yellow", "pink"][i]);
    // translate([i * resource_box_2_width, hex_box_length, long_player_box_height * 3])
    // LongResource2Box(colour=["lightblue", "lightgreen", "red"][i]);
  }
  translate([0, box_length - action_card_box_length, long_player_box_height * 3]) {
    translate([0, 0, 0])
      BonusCardBox();
    translate([0, 0, bonus_card_box_height])
      AmbassadorCardBox();
    translate([action_card_box_width, 0, 0])
      ActionCardBox();
    translate([action_card_box_width, 0, action_card_box_height])
      RiderCardBox();
  }
  translate([box_width - 2, long_resource_box_length * 5, long_player_box_height * 2])
    rotate(90)
      RivalCardBox();
  translate([box_width - 2, long_resource_box_length * 5, long_player_box_height * 2 + rival_card_box_height])
    rotate(90)
      FactionCardBox();

  translate([0, hex_box_length, long_player_box_height * 3])
    SpacerMiddle();

  translate([0, hex_box_length, box_height - board_thickness - upgrade_thickness * 5])
    cube([screen_length, screen_width, upgrade_thickness * 5]);
  translate([0, 0, long_player_box_height * 3])
    HexBox();
  translate([long_resource_box_width, 0, long_player_box_height * 2])
    UrResourceBox();

  translate([0, hex_box_length, box_height - upgrade_thickness * 5 - cardboard_token_thickness - 0.5])
    cube([screen_length, screen_width, upgrade_thickness * 5]);
}

if (FROM_MAKE != 1) {
  BoxLayoutLong();
}
