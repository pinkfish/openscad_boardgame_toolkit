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

# LibFile: tests/test_sliding_box.py
#    Numeric/mock tests for sliding_box.py's plain-Python helper: MakeSlidingLidOptions().
#    Complements tests/test_sliding_box_render.py (which renders the actual solid-producing
#    functions with the real PythonSCAD binary): everything else in sliding_box.py builds real
#    geometry via native primitives, real BOSL2 (osuse()), or the pybosl2/ port, none of which the
#    numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand in for (its native
#    cube()/cylinder()/sphere() stubs return None, so any real geometry chain crashes under it).
#
# FileGroup: sliding_box

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py live inside the installed pysolidfive
# package in the venv.
_venv_tests = (
    Path(__file__).resolve().parent.parent / ".venv" / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages" / "pysolidfive" / "tests"
)
if _venv_tests.is_dir():
    sys.path.insert(0, str(_venv_tests))

import mock_libfive  # noqa: E402  (must be imported, and installed, before sliding_box)

import sliding_box  # noqa: E402


class TestMakeSlidingLidOptions(unittest.TestCase):
    def test_defaults(self) -> None:
        opts = sliding_box.MakeSlidingLidOptions()
        self.assertFalse(opts.two_layer)
        self.assertEqual(opts.two_layer_top_lid_ratio, 0.5)
        self.assertFalse(opts.two_layer_vee_shape)

    def test_overrides(self) -> None:
        opts = sliding_box.MakeSlidingLidOptions(
            two_layer=True, two_layer_top_lid_ratio=0.3, two_layer_vee_shape=True
        )
        self.assertTrue(opts.two_layer)
        self.assertEqual(opts.two_layer_top_lid_ratio, 0.3)
        self.assertTrue(opts.two_layer_vee_shape)


if __name__ == "__main__":
    unittest.main()
