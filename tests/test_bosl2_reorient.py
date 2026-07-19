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
    dict(r=10, angle=90, wedge=True),
    dict(r=10, angle=[30, 90]),
    dict(n=7, width=10, thickness=3),
    dict(n=6, cp=[0, 0], points=[[10, 0], [0, 10]]),
    dict(n=6, cp=[0, 0], points=[[10, 0], [0, 10]], long=True),
    dict(corner=[[0, 10], [0, 0], [10, 0]], r=3),
]

CATENARY_CASES = [
    dict(width=80, droop=30, n=20),
    dict(width=80, angle=45, n=20),
    dict(width=50, droop=-15, n=15),
]

HELIX_CASES = [
    dict(turns=2.5, h=100, r=30),
    dict(h=0, r1=50, r2=25, l=0, turns=4),
    dict(turns=-2, h=60, r=20),
]

TURTLE_CASES = [
    ["move", 40, "left", 90, "move", 40, "left", 90, "move", 40, "left", 90, "move", 40],
    ["repeat", 4, ["move", 40, "left", 90]],
    ["move", 40, "arcleft", 8, "move", 40, "arcleft", 8, "move", 40, "arcleft", 8, "move", 40, "arcleft", 8],
    ["move", 20, "arcrightto", 10, -90],
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


class TestCatenaryMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from bosl2.drawing import catenary
        for kwargs, case in zip(CATENARY_CASES, TRUTH["catenary"]):
            with self.subTest(kw=case["kw"]):
                got = catenary(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestHelixMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from bosl2.drawing import helix
        for kwargs, case in zip(HELIX_CASES, TRUTH["helix"]):
            with self.subTest(kw=case["kw"]):
                got = helix(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestTurtleMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from bosl2.drawing import turtle
        for cmds, case in zip(TURTLE_CASES, TRUTH["turtle"]):
            with self.subTest(kw=case["kw"]):
                got = turtle(cmds)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestDistributorsMatchBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from bosl2 import distributors as D
        dpath = [[0, 0], [20, 0], [20, 20], [40, 20]]
        calls = {
            "move_copies": lambda: D.move_copies([[0, 0, 0], [5, 5, 5], [10, 0, -3]]),
            "xcopies_n": lambda: D.xcopies(20, n=3),
            "ycopies_l": lambda: D.ycopies(l=50, n=4),
            "zcopies_list": lambda: D.zcopies([1, 3, 7]),
            "line_spacing": lambda: D.line_copies(spacing=10, n=5),
            "line_vec_l": lambda: D.line_copies(l=[10, 20, 0], n=4),
            "grid_nspacing": lambda: D.grid_copies(n=[3, 2], spacing=10),
            "grid_stagger": lambda: D.grid_copies(spacing=8, n=[4, 3], stagger=True),
            "rot_n6": lambda: D.rot_copies(n=6),
            "xrot_ring": lambda: D.xrot_copies(n=5, r=10),
            "yrot_ring": lambda: D.yrot_copies(n=4, r=12),
            "zrot_list": lambda: D.zrot_copies([0, 30, 60], r=8),
            "arc_r": lambda: D.arc_copies(n=6, r=20),
            "arc_ellipse": lambda: D.arc_copies(n=5, rx=20, ry=10, sa=30, ea=200),
            "sphere": lambda: D.sphere_copies(n=8, r=30, cone_ang=90),
            "mirror_off": lambda: D.mirror_copy([1, 1, 0], offset=2),
            "xflip": lambda: D.xflip_copy(offset=3, x=1),
            "path_n": lambda: D.path_copies(dpath, n=5),
        }
        for case in TRUTH["distrib"]:
            with self.subTest(kw=case["kw"]):
                got = np.array([np.asarray(m) for m in calls[case["kw"]]()], dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "matrix count must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


if __name__ == "__main__":
    unittest.main()
