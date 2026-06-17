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

// LibFile: quad_tesselations.scad
//    This file has all the modules needed to make a variety of tesselations.

// Includes:
//   include <boardgame_toolkit.scad>

// Function: QuadrilateralCoords()
// Description:
//   Computes the four 2-D vertices [P0, P1, P2, P3] of a quadrilateral given
//   its four interior angles and the length of one side.
//
//   The quadrilateral is placed with P0 at the origin and side P0→P1 along
//   the positive x-axis.  Because a quadrilateral with four known angles still
//   has one free degree of freedom (unlike a triangle), the parameter
//   `side_ratio` sets the ratio of the second side (P1→P2) to the first side.
//   All four interior angles must sum to 360°.
//
//   Algorithm:
//     1. Fix P0=[0,0] and P1=[side,0].
//     2. Accumulate edge directions by turning the exterior angle (180°−angle)
//        at each successive vertex.
//     3. With t2 = side_ratio * side known, solve the 2×2 linear system
//        t3·d̂₂ + t4·d̂₃ = −P2  to find the remaining side lengths t3 and t4,
//        where d̂ᵢ is the unit direction vector for each edge.
//     4. Walk the boundary to yield P2 and P3.
//
// Arguments:
//   angles     = Four interior angles [a0, a1, a2, a3] in degrees, one per
//                vertex.  Must sum to 360.
//   side       = Length of side P0→P1.
//   side_ratio = Ratio of side P1→P2 to side P0→P1.  Adjusting this parameter
//                slides through the family of valid quadrilaterals that share
//                the same four angles.  Default: 1 (equal adjacent sides).
// Example:
//   polygon(QuadrilateralCoords(angles=[90, 90, 90, 90], side=20));
// Example:
//   polygon(QuadrilateralCoords(angles=[70, 110, 70, 110], side=20));
// Example:
//   polygon(QuadrilateralCoords(angles=[60, 120, 60, 120], side=20, side_ratio=1.5));
function QuadrilateralCoords(angles, side, side_ratio = 1) =
  assert(len(angles) == 4, "angles must be a list of exactly four values")
  assert(
    abs(angles[0] + angles[1] + angles[2] + angles[3] - 360) < 1e-6,
    str("Interior angles must sum to 360°, got ", angles[0] + angles[1] + angles[2] + angles[3])
  )
  assert(side > 0, "side must be positive")
  assert(side_ratio > 0, "side_ratio must be positive")
  let (
    // Fixed vertices
    P0 = [0, 0],
    P1 = [side, 0],

    // Accumulated edge directions (exterior turn = 180° − interior angle).
    // dir0 = 0° (P0→P1 along +x).
    // At each vertex we turn left by the exterior angle.
    dir1 = 180 - angles[1], // direction of P1→P2
    dir2 = dir1 + (180 - angles[2]), // direction of P2→P3
    dir3 = dir2 + (180 - angles[3]), // direction of P3→P0

    // Unit direction vectors for edges 1→2, 2→3, 3→0
    d1 = [cos(dir1), sin(dir1)],
    d2 = [cos(dir2), sin(dir2)],
    d3 = [cos(dir3), sin(dir3)],

    // P2 is known once t2 = side_ratio * side is fixed
    t2 = side_ratio * side,
    P2 = P1 + t2 * d1,

    // Solve  t3 * d2 + t4 * d3 = P0 - P2  (closing condition)
    //   | d2x  d3x | | t3 |   | -P2x |
    //   | d2y  d3y | | t4 | = | -P2y |
    det = d2[0] * d3[1] - d3[0] * d2[1],
    rhs_x = -P2[0],
    rhs_y = -P2[1],
    t3 = (rhs_x * d3[1] - d3[0] * rhs_y) / det,
    t4 = (d2[0] * rhs_y - rhs_x * d2[1]) / det,
    P3 = P2 + t3 * d2
  ) assert(det != 0, "Degenerate quadrilateral: parallel opposite edges")
  assert(t3 > 0, str("Invalid quadrilateral geometry: side P2→P3 length is non-positive (", t3, "). Try a different side_ratio."))
  assert(t4 > 0, str("Invalid quadrilateral geometry: side P3→P0 length is non-positive (", t4, "). Try a different side_ratio."))
  [P0, P1, P2, P3];

// Function: TesselationFromQuadradicPoints()
// Description:
//    Make a nice tesselation from a set of points and sides.
// Arguments:
//    points = the quad points
//    side1 = the line for the one side, [-0.5, x] - [0.5, x]
//    side2 = the line for the one side, [-0.5, x] - [0.5, x]
//    side3 = the line for the one side, [-0.5, x] - [0.5, x]
//    side4 = the line for the one side, [-0.5, x] - [0.5, x]
function TesselationFromQuadradicPoints(points, side1, side2, side3, side4) =
  let (
  ) path_merge_collinear(
    [
      each TesselationSideLine([points[0], points[1]], side1, TESSELATION_LINE_NORMAL),
      each TesselationSideLine([points[1], points[2]], side2, TESSELATION_LINE_NORMAL),
      each TesselationSideLine([points[2], points[3]], side3, TESSELATION_LINE_NORMAL),
      each TesselationSideLine([points[len(points) - 1], points[0]], side4, TESSELATION_LINE_NORMAL)
    ]
  );
