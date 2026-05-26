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

// Constant: STACKABLE_TYPE_NONE
// Description: No additional base added.
STACKABLE_TYPE_NONE = 0;

// Constant: STACKABLE_TYPE_INSIDE
// Description: Base is added to the inside of the box.
STACKABLE_TYPE_INSIDE = 1;

// Constant: STACKABLE_TYPE_OUTSIDE
// Description: Base is added to the outside of the box.
STACKABLE_TYPE_OUTSIDE = 2;

// Function: QuicksortExtraFloors(list)
// Description:
//   Sorts a list of extra floors by floor_height.
// Arguments:
//   list = list of extra floors
// Example:
//   QuicksortExtraFloors(list = [object(path=path, floor_height=5, top_height=0), object(path=path, floor_height=10, top_height=0)]);
function QuicksortExtraFloors(list) =
  !(len(list) > 0) ? []
  : let (
    pivot = list[floor(len(list) / 2)],
    lesser = [for (i = list) if (i.floor_height < pivot.floor_height) i],
    equal = [for (i = list) if (i.floor_height == pivot.floor_height) i],
    greater = [for (i = list) if (i.floor_height > pivot.floor_height) i]
  ) concat(QuicksortExtraFloors(lesser), equal, QuicksortExtraFloors(greater));

// Module: MakeBoxWithNoLid()
// Description:
//   Makes a box with no lid, useful for spacers and other things in games.
// Arguments:
//   size = [width, length, height] outside size of the box
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   material_colour = the material colour to use (default {{default_material_colour}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   make_finger_x = makes finger dip on the x axis (default width > length)
//   make_finger_y = makes finger dip on the y axis (default length > width)
//   finger_hole_size = size of the finger dip (default 20)
//   hollow = make the inside hollow (default false)
// Example:
//   MakeBoxWithNoLid(size = [100, 50, 20]);
// Example:
//   MakeBoxWithNoLid(size = [100, 50, 20], hollow=true);
module MakeBoxWithNoLid(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  make_finger_x = undef,
  make_finger_y = undef,
  material_colour = "grey",
  finger_hole_size = undef,
  hollow = false
) {
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width,length, height > 0 width=", width, " length=", length, " height=", height));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));

  calc_finger_hole_size = DefaultValue(finger_hole_size, min(20, min(min(length, width) / 4), height - floor_thickness + 1));
  calc_make_finger_x = make_finger_x == undef && make_finger_y == undef ? width > length : false;
  calc_make_finger_y = make_finger_y == undef && make_finger_x == undef ? length > width : false;
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
          cuboid(
            [width - (wall_thickness) * 2, length - (wall_thickness) * 2, height],
            rounding=wall_thickness / 4,
            anchor=BOTTOM + LEFT + FRONT
          );
        }
    }

    if (calc_make_finger_y) {
      translate([wall_thickness / 2 - 0.01, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(
            radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1), spin=90,
            depth_of_hole=wall_thickness + 0.03, rounding_edge=wall_thickness / 2
          );
      translate([width - wall_thickness / 2 + 0.01, length / 2, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(
            radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1), spin=90,
            depth_of_hole=wall_thickness + 0.03, rounding_edge=wall_thickness / 2
          );
    }

    if (calc_make_finger_x) {
      translate([width / 2, wall_thickness / 2 - 0.01, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(
            radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1),
            depth_of_hole=wall_thickness + 0.03, rounding_edge=wall_thickness / 2
          );
      translate([width / 2, length - wall_thickness / 2 + 0.01, height - calc_finger_hole_size + 0.01])
        color(material_colour)
          FingerHoleWall(
            radius=calc_finger_hole_size, height=min(calc_finger_hole_size, height - default_floor_thickness + 1),
            depth_of_hole=wall_thickness + 0.03, rounding_edge=wall_thickness / 2
          );
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
//   height = the height of the box
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   material_colour = the material colour to use (default {{default_material_colour}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   make_finger_x = makes finger dip on the x axis
//   make_finger_y = makes finger dip on the y axis
//   finger_hole_size = size of the finger dip (default 20)
//   offset_sweep_options = the options to use in the offset_sweep hollow box ({ offset = "round", check_valid: true, quality: 1, steps: 16}})
//   hollow = if the box should be hollow (default false)
//   stackable_lid_thickness = the thickness of the stackable part of the lid (default {{default_stackable_lid_thickness}})
//   stackable_fit_offset = the offset to use for stackable fit (default 0.1)
//   hollow_radius = the radius options for a hollow box (default object(top=default_wall_thickness/4, bottom=default_wall_thickness/4, radius=default_wall_thickness/2))
//   stackable = if the box should be stackable (default false)
//   extra_floors = optional set of extra paths and heights to carve out as [object(path=[], floor_height=N, top_height=N) (default [])]
// Example:
//   MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20);
// Example:
//   MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20, hollow=true);
// Example:
//   MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20, stackable=true);
module MakePathBoxWithNoLid(
  path,
  height,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  stackable_thickness = default_stackable_thickness,
  stackable_fit_offset = 0.1,
  hollow_radius = object(top=default_wall_thickness / 4, bottom=default_wall_thickness / 4, radius=default_wall_thickness / 2),
  make_finger_x = undef,
  make_finger_y = undef,
  material_colour = "grey",
  finger_hole_size = undef,
  offset_sweep_options = object(offset="round", check_valid=true, quality=1, steps=16),
  hollow = false,
  stackable = STACKABLE_TYPE_NONE,
  magnet = object(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0], height=0),
  extra_floors = [],
) {
  module StackableBoxInternal(bottom = false) {
    if (stackable == STACKABLE_TYPE_INSIDE) {
      difference() {
        color(material_colour)
          offset_sweep(
            round_corners(
              bottom ? inner_path_stackable_bottom_outside : inner_path_stackable,
              radius=stackable_thickness / 2
            ),
            height=stackable_thickness + (bottom ? stackable_fit_offset : 0),
            top=os_circle(
              wall_thickness / 4
            ),
            offset=offset_sweep_options.offset,
            check_valid=offset_sweep_options.check_valid,
            quality=offset_sweep_options.quality,
            steps=offset_sweep_options.steps
          );

        color(material_colour)
          translate([0, 0, -0.01]) {
            offset_sweep(
              round_corners(
                bottom ? inner_path_stackable_bottom_inside : inner_path,
                radius=stackable_thickness / 4
              ),
              height=stackable_thickness + 0.02 + (bottom ? stackable_fit_offset : 0),
              top=os_circle(-wall_thickness / 4),
              offset=offset_sweep_options.offset,
              check_valid=offset_sweep_options.check_valid,
              quality=offset_sweep_options.quality,
              steps=offset_sweep_options.steps
            );
          }
      }
    } else if (stackable == STACKABLE_TYPE_OUTSIDE) {
      difference() {
        color(material_colour)
          offset_sweep(
            calc_path,
            height=stackable_lid_thickness + (bottom ? stackable_fit_offset : 0),
            top=os_circle(
              wall_thickness / 4
            ),
            offset=offset_sweep_options.offset,
            check_valid=offset_sweep_options.check_valid,
            quality=offset_sweep_options.quality,
            steps=offset_sweep_options.steps
          );

        color(material_colour)
          translate([0, 0, -0.01]) {
            offset_sweep(
              round_corners(
                bottom ? inner_path_stackable_bottom_inside_inside : inner_path_stackable,
                radius=stackable_lid_thickness / 4
              ),
              height=stackable_lid_thickness + 0.02 + (bottom ? stackable_fit_offset : 0),
              top=os_circle(-wall_thickness / 4),
              offset=offset_sweep_options.offset,
              check_valid=offset_sweep_options.check_valid,
              quality=offset_sweep_options.quality,
              steps=offset_sweep_options.steps
            );
          }
      }
    }
  }

  assert(is_path(path, 2), "Path must be a 2d path");
  assert(len(path) >= 3, str("Path must be at least 3 elements long path_length=", len(path)));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));
  assert(height > 0, str("Need height > 0, height=", height));

  x_arr = [for (x = [0:len(path) - 1]) path[x][0]];
  y_arr = [for (x = [0:len(path) - 1]) path[x][1]];
  calc_length = max(y_arr) - min(y_arr);
  calc_width = max(x_arr) - min(x_arr);

  calc_finger_hole_size = DefaultValue(finger_hole_size, min(20, min(min(calc_length, calc_width) / 4), height - floor_thickness + 1));
  calc_finger_hole_height = min(calc_finger_hole_size, height - default_floor_thickness * 2 + 1);
  calc_make_finger_x = make_finger_x == undef && make_finger_y == undef ? calc_width > calc_length : false;
  calc_make_finger_y = make_finger_y == undef && make_finger_x == undef ? calc_length > calc_width : false;

  sorted_floors = QuicksortExtraFloors(extra_floors);
  region_path = make_region(path);
  region_extra_floors = [for (extra_floor = sorted_floors) make_region(extra_floor.path)];
  region_outside = union(concat([region_path, for (region = region_extra_floors) region]));

  // Make the outside path.
  calc_path = round_corners(region_outside[0], radius=wall_thickness);

  main_path = difference([path, for (extra_floor = sorted_floors) extra_floor.path]);

  inner_path = offset(main_path, r=-wall_thickness);
  inner_path_stackable = offset(main_path, r=-wall_thickness / 2);
  inner_path_stackable_bottom_outside = offset(main_path, r=-wall_thickness / 2 + stackable_fit_offset);
  inner_path_stackable_bottom_inside = offset(main_path, r=-wall_thickness - stackable_fit_offset);
  inner_path_stackable_bottom_inside_inside = offset(main_path, r=-wall_thickness / 2 - stackable_fit_offset);

  difference() {
    color(material_colour)
      union() {
        difference() {
          union() {
            offset_sweep(
              calc_path,
              height=stackable ? height - stackable_thickness : height,
              bottom=os_circle(stackable ? wall_thickness / 4 : wall_thickness / 2),
              top=os_circle(stackable ? wall_thickness / 8 : wall_thickness / 4),
              offset=offset_sweep_options.offset,
              check_valid=offset_sweep_options.check_valid,
              quality=offset_sweep_options.quality,
              steps=offset_sweep_options.steps
            );
            if (stackable) {
              translate([0, 0, height - stackable_thickness])
                StackableBoxInternal(bottom=false);
            }
          }

          for (extra_floor = sorted_floors) {
            if (extra_floor.floor_height > 0) {
              linear_extrude(height=extra_floor.floor_height)
                polygon(extra_floor.path);
            }
            if (extra_floor.top_height > 0) {
              translate([0, 0, height - extra_floor.top_height])
                linear_extrude(height=extra_floor.top_height)
                  polygon(extra_floor.path);
            }
          }
        }
        for (extra_floor = sorted_floors) {
          translate([0, 0, extra_floor.floor_height])
            offset_sweep(
              round_corners(extra_floor.path, radius=wall_thickness),
              height=stackable ? height - (extra_floor.floor_height) - stackable_thickness : height - (extra_floor.floor_height),
              bottom=os_circle(stackable ? wall_thickness / 4 : wall_thickness / 2),
              top=os_circle(stackable ? wall_thickness / 8 : wall_thickness / 4),
              offset=offset_sweep_options.offset,
              check_valid=offset_sweep_options.check_valid,
              quality=offset_sweep_options.quality,
              steps=offset_sweep_options.steps
            );
        }
      }
    if (hollow) {
      translate([0, 0, floor_thickness])
        color(material_colour)
          offset_sweep(
            round_corners(inner_path, radius=hollow_radius.radius),
            height=height - floor_thickness,
            bottom=os_circle(hollow_radius.bottom),
            top=stackable ? undef : os_circle(-hollow_radius.top),
            offset=offset_sweep_options.offset,
            check_valid=offset_sweep_options.check_valid,
            quality=offset_sweep_options.quality,
            steps=offset_sweep_options.steps
          );
      for (extra_floor = sorted_floors) {
        if (extra_floor.floor_height > 0) {
          translate([0, 0, extra_floor.floor_height + floor_thickness])
            offset_sweep(
              intersection(
                round_corners(
                  offset(
                    union(extra_floor.path, path),
                    r=-wall_thickness
                  ), radius=wall_thickness
                ),
                union(
                  [
                    offset(extra_floor.path, delta=wall_thickness),
                    inner_path,
                    // Join the paths with lower heght floors too.
                    for (path = sorted_floors) if (path.floor_height > extra_floor.floor_height) path.path,
                  ]
                )
              ),
              height=height - floor_thickness - extra_floor.floor_height,
              bottom=os_circle(hollow_radius.bottom),
              top=stackable ? undef : os_circle(-hollow_radius.top),
              offset=offset_sweep_options.offset,
              check_valid=offset_sweep_options.check_valid,
              quality=offset_sweep_options.quality,
              steps=offset_sweep_options.steps
            );
        }
      }
    }

    if (stackable) {
      translate([0, 0, -stackable_fit_offset])
        StackableBoxInternal(bottom=true);
    }

    calc_middle_path = offset(path, r=-wall_thickness / 2);

    // Finger hole bits.
    for (i = [0:1:len(calc_middle_path) - 2]) {
      segment = [calc_middle_path[i], calc_middle_path[i + 1]];
      FingerHoleWallSegment(
        path=[calc_middle_path[i], calc_middle_path[i + 1]],
        wall_thickness=wall_thickness,
        finger_hole_size=calc_finger_hole_size,
        finger_hole_height=calc_finger_hole_height,
        make_finger_y=calc_make_finger_y,
        make_finger_x=calc_make_finger_x,
        height=height
      );
    }
    FingerHoleWallSegment(
      path=[calc_middle_path[len(calc_middle_path) - 1], calc_middle_path[0]],
      wall_thickness=wall_thickness,
      finger_hole_size=calc_finger_hole_size,
      finger_hole_height=calc_finger_hole_height,
      height=height,
      make_finger_y=calc_make_finger_y,
      make_finger_x=calc_make_finger_x
    );

    // Make sure the children start from the bottom corner of the box.
    $inner_path = inner_path;
    $inner_width = calc_width;
    $inner_length = calc_length;
    $inner_height = height - floor_thickness;
    children();
  }
}

// Module: MakePolygonBoxWithNoLid()
// Description:
//   Makes a polygon box with no lid.
// Arguments:
//   size = [width, height] outside size of the box
//   sides = the number of sides for the polygon
//   stackable_lid_thickness = thickness of the stackable lid (default 2)
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   stackable = make the box stackable (default false)
//   make_finger_x = makes finger dip on the x axis (default false)
//   make_finger_y = makes finger dip on the y axis (default false)
//   material_colour = the material colour to use (default {{default_material_colour}})
//   finger_hole_size = size of the finger dip (default 20)
//   hollow = make the inside hollow (default false)
//   hollow_radius = radius of the hollow (default object(top=2, bottom=10, radius=2))
//   offset_sweep_options = options to pass to the offset_sweep module (default object(offset="round", check_valid=true, quality=1, steps=16))
//   magnet = magnet to use (default object(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0]))
// Example:
//   MakePolygonBoxWithNoLid(size = [100, 100, 20], sides = 6);
module MakePolygonBoxWithNoLid(
  size,
  sides,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  stackable_thickness = default_stackable_thickness,
  make_finger_x = undef,
  make_finger_y = undef,
  material_colour = "grey",
  finger_hole_size = undef,
  hollow = false,
  stackable = STACKABLE_TYPE_NONE,
  offset_sweep_options = object(offset="round", check_valid=true, quality=1, steps=16),
  hollow_radius = object(top=2, bottom=10, radius=2),
  magnet = object(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0])
) {
  width = size[0];
  height = size[1];
  assert(width > 0 && height > 0, str("Need width, height > 0 width=", width, " height=", height));
  assert(sides >= 3, str("sides must be >= 3, sides=", sides));

  calc_path = regular_ngon(n=sides, d=width);

  MakePathBoxWithNoLid(
    path=calc_path,
    height=height,
    offset_sweep_options=offset_sweep_options,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    stackable_thickness=stackable_thickness,
    make_finger_x=make_finger_x,
    make_finger_y=make_finger_y,
    material_colour=material_colour,
    finger_hole_size=finger_hole_size,
    hollow=hollow,
    stackable=stackable,
    hollow_radius=hollow_radius
  ) {
    // Handle the magnets here specifically.
    if (magnet.type != MAGNET_SLOT_TYPE_NONE) {
      calc_path_magnet = regular_ngon(n=sides, d=width - wall_thickness);

      for (i = [0:1:sides - 1]) {
        p1 = calc_path_magnet[i];
        p2 = calc_path_magnet[ (i + 1) % sides];
        mid = (p1 + p2) / 2;
        angle = atan2(p2[1] - p1[1], p2[0] - p1[0]) - 90;
        translate([mid[0], mid[1], 0])
          rotate([0, 0, angle])
            rotate([0, 90, 0])
              MagnetSlot(size=magnet.size, magnet_type=magnet.type, anchor=LEFT + BOTTOM, spin=180);
      }
    }

    if ($children > 0) children();
  }
}

// Description:
//    Makes a single segment for use in the no lid wall.  It will make the rounded
//    finger wall holes on the side of the box at the correct direction and length.
// Arguments:
//    path = the path to generate for (this should be one line segment)
//    finger_hole_size = the size of the finger hole
//    finger_hole_height = the height of the fingerhole
//    height = the height of the box
//    make_finger_x = makes finger dip on the x axis
//    make_finger_y = makes finger dip on the y axis
//    wall_thickness = thickness of the walls
// Example:
//    FingerHoleWallSegment([[0,0], [50,50]], finger_hole_size=5, finger_hole_height=4, height=7, make_finger_x=true, wall_thickness=2);
// Example:
//    FingerHoleWallSegment([[0,0], [50,50]], finger_hole_size=5, finger_hole_height=4, height=7, make_finger_y=true, wall_thickness=2);
module FingerHoleWallSegment(path, finger_hole_size, finger_hole_height, height, wall_thickness, make_finger_x = undef, make_finger_y = undef) {
  assert(is_path(path, 2), "Path must be a 2d path");
  assert(len(path) == 2, str("Path must be at least exactly 2 elements long path_length=", len(path)));
  assert(finger_hole_size > 0, str("Need finger hole size > 0, finger_hole_size=", finger_hole_size));
  assert(finger_hole_height > 0, str("Need finger hole height > 0, finger_hole_height=", finger_hole_height));
  assert(height > 0, str("Need height > 0, height=", height));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));

  split_length = path_length(path);
  normal = path_normals(path);
  angle = atan(normal[0][1] / normal[0][0]);

  if (split_length > finger_hole_size * 2.5 && (angle < 90 && angle > -90 ? make_finger_y : make_finger_x)) {
    pts = path_cut_points(
      path=path,
      cutdist=[split_length / 2]
    );
    translate([0, 0, height - finger_hole_height + 0.01])
      translate(pts[0][0])
        rotate(angle)
          FingerHoleWall(
            radius=finger_hole_size, height=finger_hole_height, spin=90, depth_of_hole=wall_thickness + 0.03,
            rounding_edge=wall_thickness / 2
          );
  }
}
