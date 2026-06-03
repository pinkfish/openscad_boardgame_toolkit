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
include <lib/dominion.scad>

box_width = 288;
box_length = 288;
box_height = 72;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_lid_shape_type = SHAPE_TYPE_VORONOI;

player_board_width = 242;
player_board_length = 288;
player_board_thickness = 2.1;
player_board_count = 6;
adundance_middle_board_thickness = 2.1;

abundance_board_width = 57;
abundance_board_length = 240;
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

readyness_token_width = 36;
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

abundance_box_width = box_width - card_box_width * 4;
abundance_box_length = box_length - 3;
abundance_box_height = box_height;

player_box_width = card_box_width;
player_box_length = card_box_length;
player_box_height = card_box_height / 6;

score_pad_box_width = score_pad_width + default_wall_thickness * 4;
score_pad_box_length = box_length - card_box_length * 2 - 1;
score_pad_box_height = score_pad_thickness * score_pad_number + default_floor_thickness;

canopy_box_width = box_width - abundance_box_width - score_pad_box_width;
canopy_box_length = score_pad_box_length;
canopy_box_height = card_box_height;

seed_box_width = score_pad_box_width;
seed_box_length = canopy_box_length;
seed_box_height = default_floor_thickness + default_lid_thickness + leaf_thickness * 1.5;

sprout_box_width = score_pad_box_width;
sprout_box_length = canopy_box_length;
sprout_box_height = (card_box_height - score_pad_box_height - seed_box_height);

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
  finger_d = 12;
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
              d=start_disk_diameter, h=start_box_height, anchor=BOTTOM,
              finger_hole_radius=11.5,
              finger_holes=[45, 215]
            );
      up($inner_height - readyness_token_thickness - 0.5)
        right($inner_width / 2)
          back($inner_length - readyness_token_width / 2 - 2)
            CuboidWithIndentsBottom(
              [readyness_token_length, readyness_token_width, readyness_token_thickness + 1], anchor=BOTTOM,
              finger_holes=[0],
              finger_hole_radius=15,
              rounding=1,
              edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
            );

      up($inner_height - score_overide_thickness - 0.5)
        back(start_disk_diameter)
          right(score_override_marker_length / 2 + 2)
            CuboidWithIndentsBottom(
              [score_override_marker_width, score_override_marker_length, score_overide_thickness + 1],
              anchor=BOTTOM,
              finger_hole_radius=9,
              finger_holes=[0],
              rounding=1,
              edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
            );
    }
    union() {
      up($inner_height - score_overide_thickness - 0.5)
        back(start_disk_diameter)
          right(score_override_marker_length / 2 + 2)
            text("11", valign="center", halign="center");
      up($inner_height - readyness_token_thickness - 0.5)
        right($inner_width / 2)
          back($inner_length - readyness_token_width / 2 - 2)
            text("Active", valign="center", halign="center");
      back(start_disk_diameter / 2 + 2)
        right($inner_width / 2 + 7)
          up($inner_height - start_disk_thickness - 0.5)
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

module AbundanceBoardBox() // `make` me
{
  width = abundance_board_count * abundance_board_thickness + 1;
  MakeBoxWithNoLid(
    [abundance_box_width, abundance_box_length, abundance_box_height],
    finger_hole_size=25,
    finger_hole_wall_width=(abundance_box_width - width) / 2
  ) {
    right($inner_width / 2)
      up($inner_height - abundance_board_width)
        cuboid(
          [width, $inner_length, abundance_box_height],
          anchor=BOTTOM + FRONT, rounding=1
        );
  }
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
          right(10.5)
            back(readyness_token_width)
              cyl(d=13, h=player_box_height * 3, rounding=6.5, anchor=BOTTOM);
          left(10.5)
            back(readyness_token_width)
              cyl(d=13, h=player_box_height * 3, rounding=6.5, anchor=BOTTOM);
        }
      back(readyness_token_width + leaf_length * 3 / 4)
        up($inner_height - leaf_thickness - 0.3) {
          for (i = [0:2]) {
            right((leaf_width + 8) * (i - 1))for (j = [0:1]) {
              back((leaf_length + 7) * j)
                LeafTeardropWithFingerGrabs(leaf_thickness + 1);
            }
          }
        }
    }
    right($inner_width / 2) {
      up($inner_height - readyness_token_thickness - 0.3)
        back(2 + readyness_token_width / 2)
          text("Ready", valign="center", halign="center");
    }
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[player_box_width, player_box_length, player_box_height],
    text_str="Player",
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
    [seed_box_width, seed_box_length, seed_box_height],
    material_colour="brown"
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[seed_box_width, seed_box_length, seed_box_height]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, seed_box_height],
          radius=10
        );
    }
  }
}

module SeedBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[seed_box_width, seed_box_length, seed_box_height],
    text_str="Seeds",
    material_colour="brown"
  );
}

module SproutBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [sprout_box_width, sprout_box_length, sprout_box_height],
    material_colour="green"
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
  right(4 * card_box_width)
    AbundanceBoardBox();

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
        if (layout < 2) {
          up(sprout_box_height + score_pad_box_height)
            SeedBox();
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

if (FROM_MAKE != 1) {
  PlayerBox();
}
