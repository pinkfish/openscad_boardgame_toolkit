# mathgrrl Pentagon Tilings
#
# pentagon vertices, lattices, and offsets from Ed Pegg's Wolfram Demonstration
# http://demonstrations.wolfram.com/PentagonTilings/
#
# history of the fifteen pentagon classes from Wikipedia
# https://en.wikipedia.org/wiki/Pentagonal_tiling
#
# what is this business about there being a new pentagon that tiles the plane?
# http://www.zmescience.com/science/math/pentagon-tiles-surface-0342523454/

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

# LibFile: pentagon_tilings.py
#    All 15 known classes of convex pentagons that tile the plane.

# pentagon_tesselation_data's 15 sequential pentagon-type data blocks exceed pyright's
# code-flow complexity budget (the 'too complex to analyze' diagnostic); everything
# else in this file is still checked.
# pyright: reportGeneralTypeIssues=false
from __future__ import annotations

import numpy as np

from collections.abc import Sequence
import math
import types

from pythonscad import *
from base_bgtk import *
from pybosl2 import shapes2d


def _cosd(deg: float) -> float:
    return math.cos(math.radians(deg))


def _sind(deg: float) -> float:
    return math.sin(math.radians(deg))


def _tand(deg: float) -> float:
    return math.tan(math.radians(deg))


def _sc(scale: float, pts: list[list[float]]) -> list[list[float]]:
    """Scalar multiply every point in a path."""
    return [[p[0] * scale, p[1] * scale] for p in pts]


def _v(a: list[float], b: list[float]) -> list[float]:
    """Vector add two 2-D points."""
    return [a[0] + b[0], a[1] + b[1]]


def pentagon_tesselation_area(
    pentagon_type: str,
    pentagon_size: float,
    width: float,
    length: float,
    thickness: float,
    first_angle_modifier: float = 0,
    second_angle_modifier: float = 0,
    first_length_modifier: float = 0,
    second_length_modifier: float = 0,
    third_length_modifier: float = 0,
    line1: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line2: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line3: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    spin: float = 60,
) -> "shapes2d.Bosl2Shape2D":
    """Make the pentagon tessellation tiled across a rectangular area.

    Usage::

        pentagon_tesselation_area(pentagon_type="R1", pentagon_size=30, width=100, length=100, thickness=2)

    Args:
        pentagon_type: type of the pentagon, "R1" through "R15"
        pentagon_size: the size of the pentagon
        width:  width of the area to fill
        length: length of the area to fill
        thickness: thickness of the edges of the pattern
        first_angle_modifier/second_angle_modifier/first_length_modifier/second_length_modifier/third_length_modifier:
            tweak the shape of the pentagon (see :func:`pentagon_tesselation`)
        line1/line2/line3: profile lines used by the R2 type (default straight lines)
        spin: rotation of the whole lattice (default 60)
    """
    if line1 is None:
        line1 = [[0, 0], [1, 0]]
    if line2 is None:
        line2 = [[0, 0], [1, 0]]
    if line3 is None:
        line3 = [[0, 0], [1, 0]]

    cols = width / pentagon_size + 4
    rows = (length * 2) / pentagon_size + 4
    data = pentagon_tesselation_data(
        pentagon_type,
        pentagon_size,
        0,
        0,
        thickness,
        first_angle_modifier=first_angle_modifier,
        second_angle_modifier=second_angle_modifier,
        first_length_modifier=first_length_modifier,
        second_length_modifier=second_length_modifier,
        third_length_modifier=third_length_modifier,
        line1=line1,
        line2=line2,
        line3=line3,
    )

    # The area frame is corner-anchored 0..width x 0..length, which anchor=[-1,-1] already
    # gives; the extra half-size translate the SDF version carried put the clip window on
    # width/2..3*width/2, so the tiling only ever covered the far half of what it was asked
    # to fill. (Invisible until the fill's bounding box could be measured -- see
    # tests/test_lid_patterns.py.)
    bound = shapes2d.square([width, length], anchor=[-1, -1, 0])

    pieces = []
    for yy in range(math.floor(rows) + 1):
        for xx in range(math.floor(cols) + 1):
            dx = pentagon_size * (cols / 2 - xx) * data.x_offset[0] + pentagon_size * (rows / 2 - yy) * data.y_offset[0]
            dy = pentagon_size * (cols / 2 - xx) * data.x_offset[1] + pentagon_size * (rows / 2 - yy) * data.y_offset[1]
            pieces.append(data.points.translate([dx - pentagon_size * 2, dy - pentagon_size * 2, 0]))
    shape = pieces[0]
    for piece in pieces[1:]:
        shape = shape | piece
    shape = shape.rotate([0, 0, spin]).translate([width / 2, length / 2])

    return bound & shape


def pentagon_tesselation(
    pentagon_type: str,
    pentagon_size: float,
    x: float,
    y: float,
    thickness: float,
    first_angle_modifier: float = 0,
    second_angle_modifier: float = 0,
    first_length_modifier: float = 0,
    second_length_modifier: float = 0,
    third_length_modifier: float = 0,
    line1: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line2: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line3: "Sequence[Sequence[float]] | np.ndarray | None" = None,
) -> "shapes2d.Bosl2Shape2D":
    """Renders one tile of one of the 15 known classes of pentagon that tiles the plane,
    positioned at lattice index (x, y).

    Usage::

        pentagon_tesselation(pentagon_type="R1", pentagon_size=30, x=0, y=0, thickness=2)

    Args:
        pentagon_type: type of the pentagon, "R1" through "R15"
        pentagon_size: the size of the pentagon
        x: x index for the pattern lattice
        y: y index for the pattern lattice
        thickness: thickness of the edges of the pattern
        first_angle_modifier/second_angle_modifier/first_length_modifier/second_length_modifier/third_length_modifier:
            tweak the shape of the pentagon (see :func:`pentagon_tesselation_data`)
        line1/line2/line3: profile lines used by the R2 type (default straight lines)
    """
    data = pentagon_tesselation_data(
        pentagon_type,
        pentagon_size,
        x,
        y,
        thickness,
        first_angle_modifier=first_angle_modifier,
        second_angle_modifier=second_angle_modifier,
        first_length_modifier=first_length_modifier,
        second_length_modifier=second_length_modifier,
        third_length_modifier=third_length_modifier,
        line1=line1,
        line2=line2,
        line3=line3,
    )
    dx = pentagon_size * x * data.x_offset[0] + pentagon_size * y * data.y_offset[0]
    dy = pentagon_size * x * data.x_offset[1] + pentagon_size * y * data.y_offset[1]
    return data.points.translate([dx, dy, 0])


def pentagon_tesselation_data(
    pentagon_type: str,
    pentagon_size: float,
    x: float,
    y: float,
    thickness: float,
    first_angle_modifier: float = 0,
    second_angle_modifier: float = 0,
    first_length_modifier: float = 0,
    second_length_modifier: float = 0,
    third_length_modifier: float = 0,
    line1: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line2: "Sequence[Sequence[float]] | np.ndarray | None" = None,
    line3: "Sequence[Sequence[float]] | np.ndarray | None" = None,
) -> types.SimpleNamespace:
    """Computes the raw lattice data for one of the 15 known classes of pentagon that tiles the plane.

    Usage::

        pentagon_tesselation_data(pentagon_type="R1", pentagon_size=30, x=0, y=0, thickness=2)

    Args:
        pentagon_type: type of the pentagon, "R1" through "R15" (R1..R15, except R1 has no second
            pentagon variant labeled "R1_2" used internally)
        pentagon_size: the size of the pentagon
        x: x index for the pattern lattice (unused by the data computation itself)
        y: y index for the pattern lattice (unused by the data computation itself)
        thickness: thickness of the edges of the pattern
        first_angle_modifier: tweak angle AA, degrees in [-60, 60] (applies to R1,R2,R4-R8,R10-R13)
        second_angle_modifier: tweak angle BB, degrees in [-60, 60] (applies to R1, R2)
        first_length_modifier: tweak length b, in [-1, 1] (applies to R1-R5, R9)
        second_length_modifier: tweak length c, in [-1, 1] (applies to R1)
        third_length_modifier: tweak length e, in [-1, 1] (applies to R1, R2)
        line1/line2/line3: profile lines used by the R2 type (default straight lines)
    Returns:
        a namespace(points=<rendered region>, x_offset=[x,y], y_offset=[x,y])
    """
    if line1 is None:
        line1 = [[0, 0], [1, 0]]
    if line2 is None:
        line2 = [[0, 0], [1, 0]]
    if line3 is None:
        line3 = [[0, 0], [1, 0]]

    assert -60 <= first_angle_modifier <= 60, (
        f"Invalid first angle modifier first_angle_modifier={first_angle_modifier}"
    )
    assert -60 <= second_angle_modifier <= 60, (
        f"Invalid second angle modifier second_angle_modifier={second_angle_modifier}"
    )
    assert -1 <= first_length_modifier <= 1, (
        f"Invalid first length modifier first_length_modifier={first_length_modifier}"
    )
    assert -1 <= second_length_modifier <= 1, (
        f"Invalid second length modifier second_length_modifier={second_length_modifier}"
    )
    assert -1 <= third_length_modifier <= 1, (
        f"Invalid third length modifier third_length_modifier={third_length_modifier}"
    )

    from tesselations import (
        tesselation_polygon,
        TESSELATION_LINE_SYMETRIC,
        TESSELATION_LINE_NORMAL,
        TESSELATION_LINE_FLIPPED,
    )

    # convex initial conditions for each pentagon
    AA_init = {
        "R1": 70,
        "R2": 150,
        "R4": 135,
        "R5": 120,
        "R6": 120,
        "R7": 150,
        "R8": 90,
        "R10": 90,
        "R11": 130,
        "R12": 125,
        "R13": 135,
    }.get(pentagon_type, 0)
    BB_init = {"R1": 140, "R2": 100}.get(pentagon_type, 0)
    b_init = {"R1": 1, "R2": 0.7, "R3": 0.5, "R4": 1.25, "R5": 0.5, "R9": 1.573}.get(pentagon_type, 0)
    c_init = {"R1": 0.5}.get(pentagon_type, 0)
    e_init = {"R1": 0.7, "R2": 1.2}.get(pentagon_type, 0)

    AA_mod = AA_init + first_angle_modifier
    BB_mod = BB_init + second_angle_modifier
    b_mod = b_init + first_length_modifier
    c_mod = c_init + second_length_modifier
    e_mod = e_init + third_length_modifier

    AA = 0 if AA_mod < 0 else (360 if AA_mod > 360 else AA_mod)
    BB = 0 if BB_mod < 0 else (360 if BB_mod > 360 else BB_mod)
    b = 0 if b_mod < 0 else (2 if b_mod > 2 else b_mod)
    c = 0 if c_mod < 0 else (2 if c_mod > 2 else c_mod)
    e = 0 if e_mod < 0 else (2 if e_mod > 2 else e_mod)

    cos, sin, sqrt, tan = _cosd, _sind, math.sqrt, _tand

    # ------------------------------------------------------------------
    # TYPE 1 PENTAGON DATA: Reinhardt 1918
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R1scale = 1
        R1 = _sc(
            R1scale,
            [
                [0.5 - b * cos(AA), b * sin(AA)],
                [0.5 - b * cos(AA) + c * cos(AA + BB), b * sin(AA) - c * sin(AA + BB)],
                [-0.5 - e * cos(AA), e * sin(AA)],
                [-0.5, 0],
                [0.5, 0],
            ],
        )
        R1_2 = _sc(
            R1scale,
            [
                [-0.5 + b * cos(AA), -b * sin(AA)],
                [-0.5 + b * cos(AA) - c * cos(AA + BB), -b * sin(AA) + c * sin(AA + BB)],
                [0.5 + e * cos(AA), -e * sin(AA)],
                [0.5, 0],
                [-0.5, 0],
            ],
        )
        R1xoff = _sc(R1scale, [[-1 + b * cos(AA) - e * cos(AA), -b * sin(AA) + e * sin(AA)]])[0]
        R1yoff = _sc(
            R1scale, [[-b * cos(AA) - e * cos(AA) + c * cos(AA + BB), b * sin(AA) + e * sin(AA) - c * sin(AA + BB)]]
        )[0]

    except (ZeroDivisionError, ValueError):
        R1scale = []
        R1 = []
        R1_2 = []
        R1xoff = [0.0, 0.0]
        R1yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 2 PENTAGON DATA: Reinhardt 1918
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R2scale = 0.8
        R2 = tesselation_polygon(
            _sc(
                R2scale,
                [
                    [0.5 * (b - 2 * cos(BB)), sin(BB)],
                    [-0.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
                    [-0.5 * b + cos(AA), sin(AA)],
                    [-0.5 * b, 0],
                    [0.5 * b, 0],
                ],
            ),
            [0, 1, 2, 1, 2],
            [line1, line2, line3],
            [
                TESSELATION_LINE_SYMETRIC,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_NORMAL,
            ],
        )
        R2_2 = tesselation_polygon(
            _sc(
                R2scale,
                [
                    [
                        0.5 * (b - 2 * cos(AA) + 2 * b * cos(AA - BB) - 2 * cos(BB)),
                        -sin(AA) + b * sin(AA - BB) + sin(BB),
                    ],
                    [0.5 * b + e, 0],
                    [b / 2, 0],
                    [0.5 * (b - 2 * cos(BB)), sin(BB)],
                    [0.5 * (b + 2 * b * cos(AA - BB) - 2 * cos(BB)), b * sin(AA - BB) + sin(BB)],
                ],
            ),
            [0, 1, 2, 1, 2],
            [line1, line2, line3],
            [
                TESSELATION_LINE_SYMETRIC,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_FLIPPED,
            ],
        )
        R2_3 = tesselation_polygon(
            _sc(
                R2scale,
                [
                    [-0.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
                    [0.5 * (b - 2 * cos(BB)), sin(BB)],
                    [0.5 * b + e * cos(AA - BB) - cos(BB), e * sin(AA - BB) + sin(BB)],
                    [0.5 * b + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
                    [-0.5 * b + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
                ],
            ),
            [0, 1, 2, 1, 2],
            [line1, line2, line3],
            [
                TESSELATION_LINE_SYMETRIC,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_NORMAL,
            ],
        )
        R2_4 = tesselation_polygon(
            _sc(
                R2scale,
                [
                    [-0.5 * b + 2 * cos(AA) + (-b + e) * cos(AA - BB), 2 * sin(AA) + (-b + e) * sin(AA - BB)],
                    [-0.5 * b - e + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
                    [-b / 2 + cos(AA) + e * cos(AA - BB) - cos(BB), sin(AA) + e * sin(AA - BB) + sin(BB)],
                    [-0.5 * b + cos(AA) + e * cos(AA - BB), sin(AA) + e * sin(AA - BB)],
                    [-0.5 * b + cos(AA) + (-b + e) * cos(AA - BB), sin(AA) + (-b + e) * sin(AA - BB)],
                ],
            ),
            [0, 1, 2, 1, 2],
            [line1, line2, line3],
            [
                TESSELATION_LINE_SYMETRIC,
                TESSELATION_LINE_FLIPPED,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_NORMAL,
                TESSELATION_LINE_FLIPPED,
            ],
        )
        R2xoff = _sc(
            R2scale,
            [
                [
                    0.5 * b - cos(AA) + 0.5 * (b + 2 * b * cos(AA - BB) - 2 * cos(BB)),
                    -sin(AA) + b * sin(AA - BB) + sin(BB),
                ]
            ],
        )[0]
        R2yoff = _sc(R2scale, [[b + e - 2 * cos(AA) + (b - e) * cos(AA - BB), -2 * sin(AA) + (b - e) * sin(AA - BB)]])[
            0
        ]

    except (ZeroDivisionError, ValueError):
        R2scale = []
        R2 = []
        R2_2 = []
        R2_3 = []
        R2_4 = []
        R2xoff = [0.0, 0.0]
        R2yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 3 PENTAGON DATA: Reinhardt 1918
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R3scale = 1
        R3 = _sc(
            R3scale,
            [
                [0, 0],
                [0.5, 0.5 * sqrt(3)],
                [0.5 * b, -0.5 * sqrt(3) * (-2 + b)],
                [-0.5, sqrt(3) / 2],
                [-b, 0],
            ],
        )
        R3_2 = _sc(
            R3scale,
            [
                [-0.5 * 3, 0.5 * sqrt(3)],
                [-1, 0],
                [-b, 0],
                [-0.5, 0.5 * sqrt(3)],
                [0.5 * (-3 + b), 0.5 * sqrt(3) * (1 + b)],
            ],
        )
        R3_3 = _sc(
            R3scale,
            [
                [0, sqrt(3)],
                [-1, sqrt(3)],
                [0.5 * (-3 + b), 0.5 * sqrt(3) * (1 + b)],
                [-0.5, 0.5 * sqrt(3)],
                [0.5 * b, -0.5 * sqrt(3) * (-2 + b)],
            ],
        )
        R3xoff = _sc(R3scale, [[0.5 * 3, 0.5 * sqrt(3)]])[0]
        R3yoff = _sc(R3scale, [[0, sqrt(3)]])[0]

    except (ZeroDivisionError, ValueError):
        R3scale = []
        R3 = []
        R3_2 = []
        R3_3 = []
        R3xoff = [0.0, 0.0]
        R3yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 4 PENTAGON DATA: Reinhardt 1918
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R4scale = 0.7
        R4 = _sc(
            R4scale,
            [
                [0, 0],
                [0, 1],
                [-b * sin(AA), 1 - b * cos(AA)],
                [b * (cos(AA) - sin(AA)), 1 - b * (cos(AA) + sin(AA))],
                [-1, 0],
            ],
        )
        R4_2 = _sc(
            R4scale,
            [
                [0, 0],
                [-1, 0],
                [-1 + b * cos(AA), -b * sin(AA)],
                [-1 + b * (cos(AA) + sin(AA)), b * (cos(AA) - sin(AA))],
                [0, -1],
            ],
        )
        R4_3 = _sc(
            R4scale,
            [
                [0, 0],
                [0, -1],
                [b * sin(AA), -1 + b * cos(AA)],
                [-b * (cos(AA) - sin(AA)), -1 + b * (cos(AA) + sin(AA))],
                [1, 0],
            ],
        )
        R4_4 = _sc(
            R4scale,
            [
                [0, 0],
                [1, 0],
                [1 - b * cos(AA), b * sin(AA)],
                [1 - b * (cos(AA) + sin(AA)), -b * (cos(AA) - sin(AA))],
                [0, 1],
            ],
        )
        R4xoff = _sc(R4scale, [[-1 + b * (cos(AA) - sin(AA)), 1 - b * (cos(AA) + sin(AA))]])[0]
        R4yoff = _sc(R4scale, [[1 - b * (cos(AA) + sin(AA)), 1 - b * (cos(AA) - sin(AA))]])[0]

    except (ZeroDivisionError, ValueError):
        R4scale = []
        R4 = []
        R4_2 = []
        R4_3 = []
        R4_4 = []
        R4xoff = [0.0, 0.0]
        R4yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 5 PENTAGON DATA: Reinhardt 1918
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R5scale = 1
        R5 = _sc(
            R5scale,
            [
                [0, 0],
                [1, 0],
                [1 - b * cos(AA), b * sin(AA)],
                [0.5 * (2 - 3 * b * cos(AA) - sqrt(3) * b * sin(AA)), -0.5 * b * (sqrt(3) * cos(AA) - 3 * sin(AA))],
                [0.5, 0.5 * sqrt(3)],
            ],
        )
        R5_2 = _sc(
            R5scale,
            [
                [0, 0],
                [0.5, 0.5 * sqrt(3)],
                [0.5 * (1 - b * (cos(AA) + sqrt(3) * sin(AA))), 0.5 * (sqrt(3) * (1 - b * cos(AA)) + b * sin(AA))],
                [0.5 - sqrt(3) * b * sin(AA), 0.5 * sqrt(3) * (1 - 2 * b * cos(AA))],
                [-0.5, 0.5 * sqrt(3)],
            ],
        )
        R5_3 = _sc(
            R5scale,
            [
                [0, 0],
                [-0.5, 0.5 * sqrt(3)],
                [0.5 * (-1 + b * cos(AA) - sqrt(3) * b * sin(AA)), 0.5 * (sqrt(3) * (1 - b * cos(AA)) - b * sin(AA))],
                [
                    0.5 * (-1 + 3 * b * cos(AA) - sqrt(3) * b * sin(AA)),
                    0.5 * (sqrt(3) - sqrt(3) * b * cos(AA) - 3 * b * sin(AA)),
                ],
                [-1, 0],
            ],
        )
        R5_4 = _sc(
            R5scale,
            [
                [0, 0],
                [-1, 0],
                [-1 + b * cos(AA), -b * sin(AA)],
                [0.5 * (-2 + 3 * b * cos(AA) + sqrt(3) * b * sin(AA)), 0.5 * b * (sqrt(3) * cos(AA) - 3 * sin(AA))],
                [-0.5, -0.5 * sqrt(3)],
            ],
        )
        R5_5 = _sc(
            R5scale,
            [
                [0, 0],
                [-0.5, -0.5 * sqrt(3)],
                [0.5 * (-1 + b * cos(AA) + sqrt(3) * b * sin(AA)), 0.5 * (sqrt(3) * (-1 + b * cos(AA)) - b * sin(AA))],
                [-0.5 + sqrt(3) * b * sin(AA), 0.5 * sqrt(3) * (-1 + 2 * b * cos(AA))],
                [0.5, -0.5 * sqrt(3)],
            ],
        )
        R5_6 = _sc(
            R5scale,
            [
                [0, 0],
                [0.5, -0.5 * sqrt(3)],
                [0.5 * (1 - b * cos(AA) + sqrt(3) * b * sin(AA)), 0.5 * (sqrt(3) * (-1 + b * cos(AA)) + b * sin(AA))],
                [
                    0.5 * (1 - 3 * b * cos(AA) + sqrt(3) * b * sin(AA)),
                    0.5 * (-sqrt(3) + sqrt(3) * b * cos(AA) + 3 * b * sin(AA)),
                ],
                [1, 0],
            ],
        )
        R5xoff = _sc(
            R5scale,
            [
                [
                    0.5 * (3 - 3 * b * cos(AA) + sqrt(3) * b * sin(AA)),
                    0.5 * (-sqrt(3) + sqrt(3) * b * cos(AA) + 3 * b * sin(AA)),
                ]
            ],
        )[0]
        R5yoff = _sc(R5scale, [[-sqrt(3) * b * sin(AA), sqrt(3) * (1 - b * cos(AA))]])[0]

    except (ZeroDivisionError, ValueError):
        R5scale = []
        R5 = []
        R5_2 = []
        R5_3 = []
        R5_4 = []
        R5_5 = []
        R5_6 = []
        R5xoff = [0.0, 0.0]
        R5yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 6 PENTAGON DATA: Kershner 1968
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R6scale = 0.55
        R6 = _sc(
            R6scale,
            [
                [0.5, 0],
                [0.5 - cos(AA), sin(AA)],
                [-cos(AA / 2) - cos(AA), 0.5 * cos(AA / 4) / sin(AA / 4) + sin(AA / 2) + sin(AA)],
                [-0.5 - cos(AA / 2), sin(AA / 2)],
                [-0.5, 0],
            ],
        )
        R6_2 = _sc(
            R6scale,
            [
                [-0.5 - cos(AA / 2), sin(AA / 2)],
                [-0.5 - cos(AA / 2) + cos(3 * AA / 2), sin(AA / 2) - sin(3 * AA / 2)],
                [
                    -1 - cos(AA / 2) + cos(AA) + cos(3 * AA / 2),
                    0.5 * (-2 * cos(3 * AA / 4) + cos(7 * AA / 4)) * (1 / sin(AA / 4)),
                ],
                [-0.5 + cos(AA), -1 * sin(AA)],
                [-0.5, 0],
            ],
        )
        R6_3 = _sc(
            R6scale,
            [
                [-0.5, 0],
                [-0.5 + cos(AA), -1 * sin(AA)],
                [cos(AA / 2) + cos(AA), -0.5 * cos(AA / 4) / sin(AA / 4) - sin(AA / 2) - sin(AA)],
                [0.5 + cos(AA / 2), -sin(AA / 2)],
                [0.5, 0],
            ],
        )
        R6_4 = _sc(
            R6scale,
            [
                [0.5 + cos(AA / 2), -1 * sin(AA / 2)],
                [0.5 + cos(AA / 2) - cos(3 * AA / 2), -1 * sin(AA / 2) + sin(3 * AA / 2)],
                [
                    1 + cos(AA / 2) - cos(AA) - cos(3 * AA / 2),
                    -0.5 * (-2 * cos(3 * AA / 4) + cos(7 * AA / 4)) * (1 / sin(AA / 4)),
                ],
                [0.5 - cos(AA), sin(AA)],
                [0.5, 0],
            ],
        )
        R6xoff = _sc(R6scale, [[-1 - 2 * cos(AA / 2) + cos(3 * AA / 2), 2 * sin(AA / 2) - sin(3 * AA / 2)]])[0]
        R6yoff = _sc(
            R6scale, [[0.5 - cos(AA / 2) - 2 * cos(AA), 0.5 * cos(AA / 4) / sin(AA / 4) + sin(AA / 2) + 2 * sin(AA)]]
        )[0]

    except (ZeroDivisionError, ValueError):
        R6scale = []
        R6 = []
        R6_2 = []
        R6_3 = []
        R6_4 = []
        R6xoff = [0.0, 0.0]
        R6yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 7 PENTAGON DATA: Kershner 1968
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R7scale = 0.9
        R7denom = 4 * (2 + cos(AA) - cos(3 * AA))
        R7 = _sc(
            R7scale,
            [
                [1 - cos(AA) / 2, sin(AA) / 2],
                [-1 * cos(AA) / 2, sin(AA) / 2],
                [cos(AA) / 2, -1 * sin(AA) / 2],
                [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
                [
                    -1 * (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom,
                    (-2 * sin(2 * AA) - 4 * sin(3 * AA) + sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_2 = _sc(
            R7scale,
            [
                [
                    -1
                    * (-1 + 4 * cos(AA) - 8 * cos(2 * AA) - 2 * cos(3 * AA) + cos(4 * AA) + 2 * cos(5 * AA))
                    / R7denom,
                    (4 * sin(AA) + 6 * sin(2 * AA) - 2 * sin(3 * AA) + sin(4 * AA) - 2 * sin(5 * AA)) / R7denom,
                ],
                [
                    -1 * (-3 + 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
                    -1 * (-2 * sin(2 * AA) + 6 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
                ],
                [
                    (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom,
                ],
                [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
                [
                    -1 * (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom,
                    (-2 * sin(2 * AA) - 4 * sin(3 * AA) + sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_3 = _sc(
            R7scale,
            [
                [-1 * cos(AA) / 2, -3 * sin(AA) / 2],
                [cos(AA) / 2, -1 * sin(AA) / 2],
                [0.5 * (-2 + cos(AA)), -1 * sin(AA) / 2],
                [-1 + cos(AA) / 2 + cos(2 * AA), -1 * sin(AA) / 2 + sin(2 * AA)],
                [
                    (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_4 = _sc(
            R7scale,
            [
                [
                    -1 * (-1 + 2 * cos(2 * AA) + 4 * cos(3 * AA) + cos(4 * AA) - 2 * cos(6 * AA)) / R7denom,
                    (-4 * sin(AA) - 8 * sin(3 * AA) + sin(4 * AA) + 2 * sin(6 * AA)) / R7denom,
                ],
                [
                    (cos(AA) * (-3 * cos(AA) + cos(3 * AA) + 2 * (cos(4 * AA) + cos(5 * AA)))) / (R7denom / 2),
                    (-8 * sin(AA) - 2 * sin(3 * AA) + 5 * sin(4 * AA) + 2 * (sin(5 * AA) + sin(6 * AA))) / R7denom,
                ],
                [
                    (5 - 4 * cos(AA) - 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / (-1 * R7denom),
                    -1 * (4 * sin(AA) - 2 * sin(2 * AA) + 2 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
                ],
                [-1 + cos(AA) / 2 + cos(2 * AA), -1 * sin(AA) / 2 + sin(2 * AA)],
                [
                    (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (-4 * sin(AA) + 2 * sin(2 * AA) + 3 * sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_5 = _sc(
            R7scale,
            [
                [0.5 * (-2 + cos(AA)), -1 * sin(AA) / 2],
                [cos(AA) / 2, -1 * sin(AA) / 2],
                [-1 * cos(AA) / 2, sin(AA) / 2],
                [cos(AA) / 2, 3 * sin(AA) / 2],
                [
                    (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom,
                    (2 * sin(2 * AA) + 4 * sin(3 * AA) - sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_6 = _sc(
            R7scale,
            [
                [
                    (-1 + 4 * cos(AA) - 8 * cos(2 * AA) - 2 * cos(3 * AA) + cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
                    -1 * (4 * sin(AA) + 6 * sin(2 * AA) - 2 * sin(3 * AA) + sin(4 * AA) - 2 * sin(5 * AA)) / R7denom,
                ],
                [
                    (cos(AA) * (-3 * cos(AA) + 3 * cos(3 * AA) + 2 * cos(4 * AA))) / (R7denom / 2),
                    (-2 * sin(2 * AA) + 6 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
                ],
                [
                    -1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom,
                ],
                [cos(AA) / 2, 3 * sin(AA) / 2],
                [
                    (-1 + 4 * cos(AA) + cos(4 * AA)) / R7denom,
                    (2 * sin(2 * AA) + 4 * sin(3 * AA) - sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_7 = _sc(
            R7scale,
            [
                [cos(AA) / 2, 3 * sin(AA) / 2],
                [-1 * cos(AA) / 2, sin(AA) / 2],
                [1 - cos(AA) / 2, sin(AA) / 2],
                [-1 * cos(AA) / 2 + 2 * sin(AA) * sin(AA), 0.5 * (1 - 4 * cos(AA)) * sin(AA)],
                [
                    -1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7_8 = _sc(
            R7scale,
            [
                [
                    (-1 + 2 * cos(2 * AA) + 4 * cos(3 * AA) + cos(4 * AA) - 2 * cos(6 * AA)) / R7denom,
                    -1 * (-4 * sin(AA) - 8 * sin(3 * AA) + sin(4 * AA) + 2 * sin(6 * AA)) / R7denom,
                ],
                [
                    -1 * (cos(AA) * (-3 * cos(AA) + cos(3 * AA) + 2 * (cos(4 * AA) + cos(5 * AA)))) / (R7denom / 2),
                    (8 * sin(AA) + 2 * sin(3 * AA) - 5 * sin(4 * AA) - 2 * (sin(5 * AA) + sin(6 * AA))) / R7denom,
                ],
                [
                    (5 - 4 * cos(AA) - 2 * cos(3 * AA) + 3 * cos(4 * AA) + 2 * cos(5 * AA)) / R7denom,
                    (4 * sin(AA) - 2 * sin(2 * AA) + 2 * sin(3 * AA) + sin(4 * AA) + 2 * sin(5 * AA)) / R7denom,
                ],
                [-cos(AA) / 2 + 2 * sin(AA) * sin(AA), 0.5 * (1 - 4 * cos(AA)) * sin(AA)],
                [
                    -1 * (-1 + 4 * cos(3 * AA) + cos(4 * AA)) / R7denom,
                    (4 * sin(AA) - 2 * sin(2 * AA) - 3 * sin(4 * AA)) / R7denom,
                ],
            ],
        )
        R7xoff = _sc(
            R7scale,
            [[1 + (2 * cos(AA)) / (-2 - cos(AA) + cos(3 * AA)), (sin(AA) - sin(3 * AA)) / (2 + cos(AA) - cos(3 * AA))]],
        )[0]
        R7yoff = _sc(
            R7scale,
            [
                [
                    -1 * (sin(2 * AA) * sin(4 * AA)) / (2 + cos(AA) - cos(3 * AA)),
                    (-4 * sin(AA) + sin(2 * AA) - 4 * sin(3 * AA) + 2 * sin(4 * AA) + sin(6 * AA))
                    / (2 * (2 + cos(AA) - cos(3 * AA))),
                ]
            ],
        )[0]

    except (ZeroDivisionError, ValueError):
        R7scale = []
        R7denom = []
        R7 = []
        R7_2 = []
        R7_3 = []
        R7_4 = []
        R7_5 = []
        R7_6 = []
        R7_7 = []
        R7_8 = []
        R7xoff = [0.0, 0.0]
        R7yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 8 PENTAGON DATA: Kershner 1968
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R8scale = 0.8
        R8 = _sc(
            R8scale,
            [
                [-(1 / 2), 0],
                [1 / 2, 0],
                [1 / 2 - cos(AA), -1 * sin(AA)],
                [
                    -(3 / 4) + 9 / (4 * (5 + 4 * cos(AA / 2))) - cos(AA),
                    (-5 * (sin(AA / 2) + sin(AA)) - 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
                ],
                [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
            ],
        )
        R8_2 = _sc(
            R8scale,
            [
                [
                    -((11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2))),
                    -((3 * (3 * sin(AA / 2) + 2 * sin(AA))) / (5 + 4 * cos(AA / 2))),
                ],
                [
                    -((11 + 24 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
                    -((2 * (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2))),
                ],
                [
                    -((3 + 14 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
                    -(((11 + 20 * cos(AA / 2) + 8 * cos(AA)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2))),
                ],
                [
                    -((3 + 10 * cos(AA / 2) + 10 * cos(AA) + 4 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2))),
                    (-5 * (sin(AA / 2) + sin(AA)) - 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
                ],
                [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
            ],
        )
        R8_3 = _sc(
            R8scale,
            [
                [1 / 2, 0],
                [-(1 / 2), 0],
                [-(1 / 2) + cos(AA), sin(AA)],
                [
                    3 / 4 - 9 / (4 * (5 + 4 * cos(AA / 2))) + cos(AA),
                    (5 * (sin(AA / 2) + sin(AA)) + 2 * (sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2)),
                ],
                [1 / 2 + cos(AA / 2), sin(AA / 2)],
            ],
        )
        R8_4 = _sc(
            R8scale,
            [
                [
                    (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2)),
                    (9 * sin(AA / 2) + 6 * sin(AA)) / (5 + 4 * cos(AA / 2)),
                ],
                [
                    (11 + 24 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2)),
                    (2 * (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2))) / (5 + 4 * cos(AA / 2)),
                ],
                [
                    (3 + 14 * cos(AA / 2) + 20 * cos(AA) + 8 * cos((3 * AA) / 2)) / (10 + 8 * cos(AA / 2)),
                    ((11 + 20 * cos(AA / 2) + 8 * cos(AA)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2)),
                ],
                [
                    (3 + 10 * cos(AA / 2) + 10 * cos(AA) + 4 * (cos((3 * AA) / 2))) / (10 + 8 * cos(AA / 2)),
                    (5 * (sin(AA / 2) + sin(AA)) + 2 * sin((3 * AA) / 2)) / (5 + 4 * cos(AA / 2)),
                ],
                [1 / 2 + cos(AA / 2), sin(AA / 2)],
            ],
        )
        R8_5 = _sc(
            R8scale,
            [
                [-(1 / 2), 0],
                [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
                [-(1 / 2) - cos(AA / 2) + cos((3 * AA) / 2), 2 * cos(AA) * sin(AA / 2)],
                [
                    (-7 - 6 * cos(AA / 2) + 8 * cos(AA) + 10 * cos((3 * AA) / 2) + 4 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    (-1 * sin(AA / 2) + 4 * sin(AA) + 5 * sin((3 * AA) / 2) + 2 * sin(2 * AA)) / (5 + 4 * cos(AA / 2)),
                ],
                [-(1 / 2) + cos(AA), sin(AA)],
            ],
        )
        R8_6 = _sc(
            R8scale,
            [
                [
                    (-11 - 22 * cos(AA / 2) - 10 * cos(AA) + 8 * cos((3 * AA) / 2) + 8 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    ((-5 + 8 * cos(AA)) * (sin(AA / 2) + sin(AA))) / (5 + 4 * cos(AA / 2)),
                ],
                [
                    -((11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2))),
                    -((3 * (3 * sin(AA / 2) + 2 * sin(AA))) / (5 + 4 * cos(AA / 2))),
                ],
                [-(1 / 2) - cos(AA / 2), -1 * sin(AA / 2)],
                [-(1 / 2) - cos(AA / 2) + cos((3 * AA) / 2), 2 * cos(AA) * sin(AA / 2)],
                [
                    (-11 - 20 * cos(AA / 2) - 2 * cos(AA) + 16 * cos((3 * AA) / 2) + 8 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    (2 * (3 * cos(AA / 2) + 8 * cos(AA) + 4 * cos((3 * AA) / 2)) * sin(AA / 2)) / (5 + 4 * cos(AA / 2)),
                ],
            ],
        )
        R8_7 = _sc(
            R8scale,
            [
                [1 / 2, 0],
                [1 / 2 + cos(AA / 2), sin(AA / 2)],
                [1 / 2 + cos(AA / 2) - cos((3 * AA) / 2), -2 * cos(AA) * sin(AA / 2)],
                [
                    (7 + 6 * cos(AA / 2) - 8 * cos(AA) - 10 * cos((3 * AA) / 2) - 4 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    (sin(AA / 2) - 4 * sin(AA) - 5 * sin((3 * AA) / 2) - 2 * sin(2 * AA)) / (5 + 4 * cos(AA / 2)),
                ],
                [1 / 2 - cos(AA), -1 * sin(AA)],
            ],
        )
        R8_8 = _sc(
            R8scale,
            [
                [
                    (11 + 22 * cos(AA / 2) + 10 * cos(AA) - 8 * cos((3 * AA) / 2) - 8 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    -(((-5 + 8 * cos(AA)) * (sin(AA / 2) + sin(AA))) / (5 + 4 * cos(AA / 2))),
                ],
                [
                    (11 + 22 * cos(AA / 2) + 12 * cos(AA)) / (10 + 8 * cos(AA / 2)),
                    (9 * sin(AA / 2) + 6 * sin(AA)) / (5 + 4 * cos(AA / 2)),
                ],
                [1 / 2 + cos(AA / 2), sin(AA / 2)],
                [1 / 2 + cos(AA / 2) - cos((3 * AA) / 2), -2 * cos(AA) * sin(AA / 2)],
                [
                    (11 + 20 * cos(AA / 2) + 2 * cos(AA) - 16 * cos((3 * AA) / 2) - 8 * cos(2 * AA))
                    / (10 + 8 * cos(AA / 2)),
                    (8 * sin(AA / 2) + sin(AA) - 4 * (2 * sin((3 * AA) / 2) + sin(2 * AA))) / (5 + 4 * cos(AA / 2)),
                ],
            ],
        )
        R8xoff = _sc(
            R8scale,
            [
                [
                    (12 * cos(AA / 4) * cos(AA / 4) * (cos(AA / 2) + 2 * cos(AA))) / (5 + 4 * cos(AA / 2)),
                    3 * (4 * sin(AA / 2) + 5 * sin(AA) + 2 * sin(3 * AA / 2)) / (5 + 4 * cos(AA / 2)),
                ]
            ],
        )[0]
        R8yoff = _sc(
            R8scale,
            [
                [
                    (11 + 22 * cos(AA / 2) + 11 * cos(AA) - 4 * cos(3 * AA / 2) - 4 * cos(2 * AA))
                    / (5 + 4 * cos(AA / 2)),
                    (18 * sin(AA / 2) + 11 * sin(AA) - 4 * (sin(3 * AA / 2) + sin(2 * AA))) / (5 + 4 * cos(AA / 2)),
                ]
            ],
        )[0]

    except (ZeroDivisionError, ValueError):
        R8scale = []
        R8 = []
        R8_2 = []
        R8_3 = []
        R8_4 = []
        R8_5 = []
        R8_6 = []
        R8_7 = []
        R8_8 = []
        R8xoff = [0.0, 0.0]
        R8yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 9 PENTAGON DATA: Rice 1975
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R9scale = 0.5
        R9 = _sc(
            R9scale,
            [
                [0, -1 * sqrt(-1 + b * b)],
                [
                    -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [-2 + 4 / (b * b), (-1 - 4 / (b * b)) * sqrt(-1 + b * b)],
                [-3 + 4 / (b * b), -((4 * sqrt(-1 + b * b)) / (b * b))],
            ],
        )
        R9_2 = _sc(
            R9scale,
            [
                [
                    4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [-2 + 4 / (b * b), (-1 - 4 / (b * b)) * sqrt(-1 + b * b)],
                [
                    -1 + 4 / (b * b) + (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (4 * sqrt(-1 + b * b) * (8 - 4 * b * b + b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
            ],
        )
        R9_3 = _sc(
            R9scale,
            [
                [1, 0],
                [0, -1 * sqrt(-1 + b * b)],
                [
                    -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    -1 + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                ],
                [
                    -2 + 8 / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (16 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
            ],
        )
        R9_4 = _sc(
            R9scale,
            [
                [
                    -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    2 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (16 + 4 * b * b - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -1 + 2 / (b * b) + (2 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    -1 + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                ],
                [
                    (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (20 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
            ],
        )
        R9_5 = _sc(
            R9scale,
            [
                [
                    -6 + 12 / (b * b) + (4 * (-7 + 3 * b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (sqrt(-1 + b * b) * (-32 + 48 * b * b - 13 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -3 + 8 / (b * b) + (4 * (-7 + 3 * b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-5 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                ],
                [
                    -4 + 8 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (24 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -1 + 4 / (b * b) + (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (4 * sqrt(-1 + b * b) * (8 - 4 * b * b + b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
            ],
        )
        R9_6 = _sc(
            R9scale,
            [
                [
                    -2 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -1 + 4 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-8 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    -4 + 8 / (b * b) + (8 * (-2 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (24 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    4 * (-1 + 1 / (b * b) + (-1 + b * b) / (8 - 5 * b * b + b * b * b * b)),
                    -(
                        (sqrt(-1 + b * b) * (32 - 5 * b * b * b * b + b * b * b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -3 + 4 / (b * b) + (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (8 * (-4 + b * b) * sqrt(-1 + b * b)) / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
            ],
        )
        R9_7 = _sc(
            R9scale,
            [
                [
                    3 - 8 / (b * b) - (8 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (8 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [
                    -(4 / (b * b)) - (8 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (sqrt(-1 + b * b) * (-32 + 20 * b * b + b * b * b * b - b * b * b * b * b * b))
                    / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    1 - 4 / (b * b) - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (4 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [1, 0],
                [
                    -2 + 8 / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (16 - 9 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
            ],
        )
        R9_8 = _sc(
            R9scale,
            [
                [-1, 0],
                [
                    -2 - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -((sqrt(-1 + b * b) * (4 - 5 * b * b + b * b * b * b)) / (8 - 5 * b * b + b * b * b * b)),
                ],
                [
                    1 - 4 / (b * b) - (4 * (-3 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    -(
                        (4 * sqrt(-1 + b * b) * (8 - 6 * b * b + b * b * b * b))
                        / (b * b * (8 - 5 * b * b + b * b * b * b))
                    ),
                ],
                [1, 0],
                [0, -1 * sqrt(-1 + b * b)],
            ],
        )
        R9xoff = _sc(
            R9scale,
            [
                [
                    (4 * (-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * (-3 + b * b) * sqrt(-1 + b * b)) / (8 - 5 * b * b + b * b * b * b),
                ]
            ],
        )[0]
        R9yoff = _sc(
            R9scale,
            [
                [
                    -4 + 12 / (b * b) + (8 * (-5 + 2 * b * b)) / (8 - 5 * b * b + b * b * b * b),
                    (4 * sqrt(-1 + b * b) * (8 - 11 * b * b + 2 * b * b * b * b))
                    / (b * b * (8 - 5 * b * b + b * b * b * b)),
                ]
            ],
        )[0]

    except (ZeroDivisionError, ValueError):
        R9scale = []
        R9 = []
        R9_2 = []
        R9_3 = []
        R9_4 = []
        R9_5 = []
        R9_6 = []
        R9_7 = []
        R9_8 = []
        R9xoff = [0.0, 0.0]
        R9yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 10 PENTAGON DATA: James 1975
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R10scale = 1
        R10 = _sc(
            R10scale,
            [
                [1, 0],
                [
                    (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
                    -((-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
                ],
                [sin(AA) * (-1 + 3 / (1 + sin(AA / 2) / cos(AA / 2))), (1 / 2) * (-1 - cos(AA) + 3 * sin(AA))],
                [0, 1],
                [0, 0],
            ],
        )
        R10_2 = _sc(
            R10scale,
            [
                [0, 1],
                [
                    (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
                    (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
                ],
                [(1 / 2) * (1 + cos(AA) - 3 * sin(AA)), sin(AA) * (-1 + 3 / (1 + sin(AA / 2) / cos(AA / 2)))],
                [-1, 0],
                [0, 0],
            ],
        )
        R10_3 = _sc(
            R10scale,
            [
                [-1, 0],
                [(1 / 2) * (1 - cos(AA) - 3 * sin(AA)), (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))],
                [sin(AA) * (1 - 3 / (1 + sin(AA / 2) / cos(AA / 2))), (1 / 2) * (1 + cos(AA) - 3 * sin(AA))],
                [0, -1],
                [0, 0],
            ],
        )
        R10_4 = _sc(
            R10scale,
            [
                [0, -1],
                [
                    -((-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
                    (1 / 2) * (1 - cos(AA) - 3 * sin(AA)),
                ],
                [(1 / 2) * (-1 - cos(AA) + 3 * sin(AA)), sin(AA) * (1 - 3 / (1 + sin(AA / 2) / cos(AA / 2)))],
                [1, 0],
                [0, 0],
            ],
        )
        R10_5 = _sc(
            R10scale,
            [
                [
                    (1 / 2) * (-3 + cos(AA) + 6 / (1 + cos(AA / 2) / sin(AA / 2)) + 3 * sin(AA)),
                    -((cos(AA / 2) * (-2 + 2 * cos(AA) + sin(AA))) / (cos(AA / 2) + sin(AA / 2))),
                ],
                [
                    (1 / 2) * (-1 + cos(AA) + 3 * sin(AA)),
                    -((-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
                ],
                [
                    (-1 + cos(AA) + 2 * sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2)),
                    (1 / 2) * (-1 - cos(AA) + 3 * sin(AA)),
                ],
                [
                    (cos(AA / 2) * (-1 + cos(AA) + 2 * sin(AA))) / (cos(AA / 2) + sin(AA / 2)),
                    (cos(AA) + cos(AA / 2) / sin(AA / 2) + 2 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2)),
                ],
                [(3 * sin(AA) * sin(AA)) / (1 - cos(AA) + sin(AA)), (3 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2))],
            ],
        )
        R10_6 = _sc(
            R10scale,
            [
                [
                    (1 / 2) * (3 - cos(AA) - 6 / (1 + cos(AA / 2) / sin(AA / 2)) - 3 * sin(AA)),
                    (cos(AA / 2) * (-2 + 2 * cos(AA) + sin(AA))) / (cos(AA / 2) + sin(AA / 2)),
                ],
                [(1 / 2) * (1 - cos(AA) - 3 * sin(AA)), (-2 + 2 * cos(AA) + sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))],
                [
                    -((-1 + cos(AA) + 2 * sin(AA)) / (1 + sin(AA / 2) / cos(AA / 2))),
                    (1 / 2) * (1 + cos(AA) - 3 * sin(AA)),
                ],
                [
                    -((cos(AA / 2) * (-1 + cos(AA) + 2 * sin(AA))) / (cos(AA / 2) + sin(AA / 2))),
                    -((cos(AA) + cos(AA / 2) / sin(AA / 2) + 2 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2))),
                ],
                [
                    -((3 * sin(AA) * sin(AA)) / (1 - cos(AA) + sin(AA))),
                    -((3 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2))),
                ],
            ],
        )
        R10xoff = _sc(
            R10scale,
            [
                [
                    -3 + 3 * cos(AA) + 6 / (1 + cos(AA / 2) / sin(AA / 2)) + sin(AA),
                    (1 + 2 * cos(AA) + 4 * sin(AA)) / (1 + cos(AA / 2) / sin(AA / 2)),
                ]
            ],
        )[0]
        R10yoff = _sc(
            R10scale,
            [
                [
                    (3 - 4 * cos(AA)) / (1 + tan(AA / 2)),
                    -1 * (sin(AA / 2) + 2 * sin(3 * AA / 2)) / (cos(AA / 2) + sin(AA / 2)),
                ]
            ],
        )[0]

    except (ZeroDivisionError, ValueError):
        R10scale = []
        R10 = []
        R10_2 = []
        R10_3 = []
        R10_4 = []
        R10_5 = []
        R10_6 = []
        R10xoff = [0.0, 0.0]
        R10yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 11 PENTAGON DATA: Rice 1976
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R11scale = 1.05
        R11 = _sc(
            R11scale,
            [
                [0, 0],
                [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
                [sin(AA) - sin(2 * AA), cos(AA) * (1 + (4 * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
                [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA))],
                [0, (-2 * cos(AA) + cos(2 * AA)) / (1 - 2 * cos(AA))],
            ],
        )
        R11_2 = _sc(
            R11scale,
            [
                [0, 0],
                [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
                [sin(AA) - sin(2 * AA), -cos(AA) * (1 + (4 * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
                [-sin(2 * AA), -((4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)))],
                [0, -((-2 * cos(AA) + cos(2 * AA)) / (1 - 2 * cos(AA)))],
            ],
        )
        R11_3 = _sc(
            R11scale,
            [
                [
                    (2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA),
                    (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA)),
                ],
                [(1 - 2 * cos(AA)) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
                [
                    sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA),
                    -1 + 3 / (1 - 2 * cos(AA)) + 2 * cos(2 * AA),
                ],
                [
                    (2 - 4 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA),
                    -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA),
                ],
                [
                    (2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA),
                    -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + cos(2 * AA),
                ],
            ],
        )
        R11_4 = _sc(
            R11scale,
            [
                [
                    (2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA),
                    (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA)),
                ],
                [(1 - 2 * cos(AA)) * sin(AA), (-2 * cos(AA) * cos(AA) + cos(3 * AA)) / (-1 + 2 * cos(AA))],
                [sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA), 0],
                [(2 - 4 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -cos(AA)],
                [(2 - 6 * cos(AA) + 3 / (-1 + 2 * cos(AA))) * sin(AA), -cos(AA) + cos(2 * AA)],
            ],
        )
        R11_5 = _sc(
            R11scale,
            [
                [
                    ((-2 + 4 * cos(AA) - 3 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)),
                    (2 + cos(AA) + 2 * cos(2 * AA) - 3 * cos(3 * AA)) / (2 - 4 * cos(AA)),
                ],
                [-2 * sin(2 * AA) + sin(3 * AA), (1 + 2 * cos(AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
                [
                    (2 - 3 / (1 - 2 * cos(AA)) - 4 * cos(AA)) * sin(AA),
                    -2 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA),
                ],
                [
                    (2 - 3 / (1 - 2 * cos(AA)) - 4 * cos(AA)) * sin(AA),
                    -1 + 3 / (1 - 2 * cos(AA)) + cos(AA) + 2 * cos(2 * AA),
                ],
                [
                    sin(AA) + (3 * sin(AA)) / (-1 + 2 * cos(AA)) - 2 * sin(2 * AA),
                    -1 + 3 / (1 - 2 * cos(AA)) + 2 * cos(2 * AA),
                ],
            ],
        )
        R11_6 = _sc(
            R11scale,
            [
                [
                    ((-2 + 4 * cos(AA) - 3 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)),
                    (2 + cos(AA) + 2 * cos(2 * AA) - 3 * cos(3 * AA)) / (2 - 4 * cos(AA)),
                ],
                [-2 * sin(2 * AA) + sin(3 * AA), (1 + 2 * cos(AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
                [-2 * sin(2 * AA) + sin(3 * AA), (2 * cos(2 * AA) - 3 * cos(3 * AA) + cos(4 * AA)) / (1 - 2 * cos(AA))],
                [
                    -sin(2 * AA) + sin(3 * AA),
                    (cos(AA) - 4 * cos(3 * AA) * sin(AA / 2) * sin(AA / 2)) / (1 - 2 * cos(AA)),
                ],
                [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (1 - 2 * cos(AA))],
            ],
        )
        R11_7 = _sc(
            R11scale,
            [
                [
                    (3 * (sin(AA) - 2 * sin(2 * AA) + sin(3 * AA))) / (2 - 4 * cos(AA)),
                    (sin(AA) * sin(2 * AA)) / (-1 + 2 * cos(AA)),
                ],
                [
                    (8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
                    -3 * cos(AA) + 3 / (-1 + 2 * cos(AA)) - cos(2 * AA) + cos(3 * AA),
                ],
                [-sin(2 * AA), (1 - 3 * cos(AA) + cos(3 * AA)) / (1 - 2 * cos(AA))],
                [-sin(2 * AA), (4 * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA))],
                [(1 - 2 * cos(AA)) * sin(AA), (1 + cos(2 * AA) - cos(3 * AA)) / (-1 + 2 * cos(AA))],
            ],
        )
        R11_8 = _sc(
            R11scale,
            [
                [
                    (3 * (sin(AA) - 2 * sin(2 * AA) + sin(3 * AA))) / (2 - 4 * cos(AA)),
                    (sin(AA) * sin(2 * AA)) / (-1 + 2 * cos(AA)),
                ],
                [
                    (8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
                    -3 * cos(AA) + 3 / (-1 + 2 * cos(AA)) - cos(2 * AA) + cos(3 * AA),
                ],
                [
                    (8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
                    -cos(AA) - cos(2 * AA) + cos(3 * AA),
                ],
                [
                    (sin(AA) - 3 * sin(2 * AA) + sin(3 * AA) + sin(4 * AA)) / (1 - 2 * cos(AA)),
                    -4 * cos(AA) * sin(AA) * sin(AA),
                ],
                [(2 + 3 / (-1 + 2 * cos(AA))) * sin(AA) - 2 * sin(2 * AA), -cos(AA)],
            ],
        )
        R11xoff = _sc(
            R11scale,
            [
                [
                    (8 * cos(AA) * sin(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
                    -1 * (8 * (-1 + cos(AA)) * cos(AA) * sin(AA) * sin(AA)) / (-1 + 2 * cos(AA)),
                ]
            ],
        )[0]
        R11yoff = _sc(
            R11scale,
            [
                [
                    ((3 - 8 * cos(AA) + 4 * cos(2 * AA)) * sin(AA)) / (-1 + 2 * cos(AA)),
                    (1 + 3 * cos(AA) - 2 * cos(3 * AA)) / (-1 + 2 * cos(AA)),
                ]
            ],
        )[0]

    except (ZeroDivisionError, ValueError):
        R11scale = []
        R11 = []
        R11_2 = []
        R11_3 = []
        R11_4 = []
        R11_5 = []
        R11_6 = []
        R11_7 = []
        R11_8 = []
        R11xoff = [0.0, 0.0]
        R11yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 12 PENTAGON DATA: Rice 1976
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R12scale = 0.65
        R12 = _sc(
            R12scale,
            [
                [0, 1],
                [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
                [
                    (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (1 / 2) * (-(4 / (1 + 2 * cos(AA / 2))) + (1 / sin(AA / 4)) * (1 / sin(AA / 4))) * sin(AA),
                    2 + (1 / (-1 + cos(AA / 2)) + 1 / ((1 / 2) + cos(AA / 2))) * cos(AA),
                ],
                [0, 2],
            ],
        )
        R12_2 = _sc(
            R12scale,
            [
                [0, 1],
                [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
                [
                    (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    (1 + cos(AA / 2) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    1 / 2 * (-(4 / (1 + 2 * cos(AA / 2))) + (1 / sin(AA / 4)) * (1 / sin(AA / 4))) * sin(AA),
                    ((-1 + 4 * cos(AA / 2)) * cos(AA)) / (cos(AA / 2) - cos(AA)),
                ],
                [0, 0],
            ],
        )
        R12_3 = _sc(
            R12scale,
            [
                [
                    (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2),
                    1 + (2 * (1 + cos(AA) + cos((3 * AA) / 2))) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2),
                    (1 + 2 * cos(AA / 2) + 3 * cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
            ],
        )
        R12_4 = _sc(
            R12scale,
            [
                [
                    (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [
                    (4 * cos(AA / 4) + cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
                [3 * (cos(AA / 4) / sin(AA / 4)) - 4 * sin(AA / 2), 1],
                [3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2), 1 + 2 * cos(AA / 2)],
                [
                    (8 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    1 + (1 + cos(AA / 2) + cos((3 * AA) / 2)) / (cos(AA / 2) - cos(AA)),
                ],
            ],
        )
        R12_5 = _sc(
            R12scale,
            [
                [
                    (1 / 2) * (-3 * cos(AA / 4) - 4 * cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    2 + 1 / (-1 - 2 * cos(AA / 2)) + 1 / (-1 + cos(AA / 2)) + cos(AA / 2),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [0, 2],
                [0, 0],
                [
                    (-cos(AA / 4) - 2 * cos((3 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    2 + (2 + cos(AA / 2)) / (-cos(AA / 2) + cos(AA)),
                ],
            ],
        )
        R12_6 = _sc(
            R12scale,
            [
                [
                    (1 / 2) * (-3 * cos(AA / 4) - 4 * cos((3 * AA) / 4) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    2 + 1 / (-1 - 2 * cos(AA / 2)) + 1 / (-1 + cos(AA / 2)) + cos(AA / 2),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (cos(AA / 4) + cos((3 * AA) / 4) + 2 * (cos((5 * AA) / 4) + cos((7 * AA) / 4)))
                    * (1 / sin(3 * AA / 4)),
                    (1 + 3 * cos(AA) + 2 * cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (-2 * (cos(AA / 4) + cos((3 * AA) / 4)) + cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    (1 + cos(AA) + cos((3 * AA) / 2)) / (-cos(AA / 2) + cos(AA)),
                ],
            ],
        )
        R12_7 = _sc(
            R12scale,
            [
                [
                    (1 / 2)
                    * (11 * cos(AA / 4) + 8 * cos((3 * AA) / 4) + 7 * cos((5 * AA) / 4) + 4 * cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    6
                    + 7 * cos(AA / 2)
                    + 1 / (1 + 2 * cos(AA / 2))
                    + 4 * cos(AA)
                    - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    2
                    * (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    -(1 / 2) * (1 + 2 * cos((3 * AA) / 2)) * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ],
                [
                    2
                    * (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    8 + 8 * cos(AA / 2) + 4 * cos(AA) - 3 / 2 * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ],
                [
                    (5 * cos(AA / 4) + 4 * (cos((3 * AA) / 4) + cos((5 * AA) / 4)) + 2 * cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    6
                    + 8 * cos(AA / 2)
                    + 1 / (1 + 2 * cos(AA / 2))
                    + 4 * cos(AA)
                    - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ],
            ],
        )
        R12_8 = _sc(
            R12scale,
            [
                [
                    (1 / 2)
                    * (11 * cos(AA / 4) + 8 * cos((3 * AA) / 4) + 7 * cos((5 * AA) / 4) + 4 * cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    6
                    + 7 * cos(AA / 2)
                    + 1 / (1 + 2 * cos(AA / 2))
                    + 4 * cos(AA)
                    - (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (cos(AA / 2) + 3 * cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (2 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4) + cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (1 - cos(AA / 2) + cos(AA) + cos((3 * AA) / 2) + cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (3 * cos(AA / 4) + cos((3 * AA) / 4) + 2 * cos((5 * AA) / 4)) * (1 / sin(3 * AA / 4)),
                    (cos(AA) + 2 * cos((3 * AA) / 2)) / (-cos(AA / 2) + cos(AA)),
                ],
                [
                    (6 * cos(AA / 4) + 4 * cos((3 * AA) / 4) + 3 * cos((5 * AA) / 4) + 2 * cos((7 * AA) / 4))
                    * (1 / sin(3 * AA / 4)),
                    (3 * cos(AA) + cos((3 * AA) / 2) + 2 * cos(2 * AA)) / (-cos(AA / 2) + cos(AA)),
                ],
            ],
        )
        R12xoff = _sc(
            R12scale,
            [
                [
                    cos(AA / 4) / sin(AA / 4) + (2 * (3 + 4 * cos(AA / 2)) * sin(AA)) / (1 + 2 * cos(AA / 2)),
                    -8
                    - 10 * cos(AA / 2)
                    + 1 / (1 + 2 * cos(AA / 2))
                    - 4 * cos(AA)
                    + 2 * (1 / sin(AA / 4)) * (1 / sin(AA / 4)),
                ]
            ],
        )[0]
        R12yoff = _sc(R12scale, [[3 * (cos(AA / 4) / sin(AA / 4)) - 2 * sin(AA / 2), 1 + 2 * cos(AA / 2)]])[0]

    except (ZeroDivisionError, ValueError):
        R12scale = []
        R12 = []
        R12_2 = []
        R12_3 = []
        R12_4 = []
        R12_5 = []
        R12_6 = []
        R12_7 = []
        R12_8 = []
        R12xoff = [0.0, 0.0]
        R12yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 13 PENTAGON DATA: Rice 1977
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R13scale = 0.7
        R13 = _sc(
            R13scale,
            [
                [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
                [0, 1],
                [0, 0],
                [-1, 0],
                [-1 + 2 * cos(AA), 2 * sin(AA)],
            ],
        )
        R13_2 = _sc(
            R13scale,
            [
                [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
                [-3 + 3 * cos(AA) + sin(AA), -cos(AA) + 3 * sin(AA)],
                [3 * (-1 + cos(AA)), 3 * sin(AA)],
                [-3 + 2 * cos(AA), 2 * sin(AA)],
                [-1 + 2 * cos(AA), 2 * sin(AA)],
            ],
        )
        R13_3 = _sc(
            R13scale,
            [
                [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
                [0, 1],
                [sin(AA), 1 - cos(AA)],
                [cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
                [-2 + cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
            ],
        )
        R13_4 = _sc(
            R13scale,
            [
                [(1 / 2) * (-3 + 3 * cos(AA) + sin(AA)), (1 / 2) * (1 - cos(AA) + 3 * sin(AA))],
                [-3 + 3 * cos(AA) + sin(AA), -cos(AA) + 3 * sin(AA)],
                [-3 + 3 * cos(AA) + sin(AA), 1 - cos(AA) + 3 * sin(AA)],
                [-2 + 3 * cos(AA) + sin(AA), 1 - cos(AA) + 3 * sin(AA)],
                [-2 + cos(AA) + sin(AA), 1 - cos(AA) + sin(AA)],
            ],
        )
        R13_5 = _sc(
            R13scale,
            [
                [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
                [1, 0],
                [0, 0],
                [0, 1],
                [2 * sin(AA), 1 - 2 * cos(AA)],
            ],
        )
        R13_6 = _sc(
            R13scale,
            [
                [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
                [-cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
                [3 * sin(AA), -3 * (-1 + cos(AA))],
                [2 * sin(AA), 3 - 2 * cos(AA)],
                [2 * sin(AA), 1 - 2 * cos(AA)],
            ],
        )
        R13_7 = _sc(
            R13scale,
            [
                [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
                [1, 0],
                [1 - cos(AA), -sin(AA)],
                [1 - cos(AA) + sin(AA), -cos(AA) - sin(AA)],
                [1 - cos(AA) + sin(AA), 2 - cos(AA) - sin(AA)],
            ],
        )
        R13_8 = _sc(
            R13scale,
            [
                [(1 / 2) * (1 - cos(AA) + 3 * sin(AA)), (1 / 2) * (3 - 3 * cos(AA) - sin(AA))],
                [-cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
                [1 - cos(AA) + 3 * sin(AA), 3 - 3 * cos(AA) - sin(AA)],
                [1 - cos(AA) + 3 * sin(AA), 2 - 3 * cos(AA) - sin(AA)],
                [1 - cos(AA) + sin(AA), 2 - cos(AA) - sin(AA)],
            ],
        )
        R13xoff = _sc(R13scale, [[1 - cos(AA) - sin(AA), -1 + cos(AA) - sin(AA)]])[0]
        R13yoff = _sc(R13scale, [[3 * (-1 + cos(AA)) - 3 * sin(AA), 3 * (-1 + cos(AA)) + 3 * sin(AA)]])[0]

    except (ZeroDivisionError, ValueError):
        R13scale = []
        R13 = []
        R13_2 = []
        R13_3 = []
        R13_4 = []
        R13_5 = []
        R13_6 = []
        R13_7 = []
        R13_8 = []
        R13xoff = [0.0, 0.0]
        R13yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 14 PENTAGON DATA: Stein 1985
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R14scale = 0.52
        R14 = _sc(
            R14scale,
            [
                [(1 / 8) * (-3 + sqrt(57)), 3.51623],
                [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
                [1, 0],
                [0, 0],
                [0, 2.6937],
            ],
        )
        R14_2 = _sc(
            R14scale,
            [
                [(1 / 8) * (3 - sqrt(57)), 3.51623],
                [(1 / 8) * (9 - 3 * sqrt(57)), 1.87118],
                [-1, 0],
                [0, 0],
                [0, 2.6937],
            ],
        )
        R14_3 = _sc(
            R14scale,
            [
                [(1 / 4) * (1 + sqrt(57)), -1.64505],
                [1, 0],
                [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-1 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-1 + 3 * sqrt(57)), -0.822525],
            ],
        )
        R14_4 = _sc(
            R14scale,
            [
                [(1 / 2) * (-1 + sqrt(57)), -1.64505],
                [(1 / 4) * (-5 + 3 * sqrt(57)), 0],
                [(1 / 8) * (7 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-1 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-1 + 3 * sqrt(57)), -0.822525],
            ],
        )
        R14_5 = _sc(
            R14scale,
            [
                [(1 / 8) * (7 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-9 + 3 * sqrt(57)), 1.87118],
                [(1 / 8) * (-3 + sqrt(57)), 3.51623],
                [(1 / 4) * (-3 + sqrt(57)), 4.33875],
                [(1 / 16) * (31 + 3 * sqrt(57)), 2.80676],
            ],
        )
        R14_6 = _sc(
            R14scale,
            [
                [-1, 0],
                [1, 0],
                [(1 / 4) * (1 + sqrt(57)), -1.64505],
                [(1 / 8) * (5 + sqrt(57)), -2.46757],
                [(3 / 16) * (-11 + sqrt(57)), -0.935588],
            ],
        )
        R14xoff = _sc(R14scale, [[(1 / 2) * (1 - sqrt(57)), 4.33875]])[0]
        R14yoff = _sc(R14scale, [[(1 / 16) * (21 + sqrt(57)), 5.27434]])[0]

    except (ZeroDivisionError, ValueError):
        R14scale = []
        R14 = []
        R14_2 = []
        R14_3 = []
        R14_4 = []
        R14_5 = []
        R14_6 = []
        R14xoff = [0.0, 0.0]
        R14yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # TYPE 15 PENTAGON DATA: Mann/McLoud/VonDerau 2015
    # ------------------------------------------------------------------
    # SCAD evaluates 1/0 to inf and sqrt(-x) to nan and carries on; Python raises.
    # Every type's data is computed eagerly here regardless of which one was requested,
    # so a division or sqrt that only makes sense for another type's angles must not
    # kill this call -- the angle asserts above guarantee the REQUESTED type's own
    # block can't hit the bad values.
    try:
        R15scale = 0.165
        R15shift = [-1, 23]
        R15 = _sc(
            R15scale,
            [
                _v(R15shift, [2 - sqrt(3), -17 - 6 * sqrt(3)]),
                _v(R15shift, [6 - sqrt(3), -17 - 6 * sqrt(3)]),
                _v(R15shift, [3 * (2 + sqrt(3)), -13 - 6 * sqrt(3)]),
                _v(R15shift, [6 + sqrt(3), -11 - 6 * sqrt(3)]),
                _v(R15shift, [2 - sqrt(3), -13 - 6 * sqrt(3)]),
            ],
        )
        R15_2 = _sc(
            R15scale,
            [
                _v(R15shift, [-sqrt(3), -13 - 4 * sqrt(3)]),
                _v(R15shift, [sqrt(3), -11 - 4 * sqrt(3)]),
                _v(R15shift, [8 + sqrt(3), -11 - 4 * sqrt(3)]),
                _v(R15shift, [6 + sqrt(3), -11 - 6 * sqrt(3)]),
                _v(R15shift, [2 - sqrt(3), -13 - 6 * sqrt(3)]),
            ],
        )
        R15_3 = _sc(
            R15scale,
            [
                _v(R15shift, [6 + sqrt(3), -11 - 6 * sqrt(3)]),
                _v(R15shift, [8 + sqrt(3), -11 - 4 * sqrt(3)]),
                _v(R15shift, [8 + 5 * sqrt(3), -7 - 4 * sqrt(3)]),
                _v(R15shift, [8 + 5 * sqrt(3), -11 - 4 * sqrt(3)]),
                _v(R15shift, [3 * (2 + sqrt(3)), -13 - 6 * sqrt(3)]),
            ],
        )
        R15_4 = _sc(
            R15scale,
            [
                _v(R15shift, [-sqrt(3), -13 - 4 * sqrt(3)]),
                _v(R15shift, [-2 - sqrt(3), -13 - 2 * sqrt(3)]),
                _v(R15shift, [-2 - sqrt(3), -5 - 2 * sqrt(3)]),
                _v(R15shift, [-2 + sqrt(3), -7 - 2 * sqrt(3)]),
                _v(R15shift, [sqrt(3), -11 - 4 * sqrt(3)]),
            ],
        )
        R15_5 = _sc(
            R15scale,
            [
                _v(R15shift, [4 + sqrt(3), -11 - 4 * sqrt(3)]),
                _v(R15shift, [4 + sqrt(3), -7 - 4 * sqrt(3)]),
                _v(R15shift, [sqrt(3), -7]),
                _v(R15shift, [-2 + sqrt(3), -7 - 2 * sqrt(3)]),
                _v(R15shift, [sqrt(3), -11 - 4 * sqrt(3)]),
            ],
        )
        R15_6 = _sc(
            R15scale,
            [
                _v(R15shift, [-2 + sqrt(3), -7 - 2 * sqrt(3)]),
                _v(R15shift, [sqrt(3), -7]),
                _v(R15shift, [sqrt(3), 1]),
                _v(R15shift, [-sqrt(3), -1]),
                _v(R15shift, [-2 - sqrt(3), -5 - 2 * sqrt(3)]),
            ],
        )
        R15_7 = _sc(
            R15scale,
            [
                _v(R15shift, [-2 + sqrt(3), 17 + 6 * sqrt(3)]),
                _v(R15shift, [-6 + sqrt(3), 17 + 6 * sqrt(3)]),
                _v(R15shift, [-3 * (2 + sqrt(3)), 13 + 6 * sqrt(3)]),
                _v(R15shift, [-6 - sqrt(3), 11 + 6 * sqrt(3)]),
                _v(R15shift, [-2 + sqrt(3), 13 + 6 * sqrt(3)]),
            ],
        )
        R15_8 = _sc(
            R15scale,
            [
                _v(R15shift, [sqrt(3), 13 + 4 * sqrt(3)]),
                _v(R15shift, [-sqrt(3), 11 + 4 * sqrt(3)]),
                _v(R15shift, [-8 - sqrt(3), 11 + 4 * sqrt(3)]),
                _v(R15shift, [-6 - sqrt(3), 11 + 6 * sqrt(3)]),
                _v(R15shift, [-2 + sqrt(3), 13 + 6 * sqrt(3)]),
            ],
        )
        R15_9 = _sc(
            R15scale,
            [
                _v(R15shift, [-6 - sqrt(3), 11 + 6 * sqrt(3)]),
                _v(R15shift, [-8 - sqrt(3), 11 + 4 * sqrt(3)]),
                _v(R15shift, [-8 - 5 * sqrt(3), 7 + 4 * sqrt(3)]),
                _v(R15shift, [-8 - 5 * sqrt(3), 11 + 4 * sqrt(3)]),
                _v(R15shift, [-3 * (2 + sqrt(3)), 13 + 6 * sqrt(3)]),
            ],
        )
        R15_10 = _sc(
            R15scale,
            [
                _v(R15shift, [sqrt(3), 13 + 4 * sqrt(3)]),
                _v(R15shift, [2 + sqrt(3), 13 + 2 * sqrt(3)]),
                _v(R15shift, [2 + sqrt(3), 5 + 2 * sqrt(3)]),
                _v(R15shift, [2 - sqrt(3), 7 + 2 * sqrt(3)]),
                _v(R15shift, [-sqrt(3), 11 + 4 * sqrt(3)]),
            ],
        )
        R15_11 = _sc(
            R15scale,
            [
                _v(R15shift, [-4 - sqrt(3), 11 + 4 * sqrt(3)]),
                _v(R15shift, [-4 - sqrt(3), 7 + 4 * sqrt(3)]),
                _v(R15shift, [-sqrt(3), 7]),
                _v(R15shift, [2 - sqrt(3), 7 + 2 * sqrt(3)]),
                _v(R15shift, [-sqrt(3), 11 + 4 * sqrt(3)]),
            ],
        )
        R15_12 = _sc(
            R15scale,
            [
                _v(R15shift, [2 - sqrt(3), 7 + 2 * sqrt(3)]),
                _v(R15shift, [-sqrt(3), 7]),
                _v(R15shift, [-sqrt(3), -1]),
                _v(R15shift, [sqrt(3), 1]),
                _v(R15shift, [2 + sqrt(3), 5 + 2 * sqrt(3)]),
            ],
        )
        R15xoff = _sc(R15scale, [[2 * (1 + sqrt(3)), 2 * (3 + sqrt(3))]])[0]
        R15yoff = _sc(R15scale, [[2 * (-8 - 5 * sqrt(3)), 2 * (9 + 4 * sqrt(3))]])[0]

    except (ZeroDivisionError, ValueError):
        R15scale = []
        R15shift = [0.0, 0.0]
        R15 = []
        R15_2 = []
        R15_3 = []
        R15_4 = []
        R15_5 = []
        R15_6 = []
        R15_7 = []
        R15_8 = []
        R15_9 = []
        R15_10 = []
        R15_11 = []
        R15_12 = []
        R15xoff = [0.0, 0.0]
        R15yoff = [0.0, 0.0]

    # ------------------------------------------------------------------
    # RENDER: select the pattern for the requested type
    # ------------------------------------------------------------------
    patterns = {
        "R1": [R1, [R1, R1_2], R1xoff, R1yoff],
        "R2": [R2, [R2, R2_2, R2_3, R2_4], R2xoff, R2yoff],
        "R3": [R3, [R3, R3_2, R3_3], R3xoff, R3yoff],
        "R4": [R4, [R4, R4_2, R4_3, R4_4], R4xoff, R4yoff],
        "R5": [R5, [R5, R5_2, R5_3, R5_4, R5_5, R5_6], R5xoff, R5yoff],
        "R6": [R6, [R6, R6_2, R6_3, R6_4], R6xoff, R6yoff],
        "R7": [R7, [R7, R7_2, R7_3, R7_4, R7_5, R7_6, R7_7, R7_8], R7xoff, R7yoff],
        "R8": [R8, [R8, R8_2, R8_3, R8_4, R8_5, R8_6, R8_7, R8_8], R8xoff, R8yoff],
        "R9": [R9, [R9, R9_2, R9_3, R9_4, R9_5, R9_6, R9_7, R9_8], R9xoff, R9yoff],
        "R10": [R10, [R10, R10_2, R10_3, R10_4, R10_5, R10_6], R10xoff, R10yoff],
        "R11": [R11, [R11, R11_2, R11_3, R11_4, R11_5, R11_6, R11_7, R11_8], R11xoff, R11yoff],
        "R12": [R12, [R12, R12_2, R12_3, R12_4, R12_5, R12_6, R12_7, R12_8], R12xoff, R12yoff],
        "R13": [R13, [R13, R13_2, R13_3, R13_4, R13_5, R13_6, R13_7, R13_8], R13xoff, R13yoff],
        "R14": [R14, [R14, R14_2, R14_3, R14_4, R14_5, R14_6], R14xoff, R14yoff],
        "R15": [
            R15,
            [R15, R15_2, R15_3, R15_4, R15_5, R15_6, R15_7, R15_8, R15_9, R15_10, R15_11, R15_12],
            R15xoff,
            R15yoff,
        ],
    }
    pattern = patterns.get(pentagon_type, [[], [], [0, 0], [0, 0]])

    points = inner_pentagon_tesselation(pattern=pattern, pentagon_size=pentagon_size, thickness=thickness)
    return types.SimpleNamespace(y_offset=pattern[2], x_offset=pattern[3], points=points)


def _clean_path(pts: list[list[float]]) -> list[list[float]]:
    """Drops consecutive duplicate points and collinear middle points (the same clean-up the
    pybosl2 port's deduplicate()/path_merge_collinear() did before the region offsets), so the
    polygon SDF machinery never sees zero-length or degenerate edges."""
    out: list[list[float]] = []
    for q in pts:
        if not out or math.dist(out[-1], q) > 1e-9:
            out.append([float(q[0]), float(q[1])])
    if len(out) > 1 and math.dist(out[0], out[-1]) < 1e-9:
        out.pop()
    merged: list[list[float]] = []
    n = len(out)
    for i in range(n):
        a, b, c = out[(i - 1) % n], out[i], out[(i + 1) % n]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cross) > 1e-9:
            merged.append(b)
    return merged


def pentagon_border(vertices: list[list[float]], size: float, thickness: float) -> "shapes2d.Bosl2Shape2D":
    """Internal: the outline ring of one pentagon instance -- the pentagon grown a hair minus
    the pentagon shrunk by the wall thickness.

    Direct 2-D CSG, not an SDF. The SDF form was exact and elegant, but a lid's worth of these
    can only reach the CSG lid stack by MESHING, which cost minutes per lid and made the
    result impossible to measure (reading a bounding box off it crashed the app). The offsets
    are the same two subtractions either way."""
    scaled = _clean_path(_sc(size, vertices))
    return shapes2d.polygon(scaled).offset(delta=0.01) - shapes2d.polygon(scaled).offset(delta=-thickness)


def inner_pentagon_tesselation(pattern: list, pentagon_size: float, thickness: float) -> "shapes2d.Bosl2Shape2D":
    """Internal: every pentagon ring in the pattern, unioned."""
    pieces = [pentagon_border(vertices=v, size=pentagon_size, thickness=thickness) for v in pattern[1]]
    assert pieces, "pentagon pattern has no pentagons -- unknown pentagon_type?"
    shape = pieces[0]
    for piece in pieces[1:]:
        shape = shape | piece
    return shape
