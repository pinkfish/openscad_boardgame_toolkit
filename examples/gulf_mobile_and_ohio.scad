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

box_width = 217;
box_length = 307;
box_height = 39;

default_wall_thickness = 3;

board_thickness = 9.5;

cube_size = 8.25;

marker_diameter = 16.5;
marker_thickness = 14.5;

common_share_diameter = 20.5;
common_share_thickness = 31;

money_width = 53;
money_length = 101;

card_width = 66;
card_length = 91;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

num_player_aid_cards = 4;
num_railroads = 23;
num_card_per_railroad = 2;

red_cubes_num = 20;
yellow_cubes_num = 26;
green_cubes_num = 32;
blue_cubes_num = 16;
black_cubes_num = 12;
purple_cubes_num = 6;

money_box_width = (money_width + 2) * 3 + default_wall_thickness * 2;
money_box_length = (money_length) + default_wall_thickness * 2;
money_box_height = box_height - board_thickness;

company_box_width = card_width + default_wall_thickness * 2;
company_box_length = card_length + default_wall_thickness * 2;
company_box_height = box_height - board_thickness;

cube_box_length = box_length - company_box_length - money_box_length;
cube_box_width = box_width / 4;
cube_box_height = (box_height - board_thickness) / 2;

player_token_box_length = cube_box_length;
player_token_box_width = cube_box_width;
player_token_box_height = common_share_diameter + default_floor_thickness + default_lid_thickness;

front_spacer_box_length = player_token_box_length;
front_spacer_box_width = player_token_box_width;
front_spacer_box_height = box_height - board_thickness - player_token_box_height;

cube_info = [
  object(color="red", num_x=red_cubes_num / 5, num_y=5, remainder=red_cubes_num % 5),
  object(color="yellow", num_x=floor(yellow_cubes_num / 8), num_y=8, remainder=yellow_cubes_num % 8),
  object(color="green", num_x=green_cubes_num / 8, num_y=8, remainder=green_cubes_num % 8),
  object(color="blue", num_x=blue_cubes_num / 8, num_y=8, remainder=blue_cubes_num % 8),
  object(color="black", num_x=black_cubes_num / 6, num_y=6, remainder=black_cubes_num % 6),
  object(color="purple", num_x=purple_cubes_num / 6, num_y=6, remainder=purple_cubes_num % 6),
];

module MoneyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[money_box_width, money_box_length, money_box_height],
    positive_negative_children=[1]
  ) {
    union() {
      for (i = [0:2]) {
        translate([(money_width + 2) * i, 0, 0]) {
          cuboid([money_width, money_length, money_box_height], anchor=BOTTOM + FRONT + LEFT);
          translate([money_width / 2, 0, -2]) FingerHoleBase(radius=15, height=money_box_height);
        }
      }
    }

    union() {
      for (i = [0:2]) {
        translate([(money_width + 2) * i, 0, 0]) {
          translate([money_width / 2, money_length / 2, -0.2]) {
            color("black")
              linear_extrude(height=0.2)
                text(["1", "5", "20"][i], size=20, font="Impact", halign="center", valign="center");
          }
        }
      }
    }
  }
}

module MoneyBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[money_box_width, money_box_length, money_box_height], text_str="Bank",
    lid_on_length=true
  );
}

module CompanyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[company_box_width, company_box_length, company_box_height]
  ) {
    cube([card_width, card_length, company_box_height]);
    translate([card_width / 2, 0, -2]) FingerHoleBase(radius=15, height=money_box_height);
  }
}

module CompanyBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[company_box_width, company_box_length, company_box_height], text_str="Companies"
  );
}

module CubeBox(num = 0) {
  MakeBoxWithCapLid(
    size=[cube_box_width, cube_box_length, cube_box_height],
    material_colour=cube_info[num].color
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - cube_size - 0.5]) {
      cuboid([cube_size * cube_info[num].num_x, cube_size * cube_info[num].num_y, cube_box_height], anchor=BOTTOM);
      if (cube_info[num].remainder > 0) {
        translate([(cube_size * cube_info[num].num_x) / 2 + cube_size / 2, 0, 0])
          cuboid([cube_size, cube_size * cube_info[num].remainder, cube_box_height], anchor=BOTTOM);
      }
    }
    translate([2, 2, $inner_height - cube_size / 2])
      RoundedBoxAllSides([$inner_width - 4, $inner_length - 4, cube_box_height], radius=5);
  }
}

module CubeBoxRed() // `make` me
{
  CubeBox(num=0);
}

module CubeBoxYellow() // `make` me
{
  CubeBox(num=1);
}

module CubeBoxGreen() // `make` me
{
  CubeBox(num=2);
}

module CubeBoxBlue() // `make` me
{
  CubeBox(num=3);
}

module CubeBoxBlack() // `make` me
{
  CubeBox(num=4);
}

module CubeBoxPurple() // `make` me
{
  CubeBox(num=5);
}

module CubeBoxLid(num = 0) {
  CapBoxLidWithLabel(
    size=[cube_box_width, cube_box_length, cube_box_height],
    text_str=str_join([upcase(cube_info[num].color[0]), substr(cube_info[num].color, 1)])
  );
}

module CubeBoxLidRed() // `make` me
{
  CubeBoxLid(num=0);
}

module CubeBoxLidYellow() // `make` me
{
  CubeBoxLid(num=1);
}

module CubeBoxLidGreen() // `make` me
{
  CubeBoxLid(num=2);
}

module CubeBoxLidBlue() // `make` me
{
  CubeBoxLid(num=3);
}

module CubeBoxLidBlack() // `make` me
{
  CubeBoxLid(num=4);
}

module CubeBoxLidPurple() // `make` me
{
  CubeBoxLid(num=5);
}

module PlayerTokenBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[player_token_box_width, player_token_box_length, player_token_box_height]
  ) {
    translate([5, 6, $inner_height - marker_thickness]) {
      for (i = [0:4]) {
        translate([marker_diameter / 2, marker_diameter / 2 + (marker_diameter + 1) * i, 0])
          cyl(d=marker_diameter, h=player_token_box_height, anchor=BOTTOM);
      }
    }
    translate([$inner_width - common_share_diameter * 3 / 4, $inner_length / 2, $inner_height - common_share_diameter - 0.5])
      cuboid(
        [common_share_diameter, common_share_thickness, common_share_diameter + 10], anchor=BOTTOM,
        rounding=common_share_diameter / 2,
        edges=BOTTOM
      );
    translate([1, 1, $inner_height - marker_thickness / 2])
      RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, player_token_box_height], radius=5);
  }
}

module PlayerTokenBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[player_token_box_width, player_token_box_length, player_token_box_height], text_str="Tokens"
  );
}

module FrontSpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    size=[front_spacer_box_width, front_spacer_box_length, front_spacer_box_height],
    hollow=true
  );
}

module SideSpacerBox() // `make` me
{
  width_offset = money_box_width - company_box_width * 2;
  box_path = [
    [width_offset, 0],
    [width_offset, money_box_length + 2],

    [0, money_box_length + 2],
    [0, money_box_length + company_box_length - 2],
    [box_width - company_box_width * 2 - 2, money_box_length + company_box_length - 2],
    [box_width - company_box_width * 2 - 2, 0],
  ];

  MakePathBoxWithNoLid(
    path=box_path, height=box_height - board_thickness,
    hollow=true,
    $fn=16
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([1, box_length, box_height]);
  }

  MoneyBox();
  translate([0, money_box_length, 0]) CompanyBox();
  translate([company_box_width, money_box_length, 0]) CompanyBox();
  if (layout < 2)
    translate([company_box_width * 2, 0, 0]) SideSpacerBox();
  translate([0, money_box_length + company_box_length, 0])for (i = [0:2]) {
    translate([cube_box_width * i, 0, 0])
      CubeBox(num=i);
    if (layout < 2)
      translate([cube_box_width * i, 0, cube_box_height])
        CubeBox(num=i + 3);
  }
  translate([cube_box_width * 3, money_box_length + company_box_length, 0])
    PlayerTokenBox();
  if (layout < 2)
    translate([cube_box_width * 3, money_box_length + company_box_length, player_token_box_height])
      FrontSpacerBox();
}

module BoxLayoutA() // `document` me
{
  BoxLayout(layout=1);
}

module BoxLayoutB() // `document` me
{
  BoxLayout(layout=2);
}

if (FROM_MAKE != 1) {
  BoxLayoutB();
}
