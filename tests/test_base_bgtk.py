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

# LibFile: tests/test_base_bgtk.py
#    Numeric/mock tests for base_bgtk.py's plain-Python pieces: the Vec3 anchor-vector
#    arithmetic, ResolveChild's callable-vs-plain dispatch, the IntEnum constants, and the
#    InnerSize/InnerObject dataclasses. Complements tests/test_base_bgtk_render.py (which
#    renders DifferenceWithOffset()/DifferenceWithOffsetRounded() -- the only actual
#    geometry-producing functions in this file -- with the real PythonSCAD binary; those call
#    real BOSL2 (osuse()) and native offset()/difference(), neither of which the numeric mock in
#    pysolidfive/tests/mock_libfive.py can meaningfully stand in for).
#
# FileGroup: base_bgtk

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py now live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))


import base_bgtk  # noqa: E402


class TestVec3(unittest.TestCase):
    def test_direction_constants(self) -> None:
        self.assertEqual(base_bgtk.TOP, [0, 0, 1])
        self.assertEqual(base_bgtk.BOTTOM, [0, 0, -1])
        self.assertEqual(base_bgtk.FRONT, [0, -1, 0])
        self.assertEqual(base_bgtk.BACK, [0, 1, 0])
        self.assertEqual(base_bgtk.LEFT, [-1, 0, 0])
        self.assertEqual(base_bgtk.RIGHT, [1, 0, 0])
        self.assertEqual(base_bgtk.CENTER, [0, 0, 0])

    def test_aliases_match_their_canonical_direction(self) -> None:
        self.assertEqual(base_bgtk.BOT, base_bgtk.BOTTOM)
        self.assertEqual(base_bgtk.UP, base_bgtk.TOP)
        self.assertEqual(base_bgtk.DOWN, base_bgtk.BOTTOM)

    def test_elementwise_addition_not_concatenation(self) -> None:
        # The whole reason Vec3 exists: BOSL2-style anchor=TOP+LEFT must add elementwise, not
        # concatenate like a plain Python list's `+` would.
        self.assertEqual(base_bgtk.TOP + base_bgtk.LEFT, [-1, 0, 1])
        self.assertEqual(len(base_bgtk.TOP + base_bgtk.LEFT), 3)

    def test_elementwise_subtraction(self) -> None:
        self.assertEqual(base_bgtk.TOP - base_bgtk.BOTTOM, [0, 0, 2])

    def test_negation(self) -> None:
        self.assertEqual(-base_bgtk.TOP, base_bgtk.BOTTOM)

    def test_scalar_multiplication_both_orders(self) -> None:
        self.assertEqual(base_bgtk.TOP * 2, [0, 0, 2])
        self.assertEqual(2 * base_bgtk.TOP, [0, 0, 2])

    def test_radd_and_rsub_with_a_plain_list(self) -> None:
        # __radd__/__rsub__ matter when a Vec3 is the *right*-hand operand of a plain list.
        self.assertEqual([1, 1, 1] + base_bgtk.TOP, [1, 1, 2])
        self.assertEqual([1, 1, 1] - base_bgtk.TOP, [1, 1, 0])

    def test_still_behaves_like_a_list(self) -> None:
        v = base_bgtk.TOP + base_bgtk.LEFT
        self.assertIsInstance(v, list)
        self.assertEqual(v[2], 1)
        self.assertEqual(list(v), [-1, 0, 1])


class TestResolveChild(unittest.TestCase):
    def test_plain_value_passed_through_unchanged(self) -> None:
        self.assertEqual(base_bgtk.ResolveChild("a solid", 10, 20, 30), "a solid")

    def test_callable_invoked_with_inner_dimensions(self) -> None:
        seen = {}

        def child(inner_width, inner_length, inner_height):
            seen["args"] = (inner_width, inner_length, inner_height)
            return "resolved"

        result = base_bgtk.ResolveChild(child, 10, 20, 30)
        self.assertEqual(result, "resolved")
        self.assertEqual(seen["args"], (10, 20, 30))


class TestEnumsHaveUniqueValues(unittest.TestCase):
    """Guards against a copy-paste typo giving two constants the same underlying int -- an
    IntEnum with an accidental alias silently makes two named members compare equal."""

    def _assert_unique(self, enum_cls) -> None:
        values = [member.value for member in enum_cls]
        self.assertEqual(len(values), len(set(values)), f"{enum_cls.__name__} has duplicate values")

    def test_shape_type_values_are_unique(self) -> None:
        self._assert_unique(base_bgtk.ShapeType)

    def test_catch_type_values_are_unique(self) -> None:
        self._assert_unique(base_bgtk.CatchType)

    def test_label_type_values_are_unique(self) -> None:
        self._assert_unique(base_bgtk.LabelType)

    def test_object_type_values_are_unique(self) -> None:
        self._assert_unique(base_bgtk.ObjectType)


class TestDataclasses(unittest.TestCase):
    def test_inner_size_fields(self) -> None:
        size = base_bgtk.InnerSize(width=10, length=20, height=30)
        self.assertEqual((size.width, size.length, size.height), (10, 20, 30))

    def test_inner_object_defaults(self) -> None:
        obj = base_bgtk.InnerObject(value="a solid")
        self.assertEqual(obj.value, "a solid")
        self.assertEqual(obj.type, base_bgtk.ObjectType.NEGATIVE)
        self.assertIsNone(obj.color)

    def test_inner_object_overrides(self) -> None:
        obj = base_bgtk.InnerObject(value="a solid", type=base_bgtk.ObjectType.POSITIVE, color="red")
        self.assertEqual(obj.type, base_bgtk.ObjectType.POSITIVE)
        self.assertEqual(obj.color, "red")


if __name__ == "__main__":
    unittest.main()
