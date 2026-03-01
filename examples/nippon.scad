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

box_width = 303;
box_length = 380;
box_height = 70;

board_thickness = 9;
board_width = 205;
board_length = 306;

player_board_thickness = 4.3;
player_board_width = 235;
player_board_length = 345;

player_handbook_thickness = 6;
player_handbook_length = 233;
player_handbook_width = 103;

cube_size = 11;

cardboard_token_thickness = 2.5;

track_marker_cylinder_diameter = 10.5;
track_marker_cylinder_length = 14;

scoring_disk_diameter = 15.5;
scoring_disk_thickness = 6.5;

round_marker_diameter = 12;
round_marker_length = 16;

expert_worker_width = 16.5;
expert_worker_thickness = 7;

machine_diameter = 15.5;
machine_thickness = 6;

ship_length = 21;
ship_width = 13.5;
ship_thickness = 10;

train_length = 21;
train_width = 13.5;

worker_length = 18.5;
worker_width = 14.5;
worker_thickness = 10;

upgrade_token_width = 16;

favour_token_width = 16;
favour_token_corner = 3;

influence_token_width = 16;
influence_token_middle_size = 5;

factory_token_width = 57;
factory_token_length = 57;

demand_token_width = 42;
demand_token_length = 42;

money_token_length = 32;
money_token_width = 17;
money_token_corner = 3;

contract_token_width = 21;
contract_token_length = 41;

automata_board_width = 121;
automata_board_length = 182;

solo_goal_token_width = 22;
solo_goal_token_length = 31;
solo_goal_token_edge = 2.5;

starting_token_width = 32;
starting_token_length = 42;
old_factory_tile_width = 51;
old_factory_tile_length = 57;

action_token_width = 26;
action_token_length = 41;

space_left = box_height - board_thickness - player_board_thickness * 4 - player_handbook_thickness;

player_box_width = box_width / 4;
player_box_height = default_floor_thickness + default_lid_thickness + 1 + ship_thickness;
player_box_length = 92;

player_box_bits_width = box_width / 2;
player_box_bits_height = (space_left - player_box_height) / 2;
player_box_bits_length = 92;

factory_tile_box_width = default_wall_thickness * 2 + factory_token_width + 1;
factory_tile_box_length = default_wall_thickness * 2 + factory_token_length + 1;
factory_tile_box_height = space_left;

demand_tile_box_width = default_wall_thickness * 2 + demand_token_width + 1;
demand_tile_box_length = factory_tile_box_length;
demand_tile_box_height = factory_tile_box_height;

starting_tile_box_width = default_wall_thickness * 2 + old_factory_tile_width + 1;
starting_tile_box_length = factory_tile_box_length;
starting_tile_box_height = factory_tile_box_height;

upgraded_tile_box_width = box_width - starting_tile_box_width - demand_tile_box_width - factory_tile_box_width * 2;
upgraded_tile_box_length = factory_tile_box_length;
upgraded_tile_box_height = cardboard_token_thickness * (24 / 6) + default_floor_thickness + default_lid_thickness;

money_box_width = upgraded_tile_box_width;
money_box_length = upgraded_tile_box_length;
money_box_height = space_left - upgraded_tile_box_height;

solo_box_width = 89;
solo_box_length = upgraded_tile_box_length;
solo_box_height = default_floor_thickness + default_lid_thickness + 1 + cardboard_token_thickness * 5;

late_game_factory_box_width = default_wall_thickness * 2 + factory_token_width + 1;
late_game_factory_box_length = solo_box_length;
late_game_factory_box_height = space_left - solo_box_height;

round_marker_box_width = solo_box_width - late_game_factory_box_width - 0.5;
round_marker_box_length = solo_box_length;
round_marker_box_height = space_left - solo_box_height;

worker_box_width = (box_width - solo_box_width - 1) / 3;
worker_box_length = upgraded_tile_box_length;
worker_box_height = space_left / 2;

resource_box_width = default_wall_thickness * 2 + cube_size * 8 + 24;
resource_box_length = default_wall_thickness * 2 + cube_size * 3 + 2;
resource_box_height = space_left / 2;
resource_box_double_width = box_width - resource_box_width;

front_spacer_width = box_width;
front_spacer_length = box_length - solo_box_length - factory_tile_box_length - player_box_length - resource_box_length;
front_spacer_height = factory_tile_box_height;

module TrainItem() {
  bez = [
    [573.58, 244.28],
    [527.58, 245.81],
    [463.35, 230.55],
    [427.07000000000005, 262.87],
    [410.33000000000004, 277.79],
    [406.40000000000003, 279.12],
    [395.74000000000007, 295.58],
    [389.87000000000006, 304.65],
    [378.76000000000005, 321.51],
    [368.2300000000001, 330.53],
    [334.36000000000007, 337.73999999999995],
    [246.82000000000008, 336.96999999999997],
    [242.2100000000001, 334.88],
    [205.4900000000001, 318.27],
    [272.1200000000001, 239.85],
    [188.72000000000008, 242.32],
    [143.92000000000007, 237.26999999999998],
    [145.48000000000008, 288.33],
    [153.0600000000001, 315.4],
    [148.1400000000001, 342.66999999999996],
    [138.29000000000008, 368.92999999999995],
    [137.23000000000008, 397.96],
    [131.71000000000006, 402.78999999999996],
    [116.89000000000007, 397.58],
    [110.22000000000007, 400.46999999999997],
    [104.17000000000007, 403.09],
    [102.83000000000007, 406.65],
    [101.25000000000007, 409.38],
    [84.88000000000007, 437.71],
    [113.13000000000007, 514.52],
    [138.87000000000006, 534.72],
    [159.22000000000006, 550.69],
    [228.08000000000004, 544.51],
    [241.61000000000007, 547.0600000000001],
    [268.4200000000001, 543.58],
    [515.25, 544.6],
    [530.8100000000001, 543.5300000000001],
    [564.0400000000001, 541.2400000000001],
    [591.33, 528.1200000000001],
    [591.33, 484.11000000000007],
    [603.0300000000001, 424.44000000000005],
    [595.7700000000001, 364.6400000000001],
    [597.58, 305.37000000000006],
    [598.4200000000001, 277.87000000000006],
    [601.45, 247.27000000000007],
    [573.59, 244.28000000000006],
  ];
  min_x = min([for (i = bez) i[0]]);
  max_x = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[1]]);
  max_y = max([for (i = bez) i[1]]);
  resize([train_length, train_width])
    translate([-max_x + (max_x - min_x) / 2, -max_y + ( (max_y - min_y) / 2)])
      polygon(bezpath_curve(bez));
}

module ShipItem() {
  bez = [
    [245.74, 247.34],
    [232.95000000000002, 256.1],
    [218.21, 297.03],
    [206.59, 310.93],
    [176.82, 317.40000000000003],
    [117.11, 383.06],
    [117.11, 383.06],
    [117.11, 383.06],
    [95.0, 383.93],
    [91.78, 397.45],
    [89.03, 408.99],
    [143.22, 493.15999999999997],
    [152.4, 497.58],
    [157.95000000000002, 500.26],
    [482.85, 502.55],
    [495.73, 496.03999999999996],
    [516.57, 482.09999999999997],
    [533.5500000000001, 455.89],
    [541.3100000000001, 433.73999999999995],
    [538.4100000000001, 398.28],
    [518.2800000000001, 325.64],
    [498.69000000000005, 295.14],
    [495.74000000000007, 290.55],
    [485.8500000000001, 283.71999999999997],
    [476.90000000000003, 294.5],
    [463.16, 311.04],
    [453.1, 376.13],
    [453.1, 376.13],
    [453.1, 376.13],
    [428.36, 269.81],
    [409.74, 237.89],
    [403.3, 226.85],
    [397.29, 226.70999999999998],
    [389.69, 243.35999999999999],
    [378.16, 268.62],
    [369.36, 327.27],
    [366.96, 352.08],
    [358.76, 343.89],
    [344.96999999999997, 336.94],
    [332.78999999999996, 342.0],
    [329.46999999999997, 324.34],
    [327.84, 291.07],
    [322.95, 273.3],
    [318.06, 255.53000000000003],
    [286.66999999999996, 181.29000000000002],
    [245.74, 247.33],
  ];
  min_x = min([for (i = bez) i[0]]);
  max_x = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[1]]);
  max_y = max([for (i = bez) i[1]]);
  offset(0.5)
    resize([ship_length - 1, ship_width - 1])
      translate([-max_x + (max_x - min_x) / 2, -max_y + ( (max_y - min_y) / 2)])
        polygon(bezpath_curve(bez));
}

module WorkerItem() {
  bez = [
    [399.0, 488.74],
    [399.0, 488.74],
    [398.72, 462.86],
    [368.34, 466.24],
    [366.09, 442.05],
    [358.5, 400.99],
    [354.56, 377.65],
    [354.26, 375.87],
    [354.84, 371.46],
    [354.84, 371.46],
    [354.84, 371.46],
    [360.78999999999996, 365.22999999999996],
    [368.04999999999995, 356.40999999999997],
    [374.34, 350.35999999999996],
    [380.21999999999997, 342.78999999999996],
    [385.59, 332.16999999999996],
    [390.42999999999995, 324.10999999999996],
    [393.89, 316.22999999999996],
    [393.92999999999995, 310.14],
    [394.19999999999993, 269.61],
    [327.85999999999996, 228.56],
    [307.13999999999993, 222.95],
    [313.94999999999993, 208.38],
    [329.7299999999999, 178.31],
    [327.41999999999996, 173.17],
    [327.31999999999994, 172.95999999999998],
    [327.21999999999997, 172.76],
    [327.11999999999995, 172.54999999999998],
    [327.28999999999996, 172.07999999999998],
    [327.43999999999994, 171.63],
    [327.55999999999995, 171.20999999999998],
    [324.3299999999999, 163.42],
    [316.78999999999996, 156.96999999999997],
    [306.8999999999999, 152.23],
    [294.8999999999999, 145.82999999999998],
    [279.80999999999995, 143.01],
    [264.7699999999999, 143.17999999999998],
    [249.72999999999993, 143.01],
    [234.63999999999993, 145.82999999999998],
    [222.63999999999993, 152.23],
    [212.74999999999994, 156.97],
    [205.20999999999992, 163.42],
    [201.97999999999993, 171.20999999999998],
    [202.09999999999994, 171.62999999999997],
    [202.24999999999994, 172.07999999999998],
    [202.41999999999993, 172.54999999999998],
    [202.31999999999994, 172.76],
    [202.20999999999992, 172.95999999999998],
    [202.11999999999992, 173.17],
    [199.80999999999992, 178.30999999999997],
    [215.58999999999992, 208.38],
    [222.39999999999992, 222.95],
    [201.67999999999992, 228.56],
    [135.33999999999992, 269.61],
    [135.6099999999999, 310.14],
    [135.6499999999999, 316.22999999999996],
    [139.1099999999999, 324.11],
    [143.9499999999999, 332.16999999999996],
    [149.3199999999999, 342.78],
    [155.1999999999999, 350.34999999999997],
    [161.4899999999999, 356.4],
    [168.7499999999999, 365.21999999999997],
    [174.6999999999999, 371.45],
    [174.6999999999999, 371.45],
    [174.6999999999999, 371.45],
    [175.27999999999992, 375.84999999999997],
    [174.9799999999999, 377.64],
    [171.0399999999999, 400.97999999999996],
    [163.4499999999999, 442.04999999999995],
    [161.1999999999999, 466.23],
    [130.8199999999999, 462.85],
    [130.5399999999999, 488.73],
    [130.5399999999999, 488.73],
    [133.3499999999999, 496.61],
    [133.3499999999999, 496.61],
    [135.4799999999999, 500.27000000000004],
    [137.9799999999999, 500.27000000000004],
    [161.3699999999999, 500.27000000000004],
    [227.4099999999999, 498.24000000000007],
    [227.4099999999999, 498.24000000000007],
    [264.75999999999993, 424.4100000000001],
    [302.10999999999996, 498.24000000000007],
    [302.10999999999996, 498.24000000000007],
    [368.90999999999997, 500.27000000000004],
    [391.53999999999996, 500.27000000000004],
    [394.41999999999996, 500.27000000000004],
    [396.16999999999996, 496.61],
    [396.16999999999996, 496.61],
    [398.97999999999996, 488.73],
    [398.97999999999996, 488.73],
    [398.97999999999996, 488.73],
  ];
  min_x = min([for (i = bez) i[0]]);
  max_x = max([for (i = bez) i[0]]);
  min_y = min([for (i = bez) i[1]]);
  max_y = max([for (i = bez) i[1]]);
  resize([worker_width, worker_length])
    translate([-max_x + (max_x - min_x) / 2, -max_y + ( (max_y - min_y) / 2)])
      polygon(bezpath_curve(bez));
}

module PlayerBox(material_colour = "yellow") // `make` me
{
  MakeBoxWithCapLid(
    width=player_box_width,
    length=player_box_length,
    height=player_box_height,
    material_colour=material_colour
  ) {
    translate([0, 0, $inner_height - ship_thickness / 2])
      RoundedBoxAllSides(
        width=$inner_width,
        length=$inner_length,
        height=ship_thickness,
        radius=5
      );

    // ships in spaces
    for (i = [0:4]) {
      for (j = [0:1]) {
        if (j != 1 || i < 1) {
          translate(
            [
              3 + (ship_length + 0.5) * j + ship_length / 2,
              (ship_width + 2.4) * i + 5 + ship_width / 2,
              $inner_height - ship_thickness - 0.5,
            ]
          )
            linear_extrude(ship_thickness + 1)
              ShipItem();
          //cuboid([ship_length, ship_width, ship_thickness + 1], anchor=BOTTOM + FRONT + LEFT);
        }
      }
    }

    // trains in spaces
    translate([(ship_length + 0.5) * 1 + 3, 5, 0]) {
      for (i = [0:4]) {
        for (j = [0:1]) {
          if ( (j == 1 || i >= 1) && (j == 0 || i > 2)) {
            translate(
              [
                (train_length + 1) * j + train_length / 2,
                (train_width + 2.4) * i + train_width / 2,
                $inner_height - ship_thickness - 0.5,
              ]
            )
              linear_extrude(ship_thickness + 1)
                TrainItem();
            //cuboid([train_length, train_width, ship_thickness + 1], anchor=BOTTOM + FRONT + LEFT);
          }
        }
      }
      translate([(train_length + 1.5) * 1 + 2, 3, 0]) {
        for (i = [0:2]) {
          translate([0, (track_marker_cylinder_diameter + 2.5) * i, $inner_height - track_marker_cylinder_diameter - 0.5])
            xcyl(d=track_marker_cylinder_diameter + 0.5, h=track_marker_cylinder_length + 1, anchor=BOTTOM + FRONT + LEFT);
        }
      }
    }
  }
}

module PlayerBoxBits(material_colour = "yellow") // `make` me
{
  MakeBoxWithCapLid(
    width=player_box_bits_width,
    length=player_box_bits_length,
    height=player_box_bits_height,
    material_colour=material_colour
  ) {

    // machine disks
    translate([machine_diameter / 2 + 1, 14, $inner_height - machine_thickness - 0.5]) {
      for (i = [0:2]) {
        for (j = [0:1]) {
          translate([(machine_diameter + 1.5) * j, (machine_diameter + 1.5) * i, 0])
            CylinderWithIndents(
              d=machine_diameter, h=machine_thickness * 2 + 1,
              anchor=BOTTOM,
              finger_holes=[90, 270],
              finger_hole_radius=6
            );
        }
      }
    }

    // influence tokens
    translate(
      [
        machine_diameter * 2 + 10,
        2,
        0,
      ]
    ) {
      for (j = [0:4]) {
        for (i = [0:1]) {
          translate(
            [
              (influence_token_width + 1.5) * j,
              (influence_token_width + 2) * i,
              $inner_height - cardboard_token_thickness * (j == 1 || j == 2 ? 2 : 2) - 0.5,
            ]
          ) {
            difference() {
              CuboidWithIndentsBottom(
                [influence_token_width, influence_token_width, cardboard_token_thickness * 8],
                anchor=BOTTOM + FRONT + LEFT,
                finger_holes=[2, 6],
                finger_hole_radius=6.5
              );
              if (j <= 1 || (j == 2 && i == 0)) {
                translate([influence_token_width / 2, 0, 0])
                  rotate(45)
                    cuboid(
                      [influence_token_middle_size, influence_token_middle_size, player_box_height], anchor=BOTTOM,
                      rounding=2, edges=[BACK + RIGHT]
                    );
                translate([influence_token_width / 2, influence_token_width, 0])
                  rotate(45)
                    cuboid(
                      [influence_token_middle_size, influence_token_middle_size, player_box_height], anchor=BOTTOM,
                      rounding=2, edges=[FRONT + LEFT]
                    );
              }
              if (j > 3 && (j == 2 && i == 1)) {
                cyl(d=favour_token_corner, h=player_box_height, anchor=BOTTOM);
                translate([favour_token_width, 0, 0])
                  cyl(d=favour_token_corner, h=player_box_height, anchor=BOTTOM);
                translate([favour_token_width, favour_token_width, 0])
                  cyl(d=favour_token_corner, h=player_box_height, anchor=BOTTOM);
                translate([0, favour_token_width, 0])
                  cyl(d=favour_token_corner, h=player_box_height, anchor=BOTTOM);
              }
            }
          }
        }
      }
    }

    // contract tokens
    for (i = [0:1])
      for (j = [0:1])
        translate(
          [
            machine_diameter * 2 + 15 + ( (contract_token_length + 2) * j),
            $inner_length - contract_token_width * 2 - 5 + (contract_token_width + 2) * i,
            $inner_height - cardboard_token_thickness * (i == 0 ? 2 : 2) - 0.5,
          ]
        ) {
          cuboid(
            [contract_token_length, contract_token_width, cardboard_token_thickness * 10],
            anchor=BOTTOM + LEFT + FRONT
          );
          translate([0, contract_token_width / 2, 0])
            cyl(
              d=contract_token_width - 5, h=100,
              anchor=BOTTOM,
              rounding=(contract_token_width - 5) / 2
            );
          translate([contract_token_length, contract_token_width / 2, 0])
            cyl(
              d=contract_token_width - 5, h=100,
              anchor=BOTTOM,
              rounding=(contract_token_width - 5) / 2
            );
        }

    // scoring disks
    for (i = [0:1]) {
      translate(
        [
          scoring_disk_diameter / 2 + (scoring_disk_diameter + 1) * i + 2,
          $inner_length - scoring_disk_diameter / 2 - 2,
          $inner_height - scoring_disk_thickness - 0.5,
        ]
      )
        CylinderWithIndents(
          d=scoring_disk_diameter,
          h=player_box_height,
          finger_holes=[270],
          finger_hole_radius=8
        );
    }
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width,
    length=player_box_length,
    height=player_box_height,
    text_str="Ships & Trains"
  );
}

module PlayerBoxBitsLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_bits_width,
    length=player_box_bits_length,
    height=player_box_bits_height,
    text_str="Player"
  );
}

module FactoryTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=factory_tile_box_width,
    length=factory_tile_box_length,
    height=factory_tile_box_height
  ) {
    translate([0, 0, $inner_height - cardboard_token_thickness * 12 - 1])
      cuboid([$inner_width, $inner_length, factory_tile_box_height], anchor=BOTTOM + LEFT + FRONT);

    translate([$inner_width / 2, 0, -2]) FingerHoleBase(
        radius=17, height=factory_tile_box_height - default_lid_thickness,
        spin=0
      );
  }
}

module FactoryTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=factory_tile_box_width,
    length=factory_tile_box_length,
    text_str="Factories"
  );
}

module DemandTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=demand_tile_box_width,
    length=demand_tile_box_length,
    height=demand_tile_box_height
  ) {
    translate([0, 0, $inner_height - cardboard_token_thickness * 9 - 1])
      cuboid([demand_token_length, demand_token_width, demand_tile_box_height], anchor=BOTTOM + LEFT + FRONT);

    translate([$inner_width / 2, 0, -2]) FingerHoleBase(
        radius=17, height=factory_tile_box_height - default_lid_thickness,
        spin=0
      );
  }
}

module DemandTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=demand_tile_box_width,
    length=demand_tile_box_length,
    text_str="Demand"
  );
}

module StartingTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=starting_tile_box_width,
    length=starting_tile_box_length,
    height=starting_tile_box_height
  ) {
    translate([$inner_width / 2, 0, $inner_height - cardboard_token_thickness * 11 - 1])
      cuboid([starting_token_width, starting_token_length, demand_tile_box_height], anchor=BOTTOM + FRONT);

    translate([0, 0, $inner_height - cardboard_token_thickness - 0.2])
      cuboid([old_factory_tile_width, old_factory_tile_length, demand_tile_box_height], anchor=BOTTOM + LEFT + FRONT);

    translate([$inner_width / 2, 0, -2]) FingerHoleBase(
        radius=12, height=factory_tile_box_height - default_lid_thickness,
        spin=0
      );
  }
}

module StartingTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=starting_tile_box_width,
    length=starting_tile_box_length,
    text_str="Start"
  );
}

module UpgradeTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=upgraded_tile_box_width,
    length=upgraded_tile_box_length,
    height=upgraded_tile_box_height
  ) {
    for (i = [0:2]) {
      for (j = [0:1]) {
        translate(
          [
            (upgrade_token_width + 20) * j + 10,
            (upgrade_token_width + 5) * i,
            $inner_height - cardboard_token_thickness * 4,
          ]
        )
          CuboidWithIndentsBottom(
            [upgrade_token_width, upgrade_token_width, upgraded_tile_box_height],
            anchor=BOTTOM + LEFT + FRONT,
            finger_holes=[2, 6],
            finger_hole_radius=6.5
          );
      }
    }
  }
}

module UpgradedTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=upgraded_tile_box_width,
    length=upgraded_tile_box_length,
    text_str="Upgraded"
  );
}

module MoneyBox() // `make` me
{
  MakeBoxWithCapLid(
    width=money_box_width,
    length=money_box_length,
    height=money_box_height
  ) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=money_box_height, radius=5);
  }
}

module MoneyBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=money_box_width,
    length=money_box_length,
    height=money_box_height,
    text_str="Money"
  );
}

module SoloBox() // `make` me
{
  MakeBoxWithCapLid(
    width=solo_box_width,
    length=solo_box_length,
    height=solo_box_height
  ) {
    translate([10, 5, $inner_height - cardboard_token_thickness * 4])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=9
      );
    translate([10, 30, $inner_height - cardboard_token_thickness * 5])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=9
      );

    translate([43, 5, $inner_height - cardboard_token_thickness * 4])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=9
      );

    translate([43, 30, $inner_height - cardboard_token_thickness * 5])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=9
      );
  }
}

module SoloBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=solo_box_width,
    length=solo_box_length,
    text_str="Solo"
  );
}

module LateGameFactoryBox() // `make` me
{

  MakeBoxWithSlidingLid(
    width=late_game_factory_box_width,
    length=late_game_factory_box_length,
    height=late_game_factory_box_height
  ) {
    translate([$inner_width / 2, 0, $inner_height - cardboard_token_thickness * 6 - 1])
      cuboid(
        [factory_token_width, factory_token_length, late_game_factory_box_height],
        anchor=BOTTOM + FRONT
      );
    translate([$inner_width / 2, 0, -2]) FingerHoleBase(
        radius=15, height=factory_tile_box_height - default_lid_thickness,
        spin=0
      );
  }
}

module LateGameFactoryBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=late_game_factory_box_width,
    length=late_game_factory_box_length,
    text_str="Late Game"
  );
}

module RoundMarkerBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=round_marker_box_width,
    length=round_marker_box_length,
    height=round_marker_box_height
  ) {
    translate(
      [0, 0, $inner_height - round_marker_length / 2]
    )
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=round_marker_box_height, radius=5);

    translate([$inner_width / 2, $inner_length / 4, $inner_height - round_marker_length])
      cyl(d=round_marker_diameter, anchor=BOTTOM, h=round_marker_length + 10);
    translate([$inner_width / 2, $inner_length * 3 / 4, $inner_height - round_marker_length])
      cyl(d=round_marker_diameter, anchor=BOTTOM, h=round_marker_length + 10);
  }
}

module RoundMarkerBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=round_marker_box_width,
    length=round_marker_box_length,
    text_str="Round"
  );
}

module WorkerBox(material_colour = "yellow") // `make` me
{
  MakeBoxWithCapLid(
    width=worker_box_width,
    length=worker_box_length,
    height=worker_box_height,
    material_colour=material_colour
  ) {
    translate([0, 0, $inner_height - worker_thickness / 2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=worker_box_height, radius=5);
    for (i = [0:1]) {
      for (j = [0:2]) {
        if (i != 2 || j != 2) {
          translate(
            [
              worker_length / 2 + (worker_length + 1) * i + 4.5,
              worker_width / 2 + (worker_width+1) * j + 7,
              $inner_height - worker_thickness - 0.5,
            ]
          )
            rotate(j == 1 ? 90 : 90)
              linear_extrude(worker_box_height) WorkerItem();
        }
      }
      translate(
        [
          worker_length / 2 + (worker_length + 1) * 1 + worker_length + 5.25,
          worker_width / 2 + (worker_width * 2 + 4.5) * i + 5,
          $inner_height - worker_thickness - 0.5,
        ]
      )
        rotate(90)
          linear_extrude(worker_box_height) WorkerItem();

      
      // exper worker.
      translate(
        [
          $inner_width - expert_worker_width / 2-6,
          $inner_length / 2,
          $inner_height - expert_worker_thickness - 0.5,
        ]
      )
        cuboid([expert_worker_width, expert_worker_width, expert_worker_thickness + 1], anchor=BOTTOM);
    }
  }
}

module WorkerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=worker_box_width,
    length=worker_box_length,
    height=worker_box_height,
    text_str="Workers"
  );
}

module ResourceBox(material_colour = "yellow") // `make` me
{
  MakeBoxWithSlidingLid(
    width=resource_box_width,
    length=resource_box_length,
    height=resource_box_height,
    material_colour=material_colour
  ) {
    translate([0, 0, $inner_height - cube_size / 2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
    translate([$inner_width / 2, $inner_length / 2, $inner_height - cube_size - 0.5])
      cuboid([cube_size * 8 + 1, cube_size * 3, cube_size + 1], anchor=BOTTOM);
  }
}

module ResourceDoubleBox(material_colour = "yellow") // `make` me
{
  MakeBoxWithSlidingLid(
    width=resource_box_double_width,
    length=resource_box_length,
    height=resource_box_height,
    material_colour=material_colour
  ) {
    translate([0, 0, $inner_height - cube_size / 2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
    translate([$inner_width / 2 - cube_size / 2, $inner_length / 2, $inner_height - cube_size - 0.5])
      cuboid([cube_size * 10 + 1, cube_size * 3 + 0.5, cube_size + 1], anchor=BOTTOM);
    translate([$inner_width / 2 + cube_size * 5, $inner_length / 2, $inner_height - cube_size - 0.5])
      cuboid([cube_size * 1 + 1, cube_size * 2 + 0.5, cube_size + 1], anchor=BOTTOM);
  }
}

module SpacerFront() // `make` me
{
  MakeBoxWithNoLid(
    width=front_spacer_width,
    length=front_spacer_length,
    height=front_spacer_height,
    hollow=true
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([1, box_length, box_height]);
  }
  player_colours = ["purple", "yellow", "green", "red"];
  worker_colours = ["white", "blue", "grey", "yellow", "red", "black"];
  resource_colours = ["lightgrey", "red", "black", "palegoldenrod"];
  if (layout == 1) {
    translate([0, 0, player_box_height + player_box_bits_height * 2]) {
      for (i = [0:3])
        translate([0, 0, player_board_thickness * i])
          color(player_colours[i])
            cube([player_board_width, player_board_length, player_board_thickness]);
      translate([0, 0, player_board_thickness * 4]) {
        translate([3, 3, 4]) {
          color("darkblue")
            cube([board_width, board_length, board_thickness]);
          translate([0, 0, board_thickness])
            color("blue")
              cube([player_handbook_length, player_handbook_width, player_handbook_thickness]);
        }
      }
    }
  }
  for (j = [0:3]) {
    translate([player_box_width * j, player_box_length * 0, 0])
      PlayerBox(material_colour=player_colours[j]);
  }
  translate([0, 0, player_box_height])for (j = [0:1]) {
    translate([player_box_bits_width * j, 0, 0])
      PlayerBoxBits(material_colour=player_colours[j]);

    translate([player_box_bits_width * j, 0, player_box_bits_height])
      PlayerBoxBits(material_colour=player_colours[j + 2]);
  }
  translate([0, player_box_length, 0]) {
    FactoryTileBox();
    translate([factory_tile_box_width, 0, 0]) {
      FactoryTileBox();
      translate([factory_tile_box_width, 0, 0]) {
        DemandTileBox();
        translate([demand_tile_box_width, 0, 0]) {
          StartingTileBox();
          translate([starting_tile_box_width, 0, 0]) {
            UpgradeTileBox();
            translate([0, 0, upgraded_tile_box_height]) {
              MoneyBox();
            }
          }
        }
      }
    }
  }
  translate([0, player_box_length + factory_tile_box_length, 0]) {
    SoloBox();
    translate([0, 0, solo_box_height]) {
      LateGameFactoryBox();
      translate([late_game_factory_box_width, 0, 0]) {
        RoundMarkerBox();
      }
    }

    translate([solo_box_width, 0, 0]) {
      for (i = [0:2]) {
        translate([worker_box_width * i, 0, 0])
          WorkerBox(material_colour=worker_colours[i]);
        translate([worker_box_width * i, 0, worker_box_height])
          WorkerBox(material_colour=worker_colours[i + 3]);
      }
    }
    for (i = [0:1]) {
      translate([0, solo_box_length, resource_box_height * i])
        ResourceBox(material_colour=resource_colours[i]);
      translate([resource_box_width, solo_box_length, resource_box_height * i])
        ResourceDoubleBox(material_colour=resource_colours[i + 2]);
    }
    translate([0, solo_box_length + resource_box_length, 0]) {
      SpacerFront();
    }
  }
}

module BoxLayoutA() // `document` me
{
  BoxLayout(layout=1);
}

module TestBox() {
  difference() {
    cuboid([55, 45, 4], anchor=BOTTOM);
    translate([10, 10, 1])
      linear_extrude(10)
        ShipItem();
    translate([-15, 10, 1])
      linear_extrude(10)
        TrainItem();
    translate([0, -10, 1])
      linear_extrude(10)
        WorkerItem();
  }
}

if (FROM_MAKE != 1) {
  WorkerBox();
}
