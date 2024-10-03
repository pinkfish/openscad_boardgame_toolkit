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

silo_piece_width = 22;
silo_piece_height = 40;
water_height = 27;
water_width = 21;
roundhouse_height = 40;
roundhouse_total_width = 90;

ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

money_thickness = 10;
money_length = 134;
money_width = 60;
tile_width = 29;
tile_thickness = 2;
sweden_bonus_length = 35;
sweden_bonus_width = 16;
australia_switch_track_token_radius = 5;

eastern_us_cards = 12 + 31 + 6 + 2;
mexico_cards = 12 + 38 + 4;
europe_cards = 10 + 29 + 5;
western_us_cards = 12 + 38 + 6;
great_britan_cards = 10 + 27 + 5;
north_america_cards = 24 + 50 + 12;
portugal_cards = 10 + 34 + 4;
australia_cards = 63 + 15 + 6;
sweden_cards = 12 + 43;

lid_height = 3;
wall_thickness = 2;
inner_wall = 1.5;

all_boxes_height = card_width + wall_thickness + lid_height;
card_box_width = card_length + wall_thickness * 2 + 1;
eastern_us_card_box_length =
    eastern_us_cards * single_card_thickness + bond_card_thickness + inner_wall + wall_thickness * 2;

player_box_width = (box_length - card_box_width - 2) / 3;
player_box_length = train_card_width + silo_piece_height * 2 + roundhouse_height + inner_wall * 2 + wall_thickness * 2;
player_box_height = crossing_height + inner_wall + lid_height + 4 * train_card_thickness;

top_section_height = all_boxes_height - player_box_height * 2;
top_section_width = box_length - card_box_width - 2;

western_us_expansion_box_width = 41;

hex_box_length = 207;
hex_box_width = 172;

money_section_width = money_width + wall_thickness * 2;
money_section_length = money_length + wall_thickness * 2;

new_city_box_length = hex_box_width;
new_city_box_width = box_width - money_section_width - hex_box_length;

empty_city_width = 50;
empty_city_length = (player_box_width * 3) / 2 - 0.5;
empty_city_height = player_box_height * 2;

player_box_trains_length = box_width - empty_city_width - player_box_length - 2;

expansion_area_box_width = box_width - hex_box_width;

sweden_box_width = expansion_area_box_width;
sweden_box_length = 3 * tile_width + sweden_bonus_width + wall_thickness * 2 + inner_wall;

australia_box_width = expansion_area_box_width;
australia_box_length = 3 * tile_width + australia_switch_track_token_radius * 2 + wall_thickness * 2 + inner_wall / 2;

echo(expansion_area_box_width);

module CardBoxEasternUS()
{
    difference()
    {
        union()
        {
            MakeBoxWithSlidingLid(width = card_box_width, length = eastern_us_card_box_length,
                                  height = all_boxes_height, lid_height = lid_height, wall_thickness = wall_thickness)
            {
                translate([ wall_thickness, wall_thickness, wall_thickness ]) cube([
                    card_box_width - wall_thickness * 2, eastern_us_card_box_length - wall_thickness * 2,
                    all_boxes_height -
                    lid_height
                ]);
            }
            // Bond section.
            translate([ wall_thickness, wall_thickness - inner_wall, 0 ]) difference()
            {
                cube([
                    card_box_width - wall_thickness * 2, bond_card_thickness + inner_wall * 2, all_boxes_height -
                    lid_height
                ]);
                translate(
                    [ (card_box_width - wall_thickness * 2 - bond_length) / 2, inner_wall, card_width - bond_width ])
                    cube([ bond_length, bond_card_thickness, bond_width + wall_thickness + 1 ]);
            }
        }
        translate([ card_box_width / 2, eastern_us_card_box_length / 2, all_boxes_height ])
            ycyl(h = eastern_us_card_box_length + 2, r = 25, $fn = 8);
    }
    text_str = "Eastern US";
    text_width = 80;
    text_length = 20;
    translate([ card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = card_box_width, length = eastern_us_card_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

module CardBox(num_cards, text_str)
{
    box_length = num_cards + single_card_thickness + wall_thickness * 2;
    difference()
    {
        union()
        {
            MakeBoxWithSlidingLid(width = card_box_width, length = box_length, height = all_boxes_height,
                                  lid_height = lid_height, wall_thickness = wall_thickness)
            {
                translate([ wall_thickness, wall_thickness, wall_thickness ]) cube([
                    card_box_width - wall_thickness * 2, box_length - wall_thickness * 2, all_boxes_height - lid_height
                ]);
            }
        }
        translate([ card_box_width / 2, box_length / 2, all_boxes_height ]) ycyl(h = box_length + 2, r = 25, $fn = 8);
    }
    text_width = 70;
    text_length = 20;
    translate([ card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = card_box_width, length = box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

module CardBoxAustralia()
{
    CardBox(australia_cards, "Australia");
}

module CardBoxMexico()
{
    CardBox(mexico_cards, "Mexico");
}

module CardBoxSweden()
{
    CardBox(sweden_cards, "Sweden");
}

module PlayerBox()
{
    card_height = train_card_thickness * 4.5;
    difference()
    {
        MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height,
                              lid_height = lid_height, wall_thickness = wall_thickness)
        {
            translate([ wall_thickness, wall_thickness, wall_thickness ])
                cube([ player_box_width - wall_thickness * 2, roundhouse_height, player_box_height ]);
            translate([ wall_thickness, wall_thickness + roundhouse_height + inner_wall, wall_thickness ]) cube([
                player_box_width - wall_thickness * 2 - water_width - inner_wall, silo_piece_height * 2,
                player_box_height
            ]);
            translate([
                player_box_width - wall_thickness * 2 - water_width + inner_wall,
                wall_thickness + roundhouse_height + inner_wall,
                wall_thickness
            ]) cube([ water_width, silo_piece_height * 2, player_box_height ]);
            translate([
                wall_thickness,
                wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2,
                player_box_height - lid_height - card_height,
            ]) cube([ player_box_width - wall_thickness * 2, train_card_length, player_box_height ]);
            translate([
                player_box_width * 1 / 8,
                wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + 7,
                wall_thickness,
            ]) cube([ player_box_width * 3 / 4, crossing_length * 1.25, crossing_height ]);
        };
        translate([
            0,
            wall_thickness + roundhouse_height + inner_wall * 2 + silo_piece_height * 2 + crossing_length * 1.25 / 2 +
                7,
            0
        ]) cyl(h = player_box_height * 2 + 1, r = 10);
    }
    text_str = "Player";
    text_width = 80;
    text_length = 30;
    translate([ player_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = player_box_width, length = player_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = true);
}

module PlayerBoxTrains()
{
    MakeBoxWithSlidingLid(width = player_box_width, length = player_box_trains_length, height = empty_city_height,
                          lid_height = lid_height, wall_thickness = wall_thickness)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ]) cube([
            player_box_width - wall_thickness * 2, player_box_trains_length - 2 * wall_thickness,
            empty_city_height
        ]);
    }
    text_str = "Trains";
    text_width = 60;
    text_length = 20;
    translate([ player_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = player_box_width, length = player_box_trains_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

module EmptyCityBox()
{
    MakeBoxWithSlidingLid(width = empty_city_width, length = empty_city_length, height = empty_city_height,
                          lid_height = lid_height, wall_thickness = wall_thickness)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            cube([ empty_city_width - wall_thickness * 2, empty_city_length - 2 * wall_thickness, empty_city_height ]);
    }
    text_str = "Empty City";
    text_width = 80;
    text_length = 20;
    translate([ empty_city_width + 10, 0, 0 ]) SlidingLid(empty_city_width, empty_city_length, lid_height = lid_height)
    {
        translate([ 10, 10, 0 ]) LidMeshHex(width = empty_city_width, length = empty_city_length,
                                            lid_height = lid_height, boundary = 10, radius = 12);
        translate([ (empty_city_width + text_length) / 2, (empty_city_length - text_width) / 2, 0 ])
            rotate([ 0, 0, 90 ]) MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height,
                                                     label = text_str, border = wall_thickness, offset = 4);
    }
}

module MoneyBox()
{
    difference()
    {
        MakeBoxWithSlidingLid(width = money_section_width, length = money_section_length, height = top_section_height,
                              lid_height = lid_height, wall_thickness = wall_thickness)
        {
            translate([ wall_thickness, wall_thickness, wall_thickness ])
                cube([ money_width, money_length, empty_city_height ]);
        }
        translate([ money_section_width / 2, 1, -1 ]) cyl(h = top_section_height * 3, r = 15);
    }
    text_str = "Money";
    text_width = 80;
    text_length = 20;
    translate([ money_section_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = money_section_width, length = money_section_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = true);
}

module HexBox()
{
    MakeHexBoxWithSlidingLid(rows = 5, cols = 7, height = top_section_height, push_block_height = 0.75,
                             tile_width = tile_width);
}

module NewCityBox()
{
    difference()
    {
        MakeBoxWithSlidingLid(width = new_city_box_width, length = new_city_box_length, height = top_section_height,
                              lid_height = lid_height, wall_thickness = wall_thickness)
        {
            translate([ wall_thickness + 0.5, wall_thickness, top_section_height - lid_height - tile_thickness * 4 ])
                RegularPolygonGrid(width = tile_width, rows = 1, cols = 4, spacing = 0)
            {
                RegularPolygon(width = tile_width, height = tile_thickness * 4.25, shape_edges = 6);
                cyl(r = 10, h = 20);
            }
            translate([
                wall_thickness + 3 + tile_width / 2, wall_thickness * 2 + (tile_width + 1) * 4 + tile_width / 2 + 16,
                top_section_height - lid_height - tile_thickness * 2.5
            ])
            {
                RegularPolygon(width = tile_width, height = top_section_height, shape_edges = 6);
                translate([ 0, -tile_width / 2, 7 ]) ycyl(h = 12, r = 7);
            }
            translate(
                [ wall_thickness + 1, wall_thickness + (tile_width + 1) * 4 - 8, top_section_height - lid_height - 10 ])
                rotate([ 0, 0, 22 ]) cube([ 40, 15.5, 11 ]);
        }
        translate([ new_city_box_width / 2, wall_thickness, top_section_height - 1 ])
            ycyl(h = (tile_width + 2) * 8.2, r = 10);
    }
    text_str = "New Cities";
    text_width = 80;
    text_length = 20;
    translate([ new_city_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = new_city_box_width, length = new_city_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = true);
}

module SwedenBox()
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(width = sweden_box_width, length = sweden_box_length, height = top_section_height,
                          lid_height = lid_height, wall_thickness = wall_thickness)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ]) intersection()
        {
            translate([ 0, 0, -3 ]) cube([ radius * 4 * 2, tile_width * 3, top_section_height + 1 ]);
            HexGridWithCutouts(rows = 4, cols = 3, tile_width = tile_width, spacing = 0,
                               wall_thickness = wall_thickness, push_block_height = 0.75, height = top_section_height);
        }
        // bonus bit (top)
        translate([
            wall_thickness * 2, sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            wall_thickness * 2 + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (middle)
        translate([
            sweden_box_width - wall_thickness * 2 - sweden_bonus_length,
            sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            sweden_box_width - wall_thickness * 2 - sweden_bonus_length + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);

        // bonus bit (bottom)
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ sweden_bonus_length, sweden_bonus_width, tile_thickness * 2.5 ]);
        translate([
            (sweden_box_width - wall_thickness * 2 - sweden_bonus_length) / 2 + (sweden_bonus_length - 10) / 2,
            sweden_box_length - wall_thickness - sweden_bonus_width - 5,
            top_section_height - lid_height - tile_thickness * 2.4
        ]) cube([ 10, 10, 10 ]);
    }
    text_str = "Sweden";
    text_width = 80;
    text_length = 20;
    translate([ sweden_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = sweden_box_width, length = sweden_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

module AustraliaBox()
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(width = australia_box_width, length = australia_box_length, height = top_section_height,
                          lid_height = lid_height, wall_thickness = wall_thickness)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ]) intersection()
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
            (australia_box_width - wall_thickness * 2 - sweden_bonus_width),
            wall_thickness + tile_width * 2 + wall_thickness, top_section_height - lid_height - tile_thickness * 6.4
        ]) cube([ sweden_bonus_width, sweden_bonus_length, tile_thickness * 6.5 ]);
        // Fingercut for the bonus cards.
        translate([
            (australia_box_width - wall_thickness * 2 - sweden_bonus_width) + 8,
            wall_thickness + tile_width * 2 + wall_thickness, top_section_height / 2 + 4.3
        ]) cyl(h = top_section_height, r = 5);

        // For the switch track tokens.
        for (i = [0:1:8])
            translate([
                wall_thickness + australia_switch_track_token_radius +
                    (australia_switch_track_token_radius * 2 + inner_wall) * i,
                australia_box_length - wall_thickness - australia_switch_track_token_radius,
                top_section_height - lid_height - tile_thickness * 2.4 / 2
            ])
            {
                cyl(r = australia_switch_track_token_radius, h = tile_thickness * 2.5);
                translate([
                    -australia_switch_track_token_radius / 2, -australia_switch_track_token_radius - 1,
                    -(tile_thickness * 2.5) / 2
                ])
                    cube([
                        australia_switch_track_token_radius, australia_switch_track_token_radius, tile_thickness * 2.5
                    ]);
            }
        // Extra switch track tokens
        translate([
            3 * radius * 2 + australia_switch_track_token_radius + wall_thickness,
            2 * apothem * 2 + australia_switch_track_token_radius + wall_thickness + 15,
            top_section_height - lid_height - tile_thickness * 2.4 / 2
        ])
        {
            cyl(r = australia_switch_track_token_radius, h = tile_thickness * 2.5);
            translate([
                -australia_switch_track_token_radius - 1, -australia_switch_track_token_radius / 2,
                -(tile_thickness * 2.5) / 2
            ]) cube([ australia_switch_track_token_radius, australia_switch_track_token_radius, tile_thickness * 2.5 ]);
        }
    }
    text_str = "Australia";
    text_width = 80;
    text_length = 20;
    translate([ australia_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
        width = australia_box_width, length = australia_box_length, lid_height = lid_height, text_width = text_width,
        text_length = text_length, text_str = text_str, label_rotated = false);
}

AustraliaBox();
