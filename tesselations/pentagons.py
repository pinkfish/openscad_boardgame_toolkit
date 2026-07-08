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

# LibFile: pentagons.py
#    Sheep tesselation (built from the R2 pentagon tiling).

from __future__ import annotations
import math
import types
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2 import beziers


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. PentagonTesselation is
# imported lazily below since pentagon_tilings is a large sibling module
# converted separately.
_bosl2 = osuse("BOSL2/std.scad")


def SheepTesselation(size: float, x: float, y: float, thickness: float) -> types.SimpleNamespace:
    """Computes the sheep tile data (an R2 pentagon tiling with custom profile lines).

    Usage::

        SheepTesselation(size=20, x=0, y=0, thickness=2)

    Args:
        size: length of the sheep
        x:    x location
        y:    y location
        thickness: thickness of the sheep
    Returns:
        a tile-data object with .points, .x_offset, .y_offset (see PentagonTesselationData)
    """
    from pentagon_tilings import PentagonTesselationData

    line3 = beziers.bezier_curve(
        beziers.flatten(
            [
                beziers.bez_begin([0, 0], -60, 0.4),
                beziers.bez_tang([0.4, -0.04], 0, 0.2, 0.5),
                beziers.bez_tang([0.8, -0.2], 0, 0.5, 0.2),
                beziers.bez_end([1, 0], 210, 0.2),
            ]
        ),
        20,
    )
    line2 = beziers.bezier_curve(
        beziers.flatten(
            [
                beziers.bez_begin([0, 0], 0, 0.4),
                beziers.bez_tang([0.4, 0.0], 0, 0.1, 0.5),
                beziers.bez_tang([0.6, -0.04], 270, 0.1, 0.5),
                beziers.bez_tang([0.8, -0.3], 0, 0.5, 0.2),
                beziers.bez_tang([0.9, -0.3], 20, 0.5, 0.2),
                beziers.bez_end([1, 0], 300, 0.3),
            ]
        ),
        20,
    )
    line1 = [[0, 0], [1, 0]]
    line3_rev = list(reversed([[abs(i[0] - 1), i[1]] for i in line3]))

    return PentagonTesselationData(
        "R2",
        size,
        x,
        y,
        thickness,
        first_angle_modifier=-50,
        second_angle_modifier=0,
        first_length_modifier=0.5,
        second_length_modifier=0,
        third_length_modifier=0,
        line1=line1,
        line2=line2,
        line3=line3_rev,
    )


def SheepTesselationArea(size: float, width: float, length: float, thickness: float) -> PyOpenSCAD:
    """Tiles the sheep pattern across an area.

    Usage::

        SheepTesselationArea(size=20, width=200, length=100, thickness=1)

    Args:
        size:   length of the sheep
        width:  width of the space
        length: length of the space
        thickness: thickness of the sheep
    """
    data = SheepTesselation(size, 0, 0, thickness)

    rows = math.floor(width / (max(abs(data.x_offset[0]), abs(data.y_offset[0])) * size)) + 2
    cols = math.floor(length / (max(abs(data.x_offset[1]), abs(data.y_offset[1])) * size)) * 8 // 4 + 1
    x_offset = [data.x_offset[0], -data.x_offset[1]]
    y_offset = [data.y_offset[0], -data.y_offset[1]]

    shape = None
    for x in range(rows + 1):
        for y in range(cols + 1):
            piece = (
                region(data.points)
                .translate([size * x * x_offset[0], size * x * x_offset[1], 0])
                .translate([size * y * y_offset[0], size * y * y_offset[1], 0])
            )
            shape = piece if shape is None else shape | piece
    return shape.translate([-cols * size, -size * 3 / 4, 0])
