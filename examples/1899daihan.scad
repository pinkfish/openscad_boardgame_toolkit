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

box_length = 305;
box_width = 225;
box_height = 63;

board_thickness = 13;

priority_deal_radius = 27;
priority_deal_bump_diameter = 25;
priority_deal_marker_thickness = 15;

disc_double_diameter = 15.5;
disc_thickness = 5;
disc_diameter = 14;
disc_double_thickness = 10;

executive_card_token_width = 28.5;
product_hub_width = 18.5;
product_source_width = 15.5;

tile_width = 40;
tile_radius = tile_width / 2 / cos(180 / 6);
tile_thickness = 2.5;

money_width = 44;
money_length = 68;
money_types = ["1", "5", "20", "100", "500"];

train_types = ["2", "3", "4", "5", "6", "D"];
train_counts = [7, 5, 4, 3, 1, 6];

small_card_width = 48;
small_card_length = 71;

card_width = 66;
card_length = 91;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

hex_box_width = tile_radius * 6 + default_wall_thickness * 3;
hex_box_height = tile_thickness * 4 + default_floor_thickness + default_lid_thickness + 2;
hex_box_length = tile_width * 3 + default_wall_thickness * 3;
hex_box_height_2 = tile_thickness * 4 + default_floor_thickness + default_lid_thickness + 2;

money_box_width = box_width - hex_box_width - 1;
money_box_length = hex_box_length * 2;
money_box_height = (box_height - board_thickness) / 3;

share_box_width = box_width - hex_box_width - 1;
share_box_length = hex_box_length * 2;
share_box_height = (box_height - board_thickness) / 3;

train_card_box_width = small_card_length + default_wall_thickness * 2;
train_card_box_length = small_card_width + default_wall_thickness * 2;
train_card_box_height = single_card_thickness * 48 + default_floor_thickness + default_lid_thickness;

company_marker_box_width = hex_box_width;
company_marker_box_length = disc_diameter * 2 + default_wall_thickness * 5;
company_marker_box_height = box_height - 1 - board_thickness - hex_box_height * 2;

private_company_card_box_width = card_length + default_wall_thickness * 2;
private_company_card_box_length = card_width + default_wall_thickness * 2;
private_company_card_box_height = company_marker_box_height;

extra_bits_box_width = private_company_card_box_width;
extra_bits_box_length = hex_box_length - private_company_card_box_length;
extra_bits_box_height = private_company_card_box_height;

module PriorityDealMarker(height) {
  // (8.1cos(−54°);8.1sin(−54°))

  radius = priority_deal_radius - priority_deal_bump_diameter / 2;
  linear_extrude(height=height)
    union() {
      for (i = [0:4]) {
        translate([radius * cos(i * 72), radius * sin(i * 72)])
          circle(d=priority_deal_bump_diameter);
      }
      circle(d=priority_deal_bump_diameter);
    }
}

module HexBox1() // `make` me
{
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=hex_box_height) {
    translate([default_wall_thickness / 2, default_wall_thickness / 2, 0])
      HexGridWithCutouts(
        rows=3, cols=3, height=hex_box_height, spacing=0,
        tile_width=tile_width, push_block_height=1
      );
  }
}

module HexBoxLid() // `make` me
{
  CapBoxLidWithLabel(width=hex_box_width, length=hex_box_length, height=hex_box_height, "1899 Daihan");
}

module HexBox2() // `make` me
{
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=hex_box_height_2) {
    translate([default_wall_thickness / 2, default_wall_thickness / 2, 0])
      HexGridWithCutouts(
        rows=3, cols=3, height=hex_box_height, spacing=0,
        tile_width=tile_width, push_block_height=1
      );
  }
}

module MoneyBox() // `make` me
{
  MakeBoxWithCapLid(width=money_box_width, length=money_box_length, height=money_box_height) {
    for (i = [0:4]) {
      translate([3, (money_width + 3) * i + 7, 0]) {
        cuboid([money_length, money_width, money_box_height], anchor=BOTTOM + LEFT + FRONT);
        translate([0, money_width / 2, -default_floor_thickness - 0.1])
          FingerHoleBase(
            radius=13, height=money_box_height - default_floor_thickness, spin=270,
            wall_thickness=default_wall_thickness + 3
          );
      }
    }
  }
}

module MoneyBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=money_box_width, length=money_box_length, height=money_box_height,
    text_str="Money"
  );
}

module ShareBox() // `make` me
{
  MakeBoxWithCapLid(width=share_box_width, length=share_box_length, height=share_box_height) {
    for (i = [0:3]) {
      translate([3, (small_card_width + 7) * i + 17, 0]) {
        cuboid([small_card_length, small_card_width, share_box_height], anchor=BOTTOM + LEFT + FRONT);
        translate([0, small_card_width / 2, -default_floor_thickness - 0.1])
          FingerHoleBase(
            radius=13, height=share_box_height - default_floor_thickness, spin=270,
            wall_thickness=default_wall_thickness + 3
          );
      }
    }
  }
}

module ShareBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=share_box_width, length=share_box_length, height=share_box_height,
    text_str="Shared"
  );
}

module TrainCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=train_card_box_width,
    length=train_card_box_length, height=train_card_box_height, lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, train_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=13, height=train_card_box_height - default_lid_thickness + 0.01, spin=270);
  }
}

module TrainCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=train_card_box_width,
    length=train_card_box_length, lid_on_length=true,
    text_str="Trains"
  );
}

module CompanyMarkerBox() // `make` me
{
  MakeBoxWithSlipoverLid(
    width=company_marker_box_width, length=company_marker_box_length,
    height=company_marker_box_height, foot=default_floor_thickness
  ) {
    for (i = [0:7]) {
      translate([disc_diameter / 2 + (disc_diameter + 3.5) * i, disc_diameter / 2, $inner_height - disc_thickness * 2 - 1]) {
        CylinderWithIndents(
          radius=disc_diameter / 2, height=company_marker_box_height,
          finger_hole_radius=7,
          finger_holes=[270]
        );
        translate([0, disc_diameter + default_wall_thickness, (i % 2) * disc_thickness])
          CylinderWithIndents(
            radius=disc_diameter / 2, height=company_marker_box_height,
            finger_hole_radius=7,
            finger_holes=[90]
          );
      }
    }
  }
}

module CompanyMarkerBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    width=company_marker_box_width, length=company_marker_box_length,
    height=company_marker_box_height, foot=default_floor_thickness,
    text_str="Company"
  );
}

module ExtraBitsBox() // `make` me
{
  MakeBoxWithSlipoverLid(
    width=company_marker_box_width, length=company_marker_box_length,
    height=company_marker_box_height, foot=default_floor_thickness
  ){}
}

module ExtraBitsBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    width=company_marker_box_width, length=company_marker_box_length,
    height=company_marker_box_height, foot=default_floor_thickness,
    text_str="Extra"
  );
}

module PrivateCompanyCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=private_company_card_box_width, length=private_company_card_box_length,
    height=private_company_card_box_height, lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, private_company_card_box_height]);
    translate([0, $inner_length / 2, -default_floor_thickness - 0.01])
      FingerHoleBase(radius=13, height=private_company_card_box_height - default_lid_thickness + 0.01, spin=270);
  }
}

module PrivateCompanyCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=private_company_card_box_width, length=private_company_card_box_length,
    lid_on_length=true,
    text_str="Private"
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    HexBox1();
    translate([0, 0, hex_box_height]) HexBox2();
    translate([0, hex_box_length, 0]) HexBox1();
    translate([0, hex_box_length, hex_box_height]) HexBox2();
    translate([0, 0, hex_box_height * 2])
      CompanyMarkerBox();
    translate([0, company_marker_box_length, hex_box_height * 2])
      CompanyMarkerBox();
    translate([0, company_marker_box_length * 2, hex_box_height * 2])
      PrivateCompanyCardBox();
    translate([private_company_card_box_width, company_marker_box_length * 2, hex_box_height * 2])
      ExtraBitsBox();
    translate([hex_box_width, 0, 0])
      ShareBox();
    translate([hex_box_width, 0, share_box_height])
      ShareBox();
    translate([hex_box_width, 0, share_box_height * 2])
      MoneyBox();
    translate([0, hex_box_length * 2, 0]) TrainCardBox();
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
