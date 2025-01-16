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
module MakeStripedGrid(width, length, bar_width = 1)
{
    dx = bar_width * 2;
    x_count = (width + length) / (bar_width + dx);

    intersection()
    {
        square([ width, length ]);
        for (j = [0:x_count])
        {

            translate([ j * (bar_width + dx), 0 ]) rotate([ 0, 0, 45 ]) square([ bar_width, length * 2 ]);
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
module Make3dStripedGrid(width, length, height, bar_width_top = 1, bar_width_bottom = undef, spacing = 0)
{
    calc_bar_width_bottom = bar_width_bottom == undef ? bar_width_top : bar_width_bottom;
    bar_width = max(bar_width_top, calc_bar_width_bottom);

    dx = bar_width * 2 + spacing;
    x_count = (width + length) / (bar_width + dx);

    for (j = [0:x_count])
    {

        translate([ j * (bar_width + dx), length / 2, 0 ]) rotate([ 0, 0, 45 ])
            prismoid(size1 = [ calc_bar_width_bottom, length * 2 ], size2 = [ bar_width_top, length * 2 ],
                     height = height, anchor = BOTTOM + LEFT);
    }
}

// Module: MakeMainLidLabel()
// Description:
//   Makes a label inside a solid or striped grid to use in the lid.  It makes a label with a border and a stripped
//   or solid grid in the background to keep the label in place.
// Usage:
//   MakeMainLidLabel(20, 80, 2, label="Australia", border = 2, offset = 4);
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
//   MakeMainLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia");
// Example(Render):
//   MakeMainLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia", full_height = true);
// Example(Render):
//   MakeMainLidLabel(width = 20, length = 80, lid_thickness = 2, label = "Australia", full_height = true,
//   label_colour = "blue");
module MakeMainLidLabel(width, length, lid_thickness, label, border = 2, offset = 4, font = default_label_font,
                        radius = 5, full_height = false, label_colour = undef,
                        material_colour = default_material_colour, background_colour = undef, solid_background = false,
                        label_background_colour = undef)
{
    module TextShape(text_height = lid_thickness, edge_offset = 0)
    {
        linear_extrude(text_height) union()
        {
            // Edge box.
            offset(edge_offset) translate([ offset, offset, 0 ])
                resize([ width - offset * 2, length - offset * 2, 0 ], auto = true)
            {
                text(text = str(label), font = calc_font, size = 10, spacing = 1, halign = "left", valign = "bottom");
            }
        }
    }
    module StripedBackground()
    {
        intersection()
        {
            translate([
                border + 0.01, border + 0.01,
                full_height ? lid_wall_thickness - default_slicing_layer_height : lid_thickness / 2 -
                default_slicing_layer_height
            ]) color(calc_background_color)
                cuboid(size = [ width - border * 2, length - border * 2, default_slicing_layer_height ],
                       rounding = radius, edges = "Z", anchor = FRONT + LEFT + BOTTOM);
            color(calc_background_color) linear_extrude(height = lid_thickness)
                MakeStripedGrid(width = width, length = length);
        }
        intersection()
        {
            translate([ border, border, 0 ]) color(material_colour)
                cuboid(size =
                           [
                               width - border * 2, length - border * 2,
                               full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2 -
                               default_slicing_layer_height
                           ],
                       rounding = radius, edges = "Z", anchor = FRONT + LEFT + BOTTOM);
            color(material_colour) linear_extrude(height = lid_thickness)
                MakeStripedGrid(width = width, length = length);
        }
    }
    calc_font = DefaultValue(font, default_label_font);

    if (solid_background)
    {
        translate([
            0, 0, full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2 -
            default_slicing_layer_height
        ]) color(DefaultValue(label_colour, default_label_colour))
            TextShape(text_height = default_slicing_layer_height + 0.01);
    }
    else
    {
        color(material_colour)
            TextShape(text_height = full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2);
        translate([ 0, 0, full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2 ])
            color(DefaultValue(label_colour, default_label_colour))
                TextShape(text_height = default_slicing_layer_height);
    }
    calc_background_color = DefaultValue(label_background_colour, default_label_background_colour);
    difference()
    {
        color(material_colour) cuboid(size = [ width, length, lid_thickness ], rounding = radius, edges = "Z",
                                      anchor = FRONT + LEFT + BOTTOM);

        translate([
            border, border,
            solid_background ? (full_height ? lid_thickness - default_slicing_layer_height
                                            : lid_thickness / 2 - default_slicing_layer_height)
                             : -0.5
        ]) color(material_colour) cuboid(size = [ width - border * 2, length - border * 2, lid_thickness + 1 ],
                                         rounding = radius, edges = "Z", anchor = FRONT + LEFT + BOTTOM);
    }
    if (solid_background)
    {
        difference()
        {
            translate([
                border, border, full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2 -
                default_slicing_layer_height
            ]) color(calc_background_color)
                cuboid(size = [ width - border * 2, length - border * 2, default_slicing_layer_height ],
                       anchor = BOTTOM + LEFT + FRONT, rounding = radius, edges = "Z");
            translate([
                0, 0, full_height ? lid_thickness - default_slicing_layer_height : lid_thickness / 2 -
                default_slicing_layer_height
            ]) color(calc_background_color)
                TextShape(text_height = default_slicing_layer_height + 1, edge_offset = -0.01);
        }
    }
    else
    {
        difference()
        {
            StripedBackground();
            color(calc_background_color) TextShape(text_height = lid_thickness, edge_offset = -0.01);
        }
    }
}