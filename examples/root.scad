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

box_length = 278;
box_width = 214;
box_height = 67;
board_thickness = 28;
wall_thickness = 3;
lid_thickness = 2;
inner_thickness = 1;

square_tile_size = 18;
round_tile_diameter = 20;
slightly_larger_round_tile_diameter = 21;
larger_square_tile_ = 19;
tile_thickness = 2;

riverfolk_glass_diameter = 17;
riverfolk_glass_thickness = 9;

player_token_thickness = 9;

round_winter_thing_width = 29;
round_winter_thing_length = 15;
round_winter_thing_curve_width = 7;
round_winter_thing_cap_width = 12;
round_winter_thing_diameter = 50;
round_winter_thing_top_round = 10;

// Sleeved card size.
card_width = 68.5;
card_length = 92.5;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

// Player token sizes
vagabond_length = 22;
vagabond_width = 21;
vagabond_ear_base_width = 14;
vagabond_ear_top_width = 9;
vagabond_ear_top_length = 4;
vagabond_ear_bottom_length = 6;
vagabond_base_width = 16;
vagagond_middle_length = 10;
vagabond_middle_width = 15;
vagabond_cheek_middle_length = 13;
vagabond_cheek_top_length = 16;
erie_base_width = 15;
erie_length = 22;
erie_width = 18;
erie_middle_width = 12;
erie_top_head = 3;
erie_beak_start_width = 14;
erie_beak_length = 5;
erie_beak_top_length = 15;
erie_beak_middle_length = 12;
erie_middle_length = 10;
erie_top_radius = 11;
marquis_length = 22;
marquis_width = 16;
maarquis_middle_width = 14;
marquis_middle_length = 10;
marquis_ear_width = 9;
marquis_ear_length = 3;
marquis_ear_flat_middle = 2;
marquis_ear_base_width = 13;
marquis_eye_bulge_top_length = 16;
marquis_bulge_radius = 5;
alliance_length = 19;
alliance_width = 19;
alliance_middle_width = 14;
alliance_middle_length = 9;
alliance_base_width = 16;
alliance_ear_diameter = 10;
lizard_length = 20;
lizard_width = 18;
lizard_base_width = 16;
lizard_middle_width = 13;
lizard_middle_length = 9;
lizard_middle_offset = 3;
lizard_head_bumps_length = 7;
lizard_nose_start_length = 15;
lizard_nose_length = 2.5;
lizard_nose_slope_start = 7;
lizard_nose_flat = 3;
lizard_bumps_width = 2;
riverfolk_length = 20;
riverfolk_width = 16;
riverfolk_middle_width = 15;
riverfolk_middle_length = 9;
riverfolk_checks_width = 15.5;
riverfolk_checks_length = 7;
riverfolk_ear_width = 5;
riverfolk_ear_dip = 1;
dice_width = 22;

marquis_de_cat_num = 25;
erie_dynasty_num = 20;
woodland_aliance_num = 10;
vagabond_num = 1;
riverfolk_num = 15;
lizard_num = 25;
erie_card_num = 6;
vagabond_card_num = 18;
overview_example_cards_num = 5;
marquis_wood_token_num = 8;
marquis_building_token_num = 6;
erie_roost_building_num = 7;
woodland_aliance_sympathy_num = 10;
woodland_alliance_base_num = 3;
vagabond_relationship_num = 12; // 3 base base, riverfolk: +3base, +6 for expansion

ruin_loot_num = 4;
starting_loot_num = 7;
craftable_items_num = 7;
craftable_items_per_type = [ 2, 2, 1, 1, 2, 2, 2 ];

clearing_board_marker_per_type_num = 4;

shared_cards_num = 54;

dice_num = 2;

quarter_width = (box_width - 1) / 4;

card_box_width = quarter_width * 3;
card_box_length = card_length + wall_thickness * 2;
card_box_height = box_height - board_thickness;

marquis_box_width = quarter_width * 2;
marquis_box_length = marquis_width * 3 + wall_thickness * 2 + 2;
marquis_box_height = marquis_length + lid_thickness * 2 + 0.5;
marquis_box_top_height = box_height - board_thickness - marquis_box_height;

erie_box_width = quarter_width * 2;
erie_box_length = marquis_box_length;
erie_box_height = erie_width + lid_thickness * 2 + 0.5;
erie_box_top_width = quarter_width;
erie_box_top_length = erie_box_length;
erie_box_top_height = box_height - board_thickness - erie_box_height;

vagabond_box_height = erie_box_top_height;
vagabond_box_length = marquis_box_length;
vagabond_box_width = quarter_width;

alliance_box_width = quarter_width;
alliance_box_length = erie_box_length;
alliance_box_height = alliance_width + lid_thickness * 2 + 0.5;
alliance_box_top_height = box_height - alliance_box_height - board_thickness;

riverfolk_box_width = quarter_width;
riverfolk_box_length = erie_box_length;
riverfolk_box_height = riverfolk_length + lid_thickness * 2 + 0.5;
riverfolk_box_top_height = box_height - riverfolk_box_height - board_thickness;

item_box_length = card_box_length;
item_box_width = quarter_width;
item_box_height = tile_thickness * 3 + 1 + lid_thickness * 2;
item_box_middle_height = tile_thickness * 2 + 1 + lid_thickness * 2;
item_box_winter_height = tile_thickness * 2 + 1 + lid_thickness * 2;

echo([ card_box_width, card_box_length, erie_box_top_height ]);

module CylBothWidth(width_offset, len_offset, height, r = 1)
{
    translate([ width_offset - r, len_offset, 0 ]) cyl(r = r, h = height);
    translate([ -width_offset + r, len_offset, 0 ]) cyl(r = r, h = height);
}

module VagabondCharacter(height)
{
    module Ear()
    {
        hull()
        {
            translate([ vagabond_ear_base_width / 2 - 1, vagabond_length / 2 - vagabond_cheek_top_length - 1, 0 ])
                cyl(r = 1, h = height);
            translate([ vagabond_ear_top_width / 2 - 1, -vagabond_length / 2 + 1, 0 ]) cyl(r = 1, h = height);
            translate([ 0, -vagabond_length / 2 + vagabond_ear_top_length + 1, 0 ]) cyl(r = 1, h = height);
        }
    }
    union()
    {
        // bottom
        hull()
        {
            CylBothWidth(vagabond_base_width / 2 - 1, vagabond_length / 2 - 1, height);
            CylBothWidth(vagabond_middle_width / 2 - 1, vagabond_length / 2 - vagagond_middle_length - 1, height);
        }
        // middle cheeks.
        hull()
        {
            CylBothWidth(vagabond_middle_width / 2 - 1, vagabond_length / 2 - vagagond_middle_length - 1, height);
            CylBothWidth(vagabond_width / 2 - 1, vagabond_length / 2 - vagabond_cheek_middle_length - 1, height);
            CylBothWidth(vagabond_ear_base_width / 2, vagabond_length / 2 - vagabond_cheek_top_length - 1, height);
            translate([ 0, -vagabond_length / 2 + vagabond_ear_top_length + 1, 0 ]) cyl(r = 1, h = height);
        }
        // Ears.
        Ear();
        mirror([ 1, 0, 0 ]) Ear();
    }
}

module MarquisCharacter(height)
{
    module Ear()
    {
        hull()
        {
            translate([ marquis_ear_flat_middle / 2 - 1, -marquis_length / 2 + marquis_ear_length + 1, 0 ])
                cyl(r = 1, h = height);
            translate([ marquis_ear_width / 2 - 1, -marquis_length / 2 + 1, 0 ]) cyl(r = 1, h = height);
            translate([ marquis_ear_base_width / 2 - 1, marquis_length / 2 - marquis_eye_bulge_top_length, 0 ])
                cyl(r = 1, h = height);
        }
    }
    // Base
    hull()
    {
        CylBothWidth(width_offset = marquis_width / 2, len_offset = marquis_length / 2 - 1, height = height);
        CylBothWidth(width_offset = maarquis_middle_width / 2, len_offset = marquis_length / 2 - marquis_middle_length,
                     height = height);
    }
    // Top
    hull()
    {
        CylBothWidth(width_offset = marquis_ear_base_width / 2,
                     len_offset = marquis_length / 2 - marquis_eye_bulge_top_length, height = height);
        CylBothWidth(width_offset = maarquis_middle_width / 2, len_offset = marquis_length / 2 - marquis_middle_length,
                     height = height);
        CylBothWidth(width_offset = marquis_ear_flat_middle / 2,
                     len_offset = -marquis_length / 2 + marquis_ear_length + 1, height = height);
    }
    // Ears
    Ear();
    mirror([ 1, 0, 0 ]) Ear();
    translate(
        [ (marquis_width) / 2, marquis_length / 2 - (marquis_eye_bulge_top_length + marquis_middle_length) / 2, 0 ])
        cyl(r = marquis_bulge_radius, anchor = RIGHT, h = height);
    translate(
        [ -(marquis_width) / 2, marquis_length / 2 - (marquis_eye_bulge_top_length + marquis_middle_length) / 2, 0 ])
        cyl(r = marquis_bulge_radius, anchor = LEFT, h = height);
}

module ErieCharacter(height)
{
    union()
    {
        // Base
        translate([ (erie_width - erie_base_width) / 2, 0, 0 ]) hull()
        {
            CylBothWidth(width_offset = erie_base_width / 2, len_offset = erie_length / 2 - 1, height = height);
            CylBothWidth(width_offset = erie_middle_width / 2, len_offset = erie_length / 2 - erie_middle_length,
                         height = height);
        }
        // Top
        hull()
        {
            CylBothWidth(width_offset = erie_middle_width / 2, len_offset = erie_length / 2 - erie_middle_length,
                         height = height);
            CylBothWidth(width_offset = erie_middle_width / 2, len_offset = erie_length / 2 - erie_beak_top_length,
                         height = height);
            translate([ erie_width / 2 - 1 - erie_top_head, -erie_length / 2 + 1, 0 ]) cyl(r = 1, h = height);
        }
        // Beak.
        hull()
        {
            translate([ -erie_width / 2 + 1, erie_length / 2 - erie_beak_middle_length - 1, 0 ]) cyl(r = 1, h = height);
            translate([ -erie_middle_width / 2 + 1, erie_length / 2 - erie_middle_length, 0 ]) cyl(r = 1, h = height);
            translate([ -erie_middle_width / 2 + 1, erie_length / 2 - erie_beak_top_length, 0 ]) cyl(r = 1, h = height);
        }
        translate([ erie_width / 2 - 1 - erie_top_head, -erie_length / 2, 0 ]) intersection()
        {
            cyl(r = erie_top_radius, h = height, anchor = FRONT);
            cuboid([ erie_top_radius, erie_top_radius, height ], anchor = FRONT + RIGHT);
        }
    }
}

module AllianceCharacter(height)
{
    union()
    {
        // Base
        hull()
        {
            CylBothWidth(width_offset = alliance_base_width / 2, len_offset = alliance_length / 2 - 1, height = height);
            CylBothWidth(width_offset = alliance_middle_width / 2,
                         len_offset = alliance_length / 2 - alliance_middle_length, height = height);
        }
        hull()
        {
            translate([ alliance_width / 2, -alliance_length / 2 + alliance_ear_diameter / 2, 0 ])
                cyl(d = alliance_ear_diameter, h = height, anchor = RIGHT);
            translate([ 0, alliance_length / 2 - alliance_middle_length, 0 ]) cyl(r = 1, h = height);
            translate([ alliance_middle_width / 2 - 1, alliance_length / 2 - alliance_middle_length, 0 ])
                cyl(r = 1, h = height);
        }
        hull()
        {
            translate([ -alliance_width / 2, -alliance_length / 2 + alliance_ear_diameter / 2, 0 ])
                cyl(d = alliance_ear_diameter, h = height, anchor = LEFT);
            translate([ 0, alliance_length / 2 - alliance_middle_length, 0 ]) cyl(r = 1, h = height);
            translate([ -alliance_middle_width / 2 + 1, alliance_length / 2 - alliance_middle_length, 0 ])
                cyl(r = 1, h = height);
        }
    }
}

module RiverfolkCharacter(height)
{
    // Base
    hull()
    {
        CylBothWidth(width_offset = riverfolk_width / 2, len_offset = riverfolk_length / 2 - 1, height = height);
        CylBothWidth(width_offset = riverfolk_middle_width / 2,
                     len_offset = riverfolk_length / 2 - riverfolk_middle_length, height = height);
    }
    translate([ 0, -riverfolk_length / 2, 0 ]) cyl(d = riverfolk_width, h = height, anchor = FRONT);
    translate([ riverfolk_width / 2 - riverfolk_ear_width / 2, -riverfolk_length / 2, 0 ])
        cyl(d = riverfolk_ear_width, h = height, anchor = FRONT);
    translate([ -riverfolk_width / 2 + riverfolk_ear_width / 2, -riverfolk_length / 2, 0 ])
        cyl(d = riverfolk_ear_width, h = height, anchor = FRONT);
}

module LizardCharacter(height)
{
    // Base
    hull()
    {
        CylBothWidth(width_offset = lizard_base_width / 2, len_offset = lizard_length / 2 - 1, height = height);
        CylBothWidth(width_offset = lizard_middle_width / 2, len_offset = lizard_length / 2 - lizard_middle_length,
                     height = height);
    }
    // Nose
    hull()
    {
        translate([ lizard_width / 2 - 1 - lizard_bumps_width, -riverfolk_length / 2 + 1, 0 ]) cyl(r = 1, h = height);
        translate([ lizard_middle_width / 2 - 1, lizard_length / 2 - lizard_middle_length, 0 ]) cyl(r = 1, h = height);
        translate([ -lizard_middle_width / 2 + 1, lizard_length / 2 - lizard_middle_length, 0 ]) cyl(r = 1, h = height);
        translate([ -lizard_width / 2 + 1, lizard_length / 2 - lizard_nose_start_length - 1, 0 ])
            cyl(r = 1, h = height);
        translate([ -lizard_width / 2 + 1, lizard_length / 2 - lizard_nose_start_length - lizard_nose_flat + 1, 0 ])
            cyl(r = 1, h = height);
        translate([ riverfolk_width / 2 - lizard_nose_slope_start, -riverfolk_length / 2 + 1, 0 ])
            cyl(r = 1, h = height);
    }
    // bumps
    translate([ lizard_width / 2, -lizard_length / 2, 0 ])
        cuboid([ lizard_bumps_width + 1, lizard_head_bumps_length, height ], anchor = FRONT + RIGHT, rounding = 1,
               edges = [ FRONT + RIGHT, BACK + RIGHT ]);
}

module WinterToken(height)
{
    translate([ -round_winter_thing_length / 2, 0, 0 ])
    {
        union()
        {
            translate([ round_winter_thing_length - round_winter_thing_cap_width / 2, 0, 0 ])
                cyl(d = round_winter_thing_cap_width, h = height, anchor = BOTTOM);
            difference()
            {
                intersection()
                {
                    translate([ -round_winter_thing_diameter / 2 + round_winter_thing_top_round, 0, 0 ]) difference()
                    {
                        cyl(d = round_winter_thing_diameter, h = height, anchor = BOTTOM);
                        translate([ 0, 0, -0.5 ])
                            cyl(d = round_winter_thing_diameter - round_winter_thing_curve_width * 2, h = height + 2,
                                anchor = BOTTOM);
                    }
                    cuboid([ round_winter_thing_length, round_winter_thing_width, height ], anchor = LEFT + BOTTOM);
                }
                translate([
                    round_winter_thing_curve_width * 3 / 7 + 0.25,
                    round_winter_thing_width - round_winter_thing_curve_width * 2.5 - 0.5, -0.5
                ]) rotate([ 0, 0, 30 ]) difference()
                {
                    cuboid([ round_winter_thing_curve_width + 2, round_winter_thing_curve_width, height + 1 ],
                           anchor = FRONT + BOTTOM);
                    cyl(d = round_winter_thing_curve_width, h = height + 1, $fn = 64, anchor = BOTTOM);
                }

                translate([
                    round_winter_thing_curve_width * 3 / 7 + 0.25,
                    -round_winter_thing_width + round_winter_thing_curve_width * 2.5 + 0.5, -0.5
                ]) rotate([ 0, 0, 150 ]) difference()
                {
                    cuboid([ round_winter_thing_curve_width + 2, round_winter_thing_curve_width, height + 1 ],
                           anchor = FRONT + BOTTOM);
                    cyl(d = round_winter_thing_curve_width, h = height + 1, $fn = 64, anchor = BOTTOM);
                }
            }
        }
    }
}

module CardBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = card_box_width, length = card_box_length, height = card_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_width = card_box_width - wall_thickness * 2;
        middle = card_width * 2 + 3;
        translate([ (inner_width - middle) / 2, 0, 0 ])
        {
            cube([ card_width, card_length, card_box_height ]);
            translate([ card_width + 3, 0, 0 ]) cube([ card_width, card_length, card_box_height ]);
            translate([ card_width / 2, -1, -lid_thickness - 0.01 ])
                FingerHoleBase(radius = 15, height = card_box_height);
            translate([ card_width / 2 + card_width + 3, -1, -lid_thickness - 0.01 ])
                FingerHoleBase(radius = 15, height = card_box_height);
        }
    }
}

module MarquisBoxBottom(generate_lid = true)
{
    MakeBoxWithCapLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_width = marquis_box_width - wall_thickness * 2;
        len = player_token_thickness * 8 + 1;
        // Put a bunch of places in for the marquis items
        translate([ (inner_width - len) / 2, 0, 0 ])
        {
            translate([ len / 2, marquis_width / 2, marquis_length / 2 + 1 ]) rotate([ 90, 0, 90 ])
                MarquisCharacter(height = len);
            translate([ len / 2, marquis_width / 2, marquis_length / 2 + 10 ])
                cuboid([ len, marquis_width, marquis_length ]);
            translate([ len / 2, marquis_width / 2 + marquis_width + 1, marquis_length / 2 + 1 ]) rotate([ 90, 0, 90 ])
                MarquisCharacter(height = len);
        }
        translate([ (inner_width - len - player_token_thickness) / 2, 0, 0 ])
        {
            translate([
                (len + player_token_thickness) / 2, marquis_width / 2 + marquis_width * 2 + 2, marquis_length / 2 + 1
            ]) rotate([ 90, 0, 90 ]) MarquisCharacter(height = len + player_token_thickness);
            translate([
                (len + player_token_thickness) / 2, marquis_width / 2 + marquis_width * 2 + 2, marquis_length / 2 + 10
            ]) cuboid([ len + player_token_thickness, marquis_width, marquis_length ]);
        }
        translate([ 0, 0, marquis_length / 2 ])
            RoundedBoxAllSides(inner_width, marquis_box_length - wall_thickness * 2, marquis_length, 7);
    }
}

module MarquisBoxTop(generate_lid = true)
{
    module BuildingSpots()
    {
        cube([ square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 ]);
        translate([ square_tile_size + 1, 0, 0 ])
            cube([ square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 ]);
    }
    MakeBoxWithCapLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_top_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_width = marquis_box_width - wall_thickness * 2;
        inner_length = marquis_box_length - wall_thickness * 2;
        inner_height = marquis_box_top_height - lid_thickness * 2;

        // Wood markers.
        translate([
            round_tile_diameter / 2, round_tile_diameter / 2, inner_height - tile_thickness * marquis_wood_token_num / 2
        ]) cyl(d = round_tile_diameter, h = tile_thickness * marquis_wood_token_num / 2, anchor = BOTTOM);
        translate([
            round_tile_diameter / 2 + round_tile_diameter + 2, round_tile_diameter / 2,
            inner_height - tile_thickness * marquis_wood_token_num / 2
        ]) cyl(d = round_tile_diameter, h = tile_thickness * marquis_wood_token_num / 2, anchor = BOTTOM);

        // Keep token
        translate([
            round_tile_diameter / 2 + round_tile_diameter * 2 + 2, round_tile_diameter / 2 * 6 / 4,
            inner_height - tile_thickness - 0.5
        ]) cyl(d = round_tile_diameter, h = tile_thickness + 1, anchor = BOTTOM);

        // Score marker.
        translate(
            [ round_tile_diameter * 2 + 2, inner_length - 5 - square_tile_size, inner_height - tile_thickness - 0.5 ])
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);

        // Buildings.
        translate(
            [ 0, inner_length - square_tile_size, inner_height - tile_thickness * marquis_building_token_num / 2 ])
        {
            BuildingSpots();
        }
        translate([
            inner_width - square_tile_size * 2 - 1, inner_length - square_tile_size,
            inner_height - tile_thickness * marquis_building_token_num / 2
        ])
        {
            BuildingSpots();
        }
        translate([
            inner_width - square_tile_size * 2 - 1, 0, inner_height - tile_thickness * marquis_building_token_num / 2
        ])
        {
            BuildingSpots();
        }
    }
}

module VagabondBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = vagabond_box_width, length = vagabond_box_length, height = vagabond_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = vagabond_box_height - lid_thickness * 2;
        inner_width = vagabond_box_width - wall_thickness * 2;
        inner_length = vagabond_box_length - wall_thickness * 2;
        translate([
            vagabond_width / 2, vagabond_length / 2,
            inner_height - player_token_thickness - 0.5 + (player_token_thickness + tile_thickness) / 2 -
            tile_thickness
        ])
        {
            rotate([ 0, 0, 180 ]) VagabondCharacter(height = player_token_thickness + 1 + tile_thickness);
            translate([
                vagabond_width / 2, vagabond_length / 8,
                player_token_thickness / 2 - (player_token_thickness + tile_thickness) / 2
            ]) cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }
        translate([
            inner_width - vagabond_length / 2, vagabond_width / 2,
            inner_height - player_token_thickness - 0.5 + (player_token_thickness + tile_thickness) / 2 -
            tile_thickness
        ])
        {
            rotate([ 0, 0, 180 ]) VagabondCharacter(height = player_token_thickness + 1 + tile_thickness);
            translate([
                -vagabond_width / 2, vagabond_length / 8,
                player_token_thickness / 2 - (player_token_thickness + tile_thickness) / 2
            ]) cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }

        // Score marker.
        translate([ inner_width / 2 - square_tile_size - 0.5, 3, inner_height - tile_thickness - 0.5 ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);
            translate([ square_tile_size / 2, square_tile_size, 0 ])
                cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }
        translate([ inner_width / 2 + 0.5, 3, inner_height - tile_thickness - 0.5 ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);
            translate([ square_tile_size / 2, square_tile_size, 0 ])
                cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }

        // Relationship markers.
        translate([
            inner_width - square_tile_size, inner_length - square_tile_size,
            inner_height - tile_thickness * vagabond_relationship_num / 2 - 0.5
        ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num / 2 + 1 ]);
            translate([ square_tile_size / 2, 0, 0 ]) cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }
        translate(
            [ 0, inner_length - square_tile_size, inner_height - tile_thickness * vagabond_relationship_num / 2 - 0.5 ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num / 2 + 1 ]);
            translate([ square_tile_size / 2, 0, 0 ]) cyl(r = 6, h = box_height, anchor = BOTTOM, rounding = 5.5);
        }
    }
}

module ErieBoxBottom(generate_lid = true)
{
    MakeBoxWithCapLid(width = erie_box_width, length = erie_box_length, height = erie_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = erie_box_height - lid_thickness * 2;
        inner_width = erie_box_width - wall_thickness * 2;
        len = player_token_thickness * 10 + 1;

        translate([ (inner_width - len) / 2, 0, 0 ])
        {
            translate([ len / 2, erie_length / 2 + 2, inner_height - erie_width / 2 - 0.5 ])
            {
                rotate([ 0, 270, 0 ]) ErieCharacter(height = len);
                translate([ 0, 0, 5 + erie_width / 2 ]) cuboid([ len, erie_length, erie_width / 2 ], anchor = TOP);
            }
            translate([ len / 2, erie_length / 2 + erie_length + 4, inner_height - erie_width / 2 - 0.5 ])
            {
                rotate([ 0, 270, 0 ]) ErieCharacter(height = len);
                translate([ 0, 0, 5 + erie_width / 2 ]) cuboid([ len, erie_length, erie_width / 2 ], anchor = TOP);
            }
        }
    }
}
module ErieBoxTop(generate_lid = true)
{
    MakeBoxWithCapLid(width = erie_box_top_width, length = erie_box_top_length, height = erie_box_top_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_length = erie_box_length - wall_thickness * 2;
        inner_width = erie_box_width - wall_thickness * 2;
        inner_height = erie_box_top_height - lid_thickness * 2;

        // Score marker.
        translate([ 0, inner_length - square_tile_size, inner_height - tile_thickness - 0.5 ])
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);

        // Roosts.
        for (i = [0:1:1])
        {
            num_tiles = 3 + i;
            translate([ (square_tile_size + 1) * i, 0, inner_height - num_tiles * tile_thickness - 0.5 ])
                cube([ square_tile_size, square_tile_size, tile_thickness * num_tiles + 1 ]);
        }
    }
}

module AllianceBoxBottom(generate_lid = true)
{
    MakeBoxWithCapLid(width = alliance_box_width, length = alliance_box_length, height = alliance_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = alliance_box_height - lid_thickness * 2;
        inner_width = alliance_box_width - wall_thickness * 2;
        len = player_token_thickness * 5 + 1;

        translate([ (inner_width - len) / 2, 1.5, 0 ])
        {
            translate([ len / 2, alliance_length / 2 + 2, inner_height - alliance_width / 2 ])
            {
                rotate([ 0, 270, 0 ]) AllianceCharacter(height = len);
                translate([ 0, 0, alliance_width / 2 ])
                    cuboid([ len, alliance_length, alliance_width / 2 + 4.5 ], anchor = TOP);
            }
            translate([ len / 2, alliance_length / 2 + 2 + alliance_length + 4, inner_height - alliance_width / 2 ])
            {
                rotate([ 0, 270, 0 ]) AllianceCharacter(height = len);
                translate([ 0, 0, alliance_width / 2 ])
                    cuboid([ len, alliance_length, alliance_width / 2 + 4.5 ], anchor = TOP);
            }
        }
    }
}

module AllianceBoxTop(generate_lid = true)
{
    MakeBoxWithCapLid(width = alliance_box_width, length = alliance_box_length, height = alliance_box_top_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = alliance_box_top_height - lid_thickness * 2;
        inner_width = alliance_box_width - wall_thickness * 2;
        inner_length = alliance_box_length - wall_thickness * 2;

        // Score marker.
        translate([ 0, 0, inner_height - tile_thickness - 0.5 ])
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);

        // Sympathy tokens.
        translate([
            inner_width - round_tile_diameter / 2, round_tile_diameter / 2,
            inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 + 0.5
        ]) cyl(d = round_tile_diameter, h = tile_thickness * woodland_aliance_sympathy_num / 2 + 1, anchor = BOTTOM);
        translate([
            inner_width - round_tile_diameter / 2, round_tile_diameter / 2 + round_tile_diameter + 1,
            inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 + 0.5
        ]) cyl(d = round_tile_diameter, h = tile_thickness * woodland_aliance_sympathy_num / 2 + 1, anchor = BOTTOM);

        // Bases.
        translate(
            [ 0, inner_length - square_tile_size, inner_height - tile_thickness * woodland_alliance_base_num - 0.5 ])
            cube([ square_tile_size, square_tile_size, tile_thickness * woodland_alliance_base_num + 1 ]);
    }
}

module RiverfolkBoxBottom(generate_lid = true)
{
    MakeBoxWithCapLid(width = riverfolk_box_width, length = riverfolk_box_length, height = riverfolk_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = riverfolk_box_height - lid_thickness * 2;
        inner_width = riverfolk_box_width - wall_thickness * 2;
        inner_length = riverfolk_box_length - wall_thickness * 2;
        echo([ inner_width, inner_length, riverfolk_width, riverfolk_length ]);
        len = player_token_thickness * 5 + 1;
        translate([ 0, 0, 0 ]) for (i = [0:1:2])
        {
            translate([ len / 2, riverfolk_width / 2 + (riverfolk_width + 1) * i, inner_height - riverfolk_length / 2 ])
            {
                rotate([ 90, 0, 90 ]) RiverfolkCharacter(height = len + 1);
                translate([ 0, 0, riverfolk_length / 2 ])
                    cuboid([ len + 1, riverfolk_width, riverfolk_length - 3 ], anchor = TOP);
            }
        }
    }
}

module RiverfolkBoxTop(generate_lid = true)
{
    MakeBoxWithCapLid(width = riverfolk_box_width, length = riverfolk_box_length, height = riverfolk_box_top_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = riverfolk_box_top_height - lid_thickness * 2;
        inner_width = riverfolk_box_width - wall_thickness * 2;
        inner_length = riverfolk_box_length - wall_thickness * 2;

        // Score marker.
        translate([ 0, 0, inner_height - tile_thickness - 0.5 ])
            cube([ square_tile_size, square_tile_size, tile_thickness + 1 ]);

        // trading posts.
        translate(
            [ inner_width - round_tile_diameter / 2, round_tile_diameter / 2, inner_height - tile_thickness * 5 + 0.5 ])
            cyl(d = round_tile_diameter + 0.5, h = tile_thickness * 5 + 1, anchor = BOTTOM);
        translate([
            inner_width - round_tile_diameter / 2, inner_length - round_tile_diameter / 2,
            inner_height - tile_thickness * 4 + 0.5
        ]) cyl(d = round_tile_diameter + 0.5, h = tile_thickness * 4 + 1, anchor = BOTTOM);
        // translate([ inner_width - round_tile_diameter - 1, inner_length / 2, inner_height - tile_thickness * 4 + 0.5
        // ])
        //   cyl(d = round_tile_diameter, h = tile_thickness * 4 + 1, anchor = BOTTOM);

        // glass things.
        translate([ inner_width / 2, inner_length / 2 + 0.5, inner_height - riverfolk_glass_thickness - 0.5 ])
            cyl(d = riverfolk_glass_diameter, h = riverfolk_glass_thickness + 1, anchor = BOTTOM);
        translate([
            riverfolk_glass_diameter / 2, inner_length - riverfolk_glass_diameter / 2,
            inner_height - riverfolk_glass_thickness - 0.5
        ]) cyl(d = riverfolk_glass_diameter, h = riverfolk_glass_thickness + 1, anchor = BOTTOM);
        translate([
            riverfolk_glass_diameter / 2 + 0.5, riverfolk_glass_diameter / 2 + 0.5,
            inner_height - riverfolk_glass_thickness - 0.75 -
            tile_thickness
        ]) cyl(d = riverfolk_glass_diameter, h = riverfolk_glass_thickness + tile_thickness + 1, anchor = BOTTOM);
    }
}

module ItemsBoxBottom()
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = item_box_height - lid_thickness * 2;
        inner_width = item_box_width - wall_thickness * 2;
        depths = [
            "torch", 2, "boot",          3, "coin", 2, "crossbow", 2, "sword", 3,
            "bag",   1, "hammer/teapot", 2, "ruin", 3, "ruin",     3, "ruin",  2
        ];
        for (i = [0:1:4])
        {
            if (depths[i * 4 + 1] != 0)
            {
                translate([ 0, (square_tile_size + 0.6) * i, inner_height - tile_thickness * depths[i * 4 + 1] - 0.5 ])
                {
                    cube([ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1 ]);
                    translate([ square_tile_size, square_tile_size / 2, 0 ])
                        cyl(r = 6, anchor = BOTTOM, h = item_box_height, rounding = 5, $fn = 32);
                    translate([ (square_tile_size) / 2, square_tile_size / 2, -0.5 ]) linear_extrude(height = 2)
                        rotate(90) text(text = depths[i * 4], font = "Stencil Std:style=Bold", size = 2.5,
                                        halign = "center", valign = "center");
                }
            }
            if (depths[i * 4 + 3] != 0)
            {
                translate([
                    inner_width - square_tile_size, (square_tile_size + 0.6) * i,
                    inner_height - tile_thickness * depths[i * 4 + 3] - 0.5
                ])
                {
                    cube([ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1 ]);
                    translate([ 0, square_tile_size / 2, 0 ])
                        cyl(r = 6, anchor = BOTTOM, h = item_box_height, rounding = 5, $fn = 32);
                    translate([ (square_tile_size) / 2, square_tile_size / 2, -0.5 ]) linear_extrude(height = 2)
                        rotate(90) text(text = depths[i * 4 + 2], font = "Stencil Std:style=Bold", size = 2.5,
                                        halign = "center", valign = "center");
                }
            }
        }
    }
}

module ItemsBoxMiddle()
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_middle_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = item_box_middle_height - lid_thickness * 2;
        inner_width = item_box_width - wall_thickness * 2;
        // 12 craftable items (2× bag, 2× boot, 1× crossbow, 1× hammer, 2× sword, 2× teapot, 2× coins)
        depths = [
            "bag",    2, "boot",  2, "crossbow", 1, "hammer", 1, "sword", 2,
            "teapot", 2, "coins", 2, "n/a",      0, "ruins",  2, "ruins", 2
        ];
        for (i = [0:1:4])
        {
            if (depths[i * 4 + 1] != 0)
            {
                translate([ 0, (square_tile_size + 0.6) * i, inner_height - tile_thickness * depths[i * 4 + 1] - 0.5 ])
                {
                    cube([ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1 ]);
                    translate([ square_tile_size, square_tile_size / 2, 0 ])
                        cyl(r = 6, anchor = BOTTOM, h = item_box_height, rounding = 5, $fn = 32);
                    translate([ (square_tile_size) / 2, square_tile_size / 2, -0.5 ]) linear_extrude(height = 2)
                        rotate(90) text(text = depths[i * 4], font = "Stencil Std:style=Bold", size = 2.5,
                                        halign = "center", valign = "center");
                }
            }
            if (depths[i * 4 + 3] != 0)
            {
                translate([
                    inner_width - square_tile_size, (square_tile_size + 0.6) * i,
                    inner_height - tile_thickness * depths[i * 4 + 3] - 0.5
                ])
                {
                    cube([ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1 ]);
                    translate([ 0, square_tile_size / 2, 0 ])
                        cyl(r = 6, anchor = BOTTOM, h = item_box_height, rounding = 5, $fn = 32);
                    translate([ (square_tile_size) / 2, square_tile_size / 2, -0.5 ]) linear_extrude(height = 2)
                        rotate(90) text(text = depths[i * 4 + 2], font = "Stencil Std:style=Bold", size = 2.5,
                                        halign = "center", valign = "center");
                }
            }
        }
    }
}

module ItemsBoxWinter()
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_winter_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        inner_height = item_box_winter_height - lid_thickness * 2;
        inner_width = item_box_width - wall_thickness * 2;
        for (i=[0:1:5]) {
        translate([ round_winter_thing_width / 2, round_winter_thing_length / 2 + round_winter_thing_length*i, 0 ]) rotate([ 0, 0, 90 ])
            WinterToken(tile_thickness * 2 + 1);
        }
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    // cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        CardBox(generate_lid = false);
        translate([ card_box_width, 0, 0 ]) ItemsBoxBottom();
        translate([ card_box_width, 0, item_box_height ]) ItemsBoxMiddle();
        translate([ card_box_width, 0, item_box_height + item_box_middle_height ]) ItemsBoxWinter();
        translate([ 0, card_box_length, 0 ]) MarquisBoxBottom(generate_lid = false);
        translate([ marquis_box_width, card_box_length, 0 ]) AllianceBoxBottom(generate_lid = false);
        translate([ marquis_box_width, card_box_length, alliance_box_height ]) AllianceBoxTop(generate_lid = false);
        translate([ 0, card_box_length, marquis_box_height ]) MarquisBoxTop(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length, 0 ]) ErieBoxBottom(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length, erie_box_height ]) ErieBoxTop(generate_lid = false);
        translate([ erie_box_top_width, card_box_length + marquis_box_length, erie_box_height ])
            VagabondBox(generate_lid = false);
        translate([ erie_box_width, card_box_length + marquis_box_length, 0 ]) RiverfolkBoxBottom(generate_lid = false);
        translate([ erie_box_width, card_box_length + marquis_box_length, riverfolk_box_height ])
            RiverfolkBoxTop(generate_lid = false);
    }
}

BoxLayout();

// WinterToken(5);