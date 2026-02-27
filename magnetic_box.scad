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

// LibFile: magnetic_box.scad
//    This file has all the modules needed to generate a magnetic box.

// FileSummary: Magnetic box pieces for the magnetic boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: MagneticLid
// Description:
//   Lid using magnets to hold the top and bottom together.

// Module: MakeBoxWithMagneticLid
// Description:
//   Makes a box with holes for the round magnets in the corners. Inside the children of the box you can use the
//    $inner_height , $inner_width, $inner_length = length variables to
//    deal with the box sizes.
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    magnet_diameter = diameter of the magnet
//    magnet_thickness = thickness of the magnet
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1);
module MakeBoxWithMagneticLid(
  width,
  length,
  height,
  magnet_diameter,
  magnet_thickness,
  lid_thickness = default_lid_thickness,
  magnet_border = 1.5,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  material_colour = default_material_colour
) {
  difference() {
    color(material_colour)
      cuboid(
        [width, length, height - lid_thickness], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );
    translate(
      [
        magnet_diameter / 2 + magnet_border,
        magnet_diameter / 2 + magnet_border,
        height - lid_thickness - magnet_thickness,
      ]
    ) color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
    translate(
      [
        width - magnet_diameter / 2 - magnet_border,
        magnet_diameter / 2 + magnet_border,
        height - lid_thickness - magnet_thickness,
      ]
    ) color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
    translate(
      [
        width - magnet_diameter / 2 - magnet_border,
        length - magnet_diameter / 2 - magnet_border,
        height - lid_thickness - magnet_thickness,
      ]
    ) color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
    translate(
      [
        magnet_diameter / 2 + magnet_border,
        length - magnet_diameter / 2 - magnet_border,
        height - lid_thickness - magnet_thickness,
      ]
    ) color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    translate([wall_thickness, wall_thickness, floor_thickness]) children();
  }
}

// Module: MakeBoxWithMagneticLidInsideSpace()
// Description:
//   Makes the inside space template for the box so that it can used to intersect to pull out the corners
//   for the magnet safely.
// Usage: MakeBoxWithMagneticLidInsideSpace(100, 20, 20, 4, 1);
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    magnet_diameter = diameter of the magnet
//    magnet_thickness = thickness of the magnet
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    full_height = if the cyclinder should be the full height of the box (default true)
//    magnet_border = how far around the edges of the magnet the space should be (default 1.5)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Example:
//    MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness =
//    1);
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1)
//      MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness =
//      1);
// Example:
//    MakeBoxWithMagneticLid(width = 100, length = 50, height = 20, magnet_diameter = 5, magnet_thickness = 1)
//      MakeBoxWithMagneticLidInsideSpace(width = 100, length = 50, height = 20, magnet_diameter = 5,
//      magnet_thickness = 1, full_height = false);
module MakeBoxWithMagneticLidInsideSpace(
  width,
  length,
  height,
  magnet_diameter,
  magnet_thickness,
  lid_thickness = default_lid_thickness,
  magnet_border = 1.5,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  full_height = false,
  material_colour = default_material_colour
) {
  module make_side_cylinder(box_size) {
    union() {
      actual_height = full_height ? height - lid_thickness - floor_thickness : box_size;
      if (full_height) {
        offset = wall_thickness;
        translate(
          [
            -offset + box_size / 2,
            -offset + box_size / 2,
            height - lid_thickness - floor_thickness - actual_height,
          ]
        ) color(material_colour) cyl(h=actual_height, d=box_size, anchor=BOTTOM, $fn=32);
      } else {
        offset = wall_thickness + box_size / 2 - wall_thickness;
        translate(
          [
            -wall_thickness + box_size / 2,
            -wall_thickness + box_size / 2,
            height - lid_thickness - floor_thickness - magnet_thickness * 1.5,
          ]
        ) color(material_colour) cyl(h=magnet_thickness * 1.5, d=box_size, anchor=BOTTOM, $fn=32);
        translate(
          [
            -offset + box_size / 2,
            -offset + box_size / 2,
            height - lid_thickness - floor_thickness - actual_height - magnet_thickness * 1.5,
          ]
        ) color(material_colour)
            cyl(
              h=actual_height + 0.01, d2=box_size, d1=full_height ? box_size : 0, anchor=BOTTOM,
              $fn=32, shift=[box_size / 2 - wall_thickness, box_size / 2 - wall_thickness]
            );
      }
      side_radius = box_size / 2 - wall_thickness;
      echo(side_radius);
      if (side_radius > 0 && full_height) {
        difference() {

          translate(
            [
              -wall_thickness + box_size,
              -wall_thickness + box_size / 2 - side_radius,
              height - lid_thickness - floor_thickness - actual_height,
            ]
          ) color(material_colour)
              prismoid(
                size1=[side_radius * 2, side_radius * 2],
                size2=[side_radius * 2, side_radius * 2], h=actual_height, anchor=BOTTOM
              );
          translate(
            [
              -wall_thickness + box_size + side_radius,
              -wall_thickness + box_size / 2,
              height - lid_thickness - floor_thickness - actual_height,
            ]
          ) color(material_colour) cyl(r=side_radius, h=actual_height + 1, anchor=BOTTOM, $fn=32);
        }
        difference() {
          translate(
            [
              -wall_thickness + box_size / 2 - side_radius,
              -wall_thickness + box_size,
              height - lid_thickness - floor_thickness - actual_height,
            ]
          ) color(material_colour)
              prismoid(
                size1=[side_radius * 2, side_radius * 2],
                size2=[side_radius * 2, side_radius * 2], h=actual_height, anchor=BOTTOM
              );
          translate(
            [
              -wall_thickness + box_size / 2,
              -wall_thickness + box_size + side_radius,
              height - lid_thickness - floor_thickness - actual_height,
            ]
          ) color(material_colour) cyl(r=side_radius, h=actual_height + 1, anchor=BOTTOM, $fn=32);
        }
      }
    }
  }

  difference() {
    color(material_colour) cube(
        [
          width - wall_thickness * 2,
          length - wall_thickness * 2,
          height - lid_thickness - floor_thickness + 0.1,
        ]
      );
    box_size = magnet_diameter + magnet_border * 2;
    color(material_colour) make_side_cylinder(box_size);
    translate([width - wall_thickness * 2, 0, 0]) rotate([0, 0, 90]) color(material_colour)
          make_side_cylinder(box_size);
    translate([width - wall_thickness * 2, length - wall_thickness * 2, 0]) rotate([0, 0, 180])
        color(material_colour) make_side_cylinder(box_size);
    translate([0, length - wall_thickness * 2, 0]) rotate([0, 0, 270]) color(material_colour)
          make_side_cylinder(box_size);
  }
}

// Module: MagneticBoxLid()
// Topics: MagneticLid
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    top_thickness = the thickness of the all above the catch (default 2)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: MagneticBoxLid(100, 50, 5, 1);
// Example:
//    MagneticBoxLid(100, 50, 5, 1);
module MagneticBoxLid(
  width,
  length,
  magnet_diameter,
  magnet_thickness,
  magnet_border = 1.5,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  top_thickness = 2,
  lid_rounding = undef,
  size_spacing = m_piece_wiggle_room,
  material_colour = default_material_colour
) {
  calc_lid_rounding = DefaultValue(lid_rounding, wall_thickness);
  internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
    difference() {
      color(material_colour)
        cuboid(
          [width, length, lid_thickness], rounding=calc_lid_rounding, anchor=BOTTOM + FRONT + LEFT,
          edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
        );
      translate([magnet_diameter / 2 + magnet_border, magnet_diameter / 2 + magnet_border, -1])
        color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
      translate([width - magnet_diameter / 2 - magnet_border, magnet_diameter / 2 + magnet_border, -1])
        color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
      translate([width - magnet_diameter / 2 - magnet_border, length - magnet_diameter / 2 - magnet_border, -1])
        color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
      translate([magnet_diameter / 2 + magnet_border, length - magnet_diameter / 2 - magnet_border, -1])
        color(material_colour) cyl(d=magnet_diameter, h=magnet_thickness + 1, anchor=BOTTOM, $fn=32);
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

// Module: MagneticBoxLidWithLabelAndCustomShape()
// Topics: MagneticLid
// Description:
//    Lid for a magnetic lid box.  This uses the first
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
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: MagneticBoxLidWithLabelAndCustomShape(100, 50,  5, 1, text_str = "Frog");
// Example:
//    MagneticBoxLidWithLabelAndCustomShape(100, 50, 5, 1, text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module MagneticBoxLidWithLabelAndCustomShape(
  width,
  length,
  magnet_diameter,
  magnet_thickness,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  wall_thickness = default_wall_thickness,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  pattern_inner_control = false,
  material_colour = default_material_colour,
  label_options = undef,
) {
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
      full_height=true
    )
  );

  MagneticBoxLid(
    width, length, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, magnet_diameter=magnet_diameter,
    magnet_thickness=magnet_thickness, material_colour=material_colour
  ) {
    LidMeshBasic(
      width=width, length=length, lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
      dense_shape_edges=lid_dense_shape_edges, inner_control=pattern_inner_control,
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
      options=object(calc_label_options, full_height=true),
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

// Module: MagneticBoxLidWithLabel()
// Topics: SlidingCatch
// Description:
//    Lid for a sliding catch with a label on top of it.
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
// Usage: MagneticBoxLidWithLabel(100, 50, 5, 1, text_str = "Frog");
// Example:
//    MagneticBoxLidWithLabel(100, 50, 5, 1, text_str = "Frog");
module MagneticBoxLidWithLabel(
  width,
  length,
  magnet_diameter,
  magnet_thickness,
  text_str,
  magnet_border = 1.5,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = undef,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  material_colour = default_material_colour,
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

  MagneticBoxLidWithLabelAndCustomShape(
    width=width, length=length, magnet_diameter=magnet_diameter,
    magnet_thickness=magnet_thickness,
    wall_thickness=wall_thickness, lid_thickness=lid_thickness, text_str=text_str,
    layout_width=layout_width, size_spacing=size_spacing, aspect_ratio=aspect_ratio,
    lid_rounding=lid_rounding, lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
    material_colour=material_colour,
    label_options=calc_label_options
  ) {
    color(material_colour)
      ShapeByType(
        options=calc_shape_options,
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
