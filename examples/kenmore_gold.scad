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

box_height = 77;
default_wall_thickness = 3;
inner_thickness = 2;
default_floor_thickness = 2;
default_lid_thickness = 2;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

// default_lid_shape_type = SHAPE_TYPE_CIRCLE;
// default_lid_shape_thickness = 1;
// default_lid_shape_width = 13;
// default_lid_layout_width = 10;

square_tile_width = 58;

cave_start_width = 38;
cave_start_length = 77;
cave_start_indent = 7;
cave_start_total_height = 17;
tile_half_height = 50;

tile_box_width = square_tile_width * 2 + default_wall_thickness * 2 + inner_thickness;
tile_box_length = square_tile_width + default_wall_thickness * 2;
tile_box_height = tile_half_height + default_floor_thickness * 2 + 15;

start_cave_box_width = tile_box_width;
start_cave_box_length = 50;
start_cave_box_height = cave_start_total_height + default_floor_thickness * 2;

loot_box_width = start_cave_box_width;
loot_box_length = start_cave_box_length;
loot_box_height = tile_box_height - start_cave_box_height;

module SquareTileBox() // `make` me
{
  MakeBoxWithCapLid(width=tile_box_width, length=tile_box_length, height=tile_box_height) {
    cube([square_tile_width, square_tile_width, tile_box_height]);
    translate([square_tile_width + inner_thickness, 0, 0])
      cube([square_tile_width, square_tile_width, tile_box_height]);
    translate([square_tile_width / 2, 0, -default_floor_thickness - 1])
      FingerHoleBase(
        radius=18, height=tile_box_height - default_floor_thickness + 1,
        wall_thickness=default_wall_thickness
      );
    translate([square_tile_width * 3 / 2 + inner_thickness, 0, -default_floor_thickness - 1])
      FingerHoleBase(
        radius=18, height=tile_box_height - default_floor_thickness + 1,
        wall_thickness=default_wall_thickness
      );
  }
}
module SquareTileBoxLid() // `make` me
{
  CapBoxLidWithLabel(width=tile_box_width, length=tile_box_length, height=tile_box_height, text_str="Kenmore Gold", label_colour="black");
}

module StartCaveBox() // `make` me
{
  MakeBoxWithCapLid(width=start_cave_box_width, length=start_cave_box_length, height=start_cave_box_height) {
    translate([$inner_width / 2, $inner_length / 2, 0]) {
      difference() {
        cuboid([cave_start_length, cave_start_width, start_cave_box_height], anchor=BOTTOM);
        translate([0, cave_start_width / 2 - cave_start_indent, 0])
          cuboid([square_tile_width - 1, cave_start_width, start_cave_box_height], anchor=BOTTOM + FRONT);
      }
    }
    translate([start_cave_box_width / 2, 0, -default_floor_thickness - 1])
      FingerHoleBase(
        radius=18, height=tile_box_height - default_floor_thickness + 1,
        wall_thickness=default_wall_thickness
      );
  }
}

module StartCaveBoxLid() // `make` me
{
  translate([start_cave_box_width + 10, 0, 0])
    CapBoxLidWithLabel(
      width=start_cave_box_width, length=start_cave_box_length, height=start_cave_box_height,
      text_str="Start Cave", label_colour="black"
    );
}

module LootBox() // `make` me
{
  MakeBoxWithCapLid(width=loot_box_width, length=loot_box_length, height=loot_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=$inner_height, radius=10);
  }
}

module LootBoxLid() // `make` me
{
  CapBoxLidWithLabel(width=loot_box_width, length=loot_box_length, height=loot_box_height, text_str="Loot", label_colour="black");
}

if (FROM_MAKE != 1) {
  LootBox();
}
