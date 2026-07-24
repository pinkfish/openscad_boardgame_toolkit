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

"""Tests for bosl2.paths.Path3D: the 3-D path object -- construction, measurement, the 3-D
transforms (move / directional / scale / rotate / mirror), resampling/cutting, and the drop-to-2-D
conversion. The numeric kernels are shared with Path (and pinned to real BOSL2 elsewhere); these
tests focus on the 3-D object surface."""

import math

import numpy as np
import pytest

from bosl2.paths import Path, Path3D


SQUARE_LOOP = [[0, 0, 0], [10, 0, 0], [10, 10, 5], [0, 10, 5]]


def test_construction_requires_3d_points():
    p = Path3D(SQUARE_LOOP)
    assert isinstance(p, list) and len(p) == 4
    assert p[0] == [0.0, 0.0, 0.0]
    with pytest.raises(AssertionError):
        Path3D([[0, 0], [1, 1]])  # 2-D points rejected


def test_closed_flag_and_repr():
    assert Path3D(SQUARE_LOOP).closed is True
    assert Path3D(SQUARE_LOOP, closed=False).closed is False
    assert "Path3D" in repr(Path3D(SQUARE_LOOP))


def test_array_and_bounds():
    p = Path3D(SQUARE_LOOP)
    assert p.array.shape == (4, 3)
    np.testing.assert_allclose(p.bounds(), [[0, 0, 0], [10, 10, 5]], atol=1e-9)


def test_perimeter_open_vs_closed():
    line = Path3D([[0, 0, 0], [0, 0, 10], [0, 0, 30]], closed=False)
    assert math.isclose(line.perimeter(), 30.0, abs_tol=1e-9)
    tri = Path3D([[0, 0, 0], [3, 0, 0], [3, 4, 0]], closed=True)
    assert math.isclose(tri.perimeter(), 3 + 4 + 5, abs_tol=1e-9)  # closed adds the 5 hypotenuse


def test_segment_lengths_and_fractions():
    line = Path3D([[0, 0, 0], [0, 0, 10], [0, 0, 40]], closed=False)
    np.testing.assert_allclose(line.segment_lengths(), [10, 30], atol=1e-9)
    np.testing.assert_allclose(line.length_fractions(), [0, 0.25, 1.0], atol=1e-9)


def test_translate_and_directional_moves():
    p = Path3D([[0, 0, 0]], closed=False)
    np.testing.assert_allclose(p.translate([1, 2, 3])[0], [1, 2, 3], atol=1e-9)
    np.testing.assert_allclose(p.move([1, 2, 3])[0], [1, 2, 3], atol=1e-9)
    np.testing.assert_allclose(p.right(5)[0], [5, 0, 0], atol=1e-9)
    np.testing.assert_allclose(p.left(5)[0], [-5, 0, 0], atol=1e-9)
    np.testing.assert_allclose(p.back(5)[0], [0, 5, 0], atol=1e-9)
    np.testing.assert_allclose(p.forward(5)[0], [0, -5, 0], atol=1e-9)
    np.testing.assert_allclose(p.up(5)[0], [0, 0, 5], atol=1e-9)
    np.testing.assert_allclose(p.down(5)[0], [0, 0, -5], atol=1e-9)


def test_scale_scalar_and_vector():
    p = Path3D([[1, 2, 3]], closed=False)
    np.testing.assert_allclose(p.scale(2)[0], [2, 4, 6], atol=1e-9)
    np.testing.assert_allclose(p.scale([1, 0, 3])[0], [1, 0, 9], atol=1e-9)


def test_rotate_about_z_axis_and_euler():
    p = Path3D([[1, 0, 0]], closed=False)
    np.testing.assert_allclose(p.rotate(90)[0], [0, 1, 0], atol=1e-9)          # scalar -> Z
    np.testing.assert_allclose(p.rotate(90, [1, 0, 0])[0], [1, 0, 0], atol=1e-9)  # about its own axis
    np.testing.assert_allclose(p.rotate([0, 0, 90])[0], [0, 1, 0], atol=1e-9)  # euler Z
    z_up = Path3D([[0, 0, 1]], closed=False)
    np.testing.assert_allclose(z_up.rotate([90, 0, 0])[0], [0, -1, 0], atol=1e-9)  # euler X: +Z -> -Y


def test_mirror_across_plane():
    p = Path3D([[1, 2, 3]], closed=False)
    np.testing.assert_allclose(p.mirror([0, 0, 1])[0], [1, 2, -3], atol=1e-9)
    np.testing.assert_allclose(p.mirror([1, 0, 0])[0], [-1, 2, 3], atol=1e-9)


def test_reverse_close_cleanup_dedup():
    p = Path3D([[0, 0, 0], [1, 0, 0], [1, 1, 1]], closed=False)
    np.testing.assert_allclose(p.reversed_path()[0], [1, 1, 1], atol=1e-9)
    closed = p.close()
    np.testing.assert_allclose(closed[-1], [0, 0, 0], atol=1e-9)  # start point appended
    assert len(closed.cleanup()) == 3  # duplicate closing point dropped
    dd = Path3D([[0, 0, 0], [0, 0, 0], [1, 0, 0]], closed=False).deduplicated()
    assert len(dd) == 2


def test_resample_and_subdivide_keep_3d():
    p = Path3D([[0, 0, 0], [0, 0, 30]], closed=False)
    r = p.resample(n=7)
    assert isinstance(r, Path3D) and len(r) == 7
    assert r.array.shape[1] == 3
    s = p.subdivide(n=4)
    assert isinstance(s, Path3D) and s.array.shape[1] == 3


def test_cut_returns_path3d_subpaths():
    line = Path3D([[0, 0, 0], [0, 0, 40]], closed=False)
    parts = line.cut([10.0])
    assert len(parts) == 2
    assert all(isinstance(pt, Path3D) for pt in parts)


def test_tangents_normals_curvature_torsion_shapes():
    p = Path3D([[math.cos(t), math.sin(t), t / 3] for t in np.linspace(0, 2 * math.pi, 24)],
               closed=False)
    assert p.tangents().shape == (24, 3)
    assert p.normals().shape == (24, 3)
    assert p.curvature().shape == (24,)
    assert p.torsion().shape == (24,)


def test_closest_point():
    line = Path3D([[0, 0, 0], [0, 0, 10]], closed=False)
    seg, pt = line.closest_point([1, 0, 5])
    np.testing.assert_allclose(pt, [0, 0, 5], atol=1e-9)


def test_path2d_drops_z():
    p = Path3D([[1, 2, 9], [3, 4, 8]], closed=False)
    flat = p.path2d()
    assert isinstance(flat, Path)
    np.testing.assert_allclose(flat, [[1, 2], [3, 4]], atol=1e-9)
    assert flat.closed is False


def test_stroke_and_dashed_build():
    p = Path3D([[0, 0, 0], [20, 0, 0], [20, 20, 10]], closed=False)
    assert p.stroke(width=3) is not None
    dashes = p.dashed_stroke(dashpat=[5, 5])
    assert all(isinstance(d, Path3D) for d in dashes)
