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

// LibFile: slipover_path_box.scad
//    This file has all the modules needed to generate a slipover box
//    using a polygon for the outside.

// FileSummary: Slipover box pieces for the slipover boxes with polygon outline.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Module: FingerHoleWallSegmentCutout()
// Description:
//    Makes a single segment for use in the capbox wall.  It will make the rounded
//    finger holes on the side of the capbox at the correct direction and length.
// Arguments:
//    path = the path to generate for (this should be one line segment)
//    radius = the radius of the rounding on the fingerhole
//    height = the height of the fingerhole
//    depth = the thickness of the walls
//.   finger_catch = the type of catch to use and where to put them
// Example:
//    FingerHoleWallSegmentCutout([[0,0], [50,50]], radius=5, height=7, depth=6, finger_catch=CATCH_ALL);
module FingerHoleWallSegmentCutout(path, height, radius, depth, finger_catch) {
  assert(is_path(path), "\nInvalid path in MakePathBoxWithCapLid.");
  split_length = path_length(path);
  normal = path_normals(path);
  vec_m = abs(path[0][0] - path[1][0]) / abs(path[0][1] - path[1][1]);
  if (
    finger_catch == CATCH_ALL || (finger_catch == CATCH_LENGTH && vec_m > 1000000) || (finger_catch == CATCH_WIDTH && vec_m < 0.01)
  ) {
    if (split_length > radius * 3) {
      pts = path_cut_points(
        path=path,
        cutdist=[split_length / 2]
      );
      translate([0, 0, height - 0.01])
        translate(pts[0][0])
          rotate([0, 180, 90])
            rotate(atan(normal[0][1] / normal[0][0]))
              FingerHoleWall(radius=radius, height=height, depth_of_hole=depth);
    }
  }
}

// Module: MakePathBoxWithSlipoverLid()
// Topics: SlipoverBox
// Description:
//   Makes the inside of the slip box, this will take a second lid that slides over the outside of the box.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Usage: MakePathBoxWithSlipoverLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10);
// Arguments:
//    path = the path for the bottom of the box
//    height = outside height of the box
//    foot = how big the foot should be around the bottom of the box (default 0)
//    size_spacing = amount of wiggle room to put into the model when making it (default {{m_piece_wiggle_room}})
//    wall_height = height of the wall if not set (default height - wall_thickness*2 - size_spacing*2)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    last_child_postitive = if the last child in the list should be a postive, not negative
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LENGTH}} - length catch, {{CATCH_WIDTH}} - width catch (default
//       {{CATCH_LENGTH}})
// Example:
//   MakePathBoxWithSlipoverLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10);
module MakePathBoxWithSlipoverLid(
  path,
  height,
  wall_thickness = default_wall_thickness,
  foot = 0,
  size_spacing = m_piece_wiggle_room,
  wall_height = undef,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  last_child_positive = false,
  lid_catch = CATCH_LENGTH
) {
  wall_height_calc = wall_height == undef ? height - lid_thickness - size_spacing : wall_height;
  inner_path = offset(path, r=-wall_thickness - size_spacing);
  calc_inner_path = round_corners(inner_path, radius=wall_thickness / 2);
  calc_path = round_corners(path, radius=wall_thickness);

  x_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][0]];
  y_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][1]];

  calc_width = max(x_arr) - min(x_arr);
  calc_length = max(y_arr) - min(y_arr);

  difference() {
    union() {
      color(material_colour)
        linear_extrude(height=height - lid_thickness - size_spacing) polygon(calc_inner_path);

       if (foot > 0) {
        color(material_colour)
          linear_extrude(height=foot) diff() polygon(calc_path);
        ;
      }
    }

    // Catches
    translate([0, 0, foot]) {
      for (i = [0:1:len(calc_inner_path) - 2]) {
        PolygonBoxLidCatch(
          path=[calc_inner_path[i], calc_inner_path[i + 1]],
          wall_thickness=wall_thickness,
          delta=size_spacing,
          offset=0,
          lid_catch=lid_catch
        );
      }
      PolygonBoxLidCatch(
        path=[calc_inner_path[len(calc_inner_path) - 1], calc_inner_path[0]],
        wall_thickness=wall_thickness,
        delta=size_spacing,
        offset=0,
        lid_catch=lid_catch
      );
    }

    $inner_width = calc_width;
    $inner_length = calc_length;
    $inner_height = height - lid_thickness - floor_thickness;
    if (last_child_positive) {
      translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children([0:$children - 2]);
    } else {
      translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children();
    }
  }
  if (last_child_positive) {
    $inner_width = calc_width;
    $inner_length = calc_length;
    $inner_height = height - lid_thickness - floor_thickness;
    translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children($children - 1);
  }
}

// Module: SlipoverPathBoxLid()
// Topics: SlipoverBox
// Description:
//   Make a box with a slip lid, a lid that slips over the outside of a box.
// Usage: SlipoverPathBoxLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10);
// Arguments:
//   path = the path of the box (outside width)
//   height = height of the lid (outside height)
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   finger_catch = where to put the catches (default {{CATCH_WIDTH}})
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
//   lid_rounding = how much to round the lid (default wall_thickness)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LENGTH}} - length catch, {{CATCH_WIDTH}} - width catch (default
//       {{CATCH_LENGTH}})
// Example:
//   SlipoverPathBoxLid(path=[[0,0], [0,100], [50,100], [50,0]], height=10);
module SlipoverPathBoxLid(
  path,
  height,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  foot = 0,
  finger_catch = CATCH_WIDTH,
  lid_rounding = undef,
  material_colour = default_material_colour,
  lid_catch = CATCH_LENGTH
) {
  foot_offset = foot > 0 ? foot + size_spacing : 0;
  calc_lid_rounding = DefaultValue(lid_rounding, wall_thickness);

  inner_path = offset(path, r=-wall_thickness + size_spacing);
  calc_inner_path = round_corners(inner_path, radius=wall_thickness / 2);
  calc_path = round_corners(path, radius=calc_lid_rounding);

  x_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][0]];
  y_arr = [for (x = [0:len(inner_path) - 1]) inner_path[x][1]];

  calc_width = max(x_arr) - min(x_arr);
  calc_length = max(y_arr) - min(y_arr);

  translate([0, calc_length, height - foot]) rotate([180, 0, 0]) {
      union() {
        translate([0, 0, height - foot_offset - lid_thickness]) {
          internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
            // Top piece
            difference() {
              color(material_colour)
                linear_extrude(lid_thickness) polygon(calc_path);
              difference() {
                color(material_colour)
                  linear_extrude(lid_thickness) polygon(calc_path);
                color(material_colour) offset_sweep(calc_path, height=lid_thickness, top=os_smooth(joint=lid_thickness / 2));
              }
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
        finger_height = min(20, (height - foot_offset - lid_thickness) / 2);
        difference() {
          union() {
            difference() {
              color(material_colour)
                linear_extrude(height - foot_offset - lid_thickness / 2) polygon(calc_path);
              translate([0, 0, -0.5])
                color(material_colour) linear_extrude(height + 1) polygon(calc_inner_path);
            }

            // lid catch
            for (i = [0:1:len(calc_inner_path) - 2]) {
              color(material_colour)
                PolygonBoxLidCatch(
                  path=[calc_inner_path[i], calc_inner_path[i + 1]],
                  wall_thickness=wall_thickness,
                  delta=0,
                  offset=0,
                  lid_catch=lid_catch
                );
            }
            color(material_colour)
              PolygonBoxLidCatch(
                path=[calc_inner_path[len(calc_inner_path) - 1], calc_inner_path[0]],
                wall_thickness=wall_thickness,
                delta=0,
                offset=0,
                lid_catch=lid_catch
              );
          }

          for (i = [0:1:len(calc_inner_path) - 2]) {
            color(material_colour)
              FingerHoleWallSegmentCutout(
                path=[calc_inner_path[i], calc_inner_path[i + 1]],
                depth=wall_thickness * 5,
                height=finger_height,
                radius=max(finger_height, 7),
                finger_catch=finger_catch
              );
          }
          color(material_colour)
            FingerHoleWallSegmentCutout(
              path=[calc_inner_path[len(calc_inner_path) - 1], calc_inner_path[0]],
              depth=wall_thickness * 5,
              height=finger_height,
              radius=max(finger_height, 7),
              finger_catch=finger_catch
            );
        }
      }
    }
}

// Module: SlipoverPathBoxLidWithLabelAndCustomShape()
// Topics: SlipoverBox
// Description:
//    Lid for a slipover box.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    width = outside width of the box
//    length = outside length of the box
//    lid_boundary = boundary around the outside for the lid (default 10)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    size_sizeing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    text_str = the string to use for the label
//    text_length = the length of the text to use (defaults to 3/4 of length/width)
//    text_scale = the scale of the text, making it higher or shorter on the width (default 1.0)
//    label_radius = radius of the label corners (default text_width/4)
//    label_type = the type of the label (default {{default_label_type}})
//    label_border = border of the item (default 2)
//    label_offset = offset in from the edge for the label (default 4)
//    label_width_offset = the width to move the label by (default 0})
//    label_length_offset = the length to move the label by (default 0)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    shape_width = width of the shape (default {{default_lid_shape_width}})
//    shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LENGTH}} - length catch, {{CATCH_WIDTH}} - width catch (default
//       {{CATCH_LENGTH}})
// Usage: SlipoverPathBoxLidWithLabelAndCustomShape(100, 50, 20, text_str = "Frog");
// Example:
//   long_player_box_width = 136.5;
//   long_player_box_length = 305;
//   long_player_box_height = 18.5;
//   long_player_box_gap = 60;
//   long_player_box_upgrade_buffer= 5;
//   upgrade_width = 86;
//   SlipoverPathBoxLidWithLabelAndCustomShape(
//    [
//      [0, 0],
//      [0, long_player_box_length],
//      [long_player_box_width, long_player_box_length],
//      [long_player_box_width, long_player_box_length - 2 * 2 - upgrade_width - long_player_box_upgrade_buffer],
//      [long_player_box_width - long_player_box_gap, long_player_box_length - 2 * 2 - upgrade_width - long_player_box_upgrade_buffer],
//      [long_player_box_width - long_player_box_gap, 0],
//    ],
//    height=long_player_box_height,
//    material_colour="orange",
//    foot=2,
//    text_str="frog",
//    text_length=50,
//    text_scale=0.5,
//    label_width_offset=-28
//    ) {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//    }
module SlipoverPathBoxLidWithLabelAndCustomShape(
  path,
  height,
  text_str,
  text_length = undef,
  text_scale = 1.0,
  label_type = default_label_type,
  lid_boundary = 10,
  label_radius = undef,
  label_border = 2,
  label_offset = 4,
  layout_width = undef,
  label_type = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  label_width_offset = 0,
  label_length_offset = 0,
  aspect_ratio = 1.0,
  font = undef,
  lid_rounding = undef,
  wall_thickness = default_wall_thickness,
  foot = 0,
  finger_catch = CATCH_WIDTH,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  label_colour = undef,
  material_colour = default_material_colour,
  label_background_colour = undef,
  lid_catch = CATCH_LENGTH,
  pattern_inner_control
) {
  calc_path = round_corners(path, radius=wall_thickness, $fn=16);

  x_arr = [for (x = [0:len(path) - 1]) path[x][0]];
  y_arr = [for (x = [0:len(path) - 1]) path[x][1]];

  calc_width = max(x_arr) - min(x_arr);
  calc_length = max(y_arr) - min(y_arr);

  SlipoverPathBoxLid(
    path, height, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, foot=foot,
    finger_catch=finger_catch,
    material_colour=material_colour, lid_catch=lid_catch
  ) {
    LidMeshBasic(
      path=path, lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
      dense_shape_edges=lid_dense_shape_edges, inner_control=pattern_inner_control,
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
        lid_thickness=lid_thickness, border=label_border, offset=label_offset, full_height=true,
        font=font, text_length=text_length, text_scale=text_scale, text_str=text_str,
        label_radius=label_radius,
        material_colour=material_colour, label_colour=label_colour,
        label_background_colour=label_background_colour,
        label_type=label_type,
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

// Module: SlipoverPathBoxLidWithLabel()
// Topics: SlipoverBox
// Usage: SlipoverPathBoxLidWithLabel(20, 100, 10, text_str = "Marmoset", shape_type = SHAPE_TYPE_CIRCLE, layout_width = 10, shape_width = 14) 
// Arguments:
//   width = width of the lid (outside width)
//   length = of the lid (outside length)
//   height = height of the lid (outside height)
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
//   text_str = the string to use for the label
//   text_length = the length of the text to use (defaults to 3/4 of length/width)
//   text_scale = the scale of the text, making it higher or shorter on the width (default 1.0)
//   label_radius = radius of the label corners (default text_width/4)
//   label_type = the type of the label (default {{default_label_type}})
//   label_width_offset = the width to move the label by (default 0})
//   label_length_offset = the length to move the label by (default 0)
//   border= border of the item (default 2)
//   offset = offset in from the edge for the label (default 4)
//   layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//   shape_width = width of the shape (default {{default_lid_shape_width}})
//   shape_thickness = how wide the pieces are (default {{default_lid_shape_thickness}})
//   aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   label_background_colour = the colour of the label background (default {{default_label_background_colour}})
//   lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LENGTH}} - length catch, {{CATCH_WIDTH}} - width catch (default
//       {{CATCH_LENGTH}})
// Example:
//   long_player_box_width = 136.5;
//   long_player_box_length = 305;
//   long_player_box_height = 18.5;
//   long_player_box_gap = 60;
//   long_player_box_upgrade_buffer= 5;
//   upgrade_width = 86;
//   SlipoverPathBoxLidWithLabel(
//    [
//      [0, 0],
//      [0, long_player_box_length],
//      [long_player_box_width, long_player_box_length],
//      [long_player_box_width, long_player_box_length - 2 * 2 - upgrade_width - long_player_box_upgrade_buffer],
//      [long_player_box_width - long_player_box_gap, long_player_box_length - 2 * 2 - upgrade_width - long_player_box_upgrade_buffer],
//      [long_player_box_width - long_player_box_gap, 0],
//    ],
//    height=long_player_box_height,
//    material_colour="orange",
//    foot=2,
//    text_str="frog",
//    text_length=50,
//    text_scale=0.5,
//    label_width_offset=-28
//    );
module SlipoverPathBoxLidWithLabel(
  path,
  height,
  text_str,
  text_length = undef,
  text_scale = 1.0,
  label_type = default_label_type,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  label_radius = undef,
  label_border = 2,
  label_offset = 4,
  label_width_offset = 0,
  label_length_offset = 0,
  label_type = undef,
  foot = 0,
  layout_width = undef,
  shape_width = undef,
  shape_type = undef,
  shape_thickness = undef,
  aspect_ratio = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  font = undef,
  lid_rounding = undef,
  shape_rounding = default_lid_shape_rounding,
  label_colour = undef,
  material_colour = default_material_colour,
  label_background_colour = undef,
  lid_catch = CATCH_LENGTH,
) {
  SlipoverPathBoxLidWithLabelAndCustomShape(
    path=path, height=height, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    font=font, text_str=text_str,
    label_radius=label_radius, text_length=text_length, text_scale=text_scale, layout_width=layout_width,
    size_spacing=size_spacing, aspect_ratio=aspect_ratio, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary, label_border=label_border, label_offset=label_offset,
    foot=foot,
    lid_pattern_dense=IsDenseShapeType(shape_type), lid_dense_shape_edges=DenseShapeEdges(shape_type),
    material_colour=material_colour,
    label_background_colour=label_background_colour, lid_catch=lid_catch,
    pattern_inner_control=ShapeNeedsInnerControl(shape_type), label_type=label_type,
    label_width_offset=label_width_offset,
    label_length_offset=label_length_offset
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
