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

default_lid_shape_type = SHAPE_TYPE_CLOUD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 12;
default_lid_aspect_ratio = 1.5;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;

box_length = 266;
box_width = 182;
box_height = 65;

board_thickness = 10;
card_width = 44;
card_length = 68;
money_width = 43;
money_length = 82;
num_green_cards = 31;
num_blue_cards = 28;
num_orange_cards = 27;
num_multi_color_cards = 30;
num_start_cards = 4;

wood_token_thickness = 10;

square_size = 23;
h_length = 25;
h_width = 18.5;
h_elbow_length = 13;
h_leg_width = 7;
club_width = 25;
club_length = 25;
club_base_length = 5;
club_base_width = 12.5;
club_round_diameter = 13;
club_top_diameter = 3;
head_length = 21;
head_width = 25;
head_edge_length = 4.5;
head_edge_width = 5;
head_nose_length = 7;
head_nose_width = 4;
head_nose_diameter = 4;
head_top_nose = 14;
head_round_diameter = 19;
head_back_offset = 2;

meeple_length = 15;
meeple_width = 20;
meeple_angle_length = 8;
meeple_angle_width = 15.5;
meeple_head_width = 11.5;
meeple_bottom_head_width = 9;
meeple_head_diameter = 4;
meeple_head_round_middle = 11;
meeple_top_radius = 2;

money_box_width = money_length + default_wall_thickness * 2;
money_box_length = box_length - 2;
money_box_height = 15;

card_box_length = box_length - 2;
card_box_width = box_width - money_box_width - 2;
card_box_height = box_height - board_thickness - 0.5;

tokens_box_length = box_length - 2;
tokens_box_width = money_box_width;
tokens_box_height = wood_token_thickness + default_lid_thickness + default_floor_thickness;

spacer_box_length = tokens_box_length;
spacer_box_width = tokens_box_width;
spacer_box_height = box_height - board_thickness - money_box_height - tokens_box_height - 0.5;

module HToken(height)
{
    translate([ 0, 0, height / 2 ]) union()
    {
        translate([ h_width / 2 - h_leg_width / 2, 0, 0 ])
            cuboid([ h_leg_width, h_length, height ], rounding = 0.5,
                   edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
        translate([ 0, -h_length / 2 + h_leg_width / 2 + h_elbow_length - h_leg_width, 0 ])
            cuboid([ h_width, h_leg_width, height ], rounding = 0.5,
                   edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
        translate([ -h_width / 2 + h_leg_width / 2, -h_length / 2 + h_elbow_length / 2, 0 ])
            cuboid([ h_leg_width, h_elbow_length, height ], rounding = 0.5,
                   edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
    }
}

module ClubToken(height)
{
    translate([ 0, 0, height / 2 ]) union()
    {
        cut_out_round = club_round_diameter - club_top_diameter;
        translate([ cut_out_round / 2 + club_top_diameter / 2, club_length / 2 - club_top_diameter / 2, 0 ])
            difference()
        {
            translate([ -cut_out_round / 4, -cut_out_round / 4, 0 ])
                cuboid([ cut_out_round / 2, cut_out_round / 2, height ]);
            cyl(d = cut_out_round, h = height + 1);
        }
        mirror([ 1, 0, 0 ])
            translate([ cut_out_round / 2 + club_top_diameter / 2, club_length / 2 - club_top_diameter / 2, 0 ])
                difference()
        {
            translate([ -cut_out_round / 4, -cut_out_round / 4, 0 ])
                cuboid([ cut_out_round / 2, cut_out_round / 2, height ]);
            cyl(d = cut_out_round, h = height + 1);
        }
        hull()
        {
            translate([ 0, club_length / 2 - club_top_diameter / 2, 0 ])
                cyl(d = club_top_diameter, h = height, $fn = 32);
            translate([ 0, 0, 0 ]) cyl(d = club_top_diameter, h = height, $fn = 32);
        }
        // Middle bit.
        hull()
        {
            translate(
                [ cut_out_round / 2 + 1.25, club_length / 2 - club_top_diameter / 2 - cut_out_round / 2 - 0.4, 0 ])
                cyl(r = 0.5, h = height);
            translate(
                [ -cut_out_round / 2 - 1.75, club_length / 2 - club_top_diameter / 2 - cut_out_round / 2 - 0.4, 0 ])
                cyl(r = 0.5, h = height);
            translate([
                club_width / 2 - club_round_diameter / 2, -club_length / 2 + club_round_diameter / 2 + club_base_length,
                0
            ]) cyl(d = club_round_diameter, h = height);
            translate([
                -club_width / 2 + club_round_diameter / 2,
                -club_length / 2 + club_round_diameter / 2 + club_base_length, 0
            ]) cyl(d = club_round_diameter, h = height);
        }
        // Foot.
        translate([ 0, -club_length / 2 + (club_base_length + 1) / 2, 0 ])
            cuboid([ club_base_width, club_base_length + 1, height ], rounding = 0.5,
                   edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
    }
}

module PersonHeadToken(height)
{
    translate([ 0, 0, height / 2 ]) union()
    {
        // Round bit of head.
        translate([
            head_width / 2 - head_round_diameter / 2 - head_back_offset, head_length / 2 - head_round_diameter / 2, 0
        ]) cyl(d = head_round_diameter, h = height);
        // Pedastle.
        hull()
        {
            translate([ head_width / 2 - 1.5, -head_length / 2 + 1.5, 0 ]) cyl(r = 1.5, h = height);
            translate([ head_width / 2 - 0.5 - head_edge_width, -head_length / 2 + 1 + head_edge_length, 0 ])
                cyl(r = 0.5, h = height);
            translate([ -head_width / 2 + 1.5, -head_length / 2 + 1.5, 0 ]) cyl(r = 1.5, h = height);
            translate([ -head_width / 2 + 0.5 + head_edge_width, -head_length / 2 + 1 + head_edge_length, 0 ])
                cyl(r = 0.5, h = height);
        }
        // Nose.
        hull()
        {
            translate([ -head_width / 2 + 0.5 + head_edge_width, -head_length / 2 + 1.5 + head_edge_length, 0 ])
                cyl(r = 0.5, h = height);
            translate([
                -head_width / 2 + head_nose_diameter / 2, -head_length / 2 + head_nose_length + head_nose_diameter / 2,
                0
            ]) cyl(d = head_nose_diameter, h = height);
            translate([ -head_width / 2 + 0.5 + head_edge_width, -head_length / 2 + head_top_nose + 0.5, 0 ])
                cyl(r = 0.5, h = height);
        }
    }
}

module MeepleToken(height)
{
    translate([ 0, 0, height / 2 ]) union()
    {
        // Base section.
        hull()
        {
            translate([ meeple_width / 2 - 1, meeple_length / 2 - 1, 0 ]) cyl(r = 1, h = height);
            translate([ -meeple_width / 2 + 1, meeple_length / 2 - 1, 0 ]) cyl(r = 1, h = height);
            translate([ meeple_bottom_head_width / 2 - 1, meeple_length / 2 - meeple_angle_length, 0 ])
                cyl(r = 1, h = height);
            translate([ -meeple_bottom_head_width / 2 + 1, meeple_length / 2 - meeple_angle_length, 0 ])
                cyl(r = 1, h = height);
        }
        // Top Round bit.
        hull()
        {
            translate(
                [ -meeple_head_width / 2 + meeple_head_diameter / 2, meeple_length / 2 - meeple_head_round_middle, 0 ])
                cyl(d = meeple_head_diameter, h = height);
            translate(
                [ meeple_head_width / 2 - meeple_head_diameter / 2, meeple_length / 2 - meeple_head_round_middle, 0 ])
                cyl(d = meeple_head_diameter, h = height);
            translate([ meeple_bottom_head_width / 2 - 1, meeple_length / 2 - meeple_angle_length, 0 ])
                cyl(r = 1, h = height);
            translate([ -meeple_bottom_head_width / 2 + 1, meeple_length / 2 - meeple_angle_length, 0 ])
                cyl(r = 1, h = height);
            translate([ 0, -meeple_length / 2 + meeple_top_radius, 0 ]) cyl(r = meeple_top_radius, h = height);
        }
    }
}

module MoneyBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = money_box_width, length = money_box_length, height = money_box_height)
    {
        for (i = [0:1:4])
        {
            translate([ 0, (money_width + 4) * i, 0 ]) cube([ money_length, money_width, money_box_height ]);
            translate([ -1, (money_width + 4) * i + money_width / 2, -default_floor_thickness - 0.01 ])
                FingerHoleBase(radius = 12, height = money_box_height, spin = 270);
        }
    }
    if (generate_lid)
    {
        translate([ money_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = money_box_width, length = money_box_length, height = money_box_height,
                               text_width = 70, text_height = 20, text_str = "Money", label_rotated = true);
    }
}
module CardBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = card_box_width, length = card_box_length, height = card_box_height)
    {
        for (i = [0:1:3])
        {
            translate([ 0, (card_width + 4) * i, 0 ]) cube([ card_length, card_width, card_box_height ]);
            translate([ -1, (card_width + 4) * i + card_width / 2, -default_floor_thickness - 0.01 ])
                FingerHoleBase(radius = 12, height = card_box_height, spin = 270);
        }
        translate([ 0, $inner_length - card_width, $inner_height - 5 ])
        {
            cube([ card_length, card_width, card_box_height ]);
            translate([ 0, card_width / 2, 0 ]) xcyl(r = 14, h = 50, anchor = BOTTOM);
        }
    }
    if (generate_lid)
    {
        translate([ card_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = card_box_width, length = card_box_length, height = card_box_height,
                               text_width = 70, text_height = 20, text_str = "Cards", label_rotated = true);
    }
}

module TokensBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = tokens_box_width, length = tokens_box_length, height = tokens_box_height)
    {
        translate([ 15, 8, 0 ])
        {
            translate([ square_size / 2, square_size / 2, $inner_height - wood_token_thickness - 0.5 ])
            {
                cuboid([ square_size, square_size, wood_token_thickness + 1 ], anchor = BOTTOM);
                translate([ 0, square_size / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -square_size / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
            translate([ head_width * 3 / 2 + 4, h_length / 2, $inner_height - wood_token_thickness - 0.5 ])
            {
                HToken(wood_token_thickness + 1);
                translate([ 5, h_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -h_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
            translate(
                [ head_width * 3 / 2 + 4, h_length + club_length / 2 + 15, $inner_height - wood_token_thickness - 0.5 ])
            {
                ClubToken(wood_token_thickness + 1);
                translate([ 5, club_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -club_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
            translate([ head_width / 2, h_length + head_length / 2 + 15, $inner_height - wood_token_thickness - 0.5 ])
            {
                PersonHeadToken(wood_token_thickness + 1);
                translate([ 5, head_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -head_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
        }

        translate([ 0, -10, 0 ]) for (i = [0:1:3])
        {
            translate([
                $inner_width / 2 - meeple_width / 2 - 2, $inner_length - meeple_length / 2 - (meeple_length + 15) * i,
                $inner_height - wood_token_thickness - 0.5
            ])
            {
                MeepleToken(height = wood_token_thickness + 1);
                translate([ 0, meeple_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -meeple_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
            translate([
                $inner_width / 2 + meeple_width / 2 + 2, $inner_length - meeple_length / 2 - (meeple_length + 15) * i,
                $inner_height - wood_token_thickness - 0.5
            ])
            {
                MeepleToken(height = wood_token_thickness + 1);
                translate([ 0, meeple_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
                translate([ 0, -meeple_length / 2, wood_token_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
            }
        }
    }
    if (generate_lid)
    {
        translate([ tokens_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = tokens_box_width, length = tokens_box_length, height = tokens_box_height,
                               text_width = 70, text_height = 20, text_str = "Tokens", label_rotated = true);
    }
}

module Spacer() // `make` me
{
    difference()
    {
        cuboid([ spacer_box_width, spacer_box_length, spacer_box_height ], rounding = 2,
               anchor = BOTTOM + LEFT + FRONT);
        translate([ default_wall_thickness, default_wall_thickness, default_floor_thickness ]) cuboid(
            [
                spacer_box_width - default_wall_thickness * 2, spacer_box_length - default_wall_thickness * 2,
                spacer_box_height
            ],
            rounding = 2, anchor = BOTTOM + LEFT + FRONT);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        MoneyBox(generate_lid = false);
        translate([ 0, 0, money_box_height ]) TokensBox(generate_lid = false);
        translate([ 0, 0, money_box_height + tokens_box_height ]) Spacer();
        translate([ money_box_width, 0, 0 ]) CardBox(generate_lid = false);
    }
}

if (FROM_MAKE != 1)
{
    TokensBox();
}