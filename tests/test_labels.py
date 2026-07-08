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

# LibFile: tests/test_labels.py
#    Numeric/mock tests for labels.py's plain-Python pieces (LabelOptions/MakeLabelOptions
#    defaults and overrides). Complements tests/test_labels_render.py (which renders the actual
#    solid-producing functions with the real PythonSCAD binary): everything else in labels.py
#    builds real geometry via native primitives, real BOSL2 (osuse()), or the bosl2/ port, none
#    of which the numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand in for.
#
# FileGroup: labels

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py now live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before labels)

import labels  # noqa: E402
from base_bgtk import LabelType  # noqa: E402


class TestMakeLabelOptions(unittest.TestCase):
    def test_defaults_match_dataclass_defaults(self) -> None:
        opts = labels.MakeLabelOptions()
        self.assertEqual(opts.text_scale, 1.0)
        self.assertIsNone(opts.text_length)
        self.assertEqual(opts.border, 2)
        self.assertEqual(opts.offset, 4)
        self.assertEqual(opts.radius, 5)
        self.assertFalse(opts.full_height)
        self.assertEqual(opts.label_diff, [0, 0])

    def test_overrides_apply(self) -> None:
        opts = labels.MakeLabelOptions(material_colour="blue", text_scale=2.0, label_type=LabelType.FRAMELESS)
        self.assertEqual(opts.material_colour, "blue")
        self.assertEqual(opts.text_scale, 2.0)
        self.assertEqual(opts.label_type, LabelType.FRAMELESS)
        # Unset fields still fall back to their defaults.
        self.assertEqual(opts.border, 2)

    def test_label_diff_defaults_are_independent_lists(self) -> None:
        # label_diff uses a dataclass default_factory -- each call must get its own list, not a
        # shared mutable default that leaks state between callers.
        opts_a = labels.MakeLabelOptions()
        opts_b = labels.MakeLabelOptions()
        opts_a.label_diff.append(99)
        self.assertEqual(opts_b.label_diff, [0, 0])


if __name__ == "__main__":
    unittest.main()
