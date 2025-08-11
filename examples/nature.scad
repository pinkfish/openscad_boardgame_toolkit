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

box_width = 210;
box_length = 210;
box_height = 75;

default_label_solid_background = MAKE_MMU == 1;
default_label_type = LABEL_TYPE_FRAMELESS_ANGLE;

disk_diameter = 46;
disk_thickness = 4;
disk_middle_width = 10;
disk_middle_thickness = 1.5;

leopard_length = 100;
leopard_width = 40;

board_thickness = 7;

nature_card_number = 99;
hunter_card_number = 10;

card_length = 91.5;
card_width = 66.5;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

resource_box_width = (box_length - 2) / 2;
resource_box_length = card_width + default_wall_thickness * 2 + 1;
resource_box_height = (box_height - board_thickness) / 3;

hunter_card_box_width = card_length + default_wall_thickness * 2;
hunter_card_box_length = card_width + default_wall_thickness * 2;
hunter_card_box_height = resource_box_height;

dial_box_height = disk_diameter + default_wall_thickness + default_floor_thickness + 1;
dial_box_width = (box_width - hunter_card_box_width - 2) / 2;
dial_box_length = (box_length - resource_box_length - 2);

card_box_width = card_length + default_wall_thickness * 2;
card_box_length = card_width + default_wall_thickness * 2;
card_box_height = box_height - board_thickness - 1;

spacer_card_width = box_width - hunter_card_box_width - 1;
spacer_card_length = hunter_card_box_length;
spacer_card_height = hunter_card_box_height;

spacer_side_width = hunter_card_box_width;
spacer_side_length = box_length - hunter_card_box_length - resource_box_length - 2;
spacer_side_height = box_height - board_thickness - 2;

spacer_dial_box_width = dial_box_width * 2;
spacer_dial_box_length = dial_box_length;
spacer_dial_box_height = box_height - board_thickness - 2 - dial_box_height;

module ResourceBox() // `make` me
{
  MakeBoxWithCapLid(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height
  ) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
  }
}

module ResourceGrassBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    text_str="Grass"
  );
}

module ResourceMeatBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    text_str="Meat"
  );
}

module ResourcePopulationBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    text_str="Population"
  );
}

module DialBox() // `make` me
{
  MakeBoxWithCapLid(
    width=dial_box_width,
    length=dial_box_length,
    height=dial_box_height
  ) {
    translate([$inner_width / 2, dial_box_length / 2, $inner_height - disk_diameter / 2])
      cuboid(
        [disk_diameter / 2, dial_box_length + 10, disk_diameter], anchor=BOTTOM,
        rounding=disk_diameter / 4,
        edges=[LEFT + BOTTOM, RIGHT + BOTTOM]
      );
    translate([$inner_width / 2, dial_box_length / 2, $inner_height - disk_diameter / 4])
      cuboid(
        [disk_diameter / 2, dial_box_length + 10, disk_diameter / 4], anchor=BOTTOM,
        rounding=-disk_diameter / 4,
        edges=[LEFT + TOP, RIGHT + TOP]
      );
    for (i = [0:14]) {
      translate([$inner_width / 2, disk_thickness / 2 + 5 + (disk_thickness + 4.5) * i, $inner_height - disk_diameter])
        cuboid(
          [disk_diameter, disk_thickness + 0.5, disk_diameter], anchor=BOTTOM,
          rounding=disk_diameter / 4,
          edges=[LEFT + BOTTOM, RIGHT + BOTTOM]
        );
    }
  }
}

module DialBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=dial_box_width,
    length=dial_box_length,
    height=dial_box_height,
    text_str="Population",
    label_type=LABEL_TYPE_FRAMELESS
  );
}

module NatureCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    height=card_box_height,
    lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, card_box_height]);
  }
}

module NatureCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    text_str="Nature"
  );
}

module HunterCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=hunter_card_box_width,
    length=hunter_card_box_length,
    height=hunter_card_box_height,
    lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, card_box_height]);
  }
}

module HunterCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=hunter_card_box_width,
    length=hunter_card_box_length,
    text_str="Hunter"
  );
}

module SpacerCardBox() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_card_width,
    length=spacer_card_length,
    height=spacer_card_height,
    hollow=true
  );
}

module SpacerSideBox() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_side_width,
    length=spacer_side_length,
    height=spacer_side_height,
    hollow=true
  );
}

module SpacerDialBox() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_dial_box_width,
    length=spacer_dial_box_length,
    height=spacer_dial_box_height,
    hollow=true
  );
}

module BoxLayout() {
  cube([1, box_length, box_height]);
  cube([box_width, box_length, board_thickness]);
  translate([0, 0, board_thickness]) {
    ResourceBox();
    translate([0, 0, resource_box_height])
      ResourceBox();
    translate([0, 0, resource_box_height * 2])
      HunterCardBox();
    translate([hunter_card_box_width, 0, resource_box_height * 2]) {
      SpacerCardBox();
    }
    translate([0, resource_box_length, dial_box_height]) {
      SpacerDialBox();
    }
    translate([resource_box_width, 0, 0]) {
      ResourceBox();
      translate([0, 0, resource_box_height])
        ResourceBox();
    }
    translate([0, resource_box_length, 0]) {
      DialBox();
    }
    translate([dial_box_width, resource_box_length, 0]) {
      DialBox();
    }
    translate([dial_box_width * 2, resource_box_length, 0]) {
      NatureCardBox();
    }
    translate([dial_box_width * 2, resource_box_length + hunter_card_box_length, 0]) {
      SpacerSideBox();
    }
  }
}

if (FROM_MAKE != 1) {
  DialBoxLid();
}
