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

middle_height = box_height - board_thickness;

tile_thickness = 2;
wall_thickness = 3;
lid_thickness = 2;

train_tile_width = 20.5;
train_tile_length = 41;
train_tile_pointy_len = 10;

bonus_train_tile_width = 26;
bonus_train_tile_length = 45;

kiev_medal_width = 24.5;
kiev_medal_length = 39;

question_token_diameter = 22;

rubel_token_diameter = 24.5;

doubler_size = 20;

extra_score_track_width = 18;
extra_score_track_length = 31.5;

engineer_width = 36;
engineer_length = 81.5;
engineer_long_cut = 10;
engineer_short_cut = 6;

worker_length = 23;
worker_width = 16;
worker_thickness = 10;

pawn_width = 20.5;
pawn_length = 18;
pawn_thickness = 10;
pawn_top_width = 15;
pawn_top_height = 7.5;
pawn_bottom_shoulder = 7;
pawn_middle_width = 11;

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
player_box_length = worker_length * 2 + wall_thickness * 2 + 4 + kiev_medal_width;
player_box_height = middle_height / 3;

extra_tokens_box_width = player_box_width;
extra_tokens_box_length = player_box_length;
extra_tokens_box_height = player_box_height;

money_box_width = player_box_width;
money_box_length = player_box_length;
money_box_height = player_box_height;

train_box_length = train_tile_length * 2 + wall_thickness * 2 + 2;
train_box_width = box_width - 2;
train_box_height = middle_height / 2;

engineer_box_length = train_box_length;
engineer_box_width = train_box_width;
engineer_box_height = train_box_height;

track_box_length = train_box_length;
track_box_width = train_box_width;
track_box_height = train_box_height;

echo([player_box_height]);

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

            translate([ -pawn_width / 2 + 0.5, pawn_length, 0 ]) cyl(r = 1, h = height, anchor = BOTTOM + BACK);
            translate([ pawn_width / 2 - 0.5, pawn_length, 0 ]) cyl(r = 1, h = height, anchor = BOTTOM + BACK);
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

module PlayerBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = player_box_width, length = player_box_length, height = player_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {

        for (j = [0:1:3])
        {
            translate([
                (worker_width + 1) * j + worker_width / 2, worker_length / 2,
                player_box_height - lid_thickness * 2 - worker_thickness - 0.5
            ]) cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);
            translate([
                (worker_width + 1) * j + worker_width / 2, player_box_length - wall_thickness * 2 - worker_length / 2,
                player_box_height - lid_thickness * 2 - worker_thickness - 0.5
            ]) cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);

            translate([
                (worker_width + 1) * j + worker_width / 2, -wall_thickness - 0.02,
                player_box_height - lid_thickness * 2 - worker_thickness / 2 - 0.5
            ]) ycyl(r = 7.5, h = wall_thickness * 3, anchor = BOTTOM);
            translate([
                (worker_width + 1) * j + worker_width / 2, player_box_length - wall_thickness * 2,
                player_box_height - lid_thickness * 2 - worker_thickness / 2 - 0.5
            ]) ycyl(r = 7.5, h = wall_thickness * 3, anchor = BOTTOM);
        }
        translate([
            (worker_width + 1) * 4 + pawn_width / 2, pawn_length / 2,
            player_box_height - lid_thickness * 2 - pawn_thickness - 0.5
        ]) rotate([ 0, 0, 180 ]) PawnOutline(pawn_thickness + 1);
        translate(
            [ (worker_width + 1) * 4 + pawn_width / 2, -3, player_box_height - lid_thickness * 2 - pawn_thickness / 2 ])
            FingerHoleWall(radius = 6, height = pawn_thickness / 2, depth_of_hole = 12);

        translate([
            (worker_width + 1) * 4 + pawn_width / 2, player_box_length - pawn_length / 2 - wall_thickness * 2,
            player_box_height - lid_thickness * 2 - pawn_thickness - 0.5
        ]) PawnOutline(pawn_thickness + 1);
        translate([
            (worker_width + 1) * 4 + pawn_width / 2, player_box_length - wall_thickness,
            player_box_height - lid_thickness * 2 - pawn_thickness / 2
        ]) FingerHoleWall(radius = 6, height = pawn_thickness / 2, depth_of_hole = 12);

        translate([
            player_box_width - wall_thickness * 2 - question_token_diameter / 2,
            (player_box_length - wall_thickness * 2) / 2,
            player_box_height - lid_thickness * 2 - num_question_tokens_per_player * tile_thickness - 0.2
        ]) cyl(d = question_token_diameter, h = num_question_tokens_per_player * tile_thickness + 100, anchor = BOTTOM);
        translate([ player_box_width - wall_thickness * 2 + 0.3, (player_box_length - wall_thickness * 2) / 2, 0.34 ])
            FingerHoleWall(radius = 8, height = num_question_tokens_per_player * tile_thickness, spin = 90,
                           depth_of_hole = 12);

        translate([
            bonus_train_tile_length / 2, (player_box_length - wall_thickness * 2) / 2,
            player_box_height - lid_thickness * 2 - 2 * tile_thickness - 0.5
        ])
        {
            cuboid([ kiev_medal_length, kiev_medal_width, tile_thickness * 2 + 3 ], anchor = BOTTOM);
            translate([ kiev_medal_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
            translate([ 0, 0, 2.2 ])
            {
                cuboid([ bonus_train_tile_length, bonus_train_tile_width, tile_thickness * 2 + 4 ], anchor = BOTTOM);
                translate([ bonus_train_tile_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
            }
        }

        translate([
            bonus_train_tile_length + 2 + industry_hex + 1, (player_box_length - wall_thickness * 2) / 2,
            player_box_height - lid_thickness * 2 - industry_thickness - 0.5
        ])
        {
            rotate([ 0, 0, 30 ]) RegularPolygon(width = industry_hex, height = industry_thickness + 1, shape_edges = 6);
            translate([ industry_hex / 2 + 1, 0, industry_thickness / 2 ]) sphere(r = 9, anchor = BOTTOM);
            translate([ industry_hex + 2, 0, 0 ]) rotate([ 0, 0, 30 ])
                RegularPolygon(width = industry_hex, height = industry_thickness + 1, shape_edges = 6);
        }
    }
    if (generate_lid)
    {
        translate([ 0, player_box_length + 10, 0 ]) CapBoxLidWithLabel(
            width = player_box_width, length = player_box_length, height = player_box_height, text_width = 70,
            text_height = 20, text_str = "Player", wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module ExtraTokensBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = extra_tokens_box_width, length = extra_tokens_box_length,
                      height = extra_tokens_box_height, wall_thickness = wall_thickness, lid_thickness = lid_thickness,
                      floor_thickness = lid_thickness)
    {
        // Blue
        translate(
            [ worker_width / 2, worker_length / 2, player_box_height - lid_thickness * 2 - worker_thickness - 0.5 ])
        {
            cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);
            translate([ 0, -worker_length / 2, 0 ])
            {
                ycyl(r = 6, h = 10, anchor = BOTTOM);
                translate([ 0, 0, 6 ])
                    cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3, edges = [ TOP + LEFT, TOP + RIGHT ]);
            }
        }
        translate([
            worker_width + worker_width / 2 + 2, worker_length / 2,
            player_box_height - lid_thickness * 2 - worker_thickness - 0.5
        ])
        {
            cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);
            translate([ 0, -worker_length / 2, 0 ])
            {
                ycyl(r = 6, h = 10, anchor = BOTTOM);
                translate([ 0, 0, 6 ])
                    cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3, edges = [ TOP + LEFT, TOP + RIGHT ]);
            }
        }

        // Black
        translate([
            worker_width, player_box_length - wall_thickness * 2 - worker_length / 2,
            player_box_height - lid_thickness * 2 - worker_thickness - 0.5
        ])
        {
            cuboid([ worker_width, worker_length, worker_thickness + 1 ], anchor = BOTTOM);
            translate([ 0, worker_length / 2, 0 ])
            {
                ycyl(r = 6, h = 10, anchor = BOTTOM);
                translate([ 0, 0, 6 ])
                    cuboid([ 12, 12, 6 ], anchor = BOTTOM, rounding = -3, edges = [ TOP + LEFT, TOP + RIGHT ]);
            }
        }

        // Doublers.
        translate([ worker_width * 2 + 4, 0,
                    player_box_height - lid_thickness * 2 - tile_thickness * 4 - 0.5 ]) for (j = [0:1:2])
        {
            translate([ j * (doubler_size + 3) + doubler_size / 2, doubler_size / 2, 0 ])
            {
                cuboid([ doubler_size, doubler_size, tile_thickness * 4 + 1 ], anchor = BOTTOM);
                translate([ 0, -doubler_size / 2, 0 ]) ycyl(r = 8, h = 5, anchor = BOTTOM);
            }
            translate([
                j * (doubler_size + 3) + doubler_size / 2, player_box_length - wall_thickness * 2 - doubler_size / 2, 0
            ])
            {
                cuboid([ doubler_size, doubler_size, tile_thickness * num_doubler_tokens * 4 + 1 ], anchor = BOTTOM);
                translate([ 0, doubler_size / 2, 0 ]) ycyl(r = 8, h = 5, anchor = BOTTOM);
            }
        }

        // Bonus tiles.
        translate([
            extra_score_track_length / 2, (player_box_length - wall_thickness * 2) / 2,
            player_box_height - lid_thickness * 2 - tile_thickness * 4 - 0.5
        ])
        {
            cuboid([ extra_score_track_length, extra_score_track_width, tile_thickness * 4 + 1 ], anchor = BOTTOM);
            translate([ -extra_score_track_length / 2, 0, 0 ])
            {
                xcyl(r = 7, h = 20, anchor = BOTTOM);
                translate([ 0, 0, 7 ]) cuboid([ 14, 14, tile_thickness * 4 - 7 ], anchor = BOTTOM, rounding = -3,
                                              edges = [ TOP + LEFT, TOP + RIGHT ]);
            }
        }
        translate([
            player_box_width - wall_thickness * 2 - extra_score_track_length / 2,
            (player_box_length - wall_thickness * 2) / 2,
            player_box_height - lid_thickness * 2 - tile_thickness * 4 - 0.5
        ])
        {

            cuboid([ extra_score_track_length, extra_score_track_width, tile_thickness * 4 + 1 ], anchor = BOTTOM);
            translate([ extra_score_track_length / 2, 0, 0 ])
            {
                xcyl(r = 7, h = 20, anchor = BOTTOM);
                translate([ 0, 0, 7 ]) cuboid([ 14, 14, tile_thickness * 4 - 7 ], anchor = BOTTOM, rounding = -3,
                                              edges = [ TOP + LEFT, TOP + RIGHT ]);
            }
        }
    }
    if (generate_lid)
    {
        translate([ 0, extra_tokens_box_length + 10, 0 ])
            CapBoxLidWithLabel(width = extra_tokens_box_width, length = extra_tokens_box_length,
                               height = extra_tokens_box_height, text_width = 70, text_height = 20, text_str = "Extra",
                               wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module MoneyBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = money_box_width, length = money_box_length, height = money_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        RoundedBoxAllSides(width = money_box_width - wall_thickness * 2, length = money_box_length - wall_thickness * 2,
                           height = money_box_height, radius = 6);
    }
    if (generate_lid)
    {
        translate([ 0, money_box_length + 10, 0 ]) CapBoxLidWithLabel(
            width = money_box_width, length = money_box_length, height = money_box_height, text_width = 70,
            text_height = 20, text_str = "Money", wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module TrainBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = train_box_width, length = train_box_length, height = train_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        for (i = [0:1:3])
        {
            translate([
                (train_tile_width + 2) * i + train_tile_width / 2 + 5, train_tile_length / 2,
                train_box_height - lid_thickness * 2 - tile_thickness * 4 - 0.5
            ]) TrainTile(height = tile_thickness * 4 + 1);
            translate([
                (train_tile_width + 2) * i + train_tile_width / 2 + 5,
                train_box_length - wall_thickness * 2 - train_tile_length / 2,
                train_box_height - lid_thickness * 2 - tile_thickness * 4 - 0.5
            ]) rotate([ 0, 0, 180 ]) TrainTile(height = tile_thickness * 4 + 1);
        }
        translate([
            (train_tile_width + 2) * 5 + 5, train_box_length - wall_thickness * 2 - train_tile_length / 2,
            train_box_height - lid_thickness * 2 - tile_thickness * 5 - 0.5
        ]) rotate([ 0, 0, 180 ]) TrainTile(height = tile_thickness * 5 + 1);
    }
    if (generate_lid)
    {
        translate([ 0, train_box_length + 10, 0 ]) CapBoxLidWithLabel(
            width = train_box_width, length = train_box_length, height = train_box_height, text_width = 70,
            text_height = 20, text_str = "Trains", wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module EngineerBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = engineer_box_width, length = engineer_box_length, height = engineer_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        translate(
            [ engineer_width / 2 + 4, 0,
              engineer_box_height - lid_thickness * 2 - tile_thickness * 3 - 0.5 ]) for (i = [0:1:4])
        {
            translate([ (engineer_width + 5) * i, engineer_length / 2, 0 ]) rotate([ 0, 0, 180 ])
                EngineerTile(height = tile_thickness * 3 + 1);
        }
    }
    if (generate_lid)
    {
        translate([ 0, engineer_box_length + 10, 0 ]) CapBoxLidWithLabel(
            width = engineer_box_width, length = engineer_box_length, height = engineer_box_height, text_width = 70,
            text_height = 20, text_str = "Engineers", wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module TrackBox(generate_lid = true) // `make` me
{
    MakeBoxWithCapLid(width = track_box_width, length = track_box_length, height = track_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness, floor_thickness = lid_thickness)
    {
        translate([ 0.5, 0.5, 0 ])
        {
            box_section_len = (track_box_width - wall_thickness * 2 - 5 - rail_white_width - 2) / 3;
            cube([ box_section_len, track_box_length - wall_thickness * 2 - 1, track_box_height ]);
            translate([ box_section_len + 2, 0, 0 ])
            {
                cube([ box_section_len, track_box_length - wall_thickness * 2 - 1, track_box_height ]);
                translate([ box_section_len + 2, 0, 0 ])
                {
                    cube([ box_section_len, track_box_length - wall_thickness * 2 - 1, track_box_height ]);
                    for (i = [0:1:3])
                    {
                        translate([
                            box_section_len + 2 + rail_white_width / 2,
                            rail_white_length / 2 + (rail_white_length + 5) * i + 4,
                            track_box_height - lid_thickness * 2 - rail_white_thickness - 0.5
                        ])
                        {
                            rotate([0,0,90])
                            WhiteTrack(height = rail_white_thickness + 1);
                            translate([ -rail_white_length / 2, 0, rail_white_thickness / 2 ])
                                sphere(r = 7, anchor = BOTTOM);
                        }
                    }
                }
            }
        }
    }
    if (generate_lid)
    {
        translate([ 0, track_box_length + 10, 0 ]) CapBoxLidWithLabel(
            width = track_box_width, length = track_box_length, height = track_box_height, text_width = 70,
            text_height = 20, text_str = "Tracks", wall_thickness = wall_thickness, lid_thickness = lid_thickness);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        PlayerBox(generate_lid = false);
        translate([ player_box_width, 0, 0 ]) PlayerBox(generate_lid = false);
        translate([ 0, 0, player_box_height ]) PlayerBox(generate_lid = false);
        translate([ player_box_width, 0, player_box_height ]) PlayerBox(generate_lid = false);
        translate([ 0, 0, player_box_height * 2 ]) ExtraTokensBox(generate_lid = false);
        translate([ player_box_width, 0, player_box_height * 2 ]) MoneyBox(generate_lid = false);
        translate([ 0, player_box_length, 0 ]) TrainBox(generate_lid = false);
        translate([ 0, player_box_length, player_box_height ]) EngineerBox(generate_lid = false);
        translate([ 0, player_box_length + engineer_box_length, 0 ]) TrackBox(generate_lid = false);
    }
}

module PrintLayout()
{
    PlayerBox(generate_lid = true);
    translate([ player_box_width + 10, 0, 0 ])
    {
        ExtraTokensBox(generate_lid = false);
        translate([ extra_tokens_box_width + 10, 0, 0 ])
        {
            MoneyBox(generate_lid = false);
            translate([ money_box_width + 10, 0, 0 ])
            {
                TrainBox(generate_lid = false);
                translate([ train_box_width + 10, 0, 0 ])
                {
                    EngineerBox(generate_lid = false);
                    translate([ engineer_box_width + 10, 0, 0 ])
                    {
                        TrackBox(generate_lid = false);
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
        cuboid([ 100, 100, 6 ], anchor = BOTTOM);
        translate([ 0, 0, 1 ])
        {
            WhiteTrack(10);
            translate([ rail_white_width / 2 + engineer_width / 2 + 2, 0, 0 ]) EngineerTile(height = 10);
            translate([ -rail_white_width / 2 - train_tile_width / 2 - 2, 10, 0 ]) TrainTile(height = 10);
            translate([ -2, rail_white_length / 2 + pawn_length / 2 + 2, 0 ]) PawnOutline(height = 10);
            translate([ -2, rail_white_length / 2 + pawn_length + 2 + 11, 0 ])
                RegularPolygon(width = industry_hex, height = 101, shape_edges = 6);

            translate([ -20, -rail_white_length / 2 - kiev_medal_width / 2 - 2 - 11, 0 ])
            {
                cuboid([ kiev_medal_length, kiev_medal_width, tile_thickness * 2 + 3 ], anchor = BOTTOM);
                translate([ kiev_medal_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
                translate([ 0, 0, 2.2 ])
                {
                    cuboid([ bonus_train_tile_length, bonus_train_tile_width, tile_thickness * 2 + 4 ],
                           anchor = BOTTOM);
                    translate([ bonus_train_tile_length / 2, 0, 0 ]) sphere(r = 10, anchor = BOTTOM);
                }
            }
        }
    }
}

if (FROM_MAKE != 1)
{
    BoxLayout();
}