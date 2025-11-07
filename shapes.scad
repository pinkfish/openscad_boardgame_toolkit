// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

// LibFile: shapes.scad
//    This file has all the modules needed to make various shapes.

// FileSummary: Shapes for all sorts of things.
// FileGroup: Shapes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Shapes
//    Shapes to use in boxes and stuff.

calc_sqrt_three = sqrt(3);

// Module: Sword2d()
// Description:
//    2d shape of a sword.
// Arguments:
//    length = length of the sword
//    width = width of the sword
//    blade_width = width of the blade (default width / 3)
//    hilt_length = length of the hilt (default length / 15)
//    hilt_pos = position on the blade where the hilt starts (default length / 7)
//    blade_rounding = how much rounding on the end of the blade (default 1)
//    hilt_rounding = how much rounding on the hilt (default 1)
// Example(2D):
//    Sword2d(100, 20);
module Sword2d(
  length,
  width,
  blade_width = undef,
  hilt_length = undef,
  hilt_pos = undef,
  hilt_rounding = undef,
  blade_rounding = undef
) {
  calc_hilt_length = DefaultValue(hilt_length, length / 15);
  calc_hilt_pos = DefaultValue(hilt_pos, length / 7);
  calc_blade_width = DefaultValue(blade_width, width / 3);
  calc_hilt_rounding = DefaultValue(hilt_rounding, length / 40);
  calc_blade_rounding = DefaultValue(hilt_rounding, width / 8);
  union() {
    difference() {
      rect([length, calc_blade_width], rounding=[0, calc_blade_rounding, calc_blade_rounding, 0]);
      translate([length / 2, width / 2]) right_triangle([length / 3, width / 2], spin=180);
      mirror([0, 1]) translate([length / 2, width / 2]) right_triangle([length / 3, width / 2], spin=180);
    }
    translate([-length / 2 + calc_hilt_pos + calc_hilt_length / 2, 0])
      rect([calc_hilt_length, width], rounding=calc_hilt_rounding);
  }
}
// Module: Sword2dOutline()
// Description:
//    2d outline of a sword.
// Arguments:
//    length = length of the sword
//    width = width of the sword
//    blade_width = width of the blade (default width / 3)
//    hilt_length = length of the hilt (default length / 15)
//    hilt_pos = position on the blade where the hilt starts (default length / 7)
//    blade_rounding = how much rounding on the end of the blade (default 1)
//    hilt_rounding = how much rounding on the hilt (default 1)
//    line_width = how wide the line is (default 1)
// Example(2D):
//    Sword2dOutline(100, 20);
module Sword2dOutline(
  length,
  width,
  blade_width = undef,
  hilt_length = undef,
  hilt_pos = undef,
  hilt_rounding = undef,
  blade_rounding = undef,
  line_width = 1
) {
  calc_hilt_length = DefaultValue(hilt_length, length / 15);
  calc_hilt_pos = DefaultValue(hilt_pos, length / 7);
  calc_blade_width = DefaultValue(blade_width, width / 3);
  calc_hilt_rounding = DefaultValue(hilt_rounding, length / 40);
  union() {
    DifferenceWithOffset(offset=-line_width)
      Sword2d(
        length, width, blade_width=calc_blade_width, hilt_length=calc_hilt_length,
        hilt_pos=calc_hilt_pos, hilt_rounding=calc_hilt_rounding, blade_rounding=blade_rounding,
      );
    translate([-length / 2 + calc_hilt_pos + calc_hilt_length / 2, 0]) DifferenceWithOffset(offset=-line_width)
        rect([calc_hilt_length, width], rounding=calc_hilt_rounding);
    difference() {
      translate(
        [-length / 2 + calc_hilt_pos + (length - calc_hilt_pos - calc_hilt_length) / 2 + calc_hilt_length, 0],
      )
        rect([length - calc_hilt_pos - calc_hilt_length, line_width]);
      translate([length / 2, width / 2]) right_triangle([length / 3, width / 2], spin=180);
      mirror([0, 1]) translate([length / 2, width / 2]) right_triangle([length / 3, width / 2], spin=180);
    }
  }
}

// Module: Crossbow2d()
// Description:
//    A 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/8)
//    bow_width = width of the bow section of the bow (default width/4)
//    outer_circle = how big of a circle with the crossbow to draw (default width*2)
// Example(2D):
//    Crossbow2d(70, 50);
module Crossbow2d(length, width, handle_width = undef, bow_width = undef, outer_circle = undef) {
  calc_handle_width = DefaultValue(handle_width, width / 8);
  calc_outer_circle = DefaultValue(outer_circle, width * 2);
  calc_bow_width = DefaultValue(bow_width, width / 4);
  intersection() {
    rect([width, length]);
    union() {
      translate([0, calc_outer_circle / 2 - length / 2]) {
        difference() {
          circle(d=calc_outer_circle);
          circle(d=calc_outer_circle - calc_bow_width);
          translate([-calc_outer_circle, 0]) square(calc_outer_circle * 2);
        }
      }
      rect([calc_handle_width, length]);
    }
  }
}

// Module: Crossbow2dOutline()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/8)
//    bow_width = width of the bow section of the bow (default width/4)
//    outer_circle = how big of a circle with the crossbow to draw (default width*2)
//    line_width = width of the line to display (default 1)
// Example(2D):
//    Crossbow2dOutline(70, 50);
module Crossbow2dOutline(length, width, handle_width = undef, bow_width = undef, outer_circle = undef, line_width = 1) {
  calc_handle_width = DefaultValue(handle_width, width / 8);

  DifferenceWithOffset(offset=-line_width)
    Crossbow2d(
      length=length, width=width, handle_width=calc_handle_width, bow_width=bow_width,
      outer_circle=outer_circle,
    );
  DifferenceWithOffset(offset=-line_width) rect([calc_handle_width, length]);
}

// Module: Sledgehammer2d()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/4)
//    head_lenght = length of the head (default length/3.5)
//    rounding_head = rounding amoubnt on the head (default width/5)
//    rounding_handle = rounding amount on the handle (default width/10)
// Example(2D):
//    Sledgehammer2d(70, 50);
module Sledgehammer2d(
  length,
  width,
  handle_width = undef,
  head_length = undef,
  rounding_head = undef,
  rounding_handle = undef
) {
  calc_hammer_handle_width = DefaultValue(handle_width, width / 4);
  calc_hammer_head_length = DefaultValue(head_length, length / 3.5);
  calc_rounding_handle = DefaultValue(rounding_handle, width / 10);
  calc_rounding_head = DefaultValue(rounding_head, width / 5);
  rect([calc_hammer_handle_width, length], rounding=calc_rounding_handle);
  translate([0, length / 2 - calc_hammer_head_length / 2])
    rect([width, calc_hammer_head_length], rounding=calc_rounding_head);
}

// Module: Sledgehammer2dOutline()
// Description:
//    An outline of a 2d crossbow shape.
// Arguments:
//    length = length of the cross bpw.
//    width = width of the cross bow
//    handle_width = width of the handle bit (default width/4)
//    head_lenght = length of the head (default length/3.5)
//    rounding_head = rounding amoubnt on the head (default 2)
//    rounding_handle = rounding amount on the handle (default 1)
//    line_width = width of the lione (default 1)
//    strap_width = width of the strap outline(default line_width*4)
// Example(2D):
//    Sledgehammer2dOutline(70, 50);
module Sledgehammer2dOutline(
  length,
  width,
  handle_width = undef,
  head_length = undef,
  rounding_head = 2,
  rounding_handle = 1,
  line_width = 1,
  strap_width = undef
) {
  calc_hammer_handle_width = DefaultValue(handle_width, width / 4);
  calc_hammer_head_length = DefaultValue(head_length, length / 3.5);
  calc_strap_width = DefaultValue(strap_width, line_width * 4);
  DifferenceWithOffset(offset=-line_width) Sledgehammer2d(
      length=length, width=width, handle_width=calc_hammer_handle_width, head_length=calc_hammer_head_length,
    );
  translate([0, length / 2 - calc_hammer_head_length / 2]) DifferenceWithOffset(offset=-line_width)
      rect([width, calc_hammer_head_length], rounding=rounding_head);
  DifferenceWithOffset(offset=-line_width) polygon(
      [
        [calc_hammer_handle_width / 2, length / 2 - calc_hammer_head_length],
        [calc_hammer_handle_width / 2 + calc_strap_width, length / 2 - calc_hammer_head_length],
        [-calc_hammer_handle_width / 2, length / 2],
        [-calc_hammer_handle_width / 2 - calc_strap_width, length / 2],
      ],
    );
  DifferenceWithOffset(offset=-line_width) mirror([1, 0]) polygon(
        [
          [calc_hammer_handle_width / 2, length / 2 - calc_hammer_head_length],
          [calc_hammer_handle_width / 2 + calc_strap_width, length / 2 - calc_hammer_head_length],
          [-calc_hammer_handle_width / 2, length / 2],
          [-calc_hammer_handle_width / 2 - calc_strap_width, length / 2],
        ],
      );
}

// Module: Shoe2d()
// Description:
//    An nice 2d shoe shape.
// Arguments:
//    size = size of the shoe
//    leg_length = length of the leg bit of the shoe (default size/3)
//    sole_height = height of the sole base of the shoe (default size/20)
//    base_width = height of the base part of the shoe (default size/3)
// Example(2D):
//    Shoe2d(50);
module Shoe2d(size, leg_length = undef, base_width = undef, sole_height = undef) {
  calc_leg_length = DefaultValue(leg_length, size / 3);
  calc_base_width = DefaultValue(base_width, size / 3);
  calc_sole_height = DefaultValue(sole_height, size / 20);
  union() {
    translate([0, -size / 2 + calc_leg_length / 2]) rect([size, calc_leg_length]);
    translate([size / 2 - calc_base_width / 2 - calc_sole_height, 0])
      rect([calc_base_width, size], rounding=[0, calc_base_width * 3 / 4, 0, 0]);
    hull() {
      translate([size / 2 - calc_sole_height, (size * 3 / 5) / 2]) circle(r=calc_sole_height);
      translate([size / 2 - calc_sole_height * 2, -size / 2 + calc_leg_length]) circle(r=calc_sole_height);
      translate([size / 2 - calc_sole_height / 2, size / 2 - calc_sole_height / 2])
        circle(r=calc_sole_height / 2);
      translate([size / 2 - calc_sole_height * 2, size / 2 - calc_sole_height / 2])
        circle(r=calc_sole_height / 2);
    }
  }
}

// Module: Shoe2dOutline()
// Description:
//    An nice 2d shoe outline shape.
// Arguments:
//    size = size of the shoe
//    leg_length = length of the leg bit of the shoe (default size/3)
//    sole_height = height of the sole base of the shoe (default size/20)
//    base_width = height of the base part of the shoe (default size/3)
//    line_width = width of the outline line (default 1)
// Example(2D):
//    Shoe2dOutline(50);
module Shoe2dOutline(size, leg_length = undef, base_width = undef, sole_height = undef, line_width = 1) {
  DifferenceWithOffset(offset=-line_width)
    Shoe2d(size, leg_length=leg_length, base_width=base_width, sole_height=sole_height);
}

// Module: Bag2d()
// Description:
//    An nice 2d bag shape.
// Arguments:
//    size = size of the bag
//    base_round_diameter = round diameter of the base circles (default size/4)
//    main_round_diameter = round diameter of the middle bulge bit (default size/2)
//    neck_width = width of the neck of the bag (default size/6)
//    rope_length = length of the rope (default size/4)
// Example(2D):
//    Bag2d(50);
module Bag2d(size, base_round_diameter = undef, main_round_diameter = undef, neck_width = undef, rope_length = undef) {
  calc_base_round = DefaultValue(base_round_diameter, size / 4);
  calc_main_round = DefaultValue(main_round_diameter, size / 2);
  calc_neck_width = DefaultValue(neck_width, size / 6);
  calc_rope_length = DefaultValue(rope_length, size / 4);
  union() {
    // Bag bit
    hull() {
      translate([size / 2 - calc_base_round / 2, size / 2 - calc_base_round / 2]) circle(d=calc_base_round);
      translate([size / 2 - calc_base_round / 2, -size / 2 + calc_base_round / 2]) circle(d=calc_base_round);
      translate([size / 2 - calc_base_round / 2, -size / 2 + calc_base_round / 2]) circle(d=calc_base_round);
      translate([size / 2 - calc_base_round, -size / 2 + calc_base_round / 2]) circle(d=calc_base_round);
      translate([-size / 2 + calc_base_round, size / 2 - calc_base_round / 2]) circle(d=calc_base_round);
      translate([-size / 2 + calc_base_round + calc_main_round / 2, -calc_main_round / 4])
        circle(d=calc_main_round);
    }
    // Top bit.
    polygon(
      [
        [-size / 2, size / 2 - calc_neck_width * 5 / 8 - calc_neck_width / 4 - calc_neck_width],
        [-size / 2, size / 2 - calc_neck_width * 5 / 8 - calc_neck_width / 4],
        [0, calc_neck_width],
        [0, calc_neck_width / 2],
      ],
    );
    // Rope
    DifferenceWithOffset(offset=-calc_rope_length / 10)
      translate([-size / 2 + calc_rope_length / 6 * 2, size / 2 - calc_rope_length / 2 - calc_neck_width * 1.8])
        rotate(90)
          egg(calc_rope_length, calc_rope_length / 3, calc_rope_length / 8, calc_rope_length, $fn=180);
  }
}

// Module: Bag2dOutline()
// Description:
//    An nice 2d bag outline shape.
// Arguments:
//    size = size of the bag
//    base_round_diameter = round diameter of the base circles (default size/4)
//    main_round_diameter = round diameter of the middle bulge bit (default size/2)
//    neck_width = width of the neck of the bag (default size/6)
//    line_width = width of the line to use for the outline
// Example(2D):
//    Bag2d(50);
module Bag2dOutline(
  size,
  base_round_diameter = undef,
  main_round_diameter = undef,
  neck_width = undef,
  rope_length = undef,
  line_width = 1
) {
  DifferenceWithOffset(offset=-line_width)
    Bag2d(
      size, base_round_diameter=base_round_diameter, main_round_diameter=main_round_diameter,
      neck_width=neck_width, rope_length=rope_length,
    );
}

// Module: Torch2d()
// Description:
//    An nice 2d torch shape.
// Arguments:
//    size = size of the torch
//    handle_width = the width of the handle (default width/2)
//    head_length = length of the head (default length/7)
// Example(2D):
//    Torch2d(100, 20);
module Torch2d(length, width, handle_width = undef, head_length = undef) {
  calc_handle_width = DefaultValue(handle_width, width / 2);
  calc_head_length = DefaultValue(head_length, length / 7);
  rect([length, calc_handle_width], rounding=width / 6);
  hull() {
    translate([length / 2 - width / 4, width / 4]) circle(d=width / 2);
    translate([length / 2 - width / 4 - calc_head_length, width / 4]) circle(d=width / 2);
    translate([length / 2 - width / 4, -width / 4]) circle(d=width / 2);
    translate([length / 2 - width / 4 - calc_head_length, -width / 4]) circle(d=width / 2);
  }
}

// Module: Torch2dOutline()
// Description:
//    An nice 2d torch outline shape.
// Arguments:
//    size = size of the torch
//    handle_width = the width of the handle (default width/2)
//    head_length = length of the head (default length/7)
//    line_width = width of the line (default 1)
// Example(2D):
//    Torch2dOutline(100, 20);
module Torch2dOutline(length, width, handle_width = undef, head_length = undef, line_width = 1) {
  calc_handle_width = DefaultValue(handle_width, width / 2);
  calc_head_length = DefaultValue(head_length, length / 7);
  DifferenceWithOffset(offset=-line_width)
    Torch2d(length=length, width=width, handle_width=calc_handle_width, head_length=calc_head_length);
  DifferenceWithOffset(offset=-line_width) hull() {
      translate([length / 2 - width / 4, width / 4]) circle(d=width / 2);
      translate([length / 2 - width / 4 - calc_head_length, width / 4]) circle(d=width / 2);
      translate([length / 2 - width / 4, -width / 4]) circle(d=width / 2);
      translate([length / 2 - width / 4 - calc_head_length, -width / 4]) circle(d=width / 2);
    }
}

// Module: Teapot2d()
// Description:
//    An nice 2d teapor shape.
// Arguments:
//    length = length of the teapot
//    width = width of the teapot
//    top_width = top width of the teapot (default width*6/10)
//    top_length = length to the top part of the teapot.
//    top_circle_diameter = circle of the top part of the teapot
//    handle_rounding = rounding amount to use int he top handle
//    handle_width = width of the top handle
//    spout_length = length of the spout
//    side_handle_length = length of the side handle
//    side_handle_rounding = rounding of the bottom part of the handle
// Example(2D):
//    Teapot2d(100, 70);
module Teapot2d(
  length,
  width,
  top_width = undef,
  top_length = undef,
  top_circle_diameter = undef,
  handle_rounding = undef,
  handle_width = undef,
  spout_length = undef,
  side_handle_length = undef,
  side_handle_rounding = undef
) {
  calc_top_width = DefaultValue(top_width, width * 6 / 10);
  calc_top_length = DefaultValue(top_length, length * 7 / 10);
  calc_top_circle_diameter = DefaultValue(top_circle_diameter, calc_top_width * 8 / 10);
  calc_handle_rounding = DefaultValue(handle_rounding, width / 15);
  calc_handle_width = DefaultValue(handle_width, width / 30);
  calc_spout_length = DefaultValue(spout_length, length / 5);
  calc_side_handle_length = DefaultValue(side_handle_length, length / 3);
  calc_side_handle_rounding = DefaultValue(side_handle_rounding, width * 4 / 10);
  union() {
    // Base
    polygon(
      [
        [length / 2, width / 2],
        [length / 2 - calc_top_length, calc_top_width / 2],
        [length / 2 - calc_top_length, -calc_top_width / 2],
        [length / 2, -width / 2],
      ],
    );
    // Spout
    polygon(
      [
        [length / 2 - calc_top_length, calc_top_width / 2],
        [length / 2 - calc_top_length, width / 2],
        [length / 2 - calc_top_length + calc_spout_length, calc_top_width / 2],
      ],
    );
    // Top bit
    translate([length / 2 - calc_top_length, 0]) circle(d=calc_top_circle_diameter);
    diff_top = length - calc_top_length - calc_top_circle_diameter / 2;
    // Handle
    translate([-length / 2 + diff_top, 0]) {
      DifferenceWithOffset(offset=-calc_handle_width)
        rect([diff_top * 2, diff_top * 2], rounding=calc_handle_rounding);
    }
    // Back Handle.
    DifferenceWithOffset(offset=-calc_handle_width) hull() {
        side_diameter = width / 20;
        translate([side_diameter / 2, side_diameter / 2]) {
          translate([length / 2 - calc_top_length, -calc_top_width / 2]) circle(d=side_diameter);
          translate([length / 2 - calc_top_length, -width / 2]) circle(d=side_diameter);
        }
        translate([-calc_side_handle_rounding / 2, calc_side_handle_rounding / 2])
          translate([length / 2 - calc_top_length + calc_side_handle_length, -width / 2])
            circle(d=calc_side_handle_rounding);
      }
  }
}

// Module: Coin2d()
// Description:
//   A simple coin icon to use in things.
// Arguments:
//   size = the size of the coin
//   text = text to put in the coin (default 1)
//   text_size = size of the text to use (dewfault size/2)
// Example(2D):
//   Coin2d(50);
// Example(2D):
//   Coin2d(50, text = "5");
module Coin2d(size, text = "1", text_size = undef) {
  calc_text_size = DefaultValue(text_size, size / 2);
  difference() {
    supershape(m1=20, n1=19, n2=4, n3=5, a=2.7, d=size);

    DifferenceWithOffset(offset=-size / 30)
      supershape(m1=10, n1=19, n2=4, n3=5, a=2.7, d=size * 3 / 4);

    rotate(90) text(
        text=text, font="Stencil Std:style=Bold", size=calc_text_size, halign="center",
        valign="center",
      );
  }
}

// Module: CoinPile2d()
// Description:
//   Makes a coin pile to use in other places.
// Arguments:
//   size = size of the pile
//   coin_num = number of coins in the pile (default 5)
//   rounding = how much to round the coins (default (size * 3 / 4) / (calc_coin_num * 2))
// Example(2D):
//   CoinPile2d(50);
// Example(2D):
//   CoinPile2d(50, coin_num=3);
// Example(2D):
//   CoinPile2d(50, coin_num=10);
module CoinPile2d(size, rounding = undef, coin_num = undef) {
  calc_coin_num = DefaultValue(coin_num, 5);
  calc_rounding = DefaultValue(rounding, (size * 3 / 4) / (calc_coin_num * 2));
  coin_width = (size * 3 / 4) / calc_coin_num;
  for (i = [0:1:calc_coin_num - 1]) {
    translate([size / 2 - coin_width * i, 0]) rect([coin_width, size], rounding=calc_rounding);
  }
  translate([-size / 2 + size / 8, 0]) rotate(15) rect([coin_width, size], rounding=calc_rounding);
}

// Constant: australia_map_length
// Description: The length of the australian svg map
australia_map_length = 365.040;
// Constant: australia_map_width
// Description: The width of the australian svg map
australia_map_width = 340.160;

// Function: AustraliaMapWidth()
// Description: Works out the width of the map from the length.
function AustraliaMapWidth(length) = length * (australia_map_width / australia_map_length);

// Module: AustraliaMap2d()
// Description:
//    a map of australia
// Arguments:
//    length = length of the map
// Example(2D):
//    AustraliaMap2d(100);
module AustraliaMap2d(length) {
  resize([length, AustraliaMapWidth(length)]) import("svg/australia.svg");
}

// Module: Rock2d()
// Description:
//  Makes a rock shape to use in walls and things.
// Arguments:
//    width = width of the rock
//    length = length of the rock
//    rounding = rounding on the edge of the rock (default min(width,lenght)/5)
// Example(2D);
//    Rock2d(50, 20);
module Rock2d(length, width, rounding = undef) {
  calc_rounding = min(length, width) / 5;
  rect([length, width], rounding=calc_rounding);
}

// Constant: ruins_2d_length
// Description: The length of the ruins svg
ruins_2d_length = 100;
// Constant: ruins_2d_width
// Description: The length of the ruins svg
ruins_2d_width = 62.921;

// Function: Ruins2dWidth()
// Description: Works out the width of the map from the length.
function Ruins2dWidth(length) = length * (ruins_2d_width / ruins_2d_length);

// Module: Ruins2d()
// Description:
//    Makes a small ruins image to use in stuff.
// Example(2D):
//    Ruins2d(50);
module Ruins2d(size) {
  // offset helps fix the shape not closed issue.
  translate([-size / 2, -Ruins2dWidth(size) / 2]) resize([size, Ruins2dWidth(size)]) offset(delta=0.01)
        import("svg/ruins.svg");
}

// Module: RockWall2d()
// Description:
//   Makes a nice rock wall
// Arguments:
//   size = size of the rock wall
//   num_rows = number of rows (default 10)
//   num_cols = numer of cols (default 40)
// Example(2D):
//    RockWall2d(50);
module RockWall2d(size, num_rows = 10, num_cols = 40, spacing = undef) {
  calc_rock_length = size / num_rows;
  calc_rock_width = size / num_cols;
  calc_spacing = DefaultValue(spacing, size / 200);
  for (j = [0:1:num_rows - 1]) {
    for (i = [0:1:num_cols - 1]) {
      translate(
        [
          -size / 2 + (i % 2) * calc_rock_length / 2 + calc_rock_length * j,
          -size / 2 + calc_rock_width * i + calc_rock_width / 2,
        ],
      ) Rock2d(calc_rock_length - calc_spacing, calc_rock_width - calc_spacing);
    }
  }
}

// Module: D20Outline2d()
// Description:
//   Makes a nice d20 outline for some dice.
// Arguments:
//   size = size of the die image
//   offset = the size of the walls
// Example(2D):
//    D20Outline2d(10, 0.5);
module D20Outline2d(size, offset) {
  r = size / 2 - offset / 2;
  union() {
    points = [for (i = [0:1:5]) ([r * cos(360 * i / 6), r * sin(360 * i / 6)])];
    r_triangle = r / 5 * 3;
    points_triangle = [for (i = [0:1:2]) ([r_triangle * cos(360 * i / 3), r_triangle * sin(360 * i / 3)])];
    stroke([points[0], points[5], points_triangle[0], points[0]], width=offset);
    stroke([points[0], points[1], points_triangle[0], points[1]], width=offset);
    stroke([points[1], points[2], points_triangle[1], points[1]], width=offset);
    stroke([points[2], points[3], points_triangle[1], points[2]], width=offset);
    stroke([points[3], points[4], points_triangle[2], points[3]], width=offset);
    stroke([points[4], points[5], points_triangle[2], points[4]], width=offset);
    stroke([points_triangle[0], points_triangle[1], points_triangle[2], points_triangle[0]], width=offset);
  }
}

// Module: SawBlade2d()
// Description:
//   Makes a nice 2d saw blade.
// Arguments:
//   size = size of the saw blade
//   inner_spindle_size = size of the inside spindle (default size/10)
// Example(2D):
//    SawBlade2d(50);
module SawBlade2d(size, inner_spindle_size = undef) {
  calc_inner_spindle_size = DefaultValue(inner_spindle_size, size / 10);
  difference() {
    resize([size, size]) supershape(m1=20, n1=20, n2=9, n3=6);
    circle(r=calc_inner_spindle_size);
  }
}

// Module: SawBlade2dOutline()
// Description:
//   Makes a nice 2d saw blade.
// Arguments:
//   size = size of the saw blade
//   inner_spindle_size = size of the inside spindle (default size/10)
// Example(2D):
//    SawBlade2d(50);
module SawBlade2dOutline(size, inner_spindle_size = undef, outer_width = 1) {
  module OuterBlade() {
    resize([size, size]) supershape(m1=20, n1=20, n2=9, n3=6);
  }
  calc_inner_spindle_size = DefaultValue(inner_spindle_size, size / 10);
  difference() {
    OuterBlade();
    hull() offset(-outer_width) OuterBlade();
  }
  circle(r=calc_inner_spindle_size);
}

// Module: Handshake2d()
// Description:
//   Creates two hands shaking hands.
// Arguments:
//   size = size of the hands.
// Example(2D):
//   Handshake2d(30);
module Handshake2d(size) {
  module Thumb() {
    translate([38, 3]) rotate(220) stroke(egg(15, 5, 4, 60), closed=true);
  }
  module Finger() {
    rotate(230) stroke(egg(12, 4, 5, 60), closed=true);
  }
  resize([size, size * 60 / 80]) translate([-40, 0]) {
      difference() {
        union() {
          polygon(points=[[0, 0], [0, 30], [40, 5], [40, -25]]);
          translate([80, 0]) mirror([1, 0]) polygon(points=[[0, 0], [0, 30], [40, 5], [40, -25]]);
          hull() {
            translate([34, -17]) circle(r=5);
            translate([44, -25]) circle(r=5);
          }
          translate([50, -20]) circle(r=5);
          translate([57, -15]) circle(r=5);
          translate([35, 5]) circle(r=5);
        }
        Thumb();

        path = bezier_points([[44, 5], [48, 6], [64, -15]], [0:0.2:1]);
        stroke(path);
        translate([35, -20]) Finger();
        translate([30, -17]) Finger();
        translate([25, -14]) Finger();
      }
      offset(-1) hull() Thumb();
      translate([35, -20]) offset(-1) hull() Finger();
      difference() {
        translate([30, -17]) offset(-1) hull() Finger();
        translate([35, -20]) Finger();
      }
      difference() {
        translate([25, -14]) offset(-1) hull() Finger();
        translate([30, -17]) Finger();
      }
    }
}

// Module: Fist2d()
// Description:
//   A nice fist for use in stuff.  Fist is from
//   [fist printables](https://www.printables.com/model/799571-fist-customizable)
//   by [Vendicar Design](https://www.printables.com/@VendicarDecarian)
// Arguments:
//   size = size of the fist
// Example(2D):
//   Fist2d(20);
module Fist2d(size) {

  Tight = true;
  Hollow = false;
  Loop = false;

  // Length 172

  Scale = size / 172; // [.1:.01:1.5]
  Offset = 5; // [.5:.2:10]

  scale([Scale, Scale]) translate([0, (100 - 72) / 2]) All();
  module _Loop() {
    translate([0, -111 - Offset]) difference() {
        circle(d=30);
        circle(d=16);
      }
  }

  module All() {
    polygon(
      points=[
        [6.75602, 71.5659],
        [6.837219, 71.4035],
        [6.75602, 71.1599],
        [6.59362, 70.83509],
        [6.350021, 70.51029],
        [6.025223, 69.86069],
        [5.781624, 69.5359],
        [5.619225, 69.21109],
        [5.132019, 68.56149],
        [4.96962, 68.23669],
        [4.482422, 67.5871],
        [4.320023, 67.26229],
        [4.076424, 66.93749],
        [3.751625, 66.2879],
        [3.508018, 65.9631],
        [3.345619, 65.63829],
        [2.858421, 64.98869],
        [2.696022, 64.66389],
        [2.452423, 64.3391],
        [2.127625, 63.68949],
        [1.884026, 63.36469],
        [1.721619, 63.03989],
        [1.234421, 62.39029],
        [1.072021, 62.06549],
        [0.5848236, 61.41589],
        [0.4224243, 61.09109],
        [0.1788254, 60.76629],
        [-0.1459808, 60.11669],
        [-0.3895798, 59.79189],
        [-0.5519791, 59.46709],
        [-1.039177, 58.81749],
        [-1.201576, 58.49269],
        [-1.445175, 58.16789],
        [-1.769981, 57.5183],
        [-2.01358, 57.19349],
        [-2.17598, 56.86869],
        [-2.663177, 56.21909],
        [-2.825577, 55.89429],
        [-3.312775, 55.24469],
        [-3.475182, 54.91989],
        [-3.718781, 54.59509],
        [-4.043579, 53.9455],
        [-4.287178, 53.62069],
        [-4.449577, 53.29589],
        [-4.936775, 52.64629],
        [-5.099174, 52.3215],
        [-5.829979, 51.34709],
        [-6.804375, 50.37269],
        [-7.129181, 50.12909],
        [-7.453979, 49.96669],
        [-7.778778, 49.88549],
        [-9.402779, 49.88549],
        [-10.05238, 50.04789],
        [-10.70198, 50.37269],
        [-11.02678, 50.4539],
        [-11.35158, 50.61629],
        [-11.67638, 50.69749],
        [-13.62518, 51.67189],
        [-13.94998, 51.75309],
        [-14.27478, 51.91549],
        [-14.59958, 51.99669],
        [-20.44598, 54.91989],
        [-20.77078, 55.00109],
        [-21.09558, 55.16349],
        [-21.42038, 55.24469],
        [-29.54038, 59.3047],
        [-29.86518, 59.54829],
        [-30.02758, 59.79189],
        [-30.02758, 60.03549],
        [-29.86518, 60.19789],
        [-29.54038, 60.36029],
        [-28.89078, 60.52269],
        [-28.56598, 60.68509],
        [-27.91638, 60.8475],
        [-27.59158, 61.0099],
        [-25.64278, 61.49709],
        [-25.31798, 61.65949],
        [-24.66838, 61.82189],
        [-24.34358, 61.98429],
        [-23.69398, 62.14669],
        [-23.36918, 62.30909],
        [-22.71958, 62.47149],
        [-22.39478, 62.6339],
        [-20.44598, 63.12109],
        [-20.12118, 63.28349],
        [-19.47158, 63.44589],
        [-19.14678, 63.60829],
        [-18.49718, 63.77069],
        [-18.17238, 63.93309],
        [-17.52278, 64.09549],
        [-17.19798, 64.2579],
        [-15.24918, 64.74509],
        [-14.92438, 64.90749],
        [-14.27478, 65.06989],
        [-13.94998, 65.23229],
        [-13.30038, 65.39469],
        [-12.97558, 65.55709],
        [-12.32598, 65.7195],
        [-12.00117, 65.8819],
        [-10.05238, 66.36909],
        [-9.727577, 66.53149],
        [-9.07798, 66.69389],
        [-8.753181, 66.85629],
        [-8.103577, 67.01869],
        [-7.778778, 67.18109],
        [-7.129181, 67.34349],
        [-6.804375, 67.50589],
        [-6.154778, 67.6683],
        [-5.829979, 67.8307],
        [-3.88118, 68.31789],
        [-3.556381, 68.48029],
        [-2.906776, 68.64269],
        [-2.581978, 68.80509],
        [-1.932381, 68.96749],
        [-1.607574, 69.12989],
        [-0.9579773, 69.2923],
        [-0.6331787, 69.4547],
        [1.31562, 69.94189],
        [1.640419, 70.10429],
        [2.290024, 70.26669],
        [2.614822, 70.42909],
        [3.26442, 70.59149],
        [3.589226, 70.75389],
        [4.238823, 70.91629],
        [4.563622, 71.0787],
        [6.512421, 71.5659],
        [13.00842, 70.10429],
        [13.33322, 69.86069],
        [26.97482, 56.21909],
        [27.29962, 55.97549],
        [27.78683, 55.48829],
        [28.03043, 55.32589],
        [28.19283, 55.08229],
        [28.43642, 54.83869],
        [28.68002, 54.67629],
        [28.92362, 54.43269],
        [29.57323, 53.9455],
        [30.22282, 53.29589],
        [30.95362, 52.3215],
        [31.27843, 51.67189],
        [31.27843, 51.34709],
        [31.19722, 51.02229],
        [31.03482, 50.69749],
        [30.54762, 50.04789],
        [30.22282, 49.72309],
        [29.24842, 48.42389],
        [28.59882, 47.77429],
        [27.62442, 46.47509],
        [26.97482, 45.82549],
        [26.00042, 44.52629],
        [25.35082, 43.87669],
        [24.37643, 42.57749],
        [23.72682, 41.92789],
        [22.75243, 40.62869],
        [22.10282, 39.97909],
        [21.12843, 38.67989],
        [20.47882, 38.03029],
        [19.50443, 36.73109],
        [18.85482, 36.08149],
        [17.88042, 34.78229],
        [17.23082, 34.13269],
        [16.25642, 32.83349],
        [15.60682, 32.18389],
        [14.63242, 30.88469],
        [13.98283, 30.23509],
        [13.00842, 28.93589],
        [12.03402, 27.96149],
        [11.79042, 27.79909],
        [11.62802, 27.79909],
        [11.54682, 27.96149],
        [11.54682, 33.15829],
        [10.73483, 36.40629],
        [9.922821, 38.03029],
        [9.679222, 38.35509],
        [9.516823, 38.67989],
        [8.786026, 39.65429],
        [7.486824, 40.95349],
        [6.512421, 41.68429],
        [6.187622, 41.84669],
        [5.538025, 42.33389],
        [5.213219, 42.49629],
        [4.563622, 42.98349],
        [4.238823, 43.14589],
        [3.914024, 43.38949],
        [2.614822, 44.03909],
        [2.290024, 44.28269],
        [1.965225, 44.44509],
        [1.640419, 44.68869],
        [0.9908218, 45.01349],
        [0.6660233, 45.25709],
        [0.3412247, 45.41949],
        [0.01641846, 45.66309],
        [-0.6331787, 45.98789],
        [-0.9579773, 46.23149],
        [-1.282776, 46.39389],
        [-1.932381, 46.88109],
        [-2.17598, 47.12469],
        [-2.338379, 47.44949],
        [-2.419579, 47.77429],
        [-2.257179, 48.42389],
        [-1.769981, 49.39829],
        [-1.526375, 49.72309],
        [-1.363976, 50.04789],
        [-0.8767776, 50.69749],
        [-0.7143784, 51.02229],
        [-0.2271805, 51.67189],
        [-0.06478119, 51.99669],
        [0.4224243, 52.64629],
        [0.5848236, 52.97109],
        [1.072021, 53.62069],
        [1.234421, 53.9455],
        [1.721619, 54.59509],
        [1.884026, 54.91989],
        [2.371223, 55.56949],
        [2.533623, 55.89429],
        [3.020821, 56.54389],
        [3.18322, 56.86869],
        [3.670425, 57.5183],
        [3.832825, 57.84309],
        [4.320023, 58.49269],
        [4.482422, 58.81749],
        [5.944023, 60.76629],
        [6.106422, 61.09109],
        [6.59362, 61.74069],
        [6.75602, 62.06549],
        [7.243225, 62.7151],
        [7.405624, 63.03989],
        [7.892822, 63.68949],
        [8.055222, 64.0143],
        [9.516823, 65.9631],
        [9.679222, 66.2879],
        [10.16642, 66.93749],
        [10.32882, 67.26229],
        [10.81602, 67.9119],
        [10.97842, 68.23669],
        [11.46562, 68.88629],
        [11.62802, 69.21109],
        [12.11522, 69.86069],
        [12.35883, 70.10429],
        [12.68362, 70.18549],
        [-34.73718, 57.27469],
        [-33.11318, 56.86869],
        [-27.59158, 54.10789],
        [-27.26678, 53.86429],
        [-26.94198, 53.70189],
        [-26.61718, 53.45829],
        [-18.17238, 49.23589],
        [-17.84758, 48.99229],
        [-17.52278, 48.8299],
        [-17.19798, 48.58629],
        [-9.402779, 44.68869],
        [-9.07798, 44.44509],
        [-8.753181, 44.28269],
        [-8.428375, 44.03909],
        [0.01641846, 39.81669],
        [0.3412247, 39.57309],
        [0.6660233, 39.41069],
        [0.9908218, 39.16709],
        [2.939621, 38.19269],
        [3.914024, 37.46189],
        [4.644821, 36.73109],
        [5.375626, 35.75669],
        [6.187622, 34.13269],
        [6.67482, 32.18389],
        [6.67482, 26.01269],
        [6.350021, 24.71349],
        [6.350021, 24.38869],
        [5.781624, 22.11509],
        [5.619225, 21.79029],
        [5.456825, 21.14069],
        [5.294426, 20.81589],
        [5.132019, 20.16629],
        [4.96962, 19.84149],
        [4.88842, 19.51669],
        [3.10202, 15.94389],
        [2.858421, 15.61909],
        [2.696022, 15.29429],
        [2.452423, 14.96949],
        [2.127625, 14.31989],
        [1.884026, 13.99509],
        [1.721619, 13.67029],
        [1.234421, 13.02069],
        [1.072021, 12.69589],
        [-1.363976, 9.447891],
        [-1.526375, 9.123093],
        [-2.257179, 8.148689],
        [-2.581978, 7.90509],
        [-2.906776, 7.742691],
        [-3.231575, 7.661491],
        [-3.556381, 7.661491],
        [-4.205978, 7.823891],
        [-5.50518, 8.473488],
        [-5.829979, 8.554688],
        [-7.453979, 9.366692],
        [-7.778778, 9.447891],
        [-14.27478, 12.69589],
        [-14.59958, 12.77709],
        [-16.22358, 13.58909],
        [-16.54838, 13.67029],
        [-19.47158, 15.13189],
        [-19.71518, 15.37549],
        [-19.79638, 15.53789],
        [-19.71518, 15.70029],
        [-19.47158, 15.78149],
        [-19.14678, 15.78149],
        [-17.84758, 16.10629],
        [-13.94998, 16.10629],
        [-12.65078, 16.43109],
        [-11.02678, 16.43109],
        [-9.727577, 16.75589],
        [-9.402779, 16.75589],
        [-8.103577, 17.08069],
        [-7.778778, 17.08069],
        [-6.479576, 17.40549],
        [-6.154778, 17.40549],
        [-5.829979, 17.48669],
        [-5.50518, 17.64909],
        [-5.180382, 17.89269],
        [-4.936775, 18.21749],
        [-4.774376, 18.54229],
        [-4.774376, 18.86709],
        [-4.936775, 19.11069],
        [-5.180382, 19.27309],
        [-5.50518, 19.35429],
        [-7.129181, 19.35429],
        [-8.428375, 19.02949],
        [-11.67638, 19.02949],
        [-12.97558, 19.35429],
        [-13.30038, 19.35429],
        [-15.57398, 19.92269],
        [-15.89878, 20.08509],
        [-16.22358, 20.16629],
        [-19.14678, 21.62789],
        [-19.47158, 21.87149],
        [-19.79638, 22.03389],
        [-20.44598, 22.52109],
        [-20.77078, 22.68349],
        [-21.74518, 23.41429],
        [-22.39478, 24.06389],
        [-23.69398, 25.03829],
        [-25.31798, 26.66229],
        [-26.29238, 27.96149],
        [-27.91638, 29.58549],
        [-28.24118, 29.82909],
        [-28.56598, 29.91029],
        [-28.80958, 29.82909],
        [-28.97198, 29.58549],
        [-29.05318, 29.26069],
        [-29.05318, 28.61109],
        [-28.72838, 27.31189],
        [-28.72838, 26.66229],
        [-28.40358, 25.36309],
        [-28.40358, 25.03829],
        [-28.07878, 23.73909],
        [-28.07878, 23.41429],
        [-27.75398, 22.11509],
        [-27.75398, 21.79029],
        [-27.42918, 20.49109],
        [-27.42918, 20.16629],
        [-27.26678, 19.51669],
        [-27.26678, 18.86709],
        [-27.42918, 18.54229],
        [-27.67278, 18.29869],
        [-27.91638, 18.13629],
        [-28.24118, 17.97389],
        [-28.56598, 17.89269],
        [-29.21558, 17.56789],
        [-29.54038, 17.48669],
        [-29.86518, 17.32429],
        [-30.51478, 17.16189],
        [-30.83958, 16.99949],
        [-31.16438, 16.91829],
        [-31.81398, 16.59349],
        [-32.13878, 16.51229],
        [-32.46358, 16.34989],
        [-33.11318, 16.18749],
        [-33.43798, 16.02509],
        [-33.76278, 15.94389],
        [-34.08758, 15.78149],
        [-34.41238, 15.53789],
        [-34.57478, 15.29429],
        [-34.57478, 14.96949],
        [-34.41238, 14.64469],
        [-34.08758, 14.40109],
        [-33.43798, 14.07629],
        [-33.11318, 13.99509],
        [-30.51478, 12.69589],
        [-30.18998, 12.61469],
        [-29.86518, 12.45229],
        [-29.54038, 12.37109],
        [-24.01878, 9.610291],
        [-23.69398, 9.366692],
        [-23.36918, 9.204292],
        [-23.04438, 8.960693],
        [-22.39478, 8.635895],
        [-22.06998, 8.392288],
        [-21.74518, 8.229889],
        [-21.09558, 7.742691],
        [-20.77078, 7.580292],
        [-20.12118, 7.093094],
        [-19.79638, 6.930695],
        [-18.82198, 6.19989],
        [-17.52278, 4.900688],
        [-16.79198, 3.926292],
        [-16.62958, 3.601494],
        [-16.14238, 2.951889],
        [-15.97998, 2.62709],
        [-15.49277, 1.977493],
        [-15.33038, 1.652687],
        [-14.84318, 1.00309],
        [-14.68078, 0.6782913],
        [-14.43718, 0.3534927],
        [-14.11238, -0.2961121],
        [-13.86878, -0.6209106],
        [-13.70638, -0.9457092],
        [-13.46278, -1.270508],
        [-13.13798, -1.920113],
        [-12.89438, -2.244911],
        [-12.73198, -2.56971],
        [-12.48838, -2.894508],
        [-12.16358, -3.544113],
        [-11.91998, -3.868912],
        [-11.75758, -4.19371],
        [-11.51398, -4.518509],
        [-11.18918, -5.168106],
        [-10.94558, -5.492912],
        [-10.78318, -5.817711],
        [-10.53958, -6.142509],
        [-10.21478, -6.792107],
        [-9.971176, -7.116913],
        [-9.808777, -7.441711],
        [-9.565178, -7.76651],
        [-9.240379, -8.416107],
        [-8.99678, -8.740913],
        [-8.834381, -9.065712],
        [-8.590782, -9.390511],
        [-8.265976, -10.04011],
        [-8.022377, -10.36491],
        [-7.859978, -10.68971],
        [-7.616379, -11.01451],
        [-7.29158, -11.66411],
        [-7.047981, -11.98891],
        [-6.885582, -12.31371],
        [-6.641975, -12.63851],
        [-6.317177, -13.28811],
        [-6.073578, -13.61291],
        [-5.911179, -13.93771],
        [-5.66758, -14.26251],
        [-5.342781, -14.91211],
        [-5.099174, -15.23691],
        [-4.936775, -15.56171],
        [-4.693176, -15.88651],
        [-4.368378, -16.53611],
        [-4.124779, -16.86091],
        [-3.962379, -17.18571],
        [-3.718781, -17.51051],
        [-3.393974, -18.16011],
        [-3.150375, -18.48491],
        [-2.987976, -18.80971],
        [-2.744377, -19.13451],
        [-2.419579, -19.78411],
        [-2.17598, -20.10891],
        [-2.01358, -20.43371],
        [-1.769981, -20.75851],
        [-1.445175, -21.40811],
        [-1.201576, -21.73291],
        [-1.039177, -22.05771],
        [-0.795578, -22.38251],
        [-0.4707794, -23.03211],
        [-0.2271805, -23.35691],
        [-0.06478119, -23.68171],
        [0.1788254, -24.00651],
        [0.503624, -24.65611],
        [0.7472229, -24.98091],
        [0.9096222, -25.30571],
        [1.153221, -25.63051],
        [1.47802, -26.28011],
        [1.721619, -26.60491],
        [1.884026, -26.92971],
        [2.127625, -27.25451],
        [2.452423, -27.90411],
        [2.696022, -28.22891],
        [2.858421, -28.55371],
        [3.10202, -28.87851],
        [3.426819, -29.52811],
        [3.670425, -29.85291],
        [3.832825, -30.17771],
        [4.076424, -30.50251],
        [4.401222, -31.15211],
        [4.644821, -31.47691],
        [4.80722, -31.80171],
        [5.050819, -32.12651],
        [5.375626, -32.77611],
        [5.619225, -33.10091],
        [5.781624, -33.42571],
        [6.025223, -33.75051],
        [6.350021, -34.40011],
        [6.59362, -34.72491],
        [6.75602, -35.04971],
        [6.999626, -35.37451],
        [7.324425, -36.02411],
        [7.568024, -36.34891],
        [7.730423, -36.67371],
        [7.974022, -36.99851],
        [9.435623, -39.92171],
        [9.516823, -40.24651],
        [9.679222, -40.57131],
        [9.841621, -41.22091],
        [10.00402, -41.54571],
        [10.24762, -42.52011],
        [10.24762, -43.16971],
        [10.00402, -44.14411],
        [9.841621, -44.46891],
        [9.760422, -44.79371],
        [9.598022, -45.11852],
        [9.110825, -45.76811],
        [8.46122, -46.41771],
        [7.486824, -47.14851],
        [7.162025, -47.31091],
        [6.837219, -47.55451],
        [5.538025, -48.20411],
        [5.050819, -48.69131],
        [4.88842, -49.01611],
        [4.88842, -49.34091],
        [4.96962, -49.66571],
        [5.213219, -49.99051],
        [5.538025, -50.23412],
        [5.862823, -50.39651],
        [6.187622, -50.47771],
        [6.837219, -50.47771],
        [8.136421, -50.80251],
        [8.786026, -50.80251],
        [9.110825, -50.88371],
        [9.354424, -51.04611],
        [9.516823, -51.28972],
        [9.598022, -51.61452],
        [9.598022, -53.88811],
        [9.273224, -55.18732],
        [9.273224, -56.81131],
        [8.948425, -58.11052],
        [8.948425, -60.05931],
        [8.623619, -61.35851],
        [8.623619, -63.30731],
        [8.29882, -64.60651],
        [8.29882, -66.55531],
        [7.974022, -67.85451],
        [7.974022, -69.80331],
        [7.649223, -71.10251],
        [7.649223, -73.05132],
        [7.324425, -74.35051],
        [7.324425, -76.29932],
        [6.999626, -77.59851],
        [6.999626, -79.54732],
        [6.67482, -80.84651],
        [6.67482, -82.79532],
        [6.350021, -84.09451],
        [6.350021, -86.36812],
        [6.025223, -87.66731],
        [6.025223, -89.29132],
        [5.700424, -90.59052],
        [5.700424, -92.53931],
        [5.375626, -93.83852],
        [5.375626, -95.46251],
        [5.050819, -96.76172],
        [5.050819, -98.38571],
        [4.726021, -99.68492],
        [4.726021, -100.3345],
        [4.644821, -100.5781],
        [4.482422, -100.8217],
        [4.238823, -100.9841],
        [3.589226, -101.1465],
        [-32.78838, -101.1465],
        [-33.03198, -101.0653],
        [-33.19438, -100.9029],
        [-33.35678, -100.6593],
        [-33.51918, -100.0097],
        [-33.68158, -99.68492],
        [-33.84398, -99.03531],
        [-34.00638, -98.71051],
        [-34.08758, -98.38571],
        [-34.41238, -97.73611],
        [-34.49358, -97.41132],
        [-34.65598, -97.08652],
        [-34.81838, -96.43692],
        [-34.98078, -96.11211],
        [-35.22438, -95.13771],
        [-35.22438, -92.53931],
        [-34.89958, -91.24011],
        [-34.89958, -90.59052],
        [-34.57478, -89.29132],
        [-34.57478, -88.64171],
        [-34.24998, -87.34251],
        [-34.24998, -86.36812],
        [-33.92518, -85.06891],
        [-33.92518, -84.74411],
        [-33.60038, -83.44492],
        [-33.60038, -82.79532],
        [-33.27558, -81.49611],
        [-33.27558, -80.84651],
        [-32.95078, -79.54732],
        [-32.95078, -78.89772],
        [-32.62598, -77.59851],
        [-32.62598, -76.94891],
        [-32.30118, -75.64972],
        [-32.30118, -75.00011],
        [-31.97638, -73.70091],
        [-31.97638, -73.05132],
        [-31.65158, -71.75211],
        [-31.65158, -71.10251],
        [-31.32678, -69.80331],
        [-31.32678, -69.15372],
        [-31.00198, -67.85451],
        [-31.00198, -67.20491],
        [-30.67718, -65.90572],
        [-30.67718, -65.25612],
        [-30.35238, -63.95691],
        [-30.35238, -62.98251],
        [-30.02758, -61.68332],
        [-30.02758, -59.08492],
        [-29.70278, -57.78571],
        [-29.70278, -55.83691],
        [-30.02758, -54.5377],
        [-30.02758, -51.93932],
        [-30.51478, -49.99051],
        [-30.83958, -49.34091],
        [-30.92078, -49.01611],
        [-31.40798, -48.04171],
        [-31.65158, -47.71691],
        [-32.30118, -46.41771],
        [-32.54478, -46.09291],
        [-32.70718, -45.76811],
        [-33.19438, -45.11852],
        [-33.35678, -44.79371],
        [-33.60038, -44.46891],
        [-33.92518, -43.81931],
        [-34.16878, -43.49451],
        [-34.33118, -43.16971],
        [-34.81838, -42.52011],
        [-34.98078, -42.19531],
        [-35.46798, -41.54571],
        [-35.63038, -41.22091],
        [-35.87398, -40.89611],
        [-36.19878, -40.24651],
        [-36.44238, -39.92171],
        [-36.60478, -39.59691],
        [-37.09198, -38.94731],
        [-37.25438, -38.62251],
        [-37.74158, -37.97291],
        [-37.90398, -37.64811],
        [-38.14758, -37.32331],
        [-38.47238, -36.67371],
        [-38.71598, -36.34891],
        [-38.87838, -36.02411],
        [-39.12198, -35.69931],
        [-39.44678, -35.04971],
        [-39.69038, -34.72491],
        [-39.85278, -34.40011],
        [-40.33998, -33.75051],
        [-40.50238, -33.42571],
        [-40.98958, -32.77611],
        [-41.15198, -32.45131],
        [-41.39558, -32.12651],
        [-41.72038, -31.47691],
        [-41.96398, -31.15211],
        [-42.12638, -30.82731],
        [-42.61358, -30.17771],
        [-42.77598, -29.85291],
        [-43.01958, -29.52811],
        [-43.34438, -28.87851],
        [-43.58798, -28.55371],
        [-43.75038, -28.22891],
        [-44.23758, -27.57931],
        [-44.39998, -27.25451],
        [-44.64358, -26.92971],
        [-44.96838, -26.28011],
        [-45.21198, -25.95531],
        [-45.37438, -25.63051],
        [-45.86158, -24.98091],
        [-46.02398, -24.65611],
        [-46.51118, -24.00651],
        [-46.67358, -23.68171],
        [-46.91718, -23.35691],
        [-47.24198, -22.70731],
        [-47.48558, -22.38251],
        [-47.64798, -22.05771],
        [-48.13518, -21.40811],
        [-48.29758, -21.08331],
        [-48.78478, -20.43371],
        [-48.94718, -20.10891],
        [-49.19078, -19.78411],
        [-49.51558, -19.13451],
        [-49.75918, -18.80971],
        [-49.92158, -18.48491],
        [-50.40878, -17.83531],
        [-50.57118, -17.51051],
        [-51.05838, -16.86091],
        [-51.22078, -16.53611],
        [-51.46438, -16.21131],
        [-51.78918, -15.56171],
        [-52.03278, -15.23691],
        [-52.19518, -14.91211],
        [-52.68238, -14.26251],
        [-52.84478, -13.93771],
        [-53.33198, -13.28811],
        [-53.49438, -12.96331],
        [-53.73798, -12.63851],
        [-54.06278, -11.98891],
        [-54.30638, -11.66411],
        [-54.46878, -11.33931],
        [-54.95598, -10.68971],
        [-55.11838, -10.36491],
        [-55.60558, -9.715309],
        [-55.76798, -9.390511],
        [-56.01158, -9.065712],
        [-56.33638, -8.416107],
        [-56.57998, -8.091309],
        [-56.74238, -7.76651],
        [-57.22958, -7.116913],
        [-57.39198, -6.792107],
        [-57.87918, -6.142509],
        [-58.04158, -5.817711],
        [-58.28518, -5.492912],
        [-58.60998, -4.843307],
        [-58.85358, -4.518509],
        [-59.01598, -4.19371],
        [-59.50318, -3.544113],
        [-59.66558, -3.219307],
        [-60.15278, -2.56971],
        [-60.31518, -2.244911],
        [-60.55878, -1.920113],
        [-60.88358, -1.270508],
        [-61.12718, -0.9457092],
        [-61.28958, -0.6209106],
        [-61.77678, 0.02869415],
        [-61.93918, 0.3534927],
        [-62.42638, 1.00309],
        [-62.58878, 1.327888],
        [-63.07598, 1.977493],
        [-63.23838, 2.302292],
        [-63.48198, 2.62709],
        [-63.80678, 3.276688],
        [-64.05038, 3.601494],
        [-64.21278, 3.926292],
        [-64.69998, 4.57589],
        [-64.86238, 4.900688],
        [-65.34958, 5.550293],
        [-65.51198, 5.875092],
        [-65.75558, 6.19989],
        [-66.08038, 6.849487],
        [-66.32398, 7.174294],
        [-66.48638, 7.499092],
        [-66.72998, 7.823891],
        [-67.21718, 8.798294],
        [-67.29839, 9.123093],
        [-67.46078, 9.447891],
        [-68.02918, 11.72149],
        [-68.02918, 13.99509],
        [-67.70438, 15.29429],
        [-67.70438, 15.61909],
        [-67.54198, 16.26869],
        [-67.21718, 16.91829],
        [-67.13598, 17.24309],
        [-66.97358, 17.56789],
        [-66.89238, 17.89269],
        [-65.75558, 20.16629],
        [-65.51198, 20.49109],
        [-65.34958, 20.81589],
        [-64.86238, 21.46549],
        [-64.69998, 21.79029],
        [-64.21278, 22.43989],
        [-64.05038, 22.76469],
        [-60.39638, 27.63669],
        [-60.07158, 27.96149],
        [-59.09718, 29.26069],
        [-58.77238, 29.58549],
        [-57.79798, 30.88469],
        [-57.47318, 31.20949],
        [-56.49878, 32.50869],
        [-55.84918, 33.15829],
        [-54.87478, 34.45749],
        [-54.22518, 35.10709],
        [-53.25078, 36.40629],
        [-52.60118, 37.05589],
        [-51.62678, 38.35509],
        [-50.97718, 39.00469],
        [-50.00278, 40.30389],
        [-49.35318, 40.95349],
        [-48.37878, 42.25269],
        [-47.72918, 42.90229],
        [-46.75478, 44.20149],
        [-46.10518, 44.85109],
        [-45.13078, 46.15029],
        [-44.80598, 46.47509],
        [-43.83158, 47.77429],
        [-43.50678, 48.09909],
        [-42.53238, 49.39829],
        [-42.20758, 49.72309],
        [-41.23318, 51.02229],
        [-40.90838, 51.34709],
        [-39.93398, 52.64629],
        [-39.60918, 52.97109],
        [-38.63478, 54.27029],
        [-38.30998, 54.59509],
        [-37.33558, 55.89429],
        [-36.68598, 56.54389],
        [-36.36118, 56.78749],
        [-35.71158, 57.11229],
        [-35.06198, 57.27469],
        [35.41962, 47.69309],
        [35.74442, 47.44949],
        [39.31722, 43.87669],
        [40.61642, 42.90229],
        [45.81322, 37.70549],
        [47.11242, 36.73109],
        [50.68522, 33.15829],
        [51.17242, 32.50869],
        [51.33483, 32.18389],
        [51.49723, 31.53429],
        [51.49723, 31.20949],
        [51.33483, 30.55989],
        [51.17242, 30.23509],
        [50.92883, 29.91029],
        [50.76643, 29.58549],
        [50.03562, 28.61109],
        [48.41163, 26.98709],
        [47.43722, 25.68789],
        [45.48843, 23.73909],
        [44.51403, 22.43989],
        [42.56522, 20.49109],
        [41.59083, 19.19189],
        [39.31722, 16.91829],
        [38.34283, 15.61909],
        [36.39402, 13.67029],
        [35.41962, 12.37109],
        [33.47083, 10.42229],
        [32.49642, 9.123093],
        [30.54762, 7.174294],
        [29.57323, 5.875092],
        [27.62442, 3.926292],
        [26.65002, 2.62709],
        [24.37643, 0.3534927],
        [23.64562, -0.6209106],
        [23.40202, -0.8645096],
        [22.75243, -1.351707],
        [22.42762, -1.514107],
        [22.10282, -1.757706],
        [21.77802, -1.920113],
        [20.47882, -2.244911],
        [19.82922, -2.244911],
        [18.53002, -1.920113],
        [9.760422, 2.464691],
        [9.435623, 2.70829],
        [9.110825, 2.870689],
        [8.46122, 3.357887],
        [8.136421, 3.520294],
        [7.486824, 4.007492],
        [7.162025, 4.169891],
        [6.512421, 4.657089],
        [6.187622, 4.819489],
        [5.213219, 5.550293],
        [4.88842, 5.875092],
        [3.914024, 6.605888],
        [3.670425, 6.849487],
        [3.426819, 7.174294],
        [3.345619, 7.499092],
        [3.345619, 7.823891],
        [3.426819, 8.148689],
        [3.751625, 8.798294],
        [5.213219, 10.74709],
        [5.538025, 11.07189],
        [6.512421, 12.37109],
        [6.837219, 12.69589],
        [7.811623, 13.99509],
        [8.136421, 14.31989],
        [9.110825, 15.61909],
        [9.435623, 15.94389],
        [10.41002, 17.24309],
        [10.73483, 17.56789],
        [11.70922, 18.86709],
        [12.03402, 19.19189],
        [13.98283, 21.79029],
        [14.30762, 22.11509],
        [15.28202, 23.41429],
        [15.60682, 23.73909],
        [16.58122, 25.03829],
        [16.90602, 25.36309],
        [17.88042, 26.66229],
        [18.20522, 26.98709],
        [19.17963, 28.28629],
        [19.50443, 28.61109],
        [20.47882, 29.91029],
        [20.80362, 30.23509],
        [22.75243, 32.83349],
        [23.07722, 33.15829],
        [24.05162, 34.45749],
        [24.37643, 34.78229],
        [25.35082, 36.08149],
        [25.67562, 36.40629],
        [26.65002, 37.70549],
        [26.97482, 38.03029],
        [27.94923, 39.32949],
        [28.27402, 39.65429],
        [29.24842, 40.95349],
        [29.57323, 41.27829],
        [30.54762, 42.57749],
        [30.87242, 42.90229],
        [33.79562, 46.79989],
        [34.44522, 47.44949],
        [34.77003, 47.69309],
        [35.09483, 47.77429],
        [56.20683, 28.12389],
        [56.53162, 28.04269],
        [56.85642, 27.88029],
        [57.18122, 27.63669],
        [57.83082, 26.98709],
        [58.80523, 25.68789],
        [60.10442, 24.38869],
        [61.07882, 23.08949],
        [61.40362, 22.76469],
        [64.08323, 19.19189],
        [64.24563, 18.86709],
        [64.48922, 18.54229],
        [64.81402, 17.89269],
        [65.05762, 17.56789],
        [65.22002, 17.24309],
        [65.46363, 16.91829],
        [65.78843, 16.26869],
        [66.03202, 15.94389],
        [66.19442, 15.61909],
        [66.43803, 15.29429],
        [67.25002, 13.67029],
        [67.33123, 13.34549],
        [67.49363, 13.02069],
        [67.65603, 12.37109],
        [67.81843, 12.04629],
        [68.06202, 11.07189],
        [68.06202, 10.09749],
        [67.89962, 9.447891],
        [67.73722, 9.123093],
        [67.25002, 8.473488],
        [66.27563, 7.499092],
        [64.97642, 6.524689],
        [64.65162, 6.19989],
        [63.35242, 5.225494],
        [62.37803, 4.251091],
        [61.07882, 3.276688],
        [59.13003, 1.327888],
        [57.83082, 0.3534927],
        [56.53162, -0.9457092],
        [55.23243, -1.920113],
        [54.25802, -2.894508],
        [52.95882, -3.868912],
        [51.98443, -4.843307],
        [50.68522, -5.817711],
        [50.36042, -6.142509],
        [49.06123, -7.116913],
        [48.73643, -7.441711],
        [47.43722, -8.416107],
        [47.11242, -8.740913],
        [44.83883, -10.44611],
        [44.51403, -10.60851],
        [42.56522, -12.07011],
        [42.24043, -12.23251],
        [40.29162, -13.69411],
        [39.96682, -13.85651],
        [39.31722, -14.34371],
        [38.99242, -14.50611],
        [38.34283, -14.99331],
        [38.01802, -15.15571],
        [37.36842, -15.64291],
        [37.04362, -15.80531],
        [36.71883, -16.04891],
        [36.39402, -16.21131],
        [36.06922, -16.29251],
        [35.74442, -16.29251],
        [35.09483, -15.96771],
        [34.12042, -15.23691],
        [29.57323, -10.68971],
        [28.27402, -9.715309],
        [26.97482, -8.416107],
        [26.00042, -7.68531],
        [25.67562, -7.522911],
        [24.70123, -6.792107],
        [24.37643, -6.467308],
        [24.13282, -6.142509],
        [23.97042, -5.817711],
        [23.97042, -5.492912],
        [24.29522, -4.843307],
        [25.02602, -3.868912],
        [29.57323, 0.6782913],
        [30.54762, 1.977493],
        [35.41962, 6.849487],
        [36.39402, 8.148689],
        [40.61642, 12.37109],
        [41.59083, 13.67029],
        [46.46282, 18.54229],
        [47.43722, 19.84149],
        [51.65963, 24.06389],
        [52.63403, 25.36309],
        [53.93322, 26.66229],
        [55.55723, 27.88029],
        [55.88203, 28.04269],
        [-8.103577, 4.41349],
        [-6.804375, 4.088692],
        [-5.180382, 4.088692],
        [-3.88118, 3.763893],
        [-3.231575, 3.763893],
        [-1.932381, 3.439087],
        [-1.607574, 3.439087],
        [3.26442, 2.221092],
        [3.589226, 2.058693],
        [4.238823, 1.896294],
        [4.563622, 1.733894],
        [5.213219, 1.571487],
        [5.538025, 1.409088],
        [6.187622, 1.246689],
        [6.512421, 1.08429],
        [6.837219, 1.00309],
        [7.486824, 0.6782913],
        [7.811623, 0.5970917],
        [8.136421, 0.4346924],
        [8.46122, 0.3534927],
        [9.760422, -0.2961121],
        [10.08522, -0.3773117],
        [10.41002, -0.539711],
        [10.73483, -0.6209106],
        [12.35883, -1.432907],
        [12.68362, -1.676506],
        [13.00842, -1.838913],
        [13.33322, -2.082512],
        [15.28202, -3.056908],
        [15.60682, -3.300507],
        [15.93163, -3.462906],
        [16.58122, -3.950111],
        [16.90602, -4.112511],
        [17.55563, -4.599709],
        [17.88042, -4.762108],
        [18.20522, -5.005707],
        [18.85482, -5.330513],
        [22.10282, -7.76651],
        [22.42762, -8.091309],
        [23.72682, -9.065712],
        [26.00042, -11.33931],
        [27.29962, -12.31371],
        [31.52203, -16.53611],
        [35.09483, -19.21571],
        [35.74442, -19.37811],
        [36.06922, -19.37811],
        [36.39402, -19.21571],
        [36.71883, -19.13451],
        [37.04362, -18.97211],
        [37.36842, -18.72851],
        [37.69322, -18.56611],
        [38.01802, -18.32251],
        [38.66763, -17.99771],
        [38.99242, -17.75411],
        [39.31722, -17.59171],
        [39.96682, -17.10451],
        [40.29162, -16.94211],
        [40.94123, -16.45491],
        [41.26603, -16.29251],
        [41.91563, -15.80531],
        [42.24043, -15.64291],
        [42.89002, -15.15571],
        [43.21482, -14.99331],
        [43.86442, -14.50611],
        [44.18922, -14.34371],
        [46.13802, -12.88211],
        [46.46282, -12.71971],
        [48.41163, -11.25811],
        [48.73643, -11.09571],
        [50.68522, -9.634109],
        [51.01002, -9.47171],
        [56.53162, -5.330513],
        [56.85642, -5.168106],
        [57.10003, -5.168106],
        [57.26243, -5.249313],
        [57.34362, -5.492912],
        [57.34362, -7.76651],
        [57.01882, -9.065712],
        [57.01882, -11.33931],
        [56.69402, -12.63851],
        [56.69402, -13.28811],
        [56.36922, -14.58731],
        [56.36922, -15.56171],
        [56.04443, -16.86091],
        [56.04443, -17.18571],
        [55.71963, -18.48491],
        [55.71963, -18.80971],
        [55.39483, -20.10891],
        [55.39483, -20.43371],
        [55.07003, -21.73291],
        [55.07003, -22.05771],
        [54.42042, -24.65611],
        [54.42042, -24.98091],
        [53.52723, -28.55371],
        [53.36483, -28.87851],
        [52.30923, -33.10091],
        [51.98443, -33.75051],
        [51.65963, -35.04971],
        [51.33483, -35.69931],
        [51.25362, -36.02411],
        [51.09122, -36.34891],
        [50.92883, -36.99851],
        [50.76643, -37.32331],
        [50.60403, -37.97291],
        [50.44163, -38.29771],
        [50.36042, -38.62251],
        [50.03562, -39.27211],
        [49.95443, -39.59691],
        [49.79203, -39.92171],
        [49.71082, -40.24651],
        [48.24923, -43.16971],
        [48.00562, -43.49451],
        [47.84322, -43.81931],
        [47.59962, -44.14411],
        [47.27482, -44.79371],
        [47.03123, -45.11852],
        [46.86883, -45.44331],
        [46.38163, -46.09291],
        [46.21923, -46.41771],
        [45.73202, -47.06731],
        [45.56962, -47.39211],
        [43.86442, -49.66571],
        [42.56522, -50.9649],
        [41.59083, -52.26411],
        [40.29162, -53.56331],
        [38.58643, -55.83691],
        [38.42403, -56.16171],
        [37.93682, -56.81131],
        [37.77442, -57.13611],
        [37.53082, -57.46091],
        [37.04362, -58.43532],
        [36.96243, -58.76012],
        [36.80003, -59.08492],
        [36.71883, -59.40971],
        [36.39402, -60.05931],
        [35.90682, -62.00812],
        [35.90682, -62.33292],
        [35.58202, -63.63211],
        [35.58202, -65.58092],
        [35.25723, -66.88011],
        [35.25723, -79.87212],
        [34.93243, -81.17131],
        [34.93243, -98.71051],
        [34.52642, -100.3345],
        [34.36402, -100.5781],
        [34.12042, -100.7405],
        [33.79562, -100.8217],
        [10.08522, -100.8217],
        [9.922821, -100.7405],
        [9.841621, -100.5781],
        [9.841621, -100.3345],
        [9.922821, -100.0097],
        [9.922821, -98.38571],
        [10.24762, -97.08652],
        [10.24762, -95.13771],
        [10.57243, -93.83852],
        [10.57243, -91.56491],
        [10.89722, -90.26572],
        [10.89722, -88.31691],
        [11.22202, -87.01772],
        [11.22202, -84.74411],
        [11.54682, -83.44492],
        [11.54682, -81.17131],
        [11.87162, -79.87212],
        [11.87162, -77.59851],
        [12.19642, -76.29932],
        [12.19642, -74.35051],
        [12.52122, -73.05132],
        [12.52122, -70.45291],
        [12.84602, -69.15372],
        [12.84602, -66.88011],
        [13.17082, -65.58092],
        [13.17082, -63.30731],
        [13.49562, -62.00812],
        [13.49562, -59.73451],
        [13.82042, -58.43532],
        [13.82042, -56.16171],
        [14.14523, -54.86252],
        [14.14523, -52.91371],
        [14.38882, -51.93932],
        [14.55122, -51.69571],
        [14.71362, -51.53331],
        [14.95722, -51.45212],
        [16.25642, -51.77692],
        [18.53002, -51.77692],
        [19.82922, -52.10172],
        [20.15402, -52.02051],
        [20.39762, -51.85811],
        [20.56002, -51.61452],
        [20.64122, -51.28972],
        [20.47882, -50.64011],
        [19.99162, -49.66571],
        [19.74802, -49.34091],
        [19.58562, -49.01611],
        [19.34203, -48.69131],
        [18.36762, -46.74251],
        [18.12402, -46.41771],
        [17.96162, -46.09291],
        [17.71803, -45.76811],
        [16.41882, -43.16971],
        [16.17522, -42.84491],
        [16.01283, -42.52011],
        [15.76923, -42.19531],
        [14.47002, -39.59691],
        [14.22643, -39.27211],
        [14.06403, -38.94731],
        [13.82042, -38.62251],
        [12.84602, -36.67371],
        [12.60242, -36.34891],
        [12.44003, -36.02411],
        [12.19642, -35.69931],
        [11.22202, -33.75051],
        [10.97842, -33.42571],
        [10.81602, -33.10091],
        [10.57243, -32.77611],
        [9.273224, -30.17771],
        [9.029625, -29.85291],
        [8.867226, -29.52811],
        [8.623619, -29.20331],
        [7.649223, -27.25451],
        [7.405624, -26.92971],
        [7.243225, -26.60491],
        [6.999626, -26.28011],
        [5.700424, -23.68171],
        [5.456825, -23.35691],
        [5.294426, -23.03211],
        [5.050819, -22.70731],
        [3.751625, -20.10891],
        [3.508018, -19.78411],
        [3.345619, -19.45931],
        [3.10202, -19.13451],
        [2.127625, -17.18571],
        [1.884026, -16.86091],
        [1.721619, -16.53611],
        [1.47802, -16.21131],
        [0.1788254, -13.61291],
        [-0.06478119, -13.28811],
        [-0.2271805, -12.96331],
        [-0.4707794, -12.63851],
        [-1.445175, -10.68971],
        [-1.688782, -10.36491],
        [-1.851181, -10.04011],
        [-2.09478, -9.715309],
        [-3.393974, -7.116913],
        [-3.637581, -6.792107],
        [-3.79998, -6.467308],
        [-4.043579, -6.142509],
        [-5.342781, -3.544113],
        [-5.58638, -3.219307],
        [-5.748779, -2.894508],
        [-5.992378, -2.56971],
        [-6.966782, -0.6209106],
        [-7.210381, -0.2961121],
        [-7.37278, 0.02869415],
        [-7.616379, 0.3534927],
        [-9.240379, 3.601494],
        [-9.321579, 3.845093],
        [-9.240379, 4.007492],
        [-9.07798, 4.169891],
        [-8.428375, 4.332291],
      ],
      paths=[
        [
          0,
          1,
          2,
          3,
          4,
          5,
          6,
          7,
          8,
          9,
          10,
          11,
          12,
          13,
          14,
          15,
          16,
          17,
          18,
          19,
          20,
          21,
          22,
          23,
          24,
          25,
          26,
          27,
          28,
          29,
          30,
          31,
          32,
          33,
          34,
          35,
          36,
          37,
          38,
          39,
          40,
          41,
          42,
          43,
          44,
          45,
          46,
          47,
          48,
          49,
          50,
          51,
          52,
          53,
          54,
          55,
          56,
          57,
          58,
          59,
          60,
          61,
          62,
          63,
          64,
          65,
          66,
          67,
          68,
          69,
          70,
          71,
          72,
          73,
          74,
          75,
          76,
          77,
          78,
          79,
          80,
          81,
          82,
          83,
          84,
          85,
          86,
          87,
          88,
          89,
          90,
          91,
          92,
          93,
          94,
          95,
          96,
          97,
          98,
          99,
          100,
          101,
          102,
          103,
          104,
          105,
          106,
          107,
          108,
          109,
          110,
          111,
          112,
          113,
          114,
          115,
          116,
          117,
          118,
          119,
          120,
          121,
          122,
          123,
          124,
          125,
        ],
        [
          126,
          127,
          128,
          129,
          130,
          131,
          132,
          133,
          134,
          135,
          136,
          137,
          138,
          139,
          140,
          141,
          142,
          143,
          144,
          145,
          146,
          147,
          148,
          149,
          150,
          151,
          152,
          153,
          154,
          155,
          156,
          157,
          158,
          159,
          160,
          161,
          162,
          163,
          164,
          165,
          166,
          167,
          168,
          169,
          170,
          171,
          172,
          173,
          174,
          175,
          176,
          177,
          178,
          179,
          180,
          181,
          182,
          183,
          184,
          185,
          186,
          187,
          188,
          189,
          190,
          191,
          192,
          193,
          194,
          195,
          196,
          197,
          198,
          199,
          200,
          201,
          202,
          203,
          204,
          205,
          206,
          207,
          208,
          209,
          210,
          211,
          212,
          213,
          214,
          215,
          216,
          217,
          218,
          219,
          220,
          221,
          222,
          223,
          224,
          225,
          226,
          227,
          228,
          229,
          230,
          231,
          232,
          233,
          234,
          235,
          236,
          237,
          238,
          239,
        ],
        [
          240,
          241,
          242,
          243,
          244,
          245,
          246,
          247,
          248,
          249,
          250,
          251,
          252,
          253,
          254,
          255,
          256,
          257,
          258,
          259,
          260,
          261,
          262,
          263,
          264,
          265,
          266,
          267,
          268,
          269,
          270,
          271,
          272,
          273,
          274,
          275,
          276,
          277,
          278,
          279,
          280,
          281,
          282,
          283,
          284,
          285,
          286,
          287,
          288,
          289,
          290,
          291,
          292,
          293,
          294,
          295,
          296,
          297,
          298,
          299,
          300,
          301,
          302,
          303,
          304,
          305,
          306,
          307,
          308,
          309,
          310,
          311,
          312,
          313,
          314,
          315,
          316,
          317,
          318,
          319,
          320,
          321,
          322,
          323,
          324,
          325,
          326,
          327,
          328,
          329,
          330,
          331,
          332,
          333,
          334,
          335,
          336,
          337,
          338,
          339,
          340,
          341,
          342,
          343,
          344,
          345,
          346,
          347,
          348,
          349,
          350,
          351,
          352,
          353,
          354,
          355,
          356,
          357,
          358,
          359,
          360,
          361,
          362,
          363,
          364,
          365,
          366,
          367,
          368,
          369,
          370,
          371,
          372,
          373,
          374,
          375,
          376,
          377,
          378,
          379,
          380,
          381,
          382,
          383,
          384,
          385,
          386,
          387,
          388,
          389,
          390,
          391,
          392,
          393,
          394,
          395,
          396,
          397,
          398,
          399,
          400,
          401,
          402,
          403,
          404,
          405,
          406,
          407,
          408,
          409,
          410,
          411,
          412,
          413,
          414,
          415,
          416,
          417,
          418,
          419,
          420,
          421,
          422,
          423,
          424,
          425,
          426,
          427,
          428,
          429,
          430,
          431,
          432,
          433,
          434,
          435,
          436,
          437,
          438,
          439,
          440,
          441,
          442,
          443,
          444,
          445,
          446,
          447,
          448,
          449,
          450,
          451,
          452,
          453,
          454,
          455,
          456,
          457,
          458,
          459,
          460,
          461,
          462,
          463,
          464,
          465,
          466,
          467,
          468,
          469,
          470,
          471,
          472,
          473,
          474,
          475,
          476,
          477,
          478,
          479,
          480,
          481,
          482,
          483,
          484,
          485,
          486,
          487,
          488,
          489,
          490,
          491,
          492,
          493,
          494,
          495,
          496,
          497,
          498,
          499,
          500,
          501,
          502,
          503,
          504,
          505,
          506,
          507,
          508,
          509,
          510,
          511,
          512,
          513,
          514,
          515,
          516,
          517,
          518,
          519,
          520,
          521,
          522,
          523,
          524,
          525,
          526,
          527,
          528,
          529,
          530,
          531,
          532,
          533,
          534,
          535,
          536,
          537,
          538,
          539,
          540,
          541,
          542,
          543,
          544,
          545,
          546,
          547,
          548,
          549,
          550,
          551,
          552,
          553,
          554,
          555,
          556,
          557,
          558,
          559,
          560,
          561,
          562,
          563,
          564,
          565,
          566,
          567,
          568,
          569,
          570,
          571,
          572,
          573,
          574,
          575,
          576,
          577,
          578,
          579,
          580,
          581,
          582,
          583,
          584,
          585,
          586,
          587,
          588,
          589,
          590,
          591,
          592,
          593,
          594,
          595,
          596,
          597,
          598,
          599,
          600,
          601,
          602,
          603,
          604,
          605,
          606,
          607,
          608,
          609,
          610,
          611,
          612,
          613,
          614,
          615,
          616,
          617,
          618,
          619,
          620,
          621,
          622,
          623,
          624,
          625,
          626,
          627,
          628,
          629,
          630,
          631,
          632,
          633,
          634,
          635,
          636,
          637,
          638,
          639,
          640,
          641,
          642,
          643,
          644,
          645,
          646,
          647,
          648,
          649,
          650,
          651,
          652,
          653,
          654,
          655,
          656,
          657,
          658,
          659,
          660,
          661,
          662,
          663,
          664,
          665,
          666,
          667,
          668,
          669,
          670,
          671,
          672,
          673,
          674,
          675,
          676,
          677,
          678,
          679,
          680,
          681,
          682,
          683,
          684,
          685,
          686,
          687,
          688,
          689,
          690,
          691,
          692,
          693,
          694,
          695,
          696,
          697,
          698,
          699,
          700,
          701,
          702,
          703,
          704,
          705,
          706,
          707,
          708,
          709,
          710,
          711,
          712,
          713,
          714,
          715,
          716,
          717,
          718,
          719,
          720,
          721,
          722,
          723,
          724,
          725,
          726,
          727,
          728,
          729,
          730,
          731,
          732,
          733,
          734,
          735,
          736,
          737,
          738,
          739,
          740,
          741,
          742,
          743,
          744,
          745,
          746,
          747,
          748,
          749,
          750,
          751,
          752,
          753,
          754,
          755,
          756,
          757,
          758,
          759,
          760,
          761,
          762,
          763,
          764,
          765,
          766,
          767,
          768,
          769,
          770,
          771,
          772,
          773,
          774,
          775,
          776,
          777,
          778,
          779,
          780,
          781,
          782,
          783,
          784,
          785,
          786,
          787,
          788,
          789,
          790,
          791,
          792,
          793,
          794,
          795,
          796,
          797,
          798,
          799,
          800,
          801,
          802,
          803,
          804,
          805,
          806,
          807,
        ],
        [
          808,
          809,
          810,
          811,
          812,
          813,
          814,
          815,
          816,
          817,
          818,
          819,
          820,
          821,
          822,
          823,
          824,
          825,
          826,
          827,
          828,
          829,
          830,
          831,
          832,
          833,
          834,
          835,
          836,
          837,
          838,
          839,
          840,
          841,
          842,
          843,
          844,
          845,
          846,
          847,
          848,
          849,
          850,
          851,
          852,
          853,
          854,
          855,
          856,
          857,
          858,
          859,
          860,
          861,
          862,
          863,
          864,
          865,
          866,
          867,
          868,
          869,
          870,
          871,
          872,
          873,
          874,
          875,
          876,
          877,
          878,
          879,
          880,
          881,
          882,
          883,
          884,
          885,
          886,
          887,
          888,
          889,
          890,
          891,
          892,
          893,
          894,
          895,
          896,
          897,
          898,
          899,
          900,
          901,
          902,
          903,
          904,
          905,
          906,
          907,
          908,
          909,
        ],
        [
          910,
          911,
          912,
          913,
          914,
          915,
          916,
          917,
          918,
          919,
          920,
          921,
          922,
          923,
          924,
          925,
          926,
          927,
          928,
          929,
          930,
          931,
          932,
          933,
          934,
          935,
          936,
          937,
          938,
          939,
          940,
          941,
          942,
          943,
          944,
          945,
          946,
          947,
          948,
          949,
          950,
          951,
          952,
          953,
          954,
          955,
          956,
          957,
          958,
          959,
          960,
          961,
          962,
          963,
          964,
          965,
          966,
          967,
          968,
          969,
          970,
          971,
          972,
          973,
          974,
          975,
          976,
          977,
          978,
          979,
          980,
          981,
          982,
          983,
          984,
          985,
          986,
          987,
          988,
          989,
          990,
          991,
          992,
          993,
          994,
          995,
          996,
          997,
          998,
          999,
          1000,
          1001,
        ],
        [
          1002,
          1003,
          1004,
          1005,
          1006,
          1007,
          1008,
          1009,
          1010,
          1011,
          1012,
          1013,
          1014,
          1015,
          1016,
          1017,
          1018,
          1019,
          1020,
          1021,
          1022,
          1023,
          1024,
          1025,
          1026,
          1027,
          1028,
          1029,
          1030,
          1031,
          1032,
          1033,
          1034,
          1035,
          1036,
          1037,
          1038,
          1039,
          1040,
          1041,
          1042,
          1043,
          1044,
          1045,
          1046,
          1047,
          1048,
          1049,
          1050,
          1051,
          1052,
          1053,
          1054,
          1055,
          1056,
          1057,
          1058,
          1059,
          1060,
          1061,
          1062,
          1063,
          1064,
          1065,
          1066,
          1067,
          1068,
          1069,
          1070,
          1071,
          1072,
          1073,
          1074,
          1075,
          1076,
          1077,
          1078,
          1079,
          1080,
          1081,
          1082,
          1083,
          1084,
          1085,
          1086,
          1087,
          1088,
          1089,
          1090,
          1091,
          1092,
          1093,
          1094,
          1095,
          1096,
          1097,
          1098,
          1099,
          1100,
          1101,
          1102,
          1103,
          1104,
          1105,
          1106,
          1107,
          1108,
          1109,
          1110,
          1111,
          1112,
          1113,
          1114,
          1115,
          1116,
          1117,
          1118,
          1119,
          1120,
          1121,
          1122,
          1123,
          1124,
          1125,
          1126,
          1127,
          1128,
          1129,
          1130,
          1131,
          1132,
          1133,
          1134,
          1135,
          1136,
          1137,
          1138,
          1139,
          1140,
          1141,
          1142,
          1143,
          1144,
          1145,
          1146,
          1147,
          1148,
          1149,
          1150,
          1151,
          1152,
          1153,
          1154,
          1155,
          1156,
          1157,
          1158,
          1159,
          1160,
          1161,
          1162,
          1163,
          1164,
          1165,
          1166,
          1167,
          1168,
          1169,
          1170,
          1171,
          1172,
          1173,
          1174,
          1175,
          1176,
          1177,
          1178,
          1179,
          1180,
          1181,
          1182,
          1183,
          1184,
          1185,
          1186,
          1187,
          1188,
          1189,
          1190,
          1191,
          1192,
          1193,
          1194,
          1195,
          1196,
          1197,
          1198,
          1199,
          1200,
          1201,
          1202,
          1203,
          1204,
          1205,
          1206,
          1207,
          1208,
          1209,
          1210,
          1211,
          1212,
          1213,
          1214,
          1215,
          1216,
          1217,
          1218,
          1219,
          1220,
          1221,
          1222,
          1223,
          1224,
          1225,
          1226,
          1227,
          1228,
          1229,
          1230,
          1231,
          1232,
          1233,
          1234,
          1235,
          1236,
          1237,
          1238,
          1239,
          1240,
          1241,
          1242,
          1243,
          1244,
          1245,
          1246,
          1247,
          1248,
          1249,
          1250,
          1251,
          1252,
          1253,
          1254,
          1255,
          1256,
          1257,
          1258,
          1259,
          1260,
          1261,
        ],
      ],
    );
  }
}
;

// Module: Fist2dOutline()
// Description:
//   Outline of a fst
// Arguments:
//   size = size of the fist
//   line_width = width of the line (default 1)
module Fist2dOutline(size, line_width) {
  DifferenceWithOffset(-line_width) Fist2d(size);
}

// Module: Leaf2d()
// Description:
//   Makes a nice leaf.
// Arguments:
//   size = size of the leaf
module Leaf2d(size) {
  module LeafHalf() {
    hull() {
      translate([0, 0.125]) circle(d=0.25);
      translate([11, 23]) circle(d=8, $fn=64);
      translate([14, 48]) circle(d=8, $fn=64);
      translate([0, 98.125]) circle(d=0.25);
    }
  }

  resize([size / 100 * 18 * 2, size]) translate([0, -50]) {
      LeafHalf();
      mirror([1, 0]) LeafHalf();
    }
}

// Module: LaurelWreath2d()
// Description:
//   Makes a laurel wreathe for use all over the place
// Arguments:
//   size = size of the laurel
module LaurelWreath2d(size) {

  module TwoLeafs() {
    rotate(270) translate([0, -25]) {
        translate([0, 50]) rotate(60) mirror([0, 1]) Leaf2d(100);
        rotate(-60) Leaf2d(100);
      }
  }
  module HalfLaurel() {
    translate([-150, 0]) rotate(-50) {
        nleafs = 10;
        for (angle = [30:140 / nleafs:160 - 1])
          rotate([0, 0, angle - (angle - 30) / 180 * 80]) translate([300 + (angle / 180) * 600, 0, 0])
              rotate(-30) TwoLeafs();
      }
  }
  basic_height = 859.35;
  basic_length = 1021.31;
  scale = size / basic_length;
  resize([size, scale * basic_height]) translate([0, -230]) {
      HalfLaurel();
      mirror([1, 0]) HalfLaurel();
    }
}

// Module: Anvil2d()
// Description:
//    Makes a nice 2d anvil.
// Arguments:
//    size = size of the anvil
//    with_hammer = show a hammer on the anvil and spark too
// Example(2D):
//   Anvil2d(30);
// Example(2D):
//   Anvil2d(30, with_hammer = true);
module Anvil2d(size, with_hammer = false) {
  new_height = with_hammer ? size : size * 10 / 18;
  resize([size, new_height]) translate([4, with_hammer ? -8.5 : -4.5]) {
      rect([10, 1]);
      translate([0, 1.7]) rect([8, 1.5]);
      translate([0, 3.3]) rect([10, 1]);
      translate([0, 6.8]) rect([10, 6]);
      translate([-8, 6.8]) intersection() {
          rect([10, 6]);
          translate([6, 8]) circle(12, $fn=64);
        }
      if (with_hammer) {
        translate([-10, 12]) rotate(30) rect([5, 1]);
        translate([-8, 13.3]) rotate(-60) rect([4, 3], rounding=0.5);
        hull() {
          translate([-4, 11]) circle(d=0.5);
          translate([-3, 11]) circle(d=0.5);
          translate([3, 16.5]) circle(d=1);
        }
        hull() {
          translate([-2, 11]) circle(d=0.5);
          translate([-3, 11]) circle(d=0.5);
          translate([4, 14.5]) circle(d=1);
        }
        hull() {
          translate([-1, 11]) circle(d=0.5);
          translate([-2, 11]) circle(d=0.5);
          translate([4, 12]) circle(d=1);
        }
      }
    }
}

// Module: HalfEye2d()
// Description:
//   Makes a single eye for use in various things where eyes are needed.  This is a half eye on an angle.
// Arguments:
//   angle = angle the eye is on
//   outer_size = size of the outside circle.
//   inner_size = size of the inside circle
//   pupil_size = size of the pupil
// Example:
//   HalfEye2d(30);
// Example:
//   HalfEye2d(60);
// Example:
//   translate([-6, 0, 0]) HalfEye2d(60);
//   translate([6, 0, 0]) mirror([1, 0]) HalfEye2d(60);
//   // Nose.
//   translate([0, -4, 0]) {
//     circle(d=3);
//     translate([0, -2]) {
//       rect([1, 3]);
//       translate([-3, -1.5]) ring(r1=2.5, r2=3, angle=[360, 180], n=32);
//       translate([3, -1.5]) mirror([1, 0]) ring(r1=2.5, r2=3, angle=[360, 180], n=32);
//     }
//   }
module HalfEye2d(angle, outer_size = 10, inner_size = 8, pupil_size = 5) {
  difference() {
    union() {
      difference() {
        circle(d=outer_size);
        circle(d=inner_size);
      }
      circle(d=pupil_size);
    }
    translate([outer_size * cos(angle), outer_size * sin(angle)]) rotate(angle)
        rect([outer_size * 2, outer_size * 2]);
  }
  rotate(angle + 90) rect([outer_size, (outer_size - inner_size) / 2]);
}

// Module: SideEye2d()
// Description:
//   Makes a single eye for use in various things where eyes are needed.  This is a half eye on an angle.
// Arguments:
//   angle = angle the pupil is at
//   outer_size = size of the outside circle.
//   inner_size = size of the inside circle
//   pupil_size = size of the pupil
// Example:
//   SideEye2d(30);
// Example:
//   SideEye2d(90);
// Example:
//   translate([6, 0, 0]) SideEye2d(90);
//   translate([-6, 0, 0]) SideEye2d(90);
//   translate([0, -4, 0]) {
//     translate([1, 0.6]) rotate(30) rect([4, 1]);
//     translate([-1, 0.6]) rotate(150) rect([4, 1]);
//     circle(d=3);
//   }
module SideEye2d(angle, outer_size = 10, inner_size = 8, pupil_size = 5) {
  difference() {
    circle(d=outer_size);
    circle(d=inner_size);
  }
  intersection() {
    translate([outer_size / 3 * cos(angle), outer_size / 3 * sin(angle)]) circle(d=pupil_size);
    circle(d=outer_size);
  }
}

// Module: CloudShape2d()
// Description:
//   Makes a cloud object.  This object was made by Twanne on thingiverse:
//   https://www.thingiverse.com/thing:641665/files
// Arguments:
//   width = The width of the cloud. This also determine the height, because the height is half the width.
//   height = Height of the object.
//   line_width = width of the outside line (0 if no line)
// Example:
//   CloudShape2d(100);
module CloudShape2d(width) {
  union() {
    translate([width * .37, width * .25, 0]) circle(r=width * .25, $fn=16);
    translate([width * .15, width * .2, 0]) circle(r=width * .15, $fn=16);
    translate([width * .65, width * .22, 0]) circle(r=width * .2, $fn=16);
    translate([width * .85, width * .2, 0]) circle(r=width * .15, $fn=16);
  }
}

// Module: SingleLog2d()
// Description:
//   A single log image.
// Arguments:
//   size = size of the log
//   line_width= width of the line
// Example(2D):
//   SingleLog2d(15);
module SingleLog2d(size, line_width = 1) {
  // 35.00 25.00
  resize([size, size / 35 * 25]) translate([-10, -5]) {
      DifferenceWithOffset(offset=-line_width) circle(d=size);
      difference() {
        DifferenceWithOffset(offset=-line_width / 2) circle(d=size * 7 / 10);
        translate([size * 5 / 7, -size * 4 / 7]) rect([size, size]);
        translate([-size * 3 / 5, -size * 4 / 7]) rect([size, size]);
      }
      difference() {
        DifferenceWithOffset(offset=-line_width / 2) circle(d=size * 4 / 10);
        translate([-size / 2, size / 2]) rect([size, size]);
        translate([-size * 4 / 7, -size * 4 / 7]) rect([size, size]);
      }
      DifferenceWithOffset(offset=-line_width) hull() {
          circle(d=size);
          translate([20, 10]) circle(d=size);
        }
      polygon([[8, 0.5], [8, -0.5], [26, 9], [26, 10]]);
      polygon([[4, 7.5], [4, 6.5], [22.5, 15.7], [21, 16]]);
      polygon([[7, 3], [7, 4], [25, 13], [25, 12]]);
    }
}

// Module: Tower2d()
// Description:
//    Make a single keep tower for use in gams and stuff.
// Arguments:
//    size = size of the tower
// Example(2D):
//    Tower2d(20);
module Tower2d(size) {
  translate([0, -size / 4]) {
    top_size = size / 8;
    // bottom of top.
    translate([-size / 2 + top_size * 3 / 2, 0]) hull() {
        translate([0, size / 2 - top_size / 2]) circle(r=top_size / 2);
        translate([0, top_size / 2]) circle(r=top_size / 2);
      }
    // Crown bits.
    crown_length = size / 2 / 5;
    for (i = [0:2:5]) {
      hull() {
        translate([-size / 2 + top_size / 2, size / 2 - top_size / 2 - crown_length * i])
          circle(r=top_size / 2);
        translate([-size / 2 + top_size / 2 + top_size, size / 2 - top_size / 2 - crown_length * i])
          circle(r=top_size / 2);
      }
    }
    // Side tower.
    polygon(
      [
        [-size / 2 + top_size, top_size / 2],
        [size / 2, top_size / 2],
        [size / 2, size / 2 - top_size / 2],
        [-size / 2 + top_size, size / 2 - top_size / 2],
      ],
    );
  }
}

// Module: Sign2d()
// Description:
//   Makes a sign shape to use for stuff.
// Arguments:
//   size = size of the sign
module Sign2d(size) {
  difference() {
    rect([size / 10, size * 3 / 4]);
    translate([0, size * 1.5 / 4 - size / 4 - size / 20]) rect([size, size / 2]);
  }
  DifferenceWithOffset(-1) translate([0, size * 1.5 / 4 - size / 4 - size / 20]) rect([size, size / 2]);
}

// Function: ShapeNeedsInnerControl()
// Description:
//   If the specified shape needs inner control
// Arguments:
//   shnape_type = the type of shape to check
function ShapeNeedsInnerControl(shape_type) =
  (shape_type == SHAPE_TYPE_PENTAGON_R1 || shape_type == SHAPE_TYPE_PENTAGON_R2 || shape_type == SHAPE_TYPE_PENTAGON_R3 || shape_type == SHAPE_TYPE_PENTAGON_R4 || shape_type == SHAPE_TYPE_PENTAGON_R5 || shape_type == SHAPE_TYPE_PENTAGON_R6 || shape_type == SHAPE_TYPE_PENTAGON_R7 || shape_type == SHAPE_TYPE_PENTAGON_R8 || shape_type == SHAPE_TYPE_PENTAGON_R9 || shape_type == SHAPE_TYPE_PENTAGON_R10 || shape_type == SHAPE_TYPE_PENTAGON_R11 || shape_type == SHAPE_TYPE_PENTAGON_R12 || shape_type == SHAPE_TYPE_PENTAGON_R13 || shape_type == SHAPE_TYPE_PENTAGON_R14 || shape_type == SHAPE_TYPE_PENTAGON_R15 || shape_type == SHAPE_TYPE_ESCHER_LIZARD || shape_type == SHAPE_TYPE_LEAF || shape_type == SHAPE_TYPE_HALF_REGULAR_HEXAGON || shape_type == SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL) ?
    1
  : (shape_type == SHAPE_TYPE_VORONOI || shape_type == SHAPE_TYPE_PENROSE_TILING_5 || shape_type == SHAPE_TYPE_PENROSE_TILING_7 ? 2 : 0);

// Module: ShapeByType()
// Description:
//   Creates shapes by a specific type to use in the lids.  This is pulled out so the shape creation
//   layout are handled independantly.
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, shape_width = 10);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 11);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DENSE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 14);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 16);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 13, shape_aspect_ratio=1.25);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 10.5, shape_aspect_ratio=1);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
// Example:
//   default_lid_shape_rounding = 3;
//   ShapeByType(shape_type= SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_CLOUD, shape_thickness = 2, shape_width = 11);
// Example(2D,Med):
//   ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2);
// Example(2D,Big):
//   ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//       supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R1, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R2, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R3, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R4, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R5, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R6, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R7, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R8, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R9, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R10, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R11, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R12, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R13, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R14, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_PENTAGON_R15, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_ESCHER_LIZARD, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_HALF_REGULAR_HEXAGON, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(shape_type = SHAPE_TYPE_DROP, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(shape_type = SHAPE_TYPE_VORONOI, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(shape_type = SHAPE_TYPE_PENROSE_TILING_5, shape_thickness = 1, shape_width = 10);
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(shape_type = SHAPE_TYPE_PENROSE_TILING_7, shape_thickness = 1, shape_width = 10);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DELTOID_TRIHEXAGONAL, shape_thickness = 1, shape_width = 10);
// Example:
//   ShapeByType(shape_type = SHAPE_TYPE_DELTOID_TRIHEXAGONAL_KITE, shape_thickness = 1, shape_width = 10);
module ShapeByType(
  shape_type,
  shape_width,
  shape_thickness,
  shape_aspect_ratio = 1.0,
  rounding = undef,
  supershape_m1 = undef,
  supershape_m2 = undef,
  supershape_n1 = undef,
  supershape_n2 = undef,
  supershape_n3 = undef,
  supershape_a = undef,
  supershape_b = undef
) {
  calc_shape_type = DefaultValue(shape_type, default_lid_shape_type);
  calc_shape_width = DefaultValue(shape_width, default_lid_shape_width);
  calc_shape_thickness = DefaultValue(shape_thickness, default_lid_shape_thickness);
  calc_aspect_ratio = DefaultValue(shape_aspect_ratio, default_lid_aspect_ratio);
  calc_rounding = DefaultValue(rounding, default_lid_shape_rounding);
  calc_supershape_m1 = DefaultValue(supershape_m1, default_lid_supershape_m1);
  calc_supershape_m2 = DefaultValue(supershape_m2, default_lid_supershape_m2);
  calc_supershape_n1 = DefaultValue(supershape_n1, default_lid_supershape_n1);
  calc_supershape_n2 = DefaultValue(supershape_n2, default_lid_supershape_n2);
  calc_supershape_n3 = DefaultValue(supershape_n3, default_lid_supershape_n3);
  calc_supershape_a = DefaultValue(supershape_a, default_lid_supershape_a);
  calc_supershape_b = DefaultValue(supershape_b, default_lid_supershape_b);
  if (calc_shape_type == SHAPE_TYPE_NONE) {
    // Don't do anything.
  } else {
    // Thin border around the pattern to stick it on.

    if (calc_shape_type == SHAPE_TYPE_DENSE_HEX) {
      difference() {
        regular_ngon(or=calc_shape_width / 2 + calc_shape_thickness / 2, n=6, rounding=calc_rounding);
        regular_ngon(or=calc_shape_width / 2 - calc_shape_thickness / 2, n=6, rounding=calc_rounding);
      }
    } else if (calc_shape_type == SHAPE_TYPE_DENSE_TRIANGLE) {
      side_length = calc_shape_width / 2 * sqrt(3);
      difference() {
        regular_ngon(or=calc_shape_width / 2 + calc_shape_thickness / 2, n=3, rounding=calc_rounding);
        regular_ngon(or=calc_shape_width / 2 - calc_shape_thickness / 2, n=3, rounding=calc_rounding);
      }
    } else if (calc_shape_type == SHAPE_TYPE_CIRCLE) {
      difference() {
        circle(r=calc_shape_width / 2);
        circle(r=(calc_shape_width - calc_shape_thickness) / 2);
      }
    } else if (
      calc_shape_type == SHAPE_TYPE_TRIANGLE || calc_shape_type == SHAPE_TYPE_HEX || calc_shape_type == SHAPE_TYPE_OCTOGON || calc_shape_type == SHAPE_TYPE_SQUARE
    ) {
      shape_edges =
        calc_shape_type == SHAPE_TYPE_TRIANGLE ? 3
        : (calc_shape_type == SHAPE_TYPE_HEX ? 6 : (calc_shape_type == SHAPE_TYPE_SQUARE ? 4 : 8));
      difference() {
        regular_ngon(r=calc_shape_width / 2, n=shape_edges, rounding=calc_rounding);
        regular_ngon(
          r=(calc_shape_width - calc_shape_thickness) / 2, n=shape_edges,
          rounding=calc_rounding,
        );
      }
    } else if (calc_shape_type == SHAPE_TYPE_SUPERSHAPE) {
      difference() {
        DifferenceWithOffset(offset=-calc_shape_thickness) supershape(
            d=calc_shape_width, m1=calc_supershape_m1, m2=calc_supershape_m2, n1=calc_supershape_n1,
            n2=calc_supershape_n2, n3=calc_supershape_n3, a=calc_supershape_a, b=calc_supershape_b,
          );
      }
    } else if (calc_shape_type == SHAPE_TYPE_CLOUD) {
      translate([-calc_shape_width / 2, -calc_shape_width / 2]) difference() {
          resize([calc_shape_width * calc_aspect_ratio, calc_shape_width]) {
            CloudShape2d(width=calc_shape_width);
          }
          offset(delta=-calc_shape_thickness) resize([calc_shape_width * calc_aspect_ratio, calc_shape_width]) {
              CloudShape2d(width=calc_shape_width);
            }
        }
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R1) {
      PentagonTesselation(pentagon_type="R1", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R2) {
      PentagonTesselation(pentagon_type="R2", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R3) {
      PentagonTesselation(pentagon_type="R3", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R4) {
      PentagonTesselation(pentagon_type="R4", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R5) {
      PentagonTesselation(pentagon_type="R5", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R6) {
      PentagonTesselation(pentagon_type="R6", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R7) {
      PentagonTesselation(pentagon_type="R7", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R8) {
      PentagonTesselation(pentagon_type="R8", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R9) {
      PentagonTesselation(pentagon_type="R9", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R10) {
      PentagonTesselation(pentagon_type="R10", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R11) {
      PentagonTesselation(pentagon_type="R11", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R12) {
      PentagonTesselation(pentagon_type="R12", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R13) {
      PentagonTesselation(pentagon_type="R13", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R14) {
      PentagonTesselation(pentagon_type="R14", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R15) {
      PentagonTesselation(pentagon_type="R15", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0);
    } else if (calc_shape_type == SHAPE_TYPE_ESCHER_LIZARD) {
      EscherLizardRepeatAtLocation(size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_VORONOI) {
      Voronoi(width=$polygon_width, length=$polygon_length, cellsize=calc_shape_width, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_PENROSE_TILING_5) {
      max_width = max($polygon_width, $polygon_length);
      PenroseTiling(max_width * 1.5, divisions=ceil((max_width * 2 / calc_shape_width) / 3), base=5, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_PENROSE_TILING_7) {
      max_width = max($polygon_width, $polygon_length);
      PenroseTiling(max_width * 1.5, divisions=ceil((max_width * 2 / calc_shape_width) / 3), base=7, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_DROP) {
      TesselationDrop(size=[calc_shape_width, calc_shape_width * calc_aspect_ratio], thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_DELTOID_TRIHEXAGONAL) {
      DeltoidTrihexagonalTiling(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_DELTOID_TRIHEXAGONAL_KITE) {
      DeltoidTrihexagonalTiling(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.1, kite=true);
    } else if (calc_shape_type == SHAPE_TYPE_HALF_REGULAR_HEXAGON) {
      TriangleTesselationRepeatAtLocation(size=calc_shape_width, x=$polygon_x, y=$polygon_y)
        HalfRegularHexagon(size=calc_shape_width, thickness=calc_shape_thickness, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL) {
      HexagonTesselationRepeatAtLocation(size=calc_shape_width / 2, x=$polygon_x, y=$polygon_y)
        RhombiTriHexagonal(calc_shape_width);
    } else if (calc_shape_type == SHAPE_TYPE_LEAF) {
      section = calc_shape_width / 4;
      section_height = section * calc_sqrt_three / 2;
      pos = ($polygon_x % 4);
      offset = (
        pos == 0 ?
          0
        : pos == 1 ?
          section * 2
        : pos == 2 ?
          section * 4
        : section * 6
      );
      translate(
        [
          $polygon_x * section_height * 6 + ($polygon_y % 2) * section_height * 2,
          $polygon_y * section * 4 - offset,
        ]
      ) {
        rotate(($polygon_y % 2) * 180)
          TesselationLeafOutlineThree(
            size=calc_shape_width + 0.1,
            thickness=calc_shape_thickness / 2,
            vein_thickness=calc_shape_thickness / 4,
            with_veins=false
          );
      }
    } else if (calc_shape_type == SHAPE_TYPE_LEAF_VEINS) {
      section = calc_shape_width / 4;
      section_height = section * calc_sqrt_three / 2;
      pos = ($polygon_x % 4);
      offset = (
        pos == 0 ?
          0
        : pos == 1 ?
          section * 2
        : pos == 2 ?
          section * 4
        : section * 6
      );
      translate(
        [
          $polygon_x * section_height * 6 + ($polygon_y % 2) * section_height * 2,
          $polygon_y * section * 4 - offset,
        ]
      ) {
        rotate(($polygon_y % 2) * 180)
          TesselationLeafOutlineThree(
            size=calc_shape_width + 0.1,
            thickness=calc_shape_thickness / 2,
            vein_thickness=calc_shape_thickness / 4,
            with_veins=true
          );
      }
    } else {
      assert(false, "Invalid shape type");
    }
  }
}

// Module: PortugalCastle()
// Description:
//   The castle used on the flag of portugal
// Arguments:
//   stroke_width = width of the stroke to use for the castle outline
//   width = the final width of the castle.
// Example:
//   PortugalCastle(0.2, 50);
module PortugalCastle(stroke_width, width) {
  max_height = 155.62545;
  min_height = 135.882;
  max_width = 203.44508;
  min_width = 185.20092;
  mult = width / (max_width - min_width);
  resize([width, (max_height - min_height) * mult])
    translate([-min_width - (max_width - min_width) / 2, -min_height - (max_height - min_height) / 2]) {

      color("black") stroke(
          bezpath_curve(
            [
              [190.19, 154.43],
              [190.32493, 148.90900000000002],
              [194.2424, 147.602],
              [194.2706, 147.5826],
              [194.2988, 147.56410000000002],
              [198.502, 148.99020000000002],
              [198.4879, 154.4812],
              [198.4879, 154.4812],
              [190.1901, 154.43],
              [190.1901, 154.43],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [186.81, 147.69],
              [186.81, 147.69],
              [186.12828, 154.0347],
              [186.12828, 154.0347],
              [186.12828, 154.0347],
              [190.26888, 154.04369999999997],
              [190.26888, 154.04369999999997],
              [190.30858, 148.79439999999997],
              [194.24277999999998, 147.92119999999997],
              [194.33798, 147.94059999999996],
              [194.42708, 147.93559999999997],
              [198.32688, 149.10119999999995],
              [198.43088, 154.04369999999997],
              [198.43088, 154.04369999999997],
              [202.58198, 154.04369999999997],
              [202.58198, 154.04369999999997],
              [202.58198, 154.04369999999997],
              [201.83236, 147.65049999999997],
              [201.83236, 147.65049999999997],
              [201.83236, 147.65049999999997],
              [186.81036, 147.68839999999997],
              [186.81036, 147.68839999999997],
              [186.81036, 147.68839999999997],
              [186.81036, 147.69039999999998],
              [186.81036, 147.69039999999998],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [185.85, 154.06],
              [185.85, 154.06],
              [202.796, 154.06],
              [202.796, 154.06],
              [203.15317, 154.06],
              [203.44508, 154.41277],
              [203.44508, 154.84404],
              [203.44508, 155.27443],
              [203.15317, 155.62545],
              [202.796, 155.62545],
              [202.796, 155.62545],
              [185.85, 155.62545],
              [185.85, 155.62545],
              [185.49283, 155.62545],
              [185.20092, 155.27443],
              [185.20092, 154.84404],
              [185.20092, 154.41277],
              [185.49283, 154.06],
              [185.85, 154.06],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [192.01, 154.03],
              [192.02849999999998, 150.7174],
              [194.2721, 149.7799],
              [194.28359999999998, 149.7817],
              [194.28447999999997, 149.7817],
              [196.62589999999997, 150.74831],
              [196.64449999999997, 154.03],
              [196.64449999999997, 154.03],
              [192.01009999999997, 154.03],
              [192.01009999999997, 154.03],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [186.21, 145.05],
              [186.21, 145.05],
              [202.455, 145.05],
              [202.455, 145.05],
              [202.79718000000003, 145.05],
              [203.07763, 145.36839],
              [203.07763, 145.75468],
              [203.07763, 146.14185],
              [202.79718, 146.45935],
              [202.455, 146.45935],
              [202.455, 146.45935],
              [186.21, 146.45935],
              [186.21, 146.45935],
              [185.86782, 146.45935],
              [185.58737000000002, 146.14362],
              [185.58737000000002, 145.75468],
              [185.58737000000002, 145.36839],
              [185.86782000000002, 145.05],
              [186.21, 145.05],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [186.55, 146.47],
              [186.55, 146.47],
              [202.08800000000002, 146.47],
              [202.08800000000002, 146.47],
              [202.41519000000002, 146.47],
              [202.68329000000003, 146.78662],
              [202.68329000000003, 147.17379],
              [202.68329000000003, 147.56184],
              [202.41519000000002, 147.87846],
              [202.08800000000002, 147.87846],
              [202.08800000000002, 147.87846],
              [186.55, 147.87846],
              [186.55, 147.87846],
              [186.22281, 147.87846],
              [185.95471, 147.56184],
              [185.95471, 147.17379],
              [185.95471, 146.78662],
              [186.22281, 146.47],
              [186.55, 146.47],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [191.57, 135.88],
              [191.57, 135.88],
              [192.7967, 135.882],
              [192.7967, 135.882],
              [192.7967, 135.882],
              [192.7967, 136.75336000000001],
              [192.7967, 136.75336000000001],
              [192.7967, 136.75336000000001],
              [193.69182999999998, 136.75336000000001],
              [193.69182999999998, 136.75336000000001],
              [193.69182999999998, 136.75336000000001],
              [193.69182999999998, 135.86260000000001],
              [193.69182999999998, 135.86260000000001],
              [193.69182999999998, 135.86260000000001],
              [194.94852999999998, 135.8666],
              [194.94852999999998, 135.8666],
              [194.94852999999998, 135.8666],
              [194.94852999999998, 136.75383],
              [194.94852999999998, 136.75383],
              [194.94852999999998, 136.75383],
              [195.84631, 136.75383],
              [195.84631, 136.75383],
              [195.84631, 136.75383],
              [195.84631, 135.86307],
              [195.84631, 135.86307],
              [195.84631, 135.86307],
              [197.10390999999998, 135.86307],
              [197.10390999999998, 135.86307],
              [197.10390999999998, 135.86307],
              [197.10190999999998, 137.87476999999998],
              [197.10190999999998, 137.87476999999998],
              [197.10190999999998, 138.19051],
              [196.84792999999996, 138.39512],
              [196.55336999999997, 138.39512],
              [196.55336999999997, 138.39512],
              [192.14206999999996, 138.39512],
              [192.14206999999996, 138.39512],
              [191.84573999999995, 138.39512],
              [191.57234999999997, 138.15787999999998],
              [191.57146999999995, 137.8686],
              [191.57146999999995, 137.8686],
              [191.56846999999996, 135.8807],
              [191.56846999999996, 135.8807],
              [191.56846999999996, 135.8807],
              [191.56934999999996, 135.8807],
              [191.56934999999996, 135.8807],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [196.19, 138.57],
              [196.19, 138.57],
              [196.46690999999998, 145.0214],
              [196.46690999999998, 145.0214],
              [196.46690999999998, 145.0214],
              [192.16411, 145.0055],
              [192.16411, 145.0055],
              [192.16411, 145.0055],
              [192.44897, 138.5532],
              [192.44897, 138.5532],
              [192.44897, 138.5532],
              [196.18997000000002, 138.57],
              [196.18997000000002, 138.57],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [190.94, 141.56],
              [190.94, 141.56],
              [191.07141, 145.0375],
              [191.07141, 145.0375],
              [191.07141, 145.0375],
              [186.94581, 145.0395],
              [186.94581, 145.0395],
              [186.94581, 145.0395],
              [187.06222, 141.5602],
              [187.06222, 141.5602],
              [187.06222, 141.5602],
              [190.94082, 141.5602],
              [190.94082, 141.5602],
              [190.94082, 141.5602],
              [190.93993, 141.5602],
              [190.93993, 141.5602],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [186.3, 139.04],
              [186.3, 139.04],
              [187.4994, 139.04299999999998],
              [187.4994, 139.04299999999998],
              [187.4994, 139.04299999999998],
              [187.4994, 139.91523999999998],
              [187.4994, 139.91523999999998],
              [187.4994, 139.91523999999998],
              [188.3769, 139.91523999999998],
              [188.3769, 139.91523999999998],
              [188.3769, 139.91523999999998],
              [188.3769, 139.02271],
              [188.3769, 139.02271],
              [188.3769, 139.02271],
              [189.6063, 139.02670999999998],
              [189.6063, 139.02670999999998],
              [189.6063, 139.02670999999998],
              [189.6063, 139.91571],
              [189.6063, 139.91571],
              [189.6063, 139.91571],
              [190.48556, 139.91571],
              [190.48556, 139.91571],
              [190.48556, 139.91571],
              [190.48556, 139.02318],
              [190.48556, 139.02318],
              [190.48556, 139.02318],
              [191.71576, 139.02518],
              [191.71576, 139.02518],
              [191.71576, 139.02518],
              [191.71375999999998, 141.03688],
              [191.71375999999998, 141.03688],
              [191.71375999999998, 141.35085999999998],
              [191.46505999999997, 141.55546999999999],
              [191.17755999999997, 141.55546999999999],
              [191.17755999999997, 141.55546999999999],
              [186.86065999999997, 141.55546999999999],
              [186.86065999999997, 141.55546999999999],
              [186.57139999999995, 141.55546999999999],
              [186.30241999999996, 141.31999],
              [186.30152999999996, 141.02982999999998],
              [186.30152999999996, 141.02982999999998],
              [186.29852999999997, 139.04102999999998],
              [186.29852999999997, 139.04102999999998],
              [186.29852999999997, 139.04102999999998],
              [186.29940999999997, 139.04102999999998],
              [186.29940999999997, 139.04102999999998],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [193.9, 140.61],
              [193.8735, 139.98294],
              [194.77661, 139.97589000000002],
              [194.76603, 140.61],
              [194.76603, 140.61],
              [194.76603, 142.1464],
              [194.76603, 142.1464],
              [194.76603, 142.1464],
              [193.90003, 142.1464],
              [193.90003, 142.1464],
              [193.90003, 142.1464],
              [193.90003, 140.6104],
              [193.90003, 140.6104],
            ],
          ),
          width=0.2,
        );
      color("black") stroke(
          bezpath_curve(
            [
              [188.57, 142.84],
              [188.567, 142.2341],
              [189.40693, 142.22176000000002],
              [189.39634999999998, 142.84],
              [189.39634999999998, 142.84],
              [189.39634999999998, 144.0271],
              [189.39634999999998, 144.0271],
              [189.39634999999998, 144.0271],
              [188.57035, 144.0271],
              [188.57035, 144.0271],
              [188.57035, 144.0271],
              [188.57035, 142.84009999999998],
              [188.57035, 142.84009999999998],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [201.549, 141.56],
              [201.549, 141.56],
              [201.68041, 145.0375],
              [201.68041, 145.0375],
              [201.68041, 145.0375],
              [197.55481, 145.0395],
              [197.55481, 145.0395],
              [197.55481, 145.0395],
              [197.67122, 141.5602],
              [197.67122, 141.5602],
              [197.67122, 141.5602],
              [201.54982, 141.5602],
              [201.54982, 141.5602],
              [201.54982, 141.5602],
              [201.54893, 141.5602],
              [201.54893, 141.5602],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [196.90900000000002, 139.04],
              [196.90900000000002, 139.04],
              [198.10840000000002, 139.04299999999998],
              [198.10840000000002, 139.04299999999998],
              [198.10840000000002, 139.04299999999998],
              [198.10840000000002, 139.91523999999998],
              [198.10840000000002, 139.91523999999998],
              [198.10840000000002, 139.91523999999998],
              [198.98590000000002, 139.91523999999998],
              [198.98590000000002, 139.91523999999998],
              [198.98590000000002, 139.91523999999998],
              [198.98590000000002, 139.02271],
              [198.98590000000002, 139.02271],
              [198.98590000000002, 139.02271],
              [200.2153, 139.02670999999998],
              [200.2153, 139.02670999999998],
              [200.2153, 139.02670999999998],
              [200.2153, 139.91571],
              [200.2153, 139.91571],
              [200.2153, 139.91571],
              [201.09456, 139.91571],
              [201.09456, 139.91571],
              [201.09456, 139.91571],
              [201.09456, 139.02318],
              [201.09456, 139.02318],
              [201.09456, 139.02318],
              [202.32476, 139.02518],
              [202.32476, 139.02518],
              [202.32476, 139.02518],
              [202.32276, 141.03688],
              [202.32276, 141.03688],
              [202.32276, 141.35085999999998],
              [202.07405999999997, 141.55546999999999],
              [201.78655999999998, 141.55546999999999],
              [201.78655999999998, 141.55546999999999],
              [197.46965999999998, 141.55546999999999],
              [197.46965999999998, 141.55546999999999],
              [197.18039999999996, 141.55546999999999],
              [196.91141999999996, 141.31999],
              [196.91052999999997, 141.02982999999998],
              [196.91052999999997, 141.02982999999998],
              [196.90752999999998, 139.04102999999998],
              [196.90752999999998, 139.04102999999998],
              [196.90752999999998, 139.04102999999998],
              [196.90840999999998, 139.04102999999998],
              [196.90840999999998, 139.04102999999998],
            ],
          ),
          width=0.2,
        );

      color("black") stroke(
          bezpath_curve(
            [
              [199.21099999999998, 142.84],
              [199.208, 142.2341],
              [200.04792999999998, 142.22176000000002],
              [200.03734999999998, 142.84],
              [200.03734999999998, 142.84],
              [200.03734999999998, 144.0271],
              [200.03734999999998, 144.0271],
              [200.03734999999998, 144.0271],
              [199.21134999999998, 144.0271],
              [199.21134999999998, 144.0271],
              [199.21134999999998, 144.0271],
              [199.21134999999998, 142.84009999999998],
              [199.21134999999998, 142.84009999999998],
            ],
          ),
          width=0.2,
        );
    }
}

// Module: TrainOutline()
// Description:
//   Creates a nice train outline to use for stuff.
// Arguments:
//   length = length of the train
// Example:
//   TrainOutline(100);
module TrainOutline(length) {
  assert(length > 0, "Length must be > 0");
  train_length = 688.4302;
  train_width = 268.8392;
  scale = length / train_length;
  bez = [
    [688.43, 119.93],
    [682.04, 111.12],
    [670.5899999999999, 113.53],
    [658.1999999999999, 112.13000000000001],
    [646.89, 110.85000000000001],
    [639.39, 101.20000000000002],
    [628.9499999999999, 103.35000000000001],
    [622.4499999999999, 104.69000000000001],
    [620.3399999999999, 111.97000000000001],
    [614.3199999999999, 113.10000000000001],
    [606.89, 111.84],
    [604.8299999999999, 108.06],
    [596.77, 109.2],
    [587.26, 110.54],
    [585.43, 119.23],
    [572.39, 117.0],
    [558.76, 114.66],
    [553.16, 95.35],
    [553.86, 84.82],
    [555.19, 64.99],
    [574.0500000000001, 48.419999999999995],
    [596.76, 51.669999999999995],
    [606.0, 52.989999999999995],
    [609.09, 60.019999999999996],
    [621.14, 60.449999999999996],
    [626.18, 55.86],
    [629.37, 39.56999999999999],
    [624.0699999999999, 33.14999999999999],
    [466.1099999999999, 33.14999999999999],
    [454.5299999999999, 35.60999999999999],
    [432.9599999999999, 52.64999999999999],
    [432.9599999999999, 52.64999999999999],
    [445.63999999999993, 68.24999999999999],
    [445.63999999999993, 90.67999999999998],
    [406.63999999999993, 90.67999999999998],
    [406.63999999999993, 62.39999999999998],
    [387.13999999999993, 52.64999999999998],
    [387.13999999999993, 34.119999999999976],
    [390.06999999999994, 34.119999999999976],
    [382.2699999999999, 26.319999999999975],
    [374.4699999999999, 34.119999999999976],
    [377.3999999999999, 34.119999999999976],
    [377.3999999999999, 52.64999999999998],
    [358.8699999999999, 61.42999999999998],
    [358.8699999999999, 90.67999999999998],
    [310.1099999999999, 90.67999999999998],
    [310.1099999999999, 80.92999999999998],
    [314.0099999999999, 80.92999999999998],
    [291.57999999999987, 58.49999999999998],
    [271.09999999999985, 80.92999999999998],
    [274.99999999999983, 80.92999999999998],
    [274.99999999999983, 90.67999999999998],
    [234.04999999999984, 90.67999999999998],
    [234.04999999999984, 84.82999999999998],
    [237.94999999999985, 84.82999999999998],
    [229.16999999999985, 76.04999999999998],
    [221.36999999999983, 84.82999999999998],
    [225.26999999999984, 84.82999999999998],
    [225.26999999999984, 90.67999999999998],
    [173.58999999999983, 90.67999999999998],
    [167.73999999999984, 84.82999999999998],
    [167.73999999999984, 32.16999999999999],
    [167.73999999999984, 32.16999999999999],
    [177.54999999999984, 21.919999999999987],
    [175.53999999999985, 13.639999999999986],
    [172.97999999999985, 3.109999999999987],
    [152.05999999999986, 3.029999999999987],
    [150.18999999999986, 13.639999999999986],
    [149.11999999999986, 19.699999999999985],
    [157.01999999999987, 32.16999999999999],
    [157.01999999999987, 32.16999999999999],
    [156.03999999999988, 84.82999999999998],
    [150.18999999999988, 90.67999999999998],
    [132.62999999999988, 55.57999999999998],
    [133.60999999999987, 15.59999999999998],
    [119.94, 0.0],
    [106.28999999999999, 15.6],
    [106.28999999999999, 59.480000000000004],
    [116.03999999999999, 59.480000000000004],
    [113.02999999999999, 62.32000000000001],
    [106.77999999999999, 67.26],
    [110.19, 73.13000000000001],
    [112.62, 75.9],
    [117.21, 76.51],
    [122.87, 76.06000000000002],
    [139.9, 93.86000000000001],
    [132.62, 153.09000000000003],
    [132.62, 153.09000000000003],
    [114.30000000000001, 166.35000000000002],
    [76.06, 190.14000000000004],
    [76.06, 190.14000000000004],
    [59.480000000000004, 176.49000000000004],
    [0.0, 226.22],
    [0.0, 240.85],
    [73.13, 240.85],
    [83.52, 225.57],
    [82.69, 228.51],
    [82.24, 231.6],
    [82.24, 234.79999999999998],
    [82.24, 253.6],
    [97.47999999999999, 268.84],
    [116.28, 268.84],
    [135.08, 268.84],
    [150.32, 253.59999999999997],
    [150.32, 234.79999999999998],
    [150.32, 230.76],
    [149.60999999999999, 226.89],
    [148.32, 223.29999999999998],
    [160.29999999999998, 223.29999999999998],
    [159.01, 226.89],
    [158.29999999999998, 230.76999999999998],
    [158.29999999999998, 234.79999999999998],
    [158.29999999999998, 253.6],
    [173.54, 268.84],
    [192.33999999999997, 268.84],
    [211.13999999999996, 268.84],
    [226.37999999999997, 253.59999999999997],
    [226.37999999999997, 234.79999999999998],
    [226.37999999999997, 230.76],
    [225.66999999999996, 226.89],
    [224.37999999999997, 223.29999999999998],
    [269.34999999999997, 223.29999999999998],
    [272.87999999999994, 248.45999999999998],
    [294.47999999999996, 267.83],
    [320.61999999999995, 267.83],
    [346.75999999999993, 267.83],
    [368.35999999999996, 248.45999999999998],
    [371.88999999999993, 223.29999999999998],
    [398.06999999999994, 223.29999999999998],
    [401.5999999999999, 248.45999999999998],
    [423.19999999999993, 267.83],
    [449.3399999999999, 267.83],
    [475.4799999999999, 267.83],
    [497.0799999999999, 248.45999999999998],
    [500.6099999999999, 223.29999999999998],
    [520.7199999999999, 223.29999999999998],
    [543.1499999999999, 212.57],
    [553.8799999999999, 223.29999999999998],
    [554.2599999999999, 223.29999999999998],
    [552.9699999999999, 226.89],
    [552.2599999999999, 230.76999999999998],
    [552.2599999999999, 234.79999999999998],
    [552.2599999999999, 253.6],
    [567.4999999999999, 268.84],
    [586.2999999999998, 268.84],
    [605.0999999999998, 268.84],
    [620.3399999999998, 253.59999999999997],
    [620.3399999999998, 234.79999999999998],
    [620.3399999999998, 230.76],
    [619.6299999999998, 226.89],
    [618.3399999999998, 223.29999999999998],
    [628.9599999999998, 223.29999999999998],
    [655.1899999999998, 194.26999999999998],
    [673.7399999999998, 160.48999999999998],
    [688.4399999999998, 119.92999999999998],
  ];

  translate([-length / 2, -length * train_width / train_length / 2])
    resize([length, length * train_width / train_length])
      difference() {
        polygon(bez);
        rect1 = [
          [469.03, 66.3],
          [469.03, 66.3 + 38.03],
          [469.03 + 25.35, 66.3 + 38.03],
          [469.03 + 25.35, 66.3],
        ];
        polygon(rect1);
        rect2 = [
          [512.91, 66.3],
          [512.91, 66.3 + 38.03],
          [512.91 + 25.35, 66.3 + 38.03],
          [512.91 + 25.35, 66.3],
        ];
        polygon(rect2);
        rect3 = [
          [551.91, 152.11],
          [551.91, 152.11 + 31.2],
          [551.91 + 14.63, 152.11 + 31.2],
          [551.91 + 14.63, 152.11],
        ];
        polygon(rect3);
      }
}

// Module: WagonOutline()
// Description:
//    Create a wagon outline from the exciting svg.
// Arguments:
//    length = the length of the wagon
// Example:
//    WagonOutline(50);
module WagonOutline(length) {
  assert(length > 0, "Length must be > 0");

  wagon_length = 1309.8456;
  wagon_width = 909.6154;
  scale = length / wagon_length;
  bez = [
    [1294.89, 615.57],
    [1290.0, 264.6600000000001],
    [1293.82, 262.94000000000005],
    [1315.6299999999999, 253.11000000000004],
    [1315.04, 204.87000000000006],
    [1292.98, 193.90000000000003],
    [1288.6, 191.72000000000003],
    [1078.37, 191.48000000000002],
    [868.1399999999999, 191.24],
    [868.1399999999999, 74.18],
    [872.5599999999998, 73.89],
    [885.6299999999999, 73.04],
    [889.6999999999998, 10.149999999999999],
    [877.2399999999998, 1.4200000000000017],
    [875.4499999999998, 0.1700000000000017],
    [848.9099999999997, 0.010000000000001785],
    [646.8399999999998, 0.010000000000001785],
    [418.4599999999998, 0.010000000000001785],
    [416.4599999999998, 2.150000000000002],
    [411.67999999999984, 7.240000000000002],
    [411.1299999999998, 10.840000000000002],
    [411.1299999999998, 37.05],
    [411.1299999999998, 69.41],
    [412.73999999999984, 74.08],
    [423.92999999999984, 74.08],
    [429.3899999999998, 74.08],
    [429.3899999999998, 191.25],
    [224.7099999999998, 191.49],
    [20.029999999999802, 191.73000000000002],
    [14.499999999999801, 194.56000000000003],
    [2.75, 200.56],
    [-0.01, 207.19],
    [0.0, 229.34],
    [0.01, 249.1],
    [1.74, 253.86],
    [11.48, 261.07],
    [15.0, 263.67],
    [15.0, 613.4200000000001],
    [11.21, 616.6700000000001],
    [3.0500000000000007, 623.6500000000001],
    [2.380000000000001, 626.3000000000001],
    [2.030000000000001, 653.2600000000001],
    [1.5100000000000011, 693.7700000000001],
    [6.520000000000001, 700.3900000000001],
    [38.2, 701.0900000000001],
    [54.370000000000005, 701.4500000000002],
    [54.370000000000005, 750.8100000000002],
    [54.370000000000005, 750.8100000000002],
    [54.39000000000001, 800.1700000000002],
    [54.39000000000001, 800.1700000000002],
    [56.59000000000001, 804.8900000000002],
    [62.26000000000001, 817.0700000000002],
    [70.20000000000002, 820.3200000000002],
    [94.26000000000002, 820.3200000000002],
    [111.43000000000002, 820.3200000000002],
    [112.95000000000002, 825.7100000000002],
    [143.62, 934.5700000000002],
    [293.97, 931.5700000000002],
    [324.93, 821.4900000000001],
    [325.49, 819.4900000000001],
    [359.07, 819.8300000000002],
    [359.07, 821.8400000000001],
    [359.07, 837.2100000000002],
    [380.4, 870.8700000000001],
    [399.38, 885.4600000000002],
    [461.56, 933.2400000000001],
    [558.34, 898.6100000000001],
    [572.42, 823.5400000000002],
    [573.03, 820.3100000000002],
    [648.03, 820.5500000000002],
    [723.03, 820.7900000000002],
    [725.3, 828.7600000000002],
    [754.81, 932.5800000000002],
    [905.04, 932.5700000000002],
    [934.99, 828.7500000000002],
    [937.28, 820.8000000000002],
    [953.6, 820.5400000000002],
    [969.9200000000001, 820.2800000000002],
    [972.48, 829.4400000000002],
    [983.98, 870.6300000000001],
    [1019.23, 901.8200000000002],
    [1061.72, 908.4100000000002],
    [1061.74, 908.3900000000002],
    [1116.03, 916.8000000000002],
    [1169.99, 880.8600000000002],
    [1183.69, 827.1500000000002],
    [1185.41, 820.4000000000002],
    [1213.1100000000001, 820.1200000000002],
    [1244.3100000000002, 819.8000000000002],
    [1245.7500000000002, 819.5200000000002],
    [1252.96, 812.3000000000002],
    [1260.69, 804.5700000000002],
    [1260.46, 806.4300000000002],
    [1260.76, 750.7800000000002],
    [1261.03, 701.4200000000002],
    [1272.95, 701.0500000000002],
    [1286.93, 700.6200000000002],
    [1292.51, 698.7400000000002],
    [1298.0900000000001, 692.5600000000002],
    [1305.2, 684.6900000000002],
    [1305.4900000000002, 683.2100000000002],
    [1305.4900000000002, 655.2200000000001],
    [1305.4900000000002, 630.3100000000002],
    [1302.6500000000003, 624.7500000000002],
    [1300.6500000000003, 620.8400000000003],
    [1298.3600000000004, 618.1100000000002],
    [1294.9200000000003, 615.5400000000002],
  ];
  translate([-length / 2, -length * wagon_width / wagon_length / 2])
    resize([length, length * wagon_width / wagon_length])
      difference() {
        polygon(bez);
        line1 = [
          [1036.93, 274.71],
          [1223.5, 274.71],
          [1223.5, 360.02],
          [1223.5, 445.33],
          [1130.22, 445.33],
          [1036.93, 445.33],
        ];
        polygon(line1);
        line2 = [
          [796.91, 275.86],
          [800.18, 274.98],
          [842.16, 274.73],
          [892.3, 274.74],
          [983.4699999999999, 274.76],
          [983.4699999999999, 446.27],
          [890.81, 446.27],
          [839.8499999999999, 446.27],
          [797.8699999999999, 445.99],
          [797.53, 445.65],
          [797.53, 445.65],
          [797.1899999999999, 445.31],
          [796.91, 406.96999999999997],
          [796.91, 360.45],
          [796.91, 275.87],
        ];
        polygon(line2);
        line3 = [
          [567.22, 275.65],
          [753.79, 275.65],
          [753.79, 360.96],
          [753.79, 446.27],
          [660.5, 446.27],
          [567.22, 446.27],
        ];
        polygon(line3);
        line4 = [
          [333.78, 276.59],
          [427.06, 276.59],
          [520.35, 276.59],
          [520.35, 361.9],
          [520.35, 447.21],
          [333.78, 447.21],
        ];
        polygon(line4);
        line5 = [
          [93.78, 276.59],
          [280.34, 276.59],
          [280.34, 361.9],
          [280.34, 447.21],
          [187.06, 447.21],
          [93.78, 447.21],
          [93.78, 361.9],
          [93.78, 276.59],
        ];
        polygon(line5);
      }
}
