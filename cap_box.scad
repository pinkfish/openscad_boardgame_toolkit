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

// LibFile: cap_box.scad
//    This file has all the modules needed to generate a cap box.

// FileSummary: Cap box pieces for the cap boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: CapLid
// Description:
//    Cap lid to go on insets, this is a smaller lid that fits onto the top of the box. It only covers
//    the top few mms and has some cut outs on the side to make removal easier.

// Function: CapBoxDefaultCapHeight()
// Description:
//   Works out the default value for the cap box height.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultCapHeight(height) = min(10, height / 2);

// Function: CapBoxDefaultFingerHoldHeight()
// Description:
//   Works out the default value for the cap box finger hold height.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultFingerHoldHeight(height) = min(5, height / 4);

// Function: CapBoxDefaultFingerHoldLen()
// Description:
//   Works out the default value for the cap box finger hold length.
// Arguments:
//   height = the height of the box.
function CapBoxDefaultFingerHoldLen(width, length) = min(width, length) / 5;

// Function: CapBoxDefaultLidWallThickness()
// Description:
//   Works out the default value for the cap box wall thickness.
// Arguments:
//   wall_thickness = the wall thickness of the box.
function CapBoxDefaultLidWallThickness(wall_thickness) = wall_thickness / 2;

// Function:CapBoxDefaultLidFingerHoldRounding()
// Description:
//   Works out the default value for the cap box rounding piece on the edge.
// Arguments:
//   cap_height = the current cap height
function CapBoxDefaultLidFingerHoldRounding(cap_height) = min(3, cap_height / 2);

// Module: MakeBoxWithCapLid()
// Topics: CapLid
// Description:
//    Makes a box with a cap lid.  Inside the children of the box you can use the
//    $inner_height , $inner_width, $inner_length = length variables to
//    deal with the box sizes.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    lid_finger_hold_len = length of the finger hold sections to cut out (default min(width,lenght)/5)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    last_child_positive = if the last child in the list is a positive add to the box, not negative (default false)
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LENGTH}} - length catch, {{CATCH_WIDTH}} - width catch (default
//       {{CATCH_LENGTH}})
// Usage: MakeBoxWithCapLid(100, 50, 20);
// Example:
//    MakeBoxWithCapLid(100, 50, 20);
// Example:
//    MakeBoxWithCapLid(100, 50, 10, lid_finger_hold_len = 4);
// Example:
//    MakeBoxWithCapLid(100, 50, 5, cap_height = 2, finger_hold_height = 1);
module MakeBoxWithCapLid(
  width,
  length,
  height,
  cap_height = undef,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_wall_thickness = undef,
  lid_finger_hold_len = undef,
  finger_hold_height = 5,
  floor_thickness = default_floor_thickness,
  material_colour = default_material_colour,
  last_child_positive = false,
  lid_catch = CATCH_LENGTH
) {
  calc_lid_wall_thickness =
    lid_wall_thickness == undef ? CapBoxDefaultLidWallThickness(wall_thickness) : lid_wall_thickness;
  calc_lid_finger_hold_len =
    lid_finger_hold_len == undef ? CapBoxDefaultFingerHoldLen(width, length) : lid_finger_hold_len;
  calc_floor_thickness = floor_thickness == undef ? wall_thickness : floor_thickness;
  calc_cap_height = cap_height == undef ? CapBoxDefaultCapHeight(height) : cap_height;
  calc_finger_hold_height = finger_hold_height == undef ? CapBoxDefaultFingerHoldHeight(height) : finger_hold_height;
  calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height);
  difference() {
    color(material_colour)
      cuboid(
        [width, length, height - lid_thickness - size_spacing], anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );
    // lid diff.
    translate([0, 0, height - calc_cap_height]) difference() {
        translate([-size_spacing, -size_spacing, 0]) color(material_colour)
            cuboid(
              [width + size_spacing * 2, length + size_spacing * 2, calc_cap_height],
              anchor=BOTTOM + FRONT + LEFT
            );
        translate([calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0])
          color(material_colour) cuboid(
              [
                width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                length - calc_lid_wall_thickness * 2 - size_spacing * 2,
                calc_cap_height,
              ],
              anchor=BOTTOM + FRONT + LEFT, rounding=calc_lid_wall_thickness,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            );
      }

    // lid catches
    translate([0, 0, height - calc_cap_height]) {
      if (lid_catch == CATCH_LENGTH) {
        catch_width = width - wall_thickness * 2;
        translate([(catch_width * 2 / 8) + wall_thickness, 0, 0]) color(material_colour)
            wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]);
        translate([(catch_width * 6 / 8) + wall_thickness, length, 0]) rotate(180) color(material_colour)
              wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]);
      } else if (lid_catch == CATCH_WIDTH) {
        catch_length = length - wall_thickness * 2;
        translate([width, catch_length * 2 / 8 + wall_thickness, 0]) rotate(90) color(material_colour)
              wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]);
        translate([0, catch_length * 6 / 8 + wall_thickness, 0]) rotate(270) color(material_colour)
              wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]);
      }
    }

    // finger cutouts.
    translate([0, 0, height - calc_cap_height - calc_finger_hold_height]) difference() {
        // Remove the edge around the outside where the finger bits go.
        difference() {
          translate([-size_spacing, -size_spacing, 0]) color(material_colour)
              cuboid(
                [width + size_spacing * 2, length + size_spacing * 2, calc_finger_hold_height + 1],
                anchor=BOTTOM + FRONT + LEFT
              );

          translate([calc_lid_wall_thickness + size_spacing, calc_lid_wall_thickness + size_spacing, 0])
            color(material_colour) cuboid(
                [
                  width - calc_lid_wall_thickness * 2 - size_spacing * 2,
                  length - calc_lid_wall_thickness * 2 - size_spacing * 2,
                  calc_finger_hold_height + 2,
                ],
                anchor=BOTTOM + FRONT + LEFT, rounding=calc_lid_wall_thickness,
                edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
              );
        }
        // Finger hole bits.
        translate([calc_lid_finger_hold_len, 0, -0.1]) color(material_colour)
            cuboid(
              [width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness, calc_finger_hold_height + 0.2],
              rounding=calc_finger_hole_rounding, edges=[TOP + LEFT, TOP + RIGHT],
              anchor=BOTTOM + LEFT + FRONT, $fn=32
            );
        translate([calc_lid_finger_hold_len, length - calc_lid_wall_thickness, -0.1]) color(material_colour)
            cuboid(
              [width - calc_lid_finger_hold_len * 2 + 0.1, wall_thickness, calc_finger_hold_height + 0.2],
              rounding=calc_finger_hole_rounding, edges=[TOP + LEFT, TOP + RIGHT],
              anchor=BOTTOM + LEFT + FRONT, $fn=32
            );
        translate([0, calc_lid_finger_hold_len, -0.1]) color(material_colour)
            cuboid(
              [wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1, calc_finger_hold_height + 0.2],
              rounding=calc_finger_hole_rounding, edges=[TOP + FRONT, TOP + BACK],
              anchor=BOTTOM + LEFT + FRONT, $fn=32
            );
        translate([width - calc_lid_wall_thickness, calc_lid_finger_hold_len, -0.1]) color(material_colour)
            cuboid(
              [wall_thickness, length - calc_lid_finger_hold_len * 2 + 0.1, calc_finger_hold_height + 0.2],
              rounding=calc_finger_hole_rounding, edges=[TOP + FRONT, TOP + BACK],
              anchor=BOTTOM + LEFT + FRONT, $fn=32
            );
      }
    // Put the children in the box.
    $inner_height = height - lid_thickness - floor_thickness;
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    if (last_child_positive) {
      translate([wall_thickness, wall_thickness, calc_floor_thickness]) children([0:$children - 2]);
    } else {
      translate([wall_thickness, wall_thickness, calc_floor_thickness]) children();
    }
  }
  if (last_child_positive) {
    $inner_height = height - lid_thickness - floor_thickness;
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    translate([wall_thickness, wall_thickness, calc_floor_thickness]) children($children - 1);
  }
}

// Module: CapBoxLid()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    lid_roudning = how much to round the edge of the lid (default wall_thickness / 2)
//    lid_inner_rounding = how much to round the inside of the box (default calc_lid_wall_thickness/2)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: CapBoxLid(100, 50, 20);
// Example:
//    CapBoxLid(100, 50, 30);
// Example:
//    CapBoxLid(100, 50, 10);
// Example:
//    CapBoxLid(100, 50, 10, cap_height = 3);
module CapBoxLid(
  width,
  length,
  height,
  cap_height = undef,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_wall_thickness = undef,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  material_colour = default_material_colour,
  lid_catch = CATCH_LENGTH
) {
  calc_lid_wall_thickness = lid_wall_thickness == undef ? wall_thickness / 2 : lid_wall_thickness;
  calc_cap_height = cap_height == undef ? CapBoxDefaultCapHeight(height) : cap_height;
  calc_lid_rounding = DefaultValue(lid_rounding, wall_thickness / 2);
  calc_lid_inner_rounding = DefaultValue(lid_rounding, calc_lid_wall_thickness / 2);
  translate([0, length, calc_cap_height]) rotate([180, 0, 0]) {
      union() {
        translate([0, 0, calc_cap_height - lid_thickness])
          internal_build_lid(width, length, lid_thickness, wall_thickness, size_spacing=size_spacing) {
            difference() {
              // Top piece
              color(material_colour) cuboid(
                  [width, length, lid_thickness], anchor=BOTTOM + FRONT + LEFT,
                  rounding=calc_lid_rounding,
                  edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
                );
            }
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
        difference() {
          color(material_colour) cuboid(
              [width, length, calc_cap_height], anchor=BOTTOM + FRONT + LEFT,
              rounding=calc_lid_wall_thickness / 2,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            );
          translate([calc_lid_wall_thickness, calc_lid_wall_thickness, -0.5]) color(material_colour) cube(
                [width - calc_lid_wall_thickness * 2, length - calc_lid_wall_thickness * 2, calc_cap_height + 1]
              );
        }
      }
    }
  // lid catches
  translate([0, 0, calc_cap_height]) {
    if (lid_catch == CATCH_LENGTH) {
      catch_width = width - wall_thickness * 2;
      translate([(catch_width * 6 / 8) + wall_thickness, 0, 0]) color(material_colour) rotate([0, 180, 0])
            wedge([catch_width * 2 / 4 - size_spacing * 2, lid_thickness, lid_thickness]);
      translate([(catch_width * 2 / 8) + wall_thickness, length, 0]) rotate(180) rotate([0, 180, 0])
            color(material_colour) wedge([catch_width * 2 / 4 - size_spacing * 2, lid_thickness, lid_thickness]);
    } else if (lid_catch == CATCH_WIDTH) {
      catch_length = length - wall_thickness * 2;
      translate([width, catch_length * 6 / 8 + wall_thickness + size_spacing, 0]) rotate(90)
          color(material_colour) rotate([0, 180, 0])
              wedge([catch_length * 2 / 4 - size_spacing * 2, lid_thickness, lid_thickness]);
      translate([0, catch_length * 2 / 8 + wall_thickness + size_spacing, 0]) rotate(270) color(material_colour)
            rotate([0, 180, 0]) wedge([catch_length * 2 / 4 - size_spacing * 2, lid_thickness, lid_thickness]);
    }
  }
}

// Module: CapBoxLidWithLabelAndCustomShape()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    label_radius = radius of the label corners (default 5)
//    label_border= border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    label_rotated = if the label is rotated (default false)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    label_colour = the color of the label (default undef)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_solid_background = generate a solid label background, useful for mmu (default
//    {{default_label_solid_background}})
//    label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//    inner_control = if the shape needs inner control (default false)
//    finger_hole_size = size of the finger hole to use in the lid (default 10)
// Usage: CapBoxLidWithLabelAndCustomShape(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabelAndCustomShape(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog") {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module CapBoxLidWithLabelAndCustomShape(
  width,
  length,
  height,
  text_width,
  text_height,
  text_str,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  label_radius = 5,
  label_border = 2,
  label_offset = 4,
  label_rotated = false,
  cap_height = undef,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  lid_wall_thickness = undef,
  aspect_ratio = 1.0,
  font = undef,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  label_border = 2,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  label_colour = undef,
  material_colour = default_material_colour,
  label_solid_background = undef,
  label_background_colour = undef,
  pattern_inner_control = false,
  finger_hole_size = undef
) {
  CapBoxLid(
    width=width, length=length, height=height, cap_height=cap_height, wall_thickness=wall_thickness,
    lid_thickness=lid_thickness, lid_wall_thickness=lid_wall_thickness,
    size_spacing=m_piece_wiggle_room, lid_rounding=lid_rounding, lid_inner_rounding=lid_inner_rounding,
    material_colour=material_colour
  ) {
    translate([lid_boundary, lid_boundary, 0])
      LidMeshBasic(
        width=width, length=length, lid_thickness=lid_thickness, boundary=lid_boundary,
        layout_width=layout_width, aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
        dense_shape_edges=lid_dense_shape_edges, material_colour=material_colour, inner_control=pattern_inner_control
      ) {
        if ($children > 0) {
          children(0);
        } else {
          color(material_colour) square([10, 10]);
        }
      }
    MakeLidLabel(
      width=width, length=length, text_width=text_width, text_height=text_height,
      lid_thickness=lid_thickness, border=label_border, offset=label_offset, full_height=true,
      font=font, label_rotated=label_rotated, text_str=text_str, label_radius=label_radius,
      label_colour=label_colour, material_colour=material_colour,
      solid_background=DefaultValue(label_solid_background, default_label_solid_background),
      label_background_colour=label_background_colour,
      finger_hole_size=DefaultValue(finger_hole_size, (label_rotated ? length - text_height - 10 - lid_boundary * 2 > 0 : width - text_width - 10 - lid_boundary * 2 > 0) ? 10 : 0)
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

// Module: CapBoxLidWithLabel()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//   width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    label_radius = radius of the label corners (default 5)
//    border= border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    label_rotated = if the label is rotated (default false)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    label_colour = the color of the label (default undef)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_solid_background = generate a solid label background, useful for mmu (default
//    {{default_label_solid_background}})
//    label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//    finger_hole_size = size of the finger hole to use in the lid (default 10)
// Usage: CapBoxLidWithLabel(100, 50, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabel(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabel(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog");
// Example:
//    CapBoxLidWithLabel(100, 50, 30, text_width = 70, text_height = 20, text_str = "Frog", material_colour =
//    "lightblue", label_colour = "black");
// Example:
//    default_lid_shape_type = SHAPE_TYPE_CIRCLE;
//    default_lid_shape_thickness = 1;
//    default_lid_shape_width = 13;
//    default_lid_layout_width = 10;
//    CapBoxLidWithLabel(120, 70, 30, text_width = 70, text_height = 20, text_str = "Cards");
module CapBoxLidWithLabel(
  width,
  length,
  height,
  text_width,
  text_height,
  text_str,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  label_radius = 5,
  label_border = 2,
  label_offset = 4,
  label_rotated = false,
  cap_height = undef,
  layout_width = undef,
  shape_width = undef,
  shape_type = default_lid_shape_type,
  shape_thickness = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  lid_wall_thickness = undef,
  aspect_ratio = 1.0,
  font = undef,
  lid_rounding = undef,
  lid_inner_rounding = undef,
  shape_rounding = undef,
  material_colour = default_material_colour,
  label_colour = undef,
  label_solid_background = undef,
  label_background_colour = undef,
  finger_hole_size = undef
) {
  CapBoxLidWithLabelAndCustomShape(
    width=width, length=length, height=height, cap_height=cap_height, wall_thickness=wall_thickness,
    lid_thickness=lid_thickness, lid_wall_thickness=lid_wall_thickness, font=font, text_str=text_str,
    text_width=text_width, text_height=text_height, label_radius=label_radius, label_rotated=label_rotated,
    layout_width=layout_width, size_spacing=size_spacing, aspect_ratio=aspect_ratio,
    label_border=label_border, label_offset=label_offset, lid_rounding=undef, lid_inner_rounding=undef,
    lid_pattern_dense=IsDenseShapeType(shape_type), lid_dense_shape_edges=DenseShapeEdges(shape_type),
    material_colour=material_colour, label_colour=label_colour, label_solid_background=label_solid_background,
    label_background_colour=label_background_colour, pattern_inner_control=ShapeNeedsInnerControl(shape_type),
    finger_hole_size=finger_hole_size
  ) {
    color(material_colour)
      ShapeByType(
        shape_type=shape_type, shape_width=shape_width, shape_thickness=shape_thickness,
        shape_aspect_ratio=aspect_ratio, rounding=shape_rounding
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
