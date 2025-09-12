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
//    EscherLizardSingle(size=20);
module EscherLizardSingle(size) {
  EscherLizardHexTesselation(radius=size / 2);
}

// Module: EscherLizardTrangle()
// Description:
//    Makes the triangle that can be used to fill in the lizard
//    tesselation in a wider group.  This will not need to be
//    rotated.
// Arguments:
//    size = size the lizard
//    thickness = thickness of the walls/edges
// Example:
//    EscherLizardTriangle(size=20, thickness=1);
module EscherLizardTriangle(size, thickness) {
  module SingleLizard() {
    difference() {
      offset(delta=0.05, chamfer=true)
        EscherLizardHexTesselation(radius=size / 2);
      offset(delta=-thickness, chamfer=true) EscherLizardHexTesselation(radius=size / 2);
    }
  }

  side_length = 2 * size * sin(30);
  apothem = sqrt(3) / 2 * side_length;

  translate([-apothem / 2, size]) {
    union() {
      SingleLizard();
      translate(
        [apothem / 2, size * 3 / 4]
      )
        rotate(240)
          SingleLizard();

      translate(
        [
          apothem,
          0,
        ]
      )
        rotate(120)
          SingleLizard();
    }
  }
}

// Module: EscherLizardSingleOutline()
// Description:
//   Creates a single escher lizard with an outline.
// Arguments:
//   size = the size of the lizard
// Example:
//    EscherLizardSingleOutline(size=20, thickness=1);
module EscherLizardSingleOutline(size, thickness) {
  difference() {
    EscherLizardSingle(size=size);
    offset(-thickness) EscherLizardSingle(size=size);
  }
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
// Example:
//    EscherLizardRepeatAtLocation(x=0, y=0, size=20, thickness=1);
module EscherLizardRepeatAtLocation(x, y, size, thickness) {
  radius = size / 2;
  shape_edges = 3;
  side_length = radius * sqrt(3);
  apothem = sqrt(3) / 2 * side_length;
  extra_edge = 2 * side_length * cos(360 / shape_edges);
  triangle_height = sqrt(3) / 2 * side_length;

  dx = apothem * 2;
  col_x = apothem + radius;
  dy = radius * 4 + apothem * 0.8;

  translate([x / 2 * dy, y * dx + ( (x + 1) % 2) * (dx / 2)]) {
    EscherLizardTriangle(size=size, thickness=thickness);
  }
}

// Module: EscherLizardRepeat()
// Description:
//   Creates an escher lizard blob that can be repeated.
// Arguments:
//   size = the size of the lizard
// Example:
//    EscherLizardRepeat(rows=4, cols=4, size=20, thickness=1);
module EscherLizardRepeat(rows, cols, size, thickness) {
  // Magic numbers, yay.
  radius = size / 2;
  shape_edges = 3;
  side_length = radius * sqrt(3);
  apothem = sqrt(3) / 2 * side_length;
  extra_edge = 2 * side_length * cos(360 / shape_edges);
  triangle_height = sqrt(3) / 2 * side_length;

  dx = apothem * 2;
  col_x = apothem + radius;
  dy = radius * 4 + apothem * 0.8;

  for (i = [0:rows - 1]) {
    for (j = [0:cols - 1]) {
      translate([i / 2 * dy, j * dx + ( (i + 1) % 2) * (dx / 2)]) {
        EscherLizardTriangle(size=size, thickness=thickness);
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
//    Voronoi(width=100, length=100, thickness=1.5);
module Voronoi(
  width,
  length,
  thickness,
  corner_size = 1,
  cellsize = 10,
  seed = default_voronoi_seed,
  allowable = 0.99
) {
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
  assert(len(points) == 3, "points must have three arrays");
  for (c = [0:len(points) - 1]) {
    assert(len(points[c]) > 1, "Each array must have more than two elements");
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

// Module: EscherLizardHexTesselation()
// Description:
//    A hex tesselation of the esched lizard, this can be rotated and used
//    to fill in hex spaces when doing tesselations.
// Arguments:
//    radius = the radius of the hex to use
// Example:
//    EscherLizardHexTesselation(radius=29);
module EscherLizardHexTesselation(radius) {
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
  HexagonalTesselation(
    points=[
      tail,
      top,
      other_leg,
    ],
    radius=radius
  );
}
