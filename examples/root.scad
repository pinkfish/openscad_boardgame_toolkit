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

default_lid_thickness = 2;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 10;

box_length = 278;
box_width = 214;
box_height = 67;
board_thickness = 28;
wall_thickness = default_wall_thickness;
lid_thickness = default_lid_thickness;
inner_thickness = 1;

square_tile_size = 18.5;
round_tile_diameter = 20;
slightly_larger_round_tile_diameter = 21;
larger_square_tile_ = 19;
tile_thickness = 2;

riverfolk_glass_diameter = 17;
riverfolk_glass_thickness = 9;

player_token_thickness = 9;

round_winter_thing_width = 29.5;
round_winter_thing_length = 15.5;
round_winter_thing_curve_width = 7.5;
round_winter_thing_cap_width = 12.5;
round_winter_thing_diameter = 50;
round_winter_thing_top_round = 10.5;

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
dice_length = 28;

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
vagabond_relationship_num_each = 6; // 3 base base, riverfolk: +3base, +6 for expansion

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
marquis_box_length = (box_length - card_box_length - 2) / 3;
marquis_box_height = marquis_length + lid_thickness * 2 + 0.5;
marquis_box_top_height = box_height - board_thickness - marquis_box_height;

erie_box_width = quarter_width * 2;
erie_box_length = marquis_box_length;
erie_box_height = erie_width + lid_thickness * 2 + 0.5;
erie_box_top_width = quarter_width;
erie_box_top_length = erie_box_length;
erie_box_top_height = box_height - board_thickness - erie_box_height;

alliance_box_width = quarter_width;
alliance_box_length = erie_box_length;
alliance_box_height = alliance_width + lid_thickness * 2 + 0.5;
alliance_box_top_height = box_height - alliance_box_height - board_thickness;

riverfolk_box_width = quarter_width;
riverfolk_box_length = erie_box_length;
riverfolk_box_height = riverfolk_length + lid_thickness * 2 + 0.5;
riverfolk_box_top_height = box_height - riverfolk_box_height - board_thickness;
riverfolk_box_top_width = quarter_width * 2;

vagabond_box_height = player_token_thickness + lid_thickness * 2 + 1;
vagabond_box_length = erie_box_length;
vagabond_box_width = quarter_width;

lizard_box_width = quarter_width * 2;
lizard_box_length = marquis_box_length;
lizard_box_height = lizard_length + lid_thickness * 2 + 0.5;
lizard_box_top_width = quarter_width;
lizard_box_top_height = box_height - lizard_box_height - board_thickness;

item_box_length = wall_thickness * 2 + (square_tile_size + 1) * 5;
item_box_width = quarter_width;
item_box_height = tile_thickness * 3 + 1 + lid_thickness * 2;
item_box_middle_height = tile_thickness * 2 + 1 + lid_thickness * 2;
item_box_winter_height = tile_thickness * 2 + 1 + lid_thickness * 2;
item_box_extras_height =
    box_height - board_thickness - item_box_height - item_box_middle_height - item_box_winter_height;

dice_box_height = dice_width + lid_thickness * 2 + 1;
dice_box_length = card_box_length + erie_box_length - item_box_length;
dice_box_width = quarter_width;

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

module MarquisEyes2d()
{
    translate([ -6, 0, 0 ]) HalfEye2d(60);
    translate([ 6, 0, 0 ]) mirror([ 1, 0 ]) HalfEye2d(60);
    // Nose.
    translate([ 0, -4, 0 ])
    {
        circle(d = 3);
        translate([ 0, -2 ])
        {
            rect([ 1, 3 ]);
            translate([ -3, -1.5 ]) ring(r1 = 2.5, r2 = 3, angle = [ 360, 180 ], n = 32);
            translate([ 3, -1.5 ]) mirror([ 1, 0 ]) ring(r1 = 2.5, r2 = 3, angle = [ 360, 180 ], n = 32);
        }
    }
}

module CardBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = card_box_width, length = card_box_length, height = card_box_height)
    {
        $inner_width = card_box_width - wall_thickness * 2;
        middle = card_width * 2 + 3;
        translate([ ($inner_width - middle) / 2, 0, 0 ])
        {
            cube([ card_width, card_length, card_box_height ]);
            translate([ card_width + 3, 0, 0 ]) cube([ card_width, card_length, card_box_height ]);
            translate([ card_width / 2, -1, -lid_thickness - 0.01 ])
                FingerHoleBase(radius = 15, height = card_box_height);
            translate([ card_width / 2 + card_width + 3, -1, -lid_thickness - 0.01 ])
                FingerHoleBase(radius = 15, height = card_box_height);
        }
    }
    if (generate_lid)
    {
        translate([ marquis_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = card_box_width, length = card_box_length, height = card_box_height,
                               text_width = 70, text_height = 20, text_str = "Marquis", label_rotated = true);
        }
    }
}

module MarquisBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_height)
    {
        len = player_token_thickness * 8 + 1;
        // Put a bunch of places in for the marquis items
        translate([ ($inner_width - len) / 2, 0, 0 ])
        {
            translate([ len / 2, marquis_width / 2, marquis_length / 2 + 1 ]) rotate([ 90, 0, 90 ])
                MarquisCharacter(height = len);
            translate([ len / 2, marquis_width / 2, marquis_length / 2 + 10 ])
                cuboid([ len, marquis_width, marquis_length ]);
            translate([ len / 2, marquis_width / 2 + marquis_width + 1, marquis_length / 2 + 1 ]) rotate([ 90, 0, 90 ])
                MarquisCharacter(height = len);
        }
        translate([ ($inner_width - len - player_token_thickness) / 2, 0, 0 ])
        {
            translate([
                (len + player_token_thickness) / 2, marquis_width / 2 + marquis_width * 2 + 2, marquis_length / 2 + 1
            ]) rotate([ 90, 0, 90 ]) MarquisCharacter(height = len + player_token_thickness);
            translate([
                (len + player_token_thickness) / 2, marquis_width / 2 + marquis_width * 2 + 2, marquis_length / 2 + 10
            ]) cuboid([ len + player_token_thickness, marquis_width, marquis_length ]);
        }
        translate([ 0, 0, marquis_length / 2 ])
            RoundedBoxAllSides($inner_width, marquis_box_length - wall_thickness * 2, marquis_length, 7);
    }
    if (generate_lid)
    {
        translate([ marquis_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = marquis_box_width, length = marquis_box_length, height = marquis_box_height,
                               text_width = 70, text_height = 20, text_str = "Marquis", label_rotated = true);
        }
    }
}

module MarquisBoxTop(generate_lid = true) // `make` me
{
    module BuildingSpots(finger_holes)
    {
        translate([ square_tile_size / 2, square_tile_size / 2, 0 ])
        {
            CuboidWithIndentsBottom(
                [ square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 ],
                finger_hole_radius = 7, finger_holes = finger_holes);
            translate([ square_tile_size + 1, 0, 0 ]) CuboidWithIndentsBottom(
                [ square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 ],
                finger_hole_radius = 7, finger_holes = finger_holes);
        }
    }
    MakeBoxWithCapLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_top_height)
    {
        // Wood markers.
        translate([
            round_tile_diameter / 2, round_tile_diameter / 2,
            $inner_height - tile_thickness * marquis_wood_token_num / 2
        ]) CylinderWithIndents(radius = round_tile_diameter / 2, height = tile_thickness * marquis_wood_token_num / 2,
                               finger_hole_radius = 7, finger_holes = [110]);
        translate([
            round_tile_diameter / 2 + round_tile_diameter + 2, round_tile_diameter / 2,
            $inner_height - tile_thickness * marquis_wood_token_num / 2
        ]) CylinderWithIndents(radius = round_tile_diameter / 2, height = tile_thickness * marquis_wood_token_num / 2,
                               finger_hole_radius = 7, finger_holes = [110]);

        // Keep token
        translate([
            round_tile_diameter / 2 + round_tile_diameter * 2 + 2, round_tile_diameter / 2 * 6 / 4,
            $inner_height - tile_thickness - 0.5
        ]) CylinderWithIndents(radius = round_tile_diameter / 2, height = tile_thickness + 1, finger_hole_radius = 10,
                               finger_holes = [135]);

        // Score marker.
        translate([
            round_tile_diameter * 2 + 2 + square_tile_size / 2, $inner_length - 5 - square_tile_size / 2,
            $inner_height - tile_thickness - 0.5
        ]) CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness + 1 ], finger_hole_radius = 9.5,
                                   finger_holes = [2]);

        // Buildings.
        translate(
            [ 0, $inner_length - square_tile_size, $inner_height - tile_thickness * marquis_building_token_num / 2 ])
        {
            BuildingSpots(finger_holes = [6]);
        }
        translate([
            $inner_width - square_tile_size * 2 - 1, $inner_length - square_tile_size,
            $inner_height - tile_thickness * marquis_building_token_num / 2
        ])
        {
            BuildingSpots(finger_holes = [6]);
        }
        translate([
            $inner_width - square_tile_size * 2 - 1, 0, $inner_height - tile_thickness * marquis_building_token_num / 2
        ])
        {
            BuildingSpots(finger_holes = [2]);
        }
    }
    if (generate_lid)
    {
        translate([ marquis_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = marquis_box_width, length = marquis_box_length, height = marquis_box_top_height,
                               text_width = 70, text_height = 20, text_str = "Marquis", label_rotated = true);
        }
    }
}

module VagabondBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = vagabond_box_width, length = vagabond_box_length, height = vagabond_box_height)
    {
        translate([
            vagabond_width / 2, vagabond_length / 2,
            $inner_height - player_token_thickness - 0.5 + (player_token_thickness + 1) / 2
        ])
        {
            rotate([ 0, 0, 180 ]) VagabondCharacter(height = player_token_thickness + 1);
            translate([ 0, vagabond_length / 2 - 3, 0 ]) cyl(r = 6, anchor = BOTTOM, rounding = 5.75, h = box_height);
            translate([ 0, -vagabond_length / 2, 0 ]) cyl(r = 6, anchor = BOTTOM, rounding = 5.75, h = box_height);
        }

        // Score marker.
        translate(
            [ $inner_width - square_tile_size * 2 / 4, square_tile_size / 2, $inner_height - tile_thickness - 0.5 ])
        {
            CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness + 1 ], finger_hole_radius = 10,
                                    finger_holes = [2]);
        }

        // Relationship markers.
        translate([
            $inner_width - square_tile_size, $inner_length - square_tile_size,
            $inner_height - tile_thickness * vagabond_relationship_num_each / 2 - 0.5
        ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num_each / 2 + 1 ]);
            translate([ -5, square_tile_size / 2, 0 ]) xcyl(r = 7, h = vagabond_box_height, anchor = BOTTOM);
        }
        translate([
            0, $inner_length - square_tile_size,
            $inner_height - tile_thickness * vagabond_relationship_num_each / 2 - 0.5
        ])
        {
            cube([ square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num_each / 2 + 1 ]);
        }
    }
    if (generate_lid)
    {
        translate([ vagabond_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = vagabond_box_width, length = vagabond_box_length, height = vagabond_box_height,
                               text_width = 70, text_height = 20, text_str = "Vagabond", label_rotated = true);
        }
    }
}

module ErieBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = erie_box_width, length = erie_box_length, height = erie_box_height)
    {
        len = player_token_thickness * 10 + 1;

        translate([ ($inner_width - len) / 2, 0, 0 ])
        {
            translate([ len / 2, erie_length / 2 + 2, $inner_height - erie_width / 2 - 0.5 ])
            {
                rotate([ 0, 270, 0 ]) ErieCharacter(height = len);
                translate([ 0, 0, 5 + erie_width / 2 ]) cuboid([ len, erie_length, erie_width / 2 ], anchor = TOP);
            }
            translate([ len / 2, erie_length / 2 + erie_length + 4, $inner_height - erie_width / 2 - 0.5 ])
            {
                rotate([ 0, 270, 0 ]) ErieCharacter(height = len);
                translate([ 0, 0, 5 + erie_width / 2 ]) cuboid([ len, erie_length, erie_width / 2 ], anchor = TOP);
            }
        }
    }
    if (generate_lid)
    {
        translate([ erie_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = erie_box_width, length = erie_box_length, height = erie_box_height,
                               text_width = 70, text_height = 20, text_str = "Erie", label_rotated = true);
        }
    }
}

module ErieBoxTop(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = erie_box_top_width, length = erie_box_top_length, height = erie_box_top_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        // Score marker.
        translate([ square_tile_size / 2, $inner_length - square_tile_size / 2, $inner_height - tile_thickness - 0.5 ])
            CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness + 1 ], finger_hole_radius = 8,
                                    finger_holes = [6]);

        // Roosts.
        for (i = [0:1:1])
        {
            num_tiles = 3 + i;
            translate([
                (square_tile_size + 1) * i + square_tile_size / 2, square_tile_size / 2,
                $inner_height - num_tiles * tile_thickness - 0.5
            ]) CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness * num_tiles + 1 ],
                                       finger_hole_radius = 8, finger_holes = [2]);
        }
    }
    if (generate_lid)
    {
        translate([ erie_box_top_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = erie_box_top_width, length = erie_box_top_length, height = erie_box_top_height,
                               text_width = 70, text_height = 20, text_str = "Erie", label_rotated = true);
        }
    }
}

module AllianceBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = alliance_box_width, length = alliance_box_length, height = alliance_box_height)
    {
        len = player_token_thickness * 5 + 1;

        translate([ ($inner_width - len) / 2, 1.5, 0 ])
        {
            translate([ len / 2, alliance_length / 2 + 2, $inner_height - alliance_width / 2 ])
            {
                rotate([ 0, 270, 0 ]) AllianceCharacter(height = len);
                translate([ 0, 0, alliance_width / 2 ])
                    cuboid([ len, alliance_length, alliance_width / 2 + 4.5 ], anchor = TOP);
            }
            translate([ len / 2, alliance_length / 2 + 2 + alliance_length + 4, $inner_height - alliance_width / 2 ])
            {
                rotate([ 0, 270, 0 ]) AllianceCharacter(height = len);
                translate([ 0, 0, alliance_width / 2 ])
                    cuboid([ len, alliance_length, alliance_width / 2 + 4.5 ], anchor = TOP);
            }
        }
    }
    if (generate_lid)
    {
        translate([ alliance_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = alliance_box_width, length = alliance_box_length, height = alliance_box_height,
                               text_width = 70, text_height = 20, text_str = "Alliance", label_rotated = true);
        }
    }
}

module AllianceBoxTop(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = alliance_box_width, length = alliance_box_length, height = alliance_box_top_height)
    {
        // Score marker.
        translate([ square_tile_size / 2, square_tile_size / 2, $inner_height - tile_thickness - 0.5 ])
            CuboidWithIndentsBottom(size = [ square_tile_size, square_tile_size, tile_thickness + 1 ],
                                    finger_hole_radius = 10, finger_holes = [0]);

        // Sympathy tokens.
        translate([
            $inner_width - round_tile_diameter / 2, round_tile_diameter / 2 + 1,
            $inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 + 0.5
        ]) CylinderWithIndents(radius = round_tile_diameter / 2,
                               height = tile_thickness * woodland_aliance_sympathy_num / 2 + 1, finger_hole_radius = 8,
                               finger_holes = [135]);
        translate([
            $inner_width - round_tile_diameter / 2, $inner_length - round_tile_diameter / 2 - 1,
            $inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 + 0.5
        ]) CylinderWithIndents(radius = round_tile_diameter / 2,
                               height = tile_thickness * woodland_aliance_sympathy_num / 2 + 1, finger_hole_radius = 8,
                               finger_holes = [225]);

        // Bases.
        translate([
            square_tile_size / 2, $inner_length - square_tile_size / 2,
            $inner_height - tile_thickness * woodland_alliance_base_num - 0.5
        ])
            CuboidWithIndentsBottom(
                [ square_tile_size, square_tile_size, tile_thickness * woodland_alliance_base_num + 1 ],
                finger_hole_radius = 7, finger_holes = [0]);
    }
    if (generate_lid)
    {
        translate([ alliance_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = alliance_box_width, length = alliance_box_length,
                               height = alliance_box_top_height, text_width = 70, text_height = 20,
                               text_str = "Alliance", label_rotated = true);
        }
    }
}

module RiverfolkBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = riverfolk_box_width, length = riverfolk_box_length, height = riverfolk_box_height)
    {
        len = player_token_thickness * 5 + 1;
        translate([ 0, 0, 0 ]) for (i = [0:1:2])
        {
            translate(
                [ len / 2, riverfolk_width / 2 + (riverfolk_width + 1) * i, $inner_height - riverfolk_length / 2 ])
            {
                rotate([ 90, 0, 90 ]) RiverfolkCharacter(height = len + 1);
                translate([ 0, 0, riverfolk_length / 2 ])
                    cuboid([ len + 1, riverfolk_width, riverfolk_length - 3 ], anchor = TOP);
            }
        }
    }
    if (generate_lid)
    {
        translate([ riverfolk_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = riverfolk_box_width, length = riverfolk_box_length,
                               height = riverfolk_box_height, text_width = 70, text_height = 20, text_str = "Riverfolk",
                               label_rotated = true);
        }
    }
}

module RiverfolkBoxTop(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = riverfolk_box_top_width, length = riverfolk_box_length, height = riverfolk_box_top_height)
    {
        // Score marker.
        translate([ square_tile_size / 2, square_tile_size / 2, $inner_height - tile_thickness - 0.5 ])
        {
            CuboidWithIndentsBottom(size = [ square_tile_size, square_tile_size, tile_thickness + 1 ],
                                    finger_hole_radius = 10, finger_holes = [2]);
        }

        // trading posts.
        for (i = [0:1:2])
        {
            translate([
                $inner_width - round_tile_diameter / 2 - (round_tile_diameter + 2) * i - 2, round_tile_diameter / 2 + 2,
                $inner_height - tile_thickness * 5 + 0.5
            ]) CylinderWithIndents(radius = (round_tile_diameter + 0.5) / 2, height = tile_thickness * 5 + 1,
                                   finger_hole_radius = 8, finger_holes = [90]);
        }

        // glass things.
        translate([ ($inner_width - (riverfolk_glass_diameter + 10) * 3) / 2, 0, 0 ]) for (i = [0:1:2])
        {
            translate([
                2 + riverfolk_glass_diameter / 2 + (riverfolk_glass_diameter + 10) * i,
                $inner_length - riverfolk_glass_diameter / 2 - 2, $inner_height - riverfolk_glass_thickness - 0.5
            ])
            {
                CylinderWithIndents(radius = riverfolk_glass_diameter / 2, height = riverfolk_glass_thickness + 1,
                                    finger_hole_radius = 8, finger_holes = [ 0, 180 ]);
            }
        }
    }
    if (generate_lid)
    {
        translate([ riverfolk_box_top_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = riverfolk_box_top_width, length = riverfolk_box_length,
                               height = riverfolk_box_height, text_width = 70, text_height = 20, text_str = "Riverfolk",
                               label_rotated = true);
        }
    }
}

module LizardBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = lizard_box_width, length = lizard_box_length, height = lizard_box_height)
    {
        //  Put a bunch of places in for the lizard items
        for (j = [0:1:4])
        {
            for (i = [0:1:4])
            {
                translate([
                    (lizard_width + 1.8) * i + lizard_width / 2,
                    (player_token_thickness + 0.1) * j + player_token_thickness / 2 + 1.5, lizard_length / 2 - 0.25
                ])
                {
                    rotate([ 90, 0, 0 ]) LizardCharacter(height = player_token_thickness + 0.5);
                }
            }
        }
        translate([ 0, 0, lizard_length / 2 ])
            RoundedBoxAllSides($inner_width, lizard_box_length - wall_thickness * 2, lizard_length, 7);
    }
    if (generate_lid)
    {
        translate([ lizard_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = lizard_box_width, length = lizard_box_length, height = lizard_box_height,
                               text_width = 70, text_height = 20, text_str = "Lizard", label_rotated = true);
        }
    }
}

module LizardBoxTop(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = lizard_box_top_width, length = lizard_box_length, height = lizard_box_top_height)
    {
        // Garden markers.
        for (i = [0:1:1])
        {
            translate([
                square_tile_size / 2 + (square_tile_size + 5) * i + 3, square_tile_size / 2 + 2,
                $inner_height - tile_thickness * 5 - 0.5
            ]) CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness * 5 + 1 ],
                                       finger_hole_radius = 8, finger_holes = [2]);
        }
        translate([
            square_tile_size / 2 + (square_tile_size + 5) * 1 + 3, $inner_length - square_tile_size + 2,
            $inner_height - tile_thickness * 5 - 0.5
        ]) CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness * 5 + 1 ],
                                   finger_hole_radius = 8, finger_holes = [6]);

        // Score marker.
        translate(
            [ square_tile_size / 2, $inner_length - square_tile_size / 2, $inner_height - tile_thickness * 2 - 0.5 ])
            CuboidWithIndentsBottom([ square_tile_size, square_tile_size, tile_thickness * 2 + 1 ],
                                    finger_hole_radius = 8, finger_holes = [6]);
    }
    if (generate_lid)
    {
        translate([ lizard_box_top_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = lizard_box_top_width, length = lizard_box_length, height = lizard_box_top_height,
                               text_width = 70, text_height = 20, text_str = "Lizard", label_rotated = true);
        }
    }
}

module ItemsBoxBottom(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_height,
                      finger_hold_height = 3)
    {
        depths = [
            "torch", 2, "boot",          3, "coins", 1, "crossbow", 2, "sword", 3,
            "bag",   1, "hammer/teapot", 2, "ruins", 3, "ruins",    3, "ruins", 2
        ];
        for (i = [0:1:4])
        {
            if (depths[i * 4 + 1] != 0)
            {
                translate([
                    square_tile_size / 2, (square_tile_size + 1) * i + square_tile_size / 2,
                    $inner_height - tile_thickness * depths[i * 4 + 1] - 0.5
                ])
                {
                    CuboidWithIndentsBottom(
                        [ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1 ],
                        finger_hole_radius = 6, finger_holes = [0]);
                    translate([ 0, 0, -0.5 ])
                    {
                        GenerateIcon(depths[i * 4]);
                        translate([ square_tile_size * 4 / 10, 0, 0 ]) linear_extrude(height = 2) rotate(90)
                            text(text = depths[i * 4] == "ruins" ? "R" : "S", font = "Stencil Std:style=Bold", size = 2,
                                 halign = "center", valign = "center");
                    }
                }
            }
            if (depths[i * 4 + 3] != 0)
            {
                translate([
                    $inner_width - square_tile_size + square_tile_size / 2,
                    (square_tile_size + 1) * i + square_tile_size / 2,
                    $inner_height - tile_thickness * depths[i * 4 + 3] - 0.5
                ])
                {
                    CuboidWithIndentsBottom(
                        [ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1 ],
                        finger_hole_radius = 6, finger_holes = [4]);
                    translate([ 0, 0, -0.5 ])
                    {
                        GenerateIcon(depths[i * 4 + 2]);
                        translate([ square_tile_size * 4 / 10, 0, 0 ]) linear_extrude(height = 2) rotate(90)
                            text(text = depths[i * 4 + 2] == "ruins" ? "R" : "S", font = "Stencil Std:style=Bold",
                                 size = 2, halign = "center", valign = "center");
                    }
                }
            }
        }
    }
    if (generate_lid)
    {
        translate([ item_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = item_box_width, length = item_box_length, height = item_box_height,
                               text_width = 70, text_height = 20, text_str = "Items", label_rotated = true);
        }
    }
}

module GenerateIcon(icon, height = 2)
{
    if (icon == "bag")
    {
        linear_extrude(height = height) Bag2d(10);
    }
    else if (icon == "boot")
    {
        linear_extrude(height = height) Shoe2d(10);
    }
    else if (icon == "torch")
    {
        linear_extrude(height = height) Torch2d(10, 3);
    }
    else if (icon == "crossbow")
    {
        linear_extrude(height = height) Crossbow2d(10, 8);
    }
    else if (icon == "hammer/teapot")
    {
        translate([ 0, -5, 0 ]) linear_extrude(height = height) rotate(90) Sledgehammer2d(10, 5);
        translate([ 0, 3, 0 ]) linear_extrude(height = height) Teapot2d(10, 8);
    }
    else if (icon == "hammer")
    {
        linear_extrude(height = height) Sledgehammer2d(10, 5);
    }
    else if (icon == "sword")
    {
        linear_extrude(height = height) Sword2d(10, 5);
    }
    else if (icon == "teapot")
    {
        linear_extrude(height = height) Teapot2d(10, 8);
    }
    else if (icon == "coins")
    {
        linear_extrude(height = height) CoinPile2d(10);
    }
    else if (icon == "ruins")
    {
        linear_extrude(height = height) rotate(90) Ruins2d(10);
    }
    else if (icon == "n/a")
    {
        linear_extrude(height = height) rotate(90)
            text(text = icon, font = "Stencil Std:style=Bold", size = 2.5, halign = "center", valign = "center");
    }
}

module ItemsBoxMiddle(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_middle_height,
                      finger_hold_height = 3, cap_height = 5)
    {
        // 12 craftable items (2× bag, 2× boot, 1× crossbow, 1× hammer, 2× sword, 2× teapot, 2× coins)
        depths = [
            "bag",    2, "boot",  2, "crossbow", 1, "hammer", 1, "sword", 2,
            "teapot", 2, "coins", 2, "n/a",      0, "ruins",  2, "ruins", 2
        ];
        for (i = [0:1:4])
        {
            if (depths[i * 4 + 1] != 0)
            {
                translate([
                    square_tile_size / 2, (square_tile_size + 01) * i + square_tile_size / 2,
                    $inner_height - tile_thickness * depths[i * 4 + 1] - 0.5
                ])
                {
                    CuboidWithIndentsBottom(
                        [ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1 ],
                        finger_hole_radius = 6, finger_holes = [0]);

                    translate([ 0, 0, -0.5 ]) GenerateIcon(depths[i * 4]);
                }
            }
            if (depths[i * 4 + 3] != 0)
            {
                translate([
                    $inner_width - square_tile_size + square_tile_size / 2,
                    (square_tile_size + 1) * i + square_tile_size / 2,
                    $inner_height - tile_thickness * depths[i * 4 + 3] - 0.5
                ])
                {
                    CuboidWithIndentsBottom(
                        [ square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1 ],
                        finger_hole_radius = 6, finger_holes = [4]);
                    translate([ 0, 0, -0.5 ]) GenerateIcon(depths[i * 4 + 2]);
                }
            }
        }
    }
    if (generate_lid)
    {
        translate([ item_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = item_box_width, length = item_box_length, height = item_box_middle_height,
                               text_width = 70, text_height = 20, text_str = "Items", label_rotated = true,
                               cap_height = 5);
        }
    }
}

module ItemsBoxWinter(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_winter_height,
                      finger_hold_height = 3)
    {
        for (i = [0:1:5])
        {
            translate([ $inner_width / 2, round_winter_thing_length / 2 + (round_winter_thing_length + 1) * i, 0 ])
            {
                rotate([ 0, 0, 90 ]) WinterToken(tile_thickness * 2 + 1);
                translate([ round_winter_thing_width / 2, -5, 0 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ -round_winter_thing_width / 2, -5, 0 ]) sphere(r = 8, anchor = BOTTOM);
            }
        }
    }
    if (generate_lid)
    {
        translate([ item_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = item_box_width, length = item_box_length, height = item_box_winter_height,
                               text_width = 70, text_height = 20, text_str = "Winter", label_rotated = true);
        }
    }
}

module DiceBox(generate_lid = true) // `make` me
{
    $inner_height = dice_box_height - lid_thickness * 2;
    $inner_width = dice_box_width - wall_thickness * 2;
    $inner_length = dice_box_length - wall_thickness * 2;
    MakeBoxWithCapLid(width = dice_box_width, length = dice_box_length, height = dice_box_height)
    {
        translate([ dice_width / 2 + 3, dice_width / 2 + 3, dice_width / 2 ])
        {
            Dodecahedron(dice_width);
            translate([ 0, 0, dice_width / 2 ]) cyl(d = dice_length, h = dice_box_height);
        }

        translate([ $inner_width - dice_width / 2 - 3, $inner_length - dice_width / 2 - 3, dice_width / 2 ])
        {
            Dodecahedron(dice_width);
            translate([ 0, 0, dice_width / 2 ]) cyl(d = dice_length, h = dice_box_height);
        }
        translate([ 0, 0, dice_width / 2 ])
            RoundedBoxAllSides(width = $inner_width, length = $inner_length, height = dice_box_height, radius = 10);
    }
    if (generate_lid)
    {
        translate([ item_box_width + 10, 0, 0 ])
        {
            CapBoxLid(width = dice_box_width, length = dice_box_length, height = dice_box_height)
            {
                translate([ 10, 10, 0 ])
                    LidMeshBasic(width = dice_box_width, length = dice_box_length, lid_thickness = lid_thickness,
                                 boundary = 10, layout_width = default_lid_layout_width,
                                 shape_type = default_lid_shape_type, shape_width = default_lid_shape_width,
                                 shape_thickness = default_lid_shape_thickness, aspect_ratio = 1.0);

                translate([ (dice_box_width) / 2, (dice_box_length) / 2, 0 ]) linear_extrude(height = lid_thickness)
                    D20Outline2d(20, 1);
            }
        }
    }
}

module ItemsBoxExtras(generate_lid = true) // `make` me
{
    module RenderItem(item)
    {
        if (item[2] == "square")
        {
            translate([ slightly_larger_round_tile_diameter / 2, slightly_larger_round_tile_diameter / 2, 0 ])
            {
                CuboidWithIndentsBottom([ larger_square_tile_, larger_square_tile_, tile_thickness * item[1] + 1 ],
                                        finger_hole_radius = 6, finger_holes = [item[3] == 1 ? 0 : 4]);
            }
        }
        else
        {
            translate([ slightly_larger_round_tile_diameter / 2, slightly_larger_round_tile_diameter / 2, 0 ])
            {
                CylinderWithIndents(radius = slightly_larger_round_tile_diameter / 2,
                                    height = tile_thickness * item[1] + 1, finger_hole_radius = 6,
                                    finger_holes = [item[3] == 1 ? 0 : 180]);
            }
        }
        translate([ (slightly_larger_round_tile_diameter) / 2, slightly_larger_round_tile_diameter / 2, -0.5 ])
            linear_extrude(height = 2) rotate(90)
                text(text = item[0], font = "Stencil Std:style=Bold", size = 2.5, halign = "center", valign = "center");
    }

    MakeBoxWithCapLid(width = item_box_width, length = item_box_length, height = item_box_extras_height,
                      finger_hold_height = 3)
    {
        $inner_height = item_box_extras_height - lid_thickness * 2;
        $inner_width = item_box_width - wall_thickness * 2;
        // 12 craftable items (2× bag, 2× boot, 1× crossbow, 1× hammer, 2× sword, 2× teapot, 2× coins)
        depths = [
            [ "A/B", 2, "round", 1 ],
            [ "C/D", 2, "round", -1 ],
            [ "E/F", 2, "round", 1 ],
            [ "G/H", 2, "square", -1 ],
            [ "I/J", 2, "square", 1 ],
            [ "K/L", 2, "square", -1 ],
            [ "M/N", 2, "square", 1 ],
            [ "O/P", 2, "square", -1 ],
        ];
        for (i = [0:1:3])
        {
            if (depths[i * 2][1] != 0)
            {
                translate([
                    0, (slightly_larger_round_tile_diameter + 3.6) * i + 1,
                    $inner_height - tile_thickness * depths[i * 2][1] - 0.5
                ])
                {
                    RenderItem(depths[i * 2]);
                }
            }
            if (depths[i * 2 + 1][1] != 0)
            {
                translate([
                    $inner_width - slightly_larger_round_tile_diameter,
                    (slightly_larger_round_tile_diameter + 3.6) * i + 1,
                    $inner_height - tile_thickness * depths[i * 2 + 1][1] - 0.5
                ])
                {
                    RenderItem(depths[i * 2 + 1]);
                }
            }
        }
    }
    if (generate_lid)
    {
        translate([ item_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = item_box_width, length = item_box_length, height = item_box_extras_height,
                               text_width = 70, text_height = 20, text_str = "Items", label_rotated = true);
        }
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        CardBox(generate_lid = false);
        translate([ card_box_width, 0, 0 ]) ItemsBoxBottom(generate_lid = false);
        translate([ card_box_width, 0, item_box_height ]) ItemsBoxMiddle(generate_lid = false);
        translate([ card_box_width, 0, item_box_height + item_box_middle_height ]) ItemsBoxWinter(generate_lid = false);
        translate([ card_box_width, 0, item_box_height + item_box_middle_height + item_box_winter_height ])
            ItemsBoxExtras(generate_lid = false);
        translate([ 0, card_box_length, 0 ]) MarquisBoxBottom(generate_lid = false);
        translate([ marquis_box_width, card_box_length, 0 ]) AllianceBoxBottom(generate_lid = false);
        translate([ marquis_box_width, card_box_length, alliance_box_height ]) AllianceBoxTop(generate_lid = false);
        translate([ 0, card_box_length, marquis_box_height ]) MarquisBoxTop(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length, 0 ]) ErieBoxBottom(generate_lid = false);
        translate([ erie_box_width, card_box_length + erie_box_length, 0 ]) VagabondBox(generate_lid = false);
        translate([ erie_box_width, card_box_length + erie_box_length, vagabond_box_height ])
            VagabondBox(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length, erie_box_height ]) ErieBoxTop(generate_lid = false);
        translate([ erie_box_width, card_box_length + marquis_box_length + erie_box_length, 0 ])
            RiverfolkBoxBottom(generate_lid = false);
        translate(
            [ lizard_box_top_width, card_box_length + marquis_box_length + erie_box_length, riverfolk_box_height ])
            RiverfolkBoxTop(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length + erie_box_length, 0 ])
            LizardBoxBottom(generate_lid = false);
        translate([ 0, card_box_length + marquis_box_length + erie_box_length, lizard_box_height ])
            LizardBoxTop(generate_lid = false);
    }
}

if (FROM_MAKE != 1)
{
    SideEye2d(0);
}