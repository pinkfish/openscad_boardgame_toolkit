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

$fn = 128;

default_lid_shape_type = SHAPE_TYPE_CLOUD;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 12;
default_lid_aspect_ratio = 1.5;
default_wall_thickness = 3;
default_lid_thickness = 2;
default_floor_thickness = 2;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

box_width = 211;
box_length = 268;
box_height = 50;
board_thickness = 4;

card_width = 68;
card_length = 92;

token_thickness = 2;

trading_post_triangle_width = 17.5;
trading_post_triangle_height = 16;
trading_post_triangle_inset_side = 2;
trading_post_triangle_inset_up = 3;

trading_post_white_base = 11;
trading_post_white_base_height = 2;
trading_post_white_height = 15;
trading_post_white_width = 16;
trading_post_white_edge_height = 8;

explorer_white_base_width = 17;
explorer_white_middle_width = 15;
explorer_white_triangle_width = 18.5;
explorer_white_triangle_height = 12;
explorer_white_height = 21.5;

faction_skill_width = 60;
faction_skill_main_length = 71;
faction_skill_arrow_length = 5;
num_faction_tiles = 9;

exploration_tiles_width = 34;
exploration_tiles_length = 42;

start_order_oval_width = 61;
start_order_oval_length = 92;
start_order_top_bump = 44;
start_order_bump_radius = 5;
start_order_bottom_bump = 20;
start_order_bottom_bump_diff = 3;

player_overlay_length = 120;
player_overlay_width = 73;

specied_token_diameter = 25;

bits_box_width = box_width - player_box_width - 2;
bits_box_length = faction_skill_main_length * 2 + default_wall_thickness * 3 + 1;
bits_box_height = default_lid_thickness + default_floor_thickness + marker_thickness + 1;

tokens_box_height = box_height - player_box_height - 1;
tokens_box_width = player_box_width;
tokens_box_length = player_box_length;

faction_skill_box_width = faction_skill_width + default_wall_thickness * 2 + 1;
faction_skill_box_length = bits_box_length;
faction_skill_box_height = box_height - bits_box_height - board_thickness - 1;

filler_box_width = bits_box_width - faction_skill_box_width;
filler_box_length = bits_box_length;
filler_box_height = faction_skill_box_height;

card_box_width = box_width - player_box_width - 2;
card_box_length = box_length - faction_skill_box_length - 2;
card_box_height = box_height - board_thickness - 1;

module TradingPostWhite(height) {
  module OneSide() {
    stroke(
      bezier_curve(
        [
          [
            trading_post_white_base / 2 - 0.5,
            trading_post_white_height / 2 - trading_post_white_base_height - 0.5,
          ],
          [
            trading_post_white_base / 2 + 3,
            trading_post_white_height / 2 - trading_post_white_edge_height + 5,
          ],
          [
            trading_post_white_width / 2 - 0.5,
            trading_post_white_height / 2 - trading_post_white_edge_height + 0.5,
          ],
        ],
        10
      ),
      width=1
    );

    stroke(
      bezier_curve(
        [
          [
            trading_post_white_width / 2 - 0.5,
            trading_post_white_height / 2 - trading_post_white_edge_height + 0.5,
          ],
          [
            trading_post_white_base / 2 - 1,
            trading_post_white_height / 2 - trading_post_white_edge_height + 3.5,
          ],
          [0, -trading_post_white_height / 2 + 0.5],
        ],
        20
      ),
      width=1
    );
  }

  hull() {
    translate([0, trading_post_white_height / 2, 0]) {
      translate([trading_post_white_base / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + RIGHT + BACK);
      translate([-trading_post_white_base / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + LEFT + BACK);
    }
    translate([0, trading_post_white_height / 2 - trading_post_white_base_height, 0]) {
      translate([trading_post_white_base / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + RIGHT + BACK);
      translate([-trading_post_white_base / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + LEFT + BACK);
    }
  }
  linear_extrude(height=height) fill() {
      OneSide();
      mirror([1, 0, 0]) OneSide();
      stroke(
        [
          [trading_post_white_base / 2 - 0.5, trading_post_white_height / 2 - trading_post_white_base_height - 0.5],
          [
            -trading_post_white_base / 2 + 0.5,
            trading_post_white_height / 2 - trading_post_white_base_height - 0.5,
          ],
        ],
        width=1
      );
    }
}

module ExplorerMarkerWhite(height) {
  hull() {
    translate([0, -explorer_white_height / 2, 0]) {
      translate([explorer_white_base_width / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + RIGHT);
      translate([-explorer_white_base_width / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + LEFT);
    }
    translate([0, explorer_white_height / 2 - explorer_white_triangle_height, 0]) {

      translate([explorer_white_middle_width / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + RIGHT);
      translate([-explorer_white_middle_width / 2, 0, 0]) cyl(h=height, d=1, anchor=BOTTOM + LEFT);
    }
  }
  hull() {
    translate([0, explorer_white_height / 2 - explorer_white_triangle_height, 0]) {
      translate([-explorer_white_triangle_width / 2, 0, 0])
        cyl(h=height, d=2, anchor=BOTTOM + LEFT + FRONT);
      translate([explorer_white_triangle_width / 2, 0, 0])
        cyl(h=height, d=2, anchor=BOTTOM + RIGHT + FRONT);
    }
    translate([0, explorer_white_height / 2, 0]) cyl(h=height, d=1, anchor=BOTTOM + BACK);
  }
}

module StartOvalFrom(height, offset = 0) {
  linear_extrude(height=height) offset(delta=offset) resize([start_order_oval_length, start_order_oval_width])
        polygon(
          bezpath_curve(
            [
              [361.51, 137.88],
              [361.51, 137.88],
              [361.49, 137.82],
              [361.48, 137.78],
              [361.01, 135.13],
              [360.41, 132.51],
              [359.68, 129.92],
              [357.7, 117.54999999999998],
              [359.95, 107.24999999999999],
              [361.5, 102.14999999999999],
              [362.56, 100.57],
              [363.18, 98.67999999999999],
              [363.18, 96.63],
              [363.18, 91.17],
              [358.76, 86.75],
              [353.3, 86.75],
              [352.5, 86.75],
              [351.73, 86.86],
              [350.98, 87.04],
              [343.14000000000004, 85.72000000000001],
              [330.66, 83.22000000000001],
              [326.37, 80.11000000000001],
              [326.37, 80.11000000000001],
              [326.36, 80.11000000000001],
              [326.35, 80.09000000000002],
              [298.95000000000005, 56.13000000000002],
              [258.16, 39.19000000000002],
              [211.3, 34.070000000000014],
              [203.95000000000002, 31.780000000000015],
              [196.83, 26.850000000000016],
              [193.0, 22.620000000000015],
              [192.53, 21.830000000000016],
              [191.96, 21.110000000000014],
              [191.3, 20.480000000000015],
              [191.3, 20.480000000000015],
              [191.3, 20.470000000000013],
              [191.29000000000002, 20.460000000000015],
              [191.29000000000002, 20.460000000000015],
              [191.29000000000002, 20.460000000000015],
              [191.29000000000002, 20.460000000000015],
              [189.52, 18.790000000000013],
              [187.14000000000001, 17.760000000000016],
              [184.51000000000002, 17.760000000000016],
              [181.65, 17.760000000000016],
              [179.08, 18.980000000000015],
              [177.28000000000003, 20.920000000000016],
              [175.05000000000004, 23.150000000000016],
              [165.06000000000003, 32.920000000000016],
              [160.40000000000003, 33.23000000000002],
              [160.40000000000003, 33.23000000000002],
              [160.49000000000004, 33.23000000000002],
              [160.49000000000004, 33.23000000000002],
              [160.49000000000004, 33.23000000000002],
              [160.41000000000003, 33.23000000000002],
              [160.37000000000003, 33.240000000000016],
              [160.37000000000003, 33.240000000000016],
              [160.40000000000003, 33.240000000000016],
              [160.40000000000003, 33.240000000000016],
              [151.55000000000004, 34.08000000000002],
              [143.55000000000004, 25.180000000000014],
              [134.71000000000004, 14.970000000000017],
              [132.95000000000005, 12.220000000000017],
              [130.79000000000005, 9.760000000000016],
              [128.31000000000003, 7.660000000000017],
              [128.31000000000003, 7.660000000000017],
              [128.30000000000004, 7.650000000000017],
              [128.29000000000002, 7.640000000000017],
              [128.29000000000002, 7.640000000000017],
              [128.29000000000002, 7.640000000000017],
              [128.29000000000002, 7.640000000000017],
              [122.64000000000001, 2.870000000000018],
              [115.34000000000002, -0.009999999999982911],
              [107.37000000000002, -0.009999999999982911],
              [101.00000000000001, -0.009999999999982911],
              [95.07000000000002, 1.8300000000000172],
              [90.06000000000002, 5.000000000000017],
              [58.170000000000016, 23.930000000000017],
              [56.95000000000002, 64.99000000000002],
              [47.52000000000002, 71.28000000000002],
              [47.52000000000002, 71.28000000000002],
              [47.52000000000002, 71.28000000000002],
              [47.52000000000002, 71.28000000000002],
              [46.990000000000016, 71.66000000000001],
              [46.460000000000015, 72.05000000000001],
              [45.94000000000002, 72.44000000000001],
              [45.94000000000002, 72.44000000000001],
              [45.94000000000002, 72.42000000000002],
              [45.94000000000002, 72.42000000000002],
              [36.98000000000002, 79.59000000000002],
              [13.700000000000017, 80.82000000000002],
              [13.700000000000017, 80.82000000000002],
              [8.240000000000016, 80.82000000000002],
              [3.8200000000000163, 85.24000000000002],
              [3.8200000000000163, 90.70000000000002],
              [3.8200000000000163, 91.47000000000001],
              [3.9200000000000164, 92.22000000000001],
              [4.090000000000016, 92.94000000000001],
              [5.160000000000016, 103.11000000000001],
              [5.150000000000016, 119.46000000000001],
              [2.880000000000016, 130.60000000000002],
              [2.530000000000016, 131.87000000000003],
              [2.230000000000016, 133.15000000000003],
              [1.940000000000016, 134.44000000000003],
              [1.930000000000016, 134.48000000000002],
              [1.920000000000016, 134.53000000000003],
              [1.900000000000016, 134.57000000000002],
              [1.900000000000016, 134.57000000000002],
              [1.900000000000016, 134.55],
              [1.900000000000016, 134.55],
              [0.6700000000000159, 140.19],
              [0.020000000000016005, 145.96],
              [0.020000000000016005, 151.82000000000002],
              [0.020000000000016005, 186.74],
              [22.80000000000002, 218.16000000000003],
              [59.12000000000002, 239.99],
              [59.12000000000002, 239.99],
              [59.09000000000002, 239.99],
              [59.09000000000002, 239.99],
              [62.98000000000002, 242.25],
              [68.84000000000002, 253.70000000000002],
              [68.84000000000002, 253.70000000000002],
              [68.84000000000002, 253.70000000000002],
              [68.84000000000002, 253.70000000000002],
              [68.84000000000002, 253.70000000000002],
              [70.51000000000002, 256.81],
              [73.78000000000002, 258.92],
              [77.55000000000001, 258.92],
              [78.98000000000002, 258.92],
              [80.34000000000002, 258.61],
              [81.57000000000001, 258.06],
              [81.57000000000001, 258.06],
              [81.57000000000001, 258.06],
              [81.57000000000001, 258.06],
              [81.57000000000001, 258.06],
              [89.42, 255.5],
              [93.52000000000001, 256.29],
              [93.52000000000001, 256.29],
              [93.44000000000001, 256.25],
              [93.44000000000001, 256.25],
              [119.49000000000001, 265.77],
              [149.47000000000003, 271.2],
              [181.38, 271.2],
              [207.82, 271.2],
              [232.94, 267.46999999999997],
              [255.6, 260.78],
              [255.6, 260.78],
              [255.59, 260.78],
              [255.59, 260.78],
              [262.79, 259.83],
              [275.22, 263.21999999999997],
              [283.68, 261.58],
              [287.25, 261.58],
              [290.36, 259.69],
              [292.1, 256.84999999999997],
              [297.24, 249.27999999999997],
              [307.41, 239.48999999999995],
              [316.91, 231.14999999999998],
              [316.91, 231.14999999999998],
              [316.87, 231.17],
              [316.87, 231.17],
              [345.4, 210.07999999999998],
              [362.75, 182.27999999999997],
              [362.75, 151.82],
              [362.75, 147.7],
              [362.43, 143.63],
              [361.81, 139.60999999999999],
              [361.86, 139.29],
              [361.78000000000003, 138.72],
              [361.52, 137.85999999999999],
            ]
          )
        );
}

module PlayerOverlay(height, offset = 0) {
  linear_extrude(height=height) offset(delta=offset) resize([player_overlay_length, player_overlay_width])
        polygon(
          bezpath_curve(
            [
              [468.93, 173.12],
              [468.93, 173.12],
              [468.93, 173.12],
              [468.93, 173.12],
              [468.93, 173.12],
              [468.90000000000003, 173.08],
              [468.88, 173.06],
              [467.86, 171.8],
              [466.77, 170.59],
              [465.6, 169.46],
              [448.15000000000003, 149.34],
              [451.31, 135.34],
              [443.61, 122.98000000000002],
              [438.79, 115.24000000000002],
              [417.46000000000004, 104.41000000000003],
              [417.46000000000004, 104.41000000000003],
              [402.76000000000005, 96.64000000000003],
              [369.56000000000006, 91.21000000000002],
              [353.90000000000003, 77.83000000000003],
              [352.87000000000006, 76.69000000000003],
              [351.76000000000005, 75.62000000000003],
              [350.6, 74.60000000000002],
              [350.6, 74.60000000000002],
              [350.59000000000003, 74.59000000000002],
              [350.58000000000004, 74.58000000000003],
              [350.58000000000004, 74.58000000000003],
              [350.58000000000004, 74.58000000000003],
              [350.58000000000004, 74.58000000000003],
              [343.52000000000004, 68.40000000000003],
              [334.28000000000003, 64.65000000000003],
              [324.17, 64.65000000000003],
              [323.44, 64.65000000000003],
              [322.71000000000004, 64.67000000000003],
              [321.99, 64.71000000000004],
              [321.99, 64.71000000000004],
              [321.81, 64.65000000000003],
              [321.81, 64.65000000000003],
              [307.12, 64.65000000000003],
              [293.04, 66.00000000000003],
              [286.17, 61.84000000000003],
              [285.79, 61.56000000000003],
              [285.41, 61.290000000000035],
              [285.02000000000004, 61.02000000000003],
              [284.97, 60.98000000000003],
              [284.91, 60.95000000000003],
              [284.86, 60.91000000000003],
              [284.86, 60.91000000000003],
              [284.86, 60.91000000000003],
              [284.86, 60.91000000000003],
              [278.42, 56.50000000000003],
              [270.63, 53.92000000000003],
              [262.23, 53.92000000000003],
              [260.20000000000005, 53.92000000000003],
              [258.21000000000004, 54.07000000000003],
              [256.27000000000004, 54.36000000000003],
              [256.27000000000004, 54.36000000000003],
              [256.27000000000004, 54.36000000000003],
              [256.27000000000004, 54.36000000000003],
              [227.16000000000003, 58.00000000000003],
              [226.57000000000005, 60.410000000000025],
              [196.40000000000003, 26.670000000000027],
              [193.45000000000005, 22.330000000000027],
              [189.94000000000003, 18.400000000000027],
              [186.00000000000003, 14.970000000000027],
              [185.97000000000003, 14.940000000000028],
              [185.94000000000003, 14.910000000000027],
              [185.91000000000003, 14.870000000000028],
              [185.91000000000003, 14.870000000000028],
              [185.91000000000003, 14.900000000000027],
              [185.91000000000003, 14.900000000000027],
              [175.22000000000003, 5.620000000000028],
              [161.28000000000003, -0.009999999999973141],
              [146.01000000000002, -0.009999999999973141],
              [130.74, -0.009999999999973141],
              [117.76000000000002, 5.220000000000027],
              [107.23000000000002, 13.930000000000026],
              [107.23000000000002, 13.930000000000026],
              [107.23000000000002, 13.930000000000026],
              [107.23000000000002, 13.930000000000026],
              [90.92000000000002, 25.700000000000024],
              [72.21000000000001, 47.370000000000026],
              [45.100000000000016, 46.03000000000003],
              [43.860000000000014, 45.87000000000003],
              [42.600000000000016, 45.760000000000026],
              [41.33000000000001, 45.71000000000003],
              [41.210000000000015, 45.690000000000026],
              [41.09000000000001, 45.690000000000026],
              [40.97000000000001, 45.67000000000003],
              [40.97000000000001, 45.67000000000003],
              [40.990000000000016, 45.70000000000003],
              [40.990000000000016, 45.70000000000003],
              [40.600000000000016, 45.69000000000003],
              [40.20000000000002, 45.67000000000003],
              [39.81000000000002, 45.67000000000003],
              [17.82, 45.68],
              [0.0, 63.5],
              [0.0, 85.49],
              [0.0, 97.06],
              [4.94, 107.47],
              [12.81, 114.74],
              [18.57, 121.07],
              [24.94, 126.25999999999999],
              [28.12, 132.04999999999998],
              [24.73, 136.70999999999998],
              [18.1, 147.29999999999998],
              [16.66, 155.36999999999998],
              [16.66, 155.36999999999998],
              [16.66, 155.36999999999998],
              [16.66, 155.36999999999998],
              [14.780000000000001, 159.98999999999998],
              [13.73, 165.04999999999998],
              [13.73, 170.34999999999997],
              [13.73, 189.00999999999996],
              [26.57, 204.65999999999997],
              [43.89, 208.97999999999996],
              [43.89, 208.97999999999996],
              [43.89, 208.97999999999996],
              [43.89, 208.97999999999996],
              [44.05, 209.02999999999997],
              [44.24, 209.06999999999996],
              [44.43, 209.09999999999997],
              [47.36, 209.78999999999996],
              [50.41, 210.15999999999997],
              [53.55, 210.15999999999997],
              [55.349999999999994, 210.15999999999997],
              [57.12, 210.02999999999997],
              [58.86, 209.79999999999995],
              [62.9, 210.00999999999996],
              [66.65, 210.43999999999994],
              [68.63, 211.52999999999994],
              [67.39, 216.74999999999994],
              [62.74999999999999, 220.70999999999995],
              [60.3, 225.88999999999993],
              [60.3, 225.88999999999993],
              [60.3, 225.88999999999993],
              [60.3, 225.88999999999993],
              [57.32, 231.46999999999994],
              [55.62, 237.83999999999992],
              [55.62, 244.60999999999993],
              [55.62, 266.5999999999999],
              [73.44, 284.41999999999996],
              [95.43, 284.41999999999996],
              [97.67, 284.41999999999996],
              [99.86000000000001, 284.22999999999996],
              [101.99000000000001, 283.86999999999995],
              [125.91000000000001, 282.65999999999997],
              [168.03000000000003, 287.36999999999995],
              [192.92000000000002, 284.41999999999996],
              [242.36, 256.60999999999996],
              [300.52, 261.12999999999994],
              [343.35, 269.12999999999994],
              [363.72, 260.67999999999995],
              [410.71000000000004, 257.35999999999996],
              [430.32000000000005, 254.91999999999993],
              [431.33000000000004, 254.81999999999994],
              [432.34000000000003, 254.67999999999992],
              [433.33000000000004, 254.51999999999992],
              [433.37000000000006, 254.51999999999992],
              [433.43000000000006, 254.50999999999993],
              [433.47, 254.49999999999991],
              [433.47, 254.49999999999991],
              [433.47, 254.49999999999991],
              [433.47, 254.49999999999991],
              [451.71000000000004, 251.45999999999992],
              [466.39000000000004, 237.9399999999999],
              [471.11, 220.32999999999993],
              [475.3, 213.98999999999992],
              [477.74, 206.39999999999992],
              [477.74, 198.22999999999993],
              [477.74, 188.72999999999993],
              [474.43, 179.99999999999994],
              [468.91, 173.11999999999995],
            ]
          )
        );
}

module PlayerBoxWhiteOne() // `make` me
{
  PlayerBoxOneBase(generate_lid=false, material_colour="white") {
    rotate([0, 0, 90]) color("white") TradingPostWhite(marker_thickness + 1);
    rotate([0, 0, -90]) color("white") TradingPostWhite(marker_thickness + 1);
  }
}

module PlayerBoxWhiteOneLid() // `make` me
{
  PlayerBoxOneBase(generate_lid=true, material_colour="white") {
    rotate([0, 0, 90]) color("white") TradingPostWhite(marker_thickness + 1);
    rotate([0, 0, -90]) color("white") TradingPostWhite(marker_thickness + 1);
  }
}

module PlayerBoxWhiteTwo() // `make` me
{
  PlayerBoxTwoBase(generate_lid=false, material_colour="white") {
    rotate([0, 0, 90]) color("white") ExplorerMarkerWhite(marker_thickness + 1);
    rotate([0, 0, -90]) color("white") ExplorerMarkerWhite(marker_thickness + 1);
  }
}

module PlayerBoxWhiteTwoLid() // `make` me
{
  PlayerBoxTwoBase(generate_lid=true, material_colour="white") {
    rotate([0, 0, 90]) color("white") ExplorerMarkerWhite(marker_thickness + 1);
    rotate([0, 0, -90]) color("white") ExplorerMarkerWhite(marker_thickness + 1);
  }
}

module FactionSkillTiles() {
  MakeBoxWithSlidingLid(
    width=faction_skill_box_width, length=faction_skill_box_length,
    height=faction_skill_box_height
  ) {
    cuboid(
      [faction_skill_width + 1, faction_skill_main_length + 0.5, $inner_height + 1],
      anchor=BOTTOM + FRONT + LEFT
    );
    linear_extrude(height=$inner_height + 1) polygon(
        [
          [0, faction_skill_main_length - 0.49],
          [faction_skill_width / 2, faction_skill_main_length + faction_skill_arrow_length],
          [faction_skill_width, faction_skill_main_length - 0.49],
        ]
      );
    difference() {
      translate([0, $inner_length, 0])
        cuboid(
          [faction_skill_width + 1, faction_skill_main_length + 0.5, $inner_height + 1],
          anchor=BOTTOM + BACK + LEFT
        );
      linear_extrude(height=$inner_height + 1) polygon(
          [
            [0, faction_skill_main_length - 0.01 + default_wall_thickness - 0.5],
            [
              faction_skill_width / 2,
              faction_skill_main_length + faction_skill_arrow_length + default_wall_thickness - 0.5,
            ],
            [faction_skill_width, faction_skill_main_length - 0.01 + default_wall_thickness - 0.5],
          ]
        );
    }

    translate([$inner_width / 2, 0, -default_lid_thickness - default_floor_thickness - 0.99])
      FingerHoleBase(radius=15, height=faction_skill_box_height + 1);
    translate([$inner_width / 2, $inner_length, -default_lid_thickness - 0.99])
      FingerHoleBase(radius=15, height=faction_skill_box_height + 1, spin=180);
    translate([$inner_width / 2, $inner_length / 2 + 3, 0]) FingerHoleWall(
        radius=15, height=faction_skill_box_height - default_lid_thickness - default_floor_thickness + 0.01,
        depth_of_hole=10
      );
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
    text_str="Cards"
  );
}

module BitsBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=bits_box_width, length=bits_box_length, height=bits_box_height,
    lid_on_length=true
  ) {
    PlayerOverlay(bits_box_height);
    translate([start_order_oval_width, 0, $inner_height - token_thickness - 1]) rotate([0, 0, 90])
        StartOvalFrom(100);
    translate(
      [
        $inner_width - exploration_tiles_width / 2 - 13,
        $inner_length - exploration_tiles_width / 2 - 5,
        $inner_height - token_thickness * 2 - 0.9,
      ]
    ) CuboidWithIndentsBottom(
        [exploration_tiles_width, exploration_tiles_length, token_thickness * 2 + 1],
        finger_holes=[0, 4], finger_hole_radius=20
      );
    translate(
      [
        $inner_width - exploration_tiles_width * 3 / 2 - 20,
        $inner_length - exploration_tiles_width / 2 - 5,
        $inner_height - token_thickness * 2 - 0.9,
      ]
    ) CuboidWithIndentsBottom(
        [exploration_tiles_width, exploration_tiles_length, token_thickness * 2 + 1],
        finger_holes=[0, 4], finger_hole_radius=20
      );
    translate(
      [
        $inner_width - exploration_tiles_width * 5 / 2 - 27,
        $inner_length - exploration_tiles_width / 2 - 5,
        $inner_height - token_thickness * 2 - 0.9,
      ]
    ) CuboidWithIndentsBottom(
        [exploration_tiles_width, exploration_tiles_length, token_thickness * 2 + 1],
        finger_holes=[0, 4], finger_hole_radius=20
      );

    translate([$inner_width - specied_token_diameter, specied_token_diameter / 2, 0.5])
      CylinderWithIndents(
        radius=specied_token_diameter / 2, height=marker_thickness + 1,
        finger_holes=[0, 180], finger_hole_radius=10
      );
    translate([$inner_width - specied_token_diameter, specied_token_diameter * 7 / 2, 0.5])
      CylinderWithIndents(
        radius=specied_token_diameter / 2, height=marker_thickness + 1,
        finger_holes=[0, 180], finger_hole_radius=10
      );
    translate([$inner_width - specied_token_diameter * 2 - 4, specied_token_diameter * 7 / 2, 0.5])
      CylinderWithIndents(
        radius=specied_token_diameter / 2, height=marker_thickness + 1,
        finger_holes=[0, 180], finger_hole_radius=10
      );
    translate([$inner_width - specied_token_diameter / 2, specied_token_diameter * 3 / 2, 0.5])
      CylinderWithIndents(
        radius=specied_token_diameter / 2, height=marker_thickness + 1,
        finger_holes=[80, 270], finger_hole_radius=10
      );
  }
}

module BitsBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=bits_box_width, length=bits_box_length,
    text_str="Navoria"
  );
}

module TokensBox() // `make` me
{
  MakeBoxWithSlidingLid(width=tokens_box_width, length=tokens_box_length, height=tokens_box_height) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=tokens_box_height, radius=5);
  }
}

module TokensBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=tokens_box_width, length=tokens_box_length,
    text_str="Solo"
  );
  translate([tokens_box_width + 5, 0, 0]) SlidingBoxLidWithLabel(
      width=tokens_box_width, length=tokens_box_length, text_str="Contract"
    );
}

module SpacerBox() // `make` me
{
  color("purple") translate([filler_box_width / 2, filler_box_length / 2, filler_box_height / 2]) difference() {
        cuboid([filler_box_width, filler_box_length, filler_box_height], rounding=2);
        translate([0, 0, default_floor_thickness]) cuboid(
            [
              filler_box_width - default_wall_thickness * 2,
              filler_box_length - default_wall_thickness * 2,
              filler_box_height,
            ]
          );
      }
}

module BoxLayout() {
  cube([1, box_length, expansion_box_height]);

  //    translate([ box_width - player_layout_width, 0, expansion_box_height - player_layout_thickness ])
  // cube([ player_layout_width, box_length, player_layout_thickness * player_layout_num ]);

  PlayerBoxWhiteOne();
  translate([0, player_box_length, 0]) PlayerBoxWhiteTwo();
  translate([0, 0, player_box_height]) TokensBox();
  translate([0, player_box_length, player_box_height]) TokensBox();
  translate([player_box_width, 0, 0]) BitsBox();
  translate([player_box_width, 0, bits_box_height]) FactionSkillTiles();
  translate([player_box_width + faction_skill_box_width, 0, bits_box_height]) SpacerBox();

  translate([player_box_width, faction_skill_box_length, 0]) CardBox();
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
