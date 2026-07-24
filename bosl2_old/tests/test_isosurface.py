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

"""Tests for bosl2/isosurface.py: the marching-cubes mesher, the metaball field primitives, and
metaballs(). The mb_* formulas are pinned to real BOSL2 in tests/test_bosl2_reorient.py; here we
check the field values against their closed forms and the meshes GEOMETRICALLY (a lone metaball is
a sphere; overlapping ones merge; a torus has a hole). Native VNF is mocked, so mesh volume/vertex
checks run on the pure-Python VNF, and real geometry is verified in test_stl_render.py."""

import math

import numpy as np
import pytest

from bosl2.isosurface import (isosurface, metaballs, mb_sphere, mb_cuboid, mb_torus, mb_capsule,
                             mb_disk, mb_octahedron, mb_connector, Metaball)


# -- field primitives ---------------------------------------------------------------------

def test_sphere_field_is_r_over_dist():
    f = mb_sphere(5)
    assert math.isclose(f([5, 0, 0]), 1.0, abs_tol=1e-9)     # on the surface
    assert math.isclose(f([10, 0, 0]), 0.5, abs_tol=1e-9)    # r/dist
    assert math.isclose(f([0, 3, 4]), 1.0, abs_tol=1e-9)     # dist=5


def test_negative_flips_sign():
    assert mb_sphere(5, negative=True)([10, 0, 0]) < 0


def test_influence_and_cutoff():
    # influence raises r/dist to the 1/influence power
    base = mb_sphere(5)([10, 0, 0])
    inf = mb_sphere(5, influence=2)([10, 0, 0])
    assert math.isclose(inf, base ** 0.5, abs_tol=1e-9)
    # cutoff zeroes the field beyond the cutoff distance
    assert mb_sphere(5, cutoff=8)([20, 0, 0]) == 0


def test_torus_field_hole():
    f = mb_torus(8, 2)
    assert math.isclose(f([10, 0, 0]), 1.0, abs_tol=1e-9)   # on the tube (dist from ring = 2)
    assert f([0, 0, 0]) < f([8, 0, 0])                       # center of hole is weaker than the ring


def test_capsule_field_straight_section():
    f = mb_capsule(24, 4)  # straight length 24-8=16, hl=8
    # anywhere along the straight axis the field is r/rxy
    assert math.isclose(f([4, 0, 0]), 1.0, abs_tol=1e-9)
    assert math.isclose(f([4, 0, 5]), 1.0, abs_tol=1e-9)     # still on the straight part (|z|<=8)


def test_cuboid_and_octahedron_build():
    assert isinstance(mb_cuboid(20)([10, 0, 0]), float)
    assert isinstance(mb_cuboid([16, 20, 24], 0.9)([8, 0, 0]), float)
    assert isinstance(mb_octahedron(20)([10, 0, 0]), float)


def test_connector_is_symmetric_capsule():
    f = mb_connector([-10, 0, 0], [10, 0, 0], 3)
    assert math.isclose(f([0, 3, 0]), 1.0, abs_tol=1e-9)     # 3 away from the axis midpoint
    assert math.isclose(f([5, 0, 3]), f([-5, 0, 3]), abs_tol=1e-9)  # symmetric


def test_metaball_vectorized_field():
    f = mb_sphere(5)
    vals = f.field(np.array([[5, 0, 0], [10, 0, 0], [0, 5, 0]]))
    np.testing.assert_allclose(vals, [1.0, 0.5, 1.0], atol=1e-9)


# -- isosurface meshing -------------------------------------------------------------------

def test_isosurface_sphere_volume():
    # f = R/|p|, isovalue 1 -> a sphere of radius R
    def sf(pts):
        return 8.0 / np.linalg.norm(pts, axis=1)
    vnf = isosurface(sf, 1, bounding_box=24, voxel_size=1.5)
    ideal = 4 / 3 * math.pi * 8 ** 3
    assert 0.9 * ideal < abs(vnf.volume()) < 1.05 * ideal
    assert len(vnf.faces) > 0


def test_isosurface_from_array():
    # a small precomputed field: a filled ball inside a grid
    n = 12
    xs = np.linspace(-6, 6, n)
    gx, gy, gz = np.meshgrid(xs, xs, xs, indexing="ij")
    field = 4.0 / np.sqrt(gx ** 2 + gy ** 2 + gz ** 2 + 1e-9)
    vnf = isosurface(field, 1, bounding_box=[[-6, -6, -6], [6, 6, 6]])
    assert len(vnf.faces) > 0


def test_isosurface_reverse_flips_winding():
    def sf(pts):
        return 8.0 / np.linalg.norm(pts, axis=1)
    a = isosurface(sf, 1, bounding_box=24, voxel_size=2)
    b = isosurface(sf, 1, bounding_box=24, voxel_size=2, reverse=True)
    assert np.sign(a.volume()) == -np.sign(b.volume())


# -- metaballs ----------------------------------------------------------------------------

def test_metaballs_single_sphere_volume():
    vnf = metaballs([([0, 0, 0], mb_sphere(8))],
                    bounding_box=[[-14, -14, -14], [14, 14, 14]], voxel_size=1.5)
    ideal = 4 / 3 * math.pi * 8 ** 3   # lone mb_sphere(8) at iso=1 -> sphere radius 8
    assert 0.9 * ideal < abs(vnf.volume()) < 1.05 * ideal


def test_metaballs_merge_is_bigger_than_parts():
    close = metaballs([([-6, 0, 0], mb_sphere(8)), ([6, 0, 0], mb_sphere(8))],
                      bounding_box=[[-24, -16, -16], [24, 16, 16]], voxel_size=2)
    one = metaballs([([0, 0, 0], mb_sphere(8))],
                    bounding_box=[[-16, -16, -16], [16, 16, 16]], voxel_size=2)
    # summed fields inflate the merged blob well past a single ball
    assert abs(close.volume()) > 2 * abs(one.volume())


def test_metaballs_flat_spec_form():
    paired = metaballs([([0, 0, 0], mb_sphere(8))],
                       bounding_box=[[-14, -14, -14], [14, 14, 14]], voxel_size=2)
    flat = metaballs([[0, 0, 0], mb_sphere(8)],
                     bounding_box=[[-14, -14, -14], [14, 14, 14]], voxel_size=2)
    assert math.isclose(paired.volume(), flat.volume(), rel_tol=1e-6)


def test_metaballs_voxel_count():
    vnf = metaballs([([0, 0, 0], mb_sphere(8))],
                    bounding_box=[[-14, -14, -14], [14, 14, 14]], voxel_count=8000)
    assert len(vnf.faces) > 0


def test_metaballs_scalar_bounding_box():
    vnf = metaballs([([0, 0, 0], mb_sphere(6))], bounding_box=24, voxel_size=2)
    assert len(vnf.faces) > 0
