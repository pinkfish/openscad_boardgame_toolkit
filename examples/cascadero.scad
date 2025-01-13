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

box_length = 304;
box_width = 212;
box_height = 40;
lid_thickness = 3;
wall_thickness = 2;

generate_mmu = MMU == 1;

default_solid_label_background = generate_mmu;
default_lid_shape_type = SHAPE_TYPE_DENSE_HEX;

side_width = 2;
gap = 2;

boards_height = 10;

section_height = box_height - boards_height - 4;
player_width = (box_width - gap) / 2;
player_length = player_width;
player_section_width = 40;
lid_boundary = 7;

top_width = ((box_width - gap) - 40) / 2;
top_length = top_width;
herald_width = 40;

$fn = 180;

first_width = 40;
radius = 10;

module SealsBox() // `make` me
{
    MakeBoxWithSlidingLid(width = top_width, length = top_length, height = section_height)
    {
        RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = top_width - wall_thickness * 2,
                           height = section_height, radius = 15);
    }
    translate([ top_width + 10, 0, 0 ]) SlidingLid(top_width, top_length)
        SlidingBoxLidWithLabel(top_width, top_length, lid_thickness = lid_thickness, text_width = 60, text_height = 20,
                               text_str = "Seals", label_colour = "blue", label_radius = 5);
}

module FarmerBox() // `make` me
{
    MakeBoxWithSlidingLid(width = top_width, length = top_length, height = section_height)
    {
        RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = top_width - wall_thickness * 2,
                           height = section_height, radius = 15);
    }
    translate([ top_width + 10, 0, 0 ])
        SlidingBoxLidWithLabel(herald_width, top_length, lid_thickness = lid_thickness, text_width = 60,
                               text_height = 20, text_str = "Farmer", label_colour = "blue", label_radius = 5);
}

module HeraldBox() // `make` me
{
    MakeBoxWithSlidingLid(width = herald_width, length = top_length, height = section_height)
    {
        RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = herald_width - wall_thickness * 2,
                           height = section_height, radius = 15);
    }
    translate([ herald_width + 10, 0, 0 ]) SlidingLid(herald_width, top_length)
        SlidingBoxLidWithLabel(herald_width, top_length, lid_thickness = lid_thickness, text_width = 60,
                               text_height = 20, text_str = "Herald", label_colour = "blue", label_radius = 5);
}

module PlayerBox() // `make` me
{
    MakeBoxWithSlidingLid(width = player_width, length = player_length, height = section_height)
    {

        RoundedBoxGrid(width = $inner_width, length = first_width, height = section_height, radius = radius, rows = 2,
                       cols = 1, all_sides = true);
        translate([ 0, first_width + wall_thickness, 0 ]) RoundedBoxAllSides(
            width = $inner_width, length = $inner_length - first_width, height = section_height, radius = radius);
    }
    translate([ player_width + 10, 0, 0 ])
        SlidingBoxLidWithLabel(player_width, player_width, lid_thickness = lid_thickness, text_width = 60,
                               text_height = 20, text_str = "Player", label_colour = "blue", label_radius = 5);
}

if (FROM_MAKE != 1)
{
    //    BoxLayout();

    SealsBox();

    translate([ 0, 100, 0 ]) FarmerBox();

    translate([ 0, 200, 0 ]) HeraldBox();

    translate([ 0, 300, 0 ]) PlayerBox();
}