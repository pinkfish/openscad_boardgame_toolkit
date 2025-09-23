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

// Module: EscherLizardSingle()
// Description:
//   Creates a single escher lizard.
// Arguments:
//   size = the size of the lizard
// Example:
//   EscherLizardSingle(size=20);
module EscherLizardSingle(size) {
  EscherLizardHexTesselation(radius=size / 2);
}

// Module: EscherLizardTriangle()
// Description:
//    Makes the triangle that can be used to fill in the escher lizard
//    tesselation in a wider group.  This will not need to be
//    rotated.
// Arguments:
//    size = size the hex
//    thickness = thickness of the walls/edges
//    outer_offset = how much padding on the outside
// Example:
//    HexagonalTesselationTriangle(size=20)
//       EscherLizardHexTesselation(radius=10, thickness=1);
module EscherLizardTriangle(size, thickness, outer_offset = 0) {
  HexagonalTesselationTriangle(size=size)
    EscherLizardHexTesselation(radius=size / 2, thickness=thickness, outer_offset=outer_offset);
}

// Module: HexagonalTesselationTriangle()
// Description:
//    Makes the triangle that can be used to fill in the hexagonal
//    tesselation in a wider group.  This will not need to be
//    rotated.
// Arguments:
//    size = size the hex
// Example:
//    HexagonalTesselationTriangle(size=20)
//       EscherLizardHexTesselation(radius=10, thickness=1);
module HexagonalTesselationTriangle(size) {
  assert(size > 0, str("Need to have a size specified size=", size));

  side_length = 2 * size * sin(30);
  apothem = sqrt(3) / 2 * side_length;

  translate([-apothem / 2, size]) {
    union() {
      children();
      translate(
        [apothem / 2, size * 3 / 4]
      )
        rotate(240)
          children();

      translate(
        [
          apothem,
          0,
        ]
      )
        rotate(120)
          children();
    }
  }
}

// Module: EscherLizardSingleOutline()
// Description:
//   Creates a single escher lizard with an outline.
// Arguments:
//   size = the size of the lizard
// Example:
//   EscherLizardSingleOutline(size=20, thickness=1);
module EscherLizardSingleOutline(size, thickness) {
  assert(size > 0, str("Need to have a size specified size=", size));
  assert(thickness > 0, str("Need to have a thickness specified thickness=", thickness));
  EscherLizardHexTesselation(radius=size / 2, thickness=thickness);
}

// Module: EscherLizardRepeatAtLocation()
// Description:
//   Used to create an escher lizard at a specific spot in a grid given an
//   x and a y location.
// Arguments:
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the lizard
//   thickness = the thickness of the lines
//   outer_offset = extra space to put around the shape.
// Example:
//   EscherLizardRepeatAtLocation(x=0, y=0, size=20, thickness=1);
// Example:
//   EscherLizardRepeatAtLocation(x=0, y=0, size=20, thickness=1, outer_offset=0.1);
module EscherLizardRepeatAtLocation(x, y, size, thickness, outer_offset = 0) {
  HexagonTesselationRepeatAtLocation(x=x, y=y, size=size)
    EscherLizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset);
}

// Module: EscherLizardRepeat()
// Description:
//   Creates an escher lizard blob that can be repeated.
// Arguments:
//   size = the size of the lizard
// Example:
//   EscherLizardRepeat(rows=4, cols=4, size=20, thickness=1);
module EscherLizardRepeat(rows, cols, size, thickness, outer_offset = 0.01) {
  HexagonTesselationRepeat(rows=rows, cols=cols, size=size)
    EscherLizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset);
}

// Module: HexagonTesselationRepeatAtLocation()
// Description:
//   Used to create a hexagonal tesselation at a specific spot in a grid given an
//   x and a y location.
// Arguments:
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the lizard
//   thickness = the thickness of the lines
// Example:
//   HexagonTesselationRepeatAtLocation(x=0, y=0, size=20)
//      EscherLizardTriangle(size=20, thickness=1);
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

// Module: HexagonTesselationRepeat()
// Description:
//   Creates any hexagonal tesselation spaced correctly, using the triangle layout.
// Arguments:
//   size = the size of the tesselation
// Example:
//   HexagonTesselationRepeat(rows=4, cols=4, size=20)
//       EscherLizardTriangle(size=20, thickness=1);
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

// Module: TriangleTesselationRepeatAtLocation()
// Description:
//   Used to create a triangle tesselation at a specific spot in a grid given an
//   x and a y location.
// Arguments:
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the lizard
//   thickness = the thickness of the lines
// Example:
//   TriangleTesselationRepeatAtLocation(x=0, y=0, size=20)
//       EscherLizardTriangle(size=20, thickness=1);
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

// Module: TriangleTesselationRepeat()
// Description:
//   Creates any triangle tesselation spaced correctly.
// Arguments:
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

// Function: VoronoiPoints()
// Description:
//   Generates a set of Voronoi points to use in the system to make
//   the nice voronoi pattern.
function VoronoiPoints(width, length, cellsize, allowable, seed) =
  let (
    seed_calc = DefaultValue(seed + width * length / allowable + cellsize, round(rands(0, 100000, 1)[0])),
    half_cell = cellsize / 2,
    x_cells = floor(width / cellsize),
    y_cells = floor(length / cellsize),
    allowable_min = half_cell - allowable * half_cell,
    allowable_max = half_cell + allowable * half_cell,
    num_points = x_cells * y_cells,
    rnd_points = rands(allowable_min, allowable_max, num_points * 2, seed=seed_calc)
  ) [
      for (x = [0:x_cells - 1]) for (y = [0:y_cells - 1]) [
        x * cellsize + rnd_points[ (x + y * x_cells) * 2],
        y * cellsize + rnd_points[ (x + y * x_cells) * 2 + 1],
      ],
  ];

// Function: NormalizeVector()
// Description:
//    Normalizes the vector to a size of 1, but keeps the relative sizes.
function NormalizeVector(v) = v / (sqrt(v[0] * v[0] + v[1] * v[1]));

// Module: Vornonoi()
// Description:
//   Creates a voronoi pattern to use on lids (and elsewhere).
// Arguments:
//   width = width of the space to fill
//   length = length of the space to fill
//   thickness = thickness of the gaps between the shapes
//   corner_size = how much rounding to use in the corners
//   cellsize = the size of the cells in the space
//   seed = the seed to use for the random number (degault {{default_voronoi_seed}})
//   allowable = how much space to randomize within the cell
// Example:
//   Voronoi(width=100, length=100, thickness=1.5);
module Voronoi(
  width,
  length,
  thickness,
  corner_size = 1,
  cellsize = 10,
  seed = default_voronoi_seed,
  allowable = 0.99
) {
  assert(width != 0, "Need to have a width specified");
  assert(length != 0, "Need to have a length specified");
  assert(thickness != 0, "Need to have a thickness specified");

  points = VoronoiPoints(width=width, length=length, cellsize=cellsize, seed=seed, allowable=allowable);
  bounding_box = 2.1 * sqrt(2) * cellsize;
  bounding_box_square = bounding_box * bounding_box;
  difference() {
    square([width, length]);
    offset(r=corner_size, $fn=16) {
      for (p1 = points) {
        intersection_for (p2 = points) {
          diff = p2 - p1;
          if (p1 != p2 && diff[0] * diff[0] + diff[1] * diff[1] <= bounding_box_square) {
            angle = 90 + atan2(p1[1] - p2[1], p1[0] - p2[0]);
            translate((p1 + p2) / 2 - NormalizeVector(p2 - p1) * (thickness / 2 + corner_size)) {
              rotate([0, 0, angle]) {
                translate([-bounding_box, -bounding_box]) {
                  square([bounding_box * 2, bounding_box]);
                }
              }
            }
          }
        }
      }
    }
  }
}

// Module: HexagonalTesselation()
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
module HexagonalTesselation(points, radius = 10) {
  assert(len(points) == 3, str("points must have three arrays", points));
  for (c = [0:len(points) - 1]) {
    assert(len(points[c]) > 1, str("Each array must have more than two elements", points[c]));
  }
  side_length = 2 * radius * sin(30);
  apothem = sqrt(3) / 2 * side_length;
  function GenerateEdge(pts) = [for (i = [0:len(pts) - 1]) (pts[i] * side_length)];

  // List of 3 sets of points to work as the exterior points on the line
  // represented as a percentage of the side.

  poly = [
    for (i = [0:5]) each move(
      rot(a=60 * i, p=[[apothem, 0]])[0],
      rot(a=60 * i + 90, p=GenerateEdge(pts=i % 2 == 0 ? reverse(rot(a=180, p=points[i / 2 % 3])) : points[i / 2 % 3]))
    ),
  ];
  polygon(poly);
}

// Module: SquareTesselation()
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
module SquareTesselation(points, size, thickness = 0, outer_offset = 0) {
  assert(size != 0, "Need to have a size specified");
  assert(len(points) == 2, str("Input points must be of size 2", points));
  assert(len(size) == 2, str("Input size must be of form [x,y]", size));

  function GenerateEdge(pts, side_length) = [for (i = [0:len(pts) - 1]) (pts[i] * side_length)];

  width = size[0];
  length = size[1];
  length_line = GenerateEdge(points[0], length);
  width_line = GenerateEdge(points[1], width);
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

// Module: EscherLizardHexTesselation()
// Description:
//    A hex tesselation of the esched lizard, this can be rotated and used
//    to fill in hex spaces when doing tesselations.
// Arguments:
//    radius = the radius of the hex to use
// Example:
//    EscherLizardHexTesselation(radius=29);
module EscherLizardHexTesselation(radius, thickness = 0, outer_offset = 0) {
  assert(radius != 0, "Need to have a radius specified");
  top = [
    [-0.5, 0.0],
    [-0.15, -0.3],
    [-0.0, -0.3],
    [0.25, -0.05],
    [0.05, 0.35],
    [0.2, 0.4],
    [0.45, 0.35],
    [0.45, 0.2],
    [0.35, 0.15],
    [0.5, 0.0],
  ];
  tail = [
    [-0.5, 0],
    [-0.65, -0.35],
    [-0.4, -0.35],
    [-0.25, -0.25],
    [0, -0.2],
    [0.1, 0],
    [0.05, 0.3],
    [-0.15, 0.5],
    [0.25, 0.35],
    [0.35, 0.1],
    [0.4, 0.0],
  ];
  other_leg = [
    [-0.5, 0],
    [-0.35, -0.25],
    [-0.35, -0.55],
    [-0.05, -0.45],
    [-0.15, -0.05],
    [0.15, 0.05],
    [0.3, 0.15],
    [0.5, 0],
  ];
  difference() {
    offset(outer_offset)
      HexagonalTesselation(
        points=[
          tail,
          top,
          other_leg,
        ],
        radius=radius
      );
    if (thickness > 0) {
      offset(-thickness)
        HexagonalTesselation(
          points=[
            tail,
            top,
            other_leg,
          ],
          radius=radius
        );
    }
  }
}

// Module: TesselationDrop()
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
  assert(size != 0, "Need to have a size specified");
  SquareTesselation(
    points=[
      arc(n=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]]),
      arc(n=arc_points, points=[[-0.5, 0], [0, arc_offset], [0.5, 0]]),
    ],
    size=size, thickness=thickness, outer_offset=outer_offset
  );
}

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

// Module: TesselationLeafOutline()
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
  module MakePolygon() {
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
  module MakeVeins() {
    vein_base_x = -section_height * 2 + calc_thickness;
    vein_side_x = calc_vein_thickness / 2;
    vein_side_y = section * 2 - calc_vein_thickness;
    stroke(
      [
        [vein_base_x, 0],
        [section_height * 2 - calc_thickness, 0],
      ],
      width=calc_vein_thickness
    );
    stroke(
      [
        [vein_base_x, 0],
        [vein_side_x, vein_side_y],
      ],
      width=calc_vein_thickness
    );
    stroke(
      [
        [vein_base_x, 0],
        [-vein_side_x, -vein_side_y],
      ],
      width=calc_vein_thickness
    );
    vein_spacing = section_height * 3 / 2 / 3;
    len_bottom_vein = sqrt(
      sqr(vein_base_x - vein_side_x) + sqr(vein_side_y)
    );
    line_m = (vein_side_x - vein_base_x) / (vein_side_y);
    line_angle = atan(line_m);
    mini_seg = len_bottom_vein / 7;
    intersection() {
      for (i = [0:3]) {
        stroke(
          [
            [section_height - section_height * 4 / 2 + vein_spacing * i, 0],
            [section_height - section_height * 3 / 2 + 20 + vein_spacing * i, 15],
          ], width=calc_vein_thickness
        );
        stroke(
          [
            [section_height - section_height * 4 / 2 + vein_spacing * i, 0],
            [section_height - section_height * 3 / 2 + 20 + vein_spacing * i, -15],
          ], width=calc_vein_thickness
        );
        translate([vein_base_x, 0]) rotate((90 - line_angle)) {
            stroke(
              [
                [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                [mini_seg * (i + 2) + mini_seg * 3, -mini_seg * 2.5 - calc_vein_thickness / 4],
              ], width=calc_vein_thickness
            );
          }
        translate([vein_base_x, 0]) rotate(90 - line_angle) {
            stroke(
              [
                [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                [mini_seg * (i + 2) + mini_seg * 3, mini_seg * 2 + calc_vein_thickness / 4],
              ], width=calc_vein_thickness
            );
          }
        translate([vein_base_x, 0]) rotate(-(90 - line_angle)) {
            stroke(
              [
                [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                [mini_seg * (i + 2) + mini_seg * 3, -mini_seg * 2],
              ], width=calc_vein_thickness
            );
          }
        translate([vein_base_x, 0]) rotate(-(90 - line_angle)) {
            stroke(
              [
                [mini_seg * (i + 1.2), -calc_vein_thickness / 4],
                [mini_seg * (i + 2) + mini_seg * 3, mini_seg * 2.5 + calc_vein_thickness / 4],
              ], width=calc_vein_thickness
            );
          }
      }
      MakePolygon();
    }
  }
  calc_thickness = DefaultValue(thickness, size / 30);
  calc_vein_thickness = DefaultValue(vein_thickness, calc_thickness / 2);
  section = size / 4;
  section_height = section * calc_sqrt_three / 2;
  union() {
    difference() {
      MakePolygon();
      offset(-calc_thickness) MakePolygon();
    }
    if (with_veins) {
      MakeVeins();
    }
  }
}

// Module: TesselationLeafOutlineThree()
// Description:
//   A leaf outline for use with tesselations, this groups into three
//   to make layout a lot easier.
// Arguments:
//   size = size of the leaf
//   thickness = thickness of the sides
//   with_veins = show veins in the leaf
//   vein_thickness = how thick the veins in the lid are
module TesselationLeafOutlineThree(size, thickness = undef, with_veins = false, vein_thickness = undef) {
  assert(size != 0, "Need to have a size specified");
  section = size / 4;
  section_height = section * calc_sqrt_three / 2;

  translate([0, -section * 3 / 2])
    TesselationLeafOutline(
      size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
    );
  translate([-section_height * 2, section * 3 / 2])
    rotate(180)
      TesselationLeafOutline(
        size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
      );
  translate([section_height * 2, section / 2])
    TesselationLeafOutline(
      size=size, thickness=thickness, with_veins=with_veins, vein_thickness=vein_thickness
    );
}

// Module: DeltoidTrihexagonalTiling()
// Description:
//   A tesselation to use with the layout to make nice triagnel layout hex
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
module DeltoidTrihexagonalTiling(size, thickness = 1, outer_offset = 0, kite = false) {
  assert(size != 0, "Need to have a size specified");
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
  function GetPoints(pts, i) = kite ? [pts[i], (pts[ (i + 1) % 6] + pts[i]) / 2, [0, 0], (pts[ (i + 5) % 6] + pts[i]) / 2] : [pts[i], pts[ (i + 1) % 6], [0, 0]];
  module InnerParts() {
    union() {
      for (i = [0:5]) {
        difference() {

          offset(thickness / 10)
            polygon(
              GetPoints(pts, i)
            );
          offset(delta=-thickness)
            polygon(
              GetPoints(pts, i)
            );
        }
      }
    }
  }
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

// Module: HalfRegularHexagon()
// Description:
//   A half regular hexagon to use with the layout to make nice layout.
//   This is actually based on a triangle tesselation with rotations
// Arguments:
//   size = size of the hex
//   thickness = thickness of the sides
//   outer_offset = how much to offset the outside edge
// Example:
//   HalfRegularHexagon(20);
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

// Module: RhombiTriHexagonal()
// Description:
//   A rhombitrihexagon layout, which makes a nifty tesselation.
//   This is actually based on a triangle tesselation with rotations
// Arguments:
//   size = size of the hex
//   thickness = thickness of the sides
//   outer_offset = how much to offset the outside edge
// Example:
//   RhombiTriHexagonal(20);
module RhombiTriHexagonal(size, thickness = 1, outer_offset = 0.1) {
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
