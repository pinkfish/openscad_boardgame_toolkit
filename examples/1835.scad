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

box_length = 298;
box_width = 216;
box_height = 50;

wall_thickness = 3;
inner_wall = 1;
lid_height = 2;
floor_thickness = 2;

share_width = 46;
share_length = 66;
share_thickness_twenty = 7;
money_width = 52;
money_length = 98;
money_one_thickness = 5;
money_total = 22;
company_card_bmb_length = 151;
company_card_bmb_width = 106;
company_card_bmb_thickness_six = 2.5;
company_card_length = 200;
company_card_lenght = 131;
token_diameter = 6;
token_thickness = 2;
large_marker_diamter = 20;
large_marker_length = 41;
tile_width = 40;
train_tile_thickness_10 = 6;
board_thickness = 15;

num_train_cards = 33;
num_shares = 68;
num_private_railroad = 6;

main_height = 50 - board_thickness;

hex_box_width = 144;
hex_box_height = main_height / 4;
hex_box_length = max(tile_width * 5 + wall_thickness * 2, 214);

money_box_width = (money_width + 0.5) * 4 + wall_thickness * 2;
money_box_length = money_length + wall_thickness;
money_box_height_1 = floor_thickness + lid_height + money_one_thickness + 0.5;
money_box_height_2 = money_box_height_1 - 1;

money_names = [ "1", "5", "10", "20", "50", "100", "200", "500" ];
share_names = [
    "Bayerische Eisenbahn", "Sächsische Eisenbahn", "Badische Eisenbahn", "Württembergische", "Hessische Eisenbahn",
    "Preußische Eisenbahn", "Mecklenburg-Schwerin", "Oldenburgische"
];

last_section_width = box_length - hex_box_width - money_box_length - 2;
last_section_length = share_length * 2 + wall_thickness * 2;

last_section_first_player = box_width - last_section_length - 1;

shares_height = main_height / 4;

middle_height = main_height - money_box_height_1 - money_box_height_2;
middle_width = money_box_length;
middle_length = money_box_width;

insert_width = middle_width - wall_thickness * 2;
insert_length = middle_length - wall_thickness * 3 - large_marker_diamter;
insert_height = middle_height - lid_height - floor_thickness;

module MoneyBox1()
{
    MakeBoxWithTabsInsetLid(width = money_box_width, length = money_box_length, height = money_box_height_1,
                            wall_thickness = wall_thickness, lid_height = lid_height, floor_thickness = floor_thickness,
                            make_tab_length = false, make_tab_width = true) for (i = [0:1:3])
    {
        translate([ (money_width + inner_wall) * i, 0, 0 ]) difference()
        {
            cube([ money_width, money_length, money_box_height_1 ]);
            translate([ money_width / 2, money_length / 2, 0 ]) linear_extrude(height = 0.2)
                text(money_names[i], font = "Stencil Std:style=Bold", anchor = CENTER);
        }
    }
}

module MoneyBox2()
{
    MakeBoxWithTabsInsetLid(width = money_box_width, length = money_box_length, height = money_box_height_2,
                            wall_thickness = wall_thickness, lid_height = lid_height, floor_thickness = floor_thickness,
                            make_tab_length = false, make_tab_width = true) for (i = [0:1:3])
    {
        translate([ (money_width + inner_wall) * i, 0, 0 ]) difference()
        {
            cube([ money_width, money_length, money_box_height_2 ]);
            translate([ money_width / 2, money_length / 2, 0 ]) linear_extrude(height = 0.2)
                text(money_names[i + 4], font = "Stencil Std:style=Bold", anchor = CENTER);
        }
    }
}

module AllMoneyBoxes()
{
    MoneyBox1();
    translate([ 0, money_box_length + 10, 0 ]) MoneyBox2();
    translate([ 0, money_box_length * 2 + 20, 0 ]) InsetLidTabbedWithLabel(
        width = money_box_width, length = money_box_length, lid_height = lid_height, text_width = 70, text_length = 20,
        text_str = "Money", make_tab_length = false, make_tab_width = true);
}

module HexBox()
{
    MakeBoxWithTabsInsetLid(width = hex_box_width, length = hex_box_length, height = hex_box_height,
                            wall_thickness = wall_thickness, lid_height = lid_height, floor_thickness = floor_thickness)
    {
        translate([ 0, 5, 0 ])
        {
            intersection()
            {
                translate([ 0, 0, -3 ]) cube([ 140, tile_width * 5, hex_box_height ]);
                HexGridWithCutouts(rows = 3, cols = 5, height = hex_box_height, spacing = 0, push_block_height = 0,
                                   tile_width = tile_width);
            }
        }
    }
    translate([ 0, hex_box_length + 10, 0 ])
        InsetLidTabbedWithLabel(width = hex_box_width, length = hex_box_length, lid_height = lid_height,
                                text_width = 70, text_length = 20, text_str = "Tiles");
}

module SharesBox(offset)
{
    MakeBoxWithTabsInsetLid(width = last_section_width, length = last_section_length, height = shares_height,
                            wall_thickness = wall_thickness, lid_height = lid_height, floor_thickness = floor_thickness)
    {
        for (i = [0:1:1])
        {
            translate([ 0, (share_length + 4.5) * i, 0 ])
            {
                if (i + offset < len(share_names))
                {
                    cube([ share_width, share_length, main_height ]);
                    translate([ share_width / 2, share_length / 2, -0.4 ]) linear_extrude(height = 1) rotate(90)
                        text(share_names[i + offset], font = "Stencil Std:style=Bold", anchor = CENTER, size = 4);
                }
                else
                {
                    translate([ share_width / 2, share_length / 2, shares_height - lid_height - 2 ])
                        linear_extrude(height = 1) rotate(90)
                            text("1835", font = "Stencil Std:style=Bold", anchor = CENTER, size = 20);
                }
            }
        }
    };
}

module AllShareBoxes()
{
    SharesBox(0);
    translate([ 0, last_section_length + 10, 0 ]) SharesBox(2);
    translate([ 0, last_section_length * 2 + 20, 0 ]) SharesBox(4);
    translate([ 0, last_section_length * 3 + 30, 0 ]) SharesBox(6);
    translate([ 0, last_section_length * 4 + 40, 0 ])
        InsetLidTabbedWithLabel(width = last_section_width, length = last_section_length, text_width = 70,
                                text_length = 20, text_str = "Shares", lid_height = lid_height, label_rotated = true);
}

module MiddleBox()
{
    token_depths = [ 1, 1, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 4, 4 ];
    labels = [ "White", "Wheel", "1-3", "4-6", "L", "A", "E", "T", "S", "X", "Y", "Y", "R", "R" ];

    difference()
    {
        MakeBoxWithTabsInsetLid(width = middle_width, length = middle_length, height = middle_height,
                                wall_thickness = wall_thickness, lid_height = lid_height,
                                floor_thickness = floor_thickness)
        {
            translate([ insert_width / 2, 11.5, middle_height - lid_height - floor_thickness ])
                linear_extrude(height = 5) text("1835", font = "Stencil Std:style=Bold", anchor = CENTER, size = 20);
            translate([ 47, large_marker_diamter + wall_thickness + 15, 0 ])
                cube([ share_width, share_length, middle_height ]);
            translate([ 47, large_marker_diamter + wall_thickness + share_length + wall_thickness + 30, 0 ])
                cube([ share_width, share_length, middle_height ]);
            translate([ 0, 20, 0 ]) for (i = [0:1:len(token_depths) - 1])
            {
                token_height = token_depths[i] * token_thickness;

                translate([ 0, (i < 6 ? i : i + 1) * (token_diameter + wall_thickness * 2) + 10, 0 ])
                {
                    translate([
                        token_diameter / 2, token_diameter / 2, token_height / 2 + insert_height - token_height - 0.45
                    ]) cyl(d = token_diameter, h = token_height + 1, $fn = 32);
                    translate([ 7, 3, insert_height - 1 ]) linear_extrude(height = 2)
                        text(labels[i], font = "Stencil Std:style=Bold", anchor = LEFT, size = 4);
                }
            }
        }
        translate([ 0, 24.5, 0 ]) for (i = [0:1:len(token_depths) - 1])
        {
            token_height = token_depths[i] * token_thickness;

            translate([ wall_thickness, (i < 6 ? i : i + 1) * (token_diameter + wall_thickness * 2) + 10, 0 ])
                translate([
                    -9, token_diameter / 2 - 1.5, middle_height - token_height - 0.5 + middle_height / 2 -
                    lid_height
                ]) resize([ 20, 8, middle_height ]) rotate([ 0, 0, 30 ]) cyl(d = 5, h = middle_height, $fn = 6);
        }
    }
    translate([ 0, middle_length + 10, 0 ])
        InsetLidTabbedWithLabel(width = middle_width, length = middle_length, lid_height = lid_height, text_length = 20,
                                text_width = 120, text_str = "Tokens/Trains", label_rotated = true);
}

module InsertTray()
{
    token_depths = [ 1, 1, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 4, 4 ];
    labels = [ "White", "Wheel", "1-3", "4-6", "L", "A", "E", "T", "S", "X", "Y", "Y", "R", "R" ];
    first_tray_height = insert_height;
    difference()
    {
        cube([ insert_width, insert_length, first_tray_height ]);
        translate([ wall_thickness, wall_thickness, floor_thickness ])
            cube([ insert_width - 29, insert_length - wall_thickness * 2, insert_height ]);
        for (i = [0:1:len(token_depths) - 1])
        {
            token_height = token_depths[i] * token_thickness;
            translate([ 69, i * (token_diameter + wall_thickness * 2) + 10, 0 ])
            {
                translate(
                    [ token_diameter / 2, token_diameter / 2, token_height / 2 + insert_height - token_height - 0.45 ])
                    cyl(d = token_diameter, h = token_height + 1, $fn = 32);
                translate([ -1, token_diameter / 2 - 1.5, insert_height - token_height - 0.45 ])
                    cube([ 5, token_diameter - 3, first_tray_height ]);
                translate([ 7, 3, insert_height - 1 ]) linear_extrude(height = 2)
                    text(labels[i], font = "Stencil Std:style=Bold", anchor = LEFT, size = 4);
            }
        }
    }
}

module LastSectionFirstPlayer()
{
    MakeBoxWithCapLid(width = last_section_width, length = last_section_first_player, height = main_height,
                      floor_thickness = floor_thickness)
    {
        translate([ 3, 30, 14 ])
        {
            xcyl(d = large_marker_diamter, h = large_marker_length, anchor = BOTTOM + LEFT + FRONT, $fn = 64);
            translate([ 0, -3, large_marker_diamter / 2 - 2 ])
                cuboid([ large_marker_length, large_marker_diamter, large_marker_diamter / 2 ],
                       anchor = BOTTOM + LEFT + FRONT);
        }
        translate([ last_section_width / 2 - 1, 21, 20 ])
        {
            translate([ 0, -3, 5 ]) cyl(r = 10, h = large_marker_diamter, anchor = BOTTOM + FRONT);
            sphere(r = 10, anchor = BOTTOM + FRONT, $fn = 64);
        }
        translate([ last_section_width / 2 - 1, 39, 20 ])
        {
            translate([ 0, -3, 5 ]) cyl(r = 10, h = large_marker_diamter, anchor = BOTTOM + FRONT);
            sphere(r = 10, anchor = BOTTOM + FRONT, $fn = 64);
        }
    }
}

MiddleBox();

translate([ middle_width + 10, 0, 0 ]) AllShareBoxes();

translate([ middle_width + last_section_width + last_section_width + 30, 0, 0 ]) AllMoneyBoxes();

translate([ middle_width + last_section_width + last_section_width + money_box_width + 40, 0, 0 ]) HexBox();