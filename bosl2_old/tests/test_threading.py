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

"""Tests for bosl2/threading.py: the thread profiles (ported verbatim from BOSL2) and the
Threading rod/nut builders. Native geometry is mocked, so these check the profiles numerically and
that every builder returns a Bosl2Solid; the real geometry (watertight rods/nuts with the right
major/minor diameter and length) is verified in test_stl_render.py."""

import math

import numpy as np
import pytest

from bosl2.threading import Threading, _iso_profile, _trapezoidal_profile, _buttress_profile
from bosl2.shapes3d import Bosl2Solid


# -- thread profiles (in pitch units) -----------------------------------------------------

def test_iso_profile():
    depth = math.cos(math.radians(30)) * 5 / 8
    exp = [[-depth / math.sqrt(3) - 1 / 16, -depth], [-1 / 16, 0], [1 / 16, 0],
           [depth / math.sqrt(3) + 1 / 16, -depth]]
    np.testing.assert_allclose(_iso_profile(), exp, atol=1e-12)


def test_trapezoidal_profile_30deg():
    # thread_angle 30, depth = pitch/2 -> pa_delta = 0.5*(p/2)*tan(15)/p = tan(15)/4
    p = 2.0
    pa = math.tan(math.radians(15)) / 4
    exp = [[-(0.25 + pa), -0.5], [-(0.25 - pa), 0], [0.25 - pa, 0], [0.25 + pa, -0.5]]
    np.testing.assert_allclose(_trapezoidal_profile(p, 30), exp, atol=1e-12)


def test_trapezoidal_depth_scales_with_pitch():
    # y (the depth fraction) is thread_depth/pitch; default depth = pitch/2 -> -0.5
    prof = _trapezoidal_profile(4, 30)
    assert math.isclose(min(p[1] for p in prof), -0.5, abs_tol=1e-12)


def test_buttress_profile_is_asymmetric():
    prof = _buttress_profile()
    assert prof[0] == [-1 / 2, -0.77]
    # asymmetric: the crest [5/16, 7/16] is offset from center, not centred on 0
    crest = [p for p in prof if p[1] == 0]
    crest_mid = (crest[0][0] + crest[-1][0]) / 2
    assert not math.isclose(crest_mid, 0.0, abs_tol=1e-6)


def test_impossible_trapezoid_raises():
    with pytest.raises(AssertionError):
        _trapezoidal_profile(1, 170)  # flanks would cross


# -- rod builders return solids -----------------------------------------------------------

@pytest.mark.parametrize("call", [
    lambda: Threading.threaded_rod(12, 24, 1.75),
    lambda: Threading.trapezoidal_threaded_rod(20, 30, 4),
    lambda: Threading.acme_threaded_rod(20, 30, 4),
    lambda: Threading.square_threaded_rod(20, 30, 4),
    lambda: Threading.buttress_threaded_rod(20, 30, 4),
    lambda: Threading.generic_threaded_rod(16, 24, 2, _iso_profile()),
    lambda: Threading.threaded_rod(16, 24, 2, starts=2),
    lambda: Threading.threaded_rod(12, 24, 1.75, left_handed=True),
])
def test_rod_builders(call):
    assert isinstance(call(), Bosl2Solid)


# -- nut builders return solids -----------------------------------------------------------

@pytest.mark.parametrize("call", [
    lambda: Threading.threaded_nut(18, 12, 10, 1.75, slop=0.1),
    lambda: Threading.threaded_nut(18, 12, 10, 1.75, shape="square", slop=0.1),
    lambda: Threading.trapezoidal_threaded_nut(24, 16, 12, 3, slop=0.1),
    lambda: Threading.acme_threaded_nut(24, 16, 12, 3, slop=0.1),
    lambda: Threading.square_threaded_nut(24, 16, 12, 3, slop=0.1),
    lambda: Threading.buttress_threaded_nut(24, 16, 12, 3, slop=0.1),
    lambda: Threading.generic_threaded_nut(18, 12, 10, 1.75, _iso_profile(), slop=0.1),
])
def test_nut_builders(call):
    assert isinstance(call(), Bosl2Solid)


def test_nut_with_zero_pitch_is_plain_hole():
    # pitch 0 -> unthreaded bore
    assert isinstance(Threading.threaded_nut(18, 12, 10, 0), Bosl2Solid)


def test_thread_helix_builds():
    assert isinstance(Threading.thread_helix(20, 4, turns=3), Bosl2Solid)
    assert isinstance(Threading.thread_helix(20, 4, thread_depth=1.5, flank_angle=20, turns=2), Bosl2Solid)


def test_invalid_rod_dims_raise():
    with pytest.raises(AssertionError):
        Threading.generic_threaded_rod(12, 24, 0, _iso_profile())  # pitch 0
    with pytest.raises(AssertionError):
        Threading.generic_threaded_rod(0, 24, 1.5, _iso_profile())  # d 0


def test_bad_nut_shape_raises():
    with pytest.raises(AssertionError):
        Threading.threaded_nut(18, 12, 10, 1.75, shape="round")
