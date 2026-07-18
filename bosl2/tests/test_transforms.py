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

"""Tests for bosl2/transforms.py: polar_to_xy and the affine reorient/apply machinery."""

import math

import numpy as np

from bosl2.constants import CENTER, LEFT, UP
from bosl2.transforms import apply, axis_angle_matrix, polar_to_xy, reorient, rot_from_to


def test_polar_to_xy():
    np.testing.assert_allclose(polar_to_xy(1, 0), [1, 0], atol=1e-12)
    np.testing.assert_allclose(polar_to_xy(1, 90), [0, 1], atol=1e-12)
    np.testing.assert_allclose(polar_to_xy(2, 180), [-2, 0], atol=1e-12)


def test_rot_from_to_perpendicular():
    ang, axis = rot_from_to([1, 0, 0], [0, 1, 0])
    assert math.isclose(ang, 90.0)
    np.testing.assert_allclose(np.abs(axis), [0, 0, 1], atol=1e-9)


def test_rot_from_to_parallel_is_zero():
    ang, _ = rot_from_to([0, 0, 1], [0, 0, 5])
    assert math.isclose(ang, 0.0, abs_tol=1e-9)


def test_rot_from_to_antiparallel_is_180():
    ang, axis = rot_from_to([0, 0, 1], [0, 0, -1])
    assert math.isclose(ang, 180.0)
    assert math.isclose(float(np.linalg.norm(axis)), 1.0)


def test_axis_angle_matrix_is_rotation():
    m = axis_angle_matrix(90, [0, 0, 1])
    np.testing.assert_allclose(m @ m.T, np.eye(3), atol=1e-9)
    assert math.isclose(float(np.linalg.det(m)), 1.0)
    np.testing.assert_allclose(m @ [1, 0, 0], [0, 1, 0], atol=1e-9)


def test_reorient_identity_is_noop():
    m = reorient(anchor=CENTER, spin=0, orient=UP, size=[10, 20, 30])
    pts = [[1, 2, 3], [-4, 5, -6]]
    np.testing.assert_allclose(apply(m, pts), pts, atol=1e-9)


def test_reorient_orient_left_rotates_up_to_left():
    m = reorient(anchor=CENTER, orient=LEFT, size=[1, 1, 1])
    # a point on +Z should map onto -X (UP -> LEFT)
    got = apply(m, [0, 0, 1])
    np.testing.assert_allclose(got, [-1, 0, 0], atol=1e-9)


def test_apply_single_point_vs_list():
    m = np.eye(4)
    m[:3, 3] = [10, 20, 30]  # pure translation
    np.testing.assert_allclose(apply(m, [1, 1, 1]), [11, 21, 31])
    np.testing.assert_allclose(apply(m, [[0, 0, 0], [1, 2, 3]]), [[10, 20, 30], [11, 22, 33]])


def test_apply_returns_plain_lists():
    out = apply(np.eye(4), [[1, 2, 3]])
    assert isinstance(out, list) and isinstance(out[0], list)
