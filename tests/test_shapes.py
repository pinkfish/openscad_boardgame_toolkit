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

# LibFile: tests/test_shapes.py
#    Numeric/mock tests for shapes.py's plain-Python pieces: MakeShapeObject()'s options
#    factory and the *Width() aspect-ratio calculators. Every actual 2-D shape function builds
#    real geometry (native circle/polygon/hull, real-BOSL2 stroke, the pybosl2/ port's rect/
#    supershape), which the numeric mock can't stand in for -- that side is covered
#    exhaustively by tests/test_shapes_render.py's golden-image renders.
#
# FileGroup: shapes

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before shapes)

import shapes  # noqa: E402


class TestMakeShapeObject(unittest.TestCase):
    def test_defaults(self) -> None:
        obj = shapes.MakeShapeObject()
        self.assertEqual(obj.shape_type, shapes.default_lid_shape_type)
        self.assertEqual(obj.shape_width, shapes.default_lid_shape_width)
        self.assertEqual(obj.shape_thickness, shapes.default_lid_shape_thickness)

    def test_overrides(self) -> None:
        obj = shapes.MakeShapeObject(shape_width=25, shape_thickness=3)
        self.assertEqual(obj.shape_width, 25)
        self.assertEqual(obj.shape_thickness, 3)


class TestWidthCalculators(unittest.TestCase):
    def test_australia_map_width_scales_linearly(self) -> None:
        w100 = shapes.australia_map_width(100)
        w200 = shapes.australia_map_width(200)
        self.assertAlmostEqual(w200, 2 * w100, places=9)
        self.assertGreater(w100, 0)

    def test_ruins_width_scales_linearly(self) -> None:
        w100 = shapes.ruins2d_width(100)
        w200 = shapes.ruins2d_width(200)
        self.assertAlmostEqual(w200, 2 * w100, places=9)
        self.assertGreater(w100, 0)


if __name__ == "__main__":
    unittest.main()
