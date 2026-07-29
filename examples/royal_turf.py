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

# LibFile: examples/royal_turf.py
#    PythonSCAD port of royal_turf.scad. Cap-box children are callable(inner_size) -> list of
#    InnerObject; sliding-box children are callable(inner_width, inner_length, inner_height) ->
#    solid. default_wall_thickness = 3 is passed explicitly (3.5 for the cap boxes).

from base_bgtk import *
from pybosl2.shapes3d import cuboid, ycyl
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from no_lid import MakeBoxWithNoLid
from components import RoundedBoxAllSides, FingerHoleWall

wall_thickness = 3
cap_wall = 3.5

box_width = 176
box_length = 225
box_height = 35
board_thickness = 6

horse_card_width = 41
horse_card_length = 61
horse_standee_height = 32
horse_standee_width = 27.5
horse_standee_round = 16.5
horse_standee_round_thickness = 2.5
bet_size = 19.5
person_marker_length = 38.5
cardboard_thickness = 1.5

player_box_width = box_width / 3
player_box_length = bet_size + wall_thickness * 2 + 1
player_box_height = (box_height - board_thickness - 1) / 2

horse_box_width = box_width
horse_box_length = horse_standee_height * 2 + wall_thickness * 3
horse_box_height = box_height - board_thickness

horse_tile_box_width = box_width
horse_tile_box_length = horse_card_length + wall_thickness * 2
horse_tile_box_height = box_height - board_thickness

money_box_width = box_width / 2
money_box_length = box_length - horse_box_length - player_box_length - horse_tile_box_length
money_box_height = box_height - board_thickness

spacer_box_width = money_box_width
spacer_box_length = money_box_length
spacer_box_height = money_box_height


@make_box
def PlayerBox():
    def bet(iw, il, ih):
        return cuboid([bet_size, bet_size, cardboard_thickness * 5 + 1], anchor=BOTTOM).translate([iw / 2, il / 2, ih - cardboard_thickness * 5 - 1])

    def marker(iw, il, ih):
        return cuboid([person_marker_length, bet_size, cardboard_thickness * 5 + 1], anchor=BOTTOM).translate([iw / 2, il / 2, ih - cardboard_thickness - 0.5])

    def fh(iw, il, ih):
        return FingerHoleWall(radius=7, height=cardboard_thickness * 5 + 1).translate([iw / 2, 0, ih - cardboard_thickness * 5 - 0.9])

    return MakeBoxWithSlidingLid(size=[player_box_width, player_box_length, player_box_height], wall_thickness=wall_thickness, children=[bet, marker, fh])


@make_box
def PlayerBoxLid():
    return SlidingBoxLidWithLabel(size=[player_box_width, player_box_length, player_box_height], wall_thickness=wall_thickness, text_str="Player")


@make_box
def MoneyBox():
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([inner.width, inner.length, money_box_height], radius=money_box_height / 2))]

    return MakeBoxWithCapLid(size=[money_box_width, money_box_length, money_box_height], wall_thickness=cap_wall, children=kids)


@make_box
def MoneyBoxLid():
    return CapBoxLidWithLabel(size=[money_box_width, money_box_length, money_box_height], wall_thickness=cap_wall, text_str="Money")


@make_box
def HorseBox():
    def standee(front):
        cyl_y = -horse_standee_height / 2 if front else horse_standee_height / 2
        anchor = FRONT if front else BACK
        return (
            cuboid([horse_standee_width, horse_standee_height, horse_box_height], anchor=BOTTOM)
            | ycyl(d=horse_standee_round, l=horse_standee_round_thickness + 0.5, anchor=anchor).translate([0, cyl_y, 0])
        )

    def kids(inner):
        z = inner.height - horse_standee_round / 2 - horse_standee_round_thickness
        objs = []
        for i in range(4):
            objs.append(InnerObject(standee(True).translate([inner.width / 2 - (horse_standee_width + 2) * (1.5 - i), horse_standee_height / 2, z])))
        for i in range(3):
            objs.append(InnerObject(standee(False).translate([inner.width / 2 - (horse_standee_width + 2) * (1 - i), inner.length - horse_standee_height / 2, z])))
        return objs

    return MakeBoxWithCapLid(size=[horse_box_width, horse_box_length, horse_box_height], wall_thickness=cap_wall, children=kids)


@make_box
def HorseBoxLid():
    return CapBoxLidWithLabel(size=[horse_box_width, horse_box_length, horse_box_height], wall_thickness=cap_wall, text_str="Horses")


@make_box
def HorseCardBox():
    def kids(inner):
        z = inner.height - cardboard_thickness * 7 - 1
        objs = []
        for i in range(3):
            x = inner.width / 2 - (horse_card_width + wall_thickness) * (1 - i)
            objs.append(InnerObject(cuboid([horse_card_width, horse_card_length, horse_tile_box_height], anchor=BOTTOM).translate([x, inner.length / 2, z])))
            objs.append(InnerObject(FingerHoleWall(radius=13, height=cardboard_thickness * 7 + 1).translate([x, 0, z])))
        return objs

    return MakeBoxWithCapLid(size=[horse_tile_box_width, horse_tile_box_length, horse_tile_box_height], wall_thickness=cap_wall, children=kids)


@make_box
def HorseCardBoxLid():
    return CapBoxLidWithLabel(size=[horse_tile_box_width, horse_tile_box_length, horse_tile_box_height], wall_thickness=cap_wall, text_str="Horse Tiles")


@make_box
def SpacerBox():
    return MakeBoxWithNoLid(size=[spacer_box_width, spacer_box_length, spacer_box_height], wall_thickness=wall_thickness, hollow=True)


if FROM_MAKE != 1:
    HorseBox().show()
