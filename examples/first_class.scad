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

box_length = 307;
box_width = 217;
box_height = 70;

default_wall_thickness = 3;

rule_book_thickness = 3;

board_thickness = 2.5;

player_board_thickness = 9.5;
player_board_length = 205;
player_board_width = 160;
player_board_thin_length = 139;
player_board_thin_width = 87;
player_board_bump_width = 8;
player_board_bump_length = 48;
player_board_bump_edge_offset = 67;

locomotive_tile_width = 68.5;
locomotive_tile_length = 64.5;

evidence_token_length = 22;
evidence_token_width = 18.5;

coin_diameter = 18.5;

player_cube = 8.5;

card_width = 47;
card_length = 70;
card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;

num_railroad_cards = 94;
num_mail_cards = 16;
num_base_cards = 72;
num_game_end_cards = 21;
num_module_cards = 24;
num_modules = 5;
num_whodunit_cards = 4;
num_evidence_cards = 26;
num_railroad_0_1_card = 50;
num_railroad_2_4_card = 24;
num_railroad_7_12_card = 20;

start_player_tile_width = 44.5;
start_player_tile_length = 68;

score_board_width = 182;
score_board_length = 252;

meeple_width = 15.5;
meeple_length = 21;
meeple_thickness = 10.5;

train_length = 15.5;
train_width = 11.5;
train_thickness = 8;

player_box_width = box_width / 2;
player_box_length = card_width + default_wall_thickness * 2;
player_box_height = (box_height - rule_book_thickness - board_thickness) / 3;

card_box_width = box_width / 4;
card_box_length = card_length + default_wall_thickness * 2;

module_box_height = (box_height - rule_book_thickness - board_thickness) / 3;
railroad_0_1_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_railroad_0_1_card + 1;
railroad_2_4_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_module_cards + 1;
railroad_7_12_height = module_box_height;
whodunit_card_box_height = box_height - rule_book_thickness - railroad_0_1_height - railroad_2_4_height - board_thickness;
start_tile_box_height = default_floor_thickness + default_lid_thickness + board_thickness + 1;

locomotive_box_length = card_box_length;
locomotive_box_width = default_floor_thickness + default_lid_thickness + locomotive_tile_length + default_wall_thickness * 2;
locomotive_box_height = default_floor_thickness + default_lid_thickness + board_thickness * 9 + 1;
game_end_card_box_height = locomotive_box_height - start_tile_box_height;

spacer_card_box_length = card_box_length;
spacer_card_box_width = card_box_width + locomotive_box_width;
spacer_card_box_height = box_height - rule_book_thickness - player_board_thickness - locomotive_box_height - board_thickness;

rest_spacer_box_height = box_height - rule_book_thickness - player_board_thickness - board_thickness;

player_colors = ["yellow", "blue", "red", "green"];

module TrainToken() {
  bez = [
    [202.08, 72.67],
    [225.63000000000002, 74.54],
    [248.84, 98.69],
    [248.84, 98.69],
    [248.84, 98.69],
    [257.43, 105.39999999999999],
    [260.22, 103.97],
    [265.13000000000005, 101.45],
    [262.02000000000004, 85.37],
    [262.75, 76.24],
    [264.85, 50.169999999999995],
    [274.08, 23.33],
    [274.08, 23.33],
    [274.08, 23.33],
    [281.75, 11.29],
    [285.09, 11.059999999999999],
    [327.71999999999997, 8.18],
    [363.62, 4.679999999999999],
    [417.16999999999996, 2.789999999999999],
    [428.71, 2.379999999999999],
    [437.22999999999996, 1.4099999999999993],
    [444.34, 8.379999999999999],
    [452.09999999999997, 15.979999999999999],
    [450.33, 42.56999999999999],
    [448.34, 59.16],
    [447.36999999999995, 67.24],
    [445.90999999999997, 70.22999999999999],
    [444.34, 73.33],
    [442.16999999999996, 77.61],
    [433.11999999999995, 86.84],
    [433.11999999999995, 86.84],
    [393.87999999999994, 128.03],
    [395.48999999999995, 172.23000000000002],
    [440.86999999999995, 210.27],
    [440.86999999999995, 210.27],
    [444.86999999999995, 214.09],
    [446.59999999999997, 218.70000000000002],
    [447.59, 221.36],
    [446.59999999999997, 226.76000000000002],
    [446.26, 231.66000000000003],
    [445.46, 243.74000000000004],
    [443.01, 257.91],
    [443.01, 257.91],
    [387.19, 262.98],
    [387.19, 262.98],
    [387.48, 306.22],
    [347.68, 309.08000000000004],
    [295.7, 312.82000000000005],
    [293.09000000000003, 254.39000000000004],
    [293.09000000000003, 254.39000000000004],
    [189.09000000000003, 267.48],
    [189.09000000000003, 267.48],
    [184.90000000000003, 310.31],
    [136.62000000000003, 310.13],
    [96.09000000000003, 309.98],
    [86.02000000000004, 258.06],
    [86.02000000000004, 258.06],
    [46.250000000000036, 254.43],
    [46.250000000000036, 254.43],
    [30.640000000000036, 255.51000000000002],
    [26.640000000000036, 252.64000000000001],
    [24.080000000000037, 250.81],
    [23.070000000000036, 247.11],
    [20.150000000000034, 240.19000000000003],
    [13.420000000000034, 224.19000000000003],
    [3.6300000000000345, 196.89000000000004],
    [2.5500000000000327, 185.49],
    [1.9000000000000328, 178.61],
    [7.530000000000033, 142.84],
    [10.950000000000033, 136.83],
    [18.760000000000034, 123.11000000000001],
    [52.41000000000003, 118.87],
    [52.41000000000003, 118.87],
    [57.180000000000035, 109.88000000000001],
    [62.720000000000034, 49.20000000000001],
    [62.720000000000034, 49.20000000000001],
    [67.75000000000003, 23.61000000000001],
    [77.22000000000003, 17.20000000000001],
    [86.69000000000003, 10.79000000000001],
    [95.02000000000002, 7.810000000000009],
    [109.82000000000002, 9.730000000000011],
    [134.44000000000003, 12.26000000000001],
    [138.42000000000002, 104.69000000000001],
    [138.42000000000002, 104.69000000000001],
    [163.65, 69.61000000000001],
    [202.07000000000002, 72.66000000000001],
  ];
  min_x = min([for (i = bez) i[0]]);
  max_x = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[1]]);
  max_y = max([for (i = bez) i[1]]);
  offset(0.5)
    resize([train_length - 0.5, train_width - 0.5])
      translate([-max_x + (max_x - min_x) / 2, -max_y + ( (max_y - min_y) / 2)])
        polygon(bez);
}

module MeepleToken() {
  bez = [
    [298.28, 595.68],
    [231.36999999999998, 518.8599999999999],
    [221.48, 518.8699999999999],
    [217.80999999999997, 524.5799999999999],
    [176.83999999999997, 591.0999999999999],
    [175.00999999999996, 593.9499999999999],
    [165.86999999999998, 602.9599999999999],
    [161.95, 602.9599999999999],
    [29.96, 602.9599999999999],
    [10.080000000000002, 602.9599999999999],
    [10.04, 595.6099999999999],
    [5.580000000000002, 588.5099999999999],
    [-0.049999999999998046, 579.5399999999998],
    [3.040000000000002, 564.8999999999999],
    [6.850000000000001, 556.7499999999999],
    [28.07, 511.40999999999985],
    [64.87, 442.4699999999999],
    [79.06, 416.1199999999999],
    [81.98, 410.6999999999999],
    [79.45, 403.9899999999999],
    [73.71000000000001, 401.7799999999999],
    [53.45, 393.9799999999999],
    [12.400000000000006, 371.6199999999999],
    [9.230000000000004, 317.8399999999999],
    [5.840000000000003, 260.3499999999999],
    [74.61, 232.50999999999993],
    [107.99000000000001, 218.17999999999992],
    [111.94000000000001, 216.47999999999993],
    [114.39000000000001, 212.49999999999991],
    [114.13000000000001, 208.20999999999992],
    [112.35000000000001, 179.04999999999993],
    [112.33000000000001, 178.63999999999993],
    [112.28000000000002, 178.23999999999992],
    [112.2, 177.82999999999993],
    [106.06, 144.29999999999993],
    [105.09, 138.98999999999992],
    [100.14, 135.33999999999992],
    [94.78, 136.02999999999992],
    [76.36, 138.4099999999999],
    [36.97, 138.3499999999999],
    [31.53, 95.81999999999991],
    [27.150000000000002, 61.549999999999905],
    [71.47, 51.08999999999991],
    [90.33, 48.19999999999991],
    [94.96, 47.48999999999991],
    [98.47, 43.70999999999991],
    [98.92, 39.04999999999991],
    [99.5, 33.01999999999991],
    [101.01, 25.049999999999912],
    [104.89, 20.209999999999912],
    [122.89, -2.22],
    [162.96, 3.36],
    [209.21, 3.15],
    [249.22, 2.9699999999999998],
    [290.16, -2.28],
    [309.12, 20.33],
    [318.8, 31.869999999999997],
    [316.95, 52.51],
    [318.16, 77.97],
    [320.35, 123.69],
    [319.45000000000005, 172.35],
    [318.98, 190.68],
    [318.87, 195.13],
    [321.65000000000003, 199.12],
    [325.85, 200.56],
    [353.25, 209.94],
    [450.82000000000005, 247.69],
    [453.99, 310.63],
    [456.42, 358.97],
    [404.54, 382.87],
    [381.76, 391.0],
    [376.19, 392.99],
    [373.48, 399.26],
    [375.84999999999997, 404.68],
    [438.88, 547.72],
    [442.38, 555.6],
    [443.54, 558.21],
    [446.58, 573.53],
    [445.39, 581.2900000000001],
    [444.2, 589.0500000000002],
    [445.83, 602.9800000000001],
    [412.45, 602.9800000000001],
    [386.57, 602.9800000000001],
    [330.91999999999996, 602.4300000000002],
    [310.83, 602.9800000000001],
    [307.78999999999996, 603.0600000000002],
    [300.27, 597.9900000000001],
  ];
  min_x = min([for (i = bez) i[0]]);
  max_x = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[1]]);
  max_y = max([for (i = bez) i[1]]);
  offset(0.5)
    resize([meeple_width - 0.5, meeple_length - 0.5])
      translate([-max_x + (max_x - min_x) / 2, -max_y + ( (max_y - min_y) / 2)])
        polygon(round_corners(bez, radius=5));
}

module PlayerBoards() {
  polygon(
    round_corners(
      [
        [0, 0],
        [0, player_board_thin_length],
        [player_board_thin_width, player_board_thin_length],
        [player_board_thin_width, player_board_length],
        [player_board_width - player_board_bump_width, player_board_length],
        [player_board_width - player_board_bump_width, player_board_bump_edge_offset + player_board_bump_length],
        [player_board_width, player_board_bump_edge_offset + player_board_bump_length],
        [player_board_width, player_board_bump_edge_offset],
        [player_board_width - player_board_bump_width, player_board_bump_edge_offset],
        [player_board_width - player_board_bump_width, 0],
      ], radius=2
    )
  );
}

module PlayerBox(colour = "yellow") // `make` me
{
  MakeBoxWithSlidingLid(
    width=player_box_width, length=player_box_length, height=player_box_height,
    lid_on_length=true,
    material_colour=colour
  ) {
    card_diff = 1 + single_card_thickness * 6;
    translate([0, 0, $inner_height - card_diff])
      cube([card_length, card_width, player_box_height]);
    translate([train_length / 2 + 25, train_width / 2 + 7, $inner_height - meeple_thickness - 0.5 - card_diff])
      linear_extrude(h=player_box_height)
        TrainToken();
    for (i = [0:2])
      translate([meeple_width / 2 + 9 + (meeple_width + 2) * i, meeple_length / 2 + 20, $inner_height - meeple_thickness - 0.5 - card_diff])
        linear_extrude(h=player_box_height)
          MeepleToken();
    translate([5, 2.5, $inner_height - card_diff - meeple_thickness / 2])
      RoundedBoxAllSides([card_length - 10, card_width - 5, player_box_height], radius=5);
    translate([$inner_width - 7, $inner_length / 2, $inner_height - player_cube - 0.5]) {
      cuboid([player_cube * 2, player_cube * 3, player_box_height], anchor=BOTTOM + RIGHT);
    }
    translate([$inner_width - 7 - player_cube * 2 - 5, $inner_length / 2 - player_cube * 2, $inner_height - player_cube / 2]) {
      RoundedBoxAllSides([player_cube * 2 + 10, player_cube * 3 + 10, player_box_height], radius=5);
    }
  }
}

module MoneyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=player_box_width, length=player_box_length, height=player_box_height,
    lid_on_length=true,
    material_colour="LightGrey"
  ) {
    RoundedBoxAllSides([$inner_width, $inner_length, player_box_height], radius=5);
  }
}

module EvidenceBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=player_box_width, length=player_box_length, height=player_box_height,
    lid_on_length=true,
    material_colour="LightSalmon"
  ) {
    RoundedBoxAllSides([$inner_width, $inner_length, player_box_height], radius=5);
  }
}

module ModuleCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=module_box_height
  ) {
    cube([card_width, card_length, module_box_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=module_box_height - default_lid_thickness, radius=15, spin=0);
  }
}

module Railroad01CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=railroad_0_1_height,
    material_colour="Cyan"
  ) {
    cube([card_width, card_length, railroad_0_1_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=railroad_0_1_height - default_lid_thickness, radius=15, spin=0);
  }
}

module Railroad24CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=railroad_2_4_height,
    material_colour="Cyan"
  ) {
    cube([card_width, card_length, railroad_2_4_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=railroad_2_4_height - default_lid_thickness, radius=15, spin=0);
  }
}

module Railroad712CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=railroad_7_12_height,
    material_colour="Cyan"
  ) {
    cube([card_width, card_length, railroad_7_12_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=railroad_7_12_height - default_lid_thickness, radius=15, spin=0);
  }
}

module WhodunitCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=whodunit_card_box_height
  ) {
    cube([card_width, card_length, whodunit_card_box_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=whodunit_card_box_height - default_lid_thickness, radius=15, spin=0);
  }
}

module GameEndCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=game_end_card_box_height,
    material_colour="DeepSkyBlue"
  ) {
    cube([card_width, card_length, game_end_card_box_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=game_end_card_box_height - default_lid_thickness, radius=15, spin=0);
  }
}

module StartTileCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=start_tile_box_height,
    material_colour="Khaki"
  ) {
    translate([($inner_width - start_player_tile_width) / 2, 0, 0])
      cube([start_player_tile_width, start_player_tile_length, start_tile_box_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=start_tile_box_height - default_lid_thickness, radius=15, spin=0);
  }
}

module LocomotiveCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=locomotive_box_width, length=locomotive_box_length, height=locomotive_box_height,
    material_colour="Aquamarine"
  ) {
    cube([locomotive_tile_width, locomotive_tile_length, locomotive_box_height]);
    translate([$inner_width / 2, 0, -2])
      FingerHoleBase(height=locomotive_box_height - default_lid_thickness, radius=15, spin=0);
  }
}

module PlayerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=player_box_width, length=player_box_length, text_str="Player", lid_on_length=true);
}

module MoneyBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=player_box_width, length=player_box_length, text_str="Money", lid_on_length=true);
}

module EvidenceBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=player_box_width, length=player_box_length, text_str="Evidence", lid_on_length=true);
}

module ModuleCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="Module");
}

module Railroad01CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="0-1");
}

module Railroad24CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="2-4");
}

module Railroad712CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="7-12");
}

module WhodunitCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="Whodunit");
}

module GameEndCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="End");
}

module StartTileCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=card_box_width, length=card_box_length, text_str="Start");
}

module LocomotiveCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(width=locomotive_box_width, length=locomotive_box_length, text_str="Locomotive");
}

module SpacerCardBox() // `make` me
{
  MakeBoxWithNoLid(
    length=spacer_card_box_length, width=spacer_card_box_width, height=spacer_card_box_height,
    hollow=true, $fn=16
  );
}

module RestSpacerBox() // `make` me
{
  rest_length = box_length - player_box_length - card_box_length - 2;
  path = [
    [0, card_box_length],
    [card_box_width + locomotive_box_width + 2, card_box_length],
    [card_box_width + locomotive_box_width + 2, 0],
    [box_width, 0],
    [box_width, rest_length],
    [0, rest_length],
  ];
  MakePathBoxWithNoLid(
    path=path, height=rest_spacer_box_height,
    hollow=true,
    $fn=16
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([1, box_length, box_height]);
  }

  if (layout <= 2) {
    translate([player_board_length, box_length - player_board_width, box_height - player_board_thickness - rule_book_thickness - board_thickness])
      color("BurlyWood")
        linear_extrude(height=player_board_thickness)
          rotate(90)
            PlayerBoards();
  }

  if (layout <= 1) {
    translate([0, 0, box_height - rule_book_thickness - board_thickness])
      color("brown")
        cube([score_board_width, score_board_length, board_thickness]);
    translate([0, 0, box_height - rule_book_thickness])
      color("darkblue")
        cube([box_width, box_length, rule_book_thickness]);
  }

  for (i = [0:2]) {
    if (layout <= 2 || i < 2)
      if (layout <= 3 || i < 1)
        translate([0, 0, player_box_height * i])
          PlayerBox(colour=player_colors[i]);
    if (i == 0)
      translate([player_box_width, 0, player_box_height * i])
        PlayerBox(colour=player_colors[i + 3]);
  }
  if (layout <= 3) {
    translate([player_box_width, 0, player_box_height * 1])
      MoneyBox();
  }
  if (layout <= 2) {
    translate([player_box_width, 0, player_box_height * 2])
      EvidenceBox();
  }
  for (i = [0:2]) {
    for (j = [0:2]) {
      if (layout <= 2 || j < 2)
        if (layout <= 3 || j < 1)
          if (!(i == 2 && j == 2))
            translate([card_box_width * i, player_box_length, module_box_height * j])
              ModuleCardBox();
    }
  }
  translate([card_box_width * 3, player_box_length, 0])
    Railroad01CardBox();
  if (layout <= 3)
    translate([card_box_width * 3, player_box_length, railroad_0_1_height])
      Railroad24CardBox();
  if (layout <= 2)
    translate([card_box_width * 2, player_box_length, module_box_height * 2])
      Railroad712CardBox();
  if (layout <= 2)
    translate([card_box_width * 3, player_box_length, railroad_0_1_height + railroad_2_4_height])
      WhodunitCardBox();
  translate([0, player_box_length + card_box_length, 0])
    GameEndCardBox();
  translate([0, player_box_length + card_box_length, game_end_card_box_height])
    StartTileCardBox();
  translate([card_box_width, player_box_length + card_box_length, 0])
    LocomotiveCardBox();
  if (layout <= 3)
    translate([0, player_box_length + card_box_length, locomotive_box_height])
      SpacerCardBox();
  if (layout <= 3)
    translate([0, player_box_length + card_box_length, 0])
      RestSpacerBox();
}

module BoxLayoutA() // `document` me
{
  BoxLayout(layout=1);
}

module BoxLayoutB() // `document` me
{
  BoxLayout(layout=2);
}

module BoxLayoutC() // `document` me
{
  BoxLayout(layout=3);
}

module BoxLayoutD() // `document` me
{
  BoxLayout(layout=4);
}

if (FROM_MAKE != 1) {
  BoxLayoutD();
}
