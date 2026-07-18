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

"""Tests for bosl2/skin.py: frame_map, sweep and path_sweep frame methods."""

import math

import numpy as np
import pytest

from bosl2.skin import (
    clockwise_polygon,
    frame_map,
    linear_sweep,
    path3d,
    path_sweep,
    rotate_sweep,
    skin,
    slice_profiles,
    spiral_sweep,
    sweep,
)

SQUARE = [[-1, -1], [1, -1], [1, 1], [-1, 1]]


def _valid(vnf):
    return not vnf.faces or max(i for f in vnf.faces for i in f) < len(vnf.vertices)


def _circle(r, n=24):
    return [[r * math.cos(t), r * math.sin(t)] for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]


def test_path3d_pads_z():
    assert path3d([[1, 2], [3, 4]]) == [[1, 2, 0], [3, 4, 0]]
    assert path3d([[1, 2, 3]]) == [[1, 2, 3]]


def test_clockwise_polygon():
    ccw = [[0, 0], [1, 0], [1, 1], [0, 1]]
    assert clockwise_polygon(ccw) == list(reversed(ccw))  # ccw gets reversed
    cw = list(reversed(ccw))
    assert clockwise_polygon(cw) == cw  # already clockwise, unchanged


def test_frame_map_orthonormal():
    m = frame_map(y=[0, 1, 0], z=[0, 0, 1])
    r = m[:3, :3]
    np.testing.assert_allclose(r @ r.T, np.eye(3), atol=1e-9)
    assert math.isclose(float(np.linalg.det(r)), 1.0)


def test_frame_map_fills_third_axis():
    m = frame_map(y=[0, 1, 0], z=[0, 0, 1])  # x should be +X
    np.testing.assert_allclose(m[:3, 0], [1, 0, 0], atol=1e-9)


def test_straight_sweep_counts():
    vnf = path_sweep(SQUARE, [[0, 0, 0], [0, 0, 5], [0, 0, 10]])
    assert len(vnf.vertices) == 12  # 4 shape pts x 3 profiles
    assert _valid(vnf)


def test_sweep_open_has_caps_closed_does_not():
    line = [[0, 0, 0], [0, 0, 5], [0, 0, 10]]
    open_faces = len(path_sweep(SQUARE, line, caps=True).faces)
    nocap_faces = len(path_sweep(SQUARE, line, caps=False).faces)
    assert open_faces == nocap_faces + 2  # two flat end caps


@pytest.mark.parametrize("method", ["incremental", "natural"])
def test_curved_sweep_methods(method):
    curve = [[math.cos(t) * 10, math.sin(t) * 10, t * 2] for t in np.linspace(0, math.pi, 10)]
    vnf = path_sweep(SQUARE, curve, method=method)
    assert len(vnf.vertices) == 40
    assert _valid(vnf)


def test_manual_method_with_normals():
    path = [[0, 0, 0], [0, 0, 5], [0, 0, 10]]
    normals = [[1, 0, 0]] * 3
    vnf = path_sweep(SQUARE, path, method="manual", normal=normals)
    assert _valid(vnf)


def test_closed_sweep_has_no_caps():
    circ = [[math.cos(t) * 20, math.sin(t) * 20, 0] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    vnf = path_sweep(SQUARE, circ, closed=True)
    assert _valid(vnf)
    # 25 profiles (closed adds the wrap) x 4 verts
    assert len(vnf.vertices) == 100


def test_transforms_mode_returns_matrices():
    tl = path_sweep(SQUARE, [[0, 0, 0], [0, 0, 5], [0, 0, 10]], transforms=True)
    assert len(tl) == 3
    assert np.asarray(tl[0]).shape == (4, 4)


def test_twist_and_scale_run():
    vnf = path_sweep(SQUARE, [[0, 0, 0], [0, 0, 5], [0, 0, 10]], twist=90, scale=2)
    assert _valid(vnf)


def test_unknown_method_raises():
    with pytest.raises(AssertionError):
        path_sweep(SQUARE, [[0, 0, 0], [0, 0, 5]], method="bogus")


def test_sweep_direct_from_transforms():
    ident = np.eye(4)
    up = np.eye(4)
    up[2, 3] = 10
    vnf = sweep(SQUARE, [ident, up])
    assert _valid(vnf)
