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

// Function: MakeCardSize()
// Description:
//   Creates a card size object.
// Arguments:
//   width = width of the cards
//   length = length of the cards
//   single_card_thickness = thickness of a single card
//.  sleeve_wall_thickness = the thickness of the sleeve (default {{default_wall_thickness}}*0.75)
// Example:
//   MakeCardSize(93, 62, 0.1);
function MakeCardSize(width, length, single_card_thickness, sleeve_wall_thickness = default_wall_thickness * 0.75) = object(length=length, width=width, single_card_thickness=single_card_thickness, sleeve_wall_thickness=sleeve_wall_thickness);

// Function: sumVec()
// Description:
//   Sums all the vectors together to get a final result.
// Arguments:
//   vec = the vector to sum
//   index = the current index (default 0)
//   sum = the current sum (default 0)
// Example:
//   sumVec([1, 2, 3]);
function sumVec(vec, index = 0, sum = 0) =
  index >= len(vec) ?
    sum
  : sumVec(vec, index + 1, sum + vec[index]);

// Function: SleeveSizeWidth()
// Description:
//   Calculates the width of a card sleeve.
// Arguments:
//   num_cards = number of cards in the sleeve
//   card_size = the card size object
//   wall_thickness = thickness of the walls (default ({{default_wall_thickness}})
// Example:
//   SleeveSizeWidth(10);
function SleeveSizeWidth(num_cards, card_size, wall_thickness = default_wall_thickness) = card_size.single_card_thickness * num_cards + card_size.sleeve_wall_thickness * 2;

// Function: SleeveSize()
// Description:
//   Calculates the size of a card sleeve.
// Arguments:
//   num_cards = number of cards in the sleeve
//   card_size = the card size object
//   wall_thickness = thickness of the walls (default ({{default_wall_thickness}})
// Example:
//   SleeveSize(10);
function SleeveSize(num_cards, card_size, wall_thickness = default_wall_thickness) =
  [
    card_size.length + card_size.sleeve_wall_thickness * 2,
    SleeveSizeWidth(num_cards, card_size, wall_thickness),
    card_size.width + wall_thickness,
  ];

// Function: CardLibrarySize()
// Description:
//   Calculates the size of a card library box.
// Arguments:
//   array = array of card arrays
//   card_size = the card size object
//   wall_thickness = thickness of the walls (default ({{default_wall_thickness}})
//   lid_thickness = thickness of the lid (default ({{default_lid_thickness}}))
//   floor_thickness = thickness of the floor (default ({{default_floor_thickness}}))
// Example:
//   CardLibrarySize([["Card 1", 10], ["Card 2", 20]]);
function CardLibrarySize(array, card_size, wall_thickness = default_wall_thickness, lid_thickness = default_lid_thickness, floor_thickness = default_floor_thickness, extra_width = 0.5) =
  [
    card_size.length + wall_thickness * 4,
    sumVec([for (x = array) SleeveSizeWidth(x[1], card_size, wall_thickness)]) + wall_thickness * 2 + extra_width,
    card_size.width + wall_thickness * 2 + lid_thickness + floor_thickness,
  ];

CARD_LIBRARY_LATCH_SLIDING = "sliding";
CARD_LIBRARY_LATCH_CLIP = "clip";
CARD_LIBRARY_LATCH_NONE = "none";

// Module: MakeCardLibraryBox()
// Description:
//   Makes a card library box with the specified latch type.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   floor_thickness = thickness of the floor
//   wall_thickness = thickness of the walls
//   lip_size = size of the lip (default default_floor_thickness * 3)
//   lid_thickness = thickness of the lid
//   material_colour = the colour of the material in the box (default "magenta")
//   latch = latch type to use (default CARD_LIBRARY_LATCH_SLIDING)
//   hinge_hole_diameter = diameter of the hinge hole (default 2.2)
// Example:
//   MakeCardLibraryBox([100, 50, 20]);

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

// Module: SlidingChannel()
// Description:
//   Creates a sliding channel for the card library latch.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   wall_thickness = thickness of the walls

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

// Module: SlidingLatch()
// Description:
//   Creates a sliding latch for the card library box lid.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   print_in_place_offset = offset for print-in-place mechanisms
//   lid_thickness = thickness of the lid
//   wall_thickness = thickness of the walls

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

// Module: CardLibraryBoxLid()
// Description:
//   Creates a basic lid for the card library box.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   wall_thickness = thickness of the walls
//   lid_thickness = thickness of the lid
//   lip_size = size of the lip (default default_lid_thickness * 3)
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   latch = latch type to use (default CARD_LIBRARY_LATCH_SLIDING)
//   material_colour = the colour of the material in the box (default "magenta")
//   hinge_hole_diameter = diameter of the hinge hole (default 2.2)
//   print_in_place_offset = offset for print-in-place mechanisms (default 0.25)
//   size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
// Example:
//   CardLibraryBoxLid([100, 50, 20]);

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

// Module: CardLibraryBoxLidWithCustomShape()
// Description:
//   Creates a lid for the card library box configured for custom shapes.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   wall_thickness = thickness of the walls
//   lid_thickness = thickness of the lid
//   lip_size = size of the lip (default default_lid_thickness * 3)
//   latch = latch type to use (default CARD_LIBRARY_LATCH_SLIDING)
//   material_colour = the colour of the material in the box (default "magenta")
//   hinge_hole_diameter = diameter of the hinge hole (default 2.2)
//   print_in_place_offset = offset for print-in-place mechanisms (default 0.25)
//   size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//   lid_rounding = how much to round the edge of the lid
//   lid_inner_rounding = how much to round the inside of the box
//   lid_pattern_dense = boolean if the pattern is dense
//   lid_dense_shape_edges = number of edges for the dense shape
//   aspect_ratio = aspect ratio of the elements
//   pattern_inner_control = if the shape needs inner control (default false)
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
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
  }
}

// Module: CardLibraryBoxLidWithShape()
// Description:
//   Creates a lid for the card library box using standard shapes.
// Topics: CardLibrary
// Arguments:
//   size = the size of the object [width, length, height]
//   wall_thickness = thickness of the walls
//   lid_thickness = thickness of the lid
//   lip_size = size of the lip (default default_lid_thickness * 3)
//   latch = latch type to use (default CARD_LIBRARY_LATCH_SLIDING)
//   material_colour = the colour of the material in the box (default "magenta")
//   hinge_hole_diameter = diameter of the hinge hole (default 2.2)
//   print_in_place_offset = offset for print-in-place mechanisms (default 0.25)
//   size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//   lid_rounding = how much to round the edge of the lid
//   lid_inner_rounding = how much to round the inside of the box
//   lid_pattern_dense = boolean if the pattern is dense
//   lid_dense_shape_edges = number of edges for the dense shape
//   pattern_inner_control = if the shape needs inner control (default false)
//   shape_options = options object for the shape
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
//   aspect_ratio = aspect ratio of the elements
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
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  pattern_inner_control = false,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = undef,
  shape_options = undef
) {
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject()
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
    aspect_ratio=aspect_ratio,
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

// Module: CardSleeveForLibrary()
// Description:
//   Creates a card sleeve configured for the library.
// Topics: CardLibrary
// Arguments:
//   card_size = the size of the card using the object
//   wall_thickness = thickness of the walls
//   side_wall_thickness = thickness of the side walls
//   lip_size = size of the lip
//   material_colour = the colour of the material in the box (default "magenta")
//   font = the font to use for the label
//   label_colour = the color of the label
//   label = the string to use for the label
//   add_positive = whether to add the positive part
//   emboss_text = amount of text embossing
//   text_length_offset = text offset along the length
// Example:
//   CardSleeveForLibrary([60, 90, 10]);
module CardSleeveForLibrary(
  num_cards,
  card_size,
  wall_thickness = default_wall_thickness,
  lip_size = default_floor_thickness * 3,
  material_colour = "magenta",
  font = default_label_font,
  label_colour = default_label_colour,
  label = "",
  add_positive = false,
  emboss_text = 0.2,
  text_length_offset = default_wall_thickness * 3,
  min_text_height = 3
) {
  assert(num_cards > 0, str("num cards must be > 0", num_cards));
  assert(is_object(card_size), str("card_size must be an object", card_size));

  size = SleeveSize(num_cards, card_size, wall_thickness);
  translate([size[0], size[1], 0])
    rotate([0, 0, 180]) {
      width = size[0];
      length = size[1];
      height = size[2];

      metrics = textmetrics(label, font=font);

      text_length = height - text_length_offset - wall_thickness;
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
          [wall_thickness, card_size.sleeve_wall_thickness, wall_thickness]
        ) color(material_colour) cuboid(
              [width - wall_thickness - card_size.sleeve_wall_thickness, length - card_size.sleeve_wall_thickness * 2, height],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=min(wall_thickness / 4, (length - card_size.sleeve_wall_thickness * 2) / 2, (width - wall_thickness - card_size.sleeve_wall_thickness) / 2)
            );
        // Rounding out the top and out the back.
        translate(
          [wall_thickness, card_size.sleeve_wall_thickness, wall_thickness * 3]
        ) color(material_colour) cuboid(
              [width, length - card_size.sleeve_wall_thickness * 2, height],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=min(wall_thickness / 4, width / 2, (length - card_size.sleeve_wall_thickness * 2) / 2)
            );

        // Edge rounding for the sides.
        translate(
          [wall_thickness * 5, 0.01, wall_thickness * 5]
        ) {
          rounding = -min(wall_thickness, length / 2, width / 2);
          translate([width / 2, length, height / 2])
            rotate([90, 0, 0])
              color(material_colour)
                offset_sweep(
                  round_corners(rect([width, height]), r=wall_thickness * 2), bottom=os_circle(r=rounding), top=os_circle(r=rounding),
                  height=length + 0.02, offset="delta"
                );
        }

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
        if (text_new_width > min_text_height)
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
      if (text_new_width > min_text_height && (add_positive || emboss_text > 0))
        translate([emboss_text ? 0.3 : 0.5, length / 2, text_length / 2 + text_length_offset])
          color(label_colour)
            rotate([180, 90, 0])
              linear_extrude(0.3 + emboss_text)
                resize([text_new_length, text_new_width])
                  text(label, font=font, valign="center", halign="center");
    }
}

// Module: MakeAllSleeves()
// Description:
//   Makes all the sleeves for a card array.
// Arguments:
//   card_array = array of card arrays (format ["card_name", card_count, "svg_filename"])
//   spacing = spacing between sleeves (default 2)
//   card_size = the card size object
// Example:
//   MakeAllSleeves(base_game_cards_v2, spacing = 2, MakeCardSize(63.5, 88, 0.3));
module MakeAllSleeves(
  card_array,
  spacing = 2,
  card_size,
  wall_thickness = default_wall_thickness,
) {
  sleeve_sizes = [for (x = card_array) SleeveSize(x[1], card_size, wall_thickness=wall_thickness)];
  for (i = [0:len(card_array) - 1]) {
    translate([0, sumVec([for (x = [0:i - 1]) sleeve_sizes[x][1] + spacing]), 0])
      CardSleeveForLibrary(
        num_cards=card_array[i][1], card_size=card_size, label=card_array[i][0], add_positive=true,
        text_length_offset=18, emboss_text=0.3
      ) if ($children > 0) {
        $inner_2d =
          (len(card_array[i]) > 2 && card_array[i][2] != "") ?
            card_array[i][2]
          : undef;
        children(0);
      }
  }
}
