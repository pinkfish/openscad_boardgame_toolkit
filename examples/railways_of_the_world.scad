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

card_width = 68;
card_length = 92;
bond_width = 59;
bond_length = 78;
bond_card_thickness = 17;
train_card_width = 58;
train_card_length = 90;
train_card_thickness = 2;
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
sweden_bonus_length = 35;
sweden_bonus_width = 16;
australia_switch_track_token_radius = 8;

eastern_us_cards = 12 + 31 + 6 + 2;
mexico_cards = 12 + 38 + 4;
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

all_boxes_height = card_width + wall_thickness + lid_thickness;

card_box_length = card_length + wall_thickness * 2 + 1;

eastern_us_card_box_width =
    eastern_us_cards * single_card_thickness + bond_card_thickness + inner_wall + wall_thickness * 2;

player_box_width = (box_length - card_box_length - 2) / 3;
player_box_length = train_card_width + silo_piece_height * 2 + roundhouse_height + inner_wall * 2 + wall_thickness * 2;
player_box_height = silo_piece_width + lid_thickness * 2;
player_box_silo_lid_hole_first = 81;
player_box_silo_lid_hole_second = 121;
player_box_silo_lid_hole_size = 4;

top_section_height = all_boxes_height - player_box_height * 2;
top_section_width = box_length - card_box_length - 2;

western_us_expansion_box_width = 41;

money_section_width = money_width + 1.5 + wall_thickness * 2;
money_section_length = money_length + 1.5 + wall_thickness * 2;

hex_box_width = money_section_length;
hex_box_length = tile_width * 5 + wall_thickness * 2;

new_city_box_length = money_section_width;
new_city_box_width = money_section_length;

empty_city_width = 47;
empty_city_length = (player_box_width * 3) / 2 - 0.5;
empty_city_height = player_box_height * 2;

player_box_trains_length = box_width - empty_city_width - player_box_length - 2;

expansion_area_box_width = box_width - hex_box_width;

sweden_box_width = expansion_area_box_width;
sweden_box_length = 3 * tile_width + sweden_bonus_width + wall_thickness * 2 + inner_wall;

australia_box_width = expansion_area_box_width;
australia_box_length = 4 * tile_width + australia_switch_track_token_radius * 2 + wall_thickness * 2 + inner_wall / 2;

echo([ top_section_height, new_city_box_width, new_city_box_length, box_width - money_section_length*2 ]);

module CardBoxEasternUS(generate_lid = true)
{
    MakeBoxWithSlidingLid(length = card_box_length, width = eastern_us_card_box_width, height = all_boxes_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        difference()
        {
            cube([
                eastern_us_card_box_width - wall_thickness * 2, card_box_length - wall_thickness * 2, all_boxes_height -
                lid_thickness
            ]);

            // Bond section.
            translate([ -inner_wall, 0, 0 ]) difference()
            {
                cube([
                    bond_card_thickness + inner_wall * 2, card_box_length - wall_thickness * 2, all_boxes_height -
                    lid_thickness
                ]);
                translate(
                    [ inner_wall, (card_box_length - wall_thickness * 2 - bond_length) / 2, card_width - bond_width ])
                    cube([ bond_card_thickness, bond_length, bond_width + wall_thickness + 1 ]);
            }
        }

        translate(
            [ eastern_us_card_box_width / 2, card_box_length / 2, all_boxes_height - 28 + 0.01 - lid_thickness / 2 ])
            FingerHoleWall(radius = 25, height = 28, depth_of_hole = eastern_us_card_box_width + 2, orient = UP,
                           spin = 90, rounding_radius = 5);
    }

    if (generate_lid)
    {
        text_str = "Eastern US";
        text_width = 80;
        text_height = 20;
        translate([ eastern_us_card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = card_box_length, length = eastern_us_card_box_width, lid_thickness = lid_thickness,
            text_width = text_width, text_height = text_height, text_str = text_str, label_rotated = true);
    }
}

module CardBox(num_cards, text_str, generate_lid = true)
{
    box_width = num_cards + single_card_thickness + wall_thickness * 2;
    MakeBoxWithSlidingLid(width = box_width, length = card_box_length, height = all_boxes_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        cube(
            [ box_width - wall_thickness * 2, card_box_length - wall_thickness * 2, all_boxes_height - lid_thickness ]);
        translate([ box_width / 2, card_box_length / 2, all_boxes_height - 28 + 0.01 - lid_thickness / 2 ])
            FingerHoleWall(radius = 25, height = 28, depth_of_hole = box_width + 2, orient = UP, spin = 90,
                           rounding_radius = 5);
    }
    if (generate_lid)
    {
        text_width = 70;
        text_height = 20;
        translate([ card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = box_width, length = card_box_length, lid_thickness = lid_thickness, text_width = text_width,
            text_height = text_height, text_str = text_str, label_rotated = true) children();
    }
}

module CardBoxAustralia(generate_lid = true)
{
    CardBox(australia_cards, "Australia", generate_lid = generate_lid)
    {
        translate([ 20, 0, 0 ]) linear_extrude(height = lid_thickness) scale(0.3) difference()
        {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
        }
    }
}

module CardBoxMexico(generate_lid = true)
{
    CardBox(mexico_cards, "Mexico", generate_lid = generate_lid);
}

module CardBoxSweden(generate_lid = true)
{
    CardBox(sweden_cards, "Sweden", generate_lid = generate_lid);
}

module PlayerBox(generate_lid = true)
{
    card_height = train_card_thickness * 4.5;
    MakeBoxWithInsetLidTabbed(width = player_box_width, length = player_box_length, height = player_box_height,
                              lid_thickness = lid_thickness, wall_thickness = wall_thickness, floor_thickness = 1)
    {
        // Round houses.
        difference()
        {
            cube([ player_box_width - wall_thickness * 2, roundhouse_height, player_box_height ]);

            translate([ (player_box_width - wall_thickness * 2) / 2 - 7, wall_thickness * 3, 0 ])
                linear_extrude(height = 0.5) import("svg/rotw - roundhouse.svg");
        }
        // water tower.
        difference()
        {
            translate([ 0, roundhouse_height + inner_wall, 0 ]) cube([
                player_box_width - wall_thickness * 2 - mine_width - inner_wall - 5, silo_piece_height * 2,
                player_box_height
            ]);
            translate([
                wall_thickness + silo_piece_width,
                wall_thickness + roundhouse_height + inner_wall + silo_piece_height / 2, 0
            ]) linear_extrude(height = 0.5) import("svg/rotw - water.svg");
        }
        // mine section.
        difference()
        {
            translate([
                player_box_width - wall_thickness * 3 - mine_width + inner_wall - 4, roundhouse_height + inner_wall, 0
            ]) cube([ mine_width + 4, silo_piece_height * 2, player_box_height ]);
            // Offset in here fixes the error in the svg file.
            translate([
                player_box_width - wall_thickness * 2 - mine_width + inner_wall,
                roundhouse_height + inner_wall + silo_piece_height / 2, 0
            ]) linear_extrude(height = 0.5) offset(delta = 0.001) import("svg/rotw - mine.svg");
        }
        // cards.
        translate([
            0,
            roundhouse_height + inner_wall * 2 + silo_piece_height * 2,
            player_box_height - lid_thickness - card_height - 1,
        ]) cube([ train_card_length, train_card_width, player_box_height ]);
        // Recessed box for crossings.
        difference()
        {
            translate(
                [ player_box_width * 1 / 8 + 4, roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + 7, 0 ])
                difference()
            {
                cube([ player_box_width * 3 / 4, crossing_length * 1.25, player_box_height + 1 ]);
                translate([ 25, 5, 0 ]) linear_extrude(height = 0.5) import("svg/rotw - signal.svg");
            }
        }
        translate([
            wall_thickness - 0.3,
            roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + crossing_length * 1.25 / 2 + 16, 0
        ]) FingerHoleBase(radius = 10, height = player_box_height - 1 + 0.01, wall_thickness = wall_thickness * 2,
                          spin = 270, rounding_radius = 5, floor_thickness = 1);
    };

    if (generate_lid)
    {
        text_str = "Player";
        text_width = 80;
        text_height = 30;
        translate([ player_box_width + 10, 0, 0 ])
        {
            difference()
            {
                InsetLidTabbedWithLabel(width = player_box_width, length = player_box_length,
                                        lid_thickness = lid_thickness, text_width = text_width,
                                        text_height = text_height, text_str = text_str, label_rotated = true);
                translate(
                    [ player_box_width - 56, player_box_silo_lid_hole_first - player_box_silo_lid_hole_size, 0.5 ])
                    cube([ 50, player_box_silo_lid_hole_size, lid_thickness + 1 ]);
                translate(
                    [ player_box_width - 56, player_box_silo_lid_hole_second - player_box_silo_lid_hole_size, 0.5 ])
                    cube([ 50, player_box_silo_lid_hole_size, lid_thickness + 1 ]);
            }
        }
    }
}

module PlayerBoxTrains(generate_lid = true)
{
    MakeBoxWithSlidingLid(width = player_box_width, length = player_box_trains_length, height = player_box_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness, floor_thickness = 1)
    {
        cube([
            player_box_width - wall_thickness * 2, player_box_trains_length - 2 * wall_thickness,
            empty_city_height
        ]);
    }
    if (generate_lid)
    {
        text_str = "Trains";
        text_width = 60;
        text_height = 20;
        translate([ player_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = player_box_width, length = player_box_trains_length, lid_thickness = lid_thickness,
            text_width = text_width, text_height = text_height, text_str = text_str, label_rotated = false);
    }
}

module EmptyCityBox(generate_lid = true)
{
    MakeBoxWithSlidingLid(width = empty_city_width, length = empty_city_length, height = empty_city_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        cube([ empty_city_width - wall_thickness * 2, empty_city_length - 2 * wall_thickness, empty_city_height ]);
    }
    if (generate_lid)
    {
        text_str = "Empty City";
        text_width = 80;
        text_height = 20;
        translate([ empty_city_width + 10, 0, 0 ])
            SlidingLid(empty_city_width, empty_city_length, lid_thickness = lid_thickness)
        {
            translate([ 10, 10, 0 ]) LidMeshHex(width = empty_city_width, length = empty_city_length,
                                                lid_thickness = lid_thickness, boundary = 10, radius = 12);
            translate([ (empty_city_width + text_height) / 2, (empty_city_length - text_width) / 2, 0 ])
                rotate([ 0, 0, 90 ])
                    MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                        label = text_str, border = wall_thickness, offset = 4);
        }
    }
}

module MoneyBox(generate_lid = true)
{
    MakeBoxWithSlidingLid(width = money_section_width, length = money_section_length, height = top_section_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        cube([ money_width, money_length, empty_city_height ]);

        translate([ money_section_width / 2 - 15, 0, top_section_height - 20 ])
            FingerHoleBase(radius = 15, height = 20);
    }
    if (generate_lid)
    {
        text_str = "Money";
        text_width = 80;
        text_height = 20;
        translate([ money_section_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = money_section_width, length = money_section_length, lid_thickness = lid_thickness,
            text_width = text_width, text_height = text_height, text_str = text_str, label_rotated = true);
    }
}

module HexBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = hex_box_width, length = hex_box_length, height = top_section_height)
    {
        HexGridWithCutouts(rows = 4, cols = 5, height = top_section_height, spacing = 0, push_block_height = 0.25,
                           tile_width = tile_width);
    }
    if (generate_lid)
    {
        text_str = "Tracks";
        text_width = 80;
        text_height = 20;
        translate([ 6.5 * tile_width, 0, 0 ])
            CapBoxLidWithLabel(width = hex_box_width, length = hex_box_length, height = top_section_height,
                               text_width = text_width, text_height = text_height, text_str = text_str);
    }
}

module NewCityBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = new_city_box_width, length = new_city_box_length, height = top_section_height,
                      lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        translate([ 2, 2.5, 0 ])
        {
            translate([ 0, 0, top_section_height - lid_thickness - tile_thickness * 4 - wall_thickness ])
                RegularPolygonGrid(width = tile_width, rows = 2, cols = 2, spacing = 0)
            {
                RegularPolygon(width = tile_width, height = tile_thickness * 4.25, shape_edges = 6);
                cyl(r = 10, h = 20, $fn = 64);
            }
            translate([ tile_radius * 2, tile_width / 2, 14 ]) sphere(r = 10, $fn = 64);
            translate([ tile_radius * 2, tile_width * 3 / 2, 14 ]) sphere(r = 10, $fn = 64);
            translate([
                3 + tile_radius * 5, tile_width, top_section_height - lid_thickness - tile_thickness * 2.5 -
                wall_thickness
            ])
            {
                RegularPolygon(width = tile_width, height = top_section_height, shape_edges = 6);
                translate([ 0, -tile_width / 2, 10 ]) sphere(r = 10);
            }
        }
        translate([ tile_radius * 7, 12, top_section_height - lid_thickness - 10 - wall_thickness ])
            cube([ 15.5, 40, 11 ]);
    }
    if (generate_lid)
    {
        text_str = "New Cities";
        text_width = 80;
        text_height = 20;
        translate([ new_city_box_width + 10, 0, 0 ]) CapBoxLidWithLabel(
            width = new_city_box_width, length = new_city_box_length, height = top_section_height, lid_thickness = lid_thickness,
            text_width = text_width, text_height = text_height, text_str = text_str, label_rotated = true);
    }
}

module SwedenBox()
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(width = sweden_box_width, length = sweden_box_length, height = top_section_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        intersection()
        {
            translate([ 0, 0, -3 ]) cube([ radius * 4 * 2, tile_width * 3, top_section_height + 1 ]);
            HexGridWithCutouts(rows = 4, cols = 3, tile_width = tile_width, spacing = 0,
                               wall_thickness = wall_thickness, push_block_height = 0.75, height = top_section_height);
        }
        // bonus bit (top)
        translate([
            wall_thickness, sweden_box_length - wall_thickness * 2 - sweden_bonus_width,
            top_section_height - lid_thickness - tile_thickness * 2.4 -
            wall_thickness
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            (sweden_bonus_length - 10) / 2, sweden_box_length - wall_thickness * 2 - sweden_bonus_width - 5,
            top_section_height - lid_thickness - tile_thickness * 2.4 -
            wall_thickness
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (middle)
        translate([
            sweden_box_width - wall_thickness - sweden_bonus_length,
            sweden_box_length - wall_thickness * 2 - sweden_bonus_width,
            top_section_height - lid_thickness - tile_thickness * 2.4 -
            wall_thickness
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            sweden_box_width - wall_thickness * 2 - sweden_bonus_length + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_thickness - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (bottom)
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_thickness - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2 + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_thickness - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);
    }
    if (generate_lid)
    {
        text_str = "Sweden";
        text_width = 80;
        text_height = 20;
        translate([ sweden_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = sweden_box_width, length = sweden_box_length, lid_thickness = lid_thickness,
                                   text_width = text_width, text_height = text_height, text_str = text_str,
                                   label_rotated = false) translate([ 84, 58, 0 ]) scale(0.25) rotate([ 0, 0, 90 ])
                linear_extrude(height = lid_thickness) difference()
        {
            // Offset fixes the svg error.
            offset(delta = 0.001) import("svg/sweden.svg");
            offset(-4) import("svg/sweden.svg");
        }
    }
}

module AustraliaBox(generate_lid = true)
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(width = australia_box_width, length = australia_box_length, height = top_section_height,
                          lid_thickness = lid_thickness, wall_thickness = wall_thickness)
    {
        intersection()
        {
            translate([ 0, 0, -3 ]) cube([ radius * 4 * 2, tile_width * 3, top_section_height + 1 ]);
            difference()
            {

                HexGridWithCutouts(rows = 4, cols = 3, tile_width = tile_width, spacing = 0,
                                   wall_thickness = wall_thickness, push_block_height = 0.75,
                                   height = top_section_height);
                // Cut out the bottom square to put the bonus tiles in.
                translate([ 3 * radius * 2, 2 * apothem * 2, -wall_thickness ])
                    cube([ radius * 2, tile_width, top_section_height ]);
            }
        }

        // Cutouts for the bonus cards.
        translate([
            (australia_box_width - wall_thickness * 3 - sweden_bonus_width), tile_width * 2 + wall_thickness,
            top_section_height - lid_thickness - tile_thickness * 6.4
        ]) cube([ sweden_bonus_width, sweden_bonus_length, tile_thickness * 6.5 ]);
        // Fingercut for the bonus cards.
        translate([
            (australia_box_width - wall_thickness * 2 - sweden_bonus_width) + 8 - wall_thickness, tile_width * 2,
            top_section_height / 2 + 4.3
        ]) cyl(h = top_section_height, r = 5);

        // New citites
        translate([
            radius, australia_box_length - tile_width + apothem,
            top_section_height - lid_thickness - tile_thickness * 5.4 -
            wall_thickness
        ])
        {
            RegularPolygon(shape_edges = 6, width = tile_width, height = tile_thickness * 5.5);
            translate([ 0, 0, -10 ]) cylinder(r = 8, h = 15);
        }
        translate([
            radius + radius * 2, australia_box_length - tile_width + apothem,
            top_section_height - lid_thickness - tile_thickness * 5.4 -
            wall_thickness
        ])
        {
            RegularPolygon(shape_edges = 6, width = tile_width, height = tile_thickness * 5.5);
            translate([ 0, 0, -10 ]) cylinder(r = 8, h = 15);
        }
        translate([
            radius * 2 - 6, australia_box_length - tile_width + apothem - 6,
            top_section_height - lid_thickness - tile_thickness * 5.4 -
            wall_thickness
        ]) cube([ 12, 12, tile_thickness * 5.5 ]);
        // For the switch track tokens.
        for (i = [0:1:5])
            translate([
                australia_switch_track_token_radius + (australia_switch_track_token_radius * 2 + inner_wall) * i,
                australia_box_length - wall_thickness - australia_switch_track_token_radius - tile_width,
                top_section_height - lid_thickness - tile_thickness * 2.4 / 2 -
                wall_thickness
            ])
            {
                cyl(r = australia_switch_track_token_radius, h = tile_thickness * 5);
                translate([
                    -australia_switch_track_token_radius / 2, -australia_switch_track_token_radius - 1 - wall_thickness,
                    -(tile_thickness * 5) / 2
                ])
                    cube([
                        australia_switch_track_token_radius, australia_switch_track_token_radius, tile_thickness * 5
                    ]);
            }
        // Map in the top section.
        translate(
            [ player_box_width - 20, player_box_length - 90, top_section_height - lid_thickness - 1 - wall_thickness ])
            scale(0.3) linear_extrude(height = 30) difference()
        {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
        }
    }
    if (generate_lid)
    {
        text_str = "Australia";
        text_width = 80;
        text_height = 20;
        translate([ australia_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = australia_box_width, length = australia_box_length,
                                   lid_thickness = lid_thickness, text_width = text_width, text_height = text_height,
                                   text_str = text_str, label_rotated = false) translate([ 44, 15, 0 ])
                linear_extrude(height = lid_thickness) scale(0.3) difference()
        {
            fill() import("svg/australia.svg");
            offset(-4) fill() import("svg/australia.svg");
        }
    }
}

module EmptyCityModel()
{
    cyl(h = 6, d = 27, anchor = BOTTOM);
    cyl(h = 48, d = 3.5, anchor = BOTTOM);
    translate([ 0, 3.5, 20 ]) ycyl(h = 3, d = 15, anchor = TOP + BACK);
    translate([ 0, 3.5, 34 ]) cuboid([ 20, 3, 5.5 ], anchor = TOP + BACK);
    translate([ 0, 5.5, 48 ]) cuboid([ 6, 5, 10 ], anchor = TOP + BACK, rounding = 1);
    translate([ 0, 4.5, 50 ]) difference()
    {
        cuboid([ 12.5, 3, 7 ], anchor = TOP + BACK, rounding = 4, edges = [ BOTTOM + RIGHT, BOTTOM + LEFT ]);
        translate([ 0, 0.5, -3 ]) ycyl(d = 11, h = 4, anchor = BOTTOM + BACK);
    }
}

module MirrorEmptyCity()
{
    translate([ 0, 0, 50 ]) mirror([ 0, 0, 1 ]) EmptyCityModel();
}

module EmptyCityPair()
{
    translate([ 7.5, 0, 0 ]) EmptyCityModel();
    translate([ -7.5, 0, 7 ]) MirrorEmptyCity();
}

module BoxLayout()
{
    module PlayerBoxes()
    {
        translate([ 0, player_box_width, 0 ]) rotate([ 0, 0, -90 ]) PlayerBox(generate_lid = false);
        translate([ player_box_length, player_box_width, 0 ]) rotate([ 0, 0, -90 ])
            PlayerBoxTrains(generate_lid = false);
    }
    cube([ 1, box_length, box_height ]);
    cube([ box_width, box_length, total_board_thickness ]);
    translate([ 0, 0, total_board_thickness ])
    {
        CardBoxEasternUS(generate_lid = false);
        translate([ eastern_us_card_box_width, 0, 0 ]) CardBoxAustralia(generate_lid = false);
        translate([ 0, card_box_length, 0 ]) EmptyCityBox(generate_lid = false);
        translate([ 0, card_box_length + empty_city_length, 0 ]) EmptyCityBox(generate_lid = false);
        translate([ empty_city_width, card_box_length, 0 ]) PlayerBoxes();
        translate([ empty_city_width, card_box_length + player_box_width, 0 ]) PlayerBoxes();
        translate([ empty_city_width, card_box_length + player_box_width * 2, 0 ]) PlayerBoxes();
        translate([ empty_city_width, card_box_length, player_box_height ]) PlayerBoxes();
        translate([ empty_city_width, card_box_length + player_box_width, player_box_height ]) PlayerBoxes();
        translate([ empty_city_width, card_box_length + player_box_width * 2, player_box_height ]) PlayerBoxes();
        translate([ 0, card_box_length + money_section_width, player_box_height * 2 ]) rotate([ 0, 0, -90 ])
            MoneyBox(generate_lid = false);
        translate([ 0, card_box_length + money_section_width, player_box_height * 2 ]) HexBox(generate_lid = false);
        translate([ hex_box_width, card_box_length + money_section_width, player_box_height * 2 ])
            HexBox(generate_lid = false);
        translate([ money_section_length, card_box_length, player_box_height * 2 ]) NewCityBox(generate_lid = false);
    }
}

BoxLayout();

// translate([ 12, 0, 10 ]) rotate([ 0, 35, 0 ]) EmptyCityModel();

/*
translate([ 0, 0, 3 ]) EmptyCityPair();
translate([ 0, 0, 62 ]) EmptyCityPair();
translate([ 0, 0, 121 ]) EmptyCityPair();
translate([ 0, 0, 180 ]) EmptyCityPair();

translate([0,20,260])
rotate([ 0, 180, 0 ])
{
    translate([ 0, 0, 3 ]) EmptyCityPair();
    translate([ 0, 0, 62 ]) EmptyCityPair();
    translate([ 0, 0, 121 ]) EmptyCityPair();
    translate([ 0, 0, 180 ]) EmptyCityPair();
}

translate([0,40,0]) {
translate([ 0, 0, 3 ]) EmptyCityPair();
translate([ 0, 0, 62 ]) EmptyCityPair();
translate([ 0, 0, 121 ]) EmptyCityPair();
translate([ 0, 0, 180 ]) EmptyCityPair();
}
*/
// translate([ 0, 0, 239 ]) EmptyCityPair();

// translate([ 0, 0, 0 ]) cube([ empty_city_width, 3, empty_city_length * 2 ]);

// InsetLidRabbitClip(width = player_box_width, length = player_box_length, lid_thickness = lid_thickness, rabbit_depth
// = 1.5);

// MakeBoxWithInsetLidRabbitClip(width = player_box_width, length = player_box_length, lid_thickness = lid_thickness,
// height = 20, rabbit_depth = 1.5);
//  MoneyBox();

// CardBoxSweden();

// FingerHoleBase(radius = 10, height = player_box_height + 1.01, wall_thickness = wall_thickness *2);
// translate([0,50,0])
// FingerHoleWall(radius = 10, height = 20);

// PlayerBox();

// PlayerBoxTrains();
/*
MakeBoxAndLidWithInsetHinge(length = 60, hinge_diameter = 6, hinge_offset = 0.5, width = 20, height = 20)
{
    cube([ 20 - 8, 60 - 4, 20 ]);
    cube([ 20 - 8, 60 - 4, 20 ]);
};*/
//  link(20, 0.5, cone_gap = 1, cone_r1 = 5, cone_r2 = 2, side_offset = 1);