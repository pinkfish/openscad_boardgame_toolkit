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

# LibFile: tests/test_bosl2_anchor.py
#    Pure-Python tests for pybosl2.shapes3d's bbox-backed anchoring/attachment system --
#    Bosl2Solid.bounds()/anchor_point()/reanchor()/position()/attach()/align(), the
#    _rot_from_to() helper, bbox-backed masking on an object with no tracked size metadata,
#    and regular_prism(). These run against whatever geometry backend is importable -- the
#    pythonscad wheel is enough, no app window needed -- so every expectation here must be the
#    REAL bounding box, not the bounding cylinder a stand-in would report. (They used to run
#    against mock_libfive's _AabbSolid; that moved inside the installed pysolidfive package and
#    is no longer importable from here, which left the mock-only expectations below failing
#    silently against real geometry.) The real-render equivalents live in the box-module
#    render tests.
#
#    NOTE on attachments: position()/attach()/align() record the child in .attachments and
#    defer the union to realize() -- pybosl2's own tests measure them the same way -- so
#    bounds() on the returned solid still reports only the parent. Measure .realize().bounds()
#    when you want the combined box.
#
# FileGroup: BOSL2

import math
import os
import sys
import unittest
from typing import Any

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "pysolidfive", "tests"))


import venv_path  # noqa: F401,E402  -- pin pybosl2 to the project venv
import pybosl2.shapes3d as b3  # noqa: E402
import pybosl2.masking as bm  # noqa: E402
from pybosl2.constants import TOP, BOTTOM, RIGHT, LEFT, FRONT, BACK, CENTER  # noqa: E402
from pybosl2.shapes3d import Bosl2Solid  # noqa: E402
from pybosl2.transforms import rot_from_to as _rot_from_to  # 0.6.7 moved it out of shapes3d


def approx(a, b, tol=1e-6):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


class TestBounds(unittest.TestCase):
    def test_cuboid_bounds_from_native_bbox(self):
        box = b3.cuboid([40, 30, 20])
        center, size = box.bounds()
        self.assertTrue(approx(center, [0, 0, 0]), center)
        self.assertTrue(approx(size, [40, 30, 20]), size)

    def test_bounds_after_translate_reflects_move(self):
        box = b3.cuboid([10, 10, 10]).translate([5, 6, 7])
        center, size = box.bounds()
        self.assertTrue(approx(center, [5, 6, 7]), center)
        self.assertTrue(approx(size, [10, 10, 10]), size)

    def test_bounds_of_union_is_combined_box(self):
        u = b3.cuboid([10, 10, 10]) | b3.cuboid([10, 10, 10]).translate([40, 0, 0])
        center, size = u.bounds()
        self.assertTrue(approx(center, [20, 0, 0]), center)
        self.assertTrue(approx(size, [50, 10, 10]), size)

    def test_bounds_falls_back_to_tracked_metadata(self):
        # A handle whose native accessors read None (what PythonSCAD returns for empty or
        # degenerate geometry) has no native bounds; the tracked cuboid size/anchor metadata
        # is used instead.
        class _NoBox:
            position = None
            size = None

        blank: Any = _NoBox()
        solid = Bosl2Solid(blank, size=[8, 6, 4], anchor=CENTER)
        center, size = solid.bounds()
        self.assertTrue(approx(center, [0, 0, 0]), center)
        self.assertTrue(approx(size, [8, 6, 4]), size)


class TestAnchorPoint(unittest.TestCase):
    def setUp(self):
        self.box = b3.cuboid([40, 30, 20])  # centered

    def test_face_anchors(self):
        self.assertTrue(approx(self.box.anchor_point(TOP), [0, 0, 10]))
        self.assertTrue(approx(self.box.anchor_point(BOTTOM), [0, 0, -10]))
        self.assertTrue(approx(self.box.anchor_point(RIGHT), [20, 0, 0]))
        self.assertTrue(approx(self.box.anchor_point(FRONT), [0, -15, 0]))

    def test_corner_anchor(self):
        self.assertTrue(approx(self.box.anchor_point([1, 1, 1]), [20, 15, 10]))

    def test_center_anchor(self):
        self.assertTrue(approx(self.box.anchor_point(CENTER), [0, 0, 0]))


class TestReanchor(unittest.TestCase):
    def test_reanchor_moves_anchor_to_origin(self):
        box = b3.cuboid([40, 30, 20])
        # re-anchor to BOTTOM: the bottom face center should now sit at the origin
        rb = box.reanchor(BOTTOM)
        self.assertTrue(approx(rb.anchor_point(BOTTOM), [0, 0, 0]), rb.anchor_point(BOTTOM))
        center, size = rb.bounds()
        self.assertTrue(approx(center, [0, 0, 10]), center)  # box now sits on z=0
        self.assertTrue(approx(size, [40, 30, 20]), size)


class TestPosition(unittest.TestCase):
    def test_position_places_child_origin_at_parent_anchor(self):
        box = b3.cuboid([40, 30, 20])
        # a 6-cube (centered) placed at the parent's TOP -> its center lands at z=10,
        # so the combined top rises to 10+3=13
        combined = box.position(TOP, b3.cuboid([6, 6, 6]))
        center, size = combined.realize().bounds()
        self.assertTrue(approx(size, [40, 30, 23]), size)  # z from -10 to 13
        self.assertAlmostEqual(center[2], 1.5, places=6)


class TestAttach(unittest.TestCase):
    def test_attach_mates_child_bottom_to_parent_top(self):
        box = b3.cuboid([40, 30, 20])
        # cylinder h=12 attached to TOP, default child_anchor=BOTTOM, no overlap:
        # cyl spans z=[10,22]; combined z=[-10,22]
        combined = box.attach(TOP, b3.cylinder(height=12, radius=4))
        center, size = combined.realize().bounds()
        self.assertAlmostEqual(size[2], 32.0, places=6)

    def test_attach_overlap_sinks_child_in(self):
        box = b3.cuboid([40, 30, 20])
        combined = box.attach(TOP, b3.cylinder(height=12, radius=4), overlap=2)
        _, size = combined.realize().bounds()
        self.assertAlmostEqual(size[2], 30.0, places=6)  # cyl now z=[8,20]


class TestAlign(unittest.TestCase):
    def test_align_outside_default(self):
        box = b3.cuboid([40, 30, 20])
        combined = box.align(TOP, b3.cuboid([6, 6, 6]))
        _, size = combined.realize().bounds()
        self.assertAlmostEqual(size[2], 26.0, places=6)  # child sits on top, z=[10,16]

    def test_align_inside(self):
        box = b3.cuboid([40, 30, 20])
        combined = box.align(TOP, b3.cuboid([6, 6, 6]), inside=True)
        _, size = combined.realize().bounds()
        self.assertAlmostEqual(size[2], 20.0, places=6)  # child tucked inside, bbox unchanged


class TestRotFromTo(unittest.TestCase):
    def test_parallel_is_no_rotation(self):
        angle, _ = _rot_from_to([0, 0, 1], [0, 0, 1])
        self.assertEqual(angle, 0.0)

    def test_antiparallel_is_180(self):
        angle, axis = _rot_from_to([0, 0, 1], [0, 0, -1])
        self.assertEqual(angle, 180.0)
        self.assertAlmostEqual(sum(a * b for a, b in zip(axis, [0, 0, 1])), 0.0, places=6)  # axis perp to z

    def test_ninety_degrees(self):
        angle, axis = _rot_from_to([1, 0, 0], [0, 1, 0])
        self.assertAlmostEqual(angle, 90.0, places=6)
        self.assertTrue(approx([abs(x) for x in axis], [0, 0, 1]))


class TestBboxBackedMasking(unittest.TestCase):
    def test_edge_mask_works_without_tracked_size(self):
        # Wrap a raw native cube with NO tracked size metadata -- masking must still find the
        # box via the native bbox and not raise.
        raw: Any = b3.cuboid([30, 30, 30]).shape  # the bare native handle, no wrapper metadata
        solid = Bosl2Solid(raw)  # size=None
        self.assertIsNone(solid.size)
        result = solid.edge_mask([TOP], children=bm.rounding_edge_mask(radius=4, length=30))
        # rounding an edge takes material away, so the box keeps its nominal extents
        _, size = result.bounds()
        self.assertTrue(approx(size, [30, 30, 30]), size)


class TestRegularPrism(unittest.TestCase):
    def test_hexagon_circumradius(self):
        # under the mock the prism's bbox is its bounding cylinder (2*circumradius square)
        prism = b3.regular_prism(6, height=20, radius=15)
        _, size = prism.bounds()
        self.assertAlmostEqual(size[0], 30.0, places=6)
        self.assertAlmostEqual(size[2], 20.0, places=6)

    def test_inradius_converts_to_circumradius(self):
        # A real pentagon's bbox is NOT 2*circumradius wide (only the even-n cases with a
        # vertex on each side are), so assert the conversion itself: inner_radius=r has to
        # build exactly the prism radius=r/cos(pi/n) builds.
        by_inradius = b3.regular_prism(5, height=10, inner_radius=12)
        by_radius = b3.regular_prism(5, height=10, radius=12 / math.cos(math.pi / 5))
        self.assertTrue(approx(by_inradius.bounds()[1], by_radius.bounds()[1]), by_inradius.bounds()[1])

    def test_side_converts_to_circumradius(self):
        prism = b3.regular_prism(4, height=10, side=10)
        _, size = prism.bounds()
        self.assertAlmostEqual(size[0], 2 * (10 / (2 * math.sin(math.pi / 4))), places=5)

    def test_rejects_bad_n(self):
        with self.assertRaises(AssertionError):
            b3.regular_prism(2, height=10, radius=5)


if __name__ == "__main__":
    unittest.main()
