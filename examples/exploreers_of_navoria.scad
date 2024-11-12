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

box_width = 211;
box_length = 268;
box_height = 68;
board_thickness = 12;
lid_thickness = 2;
wall_thickness = 3;

player_layout_thickness = 2;
player_layout_num = 4;
player_layout_width = 147;
player_layout_length = 266;

// per player
king_marker_num = 1;
trading_post_maker_num = 9;
favour_token_num = 4;
turn_order_token = 1;
explorer_token = 3;

// total
num_favour_tiles = 10;
num_cards = 60;
num_ref_cards = 4;

favour_tile_width = 72;
favour_tile_length = 60.5;
favour_tile_side_bit = 18.5;
favour_tile_edge_slope_in = 5;
favour_tile_edge_slope_down = 3;
favour_tile_top_dip = 8.5;

marker_thickness = 10;

bird_diameter = 20.5;
bird_length = 25;
bird_base = 7;
bird_top_base = 11;
bird_lump = 3.75;
bird_beak_diameter = 21.5;
bird_diameter_base = 6;
bird_lump_length = 23;
bird_lump_second_length = 21.75;

trading_post_mushroom_width = 17;
trading_post_mushroom_height = 16;
trading_post_mushroom_inset_side = 2;
trading_post_mushroom_inset_up = 3;

trading_post_triangle_width = 17;
trading_post_triangle_height = 16;
trading_post_triangle_inset_side = 2;
trading_post_triangle_inset_up = 3;

trading_post_barn_width = 17;
trading_post_barn_height = 16;
trading_post_barn_inset_side = 1.5;
trading_post_barn_inset_up = 3;
trading_post_barn_top_width = 10;

trading_post_castle_width = 17;
trading_post_castle_height = 16;
trading_post_castle_base_width = 12;
trading_post_castle_top_height = 7;
trading_post_castle_gap = 2;
trading_post_castle_inset_up = 2;
trading_post_castle_crenelation_height = 4;

king_marker = 20.5;
favour_marker_width = 23.5;
favour_marker_length = 26.5;
favour_base_width = 16;

explorer_marker_height = 21.5;
explorer_base_width = 17.5;
explorer_hat_width = 18.5;
explorer_hat_green_top_left = 17.75;
explorer_hat_green_top_right = 14.75;
explorer_hat_yellow_top = 18.5;
explorer_hat_yellow_bottom = 13.3;
explorer_hat_yellow_top_flat = 6;
explorer_hat_yellow_lower_flat = 10;
explorer_marker_top_diameter = 12.5;
explorer_hat_black_width = 9.75;
explorer_hat_black_height = 7;
explorer_hat_black_top_height = 15.5;
explorer_hat_black_bottom_height = 11.5;
explorer_hat_purple_top_height = 18.25;
explorer_hat_purple_bottom_height = 13.25;
explorer_hat_purple_bottom_width = 10;
explorer_hat_purple_top_width = 7;

player_box_height = (box_height - board_thickness - 1) / 4; // marker_thickness + lid_thickness * 2 + 0.5;
player_box_length = (box_length - 2) / 2;
player_box_width = box_width - player_layout_width - 2;

favour_box_width = box_width - player_box_width - 1.5;
favour_box_length = favour_tile_width + wall_thickness * 2;
favour_box_height = lid_thickness * 2 + player_layout_thickness * num_favour_tiles / 2 + 0.5;

stuff_box_height = box_height - board_thickness - favour_box_height - 1 - player_layout_thickness * player_layout_num;
stuff_box_width = favour_box_width / 3;
stuff_box_length = favour_box_length;

bag_box_length = box_length - stuff_box_length - 2;
bag_box_width = box_width - player_box_width - 2;
bag_box_height =
    box_height - board_thickness - player_layout_thickness - 1 - player_layout_thickness * player_layout_num;
echo(player_box_height);

module FavourTile(height)
{
    module OneBar(reverse)
    {
        width = favour_tile_width;
        mirror([ reverse, 0, 0 ]) hull()
        {
            translate([ width / 2 - 2 - favour_tile_edge_slope_in, favour_tile_length / 2 - 2, 0 ])
                cyl(d = 4, h = height, $fn = 32);
            translate([ width / 2 - 2, favour_tile_length / 2 - 2 - favour_tile_edge_slope_down, 0 ])
                cyl(d = 4, h = height, $fn = 32);
            translate([ width / 2 - favour_tile_side_bit + 3, favour_tile_length / 2 - 3, 0 ])
                cyl(d = 6, h = height, $fn = 32);
            translate([ width / 2 - 2, -favour_tile_length / 2 + 2 + favour_tile_edge_slope_down, 0 ])
                cyl(d = 4, h = height, $fn = 32);
            translate([ width / 2 - 2 - favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0 ])
                cyl(d = 4, h = height, $fn = 32);
            translate([ width / 2 - favour_tile_side_bit + 2, -favour_tile_length / 2 + 2, 0 ])
                cyl(d = 4, h = height, $fn = 32);
        }
    }
    translate([ 0, 0, height / 2 ])
    {
        difference()
        {
            union()
            {
                OneBar(0);
                OneBar(1);
                hull()
                {
                    translate([
                        favour_tile_width / 2 - 2 - favour_tile_edge_slope_in,
                        favour_tile_length / 2 - 2 - favour_tile_top_dip + 2, 0
                    ]) cyl(d = 4, h = height, $fn = 32);
                    translate([
                        -favour_tile_width / 2 + 2 + favour_tile_edge_slope_in,
                        favour_tile_length / 2 - 2 - favour_tile_top_dip + 2, 0
                    ]) cyl(d = 4, h = height, $fn = 32);
                    translate([ favour_tile_width / 2 - 2 - favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0 ])
                        cyl(d = 4, h = height, $fn = 32);
                    translate(
                        [ -favour_tile_width / 2 + 2 + favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0 ])
                        cyl(d = 4, h = height, $fn = 32);
                }
            }
            translate([ 0, (favour_tile_length - favour_tile_top_dip) / 2, 0 ])
                cuboid([ favour_tile_width - favour_tile_side_bit * 2, favour_tile_top_dip, height + 1 ], rounding = 2,
                       edges = [ FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT ], $fn = 32);
        }
    }
}

module BirdTurnOrder(height)
{
    translate([ (bird_length - bird_diameter) / 2, 0, 0 ])
    {
        // Main bird
        extra = bird_length - bird_diameter;
        cyl(h = height, d = bird_diameter, anchor = BOTTOM);
        // base bit.
        translate([ -bird_diameter / 2 + bird_diameter_base - extra, 0, height / 2 ]) rotate([ 0, -90, 0 ])
            prismoid(size1 = [ height, bird_top_base ], size2 = [ height, bird_base ], h = bird_diameter_base);
        // beak.
        hull()
        {
            translate([ 0, bird_diameter / 2 + bird_beak_diameter - bird_diameter - 0.5, 0 ])
                cyl(h = height, r = 1, $fn = 16, anchor = BOTTOM);
            translate([ 0, bird_diameter / 2 - 0.45, 0 ]) cuboid([ 4, 0.5, height ], anchor = BOTTOM);
        }

        // top bit
        rotate([ 0, 0, -40 ]) union()
        {
            top_offset = bird_lump_length - bird_diameter;
            hull()
            {
                translate([ bird_diameter / 2 + top_offset - bird_lump / 2, 0, 0 ])
                    cyl(d = bird_lump, h = height, $fn = 32, anchor = BOTTOM);

                translate([ bird_diameter / 2, 0, 0 ]) cuboid([ bird_lump / 2, bird_lump, height ], anchor = BOTTOM);
            }
            hull()
            {
                rotate([ 0, 0, -14 ]) translate([ bird_diameter / 2, 0, 0 ])
                    cyl(d = (bird_lump_second_length - bird_diameter) * 2, h = height, $fn = 16, anchor = BOTTOM);
                rotate([ 0, 0, -24 ]) translate([ bird_diameter / 2 - 3, 0, 0 ])
                    cuboid([ bird_lump / 2, bird_lump, height ], anchor = BOTTOM);
            }
        }
    }
}

module TradingPostYellow(height)
{
    translate(
        [ 0, trading_post_mushroom_height - trading_post_mushroom_inset_up - trading_post_mushroom_height / 2, 0 ])
    {
        difference()
        {
            translate([ 0, -trading_post_mushroom_height + trading_post_mushroom_inset_up, 0 ])
                linear_extrude(height = height)
                    ellipse(d = [ trading_post_mushroom_width, trading_post_mushroom_height * 2 ], anchor = FRONT);
            translate([ 0, trading_post_mushroom_height + 0.5, -0.5 ]) cuboid(
                [ trading_post_mushroom_width + 1, trading_post_mushroom_height * 2 + 1, height + 1 ], anchor = BOTTOM);
        }
        translate([ 0, trading_post_mushroom_inset_up, 0 ]) cuboid(
            [
                trading_post_mushroom_width - trading_post_mushroom_inset_side * 2,
                trading_post_mushroom_inset_up + 0.5,
                height
            ],
            anchor = BOTTOM + BACK);
    }
}

module TradingPostPurple(height)
{
    translate(
        [ 0, trading_post_triangle_height - trading_post_triangle_inset_up - trading_post_triangle_height / 2, 0 ])
    {
        hull()
        {
            translate([ trading_post_triangle_width / 2 - 0.5, -0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
            translate([ -trading_post_triangle_width / 2 + 0.5, -0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
            translate([ 0, -trading_post_triangle_height + trading_post_triangle_inset_up + 0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
        }
        translate([ 0, trading_post_triangle_inset_up, 0 ]) cuboid(
            [
                trading_post_triangle_width - trading_post_triangle_inset_side * 2,
                trading_post_triangle_inset_up + 0.5,
                height
            ],
            anchor = BOTTOM + BACK);
    }
}

module TradingPostBlack(height)
{
    translate([ 0, trading_post_barn_height - trading_post_barn_inset_up - trading_post_barn_height / 2, 0 ])
    {
        hull()
        {
            translate([ trading_post_barn_width / 2 - 0.5, -0.5, 0 ]) cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
            translate([ -trading_post_barn_width / 2 + 0.5, -0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
            translate(
                [ trading_post_barn_top_width / 2, -trading_post_barn_height + trading_post_barn_inset_up + 0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
            translate(
                [ -trading_post_barn_top_width / 2, -trading_post_barn_height + trading_post_barn_inset_up + 0.5, 0 ])
                cyl(d = 1, h = height, $fn = 16, anchor = BOTTOM);
        }
        translate([ 0, trading_post_barn_inset_up, 0 ]) cuboid(
            [ trading_post_barn_width - trading_post_barn_inset_side * 2, trading_post_barn_inset_up + 0.5, height ],
            anchor = BOTTOM + BACK);
    }
}

module TradingPostGreen(height)
{
    translate([ 0, -trading_post_castle_height / 2, 0 ])
    {
        translate([ 0, 0, 0 ]) cuboid([ trading_post_castle_base_width, trading_post_castle_inset_up + 0.5, height ],
                                      anchor = BOTTOM + FRONT);
        difference()
        {
            // middle bit
            translate([ 0, trading_post_castle_height, 0 ])
                cuboid([ trading_post_castle_width, trading_post_castle_top_height, height ], anchor = BOTTOM + BACK,
                       rounding = 0.5, edges = [ BACK + LEFT, BACK + RIGHT ], $fn = 16);
            // bottom rounding
            translate([
                -(trading_post_castle_width - trading_post_castle_gap * 2) / 3.5, trading_post_castle_height + 1, -0.5
            ]) cuboid([ trading_post_castle_gap, trading_post_castle_crenelation_height + 1, height + 1 ],
                      anchor = BOTTOM + BACK, rounding = 0.5, edges = [ FRONT + LEFT, FRONT + RIGHT ], $fn = 16);
            translate([
                (trading_post_castle_width - trading_post_castle_gap * 2) / 3.5, trading_post_castle_height + 1, -0.5
            ]) cuboid([ trading_post_castle_gap, trading_post_castle_crenelation_height + 1, height + 1 ],
                      anchor = BOTTOM + BACK, rounding = 0.5, edges = [ FRONT + LEFT, FRONT + RIGHT ], $fn = 16);
        }

        hull()
        {
            translate(
                [ trading_post_castle_width / 2 - 0.5, trading_post_castle_height - trading_post_castle_top_height, 0 ])
                cyl(d = 1, h = height, anchor = BOTTOM, $fn = 16);
            translate([
                -trading_post_castle_width / 2 + 0.5, trading_post_castle_height - trading_post_castle_top_height, 0
            ]) cyl(d = 1, h = height, anchor = BOTTOM, $fn = 16);
            translate([ trading_post_castle_base_width / 2 - 0.5, trading_post_castle_inset_up, 0 ])
                cyl(d = 1, h = height, anchor = BOTTOM, $fn = 16);
            translate([ -trading_post_castle_base_width / 2 + 0.5, trading_post_castle_inset_up, 0 ])
                cyl(d = 1, h = height, anchor = BOTTOM, $fn = 16);
        }
    }
}

module FavourMarker(height)
{
    translate([ 0, -favour_marker_length / 2, 0 ])
    {
        translate([ 0, favour_marker_width / 2, 0 ])
            cyl(d = favour_marker_width, h = height, anchor = BOTTOM, $fn = 64);

        hull()
        {
            translate([ favour_base_width / 2, favour_marker_length, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ favour_base_width / 2, favour_marker_width / 2, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ 0, favour_marker_width, 0 ]) cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
        }

        hull()
        {
            translate([ -favour_base_width / 2, favour_marker_length, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ -favour_base_width / 2, favour_marker_width / 2, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ 0, favour_marker_width, 0 ]) cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
        }
    }
}

module ExplorerMarkerGreen(height)
{
    translate([ 0, -explorer_marker_height / 2, 0 ])
    {
        difference()
        {
            union()
            {
                hull()
                {
                    translate([ 0, explorer_marker_height, 0 ])
                        cyl(d = explorer_marker_top_diameter, h = height, anchor = BOTTOM + BACK, $fn = 64);
                    translate([ explorer_base_width / 2 - 0.5, 0, 0 ])
                        cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
                    translate([ -explorer_base_width / 2 + 0.5, 0, 0 ])
                        cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
                }
                hull()
                {
                    translate([ explorer_hat_width / 2 - 2.5, explorer_hat_green_top_left, 0 ])
                        cyl(d = 5, anchor = BOTTOM + BACK, h = height, $fn = 32);
                    translate([ -explorer_hat_width / 2 + 2.5, explorer_hat_green_top_right, 0 ])
                        cyl(d = 5, anchor = BOTTOM + BACK, h = height, $fn = 32);
                }
                translate([ explorer_marker_top_diameter / 2 + 0.7, explorer_hat_green_top_left + 2.9, 0 ])
                {
                    difference()
                    {
                        translate([ -0.35, -1.5, 0 ]) cuboid([ 1.5, 1.6, height + 1 ], anchor = BOTTOM + BACK);
                        cyl(d = 3, h = height + 1, anchor = BOTTOM + BACK, $fn = 16);
                    }
                }
                translate([ -explorer_marker_top_diameter / 2 - 1.8, explorer_hat_green_top_right + 3.7, 0 ])
                {
                    difference()
                    {
                        translate([ 1, -1.6, 0 ]) cuboid([ 2, 2.1, height + 1 ], anchor = BOTTOM + BACK);
                        cyl(d = 4, h = height + 1, anchor = BOTTOM + BACK, $fn = 16);
                    }
                }
            }
        }
    }
}

module ExplorerMarkerYellow(height)
{
    translate([ 0, -explorer_marker_height / 2, 0 ])
    {
        difference()
        {
            hull()
            {
                translate([ 0, explorer_marker_height, 0 ])
                    cyl(d = explorer_marker_top_diameter + 2, h = height, anchor = BOTTOM + BACK, $fn = 64);
                translate([ explorer_base_width / 2 - 0.5, 0, 0 ])
                    cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
                translate([ -explorer_base_width / 2 + 0.5, 0, 0 ])
                    cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
            }
            translate([ 0, explorer_hat_yellow_bottom, -0.5 ])
                cuboid([ explorer_hat_width, explorer_marker_height, height + 1 ], anchor = BOTTOM + FRONT);
        }
        // Arms section
        hull()
        {
            // Left side
            translate([ explorer_hat_width / 2 - 1.5, explorer_hat_yellow_bottom + 1.5, 0 ])
                cyl(d = 3, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_width / 2 - 1, explorer_hat_yellow_bottom + 2.5, 0 ])
                cyl(d = 2, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_yellow_lower_flat / 2 - 0.2, explorer_hat_yellow_top, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_yellow_lower_flat / 2 - 1.5, explorer_hat_yellow_bottom - 1, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([
                (explorer_hat_yellow_lower_flat + explorer_hat_width) / 4 - 0.5,
                (explorer_hat_yellow_top + explorer_hat_yellow_bottom) / 2 + 0.8, 0
            ]) cyl(d = 3.75, anchor = BOTTOM + BACK, h = height, $fn = 32);

            // Right side
            translate([ -explorer_hat_width / 2 + 1.5, explorer_hat_yellow_bottom + 1.5, 0 ])
                cyl(d = 3, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_width / 2 + 1, explorer_hat_yellow_bottom + 2.5, 0 ])
                cyl(d = 2, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_yellow_lower_flat / 2 + 0.2, explorer_hat_yellow_top, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_yellow_lower_flat / 2 + 1.5, explorer_hat_yellow_bottom - 1, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([
                -(explorer_hat_yellow_lower_flat + explorer_hat_width) / 4 + 0.5,
                (explorer_hat_yellow_top + explorer_hat_yellow_bottom) / 2 + 0.8, 0
            ]) cyl(d = 3.75, anchor = BOTTOM + BACK, h = height, $fn = 32);
        }
        // Hat section.
        hull()
        {
            translate([ explorer_hat_yellow_lower_flat / 2 - 0.5, explorer_hat_yellow_top, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_yellow_lower_flat / 2 + 0.5, explorer_hat_yellow_top, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);

            translate([ -explorer_hat_yellow_top_flat / 2 + 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_yellow_top_flat / 2 - 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
        }
    }
}

module ExplorerMarkerBlack(height)
{
    translate([ 0, -explorer_marker_height / 2, 0 ])
    {
        difference()
        {
            hull()
            {
                translate([ 0, explorer_marker_height, 0 ])
                    cyl(d = explorer_marker_top_diameter + 2, h = height, anchor = BOTTOM + BACK, $fn = 64);
                translate([ explorer_base_width / 2 - 0.25, 0, 0 ])
                    cyl(d = 1.5, h = height, anchor = BOTTOM + FRONT, $fn = 32);
                translate([ -explorer_base_width / 2 + 0.25, 0, 0 ])
                    cyl(d = 1.5, h = height, anchor = BOTTOM + FRONT, $fn = 32);
            }
            translate([ 0, explorer_hat_black_top_height, -0.5 ]) cuboid(
                [ explorer_hat_black_width + 10, explorer_hat_black_top_height, height + 1 ], anchor = BOTTOM + FRONT);
        }

        hull()
        {
            translate([ explorer_hat_black_width / 2 - 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ -explorer_hat_black_width / 2 + 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ explorer_hat_black_width / 2 - 0.75, explorer_hat_black_top_height, 0 ])
                cyl(d = 1.5, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ -explorer_hat_black_width / 2 + 0.75, explorer_hat_black_top_height, 0 ])
                cyl(d = 1.5, anchor = BOTTOM + BACK, h = height, $fn = 16);
        }

        hull()
        {
            translate([ explorer_hat_width / 2 - 0.5, explorer_hat_black_top_height, 0 ])
                cyl(d = 2, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_black_width / 2 - 0.5, explorer_hat_black_bottom_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_width / 2 + 0.5, explorer_hat_black_top_height, 0 ])
                cyl(d = 2, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_black_width / 2 + 0.5, explorer_hat_black_bottom_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
        }
    }
}

module ExplorerMarkerPurple(height)
{
    translate([ 0, -explorer_marker_height / 2, 0 ])
    {
        difference()
        {
            hull()
            {
                translate([ 0, explorer_marker_height, 0 ])
                    cyl(d = explorer_marker_top_diameter, h = height, anchor = BOTTOM + BACK, $fn = 64);
                translate([ explorer_base_width / 2 - 0.5, 0, 0 ])
                    cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
                translate([ -explorer_base_width / 2 + 0.5, 0, 0 ])
                    cyl(d = 1, h = height, anchor = BOTTOM + FRONT, $fn = 32);
            }
        }

        hull()
        {
            translate([ explorer_hat_purple_top_width / 2 - 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ -explorer_hat_purple_top_width / 2 + 0.5, explorer_marker_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ explorer_hat_purple_bottom_width / 2 - 0.5, explorer_hat_purple_top_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
            translate([ -explorer_hat_purple_bottom_width / 2 + 0.5, explorer_hat_purple_top_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 16);
        }

        hull()
        {
            translate([ explorer_hat_width / 2 - 0.5, explorer_hat_purple_top_height, 0 ])
                cyl(d = 2.5, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ explorer_hat_purple_bottom_width / 2 - 0.5, explorer_hat_purple_bottom_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_width / 2 + 0.5, explorer_hat_purple_top_height, 0 ])
                cyl(d = 2.5, anchor = BOTTOM + BACK, h = height, $fn = 32);
            translate([ -explorer_hat_purple_bottom_width / 2 + 0.5, explorer_hat_purple_bottom_height, 0 ])
                cyl(d = 1, anchor = BOTTOM + BACK, h = height, $fn = 32);
        }
    }
}

module PlayerBoxOneBase(generate_lid = true)
{
    MakeBoxWithCapLid(width = player_box_width, length = player_box_length, height = player_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        inner_box_width = player_box_width - wall_thickness;
        inner_box_length = player_box_length - wall_thickness;
        inner_box_height = player_box_height - lid_thickness * 2;
        translate([ wall_thickness / 2, -wall_thickness - 1, inner_box_height - wall_thickness ]) RoundedBoxAllSides(
            width = inner_box_width - wall_thickness * 2, length = inner_box_length + wall_thickness * 2 + 2,
            height = player_box_height, radius = wall_thickness);
        marker_depth = player_box_height - lid_thickness * 2 - marker_thickness - 0.5;
        // king marker
        translate([ (inner_box_width - king_marker) / 2, 0, marker_depth ])
        {
            cuboid([ king_marker, king_marker, marker_thickness + 1 ], anchor = BOTTOM + LEFT + FRONT);
            translate([ king_marker, king_marker / 2, marker_thickness / 2 - 1 ]) sphere(r = 8, anchor = BOTTOM);
            translate([ 0, king_marker / 2, marker_thickness / 2 - 1 ]) sphere(r = 8, anchor = BOTTOM);
        }

        // bird marker
        translate([
            bird_length / 2 + (inner_box_width - bird_length) / 2, king_marker + 1 + bird_diameter / 2,
            marker_depth
        ])
        {
            BirdTurnOrder(marker_thickness + 1);
            translate([ bird_length / 2, 0, marker_thickness / 2 - 1 ]) sphere(r = 8, anchor = BOTTOM);
            translate([ -bird_length / 2, 0, marker_thickness / 2 - 1 ]) sphere(r = 8, anchor = BOTTOM);
        }

        width = trading_post_castle_height * 2 + 18;
        translate([
            (inner_box_width - width) / 2 + trading_post_castle_height / 2,
            bird_diameter + king_marker + trading_post_castle_width / 2,
            marker_depth
        ])
        {
            for (i = [0:1:3])
            {
                translate([ 2, (trading_post_castle_width + 0.75) * i, 0 ])
                {
                    children(0);
                    translate([ trading_post_castle_height / 2, 0, marker_thickness / 2 - 1 ])
                        sphere(r = 8, anchor = BOTTOM);
                }
            }
            for (i = [0:1:3])
            {
                translate([ trading_post_castle_height + 13, (trading_post_castle_width + 0.75) * i, 0 ])
                {
                    children(1);
                    translate([ -trading_post_castle_height / 2, 0 * i, marker_thickness / 2 - 1 ])
                        sphere(r = 8, anchor = BOTTOM);
                }
            }
        }
        translate([ inner_box_width / 2 - 1.5, inner_box_length - trading_post_castle_width / 2 - wall_thickness, 0 ])
        {
            rotate([ 0, 0, 90 ]) children(1);
            translate([ 0, -trading_post_castle_height / 2, marker_thickness / 2 ]) sphere(r = 8, anchor = BOTTOM);
        }
    }
    if (generate_lid)
    {
        translate([ player_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = player_box_width, length = player_box_length, height = player_box_height,
                               wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                               text_height = 15, text_str = "Player", label_rotated = true);
        }
    }
}

module PlayerBoxGreenOne(generate_lid = true)
{
    PlayerBoxOneBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, 90 ]) TradingPostGreen(marker_thickness + 1);
        rotate([ 0, 0, -90 ]) TradingPostGreen(marker_thickness + 1);
    }
}

module PlayerBoxYellowOne(generate_lid = true)
{
    PlayerBoxOneBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, -90 ]) TradingPostYellow(marker_thickness + 1);
        rotate([ 0, 0, 90 ]) TradingPostYellow(marker_thickness + 1);
    }
}

module PlayerBoxPurpleOne(generate_lid = true)
{
    PlayerBoxOneBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, -90 ]) TradingPostPurple(marker_thickness + 1);
        rotate([ 0, 0, 90 ]) TradingPostPurple(marker_thickness + 1);
    }
}

module PlayerBoxBlackOne(generate_lid = true)
{
    PlayerBoxOneBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, -90 ]) TradingPostBlack(marker_thickness + 1);
        rotate([ 0, 0, 90 ]) TradingPostBlack(marker_thickness + 1);
    }
}

module PlayerBoxTwoBase(generate_lid = true)
{
    MakeBoxWithCapLid(width = player_box_width, length = player_box_length, height = player_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        marker_depth = player_box_height - lid_thickness * 2 - marker_thickness - 0.5;
        inner_box_height = player_box_height - lid_thickness * 2;
        inner_box_length = player_box_length - wall_thickness * 2;
        inner_box_width = player_box_width - wall_thickness * 2;
        translate([ wall_thickness / 2, -wall_thickness - 1, inner_box_height - wall_thickness ]) RoundedBoxAllSides(
            width = inner_box_width - wall_thickness, length = inner_box_length + wall_thickness * 2 + 2,
            height = player_box_height, radius = wall_thickness);
        translate([ 0, 0, marker_depth ])
        {
            // favour.
            translate([ (inner_box_width - favour_marker_width * 2 - 1.5) / 2, favour_marker_length / 2 + 1, 0 ])
            {
                for (i = [0:1:1])
                {
                    translate([ favour_marker_width / 2, (favour_marker_length + 7) * i, 0 ])
                    {
                        rotate([ 0, 0, 180 ]) FavourMarker(height = marker_thickness + 1);
                        translate([ 0, favour_marker_length / 2, marker_thickness / 2 ]) sphere(r = 9, anchor = BOTTOM);
                        translate([ 0, -favour_marker_length / 2 + 3, marker_thickness / 2 ])
                            sphere(r = 9, anchor = BOTTOM);
                    }
                    translate(
                        [ favour_marker_width / 2 + favour_marker_width + 1.5, (favour_marker_length + 7) * i, 0 ])
                    {
                        rotate([ 0, 0, 180 ]) FavourMarker(height = marker_thickness + 1);
                        translate([ 0, favour_marker_length / 2, marker_thickness / 2 ]) sphere(r = 9, anchor = BOTTOM);
                        translate([ 0, -favour_marker_length / 2 + 2, marker_thickness / 2 ])
                            sphere(r = 9, anchor = BOTTOM);
                    }
                }
            }
            // explorers.
            translate([
                (inner_box_width - explorer_marker_height) / 2,
                (favour_marker_length + 5.5) * 2 + explorer_hat_width / 2 + 5, 0
            ])
            {
                for (i = [0:1:2])
                {
                    translate([ explorer_marker_height / 2, (explorer_base_width + 2) * i, 0 ])
                    {
                        children(0);
                        translate([ explorer_marker_height / 2, 0, marker_thickness / 2 ])
                            sphere(r = 8, anchor = BOTTOM);
                        translate([ -explorer_marker_height / 2, 0, marker_thickness / 2 ])
                            sphere(r = 8, anchor = BOTTOM);
                    }
                }
            }
        }
    }
    if (generate_lid)
    {
        translate([ player_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = player_box_width, length = player_box_length, height = player_box_height,
                               wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                               text_height = 15, text_str = "Player", label_rotated = true);
        }
    }
}

module PlayerBoxGreenTwo(generate_lid = true)
{
    PlayerBoxTwoBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, 90 ]) ExplorerMarkerGreen(marker_thickness + 1);
        rotate([ 0, 0, -90 ]) ExplorerMarkerGreen(marker_thickness + 1);
    }
}

module PlayerBoxYellowTwo(generate_lid = true)
{
    PlayerBoxTwoBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, 90 ]) ExplorerMarkerYellow(marker_thickness + 1);
        rotate([ 0, 0, -90 ]) ExplorerMarkerYellow(marker_thickness + 1);
    }
}

module PlayerBoxPurpleTwo(generate_lid = true)
{
    PlayerBoxTwoBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, 90 ]) ExplorerMarkerPurple(marker_thickness + 1);
        rotate([ 0, 0, -90 ]) ExplorerMarkerPurple(marker_thickness + 1);
    }
}

module PlayerBoxBlackTwo(generate_lid = true)
{
    PlayerBoxTwoBase(generate_lid = generate_lid)
    {
        rotate([ 0, 0, 90 ]) ExplorerMarkerBlack(marker_thickness + 1);
        rotate([ 0, 0, -90 ]) ExplorerMarkerBlack(marker_thickness + 1);
    }
}

module FavourBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = favour_box_width, length = favour_box_length, height = favour_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        translate([ favour_tile_length / 2, favour_tile_width / 2, 0 ])
        {
            rotate([ 0, 0, 270 ]) FavourTile(height = num_favour_tiles / 2 * player_layout_thickness + 1);
            translate([ favour_tile_length / 2 - favour_tile_top_dip, 0, 0 ])
                cyl(r = 11, anchor = BOTTOM, h = favour_box_height * 2, rounding = 9.5);
        }
        translate([ favour_box_width - wall_thickness * 2 - favour_tile_length / 2, favour_tile_width / 2, 0 ])
        {
            rotate([ 0, 0, 90 ]) FavourTile(height = num_favour_tiles / 2 * player_layout_thickness + 1);
            translate([ -favour_tile_length / 2 + favour_tile_top_dip, 0, 0 ])
                cyl(r = 11, anchor = BOTTOM, h = favour_box_height * 2, rounding = 9.5);
        }
    }
    if (generate_lid)
    {
        translate([ favour_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = favour_box_width, length = favour_box_length, height = favour_box_height,
                               wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                               text_height = 15, text_str = "Favours", label_rotated = true);
        }
    }
}

module StuffBox(generate_lid = true)
{
    MakeBoxWithCapLid(width = stuff_box_width, length = stuff_box_length, height = stuff_box_height,
                      wall_thickness = wall_thickness, lid_thickness = lid_thickness)
    {
        RoundedBoxAllSides(width = stuff_box_width - wall_thickness * 2, length = stuff_box_length - wall_thickness * 2,
                           height = stuff_box_height, radius = 10);
    }
    if (generate_lid)
    {
        translate([ stuff_box_width + 10, 0, 0 ])
        {
            CapBoxLidWithLabel(width = stuff_box_width, length = stuff_box_length, height = stuff_box_height,
                               wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                               text_height = 15, text_str = "Swords", label_rotated = true);
            translate([ stuff_box_width + 10, 0, 0 ])
            {
                CapBoxLidWithLabel(width = stuff_box_width, length = stuff_box_length, height = stuff_box_height,
                                   wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                                   text_height = 15, text_str = "Apples", label_rotated = true);
                translate([ stuff_box_width + 10, 0, 0 ])
                {
                    CapBoxLidWithLabel(width = stuff_box_width, length = stuff_box_length, height = stuff_box_height,
                                       wall_thickness = wall_thickness, lid_thickness = lid_thickness, text_width = 50,
                                       text_height = 15, text_str = "Crystals", label_rotated = true);
                }
            }
        }
    }
}

module BagBox()
{
    translate([ bag_box_width / 2, bag_box_length / 2, 0 ]) difference()
    {
        cuboid([ bag_box_width, bag_box_length, bag_box_height ], rounding = 2, anchor = BOTTOM);
        translate([ 0, 0, lid_thickness ])
            cuboid([ bag_box_width - wall_thickness * 2, bag_box_length - wall_thickness * 2, bag_box_height ],
                   anchor = BOTTOM);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        PlayerBoxGreenOne(generate_lid = false);
        translate([ 0, 0, player_box_height ]) PlayerBoxYellowOne(generate_lid = false);
        translate([ 0, 0, player_box_height * 2 ]) PlayerBoxPurpleOne(generate_lid = false);
        translate([ 0, 0, player_box_height * 3 ]) PlayerBoxBlackOne(generate_lid = false);
        translate([ 0, player_box_length, 0 ]) PlayerBoxGreenTwo(generate_lid = false);
        translate([ 0, player_box_length, player_box_height ]) PlayerBoxYellowTwo(generate_lid = false);
        translate([ 0, player_box_length, player_box_height * 2 ]) PlayerBoxPurpleTwo(generate_lid = false);
        translate([ 0, player_box_length, player_box_height * 3 ]) PlayerBoxBlackTwo(generate_lid = false);
        translate([ player_box_width, 0, 0 ]) FavourBox(generate_lid = false);
        translate([ player_box_width, 0, favour_box_height ]) StuffBox(generate_lid = false);
        translate([ player_box_width + stuff_box_width, 0, favour_box_height ]) StuffBox(generate_lid = false);
        translate([ player_box_width + stuff_box_width * 2, 0, favour_box_height ]) StuffBox(generate_lid = false);
        translate([ player_box_width, favour_box_length, 0 ]) BagBox();
    }
    translate([ box_width - player_layout_width, 0, box_height - player_layout_thickness * player_layout_num ])
        cube([ player_layout_width, box_length, player_layout_thickness * player_layout_num ]);
}

module PrintLayout()
{
    PlayerBoxGreenOne();
    translate([ 0, player_box_length + 10, 0 ])
    {
        PlayerBoxYellowOne();
        translate([ 0, player_box_length + 10, 0 ])
        {
            PlayerBoxPurpleOne();
            translate([ 0, player_box_length + 10, 0 ])
            {
                PlayerBoxBlackOne();
                translate([ 0, player_box_length + 10, 0 ])
                {
                    PlayerBoxBlackTwo();
                    translate([ 0, player_box_length + 10, 0 ])
                    {
                        PlayerBoxYellowTwo();
                        translate([ 0, player_box_length + 10, 0 ])
                        {
                            PlayerBoxPurpleTwo();
                            translate([ 0, player_box_length + 10, 0 ])
                            {
                                PlayerBoxGreenTwo();
                                translate([ 0, player_box_length + 10, 0 ])
                                {
                                    StuffBox();
                                    translate([ 0, stuff_box_length + 10, 0 ])
                                    {
                                        FavourBox();
                                        translate([ 0, favour_box_length + 10, 0 ])
                                        {
                                            BagBox();
                                        }
                                    }
                                }
                            }
                        }
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
        cube([ 110, 50, 6 ]);
        translate([ trading_post_barn_width / 2 + 2, trading_post_barn_height / 2 + 2, 1 ])
        {
            TradingPostPurple(height = 6);
            translate([ trading_post_barn_width + 2, 0, 0 ])
            {
                TradingPostGreen(height = 6);
                translate([ trading_post_barn_width + 2, 0, 0 ])
                {
                    TradingPostYellow(height = 6);
                    translate([ trading_post_barn_width + 2, 0, 0 ])
                    {
                        TradingPostBlack(height = 6);
                    }
                }
            }
        }
        translate([ explorer_hat_width / 2 + 2, trading_post_barn_height + 4 + explorer_marker_height / 2, 1 ])
        {
            ExplorerMarkerPurple(height = 6);
            translate([ explorer_hat_width + 2, 0, 0 ])
            {
                ExplorerMarkerGreen(height = 6);
                translate([ explorer_hat_width + 2, 0, 0 ])
                {
                    ExplorerMarkerBlack(height = 6);
                    translate([ explorer_hat_width + 2, 0, 0 ])
                    {
                        ExplorerMarkerYellow(height = 6);
                        translate([ explorer_hat_width + 5, 0, 0 ])
                        {
                            BirdTurnOrder(height = 6);
                        }
                    }
                }
            }
        }
    }
    translate([ 112, 0, 0 ]) difference()
    {
        cube([ favour_tile_width + 4, favour_tile_length + 4, 5 ]);
        translate([ 2 + favour_tile_width / 2, 2 + favour_tile_length / 2, 1 ])
        {
            FavourTile(height = 6);
        }
    }
}

PlayerBoxYellowTwo();