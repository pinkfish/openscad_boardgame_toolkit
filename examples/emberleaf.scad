// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//   http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

include <BOSL2/std.scad>
include <boardgame_toolkit.scad>
include <lib/emberleaf.scad>

$fn = 128;

default_lid_shape_type = SHAPE_TYPE_PENTAGON_R5;
default_lid_shape_thickness = 1;
default_lid_shape_width = 10;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;
default_label_font = "Impact";

default_label_type = LABEL_TYPE_FRAMELESS_ANGLE;

board_thickness = 23.5;

box_width = 287;
box_length = 287;
box_height = 79;

hex_size = 38.5;
trophy_width = 26;
trophy_length = 36;
wood_token_diameter = 15.5;
wood_token_thickness = 3;

frog_height = 17;
frog_width = 15.5;
frog_base = 12;

card_length = 91;
card_width = 66;
card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;
cardboard_token_thickness = 2;
small_victory_width = 20.5;
small_victory_length = 17.5;

token_thickness = 9;

player_box_height = (79 - board_thickness) / 4;
player_box_length = (box_length - 2) / 2;
player_box_width = card_length + default_wall_thickness * 2;

material_box_width = player_box_width;
material_box_height = player_box_height;
material_box_length = player_box_length / 2;

common_box_width = player_box_width;
common_box_height = player_box_height;
common_box_length = player_box_length;

card_box_width = player_box_width;
card_box_length = card_width + default_wall_thickness * 2 + 1;
card_box_height = box_height - board_thickness;

module PlayerBoxInside() {
  MakeBoxWithCapLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    // workers
    translate([12, 7, $inner_height - token_thickness - 0.5])for (i = [0:2]) {
      translate([0, 12 * i, 0])
        OwlWorker(height=player_box_height);
      translate([24, 12 * i, 0])
        rotate(180 * (i % 2))
          RabbitWorker(height=player_box_length);
      translate([45.5, 14.5 * i+1, 0])
        FrogWorker(height=player_box_height);
      translate([65, 14.5 * i+1, 0])
        rotate(180 * (i % 2))
          RatWorker(height=player_box_height);
    }
    // markers
    translate(
      [
        $inner_width - wood_token_diameter / 2,
        60,
        $inner_height - wood_token_thickness * 3 - 0.5,
      ]
    ) {
      cyl(d=wood_token_diameter, h=player_box_height, anchor=BOTTOM);
      translate([-wood_token_diameter / 2, 0, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
    }
    translate(
      [
        $inner_width - wood_token_diameter * 3 / 2 - 5,
        60,
        $inner_height - wood_token_thickness * 2 - 0.5,
      ]
    ) {
      cyl(d=wood_token_diameter, h=player_box_height, anchor=BOTTOM);
      translate([wood_token_diameter / 2, 0, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
    }

    // victory.
    translate(
      [
        $inner_width - 12.5,
        $inner_length - hex_size - 14,
        $inner_height - single_card_thickness * 6 - 0.3 - cardboard_token_thickness - 0.5,
      ]
    ) {
      rotate(0) {
        VictoryToken(height=cardboard_token_thickness + 1);
        translate([-small_victory_length / 2, 0, 0])
          sphere(r=10, anchor=BOTTOM);
      }
    }

    translate(
      [
        10,
        $inner_length - hex_size - 16,
        $inner_height - single_card_thickness * 6 - 0.3 - cardboard_token_thickness - 0.5,
      ]
    ) {
      rotate(180) {
        VictoryTokenSmall(height=cardboard_token_thickness + 1);
        translate([-small_victory_length / 2, 0, 0])
          sphere(r=10, anchor=BOTTOM);
      }
    }

    // hero
    children(0);

    // cards
    translate(
      [
        card_length / 2,
        $inner_length - card_width / 2,
        $inner_height - single_card_thickness * 6 - 0.3,
      ]
    ) {
      cuboid([card_length, card_width, player_box_height], anchor=BOTTOM);
    }

    // Hexes (under the cards)
    translate(
      [
        hex_size / 2 + 2,
        $inner_length - hex_size / 2 - 3,
        $inner_height - single_card_thickness * 6 - 0.3 - cardboard_token_thickness * 3,
      ]
    ) {
      rotate(30)
        RegularPolygon(
          width=hex_size, shape_edges=6, height=player_box_height,
          finger_holes=[4]
        );
    }

    translate(
      [
        $inner_width - hex_size / 2 - 1,
        $inner_length - hex_size / 2 - 3,
        $inner_height - single_card_thickness * 6 - 0.3 - cardboard_token_thickness * 3,
      ]
    ) {
      rotate(30)
        RegularPolygon(
          width=hex_size,
          shape_edges=6, height=player_box_height,
          finger_holes=[3]
        );
    }

    // Depth to pull out pieces.
    translate([0, 0, $inner_height - token_thickness / 2])
      RoundedBoxAllSides(width=$inner_width, length=50, height=token_thickness, radius=5);
    translate([0, 0, $inner_height - token_thickness / 2])
      RoundedBoxAllSides(width=50, length=70, height=token_thickness, radius=5);
  }
}

module BlackPlayerBox() // `make` me
{
  PlayerBoxInside() {
    translate([27, 51, $inner_height - token_thickness - 0.5])
      BlackHero(height=player_box_height);
  }
}

module RedPlayerBox() // `make` me
{
  PlayerBoxInside() {
    translate([25, 51, $inner_height - token_thickness - 0.5])
      RedHero(height=player_box_height);
  }
}

module YellowPlayerBox() // `make` me
{
  PlayerBoxInside() {
    translate([25, 50, $inner_height - token_thickness - 0.5])
      YellowHero(height=player_box_height);
  }
}

module BluePlayerBox() // `make` me
{
  PlayerBoxInside() {
    translate([25, 53, $inner_height - token_thickness - 0.5])
      BlueHero(height=player_box_height);
  }
}

module GreyPlayerBox() // `make` me
{
  PlayerBoxInside() {
    translate([25, 50.5, $inner_height - token_thickness - 0.5])
      rotate(90)
        GreyHero(height=player_box_height);
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_height,
    text_str="Player", text_scale=0.5, font="Impact"
  );
}

module MaterialBox() // `make` me
{
  MakeBoxWithCapLid(
    width=material_box_width,
    length=material_box_length, height=material_box_height
  ) {
    RoundedBoxAllSides(
      width=$inner_width,
      length=$inner_length, height=$inner_height, radius=$inner_height - 2
    );
  }
}

module MaterialHoneyBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=material_box_width, length=material_box_length, height=material_box_height,
    text_str="Honey", text_scale=0.5, font="Impact"
  );
}

module MaterialWoodBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=material_box_width, length=material_box_length, height=material_box_height,
    text_str="Wood", text_scale=0.5, font="Impact"
  );
}

module MaterialFoodBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=material_box_width, length=material_box_length, height=material_box_height,
    text_str="Food", text_scale=0.5, font="Impact"
  );
}

module MaterialStoneBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=material_box_width, length=material_box_length, height=material_box_height,
    text_str="Stone", text_scale=0.5, font="Impact"
  );
}

module CommonBox() // `make` me
{
  MakeBoxWithCapLid(
    width=common_box_width,
    length=common_box_length, height=common_box_height
  ) {
    for (i = [0:1]) {
      for (j = [0:2]) {
        translate([(trophy_length / 2 + 5) * (1 + i * 2), (trophy_width / 2 + 2) * (1 + j * 2), $inner_height - cardboard_token_thickness + 0.5]) {
          cuboid([trophy_length, trophy_width, common_box_height], anchor=BOTTOM);
          translate([trophy_length / 2, 0, 0])
            sphere(r=15, anchor=BOTTOM);
          translate([-trophy_length / 2, 0, 0])
            sphere(r=15, anchor=BOTTOM);
        }
      }
      translate(
        [
          $inner_width / 2,
          $inner_length - wood_token_diameter / 2 - 10,
          $inner_height - wood_token_thickness - 0.5,
        ]
      ) {
        cyl(d=wood_token_diameter, h=wood_token_thickness * 2, anchor=BOTTOM);
        translate([wood_token_diameter / 2, 0, 1])
          sphere(r=10, anchor=BOTTOM);
        translate([-wood_token_diameter / 2, 0, 1])
          sphere(r=10, anchor=BOTTOM);
      }
    }
  }
}

module CardBoxHero() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length, height=card_box_height,
    lid_on_length=true
  ) {
    translate([0, 0, 0])
      cube([card_length, card_width, card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.02])
      FingerHoleBase(radius=20, height=card_box_height, spin=270);
  }
}

module CardBoxFavor() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length, height=card_box_height,
    lid_on_length=true
  ) {
    translate([0, 0, $inner_height - single_card_thickness * 88 + 2])
      cube([card_length, card_width, card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.02])
      FingerHoleBase(radius=20, height=card_box_height, spin=270);
  }
}

module CardBoxSolo() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length, height=card_box_height,
    lid_on_length=true
  ) {
    translate([0, 0, 0])
      cube([card_length, card_width, card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.02])
      FingerHoleBase(radius=20, height=card_box_height, spin=270);
  }
}

module CardBoxSoloLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Solo", lid_on_length=true
  );
}

module CardBoxFavorLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Favors", lid_on_length=true
  );
}

module CardBoxHerosLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Heros", lid_on_length=true
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    BlackPlayerBox();
    translate([0, player_box_length, 0])
      RedPlayerBox();
    translate([0, 0, player_box_height])
      YellowPlayerBox();
    translate([0, player_box_length, player_box_height])
      BluePlayerBox();
    translate([0, 0, player_box_height * 2])
      GreyPlayerBox();
    translate([0, player_box_length, player_box_height * 2])
      MaterialBox();
    translate([0, player_box_length + material_box_length, player_box_height * 2])
      MaterialBox();
    translate([0, 0, player_box_height * 3])
      MaterialBox();
    translate([0, material_box_length, player_box_height * 3])
      MaterialBox();
    translate([0, material_box_length * 2, player_box_height * 3])
      CommonBox();
    translate([player_box_width, 0, 0])
      CardBoxFavor();
    translate([player_box_width, card_box_length, 0])
      CardBoxHero();
    translate([player_box_width, card_box_length * 2, 0])
      CardBoxSolo();
  }
}

if (FROM_MAKE != 1) {
  PlayerBoxLid();
}
