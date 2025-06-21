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

box_length = 285;
box_width = 285;
box_height = 73;

default_lid_shape_type = SHAPE_TYPE_ESCHER_LIZARD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 10;

board_thickness = 20;
board_width = 255;

default_wall_thickness = 3;
default_lid_thickness = 3;
default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

tile_thickness = 2;

spinner = 132;
spinner_base = 25;
spinner_thickness = 9;

card_width = 66;
card_length = 91;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

nest_width = 45;
nest_total_length = 180;

player_cube = 8;
player_token_diameter = 10;

other_token_thickness = 6.5;
cresent_diameter = 16;
leaf_width = 9;
leaf_length = 28;
leaf_stem = 5;
leaf_stem_width = 2;
die_size = 16;
coin_diamter = 25.5;
coin_thickness = 3;

player_box_width = default_wall_thickness * 4 + nest_width;
player_box_length = (box_length - 2) / 4;
player_box_height = (box_height - board_thickness - 1) / 3;

resource_box_width = player_box_width;
resource_box_length = player_box_length;
resource_box_height = player_box_height;

nest_box_length = box_length - 2;
nest_box_width = nest_width + default_floor_thickness + default_lid_thickness + 2;
nest_box_height = box_height - board_thickness - 1;

spinner_box_width = box_width - player_box_width - nest_box_width - 2;
spinner_box_length = box_length - 2;
spinner_box_height = spinner_thickness + default_floor_thickness;

card_box_length = card_length + 1 + default_wall_thickness * 2;
card_box_width = card_width + 1 + default_wall_thickness * 2;
card_box_height = box_height - spinner_box_height - board_thickness - 1;

starting_card_box_height = single_card_thickness * 14 + default_lid_thickness + default_floor_thickness + 1;
achievment_card_box_height = single_card_thickness * 13 + default_lid_thickness + default_floor_thickness + 1;
changing_condition_card_box_height = single_card_thickness * 11 + default_lid_thickness + default_floor_thickness + 1;
legend_card_box_height = single_card_thickness * 9 + default_lid_thickness + default_floor_thickness + 1;
plant_animal_extra_card_box_height = card_box_height - legend_card_box_height;

extra_bits_box_height = board_thickness;
extra_bits_box_width = box_width - board_width - 1;
extra_bits_box_length = box_length - 1;

spacer_side_width = box_width - nest_box_width - player_box_width - 2;
spacer_side_length = box_length - card_box_length * 2 - 2;
spacer_side_height = card_box_height;

spacer_front_width = box_width - nest_box_width - player_box_width - card_box_width * 2;
spacer_front_length = box_length - spacer_side_length - 2;
spacer_front_height = card_box_height;

module PlayerBox() // `make` me
{
  MakeBoxWithCapLid(width=player_box_width, length=player_box_length, height=player_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=player_box_height, radius=5);
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_height,
    text_str="Player", label_rotated=true
  );
}

module ResourceBox() // `make` me
{
  MakeBoxWithCapLid(width=resource_box_width, length=resource_box_length, height=resource_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
  }
}

module ResourceBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height,
    text_str="Mouse", label_rotated=true
  );
  translate([resource_box_width + 10, 0, 0]) {
    CapBoxLidWithLabel(
      width=resource_box_width, length=resource_box_length, height=resource_box_height,
      text_str="Sun", label_rotated=true
    );
    translate([resource_box_width + 10, 0, 0]) {
      CapBoxLidWithLabel(
        width=resource_box_width, length=resource_box_length, height=resource_box_height,
        text_str="Fish", label_rotated=true
      );
      translate([resource_box_width + 10, 0, 0]) {
        CapBoxLidWithLabel(
          width=resource_box_width, length=resource_box_length,
          height=resource_box_height, text_str="Leaf",
          label_rotated=true
        );
        translate([resource_box_width + 10, 0, 0]) {
          CapBoxLidWithLabel(
            width=resource_box_width, length=resource_box_length,
            height=resource_box_height,
            text_str="Spider", label_rotated=true
          );
          translate([resource_box_width + 10, 0, 0]) {
            CapBoxLidWithLabel(
              width=resource_box_width, length=resource_box_length,
              height=resource_box_height,
              text_str="Fruit", label_rotated=true
            );
          }
        }
      }
    }
  }
}

module NestBox() // `make` me
{
  MakeBoxWithCapLid(width=nest_box_width, length=nest_box_length, height=nest_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=nest_box_height, radius=5);
  }
}

module NestBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=nest_box_width, length=nest_box_length, height=nest_box_height,
    text_str="Nests", label_rotated=true
  );
}

module ExtraBitsBox() // `make` me
{
  MakeBoxWithCapLid(
    width=extra_bits_box_width, length=extra_bits_box_length, height=extra_bits_box_height,
    last_child_positive=default_label_solid_background
  ) {
    // Phase and year token.
    translate([$inner_width / 2, 15, $inner_height - 9.5]) {
      cuboid([8, 8, 10], anchor=BOTTOM);
      translate([0, 7.5, 4]) ycyl(d=30, h=40, rounding=10, anchor=BOTTOM);
    }
    translate([$inner_width / 2, 30, $inner_height - 9.5]) {
      cuboid([8, 8, 10], anchor=BOTTOM);
      // translate([ 0, 0, 4 ]) sphere(d = 20, anchor = BOTTOM);
    }

    // Coin.
    translate([$inner_width / 2, $inner_length / 2, $inner_height - coin_thickness - 0.5]) {
      cyl(d=coin_diamter, h=coin_thickness + 1, anchor=BOTTOM);
      translate([0, coin_diamter / 2, 0]) sphere(d=30, anchor=BOTTOM);
      translate([0, -coin_diamter / 2, 0]) sphere(d=30, anchor=BOTTOM);
    }

    // Die.
    translate([$inner_width / 2, $inner_length - 30, $inner_height - die_size - 0.5]) {
      cuboid([die_size, die_size, die_size + 4], anchor=BOTTOM, rounding=1);
      translate([0, 0, die_size / 2]) ycyl(d=25, h=40, rounding=10, anchor=BOTTOM);
    }

    // Text.
    translate([$inner_width / 2, $inner_length / 4 + 8, $inner_height - 0.4]) linear_extrude(height=0.21)
        rotate(90) text("Biome", halign="center", valign="center", size=15);

    
    // season token
    translate([$inner_width / 2, $inner_length / 2 + 35, 0]) {
      translate([0, 0, $inner_height - other_token_thickness - 0.5]) {
        difference() {
          cyl(d=cresent_diameter, h=other_token_thickness + 2, anchor=BOTTOM);
          translate([0, -7, 0]) cyl(d=cresent_diameter, h=other_token_thickness + 2, anchor=BOTTOM);
        }
      }
      translate([0, 20, $inner_height - other_token_thickness / 2])
        ycyl(d=40, h=65, rounding=10, anchor=BOTTOM);

      // start player token.
      translate([0, 25, $inner_height - other_token_thickness - 0.5]) {
        linear_extrude(height=other_token_thickness + 1) resize([leaf_width + 2, leaf_length - leaf_stem])
            circle(d=leaf_length - leaf_stem);
        translate([0, (leaf_length - leaf_stem) / 2 + leaf_stem / 2 - 0.5, 0]) rotate(-10)
            cuboid([leaf_stem_width + 2, leaf_stem + 2, other_token_thickness + 1], anchor=BOTTOM);
      }
    }

    if (default_label_solid_background) {
      color("black") translate([$inner_width / 2, $inner_length / 4 + 8, $inner_height - 0.4])
          linear_extrude(height=0.21) rotate(90) text("Biome", halign="center", valign="center", size=15);
    }
  }
}

module ExtraBitsBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=extra_bits_box_width, length=extra_bits_box_length, height=extra_bits_box_height,
    text_str="Biome", label_rotated=true
  );
}

module SpinnerHolder() // `make` me
{
  color(default_material_colour) difference() {
      cuboid(
        [spinner_box_width, spinner_box_length, spinner_box_height], rounding=2,
        anchor=BOTTOM + FRONT + LEFT
      );
      translate([spinner_box_width / 2, spinner_box_length / 2, default_floor_thickness + tile_thickness * 2])
        cyl(d=spinner, h=spinner_thickness - tile_thickness * 2 + 0.1, anchor=BOTTOM);
      translate([spinner_box_width / 2, spinner_box_length / 2, default_floor_thickness])
        cyl(d=spinner_base, h=spinner_thickness - tile_thickness * 2 + 0.1, anchor=BOTTOM);
    }
}
module StartingCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=starting_card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module StartingCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Starting",
  );
}

module AchievmentCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=achievment_card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module AchievementCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Achievement",
  );
}

module ChangingConditionCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=changing_condition_card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module ChangingConditionCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Change",
  );
}

module LegendCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=legend_card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module LegendCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Legend",
  );
}

module PlantAnimalCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module PlantAnimalCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Play",
  );
}

module PlantAnimalExtraCardBox() // `make` me
{
  MakeBoxWithSlidingLid(width=card_box_width, length=card_box_length, height=plant_animal_extra_card_box_height) {
    cube([$inner_width, $inner_length, $inner_height + default_lid_thickness]);
  }
}

module SpacerSide() // `make` me
{
  color(default_material_colour) {
    difference() {
      cuboid(
        [spacer_side_width, spacer_side_length, spacer_side_height], anchor=BOTTOM + LEFT + FRONT,
        rounding=2
      );
      translate([default_wall_thickness, default_wall_thickness, default_floor_thickness]) {
        cube(
          [
            spacer_side_width - default_wall_thickness * 2,
            spacer_side_length - default_wall_thickness * 2,
            spacer_side_height,
          ]
        );
      }
    }
  }
}

module SpacerFront() // `make` me
{
  color(default_material_colour) {
    difference() {
      cuboid(
        [spacer_front_width, spacer_front_length, spacer_front_height], anchor=BOTTOM + LEFT + FRONT,
        rounding=2
      );
      translate([default_wall_thickness, default_wall_thickness, default_floor_thickness]) {
        cube(
          [
            spacer_front_width - default_wall_thickness * 2,
            spacer_front_length - default_wall_thickness * 2,
            spacer_front_height,
          ]
        );
      }
    }
  }
}

module BoxLayout() {
  //    cube([ box_width, box_length, board_thickness ]);
  cube([1, box_length, box_height]);
  //  translate([ 0, 0, board_thickness ])
  {
    PlayerBox();
    translate([0, player_box_length, 0]) PlayerBox();
    translate([0, player_box_length * 2, 0]) PlayerBox();
    translate([0, player_box_length * 3, 0]) PlayerBox();
    translate([0, 0, player_box_height]) ResourceBox();
    translate([0, player_box_length, player_box_height]) ResourceBox();
    translate([0, player_box_length * 2, player_box_height]) ResourceBox();
    translate([0, player_box_length * 3, player_box_height]) ResourceBox();
    translate([0, 0, player_box_height * 2]) ResourceBox();
    translate([0, player_box_length, player_box_height * 2]) ResourceBox();
    translate([0, player_box_length * 2, player_box_height * 2]) ResourceBox();
    translate([0, player_box_length * 3, player_box_height * 2]) ResourceBox();
    translate([player_box_width, 0, 0]) NestBox();
    translate([player_box_width + nest_box_width, 0, card_box_height]) SpinnerHolder();
    translate(
      [
        player_box_width + nest_box_width,
        0,
      ]
    ) PlantAnimalCardBox();
    translate(
      [
        player_box_width + nest_box_width + card_box_width,
        0,
      ]
    ) PlantAnimalCardBox();
    translate([player_box_width + nest_box_width, card_box_length, 0]) StartingCardBox();
    translate([player_box_width + nest_box_width, card_box_length, starting_card_box_height]) AchievmentCardBox();
    translate(
      [
        player_box_width + nest_box_width,
        card_box_length,
        starting_card_box_height + achievment_card_box_height,
      ]
    ) ChangingConditionCardBox();
    translate([player_box_width + nest_box_width + card_box_width, card_box_length, 0]) LegendCardBox();
    translate([player_box_width + nest_box_width + card_box_width, card_box_length, legend_card_box_height])
      PlantAnimalExtraCardBox();
    translate([player_box_width + nest_box_width, card_box_length * 2, 0]) SpacerSide();
    translate([player_box_width + nest_box_width + card_box_width * 2, 0, 0]) SpacerFront();
    translate([board_width, 0, card_box_height + spinner_box_height]) ExtraBitsBox();
  }
  translate([0, 0, box_height - board_thickness - 1]) cube([board_width, box_length, board_thickness]);
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
