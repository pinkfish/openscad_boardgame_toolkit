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

# LibFile: examples/maglev_metro.py
#    PythonSCAD port of maglev_metro.scad. rotate(a) -> .rotate([0,0,a]); MetroTile is a small
#    helper (3 hex polygons); the SpacerTop uses MakePathBoxWithNoLid with a custom path.

import types

from base_bgtk import *
from bosl2.shapes3d import cuboid
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from no_lid import MakeBoxWithNoLid, MakePathBoxWithNoLid
from components import FingerHoleBase, FingerHoleWall, RegularPolygon, CuboidWithIndentsBottom, PolygonRadiusFromApothem

box_height = 65
box_width = 286
box_length = 286
wt = default_wall_thickness

player_board_thickness = 2.2
game_board_thickness = 4.2
game_board_base_thickness = 4.2
game_board_base_width = 241

factory_hex_width = 56
factory_hex_thickness = 7.5
factory_hex_radius = PolygonRadiusFromApothem(factory_hex_width, 6)

player_overlay_hex_width = 55.5
player_overlay_hex_radius = PolygonRadiusFromApothem(player_overlay_hex_width, 6)
player_overlay_hex_thickness = 1.5
player_overlay_hex_per_player = 18

robot_width = 8.5
robot_length = 18.5
robot_thickness = 8

start_token_diameter = 45.5
train_width = 14
train_length = 41.5
train_thickness = 10

card_width = 67
card_length = 90

card_box_width = wt * 2 + card_width
card_box_length = wt * 2 + card_length
card_box_height = (box_height - game_board_base_thickness * 2 - player_board_thickness * 4) / 2

robot_box_width = card_box_width - 10
robot_box_length = box_length - card_box_length * 2
robot_box_height = card_box_height / 2

commuter_box_width = robot_box_width
commuter_box_length = robot_box_length / 2
commuter_box_height = robot_box_height

commuter_box_small_width = box_width - game_board_base_width
commuter_box_small_length = wt * 2 + robot_width * 7 + 2
commuter_box_small_height = box_height - card_box_height * 2

start_token_box_width = 10
start_token_box_length = robot_box_length
start_token_box_height = box_height

player_box_width = wt * 2 + player_overlay_hex_width
player_box_length = box_width / 2
player_box_height = (box_height - game_board_base_thickness * 2 - player_board_thickness * 4 - game_board_thickness * 2) / 2

factory_tile_box_width = (box_width - card_box_width - player_box_width) / 2
factory_tile_box_length = box_width / 4
factory_tile_box_height = player_box_height

metro_box_width = box_width - card_box_width - player_box_width
metro_box_length = box_length - factory_tile_box_length * 2
metro_box_height = factory_tile_box_height

spacer_box_width = metro_box_width
spacer_box_length = metro_box_length + factory_tile_box_length - 2
spacer_box_height = factory_tile_box_height * 2 - metro_box_height
spacer_box_top_height = commuter_box_small_height


def MetroTile(thickness=2):
    tile = None
    for i in range(3):
        hexp = RegularPolygon(factory_hex_width, height=thickness, shape_edges=6).translate([factory_hex_radius, 0, 0]).rotate([0, 0, i * 120])
        tile = hexp if tile is None else tile | hexp
    return tile


@make_box
def CardBox():
    def cavity(iw, il, ih):
        return cube([iw, il, box_height])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=20, height=card_box_height - default_lid_thickness).translate([iw / 2.0, 0, -default_floor_thickness])

    return MakeBoxWithSlidingLid(size=[card_box_width, card_box_length, card_box_height], lid_thickness=4, children=[cavity, finger])


def _card_lid(text):
    return SlidingBoxLidWithLabel(size=[card_box_width, card_box_length, card_box_height], text_str=text, lid_thickness=4)


@make_box
def CardBoxLidDirectConnection():
    return _card_lid("Connection")


@make_box
def CardBoxLidPassenger():
    return _card_lid("Passenger")


@make_box
def CardBoxLidTrack():
    return _card_lid("Track")


@make_box
def CardBoxLidPlayerBoard():
    return _card_lid("Player Board")


@make_box
def FactoryTileBox(colour="yellow"):
    def hexp(iw, il, ih):
        return RegularPolygon(width=factory_hex_width, height=factory_tile_box_height, shape_edges=6).rotate([0, 0, 90]).translate([iw / 2, il / 2, ih - factory_hex_thickness * 2])

    def finger(iw, il, ih):
        return FingerHoleWall(radius=17, height=factory_hex_thickness * 2, spin=90, rounding_edge=wt / 2, round_back=False, round_front=True, depth_of_hole=wt * 10 + 0.03).translate([wt * 4, il / 2, ih - factory_hex_thickness * 2])

    return MakeBoxWithSlidingLid(size=[factory_tile_box_length, factory_tile_box_width, factory_tile_box_height], spin=90, anchor=BACK + BOTTOM + LEFT, material_colour=colour, children=[hexp, finger])


def _factory_lid(text):
    return SlidingBoxLidWithLabel(size=[factory_tile_box_length, factory_tile_box_width], text_str=text)


@make_box
def FactoryTileBoxLid():
    return _factory_lid("Factories")


@make_box
def FactoryTileBoxLidWarehouse():
    return _factory_lid("Warehouses")


@make_box
def FactoryTileBoxLidLabs():
    return _factory_lid("Labs")


@make_box
def FactoryTileBoxLidOffices():
    return _factory_lid("Offices")


@make_box
def FactoryTileBoxLidStores():
    return _factory_lid("Stores")


@make_box
def FactoryTileBoxLidEmbassies():
    return _factory_lid("Embassies")


@make_box
def PlayerBox(colour="green"):
    depth = player_overlay_hex_per_player * player_overlay_hex_thickness / 2 + 1

    def hex1(iw, il, ih):
        return RegularPolygon(width=player_overlay_hex_width, height=depth + 0.5, shape_edges=6).rotate([0, 0, 90]).translate([player_overlay_hex_radius - 0.5, player_overlay_hex_width / 2, ih - depth])

    def hex2(iw, il, ih):
        return RegularPolygon(width=player_overlay_hex_width, height=depth + 0.5, shape_edges=6).rotate([0, 0, 90]).translate([iw - player_overlay_hex_radius + 0.5, player_overlay_hex_width / 2, ih - player_overlay_hex_per_player * player_overlay_hex_thickness / 2 - 1])

    def finger1(iw, il, ih):
        return FingerHoleWall(radius=14, height=player_box_height - default_lid_thickness - default_floor_thickness, spin=0, depth_of_hole=wt + 0.03, rounding_edge=wt / 2, round_back=False).translate([player_overlay_hex_radius, -wt / 2 - 0.01, 0])

    def finger2(iw, il, ih):
        return FingerHoleWall(radius=14, height=player_box_height - default_lid_thickness - default_floor_thickness, spin=0, depth_of_hole=wt + 0.03, rounding_edge=wt / 2, round_back=False).translate([iw - player_overlay_hex_radius, -wt / 2 - 0.01, 0])

    def train_tray(iw, il, ih):
        return CuboidWithIndentsBottom([train_length, train_width, train_thickness + 1], finger_holes=[], finger_hole_radius=10, rounding=2, edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT, BOTTOM + LEFT, BOTTOM + RIGHT], anchor=BOTTOM).translate([iw / 2, il / 2, ih - train_thickness])

    def train_slot(iw, il, ih):
        return cuboid([20, train_length, train_thickness + 1], anchor=BOTTOM, rounding=10, edges=[BOTTOM + LEFT, BOTTOM + RIGHT]).translate([iw / 2, il / 2, ih - train_thickness])

    return MakeBoxWithSlidingLid(size=[player_box_length, player_box_width, player_box_height], material_colour=colour, spin=90, anchor=BACK + BOTTOM + LEFT, children=[hex1, hex2, finger1, finger2, train_tray, train_slot])


@make_box
def PlayerBoxLid():
    return SlidingBoxLidWithLabel(size=[player_box_length, player_box_width], text_str="Player")


@make_box
def RobotBox(colour="silver"):
    def kids(inner):
        return [InnerObject(cuboid([robot_length * 3, robot_width * 18 / 3, robot_thickness + 1], anchor=BOTTOM).translate([inner.width / 2, inner.length / 2, inner.height - robot_thickness - 0.5]))]

    return MakeBoxWithCapLid(size=[robot_box_width, robot_box_length, robot_box_height], material_colour=colour, children=kids)


@make_box
def RobotBoxLid():
    return CapBoxLidWithLabel(size=[robot_box_width, robot_box_length, robot_box_height], text_str="Robots")


@make_box
def CommuterBox(colour="purple"):
    def kids(inner):
        return [InnerObject(cuboid([robot_length * 3, robot_width * 5, robot_thickness + 1], anchor=BOTTOM).translate([inner.width / 2, inner.length / 2, inner.height - robot_thickness - 0.5]))]

    return MakeBoxWithCapLid(size=[commuter_box_width, commuter_box_length, commuter_box_height], material_colour=colour, children=kids)


@make_box
def CommuterBoxLid():
    return CapBoxLidWithLabel(size=[commuter_box_width, commuter_box_length, commuter_box_height], text_str="Commuter")


@make_box
def CommuterBoxSmall(colour="yellow"):
    def kids(inner):
        return [InnerObject(cuboid([robot_length * 2, robot_width * 7, robot_thickness + 1], anchor=BOTTOM).translate([inner.width / 2, inner.length / 2, inner.height - robot_thickness - 0.5]))]

    return MakeBoxWithCapLid(size=[commuter_box_small_width, commuter_box_small_length, commuter_box_small_height], material_colour=colour, children=kids)


@make_box
def CommuterBoxSmallLid():
    return CapBoxLidWithLabel(size=[commuter_box_small_width, commuter_box_small_length, commuter_box_small_height], text_str="Commuter")


@make_box
def MetroTileBox(colour="yellow"):
    def tile(iw, il, ih):
        return MetroTile(thickness=factory_hex_thickness + 1).rotate([0, 0, 90]).translate([factory_hex_radius * 3 / 2, factory_hex_width, ih - factory_hex_thickness])

    def hexp(iw, il, ih):
        return RegularPolygon(width=factory_hex_width, height=metro_box_height, shape_edges=6).rotate([0, 0, 90]).translate([iw - factory_hex_radius, il - factory_hex_width / 2, ih - factory_hex_thickness * 2])

    return MakeBoxWithSlidingLid(size=[metro_box_length, metro_box_width, metro_box_height], spin=90, anchor=BACK + BOTTOM + LEFT, material_colour=colour, children=[tile, hexp])


@make_box
def MetroTileBoxLid():
    return SlidingBoxLidWithLabel(size=[metro_box_length, metro_box_width], text_str="Metro & Studios")


@make_box
def StartTokenBox():
    def kids(iw, il, ih):
        return cuboid([iw, start_token_diameter, start_token_diameter + 1], anchor=BOTTOM, rounding=start_token_diameter / 2, edges=[FRONT + BOTTOM, BACK + BOTTOM]).translate([iw / 2, il / 2, ih - start_token_diameter])

    return MakeBoxWithNoLid(size=[start_token_box_width, start_token_box_length, start_token_box_height], finger_hole_size=20, children=[kids])


@make_box
def SpacerBox():
    return MakeBoxWithNoLid(size=[spacer_box_width, spacer_box_length, spacer_box_height], hollow=True)


@make_box
def SpacerTop():
    length = box_length - commuter_box_small_length * 2
    small_width = start_token_box_width + 1
    start_length = length - start_token_box_length - 1
    path = [
        [0, 0],
        [commuter_box_small_width, 0],
        [commuter_box_small_width, length],
        [small_width, length],
        [small_width, start_length],
        [0, start_length],
    ]
    return MakePathBoxWithNoLid(path=path, height=spacer_box_top_height, hollow=True)


if FROM_MAKE != 1:
    CardBox().show()
