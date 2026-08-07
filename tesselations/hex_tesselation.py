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

# LibFile: hex_tesselation.py
#    Hexagon-grid helpers and the flying-bird tesselation.

from __future__ import annotations
import math
import types
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from pybosl2 import Path2D
from pybosl2 import Bezier


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. tesselation_polygon and
# the TESSELATION_LINE_* constants are imported lazily below since
# tesselations is a large sibling module converted separately.


def generate_hexagon(
    side_lengths: list[float],
    interior_angles: list[float],
    current_x: float = 0,
    current_y: float = 0,
    current_angle: float = 0,
    num: int = 0,
) -> list[list[float]]:
    """Calculates vertices for an irregular hexagon from side lengths and interior angles.

    Args:
        side_lengths:     the lengths of the sides
        interior_angles:  the interior angles, same length as side_lengths
        current_x/current_y/current_angle/num: internal recursion counters
    """
    if num >= len(side_lengths):
        return [[0, 0]]
    assert sum(interior_angles) < 180 * (len(side_lengths) - 1), (
        f"Sum of angles less than {180 * (len(side_lengths) - 2)}"
    )
    assert len(interior_angles) == len(side_lengths), "Interior angle size and side length size should be the same"

    new_angle = 180 - interior_angles[num] + current_angle
    new_x = side_lengths[num] * math.cos(math.radians(current_angle)) + current_x
    new_y = side_lengths[num] * math.sin(math.radians(current_angle)) + current_y
    return [[new_x, new_y]] + generate_hexagon(
        side_lengths, interior_angles, current_x=new_x, current_y=new_y, current_angle=new_angle, num=num + 1
    )


def FlyingBirdTesselation(size: float, thickness: float = 0, outer_offset: float = 0, spin: float = 0) -> types.SimpleNamespace:
    """Computes the flying-bird tile data.

    Usage::

        FlyingBirdTesselation(20)
        FlyingBirdTesselation(20, thickness=2)

    Args:
        size:      size of the bird
        thickness: thickness of the bird (default 0)
        outer_offset: extra outward offset (default 0)
        spin:      rotation of the underlying hexagon (default 0)
    Returns:
        a tile-data object with .geometry (native 2-D shape), .x_vec, .y_vec, .angles
    """
    from tesselations import tesselation_polygon, TESSELATION_LINE_FLIPPED_REVERSE, TESSELATION_LINE_FLIPPED, TESSELATION_LINE_NORMAL

    ratio = 1 / 22 * size
    s1 = 15 * ratio
    s3 = 22 * ratio
    sides = [s1, s1, s1, s3, s1]
    angles = [180, 125.1, 79.5, 156.428, 100]

    line2 = Bezier.flatten(
        [
            Bezier.begin([0, 0], -20, 0.4),
            Bezier.tang([0.25, 0.0], 0, 0.2, 0.4),
            Bezier.tang([0.4, -0.25], 0, 0, 0),
            Bezier.end([1, 0], 230, 1),
        ]
    ).curve(20)
    line3 = list(
        reversed(
            [
                [1 - i[0], i[1]]
                for i in Bezier.flatten(
                    [Bezier.begin([0, 0], -45, 0.8), Bezier.end([1, 0], 235, 0.8)]
                ).curve(20)
            ]
        )
    )
    # NATIVE, not osuse: a failing assert inside an osuse'd .scad function aborts the whole
    # process rather than raising (tests/repro_osuse_assert_aborts.py), and this was the last
    # such call in the toolkit. BOSL2's smooth_path(method="corners") routes through
    # path_to_bezcornerpath(), which pybosl2 ports as Path2D.to_bezcornerpath().
    #
    # The .scad says size=0.3 -- and 0.3 CANNOT be used. This profile's shortest segment is
    # 0.038, so a 0.3 corner offset puts each control point well past its neighbours and the
    # resulting outline SELF-INTERSECTS (Path2D.is_path_simple() is False at 0.3 and 0.1,
    # True from 0.05 down; the point count is 54 either way). A self-intersecting tile is not
    # just cosmetically wrong: every boolean against it is pathological, and it took a
    # flying-bird lid from ~5s to over 30 MINUTES -- it was the single reason the lid-pattern
    # suite could not finish. Pick the largest offset that keeps the outline simple instead
    # of hard-coding one, so the choice stays honest if the profile is ever edited.
    profile = Path2D(
        [
            [-1, 0], [-0.951467, 0.23843], [-0.84139, 0.462284], [-0.746843, 0.428975],
            [-0.751917, 0.323591], [-0.674043, 0.280095], [-0.576252, 0.374566],
            [-0.49338, 0.341715], [-0.479721, 0.200504], [-0.269411, 0.261361],
            [-0.240604, 0.121256], [-0.0694036, 0.168683], [0.00618108, 0.133237],
            [0.00442596, 0.0381548], [0, 0],
        ],
        closed=False,
    )
    smoothed = None
    for corner_size in (0.3, 0.15, 0.08, 0.05, 0.03, 0.015):
        candidate = profile.to_bezcornerpath(corner_size, fn=3)  # .scad: splinesteps=3
        if candidate.is_path_simple():
            smoothed = candidate
            break
    assert smoothed is not None, "no corner size leaves the flying-bird profile simple"
    line1 = [[i[0] + 1, i[1]] for i in smoothed]

    hexagon = Path2D(generate_hexagon(sides, angles)).rot(spin) if spin != 0 else generate_hexagon(sides, angles)

    new_hex = tesselation_polygon(
        hexagon,
        [1, 2, 0, 1, 0, 2],
        [line1, line2, line3],
        [
            TESSELATION_LINE_FLIPPED_REVERSE,
            TESSELATION_LINE_FLIPPED,
            TESSELATION_LINE_FLIPPED,
            TESSELATION_LINE_NORMAL,
            TESSELATION_LINE_NORMAL,
            TESSELATION_LINE_NORMAL,
        ],
    )

    rot_hex = Path2D(hexagon).yflip().rot(180 - (angles[1] - spin * 2)).move(hexagon[3])
    rot_new_hex = Path2D(new_hex).yflip().rot(180 - (angles[1] - spin * 2)).move(hexagon[3])
    x_vec = [hexagon[4][0] - hexagon[0][0], hexagon[4][1] - hexagon[0][1]]
    y_vec = rot_hex[3]

    # outline_shell, NOT DifferenceWithOffset: this outline is 186 points of fine concave
    # detail, and up to pybosl2 0.6.7 Path2D.offset() (which DifferenceWithOffset's pts= form
    # uses) moved vertices without resolving the self-intersections that creates -- the outline
    # was simple and every offset of it was not, at ANY distance including +0.2 outward.
    # Tangled rings make every later boolean pathological: tiling twenty of them did not finish
    # in fifteen minutes, which is why FLYING_BIRD could never build a lid. 0.7 repairs the
    # folds, so both routes are sound now; this stays on the native offsetter, which clips them
    # away in one call and meshes the tiling in about five seconds.
    geometry = (
        outline_shell(new_hex, thickness=thickness, outer_offset=outer_offset)
        | outline_shell(rot_new_hex, thickness=thickness, outer_offset=outer_offset)
    )

    return types.SimpleNamespace(geometry=geometry, y_vec=y_vec, x_vec=x_vec, angles=angles)


def TesselationFlyingBirdGrid(
    row: int, col: int, size: float, thickness: float, outer_offset: float = 0.1, spin: float = 0
) -> PyOpenSCAD:
    """The flying-bird shape, tiled in a grid.

    Usage::

        TesselationFlyingBirdGrid(5, 5, size=30, thickness=1)

    Args:
        row:   number of rows
        col:   number of columns
        size:  size of the bird
        thickness: thickness of the bird
        outer_offset: extra outward offset (default 0.1)
        spin:  rotation of the underlying hexagon (default 0)
    """
    assert row > 0, "Need a row"
    assert col > 0, "Need a col"
    assert size > 0, "Need a size"
    assert thickness > 0, "Need a thickness"

    bird = FlyingBirdTesselation(size, thickness=thickness, outer_offset=outer_offset, spin=spin)
    tile = bird.geometry

    pieces = [
        tile.translate(
            [i * bird.x_vec[0] + j * bird.y_vec[0], i * bird.x_vec[1] + j * bird.y_vec[1], 0]
        )
        for i in range(row + 1)
        for j in range(col + 1)
    ]
    # Balanced union, not `shape = shape | piece`. PythonSCAD assembles the CSG tree
    # lazily, so a left fold looks free and then costs everything at MESH time: Manifold
    # re-booleans the whole accumulated tiling once per cell. These bird outlines OVERLAP
    # (see FlyingBirdTesselation), so every one of those is real polygon clipping -- this
    # single loop was taking a flying-bird lid past the test harness's 15-minute timeout.
    shape = union_all_2d(pieces)
    assert shape is not None
    return shape


def TesselationFlyingBirdArea(width: float, length: float, size: float, thickness: float, spin: float = 0) -> PyOpenSCAD:
    """The flying-bird shape, tiled across an area.

    Usage::

        TesselationFlyingBirdArea(200, 100, size=50, thickness=2)

    Args:
        width:  width of the space
        length: length of the space
        size:   size of the bird
        thickness: thickness of the bird
        spin:  rotation of the underlying hexagon (default 0)
    """
    assert width > 0, "Need a width"
    assert length > 0, "Need a length"
    assert size > 0, "Need a size"
    assert thickness > 0, "Need a thickness"

    cols = math.floor(width / 2.5 / size + 1)
    rows = math.floor(length / 1.3 / size + 1)

    grid = TesselationFlyingBirdGrid(row=rows, col=cols, size=size, thickness=thickness, outer_offset=0.2, spin=-27.5)
    return grid.translate([-size, -size / 4, 0])
