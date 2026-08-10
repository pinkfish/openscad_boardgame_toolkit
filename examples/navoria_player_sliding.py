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

# LibFile: examples/navoria_player_sliding.py
#    The Explorers of Navoria player box (see examples/explorers_of_navoria.scad's
#    PlayerBoxOneBase) rebuilt on the NEW framework: a BoxKit-configured SlidingBox
#    whose interior is laid out AUTOMATICALLY by compartments.layout_compartments --
#    marker wells in rows, each row sharing one contiguous scoop, no hand-placed
#    coordinates.
#
#    NOTE: the marker footprints use the real Navoria dimensions but simple
#    rect/circle wells; the custom marker silhouettes (TradingPost / Bird / King art)
#    from the .scad original are approximated by their bounding footprint here -- the
#    point is that the layout + removal framework expresses the whole box.

from base_bgtk import FROM_MAKE, make_box
from box_base import BoxKit
from sliding_box import SlidingBox
from compartments import Compartment, Group, Shape, layout_compartments
from navoria_markers import BirdMarker, KingMarker, TradingPostMarker

# ---- Navoria measurements (from examples/lib/explorers_of_navoria_shared.scad) ----
player_box_width = 62      # 211 - player_layout_width(147) - 2
player_box_length = 133    # (268 - 2) / 2
player_box_height = 13.75  # (68 - 12 - 1) / 4
marker_thickness = 10

king_marker = 20.5
bird_diameter = 20.5
trading_post_width = 17
trading_post_height = 16

SCOOP = 5  # explicit scoop depth (the .scad used cyl(r=10, rounding=9) dips)

# ---- One kit configures the box type + shared basics for the whole player box ----
KIT = BoxKit(
    SlidingBox,
    wall_thickness=3,
    lid_thickness=2,
    floor_thickness=1.5,   # so a 10mm marker fits: 13.75 - 2(lid) - 1.5(floor) = 10.25 interior
    material_colour="green",
)

# ---- The interior, laid out automatically ----------------------------------------
# Each row of markers shares ONE contiguous scoop (a row of separate scoops would
# leave ridges); scoop depth is set explicitly.
_contents = layout_compartments(
    [
        # King + Bird use the REAL ported marker silhouettes (navoria_markers.py) as
        # custom well shapes; the trading posts still use their rect footprint.
        Group([Compartment(shape=Shape.CUSTOM, w=king_marker + 1, l=king_marker + 1,
                           depth=marker_thickness, solid=KingMarker, scoop_depth=SCOOP)]),
        Group([Compartment(shape=Shape.CUSTOM, w=27, l=26, depth=marker_thickness,
                           solid=BirdMarker, scoop_depth=SCOOP)]),
        # four rows of two trading-post CASTLE silhouettes each -> merged scoop per row.
        *[
            Group([Compartment(shape=Shape.CUSTOM, w=18, l=17, solid=TradingPostMarker,
                               depth=marker_thickness, count=2, scoop_depth=SCOOP)])
            for _ in range(4)
        ],
    ],
    # Tight packing (the real marker footprints fill the length; at min_gap=2 the
    # ported bird silhouette overflows by ~2.5mm and layout_compartments raises).
    min_gap=1,
)

_player = KIT.box(
    size=[player_box_width, player_box_length, player_box_height],
    label="PlayerBox",
    lid="Player",
    contents=_contents,
)


@make_box
def PlayerBox():
    return _player.make_box()


@make_box
def PlayerBoxLid():
    return _player.make_lid()


if FROM_MAKE != 1:
    PlayerBox().show()
