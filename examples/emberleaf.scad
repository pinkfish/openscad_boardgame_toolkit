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
default_material_colour = "green";

default_label_type = LABEL_TYPE_FRAMELESS_ANGLE;

board_thickness = 23.5;

box_width = 287;
box_length = 287;
box_height = 79;

hex_size = 38.5;
trophy_width = 26;
trophy_length = 36;
wood_token_diameter = 16.5;
wood_token_thickness = 4;

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
player_box_width = card_length + default_wall_thickness * 2 + 1;

material_box_width = player_box_width;
material_box_height = player_box_height;
material_box_length = player_box_length / 2;

common_box_width = player_box_width;
common_box_height = player_box_height;
common_box_length = player_box_length;

card_box_width = player_box_width;
card_box_length = card_width + default_wall_thickness * 2 + 1;
card_box_height = box_height - board_thickness;

player_card_box_width = box_width - player_box_width - card_box_width - 1;
player_card_box_length = card_length + default_wall_thickness * 2 + 1;
player_card_box_height = (79 - board_thickness) / 5;

spacer_front_height = box_height - board_thickness - 1;
spacer_front_width = player_card_box_width;
spacer_front_length = box_length - player_card_box_length - 1;

spacer_side_height = card_box_height;
spacer_side_width = card_box_width;
spacer_side_length = box_length - card_box_length * 3 - 1;

module PlayerBoxInside(colour = "pink") {
  MakeBoxWithCapLid(
    width=player_box_width,
    length=player_box_length, height=player_box_height, material_colour=colour
  ) {
    // workers
    translate([12, 7, $inner_height - token_thickness - 0.5])for (i = [0:4]) {
      translate([0, 12 * i, 0])
        OwlWorker(height=player_box_height);
      translate([24, 12 * i, 0])
        rotate(180 * (i % 2))
          RabbitWorker(height=player_box_length);
      translate([45.5, 14.5 * i + 1, 0])
        FrogWorker(height=player_box_height);
      translate([65, 15 * i + 1, 0])
        rotate(180 * (i % 2))
          RatWorker(height=player_box_height);
    }

    // hero
    children(0);

    // markers
    translate(
      [
        $inner_width - wood_token_diameter / 2,
        89,
        $inner_height - wood_token_thickness * 2 - 0.5,
      ]
    ) {
      cyl(d=wood_token_diameter, h=player_box_height, anchor=BOTTOM);
      translate([-wood_token_diameter / 2, 0, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
      translate([0, -wood_token_diameter / 2, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
    }
    translate(
      [
        $inner_width - wood_token_diameter * 3 / 2 - 5,
        89,
        $inner_height - wood_token_thickness * 2 - 0.5,
      ]
    ) {
      cyl(d=wood_token_diameter, h=player_box_height, anchor=BOTTOM);
      translate([wood_token_diameter / 2, 0, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
      translate([0, -wood_token_diameter / 2, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
    }

    translate(
      [
        $inner_width / 2,
        102,
        $inner_height - wood_token_thickness - 0.5,
      ]
    ) {
      cyl(d=wood_token_diameter, h=player_box_height, anchor=BOTTOM);
      translate([wood_token_diameter / 2, 0, 0])
        cyl(d=13, rounding=6, h=player_box_height, anchor=BOTTOM);
    }

    // victory (under tile)
    translate(
      [
        hex_size / 2,
        $inner_length - hex_size / 2,
        $inner_height - 0.3 - cardboard_token_thickness * 2 - 0.5,
      ]
    ) {
      rotate(0) {
        VictoryToken(height=player_box_height);
        translate([-small_victory_length / 2, 0, 0])
          sphere(r=10, anchor=BOTTOM);
      }
    }

    translate(
      [
        hex_size / 2 + 2,
        $inner_length - hex_size / 2,
        $inner_height - 0.3 - cardboard_token_thickness * 3 - 0.8,
      ]
    ) {
      {
        VictoryTokenSmall(height=player_box_height);
        translate([-small_victory_length / 2, 0, 0])
          sphere(r=10, anchor=BOTTOM);
      }
    }

    // Hexes (under the cards)
    translate(
      [
        hex_size / 2 + 2.5,
        $inner_length - hex_size / 2,
        $inner_height - 0.3 - cardboard_token_thickness * 1,
      ]
    ) {
      RegularPolygon(
        width=hex_size, shape_edges=6, height=player_box_height,
        finger_holes=[0]
      );
    }

    translate(
      [
        $inner_width - hex_size / 2 - 2.5,
        $inner_length - hex_size / 2,
        $inner_height - 0.3 - cardboard_token_thickness * 5,
      ]
    ) {
      RegularPolygon(
        width=hex_size,
        shape_edges=6, height=player_box_height,
        finger_holes=[2]
      );
    }

    // Depth to pull out pieces.
    translate([0, 0, $inner_height - token_thickness / 2])
      RoundedBoxAllSides(width=$inner_width, length=80, height=token_thickness, radius=5);
    translate([0, 0, $inner_height - token_thickness / 2])
      RoundedBoxAllSides(width=50, length=96, height=token_thickness, radius=5);
  }
}

module BlackPlayerBox() // `make` me
{
  PlayerBoxInside("black") {
    translate([27, 78, $inner_height - token_thickness - 0.5])
      BlackHero(height=player_box_height);
  }
}

module RedPlayerBox() // `make` me
{
  PlayerBoxInside("red") {
    translate([25, 78, $inner_height - token_thickness - 0.5])
      RedHero(height=player_box_height);
  }
}

module YellowPlayerBox() // `make` me
{
  PlayerBoxInside("yellow") {
    translate([25, 77, $inner_height - token_thickness - 0.5])
      YellowHero(height=player_box_height);
  }
}

module BluePlayerBox() // `make` me
{
  PlayerBoxInside("blue") {
    translate([25, 80, $inner_height - token_thickness - 0.5])
      BlueHero(height=player_box_height);
  }
}

module GreyPlayerBox() // `make` me
{
  PlayerBoxInside("grey") {
    translate([25, 76.5, $inner_height - token_thickness - 0.5])
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

module MaterialBox(colour) // `make` me
{
  MakeBoxWithCapLid(
    width=material_box_width,
    length=material_box_length, height=material_box_height,
    material_colour=colour
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
      cube([card_length + 1, card_width + 1, card_box_height]);
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
      cube([card_length + 1, card_width + 1, card_box_height]);
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
      cube([card_length + 1, card_width + 1, card_box_height]);
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

module CardBoxPlayer(colour) // `make` me
{
  MakeBoxWithSlidingLid(
    width=player_card_box_width,
    length=player_card_box_length, height=player_card_box_height,
    material_colour=colour
  ) {
    translate([($inner_width - card_width) / 2, 0, 0])
      cube([card_width + 1, card_length + 1, card_box_height]);
    translate([$inner_width / 2, 0, -default_floor_thickness - default_lid_thickness + 0.02])
      FingerHoleBase(radius=20, height=card_box_height, spin=0);
  }
}

module CardBoxPlayerLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Player"
  );
}

module SpacerFront() // `make` me
{
  color("blue")
    difference() {
      cuboid(
        [spacer_front_width, spacer_front_length, spacer_front_height],
        anchor=BOTTOM + FRONT + LEFT, rounding=2
      );
      translate([default_wall_thickness, default_wall_thickness, default_floor_thickness])
        cuboid(
          [spacer_front_width - default_wall_thickness * 2, spacer_front_length - default_wall_thickness * 2, spacer_front_height],
          anchor=BOTTOM + FRONT + LEFT, rounding=2
        );
      translate([0, spacer_front_length / 2, spacer_front_height - 20])
        FingerHoleWall(20, 20, spin=90);
      translate([spacer_front_width - 2, spacer_front_length / 2, spacer_front_height - 20])
        FingerHoleWall(20, 20, spin=90);
    }
}

module SpacerSide() // `make` me
{
  color("blue")
    difference() {
      cuboid(
        [spacer_side_width, spacer_side_length, spacer_side_height],
        anchor=BOTTOM + FRONT + LEFT, rounding=2
      );
      translate([default_wall_thickness, default_wall_thickness, default_floor_thickness])
        cuboid(
          [spacer_side_width - default_wall_thickness * 2, spacer_side_length - default_wall_thickness * 2, spacer_side_height],
          anchor=BOTTOM + FRONT + LEFT, rounding=2
        );
      translate([0, spacer_side_length / 2, spacer_side_height - 20])
        FingerHoleWall(20, 20, spin=90);
      translate([spacer_side_width - 2, spacer_side_length / 2, spacer_side_height - 20])
        FingerHoleWall(20, 20, spin=90);
    }
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
      MaterialBox("red");
    translate([0, player_box_length + material_box_length, player_box_height * 2])
      MaterialBox("grey");
    translate([0, 0, player_box_height * 3])
      MaterialBox("yellow");
    translate([0, material_box_length, player_box_height * 3])
      MaterialBox("brown");
    translate([0, material_box_length * 2, player_box_height * 3])
      CommonBox();
    translate([player_box_width, 0, 0])
      CardBoxFavor();
    translate([player_box_width, card_box_length, 0])
      CardBoxHero();
    translate([player_box_width, card_box_length * 2, 0])
      CardBoxSolo();
    translate([player_box_width, card_box_length * 3, 0]) SpacerSide();
    for (i = [0:4]) {
      translate([player_box_width * 2, 0, i * player_card_box_height])
        CardBoxPlayer(
          ["black", "blue", "yellow", "grey", "red"][i]
        );
    }
    translate([player_box_width * 2, player_card_box_length, 0]) SpacerFront();
  }
}

if (FROM_MAKE != 1) {
  YellowPlayerBox();
}
