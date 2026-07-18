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

# LibFile: examples/moonrakers.py
#    PythonSCAD port of moonrakers.scad. Ten near-identical card boxes, factored through a
#    card_box() helper (a sliding box with a card cavity + finger hole, one filament colour each).

from base_bgtk import *
from sliding_box import MakeBoxWithSlidingLid
from components import FingerHoleBase

ten_cards_thickness = 6
single_card_thickness = ten_cards_thickness / 10

card_width = 67
card_length = 90

card_box_width = default_wall_thickness * 2 + card_length
card_box_length = default_wall_thickness * 2 + card_width


def _height(num_cards, extra):
    return default_floor_thickness + default_lid_thickness + single_card_thickness * num_cards + extra


def card_box(height, colour):
    # Two separate children (the .scad has a cube and a finger hole): the cube is a native
    # solid and FingerHoleBase is a Bosl2Solid, and `native | Bosl2Solid` doesn't compose
    # cleanly (native's operator won't fall back to the wrapper), so keep them as list entries.
    def cavity(iw, il, ih):
        return cube([iw, il, height])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=17, height=height - default_lid_thickness, spin=0).translate([iw / 2, 0, -2])

    return MakeBoxWithSlidingLid(
        size=[card_box_length, card_box_width, height], spin=90, anchor=BACK + BOTTOM + LEFT, material_colour=colour, children=[cavity, finger]
    )


@make_box
def ThrusterCardBox():
    return card_box(_height(25, 2), "yellow")


@make_box
def DamageCardBox():
    return card_box(_height(35, 2), "red")


@make_box
def ReactorCardBox():
    return card_box(_height(30, 0.5), "blue")


@make_box
def MissCardBox():
    return card_box(_height(15, 0.5), "grey")


@make_box
def ShieldCardBox():
    return card_box(_height(25, 1.5), "green")


@make_box
def ReferenceCardBox():
    return card_box(_height(10, 0), "white")


@make_box
def CrewCardBox():
    return card_box(_height(20 + 10, 1), "orange")


@make_box
def ContractCardBox():
    return card_box(_height(40 + 10, 1), "purple")


@make_box
def ShipCardBox():
    return card_box(_height(37 + 10, 1), None)


@make_box
def ObjectiveCardBox():
    return card_box(_height(23 + 10, 1), None)


if FROM_MAKE != 1:
    ThrusterCardBox().show()
