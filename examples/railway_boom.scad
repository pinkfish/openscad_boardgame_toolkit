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

default_label_font = "Impact";
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_lid_shape_type = SHAPE_TYPE_DROP;

box_width = 209;
box_length = 300;
box_height = 46;

board_thickness = 10;
player_board_thickness = 2;
player_board_width = 161;
player_board_length = 228;
player_board_num = 4;

card_length = 92;
card_width = 67;
card_20_thickness = 14;
single_card_thickness = card_20_thickness / 20;

small_card_width = 46;
small_card_length = 66;

cube_size = 8.5;
train_length = 16;
train_width = 9;
train_height = 9;
pentagon_height = 16;
house_base_width = 10;
house_base_height = 6.5;
house_top_width = 13;
house_total_height = 13;
house_length = 16;
disc_diameter = 16;
disc_thickness = 3.5;
pentagon_thickness = 3.5;
pentagon_diameter = pentagon_height * 2 / (1 + cos(36));

num_cubes = 23;
num_trains = 30;
num_discs = 1;
num_stations = 4;

usable_height = box_height - board_thickness - 4 * player_board_thickness;

player_box_height = (usable_height) / 2;
player_box_width = (box_width - 2) / 2;
player_box_length = 108;

city_tile_width = 14.5;
city_tile_length = 32.5;
city_tile_edge_width = 10.5;
city_tile_middle_offset = 9;

regular_city_tiles = 36;
touristy_city_tiles = 14;
city_tile_thickness = 2.2;

starting_locamative_cards = 4;
locamotive_cards = 22;
carriage_cards = 30;
developmnent_cards = 74;
station_cards = 36;
objective_cards = 18;
route_cards = 7;

indicator_octogon_width = 16.5;
indicator_octogon_length = 24;
indicator_octogon_diameter = 17.318;

card_box_width = card_length + default_wall_thickness * 2;
card_box_length = card_width + default_wall_thickness * 2;
station_card_box_height = usable_height;
objective_card_box_height = single_card_thickness * objective_cards + default_floor_thickness + default_lid_thickness + 1;
route_card_box_height = usable_height - objective_card_box_height - 0.5;

small_card_box_width = small_card_length + default_wall_thickness * 2;
small_card_box_length = small_card_width + default_wall_thickness * 2;
locomotive_card_box_height = station_card_box_height;
carriage_card_box_height = station_card_box_height;
development_card_box_height = box_height - board_thickness;

city_tile_box_length = small_card_box_length;
city_tile_box_width = card_box_width * 2 - small_card_box_width * 2;
city_tile_box_height = station_card_box_height;

tourist_tile_box_length = card_box_length;
tourist_tile_box_width = box_width - 2 * card_box_width;
tourist_tile_box_height = box_height - board_thickness;

resource_box_length = (box_length - player_box_length - card_box_length - small_card_box_length) / 2;
resource_box_width = box_width - 2 * small_card_box_width;
resource_box_height = (box_height - board_thickness) / 2;

indicator_box_length = box_length - player_box_length - card_box_length - small_card_box_length * 2 - 1;
indicator_box_width = indicator_octogon_diameter * 4 + default_wall_thickness * 2 + 2;
indicator_box_height = box_height - board_thickness;

resource_box_five_width = small_card_box_width * 2 - indicator_box_width;
resource_box_five_length = box_height - board_thickness;
resource_box_five_height = indicator_box_length;

spacer_front_length = small_card_box_length;
spacer_front_width = tourist_tile_box_width;
spacer_front_height = box_height - board_thickness;

spacer_player_board_length = player_box_length;
spacer_player_board_width = box_width - player_board_width - 1;
spacer_player_board_height = player_board_thickness * 4;

module CityTile() {
  polygon(
    round_corners(
      [
        [city_tile_length / 2, city_tile_width / 2],
        [city_tile_length / 2, city_tile_width / 2 - city_tile_edge_width],
        [city_tile_length / 2 - city_tile_middle_offset, -city_tile_width / 2],
        [-city_tile_length / 2 + city_tile_middle_offset, -city_tile_width / 2],
        [-city_tile_length / 2, city_tile_width / 2 - city_tile_edge_width],
        [-city_tile_length / 2, city_tile_width / 2],
      ], radius=1
    )
  );
}

module StationPiece(height) {
  linear_extrude(height=height)
    polygon(
      points=round_corners(
        [
          [-house_base_width / 2, -house_total_height / 2 + house_base_height],
          [-house_base_width / 2, -house_total_height / 2],
          [house_base_width / 2, -house_total_height / 2],
          [house_base_width / 2, -house_total_height / 2 + house_base_height],
          [house_top_width / 2, -house_total_height / 2 + house_base_height],
          [house_top_width / 2, -house_total_height / 2 + house_base_height + 2],
          [0, house_total_height / 2],
          [-house_top_width / 2, -house_total_height / 2 + house_base_height + 2],
          [-house_top_width / 2, -house_total_height / 2 + house_base_height],
        ], radius=0.5
      )
    );
}

module StationCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=station_card_box_height,
    lid_on_length=true
  ) {
    cube([card_length, card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=17, height=station_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module StationCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Stations",
    lid_on_length=true
  );
}

module ObjectiveCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=objective_card_box_height,
    lid_on_length=true
  ) {
    cube([card_length, card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=17, height=objective_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module ObjectiveCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Objectives",
    lid_on_length=true
  );
}

module RouteCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=card_box_width, length=card_box_length, height=route_card_box_height,
    lid_on_length=true
  ) {
    cube([card_length, card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=17, height=route_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module RouteCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width, length=card_box_length, text_str="Routes",
    lid_on_length=true
  );
}

module CarriageCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=small_card_box_width, length=small_card_box_length, height=carriage_card_box_height,
    lid_on_length=true
  ) {
    cube([small_card_length, small_card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=15, height=carriage_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module CarriageCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=small_card_box_width, length=small_card_box_length, text_str="Carriages",
    lid_on_length=true
  );
}

module LocomotiveCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=small_card_box_width, length=small_card_box_length, height=locomotive_card_box_height,
    lid_on_length=true
  ) {
    cube([small_card_length, small_card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=15, height=locomotive_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module LocomotiveCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=small_card_box_width, length=small_card_box_length, text_str="Locomotives",
    lid_on_length=true
  );
}

module DevelopmentCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=small_card_box_width, length=small_card_box_length, height=development_card_box_height,
    lid_on_length=true
  ) {
    cube([small_card_length, small_card_width, box_height]);
    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=15, height=development_card_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module DevelopmentCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=small_card_box_width, length=small_card_box_length, text_str="Development",
    lid_on_length=true
  );
}

module CityTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=city_tile_box_width, length=city_tile_box_length, height=city_tile_box_height,
  ) {
    for (i = [0:2]) {
      translate([0, i * (city_tile_width + 1), 0])
        translate([city_tile_length / 2, city_tile_width / 2, 0])
          linear_extrude(height=city_tile_box_height)
            rotate(180)
              CityTile();

      translate([$inner_width - city_tile_width / 2, $inner_length / 2, $inner_height - 3 * city_tile_thickness]) {
        linear_extrude(height=city_tile_box_height)
          rotate(90)
            CityTile();
        translate([-1, city_tile_length / 2, 0])
          sphere(r=5, anchor=BOTTOM);
        translate([-1, -city_tile_length / 2, 0])
          sphere(r=5, anchor=BOTTOM);
      }

      translate([city_tile_length / 2, 0, -2]) FingerHoleBase(
          radius=10, height=city_tile_box_height - default_lid_thickness,
          spin=0
        );
      translate([city_tile_length / 2 - 7.5, 0, 0])
        RoundedBoxAllSides(width=15, length=city_tile_width * 3, height=city_tile_box_height, radius=7);
    }
  }
}

module CityTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=city_tile_box_width, length=city_tile_box_length, text_str="City",
  );
}

module TouristTileBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=tourist_tile_box_width, length=tourist_tile_box_length, height=tourist_tile_box_height,
    lid_on_length=true
  ) {

    translate([city_tile_width / 2 - 1, $inner_length / 2, 0])
      linear_extrude(height=tourist_tile_box_height)
        rotate(90)
          CityTile();

    translate([0, $inner_length / 2, -2]) FingerHoleBase(
        radius=10, height=tourist_tile_box_height - default_lid_thickness,
        spin=270
      );
  }
}

module TouristTileBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=tourist_tile_box_width, length=tourist_tile_box_length, text_str="Tourist",
    lid_on_length=true
  );
}

module PlayerBox(material_colour = "yellow") // `make` me
{
  MakeBoxWithCapLid(
    width=player_box_width, length=player_box_length, height=player_box_height,
    positive_negative_children=MAKE_MMU == 1 ? [1] : [],
    material_colour=material_colour
  ) {
    union() {
      translate([0, 0, $inner_height - 4])
        RoundedBoxAllSides(width=$inner_width - train_length - 2, length=$inner_length, height=player_box_height, radius=3);
      translate([5 + cube_size * 3 + train_length * 3, 0, $inner_height - 4])
        RoundedBoxAllSides(width=cube_size + 1 + 6, length=cube_size * 2 + 2, height=player_box_height, radius=3);
      translate([1, 7, $inner_height - train_height - 0.5]) {
        cuboid([train_length * 3, train_width * 10, train_height + 1], anchor=BOTTOM + LEFT + FRONT);
      }
      translate([train_length * 3 + 15, 5, $inner_height - cube_size - 0.5]) {
        cuboid([cube_size * 2, cube_size * 11, cube_size + 1], anchor=BOTTOM + LEFT + FRONT);
        translate([-0.25 + cube_size * 2, 0, 0])
          cuboid([cube_size + 1, cube_size, cube_size + 1], anchor=BOTTOM + LEFT + FRONT);
      }
      translate([17.5 + cube_size * 3 + train_length * 3, train_width * 3 + 16, $inner_height - disc_thickness - 0.5]) {
        CylinderWithIndents(
          d=disc_diameter, h=disc_thickness + 1, anchor=BOTTOM,
          finger_holes=[90, 270], finger_hole_radius=6
        );
      }
      translate([16.5 + cube_size * 3 + train_length * 3, train_width * 6 + 15, $inner_height - pentagon_thickness - 0.5]) {
        CylinderWithIndents(
          d=pentagon_diameter, h=pentagon_thickness + 1, anchor=BOTTOM, cyl_fn=5,
          finger_holes=[70, 290], finger_hole_radius=6
        );
      }

      for (i = [0:4]) {
        translate([train_length * 3 + 2 + house_top_width / 2, 24 + (house_length + 2) * i, $inner_height - 5]) {
          rotate([90, 0, 0])
            StationPiece(house_length);
          translate([-house_top_width / 2, -4 - house_length, 0])
            RoundedBoxAllSides(width=house_top_width + 0.5, length=house_length + 8, height=house_total_height * 10, radius=3);
        }
      }
    }

    union() {
      translate([1 + cube_size * 8.2, 3 + cube_size * 11 / 2, $inner_height - cube_size - 0.7]) {
        rotate(90)
          linear_extrude(height=0.2)
            text("Cubes", size=5, font="Impact", halign="center", valign="center");
      }
      translate([1 + train_length * 1.5, 3 + cube_size * 11 / 2, $inner_height - train_height - 0.7]) {
        rotate(90)
          linear_extrude(height=0.2)
            text("Trains", size=5, font="Impact", halign="center", valign="center");
      }
    }
  }
}

module PlayerBoxLid() // `make` me
{
  CapBoxLidWithLabel(
    width=player_box_width, length=player_box_length, height=player_box_height, text_str="Player",
  );
}

module ResourceBox(material_colour) // `make` me
{
  MakeBoxWithCapLid(
    width=resource_box_width, length=resource_box_length, height=resource_box_height,
    material_colour=material_colour,
  ) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_height, radius=5);
  }
}

module ResourceBoxCoalLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height, text_str="Coal",
    material_colour="black", label_colour="white"
  );
}

module ResourceBoxVPLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height, text_str="VP",
    material_colour="blue",
  );
}

module ResourceBoxMaterialsLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height, text_str="Materials",
    material_colour="brown",
  );
}

module ResourceBoxTechnologyLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_width, length=resource_box_length, height=resource_box_height, text_str="Tech",
    material_colour="purple",
  );
}

module IndicatorBox() // `make` me
{
  MakeBoxWithSlidingLid(width=indicator_box_width, length=indicator_box_length, height=indicator_box_height) {
    for (i = [0:3]) {
      translate([indicator_octogon_width / 2 + indicator_octogon_diameter * i, indicator_octogon_width / 2 - 1, $inner_height - indicator_octogon_length]) {
        rotate(20)
          cyl(
            d=indicator_octogon_diameter, h=indicator_octogon_length * 2, $fn=8,
            anchor=BOTTOM
          );
        translate([0, -5, 0])
          cuboid([8, 20, indicator_octogon_length * 2], rounding=3, anchor=BOTTOM);
      }
    }
  }
}

module IndicatorBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=indicator_box_width, length=indicator_box_length, text_str="Indicators",
  );
}

module ResourceBoxFive(material_colour) // `make` me
{
  MakeBoxWithCapLid(
    width=resource_box_five_width, length=resource_box_five_length, height=resource_box_five_height,
    positive_negative_children=MAKE_MMU == 1 ? [1] : [],
    material_colour=material_colour,
  ) {
    RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=resource_box_five_height, radius=5);
    union() {
      translate([$inner_width / 2, -default_wall_thickness + 0.4, 3])
        rotate([90, 0, 0])
          linear_extrude(height=40)
            text("Resource", size=5, font="Impact", halign="center", valign="center");
      translate([$inner_width / 2, $inner_length + default_wall_thickness - 0.398, 3])
        rotate([90, 0, 180])
          linear_extrude(height=0.4)
            text("Resource", size=5, font="Impact", halign="center", valign="center");
    }
  }
}

module ResourceBoxFiveLid() // `make` me
{
  CapBoxLidWithLabel(
    width=resource_box_five_width, length=resource_box_five_length, height=resource_box_five_height, text_str="Money",
    material_colour="orange"
  );
}
module FrontSpacerBox() // `make` me
{
  MakeBoxWithNoLid(width=spacer_front_width, length=spacer_front_length, height=spacer_front_height, hollow=true);
}

module SpacerPlayerBoardBox() // `make` me
{
  width_offset = box_width - player_board_width - tourist_tile_box_width - 2;
  spacer_box_width = box_width - player_board_width - 1;
  box_path = [
    [0, 0],
    [0, player_board_length - 2],

    [width_offset, player_board_length - 2],
    [width_offset, player_box_length - 2],
    [spacer_box_width, player_box_length - 2],
    [spacer_box_width, 0],
  ];
  MakePathBoxWithNoLid(
    path=box_path, height=player_board_thickness * 4, hollow=true,
    $fn=16
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([1, box_length, box_height]);
  }
  color("lightblue")
    cube([box_width, box_length, board_thickness]);
  color("aquamarine")
    translate([0, 0, board_thickness]) {
      cube([player_board_width, player_board_length, player_board_thickness * 4]);
    }
  if (layout < 3) {
    translate([0, 0, board_thickness + player_board_thickness * 4]) {
      PlayerBox(material_colour="green");
      if (layout < 2) {
        translate([0, 0, player_box_height]) {
          PlayerBox(material_colour="blue");
        }
      }
      translate([player_box_width, 0, 0]) {
        PlayerBox(material_colour="red");
      }
      if (layout < 2) {
        translate([player_box_width, 0, player_box_height]) {
          PlayerBox(material_colour="white");
        }
      }
      if (layout < 2) {
        translate([0, player_box_length, 0]) {
          StationCardBox();
        }
      }

      translate([card_box_width, player_box_length, 0]) {
        ObjectiveCardBox();
        translate([0, 0, objective_card_box_height]) {
          if (layout < 2) {
            RouteCardBox();
          }
        }
        if (layout < 2) {
          translate([card_box_width, 0, -player_board_thickness * 4]) {
            TouristTileBox();
          }
        }
      }

      if (layout < 2) {
        translate([0, player_box_length + card_box_length, 0]) {
          CarriageCardBox();
          translate([small_card_box_width, 0, 0]) {
            if (layout < 2) {
              LocomotiveCardBox();
              translate([small_card_box_width, 0, 0]) {
                CityTileBox();
                translate([city_tile_box_width, 0, -player_board_thickness * 4]) {
                  FrontSpacerBox();
                }
              }
            }
          }
        }
      }

      translate([0, player_box_length + card_box_length + small_card_box_length, -player_board_thickness * 4]) {
        if (layout < 2) {
          DevelopmentCardBox();
        }
        translate([small_card_box_width, 0, 0]) {
          if (layout < 2) {
            DevelopmentCardBox();
          }
          translate([small_card_box_width, 0, 0]) {
            for (i = [0:1]) {
              if (layout < 2 || i == 0) {
                translate([0, 0, resource_box_height * i]) {
                  ResourceBox(material_colour=["brown", "blue"][i]);
                  translate([0, resource_box_length, 0]) {
                    ResourceBox(material_colour=["purple", "black"][i]);
                  }
                }
              }
            }
          }
        }
      }
      if (layout < 2) {
        translate([0, player_box_length + card_box_length + small_card_box_length * 2, -player_board_thickness * 4]) {
          IndicatorBox();
          translate([indicator_box_width, 0, 0]) {
            translate([0, resource_box_five_height, 0]) {
              rotate([90, 0, 0]) {
                ResourceBoxFive(material_colour="orange");
              }
            }
          }
        }
      }
    }
  }
  translate([0, 0, board_thickness + player_board_thickness * 4]) {

    translate([player_board_width, 0, -player_board_thickness * 4]) {
      SpacerPlayerBoardBox();
    }
  }
}

module BoxLayoutOne() // `document` me
{
  BoxLayout(layout=1);
}

module BoxLayoutTwo() // `document` me
{
  BoxLayout(layout=2);
}

module BoxLayoutThree() // `document` me
{
  BoxLayout(layout=3);
}

if (FROM_MAKE != 1) {
  BoxLayoutThree();
}
