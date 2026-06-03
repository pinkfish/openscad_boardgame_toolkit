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
include <lib/dominion.scad>

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

elephant_width = 43.5; // done
elephant_length = 54;

polar_bear_length = 53; // done
polar_bear_width = 36.5;

cow_length = 47.5; // done
cow_width = 36.5;

pig_length = 35; // done
pig_width = 24.5;

gazelle_length = 35; // done
gazelle_width = 41;

turkey_width = 24;
turkey_length = 25;
turkey_num = 5;

fly_length = 11;
fly_width = 11;

capybara_length = 32;
capybara_width = 16.5;
capybara_num = 5;

monkey_length = 24; // done
monkey_width = 29;

pangolin_length = 21;
pangolin_width = 16;
pangolin_num = 5;

deer_length = 25.5; // done
deer_width = 47;

goanna_length = 30; // done
goanna_width = 25;

fox_length = 35; // done
fox_width = 16;

snake_length = 41.5;
snake_width = 14;

rabbit_length = 21;
rabbit_width = 18.5;

termite_length = 12;
termite_width = 12;
termite_num = 5;

ornx_width = 39;
ornx_length = 40;

platypus_length = 25; // done
platypus_width = 14.5;

lemur_length = 30; // done
lemur_width = 22;

peacock_length = 27; // done
peacock_width = 30;

gopher_length = 17;
gopher_width = 17.5;
gopher_num = 5;

crockodile_length = 85;
crockodile_width = 16;

goat_length = 36; // done
goat_width = 37;

jaguar_length = 49;
jaguar_width = 20;

rhino_width = 36; // done
rhino_length = 64;

goose_length = 21; // done
goose_width = 25;

eagle_length = 43; // done
eagle_width = 31;

spider_monkey_length = 25;
spider_monkey_width = 26.5;

hoopoe_length = 16;
hoopoe_width = 17;

kangaroo_length = 39; // done
kangaroo_width = 37;

loon_length = 26.5;
loon_width = 13;

tarsier_length = 29; // done
tarsier_width = 12.5;

jay_length = 12;
jay_width = 12.5;

chipmunk_length = 15;
chipmunk_width = 14;

quokka_length = 15; // done
quokka_width = 24;

beaver_length = 35; // done
beaver_width = 15.5;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;
animal_card_size = MakeCardSize(
  length=123,
  width=72,
  single_card_thickness=single_card_thickness
);

card_box_width = default_wall_thickness * 2 + animal_card_size.width;
card_box_length = default_wall_thickness * 2 + animal_card_size.length;
animal_cards_height = animal_card_size.single_card_thickness * animal_card_num + 2;

score_pad_box_width = score_pad_width + default_wall_thickness * 4;
score_pad_box_length = box_length - card_box_length * 2 - 1;
score_pad_box_height = score_pad_thickness * score_pad_number + default_floor_thickness;

sprout_box_length = box_length / 3;
sprout_box_width = card_box_width;
sprout_box_height = box_height - animal_cards_height;

canopy_box_length = box_length - sprout_box_length;
canopy_box_width = card_box_width;
canopy_box_height = sprout_box_height;

animal_box_width = box_width - card_box_width;
animal_box_length = box_length;
animal_box_height = default_floor_thickness + default_lid_thickness + animal_token_thickness + 0.5;

module AnimalCardsBox() // `make` me
{
  MakeBoxWithSlidingLid(
    [card_box_width, card_box_length, animal_cards_height],
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
  MakeBoxWithCapLid(
    [sprout_box_width, sprout_box_length, sprout_box_height],
  ) {
    right(1) back(1)
        RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, sprout_box_height], radius=5);
  }
}

module CanopyBox() // `make` me
{
  MakeBoxWithCapLid(
    [canopy_box_width, canopy_box_length, canopy_box_height],
  ) {
    right(1) back(1)
        RoundedBoxAllSides([$inner_width - 2, $inner_length - 2, sprout_box_height], radius=5);
  }
}

module AnimalBox() // `make` me
{
  MakeBoxWithCapLid(
    [animal_box_width, animal_box_length, animal_box_height],
  ) {
    up($inner_height - animal_token_thickness - 0.5) {
      right(1) back(1) {
          cuboid([elephant_length, elephant_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
          back(elephant_width + 3) {
            cuboid([rhino_length, rhino_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
            back(rhino_width + 3) {
              cuboid([polar_bear_length, polar_bear_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              back(polar_bear_width + 3) {
                cuboid([deer_width, deer_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              }
            }
          }
          right(elephant_length + 3) {
            cuboid([eagle_width, eagle_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
            right(eagle_width + 3) {
              cuboid([snake_width, snake_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              right(snake_width + 3) {
                cuboid([ornx_length, ornx_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                right(ornx_length + 3) {
                  cuboid([kangaroo_width, kangaroo_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                  //right(kangaroo_width + 3){}
                }
              }
            }
          }
          right(rhino_length + 3) back(elephant_width + 3) {
              cuboid([goat_width, goat_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              right(goat_width + 3) {
                cuboid([gazelle_width, gazelle_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                right(gazelle_width + 3) {
                  cuboid([fox_width, fox_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                  right(fox_width + 3) {
                    cuboid([pig_width, pig_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                  }
                }
              }
            }
          right(polar_bear_length + 3) back(elephant_width + rhino_width + 6) {
              cuboid([cow_length, cow_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              right(cow_length + 3) {
                cuboid([beaver_width, beaver_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                right(beaver_width + 3) {
                  cuboid([lemur_width, lemur_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                  right(lemur_width + 3) {
                    cuboid([tarsier_width, tarsier_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                    right(tarsier_width + 3) {
                      cuboid([monkey_length, monkey_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                    }
                  }
                }
              }
            }
          right(deer_width + 3) back(elephant_width + rhino_width + polar_bear_width + 9) {
              cuboid([goanna_length, goanna_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
              right(goanna_length + 3) {
                cuboid([platypus_width, platypus_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                right(platypus_width + 3) {
                  cuboid([goose_length, goose_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                  right(goose_length + 3) {
                    cuboid([quokka_length, quokka_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                    right(quokka_length + 3) {
                      fwd(4)
                        cuboid([peacock_width, peacock_length, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
                      right(peacock_width + 3) {
                      fwd(4)
                        cuboid([spider_monkey_length, spider_monkey_width, animal_token_thickness + 1], anchor=BOTTOM + LEFT + FRONT);
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

module BoxLayout(layout = 0) {
  if (layout == 0) {
    cube([box_width, box_length, 1]);
    cube([box_width, 1, box_height]);
  }
  AnimalCardsBox();
  up(animal_cards_height) {
    SproutBox();
    back(sprout_box_length)
      CanopyBox();
  }
  right(card_box_width)
    AnimalBox();
}

if (FROM_MAKE != 1) {
  BoxLayout();
}
