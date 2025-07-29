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

// LibFile: labels.scad
//    This file has all the shared label pieces for the system.

// FileSummary: Shared label pieces.
// FileGroup: Basics

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Labels
//   Building blocks for making labels.

// Module: MakeStripedGrid()
// Description:
//   Creates a background striped grid, this is used in the label space generation.
// Usage:
//   MakeStripedGrid(20,50);
// Arguments:
//   width = width of the grid space
//   length = length of the grid space
//   bar_width = width of the bars (default 1)
// Topics: Label
// Example:
//   MakeStripedGrid(20, 50);
module MakeStripedGrid(width, length, bar_width = 1) {
  dx = bar_width * 2;
  x_count = (width + length) / (bar_width + dx);

  for (j = [0:x_count])
    intersection() {
      square([width, length]);
      {
        translate([j * (bar_width + dx), -bar_width]) rotate(45) square([bar_width, length * 2]);
      }
    }
}

// Module: Make3dStripedGrid()
// Description:
//   Creates a background striped grid, this is used in the label space generation.
// Usage:
//   Make3dStripedGrid(20,50);
// Arguments:
//   width = width of the grid space
//   length = length of the grid space
//   bar_width_top = width of the bars (default 1)
//   bar_width_bottom = height of the bar (default bar_width_top)
// Topics: Label
// Example:
//   Make3dStripedGrid(width = 20, length = 50, height = 1);
// Example:
//   Make3dStripedGrid(width = 20, length = 50, height = 0.2, bar_width_bottom = 1);
module Make3dStripedGrid(width, length, height, bar_width_top = 1, bar_width_bottom = undef, spacing = 0) {
  calc_bar_width_bottom = bar_width_bottom == undef ? bar_width_top : bar_width_bottom;
  bar_width = max(bar_width_top, calc_bar_width_bottom);

  dx = bar_width * 2 + spacing;
  x_count = (width + length) / (bar_width + dx);

  for (j = [0:x_count]) {

    translate([j * (bar_width + dx), length / 2, 0]) rotate([0, 0, 45])
        prismoid(
          size1=[calc_bar_width_bottom, length * 2], size2=[bar_width_top, length * 2],
          height=height, anchor=BOTTOM + LEFT
        );
  }
}

// Module: MakeMainLidLabelSolid()
// Description:
//   Makes a label inside a solid background to use in the lid.  It makes a label with a border and a stripped
//   or solid grid in the background to keep the label in place.
// Usage:
//   MakeMainLidLabelSolid(20, 80, 2, label="Australia", border = 2, offset = 4);
// Arguments:
//   width = width of the label section
//   length = length of the label section
//   lid_thickness = height of the lid/label
//   label = the text of the label
//   border = how wide the border is around the label (default 2)
//   offset = how far in from the sides the text should be (default 4)
//   font = the font to use for the text (default {{default_label_font}})
//   radius = the radius of the corners on the label section (default 5)
//   full_height = full height of the lid (default false)
//   label_colour = the label colour to use (default {{default_label_colour}})
//   solid_background = if the background should be solid (default false)
//   label_background_colour = the colour to use for the label background (default {{default_label_background_colour}})
// Topics: Label
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2, label = "Australia");
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//   full_height = true);
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//   full_height = true, label_colour = "blue");
module MakeMainLidLabelSolid(
  width,
  length,
  lid_thickness,
  label,
  border = 2,
  offset = 4,
  font = default_label_font,
  radius = 5,
  full_height = false,
  label_colour = undef,
  material_colour = default_material_colour,
  background_colour = undef,
  solid_background = false,
  label_background_colour = undef
) {
  module TextShape(calc_font, text_height = lid_thickness, edge_offset = 0) {
    linear_extrude(text_height) union() {
        // Edge box.
        offset(edge_offset) translate([offset, offset, 0])
            resize([width - offset * 2.5, length - offset * 2, 0], auto=true) {
              text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom");
            }
      }
  }
  translate([-width / 2, -length / 2, 0]) {

    calc_font = DefaultValue(font, default_label_font);

    translate(
      [
        0,
        0,
        full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) color(DefaultValue(label_colour, default_label_colour))
        TextShape(text_height=default_slicing_layer_height + 0.01, calc_font=calc_font);

    color(material_colour)
      cuboid(
        size=[
          width,
          length,
          full_height ? lid_thickness - default_slicing_layer_height
          : lid_thickness / 2 - default_slicing_layer_height,
        ],
        rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
      );

    calc_background_colour = DefaultValue(label_background_colour, default_label_background_colour);
    difference() {
      color(material_colour)
        cuboid(
          size=[width, length, full_height || border > 0 ? lid_thickness : lid_thickness / 2],
          rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
        );

      translate(
        [
          border,
          border,
          solid_background ? (
              full_height ? lid_thickness + default_slicing_layer_height
              : lid_thickness / 2 + default_slicing_layer_height
            )
          : -0.5,
        ]
      ) color(material_colour) cuboid(
            size=[width - border * 2, length - border * 2, lid_thickness + 1],
            rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
          );
    }

    translate(
      [
        0,
        0,
        full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) difference() {
        translate([border + 0.01, border + 0.01, 0]) color(calc_background_colour)
            cuboid(
              size=[width - border * 2 - 0.02, length - border * 2 - 0.02, default_slicing_layer_height],
              rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
            );
        translate([0, 0, -1]) color(calc_background_colour) TextShape(text_height=default_slicing_layer_height + 21, calc_font=calc_font);
      }
  }
}

// Module: MakeMainLidLabelStriped()
// Description:
//   Makes a label inside a striped grid to use in the lid.  It makes a label with a border and a stripped
//   or solid grid in the background to keep the label in place.
// Usage:
//   MakeMainLidLabelStriped(20, 80, 2, label="Australia", border = 2, offset = 4);
// Arguments:
//   width = width of the label section
//   length = length of the label section
//   lid_thickness = height of the lid/label
//   label = the text of the label
//   border = how wide the border is around the label (default 2)
//   offset = how far in from the sides the text should be (default 4)
//   font = the font to use for the text (default {{default_label_font}})
//   radius = the radius of the corners on the label section (default 5)
//   full_height = full height of the lid (default false)
//   label_colour = the label colour to use (default {{default_label_colour}})
//   solid_background = if the background should be solid (default false)
//   label_background_colour = the colour to use for the label background (default {{default_label_background_colour}})
// Topics: Label
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2, label = "Australia");
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//   full_height = true);
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//   full_height = true, label_colour = "blue");
module MakeMainLidLabelStriped(
  width,
  length,
  lid_thickness,
  label,
  border = 2,
  offset = 4,
  font = default_label_font,
  radius = 5,
  full_height = false,
  label_colour = undef,
  material_colour = default_material_colour,
  background_colour = undef,
  solid_background = false,
  label_background_colour = undef
) {

  module TextShape(calc_font, text_thickness = lid_thickness, edge_offset = 0) {
    linear_extrude(text_thickness) union() {
        // Edge box.
        offset(edge_offset) translate([offset, offset, 0])
            resize([width - offset * 2.5, length - offset * 2, 0], auto=true) {
              text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom");
            }
      }
  }
  module StripedBackground(calc_background_color) {
    translate(
      [
        0,
        0,
        full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) intersection() {
        translate([border + 0.01, border + 0.01, 0]) color(calc_background_color)
            cuboid(
              size=[width - border * 2, length - border * 2, default_slicing_layer_height],
              rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
            );
        translate([0, 0, -default_slicing_layer_height / 2]) color(calc_background_color)
            linear_extrude(height=default_slicing_layer_height * 2)
              MakeStripedGrid(width=width, length=length);
      }

    intersection() {
      translate([border, border, 0]) color(material_colour)
          cuboid(
            size=[
              width - border * 2,
              length - border * 2,
              full_height ? lid_thickness - default_slicing_layer_height
              : lid_thickness / 2 - default_slicing_layer_height,
            ],
            rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
          );

      color(material_colour) linear_extrude(height=lid_thickness)
          MakeStripedGrid(width=width, length=length);
    }
  }

  translate([-width / 2, -length / 2, 0]) {
    calc_font = DefaultValue(font, default_label_font);
    calc_background_color = DefaultValue(label_background_colour, default_label_background_colour);
    difference() {
      color(material_colour)
        cuboid(
          size=[width, length, full_height || border > 0 ? lid_thickness : lid_thickness / 2],
          rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
        );

      translate(
        [
          border,
          border,
          -0.5,
        ]
      ) color(material_colour) cuboid(
            size=[width - border * 2, length - border * 2, lid_thickness + 1],
            rounding=radius, edges="Z", anchor=FRONT + LEFT + BOTTOM
          );
    }

    translate(
      [
        0,
        0,
        full_height ? 0
        : 0,
      ]
    ) color(material_colour) TextShape(
          calc_font=calc_font,
          text_thickness=full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2,
          edge_offset=0.01
        );

    translate(
      [
        0,
        0,
        full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2,
      ]
    ) color(label_colour) TextShape(
          calc_font=calc_font,
          text_thickness=full_height ? default_slicing_layer_height : default_slicing_layer_height * 2,
          edge_offset=0.01
        );

    translate(
      [
        0,
        0,
        full_height ? 0
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) color(material_colour) TextShape(
          calc_font=calc_font,
          text_thickness=full_height ? lid_thickness - default_slicing_layer_height : default_slicing_layer_height * 2,
          edge_offset=0.01
        );

    difference() {
      StripedBackground(calc_background_color=calc_background_color);
      translate(
        [
          0,
          0,
          full_height ? -lid_thickness / 2
          : lid_thickness / 2 - default_slicing_layer_height * 2,
        ]
      ) color(material_colour) TextShape(
            calc_font=calc_font,
            text_thickness=lid_thickness * 4,
            edge_offset=0.01
          );
    }
  }
}

// Module: MakeFramedLidLabel()
// Description:
//   Makes a label inside a solid or striped grid to use in the lid.  It makes a label with a border and a stripped
//   or solid grid in the background to keep the label in place.
// Usage:
//   MakeFramedLidLabel(20, 80, 2, label="Australia", border = 2, offset = 4);
// Arguments:
//   width = width of the label section
//   length = length of the label section
//   lid_thickness = height of the lid/label
//   label = the text of the label
//   text_scale = the scale of the font to use (default 1.0)
//   border = how wide the border is around the label (default 2)
//   offset = how far in from the sides the text should be (default 4)
//   font = the font to use for the text (default {{default_label_font}})
//   radius = the radius of the corners on the label section (default 5)
//   full_height = full height of the lid (default false)
//   label_colour = the label colour to use (default {{default_label_colour}})
//   solid_background = if the background should be solid (default false)
//   label_background_colour = the colour to use for the label background (default {{default_label_background_colour}})
//   finger_holes = put in finger holes around the label {{default true}}
// Topics: Label
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia");
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//   full_height = true);
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//   full_height = true, label_colour = "blue");
module MakeFramedLidLabel(
  width,
  length,
  text_length,
  lid_thickness,
  label,
  short_length,
  text_scale = 1.0,
  border = 2,
  offset = 4,
  font = default_label_font,
  radius = undef,
  full_height = false,
  label_colour = undef,
  material_colour = default_material_colour,
  background_colour = undef,
  solid_background = false,
  label_background_colour = undef,
  finger_hole_size = 10
) {
  rotate([0, 0, 90]) translate([length / 2, -width / 2, 0]) {
      metrics = textmetrics(label, font=font);
      calc_text_length = DefaultValue(
        text_length,
        length > width && !short_length || short_length && length < width ?
          length * 3 / 4 - offset * 2
        : width * 3 / 4 - offset * 2
      );
      calc_text_width = metrics.size[1] / metrics.size[0] * calc_text_length * text_scale + offset * 2;
      calc_finger_hole_size = DefaultValue(finger_hole_size, (short_length ? min(length, width) : max(length, width)) - calc_text_length - 10 > 0 ? 10 : 0);
      calc_radius = DefaultValue(radius, min(5, calc_text_width / 4));

      rotate(width > length && !short_length || short_length && width < length ? 90 : 0) {
        if (
          calc_finger_hole_size > 0 && calc_text_width + calc_finger_hole_size * 2 < width && calc_text_width + calc_finger_hole_size * 2 < length
        ) {
          color(material_colour)
            difference() {
              union() {
                translate([0, -calc_text_width / 2, 0]) difference() {
                    cyl(r=calc_finger_hole_size, h=lid_thickness, anchor=BOTTOM);
                    translate([0, 0, -0.5])
                      cyl(r=calc_finger_hole_size - border, h=lid_thickness + 1, anchor=BOTTOM);
                  }

                translate([0, calc_text_width / 2, 0]) difference() {
                    cyl(r=calc_finger_hole_size, h=lid_thickness, anchor=BOTTOM);
                    translate([0, 0, -0.5])
                      cyl(r=calc_finger_hole_size - border, h=lid_thickness + 1, anchor=BOTTOM);
                  }
              }
              translate([0, 0, -0.5])
                cuboid([calc_text_length, calc_text_width, lid_thickness + 1], anchor=BOTTOM);
            }
        }

        if (solid_background) {
          MakeMainLidLabelSolid(
            width=calc_text_length, length=calc_text_width,
            lid_thickness=lid_thickness, label=label,
            border=border, offset=offset, font=font, radius=calc_radius,
            full_height=full_height,
            label_colour=label_colour, material_colour=material_colour,
            background_colour=background_colour, label_background_colour=label_background_colour
          );
        } else {
          MakeMainLidLabelStriped(
            width=calc_text_length, length=calc_text_width,
            lid_thickness=lid_thickness, label=label,
            border=border, offset=offset, font=font, radius=calc_radius,
            full_height=full_height, label_colour=label_colour,
            material_colour=material_colour, background_colour=background_colour,
            label_background_colour=label_background_colour
          );
        }
      }
    }
}

// Module: MakeFramelessLidLabel()
// Description:
//   Makes a label with just the text and no frame.
// Usage:
//   MakeFramelessLidLabel(20, 80, 2, "Australia");
// Arguments:
//   width = width of the box without the walls
//   length = length of the box without the walls
//   lid_thickness = height of the lid/label
//   label = the text of the label
//   text_scale = the scale of the font to use
//   font = the font to use for the text (default {{default_label_font}})
//   label_colour = the label colour to use (default {{default_label_colour}})
//   solid_background = if the background should be solid (default false)
//   label_background_colour = the colour to use for the label background (default {{default_label_background_colour}})
// Topics: Label
// Example(Render):
//   MakeFramelessLidLabel(width = 40, length = 80, lid_thickness = 2, label = "Australia",
//      label_type = LABEL_TYPE_FRAMELESS, font="Stencil Std:style=Bold");
// Example(Render):
//   MakeFramelessLidLabel(width = 40, length = 80, lid_thickness = 2, label = "Australia",
//      label_colour = "blue", label_type = LABEL_TYPE_FRAMELESS_ANGLE, font="Stencil Std:style=Bold");
module MakeFramelessLidLabel(
  width,
  length,
  lid_thickness,
  label,
  label_type,
  text_length = undef,
  font = default_label_font,
  text_scale = 1.0,
  angle = undef,
  label_colour = default_label_colour,
  material_colour = default_material_colour,
  label_background_colour = default_label_background_colour,
) {
  cross_angle = asin(min(width, length) / sqrt(width * width + length * length));
  metrics = textmetrics(label, font=font);
  calc_text_length_start = DefaultValue(text_length, length > width ? length * 3 / 4 : width * 3 / 4);
  temp_text_width = metrics.size[1] / metrics.size[0] * calc_text_length_start * text_scale;
  temp_text_length =
    length < width ?
      (temp_text_width > length * 3 / 4 ? calc_text_length_start * (length * 3 / 4) / temp_text_width : calc_text_length_start)
    : (temp_text_width > width * 3 / 4 ? calc_text_length_start * (width * 3 / 4) / temp_text_width : calc_text_length_start);
  calc_text_length = min(temp_text_length, calc_text_length_start);
  angle = DefaultValue(angle, label_type == LABEL_TYPE_FRAMELESS_ANGLE ? (length > width ? 90 - cross_angle : cross_angle) : length > width ? 90 : 0);
  color(DefaultValue(label_background_colour, default_label_background_colour))
    translate([(width) / 2 + (sin(angle) * metrics.descent / 2), (length) / 2 + (cos(angle) * metrics.descent / 2), 0])
      linear_extrude(lid_thickness - default_slicing_layer_height)
        rotate(angle)
          resize([calc_text_length, metrics.size[1] / metrics.size[0] * calc_text_length * text_scale])
            text(label, font=font, halign="center", valign="center");
  color(DefaultValue(label_colour, default_label_colour))
    translate([(width) / 2 + (sin(angle) * metrics.descent / 2), (length) / 2 + (cos(angle) * metrics.descent / 2), lid_thickness - default_slicing_layer_height])
      linear_extrude(default_slicing_layer_height + 0.01)
        rotate(angle)
          resize([calc_text_length, metrics.size[1] / metrics.size[0] * calc_text_length * text_scale])
            text(label, font=font, halign="center", valign="center");
}
