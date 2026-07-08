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

# LibFile: tests/test_components.py
#    Numeric/mock tests for components.py's plain-Python helper functions (polygon math,
#    position-index mapping). Complements tests/test_components_render.py (which renders the
#    actual solid-producing functions with the real PythonSCAD binary): everything else in
#    components.py builds real geometry via native primitives, real BOSL2 (osuse()), or the
#    bosl2/ port, none of which the numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand
#    in for (its native cube()/cylinder()/sphere() stubs return None, so any real geometry chain
#    crashes under it) -- real-render testing is what tests/test_components_render.py is for.
#
# FileGroup: components

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py now live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before components)

import components  # noqa: E402


class TestPolygonMath(unittest.TestCase):
    def test_apothem_radius_roundtrip(self) -> None:
        for shape_edges in (3, 4, 5, 6, 8, 12):
            for apothem in (1.0, 5.5, 20.0):
                radius = components.PolygonRadiusFromApothem(apothem, shape_edges)
                roundtrip = components.PolygonApothemFromRadius(radius, shape_edges)
                self.assertAlmostEqual(roundtrip, apothem, places=9)

    def test_known_hexagon_values(self) -> None:
        # PolygonRadiusFromApothem()'s `apothem` arg is actually the full flat-to-flat width
        # (2x the true apothem) -- matches every caller's usage (e.g. RegularPolygon()'s `width`
        # docstring: "total width (apothem * 2)"). A regular hexagon's apothem is r*cos(30deg),
        # so radius = width / (2*cos(30deg)) = width/sqrt(3).
        radius = components.PolygonRadiusFromApothem(10.0, 6)
        self.assertAlmostEqual(radius, 10.0 / (3**0.5), places=9)

    def test_known_square_values(self) -> None:
        # Same width-not-apothem convention as above; a square's apothem is r*cos(45deg), so
        # radius = width / (2*cos(45deg)) = width/sqrt(2).
        radius = components.PolygonRadiusFromApothem(10.0, 4)
        self.assertAlmostEqual(radius, 10.0 / (2**0.5), places=9)


class TestHoleToPosition(unittest.TestCase):
    def test_all_eight_positions(self) -> None:
        expected = {
            0: [0, -1, 0],
            1: [1, -1, 0],
            2: [1, 0, 0],
            3: [1, 1, 0],
            4: [0, 1, 0],
            5: [-1, 1, 0],
            6: [-1, 0, 0],
            7: [-1, -1, 0],
        }
        for pos, vec in expected.items():
            self.assertEqual(components.HoleToPosition(pos), vec)

    def test_invalid_position_defaults_to_front(self) -> None:
        self.assertEqual(components.HoleToPosition(99), [0, -1, 0])


if __name__ == "__main__":
    unittest.main()
