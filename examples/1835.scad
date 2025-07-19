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

box_length = 298;
box_width = 216;
box_height = 50;

default_wall_thickness = 2;
default_lid_thickness = 2;
default_floor_thickness = 2;

default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

inner_wall = 1;

share_width = 46;
share_length = 66;
share_thickness_twenty = 7;
money_width = 52;
money_length = 98;
money_one_thickness = 5;
money_total = 22;
company_card_bmb_length = 151;
company_card_bmb_width = 106;
company_card_bmb_thickness_six = 2.5;
company_card_length = 200;
company_card_lenght = 131;
token_diameter = 6;
token_thickness = 2;
large_marker_diameter = 20;
large_marker_length = 41;
tile_width = 40;
tile_radius = tile_width / 2 / cos(180 / 6);
train_tile_thickness_10 = 6;
board_thickness = 15;

num_train_cards = 33;
num_shares = 68;
num_private_railroad = 6;

main_height = box_height - board_thickness;

hex_box_width = tile_radius * 6 + default_wall_thickness * 2;
hex_box_height = main_height / 4;
hex_box_length = box_width - 1;

money_box_width = box_width - 1;
money_box_length = money_length + default_wall_thickness * 2;
money_box_height_1 = default_floor_thickness + default_lid_thickness + money_one_thickness + 0.5;
money_box_height_2 = money_box_height_1 - 1;

money_names = ["1", "5", "10", "20", "50", "100", "200", "500"];
share_names = [
  "Bayerische Eisenbahn",
  "Sächsische Eisenbahn",
  "Badische Eisenbahn",
  "Württembergische",
  "Hessische Eisenbahn",
  "Preußische Eisenbahn",
  "Mecklenburg-Schwerin",
  "Oldenburgische",
];

shares_box_width = box_length - hex_box_width - money_box_length - 1;
shares_box_length = share_length * 2 + 3 * 2;

first_player_box_length = box_width - shares_box_length - 1;
first_player_box_width = shares_box_width;
first_player_box_height = large_marker_diameter + 4;

shares_height = main_height / 4;

middle_height = main_height - money_box_height_1 - money_box_height_2;
middle_width = money_box_length;
middle_length = money_box_width;

insert_width = middle_width - default_wall_thickness * 2;
insert_length = middle_length - default_wall_thickness * 3 - large_marker_diameter;
insert_height = middle_height - default_lid_thickness - default_floor_thickness;

spacer_box_width = first_player_box_width;
spacer_box_length = first_player_box_length;
spacer_box_height = main_height - first_player_box_height;

module MoneyBox1() // `make` me
{
  module InnerPieces(show_everything) {
    for (i = [0:1:3])

      translate([(money_width + inner_wall) * i, 0, 0]) {
        if (show_everything) {
          cube([money_width, money_length, money_box_height_1]);
          translate([money_width / 2, 1.2, 0])
            FingerHoleBase(radius=10, height=$inner_height, spin=0);
        } else {
          translate([money_width / 2, money_length / 2, 0]) linear_extrude(height=0.2)
              text(money_names[i], font="Stencil Std:style=Bold", anchor=CENTER);
        }
      }
  }
  MakeBoxWithCapLid(
    width=money_box_width, length=money_box_length, height=money_box_height_1,
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(show_everything=true);
    color("black") InnerPieces(show_everything=false);
  }
}

module MoneyBox1Lid() // `make` me
{
  CapBoxLidWithLabel(width=money_box_width, length=money_box_length, height=money_box_height_1, text_str="Money", label_colour="black");
}

module MoneyBox2() // `make` me
{
  module InnerPieces(show_everything) {
    for (i = [0:1:3]) {
      translate([(money_width + inner_wall) * i, 0, 0]) {
        if (show_everything) {
          cube([money_width, money_length, money_box_height_2]);
          translate([money_width / 2, 1.2, 0])
            FingerHoleBase(radius=10, height=$inner_height, spin=0);
        } else {
          translate([money_width / 2, money_length / 2, 0]) linear_extrude(height=0.2)
              text(money_names[i + 4], font="Stencil Std:style=Bold", anchor=CENTER);
        }
      }
    }
  }
  MakeBoxWithCapLid(
    width=money_box_width, length=money_box_length, height=money_box_height_2,
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(show_everything=true);
    color("black") InnerPieces(show_everything=false);
  }
}

module MoneyBox2Lid() // `make` me
{
  CapBoxLidWithLabel(
    width=money_box_width, length=money_box_length, height=money_box_height_2,
    text_str="Money", label_colour="black"
  );
}

module HexBox() // `make` me
{
  MakeBoxWithInsetLidTabbed(width=hex_box_width, length=hex_box_length, height=hex_box_height) {
    translate([0, 5, 0]) {
      intersection() {
        translate([0, 0, -3]) cube([140, tile_width * 5, hex_box_height]);
        HexGridWithCutouts(
          rows=3, cols=5, height=hex_box_height, spacing=0, push_block_height=0,
          tile_width=tile_width
        );
      }
    }
  }
}

module HexBoxLid() // `make` me
{

  InsetLidTabbedWithLabel(
    width=hex_box_width, length=hex_box_length,
    text_str="Tiles", label_colour="black"
  );
}

module SharesBox(offset) {
  module InnerPieces(show_everything) {
    for (i = [0:1:1]) {
      translate([0, (share_length + 0.5) * i, 0]) {
        if (i + offset + 1 < len(share_names)) {
          if (show_everything) {
            color("yellow") cube([share_width, share_length, main_height]);
          }
          translate([share_width / 2, share_length / 2, -0.2]) linear_extrude(height=0.2) rotate(90)
                text(share_names[i + offset], font="Stencil Std:style=Bold", anchor=CENTER, size=4);
        } else {
          translate([share_width / 2, share_length / 2, $inner_height - 0.2]) linear_extrude(height=0.2)
              rotate(90) text("1835", font="Stencil Std:style=Bold", anchor=CENTER, size=20);
        }
      }
    }
    if (show_everything) {
      translate([-1, share_length / 2, -default_floor_thickness - 0.1]) color("yellow")
          FingerHoleBase(radius=10, height=$inner_height + default_floor_thickness, spin=270);
      if (offset != 6) {
        translate([-1, share_length / 2 + share_length, -default_floor_thickness - 0.1]) color("yellow")
            FingerHoleBase(radius=10, height=$inner_height + default_floor_thickness, spin=270);
      }
    }
  }
  MakeBoxWithSlipoverLid(
    width=shares_box_width, length=shares_box_length, height=shares_height,
    wall_thickness=1.5, foot=2, last_child_positive=default_label_solid_background
  ) {
    InnerPieces(show_everything=true);
    if (default_label_solid_background) {
      color("black") InnerPieces(show_everything=false);
    }
  }
}

module AllShareBoxes() // `make` me
{
  SharesBox(0);
  translate([0, shares_box_length + 10, 0]) SharesBox(2);
  translate([0, shares_box_length * 2 + 20, 0]) SharesBox(4);
  translate([0, shares_box_length * 3 + 30, 0]) SharesBox(6);
}
module AllShareBoxesLid() // `make` me
{

  SlipoverBoxLidWithLabel(
    width=shares_box_width, length=shares_box_length,
    text_str="Shares", wall_thickness=1.5, height=shares_height,
    label_colour="black"
  );
}

module MiddleBox() // `make` me
{
  token_depths = [1, 1, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 4, 4];
  labels = ["White", "Wheel", "1-3", "4-6", "L", "A", "E", "T", "S", "X", "Y", "Y", "R", "R"];

  module InnerPieces(show_everything) {
    translate([insert_width / 2, 11.5, $inner_height - 0.19]) linear_extrude(height=0.2)
        text("1835", font="Stencil Std:style=Bold", anchor=CENTER, size=20);
    translate([47, first_player_box_height + default_wall_thickness + 15, 0]) {
      if (show_everything) {
        cube([share_width + 0.5, share_length + 0.5, middle_height]);
        translate([share_width / 2, 0, 18]) cyl(r=20, h=middle_height * 2, rounding=12);
      }
      translate([share_width / 2, share_length / 2, -0.19]) linear_extrude(height=0.2) rotate(90)
            text("Trains", font="Stencil Std:style=Bold", anchor=CENTER, size=10);
    }
    private_company_cards = share_thickness_twenty * 10 / 20 + 1;
    translate(
      [
        47,
        first_player_box_height + default_wall_thickness + share_length + default_wall_thickness + 30,
        $inner_height - private_company_cards,
      ]
    ) {
      if (show_everything) {
        cube([share_width, share_length, private_company_cards]);
        translate([share_width / 2, share_length, 24]) cyl(r=15, h=50, rounding=9);
      }
      translate([share_width / 2, share_length / 2, -0.19]) linear_extrude(height=0.2) rotate(90)
            text("Private", font="Stencil Std:style=Bold", anchor=CENTER, size=10);
    }
    translate([0, 0, 0])for (i = [0:1:len(token_depths) - 1]) {
      token_num = token_depths[i];

      translate([0, (i < 4 ? i : i + 1) * (token_diameter + default_wall_thickness * 2 + 4) + 5, 0]) {
        if (show_everything) {
          for (j = [0:1:token_num - 1]) {
            translate(
              [
                token_diameter / 2 + j * (token_diameter + 5),
                token_diameter / 2 + 3,
                token_thickness / 2 + insert_height - token_thickness - 0.45,
              ]
            ) {
              cyl(d=token_diameter, h=token_thickness + 1, $fn=32);
              translate([token_diameter / 2, 0, 7]) sphere(r=7);
            }
          }
        }
        translate([2, -1, insert_height - 0.39]) linear_extrude(height=0.2)
            text(labels[i], font="Stencil Std:style=Bold", anchor=LEFT, size=4);
      }
    }
  }
  MakeBoxWithCapLid(
    width=middle_width, length=middle_length, height=middle_height,
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(show_everything=true);
    if (default_label_solid_background) {
      color("black") InnerPieces(show_everything=false);
    }
  }
}
module MiddleBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=middle_width, length=middle_length, height=middle_height, text_str="Tokens/Trains", label_colour="black"
  );
}

module SpacerBox() // `make` me
{
  difference() {
    color(default_material_colour) cube([spacer_box_width, spacer_box_length, spacer_box_height]);
    translate([default_wall_thickness, default_wall_thickness, default_wall_thickness])
      color(default_material_colour) cube(
          [
            spacer_box_width - default_wall_thickness * 2,
            spacer_box_length - default_wall_thickness * 2,
            spacer_box_height,
          ]
        );
  }
}

module LastSectionFirstPlayer() // `make` me
{
  MakeBoxWithSlipoverLid(
    width=first_player_box_width, length=first_player_box_length,
    height=first_player_box_height, wall_thickness=3, foot=2
  ) {
    translate([-1, 30, 14]) {
      xcyl(d=large_marker_diameter, h=large_marker_length, anchor=BOTTOM + LEFT + FRONT, $fn=64);
      translate([0, -3, large_marker_diameter / 2 - 2])
        cuboid(
          [large_marker_length, large_marker_diameter, large_marker_diameter / 2],
          anchor=BOTTOM + LEFT + FRONT
        );
    }
    translate([first_player_box_width / 2 - 4.5, 21, 20]) {
      translate([0, -3, 5]) cyl(r=10, h=large_marker_diameter, anchor=BOTTOM + FRONT);
      sphere(r=10, anchor=BOTTOM + FRONT, $fn=64);
    }
    translate([first_player_box_width / 2 - 4.5, 39, 20]) {
      translate([0, -3, 5]) cyl(r=10, h=large_marker_diameter, anchor=BOTTOM + FRONT);
      sphere(r=10, anchor=BOTTOM + FRONT, $fn=64);
    }
  }
}

module LastSectionFirstPlayerLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    width=first_player_box_width, length=first_player_box_length,
    height=first_player_box_height, wall_thickness=3, foot=2, label_colour="black",
    text_str="First", label_radius=2, 
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, 0, board_thickness]) {
    MoneyBox1();
    translate([0, 0, money_box_height_1]) MoneyBox2();
    translate([0, middle_width, money_box_height_1 + money_box_height_2]) rotate([0, 0, -90]) MiddleBox();
    translate([0, money_box_length + hex_box_width, 0]) rotate([0, 0, -90]) HexBox();
    translate([0, money_box_length + hex_box_width, hex_box_height]) rotate([0, 0, -90]) HexBox();
    translate([0, money_box_length + hex_box_width, hex_box_height * 2]) rotate([0, 0, -90]) HexBox();
    translate([0, money_box_length + hex_box_width, hex_box_height * 3]) rotate([0, 0, -90]) HexBox();
    translate([0, money_box_length + hex_box_width + shares_box_width, 0]) rotate([0, 0, -90]) SharesBox(0);
    translate([0, money_box_length + hex_box_width + shares_box_width, shares_height]) rotate([0, 0, -90])
        SharesBox(2);
    translate([0, money_box_length + hex_box_width + shares_box_width, shares_height * 2]) rotate([0, 0, -90])
        SharesBox(4);
    translate([0, money_box_length + hex_box_width + shares_box_width, shares_height * 3]) rotate([0, 0, -90])
        SharesBox(6);
    translate([shares_box_length, money_box_length + hex_box_width + first_player_box_width, 0])
      rotate([0, 0, -90]) LastSectionFirstPlayer();
    translate(
      [shares_box_length, money_box_length + hex_box_width + first_player_box_width, first_player_box_height]
    )
      rotate([0, 0, -90]) SpacerBox();
  }
}

if (FROM_MAKE != 1) {
  LastSectionFirstPlayerLid();
}
