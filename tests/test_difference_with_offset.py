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

"""DifferenceWithOffset's pts= form, pinned to the real BOSL2.

The pts= form used to be `_bosl2.difference(_bosl2.offset(p, outer), _bosl2.offset(p, inner))`.
Those two offsets are CONCENTRIC -- the inner is always strictly inside the outer -- so the
difference needs no polygon clipping: it is just "outline plus hole", which is exactly how a
BOSL2 region is represented. tests/bosl2_dwo_truth.json is ground truth from the real BOSL2
proving `difference(outer, inner)` is literally `[outer, inner]`, same order, same winding, for
both the delta and r variants.

That is what lets this be pure numpy. If a future caller ever passes a path where the "inner"
offset is NOT strictly inside the outer (a self-intersecting or very large offset), this
assumption breaks and real clipping would be needed -- see test_assumption_is_concentric_only.
"""

import json
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base_bgtk import DifferenceWithOffset, DifferenceWithOffsetRounded  # noqa: E402

TRUTH = json.load(open(os.path.join(os.path.dirname(__file__), "bosl2_dwo_truth.json")))


class TestMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        self.assertEqual(len(TRUTH["cases"]), 18)
        for case in TRUTH["cases"]:
            with self.subTest(path=case["path"], mode=case["mode"],
                              outer=case["outer"], inner=case["inner"]):
                fn = DifferenceWithOffset if case["mode"] == "delta" else DifferenceWithOffsetRounded
                got = fn(offset=case["inner"], outer_offset=case["outer"],
                         pts=TRUTH["paths"][case["path"]])
                self.assertEqual(len(got), len(case["res"]), "region path count must match BOSL2")
                for g, e in zip(got, case["res"]):
                    np.testing.assert_allclose(np.array(g), np.array(e), atol=1e-6)

    def test_bosl2_difference_of_concentric_is_just_outer_inner(self):
        # The assumption the numpy version rests on, asserted against the captured truth:
        # BOSL2 returns [outer, inner] verbatim -- no reordering, no winding flip.
        for case in TRUTH["cases"]:
            with self.subTest(path=case["path"], mode=case["mode"]):
                self.assertEqual(len(case["res"]), 2)
                np.testing.assert_allclose(np.array(case["res"][0]), np.array(case["outer_only"]), atol=1e-9)
                np.testing.assert_allclose(np.array(case["res"][1]), np.array(case["inner_only"]), atol=1e-9)


class TestContract(unittest.TestCase):
    SQUARE = [[0, 0], [80, 0], [80, 60], [0, 60]]

    def test_offset_zero_returns_a_single_path_not_a_region(self):
        # offset == 0 means "solid, no cutout": one path, not [outer, inner]
        out = DifferenceWithOffset(offset=0, outer_offset=0, pts=self.SQUARE)
        self.assertEqual([list(p) for p in out], [[float(x), float(y)] for x, y in self.SQUARE])

    def test_region_is_outline_then_hole(self):
        out = DifferenceWithOffset(offset=-2, outer_offset=0, pts=self.SQUARE)
        self.assertEqual(len(out), 2)
        outer, hole = np.array(out[0]), np.array(out[1])
        # the hole must sit strictly inside the outline -- the concentric assumption
        self.assertGreater(outer[:, 0].max() - outer[:, 0].min(), hole[:, 0].max() - hole[:, 0].min())

    def test_children_form_is_untouched_and_native(self):
        # the children= branch never used osuse; it must still return a solid, not a region
        class _Fake:
            def offset(self, **kw):
                return self
            def __sub__(self, other):
                return "solid"
        self.assertEqual(DifferenceWithOffset(offset=-1, children=_Fake()), "solid")

    def test_returns_plain_floats(self):
        out = DifferenceWithOffset(offset=-2, pts=self.SQUARE)
        self.assertIsInstance(out[0][0][0], float)


if __name__ == "__main__":
    unittest.main()
