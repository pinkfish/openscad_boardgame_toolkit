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

"""Tests for bosl2/color.py: the HSL/HSV conversions, rainbow(), and the Colorable colour operators
on Bosl2Solid. The conversions are pinned to real BOSL2 in tests/test_bosl2_reorient.py; here we
check edge cases and the object-level operators (native colour is mocked, so we assert type/wrapper
behaviour, verified for real in test_stl_render.py)."""

import numpy as np
import pytest

from bosl2.color import hsl, hsv, rainbow, rainbow_colors
from bosl2.shapes3d import Bosl2Solid, cuboid


# -- HSV / HSL primaries ------------------------------------------------------------------

def test_hsv_primaries():
    np.testing.assert_allclose(hsv(0, 1, 1), [1, 0, 0], atol=1e-9)
    np.testing.assert_allclose(hsv(120, 1, 1), [0, 1, 0], atol=1e-9)
    np.testing.assert_allclose(hsv(240, 1, 1), [0, 0, 1], atol=1e-9)
    np.testing.assert_allclose(hsv(60, 1, 1), [1, 1, 0], atol=1e-9)   # yellow
    np.testing.assert_allclose(hsv(180, 1, 1), [0, 1, 1], atol=1e-9)  # cyan


def test_hsl_primaries():
    np.testing.assert_allclose(hsl(0, 1, 0.5), [1, 0, 0], atol=1e-9)
    np.testing.assert_allclose(hsl(120, 1, 0.5), [0, 1, 0], atol=1e-9)
    np.testing.assert_allclose(hsl(240, 1, 0.5), [0, 0, 1], atol=1e-9)


def test_hsl_lightness_extremes():
    np.testing.assert_allclose(hsl(200, 1, 0.0), [0, 0, 0], atol=1e-9)  # black
    np.testing.assert_allclose(hsl(200, 1, 1.0), [1, 1, 1], atol=1e-9)  # white


def test_grayscale_when_saturation_zero():
    np.testing.assert_allclose(hsv(123, 0, 0.4), [0.4, 0.4, 0.4], atol=1e-9)
    np.testing.assert_allclose(hsl(123, 0, 0.4), [0.4, 0.4, 0.4], atol=1e-9)


def test_alpha_appended_only_when_given():
    assert len(hsv(120, 1, 1)) == 3
    assert len(hsl(120, 1, 0.5)) == 3
    assert hsv(120, 1, 1, 0.25)[-1] == 0.25 and len(hsv(120, 1, 1, 0.25)) == 4
    assert hsl(120, 1, 0.5, 0.25)[-1] == 0.25 and len(hsl(120, 1, 0.5, 0.25)) == 4


def test_hue_wraps_modulo_360():
    np.testing.assert_allclose(hsv(360, 1, 1), hsv(0, 1, 1), atol=1e-9)
    np.testing.assert_allclose(hsv(480, 1, 1), hsv(120, 1, 1), atol=1e-9)


def test_hsv_validates_ranges():
    with pytest.raises(AssertionError):
        hsv(0, 1.5, 1)
    with pytest.raises(AssertionError):
        hsv(0, 1, -0.1)
    with pytest.raises(AssertionError):
        hsv(0, 1, 1, a=2)


# -- rainbow ------------------------------------------------------------------------------

def test_rainbow_colors_count_and_spread():
    cols = rainbow_colors(6)
    assert len(cols) == 6
    assert all(len(c) == 3 for c in cols)
    assert cols[0] != cols[1]  # consecutive hues differ


def test_rainbow_colors_empty():
    assert rainbow_colors(0) == []


def test_rainbow_shuffle_is_seed_stable():
    a = rainbow_colors(8, shuffle=True, seed=42)
    b = rainbow_colors(8, shuffle=True, seed=42)
    assert a == b  # deterministic for a fixed seed


def test_rainbow_colors_each_object():
    parts = [cuboid([5, 5, 5]) for _ in range(4)]
    out = rainbow(parts)
    assert len(out) == 4
    assert all(isinstance(o, Bosl2Solid) for o in out)


# -- Colorable operators on Bosl2Solid ----------------------------------------------------

BOX = cuboid([10, 10, 10])


def test_color_forms_return_solid():
    assert isinstance(BOX.color("red"), Bosl2Solid)
    assert isinstance(BOX.color([1, 0, 0]), Bosl2Solid)
    assert isinstance(BOX.color([1, 0, 0, 0.5]), Bosl2Solid)
    assert isinstance(BOX.color("red", alpha=0.4), Bosl2Solid)


def test_color_noop_when_nothing_given():
    assert BOX.color() is BOX


def test_recolor_and_color_this():
    assert isinstance(BOX.recolor("blue"), Bosl2Solid)
    assert isinstance(BOX.color_this("green"), Bosl2Solid)
    # "default"/None leaves the object unchanged (no $color scheme in the native backend)
    assert BOX.recolor("default") is BOX
    assert BOX.recolor(None) is BOX
    assert BOX.color_this("default") is BOX


def test_hsl_hsv_methods_return_solid():
    assert isinstance(BOX.hsl(200, 0.8, 0.5), Bosl2Solid)
    assert isinstance(BOX.hsv(60, 1, 1), Bosl2Solid)
    assert isinstance(BOX.hsv(60, 1, 1, 0.5), Bosl2Solid)


def test_highlight_and_ghost():
    assert isinstance(BOX.highlight(), Bosl2Solid)
    assert isinstance(BOX.ghost(), Bosl2Solid)
    assert BOX.highlight(False) is BOX  # disabling is a no-op
    assert BOX.ghost(False) is BOX


def test_color_chains_with_transforms():
    # colour returns a Bosl2Solid, so the fluent chain keeps working
    result = cuboid([10, 10, 10]).hsv(30).right(5).up(2)
    assert isinstance(result, Bosl2Solid)
