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

# LibFile: quad_tesselation.py
#    Quadrilateral-based tesselation helpers and the bird tesselation.

from __future__ import annotations
import math
import numpy as np
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import Path2D
from pybosl2 import Bezier


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. tesselation_side_line and
# TESSELATION_LINE_NORMAL are imported lazily below since tesselations is a
# large sibling module converted separately.


def QuadrilateralCoords(angles: list[float], side: float, side_ratio: float = 1) -> list[list[float]]:
    """Computes the four 2-D vertices [P0, P1, P2, P3] of a quadrilateral.

    The quadrilateral is placed with P0 at the origin and side P0->P1 along
    the positive x-axis. Because a quadrilateral with four known angles
    still has one free degree of freedom (unlike a triangle), *side_ratio*
    sets the ratio of the second side (P1->P2) to the first side. All four
    interior angles must sum to 360 degrees.

    Usage::

        QuadrilateralCoords(angles=[90, 90, 90, 90], side=20)
        QuadrilateralCoords(angles=[70, 110, 70, 110], side=20)
        QuadrilateralCoords(angles=[60, 120, 60, 120], side=20, side_ratio=1.5)

    Args:
        angles:     four interior angles [a0, a1, a2, a3] in degrees, summing to 360
        side:       length of side P0->P1
        side_ratio: ratio of side P1->P2 to side P0->P1 (default 1)
    """
    assert len(angles) == 4, "angles must be a list of exactly four values"
    assert abs(sum(angles) - 360) < 1e-6, f"Interior angles must sum to 360 degrees, got {sum(angles)}"
    assert side > 0, "side must be positive"
    assert side_ratio > 0, "side_ratio must be positive"

    P0 = [0.0, 0.0]
    P1 = [float(side), 0.0]

    dir1 = 180 - angles[1]
    dir2 = dir1 + (180 - angles[2])
    dir3 = dir2 + (180 - angles[3])

    d1 = [math.cos(math.radians(dir1)), math.sin(math.radians(dir1))]
    d2 = [math.cos(math.radians(dir2)), math.sin(math.radians(dir2))]
    d3 = [math.cos(math.radians(dir3)), math.sin(math.radians(dir3))]

    t2 = side_ratio * side
    P2 = [P1[0] + t2 * d1[0], P1[1] + t2 * d1[1]]

    det = d2[0] * d3[1] - d3[0] * d2[1]
    assert det != 0, "Degenerate quadrilateral: parallel opposite edges"
    rhs_x = -P2[0]
    rhs_y = -P2[1]
    t3 = (rhs_x * d3[1] - d3[0] * rhs_y) / det
    t4 = (d2[0] * rhs_y - rhs_x * d2[1]) / det
    P3 = [P2[0] + t3 * d2[0], P2[1] + t3 * d2[1]]

    assert t3 > 0, f"Invalid quadrilateral geometry: side P2->P3 length is non-positive ({t3}). Try a different side_ratio."
    assert t4 > 0, f"Invalid quadrilateral geometry: side P3->P0 length is non-positive ({t4}). Try a different side_ratio."

    return [P0, P1, P2, P3]


def TesselationFromQuadradicPoints(
    points,
    side1,
    side2,
    side3,
    side4,
) -> list[list[float]]:
    """Builds a tesselation path from four quad corner points and four profile lines.

    Args:
        points: the quad points [P0, P1, P2, P3]
        side1/side2/side3/side4: profile line for each side, points span x in [-0.5, 0.5]
    """
    from tesselations import tesselation_side_line, TESSELATION_LINE_NORMAL

    # tesselation_side_line() hands back a pybosl2 Path2D, which has no `+` -- join the POINT
    # LISTS instead. NB `to_list` is a property, not a method.
    def side(a, b, profile):
        return tesselation_side_line([points[a], points[b]], profile, TESSELATION_LINE_NORMAL).to_list

    path = (
        side(0, 1, side1)
        + side(1, 2, side2)
        + side(2, 3, side3)
        + side(len(points) - 1, 0, side4)
    )
    return Path2D(path, closed=True).merge_collinear()


def TesselationBird(size: float, thickness: float = 2, outer_offset: float = 0.1, flip: bool = False) -> "Bosl2Shape2D":
    """A simple bird tesselation.

    Usage::

        TesselationBird(size=20)
        TesselationBird(size=20, flip=True)
        TesselationBird(size=20, thickness=1)
        TesselationBird(size=20, thickness=1, outer_offset=0.1)

    Args:
        size:      the size of the bird
        thickness: the thickness of the bird (default 2)
        outer_offset: extra outward offset (default 0.1)
        flip:      mirror the bird (default False)
    """
    bezpath = [[0, 0], [0.4, 0], [0.5, 0.55]]
    other_bez = [[0.5, 0.55], [0.85, 0.42], [0.6, 0.0], [0.65, -0.05], [0.75, 0.05], [0.9, -0.1], [1, 0]]

    bez = np.concatenate([Bezier(bezpath).curve(20), Bezier(other_bez).curve(20)])
    flip_bez = list(reversed([[1 - i[0], i[1]] for i in bez]))

    chosen_bez = flip_bez if flip else bez
    quad_points = [[p[0] * size / 10, p[1] * size / 10] for p in [[5, 5], [5, -5], [-5, -4], [-5, 4]]]
    side1 = [[0, 0], [0.4, 0.1], [0.6, -0.1], [1, 0]] if flip else [[0, 0], [0.4, -0.1], [0.6, 0.1], [1, 0]]
    side4 = [[i[0], -i[1]] for i in chosen_bez]

    path = TesselationFromQuadradicPoints(quad_points, side1, chosen_bez, [[0, 0], [1, 0]], side4)

    return DifferenceWithOffset(offset=-thickness, outer_offset=outer_offset, children=region(path))


def TesselationBirdBlock(size: float, thickness: float, outer_offset: float = 0) -> PyOpenSCAD:
    """The nice bird shape, as a 4-bird tileable block.

    Usage::

        TesselationBirdBlock(size=30, thickness=1)
        TesselationBirdBlock(size=20, thickness=0.5)

    Args:
        size:      the size of the bird
        thickness: the thickness of the bird
        outer_offset: extra outward offset (default 0)
    """
    assert size > 0, "need a size"
    assert thickness >= 0, "need a thickness"
    ratio = size / 100

    a = TesselationBird(size=size, flip=False, thickness=thickness, outer_offset=outer_offset).color("red")
    b = (
        TesselationBird(size=size, flip=False, thickness=thickness, outer_offset=outer_offset)
        .mirror([1, 0, 0])
        .translate([0, size - 10 * ratio, 0])
        .color("cyan")
    )
    c = (
        TesselationBird(size=size, flip=True, thickness=thickness, outer_offset=outer_offset)
        .color("purple")
        .mirror([1, 0, 0])
        .translate([-size, 0, 0])
    )
    d = (
        TesselationBird(size=size, flip=True, thickness=thickness, outer_offset=outer_offset)
        .color("magenta")
        .translate([-size, size - 10 * ratio, 0])
    )
    return a | b | c | d


def TesselationBirdGrid(row: int, col: int, size: float, thickness: float, outer_offset: float = 0.1) -> PyOpenSCAD:
    """The nice bird shape, tiled in a grid.

    Usage::

        TesselationBirdGrid(5, 5, size=30, thickness=1)

    Args:
        row:   number of rows
        col:   number of columns
        size:  size of the bird
        thickness: thickness of the bird
        outer_offset: extra outward offset (default 0.1)
    """
    assert row > 0, "Need a row"
    assert col > 0, "Need a col"
    assert size > 0, "Need a size"
    assert thickness > 0, "Need a thickness"

    ratio = size / 100
    pieces = []
    for i in range(row + 1):
        for j in range(col + 1):
            y = i * (size * 2 - 20 * ratio)
            x = size * j * 2
            piece = TesselationBirdBlock(size=size, thickness=thickness, outer_offset=outer_offset).translate(
                [x, y, 0]
            )
            pieces.append(piece)
    # Balanced union -- a left fold costs nothing to assemble (PythonSCAD is lazy)
    # and then makes Manifold re-boolean the whole accumulated tiling once per cell
    # at mesh time.
    shape = union_all_2d(pieces)
    assert shape is not None
    return shape


def TesselationBirdArea(width: float, length: float, size: float, thickness: float) -> PyOpenSCAD:
    """The nice bird shape, tiled across an area.

    Usage::

        TesselationBirdArea(200, 100, size=50, thickness=2)

    Args:
        width:  width of the space
        length: length of the space
        size:   size of the bird
        thickness: thickness of the bird
    """
    assert width > 0, "Need a width"
    assert length > 0, "Need a length"
    assert size > 0, "Need a size"
    assert thickness > 0, "Need a thickness"
    rows = math.floor(width / (size * 1.5) + 1)
    cols = math.floor(length / (size * 1.5) + 1)

    grid = TesselationBirdGrid(row=rows, col=cols, size=size, thickness=thickness, outer_offset=0.1)
    return grid.translate([0, size / 2, 0])
