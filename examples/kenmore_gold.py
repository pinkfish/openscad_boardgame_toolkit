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
#    PythonSCAD port of kenmore_gold.scad: three CapBox inserts for
#    Kenmore Gold -- square tiles, start cave, and loot.
#
#    The .scad built each box as a ``MakeBoxWithCapLid`` with raw cuboids
#    and finger holes as children. Here the same geometry is InnerObject
#    entries; the start cave's notched cavity is a difference of two
#    cuboids matching the .scad exactly.
#
# FileSummary: Kenmore Gold insert -- tiles, start cave and loot.
# FileGroup: Examples

import pybosl2.shapes3d as s3

from base_bgtk import (
    BOTTOM,
    FROM_MAKE,
    FRONT,
    MAKE_MMU,
    InnerObject,
    LabelType,
    ObjectType,
    make_box,
)
from box_base import BoxKit, BoxSpec, Label, Lid
from cap_box import CapBox
from components import FingerHoleBase, RoundedBoxAllSides
from labels import MakeLabelOptions

# ---- Measurements (from kenmore_gold.scad) ------------------------------------
wall_thickness = 3
inner_thickness = 2
floor_thickness = 2
lid_thickness = 2

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

# The .scad overrides the label type per the MMU setting, with black colour.
_LABEL_OPTIONS = MakeLabelOptions(
    label_colour="black",
    label_type=LabelType.FRAMED_SOLID if MAKE_MMU else LabelType.FRAMED,
)

# ---- Kit: all three boxes are CapBoxes with the same thicknesses --------------
KIT = BoxKit(
    CapBox,
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
)

# ---- SquareTileBox ------------------------------------------------------------
_square_tile = KIT.box(
    size=[tile_box_width, tile_box_length, tile_box_height],
    label="SquareTileBox",
    contents=lambda inner: [
        # Two tile bays side by side, separated by inner_thickness.
        InnerObject(
            s3.cuboid(
                [square_tile_width, square_tile_width, tile_box_height],
                anchor=BOTTOM,
            ),
            ObjectType.NEGATIVE,
        ),
        InnerObject(
            s3.cuboid(
                [square_tile_width, square_tile_width, tile_box_height],
                anchor=BOTTOM,
            ).translate([square_tile_width + inner_thickness, 0, 0]),
            ObjectType.NEGATIVE,
        ),
        # Finger holes through the front wall under each bay.
        InnerObject(
            FingerHoleBase(
                radius=18,
                height=tile_box_height - floor_thickness + 1,
                wall_thickness=wall_thickness,
            ).translate([
                square_tile_width / 2,
                0,
                -floor_thickness - 1,
            ]),
            ObjectType.POSITIVE_NEGATIVE,
        ),
        InnerObject(
            FingerHoleBase(
                radius=18,
                height=tile_box_height - floor_thickness + 1,
                wall_thickness=wall_thickness,
            ).translate([
                square_tile_width * 3 / 2 + inner_thickness,
                0,
                -floor_thickness - 1,
            ]),
            ObjectType.POSITIVE_NEGATIVE,
        ),
    ],
    lid=(
        Lid.builder()
        .label("Kenmore Gold", options=_LABEL_OPTIONS)
        .build()
    ),
)


@make_box
def SquareTileBox():
    return _square_tile.make_box()


@make_box
def SquareTileBoxLid():
    return _square_tile.make_lid()


# ---- StartCaveBox -------------------------------------------------------------
def _start_cave_cavity():
    """An L-shaped cavity: a full-width cuboid with a front-notch cut out.

    Matches the .scad difference-of-two-cuboids exactly.
    """
    main = s3.cuboid(
        [cave_start_length, cave_start_width, start_cave_box_height],
        anchor=BOTTOM,
    )
    notch = s3.cuboid(
        [square_tile_width - 1, cave_start_width, start_cave_box_height],
        anchor=BOTTOM + FRONT,
    ).translate([0, cave_start_width / 2 - cave_start_indent, 0])
    return main - notch


_start_cave = KIT.box(
    size=[start_cave_box_width, start_cave_box_length, start_cave_box_height],
    label="StartCaveBox",
    contents=lambda inner: [
        InnerObject(
            _start_cave_cavity().translate([
                inner.width / 2,
                inner.length / 2,
                0,
            ]),
            ObjectType.NEGATIVE,
        ),
        InnerObject(
            FingerHoleBase(
                radius=18,
                height=tile_box_height - floor_thickness + 1,
                wall_thickness=wall_thickness,
            ).translate([
                start_cave_box_width / 2,
                0,
                -floor_thickness - 1,
            ]),
            ObjectType.POSITIVE_NEGATIVE,
        ),
    ],
    lid=(
        Lid.builder()
        .label("Start Cave", options=_LABEL_OPTIONS)
        .build()
    ),
)


@make_box
def StartCaveBox():
    return _start_cave.make_box()


@make_box
def StartCaveBoxLid():
    return _start_cave.make_lid()


# ---- LootBox ------------------------------------------------------------------
_loot = (
    BoxSpec.box_builder()
    .size(loot_box_width, loot_box_length, loot_box_height)
    .label("LootBox")
    .wall_thickness(wall_thickness)
    .floor_thickness(floor_thickness)
    .lid_thickness(lid_thickness)
    .contents(lambda inner: [
        InnerObject(
            RoundedBoxAllSides(
                [inner.width, inner.length, inner.height], radius=10,
            ),
            ObjectType.NEGATIVE,
        ),
    ])
    .lid_label("Loot", options=_LABEL_OPTIONS)
    .cap()
    .build()
)


@make_box
def LootBox():
    return _loot.make_box()


@make_box
def LootBoxLid():
    return _loot.make_lid()


# ---- Preview ------------------------------------------------------------------
if FROM_MAKE != 1:
    LootBox()
