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

// LibFile: shape_type.scad
//    Used in the lids to generate shapes of specific types.

// FileSummary: Shapes for all sorts of things.
// FileGroup: Shapes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Shapes
//    Shapes to use in boxes and stuff.

// Function: ShapeNeedsInnerControl()
// Description:
//   If the specified shape needs inner control
// Arguments:
//   shnape_type = the type of shape to check
function ShapeNeedsInnerControl(shape_type) =
  (
    shape_type == SHAPE_TYPE_PENTAGON_R1 || shape_type == SHAPE_TYPE_PENTAGON_R3 || shape_type == SHAPE_TYPE_PENTAGON_R4 || shape_type == SHAPE_TYPE_PENTAGON_R5 || shape_type == SHAPE_TYPE_PENTAGON_R6 || shape_type == SHAPE_TYPE_PENTAGON_R7 || shape_type == SHAPE_TYPE_PENTAGON_R8 || shape_type == SHAPE_TYPE_PENTAGON_R9 || shape_type == SHAPE_TYPE_PENTAGON_R10 || shape_type == SHAPE_TYPE_PENTAGON_R11 || shape_type == SHAPE_TYPE_PENTAGON_R12 || shape_type == SHAPE_TYPE_PENTAGON_R13 || shape_type == SHAPE_TYPE_PENTAGON_R14 || shape_type == SHAPE_TYPE_PENTAGON_R15 || shape_type == SHAPE_TYPE_LIZARD || shape_type == SHAPE_TYPE_LEAF || shape_type == SHAPE_TYPE_HALF_REGULAR_HEXAGON || shape_type == SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL
  ) ?
    1
  : (shape_type == SHAPE_TYPE_VORONOI || shape_type == SHAPE_TYPE_PENTAGON_R2 || shape_type == SHAPE_TYPE_PENROSE_TILING_5 || shape_type == SHAPE_TYPE_PENROSE_TILING_7 || shape_type == SHAPE_TYPE_GOOSE || shape_type == SHAPE_TYPE_CHICKEN || shape_type == SHAPE_TYPE_SHEEP || shape_type == SHAPE_TYPE_BIRD || shape_type == SHAPE_TYPE_FLYING_BIRD ? 2 : 0);

// Module: ShapeByType()
// Description:
//   Creates shapes by a specific type to use in the lids.  This is pulled out so the shape creation
//   layout are handled independantly.
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, shape_width = 10));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 14));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 11));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DENSE_TRIANGLE, shape_thickness = 2, shape_width = 10));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 14));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_TRIANGLE, shape_thickness = 2, shape_width = 10));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_HEX, shape_thickness = 1, shape_width = 14));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 16));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 13, shape_aspect_ratio=1.25));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 10.5, shape_aspect_ratio=1));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11));
// Example:
//   default_lid_shape_rounding = 3;
//   ShapeByType(MakeShapeObject(shape_type= SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_CLOUD, shape_thickness = 2, shape_width = 11));
// Example(2D,Med):
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2));
// Example(2D,Big):
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//       supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   $polygon_grid_rows = 2;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R1, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_width = 50;
//   $polygon_length = 50;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R2, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_width = 50;
//   $polygon_length = 50;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R2, shape_thickness = 1, shape_width = 10, pentagon_first_angle_modifier=10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R3, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R4, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R5, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R6, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R7, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R8, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R9, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R10, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R11, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R12, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R13, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R14, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENTAGON_R15, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_LIZARD, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_HALF_REGULAR_HEXAGON, shape_thickness = 1, shape_width = 20));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DROP, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_VORONOI, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENROSE_TILING_5, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PENROSE_TILING_7, shape_thickness = 1, shape_width = 10));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DELTOID_TRIHEXAGONAL, shape_thickness = 1, shape_width = 10));
// Example:
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_DELTOID_TRIHEXAGONAL_KITE, shape_thickness = 1, shape_width = 10));
// Example:
//   $polygon_x = 0;
//   $polygon_y = 0;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_PEGASUS, shape_thickness = 1, shape_width = 25));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_GOOSE, shape_thickness = 1, shape_width = 25));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_CHICKEN, shape_thickness = 1, shape_width = 25));
// Example:
//   $polygon_width = 100;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SHEEP, shape_thickness = 1, shape_width = 25));
// Example:
//   $polygon_width = 101;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_BIRD, shape_thickness = 1, shape_width = 25));
// Example:
//   $polygon_width = 101;
//   $polygon_length = 100;
//   ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_FLYING_BIRD, shape_thickness = 1, shape_width = 25));
module ShapeByType(
  options
) {
  assert(options != undef, "Must specify options");

  calc_shape_type = options.shape_type;
  calc_shape_width = options.shape_width;
  calc_shape_thickness = options.shape_thickness;
  calc_rounding = options.rounding;
  calc_aspect_ratio = options.shape_aspect_ratio;

  calc_supershape_m1 = options.supershape_m1;
  calc_supershape_m2 = options.supershape_m2;
  calc_supershape_n1 = options.supershape_n1;
  calc_supershape_n2 = options.supershape_n2;
  calc_supershape_n3 = options.supershape_n3;
  calc_supershape_a = options.supershape_a;
  calc_supershape_b = options.supershape_b;

  if (calc_shape_type == SHAPE_TYPE_NONE) {
    // Don't do anything.
  } else {
    // Thin border around the pattern to stick it on.

    if (calc_shape_type == SHAPE_TYPE_DENSE_HEX) {
      difference() {
        regular_ngon(or=calc_shape_width / 2 + calc_shape_thickness / 2, n=6, rounding=calc_rounding);
        regular_ngon(or=calc_shape_width / 2 - calc_shape_thickness / 2, n=6, rounding=calc_rounding);
      }
    } else if (calc_shape_type == SHAPE_TYPE_DENSE_TRIANGLE) {
      side_length = calc_shape_width / 2 * sqrt(3);
      difference() {
        regular_ngon(or=calc_shape_width / 2 + calc_shape_thickness / 2, n=3, rounding=calc_rounding);
        regular_ngon(or=calc_shape_width / 2 - calc_shape_thickness / 2, n=3, rounding=calc_rounding);
      }
    } else if (calc_shape_type == SHAPE_TYPE_CIRCLE) {
      difference() {
        circle(r=calc_shape_width / 2 + calc_shape_thickness / 4);
        circle(r=(calc_shape_width - calc_shape_thickness / 2) / 2);
      }
    } else if (
      calc_shape_type == SHAPE_TYPE_TRIANGLE || calc_shape_type == SHAPE_TYPE_HEX || calc_shape_type == SHAPE_TYPE_OCTOGON || calc_shape_type == SHAPE_TYPE_SQUARE
    ) {
      shape_edges =
        calc_shape_type == SHAPE_TYPE_TRIANGLE ? 3
        : (calc_shape_type == SHAPE_TYPE_HEX ? 6 : (calc_shape_type == SHAPE_TYPE_SQUARE ? 4 : 8));
      difference() {
        regular_ngon(
          r=calc_shape_width / 2 + (calc_shape_type == SHAPE_TYPE_TRIANGLE ? calc_shape_thickness * 1.5 : calc_shape_thickness / 4),
          n=shape_edges, rounding=calc_rounding
        );
        regular_ngon(
          r=(calc_shape_width - (calc_shape_type == SHAPE_TYPE_TRIANGLE ? calc_shape_thickness * 0.5 : calc_shape_thickness / 2)) / 2,
          n=shape_edges,
          rounding=calc_rounding,
        );
      }
    } else if (calc_shape_type == SHAPE_TYPE_SUPERSHAPE) {
      difference() {
        DifferenceWithOffset(offset=-calc_shape_thickness) supershape(
            d=calc_shape_width, m1=calc_supershape_m1, m2=calc_supershape_m2, n1=calc_supershape_n1,
            n2=calc_supershape_n2, n3=calc_supershape_n3, a=calc_supershape_a, b=calc_supershape_b,
          );
      }
    } else if (calc_shape_type == SHAPE_TYPE_CLOUD) {
      translate([-calc_shape_width / 2, -calc_shape_width / 2]) difference() {
          resize([calc_shape_width * calc_aspect_ratio, calc_shape_width]) {
            CloudShape2d(width=calc_shape_width);
          }
          offset(delta=-calc_shape_thickness) resize([calc_shape_width * calc_aspect_ratio, calc_shape_width]) {
              CloudShape2d(width=calc_shape_width);
            }
        }
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R1) {
      translate([($polygon_grid_rows * calc_shape_width) / 2, 0])
        PentagonTesselation(
          pentagon_type="R1", pentagon_size=calc_shape_width,
          thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
          first_angle_modifier=options.pentagon_first_angle_modifier,
          second_angle_modifier=options.pentagon_second_angle_modifier,
          first_length_modifier=options.pentagon_first_length_modifier,
          second_length_modifier=options.pentagon_second_length_modifier,
          third_length_modifier=options.pentagon_third_length_modifier,
        );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R2) {
      PentagonTesselationArea(
        pentagon_type="R2",
        width=$polygon_width,
        length=$polygon_length,
        pentagon_size=calc_shape_width,
        thickness=calc_shape_thickness / 2,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
        spin=60
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R3) {
      PentagonTesselation(
        pentagon_type="R3", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R4) {
      PentagonTesselation(
        pentagon_type="R4", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R5) {
      PentagonTesselation(
        pentagon_type="R5", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R6) {
      PentagonTesselation(
        pentagon_type="R6", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R7) {
      PentagonTesselation(
        pentagon_type="R7", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R8) {
      PentagonTesselation(
        pentagon_type="R8", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R9) {
      PentagonTesselation(
        pentagon_type="R9", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R10) {
      PentagonTesselation(
        pentagon_type="R10", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R11) {
      PentagonTesselation(
        pentagon_type="R11", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R12) {
      PentagonTesselation(
        pentagon_type="R12", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R13) {
      PentagonTesselation(
        pentagon_type="R13", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R14) {
      PentagonTesselation(
        pentagon_type="R14", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENTAGON_R15) {
      PentagonTesselation(
        pentagon_type="R15", pentagon_size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0,
        first_angle_modifier=options.pentagon_first_angle_modifier,
        second_angle_modifier=options.pentagon_second_angle_modifier,
        first_length_modifier=options.pentagon_first_length_modifier,
        second_length_modifier=options.pentagon_second_length_modifier,
        third_length_modifier=options.pentagon_third_length_modifier,
      );
    } else if (calc_shape_type == SHAPE_TYPE_LIZARD) {
      LizardRepeatAtLocation(size=calc_shape_width, thickness=calc_shape_thickness / 2, x=$polygon_x ? floor($polygon_grid_rows / 2) - $polygon_x : 0, y=$polygon_y ? floor($polygon_grid_cols / 2) - $polygon_y : 0, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_CHICKEN) {
      TesselationHexKiteArea(
        size=calc_shape_width, width=$polygon_width, length=$polygon_length
      )
        rotate(30)
          TesselationChickenHex(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_VORONOI) {
      Voronoi(width=$polygon_width, length=$polygon_length, cellsize=calc_shape_width, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_GOOSE) {
      TesselationGooseArea(
        width=$polygon_width, length=$polygon_length, thickness=calc_shape_thickness,
        size=calc_shape_width
      );
    } else if (calc_shape_type == SHAPE_TYPE_BIRD) {
      TesselationBirdArea(
        width=$polygon_width, length=$polygon_length, thickness=calc_shape_thickness,
        size=calc_shape_width
      );
    } else if (calc_shape_type == SHAPE_TYPE_FLYING_BIRD) {
      TesselationFlyingBirdArea(
        width=$polygon_width, length=$polygon_length, thickness=calc_shape_thickness,
        size=calc_shape_width
      );
    } else if (calc_shape_type == SHAPE_TYPE_SHEEP) {
      SheepTesselationArea(
        size=calc_shape_width, thickness=calc_shape_thickness / 2,
        width=$polygon_width,
        length=$polygon_length
      );
    } else if (calc_shape_type == SHAPE_TYPE_PENROSE_TILING_5) {
      max_width = max($polygon_width, $polygon_length);
      PenroseTiling(max_width * 1.5, divisions=ceil((max_width * 2 / calc_shape_width) / 3), base=5, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_PENROSE_TILING_7) {
      max_width = max($polygon_width, $polygon_length);
      PenroseTiling(max_width * 1.5, divisions=ceil((max_width * 2 / calc_shape_width) / 3), base=7, thickness=calc_shape_thickness);
    } else if (calc_shape_type == SHAPE_TYPE_DROP) {
      TesselationDrop(size=[calc_shape_width, calc_shape_width * calc_aspect_ratio], thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_DELTOID_TRIHEXAGONAL) {
      DeltoidTrihexagonalTiling(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_DELTOID_TRIHEXAGONAL_KITE) {
      DeltoidTrihexagonalTiling(size=calc_shape_width, thickness=calc_shape_thickness / 2, outer_offset=0.1, kite=true);
    } else if (calc_shape_type == SHAPE_TYPE_PEGASUS) {
      TesselationPegasus(size=[calc_shape_width, calc_shape_width * calc_aspect_ratio], thickness=calc_shape_thickness / 2, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_HALF_REGULAR_HEXAGON) {
      // Multiply size by three since this breaks the triangle up into three.
      TriangleTesselationRepeatAtLocation(
        size=calc_shape_width * 3, x=$polygon_x, y=$polygon_y
      )
        HalfRegularHexagon(size=calc_shape_width * 3, thickness=calc_shape_thickness, outer_offset=0.1);
    } else if (calc_shape_type == SHAPE_TYPE_RHOMBI_TRI_HEXAGONAL) {
      HexagonTesselationRepeatAtLocation(
        size=calc_shape_width / 2, x=$polygon_x, y=$polygon_y
      )
        RhombiTriHexagonal(calc_shape_width);
    } else if (calc_shape_type == SHAPE_TYPE_LEAF) {
      section = calc_shape_width / 4;
      section_height = section * calc_sqrt_three / 2;
      pos = ($polygon_x % 4);
      offset = (
        pos == 0 ?
          0
        : pos == 1 ?
          section * 2
        : pos == 2 ?
          section * 4
        : section * 6
      );
      translate(
        [
          $polygon_x * section_height * 6 + ($polygon_y % 2) * section_height * 2,
          $polygon_y * section * 4 - offset,
        ]
      ) {
        rotate(($polygon_y % 2) * 180)
          TesselationLeafOutlineThree(
            size=calc_shape_width + 0.1,
            thickness=calc_shape_thickness / 2,
            vein_thickness=calc_shape_thickness / 4,
            with_veins=false
          );
      }
    } else if (calc_shape_type == SHAPE_TYPE_LEAF_VEINS) {
      section = calc_shape_width / 4;
      section_height = section * calc_sqrt_three / 2;
      pos = ($polygon_x % 4);
      offset = (
        pos == 0 ?
          0
        : pos == 1 ?
          section * 2
        : pos == 2 ?
          section * 4
        : section * 6
      );
      translate(
        [
          $polygon_x * section_height * 6 + ($polygon_y % 2) * section_height * 2,
          $polygon_y * section * 4 - offset,
        ]
      ) {
        rotate(($polygon_y % 2) * 180)
          TesselationLeafOutlineThree(
            size=calc_shape_width + 0.1,
            thickness=calc_shape_thickness / 2,
            vein_thickness=calc_shape_thickness / 4,
            with_veins=true
          );
      }
    } else {
      assert(false, str("Invalid shape type type=", calc_shape_type));
    }
  }
}
