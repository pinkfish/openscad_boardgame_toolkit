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

# LibFile: examples/cascadero.py
#    PythonSCAD port of cascadero.scad. Sliding-box children are a list of callables
#    (inner_width, inner_length, inner_height) -> solid; the .scad `$inner_width`/`$inner_length`
#    become those parameters. wall_thickness=2 / lid_thickness=3 are passed explicitly.

from base_bgtk import *
from sliding_box import MakeBoxWithSlidingLid, SlidingBoxLidWithLabel
from components import RoundedBoxAllSides, RoundedBoxGrid
from labels import MakeLabelOptions

box_width = 212
box_height = 40
lid_thickness = 3
wall_thickness = 2
gap = 2
boards_height = 10

section_height = box_height - boards_height - 4
player_width = (box_width - gap) // 2
player_length = player_width
top_width = ((box_width - gap) - 40) // 2
top_length = top_width
herald_width = 40
first_width = 40
radius = 10

BLUE = MakeLabelOptions(label_colour="blue")
BLUE_R5 = MakeLabelOptions(label_colour="blue", radius=5)


def _rounded_section(box_size):
    def kids(inner_width, inner_length, inner_height):
        return RoundedBoxAllSides([inner_width, inner_length, section_height], radius=15)

    return MakeBoxWithSlidingLid(size=box_size, wall_thickness=wall_thickness, lid_thickness=lid_thickness, children=[kids])


@make_box
def SealsBox():
    return _rounded_section([top_width, top_length, section_height])


@make_box
def SealsBoxLid():
    return SlidingBoxLidWithLabel(size=[top_width, top_length, section_height], lid_thickness=lid_thickness, wall_thickness=wall_thickness, text_str="Seals", label_options=BLUE_R5)


@make_box
def FarmerBox():
    return _rounded_section([top_width, top_length, section_height])


@make_box
def FarmerBoxLid():
    return SlidingBoxLidWithLabel(size=[top_width, top_length, section_height], lid_thickness=lid_thickness, wall_thickness=wall_thickness, text_str="Farmer", label_options=BLUE)


@make_box
def HeraldBox():
    return _rounded_section([herald_width, top_length, section_height])


@make_box
def HeraldBoxLid():
    return SlidingBoxLidWithLabel(size=[herald_width, top_length, section_height], lid_thickness=lid_thickness, wall_thickness=wall_thickness, text_str="Herald", label_options=BLUE)


@make_box
def PlayerBox():
    def grid(inner_width, inner_length, inner_height):
        return RoundedBoxGrid([inner_width, first_width, section_height], radius=radius, rows=2, cols=1, all_sides=True)

    def rest(inner_width, inner_length, inner_height):
        return RoundedBoxAllSides([inner_width, inner_length - first_width, section_height], radius=radius).translate([0, first_width + wall_thickness, 0])

    return MakeBoxWithSlidingLid(size=[player_width, player_length, section_height], wall_thickness=wall_thickness, lid_thickness=lid_thickness, children=[grid, rest])


@make_box
def PlayerBoxLid():
    return SlidingBoxLidWithLabel(size=[player_width, player_length, section_height], lid_thickness=lid_thickness, wall_thickness=wall_thickness, text_str="Player", label_options=BLUE_R5)


if FROM_MAKE != 1:
    SealsBox().show()
