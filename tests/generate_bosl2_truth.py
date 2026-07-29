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

"""Regenerate tests/bosl2_truth.json -- ground truth from the REAL BOSL2 via osuse().

This is the fixture tests/test_bosl2_reorient.py checks the pure-Python reorient/apply/arc
against. It needs the real app plus the patched BOSL2 (see CLAUDE.md), and must be run through
the PythonSCAD binary because osuse() only exists there:

    cd examples && TRUTH_OUT=../tests/bosl2_truth.json FROM_MAKE=1 \
      BOSL2_SCAD_DIR=~/Documents/OpenSCAD/libraries-pythonscad-patched \
      /Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD --trust-python \
      --enable python-engine --backend Manifold --export-format 3mf -o /tmp/t.3mf \
      ../tests/generate_bosl2_truth.py

The toolkit itself no longer calls osuse() for these; this script is the only remaining user,
kept solely so the fixture can be re-derived if BOSL2's semantics ever change.
"""
import os, sys, json
_examples = os.getcwd(); _root = os.path.dirname(_examples)
for _p in (_examples, _root):
    if _p not in sys.path: sys.path.insert(0, _p)
from base_bgtk import *
import base_bgtk
from pythonscad import osuse

# The pure-Python pybosl2/ port no longer osuse()s BOSL2, so load the real library directly here
# (this generator is the sole remaining osuse() user, kept to re-derive the fixture).
b = osuse(base_bgtk.BOSL2_STD_PATH)
out = {"reorient": [], "apply": [], "arc": [], "catenary": [], "helix": [], "turtle": [],
       "distrib": [], "color": [], "partition": [], "nurbs": [], "rounding": [], "isosurface": []}

ANCH = {"CENTER": CENTER, "BOTTOM": BOTTOM, "TOP": TOP,
        "BFL": BOTTOM+FRONT+LEFT, "TRB": TOP+RIGHT+BACK, "LEFT": LEFT}
ORI = {"TOP": TOP, "BOTTOM": BOTTOM, "LEFT": LEFT, "RIGHT": RIGHT, "FRONT": FRONT, "BACK": BACK}

def jl(x):
    try: return [jl(i) for i in x]
    except TypeError: return float(x)

for an, av in ANCH.items():
    for on, ov in ORI.items():
        for spin in (0, 45, 90, 180):
            for size in ([1,1,1], [10,20,30]):
                try:
                    m = b.reorient(anchor=av, spin=spin, orient=ov, size=size)
                    out["reorient"].append({"anchor": an, "orient": on, "spin": spin,
                                            "size": size, "m": jl(m)})
                except Exception as e:
                    out["reorient"].append({"anchor": an, "orient": on, "spin": spin,
                                            "size": size, "err": str(e)})

# apply: reuse a couple of matrices
m1 = b.reorient(anchor=CENTER, spin=30, orient=LEFT, size=[1,1,1])
for pts in ([[5,0,0],[-5,0,0]], [[0,3,-2]], [[1,2,3],[4,5,6],[-7,8,-9]]):
    out["apply"].append({"m": jl(m1), "pts": pts, "res": jl(b.apply(m1, pts))})

# arc
out["arc"].append({"kw": "r16_start0_ang60_n?", "res": jl(b.arc(r=16, start=0, angle=60))})
out["arc"].append({"kw": "r5_start30_ang90", "res": jl(b.arc(r=5, start=30, angle=90))})
out["arc"].append({"kw": "n8_pts3", "res": jl(b.arc(n=8, points=[[-0.5,0],[0,0.3],[0.5,0]]))})
out["arc"].append({"kw": "n12_pts3b", "res": jl(b.arc(n=12, points=[[-1,0],[0,1],[1,0]]))})
out["arc"].append({"kw": "wedge_r10_ang90", "res": jl(b.arc(r=10, angle=90, wedge=True))})
out["arc"].append({"kw": "range_r10_30_90_n?", "res": jl(b.arc(r=10, angle=[30,90]))})
out["arc"].append({"kw": "width10_thick3_n7", "res": jl(b.arc(n=7, width=10, thickness=3))})
out["arc"].append({"kw": "cp2pts_short_n6", "res": jl(b.arc(n=6, cp=[0,0], points=[[10,0],[0,10]]))})
out["arc"].append({"kw": "cp2pts_long_n6", "res": jl(b.arc(n=6, cp=[0,0], points=[[10,0],[0,10]], long=True))})
out["arc"].append({"kw": "corner_r3", "res": jl(b.arc(corner=[[0,10],[0,0],[10,0]], r=3))})

# catenary
out["catenary"].append({"kw": "w80_droop30_n20", "res": jl(b.catenary(width=80, droop=30, n=20))})
out["catenary"].append({"kw": "w80_angle45_n20", "res": jl(b.catenary(width=80, angle=45, n=20))})
out["catenary"].append({"kw": "w50_droopneg15_n15", "res": jl(b.catenary(width=50, droop=-15, n=15))})

# helix
out["helix"].append({"kw": "turns2.5_h100_r30", "res": jl(b.helix(turns=2.5, h=100, r=30))})
out["helix"].append({"kw": "flat_r1_50_r2_25_turns4", "res": jl(b.helix(h=0, r1=50, r2=25, l=0, turns=4))})
out["helix"].append({"kw": "turnsneg2_h60_r20", "res": jl(b.helix(turns=-2, h=60, r=20))})

# turtle
out["turtle"].append({"kw": "square_left", "res": jl(b.turtle(["move",40,"left",90,"move",40,"left",90,"move",40,"left",90,"move",40]))})
out["turtle"].append({"kw": "repeat4", "res": jl(b.turtle(["repeat",4,["move",40,"left",90]]))})
out["turtle"].append({"kw": "arcleft_rounded", "res": jl(b.turtle(["move",40,"arcleft",8,"move",40,"arcleft",8,"move",40,"arcleft",8,"move",40,"arcleft",8]))})
out["turtle"].append({"kw": "arcrightto", "res": jl(b.turtle(["move",20,"arcrightto",10,-90]))})

# distributors (function form: a list of 4x4 transformation matrices)
_dpath = [[0,0],[20,0],[20,20],[40,20]]
out["distrib"].append({"kw": "move_copies", "res": jl(b.move_copies([[0,0,0],[5,5,5],[10,0,-3]]))})
out["distrib"].append({"kw": "xcopies_n", "res": jl(b.xcopies(20, n=3))})
out["distrib"].append({"kw": "ycopies_l", "res": jl(b.ycopies(l=50, n=4))})
out["distrib"].append({"kw": "zcopies_list", "res": jl(b.zcopies([1,3,7]))})
out["distrib"].append({"kw": "line_spacing", "res": jl(b.line_copies(spacing=10, n=5))})
out["distrib"].append({"kw": "line_vec_l", "res": jl(b.line_copies(l=[10,20,0], n=4))})
out["distrib"].append({"kw": "grid_nspacing", "res": jl(b.grid_copies(n=[3,2], spacing=10))})
out["distrib"].append({"kw": "grid_stagger", "res": jl(b.grid_copies(spacing=8, n=[4,3], stagger=True))})
out["distrib"].append({"kw": "rot_n6", "res": jl(b.rot_copies(n=6))})
out["distrib"].append({"kw": "xrot_ring", "res": jl(b.xrot_copies(n=5, r=10))})
out["distrib"].append({"kw": "yrot_ring", "res": jl(b.yrot_copies(n=4, r=12))})
out["distrib"].append({"kw": "zrot_list", "res": jl(b.zrot_copies([0,30,60], r=8))})
out["distrib"].append({"kw": "arc_r", "res": jl(b.arc_copies(n=6, r=20))})
out["distrib"].append({"kw": "arc_ellipse", "res": jl(b.arc_copies(n=5, rx=20, ry=10, sa=30, ea=200))})
out["distrib"].append({"kw": "sphere", "res": jl(b.sphere_copies(n=8, r=30, cone_ang=90))})
out["distrib"].append({"kw": "mirror_off", "res": jl(b.mirror_copy([1,1,0], offset=2))})
out["distrib"].append({"kw": "xflip", "res": jl(b.xflip_copy(offset=3, x=1))})
out["distrib"].append({"kw": "path_n", "res": jl(b.path_copies(_dpath, n=5))})

# color: hsl/hsv -> RGB(A)
for _h in (0, 60, 120, 180, 240, 300, 270, 33):
    out["color"].append({"fn": "hsl", "args": [_h, 0.75, 0.6], "res": jl(b.hsl(_h, 0.75, 0.6))})
    out["color"].append({"fn": "hsv", "args": [_h, 0.75, 0.9], "res": jl(b.hsv(_h, 0.75, 0.9))})
out["color"].append({"fn": "hsl", "args": [200, 1, 0.5, 0.4], "res": jl(b.hsl(200, 1, 0.5, 0.4))})
out["color"].append({"fn": "hsv", "args": [200, 1, 1, 0.4], "res": jl(b.hsv(200, 1, 1, 0.4))})

# partition_path (polygonal patterns are $fn-independent; arc-based ones use the default $fa/$fs)
def _pp(desc, **kw):
    return jl(b.partition_path(desc, **kw))
out["partition"].append({"kw": "flat", "res": _pp(["flat"])})
out["partition"].append({"kw": "sawtooth", "res": _pp(["sawtooth"])})
out["partition"].append({"kw": "square", "res": _pp(["square"])})
out["partition"].append({"kw": "triangle", "res": _pp(["triangle"])})
out["partition"].append({"kw": "dovetail", "res": _pp(["dovetail"])})
out["partition"].append({"kw": "hammerhead", "res": _pp(["hammerhead"])})
out["partition"].append({"kw": "comb", "res": _pp(["comb"])})
out["partition"].append({"kw": "finger", "res": _pp(["finger"])})
out["partition"].append({"kw": "sawtooth_xflip", "res": _pp(["sawtooth xflip"])})
out["partition"].append({"kw": "sawtooth_addflip", "res": _pp(["sawtooth addflip"])})
out["partition"].append({"kw": "sawtooth_3x", "res": _pp(["sawtooth 3x"])})
out["partition"].append({"kw": "hammerhead_yflip", "res": _pp(["hammerhead yflip"])})
out["partition"].append({"kw": "square_skew", "res": _pp(["square skew:15"])})
out["partition"].append({"kw": "square_pinch", "res": _pp(["square pinch:30"])})
out["partition"].append({"kw": "mixed_flat", "res": _pp([40, "dovetail", 40])})
out["partition"].append({"kw": "closed_y", "res": _pp([30, "hammerhead", 30], y=150)})

# nurbs curve/patch/elevate evaluation (nurbs.scad is not in std.scad, so osuse a wrapper that
# includes both std.scad and nurbs.scad by absolute path)
_bdir = os.path.dirname(base_bgtk.BOSL2_STD_PATH)
_wrap = os.path.join(_bdir, "_truth_nurbs_wrapper.scad")
open(_wrap, "w").write("include <%s>\ninclude <%s>\n" % (
    os.path.join(_bdir, "std.scad"), os.path.join(_bdir, "nurbs.scad")))
bn = osuse(_wrap)
_c3 = [[0,0,0],[10,20,5],[30,-10,10],[50,20,0],[60,0,15]]
_c2 = [[0,0],[10,20],[30,-10],[50,20],[60,0]]
out["nurbs"].append({"kw": "clamped3_ss", "res": jl(bn.nurbs_curve(_c3, 3, splinesteps=5))})
out["nurbs"].append({"kw": "clamped2_u", "res": jl(bn.nurbs_curve(_c2, 3, u=[0,0.2,0.4,0.6,0.8,1]))})
out["nurbs"].append({"kw": "open3_ss", "res": jl(bn.nurbs_curve(_c3, 3, splinesteps=4, type="open"))})
out["nurbs"].append({"kw": "closed2_ss", "res": jl(bn.nurbs_curve(_c2, 2, splinesteps=4, type="closed"))})
out["nurbs"].append({"kw": "deg2_ss", "res": jl(bn.nurbs_curve(_c3, 2, splinesteps=6))})
out["nurbs"].append({"kw": "weighted_u", "res": jl(bn.nurbs_curve([[0,0],[10,0],[10,10],[0,10]], 2, u=[0,0.25,0.5,0.75,1], weights=[1,5,1,5]))})
out["nurbs"].append({"kw": "mult_ss", "res": jl(bn.nurbs_curve(_c3+[[70,10,5]], 3, splinesteps=4, mult=[1,2,1]))})
out["nurbs"].append({"kw": "knots_u", "res": jl(bn.nurbs_curve(_c2, 3, u=[0,0.3,0.6,1], knots=[0,0.4,1]))})
_patch = [[[-50,50,0],[-16,50,20],[16,50,20],[50,50,0]],
          [[-50,16,20],[-16,16,40],[16,16,40],[50,16,20]],
          [[-50,-16,20],[-16,-16,40],[16,-16,40],[50,-16,20]],
          [[-50,-50,0],[-16,-50,20],[16,-50,20],[50,-50,0]]]
out["nurbs"].append({"kw": "patch3_ss", "res": jl(bn.nurbs_patch_points(_patch, 3, splinesteps=3))})
out["nurbs"].append({"kw": "patch_uv", "res": jl(bn.nurbs_patch_points(_patch, 3, u=[0,0.5,1], v=[0,0.5,1]))})
out["nurbs"].append({"kw": "patch_mixed", "res": jl(bn.nurbs_patch_points(_patch, [3,2], splinesteps=[2,3]))})
_el = bn.nurbs_elevate_degree(_c2, 3)
out["nurbs"].append({"kw": "elevate_deg", "res": _el[1]})
out["nurbs"].append({"kw": "elevate_ctrl", "res": jl(_el[2])})

# rounding: round_corners (circle/smooth/chamfer, radius/cut/joint/width) and smooth_path
_sq = [[0,0],[40,0],[40,30],[0,30]]
_op = [[0,0],[40,0],[40,30],[20,45],[0,30]]
_p3 = [[0,0,0],[40,0,0],[40,40,20],[0,40,20]]
_wig = [[0,0],[10,30],[30,-10],[50,20],[70,0]]
out["rounding"].append({"kw": "circle_radius", "res": jl(b.round_corners(_sq, radius=5))})
out["rounding"].append({"kw": "circle_cut", "res": jl(b.round_corners(_sq, cut=3))})
out["rounding"].append({"kw": "circle_joint", "res": jl(b.round_corners(_sq, joint=5))})
out["rounding"].append({"kw": "smooth_joint", "res": jl(b.round_corners(_sq, method="smooth", joint=8))})
out["rounding"].append({"kw": "smooth_cut", "res": jl(b.round_corners(_sq, method="smooth", cut=2))})
out["rounding"].append({"kw": "smooth_k", "res": jl(b.round_corners(_sq, method="smooth", joint=8, k=0.8))})
out["rounding"].append({"kw": "chamfer_joint", "res": jl(b.round_corners(_sq, method="chamfer", joint=6))})
out["rounding"].append({"kw": "chamfer_cut", "res": jl(b.round_corners(_sq, method="chamfer", cut=4))})
out["rounding"].append({"kw": "chamfer_width", "res": jl(b.round_corners(_sq, method="chamfer", width=5))})
out["rounding"].append({"kw": "open_circle", "res": jl(b.round_corners(_op, radius=5, closed=False))})
out["rounding"].append({"kw": "d3_smooth", "res": jl(b.round_corners(_p3, method="smooth", joint=6))})
out["rounding"].append({"kw": "d3_chamfer", "res": jl(b.round_corners(_p3, method="chamfer", joint=6))})
out["rounding"].append({"kw": "smoothpath_rel", "res": jl(b.smooth_path(_wig, relsize=0.4))})
out["rounding"].append({"kw": "smoothpath_size", "res": jl(b.smooth_path(_wig, size=5))})
out["rounding"].append({"kw": "smoothpath_closed", "res": jl(b.smooth_path(_sq, relsize=0.3, closed=True))})

# isosurface metaball field-function values (isosurface.scad not in std; wrap with helper functions)
_iwrap = os.path.join(_bdir, "_truth_iso_wrapper.scad")
open(_iwrap, "w").write(
    "include <%s>\ninclude <%s>\n" % (os.path.join(_bdir, "std.scad"), os.path.join(_bdir, "isosurface.scad"))
    + "function _t_sphere(pt,r,cut,inf) = mb_sphere(r=r,cutoff=cut,influence=inf)[0](pt);\n"
    + "function _t_cuboid(pt,sz,sq) = mb_cuboid(sz,squareness=sq)[0](pt);\n"
    + "function _t_torus(pt,rmaj,rmin) = mb_torus(rmaj,rmin)[0](pt);\n"
    + "function _t_capsule(pt,h,r) = mb_capsule(h,r)[0](pt);\n"
    + "function _t_disk(pt,h,r) = mb_disk(h,r)[0](pt);\n"
    + "function _t_octa(pt,sz,sq) = mb_octahedron(sz,squareness=sq)[0](pt);\n"
    + "function _t_conn(pt,p1,p2,r) = mb_connector(p1,p2,r)[0](pt);\n")
bi = osuse(_iwrap)
_ipts = [[5,0,0],[10,3,2],[0,8,6],[12,4,-5],[3,3,3]]
out["isosurface"].append({"fn": "sphere", "res": [bi._t_sphere(p, 5, 1e9, 1) for p in _ipts]})
out["isosurface"].append({"fn": "sphere_cut", "res": [bi._t_sphere(p, 5, 12, 1.5) for p in _ipts]})
out["isosurface"].append({"fn": "cuboid", "res": [bi._t_cuboid(p, 20, 0.5) for p in _ipts]})
out["isosurface"].append({"fn": "cuboid_sq", "res": [bi._t_cuboid(p, [16,20,24], 0.8) for p in _ipts]})
out["isosurface"].append({"fn": "torus", "res": [bi._t_torus(p, 8, 3) for p in _ipts]})
out["isosurface"].append({"fn": "capsule", "res": [bi._t_capsule(p, 24, 4) for p in _ipts]})
out["isosurface"].append({"fn": "disk", "res": [bi._t_disk(p, 6, 12) for p in _ipts]})
out["isosurface"].append({"fn": "octa", "res": [bi._t_octa(p, 20, 0.5) for p in _ipts]})
out["isosurface"].append({"fn": "connector", "res": [bi._t_conn(p, [-10,0,0], [10,5,3], 4) for p in _ipts]})

open(os.environ["TRUTH_OUT"], "w").write(json.dumps(out, indent=1))
cube(1).show()
