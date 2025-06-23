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

box_width = 310;
box_length = 385;
box_height = 100;

generate_mmu = MAKE_MMU == 1;

default_material_colour = "purple";
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

card_width = 68;
card_length = 92;
bond_width = 59;
bond_length = 78;
bond_card_thickness = 17;
train_card_width = 58;
train_card_length = 90;
train_card_thickness = 10 / 4;
crossing_height = 14;
crossing_length = 34;
total_board_thickness = 22;

silo_piece_width = 22;
silo_piece_height = 43;
mine_height = 27;
mine_width = 21;
roundhouse_height = 40;
roundhouse_total_width = 90;

ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

money_thickness = 10;
money_length = 134;
money_width = 62;
tile_width = 29;
tile_radius = tile_width / 2 / cos(180 / 6);
tile_thickness = 2;
sweden_bonus_length = 35.5;
sweden_bonus_width = 16.5;
australia_switch_track_token_radius = 8.5;
player_marker_diameter = 15.5;
player_marker_thickness = 5;

eastern_us_cards = 12 + 31 + 6 + 2;
mexico_cards = 12 + 38 + 5 + 4;
europe_cards = 10 + 29 + 5;
western_us_cards = 12 + 38 + 6;
great_britan_cards = 10 + 27 + 5;
north_america_cards = 24 + 50 + 12;
portugal_cards = 10 + 34 + 4;
australia_cards = 63 + 15 + 6;
sweden_cards = 12 + 43;

lid_thickness = 3;
wall_thickness = 2;
inner_wall = 1.5;

function CardBoxWidth(num_cards) = num_cards * single_card_thickness + wall_thickness * 2;

all_boxes_height = card_width + wall_thickness + lid_thickness;

card_box_width = card_length + wall_thickness * 2 + 1;

eastern_us_card_box_length = CardBoxWidth(eastern_us_cards) + inner_wall + bond_card_thickness + 0.5;

//    eastern_us_cards * single_card_thickness + bond_card_thickness + inner_wall + wall_thickness * 2;

player_box_width = (box_length - card_box_width - 2) / 3;
player_box_plastic_extra_length =
train_card_width + silo_piece_height * 2 + roundhouse_height + inner_wall * 2 + wall_thickness * 2;
player_box_height = silo_piece_width + lid_thickness * 2;
player_box_length = train_card_width + wall_thickness * 2 + 7.4;
player_box_silo_lid_hole_first = 81;
player_box_silo_lid_hole_second = 121;
player_box_silo_lid_hole_size = 4;
player_box_small_height = player_box_height * 2 / 3;

top_section_height = all_boxes_height - player_box_height * 2;
top_section_width = box_length - card_box_width - 2;

western_us_expansion_box_width = 41;

money_section_width = money_width + 1.5 + wall_thickness * 2;
money_section_length = money_length + 1.5 + wall_thickness * 2;

hex_box_width = money_section_length;
hex_box_length = tile_width * 5 + wall_thickness * 2;
hex_box_extra_height = (player_box_height * 2 - top_section_height * 3) / 2;

new_city_box_length = money_section_width;
new_city_box_width = money_section_length;
new_city_extra_length = (hex_box_width - money_section_width * 2) / 2;
new_city_extra_width = hex_box_length - money_section_length;

empty_city_width = 47;
empty_city_length = (player_box_width * 3) / 2 - 0.5;
empty_city_height = player_box_height * 2;

player_box_trains_length = box_width - empty_city_width - player_box_plastic_extra_length - 2;

expansion_area_box_width = box_width - CardBoxWidth(portugal_cards) - money_section_width - 1 - new_city_extra_length;

sweden_box_width = expansion_area_box_width;
sweden_box_length = empty_city_length;

australia_box_width = expansion_area_box_width;
australia_box_length = empty_city_length - 0.5;

module CardBox(num_cards, text_str, generate_lid = true) {
  if (generate_lid) {
    translate([box_length * 2 + 10, 0, 0]) rotate([0, 0, 90]) SlidingBoxLidWithLabel(
          width=card_box_width, length=box_length, lid_thickness=lid_thickness,
          text_str=text_str, wall_thickness=2,
          lid_on_length=true, label_colour="black"
        ) children();
  } else {
    box_length = CardBoxWidth(num_cards);
    translate([box_length, 0, 0]) rotate([0, 0, 90]) {
        MakeBoxWithSlidingLid(
          width=card_box_width, length=box_length, height=all_boxes_height,
          lid_thickness=lid_thickness, wall_thickness=wall_thickness, lid_on_length=true
        ) {
          cube([$inner_width, $inner_length, all_boxes_height - lid_thickness]);
          translate([card_box_width / 2, box_length / 2, all_boxes_height - 28 + 0.01 - lid_thickness / 2])
            FingerHoleWall(
              radius=25, height=28, depth_of_hole=card_box_width + 2, orient=UP,
              rounding_radius=5
            );
        }
      }
  }
}

module CardBoxEasternUS() // `make` me
{
  translate([eastern_us_card_box_length, 0, 0]) rotate([0, 0, 90]) {
      union() {
        MakeBoxWithSlidingLid(
          width=card_box_width, length=eastern_us_card_box_length,
          height=all_boxes_height, lid_thickness=lid_thickness,
          wall_thickness=wall_thickness
        ) {
          cube(
            [
              $inner_width,
              CardBoxWidth(num_cards=eastern_us_cards) - wall_thickness * 2,
              all_boxes_height - lid_thickness,
            ]
          );
          translate(
            [
              card_box_width / 2,
              eastern_us_card_box_length / 2,
              all_boxes_height - 28 + 0.01 - lid_thickness / 2,
            ]
          ) FingerHoleWall(
              radius=25, height=eastern_us_card_box_length * 2,
              depth_of_hole=card_box_width + 2, orient=UP, rounding_radius=5
            );
          translate(
            [
              ($inner_width - bond_length) / 2,
              CardBoxWidth(num_cards=eastern_us_cards) + inner_wall - wall_thickness * 2,
              card_width - bond_width,
            ]
          ) cube([bond_length, bond_card_thickness, bond_width + wall_thickness + 1]);
        }
        // Bond section.
      }
    }
}

module CardBoxEasternUSLid() // `make` me

{
  text_str = "Eastern US";
  rotate([0, 0, 90]) {
    SlidingBoxLidWithLabel(
      width=card_box_width, length=eastern_us_card_box_length,
      lid_thickness=lid_thickness,
      text_str=text_str, label_rotated=false, label_colour="black",
      label_width_offset=-5
    ) {
      translate([25, 40, 0]) rotate(270) {
          UnitedStatesFlag(
            length=30, white_height=lid_thickness, red_height=1.5, blue_height=1.5,
            border=1, solid_background=true
          );
        }
    }
  }
}
module CardBoxAustralia() // `make` me
{
  CardBox(australia_cards, "Australia", generate_lid=false) {
    translate([17, 27, 0]) rotate(90) {
        AustralianFlag(
          length=30, white_height=2, red_height=1.5, blue_height=1, border=1,
          solid_background=generate_mmu
        );
      }
  }
}

module CardBoxAustraliaLid() // `make` me
{
  CardBox(australia_cards, "Australia") {
    translate([17, 27, 0]) rotate(90) {
        AustralianFlag(
          length=30, white_height=2, red_height=1.5, blue_height=1, border=1,
          solid_background=generate_mmu
        );
      }
  }
}

module CardBoxMexico() // `make` me
{
  CardBox(mexico_cards, "Mexico", generate_lid=false);
}

module CardBoxMexicoLid() // `make` me
{
  CardBox(mexico_cards, "Mexico");
}

module CardBoxSweden() // `make` me
{
  CardBox(sweden_cards, "Sweden", generate_lid=false) {
    translate([12, 18, 0]) rotate(90) {
        SwedenFlag(length=20, height=lid_thickness, border=1, solid_background=generate_mmu);
      }
  }
}

module CardBoxSwedenLid() // `make` me
{
  CardBox(sweden_cards, "Sweden") {
    translate([12, 18, 0]) rotate(90) {
        SwedenFlag(length=20, height=lid_thickness, border=1, solid_background=generate_mmu);
      }
  }
}

module CardBoxPortugal() // `make` me
{
  CardBox(portugal_cards, "Portugal", generate_lid=false);
}

module CardBoxPortugalLid() // `make` me
{
  CardBox(portugal_cards, "Portugal");
}

module PlayerBoxWithPlasticExtras() // `make` me
{
  card_height = train_card_thickness * 4 + 0.5;
  MakeBoxWithInsetLidTabbed(
    width=player_box_width, length=player_box_plastic_extra_length,
    height=player_box_height, lid_thickness=lid_thickness,
    wall_thickness=wall_thickness, floor_thickness=1
  ) {
    // Round houses.
    difference() {
      cube([$inner_width, roundhouse_height, player_box_height]);

      translate([(player_box_width - wall_thickness * 2) / 2 - 7, wall_thickness * 3, 0])
        linear_extrude(height=0.5) import("svg/rotw - roundhouse.svg");
    }
    // water tower.
    difference() {
      translate([0, roundhouse_height + inner_wall, 0])
        cube([$inner_width - mine_width - inner_wall - 5, silo_piece_height * 2, player_box_height]);
      translate(
        [
          wall_thickness + silo_piece_width,
          wall_thickness + roundhouse_height + inner_wall + silo_piece_height / 2,
          0,
        ]
      ) linear_extrude(height=0.5) import("svg/rotw - water.svg");
    }
    // mine section.
    difference() {
      translate(
        [$inner_width - wall_thickness - mine_width + inner_wall - 4, roundhouse_height + inner_wall, 0]
      )
        cube([mine_width + 4, silo_piece_height * 2, player_box_height]);
      // Offset in here fixes the error in the svg file.
      translate(
        [$inner_width - mine_width + inner_wall, roundhouse_height + inner_wall + silo_piece_height / 2, 0]
      )
        linear_extrude(height=0.5) offset(delta=0.001) import("svg/rotw - mine.svg");
    }
    // cards.
    translate(
      [
        0,
        roundhouse_height + inner_wall * 2 + silo_piece_height * 2,
        player_box_height - lid_thickness - card_height - 1,
      ]
    ) cube([train_card_length, train_card_width, player_box_height]);
    // Recessed box for crossings.
    difference() {
      translate(
        [player_box_width * 1 / 8 + 4, roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + 7, 0]
      )
        difference() {
          cube([player_box_width * 3 / 4, crossing_length * 1.25, player_box_height + 1]);
          translate([25, 5, 0]) linear_extrude(height=0.5) import("svg/rotw - signal.svg");
        }
    }
    translate(
      [
        wall_thickness - 0.3,
        roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + crossing_length * 1.25 / 2,
        0,
      ]
    ) FingerHoleBase(
        radius=10, height=player_box_height - 1 + 0.01, wall_thickness=wall_thickness * 2,
        spin=270, rounding_radius=5, floor_thickness=1
      );
  }
  ;
}

module PlayerBoxWithPlasticExtrasLid() // `make` me
{
  text_str = "Player";

  difference() {
    InsetLidTabbedWithLabel(
      width=player_box_width, length=player_box_plastic_extra_length,
      lid_thickness=lid_thickness,
      text_str=text_str, label_colour="black"
    );
    translate([player_box_width - 56, player_box_silo_lid_hole_first - player_box_silo_lid_hole_size, 0.5])
      cube([50, player_box_silo_lid_hole_size, lid_thickness + 1]);
    translate([player_box_width - 56, player_box_silo_lid_hole_second - player_box_silo_lid_hole_size, 0.5])
      cube([50, player_box_silo_lid_hole_size, lid_thickness + 1]);
  }
}

module PlayerBox() // `make` me
{
  card_height = train_card_thickness * 4 + 1;
  lid_thickness = 1.7;
  echo(
    [
      1111,
      card_height + player_marker_thickness + 1.7 * 2,
      player_box_height,
      card_box_width,
      player_box_length,
      player_box_small_height,
      lid_thickness,
    ]
  );
  MakeBoxWithCapLid(
    width=player_box_width, length=player_box_length, height=player_box_small_height,
    lid_thickness=lid_thickness
  ) {
    translate(
      [
        ($inner_width) / 2,
        ($inner_length) / 2,
        $inner_height - card_height,
      ]
    ) cuboid([train_card_length, train_card_width, player_box_small_height], anchor=BOTTOM);

    translate([0, player_box_length / 2, 0]) FingerHoleBase(radius=14, height=player_box_height, spin=270);

    translate(
      [
        $inner_width / 2,
        $inner_length / 2,
        $inner_height - card_height - player_marker_thickness - 0.4,
      ]
    ) {
      cyl(d=player_marker_diameter + 0.5, h=player_marker_thickness + 2, anchor=BOTTOM);
      translate([player_marker_diameter / 2, 0, 10]) sphere(r=10);
    }
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_small_height,
    text_str="Player", lid_thickness=1.7,
    label_colour="black"
  );
}

module PlayerBoxTrains() // `make` me
{
  MakeBoxWithSlidingLid(
    width=player_box_width, length=player_box_trains_length, height=player_box_height,
    lid_thickness=lid_thickness, wall_thickness=wall_thickness, floor_thickness=1
  ) {
    cube([$inner_width, $inner_length, empty_city_height]);
  }
}

module PlayerBoxTrainsLid() // `make` me
{
  text_str = "Trains";
  SlidingBoxLidWithLabel(
    width=player_box_width, length=player_box_trains_length, lid_thickness=lid_thickness,
    text_str=text_str,
    label_rotated=false, label_colour="black"
  );
}

module EmptyCityBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=empty_city_width, length=empty_city_length, height=empty_city_height,
    lid_thickness=lid_thickness, wall_thickness=wall_thickness
  ) {
    cube([$inner_width, $inner_length, empty_city_height]);
  }
}

module EmptyCityBoxLid() // `make` me
{
  text_str = "Empty City";

  SlidingLid(empty_city_width, empty_city_length, lid_thickness=lid_thickness) {
    translate([10, 10, 0]) LidMeshHex(
        width=empty_city_width, length=empty_city_length,
        lid_thickness=lid_thickness, boundary=10, radius=12
      );
    translate([(empty_city_width + text_height) / 2, (empty_city_length - text_width) / 2, 0])
      rotate([0, 0, 90])
        MakeStripedLidLabel(
          width=text_width, length=text_height, lid_thickness=lid_thickness,
          label=text_str, border=wall_thickness, offset=4, label_colour="black"
        );
  }
}

module MoneyBox(extra_length = 0, extra_width = 0) // `make` me
{
  MakeBoxWithSlidingLid(
    width=money_section_width + extra_width, length=money_section_length + extra_length,
    height=top_section_height, lid_thickness=lid_thickness, wall_thickness=wall_thickness
  ) {
    cube([money_width + extra_width, money_length + extra_length, empty_city_height]);

    translate([money_section_width / 2, 0, top_section_height - 20]) FingerHoleBase(radius=15, height=20);
  }
}

module MoneyBoxLid(extra_length = 0, extra_width = 0) // `make` me
{
  text_str = "Money";
  SlidingBoxLidWithLabel(
    width=money_section_width + extra_width, length=money_section_length + extra_length,
    lid_thickness=lid_thickness,
    text_str=text_str, label_colour="black"
  );
}

module HexBox(extra_height = 0) // `make` me
{
  MakeBoxWithCapLid(width=hex_box_width, length=hex_box_length, height=top_section_height + extra_height) {
    HexGridWithCutouts(
      rows=4, cols=5, height=top_section_height + extra_height, spacing=0,
      push_block_height=0.25, tile_width=tile_width
    );
  }
}

module HexBoxLid(extra_height = 0) // `make` me
{
  text_str = "Tracks";
  CapBoxLidWithLabel(
    width=hex_box_width, length=hex_box_length, height=top_section_height + extra_height,
    text_str=text_str, label_colour="black"
  );
}

module NewCityBox(extra_width = 0, extra_length = 0) // `make` me
{
  MakeBoxWithCapLid(
    width=new_city_box_width + extra_width, length=new_city_box_length + extra_length,
    height=top_section_height, lid_thickness=lid_thickness, wall_thickness=wall_thickness
  ) {
    translate([2, 2.5, 0]) {
      translate([0, 0, $inner_height - tile_thickness * 4])
        RegularPolygonGrid(width=tile_width, rows=2, cols=2, spacing=0) {
          RegularPolygon(width=tile_width, height=tile_thickness * 4.25, shape_edges=6);
          cyl(r=10, h=20, $fn=64);
        }
      translate([tile_radius * 2, tile_width / 2, 14]) sphere(r=10, $fn=64);
      translate([tile_radius * 2, tile_width * 3 / 2, 14]) sphere(r=10, $fn=64);
      translate([3 + tile_radius * 5, tile_width, $inner_height - tile_thickness * 2.5]) {
        RegularPolygon(width=tile_width, height=top_section_height, shape_edges=6);
        translate([0, -tile_width / 2, 10]) sphere(r=10);
      }
    }
    translate([tile_radius * 7, 12, $inner_height - 10]) {
      cube([15.5, 41, 11]);
      translate([7.75, 0, 3]) sphere(r=8, anchor=BOTTOM);
    }
  }
}

module NewCityBoxLid(extra_width = 0, extra_length = 0) // `make` me
{
  text_str = "New Cities";
  CapBoxLidWithLabel(
    width=new_city_box_width + extra_width, length=new_city_box_length + extra_length,
    height=top_section_height, lid_thickness=lid_thickness,
    text_str=text_str, label_rotated=false, label_colour="black"
  );
}

module SwedenBox() // `make` me
{
  apothem = tile_width / 2;
  radius = apothem / cos(180 / 6);

  MakeBoxWithCapLid(
    width=sweden_box_width, length=sweden_box_length, height=top_section_height,
    lid_thickness=lid_thickness, wall_thickness=wall_thickness
  ) {
    HexGridWithCutouts(
      rows=6, cols=3, tile_width=tile_width, spacing=0, wall_thickness=wall_thickness,
      push_block_height=0.75, height=top_section_height
    );
    // bonus bit (top)
    for (i = [0:1:2]) {
      translate(
        [
          wall_thickness * 2 + (sweden_bonus_length + 4) * (i + 1),
          sweden_box_length - wall_thickness * 3 - sweden_bonus_width,
          top_section_height - lid_thickness - tile_thickness * 2.4 - wall_thickness,
        ]
      ) {
        cube([sweden_bonus_length, sweden_bonus_width, tile_thickness * 100.5]);
        translate([sweden_bonus_length / 2, 0, 10]) sphere(r=10);
      }
    }
    sweden_flag_len = 35;
    sweden_flag_wid = sweden_flag_len * 5 / 8;
    translate([2 + sweden_flag_len / 2, $inner_length - sweden_flag_wid / 2 - 2, $inner_height - 1]) {
      line_horiz = sweden_flag_wid * 2 / 10;
      line_vert = sweden_flag_len * 2 / 16;
      difference() {
        cuboid([sweden_flag_len, sweden_flag_wid, 50], anchor=BOTTOM);
        cuboid([sweden_flag_len - 2, sweden_flag_wid - 2, 50], anchor=BOTTOM);
      }
      cuboid([sweden_flag_len, line_horiz, 50], anchor=BOTTOM);
      translate([-sweden_flag_len * 3 / 16, 0, 0]) cuboid([line_vert, sweden_flag_wid, 50], anchor=BOTTOM);
    }
    translate([0, $inner_length - sweden_flag_wid * 3 / 2 - 10, $inner_height - 1]) linear_extrude(height=50)
        text("Sweden", font="Stencil Std:style=Bold", size=15);
  }
}

module SwedenBoxLid() // `make` me
{
  text_str = "Sweden";
  CapBoxLidWithLabel(
    width=sweden_box_width, length=sweden_box_length, height=top_section_height,
    lid_thickness=lid_thickness,
    text_str=text_str, label_rotated=false, label_colour="black"
  ) translate([84, 58, 0])
      scale(0.25) rotate([0, 0, 90]) color("lightblue") linear_extrude(height=lid_thickness) difference() {
                // Offset fixes the svg error.
                offset(delta=0.001) import("svg/sweden.svg");
                offset(-4) import("svg/sweden.svg");
              }
}

module AustraliaBox() // `make` me
{
  apothem = tile_width / 2;
  radius = apothem / cos(180 / 6);

  module NewCityHex(depth) {
    rotate([0, 0, 30]) RegularPolygon(shape_edges=6, width=tile_width, height=depth);
    translate([-apothem / 2, tile_radius * 3 / 4, 0]) sphere(r=8, anchor=BOTTOM);
    translate([apothem / 2, -tile_radius * 3 / 4, 0]) sphere(r=8, anchor=BOTTOM);
    translate([-apothem + 2, 0, -0.5]) linear_extrude(height=2)
        text("New City", font="Stencil Std:style=Bold", size=4);
  }

  MakeBoxWithCapLid(
    width=australia_box_width, length=australia_box_length, height=top_section_height,
    lid_thickness=lid_thickness, wall_thickness=wall_thickness, floor_thickness=lid_thickness
  ) {
    intersection() {
      translate([0, 0, -3]) cube([radius * 5 * 2, tile_width * 4, top_section_height + 1]);
      difference() {
        difference() {
          HexGridWithCutouts(
            rows=5, cols=4, tile_width=tile_width, spacing=0,
            wall_thickness=wall_thickness, push_block_height=0.75,
            height=top_section_height
          );
          translate([radius * 2, tile_width * 3, -3])
            cube([radius * 3 * 2, tile_width, top_section_height + 4]);
          translate([radius * 2 * 4, tile_width * 1, -3])
            cube([radius * 2, tile_width * 3, top_section_height + 4]);
        }
      }
    }

    // Cutouts for the bonus tiles.
    for (i = [0:1:1]) {
      translate(
        [
          ($inner_width - sweden_bonus_width),
          (sweden_bonus_length + 57) * i + 5,
          $inner_height - tile_thickness * 4.4,
        ]
      ) {
        cube([sweden_bonus_width, sweden_bonus_length, tile_thickness * 4.5]);

        translate([sweden_bonus_width, sweden_bonus_length / 2, 0]) xcyl(r=10, anchor=BOTTOM, h=10);
      }
    }

    // New city tiles.

    translate(
      [
        $inner_width - sweden_bonus_width - apothem - 1,
        apothem * 3 + wall_thickness + 2,
        $inner_height - tile_thickness * 3.3,
      ]
    ) {
      translate([0, 0, 0]) NewCityHex(tile_thickness * 3.3);
      translate([-apothem - 0.5, tile_radius * 3 / 2 + (tile_radius - apothem) / 2, 0])
        NewCityHex(tile_thickness * 3.3);
      translate([0, tile_radius * 3 + 2, tile_thickness]) NewCityHex(tile_thickness * 2.3);
      translate([apothem + 0.5, tile_radius * 3 / 2 + (tile_radius - apothem) / 2, tile_thickness])
        NewCityHex(tile_thickness * 2.3);
    }

    // Commonweath of Australia tile.
    translate(
      [
        $inner_width - tile_width * 2 - wall_thickness * 3 + 3,
        australia_box_length - tile_radius - wall_thickness * 3 - 1,
        $inner_height - tile_thickness * 1.4,
      ]
    ) {
      rotate([0, 0, 30]) RegularPolygon(shape_edges=6, width=tile_width, height=tile_thickness * 15);
      translate([apothem / 2, tile_radius * 3 / 4, 0]) sphere(r=9, anchor=BOTTOM);
      translate([-apothem / 2, -tile_radius * 3 / 4, 0]) sphere(r=9, anchor=BOTTOM);
    }

    // For the switch track tokens.
    for (i = [0:1:4]) {
      translate(
        [
          tile_radius * 2 + 1 + australia_switch_track_token_radius + (australia_switch_track_token_radius * 2 + inner_wall) * i,
          australia_box_length - wall_thickness - australia_switch_track_token_radius - tile_width - 5,
          $inner_height - tile_thickness * 2.2,
        ]
      ) {
        cyl(r=australia_switch_track_token_radius, h=tile_thickness * 2.4, anchor=BOTTOM);
        translate([0, australia_switch_track_token_radius, 1]) sphere(r=6, anchor=BOTTOM);
      }
      translate(
        [
          tile_radius * 2 + 1 + australia_switch_track_token_radius + (australia_switch_track_token_radius * 2 + inner_wall) * i,
          australia_box_length - wall_thickness * 2 - australia_switch_track_token_radius - 2,
          $inner_height - tile_thickness * 2.2,
        ]
      ) {
        cyl(r=australia_switch_track_token_radius, h=tile_thickness * 2.4, anchor=BOTTOM);
        translate([0, -australia_switch_track_token_radius, 1]) sphere(r=6, anchor=BOTTOM);
      }
    }

    // Map in the top section.
    translate([5, australia_box_length - 26, $inner_height - 1]) scale(0.17) linear_extrude(height=100)
          difference() {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
          }
  }
}

module AustraliaBoxLid() // `make` me
{
  text_str = "Australia";
  CapBoxLidWithLabel(
    width=australia_box_width, length=australia_box_length, height=top_section_height,
    lid_thickness=lid_thickness,
    text_str=text_str, label_rotated=false, label_colour="black"
  ) translate([44, 15, 0])
      color("blue") linear_extrude(height=lid_thickness) scale(0.3) difference() {
              fill() import("svg/australia.svg");
              offset(-4) fill() import("svg/australia.svg");
            }
}

module EmptyCityModel() {
  cyl(h=6, d=27, anchor=BOTTOM);
  cyl(h=48, d=3.5, anchor=BOTTOM);
  translate([0, 3.5, 20]) ycyl(h=3, d=15, anchor=TOP + BACK);
  translate([0, 3.5, 34]) cuboid([20, 3, 5.5], anchor=TOP + BACK);
  translate([0, 5.5, 48]) cuboid([6, 5, 10], anchor=TOP + BACK, rounding=1);
  translate([0, 4.5, 50]) difference() {
      cuboid([12.5, 3, 7], anchor=TOP + BACK, rounding=4, edges=[BOTTOM + RIGHT, BOTTOM + LEFT]);
      translate([0, 0.5, -3]) ycyl(d=11, h=4, anchor=BOTTOM + BACK);
    }
}

module MirrorEmptyCity() {
  translate([0, 0, 50]) mirror([0, 0, 1]) EmptyCityModel();
}

module EmptyCityPair() {
  translate([7.5, 0, 0]) EmptyCityModel();
  translate([-7.5, 0, 7]) MirrorEmptyCity();
}

spacer_plastic_side_length = box_length - card_box_width - player_box_width - hex_box_width - 1 - new_city_extra_width;

module SpacerNoPlasticPlayerBoxSide() // `make` me
{
  difference() {
    color(default_material_colour) cuboid(
        [
          box_width - empty_city_width - player_box_trains_length - 2,
          spacer_plastic_side_length,
          all_boxes_height,
        ],
        rounding=2, edges=[FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT],
        anchor=BOTTOM + FRONT + LEFT, $fn=16
      );
    translate([wall_thickness, wall_thickness, wall_thickness]) color(default_material_colour) cube(
          [
            box_width - empty_city_width - player_box_trains_length - 2 - wall_thickness * 2,
            spacer_plastic_side_length - wall_thickness * 2,
            all_boxes_height,
          ]
        );
    translate([-1, -1, all_boxes_height - top_section_height]) color(default_material_colour)
        cuboid([90.5, 120, top_section_height + 1], anchor=BOTTOM + FRONT + LEFT, $fn=16, rounding=1);
    translate([-1, -1, all_boxes_height - top_section_height + 4.01]) color(default_material_colour)
        cuboid(
          [90.5, 125, top_section_height + 1 - 5], anchor=BOTTOM + FRONT + LEFT, $fn=16, rounding=-2,
          edges=[TOP + RIGHT]
        );
  }
}

spacer_front_width = box_width - (
  empty_city_width + player_box_trains_length + money_section_width + new_city_box_length + new_city_extra_length * 2
) - 2;

module SpacerNoPlasticPlayerBoxFront() // `make` me
{
  difference() {
    color(default_material_colour)
      cuboid(
        [spacer_front_width, box_length - card_box_width - spacer_plastic_side_length, all_boxes_height],
        rounding=2, edges=[FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT],
        anchor=BOTTOM + FRONT + LEFT, $fn=16
      );
    translate([wall_thickness, wall_thickness, wall_thickness]) color(default_material_colour) cube(
          [
            spacer_front_width - wall_thickness * 2,
            box_length - card_box_width - spacer_plastic_side_length - wall_thickness * 2,
            all_boxes_height,
          ]
        );
  }
}

module SpacerNoPlasticPlayerBoxTop() // `make` me
{
  spacer_width = box_width - sweden_box_width - spacer_front_width;
  difference() {
    color(default_material_colour)
      cuboid(
        [spacer_width, box_length - card_box_width - spacer_plastic_side_length, top_section_height],
        rounding=2, edges=[FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT],
        anchor=BOTTOM + FRONT + LEFT, $fn=16
      );
    translate([wall_thickness, wall_thickness, wall_thickness]) color(default_material_colour) cube(
          [
            spacer_width - wall_thickness * 2,
            box_length - card_box_width - spacer_plastic_side_length - wall_thickness * 2,
            all_boxes_height,
          ]
        );
  }
}

module BoxLayout(plastic_player_box = false) {
  module PlayerBoxTrainsRotated() {
    translate([0, player_box_width, 0]) rotate([0, 0, -90]) PlayerBoxTrains();
  }
  module PlayerBoxSmallRotated() {
    translate([0, player_box_width, 0]) rotate([0, 0, -90]) PlayerBox();
  }
  module PlayerBoxes() {
    translate([0, player_box_width, 0]) rotate([0, 0, -90]) PlayerBox();
    translate([player_box_length, player_box_width, 0]) rotate([0, 0, -90]) PlayerBoxTrains();
  }
  cube([1, box_length, box_height]);
  cube([box_width, box_length, total_board_thickness]);
  translate([0, 0, total_board_thickness]) {
    CardBoxEasternUS();
    translate([eastern_us_card_box_length, 0, 0]) CardBoxAustralia();
    translate([eastern_us_card_box_length + CardBoxWidth(australia_cards), 0, 0]) CardBoxSweden();
    translate([eastern_us_card_box_length + CardBoxWidth(australia_cards) + CardBoxWidth(sweden_cards), 0, 0])
      CardBoxMexico();
    translate(
      [
        eastern_us_card_box_length + CardBoxWidth(australia_cards) + CardBoxWidth(sweden_cards) + CardBoxWidth(mexico_cards),
        0,
        0,
      ]
    ) CardBoxPortugal();
    translate([0, card_box_width, 0]) EmptyCityBox();
    translate([0, card_box_width + empty_city_length, 0]) EmptyCityBox();
    if (plastic_player_box) {
      translate([empty_city_width, card_box_width, 0]) PlayerBoxes();
      translate([empty_city_width, card_box_width + player_box_width, 0]) PlayerBoxes();
      translate([empty_city_width, card_box_width + player_box_width * 2, 0]) PlayerBoxes();
      translate([empty_city_width, card_box_width, player_box_height]) PlayerBoxes();
      translate([empty_city_width, card_box_width + player_box_width, player_box_height]) PlayerBoxes();
      translate([empty_city_width, card_box_width + player_box_width * 2, player_box_height]) PlayerBoxes();
      translate([0, card_box_width + money_section_width, player_box_height * 2]) rotate([0, 0, -90])
          MoneyBox();
      translate([0, card_box_width + money_section_width, player_box_height * 2]) HexBox();
      translate([hex_box_width, card_box_width + money_section_width, player_box_height * 2]) HexBox();
      translate([money_section_length, card_box_width, player_box_height * 2]) NewCityBox();
    } else {

      translate([empty_city_width, card_box_width, 0]) PlayerBoxTrainsRotated();
      translate([empty_city_width, card_box_width + player_box_width, 0]) PlayerBoxTrainsRotated();
      translate([empty_city_width, card_box_width + player_box_width * 2, 0]) PlayerBoxTrainsRotated();
      translate([empty_city_width, card_box_width, player_box_height]) PlayerBoxTrainsRotated();
      translate([empty_city_width, card_box_width + player_box_width, player_box_height])
        PlayerBoxTrainsRotated();
      translate([empty_city_width, card_box_width + player_box_width * 2, player_box_height])
        PlayerBoxTrainsRotated();
      for (i = [0:1:2]) {
        translate([empty_city_width + player_box_trains_length, card_box_width, player_box_small_height * i])
          PlayerBoxSmallRotated();
      }
      for (i = [0:1:2]) {
        translate(
          [
            empty_city_width + player_box_trains_length + player_box_length,
            card_box_width,
            player_box_small_height * i,
          ]
        ) PlayerBoxSmallRotated();
      }
      translate([empty_city_width + player_box_trains_length, card_box_width + player_box_width, 0])
        HexBox(extra_height=hex_box_extra_height);
      translate(
        [
          empty_city_width + player_box_trains_length,
          card_box_width + player_box_width,
          top_section_height + hex_box_extra_height,
        ]
      ) HexBox(extra_height=hex_box_extra_height);
      translate(
        [
          empty_city_width + player_box_trains_length,
          card_box_width + player_box_width,
          top_section_height * 2 + hex_box_extra_height * 2,
        ]
      ) MoneyBox(extra_length=new_city_extra_width, extra_width=new_city_extra_length);
      translate(
        [
          empty_city_width + player_box_trains_length + money_section_width + new_city_box_length + new_city_extra_length * 2,
          card_box_width + player_box_width,
          top_section_height * 2 + hex_box_extra_height * 2,
        ]
      ) rotate([0, 0, 90])
          NewCityBox(extra_length=new_city_extra_length, extra_width=new_city_extra_width);
      translate([0, card_box_width, empty_city_height]) AustraliaBox();
      translate([0, card_box_width + australia_box_length, empty_city_height]) SwedenBox();
      translate(
        [
          empty_city_width + player_box_trains_length,
          card_box_width + player_box_width + money_section_length + new_city_extra_width,
          0,
        ]
      ) SpacerNoPlasticPlayerBoxSide();
      translate(
        [
          empty_city_width + player_box_trains_length + money_section_width + new_city_box_length + new_city_extra_length * 2,
          card_box_width,
          0,
        ]
      ) SpacerNoPlasticPlayerBoxFront();
      translate([australia_box_width, card_box_width, empty_city_height]) SpacerNoPlasticPlayerBoxTop();
    }
  }
}

module PrintLayout(plastic_player_box = false) {
  module PlayerBoxes() {
    PlayerBox(generate_lid=generate_lid);
    translate([0, player_box_length + 10, 0]) PlayerBoxTrains(generate_lid=generate_lid);
    translate([0, player_box_length * 2 + 20, 0]) children();
  }

  module CardBoxes() {
    CardBoxEasternUS(generate_lid=generate_lid);
    translate([0, card_box_width + 10, 0]) {
      CardBoxAustralia(generate_lid=generate_lid);
      translate([0, card_box_width + 10, 0]) {
        CardBoxSweden(generate_lid=generate_lid);
        translate([0, card_box_width + 10, 0]) {
          CardBoxMexico(generate_lid=generate_lid);
          translate([0, card_box_width + 10, 0]) {
            children();
          }
        }
      }
    }
  }

  EmptyCityBox(generate_lid=generate_lid);
  translate([0, empty_city_length + 10, 0]) {
    CardBoxes() {
      if (plastic_player_box) {
        PlayerBoxes() {
          MoneyBox(generate_lid=generate_lid);
          translate([0, money_box_length, 0]) {
            HexBox(generate_lid=generate_lid);
            translate([0, hex_box_length, 0]) {
              NewCityBox(generate_lid=generate_lid);
            }
          }
        }
      } else {

        CardBoxPortugal(generate_lid=generate_lid);
        translate([0, card_box_width + 10, 0]) {

          PlayerBoxTrains(generate_lid=generate_lid);
          translate([0, player_box_length + 10, 9]) {
            PlayerBox(generate_lid=generate_lid);
            translate([0, player_box_length + 10, 0]) {
              HexBox(generate_lid=generate_lid, extra_height=hex_box_extra_height);
              translate([0, hex_box_length + 10, 0]) {
                MoneyBox(
                  generate_lid=generate_lid, extra_length=new_city_extra_width,
                  extra_width=new_city_extra_length
                );
                translate([0, money_section_length + new_city_extra_length + 10]) {
                  NewCityBox(
                    generate_lid=generate_lid, extra_length=new_city_extra_length,
                    extra_width=new_city_extra_width
                  );
                  translate([0, new_city_box_length + new_city_extra_length + 10, 0]) {
                    // Expansions
                    AustraliaBox(generate_lid=generate_lid);
                    translate([0, australia_box_length + 10, 0]) {
                      SwedenBox(generate_lid=generate_lid);
                      translate([0, sweden_box_length + 10, 0]) {
                        // Spacers to fill up the box
                        SpacerNoPlasticPlayerBoxSide();
                        translate([0, spacer_plastic_side_length + 10, 0]) {
                          SpacerNoPlasticPlayerBoxFront();
                          translate(
                            [
                              0,
                              box_length - card_box_width * 2 - spacer_plastic_side_length + 10,
                              0,
                            ]
                          ) {
                            SpacerNoPlasticPlayerBoxTop();
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}

if (FROM_MAKE != 1) {
  PortugeseFlag(100, 3);
}
