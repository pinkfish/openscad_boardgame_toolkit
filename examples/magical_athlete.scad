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

box_height = 45;
box_width = 184;
box_length = 294;
board_thickness = 7;

default_lid_thickness = 2;
default_floor_thickness = 2;
default_wall_thickness = 3;

default_lid_shape_type = SHAPE_TYPE_DROP;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

card_width = 67;
card_length = 90;

dice_size = 21;

cardboard_thickness = 2.2;

piece_thickness = 11;

piece_width = 24;
piece_length = 38;

tall_piece_length = 52;
tall_piece_width = 18;

big_baby_width = 39;
big_baby_length = 35.5;
big_baby_thickness = 32;

gold_height = [25, 23, 21];
gold_width = [32, 29, 26];

silver_diameter = [21.75, 18.5, 15.5];
silver_tag_width = [11, 10, 8.5];
silver_tag_diameter = [26, 23.5, 19.5];

card_box_width = card_length + default_wall_thickness * 2;
card_box_length = card_width + default_wall_thickness * 2;
card_box_height = box_height - board_thickness;


dice_box_width = box_width - card_box_width;
dice_box_length = card_box_length;
dice_box_height = dice_size + default_floor_thickness + default_lid_thickness + 1;

award_box_width = dice_box_width;
award_box_length = dice_box_length;
award_box_height = box_height - board_thickness - dice_box_height;

big_baby_box_width = big_baby_length + 20 + default_wall_thickness * 2;
big_baby_box_length = big_baby_width + default_wall_thickness * 2 + 1;
big_baby_box_height = box_height - board_thickness;

piece_box_width = box_width;
piece_box_length = box_length - card_box_length - big_baby_box_length;
piece_box_height = (box_height - board_thickness) / 2;

award_tokens_length = big_baby_box_length;
award_tokens_width = 50;
award_tokens_height = (box_height - board_thickness) / 2;

spacer_box_width = box_width - award_tokens_width - big_baby_box_width;
spacer_box_length = award_tokens_length;
spacer_box_height = box_height - board_thickness;

module SilverMedal(index) {
  circle(d=silver_diameter[index]);
  rotate(index == 2 ? 35 : 32)
    polygon(
      round_corners(
        [
          [silver_tag_width[index] / 2, 0],
          [silver_tag_width[index] / 2, silver_tag_diameter[index] / 2],
          [0, silver_tag_diameter[index] / 2 - 1],
          [-silver_tag_width[index] / 2, silver_tag_diameter[index] / 2],
          [-silver_tag_width[index] / 2, 0],
        ], radius=1
      )
    );

  rotate(index == 2 ? -35 : -32)
    polygon(
      round_corners(
        [
          [silver_tag_width[index] / 2, 0],
          [silver_tag_width[index] / 2, silver_tag_diameter[index] / 2],
          [0, silver_tag_diameter[index] / 2 - 1],
          [-silver_tag_width[index] / 2, silver_tag_diameter[index] / 2],
          [-silver_tag_width[index] / 2, 0],
        ], radius=1
      )
    );
}

module GoldMedal(index) {

  line = [
    [80.61, 14.17],
    [80.61, 14.07],
    [80.35, 12.02],
    [80.22, 11.36],
    [80.1, 10.87],
    [79.45, 8.74],
    [79.42, 8.64],
    [79.39, 8.58],
    [79.06, 7.76],
    [78.34, 6.27],
    [77.9, 5.47],
    [77.72, 5.22],
    [77.53, 4.89],
    [76.92, 4.0],
    [75.83, 2.65],
    [75.63, 2.45],
    [75.57, 2.38],
    [75.2, 1.99],
    [73.99, 0.96],
    [73.27, 0.3],
    [73.19, 0.24],
    [73.1, 0.2],
    [72.83, 0.06],
    [72.51, 0.04],
    [71.02, 0.0],
    [70.53, 0.0],
    [70.47, 0.0],
    [9.79, 0.0],
    [9.13, 0.01],
    [8.37, 0.02],
    [8.02, 0.02],
    [7.73, 0.22],
    [6.61, 1.05],
    [6.45, 1.19],
    [6.4, 1.24],
    [5.96, 1.64],
    [5.91, 1.68],
    [5.11, 2.5],
    [5.11, 2.51],
    [5.1, 2.51],
    [4.28, 3.48],
    [3.47, 4.55],
    [2.76, 5.62],
    [2.08, 6.79],
    [1.51, 7.93],
    [1.1, 8.88],
    [1.06, 8.99],
    [1.0, 9.12],
    [0.59, 10.31],
    [0.51, 10.59],
    [0.49, 10.66],
    [0.42, 10.9],
    [0.37, 11.16],
    [0.21, 11.87],
    [0.09, 12.63],
    [0.0, 15.34],
    [0.0, 15.35],
    [0.33, 18.04],
    [0.33, 18.05],
    [1.04, 20.66],
    [1.04, 20.66],
    [2.12, 23.12],
    [2.14, 23.15],
    [3.53, 25.34],
    [3.6, 25.44],
    [3.57, 25.38],
    [5.25, 27.26],
    [7.25, 28.81],
    [9.51, 29.91],
    [11.4, 30.39],
    [13.36, 30.66],
    [16.06, 31.1],
    [16.5, 31.29],
    [16.67, 31.41],
    [16.81, 31.55],
    [18.04, 32.79],
    [19.78, 34.24],
    [22.0, 35.71],
    [24.69, 36.99],
    [25.86, 37.45],
    [26.55, 37.82],
    [26.89, 38.1],
    [26.97, 38.2],
    [27.0, 38.27],
    [27.01, 38.29],
    [27.01, 38.31],
    [27.01, 38.35],
    [26.98, 38.46],
    [26.84, 38.73],
    [26.66, 38.95],
    [26.42, 39.14],
    [25.77, 39.51],
    [24.11, 40.16],
    [22.05, 40.98],
    [19.16, 42.42],
    [15.6, 44.83],
    [12.66, 47.64],
    [10.5, 50.62],
    [10.73, 50.2],
    [10.49, 50.64],
    [10.36, 50.8],
    [9.75, 51.93],
    [9.65, 52.14],
    [8.76, 54.29],
    [8.45, 55.31],
    [8.2, 56.53],
    [8.13, 57.07],
    [8.06, 57.91],
    [8.05, 58.5],
    [8.1, 59.39],
    [8.16, 59.91],
    [8.36, 60.84],
    [8.48, 61.23],
    [8.89, 62.21],
    [9.02, 62.44],
    [9.27, 62.83],
    [9.73, 63.4],
    [9.8, 63.48],
    [10.26, 63.89],
    [10.3, 63.92],
    [10.86, 64.3],
    [11.06, 64.42],
    [11.29, 64.46],
    [11.71, 64.51],
    [11.91, 64.53],
    [12.08, 64.55],
    [12.44, 64.58],
    [13.2, 64.63],
    [13.22, 64.63],
    [13.25, 64.64],
    [14.28, 64.69],
    [14.45, 64.7],
    [14.48, 64.7],
    [14.81, 64.71],
    [67.23, 64.82],
    [68.08, 64.79],
    [68.53, 64.74],
    [68.54, 64.73],
    [68.56, 64.73],
    [68.98, 64.65],
    [69.2, 64.59],
    [69.21, 64.58],
    [69.22, 64.58],
    [69.84, 64.32],
    [69.86, 64.32],
    [69.88, 64.29],
    [70.54, 63.83],
    [70.61, 63.77],
    [70.93, 63.46],
    [71.06, 63.32],
    [71.12, 63.27],
    [71.23, 63.14],
    [71.61, 62.62],
    [71.73, 62.42],
    [72.0, 61.92],
    [72.13, 61.63],
    [72.29, 61.21],
    [72.39, 60.79],
    [72.52, 60.37],
    [72.62, 59.88],
    [72.73, 58.75],
    [72.73, 58.55],
    [72.74, 58.47],
    [72.73, 58.0],
    [72.68, 57.18],
    [72.67, 57.12],
    [72.66, 57.04],
    [72.51, 56.09],
    [72.46, 55.86],
    [72.19, 54.87],
    [71.98, 54.29],
    [70.92, 51.98],
    [70.81, 51.77],
    [70.79, 51.72],
    [70.51, 51.24],
    [70.66, 51.54],
    [69.61, 49.79],
    [68.03, 47.75],
    [66.19, 45.85],
    [64.1, 44.12],
    [61.75, 42.56],
    [59.16, 41.2],
    [56.32, 40.05],
    [56.16, 39.99],
    [54.98, 39.54],
    [54.47, 39.27],
    [54.07, 38.96],
    [53.88, 38.7],
    [53.77, 38.5],
    [53.72, 38.36],
    [53.71, 38.32],
    [53.71, 38.3],
    [53.71, 38.29],
    [53.73, 38.25],
    [53.75, 38.2],
    [53.83, 38.09],
    [53.98, 37.96],
    [54.22, 37.8],
    [54.98, 37.41],
    [56.25, 36.92],
    [56.31, 36.9],
    [58.75, 35.72],
    [60.83, 34.36],
    [62.54, 32.94],
    [63.89, 31.61],
    [64.24, 31.36],
    [64.64, 31.17],
    [65.55, 30.9],
    [67.64, 30.62],
    [69.54, 30.4],
    [71.39, 29.89],
    [72.63, 29.4],
    [73.77, 28.75],
    [75.75, 27.11],
    [77.15, 25.48],
    [77.02, 25.67],
    [77.22, 25.4],
    [77.3, 25.31],
    [77.71, 24.73],
    [78.39, 23.69],
    [78.86, 22.85],
    [79.37, 21.78],
    [79.43, 21.64],
    [79.81, 20.63],
    [79.83, 20.55],
    [79.86, 20.49],
    [80.14, 19.5],
    [80.27, 18.96],
    [80.38, 18.21],
    [80.53, 17.41],
    [80.59, 16.8],
    [80.65, 15.5],
    [80.61, 14.17],
  ];
  translate([-gold_width[index] / 2, -gold_height[index] / 2])
    resize([gold_width[index], gold_height[index]])
      polygon(line);
}

module CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=card_box_height,
    lid_on_length=true,
    material_colour="fuchsia"
  ) {
    cube([card_length, card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=17, height=card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    lid_on_length=true,
    text_str="Athletes", label_colour="black"
  );
}

module DiceBox() // `make` me
{
  MakeBoxWithCapLid(
    width=dice_box_width,
    length=dice_box_length,
    height=dice_box_height,
    material_colour="red"
  ) {
    for (x = [0:2]) {
      for (y = [0:1]) {
        translate(
          [
            (x - 1.5) * (dice_size + 1) + $inner_width / 2,
            (y - 1) * (dice_size + 1) + $inner_length / 2,
            0,
          ]
        ) {
          cuboid([dice_size, dice_size, dice_box_height], anchor=BOTTOM + LEFT + FRONT, rounding=1);
        }
      }
    }
    translate([0, 0, dice_size / 2])
      RoundedBoxAllSides($inner_width, $inner_length, dice_box_height, 8);
  }
}

module DiceBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=dice_box_width, length=dice_box_length, height=dice_box_height,
    text_str="Dice", label_colour="black"
  );
}

module AwardBox() // `make` me
{
  MakeBoxWithSlipoverLid(
    width=award_box_width,
    length=award_box_length,
    height=award_box_height,
    foot=2,
    positive_negative_children=MAKE_MMU == 1 ? [1] : [],
    positive_colour="black",
    material_colour="gold"
  ) {
    union() {
      for (i = [0:2]) {
        translate(
          [
            (gold_height[0] + 1) * (i + 0.5),
            gold_width[0] / 2,
            $inner_height - cardboard_thickness * (i == 1 ? 2 : 1),
          ]
        ) {
          linear_extrude(height=cardboard_thickness * 3 + 1) {
            rotate(90)
              GoldMedal(index=i);
          }
          if (i == 1) {
            translate([(gold_width[i] / 2 - cardboard_thickness * 2), 0, 0])
              sphere(d=cardboard_thickness * 10, anchor=BOTTOM);
            translate([(gold_width[i] / 2 - cardboard_thickness * 2) * (-1), 0, 0])
              sphere(d=cardboard_thickness * 10, anchor=BOTTOM);
          }
        }
        translate(
          [
            (silver_diameter[0] + 5) * (i + 0.5),
            $inner_length - silver_diameter[i] / 2 - 1.5,
            $inner_height - cardboard_thickness * (i == 1 ? 2 : 1),
          ]
        ) {
          linear_extrude(height=cardboard_thickness * 4 + 1) {
            SilverMedal(index=i);
          }
          translate([0, -silver_diameter[i] / 2 + cardboard_thickness, 0])
            sphere(d=cardboard_thickness * 10, anchor=BOTTOM);
        }
      }
    }
    union() {
      translate([(gold_height[0] + 3) * (0 + 0) + 4, $inner_length / 2 + 4, $inner_height - default_slicing_layer_height]) {
        linear_extrude(h=default_slicing_layer_height + 0.01)
          rotate(270)
            text("1st", valign="center", halign="center", size=5);
      }
      translate([(gold_height[0] + 3) * (1) - 0.5, $inner_length / 2 + 18.5, $inner_height - default_slicing_layer_height]) {
        linear_extrude(h=default_slicing_layer_height + 0.01)
          rotate(270)
            text("2nd", valign="center", halign="center", size=5);
      }
      translate([(gold_height[0] + 3) * (1) - 0.5, $inner_length / 2 + 5, $inner_height - default_slicing_layer_height]) {
        linear_extrude(h=default_slicing_layer_height + 0.01)
          rotate(270)
            text("3rd", valign="center", halign="center", size=5);
      }
      translate([(gold_height[0] + 3) * (2) - 0.5, $inner_length / 2 + 15, $inner_height - default_slicing_layer_height]) {
        linear_extrude(h=default_slicing_layer_height + 0.01)
          rotate(270)
            text("4th", valign="center", halign="center", size=5);
      }
    }
  }
}

module AwardBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    width=award_box_width, length=award_box_length, height=award_box_height,
    text_str="Awards", label_colour="black", foot=2,
  );
}

module PieceBoxOne() // `make` me
{
  MakeBoxWithCapLid(
    width=piece_box_width,
    length=piece_box_length,
    height=piece_box_height,
    material_colour="teal"
  ) {
    for (x = [0:3]) {
      for (y = [0:4]) {
        translate(
          [
            (x) * (piece_length + 2) + 10,
            (y) * (piece_width + 2) + 7,
            0,
          ]
        ) {
          cuboid([piece_length, piece_width, piece_thickness], anchor=BOTTOM + LEFT + FRONT, rounding=1);
        }
      }
    }

    translate([62, $inner_length - tall_piece_width - 12, 0]) {
      cuboid([tall_piece_length, tall_piece_width, piece_thickness], anchor=BOTTOM + LEFT + FRONT, rounding=1);
    }

    translate([0, 0, piece_thickness / 2 + 1])
      RoundedBoxAllSides($inner_width, $inner_length, piece_box_height, 8);
  }
}

module PieceboxOneLid() // `make` me
{
  CapBoxLidWithLabel(
    width=piece_box_width, length=piece_box_length, height=piece_box_height,
    text_str="Athletes", label_colour="black",
    material_colour="aqua"
  );
}

module PieceBoxTwo() // `make` me
{
  MakeBoxWithCapLid(
    width=piece_box_width,
    length=piece_box_length,
    height=piece_box_height,
  ) {
    for (x = [0:3]) {
      for (y = [0:3]) {
        translate(
          [
            (x) * (piece_length + 2) + 10,
            (y) * (piece_width + 2) + 7,
            0,
          ]
        ) {
          if (y != 3 || x < 2)
            cuboid([piece_length, piece_width, piece_thickness], anchor=BOTTOM + LEFT + FRONT, rounding=1);
        }
      }
    }

    translate([0, 0, piece_thickness / 2 + 1])
      RoundedBoxAllSides($inner_width, $inner_length, piece_box_height, 8);
  }
}

module PieceboxTwoLid() // `make` me
{
  CapBoxLidWithLabel(
    width=piece_box_width, length=piece_box_length, height=piece_box_height,
    text_str="Athletes", label_colour="black"
  );
}

module BigBabyBox() // `make` me
{
  MakeBoxWithCapLid(
    width=big_baby_box_width,
    length=big_baby_box_length,
    height=big_baby_box_height,
    material_colour="pink"
  ) {
    translate([$inner_width / 2 - big_baby_thickness / 2, 0, $inner_height - big_baby_thickness])
      cuboid([big_baby_length, big_baby_width, big_baby_thickness], anchor=BOTTOM + LEFT + FRONT, rounding=1);

    translate([0, 0, big_baby_thickness / 2 + 1])
      RoundedBoxAllSides($inner_width, $inner_length, big_baby_box_height, 8);
  }
}

module BigBabyBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=big_baby_box_width, length=big_baby_box_length, height=big_baby_box_height,
    text_str="Big Baby", label_colour="black",
  );
}

module AwardsTokensBox() // `make` me
{
  MakeBoxWithCapLid(
    width=award_tokens_width,
    length=award_tokens_length,
    height=award_tokens_height,
    material_colour="brown"
  ) {
    RoundedBoxAllSides($inner_width, $inner_length, award_tokens_height, 5);
  }
}

module AwardsTokensBoxOneLid() // `make` me
{
  echo([award_tokens_height, award_tokens_length, award_tokens_width]);
  CapBoxLidWithLabel(
    width=award_tokens_width, length=award_tokens_length, height=award_tokens_height,
    text_str="1", label_colour="black"
  );
}

module AwardsTokensBoxThreeLid() // `make` me
{
  CapBoxLidWithLabel(
    width=award_tokens_width, length=award_tokens_length, height=award_tokens_height,
    text_str="3", label_colour="black"
  );
}

module SpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_box_width,
    length=spacer_box_length,
    height=spacer_box_height,
    hollow=true
  );
}

module BoxLayout(layout = 0) {
  if (layout == 3) {
    cube([box_width, box_length, 1]);
  }
  if (layout == 0) {
    cube([1, box_length, box_height]);
  }
  translate([0, 0, 0]) {
    if (layout < 3) {
      CardBox();
      translate([card_box_width, 0, dice_box_height])
        AwardBox();
    }
    translate([card_box_width, 0, 0]) DiceBox();
    translate([0, card_box_length, 0])
      PieceBoxOne();
    if (layout < 3) {
      translate([0, card_box_length, piece_box_height])
        PieceBoxTwo();
      translate([0, card_box_length + piece_box_length, 0])
        BigBabyBox();
    }
    translate([big_baby_box_width, card_box_length + piece_box_length, 0])
      AwardsTokensBox();
    if (layout < 3) {
      translate([big_baby_box_width, card_box_length + piece_box_length, award_tokens_height])
        AwardsTokensBox();
      translate([big_baby_box_width + award_tokens_width, card_box_length + piece_box_length, 0])
        SpacerBox();
    }
  }

  if (layout < 2)
    color("black")
      translate([0, 0, box_height - board_thickness])
        cube([box_width, box_length, board_thickness]);
}

module BoxLayoutA() // `document` me
{
  BoxLayout(1);
}

module BoxLayoutB() // `document` me
{
  BoxLayout(2);
}

module BoxLayoutC() // `document` me
{
  BoxLayout(3);
}

if (FROM_MAKE != 1) {
  AwardBox();
}
