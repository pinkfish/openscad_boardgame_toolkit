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
from bosl2.transforms import (
    apply,
    axis_angle_matrix,
    polar_to_xy,
    reorient,
    rot_about_axis,
    rot_decode,
    rot_from_to,
    rot_inverse,
)


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


def test_rot_about_axis_through_point():
    m = rot_about_axis(90, [0, 0, 1], cp=[5, 0, 0])  # rotate 90 about the vertical line at x=5
    np.testing.assert_allclose(apply(m, [5, 0, 0]), [5, 0, 0], atol=1e-9)  # the axis point is fixed
    np.testing.assert_allclose(apply(m, [6, 0, 0]), [5, 1, 0], atol=1e-9)


def test_rot_inverse_undoes_transform():
    m = rot_about_axis(37, [0.3, 0.5, 0.8], cp=[2, -1, 4])
    np.testing.assert_allclose(rot_inverse(m) @ m, np.eye(4), atol=1e-9)


def test_rot_decode_round_trip():
    m = rot_about_axis(40, [0, 0, 1], cp=[5, 0, 0])
    angle, axis, cp, axial = rot_decode(m)
    assert math.isclose(angle, 40.0, abs_tol=1e-6)
    np.testing.assert_allclose(axis, [0, 0, 1], atol=1e-9)
    np.testing.assert_allclose(cp[:2], [5, 0], atol=1e-6)
    np.testing.assert_allclose(axial, [0, 0, 0], atol=1e-9)


def test_rot_decode_identity_is_zero_angle():
    angle, axis, cp, axial = rot_decode(np.eye(4))
    assert math.isclose(angle, 0.0, abs_tol=1e-9)


def test_rot_decode_axis_is_vec3():
    from bosl2.constants import Vec3

    _, axis, cp, axial = rot_decode(rot_about_axis(30, [1, 0, 0], cp=[0, 2, 0]))
    assert isinstance(axis, Vec3) and isinstance(cp, Vec3) and isinstance(axial, Vec3)
