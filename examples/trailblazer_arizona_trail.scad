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

box_width = 283;
box_length = 283;
box_height = 70;

default_lid_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_LEAF;

board_thickness = 17.5;
player_board_thickness = 10;

player_board_width = 154;
player_board_length = 268;

player_supersition_marker = 16;
player_resource_hex = 11;
player_grit_marker = 16;
player_currency_cube = 10;

mountain_height = 14;
mountain_width = 16;
mountain_top_width = 9;
mountain_top_height = 12;

venom_disk_diameter = 32.5;
roadrunner_cyote_hex = 43.5;

saguaro_width = 23;

flora_double_polyominoes = 45;
cardboard_token_thickness = 2;

large_mountain_width = 20.5;
large_mountain_height = 18;
large_mountain_top_width = 11;
large_mountain_top_height = 15;

lost_dutchman_height = 16.5;
lost_dutchman_width = 10.5;

saguaro_height = 35;
saguaro_base_width = 15;
saguaro_middle_width = 12;
saguaro_base_height = 4;
saguaro_stalk_width = 4.5;
saguaro_top_depth = 6;
saguaro_middle_depth = 21;

tortoise_height = 16.5;
tortoise_width = 30;

jackalope_height = 30;
jackalope_width = 21.5;

javelina_width = 30;
javelina_height = 21;

gila_monster_width = 37;
gila_monster_height = 16.5;

roadrunner_width = 27;
roadrunner_height = 25;

wood_token_thickness = 10.5;

player_aid_card_width = 83;
player_aid_card_length = 123;

animal_cards_width = 65;
animal_cards_length = 90;
animal_cards_thickness = 23;

backpack_cards_width = 45;
backpack_cards_length = 65;
backpack_cards_thickness = 30;

destination_cards_width = 81;
destination_cards_length = 122;
destination_cards_thickness = 23 - 2.5;

player_box_length = box_length / 2 - 1;
player_box_width = player_board_width / 2 - 1;
player_box_height = (box_height - board_thickness - player_board_thickness - 1) / 2;

destination_card_box_height = destination_cards_thickness + default_floor_thickness + default_lid_thickness + 1;
destination_card_box_width = destination_cards_length + default_wall_thickness * 2 + 1;
destination_card_box_length = destination_cards_width + default_wall_thickness * 2 + 1;

field_guide_card_box_length = animal_cards_width + default_wall_thickness * 2 + 1;
field_guide_card_box_width = destination_card_box_width;
field_guide_card_box_height = destination_card_box_height;

trails_card_box_length = backpack_cards_length + default_wall_thickness * 2 + 1;
trails_card_box_width = destination_card_box_width;
trails_card_box_height = destination_card_box_height;

pieces_box_length_1 = (box_length - 2) / 2 + 10;
pieces_box_length_2 = (box_length - 2) / 2 - 10;
pieces_box_width = destination_card_box_width;
pieces_box_height = cardboard_token_thickness * 4 + 1 + default_floor_thickness + default_lid_thickness + 1;

pieces_box_small_length_1 = (box_length - 2) / 2 + 10;
pieces_box_small_length_2 = (box_length - 2) / 2 - 10;
pieces_box_small_width = destination_card_box_width + player_box_width - player_board_width;
pieces_box_small_height = player_board_thickness;

pieces_box_cards_width = destination_card_box_width;
pieces_box_cards_length = box_length - destination_card_box_length - trails_card_box_length - field_guide_card_box_length - 2;
pieces_box_cards_height = destination_card_box_height;

two_size = 16; // cards
three_corner = 11; // cards
three_straight = 5; // 1
four_l_left = 4; // 2
four_l_right = 2; // 3
four_square = 4; // 1
four_zig_zag_left = 1; // 1
four_zig_zag_right = 1; // 1
four_t = 3; // 2
five_cross = 2; // 2
five_balanced_l = 2; // 3
five_t = 2; // 4
five_square_plus_left = 4; // 2
five_square_plus_right = 4; // 1
five_u = 2; // 2
five_corner = 2; // 1

module TwoShape(h) {
  linear_extrude(height=h) rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
}

module ThreeShape(h) {
  linear_extrude(height=h) rect([flora_double_polyominoes * 3 / 2, flora_double_polyominoes / 2], rounding=1);
}

module ThreeCorner(h) {
  linear_extrude(height=h) translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 4]) {
      translate([flora_double_polyominoes / 4, 0])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 4])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes], rounding=1);
    }
}

module FourLLeft(h) {
  linear_extrude(height=h) translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 2]) {
      translate([flora_double_polyominoes / 4, 0])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FourLRight(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 4, -flora_double_polyominoes / 2]) {
      translate([-flora_double_polyominoes / 4, 0])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FiveCross(h) {
  linear_extrude(height=h) translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 2]) {
      translate([flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FourSquare(h) {
  linear_extrude(height=h) {
    rect([flora_double_polyominoes, flora_double_polyominoes], rounding=1);
  }
}

module FourT(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 4, -flora_double_polyominoes / 2]) {
      translate([-flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FourZigZagRight(h) {
  linear_extrude(height=h) translate([0, -flora_double_polyominoes / 4]) {
      translate([-flora_double_polyominoes / 4, 0])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 4])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes], rounding=1);
      translate([flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
    }
}

module FourZigZagLeft(h) {
  linear_extrude(height=h) translate([0, -flora_double_polyominoes / 4]) {
      translate([flora_double_polyominoes / 4, 0])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([0, flora_double_polyominoes / 4])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes], rounding=1);
      translate([-flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
    }
}

module FiveCross(h) {
  linear_extrude(height=h) translate([0, 0]) {
      rect([flora_double_polyominoes / 2 * 3, flora_double_polyominoes / 2], rounding=1);
      rect([flora_double_polyominoes / 2, flora_double_polyominoes / 2 * 3], rounding=1);
    }
}

module FiveSquareLeft(h) {
  linear_extrude(height=h) translate([0, 0]) {
      rect([flora_double_polyominoes, flora_double_polyominoes], rounding=1);
      translate([flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes], rounding=1);
    }
}

module FiveSquareRight(h) {
  linear_extrude(height=h) translate([0, 0]) {
      rect([flora_double_polyominoes, flora_double_polyominoes], rounding=1);
      translate([-flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes / 2, flora_double_polyominoes], rounding=1);
    }
}

module FiveU(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 4, 0]) {
      translate([-flora_double_polyominoes / 4, flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 2])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FiveCorner(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 2, 0]) {
      translate([-flora_double_polyominoes / 2, -flora_double_polyominoes * 2 / 4])
        rect([flora_double_polyominoes * 3 / 2, flora_double_polyominoes / 2], rounding=1);
      rect([flora_double_polyominoes / 2, flora_double_polyominoes * 3 / 2], rounding=1);
    }
}

module FiveT(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 4, 0]) {
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 4])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      rect([flora_double_polyominoes / 2, flora_double_polyominoes * 4 / 2], rounding=1);
    }
}

module FiveL(h) {
  linear_extrude(height=h) translate([flora_double_polyominoes / 4, 0]) {
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes * 3 / 4])
        rect([flora_double_polyominoes, flora_double_polyominoes / 2], rounding=1);
      rect([flora_double_polyominoes / 2, flora_double_polyominoes * 4 / 2], rounding=1);
    }
}

module SmallMountain() {
  mountain_top = mountain_height - mountain_top_height;
  polygon(
    [
      [mountain_width / 2, -mountain_height / 2],
      [mountain_top_width / 2, mountain_height / 2 - (mountain_top)],
      [mountain_top_width / 2 - mountain_top - 1, mountain_height / 2],
      [-mountain_top_width / 2 + mountain_top + 1, mountain_height / 2],
      [-mountain_top_width / 2, mountain_height / 2 - (mountain_top)],
      [-mountain_width / 2, -mountain_height / 2],
    ],
  );
}

module LargeMountain() {
  mountain_top = large_mountain_height - large_mountain_top_height;
  polygon(
    [
      [large_mountain_width / 2, -large_mountain_height / 2],
      [large_mountain_top_width / 2, large_mountain_height / 2 - (mountain_top)],
      [large_mountain_top_width / 2 - mountain_top - 1, large_mountain_height / 2],
      [-large_mountain_top_width / 2 + mountain_top + 1, large_mountain_height / 2],
      [-large_mountain_top_width / 2, large_mountain_height / 2 - (mountain_top)],
      [-large_mountain_width / 2, -large_mountain_height / 2],
    ],
  );
}

module PlayerBox() // `make` me
{
  MakeBoxWithSlidingLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    translate([0, 0, $inner_height - wood_token_thickness / 2 + 0.2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=wood_token_thickness / 2, radius=4);
    // SUperstition markers.
    translate([player_supersition_marker / 2 + 5, player_supersition_marker + 12, $inner_height - wood_token_thickness - 0.5])
      cyl(h=wood_token_thickness + 1, d=player_supersition_marker, anchor=BOTTOM);
    translate([player_supersition_marker / 2 + player_supersition_marker + 7, player_supersition_marker + 12, $inner_height - wood_token_thickness - 0.5])
      cyl(h=wood_token_thickness + 1, d=player_supersition_marker, anchor=BOTTOM);
    // Small mountains
    translate([mountain_width / 2 + player_supersition_marker * 2 - 0.25, mountain_height / 2 + 7.5, $inner_height - wood_token_thickness - 0.5])
      linear_extrude(height=wood_token_thickness + 1) SmallMountain();
    translate([mountain_width / 2 + player_supersition_marker * 2 + 2 + mountain_width, mountain_height / 2 + 7.5, $inner_height - wood_token_thickness - 0.5])
      linear_extrude(height=wood_token_thickness + 1) SmallMountain();
    translate([mountain_width / 2 + player_supersition_marker * 3 / 2 + 3.75 + mountain_width, mountain_height + 16, $inner_height - wood_token_thickness - 0.5])
      linear_extrude(height=wood_token_thickness + 1) rotate(180) SmallMountain();
    // Large mountain
    translate([$inner_width / 2 - large_mountain_width / 2 - 2, $inner_length / 2 - large_mountain_height / 2 - 10, $inner_height - wood_token_thickness - 0.5])
      linear_extrude(height=wood_token_thickness + 1) LargeMountain();
    // grit marker
    translate([$inner_width / 2 + player_grit_marker / 2, $inner_length / 2 - large_mountain_height / 2 - 10, $inner_height - wood_token_thickness - 0.5])
      RegularPolygon(player_grit_marker, wood_token_thickness + 1, 6);
    translate([17, $inner_length / 2 - 4, 0]) {
      // Resource Hex
      for (i = [0:2]) {
        translate([player_resource_hex / 2 + i * (player_resource_hex + 3), player_resource_hex / 2, $inner_height - wood_token_thickness - 0.5])
          RegularPolygon(player_resource_hex, wood_token_thickness + 1, 6);
      }
      // Currency cubes
      for (i = [0:2]) {
        translate([player_currency_cube / 2 + i * (player_currency_cube + 3), 2 + player_resource_hex + player_currency_cube / 2, $inner_height - player_currency_cube - 0.5])
          cuboid([player_currency_cube, player_currency_cube, player_currency_cube + 1], anchor=BOTTOM);
      }
    }
    // Trackers
    for (i = [0:3]) {
      for (j = [0:2]) {
        translate([$inner_width - player_resource_hex / 2 - 9 - i * (player_resource_hex + 3), $inner_length - player_resource_hex / 2 - 8 - j * (player_resource_hex + 1), $inner_height - wood_token_thickness - 0.5])
          RegularPolygon(player_resource_hex, wood_token_thickness + 1, 6);
      }
    }
  }
}

module DestinationCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=destination_card_box_width, length=destination_card_box_length,
    height=destination_card_box_height, lid_on_length=true,
  ) {
    cube([$inner_width, $inner_length, destination_card_box_height]);
    translate([-0.1, destination_cards_width / 2, -default_floor_thickness - 0.01]) FingerHoleBase(
        radius=10, height=destination_card_box_height - default_lid_thickness + 0.02, spin=270,
      );
  }
}
module DestinationCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=destination_card_box_width, length=destination_card_box_length,
    lid_on_length=true, text_str="Destination",
  );
}

module FieldGuideCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=field_guide_card_box_width, length=field_guide_card_box_length,
    height=field_guide_card_box_height, lid_on_length=true,
  ) {
    cube([animal_cards_length + 1, $inner_length, field_guide_card_box_height]);
    translate([-0.1, field_guide_card_box_length / 2, -default_floor_thickness - 0.01]) FingerHoleBase(
        radius=10, height=field_guide_card_box_height - default_lid_thickness + 0.02, spin=270,
      );
  }
}
module FieldGuideCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=field_guide_card_box_width, length=field_guide_card_box_length,
    lid_on_length=true, text_str="Field Guide",
  );
}

module PiecesBoxOne() // `make` me
{
  MakeBoxWithSlidingLid(width=pieces_box_width, length=pieces_box_length_1, height=pieces_box_height) {

    translate(
      [
        flora_double_polyominoes * 2 / 4,
        flora_double_polyominoes * 3 / 4,
        $inner_height - cardboard_token_thickness * four_zig_zag_right - 0.5,
      ],
    ) {
      rotate(90)
        FourZigZagRight(h=cardboard_token_thickness * 4 + 1);
      translate([0, flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
      translate([0, -flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    translate(
      [
        flora_double_polyominoes * 4 / 4 + 1.5,
        flora_double_polyominoes * 7 / 4 + 4.5,
        $inner_height - cardboard_token_thickness * four_zig_zag_left - 0.5,
      ],
    ) {
      rotate(90)
        FourZigZagLeft(h=cardboard_token_thickness * 4 + 1);
      translate([0, flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
      translate([0, -flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // Three straight - 5
    translate(
      [
        $inner_width - flora_double_polyominoes * 3 / 4,
        flora_double_polyominoes / 4,
        $inner_height - cardboard_token_thickness * 4 - 0.5,
      ],
    ) {
      ThreeShape(h=cardboard_token_thickness * 4 + 1);
      translate([0, flora_double_polyominoes / 4, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
    }
    translate(
      [
        $inner_width - flora_double_polyominoes * 3 / 4,
        flora_double_polyominoes / 4 + flora_double_polyominoes / 2 + 1.5,
        $inner_height - cardboard_token_thickness * 1 - 0.75,
      ],
    ) {
      ThreeShape(h=cardboard_token_thickness * 4 + 1);
    }

    // Corner 5 size.
    translate(
      [
        flora_double_polyominoes * 3 / 4,
        flora_double_polyominoes * 4 / 2 + 6 + flora_double_polyominoes / 4,
        $inner_height - cardboard_token_thickness * five_corner - 0.5,
      ],
    ) {
      rotate(180)
        FiveCorner(h=cardboard_token_thickness * 4 + 1);
      translate([-flora_double_polyominoes / 4, flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // Square
    translate(
      [
        $inner_width - flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 5 / 2 + 6,
        $inner_height - cardboard_token_thickness * four_square - 0.5,
      ],
    ) {
      FourSquare(h=cardboard_token_thickness * 4 + 1);
      translate([0, -flora_double_polyominoes / 2, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // Square + right
    translate(
      [
        $inner_width - flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 3 / 2 + 3,
        $inner_height - cardboard_token_thickness * five_square_plus_right - 0.5,
      ],
    ) {
      rotate(90)
        FiveSquareRight(h=cardboard_token_thickness * five_square_plus_right + 1);
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 2, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }
  }
}

module PiecesBoxTwo() // `make` me
{
  MakeBoxWithSlidingLid(width=pieces_box_width, length=pieces_box_length_2, height=pieces_box_height) {

    // Five U
    translate(
      [
        $inner_width - flora_double_polyominoes * 3 / 4,
        flora_double_polyominoes * 8 / 4 + 4.5,
        $inner_height - cardboard_token_thickness * five_u - 0.5,
      ],
    ) {
      rotate(90)
        FiveU(h=cardboard_token_thickness * 4 + 1);
      translate([0, 0, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // Five Cross
    translate(
      [
        flora_double_polyominoes * 3 / 4 + 1.5,
        flora_double_polyominoes * 3 / 4 + 1.5,
        $inner_height - cardboard_token_thickness * five_cross - 0.5,
      ],
    ) {
      rotate(180)
        FiveCross(h=cardboard_token_thickness * 4 + 1);
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
      translate([flora_double_polyominoes / 4, flora_double_polyominoes / 4, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // L shapes (4 + 2)
    translate(
      [
        $inner_width - flora_double_polyominoes * 3 / 4,
        flora_double_polyominoes * 2 / 4,
        $inner_height - cardboard_token_thickness * four_l_left - 0.5,
      ],
    ) {
      rotate(90)
        FourLLeft(h=cardboard_token_thickness * 4 + 1);
      translate([-3, 0, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }

    // T shape.
    translate(
      [
        $inner_width - flora_double_polyominoes * 3 / 4 - 3,
        flora_double_polyominoes * 4 / 4 + 3,
        $inner_height - cardboard_token_thickness * four_t - 0.5,
      ],
    ) {
      rotate(90)
        FourT(h=cardboard_token_thickness * 4 + 1);
    }

    // Five square (4 + 4)
    translate(
      [
        flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 0 / 8 + flora_double_polyominoes * 4 / 2 + 3,
        $inner_height - cardboard_token_thickness * five_square_plus_left - 0.5,
      ],
    ) {
      rotate(180)
        FiveSquareLeft(h=cardboard_token_thickness * five_square_plus_left + 1);
      translate([flora_double_polyominoes / 2, 0, 0])
        cyl(r=12, anchor=BOTTOM, h=20, rounding=6);
    }
  }
}

module PiecesBoxThree() // `make` me
{
  MakeBoxWithSlidingLid(width=pieces_box_small_width, length=pieces_box_small_length_1, height=pieces_box_small_height) {
    translate(
      [
        flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 3 / 4,
        $inner_height - cardboard_token_thickness * four_l_right - 0.5,
      ],
    ) {
      rotate(0)
        FourLRight(h=cardboard_token_thickness * 4 + 1);
      translate([0, flora_double_polyominoes / 2, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
      translate([-flora_double_polyominoes / 4, -flora_double_polyominoes / 4, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
    }
    translate(
      [
        flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 9 / 4,
        $inner_height - cardboard_token_thickness * five_balanced_l - 0.5,
      ],
    ) {
      rotate(180)
        FiveL(h=cardboard_token_thickness * 4 + 1);
      translate([0, -flora_double_polyominoes * 6 / 8, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
      translate([flora_double_polyominoes / 4, flora_double_polyominoes * 2 / 4, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
    }
  }
}

module PiecesBoxFour() // `make` me
{
  MakeBoxWithSlidingLid(width=pieces_box_small_width, length=pieces_box_small_length_2, height=pieces_box_small_height) {
    translate(
      [
        flora_double_polyominoes * 4 / 8,
        flora_double_polyominoes * 5.5 / 4,
        $inner_height - cardboard_token_thickness * five_t - 0.5,
      ],
    ) {
      rotate(0)
        FiveT(h=cardboard_token_thickness * 4 + 1);
      translate([flora_double_polyominoes / 4, flora_double_polyominoes, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
      translate([flora_double_polyominoes / 4, -flora_double_polyominoes, 0])
        intersection() {
          sphere(r=15, anchor=BOTTOM);
          cyl(r=11, anchor=BOTTOM, h=20);
        }
    }
  }
}

module PiecesBoxCards() // `make` me
{
  MakeBoxWithSlidingLid(width=pieces_box_cards_width, length=pieces_box_cards_length, height=pieces_box_cards_height) {
    translate(
      [
        flora_double_polyominoes * 12 / 8 + 7,
        flora_double_polyominoes * 2 / 4,
        $inner_height - cardboard_token_thickness * floor(three_corner / 2) - 0.5,
      ],
    ) {
      ThreeCorner(h=cardboard_token_thickness * floor(three_corner / 2) + 1);
      translate([flora_double_polyominoes / 2, -flora_double_polyominoes / 4, 0])
        cyl(r=11, h=20, anchor=BOTTOM, rounding=5.5);
    }
    translate(
      [
        $inner_width - flora_double_polyominoes * 4 / 8,
        $inner_length - flora_double_polyominoes * 2 / 4,
        $inner_height - cardboard_token_thickness * (floor(three_corner / 2) + 1) - 0.5,
      ],
    ) {
      rotate(180)
        ThreeCorner(h=cardboard_token_thickness * (three_corner / 2 + 1) + 1);
      translate([0, -flora_double_polyominoes / 4, 0])
        cyl(r=11, h=20, anchor=BOTTOM, rounding=5.5);
    }
    translate(
      [
        flora_double_polyominoes * 2 / 8,
        $inner_length - flora_double_polyominoes * 2 / 4,
        $inner_height - cardboard_token_thickness * two_size / 2 - 0.5,
      ],
    ) {
      rotate(90)
        TwoShape(h=cardboard_token_thickness * two_size + 1);
      translate([flora_double_polyominoes / 4, -2, 0])
        cyl(r=11, h=20, anchor=BOTTOM, rounding=5.5);
    }
    translate(
      [
        flora_double_polyominoes * 6 / 8 + 3.5,
        flora_double_polyominoes * 2 / 4,
        $inner_height - cardboard_token_thickness * two_size / 2 - 0.5,
      ],
    ) {
      rotate(90)
        TwoShape(h=cardboard_token_thickness * two_size + 1);
      translate([-flora_double_polyominoes / 4, 4, 0])
        cyl(r=11, h=20, anchor=BOTTOM, rounding=5.5);
      translate([flora_double_polyominoes / 4, 0, 0])
        cyl(r=11, h=20, anchor=BOTTOM, rounding=5.5);
    }
  }
}

module TrailsCardsBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=trails_card_box_width, length=trails_card_box_length,
    height=trails_card_box_height, lid_on_length=true,
  ) {
    cube([backpack_cards_width + 1, $inner_length, trails_card_box_height]);
    translate([$inner_width - backpack_cards_width - 1, 0, 0])
      cube([backpack_cards_width, $inner_length, trails_card_box_height]);
    translate([backpack_cards_width / 2, -0.1, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=10, height=destination_card_box_height + 0.02, spin=0);
    translate([$inner_width - backpack_cards_width / 2, -0.1, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=10, height=destination_card_box_height + 0.02, spin=0);
  }
}

module TrailsCardsBoxLid() // `make` me
{

  SlidingBoxLidWithLabel(
    width=trails_card_box_width, length=trails_card_box_length, lid_on_length=true,
    text_str="Trails"
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    PlayerBox();
    translate([0, player_box_length, 0]) PlayerBox();
    translate([0, 0, player_box_height]) PlayerBox();
    translate([0, player_box_length, player_box_height]) PlayerBox();
    translate([player_box_width, 0, 0]) DestinationCardBox();
    translate([player_box_width, destination_card_box_length, 0]) TrailsCardsBox();
    translate([player_box_width, destination_card_box_length + trails_card_box_length, 0]) FieldGuideCardBox();
    translate([player_box_width, destination_card_box_length + trails_card_box_length + field_guide_card_box_length, 0]) PiecesBoxCards();
    translate([player_box_width, 0, destination_card_box_height]) PiecesBoxOne();
    translate([player_box_width, pieces_box_length_1, destination_card_box_height]) PiecesBoxTwo();
    translate([player_board_width, 0, destination_card_box_height + pieces_box_height]) PiecesBoxThree();
    translate([player_board_width, pieces_box_small_length_1, destination_card_box_height + pieces_box_height]) PiecesBoxFour();
  }
  translate([0, 0, box_height - player_board_thickness])
    cube([player_board_width, player_board_length, player_board_thickness]);
}

if (FROM_MAKE != 1) {
  TrailsCardsBoxLid();
}
