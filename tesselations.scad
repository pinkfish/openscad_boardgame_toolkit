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

// LibFile: tesselations.scad
//    This file has all the modules needed to make a variety of tesselations.

// Includes:
//   include <boardgame_toolkit.scad>

// Function&Module: HexagonTesselationRepeatAtLocation()
// Description:
//   Used to create a hexagonal tesselation at a specific spot in a grid given an
//   x and a y location.
// Arguments:
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the hex
//   pts = the points (function only)
// Example:
//   HexagonTesselationRepeatAtLocation(x=0, y=0, size=20)
//      LizardTriangle(size=20, thickness=1);
// Example:
//   region(HexagonTesselationRepeatAtLocation(x=0, y=0, size=20, 
//      pts=LizardTriangle(size=20, thickness=1)));
module HexagonTesselationRepeatAtLocation(x, y, size) {
  assert(size > 0, str("Need to have a size specified size=", size));
  assert(is_int(x), str("Need to have a x int specified x=", x));
  assert(is_int(y), str("Need to have a y int specified y=", y));
  radius = size / 2;
  side_length = radius * sqrt(3);
  apothem = sqrt(3) / 2 * side_length;

  dx = apothem * 2;
  col_x = apothem + radius;
  dy = radius * 4 + apothem * 0.8;

  translate([x / 2 * dy, y * dx + ( (x + 1) % 2) * (dx / 2)]) {
    children();
  }
}

function HexagonTesselationRepeatAtLocation(x, y, size, pts) =
  let (
    radius = size / 2,
    side_length = radius * sqrt(3),
    apothem = sqrt(3) / 2 * side_length,
    dx = apothem * 2,
    col_x = apothem + radius,
    dy = radius * 4 + apothem * 0.8,
    new_pts = move(
      [x / 2 * dy, y * dx + ( (x + 1) % 2) * (dx / 2)],
      pts
    ),
  ) make_region(new_pts);

// Module: HexagonTesselationRepeat()
// Description:
//   Creates any hexagonal tesselation spaced correctly, using the triangle layout.
// Arguments:
//   rows = number of rows to generate
//   cols = number of columns to generate
//   size = the size of the tesselation
// Example:
//   HexagonTesselationRepeat(rows=4, cols=4, size=20)
//       LizardTriangle(size=20, thickness=1);
// Example:
//   HexagonTesselationRepeat(rows=4, cols=4, size=20)
//       RhombiTriHexagonal(40); // need to double this since not using a triangle
module HexagonTesselationRepeat(rows, cols, size) {
  assert(size > 0, str("Need to have a size specified size=", size));
  assert(rows > 0, str("Need to have a rows specified rows=", rows));
  assert(cols > 0, str("Need to have a cols specified cols=", cols));
  // Magic numbers, yay.
  radius = size / 2;
  side_length = radius * sqrt(3);
  apothem = sqrt(3) / 2 * side_length;

  dx = apothem * 2;
  col_x = apothem + radius;
  dy = radius * 4 + apothem * 0.8;

  for (i = [0:rows - 1]) {
    for (j = [0:cols - 1]) {
      translate([i / 2 * dy, j * dx + ( (i + 1) % 2) * (dx / 2)]) {
        children();
      }
    }
  }
}

// Function&Module: TriangleTesselationRepeatAtLocation()
// Description:
//   Creates any hexagonal tesselation spaced correctly, using the triangle layout.
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the triangle
// Example:
//   TriangleTesselationRepeatAtLocation(x=0, y=0, size=20)
//       LizardTriangle(size=20, thickness=1);
// Example:
//   region(TriangleTesselationRepeatAtLocation(x=0, y=0, size=20, 
//       pts=LizardTriangle(size=20, thickness=1)));
module TriangleTesselationRepeatAtLocation(x, y, size) {
  assert(size != 0, "Need to have a size specified");
  assert(is_int(x), str("Need to have a x int specified x=", x));
  assert(is_int(y), str("Need to have a y int specified y=", y));
  side_length = size * sin(60);
  height = side_length * (sqrt(3) / 2);

  translate([side_length / 2 * x, height * y + (size - height) * (x % 2)]) {
    rotate(60 * (x % 2))
      children();
  }
}

function TriangleTesselationRepeatAtLocation(x, y, size, pts) =
  assert(size != 0, "Need to have a size specified")
  assert(is_int(x), str("Need to have a x int specified x=", x))
  assert(is_int(y), str("Need to have a y int specified y=", y))
  let (
    side_length = size * sin(60),
    height = side_length * (sqrt(3) / 2),
  ) move(
    [side_length / 2 * x, height * y + (size - height) * (x % 2)],
    rot(a=60 * (x % 2), p=pts)
  );

// Module: TriangleTesselationRepeat()
// Description:
//   Creates any triangle tesselation spaced correctly.
// Arguments:
//   rows = number of rows to generate
//   cols = number of columns to generate
//   size = the size of the tesselation
// Example:
//   TriangleTesselationRepeat(rows=4, cols=4, size=20)
//       HalfRegularHexagon(20);
module TriangleTesselationRepeat(rows, cols, size) {
  assert(size > 0, str("Need to have a size specified size=", size));
  assert(rows > 0, str("Need to have a rows specified rows=", rows));
  assert(cols > 0, str("Need to have a cols specified cols=", cols));
  side_length = size * sin(60);
  height = side_length * (sqrt(3) / 2);

  for (i = [0:rows - 1]) {
    for (j = [0:cols - 1]) {
      translate([side_length / 2 * i, height * j + (size - height) * (i % 2)]) {
        rotate(60 * (i % 2))
          children();
      }
    }
  }
}

// Function: HexagonalTesselationGenerateEdge()
// Description:
//   Internal helper for the hexagonal tesselation generation to setup an edge.
function HexagonalTesselationGenerateEdge(pts, side_length) = [for (i = [0:len(pts) - 1]) (pts[i] * side_length)];

// Function&Module: HexagonalTesselation()
// Description:
//   Make a tessealation around a hex.  It will distort the sides using
//   the input sets for each side.  Each goes from -0.5 - 0.5 in the x
//   direction using the set of points to create the line.
// Arguments:
//   points = set of three lines to use as points on the hex.
//   radius = the radius of the hex.
// Example:
//   HexagonalTesselation(
//     points=[
//       [[-0.5, 0], [0, 0.2], [0.5, 0]],
//       [[-0.5, 0], [0, -0.2], [0.5, 0]],
//       [[-0.5, 0], [0.3, 0.2], [0.5, 0]],
//     ]
//   );
// Example:
//   region(HexagonalTesselation(
//     points=[
//       [[-0.5, 0], [0, 0.2], [0.5, 0]],
//       [[-0.5, 0], [0, -0.2], [0.5, 0]],
//       [[-0.5, 0], [0.3, 0.2], [0.5, 0]],
//     ]
//   ));
module HexagonalTesselation(points, radius = 10) {
  assert(len(points) == 3, str("points must have three arrays", points));
  for (c = [0:len(points) - 1]) {
    assert(len(points[c]) > 1, str("Each array must have more than two elements", points[c]));
  }
  side_length = 2 * radius * sin(30);
  apothem = sqrt(3) / 2 * side_length;

  // List of 3 sets of points to work as the exterior points on the line
  // represented as a percentage of the side.

  poly = [
    for (i = [0:5]) each move(
      rot(a=60 * i, p=[[apothem, 0]])[0],
      rot(
        a=60 * i + 90, p=HexagonalTesselationGenerateEdge(
          pts=i % 2 == 0 ? reverse(rot(a=180, p=points[i / 2 % 3])) : points[i / 2 % 3],
          side_length
        )
      )
    ),
  ];
  polygon(poly);
}

function HexagonalTesselation(points, radius = 10) =
  let (
    side_length = 2 * radius * sin(30),
    apothem = sqrt(3) / 2 * side_length,
    poly = [
      for (i = [0:5]) each move(
        rot(a=60 * i, p=[[apothem, 0]])[0],
        rot(
          a=60 * i + 90, p=HexagonalTesselationGenerateEdge(
            pts=i % 2 == 0 ? reverse(rot(a=180, p=points[i / 2 % 3])) : points[i / 2 % 3],
            side_length
          )
        )
      ),
    ]
  ) poly;

function SquareTesselationGenerateEdge(pts, side_length) = [for (i = [0:len(pts) - 1]) (pts[i] * side_length)];

// Function&Module: SquareTesselation()
// Description:
//   Make a tessealation around a square.  It will distort the sides using
//   the input sets this only needs two sides.  Each goes from -0.5 - 0.5 in the x
//   direction using the set of points to create the line.
// Arguments:
//   points = set of two lines to use as points on the square.
//   size = the size of the square (width, length).
//   thickness = the thickness of the outline, if non-0 adds an outline.
//   outer_offset = how much to offset the edge by so it overlaps in a pattern, added to the outside.
// Example:
//   SquareTesselation(
//     points=[
//       [[-0.5, 0], [0, 0.2], [0.5, 0]],
//       [[-0.5, 0], [0, -0.2], [0.5, 0]],
//     ],
//     size=[20,20]
//   );
// Example:
//   linear_extrude(height = 2) 
//   RegularPolygonGrid(
//     width=20, rows=5, cols=5, spacing=0,
//     shape_edges=4, aspect_ratio=1.0,
//     space_width=20, space_length=20
//   )
//     SquareTesselation(
//       points=[
//         [[-0.5, 0], [0.2, 0.3], [0.5, 0]],
//         [[-0.5, 0], [0.1, 0.2], [0.5, 0]],
//       ],
//       size=[20, 20], thickness=1, outer_offset=0.1
//     );
// Example:
//   region(SquareTesselation(
//     points=[
//       [[-0.5, 0], [0, 0.2], [0.5, 0]],
//       [[-0.5, 0], [0, -0.2], [0.5, 0]],
//     ],
//     size=[20,20]
//   ));
module SquareTesselation(points, size, thickness = 0, outer_offset = 0) {
  width = size[0];
  length = size[1];
  length_line = SquareTesselationGenerateEdge(points[0], length);
  width_line = SquareTesselationGenerateEdge(points[1], width);
  poly = [
    each move([-width / 2, 0], reverse(rot(a=90, p=width_line))),
    each move([0, -length / 2], rot(a=0, p=length_line)),
    each move([width / 2, 0], rot(a=90, p=width_line)),
    each move([0, length / 2], reverse(rot(a=0, p=length_line)))
  ];
  difference() {
    if (outer_offset != 0) {
      offset(delta=outer_offset, chamfer=true) polygon(poly);
    } else {
      polygon(poly);
    }
    if (thickness != 0) {
      offset(delta=-thickness, chamfer=true) polygon(poly);
    }
  }
}

function SquareTesselation(points, size, thickness = 0, outer_offset = 0) =
  assert(size != 0, "Need to have a size specified")
  assert(len(points) == 2, str("Input points must be of size 2", points))
  assert(len(size) == 2, str("Input size must be of form [x,y]", size))
  let (
    width = size[0],
    length = size[1],
    length_line = SquareTesselationGenerateEdge(points[0], length),
    width_line = SquareTesselationGenerateEdge(points[1], width),
    poly = path_merge_collinear(
      [
        each move([-width / 2, 0], reverse(rot(a=90, p=width_line))),
        each move([0, -length / 2], rot(a=0, p=length_line)),
        each move([width / 2, 0], rot(a=90, p=width_line)),
        each move([0, length / 2], reverse(rot(a=0, p=length_line)))
      ], closed=true
    )
  ) difference(
    make_region(
      outer_offset != 0 ?
        offset(poly, delta=outer_offset, chamfer=true)
      : poly
    ),

    make_region(
      thickness != 0 ?
        path_merge_collinear(offset(poly, delta=-thickness, chamfer=true), closed=true)
      : [[-100, -100], [-101, -100], [-101, -101]]
    )
  );

// Function: TesselationSideLine()
// Description:
//    Do the tesselation from a side line.
// Arguments:
//    path = the path to point the side on
//    side = the pattern to do with the side
function TesselationSideLine(path, side) =
  assert(len(path) == 2, str("Input path must be of size 2", path))
  assert(len(path[0]) == 2 && len(path[1]) == 2, str("Input path[0],[1] must be of size 2", path))
  assert(len(side) >= 2, str("Input side must be more than size 2", side))
  let (
    x = path[1][0] - path[0][0],
    y = path[1][1] - path[0][1],
    split_length = sqrt(x * x + y * y),
    angle = atan2(y, x),
    rotated_line = rot(a=angle, p=side * split_length)
  ) move(path[0], rotated_line);

// Function: TesselationPolygon()
// Description:
//    Do the tesselation for a whole polygon given lines and indexes.
// Arguments:
//    path = the path to point the side on
//    side = the pattern to do with the side
function TesselationPolygon(path, side_indexes, sides) =
  assert(len(path) > 2, str("Input path must be of size 2", path))
  assert(len(side_indexes) == len(path)-1, str("side indexes -1 and paths must be the same size", path, side_indexes))
  let (
    each_line = [
      each for (i =[0:len(side_indexes)-1]) TesselationSideLine(
        [path[i], path[(i+1)%len(path)]], sides[side_indexes[i]])
    ]
  ) each_line;

// Function&Module: TesselationDrop()
// Description:
//  Creates a drop tesselation.
// Arguments:
//   size = the size of the drop ([x,y])
//   arc_offset = how wide the arc should be.
//   thickness = the thickness of the wall (if non 0)
//   outer_offset = the amount to add to the outside of the shape for layout
//   arc_points = how many points on the arc
// Example:
//   TesselationDrop(size = [20,20]);
module TesselationDrop(size, thickness = 0, outer_offset = 0, arc_offset = 0.2, arc_points = 10) {
  region(
    TesselationDrop(size=size, thickness=thickness, outer_offset=outer_offset, arc_offset=arc_offset, arc_points=arc_points)
  );
}

function TesselationDrop(size, thickness = 0, outer_offset = 0, arc_offset = 0.2, arc_points = 10) =
  assert(size != 0, "Need to have a size specified")
  SquareTesselation(
    points=[
      arc(n=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]]),
      arc(n=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]]),
    ],
    size=size, thickness=thickness, outer_offset=outer_offset
  );

// Module: TesselationLeaf()
// Description:
//   A solid leaf for use with tesselations.
// Arguments:
//   size = size of the leaf
// Example:
//   TesselationLeaf(40);
module TesselationLeaf(size) {
  assert(size != 0, "Need to have a size specified");
  section = size / 4;
  section_height = section * calc_sqrt_three / 2;
  polygon(
    [
      [section_height * 2, 0],
      [0, section * 1],
      [0, section * 2],
      [-section_height * 2, section],
      [-section_height * 2, -section],
      [0, -section * 2],
      [0, -section * 1],
    ]
  );
}

// Function&Module: TesselationLeafOutline()
// Description:
//   A leaf outline for use with tesselations.
// Arguments:
//   size = size of the leaf
//   thickness = thickness of the sides
//   with_veins = show veins in the leaf
//   vein_thickness = how thick to make the veins in the leaf
// Example:
//   TesselationLeafOutline(40);
// Example:
//   TesselationLeafOutline(40, with_veins=true);
module TesselationLeafOutline(size, thickness = undef, with_veins = false, vein_thickness = undef) {
  assert(size != 0, "Need to have a size specified");
  region(TesselationLeafOutline(size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness));
}

// Function: TesselationLeafOutlineMakePolygon()
// Description:
//   The internal piece to make a boundary for the leaf.
// Arguments:
//   section_height = height of the section
//   section = the section
function TesselationLeafOutlineMakePolygon(section_height, section) =
  path_merge_collinear(
    [
      [section_height * 2, 0],
      [0, section * 1],
      [0, section * 2],
      [-section_height * 2, section],
      [-section_height * 2, -section],
      [0, -section * 2],
      [0, -section * 1],
    ], closed=true
  );

// Function: TesselationLeafOutlineMakeVeins()
// Description:
//   Make the veins for the leaf.
// Arguments:
//   calc_thickness = the thickness of the leaf
//   section_height = height of the section
//   section = the section
//   calc_vein_thickness = how thick to make the veins in the leaf
function TesselationLeafOutlineMakeVeins(calc_thickness, section_height, section, calc_vein_thickness) =
  let (
    vein_base_x = -section_height * 2 + calc_thickness,
    vein_side_x = calc_vein_thickness / 2,
    vein_side_y = section * 2 - calc_vein_thickness,
    vein_spacing = section_height * 3 / 2 / 3,
    len_bottom_vein = sqrt(
      sqr(vein_base_x - vein_side_x) + sqr(vein_side_y)
    ),
    line_m = (vein_side_x - vein_base_x) / (vein_side_y),
    line_angle = atan(line_m),
    mini_seg = len_bottom_vein / 7,
    veins = intersection(

      union(
        make_region(
          offset_stroke(
            [
              [vein_base_x, 0],
              [section_height * 2 - calc_thickness, 0],
            ],
            width=calc_vein_thickness,
          )
        ),
        union(
          make_region(
            offset_stroke(
              [
                [vein_base_x, 0],
                [vein_side_x, vein_side_y],
              ],
              width=calc_vein_thickness
            )
          ),

          make_region(
            offset_stroke(
              [
                [vein_base_x, 0],
                [-vein_side_x, -vein_side_y],
              ],
              width=calc_vein_thickness
            )
          ),

          union(
            [
              for (i = [0:3]) union(
                make_region(
                  offset_stroke(
                    [
                      [section_height - section_height * 4 / 2 + vein_spacing * i, 0],
                      [section_height - section_height * 3 / 2 + 20 + vein_spacing * i, 15],
                    ], width=calc_vein_thickness
                  )
                ),
                make_region(
                  offset_stroke(
                    [
                      [section_height - section_height * 4 / 2 + vein_spacing * i, 0],
                      [section_height - section_height * 3 / 2 + 20 + vein_spacing * i, -15],
                    ], width=calc_vein_thickness
                  )
                ),
                union(
                  move(
                    [vein_base_x, 0], rot(
                      a=(90 - line_angle),
                      p=offset_stroke(
                        [
                          [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                          [mini_seg * (i + 2) + mini_seg * 3, -mini_seg * 2.5 - calc_vein_thickness / 4],
                        ], width=calc_vein_thickness
                      ),
                    )
                  ),
                  move(
                    [vein_base_x, 0], rot(
                      a=90 - line_angle,
                      p=offset_stroke(
                        [
                          [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                          [mini_seg * (i + 2) + mini_seg * 3, mini_seg * 2 + calc_vein_thickness / 4],
                        ], width=calc_vein_thickness
                      )
                    ),
                  ),
                  union(
                    move(
                      [vein_base_x, 0], rot(
                        a=-(90 - line_angle),
                        p=offset_stroke(
                          [
                            [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                            [mini_seg * (i + 2) + mini_seg * 3, -mini_seg * 2],
                          ], width=calc_vein_thickness
                        ),
                      ),
                    ),
                    move(
                      [vein_base_x, 0], rot(
                        a=-(90 - line_angle),
                        p=offset_stroke(
                          [
                            [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                            [mini_seg * (i + 2) + mini_seg * 3, mini_seg * 2.5 + calc_vein_thickness / 4],
                          ], width=calc_vein_thickness
                        )
                      ),
                    )
                  )
                )
              ),
            ]
          ),
        ),
      ),
      make_region(
        TesselationLeafOutlineMakePolygon(section_height=section_height, section=section)
      )
    )
  ) veins;

function TesselationLeafOutline(size, thickness = undef, with_veins = false, vein_thickness = undef) =
  let (
    calc_thickness = DefaultValue(thickness, size / 30),
    calc_vein_thickness = DefaultValue(vein_thickness, calc_thickness / 2),
    section = size / 4,
    section_height = section * calc_sqrt_three / 2,
    pts = union(
      difference(
        TesselationLeafOutlineMakePolygon(section=section, section_height=section_height),
        offset(TesselationLeafOutlineMakePolygon(section=section, section_height=section_height), delta=-calc_thickness),
      ),
      with_veins ?
        TesselationLeafOutlineMakeVeins(
          calc_thickness=calc_thickness,
          section_height=section_height, section=section, calc_vein_thickness=calc_vein_thickness
        )
      : make_region([[-100, -100], [-101, -100], [-101, -101]])
    )
  ) pts;

// Function&Module: TesselationLeafOutlineThree()
// Description:
//   A leaf outline for use with tesselations, this groups into three
//   to make layout a lot easier.
// Arguments:
//   size = size of the leaf
//   thickness = thickness of the sides
//   with_veins = show veins in the leaf
//   vein_thickness = how thick the veins in the lid are
// Example:
//   TesselationLeafOutlineThree(40);
// Example:
//   TesselationLeafOutlineThree(40, with_veins=true);
// Example:
//   TesselationLeafOutlineThree(40, thickness=2, with_veins=true);
module TesselationLeafOutlineThree(size, thickness = undef, with_veins = false, vein_thickness = undef) {
  assert(size != 0, "Need to have a size specified");
  region(TesselationLeafOutlineThree(size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness));
}

function TesselationLeafOutlineThree(size, thickness = undef, with_veins = false, vein_thickness = undef) =
  let (
    section = size / 4,
    section_height = section * calc_sqrt_three / 2,
    pts = union(
      move(
        [0, -section * 3 / 2],
        TesselationLeafOutline(
          size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
        ),
      ),
      move(
        [-section_height * 2, section * 3 / 2],
        rot(
          a=180,
          p=TesselationLeafOutline(
            size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
          )
        ),
      ),
      move(
        [section_height * 2, section / 2],
        TesselationLeafOutline(
          size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
        )
      ),
    ),
  ) pts;

// Function&Module: DeltoidTrihexagonalTiling()
// Description:
//   A tesselation to use with the layout to make nice triangle layout hex
//   pattern.
// Arguments:
//   size = size of the hex
//   thickness = thickness of the sides
//   outer_offset = how much to offset the outside edge
//   kite = do a kite tiling
// Example:
//   DeltoidTrihexagonalTiling(20);
// Example:
//   DeltoidTrihexagonalTiling(20, kite=true);
// Example:
//   region(DeltoidTrihexagonalTiling(20));
module DeltoidTrihexagonalTiling(size, thickness = 1, outer_offset = 0, kite = false) {
  assert(size != 0, "Need to have a size specified");
  module InnerParts() {
    union() {
      for (i = [0:5]) {
        difference() {
          offset(thickness / 10)
            polygon(
              DeltoidTrihexagonalTilingGetPoints(pts, i)
            );
          offset(delta=-thickness)
            polygon(
              DeltoidTrihexagonalTilingGetPoints(pts, i)
            );
        }
      }
    }
  }

  width = size / 2;
  height = sqrt(3) * width;
  pts = [
    [width * 0.5, height / 2],
    [width, 0],
    [width * 0.5, -height / 2],
    [width * -0.5, -height / 2],
    [-width, 0],
    [width * -0.5, height / 2],
  ];
  union() {
    difference() {
      offset(outer_offset)
        polygon(
          pts
        );
      offset(delta=-thickness)
        polygon(
          pts
        );
    }
    intersection() {
      InnerParts();
      offset(delta=-thickness + 0.1)
        polygon(
          pts
        );
    }
  }
}

// Function: DeltoidTrihexagonalTilingGetPoints()
// Description:
//   A interl part of the deltoid tesslation.
// Arguments:
//   pts = the points to mess with
//   thickness = thickness of the sides
//   kite = do a kite tiling
function DeltoidTrihexagonalTilingGetPoints(pts, i, kite) =
  kite ?
    [pts[i], (pts[ (i + 1) % 6] + pts[i]) / 2, [0, 0], (pts[ (i + 5) % 6] + pts[i]) / 2]
  : [pts[i], pts[ (i + 1) % 6], [0, 0]];

// Function: DeltoidTrihexagonalTilingInnerParts()
// Description:
//   A interl part of the deltoid tesslation.
// Arguments:
//   pts = the points to mess with
//   thickness = thickness of the sides
//   kite = do a kite tiling
function DeltoidTrihexagonalTilingInnerParts(pts, thickness, kite) =
  union(
    [
      for (i = [0:5]) difference(
        offset(
          DeltoidTrihexagonalTilingGetPoints(pts, i, kite),
          delta=thickness / 10
        ),
        offset(
          DeltoidTrihexagonalTilingGetPoints(pts, i, kite),
          delta=-thickness
        )
      ),
    ]
  );

function DeltoidTrihexagonalTiling(size, thickness = 1, outer_offset = 0, kite = false) =
  assert(size != 0, "Need to have a size specified")
  let (
    width = size / 2,
    height = sqrt(3) * width,
    pts = [
      [width * 0.5, height / 2],
      [width, 0],
      [width * 0.5, -height / 2],
      [width * -0.5, -height / 2],
      [-width, 0],
      [width * -0.5, height / 2],
    ],
  ) union(
    difference(
      offset(
        pts, delta=outer_offset
      ),
      offset(
        pts, delta=-thickness
      )
    ),
    intersection(
      DeltoidTrihexagonalTilingInnerParts(pts, thickness, kite),
      offset(
        pts,
        delta=-thickness + 0.1
      )
    )
  );

// Function&Module: HalfRegularHexagon()
// Description:
//   A half regular hexagon to use with the layout to make nice layout.
//   This is actually based on a triangle tesselation with rotations
// Arguments:
//   size = size of the hex
//   thickness = thickness of the sides
//   outer_offset = how much to offset the outside edge
// Example:
//   HalfRegularHexagon(20);
// Example:
//   region(HalfRegularHexagon(20));
module HalfRegularHexagon(size, thickness = 1, outer_offset = 0) {
  assert(size != 0, "Need to have a size specified");
  side_length = size * sin(60);
  height = side_length * (sqrt(3) / 2);
  pts = [
    [0, size / 2],
    [side_length / 2, size / 2 - height],
    [-side_length / 2, size / 2 - height],
  ];
  for (i = [0:2]) {
    difference() {
      offset(outer_offset)
        polygon(
          [
            pts[i],
            (pts[i] + pts[ (i + 1) % 3] * 2) / 3,
            [0, 0],
            (pts[i] * 2 + pts[ (i + 2) % 3]) / 3,
            pts[i],
          ]
        );
      offset(-thickness)
        polygon(
          [
            pts[i],
            (pts[i] + pts[ (i + 1) % 3] * 2) / 3,
            [0, 0],
            (pts[i] * 2 + pts[ (i + 2) % 3]) / 3,
            pts[i],
          ]
        );
    }
  }
}

function HalfRegularHexagon(size, thickness = 1, outer_offset = 0) =
  assert(size != 0, "Need to have a size specified")
  let (
    side_length = size * sin(60),
    height = side_length * (sqrt(3) / 2),
    pts = [
      [0, size / 2],
      [side_length / 2, size / 2 - height],
      [-side_length / 2, size / 2 - height],
    ]
  ) union(
    [
      for (i = [0:2]) difference(
        path_merge_collinear(
          offset(
            path_merge_collinear(
              [
                pts[i],
                (pts[i] + pts[ (i + 1) % 3] * 2) / 3,
                [0, 0],
                (pts[i] * 2 + pts[ (i + 2) % 3]) / 3,
                pts[i],
              ],
              closed=true
            ),
            delta=outer_offset
          )
        ),
        offset(
          path_merge_collinear(
            [
              pts[i],
              (pts[i] + pts[ (i + 1) % 3] * 2) / 3,
              [0, 0],
              (pts[i] * 2 + pts[ (i + 2) % 3]) / 3,
              pts[i],
            ],
            closed=true
          ), delta=-thickness
        )
      ),
    ]
  );

// Function&Module: RhombiTriHexagonal()
// Description:
//   A rhombitrihexagon layout, which makes a nifty tesselation.
//   This is actually based on a triangle tesselation with rotations
// Arguments:
//   size = size of the hex
//   thickness = thickness of the sides
//   outer_offset = how much to offset the outside edge
// Example:
//   RhombiTriHexagonal(20);
// Example:
//   region(RhombiTriHexagonal(20));
module RhombiTriHexagonal(size, thickness = 1, outer_offset = 0.1) {
  assert(size > 0, "Need to have a size specified");
  calc_size = size * 0.8;
  radius = calc_size / 2;
  apothem = cos(30) * radius;
  side_length = radius;

  width = calc_size / 2;
  height = sqrt(3) * width;
  pts = [
    [width * 0.5, height / 2],
    [width, 0],
    [width * 0.5, -height / 2],
    [width * -0.5, -height / 2],
    [-width, 0],
    [width * -0.5, height / 2],
  ];
  inner_side_length = apothem * sqrt(3) / 2;
  inner_apothem = inner_side_length / (sqrt(3)) * 2;

  // outer_apothem=inner_apothem+side_length/2
  // inner_apothem=side_length/(sqrt(3)*2)
  // outer_apothem=side_length/(sqrt(3)*2)+side_length/2
  // outer_apothem=(side_length*2)/(sqrt(3)*2/2)
  // outer_apothem=side_length*2/sqrt(3)
  // side_length = outer_apothem*sqrt(3)/2

  intersection() {
    circle(d=size, $fn=6);
    union() {
      difference() {
        offset(outer_offset)
          circle(d=inner_side_length * 2, $fn=6);
        offset(-thickness) circle(d=inner_side_length * 2, $fn=6)
            circle(d=inner_side_length * 2, $fn=6);
      }
      for (i = [0:5]) {
        difference() {
          union() {
            offset(outer_offset)
              polygon(
                rot(
                  a=60 * i - 30, p=move(
                    [(calc_size / 2), 0], p=square([inner_side_length, inner_side_length + thickness], center=true)
                  )
                )
              );
          }
          offset(-thickness)
            polygon(
              rot(
                a=60 * i - 30, p=move(
                  [(calc_size / 2), 0], p=square([inner_side_length, inner_side_length], center=true)
                )
              )
            );
        }
      }
    }
  }
}

function RhombiTriHexagonal(size, thickness = 1, outer_offset = 0.1) =
  assert(size > 0, "Need to have a size specified")
  let (
    calc_size = size * 0.8,
    radius = calc_size / 2,
    apothem = cos(30) * radius,
    side_length = radius,
    width = calc_size / 2,
    height = sqrt(3) * width,
    pts = [
      [width * 0.5, height / 2],
      [width, 0],
      [width * 0.5, -height / 2],
      [width * -0.5, -height / 2],
      [-width, 0],
      [width * -0.5, height / 2],
    ],
    inner_side_length = apothem * sqrt(3) / 2,
    inner_apothem = inner_side_length / (sqrt(3)) * 2,

    // outer_apothem=inner_apothem+side_length/2
    // inner_apothem=side_length/(sqrt(3)*2)
    // outer_apothem=side_length/(sqrt(3)*2)+side_length/2
    // outer_apothem=(side_length*2)/(sqrt(3)*2/2)
    // outer_apothem=side_length*2/sqrt(3)
    // side_length = outer_apothem*sqrt(3)/2
  ) make_region(
    intersection(
      circle(d=size, $fn=6),
      union(
        make_region(
          difference(
            offset(
              circle(d=inner_side_length * 2, $fn=6),
              delta=outer_offset,
            ),
            offset(
              circle(
                d=inner_side_length * 2, $fn=6,
              ),
              delta=-thickness
            )
          )
        ),
        union(
          [
            for (i = [0:5]) difference(
              make_region(
                offset(
                  rot(
                    a=60 * i - 30, p=move(
                      [(calc_size / 2), 0], p=square([inner_side_length, inner_side_length + thickness], center=true)
                    )
                  ),
                  delta=outer_offset,
                )
              ),
              make_region(
                offset(
                  rot(
                    a=60 * i - 30, p=move(
                      [(calc_size / 2), 0], p=square([inner_side_length, inner_side_length], center=true)
                    )
                  ),
                  delta=-thickness,
                )
              )
            ),
          ]
        )
      )
    )
  );

// Module: TesselationPegasus()
// Description:
//    Pegasus tesselation to use on the lids.
// Arguments:
//    size = size of the hex
//    thickness = thickness of the sides
//    outer_offset = how much to offset the outside edge
// Example:
//    TesselationPegasus(size=[20, 20]);
// Example:
//    TesselationPegasus(size=[30, 20], thickness=0.5);
module TesselationPegasus(size, thickness = 0, outer_offset = 0) {
  assert(len(size) == 2, "Need to have a size specified as two element array");
  assert(size[0] > 0 && size[1] > 0, "Need to have a size specified > 0");
  assert(thickness >= 0, "Need to have thickness specified");
  assert(outer_offset >= 0, "Need to have outer_offset specified");

  SquareTesselation(
    points=[
      (
        (
          [
            for (
              i = (
                [
                  [-0.5, -0],
                  [-0.131497, 0.189891],
                  [-0.111942, 0.23038],
                  [-0.101048, 0.273655],
                  [-0.0887842, 0.316685],
                  [-0.0365644, 0.30475],
                  [0.0156516, 0.292797],
                  [0.0678689, 0.280851],
                  [0.0172526, 0.161771],
                  [-0.036603, 0.0942535],
                  [-0.104924, 0.0332333],
                  [-0.166696, -0.0188206],
                  [-0.172123, -0.107408],
                  [-0.118787, -0.210899],
                  [-0.121088, -0.235661],
                  [-0.123389, -0.260423],
                  [-0.12569, -0.285184],
                  [-0.0345562, -0.301811],
                  [0.0625798, -0.319535],
                  [0.141772, -0.333985],
                  [0.172519, -0.4],
                  [0.193835, -0.333349],
                  [0.493345, -0.21837],
                  [0.491797, -0.170607],
                  [0.469955, -0.158724],
                  [0.465464, -0.119576],
                  [0.443623, -0.107693],
                  [0.46217, -0.0703219],
                  [0.480717, -0.0329511],
                  [0.499265, 0.00441975],
                  [0.499512, 0.00494432],
                  [0.5, 0],
                ]
              )
            ) [i[0], -i[1]],
          ]
        )
      ),
      (
        [
          for (
            i = (
              [
                [0.5, -0.0],
                [0.456143, -0.0789084],
                [0.406509, -0.123072],
                [0.365506, -0.158244],
                [0.29841, -0.12978],
                [0.27285, -0.0853574],
                [0.205624, -0.0572037],
                [0.165011, 0.0314834],
                [0.06979, 0.117951],
                [-0.0974454, 0.0612218],
                [-0.093908, -0.0578449],
                [-0.0255355, -0.0900762],
                [-0.00708426, -0.0756784],
                [0.0252447, -0.0474022],
                [0.0436957, -0.0330041],
                [0.110764, -0.115447],
                [0.0767458, -0.148258],
                [0.0311628, -0.16719],
                [-0.00285616, -0.2],
                [-0.0599237, -0.179476],
                [-0.116194, -0.156928],
                [-0.172503, -0.134443],
                [-0.178267, 0.0363945],
                [-0.178267, 0.0363945],
                [-0.325784, 0.11531],
                [-0.394859, 0.166938],
                [-0.498287, 0.220646],
                [-0.5, 0.221534],
                [-0.498991, 0.13894],
                [-0.497203, 0.131818],
                [-0.458524, -0.0222559],
                [-0.456539, -0.0],
              ]
            )
          ) [-i[0], i[1]],
        ]
      ),
    ],
    size=size, thickness=thickness, outer_offset=outer_offset
  );
}
