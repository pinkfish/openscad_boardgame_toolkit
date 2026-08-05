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

# LibFile: tests/test_lids_base.py
#    Numeric/mock tests for lids_base.py's plain-Python helper functions (dense-shape-type
#    classification). Complements tests/test_lids_base_render.py (which renders the actual
#    solid-producing functions with the real PythonSCAD binary): everything else in lids_base.py
#    builds real geometry via native primitives, real BOSL2 (osuse()), or the pybosl2/ port, none
#    of which the numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand in for (its native
#    cube()/cylinder()/sphere() stubs return None, so any real geometry chain crashes under it).
#
# FileGroup: lids_base

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py now live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))


import lids_base  # noqa: E402
import patterns  # noqa: E402  -- IsDenseShapeType/DenseShapeEdges moved here with
                 #                the pattern refactor (lids_base no longer owns the
                 #                'is this shape dense' question; the lattice does)


class TestIsDenseShapeType(unittest.TestCase):
    def test_dense_types(self) -> None:
        for t in (
            lids_base.ShapeType.DENSE_HEX,
            lids_base.ShapeType.DENSE_TRIANGLE,
            lids_base.ShapeType.DELTOID_TRIHEXAGONAL_KITE,
            lids_base.ShapeType.DELTOID_TRIHEXAGONAL,
        ):
            self.assertTrue(patterns.IsDenseShapeType(t), f"{t} should be dense")

    def test_non_dense_type(self) -> None:
        self.assertFalse(patterns.IsDenseShapeType(lids_base.ShapeType.SUPERSHAPE))

    def test_default_uses_module_default(self) -> None:
        self.assertEqual(patterns.IsDenseShapeType(), patterns.IsDenseShapeType(lids_base.default_lid_shape_type))


class TestDenseShapeEdges(unittest.TestCase):
    def test_triangle_has_three_edges(self) -> None:
        self.assertEqual(patterns.DenseShapeEdges(lids_base.ShapeType.DENSE_TRIANGLE), 3)

    def test_hex_has_six_edges(self) -> None:
        self.assertEqual(patterns.DenseShapeEdges(lids_base.ShapeType.DENSE_HEX), 6)

    def test_other_dense_types_default_to_six(self) -> None:
        self.assertEqual(patterns.DenseShapeEdges(lids_base.ShapeType.DELTOID_TRIHEXAGONAL), 6)


if __name__ == "__main__":
    unittest.main()
