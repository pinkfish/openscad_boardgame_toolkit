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

"""Pin bosl2.transforms.reorient/apply and bosl2.shapes2d.arc to the real BOSL2's output.

tests/bosl2_truth.json holds ground truth captured from the actual BOSL2 scad library through
osuse() (every anchor/orient/spin/size combination the toolkit uses). These functions replaced
the osuse() FFI calls, so the fixture is what proves the pure-Python versions are exact.

To regenerate the fixture (needs the real app + patched BOSL2), see
tests/generate_bosl2_truth.py.
"""

import json
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pysolidfive", "tests"))
import mock_libfive  # noqa: F401,E402  (installs numeric stand-ins; must precede toolkit imports)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from bosl2.shapes2d import arc  # noqa: E402
from bosl2.transforms import apply, reorient  # noqa: E402

TRUTH = json.load(open(os.path.join(os.path.dirname(__file__), "bosl2_truth.json")))

ANCHORS = {"CENTER": (0, 0, 0), "BOTTOM": (0, 0, -1), "TOP": (0, 0, 1),
           "BFL": (-1, -1, -1), "TRB": (1, 1, 1), "LEFT": (-1, 0, 0)}
ORIENTS = {"TOP": (0, 0, 1), "BOTTOM": (0, 0, -1), "LEFT": (-1, 0, 0),
           "RIGHT": (1, 0, 0), "FRONT": (0, -1, 0), "BACK": (0, 1, 0)}

ARC_CASES = [
    dict(r=16, start=0, angle=60),
    dict(r=5, start=30, angle=90),
    dict(n=8, points=[[-0.5, 0], [0, 0.3], [0.5, 0]]),
    dict(n=12, points=[[-1, 0], [0, 1], [1, 0]]),
]


class TestReorientMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        self.assertEqual(len(TRUTH["reorient"]), 288)
        for case in TRUTH["reorient"]:
            with self.subTest(anchor=case["anchor"], orient=case["orient"],
                              spin=case["spin"], size=case["size"]):
                got = reorient(anchor=ANCHORS[case["anchor"]], spin=case["spin"],
                               orient=ORIENTS[case["orient"]], size=case["size"])
                np.testing.assert_allclose(got, np.array(case["m"]), atol=1e-9)

    def test_defaults_are_identity(self):
        np.testing.assert_allclose(reorient(), np.eye(4), atol=1e-12)

    def test_returns_plain_4x4_lists(self):
        # reorient() feeds the native multmatrix(), which rejects ndarrays with
        # "Error during parsing multmatrix(object, vec16)" -- so the result must be plain
        # nested Python floats, not numpy.
        m = reorient(anchor=(0, 0, -1), size=[2, 4, 6])
        self.assertIsInstance(m, list)
        self.assertEqual(len(m), 4)
        for row in m:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), 4)
            for value in row:
                self.assertIsInstance(value, float)


class TestApplyMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        for case in TRUTH["apply"]:
            with self.subTest(pts=case["pts"]):
                np.testing.assert_allclose(apply(case["m"], case["pts"]),
                                           np.array(case["res"]), atol=1e-9)

    def test_identity_roundtrip(self):
        pts = [[1, 2, 3], [-4, 5, -6]]
        np.testing.assert_allclose(apply(np.eye(4), pts), pts, atol=1e-12)

    def test_single_point(self):
        m = np.eye(4)
        m[:3, 3] = [1, 2, 3]
        np.testing.assert_allclose(apply(m, [0, 0, 0]), [1, 2, 3], atol=1e-12)

    def test_returns_plain_lists(self):
        # the native FFI rejects ndarrays, so apply() must hand back plain floats
        out = apply(np.eye(4), [[1, 2, 3]])
        self.assertIsInstance(out, list)
        self.assertIsInstance(out[0], list)
        self.assertIsInstance(out[0][0], float)


class TestArcMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        for kwargs, case in zip(ARC_CASES, TRUTH["arc"]):
            with self.subTest(kw=case["kw"]):
                got = arc(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-9)

    def test_point_count_follows_fn(self):
        # explicit $fn wins over the $fa/$fs rules
        self.assertEqual(len(arc(r=10, angle=90, _fn=32)), 32 // 4 + 1)

    def test_three_point_arc_hits_endpoints(self):
        pts = arc(n=9, points=[[-1, 0], [0, 1], [1, 0]])
        np.testing.assert_allclose(pts[0], [-1, 0], atol=1e-9)
        np.testing.assert_allclose(pts[-1], [1, 0], atol=1e-9)


if __name__ == "__main__":
    unittest.main()
