// Licensed to the Apache Software Foundation (ASF) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The ASF licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

// Used the information on this page to generate this code
// https://preshing.com/20110831/penrose-tiling-explained/

// LibFile: penrose_tilings.scad
//    This file has all the modules needed to make a penrose tesslation.

// Function: PenroseTriangles()
// Description:
//   Subdivides the triangles to the correct size.
function PenroseTriangles(triangles) =
  (
    [
      for (i = [0:len(triangles) - 1]) each (
        triangles[i][0] == "thin" ? let (
            p1 = triangles[i][1] + (triangles[i][2] - triangles[i][1]) / PHI,
          ) [
              [
                "thin",
                triangles[i][3],
                p1,
                triangles[i][2],
              ],
              [
                "thicc",
                p1,
                triangles[i][3],
                triangles[i][1],
              ],
          ]
        : let (
          R = triangles[i][2] + (triangles[i][3] - triangles[i][2]) / PHI,
          Q = triangles[i][2] + (triangles[i][1] - triangles[i][2]) / PHI
        ) [
            [
              "thicc",
              R,
              triangles[i][3],
              triangles[i][1],
            ],
            [
              "thicc",
              Q,
              R,
              triangles[i][2],
            ],
            [
              "thin",
              R,
              Q,
              triangles[i][1],
            ],
        ]
      ),
    ]
  );

// Function: PenroseTrianglesDivision()
// Description:
//   Recursively call the triangles function to subdivide.
function PenroseTrianglesDivision(triangles, division) =
  let (new_triangles = PenroseTriangles(triangles)) (
    division > 0 ?
      PenroseTrianglesDivision(new_triangles, division - 1)
    : new_triangles
  );

// A function to convert radians to degrees
// Function: r2d()
// Description: Convert radians to degrees.
function r2d(rad) = rad * 180 / PI;

// Module: PenroseTiling()
// Description:
//    This makes a penrose tiling based on the nice layout with a different
//    type of spaces.
// Arguments:
//    width = the width of the tiling space
//    divisions = the number of recursive divisions
//    thickness = the thickness of the stoke to use
//    base = the base divisions of the circle
// Example:
//    PenroseTilding(100, divisions=5, thickness=1, base=5);
// Example:
//    PenroseTilding(100, divisions=5, thickness=1, base=7);
module PenroseTiling(width, divisions = 7, thickness = 1, base = 5) {

  // Create first layer of triangles
  triangles = [
    for (i = [0:base * 2 - 1]) (

      let (
        p2 = polar_to_xy(1, r2d((2 * i - 1) * PI / (base * 2))),
        p3 = polar_to_xy(1, r2d((2 * i + 1) * PI / (base * 2)))
      ) [
          "thin",
          [0, 0],
          (i % 2 == 0) ? p2 : p3,
          (i % 2 == 0) ? p3 : p2,
      ]
    ),
  ];

  final_triangles = PenroseTrianglesDivision(triangles, divisions);

  // Draw the rhombi
  union() {
    for (i = [0:len(final_triangles) - 1]) {
      if (final_triangles[i][0] == "thin") {
        color("red")
          polygon(
            [
              final_triangles[i][1] * width,
              final_triangles[i][2] * width,
              final_triangles[i][3] * width,
            ]
          );
      } else {
        color("green")
          stroke(
            path=[
              final_triangles[i][1] * width,
              final_triangles[i][2] * width,
              final_triangles[i][3] * width,
            ],
            width=thickness
          );
      }
    }
  }
}
