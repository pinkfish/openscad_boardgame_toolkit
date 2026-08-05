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

# LibFile: tests/test_no_lid.py
#    Numeric/mock tests for no_lid.py's plain-Python pieces: SortExtraFloors() ordering,
#    FingerHoleWallSegment()'s doesn't-qualify (returns None) logic, and the STACKABLE_TYPE_*
#    constants. Complements tests/test_no_lid_render.py (which renders the actual
#    solid-producing functions with the real PythonSCAD binary): everything else in no_lid.py
#    builds real geometry via native primitives, real BOSL2 (osuse()), or the pybosl2/ port, none
#    of which the numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand in
#    for. FingerHoleWallSegment's qualifying branch builds a FingerHoleWall solid, so only its
#    None-returning disqualification paths are checked here -- the geometry side is covered by
#    the render tests.
#
# FileGroup: no_lid

from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))


import no_lid  # noqa: E402


def _floor(height: float) -> types.SimpleNamespace:
    return types.SimpleNamespace(floor_height=height)


class TestSortExtraFloors(unittest.TestCase):
    def test_empty_list(self) -> None:
        self.assertEqual(no_lid.SortExtraFloors([]), [])

    def test_sorts_by_floor_height(self) -> None:
        floors = [_floor(5.0), _floor(1.0), _floor(3.0), _floor(2.0)]
        result = no_lid.SortExtraFloors(floors)
        self.assertEqual([f.floor_height for f in result], [1.0, 2.0, 3.0, 5.0])

    def test_preserves_duplicates(self) -> None:
        floors = [_floor(2.0), _floor(1.0), _floor(2.0)]
        result = no_lid.SortExtraFloors(floors)
        self.assertEqual([f.floor_height for f in result], [1.0, 2.0, 2.0])

    def test_already_sorted_is_stable_length(self) -> None:
        floors = [_floor(h) for h in (1.0, 2.0, 3.0)]
        result = no_lid.SortExtraFloors(floors)
        self.assertEqual(len(result), 3)
        self.assertEqual([f.floor_height for f in result], [1.0, 2.0, 3.0])


class TestFingerHoleWallSegmentDisqualification(unittest.TestCase):
    """Only the returns-None (segment doesn't qualify) branches -- the qualifying branch builds
    real FingerHoleWall geometry, which the numeric mock can't stand in for; that's covered by
    the render tests instead."""

    def test_too_short_a_segment_returns_none(self) -> None:
        # Needs split_length > finger_hole_size * 2.5; 20 <= 10 * 2.5, so no hole.
        seg = no_lid.FingerHoleWallSegment(
            path=[[0, 0], [20, 0]], finger_hole_size=10, finger_hole_height=5, height=20,
            wall_thickness=2, make_finger_x=True, make_finger_y=True,
        )
        self.assertIsNone(seg)

    def test_x_axis_segment_with_finger_x_disabled_returns_none(self) -> None:
        # A segment running along X gets a +-90-degree normal -> gated by make_finger_x.
        seg = no_lid.FingerHoleWallSegment(
            path=[[0, 0], [100, 0]], finger_hole_size=10, finger_hole_height=5, height=20,
            wall_thickness=2, make_finger_x=False, make_finger_y=True,
        )
        self.assertIsNone(seg)

    def test_y_axis_segment_with_finger_y_disabled_returns_none(self) -> None:
        # A segment running along Y gets a 0-degree normal -> gated by make_finger_y.
        seg = no_lid.FingerHoleWallSegment(
            path=[[0, 0], [0, 100]], finger_hole_size=10, finger_hole_height=5, height=20,
            wall_thickness=2, make_finger_x=True, make_finger_y=False,
        )
        self.assertIsNone(seg)

    def test_rejects_multi_segment_path(self) -> None:
        with self.assertRaises(AssertionError):
            no_lid.FingerHoleWallSegment(
                path=[[0, 0], [50, 0], [50, 50]], finger_hole_size=10, finger_hole_height=5,
                height=20, wall_thickness=2,
            )


class TestStackableConstants(unittest.TestCase):
    def test_values_are_distinct(self) -> None:
        self.assertEqual(no_lid.STACKABLE_TYPE_NONE, 0)
        self.assertEqual(no_lid.STACKABLE_TYPE_INSIDE, 1)
        self.assertEqual(no_lid.STACKABLE_TYPE_OUTSIDE, 2)

    def test_none_is_falsy_inside_and_outside_truthy(self) -> None:
        # MakePathBoxWithNoLid branches on bare `if stackable:` -- NONE must stay falsy.
        self.assertFalse(no_lid.STACKABLE_TYPE_NONE)
        self.assertTrue(no_lid.STACKABLE_TYPE_INSIDE)
        self.assertTrue(no_lid.STACKABLE_TYPE_OUTSIDE)


if __name__ == "__main__":
    unittest.main()
