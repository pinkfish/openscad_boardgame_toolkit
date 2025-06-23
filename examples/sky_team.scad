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

$fn = 128;

default_lid_thickness = 3;

default_lid_shape_type = SHAPE_TYPE_CLOUD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 11;
default_lid_layout_width = 10.3;
default_lid_aspect_ratio = 1.5;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

box_width = 177;
box_length = 247;
box_height = 49;

double_board_thickness = 4;
single_board_thickness = 2;

board_width = 175;
board_length = 245;
board_middle_width = 20;
board_middle_gap_width = 46;

wind_speed_direction_width = 81.5;
wind_speed_direction_length = 81.5;
wind_speed_middle_hole = 51;
wind_speed_corner_radius = 2;

blue_airplane_disameter = 50.5;

ice_brakes_width = 66;
ice_brakes_length = 114;

kerosene_board_length = 184;
kerosene_board_width = 35.5;

intern_board_length = 186;
intern_board_width = 29.5;

rules_player_stuff_thickness = 6;

airplan_angle_diameter = 60;
airplae_angle_thickness = 5;

cards_width = 68;
cards_length = 92;
card_thickness = 4;

dice_width = 16.5;
num__dice = 8;

switch_width = 10.5;

intern_width = 15.5;
intern_length = 26;
intern_top_length = 5;
intern_top_width = 12;
intern_bottom_top_width = 10;

reroll_token_diameter = 16.5;

keroscene_width = 10;
keroscene_length = 14;

approach_track_length_8 = 236;
approach_track_length_7 = 213;
approach_track_length_6 = 181;
approach_track_length_5 = 153;
approach_track_thickness_5 = 7.75;
approach_track_thickness_6 = 7;
approach_track_thickness_7 = 5;
approach_track_thickness_8 = 3.5;
approach_track_width = 50.5;

wood_place_marker_width = 7.5;
wood_piece_marker_length = 10;
wood_piece_marker_thickness = 5;

bottom_boxes_length = box_length - 2;
bottom_boxes_width = (box_width - 2) / 2;
bottom_boxes_height = default_lid_thickness + default_floor_thickness + airplae_angle_thickness + 0.5;

approach_track_box_width = approach_track_width + default_wall_thickness * 2 + 1;
appraoch_track_box_length = box_length - 2;
approach_track_box_height = approach_track_thickness_5 + default_floor_thickness + default_lid_thickness + 2;

dice_box_width = dice_width + default_wall_thickness * 2 + 2;
dice_box_length = appraoch_track_box_length;
dice_box_height = box_height - rules_player_stuff_thickness - double_board_thickness - bottom_boxes_height;

buttons_box_width = approach_track_box_width;
buttons_box_length = (box_length - 2) / 12;
buttons_box_height = dice_box_height - approach_track_box_height;

card_box_width = cards_length + default_wall_thickness * 2 + 1;
card_box_length = cards_width + default_wall_thickness * 2 + 1;
card_box_height = dice_box_height;

spacer_width = box_width - approach_track_box_width - dice_box_width - 2;
spacer_length = dice_box_length - card_box_length;
spacer_height = dice_box_height;

module WindSpeedPiece(height) {
  hull() {
    translate([wind_speed_corner_radius, wind_speed_corner_radius, 0])
      cyl(r=wind_speed_corner_radius, anchor=BOTTOM, h=height);
    translate([wind_speed_corner_radius, wind_speed_direction_length - wind_speed_corner_radius, 0])
      cyl(r=wind_speed_corner_radius, anchor=BOTTOM, h=height);
    translate([wind_speed_direction_width - wind_speed_corner_radius, wind_speed_corner_radius, 0])
      cyl(r=wind_speed_corner_radius, anchor=BOTTOM, h=height);
    translate([wind_speed_direction_width / 2, wind_speed_direction_length / 2.0])
      cyl(d=wind_speed_direction_width, h=height, anchor=BOTTOM);
  }
}

module InternPiece(height)

{
  translate([0, -intern_top_length / 2, 0])
    cuboid(
      [intern_width, intern_length - intern_top_length, height], anchor=BOTTOM, rounding=1,
      edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
    );
  hull() {
    translate([intern_top_width / 2, intern_length / 2, 0])
      cyl(r=1, h=height, anchor=BOTTOM + RIGHT + BACK);
    translate([-intern_top_width / 2, intern_length / 2, 0])
      cyl(r=1, h=height, anchor=BOTTOM + LEFT + BACK);
    translate([-intern_bottom_top_width / 2, intern_length / 2 - intern_top_length, 0])
      cuboid([1, 1, height], anchor=BOTTOM + LEFT + BACK);
    translate([intern_bottom_top_width / 2, intern_length / 2 - intern_top_length, 0])
      cuboid([1, 1, height], anchor=BOTTOM + RIGHT + BACK);
  }
}

module BasePiecesOne() // `make` me
{
  MakeBoxWithSlidingLid(width=bottom_boxes_width, length=bottom_boxes_length, height=bottom_boxes_height) {
    translate([0, 8, $inner_height - double_board_thickness - 0.5]) {
      CuboidWithIndentsBottom(
        [kerosene_board_width, kerosene_board_length, double_board_thickness + 0.6],
        anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT],
        finger_hole_radius=10
      );
      translate([kerosene_board_width / 2, kerosene_board_length / 2, -1]) rotate([0, 0, 90])
          linear_extrude(height=2) text("Kerosene", halign="center", valign="center", size=10);
    }
    translate([$inner_width - intern_board_width, 10, $inner_height - single_board_thickness - 0.5]) {
      CuboidWithIndentsBottom(
        [intern_board_width, intern_board_length, single_board_thickness + 0.6],
        anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT],
        finger_hole_radius=15
      );
      translate([intern_board_width / 2, intern_board_length / 2, -1]) rotate([0, 0, 90])
          linear_extrude(height=2) text("Intern", halign="center", valign="center", size=10);
    }
    for (i = [0:5]) {
      translate(
        [$inner_width / 2 + 3, 19 + (intern_length + 14) * i, $inner_height - single_board_thickness - 0.5]
      ) {
        InternPiece(height=single_board_thickness + 1);
        translate([0, 0, -1]) linear_extrude(height=2)
            text(str(i + 1), halign="center", valign="center", size=10);

        translate([0, intern_length / 2, 0]) cyl(r=9, h=20, rounding=5, anchor=BOTTOM);
      }
    }
    // 7th one
    translate(
      [
        $inner_width / 2 + 3 - intern_width - 5,
        19 + (intern_length + 14) * 5,
        $inner_height - single_board_thickness - 0.5,
      ]
    ) {
      InternPiece(height=single_board_thickness + 1);
      translate([0, 0, -1]) linear_extrude(height=2) text(str(7), halign="center", valign="center", size=10);

      translate([0, intern_length / 2, 0]) cyl(r=9, h=20, rounding=5, anchor=BOTTOM);
    }
  }
}

module BasePiecesTwo() // `make` me
{
  MakeBoxWithSlidingLid(width=bottom_boxes_width, length=bottom_boxes_length, height=bottom_boxes_height) {
    translate([10, 12, $inner_height - double_board_thickness - 0.5]) {
      CuboidWithIndentsBottom(
        [ice_brakes_width, ice_brakes_length, double_board_thickness + 0.6],
        anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT],
        finger_hole_radius=20
      );
      translate([ice_brakes_width / 2, ice_brakes_length / 2, -1]) rotate([0, 0, 90])
          linear_extrude(height=2) text("Ice Brakes", halign="center", valign="center", size=10);
    }
    translate([1, $inner_length - wind_speed_direction_length - 2, $inner_height - single_board_thickness - 0.5]) {
      WindSpeedPiece(height=single_board_thickness + 0.6);
      translate([wind_speed_direction_width / 2, 0, 0]) cyl(r=20, h=40, rounding=20, anchor=BOTTOM);
      translate([wind_speed_direction_width - 12, wind_speed_direction_length - 12, 0])
        cyl(r=20, h=40, rounding=20, anchor=BOTTOM);
      translate([wind_speed_direction_width / 2, wind_speed_direction_length / 2, -1]) rotate([0, 0, 135])
          linear_extrude(height=2) text("Wind Speed", halign="center", valign="center", size=10);
    }
  }
}

module BasePiecesLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=bottom_boxes_width, length=bottom_boxes_length,
    text_str="Sky Team"
  );
}

module ApproachTracks() // `make` me
{
  MakeBoxWithSlidingLid(
    width=approach_track_box_width, length=appraoch_track_box_length,
    height=approach_track_box_height
  ) {
    translate([0, 0, $inner_height - approach_track_thickness_8 - 0.5])
      cube([approach_track_width + 1, approach_track_length_8, approach_track_thickness_8 + 1]);
    translate([0, 0, $inner_height - approach_track_thickness_7 - 1])
      cube([approach_track_width + 1, approach_track_length_7, approach_track_thickness_7 + 1.25]);
    translate([0, 0, $inner_height - approach_track_thickness_6 - 1.5])
      cube([approach_track_width + 1, approach_track_length_6, approach_track_thickness_6 + 1.75]);
    translate([0, 0, $inner_height - approach_track_thickness_5 - 2])
      cube([approach_track_width + 1, approach_track_length_5, approach_track_thickness_5 + 2.5]);
    translate([$inner_width / 2, 0, 0]) FingerHoleWall(radius=10, height=approach_track_thickness_5 + 2.01);
  }
}

module ApproachTracksLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=approach_track_box_width, length=appraoch_track_box_length,
    text_str="Approach"
  );
}

module DiceBox() // `make` me
{
  MakeBoxWithCapLid(width=dice_box_width, length=dice_box_length, height=dice_box_height) {
    for (i = [0:num__dice - 1]) {
      translate([0, (dice_width + 0.75) * i + 10, $inner_height - dice_width - 2])
        cube([dice_width + 2, dice_box_width + 1, dice_width + 2.5]);
    }
    translate([$inner_width / 2, 10, 0]) cyl(r=9, h=40, anchor=BOTTOM, rounding=4);
    translate([$inner_width / 2, (dice_width + 0.75) * num__dice + 10 + dice_width / 2, 0])
      cyl(r=9, h=40, anchor=BOTTOM, rounding=4);
  }
}

module DiceBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=dice_box_width, length=dice_box_length, height=dice_box_height,
    text_str="Dice"
  );
}

module ButtonsBox() // `make` me
{
  MakeBoxWithSlidingLid(width=buttons_box_width, length=buttons_box_length, height=buttons_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=$inner_height + 5, radius=5);
  }
}

module ButtonsBoxDouble() // `make` me
{
  MakeBoxWithSlidingLid(width=buttons_box_width, length=buttons_box_length * 2, height=buttons_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=$inner_height + 5, radius=5);
  }
}

module ButtonsBoxOnePointFive() // `make` me
{
  MakeBoxWithSlidingLid(width=buttons_box_width, length=buttons_box_length * 1.5, height=buttons_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=$inner_height + 5, radius=5);
  }
}

module ButtonsBoxTripple() // `make` me
{
  MakeBoxWithSlidingLid(width=buttons_box_width, length=buttons_box_length * 3, height=buttons_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=$inner_height + 5, radius=5);
  }
}

module CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=card_box_height,
    lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - default_lid_thickness + 0.01])
      FingerHoleBase(radius=20, height=card_box_height, spin=270);
  }
}

module CardsBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Sky Team", lid_on_length=true
  );
}

module SpacerBox() // `make` me
{
  color("purple") translate([spacer_width / 2, spacer_length / 2, 0]) difference() {
        cuboid(
          [spacer_width, spacer_length, spacer_height], rounding=2, anchor=BOTTOM,
          edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
        );
        translate([0, 0, default_floor_thickness]) cuboid(
            [
              spacer_width - default_wall_thickness * 2,
              spacer_length - default_wall_thickness * 2,
              spacer_height + 10,
            ],
            anchor=BOTTOM, rounding=1
          );
      }
}

module ButtonsBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=buttons_box_width, length=buttons_box_length,
    text_str="Button"
  );
  translate([buttons_box_width + 10, 0, 0]) {
    SlidingBoxLidWithLabel(
      width=buttons_box_width, length=buttons_box_length * 2,
      text_str="Alerts"
    );

    translate([buttons_box_width + 10, 0, 0]) {
      SlidingBoxLidWithLabel(
        width=buttons_box_width, length=buttons_box_length * 2,
        text_str="Pengiun"
      );

      translate([buttons_box_width + 10, 0, 0]) {
        SlidingBoxLidWithLabel(
          width=buttons_box_width, length=buttons_box_length * 3,
          text_str="Plane"
        );

        translate([buttons_box_width + 10, 0, 0]) {
          SlidingBoxLidWithLabel(
            width=buttons_box_width, length=buttons_box_length,
            text_str="Marker"
          );

          translate([buttons_box_width + 10, 0, 0]) {
            SlidingBoxLidWithLabel(
              width=buttons_box_width, length=buttons_box_length,
              text_str="Kero"
            );
            translate([buttons_box_width + 10, 0, 0]) {
              SlidingBoxLidWithLabel(
                width=buttons_box_width, length=buttons_box_length * 2,
                text_str="Stuff"
              );
            }
          }
        }
      }
    }
  }
}

module BoxLayout() {
  cube([box_width, 1, box_height]);
  cube([box_width, box_length, rules_player_stuff_thickness]);
  translate([0, 0, rules_player_stuff_thickness]) {
    BasePiecesOne();
    translate([bottom_boxes_width, 0, 0]) BasePiecesTwo();
    translate([0, 0, bottom_boxes_height]) ApproachTracks();
    translate([0, 0, bottom_boxes_height + approach_track_box_height]) ButtonsBox();
    translate([0, buttons_box_length, bottom_boxes_height + approach_track_box_height]) ButtonsBox();
    translate([0, buttons_box_length * 2, bottom_boxes_height + approach_track_box_height]) ButtonsBox();
    translate([0, buttons_box_length * 3, bottom_boxes_height + approach_track_box_height]) ButtonsBoxDouble();
    translate([0, buttons_box_length * 5, bottom_boxes_height + approach_track_box_height]) ButtonsBoxDouble();
    translate([0, buttons_box_length * 7, bottom_boxes_height + approach_track_box_height]) ButtonsBoxDouble();
    translate([0, buttons_box_length * 9, bottom_boxes_height + approach_track_box_height]) ButtonsBoxTripple();
    translate([approach_track_box_width, 0, bottom_boxes_height]) DiceBox();
    translate([approach_track_box_width + dice_box_width, 0, bottom_boxes_height]) CardBox();
    translate([approach_track_box_width + dice_box_width, card_box_length, bottom_boxes_height]) SpacerBox();
  }
}

if (FROM_MAKE != 1) {
  BasePiecesOne();
}
