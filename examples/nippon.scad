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
player_handboook_length = 233;
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

machine_diameter = 15.5;
machine_thickness = 6;

ship_length = 25;
ship_width = 16;
ship_thickness = 10;

train_length = 20.5;
train_width = 13;

worker_length = 18.5;
worker_width = 14;

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

player_box_width = box_width / 2;
player_box_height = (box_height - board_thickness - player_board_thickness * 4) / 2;
player_box_length = 92;

factory_tile_box_width = default_wall_thickness * 2 + factory_token_width + 1;
factory_tile_box_length = default_wall_thickness * 2 + factory_token_length + 1;
factory_tile_box_height = box_height - board_thickness - player_board_thickness * 4;

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
money_box_height = box_height - upgraded_tile_box_height - board_thickness - player_board_thickness * 4;

solo_box_width = 100;
solo_box_length = upgraded_tile_box_length;
solo_box_height = default_floor_thickness + default_lid_thickness + 1 + cardboard_token_thickness * 5;

late_game_factory_box_width = solo_box_width;
late_game_factory_box_length = solo_box_length;
late_game_factory_box_height = box_height - board_thickness - player_board_thickness * 4 - solo_box_height;

middle_spacer_width = box_width - solo_box_width;
middle_spacer_length = solo_box_length;
middle_spacer_height = factory_tile_box_height;

front_spacer_width = box_width;
front_spacer_length = box_length - solo_box_length - factory_tile_box_length - player_box_length;
front_spacer_height = factory_tile_box_height;

module PlayerBox() // `make` me
{
  MakeBoxWithCapLid(
    width=player_box_width,
    length=player_box_length,
    height=player_box_height
  ) {
    translate([0, 0, $inner_height - ship_thickness / 2])
      RoundedBoxAllSides(
        width=ship_length * 2 + train_length + 6,
        length=$inner_length,
        height=ship_thickness,
        radius=5
      );

    // ships in spaces
    for (i = [0:4]) {
      for (j = [0:1]) {
        if (j != 1 || i < 1) {
          translate([1 + (ship_length + 1.5) * j, (ship_width + 1.5) * i + 1, $inner_height - ship_thickness])
            cuboid([ship_length, ship_width, ship_thickness + 1], anchor=BOTTOM + FRONT + LEFT);
        }
      }
    }

    // trains in spaces
    translate([(ship_length + 1.5) * 2 - train_length - 5, 8, 0]) {
      for (i = [0:4]) {
        for (j = [0:1]) {
          if ( (j == 1 || i >= 1) && (j == 0 || i > 2)) {
            translate([(train_length + 1.5) * j, 4 + (train_width + 1.5) * i + 1, $inner_height - ship_thickness])
              cuboid([train_length, train_width, ship_thickness + 1], anchor=BOTTOM + FRONT + LEFT);
          }
        }
      }
      translate([(train_length + 1.5) * 1 + 9, 0, 0]) {
        for (i = [0:2]) {
          translate([0, (track_marker_cylinder_diameter + 1.5) * i, $inner_height - track_marker_cylinder_length])
            cyl(d=track_marker_cylinder_diameter, h=track_marker_cylinder_length + 1, anchor=BOTTOM + FRONT + LEFT);
        }
      }
    }

    // machine disks
    translate([$inner_width - machine_diameter / 2 - 1, 20, $inner_height - machine_thickness * 2 + 0.5]) {
      for (i = [0:2]) {
        translate([0, (machine_diameter + 1.5) * i, 0])
          CylinderWithIndents(
            d=machine_diameter, h=machine_thickness * 2 + 1,
            anchor=BOTTOM,
            finger_holes=[90, 270],
            finger_hole_radius=6
          );
      }
    }

    // influence tokens
    translate([$inner_width - machine_diameter * 2 - 10, 25, $inner_height - cardboard_token_thickness * 5 + 0.5]) {
      for (j = [0:1]) {
        for (i = [0:1]) {
          translate([-(influence_token_width + 1.5) * j, (influence_token_width + 2) * i, 0]) {
            difference() {
              if (j == 1 && i == 0) {
                translate([0, 0, cardboard_token_thickness])
                  CuboidWithIndentsBottom(
                    [influence_token_width, influence_token_width, cardboard_token_thickness * 8],
                    anchor=BOTTOM + FRONT + LEFT,
                    finger_holes=[2, 6],
                    finger_hole_radius=5.5
                  );
              } else {
                CuboidWithIndentsBottom(
                  [influence_token_width, influence_token_width, cardboard_token_thickness * 8],
                  anchor=BOTTOM + FRONT + LEFT,
                  finger_holes=[2, 6],
                  finger_hole_radius=5.5
                );
              }
              if (j == 0) {
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
              if (j == 1) {
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

      // contract tokens
      translate([-contract_token_length + 22, $inner_length - contract_token_width * 2 - 5, 0 - cardboard_token_thickness * 3]) {
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
    }

    // scoring disks
    for (i = [0:1]) {
      translate(
        [
          $inner_width - scoring_disk_diameter * 2 + -(scoring_disk_diameter + 1.5) * i,
          scoring_disk_diameter / 2 + 4,
          $inner_height - scoring_disk_thickness,
        ]
      )
        CylinderWithIndents(
          d=scoring_disk_diameter,
          h=player_box_height,
          finger_holes=[0, 180],
          finger_hole_radius=5
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
    translate([0, 0, $inner_height - cardboard_token_thickness * 12])
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
    translate([8, 5, $inner_height - cardboard_token_thickness * 4])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=7
      );
    translate([8, 30, $inner_height - cardboard_token_thickness * 5])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=7
      );

    translate([55, 5, $inner_height - cardboard_token_thickness * 4])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=7
      );

    translate([55, 30, $inner_height - cardboard_token_thickness * 5])
      CuboidWithIndentsBottom(
        [solo_goal_token_length, solo_goal_token_width, solo_box_height],
        anchor=BOTTOM + LEFT + FRONT,
        finger_holes=[2, 6],
        finger_hole_radius=7
      );
  }
}

module LateGameFactoryBoxLid() // `make` me
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

module SpacerMiddle() // `make` me
{
  MakeBoxWithNoLid(
    width=middle_spacer_width,
    length=middle_spacer_length,
    height=middle_spacer_height,
    hollow=true
  );
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

module BoxLayout() {
  cube([box_width, box_length, 1]);
  cube([1, box_length, box_height]);
  for (j = [0:1]) {
    translate([player_box_width * j, player_box_length * 0, 0])
      PlayerBox();
    translate([player_box_width * j, player_box_length * 0, player_box_height])
      PlayerBox();
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
    }
    translate([solo_box_width, 0, 0]) {
      SpacerMiddle();
    }
    translate([0, solo_box_length, 0]) {
      SpacerFront();
    }
  }
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
