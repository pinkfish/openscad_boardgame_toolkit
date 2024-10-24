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

// LibFile: components.scad
//    This file has all the modules needed to generate varioius inserts
//    for board games.  It makes the generation of the inserts simpler by
//    creating a number of useful base modules for making boxes and lids
//    of various types specific to board game inserts.  Specifically it
//    makes tabbed lids and sliding lids easily.
//

// FileSummary: Various modules to generate board game inserts.
// FileGroup: Basics

// Includes:
//   include <boardgame_toolkit.scad>

assert(version_num() >= 20190500, "boardgame_toolkit requires OpenSCAD version 2019.05 or later.");

include <BOSL2/rounding.scad>
include <BOSL2/std.scad>
include <base_bgtk.scad>

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

    intersection()
    {
        // Narrow it down to being inside the box itself.
        translate([ 0, 0, -10 ]) cube([ rows * (radius * 2 + spacing), cols * (apothem * 2 + spacing), height + 20 ]);
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
