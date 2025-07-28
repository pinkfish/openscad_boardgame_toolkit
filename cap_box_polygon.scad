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

// LibFile: cap_box_polygon.scad
//    This file has all the modules needed to generate a cap box
//    using a polygon for the outside.

// FileSummary: Cap box pieces for the cap boxes with polygon outline.
// FileGroup: Boxes

module SegmentCutout(path, radius, height, wall_thickness) {
  split_length = path_length(path);
  normal = path_normals(path);
  calc_len = split_length / 5;
  if (split_length > radius * 2) {
    if (calc_len * 3 < radius * 2) {
      pts = path_cut_points(
        path=path,
        cutdist=[split_length / 2]
      );
      translate(pts[0][0])
        rotate(atan(normal[0][1] / normal[0][0]))
          xcyl(h=wall_thickness * 2, r=radius);
    } else {
      pts = path_cut_points(
        path=path,
        cutdist=[calc_len + wall_thickness, calc_len + radius, calc_len * 4 - radius, calc_len * 4 - wall_thickness]
      );
      hull() {
        translate([0, 0, height - radius]) {
          translate(pts[1][0])
            rotate(atan(normal[0][1] / normal[0][0]))
              xcyl(h=wall_thickness * 2, r=radius);
          translate(pts[2][0])
            rotate(atan(normal[0][1] / normal[0][0]))
              xcyl(h=wall_thickness * 2, r=radius);
        }
        translate([0, 0, radius - height]) {
          translate(pts[0][0])
            rotate(atan(normal[0][1] / normal[0][0]))
              cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2]);
          translate(pts[3][0])
            rotate(atan(normal[0][1] / normal[0][0]))
              cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2]);
        }
      }
    }
  }
}

module PolygonBoxLidCatch(path, wall_thickness, radius, delta) {
  split_length = path_length(path);
  normal = path_normals(path);
  calc_len = split_length / 5;

  if (calc_len * 4 - radius - wall_thickness - (calc_len + wall_thickness + radius) > 5) {
    pts = path_cut_points(
      path=path,
      cutdist=[calc_len + wall_thickness + radius, calc_len * 4 - radius - wall_thickness]
    );

    path_sweep([[-delta, -delta], [-wall_thickness - delta, -delta], [-delta, wall_thickness + delta]], [pts[0][0], pts[1][0]]);
  }
}

// Module: MakePolygonBoxWithCapLid()
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
module MakePathBoxWithCapLid(
  path,
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
  assert(is_path(path), "\nInvalid path in MakePathBoxWithCapLid.");
  calc_lid_wall_thickness =
    lid_wall_thickness == undef ? CapBoxDefaultLidWallThickness(wall_thickness) : lid_wall_thickness;
  calc_floor_thickness = floor_thickness == undef ? wall_thickness : floor_thickness;
  calc_cap_height = cap_height == undef ? CapBoxDefaultCapHeight(height) : cap_height;
  calc_finger_hold_height = finger_hold_height == undef ? CapBoxDefaultFingerHoldHeight(height) : finger_hold_height;
  calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height);
  calc_path = round_corners(path, radius=wall_thickness);
  echo([calc_cap_height]);
  // translate([-size_spacing, -size_spacing, 0]) 

  difference() {
    color(material_colour)
      linear_extrude(height=height) polygon(calc_path);

    // lid diff.
    translate([0, 0, height - calc_cap_height]) difference() {
        difference() {
          color(material_colour)
            linear_extrude(height=height) offset(size_spacing) polygon(calc_path);
          color(material_colour)
            translate([0, 0, -0.5])
              linear_extrude(height + 1) offset(-calc_lid_wall_thickness - size_spacing) polygon(calc_path);
        }
      }

    // Finger cutouts.
    translate([0, 0, height - calc_cap_height - calc_finger_hold_height]) difference() {
        // Remove the edge around the outside where the finger bits go.
        difference() {
          color(material_colour)
            linear_extrude(height=height) offset(size_spacing) polygon(calc_path);
          color(material_colour)
            linear_extrude(height=height) offset(-calc_lid_wall_thickness - size_spacing) polygon(calc_path);
        }

        // Finger hole bits.
        for (i = [0:1:len(calc_path) - 2]) {
          segment = [calc_path[i], calc_path[i + 1]];
          SegmentCutout(
            path=[calc_path[i], calc_path[i + 1]],
            height=calc_finger_hold_height, radius=calc_finger_hole_rounding,
            wall_thickness=wall_thickness
          );
        }
        SegmentCutout(
          path=[calc_path[len(calc_path) - 1], calc_path[0]],
          height=calc_finger_hold_height, radius=calc_finger_hole_rounding,
          wall_thickness=wall_thickness
        );
      }

    translate([0, 0, height - calc_cap_height]) {
      for (i = [0:1:len(calc_path) - 2]) {
        PolygonBoxLidCatch(
          path=[calc_path[i], calc_path[i + 1]],
          radius=calc_finger_hole_rounding,
          wall_thickness=wall_thickness,
          delta=size_spacing
        );
      }
      PolygonBoxLidCatch(
        path=[calc_path[len(calc_path) - 1], calc_path[0]],
        radius=calc_finger_hole_rounding,
        wall_thickness=wall_thickness,
        delta=size_spacing
      );
    }

    // Put the children in the box.
    if ($children > 0) {
      $inner_height = height - lid_thickness - floor_thickness;
      $inner_path = calc_path;
      if (last_child_positive) {
        translate([wall_thickness, wall_thickness, calc_floor_thickness]) children([0:$children - 2]);
      } else {
        translate([wall_thickness, wall_thickness, calc_floor_thickness]) children([0:$children - 1]);
      }
    }
  }
  if (last_child_positive) {
    $inner_height = height - lid_thickness - floor_thickness;
    $inner_path = calc_path;
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
module CapBoxPathLid(
  path,
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
  calc_path = round_corners(path, radius=wall_thickness, $fn=16);
  calc_finger_hole_rounding = CapBoxDefaultLidFingerHoldRounding(calc_cap_height);

  y_arr = [for (x = [0:len(path) - 1]) path[x][1]];

  calc_length = max(y_arr) - min(y_arr);

  translate([0, calc_length, calc_cap_height])
    rotate([180, 0, 0]) {
      union() {
        translate([0, 0, calc_cap_height - lid_thickness]) {
          internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
            difference() {
              // Top piece
              color(material_colour) offset_sweep(calc_path, height=lid_thickness, top=os_smooth(joint=wall_thickness));
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
        }
        difference() {
          color(material_colour) offset_sweep(calc_path, height=calc_cap_height, top=os_smooth(joint=wall_thickness));
          translate([0, 0, -0.5])
            color(material_colour) linear_extrude(height=calc_cap_height + 1) offset(-wall_thickness / 2 + size_spacing) polygon(calc_path);
        }

        // lid catches
        for (i = [0:1:len(calc_path) - 2]) {
          color(material_colour)
            PolygonBoxLidCatch(
              path=[calc_path[i], calc_path[i + 1]],
              radius=calc_finger_hole_rounding,
              wall_thickness=wall_thickness,
              delta=0
            );
        }
        color(material_colour)
          PolygonBoxLidCatch(
            path=[calc_path[len(calc_path) - 1], calc_path[0]],
            radius=calc_finger_hole_rounding,
            wall_thickness=wall_thickness,
            delta=0
          );
      }
    }
}

// Module: CapBoxPathLidWithLabelAndCustomShape()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    psth = the path for the outside of the box
//    height = outside height of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    text_str = the string to use for the label
//    text_length = the length of the text to use (defaults to 3/4 of length/width)
//    text_scale = the scale of the text, making it higher or shorter on the width (default 1.0)
//    label_radius = radius of the label corners (default text_width/4)
//    label_type = the type of the label (default {{default_label_type}})
//    label_border= border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    label_colour = the color of the label (default undef)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//    inner_control = if the shape needs inner control (default false)
//    finger_hole_size = size of the finger hole to use in the lid (default 10)
// Usage: CapBoxPathLidWithLabelAndCustomShape(100, 50, text_str = "Frog");
// Example:
//    CapBoxPathLidWithLabelAndCustomShape(100, 50, 30, text_str = "Frog") {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module CapBoxPathLidWithLabelAndCustomShape(
  path,
  height,
  text_length,
  text_str,
  text_scale = 1.0,
  label_type = undef,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  label_radius = undef,
  label_border = 2,
  label_offset = 4,
  label_width_offset = 0,
  label_length_offset = 0,
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
  label_background_colour = undef,
  pattern_inner_control = false,
  finger_hole_size = undef
) {
  calc_path = round_corners(path, radius=wall_thickness, $fn=16);

  x_arr = [for (x = [0:len(path) - 1]) path[x][0]];
  y_arr = [for (x = [0:len(path) - 1]) path[x][1]];

  calc_width = max(x_arr) - min(x_arr);
  calc_length = max(y_arr) - min(y_arr);

  CapBoxPathLid(
    path=path, height=height, cap_height=cap_height, wall_thickness=wall_thickness,
    lid_thickness=lid_thickness, lid_wall_thickness=lid_wall_thickness,
    size_spacing=m_piece_wiggle_room, lid_rounding=lid_rounding, lid_inner_rounding=lid_inner_rounding,
    material_colour=material_colour
  ) {
    LidMeshBasic(
      path=path, lid_thickness=lid_thickness, boundary=lid_boundary,
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
    translate([label_width_offset, label_length_offset, 0])
      MakeLidLabel(
        length=calc_length, width=calc_width,
        text_length=text_length, text_scale=text_scale,
        lid_thickness=lid_thickness, border=label_border, offset=label_offset, full_height=true,
        font=font, label_type=label_type, text_str=text_str, label_radius=label_radius,
        label_colour=label_colour, material_colour=material_colour,
        label_background_colour=label_background_colour,
        finger_hole_size=finger_hole_size
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

// Module: CapBoxPathLidWithLabel()
// Topics: CapBox
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.
// Arguments:
//    path = the path dor the outside ot the box
//    height = outside height of the box
//    text_str = the string to use for the label
//    text_length = the length of the text to use (defaults to 3/4 of length/width)
//    text_scale = the scale of the text, making it higher or shorter on the width (default 1.0)
//    label_radius = radius of the label corners (default text_width/4)
//    label_type = the type of the label (default {{default_label_type}})
//    lid_boundary = boundary around the outside for the lid (default 10)
//    cap_height = height of the cap on the box (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_wall_thickness = the thickess of the walls in the lid (default wall_thickness / 2)
//    finger_hold_height = how heigh the finger hold bit it is (default 5)
//    border= border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    label_colour = the color of the label (default undef)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//    finger_hole_size = size of the finger hole to use in the lid (default 10)
// Usage: CapBoxPathLidWithLabel(100, 50, text_str = "Frog");
// Example:
//    CapBoxPathLidWithLabel(100, 50, 30, text_str = "Frog");
// Example:
//    CapBoxPathLidWithLabel(100, 50, 30, text_str = "Frog");
// Example:
//    CapBoxPathLidWithLabel(100, 50, 30, text_str = "Frog", material_colour =
//    "lightblue", label_colour = "black");
// Example:
//    default_lid_shape_type = SHAPE_TYPE_CIRCLE;
//    default_lid_shape_thickness = 1;
//    default_lid_shape_width = 13;
//    default_lid_layout_width = 10;
//    CapBoxPathLidWithLabel(120, 70, 30, text_str = "Cards");
module CapBoxPathLidWithLabel(
  path,
  height,
  text_str,
  text_length = undef,
  text_scale = 1.0,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  label_radius = undef,
  label_border = 2,
  label_offset = 4,
  label_width_offset = 0,
  label_length_offset = 0,
  label_type = undef,
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
  label_background_colour = undef,
  finger_hole_size = undef
) {
  CapBoxPathLidWithLabelAndCustomShape(
    path=path, height=height, cap_height=cap_height, wall_thickness=wall_thickness,
    lid_thickness=lid_thickness, lid_wall_thickness=lid_wall_thickness, font=font, text_str=text_str,
    text_length=text_length, text_scale=text_scale, label_type=label_type, label_radius=label_radius,
    layout_width=layout_width, size_spacing=size_spacing, aspect_ratio=aspect_ratio,
    label_border=label_border, label_offset=label_offset, lid_rounding=undef, lid_inner_rounding=undef,
    lid_pattern_dense=IsDenseShapeType(shape_type), lid_dense_shape_edges=DenseShapeEdges(shape_type),
    material_colour=material_colour, label_colour=label_colour,
    label_background_colour=label_background_colour, pattern_inner_control=ShapeNeedsInnerControl(shape_type),
    finger_hole_size=finger_hole_size,
    label_width_offset=label_width_offset,
    label_length_offset=label_length_offset,
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
