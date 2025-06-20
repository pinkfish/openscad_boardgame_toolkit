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

include <BOSL2/beziers.scad>
include <BOSL2/std.scad>
include <boardgame_toolkit.scad>

include <root_shared.scad>

default_lid_thickness = 3;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 10;
default_label_type = MAKE_MMU == 1 ? LABEL_TYPE_FRAMED_SOLID : LABEL_TYPE_FRAMED;


only_board_height = 16;

marquis_box_width = boxData("marquis", "length") + default_wall_thickness;
marquis_box_length = (boxData("marquis", "width") + 2) * 5 + default_wall_thickness * 2;
marquis_box_height = boxData("box", "height") - only_board_height;

erie_box_length = (boxData("erie", "width")) * 4 + default_wall_thickness * 2;
alliance_box_length = (boxData("alliance", "width") + 1) * 2 + default_wall_thickness * 2;
riverfolk_box_length = (boxData("riverfolk", "width") + 1) * 3 + default_wall_thickness * 2;
lizard_box_length = (boxData("lizard", "width") + 1) * 5 + default_wall_thickness * 2;

echo([ marquis_box_height, (boxData("box", "height") - only_board_height) ]);

module MarquisCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_height)
    {
        for (i = [0:1:4])
        {
            height = boxData("token", "thickness") * 5 + 10;
            translate([
                boxData("marquis", "length") / 2 - default_wall_thickness,
                boxData("marquis", "width") / 2 + (boxData("marquis", "width") + 2) * i,
                $inner_height - height - 0.5 + height / 2 + 10
            ]) rotate([ 0, 0, 270 ]) MarquisCharacter(height = height + 1);
        }
    }
}

module ErieCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = erie_box_length, height = marquis_box_height)
    {
        for (i = [0:1:3])
        {
            height = boxData("token", "thickness") * 5 + 10;
            translate([
                boxData("erie", "length") / 2 - default_wall_thickness,
                boxData("erie", "width") / 2 + (boxData("erie", "width")) * i,
                $inner_height - height - 0.5 + height / 2 + 10
            ]) rotate([ 0, 0, 270 ]) ErieCharacter(height = height + 1);
        }
    }
}

module AllianceCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = alliance_box_length, height = marquis_box_height)
    {
        for (i = [0:1:1])
        {
            height = boxData("token", "thickness") * 5 + 10;
            translate([
                boxData("alliance", "length") / 2 - default_wall_thickness,
                boxData("alliance", "width") / 2 + (boxData("alliance", "width") + 1) * i,
                $inner_height - height - 0.5 + height / 2 + 10
            ]) rotate([ 0, 0, 270 ]) AllianceCharacter(height = height + 1);
        }
    }
}

module LizardCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = lizard_box_length, height = marquis_box_height)
    {
        for (i = [0:1:4])
        {
            height = boxData("token", "thickness") * 5 + 10;
            translate([
                boxData("lizard", "length") / 2 - default_wall_thickness,
                boxData("lizard", "width") / 2 + (boxData("lizard", "width") + 1) * i,
                $inner_height - height - 0.5 + height / 2 + 10
            ]) rotate([ 0, 0, 270 ]) LizardCharacter(height = height + 1);
        }
    }
}

module RiverfolkCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = riverfolk_box_length, height = marquis_box_height)
    {
        for (i = [0:1:2])
        {
            height = boxData("token", "thickness") * 5 + 10;
            translate([
                boxData("riverfolk", "length") / 2 - default_wall_thickness,
                boxData("riverfolk", "width") / 2 + (boxData("riverfolk", "width") + 1) * i,
                $inner_height - height - 0.5 + height / 2 + 10
            ]) rotate([ 0, 0, 270 ]) RiverfolkCharacter(height = height + 1);
        }
    }
}

module BoxLayout()
{
    cube([ boxData("box", "width"), boxData("box", "length"), only_board_height ]);
    translate([ 0, 0, only_board_height ])
    {
        MarquisCharacterBox();
        translate([ 0, marquis_box_length, 0 ]) ErieCharacterBox();
        translate([ 0, marquis_box_length + erie_box_length, 0 ]) AllianceCharacterBox();
        translate([ 0, marquis_box_length + erie_box_length + alliance_box_length, 0 ]) RiverfolkCharacterBox();
        translate([ marquis_box_width, 0, 0 ]) LizardCharacterBox();
    }
}

BoxLayout();