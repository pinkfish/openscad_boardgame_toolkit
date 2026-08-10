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
#    Cascadero organiser.  Every box is built from one shared BoxKit, so the basic
#    parts (wall/lid thickness, label style, box type) are configured in a single
#    place and each box only specifies what is unique to it (size, label, contents).
#
#    Switch the WHOLE organiser between box types by changing the one class name in
#    the BoxKit(...) call below -- e.g. BoxKit(CapBox, ...) once CapBox is available.
#    Nothing else in this file mentions the box type.

from base_bgtk import FROM_MAKE, InnerObject, make_box
from box_base import BoxKit, BoxSpec, Label, Lid
from sliding_box import SlidingBox
from components import RoundedBoxAllSides, RoundedBoxGrid
from labels import MakeLabelOptions

# ---------------------------------------------------------------------------
# Game measurements
# ---------------------------------------------------------------------------

box_width = 212
box_height = 40
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

# ---------------------------------------------------------------------------
# Shared label styles
# ---------------------------------------------------------------------------

BLUE = MakeLabelOptions(label_colour="blue")
BLUE_R5 = MakeLabelOptions(label_colour="blue", radius=5)

# ---------------------------------------------------------------------------
# One kit configures the basic parts shared by every box in this organiser --
# the box TYPE and the common thicknesses/label style.  Change SlidingBox here
# to rebuild the entire organiser as a different box type; nothing below needs
# to be touched.
# ---------------------------------------------------------------------------

KIT = BoxKit(
    SlidingBox,
    wall_thickness=2,
    lid_thickness=3,
    # The lid style every box shares. Each box passes its own text as lid="...", which
    # BoxKit merges into this one (Lid.with_label) rather than replacing it -- so the
    # blue label styling is written once, here.
    lid=(
        Lid.builder()
        .label("", options=BLUE)
        .build()
    ),
)


# A tiny helper for the single-compartment rounded sections (Seals/Farmer/Herald):
# custom interior geometry is supplied through contents= as InnerObject components.
def _section(size, label, options=None):
    return KIT.box(
        size=size,
        label=label,
        contents=lambda inner: [
            InnerObject(RoundedBoxAllSides([inner.width, inner.length, section_height], radius=15))
        ],
        # Just the text (kit styling), or a whole Lid when this box wants its own style.
        lid=label if options is None else Lid.builder().label(label, options=options).build(),
    )


# ---------------------------------------------------------------------------
# Seals / Farmer / Herald -- single rounded compartment each
# ---------------------------------------------------------------------------

_seals = _section([top_width, top_length, section_height], "Seals", BLUE_R5)
_farmer = _section([top_width, top_length, section_height], "Farmer")
_herald = _section([herald_width, top_length, section_height], "Herald")


@make_box
def SealsBox():
    return _seals.make_box()


@make_box
def SealsBoxLid():
    return _seals.make_lid()


@make_box
def FarmerBox():
    return _farmer.make_box()


@make_box
def FarmerBoxLid():
    return _farmer.make_lid()


@make_box
def HeraldBox():
    return _herald.make_box()


@make_box
def HeraldBoxLid():
    return _herald.make_lid()


# ---------------------------------------------------------------------------
# Player box -- two-section interior (grid + open area), still one kit box
# ---------------------------------------------------------------------------

_player = (
    BoxSpec.box_builder()
    .size(player_width, player_length, section_height)
    .label("Player")
    .wall_thickness(2)
    .lid_thickness(3)
    .contents(lambda inner: [
        InnerObject(
            RoundedBoxGrid([inner.width, first_width, section_height],
                           radius=radius, rows=2, cols=1, all_sides=True)
        ),
        InnerObject(
            RoundedBoxAllSides(
                [inner.width, inner.length - first_width, section_height], radius=radius
            ).translate([0, first_width + 2, 0])   # 2 = wall_thickness
        ),
    ])
    .lid_label("Player", options=BLUE_R5)
    .sliding()
    .build()
)


@make_box
def PlayerBox():
    return _player.make_box()


@make_box
def PlayerBoxLid():
    return _player.make_lid()


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

if FROM_MAKE != 1:
    SealsBox().show()
