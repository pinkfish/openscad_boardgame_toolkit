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

box_width = 233;
box_length = 304;
box_height = 80;

board_thickness = 12;
board_width = 203.5;
board_length = 234;

player_board_width = 108;
player_board_length = 214;
player_board_thickness = 16.5;

caravan_board_length = 101;
caravan_board_width = 76;
caravan_board_thickness = 16.5;

player_cube_size = 8.5;

pollution_tile_size = 25.5;

lantern_token_diameter = 21;

pollution_meter_length = 182;
pollution_meter_width = 13;
pollution_meter_thickness = 2.1;

pollution_tracker_token_diameter = 14.5;
pollution_tracker_token_thickness = 8.3;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;
card_size = MakeCardSize(length=92, width=66, single_card_thickness=single_card_thickness);
mutation_card_size = MakeCardSize(length=122, width=74, single_card_thickness=single_card_thickness);

trait_tile_width = 26.5;
trait_tile_length = 69.5;
trait_tile_thickness = 2.1;

num_curse_cards = 20;
num_equipment_cards = 20;
num_night_event_cards = 20;
num_day_event_cards = 20;
num_flock_cards = 24;
num_mutation_cards = 18;
num_reminder_cards = 8;

card_box_width = box_width / 2 - 0.5;
card_box_length = card_size.width + default_wall_thickness * 2 + 1;

mutation_card_box_width = mutation_card_size.length + default_wall_thickness * 2 + 1;
mutation_card_box_length = mutation_card_size.width + default_wall_thickness * 2 + 1;

curse_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_curse_cards + 2;
equipment_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_equipment_cards + 2;
night_event_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_night_event_cards + 2;
day_event_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_day_event_cards + 2;
flock_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_flock_cards + 2;

mutation_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_mutation_cards + 2;
reminder_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_reminder_cards + 2;

trait_tile_box_width = card_box_width / 3;
trait_tile_box_length = mutation_card_box_length;
trait_tile_box_height = default_floor_thickness + default_lid_thickness + trait_tile_thickness * 3 + 1;

tracker_pieces_width = default_wall_thickness * 2 + player_cube_size * 4.5;
tracker_pieces_length = board_length - card_box_length - mutation_card_box_length;
tracker_pieces_height = default_floor_thickness + default_lid_thickness + pollution_tracker_token_thickness + 1;

caravan_board_box_width = mutation_card_box_width;
caravan_board_box_length = tracker_pieces_length;
caravan_board_box_height = flock_card_box_height + tracker_pieces_height;

polution_box_width = card_box_width;
polution_box_length = default_wall_thickness * 2 + pollution_tile_size + 2;
polution_box_height = box_height - board_thickness - curse_card_box_height - equipment_card_box_height - flock_card_box_height;

lantern_token_box_width = card_box_length - polution_box_length - 0.5;
lantern_token_box_length = card_box_width;
lantern_token_box_height = polution_box_height;

essence_box_width = card_box_width;
essence_box_length = board_length - player_board_width - card_box_length;
essence_box_height = polution_box_height;

shepard_box_width = card_box_width;
shepard_box_length = card_box_length;
shepard_box_height = box_height - day_event_card_box_height - night_event_card_box_height - board_thickness - 0.5;

caravan_token_box_width = box_width - mutation_card_box_width - 1;
caravan_token_box_length = essence_box_length;
caravan_token_box_height = (box_height - board_thickness - 1) / 2;

standee_box_width = box_width - mutation_card_box_width - 1;
standee_box_length = essence_box_length;
standee_box_height = (box_height - board_thickness - 1) / 2;

back_spacer_box_width = box_width - 1;
back_spacer_box_length = box_length - board_length;
back_spacer_box_height = box_height - 1;

side_spacer_box_width = box_width - mutation_card_box_width - 1;
side_spacer_box_length = board_length - standee_box_length - card_box_length - 1;
side_spacer_box_height = box_height - board_thickness - player_board_thickness;

player_equipment_box_width = caravan_board_box_width;
player_equipment_box_length = caravan_board_box_length;
player_equipment_box_height = box_height - board_thickness - player_board_thickness - caravan_board_box_height;

module CurseCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, curse_card_box_height], lid_on_length=true
  ) {
    translate([0, $inner_length / 2, 0])
      cuboid(
        [card_size.length + 2, card_size.width, curse_card_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=curse_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module CurseCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, curse_card_box_height], text_str="Curse", lid_on_length=true);
}

module EquipmentCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, equipment_card_box_height], lid_on_length=true
  ) {
    translate([0, $inner_length / 2, 0])
      cuboid(
        [card_size.length + 2, card_size.width, curse_card_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=equipment_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module EquipmentCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, equipment_card_box_height], text_str="Equipment", lid_on_length=true);
}

module NightEventCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, night_event_card_box_height], lid_on_length=true
  ) {
    translate([0, $inner_length / 2, 0])
      cuboid(
        [card_size.length + 2, card_size.width, curse_card_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=night_event_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module NightEventCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, night_event_card_box_height], text_str="Night Event", lid_on_length=true);
}

module DayEventCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, day_event_card_box_height], lid_on_length=true
  ) {
    translate([0, $inner_length / 2, 0])
      cuboid(
        [card_size.length + 2, card_size.width, curse_card_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=day_event_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module DayEventCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, day_event_card_box_height], text_str="Day Event", lid_on_length=true);
}

module FlockCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[card_box_width, card_box_length, flock_card_box_height], lid_on_length=true
  ) {
    translate([0, $inner_length / 2, 0])
      cuboid(
        [card_size.length + 2, card_size.width, curse_card_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=flock_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module FlockCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, flock_card_box_height], text_str="Flock", lid_on_length=true);
}

module MutationCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[mutation_card_box_width, mutation_card_box_length, mutation_card_box_height], lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, mutation_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=mutation_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module MutationCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[mutation_card_box_width, mutation_card_box_length, mutation_card_box_height], text_str="Mutations", lid_on_length=true);
}

module ReminderCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[mutation_card_box_width, mutation_card_box_length, reminder_card_box_height], lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, reminder_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=reminder_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ReminderCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[mutation_card_box_width, mutation_card_box_length, reminder_card_box_height], text_str="Reminders", lid_on_length=true);
}

module TraitTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[trait_tile_box_width, trait_tile_box_length, trait_tile_box_height],
    lid_on_length=true,
  ) {
    translate([$inner_width / 2, $inner_length / 2, 0])
      cuboid(
        [trait_tile_width, trait_tile_length, trait_tile_box_height],
        anchor=BOTTOM
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=12, height=trait_tile_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module TraitTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(size=[trait_tile_box_width, trait_tile_box_length, trait_tile_box_height], text_str="Traits", lid_on_length=true);
}

module TrackerPiecesBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[tracker_pieces_width, tracker_pieces_length, tracker_pieces_height],
  ) {
    translate(
      (
        [
          1,
          1,
          $inner_height - player_cube_size / 2,
        ]
      )
    ) {
      RoundedBoxAllSides(
        [
          $inner_width - 2,
          $inner_length - 2,
          player_cube_size,
        ],
        radius=player_cube_size / 2
      );
    }
    translate(
      [
        $inner_width / 2,
        pollution_tracker_token_diameter / 2 + 4.5,
        $inner_height - pollution_tracker_token_thickness,
      ]
    )
      cyl(
        d=pollution_tracker_token_diameter,
        h=$inner_height,
        anchor=BOTTOM
      );
    translate(
      [
        10.5,
        pollution_tracker_token_diameter + 6.5,
        $inner_height - player_cube_size - 0.5,
      ]
    ) {
      cuboid(
        [
          player_cube_size * 2,
          player_cube_size * 2,
          player_cube_size + 1,
        ],
        anchor=BOTTOM + FRONT + LEFT
      );
      cuboid(
        [
          player_cube_size,
          player_cube_size * 3,
          player_cube_size + 1,
        ],
        anchor=BOTTOM + FRONT + LEFT
      );
    }
    translate(
      [
        6.5,
        pollution_tracker_token_diameter + 9 + player_cube_size * 3,
        $inner_height - player_cube_size - 0.5,
      ]
    ) {
      cuboid(
        [
          player_cube_size * 3,
          player_cube_size * 3,
          player_cube_size + 1,
        ],
        anchor=BOTTOM + FRONT + LEFT
      );
      translate(
        [
          player_cube_size * 2,
          -player_cube_size,
          0,
        ]
      )
        cuboid(
          [
            player_cube_size,
            player_cube_size * 3,
            player_cube_size + 1,
          ],
          anchor=BOTTOM + FRONT + LEFT
        );
    }
  }
}

module TrackerPiecesBoxLid() // `make` me
{
  CapBoxLidWithLabel(size=[tracker_pieces_width, tracker_pieces_length, tracker_pieces_height], text_str="Tracker");
}

module PolutionBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[polution_box_width, polution_box_length, polution_box_height],
  ) {
    translate(
      [
        pollution_tile_size / 2 + 10,
        $inner_length / 2,
        $inner_height - 3 * trait_tile_thickness,
      ]
    )
      CuboidWithIndentsBottom(
        [pollution_tile_size, pollution_tile_size, polution_box_height],
        anchor=BOTTOM,
        finger_holes=[2, 6],
        finger_hole_radius=8
      );
    translate(
      [
        $inner_width - pollution_tile_size / 2 - 10,
        $inner_length / 2,
        $inner_height - 3 * trait_tile_thickness,
      ]
    )
      CuboidWithIndentsBottom(
        [pollution_tile_size, pollution_tile_size, polution_box_height],
        anchor=BOTTOM,
        finger_holes=[2, 6],
        finger_hole_radius=8
      );
  }
}

module PolutionBoxLid() // `make` me
{
  CapBoxLidWithLabel(size=[polution_box_width, polution_box_length, polution_box_height], text_str="Polution");
}

module CaravanBoardBox() // `make` me
{
  MakeBoxWithNoLid(
    size=[
      caravan_board_box_width,
      caravan_board_box_length,
      caravan_board_box_height,
    ],
    make_finger_x=false,
    make_finger_y=false
  ) {
    translate([$inner_width, $inner_length / 2, 0])
      cuboid(
        [
          caravan_board_length,
          caravan_board_width,
          caravan_board_box_height,
        ],
        anchor=BOTTOM + RIGHT
      );

    translate([$inner_width - caravan_board_length / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=caravan_board_box_height,
      );
    }
    translate([-default_wall_thickness - 0.5, -default_wall_thickness - 0.5, $inner_height - tracker_pieces_height])
      cube([tracker_pieces_width + 1, caravan_board_box_length + 1, tracker_pieces_height + 1]);
  }
}

module LanternBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[lantern_token_box_length, lantern_token_box_width, lantern_token_box_height],
  ) {
    for (i = [0:3])
      translate(
        [
          lantern_token_diameter / 2 + 1 + (lantern_token_diameter + 3.75) * i,
          $inner_length / 2,
          $inner_height - (i < 2 ? 4 : 3) * trait_tile_thickness - 0.5,
        ]
      ) {
        CylinderWithIndents(
          d=lantern_token_diameter,
          h=4 * trait_tile_thickness + 1,
          anchor=BOTTOM,
          finger_holes=[90, 270],
          finger_hole_radius=7
        );
      }
  }
}

module LanternBoxLid() // `make` me
{
  CapBoxLidWithLabel(size=[lantern_token_box_length, lantern_token_box_width, lantern_token_box_height], text_str="Lanterns");
}

module EssenceTokenBox() // `make` me
{
  MakeBoxWithCapLid(
    size=[essence_box_width, essence_box_length, essence_box_height]
  ) {
    translate([0.5, 0.5, 0])
      RoundedBoxAllSides(
        size=[$inner_width - 1, $inner_length - 1, essence_box_height],
        radius=5
      );
  }
}

module EssenceTokenBoxLid() // `make` me
{
  CapBoxLidWithLabel(size=[essence_box_width, essence_box_length, essence_box_height], text_str="Essence");
}

module ShepardBox() // `make` me
{
  MakeBoxWithFilamentHinge(
    size=[shepard_box_width, shepard_box_length, shepard_box_height],
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[shepard_box_width, shepard_box_length, shepard_box_height]);
      translate([0.5, 0.5, 0])
        RoundedBoxAllSides(
          size=[$inner_width - 1, $inner_length - 1, shepard_box_height],
          radius=10
        );
    }
  }
}

module ShepardBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(size=[shepard_box_width, shepard_box_length, shepard_box_height], text_str="Shepard");
}

module CaravanTokenBox() // `make` me
{
  MakeBoxWithFilamentHinge(
    size=[caravan_token_box_width, caravan_token_box_length, caravan_token_box_height],
  ) {

    intersection() {
      FilamentBoxInsideMask(size=[caravan_token_box_width, caravan_token_box_length, caravan_token_box_height]);

      translate([0, 0, 0])
        RoundedBoxAllSides(
          size=[$inner_width, $inner_length, caravan_token_box_height],
          radius=10
        );
    }
  }
}

module CaravanTokenBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(size=[caravan_token_box_width, caravan_token_box_length, caravan_token_box_height], text_str="Caravans");
}

module StandeeBox() // `make` me
{
  MakeBoxWithFilamentHinge(
    size=[standee_box_width, standee_box_length, standee_box_height],
  ) {
    intersection() {
      FilamentBoxInsideMask(size=[standee_box_width, standee_box_length, standee_box_height]);

      RoundedBoxAllSides(
        size=[$inner_width, $inner_length, standee_box_height],
        radius=10
      );
    }
  }
}

module StandeeBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[standee_box_width, standee_box_length, standee_box_height],
    text_str="Standees"
  );
}

module BackSpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    size=[back_spacer_box_width, back_spacer_box_length, back_spacer_box_height],
    hollow=true,
  );
}

module SideSpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    size=[side_spacer_box_width, side_spacer_box_length, side_spacer_box_height],
    hollow=true,
  );
}

module PlayerEquipmentBox() // `make` me
{
  MakeBoxWithSlidingLid(
    size=[player_equipment_box_width, player_equipment_box_length, player_equipment_box_height],
    lid_on_length=true,
  ) {
    back($inner_length / 2)
      cube(
        [card_size.length, card_size.width, player_equipment_box_height],
        anchor=BOTTOM + LEFT
      );
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=player_equipment_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module PlayerEquipmentBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    size=[player_equipment_box_width, player_equipment_box_length, player_equipment_box_height],
    text_str="Player Equipment"
  );
}

module BoxLayout(layout = 0) {
  player_colors = [
    "blue",
    "yellow",
    "green",
    "red",
    "purple",
    "brown",
  ];
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([1, box_length, box_height]);
  }

  if (layout < 2) {
    translate([0, 0, box_height - board_thickness]) cube([board_width, board_length, board_thickness]);
  }
  if (layout < 3) {
    translate([0, board_length - player_board_width, box_height - board_thickness - player_board_thickness]) cube([player_board_length, player_board_width, player_board_thickness]);
  }

  translate([0, 0, 0]) CurseCardBox();
  translate([0, 0, curse_card_box_height]) EquipmentCardBox();
  if (layout < 4) {
    translate([0, 0, curse_card_box_height + equipment_card_box_height]) FlockCardBox();
  }
  if (layout < 3) {
    translate([0, 0, curse_card_box_height + equipment_card_box_height + flock_card_box_height]) PolutionBox();
    translate([0, polution_box_length, curse_card_box_height + equipment_card_box_height + flock_card_box_height]) LanternBox();
  }
  translate([card_box_width, 0, 0]) color("yellow") DayEventCardBox();
  if (layout < 4) {
    translate([card_box_width, 0, day_event_card_box_height]) color("black") NightEventCardBox();
  }
  if (layout < 3) {
    translate([card_box_width, 0, day_event_card_box_height + night_event_card_box_height]) color("brown") ShepardBox();
  }
  translate([mutation_card_box_width, card_box_length, 0]) color("blue") CaravanTokenBox();
  if (layout < 3) {
    translate([mutation_card_box_width, card_box_length, caravan_token_box_height]) color("green") StandeeBox();
  }

  if (layout < 4) {
    for (i = [0:2]) {
      translate([trait_tile_box_width * i, card_box_length, mutation_card_box_height + reminder_card_box_height]) color(player_colors[i]) TraitTileBox();
      translate([trait_tile_box_width * i, card_box_length, mutation_card_box_height + reminder_card_box_height + trait_tile_box_height]) color(player_colors[i + 3]) TraitTileBox();
    }
  }
  if (layout < 3) {
    translate([0, card_box_length, day_event_card_box_height + night_event_card_box_height + trait_tile_box_height * 2]) EssenceTokenBox();
  }

  translate([0, card_box_length, 0]) MutationCardBox();
  translate([0, card_box_length, mutation_card_box_height]) ReminderCardBox();
  translate([0, card_box_length + mutation_card_box_length, caravan_board_box_height - tracker_pieces_height]) TrackerPiecesBox();
  translate([0, card_box_length + mutation_card_box_length, 0]) CaravanBoardBox();
  translate([0, card_box_length + mutation_card_box_length, caravan_board_box_height]) PlayerEquipmentBox();
  if (layout < 4) {
    translate([mutation_card_box_width, card_box_length + standee_box_length, 0]) SideSpacerBox();
  }
  translate([0, board_length, 0]) BackSpacerBox();
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
  ShepardBox();
  //translate([default_wall_thickness, default_wall_thickness, default_floor_thickness])
  //FilamentBoxInsideMask(size=[caravan_token_box_width, caravan_token_box_length, caravan_token_box_height]);
}
