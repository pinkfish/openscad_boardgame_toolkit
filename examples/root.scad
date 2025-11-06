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

include <BOSL2/beziers.scad>
include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

include <lib/root_shared.scad>

default_lid_thickness = 2;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_SQUARE;

default_label_solid_background = MAKE_MMU == 1;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

sliding_lid_thickness = 3;

wall_thickness = default_wall_thickness;
lid_thickness = default_lid_thickness;
inner_thickness = 1;

quarter_width = (boxData("box", "width") - 1) / 4;

card_box_width = quarter_width * 3;
card_box_length = card_length + wall_thickness * 2;
card_box_height = boxData("box", "height") - boxData("board", "thickness");

marquis_box_width = quarter_width * 2;
marquis_box_length = (boxData("box", "length") - card_box_length - 2) / 3;
marquis_box_height = boxData("marquis", "length") + lid_thickness * 2 + 0.5;
marquis_box_top_height = boxData("box", "height") - boxData("board", "thickness") - marquis_box_height;

erie_box_width = quarter_width * 2;
erie_box_length = marquis_box_length;
erie_box_height = boxData("erie", "width") + lid_thickness * 2 + 0.5;
erie_box_top_width = quarter_width;
erie_box_top_length = erie_box_length;
erie_box_top_height = boxData("box", "height") - boxData("board", "thickness") - erie_box_height;

alliance_box_width = quarter_width;
alliance_box_length = erie_box_length;
alliance_box_height = boxData("alliance", "width") + lid_thickness * 2 + 0.5;
alliance_box_top_height = boxData("box", "height") - alliance_box_height - boxData("board", "thickness");

riverfolk_box_width = quarter_width;
riverfolk_box_length = erie_box_length;
riverfolk_box_height = boxData("riverfolk", "length") + lid_thickness * 2 + 0.5;
riverfolk_box_top_height = boxData("box", "height") - riverfolk_box_height - boxData("board", "thickness");
riverfolk_box_top_width = quarter_width * 2;

vagabond_box_height = boxData("token", "thickness") + lid_thickness * 2 + 1;
vagabond_box_length = erie_box_length;
vagabond_box_width = quarter_width;

lizard_box_width = quarter_width * 2;
lizard_box_length = marquis_box_length;
lizard_box_height = boxData("lizard", "length") + lid_thickness * 2 + 0.5;
lizard_box_top_width = quarter_width * 2;
lizard_box_top_height = boxData("box", "height") - lizard_box_height - boxData("board", "thickness");

item_box_length = wall_thickness * 2 + (square_tile_size + 1) * 5;
item_box_width = quarter_width;
item_box_height = tile_thickness * 3 + 1 + lid_thickness * 2 + 0.5;
item_box_middle_height = tile_thickness * 2 + 1 + lid_thickness * 2 + 0.5;
item_box_winter_height = tile_thickness * 2 + 1 + lid_thickness * 2 + 0.5;
item_box_extras_height = boxData("box", "height") - boxData("board", "thickness") - item_box_height - item_box_middle_height - item_box_winter_height;

dice_box_height = dice_width + lid_thickness * 2 + 1;
dice_box_length = card_box_length + erie_box_length - item_box_length;
dice_box_width = quarter_width;

module CardBox(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=card_box_width, length=card_box_length, height=card_box_height,
    material_colour="grey"
  ) {
    $inner_width = card_box_width - wall_thickness * 2;
    middle = card_width * 2 + 3;
    translate([($inner_width - middle) / 2, 0, 0]) {
      cube([card_width, card_length, card_box_height]);
      translate([card_width + 3, 0, 0]) cube([card_width, card_length, card_box_height]);
      translate([card_width / 2, -1, -lid_thickness - 0.01])
        FingerHoleBase(radius=15, height=card_box_height);
      translate([card_width / 2 + card_width + 3, -1, -lid_thickness - 0.01])
        FingerHoleBase(radius=15, height=card_box_height);
    }
  }
  if (generate_lid) {
    translate([card_box_width + 10, 0, 0]) {
      CapBoxLidWithLabel(
        width=card_box_width, length=card_box_length, height=card_box_height,
        text_width=70, text_height=20, text_str="Cards", label_rotated=false,
        material_colour="grey"
      );
    }
  }
}

module MarquisBoxBottom(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=marquis_box_width, length=marquis_box_length, height=marquis_box_height,
    material_colour="orange"
  ) {
    len = boxData("token", "thickness") * 8 + 1;
    // Put a bunch of places in for the marquis items
    translate([($inner_width - len) / 2, 1, -0.75]) {
      translate([len / 2, boxData("marquis", "width") / 2 + 1, boxData("marquis", "length") / 2 + 1])
        rotate([90, 0, 90]) MarquisCharacter(height=len);
      translate([len / 2, boxData("marquis", "width") / 2, boxData("marquis", "length") / 2 + 10])
        cuboid([len, boxData("marquis", "width"), boxData("marquis", "length")]);
      translate(
        [
          len / 2,
          boxData("marquis", "width") / 2 + boxData("marquis", "width") + 2,
          boxData("marquis", "length") / 2 + 1,
        ]
      ) rotate([90, 0, 90]) MarquisCharacter(height=len);
    }
    // Second smaller marquis bits
    translate([($inner_width - len - boxData("token", "thickness")) / 2, 1, -0.75]) {
      second_len = len + boxData("token", "thickness");
      translate(
        [
          second_len / 2,
          boxData("marquis", "width") / 2 + boxData("marquis", "width") * 2 + 3,
          boxData("marquis", "length") / 2 + 1,
        ]
      ) rotate([90, 0, 90]) MarquisCharacter(height=second_len);
      translate(
        [
          second_len / 2,
          boxData("marquis", "width") / 2 + boxData("marquis", "width") * 2 + 3,
          boxData("marquis", "length") / 2 + 10,
        ]
      ) cuboid([second_len, boxData("marquis", "width"), boxData("marquis", "length")]);
    }
    translate([0, 0, boxData("marquis", "length") / 2])
      RoundedBoxAllSides($inner_width, marquis_box_length - wall_thickness * 2, boxData("marquis", "length"), 7);
  }
  if (generate_lid) {
    translate([marquis_box_width + 10, 0, 0]) {
      CapBoxLidWithEyes(
        width=marquis_box_width, length=marquis_box_length, height=marquis_box_height,
        material_colour="orange"
      ) {
        color("black") translate([0, 10, 0]) linear_extrude(height=default_lid_thickness) scale(2)
                MarquisEyes2d();
      }
    }
  }
}

module MarquisBoxTop(generate_lid = true) // `make` me
{
  module BuildingSpots(finger_holes, icon, just_icons) {
    label_depth = just_icons ? -0.495 : -0.5;
    label_height = just_icons ? 0.5 : 2;
    translate([square_tile_size / 2, square_tile_size / 2, 0]) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 + 1],
          finger_hole_radius=7, finger_holes=finger_holes
        );
      }

      if (icon == "anvil") {
        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
              Anvil2d(size=10, with_hammer=true);
      } else if (icon == "saw") {
        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
              SawBlade2d(size=10, $fn=32);
      } else if (icon == "handshake") {
        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
              Handshake2d(size=10);
      }

      translate([square_tile_size + 1, 0, 0]) {
        if (just_icons == false) {
          CuboidWithIndentsBottom(
            [square_tile_size, square_tile_size, tile_thickness * marquis_building_token_num / 2 + 1],
            finger_hole_radius=7, finger_holes=finger_holes
          );
        }
        if (icon == "anvil") {
          translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
                Anvil2d(size=10, with_hammer=true);
        } else if (icon == "saw") {
          translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
                SawBlade2d(size=10);
        } else if (icon == "handshake") {
          translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height)
                Handshake2d(size=10);
        }
      }
    }
  }
  module InnerPieces(just_icons) {
    label_depth = just_icons ? -0.495 : -0.5;
    label_height = just_icons ? 0.5 : 2;
    // Wood markers.
    translate(
      [
        round_tile_diameter / 2,
        round_tile_diameter / 2,
        $inner_height - tile_thickness * marquis_wood_token_num / 2,
      ]
    ) {
      if (just_icons == false) {

        CylinderWithIndents(
          radius=round_tile_diameter / 2,
          height=tile_thickness * marquis_wood_token_num / 2, finger_hole_radius=7,
          finger_holes=[110]
        );
      }

      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) SingleLog2d(15);
    }
    translate(
      [
        round_tile_diameter / 2 + round_tile_diameter + 2,
        round_tile_diameter / 2,
        $inner_height - tile_thickness * marquis_wood_token_num / 2,
      ]
    ) {
      if (just_icons == false) {
        CylinderWithIndents(
          radius=round_tile_diameter / 2,
          height=tile_thickness * marquis_wood_token_num / 2, finger_hole_radius=7,
          finger_holes=[110]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) SingleLog2d(15);
    }

    // Keep token
    translate(
      [
        round_tile_diameter / 2 + round_tile_diameter * 2 + 2,
        round_tile_diameter / 2 * 6 / 4,
        $inner_height - tile_thickness - 0.5,
      ]
    ) {
      if (just_icons == false) {
        CylinderWithIndents(
          radius=round_tile_diameter / 2, height=tile_thickness + 1,
          finger_hole_radius=10, finger_holes=[135]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) rotate(-90)
              Keep2d(15);
    }

    // Score marker.
    translate(
      [
        round_tile_diameter * 2 + 2 + square_tile_size / 2,
        $inner_length - 5 - square_tile_size / 2,
        $inner_height - tile_thickness - 0.5,
      ]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness + 1],
          finger_hole_radius=9.5, finger_holes=[2]
        );
      }

      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) LaurelWreath2d(15);
    }

    // Buildings.
    translate(
      [
        0,
        $inner_length - square_tile_size,
        $inner_height - tile_thickness * marquis_building_token_num / 2 - 0.5,
      ]
    ) {
      BuildingSpots(finger_holes=[6], "anvil", just_icons);
    }
    translate(
      [
        $inner_width - square_tile_size * 2 - 1,
        $inner_length - square_tile_size,
        $inner_height - tile_thickness * marquis_building_token_num / 2 - 0.5,
      ]
    ) {
      BuildingSpots(finger_holes=[6], "saw", just_icons);
    }
    translate(
      [
        $inner_width - square_tile_size * 2 - 1,
        0,
        $inner_height - tile_thickness * marquis_building_token_num / 2 - 0.5,
      ]
    ) {
      BuildingSpots(finger_holes=[2], "handshake", just_icons);
    }
  }
  MakeBoxWithSlidingLid(
    width=marquis_box_width, length=marquis_box_length, height=marquis_box_top_height,
    lid_thickness=sliding_lid_thickness, material_colour="orange",
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(just_icons=false);
    if (default_label_solid_background) {
      InnerPieces(just_icons=true);
    }
  }
  if (generate_lid) {
    translate([marquis_box_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=marquis_box_width, length=marquis_box_length,
        lid_thickness=sliding_lid_thickness, material_colour="orange"
      ) {
        color("black") translate([0, 10, 0]) linear_extrude(height=default_lid_thickness) scale(2)
                MarquisEyes2d();
      }
    }
  }
}

module VagabondBox(generate_lid = true) // `make` me
{
  module InnerPieces(just_icons) {
    label_depth = just_icons ? -0.495 : -0.5;
    label_height = just_icons ? 0.5 : 2;
    if (just_icons == false) {
      translate(
        [
          boxData("vagabond", "width") / 2,
          boxData("vagabond", "length") / 2 + 5,
          $inner_height - boxData("token", "thickness") - 0.5 + (boxData("token", "thickness") + 1) / 2,
        ]
      ) {
        rotate([0, 0, 180]) VagabondCharacter(height=boxData("token", "thickness") + 1);
        translate([0, boxData("vagabond", "length") / 2 - 3, 0])
          cyl(r=6, anchor=BOTTOM, rounding=5.75, h=boxData("box", "height"));
        translate([0, -boxData("vagabond", "length") / 2, 0])
          cyl(r=6, anchor=BOTTOM, rounding=5.75, h=boxData("box", "height"));
      }
    }

    // Score marker.
    translate(
      [$inner_width - square_tile_size * 2 / 4, square_tile_size / 2, $inner_height - tile_thickness - 0.5]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness + 1],
          finger_hole_radius=10, finger_holes=[2]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) LaurelWreath2d(15);
    }

    // Relationship markers.
    translate(
      [
        $inner_width - square_tile_size,
        $inner_length - square_tile_size,
        $inner_height - tile_thickness * vagabond_relationship_num_each / 2 - 0.5,
      ]
    ) {
      if (just_icons == false) {
        cube([square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num_each / 2 + 1]);
        translate([-5, square_tile_size / 2, 0]) xcyl(r=7, h=vagabond_box_height, anchor=BOTTOM);
      }

      translate([square_tile_size / 2, square_tile_size / 2, label_depth]) color("black")
          linear_extrude(height=label_height) text("Relation", valign="center", halign="center", size=3);
    }
    translate(
      [
        0,
        $inner_length - square_tile_size,
        $inner_height - tile_thickness * vagabond_relationship_num_each / 2 - 0.5,
      ]
    ) {
      if (just_icons == false) {

        cube([square_tile_size, square_tile_size, tile_thickness * vagabond_relationship_num_each / 2 + 1]);
      }
      translate([square_tile_size / 2, square_tile_size / 2, label_depth]) color("black")
          linear_extrude(height=label_height) text("Relation", valign="center", halign="center", size=3);
    }
  }
  MakeBoxWithSlidingLid(
    width=vagabond_box_width, length=vagabond_box_length, height=vagabond_box_height,
    lid_thickness=sliding_lid_thickness, material_colour="grey",
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(just_icons=false);
    if (default_label_solid_background) {
      InnerPieces(just_icons=true);
    }
  }
  if (generate_lid) {
    translate([vagabond_box_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=vagabond_box_width, length=vagabond_box_length,
        lid_thickness=sliding_lid_thickness, material_colour="grey"
      ) {
        color("black") translate([0, -8, 0]) linear_extrude(height=default_lid_thickness) VagabondEyes2d();
      }
    }
  }
}

module ErieBoxBottom(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=erie_box_width, length=erie_box_length, height=erie_box_height,
    material_colour="blue"
  ) {
    len = boxData("token", "thickness") * 10 + 1;

    translate([($inner_width - len) / 2, 0, 0]) {
      translate(
        [len / 2, boxData("erie", "length") / 2 + 3, $inner_height - boxData("erie", "width") / 2 - 0.5]
      ) {
        rotate([0, 270, 0]) ErieCharacter(height=len);
        translate([0, 0, 5 + boxData("erie", "width") / 2])
          cuboid([len, boxData("erie", "length"), boxData("erie", "width") / 2], anchor=TOP);
      }
      translate(
        [
          len / 2,
          boxData("erie", "length") / 2 + boxData("erie", "length") + 6,
          $inner_height - boxData("erie", "width") / 2 - 0.5,
        ]
      ) {
        rotate([0, 270, 0]) ErieCharacter(height=len);
        translate([0, 0, 5 + boxData("erie", "width") / 2])
          cuboid([len, boxData("erie", "length"), boxData("erie", "width") / 2], anchor=TOP);
      }
    }
    translate([0, 0, $inner_height - boxData("erie", "width") / 2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=erie_box_height, radius=5);
  }
  if (generate_lid) {
    translate([erie_box_width + 10, 0, 0]) {
      CapBoxLidWithEyes(
        width=erie_box_width, length=erie_box_length, height=erie_box_height,
        material_colour="blue"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(2) ErieEyes2d();
      }
    }
  }
}

module ErieBoxTop(generate_lid = true) // `make` me
{
  module InnerPieces(just_icons) {
    icon_height = just_icons ? 0.5 : 2;
    icon_depth = just_icons ? -0.495 : -0.5;
    // Score marker.
    translate([square_tile_size / 2, $inner_length - square_tile_size / 2, $inner_height - tile_thickness - 0.5]) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness + 1],
          finger_hole_radius=8, finger_holes=[6]
        );
      }

      translate([0, 0, icon_depth]) color("black") linear_extrude(height=icon_height) LaurelWreath2d(15);
    }

    // Roosts.
    for (i = [0:1:1]) {
      num_tiles = 3 + i;
      translate(
        [
          (square_tile_size + 1) * i + square_tile_size / 2,
          square_tile_size / 2,
          $inner_height - num_tiles * tile_thickness - 0.5,
        ]
      ) {
        if (just_icons == false) {
          CuboidWithIndentsBottom(
            [square_tile_size, square_tile_size, tile_thickness * num_tiles + 1],
            finger_hole_radius=8, finger_holes=[2]
          );
        }

        translate([0, 0, icon_depth]) color("black") linear_extrude(height=icon_height) ErieTree2d(15);
      }
    }
  }
  MakeBoxWithSlidingLid(
    width=erie_box_top_width, length=erie_box_top_length, height=erie_box_top_height,
    wall_thickness=wall_thickness, floor_thickness=lid_thickness,
    lid_thickness=sliding_lid_thickness, material_colour="blue",
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(just_icons=false);
    if (default_label_solid_background) {
      InnerPieces(just_icons=true);
    }
  }
  if (generate_lid) {
    translate([erie_box_top_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=erie_box_top_width, length=erie_box_top_length,
        lid_thickness=sliding_lid_thickness, material_colour="blue"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(2) ErieEyes2d();
      }
    }
  }
}

module AllianceBoxBottom(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=alliance_box_width, length=alliance_box_length, height=alliance_box_height,
    material_colour="green"
  ) {
    len = boxData("token", "thickness") * 5 + 1;

    translate([($inner_width - len) / 2, 3.5, 0]) {
      translate(
        [
          len / 2,
          boxData("alliance", "length") / 2 + 1.5,
          $inner_height - boxData("alliance", "width") / 2 - 0.5,
        ]
      ) {
        rotate([0, 270, 0]) AllianceCharacter(height=len);
        translate([0, 0, boxData("alliance", "width") / 2]) cuboid(
            [len, boxData("alliance", "length"), boxData("alliance", "width") / 2 + 4.5], anchor=TOP
          );
      }
      translate(
        [
          len / 2,
          boxData("alliance", "length") / 2 + 2 + boxData("alliance", "length") + 4,
          $inner_height - boxData("alliance", "width") / 2 - 0.5,
        ]
      ) {
        rotate([0, 270, 0]) AllianceCharacter(height=len);
        translate([0, 0, boxData("alliance", "width") / 2]) cuboid(
            [len, boxData("alliance", "length"), boxData("alliance", "width") / 2 + 4.5], anchor=TOP
          );
      }
    }
    translate([0, 0, $inner_height - boxData("alliance", "length") / 2])
      RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=erie_box_height, radius=5);
  }
  if (generate_lid) {
    translate([alliance_box_width + 10, 0, 0]) {
      CapBoxLidWithEyes(
        width=alliance_box_width, length=alliance_box_length, height=alliance_box_height,
        material_colour="green"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(1.5) AllianceEyes2d();
      }
    }
  }
}

module AllianceBoxTop(generate_lid = true) // `make` me
{
  module InnerPieces(just_icon) {
    label_depth = just_icon ? -0.495 : -0.5;
    label_height = just_icon ? 0.5 : 2;
    // Score marker.
    translate([square_tile_size / 2, square_tile_size / 2, $inner_height - tile_thickness - 0.5]) {
      if (just_icon == false) {
        CuboidWithIndentsBottom(
          size=[square_tile_size, square_tile_size, tile_thickness + 1],
          finger_hole_radius=10, finger_holes=[0]
        );
      }

      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) LaurelWreath2d(15);
    }

    // Sympathy tokens.
    translate(
      [
        $inner_width - round_tile_diameter / 2,
        round_tile_diameter / 2 + 1,
        $inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 - 0.5,
      ]
    ) {
      if (just_icon == false) {
        CylinderWithIndents(
          radius=round_tile_diameter / 2,
          height=tile_thickness * woodland_aliance_sympathy_num / 2 + 1,
          finger_hole_radius=8, finger_holes=[135]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) Fist2d(12);
    }
    translate(
      [
        $inner_width - round_tile_diameter / 2,
        $inner_length - round_tile_diameter / 2 - 1,
        $inner_height - tile_thickness * woodland_aliance_sympathy_num / 2 - 0.5,
      ]
    ) {
      if (just_icon == false) {
        CylinderWithIndents(
          radius=round_tile_diameter / 2,
          height=tile_thickness * woodland_aliance_sympathy_num / 2 + 1,
          finger_hole_radius=8, finger_holes=[225]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) Fist2d(12);
    }

    // Bases.
    translate(
      [
        square_tile_size / 2,
        $inner_length - square_tile_size / 2,
        $inner_height - tile_thickness * woodland_alliance_base_num - 0.5,
      ]
    ) {
      if (just_icon == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * woodland_alliance_base_num + 1],
          finger_hole_radius=7, finger_holes=[0]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) AllianceCamp2d(12);
    }
  }

  MakeBoxWithSlidingLid(
    width=alliance_box_width, length=alliance_box_length, height=alliance_box_top_height,
    lid_thickness=sliding_lid_thickness, material_colour="green", last_child_positive=true
  ) {
    InnerPieces(false);
    if (default_label_solid_background) {
      InnerPieces(just_icon=true);
    }
  }
  if (generate_lid) {
    translate([alliance_box_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=alliance_box_width, length=alliance_box_length,
        lid_thickness=sliding_lid_thickness, material_colour="green"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(1.5) AllianceEyes2d();
      }
    }
  }
}

module RiverfolkBoxBottom(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=riverfolk_box_width, length=riverfolk_box_length, height=riverfolk_box_height,
    material_colour="lightblue"
  ) {
    len = boxData("token", "thickness") * 5 + 1;
    translate([0, 0, 0])for (i = [0:1:2]) {
      translate(
        [
          len / 2,
          boxData("riverfolk", "width") / 2 + (boxData("riverfolk", "width") + 2) * i,
          $inner_height - boxData("riverfolk", "length") / 2 - 0.5,
        ]
      ) {
        rotate([90, 0, 90]) RiverfolkCharacter(height=len + 1);
        translate([0, 0, boxData("riverfolk", "length") / 2]) cuboid(
            [len + 1, boxData("riverfolk", "width"), boxData("riverfolk", "length") - 3], anchor=TOP
          );
      }
    }
    translate([0, 0, $inner_height - boxData("riverfolk", "length") / 2]) RoundedBoxAllSides(
        width=$inner_width, length=$inner_length, height=boxData("riverfolk", "length") / 2, radius=5
      );
  }
  if (generate_lid) {
    translate([riverfolk_box_width + 10, 0, 0]) {
      CapBoxLidWithEyes(
        width=riverfolk_box_width, length=riverfolk_box_length, height=riverfolk_box_height,
        material_colour="lightblue"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(1.5) RiverfolkEyes2d();
      }
    }
  }
}

module RiverfolkBoxTop(generate_lid = true) // `make` me
{
  module InnerPieces(just_icon) {
    label_depth = just_icon ? -0.495 : -0.5;
    label_height = just_icon ? 0.5 : 2;
    // Score marker.
    translate([square_tile_size / 2, square_tile_size / 2, $inner_height - tile_thickness - 0.5]) {
      if (just_icon == false) {
        CuboidWithIndentsBottom(
          size=[square_tile_size, square_tile_size, tile_thickness + 1],
          finger_hole_radius=10, finger_holes=[2]
        );
      }

      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) LaurelWreath2d(15);
    }

    // trading posts.
    for (i = [0:1:2]) {
      translate(
        [
          $inner_width - round_tile_diameter / 2 - (round_tile_diameter + 2) * i - 2,
          round_tile_diameter / 2 + 2,
          $inner_height - tile_thickness * 5 + 0.5,
        ]
      ) {
        if (just_icon == false) {

          CylinderWithIndents(
            radius=(round_tile_diameter + 0.5) / 2, height=tile_thickness * 5 + 1,
            finger_hole_radius=8, finger_holes=[90]
          );
        }

        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) Sign2d(15);
      }
    }

    // glass things.
    translate([($inner_width - (riverfolk_glass_diameter + 10) * 3) / 2, 0, 0])for (i = [0:1:2]) {
      translate(
        [
          2 + riverfolk_glass_diameter / 2 + (riverfolk_glass_diameter + 10) * i,
          $inner_length - riverfolk_glass_diameter / 2 - 2,
          $inner_height - riverfolk_glass_thickness - 0.5,
        ]
      ) {
        if (just_icon == false) {

          CylinderWithIndents(
            radius=riverfolk_glass_diameter / 2, height=riverfolk_glass_thickness + 1,
            finger_hole_radius=8, finger_holes=[0, 180]
          );
        }

        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) egg(13, 4, 4, 20);
      }
    }
  }

  MakeBoxWithSlidingLid(
    width=riverfolk_box_top_width, length=riverfolk_box_length,
    height=riverfolk_box_top_height, lid_thickness=sliding_lid_thickness,
    lid_on_length=true, material_colour="lightblue",
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(false);
    if (default_label_solid_background) {
      InnerPieces(just_icon=true);
    }
  }
  if (generate_lid) {
    translate([riverfolk_box_top_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=riverfolk_box_top_width, length=riverfolk_box_length,
        lid_thickness=sliding_lid_thickness, material_colour="lightblue"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(2.2) RiverfolkEyes2d();
      }
    }
  }
}

module LizardBoxBottom(generate_lid = true) // `make` me
{
  MakeBoxWithCapLid(
    width=lizard_box_width, length=lizard_box_length, height=lizard_box_height,
    material_colour="yellow"
  ) {
    //  Put a bunch of places in for the lizard items
    for (j = [0:1:4]) {
      for (i = [0:1:4]) {
        translate(
          [
            (boxData("lizard", "width") + 1.8) * i + boxData("lizard", "width") / 2,
            (boxData("token", "thickness") + 0.1) * j + boxData("token", "thickness") / 2 + 1.5 + 2,
            boxData("lizard", "length") / 2 - 0.25,
          ]
        ) {
          rotate([90, 0, 0]) LizardCharacter(height=boxData("token", "thickness") + 0.5);
          translate([0, 0, 4.5])
            cuboid([boxData("lizard", "width"), boxData("token", "thickness") + 0.5, 20]);
        }
      }
    }
    translate([0, 0, boxData("lizard", "length") / 2])
      RoundedBoxAllSides($inner_width, lizard_box_length - wall_thickness * 2, boxData("lizard", "length"), 7);
  }
  if (generate_lid) {
    translate([lizard_box_width + 10, 0, 0]) {
      CapBoxLidWithEyes(
        width=lizard_box_width, length=lizard_box_length, height=lizard_box_height,
        material_colour="yellow"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(2.5) LizardEyes2d();
      }
    }
  }
}

module LizardBoxTop(generate_lid = true) // `make` me
{
  module InnerPieces(just_icons) {
    label_depth = just_icons ? -0.495 : -0.5;
    label_height = just_icons ? 0.5 : 2;
    // Garden markers.
    for (i = [0:1:1]) {
      translate(
        [
          square_tile_size / 2 + (square_tile_size + 10) * i + 3,
          square_tile_size / 2,
          $inner_height - tile_thickness * 5 - 0.5,
        ]
      ) {
        if (just_icons == false) {
          CuboidWithIndentsBottom(
            [square_tile_size, square_tile_size, tile_thickness * 5 + 1],
            finger_hole_radius=8, finger_holes=[2]
          );
        }

        translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) if (i == 0) {
              Fox2d(10);
            } else {
              Rabbit2d(10);
            }
      }
    }
    translate(
      [
        square_tile_size / 2 + (square_tile_size + 10) * 1 + 3,
        $inner_length - square_tile_size / 2,
        $inner_height - tile_thickness * 5 - 0.5,
      ]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * 5 + 1],
          finger_hole_radius=8, finger_holes=[6]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) Mouse2d(10);
    }

    // no go marker
    translate(
      [
        $inner_width - square_tile_size / 2,
        $inner_length - square_tile_size / 2,
        $inner_height - tile_thickness * 1 - 0.5,
      ]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * 1 + 1],
          finger_hole_radius=8, finger_holes=[6]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) union() {
              difference() {
                circle(d=15);
                circle(d=13);
              }
              rotate(45) rect([2, 14.5]);
              rotate(-45) rect([2, 14.5]);
            }
    }

    // lizard marker
    translate(
      [$inner_width - square_tile_size / 2, square_tile_size / 2, $inner_height - tile_thickness * 2 - 0.5]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * 2 + 1],
          finger_hole_radius=8, finger_holes=[2]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) scale(0.5)
              LizardEyes2d();
    }

    // Score marker.
    translate(
      [square_tile_size / 2, $inner_length - square_tile_size / 2, $inner_height - tile_thickness * 1 - 0.5]
    ) {
      if (just_icons == false) {
        CuboidWithIndentsBottom(
          [square_tile_size, square_tile_size, tile_thickness * 1 + 1],
          finger_hole_radius=8, finger_holes=[6]
        );
      }
      translate([0, 0, label_depth]) color("black") linear_extrude(height=label_height) LaurelWreath2d(15);
    }
  }
  MakeBoxWithSlidingLid(
    width=lizard_box_top_width, length=lizard_box_length, height=lizard_box_top_height,
    lid_thickness=sliding_lid_thickness, material_colour="yellow",
    last_child_positive=default_label_solid_background
  ) {
    InnerPieces(just_icons=false);
    if (default_label_solid_background) {
      union() InnerPieces(just_icons=true);
    }
  }
  if (generate_lid) {
    translate([lizard_box_top_width + 10, 0, 0]) {
      SlidingLidWithEyes(
        width=lizard_box_top_width, length=lizard_box_length,
        lid_thickness=sliding_lid_thickness, material_colour="yellow"
      ) {
        color("black") linear_extrude(height=default_lid_thickness) scale(2) LizardEyes2d();
      }
    }
  }
}

module ItemsBoxBottom() // `make` me
{
  module MakeItems(just_icon) {
    depths = [
      "torch",
      2,
      "boot",
      3,
      "coins",
      1,
      "crossbow",
      2,
      "sword",
      3,
      "bag",
      1,
      "hammer/teapot",
      2,
      "ruins",
      3,
      "ruins",
      3,
      "ruins",
      2,
    ];
    for (i = [0:1:4]) {
      if (depths[i * 4 + 1] != 0) {
        translate(
          [
            square_tile_size / 2,
            (square_tile_size + 1) * i + square_tile_size / 2,
            $inner_height - tile_thickness * depths[i * 4 + 1] - 0.5,
          ]
        ) {
          if (just_icon) {
          } else {
            CuboidWithIndentsBottom(
              [square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1],
              finger_hole_radius=6, finger_holes=[0]
            );
          }
          translate([0, 0, just_icon ? -0.495 : -0.5]) {
            color("black") GenerateIcon(depths[i * 4], height=just_icon ? 0.5 : 2);
            translate([square_tile_size * 4 / 10, 0, 0]) color("black")
                linear_extrude(height=just_icon ? 0.5 : 2) rotate(90)
                    text(
                      text=depths[i * 4] == "ruins" ? "R" : "S", font="Stencil Std:style=Bold",
                      size=2, halign="center", valign="center"
                    );
          }
        }
      }
      if (depths[i * 4 + 3] != 0) {
        translate(
          [
            $inner_width - square_tile_size + square_tile_size / 2,
            (square_tile_size + 1) * i + square_tile_size / 2,
            $inner_height - tile_thickness * depths[i * 4 + 3] - 0.5,
          ]
        ) {
          if (just_icon) {
          } else {

            CuboidWithIndentsBottom(
              [square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1],
              finger_hole_radius=6, finger_holes=[4]
            );
          }
          translate([0, 0, just_icon ? -0.495 : -0.5]) {
            color("black") GenerateIcon(depths[i * 4 + 2], height=just_icon ? 0.5 : 2);
            translate([square_tile_size * 4 / 10, 0, 0]) color("black")
                linear_extrude(height=just_icon ? 0.5 : 2) rotate(90)
                    text(
                      text=depths[i * 4 + 2] == "ruins" ? "R" : "S", font="Stencil Std:style=Bold",
                      size=2, halign="center", valign="center"
                    );
          }
        }
      }
    }
  }
  MakeBoxWithSlidingLid(
    width=item_box_width, length=item_box_length, height=item_box_height,
    lid_thickness=sliding_lid_thickness, material_colour="grey",
    last_child_positive=default_label_solid_background
  ) {
    MakeItems(false);
    if (default_label_solid_background) {
      MakeItems(true);
    }
  }
}

module ItemsBoxBottomLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=item_box_width, length=item_box_length,
    text_str="Items", lid_thickness=sliding_lid_thickness,
    material_colour="grey", label_background_colour="grey"
  );
}

module GenerateIcon(icon, height = 2) {
  if (icon == "bag") {
    linear_extrude(height=height) Bag2d(10);
  } else if (icon == "boot") {
    linear_extrude(height=height) Shoe2d(10);
  } else if (icon == "torch") {
    linear_extrude(height=height) Torch2d(10, 3);
  } else if (icon == "crossbow") {
    linear_extrude(height=height) Crossbow2d(10, 8);
  } else if (icon == "hammer/teapot") {
    translate([0, -5, 0]) linear_extrude(height=height) rotate(90) Sledgehammer2d(10, 5);
    translate([0, 3, 0]) linear_extrude(height=height) Teapot2d(10, 8);
  } else if (icon == "hammer") {
    linear_extrude(height=height) Sledgehammer2d(10, 5);
  } else if (icon == "sword") {
    linear_extrude(height=height) Sword2d(10, 5);
  } else if (icon == "teapot") {
    linear_extrude(height=height) Teapot2d(10, 8);
  } else if (icon == "coins") {
    linear_extrude(height=height) CoinPile2d(10);
  } else if (icon == "ruins") {
    linear_extrude(height=height) rotate(90) Ruins2d(10);
  } else if (icon == "n/a") {
    linear_extrude(height=height) rotate(90)
        text(text=icon, font="Stencil Std:style=Bold", size=2.5, halign="center", valign="center");
  }
}

module ItemsBoxMiddle(generate_lid = true) // `make` me
{

  module MakeAllItems(just_icon) {
    // 12 craftable items (2× bag, 2× boot, 1× crossbow, 1× hammer, 2× sword, 2× teapot, 2× coins)
    depths = [
      "bag",
      2,
      "boot",
      2,
      "crossbow",
      1,
      "hammer",
      1,
      "sword",
      2,
      "teapot",
      2,
      "coins",
      2,
      "n/a",
      0,
      "ruins",
      2,
      "ruins",
      2,
    ];
    for (i = [0:1:4]) {
      if (depths[i * 4 + 1] != 0) {
        translate(
          [
            square_tile_size / 2,
            (square_tile_size + 01) * i + square_tile_size / 2,
            $inner_height - tile_thickness * depths[i * 4 + 1] - 0.5,
          ]
        ) {
          if (just_icon) {
          } else {
            CuboidWithIndentsBottom(
              [square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 1] + 1],
              finger_hole_radius=6, finger_holes=[0]
            );
          }

          translate([0, 0, just_icon ? -0.48 : -0.5]) color("black")
              GenerateIcon(depths[i * 4], height=just_icon ? 0.5 : 2);
        }
      }
      if (depths[i * 4 + 3] != 0) {
        translate(
          [
            $inner_width - square_tile_size + square_tile_size / 2,
            (square_tile_size + 1) * i + square_tile_size / 2,
            $inner_height - tile_thickness * depths[i * 4 + 3] - 0.5,
          ]
        ) {
          if (just_icon) {
          } else {
            CuboidWithIndentsBottom(
              [square_tile_size, square_tile_size, tile_thickness * depths[i * 4 + 3] + 1],
              finger_hole_radius=6, finger_holes=[4]
            );
          }
          translate([0, 0, just_icon ? -0.48 : -0.5]) color("black")
              GenerateIcon(depths[i * 4 + 2], height=just_icon ? 0.5 : 2);
        }
      }
    }
  }
  MakeBoxWithSlidingLid(
    width=item_box_width, length=item_box_length, height=item_box_middle_height,
    lid_thickness=sliding_lid_thickness, material_colour="grey",
    last_child_positive=default_label_solid_background, label_background_colour="grey"
  ) {
    MakeAllItems(false);
    if (default_label_solid_background) {
      union() {
        MakeAllItems(true);
      }
    }
  }
  if (generate_lid) {
    translate([item_box_width + 10, 0, 0]) {
      SlidingBoxLidWithLabel(
        width=item_box_width, length=item_box_length,
        text_str="Items", lid_thickness=sliding_lid_thickness,
        label_colour="blue", material_colour="grey", label_background_colour="grey"
      );
    }
  }
}

module ItemsBoxWinter(generate_lid = true) // `make` me
{
  MakeBoxWithSlidingLid(
    width=item_box_width, length=item_box_length, height=item_box_winter_height,
    finger_hold_height=3, lid_thickness=sliding_lid_thickness, material_colour="grey"
  ) {
    for (i = [0:1:5]) {
      translate(
        [$inner_width / 2, boxData("winter", "length") / 2 + (boxData("winter", "length") + 0) * i + 3, 0]
      ) {
        rotate([0, 0, 90]) WinterToken(tile_thickness * 2 + 1);
        translate([boxData("winter", "width") / 2, -5, 0]) sphere(r=8, anchor=BOTTOM);
        translate([-boxData("winter", "width") / 2, -5, 0]) sphere(r=8, anchor=BOTTOM);
      }
    }
  }
  if (generate_lid) {
    translate([item_box_width + 10, 0, 0]) {
      SlidingBoxLidWithLabel(
        width=item_box_width, length=item_box_length,
        text_str="Winter", lid_thickness=sliding_lid_thickness,
        label_colour="blue", material_colour="grey", label_background_colour="grey"
      );
    }
  }
}

module DiceBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=dice_box_width, length=dice_box_length, height=dice_box_height,
    lid_thickness=sliding_lid_thickness, material_colour="grey"
  ) {
    translate([dice_width / 2 + 3, dice_width / 2 + 3, dice_width / 2]) {
      color("grey") Dodecahedron(dice_width);
      translate([0, 0, dice_width / 2]) color("grey") cyl(d=dice_length, h=dice_box_height);
    }

    translate([$inner_width - dice_width / 2 - 3, $inner_length - dice_width / 2 - 3, dice_width / 2]) {
      color("grey") Dodecahedron(dice_width);
      translate([0, 0, dice_width / 2]) color("grey") cyl(d=dice_length, h=dice_box_height);
    }
    translate([0, 0, dice_width / 2]) color("grey")
        RoundedBoxAllSides(width=$inner_width, length=$inner_length, height=dice_box_height, radius=10);
  }
}
module DiceBoxLid() // `make` me
{
  SlidingLid(
    width=dice_box_width, length=dice_box_length, lid_thickness=sliding_lid_thickness,
    material_colour="grey"
  ) {
    translate([0, 0, 0])
      LidMeshBasic(
        width=$inner_width, length=$inner_length, lid_thickness=lid_thickness,
        boundary=5, layout_width=default_lid_layout_width, material_colour="grey"
      )
        color("grey")
          ShapeByType(
            shape_type=default_lid_shape_type, shape_width=default_lid_shape_width,
            shape_thickness=default_lid_shape_thickness, shape_aspect_ratio=1.0
          );

    translate([(dice_box_width) / 2, (dice_box_length) / 2, 0]) color("black")
        linear_extrude(height=lid_thickness) D20Outline2d(20, 1);
  }
}

module ItemsBoxExtras(generate_lid = true) // `make` me
{
  module RenderItem(item, just_icon) {
    if (just_icon) {
    } else {
      if (item[2] == "square") {
        translate([slightly_larger_round_tile_diameter / 2, slightly_larger_round_tile_diameter / 2, 0]) {
          color("grey") CuboidWithIndentsBottom(
              [larger_square_tile_, larger_square_tile_, tile_thickness * item[1] + 1],
              finger_hole_radius=6, finger_holes=[item[3] == 1 ? 0 : 4]
            );
        }
      } else {
        translate([slightly_larger_round_tile_diameter / 2, slightly_larger_round_tile_diameter / 2, 0]) {
          color("grey") CylinderWithIndents(
              radius=slightly_larger_round_tile_diameter / 2,
              height=tile_thickness * item[1] + 1, finger_hole_radius=6,
              finger_holes=[item[3] == 1 ? 0 : 180]
            );
        }
      }
    }
    translate(
      [
        (slightly_larger_round_tile_diameter) / 2,
        slightly_larger_round_tile_diameter / 2,
        just_icon ? -0.48 : -0.5,
      ]
    ) color("black") linear_extrude(height=just_icon ? 0.5 : 2) rotate(90)
            text(text=item[0], font="Stencil Std:style=Bold", size=2.5, halign="center", valign="center");
  }

  module MakeAllItems(just_icon) {
    depths = [
      ["A/B", 2, "round", 1],
      ["C/D", 2, "round", -1],
      ["E/F", 2, "round", 1],
      ["G/H", 2, "square", -1],
      ["I/J", 2, "square", 1],
      ["K/L", 2, "square", -1],
      ["M/N", 2, "square", 1],
      ["O/P", 2, "square", -1],
    ];
    for (i = [0:1:3]) {
      if (depths[i * 2][1] != 0) {
        translate(
          [
            0,
            (slightly_larger_round_tile_diameter + 3.6) * i + 1,
            $inner_height - tile_thickness * depths[i * 2][1] - 0.5,
          ]
        ) {
          RenderItem(depths[i * 2], just_icon);
        }
      }
      if (depths[i * 2 + 1][1] != 0) {
        translate(
          [
            $inner_width - slightly_larger_round_tile_diameter,
            (slightly_larger_round_tile_diameter + 3.6) * i + 1,
            $inner_height - tile_thickness * depths[i * 2 + 1][1] - 0.5,
          ]
        ) {
          RenderItem(depths[i * 2 + 1], just_icon);
        }
      }
    }
  }

  MakeBoxWithSlidingLid(
    width=item_box_width, length=item_box_length, height=item_box_extras_height,
    lid_thickness=sliding_lid_thickness, last_child_positive=default_label_solid_background,
    material_colour="grey"
  ) {
    $inner_height = item_box_extras_height - lid_thickness * 2;
    $inner_width = item_box_width - wall_thickness * 2;
    // 12 craftable items (2× bag, 2× boot, 1× crossbow, 1× hammer, 2× sword, 2× teapot, 2× coins)
    MakeAllItems(just_icon=false);
    if (default_label_solid_background) {
      union() {
        MakeAllItems(just_icon=true);
      }
    }
  }
  if (generate_lid) {
    translate([item_box_width + 10, 0, 0]) {
      SlidingBoxLidWithLabel(
        width=item_box_width, length=item_box_length,
        text_str="Items", lid_thickness=sliding_lid_thickness,
        label_colour="blue", material_colour="grey", label_background_colour="grey"
      );
    }
  }
}

module BoxLayout() {
  cube([boxData("box", "width"), boxData("box", "length"), boxData("board", "thickness")]);
  cube([1, boxData("box", "length"), boxData("box", "height")]);
  translate([0, 0, boxData("board", "thickness")]) {
    CardBox(generate_lid=false);
    translate([card_box_width, 0, 0]) ItemsBoxBottom(generate_lid=false);
    translate([card_box_width, 0, item_box_height]) ItemsBoxMiddle(generate_lid=false);
    translate([card_box_width, 0, item_box_height + item_box_middle_height]) ItemsBoxWinter(generate_lid=false);
    translate([card_box_width, 0, item_box_height + item_box_middle_height + item_box_winter_height])
      ItemsBoxExtras(generate_lid=false);
    translate([0, card_box_length, 0]) MarquisBoxBottom(generate_lid=false);
    translate([marquis_box_width, card_box_length, 0]) AllianceBoxBottom(generate_lid=false);
    translate([marquis_box_width, card_box_length, alliance_box_height]) AllianceBoxTop(generate_lid=false);
    translate([0, card_box_length, marquis_box_height]) MarquisBoxTop(generate_lid=false);
    translate([0, card_box_length + marquis_box_length, 0]) ErieBoxBottom(generate_lid=false);
    translate([erie_box_width, card_box_length + erie_box_length, 0]) VagabondBox(generate_lid=false);
    translate([erie_box_width, card_box_length + erie_box_length, vagabond_box_height])
      VagabondBox(generate_lid=false);
    translate([0, card_box_length + marquis_box_length, erie_box_height]) ErieBoxTop(generate_lid=false);
    translate([erie_box_width, card_box_length + marquis_box_length + erie_box_length, 0])
      RiverfolkBoxBottom(generate_lid=false);
    translate([0, card_box_length + marquis_box_length, riverfolk_box_height])
      RiverfolkBoxTop(generate_lid=false);
    translate([0, card_box_length + marquis_box_length + erie_box_length, 0])
      LizardBoxBottom(generate_lid=false);
    translate([0, card_box_length + marquis_box_length + erie_box_length, lizard_box_height])
      LizardBoxTop(generate_lid=false);
  }
}

if (FROM_MAKE != 1) {
  //DiceBoxLid();
  ItemsBoxBottomLid();
}
