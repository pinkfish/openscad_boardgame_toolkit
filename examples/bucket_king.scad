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

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

box_length = 288;
box_width = 140;
box_height = 70;

bucket_top_width = 28;
bucket_length = 32;
bucket_bottom_width = 19;
bucket_base_round = 3;
bucket_top_round = 3;
bucket_lip = 10;
bucket_top_section_width = 23;
bucket_rounding_radius = 3;
bucket_top_radius = 22;
bucket_bottom_radius = 9;

buckets_per_player = 5 * 3;

tile_thickness = 2;

card_width = 68;
card_length = 92;

card_box_length = card_width + default_wall_thickness * 2 + 1;
card_box_width = box_width - 2;
card_box_height = box_height - 2;

player_box_width = (box_width - 2) / 2;
player_box_length = (box_length - 2 - card_box_length) / 3;
player_box_height = (box_height - 1) / 2;

module Bucket(height)
{
    union()
    {
        // Top lip
        hull()
        {
            // Top
            intersection()
            {
                translate([ 0, bucket_length / 2 - (bucket_top_round + 2) / 2, 0 ]) cuboid(
                    [ bucket_top_width - bucket_rounding_radius * 2, bucket_top_round + 2, height ], anchor = BOTTOM);
                translate([ 0, bucket_length / 2 - bucket_top_radius, 0 ])
                    cyl(r = bucket_top_radius, h = height, anchor = BOTTOM, $fn = 128);
            }
            translate([
                bucket_top_width / 2 - bucket_rounding_radius,
                bucket_length / 2 - bucket_top_round - bucket_rounding_radius, 0
            ]) cyl(h = height, r = bucket_rounding_radius, anchor = BOTTOM, $fn = 64);
            translate([
                -bucket_top_width / 2 + bucket_rounding_radius,
                bucket_length / 2 - bucket_top_round - bucket_rounding_radius, 0
            ]) cyl(h = height, r = bucket_rounding_radius, anchor = BOTTOM, $fn = 64);
            translate([
                -bucket_top_width / 2 + bucket_rounding_radius, bucket_length / 2 - bucket_lip + bucket_rounding_radius,
                0
            ]) cyl(h = height, r = bucket_rounding_radius, anchor = BOTTOM, $fn = 64);
            translate([
                bucket_top_width / 2 - bucket_rounding_radius, bucket_length / 2 - bucket_lip + bucket_rounding_radius,
                0
            ]) cyl(h = height, r = bucket_rounding_radius, anchor = BOTTOM, $fn = 64);
        }
        // Pail.
        hull()
        {
            translate([
                bucket_bottom_width / 2 - bucket_rounding_radius, -bucket_length / 2 + bucket_base_round +
                bucket_rounding_radius
            ]) cyl(h = height, r = bucket_rounding_radius, $fn = 64, anchor = BOTTOM);
            translate([
                -bucket_bottom_width / 2 + bucket_rounding_radius, -bucket_length / 2 + bucket_base_round +
                bucket_rounding_radius
            ]) cyl(h = height, r = bucket_rounding_radius, $fn = 64, anchor = BOTTOM);
            translate([ -bucket_top_section_width / 2 + 0.44, bucket_length / 2 - bucket_lip - 0.5 ])
                cyl(h = height, r = 0.5, anchor = BOTTOM);
            translate([ bucket_top_section_width / 2 - 0.5, bucket_length / 2 - bucket_lip - 0.5 ])
                cyl(h = height, r = 0.5, anchor = BOTTOM);

            // Bottom
            intersection()
            {
                translate([ 0, -bucket_length / 2 + (bucket_base_round + 2) / 2, 0 ])
                    cuboid([ bucket_bottom_width - bucket_rounding_radius * 2, bucket_base_round + 2, height ],
                           anchor = BOTTOM);
                translate([ 0, -bucket_length / 2 + bucket_bottom_radius, 0 ])
                    cyl(r = bucket_bottom_radius, h = height, anchor = BOTTOM, $fn = 128);
            }
        }

        linear_extrude(height = height)
            translate([ bucket_top_section_width / 2 - 0.05, bucket_length / 2 - bucket_lip, 0 ]) rotate(270)
                mask2d_roundover(r = bucket_rounding_radius / 2, mask_angle = 110, $fn = 64);
        linear_extrude(height = height) mirror([ 1, 0, 0 ])
            translate([ bucket_top_section_width / 2 - 0.05, bucket_length / 2 - bucket_lip, 0 ]) rotate(270)
                mask2d_roundover(r = bucket_rounding_radius / 2, mask_angle = 110, $fn = 64);
        translate([ 0, bucket_length / 2 - bucket_lip + bucket_rounding_radius * 3 / 4, height / 2 ])
            rotate([ 90, 0, 00 ]) prismoid(size1 = [ bucket_top_section_width + 2, height ],
                                           size2 = [ bucket_top_section_width - 0.1, height ],
                                           h = bucket_rounding_radius, anchor = BOTTOM);
    }
}

module PlayerBox() // `make` me
{
    MakeBoxAndLidWithInsetHinge(width = player_box_width, length = player_box_length, height = player_box_height)
    {
        color(default_material_colour) union()
        {
            for (j = [0:1:1])
            {
                for (i = [0:1:1])
                {
                    num_tiles = i == 0 && j == 0 ? 3 : 4;
                    translate([
                        bucket_top_width / 2 + (bucket_top_width + 1) * i, bucket_length / 2 + (bucket_length + 2) * j,
                        $inner_height - num_tiles * tile_thickness - 0.5
                    ])
                    {
                        Bucket(height = num_tiles * tile_thickness + 1);
                        translate([ 0, bucket_length / 2, 0 ])
                            cyl(h = player_box_height, r = 8, rounding = 5, anchor = BOTTOM);
                        translate([ 0, -bucket_length / 2, 0 ])
                            cyl(h = player_box_height, r = 8, rounding = 5, anchor = BOTTOM);
                    }
                }
            }
        }
        color(default_material_colour) union()
        {
            difference()
            {
                RoundedBoxAllSides(width = $inner_width, length = $inner_length, height = player_box_height,
                                   radius = 5);
                for (j = [0:1:1])
                {
                    for (i = [0:1:1])
                    {
                        num_tiles = i == 0 && j == 0 ? 3 : 4;
                        translate([
                            bucket_top_width / 2 + (bucket_top_width + 1) * i,
                            bucket_length / 2 + (bucket_length + 2) * j, 0
                        ])
                        {

                            cyl(h = $inner_height + 0.01, r = 8, rounding = 1, anchor = BOTTOM);
                        }
                    }
                }
            }
        }
    }
}

module CardBox() // `make` me
{
    MakeBoxWithCapLid(width = card_box_width, length = card_box_length, height = card_box_height)
    {
        cube([ $inner_width, $inner_length, card_box_height ]);
        translate([ 0, $inner_length / 2, -default_floor_thickness - 0.01 ])
            FingerHoleBase(radius = 10, height = card_box_height, spin = 270);
    }
    if (generate_lid)
    {
        translate([ card_box_width + 10, 0, 0 ])
            CapBoxLidWithLabel(width = card_box_width, length = card_box_length, height = card_box_height,
                              text_str = "Bucket King", label_colour = "black");
    }
}

if (FROM_MAKE != 1)
{
  /*  
    hinge_diameter = 6;
    hinge_width = hinge_diameter * 2 + 1;
    hinge_length = 200 - 3 * 2;
    hinge_offset = 0.5;
    InsetHinge(length = hinge_length, width = hinge_width, offset = hinge_offset, diameter = hinge_diameter);
    */
     PlayerBox();
}