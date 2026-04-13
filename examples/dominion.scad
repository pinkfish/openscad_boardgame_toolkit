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

include <card_library.scad>

dominion_big_box_width = 470;
dominion_big_box_length = 290;
dominion_big_box_height = 90;

card_length = 93;
card_width = 62;
card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;

function sumVec(vec, index = 0, sum = 0) =
  index >= len(vec) ?
    sum
  : sumVec(vec, index + 1, sum + vec[index]);

function SleeveSizeWidth(num_cards) = single_card_thickness * num_cards + default_wall_thickness + 0.5;

function SleeveSize(num_cards) =
  [
    card_length + default_wall_thickness * 1.5,
    SleeveSizeWidth(num_cards),
    card_width + default_wall_thickness,
  ];

function CardLibrarySize(array) =
  [
    card_length + default_wall_thickness * 4,
    sumVec([for (x = array) SleeveSizeWidth(x[1])]) + default_wall_thickness * 2,
    card_width + default_wall_thickness * 2 + default_lid_thickness + default_floor_thickness,
  ];

base_game_cards_v2 = [
  ["Artisan", 10],
  ["Bandit", 10],
  ["Bureaucrat", 10],
  ["Cellar", 10],
  ["Chapel", 10],
  ["Council Room", 10],
  ["Festival", 10],
  ["Gardens", 10],
  ["Harbinger", 10],
  ["Laboratory", 10],
  ["Library", 10],
  ["Market", 10],
  ["Merchant", 10],
  ["Militia", 10],
  ["Mine", 10],
  ["Moat", 10],
  ["Moneylender", 10],
  ["Poacher", 10],
  ["Remodel", 10],
  ["Sentry", 10],
  ["Smithy", 10],
  ["Throne Room", 10],
  ["Village", 10],
  ["Vassal", 10],
  ["Witch", 10],
  ["Workshop", 10],
];

base_game_cards_v1 = [
  ["Adventurer", 10],
  ["Bureaucrat", 10],
  ["Cellar", 10],
  ["Chancellor", 10],
  ["Chapel", 10],
  ["Council Room", 10],
  ["Feast", 10],
  ["Festival", 10],
  ["Gardens", 10],
  ["Laboratory", 10],
  ["Library", 10],
  ["Market", 10],
  ["Militia", 10],
  ["Mine", 10],
  ["Moat", 10],
  ["Moneylender", 10],
  ["Remodel", 10],
  ["Smithy", 10],
  ["Spy", 10],
  ["Thief", 10],
  ["Throne Room", 10],
  ["Village", 10],
  ["Witch", 10],
  ["Workshop", 10],
  ["Woodcutter", 10],
];

alchemy_game_cards = [
  ["Alchemist", 10],
  ["Apothecary", 10],
  ["Apprentice", 10],
  ["Famililiar", 10],
  ["Golem", 10],
  ["Herbalist", 10],
  ["Philosophers Stone", 10],
  ["Possession", 10],
  ["Scrying Pool", 10],
  ["Transmute", 10],
  ["University", 10],
  ["Vineyards", 10],
];

money_victory_cards = [
  ["Potion", 16, "potion_svg"],
  ["Gold", 60, "gold_svg"],
  ["Silver", 40, "silver_svg"],
  ["Copper", 30, "copper_svg"],
  ["Platinum", 12, "platinum_svg"],
  ["Estate", 12, "estate_svg"],
  ["Colony", 12, "colony_svg"],
  ["Province", 12, "province_svg"],
  ["Dutchy", 12, "dutchy_svg"],
  ["Curse", 30],
];

prosperity_game_cards = [
    
];

module RenderSvg(svg) {
  color("aqua")
    translate([12, $inner_length / 2, -0.2])
      mirror([0, 1, 0])
        linear_extrude(h=0.5) {
          if (svg == "potion_svg") {
            resize([9, 0], auto=true)
              PotionLogo();
          }
          if (svg == "gold_svg") {
            resize([9, 0], auto=true)
              MoneyLogo();
            rotate(270)
              text("3", size=4, halign="center", valign="center");
          }
          if (svg == "silver_svg") {
            resize([9, 0], auto=true)
              MoneyLogo();
            rotate(270)
              text("2", size=4, halign="center", valign="center");
          }
          if (svg == "copper_svg") {
            resize([9, 0], auto=true)
              MoneyLogo();
            rotate(270)
              text("1", size=4, halign="center", valign="center");
          }
          if (svg == "platinum_svg") {
            resize([9, 0], auto=true)
              MoneyLogo();
            rotate(270)
              text("6", size=4, halign="center", valign="center");
          }
          if (svg == "estate_svg") {
            resize([9, 0], auto=true)
              ShieldLogo();
            rotate(270)
              text("1", size=4, halign="center", valign="center");
          }
          if (svg == "dutchy_svg") {
            resize([9, 0], auto=true)
              ShieldLogo();
            rotate(270)
              text("3", size=4, halign="center", valign="center");
          }
          if (svg == "province_svg") {
            resize([9, 0], auto=true)
              ShieldLogo();
            rotate(270)
              text("6", size=4, halign="center", valign="center");
          }
          if (svg == "colony_svg") {
            resize([9, 0], auto=true)
              ShieldLogo();
            rotate(270)
              text("10", size=4, halign="center", valign="center");
          }
        }
}

module MoneyVictoryCardSleeve(label) {
  CardSleeveForLibrary(
    size=money_victory_card_box_size, label=label, add_positive=true,
    text_length_offset=18, emboss_text=0.3
  ) {
    color("aqua")
      translate([13, $inner_length / 2, 0])
        linear_extrude(h=0.5)
          resize([8, 8])
            BaseSetV1Logo();
  }
}

module InternalSleeves(card_array, spacing = 2) {
  sleeve_sizes = [for (x = card_array) SleeveSize(x[1])];
  for (i = [0:len(card_array) - 1]) {
    translate([0, sumVec([for (x = [0:i - 1]) sleeve_sizes[x][1] + spacing]), 0])
      CardSleeveForLibrary(
        size=sleeve_sizes[i], label=card_array[i][0], add_positive=true,
        text_length_offset=18, emboss_text=0.3
      ) if (len(card_array[i]) > 2 && card_array[i][2] != "")
        RenderSvg(card_array[i][2]);
      else
        children(0);
  }
}

module DominionBaseGamev2Sleeves(spacing = 2) // `make` me
{
  InternalSleeves(base_game_cards_v2, spacing) {
    color("aqua")
      translate([12, $inner_length / 2, 0])
        linear_extrude(h=0.5)
          resize([9, 0], auto=true)
            BaseSetV2Logo();
  }
}

module DominionBaseGamev1Sleeves(spacing = 2) // `make` me
{
  InternalSleeves(base_game_cards_v1, spacing) {
    color("aqua")
      translate([12, $inner_length / 2, 0])
        linear_extrude(h=0.5)
          resize([9, 0], auto=true)
            BaseSetV1Logo();
  }
}

module MoneyVictoryGamev1Sleeves(spacing = 2) // `make` me
{
  InternalSleeves(money_victory_cards, spacing) {
    color("aqua")
      translate([12, $inner_length / 2, 0])
        linear_extrude(h=0.5)
          resize([9, 0], auto=true)
            MoneyLogo();
  }
}

module AlchemcyGameSleeves(spacing = 2) // `make` me
{
  InternalSleeves(alchemy_game_cards, spacing) {
    color("aqua")
      translate([12, $inner_length / 2, 0])
        linear_extrude(h=0.5)
          resize([9, 0], auto=true)
            PotionLogo();
  }
}

module DominionLibraryBoxInternal(card_array) {
  box_size = CardLibrarySize(card_array);

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
  Logos()
    children(0);
}

module BaseGameDominionv1LibraryBox() // `make` me
{
  DominionLibraryBoxInternal(base_game_cards_v1)
    BaseSetV1Logo();
}

module BaseGameDominionv2LibraryBox() // `make` me
{
  DominionLibraryBoxInternal(base_game_cards_v2)
    BaseSetV1Logo();
}

module MoneyVictoryDominionLibraryBox() // `make` me
{
  DominionLibraryBoxInternal(money_victory_cards)
    MoneyLogo();
}

module AlchemyDominionLibraryBox() // `make` me
{
  DominionLibraryBoxInternal(alchemy_game_cards)
    PotionLogo();
}

module DominionLidInternal(card_array) {
  CardLibraryBoxLidWithShape(size=CardLibrarySize(card_array))
    translate([$inner_width / 2, $inner_length / 2, 0]) {
      union() {
        color("black")
          linear_extrude(h=0.2)
            rotate(90)
              mirror([1, 0])
                DominionLogo();
        color("magenta")
          translate([0, 0, 0.2])
            linear_extrude(h=default_lid_thickness - 0.2)
              rotate(90)
                mirror([1, 0])
                  DominionLogo();
        translate([27, 0, 0]) {
          color("black")
            linear_extrude(h=0.2)
              resize([20, 20])
                children(0);

          color("magenta")
            translate([0, 0, 0.2]) {
              linear_extrude(h=default_lid_thickness - 0.2)
                fill() {
                  resize([20, 20])
                    children(0);
                }
            }
        }
      }
    }
}

module DominionV2Lid() // `make` me
{
  DominionLidInternal(base_game_cards_v2)
    BaseSetV2Logo(angle=90);
}

module DominionV1Lid() // `make` me
{
  DominionLidInternal(base_game_cards_v1)
    BaseSetV1Logo(angle=90);
}

module BoxLayout() {
  cube([dominion_big_box_width, dominion_big_box_length, 1]);
  cube([1, dominion_big_box_length, dominion_big_box_height]);

  base = CardLibrarySize(base_game_cards_v1);
  money_victory = CardLibrarySize(money_victory_cards);
  BaseGameDominionv1LibraryBox();
  translate([default_wall_thickness, default_wall_thickness, default_wall_thickness])
    DominionBaseGamev1Sleeves(spacing=0);
  translate([base[0], 0, 0]) {
    MoneyVictoryDominionLibraryBox();
    translate([default_wall_thickness, default_wall_thickness, default_wall_thickness])
      MoneyVictoryGamev1Sleeves(spacing=0);
    translate([0, money_victory[1] + 1, 0])
      AlchemyDominionLibraryBox();
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
  /*
  AlchemyDominionLibraryBox();
    translate([default_wall_thickness, default_wall_thickness, default_wall_thickness])
      AlchemcyGameSleeves(spacing=0);
      */
}
