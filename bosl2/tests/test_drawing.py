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

"""Tests for bosl2/drawing.py: the path generators (arc/catenary/helix/turtle) and the
renderers (stroke/dashed_stroke). The native primitives are mocked (see conftest), so the
render tests here only assert that geometry is produced; the geometry itself is checked against
the real app in bosl2/tests/test_stl_render.py, and the generators are pinned to real-BOSL2
ground truth in tests/test_bosl2_reorient.py."""

import math

import numpy as np
import pytest

from bosl2.drawing import arc, catenary, dashed_stroke, helix, stroke, turtle
from bosl2.drawing import _ENDCAP_DEFAULTS, _endcap_polys, _endcap_trim
from bosl2.paths import Path, Path3D
from bosl2.regions import Region


# -- arc returns a Path -------------------------------------------------------------------

def test_arc_returns_open_path():
    a = arc(r=16, start=0, angle=60)
    assert isinstance(a, Path)
    assert a.closed is False
    np.testing.assert_allclose(a[0], [16, 0], atol=1e-9)


def test_arc_wedge_is_closed_with_centre_first():
    w = arc(r=10, angle=90, cp=[2, 3], wedge=True)
    assert isinstance(w, Path)
    assert w.closed is True
    np.testing.assert_allclose(w[0], [2, 3], atol=1e-9)  # centre point prepended


def test_arc_angle_range_form():
    a = arc(n=5, r=10, angle=[30, 90])
    np.testing.assert_allclose(a[0], [10 * math.cos(math.radians(30)), 10 * math.sin(math.radians(30))], atol=1e-9)
    np.testing.assert_allclose(a[-1], [0, 10], atol=1e-9)


def test_arc_two_point_short_and_long():
    short = arc(n=7, cp=[0, 0], points=[[10, 0], [0, 10]])
    long = arc(n=7, cp=[0, 0], points=[[10, 0], [0, 10]], long=True)
    # both start/end at the same points, but the long one bulges the other way (negative x mid)
    np.testing.assert_allclose(short[0], [10, 0], atol=1e-9)
    np.testing.assert_allclose(long[0], [10, 0], atol=1e-9)
    assert short[len(short) // 2][0] > 0  # short arc stays in the +x/+y quadrant
    assert long[len(long) // 2][0] < 0    # long arc swings around through -x


def test_arc_corner_is_tangent_fillet():
    c = arc(corner=[[0, 10], [0, 0], [10, 0]], r=3)
    assert isinstance(c, Path)
    # tangent points sit 3 up the y-leg and 3 along the x-leg
    np.testing.assert_allclose(sorted([c[0].tolist() if hasattr(c[0], "tolist") else c[0], c[-1]]),
                               sorted([[0.0, 3.0], [3.0, 0.0]]), atol=1e-9)


def test_arc_collinear_points_raise():
    with pytest.raises(AssertionError):
        arc(n=5, points=[[0, 0], [1, 0], [2, 0]])


# -- catenary -----------------------------------------------------------------------------

def test_catenary_droop_hits_endpoints_and_midpoint():
    c = catenary(width=80, droop=30, n=21)
    assert isinstance(c, Path) and c.closed is False
    np.testing.assert_allclose(c[0], [-40, 0], atol=1e-6)
    np.testing.assert_allclose(c[-1], [40, 0], atol=1e-6)
    np.testing.assert_allclose(c[10], [0, -30], atol=1e-6)  # middle droops by 30


def test_catenary_sign_flips_with_negative_droop():
    up = catenary(width=50, droop=-15, n=15)
    assert up[len(up) // 2][1] > 0  # negative droop hangs upward


def test_catenary_requires_exactly_one_of_droop_angle():
    with pytest.raises(AssertionError):
        catenary(width=10)
    with pytest.raises(AssertionError):
        catenary(width=10, droop=2, angle=30)


# -- helix --------------------------------------------------------------------------------

def test_helix_returns_path3d():
    h = helix(turns=2, h=40, r=10)
    assert isinstance(h, Path3D)  # the 3-D path object
    assert not isinstance(h, Path)
    assert len(h[0]) == 3
    np.testing.assert_allclose(h[0], [10, 0, 0], atol=1e-9)
    assert math.isclose(h[-1][2], 40, abs_tol=1e-9)  # ends at the full height


def test_helix_needs_exactly_two_params():
    with pytest.raises(AssertionError):
        helix(h=40, r=10)  # only one of length/turns/angle


def test_helix_flat_spiral():
    h = helix(h=0, r1=50, r2=25, l=0, turns=4)
    assert all(math.isclose(p[2], 0, abs_tol=1e-9) for p in h)  # flat: every z is 0


# -- turtle -------------------------------------------------------------------------------

def test_turtle_square():
    p = turtle(["move", 10, "left", 90, "move", 10, "left", 90, "move", 10])
    assert isinstance(p, Path)
    np.testing.assert_allclose(p, [[0, 0], [10, 0], [10, 10], [0, 10]], atol=1e-9)


def test_turtle_repeat_closes_square():
    p = turtle(["repeat", 4, ["move", 40, "left", 90]])
    np.testing.assert_allclose(p[0], [0, 0], atol=1e-9)
    np.testing.assert_allclose(p[-1], [0, 0], atol=1e-9)  # 4 turns back to origin


def test_turtle_full_state():
    st = turtle(["move", 5], full_state=True)
    assert len(st) == 4  # [path, step, angle, arcsteps]
    np.testing.assert_allclose(st[0][-1], [5, 0], atol=1e-9)


def test_turtle_unknown_command_raises():
    with pytest.raises(AssertionError):
        turtle(["frobnicate", 3])


# -- stroke / dashed_stroke build geometry ------------------------------------------------

def test_stroke_2d_builds():
    assert arc(r=30, angle=200).stroke(width=3) is not None


def test_stroke_3d_builds():
    assert stroke(helix(turns=2, h=40, r=20), width=3) is not None


def test_stroke_closed_path_defaults_from_flag():
    sq = Path([[0, 0], [10, 0], [10, 10], [0, 10]], closed=True)
    assert sq.stroke(width=1) is not None


def test_stroke_region_strokes_every_path():
    reg = Region.with_holes([[0, 0], [40, 0], [40, 30], [0, 30]],
                            [[10, 10], [30, 10], [30, 20], [10, 20]])
    assert reg.stroke(width=2) is not None


def test_dashed_stroke_returns_paths():
    dashes = dashed_stroke(arc(r=30, angle=360), dashpat=[6, 4], closed=True)
    assert len(dashes) > 1
    assert all(isinstance(d, Path) for d in dashes)


def test_dashed_stroke_on_path_method():
    dashes = Path([[0, 0], [100, 0]], closed=False).dashed_stroke(dashpat=[5, 5])
    assert len(dashes) > 1
    assert all(isinstance(d, Path) for d in dashes)


def test_dashed_stroke_region_flattens():
    reg = Region([[[0, 0], [40, 0], [40, 40], [0, 40]]])
    dashes = reg.dashed_stroke(dashpat=[8, 4])
    assert all(isinstance(d, Path) for d in dashes)


def test_dashed_stroke_3d_yields_path3d():
    dashes = helix(turns=2, h=40, r=10).dashed_stroke(dashpat=[6, 4])
    assert len(dashes) > 1
    assert all(isinstance(d, Path3D) for d in dashes)


# -- fancy endcaps generate directly (no fallback) ----------------------------------------

ALL_ENDCAPS = ["round", "square", "butt", False, "dot", "block", "diamond", "chisel", "line",
               "x", "cross", "arrow", "arrow2", "arrow3", "tail", "tail2"]


@pytest.mark.parametrize("style", ALL_ENDCAPS)
def test_every_endcap_style_builds_2d(style):
    assert stroke([[0, 0], [40, 0]], width=3, endcaps=style) is not None


@pytest.mark.parametrize("style", ALL_ENDCAPS)
def test_every_endcap_style_builds_3d(style):
    assert stroke([[0, 0, 0], [40, 0, 0]], width=3, endcaps=style) is not None


def test_endcap_polys_shapes():
    # butt/false produce no polygon; x and cross are four triangles; arrow is one hexagon-ish poly
    assert _endcap_polys("butt", 1) == []
    assert _endcap_polys(False, 1) == []
    assert len(_endcap_polys("x", 1)) == 4
    assert len(_endcap_polys("cross", 1)) == 4
    assert len(_endcap_polys("arrow", 1)) == 1
    assert len(_endcap_polys("arrow", 1)[0]) == 6
    assert len(_endcap_polys("arrow3", 1)[0]) == 3  # a plain triangle


def test_endcap_polys_scale_with_linewidth():
    small = _endcap_polys("arrow", 1)[0]
    big = _endcap_polys("arrow", 2)[0]
    np.testing.assert_allclose(np.array(big), 2 * np.array(small), atol=1e-9)


def test_arrow_endcaps_trim_but_round_does_not():
    assert _endcap_trim("arrow", 3) > 0
    assert _endcap_trim("arrow3", 3) > 0
    assert _endcap_trim("arrow2", 3) > 0
    assert _endcap_trim("round", 3) == 0
    assert _endcap_trim("square", 3) == 0
    assert _endcap_trim(False, 3) == 0


def test_unknown_endcap_style_raises():
    with pytest.raises(AssertionError):
        stroke([[0, 0], [40, 0]], width=3, endcaps="banana")


def test_every_style_in_defaults_table():
    for style in ALL_ENDCAPS:
        assert style in _ENDCAP_DEFAULTS


def test_fancy_joint_style_builds():
    assert stroke([[0, 0], [20, 0], [20, 20]], width=3, joints="diamond") is not None
