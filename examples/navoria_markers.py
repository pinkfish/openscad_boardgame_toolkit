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

# LibFile: examples/navoria_markers.py
#    Explorers of Navoria marker silhouettes ported from the .scad original
#    (examples/lib/explorers_of_navoria_shared.scad's BirdTurnOrder / FavourMarker /
#    king marker) to pybosl2 Python, so they can be used as custom compartment wells:
#
#        Compartment(shape="custom", w=25, l=26, solid=BirdMarker)
#
#    Each function takes the well depth and returns the marker cavity solid built
#    around its own origin (the compartment layout centres it in the cell).

from base_bgtk import BACK, BOTTOM, FRONT, LEFT, RIGHT
import pybosl2.shapes3d as s3

# ---- Navoria marker measurements (from the shared .scad) --------------------------
bird_diameter = 20.5
bird_length = 25
bird_base = 7
bird_top_base = 11
bird_lump = 3.75
bird_beak_diameter = 21.5
bird_diameter_base = 6
bird_lump_length = 23
bird_lump_second_length = 21.75

king_marker = 20.5

# Trading post (the "castle" silhouette, TradingPostGreen in the .scad).
tp_width = 17
tp_height = 16
tp_base_width = 12
tp_top_height = 7
tp_gap = 2
tp_inset_up = 2
tp_crenelation_height = 4


def BirdMarker(height: float):
    """The turn-order bird silhouette (BirdTurnOrder in the .scad), extruded to
    *height*. Body cylinder + prismoid tail base + hulled beak + two hulled top lumps,
    matching the original construction."""
    extra = bird_length - bird_diameter
    top_offset = bird_lump_length - bird_diameter

    # Main body.
    body = s3.cyl(height=height, diameter=bird_diameter, anchor=BOTTOM)

    # Tail base: a prismoid laid on its side (rotate([0,-90,0])).
    base = (
        s3.prismoid(size1=[height, bird_top_base], size2=[height, bird_base], height=bird_diameter_base)
        .rotate([0, -90, 0])
        .translate([-bird_diameter / 2 + bird_diameter_base - extra, 0, height / 2])
    )

    # Beak: hull of a small cylinder and a thin cuboid out the front.
    beak = (
        s3.cyl(height=height, radius=1, fn=16, anchor=BOTTOM)
        .translate([0, bird_diameter / 2 + bird_beak_diameter - bird_diameter - 0.5, 0])
    ).hull(
        s3.cuboid([4, 0.5, height], anchor=BOTTOM).translate([0, bird_diameter / 2 - 0.45, 0])
    )

    # Top wing lumps (built rotated -40 degrees), each a hull of a cylinder + cuboid.
    lump1 = (
        s3.cyl(diameter=bird_lump, height=height, fn=32, anchor=BOTTOM)
        .translate([bird_diameter / 2 + top_offset - bird_lump / 2, 0, 0])
    ).hull(
        s3.cuboid([bird_lump / 2, bird_lump, height], anchor=BOTTOM).translate([bird_diameter / 2, 0, 0])
    )
    lump2 = (
        s3.cyl(diameter=(bird_lump_second_length - bird_diameter) * 2, height=height, fn=16, anchor=BOTTOM)
        .rotate([0, 0, -14]).translate([bird_diameter / 2, 0, 0])
    ).hull(
        s3.cuboid([bird_lump / 2, bird_lump, height], anchor=BOTTOM)
        .rotate([0, 0, -24]).translate([bird_diameter / 2 - 3, 0, 0])
    )
    top = (lump1 | lump2).rotate([0, 0, -40])

    return (body | base | beak | top).translate([(bird_length - bird_diameter) / 2, 0, 0])


def KingMarker(height: float):
    """The king marker: a simple rounded square token, extruded to *height*."""
    return s3.cuboid([king_marker, king_marker, height], anchor=BOTTOM, rounding=2,
                     edges=[FRONT + LEFT, FRONT + RIGHT, BACK + LEFT, BACK + RIGHT])


def TradingPostMarker(height: float):
    """The trading-post castle silhouette (TradingPostGreen in the .scad), extruded to
    *height*: a base, a trapezoid body (hull of four corner pins), and a crenellated
    top (a rounded block with two notches cut out)."""
    h = height

    base = s3.cuboid([tp_base_width, tp_inset_up + 0.5, h], anchor=BOTTOM + FRONT)

    # Crenellated top: a rounded block minus two notch gaps.
    top = s3.cuboid([tp_width, tp_top_height, h], anchor=BOTTOM + BACK, rounding=0.5,
                    edges=[BACK + LEFT, BACK + RIGHT]).translate([0, tp_height, 0])
    gx = (tp_width - tp_gap * 2) / 3.5
    for sx in (-gx, gx):
        notch = s3.cuboid([tp_gap, tp_crenelation_height + 1, h + 1], anchor=BOTTOM + BACK,
                          rounding=0.5, edges=[FRONT + LEFT, FRONT + RIGHT]).translate([sx, tp_height + 1, -0.5])
        top = top - notch

    # Trapezoid body: convex hull of four corner pins (top corners -> base corners).
    def pin(px, py):
        return s3.cyl(diameter=1, height=h, fn=16, anchor=BOTTOM).translate([px, py, 0])

    body = (
        pin(tp_width / 2 - 0.5, tp_height - tp_top_height)
        .hull(pin(-tp_width / 2 + 0.5, tp_height - tp_top_height))
        .hull(pin(tp_base_width / 2 - 0.5, tp_inset_up))
        .hull(pin(-tp_base_width / 2 + 0.5, tp_inset_up))
    )

    return (base | top | body).translate([0, -tp_height / 2, 0])
