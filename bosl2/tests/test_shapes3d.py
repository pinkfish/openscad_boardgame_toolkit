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

"""Tests for bosl2/shapes3d.py: the Bosl2Solid wrapper, its transforms and bbox anchoring.

The native primitives are mocked (see conftest); the mock's cube/cylinder/sphere track an
axis-aligned bounding box, so Bosl2Solid's bbox-backed anchoring math is numerically exercised.
"""

import numpy as np

from bosl2.constants import BACK, BOTTOM, CENTER, FRONT, LEFT, RIGHT, TOP
from bosl2.shapes3d import Bosl2Solid, cuboid, cyl, sphere


def test_cuboid_is_bosl2solid_with_size():
    c = cuboid([40, 30, 20])
    assert isinstance(c, Bosl2Solid)
    assert list(c.size) == [40, 30, 20]


def test_bounds_center_and_size():
    center, size = cuboid([40, 30, 20]).bounds()
    np.testing.assert_allclose(center, [0, 0, 0], atol=1e-9)
    np.testing.assert_allclose(size, [40, 30, 20], atol=1e-9)


def test_anchor_points_on_faces():
    c = cuboid([40, 30, 20])
    np.testing.assert_allclose(c.anchor_point(TOP), [0, 0, 10], atol=1e-9)
    np.testing.assert_allclose(c.anchor_point(BOTTOM), [0, 0, -10], atol=1e-9)
    np.testing.assert_allclose(c.anchor_point(RIGHT), [20, 0, 0], atol=1e-9)
    np.testing.assert_allclose(c.anchor_point(FRONT), [0, -15, 0], atol=1e-9)
    np.testing.assert_allclose(c.anchor_point([1, 1, 1]), [20, 15, 10], atol=1e-9)


def test_directional_moves_shift_center():
    c = cuboid([10, 10, 10])
    np.testing.assert_allclose(c.right(5).anchor_point(CENTER), [5, 0, 0], atol=1e-9)
    np.testing.assert_allclose(c.left(5).anchor_point(CENTER), [-5, 0, 0], atol=1e-9)
    np.testing.assert_allclose(c.back(5).anchor_point(CENTER), [0, 5, 0], atol=1e-9)
    np.testing.assert_allclose(c.forward(5).anchor_point(CENTER), [0, -5, 0], atol=1e-9)
    np.testing.assert_allclose(c.up(5).anchor_point(CENTER), [0, 0, 5], atol=1e-9)
    np.testing.assert_allclose(c.down(5).anchor_point(CENTER), [0, 0, -5], atol=1e-9)


def test_move_and_translate_agree():
    c = cuboid([10, 10, 10])
    np.testing.assert_allclose(c.move([1, 2, 3]).anchor_point(CENTER), [1, 2, 3], atol=1e-9)
    np.testing.assert_allclose(c.translate([1, 2, 3]).anchor_point(CENTER), [1, 2, 3], atol=1e-9)


def test_rot_is_rotate_alias():
    assert Bosl2Solid.rot is Bosl2Solid.rotate
    assert isinstance(cuboid([10, 10, 10]).rot(90), Bosl2Solid)


def test_reanchor_moves_anchor_to_origin():
    rb = cuboid([40, 30, 20]).reanchor(BOTTOM)
    center, size = rb.bounds()
    np.testing.assert_allclose(center, [0, 0, 10], atol=1e-9)  # box now sits on z=0
    np.testing.assert_allclose(size, [40, 30, 20], atol=1e-9)


def test_wrap_unwrap():
    c = cuboid([10, 10, 10])
    assert c.shape is not None
    assert Bosl2Solid._unwrap(c) is c.shape
    assert Bosl2Solid._unwrap(c.shape) is c.shape


def test_csg_operators_return_bosl2solid():
    a, b = cuboid([10, 10, 10]), cuboid([5, 5, 5])
    assert isinstance(a | b, Bosl2Solid)
    assert isinstance(a - b, Bosl2Solid)
    assert isinstance(a & b, Bosl2Solid)


def test_color_and_scale_preserve_wrapper():
    c = cuboid([10, 10, 10])
    assert isinstance(c.color("red"), Bosl2Solid)
    assert isinstance(c.scale([2, 2, 2]), Bosl2Solid)


def test_other_primitives_build():
    assert isinstance(sphere(r=5), Bosl2Solid)
    assert isinstance(cyl(h=10, r=3), Bosl2Solid)


def test_getattr_falls_through_to_native():
    # a method not defined on Bosl2Solid resolves on the wrapped native shape
    c = cuboid([10, 10, 10])
    assert c.position is not None  # native accessor via __getattr__
