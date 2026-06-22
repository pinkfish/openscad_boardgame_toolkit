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

// This also includes the boxes for the abundance expansion.
// However the animal kingdom one will not fit in the box.

include <boardgame_toolkit.scad>
include <lib/animal_kingdom_items.scad>
include <lib/animal_kingdom_items_layout.scad>

box_width = 288;
box_length = 158;
box_height = 47;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;
default_lid_shape_type = SHAPE_TYPE_SHEEP;
default_lid_shape_width = 20;
default_lid_shape_thickness = 1.5;

score_pad_width = 81;
score_pad_length = 99;
score_pad_thickness = 5;
score_pad_number = 1;

canopies_num = 20;

animal_token_thickness = 8;

sprout_cube_width = 8;
sprout_cube_number = 50;

animal_card_num = 36;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;
animal_card_size = MakeCardSize(
  length=123,
  width=72,
  single_card_thickness=single_card_thickness
);

card_box_width = default_wall_thickness * 2 + animal_card_size.width;
card_box_length = box_length - 2;
animal_cards_height = animal_card_size.single_card_thickness * animal_card_num + 2;

score_pad_box_width = score_pad_width + default_wall_thickness * 4;
score_pad_box_length = box_length - card_box_length * 2 - 1;
score_pad_box_height = score_pad_thickness * score_pad_number + default_floor_thickness;

sprout_box_length = box_length;
sprout_box_width = card_box_width;
sprout_box_height = box_height - animal_cards_height - 1;

canopy_box_length = box_length;
canopy_box_width = 38;
canopy_box_height = box_height - 1;

animal_box_width = box_width - card_box_width - 38;
animal_box_length = box_length;
animal_box_height = default_floor_thickness + default_lid_thickness + animal_token_thickness + 0.5;

spacer_box_width = animal_box_width;
spacer_box_length = animal_box_length;
spacer_box_height = box_height - animal_box_height * 2 - 1;

module AnimalCardsBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, animal_cards_height],
    material_colour="maroon"
  ) {
    cube([animal_card_size.width, animal_card_size.length, animal_cards_height]);
    translate([$inner_width / 2, 0, -2]) {
      FingerHoleBase(
        radius=17, height=animal_cards_height - default_lid_thickness,
        spin=0
      );
    }
  }
}

module SproutBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [sprout_box_width, sprout_box_length, sprout_box_height],
    material_colour="green"
  ) {
    right(1) back(1)
        RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, sprout_box_height], radius=5);
  }
}

module CanopyBox() // `make` me
{
  MakeBoxWithFilamentHingeLid(
    [canopy_box_width, canopy_box_length, canopy_box_height],
    material_colour="cornsilk"
  ) {
    right(1) back(1)
        RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, canopy_box_height], radius=5);
  }
}

module AnimalBox() // `make` me
{
  MakeBoxWithSlipoverLid(
    [animal_box_width, animal_box_length, animal_box_height],
    wall_thickness=1.5,
    positive_negative_children=[2],
    foot=4
  ) {
    up($inner_height - animal_token_thickness / 2) right(1) back(1) {
          RoundedBoxAllSides(
            [
              $inner_width - 2,
              $inner_length - 2,
              animal_box_height,
            ],
            radius=3
          );
        }
    up($inner_height - animal_token_thickness - 0.5) {
      Layout_container0(animal_token_thickness + 1);
    }
    up($inner_height - animal_token_thickness - 0.5 - 0.2) {
      Layout_Text_container0(0.201);
    }
  }
}

module AnimalBox2() // `make` me
{
  MakeBoxWithSlipoverLid(
    [animal_box_width, animal_box_length, animal_box_height],
    wall_thickness=1.5,
    positive_negative_children=[2],
    foot=4
  ) {
    up($inner_height - animal_token_thickness / 2) right(1) back(1) {
          RoundedBoxAllSides(
            [
              $inner_width - 2,
              $inner_length - 2,
              animal_box_height,
            ],
            radius=3
          );
        }
    up($inner_height - animal_token_thickness - 0.5) {
      Layout_container1(animal_token_thickness + 1);
    }
    up($inner_height - animal_token_thickness - 0.5 - 0.2) {
      Layout_Text_container1(0.201);
    }
  }
}

module SpacerBox() // `make` me
{
  MakeBoxWithNoLid(
    [spacer_box_width, spacer_box_length, spacer_box_height],
    hollow=true
  );
}

module AnimalCardsBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    size=[card_box_width, card_box_length, animal_cards_height],
    text_str="Animal Cards"
  );
}

module SproutBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[sprout_box_width, sprout_box_length, sprout_box_height],
    text_str="Sprouts"
  );
}

module CanopyBoxLid() // `make` me
{
  FilamentHingeBoxLidWithLabel(
    size=[canopy_box_width, canopy_box_length, canopy_box_height],
    text_str="Canopies"
  );
}

module AnimalBoxLid() // `make` me
{
  SlipoverBoxLidWithLabel(
    size=[animal_box_width, animal_box_length, animal_box_height],
    text_str="Animals",
    foot=4,
    wall_thickness=1.5,
  );
}

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([box_width, 1, box_height]);
  }
  AnimalCardsBox();
  if (layout < 2) {
    up(animal_cards_height) {
      SproutBox();
    }
  }
  right(card_box_width) {
    AnimalBox();
    if (layout < 3) {
      up(animal_box_height) AnimalBox2();
    }
    if (layout < 2) {
      up(animal_box_height * 2) SpacerBox();
    }
    right(animal_box_width) {
      CanopyBox();
    }
  }
}

module BoxLayoutA() // `document` me
{
  BoxLayout(layout=1);
}

module BoxLayoutB() // `document` me
{
  BoxLayout(layout=2);
}

module BoxLayoutC() // `document` me
{
  BoxLayout(layout=3);
}

// Function to calculate vertices 
function generate_hexagon(side_lengths, interior_angles, current_x = 0, current_y = 0, current_angle = 0, num = 0) =
  num >= len(side_lengths) ? [[0, 0]]
  : assert(
    sumVec(interior_angles) < 180 * (len(side_lengths) - 1), str(
      "Sum of angles less than  ",
      180 * (len(side_lengths) - 2)
    )
  )
  assert(len(interior_angles) == len(side_lengths), "Interial angle size and side length side sdhould be the same")
  let (
    new_angle = 180 - interior_angles[num] + current_angle,
    new_x = side_lengths[num] * cos(current_angle) + current_x,
    new_y = side_lengths[num] * sin(current_angle) + current_y
  ) concat(
    [[new_x, new_y]],
    generate_hexagon(
      side_lengths, interior_angles,
      current_x=new_x, current_y=new_y,
      current_angle=new_angle, num=num + 1
    )
  );

module Bits() {
  s1 = 15; // Side 1 (Bottom)
  s2 = 15; // Side 2
  s3 = 22; // Side 3

  a1 = 170;
  a2 = 100;
  a3 = 170;
  a4 = 70;
  a5 = (720 - a1 - a2 * 2 - a3 - a4);
  sides = [s1, s1, s1, s3, s1];
  angles = [180, 125.1, 79.5, 156.428, 100];
  //  echo(sumVec(angles), angles);

  line2 = bezier_curve(
    flatten(
      [
        bez_begin([0, 0], -20, 0.4),
        bez_tang([0.25, 0.0], 0, 0.2, 0.4),
        //bez_tang([0.2, 0.1], 0, 0.2, 0.6),
        bez_tang([0.4, -0.25], 0, 0, 0),
        bez_end([1, 0], 230, 1),
      ]
    ), 20
  );
  line3 = reverse(
    [
      for (
        i = bezier_curve(
          flatten(
            [
              bez_begin([0, 0], -45, 0.8),
              bez_end([1, 0], 235, 0.8),
            ]
          ),
          20
        )
      ) [1 - i[0], i[1]],
    ]
  );
  line1 = bezier_curve(
    reverse(
      [
        for (
          i = [
            [1, 0],
            [1.00443, 0.0381548],
            [1.00618, 0.133237],
            [0.971956, 0.1493],
            [0.930596, 0.168683],
            [0.834179, 0.0743256],
            [0.796787, 0.0977908],
            [0.759396, 0.121256],
            [0.772177, 0.246671],
            [0.730589, 0.261361],
            [0.678965, 0.279637],
            [0.565569, 0.169751],
            [0.520279, 0.200504],
            [0.486207, 0.223664],
            [0.50662, 0.341715],
            [0.468312, 0.3569],
            [0.423748, 0.374566],
            [0.325957, 0.280095],
            [0.284101, 0.303484],
            [0.248083, 0.323591],
            [0.253157, 0.428975],
            [0.202373, 0.446869],
            [0.15861, 0.462284],
            [0.048533, 0.23843],
            [0, 0],
          ]
        ) [i[0], i[1]],
      ]
    ), 30
  );
  /*
  bezier_curve(
    flatten(
      [
        bez_begin([0, 0], -45, 0.4),
        bez_tang([0.2, -0.15], 0, 0.1, 0.2),
        bez_tang([0.4, -0.2], 90, 0.2, 0.4),
        bez_tang([0.5, -0.04], 0, 0.4, 0.4),
        bez_tang([0.6, -0.23], 90, 0.2, 0.4),
        bez_tang([0.7, -0.03], 0, 0.4, 0.4),
        bez_tang([0.8, -0.13], 90, 0.2, 0.4),
        bez_end([1, 0], 260, 0.3),
      ]
    ), 20
  );
  */

  // Draw the polygon
  hexagon = generate_hexagon(sides, angles);
  //x_diff = hexagon[4][0] - hexagon[5][0];
  //y_diff = hexagon[4][1] - hexagon[5][1];
  //line1 = [[0, 0], [1, 0]];
  //line3 = [[0, 0], [1, 0]];
  new_hex = TesselationPolygon(
    hexagon,
    [1, 2, 0, 1, 0, 2],
    [line1, line2, line3],
    [TESSELATION_LINE_FLIPPED_REVERSE, TESSELATION_LINE_FLIPPED, TESSELATION_LINE_FLIPPED, TESSELATION_LINE_NORMAL, TESSELATION_LINE_NORMAL, TESSELATION_LINE_NORMAL]
  );
  color("blue") {
    stroke(new_hex, closed=true);
    //rainbow(hexagon) move($item) sphere(1.5, $fn=12);
  }

  right(18.5)
    back(21.5)
      rotate(180 - angles[1])
        color("magenta") yflip() {
            stroke(new_hex, closed=true);
            // rainbow(hexagon) move($item) sphere(1.5, $fn=12);
          }
}

module BitsAtLocation(x, y) {
  x_vec = [3.6243 - 15, 21.6995];
  y_vec = [58.3, 2.7];
  translate(y_vec * y)
    translate(x_vec * x)
      Bits();
}

if (FROM_MAKE != 1) {
  for (x = [0:1]) {
    for (y = [0:1]) {
      // BitsAtLocation(x, y);
    }
  }

  bez = bezier_curve(
    flatten(
      [
        bez_begin([0, 0], -45, 0.4),
        bez_tang([0.2, -0.15], 0, 0.1, 0.2),
        bez_tang([0.4, -0.2], 90, 0.2, 0.4),
        bez_tang([0.5, -0.04], 0, 0.4, 0.4),
        bez_tang([0.6, -0.23], 90, 0.2, 0.4),
        bez_tang([0.7, -0.03], 0, 0.4, 0.4),
        bez_tang([0.8, -0.13], 90, 0.2, 0.4),
        bez_end([1, 0], 260, 0.3),
      ]
    ), 20
  ) * 100;

  bez2 = reverse(
    [
      for (
        i = [
          [-1, 0],
          [-0.951467, 0.23843],
          [-0.84139, 0.462284],
          [-0.797627, 0.446869],
          [-0.746843, 0.428975],
          [-0.751917, 0.323591],
          [-0.715899, 0.303484],
          [-0.674043, 0.280095],
          [-0.576252, 0.374566],
          [-0.531688, 0.3569],
          [-0.49338, 0.341715],
          [-0.513793, 0.223664],
          [-0.479721, 0.200504],
          [-0.434431, 0.169751],
          [-0.321035, 0.279637],
          [-0.269411, 0.261361],
          [-0.227823, 0.246671],
          [-0.240604, 0.121256],
          [-0.203213, 0.0977908],
          [-0.165821, 0.0743256],
          [-0.0694036, 0.168683],
          [-0.0280438, 0.1493],
          [0.00618108, 0.133237],
          [0.00442596, 0.0381548],
          [0, 0],
        ]
      ) [i[0] + 1, i[1]],
    ]
  );
  stroke(bez2 * 100);
  line1 = bezier_curve(
    flatten(
      [
        bez_begin([0, 0], 70, 0.8),
        bez_tang([0.048533, 0.23843], 70, 1, 0.4),
        bez_tang([0.15861, 0.462284], -70, 0.4, 0.4),
        bez_tang([0.202373, 0.446869], -70, 0.4, 0.4),
        bez_tang([0.253157, 0.428975], 70, 0.4, 0.4),
        bez_tang([0.248083, 0.323591], 70, 0.4, 0.4),
        bez_tang([0.284101, 0.303484], -70, 0.4, 0.4),
        bez_tang([0.325957, 0.280095], -70, 0.4, 0.4),
        bez_tang([0.423748, 0.374566], 70, 0.4, 0.4),
        bez_tang([0.468312, 0.3569], 70, 0.4, 0.4),
        bez_tang([0.50662, 0.341715], -70, 0.4, 0.4),
        bez_tang([0.486207, 0.223664], -70, 0.4, 0.4),
        bez_tang([0.520279, 0.200504], 70, 0.4, 0.4),
        bez_tang([0.565569, 0.169751], 70, 0.4, 0.4),
        bez_tang([0.678965, 0.279637], -70, 0.4, 0.4),
        bez_tang([0.730589, 0.261361], -70, 0.4, 0.4),
        bez_tang([0.772177, 0.246671], 70, 0.4, 0.4),
        bez_tang([0.759396, 0.121256], 70, 0.4, 0.4),
        bez_tang([0.796787, 0.0977908], -70, 0.4, 0.4),
        bez_tang([0.834179, 0.0743256], -70, 0.4, 0.4),
        bez_tang([0.930596, 0.168683], 70, 0.4, 0.4),
        bez_tang([0.971956, 0.1493], 70, 0.4, 0.4),
        //bez_tang([1.00618, 0.133237], -70, 0.4, 0.4),

        //bez_tang([1.00443, 0.0381548], 70, 1, 0.4),
        bez_end([1, 0], 90, 0.8),
      ]
    ), 20
  );

  stroke(line1 * 100);
  echo(bez2);
  //color("blue")
  // stroke(bez2 * 100);
}
