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

# LibFile: lizard.py
#    Lizard (Escher-style) tesselation.

from __future__ import annotations
import math
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2.paths import Path


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. HexagonalTesselation /
# HexagonTesselationRepeatAtLocation / HexagonTesselationRepeat are imported
# lazily below since tesselations is a large sibling module converted
# separately.
_bosl2 = osuse("BOSL2/std.scad")

_LIZARD_TOP = [
    [-0.5, 0.0], [-0.15, -0.3], [-0.0, -0.3], [0.25, -0.05], [0.05, 0.35],
    [0.2, 0.4], [0.45, 0.35], [0.45, 0.2], [0.35, 0.15], [0.5, 0.0],
]
_LIZARD_TAIL = [
    [-0.5, 0], [-0.65, -0.35], [-0.4, -0.35], [-0.25, -0.25], [0, -0.2],
    [0.1, 0], [0.05, 0.3], [-0.15, 0.5], [0.25, 0.35], [0.35, 0.1],
]
_LIZARD_OTHER_LEG = [
    [-0.5, 0], [-0.35, -0.25], [-0.35, -0.55], [-0.05, -0.45], [-0.15, -0.05],
    [0.15, 0.05], [0.3, 0.15], [0.5, 0],
]


def LizardHexTesselation(radius: float, thickness: float = 0, outer_offset: float = 0) -> list:
    """A hex tesselation of the Escher lizard.

    Can be rotated and used to fill in hex spaces when doing tesselations.

    Usage::

        LizardHexTesselation(radius=29)
        region(LizardHexTesselation(radius=29))

    Args:
        radius:    the radius of the hex to use
        thickness: thickness of the lines (default 0)
        outer_offset: extra space to put around the shape (default 0)
    """
    from tesselations import HexagonalTesselation

    sized_lizard_points = Path(
        HexagonalTesselation(points=[_LIZARD_TAIL, _LIZARD_TOP, _LIZARD_OTHER_LEG], radius=radius)
    ).merge_collinear()
    if outer_offset == 0 and thickness == 0:
        return sized_lizard_points

    outer = sized_lizard_points.offset(delta=outer_offset)
    inner = sized_lizard_points.offset(delta=-thickness) if thickness > 0 else []
    return _bosl2.difference(outer, inner)


def LizardSingle(size: float) -> PyOpenSCAD:
    """Creates a single lizard.

    Usage::

        LizardSingle(size=20)

    Args:
        size: the size of the lizard
    """
    assert size > 0, "Need to have a size specified"
    return polygon(LizardHexTesselation(radius=size / 2))


def LizardSingleOutline(size: float, thickness: float) -> PyOpenSCAD:
    """Creates a single lizard with an outline.

    Usage::

        LizardSingleOutline(size=20, thickness=1)

    Args:
        size: the size of the lizard
        thickness: the thickness to use
    """
    assert size > 0, f"Need to have a size specified size={size}"
    assert thickness > 0, f"Need to have a thickness specified thickness={thickness}"
    return region(LizardHexTesselation(radius=size / 2, thickness=thickness))


def HexagonalTesselationTriangle(size: float, pts: list) -> list:
    """Makes the triangle that can be used to fill in the hexagonal tesselation, rotated.

    Usage::

        HexagonalTesselationTriangle(size=20, pts=LizardHexTesselation(radius=10, thickness=1))

    Args:
        size: size of the hex
        pts:  the path/region data to repeat 3 times around the triangle
    """
    assert size > 0, f"Need to have a size specified size={size}"
    side_length = 2 * size * math.sin(math.radians(30))
    apothem = math.sqrt(3) / 2 * side_length

    combined = _bosl2.union(
        [
            pts,
            Path(pts).rot(240).move([apothem / 2, size * 3 / 4]),
            Path(pts).rot(120).move([apothem, 0]),
        ]
    )
    return Path(combined).move([-apothem / 2, size])


def LizardTriangle(size: float, thickness: float = 0, outer_offset: float = 0) -> PyOpenSCAD:
    """Makes the triangle that can be used to fill in the lizard tesselation in a wider group.

    This will not need to be rotated.

    Usage::

        LizardTriangle(size=20, thickness=2)
        LizardTriangle(size=20, thickness=2, outer_offset=0.1)

    Args:
        size: size the hex
        thickness: thickness of the lines (default 0)
        outer_offset: how much padding on the outside (default 0)
    """
    pts = LizardHexTesselation(radius=size / 2, thickness=thickness, outer_offset=outer_offset)
    return region(HexagonalTesselationTriangle(size=size, pts=pts))


def LizardRepeatAtLocation(x: int, y: int, size: float, thickness: float, outer_offset: float = 0) -> PyOpenSCAD:
    """Creates a lizard at a specific spot in a grid given an x and a y location.

    Usage::

        LizardRepeatAtLocation(x=0, y=0, size=20, thickness=1)
        LizardRepeatAtLocation(x=0, y=0, size=20, thickness=1, outer_offset=0.1)

    Args:
        x: the x location to generate at
        y: the y location to generate at
        size: the size of the lizard
        thickness: the thickness of the lines
        outer_offset: extra space to put around the shape (default 0)
    """
    from tesselations import HexagonTesselationRepeatAtLocation

    assert x is not None, "Need to have a x specified"
    assert y is not None, "Need to have a y specified"
    assert size > 0, f"Need to have a size specified size={size}"

    triangle = LizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset)
    return HexagonTesselationRepeatAtLocation(x=x, y=y, size=size, children=triangle)


def LizardRepeat(rows: int, cols: int, size: float, thickness: float, outer_offset: float = 0.01) -> PyOpenSCAD:
    """Creates a lizard blob that can be repeated.

    Usage::

        LizardRepeat(rows=4, cols=4, size=20, thickness=1)

    Args:
        rows: number of rows to generate
        cols: number of columns to generate
        size: the size of the lizard
        thickness: the thickness of the lines
        outer_offset: offset for the outer edge (default 0.01)
    """
    from tesselations import HexagonTesselationRepeat

    assert rows > 0, "Need to have a rows specified"
    assert cols > 0, "Need to have a cols specified"
    assert size > 0, "Need to have a size specified"
    assert thickness > 0, "Need to have a thickness specified"

    triangle = LizardTriangle(size=size, thickness=thickness, outer_offset=outer_offset)
    return HexagonTesselationRepeat(rows=rows, cols=cols, size=size, children=triangle)
