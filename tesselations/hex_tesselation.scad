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

// LibFile: hex_tesselations.scad
//    This file has all the modules needed to make a variety of tesselations.

// Includes:
//   include <boardgame_toolkit.scad>

// Function: generate_hexagon()
// Description:
//     Function to calculate vertices for an irregular hexagon if you give the side_lengths and interor angles.
// Arguments:
//     side_lengths = the lengths of the sides to make the hex for, only 5 specified last one is calculated
//     interior_angles = the interior angles for use inside the hex, only 5 specified last one is caldulated
//     current_x = interal counter
//     current_y = interal counter
//     current_angle = interal counter
//     num = interal counter
function generate_hexagon(side_lengths, interior_angles, current_x = 0, current_y = 0, current_angle = 0, num = 0) =
  num >= len(side_lengths) ? [[0, 0]]
  : assert(
    sumVec(interior_angles) < 180 * (len(side_lengths) - 1), str(
      "Sum of angles less than  ",
      180 * (len(side_lengths) - 2)
    )
  )
  assert(len(interior_angles) == len(side_lengths), "Interial angle size and side length side sdhould be the same")
  let (
    new_angle = 180 - interior_angles[num] + current_angle,
    new_x = side_lengths[num] * cos(current_angle) + current_x,
    new_y = side_lengths[num] * sin(current_angle) + current_y
  ) concat(
    [[new_x, new_y]],
    generate_hexagon(
      side_lengths, interior_angles,
      current_x=new_x, current_y=new_y,
      current_angle=new_angle, num=num + 1
    )
  );

// Function&Module: FlyingBirdTesselation()
// Description:
//     Makes a hex sized flying bird tesselation.
// Arguments:
//     size = size of the bird
//     thickness = thickness of the bird (default 0)
// Example:
//     FlyingBirdTesselation(20);
// Example:
//     FlyingBirdTesselation(20, 2);
module FlyingBirdTesselation(size, x = 0, y = 0, thickness = 0, outer_offset = 0, spin = 0) {
  bird = FlyingBirdTesselation(size, thickness=thickness, outer_offset=outer_offset, spin=spin);
  translate(x * bird.x_vec)
    translate(y * bird.y_vec) {
      region(bird.pts);
    }
}

function FlyingBirdTesselation(size, thickness = 0, outer_offset = 0, spin = 0) =
  let (
    ratio = 1 / 22 * size,
    s1 = 15 * ratio, // Side 1 (Bottom)
    s2 = 15 * ratio, // Side 2
    s3 = 22 * ratio, // Side 3
    a1 = 170,
    a2 = 100,
    a3 = 170,
    a4 = 70,
    a5 = (720 - a1 - a2 * 2 - a3 - a4),
    sides = [s1, s1, s1, s3, s1],
    angles = [180, 125.1, 79.5, 156.428, 100],
    line2 = bezier_curve(
      flatten(
        [
          bez_begin([0, 0], -20, 0.4),
          bez_tang([0.25, 0.0], 0, 0.2, 0.4),
          bez_tang([0.4, -0.25], 0, 0, 0),
          bez_end([1, 0], 230, 1),
        ]
      ), 20
    ),
    line3 = reverse(
      [
        for (
          i = bezier_curve(
            flatten(
              [
                bez_begin([0, 0], -45, 0.8),
                bez_end([1, 0], 235, 0.8),
              ]
            ),
            20
          )
        ) [1 - i[0], i[1]],
      ]
    ),
    line1 = [
      for (
        i = smooth_path(
          [
            [-1, 0],
            [-0.951467, 0.23843],
            [-0.84139, 0.462284],
            [-0.746843, 0.428975],
            [-0.751917, 0.323591],
            [-0.674043, 0.280095],
            [-0.576252, 0.374566],
            [-0.49338, 0.341715],
            [-0.479721, 0.200504],
            [-0.269411, 0.261361],
            [-0.240604, 0.121256],
            [-0.0694036, 0.168683],
            [0.00618108, 0.133237],
            [0.00442596, 0.0381548],
            [0, 0],
          ],
          size=0.3,
          method="corners",
          closed=false,
          splinesteps=3
        )
      ) [i[0] + 1, i[1]],
    ],
    hexagon = spin != 0 ? rot(p=generate_hexagon(sides, angles), a=spin) : generate_hexagon(sides, angles),
    new_hex = TesselationPolygon(
      hexagon,
      [1, 2, 0, 1, 0, 2],
      [line1, line2, line3],
      [TESSELATION_LINE_FLIPPED_REVERSE, TESSELATION_LINE_FLIPPED, TESSELATION_LINE_FLIPPED, TESSELATION_LINE_NORMAL, TESSELATION_LINE_NORMAL, TESSELATION_LINE_NORMAL]
    ),
    // Draw the polygon
    rot_hex = move(hexagon[3], rot(p=yflip(hexagon), a=180 - (angles[1] - spin * 2))),
    rot_new_hex = move(hexagon[3], rot(p=yflip(new_hex), a=180 - (angles[1] - spin * 2))),
    x_vec = [hexagon[4][0] - hexagon[0][0], hexagon[4][1] - hexagon[0][1]],
    y_vec = rot_hex[3],
  ) object(
    pts=union(
      [
        DifferenceWithOffset(pts=new_hex, offset=-thickness, outer_offset=outer_offset),
        DifferenceWithOffset(pts=rot_new_hex, offset=-thickness, outer_offset=outer_offset),
      ]
    ), y_vec=y_vec, x_vec=x_vec, angles=angles
  );

// Module: TesselationFlyingBirdGrid()
// Description:
//    The nice goose shape.
// Arguments:
//    row = number of rows
//    col = number of columns
//    size = size of the goose
//    thickness = thickness of the goose
// Example:
//    TesselationFlyingBirdGrid(5, 5, size=30, thickness=1);
module TesselationFlyingBirdGrid(row, col, size, thickness, outer_offset = 0.1, spin = 0) {
  assert(row > 0, "Need a row");
  assert(col > 0, "Need a col");
  assert(size > 0, "Need a size");
  assert(thickness > 0, "Need a thickness");

  bird = FlyingBirdTesselation(size, thickness=thickness, outer_offset=outer_offset, spin=spin);

  module InnerFlyingBird() {
    region(bird.pts);
  }

  ratio = size / 100;
  for (i = [0:row])
    for (j = [0:col])
      translate(i * bird.x_vec)
        translate(j * bird.y_vec) {
          InnerFlyingBird();
        }
}

// Module: TesselationFlyingBirdArea()
// Description:
//    The nice goose shape.
// Arguments:
//    width = width of the space
//    length = length of the space
//    size = size of the goose
//    thickness = thickness of the goose
// Example:
//    TesselationFlyingBirdArea(200, 100, size=50, thickness=2);
module TesselationFlyingBirdArea(width, length, size, thickness, spin = 0) {
  assert(width > 0, "Need a width");
  assert(length > 0, "Need a length");
  assert(size > 0, "Need a size");
  assert(thickness > 0, "Need a thickness");
  size_height = size / 2;
  cols = floor(width / 2.5 / (size) + 1);
  rows = floor(length / 1.3 / (size) + 1);
  fwd(size / 4)
    left(size)
      TesselationFlyingBirdGrid(
        row=rows,
        col=cols,
        size=size,
        thickness=thickness,
        outer_offset=0.2,
        spin=-27.5
      );
}
