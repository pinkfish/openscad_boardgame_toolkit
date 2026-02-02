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

box_length = 303;
box_width = 213;
box_height = 93;

board_thickness = 9;

board_width = 196;

player_board_width = 174;
player_board_length = 269;
player_board_thickness = 15;

binding_ties_width = 97;
binding_ties_length = 270;
binding_ties_thickness = 13.5;

total_thickness = board_thickness + player_board_thickness + binding_ties_thickness;

dice_size = 17;

card_width = 67;
card_length = 90;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

num_thruster_cards = 25;
num_damage_cards = 35;
num_reactor_cards = 30;
num_crew_cards = 20;
num_miss_cards = 15;
num_shield_cards = 25;
num_reference_cards = 10;
num_contract_cards = 40;
num_ship_cards = 37;
num_objective_cards = 23;
num_binding_ties_objective_cards = 10;
num_binding_ties_ship_cards = 10;
num_binding_ties_contract_cards = 10;
num_binding_ties_crew_cards = 10;

card_box_width = default_wall_thickness * 2 + card_length;
card_box_length = default_wall_thickness * 2 + card_width;
thruster_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_thruster_cards + 2;
damage_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_damage_cards + 2;
shield_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_shield_cards + 1.5;
reactor_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_reactor_cards + 0.5;
miss_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_miss_cards + 0.5;
reference_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * num_reference_cards;
crew_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * (num_crew_cards + num_binding_ties_crew_cards) + 1;
contract_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * (num_contract_cards + num_binding_ties_contract_cards) + 1;
ship_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * (num_ship_cards + num_binding_ties_ship_cards) + 1;
objective_card_box_height = default_floor_thickness + default_lid_thickness + single_card_thickness * (num_objective_cards + num_binding_ties_objective_cards) + 1;

module ThrusterCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=thruster_card_box_height,
    lid_on_length=true, material_colour = "yellow"
  ) {
    cube([$inner_width, $inner_length, thruster_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=thruster_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module DamageCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=damage_card_box_height,
    lid_on_length=true, material_colour = "red"
  ) {
    cube([$inner_width, $inner_length, damage_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=damage_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ReactorCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=reactor_card_box_height,
    lid_on_length=true, material_colour = "blue"
  ) {
    cube([$inner_width, $inner_length, reactor_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=reactor_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module MissCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=miss_card_box_height,
    lid_on_length=true, material_colour = "grey"
  ) {
    cube([$inner_width, $inner_length, miss_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=miss_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ShieldCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=shield_card_box_height,
    lid_on_length=true, material_colour = "green"
  ) {
    cube([$inner_width, $inner_length, shield_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=shield_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ReferenceCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=reference_card_box_height,
    lid_on_length=true, material_colour = "white"
  ) {
    cube([$inner_width, $inner_length, reference_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=reference_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module CrewCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=crew_card_box_height,
    lid_on_length=true, material_colour = "orange"
  ) {
    cube([$inner_width, $inner_length, crew_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=crew_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ContractCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=contract_card_box_height,
    lid_on_length=true, material_colour = "purple"
  ) {
    cube([$inner_width, $inner_length, contract_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=contract_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ShipCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=ship_card_box_height,
    lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, ship_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=ship_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module ObjectiveCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=objective_card_box_height,
    lid_on_length=true
  ) {
    cube([$inner_width, $inner_length, objective_card_box_height]);
    translate([0, $inner_length / 2, -2]) {
      FingerHoleBase(
        radius=17, height=objective_card_box_height - default_lid_thickness,
        spin=270
      );
    }
  }
}

module BoxLayout() {
  cube([box_length, box_width, 0.1]);
  cube([box_length, 0.1, box_height]);
  translate([0, 0, board_thickness + player_board_thickness]) {
    ThrusterCardBox();
    translate([0, 0, thruster_card_box_height]) {
      DamageCardBox();
      translate([0, 0, damage_card_box_height]) {
        ShieldCardBox();
      }
    }
    translate([card_box_width, 0, 0]) {
      ReactorCardBox();
      translate([0, 0, reactor_card_box_height]) {
        MissCardBox();
        translate([0, 0, miss_card_box_height]) {
          CrewCardBox();
          translate([0, 0, crew_card_box_height]) {
            ReferenceCardBox();
          }
        }
      }
    }
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
