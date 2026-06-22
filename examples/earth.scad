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

// This also includes the boxes for the abundance expansion.
// However the animal kingdom one will not fit in the box.

include <boardgame_toolkit.scad>

box_width = 288;
box_length = 288;
box_height = 72;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMELESS : LABEL_TYPE_FRAMED;
default_lid_shape_type = SHAPE_TYPE_VORONOI;

player_board_width = 242;
player_board_length = 288;
player_board_thickness = 2.1;
player_board_count = 6;
adundance_middle_board_thickness = 2.1;

abundance_board_width = 57;
abundance_board_length = 241;
abundance_board_thickness = 2.1;
abundance_board_count = 6;

middle_board_width = 222;
middle_board_length = 274;
middle_board_thickness = 2.1;

flora_cards = 179;
terrain_cards = 66;
event_cards = 38;
earth_cards = flora_cards + terrain_cards + event_cards;

abundance_earth_cards = 70;
abundance_other_cards = 2 + 2 + 3 + 3;

ecosystem_cards = 32;
fauna_cards = 23;
island_cards = 10;
climate_cards = 10;
solo_cards = 6;
season_cards = 12;

leaf_width = 13;
leaf_length = 17.5;
leaf_thickness = 3;
leaf_number = 5;

readyness_token_width = 36.5;
readyness_token_length = 59;
readyness_token_thickness = 5;
readyness_token_number = 10;

start_disk_diameter = 41;
start_disk_thickness = readyness_token_thickness;
start_disk_number = 1;

active_player_token_width = 36;
active_player_token_length = 59;
active_player_token_thickness = 5;
active_player_token_number = 1;

score_pad_width = 81;
score_pad_length = 99;
score_pad_thickness = 5;
score_pad_number = 2;

sprout_cube_width = 8;
sprout_cube_number = 145 + 50;

score_override_marker_width = 16.5;
score_override_marker_length = 18.5;
score_overide_thickness = 3;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;
card_size = MakeCardSize(
  length=93,
  width=62,
  single_card_thickness=single_card_thickness
);
animal_card_size = MakeCardSize(
  length=123,
  width=72,
  single_card_thickness=single_card_thickness
);

card_box_width = default_wall_thickness * 2 + card_size.width;
card_box_length = default_wall_thickness * 2 + card_size.length;
card_box_height = box_height - player_board_thickness * player_board_count - middle_board_thickness - adundance_middle_board_thickness;
ecosystem_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * ecosystem_cards + 1;
fauna_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * fauna_cards + 1;
island_cards_height = card_box_height - ecosystem_cards_height - fauna_cards_height;
climate_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * climate_cards + 1;
solo_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * solo_cards + 1;
season_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * season_cards + 1;
abundance_other_cards_height = default_floor_thickness + default_lid_thickness + single_card_thickness * abundance_other_cards + 1;
start_box_height = card_box_height - climate_cards_height - solo_cards_height - season_cards_height - abundance_other_cards_height;

player_box_width = card_box_width;
player_box_length = card_box_length;
player_box_height = card_box_height / 6;

score_pad_box_width = score_pad_length + default_wall_thickness * 4 + 7.4;
score_pad_box_length = box_length - card_box_length * 2 - 1;
score_pad_box_height = score_pad_thickness + default_floor_thickness;

canopy_box_width = box_width - abundance_board_thickness * abundance_board_count - 0.5 - score_pad_box_width;
canopy_box_length = score_pad_box_length;
canopy_box_height = card_box_height;

compost_box_width = box_width - player_board_width;
compost_box_length = abundance_board_length - 0.5;
compost_box_height = box_height - abundance_board_width;

sprout_box_width = score_pad_box_width;
sprout_box_length = canopy_box_length;
sprout_box_height = (card_box_height - score_pad_box_height - compost_box_height);

seed_box_length = box_length - abundance_board_length - 1;
seed_box_width = box_width - card_box_width * 4;
seed_box_height = box_height;

player_colours = ["red", "green", "yellow", "blue", "purple", "pink"];

module EarthCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, card_box_height],
  ) {
    cube([card_size.width, card_size.length, card_box_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=card_box_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module EarthCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, card_box_height],
    text_str="Earth"
  );
}

module EcosystemCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, ecosystem_cards_height],
  ) {
    cube([card_size.width, card_size.length, ecosystem_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=ecosystem_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module EcosystemCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, ecosystem_cards_height],
    text_str="Ecosystem"
  );
}

module FaunaCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, fauna_cards_height],
  ) {
    cube([card_size.width, card_size.length, fauna_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=fauna_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module FaunaCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, fauna_cards_height],
    text_str="Fauna"
  );
}

module IslandCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, island_cards_height],
  ) {
    cube([card_size.width, card_size.length, island_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=island_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module IslandCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, island_cards_height],
    text_str="Island"
  );
}

module ClimateCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, climate_cards_height],
  ) {
    cube([card_size.width, card_size.length, climate_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=climate_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module ClimateCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, climate_cards_height],
    text_str="Climate"
  );
}

module SoloCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, solo_cards_height],
  ) {
    cube([card_size.width, card_size.length, solo_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=solo_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module SoloCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, solo_cards_height],
    text_str="Solo"
  );
}

module SeasonCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, season_cards_height],
  ) {
    cube([card_size.width, card_size.length, season_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=season_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module SeasonCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, season_cards_height],
    text_str="Season"
  );
}

module AbundanceOtherCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, abundance_other_cards_height],
  ) {
    cube([card_size.width, card_size.length, abundance_other_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=abundance_other_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module AbundanceOtherCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, abundance_other_cards_height],
    text_str="Abundance"
  );
}

module LeafTeardrop2D() {
  tip_d = 0.5;
  translate([0, -(leaf_length / 2 - leaf_width / 2)]) {
    hull() {
      circle(d=leaf_width, $fn=64);
      translate([0, leaf_length - leaf_width / 2 - tip_d / 2])
        circle(d=tip_d, $fn=16);
    }
  }
}

module LeafTeardropWithFingerGrabs(height) {
  finger_d = 16;
  y_center = -(leaf_length / 2 - leaf_width / 2);
  union() {
    linear_extrude(height=height, convexity=10)
      LeafTeardrop2D();
    // Left finger grab
    back(leaf_length / 2)
      cyl(d=finger_d, anchor=BOTTOM, h=finger_d * 5, rounding=finger_d / 2);
  }
}

module StartBox() // `make` me
{
  cols = 3;
  rows = 4;
  MakeBoxWithCapLid(
    [card_box_width, card_box_length, start_box_height],
    positive_negative_children=[1]
  ) {
    union() {
      back(start_disk_diameter / 2 + 2)
        right($inner_width / 2 + 7)
          up($inner_height - start_disk_thickness - 0.5)
            CylinderWithIndents(
              d=start_disk_diameter, h=start_disk_thickness + 0.5001,
              anchor=BOTTOM,
              finger_hole_radius=11.5,
              finger_holes=[45, 215]
            ) {
              edge_profile([TOP]) xflip()
                  mask2d_roundover(default_wall_thickness / 4);
            }
      up($inner_height - readyness_token_thickness - 0.5)
        right($inner_width / 2)
          back($inner_length - readyness_token_width / 2 - 2)
            CuboidWithIndentsBottom(
              [readyness_token_length, readyness_token_width, readyness_token_thickness + 0.5001], anchor=BOTTOM,
              finger_holes=[0],
              finger_hole_radius=15,
              rounding=1,
              edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
            ) {
              edge_profile(TOP) xflip()
                  mask2d_roundover(default_wall_thickness / 4);
              corner_profile(TOP, r=default_wall_thickness / 8) xflip()
                  mask2d_roundover(default_wall_thickness / 4);
            }

      up($inner_height - score_overide_thickness - 0.5)
        back(start_disk_diameter)
          right(score_override_marker_length / 2 + 2)
            CuboidWithIndentsBottom(
              [score_override_marker_width, score_override_marker_length, score_overide_thickness + 0.5001],
              anchor=BOTTOM,
              finger_hole_radius=9,
              finger_holes=[0],
              rounding=1,
              edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
            ) {
              edge_profile(TOP) xflip()
                  mask2d_roundover(default_wall_thickness / 4);
              corner_profile(TOP, r=default_wall_thickness / 8) xflip()
                  mask2d_roundover(default_wall_thickness / 4);
            }
    }
    union() {
      up($inner_height - score_overide_thickness - 0.7)
        back(start_disk_diameter)
          right(score_override_marker_length / 2 + 2)
            linear_extrude(h=0.201)
              text("11", valign="center", halign="center");
      up($inner_height - readyness_token_thickness - 0.7)
        right($inner_width / 2)
          back($inner_length - readyness_token_width / 2 - 2)
            linear_extrude(h=0.201)
              text("Active", valign="center", halign="center");
      back(start_disk_diameter / 2 + 2)
        right($inner_width / 2 + 7)
          up($inner_height - start_disk_thickness - 0.7)
            linear_extrude(h=0.201)
              text("Start", valign="center", halign="center");
    }
  }
}

module StartBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[card_box_width, card_box_length, start_box_height],
    text_str="Start"
  );
}

module PlayerBox(colour = "green") // `make` me
{
  MakeBoxWithSlipoverLid(
    [player_box_width, player_box_length, player_box_height],
    material_colour=colour,
    positive_negative_children=[1],
    foot=2
  ) {
    right($inner_width / 2) {
      up($inner_height - readyness_token_thickness - 0.3)
        back(2) {
          cuboid(
            [readyness_token_length, readyness_token_width, readyness_token_thickness + 1],
            anchor=FRONT + BOTTOM
          );
          right(0)
            back(readyness_token_width)
              cyl(d=23, h=player_box_height * 3, rounding=6.5, anchor=BOTTOM);
        }
      back(readyness_token_width + leaf_length + 2.5)
        right(1.5)
          up($inner_height - leaf_thickness - 0.3) {
            for (i = [0:2]) {
              right((leaf_width + 1) * (i - 1)) {
                for (j = [0:1]) {
                  if (j != 0 || i != 1) {
                    back((leaf_length + 9.5) * (j - ( (i % 2) * 0.5)))
                      rotate(90)
                        LeafTeardropWithFingerGrabs(leaf_thickness + 1);
                  }
                }
              }
            }
          }
    }
    right($inner_width / 2) {
      up($inner_height - readyness_token_thickness - 0.5)
        back(2 + readyness_token_width / 2)
          linear_extrude(h=0.201)
            text("Ready", valign="center", halign="center");
    }
  }
}

module PlayerBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    size=[player_box_width, player_box_length, player_box_height],
    text_str="Player",
    foot=2
  );
}

module CanopyBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [canopy_box_width, canopy_box_length, canopy_box_height],
    material_colour="cornsilk"
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[canopy_box_width, canopy_box_length, canopy_box_height]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, canopy_box_height],
          radius=10
        );
    }
  }
}

module CanopyBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[canopy_box_width, canopy_box_length, canopy_box_height],
    text_str="Canopy",
    material_colour="cornsilk"
  );
}

module SeedBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [seed_box_length, seed_box_height, seed_box_width],
    material_colour="brown",
    anchor=BACK + LEFT + TOP,
    spin=90,
    orient=LEFT
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[seed_box_length, seed_box_height, seed_box_width]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, seed_box_width],
          radius=5
        );
    }
  }
}

module SeedBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    [seed_box_length, seed_box_height, seed_box_width],
    text_str="Compost",
    material_colour="cornsilk"
  );
}

module CompostBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [compost_box_width, compost_box_length, compost_box_height],
    material_colour="black"
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[compost_box_width, compost_box_length, compost_box_height]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, compost_box_height],
          radius=10
        );
    }
  }
}

module CompostBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[compost_box_width, compost_box_length, compost_box_height],
    text_str="Compost",
    material_colour="black"
  );
}

module SproutBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [sprout_box_width, sprout_box_length, sprout_box_height],
    material_colour="green",
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[sprout_box_width, sprout_box_length, sprout_box_height]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, sprout_box_height],
          radius=10
        );
    }
  }
}

module SproutBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[sprout_box_width, sprout_box_length, sprout_box_height],
    text_str="Sprouts",
    material_colour="green"
  );
}

module ScorePadBox() // `make` me
{
  MakeBoxWithNoLid(
    [score_pad_box_width, score_pad_box_length, score_pad_box_height],
    material_colour="white",
    hollow=true
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([box_width, 1, box_height]);
  }
  if (layout < 1) {
    up(box_height)
      cuboid([player_board_width, player_board_length, player_board_thickness * player_board_count + adundance_middle_board_thickness], anchor=TOP + LEFT + FRONT);
    up(card_box_height)
      cuboid([middle_board_width, middle_board_length, middle_board_thickness], anchor=BOTTOM + LEFT + FRONT);
  }
  for (i = [0:3]) {
    right(i * card_box_width)
      EarthCardBox();
  }
  right(4 * card_box_width) {
    SeedBox();
  }
  right(box_width - abundance_board_thickness * abundance_board_count)
    back(seed_box_length) {
      for (i = [0:abundance_board_count - 1]) {
        color(player_colours[i])
          right(abundance_board_thickness * i)
            cuboid([abundance_board_thickness, abundance_board_length, abundance_board_width], anchor=BOTTOM + LEFT + FRONT);
      }
    }
  right(player_board_width)
    back(seed_box_length) {
      if (layout < 2) {
        up(abundance_board_width)
          CompostBox();
      }
    }

  back(card_box_length) {
    EcosystemCardBox();
    if (layout < 3) {
      up(ecosystem_cards_height) {
        FaunaCardBox();
        if (layout < 2) {
          up(fauna_cards_height) {
            IslandCardBox();
          }
        }
      }
    }
    right(card_box_width) {
      ClimateCardBox();
      if (layout < 4) {
        up(climate_cards_height) {
          SoloCardBox();
          up(solo_cards_height) {
            SeasonCardBox();
            if (layout < 3) {
              up(season_cards_height) {
                AbundanceOtherCardBox();
                if (layout < 2) {
                  up(abundance_other_cards_height) {
                    StartBox();
                  }
                }
              }
            }
          }
        }
      }
      right(card_box_width) {
        EarthCardBox();
        right(card_box_width) {
          for (i = [0:5])
            up(player_box_height * i)
              PlayerBox(colour=player_colours[i]);
        }
      }
    }
    back(card_box_length) {
      CanopyBox();
      right(canopy_box_width) {
        ScorePadBox();
        if (layout < 3) {
          up(score_pad_box_height)
            SproutBox();
        }
      }
    }
  }
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

function round_to_2(val) = round(val * 100) / 100;

if (FROM_MAKE != 1) {

  BoxLayout();
  //SheepTesselation(20, 0,0, 1);
  //PlayerBoxLid();
  /*
  bez = bezier_curve(
    flatten(
      [
        bez_begin([0, 0], 0, 0.4),
        bez_tang([0.4, 0.0], 0, 0.1, 0.5),
        bez_tang([0.6, -0.04], 270, 0.1, 0.5),
        bez_tang([0.8, -0.3], 0, 0.5, 0.2),
        bez_tang([0.9, -0.3], 20, 0.5, 0.2),
        bez_end([1, 0], 300, 0.3),
      ]
    ), 20
  ) * 100;
  echo(bez);
  color("blue")
    stroke(bez);
  line3 = [
    [0, 0],
    [0.07, 0],
    [0.13, 0],
    [0.19, -0.03],
    [0.36, -0.08],
    [0.29, -0.28],
    [0.35, -0.39],
    [0.44, -0.56],
    [0.67, -0.53],
    [0.83, -0.45],
    [0.91, -0.42],
    [0.98, -0.37],
    [1.03, -0.3],
    [1.06, -0.26],
    [1.07, -0.22],
    [1.06, -0.17],
    [1.06, -0.11],
    [1.03, -0.06],
    [1, 0],
  ];
  color("green")
    stroke(line3 * 100);

  /*
  bez = [
    [0.0, 101.46],
    [13.6, 101.16999999999999],
    [25.87, 100.63],
    [38.41, 96.16999999999999],
    [70.52, 84.74999999999999],
    [57.809999999999995, 45.569999999999986],
    [69.03, 24.389999999999986],
    [86.91, -9.360000000000014],
    [132.09, -2.5700000000000145],
    [163.84, 11.949999999999987],
    [179.71, 19.209999999999987],
    [193.66, 28.86999999999999],
    [204.05, 42.789999999999985],
    [209.60000000000002, 50.23999999999999],
    [211.97, 58.569999999999986],
    [210.58, 67.78999999999999],
    [208.79000000000002, 79.61999999999999],
    [204.3, 90.55999999999999],
    [197.77, 100.85999999999999],
  ];
  //max_y = max([for (i = bez) i[0]]);
  max_y = 197.77;
  min_y = min([for (i = bez) i[0]]);
  ratio = 1 / max_y;
  new_bez = rot(a=0, p=[for (i = bez) [i[0], i[1] - 101.46] * ratio]);

  // echo([for (i = new_bez) [round_to_2(i[0]), round_to_2(i[1])]]);
  // color("blue")
  //  stroke(new_bez * 100);
  //echo(PentagonTesselation("R2", 30, 0,0, 2));
  line3 = [
    [0, 0],
    [0.01, -0.04],
    [0.02, -0.08],
    [0.05, -0.11],
    [0.09, -0.18],
    [0.18, -0.18],
    [0.25, -0.14],
    [0.33, -0.1],
    [0.41, -0.07],
    [0.49, -0.07],
    [0.56, -0.11],
    [0.68, -0.17],
    [0.71, -0.19],
    [0.74, -0.19],
    [0.77, -0.18],
    [0.85, -0.15],
    [0.92, -0.11],
    [0.98, -0.04],
    [0.99, -0.03],
    [1, -0.02],
    [1, 0],
  ];
  line2 = [
    [0, 0],
    [0.07, 0],
    [0.13, 0],
    [0.19, -0.03],
    [0.36, -0.08],
    [0.29, -0.28],
    [0.35, -0.39],
    [0.44, -0.56],
    [0.67, -0.53],
    [0.83, -0.45],
    [0.91, -0.42],
    [0.98, -0.37],
    [1.03, -0.3],
    [1.06, -0.26],
    [1.07, -0.22],
    [1.06, -0.17],
    [1.06, -0.11],
    [1.03, -0.06],
    [1, 0],
  ];
  line1 = [[0, 0], [1, 0]];
  // len = 0.9324
  // len2 = 0.79904
  P1 = [-0.355744, 1.1354];
  P2 = [-0.97282, 0.4];
  P3 = [-0.28, 0];
  P4 = [0.28, 0];
  // val = 0.85697125697;
  len = sqrt((P1[0] - P2[0]) * (P1[0] - P2[0]) + (P1[1] - P2[1]) * (P1[1] - P2[1]));
  len_2 = sqrt((P3[0] - P4[0]) * (P3[0] - P4[0]) + (P3[1] - P4[1]) * (P3[1] - P4[1]));
  val = len_2 / len;
  P5 = [
    P1[0] + (P2[0] - P1[0]) * val,
    P1[1] + (P2[1] - P1[1]) * val,
  ];
  /*
  echo(
    len, len_2,
    len * val,
    P5,
  );

  R2 = [[0.79423, 0.612836], [0.0525799, 0.680932], [-0.892836, 0.51423], [-0.28, 0], [0.28, 0]] * 30;

  data = TesselationPolygon(
    R2,
    [1, 0, 2, 1, 2],
    [
      line1,
      reverse([for (i = line2) [abs(i[0] - 1), i[1]]]),
      //line3
      reverse([for (i = line3) [abs(i[0] - 1), i[1]]]),
    ],
    [0, 0, 0, 0, 0],
  );
  color("blue")
    polygon(data);

  //  data = TesselationPolygon(
  //    R2, [1, 2, -3, -2, 3],
  //    [line3, line2, line1]
  // );
  //color("blue")
  //  stroke([R2[2], R2[3]], width=10);
  // echo(
  //   data
  // );
  //region(data);

  PentagonTesselation(
    "R2", 100, 0, 0, 2,
    first_angle_modifier=-45, second_angle_modifier=5,
    first_length_modifier=0.5,
    second_length_modifier=0,
    third_length_modifier=0,
    line1=line1,
    //line2=line1,
    //line3=line1
    //line2=reverse([for (i = line2) [abs(i[0] - 1), i[1]]]),
    line2=line2,
    line3=reverse([for (i = line3) [abs(i[0] - 1), i[1]]])
  );
  PentagonTesselation(
    "R2", 100, 0, 0, 2,
    first_angle_modifier=-45, second_angle_modifier=5,
    first_length_modifier=0.5,
    second_length_modifier=0,
    third_length_modifier=0,
    line1=line1,
    //line2=line1,
    //line3=line1
    //line2=reverse([for (i = line2) [abs(i[0] - 1), i[1]]]),
    line2=line2,
    line3=reverse([for (i = line3) [abs(i[0] - 1), i[1]]])
  );

  //linear_extrude(height=2)
  // TesselationGooseArea(width=200, length=100, size=30, thickness=1);

  //  linear_extrude(height=2)
  //   union() {
  //    TesselationHexKiteArea(
  //    size=30, width=30, length=30
  // )
  //        rotate(30)
  //        TesselationChickenHex(size=30, thickness=1, outer_offset=0.2);
  // }

  //CanopyBoxLid();
  // A square
  //polygon([[0, 0], [50, 10], [47, 2], [50, -10]]);

  /*
  echo(
    TesselationFromQuadradicPoints(
      [[0, 0], [50, 10], [47, 2], [50, -10]],
      [[0, 0], [0.5, 0.5], [1, 0]],
      [[0, 0], [1, 0]],
      [[0, 0], [1, 0]],
    )
  );
  echo(
    (
      [
        for (
          i = [
            [0, 0],
            [0.213176, 0.056018],
            [0.406283, 0.07],
            [0.56471, -0.0733724],
            [0.693585, -0.0370756],
            [0.761958, 0.0107027],
            [1, 0],
          ]
        ) [i[0], -i[1]],
      ]
    )
  );
  linear_extrude(height=2)
    TesselationGooseArea(width=200, length=100, size=30, thickness=2);
    Voronoi(200, 100,  1);
    */
  /*
  $polygon_width = 200;
  $polygon_length = 100;
  calc_shape_width = 30;
  calc_shape_thickness = 2;
  linear_extrude(height=2)
    union() {
      TesselationHexKiteArea(
        size=calc_shape_width, width=$polygon_width, length=$polygon_length
      )
          rotate(30)
            TesselationChickenHex(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.2);
    }
    */

  //  Voronoi(200, 100, 2);
  // CanopyBoxLid();
  /*
  bez = [
    for (
      i = rot(
        a=60, p=[
          //   [110.71, 50.17],
          //   [111.0, 50.620000000000005],
          //  [111.0, 50.800000000000004],
          // [110.47, 51.11]s,
          [110.05, 51.55],
          [82.72, 42.28],
          [82.17, 41.89],
          [81.47, 35.08],
          [80.55, 28.16],
          [78.56, 21.64],
          [76.35000000000001, 14.420000000000002],
          [72.10000000000001, 8.96],
          [66.23, 4.310000000000002],
          [60.96, 0.15],
          [55.85, -1.05],
          [49.35, 0.94],
          [37.53, 4.5600000000000005],
          [40.82, 15.2],
          [45.5, 23.630000000000003],
          [45.81, 24.310000000000002],
          [45.97, 24.810000000000002],
          [45.23, 25.130000000000003],
          [38.93, 28.310000000000002],
          [32.48, 32.03],
          [28.279999999999998, 37.84],
          [25.58, 41.59],
          [31.349999999999998, 45.38],
          [34.23, 46.74],
          [35.339999999999996, 47.370000000000005],
          [35.4, 47.78],
          [34.489999999999995, 48.67],
          [29.319999999999993, 53.18],
          [26.009999999999994, 58.84],
          [25.979999999999997, 65.83],
          [20.679999999999996, 67.51],
          [15.829999999999997, 69.49],
          [12.749999999999996, 74.38],
          [11.809999999999997, 75.86999999999999],
          [9.419999999999996, 82.24],
          [9.819999999999997, 83.64],
          [9.849999999999996, 83.74],
          [9.949999999999998, 83.8],
          [10.049999999999997, 83.78],
          [16.619999999999997, 81.34],
          [23.919999999999995, 80.84],
          [30.709999999999997, 82.58],
          [31.609999999999996, 82.72],
          [31.619999999999997, 83.33],
          [30.74, 84.41],
          [25.709999999999997, 90.8],
          [22.369999999999997, 100.16],
          [23.659999999999997, 108.28],
          [24.249999999999996, 111.99],
          [26.319999999999997, 113.29],
          [29.969999999999995, 113.1],
          [38.42999999999999, 112.66999999999999],
          [40.19, 107.74],
          [42.489999999999995, 100.53],
          [43.28999999999999, 99.89],
          [43.459999999999994, 99.84],
          [43.91, 100.83],
          [44.94, 103.08],
          [45.419999999999995, 108.88],
          [45.63999999999999, 111.61],
          [46.339999999999996, 120.42],
          [45.199999999999996, 129.22],
          [42.169999999999995, 137.54],
          [28.57, 175.66],
          [14.69, 213.54],
          [0.55, 251.16],
          [-8.61, 252.81],
          //  [100.14999999999999, 35.68000000000001],
          // [110.71, 50.16999999999999],
        ]
      )
    ) [
      i[0] - 10,
      i[1] - 121,
    ],
  ];
  //  echo(bez);
  // color("red")
  // stroke(bez);

  max_y = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[0]]);
  //echo(max_y, min_y);
  //echo((bez * 1 / max_y));

  //echo([for (i = bez * 1 / min_y) [i[0] - 0.00660387, i[1]]]);
  //  color("red")
  // stroke([for (i = bez * 1 / max_y) [i[0] - 0.00660387, i[1]]]*100);

  line1 = [
    [-0.5, 0],
    [-0.46, 0.03],
    [-0.43, 0.07],
    [-0.39, 0.1],
    [-0.32, 0.15],
    [-0.29, 0.18],
    [-0.24, 0.19],
    [-0.2, 0.21],
    [-0.17, 0.22],
    [-0.13, 0.22],
    [-0.1, 0.2],
    [-0.06, 0.18],
    [-0.03, 0.12],
    [-0.02, 0.07],
    [-0.01, 0.04],
    [0.01, 0.01],
    [0.03, -0.02],
    [0.04, -0.04],
    [0.05, -0.05],
    [0.06, -0.05],
    [0.08, -0.05],
    [0.09, -0.05],
    [0.11, -0.05],
    [0.15, -0.05],
    [0.19, -0.04],
    [0.23, -0.04],
    [0.26, -0.06],
    [0.28, -0.07],
    [0.28, -0.09],
    [0.28, -0.11],
    [0.27, -0.19],
    [0.26, -0.21],
    [0.26, -0.23],
    [0.27, -0.25],
    [0.27, -0.25],
    [0.27, -0.25],
    [0.27, -0.25],
    [0.5, 0],
  ];
  line2 = [
    for (
      i = rot(
        a=0, p=[
          [0, 0],
          [0.015, 0.12],
          [-0.01, 0.14],
          [-0.03, 0.16],
          [-0.05, 0.18],
          [-0.07, 0.20],
          [-0.09, 0.23],
          [-0.09, 0.26],
          [-0.09, 0.29],
          [-0.09, 0.31],
          [-0.06, 0.33],
          [-0.03, 0.37],
          [0.01, 0.33],
          [0.03, 0.30],
          [0.03, 0.29],
          [0.03, 0.30],
          [0.06, 0.31],
          [0.09, 0.33],
          [0.12, 0.33],
          [0.14, 0.33],
          [0.14, 0.31],
          [0.14, 0.29],
          [0.14, 0.28],
          [0.17, 0.29],
          [0.20, 0.29],
          [0.22, 0.28],
          [0.24, 0.29],
          [0.26, 0.31],
          [0.29, 0.31],
          [0.32, 0.31],
          [0.33, 0.30],
          [0.30, 0.28],
          [0.29, 0.26],
          [0.28, 0.23],
          [0.28, 0.22],
          [0.32, 0.24],
          [0.36, 0.22],
          [0.39, 0.20],
          [0.40, 0.19],
          [0.40, 0.18],
          [0.39, 0.17],
          [0.37, 0.13],
          [0.35, 0.14],
          [0.32, 0.15],
          [0.31, 0.14],
          [0.32, 0.14],
          [0.32, 0.13],
          [0.34, 0.12],
          [0.38, 0.09],
          [0.42, 0.07],
          [0.46, 0.07],
          [0.63, 0.03],
          [0.80, 0.00],
          [0.97, -0.02],
          [1, 0],
        ]
      )
    ) [(i[0] - 0.5), i[1]],
  ];
  //echo(line2);
  // stroke(line1 * 100);
  //color("red")
  //  stroke(line2 * 100);
  TesselationChickenHex(100);
  /*
  radius = 200 / 2;
  side_length = radius;
  apothem = sqrt(radius * radius - (radius / 2) * (radius / 2));

  dx = apothem * 2;
  col_x = apothem + radius;
  dy = radius * 4 + apothem * 0.8;

  for (x = [0:3])
    for (y = [0:1])
      back(x * radius * 3 / 2)
        right(apothem * 2 * y + (x % 2) * apothem)
          rotate(30)
            MakeTesselationKiteHexagon(
              100,
              [[-0.5, 0], [0.3, 0.25], [0.5, 0]],
              [[-0.5, 0], [0.3, 0.25], [0.5, 0]],
            );
            */
}
