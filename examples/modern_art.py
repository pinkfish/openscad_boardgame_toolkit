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

# LibFile: examples/modern_art.py
#    PythonSCAD port of modern_art.scad. Cap-box children use the cap_box protocol: a
#    callable(inner_size) returning a list of InnerObject (each carved from the interior by
#    default); the .scad `$inner_length` becomes inner_size.length. Global-default overrides
#    (default_wall_thickness = 3) are passed explicitly. `@make_box` marks the build sections.

from base_bgtk import *
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from components import FingerHoleBase, RoundedBoxAllSides
from labels import MakeLabelOptions

box_length = 208
box_width = 154
box_height = 44
board_thickness = 6

wall_thickness = 3
floor_thickness = 2

card_width = 61
card_length = 93

card_box_width = wall_thickness * 2 + card_length
card_box_length = box_width - 3
card_box_height = box_height - board_thickness

token_box_width = box_length - card_box_width - 3
token_box_length = box_width - 3
token_box_height = card_box_height


@make_box
def CardBox():
    def kids(inner):
        return [
            InnerObject(cube([card_length, card_width, card_box_height])),
            InnerObject(cube([card_length, card_width, card_box_height]).translate([0, inner.length - card_width, 0])),
            InnerObject(FingerHoleBase(radius=15, height=card_box_height).translate([0, card_width / 2, -floor_thickness - 0.5])),
            InnerObject(FingerHoleBase(radius=15, height=card_box_height).translate([0, inner.length - card_width / 2, -floor_thickness - 0.5])),
        ]

    return MakeBoxWithCapLid(size=[card_box_width, card_box_length, card_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def CardBoxLid():
    return CapBoxLidWithLabel(size=[card_box_width, card_box_length, card_box_height], wall_thickness=wall_thickness, text_str="Tokens")


@make_box
def TokensBox():
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([inner.width, inner.length, token_box_height], radius=15))]

    return MakeBoxWithCapLid(size=[token_box_width, token_box_length, token_box_height], wall_thickness=wall_thickness, children=kids)


@make_box
def TokensBoxLid():
    return CapBoxLidWithLabel(
        size=[token_box_width, token_box_length, token_box_height],
        wall_thickness=wall_thickness,
        text_str="Modern Art",
        label_options=MakeLabelOptions(font="Marker Felt:style=Regular"),
    )


if FROM_MAKE != 1:
    TokensBoxLid().show()
