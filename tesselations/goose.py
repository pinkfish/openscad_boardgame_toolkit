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

# LibFile: goose.py
#    Goose tesselation.

from __future__ import annotations
import math
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import shapes2d
from pybosl2 import Path2D


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. TesselationFromQuadradicPoints
# is imported lazily below since tesselations is a large sibling module
# converted separately.

TESSELATION_GOOSE_SIDE = 30
TESSELATION_GOOSE_MIDDLE = 3


def TesselationGoose(flip: bool = False, size: float = 100, thickness: float = 0, outer_offset: float = 0) -> PyOpenSCAD:
    """The nice goose shape.

    Usage::

        TesselationGoose(size=20)
        TesselationGoose(size=20, thickness=0.5)

    Args:
        flip:      flip the tail end (default False)
        size:      size of the hex (default 100)
        thickness: thickness of the sides (default 0)
        outer_offset: extra outward offset (default 0)
    """
    from quad_tesselation import TesselationFromQuadradicPoints

    line_a = [[0, 0], [0.4, -0.25], [0.5, 0], [0.6, 0.25], [1, 0]]
    line_b = [[0, 0], [1, 0]]
    line2 = line_b if flip else line_a
    line3 = [[i[0], -i[1]] for i in line_a] if flip else line_b
    ratio = size / 100

    path = TesselationFromQuadradicPoints(
        [
            [0, 0],
            [100 * ratio, TESSELATION_GOOSE_SIDE * ratio],
            [
                (100 - TESSELATION_GOOSE_MIDDLE) * ratio,
                (TESSELATION_GOOSE_MIDDLE if flip else -TESSELATION_GOOSE_MIDDLE) * ratio,
            ],
            [100 * ratio, -TESSELATION_GOOSE_SIDE * ratio],
        ],
        [
            [0, 0],
            [0.213176, -0.056018],
            [0.406283, -0.07],
            [0.56471, 0.0733724],
            [0.693585, 0.0370756],
            [0.761958, -0.0107027],
            [1, 0],
        ],
        line2,
        line3,
        [
            [0, 0],
            [0.213176, 0.056018],
            [0.406283, 0.07],
            [0.56471, -0.0733724],
            [0.693585, -0.0370756],
            [0.761958, 0.0107027],
            [1, 0],
        ],
    )
    merged = Path2D(path, closed=True).merge_collinear()
    # polygon() is the NATIVE builtin: it rejects a pybosl2 Path2D / numpy points ("Error
    # during parsing polygon(points,paths)"), so hand it plain float pairs.
    pts = [[float(x), float(y)] for x, y in (merged.to_list if hasattr(merged, "to_list") else merged)]
    return DifferenceWithOffset(offset=-thickness, outer_offset=outer_offset, children=shapes2d.polygon(pts))


def TesselationGooseBlock(size: float, thickness: float, outer_offset: float = 0) -> PyOpenSCAD:
    """The nice goose shape, as a 4-bird tileable block.

    Usage::

        TesselationGooseBlock(size=30, thickness=1)
        TesselationGooseBlock(size=20, thickness=0.5)

    Args:
        size:      the size of the goose
        thickness: the thickness of the goose
        outer_offset: extra outward offset (default 0)
    """
    assert size > 0, "need a size"
    assert thickness >= 0, "need a thickness"
    ratio = size / 100

    a = (
        TesselationGoose(size=size, flip=False, thickness=thickness, outer_offset=outer_offset)
        .mirror([1, 0, 0])
        .translate([0, -TESSELATION_GOOSE_SIDE * ratio, 0])
        .color("red")
    )
    b = (
        TesselationGoose(size=size, flip=False, thickness=thickness, outer_offset=outer_offset)
        .mirror([1, 0, 0])
        .translate([0, TESSELATION_GOOSE_SIDE * ratio, 0])
        .color("cyan")
    )
    c = (
        TesselationGoose(size=size, flip=True, thickness=thickness, outer_offset=outer_offset)
        .color("purple")
        .translate([-100 * ratio, 0, 0])
    )
    d = (
        TesselationGoose(size=size, flip=True, thickness=thickness, outer_offset=outer_offset)
        .color("magenta")
        .translate([-100 * ratio, TESSELATION_GOOSE_SIDE * ratio * 2, 0])
    )
    return a | b | c | d


def TesselationGooseGrid(row: int, col: int, size: float, thickness: float, outer_offset: float = 0.1) -> PyOpenSCAD:
    """The nice goose shape, tiled in a grid.

    Usage::

        TesselationGooseGrid(5, 5, size=30, thickness=1)

    Args:
        row:   number of rows
        col:   number of columns
        size:  size of the goose
        thickness: thickness of the goose
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
            y = TESSELATION_GOOSE_MIDDLE / 4 * i + (i + (TESSELATION_GOOSE_SIDE * 4) * j) * ratio
            x = (100 - TESSELATION_GOOSE_MIDDLE) * i * ratio
            piece = TesselationGooseBlock(size=size, thickness=thickness, outer_offset=outer_offset).translate(
                [x, y, 0]
            )
            pieces.append(piece)
    # Balanced union -- a left fold costs nothing to assemble (PythonSCAD is lazy)
    # and then makes Manifold re-boolean the whole accumulated tiling once per cell
    # at mesh time.
    shape = union_all_2d(pieces)
    assert shape is not None
    return shape


def TesselationGooseArea(width: float, length: float, size: float, thickness: float) -> PyOpenSCAD:
    """The nice goose shape, tiled across an area.

    Usage::

        TesselationGooseArea(200, 100, size=50, thickness=2)

    Args:
        width:  width of the space
        length: length of the space
        size:   size of the goose
        thickness: thickness of the goose
    """
    assert width > 0, "Need a width"
    assert length > 0, "Need a length"
    assert size > 0, "Need a size"
    assert thickness > 0, "Need a thickness"

    ratio = size / 100
    calc_size = size - TESSELATION_GOOSE_MIDDLE
    rows = math.floor(width / (calc_size * ratio) / 3 + 1)
    cols = math.floor(length / (TESSELATION_GOOSE_SIDE * 4 * ratio) + 1)

    grid = TesselationGooseGrid(row=rows, col=cols, size=size, thickness=thickness, outer_offset=0.1)
    return grid.translate([0, -TESSELATION_GOOSE_MIDDLE * ratio * rows, 0])
