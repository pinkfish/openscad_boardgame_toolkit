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

box_length = 314;
box_width = 225;
box_height = 68;
box_hexes = 20;

money_biggest_thickness = 8.5;
money_types = [ "1", "2", "5", "10", "20", "50", "100", "500" ];
company_names = [
    "Oeste", "Matanzas", "Cienfuegos", "Nuevitas-Puerto", "Sanago de Cuba", "Las Tunas", "Sanc Spiritus",
    "Florida East Coast", "Ferrocarril Central", "?"
];

minor_companies = [ "HG", "JU", "HY", "DQ", "CO", "CS" ];
major_companies = [ "Oe", "MS", "CVC", "NPP", "SdC", "TSS", "StSp", "FEC" ];

// large cards
num_train_cards = 36;
num_wagon_cards = 18;
num_ferrocari_central = 10;
num_stocks_per_company = 9;
num_major_companies = 8;
num_help_cards = 6;
num_comminishiner_cards = 6;

// small cards
num_minor_company_shares = 4;
num_minor_companies = 6;
num_narrow_guage_trains = 31;
num_playing_order_cards = 6;
num_concession_cards = 6;

train_card_width = 40;
train_card_length = 60;
share_card_length = 65;
card_thickness_twenty = 8;
token_diameter = 15;
token_thin_thickness = 5;
token_big_thickness = 10;
rail_thickness = 5;
rail_length = 25;
minor_company_width = 90;
major_company_width = 111;
total_board_thickness = 26;
money_width = 46;
money_length = 90;

rest_height = 68 - box_hexes - total_board_thickness;
inner_wall = 2;
wall_thickness = 1.5;
lid_thickness = 2;
floor_thickness = 2;

echo(rest_height);

money_box_length = box_width - 1; //(money_width + inner_wall) * len(money_types) / 2 + 1.5 * 4;
money_box_width = money_length + wall_thickness * 4;
money_box_height = rest_height / 2;

train_box_length = box_width - 1;
train_box_width = train_card_length + wall_thickness * 4;
train_box_height = rest_height / 2;

rest_section_width = box_length - train_box_width * 2 - money_box_width - 1;
echo(rest_section_width);
echo(money_box_height);

train_svg_width = 200;
train_svg_length = 200;
wagon_svg_length = 1308.800;
wagon_svg_width = 909.375;
max_size = max(wagon_svg_length, wagon_svg_width);
wagon_ratio_len = wagon_svg_length / max_size;
wagon_ratio_wid = wagon_svg_width / max_size;

module TrainOutline()
{
    resize([ train_svg_width, train_svg_length ]) import("svg/train_engine.svg");
}

module WagonOutline()
{
    resize([ wagon_svg_length, wagon_svg_width ]) import("svg/railway_wagon.svg");
}

module Outline(height = 5, outline = 1.5, offset = 0.5)
{

    difference()
    {
        linear_extrude(height = 5) offset(1.5) children();
        translate([ 0, 0, -1 ]) linear_extrude(height = 10) offset(0.5) children();
    }
}

module MoneyBox(offset = 0)
{
    MakeBoxWithSlipoverLid(length = money_box_length, width = money_box_width, height = money_box_height,
                           lid_thickness = 0.75, floor_thickness = 0.75, foot = 2, wall_thickness = wall_thickness)
    {
        for (i = [0:1:3])
        {
            translate([ 0, i * (money_width + inner_wall) + 12, 0 ])
                cube([ money_length, money_width, money_box_height ]);
            translate([ money_length / 2, i * (money_width + inner_wall) + money_width / 2 + 12, -0.3 ])
                linear_extrude(height = 2) text(money_types[i + offset], size = 10, anchor = CENTER);
        }
    }
    translate([ money_box_width + 10, 0, 0 ])
        SlipoverLidWithLabel(width = money_box_width, length = money_box_length, height = money_box_height,
                             text_width = 70, text_height = 20, text_str = "18Cuba", label_rotated = true);
}

module TrainBox()
{
    MakeBoxWithSlipoverLid(length = train_box_length, width = train_box_width, height = train_box_height,
                           lid_thickness = 1, floor_thickness = 1, foot = 2, wall_thickness = wall_thickness)
    {
        for (i = [0:1:4])
        {
            translate([ 0, i * (train_card_width + inner_wall + 2), 0 ])
                cube([ train_card_length, train_card_width, train_box_height ]);
            if (i < 3)
            {
                translate([
                    (train_card_length - train_card_width) / 2 + 5, -5 + i * (train_card_width + inner_wall + 2), -0.3
                ]) Outline(offset = 0.25) resize([ train_card_width / 2, train_card_width / 2 ]) TrainOutline();
            }
            else
            {
                translate([
                    (train_card_length - train_card_width) / 2 + 7, i * (train_card_width + inner_wall + 2) + 12, -0.3
                ]) Outline(offset = 0.1)
                    resize([ train_card_width / 2 * wagon_ratio_len, train_card_width / 2 * wagon_ratio_wid ])
                        WagonOutline();
            }
        }
    }
    translate([ train_box_width + 10, 0, 0 ])
        SlipoverLidWithLabel(width = train_box_width, length = train_box_length, height = train_box_height,
                             lid_thickness = 1, text_width = 70, text_height = 20, text_str = "Trains",
                             label_rotated = true, wall_thickness = wall_thickness, foot = 2);
}

module SharesBox(offset = 0)
{
    MakeBoxWithSlipoverLid(length = train_box_length, width = train_box_width, height = train_box_height,
                           lid_thickness = 1, floor_thickness = 1, foot = 2, wall_thickness = wall_thickness)
    {
        for (i = [0:1:4])
        {
            translate([ 0, i * (train_card_width + inner_wall + 2), 0 ])
                cube([ train_card_length, train_card_width, train_box_height ]);
            translate(
                [ train_card_length / 2 - 2, i * (train_card_width + inner_wall + 2) + train_card_width / 2, -0.3 ])
                linear_extrude(height = 2) text(company_names[i + offset], size = 4.7, anchor = CENTER);
        }
    }
    translate([ train_box_width + 10, 0, 0 ])
        SlipoverLidWithLabel(width = train_box_width, length = train_box_length, height = train_box_height,
                             lid_thickness = 1, text_width = 70, text_height = 20, text_str = "Shares",
                             label_rotated = true, wall_thickness = wall_thickness, foot = 2);
}

module LastBox()
{
    MakeBoxWithSlipoverLid(length = train_box_length, width = train_box_width, height = train_box_height,
                           lid_thickness = 1, floor_thickness = 1, foot = 2, wall_thickness = wall_thickness)
    {
        cube([ train_card_length, train_card_width, train_box_height ]);
        translate([ train_card_length / 2 - 2, train_card_width / 2, -0.3 ]) linear_extrude(height = 2)
            text("Concession", size = 4.7, anchor = CENTER);
        for (i = [0:1:9])
        {
            // Cylinder for tokens.
            translate([
                2.3, train_card_width + 4 + (token_diameter + 1) * i, train_box_height - 1 - token_thin_thickness - 0.5
            ]) cyl(d = token_diameter, h = token_thin_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            translate([
                24.2, train_card_width + 4 + (token_diameter + 1) * i, train_box_height - 1 - token_thin_thickness - 0.5
            ]) cyl(d = token_diameter, h = token_thin_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            last_i = i > 7 ? i + 1 : i;
            translate([
                46.2, train_card_width + 4 + (token_diameter + 1) * last_i,
                train_box_height - 1 - token_thin_thickness - 0.5
            ]) cyl(d = token_diameter, h = token_thin_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            // finger holes for tokens.
            translate([ 0, train_card_width + 9.4 + (token_diameter + 1) * i, 10.5 ]) xcyl(r = 6, h = 10, $fn = 32);
            translate([ 0, train_card_width + 9.4 + (token_diameter + 1) * i, 15.2 ]) cuboid([ 12, 12, 12 ]);
            translate([ 57, train_card_width + 9.4 + (token_diameter + 1) * last_i, 10.5 ])
                xcyl(r = 6, h = 10, $fn = 32);
            translate([ 57, train_card_width + 9.4 + (token_diameter + 1) * last_i, 15.2 ]) cuboid([ 12, 12, 12 ]);
            // finger indent for the middle secxtion
            translate([ 37, train_card_width + 9.4 + (token_diameter + 1) * i, 10.5 ]) sphere(r = 6, $fn = 32);
            // Text associated with the tokens.
            translate(
                [ 18.5, train_card_width + 9.4 + (token_diameter + 1) * i, train_box_height - lid_thickness - 0.4 ])
                linear_extrude(height = 2) text(minor_companies[i], size = 3.2, anchor = CENTER);
        }
        // names for the tokens.
        translate([ 18.5, train_card_width + 9.5 + (token_diameter + 1) * 7, train_box_height - lid_thickness - 0.4 ])
            linear_extrude(height = 2) rotate([ 0, 0, 90 ]) text("Green", size = 3.2, anchor = CENTER);
        translate([ 18.5, train_card_width + 9.5 + (token_diameter + 1) * 9, train_box_height - lid_thickness - 0.4 ])
            linear_extrude(height = 2) rotate([ 0, 0, 90 ]) text("Brown", size = 3.2, anchor = CENTER);
        // Rail locations.
        translate([
            10, train_card_width + 3 + (token_diameter + 1) * 10,
            train_box_height - lid_thickness - rail_thickness - 0.4
        ]) cube([ rail_length, rail_thickness * 3, rail_thickness + 1 ]);
        // finger cutout for the rails.
        translate([
            22, train_card_width + 3 + (token_diameter + 1) * 10 + 15,
            train_box_height - lid_thickness - rail_thickness - 0.4 + 5
        ]) ycyl(d = 10, h = 10, $fn = 32);
    }

    translate([ train_box_width + 10, 0, 0 ])
        SlipoverLidWithLabel(width = train_box_width, length = train_box_length, height = train_box_height,
                             lid_thickness = 1, text_width = 130, text_height = 20, text_str = "Machine/Minor",
                             label_rotated = true, wall_thickness = wall_thickness, foot = 2);
}

module LargeTokens()
{
    wall_height = 0.75 + token_big_thickness;
    MakeBoxWithSlipoverLid(length = train_box_length, width = rest_section_width, height = rest_height,
                           lid_thickness = 0.75, floor_thickness = 0.75, foot = 2, wall_thickness = wall_thickness,
                           wall_height = wall_height)
    {
        for (i = [0:1:11])
        {
            // Cylinder for tokens.
            translate([ 2.3, 4 + (token_diameter + 3) * i, wall_height - token_big_thickness - 0.2 ])
                cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            translate([ 24.2, 4 + (token_diameter + 3) * i, wall_height - token_big_thickness - 0.2 ])
                cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            last_i = i > 7 ? i : i;
            translate([ 66.2, 4 + (token_diameter + 3) * last_i, wall_height - token_big_thickness - 0.2 ])
                cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            translate([ 46.2, 4 + (token_diameter + 3) * last_i, wall_height - token_big_thickness - 0.2 ])
                cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            // finger holes for tokens.
            translate([ 0, 9.4 + (token_diameter + 3) * i, 7.5 ]) xcyl(r = 6, h = 10, $fn = 32);
            translate([ 0, 9.4 + (token_diameter + 3) * i, 12.2 ]) cuboid([ 12, 12, 12 ]);
            translate([ 77, 9.4 + (token_diameter + 3) * last_i, 7.5 ]) xcyl(r = 6, h = 10, $fn = 32);
            translate([ 77, 9.4 + (token_diameter + 3) * last_i, 12.2 ]) cuboid([ 12, 12, 12 ]);
            // finger indent for the middle secxtion
            translate([ 37, 9.4 + (token_diameter + 3) * i, 11.5 ]) sphere(r = 6, $fn = 32);
            translate([ 59, 9.4 + (token_diameter + 3) * i, 11.5 ]) sphere(r = 6, $fn = 32);
            // Text associated with the tokens.
            if (i % 3 == 0 || i % 3 == 2)
            {
                translate([ 18.5, 9.4 + (token_diameter + 3) * i, wall_height - lid_thickness - 0.4 ])
                    rotate([ 0, 0, 90 ]) linear_extrude(height = 2)
                        text(major_companies[floor(i / 1.5)], size = 3.2, anchor = CENTER);
            }
        }
    }
    echo([ rest_height, wall_height, rest_height - wall_height - 0.75 ]);

    rest_section_height = rest_height - wall_height - 0.70;

    translate([ rest_section_width + 10, 0, 0 ]) difference()
    {
        cube([
            rest_section_width - wall_thickness * 4 - m_piece_wiggle_room * 2,
            train_box_length - wall_thickness * 4 - m_piece_wiggle_room * 2,
            rest_section_height
        ]);
        translate([ 0, 0, 0.75 ])
        {
            for (i = [0:1:4])
            {
                // Cylinder for tokens.
                translate([
                    2.3, 4 + (token_diameter + 3) * i,
                    rest_section_height - (i == 4 ? token_thin_thickness : token_big_thickness) - 0.5
                ]) cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
                translate([ 77, 9.4 + (token_diameter + 3) * i, i == 4 ? 11.2 : 7.5 ]) xcyl(r = 6, h = 10, $fn = 32);
                translate([ 77, 9.4 + (token_diameter + 3) * i, i == 4 ? 20 : 12.2 ]) cuboid([ 12, 12, 12 ]);
                if (i != 1 && i != 4)
                {
                    translate([ 24.2, 4 + (token_diameter + 3) * i, rest_section_height - token_big_thickness - 0.5 ])
                        cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
                    translate([ 46.2, 4 + (token_diameter + 3) * i, rest_section_height - token_big_thickness - 0.5 ])
                        cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
                    // finger indent for the middle secxtion
                    translate([ 37, 9.4 + (token_diameter + 3) * i, 11.5 ]) sphere(r = 6, $fn = 32);
                    translate([ 59, 9.4 + (token_diameter + 3) * i, 11.5 ]) sphere(r = 6, $fn = 32);
                }
                translate([
                    65.8, 4 + (token_diameter + 3) * i,
                    rest_section_height - (i == 4 ? token_thin_thickness : token_big_thickness) - 0.5
                ]) cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
                // finger holes for tokens.
                translate([ 0, 9.4 + (token_diameter + 3) * i, i == 4 ? 13 : 6.5 ]) xcyl(r = 6, h = 10, $fn = 32);
                translate([ 0, 9.4 + (token_diameter + 3) * i, i == 4 ? 20 : 12.2 ]) cuboid([ 12, 12, 12 ]);
            }
            translate([ 38.5, 6.4 + (token_diameter + 3) * 2, rest_section_height - 1.2 ]) linear_extrude(height = 2)
                text("Ferrocarril Central", size = 3.2, anchor = CENTER);
            translate([ 38.5, 6.4 + (token_diameter + 3) * 4, rest_section_height - 1.2 ]) linear_extrude(height = 2)
                text("Yellow", size = 3.2, anchor = CENTER);
            translate([
                32, train_box_length - wall_thickness * 4 - m_piece_wiggle_room * 2 - token_diameter + 1,
                rest_section_height - token_big_thickness - 0.5
            ]) cyl(d = token_diameter, h = token_big_thickness + 1, anchor = FRONT + LEFT + BOTTOM, $fn = 64);
            translate(
                [ 37.5, train_box_length - wall_thickness * 4 - m_piece_wiggle_room * 2, rest_section_height - 4.4 ])
                ycyl(r = 6, h = 10, $fn = 32);
            translate(
                [ 37.5, train_box_length - wall_thickness * 4 - m_piece_wiggle_room * 2, rest_section_height + 1.7 ])
                cuboid([ 12, 12, 12 ]);
        }
    }

    translate([ rest_section_width * 2 + 20, 0, 0 ])
}

LargeTokens();

// Outline() scale(0.05) WagonOutline();
// Outline() scale(0.3) TrainOutline();