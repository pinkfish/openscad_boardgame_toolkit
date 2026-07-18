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

# LibFile: examples/sky_team.py
#    PythonSCAD port of sky_team.scad. The scad file overrides several lid globals
#    (default_lid_thickness=3, cloud lid pattern); Python copies don't inherit scad global
#    overrides, so they are passed explicitly through _slidelid/_caplid/box calls. The
#    document-only BoxLayout module is not ported.

from base_bgtk import *
from bosl2.shapes3d import cuboid, cyl, Bosl2Solid
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from components import CuboidWithIndentsBottom, FingerHoleWall, FingerHoleBase, RoundedBoxAllSides
from shape_type import ShapeType, MakeShapeObject

lid_th = 3

box_width = 177
box_length = 247
box_height = 49

double_board_thickness = 4
single_board_thickness = 2

wind_speed_direction_width = 81.5
wind_speed_direction_length = 81.5
wind_speed_corner_radius = 2

ice_brakes_width = 66
ice_brakes_length = 114

kerosene_board_length = 184
kerosene_board_width = 35.5

intern_board_length = 186
intern_board_width = 29.5

rules_player_stuff_thickness = 6

airplae_angle_thickness = 5

cards_width = 68
cards_length = 92

dice_width = 16.5
num__dice = 8

intern_width = 15.5
intern_length = 26
intern_top_length = 5
intern_top_width = 12
intern_bottom_top_width = 10

approach_track_length_8 = 236
approach_track_length_7 = 213
approach_track_length_6 = 181
approach_track_length_5 = 153
approach_track_thickness_5 = 7.75
approach_track_thickness_8 = 3.5
approach_track_thickness_7 = 5
approach_track_thickness_6 = 7
approach_track_width = 50.5

bottom_boxes_length = box_length - 2
bottom_boxes_width = (box_width - 2) / 2
bottom_boxes_height = default_lid_thickness + default_floor_thickness + airplae_angle_thickness + 0.5

approach_track_box_width = approach_track_width + default_wall_thickness * 2 + 1
appraoch_track_box_length = box_length - 2
approach_track_box_height = approach_track_thickness_5 + default_floor_thickness + default_lid_thickness + 2

dice_box_width = dice_width + default_wall_thickness * 2 + 2
dice_box_length = appraoch_track_box_length
dice_box_height = box_height - rules_player_stuff_thickness - double_board_thickness - bottom_boxes_height

buttons_box_width = approach_track_box_width
buttons_box_length = (box_length - 2) / 12
buttons_box_height = dice_box_height - approach_track_box_height

card_box_width = cards_length + default_wall_thickness * 2 + 1
card_box_length = cards_width + default_wall_thickness * 2 + 1
card_box_height = dice_box_height

spacer_width = box_width - approach_track_box_width - dice_box_width - 2
spacer_length = dice_box_length - card_box_length
spacer_height = dice_box_height

_SHAPE = MakeShapeObject(shape_type=ShapeType.CLOUD, shape_width=11, shape_thickness=1)


def _slidelid(size, text):
    return SlidingBoxLidWithLabel(size=size, text_str=text, lid_thickness=lid_th, layout_width=10.3, aspect_ratio=1.5, shape_options=_SHAPE)


def _caplid(size, text):
    return CapBoxLidWithLabel(size=size, text_str=text, lid_thickness=lid_th, layout_width=10.3, aspect_ratio=1.5, shape_options=_SHAPE)


def _u(*parts):
    """Union that unwraps Bosl2Solid to native first, so everything stays native (avoids the
    native-LEFT | Bosl2Solid-RIGHT compose bug)."""
    native = [p.shape if isinstance(p, Bosl2Solid) else p for p in parts]
    r = native[0]
    for p in native[1:]:
        r = r | p
    return r


def _hull(*parts):
    return hull(*[p.shape if isinstance(p, Bosl2Solid) else p for p in parts])


def WindSpeedPiece(height):
    c = wind_speed_corner_radius
    return _hull(
        cyl(r=c, anchor=BOTTOM, h=height).translate([c, c, 0]),
        cyl(r=c, anchor=BOTTOM, h=height).translate([c, wind_speed_direction_length - c, 0]),
        cyl(r=c, anchor=BOTTOM, h=height).translate([wind_speed_direction_width - c, c, 0]),
        cyl(d=wind_speed_direction_width, h=height, anchor=BOTTOM).translate([wind_speed_direction_width / 2, wind_speed_direction_length / 2, 0]),
    )


def InternPiece(height):
    part1 = cuboid([intern_width, intern_length - intern_top_length, height], anchor=BOTTOM, rounding=1, edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT]).translate([0, -intern_top_length / 2, 0])
    part2 = _hull(
        cyl(r=1, h=height, anchor=BOTTOM + RIGHT + BACK).translate([intern_top_width / 2, intern_length / 2, 0]),
        cyl(r=1, h=height, anchor=BOTTOM + LEFT + BACK).translate([-intern_top_width / 2, intern_length / 2, 0]),
        cuboid([1, 1, height], anchor=BOTTOM + LEFT + BACK).translate([-intern_bottom_top_width / 2, intern_length / 2 - intern_top_length, 0]),
        cuboid([1, 1, height], anchor=BOTTOM + RIGHT + BACK).translate([intern_bottom_top_width / 2, intern_length / 2 - intern_top_length, 0]),
    )
    return _u(part1, part2)


@make_box
def BasePiecesOne():
    def kerosene(iw, il, ih):
        board = CuboidWithIndentsBottom([kerosene_board_width, kerosene_board_length, double_board_thickness + 0.6], anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT], finger_hole_radius=10)
        t = text("Kerosene", halign="center", valign="center", size=10).linear_extrude(height=2).rotate([0, 0, 90]).translate([kerosene_board_width / 2, kerosene_board_length / 2, -1])
        return _u(board, t).translate([0, 8, ih - double_board_thickness - 0.5])

    def intern_board(iw, il, ih):
        board = CuboidWithIndentsBottom([intern_board_width, intern_board_length, single_board_thickness + 0.6], anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT], finger_hole_radius=15)
        t = text("Intern", halign="center", valign="center", size=10).linear_extrude(height=2).rotate([0, 0, 90]).translate([intern_board_width / 2, intern_board_length / 2, -1])
        return _u(board, t).translate([iw - intern_board_width, 10, ih - single_board_thickness - 0.5])

    def interns(iw, il, ih):
        pieces = []
        for i in range(6):
            piece = InternPiece(single_board_thickness + 1)
            t = text(str(i + 1), halign="center", valign="center", size=10).linear_extrude(height=2).translate([0, 0, -1])
            fin = cyl(r=9, h=20, rounding=5, anchor=BOTTOM).translate([0, intern_length / 2, 0])
            pieces.append(_u(piece, t, fin).translate([iw / 2 + 3, 19 + (intern_length + 14) * i, ih - single_board_thickness - 0.5]))
        # 7th one
        piece = InternPiece(single_board_thickness + 1)
        t = text("7", halign="center", valign="center", size=10).linear_extrude(height=2).translate([0, 0, -1])
        fin = cyl(r=9, h=20, rounding=5, anchor=BOTTOM).translate([0, intern_length / 2, 0])
        pieces.append(_u(piece, t, fin).translate([iw / 2 + 3 - intern_width - 5, 19 + (intern_length + 14) * 5, ih - single_board_thickness - 0.5]))
        return _u(*pieces)

    return MakeBoxWithSlidingLid(size=[bottom_boxes_width, bottom_boxes_length, bottom_boxes_height], lid_thickness=lid_th, children=[kerosene, intern_board, interns])


@make_box
def BasePiecesTwo():
    def ice_brakes(iw, il, ih):
        board = CuboidWithIndentsBottom([ice_brakes_width, ice_brakes_length, double_board_thickness + 0.6], anchor=BOTTOM + LEFT + FRONT, finger_positions=[BACK, FRONT], finger_hole_radius=20)
        t = text("Ice Brakes", halign="center", valign="center", size=10).linear_extrude(height=2).rotate([0, 0, 90]).translate([ice_brakes_width / 2, ice_brakes_length / 2, -1])
        return _u(board, t).translate([10, 12, ih - double_board_thickness - 0.5])

    def wind(iw, il, ih):
        wp = WindSpeedPiece(single_board_thickness + 0.6)
        c1 = cyl(r=20, h=40, rounding=20, anchor=BOTTOM).translate([wind_speed_direction_width / 2, 0, 0])
        c2 = cyl(r=20, h=40, rounding=20, anchor=BOTTOM).translate([wind_speed_direction_width - 12, wind_speed_direction_length - 12, 0])
        t = text("Wind Speed", halign="center", valign="center", size=10).linear_extrude(height=2).rotate([0, 0, 135]).translate([wind_speed_direction_width / 2, wind_speed_direction_length / 2, -1])
        return _u(wp, c1, c2, t).translate([1, il - wind_speed_direction_length - 2, ih - single_board_thickness - 0.5])

    return MakeBoxWithSlidingLid(size=[bottom_boxes_width, bottom_boxes_length, bottom_boxes_height], lid_thickness=lid_th, children=[ice_brakes, wind])


@make_box
def BasePiecesLid():
    return _slidelid([bottom_boxes_width, bottom_boxes_length, bottom_boxes_height], "Sky Team")


@make_box
def ApproachTracks():
    def tracks(iw, il, ih):
        return _u(
            cube([approach_track_width + 1, approach_track_length_8, approach_track_thickness_8 + 1]).translate([0, 0, ih - approach_track_thickness_8 - 0.5]),
            cube([approach_track_width + 1, approach_track_length_7, approach_track_thickness_7 + 1.25]).translate([0, 0, ih - approach_track_thickness_7 - 1]),
            cube([approach_track_width + 1, approach_track_length_6, approach_track_thickness_6 + 1.75]).translate([0, 0, ih - approach_track_thickness_6 - 1.5]),
            cube([approach_track_width + 1, approach_track_length_5, approach_track_thickness_5 + 2.5]).translate([0, 0, ih - approach_track_thickness_5 - 2]),
        )

    def finger(iw, il, ih):
        return FingerHoleWall(radius=10, height=approach_track_thickness_5 + 2.01).translate([iw / 2, 0, 0])

    return MakeBoxWithSlidingLid(size=[approach_track_box_width, appraoch_track_box_length, approach_track_box_height], lid_thickness=lid_th, children=[tracks, finger])


@make_box
def ApproachTracksLid():
    return _slidelid([approach_track_box_width, appraoch_track_box_length, approach_track_box_height], "Approach")


@make_box
def DiceBox():
    def kids(inner):
        objs = []
        for i in range(num__dice):
            objs.append(InnerObject(cube([dice_width + 2, dice_box_width + 1, dice_width + 2.5]).translate([0, (dice_width + 0.75) * i + 10, inner.height - dice_width - 2])))
        objs.append(InnerObject(cyl(r=9, h=40, anchor=BOTTOM, rounding=4).translate([inner.width / 2, 10, 0])))
        objs.append(InnerObject(cyl(r=9, h=40, anchor=BOTTOM, rounding=4).translate([inner.width / 2, (dice_width + 0.75) * num__dice + 10 + dice_width / 2, 0])))
        return objs

    return MakeBoxWithCapLid(size=[dice_box_width, dice_box_length, dice_box_height], lid_thickness=lid_th, children=kids)


@make_box
def DiceBoxLid():
    return _caplid([dice_box_width, dice_box_length, dice_box_height], "Dice")


def _buttons(mult):
    def kids(iw, il, ih):
        return RoundedBoxAllSides([iw, il, ih + 5], radius=5)

    return MakeBoxWithSlidingLid(size=[buttons_box_width, buttons_box_length * mult, buttons_box_height], lid_thickness=lid_th, children=[kids])


@make_box
def ButtonsBox():
    return _buttons(1)


@make_box
def ButtonsBoxDouble():
    return _buttons(2)


@make_box
def ButtonsBoxOnePointFive():
    return _buttons(1.5)


@make_box
def ButtonsBoxTripple():
    return _buttons(3)


@make_box
def CardBox():
    def kids(iw, il, ih):
        return cube([iw, il, card_box_height])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=20, height=card_box_height, spin=0).translate([iw / 2, 0, -default_floor_thickness - default_lid_thickness + 0.01])

    return MakeBoxWithSlidingLid(size=[card_box_length, card_box_width, card_box_height], lid_thickness=lid_th, spin=90, anchor=BOTTOM + BACK + LEFT, children=[kids, finger])


@make_box
def CardsBoxLid():
    return _slidelid([card_box_length, card_box_width, card_box_height], "Sky Team")


@make_box
def SpacerBox():
    outer = cuboid([spacer_width, spacer_length, spacer_height], rounding=2, anchor=BOTTOM, edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT])
    inner = cuboid([spacer_width - default_wall_thickness * 2, spacer_length - default_wall_thickness * 2, spacer_height + 10], anchor=BOTTOM, rounding=1).translate([0, 0, default_floor_thickness])
    return (outer - inner).translate([spacer_width / 2, spacer_length / 2, 0]).color("purple")


@make_box
def ButtonsBoxLid():
    labels = [
        (1, "Button"),
        (2, "Alerts"),
        (2, "Pengiun"),
        (3, "Plane"),
        (1, "Marker"),
        (1, "Kero"),
        (2, "Stuff"),
    ]
    lids = []
    for i, (mult, txt) in enumerate(labels):
        lids.append(_slidelid([buttons_box_width, buttons_box_length * mult, buttons_box_height], txt).translate([(buttons_box_width + 10) * i, 0, 0]))
    return _u(*lids)


if FROM_MAKE != 1:
    BasePiecesOne().show()
