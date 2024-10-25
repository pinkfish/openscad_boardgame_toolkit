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
//   width = the width of the box (outside width)
//   length = the length of the box (outside length)
//   lid_thickness = height of the lid (default 2)
//   wall_thickness = thickness of the walls (default 2)
//   inset = how far the side is inset from the edge of the box (default 1)
//   lid_size_spacing = how much wiggle room to give in the model (default {{m_piece_wiggle_room}})
// Topics: TabbedBox
// Example:
//  InsetLid(50, 100);
module InsetLid(width, length, lid_thickness = 2, wall_thickness = 2, inset = 1, lid_size_spacing = m_piece_wiggle_room)
{
    internal_build_lid(width, length, lid_thickness, wall_thickness, lid_size_spacing = lid_size_spacing)
    {
        translate([ wall_thickness - inset + m_piece_wiggle_room, wall_thickness - inset + m_piece_wiggle_room, 0 ])
            cube([
                width - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2,
                length - (wall_thickness - inset) * 2 - m_piece_wiggle_room * 2,
                lid_thickness
            ]);
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
//   lid_thickness = height of the lid (default 2)
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
module InsetLidTabbed(width, length, lid_thickness = 2, wall_thickness = 2, inset = 1,
                      lid_size_spacing = m_piece_wiggle_room, make_tab_width = false, make_tab_length = true,
                      prism_width = 0.75, tab_length = 10, tab_height = 8)
{
    translate([ 0, length, lid_thickness ]) rotate([ 180, 0, 0 ]) union()
    {
        InsetLid(width = width, length = length, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
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
        MakeTabs(box_width = width, box_length = length, lid_thickness = lid_thickness, make_tab_width = make_tab_width,
                 make_tab_length = make_tab_length)
            MakeLidTab(length = tab_length, height = tab_height, lid_thickness = lid_thickness,
                       prism_width = prism_width, wall_thickness = wall_thickness);
        ;
    }
}

// Module: InsetLidTabbedWithLabel()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed lid with
//   a label and a hex grid. The children to this as also pulled out of the lid so can be used to
//   build more complicated lids.
// Usage:
//    InsetLidTabbedWithLabel(width = 100, length = 100, lid_thickness = 3, text_width = 60, text_height = 30, text_str
//    = "Trains", label_rotated = false);
// Arguments:
//    width = width of the box (outside dimension)
//    length = length of the box (outside dimension)
//    text_width = width of the text section
//    text_height = length of the text section
//    text_str = The string to write
//    lid_thickness = height of the lid (default 3)
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
//        width = 100, length = 100, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module InsetLidTabbedWithLabel(width, length, text_width, text_height, text_str, lid_thickness = 3, lid_boundary = 10,
                               label_radius = 12, border = 2, offset = 4, label_rotated = false, tab_length = 10,
                               tab_height = 8, make_tab_width = false, make_tab_length = true, prism_width = 0.75,
                               layout_width = 12, shape_width = 12, shape_type = SHAPE_TYPE_DENSE_HEX,
                               shape_thickness = 2)
{
    InsetLidTabbed(width, length, lid_thickness = lid_thickness, tab_length = tab_length, tab_height = tab_height)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
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
//   lid_thickness = height of the lid (defaults to 3)
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
module InsetLidTabbedForHexBox(rows, cols, tile_width, lid_thickness = 3, wall_thickness = 2, spacing = 0,
                               tab_height = 8, tab_length = 10, inset = 1, make_tab_width = false,
                               make_tab_length = true, prism_width = 0.75)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    InsetLidTabbed(width = rows * radius * 2 + wall_thickness * 2, length = cols * apothem * 2 + wall_thickness * 2,
                   lid_thickness = lid_thickness, tab_height = tab_height, tab_length = tab_length, inset = 1)
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
//    InsetLidTabbedWithLabelForHexBox(rows = 3, cols = 4, tile_width = 29, lid_thickness = 3, text_width = 60,
//    text_height = 30, text_str = "Trains", label_rotated = false);
// Arguments:
//    rows = number of rows to generate
//    cols = number of cols to generate
//    tile_width = width of the tiles
//    lid_thickness = height of the lid (defaults to 3)
//    wall_thickness = thickness of the walls (defaults to 2)
//    spacing = spacing between the hexes
//    text_width = width of the text section
//    text_height = length of the text section
//    text_str = The string to write
//    lid_thickness = height of the lid (default 3)
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
//        cols = 3, rows = 4, tile_width = 29, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module InsetLidTabbedWithLabelForHexBox(rows, cols, tile_width, text_width, text_height, text_str, lid_thickness = 3,
                                        lid_boundary = 10, label_radius = 12, border = 2, offset = 4,
                                        label_rotated = false, wall_thickness = 2, tab_height = 8, tab_length = 10,
                                        inset = 1, layout_width = 12, shape_width = 12,
                                        shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2)
{
    apothem = tile_width / 2;
    radius = apothem / cos(180 / 6);
    width = rows * radius * 2 + wall_thickness * 2;
    length = cols * apothem * 2 + wall_thickness * 2;

    InsetLidTabbed(width, length, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
                   tab_length = tab_length, tab_height = tab_height, inset = inset)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        intersection()
        {
            cube([ width - border, length - border, lid_thickness ]);
            translate([ (width) / 2, length - border - 3, 0 ]) SlidingLidFingernail(lid_thickness);
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

// Module: MakeBoxWithInsetLidTabbed()
// Description:
//   Makes a box with an inset lid.  Handles all the various pieces for making this with tabs.  This will make
//   sure the cutouts are only inside the box and in the floor, if you want to cut out the sides of the box
//   do this with a difference after making this object.  The children and moves so 0,0,0 is the bottom inside
//   of the box to make for easier arithmatic.
// Usage:
//   MakeBoxWithInsetLidTabbed(width = 30, length = 100, height = 20);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = how thick the walls are (default 2)
//   lid_thickness = how hight the lid is (default 2)
//   tab_height = how heigh to make the tabs (default 6)
//   inset = how far to inset the lid (default 1)
//   make_tab_width = make the tabs on the width (default false)
//   make_tab_length = make the tabs on the length (default true)
//   prism_width = width of the prism to generate (default 0.75)
//   tab_length = how long the tab is (default 10)
//   stackable = should we pull a piece out the bottom of the box to let this stack (default false)
//   lid_size_spacing = wiggle room to use when generatiung box (default {{m_piece_wiggle_room}})
//   floor_thickness = thickness of the floor (default 2)
// Topics: TabbedBox, TabbedLid
// Example:
//   MakeBoxWithInsetLidTabbed(width = 30, length = 100, height = 20);
module MakeBoxWithInsetLidTabbed(width, length, height, wall_thickness = 2, lid_thickness = 2, tab_height = 8,
                                 inset = 1, make_tab_width = false, make_tab_length = true, prism_width = 0.75,
                                 tab_length = 10, stackable = false, lid_size_spacing = m_piece_wiggle_room,
                                 floor_thickness = 2, tab_offset = 0.45)
{
    difference()
    {
        cube([ width, length, height ]);
        translate([ wall_thickness - inset, wall_thickness - inset, height - lid_thickness ])
            cube([ width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1 ]);
        translate([ 0, 0, height - lid_thickness ])
            MakeTabs(box_width = width, box_length = length, lid_thickness = lid_thickness, tab_length = tab_length,
                     make_tab_length = make_tab_length, make_tab_width = make_tab_width) minkowski()
        {
            translate([ -tab_offset, -tab_offset, -tab_offset ]) cube(tab_offset * 2);
            MakeLidTab(length = tab_length, height = tab_height, lid_thickness = lid_thickness,
                       prism_width = prism_width, wall_thickness = wall_thickness);
        }

        // Make sure the children start from the bottom corner of the box.
        translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
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

// Module: InsetLidRabbitClip()
// Description:
//   Makes an inset lid with the tabes on the side.
// Usage:
//   InsetLidRabbitClip(30, 100);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   lid_thickness = height of the lid (default 2)
//   wall_thickness = thickness of the walls (default 2)
//   inset = how far to inset the lid (default 1)
//   lid_size_spacing = the wiggle room in the lid generation (default {{m_piece_wiggle_room}})
//   make_rabbit_width = makes tabes on thr width (default false)
//   make_rabbit_length = makes tabs on the length (default true)
//   rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//   rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//   rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//   rabbit_compression = how much sideway give on the rabbit (default 0.1)
//   rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//   rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//   rabbit_depth = extrustion depth of the rabbit (default 1.5)
// Topics: RabbitClipBox
// Example:
//   InsetLidRabbitClip(30, 100);
module InsetLidRabbitClip(width, length, lid_thickness = 2, wall_thickness = 2, inset = 1,
                          lid_size_spacing = m_piece_wiggle_room, make_rabbit_width = false, make_rabbit_length = true,
                          rabbit_width = 7, rabbit_length = 6, rabbit_lock = false, rabbit_compression = 0.1,
                          rabbit_thickness = 0.8, rabbit_snap = 0.25, rabbit_offset = 3, rabbit_depth = 1.5)
{
    translate([ 0, length, lid_thickness ]) rotate([ 180, 0, 0 ]) union()
    {
        InsetLid(width = width, length = length, lid_thickness = lid_thickness, wall_thickness = wall_thickness,
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
        MakeTabs(box_width = width, box_length = length, lid_thickness = lid_thickness,
                 make_tab_width = make_rabbit_width, make_tab_length = make_rabbit_length)
            translate([ (rabbit_length + rabbit_offset) / 2, wall_thickness / 2, -lid_thickness / 2 ])
                cuboid([ rabbit_length + rabbit_offset, wall_thickness, lid_thickness ]) attach(TOP)
                    rabbit_clip(type = "pin", length = rabbit_length, width = rabbit_width, snap = rabbit_snap,
                                thickness = rabbit_thickness, depth = rabbit_depth, compression = rabbit_compression,
                                lock = rabbit_lock);
    }
}

// Module: InsetLidRabbitWithLabel()
// Description:
//   This is a composite method that joins together the other pieces to make a simple inset tabbed lid with
//   a label and a hex grid. The children to this as also pulled out of the lid so can be used to
//   build more complicated lids.
// Usage:
//    InsetLidRabbitWithLabel(width = 100, length = 100, lid_thickness = 3, text_width = 60, text_height = 30, text_str
//    = "Trains", label_rotated = false);
// Arguments:
//    width = width of the box (outside dimension)
//    length = length of the box (outside dimension)
//    text_width = width of the text section
//    text_height = length of the text section
//    text_str = The string to write
//    lid_thickness = height of the lid (default 3)
//    lid_boundary = how much boundary should be around the pattern (default 10)
//    label_radius = radius of the rounded corner for the label section (default 12)
//    border = how wide the border strip on the label should be (default 2)
//    offset = how far inside the border the label should be (degault 4)
//    label_rotated = if the label should be rotated, default to false
//    make_rabbit_width = makes tabes on thr width (default false)
//    make_rabbit_length = makes tabs on the length (default true)
//    rabbit_length = length of the rabbit piece (downwards direction) (default 6)
//    rabbit_width = width of the rabbit piece (crosswise direction) (default 7)
//    rabbit_lock = if the rabbit should habe a locking piece on it (default false)
//    rabbit_compression = how much sideway give on the rabbit (default 0.1)
//    rabbit_snap = how deep the inner depth should be for the snap curve (default 0.25)
//    rabbit_offset = how much of an offset on each side of the rabbit to attach to the lid (default 3)
//    rabbit_depth = extrustion depth of the rabbit (default 1.5)
//    layout_width = space in the grid for the layout (default 12)
//    shape_width = with of the shape in the grid (default 12)
//    shape_type = type of the shape to generate on the lid (default SHAPE_TYPE_DENSE_HEX)
//    shape_thickness = thickness of the shape in the mesh (default 2)
// Topics: RabbitClipBox
// Example:
//    InsetLidRabbitWithLabel(
//        width = 100, length = 100, lid_thickness = 3, text_width = 60,
//        text_height = 30, text_str = "Trains", label_rotated = false);
module InsetLidRabbitWithLabel(width, length, text_width, text_height, text_str, lid_thickness = 3, lid_boundary = 10,
                               label_radius = 12, border = 2, offset = 4, label_rotated = false,
                               make_rabbit_width = false, make_rabbit_length = true, rabbit_width = 7,
                               rabbit_length = 6, rabbit_lock = false, rabbit_compression = 0.1, rabbit_thickness = 0.8,
                               rabbit_snap = 0.25, rabbit_offset = 3, layout_width = 12, shape_width = 12,
                               shape_type = SHAPE_TYPE_DENSE_HEX, shape_thickness = 2, rabbit_depth = 1.5)
{
    InsetLidRabbitClip(width, length, lid_thickness = lid_thickness, make_rabbit_length = make_rabbit_length,
                       make_rabbit_width = make_rabbit_width, rabbit_width = rabbit_width,
                       rabbit_length = rabbit_length, rabbit_lock = rabbit_lock, rabbit_offset = rabbit_offset,
                       rabbit_thickness = rabbit_thickness, rabbit_compression = rabbit_compression,
                       rabbit_depth = rabbit_depth)
    {

        translate([ lid_boundary, lid_boundary, 0 ])
            LidMeshBasic(width = width, length = length, lid_thickness = lid_thickness, boundary = lid_boundary,
                         layout_width = layout_width, shape_type = shape_type, shape_width = shape_width,
                         shape_thickness = shape_thickness);
        if (label_rotated)
        {
            translate([ (width + text_height) / 2, (length - text_width) / 2, 0 ]) rotate([ 0, 0, 90 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
        }
        else
        {
            translate([ (width - text_width) / 2, (length - text_height) / 2, 0 ])
                MakeStripedLidLabel(width = text_width, length = text_height, lid_thickness = lid_thickness,
                                    label = text_str, border = border, offset = offset, full_height = true);
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

// Module: MakeBoxWithInsetLidRabbitClip()
// Description:
//   Makes a box with an inset lid.  Handles all the various pieces for making this with rabbit clips.
//   The children are moved so 0,0,0 is the bottom inside of the box to make for easier arithmatic.
// Usage:
//   MakeBoxWithInsetLidRabbitClip(width = 30, length = 100, height = 20);
// Arguments:
//   width = width of the box (outside width)
//   length = length of the box (outside length)
//   height = height of the box (outside height)
//   wall_thickness = how thick the walls are (default 2)
//   lid_thickness = how hight the lid is (default 2)
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
//   lid_size_spacing = wiggle room to use when generatiung box (default {{m_piece_wiggle_room}})
//   floor_thickness = thickness of the floor (default 2)
// Topics: RabbitClipBox
// Example:
//   MakeBoxWithInsetLidRabbitClip(width = 30, length = 100, height = 20);
module MakeBoxWithInsetLidRabbitClip(width, length, height, wall_thickness = 2, lid_thickness = 2, tab_height = 8,
                                     floor_thickness = 2, inset = 1, make_rabbit_width = false,
                                     make_rabbit_length = true, rabbit_width = 6, rabbit_length = 7, rabbit_offset = 3,
                                     rabbit_lock = false, rabbit_compression = 0.1, rabbit_thickness = 0.8,
                                     rabbit_snap = 0.25, lid_size_spacing = m_piece_wiggle_room, rabbit_depth = 1.5)
{
    difference()
    {
        cube([ width, length, height ]);
        translate([ wall_thickness - inset, wall_thickness - inset, height - lid_thickness ])
            cube([ width - (wall_thickness - inset) * 2, length - (wall_thickness - inset) * 2, lid_thickness + 0.1 ]);
        translate([ 0, 0, height - lid_thickness ])
            MakeTabs(box_width = width, box_length = length, lid_thickness = lid_thickness,
                     tab_length = rabbit_length + rabbit_offset, make_tab_length = make_rabbit_length,
                     make_tab_width = make_rabbit_width) union()
        {
            translate([
                (rabbit_length + rabbit_offset + lid_size_spacing * 2) / 2, wall_thickness / 2 - 0.01,
                -lid_thickness / 2
            ])
                cuboid([
                    rabbit_length + rabbit_offset + lid_size_spacing * 2, wall_thickness + 0.01, lid_thickness + 0.01
                ]);
            translate([
                (rabbit_length + rabbit_offset + lid_size_spacing * 2) / 2, wall_thickness / 2 - 0.01, -lid_thickness
            ]) rabbit_clip(type = "socket", length = rabbit_length, width = rabbit_width, snap = rabbit_snap,
                           thickness = rabbit_thickness, depth = rabbit_depth + 0.01, compression = rabbit_compression,
                           lock = rabbit_lock);
        }

        // Make sure the children start from the bottom corner of the box.
        translate([ wall_thickness, wall_thickness, floor_thickness ]) children();
    }
}

// Module: MakeHexBoxWithInsetLidTabbed()
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
//   lid_thickness = height of the lid (default 2)
//   floor_thickness = thickness of the floor (default 2)
//   wall_thickness = the thickness of the wall (default 2)
// Topics: TabbedBox, TabbedLid, Hex
// Example:
//   MakeHexBoxWithInsetLidTabbed(rows = 4, cols = 3, height = 15, push_block_height = 1, tile_width = 29);
module MakeHexBoxWithInsetLidTabbed(rows, cols, height, push_block_height, tile_width, lid_thickness = 2,
                                    floor_thickness = 2, spacing = 0, wall_thickness = 2)
{
    width = tile_width;
    apothem = width / 2;
    radius = apothem / cos(180 / 6);

    MakeBoxWithInsetLidTabbed(rows * radius * 2 + 4, cols * apothem * 2 + 4, height, stackable = true,
                            lid_thickness = lid_thickness, floor_thickness = floor_thickness)

    {
        HexGridWithCutouts(rows = rows, cols = cols, height = height, tile_width = tile_width, spacing = spacing,
                           wall_thickness = wall_thickness);
        children();
    }
}
