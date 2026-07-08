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

# LibFile: kite_tesselation.py
#    Kite-based tesselation helpers.

from __future__ import annotations
import math
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2 import paths
from bosl2 import transforms


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse("BOSL2/std.scad")


def MakeTesselationKite(size: float, side1: list[list[float]], side2: list[list[float]]) -> list[list[float]]:
    """Builds a kite-shaped path from two profile lines.

    Args:
        size:  length of the kite
        side1: profile line for one side, points span x in [-0.5, 0.5]
        side2: profile line for the other side, points span x in [-0.5, 0.5]
    Returns:
        a closed 2-D path (list of points)
    """
    b1 = (size * math.tan(math.radians(30))) / (math.tan(math.radians(60)) + math.tan(math.radians(30)))
    a = b1 * math.tan(math.radians(60))
    small_c = math.sqrt(a * a + b1 * b1)
    long_c = math.sqrt(a * a + (size - b1) * (size - b1))
    line_small = [[p[0] * small_c, p[1] * small_c] for p in side1]
    line_long = [[p[0] * long_c, p[1] * long_c] for p in side2]

    part1 = transforms.move([b1 / 2, -a / 2], transforms.rot(p=line_small, a=60))
    part2 = list(reversed(transforms.move([b1 / 2, a / 2], transforms.rot(p=line_small, a=-60))))
    part3 = list(reversed(transforms.move([-(size - b1) / 2, a / 2], transforms.rot(p=line_long, a=30))))
    part4 = transforms.move([-(size - b1) / 2, -a / 2], transforms.rot(p=line_long, a=-30))

    merged = paths.path_merge_collinear(path=part1 + part2 + part3 + part4, closed=True)
    return transforms.move([size / 2 - b1, 0], merged)


def MakeTesselationKiteHexagon(
    size: float, side1: list[list[float]], side2: list[list[float]], thickness: float, outer_offset: float
) -> PyOpenSCAD:
    """Tiles 6 kites rotated around a point into a hexagon outline shape.

    Args:
        size:  length of the kite
        side1: profile line for one side
        side2: profile line for the other side
        thickness: outline stroke thickness
        outer_offset: extra outward offset
    """
    kites = MakeTesselationKite(size, side1, side2)

    shape = None
    for i in range(6):
        region_data = DifferenceWithOffset(
            outer_offset=outer_offset,
            offset=-thickness,
            pts=transforms.rot(p=transforms.right(size / 2, kites), a=i * 60),
        )
        piece = region(region_data)
        shape = piece if shape is None else shape | piece
    return shape


def TesselationHexKiteAtLocation(size: float, x: int, y: int, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Places *children* at a specific hex-grid location for the kite-hex tiling.

    Args:
        size: size of the hex
        x:    x grid location
        y:    y grid location
        children: solid to place
    """
    radius = size
    apothem = math.sqrt(radius * radius - (radius / 2) * (radius / 2))
    dx = apothem * 2 * y + (x % 2) * apothem
    dy = x * radius * 3 / 2
    return children.translate([dx, dy, 0])


def TesselationHexKiteArea(width: float, length: float, size: float, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Tiles *children* across an area using the kite-hex grid.

    Args:
        width:  width of the space
        length: length of the space
        size:   size of the hex
        children: solid to repeat
    """
    apothem = math.sqrt(size * size - (size / 2) * (size / 2))
    rows = math.floor(width / (size * 4) + 3)
    cols = math.floor(length / (apothem * 2) + 3)

    shape = None
    for x in range(rows + 1):
        for y in range(cols + 1):
            piece = TesselationHexKiteAtLocation(size=size, x=x, y=y, children=children)
            shape = piece if shape is None else shape | piece
    return shape.translate([-size / 2, 0, 0])
