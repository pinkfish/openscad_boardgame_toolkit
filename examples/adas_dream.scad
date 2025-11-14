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

box_length = 291;
box_width = 212;
box_height = 90;

board_thickness = 31;

assignment_tiles_thickness = 9;
assignment_tiles_width = 16;
assignment_tiles_length = 232;
assignment_tiles_num = 4;

solo_reward_thickness = 16;
solo_reward_width_thin = 36;
solo_reward_width = 81;
solo_reward_length = 212;
solo_reward_num = 4;
solo_reward_length_thin = 22.5;

player_token_diameter = 20.5;
player_num = 12;
player_token_thickness = 6.5;

research_token_diameter = 10.5;
research_token_length = 22.5;
research_token_thin = 4;
research_token_thickness = 6;
resrarch_num = 4;

alternative_objective_width = 37.5;
alternative_objective_length = 77.5;
alternative_objective_num = 12;

objective_width = 33;
objective_length = 47;
objective_num = 24;

program_width = 25;
program_length = 41;
program_num = 28;

breakthrough_width = 17;
breakthrough_length = 21;
breakthrough_num = 9;

assignment_width = 21.5;
assignment_length = 35;
assignment_num = 16;

scoring_width = 18;
scoring_length = 34.5;
scoring_num = 16;

cardboard_thickness = 2;

university_width = 20.5;
university_length = 32.5;
university_cutout = 10;
university_num = 15;

gear_width = 26;
gear_thickness = 4;
addition_gear_num = 24;
subtraction_gear_num = 8;
multiply_gear_num = 12;

dice_thickness = 9.5;
dice_num = 50;

book_width = 13.5;
book_length = 21;
book_thickness = 6;
book_num = 12;

innovation_diameter = 14;
innovation_length = 18.5;
innovation_min_width = 6.5;
innovation_num = 4;

steam_width = 18.5;
steam_length = 17;
steam_small_length = 15;
steam_round_radius = 6;
steam_bottom_radius = 3;
steam_num = 4;

first_player_width = 25;
first_player_length = 45.5;
first_player_head_height = 9;
first_player_head_width = 5.5;
first_player_head_arm_width = 13;
first_player_shoulder_length = 19;
first_player_thickness = 11.5;

score_pad_width = 83.5;
score_pad_length = 96.5;
score_pad_thickness = 6;

card_width = 66;
card_length = 91;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

starting_player_card_num = 7;

tier_1_partner_card_num = 10;
tier_2_partner_card_num = 30;

assignment_card_num = 30;

exhibitor_card_num = 12;

partner_card_num = 4;

workshop_bonus_diameter = 33;

player_aid_width = 106;
player_aid_length = 150;

great_exhibition_board = 201;
great_exhibition_board_thickness = 4;

visitor_green_width = 23;
visitor_green_length = 25;
visitor_green_bottom_length = 19.5;
visitor_green_side_width = 12;

visitor_blue_width = 20;
visitor_blue_length = 26.5;

visitor_purple_width = 16.5;
visitor_purple_length = 27;

visitor_yellow_width = 12;
visitor_yellow_length = 27;

visitor_thickness = 6.5;

card_box_width = card_length + default_wall_thickness * 2;
card_box_length = card_width + default_wall_thickness * 2;
card_box_height = default_lid_thickness + default_floor_thickness + single_card_thickness * assignment_card_num;
tier_card_box_height = default_lid_thickness + default_floor_thickness + single_card_thickness * (tier_1_partner_card_num + tier_2_partner_card_num);

player_box_height = (box_height - board_thickness - 1) / 2;

book_box_height = solo_reward_thickness;
book_box_length = default_wall_thickness * 2 + (book_length + 1) * 4;
book_box_width = card_box_width - solo_reward_width_thin;

scoring_box_width = book_box_width;
scoring_box_length = box_length - book_box_length - card_box_length - solo_reward_length_thin - 2;
scoring_box_height = book_box_height;

program_box_width = card_box_width;
program_box_length = (program_width + 2) * 4 + default_wall_thickness * 2;
program_box_height = default_floor_thickness + default_lid_thickness + cardboard_thickness * 4 + 1;

assignment_box_width = card_box_width;
assignment_box_length = default_wall_thickness * 2 + (assignment_length + 2) * 1;
assignment_box_height = program_box_height;

university_box_width = card_box_width;
univeristy_box_length = default_wall_thickness * 2 + (university_length + 2) * 1;
university_box_height = program_box_height;

solo_card_box_height = program_box_height;

steam_box_width = card_box_width;
steam_box_length = box_length - card_box_length - program_box_length - assignment_box_length - univeristy_box_length;
steam_box_height = program_box_height;

objective_box_width = card_box_width;
objective_box_length = box_length - card_box_length * 2 - 1;
objective_box_height = program_box_height;

alternative_objective_box_height = box_height - board_thickness - great_exhibition_board_thickness - 1 - objective_box_height - program_box_height - steam_box_height;
alternative_objective_box_width = card_box_width;
alternative_objective_box_length = default_wall_thickness * 2 + (alternative_objective_length + 2) * 2;

visitor_box_width = card_box_width;
visitor_box_length = box_length - card_box_length - alternative_objective_box_length - 1;
visitor_box_height = alternative_objective_box_height;

dice_box_width = card_box_width;
dice_box_length = score_pad_length + default_wall_thickness * 2;
dice_box_height = dice_thickness + default_floor_thickness + default_lid_thickness;

score_pad_box_width = dice_box_width;
score_pad_box_length = score_pad_length + default_wall_thickness * 2;
score_pad_box_height = default_floor_thickness + default_lid_thickness + score_pad_thickness;

cog_box_width = box_width - card_box_width;
cog_box_length = box_length - card_box_length * 2 - score_pad_box_length;
cog_box_height = (box_height - board_thickness - great_exhibition_board_thickness - 1) / 3;

/*
resource_box_width = box_height - board_thickness - great_exhibition_board_thickness - 1;
resource_box_height = assignment_tiles_width;
resource_box_length = assignment_tiles_length / 2;
*/

resource_box_width = score_pad_box_width / 2;
resource_box_length = score_pad_box_length;
resource_box_height = (box_height - board_thickness - great_exhibition_board_thickness - score_pad_box_height - dice_box_height - 1) / 2;

money_box_width = score_pad_width;
money_box_length = score_pad_length;
money_box_height = resource_box_height;

spacer_side_box_length = score_pad_box_length + card_box_length * 2;
spacer_side_box_width = box_width - card_box_width * 2 - 1;
spacer_side_box_height = box_height - board_thickness - great_exhibition_board_thickness - assignment_tiles_thickness;

module FirstPlayerToken() {
  translate([-first_player_width / 2, -first_player_length / 2]) {
    rect(
      [first_player_width, first_player_length - first_player_shoulder_length],
      rounding=1, anchor=FRONT + LEFT
    );
    translate([first_player_width / 2 - first_player_head_width / 2, 0])
      rect(
        [first_player_head_width, first_player_length],
        rounding=1, anchor=FRONT + LEFT
      );
    translate([first_player_width / 2 - first_player_head_arm_width / 2, 0])
      rect(
        [first_player_head_arm_width, first_player_length - first_player_head_height],
        rounding=1, anchor=FRONT + LEFT
      );
  }
  // first_player_width = 25;
  // first_player_length = 45.5;
  // first_player_head_height = 9;
  // first_player_head_width = 5.5;
  // first_player_head_arm_width = 13;
  // first_player_shoulder_length = 19;
}

module ResearchToken() {
  translate([-research_token_length / 2 + research_token_diameter / 2, 0, 0]) {
    circle(d=research_token_diameter);
    hull() {
      circle(d=research_token_thin);
      research_token_diameter = 10.5;
      translate([research_token_length - research_token_thin / 2 - research_token_diameter / 2, 0, 0])
        circle(d=research_token_thin);
    }
  }
}

module SteamToken() {
  hull() {
    circle(d=steam_round_radius);
    translate([0, steam_small_length - steam_round_radius])
      circle(d=steam_round_radius);
    translate([0, steam_length - steam_bottom_radius / 2 - steam_round_radius / 2])
      circle(d=steam_bottom_radius);
  }
  hull() {
    translate([steam_width / 2 - steam_round_radius / 2, steam_small_length - steam_round_radius])
      circle(d=steam_round_radius);
    translate([-steam_width / 2 + steam_round_radius / 2, steam_small_length - steam_round_radius])
      circle(d=steam_round_radius);
  }
  hull() {
    translate([-(steam_width / 2 - steam_round_radius / 2) / 2, (steam_small_length - steam_round_radius) / 2])
      circle(d=steam_round_radius);
    translate([(steam_width / 2 - steam_round_radius / 2) / 2, (steam_small_length - steam_round_radius) / 2])
      circle(d=steam_round_radius);
  }
  //steam_width = 18.5;
  //steam_length = 17;
  //steam_small_length = 15;
  //steam_round_radius = 6;
  //steam_num = 4;
}

module InnovationToken(height) {
  cyl(d=innovation_diameter, h=height, anchor=BOTTOM);
  translate([0, innovation_length / 2 - innovation_min_width / 2, 0])
    cyl(d=innovation_min_width, h=height, anchor=BOTTOM);
}

module AssignmentCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    height=card_box_height,
    lid_on_length=true,
    material_colour="purple"
  ) {
    cube([$inner_width, $inner_length, card_box_height]);
    translate(
      [0, $inner_length / 2, $inner_height - card_box_height]
    )
      FingerHoleBase(radius=15, height=card_box_height, spin=270);
  }
}

module TierCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    height=tier_card_box_height,
    lid_on_length=true,
    material_colour="brown"
  ) {
    cube([$inner_width, $inner_length, tier_card_box_height]);
    translate(
      [0, $inner_length / 2, $inner_height - tier_card_box_height]
    )
      FingerHoleBase(radius=15, height=tier_card_box_height, spin=270);
  }
}

module SoloCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    height=solo_card_box_height,
    lid_on_length=true,
    material_colour="purple"
  ) {
    cube([$inner_width, $inner_length, card_box_height]);
    translate(
      [0, $inner_length / 2, $inner_height - card_box_height]
    )
      FingerHoleBase(radius=15, height=card_box_height, spin=270);
  }
}

module SteamInnovationBox() // `make` me
{
  MakeBoxWithCapLid(
    width=steam_box_width,
    length=steam_box_length,
    height=steam_box_height,
    material_colour="yellow"
  ) {
    for (i = [0:0]) {
      for (j = [0:3]) {
        translate(
          [
            (innovation_diameter / 2 + 3) * j + innovation_diameter / 2,
            (innovation_diameter + 1) * i + innovation_diameter / 2 + (j % 2) * (innovation_diameter - 3),
            $inner_height - cardboard_thickness * 4 - 0.5,
          ]
        ) rotate((j % 2) * 180) {
            InnovationToken(steam_box_height);
          }
      }
    }
    for (i = [0:3]) {
      translate(
        [
          $inner_width - (steam_width / 2 + 1) * i - steam_width / 2,
          steam_length - steam_round_radius / 2 + (i % 2) * 2 - 2.5,
          $inner_height - cardboard_thickness * 4 - 0.5,
        ]
      ) rotate((i % 2) * 180) {
          linear_extrude(height=steam_box_height) SteamToken();
        }
    }
  }
}

module AssignmentBox() // `make` me
{
  MakeBoxWithCapLid(
    width=assignment_box_width,
    length=assignment_box_length,
    height=assignment_box_height,
    material_colour="lightblue"
  ) {
    for (i = [0:0]) {
      for (j = [0:3]) {
        translate(
          [
            (assignment_width + 1) * j + 1,
            (assignment_length + 1) * i + 1,
            $inner_height - cardboard_thickness * 4 - 0.5,
          ]
        )
          cube([assignment_width, assignment_length, cardboard_thickness * 4 + 1]);
      }
    }
  }
}

module UniversityBox() // `make` me
{
  MakeBoxWithCapLid(
    width=university_box_width,
    length=univeristy_box_length,
    height=university_box_height,
    material_colour="aqua"
  ) {
    for (i = [0:0]) {
      for (j = [0:3]) {
        translate(
          [
            (university_width + 2) * j + 1,
            (university_length + 1) * i + 1,
            $inner_height - cardboard_thickness * (j == 3 ? 3 : 4) - 0.5,
          ]
        )
          difference() {
            cube([university_width, university_length, cardboard_thickness * 4 + 1]);
            cyl(d=university_cutout, anchor=BOTTOM, h=university_box_height);
          }
      }
    }
  }
}

module BookBox() // `make` me
{
  MakeBoxWithCapLid(
    width=book_box_width,
    length=book_box_length,
    height=book_box_height,
    material_colour="red"
  ) {
    for (i = [0:3]) {
      for (j = [0:2]) {
        translate(
          [
            (book_width + 2) * j + 4,
            (book_length + 1) * i,
            $inner_height - book_thickness - 0.5,
          ]
        )
          cube([book_width, book_length, book_thickness + 1]);
      }
    }
  }
}

module ProgramBox() // `make` me
{
  MakeBoxWithCapLid(
    width=program_box_width,
    length=program_box_length,
    height=program_box_height,
    material_colour="brown"
  ) {
    // breakthrough tiles.
    for (i = [0:3]) {
      for (j = [0:1]) {
        translate(
          [
            (program_length + 7.5) * j + 1,
            (program_width + 2) * i + 1,
            $inner_height - cardboard_thickness * (i >= 2 ? 3 : 4) - 0.5,
          ]
        )
          cube([program_length, program_width, cardboard_thickness * 4 + 1]);
      }
    }
  }
}

module ScoringBox() // `make` me
{
  MakeBoxWithCapLid(
    width=scoring_box_width,
    length=scoring_box_length,
    height=scoring_box_height,
    material_colour="lightgrey"
  ) {
    // breakthrough tiles.
    for (i = [0:0]) {
      for (j = [0:2]) {
        translate(
          [
            (breakthrough_width + 1) * j + 1,
            (breakthrough_length + 2) * i + 2,
            $inner_height - cardboard_thickness * 3 - 0.5,
          ]
        )
          cube([breakthrough_width, breakthrough_length, cardboard_thickness * 3 + 1]);
      }
    }
    // Scoring tiles.
    translate([0, breakthrough_length + 4, 0]) {
      for (i = [0:1]) {
        for (j = [0:1]) {
          translate(
            [
              (scoring_width + 15) * j + 1,
              (scoring_length + 2) * i + 2,
              $inner_height - cardboard_thickness * 4 - 0.5,
            ]
          )
            cube([scoring_width, scoring_length, cardboard_thickness * 4 + 1]);
        }
      }
    }
  }
}

module PlayerBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    height=player_box_height,
    material_colour="blue"
  ) {
    card_height = single_card_thickness * starting_player_card_num - 0.5;
    translate([0, $inner_length / 2, $inner_height - card_height + 0.01])
      FingerHoleWall(height=card_height, radius=20, spin=270);
    translate([0, 0, $inner_height - card_height])
      cube([$inner_width, $inner_length, single_card_thickness * starting_player_card_num + 1]);
    for (i = [0:3]) {
      // research tokens
      translate(
        [
          research_token_length / 2 + 2,
          research_token_diameter / 2 + 2 + (research_token_diameter + 1) * i,
          $inner_height - card_height - research_token_thickness,
        ]
      )
        linear_extrude(height=research_token_thickness + 1) ResearchToken();
    }
    for (i = [0:2]) {
      // player discs
      translate(
        [
          $inner_width - player_token_diameter / 2 - 2,
          player_token_diameter / 2 + (player_token_diameter + 1) * i,
          $inner_height - card_height - player_token_thickness,
        ]
      )
        linear_extrude(height=player_token_thickness + 1)
          circle(d=player_token_diameter);
      translate(
        [
          $inner_width - player_token_diameter / 2 - 3 - player_token_diameter,
          player_token_diameter / 2 + (player_token_diameter + 1) * i,
          $inner_height - card_height - player_token_thickness * 2,
        ]
      )
        linear_extrude(height=player_token_thickness * 2 + 1)
          circle(d=player_token_diameter);
    }
  }
}

module ObjectiveBox() // `make` me
{
  MakeBoxWithCapLid(
    width=objective_box_width,
    length=objective_box_length,
    height=objective_box_height,
    material_colour="orange"
  ) {
    for (i = [0:2]) {
      for (j = [0:1]) {
        // objectives
        translate(
          [
            (objective_width + 19) * j + 2,
            1 + (objective_length + 1.5) * i,
            $inner_height - cardboard_thickness * 4,
          ]
        )
          cube([objective_width, objective_length, objective_box_height]);
      }
    }
  }
}

module AlternativeObjectiveBox() // `make` me
{
  MakeBoxWithCapLid(
    width=alternative_objective_box_width,
    length=alternative_objective_box_length,
    height=alternative_objective_box_height,
    material_colour="purple"
  ) {
    for (i = [0:1]) {
      for (j = [0:1]) {
        // objectives
        translate(
          [
            (alternative_objective_width + 11) * j + 2,
            1 + (alternative_objective_length + 1.5) * i,
            $inner_height - cardboard_thickness * 4,
          ]
        )
          cube([alternative_objective_width, alternative_objective_length, alternative_objective_box_height]);
      }
    }
  }
}

module VisitorBox() // `make` me
{
  MakeBoxWithCapLid(
    width=visitor_box_width,
    length=visitor_box_length,
    height=visitor_box_height,
    material_colour="pink"
  ) {
    translate([2, 0.25, 0]) {
      translate([0, 0, $inner_height - visitor_thickness])
        cube([visitor_yellow_width, visitor_yellow_length, visitor_thickness]);
      translate([visitor_yellow_width + 2, 0, $inner_height - visitor_thickness])
        cube([visitor_blue_width, visitor_blue_length, visitor_thickness]);
      translate([visitor_yellow_width + 4 + visitor_blue_width, 0, $inner_height - visitor_thickness])
        cube([visitor_purple_width, visitor_purple_length, visitor_thickness]);
      translate([visitor_yellow_width + 6 + visitor_blue_width + visitor_purple_width, 0, $inner_height - visitor_thickness]) {
        cube([visitor_green_side_width, visitor_green_length, visitor_thickness]);
        cube([visitor_green_length, visitor_green_bottom_length, visitor_thickness]);
      }
      translate([$inner_width - first_player_length / 2 - 3, $inner_length - first_player_width / 2 - 1, 0])
        linear_extrude(height=first_player_thickness)
          rotate(90)
            FirstPlayerToken();
    }
    translate([$inner_width / 2, $inner_length / 2, $inner_height - 4])
      cuboid([$inner_width - 2, $inner_length - 2, 20], rounding=4, anchor=BOTTOM);
  }
}

module DiceBox() // `make` me
{
  MakeBoxWithCapLid(
    width=dice_box_width,
    length=dice_box_length,
    height=dice_box_height,
    material_colour="green"
  ) {
    translate([7, 10, 0]) {
      cube([dice_thickness * 8, dice_thickness * 6, dice_thickness]);
      translate([0, dice_thickness * 6 - 0.5, 0])
        cube([dice_thickness * 2, dice_thickness + 0.5, dice_thickness]);
    }
    translate([$inner_width / 2, $inner_length / 2, $inner_height - 4])
      cuboid([$inner_width - 2, $inner_length - 2, 20], rounding=4, anchor=BOTTOM);
  }
}

module ScorePadBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=score_pad_box_width,
    length=score_pad_box_length,
    height=score_pad_box_height,
    material_colour="white"
  ) {
    translate([$inner_width / 2, $inner_length / 2, 0])
      cuboid([score_pad_width, score_pad_length, score_pad_box_height], anchor=BOTTOM);
    translate(
      [$inner_width / 2, 0, $inner_height - score_pad_box_height + 0.01]
    )
      FingerHoleBase(radius=15, height=score_pad_box_height, spin=0);
  }
}

module GearBox(top_box = false) // `make` me
{
  MakeBoxWithCapLid(
    width=cog_box_width,
    length=cog_box_length,
    height=cog_box_height,
    material_colour = "blue"
  ) {
    for (i = [0:1])
      for (j = [0:1]) {
        translate(
          [
            (j % 2 == 0 ? gear_width / 2 : gear_width * 1.17) + gear_width * i * 1.35,
            (j % 2 == 0 ? gear_width / 2 : $inner_length - gear_width / 2),
            $inner_height - gear_thickness * 3,
          ]
        ) {
          cyl(d=gear_width, h=cog_box_height, anchor=BOTTOM);
        }
      }
    translate(
      [
        $inner_width - gear_width / 2 - 2,
        $inner_length / 2,
        $inner_height - gear_thickness * (top_box ? 2 : 3),
      ]
    ) {
      cyl(d=gear_width, h=cog_box_height, anchor=BOTTOM);
    }
  }
}

module GearBoxTop() // `make` me
{
  GearBox(top_box=true);
}

module ResourceBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    material_colour= "gold"
  ) {
    echo([$inner_height, $inner_width, $inner_length]);
    RoundedBoxAllSides(
      width=$inner_width,
      length=$inner_length, height=resource_box_height, radius=5
    );
  }
}

module MoneyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=money_box_width,
    length=money_box_length,
    height=money_box_height
  ) {
    echo([$inner_height, $inner_width, $inner_length]);
    RoundedBoxAllSides(
      width=$inner_width,
      length=$inner_length, height=money_box_height, radius=5, 
      material_colour = "silver"
    );
  }
}

module SpacerSide() // `make` me
{
  MakeBoxWithNoLid(
    width=spacer_side_box_width,
    length=spacer_side_box_length,
    height=spacer_side_box_height,
    hollow=true
  );
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, box_height]);
  translate([0, box_length - great_exhibition_board, box_height - great_exhibition_board_thickness])
    cube([box_width, great_exhibition_board, great_exhibition_board_thickness]);
  translate([0, 0, board_thickness]) {
    translate([0, box_length - solo_reward_length, 0]) {
      cube([solo_reward_width_thin, solo_reward_length, solo_reward_thickness]);
      translate([0, solo_reward_length - solo_reward_length_thin, 0])
        cube([solo_reward_width, solo_reward_length_thin, solo_reward_thickness]);
    }
    translate([box_width - assignment_tiles_width, 0])
      cube([assignment_tiles_width, assignment_tiles_length, assignment_tiles_thickness]);
    translate([card_box_width, card_box_length, 0])
      AssignmentCardBox();
    translate([card_box_width, card_box_length, card_box_height])
      TierCardBox();
    for (i = [0:1]) {
      translate([0, 0, player_box_height * i])
        PlayerBox();
      translate([card_box_width, 0, player_box_height * i])
        PlayerBox();
    }
    translate([solo_reward_width_thin, card_box_length, 0])
      BookBox();
    translate([solo_reward_width_thin, card_box_length + book_box_length, 0])
      ScoringBox();
    translate([0, card_box_length, book_box_height])
      ProgramBox();
    translate([0, card_box_length + program_box_length, book_box_height])
      AssignmentBox();
    translate([0, card_box_length + program_box_length + assignment_box_length, book_box_height])
      UniversityBox();
    translate([0, card_box_length + program_box_length + assignment_box_length + univeristy_box_length, book_box_height])
      SteamInnovationBox();
    translate([0, card_box_length, book_box_height + steam_box_height])
      ObjectiveBox();
    translate([0, card_box_length + objective_box_length, book_box_height + steam_box_height])
      SoloCardBox();
    translate([0, card_box_length, book_box_height + steam_box_height + objective_box_height])
      AlternativeObjectiveBox();
    translate([0, card_box_length + alternative_objective_box_length, book_box_height + steam_box_height + objective_box_height])
      VisitorBox();
    translate([card_box_width, card_box_length * 2, 0])
      DiceBox();
    translate([card_box_width, card_box_length * 2, dice_box_height])
      ScorePadBox();
    translate([card_box_width, card_box_length * 2, dice_box_height + score_pad_box_height])
      ResourceBox();
    translate([card_box_width + resource_box_width, card_box_length * 2, dice_box_height])
      ResourceBox();
    translate([card_box_width, card_box_length * 2, dice_box_height + score_pad_box_height + resource_box_height])
      MoneyBox();
    for (i = [0:2]) {
      translate([card_box_width, card_box_length * 2 + score_pad_box_length, cog_box_height * i])
        GearBox();
    }
    translate([card_box_width * 2, 0, assignment_tiles_thickness])
      SpacerSide();
    /*
    translate([card_box_width * 2, 0, assignment_tiles_thickness+resource_box_width])
      rotate([0, 90, 0])
        ResourceBox();
    translate([card_box_width * 2, resource_box_length, assignment_tiles_thickness+resource_box_width])
      rotate([0, 90, 0])
        ResourceBox();
        */
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
