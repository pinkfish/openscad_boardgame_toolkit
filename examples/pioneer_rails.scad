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

default_lid_shape_type = SHAPE_TYPE_PENROSE_TILING_7;
default_lid_shape_width = 25;
default_lid_shape_thickness = 1;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;
default_label_font = "Impact";
default_material_colour = "grey";
default_lid_catch_type = CATCH_BUMPS_LONG;

default_label_type = LABEL_TYPE_FRAMELESS;

board_thickness = 16;

box_width = 209;
box_length = 209;
box_height = 38;

card_width = 66.5;
card_length = 90;
card_thickness_20 = 15;
single_card_thickness = card_thickness_20 / 20;

pencil_width = 8;
pencil_length = 90;

eraser_width = 20;
eraser_length = 40;
eraser_thickness = 10;

dealer_token_diameter = 41;
token_thickness = 3;

goal_card_box_width = box_height - board_thickness;
goal_card_box_length = card_length + default_wall_thickness * 2;
goal_card_box_height = card_width + default_wall_thickness * 2;

pencil_box_length = pencil_length + eraser_width + default_wall_thickness * 3 + 1;
pencil_box_width = box_width - goal_card_box_height * 2 - 1;
pencil_box_height = box_height - board_thickness;

playing_card_box_width = pencil_box_height;
playing_card_box_length = card_length + default_wall_thickness * 2;
playing_card_box_height = card_width + default_wall_thickness * 2;

forest_card_box_width = pencil_box_height;
forest_card_box_length = card_length + default_wall_thickness * 2;
forest_card_box_height = card_width + default_wall_thickness * 2;

company_card_box_width = pencil_box_height;
company_card_box_length = card_length + default_wall_thickness * 2;
company_card_box_height = card_width + default_wall_thickness * 2;

spacer_front_length = box_length - pencil_box_length - 1;
spacer_front_width = pencil_box_width;
spacer_front_height = pencil_box_height;

spacer_side_length = box_length - goal_card_box_length * 2 - 1;
spacer_side_width = goal_card_box_height * 2;
spacer_side_height = pencil_box_height;

module PencilBox() // `make` me
{
  MakeBoxWithCapLid(length=pencil_box_length, width=pencil_box_width, height=pencil_box_height) {
    translate([$inner_width / 2, pencil_length / 2, $inner_height - pencil_width - 1 - token_thickness])
      cuboid([pencil_width * 4, pencil_length, pencil_box_height], anchor=BOTTOM);
    translate([$inner_width / 2, $inner_length - eraser_width / 2, $inner_height - eraser_thickness - 1])
      CuboidWithIndentsBottom(
        [eraser_length, eraser_width, pencil_box_height], anchor=BOTTOM,
        finger_holes=[0]
      );
    translate([$inner_width / 2, pencil_length / 2, $inner_height - token_thickness - 0.5])
      CylinderWithIndents(radius=dealer_token_diameter / 2, height=pencil_box_height);
  }
}

module PencilBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    length=pencil_box_length, width=pencil_box_width, height=pencil_box_height,
    text_str="Pencils"
  ){}
}

module GoalCardsBox() // `make` me
{
  translate([0, 0, goal_card_box_width])
    rotate([0, 90, 0])
      MakeBoxWithSlidingLid(
        width=goal_card_box_width, length=goal_card_box_length, height=goal_card_box_height,
        material_colour="orange"
      ) {
        cube([$inner_width, card_length, goal_card_box_height]);
        translate([-1, $inner_length / 2, $inner_height - 20 + default_lid_thickness])
          FingerHoleWall(radius=20, height=20, depth_of_hole=goal_card_box_width * 2 + 2, spin=90);
      }
}

module GoalCardsLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=goal_card_box_width, length=goal_card_box_length, text_str="Goal",
    label_type=LABEL_TYPE_FRAMELESS,
  );
}

module PlayingCardsBox() // `make` me
{
  translate([0, 0, playing_card_box_width])
    rotate([0, 90, 0])
      MakeBoxWithSlidingLid(
        width=playing_card_box_width, length=playing_card_box_length, height=playing_card_box_height,
        material_colour="white"
      ) {
        cube([$inner_width, card_length, playing_card_box_height]);
        translate([-1, $inner_length / 2, $inner_height - 20 + default_lid_thickness])
          FingerHoleWall(radius=20, height=20, depth_of_hole=playing_card_box_width * 2 + 2, spin=90);
      }
}

module PlayingCardsLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=playing_card_box_width, length=playing_card_box_length, text_str="Playing",
    label_type=LABEL_TYPE_FRAMELESS,
  );
}

module ForestCardsBox() // `make` me
{
  translate([0, 0, forest_card_box_width])
    rotate([0, 90, 0])
      MakeBoxWithSlidingLid(
        width=forest_card_box_width, length=forest_card_box_length, height=forest_card_box_height,
        material_colour="green"
      ) {
        cube([$inner_width, card_length, forest_card_box_height]);
        translate([-1, $inner_length / 2, $inner_height - 20 + default_lid_thickness])
          FingerHoleWall(radius=20, height=20, depth_of_hole=forest_card_box_width * 2 + 2, spin=90);
      }
}

module ForestCardsLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=forest_card_box_width, length=forest_card_box_length, text_str="Forest",
    label_type=LABEL_TYPE_FRAMELESS,
  );
}

module CompanyOwnerCardsBox() // `make` me
{
  translate([0, 0, playing_card_box_width])
    rotate([0, 90, 0]) {
      MakeBoxWithSlidingLid(
        width=company_card_box_width, length=company_card_box_length, height=company_card_box_height,
        material_colour="yellow"
      ) {
        cube([$inner_width - 2.5 - 1.5, card_length, company_card_box_height]);
        translate([$inner_width - 2.5, 0, 0])
          cube([2.5, card_length, company_card_box_height]);
        translate([-1, $inner_length / 2, $inner_height - 20 + default_lid_thickness])
          FingerHoleWall(radius=20, height=20, depth_of_hole=company_card_box_width * 2 + 2, spin=90);
      }
    }
}

module CompanyOwnerCardsLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=company_card_box_width, length=company_card_box_length, text_str="Company",
    label_type=LABEL_TYPE_FRAMELESS,
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
      translate([0, spacer_front_length / 2, spacer_front_height - 10])
        FingerHoleWall(20, 10, spin=90);
      translate([spacer_front_width - 2, spacer_front_length / 2, spacer_front_height - 10])
        FingerHoleWall(20, 10, spin=90);
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
      translate([spacer_side_width / 2, 1, spacer_side_height - 10])
        FingerHoleWall(20, 10);
      translate([spacer_side_width / 2, spacer_side_length - 2, spacer_side_height - 10])
        FingerHoleWall(20, 10);
    }
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    PencilBox();
    translate([0, pencil_box_length, 0])
      SpacerFront();
    translate([pencil_box_width, 0, 0])
      GoalCardsBox();
    translate([pencil_box_width + goal_card_box_height, 0, 0])
      PlayingCardsBox();
    translate([pencil_box_width, goal_card_box_length, 0])
      ForestCardsBox();
    translate([pencil_box_width + forest_card_box_height, goal_card_box_length, 0])
      CompanyOwnerCardsBox();
    translate([pencil_box_width, goal_card_box_length + forest_card_box_length, 0])
      SpacerSide();
  }
}

if (FROM_MAKE != 1) {
  PencilBox();
}
