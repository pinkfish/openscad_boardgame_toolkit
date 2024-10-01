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

include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

box_length = 304;
box_width = 212;
box_height = 40;
lid_thickness = 3;
wall_thickness = 2;

side_width = 2;
gap = 2;

boards_height = 10;

section_height = box_height - boards_height - 4;
player_width = (box_width - gap) / 2;
player_length = player_width;
player_section_width = 40;
lid_boundary = 7;

top_width = ((box_width - gap) - 40) / 2;
top_length = top_width;
herald_width = 40;

$fn = 180;

first_width = 40;
radius = 10;

module SealsBox()
{
    MakeBoxWithSlidingLid(width = top_width, length = top_length, height = section_height)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = top_width - wall_thickness * 2,
                               height = section_height, radius = 15);
    }
    translate([ top_width + 10, 0, 0 ]) SlidingLid(top_width, top_length)
    {
        translate([ 10, 10, 0 ])
            LidMesh(width = top_width, length = top_length, lid_height = 3, boundary = 10, radius = 5);
        translate([ (top_width - 60) / 2, (top_length - 20) / 2, 0 ])
            MakeStripedLidLabel(width = 60, length = 20, lid_height = 3, label = "Seals", border = 2, offset = 4);
    }
}

module FarmerBox()
{
    MakeBoxWithSlidingLid(width = top_width, length = top_length, height = section_height)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = top_width - wall_thickness * 2,
                               height = section_height, radius = 15);
    }
    translate([ top_width + 10, 0, 0 ]) SlidingLid(top_width, top_length)
    {
        translate([ 10, 10, 0 ])
            LidMesh(width = top_width, length = top_length, lid_height = 3, boundary = 10, radius = 5);
        translate([ (top_width - 60) / 2, (top_length - 20) / 2, 0 ])
            MakeStripedLidLabel(width = 60, length = 20, lid_height = 3, label = "Farmer", border = 2, offset = 4);
    }
}

module HeraldBox()
{
    MakeBoxWithSlidingLid(width = herald_width, length = top_length, height = section_height)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            RoundedBoxAllSides(length = top_length - wall_thickness * 2, width = herald_width - wall_thickness * 2,
                               height = section_height, radius = 15);
    }
    translate([ herald_width + 10, 0, 0 ]) SlidingLid(herald_width, top_length)
    {
        translate([ 10, 10, 0 ])
            LidMesh(width = herald_width, length = top_length, lid_height = 3, boundary = 10, radius = 5);
        translate([ (herald_width + 15) / 2, (top_length - 50) / 2, 0 ]) rotate([ 0, 0, 90 ])
            MakeStripedLidLabel(width = 50, length = 15, lid_height = 3, label = "Herald", border = 2, offset = 4);
    }
}

module PlayerBox()
{
    MakeBoxWithSlidingLid(width = player_width, length = player_length, height = section_height)
    {
        translate([ wall_thickness, wall_thickness, wall_thickness ])
            RoundedBoxGrid(length = player_length - wall_thickness * 2, width = first_width, height = section_height,
                           radius = radius, rows = 2, cols = 1, all_sides = true);
        translate([ wall_thickness, first_width + wall_thickness * 2, wall_thickness ]) RoundedBoxAllSides(
            width = player_length - wall_thickness * 2, length = player_width - first_width - wall_thickness * 3,
            height = section_height, radius = radius);
    }
    translate([ player_width + 10, 0, 0 ]) SlidingLid(player_width, player_width, lid_height = lid_thickness)
    {
        translate([ 10, 10, 0 ])
            LidMesh(width = player_width, length = player_length, lid_height = 3, boundary = 10, radius = 5);
        translate([ (player_width - 20) / 2, (player_length - 60) / 2, 0 ]) rotate([ 0, 0, 90 ])
            MakeStripedLidLabel(width = 60, length = 20, lid_height = 3, label = "Player", border = 2, offset = 4);
    }
}

module Cascadero()
{
    PlayerBox();

    translate([ 0, player_length + 10, 0 ]) TopBox();

    translate([ 0, player_length * 2 + 10, 0 ]) HeraldBox();

    translate([ player_width + 10, 0, 0 ])
    {
        SlidingLid(width = player_width, length = player_length, lid_height = lid_thickness)
        {
            translate([ 10, 10.0 ]) LidMesh(width = player_width, length = player_length, lid_height = lid_thickness,
                                            boundary = 10, radius = 6, shape_thickness = 2);
        };
    }

    translate([ player_width * 2 + 10, 0, 0 ])
    {
        SlidingLid(width = herald_width, length = top_length, lid_height = lid_thickness)
        {
            translate([ 10, 10.0 ]) LidMesh(width = herald_width, length = top_length, lid_height = lid_thickness,
                                            boundary = 10, radius = 10);
        };
    }

    translate([ player_width * 3 + 10, 0, 0 ])
    {
        SlidingLid(width = top_width, length = top_length, lid_height = lid_thickness)
        {
            translate([ 10, 10.0 ])
                LidMesh(width = top_width, length = top_length, thickness = lid_height, boundary = 10, radius = 10);
        };
    }
}

SealsBox();

translate([ 0, 100, 0 ]) FarmerBox();

translate([ 0, 200, 0 ]) HeraldBox();

translate([ 0, 300, 0 ]) PlayerBox();
