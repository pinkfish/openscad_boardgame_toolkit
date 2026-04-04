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

include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

module CardLibraryBox(
  size,
  floor_thickness = default_floor_thickness,
  wall_thickness = default_wall_thickness,
  lip_size = default_floor_thickness * 3,
  material_colour = "magenta"
) // `make` me
{
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width,length, height > 0 width=", width, " length=", length, " height=", height));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));

  height_without_hinge = height - wall_thickness * 2;
  difference() {
    union() {
      difference() {
        color(material_colour) diff() {
            cuboid(
              [width, length, height_without_hinge], anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            ) {
              face_profile(TOP, r=wall_thickness / 2)
                mask2d_roundover(wall_thickness / 2);
              face_profile(BOTTOM, r=wall_thickness / 2)
                mask2d_roundover(wall_thickness / 2);
              corner_profile("ALL", r=wall_thickness / 2) mask2d_roundover(wall_thickness / 2);
            }
          }

        translate([wall_thickness, wall_thickness, floor_thickness]) color(material_colour) {
            cuboid(
              [width, length - (wall_thickness) * 2, height_without_hinge],
              rounding=wall_thickness / 4,
              anchor=BOTTOM + LEFT + FRONT
            );
          }
      }
      translate([0, length/8, height_without_hinge - wall_thickness])
        difference() {
          cuboid(
            [wall_thickness * 2, length*3/4, wall_thickness * 3], anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness, edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + RIGHT],
          );
          translate([wall_thickness, 0, wall_thickness * 1.5])
            ycyl(d=wall_thickness, h=length, anchor=BOTTOM);
        }
      color(material_colour)
        translate([width - wall_thickness, wall_thickness + 0.01, floor_thickness - 0.01])
          cuboid(
            [wall_thickness, length - wall_thickness * 2 + 0.02, lip_size],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness, edges=[TOP + RIGHT]
          );
    }

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

CardLibraryBox(size=[100, 200, 300]);
