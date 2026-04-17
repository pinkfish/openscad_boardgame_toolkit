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

box_width = 214;
box_length = 302;
box_height = 39;

default_wall_thickness = 3;
default_lid_thickness = 3;

dividend_marker_diameter = 7.5;
dividend_marker_thickness = 3;

board_thickness = 10.5;

train_width = 7.75;
train_length = 5.5;
train_height = 8;

num_trains_per_company = 19;

companies = [
  object(shares=2, color="orange", name=["Belfast and", "County Down", "Railway"], lid="Belfast"),
  object(shares=3, color="yellow", name=["Cork Bandon", "& South Coast", "Railway"], lid="Cork"),
  object(shares=3, color="red", name=["Midland", "Great Western", "Railway"], lid="Midland"),
  object(shares=4, color="purple", name=["Waterford", "Limerick", "& Western", "Railway"], lid="Waterford"),
  object(shares=4, color="blue", name=["Great Southern", "& Western", "Railway"], lid="Great Southern"),
];

card_width = 49;
card_length = 71;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

num_money_cards = 25;
money_num = ["1", "5", "10"];

num_dividend_cubes = 30;

company_box_width = box_width / 4;
company_box_length = card_length * 1.8 + default_wall_thickness * 2;
company_box_height = (box_height - board_thickness) / 2;

money_box_width = box_width;
money_box_length = card_length + default_wall_thickness * 2;
money_box_height = box_height - board_thickness;

spacer_company_width = company_box_width;
spacer_company_length = company_box_length;
spacer_company_height = company_box_height;

spacer_back_width = box_width;
spacer_back_length = box_length - company_box_length - money_box_length - 1;
spacer_back_height = box_height - board_thickness;

module CompanyBox(num = 0) {
  MakeBoxWithSlidingLid(
    size=[company_box_width, company_box_length, company_box_height],
    positive_negative_children=[1], material_colour=companies[num].color,
  ) {
    union() {
      translate([0, 0, $inner_height - single_card_thickness * companies[num].shares - 1]) {
        cube([card_width, card_length, company_box_height]);
      }
      translate([card_width / 2, 0, -2])
        FingerHoleBase(radius=15, height=money_box_height);
      translate([card_width / 2, card_length + dividend_marker_diameter - 1.5, $inner_height - dividend_marker_thickness - 1])
        CylinderWithIndents(
          d=dividend_marker_diameter, h=company_box_height, anchor=BOTTOM, finger_holes=[0, 180],
          finger_hole_radius=4
        );
      translate([$inner_width - 8, $inner_length - train_width * 3, $inner_height - train_height - 0.5]) {
        cuboid([train_length * 6, train_width * 4, company_box_height], anchor=BOTTOM + RIGHT);
        translate([-train_length * 6 - 5, -train_length * 2 - 10, train_height / 2])
          RoundedBoxAllSides([train_length * 6 + 10, train_length * 4 + 20, company_box_height], radius=5);
      }
    }
    union() {
      max = len(companies[num].name) - 1;
      font_size = 7.75;
      for (i = [0:len(companies[num].name) - 1]) {
        translate([card_width / 2 + (i * (font_size + 1)) - max / 2 * (font_size + 1), card_length / 2 + 7, $inner_height - single_card_thickness * companies[num].shares - 1.2])
          rotate(90) text3d(companies[num].name[i], h=0.2, size=font_size, font="Brush Script MT", anchor=CENTER + BOTTOM);
      }
    }
  }
}

module CompanyBoxBelfastAndCountyDownsRailway() // `make` me
{
  CompanyBox(num=0);
}

module CompanyBoxCorkBandonAndSouthCostRailway() // `make` me
{
  CompanyBox(num=1);
}

module CompanyBoxMidlandGreatWesternRailway() // `make` me
{
  CompanyBox(num=2);
}

module CompanyBoxWaterfordLimerickAndWesternRailway() // `make` me
{
  CompanyBox(num=3);
}

module CompanyBoxGreatSouthernAndWesternRailway() // `make` me
{
  CompanyBox(num=4);
}

module CompanyBoxLid(num = 0) {
  SlidingBoxLidWithLabel(
    size=[company_box_width, company_box_length, company_box_height],
    text_str=companies[num].lid
  );
}

module CompanyBoxLidBelfast() // `make` me
{
  CompanyBoxLid(num=0);
}

module CompanyBoxLidCork() // `make` me
{
  CompanyBoxLid(num=1);
}

module CompanyBoxLidMidland() // `make` me
{
  CompanyBoxLid(num=2);
}

module CompanyBoxLidWaterford() // `make` me
{
  CompanyBoxLid(num=3);
}

module CompanyBoxLidGreatSouthern() // `make` me
{
  CompanyBoxLid(num=4);
}

module MoneyBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[money_box_width, money_box_length, money_box_height],
    text_str="Bank",
    lid_thickness=4
  );
}

module MoneyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[money_box_width, money_box_length, money_box_height],
    positive_negative_children=[1],
    lid_thickness=4
  ) {
    union() {
      for (i = [0:2]) {
        translate([(card_width + 2) * i, 0, 0]) {
          cuboid([card_width, card_length, money_box_height], anchor=BOTTOM + LEFT + FRONT);
          translate([card_width / 2, 0, -2])
            FingerHoleBase(radius=15, height=money_box_height);
        }
      }
    }
    union() {
      for (i = [0:2]) {
        translate([(card_width + 2) * i + card_width / 2, card_width / 2, 0]) {
          text3d(money_num[i], h=0.2, font="Impact", size=20, anchor=CENTER + BOTTOM);
        }
      }
      translate([$inner_width - 30, $inner_length / 2 + 7, $inner_height - 0.2])
        text3d("Irish", h=0.2, font="Impact", size=10, anchor=CENTER + BOTTOM);
      translate([$inner_width - 30, $inner_length / 2 - 7, $inner_height - 0.2])
        text3d("Gauge", h=0.2, font="Impact", size=10, anchor=CENTER + BOTTOM);
    }
  }
}

module SpacerBoxBack() // `make` me
{
  my_path = [
    [company_box_width - 2, 0],
    [company_box_width - 2, company_box_length + 2],
    [box_width, company_box_length + 2],
    [box_width, box_length - money_box_length - 2],
    [0, box_length - money_box_length - 2],
    [0, 0],
  ];
  MakePathBoxWithNoLid(
    path=my_path,
    height=box_height - board_thickness,
    hollow=true,
    $fn=16
  );
}

module SpacerBoxCompany() // `make` me
{
  MakeBoxWithNoLid(
    size=[spacer_company_width, spacer_company_length, spacer_company_height],
    hollow=true
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([1, box_length, box_height]);
  }
  if (layout < 2) {
    MoneyBox();
  }
  for (i = [0:2]) {
    translate([company_box_width * i + company_box_width, money_box_length, 0])
      CompanyBox(num=i);
    if (layout < 2 && i < 2) {
      translate([company_box_width * i + company_box_width, money_box_length, company_box_height])
        CompanyBox(num=i + 3);
    }
  }
  if (layout < 2) {
    translate([company_box_width * 3, money_box_length, company_box_height])
      SpacerBoxCompany();
  }
  translate([0, money_box_length, 0])
    SpacerBoxBack();
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
  BoxLayout();
}
