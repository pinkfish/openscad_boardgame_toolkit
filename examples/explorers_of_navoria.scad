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

include <lib/explorers_of_navoria_shared.scad>

default_lid_shape_type = SHAPE_TYPE_CLOUD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 12;
default_lid_aspect_ratio = 1.5;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

// total
num_favour_tiles = 10;
num_cards = 60;
num_ref_cards = 4;

trading_post_mushroom_width = 17.5;
trading_post_mushroom_height = 16;
trading_post_mushroom_inset_side = 2;
trading_post_mushroom_inset_up = 3;

trading_post_triangle_width = 17.5;
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

favour_box_width = box_width - player_box_width - 1.5;
favour_box_length = favour_tile_width + default_wall_thickness * 2;
favour_box_height = default_lid_thickness * 2 + player_layout_thickness * num_favour_tiles / 2 + 0.5;

stuff_box_height =
main_box_height - board_thickness - favour_box_height - 1 - player_layout_thickness * player_layout_num;
stuff_box_width = favour_box_width / 3;
stuff_box_length = favour_box_length;

card_box_width = box_width - player_box_width - 2;
card_box_length = card_width + default_wall_thickness * 2 + 0.5;
card_box_height =
main_box_height - board_thickness - player_layout_thickness - 1 - player_layout_thickness * player_layout_num;

bag_box_length = box_length - stuff_box_length - 2 - card_box_length;
bag_box_width = box_width - player_box_width - 2;
bag_box_height =
main_box_height - board_thickness - player_layout_thickness - 1 - player_layout_thickness * player_layout_num;

module FavourTile(height) {
  module OneBar(reverse) {
    width = favour_tile_width;
    mirror([reverse, 0, 0]) hull() {
        translate([width / 2 - 2 - favour_tile_edge_slope_in, favour_tile_length / 2 - 2, 0])
          cyl(d=4, h=height, $fn=32);
        translate([width / 2 - 2, favour_tile_length / 2 - 2 - favour_tile_edge_slope_down, 0])
          cyl(d=4, h=height, $fn=32);
        translate([width / 2 - favour_tile_side_bit + 3, favour_tile_length / 2 - 3, 0])
          cyl(d=6, h=height, $fn=32);
        translate([width / 2 - 2, -favour_tile_length / 2 + 2 + favour_tile_edge_slope_down, 0])
          cyl(d=4, h=height, $fn=32);
        translate([width / 2 - 2 - favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0])
          cyl(d=4, h=height, $fn=32);
        translate([width / 2 - favour_tile_side_bit + 2, -favour_tile_length / 2 + 2, 0])
          cyl(d=4, h=height, $fn=32);
      }
  }
  translate([0, 0, height / 2]) {
    difference() {
      union() {
        OneBar(0);
        OneBar(1);
        hull() {
          translate(
            [
              favour_tile_width / 2 - 2 - favour_tile_edge_slope_in,
              favour_tile_length / 2 - 2 - favour_tile_top_dip + 2,
              0,
            ]
          ) cyl(d=4, h=height, $fn=32);
          translate(
            [
              -favour_tile_width / 2 + 2 + favour_tile_edge_slope_in,
              favour_tile_length / 2 - 2 - favour_tile_top_dip + 2,
              0,
            ]
          ) cyl(d=4, h=height, $fn=32);
          translate([favour_tile_width / 2 - 2 - favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0])
            cyl(d=4, h=height, $fn=32);
          translate(
            [-favour_tile_width / 2 + 2 + favour_tile_edge_slope_in, -favour_tile_length / 2 + 2, 0]
          )
            cyl(d=4, h=height, $fn=32);
        }
      }
      translate([0, (favour_tile_length - favour_tile_top_dip) / 2, 0])
        cuboid(
          [favour_tile_width - favour_tile_side_bit * 2, favour_tile_top_dip, height + 1], rounding=2,
          edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT], $fn=32
        );
    }
  }
}

module TradingPostYellow(height) {
  translate(
    [0, trading_post_mushroom_height - trading_post_mushroom_inset_up - trading_post_mushroom_height / 2, 0]
  ) {
    difference() {
      translate([0, -trading_post_mushroom_height + trading_post_mushroom_inset_up, 0])
        linear_extrude(height=height)
          ellipse(d=[trading_post_mushroom_width, trading_post_mushroom_height * 2], anchor=FRONT);
      translate([0, trading_post_mushroom_height + 0.5, -0.5]) cuboid(
          [trading_post_mushroom_width + 1, trading_post_mushroom_height * 2 + 1, height + 1], anchor=BOTTOM
        );
    }
    translate([0, trading_post_mushroom_inset_up, 0]) cuboid(
        [
          trading_post_mushroom_width - trading_post_mushroom_inset_side * 2,
          trading_post_mushroom_inset_up + 0.5,
          height,
        ],
        anchor=BOTTOM + BACK
      );
  }
}

module TradingPostPurple(height) {
  translate(
    [0, trading_post_triangle_height - trading_post_triangle_inset_up - trading_post_triangle_height / 2, 0]
  ) {
    hull() {
      translate([trading_post_triangle_width / 2 - 0.5, -0.5, 0])
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
      translate([-trading_post_triangle_width / 2 + 0.5, -0.5, 0])
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
      translate([0, -trading_post_triangle_height + trading_post_triangle_inset_up + 0.5, 0])
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
    }
    translate([0, trading_post_triangle_inset_up, 0]) cuboid(
        [
          trading_post_triangle_width - trading_post_triangle_inset_side * 2,
          trading_post_triangle_inset_up + 0.5,
          height,
        ],
        anchor=BOTTOM + BACK
      );
  }
}

module TradingPostBlack(height) {
  translate([0, trading_post_barn_height - trading_post_barn_inset_up - trading_post_barn_height / 2, 0]) {
    hull() {
      translate([trading_post_barn_width / 2 - 0.5, -0.5, 0]) cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
      translate([-trading_post_barn_width / 2 + 0.5, -0.5, 0])
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
      translate(
        [trading_post_barn_top_width / 2, -trading_post_barn_height + trading_post_barn_inset_up + 0.5, 0]
      )
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
      translate(
        [-trading_post_barn_top_width / 2, -trading_post_barn_height + trading_post_barn_inset_up + 0.5, 0]
      )
        cyl(d=1, h=height, $fn=16, anchor=BOTTOM);
    }
    translate([0, trading_post_barn_inset_up, 0]) cuboid(
        [trading_post_barn_width - trading_post_barn_inset_side * 2, trading_post_barn_inset_up + 0.5, height],
        anchor=BOTTOM + BACK
      );
  }
}

module TradingPostGreen(height) {
  translate([0, -trading_post_castle_height / 2, 0]) {
    translate([0, 0, 0]) cuboid(
        [trading_post_castle_base_width, trading_post_castle_inset_up + 0.5, height],
        anchor=BOTTOM + FRONT
      );
    difference() {
      // middle bit
      translate([0, trading_post_castle_height, 0])
        cuboid(
          [trading_post_castle_width, trading_post_castle_top_height, height], anchor=BOTTOM + BACK,
          rounding=0.5, edges=[BACK + LEFT, BACK + RIGHT], $fn=16
        );
      // bottom rounding
      translate(
        [
          -(trading_post_castle_width - trading_post_castle_gap * 2) / 3.5,
          trading_post_castle_height + 1,
          -0.5,
        ]
      ) cuboid(
          [trading_post_castle_gap, trading_post_castle_crenelation_height + 1, height + 1],
          anchor=BOTTOM + BACK, rounding=0.5, edges=[FRONT + LEFT, FRONT + RIGHT], $fn=16
        );
      translate(
        [
          (trading_post_castle_width - trading_post_castle_gap * 2) / 3.5,
          trading_post_castle_height + 1,
          -0.5,
        ]
      ) cuboid(
          [trading_post_castle_gap, trading_post_castle_crenelation_height + 1, height + 1],
          anchor=BOTTOM + BACK, rounding=0.5, edges=[FRONT + LEFT, FRONT + RIGHT], $fn=16
        );
    }

    hull() {
      translate(
        [trading_post_castle_width / 2 - 0.5, trading_post_castle_height - trading_post_castle_top_height, 0]
      )
        cyl(d=1, h=height, anchor=BOTTOM, $fn=16);
      translate(
        [
          -trading_post_castle_width / 2 + 0.5,
          trading_post_castle_height - trading_post_castle_top_height,
          0,
        ]
      ) cyl(d=1, h=height, anchor=BOTTOM, $fn=16);
      translate([trading_post_castle_base_width / 2 - 0.5, trading_post_castle_inset_up, 0])
        cyl(d=1, h=height, anchor=BOTTOM, $fn=16);
      translate([-trading_post_castle_base_width / 2 + 0.5, trading_post_castle_inset_up, 0])
        cyl(d=1, h=height, anchor=BOTTOM, $fn=16);
    }
  }
}

module ExplorerMarkerGreen(height) {
  translate([0, -explorer_marker_height / 2, 0]) {
    difference() {
      union() {
        hull() {
          translate([0, explorer_marker_height, 0])
            cyl(d=explorer_marker_top_diameter, h=height, anchor=BOTTOM + BACK, $fn=64);
          translate([explorer_base_width / 2 - 0.5, 0, 0])
            cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
          translate([-explorer_base_width / 2 + 0.5, 0, 0])
            cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
        }
        hull() {
          translate([explorer_hat_width / 2 - 2.5, explorer_hat_green_top_left, 0])
            cyl(d=5, anchor=BOTTOM + BACK, h=height, $fn=32);
          translate([-explorer_hat_width / 2 + 2.5, explorer_hat_green_top_right, 0])
            cyl(d=5, anchor=BOTTOM + BACK, h=height, $fn=32);
        }
        translate([explorer_marker_top_diameter / 2 + 0.7, explorer_hat_green_top_left + 2.9, 0]) {
          difference() {
            translate([-0.35, -1.5, 0]) cuboid([1.5, 1.6, height + 1], anchor=BOTTOM + BACK);
            cyl(d=3, h=height + 1, anchor=BOTTOM + BACK, $fn=16);
          }
        }
        translate([-explorer_marker_top_diameter / 2 - 1.8, explorer_hat_green_top_right + 3.7, 0]) {
          difference() {
            translate([1, -1.6, 0]) cuboid([2, 2.1, height + 1], anchor=BOTTOM + BACK);
            cyl(d=4, h=height + 1, anchor=BOTTOM + BACK, $fn=16);
          }
        }
      }
    }
  }
}

module ExplorerMarkerYellow(height) {
  translate([0, -explorer_marker_height / 2, 0]) {
    difference() {
      hull() {
        translate([0, explorer_marker_height, 0])
          cyl(d=explorer_marker_top_diameter + 2, h=height, anchor=BOTTOM + BACK, $fn=64);
        translate([explorer_base_width / 2 - 0.5, 0, 0])
          cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
        translate([-explorer_base_width / 2 + 0.5, 0, 0])
          cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
      }
      translate([0, explorer_hat_yellow_bottom, -0.5])
        cuboid([explorer_hat_width, explorer_marker_height, height + 1], anchor=BOTTOM + FRONT);
    }
    // Arms section
    hull() {
      // Left side
      translate([explorer_hat_width / 2 - 1.5, explorer_hat_yellow_bottom + 1.5, 0])
        cyl(d=3, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_width / 2 - 1, explorer_hat_yellow_bottom + 3, 0])
        cyl(d=2, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_yellow_lower_flat / 2 - 0.2, explorer_hat_yellow_top, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_yellow_lower_flat / 2 - 1.5, explorer_hat_yellow_bottom - 1, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate(
        [
          (explorer_hat_yellow_lower_flat + explorer_hat_width) / 4 - 0.5,
          (explorer_hat_yellow_top + explorer_hat_yellow_bottom) / 2 + 0.8,
          0,
        ]
      ) cyl(d=3.75, anchor=BOTTOM + BACK, h=height, $fn=32);

      // Right side
      translate([-explorer_hat_width / 2 + 1.5, explorer_hat_yellow_bottom + 1.5, 0])
        cyl(d=3, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_width / 2 + 1, explorer_hat_yellow_bottom + 3, 0])
        cyl(d=2, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_yellow_lower_flat / 2 + 0.2, explorer_hat_yellow_top, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_yellow_lower_flat / 2 + 1.5, explorer_hat_yellow_bottom - 1, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate(
        [
          -(explorer_hat_yellow_lower_flat + explorer_hat_width) / 4 + 0.5,
          (explorer_hat_yellow_top + explorer_hat_yellow_bottom) / 2 + 0.8,
          0,
        ]
      ) cyl(d=3.75, anchor=BOTTOM + BACK, h=height, $fn=32);
    }
    // Hat section.
    hull() {
      translate([explorer_hat_yellow_lower_flat / 2 - 0.5, explorer_hat_yellow_top, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_yellow_lower_flat / 2 + 0.5, explorer_hat_yellow_top, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);

      translate([-explorer_hat_yellow_top_flat / 2 + 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_yellow_top_flat / 2 - 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
    }
  }
}

module ExplorerMarkerBlack(height) {
  translate([0, -explorer_marker_height / 2, 0]) {
    difference() {
      hull() {
        translate([0, explorer_marker_height, 0])
          cyl(d=explorer_marker_top_diameter + 2, h=height, anchor=BOTTOM + BACK, $fn=64);
        translate([explorer_base_width / 2 - 0.25, 0, 0])
          cyl(d=1.5, h=height, anchor=BOTTOM + FRONT, $fn=32);
        translate([-explorer_base_width / 2 + 0.25, 0, 0])
          cyl(d=1.5, h=height, anchor=BOTTOM + FRONT, $fn=32);
      }
      translate([0, explorer_hat_black_top_height, -0.5]) cuboid(
          [explorer_hat_black_width + 10, explorer_hat_black_top_height, height + 1], anchor=BOTTOM + FRONT
        );
    }

    hull() {
      translate([explorer_hat_black_width / 2 - 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([-explorer_hat_black_width / 2 + 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([explorer_hat_black_width / 2 - 0.75, explorer_hat_black_top_height, 0])
        cyl(d=1.5, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([-explorer_hat_black_width / 2 + 0.75, explorer_hat_black_top_height, 0])
        cyl(d=1.5, anchor=BOTTOM + BACK, h=height, $fn=16);
    }

    hull() {
      translate([explorer_hat_width / 2 - 0.5, explorer_hat_black_top_height, 0])
        cyl(d=2, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_black_width / 2 - 0.5, explorer_hat_black_bottom_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_width / 2 + 0.5, explorer_hat_black_top_height, 0])
        cyl(d=2, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_black_width / 2 + 0.5, explorer_hat_black_bottom_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
    }
  }
}

module ExplorerMarkerPurple(height) {
  translate([0, -explorer_marker_height / 2, 0]) {
    difference() {
      hull() {
        translate([0, explorer_marker_height, 0])
          cyl(d=explorer_marker_top_diameter, h=height, anchor=BOTTOM + BACK, $fn=64);
        translate([explorer_base_width / 2 - 0.5, 0, 0])
          cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
        translate([-explorer_base_width / 2 + 0.5, 0, 0])
          cyl(d=1, h=height, anchor=BOTTOM + FRONT, $fn=32);
      }
    }

    // Hat
    hull() {
      translate([explorer_hat_purple_top_width / 2 - 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([-explorer_hat_purple_top_width / 2 + 0.5, explorer_marker_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([explorer_hat_purple_bottom_width / 2 - 0.5, explorer_hat_purple_top_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
      translate([-explorer_hat_purple_bottom_width / 2 + 0.5, explorer_hat_purple_top_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=16);
    }
    // Arms
    hull() {
      translate([explorer_hat_width / 2 - 0.5, explorer_hat_purple_top_height, 0])
        cyl(d=2.5, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([explorer_hat_purple_bottom_width / 2 - 0.5, explorer_hat_purple_bottom_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_width / 2 + 0.5, explorer_hat_purple_top_height, 0])
        cyl(d=2.5, anchor=BOTTOM + BACK, h=height, $fn=32);
      translate([-explorer_hat_purple_bottom_width / 2 + 0.5, explorer_hat_purple_bottom_height, 0])
        cyl(d=1, anchor=BOTTOM + BACK, h=height, $fn=32);
    }
  }
}

module PlayerBoxGreenOne() // `make` me
{
  PlayerBoxOneBase(generate_lid=false, material_colour="green") {
    rotate([0, 0, 90]) color("green") TradingPostGreen(marker_thickness + 1);
    rotate([0, 0, -90]) color("green") TradingPostGreen(marker_thickness + 1);
  }
}

module PlayerBoxGreenOneLid() // `make` me
{
  PlayerBoxOneBase(generate_lid=true, material_colour="green") {
    rotate([0, 0, 90]) color("green") TradingPostGreen(marker_thickness + 1);
    rotate([0, 0, -90]) color("green") TradingPostGreen(marker_thickness + 1);
  }
}

module PlayerBoxYellowOne() // `make` me
{
  PlayerBoxOneBase(generate_lid=false, material_colour="yellow") {
    rotate([0, 0, -90]) TradingPostYellow(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostYellow(marker_thickness + 1);
  }
}

module PlayerBoxYellowOneLid() // `make` me
{
  PlayerBoxOneBase(generate_lid=true, material_colour="yellow") {
    rotate([0, 0, -90]) TradingPostYellow(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostYellow(marker_thickness + 1);
  }
}

module PlayerBoxPurpleOne() // `make` me
{
  PlayerBoxOneBase(generate_lid=false, material_colour="purple") {
    rotate([0, 0, -90]) TradingPostPurple(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostPurple(marker_thickness + 1);
  }
}

module PlayerBoxPurpleOneLid() // `make` me
{
  PlayerBoxOneBase(generate_lid=true, material_colour="purple") {
    rotate([0, 0, -90]) TradingPostPurple(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostPurple(marker_thickness + 1);
  }
}

module PlayerBoxBlackOne() // `make` me
{
  PlayerBoxOneBase(generate_lid=false, material_colour="grey") {
    rotate([0, 0, -90]) TradingPostBlack(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostBlack(marker_thickness + 1);
  }
}

module PlayerBoxBlackOneLid() // `make` me
{
  PlayerBoxOneBase(generate_lid=true, material_colour="grey") {
    rotate([0, 0, -90]) TradingPostBlack(marker_thickness + 1);
    rotate([0, 0, 90]) TradingPostBlack(marker_thickness + 1);
  }
}

module PlayerBoxGreenTwo() // `make` me
{
  PlayerBoxTwoBase(generate_lid=false, material_colour="green") {
    rotate([0, 0, 90]) color("green") ExplorerMarkerGreen(marker_thickness + 1);
    rotate([0, 0, -90]) color("green") ExplorerMarkerGreen(marker_thickness + 1);
  }
}

module PlayerBoxGreenTwoLid() // `make` me
{
  PlayerBoxTwoBase(generate_lid=true, material_colour="green") {
    rotate([0, 0, 90]) color("green") ExplorerMarkerGreen(marker_thickness + 1);
    rotate([0, 0, -90]) color("green") ExplorerMarkerGreen(marker_thickness + 1);
  }
}

module PlayerBoxYellowTwo() // `make` me
{
  PlayerBoxTwoBase(generate_lid=false, material_colour="yellow") {
    rotate([0, 0, 90]) color("yellow") ExplorerMarkerYellow(marker_thickness + 1);
    rotate([0, 0, -90]) color("yellow") ExplorerMarkerYellow(marker_thickness + 1);
  }
}

module PlayerBoxYellowTwoLid() // `make` me
{
  PlayerBoxTwoBase(generate_lid=true, material_colour="yellow") {
    rotate([0, 0, 90]) color("yellow") ExplorerMarkerYellow(marker_thickness + 1);
    rotate([0, 0, -90]) color("yellow") ExplorerMarkerYellow(marker_thickness + 1);
  }
}

module PlayerBoxPurpleTwo() // `make` me
{
  PlayerBoxTwoBase(generate_lid=false, material_colour="purple") {
    rotate([0, 0, 90]) color("purple") ExplorerMarkerPurple(marker_thickness + 1);
    rotate([0, 0, -90]) color("purple") ExplorerMarkerPurple(marker_thickness + 1);
  }
}

module PlayerBoxPurpleTwoLid() // `make` me
{
  PlayerBoxTwoBase(generate_lid=true, material_colour="purple") {
    rotate([0, 0, 90]) color("purple") ExplorerMarkerPurple(marker_thickness + 1);
    rotate([0, 0, -90]) color("purple") ExplorerMarkerPurple(marker_thickness + 1);
  }
}

module PlayerBoxBlackTwo() // `make` me
{
  PlayerBoxTwoBase(generate_lid=false, material_colour="grey") {
    rotate([0, 0, 90]) color("grey") ExplorerMarkerBlack(marker_thickness + 1);
    rotate([0, 0, -90]) color("grey") ExplorerMarkerBlack(marker_thickness + 1);
  }
}

module PlayerBoxBlackTwoLid() // `make` me
{
  PlayerBoxTwoBase(generate_lid=true, material_colour="grey") {
    rotate([0, 0, 90]) color("grey") ExplorerMarkerBlack(marker_thickness + 1);
    rotate([0, 0, -90]) color("grey") ExplorerMarkerBlack(marker_thickness + 1);
  }
}

module FavourBox() // `make` me
{
  MakeBoxWithCapLid(width=favour_box_width, length=favour_box_length, height=favour_box_height) {
    translate([favour_tile_length / 2, favour_tile_width / 2, 0]) {
      rotate([0, 0, 270]) color(default_material_colour)
          FavourTile(height=num_favour_tiles / 2 * player_layout_thickness + 1);
      translate([favour_tile_length / 2 - favour_tile_top_dip, 0, 0]) color(default_material_colour)
          cyl(r=11, anchor=BOTTOM, h=favour_box_height * 2, rounding=9.5);
    }
    translate([favour_box_width - default_wall_thickness * 2 - favour_tile_length / 2, favour_tile_width / 2, 0]) {
      rotate([0, 0, 90]) color(default_material_colour)
          FavourTile(height=num_favour_tiles / 2 * player_layout_thickness + 1);
      translate([-favour_tile_length / 2 + favour_tile_top_dip, 0, 0]) color(default_material_colour)
          cyl(r=11, anchor=BOTTOM, h=favour_box_height * 2, rounding=9.5);
    }
  }
}

module FavourBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=favour_box_width, length=favour_box_length, height=favour_box_height,
    text_str="Favours",
    label_options=MakeLabelOptions(label_colour="black")
  );
}

module StuffBox() // `make` me
{
  MakeBoxWithSlidingLid(width=stuff_box_width, length=stuff_box_length, height=stuff_box_height) {
    color(default_material_colour)
      RoundedBoxAllSides(
        width=stuff_box_width - default_wall_thickness * 2,
        length=stuff_box_length - default_wall_thickness * 2, height=stuff_box_height, radius=10
      );
  }
}

module StuffBoxLid() // `make` me
{
  translate([stuff_box_width + 10, 0, 0]) {
    SlidingBoxLidWithLabel(
      width=stuff_box_width, length=stuff_box_length,
      text_str="Swords",
      label_options=MakeLabelOptions(label_colour="black")
    );
    translate([stuff_box_width + 10, 0, 0]) {
      SlidingBoxLidWithLabel(
        width=stuff_box_width, length=stuff_box_length,
        text_str="Apples",
        label_options=MakeLabelOptions(label_colour="black")
      );
      translate([stuff_box_width + 10, 0, 0]) {
        SlidingBoxLidWithLabel(
          width=stuff_box_width, length=stuff_box_length,
          text_str="Crystals",
          label_options=MakeLabelOptions(label_colour="black")
        );
      }
    }
  }
}

module CardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=card_box_height,
    lid_on_length=true
  ) {
    cube([card_length + 2, $inner_length, card_box_height]);
    translate([0, $inner_length / 2, -default_lid_thickness - 0.01]) color(default_material_colour)
        FingerHoleBase(radius=20, height=card_box_height);
    translate([$inner_width - ($inner_width - card_length - 2) / 2, $inner_length / 2, $inner_height - 1])
      color(default_material_colour) linear_extrude(card_box_height) rotate(270)
            text("NavoriA", size=13, font="Marker Felt:style=Regular", valign="center", halign="center");
    translate([$inner_width - ($inner_width - card_length - 2) / 2 + 11, $inner_length / 2, $inner_height - 1])
      color(default_material_colour) linear_extrude(card_box_height) rotate(270) text(
              "Explorers of", size=5, font="Marker Felt:style=Regular", valign="center", halign="center"
            );
  }
}

module CardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length,
    text_str="Cards",
    label_options=MakeLabelOptions(label_colour="black"),
    lid_on_length=true
  );
}

module BagBox() // `make` me
{
  translate([bag_box_width / 2, bag_box_length / 2, 0]) difference() {
      color(default_material_colour)
        cuboid([bag_box_width, bag_box_length, bag_box_height], rounding=2, anchor=BOTTOM);
      translate([0, 0, default_lid_thickness]) color(default_material_colour)
          cuboid(
            [bag_box_width - default_wall_thickness * 2, bag_box_length - default_wall_thickness * 2, bag_box_height],
            anchor=BOTTOM
          );
    }
}

module BoxLayout() {
  cube([box_width, box_length, board_thickness]);
  cube([1, box_length, main_box_height]);
  translate([0, 0, board_thickness]) {
    PlayerBoxGreenOne();
    translate([0, 0, player_box_height]) PlayerBoxYellowOne();
    translate([0, 0, player_box_height * 2]) PlayerBoxPurpleOne();
    translate([0, 0, player_box_height * 3]) PlayerBoxBlackOne();
    translate([0, player_box_length, 0]) PlayerBoxGreenTwo();
    translate([0, player_box_length, player_box_height]) PlayerBoxYellowTwo();
    translate([0, player_box_length, player_box_height * 2]) PlayerBoxPurpleTwo();
    translate([0, player_box_length, player_box_height * 3]) PlayerBoxBlackTwo();
    translate([player_box_width, 0, 0]) FavourBox();
    translate([player_box_width, 0, favour_box_height]) StuffBox();
    translate([player_box_width + stuff_box_width, 0, favour_box_height]) StuffBox();
    translate([player_box_width + stuff_box_width * 2, 0, favour_box_height]) StuffBox();
    translate([player_box_width, favour_box_length, 0]) CardBox();
    translate([player_box_width, favour_box_length + card_box_length, 0]) BagBox();
  }
  translate([box_width - player_layout_width, 0, main_box_height - player_layout_thickness * player_layout_num])
    cube([player_layout_width, box_length, player_layout_thickness * player_layout_num]);
}

module PrintLayout() {
  PlayerBoxGreenOne();
  translate([0, player_box_length + 10, 0]) {
    PlayerBoxYellowOne();
    translate([0, player_box_length + 10, 0]) {
      PlayerBoxPurpleOne();
      translate([0, player_box_length + 10, 0]) {
        PlayerBoxBlackOne();
        translate([0, player_box_length + 10, 0]) {
          PlayerBoxBlackTwo();
          translate([0, player_box_length + 10, 0]) {
            PlayerBoxYellowTwo();
            translate([0, player_box_length + 10, 0]) {
              PlayerBoxPurpleTwo();
              translate([0, player_box_length + 10, 0]) {
                PlayerBoxGreenTwo();
                translate([0, player_box_length + 10, 0]) {
                  StuffBox();
                  translate([0, stuff_box_length + 10, 0]) {
                    FavourBox();
                    translate([0, favour_box_length + 10, 0]) {
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

module TestBox() {
  difference() {
    cube([110, 50, 6]);
    translate([trading_post_barn_width / 2 + 2, trading_post_barn_height / 2 + 2, 1]) {
      TradingPostPurple(height=6);
      translate([trading_post_barn_width + 2, 0, 0]) {
        TradingPostGreen(height=6);
        translate([trading_post_barn_width + 2, 0, 0]) {
          TradingPostYellow(height=6);
          translate([trading_post_barn_width + 2, 0, 0]) {
            TradingPostBlack(height=6);
          }
        }
      }
    }
    translate([explorer_hat_width / 2 + 2, trading_post_barn_height + 4 + explorer_marker_height / 2, 1]) {
      ExplorerMarkerPurple(height=6);
      translate([explorer_hat_width + 2, 0, 0]) {
        ExplorerMarkerGreen(height=6);
        translate([explorer_hat_width + 2, 0, 0]) {
          ExplorerMarkerBlack(height=6);
          translate([explorer_hat_width + 2, 0, 0]) {
            ExplorerMarkerYellow(height=6);
            translate([explorer_hat_width + 5, 0, 0]) {
              BirdTurnOrder(height=6);
            }
          }
        }
      }
    }
  }
  translate([112, 0, 0]) difference() {
      cube([favour_tile_width + 4, favour_tile_length + 4, 5]);
      translate([2 + favour_tile_width / 2, 2 + favour_tile_length / 2, 1]) {
        FavourTile(height=6);
      }
    }
}

if (FROM_MAKE != 1) {
  PlayerBoxBlackOne();
  PlayerBoxBlackTwo();
}
