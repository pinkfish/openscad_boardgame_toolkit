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
default_lid_shape_type = SHAPE_TYPE_VORONOI;

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
  MakeBoxWithCapLid(
    [animal_box_width, animal_box_length, animal_box_height],
    wall_thickness=3,
    positive_negative_children=[2]
  ) {
    up($inner_height - animal_token_thickness / 2) {
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
  MakeBoxWithCapLid(
    [animal_box_width, animal_box_length, animal_box_height],
    wall_thickness=3,
    positive_negative_children=[2]
  ) {
    up($inner_height - animal_token_thickness / 2) {
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
  CapBoxLidWithLabel(
    size=[animal_box_width, animal_box_length, animal_box_height],
    text_str="Animals 1"
  );
}

module AnimalBox2Lid() // `make` me
{
  CapBoxLidWithLabel(
    size=[animal_box_width, animal_box_length, animal_box_height],
    text_str="Animals 2"
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

if (FROM_MAKE != 1) {
  BoxLayout();
}
