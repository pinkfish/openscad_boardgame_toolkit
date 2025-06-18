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
// Constant: default_slicing_layer_height
// The slicing layer height to use for cases where this matter.
default_slicing_layer_height = 0.2;

// Constant: default_material_colour
// Description: The default colour to use for material when making boxes.
default_material_colour = "yellow";
// Constant: default_label_colour
// Description: The default colour to use for the label when making boxes.
default_label_colour = "black";
// Constant: default_label_background_colour
// Description: The default colour to use for the label background when making boxes.
default_label_background_colour = "lime";

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
// Constant: SHAPE_TYPE_SUPERSHAPE
// Description:
//   Makes a nice [Superformula](https://en.wikipedia.org/wiki/Superformula) shape.
SHAPE_TYPE_SUPERSHAPE = 9;
// Constant: SHAPE_TYPE_HILBERT
// Description:
//   Layout a nice hilbert curve.
SHAPE_TYPE_HILBERT = 10;
// Constant: SHAPE_TYPE_CLOUD
// Description:
//   Makes a nice cloud shape.
SHAPE_TYPE_CLOUD = 11;
// Constant: SHAPE_TYPE_PENTAGON_R1
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R1 = 12;
// Constant: SHAPE_TYPE_PENTAGON_R2
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R2 = 13;
// Constant: SHAPE_TYPE_PENTAGON_R3
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R3 = 14;
// Constant: SHAPE_TYPE_PENTAGON_R4
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R4 = 15;
// Constant: SHAPE_TYPE_PENTAGON_R5
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R5 = 16;
// Constant: SHAPE_TYPE_PENTAGON_R6
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R6 = 17;
// Constant: SHAPE_TYPE_PENTAGON_R7
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R7 = 18;
// Constant: SHAPE_TYPE_PENTAGON_R8
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R8 = 19;
// Constant: SHAPE_TYPE_PENTAGON_R9
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R9 = 20;
// Constant: SHAPE_TYPE_PENTAGON_R10
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R10 = 21;
// Constant: SHAPE_TYPE_PENTAGON_R11
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R11 = 22;
// Constant: SHAPE_TYPE_PENTAGON_R12
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R12 = 23;
// Constant: SHAPE_TYPE_PENTAGON_R13
// Description:
//   Makes a nice repeating pentagon shape.
SHAPE_TYPE_PENTAGON_R13 = 24;

// Constant: CATCH_NONE
// Description:
//   No catch associated with the lid.
CATCH_NONE = 0;
// Constant: CATCH_LENGTH
// Description:
//   Catch on the length side
CATCH_LENGTH = 1;
// Constant: CATCH_WIDTH
// Description:
//   Catch on the width side.
CATCH_WIDTH = 2;

// Constant: LABEL_TYPE_FRAMED
// Description:
//   The label framed inside a box, with a striped background.
LABEL_TYPE_FRAMED = 0;
// Constant: LABEL_TYPE_FRAMED_SOLID
// Description:
//   The label framed inside a box, with a solid background.
LABEL_TYPE_FRAMED_SOLID = 1;
// Constant: LABEL_TYPE_FRAMED_SHORT
// Description:
//   The label framed inside a box, with a stripedbackground
//   on the short length.
LABEL_TYPE_FRAMED_SHORT = 2;
// Constant: LABEL_TYPE_FRAMED_SHORT_SOLID
// Description:
//   The label framed inside a box, with a solid background
//   on the short length.
LABEL_TYPE_FRAMED_SHORT_SOLID = 3;
// Constant: LABEL_TYPE_ANGLE
// Description:
//   The label on an angle across the lid.
LABEL_TYPE_ANGLE = 4;
// Constant: LABEL_TYPE_FRAMELESS
// Description:
//   The label across the lid on the long lenfth.
LABEL_TYPE_FRAMELESS = 4;
// Constant: LABEL_TYPE_FRAMELESS
// Description:
//   The label across the lid on the short length.
LABEL_TYPE_FRAMELESS_SHORT = 4;

// Constant: default_label_font
// Description: The default font to use for labels
default_label_font = "Stencil Std:style=Bold";
// Constant: default_label_solid_background
// Description: The default to use if the label should have a solid background or not.
default_label_solid_background = false;
// Constant: default_label_type
// Description: The detault type of label to use for all the lids.
default_label_type = LABEL_TYPE_FRAMED;

// Module: DifferenceWithOffset()
// Description:
//   Helper function that does an offset with the size inside the difference of the object
//   makes it easier for constructing outlines.
// Arguments:
//   offset = how much of an offset, -ve is inside the shape, +ve is outside the shape.
module DifferenceWithOffset(offset) {
  difference() {
    children();
    offset(delta=offset) children();
  }
}
