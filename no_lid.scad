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

// FileSummary: Boxes with no lids.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Module: MakeBoxWithNoLid()
// Description:
//   Makes a box with no lid, useful for spacers and other things in games.
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   material_colour = the material colour to use (default {{default_material_colour}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
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
  material_colour = "grey",
  finger_hole_size = undef,
  hollow = false
) {
  assert(width > 0 && length > 0 && height > 0, str("Need width,length, height > 0 width=", width, " length=", length, " height=", height));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));

  calc_finger_hole_size = DefaultValue(finger_hole_size, min(20, min(min(length, width) / 4), height - floor_thickness + 1));
  calc_make_finger_width = make_finger_width == undef && make_finger_length == undef ? width > length : false;
  calc_make_finger_length = make_finger_width == undef && make_finger_length == undef ? length > width : false;
  difference() {
    color(material_colour) diff() {
        cuboid(
          [width, length, height], anchor=BOTTOM + FRONT + LEFT,
          rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
        ) {
          face_profile(TOP, r=wall_thickness / 2)
            mask2d_roundover(wall_thickness / 2);
          face_profile(BOTTOM, r=wall_thickness / 2)
            mask2d_roundover(wall_thickness / 2);
          corner_profile("ALL", r=wall_thickness / 2) mask2d_roundover(wall_thickness / 2);
        }
      }

    if (hollow) {
      translate([wall_thickness, wall_thickness, floor_thickness]) color(material_colour) {
          cube([width - (wall_thickness) * 2, length - (wall_thickness) * 2, height]);
        }
    }

    if (calc_make_finger_length) {
      translate([0, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1), spin=90);
      translate([width - wall_thickness, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1), spin=90);
    }

    if (calc_make_finger_width) {
      translate([width / 2, 0, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1));
      translate([width / 2, length - wall_thickness, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1));
    }

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

// Module: MakePathBoxWithNoLid()
// Description:
//   Makes a box with no lid using a polygon layout, useful for spacers and other things in games.  Be
//   aware that you might get errors generating and you will need to use $fn to reduce the number of points
//   to make the corners work
// Arguments:
//   path = the path to generate for (this should be one line segment)
//   height = the height of the box (outside height)
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   material_colour = the material colour to use (default {{default_material_colour}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   make_finger_width = makes finger dip on the width (default false)
//   make_finger_length = makes finger dip on the length (default true)
//   finger_hole_size = size of the finger dip (default 20)
//   hollow = make the inside hollow (default false)
// Example:
//   MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20);
// Example:
//   MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20, hollow=true);
module MakePathBoxWithNoLid(
  path,
  height,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  make_finger_width = undef,
  make_finger_length = undef,
  material_colour = "grey",
  finger_hole_size = undef,
  hollow = false
) {
  assert(is_path(path, 2), "Path must be a 2d path");
  assert(len(path) >= 3, str("Path must be at least 3 elements long path_length=", len(path)));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));

  inner_path = offset(path, r=-wall_thickness);

  x_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][0]];
  y_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][1]];
  calc_length = max(y_arr) - min(y_arr);
  calc_width = max(x_arr) - min(x_arr);

  calc_finger_hole_size = DefaultValue(finger_hole_size, min(20, min(min(calc_length, calc_width) / 4), height - floor_thickness + 1));
  calc_finger_hole_height = min(calc_finger_hole_size, height - default_floor_thickness * 2 + 1);
  calc_make_finger_width = make_finger_width == undef && make_finger_length == undef ? calc_width > calc_length : false;
  calc_make_finger_length = make_finger_width == undef && make_finger_length == undef ? calc_length > calc_width : false;

  calc_path = round_corners(path, radius=wall_thickness);

  difference() {
    color(material_colour)
      offset_sweep(calc_path, height=height, bottom=os_circle(wall_thickness / 2), top=os_circle(wall_thickness / 4));
    if (hollow) {
      translate([0, 0, floor_thickness])
        color(material_colour)
          offset_sweep(round_corners(inner_path, radius=wall_thickness / 2), height=height, bottom=os_circle(wall_thickness / 4), top=os_circle(wall_thickness / 4));
    }

    // Finger hole bits.
    for (i = [0:1:len(calc_path) - 2]) {
      segment = [calc_path[i], calc_path[i + 1]];
      FingerHoleWallSegment(
        path=[calc_path[i], calc_path[i + 1]],
        finger_hole_size=calc_finger_hole_size,
        finger_hole_height=calc_finger_hole_height,
        wall_thickness=wall_thickness,
        make_finger_length=calc_make_finger_length,
        make_finger_width=calc_make_finger_width,
        height=height
      );
    }
    FingerHoleWallSegment(
      path=[calc_path[len(calc_path) - 1], calc_path[0]],
      finger_hole_size=calc_finger_hole_size,
      finger_hole_height=calc_finger_hole_height,
      wall_thickness=wall_thickness,
      height=height,
      make_finger_length=calc_make_finger_length,
      make_finger_width=calc_make_finger_width
    );

    // Make sure the children start from the bottom corner of the box.
    $inner_path = inner_path;
    $inner_width = calc_width;
    $inner_length = calc_length;
    $inner_height = height - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

// Module: FingerHoleWallSegment()
// Description:
//    Makes a single segment for use in the no lid wall.  It will make the rounded
//    finger wall holes on the side of the box at the correct direction and length.
// Arguments:
//    path = the path to generate for (this should be one line segment)
//    finger_hole_size = the size of the finger hole
//    finger_hole_height = the height of the fingerhole
//    wall_thickness = the thickness of the walls
//    make_finger_width = makes finger dip on the width (default false)
//    make_finger_length = makes finger dip on the length (default true)
// Example:
//    FingerHoleWallSegment([[0,0], [50,50]], finger_hole_size=5, finger_hole_height=4, height=7, wall_thickness=2, make_finger_width=true);
// Example:
//    FingerHoleWallSegment([[0,0], [50,50]], finger_hole_size=5, finger_hole_height=4, height=7, wall_thickness=2, make_finger_length=true);
module FingerHoleWallSegment(path, finger_hole_size, finger_hole_height, wall_thickness, height, make_finger_width = undef, make_finger_length = undef) {
  assert(is_path(path, 2), "Path must be a 2d path");
  assert(len(path) == 2, str("Path must be at least exactly 2 elements long path_length=", len(path)));

  split_length = path_length(path);
  normal = path_normals(path);
  angle = atan(normal[0][1] / normal[0][0]);

  if (split_length > finger_hole_size * 2.5 && (angle < 90 && angle > -90 ? make_finger_length : make_finger_width)) {
    pts = path_cut_points(
      path=path,
      cutdist=[split_length / 2]
    );
    translate([0, 0, height - finger_hole_height + 0.01])
      translate(pts[0][0])
        rotate(angle)
          FingerHoleWall(radius=finger_hole_size, height=finger_hole_height, spin=90);
  }
}
