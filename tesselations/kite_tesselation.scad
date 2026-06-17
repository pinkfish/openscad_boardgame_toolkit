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

// LibFile: kite_tesselations.scad
//    This file has all the modules needed to make a variety of tesselations.

// Includes:
//   include <boardgame_toolkit.scad>

// Function: MakeTesselationKite()
// Description:
//    Make a kite tesselation.
// Arguments:
//    size = length of the kite
//    side1 = the line for the one side, [-0.5, x] - [0.5, x]
//    side2 = the line for the one side, [-0.5, x] - [0.5, x]
// Example:
//    polygon(MakeTesselationKite(
//      size=20,
//      [[-0.5, 0], [0.3, 0.25], [0.5, 0]],
//      [[-0.5, 0], [0.3, 0.25], [0.5, 0]]
//    ))
function MakeTesselationKite(size, side1, side2) =
  // 1:√3:2
  // a  = b * tan(30)
  // a = b1 * tan(60)
  // b = size - b1
  // (size - b1) * tan(15) = b1 * tan(60)
  // size*ten(15) - b1*tan(15) = b1 * tan(60)
  // size*ten(15) = b1*(tan(60) + tan(15))
  // b1 = size*ten(15) / (tan(60) + tan(15))
  let (
    b1 = (size * tan(30)) / (tan(60) + tan(30)),
    a = b1 * tan(60),
    small_c = sqrt(a * a + b1 * b1),
    long_c = sqrt(a * a + (size - b1) * (size - b1)),
    line_small = side1 * small_c,
    line_long = side2 * long_c,
    poly = move(
      [(size) / 2 - b1, 0],
      path_merge_collinear(
        path=concat(
          move([b1 / 2, -a / 2], rot(a=60, p=line_small)),
          reverse(move([b1 / 2, a / 2], rot(a=-60, p=line_small))),
          reverse(move([-(size - b1) / 2, a / 2], rot(a=30, p=line_long))),
          move([-(size - b1) / 2, -a / 2], rot(a=-30, p=line_long)),
        ),
        closed=true
      )
    )
  ) poly;

// Module: MakeTesselationKiteHexagon()
// Description:
//.   Make a kite tesselation hexagon.
// Arguments:
//    size = length of the kite
//    side1 = the line for the one side, [-0.5, x] - [0.5, x]
//    side2 = the line for the one side, [-0.5, x] - [0.5, x]
// Example:
//    MakeTesselationKiteHexagon(
//      size=20,
//      [[-0.5, 0], [0.3, 0.25], [0.5, 0]],
//      [[-0.5, 0], [0.3, 0.25], [0.5, 0]],
//      thickness=2,
//      outer_offset=0.1
//    );
module MakeTesselationKiteHexagon(size, side1, side2, thickness, outer_offset) {
  kites = MakeTesselationKite(size, side1, side2);

  for (i = [0:5])
    DifferenceWithOffset(
      outer_offset=outer_offset,
      offset=-thickness
    )
      region(
        rot(
          a=i * 60,
          p=right(
            size / 2,
            kites
          )
        ),
      );
}

// Module: TesselationHexKiteAtLocation()
// Description:
//    Show a tesselation kite hex at a specific location.
// Arguments:
//    size = size of the hex
//    x = x location
//    y = y location
// Example:
//    TesselationHexKiteAtLocation(size=20, x=0, y=0)
//      rotate(30)
//        TesselationChickenHex(size=20);
module TesselationHexKiteAtLocation(size, x, y) {
  radius = size;
  apothem = sqrt(radius * radius - (radius / 2) * (radius / 2));

  back(x * radius * 3 / 2)
    right(apothem * 2 * y + (x % 2) * apothem)
      children();
}

// Module: TesselationHexKiteArea()
// Description:
//    Show a tesselation kite hex at a specific location.
// Arguments:
//    size = size of the hex
//    width = width of the space
//    length = length of the space
// Example:
//    TesselationHexKiteArea(width=200, length=100, size=20)
//      rotate(30)
//        TesselationChickenHex(size=20);
module TesselationHexKiteArea(width, length, size) {
  apothem = sqrt(size * size - (size / 2) * (size / 2));

  rows = floor(width / (size * 4) + 1);
  cols = floor(length / (apothem * 2) + 3);

  left(size / 2)for (x = [0:rows])
    for (y = [0:cols])
      TesselationHexKiteAtLocation(size=size, x=x, y=y)
        children();
}
