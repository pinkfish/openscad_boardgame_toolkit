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

// per player
king_marker_num = 1;
trading_post_maker_num = 9;
favour_token_num = 4;
turn_order_token = 1;
explorer_token = 3;

box_width = 211;
box_length = 268;
main_box_height = 68;
expansion_box_height = 50;
board_thickness = 12;

king_marker = 20.5;
favour_marker_width = 23.5;
favour_marker_length = 26.5;
favour_base_width = 16;

// Cards
card_width = 68;
card_length = 92;

// Player layout bits.
player_layout_thickness = 2;
player_layout_num = 4;
player_layout_width = 147;
player_layout_length = 266;

// Favour tilers.
favour_tile_width = 72;
favour_tile_length = 60.5;
favour_tile_side_bit = 18.5;
favour_tile_edge_slope_in = 5;
favour_tile_edge_slope_down = 3;
favour_tile_top_dip = 8.5;

// shared hat width
explorer_hat_width = 18.5;

// Bird stuff
bird_diameter = 20.5;
bird_length = 25;
bird_base = 7;
bird_top_base = 11;
bird_lump = 3.75;
bird_beak_diameter = 21.5;
bird_diameter_base = 6;
bird_lump_length = 23;
bird_lump_second_length = 21.75;

marker_thickness = 10;

trading_post_height = 16;
trading_post_width = 17;

explorer_marker_height = 21.5;
explorer_base_width = 18.25;

player_box_height = (main_box_height - board_thickness - 1) / 4; // marker_thickness + lid_thickness * 2 + 0.5;
player_box_length = (box_length - 2) / 2;
player_box_width = box_width - player_layout_width - 2;

module PlayerBoxTwoBase(generate_lid = true, material_colour = undef)
{
    if (generate_lid)
    {
        translate([ player_box_width + 10, 0, 0 ])
        {
            SlidingBoxLidWithLabel(width = player_box_width, length = player_box_length, text_width = 50,
                                   text_height = 15, text_str = "Player", label_rotated = true,
                                   material_colour = material_colour, label_colour = "black");
        }
    }
    else
    {
        MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height,
                              material_colour = material_colour)
        {
            marker_depth = $inner_height - marker_thickness - 0.5;
            translate([ 0, 0, $inner_height - 5 ]) color(material_colour) RoundedBoxAllSides(
                width = $inner_width, length = $inner_length, height = 5, radius = default_wall_thickness, $fn = 64);
            translate([ 0, 0, marker_depth ])
            {
                // favour.
                translate([ ($inner_width - favour_marker_width * 2 - 1.5) / 2, favour_marker_length / 2 + 1, 0 ])
                {
                    for (i = [0:1:1])
                    {
                        translate([ favour_marker_width / 2, (favour_marker_length + 7) * i, 0 ])
                        {
                            rotate([ 0, 0, 180 ]) color(material_colour) FavourMarker(height = marker_thickness + 1);
                            translate([ 0, favour_marker_length / 2, marker_thickness / 4 ]) color(material_colour)
                                sphere(r = 12, anchor = BOTTOM);
                            translate([ 0, -favour_marker_length / 2 + 3, marker_thickness / 4 ]) color(material_colour)
                                sphere(r = 12, anchor = BOTTOM);
                        }
                        translate(
                            [ favour_marker_width / 2 + favour_marker_width + 1.5, (favour_marker_length + 7) * i, 0 ])
                        {
                            rotate([ 0, 0, 180 ]) color(material_colour) FavourMarker(height = marker_thickness + 1);
                            translate([ 0, favour_marker_length / 2, marker_thickness / 4 ]) color(material_colour)
                                sphere(r = 12, anchor = BOTTOM);
                            translate([ 0, -favour_marker_length / 2 + 2, marker_thickness / 4 ]) color(material_colour)
                                sphere(r = 12, anchor = BOTTOM);
                        }
                    }
                }
                // explorers.
                translate([
                    ($inner_width - explorer_marker_height) / 2,
                    (favour_marker_length + 5.5) * 2 + explorer_hat_width / 2 + 5, 0
                ])
                {
                    for (i = [0:1:2])
                    {
                        translate([ explorer_marker_height / 2, (explorer_base_width + 2) * i, 0 ])
                        {
                            children(0);
                            translate([ explorer_marker_height / 2, 0, marker_thickness / 4 ]) color(material_colour)
                                cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                            translate([ -explorer_marker_height / 2, 0, marker_thickness / 4 ]) color(material_colour)
                                cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                        }
                    }
                }
            }
        }
    }
}

module PlayerBoxOneBase(generate_lid = true, material_colour = undef)
{
    if (generate_lid)
    {
        SlidingBoxLidWithLabel(width = player_box_width, length = player_box_length, text_width = 50, text_height = 15,
                               text_str = "Player", label_rotated = true, material_colour = material_colour,
                               label_colour = "black");
    }
    else
    {
        MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height,
                              material_colour = material_colour)
        {
            translate([ 0, 0, $inner_height - 5 ]) color(material_colour) RoundedBoxAllSides(
                width = $inner_width, length = $inner_length, height = 5, radius = default_wall_thickness, $fn = 64);
            marker_depth = player_box_height - default_lid_thickness * 2 - marker_thickness - 0.5;
            // king marker
            translate([ ($inner_width - king_marker) / 2, 0, marker_depth ])
            {
                color(material_colour)
                    cuboid([ king_marker, king_marker, marker_thickness + 1 ], anchor = BOTTOM + LEFT + FRONT);
                translate([ king_marker, king_marker / 2, marker_thickness / 4 ]) color(material_colour)
                    cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                translate([ 0, king_marker / 2, marker_thickness / 4 ]) color(material_colour)
                    cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
            }

            // bird marker
            translate([
                bird_length / 2 + ($inner_width - bird_length) / 2, king_marker + 1 + bird_diameter / 2,
                marker_depth
            ])
            {
                color(material_colour) BirdTurnOrder(marker_thickness + 1);
                translate([ bird_length / 2, 0, marker_thickness / 2 - 1 ]) color(material_colour)
                    cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                translate([ -bird_length / 2, 0, marker_thickness / 2 - 1 ]) color(material_colour)
                    cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
            }

            width = trading_post_height * 2 + 18;
            translate([
                ($inner_width - width) / 2 + trading_post_height / 2,
                bird_diameter + king_marker + trading_post_width / 2,
                marker_depth
            ])
            {
                for (i = [0:1:3])
                {
                    translate([ 2, (trading_post_width + 0.75) * i, 0 ])
                    {
                        children(0);
                        translate([ trading_post_height / 2, 0, marker_thickness / 4 ]) color(material_colour)
                            cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                    }
                }
                for (i = [0:1:3])
                {
                    translate([ trading_post_height + 13, (trading_post_width + 0.75) * i, 0 ])
                    {
                        children(1);
                        translate([ -trading_post_height / 2, 0 * i, marker_thickness / 4 ]) color(material_colour)
                            cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
                    }
                }
            }
            translate([ $inner_width / 2 - 1.5, $inner_length - trading_post_width / 2 - default_wall_thickness, 0 ])
            {
                rotate([ 0, 0, 90 ]) children(1);
                translate([ 0, -trading_post_height / 2, marker_thickness / 4 ]) color(material_colour)
                    cyl(r = 10, anchor = BOTTOM, l = 20, rounding = 9);
            }
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