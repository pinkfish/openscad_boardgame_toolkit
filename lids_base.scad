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

// LibFile: lids_base.scad
//    This file has all the shared lid pieces for making lids.

// FileSummary: Shared lid pieces for making lids.
// FileGroup: Basics

// Includes:
//   include <boardgame_toolkit.scad>

// Section: Lid
//   Building blocks for making various kinds of lids and labels.

// Constant: default_lid_shape_width
// Description: Set this at the top of the file to change the default shape width of the box lid.
default_lid_shape_width = 12;
// Constant: default_lid_layout_width
// Description: Set this at the top of the file to change the default layout width of the box lid.
default_lid_layout_width = 12;
// Constant: default_lid_aspect_ratio
// Description: Set this at the top of the file to change the default aspect ratio of the box lid.
default_lid_aspect_ratio = 1.0;
// Constant: default_lid_shape_thickness
// Description: Set this at the top of the file to change the default shape_thickness of the box lid.
default_lid_shape_thickness = 2;
// Constant: default_lid_shape_rounding
// Description: Set this at the top of the file to change the default rounding of the box lid.
default_lid_shape_rounding = 0;
// Constant: default_lid_shape_type
// Description: Set this at the top of the file to change the default shape type of the box lid.
default_lid_shape_type = SHAPE_TYPE_DENSE_HEX;
// Constant: default_lid_supershape_m1
// Description: Set this at the top of the file to change the default supershape m1 element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_m1 = 4;
// Constant: default_lid_supershape_m2
// Description: Set this at the top of the file to change the default supershape m]2 element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_m2 = 4;
// Constant: default_lid_supershape_n1
// Description: Set this at the top of the file to change the default supershape n1 element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_n1 = 1;
// Constant: default_lid_supershape_n2
// Description: Set this at the top of the file to change the default supershape n2 element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_n2 = 1;
// Constant: default_lid_supershape_n3
// Description: Set this at the top of the file to change the default supershape n3 element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_n3 = 1;
// Constant: default_lid_supershape_a
// Description: Set this at the top of the file to change the default supershape a element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_a = 1;
// Constant: default_lid_supershape_b
// Description: Set this at the top of the file to change the default supershape b element
// for [Superformula](https://en.wikipedia.org/wiki/Superformula) shape
default_lid_supershape_b = 1;

// Module: CloudShape()
// Description:
//   Makes a cloud object.  This object was made by Twanne on thingiverse:
//   https://www.thingiverse.com/thing:641665/files
// Arguments:
//   width = The width of the cloud. This also determine the height, because the height is half the width.
//   height = Height of the object.
//   line_width = width of the outside line (0 if no line)
// Example:
//   CloudShape(100);
module CloudShape(width)
{
    union()
    {
        translate([ width * .37, width * .25, 0 ]) circle(r = width * .25, $fn = 16);
        translate([ width * .15, width * .2, 0 ]) circle(r = width * .15, $fn = 16);
        translate([ width * .65, width * .22, 0 ]) circle(r = width * .2, $fn = 16);
        translate([ width * .85, width * .2, 0 ]) circle(r = width * .15, $fn = 16);
    }
}

// Module: LidMeshDense()
// Description:
//   Make a hex mesh for the lid.  This makes a nice pattern for use on the lids.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_thickness = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   radius = the radius of the polygon to create
//   shape_thickness = how thick to generate the gaps between the hexes (default 2)
//   shape_edges = number of edges for the shape (default 6)
//   offset = how much to offset the shape, so you can do overlapping shapes (default 0)
// Usage:
//   LidMeshDense(width = 70, length = 50, lid_thickness = 3, boundary = 10, radius = 5, shape_thickness = 2,
//   shape_edges = 6);
// Topics: PatternFill
// Example:
//   LidMeshDense(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10, shape_thickness = 2,
//   shape_edges = 6);
// Example:
//   LidMeshDense(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10, shape_thickness = 2,
//   shape_edges = 3);
module LidMeshDense(width, length, lid_thickness, boundary, radius, shape_thickness = 2, shape_edges = 6, offset = 0,
                    rounding = 0)
{
    cell_width = cos(180 / shape_edges) * radius;
    rows = width / cell_width;
    cols = length / cell_width;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_thickness + 1)
                RegularPolygonGridDense(radius = radius, rows = rows, cols = cols, shape_edges = shape_edges)
                    difference()
            {
                regular_ngon(or = radius + shape_thickness / 2 + offset, n = shape_edges, rounding = rounding);
                regular_ngon(or = radius - shape_thickness / 2 + offset, n = shape_edges, rounding = rounding);
            }

            difference()
            {
                cube([ width - boundary * 2, length - boundary * 2, lid_thickness + 1 ]);
                translate([ shape_thickness / 2, shape_thickness / 2, 0 ]) cube([
                    width - boundary * 2 - shape_thickness, length - boundary * 2 - shape_thickness, lid_thickness + 1
                ]);
            }
        }
        cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
    }
}

// Module: LidMeshHex()
// Description:
//   Make a hex mesh for the lid.  This makes a nice pattern for use on the lids.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_thickness = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   radius = the radius of the polygon to create
//   shape_thickness = how thick to generate the gaps between the hexes
// Usage:
//   LidMeshHex(width = 70, length = 50, lid_thickness = 3, boundary = 10, radius = 5, shape_thickness = 2);
// Topics: PatternFill
// Example:
//   LidMeshHex(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10, shape_thickness = 2);
module LidMeshHex(width, length, lid_thickness, boundary, radius, shape_thickness = 2)
{
    LidMeshDense(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary, radius = radius,
                 shape_thickness = shape_thickness, shape_edges = 6);
}

// Module: LidMeshRepeating()
// Description:
//   Make a mesh for the lid with a repeating shape.  It uses the children of this to repeat the shape.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_thickness = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   shape_width = the width to use between each shape.
//   aspect_ratio = the aspect ratio (multiple by dy) (default 1.0)
//   shape_edges = the number of edges on the shape (default 4)
// Usage:
//   LidMeshRepeating(50, 20, 3, 5, 10);
// Topics: PatternFill
// Example:
//   LidMeshRepeating(width = 50, length = 50, lid_thickness = 3, boundary = 5, shape_width = 10)
//      difference() {
//        circle(r = 7);
//        circle(r = 6);
//      }
module LidMeshRepeating(width, length, lid_thickness, boundary, shape_width, aspect_ratio = 1.0, shape_edges = 4)
{
    rows = width / shape_width;
    cols = length / shape_width * aspect_ratio;

    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_thickness + 1)
                RegularPolygonGrid(width = shape_width, rows = rows + 1, cols = cols + 1, spacing = 0,
                                   shape_edges = shape_edges, aspect_ratio = aspect_ratio)
            {
                children();
            }
            difference()
            {
                translate([ 0, 0, -0.5 ]) cube([ width, length, lid_thickness + 1 ]);
                translate([ m_piece_wiggle_room, m_piece_wiggle_room, -0.5 + m_piece_wiggle_room ]) cube([
                    width - boundary * 2 - m_piece_wiggle_room * 2, length - boundary * 2 - m_piece_wiggle_room * 2,
                    lid_thickness + 1 + m_piece_wiggle_room * 2
                ]);
            }
        }
        cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
    }
}

// Module: LidMeshBasic()
// Description:
//   Creates a lid mesh with a set of known shapes.  The width is the width of the shape
//   for layout purposes and the shape_width is the width for generation purposes.  The layout
//   width and shape width default to being the same for dense layouts, and overlapping for
//   non-dense layouts.
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 11);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_DENSE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 14);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, shape_type =
//       SHAPE_TYPE_TRIANGLE, shape_thickness = 2, shape_width = 10);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_HEX, shape_thickness = 1, shape_width = 14);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 16);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 13, aspect_ratio=1.25);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 10.5, aspect_ratio=1);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
// Example:
//   default_lid_shape_rounding = 3;
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_CLOUD, shape_thickness = 2, shape_width = 11);
// Example(2D,Med):
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2);
// Example(2D,Big):
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10,
//       SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12, 
//       supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
module LidMeshBasic(width, length, lid_thickness, boundary, layout_width, shape_type, shape_width, shape_thickness,
                    aspect_ratio = 1.0, rounding = undef, supershape_m1 = undef, supershape_m2 = undef,
                    supershape_n1 = undef, supershape_n2 = undef, supershape_n3 = undef, supershape_a = undef,
                    supershape_b = undef)
{
    calc_layout_width = DefaultValue(layout_width, default_lid_layout_width);
    calc_shape_type = DefaultValue(shape_type, default_lid_shape_type);
    calc_shape_width = DefaultValue(shape_width, default_lid_shape_width);
    calc_shape_thickness = DefaultValue(shape_thickness, default_lid_shape_thickness);
    calc_aspect_ratio = DefaultValue(aspect_ratio, default_lid_aspect_ratio);
    calc_rounding = DefaultValue(rounding, default_lid_shape_rounding);
    calc_supershape_m1 = DefaultValue(supershape_m1, default_lid_supershape_m1);
    calc_supershape_m2 = DefaultValue(supershape_m2, default_lid_supershape_m2);
    calc_supershape_n1 = DefaultValue(supershape_n1, default_lid_supershape_n1);
    calc_supershape_n2 = DefaultValue(supershape_n2, default_lid_supershape_n2);
    calc_supershape_n3 = DefaultValue(supershape_n3, default_lid_supershape_n3);
    calc_supershape_a = DefaultValue(supershape_a, default_lid_supershape_a);
    calc_supershape_b = DefaultValue(supershape_b, default_lid_supershape_b);
    if (calc_shape_type == SHAPE_TYPE_NONE)
    {
        // Don't do anything.
    }
    else
    {
        // Thin border around the pattern to stick it on.

        if (calc_shape_type == SHAPE_TYPE_DENSE_HEX)
        {
            LidMeshDense(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                         radius = calc_layout_width / 2, shape_thickness = calc_shape_thickness, shape_edges = 6,
                         offset = calc_shape_width - calc_layout_width, rounding = calc_rounding);
        }
        else if (calc_shape_type == SHAPE_TYPE_DENSE_TRIANGLE)
        {
            LidMeshDense(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                         radius = calc_layout_width / 2, shape_thickness = calc_layout_width - calc_shape_width,
                         shape_edges = 3, offset = calc_shape_width - calc_layout_width, rounding = calc_rounding);
        }
        else if (calc_shape_type == SHAPE_TYPE_CIRCLE)
        {
            LidMeshRepeating(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                             shape_width = calc_layout_width, shape_edges = 4, aspect_ratio = calc_aspect_ratio)
                difference()
            {
                circle(r = calc_shape_width / 2);
                circle(r = (calc_shape_width - calc_shape_thickness) / 2);
            }
        }
        else if (calc_shape_type == SHAPE_TYPE_TRIANGLE || calc_shape_type == SHAPE_TYPE_HEX ||
                 calc_shape_type == SHAPE_TYPE_OCTOGON || calc_shape_type == SHAPE_TYPE_SQUARE)
        {
            shape_edges =
                calc_shape_type == SHAPE_TYPE_TRIANGLE
                    ? 3
                    : (calc_shape_type == SHAPE_TYPE_HEX ? 6 : (calc_shape_type == SHAPE_TYPE_SQUARE ? 4 : 8));
            LidMeshRepeating(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                             shape_width = calc_layout_width, shape_edges = shape_edges,
                             aspect_ratio = calc_aspect_ratio) difference()
            {
                regular_ngon(r = calc_shape_width / 2, n = shape_edges, rounding = calc_rounding);
                regular_ngon(r = (calc_shape_width - calc_shape_thickness) / 2, n = shape_edges,
                             rounding = calc_rounding);
            }
        }
        else if (calc_shape_type == SHAPE_TYPE_SUPERSHAPE)
        {
            LidMeshRepeating(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                             shape_width = calc_layout_width, shape_edges = 4,
                             aspect_ratio = calc_aspect_ratio) difference()
            {
                DifferenceWithOffset(offset = -calc_shape_thickness) supershape(
                    d = calc_shape_width, m1 = calc_supershape_m1, m2 = calc_supershape_m2, n1 = calc_supershape_n1,
                    n2 = calc_supershape_n2, n3 = calc_supershape_n3, a = calc_supershape_a, b = calc_supershape_b);
            }
        }
        else if (calc_shape_type == SHAPE_TYPE_HILBERT)
        {
            intersection()
            {
                difference()
                {
                    cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
                    translate([ max(width, length) / 2, max(width, length) / 2, -0.1 ])
                        linear_extrude(height = lid_thickness + 1) HilbertCurve(
                            order = 3, size = max(width, length) / 2, line_thickness = calc_shape_thickness);
                }
                cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
            }
        }
        else if (calc_shape_type == SHAPE_TYPE_CLOUD)
        {
            LidMeshRepeating(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                             shape_width = calc_layout_width, shape_edges = 4, aspect_ratio = calc_aspect_ratio)
                translate([ -calc_shape_width / 2, -calc_shape_width / 2, 0 ]) difference()
            {
                resize([ calc_shape_width * calc_aspect_ratio, calc_shape_width ])
                {
                    CloudShape(width = calc_shape_width);
                }
                offset(delta = -calc_shape_thickness) resize([ calc_shape_width * calc_aspect_ratio, calc_shape_width ])
                {
                    CloudShape(width = calc_shape_width);
                }
            }
        }
        else
        {
            assert(false, "Invalid shape type");
        }
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
//   SlidingLidFingernail(radius = 10, lid_thickness = 3);
// Arguments:
//   radius = radius of the circle the gap is in
//   lid_thickness = height of the lid
//   finger_gap = the space to make for a finger gap (default = 1.5)
//   sphere = the size of the sphere for the inset (default 12)
//   finger_length = the length of the finger section (default = 15)
// Topics: SlidingBox, SlidingLid
// Example:
//   SlidingLidFingernail(3);

module SlidingLidFingernail(lid_thickness, radius = 6, finger_gap = 1.5, sphere = 12, finger_length = 10)
{
    difference()
    {
        translate([ 0, 0, lid_thickness / 2 ]) cyl(h = lid_thickness, r = radius);
        translate([ 0, 0, finger_length + lid_thickness - finger_gap + 0.1 ]) intersection()
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
//   lid_thickness = the height of the lid (defaults to {{default_lid_thickness}})
//   prism_width = the width of the prism (defaults to 0.75)
//   wall_thickness = the thickness of the walls (default 2)
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeLidTab(length = 5, height = 10, lid_thickness = 2, prism_width = 0.75, wall_thickness = 2);
module MakeLidTab(length, height, lid_thickness = default_lid_thickness, prism_width = 0.75, wall_thickness = 2)
{
    mirror([ 0, 0, 1 ])
    {
        // square part, join to the lid.
        cube([ length, wall_thickness, lid_thickness ]);

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
//   MakeTabs(50, 100, wall_thickness = 2, lid_thickness = 2);
// Arguments:
//   box_width = width of the box (outside size)
//   box_length = length of the box (outside size)
//   lid_thickness = the height of the lid (default = default_lid_thickness)
//   tab_length = how long the tab is (default = 10)
//   make_tab_width = make tabs on the width side (default false)
//   make_tab_length = make tabs on the length side (default true)
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeTabs(50, 100)
//     MakeLidTab(length = 10, height = 6);
module MakeTabs(box_width, box_length, lid_thickness = default_lid_thickness, tab_length = 10, make_tab_width = false,
                make_tab_length = true)
{

    if (make_tab_length)
    {
        translate([ 0, (box_length + tab_length) / 2, lid_thickness ]) rotate([ 0, 0, 270 ]) children();
        translate([ box_width, (box_length - tab_length) / 2, lid_thickness ]) rotate([ 0, 0, 90 ]) children();
    }

    if (make_tab_width)
    {
        translate([ (box_width - tab_length) / 2, 0, lid_thickness ]) children();
        translate([ (box_width + tab_length) / 2, box_length, lid_thickness ]) rotate([ 0, 0, 180 ]) children();
    }
}