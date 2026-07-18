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

"""Tests for bosl2/masking.py: the 2-D roundover mask cross-section."""

import math

import numpy as np
import pytest

from bosl2.masking import mask2d_roundover


def test_returns_a_point_path():
    path = mask2d_roundover(r=3)
    assert isinstance(path, list)
    assert len(path) > 3
    assert all(len(p) == 2 for p in path)


def test_diameter_matches_radius():
    np.testing.assert_allclose(mask2d_roundover(r=3), mask2d_roundover(d=6))


def test_corner_and_skirt_geometry():
    # the L-shape starts along +X and +Y with the given excess skirt past the origin
    path = mask2d_roundover(r=4, excess=0.1)
    arr = np.asarray(path)
    assert arr[:, 0].min() == pytest.approx(-0.1)  # x skirt
    assert arr[:, 1].min() == pytest.approx(-0.1)  # y skirt


def test_quarter_circle_bite_radius():
    # the rounded far corner points all sit radius r from the rounding center [r, r]
    r = 5.0
    path = mask2d_roundover(r=r, excess=0.01)
    arc_pts = np.asarray(path[3:])  # the first three points are the two flat legs
    for p in arc_pts:
        assert math.isclose(math.hypot(p[0] - r, p[1] - r), r, abs_tol=1e-9)


def test_requires_r_or_d():
    with pytest.raises(AssertionError):
        mask2d_roundover()


def test_finer_fn_gives_more_points():
    coarse = mask2d_roundover(r=5, _fn=8)
    fine = mask2d_roundover(r=5, _fn=64)
    assert len(fine) > len(coarse)
