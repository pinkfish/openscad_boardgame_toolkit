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

"""Tests for bosl2/distributors.py: the copier matrix generators and the Distributable methods on
Path / Path3D / Bosl2Solid. The matrices themselves are pinned to real BOSL2 in
tests/test_bosl2_reorient.py; here we check the object-level behaviour (what each host returns and
how the copies are placed). Native geometry is mocked, so Bosl2Solid tests assert type/union, not
mesh geometry (that is covered in test_stl_render.py)."""

import math

import numpy as np
import pytest

from bosl2 import distributors as D
from bosl2.paths import Path, Path3D
from bosl2.shapes3d import Bosl2Solid, cuboid


# -- matrix generators --------------------------------------------------------------------

def test_move_copies_matrices():
    mats = D.move_copies([[0, 0, 0], [10, 0, 0], [0, 5, 0]])
    assert len(mats) == 3
    np.testing.assert_allclose(mats[1][:3, 3], [10, 0, 0], atol=1e-9)  # translation column


def test_xcopies_centered_by_default():
    mats = D.xcopies(20, n=3)
    xs = sorted(m[0, 3] for m in mats)
    np.testing.assert_allclose(xs, [-20, 0, 20], atol=1e-9)  # centered on origin


def test_xcopies_explicit_positions():
    mats = D.xcopies([1, 2, 3, 5, 7])
    xs = [m[0, 3] for m in mats]
    np.testing.assert_allclose(xs, [1, 2, 3, 5, 7], atol=1e-9)


def test_grid_copies_count_and_stagger():
    assert len(D.grid_copies(n=[3, 4], spacing=10)) == 12
    # a staggered grid drops/offsets alternate columns per row
    assert len(D.grid_copies(spacing=8, n=[4, 3], stagger=True)) == 6


def test_grid_copies_inside_polygon_filters():
    # only centers inside the small square survive
    poly = [[-6, -6], [6, -6], [6, 6], [-6, 6]]
    mats = D.grid_copies(spacing=5, n=[9, 9], inside=poly)
    assert 0 < len(mats) < 81
    for m in mats:
        assert -6 <= m[0, 3] <= 6 and -6 <= m[1, 3] <= 6


def test_arc_copies_positions_on_circle():
    mats = D.arc_copies(n=4, r=10, sa=0, ea=360)
    # first copy sits on +X at radius 10
    np.testing.assert_allclose(mats[0][:3, 3], [10, 0, 0], atol=1e-9)


def test_mirror_copy_is_original_plus_reflection():
    mats = D.mirror_copy([1, 0, 0])
    assert len(mats) == 2
    np.testing.assert_allclose(mats[0], np.eye(4), atol=1e-9)          # the original
    np.testing.assert_allclose(mats[1][:3, :3], np.diag([-1, 1, 1]), atol=1e-9)  # X reflection


# -- Path (2-D) returns a list of Path copies ---------------------------------------------

SQUARE = Path([[0, 0], [10, 0], [10, 10], [0, 10]])


def test_path_xcopies_returns_paths():
    copies = SQUARE.xcopies(20, n=3)
    assert isinstance(copies, list) and len(copies) == 3
    assert all(isinstance(c, Path) for c in copies)
    # middle copy is the original, right copy is shifted +20 in X
    np.testing.assert_allclose(copies[2][0], [20, 0], atol=1e-9)


def test_path_grid_and_arc_stay_2d():
    assert len(SQUARE.grid_copies(n=[2, 3], spacing=25)) == 6
    assert all(isinstance(c, Path) for c in SQUARE.arc_copies(n=5, r=40))


def test_path_zrot_copies_in_plane():
    copies = SQUARE.zrot_copies(n=4)
    assert len(copies) == 4 and all(isinstance(c, Path) for c in copies)


def test_path_out_of_plane_copier_raises():
    for call in (lambda: SQUARE.zcopies(10, n=3),
                 lambda: SQUARE.xrot_copies(n=4, r=10),
                 lambda: SQUARE.sphere_copies(n=8, r=20)):
        with pytest.raises(AssertionError):
            call()


def test_path_mirror_copy_2d():
    copies = SQUARE.xflip_copy(x=20)
    assert len(copies) == 2 and all(isinstance(c, Path) for c in copies)


# -- Path3D returns a list of Path3D copies -----------------------------------------------

SEG3 = Path3D([[0, 0, 0], [10, 0, 0], [10, 10, 5]], closed=False)


def test_path3d_zcopies():
    copies = SEG3.zcopies(15, n=3)
    assert len(copies) == 3 and all(isinstance(c, Path3D) for c in copies)
    zs = sorted(c[0][2] for c in copies)
    np.testing.assert_allclose(zs, [-15, 0, 15], atol=1e-9)  # centered along Z


def test_path3d_xrot_copies_ring():
    copies = SEG3.xrot_copies(n=6, r=20)
    assert len(copies) == 6 and all(isinstance(c, Path3D) for c in copies)


def test_path3d_sphere_copies():
    copies = SEG3.sphere_copies(n=10, r=30)
    assert len(copies) == 10 and all(isinstance(c, Path3D) for c in copies)


# -- Bosl2Solid returns a unioned solid ---------------------------------------------------

def test_solid_grid_copies_returns_solid():
    assert isinstance(cuboid([10, 10, 10]).grid_copies(n=[3, 3], spacing=20), Bosl2Solid)


def test_solid_ring_and_flip_return_solid():
    box = cuboid([10, 10, 10])
    assert isinstance(box.zrot_copies(n=6, r=30), Bosl2Solid)
    assert isinstance(box.right(20).xflip_copy(), Bosl2Solid)
    assert isinstance(box.move_copies([[0, 0, 0], [20, 0, 0], [0, 20, 0]]), Bosl2Solid)


def test_solid_path_copies_returns_solid():
    box = cuboid([4, 4, 4])
    path = Path([[0, 0], [30, 0], [30, 30]])
    assert isinstance(box.path_copies(path, n=6), Bosl2Solid)


# -- distribute (list of distinct children) -----------------------------------------------

def test_distribute_returns_solid():
    a, b, c = cuboid([10, 10, 10]), cuboid([20, 20, 20]), cuboid([5, 5, 5])
    assert isinstance(D.xdistribute([a, b, c], spacing=5), Bosl2Solid)
    assert isinstance(D.ydistribute([a, b], sizes=[10, 20]), Bosl2Solid)
    assert isinstance(D.zdistribute([a, b, c], l=100), Bosl2Solid)
