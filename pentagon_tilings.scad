
// mathgrrl Pentagon Tilings

// pentagon vertices, lattices, and offsets from Ed Pegg's Wolfram Demonstration
// http://demonstrations.wolfram.com/PentagonTilings/

// history of the fifteen pentagon classes from Wikipedia
// https://en.wikipedia.org/wiki/Pentagonal_tiling

// what is this business about there being a new pentagon that tiles the plane?
// http://www.zmescience.com/science/math/pentagon-tiles-surface-0342523454/

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


// LibFile: pentagon_tilings.scad
//    This file has all the modules needed to make a variety of penagon tesslations.


////////////////////////////////////////////////////////////////////////////////
// PENATGON PARAMETERS

// [Pattern] 

// Module: PentagonTesselation()
// Description:
//   Make the pentagon tesslation as a specific x,y in the pattern.
// Arguments:
//   pentagon_type = type of the pentagon, eg: "R12"
//   x = x location for the pattern
//   y = y location for the pattern
//   thickness = thickness of the edges of the patter
//   pentagon_size = the size of the pentagon
module PentagonTesselation(pentagon_type, pentagon_size, x, y, thickness) {
  // convex initial conditions for each pentagon
  // R1: AA = 70; BB = 140; b = 1; c = 0.5; e = 0.7;
  // R2: AA = 150; BB = 100; b = 0.7; c = 0; e = 1.2;
  AA_init =
    (pentagon_type == "R1") ? 70
    : (pentagon_type == "R2") ? 150
    : (pentagon_type == "R4") ? 135
    : (pentagon_type == "R5") ? 120
    : (pentagon_type == "R6") ? 120
    : (pentagon_type == "R7") ? 150
    : (pentagon_type == "R8") ? 90
    : (pentagon_type == "R10") ? 90
    : (pentagon_type == "R11") ? 130
    : (pentagon_type == "R12") ? 125
    : (pentagon_type == "R13") ? 135
    : 0;
  BB_init =
    (pentagon_type == "R1") ? 140
    : (pentagon_type == "R2") ? 100
    : 0;
  b_init =
    (pentagon_type == "R1") ? 1
    : (pentagon_type == "R2") ? 0.7
    : (pentagon_type == "R3") ? 0.5
    : (pentagon_type == "R4") ? 1.25
    : (pentagon_type == "R5") ? 0.5
    : (pentagon_type == "R9") ? 1.573
    : 0;
  c_init =
    (pentagon_type == "R1") ? 0.5
    : 0;
  e_init =
    (pentagon_type == "R1") ? 0.7
    : (pentagon_type == "R2") ? 1.2
    : 0;

  // (applies to 1, 2, 4-8, 10-13) value:
  first_angle_modifier = 0; // [-60:5:60]

  // (applies to 1, 2) value:
  second_angle_modifier = 0; // [-60:5:60]

  // (applies to 1-5, 9) value:
  first_length_modifier = 0; // [-1:.1:1]

  // (applies to 1) value:
  second_length_modifier = 0; // [-1:.1:1]

  // (applies to 1, 2) value:
  third_length_modifier = 0; // [-1:.1:1]

  // add user modifiers to the initial values
  AA_mod = AA_init + first_angle_modifier;
  BB_mod = BB_init + second_angle_modifier;
  b_mod = b_init + first_length_modifier;
  c_mod = c_init + second_length_modifier;
  e_mod = e_init + third_length_modifier;

  // stay within reasonable bounds
  AA =
    (AA_mod < 0) ? 0
    : (AA_mod > 360) ? 360
    : AA_mod;
  BB =
    (BB_mod < 0) ? 0
    : (BB_mod > 360) ? 360
    : BB_mod;
  b =
    (b_mod < 0) ? 0
    : (b_mod > 2) ? 2
    : b_mod;
  c =
    (c_mod < 0) ? 0
    : (c_mod > 2) ? 2
    : c_mod;
  e =
    (e_mod < 0) ? 0
    : (e_mod > 2) ? 2
    : e_mod;

  ////////////////////////////////////////////////////////////////////////////////
  // Tesselation MODULE

  module InnerPentagonTesselation(pattern) {
    for (i = [0:len(pattern[1]) - 1]) {
      pentagonBorder(vertices=pattern[1][i], size=pentagon_size, thickness=thickness);
    }
  }

  ////////////////////////////////////////////////////////////////////////////////
  // PENTAGON AND LATTICE MODULES

  module pentagonBorder(vertices, size, thickness) {
    difference() {
      offset(0.1 * thickness)
        scale(size)
          polygon(points=vertices, paths=[[0, 1, 2, 3, 4]]);
      offset(-1 * thickness)
        scale(size)
          polygon(points=vertices, paths=[[0, 1, 2, 3, 4]]);
    }
  }

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 1 PENTAGON DATA: Reinhardt 1918
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/

  R1scale = 1;

  // main pentagon
  R1 = R1scale * [
    [.5 - b * cos(AA), b * sin(AA)],
    [.5 - b * cos(AA) + c * cos(AA + BB), b * sin(AA) - c * sin(AA + BB)],
    [-.5 - e * cos(AA), e * sin(AA)],
    [-.5, 0],
    [.5, 0],
  ];

  // other pentagons in the pattern
  R1_2 = R1scale * [
    [-.5 + b * cos(AA), -b * sin(AA)],
    [-.5 + b * cos(AA) - c * cos(AA + BB), -b * sin(AA) + c * sin(AA + BB)],
    [.5 + e * cos(AA), -e * sin(AA)],
    [.5, 0],
    [-.5, 0],
  ];

  // offsets
  R1xoff = R1scale * [-1 + b * cos(AA) - e * cos(AA), -b * sin(AA) + e * sin(AA)];
  R1yoff = R1scale * [-b * cos(AA) - e * cos(AA) + c * cos(AA + BB), b * sin(AA) + e * sin(AA) - c * sin(AA + BB)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 2 PENTAGON DATA: Reinhardt 1918
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/

  R2scale = .8;

  // main pentagon
  R2 = R2scale * [
    [.5 * (b - 2 * cos(BB)), sin(BB)],
    [-.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
    [-.5 * b + cos(AA), sin(AA)],
    [-.5 * b, 0],
    [.5 * b, 0],
  ];

  // other pentagons in the pattern
  R2_2 = R2scale * [
    [.5 * (b - 2 * cos(AA) + 2 * b * cos(AA - BB) - 2 * cos(BB)), -sin(AA) + b * sin(AA - BB) + sin(BB)],
    [.5 * b + e, 0],
    [b / 2, 0],
    [.5 * (b - 2 * cos(BB)), sin(BB)],
    [.5 * (b + 2 * b * cos(AA - BB) - 2 * cos(BB)), b * sin(AA - BB) + sin(BB)],
  ];
  R2_3 = R2scale * [
    [-.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
    [.5 * (b - 2 * cos(BB)), sin(BB)],
    [.5 * b + e * cos(AA - BB) - cos(BB), e * sin(AA - BB) + sin(BB)],
    [.5 * b + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
    [-.5 * b + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
  ];
  R2_4 = R2scale * [
    [-.5 * b + 2 * cos(AA) + ( -b + e) * cos(AA - BB), 2 * sin(AA) + ( -b + e) * sin(AA - BB)],
    [-.5 * b - e + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
    [-b / 2 + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
    [-.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
    [-.5 * b + cos(AA) + ( -b + e) * cos(AA - BB), sin(AA) + ( -b + e) * sin(AA - BB)],
  ];

  // offsets
  R2xoff = R2scale * [.5 * b - cos(AA) + .5 * (b + 2 * b * cos(AA - BB) - 2 * cos(BB)), -sin(AA) + b * sin(AA - BB) + sin(BB)];
  R2yoff = R2scale * [b + e - 2 * cos(AA) + (b - e) * cos(AA - BB), -2 * sin(AA) + (b - e) * sin(AA - BB)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 3 PENTAGON DATA: Reinhardt 1918
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/

  R3scale = 1;

  // main pentagon
  R3 = R3scale * [
    [0, 0],
    [.5, .5 * sqrt(3)],
    [.5 * b, -.5 * sqrt(3) * (-2 + b)],
    [-.5, sqrt(3) / 2],
    [-b, 0],
  ];

  // other pentagons in the pattern
  R3_2 = R3scale * [
    [-.5 * 3, .5 * sqrt(3)],
    [-1, 0],
    [-b, 0],
    [-.5, .5 * sqrt(3)],
    [.5 * (-3 + b), .5 * sqrt(3) * (1 + b)],
  ];
  R3_3 = R3scale * [
    [0, sqrt(3)],
    [-1, sqrt(3)],
    [.5 * (-3 + b), .5 * sqrt(3) * (1 + b)],
    [-.5, .5 * sqrt(3)],
    [.5 * b, -.5 * sqrt(3) * (-2 + b)],
  ];

  // offsets
  R3xoff = R3scale * [.5 * 3, .5 * sqrt(3)];
  R3yoff = R3scale * [0, sqrt(3)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 4 PENTAGON DATA: Reinhardt 1918
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R4scale = .7;

  // main pentagon
  R4 = R4scale * [
    [0, 0],
    [0, 1],
    [-b * sin(AA), 1 - b * cos(AA)],
    [b * (cos(AA) - sin(AA)), 1 - b * (cos(AA) + sin(AA))],
    [-1, 0],
  ];

  // other pentagons in the pattern
  R4_2 = R4scale * [
    [0, 0],
    [-1, 0],
    [-1 + b * cos(AA), -b * sin(AA)],
    [-1 + b * (cos(AA) + sin(AA)), b * (cos(AA) - sin(AA))],
    [0, -1],
  ];
  R4_3 = R4scale * [
    [0, 0],
    [0, -1],
    [b * sin(AA), -1 + b * cos(AA)],
    [-b * (cos(AA) - sin(AA)), -1 + b * (cos(AA) + sin(AA))],
    [1, 0],
  ];
  R4_4 = R4scale * [
    [0, 0],
    [1, 0],
    [1 - b * cos(AA), b * sin(AA)],
    [1 - b * (cos(AA) + sin(AA)), -b * (cos(AA) - sin(AA))],
    [0, 1],
  ];

  // offsets
  R4xoff = R4scale * [-1 + b * (cos(AA) - sin(AA)), 1 - b * (cos(AA) + sin(AA))];
  R4yoff = R4scale * [1 - b * (cos(AA) + sin(AA)), 1 - b * (cos(AA) - sin(AA))];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 5 PENTAGON DATA: Reinhardt 1918
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R5scale = 1;

  // main pentagon
  R5 = R5scale * [
    [0, 0],
    [1, 0],
    [1 - b * cos(AA), b * sin(AA)],
    [.5 * (2 - 3 * b * cos(AA) - sqrt(3) * b * sin(AA)), -.5 * b * (sqrt(3) * cos(AA) - 3 * sin(AA))],
    [.5, .5 * sqrt(3)],
  ];

  // other pentagons in the pattern
  R5_2 = R5scale * [
    [0, 0],
    [.5, .5 * sqrt(3)],
    [.5 * (1 - b * (cos(AA) + sqrt(3) * sin(AA))), .5 * (sqrt(3) * (1 - b * cos(AA)) + b * sin(AA))],
    [.5 - sqrt(3) * b * sin(AA), .5 * sqrt(3) * (1 - 2 * b * cos(AA))],
    [-.5, .5 * sqrt(3)],
  ];
  R5_3 = R5scale * [
    [0, 0],
    [-.5, .5 * sqrt(3)],
    [.5 * (-1 + b * cos(AA) - sqrt(3) * b * sin(AA)), .5 * (sqrt(3) * (1 - b * cos(AA)) - b * sin(AA))],
    [.5 * (-1 + 3 * b * cos(AA) - sqrt(3) * b * sin(AA)), .5 * (sqrt(3) - sqrt(3) * b * cos(AA) - 3 * b * sin(AA))],
    [-1, 0],
  ];
  R5_4 = R5scale * [
    [0, 0],
    [-1, 0],
    [-1 + b * cos(AA), -b * sin(AA)],
    [.5 * (-2 + 3 * b * cos(AA) + sqrt(3) * b * sin(AA)), .5 * b * (sqrt(3) * cos(AA) - 3 * sin(AA))],
    [-.5, -.5 * sqrt(3)],
  ];
  R5_5 = R5scale * [
    [0, 0],
    [-.5, -.5 * sqrt(3)],
    [.5 * (-1 + b * cos(AA) + sqrt(3) * b * sin(AA)), .5 * (sqrt(3) * (-1 + b * cos(AA)) - b * sin(AA))],
    [-.5 + sqrt(3) * b * sin(AA), .5 * sqrt(3) * (-1 + 2 * b * cos(AA))],
    [.5, -.5 * sqrt(3)],
  ];
  R5_6 = R5scale * [
    [0, 0],
    [.5, -.5 * sqrt(3)],
    [.5 * (1 - b * cos(AA) + sqrt(3) * b * sin(AA)), .5 * (sqrt(3) * (-1 + b * cos(AA)) + b * sin(AA))],
    [.5 * (1 - 3 * b * cos(AA) + sqrt(3) * b * sin(AA)), .5 * ( -sqrt(3) + sqrt(3) * b * cos(AA) + 3 * b * sin(AA))],
    [1, 0],
  ];

  // offsets
  R5xoff = R5scale * [.5 * (3 - 3 * b * cos(AA) + sqrt(3) * b * sin(AA)), .5 * ( -sqrt(3) + sqrt(3) * b * cos(AA) + 3 * b * sin(AA))];
  R5yoff = R5scale * [-sqrt(3) * b * sin(AA), sqrt(3) * (1 - b * cos(AA))];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 6 PENTAGON DATA: Kershner 1968
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R6scale = .55;

  // main pentagon
  R6 = R6scale * [
    [.5, 0],
    [.5 - cos(AA), sin(AA)],
    [-cos(AA / 2) - cos(AA), .5 * cos(AA / 4) / sin(AA / 4) + sin(AA / 2) + sin(AA)],
    [-.5 - cos(AA / 2), sin(AA / 2)],
    [-.5, 0],
  ];

  // other pentagons in the pattern
  R6_2 = R6scale * [
    [-.5 - cos(AA / 2), sin(AA / 2)],
    [-.5 - cos(AA / 2) + cos(3 * AA / 2), sin(AA / 2) - sin(3 * AA / 2)],
    [-1 - cos(AA / 2) + cos(AA) + cos(3 * AA / 2), .5 * (-2 * cos(3 * AA / 4) + cos(7 * AA / 4)) * (1 / sin(AA / 4))],
    [-.5 + cos(AA), -1 * sin(AA)],
    [-.5, 0],
  ];
  R6_3 = R6scale * [
    [-.5, 0],
    [-.5 + cos(AA), -1 * sin(AA)],
    [cos(AA / 2) + cos(AA), -.5 * cos(AA / 4) / sin(AA / 4) - sin(AA / 2) - sin(AA)],
    [.5 + cos(AA / 2), -sin(AA / 2)],
    [.5, 0],
  ];
  R6_4 = R6scale * [
    [.5 + cos(AA / 2), -1 * sin(AA / 2)],
    [.5 + cos(AA / 2) - cos(3 * AA / 2), -1 * sin(AA / 2) + sin(3 * AA / 2)],
    [1 + cos(AA / 2) - cos(AA) - cos(3 * AA / 2), -.5 * (-2 * cos(3 * AA / 4) + cos(7 * AA / 4)) * (1 / sin(AA / 4))],
    [.5 - cos(AA), sin(AA)],
    [.5, 0],
  ];

  // offsets
  R6xoff = R6scale * [-1 - 2 * cos(AA / 2) + cos(3 * AA / 2), 2 * sin(AA / 2) - sin(3 * AA / 2)];
  R6yoff = R6scale * [.5 - cos(AA / 2) - 2 * cos(AA), .5 * cos(AA / 4) / sin(AA / 4) + sin(AA / 2) + 2 * sin(AA)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 7 PENTAGON DATA: Kershner 1968
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R7scale = .9;

  // main pentagon
  R7denom = 4 * (2 + cos(AA) - cos(3 * AA));
  R7 = R7scale * [
    [1 - cos(AA) / 2, sin(AA) / 2],
    [-1 * cos(AA) / 2, sin(AA) / 2],
    [cos(AA) / 2, -1 * sin(AA) / 2],
    [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
    [-1 * (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom, (-2 * sin(2 * AA) - 4 * sin(3 * AA) + sin(4 * AA)) / R7denom],
  ];

  // other pentagons in the pattern
  R7_2 = R7scale * [
    [
      -1 * (-1 + 4 * cos(AA) - 8 * cos(2 * AA) - 2 * cos(3 * AA) + cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
      (4 * sin(AA) + 6 * sin(2 * AA) - 2 * sin(3 * AA) + sin(4 * AA) - 2 * sin(5 * AA)) / R7denom,
    ],
    [
      -1 * (-3 + 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
      -1 * (-2 * sin(2 * AA) + 6 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
    ],
    [(-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom],
    [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
    [-1 * (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom, (-2 * sin(2 * AA) - 4 * sin(3 * AA) + sin(4 * AA)) / R7denom],
  ];
  R7_3 = R7scale * [
    [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
    [cos(AA) / 2, -1 * sin(AA) / 2],
    [.5 * (-2 + cos(AA)), -1 * sin(AA) / 2],
    [-1 + cos(AA) / 2 + cos(2 * AA), -1 * sin(AA) / 2 + sin(2 * AA)],
    [(-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom],
  ];
  R7_4 = R7scale * [
    [
      -1 * (-1 + 2 * cos(2 * AA) + 4 * cos(3 * AA) + cos(4 * AA) - 2 * cos(6 * AA)) / R7denom,
      (-4 * sin(AA) - 8 * sin(3 * AA) + sin(4 * AA) + 2 * sin(6 * AA)) / R7denom,
    ],
    [
      (cos(AA) * (-3 * cos(AA) + cos(3 * AA) + 2 * (cos(4 * AA) + cos(5 * AA)))) / (R7denom / 2),
      (-8 * sin(AA) - 2 * sin(3 * AA) + 5 * sin(4 * AA) + 2 * (sin(5 * AA) + sin(6 * AA))) / R7denom,
    ],
    [
      (5 - 4 * cos(AA) - 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / (-1 * R7denom),
      -1 * (4 * sin(AA) - 2 * sin(2 * AA) + 2 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
    ],
    [-1 + cos(AA) / 2 + cos(2 * AA), -1 * sin(AA) / 2 + sin(2 * AA)],
    [(-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom],
  ];
  R7_5 = R7scale * [
    [.5 * (-2 + cos(AA)), -1 * sin(AA) / 2],
    [cos(AA) / 2, -1 * sin(AA) / 2],
    [-1 * cos(AA) / 2, sin(AA) / 2],
    [cos(AA) / 2, 3 * sin(AA) / 2],
    [(-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom, (2 * sin(2 * AA) + 4 * sin(3 * AA) - sin(4 * AA)) / R7denom],
  ];
  R7_6 = R7scale * [
    [
      (-1 + 4 * cos(AA) - 8 * cos(2 * AA) - 2 * cos(3 * AA) + cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
      -1 * (4 * sin(AA) + 6 * sin(2 * AA) - 2 * sin(3 * AA) + sin(4 * AA) - 2 * sin(5 * AA)) / R7denom,
    ],
    [
      (cos(AA) * (-3 * cos(AA) + 3 * cos(3 * AA) + 2 * cos(4 * AA))) / (R7denom / 2),
      (-2 * sin(2 * AA) + 6 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
    ],
    [-1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom],
    [cos(AA) / 2, 3 * sin(AA) / 2],
    [(-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom, (2 * sin(2 * AA) + 4 * sin(3 * AA) - sin(4 * AA)) / R7denom],
  ];
  R7_7 = R7scale * [
    [cos(AA) / 2, 3 * sin(AA) / 2],
    [-1 * cos(AA) / 2, sin(AA) / 2],
    [1 - cos(AA) / 2, sin(AA) / 2],
    [-1 * cos(AA) / 2 + 2 * sin(AA) * sin(AA), .5 * (1 - 4 * cos(AA)) * sin(AA)],
    [-1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom],
  ];
  R7_8 = R7scale * [
    [
      (-1 + 2 * cos(2 * AA) + 4 * cos(3 * AA) + cos(4 * AA) - 2 * cos(6 * AA)) / R7denom,
      -1 * (-4 * sin(AA) - 8 * sin(3 * AA) + sin(4 * AA) + 2 * sin(6 * AA)) / R7denom,
    ],
    [
      -1 * (cos(AA) * (-3 * cos(AA) + cos(3 * AA) + 2 * (cos(4 * AA) + cos(5 * AA)))) / (R7denom / 2),
      (8 * sin(AA) + 2 * sin(3 * AA) - 5 * sin(4 * AA) - 2 * (sin(5 * AA) + sin(6 * AA))) / R7denom,
    ],
    [
      (5 - 4 * cos(AA) - 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
      (4 * sin(AA) - 2 * sin(2 * AA) + 2 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
    ],
    [-cos(AA) / 2 + 2 * sin(AA) * sin(AA), .5 * (1 - 4 * cos(AA)) * sin(AA)],
    [-1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom, (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom],
  ];

  // offsets
  R7xoff = R7scale * [1 + (2 * cos(AA)) / (-2 - cos(AA) + cos(3 * AA)), (sin(AA) - sin(3 * AA)) / (2 + cos(AA) - cos(3 * AA))];
  R7yoff = R7scale * [
    -1 * (sin(2 * AA) * sin(4 * AA)) / (2 + cos(AA) - cos(3 * AA)),
    (-4 * sin(AA) + sin(2 * AA) - 4 * sin(3 * AA) + 2 * sin(4 * AA) + sin(6 * AA)) / (2 * (2 + cos(AA) - cos(3 * AA))),
  ];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 8 PENTAGON DATA: Kershner 1968
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R8scale = .8;

  // main pentagon
  R8 = R8scale * [
    [-(1 / 2), 0],
    [1 / 2, 0],
    [1 / 2 - cos(AA), -1 * sin(AA)],
    [
      -(3 / 4) + 9 / (4 * (5 + 4 * cos(AA / 2))) - cos(AA),
      (-5 * (sin(AA / 2) + sin(AA)) - 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
    ],
    [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
  ];

  // other pentagons in the pattern
  R8_2 = R8scale * [
    [
      -( (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2))),
      -( (3 * (3 * sin(AA / 2) + 2 * sin(AA))) / (5 + 4 * cos(AA / 2))),
    ],
    [
      -( (11 + 24 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
      -( (2 * (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2))),
    ],
    [
      -( (3 + 14 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
      -( ( (11 + 20 * cos(AA / 2) + 8 * cos(AA)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2))),
    ],
    [
      -( (3 + 10 * cos(AA / 2) + 10 * cos(AA) + 4 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
      (-5 * (sin(AA / 2) + sin(AA)) - 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
    ],
    [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
  ];
  R8_3 = R8scale * [
    [1 / 2, 0],
    [-(1 / 2), 0],
    [-(1 / 2) + cos(AA), sin(AA)],
    [
      3 / 4 - 9 / (4 * (5 + 4 * cos(AA / 2))) + cos(AA),
      (5 * (sin(AA / 2) + sin(AA)) + 2 * (sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2)),
    ],
    [1 / 2 + cos(AA / 2), sin(AA / 2)],
  ];
  R8_4 = R8scale * [
    [
      (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2)),
      (9 * sin(AA / 2) + 6 * sin(AA)) / (5 + 4 * cos(AA / 2)),
    ],
    [
      (11 + 24 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2)),
      (2 * (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2)),
    ],
    [
      (3 + 14 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2)),
      ( (11 + 20 * cos(AA / 2) + 8 * cos(AA)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2)),
    ],
    [
      (3 + 10 * cos(AA / 2) + 10 * cos(AA) + 4 * (cos((3 * AA) / 2))) / (10 + 8 * cos(AA / 2)),
      (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
    ],
    [1 / 2 + cos(AA / 2), sin(AA / 2)],
  ];
  R8_5 = R8scale * [
    [-(1 / 2), 0],
    [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
    [-(1 / 2) - cos(AA / 2) + cos((3 * AA) / 2), 2 * cos(AA) * sin(AA / 2)],
    [
      (-7 - 6 * cos(AA / 2) + 8 * cos(AA) + 10 * cos((3 * AA) / 2) + 4 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      (-1 * sin(AA / 2) + 4 * sin(AA) + 5 * sin((3 * AA) / 2) + 2 * sin(2 * AA)) / (5 + 4 * cos(AA / 2)),
    ],
    [-(1 / 2) + cos(AA), sin(AA)],
  ];
  R8_6 = R8scale * [
    [
      (-11 - 22 * cos(AA / 2) - 10 * cos(AA) + 8 * cos((3 * AA) / 2) + 8 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      ( (-5 + 8 * cos(AA)) * (sin(AA / 2) + sin(AA))) / (5 + 4 * cos(AA / 2)),
    ],
    [
      -( (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2))),
      -( (3 * (3 * sin(AA / 2) + 2 * sin(AA))) / (5 + 4 * cos(AA / 2))),
    ],
    [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
    [-(1 / 2) - cos(AA / 2) + cos((3 * AA) / 2), 2 * cos(AA) * sin(AA / 2)],
    [
      (-11 - 20 * cos(AA / 2) - 2 * cos(AA) + 16 * cos((3 * AA) / 2) + 8 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      (2 * (3 * cos(AA / 2) + 8 * cos(AA) + 4 * cos((3 * AA) / 2)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2)),
    ],
  ];
  R8_7 = R8scale * [
    [1 / 2, 0],
    [1 / 2 + cos(AA / 2), sin(AA / 2)],
    [1 / 2 + cos(AA / 2) - cos((3 * AA) / 2), -2 * cos(AA) * sin(AA / 2)],
    [
      (7 + 6 * cos(AA / 2) - 8 * cos(AA) - 10 * cos((3 * AA) / 2) - 4 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      (sin(AA / 2) - 4 * sin(AA) - 5 * sin((3 * AA) / 2) - 2 * sin(2 * AA)) / (5 + 4 * cos(AA / 2)),
    ],
    [1 / 2 - cos(AA), -1 * sin(AA)],
  ];
  R8_8 = R8scale * [
    [
      (11 + 22 * cos(AA / 2) + 10 * cos(AA) - 8 * cos((3 * AA) / 2) - 8 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      -( ( (-5 + 8 * cos(AA)) * (sin(AA / 2) + sin(AA))) / (5 + 4 * cos(AA / 2))),
    ],
    [
      (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2)),
      (9 * sin(AA / 2) + 6 * sin(AA)) / (5 + 4 * cos(AA / 2)),
    ],
    [1 / 2 + cos(AA / 2), sin(AA / 2)],
    [1 / 2 + cos(AA / 2) - cos((3 * AA) / 2), -2 * cos(AA) * sin(AA / 2)],
    [
      (11 + 20 * cos(AA / 2) + 2 * cos(AA) - 16 * cos((3 * AA) / 2) - 8 * cos(2 * AA)) / (10 + 8 * cos(AA / 2)),
      (8 * sin(AA / 2) + sin(AA) - 4 * (2 * sin((3 * AA) / 2) + sin(2 * AA))) / (5 + 4 * cos(AA / 2)),
    ],
  ];

  // offsets
  R8xoff = R8scale * [
    (12 * cos(AA / 4) * cos(AA / 4) * (cos(AA / 2) + 2 * cos(AA))) / (5 + 4 * cos(AA / 2)),
    3 * (4 * sin(AA / 2) + 5 * sin(AA) + 2 * sin(3 * AA / 2)) / (5 + 4 * cos(AA / 2)),
  ];
  R8yoff = R8scale * [
    (11 + 22 * cos(AA / 2) + 11 * cos(AA) - 4 * cos(3 * AA / 2) - 4 * cos(2 * AA)) / (5 + 4 * cos(AA / 2)),
    (18 * sin(AA / 2) + 11 * sin(AA) - 4 * (sin(3 * AA / 2) + sin(2 * AA))) / (5 + 4 * cos(AA / 2)),
  ];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 9 PENTAGON DATA: Rice 1975
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R9scale = .5;

  // main pentagon
  R9 = R9scale * [
    [0, -1 * sqrt(-1 + b * b)],
    [
      -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [-2 + 4 / (b * b), (-1 - 4 / (b * b)) * sqrt(-1 + b * b)],
    [-3 + 4 / (b * b), -( (4 * sqrt(-1 + b * b)) / (b * b))],
  ];

  // other pentagons in the pattern
  R9_2 = R9scale * [
    [
      4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [-2 + 4 / (b * b), (-1 - 4 / (b * b)) * sqrt(-1 + b * b)],
    [
      -1 + 4 / (b * b) + (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (4 * sqrt(-1 + b * b) * (8 - 4 * b * b + b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
  ];
  R9_3 = R9scale * [
    [1, 0],
    [0, -1 * sqrt(-1 + b * b)],
    [
      -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      -1 + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
    ],
    [
      -2 + 8 / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (16 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
    ],
  ];
  R9_4 = R9scale * [
    [
      -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [-1 + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b), (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b)],
    [
      (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (20 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
    ],
  ];
  R9_5 = R9scale * [
    [
      -6 + 12 / (b * b) + (4 * (-7 + 3 * b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (-32 + 48 * b * b - 13 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -3 + 8 / (b * b) + (4 * (-7 + 3 * b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-5 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
    ],
    [
      -4 + 8 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (24 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -1 + 4 / (b * b) + (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (4 * sqrt(-1 + b * b) * (8 - 4 * b * b + b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
  ];
  R9_6 = R9scale * [
    [
      -2 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -1 + 4 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (4 * (-8 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      -4 + 8 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (24 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
      -( (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
  ];
  R9_7 = R9scale * [
    [
      3 - 8 / (b * b) - (8 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (8 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [
      -(4 / (b * b)) - (8 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      (sqrt(-1 + b * b) * (-32 + 20 * b * b + b * b * b * b - b * b * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      1 - 4 / (b * b) - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (4 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [1, 0],
    [-2 + 8 / (8 - 5 * b * b + b * b * b * b), -( (sqrt(-1 + b * b) * (16 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b))],
  ];
  R9_8 = R9scale * [
    [-1, 0],
    [
      -2 - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (sqrt(-1 + b * b) * (4 - 5 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
    ],
    [
      1 - 4 / (b * b) - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
      -( (4 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b))),
    ],
    [1, 0],
    [0, -1 * sqrt(-1 + b * b)],
  ];

  // offsets
  R9xoff = R9scale * [(4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b), (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b)];
  R9yoff = R9scale * [
    -4 + 12 / (b * b) + (8 * (-5 + 2 * b * b)) / (8 - 5 * b * b + b * b * b * b),
    (4 * sqrt(-1 + b * b) * (8 - 11 * b * b + 2 * b * b * b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
  ];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 10 PENTAGON DATA: James 1975
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R10scale = 1;

  // main pentagon
  R10 = R10scale * [
    [1, 0],
    [
      (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
      -( (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
    ],
    [
      sin(AA) * (-1 + 3 / (1 + sin(AA / 2) / cos(AA / 2))),
      (1 / 2) * (-1 - cos(AA) + 3 * sin(AA)),
    ],
    [0, 1],
    [0, 0],
  ];

  // other pentagons in the pattern
  R10_2 = R10scale * [
    [0, 1],
    [
      (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
      (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
    ],
    [
      (1 / 2) * (1 + cos(AA) - 3 * sin(AA)),
      sin(AA) * (-1 + 3 / (1 + sin(AA / 2) / cos(AA / 2))),
    ],
    [-1, 0],
    [0, 0],
  ];
  R10_3 = R10scale * [
    [-1, 0],
    [
      (1 / 2) * (1 - cos(AA) - 3 * sin(AA)),
      (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
    ],
    [
      sin(AA) * (1 - 3 / (1 + sin(AA / 2) / cos(AA / 2))),
      (1 / 2) * (1 + cos(AA) - 3 * sin(AA)),
    ],
    [0, -1],
    [0, 0],
  ];
  R10_4 = R10scale * [
    [0, -1],
    [
      -( (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
      (1 / 2) * (1 - cos(AA) - 3 * sin(AA)),
    ],
    [
      (1 / 2) * (-1 - cos(AA) + 3 * sin(AA)),
      sin(AA) * (1 - 3 / (1 + sin(AA / 2) / cos(AA / 2))),
    ],
    [1, 0],
    [0, 0],
  ];
  R10_5 = R10scale * [
    [
      (1 / 2) * (-3 + cos(AA) + 6 / (1 + cos(AA / 2) / sin(AA / 2)) + 3 * sin(AA)),
      -( (cos(AA / 2) * (-2 + 2 * cos(AA) + sin(AA))) / (cos(AA / 2) + sin(AA / 2))),
    ],
    [
      (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
      -( (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
    ],
    [
      (-1 + cos(AA) + 2 * sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
      (1 / 2) * (-1 - cos(AA) + 3 * sin(AA)),
    ],
    [
      (cos(AA / 2) * (-1 + cos(AA) + 2 * sin(AA))) / (cos(AA / 2) + sin(AA / 2)),
      (cos(AA) + cos(AA / 2) / sin(AA / 2) + 2 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2)),
    ],
    [
      (3 * sin(AA) * sin(AA)) / (1 - cos(AA) + sin(AA)),
      (3 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2)),
    ],
  ];
  R10_6 = R10scale * [
    [
      (1 / 2) * (3 - cos(AA) - 6 / (1 + cos(AA / 2) / sin(AA / 2)) - 3 * sin(AA)),
      (cos(AA / 2) * (-2 + 2 * cos(AA) + sin(AA))) / (cos(AA / 2) + sin(AA / 2)),
    ],
    [
      (1 / 2) * (1 - cos(AA) - 3 * sin(AA)),
      (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
    ],
    [
      -( (-1 + cos(AA) + 2 * sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
      (1 / 2) * (1 + cos(AA) - 3 * sin(AA)),
    ],
    [
      -( (cos(AA / 2) * (-1 + cos(AA) + 2 * sin(AA))) / (cos(AA / 2) + sin(AA / 2))),
      -( (cos(AA) + cos(AA / 2) / sin(AA / 2) + 2 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2))),
    ],
    [
      -( (3 * sin(AA) * sin(AA)) / (1 - cos(AA) + sin(AA))),
      -( (3 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2))),
    ],
  ];

  // offsets
  R10xoff = R10scale * [
    -3 + 3 * cos(AA) + 6 / (1 + cos(AA / 2) / sin(AA / 2)) + sin(AA),
    (1 + 2 * cos(AA) + 4 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2)),
  ];
  R10yoff = R10scale * [
    (3 - 4 * cos(AA)) / (1 + tan(AA / 2)),
    -1 * (sin(AA / 2) + 2 * sin(3 * AA / 2)) / (cos(AA / 2) + sin(AA / 2)),
  ];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 11 PENTAGON DATA: Rice 1976
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R11scale = 1.05;

  // main pentagon
  R11 = R11scale * [
    [0, 0],
    [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
    [sin(AA) - sin(2 * AA), cos(AA) * (1 + (4 * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
    [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA))],
    [0, (-2 * cos(AA) + cos(2 * AA)) / (1 - 2 * cos(AA))],
  ];

  // other pentagons in the pattern
  R11_2 = R11scale * [
    [0, 0],
    [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
    [sin(AA) - sin(2 * AA), -cos(AA) * (1 + (4 * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
    [-sin(2 * AA), -( (4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
    [0, -( (-2 * cos(AA) + cos(2 * AA)) / (1 - 2 * cos(AA)))],
  ];
  R11_3 = R11scale * [
    [(2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
    [(1 - 2 * cos(AA)) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
    [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), -1 + 3 / (1 - 2 * cos(AA)) + 2 * cos(2 * AA)],
    [(2 - 4 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA)],
    [(2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + cos(2 * AA)],
  ];
  R11_4 = R11scale * [
    [(2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
    [(1 - 2 * cos(AA)) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
    [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
    [(2 - 4 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -cos(AA)],
    [(2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -cos(AA) + cos(2 * AA)],
  ];
  R11_5 = R11scale * [
    [
      ( (-2 + 4 * cos(AA) - 3 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)),
      (2 + cos(AA) + 2 * cos(2 * AA) - 3 * cos(3 * AA)) / (2 - 4 * cos(AA)),
    ],
    [-2 * sin(2 * AA) + sin(3 * AA), (1 + 2 * cos(AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
    [(2 - 3 / (1 - 2 * cos(AA)) - 4 * cos(AA)) * sin(AA), -2 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA)],
    [(2 - 3 / (1 - 2 * cos(AA)) - 4 * cos(AA)) * sin(AA), -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA)],
    [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), -1 + 3 / (1 - 2 * cos(AA)) + 2 * cos(2 * AA)],
  ];
  R11_6 = R11scale * [
    [( (-2 + 4 * cos(AA) - 3 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)), (2 + cos(AA) + 2 * cos(2 * AA) - 3 * cos(3 * AA)) / (2 - 4 * cos(AA))],
    [-2 * sin(2 * AA) + sin(3 * AA), (1 + 2 * cos(AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
    [-2 * sin(2 * AA) + sin(3 * AA), (2 * cos(2 * AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
    [-sin(2 * AA) + sin(3 * AA), (cos(AA) - 4 * cos(3 * AA) * sin(AA / 2) * sin(AA / 2)) / (1 - 2 * cos(AA))],
    [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (1 - 2 * cos(AA))],
  ];
  R11_7 = R11scale * [
    [(3 * (sin(AA) - 2 * sin(2 * AA) + sin(3 * AA))) / (2 - 4 * cos(AA)), (sin(AA) * sin(2 * AA)) / (-1 + 2 * cos(AA))],
    [(8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)), -3 * cos(AA) + 3 / (-1 + 2 * cos(AA)) - cos(2 * AA) + cos(3 * AA)],
    [-sin(2 * AA), (1 - 3 * cos(AA) + cos(3 * AA)) / (1 - 2 * cos(AA))],
    [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA))],
    [(1 - 2 * cos(AA)) * sin(AA), (1 + cos(2 * AA) - cos(3 * AA)) / (-1 + 2 * cos(AA))],
  ];
  R11_8 = R11scale * [
    [(3 * (sin(AA) - 2 * sin(2 * AA) + sin(3 * AA))) / (2 - 4 * cos(AA)), (sin(AA) * sin(2 * AA)) / (-1 + 2 * cos(AA))],
    [(8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)), -3 * cos(AA) + 3 / (-1 + 2 * cos(AA)) - cos(2 * AA) + cos(3 * AA)],
    [(8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)), -cos(AA) - cos(2 * AA) + cos(3 * AA)],
    [(sin(AA) - 3 * sin(2 * AA) + sin(3 * AA) + sin(4 * AA)) / (1 - 2 * cos(AA)), -4 * cos(AA) * sin(AA) * sin(AA)],
    [(2 + 3 / (-1 + 2 * cos(AA))) * sin(AA) - 2 * sin(2 * AA), -cos(AA)],
  ];

  // offsets
  R11xoff = R11scale * [
    (8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
    -1 * (8 * (-1 + cos(AA)) * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
  ];
  R11yoff = R11scale * [
    ( (3 - 8 * cos(AA) + 4 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)),
    (1 + 3 * cos(AA) - 2 * cos(3 * AA)) / (-1 + 2 * cos(AA)),
  ];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 12 PENTAGON DATA: Rice 1976
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R12scale = .65;

  // main pentagon
  R12 = R12scale * [
    [0, 1],
    [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
    [
      (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA) + cos((3 * AA) / 2)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (1 / 2) * ( -(4 / (1 + 2 * cos(AA / 2))) + (1 / sin(AA / 4)) * (1 / sin(AA / 4))) * sin(AA),
      2 + (1 / (-1 + cos(AA / 2)) + 1 / ( (1 / 2) + cos(AA / 2))) * cos(AA),
    ],
    [0, 2],
  ];

  // other pentagons in the pattern
  R12_2 = R12scale * [
    [0, 1],
    [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
    [
      (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (1 + cos(AA / 2) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [
      1 / 2 * ( -(4 / (1 + 2 * cos(AA / 2))) + (1 / sin(AA / 4)) * (1 / sin(AA / 4))) * sin(AA),
      ( (-1 + 4 * cos(AA / 2)) * cos(AA)) / (cos(AA / 2) - cos(AA)),
    ],
    [0, 0],
  ];
  R12_3 = R12scale * [
    [
      (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [
      (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [
      3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2),
      1 + (2 * (1 + cos(AA) + cos((3 * AA) / 2))) / (cos(AA / 2) - cos(AA)),
    ],
    [
      3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2),
      (1 + 2 * cos(AA / 2) + 3 * cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [
      (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
  ];
  R12_4 = R12scale * [
    [
      (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [
      (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
    [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
    [3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2), 1 + 2 * cos(AA / 2)],
    [
      (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      1 + (1 + cos(AA / 2) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
    ],
  ];
  R12_5 = R12scale * [
    [
      (1 / 2) * (-3 * cos(AA / 4) - 4 * cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      2 + 1 / (-1 - 2 * cos(AA / 2)) + 1 / (-1 + cos(AA / 2)) + cos(AA / 2),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [0, 2],
    [0, 0],
    [
      ( -cos(AA / 4) - 2 * cos((3 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      2 + (2 + cos(AA / 2)) / ( -cos(AA / 2) + cos(AA)),
    ],
  ];
  R12_6 = R12scale * [
    [
      (1 / 2) * (-3 * cos(AA / 4) - 4 * cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      2 + 1 / (-1 - 2 * cos(AA / 2)) + 1 / (-1 + cos(AA / 2)) + cos(AA / 2),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (cos(AA / 4) + cos((3 * AA) / 4) + 2 * (cos((5 * AA) / 4) + cos((7 * AA) / 4))) * (1 / sin(3 * AA / 4)),
      (1 + 3 * cos(AA) + 2 * cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (-2 * (cos(AA / 4) + cos((3 * AA) / 4)) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (
        1 + cos(AA) + cos((3 * AA) / 2)
      ) / ( -cos(AA / 2) + cos(AA)),
    ],
  ];
  R12_7 = R12scale * [
    [
      (1 / 2) * (11 * cos(AA / 4) + 8 * cos((3 * AA) / 4) + 7 * cos((5 * AA) / 4) + 4 * cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      6 + 7 * cos(AA / 2) + 1 / (1 + 2 * cos(AA / 2)) + 4 * cos(AA) - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      2 * (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      -( (1 / 2) ) * (1 + 2 * cos((3 * AA) / 2)) * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
    ],
    [
      2 * (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      8 + 8 * cos(AA / 2) + 4 * cos(AA) - 3 / 2 * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
    ],
    [
      (5 * cos(AA / 4) + 4 * (cos((3 * AA) / 4) + cos((5 * AA) / 4)) + 2 * cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      6 + 8 * cos(AA / 2) + 1 / (1 + 2 * cos(AA / 2)) + 4 * cos(AA) - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
    ],
  ];
  R12_8 = R12scale * [
    [
      (1 / 2) * (11 * cos(AA / 4) + 8 * cos((3 * AA) / 4) + 7 * cos((5 * AA) / 4) + 4 * cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      6 + 7 * cos(AA / 2) + 1 / (1 + 2 * cos(AA / 2)) + 4 * cos(AA) - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (3 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (cos(AA) + 2 * cos((3 * AA) / 2)) / ( -cos(AA / 2) + cos(AA)),
    ],
    [
      (6 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4) + 2 * cos((7 * AA) / 4)) * (1 / sin(3 * AA / 4)),
      (3 * cos(AA) + cos((3 * AA) / 2) + 2 * cos(2 * AA)) / ( -cos(AA / 2) + cos(AA)),
    ],
  ];

  // offsets
  R12xoff = R12scale * [
    cos(AA / 4) / sin(AA / 4) + (2 * (3 + 4 * cos(AA / 2)) * sin(AA)) / (1 + 2 * cos(AA / 2)),
    -8 - 10 * cos(AA / 2) + 1 / (1 + 2 * cos(AA / 2)) - 4 * cos(AA) + 2 * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
  ];
  R12yoff = R12scale * [3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2), 1 + 2 * cos(AA / 2)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 13 PENTAGON DATA: Rice 1977
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R13scale = .7;

  // main pentagon
  R13 = R13scale * [
    [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
    [0, 1],
    [0, 0],
    [-1, 0],
    [-1 + 2 * cos(AA), 2 * sin(AA)],
  ];

  // other pentagons in the pattern
  R13_2 = R13scale * [
    [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
    [-3 + 3 * cos(AA) + sin(AA), -cos(AA) + 3 * sin(AA)],
    [3 * (-1 + cos(AA)), 3 * sin(AA)],
    [-3 + 2 * cos(AA), 2 * sin(AA)],
    [-1 + 2 * cos(AA), 2 * sin(AA)],
  ];
  R13_3 = R13scale * [
    [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
    [0, 1],
    [sin(AA), 1 - cos(AA)],
    [cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
    [-2 + cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
  ];
  R13_4 = R13scale * [
    [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
    [-3 + 3 * cos(AA) + sin(AA), -cos(AA) + 3 * sin(AA)],
    [-3 + 3 * cos(AA) + sin(AA), 1 - cos(AA) + 3 * sin(AA)],
    [-2 + 3 * cos(AA) + sin(AA), 1 - cos(AA) + 3 * sin(AA)],
    [-2 + cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
  ];
  R13_5 = R13scale * [
    [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
    [1, 0],
    [0, 0],
    [0, 1],
    [2 * sin(AA), 1 - 2 * cos(AA)],
  ];
  R13_6 = R13scale * [
    [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
    [-cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
    [3 * sin(AA), -3 * (-1 + cos(AA))],
    [2 * sin(AA), 3 - 2 * cos(AA)],
    [2 * sin(AA), 1 - 2 * cos(AA)],
  ];
  R13_7 = R13scale * [
    [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
    [1, 0],
    [1 - cos(AA), -sin(AA)],
    [1 - cos(AA) + sin(AA), -cos(AA) - sin(AA)],
    [1 - cos(AA) + sin(AA), 2 - cos(AA) - sin(AA)],
  ];
  R13_8 = R13scale * [
    [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
    [-cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
    [1 - cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
    [1 - cos(AA) + 3 * sin(AA), 2 - 3 * cos(AA) - sin(AA)],
    [1 - cos(AA) + sin(AA), 2 - cos(AA) - sin(AA)],
  ];

  // offsets
  R13xoff = R13scale * [1 - cos(AA) - sin(AA), -1 + cos(AA) - sin(AA)];
  R13yoff = R13scale * [3 * (-1 + cos(AA)) - 3 * sin(AA), 3 * (-1 + cos(AA)) + 3 * sin(AA)];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 14 PENTAGON DATA: Stein 1985
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R14scale = .52;

  // main pentagon
  R14 = R14scale * [
    [(1 / 8) * (-3 + sqrt(57)), 3.51623],
    [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
    [1, 0],
    [0, 0],
    [0, 2.6937],
  ];

  // other pentagons in the pattern
  R14_2 = R14scale * [
    [(1 / 8) * (3 - sqrt(57)), 3.51623],
    [(1 / 8) * (9 - 3 * sqrt(57)), 1.87118],
    [-1, 0],
    [0, 0],
    [0, 2.6937],
  ];
  R14_3 = R14scale * [
    [(1 / 4) * (1 + sqrt(57)), -1.64505],
    [1, 0],
    [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-1 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-1 + 3 * sqrt(57)), -0.822525],
  ];
  R14_4 = R14scale * [
    [(1 / 2) * (-1 + sqrt(57)), -1.64505],
    [(1 / 4) * (-5 + 3 * sqrt(57)), 0],
    [(1 / 8) * (7 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-1 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-1 + 3 * sqrt(57)), -0.822525],
  ];
  R14_5 = R14scale * [
    [(1 / 8) * (7 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
    [(1 / 8) * (-3 + sqrt(57)), 3.51623],
    [(1 / 4) * (-3 + sqrt(57)), 4.33875],
    [(1 / 16) * (31 + 3 * sqrt(57)), 2.80676],
  ];
  R14_6 = R14scale * [
    [-1, 0],
    [1, 0],
    [(1 / 4) * (1 + sqrt(57)), -1.64505],
    [(1 / 8) * (5 + sqrt(57)), -2.46757],
    [(3 / 16) * (-11 + sqrt(57)), -0.935588],
  ];

  // offsets
  R14xoff = R14scale * [(1 / 2) * (1 - sqrt(57)), 4.33875];
  R14yoff = R14scale * [(1 / 16) * (21 + sqrt(57)), 5.27434];

  ////////////////////////////////////////////////////////////////////////////////
  // TYPE 15 PENTAGON DATA: Mann/McLoud/VonDerau 2015!!
  // coordinates adapted from Ed Pegg's Wolfram demonstration
  // http://demonstrations.wolfram.com/PentagonTilings/  

  R15scale = .165;
  R15shift = [-1, 23];

  // main pentagon
  R15 = R15scale * [
    R15shift + [2 - sqrt(3), -17 - 6 * sqrt(3)],
    R15shift + [6 - sqrt(3), -17 - 6 * sqrt(3)],
    R15shift + [3 * (2 + sqrt(3)), -13 - 6 * sqrt(3)],
    R15shift + [6 + sqrt(3), -11 - 6 * sqrt(3)],
    R15shift + [2 - sqrt(3), -13 - 6 * sqrt(3)],
  ];

  // other pentagons in the pattern
  R15_2 = R15scale * [
    R15shift + [-sqrt(3), -13 - 4 * sqrt(3)],
    R15shift + [sqrt(3), -11 - 4 * sqrt(3)],
    R15shift + [8 + sqrt(3), -11 - 4 * sqrt(3)],
    R15shift + [6 + sqrt(3), -11 - 6 * sqrt(3)],
    R15shift + [2 - sqrt(3), -13 - 6 * sqrt(3)],
  ];
  R15_3 = R15scale * [
    R15shift + [6 + sqrt(3), -11 - 6 * sqrt(3)],
    R15shift + [8 + sqrt(3), -11 - 4 * sqrt(3)],
    R15shift + [8 + 5 * sqrt(3), -7 - 4 * sqrt(3)],
    R15shift + [8 + 5 * sqrt(3), -11 - 4 * sqrt(3)],
    R15shift + [3 * (2 + sqrt(3)), -13 - 6 * sqrt(3)],
  ];
  R15_4 = R15scale * [
    R15shift + [-sqrt(3), -13 - 4 * sqrt(3)],
    R15shift + [-2 - sqrt(3), -13 - 2 * sqrt(3)],
    R15shift + [-2 - sqrt(3), -5 - 2 * sqrt(3)],
    R15shift + [-2 + sqrt(3), -7 - 2 * sqrt(3)],
    R15shift + [sqrt(3), -11 - 4 * sqrt(3)],
  ];
  R15_5 = R15scale * [
    R15shift + [4 + sqrt(3), -11 - 4 * sqrt(3)],
    R15shift + [4 + sqrt(3), -7 - 4 * sqrt(3)],
    R15shift + [sqrt(3), -7],
    R15shift + [-2 + sqrt(3), -7 - 2 * sqrt(3)],
    R15shift + [sqrt(3), -11 - 4 * sqrt(3)],
  ];
  R15_6 = R15scale * [
    R15shift + [-2 + sqrt(3), -7 - 2 * sqrt(3)],
    R15shift + [sqrt(3), -7],
    R15shift + [sqrt(3), 1],
    R15shift + [-sqrt(3), -1],
    R15shift + [-2 - sqrt(3), -5 - 2 * sqrt(3)],
  ];
  R15_7 = R15scale * [
    R15shift + [-2 + sqrt(3), 17 + 6 * sqrt(3)],
    R15shift + [-6 + sqrt(3), 17 + 6 * sqrt(3)],
    R15shift + [-3 * (2 + sqrt(3)), 13 + 6 * sqrt(3)],
    R15shift + [-6 - sqrt(3), 11 + 6 * sqrt(3)],
    R15shift + [-2 + sqrt(3), 13 + 6 * sqrt(3)],
  ];
  R15_8 = R15scale * [
    R15shift + [sqrt(3), 13 + 4 * sqrt(3)],
    R15shift + [-sqrt(3), 11 + 4 * sqrt(3)],
    R15shift + [-8 - sqrt(3), 11 + 4 * sqrt(3)],
    R15shift + [-6 - sqrt(3), 11 + 6 * sqrt(3)],
    R15shift + [-2 + sqrt(3), 13 + 6 * sqrt(3)],
  ];
  R15_9 = R15scale * [
    R15shift + [-6 - sqrt(3), 11 + 6 * sqrt(3)],
    R15shift + [-8 - sqrt(3), 11 + 4 * sqrt(3)],
    R15shift + [-8 - 5 * sqrt(3), 7 + 4 * sqrt(3)],
    R15shift + [-8 - 5 * sqrt(3), 11 + 4 * sqrt(3)],
    R15shift + [-3 * (2 + sqrt(3)), 13 + 6 * sqrt(3)],
  ];
  R15_10 = R15scale * [
    R15shift + [sqrt(3), 13 + 4 * sqrt(3)],
    R15shift + [2 + sqrt(3), 13 + 2 * sqrt(3)],
    R15shift + [2 + sqrt(3), 5 + 2 * sqrt(3)],
    R15shift + [2 - sqrt(3), 7 + 2 * sqrt(3)],
    R15shift + [-sqrt(3), 11 + 4 * sqrt(3)],
  ];
  R15_11 = R15scale * [
    R15shift + [-4 - sqrt(3), 11 + 4 * sqrt(3)],
    R15shift + [-4 - sqrt(3), 7 + 4 * sqrt(3)],
    R15shift + [-sqrt(3), 7],
    R15shift + [2 - sqrt(3), 7 + 2 * sqrt(3)],
    R15shift + [-sqrt(3), 11 + 4 * sqrt(3)],
  ];
  R15_12 = R15scale * [
    R15shift + [2 - sqrt(3), 7 + 2 * sqrt(3)],
    R15shift + [-sqrt(3), 7],
    R15shift + [-sqrt(3), -1],
    R15shift + [sqrt(3), 1],
    R15shift + [2 + sqrt(3), 5 + 2 * sqrt(3)],
  ];

  // offsets
  R15xoff = R15scale * [2 * (1 + sqrt(3)), 2 * (3 + sqrt(3))];
  R15yoff = R15scale * [2 * (-8 - 5 * sqrt(3)), 2 * (9 + 4 * sqrt(3))];

  ////////////////////////////////////////////////////////////////////////////////
  // RENDERS

  function PentagonPattern(pentagon_type) =
    (pentagon_type == "R1") ?
      [R1, [R1, R1_2], R1xoff, R1yoff]
    : (pentagon_type == "R2") ? [R2, [R2, R2_2, R2_3, R2_4], R2xoff, R2yoff]
    : (pentagon_type == "R3") ?
      [R3, [R3, R3_2, R3_3], R3xoff, R3yoff]
    : (pentagon_type == "R4") ? [R4, [R4, R4_2, R4_3, R4_4], R4xoff, R4yoff]
    : (pentagon_type == "R5") ? [R5, [R5, R5_2, R5_3, R5_4, R5_5, R5_6], R5xoff, R5yoff]
    : (pentagon_type == "R6") ? [R6, [R6, R6_2, R6_3, R6_4], R6xoff, R6yoff]
    : (pentagon_type == "R7") ? [R7, [R7, R7_2, R7_3, R7_4, R7_5, R7_6, R7_7, R7_8], R7xoff, R7yoff]
    : (pentagon_type == "R8") ?
      [R8, [R8, R8_2, R8_3, R8_4, R8_5, R8_6, R8_7, R8_8], R8xoff, R8yoff]
    : (pentagon_type == "R9") ?
      [R9, [R9, R9_2, R9_3, R9_4, R9_5, R9_6, R9_7, R9_8], R9xoff, R9yoff]
    : (pentagon_type == "R10") ?
      [R10, [R10, R10_2, R10_3, R10_4, R10_5, R10_6], R10xoff, R10yoff]
    : (pentagon_type == "R11") ?
      [R11, [R11, R11_2, R11_3, R11_4, R11_5, R11_6, R11_7, R11_8], R11xoff, R11yoff]
    : (pentagon_type == "R12") ?
      [R12, [R12, R12_2, R12_3, R12_4, R12_5, R12_6, R12_7, R12_8], R12xoff, R12yoff]
    : (pentagon_type == "R13") ?
      [R13, [R13, R13_2, R13_3, R13_4, R13_5, R13_6, R13_7, R13_8], R13xoff, R13yoff]
    : (pentagon_type == "R14") ?
      [R14, [R14, R14_2, R14_3, R14_4, R14_5, R14_6], R14xoff, R14yoff]
    : (pentagon_type == "R15") ?
      [R15, [R15, R15_2, R15_3, R15_4, R15_5, R15_6, R15_7, R15_8, R15_9, R15_10, R15_11, R15_12], R15xoff, R15yoff]
    : [];

  pattern = PentagonPattern(pentagon_type);
 // echo(pattern[2], pattern[3], x, y);
  translate(pentagon_size * x * pattern[2])
    translate(pentagon_size * y * pattern[3])
      InnerPentagonTesselation(pattern);
}
