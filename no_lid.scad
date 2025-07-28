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

// LibFile: no_lid.scad
//    The boxex which have no lids with them.
//

// Module: MakeBoxWithNoLid()
// Description:
//   Makes a box with no lid, useful for spacers and other things in games.
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   material_colour = the material colour to use (default {{default_material_colour}})
//   size_spacing = the wiggle room in the lid generation (default {{m_piece_wiggle_room}})
//.  floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   make_finger_width = makes finger dip on the width (default false)
//   make_finger_length = makes finger dip on the length (default true)
//   finger_hole_size = size of the finger dip (default 20)
//   hollow = make the inside hollow (default false)
// Example:
//   MakeBoxWithNoLid(width=100, length=50, height=20);
// Example:
//   MakeBoxWithNoLid(width=100, length=50, height=20, hollow=true);
module MakeBoxWithNoLid(
  width,
  length,
  height,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  make_finger_width = undef,
  make_finger_length = undef,
  size_spacing = m_piece_wiggle_room,
  material_colour = "grey",
  finger_hole_size = undef,
  hollow = false
) {
  calc_finger_hole_size = DefaultValue(finger_hole_size, min(20, min(min(length, width) / 4), height - floor_thickness + 1));
  calc_make_finger_width = make_finger_width == undef && make_finger_length == undef ? width > length : false;
  calc_make_finger_length = make_finger_width == undef && make_finger_length == undef ? length > width : false;
  difference() {
    color(material_colour) cuboid(
        [width, length, height], anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );

    if (hollow) {
      translate([wall_thickness, wall_thickness, floor_thickness]) color(material_colour) {
          cube([width - (wall_thickness) * 2, length - (wall_thickness) * 2, height]);
        }
    }

    if (calc_make_finger_length) {
      translate([0, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(calc_finger_hole_size, calc_finger_hole_size, spin=90);
      translate([width - wall_thickness, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(calc_finger_hole_size, calc_finger_hole_size, spin=90);
    }

    if (calc_make_finger_width) {
      translate([width / 2, 0, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(calc_finger_hole_size, calc_finger_hole_size);
      translate([width / 2, length - wall_thickness, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(calc_finger_hole_size, calc_finger_hole_size);
    }

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}
