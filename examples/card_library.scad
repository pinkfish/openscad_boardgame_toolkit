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
include <lib/dominion.scad>

CARD_LIBRARY_LATCH_SLIDING = "sliding";
CARD_LIBRARY_LATCH_CLIP = "clip";
CARD_LIBRARY_LATCH_NONE = "none";

module MakeCardLibraryBox(
  size,
  floor_thickness = default_floor_thickness,
  wall_thickness = default_wall_thickness,
  lip_size = default_floor_thickness * 3,
  lid_thickness = default_lid_thickness,
  material_colour = "magenta",
  latch = CARD_LIBRARY_LATCH_SLIDING,
  hinge_hole_diameter = 2.2 // default for a filemeter as a hinge.
) // `make` me
{
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width,length, height > 0 width=", width, " length=", length, " height=", height));
  assert(floor_thickness > 0, str("Need floor thickness > 0, floor_thickness=", floor_thickness));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(lip_size > 0, str("Need lip size > 0, lip_size=", lip_size));
  assert(hinge_hole_diameter > 0, str("Need hinge hole diameter > 0, hinge_hole_diameter=", hinge_hole_diameter));

  height_without_hinge = height - lid_thickness;
  edge_size = max(length / 6, 20);

  difference() {
    union() {
      difference() {
        color(material_colour) diff() {
            cuboid(
              [width, length, height_without_hinge], anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            ) {
              edge_profile([TOP + FRONT, TOP + BACK, TOP + RIGHT])
                mask2d_roundover(wall_thickness / 4);
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

        // Put in the holes for the sliding latch.
        if (latch == CARD_LIBRARY_LATCH_SLIDING) {
          translate([width * 3 / 4, 0, height_without_hinge + lid_thickness]) {
            translate([wall_thickness / 4, -0.01, -wall_thickness])
              cuboid(
                [wall_thickness * 2.5, wall_thickness + 0.02, wall_thickness],
                anchor=TOP + FRONT + LEFT,
              );
          }
          translate([width * 3 / 4, length, height_without_hinge + lid_thickness]) {
            translate([wall_thickness / 4, 0.01, -wall_thickness])
              cuboid(
                [wall_thickness * 2.5, wall_thickness + 0.02, wall_thickness],
                anchor=TOP + BACK + LEFT,
              );
          }
        }
      }

      // Hinge section
      translate([0, edge_size + 0.2, height_without_hinge - wall_thickness])
        color(material_colour)
          difference() {
            cuboid(
              [wall_thickness * 2, length - edge_size * 2 - 0.4, wall_thickness + lid_thickness], anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness, edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + RIGHT],
            );
          }
      // Hinge Support      
      translate([0, wall_thickness - 0.01, height_without_hinge]) {
        color(material_colour)
          cuboid(
            [wall_thickness * 2, length - wall_thickness * 2 + 0.02, height_without_hinge / 6],
            anchor=TOP + FRONT + LEFT,
            chamfer=wall_thickness,
            edges=[BOTTOM + RIGHT]
          );
      }

      // Latch
      if (latch == CARD_LIBRARY_LATCH_CLIP) {
        color(material_colour)
          translate([width * 3 / 4, 0, height_without_hinge + lid_thickness]) {
            difference() {
              cuboid(
                [wall_thickness * 3, wall_thickness, lid_thickness * 2],
                rounding=wall_thickness / 4,
                anchor=TOP + FRONT + LEFT,
                edges=[LEFT + FRONT, RIGHT + FRONT, TOP + FRONT]
              );
              translate([wall_thickness / 2, wall_thickness / 2 + 0.01, -wall_thickness / 2])
                cuboid(
                  [wall_thickness * 2, wall_thickness / 2, wall_thickness / 2],
                  chamfer=wall_thickness / 2,
                  anchor=TOP + FRONT + LEFT,
                  edges=[BOTTOM + FRONT]
                );
            }
          }
        color(material_colour)
          translate([width * 3 / 4, length, height_without_hinge + lid_thickness]) {
            difference() {
              cuboid(
                [wall_thickness * 3, wall_thickness, lid_thickness * 2],
                rounding=wall_thickness / 4,
                anchor=TOP + BACK + LEFT,
                edges=[RIGHT + BACK, LEFT + BACK, TOP + BACK]
              );
              translate([wall_thickness / 2, -wall_thickness / 2 - 0.01, -wall_thickness / 2])
                cuboid(
                  [wall_thickness * 2, wall_thickness / 2, wall_thickness / 2],
                  chamfer=wall_thickness / 2,
                  anchor=TOP + BACK + LEFT,
                  edges=[BOTTOM + BACK]
                );
            }
          }
      }

      if (latch == CARD_LIBRARY_LATCH_SLIDING) {
        color(material_colour)
          translate([width * 3 / 4, 0, height_without_hinge + lid_thickness]) {
            difference() {
              cuboid(
                [wall_thickness * 3, wall_thickness, lid_thickness * 2],
                rounding=wall_thickness / 4,
                anchor=TOP + FRONT + LEFT,
                edges=[LEFT + FRONT, RIGHT + FRONT, TOP + FRONT]
              );
              translate([wall_thickness / 2 - 0.1, -0.01, -wall_thickness])
                prismoid(
                  size1=[wall_thickness + 0.2, wall_thickness + 0.2],
                  size2=[wall_thickness * 2 + 0.2, wall_thickness + 0.2],
                  h=wall_thickness + 0.02,
                  shift=[0, 0],
                  anchor=TOP + FRONT + LEFT,
                );
            }
          }

        color(material_colour)
          translate([width * 3 / 4, length, height_without_hinge + lid_thickness]) {
            difference() {
              cuboid(
                [wall_thickness * 3, wall_thickness, lid_thickness * 2],
                rounding=wall_thickness / 4,
                anchor=TOP + BACK + LEFT,
                edges=[RIGHT + BACK, LEFT + BACK, TOP + BACK]
              );
              translate([wall_thickness / 2 - 0.1, 0.01, -wall_thickness])
                prismoid(
                  size1=[wall_thickness + 0.2, wall_thickness + 0.2],
                  size2=[wall_thickness * 2 + 0.2, wall_thickness + 0.2],
                  h=wall_thickness + 0.02,
                  shift=[0, 0],
                  anchor=TOP + BACK + LEFT,
                );
            }
          }
      }

      // front lip.
      translate([width - wall_thickness, wall_thickness + 0.01, floor_thickness - 0.01]) {
        color(material_colour)
          cuboid(
            [wall_thickness, length - wall_thickness * 2 + 0.02, lip_size],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness, edges=[TOP + RIGHT]
          );
        translate([-wall_thickness / 2, 0, lip_size - wall_thickness])
          color(material_colour)
            cuboid(
              [wall_thickness, length - wall_thickness * 2 + 0.02, wall_thickness],
              anchor=BOTTOM + FRONT + LEFT,
              chamfer=wall_thickness / 2, edges=[BOTTOM + LEFT]
            );
      }
    }

    // Remove the hinge space.
    translate([-0.01, -0.01, height_without_hinge - default_wall_thickness])
      cuboid(
        [wall_thickness * 2 + 0.02, edge_size + 0.2, wall_thickness + 0.01],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=-wall_thickness,
        edges=[TOP + RIGHT]
      );

    // Remove the hinge space.
    translate([-0.01, length + 0.01, height_without_hinge - default_wall_thickness])
      cuboid(
        [wall_thickness * 2 + 0.02, edge_size + 0.2, wall_thickness + 0.01],
        anchor=BOTTOM + LEFT + BACK,
        rounding=-wall_thickness,
        edges=[TOP + RIGHT]
      );

    translate([wall_thickness, 0, height_without_hinge - wall_thickness / 2])
      ycyl(d=hinge_hole_diameter, h=length, anchor=BOTTOM);

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

module SlidingChannel(size, wall_thickness) {
  width = size[0];
  length = size[1];
  height = size[2];
  translate([-height, 0, 0]) {
    diff() cuboid(
        [height * 2, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        chamfer=height,
        edges=[BOTTOM + RIGHT]
      ) {
        edge_profile([TOP + LEFT])
          mask2d_roundover(height / 2);
      }
  }
  translate([width - height, 0, 0]) {
    diff() cuboid(
        [height * 2, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        chamfer=height,
        edges=[BOTTOM + LEFT]
      ) {
        edge_profile([TOP + RIGHT])
          mask2d_roundover(height / 2);
      }
  }
}

module SlidingLatch(size, print_in_place_offset, lid_thickness, wall_thickness) {
  width = size[0];
  length = size[1];
  height = size[2];
  translate([0, 0, lid_thickness + print_in_place_offset])
    prismoid(
      size1=[width - print_in_place_offset, length - wall_thickness * 4 - print_in_place_offset * 2],
      size2=[width - wall_thickness * 2, length - wall_thickness * 4 - print_in_place_offset * 2],
      h=wall_thickness - print_in_place_offset,
      anchor=BOTTOM + FRONT + LEFT,
    );
  translate([print_in_place_offset, wall_thickness * 5.5 - print_in_place_offset, 0])
    cuboid(
      [width - print_in_place_offset * 2, wall_thickness, lid_thickness + print_in_place_offset],
      anchor=BOTTOM + FRONT + LEFT,
    );
  translate([print_in_place_offset, wall_thickness * 3 + print_in_place_offset, 0])
    cuboid(
      [width - print_in_place_offset * 2, wall_thickness * 2.5 - print_in_place_offset * 3, lid_thickness],
      anchor=BOTTOM + FRONT + LEFT,
    );
}

module CardLibraryBoxLid(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  lip_size = default_lid_thickness * 3,
  lid_boundary = 10,
  latch = CARD_LIBRARY_LATCH_SLIDING,
  material_colour = "magenta",
  hinge_hole_diameter = 2.2,
  print_in_place_offset = 0.25,
  size_spacing = m_piece_wiggle_room,
) {
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width,length, height > 0 width=", width, " length=", length, " height=", height));
  assert(wall_thickness > 0, str("Need walll thickness > 0, wall_thickness=", wall_thickness));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(lip_size > 0, str("Need lip size > 0, lip_size=", lip_size));
  assert(hinge_hole_diameter > 0, str("Need hinge hole diameter > 0, hinge_hole_diameter=", hinge_hole_diameter));

  edge_size = max(length / 6, 20);
  difference() {
    union() {
      internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
        difference() {
          union() {
            color(material_colour)
              cuboid(
                [
                  width,
                  length,
                  lid_thickness,
                ],
                anchor=BOTTOM + FRONT + LEFT,
                rounding=wall_thickness / 2,
                edges=[BOTTOM]
              );
            color(material_colour)
              cuboid(
                [wall_thickness * 2, edge_size, lid_thickness + wall_thickness],
                anchor=BOTTOM + FRONT + LEFT,
                rounding=wall_thickness,
                edges=[TOP + LEFT, TOP + RIGHT]
              );
            translate([0, length - edge_size, 0])
              color(material_colour)
                cuboid(
                  [wall_thickness * 2, edge_size, lid_thickness + wall_thickness],
                  anchor=BOTTOM + FRONT + LEFT,
                  rounding=wall_thickness,
                  edges=[TOP + LEFT, TOP + RIGHT]
                );

            translate([width - wall_thickness, wall_thickness + 0.5, 0])
              color(material_colour)
                cuboid(
                  [wall_thickness, length - wall_thickness * 2 - 1, lid_thickness + lip_size],
                  anchor=BOTTOM + FRONT + LEFT,
                  rounding=wall_thickness / 2,
                  edges=[TOP + LEFT, TOP + RIGHT],
                );

            if (latch == CARD_LIBRARY_LATCH_SLIDING) {
              translate([width * 3 / 4 - print_in_place_offset, wall_thickness, lid_thickness])
                color(material_colour)
                  SlidingChannel([wall_thickness * 3 + print_in_place_offset * 2, edge_size, wall_thickness]);
              translate([width * 3 / 4 - print_in_place_offset, edge_size, lid_thickness])
                color(material_colour)
                  cuboid(
                    [wall_thickness * 3 + 0.5, wall_thickness, wall_thickness],
                    edges=[TOP + LEFT, TOP + RIGHT],
                    anchor=BOTTOM + FRONT + LEFT
                  );
              translate([width * 3 / 4 - print_in_place_offset, length - edge_size - wall_thickness, lid_thickness])
                color(material_colour)
                  SlidingChannel([wall_thickness * 3 + 0.5, edge_size, wall_thickness]);
              translate([width * 3 / 4 - print_in_place_offset, length - edge_size - wall_thickness, lid_thickness])
                color(material_colour)
                  cuboid(
                    [wall_thickness * 3 + print_in_place_offset * 2, wall_thickness, wall_thickness],
                    edges=[TOP + LEFT, TOP + RIGHT],
                    anchor=BOTTOM + FRONT + LEFT
                  );
              translate([wall_thickness, wall_thickness + 0.5, 0])
                color(material_colour) cuboid(
                    [lid_boundary - wall_thickness, length - wall_thickness * 2 + 1, lid_thickness + wall_thickness],
                    anchor=BOTTOM + FRONT + LEFT,
                  );
            }
            if (latch == CARD_LIBRARY_LATCH_CLIP) {
            }
          }
          translate([wall_thickness, length / 2 - 1, wall_thickness / 2])
            ycyl(d=hinge_hole_diameter, h=length + 3, anchor=BOTTOM);

          translate([-1, edge_size, -1]) {
            cuboid(
              [wall_thickness * 2 + 1, length - edge_size * 2, lid_thickness + wall_thickness * 2],
              anchor=BOTTOM + FRONT + LEFT,
            );
          }

          if (latch == CARD_LIBRARY_LATCH_SLIDING) {
            // Holes in the side for the sides
            translate([width * 3 / 4 - print_in_place_offset, -0.01, -0.01]) {
              cuboid(
                [wall_thickness * 3 + print_in_place_offset * 2, wall_thickness + 0.02, lid_thickness * 2],
                anchor=BOTTOM + FRONT + LEFT,
              );
            }
            translate([width * 3 / 4 - print_in_place_offset, length + 0.01, -0.01]) {
              cuboid(
                [wall_thickness * 3 + print_in_place_offset * 2, wall_thickness + 0.02, lid_thickness * 2],
                anchor=BOTTOM + BACK + LEFT,
              );
            }
          }
          if (latch == CARD_LIBRARY_LATCH_CLIP) {
          }
        }

        $inner_width = width - wall_thickness * 2;
        $inner_length = length - wall_thickness * 2;
        $inner_height = lid_thickness;

        if ($children > 0) {
          children(0);
        }

        if ($children > 1) {
          children(1);
        }

        if (latch == CARD_LIBRARY_LATCH_SLIDING) {
          // Lid pieces to support the slides.
          difference() {
            union() {
              translate([width * 3 / 4 - print_in_place_offset - wall_thickness, wall_thickness, 0]) {
                color(material_colour)
                  cuboid(
                    [wall_thickness * 5 + print_in_place_offset * 2, edge_size, lid_thickness],
                    anchor=BOTTOM + FRONT + LEFT,
                  );
              }
              translate([width * 3 / 4 - print_in_place_offset - wall_thickness, length - edge_size - wall_thickness, 0]) {
                color(material_colour)
                  cuboid(
                    [wall_thickness * 5 + print_in_place_offset * 2, edge_size, lid_thickness],
                    anchor=BOTTOM + FRONT + LEFT,
                  );
              }
            }
            // Holes for the handle in the lid.
            translate([width * 3 / 4, wall_thickness * 4, lid_thickness + 0.01]) {
              cuboid(
                [wall_thickness * 3, wall_thickness * 3.5 + 0.02, lid_thickness + 1],
                anchor=TOP + FRONT + LEFT,
              );
            }
            translate([width * 3 / 4 - print_in_place_offset, length - wall_thickness * (4 + 3.5), lid_thickness + 0.01]) {
              cuboid(
                [wall_thickness * 3, wall_thickness * 3.5 + 0.02, lid_thickness + 1],
                anchor=TOP + FRONT + LEFT,
              );
            }
          }
        }

        if ($children > 2) {
          children(2);
        }
        if ($children > 3) {
          children(3);
        }
        if ($children > 4) {
          children(4);
        }
        if ($children > 5) {
          children(5);
        }
      }

      // The floating sliding latch.
      if (latch == CARD_LIBRARY_LATCH_SLIDING) {
        // First latch.
        color(material_colour)
          translate([width * 3 / 4, wall_thickness, 0]) {
            SlidingLatch(
              size=[
                wall_thickness * 3,
                edge_size,
                lid_thickness,
              ],
              print_in_place_offset=print_in_place_offset,
              lid_thickness=lid_thickness,
              wall_thickness=wall_thickness
            );
          }
        color(material_colour)
          translate([width * 3 / 4 + wall_thickness * 3 - print_in_place_offset, length - wall_thickness, 0]) {
            rotate(180)
              SlidingLatch(
                size=[
                  wall_thickness * 3,
                  edge_size,
                  lid_thickness,
                ],
                print_in_place_offset=print_in_place_offset,
                lid_thickness=lid_thickness,
                wall_thickness=wall_thickness
              );
          }
      }
    }
  }
}

module CardLibraryBoxLidWithCustomShape(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  lip_size = default_lid_thickness * 3,
  latch = CARD_LIBRARY_LATCH_SLIDING,
  material_colour = "magenta",
  hinge_hole_diameter = 2.2,
  print_in_place_offset = 0.25,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  aspect_ratio = 1.0,
  pattern_inner_control = false,
  lid_boundary = 10,
  layout_width = undef,
) {
  CardLibraryBoxLid(
    size=size,
    wall_thickness=wall_thickness,
    lid_thickness=lid_thickness,
    lip_size=lip_size,
    latch=latch,
    material_colour=material_colour,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    lid_boundary=lid_boundary,
    size_spacing=size_spacing,
  ) {
    LidMeshBasic(
      size=[
        size[0] - wall_thickness,
        size[1] - wall_thickness,
      ], lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
      dense_shape_edges=lid_dense_shape_edges, material_colour=material_colour,
      inner_control=pattern_inner_control
    ) {
      if ($children > 0) {
        children(0);
      } else {
        color(material_colour) square([10, 10]);
      }
    }
    // Don't include the first child since is it used for the lid shape.
    if ($children > 1) {
      children(1);
    }
    if ($children > 2) {
      children(2);
    }
    if ($children > 3) {
      children(3);
    }
    if ($children > 4) {
      children(4);
    }
    if ($children > 5) {
      children(5);
    }
    if ($children > 6) {
      children(6);
    }
  }
}

module CardLibraryBoxLidWithShape(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  lip_size = default_lid_thickness * 3,
  latch = CARD_LIBRARY_LATCH_SLIDING,
  material_colour = "magenta",
  hinge_hole_diameter = 2.2,
  print_in_place_offset = 0.25,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  pattern_inner_control = false,
  shape_options = undef,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = undef,
  shape_options = undef
) {
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );
  CardLibraryBoxLidWithCustomShape(
    size=size,
    wall_thickness=wall_thickness,
    lid_thickness=lid_thickness,
    lip_size=lip_size,
    latch=latch,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
  ) {
    color(material_colour)
      ShapeByType(
        options=calc_shape_options,
      );

    if ($children > 0) {
      children(0);
    }
    if ($children > 1) {
      children(1);
    }
    if ($children > 2) {
      children(2);
    }
    if ($children > 3) {
      children(3);
    }
    if ($children > 4) {
      children(4);
    }
    if ($children > 5) {
      children(5);
    }
    if ($children > 6) {
      children(6);
    }
    if ($children > 7) {
      children(7);
    }
    if ($children > 8) {
      children(8);
    }
  }
}

module CardSleeveForLibrary(
  size,
  wall_thickness = default_wall_thickness,
  side_wall_thickness = default_wall_thickness / 2,
  lip_size = default_floor_thickness * 3,
  material_colour = "magenta",
  font = default_label_font,
  label_colour = default_label_colour,
  label = "",
  add_positive = false,
  emboss_text = 0.2,
  text_length_offset = default_wall_thickness * 3
) {
  translate([size[0], size[1], 0])
    rotate([0, 0, 180]) {
      width = size[0];
      length = size[1];
      height = size[2];

      metrics = textmetrics(label, font=font);

      text_length = height - text_length_offset - wall_thickness / 2;
      text_width = length - wall_thickness;
      text_aspect = metrics.size[1] / metrics.size[0];
      text_use_length = text_width / text_aspect > text_length;

      text_new_width = text_use_length ? text_length * text_aspect : text_width;
      text_new_length = text_use_length ? text_length : text_width / text_aspect;

      difference() {
        // Main box
        color(material_colour)
          cuboid(
            size,
            anchor=BOTTOM + FRONT + LEFT,
            rounding=wall_thickness / 4
          );
        // Inside section (leaving back wall)
        translate(
          [wall_thickness, side_wall_thickness, wall_thickness]
        ) color(material_colour) cuboid(
              [width - wall_thickness - side_wall_thickness, length - side_wall_thickness * 2, height],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness / 4
            );
        // Rounding out the top and out the back.
        translate(
          [wall_thickness, side_wall_thickness, wall_thickness * 3]
        ) color(material_colour) cuboid(
              [width, length - side_wall_thickness * 2, height],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness / 4
            );

        // Edge rounding for the sides.
        translate(
          [wall_thickness * 5, -0.01, wall_thickness * 5]
        ) rotate([90, 0, 0]) color(material_colour) cuboid(
                [width, height, length + 0.02],
                anchor=TOP + FRONT + LEFT,
                rounding=-wall_thickness
              );

        radius = wall_thickness * sqrt(3) / 2;

        // Catch in the front
        translate([-radius * 1 / 2, -0.01, lip_size])
          color(material_colour)
            rotate([0, 45, 0])
              cuboid(
                [wall_thickness, length + 0.02, wall_thickness],
                anchor=FRONT
              );

        // Hole for the text.
        if (metrics.size[0] > 0)
          translate([emboss_text ? 0.3 : 0.5, length / 2, text_length / 2 + text_length_offset])
            color(label_colour)
              rotate([180, 90, 0])
                linear_extrude(0.3 + emboss_text)
                  resize([text_new_length, text_new_width])
                    text(label, font=font, valign="center", halign="center");

        $inner_width = height;
        $inner_length = length;

        // Hole for the children
        if ($children > 0)
          translate([0, length, 0])
            rotate([180, 270, 0])
              children(0);
      }

      $inner_width = height;
      $inner_length = length;

      // Add in the positive children
      if ($children > 0 && add_positive)
        translate([0, length, 0])
          rotate([180, 270, 0])
            children(0);

      // Add in the positive text.
      if (metrics.size[0] > 0 && (add_positive || emboss_text > 0))
        translate([emboss_text ? 0.3 : 0.5, length / 2, text_length / 2 + text_length_offset])
          color(label_colour)
            rotate([180, 90, 0])
              linear_extrude(0.3 + emboss_text)
                resize([text_new_length, text_new_width])
                  text(label, font=font, valign="center", halign="center");
    }
}
