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

default_label_solid_background = MAKE_MMU == 1;

num_investigator_cards = 34;

card_width = 66;
card_length = 91;

ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

card_box_width = card_length + default_wall_thickness * 2 + 1;
card_box_height = card_width + default_lid_thickness + default_floor_thickness + 1;

function CardBoxWidth(num_cards) = num_cards * single_card_thickness + default_wall_thickness * 2;

module CardBox(num_cards, text_str, generate_lid = true)
{
    card_box_length = CardBoxWidth(num_cards);
    translate([ card_box_length, 0, 0 ]) rotate([ 0, 0, 90 ])
    {
        MakeBoxWithSlidingLid(width = card_box_width, length = card_box_length, height = card_box_height,
                              lid_thickness = default_lid_thickness, wall_thickness = default_wall_thickness,
                              lid_on_length = true)
        {
            cube([ $inner_width, $inner_length, $inner_height + 1 ]);
            translate(
                [ card_box_width / 2, card_box_length / 2, $inner_height - 23.5 + 0.01 - default_lid_thickness / 2 ])
                FingerHoleWall(radius = 25, height = 28, depth_of_hole = card_box_width + 2, orient = UP,
                               rounding_radius = 5);
        }
    }
}

module InspectorCardBox() // `make` me
{
    CardBox(num_investigator_cards + 2);
}

module AgnesBakerLid() // `make` me
{
    card_box_length = CardBoxWidth(num_investigator_cards + 2);

    SlidingBoxLidWithLabel(width = card_box_width, length = card_box_length, 
                           text_str = "Agnes", lid_on_length = true, wall_thickness = default_wall_thickness);
}

module RolandBanksLid() // `make` me
{
    card_box_length = CardBoxWidth(num_investigator_cards + 2);

    SlidingBoxLidWithLabel(width = card_box_width, length = card_box_length, 
                           text_str = "Roland", lid_on_length = true, wall_thickness = default_wall_thickness);
}

module DaisyWalkerLid() // `make` me
{
    card_box_length = CardBoxWidth(num_investigator_cards + 2);

    SlidingBoxLidWithLabel(width = card_box_width, length = card_box_length, 
                           text_str = "Daisy", lid_on_length = true, wall_thickness = default_wall_thickness);
}

module SkidsOTooleLid() // `make` me
{
    card_box_length = CardBoxWidth(num_investigator_cards + 2);

    SlidingBoxLidWithLabel(width = card_box_width, length = card_box_length, 
                           text_str = "Skids", lid_on_length = true, wall_thickness = default_wall_thickness);
}

module WendyAdamsLid() // `make` me
{
    card_box_length = CardBoxWidth(num_investigator_cards + 2);

    SlidingBoxLidWithLabel(width = card_box_width, length = card_box_length,
                           text_str = "Wendy", lid_on_length = true, wall_thickness = default_wall_thickness);
}

module BoxLayout()
{
    cube([ 1, box_length, box_height ]);
    cube([ box_width, box_length, 1 ]);
    InspectorCardBox();
    translate([ CardBoxWidth(num_investigator_cards + 2), 0, 0 ]) InspectorCardBox();
    translate([ CardBoxWidth(num_investigator_cards + 2) * 2, 0, 0 ]) InspectorCardBox();
    translate([ CardBoxWidth(num_investigator_cards + 2) * 3, 0, 0 ]) InspectorCardBox();
    translate([ CardBoxWidth(num_investigator_cards + 2) * 4, 0, 0 ]) InspectorCardBox();
}

if (FROM_MAKE != 1)
{
    BoxLayout();
}