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

// LibFile: lizard.scad
//    This file has all the modules needed to make lizard tesselations.

// Includes:
//   include <boardgame_toolkit.scad>

// Module: LizardSingle()
// Description:
//   Creates a single  lizard.
// Arguments:
//   size = the size of the lizard
// Example:
//   LizardSingle(size=20);
module LizardSingle(size) {
  assert(size > 0, "Need to have a size specified");
  polygon(
    LizardHexTesselation(radius=size / 2)
  );
}

// Function&Module: LizardTriangle()
// Description:
//    Makes the triangle that can be used to fill in the  lizard
//    tesselation in a wider group.  This will not need to be
//    rotated.
// Arguments:
//    size = size the hex
//    outer_offset = how much padding on the outside
// Example:
//    LizardTriangle(size=20, thickness=2);
// Example:
//    LizardTriangle(size=20, thickness=2, outer_offset=0.1);
// Example:
//    LizardTriangle(size=20);
module LizardTriangle(size, thickness = 0, outer_offset = 0) {
  region(
    HexagonalTesselationTriangle(
      size=size,
      LizardHexTesselation(radius=size / 2, thickness=thickness, outer_offset=outer_offset)
    )
  );
}

function LizardTriangle(size, thickness = 0, outer_offset = 0) =
  HexagonalTesselationTriangle(
    size=size,
    LizardHexTesselation(radius=size / 2, thickness=thickness, outer_offset=outer_offset)
  );

// Function&Module: HexagonalTesselationTriangle()
// Description:
//    Makes the triangle that can be used to fill in the hexagonal
//    rotated.
// Arguments:
//    size = size the hex
//    pts = points to use (only in function)
// Example:
//    HexagonalTesselationTriangle(size=20)
//       LizardHexTesselation(radius=10, thickness=1);
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

function HexagonalTesselationTriangle(size, pts) =
  let (
    side_length = 2 * size * sin(30),
    apothem = sqrt(3) / 2 * side_length,
    new_pts = move(
      [-apothem / 2, size],
      union(
        pts,
        move(
          [apothem / 2, size * 3 / 4],
          rot(p=pts, a=240)
        ),
        move(
          [
            apothem,
            0,
          ],
          rot(p=pts, a=120)
        )
      )
    )
  ) new_pts;

// Module: LizardSingleOutline()
// Description:
//   Creates a single  lizard with an outline.
// Arguments:
//   size = the size of the lizard
//   thickness = the thickness to use
// Example:
//   LizardSingleOutline(size=20, thickness=1);
module LizardSingleOutline(size, thickness) {
  assert(size > 0, str("Need to have a size specified size=", size));
  assert(thickness > 0, str("Need to have a thickness specified thickness=", thickness));
  region(
    LizardHexTesselation(radius=size / 2, thickness=thickness)
  );
}

// Function&Module: LizardRepeatAtLocation()
// Description:
//   Used to create an  lizard at a specific spot in a grid given an
//   x and a y location.
// Arguments:
//   x = the x location to generate at
//   y = the y location to generate at
//   size = the size of the lizard
//   thickness = the thickness of the lines
//   outer_offset = extra space to put around the shape.
// Example:
//   LizardRepeatAtLocation(x=0, y=0, size=20, thickness=1);
// Example:
//   LizardRepeatAtLocation(x=0, y=0, size=20, thickness=1, outer_offset=0.1);
// Example:
//   region(LizardRepeatAtLocation(x=0, y=0, size=20, thickness=1));
module LizardRepeatAtLocation(x, y, size, thickness, outer_offset = 0) {
  assert(x != undef, "Need to have a x specified");
  assert(y != undef, "Need to have a y specified");
  assert(size > 0, str("Need to have a size specified size=", size));

  HexagonTesselationRepeatAtLocation(x=x, y=y, size=size)
    LizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset);
}

function LizardRepeatAtLocation(x, y, size, thickness, outer_offset = 0) =
  assert(x != undef, "Need to have a x specified")
  assert(y != undef, "Need to have a y specified")
  assert(size > 0, str("Need to have a size specified size=", size))
  HexagonTesselationRepeatAtLocation(
    x=x, y=y, size=size, pts=LizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset)
  );

// Module: LizardRepeat()
// Description:
//   Creates an  lizard blob that can be repeated.
// Arguments:
//   rows = number of rows to generate
//   cols = number of columns to generate
//   size = the size of the lizard
//   thickness = the thickness of the lines
//   outer_offset = offset for the outer edge
// Example:
//   LizardRepeat(rows=4, cols=4, size=20, thickness=1);
module LizardRepeat(rows, cols, size, thickness, outer_offset = 0.01) {
  assert(rows > 0, "Need to have a rows specified");
  assert(cols > 0, "Need to have a cols specified");
  assert(size > 0, "Need to have a size specified");
  assert(thickness > 0, "Need to have a thickness specified");

  HexagonTesselationRepeat(rows=rows, cols=cols, size=size)
    LizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset);
}

_LIZARD_TOP = [
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
_LIZARD_TAIL = [
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
];
_LIZARD_OTHER_LEG = [
  [-0.5, 0],
  [-0.35, -0.25],
  [-0.35, -0.55],
  [-0.05, -0.45],
  [-0.15, -0.05],
  [0.15, 0.05],
  [0.3, 0.15],
  [0.5, 0],
];

// Function&Module: LizardHexTesselation()
// Description:
//    A hex tesselation of the esched lizard, this can be rotated and used
//    to fill in hex spaces when doing tesselations.
// Arguments:
//    thickness = thickness of the lines
//    outer_offset = extra space to put around the shape
//    radius = the radius of the hex to use
// Example:
//    LizardHexTesselation(radius=29);
// Example:
//    region(LizardHexTesselation(radius=29));
module LizardHexTesselation(radius, thickness = 0, outer_offset = 0) {
  assert(radius != 0, "Need to have a radius specified");

  difference() {
    offset(outer_offset)
      HexagonalTesselation(
        points=[
          _LIZARD_TAIL,
          _LIZARD_TOP,
          _LIZARD_OTHER_LEG,
        ],
        radius=radius
      );
    if (thickness > 0) {
      offset(-thickness)
        HexagonalTesselation(
          points=[
            _LIZARD_TAIL,
            _LIZARD_TOP,
            _LIZARD_OTHER_LEG,
          ],
          radius=radius
        );
    }
  }
}

function LizardHexTesselation(radius, thickness = 0, outer_offset = 0) =
  let (
    sized_lizard_points = path_merge_collinear(
      HexagonalTesselation(
        points=[
          _LIZARD_TAIL,
          _LIZARD_TOP,
          _LIZARD_OTHER_LEG,
        ],
        radius=radius
      ), closed=true
    ),
    outline = outer_offset == 0 && thickness == 0 ? sized_lizard_points
    : difference(
      offset(
        sized_lizard_points, delta=outer_offset
      ),
      thickness > 0 ?
        offset(
          sized_lizard_points, delta=-thickness
        )
      : []
    )
  ) outline;
