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

box_length = 170;
box_width = 120;
box_height = 35;

token_diametter = 38;
token_thickness = 3;

card_width = 65;
card_length = 91;

card_box_width = box_width;
card_box_length = card_width + default_wall_thickness * 2;
main_deck_box_height = 20;
other_deck_box_height = box_height - main_deck_box_height;

tokens_box_height = box_height;
tokens_box_width = box_width;
tokens_box_length = box_length - card_box_length;

module TokenBox() // `make` me
{
  MakeBoxWithSlidingLid(
    height=tokens_box_height,
    width=tokens_box_width,
    length=tokens_box_length
  ) {
    translate([token_diametter / 2, token_diametter / 2, 0]) {
      for (i = [0:1]) {
        for (j = [0:2]) {
          if (j != 1 || i != 0) {
            translate([(token_diametter + 1) * j, (token_diametter + 20) * i + (j == 1 ? (i == 0 ? 9 : -25) : 0), 0])
              CylinderWithIndents(
                d=token_diametter + 2, height=tokens_box_height,
                finger_hole_radius=15,
                finger_holes=[i == 0 ? 90 : 270]
              );
          }
        }
      }
    }
  }
}

module TokenBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=tokens_box_width,
    length=tokens_box_length,
    text_str="Tokens"
  );
}

module TokenInner(num_stars) {
  module InnerBits(num_stars) {
    if (num_stars == 1 || num_stars == 5)
      linear_extrude(height=0.2)
        star(n=5, r=4, ir=2);
    num_circle_stars = (num_stars == 5 ? 4 : num_stars);
    if (num_stars != 1) {
      for (j = [0:num_stars - 1]) {
        rotate(360 / num_circle_stars * j)
          translate([8, 0, 0])
            linear_extrude(height=0.2)
              rotate(-360 / num_circle_stars * j)
                star(n=5, r=4, ir=2);
      }
    }
    tube(h=0.2, or=token_diametter / 2 - 2, ir=token_diametter / 2 - 3, anchor=BOTTOM);
    for (i = [0:5])
      rotate(i * 60) {
        translate([token_diametter / 2 - 0.5, 0.75, 0])
          cuboid([2, 1, 0.2], anchor=BOTTOM + RIGHT);
        translate([token_diametter / 2 - 0.5, -0.75, 0])
          cuboid([2, 1, 0.2], anchor=BOTTOM + RIGHT);
        translate([token_diametter / 2 - 0.5, -2.25, 0])
          cuboid([2, 1, 0.2], anchor=BOTTOM + RIGHT);
        translate([token_diametter / 2 - 0.5, 2.25, 0])
          cuboid([2, 1, 0.2], anchor=BOTTOM + RIGHT);
      }
  }
  color("yellow")
  difference() {
    cyl(d=token_diametter, h=token_thickness, anchor=BOTTOM);
    InnerBits(num_stars=num_stars);
    translate([0, 0, token_thickness - 0.2]) InnerBits(num_stars=num_stars);
  }
  color("black") {
    InnerBits(num_stars=num_stars);
    translate([0, 0, token_thickness - 0.2]) InnerBits(num_stars=num_stars);
  }
}

module TokenOne() // `make` me
{
  TokenInner(num_stars=1);
}

module TokenTwo() // `make` me
{
  TokenInner(num_stars=2);
}

module TokenThree() // `make` me
{
  TokenInner(num_stars=3);
}

module TokenFour() // `make` me
{
  TokenInner(num_stars=4);
}

module TokenFive() // `make` me
{
  TokenInner(num_stars=5);
}

module TokenSix() // `make` me
{
  TokenInner(num_stars=6);
}

module MainDeckCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    height=main_deck_box_height,
    width=card_box_width,
    length=card_box_length,
    lid_on_length=true
  ) {
    translate([card_length / 2, $inner_length / 2, 0])
      cuboid([card_length, card_width, main_deck_box_height], anchor=BOTTOM);
    translate(
      [0, $inner_length / 2, $inner_height - main_deck_box_height]
    )
      FingerHoleBase(radius=15, height=main_deck_box_height, spin=270);
  }
}

module MainDeckCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    text_str="Main"
  );
}

module OtherCardBox() // `make` me
{
  MakeBoxWithSlidingLid(
    height=other_deck_box_height,
    width=card_box_width,
    length=card_box_length
  ) {
    translate([card_length / 2, $inner_length / 2, 0])
      cuboid([card_length, card_width, main_deck_box_height], anchor=BOTTOM);
    translate(
      [0, $inner_length / 2, $inner_height - other_deck_box_height]
    )
      FingerHoleBase(radius=15, height=other_deck_box_height, spin=270);
  }
}

module OtherDeckCardBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=card_box_width,
    length=card_box_length,
    text_str="Challenge"
  );
}

module BoxLayout() {
  cube([box_width, box_length, 1]);
  cube([1, box_length, box_height]);
  MainDeckCardBox();
  translate([0, 0, main_deck_box_height]) OtherCardBox();
  translate([0, card_box_length, 0])
    TokenBox();
}

if (FROM_MAKE != 1) {
  TokenOne();
}
