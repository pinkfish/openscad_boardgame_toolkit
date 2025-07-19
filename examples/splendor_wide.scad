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

$fn = 128;

default_lid_thickness = 3;
default_label_font = "Impact";
default_lid_shape_width = 18;
default_lid_layout_width = 12;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_wall_thickness = 4;
inner_wall_thickness = 2;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

splendor_disc_diameter = 44.5;
splendor_disc_thickness = 3.5;
splendor_disc_number = 40;
splendor_nobel_width = 61.5;
splendor_nobel_thickness = 2;
splendor_card_width = 65;
splendor_card_length = 89.5;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;

splendor_box_width = splendor_card_width + default_wall_thickness * 4 + 1 + splendor_disc_diameter;
splendor_box_length = default_wall_thickness * 5 + splendor_card_length + splendor_nobel_width;
splendor_box_height = splendor_disc_diameter + default_lid_thickness + default_floor_thickness + 1;

module SplendorBox() // `make` me
{
  MakeBoxWithSlipoverLid(width=splendor_box_width, length=splendor_box_length, height=splendor_box_height, foot=3) {
    translate([splendor_disc_diameter / 2 - 2, $inner_length / 2, 0])
      cuboid(
        [
          splendor_disc_diameter,
          splendor_disc_thickness * splendor_disc_number + 0.5,
          splendor_box_height,
        ], anchor=BOTTOM,
        rounding=splendor_disc_diameter / 2,
        edges=[
          BOTTOM + LEFT,
          BOTTOM + RIGHT,
        ]
      );
    translate([0, $inner_length / 2, splendor_disc_diameter / 2])
      cuboid(
        [
          splendor_disc_diameter,
          splendor_disc_thickness * splendor_disc_number + 0.5,
          splendor_box_height,
        ],
        anchor=BOTTOM,
      );
    translate([$inner_width - splendor_card_width / 2, splendor_card_length / 2, 0])
      cuboid([splendor_card_width, splendor_card_length, splendor_box_height], anchor=BOTTOM);
    translate([$inner_width - splendor_nobel_width / 2, $inner_length - splendor_nobel_width / 2, 0])
      cuboid([splendor_nobel_width, splendor_nobel_width, splendor_box_height], anchor=BOTTOM);
  }
}

module SplendorBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    width=splendor_box_width, length=splendor_box_length, height=splendor_box_height, foot=3,
    text_str="Splendor"
  );
}

if (FROM_MAKE != 1) {
 SplendorBoxLid();
 // MakeStripedGrid(width=splendor_box_width, length=splendor_box_length);
}
