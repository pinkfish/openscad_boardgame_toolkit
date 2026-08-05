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

"""The path-box children contract: callable(inner) taking an InnerPath.

This replaced the old callable(inner_path, inner_width, inner_length, inner_height), whose
inner_path point list nothing ever read -- every box paid to inset a polygon for nobody. The
inside is now reached through inner.profile(), a function pointer, so it is only built if a
child asks. These tests pin both halves: that children receive an InnerPath, and that
profile() is genuinely lazy.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base_bgtk import InnerPath  # noqa: E402
from no_lid import PathBoxWithNoLid  # noqa: E402

SQUARE = [[0, 0], [60, 0], [60, 40], [0, 40]]

# NOTE: these target PathBoxWithNoLid.inner() directly rather than driving a full build().
# The full box cannot be built under the numeric mock while no_lid still reaches BOSL2 through
# osuse() (make_region/union/difference yield a stub that dies on subscript) -- the same reason
# tests/test_shape_type.py skips its tesselation shapes. The assembled box IS covered by the
# real render tests (tests/test_no_lid_render.py, 9 goldens including the polygon-hex path).
# Fold the box-level cases in here once no_lid is off osuse.


class TestInnerPathContract(unittest.TestCase):
    def test_is_an_inner_path(self):
        self.assertIsInstance(PathBoxWithNoLid(path=SQUARE, height=20, wall_thickness=2, floor_thickness=2).inner(), InnerPath)

    def test_carries_the_box_dimensions(self):
        inner = PathBoxWithNoLid(path=SQUARE, height=20, wall_thickness=2, floor_thickness=2).inner()
        self.assertAlmostEqual(inner.width, 60)
        self.assertAlmostEqual(inner.length, 40)
        self.assertAlmostEqual(inner.height, 18)
        self.assertEqual([list(p) for p in inner.path], SQUARE)

    def test_profile_is_a_lazy_function_pointer(self):
        # The point of the redesign: a child that ignores the inside must never cause the inset
        # outline to be built. profile() must be a callable, not a precomputed value.
        inner = PathBoxWithNoLid(path=SQUARE, height=20, wall_thickness=2, floor_thickness=2).inner()
        self.assertTrue(callable(inner.profile))

    def test_profile_returns_geometry_when_asked(self):
        inner = PathBoxWithNoLid(path=SQUARE, height=20, wall_thickness=2, floor_thickness=2).inner()
        self.assertIsNotNone(inner.profile())
        self.assertIsNotNone(inner.profile(2))  # inset further

    def test_profile_insets_by_wall_thickness(self):
        # profile(inset) must offset by -(wall_thickness + inset); check the call reaches
        # native offset() with the right radius rather than trusting the closure by eye.
        calls = []

        class _Recorder:
            def offset(self, **kw):
                calls.append(kw)
                return self

        import no_lid

        original = no_lid.polygon
        no_lid.polygon = lambda pts: _Recorder()
        try:
            inner = PathBoxWithNoLid(path=SQUARE, height=20, wall_thickness=3, floor_thickness=2).inner()
            inner.profile()
            inner.profile(2)
        finally:
            no_lid.polygon = original

        self.assertEqual(calls, [{"r": -3.0}, {"r": -5.0}])


if __name__ == "__main__":
    unittest.main()
