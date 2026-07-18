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

# LibFile: slicing.py
#    Pieces for slicing a model into sections to print on smaller print areas.
#
# FileSummary: Pieces for slicing a model into sections.
# FileGroup: Slicing

from __future__ import annotations
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2 import transforms

import math


# ---------------------------------------------------------------------------
# Section: Slicing
# ---------------------------------------------------------------------------


def _scad_range(start: float, step: float, stop: float) -> list[float]:
    """Python equivalent of OpenSCAD's [start:step:stop] numeric range."""
    if step == 0:
        return [start]
    n = math.floor((stop - start) / step + 1e-9)
    return [start + i * step for i in range(n + 1)]


def SplitBox(
    size: list[float],
    obj: PyOpenSCAD,
    join_shape: PyOpenSCAD,
    apart: float = 10,
    minX: float = -200,
    maxX: float = 200,
    minY: float = -200,
    maxY: float = 200,
    minZ: float = -200,
    maxZ: float = 200,
    play: float = 0.1,
    y: list[float] | None = None,
    orient: list[float] | None = None,
    spin: float = 0,
) -> PyOpenSCAD:
    """Slices a box into left and right parts with a puzzle-join interface.

    Usage::

        SplitBox(
            size=[100, 50, 20], spin=90,
            obj=MakeBoxWithSlipoverLid(...),
            join_shape=MakePuzzleJoin(),
        )

    Args:
        size:       [width, length, height] of the object
        obj:        the solid object to slice
        join_shape: 2-D shape used for the puzzle join (from MakePuzzleJoin)
        apart:      how far to separate the two halves (default 10)
        minX/maxX/minY/maxY/minZ/maxZ: cutting bounds (default ±200)
        play:       clearance added around the join (default 0.1)
        y:          explicit list of y-positions for join points
        orient:     BOSL2 orientation (default UP)
        spin:       BOSL2 spin (default 0)
    """
    if y is None:
        y = []
    if orient is None:
        orient = TOP

    yy = y if len(y) > 0 else _scad_range(minY, (maxY - minY) / 10, maxY)
    tmat = transforms.reorient(anchor=CENTER, spin=spin, orient=orient, size=[1, 1, 1])
    new_pts = transforms.apply(tmat, [[apart / 2, 0, 0], [-apart / 2, 0, 0]])

    def bound_box() -> PyOpenSCAD:
        return cube([maxX, maxY - minY, maxZ - minZ]).translate([0, minY, minZ]).multmatrix(tmat)

    obj_centered = obj.translate([-size[0] / 2, -size[1] / 2, -size[2] / 2])

    # Right half: intersect with the bound box, then cut a puzzle-join slot
    # (widened by `play` via a Minkowski sum) at each y position.
    right = obj_centered & bound_box()
    for yval in yy:
        y_pt = transforms.apply(tmat, [[0, yval, minZ]])[0]
        cutter = minkowski(join_shape.linear_extrude(height=maxZ - minZ), sphere(r=play)).multmatrix(tmat).translate(y_pt)
        right = right - cutter
    right = right.translate(new_pts[0])

    # Left half: subtract the bound box, but punch the puzzle-join shape
    # (without play) back out of that cut so the two halves interlock.
    bound = bound_box()
    for yval in yy:
        y_pt = transforms.apply(tmat, [[0, yval, minZ]])[0]
        plug = join_shape.linear_extrude(height=maxZ - minZ).multmatrix(tmat).translate(y_pt)
        bound = bound - plug
    left = (obj_centered - bound).translate(new_pts[1])

    return right | left


def MakePuzzleJoin(height: float = 10, width: float = 10, base: float = 5, stem: float = 6) -> PyOpenSCAD:
    """Makes a 2-D puzzle-piece join shape for use with SplitBox.

    Usage::

        MakePuzzleJoin()
        MakePuzzleJoin(height=20, width=5, base=10, stem=5)

    Args:
        height: total height/length of the puzzle piece (default 10)
        width:  width of the circular head (default 10)
        base:   width of the stem base (default 5)
        stem:   stem length (default 6)
    """
    stem_part = square([stem, base]).translate([0, -base / 2, 0])
    head = circle(d=width).scale([(height - stem) * 2 / width, 1, 0]).translate([stem, 0, 0])
    return stem_part | head
