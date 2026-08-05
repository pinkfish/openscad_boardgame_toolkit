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

"""Pin pybosl2.transforms.reorient/apply and pybosl2.shapes2d.arc to the real BOSL2's output.

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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import venv_path  # noqa: F401,E402  -- pin pybosl2 to the project venv
from pybosl2 import arc  # noqa: E402
from pybosl2.transforms import apply, reorient  # noqa: E402

TRUTH = json.load(open(os.path.join(os.path.dirname(__file__), "bosl2_truth.json")))

ANCHORS = {"CENTER": (0, 0, 0), "BOTTOM": (0, 0, -1), "TOP": (0, 0, 1),
           "BFL": (-1, -1, -1), "TRB": (1, 1, 1), "LEFT": (-1, 0, 0)}
ORIENTS = {"TOP": (0, 0, 1), "BOTTOM": (0, 0, -1), "LEFT": (-1, 0, 0),
           "RIGHT": (1, 0, 0), "FRONT": (0, -1, 0), "BACK": (0, 1, 0)}

#: BOSL2's own kwarg spelling, matching the truth fixture these are zipped with. pybosl2
#: 0.6.x removed the short forms, so _arc() translates rather than the data being rewritten.
_ARC_KW = {"r": "radius", "n": "count", "d": "diameter", "_fn": "fn", "cp": "center"}


def _arc(**kw):
    """arc() called the way BOSL2 spells it."""
    return arc(**{_ARC_KW.get(k, k): v for k, v in kw.items()})


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
                got = _arc(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-9)

    def test_point_count_follows_fn(self):
        # explicit $fn wins over the $fa/$fs rules
        self.assertEqual(len(arc(radius=10, angle=90, fn=32)), 32 // 4 + 1)

    def test_three_point_arc_hits_endpoints(self):
        pts = arc(count=9, points=[[-1, 0], [0, 1], [1, 0]])
        np.testing.assert_allclose(pts[0], [-1, 0], atol=1e-9)
        np.testing.assert_allclose(pts[-1], [1, 0], atol=1e-9)


class TestCatenaryMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import catenary
        for kwargs, case in zip(CATENARY_CASES, TRUTH["catenary"]):
            with self.subTest(kw=case["kw"]):
                got = catenary(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestHelixMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import helix
        for kwargs, case in zip(HELIX_CASES, TRUTH["helix"]):
            with self.subTest(kw=case["kw"]):
                got = helix(**kwargs)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestTurtleMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2.drawing import turtle
        for cmds, case in zip(TURTLE_CASES, TRUTH["turtle"]):
            with self.subTest(kw=case["kw"]):
                got = turtle(cmds)
                self.assertEqual(len(got), len(case["res"]), "point count must match BOSL2")
                np.testing.assert_allclose(np.array(got), np.array(case["res"]), atol=1e-6)


class TestDistributorsMatchBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import distributors as D
        dpath = [[0, 0], [20, 0], [20, 20], [40, 20]]
        calls = {
            # move_copies has no pybosl2 equivalent (0.6.7 exposes path_copies for this).
            "path_copies": lambda: D.path_copies([[0, 0, 0], [5, 5, 5], [10, 0, -3]]),
            "xcopies_n": lambda: D.xcopies(20, num_copies=3),
            "ycopies_l": lambda: D.ycopies(length=50, num_copies=4),
            "zcopies_list": lambda: D.zcopies([1, 3, 7]),
            "line_spacing": lambda: D.line_copies(spacing=10, num_copies=5),
            "line_vec_l": lambda: D.line_copies(length=[10, 20, 0], num_copies=4),
            "grid_nspacing": lambda: D.grid_copies(num_copies=[3, 2], spacing=10),
            "grid_stagger": lambda: D.grid_copies(spacing=8, num_copies=[4, 3], stagger=True),
            "rot_n6": lambda: D.rot_copies(num_copies=6),
            "xrot_ring": lambda: D.xrot_copies(num_copies=5, radius=10),
            "yrot_ring": lambda: D.yrot_copies(num_copies=4, radius=12),
            "zrot_list": lambda: D.zrot_copies([0, 30, 60], radius=8),
            "arc_r": lambda: D.arc_copies(num_copies=6, radius=20),
            "arc_ellipse": lambda: D.arc_copies(num_copies=5, radius_x=20, radius_y=10, sa=30, ea=200),
            "sphere": lambda: D.sphere_copies(num_copies=8, r=30, cone_ang=90),
            "mirror_off": lambda: D.mirror_copy([1, 1, 0], offset=2),
            "xflip": lambda: D.xflip_copy(offset=3, x=1),
            "path_n": lambda: D.path_copies(dpath, num_copies=5),
        }
        for case in TRUTH["distrib"]:
            with self.subTest(kw=case["kw"]):
                got = np.array([np.asarray(m) for m in calls[case["kw"]]()], dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "matrix count must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


class TestColorMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2.color import hsl, hsv
        for case in TRUTH["color"]:
            with self.subTest(fn=case["fn"], args=case["args"]):
                fn = hsl if case["fn"] == "hsl" else hsv
                got = np.array(fn(*case["args"]), dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "RGB(A) length must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


class TestPartitionPathMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import partition_path
        calls = {
            "flat": lambda: partition_path(["flat"]),
            "sawtooth": lambda: partition_path(["sawtooth"]),
            "square": lambda: partition_path(["square"]),
            "triangle": lambda: partition_path(["triangle"]),
            "dovetail": lambda: partition_path(["dovetail"]),
            "hammerhead": lambda: partition_path(["hammerhead"]),
            "comb": lambda: partition_path(["comb"]),
            "finger": lambda: partition_path(["finger"]),
            "sawtooth_xflip": lambda: partition_path(["sawtooth xflip"]),
            "sawtooth_addflip": lambda: partition_path(["sawtooth addflip"]),
            "sawtooth_3x": lambda: partition_path(["sawtooth 3x"]),
            "hammerhead_yflip": lambda: partition_path(["hammerhead yflip"]),
            "square_skew": lambda: partition_path(["square skew:15"]),
            "square_pinch": lambda: partition_path(["square pinch:30"]),
            "mixed_flat": lambda: partition_path([40, "dovetail", 40]),
            "closed_y": lambda: partition_path([30, "hammerhead", 30], y=150),
        }
        for case in TRUTH["partition"]:
            with self.subTest(kw=case["kw"]):
                got = np.array(calls[case["kw"]](), dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "point count must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


class TestNurbsMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import nurbs_curve, nurbs_patch_points, nurbs_elevate_degree
        c3 = [[0, 0, 0], [10, 20, 5], [30, -10, 10], [50, 20, 0], [60, 0, 15]]
        c2 = [[0, 0], [10, 20], [30, -10], [50, 20], [60, 0]]
        patch = [[[-50, 50, 0], [-16, 50, 20], [16, 50, 20], [50, 50, 0]],
                 [[-50, 16, 20], [-16, 16, 40], [16, 16, 40], [50, 16, 20]],
                 [[-50, -16, 20], [-16, -16, 40], [16, -16, 40], [50, -16, 20]],
                 [[-50, -50, 0], [-16, -50, 20], [16, -50, 20], [50, -50, 0]]]
        calls = {
            "clamped3_ss": lambda: nurbs_curve(c3, 3, splinesteps=5),
            "clamped2_u": lambda: nurbs_curve(c2, 3, u=[0, 0.2, 0.4, 0.6, 0.8, 1]),
            "open3_ss": lambda: nurbs_curve(c3, 3, splinesteps=4, type="open"),
            "closed2_ss": lambda: nurbs_curve(c2, 2, splinesteps=4, type="closed"),
            "deg2_ss": lambda: nurbs_curve(c3, 2, splinesteps=6),
            "weighted_u": lambda: nurbs_curve([[0, 0], [10, 0], [10, 10], [0, 10]], 2,
                                              u=[0, 0.25, 0.5, 0.75, 1], weights=[1, 5, 1, 5]),
            "mult_ss": lambda: nurbs_curve(c3 + [[70, 10, 5]], 3, splinesteps=4, mult=[1, 2, 1]),
            "knots_u": lambda: nurbs_curve(c2, 3, u=[0, 0.3, 0.6, 1], knots=[0, 0.4, 1]),
            "patch3_ss": lambda: nurbs_patch_points(patch, 3, splinesteps=3),
            "patch_uv": lambda: nurbs_patch_points(patch, 3, u=[0, 0.5, 1], v=[0, 0.5, 1]),
            "patch_mixed": lambda: nurbs_patch_points(patch, [3, 2], splinesteps=[2, 3]),
            "elevate_deg": lambda: nurbs_elevate_degree(c2, 3)[1],
            "elevate_ctrl": lambda: nurbs_elevate_degree(c2, 3)[2],
        }
        for case in TRUTH["nurbs"]:
            with self.subTest(kw=case["kw"]):
                got = np.array(calls[case["kw"]](), dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "shape must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


class TestRoundingMatchesBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2 import round_corners, smooth_path
        sq = [[0, 0], [40, 0], [40, 30], [0, 30]]
        op = [[0, 0], [40, 0], [40, 30], [20, 45], [0, 30]]
        p3 = [[0, 0, 0], [40, 0, 0], [40, 40, 20], [0, 40, 20]]
        wig = [[0, 0], [10, 30], [30, -10], [50, 20], [70, 0]]
        calls = {
            "circle_radius": lambda: round_corners(sq, radius=5),
            "circle_cut": lambda: round_corners(sq, cut=3),
            "circle_joint": lambda: round_corners(sq, joint=5),
            "smooth_joint": lambda: round_corners(sq, method="smooth", joint=8),
            "smooth_cut": lambda: round_corners(sq, method="smooth", cut=2),
            "smooth_k": lambda: round_corners(sq, method="smooth", joint=8, k=0.8),
            "chamfer_joint": lambda: round_corners(sq, method="chamfer", joint=6),
            "chamfer_cut": lambda: round_corners(sq, method="chamfer", cut=4),
            "chamfer_width": lambda: round_corners(sq, method="chamfer", width=5),
            "open_circle": lambda: round_corners(op, radius=5, closed=False),
            "d3_smooth": lambda: round_corners(p3, method="smooth", joint=6),
            "d3_chamfer": lambda: round_corners(p3, method="chamfer", joint=6),
            "smoothpath_rel": lambda: smooth_path(wig, relsize=0.4),
            "smoothpath_size": lambda: smooth_path(wig, size=5),
            "smoothpath_closed": lambda: smooth_path(sq, relsize=0.3, closed=True),
        }
        for case in TRUTH["rounding"]:
            with self.subTest(kw=case["kw"]):
                got = np.array(calls[case["kw"]](), dtype=float)
                exp = np.array(case["res"], dtype=float)
                self.assertEqual(got.shape, exp.shape, "shape must match BOSL2")
                np.testing.assert_allclose(got, exp, atol=1e-6)


class TestIsosurfaceFieldsMatchBosl2(unittest.TestCase):
    def test_every_truth_case(self):
        from pybosl2.isosurface import (mb_sphere, mb_cuboid, mb_torus, mb_capsule, mb_disk,
                                      mb_octahedron, mb_connector)
        pts = [[5, 0, 0], [10, 3, 2], [0, 8, 6], [12, 4, -5], [3, 3, 3]]
        calls = {
            "sphere": mb_sphere(5),
            "sphere_cut": mb_sphere(5, cutoff=12, influence=1.5),
            "cuboid": mb_cuboid(20, 0.5),
            "cuboid_sq": mb_cuboid([16, 20, 24], 0.8),
            "torus": mb_torus(8, 3),
            "capsule": mb_capsule(24, 4),
            "disk": mb_disk(6, 12),
            "octa": mb_octahedron(20, 0.5),
            "connector": mb_connector([-10, 0, 0], [10, 5, 3], 4),
        }
        for case in TRUTH["isosurface"]:
            with self.subTest(fn=case["fn"]):
                mb = calls[case["fn"]]
                got = np.array([mb(p) for p in pts])
                exp = np.array(case["res"], dtype=float)
                np.testing.assert_allclose(got, exp, atol=1e-5, rtol=1e-5)


if __name__ == "__main__":
    unittest.main()
