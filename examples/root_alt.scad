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

default_lid_thickness = 2;
default_floor_thickness = 2;
default_wall_thickness = 3;
default_lid_shape_type = SHAPE_TYPE_CIRCLE;
default_lid_shape_thickness = 1;
default_lid_shape_width = 13;
default_lid_layout_width = 10;

marquis_box_width = boxData("marquis", "length") * 2 + default_wall_thickness * 3;
marquis_box_length = boxData("marquis", "width") * 6 + default_wall_thickness * 3;
marquis_box_height = boxData("token", "thickness") * 3 + default_lid_thickness + default_floor_thickness;

module MarquisCharacterBox()
{
    MakeBoxWithSlidingLid(width = marquis_box_width, length = marquis_box_length, height = marquis_box_height,
                          floor_thickness = 0.5, lid_thickness = 1.8)
    {
        translate([ boxData("marquis", "length") / 2 - default_wall_thickness, boxData("marquis", "width") / 2, 20 ])
            rotate([ 0, 0, 270 ]) MarquisCharacter(height = 40);
    }
}

MarquisCharacterBox();