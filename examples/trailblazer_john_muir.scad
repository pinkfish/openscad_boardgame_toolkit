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
default_lid_thickness = 3;
default_floor_thickness = 2;

box_width = 282;
box_length = 282;
box_height = 69;

board_thickness = 14;
player_board_thickness = 10;

player_board_width = 154;
player_board_length = 256;

animal_cards_width = 65;
animal_cards_length = 90;
animal_cards_thickness = 23;

backpack_cards_width = 45;
backpack_cards_length = 65;
backpack_cards_thickness = 30;

destination_cards_width = 81;
destination_cards_length = 122;
destination_cards_thickness = 23;

backpack_token_width = 23.5;
backpack_token_radius = backpack_token_width / 2 / cos(180 / 6);
hiking_boots_token_diameter = 26;
achievment_token_diameter = 20;
player_score_marker_diameter = 16;
player_score_marker_thickness = 10;
tent_token_width = 12;
tent_token_length = 13;
tent_token_thickness = 10;
hiker_token_width = 17;
hiker_token_length = 31;
hiker_token_thickness = 10;

destination_cost_cards_width = 45;
destination_cost_cards_length = 65;

jmt_token_width = 24;
jmt_token_length = 24;

card_board_token_thickness = 2;

element_token_width = 20;
element_corner_round_radius = 5;

negative_token_diameter = 20;

bonus_token_diameter = 52;

bonus_tree_width = 47;
bonus_tree_length = 52;
bonus_tree_base = 28;
bonus_tree_top = 32;
bonus_tree_base_height = 9;
bonus_tree_bottom_offset = 12;

weather_token_width = 26;
weather_corner_round_radius = 5;
weather_tokens_number = 26;

generate_mmu = MAKE_MMU == 1;

default_material_colour = "purple";
default_label_solid_background = MAKE_MMU == 1;

player_box_length = box_length / 4 - 1;
player_box_width = player_board_width / 2 - 1;
player_box_height = (box_height - board_thickness - player_board_thickness - 1) / 2;

resource_box_width = player_box_width;
resource_box_length = player_box_length;
resource_box_height = player_box_height;

bonus_marker_box_width = player_box_width;
bonus_marker_box_length = player_box_length * 2;
bonus_marker_box_height = player_box_height;

destination_card_box_height = destination_cards_thickness + default_floor_thickness + default_lid_thickness + 1;
destination_card_box_width = destination_cards_length + default_wall_thickness * 2 + 1;
destination_card_box_length = destination_cards_width + default_wall_thickness * 2 + 1;

field_guide_card_box_length = animal_cards_width + default_wall_thickness * 2 + 1;
field_guide_card_box_width = destination_card_box_width;
field_guide_card_box_height = destination_card_box_height;

trails_card_box_length = backpack_cards_length + default_wall_thickness * 2 + 1;
trails_card_box_width = destination_card_box_width;
trails_card_box_height = destination_card_box_height;

weather_tokens_box_width = destination_card_box_width;
weather_tokens_box_length =
    box_width - trails_card_box_length - field_guide_card_box_length - destination_card_box_length - 2;
weather_tokens_box_height = destination_card_box_height;

echo([
    (weather_tokens_box_height - 6) / card_board_token_thickness, (resource_box_height - 6) / card_board_token_thickness
]);

module TentToken(height)
{
    linear_extrude(height)
        polygon(points = [[tent_token_width / 2, -tent_token_length / 2],
                          [-tent_token_width / 2, -tent_token_length / 2], [0, tent_token_length / 2]],
                paths = [[ 0, 1, 2 ]]);
}

module PlayerBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = player_box_width, length = player_box_length, height = player_box_height)
    {
        // tent
        translate([ tent_token_width - 2, tent_token_length / 2 + 1, $inner_height - tent_token_thickness - 0.5 ])
        {
            TentToken(tent_token_thickness + 1);
        }
        // score marker
        translate([
            player_score_marker_diameter / 2 + tent_token_width + 3, player_score_marker_diameter / 2,
            $inner_height - player_score_marker_thickness - 0.5
        ]) CylinderWithIndents(radius = player_score_marker_diameter / 2, height = player_score_marker_thickness + 1);
        // achievement tokens
        translate([
            $inner_width - achievment_token_diameter / 2, $inner_length - achievment_token_diameter / 2,
            $inner_height - card_board_token_thickness * 4 - 0.5
        ]) CylinderWithIndents(radius = achievment_token_diameter / 2, height = card_board_token_thickness * 4 + 1,
                               finger_holes = [270], finger_hole_radius = 10);

        // walking tokens
        translate([
            $inner_width - hiking_boots_token_diameter / 2, hiking_boots_token_diameter / 2,
            $inner_height - card_board_token_thickness * 5 - 0.5
        ]) CylinderWithIndents(radius = hiking_boots_token_diameter / 2, height = card_board_token_thickness * 5 + 1,
                               finger_holes = [90], finger_hole_radius = 10);
        translate([ 0, -2, $inner_height - hiker_token_thickness + 4 ])
            RoundedBoxAllSides(width = hiker_token_length + 6, length = hiker_token_width + achievment_token_diameter,
                               height = hiker_token_thickness, radius = 10);

        // hiker
        translate([
            hiker_token_length / 2, player_score_marker_diameter + 1.5 + hiker_token_width / 2,
            $inner_height - player_score_marker_thickness - 0.5
        ]) CuboidWithIndentsBottom(size = [ hiker_token_length, hiker_token_width, hiker_token_thickness + 1 ]);

        // backpack tokens
        translate([
            backpack_token_width / 2, $inner_length - backpack_token_width / 2 - 2.5,
            $inner_height - player_score_marker_thickness - 0.5
        ]) rotate([ 0, 0, 30 ])
            RegularPolygon(width = backpack_token_width, height = card_board_token_thickness * 6 + 1, shape_edges = 6,
                           finger_holes = [5], finger_hole_radius = 12);
        translate([
            backpack_token_width / 2 * 3 + 1, $inner_length - backpack_token_width / 2 - 2.5,
            $inner_height - player_score_marker_thickness - 0.5
        ]) rotate([ 0, 0, 30 ])
            RegularPolygon(width = backpack_token_width, height = card_board_token_thickness * 6 + 1, shape_edges = 6,
                           finger_holes = [2], finger_hole_radius = 12);
    }
    if (generate_lid)
    {
        translate([ player_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = player_box_width, length = player_box_length, text_width = 40,
                                   text_height = 20, text_str = "Player");
    }
}

function ResouceString(resource_num) = resource_num == 0   ? "Water"
                                       : resource_num == 1 ? "Earth"
                                       : resource_num == 2 ? "Wind"
                                       : resource_num == 3 ? "Fire"
                                       : resource_num == 4 ? "Food"
                                       : resource_num == 5 ? "Water"
                                       : resource_num == 6 ? "Sleep"
                                       : resource_num == 7 ? "Endurance"
                                       : resource_num == 8 ? "Hardship"
                                       : resource_num == 9 ? "JMT"
                                                           : "unknown";

module ResourceBox(generate_lid = true, resource_num = 0) // `make` me
{
    MakeBoxWithSlidingLid(width = resource_box_width, length = resource_box_length, height = resource_box_height)
    {
        RoundedBoxAllSides(width = $inner_width, length = $inner_length, height = resource_box_height, radius = 10);
    }
    if (generate_lid)
    {
        translate([ resource_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = resource_box_width, length = resource_box_length, text_width = 40,
                                   text_height = 20, text_str = ResourceString(resource_num));
    }
}

module DestinationCardBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = destination_card_box_width, length = destination_card_box_length,
                          height = destination_card_box_height, lid_on_length = true)
    {
        cube([ $inner_width, $inner_length, destination_card_box_height ]);
        translate([ -0.1, destination_cards_width / 2, -default_floor_thickness - 0.01 ]) FingerHoleBase(
            radius = 10, height = destination_card_box_height - default_lid_thickness + 0.02, spin = 270);
    }
    if (generate_lid)
    {
        translate([ field_guide_card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = destination_card_box_width, length = destination_card_box_length, lid_on_length = true,
            text_width = 70, text_height = 20, text_str = "Destination", label_rotated = true);
    }
}

module FieldGuideCardBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = field_guide_card_box_width, length = field_guide_card_box_length,
                          height = field_guide_card_box_height, lid_on_length = true)
    {
        cube([ animal_cards_length + 1, $inner_length, field_guide_card_box_height ]);
        translate([ -0.1, destination_cards_width / 2, -default_floor_thickness - 0.01 ]) FingerHoleBase(
            radius = 10, height = destination_card_box_height - default_lid_thickness + 0.02, spin = 270);
    }
    if (generate_lid)
    {
        translate([ field_guide_card_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = field_guide_card_box_width, length = field_guide_card_box_length, lid_on_length = true,
            text_width = 70, text_height = 20, text_str = "Field Guide", label_rotated = true);
    }
}

module TrailsCardsBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = trails_card_box_width, length = trails_card_box_length,
                          height = trails_card_box_height, lid_on_length = true)
    {
        cube([ backpack_cards_width + 1, $inner_length, trails_card_box_height ]);
        translate([ $inner_width - backpack_cards_width - 1, 0, 0 ])
            cube([ backpack_cards_width, $inner_length, trails_card_box_height ]);
        translate([ backpack_cards_width / 2, -0.1, -default_floor_thickness - 0.01 ])
            FingerHoleBase(radius = 10, height = destination_card_box_height + 0.02, spin = 0);
        translate([ $inner_width - backpack_cards_width / 2, -0.1, -default_floor_thickness - 0.01 ])
            FingerHoleBase(radius = 10, height = destination_card_box_height + 0.02, spin = 0);
    }
    if (generate_lid)
    {
        translate([ trails_card_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = trails_card_box_width, length = trails_card_box_length, lid_on_length = true,
                                   text_width = 70, text_height = 20, text_str = "Trails", label_rotated = true);
    }
}

module WeatherTokensBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = weather_tokens_box_width, length = weather_tokens_box_length,
                          height = weather_tokens_box_height, lid_on_length = true)
    {
        translate([ weather_token_width / 2, $inner_length / 2, $inner_height - card_board_token_thickness * 7 ])
        {
            cuboid([ weather_token_width, weather_token_width, card_board_token_thickness * 7 ], anchor = BOTTOM,
                   rounding = weather_corner_round_radius, edges = [FRONT + LEFT]);
            translate([ weather_token_width / 2, 0, 0 ]) cyl(d = 18, h = 30, anchor = BOTTOM, rounding = 9);
            translate([ -weather_token_width / 2, 0, 0 ]) cyl(d = 18, h = 30, anchor = BOTTOM, rounding = 9);
        }
        translate(
            [ weather_token_width * 3 / 2 + 2, $inner_length / 2, $inner_height - card_board_token_thickness * 7 ])
        {
            cuboid([ weather_token_width, weather_token_width, card_board_token_thickness * 7 ], anchor = BOTTOM,
                   rounding = weather_corner_round_radius, edges = [FRONT + LEFT]);
            translate([ weather_token_width / 2, 0, 0 ]) cyl(d = 18, h = 30, anchor = BOTTOM, rounding = 9);
        }
        translate(
            [ weather_token_width * 5 / 2 + 4, $inner_length / 2, $inner_height - card_board_token_thickness * 6 ])
        {
            cuboid([ weather_token_width, weather_token_width, card_board_token_thickness * 6 ], anchor = BOTTOM,
                   rounding = weather_corner_round_radius, edges = [FRONT + LEFT]);
            translate([ weather_token_width / 2, 0, 0 ]) cyl(d = 18, h = 30, anchor = BOTTOM, rounding = 9);
        }
        translate(
            [ weather_token_width * 7 / 2 + 6, $inner_length / 2, $inner_height - card_board_token_thickness * 6 ])
        {
            cuboid([ weather_token_width, weather_token_width, card_board_token_thickness * 6 ], anchor = BOTTOM,
                   rounding = weather_corner_round_radius, edges = [FRONT + LEFT]);
            translate([ weather_token_width / 2, 0, 0 ]) cyl(d = 18, h = 30, anchor = BOTTOM, rounding = 9);
        }
    }
    if (generate_lid)
    {
        translate([ weather_tokens_box_width + 10, 0, 0 ]) SlidingBoxLidWithLabel(
            width = weather_tokens_box_width, length = weather_tokens_box_length, lid_on_length = true, text_width = 70,
            text_height = 20, text_str = "Weather", label_rotated = true);
    }
}

module ArrowHead(height)
{
    translate([ 0, -bonus_tree_length / 2, 0 ]) linear_extrude(height = height) polygon(round_corners(
        [[bonus_tree_top / 2, bonus_tree_length * 3 / 4], [bonus_tree_width / 2, bonus_tree_base_height],
         [bonus_tree_base / 2 + 2, bonus_tree_base_height - 2], [bonus_tree_base / 2, 0], [-bonus_tree_base / 2, 0],
         [-bonus_tree_base / 2 - 2, bonus_tree_base_height - 2], [-bonus_tree_width / 2, bonus_tree_base_height],
         [-bonus_tree_top / 2, bonus_tree_length * 3 / 4], [0, bonus_tree_length]],
        radius = [ 20, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 20, 2.5 ]));
}

module BonusTileBox(generate_lid = true) // `make` me
{
    MakeBoxWithSlidingLid(width = bonus_marker_box_width, length = bonus_marker_box_length,
                          height = bonus_marker_box_height)
    {
        translate([ $inner_width / 2, bonus_token_diameter / 2, $inner_height - card_board_token_thickness * 4 - 0.5 ])
            cyl(d = bonus_token_diameter, h = card_board_token_thickness * 4 + 1, anchor = BOTTOM);
        translate([
            bonus_tree_length / 2, $inner_length - bonus_tree_width / 2,
            $inner_height - 8 * card_board_token_thickness - 0.5
        ])
        {
            rotate([ 0, 0, 270 ]) ArrowHead(8 * card_board_token_thickness + 1);
            hull()
            {
                translate([ bonus_tree_length / 2, 0, 0 ]) cyl(d = 18, anchor = BOTTOM, h = 50, rounding = 8);
                cyl(d = 18, anchor = BOTTOM, h = 50, rounding = 8);
            }
        }
        translate([
            $inner_width - bonus_tree_length / 2, $inner_length - bonus_tree_width * 3 / 2 + 10,
            $inner_height - 8 * card_board_token_thickness - 0.5
        ])
        {
            rotate([ 0, 0, 90 ]) ArrowHead(8 * card_board_token_thickness + 1);
            hull()
            {
                translate([ -bonus_tree_length / 2, 0, 0 ]) cyl(d = 18, anchor = BOTTOM, h = 50, rounding = 8);
                cyl(d = 18, anchor = BOTTOM, h = 50, rounding = 8);
            }
        }
    }
    if (generate_lid)
    {
        translate([ bonus_marker_box_width + 10, 0, 0 ])
            SlidingBoxLidWithLabel(width = bonus_marker_box_width, length = bonus_marker_box_length, text_width = 70,
                                   text_height = 20, text_str = "Bonus", label_rotated = true);
    }
}

module BoxLayout()
{
    cube([ box_width, box_length, board_thickness ]);
    cube([ 1, box_length, box_height ]);
    translate([ 0, 0, board_thickness ])
    {
        PlayerBox(false);
        translate([ 0, player_box_length, 0 ]) PlayerBox(false);
        translate([ 0, player_box_length * 2, 0 ]) PlayerBox(false);
        translate([ 0, player_box_length * 3, 0 ]) PlayerBox(false);
        translate([ 0, 0, player_box_height ]) ResourceBox(false, resource_num = 0);
        translate([ 0, player_box_length, player_box_height ]) ResourceBox(false, resource_num = 1);
        translate([ 0, player_box_length * 2, player_box_height ]) ResourceBox(false, resource_num = 2);
        translate([ 0, player_box_length * 3, player_box_height ]) ResourceBox(false, resource_num = 3);
        translate([ player_box_width, 0, 0 ]) ResourceBox(false, resource_num = 4);
        translate([ player_box_width, player_box_length, 0 ]) ResourceBox(false, resource_num = 5);
        translate([ player_box_width, player_box_length * 2, 0 ]) ResourceBox(false, resource_num = 6);
        translate([ player_box_width, player_box_length * 3, 0 ]) ResourceBox(false, resource_num = 7);
        translate([ player_box_width, 0, player_box_height ]) ResourceBox(false, resource_num = 8);
        translate([ player_box_width, player_box_length, player_box_height ]) ResourceBox(false, resource_num = 9);
        translate([ player_box_width, player_box_length * 2, player_box_height ]) BonusTileBox(false);
        translate([ player_box_width * 2, 0, 0 ]) DestinationCardBox(false);
        translate([ player_box_width * 2, destination_card_box_length, 0 ]) FieldGuideCardBox(false);
        translate([ player_box_width * 2, destination_card_box_length + field_guide_card_box_length, 0 ])
            TrailsCardsBox(false);
        translate([
            player_box_width * 2, destination_card_box_length + field_guide_card_box_length + trails_card_box_length, 0
        ]) WeatherTokensBox(false);
    }
    // translate([ 0, 0, box_height - player_board_thickness ])
    //   cube([ player_board_width, player_board_length, player_board_thickness ]);
}

if (FROM_MAKE != 1)
{
    PlayerBox();
}