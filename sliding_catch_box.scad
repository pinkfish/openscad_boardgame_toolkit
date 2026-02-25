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

// LibFile: sliding_catch_box.scad
//    This file has all the modules needed to generate a sliding catch box.

// FileSummary: Sliding catch box pieces for the sliding catch boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlidingCatch
// Description:
//    A lid that slides into a groove on the top and the front to catch, a bit harder
//    to stack but makes a nice simple box and fairly sturdy rather than a sliding lid.
//    The lid is thicker than a sliding lid box.

// Module: MakeBoxWithSlidingCatchLid()
// Topics: SlidingCatch
// Description:
//   Creates a box with a sliding catch lid on the top.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Arguments:
//   width = outside width of the box
//   length = inside width of the box
//   height = outside height of the box
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//   top_thickness = the thickness of the all above the catch (default 2)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: MakeBoxWithSlidingCatchLid(100, 50, 20);
// Example:
//    MakeBoxWithSlidingCatchLid(100, 50, 20);
module MakeBoxWithSlidingCatchLid(
  width,
  length,
  height,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  top_thickness = 2,
  floor_thickness = default_floor_thickness,
  material_colour = default_material_colour
) {
  calc_sliding_len = (length - wall_thickness) / 6;
  difference() {

    color(material_colour)
      cuboid(
        [width, length, height], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );
    // middle diff.
    translate([wall_thickness, wall_thickness, floor_thickness]) color(material_colour)
        cube([width - wall_thickness * 2, length - wall_thickness * 2, height]);

    // Sliding cutouts.
    translate([-0.5, wall_thickness + calc_sliding_len, height - lid_thickness - top_thickness])
      color(material_colour)
        cuboid(
          [width + 1, calc_sliding_len + 1, lid_thickness + size_spacing],
          anchor=FRONT + LEFT + BOTTOM, rounding=lid_thickness / 2, edges=[BACK + BOTTOM]
        );
    translate(
      [-0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - lid_thickness - top_thickness]
    )
      color(material_colour)
        cuboid(
          [width + 1, calc_sliding_len + size_spacing * 2, lid_thickness + top_thickness + size_spacing],
          anchor=FRONT + LEFT + BOTTOM, rounding=lid_thickness / 2, edges=[BACK + BOTTOM]
        );
    // Rounding corners.
    translate([-0.5, wall_thickness + calc_sliding_len * 2 - size_spacing, height - top_thickness + size_spacing])
      color(material_colour)
        cuboid(
          [width + 1, calc_sliding_len + size_spacing * 2, top_thickness - size_spacing],
          anchor=FRONT + LEFT + BOTTOM, rounding=-top_thickness / 2,
          edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK], $fn=32
        );

    // Second cutout.
    translate(
      [
        -0.5,
        wall_thickness + length - calc_sliding_len * 2 - size_spacing * 2,
        height - lid_thickness - top_thickness,
      ]
    ) color(material_colour)
        cuboid(
          [width + 1, calc_sliding_len + 1, lid_thickness + size_spacing], rounding=lid_thickness,
          anchor=FRONT + LEFT + BOTTOM, edges=[BACK + TOP]
        );
    translate([-0.5, length - calc_sliding_len - size_spacing * 2, height - lid_thickness - top_thickness])
      color(material_colour) cuboid(
          [width + 1, calc_sliding_len + size_spacing * 2 + 1, lid_thickness + top_thickness + size_spacing],
          anchor=FRONT + LEFT + BOTTOM, rounding=lid_thickness / 2, edges=[BACK + BOTTOM]
        );
    // Rounding corners.
    translate(
      [
        -0.5,
        wall_thickness + length - calc_sliding_len - wall_thickness - size_spacing * 2,
        height - top_thickness + size_spacing,
      ]
    ) color(material_colour)
        cuboid(
          [width + 1, wall_thickness + calc_sliding_len + size_spacing * 2, top_thickness - size_spacing],
          anchor=FRONT + LEFT + BOTTOM, rounding=-top_thickness / 2,
          edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK], $fn=32
        );

    // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
    // just not the walls.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    intersection() {
      translate([wall_thickness, wall_thickness, floor_thickness]) color(material_colour)
          cube([width - wall_thickness * 2, length - wall_thickness * 2, height + 2]);
      translate([wall_thickness, wall_thickness, floor_thickness]) children();
    }
  }
}

// Module: SlidingCatchBoxLid()
// Topics: SlidingCatch
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    top_thickness = the thickness of the all above the catch (default 2)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: SlidingCatchBoxLid(100, 50);
// Example:
//    SlidingCatchBoxLid(100, 50);
module SlidingCatchBoxLid(
  width,
  length,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  top_thickness = 2,
  fill_middle = true,
  lid_roudning = undef,
  lid_rounding = undef,
  material_colour = default_material_colour
) {
  calc_sliding_len = (length - wall_thickness) / 6;
  calc_lid_thickness = fill_middle ? lid_thickness + top_thickness : lid_thickness;
  calc_lid_rounding = DefaultValue(lid_roudning, top_thickness / 2);

  internal_build_lid(lid_thickness=calc_lid_thickness, size_spacing=size_spacing) {
    difference() {
      union() {
        color(material_colour) cube([width, length - wall_thickness, lid_thickness - size_spacing]);
        if (fill_middle) {
          translate([wall_thickness, 0, lid_thickness - 0.1]) color(material_colour)
              cuboid(
                [width - wall_thickness * 2 - size_spacing * 2, length, top_thickness + 0.1],
                anchor=FRONT + LEFT + BOTTOM, rounding=calc_lid_rounding, edges=TOP, $fn=32
              );
        }
      }
      // Front piece.
      translate([-1, -1, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1]);
      translate([width - wall_thickness - size_spacing, -1, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1]);
      // Middle piece.
      translate([-1, calc_sliding_len * 2, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len * 2, lid_thickness + 1]);
      translate([width - wall_thickness - size_spacing, calc_sliding_len * 2, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len * 2, lid_thickness + 1]);

      // End piece.
      translate([-1, calc_sliding_len * 5, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1]);
      translate([width - wall_thickness - size_spacing, calc_sliding_len * 5, -0.5]) color(material_colour)
          cube([wall_thickness + size_spacing + 1, wall_thickness + calc_sliding_len + 1, lid_thickness + 1]);
    }
    if ($children > 0) {
      translate([wall_thickness, 0, 0]) children(0);
    }
    if ($children > 1) {
      translate([wall_thickness, 0, 0]) children(1);
    }
    if ($children > 2) {
      translate([wall_thickness, 0, 0]) children(2);
    }
    if ($children > 3) {
      translate([wall_thickness, 0, 0]) children(3);
    }
    if ($children > 4) {
      translate([wall_thickness, 0, 0]) children(4);
    }
    if ($children > 5) {
      translate([wall_thickness, 0, 0]) children(5);
    }
  }
}

// Module: SlidingCatchBoxLidWithLabelAndCustomShape()
// Topics: SlidingCatch
// Description:
//    Lid for a sliding catch box.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    width = outside width of the box
//    length = outside length of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    text_str = the string to use for the label
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    top_thickness = the thickness of the all above the catch (default 2)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: SlidingCatchBoxLidWithLabelAndCustomShape(100, 50, text_str = "Frog");
// Example:
//    SlidingCatchBoxLidWithLabelAndCustomShape(100, 50, text_str = "Frog") {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module SlidingCatchBoxLidWithLabelAndCustomShape(
  width,
  length,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  font = undef,
  lid_rounding = undef,
  wall_thickness = default_wall_thickness,
  top_thickness = 2,
  fill_middle = true,
  material_colour = default_material_colour,
  pattern_inner_control = false,
  label_options = undef
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );

  SlidingCatchBoxLid(
    width, length, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, top_thickness=top_thickness,
    fill_middle=fill_middle, material_colour=material_colour
  ) {
    LidMeshBasic(
      width=width, length=length, lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, inner_control=pattern_inner_control
    ) {
      if ($children > 0) {
        children(0);
      } else {
        color(material_colour) square([10, 10]);
      }
    }
    MakeLidLabel(
      width=width, length=length,
      lid_thickness=lid_thickness,
      text_str=text_str, 
      options=object(calc_label_options, full_height=false),
    );

    // Fingernail pull
    intersection() {
      color(material_colour) cube([width - calc_label_options.border, length - calc_label_options.border, lid_thickness]);
      translate([(width) / 2, length - calc_label_options.border - 3, 0]) color(material_colour)
          SlidingLidFingernail(lid_thickness);
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

// Module: SlidingCatchBoxLidWithLabel()
// Topics: SlidingCatch
// Description:
//    Lid for a sliding catch with a label on top of it.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    top_thickness = thickness of the top above the lid (default 1)
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    text_str = the string to use for the label
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    top_thickness = the thickness of the all above the catch (default 2)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: SlidingCatchBoxLidWithLabel(100, 50, text_str = "Frog");
// Example:
//    SlidingCatchBoxLidWithLabel(100, 50,  text_str = "Frog");
module SlidingCatchBoxLidWithLabel(
  width,
  length,
  text_str,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  layout_width = undef,
  shape_width = undef,
  shape_type = default_lid_shape_type,
  shape_thickness = undef,
  aspect_ratio = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  top_thickness = 2,
  fill_middle = true,
  lid_rounding = undef,
  shape_rounding = undef,
  material_colour = default_material_colour,
  label_options = undef
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );

  calc_lid_thickness = fill_middle ? lid_thickness + top_thickness : lid_thickness;

  SlidingCatchBoxLidWithLabelAndCustomShape(
    width=width, length=length, wall_thickness=wall_thickness, lid_thickness=calc_lid_thickness,
    text_str=text_str,
    layout_width=layout_width,
    size_spacing=size_spacing, aspect_ratio=aspect_ratio, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary, top_thickness=top_thickness, fill_middle=fill_middle, material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(shape_type),
    label_options=calc_label_options
  ) {
    color(material_colour)
      ShapeByType(
        shape_type=shape_type, shape_width=shape_width, shape_thickness=shape_thickness,
        shape_aspect_ratio=aspect_ratio, rounding=shape_rounding
      );

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
