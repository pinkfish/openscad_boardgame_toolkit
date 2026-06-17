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

// Module: SheepTesselation()
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
  line3 = [
    [0, 0],
    [0.01, -0.04],
    [0.02, -0.08],
    [0.05, -0.11],
    [0.09, -0.18],
    [0.18, -0.18],
    [0.25, -0.14],
    [0.33, -0.1],
    [0.41, -0.07],
    [0.49, -0.07],
    [0.56, -0.11],
    [0.68, -0.17],
    [0.71, -0.19],
    [0.74, -0.19],
    [0.77, -0.18],
    [0.85, -0.15],
    [0.92, -0.11],
    [0.98, -0.04],
    [0.99, -0.03],
    [1, -0.02],
    [1, 0],
  ];
  line2 = [
    [0, 0],
    [0.07, 0],
    [0.13, 0],
    [0.19, -0.03],
    [0.36, -0.08],
    [0.29, -0.28],
    [0.35, -0.39],
    [0.44, -0.56],
    [0.67, -0.53],
    [0.83, -0.45],
    [0.91, -0.42],
    [0.98, -0.37],
    [1.03, -0.3],
    [1.06, -0.26],
    [1.07, -0.22],
    [1.06, -0.17],
    [1.06, -0.11],
    [1.03, -0.06],
    [1, 0],
  ];
  line1 = [[0, 0], [1, 0]];
  echo([size, y, y]);

  PentagonTesselation(
    "R2", size, x, y, thickness,
    first_angle_modifier=-45, second_angle_modifier=5,
    first_length_modifier=0.5,
    second_length_modifier=0,
    third_length_modifier=0,
    line1=line1,
    line2=line2,
    line3=reverse([for (i = line3) [abs(i[0] - 1), i[1]]])
  );
}

module SheepTesselationArea(size, width, length, thickness) {
  line3 = [
    [0, 0],
    [0.01, -0.04],
    [0.02, -0.08],
    [0.05, -0.11],
    [0.09, -0.18],
    [0.18, -0.18],
    [0.25, -0.14],
    [0.33, -0.1],
    [0.41, -0.07],
    [0.49, -0.07],
    [0.56, -0.11],
    [0.68, -0.17],
    [0.71, -0.19],
    [0.74, -0.19],
    [0.77, -0.18],
    [0.85, -0.15],
    [0.92, -0.11],
    [0.98, -0.04],
    [0.99, -0.03],
    [1, -0.02],
    [1, 0],
  ];
  line2 = [
    [0, 0],
    [0.07, 0],
    [0.13, 0],
    [0.19, -0.03],
    [0.36, -0.08],
    [0.29, -0.28],
    [0.35, -0.39],
    [0.44, -0.56],
    [0.67, -0.53],
    [0.83, -0.45],
    [0.91, -0.42],
    [0.98, -0.37],
    [1.03, -0.3],
    [1.06, -0.26],
    [1.07, -0.22],
    [1.06, -0.17],
    [1.06, -0.11],
    [1.03, -0.06],
    [1, 0],
  ];
  line1 = [[0, 0], [1, 0]];

  data = PentagonTesselation(
    "R2", pentagon_size=size, x=0, y=0, thickness=thickness,
    first_angle_modifier=-45, second_angle_modifier=5,
    first_length_modifier=0.5,
    second_length_modifier=0,
    third_length_modifier=0,
    line1=line1,
    line2=line2,
    line3=reverse([for (i = line3) [abs(i[0] - 1), i[1]]])
  );

  echo("x", data.x_offset, "y", data.y_offset);
  rows = floor(width / (max(abs(data.x_offset[0]), abs(data.y_offset[0])) * size)) + 1;
  cols = floor(length / (max(abs(data.x_offset[1]), abs(data.y_offset[1])) * size)) * 8 / 4;
  echo([rows, cols]);
  x_offset = [data.x_offset[0], -data.x_offset[1]];
  y_offset = [data.y_offset[0], -data.y_offset[1]];
  fix_y_offset = [-data.y_offset[0], 0];

  translate([-rows * size, 0])for (x = [0:rows])
    for (y = [0:cols])
      translate(size * x * x_offset)
        translate(size * y * y_offset)
          region(data.points);
}
