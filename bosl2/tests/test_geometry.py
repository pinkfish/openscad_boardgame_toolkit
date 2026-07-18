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

"""Tests for bosl2/geometry.py: cross, collinearity, line ops, bounds, intersection."""

import math

import numpy as np

from bosl2.geometry import (
    cross,
    general_line_intersection,
    is_collinear,
    line_closest_point,
    line_normal,
    pointlist_bounds,
    _is_point_on_segment,
)


def test_cross_2d_is_scalar_z():
    assert cross([1, 0], [0, 1]) == 1
    assert cross([0, 1], [1, 0]) == -1


def test_cross_3d_is_vector():
    np.testing.assert_allclose(cross([1, 0, 0], [0, 1, 0]), [0, 0, 1])


def test_is_collinear_true():
    assert is_collinear([0, 0], [1, 1], [2, 2])
    assert is_collinear([0, 0], [3, 0], [10, 0])


def test_is_collinear_false():
    assert not is_collinear([0, 0], [1, 0], [0, 1])


def test_line_normal_is_unit_and_perpendicular():
    n = line_normal([0, 0], [10, 0])
    assert math.isclose(float(np.linalg.norm(n)), 1.0)
    assert abs(float(np.dot(n, [1, 0]))) < 1e-9


def test_line_closest_point_clamps_to_segment():
    seg = [[0, 0], [10, 0]]
    np.testing.assert_allclose(line_closest_point(seg, [5, 5]), [5, 0], atol=1e-9)
    # points beyond the ends clamp to the nearest endpoint
    np.testing.assert_allclose(line_closest_point(seg, [-3, 2]), [0, 0], atol=1e-9)
    np.testing.assert_allclose(line_closest_point(seg, [15, 3]), [10, 0], atol=1e-9)


def test_pointlist_bounds():
    b = pointlist_bounds([[0, 0], [3, 4], [-1, 2]])
    np.testing.assert_allclose(b, [[-1, 0], [3, 4]])


def test_general_line_intersection_crossing():
    res = general_line_intersection([[0, 0], [10, 0]], [[5, -5], [5, 5]])
    assert res is not None
    pt, t, u = res
    np.testing.assert_allclose(pt, [5, 0], atol=1e-9)
    assert math.isclose(t, 0.5)
    assert math.isclose(u, 0.5)


def test_general_line_intersection_parallel_is_none():
    assert general_line_intersection([[0, 0], [10, 0]], [[0, 1], [10, 1]]) is None


def test_is_point_on_segment():
    seg = [np.array([0.0, 0.0]), np.array([10.0, 0.0])]
    assert _is_point_on_segment(np.array([5.0, 0.0]), seg)
    assert not _is_point_on_segment(np.array([5.0, 1.0]), seg)
    assert not _is_point_on_segment(np.array([15.0, 0.0]), seg)
