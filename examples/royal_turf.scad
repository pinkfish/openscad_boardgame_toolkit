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

default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_label_font = "Impact";
default_lid_shape_type = SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL;
default_lid_shape_width = 20;
default_lid_catch_type = CATCH_BUMPS_SHORT;
default_wall_thickness = 3;

box_width = 176;
box_length = 225;
box_height = 35;

board_thickness = 6;
die_size = 19;

horse_card_width = 41;
horse_card_length = 61;

horse_standee_height = 32;
horse_standee_width = 27.5;
horse_standee_round = 16.5;
horse_standee_round_thickness = 2.5;

bet_size = 19.5;
person_marker_length = 38.5;

cardboard_thickness = 1.5;

player_box_width = box_width / 3;
player_box_length = bet_size + default_wall_thickness * 2 + 1;
player_box_height = (box_height - board_thickness - 1) / 2;

horse_box_width = box_width;
horse_box_length = horse_standee_height * 2 + default_wall_thickness * 3;
horse_box_height = box_height - board_thickness;

horse_tile_box_width = box_width;
horse_tile_box_length = horse_card_length + default_wall_thickness * 2;
horse_tile_box_height = box_height - board_thickness;

money_box_width = box_width / 2;
money_box_length = box_length - horse_box_length - player_box_length - horse_tile_box_length;
money_box_height = box_height - board_thickness;

spacer_box_width = money_box_width;
spacer_box_length = money_box_length;
spacer_box_height = money_box_height;

module PlayerBox() // `make` me
{
  MakeBoxWithSlidingLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - cardboard_thickness * 5 - 1])
      cuboid([bet_size, bet_size, cardboard_thickness * 5 + 1], anchor=BOTTOM);
    translate([$inner_width / 2, $inner_length / 2, $inner_height - cardboard_thickness - 0.5])
      cuboid([person_marker_length, bet_size, cardboard_thickness * 5 + 1], anchor=BOTTOM);
    translate([$inner_width / 2, 0, $inner_height - cardboard_thickness * 5 - 0.9])
      FingerHoleWall(radius=7, height=cardboard_thickness * 5 + 1);
  }
}

module PlayerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=player_box_width, length=player_box_length, text_str="Player"
  );
}

module MoneyBox() // `make` me
{
  MakeBoxWithCapLid(
    width=money_box_width, length=money_box_length, height=money_box_height, wall_thickness=3.5
  ) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=money_box_height, radius=money_box_height / 2);
  }
}

module MoneyBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=money_box_width, length=money_box_length, height=money_box_height, wall_thickness=3.5,
    text_str="Money"
  );
}

module HorseBox() // `make` me
{
  MakeBoxWithCapLid(
    width=horse_box_width, length=horse_box_length, height=horse_box_height
  ) {
    for (i = [0:3]) {
      translate(
        [
          $inner_width / 2 - (horse_standee_width + 2) * (1.5 - i),
          horse_standee_height / 2,
          $inner_height - horse_standee_round / 2 - horse_standee_round_thickness,
        ]
      ) {
        cuboid([horse_standee_width, horse_standee_height, horse_box_height], anchor=BOTTOM);
        translate([0, -horse_standee_height / 2, 0])
          ycyl(d=horse_standee_round, l=horse_standee_round_thickness + 0.5, anchor=FRONT);
      }
    }
    for (i = [0:2]) {
      translate(
        [
          $inner_width / 2 - (horse_standee_width + 2) * (1 - i),
          $inner_length - horse_standee_height / 2,
          $inner_height - horse_standee_round / 2 - horse_standee_round_thickness,
        ]
      ) {
        cuboid([horse_standee_width, horse_standee_height, horse_box_height], anchor=BOTTOM);
        translate([0, horse_standee_height / 2, 0])
          ycyl(d=horse_standee_round, l=horse_standee_round_thickness + 0.5, anchor=BACK);
      }
    }
  }
}

module HorseBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=horse_box_width, length=horse_box_length, height=horse_box_height, wall_thickness=3.5,
    text_str="Horses"
  );
}

module HorseCardBox() // `make` me
{
  MakeBoxWithCapLid(
    width=horse_tile_box_width,
    length=horse_tile_box_length,
    height=horse_tile_box_height
  ) {
    for (i = [0:2]) {
      translate(
        [
          $inner_width / 2 - (horse_card_width + default_wall_thickness) * (1 - i),
          $inner_length / 2,
          $inner_height - cardboard_thickness * 7 - 1,
        ]
      ) {
        cuboid([horse_card_width, horse_card_length, horse_tile_box_height], anchor=BOTTOM);
      }
      translate(
        [
          $inner_width / 2 - (horse_card_width + default_wall_thickness) * (1 - i),
          0,
          $inner_height - cardboard_thickness * 7 - 1,
        ]
      ) {
        FingerHoleWall(radius=13, height=cardboard_thickness * 7 + 1);
      }
    }
  }
}

module HorseCardBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=horse_tile_box_width, length=horse_tile_box_length, height=horse_tile_box_height, wall_thickness=3.5,
    text_str="Horse Tiles"
  );
}

module SpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_box_width,
    length=spacer_box_length,
    height=spacer_box_height,
    hollow=true
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    for (i = [0:2]) {
      translate([player_box_width * i, 0, 0])
        PlayerBox();
      translate([player_box_width * i, 0, player_box_height])
        PlayerBox();
    }
    translate([0, player_box_length, 0])
      MoneyBox();
    translate([money_box_width, player_box_length, 0])
      SpacerBox();
    translate([0, player_box_length + money_box_length, 0])
      HorseBox();
    translate([0, player_box_length + money_box_length + horse_box_length, 0])
      HorseCardBox();
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
