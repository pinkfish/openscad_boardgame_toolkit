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

"""Tests for bosl2/regions.py: the Region (outline + holes) list subclass."""

import numpy as np
import pytest

from bosl2.paths import Path
from bosl2.regions import Region

SQUARE = [[0, 0], [80, 0], [80, 60], [0, 60]]
HOLE = [[20, 20], [60, 20], [60, 40], [20, 40]]


def test_single_outline_is_one_path():
    r = Region(SQUARE)
    assert len(r) == 1
    assert isinstance(r[0], Path)


def test_list_of_outlines():
    r = Region([SQUARE, HOLE])
    assert len(r) == 2
    assert all(isinstance(p, Path) for p in r)


def test_with_holes():
    r = Region.with_holes(SQUARE, HOLE)
    assert len(r) == 2
    np.testing.assert_allclose(r.outline, [[float(x), float(y)] for x, y in SQUARE])
    assert len(r.holes) == 1
    np.testing.assert_allclose(r.holes[0], [[float(x), float(y)] for x, y in HOLE])


def test_rejects_non_path_items():
    with pytest.raises(TypeError):
        Region([1, 2, 3])


def test_is_a_list():
    assert isinstance(Region(SQUARE), list)


def test_offset_applies_to_every_path():
    r = Region.with_holes(SQUARE, HOLE).offset(delta=-1)
    assert len(r) == 2
    assert all(isinstance(p, Path) for p in r)


def test_translate_moves_all():
    r = Region.with_holes(SQUARE, HOLE).translate([5, 7])
    np.testing.assert_allclose(r.outline[0], [5, 7])


def test_bounds():
    b = Region.with_holes(SQUARE, HOLE).bounds()
    np.testing.assert_allclose(b, [[0, 0], [80, 60]])


def test_round_corners_returns_region():
    r = Region(SQUARE).round_corners(radius=2)
    assert isinstance(r, Region)


def test_geometry_returns_a_solid():
    # under the mock, polygon() and subtraction return stand-in solids
    g = Region.with_holes(SQUARE, HOLE).geometry()
    assert g is not None
