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

"""Tests for bosl2/nurbs.py: NURBS curve/patch evaluation, meshing, and degree elevation. The
numeric results are pinned to real BOSL2 in tests/test_bosl2_reorient.py; here we check the object
surface (return types, endpoints, the parameter-list form, and error handling). nurbs_vnf uses the
mocked VNF, so its geometry is checked for real in test_stl_render.py."""

import math

import numpy as np
import pytest

from bosl2.nurbs import (
    nurbs_curve, nurbs_patch_points, nurbs_vnf, nurbs_elevate_degree, is_nurbs_patch,
)
from bosl2.paths import Path, Path3D
from bosl2.vnf import VNF


CTRL3 = [[0, 0, 0], [10, 20, 5], [30, -10, 10], [50, 20, 0], [60, 0, 15]]
CTRL2 = [[0, 0], [10, 20], [30, -10], [50, 20]]
PATCH = [[[-50, 50, 0], [-16, 50, 20], [16, 50, 20], [50, 50, 0]],
         [[-50, 16, 20], [-16, 16, 40], [16, 16, 40], [50, 16, 20]],
         [[-50, -16, 20], [-16, -16, 40], [16, -16, 40], [50, -16, 20]],
         [[-50, -50, 0], [-16, -50, 20], [16, -50, 20], [50, -50, 0]]]


# -- nurbs_curve --------------------------------------------------------------------------

def test_curve_returns_path3d_for_3d_control():
    c = nurbs_curve(CTRL3, 3, splinesteps=8)
    assert isinstance(c, Path3D)
    assert c.closed is False


def test_curve_returns_path_for_2d_control():
    c = nurbs_curve(CTRL2, 3, splinesteps=6)
    assert isinstance(c, Path) and not isinstance(c, Path3D)


def test_clamped_curve_interpolates_endpoints():
    c = nurbs_curve(CTRL3, 3, splinesteps=6)
    np.testing.assert_allclose(c[0], CTRL3[0], atol=1e-9)
    np.testing.assert_allclose(c[-1], CTRL3[-1], atol=1e-9)


def test_scalar_u_returns_single_point():
    pt = nurbs_curve(CTRL3, 3, u=0.5)
    assert not isinstance(pt, (Path, Path3D))
    assert len(pt) == 3 and all(isinstance(x, float) for x in pt)


def test_closed_curve_is_flagged_closed():
    c = nurbs_curve([[0, 0], [10, 0], [10, 10], [0, 10]], 2, splinesteps=4, type="closed")
    assert isinstance(c, Path) and c.closed is True


def test_u_and_splinesteps_are_exclusive():
    with pytest.raises(AssertionError):
        nurbs_curve(CTRL3, 3, splinesteps=8, u=[0, 0.5, 1])


def test_u_out_of_range_raises():
    with pytest.raises(AssertionError):
        nurbs_curve(CTRL3, 3, u=[0, 1.5])


def test_too_few_control_points_raises():
    with pytest.raises(AssertionError):
        nurbs_curve([[0, 0], [10, 0]], 3, splinesteps=4)  # degree 3 needs >= 4 points


def test_weights_pull_curve_toward_heavy_point():
    # a high weight on the middle control point pulls the curve toward it
    heavy = nurbs_curve([[0, 0], [10, 0], [10, 10]], 2, u=[0.5], weights=[1, 9, 1])[0]
    light = nurbs_curve([[0, 0], [10, 0], [10, 10]], 2, u=[0.5], weights=[1, 1, 1])[0]
    assert heavy[0] > light[0]  # pulled toward the [10,0] control point


def test_parameter_list_form():
    plist = ["clamped", 3, CTRL3, None, None, None]
    a = nurbs_curve(plist, splinesteps=5)
    b = nurbs_curve(CTRL3, 3, splinesteps=5)
    np.testing.assert_allclose(np.array(a), np.array(b), atol=1e-9)


# -- surfaces -----------------------------------------------------------------------------

def test_is_nurbs_patch():
    assert is_nurbs_patch(PATCH)
    assert not is_nurbs_patch([[0, 0], [1, 1]])          # a path, not a patch
    assert not is_nurbs_patch([1, 2, 3])


def test_patch_points_grid_shape():
    grid = nurbs_patch_points(PATCH, 3, splinesteps=3)
    assert len(grid) > 3 and len(grid[0]) > 3
    assert all(len(pt) == 3 for row in grid for pt in row)


def test_patch_points_uv_form():
    grid = nurbs_patch_points(PATCH, 3, u=[0, 0.5, 1], v=[0, 0.5, 1])
    assert len(grid) == 3 and len(grid[0]) == 3
    # the [0,0] corner interpolates the corner control point (clamped both ways)
    np.testing.assert_allclose(grid[0][0], PATCH[0][0], atol=1e-9)


def test_patch_mixed_degree():
    grid = nurbs_patch_points(PATCH, [3, 2], splinesteps=[2, 3])
    assert len(grid) > 0 and len(grid[0]) > 0


def test_nurbs_vnf_returns_vnf():
    assert isinstance(nurbs_vnf(PATCH, 3, splinesteps=4), VNF)


def test_nurbs_vnf_parameter_list():
    plist = ["clamped", 3, PATCH, None, None, None]
    assert isinstance(nurbs_vnf(plist, splinesteps=4), VNF)


def test_nurbs_vnf_caps_require_closed_clamped():
    with pytest.raises(AssertionError):
        nurbs_vnf(PATCH, 3, type="clamped", caps=True)  # both clamped -> no caps allowed


# -- degree elevation ---------------------------------------------------------------------

def test_elevate_raises_degree_and_count():
    el = nurbs_elevate_degree(CTRL2, 3)
    assert el[0] == "clamped"
    assert el[1] == 4                 # degree raised 3 -> 4
    assert len(el[2]) == len(CTRL2) + 1  # one more control point per elevation


def test_elevate_times():
    el = nurbs_elevate_degree(CTRL2, 3, times=2)
    assert el[1] == 5


def test_elevate_preserves_the_curve():
    # elevating degree must not change the geometry of the curve
    before = np.array(nurbs_curve(CTRL2, 3, splinesteps=8))
    el = nurbs_elevate_degree(CTRL2, 3)
    after = np.array(nurbs_curve(el[2], el[1], splinesteps=8))
    np.testing.assert_allclose(before, after, atol=1e-6)


def test_elevate_open_type_only():
    with pytest.raises(AssertionError):
        nurbs_elevate_degree(CTRL2, 3, type="closed")
