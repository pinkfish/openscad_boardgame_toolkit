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

include <BOSL2/beziers.scad>
include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

include <lib/root_shared.scad>

default_lid_thickness = 3;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 10;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

only_board_height = 16;

marquis_box_width = (box_data.marquis.length + 1) * 5 + default_wall_thickness;
marquis_box_length = (box_data.marquis.width + 2) * 5 + default_wall_thickness * 2 + (square_tile_size + default_wall_thickness) * 2;
marquis_box_height = box_data.token.thickness + default_floor_thickness + default_lid_thickness + 0.5;

erie_box_length = (box_data.erie.width) * 4 + default_wall_thickness * 2;
alliance_box_length = (box_data.alliance.width + 1) * 2 + default_wall_thickness * 2;
riverfolk_box_length = (box_data.riverfolk.width + 1) * 3 + default_wall_thickness * 2;
lizard_box_length = (box_data.lizard.width + 1) * 5 + default_wall_thickness * 2;

echo([box_data.marquis, box_data.token.thickness * 0.6667]);

module MarquisCharacterBox() {
  MakeBoxWithCapLid(width=marquis_box_width, length=marquis_box_length, height=marquis_box_height, material_colour="orange") {
    for (j = [0:1:4]) {
      translate([(box_data.marquis.length + 0.75) * j, 0, 0]) {
        for (i = [0:1:4]) {
          height = box_data.token.thickness + 0.5;
          translate(
            [
              box_data.marquis.length / 2,
              box_data.marquis.width / 2 + (box_data.marquis.width + 2) * i,
              $inner_height - height / 2,
            ]
          ) rotate([0, 0, 270]) MarquisCharacter(height=height);
        }
      }
    }
    for (j = [0:1:3]) {
      translate([(square_tile_size + 1) * (j + 0.5), $inner_length, $inner_height - tile_thickness * 3 - 0.5]) {
        cuboid([square_tile_size, square_tile_size, tile_thickness * 8], anchor=BOTTOM + BACK);
      }
      translate([(square_tile_size + 1) * (j + 0.5), $inner_length - square_tile_size - default_wall_thickness, $inner_height - tile_thickness * 3 - 0.5]) {
        cuboid([square_tile_size, square_tile_size, tile_thickness * 8], anchor=BOTTOM + BACK);
      }
    }
    // Wood
    translate([(square_tile_size + 1) * (4 + 0.5), $inner_length - square_tile_size - default_wall_thickness, $inner_height - tile_thickness * 2 - 0.5]) {
      cuboid([square_tile_size, square_tile_size, tile_thickness * 8], anchor=BOTTOM + BACK);
    }
    // Keep
    translate([(square_tile_size + 1) * (4 + 0.75), $inner_length, $inner_height - tile_thickness * 1 - 0.5]) {
      cuboid([square_tile_size, square_tile_size, tile_thickness * 8], anchor=BOTTOM + BACK);
    }
  }
}

module LizardCharacterBox() {
  MakeBoxWithCapLid(width=marquis_box_width, length=marquis_box_length, height=marquis_box_height, material_colour="yellow") {
    for (j = [0:1:4]) {
      translate([(box_data.lizard.length + 0.75) * j, box_data.lizard.width / 2, 0]) {
        for (i = [0:1:4]) {
          height = box_data.token.thickness + 0.5;
          translate(
            [
              0,
              (box_data.lizard.width + 2) * i,
              $inner_height - height,
            ]
          ) rotate([0, 0, 270]) translate([0.0, height / 2 + 5]) LizardCharacter(height=height + 10);
        }
      }
    }
  }
}

module ErieCharacterBox() {
  MakeBoxWithSlidingLid(width=marquis_box_width, length=erie_box_length, height=marquis_box_height) {
    for (i = [0:1:3]) {
      height = box_data.token.thickness * 5 + 10;
      translate(
        [
          box_data.erie.length / 2 - default_wall_thickness,
          box_data.erie.width / 2 + (box_data.erie.width) * i,
          $inner_height - height - 0.5 + height / 2 + 10,
        ]
      ) rotate([0, 0, 270]) ErieCharacter(height=height + 1);
    }
  }
}

module AllianceCharacterBox() {
  MakeBoxWithSlidingLid(width=marquis_box_width, length=alliance_box_length, height=marquis_box_height) {
    for (i = [0:1:1]) {
      height = box_data.token.thickness * 5 + 10;
      translate(
        [
          box_data.alliance.length / 2 - default_wall_thickness,
          box_data.alliance.width / 2 + (box_data.alliance.width + 1) * i,
          $inner_height - height - 0.5 + height / 2 + 10,
        ]
      ) rotate([0, 0, 270]) AllianceCharacter(height=height + 1);
    }
  }
}

module RiverfolkCharacterBox() {
  MakeBoxWithSlidingLid(width=marquis_box_width, length=riverfolk_box_length, height=marquis_box_height) {
    for (i = [0:1:2]) {
      height = box_data.token.thickness * 5 + 10;
      translate(
        [
          box_data.riverfolk.length / 2 - default_wall_thickness,
          box_data.riverfolk.width / 2 + (box_data.riverfolk.width + 1) * i,
          $inner_height - height - 0.5 + height / 2 + 10,
        ]
      ) rotate([0, 0, 270]) RiverfolkCharacter(height=height + 1);
    }
  }
}

module BoxLayout() {
  //cube([box_data.box.width, box_data.box.length, only_board_height]);
  translate([0, 0, only_board_height]) {
    MarquisCharacterBox();
    /*
    translate([0, marquis_box_length, 0]) ErieCharacterBox();
    translate([0, marquis_box_length + erie_box_length, 0]) AllianceCharacterBox();
    translate([0, marquis_box_length + erie_box_length + alliance_box_length, 0]) RiverfolkCharacterBox();
    translate([marquis_box_width, 0, 0]) LizardCharacterBox();
    */
  }
}

BoxLayout();
