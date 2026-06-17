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

// LibFile: voronoi.scad
//    This file has all the modules needed to make voronoi tesselations.

// Includes:
//   include <boardgame_toolkit.scad>


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

// Function&Module: Vornonoi()
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
// Example:
//   region(Voronoi(width=100, length=100, thickness=1.5));
module Voronoi(
  width,
  length,
  thickness,
  corner_size = 1,
  cellsize = 10,
  seed = default_voronoi_seed,
  allowable = 0.99
) {
  assert(width > 0, "Need to have a width specified");
  assert(length > 0, "Need to have a length specified");
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

function Voronoi(
  width,
  length,
  thickness,
  corner_size = 1,
  cellsize = 10,
  seed = default_voronoi_seed,
  allowable = 0.99
) =
  assert(width != 0, "Need to have a width specified")
  assert(length != 0, "Need to have a length specified")
  assert(thickness != 0, "Need to have a thickness specified")
  let (
    points = VoronoiPoints(width=width, length=length, cellsize=cellsize, seed=seed, allowable=allowable),
    bounding_box = 2.1 * sqrt(2) * cellsize,
    bounding_box_square = bounding_box * bounding_box,
  ) difference(
    square([width, length]),
    offset(
      union(
        [
          for (p1 = points) intersection(
            [
              for (p2 = points) if ( (p1 != p2 && (p2 - p1) [0] * (p2 - p1) [0] + (p2 - p1) [1] * (p2 - p1) [1] <= bounding_box_square) ) let (
                angle = 90 + atan2(p1[1] - p2[1], p1[0] - p2[0])
              ) move(
                (p1 + p2) / 2 - NormalizeVector(p2 - p1) * (thickness / 2 + corner_size),
                rot(
                  a=angle, p=move(
                    [-bounding_box, -bounding_box],
                    square([bounding_box * 2, bounding_box])
                  )
                )
              ),
            ]
          ),
        ]
      ), r=corner_size, $fn=16
    )
  );