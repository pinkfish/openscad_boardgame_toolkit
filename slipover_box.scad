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

// LibFile: slipover_box.scad
//    This file has all the modules needed to generate a slipover box.

// FileSummary: Slipover box pieces for the slipover boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: SlipBox
// Description:
//    A box that slips over the outside of an inner box.

// Module: MakeBoxWithSlipoverLid()
// Topics: SlipoverBox
// Description:
//   Makes the inside of the slip box, this will take a second lid that slides over the outside of the box.
//   .
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Arguments:
//    size = [width, length, height] outside size of the box
//    foot = how big the foot should be around the bottom of the box (default 0)
//    size_spacing = amount of wiggle room to put into the model when making it (default {{m_piece_wiggle_room}})
//    wall_height = height of the wall if not set (default height - wall_thickness*2 - size_spacing*2)
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    positive_only_children = the list of children to be positive only
//    positive_negative_children = the list of children to be positive and negative
//    positive_colour = colour of the postive pieces {{default_positive_colour}}
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LONG}} - length catch, {{CATCH_SHORT}} - width catch (default
//       {{default_lid_catch_type}})
// Usage: MakeBoxWithSlipoverLid([100, 50, 10]);
// Example:
//   MakeBoxWithSlipoverLid([100, 50, 10]);
module MakeBoxWithSlipoverLid(
  size,
  wall_thickness = default_wall_thickness,
  foot = 0,
  size_spacing = m_piece_wiggle_room,
  wall_height = undef,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  positive_colour = default_positive_colour,
  positive_only_children = [],
  positive_negative_children = [],
  lid_catch = default_lid_catch_type
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width, length, height > 0 width=", width, " length=", length, " height=", height));

  wall_height_calc = wall_height == undef ? height - lid_thickness - size_spacing : wall_height;
  difference() {
    union() {
      translate([wall_thickness + size_spacing, wall_thickness + size_spacing, 0]) color(material_colour)
          diff() cuboid(
              [
                width - wall_thickness * 2 - size_spacing * 2,
                length - wall_thickness * 2 - size_spacing * 2,
                wall_height_calc,
              ],
              anchor=BOTTOM + FRONT + LEFT,
              rounding=wall_thickness,
              edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
            ) {
              edge_mask(TOP) rounding_edge_mask(r=wall_thickness / 4, l=max(length, width));
            }
      if (foot > 0) {
        color(material_colour)
          cuboid(
            [width, length, foot], anchor=BOTTOM + FRONT + LEFT, rounding=min(wall_thickness / 2, foot / 2),
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
          );
      }
    }

    if ( (lid_catch == CATCH_SHORT && width < length) || (lid_catch == CATCH_LONG && width > length) || lid_catch == CATCH_ALL) {
      catch_width = width - wall_thickness * 2;
      translate([(catch_width * 2 / 8) + wall_thickness, wall_thickness, foot]) color(material_colour)
          wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]);
      translate([(catch_width * 6 / 8) + wall_thickness, length - wall_thickness, foot]) rotate(180)
          color(material_colour) wedge([catch_width * 2 / 4, lid_thickness, lid_thickness]);
    }
    if ( (lid_catch == CATCH_SHORT && length < width) || (lid_catch == CATCH_LONG && length < width) || lid_catch == CATCH_ALL) {
      catch_length = length - wall_thickness * 2;
      translate([width - wall_thickness, catch_length * 2 / 8 + wall_thickness, foot]) rotate(90)
          color(material_colour) wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]);
      translate([wall_thickness, catch_length * 6 / 8 + wall_thickness, foot]) rotate(270)
          color(material_colour) wedge([catch_length * 2 / 4, lid_thickness, lid_thickness]);
    }
    if ( (lid_catch == CATCH_BUMPS_SHORT && width < length) || (lid_catch == CATCH_BUMPS_LONG && width > length)) {
      catch_offset = width - wall_thickness * 2;
      translate([(catch_offset * 6 / 8) + wall_thickness, wall_thickness, wall_thickness + foot]) {
        color(material_colour) {
          intersection() {
            sphere(r=wall_thickness * 5 / 6 + size_spacing);
            cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=FRONT);
          }
        }
        color(material_colour) translate([0, length - wall_thickness * 2, 0]) {
            intersection() {
              sphere(r=wall_thickness * 5 / 6 + size_spacing);
              cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=BACK);
            }
          }
      }
      translate([(catch_offset * 2 / 8) + wall_thickness, wall_thickness, wall_thickness + foot]) {
        color(material_colour) {
          intersection() {
            sphere(r=wall_thickness * 5 / 6 + size_spacing);
            cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=FRONT);
          }
        }
        color(material_colour) translate([0, length - wall_thickness * 2, 0]) {
            intersection() {
              sphere(r=wall_thickness * 5 / 6 + size_spacing);
              cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=BACK);
            }
          }
      }
    }
    if ( (lid_catch == CATCH_BUMPS_SHORT && length <= width) || (lid_catch == CATCH_BUMPS_LONG && length > width)) {
      catch_offset = length - wall_thickness * 2;
      translate([wall_thickness, (catch_offset * 6 / 8) + wall_thickness, wall_thickness + foot]) {
        color(material_colour) {
          intersection() {
            sphere(r=wall_thickness * 5 / 6 + size_spacing);
            cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=LEFT);
          }
        }
        color(material_colour) translate([width - wall_thickness * 2, 0, 0]) {
            intersection() {
              sphere(r=wall_thickness * 5 / 6 + m_piece_wiggle_room);
              cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=RIGHT);
            }
          }
      }
      translate([wall_thickness, (catch_offset * 2 / 8) + wall_thickness, wall_thickness + foot]) {
        color(material_colour) {
          intersection() {
            sphere(r=wall_thickness * 5 / 6 + size_spacing);
            cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=LEFT);
          }
        }
        color(material_colour) translate([width - wall_thickness * 2, 0, 0]) {
            intersection() {
              sphere(r=wall_thickness * 5 / 6 + size_spacing);
              cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=RIGHT);
            }
          }
      }
    }

    $inner_width = width - wall_thickness * 4;
    $inner_length = length - wall_thickness * 4;
    $inner_height = wall_height_calc - default_floor_thickness;
    for (i = [0:$children - 1]) {
      if (!in_list(i, positive_only_children)) {
        translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children(i);
      }
    }
  }
  if (len(positive_only_children) > 0 || (len(positive_negative_children) > 0 && MAKE_MMU == 1)) {
    $inner_width = width - wall_thickness * 4;
    $inner_length = length - wall_thickness * 4;
    $inner_height = wall_height_calc - default_floor_thickness;
    for (i = positive_only_children) {
      color(positive_colour)
        translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children(i);
    }
    for (i = positive_negative_children) {
      color(positive_colour)
        translate([wall_thickness * 2, wall_thickness * 2, floor_thickness]) children(i);
    }
  }
}

// Module: SlipoverBoxLid()
// Topics: SlipoverBox
// Description:
//   Make a box with a slip lid, a lid that slips over the outside of a box.
// Arguments:
//   size = [width, length, height] outside size of the lid
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   finger_hole_length = finger hole on the length side (default6 false)
//   finger_hole_width = finger hole on the width side (default true)
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
//   lid_rounding = how much to round the lid (default wall_thickness)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LONG}} - length catch, {{CATCH_SHORT}} - width catch (default
//       {{default_lid_catch_type}})
// Usage: SlipoverBoxLid([100, 50, 10]);
// Example:
//   SlipoverBoxLid([100, 50, 10]);
module SlipoverBoxLid(
  size,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  size_spacing = m_piece_wiggle_room,
  foot = 0,
  finger_hole_length = false,
  finger_hole_width = true,
  lid_rounding = undef,
  material_colour = default_material_colour,
  lid_catch = default_lid_catch_type
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  assert(width > 0 && length > 0 && height > 0, str("Need width, length, height > 0 width=", width, " length=", length, " height=", height));

  foot_offset = foot > 0 ? foot + size_spacing : 0;
  calc_lid_rounding = DefaultValue(lid_rounding, wall_thickness / 2);
  translate([0, length, height - foot]) rotate([180, 0, 0]) {
      union() {
        translate([0, 0, height - foot_offset - lid_thickness]) {
          internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
            // Top piece
            color(material_colour) translate([wall_thickness * 5 / 6, wall_thickness * 5 / 6, 0]) cuboid(
                  [width - wall_thickness * 10 / 6, length - wall_thickness * 10 / 6, lid_thickness], anchor=BOTTOM + FRONT + LEFT,
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
        finger_height = min(20, (height - foot_offset - lid_thickness) / 2);
        difference() {
          color(material_colour) diff() cuboid(
                [width, length, height - foot_offset],
                anchor=BOTTOM + FRONT + LEFT,
                rounding=calc_lid_rounding,
                edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP]
              ) {
                edge_mask(BOT) rounding_edge_mask(r=max(calc_lid_rounding / 4, 0.5), l=max(width, length));
              }
          translate([wall_thickness, wall_thickness, height - foot_offset - lid_thickness - 0.01]) color(material_colour)
              cuboid(
                [width - wall_thickness * 2, length - wall_thickness * 2, foot_offset + 1],
                anchor=BOTTOM + FRONT + LEFT,
              );
          translate([wall_thickness, wall_thickness, -1 - lid_thickness]) color(material_colour)
              cuboid(
                [width - wall_thickness * 2, length - wall_thickness * 2, height - foot_offset + 1],
                anchor=BOTTOM + FRONT + LEFT,
                rounding=calc_lid_rounding / 2,
                edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP]
              );
          if (finger_hole_length) {
            translate([width / 2, wall_thickness / 2 - 0.01, finger_height - 0.01]) mirror([0, 0, 1]) color(material_colour)
                  FingerHoleWall(radius=max(finger_height, 7), height=finger_height, depth_of_hole=wall_thickness + 0.02, rounding_edge=wall_thickness / 4);
            translate([width / 2, length - wall_thickness / 2 + 0.01, finger_height - 0.01]) mirror([0, 0, 1])
                color(material_colour) FingerHoleWall(radius=max(finger_height, 7), height=finger_height, depth_of_hole=wall_thickness + 0.02, rounding_edge=wall_thickness / 4);
          }
          if (finger_hole_width) {
            echo([object(radius=max(finger_height, 7), height=finger_height, depth_of_hole=wall_thickness + 0.04, rounding_edge=wall_thickness / 4)]);
            translate([wall_thickness / 2 + 0.015, length / 2, finger_height - 0.01]) mirror([0, 0, 1]) rotate([0, 0, 90])
                  color(material_colour) FingerHoleWall(radius=max(finger_height, 7), height=finger_height, depth_of_hole=wall_thickness + 0.04, rounding_edge=wall_thickness / 4);
            translate([width - wall_thickness / 2 - 0.015, length / 2, finger_height - 0.01]) mirror([0, 0, 1]) rotate([0, 0, 90])
                  color(material_colour) FingerHoleWall(radius=max(finger_height, 7), height=finger_height, depth_of_hole=wall_thickness + 0.04, rounding_edge=wall_thickness / 4);
          }
        }

        // lid catch
        if ( (lid_catch == CATCH_SHORT && width < length) || (lid_catch == CATCH_LONG && width > length) || lid_catch == CATCH_ALL) {
          catch_width = width - wall_thickness * 2;
          translate([(catch_width * 2 / 8) + size_spacing + wall_thickness, wall_thickness, 0]) {
            color(material_colour) rotate([0, 0, 0]) wedge(
                  [
                    catch_width * 2 / 4 - size_spacing * 2,
                    lid_thickness - size_spacing,
                    lid_thickness - size_spacing,
                  ]
                );
          }
          translate([(catch_width * 6 / 8) + size_spacing + wall_thickness, length - wall_thickness, 0]) {
            rotate(180) rotate([0, 0, 0]) color(material_colour) wedge(
                    [
                      catch_width * 2 / 4 - size_spacing * 2,
                      lid_thickness - size_spacing,
                      lid_thickness - size_spacing,
                    ]
                  );
          }
        }
        if ( (lid_catch == CATCH_SHORT && length < width) || (lid_catch == CATCH_LONG && length < width) || lid_catch == CATCH_ALL) {
          catch_length = length - wall_thickness * 2;
          translate([width - wall_thickness, catch_length * 2 / 8 + size_sizeing + wall_thickness, 0]) {
            rotate(90) color(material_colour) wedge(
                  [
                    catch_length * 2 / 4 - size_spacing * 2,
                    lid_thickness - size_spacing,
                    lid_thickness - size_spacing,
                  ]
                );
          }
          translate([wall_thickness, catch_length * 6 / 8 + size_spacing + wall_thickness, 0]) {
            rotate(270) color(material_colour) wedge(
                  [
                    catch_length * 2 / 4 - size_spacing * 2,
                    lid_thickness - size_spacing,
                    lid_thickness - size_spacing,
                  ]
                );
          }
        }
        if ( (lid_catch == CATCH_BUMPS_SHORT && width <= length) || (lid_catch == CATCH_BUMPS_LONG && width > length)) {
          catch_offset = width - wall_thickness * 2;
          translate([(catch_offset * 6 / 8) + wall_thickness, wall_thickness * 5 / 8, wall_thickness]) {
            color(material_colour) {
              intersection() {
                sphere(r=wall_thickness * 4 / 6);
                cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=FRONT);
              }
            }
            color(material_colour) translate([0, length - wall_thickness * 10 / 8, 0]) {
                intersection() {
                  sphere(r=wall_thickness * 4 / 6);
                  cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=BACK);
                }
              }
          }
          translate([(catch_offset * 2 / 8) + wall_thickness, wall_thickness * 5 / 8, wall_thickness]) {
            color(material_colour) {
              intersection() {
                sphere(r=wall_thickness * 4 / 6);
                cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=FRONT);
              }
            }
            color(material_colour) translate([0, length - wall_thickness * 10 / 8, 0]) {
                intersection() {
                  sphere(r=wall_thickness * 4 / 6);
                  cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=BACK);
                }
              }
          }
        }
        if ( (lid_catch == CATCH_BUMPS_SHORT && length < width) || (lid_catch == CATCH_BUMPS_LONG && length > width)) {
          catch_offset = length - wall_thickness * 2;
          translate([wall_thickness * 5 / 8, (catch_offset * 6 / 8) + wall_thickness, wall_thickness]) {
            color(material_colour) {
              intersection() {
                sphere(r=wall_thickness * 4 / 6);
                cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=LEFT);
              }
            }
            color(material_colour) translate([width - wall_thickness * 10 / 8, 0, 0]) {
                intersection() {
                  sphere(r=wall_thickness * 4 / 6);
                  cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=RIGHT);
                }
              }
          }
          translate([wall_thickness * 5 / 8, (catch_offset * 2 / 8) + wall_thickness, wall_thickness]) {
            color(material_colour) {
              intersection() {
                sphere(r=wall_thickness * 4 / 6);
                cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=LEFT);
              }
            }
            color(material_colour) translate([width - wall_thickness * 10 / 8, 0, 0]) {
                intersection() {
                  sphere(r=wall_thickness * 4 / 6);
                  cuboid([wall_thickness * 6 / 4, wall_thickness * 6 / 4, wall_thickness * 6 / 4], anchor=RIGHT);
                }
              }
          }
        }
      }
    }
}

// Module: SlipoverBoxLidWithLabelAndCustomShape()
// Topics: SlipoverBox
// Description:
//    Lid for a slipover box.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    size = [width, length, height] outside size of the lid
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    text_str = the string to use for the label
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = extra spacing to apply between pieces (default {{m_piece_wiggle_room}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    finger_hole_length = finger hole on the length side (default6 false)
//    finger_hole_width = finger hole on the width side (default true)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_SHORT}} - length catch, {{CATCH_LONG}} - width catch (default
//       {{default_lid_catch_type}})
//    pattern_inner_control = if the pattern needs inner control (default false)
//    label_options = options for the label (default undef)
//    foot = size of the foot on the box.
//    lid_thickness = thickness of the lid
//    wall_thickness = thickness of the walls
// Usage: SlipoverBoxLidWithLabelAndCustomShape(size=[100, 50, 20], text_str = "Frog");
// Example:
//    SlipoverBoxLidWithLabelAndCustomShape([100, 50, 20], text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module SlipoverBoxLidWithLabelAndCustomShape(
  size,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  wall_thickness = default_wall_thickness,
  foot = 0,
  finger_hole_length = false,
  finger_hole_width = true,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  material_colour = default_material_colour,
  lid_catch = default_lid_catch_type,
  pattern_inner_control,
  label_options = undef
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );

  assert(size[0] > 0 && size[1] > 0 && size[2] > 0, str("Need width, length, height > 0 width=", size[0], " length=", size[1], " height=", size[2]));
  assert(text_str != undef, "text_str must not be undefined");

  SlipoverBoxLid(
    size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
    lid_rounding=lid_rounding, size_spacing=size_spacing, foot=foot,
    finger_hole_length=finger_hole_length, finger_hole_width=finger_hole_width,
    material_colour=material_colour, lid_catch=lid_catch
  ) {
    LidMeshBasic(
      size=[size[0], size[1]], lid_thickness=lid_thickness, boundary=lid_boundary,
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
      size=[size[0], size[1]],
      lid_thickness=lid_thickness,
      options=object(calc_label_options, full_height=true), text_str=text_str
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

// Module: SlipoverBoxLidWithLabel()
// Topics: SlipoverBox
// Arguments:
//    size = [width, length, height] outside size of the lid
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//    foot = size of the foot on the box.
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    finger_hole_length = finger hole on the length side (default6 false)
//    finger_hole_width = finger hole on the width side (default true)
//    lid_rounding = how much to round the lid (default wall_thickness)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    lid_catch = {{CATCH_NONE}} - no catch, {{CATCH_LONG}} - length catch, {{CATCH_SHORT}} - width catch (default {{default_lid_catch_type}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
// Usage: SlipoverBoxLidWithLabel(size=[20, 100, 10], text_str = "Marmoset", shape_options=MakeShapeObject(shape_type = SHAPE_TYPE_CIRCLE, shape_width = 14), layout_width = 10) 
// Example:
//    SlipoverBoxLidWithLabel(size=[20, 100, 10], text_str = "Marmoset",
//        shape_options=MakeShapeObject(shape_type = SHAPE_TYPE_CIRCLE, shape_width = 14), layout_width = 10);
module SlipoverBoxLidWithLabel(
  size,
  text_str,
  lid_boundary = 10,
  wall_thickness = default_wall_thickness,
  foot = 0,
  layout_width = undef,
  aspect_ratio = 1.0,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  finger_hole_length = false,
  finger_hole_width = true,
  lid_rounding = undef,
  material_colour = default_material_colour,
  lid_catch = default_lid_catch_type,
  label_options = undef,
  shape_options = undef
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
    )
  );
  calc_shape_options = DefaultValue(
    shape_options, MakeShapeObject(
    )
  );

  assert(width > 0 && length > 0 && height > 0, str("Need width, length, height > 0 width=", width, " length=", length, " height=", height));
  assert(text_str != undef, "text_str must not be undefined");
  SlipoverBoxLidWithLabelAndCustomShape(
    size=size, wall_thickness=wall_thickness, lid_thickness=lid_thickness,
    text_str=text_str,
    layout_width=layout_width,
    size_spacing=size_spacing, aspect_ratio=aspect_ratio, lid_rounding=lid_rounding,
    lid_boundary=lid_boundary,
    finger_hole_length=finger_hole_length, finger_hole_width=finger_hole_width, foot=foot,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    material_colour=material_colour,
    lid_catch=lid_catch,
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
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
