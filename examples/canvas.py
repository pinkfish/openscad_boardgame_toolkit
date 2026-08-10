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
#    PythonSCAD port of canvas.scad: a CapBox for Canvas pieces, six
#    colour-coded lids, and a standalone divider piece.
#
#    The .scad built a single ``MakeBoxWithCapLid`` for the pieces box,
#    then six separate ``CapBoxLidWithLabel`` calls for the colour lids.
#    Here one BoxKit box supplies both the body and the lid template;
#    each colour lid overrides only the label text. The divider is a
#    standalone 3D part, not a box.
#
# FileSummary: Canvas insert -- pieces box, colour lids and divider.
# FileGroup: Examples

import pybosl2.shapes3d as s3

from base_bgtk import (
    BACK,
    BOTTOM,
    FROM_MAKE,
    FRONT,
    LEFT,
    MAKE_MMU,
    RIGHT,
    TOP,
    InnerObject,
    LabelType,
    make_box,
)
from box_base import BoxKit, Label, Lid
from cap_box import CapBox
from labels import MakeLabelOptions
from shape_type import MakeShapeObject, ShapeType

# ---- Measurements (from canvas.scad) -----------------------------------------
canvas_piece_box_width = 41
canvas_piece_box_length = 73
canvas_piece_box_height = 29
wall_thickness = 3
lid_thickness = 2

divider_middle_width = 50
divider_thickness = 1
divider_length = 124
divider_height = 30
divider_total_width = 73 + 50 + 73
divider_upright_length = 45
divider_upright_diff = 73

# ---- Shared lid style (MakeLid from the .scad) ------------------------------
_BASE_LID = Lid(
    boundary=5,
    layout_width=5,
    shape_options=MakeShapeObject(
        shape_type=ShapeType.CIRCLE,
        shape_thickness=1.5,
        shape_width=7,
    ),
    label=Label("", options=MakeLabelOptions(
        label_type=LabelType.FRAMED_SOLID if MAKE_MMU else LabelType.FRAMED,
    )),
)

# ---- PiecesBox ---------------------------------------------------------------
_pieces_box = BoxKit(
    CapBox,
    wall_thickness=wall_thickness,
    lid_thickness=lid_thickness,
).box(
    size=[canvas_piece_box_width, canvas_piece_box_length, canvas_piece_box_height],
    label="PiecesBox",
    contents=lambda inner: [
        InnerObject(s3.cuboid(
            [inner.width, inner.length, canvas_piece_box_height],
            rounding=5,
            anchor=BOTTOM,
        )),
    ],
)


@make_box
def PiecesBox():
    return _pieces_box.make_box()


# Each colour lid is a separate @make_box target calling a shared factory.
def _colour_lid(colour: str):
    return _pieces_box.make_lid(lid=_BASE_LID.with_label(colour))


@make_box(colour=["Red", "Green", "Grey", "Blue", "Purple", "Palette"])
def PiecesBoxLid(colour="Red"):
    return _colour_lid(colour)


# ---- DividerPiece ------------------------------------------------------------
# Standalone part: a flat plate with cutouts and upright prongs.
def _make_divider():
    plate_rounding = 5
    plate_edges = [FRONT + RIGHT, FRONT + LEFT, LEFT + BACK, RIGHT + BACK]

    plate = s3.cuboid(
        [divider_total_width, divider_length, divider_thickness],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    )

    # Left-side cutouts
    plate -= s3.cuboid(
        [divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    ).translate([divider_upright_diff / 8, divider_length / 16, -0.5])

    plate -= s3.cuboid(
        [divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    ).translate([divider_upright_diff / 8, divider_length * 8 / 16, -0.5])

    # Right-side cutouts
    right_x = divider_upright_diff / 8 + divider_upright_diff + divider_middle_width
    plate -= s3.cuboid(
        [divider_upright_diff * 3 / 4, divider_length * 12 / 32, divider_thickness + 1],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    ).translate([right_x, divider_length / 16, -0.5])

    plate -= s3.cuboid(
        [divider_upright_diff * 3 / 4, divider_length * 13 / 32, divider_thickness + 1],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    ).translate([right_x, divider_length * 8 / 16, -0.5])

    # Middle cutout
    plate -= s3.cuboid(
        [divider_middle_width * 3 / 4 - 2, divider_length * 12 / 16, divider_thickness + 1],
        rounding=plate_rounding,
        edges=plate_edges,
        anchor=BOTTOM + LEFT + FRONT,
    ).translate([divider_upright_diff / 8 + divider_upright_diff - 2, divider_length / 8, -0.5])

    # Uprights: four posts along the edges
    upright_edges = [TOP + FRONT, TOP + LEFT + BACK]
    left_post_x = divider_upright_diff
    right_post_x = divider_upright_diff + divider_middle_width - 2

    plate |= s3.cuboid(
        [2, divider_upright_length, divider_height],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=3,
        edges=upright_edges,
    ).translate([left_post_x, 0, 0])

    plate |= s3.cuboid(
        [2, divider_upright_length, divider_height],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=3,
        edges=upright_edges,
    ).translate([left_post_x, divider_length - divider_upright_length, 0])

    plate |= s3.cuboid(
        [2, divider_upright_length, divider_height],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=3,
        edges=upright_edges,
    ).translate([right_post_x, 0, 0])

    plate |= s3.cuboid(
        [2, divider_upright_length, divider_height],
        anchor=BOTTOM + LEFT + FRONT,
        rounding=3,
        edges=upright_edges,
    ).translate([right_post_x, divider_length - divider_upright_length - 2, 0])

    return plate


@make_box
def DividerPiece():
    return _make_divider()


# ---- Preview ------------------------------------------------------------------
if FROM_MAKE != 1:
    PiecesBox()
