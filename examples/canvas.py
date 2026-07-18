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

# LibFile: examples/canvas.py
#    PythonSCAD port of canvas.scad. The shared MakeLid() helper (not a `make` section) returns
#    a labelled cap lid with a circle pattern; DividerPiece is hand-built from bosl2 cuboids
#    (a difference for the cut-outs, unioned with the uprights).

from base_bgtk import *
from bosl2.shapes3d import cuboid
from cap_box import MakeBoxWithCapLid, CapBoxLidWithLabel
from components import RoundedBoxAllSides
from shape_type import MakeShapeObject, ShapeType

canvas_piece_box_width = 41
canvas_piece_box_length = 73
canvas_piece_box_height = 29
wall_thickness = 3

divider_middle_width = 50
divider_thickness = 1
divider_length = 124
divider_height = 30
divider_total_width = 73 + 50 + 73
divider_upright_length = 45
divider_upright_diff = 73

_ROUND_EDGES = [FRONT + RIGHT, FRONT + LEFT, BACK + RIGHT, BACK + LEFT]


def MakeLid(text):
    return CapBoxLidWithLabel(
        size=[canvas_piece_box_width, canvas_piece_box_length, canvas_piece_box_height],
        text_str=text, wall_thickness=wall_thickness, lid_thickness=2, lid_boundary=5, layout_width=5,
        shape_options=MakeShapeObject(shape_type=ShapeType.CIRCLE, shape_thickness=1.5, shape_width=7),
    )


@make_box
def PiecesBox():
    def kids(inner):
        return [InnerObject(RoundedBoxAllSides([inner.width, inner.length, canvas_piece_box_height], radius=5))]

    return MakeBoxWithCapLid(
        size=[canvas_piece_box_width, canvas_piece_box_length, canvas_piece_box_height],
        wall_thickness=wall_thickness, lid_thickness=2, lid_finger_hold_len=14, children=kids,
    )


@make_box
def PiecesBoxLidRed():
    return MakeLid("Red")


@make_box
def PiecesBoxLidGreen():
    return MakeLid("Green")


@make_box
def PiecesBoxLidGrey():
    return MakeLid("Grey")


@make_box
def PiecesBoxLidBlue():
    return MakeLid("Blue")


@make_box
def PiecesBoxLidPurple():
    return MakeLid("Purple")


@make_box
def PiecesBoxLidPalette():
    return MakeLid("Palette")


@make_box
def DividerPiece():
    def cut(size, pos):
        return cuboid(size, rounding=5, edges=_ROUND_EDGES, anchor=BOTTOM + LEFT + FRONT).translate(pos)

    plate = cuboid(
        [divider_total_width, divider_length, divider_thickness], rounding=5, edges=_ROUND_EDGES, anchor=BOTTOM + LEFT + FRONT
    )
    plate = plate - cut([divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1], [divider_upright_diff / 8, divider_length / 16, -0.5])
    plate = plate - cut([divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1], [divider_upright_diff / 8, divider_length * 8 / 16, -0.5])
    plate = plate - cut([divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1], [divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length / 16, -0.5])
    plate = plate - cut([divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1], [divider_upright_diff / 8 + divider_upright_diff + divider_middle_width, divider_length * 8 / 16, -0.5])
    plate = plate - cut([divider_middle_width * 3 / 4 - 2, divider_length * 12 / 16, divider_thickness + 1], [divider_upright_diff / 8 + divider_upright_diff - 2, divider_length / 8, -0.5])

    def upright(x, y):
        return cuboid([2, divider_upright_length, divider_height], anchor=BOTTOM + LEFT + FRONT, rounding=3, edges=[TOP + FRONT, TOP + BACK]).translate([x, y, 0])

    uprights = (
        upright(divider_upright_diff, 0)
        | upright(divider_upright_diff, divider_length - divider_upright_length)
        | upright(divider_upright_diff + divider_middle_width - 2, 0)
        | upright(divider_upright_diff + divider_middle_width - 2, divider_length - divider_upright_length - 2)
    )
    return (plate | uprights).color(default_material_colour)


if FROM_MAKE != 1:
    PiecesBox().show()
