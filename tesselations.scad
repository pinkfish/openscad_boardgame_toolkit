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

escher_lizard_points =
[
  [14.54, 26.29],
  [12.63, 29.6],
  [15.62, 34.88],
  [26.43, 30.43],
  [28.0, 27.22],
  [14.86, 17.16],
  [16.24, 2.83],
  [20.92, 0.0],
  [37.7, 4.76],
  [41.97, 21.66],
  [46.75, 24.28],
  [59.82, 18.32],
  [61.97, 1.91],
  [65.56, 1.66],
  [74.84, 8.82],
  [71.74, 14.07],
  [67.93, 14.07],
  [67.58, 25.06],
  [52.81, 31.38],
  [47.37, 45.22],
  [55.94, 37.25],
  [67.65, 35.17],
  [73.29, 38.25],
  [75.31, 48.91],
  [79.69, 52.68],
  [79.35, 63.07],
  [67.8, 56.94],
  [67.34, 43.9],
  [58.21, 48.78],
  [57.13, 54.46],
  [48.92, 61.53],
  [49.07, 67.94],
  [56.71, 77.04],
  [65.41, 79.7],
  [68.43, 80.49],
  [53.19, 82.72],
  [40.31, 73.08],
  [36.18, 65.48],
  [28.81, 65.88],
  [18.22, 62.8],
  [12.57, 80.7],
  [0.0, 78.14],
  [5.4, 69.7],
  [7.57, 56.92],
  [19.72, 52.41],
  [29.7, 52.86],
  [25.65, 40.74],
  [7.33, 44.8],
  [4.69, 34.07],
  [0.66, 27.89],
  [5.18, 20.48],
];

function EscherLizardSize() =
  [
    max(
      [for (i = [0:len(escher_lizard_points) - 1]) escher_lizard_points[i][0]]
    ),
    max(
      [for (i = [0:len(escher_lizard_points) - 1]) escher_lizard_points[i][1]],
    ),
  ];

// Module: EscherLizardSingle()
// Description:
//   Creates a single escher lizard.
// Arguments:
//   size = the size of the lizard
module EscherLizardSingle(size) {
  escher_size = EscherLizardSize();

  ratio = escher_size[1] / escher_size[0];
  centroid = [
    -(escher_lizard_points[8][0] + escher_lizard_points[26][0] + escher_lizard_points[43][0]) / 3,
    -(escher_lizard_points[8][1] + escher_lizard_points[26][1] + escher_lizard_points[43][1]) / 3,
  ];
  resize([size, size * ratio])
    translate(centroid) {
      polygon(escher_lizard_points);

      color("red") polygon(
          [
            escher_lizard_points[8],
            escher_lizard_points[26],
            escher_lizard_points[43],
            escher_lizard_points[8],
          ]
        );
    }
}

// Module: EscherLizardTrangle()
// Description:
//    Makes the triangle that can be used to fill in the lizard
//    tesselation in a wider group.  This will not need to be
//    rotated.
// Arguments:
//    size = size the lizard
//    thickness = thickness of the walls/edges
module EscherLizardTriangle(size, thickness) {
  module SingleLizard() {

    translate(centroid) {

      difference() {
        polygon(escher_lizard_points);
        offset(-thickness / scale_size) polygon(escher_lizard_points);
      }
    }
  }

  escher_size = EscherLizardSize();
  scale_size = size / escher_size[0];

  ratio = escher_size[1] / escher_size[0];
  p8 = escher_lizard_points[8];
  p26 = escher_lizard_points[26];
  p42 = escher_lizard_points[43];
  centroid = [
    -(p8[0] + p26[0] + p42[0]) / 3,
    -(p8[1] + p26[1] + p42[1]) / 3,
  ];
  scale([scale_size, scale_size]) {
    SingleLizard();
    translate(
      p26 - p8
    )
      rotate(240)
        SingleLizard();

    translate(
      [
        ( (p26[0] - p42[0]) ),
        ( (p26[1] - p42[1]) ),
      ]
    )
      rotate(120)
        SingleLizard();
  }
}

// Module: EscherLizardSingleOutline()
// Description:
//   Creates a single escher lizard with an outline.
// Arguments:
//   size = the size of the lizard
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
module EscherLizardRepeatAtLocation(x, y, size, thickness) {
  escher_size = EscherLizardSize();
  p8 = escher_lizard_points[8];
  p26 = escher_lizard_points[26];
  p42 = escher_lizard_points[43];
  centroid = [
    -(p8[0] + p26[0] + p42[0]) / 3,
    -(p8[1] + p26[1] + p42[1]) / 3,
  ];
  scale_size = size / escher_size[0];

  // Magic numbers, yay.
  radius = size * 1.558;
  shape_edges = 3;
  apothem = radius * cos(180 / shape_edges);
  side_length = (shape_edges == 3) ? radius * sqrt(3) : 2 * apothem * tan(180 / shape_edges);
  extra_edge = 2 * side_length * cos(360 / shape_edges);
  triangle_height = sqrt(3) / 2 * side_length;

  // This number here is a bit iffy, but it would be based on some real data.
  dx = side_length * 0.775;
  col_x = apothem + radius;
  // This number here is a bit iffy, but it would be based on some real data.
  dy = (shape_edges == 3) ? triangle_height * 1.552 : 0.75 * (radius + radius);

  translate([x / 2 * dy, y * dx + ( (x + 1) % 2) * (dx / 2), 0]) {
    EscherLizardTriangle(size=size * 1.6, thickness=thickness);
  }
}

// Module: EscherLizardRepeat()
// Description:
//   Creates an escher lizard blob that can be repeated.
// Arguments:
//   size = the size of the lizard
module EscherLizardRepeat(rows, cols, size, thickness) {
  escher_size = EscherLizardSize();
  p8 = escher_lizard_points[8];
  p26 = escher_lizard_points[26];
  p42 = escher_lizard_points[43];
  centroid = [
    -(p8[0] + p26[0] + p42[0]) / 3,
    -(p8[1] + p26[1] + p42[1]) / 3,
  ];
  scale_size = size / escher_size[0];

  // Magic numbers, yay.
  radius = size * 1.558;
  shape_edges = 3;
  apothem = radius * cos(180 / shape_edges);
  side_length = (shape_edges == 3) ? radius * sqrt(3) : 2 * apothem * tan(180 / shape_edges);
  extra_edge = 2 * side_length * cos(360 / shape_edges);
  triangle_height = sqrt(3) / 2 * side_length;

  // This number here is a bit iffy, but it would be based on some real data.
  dx = side_length * 0.775;
  col_x = apothem + radius;
  // This number here is a bit iffy, but it would be based on some real data.
  dy = (shape_edges == 3) ? triangle_height * 1.552 : 0.75 * (radius + radius);

  for (i = [0:rows - 1]) {
    for (j = [0:cols - 1]) {
      translate([i / 2 * dy, j * dx + ( (i + 1) % 2) * (dx / 2), 0]) {
        EscherLizardTriangle(size=size * 1.6, thickness=thickness);
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
