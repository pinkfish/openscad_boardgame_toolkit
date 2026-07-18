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

# LibFile: examples/gulf_mobile_and_ohio.py
#    PythonSCAD port of gulf_mobile_and_ohio.scad (default_wall_thickness = 3). The BoxLayout
#    document-image modules are not ported (they are print-arrangement previews, not boxes).
#    MoneyBox's denomination labels are engraved text (a positive_negative child so the mmu
#    build renders them as a coloured layer).

import math

from base_bgtk import *
from bosl2.shapes3d import cuboid, cyl
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from no_lid import MakeBoxWithNoLid, MakePathBoxWithNoLid
from components import RoundedBoxAllSides, FingerHoleBase

wall = 3
box_width = 217
box_length = 307
box_height = 39
board_thickness = 9.5
cube_size = 8.25
marker_diameter = 16.5
marker_thickness = 14.5
common_share_diameter = 20.5
common_share_thickness = 31
money_width = 53
money_length = 101
card_width = 66
card_length = 91

money_box_width = (money_width + 2) * 3 + wall * 2
money_box_length = money_length + wall * 2
money_box_height = box_height - board_thickness
company_box_width = card_width + wall * 2
company_box_length = card_length + wall * 2
company_box_height = box_height - board_thickness
cube_box_length = box_length - company_box_length - money_box_length
cube_box_width = box_width / 4
cube_box_height = (box_height - board_thickness) / 2
player_token_box_length = cube_box_length
player_token_box_width = cube_box_width
player_token_box_height = common_share_diameter + default_floor_thickness + default_lid_thickness
front_spacer_box_length = player_token_box_length
front_spacer_box_width = player_token_box_width
front_spacer_box_height = box_height - board_thickness - player_token_box_height

cube_info = [
    {"color": "red", "num_x": 20 / 5, "num_y": 5, "remainder": 20 % 5},
    {"color": "yellow", "num_x": math.floor(26 / 8), "num_y": 8, "remainder": 26 % 8},
    {"color": "green", "num_x": 32 / 8, "num_y": 8, "remainder": 32 % 8},
    {"color": "blue", "num_x": 16 / 8, "num_y": 8, "remainder": 16 % 8},
    {"color": "black", "num_x": 12 / 6, "num_y": 6, "remainder": 12 % 6},
    {"color": "purple", "num_x": 6 / 6, "num_y": 6, "remainder": 6 % 6},
]


@make_box
def MoneyBox():
    def slots(iw, il, ih):
        r = None
        for i in range(3):
            piece = cuboid([money_width, money_length, money_box_height], anchor=BOTTOM + FRONT + LEFT).translate([(money_width + 2) * i, 0, 0]) | FingerHoleBase(radius=15, height=money_box_height).translate([(money_width + 2) * i + money_width / 2, 0, -2])
            r = piece if r is None else r | piece
        return r

    def labels(iw, il, ih):
        r = None
        for i in range(3):
            t = text(["1", "5", "20"][i], size=20, font="Impact", halign="center", valign="center").linear_extrude(height=0.2).color("black").translate([(money_width + 2) * i + money_width / 2, money_length / 2, -0.2])
            r = t if r is None else r | t
        return r

    return MakeBoxWithSlidingLid(size=[money_box_width, money_box_length, money_box_height], positive_negative_children=[1], children=[slots, labels])


@make_box
def MoneyBoxLid():
    return SlidingBoxLidWithLabel(size=[money_box_width, money_box_length], text_str="Bank")


@make_box
def CompanyBox():
    def kids(iw, il, ih):
        return cube([card_width, card_length, company_box_height])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=15, height=money_box_height).translate([card_width / 2, 0, -2])

    return MakeBoxWithSlidingLid(size=[company_box_width, company_box_length, company_box_height], children=[kids, finger])


@make_box
def CompanyBoxLid():
    return SlidingBoxLidWithLabel(size=[company_box_width, company_box_length, company_box_height], text_str="Companies")


def _cube_box(num):
    info = cube_info[num]

    def kids(inner):
        block = cuboid([cube_size * info["num_x"], cube_size * info["num_y"], cube_box_height], anchor=BOTTOM).translate([inner.width / 2, inner.length / 2, inner.height - cube_size - 0.5])
        objs = [InnerObject(block)]
        if info["remainder"] > 0:
            extra = cuboid([cube_size, cube_size * info["remainder"], cube_box_height], anchor=BOTTOM).translate([inner.width / 2 + (cube_size * info["num_x"]) / 2 + cube_size / 2, inner.length / 2, inner.height - cube_size - 0.5])
            objs.append(InnerObject(extra))
        objs.append(InnerObject(RoundedBoxAllSides([inner.width - 4, inner.length - 4, cube_box_height], radius=5).translate([2, 2, inner.height - cube_size / 2])))
        return objs

    return MakeBoxWithCapLid(size=[cube_box_width, cube_box_length, cube_box_height], material_colour=info["color"], children=kids)


def _cube_lid(num):
    return CapBoxLidWithLabel(size=[cube_box_width, cube_box_length, cube_box_height], text_str=cube_info[num]["color"].capitalize())


@make_box
def CubeBoxRed():
    return _cube_box(0)


@make_box
def CubeBoxYellow():
    return _cube_box(1)


@make_box
def CubeBoxGreen():
    return _cube_box(2)


@make_box
def CubeBoxBlue():
    return _cube_box(3)


@make_box
def CubeBoxBlack():
    return _cube_box(4)


@make_box
def CubeBoxPurple():
    return _cube_box(5)


@make_box
def CubeBoxLidRed():
    return _cube_lid(0)


@make_box
def CubeBoxLidYellow():
    return _cube_lid(1)


@make_box
def CubeBoxLidGreen():
    return _cube_lid(2)


@make_box
def CubeBoxLidBlue():
    return _cube_lid(3)


@make_box
def CubeBoxLidBlack():
    return _cube_lid(4)


@make_box
def CubeBoxLidPurple():
    return _cube_lid(5)


@make_box
def PlayerTokenBox():
    def markers(inner):
        objs = []
        for i in range(5):
            objs.append(InnerObject(cyl(d=marker_diameter, h=player_token_box_height, anchor=BOTTOM).translate([5 + marker_diameter / 2, 6 + marker_diameter / 2 + (marker_diameter + 1) * i, inner.height - marker_thickness])))
        objs.append(InnerObject(cuboid([common_share_diameter, common_share_thickness, common_share_diameter + 10], anchor=BOTTOM, rounding=common_share_diameter / 2, edges=BOTTOM).translate([inner.width - common_share_diameter * 3 / 4, inner.length / 2, inner.height - common_share_diameter - 0.5])))
        objs.append(InnerObject(RoundedBoxAllSides([inner.width - 2, inner.length - 2, player_token_box_height], radius=5).translate([1, 1, inner.height - marker_thickness / 2])))
        return objs

    return MakeBoxWithCapLid(size=[player_token_box_width, player_token_box_length, player_token_box_height], children=markers)


@make_box
def PlayerTokenBoxLid():
    return CapBoxLidWithLabel(size=[player_token_box_width, player_token_box_length, player_token_box_height], text_str="Tokens")


@make_box
def FrontSpacerBox():
    return MakeBoxWithNoLid(size=[front_spacer_box_width, front_spacer_box_length, front_spacer_box_height], hollow=True)


@make_box
def SideSpacerBox():
    width_offset = money_box_width - company_box_width * 2
    box_path = [
        [width_offset, 0],
        [width_offset, money_box_length + 2],
        [0, money_box_length + 2],
        [0, money_box_length + company_box_length - 2],
        [box_width - company_box_width * 2 - 2, money_box_length + company_box_length - 2],
        [box_width - company_box_width * 2 - 2, 0],
    ]
    return MakePathBoxWithNoLid(path=box_path, height=box_height - board_thickness, hollow=True)


if FROM_MAKE != 1:
    MoneyBox().show()
