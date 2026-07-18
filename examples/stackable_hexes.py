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

# LibFile: examples/stackable_hexes.py
#    PythonSCAD port of stackable_hexes.scad. The .scad `object(...)` literals become
#    types.SimpleNamespace(...); the MakePolygonBoxWithNoLid children block becomes a
#    callable(inner) taking an InnerPath. default_wall_thickness = 4 is passed explicitly.

import types

from base_bgtk import *
from no_lid import MakePolygonBoxWithNoLid, STACKABLE_TYPE_INSIDE
from components import HexBoxDivisions, MAGNET_SLOT_TYPE_ROUND, MAGNET_SLOT_TYPE_RECT

stackable_width = 100
stackable_height = 24
wall_thickness = 4


def StackableHexBox(divisions=1, magnet_type=MAGNET_SLOT_TYPE_ROUND, magnet_size=None, bottom_radius=None):
    if magnet_size is not None:
        calc_magnet_size = magnet_size
    elif magnet_type == MAGNET_SLOT_TYPE_ROUND:
        calc_magnet_size = [stackable_height / 2 - 1, 7, 2.9]
    else:
        calc_magnet_size = [12, 6, 1.65]

    def kids(inner):
        if divisions > 1:
            return HexBoxDivisions(
                stackable_width - wall_thickness * 2.5, height=stackable_height, divisions=divisions, bottom_radius=bottom_radius
            )
        return None

    return MakePolygonBoxWithNoLid(
        size=[stackable_width, stackable_height],
        sides=6,
        wall_thickness=wall_thickness,
        make_finger_x=False,
        make_finger_y=False,
        hollow=(divisions <= 1),
        hollow_radius=types.SimpleNamespace(top=2, bottom=stackable_height * 3 / 4, radius=2),
        stackable=STACKABLE_TYPE_INSIDE,
        magnet=types.SimpleNamespace(type=magnet_type, size=calc_magnet_size),
        children=kids,
    )


@make_box
def HexBoxSingle6x3RoundMagnet():
    return StackableHexBox(divisions=1, magnet_type=MAGNET_SLOT_TYPE_ROUND)


@make_box
def HexBoxSingle6x3RoundMagnetWithTwoPartitions():
    return StackableHexBox(divisions=2, magnet_type=MAGNET_SLOT_TYPE_ROUND, bottom_radius=5)


@make_box
def HexBoxSingle6x3RoundMagnetWithThreePartitions():
    return StackableHexBox(divisions=3, magnet_type=MAGNET_SLOT_TYPE_ROUND)


@make_box
def HexBoxSingle6x3RoundMagnetWithFourPartitions():
    return StackableHexBox(divisions=4, magnet_type=MAGNET_SLOT_TYPE_ROUND)


@make_box
def HexBoxSingle10x5x2RectMagnet():
    return StackableHexBox(divisions=1, magnet_type=MAGNET_SLOT_TYPE_RECT)


@make_box
def HexBoxSingle10x5x2RectMagnetWithTwoPartitions():
    return StackableHexBox(divisions=2, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10)


@make_box
def HexBoxSingle10x5x2RectMagnetWithThreePartitions():
    return StackableHexBox(divisions=3, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10)


@make_box
def HexBoxSingle10x5x2RectMagnetWithFourPartitions():
    return StackableHexBox(divisions=4, magnet_type=MAGNET_SLOT_TYPE_RECT, bottom_radius=10)


if FROM_MAKE != 1:
    HexBoxSingle10x5x2RectMagnet().show()
