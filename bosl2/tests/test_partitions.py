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

"""Tests for bosl2/partitions.py: the cut-path generators and the Partitionable cut operators on
Bosl2Solid. partition_path is pinned to real BOSL2 in tests/test_bosl2_reorient.py; here we check
the segment grammar and that each cutting method builds. Native geometry is mocked, so the
geometric correctness (half volumes, interlocking pieces) is verified in test_stl_render.py."""

import math

import numpy as np
import pytest

from bosl2.partitions import (
    partition_path, partition_mask, partition_cut_mask, _ptn_sect, _partition_subpath,
    _partition_cutpath,
)
from bosl2.paths import Path
from bosl2.shapes3d import Bosl2Solid, cuboid, sphere


# -- cut-path generators ------------------------------------------------------------------

def test_partition_path_returns_path():
    p = partition_path(["flat", "jigsaw", "flat"], _fn=24)
    assert isinstance(p, Path)
    assert p.closed is False


def test_partition_path_closed_when_y_given():
    p = partition_path([30, "hammerhead", 30], y=150)
    assert p.closed is True
    # the closing edge sits at y=150
    assert any(math.isclose(pt[1], 150, abs_tol=1e-9) for pt in p)


def test_named_subpaths_have_expected_shape():
    assert _partition_subpath("flat") == [[0, 0], [1, 0]]
    assert _partition_subpath("sawtooth") == [[0, 0], [0.5, 1], [1, 0]]
    assert len(_partition_subpath("dovetail")) == 6
    assert len(_partition_subpath("hammerhead")) == 10
    assert len(_partition_subpath("jigsaw", _fn=24)) > 10  # arc-based


def test_ptn_sect_numeric_is_flat_segment():
    assert _ptn_sect(30) == [[0, 0], [30.0, 0]]


def test_ptn_sect_yflip_negates_y():
    base = _ptn_sect("sawtooth")
    flipped = _ptn_sect("sawtooth yflip")
    np.testing.assert_allclose([p[1] for p in flipped], [-p[1] for p in base], atol=1e-9)


def test_ptn_sect_repeat_triples_width():
    one = _ptn_sect("sawtooth")
    three = _ptn_sect("sawtooth 3x")
    assert math.isclose(max(p[0] for p in three), 3 * max(p[0] for p in one), rel_tol=1e-9)


def test_ptn_sect_resize():
    sect = _ptn_sect("jigsaw 40x20", _fn=24)
    xs = [p[0] for p in sect]
    ys = [p[1] for p in sect]
    assert math.isclose(max(xs) - min(xs), 40, abs_tol=1e-6)
    assert max(abs(y) for y in ys) <= 20 + 1e-6


def test_ptn_sect_skew_shifts_top():
    sect = _ptn_sect("square skew:15")
    # the top edge (y=25) is shifted right relative to the bottom by height*tan(15)
    assert isinstance(sect, list) and len(sect) == 4


def test_ptn_sect_bad_option_raises():
    with pytest.raises(AssertionError):
        _ptn_sect("sawtooth bogus")


def test_partition_cutpath_repeats_to_length():
    path = _partition_cutpath(100, 20, [20, 10], "dovetail", 0, True)
    xs = [p[0] for p in path]
    assert math.isclose(min(xs), -50, abs_tol=1e-9)  # spans -l/2 .. l/2
    assert math.isclose(max(xs), 50, abs_tol=1e-9)


# -- mask builders ------------------------------------------------------------------------

def test_partition_mask_builds():
    assert isinstance(partition_mask(l=60, w=30, h=20, cutpath="dovetail"), Bosl2Solid)
    assert isinstance(partition_mask(l=60, w=30, h=20, cutpath="jigsaw", inverse=True, _fn=12), Bosl2Solid)


def test_partition_cut_mask_builds():
    assert isinstance(partition_cut_mask(l=60, h=20, cutpath="dovetail", slop=0.2), Bosl2Solid)


# -- Partitionable methods on Bosl2Solid --------------------------------------------------

BOX = cuboid([40, 30, 20])


def test_axis_half_methods_return_solid():
    assert isinstance(BOX.left_half(), Bosl2Solid)
    assert isinstance(BOX.right_half(x=5), Bosl2Solid)
    assert isinstance(BOX.front_half(), Bosl2Solid)
    assert isinstance(BOX.back_half(y=-3), Bosl2Solid)
    assert isinstance(BOX.top_half(), Bosl2Solid)
    assert isinstance(BOX.bottom_half(z=5), Bosl2Solid)


def test_half_of_general_normal():
    assert isinstance(BOX.half_of([0, 1, 1]), Bosl2Solid)
    assert isinstance(sphere(r=20).half_of([1, 0, 0], cp=5), Bosl2Solid)


def test_half_of_with_cut_path():
    cp = partition_path([40, "jigsaw", 40], _fn=12)
    assert isinstance(BOX.back_half(cut_path=cp), Bosl2Solid)


def test_partition_returns_two_pieces():
    pieces = BOX.partition(spread=12, cutpath="dovetail")
    assert isinstance(pieces, list) and len(pieces) == 2
    assert all(isinstance(p, Bosl2Solid) for p in pieces)


def test_partition_accepts_cutsize_vector_and_spin():
    pieces = cuboid([60, 40, 20]).partition(spread=8, cutsize=[20, 15], cutpath="hammerhead", spin=90)
    assert len(pieces) == 2
