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

default_lid_shape_type = SHAPE_TYPE_CLOUD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 12;
default_lid_aspect_ratio = 1.5;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;

box_length = 285;
box_width = 285;
box_height = 78;
board_thickness = 4;

player_board_thickness = 21;
player_board_width = 222;
player_board_length = 285;
token_thickness = 2;
wood_token_thickness = 10;

card_width = 68;
card_length = 92;

ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

player_deck_each = 28;

availability_card = 9;
knowledge_cards = 18;

community_needs_token_num = 18;

unmet_needs_size = 26;
unmet_needs_num = 18;

status_rank_size = 40;

status_awards_num = 48;
status_award_size = 24;
status_award_radius = status_award_size / 2 / cos(180 / 6);

meeple_length = 20;
meeple_width = 20;
meeple_head_diameter = 6.5;
meeple_leg_width = 7;
meeple_leg_total_width = 18;
meeple_leg_height = 9;
meeple_middle_width = 11;
meeple_arm_width = 6;
meeple_leg_v_top = 4;

wolf_head_width = 16;
wolf_head_length = 18.5;

player_box_length = (box_width - 2) / 3;
player_box_width = card_length + default_wall_thickness * 2 + 1;
player_box_height = wood_token_thickness + default_lid_thickness + default_floor_thickness + 3;

shared_box_width = player_box_width;
shared_box_length = (box_width - 2) / 2;
shared_box_height = box_height - player_box_height * 2 - board_thickness - player_board_thickness - 0.5;

side_box_width = (box_width - player_board_width);
side_box_length = box_length - 1;
side_box_height = box_height - board_thickness - 1;

resources_box_length = (box_width - 2) / 3;
resources_box_width = box_width - 2 - side_box_width - player_box_width;
resources_box_height = box_height - board_thickness - player_board_thickness - 0.5;

module Meeple(height) {
  module Leg() {
    hull() {
      translate([(meeple_leg_total_width - 1) / 2, -meeple_length / 2 + 0.5]) circle(r=0.5);
      translate([(meeple_leg_total_width - 1) / 2 - meeple_leg_width + 0.5, -meeple_length / 2 + 0.5])
        circle(r=0.5);
      translate([(meeple_middle_width - 1) / 2, -meeple_length / 2 + meeple_leg_height]) circle(r=0.5);
      translate([0, -meeple_length / 2 + meeple_leg_height]) circle(r=0.5);
      translate([0, -meeple_length / 2 + meeple_leg_v_top - 0.5]) circle(r=0.5);
    }
  }
  linear_extrude(height=height) {
    // head
    hull() {
      translate([0, meeple_length / 2 - meeple_head_diameter / 2]) circle(d=meeple_head_diameter);
      translate([meeple_arm_width / 2 + 1, -meeple_length / 2 + meeple_leg_height + meeple_arm_width - 0.5])
        circle(r=0.5);
      translate([-meeple_arm_width / 2 - 1, -meeple_length / 2 + meeple_leg_height + meeple_arm_width - 0.5])
        circle(r=0.5);
    }

    // legs
    Leg();
    mirror([1, 0]) Leg();

    // Arms
    hull() {
      translate(
        [
          (meeple_width - meeple_arm_width) / 2,
          -meeple_length / 2 + meeple_leg_height + meeple_arm_width / 2,
        ]
      ) circle(d=meeple_arm_width);
      translate(
        [
          -(meeple_width - meeple_arm_width) / 2,
          -meeple_length / 2 + meeple_leg_height + meeple_arm_width / 2,
        ]
      ) circle(d=meeple_arm_width);
    }
  }
}

module PlayerBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    cube([card_length, card_width, player_box_height]);
    translate([-1, card_width / 2, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=10, height=player_box_height, spin=270);
    translate([$inner_width / 2, $inner_length - meeple_length / 2, 0]) {
      Meeple(height=wood_token_thickness + 1);
      translate([0, 0, wood_token_thickness / 3])
        xcyl(r=10, h=meeple_width + 20, anchor=BOTTOM, rounding=10);
    }
  }
}

module PlayerBoxLid(generate_lid = true) // `make` me
{

  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_height,
    text_str="Player", label_colour="black"
  );
}

module UnmetNeedsBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(width=shared_box_width, length=shared_box_length, height=shared_box_height) {
    for (i = [0:1:2]) {
      translate(
        [
          i * (unmet_needs_size + 4) + 4 + unmet_needs_size / 2,
          12 + unmet_needs_size / 2,
          $inner_height - token_thickness * unmet_needs_num / 3 - 0.5,
        ]
      ) {
        CuboidWithIndentsBottom(
          [unmet_needs_size, unmet_needs_size, token_thickness * unmet_needs_num / 3 + 1],
          finger_holes=[2, 6], finger_hole_radius=12
        );
      }
    }
    translate([4, $inner_length - unmet_needs_size * 3, $inner_height - token_thickness * 3 - 0.5])
      HexGridWithCutouts(
        rows=3, cols=3, height=token_thickness * status_awards_num / 9, spacing=1,
        tile_width=status_award_size
      );
  }
}

module UnmetNeedsBoxLid(generate_lid = true) // `make` me
{

  CapBoxLidWithLabel(
    width=shared_box_width, length=shared_box_length, height=shared_box_height,
    text_str="Tokens", label_colour="black"
  );
}

module ExtraCardsBox(generate_lid = false) // `make` me
{
  MakeBoxWithCapLid(width=shared_box_width, length=shared_box_length, height=shared_box_height) {
    cube([card_length, card_width, shared_box_height]);
    translate([-1, card_width / 2, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=10, height=player_box_height, spin=270);

    translate(
      [
        status_rank_size / 2 + 4,
        $inner_length - status_rank_size / 2 - 4,
        $inner_height - token_thickness * 3 - 1,
      ]
    ) {
      CylinderWithIndents(
        radius=status_rank_size / 2, height=$inner_height, finger_holes=[45, 225],
        finger_hole_radius=10
      );
    }
    translate(
      [
        $inner_width - status_rank_size / 2 - 4,
        $inner_length - status_rank_size / 2 - 4,
        $inner_height - token_thickness * 3 - 1,
      ]
    ) {
      CylinderWithIndents(
        radius=status_rank_size / 2, height=$inner_height, finger_holes=[45, 225],
        finger_hole_radius=10
      );
    }
    // Start token.
    translate(
      [$inner_width / 2, card_width + wolf_head_width / 2 + 2, $inner_height - wood_token_thickness - 0.5]
    )
      CuboidWithIndentsBottom(
        size=[wolf_head_length, wolf_head_width, wood_token_thickness + 1],
        finger_holes=[0, 4], finger_hole_radius=10,
        finger_hole_height=wood_token_thickness / 2
      ) {
        translate([0, 0, -0.5]) linear_extrude(height=4)
            text("Wolf", size=4, valign="center", halign="center");
      }
  }
}

module ExtraCardsBoxLid(generate_lid = false) // `make` me
{

  CapBoxLidWithLabel(
    width=shared_box_width, length=shared_box_length, height=shared_box_height,
    text_str="Cards", label_colour="black"
  );
}

module ResourcesBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(width=resources_box_width, length=resources_box_length, height=resources_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resources_box_height, radius=10);
  }
}

module ResourcesBoxLid(generate_lid = true) // `make` me
{
  translate([resources_box_width + 10, 0, 0])
    CapBoxLidWithLabel(
      width=resources_box_width, length=resources_box_length, height=resources_box_height,
      text_str="Corn"
    );
  translate([resources_box_width * 2 + 20, 0, 0])
    CapBoxLidWithLabel(
      width=resources_box_width, length=resources_box_length, height=resources_box_height,
      text_str="Buffalo"
    );
  translate([resources_box_width * 3 + 30, 0, 0])
    CapBoxLidWithLabel(
      width=resources_box_width, length=resources_box_length, height=resources_box_height,
      text_str="Fish"
    );
}

module SideBox() // `make` me
{
  translate([side_box_width / 2, side_box_length / 2, side_box_height / 2]) difference() {
      color(default_material_colour) cuboid([side_box_width, side_box_length, side_box_height]);
      translate([0, 0, default_floor_thickness]) color(default_material_colour) cuboid(
            [
              side_box_width - default_wall_thickness * 2,
              side_box_length - default_wall_thickness * 2,
              side_box_height,
            ]
          );
    }
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([box_width, 1, box_height]);
  translate([0, 0, board_thickness]) {
    SideBox();
    for (i = [0:1:2]) {
      translate([side_box_width, i * player_box_length, 0]) PlayerBox(generate_lid=false);
      translate([side_box_width, i * player_box_length, player_box_height]) PlayerBox(generate_lid=false);
    }
    translate([side_box_width, 0, player_box_height * 2]) UnmetNeedsBox(generate_lid=false);
    translate([side_box_width, shared_box_length, player_box_height * 2]) ExtraCardsBox(generate_lid=false);
    for (i = [0:1:2]) {
      translate([side_box_width + player_box_width, i * resources_box_length, 0])
        ResourcesBox(generate_lid=false);
    }
  }
}

if (FROM_MAKE != 1) {
  ExtraCardsBox(generate_lid=false);
}
