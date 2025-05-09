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

box_length = 308;
box_width = 219;
box_height = 70;

board_thickness = 15;

default_label_solid_background = MAKE_MMU == 1;
default_lid_thickness = 3;
default_floor_thickness = 2;
default_wall_thickness = 3;

middle_height = box_height - board_thickness;

tile_thickness = 2;

train_tile_width = 20.5;
train_tile_length = 41;
train_tile_pointy_len = 10;

bonus_train_tile_width = 26;
bonus_train_tile_length = 45;

kiev_medal_width = 24.5;
kiev_medal_length = 39;

question_token_diameter = 23;

rubel_token_diameter = 24.5;

doubler_size = 20;

extra_score_track_width = 18;
extra_score_track_length = 31.5;

engineer_width = 36;
engineer_length = 81.5;
engineer_long_cut = 10;
engineer_short_cut = 6;

worker_length = 24;
worker_width = 17.5;
worker_thickness = 10;

pawn_width = 21.5;
pawn_length = 18.5;
pawn_thickness = 10;
pawn_top_width = 16;
pawn_top_height = 7.5;
pawn_bottom_shoulder = 7;
pawn_middle_width = 14;

rail_white_length = 15;
rail_white_width = 17;
rail_white_bar = 4.25;
rail_white_middle = 7.5;
rail_white_thickness = 16.5;

rail_other_length = 14;
rail_other_width = 13;
rail_other_bar = 3;
rail_other_middle = 5;
rail_other_thickness = 13;

industry_thickness = 10;
industry_hex = 11;

start_tile_width = 41;
start_tile_length = 76;

cards_width = 44;
cards_length = 68;
cards_thickness = 7;

// player stuff
num_workers_per_player = 8;
num_pawns_per_player = 2;
num_industry_markers_per_player = 2;
num_question_tokens_per_player = 7;
num_kiev_medals_per_player = 1;
num_reevaluation_markers_per_player = 1;

num_doubler_tokens = 20;

player_box_width = (box_width - 2) / 2;
player_box_length = worker_length * 2 + default_wall_thickness * 2 + 2 + kiev_medal_width;
player_box_height = middle_height / 3;
label_height = 0.2;

extra_tokens_box_width = player_box_width;
extra_tokens_box_length = player_box_length;
extra_tokens_box_height = player_box_height;

money_box_width = player_box_width;
money_box_length = player_box_length;
money_box_height = player_box_height;

card_box_length = train_tile_length * 2 + default_wall_thickness * 2 + 2;
card_box_width = default_wall_thickness * 2 + 12;
card_box_height = middle_height;

train_box_length = train_tile_length * 2 + default_wall_thickness * 2 + 2;
train_box_width = box_width - 2 - card_box_width;
train_box_height = tile_thickness * 4 + default_floor_thickness + default_lid_thickness + 2;

engineer_box_length = train_box_length;
engineer_box_width = train_box_width;
engineer_box_height = tile_thickness * 3 + default_floor_thickness + default_lid_thickness + 2;

track_box_length = train_box_length;
track_box_width = train_box_width;
track_box_height = middle_height - train_box_height - engineer_box_height;

spacer_width = box_width - 2;
spacer_length = box_length - 2 - player_box_length - train_box_length;
spacer_height = middle_height;

module WhiteTrack(height)
{
    difference()
    {
        cuboid([ rail_white_width, rail_white_length, height ], anchor = BOTTOM, rounding = 1,
               edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
        translate([ -rail_white_middle / 2, 0, -0.5 ]) cuboid(
            [ rail_white_width - rail_white_middle, rail_white_length - rail_white_bar * 2, height + 1 ],
            anchor = BOTTOM + RIGHT, edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ], rounding = 1);
        translate([ rail_white_middle / 2, 0, -0.5 ]) cuboid(
            [ rail_white_width - rail_white_middle, rail_white_length - rail_white_bar * 2, height + 1 ],
            anchor = BOTTOM + LEFT, rounding = 1, edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ]);
    }
}

module PawnOutline(height)
{
    translate([ 0, -pawn_length / 2, 0 ])
    {
        difference()
        {
            cyl(d = pawn_top_width, h = height, anchor = BOTTOM + FRONT);
            translate([ 0, pawn_top_width / 2 + 0.5, -0.5 ])
                cuboid([ pawn_top_width + 1, pawn_top_width, height + 1 ], anchor = BOTTOM + FRONT);
        }
        translate([ 0, pawn_top_height, 0 ])
            cuboid([ pawn_middle_width, pawn_length - pawn_top_height, height ], anchor = BOTTOM + FRONT);
        hull()
        {
            translate([ pawn_middle_width / 2 - 0.5, pawn_length - pawn_bottom_shoulder, 0 ])
                cyl(r = 1, h = height, anchor = BOTTOM + FRONT);
            translate([ -pawn_middle_width / 2 + 0.5, pawn_length - pawn_bottom_shoulder, 0 ])
                cyl(r = 1, h = height, anchor = BOTTOM + FRONT);
            translate([ pawn_width / 2 - 2, pawn_length - 1.5, 0 ]) cyl(r = 2, h = height, anchor = BOTTOM + BACK);

            translate([ -pawn_width / 2 + 0.5, pawn_length, 0 ]) cyl(r = 1, h = height, anchor = BOTTOM + BACK);
            translate([ pawn_width / 2 - 0.5, pawn_length, 0 ]) cyl(r = 1, h = height, anchor = BOTTOM + BACK);

            translate([ -pawn_width / 2 + 2, pawn_length - 1.5, 0 ]) cyl(r = 2, h = height, anchor = BOTTOM + BACK);
        }
    }
}

module TrainTile(height)
{
    translate([ 0, -5, 0 ]) cuboid([ train_tile_width, train_tile_length - 10, height ], anchor = BOTTOM);
    hull()
    {
        translate([ train_tile_width / 2 - 0.5, train_tile_length / 2 - 0.5 - train_tile_pointy_len, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ -train_tile_width / 2 + 0.5, train_tile_length / 2 - 0.5 - train_tile_pointy_len, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ 0, train_tile_length / 2 - 1, 0 ]) cyl(d = 2, h = height, anchor = BOTTOM);
    }
}

module EngineerTile(height)
{
    hull()
    {
        translate([ engineer_width / 2 - 0.5, engineer_length / 2 - 0.5 - engineer_short_cut, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ engineer_width / 2 - 0.5 - engineer_short_cut, engineer_length / 2 - 0.5, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ -engineer_width / 2 - 0.5 + engineer_short_cut, engineer_length / 2 - 0.5, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ -engineer_width / 2 + 0.5, engineer_length / 2 - 0.5 - engineer_short_cut, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ -engineer_width / 2 + 0.5, -engineer_length / 2 - 0.5, 0 ]) cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ engineer_width / 2 - 0.5 - engineer_long_cut, -engineer_length / 2 - 0.5, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
        translate([ engineer_width / 2 - 0.5, -engineer_length / 2 - 0.5 + engineer_long_cut, 0 ])
            cyl(d = 1, h = height, anchor = BOTTOM);
    }
}

module PlayerBox() // `make` me
{
    MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height,
                          wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness,
                          floor_thickness = default_floor_thickness)
    {

        // Question Tokens
        translate([
            $inner_width - question_token_diameter / 2, question_token_diameter / 2,
            $inner_height - num_question_tokens_per_player * tile_thickness - 0.2
        ])
        {
            cyl(d = question_token_diameter, h = num_question_tokens_per_player * tile_thickness + 100,
                anchor = BOTTOM);
            translate([ 0, -question_token_diameter / 2, 0.25 ]) FingerHoleWall(
                radius = 8, height = num_question_tokens_per_player * tile_thickness, spin = 0, depth_of_hole = 12);
        }

        // Bonus tiles.
        translate([
            $inner_width - kiev_medal_width / 2, $inner_length - kiev_medal_length / 2 - 2,
            $inner_height - 2 * tile_thickness - 0.5
        ]) rotate(270)
        {
            cuboid([ kiev_medal_length, kiev_medal_width, tile_thickness * 2 + 3 ], anchor = BOTTOM);
            translate([ kiev_medal_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
            translate([ 0, 0, 2.2 ])
            {
                cuboid([ bonus_train_tile_length, bonus_train_tile_width, tile_thickness * 2 + 4 ], anchor = BOTTOM);
                translate([ bonus_train_tile_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
            }
        }

        // Dip for all the workers and stuff.
        translate([ 0, 0, $inner_height - 5 ])
            RoundedBoxAllSides(width = (worker_width + 1) * 4 + 2, length = $inner_length, height = 6, radius = 5);

        // Workers
        for (j = [0:1:3])
        {
            translate([
                (worker_width + 1) * j + worker_width / 2, worker_length / 2, $inner_height - worker_thickness - 0.5
            ]) cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);
            translate([
                (worker_width + 1) * j + worker_width / 2, $inner_length - worker_length / 2,
                $inner_height - worker_thickness - 0.5
            ]) cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);

            translate([
                (worker_width + 1) * j + worker_width / 2, -default_wall_thickness - 0.02,
                $inner_height - worker_thickness / 2 - 0.5
            ]) ycyl(r = 7.5, h = default_wall_thickness * 3, anchor = BOTTOM);
            translate([
                (worker_width + 1) * j + worker_width / 2, $inner_length, $inner_height - worker_thickness / 2 - 0.5
            ]) ycyl(r = 7.5, h = default_wall_thickness * 3, anchor = BOTTOM);
        }

        // Industry hexes
        translate([ industry_hex, ($inner_length) / 2, $inner_height - industry_thickness - 0.5 ])
        {
            rotate([ 0, 0, 30 ]) RegularPolygon(width = industry_hex, height = industry_thickness + 1, shape_edges = 6);
            translate([ industry_hex + 2, 0, 0 ])
            {
                rotate([ 0, 0, 30 ])
                    RegularPolygon(width = industry_hex, height = industry_thickness + 1, shape_edges = 6);
            }
        }

        // Pawn 1
        translate([ industry_hex * 4, $inner_length / 2, $inner_height - pawn_thickness - 0.5 ])
        {
            rotate([ 0, 0, 180 ]) PawnOutline(pawn_thickness + 1);
        }

        // Pawn 2
        translate([ industry_hex * 4 + pawn_width - 3, $inner_length / 2, $inner_height - pawn_thickness - 0.5 ])
            PawnOutline(pawn_thickness + 1);
    }
}

module PlayerBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = player_box_width, length = player_box_length, text_width = 70, text_height = 20,
                           text_str = "Player", wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness);
}

module ExtraTokensBox() // `make` me
{
    module InnerBits(show_everything)
    {
        // Blue
        translate([ worker_width / 2, worker_length / 2, $inner_height - worker_thickness - 1.5 ])
        {
            if (show_everything)
            {
                cuboid([ worker_width, worker_length, worker_thickness + 2 ], anchor = BOTTOM);
                translate([ 0, -worker_length / 2, 0 ])
                {
                    ycyl(r = 6, h = 10, anchor = BOTTOM, $fn = 64);
                    translate([ 0, 0, 6 ]) cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3,
                                                  edges = [ TOP + LEFT, TOP + RIGHT ], $fn = 64);
                }
            }
            translate([ 0, 0, -0.19 ]) rotate(90) linear_extrude(height = label_height)
                text("Purple", valign = "center", halign = "center", size = 3);
        }
        translate([ worker_width + worker_width / 2 + 2, worker_length / 2, $inner_height - worker_thickness - 1.5 ])
        {
            if (show_everything)
            {
                cuboid([ worker_width, worker_length, worker_thickness + 2 ], anchor = BOTTOM);
                translate([ 0, -worker_length / 2, 0 ])
                {
                    ycyl(r = 6, h = 10, anchor = BOTTOM, $fn = 64);
                    translate([ 0, 0, 6 ]) cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3,
                                                  edges = [ TOP + LEFT, TOP + RIGHT ], $fn = 64);
                }
            }
            translate([ 0, 0, -0.19 ]) rotate(90) linear_extrude(height = label_height)
                text("Purple", valign = "center", halign = "center", size = 3);
        }

        // Black
        translate([
            worker_width, $inner_length - worker_length / 2, $inner_height - worker_thickness - 2.9 +
            default_lid_thickness
        ])
        {
            if (show_everything)
            {
                cuboid([ worker_width, worker_length, worker_thickness + 2 ], anchor = BOTTOM);
                translate([ 0, worker_length / 2, 0 ])
                {
                    ycyl(r = 6, h = 10, anchor = BOTTOM);
                    translate([ 0, 0, 7 ])
                        cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3, edges = [ TOP + LEFT, TOP + RIGHT ]);
                }
            }
            translate([ 0, 0, -0.19 ]) rotate(90) linear_extrude(height = label_height)
                text("Black", valign = "center", halign = "center", size = 3);
        }

        // Doublers.
        translate([ worker_width * 2 + 4, 0, $inner_height - tile_thickness * 4 - 0.5 ])
        {
            for (j = [0:1:2])
            {
                translate([ j * (doubler_size + 1) + doubler_size / 2, doubler_size / 2, 0 ])
                {
                    if (show_everything)
                    {
                        cuboid([ doubler_size, doubler_size, tile_thickness * 4 + 1 ], anchor = BOTTOM);
                        translate([ 0, -doubler_size / 2 - 2, 0 ]) ycyl(r = 8, h = 5, anchor = BOTTOM);
                        translate([ 0, -doubler_size / 2, tile_thickness * 2 + 0.51 ])
                            cuboid([ 14, 14, tile_thickness * 2 ], anchor = BOTTOM, rounding = -3,
                                   edges = [ TOP + LEFT, TOP + RIGHT ], $fn = 64);
                    }
                    translate([ 0, 0, -0.19 ]) rotate(90) linear_extrude(height = label_height)
                        text("x2", valign = "center", halign = "center", size = 3);
                }
                translate([ j * (doubler_size + 1) + doubler_size / 2, $inner_length - doubler_size / 2, 0 ])
                {
                    if (show_everything)
                    {
                        cuboid([ doubler_size, doubler_size, tile_thickness * num_doubler_tokens * 4 + 1 ],
                               anchor = BOTTOM);
                        translate([ 0, doubler_size / 2 + 2, 0 ]) ycyl(r = 8, h = 5, anchor = BOTTOM);
                        translate([ 0, doubler_size / 2, tile_thickness * 2 + 0.51 + default_lid_thickness ])
                            cuboid([ doubler_size - 4, 16, tile_thickness * 2 ], anchor = BOTTOM, rounding = -3,
                                   edges = [ TOP + LEFT, TOP + RIGHT ], $fn = 64);
                    }
                    translate([ 0, 0, -0.19 ]) rotate(90) linear_extrude(height = label_height)
                        text("x2", valign = "center", halign = "center", size = 3);
                }
            }
        }

        // Bonus tiles.
        translate([ extra_score_track_length / 2, ($inner_length) / 2, $inner_height - tile_thickness * 4 - 0.5 ])
        {
            if (show_everything)
            {
                cuboid([ extra_score_track_length, extra_score_track_width, tile_thickness * 4 + 1 ], anchor = BOTTOM);
                translate([ -extra_score_track_length / 2, 0, 0 ])
                {
                    xcyl(r = 7, h = 20, anchor = BOTTOM, $fn = 64);
                    translate([ 0, 0, default_lid_thickness + tile_thickness * 2 + 0.51 ])
                        cuboid([ 14, 14, tile_thickness * 2 ], anchor = BOTTOM, rounding = -3,
                               edges = [ TOP + FRONT, TOP + BACK ], $fn = 64);
                }
            }
            translate([ 0, 0, -0.19 ]) linear_extrude(height = label_height)
                text("Bonus", valign = "center", halign = "center", size = 3);
        }
        translate([
            $inner_width - extra_score_track_length / 2, ($inner_length) / 2, $inner_height - tile_thickness * 4 - 0.5
        ])
        {
            if (show_everything)
            {
                cuboid([ extra_score_track_length, extra_score_track_width, tile_thickness * 4 + 1 ], anchor = BOTTOM);
                translate([ extra_score_track_length / 2, 0, 0 ])
                {
                    xcyl(r = 7, h = 20, anchor = BOTTOM, $fn = 64);
                    translate([ 0, 0, default_lid_thickness + tile_thickness * 2 + 0.51 ])
                        cuboid([ 14, 14, tile_thickness * 2 ], anchor = BOTTOM, rounding = -3,
                               edges = [ TOP + FRONT, TOP + BACK ], $fn = 64);
                }
            }
            translate([ 0, 0, -0.19 ]) linear_extrude(height = label_height)
                text("Bonus", valign = "center", halign = "center", size = 3);
        }
    }
    MakeBoxWithSlidingLid(width = extra_tokens_box_width, length = extra_tokens_box_length,
                          height = extra_tokens_box_height, wall_thickness = default_wall_thickness,
                          lid_thickness = default_lid_thickness, floor_thickness = default_floor_thickness,
                          last_child_positive = default_label_solid_background)
    {
        InnerBits(true);
        if (default_label_solid_background)
        {
            color("black") InnerBits(false);
        }
    }
}

module ExtraTokensBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = extra_tokens_box_width, length = extra_tokens_box_length, text_width = 70,
                           text_height = 20, text_str = "Extra", wall_thickness = default_wall_thickness,
                           lid_thickness = default_lid_thickness);
}

module MoneyBox() // `make` me
{
    MakeBoxWithSlidingLid(width = money_box_width, length = money_box_length, height = money_box_height,
                          wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness,
                          floor_thickness = default_floor_thickness)
    {
        RoundedBoxAllSides(width = $inner_width, length = $inner_length, height = $inner_height + 1, radius = 6);
    }
}

module MoneyBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = money_box_width, length = money_box_length, text_width = 70, text_height = 20,
                           text_str = "Money", wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness);
}

module CardBox() // `make` me
{
    MakeBoxWithSlidingLid(width = card_box_width, length = card_box_length, height = card_box_height)
    {
        translate([ 0, ($inner_length - cards_length) / 2, $inner_height - cards_width - 1 ])
        {
            cube([ $inner_width, cards_length, cards_width + 2 ]);
        }
        translate([ 6, $inner_length / 2, $inner_height - 19.9 + default_lid_thickness ])
            FingerHoleWall(radius = 30, height = 20, spin = 90, depth_of_hole = card_box_width + 2);
    }
}

module CardBoxLid() // `make` me
{
    SlidingLid(width = card_box_width, length = card_box_length, wall_thickness = default_wall_thickness,
               lid_thickness = default_lid_thickness);
}

module TrainBox() // `make` me
{
    module InnerBits(show_everything)
    {
        for (i = [0:1:3])
        {
            translate([
                (train_tile_width + 8) * i + train_tile_width / 2 + 5, train_tile_length / 2,
                $inner_height - tile_thickness * 4 - 0.5
            ])
            {
                if (show_everything)
                {
                    TrainTile(height = tile_thickness * 4 + 1);
                    translate([ 0, train_tile_length / 2, 0.5 ]) ycyl(d = 15, anchor = BOTTOM, h = 20);
                }
                translate([ 0, 0, -0.19 ]) linear_extrude(height = label_height)
                    text(str(i * 2 + 1), valign = "center", halign = "center", size = 3);
            }
            translate([
                (train_tile_width + 8) * i + train_tile_width / 2 + 5, $inner_length - train_tile_length / 2,
                $inner_height - tile_thickness * 4 - 0.5
            ])
            {
                if (show_everything)
                {
                    rotate([ 0, 0, 180 ]) TrainTile(height = tile_thickness * 4 + 1);
                }
                translate([ 0, 0, -0.19 ]) rotate([ 0, 0, 180 ]) linear_extrude(height = label_height)
                    text(str(i * 2 + 1), valign = "center", halign = "center", size = 3);
            }
        }
        translate([
            (train_tile_width + 8) * 4 + 18, $inner_length - train_tile_length / 2,
            $inner_height - tile_thickness * 3 - 0.5
        ])
        {
            if (show_everything)
            {
                rotate([ 0, 0, 180 ]) TrainTile(height = tile_thickness * 5 + 1);
                translate([ -train_tile_width / 2, 4, 0 ]) sphere(d = 20, anchor = BOTTOM);
            }
            translate([ 0, 0, -0.19 ]) rotate([ 0, 0, 180 ]) linear_extrude(height = label_height)
                text("9", valign = "center", halign = "center", size = 3);
        }
        translate([ (train_tile_width + 8) * 4 + 18, train_tile_length / 2, $inner_height - tile_thickness * 2 - 0.5 ])
        {
            if (show_everything)
            {
                TrainTile(height = tile_thickness * 5 + 1);
                translate([ -train_tile_width / 2, -4, 0 ]) sphere(d = 20, anchor = BOTTOM);
            }
            translate([ 0, 0, -0.19 ]) linear_extrude(height = label_height)
                text("9", valign = "center", halign = "center", size = 3);
        }
        translate([ (train_tile_width + 8) * 5 + 23, $inner_length / 2, $inner_height - tile_thickness - 0.5 ])
        {
            if (show_everything)
            {
                rotate([ 0, 0, 180 ])
                    cuboid([ start_tile_width, start_tile_length, tile_thickness * 2 ], anchor = BOTTOM);
                translate([ engineer_width / 2, 0, 0 ]) sphere(d = 30, anchor = BOTTOM);
            }
            translate([ 0, 0, -0.19 ]) rotate(270) linear_extrude(height = label_height)
                text("Start", valign = "center", halign = "center", size = 5);
        }
    }
    MakeBoxWithSlidingLid(width = train_box_width, length = train_box_length, height = train_box_height,
                          wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness,
                          floor_thickness = default_floor_thickness, last_child_positive = default_label_solid_background)
    {
        InnerBits(true);
        if (default_label_solid_background)
        {
            union()
            {
                color("black") InnerBits(false);
            }
        }
    }
}

module TrainBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = train_box_width, length = train_box_length, text_width = 70, text_height = 20,
                           text_str = "Trains", wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness);
}

module EngineerBox() // `make` me
{
    MakeBoxWithSlidingLid(width = engineer_box_width, length = engineer_box_length, height = engineer_box_height,
                          wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness,
                          floor_thickness = default_floor_thickness)
    {
        translate([ engineer_width / 2 + 4, 0, $inner_height - tile_thickness * 3 - 0.5 ]) for (i = [0:1:4])
        {
            translate([ (engineer_width + 2.5) * i, engineer_length / 2, 0 ])
            {
                rotate([ 0, 0, 180 ]) EngineerTile(height = tile_thickness * 3 + 1);
                translate([ 0, -engineer_length / 2 - 0.5, 0 ])
                    FingerHoleWall(radius = 10, height = tile_thickness * 3 + 0.51);
            }
        }
    }
}

module EngineerBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = engineer_box_width, length = engineer_box_length, text_width = 70, text_height = 20,
                           text_str = "Engineers", wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness);
}

module TrackBox() // `make` me
{
    module InnerPieces(show_everything)
    {
        translate([ 0.5, 0.5, 0 ])
        {
            box_section_len = ($inner_width - 5 - rail_white_width - 2) / 4;
            if (show_everything)
            {
                cube([ box_section_len, $inner_length - 1, track_box_height ]);
            }
            translate([ $inner_length / 4, $inner_length / 2, -0.19 ]) rotate(270) linear_extrude(height = label_height)
                text("Grey", valign = "center", halign = "center", size = 5);
            translate([ box_section_len + 2, 0, 0 ])
            {
                if (show_everything)
                {
                    cube([ box_section_len, $inner_length - 1, track_box_height ]);
                }
                translate([ $inner_length / 4, $inner_length / 2, -0.19 ]) rotate(270)
                    linear_extrude(height = label_height) text("Brown", valign = "center", halign = "center", size = 5);
                translate([ box_section_len + 2, 0, 0 ])
                {
                    if (show_everything)
                    {
                        cube([ box_section_len, $inner_length - 1, track_box_height ]);
                    }
                    translate([ $inner_length / 4, $inner_length / 2, -0.19 ]) rotate(270)
                        linear_extrude(height = label_height)
                            text("Black", valign = "center", halign = "center", size = 5);
                    translate([ box_section_len + 2, 0, 0 ])
                    {
                        if (show_everything)
                        {
                            cube([ box_section_len, $inner_length - 1, track_box_height ]);
                        }
                        translate([ $inner_length / 4, $inner_length / 2, -0.19 ]) rotate(270)
                            linear_extrude(height = label_height)
                                text("Natural", valign = "center", halign = "center", size = 5);
                        if (show_everything)
                        {
                            translate([ box_section_len + 2 + rail_white_width / 2, rail_white_length / 2 + 4, 0 ])
                            {
                                for (i = [0:1:3])
                                {
                                    translate([
                                        0, (rail_white_length + 5) * i,
                                        $inner_height - rail_white_thickness - 0.5
                                    ])
                                    {
                                        rotate([ 0, 0, 90 ]) WhiteTrack(height = rail_white_thickness + 1);
                                        translate([ -rail_white_length / 2 - 2, 0, 4 ]) sphere(r = 7, anchor = BOTTOM);
                                    }
                                }
                                translate([ -rail_white_length / 2 - 8, -11.5, $inner_height - 5.8 ])
                                    RoundedBoxAllSides(width = rail_white_length + 10, length = $inner_length,
                                                       height = 6, radius = 5);
                            }
                        }
                    }
                }
            }
        }
    }
    MakeBoxWithSlidingLid(width = track_box_width, length = track_box_length, height = track_box_height,
                          wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness,
                          floor_thickness = lid_thickness, last_child_positive = default_label_solid_background)
    {
        InnerPieces(show_everything = true);
        if (default_label_solid_background)
        {
            color("black") InnerPieces(show_everything = false);
        }
    }
}

module TrackBoxLid() // `make` me
{
    SlidingBoxLidWithLabel(width = track_box_width, length = track_box_length, text_width = 70, text_height = 20,
                           text_str = "Tracks", wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness);
}
module SpacerSide() // `make` me
{
    difference()
    {
        color("yellow") cuboid([ spacer_width, spacer_length, spacer_height ], anchor = BOTTOM + LEFT + FRONT,
                               rounding = 2, $fn = 32);
        translate([ default_wall_thickness, default_wall_thickness, default_floor_thickness ])
            cuboid([ spacer_width - default_wall_thickness * 2, spacer_length - default_wall_thickness * 2, spacer_height + 10 ],
                   anchor = BOTTOM + LEFT + FRONT);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        PlayerBox();
        translate([ player_box_width, 0, 0 ]) PlayerBox();
        translate([ 0, 0, player_box_height ]) PlayerBox();
        translate([ player_box_width, 0, player_box_height ]) PlayerBox();
        translate([ 0, 0, player_box_height * 2 ]) ExtraTokensBox();
        translate([ player_box_width, 0, player_box_height * 2 ]) MoneyBox();
        translate([ 0, player_box_length, 0 ]) TrainBox();
        translate([ 0, player_box_length, train_box_height ]) EngineerBox();
        translate([ 0, player_box_length, train_box_height + engineer_box_height ]) TrackBox();
        translate([ engineer_box_width, player_box_length, 0 ]) CardBox();
        translate([ 0, player_box_length + train_box_length, 0 ]) SpacerSide();
    }
}

module PrintLayout()
{
    PlayerBox();
    translate([ player_box_width + 10, 0, 0 ])
    {
        ExtraTokensBox();
        translate([ extra_tokens_box_width + 10, 0, 0 ])
        {
            MoneyBox();
            translate([ money_box_width + 10, 0, 0 ])
            {
                TrainBox();
                translate([ train_box_width + 10, 0, 0 ])
                {
                    EngineerBox();
                    translate([ engineer_box_width + 10, 0, 0 ])
                    {
                        TrackBox();
                    }
                }
            }
        }
    }
}

module TestBox()
{
    difference()
    {
        cuboid([ 50, 50, 6 ], anchor = BOTTOM);
        translate([ 13, -10, 1 ])
        {
            WhiteTrack(10);
            translate([ -rail_white_width / 2 - train_tile_width / 2 - 2, 10, 0 ]) TrainTile(height = 10);
            translate([ -2, rail_white_length / 2 + pawn_length / 2 + 2, 0 ]) PawnOutline(height = 10);
        }
    }
}

if (FROM_MAKE != 1)
{
    CardBox();
}