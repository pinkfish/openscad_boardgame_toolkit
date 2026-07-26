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
#    Cascadero organiser.  Box/lid pairs are defined with a single BoxSpec so
#    dimensions and thicknesses are guaranteed to match.  Swap SlidingBox for
#    CapBox (once available) by changing one name.

from base_bgtk import *
from box_base import BoxSpec, FingerHole
from sliding_box import SlidingBox, MakeSlidingLidOptions
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
# Helper: build a BoxSpec for a rounded-compartment section box
# ---------------------------------------------------------------------------


def _section_spec(size, label, label_opts):
    """Return a BoxSpec for a single-compartment rounded section.

    Both make_box() and make_lid() are driven from this one spec, so the
    box and lid are always guaranteed to match.
    """
    return BoxSpec(
        size=size,
        label=label,
        wall_thickness=2,
        lid_thickness=3,
        contents=lambda inner: [
            InnerObject(RoundedBoxAllSides([inner.width, inner.length, section_height], radius=15))
        ],
        lid_label=label,
        label_options=label_opts,
    )


# ---------------------------------------------------------------------------
# Seals box
# ---------------------------------------------------------------------------

_seals = SlidingBox(_section_spec([top_width, top_length, section_height], "Seals", BLUE_R5))


@make_box
def SealsBox():
    return _seals.make_box()


@make_box
def SealsBoxLid():
    return _seals.make_lid()


# ---------------------------------------------------------------------------
# Farmer box
# ---------------------------------------------------------------------------

_farmer = SlidingBox(_section_spec([top_width, top_length, section_height], "Farmer", BLUE))


@make_box
def FarmerBox():
    return _farmer.make_box()


@make_box
def FarmerBoxLid():
    return _farmer.make_lid()


# ---------------------------------------------------------------------------
# Herald box
# ---------------------------------------------------------------------------

_herald = SlidingBox(_section_spec([herald_width, top_length, section_height], "Herald", BLUE))


@make_box
def HeraldBox():
    return _herald.make_box()


@make_box
def HeraldBoxLid():
    return _herald.make_lid()


# ---------------------------------------------------------------------------
# Player box  (two-section interior: grid + open area)
# ---------------------------------------------------------------------------

_player_spec = BoxSpec(
    size=[player_width, player_length, section_height],
    label="Player",
    wall_thickness=2,
    lid_thickness=3,
    contents=lambda inner: [
        InnerObject(
            RoundedBoxGrid([inner.width, first_width, section_height],
                           radius=radius, rows=2, cols=1, all_sides=True)
        ),
        InnerObject(
            RoundedBoxAllSides(
                [inner.width, inner.length - first_width, section_height], radius=radius
            ).translate([0, first_width + 2, 0])   # 2 = wall_thickness
        ),
    ],
    lid_label="Player",
    label_options=BLUE_R5,
)

_player = SlidingBox(_player_spec)


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
