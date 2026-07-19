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
    path_sweep2d,
    rot_resample,
    rotate_sweep,
    skin,
    slice_profiles,
    spiral_sweep,
    subdivide_and_slice,
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


# -- skin ---------------------------------------------------------------------------------

def test_slice_profiles_inserts_intermediates():
    a = [[0, 0], [1, 0], [1, 1]]
    b = [[0, 2], [1, 2], [1, 3]]
    out = slice_profiles([a, b], 3)  # 3 interpolated + final = 5 profiles
    assert len(out) == 5
    np.testing.assert_allclose(out[0], a)
    np.testing.assert_allclose(out[-1], b)


def test_skin_two_profiles():
    vnf = skin([_circle(6), [[-8, -8], [8, -8], [8, 8], [-8, 8]]], slices=10, z=[0, 25])
    assert _valid(vnf)
    assert vnf.volume() > 0  # winding fixed to outward


def test_skin_reindex_method():
    vnf = skin([_circle(6), [[-8, -8], [8, -8], [8, 8], [-8, 8]]], slices=8, method="reindex", z=[0, 20])
    assert _valid(vnf) and vnf.volume() > 0


def test_skin_three_profiles():
    vnf = skin([_circle(4), _circle(8), _circle(4)], slices=5, z=[0, 15, 30])
    assert _valid(vnf) and vnf.volume() > 0


def test_skin_closed_stack():
    profs = [_circle(4), [[-6, -6], [6, -6], [6, 6], [-6, 6]], _circle(4), [[-6, -6], [6, -6], [6, 6], [-6, 6]]]
    vnf = skin(profs, slices=3, closed=True, z=[0, 10, 20, 30])
    assert _valid(vnf)


def test_skin_rejects_unsupported_method():
    with pytest.raises(AssertionError):
        skin([_circle(4), _circle(6)], slices=2, method="distance", z=[0, 10])


def test_skin_needs_two_profiles():
    with pytest.raises(AssertionError):
        skin([_circle(4)], slices=2, z=[0])


# -- linear_sweep -------------------------------------------------------------------------

def test_linear_sweep_plain_box_volume():
    sq = [[-10, -10], [10, -10], [10, 10], [-10, 10]]
    vnf = linear_sweep(sq, height=5)
    assert _valid(vnf)
    assert math.isclose(vnf.volume(), 20 * 20 * 5, rel_tol=1e-6)  # 2000


def test_linear_sweep_twist_scale():
    sq = [[-10, -10], [10, -10], [10, 10], [-10, 10]]
    vnf = linear_sweep(sq, height=40, twist=120, scale=0.4)
    assert _valid(vnf) and vnf.volume() > 0


def test_linear_sweep_center_vs_base():
    sq = [[-5, -5], [5, -5], [5, 5], [-5, 5]]
    base = linear_sweep(sq, height=10)
    centered = linear_sweep(sq, height=10, center=True)
    bz = [v[2] for v in base.vertices]
    cz = [v[2] for v in centered.vertices]
    assert math.isclose(min(bz), 0.0, abs_tol=1e-9) and math.isclose(max(bz), 10.0, abs_tol=1e-9)
    assert math.isclose(min(cz), -5.0, abs_tol=1e-9) and math.isclose(max(cz), 5.0, abs_tol=1e-9)


# -- rotate_sweep -------------------------------------------------------------------------

PROFILE = [[4, -10], [12, -10], [12, 10], [4, 10]]


def test_rotate_sweep_full():
    vnf = rotate_sweep(PROFILE, 360)
    assert _valid(vnf) and vnf.volume() > 0


def test_rotate_sweep_partial_has_caps():
    vnf = rotate_sweep(PROFILE, 270)
    assert _valid(vnf) and vnf.volume() > 0


def test_rotate_sweep_rejects_bad_angle():
    with pytest.raises(AssertionError):
        rotate_sweep(PROFILE, 400)


# -- spiral_sweep -------------------------------------------------------------------------

def test_spiral_sweep_coil():
    section = [[-1.2, -1.2], [1.2, -1.2], [1.2, 1.2], [-1.2, 1.2]]
    vnf = spiral_sweep(section, h=40, r=12, turns=5)
    assert _valid(vnf) and vnf.volume() > 0


def test_spiral_sweep_conical_taper():
    section = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    vnf = spiral_sweep(section, h=30, r1=15, r2=5, turns=4)
    assert _valid(vnf) and vnf.volume() > 0


# -- path_sweep2d -------------------------------------------------------------------------

def test_path_sweep2d_open():
    shape = [[-2, -2], [2, -2], [2, 2], [-2, 2]]
    path = [[t, 8 * math.sin(t / 12)] for t in range(0, 90, 3)]
    vnf = path_sweep2d(shape, path)
    assert _valid(vnf) and vnf.volume() > 0


def test_path_sweep2d_closed_loop():
    shape = [[-1, -2], [1, -2], [1, 2], [-1, 2]]
    ring = [[20 * math.cos(t), 20 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 32, endpoint=False)]
    vnf = path_sweep2d(shape, ring, closed=True)
    assert _valid(vnf) and vnf.volume() > 0


# -- subdivide_and_slice ------------------------------------------------------------------

def test_subdivide_and_slice_equalizes_and_slices():
    profs = subdivide_and_slice([[[0, 0], [1, 0], [1, 1]], [[0, 2], [2, 2], [2, 3]]], slices=3, numpoints=6)
    assert len(profs) == 5  # 3 interpolated + 2 endpoints
    assert all(len(p) == 6 for p in profs)


# -- rot_resample -------------------------------------------------------------------------

def test_rot_resample_changes_count_and_sweeps():
    sq = [[-3, -3], [3, -3], [3, 3], [-3, 3]]
    curve = [[0, 0, 0], [10, 0, 5], [10, 10, 10], [0, 10, 15]]
    tl = path_sweep(sq, curve, transforms=True)
    out = rot_resample(tl, n=20)
    assert len(out) == 20
    assert np.asarray(out[0]).shape == (4, 4)
    assert _valid(sweep(sq, out))


def test_rot_resample_count_method():
    sq = [[-2, -2], [2, -2], [2, 2], [-2, 2]]
    tl = path_sweep(sq, [[0, 0, 0], [0, 0, 10], [0, 0, 20]], transforms=True)
    out = rot_resample(tl, n=5, method="count")
    assert len(out) == 5 * 2 + 1  # samples-per-gap * gaps + 1


def test_rot_resample_rejects_even_smoothlen():
    tl = path_sweep([[-1, -1], [1, -1], [1, 1], [-1, 1]], [[0, 0, 0], [0, 0, 10]], transforms=True)
    with pytest.raises(AssertionError):
        rot_resample(tl, n=6, smoothlen=2)
