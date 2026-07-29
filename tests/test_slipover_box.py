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

# LibFile: tests/test_slipover_box.py
#    Numeric/mock tests for slipover_box.py's plain-Python pieces -- which is just its argument
#    validation (the size/positivity asserts fire before any geometry gets built, so they're
#    checkable under the mock). Everything else in slipover_box.py builds real geometry via
#    native primitives, real BOSL2 (osuse()), pysolidfive, or the pybosl2/ port, none of which the
#    numeric mock in pysolidfive/tests/mock_libfive.py can meaningfully stand in for; that side
#    is covered by tests/test_slipover_box_render.py's golden-image renders instead.
#
# FileGroup: slipover_box

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# mock_libfive.py/render_pysolidfive.py live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before slipover_box)

import slipover_box  # noqa: E402


class TestArgumentValidation(unittest.TestCase):
    def test_box_rejects_wrong_size_shape(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_box.MakeBoxWithSlipoverLid([100, 50])

    def test_box_rejects_nonpositive_dimensions(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_box.MakeBoxWithSlipoverLid([100, 0, 10])
        with self.assertRaises(AssertionError):
            slipover_box.MakeBoxWithSlipoverLid([-1, 50, 10])

    def test_lid_rejects_wrong_size_shape(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_box.SlipoverBoxLid([100, 50])

    def test_lid_rejects_nonpositive_dimensions(self) -> None:
        with self.assertRaises(AssertionError):
            slipover_box.SlipoverBoxLid([100, 50, 0])


if __name__ == "__main__":
    unittest.main()
