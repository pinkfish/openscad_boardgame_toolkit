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

// LibFile: filament_hinge_box.scad
//    This file has all the modules needed to generate a filament hinge box.

// FileSummary: Filament hinge box pieces for the hinge boxes.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Function: HingeOptions()
// Description:
//    Returns the object containing the hinge options.
// Topics: Hinges, FilamentHingeBox
// Arguments:
//    thickness = thickness of the hinge
//    hole_diameter = diameter of the hinge hole (default=6)
function HingeOptions(
  thickness = default_hinge_thickness,
  hole_diameter = default_hinge_hole_diameter,
  num_segments = undef,
  pin_slop = default_hinge_pin_slop
) =
  object(
    thickness=thickness,
    hole_diameter=hole_diameter,
    num_segments=num_segments,
    pin_slop=pin_slop
  );

// Module: MakeBoxWithFilamentHinge()
// Description:
//   Makes a box with a filament hinge on the top.  The hole for the filement is
//   specified as a an argument to the system.
// Usage: MakeBoxWithFilamentHinge(size=[100, 50, 20]);
// Topics: Hinges, FilamentHingeBox
// Arguments:
//   size = outside size of the box [width, length, height]
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   filament_thickness = the thickness of the filement in hinger (default 2.2)
// Examples:
//   MakeBoxWithFilamentHinge(size=[100, 50, 20]);
module MakeBoxWithFilamentHingeLid(
  size,
  wall_thickness = default_wall_thickness,
  floor_thickness = default_floor_thickness,
  lid_thickness = default_lid_thickness,
  material_colour = default_material_colour,
  filament_thickness = 2.2,
  hinge_options = undef,
  print_in_place_offset = default_print_in_place_offset
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];

  edge_length = length * 1 / 6;
  catch_length = min(wall_thickness * 6, length / 6);
  catch_height = min(wall_thickness * 4, height / 6);

  calc_hinge_options = DefaultValue(hinge_options, HingeOptions());
  hinge_seg = calc_hinge_options.num_segments != undef ? calc_hinge_options.num_segments : max(floor(length / 20), 5);
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
              [calc_hinge_options.thickness * 1.25 + print_in_place_offset, length, wall_thickness + print_in_place_offset],
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
            offset=calc_hinge_options.thickness,
            knuckle_diam=calc_hinge_options.thickness,
            arm_height=0,
            arm_angle=90,
            clear_top=false,
            inner=true,
            spin=90,
            pin_diam=calc_hinge_options.hole_diameter + calc_hinge_options.pin_slop,
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
// Topics: Boxes, FilamentHinges
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
  hinge_options = undef,
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];
  calc_hinge_options = DefaultValue(hinge_options, HingeOptions());
  support_width = calc_hinge_options.thickness * 1.25 - wall_thickness;
  support_height = support_width + calc_hinge_options.thickness;

  difference() {
    color(material_colour)
      cuboid(
        [width - wall_thickness * 2, length - wall_thickness * 2, height - floor_thickness],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=rounding,
        edges=[BOTTOM, LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
      );

    translate([-0.5, -0.5, height - lid_thickness - support_height - floor_thickness])
      color(material_colour) cuboid(
          [support_width + print_in_place_offset + 0.5, length + 1, support_height + 1],
          anchor=BOTTOM + FRONT + LEFT,
          chamfer=support_width,
          edges=[BOTTOM + RIGHT],
        );
    fwd(0.5)
      up(height)
        color(material_colour)
          ycyl(d=calc_hinge_options.thickness + print_in_place_offset, length=length + 1, anchor=FRONT + LEFT + TOP);
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
  hinge_options = undef,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
) {
  edge_length = size[1] * 1 / 6;
  catch_length = min(wall_thickness * 6, size[1] / 6);
  catch_height = min(wall_thickness * 4, size[0] / 6);
  width = size[0];
  length = size[1];
  height = size[2];

  calc_hinge_options = DefaultValue(hinge_options, HingeOptions());
  hinge_seg = calc_hinge_options.num_segments != undef ? calc_hinge_options.num_segments : max(floor(length / 20), 5);
  lip_height = min(wall_thickness * 2 + print_in_place_offset * 2, height - lid_thickness - floor_thickness);
  lip_length = max(length / 4, 15);

  difference() {
    union() {
      internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
        // Top piece
        right(wall_thickness * 2.5)
          color(material_colour)
            cuboid(
              [size[0] - wall_thickness * 2.5, size[1], lid_thickness],
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
              offset=calc_hinge_options.thickness,
              knuckle_diam=calc_hinge_options.thickness,
              pin_diam=calc_hinge_options.hole_diameter + calc_hinge_options.pin_slop,
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
            ycyl(h=length + 1, d=calc_hinge_options.hole_diameter + print_in_place_offset, anchor=FRONT);
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
//   hinge_options = options for the hinge
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
  hinge_options = undef,
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
    hinge_options=hinge_options,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing
  ) {
    LidMeshBasic(
      size=[
        size[0],
        size[1],
      ], lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width,
      aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
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
//   hinge_options = options for the hinge
//   print_in_place_offset = offset for print in place mechanisms
//   size_spacing = wiggle room for size
//   lid_pattern_dense = boolean if the pattern is dense
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
  hinge_options = undef,
  print_in_place_offset = default_print_in_place_offset,
  size_spacing = m_piece_wiggle_room,
  lid_boundary = 10,
  layout_width = undef,
  aspect_ratio = 1.0,
  shape_options = undef,
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
    hinge_options=hinge_options,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    aspect_ratio=aspect_ratio,
    layout_width=layout_width,
    shape_options=shape_options
  ) {
    if ($children > 0) {
      children(0);
    } else {
      color(material_colour) square([10, 10]);
    }
    translate([size[0] - lid_boundary, lid_boundary, lid_thickness])
      xflip()
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
//   hinge_options = options for the hinge
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
  hinge_options = undef,
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
    hinge_options=hinge_options,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    aspect_ratio=aspect_ratio,
    layout_width=layout_width,
    shape_options=shape_options
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
//   hinge_options = options for the hinge
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
  hinge_options = undef,
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
    hinge_options=hinge_options,
    print_in_place_offset=print_in_place_offset,
    size_spacing=size_spacing,
    lid_boundary=lid_boundary,
    aspect_ratio=aspect_ratio,
    layout_width=layout_width,
    shape_options=calc_shape_options
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
