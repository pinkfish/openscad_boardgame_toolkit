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

"""Every ShapeType must build through ShapeByType().

This exists because ShapeType.CLOUD shipped broken: it called resize() with a 2-element vector,
which the real PythonSCAD rejects ("TypeError: Invalid resize dimensions"). Nothing referenced
CLOUD in the tests, so every lid asking for the cloud pattern rendered empty and the suite
stayed green. The sweep below covers all 43 members so a dead shape type can't hide again.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pysolidfive", "tests"))
import mock_libfive  # noqa: F401,E402  (numeric stand-ins; must precede toolkit imports)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shape_type import (  # noqa: E402
    MakeShapeObject,
    ShapeByType,
    ShapeNeedsInnerControl,
    ShapeType,
)

# ShapeType.HILBERT (=10) is declared in base_bgtk.py AND base_bgtk.scad, and components.py
# has a working HilbertCurve(), but NOTHING wires it into ShapeByType -- on either stack
# (SHAPE_TYPE_HILBERT is never referenced anywhere in the .scad). So it is a known
# declared-but-unimplemented gap, not a port regression. Asking for it raises
# "ValueError: Invalid shape type type=10". Delete this skip if it ever gets wired up.
UNIMPLEMENTED = {"HILBERT"}

# The tesselation-family shapes still reach BOSL2 through the osuse() FFI (tesselations.py's
# offset/union/difference/make_region calls). Under the numeric mock osuse() yields a permissive
# stub, so these blow up on len()/subscript rather than building. They are covered by the real
# render tests (tests/test_tesselations_render.py) meanwhile. DELETE this skip set as
# tesselations.py moves off osuse -- each shape should start passing here for free, which is a
# good progress signal for that work.
NEEDS_REAL_BOSL2 = {
    "BIRD", "CHICKEN", "DELTOID_TRIHEXAGONAL", "DELTOID_TRIHEXAGONAL_KITE", "DROP",
    "FLYING_BIRD", "GOOSE", "HALF_REGULAR_HEXAGON", "LEAF", "LEAF_VEINS", "LIZARD",
    "PEGASUS", "SHEEP", "VORONOI",
}

# The layout context ShapeNeedsInnerControl() asks for: 1 => polygon_x/y (+ grid rows/cols),
# 2 => polygon_width/length.
INNER1 = dict(polygon_x=6, polygon_y=6, polygon_grid_rows=2, polygon_grid_cols=2)
INNER2 = dict(polygon_width=30, polygon_length=30)


class TestEveryShapeTypeBuilds(unittest.TestCase):
    def test_all_shape_types(self):
        for shape_type in ShapeType:
            if shape_type is ShapeType.NONE:
                continue
            with self.subTest(shape=shape_type.name):
                if shape_type.name in UNIMPLEMENTED:
                    self.skipTest(f"{shape_type.name} is declared but not wired into "
                                  "ShapeByType on either the .py or .scad stack")
                if shape_type.name in NEEDS_REAL_BOSL2:
                    self.skipTest(f"{shape_type.name} still needs the real BOSL2 via osuse()")
                level = ShapeNeedsInnerControl(shape_type)
                kwargs = {}
                if level == 1:
                    kwargs = dict(INNER1)
                elif level == 2:
                    kwargs = dict(INNER2)
                out = ShapeByType(
                    MakeShapeObject(shape_type=shape_type, shape_width=11, shape_thickness=1),
                    **kwargs,
                )
                self.assertIsNotNone(out, f"{shape_type.name} produced no shape")

    def test_none_shape_type_returns_none(self):
        self.assertIsNone(ShapeByType(MakeShapeObject(shape_type=ShapeType.NONE)))

    def test_cloud_with_aspect_ratio(self):
        # the exact call shape that was broken: CLOUD + a non-default aspect ratio
        out = ShapeByType(MakeShapeObject(shape_type=ShapeType.CLOUD, shape_width=11,
                                          shape_thickness=1, shape_aspect_ratio=1.5))
        self.assertIsNotNone(out)


class TestMockResizeContract(unittest.TestCase):
    """The mock must reject what the real resize() rejects, or bugs like CLOUD's slip through."""

    def test_two_element_resize_raises(self):
        from mock_libfive import _AabbSolid

        with self.assertRaises(TypeError):
            _AabbSolid([0, 0, 0], [1, 1, 1]).resize([5, 5])

    def test_three_element_resize_ok(self):
        from mock_libfive import _AabbSolid

        out = _AabbSolid([0, 0, 0], [1, 1, 1]).resize([5, 4, 0])
        self.assertEqual(out.size, [5, 4, 1])  # 0 leaves that axis alone


if __name__ == "__main__":
    unittest.main()
