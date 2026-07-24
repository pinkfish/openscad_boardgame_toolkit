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

"""Tests for bosl2/miscellaneous.py: the path extrusions (path_extrude2d / path_extrude on Path /
Path3D, taking a 2-D profile object rather than children), and the bounding-box / hull / minkowski
helpers. Native geometry is mocked, so these check the API surface (types, profile forms, error
cases); geometric correctness is verified in test_stl_render.py."""

import pytest

import bosl2.shapes2d as s2
from bosl2 import miscellaneous as M
from bosl2.paths import Path, Path3D
from bosl2.shapes3d import Bosl2Solid, cuboid, sphere


L_PATH = Path([[0, 0], [40, 0], [40, 40]], closed=False)
PATH3 = Path3D([[0, 0, 0], [20, 0, 10], [20, 20, 20]], closed=False)


# -- path_extrude2d -----------------------------------------------------------------------

def test_path_extrude2d_returns_solid():
    assert isinstance(L_PATH.path_extrude2d(s2.square([4, 8], center=True)), Bosl2Solid)


def test_path_extrude2d_accepts_various_profiles():
    # native shape, a Path, a Region, a Bosl2Solid, and a factory all work as the profile
    assert isinstance(L_PATH.path_extrude2d(s2.circle(r=3)), Bosl2Solid)
    assert isinstance(L_PATH.path_extrude2d(Path([[-2, -4], [2, -4], [2, 4], [-2, 4]])), Bosl2Solid)
    from bosl2.regions import Region
    assert isinstance(L_PATH.path_extrude2d(Region([[[-2, -4], [2, -4], [2, 4], [-2, 4]]])), Bosl2Solid)
    assert isinstance(L_PATH.path_extrude2d(lambda: s2.square([4, 8], center=True)), Bosl2Solid)


def test_path_extrude2d_closed_and_caps():
    loop = Path([[0, 0], [40, 0], [40, 40], [0, 40]], closed=True)
    assert isinstance(loop.path_extrude2d(s2.square([4, 6], center=True), closed=True), Bosl2Solid)
    straight = Path([[0, 0], [40, 0]], closed=False)
    assert isinstance(straight.path_extrude2d(s2.square([6, 8], center=True), caps=True), Bosl2Solid)


def test_path_extrude2d_caps_on_closed_raises():
    loop = Path([[0, 0], [40, 0], [40, 40]], closed=True)
    with pytest.raises(AssertionError):
        loop.path_extrude2d(s2.square([4, 8]), caps=True, closed=True)


def test_path_extrude2d_requires_2d_path():
    with pytest.raises(AssertionError):
        PATH3.path_extrude2d(s2.circle(r=3))


# -- path_extrude (2-D and 3-D paths) -----------------------------------------------------

def test_path_extrude_on_2d_path():
    assert isinstance(L_PATH.path_extrude(s2.circle(r=3)), Bosl2Solid)


def test_path_extrude_on_3d_path():
    assert isinstance(PATH3.path_extrude(s2.circle(r=3)), Bosl2Solid)


def test_path_extrude_factory_profile():
    assert isinstance(PATH3.path_extrude(lambda: s2.circle(r=3)), Bosl2Solid)


# -- free functions -----------------------------------------------------------------------

def test_extrude_from_to():
    assert isinstance(M.extrude_from_to(s2.circle(r=4), [0, 0, 0], [10, 20, 30]), Bosl2Solid)
    assert isinstance(M.extrude_from_to(s2.circle(r=4), [0, 0, 0], [0, 0, 20], twist=90, scale=2), Bosl2Solid)


def test_extrude_from_to_same_point_raises():
    with pytest.raises(AssertionError):
        M.extrude_from_to(s2.circle(r=4), [1, 2, 3], [1, 2, 3])


def test_cylindrical_extrude():
    assert isinstance(M.cylindrical_extrude(s2.square([20, 8]), ir=25, or_=30), Bosl2Solid)
    assert isinstance(M.cylindrical_extrude(s2.square([20, 8]), id=50, od=60, spin=45), Bosl2Solid)


def test_cylindrical_extrude_needs_radii():
    with pytest.raises(AssertionError):
        M.cylindrical_extrude(s2.square([20, 8]), ir=25)


def test_chain_hull():
    assert isinstance(M.chain_hull(cuboid([5, 5, 5]), sphere(r=4).right(20)), Bosl2Solid)
    assert isinstance(M.chain_hull([cuboid([5, 5, 5]), sphere(r=4), cuboid([3, 3, 3])]), Bosl2Solid)
    # single object passes through
    assert isinstance(M.chain_hull(cuboid([5, 5, 5])), Bosl2Solid)


def test_minkowski_difference():
    assert isinstance(M.minkowski_difference(cuboid([40, 40, 40]), sphere(r=8)), Bosl2Solid)


# -- Bosl2Solid methods -------------------------------------------------------------------

BOX = cuboid([40, 30, 20])


def test_bounding_box():
    assert isinstance(BOX.bounding_box(), Bosl2Solid)
    assert isinstance(BOX.bounding_box(excess=3), Bosl2Solid)


def test_offset3d_zero_is_noop():
    assert BOX.offset3d(0) is BOX


def test_offset3d_and_round3d():
    assert isinstance(BOX.offset3d(2), Bosl2Solid)
    assert isinstance(BOX.offset3d(-2), Bosl2Solid)
    assert isinstance(BOX.round3d(3), Bosl2Solid)
    assert isinstance(BOX.round3d(or_=2, ir=1), Bosl2Solid)


def test_chain_hull_and_minkowski_diff_methods():
    assert isinstance(BOX.chain_hull(sphere(r=5).right(30)), Bosl2Solid)
    assert isinstance(BOX.minkowski_difference(sphere(r=4)), Bosl2Solid)
