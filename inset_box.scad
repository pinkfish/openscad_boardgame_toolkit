/*
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

// LibFile: inset_box.scad
//    This file has all the modules needed to generate an inset box.
//

// FileSummary: Various modules to generate board game inserts.
// FileGroup: Boxes

// Includes:
//   include <boardgame_toolkit.scad>

// Section: TabbedBox
// Description:
//   Creates a lid/box with tabs on the side.  This also includes inset lids, since they are used with tabs too.

// Module: InsetLid()
// Description:
//   Make a lid inset into the box with tabs on the side to close the box.  This just does the insets around the
//   top.
// Usage:
//   InsetLid(50, 100);
// Arguments:
//   size = [width, length] outside size of the lid
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   inset = how far the side is inset from the edge of the box (default 1)
//   lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//   size_spacing = how much wiggle room to give in the model (default {{m_piece_wiggle_room}})
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
// Topics: TabbedBox
// Example:
//  InsetLid([50, 100]);
module InsetLid(
  size,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  inset = 1,
  size_spacing = m_piece_wiggle_room,
  lid_rounding = undef,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_lid_rounding = lid_rounding == undef ? wall_thickness / 2 : lid_rounding;
  $inner_width = width - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2;
  $inner_length = length - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2;
  internal_build_lid(lid_thickness=lid_thickness, size_spacing=size_spacing) {
    translate([wall_thickness - inset + m_piece_wiggle_room, wall_thickness - inset + m_piece_wiggle_room, 0])
      color(material_colour) cuboid(
          [$inner_width, $inner_length, lid_thickness],
          anchor=BOTTOM + FRONT + LEFT, rounding=calc_lid_rounding,
          edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK]
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

// Module: InsetLidTabbed()
// Description:
//   Makes an inset lid with the tabes on the side.
// Usage:
//   InsetLidTabbed([30, 100]);
// Arguments:
//   size = [width, length] outside size of the lid
//   lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//   wall_thickness = thickness of the walls (default {{default_wall_thickness}})
//   inset = how far to inset the lid (default 1)
//   size_spacing = the wiggle room in the lid generation (default {{m_piece_wiggle_room}})
//   make_tab_width = makes tabes on thr width (default false)
//   make_tab_length = makes tabs on the length (default true)
//   prism_width = width of the prism in the tab. (default 0.75)
//   tab_length = length of the tab (default 10)
//   tab_height = height of the tab (default 6)
//   lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
// Topics: TabbedBox, TabbedLid
// Example:
//   InsetLidTabbed([30, 100]);
module InsetLidTabbed(
  size,
  lid_thickness = default_lid_thickness,
  wall_thickness = default_wall_thickness,
  inset = 1,
  size_spacing = m_piece_wiggle_room,
  make_tab_width = false,
  make_tab_length = true,
  prism_width = 0.75,
  tab_length = 10,
  tab_height = 8,
  lid_rounding = undef,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  translate([0, length, lid_thickness]) rotate([180, 0, 0]) union() {
        InsetLid(
          size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
          inset=inset, size_spacing=size_spacing, lid_rounding=lid_rounding, material_colour=material_colour
        ) {
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
        color(material_colour) MakeTabs(
            size=[width, length], lid_thickness=lid_thickness,
            make_tab_width=make_tab_width, make_tab_length=make_tab_length
          )
            MakeLidTab(
              length=tab_length, height=tab_height, lid_thickness=lid_thickness,
              prism_width=prism_width, wall_thickness=wall_thickness
            );
      }
}

// Module: InsetLidTabbedWithLabelAndCustomShape()
// Topics: TabbedBox, TabbedLid
// Description:
//    Lid for a cap box, small cap to go on the box with finger cutouts.  This uses the first
//    child as the shape for repeating on the lid.
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    tab_length = length of the tabs (default 10)
//    tab_height = height of the tabs (default 6)
//    make_tab_width = makes tabes on thr width (default false)
//    make_tab_length = makes tabs on the length (default true)
//    prism_width = width of the prism in the tab. (default 0.75)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    pattern_inner_control = if the pattern needs inner control (default false)
// Usage: InsetLidTabbedWithLabelAndCustomShape(size=[100, 50], text_str = "Frog");
// Example:
//    InsetLidTabbedWithLabelAndCustomShape(size=[100, 50], text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module InsetLidTabbedWithLabelAndCustomShape(
  size,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  tab_length = 10,
  tab_height = 8,
  make_tab_width = false,
  make_tab_length = true,
  prism_width = 0.75,
  material_colour = default_material_colour,
  label_options = undef,
  lid_pattern_dense = false,
  lid_dense_shape_edges = false,
  pattern_inner_control = false,
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
      full_height=true
    )
  );

  InsetLidTabbed(
    size=size, lid_thickness=lid_thickness, tab_length=tab_length, tab_height=tab_height,
    lid_rounding=lid_rounding, prism_width=prism_width, make_tab_length=make_tab_length,
    make_tab_width=make_tab_width, size_spacing=size_spacing, material_colour=material_colour
  ) {
    LidMeshBasic(
      size=size, lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, inner_control=pattern_inner_control,
      dense=lid_pattern_dense, dense_shape_edges=lid_dense_shape_edges,
    ) {
      if ($children > 0) {
        children(0);
      } else {
        color(material_colour) square([10, 10]);
      }
    }
    MakeLidLabel(
      size=[width, length],
      options=object(calc_label_options, full_height=true),
      lid_thickness=lid_thickness,
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

// Module: InsetLidTabbedWithLabel()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed lid with
//   a label and a hex grid. The children to this as also pulled out of the lid so can be used to
//   build more complicated lids.
// Usage:
//    InsetLidTabbedWithLabel(size = [100, 100], lid_thickness = 3, text_str = "Trains");
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = The string to write
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    tab_length = length of the tabs (default 10)
//    tab_height = height of the tabs (default 8)
//    make_tab_width = makes tabes on thr width (default false)
//    make_tab_length = makes tabs on the length (default true)
//    prism_width = width of the prism in the tab. (default 0.75)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    size_spacing = how much wiggle room around the piece (default {{m_piece_wiggle_room}})
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
// Topics: TabbedBox, TabbedLid
// Example:
//    InsetLidTabbedWithLabel(
//        size = [100, 100], lid_thickness = 3, text_str = "Trains");
module InsetLidTabbedWithLabel(
  size,
  text_str,
  lid_thickness = default_lid_thickness,
  lid_boundary = 10,
  tab_length = 10,
  tab_height = 8,
  make_tab_width = false,
  make_tab_length = true,
  prism_width = 0.75,
  layout_width = undef,
  aspect_ratio = undef,
  lid_rounding = undef,
  size_spacing = m_piece_wiggle_room,
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

  InsetLidTabbedWithLabelAndCustomShape(
    size=size, lid_thickness=lid_thickness, tab_length=tab_length,
    prism_width=prism_width, tab_height=tab_height, make_tab_width=make_tab_width,
    make_tab_length=make_tab_length, text_str=text_str,
    layout_width=layout_width, size_spacing=size_spacing, aspect_ratio=aspect_ratio,
    material_colour=material_colour,
    lid_rounding=lid_rounding,
    label_options=calc_label_options,
    lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
    lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
    pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
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

// Module: MakeBoxWithInsetLidTabbed()
// Description:
//   Makes a box with an inset lid.  Handles all the various pieces for making this with tabs.  This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.  The children and moves so 0,0,0 is the bottom inside
//   of the box to make for easier arithmatic.  Inside the children of the box you can use the
//    $inner_height , $inner_width, $inner_length = length variables to
//    deal with the box sizes.
// Usage:
//   MakeBoxWithInsetLidTabbed(size = [30, 100, 20]);
// Arguments:
//   size = [width, length, height] outside size of the box
//   wall_thickness = how thick the walls are (default {{default_wall_thickness}})
//   lid_thickness = how hight the lid is (default {{default_lid_thickness}})
//   tab_height = how heigh to make the tabs (default 6)
//   inset = how far to inset the lid (default 1)
//   make_tab_width = make the tabs on the width (default false)
//   make_tab_length = make the tabs on the length (default true)
//   prism_width = width of the prism to generate (default 0.75)
//   tab_length = how long the tab is (default 10)
//   stackable = should we pull a piece out the bottom of the box to let this stack (default false)
//   size_spacing = wiggle room to use when generatiung box (default {{m_piece_wiggle_room}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   tab_offset = offset for the tab cutout (default 0.45)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
//   positive_only_children = the list of children to be positive only
//   positive_negative_children = the list of children to be positive and negative
//   positive_colour = colour of the postive pieces {{default_positive_colour}}
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeBoxWithInsetLidTabbed(size = [30, 100, 20]);
module MakeBoxWithInsetLidTabbed(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  tab_height = 8,
  inset = 1,
  make_tab_width = false,
  make_tab_length = true,
  prism_width = 0.75,
  tab_length = 10,
  stackable = false,
  size_spacing = m_piece_wiggle_room,
  floor_thickness = default_floor_thickness,
  tab_offset = 0.45,
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
      cuboid(
        [width, length, height], anchor=BOTTOM + FRONT + LEFT, rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
      );
    translate([wall_thickness - inset, wall_thickness - inset, height - lid_thickness]) color(material_colour)
        cube([width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1]);
    translate([0, 0, height - lid_thickness]) color(material_colour)
        MakeTabs(
          size=[width, length], lid_thickness=lid_thickness, tab_length=tab_length,
          make_tab_length=make_tab_length, make_tab_width=make_tab_width
        ) color(material_colour)
            minkowski() {
              translate([-tab_offset, -tab_offset, -tab_offset]) color(material_colour) cube(tab_offset * 2);
              MakeLidTab(
                length=tab_length, height=tab_height, lid_thickness=lid_thickness,
                prism_width=prism_width, wall_thickness=wall_thickness
              );
            }

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    for (i = [0:$children - 1]) {
      if (!in_list(i, positive_only_children)) {
        translate([wall_thickness, wall_thickness, floor_thickness]) children();
      }
    }

    // Cuff off the bit on the bottom to allow for stacking.
    if (stackable) {
      difference() {
        translate([-0.5, -0.5, -0.5]) color(material_colour)
            cube([width + 1, length + 1, wall_thickness + 0.5 - size_spacing]);
        translate([wall_thickness - inset + size_spacing, wall_thickness - inset + size_spacing, -1])
          color(material_colour) cube(
              [
                width - (wall_thickness - inset + size_spacing) * 2,
                length - (wall_thickness - inset + size_spacing) * 2,
                wall_thickness + 2,
              ]
            );
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

// Module: InsetLidRabbitClip()
// Description:
//   Makes an inset lid with the tabes on the side.
// Arguments:
//   size = [width, length] outside size of the lid
//   lid_thickness = height of the lid (default 2)
//   wall_thickness = thickness of the walls (default 2)
//   inset = how far to inset the lid (default 1)
//   size_spacing = the wiggle room in the lid generation (default {{m_piece_wiggle_room}})
//   make_rabbit_width = makes tabes on thr width (default false)
//   make_rabbit_length = makes tabs on the length (default true)
//   rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//   rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//   rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//   rabbit_compression = how much sideway give on the rabbit (default 0.1)
//   rabbit_thickness = thickness of the rabbit (default 0.8)
//   rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//   rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//   rabbit_depth = extrustion depth of the rabbit (default 1.5)
//   lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
// Topics: RabbitClipBox
// Usage: InsetLidRabbitClip(size=[30, 100]);
// Example:
//   InsetLidRabbitClip(size=[30, 100]);
module InsetLidRabbitClip(
  size,
  lid_thickness = 2,
  wall_thickness = 2,
  inset = 1,
  size_spacing = m_piece_wiggle_room,
  make_rabbit_width = false,
  make_rabbit_length = true,
  rabbit_width = 7,
  rabbit_length = 6,
  rabbit_lock = false,
  rabbit_compression = 0.1,
  rabbit_thickness = 0.8,
  rabbit_snap = 0.25,
  rabbit_offset = 3,
  rabbit_depth = 1.5,
  lid_rounding = undef,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  translate([0, length, lid_thickness]) rotate([180, 0, 0]) union() {
        InsetLid(
          size=size, lid_thickness=lid_thickness, wall_thickness=wall_thickness,
          inset=inset, size_spacing=size_spacing, lid_rounding=lid_rounding,
          material_colour=material_colour
        ) {
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
        color(material_colour) MakeTabs(
            size=[width, length], lid_thickness=lid_thickness,
            make_tab_width=make_rabbit_width, make_tab_length=make_rabbit_length
          )
            translate([(rabbit_length + rabbit_offset) / 2, wall_thickness / 2, -lid_thickness / 2])
              cuboid([rabbit_length + rabbit_offset, wall_thickness, lid_thickness]) attach(TOP)
                  rabbit_clip(
                    type="pin", length=rabbit_length, width=rabbit_width, snap=rabbit_snap,
                    thickness=rabbit_thickness, depth=rabbit_depth, compression=rabbit_compression,
                    lock=rabbit_lock
                  );
      }
}

// Module: InsetLidRabbitClipWithLabelAndCustomShape()
// Topics: RabbitClipBox
// Description:
//    Lid for an inset lid with a rabbit clip.  This handles the first child as the pattern for the
//    lid and the following items as children to the lid itself.
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = the string to use for the label
//    lid_boundary = boundary around the outside for the lid (default 10)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    size_spacing = amount of wiggle room between pieces (default {{m_piece_wiggle_room}})
//    lid_thickness = thickness of the lid (default {{default_lid_thickness}})
//    aspect_ratio = the aspect ratio (multiple by dy) (default {{default_lid_aspect_ratio}})
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    make_rabbit_width = makes tabes on thr width (default false)
//    make_rabbit_length = makes tabs on the length (default true)
//    rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//    rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//    rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//    rabbit_compression = how much sideway give on the rabbit (default 0.1)
//    rabbit_thickness = thickness of the rabbit (default 0.8)
//    rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//    rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//    rabbit_depth = extrustion depth of the rabbit (default 1.5)
//    pattern_inner_control = if the pattern needs inner control (default false)
//    lid_pattern_dense = if the layout is dense (default false)
//    lid_dense_shape_edges = the number of edges on the dense layout (default 6)
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
// Usage: InsetLidRabbitClipWithLabelAndCustomShape(size=[100, 50], text_str = "Frog");
// Example:
//    InsetLidRabbitClipWithLabelAndCustomShape(size=[100, 50], text_str = "Frog") {
//      ShapeByType(MakeShapeObject(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//         supershape_n1 = 1, supershape_b = 1.5, shape_width = 15));
//    }
module InsetLidRabbitClipWithLabelAndCustomShape(
  size,
  text_str,
  lid_boundary = 10,
  layout_width = undef,
  size_spacing = m_piece_wiggle_room,
  lid_thickness = default_lid_thickness,
  aspect_ratio = 1.0,
  lid_rounding = undef,
  make_rabbit_width = false,
  make_rabbit_length = true,
  rabbit_width = 7,
  rabbit_length = 6,
  rabbit_lock = false,
  rabbit_compression = 0.1,
  rabbit_thickness = 0.8,
  rabbit_snap = 0.25,
  rabbit_offset = 3,
  rabbit_depth = 1.5,
  pattern_inner_control = false,
  lid_pattern_dense = false,
  lid_dense_shape_edges = 6,
  material_colour = default_material_colour,
  label_options = undef
) {
  assert(size != undef && is_list(size) && (len(size) == 2 || len(size) == 3), str("size must be set to [x,y]", size));
  width = size[0];
  length = size[1];

  calc_label_options = DefaultValue(
    label_options, MakeLabelOptions(
      material_colour=material_colour,
      full_height=true
    )
  );

  InsetLidRabbitClip(
    size=size, lid_thickness=lid_thickness, make_rabbit_length=make_rabbit_length,
    make_rabbit_width=make_rabbit_width, rabbit_width=rabbit_width,
    rabbit_length=rabbit_length, rabbit_lock=rabbit_lock, rabbit_offset=rabbit_offset,
    rabbit_thickness=rabbit_thickness, rabbit_compression=rabbit_compression,
    rabbit_depth=rabbit_depth, lid_rounding=lid_rounding, size_spacing=size_spacing,
    material_colour=material_colour
  ) {
    LidMeshBasic(
      size=size, lid_thickness=lid_thickness, boundary=lid_boundary,
      layout_width=layout_width, aspect_ratio=aspect_ratio, dense=lid_pattern_dense,
      dense_shape_edges=lid_dense_shape_edges,
      inner_control=pattern_inner_control
    ) {
      if ($children > 0) {
        children(0);
      } else {
        color(material_colour) square([10, 10]);
      }
    }
    MakeLidLabel(
      size=[width, length],
      options=object(calc_label_options, full_height=true),
      lid_thickness=lid_thickness, text_str=text_str,
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

// Module: InsetLidRabbitClipWithLabel()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed lid with
//   a label and a hex grid. The children to this as also pulled out of the lid so can be used to
//   build more complicated lids.
// Usage:
//    InsetLidRabbitClipWithLabel(size = [100, 100], lid_thickness = 3, text_str = "Trains");
// Arguments:
//    size = [width, length] outside size of the lid
//    text_str = The string to write
//    lid_thickness = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    make_rabbit_width = makes tabes on thr width (default false)
//    make_rabbit_length = makes tabs on the length (default true)
//    aspect_ratio = the aspect ratio (multiple by dy) (default 1.0)
//    rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//    rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//    rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//    rabbit_compression = how much sideway give on the rabbit (default 0.1)
//    rabbit_thickness = thickness of the rabbit (default 0.8)
//    rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//    rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//    layout_width = the width of the layout pieces (default {{default_lid_layout_width}})
//    rabbit_depth = extrustion depth of the rabbit (default 1.5)
//    lid_rounding = how much rounding on the edge of the lid (default wall_thickness/2)
//    size_spacing = how much wiggle room around the piece (default {{m_piece_wiggle_room}})
//    material_colour = the colour of the material in the box (default {{default_material_colour}})
//    label_options = options for the label (default undef)
//    shape_options = options for the shape (default undef)
// Topics: RabbitClipBox
// Example:
//    InsetLidRabbitClipWithLabel(
//        size = [100, 100], lid_thickness = 3, text_str = "Trains");
module InsetLidRabbitClipWithLabel(
  size,
  text_str,
  lid_thickness = 3,
  lid_boundary = 10,
  make_rabbit_width = false,
  make_rabbit_length = true,
  aspect_ratio = 1.0,
  rabbit_width = 7,
  rabbit_length = 6,
  rabbit_lock = false,
  rabbit_compression = 0.1,
  rabbit_thickness = 0.8,
  rabbit_snap = 0.25,
  rabbit_offset = 3,
  layout_width = undef,
  rabbit_depth = 1.5,
  lid_rounding = undef,
  size_spacing = m_piece_wiggle_room,
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

  InsetLidRabbitClipWithLabelAndCustomShape(
    size=size, lid_thickness=lid_thickness, make_rabbit_length=make_rabbit_length,
    make_rabbit_width=make_rabbit_width, rabbit_width=rabbit_width, rabbit_length=rabbit_length,
    rabbit_lock=rabbit_lock, rabbit_offset=rabbit_offset, rabbit_thickness=rabbit_thickness,
    rabbit_compression=rabbit_compression, rabbit_depth=rabbit_depth, lid_rounding=lid_rounding,
    text_str=text_str,
    layout_width=layout_width, size_spacing=size_spacing,
    aspect_ratio=aspect_ratio,
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
      children(5);
    }
  }
}

// Module: MakeBoxWithInsetLidRabbitClip()
// Description:
//   Makes a box with an inset lid.  Handles all the various pieces for making this with rabbit clips.
//   The children are moved so 0,0,0 is the bottom inside of the box to make for easier arithmatic.
//   Inside the children of the box you can use the
//   $inner_height , $inner_width, $inner_length = length variables to
//   deal with the box sizes.
// Usage:
//   MakeBoxWithInsetLidRabbitClip(width = 30, length = 100, height = 20);
// Arguments:
//   wall_thickness = how thick the walls are (default {{default_wall_thickness}})
//   lid_thickness = how hight the lid is (default {{default_lid_thickness}})
//   tab_height = how heigh to make the tabs (default 6)
//   inset = how far to inset the lid (default 1)
//   make_rabbit_width = makes tabes on thr width (default false)
//   make_rabbit_length = makes tabs on the length (default true)
//   rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//   rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//   rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//   rabbit_compression = how much sideway give on the rabbit (default 0.1)
//   rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//   rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//   rabbit_depth = extrustion depth of the rabbit (default 1.5)
//   size_spacing = wiggle room to use when generatiung box (default {{m_piece_wiggle_room}})
//   floor_thickness = thickness of the floor (default {{default_floor_thickness}})
//   positive_only_children = the list of children to be positive only
//   positive_negative_children = the list of children to be positive and negative
//   positive_colour = colour of the postive pieces {{default_positive_colour}}
//   size = the size of the object [width, length, height]
//   rabbit_thickness = thickness of the rabbit edge
//   material_colour = the colour of the material in the box (default {{default_material_colour}})
// Topics: RabbitClipBox
// Example:
//   MakeBoxWithInsetLidRabbitClip(size = [30, 100, 20]);
module MakeBoxWithInsetLidRabbitClip(
  size,
  wall_thickness = default_wall_thickness,
  lid_thickness = default_lid_thickness,
  tab_height = 8,
  floor_thickness = default_floor_thickness,
  inset = 1,
  make_rabbit_width = false,
  make_rabbit_length = true,
  rabbit_width = 6,
  rabbit_length = 7,
  rabbit_offset = 3,
  rabbit_lock = false,
  rabbit_compression = 0.1,
  rabbit_thickness = 0.8,
  rabbit_snap = 0.25,
  size_spacing = m_piece_wiggle_room,
  rabbit_depth = 1.5,
  positive_only_children = [],
  positive_negative_children = [],
  positive_colour = default_positive_colour,
  material_colour = default_material_colour
) {
  assert(size != undef && is_list(size) && len(size) == 3, str("size must be set to [x,y,z]", size));
  width = size[0];
  length = size[1];
  height = size[2];

  difference() {
    color(material_colour) cuboid(
        [width, length, height - lid_thickness - size_spacing], anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness, edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT]
      );
    translate([wall_thickness - inset, wall_thickness - inset, height - lid_thickness]) color(material_colour)
        cube([width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1]);
    translate([0, 0, height - lid_thickness]) color(material_colour)
        MakeTabs(
          size=[width, length], lid_thickness=lid_thickness,
          tab_length=rabbit_length + rabbit_offset, make_tab_length=make_rabbit_length,
          make_tab_width=make_rabbit_width
        ) union() {
            translate(
              [
                (rabbit_length + rabbit_offset + size_spacing * 2) / 2,
                wall_thickness / 2 - 0.01,
                -lid_thickness / 2,
              ]
            ) color(material_colour)
                cuboid(
                  [rabbit_length + rabbit_offset + size_spacing * 2, wall_thickness + 0.01, lid_thickness + 0.01]
                );
            translate(
              [(rabbit_length + rabbit_offset + size_spacing * 2) / 2, wall_thickness / 2 - 0.01, -lid_thickness]
            )
              color(material_colour)
                rabbit_clip(
                  type="socket", length=rabbit_length, width=rabbit_width, snap=rabbit_snap,
                  thickness=rabbit_thickness, depth=rabbit_depth + 0.01,
                  compression=rabbit_compression, lock=rabbit_lock
                );
          }

    // Make sure the children start from the bottom corner of the box.
    $inner_width = width - wall_thickness * 2;
    $inner_length = length - wall_thickness * 2;
    $inner_height = height - lid_thickness - floor_thickness;
    for (i = [0:$children - 1]) {
      if (!in_list(i, positive_only_children)) {
        translate([wall_thickness, wall_thickness, floor_thickness]) children();
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
