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

include <BOSL2/hinges.scad>

// LibFile: hinge_box.scad
//    This file has all the modules needed to generate a hinge box.

// FileSummary: Hinge box pieces for the hinge boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Hinges
// Description:
//    Types of hinges to make.

// Module: HingeCone()
// Description:
//   Makes the hinge cone for use in hinges, this makes a 45 degree cone with an inner/outer that
//   can be joined with other pieces to make a hinge.
// Topics: Hinges
// Usage: HingeCone(6, 0.5)
// Arguments:
//   r = radius of the cone
//   offset = how far inside the cone to leave space
// Example:
//   HingeCone(6, 0.5);
module HingeCone(r, offset) {
  difference() {
    cylinder(h=r, r1=r, r2=0, $fn=32);
    translate([0, 0, -0.01]) cylinder(h=r - offset, r1=r - offset, r2=0, $fn=32);
  }
}

// Module: HingeLine()
// Description:
//    Makes a hinge setup in a straight line, has pieces that stick out each side wide enough to hook onto
//    edges within 0.5 of the side.
// Topics: Hinges
// Arguments:
//    length = length of the line to hinge
//    diameter = diameter of the hinge itself
//    offset = how much of a space to leave on the conical holes for the hinge
//    spin = how much to rotate one of the legs (default 0)
// Example:
//    HingeLine(length = 60, diameter = 6, offset = 0.5);
module HingeLine(length, diameter, offset, spin = 90) {
  num = length / diameter;
  spacing = length / num;

  HingeLineWithSpacingAndNum(diameter=diameter, offset=offset, spin=spin, num=num, spacing=spacing);
}

// Module: HingeLineWithSpacingAndNum()
// Description:
//    Makes a hinge setup in a straight line, has pieces that stick out each side wide enough to hook onto
//    edges within 0.5 of the side.
// Topics: Hinges
// Arguments:
//    num = number of hinge locations
//    spacing = spacing between hinge spots
//    diameter = diameter of the hinge itself
//    offset = how much of a space to leave on the conical holes for the hinge
//    spin = how much to rotate one of the legs (default 0)
// Example:
//    HingeLineWithSpacingAndNum(num = 10, spacing = 6, diameter = 6, offset = 0.5);
module HingeLineWithSpacingAndNum(diameter, num, spacing, offset, spin = 90) {
  length = num * diameter;
  rotate([0, 270, 0]) translate([0, 0, -length / 2]) {

      difference() {
        cylinder(r=diameter / 2, h=length, $fn=32);
        for (i = [1:1:num]) {
          translate([0, 0, spacing * i]) mirror([0, 0, i % 2])
              HingeCone(diameter / 2 - 0.01, offset, $fn=32);
          if (i % 2 == 1) {
            difference() {
              translate([0, 0, spacing * i + diameter - diameter - 0.02])
                cylinder(r=diameter, h=diameter + 0.04, $fn=32);
              translate([0, 0, spacing * i + diameter - diameter - 0.03])
                cylinder(r=diameter / 2 - offset, h=diameter + 0.06, $fn=32);
            }
          }
        }
      }
      for (i = [0:1:num - 1]) {
        if (i % 2 == 1) {
          rotate([0, 0, spin]) union() {
              translate([0, 0, spacing * i + offset / 2])
                cylinder(r=diameter / 2, h=diameter - offset, $fn=32);
              translate([0, 0, spacing * i + diameter - diameter / 2]) union() {

                  rotate([0, 90, 0])
                    prismoid(
                      size1=[diameter - offset, diameter], size2=[diameter - offset, diameter],
                      h=diameter / 2 + offset * 2 + 0.01
                    );
                  translate([diameter / 2 + offset, 0, 0])
                    cuboid(
                      [offset * 2, diameter, diameter + offset * 3], chamfer=offset * 2,
                      edges=[TOP + LEFT, BOTTOM + LEFT]
                    );
                }
            }
        } else {
          union() {
            translate([-diameter / 2 - offset * 3 / 2, 0, spacing * i + diameter / 2])
              cuboid(
                [1, diameter, diameter + offset * 3], chamfer=offset * 2,
                edges=[TOP + RIGHT, BOTTOM + RIGHT]
              );
            difference() {
              translate([-diameter / 2 - offset, -diameter / 2, spacing * i])
                cube([diameter / 2 + offset, diameter, diameter]);
              translate([0, 0, spacing * i + (i % 2) * (diameter / 2) - offset * 2])
                cylinder(d=diameter - 0.02, h=diameter * 4, $fn=32);
            }
          }
        }
      }
    }
}

// Module: InsetHinge()
// Description:
//   Create a hinge that works and moves in the middle.  Centers the pices back on the line with the
//   middle being the length/2, width2/2 and the diameter/2, the legs stick down a little to make it
//   easier to join onto other parts of the system.
// Topics: Hinges
// Arguments:
//   length = length of the hinge (outside)
//   width = width of the middle pice (outside)
//   diameter = diameter of the round piece in the middle.
//   offset = how much to offset the middle sections, 0.5 is usually good for this
// Usage: InsetHinge(100, 20, 6, 0.5);
// Example:
//   InsetHinge(length = 100, width = 20, diameter = 6, offset = 0.5);
module InsetHinge(length, width, diameter, offset) {
  num = length / diameter;
  spacing = length / num;

  translate([0, -width / 2, 0]) difference() {
      union() {
        translate([0, width / 2, 0]) cuboid([length, width - diameter * 2 - offset / 2, diameter]);
        translate([0, diameter / 2, 0]) HingeLineWithSpacingAndNum(
            diameter=diameter, offset=offset,
            spin=90, num=num, spacing=spacing
          );
        translate([0, width - diameter / 2, 0]) mirror([0, 1, 0]) HingeLineWithSpacingAndNum(
              diameter=diameter, offset=offset, spin=90, num=num, spacing=spacing
            );
      }
      // Make sure the middle bits are supported by cutting out a 45 degree slice in them.
      /*
      for (i = [0:1:num - 1]) {
        rotate([0, 270, 0]) translate([-diameter, width / 2, -length / 2]) {
            rotate([0, 0, 90]) union() {
                translate([0, 0, spacing * i + offset / 2 + spacing / 2]) {
                  cuboid(
                    [
                      diameter * 2,
                      diameter * 2,
                      width - diameter * 2 - 0.05,
                    ], spin=45, orient=LEFT
                  );
                }
                if (i == 0) {
                  translate([0, -diameter, spacing * i + offset / 2 - spacing / 2]) cuboid(
                      [
                        width - diameter * 2 - 0.05,
                        diameter * 2,
                        diameter * 2,
                      ]
                    );
                }
                if (i == num - 1 && num % 2 == 1) {
                  translate([0, -diameter, spacing * i + offset / 2 + spacing * 3 / 2]) cuboid(
                      [
                        width - diameter * 2 - 0.05,
                        diameter * 2,
                        diameter * 2,
                      ]
                    );
                }
              }
          }
      }*/
    }
}

// Module: HingeBoxLidLabel()
// Description:
//    Makes a lid for one side of a hinge box with a label and pattern.  This uses the
//    $inner_width and $inner_length from the main hinge box creation.
// Arguments:
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default 1.0)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    lid_rounding = how much rounding on the edge of the lid (default undef)
//    lid_inner_rounding = how much rounding on the inside (default undef)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    size_spacing = extra spacing to apply between pieces (default {{default_slicing_layer_height}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
//    cap_height = height of the cap on the box
// Usage: HingeBoxLidLabel(size=[100, 50], text_str="Cards");
// Example:
//   $inner_width = 100;
//   $inner_length = 50;
//   HingeBoxLidLabel(text_str="Cards");
module HingeBoxLidLabel(
  text_str,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  cap_height = undef,
  layout_width = undef,
  aspect_ratio = 1.0,
  lid_thickness = default_lid_thickness,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  material_colour = default_material_colour,
  size_spacing = default_slicing_layer_height,
  label_options = undef,
  shape_options = undef
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
      full_height=true
    )
  );
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );

  internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
    difference() {
      // Top piece
      color(material_colour) cuboid(
          [$inner_width, $inner_length, lid_thickness], anchor=BOTTOM + FRONT + LEFT,
          edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
        );
    }
    LidMeshBasic(
      size=[$inner_width, $inner_length],
      lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio,
      dense=IsDenseShapeType(calc_shape_options.shape_type),
      dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
      material_colour=material_colour,
      inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type)
    ) {
      color(material_colour)
        ShapeByType(
          options=calc_shape_options,
        );
    }
    rotate([0, 180, 0])
      translate([-$inner_width, 0, -lid_thickness])
        MakeLidLabel(
          size=[$inner_width, $inner_length],
          lid_thickness=lid_thickness,
          text_str=text_str,
          options=object(calc_label_options, full_height=true),
        );
  }
}

// Module: MakeBoxWithInsetHinge()
// Description:
//   Makes a box with an inset hinge on the side, this is a print in place box with a hinge that will
//   make lid hinge onto the top, it is the same height on both sides, child 1 is in the base, child 2
//   is in the lid and child 3+ are lid pieces.  Inside the children of the box you can use the
//    $inner_height , $inner_width, $inner_length = length variables to
//    deal with the box sizes.
// Usage: MakeBoxAndLidWithInsetHinge(size=[100, 50, 20]);
// Topics: Hinges, HingeBox
// Arguments:
//   size = outside size of the box [width, length, height]
//   hinge_diameter = diameter of the hinge (default 6)
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   hinge_offset = offset for the hinge mechanism (default 0.5)
//   gap = gap between the two box halves (default 1)
//   side_gap = gap on the sides of the hinge (default 3)
//   print_layer_height = height of the print layers (default 0.2)
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   prism_width = width of the prism for the tab (default 0.75)
//   tab_offset = offset for the tab (default 0.2)
//   tab_length = length of the tab (default 10)
//   tab_height = height of the tab (default 6)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   print_in_place_offset = wiggle room between moving parts (default 0.2)
// Examples:
//   MakeBoxAndLidWithInsetHinge(size=[100, 50, 20]);
module MakeBoxAndLidWithInsetHinge(
  size,
  hinge_diameter = 6,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  hinge_offset = 0.5,
  gap = 1,
  side_gap = 3,
  print_layer_height = 0.2,
  lid_thickness = default_lid_thickness,
  prism_width = 0.75,
  tab_offset = 0.2,
  tab_length = 10,
  tab_height = 6,
  material_colour = default_material_colour,
  print_in_place_offset = default_print_in_place_offset
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];

  hinge_width = hinge_diameter * 2 + gap;
  hinge_length = length - side_gap * 2;
  difference() {
    union() {
      difference() {
        union() {
          color(material_colour)
            cuboid(
              [width, length, height / 2], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
            );
          // Add a latch.
          color(material_colour) translate([0, length / 2 + tab_length / 2, height / 2 - lid_thickness])
              rotate([0, 0, 270]) mirror([0, 0, 1])
                  MakeLidTab(
                    length=tab_length, height=tab_height, lid_thickness=lid_thickness,
                    prism_width=prism_width, wall_thickness=wall_thickness
                  );
        }
        // Add a rim to align
        difference() {
          translate([wall_thickness / 2, wall_thickness / 2, height / 2 - wall_thickness / 2])
            cuboid(
              [width - wall_thickness, length - wall_thickness, wall_thickness],
              anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness / 2,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            );
          translate([wall_thickness + print_in_place_offset, wall_thickness + print_in_place_offset, height / 2 - wall_thickness / 2])
            cuboid(
              [width - wall_thickness * 2 - print_in_place_offset * 2, length - wall_thickness * 2 - print_in_place_offset * 2, wall_thickness],
              anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness / 2,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            );
        }
        if ($children > 0) {
          $inner_width = width - wall_thickness - hinge_width;
          $inner_height = height / 2 - floor_thickness;
          $inner_length = length - wall_thickness * 2;
          $material_colour = material_colour;
          translate([wall_thickness, wall_thickness, floor_thickness]) children(0);
        }
      }
      if ($children > 2) {
        $inner_width = width - wall_thickness * 2;
        $inner_length = length - wall_thickness * 2;
        $material_colour = material_colour;
        translate([wall_thickness, wall_thickness, -0.01]) children(2);
      }

      translate([width + gap, 0, 0]) {
        difference() {
          difference() {
            union() {
              color(material_colour)
                cuboid(
                  [width, length, height / 2], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
                  edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
                );
              // Add a rim to align
              color(material_colour)
                difference() {
                  translate([wall_thickness / 2, wall_thickness / 2, height / 2])
                    cuboid(
                      [width - wall_thickness, length - wall_thickness, wall_thickness],
                      anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness / 2,
                      edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP + BACK, TOP + FRONT, TOP + LEFT, TOP + RIGHT]
                    );
                  translate([wall_thickness + print_in_place_offset, wall_thickness + print_in_place_offset, height / 2 - wall_thickness])
                    cuboid(
                      [width - wall_thickness * 2 - print_in_place_offset * 2, length - wall_thickness * 2 - print_in_place_offset * 2, wall_thickness * 4],
                      anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness / 2,
                      edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
                    );
                }
            }
            // Add a catch.
            color(material_colour) translate(
                [width + gap - wall_thickness / 2, length / 2 + tab_length / 2, height / 2 + lid_thickness]
              )
                rotate([0, 0, 270]) mirror([0, 1, 0]) minkowski() {
                      translate([-tab_offset, -tab_offset, -tab_offset]) color(material_colour)
                          cube(tab_offset * 2);

                      MakeLidTab(
                        length=tab_length, height=tab_height, lid_thickness=lid_thickness,
                        prism_width=prism_width, wall_thickness=wall_thickness
                      );
                    }
          }

          if ($children > 1) {
            $inner_width = width - wall_thickness - hinge_width;
            $inner_height = height / 2 - lid_thickness;
            $inner_length = length - wall_thickness * 2;
            $material_colour = material_colour;
            translate([hinge_width, wall_thickness, lid_thickness]) children(1);
          }
          if ($children > 3) {
            // Carve out the lid hole.
            translate([wall_thickness, wall_thickness, -1])
              cuboid([width - wall_thickness * 2, length - wall_thickness * 2, lid_thickness + 1], anchor=BOTTOM + FRONT + LEFT);
          }
        }
        if ($children > 3) {
          $inner_width = width - wall_thickness * 2;
          $inner_length = length - wall_thickness * 2;
          $material_colour = material_colour;
          translate([wall_thickness, wall_thickness, -0.01]) children(3);
        }
      }
    }
    translate([width - hinge_diameter - 0.01 - print_in_place_offset, side_gap + print_in_place_offset, height / 2 - hinge_diameter - print_layer_height - hinge_offset])
      color(material_colour) {
        cube([hinge_width + print_in_place_offset * 2 + 0.02, hinge_length + print_in_place_offset * 2, hinge_diameter + 5 + hinge_offset + 1]);
      }
  }
  translate([width + gap / 2, hinge_length / 2 + side_gap, height / 2 - hinge_diameter / 2 - hinge_offset]) rotate([0, 0, 90]) {
      color(material_colour) InsetHinge(
          length=hinge_length, width=hinge_width, offset=hinge_offset,
          diameter=hinge_diameter
        );
    }
}

// Module: MakeBoxWithFilamentHinge()
// Description:
//   Makes a box with a filament hinge on the top.  The hole for the filement is
//   specified as a an argument to the system.
// Usage: MakeBoxWithFilamentHinge(size=[100, 50, 20]);
// Topics: Hinges, HingeBox
// Arguments:
//   size = outside size of the box [width, length, height]
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   filament_thickness = the thickness of the filement in hinger (default 2.2)
// Examples:
//   MakeBoxWithFilamentHinge(size=[100, 50, 20]);
module MakeBoxWithFilamentHinge(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];

  edge_length = length * 1 / 6;
  catch_length = min(wall_thickness * 6, length / 6);
  catch_height = min(wall_thickness * 4, height / 6);

  hinge_seg = max(floor(length / 20), 5);
  lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness);
  lip_length = max(length / 4, 15);

  difference() {
    union() {
      difference() {
        union() {
          diff() color(material_colour)
              cuboid(
                [width, length, height - lid_thickness - print_in_place_offset],
                rounding=wall_thickness / 2,
                anchor=BOTTOM + FRONT + LEFT,
                edges=[BOTTOM, FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]
              ) {
                edge_mask(TOP + FRONT) rounding_edge_mask(l=width, r=wall_thickness / 4);
                edge_mask(TOP + BACK) rounding_edge_mask(l=width, r=wall_thickness / 4);
                edge_mask(TOP + RIGHT) rounding_edge_mask(l=length, r=wall_thickness / 4);
              }
        }

        up(height - lid_thickness - wall_thickness - print_in_place_offset * 2)
          color(material_colour)
            cuboid(
              [wall_thickness * 2, length, wall_thickness + print_in_place_offset],
              anchor=BOTTOM + LEFT + FRONT,
              rounding=-wall_thickness,
              edges=TOP + RIGHT
            );

        up(height - lid_thickness - lip_height - print_in_place_offset)
          back(length / 2)
            right(width) {
              color(material_colour)
                cuboid(
                  [wall_thickness / 2, lip_length + print_in_place_offset * 2, lip_height],
                  anchor=BOTTOM + RIGHT,
                  rounding=wall_thickness / 4,
                  edges=[BOTTOM + LEFT]
                );
              up(lip_height / 2)
                back(lip_length / 4)
                  color(material_colour)
                    sphere(d=wall_thickness, anchor=RIGHT);
              up(lip_height / 2)
                fwd(lip_length / 4)
                  color(material_colour)
                    sphere(d=wall_thickness, anchor=RIGHT);
            }
      }
      up(height)
        color(material_colour)
          knuckle_hinge(
            length=length,
            segs=hinge_seg,
            offset=wall_thickness + lid_thickness,
            knuckle_diam=wall_thickness + lid_thickness,
            arm_height=0,
            arm_angle=90,
            clear_top=false,
            inner=true,
            spin=90,
            pin_diam=hinge_hole_diameter,
            orient=UP,
            anchor=TOP + BACK + LEFT
          );
    }

    $inner_width = width - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    $inner_length = length - wall_thickness * 2;
    $material_colour = material_colour;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

// Module: FilamentBoxInsideMask()
// Description:
//   The inside mask to use as an intersection to make sure any inside cuts don't
//   mess with the hinges.
// Topics: Boxes, Hinges
// Arguments:
//   size = [width, length, height] of the box
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
// Example:
//   FilamentBoxInsideMask([100, 20, 10]);
module FilamentBoxInsideMask(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  print_in_place_offset = default_print_in_place_offset,
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  support_height = min(height / 6, wall_thickness * 4);

  difference() {
    color(material_colour)
      cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - floor_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=rounding,
        edges=[BOTTOM, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );

    translate([-0.5, -0.5, height - support_height - floor_thickness])
      color(material_colour) cuboid(
          [wall_thickness + 0.5, length + 1, support_height + 1],
          anchor=BOTTOM + FRONT + LEFT,
          chamfer=min(wall_thickness, support_height),
          edges=[BOTTOM + RIGHT],
        );
    fwd(0.5)
      up(height)
        color(material_colour)

          ycyl(d=wall_thickness * 2 + print_in_place_offset, length=length + 1, anchor=FRONT + LEFT + TOP);
  }
}

// Module: MakeLidForFilamentBox()
// Description:
//   Makes a lid for a box with a filament based hinge.
// Topics: Boxes, Hinges
// Arguments:
//   size = [width, length, height] of the box
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
// Example:
//   MakeLidForFilamentBox([100, 20, 6, 0.5]);
module MakeLidForFilamentBox(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
) {
  edge_length = size[1] * 1 / 6;
  catch_length = min(wall_thickness * 6, size[1] / 6);
  catch_height = min(wall_thickness * 4, size[0] / 6);
  width = size[0];
  length = size[1];
  height = size[2];

  hinge_seg = max(floor(length / 20), 5);
  lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness);
  lip_length = max(length / 4, 15);

  difference() {
    union() {
      internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
        // Top piece
        right(wall_thickness)
          color(material_colour)
            cuboid(
              [size[0] - wall_thickness, size[1], lid_thickness],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=lid_thickness / 2,
              edges=BOTTOM
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
      }

      up(0)
        diff() color(material_colour)
            knuckle_hinge(
              length=length,
              segs=hinge_seg,
              offset=wall_thickness + lid_thickness,
              knuckle_diam=wall_thickness + lid_thickness,
              pin_diam=hinge_hole_diameter,
              arm_height=0,
              arm_angle=90,
              clear_top=true,
              spin=270,
              orient=LEFT,
              anchor=TOP + FRONT + RIGHT
            ) {
              edge_mask(LEFT + FRONT) rounding_edge_mask(l=width, r=wall_thickness / 2);
              edge_mask(RIGHT + FRONT) rounding_edge_mask(l=width, r=wall_thickness / 2);
            }
      up(lid_thickness - print_in_place_offset)
        back(length / 2)
          right(width) color(material_colour) {
              cuboid(
                [wall_thickness / 2, lip_length, lip_height + print_in_place_offset],
                anchor=BOTTOM + RIGHT,
                rounding=wall_thickness / 4,
                edges=[TOP + LEFT]
              );
              up(lip_height / 2)
                back(lip_length / 4)
                  sphere(d=wall_thickness * 5 / 6, anchor=RIGHT);
              up(lip_height / 2)
                fwd(lip_length / 4)
                  sphere(d=wall_thickness * 5 / 6, anchor=RIGHT);
            }
    }
    fwd(0.5)
      right(wall_thickness)
        up(wall_thickness) color(material_colour)
            ycyl(h=length + 1, d=hinge_hole_diameter + print_in_place_offset, anchor=FRONT);
  }
}

// Module: FilamentHingeBoxLidWithCustomShape()
// Topics: Boxes, Hinges
// Description:
//   Makes a lid for a box with a filament based hinge and a custom shape.
// Arguments:
//   size = [width, length, height] of the box
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
//   hinge_hole_diameter = diameter of the hinge hole
//   print_in_place_offset = offset for print in place mechanisms
//   size_spacing = wiggle room for size
//   lid_pattern_dense = boolean if the pattern is dense
//   lid_dense_shape_edges = number of edges for the dense shape
//   aspect_ratio = aspect ratio of the elements
//   pattern_inner_control = if the shape needs inner control (default false)
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
// Example:
//   FilamentHingeBoxLidWithCustomShape([100, 20, 6]) circle(r=5);
module FilamentHingeBoxLidWithCustomShape(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  aspect_ratio = 1.0,
  pattern_inner_control = false,
  lid_boundary = 10,
  layout_width = undef,
) {
  MakeLidForFilamentBox(
    size=size,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    material_colour=material_colour,
    filament_thickness=filament_thickness,
    rounding=rounding,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing
  ) {
    LidMeshBasic(
      size=[
        size[0],
        size[1],
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

// Module: FilamentHingeBoxLidWithLabelAndCustomShape()
// Topics: Boxes, Hinges
// Description:
//   Makes a lid for a box with a filament based hinge, a text label, and a custom shape.
// Arguments:
//   size = [width, length, height] of the box
//   text_str = the string to use for the label
//   label_options = options for the label
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
//   hinge_hole_diameter = diameter of the hinge hole
//   print_in_place_offset = offset for print in place mechanisms
//   size_spacing = wiggle room for size
//   lid_pattern_dense = boolean if the pattern is dense
//   lid_dense_shape_edges = number of edges for the dense shape
//   aspect_ratio = aspect ratio of the elements
//   pattern_inner_control = if the shape needs inner control (default false)
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
// Example:
//   FilamentHingeBoxLidWithLabelAndCustomShape([100, 20, 6], "Label") circle(r=5);
module FilamentHingeBoxLidWithLabelAndCustomShape(
  size,
  text_str,
  label_options = undef,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  aspect_ratio = 1.0,
  pattern_inner_control = false,
  lid_boundary = 10,
  layout_width = undef,
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );

  FilamentHingeBoxLidWithShape(
    size=size,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    material_colour=material_colour,
    filament_thickness=filament_thickness,
    rounding=rounding,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_pattern_dense=lid_pattern_dense,
    lid_dense_shape_edges=lid_dense_shape_edges,
    aspect_ratio=aspect_ratio,
    pattern_inner_control=pattern_inner_control,
    lid_boundary=lid_boundary,
    layout_width=layout_width
  ) {
    if ($children > 0) {
      children(0);
    } else {
      color(material_colour) square([10, 10]);
    }
    translate([lid_boundary, lid_boundary, lid_thickness])
      //  translate([(size[0] - wall_thickness - lid_boundary * 2) / 2, (size[1] - lid_boundary * 2) / 2, lid_thickness])
      //    translate([-(size[0] - wall_thickness - lid_boundary * 2) / 2, -(size[1] - lid_boundary * 2) / 2, 0])
      zflip()
        MakeLidLabel(
          size=[
            size[0] - wall_thickness - lid_boundary * 2,
            size[1] - lid_boundary * 2,
          ],
          options=object(calc_label_options, full_height=true), lid_thickness=lid_thickness,
          text_str=text_str,
        );
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

// Module: FilamentHingeBoxLidWithShape()
// Topics: Boxes, Hinges
// Description:
//   Makes a lid for a box with a filament based hinge and a pre-defined shape.
// Arguments:
//   size = [width, length, height] of the box
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
//   hinge_hole_diameter = diameter of the hinge hole
//   print_in_place_offset = offset for print in place mechanisms
//   size_spacing = wiggle room for size
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
//   aspect_ratio = aspect ratio of the elements
//   shape_options = options for the shape
// Example:
//   FilamentHingeBoxLidWithShape([100, 20, 6], shape_options=MakeShapeObject());
module FilamentHingeBoxLidWithShape(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = 1.0,
  shape_options = undef
) {
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject()
  );

  FilamentHingeBoxLidWithCustomShape(
    size=size,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    material_colour=material_colour,
    filament_thickness=filament_thickness,
    rounding=rounding,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    aspect_ratio=aspect_ratio,
    layout_width=layout_width,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type)
  ) {
    if ($children > 0) {
      children(0);
    } else {
      color(material_colour)
        ShapeByType(options=calc_shape_options);
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
  }
}

// Module: FilamentHingeBoxLidWithLabel()
// Topics: Boxes, Hinges
// Description:
//   Makes a lid for a box with a filament based hinge, a text label, and a pre-defined shape.
// Arguments:
//   size = [width, length, height] of the box
//   text_str = the string to use for the label
//   label_options = options for the label
//   wall_thickness = wall thickness of the box
//   floor_thickness = floor thickness of the box
//   lid_thickness = lid thickness of the box
//   material_colour = material colour of the box
//   filament_thickness = filament thickness of the box
//   rounding = rounding of the box
//   hinge_hole_diameter = diameter of the hinge hole
//   print_in_place_offset = offset for print in place mechanisms
//   size_spacing = wiggle room for size
//   lid_boundary = bounding edge for shape generation on the lid (default 10)
//   layout_width = width of the layout
//   aspect_ratio = aspect ratio of the elements
//   shape_options = options for the shape
// Example:
//   FilamentHingeBoxLidWithLabel([100, 20, 6], "Label");
module FilamentHingeBoxLidWithLabel(
  size,
  text_str,
  label_options = undef,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  rounding = 0,
  hinge_hole_diameter = default_hinge_hole_diameter,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = 1.0,
  shape_options = undef
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject()
  );

  FilamentHingeBoxLidWithLabelAndCustomShape(
    size=size,
    text_str=text_str,
    label_options=calc_label_options,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    material_colour=material_colour,
    filament_thickness=filament_thickness,
    rounding=rounding,
    hinge_hole_diameter=hinge_hole_diameter,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    aspect_ratio=aspect_ratio,
    layout_width=layout_width,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type)
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
  }
}
