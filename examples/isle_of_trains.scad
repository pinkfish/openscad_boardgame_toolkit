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

box_width = 130;
box_length = 180;
box_height = 38;
wall_thickness = 3;
lid_thickness = 2;

card_width = 62.5;
card_length = 89;
total_card_thickness = 40;

token_thickness = 2;

destination_tile_width = 17.5 + 0.5;
destination_tile_length = 80 + 0.5;
destination_tile_corner_radius = 5 - 0.5;

track_tile_width = 20 + 0.5;
track_tile_length = 90 + 0.5;

ticket_tile_width = 30;
ticket_tile_length = 80;

train_token_length = 31.5;
train_token_width = 17.5;
train_token_thickness = 10;

victory_hex_one_width = 18;
victory_hex_three_width = 20;
victory_hex_five_width = 21.5;
victory_hex_ten_width = 24;

num_island_cards = 7;
num_train_cards = 71;
ten_card_thickness = (total_card_thickness * 10 / (num_island_cards + num_train_cards));

num_track_tiles = 2;
num_destination_tiles = 6;
num_ticket_tiles = 10;

num_victory_tokens = [12, 6, 4, 4];

destination_box_width = box_width - 1;
destination_box_length = destination_tile_width + track_tile_width + 1 + wall_thickness * 2;
destination_box_height = token_thickness * num_destination_tiles + 0.5 + lid_thickness * 2;

victory_box_width = destination_box_width;
victory_box_length = destination_box_length;
victory_box_height = box_height - destination_box_height - 0.5;

card_box_width = card_length + wall_thickness * 2 + 3;
card_box_length = card_width + wall_thickness * 2 + 0.5;
card_box_height = box_height - 1;

middle_box_length = box_length - card_box_length - destination_box_length - 1;
middle_box_height = box_height;
middle_box_width = card_box_width;

ticket_box_length = box_length - destination_box_length - 1;
ticket_box_width = box_width - middle_box_width - 1;
ticket_box_height = box_height - 1;

function TileRadius(width) = width / 2 / cos(180 / 6);

module DestinationBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=destination_box_width, length=destination_box_length, height=destination_box_height,
    wall_thickness=wall_thickness, lid_thickness=2
  ) {
    middle_width = destination_box_width - wall_thickness * 2;
    middle_length = destination_box_length - wall_thickness * 2;
    translate([(middle_width - destination_tile_length) / 2, 0, 0]) {
      difference() {
        translate(
          [
            0,
            0,
            destination_box_height - token_thickness * num_destination_tiles - 0.5 - lid_thickness * 2,
          ]
        )
          cube(
            [
              destination_tile_length,
              destination_tile_width,
              token_thickness * num_destination_tiles + 1,
            ]
          );
        cyl(
          h=token_thickness * num_destination_tiles + 2, anchor=BOTTOM,
          r=destination_tile_corner_radius
        );
        translate([0, destination_tile_width, 0]) cyl(
            h=token_thickness * num_destination_tiles + 2,
            anchor=BOTTOM, r=destination_tile_corner_radius
          );
        translate([destination_tile_length, 0, 0]) cyl(
            h=token_thickness * num_destination_tiles + 2,
            anchor=BOTTOM, r=destination_tile_corner_radius
          );
        translate([destination_tile_length, destination_tile_width, 0])
          cyl(
            h=token_thickness * num_destination_tiles + 2, anchor=BOTTOM,
            r=destination_tile_corner_radius
          );
      }
      translate([destination_tile_length / 2, -0.1, 0])
        FingerHoleWall(radius=10, height=token_thickness * num_destination_tiles + 1);
    }
    translate(
      [
        (middle_width - track_tile_length) / 2,
        destination_tile_width + 1,
        destination_box_height - token_thickness * num_track_tiles - 0.5 - lid_thickness * 2,
      ]
    ) {
      translate([track_tile_length / 2, track_tile_width / 2, 0]) CuboidWithIndentsBottom(
          [track_tile_length, track_tile_width, token_thickness * num_destination_tiles + 1],
          finger_holes=[0, 4], finger_hole_radius=token_thickness * num_destination_tiles + 0.5
        );
    }
  }
}

module DestinationBoxLid(generate_lid = true) // `make` me
{
  text_str = "Destinations";
  CapBoxLidWithLabel(
    width=destination_box_width, length=destination_box_length, lid_thickness=lid_thickness,
    height=destination_box_height,
    text_str=text_str, label_colour="black"
  );
}

module VictoryBox(generate_lid = true) // `make` me
{
  lid_thickness = 1;
  MakeBoxWithCapLid(
    width=victory_box_width, length=victory_box_length, height=victory_box_height,
    wall_thickness=wall_thickness, lid_thickness=lid_thickness
  ) {
    // One tokens.
    one_radius = TileRadius(victory_hex_one_width + 0.5);
    translate([3.5, 0, 0]) {
      one_bit_height = (num_victory_tokens[0] * token_thickness) + 2;
      translate(
        [
          one_radius,
          ($inner_length - one_bit_height) / 2 + one_bit_height,
          $inner_height - victory_hex_one_width / 2 - 0.4,
        ]
      ) rotate([90, 0, 0])
          RegularPolygon(width=victory_hex_one_width + 0.5, height=one_bit_height, shape_edges=6);
      translate([0, ($inner_length - one_bit_height) / 2, $inner_height - victory_hex_one_width / 2 - 0.4])
        cuboid(
          [one_radius * 2, one_bit_height, victory_hex_one_width / 2 + 0.25],
          anchor=BOTTOM + FRONT + LEFT, rounding=-4, edges=[TOP + LEFT, TOP + RIGHT]
        );
      translate([one_radius, 2, $inner_height - 8])
        FingerHoleWall(radius=10, height=8, depth_of_hole=victory_box_width);
    }
    // Three tokens.
    translate([10 + one_radius * 2, 0, 0]) {
      three_bit_height = (num_victory_tokens[1] * token_thickness) + 1;
      three_radius = TileRadius(victory_hex_three_width + 0.5);
      translate(
        [
          three_radius,
          ($inner_length - three_bit_height) / 2 + three_bit_height,
          $inner_height - victory_hex_three_width / 2 - 0.4,
        ]
      ) rotate([90, 0, 0])
          RegularPolygon(width=victory_hex_three_width + 0.5, height=three_bit_height, shape_edges=6);
      translate([0, ($inner_length - three_bit_height) / 2, $inner_height - victory_hex_three_width / 2 - 0.4])
        cuboid(
          [three_radius * 2, three_bit_height, victory_hex_three_width / 2 + 0.25],
          anchor=BOTTOM + FRONT + LEFT, rounding=-4, edges=[TOP + LEFT, TOP + RIGHT]
        );
      translate([three_radius, 2, $inner_height - 8])
        FingerHoleWall(radius=10, height=8, depth_of_hole=victory_box_width);
    }
    // ten token
    ten_bit_height = token_thickness * num_victory_tokens[3] + 0.5;
    ten_radius = TileRadius(victory_hex_ten_width + 0.5);
    translate(
      [
        victory_box_width - victory_hex_ten_width,
        ($inner_length - victory_hex_ten_width - 0.5) / 2 + victory_hex_ten_width / 2 + 0.25,
        $inner_height - ten_bit_height,
      ]
    ) {
      RegularPolygon(
        width=victory_hex_five_width + 0.5, height=ten_bit_height + 0.5, shape_edges=6,
        finger_hole_radius=ten_bit_height, finger_holes=[3, 6]
      );
    }
    // five token
    five_bit_height = token_thickness * num_victory_tokens[2] + 0.5;
    five_radius = TileRadius(victory_hex_five_width + 0.5);
    translate(
      [
        victory_box_width - five_radius * 2 - ten_radius * 2 - 1,
        ($inner_length - victory_hex_five_width - 0.5) / 2 + victory_hex_five_width / 2 + 0.25,
        $inner_height - five_bit_height,
      ]
    ) {
      RegularPolygon(
        width=victory_hex_five_width + 0.5, height=five_bit_height + 0.5, shape_edges=6,
        finger_hole_radius=five_bit_height, finger_holes=[3, 6]
      );
    }
  }
}

module VictoryBoxLid(generate_lid = true) // `make` me
{
  text_str = "Victory";
  CapBoxLidWithLabel(
    width=victory_box_width, length=victory_box_length, height=victory_box_height,
    lid_thickness=lid_thickness,
    text_str=text_str, label_colour="black"
  );
}

module CardBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=card_box_width, length=card_box_length, height=card_box_height,
    wall_thickness=wall_thickness
  ) {
    cube([card_length + 0.5, card_width + 0.5, card_box_height]);
    translate([0, card_width / 2 + 0.25, -2]) FingerHoleBase(radius=10, height=card_box_height);
  }
}

module CardBoxLid(generate_lid = true) // `make` me
{
  text_str = "Cards";
  CapBoxLidWithLabel(
    width=card_box_width, length=card_box_length, height=card_box_height,
    lid_thickness=lid_thickness,
    text_str=text_str, label_colour="black"
  );
}

module TicketBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=ticket_box_width, length=ticket_box_length, height=ticket_box_height,
    wall_thickness=wall_thickness, lid_thickness=lid_thickness, floor_thickness=lid_thickness
  ) {
    translate(
      [
        ($inner_width - token_thickness * num_ticket_tiles + 0.5) / 2,
        $inner_length - ticket_tile_length - 2,
        $inner_height - ticket_tile_width - 0.5,
      ]
    ) {
      cube([token_thickness * num_ticket_tiles + 0.5, ticket_tile_length, ticket_tile_width + 1]);

      translate([0, ticket_tile_length / 2, $inner_height - 17])
        FingerHoleWall(radius=10, height=ticket_tile_width / 2, spin=90, depth_of_hole=200);
    }
    translate([$inner_width / 2, train_token_length / 2 + 7, $inner_height - train_token_thickness - 0.5]) {
      CuboidWithIndentsBottom(
        [train_token_width, train_token_length, train_token_thickness + 1],
        finger_holes=[2, 6], finger_hole_radius=9
      );
    }
  }
}

module TicketBoxLid(generate_lid = true) // `make` me
{
  text_str = "Isle of Trains";
  CapBoxLidWithLabel(
    width=ticket_box_width, length=ticket_box_length, height=ticket_box_height,
    lid_thickness=lid_thickness,
    text_str=text_str, label_colour="black"
  );
}

module MiddleBox() // `make` me
{
  difference() {
    color(default_material_colour) cuboid(
        [middle_box_width, middle_box_length, middle_box_height],
        rounding=wall_thickness, anchor=BOTTOM + FRONT + LEFT
      );
    translate([wall_thickness, wall_thickness, lid_thickness]) color(default_material_colour)
        cuboid(
          [middle_box_width - wall_thickness * 2, middle_box_length - wall_thickness * 2, middle_box_height],
          rounding=1.5, anchor=BOTTOM + FRONT + LEFT
        );
  }
}

module BoxLayout() {
  cube([box_width, box_length, 1]);
  cube([1, box_length, box_height]);
  DestinationBox(generate_lid=false);
  translate([0, 0, destination_box_height]) VictoryBox(generate_lid=false);
  translate([0, destination_box_length + middle_box_length, 0]) CardBox(generate_lid=false);
  translate([0, destination_box_length, 0]) MiddleBox();
  translate([middle_box_width, destination_box_length, 0]) TicketBox(generate_lid=false);
}

module PrintLayout() {
  DestinationBox();
  translate([0, destination_box_length + 10, 0]) {
    VictoryBox();
    translate([0, victory_box_length + 10, 0]) {
      CardBox();
      translate([0, card_box_length + 10, 0]) {
        MiddleBox();
        translate([0, middle_box_length + 10, 0]) {
          TicketBox();
        }
      }
    }
  }
}

if (FROM_MAKE != 1) {
  DestinationBox(generate_lid=false);
}
