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

// LibFile: pentagons.scad
//    This file has all the modules needed to make a sheep tesselation.

// Includes:
//   include <boardgame_toolkit.scad>

// Function&Module: SheepTesselation()
// Description:
//    Make a sheep tesselation.
// Arguments:
//    size = length of the sheep
//    x = x location
//    y = y location
//    thickness = thickness of the sheep
// Example:
//    SheepTesselation(size=20, x=0, y=0, thickness=2);
module SheepTesselation(size, x, y, thickness) {
  data = SheepTesselation(size, x, y, thickness);
  translate(size * x * data.x_offset)
    translate(size * y * data.y_offset)
      region(
        data.points
      );
}

function SheepTesselation(size, x, y, thickness) =
  let (
    line3 = bezier_curve(
      flatten(
        [
          bez_begin([0, 0], -60, 0.4),
          bez_tang([0.4, -0.04], 0, 0.2, 0.5),
          bez_tang([0.8, -0.2], 0, 0.5, 0.2),
          bez_end([1, 0], 210, 0.2),
        ]
      ), 20
    ),
    line2 = bezier_curve(
      flatten(
        [
          bez_begin([0, 0], 0, 0.4),
          bez_tang([0.4, 0.0], 0, 0.1, 0.5),
          bez_tang([0.6, -0.04], 270, 0.1, 0.5),
          bez_tang([0.8, -0.3], 0, 0.5, 0.2),
          bez_tang([0.9, -0.3], 20, 0.5, 0.2),
          bez_end([1, 0], 300, 0.3),
        ]
      ), 20
    ),
    line1 = [[0, 0], [1, 0]],
  ) PentagonTesselation(
    "R2", size, x, y, thickness,
    first_angle_modifier=-50, second_angle_modifier=0,
    first_length_modifier=0.5,
    second_length_modifier=0,
    third_length_modifier=0,
    line1=line1,
    line2=line2,
    line3=reverse([for (i = line3) [abs(i[0] - 1), i[1]]])
  );

// Module: SheepTesselationArea()
// Description:
//    Make a sheep tesselation area.
// Arguments:
//    size = length of the sheep
//    width = width of the space
//    length = length of the space
//    thickness = thickness of the sheep
// Example:
//    SheepTesselationArea(size=20, width=200, length=100, thickness=1);
module SheepTesselationArea(size, width, length, thickness) {
  data = SheepTesselation(
    size, 0, 0, thickness
  );

  rows = floor(width / (max(abs(data.x_offset[0]), abs(data.y_offset[0])) * size)) + 2;
  cols = floor(length / (max(abs(data.x_offset[1]), abs(data.y_offset[1])) * size)) * 8 / 4 + 1;
  x_offset = [data.x_offset[0], -data.x_offset[1]];
  y_offset = [data.y_offset[0], -data.y_offset[1]];
  fix_y_offset = [-data.y_offset[0], 0];

  translate([-cols * size, -size * 3 / 4])for (x = [0:rows])
    for (y = [0:cols])
      translate(size * x * x_offset)
        translate(size * y * y_offset)
          region(data.points);
}
