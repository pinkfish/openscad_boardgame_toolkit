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

// LibFile: base_bgtk.scad
//    This file has all the modules needed to generate varioius inserts
//    for board games.  It makes the generation of the inserts simpler by
//    creating a number of useful base modules for making boxes and lids
//    of various types specific to board game inserts.  Specifically it
//    makes tabbed lids and sliding lids easily.
//

// FileSummary: Basic pieces of the board game insert system.
// FileGroup: Basics

// Includes:
//   include <boardgame_toolkit.scad>

// Constant: m_piece_wiggle_room
// Description:
//   How many mm to use as gaps for when things join.
m_piece_wiggle_room = 0.2;

// Constant: default_lid_thickness
// Description: The default lid thickness for all boxes.
default_lid_thickness = 2;
// Constant: default_wall_thickness
// Description: The default wall thickness for all boxes.
default_wall_thickness = 2;
// Constant: default_floor_thickness
// Description: The default lid thickness for all boxes.
default_floor_thickness = 2;

// Constant: default_label_font
// Description: The default font to use for labels
default_label_font = "Stencil Std:style=Bold";

// Function: DefaultValue()
// Description:
//    Figures out the value, uses the input if it is not undefined, default if it is undefined.
// Arguments:
//    input = input value to check, only used if not undefined
//    default = default value to use, only used if the input is undefined.
function DefaultValue(input, default) = input == undef ? default : input;

// Constant: SHAPE_TYPE_DENSE_HEX
// Description:
//   Creates a shape with a dense hexes, so they overlap.
SHAPE_TYPE_DENSE_HEX = 1;
// Constant: SHAPE_TYPE_DENSE_TRIANGLE
// Description:
//   Creates a shape with a dense triangles, so they overlap.
SHAPE_TYPE_DENSE_TRIANGLE = 2;
// Constant: SHAPE_TYPE_CIRCLE
// Description:
//   Creates a shape with a circles.
SHAPE_TYPE_CIRCLE = 3;
// Constant: SHAPE_TYPE_HEX
// Description:
//   Creates a shape with a hexes.
SHAPE_TYPE_HEX = 4;
// Constant: SHAPE_TYPE_OCTOGON
// Description:
//   Creates a shape with a octogons.
SHAPE_TYPE_OCTOGON = 5;
// Constant: SHAPE_TYPE_TRIANGLE
// Description:
//   Creates a shape with a triangle.
SHAPE_TYPE_TRIANGLE = 6;
// Constant: SHAPE_TYPE_NONE
// Description:
//   Empty shape, no space filling.
SHAPE_TYPE_NONE = 7;
// Constant: SHAPE_TYPE_SQUARE
// Description:
//   Layout a nice set of squares.
SHAPE_TYPE_SQUARE = 8;
// Constant: SHAPE_TYPE_ROUNDED_SQUARE
// Description:
//   Layout a nice set of rounded squares.
SHAPE_TYPE_ROUNDED_SQUARE = 9;
// Constant: SHAPE_TYPE_HILBERT
// Description:
//   Layout a nice hilbert curve.
SHAPE_TYPE_HILBERT = 10;
// Constant: SHAPE_TYPE_CLOUD
// Description:
//   Makes a nice cloud shape.
SHAPE_TYPE_CLOUD = 11;