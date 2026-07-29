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
#    PythonSCAD port of splendor_wide.scad. Notes on the .scad -> .py port pattern:
#      * `MakeBoxWithSlipoverLid(...) { child; child; }` becomes children=[fn], where fn is a
#        callable(inner_width, inner_length, inner_height); the .scad `$inner_width`/`$inner_length`
#        special variables become that callable's parameters.
#      * `cuboid(...)` is pybosl2.shapes3d.cuboid; `translate([v]) shape` becomes shape.translate([v]).
#      * the .scad global-default overrides (default_wall_thickness = 4, ...) don't propagate
#        through Python imports, so they are passed explicitly to each box call instead.
#      * `@make_box` marks the sections make_files.py builds (mmu + single 3mf).

from base_bgtk import *
from pybosl2.shapes3d import cuboid
from slipover_box import MakeBoxWithSlipoverLid, SlipoverBoxLidWithLabel

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

size = [splendor_box_width, splendor_box_length, splendor_box_height]


@make_box
def SplendorBox():
    def compartments(inner_width, inner_length, inner_height):
        disc_len = splendor_disc_thickness * splendor_disc_number + 0.5
        return (
            cuboid(
                [splendor_disc_diameter, disc_len, splendor_box_height],
                anchor=BOTTOM, rounding=splendor_disc_diameter / 2, edges=[BOTTOM + LEFT, BOTTOM + RIGHT],
            ).translate([splendor_disc_diameter / 2 - 2, inner_length / 2, 0])
            | cuboid([splendor_disc_diameter, disc_len, splendor_box_height], anchor=BOTTOM)
            .translate([0, inner_length / 2, splendor_disc_diameter / 2])
            | cuboid([splendor_card_width, splendor_card_length, splendor_box_height], anchor=BOTTOM)
            .translate([inner_width - splendor_card_width / 2, splendor_card_length / 2, 0])
            | cuboid([splendor_nobel_width, splendor_nobel_width, splendor_box_height], anchor=BOTTOM)
            .translate([inner_width - splendor_nobel_width / 2, inner_length - splendor_nobel_width / 2, 0])
        )

    return MakeBoxWithSlipoverLid(size=size, foot=3, wall_thickness=wall_thickness, lid_thickness=lid_thickness, children=[compartments])


@make_box
def SplendorBoxLid():
    return SlipoverBoxLidWithLabel(
        size=size, foot=3, wall_thickness=wall_thickness, lid_thickness=lid_thickness, text_str="Splendor"
    )


if FROM_MAKE != 1:
    SplendorBox().show()
