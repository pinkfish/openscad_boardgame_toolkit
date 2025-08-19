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

// LibFile: components.scad
//    This file has all the modules needed to generate varioius inserts
//    for board games.  It makes the generation of the inserts simpler by
//    creating a number of useful base modules for making boxes and lids
//    of various types specific to board game inserts.  Specifically it
//    makes tabbed lids and sliding lids easily.
//

// FileSummary: Various modules to generate board game inserts.
// FileGroup: Basics

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Components
//   Building blocks to make all the rest of the items from.  This has all the basic parts of the board game
//   toolkit for making polygons and laying them out.

// Module: RoundedBoxOnLength()
// Usage:
//   RoundedBoxOnLength(100, 50, 10, 5);
// Description:
//   Creates a rounded box for use in the board game insert with a nice radius on two sides (length side).
// Arguments:
//   width = width of the cube
//   length = of the cube
//   height = of the cube
//   radius = radius of the curve on the edges
// Topics: Recess
// Example:
//   RoundedBoxOnLength(30, 20, 10, 7);
module RoundedBoxOnLength(width, length, height, radius) {
  hull() {
    difference() {
      translate([width / 2, length / 2, radius]) hull() {
          ydistribute(l=length - radius * 2) {
            xcyl(l=width, r=radius);
            xcyl(l=width, r=radius);
          }
        }
      translate([-0.5, -0.5, radius]) cube([width + 1, length + 1, radius + 1]);
    }

    translate([0, 0, height - 1]) cube([width, length, 1]);
  }
}

// Module: RoundedBoxAllSides()
// Usage:
//   RoundedBoxAllSides(30,20,10,5);
// Description:
//   Creates a rounded box with all the sides rounded.
// Arguments:
//   width = width of the cube
//   length = of the cube
//   height = of the cube
//   radius = radius of the curve on the edges
// Topics: Recess
// Example:
//   RoundedBoxAllSides(30, 20, 10, 7);
module RoundedBoxAllSides(width, length, height, radius) {
  hull() {
    difference() {
      hull() {
        translate([radius, radius, radius]) sphere(radius);

        translate([width - radius, radius, radius]) sphere(radius);

        translate([radius, length - radius, radius]) sphere(radius);

        translate([width - radius, length - radius, radius]) sphere(radius);
      }
      translate([-0.5, -0.5, radius]) cube([width + 1, length + 1, radius + 1]);
    }

    translate([0, 0, height - 1]) cube([width, length, 1]);
  }
}

// Module: RoundedBoxGrid()
// Usage:
//   RoundedBoxGrid(20,20,10,5, rows=2, cols=1);
// Description:
//   Create a grid of rounded boxes, this is useful for inserting a number of containers inside a insert box.
// Arguments:
//   width = width of the space (total, inside will be divided by this)
//   length = of the space (total, inside will be divided by this)
//   height = of the space
//   radius = radius of the curve on the edges
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = number of mm between the spaces (default 2)
//   all_sides = round all the sides (default false)
// Topics: Recess, Grid
// Example:
//   RoundedBoxGrid(30, 20, 10, 7, rows=2, cols=1);
module RoundedBoxGrid(width, length, height, radius, rows, cols, spacing = 2, all_sides = false) {
  row_length = (width - spacing * (rows - 1)) / rows;
  col_length = (length - spacing * (cols - 1)) / cols;
  for (x = [0:rows - 1])
    for (y = [0:cols - 1])
      translate([x * (row_length + spacing), y * (col_length + spacing), 0]) {
        if (all_sides) {
          RoundedBoxAllSides(length=col_length, width=row_length, height=height, radius=radius);
        } else {
          RoundedBoxOnLength(length=col_length, width=row_length, height=height, radius=radius);
        }
      }
}

// Function: PolygonRadiusFromApothem()
// Description:
//   Find the radius of the polygon from apothem.
// Arguments:
//   apothem = apothem of the shape
//   shape_edges = the number of edges on the shape
function PolygonRadiusFromApothem(apothem, shape_edges) = apothem / cos(180 / shape_edges) / 2;

// Function: PolygonApothemFromRadius()
// Description:
//   Find the apothem of the polygon from radius.
// Arguments:
//   radius = radius of the shape
//   shape_edges = the number of edges on the shape
function PolygonApothemFromRadius(radius, shape_edges) = radius * cos(180 / shape_edges) * 2;

// Module: RegularPolygon()
// Usage:
//   RegularPolygon(10, 5, 6);
// Description:
//   Creates a regular polygon with specific height/width and number of edges.
// Arguments:
//   width = total width of the piece, this is equivilant to the apothem of a polygon * 2
//   height = how high to create the item
//   shape_edges =  number of edges for the polygon
//   finger_holes = finger holes to put on the specific edges, from 0-shapeedges
//   finger_hole_height = height of the finger holes
//   finger_hole_radius = the radius of the finger holes
// Topics: Recess
// Example:
//   RegularPolygon(10, 5, shape_edges = 6);
// Example:
//   RegularPolygon(10, 5, shape_edges = 6, finger_holes = [0, 3]);
module RegularPolygon(width, height, shape_edges, finger_holes = [], finger_hole_height = 0, finger_hole_radius = undef, rounding = 0, radius = undef) {
  rotate_deg = ( (shape_edges % 2) == 1) ? 180 / shape_edges + 90 : (shape_edges == 4 ? 45 : 0);

  calc_radius = DefaultValue(radius, PolygonRadiusFromApothem(width, shape_edges));
  calc_width = DefaultValue(width, PolygonApothemFromRadius(calc_radius, shape_edges));

  side_length = width * tan(180 / shape_edges) / 2;

  calc_finger_hole_radius = DefaultValue(finger_hole_radius, side_length * 9 / 10);

  rotate([0, 0, rotate_deg]) linear_extrude(height=height) regular_ngon(n=shape_edges, or=calc_radius, rounding=rounding);
  degree = 360 / shape_edges;
  for (i = [0:1:len(finger_holes) - 1]) {
    x = calc_width / 2 * cos(degree * finger_holes[i] + rotate_deg + degree / 2);
    y = calc_width / 2 * sin(degree * finger_holes[i] + rotate_deg + degree / 2);
    translate([x, y, finger_hole_height]) {
      cyl(
        r=calc_finger_hole_radius, h=max(height + calc_finger_hole_radius, calc_finger_hole_radius * 2),
        rounding=calc_finger_hole_radius, anchor=BOTTOM,
      );
    }
  }
  children();
}

// Module: CircleWithIndents()
// Description:
//    Makes a nice cylinder with finger holes bits at the spexific angles.
// Arguments:
//    radius = radius of the circle
//    height = of the cylinder
//    finger_holes = finger holes at the specified degrees.
//    finger_hole_height = how much to move it up from the bottom
//    finger_hole_radius = the radius to use for the finger holes
// Examples:
//    CylinderWithIndents(15, 10, finger_holes = [30, 210]);
module CylinderWithIndents(
  radius,
  height,
  finger_holes = [],
  finger_hole_height = 0,
  finger_hole_radius = undef,
  anchor = BOTTOM
) {
  cyl(r=radius, h=height, anchor=anchor);
  calc_finger_hole_radius = DefaultValue(finger_hole_radius, radius / 3);
  for (i = [0:1:len(finger_holes) - 1]) {
    x = radius * cos(finger_holes[i]);
    y = radius * sin(finger_holes[i]);
    translate([x, y, finger_hole_height]) {
      cyl(
        r=calc_finger_hole_radius, h=height + calc_finger_hole_radius * 2, anchor=BOTTOM,
        rounding=calc_finger_hole_radius,
      );
    }
  }
  children();
}

// Function: HoleToPosition()
// Description:
//   Where the whole should be based on the position number.  Used by the various
//   indent methods below for putting holes in cuboids/things.
// Arguments:
//   pos = position to put the hole in
function HoleToPosition(pos) =
  (
    pos == 0 ? FRONT
    : pos == 1 ? FRONT + RIGHT
    : pos == 2 ? RIGHT
    : pos == 3 ? RIGHT + BACK
    : pos == 4 ? BACK
    : pos == 5 ? BACK + LEFT
    : pos == 6 ? LEFT
    : pos == 7 ? LEFT + FRONT
    : FRONT
  );

// Module: CuboidWithIndentsBottom()
// Description:
//    Makes a nice cuboid with finger holes bits at the specific sides, this anchors to the bottom.
//    The holes are at:
//    [LEFT + FRONT, RIGHT+BACK, LEFT, RIGHT, FRONT, BACK, ]
// Arguments:
//    size = size of the cuboid
//    finger_holes = finger holes at the specified places
//    finger_hole_height = how much to move it up from the bottom finger_hole_radius =
//    the radius to use for the finger holes
// Examples:
//    CuboidWithIndentsBottom([15, 10, 5], finger_holes = [1, 5]);
// Examples:
//    CuboidWithIndentsBottom([15, 10, 5], finger_holes = [0, 4]);
module CuboidWithIndentsBottom(
  size,
  finger_holes = [],
  finger_positions = [],
  finger_hole_height = 0,
  finger_hole_radius = undef,
  rounding = undef,
  edges = undef,
  anchor = BOTTOM
) {
  calc_finger_hole_radius = DefaultValue(finger_hole_radius, min(size[0], size[1]) * 3 / 4);
  mult = [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]];
  poses = len(finger_positions) > 0 ? finger_positions : [for (x = finger_holes) HoleToPosition(x)];
  cuboid(size, anchor=anchor, rounding=rounding, edges=edges)for (i = [0:1:len(poses) - 1]) {
    //    data = mult[finger_holes[i]];
    position(poses[i]) translate([0, 0, finger_hole_height - size[2] / 2])
        cyl(
          r=calc_finger_hole_radius, h=size[2] + calc_finger_hole_radius * 2, anchor=BOTTOM,
          rounding=calc_finger_hole_radius,
        );
  }
  children();
}

// Module: RegularPolygonGrid()
// Description:
//   Lays out the grid with all the polygons as children.  The layout handles any shape as children.
//   This uses the exact width of the polygon to layout the underlying grid.  This just does all the
//   spacing, the actual generation is done using the children to this module.  This is usually used in
//   conjuction with {{RegularPolygon()}}
// Usage:
//   RegularPolygonGrid(10, 2, 1, 2)
// Arguments:
//   width = total width of the piece, this is equivilant to the apothem of a polygon * 2
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = spacing between shapres
//   aspect_ratio = ratio between shape and width, the dy is * this (default 1.0)
//   inner_control = if the layout is controled by the client using $polygon_x and $polygon_y as the layout (defaul false)
// Topics: Grid
// Example:
//   RegularPolygonGrid(width = 10, rows = 2, cols = 1, spacing = 2)
//      RegularPolygon(width = 10, height = 5, shape_edges = 6);
module RegularPolygonGrid(
  width,
  rows,
  cols,
  spacing = 2,
  shape_edges = 6,
  aspect_ratio = 1.0,
  inner_control = 0,
  space_width = undef,
  space_length = undef
) {
  apothem = width / 2;
  radius = apothem / cos(180 / shape_edges);
  side_length = 2 * apothem * tan(180 / shape_edges);
  extra_edge = 2 * side_length * cos(360 / shape_edges);

  dx = ( (shape_edges % 2) == 1) ? apothem + radius + spacing : apothem * 2 + spacing;
  dy =
  (
    (shape_edges % 2) == 0 ? ( (shape_edges / 2 % 2) == 1 ? radius * 2 + spacing : apothem * 2 + spacing)
    : abs(2 * apothem * sin(( (shape_edges - 1) / (shape_edges * 2)) * 360)) * 2 + spacing
  ) * aspect_ratio;
  dx_y = 0;
  offset_y = ( (shape_edges % 2) == 1) ? (apothem + radius) / 2 : apothem;
  offset_x =
    ( (shape_edges % 2) == 0) ? ( (shape_edges / 2 % 2) == 1 ? radius : apothem)
    : abs(2 * apothem * sin(( (shape_edges - 1) / (shape_edges * 2)) * 360));

  rotate_deg = ( (shape_edges % 2) == 1) ? 180 / shape_edges + 90 : (shape_edges == 4 ? 45 : 0);

  if (inner_control == 2) {
    $polygon_width = space_width;
    $polygon_length = space_length;
    $polygon_grid_cols = cols;
    $polygon_grid_rows = rows;
    children();
  } else {
    for (i = [0:rows - 1])
      for (j = [0:cols - 1]) {
        if (inner_control == 1) {
          $polygon_grid_rows = rows;
          $polygon_grid_cols = cols;
          $polygon_x = i;
          $polygon_y = j;
          children();
        } else {
          translate([i * dy + offset_x - radius, j * dx + i * dx_y + offset_y - radius]) {
            children();
          }
        }
      }
  }
}

// Module: RegularPolygonGridDense()
// Description:
//   Lays out the grid with all the polygons as children in a dense layout, this only works for triangles and hexes.
//   It will do a dense space filling using the spacing as the distance between the polygons.
//   This uses the exact width of the polygon to layout the underlying grid.  This just does all the
//   spacing, the actual generation is done using the children to this module.  This is usually used in
//   conjuction with {{RegularPolygon()}}
// Usage:
//   RegularPolygonGridDense(10, 2, 1)
// Arguments:
//   radius = this is the radius of the polygon, distance from center to edges
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = spacing between shapres
// Topics: Grid
// Example:
//   RegularPolygonGridDense(radius = 10, rows = 3, cols = 2)
//      RegularPolygon(width = 10, height = 5, shape_edges = 6);
//
module RegularPolygonGridDense(radius, rows, cols, shape_edges = 6, inner_control = false) {
  if (shape_edges == 6) {
    apothem = radius * cos(180 / shape_edges);
    side_length = 2 * apothem * tan(180 / shape_edges);
    extra_edge = 2 * side_length * cos(360 / shape_edges);

    dx = apothem;
    col_x = apothem + radius;
    dy = 0.75 * (radius + radius);

    for (i = [0:rows - 1])
      for (j = [0:cols - 1]) {
        if (inner_control) {
          $polygon_x = i;
          $polygon_y = j;
          children();
        } else {

          translate([i * dy - radius, ( (i % 2) == 0 ? (j * 2 + 1) * dx : j * 2 * dx) - radius, 0]) {
            children();
          }
        }
      }
  } else if (shape_edges == 3) {
    side_length = radius * sqrt(3);
    triangle_height = sqrt(3) * side_length / 2;

    dx = side_length;
    dy = triangle_height;

    for (i = [0:rows - 1])
      for (j = [0:cols - 1]) {
        if (inner_control) {
          $polygon_x = i;
          $polygon_y = j;
          children();
        } else {
          translate([i * dy - radius, j * dx - radius, 0]) {
            children();
            //  translate([0, side_length / 2]) mirror([1, 0, 0]) children();
          }
        }
      }
  }
}

// Module: HexGridWithCutouts()
// Description:
//   This creates a hex grid with cutouts that can be used to cut out piece of a box to make a nice hex spacing
//   inside the box.
// Usage:
//   HexGridWithCutouts(rows = 4, cols = 3, height = 10, spacing = 0, push_block_height = 1, tile_width = 29);
// Arguments:
//   rows = rows of the grid
//   cols = colrs of the grid
//   height = height of the grid
//   spacing = space between the tiles
//   tile_width = width of the tiles
//   push_block_height = height of the pushblock to use (default 0)
// Topics: Recess Grid
// Example:
//   HexGridWithCutouts(rows = 4, cols = 3, height = 10, spacing = 0, push_block_height = 1, tile_width = 29);
module HexGridWithCutouts(rows, cols, height, spacing, tile_width, push_block_height = 0, wall_thickness = 2, inner_control = false) {
  width = tile_width;
  apothem = width / 2;
  radius = apothem / cos(180 / 6);

  intersection() {
    // Narrow it down to being inside the box itself.
    translate([0, 0, -10]) cube([rows * (radius * 2 + spacing), cols * (apothem * 2 + spacing), height + 20]);
    RegularPolygonGrid(width=width, rows=rows, cols=cols, spacing=0, shape_edges=6, inner_control=inner_control) {
      union() {
        difference() {
          RegularPolygon(width=width, height=10 + height, shape_edges=6);
          RegularPolygon(width=15, height=push_block_height, shape_edges=6);
        }

        translate([0, apothem, 0]) cuboid([radius, 10, 35], anchor=BOT);

        // Put in all the finger holes in the grid.
        translate([radius + 1, -apothem, -6])
          cuboid([radius + wall_thickness, 15, radius * 2], anchor=BOT, rounding=3);
        translate([radius + 1, apothem, -6])
          cuboid([radius + wall_thickness, 15, radius * 2], anchor=BOT, rounding=3);
        translate([-radius + 1, -apothem, -6])
          cuboid([radius + wall_thickness, 15, radius * 2], anchor=BOT, rounding=3);
        translate([-radius + 1, apothem, -6])
          cuboid([radius + wall_thickness, 15, radius * 2], anchor=BOT, rounding=3);
      }
    }
  }
}

// Module FingerHoleWall()
// Description:
//   Creater a finger hole cutout with nice rounded edges at the top and a cylinder of the
//   specified radius at the bottom.
// Topics: FingerHole
// Arguments:
//   radius = radius of the finger hole
//   height = height of the finger hole
//   anchor = anchor for the hole (default CENTER)
//   depth_of_hole = how deep to make the cut through the wall (default 6)
//   rounding_radious = how round to make the top in the wall (default 3)
//   material_colour = the material colour to use (default {{default_material_colour}})
// Example:
//   FingerHoleWall(10, 20)
// Example:
//   FingerHoleWall(10, 9)
module FingerHoleWall(radius, height, depth_of_hole = 6, rounding_radius = 3, orient = UP, spin = 0, material_colour = default_material_colour) {
  tmat = reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1]);
  multmatrix(m=tmat) union() {
      if (height >= radius + rounding_radius) {
        top_height = radius * 2 - height;
        middle_height = radius - top_height;
        translate([0, 0, height])
          cuboid(
            [radius * 2, depth_of_hole, middle_height], rounding=-rounding_radius,
            edges=[TOP + LEFT, TOP + RIGHT], $fn=16, anchor=TOP,
          );
        translate([0, 0, 0]) ycyl(r=radius, h=depth_of_hole, $fn=64, anchor=BOTTOM);
      } else {
        translate([0, 0, height]) rotate([90, 0, 0]) intersection() {
              translate([0, -height / 2, 0])
                cuboid([radius * 2 + rounding_radius * 2, height, depth_of_hole], anchor=CENTER);
              union() {
                tangents = circle_circle_tangents(
                  rounding_radius,
                  [
                    radius + rounding_radius,
                    -rounding_radius,
                  ],
                  radius, [0, -height + radius],
                );
                hull() {

                  for (i = [0:1:1]) {
                    mirror([i, 0, 0]) union() {
                        translate([0, 0, -depth_of_hole / 2]) linear_extrude(height=depth_of_hole) polygon(
                              [
                                tangents[3][1],
                                tangents[3][0],
                                [tangents[3][0][0] + 0.1, 0],
                                [tangents[3][1][0], 0],
                              ],
                            );
                      }
                  }
                }
                for (i = [0:1:1]) {
                  mirror([i, 0, 0]) union() {
                      difference() {
                        translate([radius + rounding_radius, -rounding_radius, -depth_of_hole / 2 - 0.5])
                          difference() {
                            cuboid(
                              [rounding_radius, rounding_radius, depth_of_hole + 1],
                              anchor=BOTTOM + FRONT + RIGHT,
                            );
                            cyl(r=rounding_radius, h=depth_of_hole + 1, $fn=32, anchor=BOTTOM);
                          }

                        translate([0, 0, -depth_of_hole / 2 - 0.5]) linear_extrude(height=depth_of_hole + 1)
                            polygon(
                              [
                                tangents[3][1],
                                tangents[3][0],
                                [tangents[3][0][0], height - radius * 2],
                                [tangents[3][1][0], height - radius * 2],
                              ],
                            );
                      }
                    }
                }

                translate([0, -height + radius, 0]) cyl(r=radius, h=depth_of_hole, $fn=64);
              }
            }
      }
    }
}

// Module: FingerHoleBase()
// Description:
//    Creates a hole in the floor of the box with a rounding over at the top to allow for picking up of cards
//    and other things.  Center on the side of the wall and the radius of the main section is the offset to the
//    middle.
// Usage: FingerHoldBase(10, 20);
// Topics: FingerHole
// Arguments:
//    radius = radius of the hole
//    height = height of the wall
//    wall_thickness = this is used as an offset to move in from the wall by this amount to cut through it (default
//    2)
//    rounding_radius = rounding radius at the top of the hole (default 3)
//    orient = orintation of the hole, from BSOL2 (default UP)
//    spin = spin of the hole, from BSOL2 (default 0)
//    anchor = location to anchor everything (from BSOL2)
// Example:
//    FingerHoleBase(10, 20);
// Example:
//    FingerHoleBase(10, 20, rounding_radius = 7);
module FingerHoleBase(
  radius,
  height,
  rounding_radius = 3,
  wall_thickness = default_wall_thickness,
  orient = UP,
  spin = 0
) {
  tmat = reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1]);
  multmatrix(m=tmat) union() {
      translate([-radius, -wall_thickness / 2, height]) {
        translate([0, wall_thickness / 2, 0]) cyl(r=radius, h=height, anchor=TOP + LEFT, $fn=64);
        cuboid(
          [radius * 2, wall_thickness + 1, height], rounding=-rounding_radius,
          edges=[TOP + LEFT, TOP + RIGHT], anchor=TOP + LEFT, $fn=32,
        );
        translate([radius, -wall_thickness / 2 - 0.01, 0]) rotate([90, 90, 0])
            cuboid(
              [height, radius * 2, wall_thickness], rounding=-wall_thickness / 2, anchor=TOP + LEFT,
              $fn=32, edges=[FRONT + TOP, TOP + BACK],
            );
      }
    }
}

// Section: Curves
// Description:
//   Space filling curves to use on the lids and other places.

// Module: HilbertCurve()
// Description:
//   Generates a hilbert curve for uses in board games.
// Usage: HilbertCurve(3, 100);
// Arguments:
//   order = depth of recursion to use 3 is a reasonable number
//   size = size to generate the curve, this is a square size
//   line_thickness = how thick to generate the lines in the curve (default = 20)
//   smoothness = how smooth to make all the curves (default 32)
// Example:
//   HilbertCurve(3, 100);
module HilbertCurve(order, size, line_thickness = 20, smoothness = 32) {

  module topline(order) {
    if (order > 0) {
      scale([0.5, 0.5]) topline(order - 1);
    } else {
      hull() {
        translate([-size / 2, size / 2]) circle(d=line_thickness);
        translate([size / 2, size / 2]) circle(d=line_thickness);
      }
      ;
    }
  }

  module leftline(order) {
    if (order > 0) {
      scale([0.5, 0.5]) translate([-size, 0]) leftline(order - 1);
    } else {
      hull() {
        translate([-size / 2, size / 2]) circle(d=line_thickness);
        translate([-size / 2, -size / 2]) circle(d=line_thickness);
      }
      ;
    }
  }

  module rightline(order) {
    if (order > 0) {
      scale([0.5, 0.5]) translate([size, 0]) rightline(order - 1);
    } else {
      hull() {
        translate([size / 2, size / 2]) circle(d=line_thickness);
        translate([size / 2, -size / 2]) circle(d=line_thickness);
      }
      ;
    }
  }

  module hilbert(order) {

    if (order > 0) {
      union() {
        translate([size / 2, size / 2]) scale([0.5, 0.5]) hilbert(order - 1);
        translate([-size / 2, size / 2]) scale([0.5, 0.5]) hilbert(order - 1);
        translate([size / 2, -size / 2]) rotate([0, 0, 90]) scale([0.5, 0.5]) hilbert(order - 1);
        translate([-size / 2, -size / 2]) rotate([0, 0, -90]) scale([0.5, 0.5]) hilbert(order - 1);
        topline(order);
        leftline(order);
        rightline(order);
      }
      ;
    }
    else
      union() {
        hull() {
          translate([size / 2, size / 2]) circle(d=line_thickness);
          translate([size / 2, -size / 2]) circle(d=line_thickness);
        }
        ;
        hull() {
          translate([-size / 2, size / 2]) circle(d=line_thickness);
          translate([-size / 2, -size / 2]) circle(d=line_thickness);
        }
        ;
        hull() {
          translate([-size / 2, size / 2]) circle(d=line_thickness);
          translate([size / 2, size / 2]) circle(d=line_thickness);
        }
        ;
      }
    ;
  }
  hilbert(order);
}
