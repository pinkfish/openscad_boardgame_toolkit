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

// Function: MakeLabelOptions()
// Arguments:
//   text_scale = the scale of the font to use
//   font = the font to use for the text (default {{default_label_font}})
//   label_colour = the label colour to use (default {{default_label_colour}})
//   solid_background = if the background should be solid (default false)
//   label_background_colour = the colour to use for the label background (default {{default_label_background_colour}})
//   label_diff = how much to move the label (default [0, 0])
// Topics: Label
function MakeLabelOptions(
  text_scale = 1.0,
  text_length = undef,
  angle = 0,
  label_colour = default_label_colour,
  label_background_colour = default_label_background_colour,
  short_length = false,
  label_diff = [0, 0],
  border = 2,
  offset = 4,
  radius = 5,
  label_background_colour = default_label_background_colour,
  font = default_label_font,
  full_height = false,
  finger_hole_size = 10,
  material_colour = default_material_colour,
  label_type = default_label_type
) =
  object(
    text_scale=text_scale,
    text_length=text_length,
    angle=angle,
    label_colour=label_colour,
    label_background_colour=label_background_colour,
    label_diff=label_diff,
    border=border,
    offset=offset,
    radius=radius,
    full_height=full_height,
    font=font,
    short_length=short_length,
    finger_hole_size=finger_hole_size,
    material_colour=material_colour,
    label_type=label_type
  );

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
//   label_diff = how much to move the label (default [0, 0])
// Topics: Label
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions());
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions(full_height=true));
// Example(Render):
//   MakeMainLidLabelSolid(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//     options=MakeLabelOptions(full_height = true, label_colour = "blue"));
module MakeMainLidLabelSolid(
  width,
  length,
  lid_thickness,
  label,
  options
) {
  assert(width > options.border * 2, str("Width must be wider than double the offset width=", width, " offset=", options.offset, "border=", options.border));
  assert(length > options.border * 2, str("Length must be wider than double the offset length=", length, " offset=", options.offset, "border=", options.border));
  assert(label != undef, "Must specify a label");
  assert(options != undef, "Must speify label options");

  module TextShape(calc_font, text_height = lid_thickness, edge_offset = 0) {
    linear_extrude(text_height) union() {
        // Edge box.
        offset(edge_offset) translate([options.offset, options.offset, 0])
            resize([width - options.offset * 2.5, length - options.offset * 2, 0], auto=true) {
              text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom");
            }
      }
  }
  translate([-width / 2 + options.label_diff[0], -length / 2 + options.label_diff[1], 0]) {

    calc_font = DefaultValue(options.font, default_label_font);

    translate(
      [
        0,
        0,
        options.full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) color(DefaultValue(options.label_colour, default_label_colour))
        TextShape(text_height=default_slicing_layer_height + 0.01, calc_font=calc_font);

    color(options.material_colour)
      cuboid(
        size=[
          width,
          length,
          options.full_height ? lid_thickness - default_slicing_layer_height
          : lid_thickness / 2 - default_slicing_layer_height,
        ],
        rounding=options.radius * 2 <= min(width, length) ? options.radius : min(width, length) / 2,
        edges="Z", anchor=FRONT + LEFT + BOTTOM
      );

    calc_background_colour = DefaultValue(options.label_background_colour, default_label_background_colour);
    difference() {
      color(options.material_colour)
        cuboid(
          size=[width, length, options.full_height || options.border > 0 ? lid_thickness : lid_thickness / 2],
          rounding=options.radius * 2 <= min(width, length) ? options.radius : min(width, length) / 2, edges="Z", anchor=FRONT + LEFT + BOTTOM
        );

      translate(
        [
          options.border,
          options.border,
          options.solid_background ? (
              options.full_height ? lid_thickness + default_slicing_layer_height
              : lid_thickness / 2 + default_slicing_layer_height
            )
          : -0.5,
        ]
      ) color(options.material_colour) {
          w = width - options.border * 2;
          l = length - options.border * 2;
          cuboid(
            size=[w, l, lid_thickness + 1],
            rounding=options.radius * 2 <= min(w, l) ? options.radius : min(w, l) / 2, edges="Z", anchor=FRONT + LEFT + BOTTOM
          );
        }
    }

    translate(
      [
        0,
        0,
        options.full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) difference() {
        translate([options.border + 0.01, options.border + 0.01, 0]) color(calc_background_colour) {
            w = width - options.border * 2 - 0.02;
            l = length - options.border * 2 - 0.02;
            cuboid(
              size=[w, l, default_slicing_layer_height],
              rounding=options.radius * 2 < min(w, l) ? options.radius : min(w, l) / 2, edges="Z", anchor=FRONT + LEFT + BOTTOM
            );
          }
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
//   options = the options associated with the labels
// Topics: Label
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions());
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions(full_height = true));
// Example(Render):
//   MakeMainLidLabelStriped(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//     options=MakeLabelOptions(full_height = true, label_colour = "blue"));
module MakeMainLidLabelStriped(
  width,
  length,
  lid_thickness,
  label,
  options
) {
  assert(width > options.border * 2, str("Width must be wider than double the border width=", width, " offset=", options.offset, " border=", options.border));
  assert(length > options.border * 2, str("Length must be wider than double the border length=", length, " offset=", options.offset, " border=", options.border));
  assert(label != undef, "Must specify a label");
  assert(options != undef, "Must speify label options");

  module TextShape(calc_font, text_thickness = lid_thickness, edge_offset = 0) {
    linear_extrude(text_thickness) union() {
        // Edge box.
        offset(edge_offset) translate([options.offset, options.offset, 0])
            resize([width - options.offset * 2.5, length - options.offset * 2, 0], auto=true) {
              text(text=str(label), font=calc_font, size=10, spacing=1, halign="left", valign="bottom");
            }
      }
  }
  module StripedBackground(calc_background_color) {
    translate(
      [
        0,
        0,
        options.full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) intersection() {
        w = width - options.border * 2;
        l = length - options.border * 2;
        translate([options.border + 0.01, options.border + 0.01, 0]) color(calc_background_color)
            cuboid(
              size=[w, l, default_slicing_layer_height],
              rounding=options.radius * 2 <= min(w, l) ? options.radius : min(w, l) / 2, edges="Z", anchor=FRONT + LEFT + BOTTOM
            );
        translate([0, 0, -default_slicing_layer_height / 2]) color(calc_background_color)
            linear_extrude(height=default_slicing_layer_height * 2)
              MakeStripedGrid(width=width, length=length);
      }

    intersection() {
      translate([options.border, options.border, 0]) color(options.material_colour) {
          w = width - options.border * 2;
          l = length - options.border * 2;
          cuboid(
            size=[
              w,
              l,
              options.full_height ? lid_thickness - default_slicing_layer_height
              : lid_thickness / 2 - default_slicing_layer_height,
            ],
            rounding=options.radius * 2 <= min(w, l) ? options.radius : min(w, l) / 2, edges="Z", anchor=FRONT + LEFT + BOTTOM
          );
        }

      color(options.material_colour) linear_extrude(height=lid_thickness)
          MakeStripedGrid(width=width, length=length);
    }
  }

  translate([-width / 2 + options.label_diff[0], -length / 2 + options.label_diff[1], 0]) {
    calc_font = DefaultValue(options.font, default_label_font);
    calc_background_color = DefaultValue(options.label_background_colour, default_label_background_colour);
    difference() {
      z = options.full_height || options.border > 0 ? lid_thickness : lid_thickness / 2;
      color(options.material_colour)
        cuboid(
          size=[width, length, z],
          rounding=options.radius * 2 <= min(width, length) ? options.radius : min(width, length) / 2, edges="Z",
          anchor=FRONT + LEFT + BOTTOM
        );

      translate(
        [
          options.border,
          options.border,
          -0.5,
        ]
      ) color(options.material_colour) {
          w = width - options.border * 2;
          l = length - options.border * 2;
          cuboid(
            size=[w, l, lid_thickness + 1],
            rounding=options.radius * 2 <= min(w, l) ? options.radius : min(w, l) / 2,
            edges="Z", anchor=FRONT + LEFT + BOTTOM
          );
        }
    }

    translate(
      [
        0,
        0,
        options.full_height ? 0
        : 0,
      ]
    ) color(options.material_colour) TextShape(
          calc_font=calc_font,
          text_thickness=options.full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2,
          edge_offset=0.01
        );

    translate(
      [
        0,
        0,
        options.full_height ? lid_thickness - default_slicing_layer_height
        : lid_thickness / 2,
      ]
    ) color(options.label_colour) TextShape(
          calc_font=calc_font,
          text_thickness=options.full_height ? default_slicing_layer_height : default_slicing_layer_height * 2,
          edge_offset=0.01
        );

    translate(
      [
        0,
        0,
        options.full_height ? 0
        : lid_thickness / 2 - default_slicing_layer_height,
      ]
    ) color(options.material_colour) TextShape(
          calc_font=calc_font,
          text_thickness=options.full_height ? lid_thickness - default_slicing_layer_height : default_slicing_layer_height * 2,
          edge_offset=0.01
        );

    difference() {
      StripedBackground(calc_background_color=calc_background_color);
      translate(
        [
          0,
          0,
          options.full_height ? -lid_thickness / 2
          : lid_thickness / 2 - default_slicing_layer_height * 2,
        ]
      ) color(options.material_colour) TextShape(
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
//   options = the options associated with the labels
// Topics: Label
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions());
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia",
//     options=MakeLabelOptions(full_height = true));
// Example(Render):
//   MakeFramedLidLabel(width = 20, length = 80, lid_thickness = 2,label = "Australia",
//     options=MakeLabelOptions(full_height = true, label_colour = "blue"));
module MakeFramedLidLabel(
  width,
  length,
  lid_thickness,
  label,
  options,
) {
  assert(label != undef, "Must specify a label");
  assert(options != undef, "Must speify label options");

  rotate([0, 0, 90]) translate([length / 2, -width / 2, 0]) {
      metrics = textmetrics(label, font=options.font);
      max_width =
        length > width && !options.short_length || options.short_length && length < width ?
          width - options.offset * 2
        : length - options.offset * 2;
      max_length =
        length > width && !options.short_length || options.short_length && length < width ?
          length * 3 / 4 - options.offset * 2
        : width * 3 / 4 - options.offset * 2;
      temp_calc_text_length = DefaultValue(
        options.text_length,
        length > width && !options.short_length || options.short_length && length < width ?
          length * 3 / 4 - options.offset * 2
        : width * 3 / 4 - options.offset * 2
      );
      temp_calc_text_width = metrics.size[1] / metrics.size[0] * temp_calc_text_length * options.text_scale + options.offset * 2;
      calc_text_width = temp_calc_text_width > max_width ? max_width : temp_calc_text_width;
      calc_text_length = temp_calc_text_width > max_width ? temp_calc_text_length * max_width / temp_calc_text_width : temp_calc_text_length;
      calc_finger_hole_size = DefaultValue(options.finger_hole_size, (options.short_length ? min(length, width) : max(length, width)) - calc_text_length - 10 > 0 ? 10 : 0);
      calc_radius = DefaultValue(options.radius, min(5, calc_text_width / 4));

      if (calc_text_width > 10 && calc_text_length > 1) {
        rotate(width > length && !options.short_length || options.short_length && width < length ? 90 : 0) {
          if (
            calc_finger_hole_size > 0 && calc_text_width + calc_finger_hole_size * 2 < width && calc_text_width + calc_finger_hole_size * 2 < length
          ) {
            color(options.material_colour)
              difference() {
                union() {
                  translate([options.label_diff[0], -calc_text_width / 2 + options.label_diff[1], 0]) difference() {
                      cyl(r=calc_finger_hole_size, h=lid_thickness, anchor=BOTTOM);
                      translate([0, 0, -0.5])
                        cyl(r=calc_finger_hole_size - options.border, h=lid_thickness + 1, anchor=BOTTOM);
                    }

                  translate([options.label_diff[0], calc_text_width / 2 + options.label_diff[1], 0]) difference() {
                      cyl(r=calc_finger_hole_size, h=lid_thickness, anchor=BOTTOM);
                      translate([0, 0, -0.5])
                        cyl(r=calc_finger_hole_size - options.border, h=lid_thickness + 1, anchor=BOTTOM);
                    }
                }
                translate([options.label_diff[0], options.label_diff[1], -0.5])
                  cuboid([calc_text_length, calc_text_width, lid_thickness + 1], anchor=BOTTOM);
              }
          }

          if (options.solid_background) {
            MakeMainLidLabelSolid(
              width=calc_text_length, length=calc_text_width,
              lid_thickness=lid_thickness, label=label,
              options=options
            );
          } else {
            MakeMainLidLabelStriped(
              width=calc_text_length, length=calc_text_width,
              lid_thickness=lid_thickness, label=label,
              options
            );
          }
        }
      } else {
        echo("WARNING: Lid too narrow for a label (ignoring label)");
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
//   options = the options associated with the labels
// Topics: Label
// Example(Render):
//   MakeFramelessLidLabel(width = 40, length = 80, lid_thickness = 2, label = "Australia",
//       options=MakeLabelOptions(font="Stencil Std:style=Bold", label_type = LABEL_TYPE_FRAMELESS,));
// Example(Render):
//   MakeFramelessLidLabel(width = 40, length = 80, lid_thickness = 2, label = "Australia",      
//      options=MakeLabelOptions(font="Stencil Std:style=Bold",
//         label_colour = "blue", label_type = LABEL_TYPE_FRAMELESS_ANGLE, ));
module MakeFramelessLidLabel(
  width,
  length,
  lid_thickness,
  label,
  options
) {
  cross_angle = asin(min(width, length) / sqrt(width * width + length * length));
  metrics = textmetrics(label, font=options.font);
  calc_text_length_start = DefaultValue(options.text_length, length > width ? length * 3 / 4 : width * 3 / 4);
  temp_text_width = metrics.size[1] / metrics.size[0] * calc_text_length_start * options.text_scale;
  temp_text_length =
    length < width ?
      (temp_text_width > length * 3 / 4 ? calc_text_length_start * (length * 3 / 4) / temp_text_width : calc_text_length_start)
    : (temp_text_width > width * 3 / 4 ? calc_text_length_start * (width * 3 / 4) / temp_text_width : calc_text_length_start);
  calc_text_length = min(temp_text_length, calc_text_length_start);
  angle = DefaultValue(options.angle, options.label_type == LABEL_TYPE_FRAMELESS_ANGLE ? (length > width ? 90 - cross_angle : cross_angle) : length > width ? 90 : 0);
  color(DefaultValue(options.label_background_colour, default_label_background_colour))
    translate([(width) / 2 + (sin(angle) * metrics.descent / 2) + options.label_diff[0], (length) / 2 + (cos(angle) * metrics.descent / 2) + options.label_diff[1], 0])
      linear_extrude(lid_thickness - default_slicing_layer_height)
        rotate(angle)
          resize([calc_text_length, metrics.size[1] / metrics.size[0] * calc_text_length * options.text_scale])
            text(label, font=options.font, halign="center", valign="center");
  color(DefaultValue(options.label_colour, default_label_colour))
    translate([(width) / 2 + (sin(angle) * metrics.descent / 2) + options.label_diff[0], (length) / 2 + (cos(angle) * metrics.descent / 2) + options.label_diff[1], lid_thickness - default_slicing_layer_height])
      linear_extrude(default_slicing_layer_height + 0.01)
        rotate(angle)
          resize([calc_text_length, metrics.size[1] / metrics.size[0] * calc_text_length * options.text_scale])
            text(label, font=options.font, halign="center", valign="center");
}
