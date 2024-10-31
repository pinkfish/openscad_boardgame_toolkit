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

box_height = 67;
box_width = 285;
box_length = 285;
wall_thickness = 3;
inner_wall = 1;
lid_thickness = 2;
board_thickness = 27;

eggs_box_width = 75;
eggs_box_length = 112;
eggs_box_height = 27;

side_width = 47.5;

dragon_card_length = 90;
dragon_card_width = 58;

cave_card_size = 58;

money_width = 70;

bonus_card_width = 46;
bonus_card_length = 52.5;

start_token_diameter = 67;
start_token_thickness = 2;

guild_card_width = 95;
guild_card_length = 118;
guild_card_thickness = 8;

score_pad_thickness = 5;
score_pad_width = 91;
score_pad_length = 121;

round_token_diameter = 18;
round_token_thickness = 10;

// This leaves space for the boards.
side_section = 47.5;

player_box_height = (box_height - 2) / 5;
player_box_width = 36 + 15 + 2 * wall_thickness;
player_box_length = side_section;

food_box_height = (box_height - 2) / 2;
food_box_width = box_width - player_box_width - 1;
food_box_length = side_section;

dragon_card_box_width = dragon_card_length + wall_thickness * 2 + 1;
dragon_card_box_length = (dragon_card_width + 0.5) * 3 + inner_wall * 2 + wall_thickness * 2 + 1;
dragon_card_box_height = box_height - board_thickness;

cave_card_box_length = box_length - player_box_length - 1;
cave_card_box_width = box_width - 1 - dragon_card_box_width - eggs_box_width;
cave_card_box_height = box_height - board_thickness;

coin_box_length = box_width - dragon_card_box_length - player_box_length;
coin_box_width = dragon_card_box_width;
coin_box_height = dragon_card_box_height / 2;

module PlayerBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = player_box_width, length = player_box_length, height = player_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        cube([ player_box_width - 2 * wall_thickness, player_box_length - 2 * wall_thickness, player_box_height ]);
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = player_box_width, length = player_box_length, height = player_box_height,
                           text_width = 50, text_height = 15, text_str = "Player", wall_thickness = wall_thickness,
                           lid_thickness = lid_thickness);
    }
}

module FoodBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = food_box_width, length = food_box_length, height = food_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        translate([ 0, 0, 10 ])
            RoundedBoxGrid(width = food_box_width - 2 * wall_thickness, length = food_box_length - 2 * wall_thickness,
                           height = food_box_height - lid_thickness * 2, radius = 10, rows = 2, cols = 1);
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = food_box_width, length = food_box_length, height = food_box_height, text_width = 70,
                           text_height = 15, text_str = "Edibles", wall_thickness = wall_thicknes,
                           lid_thickness = lid_thickness);
    }
}

module DragonCardBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = dragon_card_box_width, length = dragon_card_box_length, height = dragon_card_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        for (i = [0:1:2])
        {
            translate([ 0, (dragon_card_width + inner_wall + 0.5) * i, 0 ])
                cube([ dragon_card_length + 0.5, dragon_card_width + 0.5, dragon_card_box_height ]);
        }
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = dragon_card_box_width, length = dragon_card_box_length,
                           height = dragon_card_box_height, text_width = 70, text_height = 15, text_str = "Dragons",
                           wall_thickness = wall_thicknes, lid_thickness = lid_thickness);
    }
}

module ProvidedEggBox()
{
    cube([ eggs_box_width, eggs_box_length, eggs_box_height ]);
}

module CaveCardBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = cave_card_box_width, length = cave_card_box_length, height = cave_card_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        // Cave cards.
        for (i = [0:1:2])
        {
            translate([ 0, (cave_card_size + inner_wall + 0.5) * i, 0 ])
                cube([ cave_card_size + 0.5, cave_card_size + 0.5, cave_card_box_height ]);
        }
        // bonus cards.
        for (i = [0:1:0])
        {
            translate([ cave_card_size + 0.5 + inner_wall, (bonus_card_length + inner_wall + 0.5) * i, 0 ])
                cube([ bonus_card_width + 0.5, bonus_card_length + 0.5, cave_card_box_height ]);
        }
        // guild cards.
        translate([
            cave_card_box_width - guild_card_width - 0.5,
            cave_card_box_length - guild_card_length - wall_thickness * 2 - 0.5,
            cave_card_box_height - lid_thickness * 2 - guild_card_thickness - 0.5
        ]) cube([ guild_card_width + 0.5, guild_card_length + 0.5, guild_card_thickness + 2 ]);
        // first player marker
        translate([
            cave_card_box_width - start_token_diameter / 2 - 0.5 - wall_thickness * 2,
            cave_card_box_length - start_token_diameter / 2 - wall_thickness * 2 - 0.5,
            cave_card_box_height - lid_thickness * 2 - guild_card_thickness - start_token_thickness - 1
        ]) cyl(d = start_token_diameter + 1, h = start_token_thickness + 1, anchor = BOTTOM);
        // round token
        translate([
            cave_card_size + 0.5 + inner_wall + bonus_card_width / 2,
            (bonus_card_length + inner_wall + 0.5) * 1 + bonus_card_length / 2,
            cave_card_box_height - lid_thickness * 2 - round_token_thickness - 0.5
        ])
        {
            cyl(d = round_token_diameter + 0.5, round_token_thickness + 0.6, anchor = BOTTOM);
            translate([ 0, round_token_diameter / 2, 13 ]) sphere(r = 10);
        }
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = cave_card_box_width, length = cave_card_box_length, height = cave_card_box_height,
                           text_width = 70, text_height = 15, text_str = "Caves + stuff",
                           wall_thickness = wall_thicknes, lid_thickness = lid_thickness);
    }
}

module CoinBox()
{
    MakeBoxWithCapLid(width = coin_box_width, length = coin_box_length, height = coin_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        RoundedBoxAllSides(width = coin_box_width - wall_thickness * 2, length = coin_box_length - wall_thickness * 2,
                           height = coin_box_height, radius = 7);
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = coin_box_width, length = coin_box_length, height = coin_box_height, text_width = 70,
                           text_height = 15, text_str = "Coins", wall_thickness = wall_thicknes,
                           lid_thickness = lid_thickness);
    }
}

module BonusBox()
{
    MakeBoxWithCapLid(width = coin_box_width, length = coin_box_length, height = coin_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        RoundedBoxAllSides(width = coin_box_width - wall_thickness * 2, length = coin_box_length - wall_thickness * 2,
                           height = coin_box_height, radius = 7);
    }
    if (generate_lid)
    {
        CapBoxLidWithLabel(width = coin_box_width, length = coin_box_length, height = coin_box_height, text_width = 70,
                           text_height = 15, text_str = "Bonus", wall_thickness = wall_thicknes,
                           lid_thickness = lid_thickness);
    }
}

module BoxLayout()
{
    cube([ box_length, box_width, 1 ]);
    cube([ box_length, 1, box_height ]);
    for (i = [0:1:4])
    {
        translate([ 0, 0, player_box_height * i ]) PlayerBox(generate_lid = false);
    }
    for (i = [0:1:1])
    {
        translate([ player_box_width, 0, food_box_height * i ]) FoodBox(generate_lid = false);
    }
    translate([ 0, player_box_length, 0 ]) DragonCardBox();
    translate([ 0, player_box_length + dragon_card_box_length, 0 ]) CoinBox();
    translate([ 0, player_box_length + dragon_card_box_length, coin_box_height ]) BonusBox();
    translate([ dragon_card_box_width, player_box_length, 0 ]) CaveCardBox(generate_lid = false);
    translate([ dragon_card_box_width + cave_card_box_width, player_box_length, 0 ]) ProvidedEggBox();
    translate([ dragon_card_box_width + cave_card_box_width, player_box_length + eggs_box_length, 0 ]) ProvidedEggBox();
}

BoxLayout();