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

# LibFile: examples/nature.py
#    PythonSCAD port of nature.scad (uses the toolkit default wall/floor/lid thicknesses).
#    Card boxes are factored through card_box(); DialBox has a hand-built disk cavity.

from base_bgtk import *
from pybosl2.shapes3d import cuboid
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from no_lid import MakeBoxWithNoLid
from components import RoundedBoxAllSides, FingerHoleBase, FingerHoleWall
from labels import MakeLabelOptions

box_width = 210
box_length = 210
box_height = 75
board_thickness = 7
disk_diameter = 46
disk_thickness = 4
leopard_length = 100
leopard_thickness = 10
card_length = 92
card_width = 67
single_card_thickness = 14 / 20

wt = default_wall_thickness
ft = default_floor_thickness
lt = default_lid_thickness

hunter_card_box_width = (box_width - 2) / 2
hunter_card_box_length = card_width + wt * 2
hunter_card_box_height = single_card_thickness * 20 + ft + lt + 1
solo_card_box_length = card_width + wt * 2
solo_card_box_width = (box_width - 2) / 2
solo_card_box_height = single_card_thickness * 6 + ft + lt + 1
dial_box_height = disk_diameter + wt + ft + 1
dial_box_width = leopard_length + wt * 2 + 1
dial_box_length = (box_width - hunter_card_box_width - 2) / 2
card_box_width = (box_width - 2) / 2
card_box_length = card_width + wt * 2
card_box_height = box_height - board_thickness - 1
resource_box_width = box_length - dial_box_width - 2
resource_box_length = (box_length - 2 - solo_card_box_length) / 2
resource_box_height = dial_box_height / 2
resource_box_double_length = box_length - 2 - solo_card_box_length
leopard_box_width = leopard_length + wt * 2 + 1
leopard_box_length = box_length - 2 - dial_box_length * 2 - card_box_length
leopard_box_height = dial_box_height
spacer_card_width = box_width - hunter_card_box_width - 1
spacer_card_length = hunter_card_box_length
spacer_card_height = card_box_height - solo_card_box_height - hunter_card_box_height
spacer_dial_box_width = box_width - 2
spacer_dial_box_length = box_length - 2 - card_box_length
spacer_dial_box_height = box_height - board_thickness - 2 - dial_box_height

FRAMELESS = MakeLabelOptions(label_type=LabelType.FRAMELESS)


def _sliding_card_box(box_size, fh_height):
    def cavity(iw, il, ih):
        return cube([card_width, card_length, card_box_height])

    def finger(iw, il, ih):
        return FingerHoleBase(radius=15, height=fh_height).translate([iw / 2, 0, -ft - lt + 0.01])

    return MakeBoxWithSlidingLid(size=box_size, spin=90, anchor=BACK + BOTTOM + LEFT, children=[cavity, finger])


def _resource(size):
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([inner.width, inner.length, resource_box_height], radius=5))]

    return MakeBoxWithCapLid(size=size, children=kids)


@make_box
def ResourceBox():
    return _resource([resource_box_width, resource_box_length, resource_box_height])


@make_box
def ResourceBoxDouble():
    return _resource([resource_box_width, resource_box_double_length, resource_box_height])


@make_box
def ResourceGrassBoxLid():
    return CapBoxLidWithLabel(size=[resource_box_width, resource_box_length, resource_box_height], text_str="Grass")


@make_box
def ResourceMeatBoxLid():
    return CapBoxLidWithLabel(size=[resource_box_width, resource_box_length, resource_box_height], text_str="Meat")


@make_box
def ResourcePopulationBoxLid():
    return CapBoxLidWithLabel(size=[resource_box_width, resource_box_double_length, resource_box_height], text_str="Population")


@make_box
def DialBox():
    def kids(inner):
        objs = [
            InnerObject(cuboid([dial_box_width + 10, disk_diameter / 2, disk_diameter], anchor=BOTTOM, rounding=disk_diameter / 4, edges=[FRONT + BOTTOM, BACK + BOTTOM]).translate([dial_box_width / 2, inner.length / 2, inner.height - disk_diameter / 2 - 5])),
            InnerObject(cuboid([dial_box_width + 10, disk_diameter / 2, disk_diameter / 4], anchor=BOTTOM, rounding=-disk_diameter / 4, edges=[FRONT + TOP, BACK + TOP]).translate([dial_box_width / 2, inner.length / 2, inner.height - disk_diameter / 4])),
        ]
        for i in range(10):
            objs.append(InnerObject(cuboid([disk_thickness + 0.5, disk_diameter, disk_diameter * 2], anchor=BOTTOM, rounding=disk_diameter / 4, edges=[FRONT + BOTTOM]).translate([disk_thickness / 2 + 5 + (disk_thickness + 5.6) * i, inner.length / 2, inner.height - disk_diameter - 1])))
        return objs

    return MakeBoxWithCapLid(size=[dial_box_width, dial_box_length, dial_box_height], children=kids)


@make_box
def DialBoxLid():
    return CapBoxLidWithLabel(size=[dial_box_width, dial_box_length, dial_box_height], text_str="Population", label_options=FRAMELESS)


@make_box
def LeopardBox():
    def slab(iw, il, ih):
        return cuboid([leopard_length, leopard_thickness + 1, leopard_box_height], anchor=BOTTOM).translate([iw / 2, il / 2, 0])

    def finger(iw, il, ih):
        return FingerHoleWall(radius=20, height=15, depth_of_hole=60).translate([iw / 2, 0, ih - 15 + lt + 0.01])

    return MakeBoxWithSlidingLid(size=[leopard_box_length, leopard_box_width, leopard_box_height], spin=90, anchor=BACK + BOTTOM + LEFT, children=[slab, finger])


@make_box
def LeopardBoxLid():
    return SlidingBoxLidWithLabel(size=[leopard_box_length, leopard_box_width], text_str="Leopard", label_options=FRAMELESS)


@make_box
def NatureCardBox():
    return _sliding_card_box([card_box_length, card_box_width, card_box_height], card_box_height)


@make_box
def NatureCardBoxLid():
    return SlidingBoxLidWithLabel(size=[card_box_length, card_box_width], text_str="Nature")


@make_box
def HunterCardBox():
    return _sliding_card_box([hunter_card_box_length, hunter_card_box_width, hunter_card_box_height], hunter_card_box_height)


@make_box
def HunterCardBoxLid():
    return SlidingBoxLidWithLabel(size=[hunter_card_box_length, hunter_card_box_width], text_str="Hunter")


@make_box
def SoloCardBox():
    return _sliding_card_box([solo_card_box_length, solo_card_box_width, solo_card_box_height], solo_card_box_height)


@make_box
def SoloCardBoxLid():
    return SlidingBoxLidWithLabel(size=[solo_card_box_length, solo_card_box_width], text_str="Solo")


@make_box
def SpacerCardBox():
    return MakeBoxWithNoLid(size=[spacer_card_width, spacer_card_length, spacer_card_height], hollow=True)


@make_box
def SpacerDialBox():
    return MakeBoxWithNoLid(size=[spacer_dial_box_width, spacer_dial_box_length, spacer_dial_box_height], hollow=True)


if FROM_MAKE != 1:
    DialBox().show()
