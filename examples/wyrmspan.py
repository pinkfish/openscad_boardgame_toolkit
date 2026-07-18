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

# LibFile: examples/wyrmspan.py
#    PythonSCAD port of wyrmspan.scad (default_wall_thickness = 3, passed explicitly).

from base_bgtk import *
from bosl2.shapes3d import cyl, sphere
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from components import RoundedBoxAllSides, RoundedBoxGrid, FingerHoleBase

wall = 3
lid = 2
inner_wall = 1

box_height = 67
box_width = 285
box_length = 285
board_thickness = 27

eggs_box_width = 75
dragon_card_length = 90
dragon_card_width = 58
cave_card_size = 58
bonus_card_width = 46
bonus_card_length = 52.5
start_token_diameter = 67
start_token_thickness = 2
guild_card_width = 95
guild_card_length = 118
guild_card_thickness = 8
round_token_diameter = 18
round_token_thickness = 10
side_section = 47.5

player_box_height = (box_height - 2) / 5
player_box_width = 36 + 15 + 2 * wall
player_box_length = side_section
food_box_height = (box_height - 2) / 2
food_box_width = box_width - player_box_width - 1
food_box_length = side_section
dragon_card_box_width = dragon_card_length + wall * 2 + 1
dragon_card_box_length = (dragon_card_width + 0.5) * 3 + inner_wall * 2 + wall * 2 + 1
dragon_card_box_height = box_height - board_thickness
cave_card_box_length = box_length - player_box_length - 1
cave_card_box_width = box_width - 1 - dragon_card_box_width - eggs_box_width
cave_card_box_height = box_height - board_thickness
coin_box_length = box_width - dragon_card_box_length - player_box_length - 1
coin_box_width = dragon_card_box_width
coin_box_height = dragon_card_box_height / 2


def _capbox(size, kids):
    return MakeBoxWithCapLid(size=size, wall_thickness=wall, children=kids)


def _caplid(size, text):
    return CapBoxLidWithLabel(size=size, wall_thickness=wall, text_str=text)


@make_box
def PlayerBox():
    def kids(inner):
        return [InnerObject(cube([player_box_width - 2 * wall, player_box_length - 2 * wall, player_box_height]))]

    return _capbox([player_box_width, player_box_length, player_box_height], kids)


@make_box
def PlayerBoxLid():
    return _caplid([player_box_width, player_box_length, player_box_height], "Player")


@make_box
def FoodBox():
    def kids(inner):
        return [InnerObject(RoundedBoxGrid([food_box_width - 2 * wall, food_box_length - 2 * wall, food_box_height - lid * 2], radius=10, rows=2, cols=1).translate([0, 0, 10]))]

    return _capbox([food_box_width, food_box_length, food_box_height], kids)


@make_box
def FoodBoxLid():
    return _caplid([food_box_width, food_box_length, food_box_height], "Edibles")


@make_box
def DragonCardBox():
    def kids(inner):
        objs = []
        for i in range(3):
            objs.append(InnerObject(cube([dragon_card_length + 0.5, dragon_card_width + 0.5, dragon_card_box_height]).translate([0, (dragon_card_width + inner_wall + 0.5) * i, 0])))
            objs.append(InnerObject(FingerHoleBase(radius=15, height=cave_card_box_height, spin=270).translate([-1, (dragon_card_width + inner_wall + 0.5) * i + dragon_card_width / 2, -2])))
        return objs

    return _capbox([dragon_card_box_width, dragon_card_box_length, dragon_card_box_height], kids)


@make_box
def DragonCardBoxLid():
    return _caplid([dragon_card_box_width, dragon_card_box_length, dragon_card_box_height], "Dragons")


@make_box
def CaveCardBox():
    def kids(inner):
        objs = []
        for i in range(3):
            objs.append(InnerObject(cube([cave_card_size + 0.5, cave_card_size + 0.5, cave_card_box_height]).translate([0, (cave_card_size + inner_wall + 0.5) * i, 0])))
            objs.append(InnerObject(FingerHoleBase(radius=15, height=cave_card_box_height, spin=270).translate([-1, (cave_card_size + inner_wall + 0.5) * i + cave_card_size / 2, -2])))
        # bonus cards
        objs.append(InnerObject(cube([bonus_card_width + 0.5, bonus_card_length + 0.5, cave_card_box_height]).translate([bonus_card_width + 0.5 + inner_wall, 0, 0])))
        objs.append(InnerObject(FingerHoleBase(radius=15, height=cave_card_box_height, spin=90).translate([cave_card_box_width - wall * 2 + 1, bonus_card_length / 2, -2])))
        # guild cards
        objs.append(InnerObject(cube([guild_card_width + 0.5, guild_card_length + 0.5, guild_card_thickness + 2]).translate([cave_card_box_width - guild_card_width - 0.5, cave_card_box_length - guild_card_length - wall * 2 - 0.5, cave_card_box_height - lid * 2 - guild_card_thickness - 0.5])))
        # first player marker
        objs.append(InnerObject(cyl(d=start_token_diameter + 1, h=start_token_thickness + 1, anchor=BOTTOM).translate([cave_card_box_width - start_token_diameter / 2 - 0.5 - wall * 2, cave_card_box_length - start_token_diameter / 2 - wall * 2 - 0.5, cave_card_box_height - lid * 2 - guild_card_thickness - start_token_thickness - 1])))
        # round token
        rx = cave_card_size + 0.5 + inner_wall + bonus_card_width / 2
        ry = (bonus_card_length + inner_wall + 0.5) * 1 + bonus_card_length / 2
        rz = cave_card_box_height - lid * 2 - round_token_thickness - 0.5
        objs.append(InnerObject(cyl(d=round_token_diameter + 0.5, h=round_token_thickness + 0.6, anchor=BOTTOM).translate([rx, ry, rz])))
        objs.append(InnerObject(sphere(r=10).translate([rx, ry + round_token_diameter / 2, rz + 13])))
        return objs

    return _capbox([cave_card_box_width, cave_card_box_length, cave_card_box_height], kids)


@make_box
def CaveCardBoxLid():
    return _caplid([cave_card_box_width, cave_card_box_length, cave_card_box_height], "Caves + stuff")


def _coin(text):
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([coin_box_width - wall * 2, coin_box_length - wall * 2, coin_box_height], radius=7))]

    return _capbox([coin_box_width, coin_box_length, coin_box_height], kids)


@make_box
def CoinBox():
    return _coin("Coins")


@make_box
def CoinBoxLid():
    return _caplid([coin_box_width, coin_box_length, coin_box_height], "Coins")


@make_box
def BonusBox():
    return _coin("Bonus")


@make_box
def BonusBoxLid():
    return _caplid([coin_box_width, coin_box_length, coin_box_height], "Bonus")


if FROM_MAKE != 1:
    CaveCardBox().show()
