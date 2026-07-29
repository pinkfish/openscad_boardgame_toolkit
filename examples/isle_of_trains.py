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

# LibFile: examples/isle_of_trains.py
#    PythonSCAD port of isle_of_trains.scad. Cap-box children build hex/tile wells from
#    RegularPolygon / CuboidWithIndentsBottom / cuboid; rotate([90,0,0]) lays a hex on its side.

import math

from base_bgtk import *
from pybosl2.shapes3d import cuboid, cyl
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from components import RegularPolygon, CuboidWithIndentsBottom, FingerHoleBase, FingerHoleWall
from labels import MakeLabelOptions

box_width = 130
box_length = 180
box_height = 38
wall_thickness = 3
lid_thickness = 2

card_width = 62.5
card_length = 89
total_card_thickness = 40
token_thickness = 2

destination_tile_width = 17.5 + 0.5
destination_tile_length = 80 + 0.5
destination_tile_corner_radius = 5 - 0.5
track_tile_width = 20 + 0.5
track_tile_length = 90 + 0.5
ticket_tile_width = 30
ticket_tile_length = 80
train_token_length = 31.5
train_token_width = 17.5
train_token_thickness = 10
victory_hex_one_width = 18
victory_hex_three_width = 20
victory_hex_five_width = 21.5
victory_hex_ten_width = 24

num_track_tiles = 2
num_destination_tiles = 6
num_ticket_tiles = 10
num_victory_tokens = [12, 6, 4, 4]

destination_box_width = box_width - 1
destination_box_length = destination_tile_width + track_tile_width + 1 + wall_thickness * 2
destination_box_height = token_thickness * num_destination_tiles + 0.5 + lid_thickness * 2
victory_box_width = destination_box_width
victory_box_length = destination_box_length
victory_box_height = box_height - destination_box_height - 0.5
card_box_width = card_length + wall_thickness * 2 + 3
card_box_length = card_width + wall_thickness * 2 + 0.5
card_box_height = box_height - 1
middle_box_length = box_length - card_box_length - destination_box_length - 1
middle_box_height = box_height
middle_box_width = card_box_width
ticket_box_length = box_length - destination_box_length - 1
ticket_box_width = box_width - middle_box_width - 1
ticket_box_height = box_height - 1

BLACK = MakeLabelOptions(label_colour="black")


def TileRadius(width):
    return width / 2 / math.cos(math.radians(180 / 6))


@make_box
def DestinationBox():
    def kids(inner):
        mw = inner.width
        objs = []
        # destination tile well: a rounded-corner rectangular pocket
        well = cube([destination_tile_length, destination_tile_width, token_thickness * num_destination_tiles + 1]).translate([0, 0, destination_box_height - token_thickness * num_destination_tiles - 0.5 - lid_thickness * 2])
        for cx, cy in ((0, 0), (0, destination_tile_width), (destination_tile_length, 0), (destination_tile_length, destination_tile_width)):
            well = well - cyl(h=token_thickness * num_destination_tiles + 2, anchor=BOTTOM, r=destination_tile_corner_radius).translate([cx, cy, 0]).shape
        well = well.translate([(mw - destination_tile_length) / 2, 0, 0])
        objs.append(InnerObject(well))
        objs.append(InnerObject(FingerHoleWall(radius=10, height=token_thickness * num_destination_tiles + 1).translate([(mw - destination_tile_length) / 2 + destination_tile_length / 2, -0.1, 0])))
        # track tile
        track = CuboidWithIndentsBottom([track_tile_length, track_tile_width, token_thickness * num_destination_tiles + 1], finger_holes=[0, 4], finger_hole_radius=token_thickness * num_destination_tiles + 0.5).translate([(mw - track_tile_length) / 2 + track_tile_length / 2, destination_tile_width + 1 + track_tile_width / 2, destination_box_height - token_thickness * num_track_tiles - 0.5 - lid_thickness * 2])
        objs.append(InnerObject(track))
        return objs

    return MakeBoxWithCapLid(size=[destination_box_width, destination_box_length, destination_box_height], wall_thickness=wall_thickness, lid_thickness=2, children=kids)


@make_box
def DestinationBoxLid():
    return CapBoxLidWithLabel(size=[destination_box_width, destination_box_length, destination_box_height], lid_thickness=lid_thickness, text_str="Destinations", label_options=BLACK)


def _victory_stack(hexw, count, extra, radius_w, x, il, ih):
    bit_h = count * token_thickness + extra
    r = TileRadius(hexw)
    hexp = RegularPolygon(width=hexw, height=bit_h, shape_edges=6).rotate([90, 0, 0]).translate([x + r, (il - bit_h) / 2 + bit_h, ih - hexw / 2 - 0.4])
    tray = cuboid([r * 2, bit_h, hexw / 2 + 0.25], anchor=BOTTOM + FRONT + LEFT, rounding=-4, edges=[TOP + LEFT, TOP + RIGHT]).translate([x, (il - bit_h) / 2, ih - hexw / 2 - 0.4])
    finger = FingerHoleWall(radius=10, height=8, depth_of_hole=victory_box_width).translate([x + r, 2, ih - 8])
    return [InnerObject(hexp), InnerObject(tray), InnerObject(finger)]


@make_box
def VictoryBox():
    def kids(inner):
        objs = []
        one_r = TileRadius(victory_hex_one_width + 0.5)
        objs += _victory_stack(victory_hex_one_width + 0.5, num_victory_tokens[0], 2, one_r, 3.5, inner.length, inner.height)
        objs += _victory_stack(victory_hex_three_width + 0.5, num_victory_tokens[1], 1, TileRadius(victory_hex_three_width + 0.5), 10 + one_r * 2, inner.length, inner.height)
        # ten + five wells (RegularPolygon with drilled finger holes)
        ten_bit = token_thickness * num_victory_tokens[3] + 0.5
        ten_r = TileRadius(victory_hex_ten_width + 0.5)
        objs.append(InnerObject(RegularPolygon(width=victory_hex_five_width + 0.5, height=ten_bit + 0.5, shape_edges=6, finger_hole_radius=ten_bit, finger_holes=[3, 6]).translate([victory_box_width - victory_hex_ten_width, (inner.length - victory_hex_ten_width - 0.5) / 2 + victory_hex_ten_width / 2 + 0.25, inner.height - ten_bit])))
        five_bit = token_thickness * num_victory_tokens[2] + 0.5
        five_r = TileRadius(victory_hex_five_width + 0.5)
        objs.append(InnerObject(RegularPolygon(width=victory_hex_five_width + 0.5, height=five_bit + 0.5, shape_edges=6, finger_hole_radius=five_bit, finger_holes=[3, 6]).translate([victory_box_width - five_r * 2 - ten_r * 2 - 1, (inner.length - victory_hex_five_width - 0.5) / 2 + victory_hex_five_width / 2 + 0.25, inner.height - five_bit])))
        return objs

    return MakeBoxWithCapLid(size=[victory_box_width, victory_box_length, victory_box_height], wall_thickness=wall_thickness, lid_thickness=1, children=kids)


@make_box
def VictoryBoxLid():
    return CapBoxLidWithLabel(size=[victory_box_width, victory_box_length, victory_box_height], lid_thickness=lid_thickness, text_str="Victory", label_options=BLACK)


@make_box
def CardBox():
    def kids(inner):
        return [
            InnerObject(cube([card_length + 0.5, card_width + 0.5, card_box_height])),
            InnerObject(FingerHoleBase(radius=10, height=card_box_height).translate([0, card_width / 2 + 0.25, -2])),
        ]

    return MakeBoxWithCapLid(size=[card_box_width, card_box_length, card_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def CardBoxLid():
    return CapBoxLidWithLabel(size=[card_box_width, card_box_length, card_box_height], lid_thickness=lid_thickness, text_str="Cards", label_options=BLACK)


@make_box
def TicketBox():
    def kids(inner):
        objs = []
        stack = cube([token_thickness * num_ticket_tiles + 0.5, ticket_tile_length, ticket_tile_width + 1]).translate([(inner.width - token_thickness * num_ticket_tiles + 0.5) / 2, inner.length - ticket_tile_length - 2, inner.height - ticket_tile_width - 0.5])
        objs.append(InnerObject(stack))
        objs.append(InnerObject(FingerHoleWall(radius=10, height=ticket_tile_width / 2, spin=90, depth_of_hole=200).translate([(inner.width - token_thickness * num_ticket_tiles + 0.5) / 2, inner.length - ticket_tile_length - 2 + ticket_tile_length / 2, inner.height - ticket_tile_width - 0.5 + inner.height - 17])))
        train = CuboidWithIndentsBottom([train_token_width, train_token_length, train_token_thickness + 1], finger_holes=[2, 6], finger_hole_radius=9).translate([inner.width / 2, train_token_length / 2 + 7, inner.height - train_token_thickness - 0.5])
        objs.append(InnerObject(train))
        return objs

    return MakeBoxWithCapLid(size=[ticket_box_width, ticket_box_length, ticket_box_height], wall_thickness=wall_thickness, lid_thickness=lid_thickness, floor_thickness=lid_thickness, children=kids)


@make_box
def TicketBoxLid():
    return CapBoxLidWithLabel(size=[ticket_box_width, ticket_box_length, ticket_box_height], lid_thickness=lid_thickness, text_str="Isle of Trains", label_options=BLACK)


@make_box
def MiddleBox():
    outer = cuboid([middle_box_width, middle_box_length, middle_box_height], rounding=wall_thickness, anchor=BOTTOM + FRONT + LEFT)
    inner = cuboid([middle_box_width - wall_thickness * 2, middle_box_length - wall_thickness * 2, middle_box_height], rounding=1.5, anchor=BOTTOM + FRONT + LEFT).translate([wall_thickness, wall_thickness, lid_thickness])
    return (outer - inner).color(default_material_colour)


if FROM_MAKE != 1:
    DestinationBox().show()
