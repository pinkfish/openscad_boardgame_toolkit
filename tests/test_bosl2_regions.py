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

"""bosl2.regions.Path / Region -- the object API over the 2-D point maths.

The load-bearing property is that both subclass list (the same trick as base_bgtk.Vec3): the
toolkit passes raw point lists to native polygon()/region()/union() everywhere, so these must
remain indistinguishable from plain lists or they would be a breaking change rather than a
drop-in. Most of these tests pin exactly that.
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pysolidfive", "tests"))
import mock_libfive  # noqa: F401,E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from bosl2.regions import Path, Region  # noqa: E402

# offset() now lives on Path as the private static engine behind Path.offset().
offset = Path._offset

SQUARE = [[0, 0], [80, 0], [80, 60], [0, 60]]


class TestPathIsADropInList(unittest.TestCase):
    def test_equals_a_plain_list(self):
        self.assertEqual(Path(SQUARE), [[float(x), float(y)] for x, y in SQUARE])

    def test_indexes_and_iterates(self):
        p = Path(SQUARE)
        self.assertEqual(len(p), 4)
        self.assertEqual(p[1], [80.0, 0.0])
        self.assertEqual([pt[0] for pt in p], [0.0, 80.0, 80.0, 0.0])

    def test_points_are_plain_floats(self):
        # numpy scalars are rejected/corrupted at the native polygon()/FFI boundary
        for pt in Path(np.asarray(SQUARE, dtype=float)):
            for v in pt:
                self.assertIsInstance(v, float)

    def test_rejects_non_xy_points(self):
        with self.assertRaises(AssertionError):
            Path([[0, 0, 0], [1, 1, 1]])

    def test_empty_path(self):
        self.assertEqual(len(Path()), 0)


class TestPathMethods(unittest.TestCase):
    def test_offset_matches_the_free_function(self):
        self.assertEqual(Path(SQUARE).offset(r=-2), offset(SQUARE, r=-2))

    def test_offset_returns_a_path(self):
        self.assertIsInstance(Path(SQUARE).offset(r=-2), Path)

    def test_chaining(self):
        out = Path(SQUARE).offset(r=-2).round_corners(radius=1)
        self.assertIsInstance(out, Path)
        self.assertGreater(len(out), 4)  # corners got rounded

    def test_does_not_mutate(self):
        p = Path(SQUARE)
        p.offset(r=-2)
        self.assertEqual(p, [[float(x), float(y)] for x, y in SQUARE])

    def test_measurements(self):
        p = Path(SQUARE)
        self.assertAlmostEqual(p.width, 80)
        self.assertAlmostEqual(p.length_y, 60)
        self.assertAlmostEqual(p.area(), 4800)
        self.assertFalse(p.is_clockwise())
        self.assertTrue(Path(list(reversed(SQUARE))).is_clockwise())

    def test_contains(self):
        p = Path(SQUARE)
        self.assertTrue(p.contains([40, 30]))
        self.assertFalse(p.contains([-5, 30]))

    def test_bounds(self):
        np.testing.assert_allclose(Path(SQUARE).bounds(), [[0, 0], [80, 60]])

    def test_transforms_return_paths(self):
        p = Path(SQUARE)
        self.assertIsInstance(p.translate([1, 2]), Path)
        self.assertIsInstance(p.rotate(90), Path)
        self.assertIsInstance(p.mirror([1, 0]), Path)
        np.testing.assert_allclose(p.translate([1, 2])[0], [1, 2])

    def test_reversed_flips_winding(self):
        self.assertTrue(Path(SQUARE).reversed_path().is_clockwise())

    def test_array_is_numpy(self):
        arr = Path(SQUARE).array
        self.assertIsInstance(arr, np.ndarray)
        self.assertEqual(arr.shape, (4, 2))


class TestRegion(unittest.TestCase):
    def test_is_a_drop_in_list_of_paths(self):
        r = Region.with_holes(SQUARE, offset(SQUARE, r=-2))
        self.assertIsInstance(r, list)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], [[float(x), float(y)] for x, y in SQUARE])
        self.assertEqual(r, [offset(SQUARE, r=0) if False else r[0], r[1]])  # plain-list compare

    def test_coerces_paths(self):
        r = Region([SQUARE])
        self.assertIsInstance(r[0], Path)

    def test_single_outline_from_flat_points(self):
        # a bare point list is one outline, not a list of paths
        r = Region(SQUARE)
        self.assertEqual(len(r), 1)
        self.assertEqual(len(r.outline), 4)

    def test_outline_and_holes(self):
        r = Region.with_holes(SQUARE, offset(SQUARE, r=-2))
        self.assertEqual(len(r.outline), 4)
        self.assertEqual(len(r.holes), 1)
        # the hole sits inside the outline
        self.assertLess(r.holes[0].area(), r.outline.area())

    def test_path_to_region(self):
        r = Path(SQUARE).to_region()
        self.assertIsInstance(r, Region)
        self.assertEqual(len(r), 1)

    def test_offset_applies_to_every_path(self):
        r = Region.with_holes(SQUARE, offset(SQUARE, r=-2)).offset(delta=-1)
        self.assertIsInstance(r, Region)
        self.assertEqual(len(r), 2)

    def test_bounds_spans_all_paths(self):
        np.testing.assert_allclose(Region.with_holes(SQUARE, offset(SQUARE, r=-2)).bounds(),
                                   [[0, 0], [80, 60]])

    def test_empty_region_has_no_outline(self):
        with self.assertRaises(AssertionError):
            Region().outline


class TestDifferenceWithOffsetReturnsRegion(unittest.TestCase):
    """The pts= form produces exactly outline+hole, so it now says so in its type."""

    def test_returns_a_region(self):
        from base_bgtk import DifferenceWithOffset

        out = DifferenceWithOffset(offset=-2, outer_offset=0, pts=SQUARE)
        self.assertIsInstance(out, Region)
        self.assertEqual(len(out.holes), 1)

    def test_solid_form_returns_a_path(self):
        from base_bgtk import DifferenceWithOffset

        self.assertIsInstance(DifferenceWithOffset(offset=0, pts=SQUARE), Path)


if __name__ == "__main__":
    unittest.main()
