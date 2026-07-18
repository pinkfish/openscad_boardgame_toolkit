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

# LibFile: examples/splendor.py
#    PythonSCAD port of splendor.scad. SplendorBoxInside is a stand-alone token-holder insert
#    hand-built from bosl2 cyl/cuboid. wall=4, lid=3 passed explicitly.

import math

from base_bgtk import *
from bosl2.shapes3d import cuboid, cyl
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from components import FingerHoleBase

wall = 4
lid = 3
floor = default_floor_thickness
inner_wall = 2

disc_d = 44.5
disc_thickness = 3.5
disc_number = 40
nobel_width = 61.5
nobel_thickness = 2
card_width = 65
card_length = 89.5
single_card_thickness = 6 / 10

box_width = card_length + wall * 2 + 1
box_length = wall * 4 + (disc_d + 1) * 3
box_height = disc_thickness * math.ceil(disc_number / 6) + lid * 3 + nobel_thickness * 5 + single_card_thickness * 45 + 1

size = [box_width, box_length, box_height]


@make_box
def SplendorBox():
    def nobel(y):
        return lambda iw, il, ih: cuboid([nobel_width, nobel_width, box_height], rounding=2, edges=[FRONT + RIGHT, BACK + RIGHT], anchor=BOTTOM).translate([iw / 2, y(il), 0])

    def card(y):
        return lambda iw, il, ih: cuboid([card_length, card_width, box_height], rounding=1, edges=[FRONT + RIGHT, BACK + RIGHT], anchor=BOTTOM).translate([iw / 2, y(il), nobel_thickness * 5 + 0.5])

    def top(iw, il, ih):
        return cuboid([iw, il, box_height], anchor=BOTTOM, rounding=1).translate([iw / 2, il / 2, nobel_thickness * 5 + 0.5 + single_card_thickness * 45])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=15, height=box_height - floor).translate([iw / 2, 0, -floor - 0.5])

    def base(iw, il, ih):
        return cuboid([40, box_length * 2 - 20, box_height], rounding=15, anchor=BOTTOM).translate([iw / 2, 0, 0])

    front = lambda il: card_width / 2
    back = lambda il: il - card_width / 2
    return MakeBoxWithSlidingLid(size=size, wall_thickness=wall, children=[nobel(front), nobel(back), card(front), card(back), top, finger, base])


@make_box
def SplendorBoxInside():
    h = disc_thickness * math.ceil(disc_number / 6)

    def token_cylinder():
        return cyl(d=disc_d + inner_wall * 2, anchor=BOTTOM, h=h + 0.5) - cyl(d=disc_d, anchor=BOTTOM, h=h + 2).translate([0, 0, -0.5])

    inner_length = box_length - wall * 2 - 1
    inner_width = box_width - wall * 2 - 1

    parts = cuboid([inner_length, inner_width, inner_wall], anchor=BOTTOM)
    for i in range(3):
        x = inner_length / 2 - disc_d / 2 - inner_wall - i * (disc_d + inner_wall + 1)
        top_col = token_cylinder()
        if i == 2:
            top_col = top_col | cyl(d=disc_d + inner_wall * 2 - 1, anchor=BOTTOM, h=disc_thickness * 2).translate([0, 0, -0.01])
        parts = parts | top_col.translate([x, inner_width / 2 - disc_d / 2 - inner_wall / 2 + 0.6, lid])
        parts = parts | token_cylinder().translate([x, -inner_width / 2 + disc_d / 2 + inner_wall / 2 - 0.6, lid])

    result = parts
    result = result - cuboid([inner_width, inner_width + 1, box_height], anchor=BOTTOM + LEFT).translate([inner_length / 2, 0, 0])
    result = result - cuboid([inner_width, inner_width + 1, box_height], anchor=BOTTOM + RIGHT).translate([-inner_length / 2, 0, 0])
    result = result - cuboid([box_length, 10, box_height], anchor=BOTTOM).translate([0, inner_width / 2, inner_wall - 0.01])
    result = result - cuboid([inner_length, 10, box_height], anchor=BOTTOM).translate([0, -inner_width / 2, inner_wall - 0.01])
    result = result - cuboid([inner_length, 10, box_height], anchor=BOTTOM).translate([0, 0, floor])
    return result.color(default_material_colour)


@make_box
def SplendorBoxLid():
    return SlidingBoxLidWithLabel(size=size, wall_thickness=wall, lid_thickness=lid, text_str="Splendor")


if FROM_MAKE != 1:
    SplendorBox().show()
