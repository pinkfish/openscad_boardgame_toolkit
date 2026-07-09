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

# LibFile: tests/test_slipover_path_box.py
#    Numeric/mock tests for slipover_path_box.py's plain-Python pieces:
#    FingerHoleWallSegmentCutout()'s doesn't-qualify (returns None) logic and the
#    argument-validation asserts (both fire before any geometry gets built, so they're checkable
#    under the mock). Everything else builds real geometry via native primitives, real BOSL2
#    (osuse()), pysolidfive, or the bosl2/ port; that side is covered by
#    tests/test_slipover_path_box_render.py's golden-image renders instead.
#
# FileGroup: slipover_path_box

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before slipover_path_box)

from base_bgtk import CatchType  # noqa: E402
import slipover_path_box  # noqa: E402


class TestFingerHoleWallSegmentCutoutDisqualification(unittest.TestCase):
    """Only the returns-None (segment doesn't qualify) branches -- the qualifying branch builds
    real FingerHoleWall geometry, which the numeric mock can't stand in for; that's covered by
    the render tests instead."""

    def test_too_short_a_segment_returns_none(self) -> None:
        # Needs split_length > radius * 3; 20 <= 7 * 3, so no hole.
        seg = slipover_path_box.FingerHoleWallSegmentCutout(
            path=[[0, 0], [20, 0]], height=5, radius=7, depth=6, finger_catch=CatchType.ALL
        )
        self.assertIsNone(seg)

    def test_long_catch_skips_vertical_segment(self) -> None:
        # CatchType.LONG only qualifies (near-)horizontal segments (vec_m very large).
        seg = slipover_path_box.FingerHoleWallSegmentCutout(
            path=[[0, 0], [0, 100]], height=5, radius=7, depth=6, finger_catch=CatchType.LONG
        )
        self.assertIsNone(seg)

    def test_short_catch_skips_horizontal_segment(self) -> None:
        # CatchType.SHORT only qualifies (near-)vertical segments (vec_m very small).
        seg = slipover_path_box.FingerHoleWallSegmentCutout(
            path=[[0, 0], [100, 0]], height=5, radius=7, depth=6, finger_catch=CatchType.SHORT
        )
        self.assertIsNone(seg)

    def test_diagonal_segment_qualifies_for_neither_axis_catch(self) -> None:
        for catch in (CatchType.LONG, CatchType.SHORT):
            seg = slipover_path_box.FingerHoleWallSegmentCutout(
                path=[[0, 0], [100, 100]], height=5, radius=7, depth=6, finger_catch=catch
            )
            self.assertIsNone(seg, msg=f"diagonal must not qualify for {catch}")

    def test_rejects_multi_segment_path(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_path_box.FingerHoleWallSegmentCutout(
                path=[[0, 0], [50, 0], [50, 50]], height=5, radius=7, depth=6, finger_catch=CatchType.ALL
            )


class TestArgumentValidation(unittest.TestCase):
    def test_box_rejects_short_path(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_path_box.MakePathBoxWithSlipoverLid(path=[[0, 0], [50, 0]], height=10)

    def test_box_rejects_nonpositive_height(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_path_box.MakePathBoxWithSlipoverLid(path=[[0, 0], [50, 0], [50, 50]], height=0)

    def test_lid_rejects_short_path(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_path_box.SlipoverPathBoxLid(path=[[0, 0], [50, 0]], height=10)

    def test_lid_rejects_nonpositive_height(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_path_box.SlipoverPathBoxLid(path=[[0, 0], [50, 0], [50, 50]], height=-1)


if __name__ == "__main__":
    unittest.main()
