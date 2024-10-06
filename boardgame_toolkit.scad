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

// LibFile: boardgame_toolkit.scad
//    This file has all the modules needed to generate varioius inserts
//    for board games.  It makes the generation of the inserts simpler by
//    creating a number of useful base modules for making boxes and lids
//    of various types specific to board game inserts.  Specifically it
//    makes tabbed lids and sliding lids easily.
//

// FileSummary: Various modules to generate board game inserts.

// Includes:
//   include <boardgame_toolkit.scad>

include <BOSL2/rounding.scad>
include <BOSL2/std.scad>

// Constant: m_piece_wiggle_room
// Description:
//   How many mm to use as gaps for when things join.
m_piece_wiggle_room = 0.2;

// Constant: SHAPE_TYPE_DENSE_HEX
// Description:
//   Creates a shape with a dense hexes, so they overlap.
SHAPE_TYPE_DENSE_HEX = 1;
// Constant: SHAPE_TYPE_DENSE_TRIANGLE
// Description:
//   Creates a shape with a dense triangles, so they overlap.
SHAPE_TYPE_DENSE_TRIANGLE = 2;
// Constant: SHAPE_TYPE_CIRCLE
// Description:
//   Creates a shape with a circles.
SHAPE_TYPE_CIRCLE = 3;
// Constant: SHAPE_TYPE_HEX
// Description:
//   Creates a shape with a hexes.
SHAPE_TYPE_HEX = 4;
// Constant: SHAPE_TYPE_OCTOGON
// Description:
//   Creates a shape with a octogons.
SHAPE_TYPE_OCTOGON = 5;
// Constant: SHAPE_TYPE_TRIANGLE
// Description:
//   Creates a shape with a triangle.
SHAPE_TYPE_TRIANGLE = 6;
// Constant: SHAPE_TYPE_NONE
// Description:
//   Empty shape, no space filling.
SHAPE_TYPE_NONE = 7;
// Constant: SHAPE_TYPE_SQUARE
// Description:
//   Layout a nice set of squares.
SHAPE_TYPE_SQUARE = 8;
// Constant: SHAPE_TYPE_ROUNDED_SQUARE
// Description:
//   Layout a nice set of rounded squares.
SHAPE_TYPE_ROUNDED_SQUARE = 9;
// Constant: SHAPE_TYPE_HILBERT
// Description:
//   Layout a nice hilbert curve.
SHAPE_TYPE_HILBERT = 10;

// Section: Components
//   Building blocks to make all the rest of the items from.  This has all the basic parts of the board game
//   toolkit for making polygons and laying them out.

// Module: RoundedBoxOnLength()
// Usage:
//   RoundedBoxOnLength(100, 50, 10, 5);
// Description:
//   Creates a rounded box for use in the board game insert with a nice radius on two sides (length side).
// Arguments:
//   width = width of the cube
//   length = of the cube
//   height = of the cube
//   radius = radius of the curve on the edges
// Topics: Recess
// Example:
//   RoundedBoxOnLength(30, 20, 10, 7);

module RoundedBoxOnLength(width, length, height, radius)
{
    hull()
    {
        difference()
        {
            translate([ width / 2, length / 2, 0 ]) hull()
            {
                ydistribute(l = length - radius * 2)
                {
                    xcyl(l = width, r = radius);
                    xcyl(l = width, r = radius);
                }
            }
            translate([ -0.5, -0.5, radius ]) cube([ width + 1, length + 1, radius + 1 ]);
        }

        translate([ 0, 0, height - 1 ]) cube([ width, length, 1 ]);
    }
}

// Module: RoundedBoxAllSides()
// Usage:
//   RoundedBoxAllSides(30,20,10,5);
// Description:
//   Creates a rounded box with all the sides rounded.
// Arguments:
//   width = width of the cube
//   length = of the cube
//   height = of the cube
//   radius = radius of the curve on the edges
// Topics: Recess
// Example:
//   RoundedBoxAllSides(30, 20, 10, 7);
module RoundedBoxAllSides(width, length, height, radius)
{
    hull()
    {
        difference()
        {
            hull()
            {
                translate([ radius, radius, radius ]) sphere(radius);

                translate([ width - radius, radius, radius ]) sphere(radius);

                translate([ radius, length - radius, radius ]) sphere(radius);

                translate([ width - radius, length - radius, radius ]) sphere(radius);
            }
            translate([ -0.5, -0.5, radius ]) cube([ width + 1, length + 1, radius + 1 ]);
        }

        translate([ 0, 0, height - 1 ]) cube([ width, length, 1 ]);
    }
}

// Module: RoundedBoxGrid()
// Usage:
//   RoundedBoxGrid(20,20,10,5, rows=2, cols=1);
// Description:
//   Create a grid of rounded boxes, this is useful for inserting a number of containers inside a insert box.
// Arguments:
//   width = width of the space (total, inside will be divided by this)
//   length = of the space (total, inside will be divided by this)
//   height = of the space
//   radius = radius of the curve on the edges
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = number of mm between the spaces (default 2)
//   all_sides = round all the sides (default false)
// Topics: Recess, Grid
// Example:
//   RoundedBoxGrid(30, 20, 10, 7, rows=2, cols=1);
module RoundedBoxGrid(width, length, height, radius, rows, cols, spacing = 2, all_sides = false)
{
    row_length = (width - spacing * (rows - 1)) / rows;
    col_length = (length - spacing * (cols - 1)) / cols;
    for (x = [0:rows - 1])
        for (y = [0:cols - 1])
            translate([ x * (row_length + spacing), y * (col_length + spacing), 0 ])
            {
                if (all_sides)
                {
                    RoundedBoxAllSides(length = col_length, width = row_length, height = height, radius = radius);
                }
                else
                {
                    RoundedBoxOnLength(length = col_length, width = row_length, height = height, radius = radius);
                }
            }
}

// Module: RegularPolygon()
// Usage:
//   RegularPolygon(10, 5, 6);
// Description:
//   Creates a regular polygon with specific height/width and number of edges.
// Arguments:
//   width = total width of the piece, this is equivilant to the apothem of a polygon * 2
//   height = how high to create the item
//   shape_edges =  number of edges for the polygon
// Topics: Recess
// Example:
//   RegularPolygon(10, 5, shape_edges = 6);
module RegularPolygon(width, height, shape_edges)
{
    rotate_deg = ((shape_edges % 2) == 1) ? 180 / shape_edges + 90 : (shape_edges == 4 ? 45 : 0);
    apothem = width / 2;
    radius = apothem / cos(180 / shape_edges);

    rotate([ 0, 0, rotate_deg ]) linear_extrude(height = height) regular_ngon(n = shape_edges, or = radius);
}

// Module: RegularPolygonGrid()
// Description:
//   Lays out the grid with all the polygons as children.  The layout handles any shape as children.
//   This uses the exact width of the polygon to layout the underlying grid.  This just does all the
//   spacing, the actual generation is done using the children to this module.  This is usually used in
//   conjuction with {{RegularPolygon()}}
// Usage:
//   RegularPolygonGrid(10, 2, 1, 2)
// Arguments:
//   width = total width of the piece, this is equivilant to the apothem of a polygon * 2
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = spacing between shapres
//   aspect_ratio = ratio between shape and width, the dy is * this (default 1.0)
// Topics: Grid
// Example:
//   RegularPolygonGrid(width = 10, rows = 2, cols = 1, spacing = 2)
//      RegularPolygon(width = 10, height = 5, shape_edges = 6);
module RegularPolygonGrid(width, rows, cols, spacing = 2, shape_edges = 6, aspect_ratio = 1.0)
{
    apothem = width / 2;
    radius = apothem / cos(180 / shape_edges);
    side_length = 2 * apothem * tan(180 / shape_edges);
    extra_edge = 2 * side_length * cos(360 / shape_edges);

    dx = ((shape_edges % 2) == 1) ? apothem + radius + spacing : apothem * 2 + spacing;
    dy =
        ((shape_edges % 2) == 0 ? ((shape_edges / 2 % 2) == 1 ? radius * 2 + spacing : apothem * 2 + spacing)
                                : abs(2 * apothem * sin(((shape_edges - 1) / (shape_edges * 2)) * 360)) * 2 + spacing) *
        aspect_ratio;
    dx_y = 0;
    offset_y = ((shape_edges % 2) == 1) ? (apothem + radius) / 2 : apothem;
    offset_x = ((shape_edges % 2) == 0) ? ((shape_edges / 2 % 2) == 1 ? radius : apothem)
                                        : abs(2 * apothem * sin(((shape_edges - 1) / (shape_edges * 2)) * 360));

    rotate_deg = ((shape_edges % 2) == 1) ? 180 / shape_edges + 90 : (shape_edges == 4 ? 45 : 0);

    for (i = [0:rows - 1])
        for (j = [0:cols - 1])
            translate([ i * dy + offset_x, j * dx + i * dx_y + offset_y, 0 ])
            {
                children();
            }
}

// Module: RegularPolygonGridDense()
// Description:
//   Lays out the grid with all the polygons as children in a dense layout, this only works for triangles and hexes.
//   It will do a dense space filling using the spacing as the distance between the polygons.
//   This uses the exact width of the polygon to layout the underlying grid.  This just does all the
//   spacing, the actual generation is done using the children to this module.  This is usually used in
//   conjuction with {{RegularPolygon()}}
// Usage:
//   RegularPolygonGridDense(10, 2, 1)
// Arguments:
//   radius = this is the radius of the polygon, distance from center to edges
//   rows = number of rows to generate
//   cols = number of cols to generate
//   spacing = spacing between shapres
// Topics: Grid
// Example:
//   RegularPolygonGridDense(radius = 10, rows = 3, cols = 2)
//      RegularPolygon(width = 10, height = 5, shape_edges = 6);
//
module RegularPolygonGridDense(radius, rows, cols, shape_edges = 6)
{
    apothem = radius * cos(180 / shape_edges);
    side_length = (shape_edges == 3) ? radius * sqrt(3) : 2 * apothem * tan(180 / shape_edges);
    extra_edge = 2 * side_length * cos(360 / shape_edges);
    triangle_height = sqrt(3) / 2 * side_length;

    dx = (shape_edges == 3) ? side_length : apothem;
    col_x = apothem + radius;
    dy = (shape_edges == 3) ? triangle_height : 0.75 * (radius + radius);

    for (i = [0:rows - 1])
        for (j = [0:cols - 1])
            if (shape_edges == 6)
            {
                translate([ i * dy, (i % 2) == 0 ? (j * 2 + 1) * dx : j * 2 * dx, 0 ])
                {
                    children();
                }
            }
            else
            {
                translate([ i / 2 * dy, j * dx + ((i + 1) % 2) * (side_length / 2), 0 ])
                {
                    if (i % 2 == 1)
                    {
                        translate([ triangle_height - side_length, 0, 0 ]) mirror([ 1, 0, 0 ]) children();
                    }
                    else
                    {
                        children();
                    }
                }
            }
}

// Module: HexGridWithCutouts()
// Description:
//   This creates a hex grid with cutouts that can be used to cut out piece of a box to make a nice hex spacing
//   inside the box.
// Usage:
//   HexGridWithCutouts(rows = 4, cols = 3, height = 10, spacing = 0, push_block_height = 1, tile_width = 29);
// Arguments:
//   rows = rows of the grid
//   cols = colrs of the grid
//   height = height of the grid
//   spacing = space between the tiles
//   tile_width = width of the tiles
//   push_block_height = height of the pushblock to use (default 0)
// Topics: Recess Grid
// Example:
//   HexGridWithCutouts(rows = 4, cols = 3, height = 10, spacing = 0, push_block_height = 1, tile_width = 29);
module HexGridWithCutouts(rows, cols, height, spacing, tile_width, push_block_height = 0, wall_thickness = 2)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    RegularPolygonGrid(width = width, rows = rows, cols = cols, spacing = 0, shape_edges = 6)
    {
        union()
        {
            difference()
            {
                RegularPolygon(width = width, height = 10 + height, shape_edges = 6);
                RegularPolygon(width = 15, height = push_block_height, shape_edges = 6);
            }

            translate([ 0, apothem, 0 ]) cuboid([ radius, 10, 35 ], anchor = BOT);

            // Put in all the finger holes in the grid.
            translate([ radius + 1, -apothem, -6 ])
                cuboid([ radius + wall_thickness, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ radius + 1, apothem, -6 ])
                cuboid([ radius + wall_thickness, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ -radius + 1, -apothem, -6 ])
                cuboid([ radius + wall_thickness, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ -radius + 1, apothem, -6 ])
                cuboid([ radius + wall_thickness, 15, radius * 2 ], anchor = BOT, rounding = 3);
        }
    }
}

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

// Module: MakeStripedLidLabel()
// Description:
//   Makes a label inside a striped grid to use in the lid.  It makes a label with a border and a striped
//   grid in the background to keep the label in plave.
// Usage:
//   MakeStripedLidLabel(20, 80, 2, label="Australia", border = 2, offset = 4);
// Arguments:
//   width = width of the label section
//   length = length of the label section
//   lid_height = height of the lid/label
//   label = the text of the label
//   border = how wide the border is around the label (default 2)
//   offset = how far in from the sides the text should be (default 4)
//   font = the font to use for the text (default "Stencil Std:style=Bold")
//   radius = the radius of the corners on the label section
// Topics: Label
// Example:
//   MakeStripedLidLabel(width = 20, length = 80, lid_height = 2, label = "Australia");
module MakeStripedLidLabel(width, length, lid_height, label, border = 2, offset = 4, font = "Stencil Std:style=Bold",
                           radius = 5)
{
    intersection()
    {
        cuboid(size = [ width, length, lid_height ], rounding = radius, edges = "Z", anchor = FRONT + LEFT + BOTTOM);
        union()
        {
            difference()
            {
                cuboid(size = [ width, length, lid_height ], rounding = radius, edges = "Z",
                       anchor = FRONT + LEFT + BOTTOM);

                translate([ border, border, -0.5 ])
                    cuboid(size = [ width - border * 2, length - border * 2, lid_height + 1 ], rounding = radius,
                           edges = "Z", anchor = FRONT + LEFT + BOTTOM);
            }
            linear_extrude(height = lid_height) union()
            {
                // Edge box.
                translate([ offset, offset, 0 ]) resize([ width - offset * 2, length - offset * 2, 0 ], auto = true)
                {
                    text(text = str(label), font = font, size = 10, spacing = 1, halign = "left", valign = "bottom");
                }
            }
            linear_extrude(height = lid_height / 2) MakeStripedGrid(width = width, length = length);
        }
    }
}

// Section: Lid
//   Building blocks for making various kinds of lids and labels.

// Module: LidMeshDense()
// Description:
//   Make a hex mesh for the lid.  This makes a nice pattern for use on the lids.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_height = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   radius = the radius of the polygon to create
//   shape_thickness = how thick to generate the gaps between the hexes (default 2)
//   shape_edges = number of edges for the shape (default 6)
//   offset = how much to offset the shape, so you can do overlapping shapes (default 0)
// Usage:
//   LidMeshDense(width = 70, length = 50, lid_height = 3, boundary = 10, radius = 5, shape_thickness = 2, shape_edges =
//   6);
// Topics: PatternFill
// Example:
//   LidMeshDense(width = 100, length = 50, lid_height = 3, boundary = 10, radius = 10, shape_thickness = 2, shape_edges
//   = 6);
// Example:
//   LidMeshDense(width = 100, length = 50, lid_height = 3, boundary = 10, radius = 10, shape_thickness = 2, shape_edges
//   = 3);
module LidMeshDense(width, length, lid_height, boundary, radius, shape_thickness = 2, shape_edges = 6, offset = 0)
{
    cell_width = cos(180 / shape_edges) * radius;
    rows = width / cell_width;
    cols = length / cell_width;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_height) RegularPolygonGridDense(radius = radius, rows = rows, cols = cols,
                                                                        shape_edges = shape_edges) difference()
            {
                regular_ngon(or = radius + shape_thickness / 2 + offset, n = shape_edges);
                regular_ngon(or = radius - shape_thickness / 2 + offset, n = shape_edges);
            }

            difference()
            {
                cube([ width - boundary * 2, length - boundary * 2, lid_height + 1 ]);
                translate([ shape_thickness / 2, shape_thickness / 2, 0 ]) cube([
                    width - boundary * 2 - shape_thickness, length - boundary * 2 - shape_thickness, lid_height + 1
                ]);
            }
        }
        cube([ width - boundary * 2, length - boundary * 2, lid_height ]);
    }
}

// Module: LidMeshHex()
// Description:
//   Make a hex mesh for the lid.  This makes a nice pattern for use on the lids.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_height = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   radius = the radius of the polygon to create
//   shape_thickness = how thick to generate the gaps between the hexes
// Usage:
//   LidMeshHex(width = 70, length = 50, lid_height = 3, boundary = 10, radius = 5, shape_thickness = 2);
// Topics: PatternFill
// Example:
//   LidMeshHex(width = 100, length = 50, lid_height = 3, boundary = 10, radius = 10, shape_thickness = 2);
module LidMeshHex(width, length, lid_height, boundary, radius, shape_thickness = 2)
{
    LidMeshDense(width = width, length = length, lid_height = lid_height, boundary = boundary, radius = radius,
                 shape_thickness = shape_thickness, shape_edges = 6);
}

// Module: LidMeshRepeating()
// Description:
//   Make a mesh for the lid with a repeating shape.  It uses the children of this to repeat the shape.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_height = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   shape_width = the width to use between each shape.
//   aspect_ratio = the aspect ratio (multiple by dy) (default 1.0)
//   shape_edges = the number of edges on the shape (default 4)
// Usage:
//   LidMeshRepeating(50, 20, 3, 5, 10);
// Topics: PatternFill
// Example:
//   LidMeshRepeating(width = 50, length = 50, lid_height = 3, boundary = 5, shape_width = 10)
//      difference() {
//        circle(r = 7);
//        circle(r = 6);
//      }
module LidMeshRepeating(width, length, lid_height, boundary, shape_width, aspect_ratio = 1.0, shape_edges = 4)
{
    rows = width / shape_width;
    cols = length / shape_width * aspect_ratio;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_height)
                RegularPolygonGrid(width = shape_width, rows = rows + 1, cols = cols + 1, spacing = 0,
                                   shape_edges = shape_edges, aspect_ratio = aspect_ratio)
            {
                children();
            }
            difference()
            {
                translate([0,0,-0.5])
                cube([ width, length, lid_height + 1 ]);
                cube([ width - boundary * 2, length - boundary * 2, lid_height + 1 ]);
            }
        }
        cube([ width - boundary * 2, length - boundary * 2, lid_height ]);
    }
}

// Module: LidMeshBasic()
// Description:
//   Creates a lid mesh with a set of known shapes.  The width is the width of the shape
//   for layout purposes and the shape_width is the width for generation purposes.  The layout
//   width and shape width default to being the same for dense layouts, and overlapping for
//   non-dense layouts.
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 11);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 14);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 16);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 13, aspect_ratio=1.25);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 10.5, aspect_ratio=1);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_height = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_ROUNDED_SQUARE, shape_thickness = 2, shape_width = 11);
module LidMeshBasic(width, length, lid_height, boundary, layout_width, shape_type, shape_width, shape_thickness,
                    aspect_ratio = 1.0)
{
    if (shape_type == SHAPE_TYPE_DENSE_HEX)
    {
        if (shape_width == undef)
        {
            LidMeshDense(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         radius = layout_width / 2, shape_thickness = shape_thickness, shape_edges = 6,
                         offset = shape_width - layout_width);
        }
        else
        {
            LidMeshDense(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         radius = layout_width / 2, shape_thickness = shape_thickness, shape_edges = 6,
                         offset = shape_width - layout_width);
        }
    }
    else if (shape_type == SHAPE_TYPE_DENSE_TRIANGLE)
    {
        if (shape_width == undef)
        {
            LidMeshDense(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         radius = layout_width / 2, shape_thickness = 2, shape_edges = 3,
                         offset = shape_width - layout_width);
        }
        else
        {
            LidMeshDense(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         radius = layout_width / 2, shape_thickness = layout_width - shape_width, shape_edges = 3,
                         offset = shape_width - layout_width);
        }
    }
    else if (shape_type == SHAPE_TYPE_CIRCLE)
    {
        LidMeshRepeating(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         shape_width = layout_width, shape_edges = 4, aspect_ratio = aspect_ratio) difference()
        {
            circle(r = shape_width / 2);
            circle(r = (shape_width - shape_thickness) / 2);
        }
    }
    else if (shape_type == SHAPE_TYPE_TRIANGLE || shape_type == SHAPE_TYPE_HEX || shape_type == SHAPE_TYPE_OCTOGON ||
             shape_type == SHAPE_TYPE_SQUARE)
    {
        shape_edges = shape_type == SHAPE_TYPE_TRIANGLE
                          ? 3
                          : (shape_type == SHAPE_TYPE_HEX ? 6 : (shape_type == SHAPE_TYPE_SQUARE ? 4 : 8));
        LidMeshRepeating(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         shape_width = layout_width, shape_edges = shape_edges, aspect_ratio = aspect_ratio)
            difference()
        {
            regular_ngon(r = shape_width / 2, n = shape_edges);
            regular_ngon(r = (shape_width - shape_thickness) / 2, n = shape_edges);
        }
    }
    else if (shape_type == SHAPE_TYPE_ROUNDED_SQUARE)
    {
        LidMeshRepeating(width = width, length = length, lid_height = lid_height, boundary = boundary,
                         shape_width = layout_width, shape_edges = 4, aspect_ratio = aspect_ratio) difference()
        {
            rect([ shape_width, shape_width ], rounding = 3, corner_flip = true, $fn = 16);
            rect([ shape_width - shape_thickness, shape_width - shape_thickness ], rounding = 3, corner_flip = true,
                 $fn = 16);
        }
    }
    else if (shape_type == SHAPE_TYPE_HILBERT)
    {
        intersection()
        {
            difference()
            {
                cube([ width - boundary * 2, length - boundary * 2, lid_height ]);
                translate([ max(width, length) / 2, max(width, length) / 2, -0.1 ])
                    linear_extrude(height = lid_height + 1)
                        HilbertCurve(order = 3, size = max(width, length) / 2, line_thickness = shape_thickness);
            }
            cube([ width - boundary * 2, length - boundary * 2, lid_height ]);
        }
    }
    else if (shape_type == SHAPE_TYPE_NONE)
    {
        // Don't do anything.
    }
    else
    {
        assert(false, "Invalid shape type");
    }
}

module internal_build_lid(width, length, lid_thickness, wall_thickness, lid_size_spacing = m_piece_wiggle_room)
{
    union()
    {
        difference()
        {
            children(0);

            // Carve out holes for the children.
            if ($children > 1)
            {
                for (i = [1:$children - 1])
                {
                    translate([ 0, 0, -0.5 ]) linear_extrude(height = lid_thickness + 1) offset(r = -lid_size_spacing)
                        fill() projection(cut = false)
                    {
                        children(i);
                    }
                }
            }
        }
        // Merge in the children.
        if ($children > 1)
        {
            for (i = [1:$children - 1])
            {
                // Carve out holes in the next children.
                difference()
                {
                    children(i);
                    if (i + 1 < $children)
                    {
                        for (j = [i + 1:$children - 1])
                        {
                            translate([ 0, 0, -0.5 ]) linear_extrude(height = lid_thickness + 1)
                                offset(r = -lid_size_spacing) fill() projection(cut = false)
                            {
                                children(j);
                            }
                        }
                    }
                }
            }
        }
    }
}

// Module: SlidingLidFingernail()
// Description:
//   Creates a fingernail section for moving a sliding lid.
// Usage:
//   SlidingLidFingernail(radius = 10, lid_height = 3);
// Arguments:
//   radius = radius of the circle the gap is in
//   lid_height = height of the lid
//   finger_gap = the space to make for a finger gap (default = 1.5)
//   sphere = the size of the sphere for the inset (default 12)
//   finger_length = the length of the finger section (default = 15)
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLidFingernail(3);

module SlidingLidFingernail(lid_height, radius = 6, finger_gap = 1.5, sphere = 12, finger_length = 10)
{
    difference()
    {
        translate([ 0, 0, lid_height / 2 ]) cyl(h = lid_height, r = radius);
        translate([ 0, 0, finger_length + lid_height - finger_gap + 0.1 ]) intersection()
        {
            translate([ -finger_length / 2, -finger_length, -finger_length ])
                cube([ finger_length, finger_length, finger_gap ]);
            sphere(r = finger_length);
        }
    }
}

// Module: MakeLidTab()
// Description:
//   Makes a lid tab, a single lid lab, to use for boxes.
// Usage:
//   MakeLidTab(5, 10, 2);
// Arguments:
//   length = the length of the tab
//   height = the height of the tab
//   lid_height = the height of the lid (defaults to 2)
//   prism_width = the width of the prism (defaults to 0.75)
//   wall_thickness = the thickness of the walls (default 2)
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeLidTab(length = 5, height = 10, lid_height = 2, prism_width = 0.75, wall_thickness = 2);
module MakeLidTab(length, height, lid_height = 2, prism_width = 0.75, wall_thickness = 2)
{
    mirror([ 0, 0, 1 ])
    {
        // square part, join to the lid.
        cube([ length, wall_thickness, lid_height ]);

        union()
        {
            // Stalk
            cube([ length, wall_thickness / 2, height - wall_thickness + 0.1 ]);

            hull()
            {
                translate([ length / 2, wall_thickness * prism_width - 0.1, height - wall_thickness + 0.1 ])
                    xcyl(h = length, r = 0.1);
                translate([ 0, 0, height - wall_thickness ]) cube([ length, 0.1, 0.1 ]);
                translate([ length / 2, 0.1, height - 0.1 ]) xcyl(h = length, r = 0.1);
            }
        }
    }
}

// Module: MakeTabs()
// Description:
//   Create the tabs for the box, this can be used on the lids and the box to create cutouts,
//   this just does the layout. Use the {{MakeLidTab()}} to make the tabs, it will place the children
//   at each of the specified offsets to make the tabs.
// Usage:
//   MakeTabs(50, 100, wall_thickness = 2, lid_height = 2);
// Arguments:
//   box_width = width of the box (outside size)
//   box_length = length of the box (outside size)
//   wall_thickness = thickness of the walls to use (default = 2)
//   lid_height = the height of the lid (default = 2)
//   tab_length = how long the tab is (default = 10)
//   make_tab_width = make tabs on the width side (default false)
//   make_tab_length = make tabs on the length side (default true)
//   prism_width = width of the prism to take from the side of the box (default 0.75)
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeTabs(50, 100)
//     MakeLidTab(length = 10, height = 6);
module MakeTabs(box_width, box_length, wall_thickness = 2, lid_height = 2, tab_length = 10, make_tab_width = false,
                make_tab_length = true, prism_width = 0.75)
{

    if (make_tab_length)
    {
        translate([ 0, (box_length + tab_length) / 2, lid_height ]) rotate([ 0, 0, 270 ]) children();
        translate([ box_width, (box_length - tab_length) / 2, lid_height ]) rotate([ 0, 0, 90 ]) children();
    }

    if (make_tab_width)
    {
        translate([ (box_width - tab_length) / 2, 0, lid_height ]) children();
        translate([ (box_width + tab_length) / 2, box_length, lid_height ]) rotate([ 0, 0, 180 ]) children();
    }
}

// Section: SlidingBox
//   All the pieces for making sliding lids and different types of sliding lids/boxes.

// Module: SlidingLid()
// Description:
//   Creates a sliding lid for a sliding lid box, the children to this module are inserted into the lid.
//   This does all the right things on the edges, uses some
//   wiggle room to add in a buffer and also does a small amount of angling on the ends to make them easier
//   to insert.
// Usage:
//   SlidingLid(width=10, length=30, lid_height=3, wall_thickness = 2, lid_size_spacing = 0.2);
// Arguments:
//   width = the width of the box itself
//   length = the length of the box itself
//   lid_height = the height of the lid (defaults to 3)
//   wall_thickness = how wide the side walls are (defaults to 2)
//   lid_size_spacing = how much of an offset to use in generate the slides spacing on all four sides defaults to
//   {{m_piece_wiggle_room}}
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLid(width=100, length=100, lid_height=3, wall_thickness = 2)
//     translate([ 10, 10, 0 ])
//       LidMeshHex(width = 100, length = 100, lid_height = 3, boundary = 10, radius = 12);
module SlidingLid(width, length, lid_height = 3, wall_thickness = 2, lid_size_spacing = m_piece_wiggle_room)
{
    internal_build_lid(width, length, lid_height, wall_thickness)
    {
        difference()
        {
            // Lip and raised bit
            union()
            {
                translate([ wall_thickness / 2, wall_thickness / 2, 0 ])
                    cube([ width - 2 * (wall_thickness + lid_size_spacing), length - wall_thickness, lid_height ]);
                translate([ 0, 0, 0 ]) cube([
                    width - wall_thickness - lid_size_spacing, length - wall_thickness / 2, lid_height / 2 -
                    lid_size_spacing
                ]);
            }

            // Edge easing.
            translate([ -lid_size_spacing, length + wall_thickness / 2 + lid_size_spacing, -lid_height / 2 ])
                linear_extrude(height = lid_height + 10) yflip() right_triangle([ lid_size_spacing * 2, 15 ]);
            translate([
                width - wall_thickness - lid_size_spacing, length + wall_thickness + lid_size_spacing, -lid_height / 2
            ]) linear_extrude(height = lid_height + 10) xflip() yflip() right_triangle([ lid_size_spacing * 2, 15 ]);
            translate([
                lid_height / 2 - lid_size_spacing, length + wall_thickness / 2 + lid_size_spacing, lid_height -
                lid_size_spacing
            ]) linear_extrude(height = lid_height + 10) yflip() right_triangle([ lid_size_spacing * 2, 15 ]);
            translate([ width - 3.2 + lid_size_spacing, length + 1.1, lid_height - lid_size_spacing ])
                linear_extrude(height = lid_height + 10) xflip() yflip() right_triangle([ lid_size_spacing * 2, 15 ]);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: SlidingBoxLidWithLabel
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
// Usage:
//    SlidingBoxLidWithLabel(width = 100, length = 100, lid_height = 3, text_width = 60, text_length = 30, text_str
//    = "Trains", label_rotated = false);
// Arguments:
//    width = width of the box (outside dimension)
//    length = length of the box (outside dimension)
//    text_width = width of the text section
//    text_length = length of the text section
//    text_str = The string to write
//    lid_height = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (default 4)
//    label_rotated = if the label should be rotated (default false)
//    layout_width = space in the grid for the layout (default 12)
//    shape_width = with of the shape in the grid (default 12)
//    shape_type = type of the shape to generate on the lid (default SHAPE_TYPE_DENSE_HEX)
//    shape_thickness = thickness of the shape in the mesh (default 2)
// Topics: SlidingBox, SlidingLid
// Example:
//    SlidingBoxLidWithLabel(
//        width = 100, length = 100, lid_height = 3, text_width = 60,
//        text_length = 30, text_str = "Trains", label_rotated = false);
module SlidingBoxLidWithLabel(width, length, text_width, text_length, text_str, lid_height = 3, lid_boundary = 10,
                              shape_width = 12, border = 2, offset = 4, label_rotated = false, layout_width = 12,
                              shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2)
{
    SlidingLid(width, length, lid_height = lid_height)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_height = lid_height, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_length) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_length) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_height ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_height);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: MakeHexBoxWithSlidingLid()
// Description:
//   Creates a box with a specific number of hex spaces given the rows/cols and width of the pieces.  Useful
//   for making 18xx style boxes quickly.  Children to this are the same as children to the
//   {{MakeBoxWithSlidingLid()}}.
//   .
//   This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.
//   .
// See also: SlidingLidForHexBox(), SlidingLidWithLabelForHexBox()
// Usage:
//   MakeHexBoxWithSlidingLid(5, 7, 19, 1, 29);
// Arguments:
//   rows = number of rows to generate
//   cols = number of cols to generate
//   height = height of the box itsdle (outside height)
//   push_block_height = height of the raised bit in the middle to make removing easier
//   lid_height = height of the lid (defaults to 3)
//   wall_thickness = thickness of the walls (defaults to 2)
//   spacing = spacing between the hexes
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//   MakeHexBoxWithSlidingLid(rows = 5, cols = 2, height = 10, push_block_height = 0.75, tile_width = 29);
module MakeHexBoxWithSlidingLid(rows, cols, height, push_block_height, tile_width, lid_height = 3, wall_thickness = 2,
                                spacing = 0)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(rows * radius * 2 + wall_thickness * 2, cols * apothem * 2 + wall_thickness * 2, height,
                          lid_height = lid_height) 
    {
        HexGridWithCutouts(rows = rows, cols = cols, height = height, tile_width = tile_width, spacing = spacing,
                           wall_thickness = wall_thickness);
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: SlidingLidForHexBox()
// Description:
//   Creates a sliding lid for use with a hex box, sets up the sizes correctly to match the
//   the hex row/col set.
// See also: MakeHexBoxWithSlidingLid(), SlidingLidWithLabelForHexBox()
// Usage:
//   SlidingLidForHexBox(5, 7, 29);
// Arguments:
//   rows = number of rows to generate
//   cols = number of cols to generate
//   tile_width = width of the tiles
//   lid_height = height of the lid (defaults to 3)
//   wall_thickness = thickness of the walls (defaults to 2)
//   spacing = spacing between the hexes
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//   SlidingLidForHexBox(rows = 5, cols = 2, tile_width = 29);
module SlidingLidForHexBox(rows, cols, tile_width, lid_height = 3, wall_thickness = 2, spacing = 0)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    SlidingLid(width = rows * radius * 2 + wall_thickness * 2, length = cols * apothem * 2 + wall_thickness * 2,
               lid_height = lid_height)
    {
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: SlidingLidWithLabelForHexBox()
// Description:
//   This is a composite method that joins together the other pieces to make a simple lid with a label and a hex
//   grid. The children to this as also pulled out of the lid so can be used to build more complicated lids.
//   .
// See also: MakeHexBoxWithSlidingLid()
// Usage:
//    SlidingLidWithLabelForHexBox(rows = 3, cols = 4, tile_width = 29, lid_height = 3, text_width = 60, text_length
//    = 30, text_str = "Trains", label_rotated = false);
// Arguments:
//    rows = number of rows to generate
//    cols = number of cols to generate
//    tile_width = width of the tiles
//    lid_height = height of the lid (defaults to 3)
//    wall_thickness = thickness of the walls (defaults to 2)
//    spacing = spacing between the hexes
//    text_width = width of the text section
//    text_length = length of the text section
//    text_str = The string to write
//    lid_height = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (degault 4)
//    label_rotated = if the label should be rotated (default false)
//    wall_thickness = how wide the walls are (default 2)
//    layout_width = space in the grid for the layout (default 12)
//    shape_width = with of the shape in the grid (default 12)
//    shape_type = type of the shape to generate on the lid (default SHAPE_TYPE_DENSE_HEX)
//    shape_thickness = thickness of the shape in the mesh (default 2)
// Topics: SlidingBox, SlidingLid, Hex
// Example:
//    SlidingLidWithLabelForHexBox(
//        cols = 3, rows = 4, tile_width = 29, lid_height = 3, text_width = 60,
//        text_length = 30, text_str = "Trains", label_rotated = false);
module SlidingLidWithLabelForHexBox(rows, cols, tile_width, text_width, text_length, text_str, lid_height = 3,
                                    lid_boundary = 10, label_radius = 12, border = 2, offset = 4, label_rotated = false,
                                    wall_thickness = 2, layout_width = 12, shape_width = 12,
                                    shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2)
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);
    width = rows * radius * 2 + wall_thickness * 2;
    length = cols * apothem * 2 + wall_thickness * 2;

    SlidingLid(width, length, lid_height = lid_height, wall_thickness = wall_thickness)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_height = lid_height, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_length) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_length) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_height ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_height);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: MakeBoxWithSlidingLid()
// Description:
//   Makes a box with a sliding lid, this just creates the box itself with the cutouts for the
//   sliding lid pieces.  The children to this will be removed from inside the box and how to add
//   in the cutouts.
//   .
//   This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.
// Usage:
//   MakeBoxWithSlidingLid(50,100,20);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = thickness of the walls (default 2)
//   lid_height = height of the lid (default 3)
// Topics: SlidingBox
// Example:
//   MakeBoxWithSlidingLid(50, 100, 20);
module MakeBoxWithSlidingLid(width, length, height, wall_thickness = 2, lid_height = 3)
{
    difference()
    {
        cube([ width, length, height ]);
        translate([ wall_thickness, -1, height - lid_height ])
            cube([ width - wall_thickness * 2, length - wall_thickness + 1, lid_height + 0.1 ]);
        translate([ wall_thickness / 2, -1, height - lid_height ])
            cube([ width - wall_thickness, length - wall_thickness / 2 + 1, lid_height / 2 ]);

        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        intersection()
        {
            translate([ wall_thickness, wall_thickness, -1 ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 2 ]);
            translate([ wall_thickness, wall_thickness, wall_thickness ]) children();
        }
    }
}

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
//   width = the width of the box (outside width)
//   length = the length of the box (outside length)
//   lid_height = height of the lid (default 2)
//   wall_thickness = thickness of the walls (default 2)
//   inset = how far the side is inset from the edge of the box (default 1)
//   lid_size_spacing = how much wiggle room to give in the model (default {{m_piece_wiggle_room}})
// Topics: TabbedBox
// Example:
//  InsetLid(50, 100);
module InsetLid(width, length, lid_height = 2, wall_thickness = 2, inset = 1, lid_size_spacing = m_piece_wiggle_room)
{
    internal_build_lid(width, length, lid_height, wall_thickness, lid_size_spacing = lid_size_spacing)
    {
        translate([ wall_thickness - inset, wall_thickness - inset, 0 ])
            cube([ width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_height ]);
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: InsetLidTabbed()
// Description:
//   Makes an inset lid with the tabes on the side.
// Usage:
//   InsetLidTabbed(30, 100);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   lid_height = height of the lid (default 2)
//   wall_thickness = thickness of the walls (default 2)
//   inset = how far to inset the lid (default 1)
//   lid_size_spacing = the wiggle room in the lid generation (default {{m_piece_wiggle_room}})
//   make_tab_width = makes tabes on thr width (default false)
//   make_tab_length = makes tabs on the length (default true)
//   prism_width = width of the prism in the tab. (default 0.75)
//   tab_length = length of the tab (default 10)
//   tab_height = height of the tab (default 6)
// Topics: TabbedBox, TabbedLid
// Example:
//   InsetLidTabbed(30, 100);
module InsetLidTabbed(width, length, lid_height = 2, wall_thickness = 2, inset = 1,
                      lid_size_spacing = m_piece_wiggle_room, make_tab_width = false, make_tab_length = true,
                      prism_width = 0.75, tab_length = 10, tab_height = 6)
{
    union()
    {
        InsetLid(width = width, length = length, lid_height = lid_height, wall_thickness = wall_thickness,
                 inset = inset, lid_size_spacing = lid_size_spacing)
        {
            if ($children > 0)
            {
                children(0);
            }
            if ($children > 1)
            {
                children(1);
            }
            if ($children > 2)
            {
                children(2);
            }
            if ($children > 3)
            {
                children(3);
            }
            if ($children > 4)
            {
                children(4);
            }
            if ($children > 5)
            {
                children(5);
            }
        }
        MakeTabs(box_width = width, box_length = length, wall_thickness = wall_thickness, lid_height = lid_height,
                 make_tab_width = make_tab_width, make_tab_length = make_tab_length, prism_width = prism_width)
            MakeLidTab(length = tab_length, height = tab_height, lid_height = lid_height, prism_width = prism_width,
                       wall_thickness = wall_thickness);
        ;
    }
}

// Module: InsetLidTabbedWithLabel()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed lid with
//   a label and a hex grid. The children to this as also pulled out of the lid so can be used to
//   build more complicated lids.
// Usage:
//    InsetLidTabbedWithLabel(width = 100, length = 100, lid_height = 3, text_width = 60, text_length = 30, text_str
//    = "Trains", label_rotated = false);
// Arguments:
//    width = width of the box (outside dimension)
//    length = length of the box (outside dimension)
//    text_width = width of the text section
//    text_length = length of the text section
//    text_str = The string to write
//    lid_height = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (degault 4)
//    label_rotated = if the label should be rotated, default to false
//    tab_height = height of the tabs (default 6)
//    tab_length = length of the tabs (default 10)
//    inset = inset of the edge (default 1)
//    make_tab_width = makes tabes on thr width (default false)
//    make_tab_length = makes tabs on the length (default true)
//    prism_width = width of the prism in the tab. (default 0.75)
//    layout_width = space in the grid for the layout (default 12)
//    shape_width = with of the shape in the grid (default 12)
//    shape_type = type of the shape to generate on the lid (default SHAPE_TYPE_DENSE_HEX)
//    shape_thickness = thickness of the shape in the mesh (default 2)
// Topics: TabbedBox, TabbedLid
// Example:
//    InsetLidTabbedWithLabel(
//        width = 100, length = 100, lid_height = 3, text_width = 60,
//        text_length = 30, text_str = "Trains", label_rotated = false);
module InsetLidTabbedWithLabel(width, length, text_width, text_length, text_str, lid_height = 3, lid_boundary = 10,
                               label_radius = 12, border = 2, offset = 4, label_rotated = false, tab_length = 10,
                               tab_height = 6, make_tab_width = false, make_tab_length = true, prism_width = 0.75,
                               layout_width = 12, shape_width = 12, shape_type = SHAPE_TYPE_DENSE_HEX,
                               shape_thickness = 2)
{
    InsetLidTabbed(width, length, lid_height = lid_height, tab_length = tab_length, tab_height = tab_height)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_height = lid_height, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_length) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_length) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_height ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_height);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: InsetLidTabbedForHexBox()
// Description:
//   Creates a inset tabbed lid for use with a hex box, sets up the sizes correctly to match the
//   the hex row/col set.
// See also: MakeHexBoxWithInsetTabbedLid(), InsetLidTabbedWithLabelForHexBox()
// Usage:
//   InsetLidTabbedForHexBox(5, 7, 29);
// Arguments:
//   rows = number of rows to generate
//   cols = number of cols to generate
//   tile_width = width of the tiles
//   lid_height = height of the lid (defaults to 3)
//   wall_thickness = thickness of the walls (defaults to 2)
//   spacing = spacing between the hexes
//   tab_height = height of the tabs (default 6)
//   tab_length = length of the tabs (default 10)
//   inset = inset of the edge (default 1)
//   make_tab_width = makes tabes on thr width (default false)
//   make_tab_length = makes tabs on the length (default true)
//   prism_width = width of the prism in the tab. (default 0.75)
// Topics: TabbedBox, TabbedLid, Hex
// Example:
//   InsetLidTabbedForHexBox(rows = 5, cols = 2, tile_width = 29);
module InsetLidTabbedForHexBox(rows, cols, tile_width, lid_height = 3, wall_thickness = 2, spacing = 0, tab_height = 6,
                               tab_length = 10, inset = 1, make_tab_width = false, make_tab_length = true,
                               prism_width = 0.75)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    InsetLidTabbed(width = rows * radius * 2 + wall_thickness * 2, length = cols * apothem * 2 + wall_thickness * 2,
                   lid_height = lid_height, tab_height = tab_height, tab_length = tab_length, inset = 1)
    {
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: InsetLidTabbedWithLabelForHexBox()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed
//   lid with a label and a hex grid. The children to this as also pulled out of the lid so can be
//   used to build more complicated lids.
// See also: InsetLidTabbedForHexBox(), MakeHexBoxWithInsetTabbedLid()
// Usage:
//    InsetLidTabbedWithLabelForHexBox(rows = 3, cols = 4, tile_width = 29, lid_height = 3, text_width = 60,
//    text_length = 30, text_str = "Trains", label_rotated = false);
// Arguments:
//    rows = number of rows to generate
//    cols = number of cols to generate
//    tile_width = width of the tiles
//    lid_height = height of the lid (defaults to 3)
//    wall_thickness = thickness of the walls (defaults to 2)
//    spacing = spacing between the hexes
//    text_width = width of the text section
//    text_length = length of the text section
//    text_str = The string to write
//    lid_height = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (degault 4)
//    label_rotated = if the label should be rotated (default false)
//    wall_thickness = how wide the walls are (default 2)
//    layout_width = space in the grid for the layout (default 12)
//    shape_width = with of the shape in the grid (default 12)
//    shape_type = type of the shape to generate on the lid (default SHAPE_TYPE_DENSE_HEX)
//    shape_thickness = thickness of the shape in the mesh (default 2)
// Topics: TabbedBox, TabbedLid, Hex
// Example:
//    InsetLidTabbedWithLabelForHexBox(
//        cols = 3, rows = 4, tile_width = 29, lid_height = 3, text_width = 60,
//        text_length = 30, text_str = "Trains", label_rotated = false);
module InsetLidTabbedWithLabelForHexBox(rows, cols, tile_width, text_width, text_length, text_str, lid_height = 3,
                                        lid_boundary = 10, label_radius = 12, border = 2, offset = 4,
                                        label_rotated = false, wall_thickness = 2, tab_height = 6, tab_length = 10,
                                        inset = 1, layout_width = 12, shape_width = 12,
                                        shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2)
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);
    width = rows * radius * 2 + wall_thickness * 2;
    length = cols * apothem * 2 + wall_thickness * 2;

    InsetLidTabbed(width, length, lid_height = lid_height, wall_thickness = wall_thickness, tab_length = tab_length,
                   tab_height = tab_height, inset = inset)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_height = lid_height, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_length) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_length) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = lid_height, label = text_str,
                                    border = border, offset = offset);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_height ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_height);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Module: MakeBoxWithTabsInsetLid()
// Description:
//   Makes a box with an inset lid.  Handles all the various pieces for making this with tabs.  This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.  The children and moves so 0,0,0 is the bottom inside
//   of the box to make for easier arithmatic.
// Usage:
//   MakeBoxWithTabsInsetLid(width = 30, length = 100, height = 20);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = how thick the walls are (default 2)
//   lid_height = how hight the lid is (default 2)
//   tab_height = how heigh to make the tabs (default 6)
//   inset = how far to inset the lid (default 1)
//   make_tab_width = make the tabs on the width (default false)
//   make_tab_length = make the tabs on the length (default true)
//   prism_width = width of the prism to generate (default 0.75)
//   tab_length = how long the tab is (default 10)
//   stackable = should we pull a piece out the bottom of the box to let this stack (default false)
//   lid_size_spacing = wiggle room to use when generatiung box (default {{m_piece_wiggle_room}})
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeBoxWithTabsInsetLid(width = 30, length = 100, height = 20);
module MakeBoxWithTabsInsetLid(width, length, height, wall_thickness = 2, lid_height = 2, tab_height = 6, inset = 1,
                               make_tab_width = false, make_tab_length = true, prism_width = 0.75, tab_length = 10,
                               stackable = false, lid_size_spacing = m_piece_wiggle_room)
{
    difference()
    {
        cube([ width, length, height ]);
        translate([ wall_thickness - inset, wall_thickness - inset, height - lid_height ]) cube([
            width - (wall_thickness - inset + m_piece_wiggle_room) * 2,
            length - (wall_thickness - inset + m_piece_wiggle_room) * 2, lid_height + 0.1
        ]);
        translate([ 0, 0, height - lid_height ])
            MakeTabs(box_width = width, box_length = length, wall_thickness = wall_thickness, lid_height = lid_height,
                     tab_length = tab_length, prism_width = prism_width, make_tab_length = make_tab_length,
                     make_tab_width = make_tab_width) minkowski()
        {
            translate([ -m_piece_wiggle_room / 2, -m_piece_wiggle_room / 2, -m_piece_wiggle_room / 2 ])
                cube(m_piece_wiggle_room);
            MakeLidTab(length = tab_length, height = tab_height, lid_height = lid_height, prism_width = prism_width,
                       wall_thickness = wall_thickness);
        }

        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        intersection()
        {
            translate([ wall_thickness, wall_thickness, -1 ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 2 ]);
            translate([ wall_thickness, wall_thickness, wall_thickness ]) children();
        }
        // Cuff off the bit on the bottom to allow for stacking.
        if (stackable)
        {
            difference()
            {
                translate([ -0.5, -0.5, -0.5 ])
                    cube([ width + 1, length + 1, wall_thickness + 0.5 - lid_size_spacing ]);
                translate([ wall_thickness - inset + lid_size_spacing, wall_thickness - inset + lid_size_spacing, -1 ])
                    cube([
                        width - (wall_thickness - inset + lid_size_spacing) * 2,
                        length - (wall_thickness - inset + lid_size_spacing) * 2, wall_thickness + 2
                    ]);
            }
        }
    }
}

// Module: MakeHexBoxWithInsetTabbedLid()
// Description:
//   Makes a hex box with an inset lid, this is a useful combination box for 18xx style games.
// See also: InsetLidTabbedWithLabelForHexBox(), InsetLidTabbedForHexBox()
// Usage:
//   MakeHexBoxWithInsetTabbedBox, TabbedLid(rows = 4, cols = 3, height = 15, push_block_height = 1, tile_width =
//   29);
// Arguments:
//   rows = number of rows in the box
//   cols = number of cols in the box
//   height = height of the box (outside height)
//   push_block_height = height of the push blocks
//   tile_width = the width of the files
//   lid_height = height of the lid (default 2)
// Topics: TabbedBox, TabbedLid, Hex
// Example:
//   MakeHexBoxWithInsetTabbedLid(rows = 4, cols = 3, height = 15, push_block_height = 1, tile_width = 29);
module MakeHexBoxWithInsetTabbedLid(rows, cols, height, push_block_height, tile_width, lid_height = 2)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithTabsInsetLid(rows * radius * 2 + 4, cols * apothem * 2 + 4, height, stackable = true,
                            lid_height = lid_height) 
        RegularPolygonGrid(width = width, rows = rows, cols = cols, spacing = 0, shape_edges = 6)
    {
        union()
        {
            difference()
            {
                RegularPolygon(width = width, height = 10 + height, shape_edges = 6);
                RegularPolygon(width = 15, height = push_block_height, shape_edges = 6);
            }

            translate([ 0, apothem, 0 ]) cuboid([ radius, 10, 35 ], anchor = BOT);

            // Put in all the finger holes in the grid.
            translate([ radius + 1, -apothem, -6 ]) cuboid([ radius + 2, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ radius + 1, apothem, -6 ]) cuboid([ radius + 2, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ -radius + 1, -apothem, -6 ]) cuboid([ radius + 2, 15, radius * 2 ], anchor = BOT, rounding = 3);
            translate([ -radius + 1, apothem, -6 ]) cuboid([ radius + 2, 15, radius * 2 ], anchor = BOT, rounding = 3);
        }
    }
}

// Section: SlipBox
// Description:
//    A box that slips over the outside of an inner box.

// Module: MakeSlipBox()
// Description:
//    Makes the inside of the slip box, this will take a second lid that slides over the outside of the box.
// Usage: MakeSlipBox(100, 50, 10);
// Arguments:
//   width = outside width of the box
//   height = outside height of the box
//   wall_thickness = thickness of the walls (default 2)
//   foot = how big the foot should be around the bottom of the box (default 0)
//   size_spacing = amount of wiggle room to put into the model when making it (default {{m_wiggle_room}})
//   wall_height = height of the wall if not set (default height - wall_thickness*2 - size_spacing*2)
// Example:
//   MakeSlipBox(100, 50, 10);
module MakeBoxWithSlipoverLid(width, length, height, wall_thickness = 2, foot = 0, size_spacing = m_piece_wiggle_room,
                              wall_height = undef)
{
    wall_height_calc = wall_height == undef ? height - wall_thickness * 2 + size_spacing : wall_height;
    difference()
    {
        union()
        {
            translate([ wall_thickness + size_spacing, wall_thickness + size_spacing, 0 ]) cube([
                width - wall_thickness * 2 - size_spacing * 2, length - wall_thickness * 2 - size_spacing * 2,
                wall_height_calc
            ]);
            if (foot > 0)
            {
                cube([ width, length, foot ]);
            }
        }
        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        intersection()
        {
            translate([ wall_thickness * 2 + size_spacing, wall_thickness * 2 + size_spacing, -1 ])

                cube([
                    width - wall_thickness * 4 - size_spacing * 2, length - wall_thickness * 4 - size_spacing * 2,
                    height + 2
                ]);
            translate([ wall_thickness * 2 + size_spacing, wall_thickness * 2 + size_spacing, wall_thickness ])
                children();
        }
    }
}

// Module: SlipoverBoxLid()
// Description:
//   Make a box with a slip lid, a lid that slips over the outside of a box.
// Usage: SlipBoxLid(100, 50, 10);
// Arguments:
//   width = width of the lid (outside width)
//   length = of the lid (outside length)
//   height = height of the lid (outside height)
//   wall_thickness = how thick the walls are (default 2)
//   size_spacing = how much to offset the pieces by to give some wiggle room (default {{m_piece_wiggle_room}})
//   foot = size of the foot on the box.
// Example:
//   SlipoverBoxLid(100, 50, 10);
module SlipoverBoxLid(width, length, height, wall_thickness = 2, size_spacing = m_piece_wiggle_room, foot = 0)
{
    foot_offset = foot > 0 ? foot + size_spacing : 0;
    union()
    {
        translate([ 0, 0, height - foot_offset ]) internal_build_lid(width, length, wall_thickness, wall_thickness)
        {
            difference()
            {
                // Top piece
                cube([ width, length, wall_thickness ]);
            }
            if ($children > 0)
            {
                children(0);
            }
            if ($children > 1)
            {
                children(1);
            }
            if ($children > 2)
            {
                children(2);
            }
            if ($children > 3)
            {
                children(3);
            }
            if ($children > 4)
            {
                children(4);
            }
            if ($children > 5)
            {
                children(5);
            }
        }
        difference()
        {
            cube([ width, length, height - foot_offset ]);
            translate([ wall_thickness, wall_thickness, -0.5 ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 1 ]);
        }
    }
}

module SlipoverLidWithLabel(width, length, height, text_width, text_length, text_str, lid_boundary = 10,
                            wall_thickness = 2, label_radius = 12, border = 2, offset = 4, label_rotated = false,
                            foot = 0, layout_width = 12, shape_width = 12, shape_type = SHAPE_TYPE_DENSE_HEX,
                            shape_thickness = 2)
{
    SlipoverBoxLid(width = width, length = length, height = height, wall_thickness = wall_thickness, foot = foot)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_height = wall_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_length) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = wall_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_length) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_length, lid_height = wall_thickness,
                                    label = text_str, border = border, offset = offset);
        }
        if ($children > 0)
        {
            children(0);
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Section: Dividers
// Description:
//    Dividers for putting in between cards or other things where you want to divide up a set of items into
//    various groups.

// Module: MakeDividerTab()
// Description:
//   Makes a divider tab tab section with nice curves in and out of the tab.  Any children to this are
//   diffed out of the tab.
// Usage: MakeDividerTab(10, 20, 1);
// See also: MakeDivider(), MakeDividerWithText()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
// Example:
//   MakeDividerTab(10, 20, 1);
// Example:
//   // Divider tab with a svg image in it.
//   MakeDividerTab(10, 20, 1)  translate([ 6, 5, -2 ]) mirror([ 0, 1, 0 ])
//       linear_extrude(height = 4) offset(delta = 0.001) scale(0.04) import("svg/australia.svg");
module MakeDividerTab(tab_height, tab_length, thickness, tab_radius = 2)
{
    difference()
    {
        translate([ 0, tab_height, 0 ]) union()
        {
            cuboid([ tab_length, tab_height, thickness ], rounding = tab_radius,
                   edges = [ FRONT + LEFT, FRONT + RIGHT ], anchor = BACK + LEFT + BOTTOM, $fn = 20);
            translate([ -tab_radius, 0, 0 ]) difference()
            {
                cuboid([ tab_length + tab_radius * 2, tab_radius, thickness ], anchor = BACK + LEFT + BOTTOM);
                translate([ 0, -tab_radius, 0.5 ]) cyl(r = tab_radius, h = thickness + 1, $fn = 20);
                translate([ tab_length + tab_radius * 2, -tab_radius, 0.5 ])
                    cyl(r = tab_radius, h = thickness + 1, $fn = 20);
            }
        }
        children();
    }
}

// Module: MakeDivider()
// Description:
//   Makes a divider with a tab section up the top.  First child is a diff to the tab, the rest is a diff to
//   the main body of the tab.
// Usage: MakeDivider(10, 20, 1, 5, 3, 0);
// See also: MakeDividerTab(), MakeDividerWithText()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
//   num_tabs = number of tabs across the top
//   tab_position = the position number of the tab, 0..num_tabs-1
// Example:
//   MakeDivider(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 0, tab_radius
//   = 2);
// Example:
//   MakeDivider(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1, tab_radius
//   = 2);
// Example:
//   MakeDivider(width = 80, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1, tab_radius
//   = 2);
// Example:
//   // Divider with a svg image in it.
//   MakeDivider(70, 50, 1, tab_height = 5, tab_position = 0, num_tabs = 3)  translate([ 6, 5, -2 ]) mirror([ 0, 1,
//   0 ])
//       linear_extrude(height = 4) offset(delta = 0.001) scale(0.04) import("svg/australia.svg");
module MakeDivider(width, length, thickness, tab_height, num_tabs, tab_position, tab_radius = 2, num_tabs = 3,
                   tab_length = undef, hole_offset = 6)
{
    assert(tab_position >= 0 && tab_position < num_tabs, "Tab position must be lower than num_tabs");
    tab_length_calc = tab_length == undef ? (width - tab_radius * num_tabs) / num_tabs : tab_length;
    spacing = (width - tab_length_calc) / (num_tabs - 1);
    assert(tab_length_calc > 0, "tab_length_calc must be > 0");
    hole_width = width > 40 ? (width - 4 * hole_offset) / 3 : (width - 3 * hole_offset) / 2;
    hole_height = length - tab_height - hole_offset * 2;
    num_holes = width > 40 ? 3 : 2;
    intersection()
    {
        cube([ width, length, thickness ]);
        union()
        {
            translate([ spacing * tab_position, 0, 0 ])
            {
                MakeDividerTab(tab_height = tab_height, tab_length = tab_length_calc, thickness = thickness,
                               tab_radius = tab_radius) if ($children == 1)
                {
                    children();
                }
                else if ($children > 1) children(0);
            }
            difference()
            {
                cube([ width, length, thickness ]);
                translate([ -0.5, -1, -0.5 ]) cube([ width + 1, tab_height + 1, thickness + 1 ]);

                // Cut out holes in the middle.
                for (i = [0:1:num_holes - 1])
                    translate([ hole_offset + (hole_width + hole_offset) * i, length - hole_offset, -0.5 ])
                        cuboid([ hole_width, hole_height, thickness + 1 ], rounding = tab_radius,
                               edges = [ FRONT + LEFT, FRONT + RIGHT ], anchor = BACK + LEFT + BOTTOM, $fn = 20);
                if ($children > 2)
                {
                    for (i = [1:$children - 1])
                    {
                        children(i);
                    }
                }
            }
        }
    }
}

// Module: MakeDividerWithText()
// Description:
//   Makes a divider with a tab section up the top.  First child is a diff to the tab, the rest is a diff to
//   the main body of the tab.
// Usage: MakeDividerWithText(10, 20, 1, 5, 3, 0);
// See also: MakeDivider(), MakeDividerTab()
// Topics: Dividers
// Arguments:
//   tab_height = height of the tab
// . tab_length = length of the tab
//   thickness = how thick the tab is (z height)
//   tab_radius = the radius of the curve to use
//   num_tabs = number of tabs across the top
//   tab_position = the position number of the tab, 0..num_tabs-1
//   text_str = the text string to use
//   text_offset = how far from the sides of the tab to put the text
//   text_height = how hight the text is, (default tab_height - text_offset)
//   font = the font to use (default "Stencil Std:style=Bold")
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 0,
//   text_str = "Frog");
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 1,
//   text_str = "Bing");
// Example:
//   MakeDividerWithText(width = 40, length = 70, thickness = 1, tab_height = 10, num_tabs = 3, tab_position = 2,
//   text_str = "Croak", text_depth=0.5);
module MakeDividerWithText(width, length, thickness, tab_height, text_str, num_tabs, tab_position, tab_radius = 2,
                           num_tabs = 3, tab_length = undef, text_offset = 2, text_height = undef, text_depth = undef,
                           font = "Stencil Std:style=Bold")
{
    assert(tab_position >= 0 && tab_position < num_tabs, "Tab position must be lower than num_tabs");
    tab_length_calc = tab_length == undef ? (width - tab_radius * num_tabs) / num_tabs : tab_length;
    text_width = tab_length_calc - text_offset * 2;
    text_height_calc = text_height == undef ? tab_height - text_offset : text_height;
    text_depth_calc = text_depth == undef ? thickness + 1 : text_depth;
    MakeDivider(width = width, length = length, thickness = thickness, tab_height = tab_height, tab_length = tab_length,
                num_tabs = num_tabs, tab_position = tab_position, tab_radius = tab_radius)
    {
        union()
        {
            translate([ text_offset, tab_height - text_offset * 1 / 4, thickness - text_depth_calc ])
                linear_extrude(height = text_depth_calc + 0.5) resize([ text_width, text_height_calc, 0 ], auto = true)
                    text(text = str(text_str), font = font, size = 10, spacing = 1, halign = "right", valign = "bottom",
                         spin = 180);
            if ($children > 0)
            {
                children(0);
            }
        }
        if ($children > 1)
        {
            children(1);
        }
        if ($children > 2)
        {
            children(2);
        }
        if ($children > 3)
        {
            children(3);
        }
        if ($children > 4)
        {
            children(4);
        }
        if ($children > 5)
        {
            children(5);
        }
    }
}

// Section: Curves
// Description:
//   Space filling curves to use on the lids and other places.

// Module: HilbertCurve()
// Description:
//   Generates a hilbert curve for uses in board games.
// Usage: HilbertCurve(3, 100);
// Arguments:
//   order = depth of recursion to use 3 is a reasonable number
//   size = size to generate the curve, this is a square size
//   line_thickness = how thick to generate the lines in the curve (default = 20)
//   smoothness = how smooth to make all the curves (default 32)
// Example:
//   HilbertCurve(3, 100);
module HilbertCurve(order, size, line_thickness = 20, smoothness = 32)
{

    module topline(order)
    {
        if (order > 0)
        {
            scale([ 0.5, 0.5 ]) topline(order - 1);
        }
        else
        {
            hull()
            {
                translate([ -size / 2, size / 2 ]) circle(d = line_thickness);
                translate([ size / 2, size / 2 ]) circle(d = line_thickness);
            };
        }
    }

    module leftline(order)
    {
        if (order > 0)
        {
            scale([ 0.5, 0.5 ]) translate([ -size, 0 ]) leftline(order - 1);
        }
        else
        {
            hull()
            {
                translate([ -size / 2, size / 2 ]) circle(d = line_thickness);
                translate([ -size / 2, -size / 2 ]) circle(d = line_thickness);
            };
        }
    }

    module rightline(order)
    {
        if (order > 0)
        {
            scale([ 0.5, 0.5 ]) translate([ size, 0 ]) rightline(order - 1);
        }
        else
        {
            hull()
            {
                translate([ size / 2, size / 2 ]) circle(d = line_thickness);
                translate([ size / 2, -size / 2 ]) circle(d = line_thickness);
            };
        }
    }

    module hilbert(order)
    {

        if (order > 0)
        {
            union()
            {
                translate([ size / 2, size / 2 ]) scale([ 0.5, 0.5 ]) hilbert(order - 1);
                translate([ -size / 2, size / 2 ]) scale([ 0.5, 0.5 ]) hilbert(order - 1);
                translate([ size / 2, -size / 2 ]) rotate([ 0, 0, 90 ]) scale([ 0.5, 0.5 ]) hilbert(order - 1);
                translate([ -size / 2, -size / 2 ]) rotate([ 0, 0, -90 ]) scale([ 0.5, 0.5 ]) hilbert(order - 1);
                topline(order);
                leftline(order);
                rightline(order);
            };
        }
        else
            union()
            {
                hull()
                {
                    translate([ size / 2, size / 2 ]) circle(d = line_thickness);
                    translate([ size / 2, -size / 2 ]) circle(d = line_thickness);
                };
                hull()
                {
                    translate([ -size / 2, size / 2 ]) circle(d = line_thickness);
                    translate([ -size / 2, -size / 2 ]) circle(d = line_thickness);
                };
                hull()
                {
                    translate([ -size / 2, size / 2 ]) circle(d = line_thickness);
                    translate([ size / 2, size / 2 ]) circle(d = line_thickness);
                };
            };
    }
    hilbert(order);
}