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

box_width = 242;
box_length = 283;
box_height = 75;

default_lid_thickness = 3;
default_wall_thickness = 3;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_lid_shape_type = SHAPE_TYPE_VORONOI;

card_10_thickness = 16 / 3;
single_card_thickness = card_10_thickness / 10;
card_size = MakeCardSize(length=92, width=66, single_card_thickness=single_card_thickness, sleeve_wall_thickness=0.75);

num_investigator_cards = 34;

card_width = 66;
card_length = 91;

card_box_width = card_length + default_wall_thickness * 2 + 1;
card_box_height = card_width + default_lid_thickness + default_floor_thickness + 1;

core_player_cards = [
  ["Agnes Baker", 34, "per_investigator"],
  ["Roland Banks", 34, "per_investigator"],
  ["Daisy Walker", 34, "per_investigator"],
  ["Skids O'Toole", 34, "per_investigator"],
  ["Wendy Adams", 34, "per_investigator"],

  ["Level 0", 15, "s_level_0"],

  ["Guardian 1+", 12, "guardian"],
  ["Survivor 1+", 12, "survivor"],
  ["Rogue 1+", 12, "rogue"],
  ["Seeker 1+", 12, "seeker"],
  ["Mystic 1+", 12, "mystic"],
  ["Neutral 1+", 10, "neutral"],
  ["Weaknesses", 10, "weakness"],
];

core_scenario_cards = [
  ["The Gathering", 16, "the_gathering"],
  ["The Midnight Masks", 20, "midnight_masks"],
  ["The Devourer Below", 18, "the_devourer_below"],
  ["Chilling Cold", [4, 4], ["chilling_cold", "nightgaunts"]],
  ["Cultists", [5, 5], ["dark_cult", "cult_of_umordoth"]],
  ["Ancient Evils", [4, 4], ["ancient_evils", "striking_fear"]],
  ["Ghouls", 7, "ghouls"],
  ["Agents", [4, 4, 4, 4], ["agents_of_yog", "agents_of_cthulhu", "agents_of_shub", "agents_of_hastur"]],
  ["Rats & Doors", [4, 4], ["rats", "locked_doors"]],
];

//echo(sumVec([for (i = core_scenario_cards) (i[1])]));

module ArkhamHorrorBaseLogo() {
  import("svg/arkham_horror/icons/core.svg", center=true);
}

module RenderSvg(svg_icon, width) {
  if (is_list(svg_icon) && len(svg_icon) > 0) {
    left(2) {
      for (i = [0:len(svg_icon) - 1]) {
        right(i * 6)
          RenderSvg(svg_icon[i], width);
      }
    }
  } else {
    resize(
      svg_icon == "the_gathering" || svg_icon == "ghouls" || svg_icon == "the_devourer_below" ? [width, 0] : [0, width],
      auto=true
    )
      rotate(270)
        import(str("svg/arkham_horror/icons/", svg_icon, ".svg"), center=true);
  }
}

module ArkhamHorrorTCGInnerBox(card_array) {
  box_size = CardLibrarySize(card_array, card_size);

  module Logos() {
    translate([box_size[0] / 2, -0.3, box_size[2] / 2])
      rotate([90, 270, 0])
        color("aqua")
          linear_extrude(h=0.5)
            resize([30, 0], auto=true)
              children(0);
    translate([box_size[0] / 2, box_size[1] + 0.2, box_size[2] / 2])
      rotate([90, 270, 0])
        color("aqua")
          linear_extrude(h=0.5)
            resize([30, 0], auto=true)
              children(0);
  }
  difference() {
    MakeCardLibraryBox(size=box_size)
      Logos()
        children(0);
  }
}

module InternalSleeves(card_array, spacing = 2) {
  MakeAllSleeves(card_array, spacing, card_size) {
    if ($inner_2d != undef) {
      color("aqua")
        translate([12, $inner_length / 2, -0.2])
          linear_extrude(h=0.5)
            RenderSvg($inner_2d, width=min($inner_length - 1.5, 7));
    } else {
      color("aqua")
        translate([12, $inner_length / 2, -0.2])
          linear_extrude(h=0.5)
            resize([min($inner_length - 1.5, 7), 0], auto=true)
              children(0);
    }
  }
}

module ArkhamHorronCoreGameBox() // `make` me
{
  ArkhamHorrorTCGInnerBox(core_player_cards) {
    ArkhamHorrorBaseLogo();
  }
}

module ArkhamHorrorCoreGameSleeves(spacing = 2) // `make` me
{
  InternalSleeves(core_player_cards, spacing) {
    ArkhamHorrorBaseLogo();
  }
}

module ArkhamHorrorCoreEncounterBox() // `make` me
{
  ArkhamHorrorTCGInnerBox(core_scenario_cards) {
    ArkhamHorrorBaseLogo();
  }
}

module ArkhamHorrorCoreEncounterSleeves(spacing = 2) // `make` me
{
  InternalSleeves(core_scenario_cards, spacing) {
    ArkhamHorrorBaseLogo();
  }
}

module ArkhamHorrorCoreGameBoxLid() // `make` me
{
  CardLibraryBoxLidWithLabel(size=CardLibrarySize(core_player_cards, card_size), label="Core Set", material_colour="blue");
}

module ArkhamHorrorCoreEncounterBoxLid() // `make` me
{
  CardLibraryBoxLidWithLabel(size=CardLibrarySize(core_scenario_cards, card_size), label="Core Campaign", material_colour="blue");
}

module BoxLayout() {
  cube([1, box_length, box_height]);
  cube([box_width, box_length, 1]);
  core_box_size = CardLibrarySize(core_player_cards, card_size);
  echo("core_box_size = ", core_box_size);
  translate([0, 0, 0])
    ArkhamHorronCoreGameBox();
  translate([0, core_box_size[1], 0])
    ArkhamHorrorCoreEncounterBox();
}

module DoThing(width, length, height, wall_thickness = default_wall_thickness) {
  rotate([90, 0, 0]) color(material_colour) cuboid(
        [width, height, length + 0.02],
        anchor=TOP + FRONT + LEFT,
        rounding=min(-wall_thickness, length / 2, width / 2)
      );
  rounding = min(-wall_thickness, length / 2, width / 2);
  translate([width / 2, length, height / 2])
    rotate([90, 0, 0])
      offset_sweep(
        round_corners(rect([width, height]), r=wall_thickness * 2), bottom=os_circle(r=rounding), top=os_circle(r=rounding)
      );
}

if (FROM_MAKE != 1) {
  size = CardLibrarySize(core_scenario_cards, card_size);
  ArkhamHorrorCoreEncounterBox();
  up(size[2])
    zflip()
      ArkhamHorrorCoreEncounterBoxLid();
}
