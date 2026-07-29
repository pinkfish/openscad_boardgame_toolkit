# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: examples/kenmore_gold.py
#    PythonSCAD port of kenmore_gold.scad. Cap-box children are callable(inner_size) -> list of
#    InnerObject; a .scad `difference() { a; b; }` child becomes `a - b`. default_wall_thickness
#    = 3 is passed explicitly.

from base_bgtk import *
from pybosl2.shapes3d import cuboid
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from components import FingerHoleBase, RoundedBoxAllSides
from labels import MakeLabelOptions

wall_thickness = 3
inner_thickness = 2
floor_thickness = 2

square_tile_width = 58
cave_start_width = 38
cave_start_length = 77
cave_start_indent = 7
cave_start_total_height = 17
tile_half_height = 50

tile_box_width = square_tile_width * 2 + wall_thickness * 2 + inner_thickness
tile_box_length = square_tile_width + wall_thickness * 2
tile_box_height = tile_half_height + floor_thickness * 2 + 15

start_cave_box_width = tile_box_width
start_cave_box_length = 50
start_cave_box_height = cave_start_total_height + floor_thickness * 2

loot_box_width = start_cave_box_width
loot_box_length = start_cave_box_length
loot_box_height = tile_box_height - start_cave_box_height

BLACK = MakeLabelOptions(label_colour="black")


@make_box
def SquareTileBox():
    def kids(inner):
        return [
            InnerObject(cube([square_tile_width, square_tile_width, tile_box_height])),
            InnerObject(cube([square_tile_width, square_tile_width, tile_box_height]).translate([square_tile_width + inner_thickness, 0, 0])),
            InnerObject(
                FingerHoleBase(radius=18, height=tile_box_height - floor_thickness + 1, wall_thickness=wall_thickness)
                .translate([square_tile_width / 2, 0, -floor_thickness - 1])
            ),
            InnerObject(
                FingerHoleBase(radius=18, height=tile_box_height - floor_thickness + 1, wall_thickness=wall_thickness)
                .translate([square_tile_width * 3 / 2 + inner_thickness, 0, -floor_thickness - 1])
            ),
        ]

    return MakeBoxWithCapLid(size=[tile_box_width, tile_box_length, tile_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def SquareTileBoxLid():
    return CapBoxLidWithLabel(size=[tile_box_width, tile_box_length, tile_box_height], wall_thickness=wall_thickness, text_str="Kenmore Gold", label_options=BLACK)


@make_box
def StartCaveBox():
    def kids(inner):
        cave = (
            cuboid([cave_start_length, cave_start_width, start_cave_box_height], anchor=BOTTOM)
            - cuboid([square_tile_width - 1, cave_start_width, start_cave_box_height], anchor=BOTTOM + FRONT).translate(
                [0, cave_start_width / 2 - cave_start_indent, 0]
            )
        ).translate([inner.width / 2, inner.length / 2, 0])
        fh = FingerHoleBase(radius=18, height=tile_box_height - floor_thickness + 1, wall_thickness=wall_thickness).translate(
            [start_cave_box_width / 2, 0, -floor_thickness - 1]
        )
        return [InnerObject(cave), InnerObject(fh)]

    return MakeBoxWithCapLid(size=[start_cave_box_width, start_cave_box_length, start_cave_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def StartCaveBoxLid():
    return CapBoxLidWithLabel(size=[start_cave_box_width, start_cave_box_length, start_cave_box_height], wall_thickness=wall_thickness, text_str="Start Cave", label_options=BLACK)


@make_box
def LootBox():
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([inner.width, inner.length, inner.height], radius=10))]

    return MakeBoxWithCapLid(size=[loot_box_width, loot_box_length, loot_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def LootBoxLid():
    return CapBoxLidWithLabel(size=[loot_box_width, loot_box_length, loot_box_height], wall_thickness=wall_thickness, text_str="Loot", label_options=BLACK)


if FROM_MAKE != 1:
    LootBox().show()
