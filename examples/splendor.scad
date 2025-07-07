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

$fn = 128;

default_lid_thickness = 3;
default_label_font = "Impact";
default_lid_shape_width = 18;
default_lid_layout_width = 12;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_wall_thickness = 4;
inner_wall_thickness = 2;

default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;

splendor_disc_diameter = 44.5;
splendor_disc_thickness = 3.5;
splendor_disc_number = 40;
splendor_nobel_width = 61.5;
splendor_nobel_thickness = 2;
splendor_card_width = 65;
splendor_card_length = 89.5;

card_10_thickness = 6;
single_card_thickness = card_10_thickness / 10;

splendor_box_width = splendor_card_length + default_wall_thickness * 2 + 1;
splendor_box_length = default_wall_thickness * 4 + (splendor_disc_diameter + 1) * 3;
splendor_box_height = splendor_disc_thickness * ceil(splendor_disc_number / 6) + default_lid_thickness * 3 + splendor_nobel_thickness * 5 + (single_card_thickness * 45) + 1;

echo([splendor_box_width, splendor_box_length, splendor_box_height, single_card_thickness * 45]);

module SplendorBox() // `make` me
{
  MakeBoxWithSlidingLid(
    width=splendor_box_width,
    length=splendor_box_length,
    height=splendor_box_height,
    wall_thickness=4
  ) {
    // Nobels
    translate(
      [
        $inner_width / 2,
        splendor_card_width / 2,
        0,
      ]
    )
      cuboid(
        [
          splendor_nobel_width,
          splendor_nobel_width,
          splendor_box_height,
        ],
        rounding=2,
        edges=[FRONT + RIGHT, BACK + RIGHT],
        anchor=BOTTOM
      );

    translate(
      [
        $inner_width / 2,
        $inner_length - splendor_card_width / 2,
        0,
      ]
    )
      cuboid(
        [
          splendor_nobel_width,
          splendor_nobel_width,
          splendor_box_height,
        ],
        rounding=2,
        edges=[FRONT + RIGHT, BACK + RIGHT],
        anchor=BOTTOM
      );

    // cards
    translate(
      [
        $inner_width / 2,
        splendor_card_width / 2,
        splendor_nobel_thickness * 5 + 0.5,
      ]
    )
      cuboid(
        [
          splendor_card_length,
          splendor_card_width,
          splendor_box_height,
        ],
        rounding=1,
        edges=[FRONT + RIGHT, BACK + RIGHT],
        anchor=BOTTOM
      );
    translate(
      [
        $inner_width / 2,
        $inner_length - splendor_card_width / 2,
        splendor_nobel_thickness * 5 + 0.5,
      ]
    )
      cuboid(
        [
          splendor_card_length,
          splendor_card_width,
          splendor_box_height,
        ],
        rounding=1,
        edges=[FRONT + RIGHT, BACK + RIGHT],
        anchor=BOTTOM
      );

    // Top bit carved out.
    translate(
      [
        $inner_width / 2,
        $inner_length / 2,
        splendor_nobel_thickness * 5 + 0.5 + single_card_thickness * 45,
      ]
    )
      cuboid(
        [
          $inner_width,
          $inner_length,
          splendor_box_height,
        ],
        anchor=BOTTOM,
        rounding=1,
      );

    // Finger holes
    translate(
      [
        $inner_width / 2,
        0,
        -default_floor_thickness - 0.5,
      ]
    )
      FingerHoleBase(
        radius=15,
        height=splendor_box_height - default_floor_thickness
      );

    // Base cut out
    translate(
      [
        $inner_width / 2,
        0,
        0,
      ]
    )
      cuboid(
        [
          40,
          splendor_box_length * 2 - 20,
          splendor_box_height,
        ],
        rounding=15,
        anchor=BOTTOM
      );
  }
}

module SplendorBoxInside() // `make` me
{
  module TokenCylinder() {
    difference() {
      cyl(
        d=splendor_disc_diameter + inner_wall_thickness * 2,
        anchor=BOTTOM,
        h=splendor_disc_thickness * ceil(splendor_disc_number / 6) + 0.5
      );
      translate([0, 0, -0.5])
        cyl(
          d=splendor_disc_diameter,
          anchor=BOTTOM,
          h=splendor_disc_thickness * ceil(splendor_disc_number / 6) + 2
        );
    }
  }
  inner_length = splendor_box_length - default_wall_thickness * 2 - 1;
  inner_width = splendor_box_width - default_wall_thickness * 2 - 1;
  color(default_material_colour)
    difference() {
      union() {
        cuboid(
          [
            inner_length,
            inner_width,
            inner_wall_thickness,
          ], anchor=BOTTOM
        );

        // Cyls
        for (i = [0:2]) {
          translate(
            [
              inner_length / 2 - splendor_disc_diameter / 2 - inner_wall_thickness - i * (splendor_disc_diameter + inner_wall_thickness + 1),
              inner_width / 2 - splendor_disc_diameter / 2 - inner_wall_thickness / 2 + 0.6,
              default_lid_thickness,
            ]
          ) {
            if (i == 2) {
              translate([0, 0, -0.01])
                cyl(
                  d=splendor_disc_diameter  + inner_wall_thickness * 2 - 1,
                  anchor=BOTTOM,
                  h=splendor_disc_thickness*2
                );
            }
            TokenCylinder();
          }
          translate(
            [
              inner_length / 2 - splendor_disc_diameter / 2 - inner_wall_thickness - i * (splendor_disc_diameter + inner_wall_thickness + 1),
              -inner_width / 2 + splendor_disc_diameter / 2 + inner_wall_thickness / 2 - 0.6,
              default_lid_thickness,
            ]
          ) {
            TokenCylinder();
          }
        }
      }
      // End cutoff.
      translate([inner_length / 2, 0, 0]) cuboid(
          [
            inner_width,
            inner_width + 1,
            splendor_box_height,
          ], anchor=BOTTOM + LEFT
        );
      translate([-inner_length / 2, 0, 0]) cuboid(
          [
            inner_width,
            inner_width + 1,
            splendor_box_height,
          ], anchor=BOTTOM + RIGHT
        ); 

      // Edge cutoffs.
      translate(
        [
          0,
          inner_width / 2,
          inner_wall_thickness - 0.01,
        ]
      )
        cuboid(
          [
            splendor_box_length,
            10,
            splendor_box_height,
          ], anchor=BOTTOM
        );

      // Edge cutoffs.
      translate(
        [
          0,
          -inner_width / 2,
          inner_wall_thickness - 0.01,
        ]
      )
        cuboid(
          [
            inner_length,
            10,
            splendor_box_height,
          ], anchor=BOTTOM
        );

      // Middle cutoff
      translate(
        [
          0,
          0,
          default_floor_thickness,
        ]
      )
        cuboid(
          [
            inner_length,
            10,
            splendor_box_height,
          ], anchor=BOTTOM
        );
    }
}

module SplendorBoxLid() // `make` me
{
  SlidingBoxLidWithLabel(
    width=splendor_box_width,
    length=splendor_box_length,
    text_str="Splendor"
  );
}

if (FROM_MAKE != 1) {
  SplendorBoxInside();
}
