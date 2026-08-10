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

# LibFile: examples/splendor_wide.py
#    PythonSCAD port of splendor_wide.scad: a slipover-lid box holding
#    Splendor's discs, cards and noble tiles.
#
#    The .scad built the disc channel as two overlapping negative cuboids
#    (rounded-bottom plus flat-top cap) and plain cuboids for cards and
#    nobles, all hand-positioned via translate. Here they are InnerObject
#    entries placed at the same coordinates in the interior frame -- the
#    direct analogue of the .scad children block.
#
# FileSummary: Splendor wide insert -- discs, cards and nobles.
# FileGroup: Examples

import pybosl2.shapes3d as s3

from base_bgtk import (
    BOTTOM,
    FROM_MAKE,
    LEFT,
    MAKE_MMU,
    RIGHT,
    InnerObject,
    LabelType,
    ObjectType,
    default_floor_thickness,
    make_box,
)
from box_base import BoxKit, BoxSpec, Label, Lid
from labels import MakeLabelOptions
from shape_type import MakeShapeObject, ShapeType
from slipover_box import SlipoverBox

# ---- Game measurements (from splendor_wide.scad) -------------------------------
wall_thickness = 4
lid_thickness = 3

splendor_disc_diameter = 44.5
splendor_disc_thickness = 3.5
splendor_disc_number = 40
splendor_nobel_width = 61.5
splendor_card_width = 65
splendor_card_length = 89.5

splendor_box_width = splendor_card_width + wall_thickness * 4 + 1 + splendor_disc_diameter
splendor_box_length = wall_thickness * 5 + splendor_card_length + splendor_nobel_width
splendor_box_height = splendor_disc_diameter + lid_thickness + default_floor_thickness + 1

# The .scad overrides the label type per the MMU setting.
_LABEL_OPTIONS = MakeLabelOptions(
    font="Impact",
    label_type=LabelType.FRAMED_SOLID if MAKE_MMU else LabelType.FRAMED,
)

# ---- Kit: one slipover box ----------------------------------------------------
KIT = BoxKit(
    SlipoverBox,
    wall_thickness=wall_thickness,
    lid_thickness=lid_thickness,
)

# ---- Contents ----------------------------------------------------------------
_disc_channel_length = splendor_disc_thickness * splendor_disc_number + 0.5


def _contents(inner):
    """The disc channel, card well and noble well, in the interior-local frame.

    Coordinates match the .scad children block exactly. The SlipoverBox
    framework translates these by interior.origin automatically.
    """
    pieces = []

    # --- Disc channel ---
    # Rounded-bottom cuboid: a trough for the disc stack.
    pieces.append(
        InnerObject(
            s3.cuboid(
                [splendor_disc_diameter, _disc_channel_length, splendor_box_height],
                anchor=BOTTOM,
                rounding=splendor_disc_diameter / 2,
                edges=[BOTTOM + LEFT, BOTTOM + RIGHT],
            ).translate([
                splendor_disc_diameter / 2 - 2,
                inner.length / 2,
                0,
            ]),
            ObjectType.NEGATIVE,
        )
    )
    # Flat-top cap: a plain cuboid that overlaps the left portion of the
    # disc channel to give it straight walls above half-diameter height.
    pieces.append(
        InnerObject(
            s3.cuboid(
                [splendor_disc_diameter, _disc_channel_length, splendor_box_height],
                anchor=BOTTOM,
            ).translate([
                0,
                inner.length / 2,
                splendor_disc_diameter / 2,
            ]),
            ObjectType.NEGATIVE,
        )
    )

    # --- Card well ---
    pieces.append(
        InnerObject(
            s3.cuboid(
                [splendor_card_width, splendor_card_length, splendor_box_height],
                anchor=BOTTOM,
            ).translate([
                inner.width - splendor_card_width / 2,
                splendor_card_length / 2,
                0,
            ]),
            ObjectType.NEGATIVE,
        )
    )

    # --- Noble well ---
    pieces.append(
        InnerObject(
            s3.cuboid(
                [splendor_nobel_width, splendor_nobel_width, splendor_box_height],
                anchor=BOTTOM,
            ).translate([
                inner.width - splendor_nobel_width / 2,
                inner.length - splendor_nobel_width / 2,
                0,
            ]),
            ObjectType.NEGATIVE,
        )
    )

    return pieces


# ---- The box ------------------------------------------------------------------
_box = (
    BoxSpec.box_builder()
    .size(splendor_box_width, splendor_box_length, splendor_box_height)
    .label("SplendorBox")
    .wall_thickness(wall_thickness)
    .lid_thickness(lid_thickness)
    .contents(_contents)
    .lid_layout_width(12)
    .lid_shape_type(ShapeType.CIRCLE)
    .lid_shape_width(18)
    .lid_shape_thickness(0.75)
    .lid_label("Splendor", options=_LABEL_OPTIONS)
    .slipover()
    .build()
)


@make_box
def SplendorBox():
    return _box.make_box()


@make_box
def SplendorBoxLid():
    return _box.make_lid()


if FROM_MAKE != 1:
    SplendorBox()
