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

// LibFile: goose.scad
//    This file has all the modules needed to make a goose tesselation.

// Includes:
//   include <boardgame_toolkit.scad>

TESSELATION_GOOSE_SIDE = 30;
TESSELATION_GOOSE_MIDDLE = 3;

// Module: TesselationGoose()
// Description:
//    The nice goose shape.
// Arguments:
//    flip = flip the tail end
//    size = size of the hex
//    thickness = thickness of the sides
// Example:
//    TesselationGoose(size=20);
// Example:
//    TesselationGoose(size=20, thickness=0.5);
module TesselationGoose(flip = false, size = 100, thickness = 0, outer_offset = 0) {

  line_a = [[0, 0], [0.4, -0.25], [0.5, 0], [0.6, 0.25], [1, 0]];
  line_b = [[0, 0], [1, 0]];
  line2 = flip ? line_b : line_a;
  line3 = flip ? [for (i = line_a) [i[0], -i[1]]] : line_b;
  ratio = size / 100;

  DifferenceWithOffset(offset=-thickness, outer_offset=outer_offset) {
    polygon(
      path_merge_collinear(
        path=TesselationFromQuadradicPoints(
          [
            [0, 0],
            [100 * ratio, TESSELATION_GOOSE_SIDE * ratio],
            [(100 - TESSELATION_GOOSE_MIDDLE) * ratio, (flip ? TESSELATION_GOOSE_MIDDLE : -TESSELATION_GOOSE_MIDDLE) * ratio],
            [100 * ratio, -TESSELATION_GOOSE_SIDE * ratio],
          ],
          [
            [0, 0],
            [0.213176, -0.056018],
            [0.406283, -0.07],
            [0.56471, 0.0733724],
            [0.693585, 0.0370756],
            [0.761958, -0.0107027],
            [1, 0],
          ],
          line2,
          line3,
          [
            [0, 0],
            [0.213176, 0.056018],
            [0.406283, 0.07],
            [0.56471, -0.0733724],
            [0.693585, -0.0370756],
            [0.761958, 0.0107027],
            [1, 0],
          ],
        ),
        closed=true
      ),
    );
  }
}



// Module: TesselationGooseBlock()
// Description:
//    The nice goose shape.
// Arguments:
//    size = the size of the goose
//    thickness = the thickness of the goose
// Example:
//    TesselationGooseBlock(size=30, thickness=1);
// Example:
//    TesselationGooseBlock(size=20, thickness=0.5);
module TesselationGooseBlock(size, thickness, outer_offset = 0) {
  assert(size > 0, "need a size");
  assert(thickness >= 0, "need a thickness");
  ratio = size / 100;
  color("red")
    fwd(TESSELATION_GOOSE_SIDE * ratio)
      xflip()
        TesselationGoose(size=size, flip=false, thickness=thickness, outer_offset=outer_offset);
  color("cyan")
    back(TESSELATION_GOOSE_SIDE * ratio)
      xflip()
        TesselationGoose(size=size, flip=false, thickness=thickness, outer_offset=outer_offset);

  left(100 * ratio)
    fwd(0)
      color("purple")
        TesselationGoose(size=size, flip=true, thickness=thickness, outer_offset=outer_offset);
  left(100 * ratio)
    back(TESSELATION_GOOSE_SIDE * ratio * 2)
      color("magenta")
        TesselationGoose(size=size, flip=true, thickness=thickness, outer_offset=outer_offset);
}

// Module: TesselationGooseGrid()
// Description:
//    The nice goose shape.
// Arguments:
//    row = number of rows
//    col = number of columns
//    size = size of the goose
//    thickness = thickness of the goose
// Example:
//    TesselationGooseGrid(5, 5, size=30, thickness=1);
module TesselationGooseGrid(row, col, size, thickness, outer_offset = 0.1) {
  assert(row > 0, "Need a row");
  assert(col > 0, "Need a col");
  assert(size > 0, "Need a size");
  assert(thickness > 0, "Need a thickness");

  ratio = size / 100;
  for (i = [0:row])
    for (j = [0:col])
      union() {
        back(TESSELATION_GOOSE_MIDDLE / 4 * i)
          back((i + (TESSELATION_GOOSE_SIDE * 4) * j) * ratio)
            right((100 - TESSELATION_GOOSE_MIDDLE) * i * ratio)
              TesselationGooseBlock(size=size, thickness=thickness, outer_offset=outer_offset);
      }
}

// Module: TesselationGooseArea()
// Description:
//    The nice goose shape.
// Arguments:
//    width = width of the space
//    length = length of the space
//    size = size of the goose
//    thickness = thickness of the goose
// Example:
//    TesselationGooseArea(200, 100, size=50, thickness=2);
module TesselationGooseArea(width, length, size, thickness) {
  assert(width > 0, "Need a width");
  assert(length > 0, "Need a length");
  assert(size > 0, "Need a size");
  assert(thickness > 0, "Need a thickness");
  ratio = size / 100;
  calc_size = size - TESSELATION_GOOSE_MIDDLE;
  rows = floor(width / (calc_size * ratio) / 3 + 1);
  cols = floor(length / (TESSELATION_GOOSE_SIDE * 4 * ratio) + 1);
  back(-TESSELATION_GOOSE_MIDDLE * ratio * rows)
    TesselationGooseGrid(
      row=rows,
      col=cols,
      size=size,
      thickness=thickness,
      outer_offset=0.1
    );
}