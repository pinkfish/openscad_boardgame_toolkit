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

// Function: MakeSlidingLidOptions()
// Description: 
//    Make the sliding lid options object.
// Arguments:
//    two_layer = if the lid has a cap layer, a second layer on top (default false)
//    two_layer_top_lid_ratio = the ratio of the top bit to the sliding bit (default 0.5)
//    two_layer_vee_shape = if the two layer lid should use a vee slide (default false)
function MakeSlidingLidOptions(
  two_layer = false,
  two_layer_top_lid_ratio = 0.5,
  two_layer_vee_shape = false
) =
  object(
    two_layer=two_layer,
    two_layer_top_lid_ratio=two_layer_top_lid_ratio,
    two_layer_vee_shape=two_layer_vee_shape
  );

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
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLid(size = [100, 100], lid_thickness=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
// Example:
//   SlidingLid(size=[100, 100], lid_thickness=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
// Example:
//   SlidingLid(size=[100, 100], lid_thickness=3, wall_thickness = 2, sliding_lid_options=MakeSlidingLidOptions(two_layer=true))
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
// Example:
//   SlidingLid(size=[100, 100], lid_thickness=3, wall_thickness = 2, 
//        sliding_lid_options=MakeSlidingLidOptions(two_layer=true, two_layer_vee_shape=true))
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
// Example:
//   SlidingLid(size=[100, 100], lid_thickness=3, wall_thickness = 2, 
//        sliding_lid_options=MakeSlidingLidOptions(two_layer=true, two_layer_top_lid_ratio=0.25))
//     translate([ 10, 10, 0 ])
//       LidMeshHex(size = [100, 100], lid_thickness = 3, boundary = 10, radius = 12);
module SlidingLid(
  size,
  sliding_lid_options = undef,
  lid_thickness = default_lid_thickness,
  wall_thickness = undef,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);
  calc_lid_thickness = DefaultValue(lid_thickness, default_lid_thickness);
  calc_lid_rounding = DefaultValue(lid_rounding, calc_wall_thickness / 2);
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  // Sizes for inside bits.
  chamfer =
    calc_sliding_lid_options.two_layer ? 0
    : calc_wall_thickness / 2 > calc_lid_thickness - size_spacing ? calc_wall_thickness / 2 : calc_lid_thickness - size_spacing;
  lid_width =
    calc_sliding_lid_options.two_layer ? width
    : width - 2 * calc_wall_thickness + chamfer * 2 + size_spacing;
  lid_length =
    calc_sliding_lid_options.two_layer ? length
    : length - calc_wall_thickness + chamfer - size_spacing;
  top_cover = calc_sliding_lid_options.two_layer_top_lid_ratio * calc_lid_thickness;
  lid_under_cover = calc_lid_thickness - top_cover;
  middle_chamfer = calc_wall_thickness > lid_under_cover ? lid_under_cover / 2 : calc_wall_thickness / 2;
  two_layer_chamfer =
    calc_sliding_lid_options.two_layer_vee_shape ? middle_chamfer
    : calc_wall_thickness / 2 < lid_under_cover ? calc_wall_thickness / 2 : lid_under_cover;

  module FlipStuff() {
    if (calc_sliding_lid_options.two_layer)
      up(lid_thickness)
        back(lid_length)
          xrot(180)
            children();
    else
      children();
  }

  module mask_2sliding_lid() {
    path = (
      calc_sliding_lid_options.two_layer_vee_shape ?
        [
          [0, 0],
          [calc_wall_thickness / 2 + size_spacing, 0],
          [calc_wall_thickness / 2 + middle_chamfer + size_spacing, middle_chamfer],
          [calc_wall_thickness / 2 + size_spacing, lid_under_cover],
          [0, lid_under_cover],
        ]
      : [
        [0, 0],
        [size_spacing, 0],
        [calc_wall_thickness - two_layer_chamfer, 0],
        [calc_wall_thickness, lid_under_cover],
        [size_spacing, lid_under_cover],
        [0, lid_under_cover],
      ]
    );
    attachable(anchor=CENTER, spin=0, two_d=true, path=path, extent=true) {
      polygon(path);
      children();
    }
  }

  FlipStuff()
    internal_build_lid(lid_thickness=calc_lid_thickness, size_spacing=size_spacing) {
      difference() {
        // Lip and raised bit
        color(material_colour)
          diff()
            cuboid(
              [lid_width, lid_length, calc_lid_thickness], anchor=BOTTOM + FRONT + LEFT,
              chamfer=chamfer + size_spacing,
              edges=calc_sliding_lid_options.two_layer ?
                [LEFT + TOP, RIGHT + TOP, TOP + FRONT, LEFT + BOTTOM, RIGHT + BOTTOM, BOTTOM + FRONT]
              : [LEFT + TOP, RIGHT + TOP, TOP + FRONT]
            ) {
              edge_mask([LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK])
                rounding_edge_mask(
                  r=calc_sliding_lid_options.two_layer ? calc_wall_thickness : calc_lid_rounding,
                  l=lid_thickness + size_spacing
                );
              edge_mask(
                calc_sliding_lid_options.two_layer ? [TOP]
                : [TOP + BACK]
              )
                rounding_edge_mask(
                  r=calc_sliding_lid_options.two_layer ? top_cover
                  : calc_lid_rounding / 2, l=max(lid_length, lid_width)
                );
              // This makes the v cut out in the side if it is a two layer lid.
              if (calc_sliding_lid_options.two_layer) {
                edge_profile_asym([BOTTOM + LEFT, BOTTOM + RIGHT])
                  mask_2sliding_lid();
              }
            }
        if (calc_sliding_lid_options.two_layer) {
          // The front cutout.
          down(size_spacing)
            cuboid(
              [lid_width, calc_wall_thickness, lid_under_cover + size_spacing],
              anchor=BOTTOM + FRONT + LEFT,
            );
          translate([calc_wall_thickness - two_layer_chamfer, wall_thickness, -top_cover])
            linear_extrude(h=lid_thickness)
              mask2d_roundover(r=calc_lid_rounding);
          translate([lid_width - calc_wall_thickness + two_layer_chamfer, wall_thickness, -top_cover])
            xflip()
              linear_extrude(h=lid_thickness)
                mask2d_roundover(r=calc_lid_rounding);
        } else {
          // Edge easing.
          translate([-size_spacing / 20, -size_spacing, -calc_lid_thickness / 2]) color(material_colour)
              linear_extrude(height=calc_lid_thickness + 10) right_triangle([calc_wall_thickness / 2, 15]);
          translate([lid_width + size_spacing / 20, -size_spacing, -calc_lid_thickness / 2])
            color(material_colour) linear_extrude(height=calc_lid_thickness + 10) xflip()
                  right_triangle([calc_wall_thickness / 2, 15]);
        }
      }

      $inner_width = width - calc_wall_thickness;
      $inner_length = length - calc_wall_thickness / 2;

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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    pattern_inner_control = if the shape needs inner control (default false)
//    sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
// Example:
//    SlidingBoxLidWithCustomShape([100, 50]) {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module SlidingBoxLidWithCustomShape(
  size,
  sliding_lid_options = undef,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  wall_thickness = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  material_colour = default_material_colour,
  pattern_inner_control = false,
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];
  calc_lid_thickness = DefaultValue(lid_thickness, default_lid_thickness);
  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  SlidingLid(
    size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing,
    material_colour=material_colour, sliding_lid_options=calc_sliding_lid_options,
  ) {
    LidMeshBasic(
      size=[
        width - calc_wall_thickness,
        length - calc_wall_thickness / 2,
      ],
      lid_thickness=lid_thickness,
      boundary=lid_boundary,
      layout_width=layout_width,
      aspect_ratio=aspect_ratio,
      dense=lid_pattern_dense,
      dense_shape_edges=lid_dense_shape_edges,
      material_colour=material_colour,
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

    // Fingernail pull
    intersection() {
      color(material_colour) cube([width - calc_wall_thickness, length - calc_wall_thickness, lid_thickness]);
      translate([(width) / 2 - calc_wall_thickness / 2, length - calc_wall_thickness - 3, 0])
        SlidingLidFingernail(calc_lid_thickness, material_colour=material_colour);
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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    pattern_inner_control = if the shape needs inner control (default false)
//    sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
// Usage: SlidingBoxLidWithLabelAndCustomShape(size=[100, 50], text_str = "Frog");
// Example:
//    SlidingBoxLidWithLabelAndCustomShape(size=[100, 50], text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module SlidingBoxLidWithLabelAndCustomShape(
  size,
  text_str,
  sliding_lid_options = undef,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  wall_thickness = default_wall_thickness,
  lid_rounding = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
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
  assert(text_str != undef, "Need to specify a label, text_str == undef");

  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  SlidingBoxLidWithCustomShape(
    size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing,
    material_colour=material_colour,
    lid_boundary=lid_boundary,
    layout_width=layout_width,
    aspect_ratio=aspect_ratio,
    lid_pattern_dense=lid_pattern_dense, lid_dense_shape_edges=lid_dense_shape_edges,
    pattern_inner_control=pattern_inner_control, sliding_lid_options=calc_sliding_lid_options
  ) {
    // 0 child is the pattern for the lid.
    children(0);

    translate([calc_wall_thickness / 2, calc_wall_thickness / 2, 0]) {
      MakeLidLabel(
        size=[width - calc_wall_thickness * 2, length - calc_wall_thickness * 2],
        lid_thickness=lid_thickness,
        text_str=text_str,
        options=object(
          calc_label_options,
          full_height=calc_sliding_lid_options.two_layer
        ),
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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
//    sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithLabel(
//        size = [100, 100], lid_thickness = 3, text_str = "Trains");
module SlidingBoxLidWithLabel(
  size,
  text_str,
  sliding_lid_options = undef,
  lid_thickness = default_lid_thickness,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = undef,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
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
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  assert(width > 0 && length > 0, str("Need width,lenght > 0 width=", width, " length=", length));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));
  assert(size_spacing > 0, str("Need size_spacing > 0, size_spacing=", size_spacing));
  assert(lid_rounding == undef || lid_rounding > 0, str("Need lid_rounding undef or > 0", lid_rounding));
  assert(text_str != undef, "Need to specify a label, text_str == undef");

  SlidingBoxLidWithLabelAndCustomShape(
    size=size, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    text_str=text_str,
    layout_width=layout_width, size_spacing=size_spacing,
    aspect_ratio=aspect_ratio, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
    label_options=calc_label_options,
    sliding_lid_options=calc_sliding_lid_options
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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    shape_options = options for the shape (default undef)
//    sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
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
  lid_rounding = undef,
  material_colour = default_material_colour,
  shape_options = undef,
  sliding_lid_options = undef,
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  assert(width > 0 && length > 0, str("Need width,lenght > 0 width=", width, " length=", length));
  assert(lid_thickness > 0, str("Need lid thickness > 0, lid_thickness=", lid_thickness));
  assert(wall_thickness > 0, str("Need wall thickness > 0, wall_thickness=", wall_thickness));
  assert(size_spacing > 0, str("Need size_spacing > 0, size_spacing=", size_spacing));
  assert(lid_rounding == undef || lid_rounding > 0, str("Need lid_rounding undef or > 0", lid_rounding));
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  SlidingBoxLidWithCustomShape(
    size=size, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    layout_width=layout_width, size_spacing=size_spacing,
    aspect_ratio=aspect_ratio, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    material_colour=material_colour,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
    sliding_lid_options=calc_sliding_lid_options
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
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    positive_only_children = the list of children to be positive only
//    positive_negative_children = the list of children to be positive and negative
//    positive_colour = colour of the postive pieces {{default_positive_colour}}
//    size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    spin = the spin to spin the box by (default 0)
//    anchor = the anchor to use (default BOTTOM + FRONT + LEFT)
//    orient = the orientation to use (default UP)
//    sliding_lid_options = the sliding lid options (default {{MakeSlidingLidOptions()})
// Topics: SlidingBox
// Example:
//   MakeBoxWithSlidingLid([50, 100, 20]);
// Example:
//   MakeBoxWithSlidingLid(size=[100, 100, 20], lid_thickness=3, wall_thickness = 2, sliding_lid_options=MakeSlidingLidOptions(two_layer=true));
// Example:
//   MakeBoxWithSlidingLid(size=[100, 100, 20], lid_thickness=3, wall_thickness = 2, 
//        sliding_lid_options=MakeSlidingLidOptions(two_layer=true, two_layer_vee_shape=true));
// Example:
//   MakeBoxWithSlidingLid(size=[100, 100, 20], lid_thickness=3, wall_thickness = 2, 
//        sliding_lid_options=MakeSlidingLidOptions(two_layer=true, two_layer_top_lid_ratio=0.25));
module MakeBoxWithSlidingLid(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  floor_thickness = default_floor_thickness,
  size_spacing = m_piece_wiggle_room,
  material_colour = default_material_colour,
  positive_colour = default_positive_colour,
  sliding_lid_options = undef,
  positive_only_children = [],
  positive_negative_children = [],
  spin = 0,
  anchor = BOTTOM + FRONT + LEFT,
  orient = UP
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  calc_sliding_lid_options = DefaultValue(sliding_lid_options, MakeSlidingLidOptions());

  calc_wall_thickness = DefaultValue(wall_thickness, default_wall_thickness);

  top_cover = calc_sliding_lid_options.two_layer_top_lid_ratio * lid_thickness;
  lid_cutout = calc_sliding_lid_options.two_layer ? lid_thickness - top_cover : lid_thickness;
  middle_chamfer = wall_thickness > lid_cutout ? lid_cutout / 2 : wall_thickness / 2;
  calc_height = calc_sliding_lid_options.two_layer ? height - top_cover - size_spacing : height;

  tmat = reorient(anchor=anchor, spin=spin, orient=orient, size=[width, length, calc_height]);
  multmatrix(m=tmat) left(width / 2)
      fwd(length / 2) down(height / 2)
          difference() {
            color(material_colour)
              diff()
                cuboid(
                  [width, length, calc_height], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
                  edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
                ) {
                  if (!calc_sliding_lid_options.two_layer) {
                    edge_mask(TOP) rounding_edge_mask(r=wall_thickness / 2, l=max(length, width));
                  }
                }
            rounding_offset = 0.01;

            // Lid top cutout for the middle.
            translate([wall_thickness, -rounding_offset, calc_height - lid_cutout]) color(material_colour) cuboid(
                  [
                    width - wall_thickness * 2,
                    length - wall_thickness + size_spacing + rounding_offset,
                    lid_cutout + size_spacing / 2,
                  ],
                  anchor=BOTTOM + FRONT + LEFT
                );

            // Lid cutout.
            if (calc_sliding_lid_options.two_layer) {
              if (calc_sliding_lid_options.two_layer_vee_shape) {
                translate([wall_thickness - middle_chamfer - size_spacing / 2, 0, calc_height - lid_cutout]) color(material_colour)
                    cuboid(
                      [width - wall_thickness * 2 + middle_chamfer * 2 + size_spacing, length - wall_thickness, lid_cutout],
                      anchor=BOTTOM + FRONT + LEFT,
                      chamfer=middle_chamfer,
                      edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + LEFT, BOTTOM + RIGHT]
                    );
              } else {
                chamfer = wall_thickness / 2 < lid_cutout ? wall_thickness / 2 : lid_cutout;
                translate([wall_thickness - chamfer - size_spacing / 2, 0, calc_height - lid_cutout]) color(material_colour)
                    cuboid(
                      [width - wall_thickness * 2 + chamfer * 2 + size_spacing, length - wall_thickness, lid_cutout],
                      anchor=BOTTOM + FRONT + LEFT,
                      chamfer=chamfer,
                      edges=[TOP + LEFT, TOP + RIGHT]
                    );
              }
            } else {
              chamfer = wall_thickness / 2 < lid_cutout ? wall_thickness / 2 : lid_cutout;
              translate([wall_thickness - chamfer, 0, calc_height - lid_cutout]) color(material_colour)
                  cuboid(
                    [width - wall_thickness * 2 + chamfer * 2, length - wall_thickness + chamfer, lid_cutout],
                    anchor=BOTTOM + FRONT + LEFT,
                    chamfer=chamfer,
                    edges=[TOP + LEFT, TOP + RIGHT, TOP + BACK]
                  );
            }

            translate([width / 2, 0, calc_height - lid_cutout])
              rotate([0, 90, 0])
                rounding_edge_mask(r=wall_thickness / 4, height=length - wall_thickness * 2);

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
