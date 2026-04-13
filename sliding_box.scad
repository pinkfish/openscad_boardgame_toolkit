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

// LibFile: sliding_box.scad
//    This file has all the modules needed to generate a sliding box.

// FileSummary: Sliding box pieces for the sliding boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlidingBox
//   All the pieces for making sliding lids and different types of sliding lids/boxes.

// Module: SlidingLid()
// Description:
//   Creates a sliding lid for a sliding lid box, the children to this module are inserted into the lid.
//   This does all the right things on the edges, uses some
//   wiggle room to add in a buffer and also does a small amount of angling on the ends to make them easier
//   to insert. 
// Usage:
//   SlidingLid(size=[10, 30], lid_thickness=3, wall_thickness = 2, size_spacing = 0.2);
// Arguments:
//   size = [width, length] the size of the box itself
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   size_spacing = how much of an offset to use in generate the slides spacing (default {{m_piece_wiggle_room}})
//   lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//   lid_on_length = lid along the length of the box (default false)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   lid_chamfer = how much to chamfer the lid
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLid(size = [100, 100], lid_thickness=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
// Example:
//   SlidingLid(size=[100, 100], lid_thickness=3, wall_thickness = 2, lid_on_length = true)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
module SlidingLid(
  size,
  lid_thickness = default_lid_thickness,
  wall_thickness = undef,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  lid_chamfer = undef,
  lid_on_length = false,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_lid_thickness = DefaultValue(lid_thickness, default_lid_thickness);
  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);
  calc_lid_rounding = DefaultValue(lid_rounding, calc_wall_thickness / 2);
  calc_lid_chamfer = DefaultValue(lid_chamfer, calc_wall_thickness / 6);
  if (lid_on_length) {
    translate([0, length, 0]) rotate([0, 0, 270])
        SlidingLid(
          size=[length, width], lid_thickness=calc_lid_thickness, wall_thickness=calc_wall_thickness,
          size_spacing=size_spacing, lid_rounding=calc_lid_rounding, lid_chamfer=calc_lid_chamfer,
          lid_on_length=false, material_colour=material_colour
        ) {
          if ($children > 0) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(0);
              }
          }
          if ($children > 1) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(1);
              }
          }
          if ($children > 2) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(2);
              }
          }
          if ($children > 3) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(3);
              }
          }
          if ($children > 4) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(4);
              }
          }
          if ($children > 5) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(5);
              }
          }
          if ($children > 6) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(6);
              }
          }
          if ($children > 7) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(7);
              }
          }
          if ($children > 8) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(8);
              }
          }
          if ($children > 9) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(9);
              }
          }
          if ($children > 10) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(10);
              }
          }
          if ($children > 11) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(11);
              }
          }
          if ($children > 12) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(12);
              }
          }
          if ($children > 13) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(13);
              }
          }
          if ($children > 14) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(14);
              }
          }
          if ($children > 15) {
            translate([length - calc_wall_thickness / 2, -calc_wall_thickness / 2, 0]) rotate([0, 0, -270]) {
                children(15);
              }
          }
        }
  } else {
    internal_build_lid(lid_thickness=calc_lid_thickness, size_spacing=size_spacing) {
      difference() {
        // Lip and raised bit
        union() {
          difference() {
            lid_width = width - 2 * (calc_wall_thickness + size_spacing);
            lid_length = length - calc_wall_thickness;
            translate([calc_wall_thickness / 2 + size_spacing, calc_wall_thickness / 2, 0])
              color(material_colour)
                diff()
                  cuboid(
                    [lid_width, lid_length, calc_lid_thickness], anchor=BOTTOM + FRONT + LEFT,
                    rounding=calc_lid_rounding,
                    edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
                  ) edge_mask(TOP + BACK) rounding_edge_mask(r=calc_lid_rounding / 2, l=lid_width);
            // Top edge easing.
            translate(
              [
                calc_wall_thickness / 2 - size_spacing,
                calc_wall_thickness / 2 - size_spacing,
                calc_lid_thickness / 2 - size_spacing,
              ]
            ) color(material_colour) linear_extrude(height=calc_lid_thickness + 10)
                  right_triangle([size_spacing * 4, 15]);
            translate(
              [
                width - calc_wall_thickness * 2 + size_spacing * 7.5,
                calc_wall_thickness / 2 - size_spacing,
                calc_lid_thickness / 2 - size_spacing,
              ]
            ) color(material_colour) linear_extrude(height=calc_lid_thickness + 10) xflip()
                    right_triangle([size_spacing * 4, 15]);
          }
          // bottom layer.
          difference() {
            translate([0, 0, 0]) color(material_colour) cuboid(
                  [
                    width - calc_wall_thickness - size_spacing * 2,
                    length - calc_wall_thickness / 2,
                    calc_lid_thickness / 2 - size_spacing,
                  ],
                  anchor=BOTTOM + FRONT + LEFT, chamfer=calc_lid_chamfer,
                  edges=[TOP + LEFT, TOP + RIGHT, TOP + FRONT, FRONT + LEFT, FRONT + RIGHT]
                );

            translate([0, 0, calc_lid_thickness / 2 - 0.25]) rotate([0, 45, 0])
                translate([-size_spacing / 20, -size_spacing, -calc_lid_thickness / 2])
                  color(material_colour) linear_extrude(height=calc_lid_thickness + 10)
                      right_triangle([calc_wall_thickness / 2, 15]);

            translate([0, -calc_wall_thickness / 2, calc_wall_thickness - 0.35]) translate(
                [
                  width - calc_wall_thickness - size_spacing / 1.1,
                  -size_spacing,
                  -calc_lid_thickness / 2,
                ]
              ) rotate([0, -45, 0]) color(material_colour) linear_extrude(height=calc_lid_thickness + 10)
                      xflip() right_triangle([calc_wall_thickness / 2, 15]);
          }
        }

        // Edge easing.
        translate([-size_spacing / 20, -size_spacing, -calc_lid_thickness / 2]) color(material_colour)
            linear_extrude(height=calc_lid_thickness + 10) right_triangle([calc_wall_thickness / 2, 15]);
        translate([width - calc_wall_thickness - size_spacing / 1.1, -size_spacing, -calc_lid_thickness / 2])
          color(material_colour) linear_extrude(height=calc_lid_thickness + 10) xflip()
                right_triangle([calc_wall_thickness / 2, 15]);
      }

      $inner_width = width - (lid_on_length ? calc_wall_thickness / 2 : calc_wall_thickness);
      $inner_length = length - (lid_on_length ? calc_wall_thickness : calc_wall_thickness / 2);

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
      if ($children > 9) {
        children(9);
      }
      if ($children > 10) {
        children(10);
      }
      if ($children > 11) {
        children(11);
      }
      if ($children > 12) {
        children(12);
      }
      if ($children > 13) {
        children(13);
      }
      if ($children > 14) {
        children(14);
      }
      if ($children > 15) {
        children(15);
      }
      if ($children > 16) {
        children(16);
      }
    }
  }
}

// Module: SlidingBoxLidWithCustomShape()
// Topics: SlidingBox, SlidingLid
// Description:
//    Lid for a sliding lid box.  This uses the first
//    child as the shape for repeating on the lid and the rest as children for the lid.
// Arguments:
//    size = [width, length] outside size of the lid
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    lid_on_length = lid along the length of the box (default false)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    lid_chamfer = how much to chamfer the lid
//    pattern_inner_control = if the shape needs inner control (default false)
// Example:
//    SlidingBoxLidWithCustomShape([100, 50]) {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module SlidingBoxLidWithCustomShape(
  size,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  wall_thickness = undef,
  lid_chamfer = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  lid_on_length = false,
  material_colour = default_material_colour,
  pattern_inner_control = false,
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];
  calc_lid_thickness = DefaultValue(lid_thickness, default_lid_thickness);
  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);

  SlidingLid(
    size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, lid_chamfer=lid_chamfer,
    lid_on_length=lid_on_length, material_colour=material_colour
  ) {
    union() {
      LidMeshBasic(
        size=[
          width - (lid_on_length ? calc_wall_thickness / 2 : calc_wall_thickness),
          length - (lid_on_length ? calc_wall_thickness : calc_wall_thickness / 2),
        ],
        lid_thickness=lid_thickness, boundary=lid_boundary,
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
    }

    // Don't include the first child since is it used for the lid shape.
    if ($children > 1) {
      children(1);
    }

    // Fingernail pull
    if (lid_on_length) {
      intersection() {
        color(material_colour) cube([width - calc_wall_thickness, length - calc_wall_thickness, lid_thickness]);
        translate([width - calc_wall_thickness - 3, length / 2 - calc_wall_thickness / 2, 0]) rotate(270)
            SlidingLidFingernail(calc_lid_thickness, material_colour=material_colour);
      }
    } else {
      intersection() {
        color(material_colour) cube([width - calc_wall_thickness, length - calc_wall_thickness, lid_thickness]);
        translate([(width) / 2 - calc_wall_thickness / 2, length - calc_wall_thickness - 3, 0])
          SlidingLidFingernail(calc_lid_thickness, material_colour=material_colour);
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
    if ($children > 6) {
      children(6);
    }
    if ($children > 7) {
      children(7);
    }
    if ($children > 8) {
      children(8);
    }
    if ($children > 9) {
      children(9);
    }
    if ($children > 10) {
      children(10);
    }
    if ($children > 11) {
      children(11);
    }

    if ($children > 12) {
      children(12);
    }
  }
}

// Module: SlidingBoxLidWithLabelAndCustomShape()
// Topics: SlidingBox, SlidingLid
// Description:
//    Lid for a sliding lid box.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    wall_thickness = the width of the wall (default {{default_wall_thickness}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    lid_on_length = lid along the length of the box (default false)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    lid_chamfer = how much to chamfer the lid
//    pattern_inner_control = if the shape needs inner control (default false)
// Usage: SlidingBoxLidWithLabelAndCustomShape(size=[100, 50], text_str = "Frog");
// Example:
//    SlidingBoxLidWithLabelAndCustomShape(size=[100, 50], text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module SlidingBoxLidWithLabelAndCustomShape(
  size,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  wall_thickness = default_wall_thickness,
  lid_rounding = undef,
  lid_chamfer = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  lid_on_length = false,
  material_colour = default_material_colour,
  pattern_inner_control = false,
  label_options = undef
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );

  assert($children > 0, "Must be one child for the pattern");
  assert(width > 0 && length > 0, str("Need width,lenght > 0 width=", width, " length=", length));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));
  assert(size_spacing > 0, str("Need size_spacing > 0, size_spacing=", size_spacing));
  assert(lid_rounding == undef || lid_rounding > 0, str("Need lid_rounding undef or > 0", lid_rounding));
  assert(lid_chamfer == undef || lid_chamfer > 0, str("Need lid_chamfer undef or > 0", lid_chamfer));
  assert(text_str != undef, "Need to specify a label, text_str == undef");

  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);

  SlidingBoxLidWithCustomShape(
    size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, lid_chamfer=lid_chamfer,
    lid_on_length=lid_on_length, material_colour=material_colour,
    lid_boundary=lid_boundary,
    layout_width=layout_width,
    aspect_ratio=aspect_ratio,
    lid_pattern_dense=lid_pattern_dense, lid_dense_shape_edges=lid_dense_shape_edges,
    pattern_inner_control=pattern_inner_control
  ) {
    // 0 child is the pattern for the lid.
    children(0);

    translate([calc_wall_thickness / 2, calc_wall_thickness / 2, 0]) {
      MakeLidLabel(
        size=[width - calc_wall_thickness * 2, length - calc_wall_thickness * 2],
        lid_thickness=lid_thickness,
        text_str=text_str,
        options=object(calc_label_options, full_height=false),
      );
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
    if ($children > 7) {
      children(7);
    }
    if ($children > 8) {
      children(8);
    }
    if ($children > 9) {
      children(9);
    }
    if ($children > 10) {
      children(10);
    }
  }
}

// Module: SlidingBoxLidWithLabel
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
// Usage:
//    SlidingBoxLidWithLabel(size = [100, 100], lid_thickness = 3, text_str
//    = "Trains");
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = The string to write
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_spacing = how much of an offset to use in generate the slides spacing (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_on_length = lid along the length of the box (default false)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
//    lid_chamfer = how much to chamfer the lid
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithLabel(
//        size = [100, 100], lid_thickness = 3, text_str = "Trains");
module SlidingBoxLidWithLabel(
  size,
  text_str,
  lid_thickness = default_lid_thickness,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = undef,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_chamfer = undef,
  lid_rounding = undef,
  lid_on_length = false,
  material_colour = default_material_colour,
  label_options = undef,
  shape_options = undef
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );

  assert(width > 0 && length > 0, str("Need width,lenght > 0 width=", width, " length=", length));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));
  assert(size_spacing > 0, str("Need size_spacing > 0, size_spacing=", size_spacing));
  assert(lid_rounding == undef || lid_rounding > 0, str("Need lid_rounding undef or > 0", lid_rounding));
  assert(lid_chamfer == undef || lid_chamfer > 0, str("Need lid_chamfer undef or > 0", lid_chamfer));
  assert(text_str != undef, "Need to specify a label, text_str == undef");

  SlidingBoxLidWithLabelAndCustomShape(
    size=size, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    text_str=text_str,
    layout_width=layout_width, size_spacing=size_spacing,
    aspect_ratio=aspect_ratio, lid_chamfer=lid_chamfer, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    lid_on_length=lid_on_length, material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
    label_options=calc_label_options
  ) {
    translate([lid_boundary, lid_boundary, 0]) {
      color(material_colour)
        ShapeByType(
          options=calc_shape_options,
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

// Module: SlidingBoxLidWithShape
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
// Usage:
//    SlidingBoxLidWithShape(size = [100, 100], lid_thickness = 3);
// Arguments:
//    size = [width, length] outside size of the lid
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = how much of an offset to use in generate the slides spacing (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_on_length = lid along the length of the box (default false)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    shape_options = options for the shape (default undef)
//    lid_chamfer = how much to chamfer the lid
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithShape(
//        size = [100, 100], lid_thickness = 3);
module SlidingBoxLidWithShape(
  size,
  lid_thickness = default_lid_thickness,
  lid_boundary = 10,
  layout_width = undef,
  wall_thickness = default_wall_thickness,
  aspect_ratio = undef,
  size_spacing = m_piece_wiggle_room,
  lid_chamfer = undef,
  lid_rounding = undef,
  lid_on_length = false,
  material_colour = default_material_colour,
  shape_options = undef
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  assert(width > 0 && length > 0, str("Need width,lenght > 0 width=", width, " length=", length));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));
  assert(size_spacing > 0, str("Need size_spacing > 0, size_spacing=", size_spacing));
  assert(lid_rounding == undef || lid_rounding > 0, str("Need lid_rounding undef or > 0", lid_rounding));
  assert(lid_chamfer == undef || lid_chamfer > 0, str("Need lid_chamfer undef or > 0", lid_chamfer));
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );

  SlidingBoxLidWithCustomShape(
    size=size, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    layout_width=layout_width, size_spacing=size_spacing,
    aspect_ratio=aspect_ratio, lid_chamfer=lid_chamfer, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    lid_on_length=lid_on_length, material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
  ) {
    translate([lid_boundary, lid_boundary, 0]) {
      color(material_colour)
        ShapeByType(
          options=calc_shape_options,
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

// Module: MakeBoxWithSlidingLid()
// Description:
//   Makes a box with a sliding lid, this just creates the box itself with the cutouts for the
//   sliding lid pieces.  The children to this will be removed from inside the box and how to add
//   in the cutouts.
//   .
//   The children all start from the edge inside the wall width and up from the floor in the box.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Usage:
//   MakeBoxWithSlidingLid([50, 100, 20]);
// Arguments:
//    size = [width, length, height] outside size of the box
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    lid_on_length = lid along the length of the box (default false)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    positive_only_children = the list of children to be positive only
//    positive_negative_children = the list of children to be positive and negative
//    positive_colour = colour of the postive pieces {{default_positive_colour}}
//    size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
// Topics: SlidingBox
// Example:
//   MakeBoxWithSlidingLid([50, 100, 20]);
module MakeBoxWithSlidingLid(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  floor_thickness = default_floor_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_on_length = false,
  material_colour = default_material_colour,
  positive_colour = default_positive_colour,
  positive_only_children = [],
  positive_negative_children = [],
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];

  difference() {
    color(material_colour)
      diff()
        cuboid(
          [width, length, height], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
          edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
        ) {
          edge_mask(TOP) rounding_edge_mask(r=wall_thickness / 2, l=max(length, width));
        }
    rounding_offset = 0.01;
    if (lid_on_length) {
      translate([-rounding_offset, wall_thickness, height - lid_thickness]) color(material_colour) cuboid(
            [
              width - wall_thickness + size_spacing + rounding_offset,
              length - wall_thickness * 2,
              lid_thickness + size_spacing / 2,
            ],
            anchor=BOTTOM + FRONT + LEFT
          );
      translate([-rounding_offset, wall_thickness / 2, height - lid_thickness]) color(material_colour)
          cuboid(
            [width - wall_thickness / 2 + rounding_offset, length - wall_thickness, lid_thickness / 2],
            anchor=BOTTOM + FRONT + LEFT, chamfer=lid_thickness / 6,
            edges=[TOP + FRONT, TOP + BACK, TOP + RIGHT]
          );

      translate([0, length / 2, height - lid_thickness])
        rotate([90, 90, 0])
          rounding_edge_mask(r=wall_thickness / 4, height=length - wall_thickness * 2);
    } else {
      translate([wall_thickness, -rounding_offset, height - lid_thickness]) color(material_colour) cuboid(
            [
              width - wall_thickness * 2,
              length - wall_thickness + size_spacing + rounding_offset,
              lid_thickness + size_spacing / 2,
            ],
            anchor=BOTTOM + FRONT + LEFT
          );

      translate([wall_thickness / 2, -rounding_offset, height - lid_thickness]) color(material_colour)
          cuboid(
            [width - wall_thickness, length - wall_thickness / 2 + rounding_offset, lid_thickness / 2],
            anchor=BOTTOM + FRONT + LEFT, chamfer=lid_thickness / 6,
            edges=[TOP + LEFT, TOP + RIGHT, TOP + BACK]
          );
      translate([width / 2, 0, height - lid_thickness])
        rotate([0, 90, 0])
          rounding_edge_mask(r=wall_thickness / 4, height=length - wall_thickness * 2);
    }

    // Make everything start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    for (i = [0:$children - 1]) {
      if (!in_list(i, positive_only_children)) {
        translate([wall_thickness, wall_thickness, floor_thickness]) children(i);
      }
    }
  }
  if (len(positive_only_children) > 0 || (len(positive_negative_children) > 0 && MAKE_MMU == 1)) {
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    for (i = positive_only_children) {
      color(positive_colour)
        translate([wall_thickness, wall_thickness, floor_thickness]) children(i);
    }
    for (i = positive_negative_children) {
      color(positive_colour)
        translate([wall_thickness, wall_thickness, floor_thickness]) children(i);
    }
  }
}
