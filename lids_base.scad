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

// Function: IsDenseShapeType()
// Description:
//   If the shape type is dense or not.
// Arguments:
//   shape_type = the shape_type to check
function IsDenseShapeType(shape_type) = DefaultValue(shape_type, default_lid_shape_type) == SHAPE_TYPE_DENSE_HEX ||
                                        DefaultValue(shape_type, default_lid_shape_type) == SHAPE_TYPE_DENSE_TRIANGLE;
// Function: DenseShapeEdges()
// Description:
//   The number of edges on the dense shape.
// Arguments:
//   shape_type = the shape_type to check
function DenseShapeEdges(shape_type) = (shape_type == SHAPE_TYPE_DENSE_TRIANGLE ? 3 : 6);

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
// Usage:
//   LidMeshDense(width = 70, length = 50, lid_thickness = 3, boundary = 10, radius = 5, shape_edges = 6);
// Topics: PatternFill
// Example:
//   LidMeshDense(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10, shape_edges = 6) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX,  shape_width = $layout_width);
//   }
// Example:
//   LidMeshDense(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10, shape_edges = 3) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_TRIANGLE,  shape_width = $layout_width);
//   }
module LidMeshDense(width, length, lid_thickness, boundary, radius, shape_edges = 6,
                    material_colour = default_material_colour)
{
    cell_width = cos(180 / shape_edges) * radius;
    rows = width / cell_width;
    cols = length / cell_width;
    // Default this to 2, this is just the overlap on the edges.
    shape_thickness = 2;

    $layout_width = radius * 2;
    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_thickness + 1)
                RegularPolygonGridDense(radius = radius, rows = rows, cols = cols, shape_edges = shape_edges)
            {
                children();
            }

            difference()
            {
                color(material_colour) cube([ width - boundary * 2, length - boundary * 2, lid_thickness + 1 ]);
                translate([ shape_thickness / 2, shape_thickness / 2, 0 ]) color(material_colour) cube([
                    width - boundary * 2 - shape_thickness, length - boundary * 2 - shape_thickness, lid_thickness + 1
                ]);
            }
        }
        color(material_colour) cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
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
//   LidMeshHex(width = 70, length = 50, lid_thickness = 3, boundary = 10, radius = 5);
// Topics: PatternFill
// Example:
//   LidMeshHex(width = 100, length = 50, lid_thickness = 3, boundary = 10, radius = 10);
module LidMeshHex(width, length, lid_thickness, boundary, radius, shape_thickness = 2)
{
    LidMeshDense(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary, radius = radius,
                 shape_edges = 6)
    {
        ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_width = $layout_width);
    }
}

// Module: LidMeshRepeating()
// Description:
//   Make a mesh for the lid with a repeating shape.  It uses the children of this to repeat the shape.
//   Sets $layout_width as the layout width
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_thickness = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   layout_width = the width to use between each shape.
//   aspect_ratio = the aspect ratio (multiple by dy) (default 1.0)
//   shape_edges = the number of edges on the shape (default 4)
// Usage:
//   LidMeshRepeating(50, 20, 3, 5, 10);
// Topics: PatternFill
// Example:
//   LidMeshRepeating(width = 50, length = 50, lid_thickness = 3, boundary = 5, layout_width = 10)
//      difference() {
//        circle(r = 7);
//        circle(r = 6);
//      }
module LidMeshRepeating(width, length, lid_thickness, boundary, layout_width, aspect_ratio = 1.0, shape_edges = 4,
                        material_colour = default_material_colour)
{
    rows = width / layout_width;
    cols = length / layout_width * aspect_ratio;

    $layout_width = layout_width;
    intersection()
    {
        translate([ 0, 0, -0.5 ]) union()
        {
            linear_extrude(height = lid_thickness + 1)
                RegularPolygonGrid(width = layout_width, rows = rows + 1, cols = cols + 1, spacing = 0,
                                   shape_edges = shape_edges, aspect_ratio = aspect_ratio)
            {
                children();
            }
            difference()
            {
                translate([ 0, 0, -0.5 ]) color(material_colour) cube([ width, length, lid_thickness + 1 ]);
                translate([ m_piece_wiggle_room, m_piece_wiggle_room, -0.5 + m_piece_wiggle_room ])
                    color(material_colour) cube([
                        width - boundary * 2 - m_piece_wiggle_room * 2, length - boundary * 2 - m_piece_wiggle_room * 2,
                        lid_thickness + 1 + m_piece_wiggle_room * 2
                    ]);
            }
        }
        color(material_colour) cube([ width - boundary * 2, length - boundary * 2, lid_thickness ]);
    }
}

// Module: LidMeshBasic()
// Description:
//   Creates a lid mesh with a set of known shapes.  The width is the width of the shape
//   for layout purposes and the shape_width is the width for generation purposes.  The layout
//   width and shape width default to being the same for dense layouts, and overlapping for
//   non-dense layouts.
// Arguments:
//   width = width of the mesh section
//   length = the length of the mesh section
//   lid_thickness = how high the lid is
//   boundary = how wide of a boundary edge to put on the side of the lid
//   radius = the radius of the polygon to create
//   dense_shape_edges = number of edges on the dense shape
//   shape_thickness = how thick to generate the gaps between the hexes (default 2)
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10, dense = true) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, shape_width = $layout_width);
//   }
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 14);
//   }
// Example:
//   LidMeshBasic(width = 70, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 1, shape_width = 11);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_DENSE_TRIANGLE, shape_thickness = 2, shape_width = $layout_width);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_CIRCLE, shape_thickness = 2, shape_width = 14);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_TRIANGLE, shape_thickness = 2, shape_width = $layout_width);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_HEX, shape_thickness = 1, shape_width = 14);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 16);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 13, shape_aspect_ratio=1.25);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_OCTOGON, shape_thickness = 1, shape_width = 10.5, shape_aspect_ratio=1);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
//   }
// Example:
//   default_lid_shape_rounding = 3;
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_SQUARE, shape_thickness = 2, shape_width = 11);
//   }
// Example:
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_CLOUD, shape_thickness = 2, shape_width = $layout_width+1);
//   }
// Example(2D,Med):
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2);
//   }
// Example(2D,Big):
//   LidMeshBasic(width = 100, length = 50, lid_thickness = 2, boundary = 10, layout_width = 10) {
//      ShapeByType(shape_type = SHAPE_TYPE_SUPERSHAPE, shape_thickness = 2, supershape_m1 = 12, supershape_m2 = 12,
//       supershape_n1 = 1, supershape_b = 1.5, shape_width = 15);
//   }
module LidMeshBasic(width, length, lid_thickness, boundary, layout_width, aspect_ratio = 1.0, dense = false,
                    dense_shape_edges = 6, material_colour = default_material_colour)
{
    calc_layout_width = DefaultValue(layout_width, default_lid_layout_width);
    calc_aspect_ratio = DefaultValue(aspect_ratio, default_lid_aspect_ratio);
    if (dense)
    {
        LidMeshDense(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                     radius = calc_layout_width / 2, shape_edges = dense_shape_edges, material_colour = material_colour)
        {
            children();
        }
    }
    else
    {
        LidMeshRepeating(width = width, length = length, lid_thickness = lid_thickness, boundary = boundary,
                         layout_width = calc_layout_width, shape_edges = 4, aspect_ratio = calc_aspect_ratio,
                         material_colour = material_colour)
        {
            children();
        }
    }
}

module internal_build_lid(width, length, lid_thickness, wall_thickness, size_spacing = m_piece_wiggle_room)
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
                    translate([ 0, 0, -0.5 ]) linear_extrude(height = lid_thickness + 1) offset(r = -size_spacing)
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
                                offset(r = -size_spacing) fill() projection(cut = false)
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

module SlidingLidFingernail(lid_thickness, radius = 6, finger_gap = 1.5, sphere = 12, finger_length = 10,
                            material_colour = default_material_colour)
{
    difference()
    {
        translate([ 0, 0, lid_thickness / 2 ]) color(material_colour) cyl(h = lid_thickness, r = radius);
        translate([ 0, 0, finger_length + lid_thickness - finger_gap + 0.1 ]) intersection()
        {
            translate([ -finger_length / 2, -finger_length, -finger_length ]) color(material_colour)
                cube([ finger_length, finger_length, finger_gap ]);
            color(material_colour) sphere(r = finger_length);
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

// Module: MakeLidLabel()
// Description:
//   Makes a label to put into the lid in the right place with the right rotation.
// Topics: Label
// Arguments:
//    width = outside width of the box
//    length = inside width of the box
//    height = outside height of the box
//    lid_thickness = thickness of the lid
//    label_radius = radius of the label corners
//    border= border of the item
//    offset = offset in from the edge for the label
//    label_rotated = if the label is rotated
//    full_height = if the label grid is the full height (when flipped upsidedown)
//    label_colour = the colout of the label (default {{default_label_colour}})
//    solid_background = if the background should be solid (default false)
// Example:
//    MakeLidLabel(100, 20, text_height = 50, text_width = 10, lid_thickness = 2,  text_str =
//    "frog", border = 2,
//       offset = 4, font = default_label_font, label_radius = 2, label_rotated = false, full_height = true);
// Example:
//    MakeLidLabel(100, 20, text_height = 50, text_width = 10, lid_thickness = 2,  text_str =
//    "frog", border = 2,
//       offset = 4, font = default_label_font, label_radius = 2, label_rotated = true, full_height = false);
// Example:
//    MakeLidLabel(100, 20, text_height = 50, text_width = 10, lid_thickness = 2, text_str =
//    "frog", border = 2,
//       offset = 4, font = default_label_font, label_radius = 2, label_rotated = true, full_height = false,
//       solid_background = true);
// Example:
//    MakeLidLabel(100, 20, text_height = 50, text_width = 10, lid_thickness = 2, text_str =
//    "frog", border = 2,
//       offset = 4, font = default_label_font, label_radius = 2, label_rotated = true, full_height = true,
//       solid_background = true);
module MakeLidLabel(width, length, text_height, text_width, lid_thickness, text_str, border, offset, font, label_radius,
                    label_rotated, full_height, label_colour = undef, material_colour = default_material_colour,
                    label_background_colour = undef, solid_background = default_label_solid_background)
{
    if (label_rotated)
    {
        translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
            MakeMainLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness, label = text_str,
                             border = border, offset = offset, full_height = full_height, font = font,
                             radius = label_radius, label_colour = label_colour, material_colour = material_colour,
                             solid_background = solid_background, label_background_colour = label_background_colour);
    }
    else
    {
        translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
            MakeMainLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness, label = text_str,
                             border = border, offset = offset, full_height = full_height, font = font,
                             radius = label_radius, label_colour = label_colour, material_colour = material_colour,
                             solid_background = solid_background, label_background_colour = label_background_colour);
    }
}