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

"""pybosl2.regions.Path2D / Region -- the object API over the 2-D point maths.

The load-bearing property is that both subclass list (the same trick as base_bgtk.Vec3): the
toolkit passes raw point lists to native polygon()/region()/union() everywhere, so these must
remain indistinguishable from plain lists or they would be a breaking change rather than a
drop-in. Most of these tests pin exactly that.
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import venv_path  # noqa: F401,E402  -- pin pybosl2 to the project venv
from pybosl2 import Path2D, Region  # noqa: E402

# BOSL2 spells offset's radius "r"; pybosl2 0.6.x removed the short kwargs and made the
# engine an INSTANCE method on Path2D. Adapt here so the call sites keep BOSL2's spelling.
_BOSL2_KW = {"r": "radius", "d": "diameter", "n": "count", "_fn": "fn"}


def offset(path, closed=True, **kw):
    """BOSL2's ``offset(path, r=...)`` over pybosl2's Path2D engine."""
    kwargs = {_BOSL2_KW.get(k, k): v for k, v in kw.items()}
    closed = kwargs.pop("closed", closed)
    return Path2D(path, closed=closed)._offset(**kwargs)

SQUARE = [[0, 0], [80, 0], [80, 60], [0, 60]]


class TestPathBehavesLikeAPointList(unittest.TestCase):
    """Path2D is no longer a ``list`` SUBCLASS (0.6.7) -- it indexes, iterates and
    measures like one, and ``.to_list`` is the plain-list view."""

    def test_equals_a_plain_list(self):
        self.assertEqual(Path2D(SQUARE).to_list, [[float(x), float(y)] for x, y in SQUARE])

    def test_indexes_and_iterates(self):
        p = Path2D(SQUARE)
        self.assertEqual(len(p), 4)
        self.assertEqual(p[1], [80.0, 0.0])
        self.assertEqual([pt[0] for pt in p], [0.0, 80.0, 80.0, 0.0])

    def test_points_are_plain_floats(self):
        # numpy scalars are rejected/corrupted at the native polygon()/FFI boundary
        for pt in Path2D(np.asarray(SQUARE, dtype=float)):
            for v in pt:
                self.assertIsInstance(v, float)

    def test_rejects_non_xy_points(self):
        with self.assertRaises(AssertionError):
            Path2D([[0, 0, 0], [1, 1, 1]])

    def test_empty_path(self):
        self.assertEqual(len(Path2D()), 0)


class TestPathMethods(unittest.TestCase):
    def test_offset_matches_the_free_function(self):
        self.assertEqual(Path2D(SQUARE).offset(radius=-2).to_list, offset(SQUARE, r=-2))

    def test_offset_returns_a_path(self):
        self.assertIsInstance(Path2D(SQUARE).offset(radius=-2), Path2D)

    def test_chaining(self):
        out = Path2D(SQUARE).offset(radius=-2).round_corners(radius=1)
        self.assertIsInstance(out, Path2D)
        self.assertGreater(len(out), 4)  # corners got rounded

    def test_does_not_mutate(self):
        p = Path2D(SQUARE)
        p.offset(radius=-2)
        self.assertEqual(p.to_list, [[float(x), float(y)] for x, y in SQUARE])

    def test_measurements(self):
        p = Path2D(SQUARE)
        self.assertAlmostEqual(p.bounds().width, 80)
        self.assertAlmostEqual(p.bounds().length, 60)
        self.assertAlmostEqual(p.area(), 4800)
        self.assertFalse(p.is_clockwise())
        self.assertTrue(Path2D(list(reversed(SQUARE))).is_clockwise())

    def test_contains(self):
        p = Path2D(SQUARE)
        self.assertTrue(p.contains([40, 30]))
        self.assertFalse(p.contains([-5, 30]))

    def test_bounds(self):
        _b = Path2D(SQUARE).bounds()
        np.testing.assert_allclose(
            [[_b.min_x, _b.min_y], [_b.max_x, _b.max_y]], [[0, 0], [80, 60]])

    def test_transforms_return_paths(self):
        p = Path2D(SQUARE)
        self.assertIsInstance(p.translate([1, 2]), Path2D)
        self.assertIsInstance(p.rotate(90), Path2D)
        self.assertIsInstance(p.mirror([1, 0]), Path2D)
        np.testing.assert_allclose(p.translate([1, 2])[0], [1, 2])

    def test_reversed_flips_winding(self):
        self.assertTrue(Path2D(SQUARE).reverse().is_clockwise())

    def test_array_is_numpy(self):
        arr = Path2D(SQUARE).array
        self.assertIsInstance(arr, np.ndarray)
        self.assertEqual(arr.shape, (4, 2))


class TestRegion(unittest.TestCase):
    def test_indexes_and_iterates_like_a_list_of_paths(self):
        """Region stopped being a ``list`` SUBCLASS in 0.6.7; it still indexes and
        iterates, and each element is a Path2D rather than a bare point list."""
        r = Region.with_holes(SQUARE, offset(SQUARE, r=-2))
        self.assertEqual(len(r), 2)
        self.assertIsInstance(r[0], Path2D)
        self.assertEqual(r[0].to_list, [[float(x), float(y)] for x, y in SQUARE])
        self.assertEqual([len(path) for path in r], [4, 4])

    def test_coerces_paths(self):
        r = Region([SQUARE])
        self.assertIsInstance(r[0], Path2D)

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
        r = Path2D(SQUARE).to_region()
        self.assertIsInstance(r, Region)
        self.assertEqual(len(r), 1)

    def test_offset_applies_to_every_path(self):
        r = Region.with_holes(SQUARE, offset(SQUARE, r=-2)).offset(delta=-1)
        self.assertIsInstance(r, Region)
        self.assertEqual(len(r), 2)

    def test_bounds_spans_all_paths(self):
        # NB: Region.bounds() gives a plain [[min], [max]] array, while Path2D.bounds()
        # gives a Bounds2D object -- they are not the same shape of value in 0.6.7.
        np.testing.assert_allclose(
            Region.with_holes(SQUARE, offset(SQUARE, r=-2)).bounds(), [[0, 0], [80, 60]])

    def test_empty_region_has_an_empty_outline(self):
        """0.6.7 returns an EMPTY path here; it used to assert. Either is defensible --
        this pins which one, so a silent flip back is caught."""
        self.assertEqual(len(Region().outline), 0)


class TestDifferenceWithOffsetReturnsRegion(unittest.TestCase):
    """The pts= form produces exactly outline+hole, so it now says so in its type."""

    def test_returns_a_region(self):
        from base_bgtk import DifferenceWithOffset

        out = DifferenceWithOffset(offset=-2, outer_offset=0, pts=SQUARE)
        self.assertIsInstance(out, Region)
        self.assertEqual(len(out.holes), 1)

    def test_solid_form_returns_a_path(self):
        from base_bgtk import DifferenceWithOffset

        self.assertIsInstance(DifferenceWithOffset(offset=0, pts=SQUARE), Path2D)


if __name__ == "__main__":
    unittest.main()
