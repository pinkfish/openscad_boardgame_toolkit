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

default_label_font = "Impact";
default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_lid_catch_type = CATCH_BUMPS_LONG;
default_lid_shape_type = SHAPE_TYPE_PENTAGON_R1;

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

player_token_diameter = 16.5;
player_num = 12;
player_token_thickness = 6.5;

research_token_diameter = 11.5;
research_token_length = 20;
research_token_thin = 4;
research_token_thickness = 6;
resrarch_num = 4;

alternative_objective_width = 38.5;
alternative_objective_length = 78.5;
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

dice_thickness = 14.5;
dice_num = 50;

book_width = 14;
book_length = 21.25;
book_thickness = 6;
book_num = 12;

innovation_diameter = 15;
innovation_length = 18.5;
innovation_min_width = 6.5;
innovation_num = 4;

steam_width = 20;
steam_length = 18;
steam_small_length = 15;
steam_round_radius = 7;
steam_bottom_radius = 3;
steam_num = 4;

first_player_width = 25;
first_player_length = 45.5;
first_player_head_height = 9;
first_player_head_width = 5.5;
first_player_head_arm_width = 13;
first_player_shoulder_length = 19;
first_player_thickness = 11.5;

man_player_height = 26;
man_player_coat_width = 12.5;
man_player_coat_height_from_top = 11.5;
man_player_head_width = 5;
man_player_head_height = 4.5;
man_player_trouser_top_width = 11.5;
man_player_trouser_middle_width = 8;
man_player_foot_height = 2;
woman_player_height = 21.5;
woman_player_width = 12.5;
woman_player_dress_height = 12.5;
woman_player_dress_top_width = 9.5;
woman_player_top_widht = 6.5;
woman_player_head_width = 5.2;
woman_player_head_height = 3;
woman_player_shoulder_width = 6;
woman_man_player_thickness = 8.5;

score_pad_width = 83.5;
score_pad_length = 96.5;
score_pad_thickness = 6;

card_width = 66;
card_length = 91;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;
assignment_card_width = 48;
assignment_card_length = 70.5;
other_card_num = 24;

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
visitor_purple_length = 27.5;

visitor_yellow_width = 12;
visitor_yellow_length = 28;

visitor_thickness = 6.5;

card_box_width = card_length + default_wall_thickness * 2;
card_box_length = card_width + default_wall_thickness * 2;
tier_card_box_height = default_lid_thickness + default_floor_thickness + single_card_thickness * (tier_1_partner_card_num + tier_2_partner_card_num);

player_box_height = default_floor_thickness + default_lid_thickness + player_token_thickness * 2 + single_card_thickness * (starting_player_card_num + 2);

book_box_height = solo_reward_thickness;
book_box_length = default_wall_thickness * 2 + (book_length + 1) * 4;
book_box_width = card_box_width - solo_reward_width_thin;

steam_box_width = card_box_width;
steam_box_length = default_wall_thickness * 2 + steam_length + 9;
steam_box_height = box_height - player_box_height * 2 - board_thickness;

scoring_box_width = card_box_width;
scoring_box_length = card_box_length - steam_box_length; //box_length - book_box_length - card_box_length - solo_reward_length_thin - 2;
scoring_box_height = steam_box_height;

assignment_box_width = book_box_width;
assignment_box_length = box_length - solo_reward_length_thin - 2 - card_box_length - book_box_length;
assignment_box_height = book_box_height;

other_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * (other_card_num);

dice_box_width = card_box_width;
dice_box_length = default_wall_thickness * 2 + dice_thickness * 9 + 1.5;
dice_box_height = dice_thickness + default_floor_thickness + default_lid_thickness;

score_pad_box_width = dice_box_width;
score_pad_box_length = score_pad_length + default_wall_thickness * 2;
score_pad_box_height = default_floor_thickness + default_lid_thickness + score_pad_thickness;

program_box_width = program_length + default_wall_thickness * 2;
program_box_length = program_width * 2 + default_wall_thickness * 3;
program_box_height = box_height - board_thickness - solo_reward_thickness - great_exhibition_board_thickness;

university_box_width = program_box_width;
univeristy_box_length = score_pad_box_length - program_box_length;
university_box_height = program_box_height;

cog_box_width = box_width - card_box_width;
cog_box_length = box_length - card_box_length * 2 - score_pad_box_length;
cog_box_height = (box_height - board_thickness - great_exhibition_board_thickness - 1) / 3;

assignment_card_box_width = box_width - cog_box_width - 1;
assignment_card_box_length = assignment_card_width + default_wall_thickness * 2;
assignment_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * assignment_card_num + 1; // box_height - board_thickness - great_exhibition_board_thickness - solo_reward_thickness - 1; 

alternative_objective_box_height = box_height - board_thickness - great_exhibition_board_thickness - 1 - dice_box_height - solo_reward_thickness;
alternative_objective_box_width = card_box_width;
alternative_objective_box_length = box_length - card_box_length - assignment_card_box_length - 1;

objective_box_width = box_width - card_box_width * 2 - 1;
objective_box_length = default_wall_thickness * 5 + objective_length * 3;
objective_box_height = (player_box_height * 2 - assignment_tiles_thickness);

first_player_box_length = box_length - card_box_length - dice_box_length - assignment_card_box_length;
first_player_box_width = card_box_width;
first_player_box_height = dice_box_height;

visitor_box_width = card_box_width;
visitor_box_length = card_box_length - univeristy_box_length;
visitor_box_height = alternative_objective_box_height;

resource_box_width = score_pad_box_width / 2;
resource_box_length = score_pad_box_length;
resource_box_height = (box_height - board_thickness - great_exhibition_board_thickness - score_pad_box_height - 1) / 2;

money_box_width = box_width - card_box_width - 1;
money_box_length = card_box_length;
money_box_height = steam_box_height;

spacer_side_box_length = score_pad_box_length + card_box_length * 2 - objective_box_length;
spacer_side_box_width = box_width - card_box_width * 2 - 1;
spacer_side_box_height = (player_box_height * 2 - assignment_tiles_thickness);

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

module VisitorTokenYellow() {
  cuboid([visitor_yellow_width, visitor_yellow_length, visitor_thickness + 2], anchor=BOTTOM);
}

module VisitorTokenBlue() {
  cuboid([visitor_blue_width, visitor_blue_length, visitor_thickness + 2], anchor=BOTTOM);
}

module VisitorTokenPurple() {
  cuboid([visitor_purple_width, visitor_purple_length, visitor_thickness + 2], anchor=BOTTOM);
}

module VisitorTokenGreen() {
  cuboid([visitor_green_side_width, visitor_green_length, visitor_thickness + 2], anchor=BOTTOM);
  translate([(visitor_green_width - visitor_green_side_width) / 2, (visitor_green_length - visitor_green_bottom_length) / 2, 0])
    cuboid([visitor_green_width, visitor_green_bottom_length, visitor_thickness + 2], anchor=BOTTOM);
}

module ManPlayerToken() {
  translate([0, -man_player_height / 2]) {
    translate([0, 0])
      rect(
        [man_player_head_width, man_player_head_height],
        rounding=[0, 0, 1, 1],
        anchor=FRONT
      );
    translate([0, man_player_head_height])
      rect(
        [man_player_coat_width, man_player_coat_height_from_top], anchor=FRONT,
        rounding=0.5
      );
    echo([man_player_trouser_middle_width]);
    translate([0, man_player_head_height])
      rect(
        [man_player_trouser_middle_width, man_player_height - man_player_head_height],
        anchor=FRONT,
      );
    translate([0, man_player_height - man_player_foot_height])
      rect(
        [man_player_trouser_top_width, man_player_foot_height], anchor=FRONT,
        rounding=0.5
      );
  }
}

module WomanPlayerToken() {
  translate([0, -woman_player_height / 2]) {
    translate([0, 0])
      rect(
        [woman_player_head_width, woman_player_head_height],
        rounding=[0, 0, 1, 1],
        anchor=FRONT
      );
    translate([0, woman_player_head_height])
      rect(
        [woman_player_shoulder_width, woman_player_height - woman_player_head_height],
        rounding=1,
        anchor=FRONT
      );
    translate([0, woman_player_height - woman_player_dress_height])
      trapezoid(
        h=woman_player_dress_height,
        w2=woman_player_width,
        w1=woman_player_dress_top_width,
        rounding=0.5,
        anchor=FRONT,
      );
  }
}

module InnovationToken(height) {
  cyl(d=innovation_diameter, h=height, anchor=BOTTOM);
  hull() {
    cyl(d=innovation_min_width, h=height, anchor=BOTTOM);
    translate([0, innovation_length / 2, 0])
      cyl(d=innovation_min_width, h=height, anchor=BOTTOM);
  }
}

module AssignmentCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=assignment_card_box_width,
    length=assignment_card_box_length,
    height=assignment_card_box_height,
    lid_on_length=true,
    material_colour="purple"
  ) {
    cube([assignment_card_length, $inner_length, assignment_card_box_height]);
    translate(
      [0, $inner_length / 2, $inner_height - assignment_card_box_height]
    )
      FingerHoleBase(radius=15, height=assignment_card_box_height, spin=270);
  }
}

module AssignmentCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    material_colour="purple",
    text_str="Assignment"
  );
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

module TierCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    material_colour="purple",
    text_str="Tier"
  );
}

module OtherCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    height=other_card_box_height,
    lid_on_length=true,
    material_colour="purple"
  ) {
    cube([$inner_width, $inner_length, other_card_box_height]);
    translate(
      [0, $inner_length / 2, $inner_height - other_card_box_height]
    )
      FingerHoleBase(radius=15, height=other_card_box_height, spin=270);
  }
}

module OtherCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    material_colour="purple",
    text_str="Other"
  );
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
            (innovation_diameter / 2 + 2.6) * j + innovation_diameter / 2 - 0.5,
            (innovation_diameter + 1) * i + innovation_diameter / 2 + (j % 2) * (innovation_diameter - 3),
            $inner_height - cardboard_thickness * 4 - 0.5,
          ]
        ) {
          if (j != 3) {
            rotate((j % 2) * 180) {
              InnovationToken(steam_box_height);
            }
          } else {
            rotate(-70)
            InnovationToken(steam_box_height);
          }
        }
      }
    }
    for (i = [0:3]) {
      translate(
        [
          $inner_width - (steam_width / 2 + 1) * i - steam_width / 2,
          steam_length - steam_round_radius / 2 + (i % 2) * 3.2 - 2.5,
          $inner_height - cardboard_thickness * 4 - 0.5,
        ]
      ) rotate((i % 2) * 180) {
          linear_extrude(height=steam_box_height) SteamToken();
        }
    }
    translate([0, 0, $inner_height - cardboard_thickness * 2])
      RoundedBoxAllSides(
        width=$inner_width,
        length=$inner_length, height=steam_box_height, radius=5,
      );
  }
}

module SteamInnovationBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=steam_box_width,
    length=steam_box_length,
    height=steam_box_height,
    material_colour="yellow",
    text_str="Steam"
  );
}

module AssignmentBox() // `make` me
{
  MakeBoxWithCapLid(
    width=assignment_box_width,
    length=assignment_box_length,
    height=assignment_box_height,
    material_colour="lightblue"
  ) {
    for (i = [0:1]) {
      for (j = [0:1]) {
        translate(
          [
            (assignment_width + 1) * j + 1,
            (assignment_length + 1) * i + 1,
            $inner_height - cardboard_thickness * 4 - 0.5,
          ]
        )
          CuboidWithIndentsBottom(
            [assignment_width, assignment_length, cardboard_thickness * 4 + 1],
            anchor=BOTTOM + FRONT + LEFT,
            finger_holes=[j == 0 ? 2 : 6]
          );
      }
    }
    /*
    translate([$inner_width / 2, $inner_length - first_player_width / 2 - 1, $inner_height - first_player_thickness - 0.5]) {
      translate([first_player_length / 2, 0, 0])
        cyl(r=5, anchor=BOTTOM, h=assignment_box_height, rounding=2.5);
      linear_extrude(h=assignment_box_height)
        rotate(90)
          FirstPlayerToken();
      translate([-$inner_width / 2, -first_player_width / 2 - 2, $inner_height - first_player_thickness / 2])
        RoundedBoxAllSides(
          width=$inner_width, length=first_player_width + 4,
          height=assignment_box_height,
          radius=5
        );
    }
    */
  }
}

module AssignmentBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=assignment_box_width,
    length=assignment_box_length,
    height=assignment_box_height,
    material_colour="lightblue",
    "Assignment"
  );
}

module UniversityBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=university_box_width,
    length=univeristy_box_length,
    height=university_box_height,
    material_colour="aqua"
  ) {
    for (i = [0:0]) {
      for (j = [0:0]) {
        translate(
          [
            $inner_width / 2,
            (university_width + 1) * i,
            $inner_height - cardboard_thickness * 16 - 0.5,
          ]
        ) {
          difference() {
            CuboidWithIndentsBottom(
              [university_width, university_length, cardboard_thickness * 17 + 1],
              anchor=BOTTOM + FRONT,
            );
            translate([-university_width / 2, university_length, 0])
              cyl(d=university_cutout, anchor=BOTTOM, h=university_box_height);
          }
        }
      }
    }
    translate(
      [$inner_width / 2, 0, $inner_height - university_box_height]
    )
      FingerHoleBase(radius=8.5, height=university_box_height, spin=0);
  }
}

module UniversityBoxLid() // `make` me
{
  SlidingBoxLidWithShape(
    width=university_box_width,
    length=univeristy_box_length,
    material_colour="aqua"
  );
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
            $inner_height - book_thickness * (i < 2 || i == 2 && j < 2 ? 2 : 1) - 0.5,
          ]
        )
          CuboidWithIndentsBottom(
            [book_width, book_length, book_thickness * 3 + 1],
            anchor=BOTTOM + FRONT + LEFT,
            finger_holes=[j == 0 ? 2 : 6]
          );
      }
    }
  }
}

module BookBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=book_box_width,
    length=book_box_length,
    height=book_box_height,
    material_colour="red",
    text_str="Book"
  );
}

module ProgramBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=program_box_width,
    length=program_box_length,
    height=program_box_height,
    lid_on_length=true,
    material_colour="brown"
  ) {
    // program tiles.
    translate(
      [
        0,
        0,
        $inner_height - cardboard_thickness * 14 - 0.5,
      ]
    )
      cube([program_length, program_width, cardboard_thickness * 14 + 1]);
    translate(
      [
        0,
        program_width + default_wall_thickness,
        $inner_height - cardboard_thickness * 14 - 0.5,
      ]
    )
      cube([program_length, program_width, cardboard_thickness * 14 + 1]);

    translate(
      [0, $inner_length / 2, $inner_height - assignment_card_box_height]
    )
      FingerHoleBase(radius=15, height=assignment_card_box_height, spin=270);
  }
}

module ProgramBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=program_box_width,
    length=program_box_length,
    height=program_box_height,
    material_colour="brown",
    text_str="Program",
    lid_on_length=true,
  );
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
    for (i = [0:1]) {
      for (j = [0:0]) {
        translate(
          [
            (breakthrough_length + 1) * j + 1.5,
            (breakthrough_width + 1) * i + 0.55,
            $inner_height - cardboard_thickness * (i == 0 ? 4 : 5) - 0.5,
          ]
        )
          CuboidWithIndentsBottom(
            [breakthrough_length, breakthrough_width, cardboard_thickness * 8 + 1],
            anchor=BOTTOM + FRONT + LEFT,
            finger_hole_radius=8,
            finger_holes=[i == 0 ? 4 : 0]
          );
      }
    }
    // Scoring tiles.
    translate([breakthrough_length + 3, 0, 0]) {
      for (i = [0:0]) {
        for (j = [0:2]) {
          translate(
            [
              (scoring_width + 4) * j + 1,
              (scoring_length + 3) * i,
              $inner_height - cardboard_thickness * (j == 0 ? 6 : 5) - 0.5,
            ]
          )
            CuboidWithIndentsBottom(
              [scoring_width, scoring_length, cardboard_thickness * 9 + 1],
              anchor=BOTTOM + FRONT + LEFT,
              finger_holes=[j == 0 ? 2 : 6]
            );
        }
      }
    }
  }
}

module ScoringBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=scoring_box_width,
    length=scoring_box_length,
    height=scoring_box_height,
    material_colour="lightgrey",
    text_str="Scoring"
  );
}

module PlayerBoxInternal(material_colour) {
  MakeBoxWithSlidingLid(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    height=player_box_height,
    material_colour=material_colour
  ) {
    card_height = single_card_thickness * starting_player_card_num + 1;
    translate([0, $inner_length / 2, $inner_height - card_height + 0.01])
      FingerHoleWall(height=card_height, radius=20, spin=270, rounding_radius=5);
    translate([0, 0, $inner_height - card_height])
      cube([$inner_width, $inner_length, card_height + 1]);
    for (i = [0:1]) {
      // research tokens
      translate(
        [
          research_token_length / 2 + 2,
          research_token_diameter / 2 + 4 + (research_token_diameter + 1) * i,
          $inner_height - card_height - research_token_thickness,
        ]
      ) {
        linear_extrude(height=research_token_thickness * 2 + 1) rotate(180) ResearchToken();
      }
      translate(
        [
          research_token_length * 3 / 2 + 4,
          research_token_diameter / 2 + 4 + (research_token_diameter + 1) * i,
          $inner_height - card_height - research_token_thickness,
        ]
      ) {
        linear_extrude(height=research_token_thickness * 2 + 1) ResearchToken();
      }
    }
    for (i = [0:2]) {
      // player discs
      translate(
        [
          $inner_width - player_token_diameter / 2 - 2,
          player_token_diameter / 2 + (player_token_diameter + 5) * i + 2,
          $inner_height - card_height - player_token_thickness * 2,
        ]
      )
        CylinderWithIndents(
          height=player_token_thickness * 2 + 1,
          d=player_token_diameter,
          finger_holes=[180],
          finger_hole_radius=10
        );
      translate(
        [
          $inner_width - player_token_diameter / 2 - 3 - player_token_diameter,
          player_token_diameter / 2 + (player_token_diameter + 5) * i + 2,
          $inner_height - card_height - player_token_thickness * 2,
        ]
      ) CylinderWithIndents(
          height=player_token_thickness * 2 + 1,
          d=player_token_diameter,
          finger_holes=[180],
          finger_hole_radius=10
        );
    }
    translate([10, research_token_diameter * 4.9, $inner_height - card_height - woman_man_player_thickness - 0.5]) {
      children(0);
    }
    translate(
      [
        visitor_blue_width / 2 + 10,
        research_token_diameter * 2 + visitor_green_width / 2 + 4.5,
        $inner_height - card_height - visitor_thickness - 0.5,
      ]
    )
      rotate(90)
        children(1);

    translate([2, 2, $inner_height - research_token_thickness / 2 - card_height])
      RoundedBoxAllSides(
        width=research_token_length * 2 + 4,
        length=$inner_length - 4,
        radius=5,
        height=player_box_height
      );
  }
}

module PlayerBoxYellow() // `make` me
{
  PlayerBoxInternal("yellow") {
    union() {
      linear_extrude(player_token_thickness + 20)
        translate([man_player_height / 2, 0])
          rotate(90)
            ManPlayerToken();
    }
    union() {
      VisitorTokenYellow();
    }
  }
}

module PlayerBoxBlue() // `make` me
{
  PlayerBoxInternal("blue") {
    union() {
      linear_extrude(player_token_thickness + 20)
        translate([man_player_height / 2, 0])
          rotate(90)
            ManPlayerToken();
    }
    union() {
      translate([0, -5, 0])
        VisitorTokenBlue();
    }
  }
}

module PlayerBoxGreen() // `make` me
{
  PlayerBoxInternal("green") {
    union() {
      linear_extrude(player_token_thickness + 20)
        translate([woman_player_height / 2, 0])
          rotate(90)
            WomanPlayerToken();
    }
    union() {
      translate([2, -14, 0])
        rotate(90)
          VisitorTokenGreen();
    }
  }
}

module PlayerBoxPurple() // `make` me
{
  PlayerBoxInternal("purple") {
    union() {
      linear_extrude(player_token_thickness + 20)
        translate([woman_player_height / 2, 0])
          rotate(90)
            WomanPlayerToken();
    }
    union() {
      translate([0, -5, 0])
        VisitorTokenPurple();
    }
  }
}

module PlayerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true,
    material_colour="blue",
    text_str="Player"
  );
}

module ObjectiveBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=objective_box_width,
    length=objective_box_length,
    height=objective_box_height,
    material_colour="orange",
    lid_on_length=true
  ) {
    for (i = [0:2]) {
      for (j = [0:1]) {
        // objectives
        translate(
          [
            (objective_width + 19) * j,
            1 + (objective_length + 1.5) * i,
            $inner_height - objective_width,
          ]
        )
          CuboidWithIndentsBottom(
            [cardboard_thickness * 9 + 0.5, objective_length, objective_width + 1],
            anchor=BOTTOM + FRONT + LEFT,
            finger_holes=[]
          );
      }
    }
    translate(
      [0, $inner_length / 2, $inner_height - objective_box_height + 0.01]
    )
      FingerHoleBase(radius=10, height=objective_box_height, spin=270);
    translate(
      [0, objective_length / 2, $inner_height - objective_box_height + 0.01]
    )
      FingerHoleBase(radius=10, height=objective_box_height, spin=270);
    translate(
      [0, $inner_length - objective_length / 2, $inner_height - objective_box_height + 0.01]
    )
      FingerHoleBase(radius=10, height=objective_box_height, spin=270);
  }
}

module FirstPlayerBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=first_player_box_width,
    length=first_player_box_length,
    height=first_player_box_height
  ) {
    translate([$inner_width / 2, $inner_length / 2, $inner_height - first_player_thickness - 0.5])
      linear_extrude(height=first_player_thickness + 1)
        rotate(90)
          FirstPlayerToken();
    translate([0, 0, $inner_height - first_player_thickness / 2])
      RoundedBoxAllSides(width=$inner_width - 2, length=$inner_length - 2, height=20, radius=5);
  }
}

module FirstPlayerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=first_player_box_width,
    length=first_player_box_length,
    text_str="First"
  );
}

module ObjectiveBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=objective_box_width,
    length=objective_box_length,
    material_colour="orange",
    "Objective",
    lid_on_length=true
  );
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
            1 + (alternative_objective_length + 1.5) * i + 3.5,
            $inner_height - cardboard_thickness * 5,
          ]
        )
          CuboidWithIndentsBottom(
            [alternative_objective_width, alternative_objective_length, alternative_objective_box_height],
            anchor=BOTTOM + FRONT + LEFT,
            finger_holes=[j % 2 == 0 ? 2 : 6]
          );
      }
    }
  }
}

module AlternativeObjectiveBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=alternative_objective_box_width,
    length=alternative_objective_box_length,
    height=alternative_objective_box_height,
    material_colour="purple",
    text_str="Alt Objective"
  );
}

module DiceBox() // `make` me
{
  MakeBoxWithCapLid(
    width=dice_box_width,
    length=dice_box_length,
    height=dice_box_height,
    material_colour="green"
  ) {
    translate([1.5, 0.5, 0]) {
      cube([dice_thickness * 6, dice_thickness * 8, dice_thickness]);
      cube([dice_thickness * 2, dice_thickness * 9, dice_thickness]);
    }
    translate([$inner_width / 2, $inner_length / 2, $inner_height - 4])
      cuboid([$inner_width - 2, $inner_length - 2, 20], rounding=4, anchor=BOTTOM);
  }
}

module DiceBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=dice_box_width,
    length=dice_box_length,
    height=dice_box_height,
    material_colour="green",
    text_str="Dice"
  );
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

module ScorePadBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=score_pad_box_width,
    length=score_pad_box_length,
    material_colour="white",
    text_str="Score Pad"
  );
}

module GearBox(top_box = false) // `make` me
{
  MakeBoxWithCapLid(
    width=cog_box_width,
    length=cog_box_length,
    height=cog_box_height,
    material_colour="blue"
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
          CylinderWithIndents(
            d=gear_width, h=cog_box_height, anchor=BOTTOM,
            finger_holes=[0], finger_hole_radius=10
          );
        }
      }
    translate(
      [
        $inner_width - gear_width / 2 - 2,
        $inner_length / 2,
        $inner_height - gear_thickness * (top_box ? 2 : 3),
      ]
    ) {
      CylinderWithIndents(
        d=gear_width, h=cog_box_height, anchor=BOTTOM,
        finger_holes=[180], finger_hole_radius=10
      );
    }
  }
}

module GearBoxTop() // `make` me
{
  GearBox(top_box=true);
}

module GearBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=cog_box_width,
    length=cog_box_length,
    height=cog_box_height,
    material_colour="blue",
    text_str="Addition"
  );
}

module GearBoxTopLid() // `make` me
{
  CapBoxLidWithLabel(
    width=cog_box_width,
    length=cog_box_length,
    height=cog_box_height,
    material_colour="blue",
    text_str="Multiplier"
  );
}

module ResourceBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    material_colour="gold"
  ) {
    RoundedBoxAllSides(
      width=$inner_width,
      length=$inner_length, height=resource_box_height, radius=5
    );
  }
}

module ResourceBoxBrassLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=resource_box_width,
    length=resource_box_length,
    text_str="Brass"
  );
}

module ResourceBoxCoalLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=resource_box_width,
    length=resource_box_length,
    text_str="Coal"
  );
}

module MoneyBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=money_box_width,
    length=money_box_length,
    height=money_box_height,
    material_colour="silver"
  ) {
    RoundedBoxAllSides(
      width=$inner_width,
      length=$inner_length, height=money_box_height, radius=5,
    );
  }
}

module MoneyBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=money_box_width,
    length=money_box_length,
    text_str="Money"
  );
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
  //translate([0, box_length - great_exhibition_board, box_height - great_exhibition_board_thickness])
  // cube([box_width, great_exhibition_board, great_exhibition_board_thickness]);
  // AssignmentCardBox();
  translate([0, 0, board_thickness]) {
    translate([0, box_length - solo_reward_length, 0]) {
      cube([solo_reward_width_thin, solo_reward_length, solo_reward_thickness]);
      translate([0, solo_reward_length - solo_reward_length_thin, 0])
        cube([solo_reward_width, solo_reward_length_thin, solo_reward_thickness]);
    }
    translate([box_width - assignment_tiles_width, 0])
      cube([assignment_tiles_width, assignment_tiles_length, assignment_tiles_thickness]);
    translate([card_box_width, card_box_length, 0])
      OtherCardBox();
    translate([card_box_width, card_box_length, other_card_box_height])
      TierCardBox();
    translate([0, 0, 0])
      PlayerBoxYellow();
    translate([card_box_width, 0, 0])
      PlayerBoxBlue();
    translate([0, 0, player_box_height])
      PlayerBoxGreen();
    translate([card_box_width, 0, player_box_height])
      PlayerBoxPurple();
    translate([0, 0, player_box_height * 2])
      SteamInnovationBox();
    translate([0, steam_box_length, player_box_height * 2])
      ScoringBox();
    translate([card_box_width, 0, player_box_height * 2])
      MoneyBox();
    translate([solo_reward_width_thin, card_box_length, 0])
      BookBox();
    translate([solo_reward_width_thin, card_box_length + book_box_length, 0])
      AssignmentBox();
    translate([0, card_box_length, book_box_height + dice_box_height])
      AlternativeObjectiveBox();
    translate([0, card_box_length, book_box_height])
      DiceBox();
    translate([0, card_box_length + dice_box_length, book_box_height])
      FirstPlayerBox();

    translate([0, card_box_length + alternative_objective_box_length, book_box_height])
      AssignmentCardBox();
    translate([card_box_width, card_box_length * 2, 0])
      ScorePadBox();
    translate([card_box_width + program_box_width, card_box_length * 2, score_pad_box_height])
      ResourceBox();
    translate([card_box_width + program_box_width, card_box_length * 2, score_pad_box_height + resource_box_height])
      ResourceBox();
    translate([card_box_width, card_box_length * 2, score_pad_box_height])
      ProgramBox();
    translate([card_box_width, card_box_length * 2 + program_box_length, score_pad_box_height])
      UniversityBox();
    for (i = [0:2]) {
      translate([card_box_width, card_box_length * 2 + score_pad_box_length, cog_box_height * i])
        GearBox();
    }
    translate([card_box_width * 2, 0, assignment_tiles_thickness])
      SpacerSide();
    translate([card_box_width * 2, spacer_side_box_length, assignment_tiles_thickness])
      ObjectiveBox();
  }
}

if (FROM_MAKE != 1) {
  SteamInnovationBox();
}
