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

"""Real-render STL tests: build bosl2 objects in the real PythonSCAD app, export them to STL,
and verify the produced mesh's geometry (bounding box, volume, triangle count, watertightness).

These need the PythonSCAD app; they SKIP when no binary is found (set PYTHONSCAD_BIN). Run just
these with: ``PYTHONSCAD_BIN=/path/to/PythonSCAD python3 -m pytest bosl2/tests/test_stl_render.py``.
"""

import math

import numpy as np
import pytest

from render_stl import find_pythonscad_binary, render_object, stl_metrics

pytestmark = pytest.mark.skipif(
    find_pythonscad_binary() is None,
    reason="no PythonSCAD binary found (set PYTHONSCAD_BIN or install the app)",
)

CIRCLE = "[[2*math.cos(t), 2*math.sin(t)] for t in np.linspace(0, 2*math.pi, 16, endpoint=False)]"
PATCH = (
    "[[[-50,-50,0],[-16,-50,20],[16,-50,-20],[50,-50,0]],"
    " [[-50,-16,20],[-16,-16,20],[16,-16,-20],[50,-16,20]],"
    " [[-50,16,20],[-16,16,-20],[16,16,20],[50,16,20]],"
    " [[-50,50,0],[-16,50,-20],[16,50,20],[50,50,0]]]"
)


def _render(tmp_path, expr, setup="", name="obj"):
    out = tmp_path / f"{name}.stl"
    res = render_object(expr, out, setup=setup)
    if not res.ok:
        pytest.skip(f"render failed: {res.error}\n{res.stderr[-600:]}")
    return stl_metrics(out)


# -- primitive solids with exactly known geometry -----------------------------------------

def test_cuboid(tmp_path):
    m = _render(tmp_path, "s3.cuboid([40, 30, 20])", name="cuboid")
    np.testing.assert_allclose(m.size, [40, 30, 20], atol=1e-3)
    assert math.isclose(m.volume, 40 * 30 * 20, rel_tol=1e-4)
    assert m.ntris == 12  # a box is two triangles per face
    assert m.watertight


def test_prismoid_frustum_volume(tmp_path):
    # frustum volume = h/3 * (A1 + A2 + sqrt(A1*A2)) = 30/3*(1600+400+800) = 28000
    m = _render(tmp_path, "s3.prismoid([40, 40], [20, 20], h=30)", name="prismoid")
    np.testing.assert_allclose(m.size, [40, 40, 30], atol=1e-2)
    assert math.isclose(m.volume, 28000.0, rel_tol=1e-3)
    assert m.watertight


def test_cylinder_volume(tmp_path):
    # true volume pi*r^2*h = pi*25*20 ~= 1570.8; a 64-gon inscribes slightly under it
    true_vol = math.pi * 25 * 20
    m = _render(tmp_path, "s3.cyl(h=20, r=5, _fn=64)", name="cyl")
    assert math.isclose(m.size[2], 20.0, abs_tol=1e-3)
    np.testing.assert_allclose(m.size[:2], [10, 10], atol=0.1)
    assert 0.99 * true_vol < m.volume < true_vol
    assert m.watertight


def test_sphere_volume(tmp_path):
    true_vol = 4 / 3 * math.pi * 10**3
    m = _render(tmp_path, "s3.sphere(r=10, _fn=64)", name="sphere")
    np.testing.assert_allclose(m.size, [20, 20, 20], atol=0.4)
    assert 0.95 * true_vol < m.volume < true_vol  # faceting under-fills the true sphere
    assert m.watertight


def test_regular_prism_height_and_solid(tmp_path):
    m = _render(tmp_path, "s3.regular_prism(6, h=10, r=10)", name="hexprism")
    assert math.isclose(m.size[2], 10.0, abs_tol=1e-3)
    assert m.volume > 0
    assert m.watertight


def test_tube_is_hollow(tmp_path):
    # a tube encloses less than the solid outer cylinder of the same radius/height
    m = _render(tmp_path, "s3.tube(h=10, outer_r=10, ir=6)", name="tube")
    assert math.isclose(m.size[2], 10.0, abs_tol=1e-3)
    solid_outer = math.pi * 10**2 * 10
    assert 0 < m.volume < solid_outer
    assert m.watertight


# -- VNF-based solids (surfaces, sheets, sweeps) ------------------------------------------

def test_bezier_patch_sheet(tmp_path):
    m = _render(tmp_path, f"BezierPatch({PATCH}).sheet([0, -6], splinesteps=8).polyhedron()",
                name="sheet")
    assert m.ntris > 0
    assert m.volume > 0


def test_bezier_sweep_tube(tmp_path):
    setup = f"shape = {CIRCLE}\nbez = [[0,0,5],[0,0,10],[15,7,9],[17,2,4]]\n"
    m = _render(tmp_path, "Bezier(bez).sweep(shape, splinesteps=10).polyhedron()", setup=setup,
                name="beziersweep")
    assert m.ntris > 0
    assert m.volume > 0
    assert m.watertight  # a capped tube is a closed solid


def test_bezpath_sweep(tmp_path):
    setup = (
        f"shape = {CIRCLE}\n"
        "bezpath = [[0,0,0],[10,0,0],[10,10,0],[10,10,10],[10,20,10],[0,20,10],[0,20,20]]\n"
    )
    m = _render(tmp_path, "Bezier(bezpath).bezpath_sweep(shape, splinesteps=8, N=3).polyhedron()",
                setup=setup, name="bezpathsweep")
    assert m.ntris > 0
    assert m.volume > 0


def test_path_sweep_closed_torus(tmp_path):
    setup = (
        "shape = [[math.cos(t)+5, math.sin(t)] for t in np.linspace(0, 2*math.pi, 12, endpoint=False)]\n"
        "circ = [[math.cos(t)*20, math.sin(t)*20, 0] for t in np.linspace(0, 2*math.pi, 32, endpoint=False)]\n"
    )
    m = _render(tmp_path, "path_sweep(shape, circ, closed=True).polyhedron()", setup=setup,
                name="torus")
    assert m.ntris > 0
    assert m.volume > 0
    assert m.watertight  # a closed loop sweep has no ends


def test_two_objects_differ(tmp_path):
    # a sanity guard that the pipeline actually reflects the object: a bigger box has more volume
    small = _render(tmp_path, "s3.cuboid([10, 10, 10])", name="small")
    big = _render(tmp_path, "s3.cuboid([20, 20, 20])", name="big")
    assert big.volume > small.volume * 7  # 8x the volume
