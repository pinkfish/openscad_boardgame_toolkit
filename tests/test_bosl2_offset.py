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

"""Pin pybosl2.paths.offset() to the real BOSL2's offset().

tests/bosl2_offset_truth.json is ground truth captured from the actual BOSL2 through osuse():
5 path shapes (square, concave, hexagon, a 6-point box outline, triangle) x 9 variants
(r inward/outward, delta inward/outward, chamfered). This numpy implementation replaced the
osuse() call, so the fixture is what proves it exact.

Regenerate with tests/generate_bosl2_offset_truth.py (needs the real app + patched BOSL2).
"""

import json
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pysolidfive", "tests"))
import mock_libfive  # noqa: F401,E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pybosl2 import Path2D  # noqa: E402

# offset() now lives on Path2D as the private static engine behind Path2D.offset().
offset = Path2D._offset

TRUTH = json.load(open(os.path.join(os.path.dirname(__file__), "bosl2_offset_truth.json")))


class TestOffsetMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        self.assertEqual(len(TRUTH["cases"]), 45)
        for case in TRUTH["cases"]:
            with self.subTest(path=case["path"], case=case["case"]):
                self.assertNotIn("err", case, "fixture case failed to capture")
                got = offset(TRUTH["paths"][case["path"]], **case["kw"])
                self.assertEqual(len(got), len(case["res"]),
                                 f"point count must match BOSL2 for {case['path']}/{case['case']}")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestOffsetContract(unittest.TestCase):
    def test_returns_plain_floats(self):
        # points cross into polygon()/native calls, which reject numpy scalars
        out = offset([[0, 0], [10, 0], [10, 10], [0, 10]], r=-1)
        self.assertIsInstance(out, list)
        self.assertIsInstance(out[0], list)
        self.assertIsInstance(out[0][0], float)

    def test_zero_offset_is_identity(self):
        square = [[0, 0], [10, 0], [10, 10], [0, 10]]
        self.assertEqual(offset(square, r=0), [[float(x), float(y)] for x, y in square])

    def test_requires_exactly_one_of_r_or_delta(self):
        square = [[0, 0], [10, 0], [10, 10], [0, 10]]
        with self.assertRaises(AssertionError):
            offset(square)
        with self.assertRaises(AssertionError):
            offset(square, r=1, delta=1)

    def test_handles_clockwise_winding(self):
        # same square, reversed: shrinking must still shrink
        ccw = [[0, 0], [10, 0], [10, 10], [0, 10]]
        cw = list(reversed(ccw))
        a = np.array(offset(ccw, r=-1))
        b = np.array(offset(cw, r=-1))
        self.assertAlmostEqual(a[:, 0].min(), 1.0)
        self.assertAlmostEqual(b[:, 0].min(), 1.0)
        self.assertAlmostEqual(a[:, 0].max(), 9.0)
        self.assertAlmostEqual(b[:, 0].max(), 9.0)


if __name__ == "__main__":
    unittest.main()
