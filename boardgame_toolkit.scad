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
 
include <BOSL2/rounding.scad>
include <BOSL2/std.scad>

// How many mm to use as gaps for when things join.
m_piece_wiggle_room = 0.2;

// The font to use for the lids by default.
m_default_font = "Stencil Std:style=Bold";

module RoundedBoxOnLength(width, length, height, radius)
{
    hull()
    {
        difference()
        {
            hull()
            {
                translate([ 0, radius, 0 ]) cyl(l = width, r = radius, anchor = BOTTOM + RIGHT, spin = [ 0, 90, 0 ]);

                translate([ 0, length - radius, 0 ])
                    cyl(l = width, r = radius, anchor = BOTTOM + RIGHT, spin = [ 0, 90, 0 ]);
            }
            translate([ -0.5, -0.5, radius ]) cube([ width + 1, length + 1, radius + 1 ]);
        }

        translate([ 0, 0, height - 1 ]) cube([ width, length, 1 ]);
    }
}

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

module RoundedBoxGrid(width, length, height, radius, rows, cols, spacing = 2, all_sides = false)
{
    row_length = (length - spacing * (rows - 1)) / rows;
    col_length = (width - spacing * (cols - 1)) / cols;
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

module regular_polygon(shape_edges = 4, radius = 1)
{
    angles = [for (i = [0:shape_edges - 1]) i * (360 / shape_edges)];
    coords = [for (th = angles)[radius * cos(th), radius * sin(th)]];
    polygon(coords);
}

module RegularPolygon(width, height, shape_edges)
{
    apothem = width / 2;
    radius = apothem / cos(180 / shape_edges);
    rotate_deg = ((shape_edges % 2) == 1) ? 180 / shape_edges + 90 : (shape_edges == 4 ? 45 : 0);

    rotate([ 0, 0, rotate_deg ]) linear_extrude(height = height)
        regular_polygon(shape_edges = shape_edges, radius = radius);
}

// Lays out the grid with all the polygons as children.  The layout handles any shape as children.
module RegularPolygonGrid(width, rows, cols, spacing, shape_edges = 6)
{
    apothem = width / 2;
    radius = apothem / cos(180 / shape_edges);
    side_length = 2 * apothem * tan(180 / shape_edges);
    extra_edge = 2 * side_length * cos(360 / shape_edges);

    dx = ((shape_edges % 2) == 1) ? apothem + radius + spacing : apothem * 2 + spacing;
    dy = (shape_edges % 2) == 0 ? ((shape_edges / 2 % 2) == 1 ? radius * 2 + spacing : apothem * 2 + spacing)
                                : abs(2 * apothem * sin(((shape_edges - 1) / (shape_edges * 2)) * 360)) * 2 + spacing;
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

// This does a dense layout, only works with triangles and hexes.  The children are laid out
// in the grid, so allow for stuff to happen.
module RegularPolygonGridDense(width, rows, cols, spacing, shape_edges = 6)
{
    apothem = width / 2;
    radius = apothem / cos(180 / shape_edges);
    side_length = 2 * apothem * tan(180 / shape_edges);
    extra_edge = 2 * side_length * cos(360 / shape_edges);

    dx = (shape_edges == 3) ? apothem + apothem + spacing / 2 : apothem + spacing;
    col_x = apothem + radius + spacing;
    dy = (shape_edges == 3) ? side_length / 2 + spacing / 2 : 0.75 * (radius + radius) + spacing;

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
                translate([ i * dy, (i % 2) == 1 ? j * col_x : (j * col_x) + 0.5 * dx, 0 ])
                {
                    children();
                }
            }
}

// Make a hex mesh for the lid.
module LidMeshHex(width, length, lid_height, boundary, radius, shape_thickness = 2)
{
    cell_width = cos(180 / 6) * radius;
    rows = width / cell_width;
    cols = length / cell_width;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_height) RegularPolygonGridDense(
                width = radius + 1, rows = rows, cols = cols, spacing = shape_thickness, shape_edges = 6) difference()
            {
                regular_polygon(radius = cell_width, shape_edges = 6);
                regular_polygon(radius = cell_width - shape_thickness, shape_edges = 6);
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

// Make a mesh for the lid with a repeating box shape.
module LidMeshRepeating(width, length, lid_height, boundary, shape_width)
{
    rows = width / shape_width;
    cols = length / shape_width;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_height)
                RegularPolygonGrid(width = shape_width, rows = rows + 1, cols = cols + 1, spacing = 0, shape_edges = 4)
            {
                children();
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

module MakeLidTab(wall_thickness, length, height, lid_height, prism_width)
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

module MakeTabs(box_width, box_length, wall_thickness, lid_height, tab_length = 10, make_tab_width = false,
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

module MakeInsetLid(width, length, lid_height, wall_thickness, inset = 1, lid_size_spacing = m_piece_wiggle_room)
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

module MakeStripedGrid(x, y, w = 1)
{
    dx = w * 2;

    x_count = (x + y) / (w + dx);

    intersection()
    {
        square([ x, y ]);
        for (j = [0:x_count])
        {

            translate([ j * (w + dx), 0 ]) rotate([ 0, 0, 45 ]) square([ w, y * 2 ]);
        }
    }
}

module MakeStripedLidLabel(width, length, lid_height, label, border, offset, font = "Stencil Std:style=Bold",
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
            linear_extrude(height = lid_height / 2) MakeStripedGrid(x = width, y = length);
        }
    }
}

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
            children();
        }
    }
}

module MakeBoxWithInsetLid(width, length, height, wall_thickness = 2, lid_height = 2, tab_height = 6, inset = 1,
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
            MakeLidTab(wall_thickness, tab_length, tab_height, lid_height, prism_width);
        }

        // Make sure the children are only in the area of the inside of the box, can make holes in the bottom
        // just not the walls.
        intersection()
        {
            translate([ wall_thickness, wall_thickness, -1 ])
                cube([ width - wall_thickness * 2, length - wall_thickness * 2, height + 2 ]);
            children();
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

module MakeHexBoxWithInsetLid(rows, cols, height, push_block_height, tile_width, lid_height = 2)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    echo(rows * radius * 2 + 4);
    echo(cols * apothem * 2 + 4);

    MakeBoxWithInsetLid(rows * radius * 2 + 4, cols * apothem * 2 + 4, height, stackable = true,
                        lid_height = lid_height) translate([ 2, 2, 2 ])
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

module HexGridWithCutouts(rows, cols, height, spacing, tile_width, push_block_height, wall_thickness = 2)
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

module MakeHexBoxWithSlidingLid(rows, cols, height, push_block_height, tile_width, lid_height = 3, wall_thickness = 2)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithSlidingLid(rows * radius * 2 + wall_thickness * 2, cols * apothem * 2 + wall_thickness * 2, height,
                          lid_height = lid_height) translate([ wall_thickness, wall_thickness, wall_thickness ])
        HexGridWithCutouts(rows = rows, cols = cols, height = height, tile_width = tile_width, spacing = spacing,
                           wall_thickness = wall_thickness);
}

module SlidingLidFingernail(radius, lid_height, finger_gap = 1.5, sphere = 12, finger_length = 10)
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

module SlidingBoxLidWithLabel(width, length, lid_height, text_width, text_length, text_str, label_boundary = 10,
                              label_radius = 12, border = 2, offset = 4, label_rotated = false)
{
    SlidingLid(width, length, lid_height = lid_height)
    {

        translate([ 10, 10, 0 ])
            LidMeshHex(width = width, length = length, lid_height = lid_height, boundary = 10, radius = 12);
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
            cube([ width-border, length-border, lid_height ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(6, lid_height);
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
