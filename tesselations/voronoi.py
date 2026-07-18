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

# LibFile: voronoi.py
#    Voronoi tesselation.

from __future__ import annotations
import math
import random
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *


def VoronoiPoints(
    width: float, length: float, cellsize: float, allowable: float, seed: float | None = None
) -> list[list[float]]:
    """Generates a set of jittered grid points to make a Voronoi pattern.

    Args:
        width:     width of the space to fill
        length:    length of the space to fill
        cellsize:  size of the grid cells
        allowable: how much to randomize within the cell
        seed:      seed for the random number generator (default random)
    """
    if seed is None:
        seed_calc = round(_rands(0, 100000, 1)[0])
    else:
        seed_calc = seed + width * length / allowable + cellsize

    half_cell = cellsize / 2
    x_cells = math.floor(width / cellsize)
    y_cells = math.floor(length / cellsize)
    allowable_min = half_cell - allowable * half_cell
    allowable_max = half_cell + allowable * half_cell
    num_points = x_cells * y_cells
    rnd_points = _rands(allowable_min, allowable_max, num_points * 2, seed=seed_calc)

    return [
        [x * cellsize + rnd_points[(x + y * x_cells) * 2], y * cellsize + rnd_points[(x + y * x_cells) * 2 + 1]]
        for x in range(x_cells)
        for y in range(y_cells)
    ]


def NormalizeVector(v: list[float]) -> list[float]:
    """Normalizes the vector to a size of 1, keeping the relative ratio of components."""
    mag = math.sqrt(v[0] * v[0] + v[1] * v[1])
    return [v[0] / mag, v[1] / mag]


def _rands(minval: float, maxval: float, n: int, seed: float | None = None) -> list[float]:
    """BOSL2 rands(): n uniform random floats in [minval, maxval], deterministic when seeded.
    (The original code called rands() without ever importing or porting it -- a NameError on
    every run -- so this local port is the first working version.)"""
    rng = random.Random(seed)
    return [rng.uniform(minval, maxval) for _ in range(n)]


def Voronoi(
    width: float,
    length: float,
    thickness: float,
    corner_size: float = 1,
    cellsize: float = 10,
    seed: float | None = None,
    allowable: float = 0.99,
) -> PyOpenSCAD:
    """Creates a Voronoi pattern to use on lids (and elsewhere).

    Usage::

        Voronoi(width=100, length=100, thickness=1.5)

    Args:
        width:       width of the space to fill
        length:      length of the space to fill
        thickness:   thickness of the gaps between the shapes
        corner_size: how much rounding to use in the corners (default 1)
        cellsize:    the size of the cells in the space (default 10)
        seed:        seed for the random number (default default_voronoi_seed via VoronoiPoints)
        allowable:   how much space to randomize within the cell (default 0.99)
    """
    assert width > 0, "Need to have a width specified"
    assert length > 0, "Need to have a length specified"
    assert thickness != 0, "Need to have a thickness specified"

    if seed is None:
        seed = default_voronoi_seed

    points = VoronoiPoints(width=width, length=length, cellsize=cellsize, seed=seed, allowable=allowable)
    bounding_box = 2.1 * math.sqrt(2) * cellsize
    bounding_box_square = bounding_box * bounding_box

    cutters = None
    for p1 in points:
        cell = None
        for p2 in points:
            diff = [p2[0] - p1[0], p2[1] - p1[1]]
            if p1 != p2 and diff[0] * diff[0] + diff[1] * diff[1] <= bounding_box_square:
                angle = 90 + math.degrees(math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
                mid = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
                norm = NormalizeVector(diff)
                offset_pt = [
                    mid[0] - norm[0] * (thickness / 2 + corner_size),
                    mid[1] - norm[1] * (thickness / 2 + corner_size),
                ]
                piece = (
                    square([bounding_box * 2, bounding_box])
                    .translate([-bounding_box, -bounding_box])
                    .rotate([0, 0, angle])
                    .translate(offset_pt)
                )
                cell = piece if cell is None else cell & piece
        if cell is not None:
            cutters = cell if cutters is None else cutters | cell

    base = square([width, length])
    if cutters is None:
        return base
    return base - cutters.offset(r=corner_size, _fn=16)
