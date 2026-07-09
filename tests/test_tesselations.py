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

# LibFile: tests/test_tesselations.py
#    Numeric/mock tests for tesselations.py's pure path-math helpers: the edge scalers, the
#    side-line/polygon distortion machinery (point-list in, point-list out), and the leaf
#    outline path builder. The geometry-producing tesselation functions are covered
#    exhaustively by tests/test_tesselations_render.py's golden-image renders instead.
#
# FileGroup: tesselations

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before tesselations)

import tesselations  # noqa: E402
from tesselations import (  # noqa: E402
    TESSELATION_LINE_FLIPPED,
    TESSELATION_LINE_NORMAL,
    TESSELATION_LINE_REVERSE,
)


class TestEdgeScalers(unittest.TestCase):
    def test_hexagonal_edge_scales_both_axes(self) -> None:
        pts = [[-0.5, 0.0], [0.0, 0.2], [0.5, 0.0]]
        out = tesselations.HexagonalTesselationGenerateEdge(pts, side_length=10)
        self.assertEqual(out, [[-5.0, 0.0], [0.0, 2.0], [5.0, 0.0]])

    def test_square_edge_scales_both_axes(self) -> None:
        pts = [[-0.5, 0.1], [0.5, -0.1]]
        out = tesselations.SquareTesselationGenerateEdge(pts, side_length=4)
        self.assertEqual(out, [[-2.0, 0.4], [2.0, -0.4]])


class TestTesselationSideLine(unittest.TestCase):
    SIDE = [[0.0, 0.0], [0.5, 0.2], [1.0, 0.0]]

    def test_normal_maps_side_onto_segment(self) -> None:
        out = tesselations.TesselationSideLine(path=[[0, 0], [10, 0]], side=self.SIDE, flip=TESSELATION_LINE_NORMAL)
        self.assertAlmostEqual(out[0][0], 0.0, places=9)
        self.assertAlmostEqual(out[0][1], 0.0, places=9)
        self.assertAlmostEqual(out[-1][0], 10.0, places=9)
        self.assertAlmostEqual(out[-1][1], 0.0, places=9)
        self.assertAlmostEqual(out[1][0], 5.0, places=9, msg="midpoint lands mid-segment")
        self.assertAlmostEqual(out[1][1], 2.0, places=9, msg="profile bump scaled by segment length")

    def test_flipped_mirrors_the_bump(self) -> None:
        out = tesselations.TesselationSideLine(path=[[0, 0], [10, 0]], side=self.SIDE, flip=TESSELATION_LINE_FLIPPED)
        self.assertAlmostEqual(out[1][1], -2.0, places=9)

    def test_reverse_runs_the_profile_backwards(self) -> None:
        asym = [[0.0, 0.0], [0.25, 0.2], [1.0, 0.0]]
        normal = tesselations.TesselationSideLine(path=[[0, 0], [10, 0]], side=asym, flip=TESSELATION_LINE_NORMAL)
        reverse = tesselations.TesselationSideLine(path=[[0, 0], [10, 0]], side=asym, flip=TESSELATION_LINE_REVERSE)
        self.assertAlmostEqual(normal[1][0], 2.5, places=9)
        self.assertAlmostEqual(reverse[1][0], 7.5, places=9, msg="bump mirrored to the other end")

    def test_rotated_segment(self) -> None:
        # Along a vertical segment the bump points in -x (90-degree rotation of +y).
        out = tesselations.TesselationSideLine(path=[[0, 0], [0, 10]], side=self.SIDE, flip=TESSELATION_LINE_NORMAL)
        self.assertAlmostEqual(out[1][0], -2.0, places=9)
        self.assertAlmostEqual(out[1][1], 5.0, places=9)

    def test_rejects_bad_arguments(self) -> None:
        with self.assertRaises(AssertionError):
            tesselations.TesselationSideLine(path=[[0, 0]], side=self.SIDE)
        with self.assertRaises(AssertionError):
            tesselations.TesselationSideLine(path=[[0, 0], [10, 0]], side=[[0, 0]])


class TestTesselationPolygon(unittest.TestCase):
    def test_square_with_flat_profiles_reproduces_square(self) -> None:
        flat = [[0.0, 0.0], [1.0, 0.0]]
        path = [[0, 0], [10, 0], [10, 10], [0, 10]]
        out = tesselations.TesselationPolygon(
            path=path, side_indexes=[0, 0, 0, 0], sides=[flat], flips=[TESSELATION_LINE_NORMAL] * 4
        )
        for corner in path:
            self.assertIn([float(corner[0]), float(corner[1])], [[round(p[0], 9), round(p[1], 9)] for p in out])

    def test_rejects_mismatched_lengths(self) -> None:
        with self.assertRaises(AssertionError):
            tesselations.TesselationPolygon(
                path=[[0, 0], [10, 0], [10, 10]], side_indexes=[0], sides=[[[0, 0], [1, 0]]], flips=[0]
            )


class TestLeafOutlinePathBuilder(unittest.TestCase):
    def test_polygon_is_closed_and_symmetric(self) -> None:
        section = 5.0
        section_height = section * math.sqrt(3) / 2
        pts = tesselations.TesselationLeafOutlineMakePolygon(section_height=section_height, section=section)
        self.assertGreaterEqual(len(pts), 6)
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(max(ys), -min(ys), places=6, msg="leaf outline symmetric about y=0")


if __name__ == "__main__":
    unittest.main()
