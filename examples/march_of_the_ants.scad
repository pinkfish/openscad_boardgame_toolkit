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

box_width = 195;
box_length = 275;
box_height = 65;

thickness_to_stuff = 6;
march_of_the_ants_boards_rules_thickness = 3;
score_track_length = 210;
score_track_width = 98;
helper_cardc_length = 162;
helper_cardc_width = 106;
helper_card_total_thickness = 2.5;
helper_card_num = 5;
score_card_thickness = helper_card_total_thickness / helper_card_num;

tile_thickness = 2;
tile_width = 84;
tile_radius = tile_width / 2 / cos(180 / 6);
tile_num_start = 8;
tile_num_standard = 17;

food_token_diameter = 14;
food_token_num = 30;
food_token_thickness = 3.5;

player_token_diameter = 15;
player_token_thickness = 3.5;
player_cube = 9;
player_cube_num = 36;

centipede_token_diameter = 26;
centipede_token_num = 15;

day_night_token = 37;

leaf_len = 38; // active player.
leaf_width = 22.42;

sleeved_card_width = 66;
sleeved_card_length = 91;
twenty_sleeved_cards_thickness = 8.5;
total_cards = 66;

// Minions of the meadow expansion
major_worker_token_diameter = 24;
flood_token_diameter = 16;
aphid_diameter = 9;
aphid_length = 10.5;
aphid_bump_width = 3;
aphid_thickness = 9;
plastic_clip_width = 9;
plastic_clip_length = 22;
plastic_clip_height = 5.5;
major_worker_width = 10;
major_worker_len = 14.5;

num_mm_cards = 36 + 5 + 8;
num_major_workers = 10;
num_aphids = 36;
aphix_hexes = 4;
empress_hex = 1;
spring_hex = 1;
num_mm_hex = spring_hex + empress_hex + aphix_hexes;
num_symboite = 15;
num_predator_meeples = 5;
num_flood_tokens = 9;

wall_thickness = 3;
lid_thickness = 2;

tile_box_length = (tile_radius * 2 + 0.5) + wall_thickness * 2;
tile_box_width = box_width - 1;
tile_box_height = box_height - thickness_to_stuff;

card_box_length = sleeved_card_length + wall_thickness * 2 + 1;
card_box_width = sleeved_card_width + 1 + wall_thickness * 2;
card_box_height = twenty_sleeved_cards_thickness * (total_cards) / 20 + lid_thickness * 2 + 1;
minions_of_the_meadow_card_box_height = twenty_sleeved_cards_thickness * (num_mm_cards) / 20 + lid_thickness * 2 + 0.75;

minions_of_the_meadow_box_length = card_box_length;
minions_of_the_meadow_box_width = box_width - card_box_width - 1;
minions_of_the_meadow_box_height = tile_thickness * num_mm_hex + lid_thickness * 2;

food_token_box_width = minions_of_the_meadow_box_width;
food_token_box_length = minions_of_the_meadow_box_length;
food_token_box_height = food_token_num / 6 * food_token_thickness + wall_thickness * 2;

aphid_box_height = tile_box_height - food_token_box_height - minions_of_the_meadow_box_height;
aphid_box_length = food_token_box_length;
aphid_box_width = food_token_box_width;

player_box_length = box_length - tile_box_length - card_box_length - 1;
player_box_width = (box_width - 1) / 2;
player_box_height = tile_box_height / 3;

predator_box_height = box_height - food_token_box_height - minions_of_the_meadow_box_height - thickness_to_stuff - 1;
predator_box_width = minions_of_the_meadow_box_width;
predator_box_length = minions_of_the_meadow_box_length;

echo([
    tile_thickness * (tile_num_standard + tile_num_start) + 4, tile_box_height, food_token_box_width, aphid_box_height,
    box_height - thickness_to_stuff, (num_mm_cards + total_cards) * twenty_sleeved_cards_thickness / 20, predator_box_height
]);

module GreatTunnel()
{
    apothem = tile_width / 2;
    radius = tile_radius;
    dy = 0.75 * (radius + radius);

    rotate([ 0, 0, -30 ]) translate([ -dy / 2, -apothem / 2, 0 ])
    {
        RegularPolygon(width = tile_width + 0.5, height = tile_thickness, shape_edges = 6);
        translate([ dy, apothem, 0 ])
            RegularPolygon(width = tile_width + 0.5, height = tile_thickness, shape_edges = 6);
        translate([ 0, apothem * 2, 0 ])
            RegularPolygon(width = tile_width + 0.5, height = tile_thickness, shape_edges = 6);
        translate([ dy, -apothem, 0 ])
            RegularPolygon(width = tile_width + 0.5, height = tile_thickness, shape_edges = 6);
    }
}

module LeafOutline()
{
    resize([ leaf_len, leaf_width ]) import("svg/mota - leaf.svg");
}

module MajorWorkerOutline()
{
    resize([ major_worker_width, major_worker_len ]) import("svg/mota - major worker.svg");
}

module TileBox()
{
    MakeBoxWithCapLid(width = tile_box_width, length = tile_box_length, height = tile_box_height,
                      wall_thickness = wall_thickness)
    {
        translate([ 8, 0, 0 ])
        {
            translate([ tile_width / 2, tile_radius, 0 ]) rotate([ 0, 0, 30 ])
                RegularPolygon(width = tile_width + 0.5, height = tile_box_height, shape_edges = 6);
            translate([ tile_width / 2 + tile_width / 4, tile_radius + tile_radius * 3 / 4, 0 ])
            {
                cyl(r = 13, h = tile_box_height + 12, anchor = BOTTOM, rounding = 6);
            }
            translate([ tile_width / 4, tile_radius / 4, 0 ])
                cyl(r = 13, h = tile_box_height + 12, anchor = BOTTOM, rounding = 6);
            translate([ tile_width * 3 / 2 + 3, tile_radius, 0 ])
            {
                rotate([ 0, 0, 30 ])
                    RegularPolygon(width = tile_width + 0.5, height = tile_box_height, shape_edges = 6);
                translate([ tile_width / 4, tile_radius * 3 / 4, 0 ])
                {
                    cyl(r = 13, h = tile_box_height + 12, anchor = BOTTOM, rounding = 6);
                }
                translate([ tile_width / 4 - tile_width / 2, tile_radius * 1 / 4 - tile_radius, 0 ])
                    cyl(r = 13, h = tile_box_height + 12, anchor = BOTTOM, rounding = 6);
            }

            translate([ tile_width - 14, tile_radius * 4 / 7, -8 ])
                cuboid([ 30, tile_width / 2, tile_box_height + 20 ], anchor = BOTTOM + FRONT + LEFT, rounding = 5);
        }
    }
}

module FoodTokenBox()
{
    centipede_height = tile_thickness * (centipede_token_num / 3) + 1;

    module Centipede()
    {
        for (i = [0:1:2])
        {
            translate([
                centipede_token_diameter / 2, centipede_token_diameter / 2 + 1 + i * (centipede_token_diameter + 7), 0
            ])
            {
                translate([ 0, 0, food_token_box_height - centipede_height - 3.1 ])
                    cyl(d = centipede_token_diameter, h = centipede_height, anchor = BOTTOM);
                translate([ centipede_token_diameter / 2, 0, food_token_box_height - centipede_height - 3 ])
                    cyl(d = 15, h = 15, anchor = BOTTOM, rounding = 4);
            }
        }
        translate([
            food_token_box_length - wall_thickness * 2 - centipede_token_diameter / 2 + 2, 20,
            food_token_box_height - tile_thickness - 2.5
        ])
        {
            cyl(d = day_night_token, h = tile_thickness + 1);
            translate([ 0, day_night_token / 2, 18.4 ]) sphere(r = 20);
        }
        translate([ 55, 53, food_token_box_height - tile_thickness - lid_thickness * 2 ]) rotate([ 0, 0, 70 ])
            linear_extrude(height = 20) offset(delta = 0.5) LeafOutline();
        translate([ 55, 53, food_token_box_height - tile_thickness - lid_thickness * 2 + 1.5 ])
            translate([ 0, day_night_token / 2, 18.4 ]) sphere(r = 20);
    }
    food_token_per_hole_top_height = 3 * food_token_thickness + 0.5;
    food_token_per_hole_bottom_height = 2 * food_token_thickness + 0.5;
    MakeBoxWithCapLid(food_token_box_width, food_token_box_length, food_token_box_height)
    {
        for (i = [0:1:5])
        {
            translate([
                food_token_diameter / 2, food_token_diameter / 2 + 1 + i * (food_token_diameter + 1.5),
                food_token_box_height - lid_thickness * 2 -
                food_token_per_hole_top_height
            ])
            {
                cyl(d = food_token_diameter, h = food_token_per_hole_top_height + 1, anchor = BOTTOM);
                // translate([ 10, 0, 0 ]) cyl(d = 10, h = food_token_box_height + 4, anchor = BOTTOM, rounding = 4);
                difference()
                {
                    translate([ 4.1, 0, 0 ]) xcyl(d = food_token_diameter, anchor = BOTTOM, h = 20);
                    translate([ 19, 0, 0 ]) cyl(d = food_token_diameter, h = 4, anchor = BOTTOM);
                }
            }
            translate([
                food_token_diameter / 2 + food_token_diameter + 5,
                food_token_diameter / 2 + 1 + i * (food_token_diameter + 1.5),
                food_token_box_height - lid_thickness * 2 -
                food_token_per_hole_bottom_height
            ])
            {
                cyl(d = food_token_diameter, h = food_token_per_hole_bottom_height + 1, anchor = BOTTOM);
            }
        }
        translate([ 40, 0, 0 ]) Centipede();
    }
}

module CardBox()
{
    MakeBoxWithCapLid(card_box_width, card_box_length, card_box_height)
    {
        translate([ 1.5, 1.5, 0 ]) cube([ sleeved_card_width, sleeved_card_length, card_box_height ]);
        translate([ sleeved_card_width / 2 - 10, 0, card_box_height - 40 ]) FingerHoleBase(radius = 15, height = 40);
    }
}

module MinionsOfTheMeadowCardBox()
{
    MakeBoxWithCapLid(card_box_width, card_box_length, minions_of_the_meadow_card_box_height)
    {
        translate([ 1.5, 1.5, 0 ])
            cube([ sleeved_card_width, sleeved_card_length, minions_of_the_meadow_card_box_height ]);
        translate([ sleeved_card_width / 2 - 10, 0, minions_of_the_meadow_card_box_height - 40 ])
            FingerHoleBase(radius = 15, height = 40);
    }
}

module Aphid(h = aphid_thickness)
{
    cyl(d = aphid_diameter, h = h, anchor = BOTTOM);
    translate([ 0, aphid_length - aphid_diameter, 0 ])
        cuboid([ aphid_bump_width, aphid_length / 2, h ], anchor = BOTTOM + FRONT, rounding = 1.5,
               edges = [ BACK + LEFT, BACK + RIGHT ]);
}

module AphidBox()
{
    MakeBoxWithCapLid(player_box_width, player_box_length, player_box_height, lid_thickness = wall_thickness,
                      floor_thickness = wall_thickness)
    {
        // cube([ player_box_width - wall_thickness * 2, player_box_length - wall_thickness * 2, player_box_height ]);
        for (j = [0:1:3])
        {
            for (i = [0:1:8])
            {
                translate([
                    5 + (aphid_diameter + 1.3) * i, 13 + j * (aphid_length + 3),
                    player_box_height - wall_thickness * 2 - aphid_thickness - 0.5
                ]) Aphid(h = aphid_thickness + 1);
            }
        }
        translate([ 0.5, 13 - aphid_length / 2 - 2, player_box_height - wall_thickness * 2 - 3 ])
            cuboid([ (aphid_diameter + 1.3) * 9, 4 * (aphid_length + 3) + 4, 10 ], anchor = BOTTOM + FRONT + LEFT,
                   rounding = 5, edges = [ FRONT + BOTTOM, BACK + BOTTOM ]);
    }
}

module MinionsOfTheMeadowBox()
{
    MakeBoxWithCapLid(minions_of_the_meadow_box_width, minions_of_the_meadow_box_length,
                      minions_of_the_meadow_box_height, wall_thickness = wall_thickness)
    {
        translate([ 9, 0, 0 ])
        {
            translate([ tile_radius, tile_width / 2 + 4, 0 ]) rotate([ 0, 0, 30 ]) rotate([ 0, 0, 90 ])
                RegularPolygon(width = tile_width + 0.5, height = tile_box_height, shape_edges = 6);
            translate([ tile_radius + tile_radius * 3 / 4, tile_width / 2 + tile_width / 4 + 4, tile_thickness * 6 ])
                sphere(r = tile_thickness * num_mm_hex);
            translate([ tile_radius / 4, tile_width / 4 + 4, tile_thickness * 6 ])
                sphere(r = tile_thickness * num_mm_hex);
        }
    }
}

module PlayerBox()
{
    MakeBoxWithCapLid(player_box_width, player_box_length, player_box_height, wall_thickness = wall_thickness,
                      lid_thickness = lid_thickness)
    {
        translate([ 0, 0, player_box_height - lid_thickness * 2 - player_cube ])
            cube([ player_cube * 10 + 1, player_cube * 3 + 1, player_cube + 1 ]);
        translate([ player_cube * 2, player_cube * 3 + 0.5, player_box_height - lid_thickness * 2 - player_cube ])
            cube([ player_cube * 6 + 1, player_cube + 1, player_cube + 1 ]);
        translate([
            player_token_diameter / 2, player_cube * 4 + 0.5, player_box_height - lid_thickness * 2 -
            player_token_thickness
        ])
        {
            cylinder(d = player_token_diameter, h = player_token_thickness, anchor = BOTTOM);
            translate([ player_token_diameter / 4 + 1.5, player_token_diameter / 4 + 1.5, 9 ]) sphere(r = 8);
        }
        translate([
            5.3, player_box_length - wall_thickness * 2 - major_worker_len,
            player_box_height - lid_thickness * 2 - aphid_thickness + 15
        ]) sphere(r = 9);
        translate([
            0, player_box_length - wall_thickness * 2 - major_worker_len, player_box_height - lid_thickness * 2 -
            aphid_thickness
        ]) linear_extrude(height = 60) offset(delta = 0.5) MajorWorkerOutline();
        for (i = [0:1:2])
        {
            translate([
                player_box_width - wall_thickness * 2 - major_worker_token_diameter / 2 -
                    (major_worker_token_diameter + 1) * i,
                player_box_length - wall_thickness * 2 - major_worker_token_diameter / 2,
                player_box_height - lid_thickness * 2 -
                tile_thickness
            ])
            {
                cylinder(d = major_worker_token_diameter, h = tile_thickness + 1, anchor = BOTTOM);
                translate([ 0, -major_worker_token_diameter / 2, 9 ]) sphere(r = 9);
            }
        }
    }
}

module PredatorBox()
{
    MakeBoxWithCapLid(predator_box_width, predator_box_length, predator_box_height, wall_thickness = wall_thickness,
                      lid_thickness = lid_thickness)
    {
    }
}

module BoxLayout()
{
    cube([ 1, box_length, box_height ]);
    cube([ box_width, box_length, thickness_to_stuff ]);

    translate([ 0, 0, thickness_to_stuff ])
    {
        TileBox();
        translate([ 0, tile_box_length, 0 ]) CardBox();
        translate([ 0, tile_box_length, card_box_height ]) MinionsOfTheMeadowCardBox();
        translate([ card_box_width, tile_box_length, 0 ]) MinionsOfTheMeadowBox();
        translate([ card_box_width, tile_box_length, minions_of_the_meadow_box_height ]) FoodTokenBox();
        translate([ card_box_width, tile_box_length, minions_of_the_meadow_box_height + food_token_box_height ])
            PredatorBox();
        translate([ 0, tile_box_length + card_box_length, 0 ]) PlayerBox();
        translate([ 0, tile_box_length + card_box_length, player_box_height ]) PlayerBox();
        translate([ 0, tile_box_length + card_box_length, player_box_height * 2 ]) PlayerBox();
        translate([ player_box_width, tile_box_length + card_box_length, 0 ]) AphidBox();
    }
}

BoxLayout();