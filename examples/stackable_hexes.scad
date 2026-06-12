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

stackable_width = 100;
stackable_height = 24;
default_wall_thickness = 4;

module StackableHexBox(
  divisions = 1,
  magnet_type = MAGNET_SLOT_TYPE_ROUND,
  magnet_size = undef,
  bottom_radius = undef
) {
  calc_magnet_size =
    magnet_size != undef ? magnet_size
    : magnet_type == MAGNET_SLOT_TYPE_ROUND ? [stackable_height / 2 - 1, 7, 2.9]
    : [12, 6, 1.5];

  MakePolygonBoxWithNoLid(
    size=[stackable_width, stackable_height],
    sides=6,
    make_finger_x=false,
    make_finger_y=false,
    hollow=(divisions <= 1),
    hollow_radius=object(top=2, bottom=stackable_height * 3 / 4, radius=2),
    stackable=STACKABLE_TYPE_INSIDE,
    magnet=object(type=magnet_type, size=calc_magnet_size),
    offset_sweep_options=object(offset="delta", check_valid=true, quality=1, steps=16),
  ) {
    if (divisions > 1) {
      HexBoxDivisions(
        stackable_width - default_wall_thickness * 2.5,
        height=stackable_height,
        divisions=divisions,
        bottom_radius=bottom_radius
      );
    }
  }
}

module HexBoxSingle6x3RoundMagnet() // `make` me
{
  StackableHexBox(divisions=1, magnet_type=MAGNET_SLOT_TYPE_ROUND);
}

module HexBoxSingle6x3RoundMagnetWithTwoPartitions() // `make` me
{
  StackableHexBox(divisions=2, magnet_type=MAGNET_SLOT_TYPE_ROUND, bottom_radius=5);
}

module HexBoxSingle6x3RoundMagnetWithThreePartitions() // `make` me
{
  StackableHexBox(divisions=3, magnet_type=MAGNET_SLOT_TYPE_ROUND);
}

module HexBoxSingle6x3RoundMagnetWithFourPartitions() // `make` me
{
  StackableHexBox(divisions=4, magnet_type=MAGNET_SLOT_TYPE_ROUND);
}

module HexBoxSingle10x5x2RectMagnet() // `make` me
{
  StackableHexBox(divisions=1, magnet_type=MAGNET_SLOT_TYPE_RECT);
}

module HexBoxSingle10x5x2RectMagnetWithTwoPartitions() // `make` me
{
  StackableHexBox(divisions=2, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10);
}

module HexBoxSingle10x5x2RectMagnetWithThreePartitions() // `make` me
{
  StackableHexBox(divisions=3, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10);
}

module HexBoxSingle10x5x2RectMagnetWithFourPartitions() // `make` me
{
  StackableHexBox(divisions=4, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10);
}

if (FROM_MAKE != 1) {
  HexBoxSingle10x5x2RectMagnet();
}
