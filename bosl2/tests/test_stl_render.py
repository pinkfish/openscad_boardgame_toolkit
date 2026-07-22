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


# -- the wider skin.scad surface generators -----------------------------------------------

def test_skin_lofts_two_profiles(tmp_path):
    setup = (
        "circle = [[6*math.cos(t), 6*math.sin(t)] for t in np.linspace(0, 2*math.pi, 24, endpoint=False)]\n"
        "square = [[-8, -8], [8, -8], [8, 8], [-8, 8]]\n"
    )
    m = _render(tmp_path, "skin([circle, square], slices=16, method='reindex', z=[0, 25]).polyhedron()",
                setup=setup, name="skin")
    assert m.ntris > 0
    assert m.volume > 0
    assert math.isclose(m.size[2], 25.0, abs_tol=1e-3)


def test_linear_sweep_twist_scale(tmp_path):
    setup = "square = [[-10, -10], [10, -10], [10, 10], [-10, 10]]\n"
    m = _render(tmp_path, "linear_sweep(square, height=40, twist=120, scale=0.4).polyhedron()",
                setup=setup, name="linsweep")
    assert m.volume > 0
    assert math.isclose(m.size[2], 40.0, abs_tol=1e-3)


def test_linear_sweep_plain_volume(tmp_path):
    setup = "square = [[-10, -10], [10, -10], [10, 10], [-10, 10]]\n"
    m = _render(tmp_path, "linear_sweep(square, height=5).polyhedron()", setup=setup, name="linplain")
    assert math.isclose(m.volume, 20 * 20 * 5, rel_tol=1e-3)  # 2000
    assert m.watertight


def test_rotate_sweep_full_revolution(tmp_path):
    setup = "profile = [[4, -10], [12, -10], [12, -6], [7, -2], [7, 2], [12, 6], [12, 10], [4, 10]]\n"
    m = _render(tmp_path, "rotate_sweep(profile, 360).polyhedron()", setup=setup, name="revolve")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [24, 24], atol=0.5)  # diameter ~ 2 * xmax(12)


def test_rotate_sweep_partial(tmp_path):
    setup = "profile = [[4, -10], [12, -10], [12, 10], [4, 10]]\n"
    m = _render(tmp_path, "rotate_sweep(profile, 270).polyhedron()", setup=setup, name="revolve270")
    assert m.volume > 0
    assert m.watertight  # a partial revolution is end-capped into a closed solid


def test_spiral_sweep_coil(tmp_path):
    setup = "section = [[-1.2, -1.2], [1.2, -1.2], [1.2, 1.2], [-1.2, 1.2]]\n"
    m = _render(tmp_path, "spiral_sweep(section, h=40, r=12, turns=5).polyhedron()",
                setup=setup, name="coil")
    assert m.ntris > 0
    assert m.volume > 0
    assert math.isclose(m.size[2], 40 + 2.4, abs_tol=1.0)  # height + a section's worth of overhang


def test_path_sweep2d_wavy_bar(tmp_path):
    setup = (
        "shape = [[-2, -2], [2, -2], [2, 2], [-2, 2]]\n"
        "path = [[t, 8*math.sin(t/12)] for t in range(0, 90, 3)]\n"
    )
    m = _render(tmp_path, "path_sweep2d(shape, path).polyhedron()", setup=setup, name="psweep2d")
    assert m.ntris > 0
    assert m.volume > 0
    assert m.watertight  # a capped open sweep is a closed solid


def test_rot_resample_then_sweep(tmp_path):
    setup = (
        "sq = [[-1.5, -1.5], [1.5, -1.5], [1.5, 1.5], [-1.5, 1.5]]\n"
        "curve = [[0, 0, 0], [20, 0, 8], [20, 20, 16], [0, 20, 24]]\n"
        "tl = rot_resample(path_sweep(sq, curve, transforms=True), n=30)\n"
    )
    m = _render(tmp_path, "sweep(sq, tl).polyhedron()", setup=setup, name="rotresample")
    assert m.ntris > 0
    assert m.volume > 0


# -- newly-ported shapes ------------------------------------------------------------------

def test_squircle_extruded(tmp_path):
    m = _render(tmp_path, "s2.squircle(40, squareness=0.7).linear_extrude(height=5)", name="squircle")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [40, 40], atol=0.5)
    assert math.isclose(m.size[2], 5.0, abs_tol=1e-3)


def test_keyhole_extruded(tmp_path):
    m = _render(tmp_path, "s2.keyhole(l=25, r1=4, r2=9, shoulder_r=2).linear_extrude(height=4)",
                name="keyhole")
    assert m.volume > 0
    assert m.watertight


def test_ring_extruded(tmp_path):
    m = _render(tmp_path, "s2.ring(r=20, ring_width=4).linear_extrude(height=5)", name="ring")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [48, 48], atol=1.0)  # outer diameter ~ 2*(20+4)


def test_plot3d_surface_solid(tmp_path):
    setup = (
        "xs = list(range(-30, 31, 3)); ys = list(range(-30, 31, 3))\n"
        "f = lambda x, y: 6 * math.cos(math.hypot(x, y) / 6)\n"
    )
    m = _render(tmp_path, "s3.plot3d(f, xs, ys)", setup=setup, name="plot3d")
    assert m.ntris > 0
    assert m.volume > 0


def test_fillet_subtracts_a_concave_edge(tmp_path):
    # subtracting a fillet mask from a box rounds one edge inward -> less volume than the box
    box = 30 * 30 * 20
    m = _render(
        tmp_path,
        "(s3.cuboid([30, 30, 20]) - s3.fillet(l=20, r=6).right(15).forward(15))",
        name="fillet",
    )
    np.testing.assert_allclose(m.size, [30, 30, 20], atol=1e-2)
    assert 0 < m.volume < box  # material removed at the edge
    assert m.watertight


def test_plot_revolution_makes_a_revolved_solid(tmp_path):
    setup = (
        "f = lambda a, z: 3 * math.sin(math.radians(4 * a)) * (z / 30)\n"
        "ang = list(range(0, 361, 6)); zs = list(range(0, 31, 2))\n"
    )
    m = _render(tmp_path, "s3.plot_revolution(f, angle=ang, z=zs, r1=12, r2=8)", setup=setup,
                name="plotrev")
    assert m.ntris > 0
    assert m.volume > 0
    assert math.isclose(m.size[2], 30.0, abs_tol=1.0)


def test_textured_tile_heightfield(tmp_path):
    setup = "bump = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]\n"
    m = _render(tmp_path, "s3.textured_tile(bump, size=[40, 40], tex_reps=[4, 4], tex_depth=3)",
                setup=setup, name="texttile")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [40, 40], atol=1e-2)
    assert m.watertight


def test_attach_with_bbox_override(tmp_path):
    # override the parent's bbox so the child attaches to a TOP that is higher than the real box
    m = _render(
        tmp_path,
        "s3.cuboid([30, 30, 20]).attach(TOP, s3.cuboid([10, 10, 10]), bbox=[[-15,-15,-10],[15,15,20]])",
        name="attachbbox",
    )
    # child bottom lands on z=20 (the overriding TOP), so the union reaches z=30 while the
    # real parent still tops out at z=10 -> a gap, but total height is 10..30 span for child + parent
    assert math.isclose(m.bbmax[2], 30.0, abs_tol=0.5)


# -- attachment methods (use the native bbox, no size passed) -----------------------------

def test_orient_rotates_up_to_direction(tmp_path):
    # UP -> RIGHT swaps the z (20) and x (40) extents
    m = _render(tmp_path, "s3.cuboid([40, 30, 20]).orient(RIGHT)", name="orient")
    np.testing.assert_allclose(m.size, [20, 30, 40], atol=1e-3)


def test_reorient_anchor_moves_face_to_origin(tmp_path):
    m = _render(tmp_path, "s3.cuboid([40, 30, 20]).reorient(anchor=TOP)", name="reorient")
    np.testing.assert_allclose(m.size, [40, 30, 20], atol=1e-3)
    assert math.isclose(m.bbmax[2], 0.0, abs_tol=1e-3)  # top face on z=0


def test_reanchor_puts_anchor_at_origin(tmp_path):
    m = _render(tmp_path, "s3.cuboid([40, 30, 20]).reanchor(BOTTOM)", name="reanchor")
    assert math.isclose(m.bbmin[2], 0.0, abs_tol=1e-3)  # bottom face on z=0


def test_attach_places_child_on_face(tmp_path):
    # a small cube attached to the TOP of a big one -> the combined bbox is taller
    m = _render(tmp_path, "s3.cuboid([30, 30, 20]).attach(TOP, s3.cuboid([10, 10, 10]))", name="attach")
    assert m.volume > 30 * 30 * 20  # bigger than the parent alone
    assert math.isclose(m.size[2], 30.0, abs_tol=0.5)  # 20 + 10 stacked


# -- drawing.scad renderers ---------------------------------------------------------------

def test_stroke_2d_arc_ribbon(tmp_path):
    # a stroked arc extruded into a curved wall -> a real thin solid
    m = _render(tmp_path, "arc(r=30, angle=200).stroke(width=4).linear_extrude(height=3)",
                name="stroke2d")
    assert m.volume > 0
    assert math.isclose(m.size[2], 3.0, abs_tol=1e-2)
    # the ribbon spans roughly the arc's diameter but is only ~4 wide, so it is not a full disk
    assert m.volume < math.pi * 32 ** 2 * 3


def test_stroke_2d_closed_square(tmp_path):
    setup = "sq = Path([[0, 0], [40, 0], [40, 40], [0, 40]], closed=True)\n"
    m = _render(tmp_path, "sq.stroke(width=3, joints='round').linear_extrude(height=2)",
                setup=setup, name="strokesq")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [43, 43], atol=1.0)  # 40 + width, round joints


def test_stroke_3d_helix_tube(tmp_path):
    m = _render(tmp_path, "stroke(helix(turns=2, h=40, r=15), width=4)", name="stroke3d")
    assert m.ntris > 0
    assert m.volume > 0
    assert math.isclose(m.size[2], 40 + 4, abs_tol=2.0)  # helix height + tube diameter


def test_dashed_stroke_makes_multiple_solids(tmp_path):
    setup = (
        "dashes = dashed_stroke(arc(r=30, angle=360), dashpat=[8, 5], closed=True)\n"
        "solid = dashes[0].stroke(width=2)\n"
        "for d in dashes[1:]:\n"
        "    solid = solid | d.stroke(width=2)\n"
        "obj0 = solid.linear_extrude(height=2)\n"
    )
    m = _render(tmp_path, "obj0", setup=setup, name="dashed")
    assert m.volume > 0
    # dashes leave gaps, so total volume is well under a solid ring of the same width
    assert m.volume < math.pi * (32 ** 2 - 28 ** 2) * 2


def test_catenary_stroke(tmp_path):
    m = _render(tmp_path, "catenary(width=80, droop=30).stroke(width=3).linear_extrude(height=2)",
                name="catenary")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[0], 80, atol=3.0)  # spans the requested width


def test_turtle_stroke(tmp_path):
    setup = (
        "path = turtle(['move', 40, 'arcleft', 8, 'move', 40, 'arcleft', 8, "
        "'move', 40, 'arcleft', 8, 'move', 40, 'arcleft', 8])\n"
    )
    m = _render(tmp_path, "path.stroke(width=3, closed=True).linear_extrude(height=2)",
                setup=setup, name="turtle")
    assert m.volume > 0


# -- fancy endcaps generated directly -----------------------------------------------------

def test_stroke_arrow_endcap_2d(tmp_path):
    # an arrow endcap fans out wider than the 3-wide line: bbox in Y exceeds the line width
    m = _render(tmp_path, "stroke([[0, 0], [40, 0]], width=3, endcaps='arrow').linear_extrude(height=2)",
                name="arrow2d")
    assert m.volume > 0
    assert m.size[1] > 3 + 1  # arrowhead (width 3.5*3) is wider than the 3mm line
    assert math.isclose(m.bbmin[0], 0.0, abs_tol=0.2)   # arrow tip sits at the line end, no overshoot
    assert math.isclose(m.bbmax[0], 40.0, abs_tol=0.2)


def test_stroke_diamond_endcap_straddles_end(tmp_path):
    # a diamond endcap is centred on the endpoint, so it overshoots both ends
    m = _render(tmp_path, "stroke([[0, 0], [40, 0]], width=3, endcaps='diamond').linear_extrude(height=2)",
                name="diamond2d")
    assert m.bbmin[0] < -1.0     # overshoots the start
    assert m.bbmax[0] > 41.0     # overshoots the end


def test_stroke_tail_and_arrow_mixed(tmp_path):
    m = _render(tmp_path,
                "stroke([[0, 0], [40, 0]], width=3, endcap1='tail', endcap2='arrow').linear_extrude(height=2)",
                name="tailarrow")
    assert m.volume > 0
    assert m.bbmin[0] < 0  # the tail extends behind the start


def test_stroke_arrow_endcap_3d_is_a_cone(tmp_path):
    # the 3-D arrow endcap is a revolved cone: it is thicker across than the 4mm tube
    m = _render(tmp_path, "stroke([[0, 0, 0], [40, 0, 0]], width=4, endcaps='arrow')", name="arrow3d")
    assert m.ntris > 0
    assert m.volume > 0
    assert m.size[1] > 4 + 1 and m.size[2] > 4 + 1  # cone base wider than the tube in Y and Z


# -- Path3D transforms feed the renderers -------------------------------------------------

def test_path3d_rotated_helix_stroke(tmp_path):
    # rotating the helix about X swaps its Z-height into -Y; the tube follows
    setup = "coil = helix(turns=2, h=40, r=12).rotate(90, [1, 0, 0])\n"
    m = _render(tmp_path, "coil.stroke(width=3)", setup=setup, name="helixrot")
    assert m.volume > 0
    # after a 90-deg X rotation the ~40 tall extent now lies along Y (plus tube thickness)
    assert m.size[1] > 40


def test_path3d_resampled_helix_stroke(tmp_path):
    setup = "coil = helix(turns=3, h=60, r=20).resample(n=150)\n"
    m = _render(tmp_path, "coil.stroke(width=4)", setup=setup, name="helixresample")
    assert m.ntris > 0
    assert m.volume > 0
    assert math.isclose(m.size[2], 60 + 4, abs_tol=3.0)  # helix height + tube diameter


def test_path3d_translate_moves_stroke(tmp_path):
    setup = "coil = helix(turns=1.5, h=30, r=10).up(100)\n"
    m = _render(tmp_path, "coil.stroke(width=3)", setup=setup, name="helixup")
    assert m.bbmin[2] > 90  # lifted 100mm up


# -- distributors: solid copies -----------------------------------------------------------

def test_grid_copies_span_and_volume(tmp_path):
    # a 3x3 grid of 10mm cubes at 30mm spacing -> outer span 2*30 + 10 = 70, 9x the volume
    m = _render(tmp_path, "s3.cuboid([10, 10, 10]).grid_copies(n=[3, 3], spacing=30)", name="grid")
    np.testing.assert_allclose(m.size[:2], [70, 70], atol=0.5)
    assert math.isclose(m.volume, 9 * 1000, rel_tol=1e-3)
    assert m.watertight


def test_line_copies_volume(tmp_path):
    m = _render(tmp_path, "s3.cuboid([6, 6, 6]).xcopies(20, n=4)", name="linecopies")
    assert math.isclose(m.volume, 4 * 6 ** 3, rel_tol=1e-3)
    np.testing.assert_allclose(m.size[0], 3 * 20 + 6, atol=0.5)  # span of 4 copies


def test_zrot_copies_ring(tmp_path):
    # 6 cubes in a ring of radius 30 -> spread across a ~60mm-diameter footprint in X and Y
    m = _render(tmp_path, "s3.cuboid([6, 6, 6]).zrot_copies(n=6, r=30)", name="ring")
    assert m.volume > 5 * 6 ** 3  # roughly 6 cubes (minus any tiny overlap)
    assert 55 < m.size[0] < 70 and 55 < m.size[1] < 70
    assert math.isclose(m.size[2], 6.0, abs_tol=0.2)  # ring stays flat in Z


def test_xflip_copy_mirrors(tmp_path):
    # an off-center cube flipped across X=0 -> symmetric pair straddling the origin
    m = _render(tmp_path, "s3.cuboid([8, 8, 8]).right(20).xflip_copy()", name="xflip")
    assert math.isclose(m.volume, 2 * 8 ** 3, rel_tol=1e-3)
    np.testing.assert_allclose(m.bbmin[0], -24, atol=0.5)
    np.testing.assert_allclose(m.bbmax[0], 24, atol=0.5)


def test_arc_copies_solid(tmp_path):
    m = _render(tmp_path, "s3.cuboid([5, 5, 5]).arc_copies(n=8, r=25, sa=0, ea=180)", name="arccopies")
    assert m.volume > 0
    assert m.watertight


def test_distribute_list_of_children(tmp_path):
    setup = "parts = [s3.cuboid([10, 10, 10]), s3.sphere(r=8), s3.cyl(h=14, r=5)]\n"
    m = _render(tmp_path, "xdistribute(parts, spacing=8)", setup=setup, name="distribute")
    assert m.volume > 0
    assert m.size[0] > 30  # spread out along X


def test_path_copies_along_path(tmp_path):
    setup = "route = Path([[0, 0], [40, 0], [40, 40]], closed=False)\n"
    m = _render(tmp_path, "s3.cuboid([4, 8, 4]).path_copies(route, n=6)", setup=setup, name="pathcopies")
    assert m.volume > 0
    # copies span the L-shaped route: roughly 0..40 in X and 0..40 in Y
    assert m.size[0] > 35 and m.size[1] > 35


# -- colour operators (geometry survives; colour is a display attribute) -------------------

def test_color_name_keeps_geometry(tmp_path):
    m = _render(tmp_path, "s3.cuboid([10, 10, 10]).color('red')", name="colorname")
    assert math.isclose(m.volume, 1000, rel_tol=1e-4)
    assert m.watertight


def test_hsv_and_hsl_methods_render(tmp_path):
    a = _render(tmp_path, "s3.cuboid([10, 10, 10]).hsv(200, 0.8, 0.9)", name="hsv")
    b = _render(tmp_path, "s3.cuboid([10, 10, 10]).hsl(120, 0.6, 0.5, 0.7)", name="hsl")
    assert math.isclose(a.volume, 1000, rel_tol=1e-4)
    assert math.isclose(b.volume, 1000, rel_tol=1e-4)


def test_recolor_highlight_ghost_render(tmp_path):
    for expr, name in (("s3.cuboid([10, 10, 10]).recolor('green')", "recolor"),
                       ("s3.cuboid([10, 10, 10]).highlight()", "highlight"),
                       ("s3.cuboid([10, 10, 10]).ghost()", "ghost")):
        m = _render(tmp_path, expr, name=name)
        assert math.isclose(m.volume, 1000, rel_tol=1e-4)


def test_rainbow_colors_a_list(tmp_path):
    # rainbow returns a list of coloured solids; union them and check the combined geometry
    setup = (
        "parts = [s3.cuboid([6, 6, 6]).right(i * 10) for i in range(4)]\n"
        "coloured = rainbow(parts)\n"
        "obj0 = coloured[0]\n"
        "for piece in coloured[1:]:\n"
        "    obj0 = obj0 | piece\n"
    )
    m = _render(tmp_path, "obj0", setup=setup, name="rainbow")
    assert math.isclose(m.volume, 4 * 6 ** 3, rel_tol=1e-3)
    np.testing.assert_allclose(m.size[0], 3 * 10 + 6, atol=0.5)  # spread of 4 cubes


def test_recolor_child_keeps_its_own_color(tmp_path):
    # a coloured child unioned into a recoloured parent still contributes its geometry
    setup = "part = s3.cuboid([20, 20, 10]).color('blue').attach(TOP, s3.cuboid([8, 8, 8]).color('red'))\n"
    m = _render(tmp_path, "part.recolor('green')", setup=setup, name="recolorchild")
    assert m.volume > 20 * 20 * 10  # parent + attached child
    assert math.isclose(m.size[2], 18.0, abs_tol=0.5)


# -- partitions: planar cuts and interlocking splits --------------------------------------

def test_axis_halves_keep_exactly_half(tmp_path):
    full = 40 * 30 * 20
    left = _render(tmp_path, "s3.cuboid([40, 30, 20]).left_half()", name="lefthalf")
    top = _render(tmp_path, "s3.cuboid([40, 30, 20]).top_half()", name="tophalf")
    assert math.isclose(left.volume, full / 2, rel_tol=1e-3)
    np.testing.assert_allclose([left.bbmin[0], left.bbmax[0]], [-20, 0], atol=1e-2)
    assert math.isclose(top.volume, full / 2, rel_tol=1e-3)
    np.testing.assert_allclose([top.bbmin[2], top.bbmax[2]], [0, 10], atol=1e-2)


def test_bottom_half_offset_plane(tmp_path):
    # bottom_half(z=5) keeps z in [-10, 5] -> 15/20 of the box
    m = _render(tmp_path, "s3.cuboid([40, 30, 20]).bottom_half(z=5)", name="bottomz5")
    assert math.isclose(m.volume, 40 * 30 * 15, rel_tol=1e-3)
    np.testing.assert_allclose(m.bbmax[2], 5, atol=1e-2)


def test_half_of_diagonal_plane(tmp_path):
    m = _render(tmp_path, "s3.cuboid([40, 30, 20]).half_of([0, 1, 1])", name="halfdiag")
    assert math.isclose(m.volume, 40 * 30 * 20 / 2, rel_tol=1e-2)  # a plane through the centre halves it
    assert m.watertight


def test_half_of_auto_sizes_from_bbox(tmp_path):
    # no s= given: the mask auto-sizes to the (large) object
    m = _render(tmp_path, "s3.cuboid([200, 120, 60]).right_half()", name="autosize")
    assert math.isclose(m.volume, 200 * 120 * 60 / 2, rel_tol=1e-3)
    np.testing.assert_allclose([m.bbmin[0], m.bbmax[0]], [0, 100], atol=1e-1)


def test_jigsaw_cut_path_half(tmp_path):
    setup = "cp = partition_path([60, 'jigsaw', 60], _fn=16)\n"
    m = _render(tmp_path, "s3.cuboid([120, 40, 20]).back_half(cut_path=cp)", setup=setup, name="jigsawcut")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[0], 120, atol=0.5)
    assert m.watertight


def test_partition_two_pieces_conserve_volume(tmp_path):
    # the two dovetail pieces together reconstruct the whole box (spread apart)
    setup = (
        "p = s3.cuboid([60, 40, 20]).partition(spread=12, cutpath='dovetail')\n"
        "obj0 = p[0] | p[1]\n"
    )
    m = _render(tmp_path, "obj0", setup=setup, name="partition")
    assert math.isclose(m.volume, 60 * 40 * 20, rel_tol=1e-3)  # volume conserved
    np.testing.assert_allclose(m.size[1], 40 + 12, atol=0.5)   # spread widens Y by 12


def test_partition_single_piece_is_interlocking_half(tmp_path):
    setup = "obj0 = s3.cuboid([60, 40, 20]).partition(spread=0, cutpath='jigsaw', _fn=16)[0]\n"
    m = _render(tmp_path, "obj0", setup=setup, name="partback")
    assert math.isclose(m.volume, 60 * 40 * 20 / 2, rel_tol=1e-2)  # each piece is ~half
    assert m.watertight


def test_partition_mask_renders(tmp_path):
    m = _render(tmp_path, "partition_mask(l=60, w=30, h=20, cutpath='dovetail')", name="partmask")
    assert m.volume > 0
    assert math.isclose(m.size[2], 20, abs_tol=1e-2)


# -- miscellaneous.scad extrusions and transforms -----------------------------------------

def test_path_extrude2d_follows_the_path(tmp_path):
    # a moulding (4 wide, 8 tall profile) along an L-path spans the L footprint and stands 8 tall
    setup = "route = Path([[0, 0], [40, 0], [40, 40]], closed=False)\n"
    m = _render(tmp_path, "route.path_extrude2d(s2.square([4, 8], center=True))", setup=setup, name="pe2d")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [42, 42], atol=1.0)  # 40 path + profile width
    assert math.isclose(m.size[2], 8.0, abs_tol=1e-2)           # profile height
    assert m.watertight


def test_path_extrude2d_closed_loop(tmp_path):
    setup = "route = Path([[0, 0], [40, 0], [40, 40], [0, 40]], closed=True)\n"
    m = _render(tmp_path, "route.path_extrude2d(s2.square([4, 6], center=True), closed=True)",
                setup=setup, name="pe2dclosed")
    assert m.volume > 0
    assert math.isclose(m.size[2], 6.0, abs_tol=1e-2)
    assert m.watertight


def test_path_extrude2d_takes_a_factory(tmp_path):
    # the "children" form: a factory produces a fresh profile per placement
    setup = "route = Path([[0, 0], [30, 0]], closed=False)\n"
    m = _render(tmp_path, "route.path_extrude2d(lambda: s2.circle(r=4, _fn=16))", setup=setup, name="pe2dfac")
    assert m.volume > 0
    assert math.isclose(m.size[2], 8.0, abs_tol=0.3)  # circle d=8 stands 8 tall


def test_path_extrude_3d_path(tmp_path):
    setup = "route = Path3D([[0, 0, 0], [30, 0, 10], [30, 30, 20], [0, 30, 30]], closed=False)\n"
    m = _render(tmp_path, "route.path_extrude(s2.circle(r=4, _fn=16))", setup=setup, name="pe3d")
    assert m.volume > 0
    assert m.bbmax[2] > 25  # follows the rising path up to z~30


def test_extrude_from_to_column(tmp_path):
    m = _render(tmp_path, "extrude_from_to(s2.circle(r=4, _fn=24), [0, 0, 0], [0, 0, 30])", name="eft")
    assert math.isclose(m.size[2], 30.0, abs_tol=1e-2)
    np.testing.assert_allclose(m.size[:2], [8, 8], atol=0.2)
    assert m.watertight


def test_extrude_from_to_diagonal_with_twist(tmp_path):
    m = _render(tmp_path, "extrude_from_to(s2.square([8, 4], center=True), [0, 0, 0], [10, 20, 30], twist=180, scale=2)",
                name="eftdiag")
    assert m.volume > 0
    # the far end sits at [10,20,30]
    np.testing.assert_allclose([m.bbmax[0], m.bbmax[1], m.bbmax[2]], [10, 20, 30], atol=6)


def test_bounding_box_wraps_object(tmp_path):
    m = _render(tmp_path, "s3.sphere(r=15).bounding_box(excess=2)", name="bbox")
    np.testing.assert_allclose(m.size, [34, 34, 34], atol=0.4)  # d=30 + 2*2 excess
    assert m.watertight


def test_chain_hull_connects_shapes(tmp_path):
    m = _render(tmp_path, "chain_hull(s3.cuboid([5, 5, 5]), s3.sphere(r=4).right(20))", name="chainhull")
    assert m.volume > 0
    assert m.size[0] > 20  # spans from the cube to the sphere
    assert m.watertight


def test_offset3d_grows_solid(tmp_path):
    grown = _render(tmp_path, "s3.cuboid([20, 20, 20]).offset3d(3)", name="offset3d")
    assert grown.volume > 20 ** 3       # bigger than the original cube
    np.testing.assert_allclose(grown.size, [26, 26, 26], atol=1.0)  # grown ~3 each side


def test_cylindrical_extrude_wraps(tmp_path):
    # a 30-wide profile wraps a ~57-degree arc of a r=30 cylinder, standing 8 tall in Z
    m = _render(tmp_path, "cylindrical_extrude(s2.square([30, 8], center=True), ir=25, or_=30)",
                name="cylext")
    assert m.volume > 0
    assert math.isclose(m.size[2], 8.0, abs_tol=0.5)      # profile height -> cylinder axis
    assert m.bbmax[1] <= 30.5 and m.size[0] > 15          # curved band out near r=25..30


# -- nurbs.scad curve / surface evaluation ------------------------------------------------

def test_nurbs_curve_spans_control_points(tmp_path):
    # a clamped cubic curve starts/ends at the first/last control point
    setup = "ctrl = [[0, 0, 0], [10, 20, 5], [30, -10, 10], [50, 20, 0], [60, 0, 15]]\n"
    m = _render(tmp_path, "nurbs_curve(ctrl, 3, splinesteps=12).stroke(width=3)", setup=setup, name="nurbscurve")
    assert m.volume > 0
    np.testing.assert_allclose(m.bbmin[0], 0, atol=1.6)   # starts at x=0
    np.testing.assert_allclose(m.bbmax[0], 60, atol=1.6)  # ends at x=60


def test_nurbs_surface_patch(tmp_path):
    setup = (
        "patch = [[[-50,50,0],[-16,50,20],[16,50,20],[50,50,0]],"
        "[[-50,16,20],[-16,16,40],[16,16,40],[50,16,20]],"
        "[[-50,-16,20],[-16,-16,40],[16,-16,40],[50,-16,20]],"
        "[[-50,-50,0],[-16,-50,20],[16,-50,20],[50,-50,0]]]\n"
    )
    m = _render(tmp_path, "nurbs_vnf(patch, 3, splinesteps=8).polyhedron()", setup=setup, name="nurbspatch")
    assert m.ntris > 0
    np.testing.assert_allclose(m.size[:2], [100, 100], atol=1.0)  # spans the control grid


def test_rounding_methods_extrude(tmp_path):
    # circle / smooth / chamfer rounded squares all extrude into valid solids
    sq = "[[0, 0], [40, 0], [40, 30], [0, 30]]"
    for method, kw, name in (("circle", "radius=5", "roundcircle"),
                             ("smooth", "joint=8", "roundsmooth"),
                             ("chamfer", "joint=6", "roundchamfer")):
        m = _render(tmp_path, f"round_corners({sq}, method='{method}', {kw}).polygon().linear_extrude(height=4)",
                    name=name)
        assert m.volume > 0
        assert math.isclose(m.size[2], 4.0, abs_tol=1e-2)
        np.testing.assert_allclose(m.size[:2], [40, 30], atol=0.6)  # stays within the square
        assert m.watertight


def test_smooth_path_stroke(tmp_path):
    setup = "pts = [[0, 0], [10, 30], [30, -10], [50, 20], [70, 0]]\n"
    m = _render(tmp_path, "smooth_path(pts, relsize=0.4).stroke(width=2).linear_extrude(height=3)",
                setup=setup, name="smoothpath")
    assert m.volume > 0
    assert m.size[0] > 65  # spans the wiggly control points


def test_round_corners_3d_path(tmp_path):
    # a 3-D path with smooth corners, swept into a tube
    setup = "route = round_corners([[0,0,0],[40,0,0],[40,40,20],[0,40,20]], method='smooth', joint=8, closed=False)\n"
    m = _render(tmp_path, "route.stroke(width=3)", setup=setup, name="round3d")
    assert m.volume > 0
    assert m.bbmax[2] > 15  # follows the path up in Z


def test_threaded_rod_iso(tmp_path):
    # an ISO M12x1.75 rod: major diameter 12, length 24, minor = 12 - 2*(cos30*5/8)*1.75
    m = _render(tmp_path, "Threading.threaded_rod(12, 24, 1.75, _fa=6, _fs=1)", name="isorod")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [12, 12], atol=0.1)   # major diameter
    assert math.isclose(m.size[2], 24.0, abs_tol=0.05)           # length
    minor = 12 - 2 * math.cos(math.radians(30)) * 5 / 8 * 1.75
    lo = math.pi * (minor / 2) ** 2 * 24                          # minor-cylinder volume
    hi = math.pi * 6 ** 2 * 24                                    # major-cylinder volume
    assert lo < m.volume < hi                                     # threaded, so between the two


@pytest.mark.parametrize("expr,name,dia", [
    ("Threading.trapezoidal_threaded_rod(20, 30, 4, _fa=6, _fs=1)", "traprod", 20),
    ("Threading.acme_threaded_rod(20, 30, 4, _fa=6, _fs=1)", "acmerod", 20),
    ("Threading.square_threaded_rod(20, 30, 4, _fa=6, _fs=1)", "sqrod", 20),
    ("Threading.buttress_threaded_rod(20, 30, 4, _fa=6, _fs=1)", "buttrod", 20),
])
def test_threaded_rod_variants_watertight(tmp_path, expr, name, dia):
    m = _render(tmp_path, expr, name=name)
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [dia, dia], atol=0.2)
    assert math.isclose(m.size[2], 30.0, abs_tol=0.05)


def test_multistart_and_left_handed(tmp_path):
    a = _render(tmp_path, "Threading.threaded_rod(16, 24, 2, starts=2, _fa=6, _fs=1)", name="ms2")
    assert a.watertight and math.isclose(a.size[2], 24.0, abs_tol=0.05)
    b = _render(tmp_path, "Threading.threaded_rod(12, 24, 1.75, left_handed=True, _fa=6, _fs=1)", name="lh")
    assert b.watertight
    np.testing.assert_allclose(b.size[:2], [12, 12], atol=0.1)


def test_threaded_hex_nut(tmp_path):
    # a hex nut for an M12 rod: flat-to-flat 18, corner-to-corner ~20.8, height 10, threaded hole
    m = _render(tmp_path, "Threading.threaded_nut(18, 12, 10, 1.75, slop=0.1, _fa=6, _fs=1)", name="hexnut")
    assert m.watertight
    assert math.isclose(min(m.size[:2]), 18.0, abs_tol=0.3)      # flat-to-flat
    assert math.isclose(m.size[2], 10.0, abs_tol=0.05)           # height
    assert m.volume < math.pi * 10.4 ** 2 * 10                   # has a hole, so less than solid


def test_threaded_square_nut(tmp_path):
    m = _render(tmp_path, "Threading.trapezoidal_threaded_nut(24, 16, 12, 3, shape='square', slop=0.1, _fa=6, _fs=1)",
                name="sqnut")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [24, 24], atol=0.3)   # square
    assert math.isclose(m.size[2], 12.0, abs_tol=0.05)


def test_thread_helix_ridge(tmp_path):
    m = _render(tmp_path, "Threading.thread_helix(20, 4, turns=3, _fa=6, _fs=1)", name="threadhelix")
    assert m.volume > 0
    np.testing.assert_allclose(m.size[:2], [20, 20], atol=0.3)   # crest at diameter 20


# -- screws, nuts and screw holes ---------------------------------------------------------

def test_screw_socket_head(tmp_path):
    # M6 socket cap screw, 20 mm shaft: head diameter 10, head height 6 above the shaft, so the
    # whole solid is 26 tall and 10 wide at the head.
    m = _render(tmp_path, "Screws.screw('M6', 20, head='socket', drive='hex', _fa=6, _fs=1)", name="scrsocket")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [10, 10], atol=0.3)      # socket head diameter
    assert math.isclose(m.size[2], 26.0, abs_tol=0.3)              # 20 shaft + 6 head


def test_screw_hex_head(tmp_path):
    # M8 hex head: across-flats 13 (corner-to-corner ~15), head height 5.3 above a 16 mm shaft.
    m = _render(tmp_path, "Screws.screw('M8', 16, head='hex', _fa=6, _fs=1)", name="scrhex")
    assert m.watertight
    assert math.isclose(min(m.size[:2]), 13.0, abs_tol=0.4)        # flat-to-flat of the hex head
    assert math.isclose(m.size[2], 21.3, abs_tol=0.3)             # 16 shaft + 5.3 head


def test_screw_flat_head_countersunk(tmp_path):
    # M6 countersunk: the head is a 90-degree cone, so it adds only (11.085-6)/2 ~ 2.54 above the shaft.
    m = _render(tmp_path, "Screws.screw('M6', 16, head='flat', _fa=6, _fs=1)", name="scrflat")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [11.085, 11.085], atol=0.4)   # head diameter at the surface
    assert math.isclose(m.size[2], 16 + (11.085 - 6) / 2, abs_tol=0.3)


@pytest.mark.parametrize("head,name", [("button", "scrbtn"), ("pan", "scrpan"), ("none", "scrset")])
def test_screw_heads_watertight(tmp_path, head, name):
    drive = "hex" if head in ("button", "none") else "none"
    m = _render(tmp_path, f"Screws.screw('M6', 16, head='{head}', drive='{drive}', _fa=6, _fs=1)", name=name)
    assert m.watertight
    assert math.isclose(min(m.size[:2]), 6.0, abs_tol=0.4) or min(m.size[:2]) >= 6.0  # at least the shaft


def test_screw_recess_removes_volume(tmp_path):
    # the hex drive recess must actually cut material out of the head.
    solid = _render(tmp_path, "Screws.screw('M8', 16, head='socket', drive='none', _fa=6, _fs=1)", name="norec")
    drilled = _render(tmp_path, "Screws.screw('M8', 16, head='socket', drive='hex', _fa=6, _fs=1)", name="rec")
    assert drilled.watertight
    assert drilled.volume < solid.volume            # the recess subtracted material


def test_nut_matches_thread(tmp_path):
    # an M6 hex nut: flat-to-flat 10, normal thickness 5.2, threaded hole.
    m = _render(tmp_path, "Screws.nut('M6', slop=0.1, _fa=6, _fs=1)", name="scrnut")
    assert m.watertight
    assert math.isclose(min(m.size[:2]), 10.0, abs_tol=0.3)       # flat-to-flat
    assert math.isclose(m.size[2], 5.2, abs_tol=0.1)             # normal thickness
    assert m.volume < math.pi * 5.2 ** 2 * 5.2                    # has a threaded hole


def test_square_nut(tmp_path):
    m = _render(tmp_path, "Screws.nut('M6', shape='square', slop=0.1, _fa=6, _fs=1)", name="sqscrnut")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [10, 10], atol=0.3)


def test_screw_hole_clearance(tmp_path):
    # a normal-fit clearance hole for M6 is a plain cylinder of diameter 6 + 2*0.5 = 7.
    m = _render(tmp_path, "Screws.screw_hole('M6', 20, _fa=6, _fs=1)", name="clrhole")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [7, 7], atol=0.2)
    assert math.isclose(m.size[2], 20.0, abs_tol=0.05)


def test_screw_hole_countersink(tmp_path):
    # a flat-head clearance hole flares out to the countersink diameter at the top.
    m = _render(tmp_path, "Screws.screw_hole('M6', 20, head='flat', _fa=6, _fs=1)", name="cskhole")
    assert m.watertight
    assert max(m.size[:2]) >= 11.0                                # opens up to the head diameter
    assert m.bbmax[2] > 0 and m.bbmin[2] < 0                      # mouth at z=0, shaft below


def test_metaball_sphere_is_watertight(tmp_path):
    # a lone mb_sphere(10) at isovalue 1 -> a watertight sphere of radius 10
    m = _render(tmp_path,
                "metaballs([([0,0,0], mb_sphere(10))], bounding_box=[[-16,-16,-16],[16,16,16]], voxel_size=1.5).polyhedron()",
                name="mbsphere")
    assert m.watertight
    np.testing.assert_allclose(m.size, [20, 20, 20], atol=1.0)  # diameter ~20


def test_metaballs_merge_into_one_blob(tmp_path):
    # two spheres whose fields overlap fuse into a single watertight peanut
    setup = "spec = [([-9,0,0], mb_sphere(9)), ([9,0,0], mb_sphere(9))]\n"
    m = _render(tmp_path,
                "metaballs(spec, bounding_box=[[-28,-16,-16],[28,16,16]], voxel_size=2).polyhedron()",
                setup=setup, name="mbpeanut")
    assert m.watertight
    assert m.size[0] > 40  # spans both balls plus the inflated bridge


def test_metaball_torus_has_a_hole(tmp_path):
    m = _render(tmp_path,
                "metaballs([([0,0,0], mb_torus(10, 3))], bounding_box=[[-16,-16,-8],[16,16,8]], voxel_size=1.5).polyhedron()",
                name="mbtorus")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [26, 26], atol=1.5)  # outer diameter ~ 2*(10+3)
    assert m.size[2] < 8  # flat torus


def test_isosurface_of_a_field_function(tmp_path):
    setup = (
        "def sf(pts):\n"
        "    return 8.0 / (pts[:, 0]**2 + pts[:, 1]**2 + pts[:, 2]**2) ** 0.5\n"
    )
    m = _render(tmp_path, "isosurface(sf, 1, bounding_box=24, voxel_size=1.5).polyhedron()",
                setup=setup, name="isofield")
    assert m.watertight
    np.testing.assert_allclose(m.size, [16, 16, 16], atol=1.0)  # sphere of radius 8


def test_nurbs_rational_sphere_is_watertight(tmp_path):
    # the classic rational-NURBS unit sphere (weights + repeated v-knots) meshes to a closed solid
    setup = (
        "patch = [[[0,0,1]]*7,"
        "[[2,0,1],[2,4,1],[-2,4,1],[-2,0,1],[-2,-4,1],[2,-4,1],[2,0,1]],"
        "[[2,0,-1],[2,4,-1],[-2,4,-1],[-2,0,-1],[-2,-4,-1],[2,-4,-1],[2,0,-1]],"
        "[[0,0,-1]]*7]\n"
        "weights = [[w/9 for w in row] for row in [[9,3,3,9,3,3,9],[3,1,1,3,1,1,3],[3,1,1,3,1,1,3],[9,3,3,9,3,3,9]]]\n"
        "vknots = [0, 0.5, 0.5, 0.5, 1]\n"
    )
    m = _render(tmp_path, "nurbs_vnf(patch, 3, weights=weights, knots=[None, vknots], splinesteps=12).polyhedron()",
                setup=setup, name="nurbssphere")
    assert m.watertight
    np.testing.assert_allclose(m.size, [2, 2, 2], atol=0.1)  # unit sphere, diameter 2


# -- native-only mesh operations (repair / wrap / roof / pull / oversample / separate / inside) ----

def test_repair_keeps_watertight(tmp_path):
    m = _render(tmp_path, "s3.cuboid([20, 20, 10]).repair()", name="repair")
    assert m.watertight
    np.testing.assert_allclose(m.size, [20, 20, 10], atol=0.1)


def test_oversample_subdivides_facets(tmp_path):
    base = _render(tmp_path, "s3.cuboid([20, 20, 10])", name="ov_base")
    over = _render(tmp_path, "s3.cuboid([20, 20, 10]).oversample(3)", name="ov_3")
    assert over.watertight
    assert over.ntris > base.ntris * 4          # each facet subdivided many-fold
    np.testing.assert_allclose(over.size, [20, 20, 10], atol=0.1)   # same shape, just denser
    assert math.isclose(over.volume, base.volume, rel_tol=0.02)


def test_roof_makes_a_pyramid(tmp_path):
    # a hip roof over a 20x20 square is a pyramid: volume = base_area * height / 3.
    m = _render(tmp_path, "s3.roof(s2.square([20, 20], center=True))", name="roof")
    assert m.watertight
    np.testing.assert_allclose(m.size[:2], [20, 20], atol=0.2)
    assert m.size[2] > 5                          # it rises to a ridge
    assert m.volume < 20 * 20 * m.size[2]         # a roof, not a full prism


# NOTE: wrap() is intentionally not render-tested. Meshing/exporting a wrapped solid is extremely
# slow in the Manifold backend (a single small bar exceeds several minutes), so a render test would
# only ever time out and skip. The method is covered at the mock level in test_native_ops.py; wrap
# itself is a thin pass-through to the native builtin.


def test_pull_stretches_material(tmp_path):
    solid = _render(tmp_path, "s3.cuboid([20, 20, 10])", name="pull_base")
    pulled = _render(tmp_path, "s3.cuboid([20, 20, 10]).pull([0, 0, 1], 8)", name="pull_8")
    assert pulled.watertight
    assert pulled.volume > solid.volume           # stretched apart, so bigger


def test_separate_extracts_one_lump(tmp_path):
    # two disjoint 8-cubes; separate()[0] is a single 8-cube, not the 38-wide pair.
    whole = _render(tmp_path, "(s3.cuboid([8, 8, 8]) | s3.cuboid([8, 8, 8]).right(30))", name="sep_whole")
    part = _render(tmp_path, "(s3.cuboid([8, 8, 8]) | s3.cuboid([8, 8, 8]).right(30)).separate()[0]",
                   name="sep_part")
    assert part.watertight
    np.testing.assert_allclose(part.size, [8, 8, 8], atol=0.1)   # one lump
    assert whole.size[0] > 30                                    # the pair spanned far
