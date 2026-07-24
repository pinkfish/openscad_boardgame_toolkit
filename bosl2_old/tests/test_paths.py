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

"""Tests for bosl2/paths.py: the Path list-subclass and its private static kernels."""

import math

import numpy as np
import pytest

from bosl2.paths import Path

SQUARE = [[0, 0], [80, 0], [80, 60], [0, 60]]
UNIT = [[0, 0], [10, 0], [10, 10], [0, 10]]


# -- construction / drop-in list behaviour ------------------------------------------------

def test_is_a_list_of_plain_floats():
    p = Path(np.asarray(SQUARE, dtype=float))
    assert isinstance(p, list)
    assert p == [[float(x), float(y)] for x, y in SQUARE]
    for pt in p:
        for v in pt:
            assert isinstance(v, float)


def test_rejects_non_xy_points():
    with pytest.raises(AssertionError):
        Path([[0, 0, 0], [1, 1, 1]])


def test_empty_path():
    assert len(Path()) == 0


def test_array_property():
    assert Path(SQUARE).array.shape == (4, 2)


# -- measurement --------------------------------------------------------------------------

def test_bounds_width_length():
    p = Path(SQUARE)
    np.testing.assert_allclose(p.bounds(), [[0, 0], [80, 60]])
    assert p.width == 80
    assert p.length_y == 60


def test_area():
    assert Path(SQUARE).area() == 4800
    assert Path(SQUARE).area(signed=True) == 4800  # CCW is positive
    assert Path(list(reversed(SQUARE))).area(signed=True) == -4800


def test_is_clockwise():
    assert not Path(SQUARE).is_clockwise()
    assert Path(list(reversed(SQUARE))).is_clockwise()


def test_perimeter_closed_vs_open():
    assert Path(SQUARE).perimeter() == 280
    assert Path(SQUARE, closed=False).perimeter() == 220  # three segments, no closing edge


def test_segment_lengths_and_fractions():
    p = Path(SQUARE)
    np.testing.assert_allclose(p.segment_lengths(), [80, 60, 80, 60])
    fr = p.length_fractions()
    assert math.isclose(fr[0], 0.0) and math.isclose(fr[-1], 1.0)


def test_is_closed_property():
    assert Path([[0, 0], [10, 0], [10, 10], [0, 0]]).is_closed is True
    assert Path(SQUARE).is_closed is False  # endpoints differ


def test_contains_only_when_closed():
    p = Path(SQUARE)
    assert p.contains([40, 30]) is True
    assert p.contains([100, 100]) is False
    assert Path(SQUARE, closed=False).contains([40, 30]) is False


def test_is_simple():
    assert Path(SQUARE).is_simple()
    figure8 = [[0, 0], [2, 2], [0, 2], [2, 0]]
    assert not Path(figure8).is_simple()


def test_closest_point():
    seg, pt = Path(SQUARE).closest_point([40, -5])
    assert seg == 0
    np.testing.assert_allclose(pt, [40, 0], atol=1e-9)


# -- tangents / normals / curvature -------------------------------------------------------

def test_tangents_are_unit():
    t = Path(SQUARE).tangents()
    np.testing.assert_allclose(np.linalg.norm(t, axis=1), np.ones(4), atol=1e-9)


def test_normals_perpendicular_to_tangents():
    p = Path(SQUARE)
    t, n = p.tangents(), p.normals()
    for i in range(len(p)):
        assert abs(float(np.dot(t[i], n[i]))) < 1e-9


def test_curvature_of_straightish_polygon():
    c = Path(SQUARE).curvature()
    assert c.shape == (4,)


# -- derived paths ------------------------------------------------------------------------

def test_offset_shrinks_area():
    assert math.isclose(Path(UNIT).offset(r=-1).area(), 64.0, abs_tol=1e-6)
    assert math.isclose(Path(UNIT).offset(delta=-1).area(), 64.0, abs_tol=1e-6)


def test_offset_returns_path():
    assert isinstance(Path(UNIT).offset(r=-1), Path)


def test_offset_needs_exactly_one_of_r_delta():
    with pytest.raises(AssertionError):
        Path(UNIT).offset()
    with pytest.raises(AssertionError):
        Path(UNIT).offset(r=1, delta=1)


def test_round_corners_inserts_points():
    out = Path(UNIT).round_corners(radius=2)
    assert isinstance(out, Path)
    assert len(out) > len(UNIT)


def test_merge_collinear_drops_midpoints():
    p = Path([[0, 0], [5, 0], [10, 0], [10, 10], [0, 10]])
    assert len(p.merge_collinear()) == 4


def test_deduplicated():
    p = Path([[0, 0], [0, 0], [1, 0], [1, 1]])
    assert len(p.deduplicated()) == 3


def test_reversed_path():
    p = Path(SQUARE).reversed_path()
    np.testing.assert_allclose(p[0], SQUARE[-1])


def test_close_and_cleanup():
    open_sq = Path(SQUARE)
    closed = open_sq.close()
    np.testing.assert_allclose(closed[-1], closed[0])
    assert len(closed) == 5
    np.testing.assert_allclose(closed.cleanup(), open_sq)


def test_subdivide_adds_points():
    out = Path(SQUARE).subdivide(n=8)
    assert len(out) == 8


def test_resample_to_n_points():
    out = Path(SQUARE).resample(n=12)
    assert len(out) == 12


def test_cut_splits_into_subpaths():
    parts = Path(SQUARE).cut([100, 200])
    assert len(parts) == 3
    assert all(isinstance(p, Path) for p in parts)


def test_cut_points_along_open_path():
    pts = Path([[0, 0], [10, 0]], closed=False).cut_points([5])
    np.testing.assert_allclose(pts[0][0], [5, 0], atol=1e-9)


# -- transforms ---------------------------------------------------------------------------

def test_translate_and_move_alias():
    np.testing.assert_allclose(Path(UNIT).translate([1, 2])[0], [1, 2])
    np.testing.assert_allclose(Path(UNIT).move([1, 2])[0], [1, 2])


def test_directional_moves():
    p = Path([[1, 1]], closed=False)
    np.testing.assert_allclose(p.right(5)[0], [6, 1])
    np.testing.assert_allclose(p.left(5)[0], [-4, 1])
    np.testing.assert_allclose(p.back(5)[0], [1, 6])
    np.testing.assert_allclose(p.forward(5)[0], [1, -4])
    np.testing.assert_allclose(p.fwd(5)[0], [1, -4])


def test_rot_and_rotate_alias():
    np.testing.assert_allclose(Path([[1, 0]], closed=False).rot(90)[0], [0, 1], atol=1e-9)
    np.testing.assert_allclose(Path([[1, 0]], closed=False).rotate(90)[0], [0, 1], atol=1e-9)


def test_mirror_across_y_axis():
    np.testing.assert_allclose(Path([[3, 2]], closed=False).mirror([1, 0])[0], [-3, 2], atol=1e-9)


def test_yflip():
    np.testing.assert_allclose(Path([[3, 2]], closed=False).yflip()[0], [3, -2], atol=1e-9)


# -- conversion ---------------------------------------------------------------------------

def test_to_region():
    from bosl2.regions import Region

    r = Path(SQUARE).to_region()
    assert isinstance(r, Region) and len(r) == 1


def test_polygon_and_geometry_use_mock():
    assert Path(SQUARE).polygon() is not None
    assert Path(SQUARE).geometry() is not None


# -- splitting ----------------------------------------------------------------------------

def test_polygon_parts_of_simple_square():
    parts = Path(SQUARE).polygon_parts()
    assert len(parts) == 1
    assert all(isinstance(p, Path) for p in parts)


def test_split_at_self_crossings():
    figure8 = [[0, 0], [2, 2], [0, 2], [2, 0]]
    subs = Path(figure8).split_at_self_crossings()
    assert len(subs) >= 2


# -- private static kernels ---------------------------------------------------------------

def test_select_circular_index():
    assert Path._select([10, 20, 30], 4) == 20  # 4 % 3
    assert Path._select([10, 20, 30], -1) == 30
    assert Path._select([10, 20, 30], [0, 3, -1]) == [10, 10, 30]


def test_select_circular_slice_wraps():
    assert Path._select([0, 1, 2, 3], 2, 0) == [2, 3, 0]
    assert Path._select([0, 1, 2, 3], 1, 2) == [1, 2]


def test_slice_inclusive_clamped():
    assert Path._slice([0, 1, 2, 3, 4], 1, 3) == [1, 2, 3]
    assert Path._slice([0, 1, 2, 3, 4], 0, -1) == [0, 1, 2, 3, 4]
    assert Path._slice([0, 1, 2], 2, 0) == []


def test_pair():
    assert Path._pair([1, 2, 3]) == [(1, 2), (2, 3)]
    assert Path._pair([1, 2, 3], wrap=True) == [(1, 2), (2, 3), (3, 1)]
    assert Path._pair([1]) == []


def test_list_head_and_tail():
    assert Path._list_head([0, 1, 2, 3], 1) == [0, 1]
    assert Path._list_tail([0, 1, 2, 3], 2) == [2, 3]


def test_repeat():
    assert Path._repeat(5, 3) == [5, 5, 5]


def test_deduplicate_static():
    assert Path._deduplicate([[0, 0], [0, 0], [1, 1]]) == [[0, 0], [1, 1]]


def test_polygon_area_static():
    assert Path._polygon_area(SQUARE) == 4800
    assert Path._polygon_area([[0, 0], [1, 0]]) == 0  # too few points


def test_point_in_polygon_static():
    assert Path._point_in_polygon([40, 30], SQUARE) == 1
    assert Path._point_in_polygon([100, 100], SQUARE) == -1
    assert Path._point_in_polygon([0, 30], SQUARE) == 0  # on the boundary


def test_path_length_static_accepts_3d():
    # the static kernel works on raw 3-D arrays (used by shapes3d.path_text)
    assert math.isclose(Path._path_length([[0, 0, 0], [0, 0, 3], [0, 4, 3]]), 7.0)
