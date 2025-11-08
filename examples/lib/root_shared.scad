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

box_data = object(
  box=object(
    length=278, width=214, height=67, length=278
  ),
  board=object(thickness=28),
  marquis=object(length=22, width=26),
  erie=object(length=22, width=18),
  alliance=object(length=19.5, width=19),
  lizard=object(length=20, width=18),
  riverfolk=object(length=20, width=16),
  winter=object(width=29.5, length=15.5),
  token=object(thickness=9),
  vagabond=object(length=22, width=21)
);

square_tile_size = 18.5;
round_tile_diameter = 20;
slightly_larger_round_tile_diameter = 21;
larger_square_tile_ = 19;
tile_thickness = 2;

riverfolk_glass_diameter = 17;
riverfolk_glass_thickness = 9;

round_winter_thing_curve_width = 7.5;
round_winter_thing_cap_width = 12.5;
round_winter_thing_diameter = 50;
round_winter_thing_top_round = 10.5;

// Sleeved card size.
card_width = 69;
card_length = 92.5;
ten_cards_thickness = 6;
single_card_thickness = ten_cards_thickness / 10;

// Player token sizes
vagabond_ear_base_width = 14;
vagabond_ear_top_width = 9;
vagabond_ear_top_length = 4;
vagabond_ear_bottom_length = 6;
vagabond_base_width = 16;
vagagond_middle_length = 10;
vagabond_middle_width = 15;
vagabond_cheek_middle_length = 13;
vagabond_cheek_top_length = 16;
erie_base_width = 15;
erie_middle_width = 12;
erie_top_head = 3;
erie_beak_start_width = 14;
erie_beak_length = 5;
erie_beak_top_length = 15;
erie_beak_middle_length = 12;
erie_middle_length = 10;
erie_top_radius = 11;
maarquis_middle_width = 14;
marquis_middle_length = 10;
marquis_ear_width = 10;
marquis_ear_length = 3;
marquis_ear_flat_middle = 2;
marquis_ear_base_width = 13;
marquis_eye_bulge_top_length = 16;
marquis_bulge_radius = 5;
alliance_middle_width = 14;
alliance_middle_length = 9;
alliance_base_width = 16;
alliance_ear_diameter = 10;
lizard_base_width = 16;
lizard_middle_width = 13;
lizard_middle_length = 9;
lizard_middle_offset = 3;
lizard_head_bumps_length = 7;
lizard_nose_start_length = 15;
lizard_nose_length = 2.5;
lizard_nose_slope_start = 7;
lizard_nose_flat = 3;
lizard_bumps_width = 2;
riverfolk_middle_width = 15;
riverfolk_middle_length = 9;
riverfolk_checks_width = 15.5;
riverfolk_checks_length = 7;
riverfolk_ear_width = 5;
riverfolk_ear_dip = 1;
dice_width = 22;
dice_length = 28;

marquis_de_cat_num = 25;
erie_dynasty_num = 20;
woodland_aliance_num = 10;
vagabond_num = 1;
riverfolk_num = 15;
lizard_num = 25;
erie_card_num = 6;
vagabond_card_num = 15 /*quest*/ + 9 /*character*/;
overview_example_cards_num = 5;
duchy_card_num = 9;
marquis_wood_token_num = 8;
marquis_building_token_num = 6;
erie_roost_building_num = 7;
woodland_aliance_sympathy_num = 10;
woodland_alliance_base_num = 3;
vagabond_relationship_num_each = 6; // 3 base base, riverfolk: +3base, +6 for expansion

ruin_loot_num = 4;
starting_loot_num = 7;
craftable_items_num = 7;
craftable_items_per_type = [2, 2, 1, 1, 2, 2, 2];

clearing_board_marker_per_type_num = 4;

shared_cards_num = 54;

dice_num = 2;

module CylBothWidth(width_offset, len_offset, height, r = 1) {
  translate([width_offset - r, len_offset, 0]) cyl(r=r, h=height);
  translate([-width_offset + r, len_offset, 0]) cyl(r=r, h=height);
}

module VagabondCharacter(height) {
  module Ear() {
    hull() {
      translate(
        [
          vagabond_ear_base_width / 2 - 1,
          box_data.vagabond.length / 2 - vagabond_cheek_top_length - 1,
          0,
        ]
      ) cyl(r=1, h=height);
      translate([vagabond_ear_top_width / 2 - 1, -box_data.vagabond.length / 2 + 1, 0])
        cyl(r=1, h=height);
      translate([0, -box_data.vagabond.length / 2 + vagabond_ear_top_length + 1, 0])
        cyl(r=1, h=height);
    }
  }
  union() {
    // bottom
    hull() {
      CylBothWidth(vagabond_base_width / 2 - 1, box_data.vagabond.length / 2 - 1, height);
      CylBothWidth(
        vagabond_middle_width / 2 - 1, box_data.vagabond.length / 2 - vagagond_middle_length - 1,
        height
      );
    }
    // middle cheeks.
    hull() {
      CylBothWidth(
        vagabond_middle_width / 2 - 1, box_data.vagabond.length / 2 - vagagond_middle_length - 1,
        height
      );
      CylBothWidth(
        box_data.vagabond.width / 2 - 1,
        box_data.vagabond.length / 2 - vagabond_cheek_middle_length - 1, height
      );
      CylBothWidth(
        vagabond_ear_base_width / 2, box_data.vagabond.length / 2 - vagabond_cheek_top_length - 1,
        height
      );
      translate([0, -box_data.vagabond.length / 2 + vagabond_ear_top_length + 1, 0])
        cyl(r=1, h=height);
    }
    // Ears.
    Ear();
    mirror([1, 0, 0]) Ear();
  }
}

module MarquisCharacter(height) {
  module Ear() {
    hull() {
      translate(
        [marquis_ear_flat_middle / 2 + 0.25, -box_data.marquis.length / 2 + marquis_ear_length + 0.5, 0]
      )
        cyl(r=0.25, h=height);
      translate([marquis_ear_width / 2 - 1, -box_data.marquis.length / 2 + 1, 0]) cyl(r=1, h=height);
      translate(
        [marquis_ear_base_width / 2 - 1, box_data.marquis.length / 2 - marquis_eye_bulge_top_length, 0]
      )
        cyl(r=1, h=height);
    }
  }
  union() {
    // Base
    hull() {
      CylBothWidth(
        width_offset=box_data.marquis.width / 2,
        len_offset=box_data.marquis.length / 2 - 1, height=height
      );
      CylBothWidth(
        width_offset=maarquis_middle_width / 2,
        len_offset=box_data.marquis.length / 2 - marquis_middle_length, height=height
      );
    }
    // Top
    hull() {
      CylBothWidth(
        width_offset=marquis_ear_base_width / 2,
        len_offset=box_data.marquis.length / 2 - marquis_eye_bulge_top_length, height=height
      );
      CylBothWidth(
        width_offset=maarquis_middle_width / 2,
        len_offset=box_data.marquis.length / 2 - marquis_middle_length, height=height
      );
      CylBothWidth(
        width_offset=marquis_ear_flat_middle / 2 + 2,
        len_offset=-box_data.marquis.length / 2 + marquis_ear_length, height=height
      );
    }
    // Ears
    Ear();
    mirror([1, 0, 0]) Ear();
    translate(
      [
        box_data.marquis.width / 2,
        box_data.marquis.length / 2 - (marquis_eye_bulge_top_length + marquis_middle_length) / 2,
        0,
      ]
    ) cyl(r=marquis_bulge_radius, anchor=RIGHT, h=height);
    translate(
      [
        -(box_data.marquis.width) / 2,
        box_data.marquis.length / 2 - (marquis_eye_bulge_top_length + marquis_middle_length) / 2,
        0,
      ]
    ) cyl(r=marquis_bulge_radius, anchor=LEFT, h=height);
  }
}

module ErieCharacter(height) {
  union() {
    // Base
    translate([(box_data.erie.width - erie_base_width) / 2, 0, 0]) hull() {
        CylBothWidth(
          width_offset=erie_base_width / 2, len_offset=box_data.erie.length / 2 - 1,
          height=height
        );
        CylBothWidth(
          width_offset=erie_middle_width / 2,
          len_offset=box_data.erie.length / 2 - erie_middle_length, height=height
        );
      }
    // Top
    hull() {
      CylBothWidth(
        width_offset=erie_middle_width / 2,
        len_offset=box_data.erie.length / 2 - erie_middle_length, height=height
      );
      CylBothWidth(
        width_offset=erie_middle_width / 2,
        len_offset=box_data.erie.length / 2 - erie_beak_top_length, height=height
      );
      translate([box_data.erie.width / 2 - 1 - erie_top_head, -box_data.erie.length / 2 + 1, 0])
        cyl(r=1, h=height);
    }
    // Beak.
    hull() {
      translate(
        [-box_data.erie.width / 2 + 1, box_data.erie.length / 2 - erie_beak_middle_length - 1, 0]
      )
        cyl(r=1, h=height);
      translate([-erie_middle_width / 2 + 1, box_data.erie.length / 2 - erie_middle_length, 0])
        cyl(r=1, h=height);
      translate([-erie_middle_width / 2 + 1, box_data.erie.length / 2 - erie_beak_top_length, 0])
        cyl(r=1, h=height);
    }
    translate([box_data.erie.width / 2 - 1 - erie_top_head, -box_data.erie.length / 2, 0])
      intersection() {
        cyl(r=erie_top_radius, h=height, anchor=FRONT);
        cuboid([erie_top_radius, erie_top_radius, height], anchor=FRONT + RIGHT);
      }
  }
}

module AllianceCharacter(height) {
  union() {
    // Base
    hull() {
      CylBothWidth(
        width_offset=alliance_base_width / 2, len_offset=box_data.alliance.length / 2 - 1,
        height=height
      );
      CylBothWidth(
        width_offset=alliance_middle_width / 2,
        len_offset=box_data.alliance.length / 2 - alliance_middle_length, height=height
      );
    }
    hull() {
      translate(
        [box_data.alliance.width / 2, -box_data.alliance.length / 2 + alliance_ear_diameter / 2, 0]
      )
        cyl(d=alliance_ear_diameter, h=height, anchor=RIGHT);
      translate([0, box_data.alliance.length / 2 - alliance_middle_length, 0]) cyl(r=1, h=height);
      translate([alliance_middle_width / 2 - 1, box_data.alliance.length / 2 - alliance_middle_length, 0])
        cyl(r=1, h=height);
    }
    hull() {
      translate(
        [
          -box_data.alliance.width / 2,
          -box_data.alliance.length / 2 + alliance_ear_diameter / 2,
          0,
        ]
      ) cyl(d=alliance_ear_diameter, h=height, anchor=LEFT);
      translate([0, box_data.alliance.length / 2 - alliance_middle_length, 0]) cyl(r=1, h=height);
      translate([-alliance_middle_width / 2 + 1, box_data.alliance.length / 2 - alliance_middle_length, 0])
        cyl(r=1, h=height);
    }
  }
}

module RiverfolkCharacter(height) {
  // Base
  hull() {
    CylBothWidth(
      width_offset=box_data.riverfolk.width / 2,
      len_offset=box_data.riverfolk.length / 2 - 1, height=height
    );
    CylBothWidth(
      width_offset=riverfolk_middle_width / 2,
      len_offset=box_data.riverfolk.length / 2 - riverfolk_middle_length, height=height
    );
  }
  translate([0, -box_data.riverfolk.length / 2, 0])
    cyl(d=box_data.riverfolk.width, h=height, anchor=FRONT);
  translate([box_data.riverfolk.width / 2 - riverfolk_ear_width / 2, -box_data.riverfolk.length / 2, 0])
    cyl(d=riverfolk_ear_width, h=height, anchor=FRONT);
  translate([-box_data.riverfolk.width / 2 + riverfolk_ear_width / 2, -box_data.riverfolk.length / 2, 0])
    cyl(d=riverfolk_ear_width, h=height, anchor=FRONT);
}

module LizardCharacter(height) {
  // Base
  hull() {
    CylBothWidth(
      width_offset=lizard_base_width / 2, len_offset=box_data.lizard.length / 2 - 1,
      height=height
    );
    CylBothWidth(
      width_offset=lizard_middle_width / 2,
      len_offset=box_data.lizard.length / 2 - lizard_middle_length, height=height
    );
  }
  // Nose
  hull() {
    translate([box_data.lizard.width / 2 - 1 - lizard_bumps_width, -box_data.lizard.length / 2 + 1, 0])
      cyl(r=1, h=height);
    translate([lizard_middle_width / 2 - 1, box_data.lizard.length / 2 - lizard_middle_length, 0])
      cyl(r=1, h=height);
    translate([-lizard_middle_width / 2 + 1, box_data.lizard.length / 2 - lizard_middle_length, 0])
      cyl(r=1, h=height);
    translate(
      [-box_data.lizard.width / 2 + 1, box_data.lizard.length / 2 - lizard_nose_start_length - 1, 0]
    )
      cyl(r=1, h=height);
    translate(
      [
        -box_data.lizard.width / 2 + 1,
        box_data.lizard.length / 2 - lizard_nose_start_length - lizard_nose_flat + 1,
        0,
      ]
    ) cyl(r=1, h=height);
    translate([box_data.lizard.width / 2 - lizard_nose_slope_start, -box_data.lizard.length / 2 + 1, 0])
      cyl(r=1, h=height);
  }
  // bumps
  translate([box_data.lizard.width / 2, -box_data.lizard.length / 2, 0])
    cuboid(
      [lizard_bumps_width + 1, lizard_head_bumps_length, height], anchor=FRONT + RIGHT, rounding=1,
      edges=[FRONT + RIGHT, BACK + RIGHT]
    );
}

module WinterToken(height) {
  translate([-box_data.winter.length / 2, 0, 0]) {
    union() {
      translate([box_data.winter.length - round_winter_thing_cap_width / 2, 0, 0])
        cyl(d=round_winter_thing_cap_width, h=height, anchor=BOTTOM);
      difference() {
        intersection() {
          translate([-round_winter_thing_diameter / 2 + round_winter_thing_top_round, 0, 0]) difference() {
              cyl(d=round_winter_thing_diameter, h=height, anchor=BOTTOM);
              translate([0, 0, -0.5])
                cyl(
                  d=round_winter_thing_diameter - round_winter_thing_curve_width * 2, h=height + 2,
                  anchor=BOTTOM
                );
            }
          cuboid([box_data.winter.length, box_data.winter.width, height], anchor=LEFT + BOTTOM);
        }
        translate(
          [
            round_winter_thing_curve_width * 3 / 7 + 0.25,
            box_data.winter.width - round_winter_thing_curve_width * 2.5 - 0.5,
            -0.5,
          ]
        ) rotate([0, 0, 30]) difference() {
              cuboid(
                [round_winter_thing_curve_width + 2, round_winter_thing_curve_width, height + 1],
                anchor=FRONT + BOTTOM
              );
              cyl(d=round_winter_thing_curve_width, h=height + 1, $fn=64, anchor=BOTTOM);
            }

        translate(
          [
            round_winter_thing_curve_width * 3 / 7 + 0.25,
            -box_data.winter.width + round_winter_thing_curve_width * 2.5 + 0.5,
            -0.5,
          ]
        ) rotate([0, 0, 150]) difference() {
              cuboid(
                [round_winter_thing_curve_width + 2, round_winter_thing_curve_width, height + 1],
                anchor=FRONT + BOTTOM
              );
              cyl(d=round_winter_thing_curve_width, h=height + 1, $fn=64, anchor=BOTTOM);
            }
      }
    }
  }
}

module MarquisEyes2d() {
  translate([-6, 0, 0]) HalfEye2d(60);
  translate([6, 0, 0]) mirror([1, 0]) HalfEye2d(60);
  // Nose.
  translate([0, -4, 0]) {
    circle(d=3);
    translate([0, -2]) {
      rect([1, 3]);
      translate([-3, -1.5]) ring(r1=2.5, r2=3, angle=[360, 180], n=32);
      translate([3, -1.5]) mirror([1, 0]) ring(r1=2.5, r2=3, angle=[360, 180], n=32);
    }
  }
}

module AllianceEyes2d() {
  translate([-6, 0, 0]) SideEye2d(0);
  translate([6, 0, 0]) SideEye2d(0);
}

module ErieEyes2d() {
  translate([-6, 6.5]) rotate(30) rect([10, 1.5]);
  translate([-6, 0, 0]) SideEye2d(270);
}

module VagabondEyes2d() {
  module OneEye(angle) {
    translate([-6, 0, 0]) SideEye2d(angle);
    {
      translate([-1.5, -2]) rotate(65) difference() {
            translate([0, -5]) difference() {
                round2d(1) difference() {

                    rect([10, 20]);
                    translate([0, -13]) circle(d=20);
                  }
                translate([0, 10]) circle(d=10);
              }
          }
    }
  }
  translate([12, 0, 0]) OneEye(180);
  translate([-12, 0, 0]) mirror([1, 0]) OneEye(0);
}

module RiverfolkEyes2d() {
  translate([6, 0, 0]) SideEye2d(90);
  translate([-6, 0, 0]) SideEye2d(90);
  translate([0, -4, 0]) {
    translate([1, 0.6]) rotate(30) rect([4, 1]);
    translate([-1, 0.6]) rotate(150) rect([4, 1]);
    circle(d=3);
  }
}

module LizardEyes2d() {
  translate([6, 0, 0]) HalfEye2d(270);
  module BezSection(len) {
    bez = [[0, len / 2], [-len, 0], [-len * 2, -len], [-len * 3, len / 2]];
    path = bezier_points(bez, [0:0.05:1]);
    stroke(path);
  }
  translate([-2, 0.5]) {
    BezSection(len=2);
    translate([-6, 0]) BezSection(len=2);
    translate([-12, 0]) BezSection(len=2);
  }
}

module Keep2d(size) {
  union() {
    tower_width = size / 4;
    tower_length = size / 4;
    roof_overhang = size / 16;
    roof_height = size / 4;
    for (i = [0:1:3]) {
      translate([(i % 2) * 1, -size / 2 + tower_width * i]) {
        translate([0, roof_overhang * 2]) {
          rect([tower_width, tower_length - roof_overhang]);
          polygon(
            [
              [-tower_width / 2, tower_length / 2],
              [-tower_width / 2 - roof_height, 0],
              [-tower_width / 2, -tower_length / 2],
            ]
          );
        }
      }
    }
    translate([size / 16, -size / 2 + tower_width]) rect([tower_width / 2, tower_length]);
    translate([size / 8, -size / 2 + tower_width * 2]) rect([tower_width / 2, tower_length]);
    translate([size / 16, -size / 2 + tower_width * 3]) rect([tower_width / 2, tower_length]);
    translate([size / 2 - tower_width, -tower_width * 3 / 4]) difference() {
        rect([tower_width, tower_length]);
        circle(d=tower_width * 5 / 8, $fn=32);
        translate([tower_width / 2, 0]) rect([tower_width, tower_length * 5 / 8]);
      }
  }
}

module ErieTree2d(size) {
  hull() {
    translate([size / 2 - 1, -size / 2 + 1]) circle(r=1);
    translate([0, -2 * size / 12]) circle(r=0.25);
  }

  translate([0, size * 2 / 6 / 2]) rotate(180) Leaf2d(size * 4 / 6);
  translate([-size * 3 / 6 / 2, size * 1 / 6 / 2]) rotate(225) Leaf2d(size * 4 / 6);
  translate([-size * 3 / 6 / 2, -size * 7 / 12 / 2]) rotate(300) Leaf2d(size * 13 / 24);
}

module AllianceCamp2d(size) {
  difference() {
    rect([size, size]);
    top_edge = size / 15;
    for (i = [0:2:14]) {
      translate([size / 2 - top_edge / 2 + 0.01, size / 2 - top_edge / 2 - top_edge * i])
        rect([top_edge, top_edge]);
    }
  }
}

module CapBoxLidWithEyes(
  width,
  length,
  height,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  material_colour = undef
) {
  CapBoxLid(
    width=width, length=length, height=height, wall_thickness=wall_thickness,
    lid_thickness=lid_thickness, size_spacing=m_piece_wiggle_room, material_colour=material_colour
  ) {
    translate([10, 10, 0])
      LidMeshBasic(
        width=width, length=length, lid_thickness=default_lid_thickness, boundary=10,
        layout_width=default_lid_layout_width, aspect_ratio=default_lid_aspect_ratio,
        material_colour=material_colour
      ) {
        color(material_colour) ShapeByType(
            shape_type=default_lid_shape_type, shape_width=default_lid_shape_width,
            shape_thickness=default_lid_shape_thickness, shape_aspect_ratio=default_lid_aspect_ratio
          );
      }
    translate([width / 2, length / 2, 0]) children();
  }
}

module SlidingLidWithEyes(
  width,
  length,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  material_colour = undef
) {
  SlidingLid(
    width=width, length=length, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    size_spacing=m_piece_wiggle_room, lid_on_length=true, material_colour=material_colour
  ) {
    translate([10, 10, 0])
      LidMeshBasic(
        width=width, length=length, lid_thickness=default_lid_thickness, boundary=10,
        layout_width=default_lid_layout_width, aspect_ratio=default_lid_aspect_ratio,
        material_colour=material_colour
      ) {
        color(material_colour) ShapeByType(
            shape_type=default_lid_shape_type, shape_width=default_lid_shape_width,
            shape_thickness=default_lid_shape_thickness, shape_aspect_ratio=default_lid_aspect_ratio
          );
      }

    // Fingernail pull
    intersection() {
      color(material_colour) cube([width - 10, length - 10, lid_thickness]);
      translate([(width) - 8 - 3, length / 2, 0]) rotate([0, 0, -90]) color(material_colour)
            SlidingLidFingernail(lid_thickness);
    }

    translate([width / 2, length / 2, 0]) children();
  }
}

module Rabbit2d(size) {
  module OneEar() {
    hull() {
      translate([-size / 2 + size / 6, size / 2 - size / 6]) circle(size / 6);
      translate([size / 4, size / 4]) circle(size / 6);
    }
  }
  resize([size, size / 1.5]) translate([-size / 4, 0]) difference() {
        union() {
          OneEar();
          mirror([0, 1]) OneEar();
          translate([size / 2, 0]) circle(size / 2);
        }
        translate([size / 3, size / 6]) circle(size / 12);
        translate([size / 3, -size / 6]) circle(size / 12);
      }
}

module Mouse2d(size) {
  ear_size = size * 4 / 17;
  difference() {
    union() {

      translate([-size / 2 + size / 5, size / 2 - ear_size]) circle(ear_size);
      translate([-size / 2 + size / 5, -size / 2 + ear_size]) circle(ear_size);
      translate([size / 2 - size * 3 / 8, 0]) circle(size * 3 / 8);
    }
    translate([size / 12, size / 6]) circle(size / 12);
    translate([size / 12, -size / 6]) circle(size / 12);
  }
}

module Fox2d(size) {
  module OneEar() {
    egg(size / 2, size / 30, size * 7 / 40, size);
  }
  difference() {
    union() {
      // Base of head.
      polygon(
        [
          [size / 2, 0],
          [0, size / 2],
          [size / 24, size / 2 - size / 6],
          [-size / 12, size / 2 - size / 24],
          [-size / 24, size / 2 - size / 12 * 3],

          [-size / 24, -size / 2 + size / 12 * 3],
          [-size / 12, -size / 2 + size / 24],
          [size / 24, -size / 2 + size / 6],
          [0, -size / 2],
        ]
      );
      translate([-size / 8, size / 6]) OneEar();
      translate([-size / 8, -size / 6]) OneEar();
    }
    translate([size / 6, size / 10]) circle(size / 24);
    translate([size / 6, -size / 10]) circle(size / 24);
  }
}
