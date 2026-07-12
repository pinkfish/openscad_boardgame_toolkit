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


# LibFile: pysolidfive/shapes3d.py
#    The 3-D layer: PyShape (the lazy symbolic-SDF solid) and every 3-D shape constructor --
#    cuboid/cube/sphere/cyl-family/torus/tube/pie_slice/prismoid/rect_tube/wedge/octahedron/
#    convex_polyhedron/teardrop/onion/heightfield, the standalone cutters
#    (interior_fillet/rounding_edge_mask/polygon_extrude), and polygon_prism (the
#    offset_sweep-equivalent extrusion with rim treatments). See pysolidfive/__init__.py's
#    module docstring for the design rationale.
#
# FileGroup: pysolidfive

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Callable

import libfive as lv
import numpy as np

from pythonscad import frep
from pysolidfive._constants import CENTER, BOTTOM, TOP, LEFT, RIGHT, FRONT, BACK
from pysolidfive._edges import (
    EDGES_ALL,
    _anchor_offset_box3,
    _anchor_offset_cyl,
    _anchor_offset_hull3,
    _anchor_offset_sphere,
    _edges,
    _pick_radius,
)
from pysolidfive.paths import (
    as_path_list,
    as_points,
    _PENALTY,
    _SQRT2,
    _lv_hypot,
    _polygon_dist2_xy,
    _polygon_sdf_xy,
    _radius,
    _rect2d,
)



def _matmul3(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _axis_angle_matrix(deg: float, axis: list[float]) -> list[list[float]]:
    """Standard Rodrigues' rotation matrix for `deg` degrees around `axis` (need not be unit)."""
    ang = math.radians(deg)
    n = math.sqrt(sum(a * a for a in axis))
    ax, ay, az = (a / n for a in axis)
    c, s, t = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    return [
        [t * ax * ax + c, t * ax * ay - s * az, t * ax * az + s * ay],
        [t * ax * ay + s * az, t * ay * ay + c, t * ay * az - s * ax],
        [t * ax * az - s * ay, t * ay * az + s * ax, t * az * az + c],
    ]


def _rotation_matrix(a, v: list[float] | None = None) -> list[list[float]]:
    """3x3 rotation matrix matching the real rotate(obj, a, v)'s two calling conventions:
    `a` a lone angle (degrees) with an explicit axis `v`, or (v is None) `a` a 3-vector of Euler
    angles [x, y, z] applied X-then-Y-then-Z -- the same composition order OpenSCAD's own
    rotate([x, y, z]) uses."""
    if v is not None:
        return _axis_angle_matrix(a, v)
    ax, ay, az = a
    rx = _axis_angle_matrix(ax, [1, 0, 0])
    ry = _axis_angle_matrix(ay, [0, 1, 0])
    rz = _axis_angle_matrix(az, [0, 0, 1])
    return _matmul3(_matmul3(rz, ry), rx)


def _rounded_box_sdf(x, y, z, size: list[float], r: float):
    """Exact SDF for a box uniformly rounded on every edge and corner: the Minkowski sum of a
    box (shrunk by `r` on every side) with a sphere of radius `r` -- the same construction
    bosl2.shapes3d.cuboid() itself special-cases via a real minkowski() for edges="ALL". Unlike
    _cuboid_edge_sdf()'s general per-axis-plane composition (max() of three independently
    rounded-rectangle extrusions, which only *approximates* the true corner blend and leaves a
    visible seam where the three rounded faces meet), this is a single closed-form expression
    with an exact, seamless spherical corner -- no per-axis composition, so no seam.
    """
    hx, hy, hz = [s / 2 - r for s in size]
    qx = lv.abs(x) - hx
    qy = lv.abs(y) - hy
    qz = lv.abs(z) - hz
    mqx, mqy, mqz = lv.max(qx, 0), lv.max(qy, 0), lv.max(qz, 0)
    outside = lv.sqrt(mqx * mqx + mqy * mqy + mqz * mqz)
    inside = lv.min(lv.max(lv.max(qx, qy), qz), 0)
    return outside + inside - r


def _edge_matrices(amount: float, edge_set: list[list[int]], mode: str):
    """The per-edge treatment state for a single (amount, edge_set, mode) selection, as the
    3x4 amounts/modes matrices _cuboid_edge_sdf() consumes (EDGE_OFFSETS row/column order)."""
    amounts = [[amount if edge_set[a][i] else 0.0 for i in range(4)] for a in range(3)]
    modes = [[mode] * 4 for _ in range(3)]
    return amounts, modes


def _cuboid_edge_sdf(x, y, z, size: list[float], amounts: list[list[float]], modes: list[list[str]]):
    """The cuboid SDF (as an explicit function of the given x/y/z trees, so callers can pass
    shifted coordinates to compose translation) with an independent treatment per edge:
    `amounts[axis][i]` (rounding radius or chamfer size, per `modes[axis][i]`) in EDGE_OFFSETS
    order. Everything is folded into ONE evaluation -- chaining several treatments by
    max()-ing full cuboid SDFs (the old .round()/.chamfer() composition) leaves their zero
    sets coincident along every untreated face, which libfive's mesher refines to the bitter
    end (a plain box ballooned to ~1M triangles and minutes of meshing).
    """
    if all(m == "round" for row in modes for m in row) and len({a for row in amounts for a in row}) == 1:
        # Uniform treatment (including the plain r=0 box): the exact closed-form SDF.
        return _rounded_box_sdf(x, y, z, size, amounts[0][0])

    p = [x, y, z]
    b = [s / 2 for s in size]
    # Perpendicular-axis pairs, in the same (row, column) order as EDGE_OFFSETS: axis 0 (X)
    # varies over (Y, Z), axis 1 (Y) over (X, Z), axis 2 (Z) over (X, Y).
    axes_perp = [(1, 2), (0, 2), (0, 1)]

    def axis_sdf(axis: int):
        pa, pb = axes_perp[axis]
        d2d = _rect2d(p[pa], p[pb], b[pa], b[pb], amounts[axis], modes[axis])
        slab = lv.abs(p[axis]) - b[axis]
        return lv.max(d2d, slab)

    return lv.max(lv.max(axis_sdf(0), axis_sdf(1)), axis_sdf(2))


class PyShape:
    """Wraps a libfive SDF, kept as a *symbolic* function of (x, y, z) rather than an
    already-evaluated tree or an already-meshed solid, plus the bounding box (`mn`/`mx`)
    frep() needs and (for cuboid-shaped instances) enough metadata to add more edge
    treatments after the fact.

    Extra controls beyond a bare `frep()` call:
      - Lazy, cached meshing: the real PythonSCAD/libfive C extension is only touched by
        .mesh() (or by falling through __getattr__ to a real method like .show()/.color()),
        so a chain of edits never re-meshes early.
      - translate(v): shifts the SDF itself (`f(p) -> f(p - v)`), exact and free -- no
        meshing involved -- and keeps chamfer()/round() working correctly afterwards by
        tracking where the cuboid's own local origin currently sits.
      - Boolean composition with another PyShape (`|` union, `&` intersection, `-`
        difference) via min()/max()/negate on the two SDFs directly, cheaper and more
        exact than meshing both shapes first and doing mesh-level CSG.
      - round(radius, edges=, except_edges=) / chamfer(size, edges=, except_edges=):
        add more edge treatment to an existing cuboid-shaped PyShape. Because this
        intersects (max()) the requested treatment into the *current* SDF rather than
        rebuilding from scratch, edges can be built up incrementally with different
        treatments -- e.g. `cuboid(size).round(2, edges="Z").chamfer(1, edges=[TOP+LEFT])`
        -- which a single bosl2.shapes3d.cuboid() call can't do (rounding/chamfer are
        mutually exclusive there, one radius for the whole call).

    CAVEAT: like bosl2.shapes3d.Bosl2Solid, this is a plain Python wrapper (composition),
    not a subclass of the real native PyOpenSCAD type. round()/chamfer() additionally only
    make sense for cuboid-shaped instances (built by cuboid(), or by a prior round()/
    chamfer() call on one) -- they assert if `cuboid_size` isn't set, the same restriction
    Bosl2Solid places on its own edge/corner masking methods.
    """

    def __init__(
        self, sdf_fn, mn, mx, res: int = 10, cuboid_size=None, cuboid_center=(0.0, 0.0, 0.0),
        cuboid_edge_amounts=None, cuboid_edge_modes=None,
    ):
        self._sdf_fn = sdf_fn
        self.mn = list(mn)
        self.mx = list(mx)
        self.res = res
        self.cuboid_size = list(cuboid_size) if cuboid_size is not None else None
        self.cuboid_center = tuple(cuboid_center)
        # 3x4 per-edge treatment state (EDGE_OFFSETS order) for cuboid-shaped instances --
        # round()/chamfer() MERGE into these and rebuild one single-pass SDF instead of
        # max()-wrapping treatment layers (see _cuboid_edge_sdf's docstring for why).
        self.cuboid_edge_amounts = [row[:] for row in cuboid_edge_amounts] if cuboid_edge_amounts is not None else None
        self.cuboid_edge_modes = [row[:] for row in cuboid_edge_modes] if cuboid_edge_modes is not None else None
        self._mesh_cache = None

    def _wrap(self, sdf_fn, mn, mx, cuboid_size=None, cuboid_center=(0.0, 0.0, 0.0),
              cuboid_edge_amounts=None, cuboid_edge_modes=None):
        return PyShape(sdf_fn, mn, mx, self.res, cuboid_size, cuboid_center, cuboid_edge_amounts, cuboid_edge_modes)

    def sdf(self):
        """The fully-evaluated libfive expression tree, at the real coordinate trees."""
        return self._sdf_fn(lv.x(), lv.y(), lv.z())

    def mesh(self):
        """Mesh this SDF into a real solid via frep() (cached after the first call).

        Pads `mn`/`mx` slightly beyond the shape's own tight bounding box before sampling:
        frep()'s octree evaluator needs the surface to lie strictly *inside* the sampled
        domain to see a sign change. Every constructor here sets mn/mx to the shape's exact
        bounds (e.g. cuboid()'s +-size/2), so any flat face sits exactly on the domain
        boundary -- libfive then finds no sign change there and leaves that face unmeshed
        (a hollow shell for e.g. a rounded box/cylinder, or an entirely empty mesh for a
        plain unrounded box, whose every face is flush with the domain boundary).
        """
        if self._mesh_cache is None:
            pad = [max(1e-3, (b - a) * 0.01) for a, b in zip(self.mn, self.mx)]
            mn = [a - p for a, p in zip(self.mn, pad)]
            mx = [b + p for b, p in zip(self.mx, pad)]
            self._mesh_cache = frep(self.sdf(), mn, mx, self.res)
        return self._mesh_cache

    def __getattr__(self, name):
        # Anything not defined on PyShape itself (color/show/... or any other real PyOpenSCAD
        # method) falls through to the meshed solid.
        return getattr(self.mesh(), name)

    # ---- SDF-level composition ----

    def translate(self, v) -> "PyShape":
        tx, ty, tz = (list(v) + [0.0, 0.0, 0.0])[:3]
        fn = self._sdf_fn
        new_fn = lambda x, y, z: fn(x - tx, y - ty, z - tz)  # noqa: E731
        new_mn = [self.mn[0] + tx, self.mn[1] + ty, self.mn[2] + tz]
        new_mx = [self.mx[0] + tx, self.mx[1] + ty, self.mx[2] + tz]
        new_center = (self.cuboid_center[0] + tx, self.cuboid_center[1] + ty, self.cuboid_center[2] + tz)
        return self._wrap(new_fn, new_mn, new_mx, self.cuboid_size, new_center, self.cuboid_edge_amounts, self.cuboid_edge_modes)

    def rotate(self, a, v: list[float] | None = None) -> "PyShape":
        """Rotate the SDF itself (`f(p) -> f(R^-1 p)`), exact and free -- no meshing involved,
        so (like translate()) a shape can still be .round()ed/.chamfer()ed/composed afterward
        without forcing an early mesh. Matches the real rotate(obj, a, v)'s two calling
        conventions: `rotate(angle, axis)`, or `rotate([x, y, z])` for Euler angles.

        Unlike translate(), this drops cuboid_size/cuboid_center metadata (so round()/chamfer()
        assert afterward) -- edges="TOP"/"LEFT"/etc. are global-frame selectors, evaluated
        before any rotation, the same order bosl2's own anchor/edges-then-spin/orient applies
        them in, so treating edges post-rotation wouldn't mean what it looks like it means.
        """
        m = _rotation_matrix(a, v)
        mt = [[m[j][i] for j in range(3)] for i in range(3)]  # transpose == inverse for a rotation
        fn = self._sdf_fn
        new_fn = lambda x, y, z: fn(  # noqa: E731
            mt[0][0] * x + mt[0][1] * y + mt[0][2] * z,
            mt[1][0] * x + mt[1][1] * y + mt[1][2] * z,
            mt[2][0] * x + mt[2][1] * y + mt[2][2] * z,
        )
        corners = [
            [self.mn[0] if i & 1 == 0 else self.mx[0], self.mn[1] if i & 2 == 0 else self.mx[1], self.mn[2] if i & 4 == 0 else self.mx[2]]
            for i in range(8)
        ]
        rotated = [[sum(m[r][k] * c[k] for k in range(3)) for r in range(3)] for c in corners]
        new_mn = [min(c[i] for c in rotated) for i in range(3)]
        new_mx = [max(c[i] for c in rotated) for i in range(3)]
        return self._wrap(new_fn, new_mn, new_mx)

    def scale(self, v) -> "PyShape":
        """Scale the SDF (`f(p) -> s_min * f(p / s)`), exact zero set, no meshing involved --
        `v` a single factor or a per-axis [sx, sy, sz], matching the real scale(). The value is
        renormalized by the smallest factor so it stays a conservative (never-overestimating)
        distance under non-uniform scaling; for uniform scaling it stays exact. Drops
        cuboid_size/cuboid_center metadata (so round()/chamfer() assert afterward), same
        rationale as rotate(): edge selectors are pre-transform concepts.
        """
        s = [float(a) for a in v] if isinstance(v, (list, tuple)) else [float(v)] * 3
        assert all(a > 0 for a in s), f"scale() factors must be positive, got {s}"
        fn = self._sdf_fn
        smin = min(s)
        new_fn = lambda x, y, z: smin * fn(x / s[0], y / s[1], z / s[2])  # noqa: E731
        new_mn = [self.mn[i] * s[i] for i in range(3)]
        new_mx = [self.mx[i] * s[i] for i in range(3)]
        return self._wrap(new_fn, new_mn, new_mx)

    def mirror(self, v: list[float]) -> "PyShape":
        """Reflect across the plane through the origin with normal `v` (`f(p) -> f(Mp)`, with
        M the Householder reflection), exact and free, matching the real mirror(). Drops
        cuboid_size/cuboid_center metadata, same rationale as rotate(): edge selectors are
        pre-transform concepts."""
        nx, ny, nz = (float(a) for a in v)
        nlen = math.sqrt(nx * nx + ny * ny + nz * nz)
        assert nlen > 0, "mirror() normal must be nonzero"
        nx, ny, nz = nx / nlen, ny / nlen, nz / nlen
        m = [
            [1 - 2 * nx * nx, -2 * nx * ny, -2 * nx * nz],
            [-2 * nx * ny, 1 - 2 * ny * ny, -2 * ny * nz],
            [-2 * nx * nz, -2 * ny * nz, 1 - 2 * nz * nz],
        ]
        fn = self._sdf_fn
        # A reflection is its own inverse, so the same matrix maps sample points back.
        new_fn = lambda x, y, z: fn(  # noqa: E731
            m[0][0] * x + m[0][1] * y + m[0][2] * z,
            m[1][0] * x + m[1][1] * y + m[1][2] * z,
            m[2][0] * x + m[2][1] * y + m[2][2] * z,
        )
        corners = [
            [self.mn[0] if i & 1 == 0 else self.mx[0], self.mn[1] if i & 2 == 0 else self.mx[1], self.mn[2] if i & 4 == 0 else self.mx[2]]
            for i in range(8)
        ]
        refl = [[sum(m[r][k] * c[k] for k in range(3)) for r in range(3)] for c in corners]
        new_mn = [min(c[i] for c in refl) for i in range(3)]
        new_mx = [max(c[i] for c in refl) for i in range(3)]
        return self._wrap(new_fn, new_mn, new_mx)

    def __or__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.min(fa(x, y, z), fb(x, y, z))  # noqa: E731
        mn = [min(self.mn[i], other.mn[i]) for i in range(3)]
        mx = [max(self.mx[i], other.mx[i]) for i in range(3)]
        return self._wrap(new_fn, mn, mx)

    def __and__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.max(fa(x, y, z), fb(x, y, z))  # noqa: E731
        # The intersection can only live where BOTH boxes overlap -- so the meshing region
        # (and its resolution budget) shrinks to the overlap, which is also what makes
        # cropping a big shape with a small cube cheap.
        mn = [max(self.mn[i], other.mn[i]) for i in range(3)]
        mx = [min(self.mx[i], other.mx[i]) for i in range(3)]
        return self._wrap(new_fn, mn, mx)

    def __sub__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.max(fa(x, y, z), -fb(x, y, z))  # noqa: E731
        return self._wrap(new_fn, list(self.mn), list(self.mx))

    # ---- cuboid-only edge treatments ----

    def _edge_treat(self, amount: float, edges, except_edges, mode: str) -> "PyShape":
        assert self.cuboid_size is not None, f"{mode}() requires a cuboid-shaped PyShape (from pysolidfive.cuboid())"
        assert self.cuboid_edge_amounts is not None and self.cuboid_edge_modes is not None, (
            f"{mode}() requires the cuboid's per-edge treatment state (lost by rotate()/scale()/booleans)"
        )
        edge_set = _edges(edges, except_edges or [])
        amounts = [row[:] for row in self.cuboid_edge_amounts]
        modes = [row[:] for row in self.cuboid_edge_modes]
        for a in range(3):
            for i in range(4):
                if edge_set[a][i]:
                    amounts[a][i] = amount
                    modes[a][i] = mode
        cx, cy, cz = self.cuboid_center
        size = self.cuboid_size
        # Rebuild ONE single-pass SDF from the merged state rather than max()-wrapping the
        # current SDF -- stacked coincident zero sets make libfive's mesher explode.
        new_fn = lambda x, y, z: _cuboid_edge_sdf(x - cx, y - cy, z - cz, size, amounts, modes)  # noqa: E731
        return self._wrap(new_fn, list(self.mn), list(self.mx), self.cuboid_size, self.cuboid_center, amounts, modes)

    def round(self, radius: float, edges: str | list = "ALL", except_edges: list | None = None) -> "PyShape":
        """Round the selected edges by `radius`, in addition to any existing edge treatment."""
        return self._edge_treat(radius, edges, except_edges, "round")

    def chamfer(self, size: float, edges: str | list = "ALL", except_edges: list | None = None) -> "PyShape":
        """Chamfer the selected edges by `size`, in addition to any existing edge treatment."""
        return self._edge_treat(size, edges, except_edges, "chamfer")


# ---------------------------------------------------------------------------
# Section: Named CSG combinators (union / difference / intersection / hull)
# ---------------------------------------------------------------------------


def _as_shape_list(shapes: tuple) -> list[PyShape]:
    """Varargs-or-single-iterable: `union(a, b)` and `union([a, b])` both work, matching the
    two calling conventions the box libraries already mix (OpenSCAD-style children vs.
    bosl2-style list arguments)."""
    if len(shapes) == 1 and isinstance(shapes[0], (list, tuple)):
        shapes = tuple(shapes[0])
    out = list(shapes)
    assert out, "need at least one shape"
    assert all(isinstance(s, PyShape) for s in out), (
        f"every argument must be a PyShape, got {[type(s).__name__ for s in out]}"
    )
    return out


def _balanced(op, vals: list):
    """Reduce `vals` with `op` as a balanced tree (depth log n) rather than a left fold
    (depth n) -- same node count either way, but libfive re-evaluates the whole expression
    per sample point and shallow trees keep its interval pruning effective on wide unions."""
    while len(vals) > 1:
        vals = [op(vals[i], vals[i + 1]) if i + 1 < len(vals) else vals[i] for i in range(0, len(vals), 2)]
    return vals[0]


def union(*shapes: PyShape) -> PyShape:
    """The union of the given PyShapes (min() of their SDFs), as one PyShape -- the named,
    n-ary form of the `|` operator, matching OpenSCAD's union(){}.

    Accepts either varargs (`union(a, b, c)`) or a single list (`union([a, b, c])`). The
    result's meshing resolution is the finest (max) `res` among the children.

    Examples:
        .. pythonscad-example::

            a = pysolidfive.cuboid([20.0, 20.0, 10.0], rounding=3, res=10)
            b = pysolidfive.sphere(r=8, res=10).translate([0.0, 0.0, 8.0])
            shape = pysolidfive.union(a, b)
            shape.show()
    """
    shs = _as_shape_list(shapes)
    if len(shs) == 1:
        return shs[0]
    fns = [s._sdf_fn for s in shs]
    sdf_fn = lambda x, y, z: _balanced(lv.min, [f(x, y, z) for f in fns])  # noqa: E731
    mn = [min(s.mn[i] for s in shs) for i in range(3)]
    mx = [max(s.mx[i] for s in shs) for i in range(3)]
    return PyShape(sdf_fn, mn, mx, max(s.res for s in shs))


def intersection(*shapes: PyShape) -> PyShape:
    """The intersection of the given PyShapes (max() of their SDFs), as one PyShape -- the
    named, n-ary form of the `&` operator, matching OpenSCAD's intersection(){}.

    Accepts either varargs or a single list. The meshing region shrinks to the overlap of
    the children's bounding boxes (which is what makes cropping a big shape with a small
    one cheap); asserts if the boxes don't overlap at all, since the intersection SDF
    would then have nothing to mesh.

    Examples:
        .. pythonscad-example::

            a = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=4, res=10)
            b = pysolidfive.sphere(r=12, res=10)
            shape = pysolidfive.intersection(a, b)
            shape.show()
    """
    shs = _as_shape_list(shapes)
    if len(shs) == 1:
        return shs[0]
    fns = [s._sdf_fn for s in shs]
    sdf_fn = lambda x, y, z: _balanced(lv.max, [f(x, y, z) for f in fns])  # noqa: E731
    mn = [max(s.mn[i] for s in shs) for i in range(3)]
    mx = [min(s.mx[i] for s in shs) for i in range(3)]
    assert all(mn[i] < mx[i] for i in range(3)), (
        f"intersection(): the shapes' bounding boxes don't overlap (got mn={mn}, mx={mx})"
    )
    return PyShape(sdf_fn, mn, mx, max(s.res for s in shs))


def difference(shape: PyShape, *tools: PyShape) -> PyShape:
    """`shape` minus the union of every `tool` (max(f, -min(tools))), as one PyShape -- the
    named, n-ary form of the `-` operator, matching OpenSCAD's difference(){} (first child
    keeps, the rest cut).

    Accepts the tools as varargs or a single list; with no tools, returns `shape` unchanged.
    Keeps `shape`'s bounds and resolution, like `-`.

    Examples:
        .. pythonscad-example::

            a = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=3, res=10)
            b = pysolidfive.zcyl(h=30, r=5, res=10)
            c = pysolidfive.xcyl(h=30, r=5, res=10)
            shape = pysolidfive.difference(a, b, c)
            shape.show()
    """
    assert isinstance(shape, PyShape), f"difference() base must be a PyShape, got {type(shape).__name__}"
    if not tools:
        return shape
    tls = _as_shape_list(tools)
    fa = shape._sdf_fn
    fns = [t._sdf_fn for t in tls]
    sdf_fn = lambda x, y, z: lv.max(fa(x, y, z), -_balanced(lv.min, [f(x, y, z) for f in fns]))  # noqa: E731
    return PyShape(sdf_fn, list(shape.mn), list(shape.mx), shape.res)


def _support_points(points, n_dirs: int):
    """Decimate a point cloud to at most `n_dirs + 6` extreme (support) points: for each of
    `n_dirs` directions spread over the sphere (a Fibonacci lattice, plus the 6 axis
    directions so bounding-box extremes always survive), keep the farthest point along it.
    The hull of the survivors is an inscribed approximation of the cloud's hull: exact at
    every vertex that is the unique maximizer of some kept direction (a cuboid's 8 corners
    all are, well before n_dirs reaches double digits), with error bounded by the direction
    spacing for smooth clouds."""
    pts = np.asarray(points, dtype=float)
    i = np.arange(n_dirs)
    golden = math.pi * (3.0 - math.sqrt(5.0))
    zc = 1.0 - 2.0 * (i + 0.5) / n_dirs
    rad = np.sqrt(np.maximum(0.0, 1.0 - zc * zc))
    dirs = np.stack([np.cos(golden * i) * rad, np.sin(golden * i) * rad, zc], axis=1)
    axes = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], dtype=float)
    dirs = np.concatenate([dirs, axes])
    idx = np.unique(np.argmax(pts @ dirs.T, axis=0))
    return pts[idx]


def _hull_planes(pts: list[list[float]]) -> list[tuple[float, float, float, float]]:
    """The supporting planes of the convex hull of `pts`, as (nx, ny, nz, offset) tuples with
    unit outward normals -- brute force over point triples (every non-degenerate triple whose
    plane has all points on one side is a hull face plane, deduplicated). O(n^4) in the point
    count, entirely fine for the tens-of-points sets convex_polyhedron()/hull() feed it, and
    it happens once in Python at construction time, not per SDF evaluation."""
    n = len(pts)
    scale = max(max(abs(v) for v in p) for p in pts) or 1.0
    eps = 1e-9 * scale

    planes: list[tuple[float, float, float, float]] = []
    seen: set = set()
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                ax, ay, az = pts[i]
                ux, uy, uz = (pts[j][0] - ax, pts[j][1] - ay, pts[j][2] - az)
                vx, vy, vz = (pts[k][0] - ax, pts[k][1] - ay, pts[k][2] - az)
                nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
                nlen = math.sqrt(nx * nx + ny * ny + nz * nz)
                if nlen < eps * scale:
                    continue  # collinear triple
                nx, ny, nz = nx / nlen, ny / nlen, nz / nlen
                d = nx * ax + ny * ay + nz * az
                side = [nx * p[0] + ny * p[1] + nz * p[2] - d for p in pts]
                assert not all(abs(s) <= eps for s in side), (
                    "hull planes: points are coplanar -- that's a 2-D outline, not a solid"
                )
                if all(s <= eps for s in side):
                    pass  # already outward
                elif all(s >= -eps for s in side):
                    nx, ny, nz, d = -nx, -ny, -nz, -d
                else:
                    continue  # not a supporting plane
                key = (round(nx, 7), round(ny, 7), round(nz, 7), round(d / scale, 7))
                if key in seen:
                    continue
                seen.add(key)
                planes.append((nx, ny, nz, d))
    assert planes, "hull planes: no supporting planes found -- are the points coplanar?"
    return planes


def hull(*shapes, directions: int = 64, res: int | None = None) -> PyShape:
    """The convex hull of the given PyShapes (and/or raw Nx3 point arrays), as a libfive SDF
    PyShape -- the named form of OpenSCAD's hull(){}.

    Because no closed-form SDF exists for the hull of arbitrary SDFs, the hull is polyhedral,
    built like convex_polyhedron(): each PyShape child is meshed (once, lazily -- the first
    .sdf()/.mesh()/native fall-through on the RESULT triggers it; constructing the hull is
    free), its mesh vertices are pooled with any raw points given, the pool is decimated to
    at most `directions` support points (see _support_points()), and the SDF is the max of
    the supporting planes' half-space distances. Consequences worth knowing:

      - Corner-dominated children (cuboids, prisms) hull exactly; smooth children (spheres,
        cylinders) get a faceted hull whose fidelity is set by `directions` (default 64) --
        raise it for a finer hull, at O(directions^4) one-off plane-extraction cost.
      - Meshing the children costs the same as rendering them, so prefer hulling simple/
        low-res shapes; for the exact smooth hull of meshed solids, the native
        pythonscad hull() on already-meshed children remains the right tool.
      - Like every PyShape, the result composes symbolically (booleans, transforms) without
        re-meshing.

    Args:
        shapes:     PyShapes and/or array-likes of 3-D points, varargs or a single list
        directions: support-direction budget for the polyhedral approximation (default 64)
        res:        meshing resolution of the result (default: finest child res, or 10)

    Examples:
        .. pythonscad-example::

            a = pysolidfive.sphere(r=6, res=10)
            b = pysolidfive.sphere(r=6, res=10).translate([18.0, 0.0, 0.0])
            shape = pysolidfive.hull(a, b, directions=96)
            shape.show()

        Mixing shapes and raw points (the point pulls the hull out to a spike):

        .. pythonscad-example::

            a = pysolidfive.cuboid([16.0, 16.0, 8.0], res=10)
            shape = pysolidfive.hull(a, [[0.0, 0.0, 18.0]])
            shape.show()
    """
    args = list(shapes)
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and args[0] and isinstance(args[0][0], PyShape):
        args = list(args[0])
    assert args, "hull() needs at least one shape or point set"

    entries: list[tuple[str, Any]] = []
    mn = [math.inf] * 3
    mx = [-math.inf] * 3
    child_res: list[int] = []
    for a in args:
        if isinstance(a, PyShape):
            entries.append(("shape", a))
            child_res.append(a.res)
            for i in range(3):
                mn[i] = min(mn[i], a.mn[i])
                mx[i] = max(mx[i], a.mx[i])
        else:
            pts = np.asarray(a, dtype=float)
            if pts.ndim == 1:
                pts = pts.reshape(1, -1)
            assert pts.ndim == 2 and pts.shape[1] == 3, (
                f"hull(): point arguments must be Nx3 array-likes, got shape {pts.shape}"
            )
            entries.append(("points", pts))
            for i in range(3):
                mn[i] = min(mn[i], float(pts[:, i].min()))
                mx[i] = max(mx[i], float(pts[:, i].max()))
    # The hull's bounding box IS the union's bounding box (an axis extreme of the hull is an
    # axis extreme of some child), so bounds are exact without meshing anything yet.

    state: dict = {}

    def planes() -> list[tuple[float, float, float, float]]:
        if "planes" not in state:
            pools = []
            for kind, v in entries:
                if kind == "points":
                    pools.append(v)
                else:
                    verts, _faces = v.mesh().mesh()
                    assert verts, "hull(): a child shape meshed to nothing (empty geometry)"
                    pools.append(np.asarray(verts, dtype=float))
            sup = _support_points(np.concatenate(pools), directions)
            state["planes"] = _hull_planes([[float(c) for c in p] for p in sup])
        return state["planes"]

    def sdf_fn(x, y, z):
        terms = [nx * x + ny * y + nz * z - off for nx, ny, nz, off in planes()]
        return _balanced(lv.max, terms)

    return PyShape(sdf_fn, mn, mx, res if res is not None else (max(child_res) if child_res else 10))


def _cuboid_flare_sdf(x, y, z, size: list[float], r: float, edge_set: list[list[int]]):
    """The cuboid SDF with BOSL2's negative-rounding treatment (an external cove flare) on the
    selected X/Y-axis edges: the top/bottom face extends outward by `r` in the horizontal
    direction, then a concave quarter-arc sweeps back to the side face -- exactly BOSL2's
    construction (an added edge block with a cylinder of radius `r`, centered `r` outward
    horizontally and `r` inward vertically from the edge, carved out of it). Z-axis edges are
    rejected by cuboid() itself, matching BOSL2's own assert.
    """
    p = [x, y, z]
    b = [s / 2 for s in size]
    base = lv.max(lv.max(lv.abs(x) - b[0], lv.abs(y) - b[1]), lv.abs(z) - b[2])
    d = base
    # EDGE_OFFSETS row order for axis 0 (X) and 1 (Y): the perpendicular signs run
    # [(-,-), (+,-), (-,+), (+,+)] over (horizontal-perp, z).
    for axis in (0, 1):
        hperp = 1 - axis  # the horizontal axis perpendicular to the edge direction
        for i, (sh, sz_) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            if not edge_set[axis][i]:
                continue
            # Block: r wide just outside the side face, r tall just inside the z face.
            block = lv.max(
                lv.max(lv.abs(p[axis]) - b[axis], lv.abs(p[hperp] - sh * (b[hperp] + r / 2)) - r / 2),
                lv.abs(p[2] - sz_ * (b[2] - r / 2)) - r / 2,
            )
            # Concave arc: carve the cylinder centered r outward / r inward from the edge.
            du = p[hperp] - sh * (b[hperp] + r)
            dv = p[2] - sz_ * (b[2] - r)
            flare = lv.max(block, r - lv.sqrt(du * du + dv * dv))
            d = lv.min(d, flare)
    return d


def cuboid(
    size: float | list[float] = [1, 1, 1],
    rounding: float = 0,
    chamfer: float = 0,
    edges: str | list = "ALL",
    except_edges: list | None = None,
    res: int = 10,
    anchor: "Sequence[float]" = CENTER,
) -> PyShape:
    """A cuboid with optional per-edge rounding or chamfering, built as a libfive signed
    distance function (F-Rep) and returned as a PyShape (meshed lazily, via frep(), on first
    use) -- see bosl2.shapes3d.cuboid() for the equivalent BOSL2-style mesh-CSG version
    (identical `edges=`/`except_edges=` semantics; both accept the same edge selector values,
    since pysolidfive._edges's edge-set resolver is a byte-for-byte copy of bosl2's own).

    `rounding` and `chamfer` are mutually exclusive in a single call (matching
    bosl2.shapes3d.cuboid()); to mix both on different edges of the same cuboid, chain
    PyShape.round()/.chamfer() calls instead, e.g.
    `cuboid(size).round(2, edges="Z").chamfer(1, edges=[TOP+LEFT])`.

    Args:
        size:         size of the cuboid, a number or length-3 vector
        rounding:     edge rounding radius applied to every selected edge (default: no rounding)
        chamfer:      edge chamfer size applied to every selected edge (default: no chamfer)
        edges:        edges to treat -- "ALL"/"NONE"/"X"/"Y"/"Z", a single edge vector (e.g.
                      TOP+LEFT), a list of edge vectors, or a raw 3x4 edge array (default "ALL")
        except_edges: edges to explicitly exclude from `edges` (BOSL2's `except=` synonym;
                      `except` is a Python keyword)
        res:          libfive meshing resolution passed to frep() (default 10; higher = finer mesh)
        anchor:       anchor point (default CENTER)

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=4)
            shape.show()

        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], chamfer=4)
            shape.show()

        Rounding only the 4 vertical edges (the per-axis-composition fallback path, not the
        exact-formula ``edges="ALL"`` case above):

        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=4, edges="Z")
            shape.show()
    """
    assert not (rounding and chamfer), "Cannot specify nonzero value for both rounding and chamfer"
    sz: list[float] = [float(v) for v in size] if isinstance(size, (list, tuple)) else [float(size)] * 3
    edge_set = _edges(edges, except_edges or [])
    half = [s / 2 for s in sz]
    if rounding < 0:
        # BOSL2's negative rounding: an external cove flare on the selected edges (see
        # _cuboid_flare_sdf). Same restriction as BOSL2: no Z-aligned edges.
        assert edge_set[2] == [0, 0, 0, 0], "Cannot use negative rounding with Z aligned edges"
        r = -rounding
        sdf_fn = lambda x, y, z: _cuboid_flare_sdf(x, y, z, sz, r, edge_set)  # noqa: E731
        # The flares stick out horizontally by r on whichever sides have a flared edge --
        # widen the meshing bounds accordingly (cuboid_size stays unset: the flared solid
        # is no longer a plain cuboid, so chained edge treatments would be wrong).
        mn = [-half[0], -half[1], -half[2]]
        mx = [half[0], half[1], half[2]]
        for axis, hperp in ((0, 1), (1, 0)):
            for i, (sh, _sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
                if edge_set[axis][i]:
                    if sh < 0:
                        mn[hperp] = min(mn[hperp], -half[hperp] - r)
                    else:
                        mx[hperp] = max(mx[hperp], half[hperp] + r)
        shape = PyShape(sdf_fn, mn, mx, res)
        offset = _anchor_offset_box3(sz, [int(a) for a in anchor])
        if offset[0] or offset[1] or offset[2]:
            shape = shape.translate(offset)
        return shape
    mode = "chamfer" if chamfer else "round"
    amount = chamfer if chamfer else rounding
    amounts, modes = _edge_matrices(amount, edge_set, mode)
    sdf_fn = lambda x, y, z: _cuboid_edge_sdf(x, y, z, sz, amounts, modes)  # noqa: E731
    shape = PyShape(
        sdf_fn, [-half[0], -half[1], -half[2]], half, res, cuboid_size=sz,
        cuboid_edge_amounts=amounts, cuboid_edge_modes=modes,
    )
    offset = _anchor_offset_box3(sz, [int(a) for a in anchor])
    if offset[0] or offset[1] or offset[2]:
        shape = shape.translate(offset)
    return shape


def cube(size: float | list[float] = 1, anchor: "Sequence[float]" = CENTER, res: int = 10) -> PyShape:
    """A cube, as a plain (unrounded) libfive SDF. See cuboid() for rounding/chamfering."""
    return cuboid(size=size, anchor=anchor, res=res)


# ---------------------------------------------------------------------------
# Section: Other simple solids without a BOSL2 rounding/chamfer concept
# ---------------------------------------------------------------------------


def octahedron(size: float = 1, anchor: "Sequence[float]" = CENTER, res: int = 10) -> PyShape:
    """An octahedron with axis-aligned points (`|x|+|y|+|z| <= size/2`), as a libfive SDF."""
    s = size / 2
    sdf_fn = lambda x, y, z: lv.abs(x) + lv.abs(y) + lv.abs(z) - s  # noqa: E731
    shape = PyShape(sdf_fn, [-s, -s, -s], [s, s, s], res)
    pts = [[s, 0, 0], [-s, 0, 0], [0, s, 0], [0, -s, 0], [0, 0, s], [0, 0, -s]]
    offset = _anchor_offset_hull3(pts, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def convex_polyhedron(points, res: int = 10) -> PyShape:
    """The convex hull of `points` as a libfive SDF: the max of the hull faces' signed
    half-space distances -- the 3-D analogue of polygon_extrude()'s half-plane form, with the
    same documented value tradeoff (exact perpendicular distance at faces, sign-correct
    underestimate out past edges/vertices). Covers the dice-style solids (tetrahedron,
    dodecahedron, icosahedron, trapezohedron, ...) that shapes3d.py builds, without needing
    BOSL2's polyhedra.scad or a mesh hull().

    Face planes come from a brute-force hull: every non-degenerate point triple whose plane has
    all points on one side is a supporting plane (deduplicated). That's O(n^4) in the point
    count -- entirely fine for the tens-of-vertices solids this is for, and it happens once in
    Python at construction time, not per SDF evaluation.
    """
    points = np.asarray(points, dtype=float)
    pts = [[float(v) for v in p] for p in points]
    n = len(pts)
    assert n >= 4, f"convex_polyhedron() needs at least 4 points, got {n}"
    planes = _hull_planes(pts)

    def sdf_fn(x, y, z):
        d = None
        for nx, ny, nz, off in planes:
            e = nx * x + ny * y + nz * z - off
            d = e if d is None else lv.max(d, e)
        return d

    mn = [min(p[i] for p in pts) for i in range(3)]
    mx = [max(p[i] for p in pts) for i in range(3)]
    return PyShape(sdf_fn, mn, mx, res)


def wedge(size: list[float] = [1, 1, 1], anchor: "Sequence[float] | None" = None, res: int = 10) -> PyShape:
    """A 3-D triangular wedge with the hypotenuse in the X+Z+ quadrant, as a libfive SDF.

    Args:
        size:   [width, thickness, height]
        anchor: anchor point (default FRONT+LEFT+BOTTOM, matching bosl2.shapes3d.wedge())
    """
    if anchor is None:
        anchor = FRONT + LEFT + BOTTOM
    bx, by, bz = size[0] / 2, size[1] / 2, size[2] / 2
    # The triangular cross-section (right angle at Y-,Z-, hypotenuse from (Y+,Z-) to (Y-,Z+))
    # lies in the (Y, Z) plane; X is the uniform extrusion axis -- verified directly against
    # bosl2.shapes3d.wedge()'s vertex list (every vertex has a fixed X, so the triangle's
    # actual shape only varies over Y/Z).
    nlen = math.hypot(by, bz)

    def sdf_fn(x, y, z):
        box = lv.max(lv.max(lv.abs(x) - bx, lv.abs(y) - by), lv.abs(z) - bz)
        diag = (bz * y + by * z) / nlen
        return lv.max(box, diag)

    shape = PyShape(sdf_fn, [-bx, -by, -bz], [bx, by, bz], res)
    pts = [[bx, by, -bz], [bx, -by, -bz], [bx, -by, bz], [-bx, by, -bz], [-bx, -by, -bz], [-bx, -by, bz]]
    offset = _anchor_offset_hull3(pts, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def sphere(r: float | None = None, d: float | None = None, anchor: "Sequence[float]" = CENTER, res: int = 10) -> PyShape:
    """A sphere, as a libfive SDF (`length(p) - r`).

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.sphere(r=10)
            shape.show()
    """
    rad = _radius(r=r, d=d, dflt=1)
    sdf_fn = lambda x, y, z: lv.sqrt(x * x + y * y + z * z) - rad  # noqa: E731
    shape = PyShape(sdf_fn, [-rad, -rad, -rad], [rad, rad, rad], res)
    offset = _anchor_offset_sphere(rad, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def spheroid(r: float | None = None, d: float | None = None, anchor: "Sequence[float]" = CENTER, res: int = 10) -> PyShape:
    """An approximate sphere; this pure-libfive port just builds a plain sphere() (matching
    bosl2.shapes3d.spheroid()'s own choice to ignore style/dual for its pure-Python port)."""
    return sphere(r=r, d=d, anchor=anchor, res=res)


def torus(
    r_maj: float | None = None,
    r_min: float | None = None,
    d_maj: float | None = None,
    d_min: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    od: float | None = None,
    id: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A torus (donut) shape, as a libfive SDF (`length(vec2(length(p.xy)-r_maj, p.z)) - r_min`).

    Note: BOSL2's outer-radius parameter is named `or`, which collides with the Python
    keyword `or`; it is exposed here as `outer_r` instead. See bosl2.shapes3d.torus() for
    the full parameter set this mirrors.

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.torus(r_maj=15, r_min=5)
            shape.show()
    """
    _or = _pick_radius(r=outer_r, d=od, dflt=None)
    _ir = _pick_radius(r=ir, d=id, dflt=None)
    _r_maj = _pick_radius(r=r_maj, d=d_maj, dflt=None)
    _r_min = _pick_radius(r=r_min, d=d_min, dflt=None)
    if _r_maj is not None:
        maj = _r_maj
    elif _ir is not None and _or is not None:
        maj = (_or + _ir) / 2
    elif _ir is not None and _r_min is not None:
        maj = _ir + _r_min
    elif _or is not None and _r_min is not None:
        maj = _or - _r_min
    else:
        assert False, "torus(): bad parameters."
    if _r_min is not None:
        minr = _r_min
    elif _ir is not None:
        minr = maj - _ir
    elif _or is not None:
        minr = _or - maj
    else:
        assert False, "torus(): bad parameters."

    sdf_fn = lambda x, y, z: _lv_hypot(_lv_hypot(x, y) - maj, z) - minr  # noqa: E731
    outer = maj + minr
    shape = PyShape(sdf_fn, [-outer, -outer, -minr], [outer, outer, minr], res)
    offset = _anchor_offset_cyl(outer, outer, minr * 2, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Cylinders
# ---------------------------------------------------------------------------


def _wall_line_sdf(rxy, z, r1: float, r2: float, hb: float):
    """Signed distance to the infinite line through `(r1, -hb)` and `(r2, hb)` in the
    `(rxy, z)` half-plane -- the slanted wall of a cylinder/cone, exact for the wall itself;
    intersecting (max()) with the top/bottom slabs (see _cylinder_sdf()) caps it off, with the
    same corner-region approximation already documented for cuboid()'s per-axis composition.
    """
    dr, dz = r2 - r1, 2 * hb
    nlen = math.hypot(dr, dz)
    return ((rxy - r1) * dz - (z + hb) * dr) / nlen


def _cylinder_sdf(x, y, z, h: float, r1: float, r2: float, shift: list[float] | None = None):
    hb = h / 2
    if shift and (shift[0] or shift[1]):
        # Oblique cone (BOSL2 cyl(shift=)): the section center slides linearly from [0, 0]
        # at the bottom to `shift` at the top -- same interpolate-per-height construction
        # (and the same not-quite-Euclidean-but-zero-set-correct caveat) as prismoid().
        t = (z + hb) / h
        x = x - shift[0] * t
        y = y - shift[1] * t
    rxy = _lv_hypot(x, y)
    wall = _wall_line_sdf(rxy, z, r1, r2, hb)
    slab = lv.abs(z) - hb
    return lv.max(wall, slab)


def _cyl_edge_sdf(axial, radial, h: float, r1: float, r2: float, amt1: float, amt2: float, mode: str):
    """_cylinder_sdf(), plus independent rounding/chamfer treatment of the bottom (amt1) and
    top (amt2) rim, using the same per-candidate-quadrant masking technique as
    bosl2.shapes3d.cuboid() (but only 2 candidates -- top/bottom -- since the radial
    coordinate has no sign ambiguity to select between, unlike a rectangle's 4 corners)."""
    hb = h / 2
    wall = _wall_line_sdf(radial, axial, r1, r2, hb)
    candidates = []
    for sz, r_ref, a in ((-1, r1, amt1), (1, r2, amt2)):
        if mode == "round":
            qu = radial - r_ref + a
            qv = lv.abs(axial) - hb + a
            base = lv.min(lv.max(qu, qv), 0) + _lv_hypot(lv.max(qu, 0), lv.max(qv, 0)) - a
        else:
            assert mode == "chamfer"
            qu = radial - r_ref
            qv = lv.abs(axial) - hb
            base = lv.max(lv.max(qu, qv), (qu + qv + a) / _SQRT2)
        mask = lv.max(0, -sz * axial)
        candidates.append(base + _PENALTY * mask)
    rim = lv.min(candidates[0], candidates[1])
    return lv.max(wall, rim)


def cylinder(
    h: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A cylinder/cone (no rounding) as a libfive SDF -- see cyl() for rounding/chamfering."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM
    sdf_fn = lambda x, y, z: _cylinder_sdf(x, y, z, length, rad1, rad2)  # noqa: E731
    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def cyl(
    h: float | None = None,
    r: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    shift: list[float] | None = None,
    anchor: "Sequence[float] | None" = None,
    res: int = 10,
) -> PyShape:
    """A cylinder/cone with optional rounding or chamfering of its end rims, as a libfive SDF.
    See bosl2.shapes3d.cyl() for the full BOSL2-style version this mirrors (circum=/realign=/
    texture= aren't supported here; shift= is, for oblique cones, but not combined with
    rounding/chamfer).

    `rounding`/`chamfer` (and their `1`/`2` bottom/top variants) are mutually exclusive, same
    as bosl2.shapes3d.cyl().

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.cyl(h=20, r=8, rounding=2)
            shape.show()
    """
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    use_anchor = anchor
    if use_anchor is None:
        use_anchor = CENTER if center is None or center else BOTTOM

    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"
    mode, amt1, amt2 = ("chamfer", c1v, c2v) if (c1v or c2v) else ("round", r1v, r2v)

    if shift is not None and (shift[0] or shift[1]):
        assert not (amt1 or amt2), "shift= cannot be combined with rounding/chamfer"
        sdf_fn = lambda x, y, z: _cylinder_sdf(x, y, z, length, rad1, rad2, shift)  # noqa: E731
    else:
        sdf_fn = lambda x, y, z: _cyl_edge_sdf(z, _lv_hypot(x, y), length, rad1, rad2, amt1, amt2, mode)  # noqa: E731
    maxr = max(rad1, rad2)
    mn = [-maxr, -maxr, -length / 2]
    mx = [maxr, maxr, length / 2]
    if shift is not None:
        # The top section slides sideways by `shift` -- widen the bounds to cover it.
        for i in (0, 1):
            mn[i] = min(mn[i], mn[i] + shift[i])
            mx[i] = max(mx[i], mx[i] + shift[i])
    shape = PyShape(sdf_fn, mn, mx, res)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def _cyl_axis(
    axis: int,
    h: float | None,
    r: float | None,
    l: float | None,
    r1: float | None,
    r2: float | None,
    d: float | None,
    d1: float | None,
    d2: float | None,
    chamfer: float | None,
    chamfer1: float | None,
    chamfer2: float | None,
    rounding: float | None,
    rounding1: float | None,
    rounding2: float | None,
    anchor: "Sequence[float]",
    res: int,
) -> PyShape:
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"
    mode, amt1, amt2 = ("chamfer", c1v, c2v) if (c1v or c2v) else ("round", r1v, r2v)

    def sdf_fn(x, y, z):
        coords = [x, y, z]
        axial = coords[axis]
        others = [coords[i] for i in range(3) if i != axis]
        radial = _lv_hypot(others[0], others[1])
        return _cyl_edge_sdf(axial, radial, length, rad1, rad2, amt1, amt2, mode)

    maxr = max(rad1, rad2)
    mn, mx = [-maxr, -maxr, -maxr], [maxr, maxr, maxr]
    mn[axis], mx[axis] = -length / 2, length / 2
    shape = PyShape(sdf_fn, mn, mx, res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor, axis=axis)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def xcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A cylinder oriented along the X axis. See cyl() for argument details."""
    return _cyl_axis(0, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def ycyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A cylinder oriented along the Y axis. See cyl() for argument details."""
    return _cyl_axis(1, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def zcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A cylinder oriented along the Z axis (same as cyl()). See cyl() for argument details."""
    return _cyl_axis(2, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def tube(
    h: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    od: float | None = None,
    id: float | None = None,
    wall: float | None = None,
    outer_r1: float | None = None,
    outer_r2: float | None = None,
    od1: float | None = None,
    od2: float | None = None,
    ir1: float | None = None,
    ir2: float | None = None,
    id1: float | None = None,
    id2: float | None = None,
    l: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A hollow cylindrical tube (outer cylinder minus inner cylinder), as a libfive SDF.

    Note: BOSL2's outer-radius parameters are named `or`/`or1`/`or2`; exposed here as
    `outer_r`/`outer_r1`/`outer_r2` since `or` is a Python keyword.
    """
    length = l if l is not None else (h if h is not None else 1)
    orr1 = _pick_radius(r1=outer_r1, d1=od1, r=outer_r, d=od, dflt=None)
    orr2 = _pick_radius(r1=outer_r2, d1=od2, r=outer_r, d=od, dflt=None)
    irr1 = _pick_radius(r1=ir1, d1=id1, r=ir, d=id, dflt=None)
    irr2 = _pick_radius(r1=ir2, d1=id2, r=ir, d=id, dflt=None)
    wall_v = wall if wall is not None else 1
    rad1 = orr1 if orr1 is not None else (irr1 + wall_v if irr1 is not None else None)
    rad2 = orr2 if orr2 is not None else (irr2 + wall_v if irr2 is not None else None)
    irad1 = irr1 if irr1 is not None else (orr1 - wall_v if orr1 is not None else None)
    irad2 = irr2 if irr2 is not None else (orr2 - wall_v if orr2 is not None else None)
    assert rad1 is not None and rad2 is not None and irad1 is not None and irad2 is not None, (
        "tube(): must specify two of inner radius/diam, outer radius/diam, and wall width."
    )

    sdf_fn = lambda x, y, z: lv.max(  # noqa: E731
        _cylinder_sdf(x, y, z, length, rad1, rad2), -_cylinder_sdf(x, y, z, length, irad1, irad2)
    )
    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def pie_slice(
    h: float | None = None,
    r: float | None = None,
    ang: float = 30,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A pie slice (wedge of a cylinder/cone), as a libfive SDF: a cylinder intersected with
    an angular sector (built from 1-2 half-planes -- `ang` is a plain Python float fixed at
    construction time, so choosing intersection vs union of the two half-planes based on
    `ang <= 180` is an ordinary Python conditional, not a per-point SDF branch)."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=10)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=10)
    ang_v = ang % 360 if (ang > 360 or ang < 0) else ang
    ang_rad = math.radians(ang_v)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)

    def sdf_fn(x, y, z):
        body = _cylinder_sdf(x, y, z, length, rad1, rad2)
        if ang_v <= 0 or ang_v >= 360:
            return body
        sdf1 = -y
        sdf2 = y * cos_a - x * sin_a
        sector = lv.max(sdf1, sdf2) if ang_v <= 180 else lv.min(sdf1, sdf2)
        return lv.max(body, sector)

    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Cuboids, Prismoids and Tubes
# ---------------------------------------------------------------------------


def prismoid(
    size1: list[float],
    size2: list[float],
    h: float | None = None,
    shift: list[float] = [0, 0],
    l: float | None = None,
    anchor: "Sequence[float]" = BOTTOM,
    res: int = 10,
) -> PyShape:
    """A rectangular prismoid (truncated pyramid), as a libfive SDF.

    CAVEAT: unlike bosl2.shapes3d.prismoid(), this pure-libfive port does not support
    rounding/chamfer of the vertical edges (deriving an exact SDF for a *tapered* box's
    independently-radiused vertical edges was out of scope here -- use
    bosl2.shapes3d.prismoid() for that, or pysolidfive.cuboid() for the non-tapered case). The SDF
    itself is built by linearly interpolating the local half-size/shift at each height `z`
    (clamped to the `[bottom, top]` range via min()/max(), so no true per-point conditional is
    needed) and taking the 2-D box distance in that local cross-section, intersected with the
    top/bottom slab -- exact for a non-tapered box (`size1 == size2`, `shift == [0, 0]`), an
    approximation (same character as cuboid()'s documented corner caveats) for a genuine taper.

    Args:
        size1:  [width, length] of the bottom end
        size2:  [width, length] of the top end
        h/l:    height of the prism
        shift:  [X,Y] shift of the top center relative to the bottom center
        anchor: anchor point (default BOTTOM)
        res:    libfive meshing resolution passed to frep() (default 10)
    """
    height = h if h is not None else (l if l is not None else 1)
    bx1, by1 = size1[0] / 2, size1[1] / 2
    bx2, by2 = size2[0] / 2, size2[1] / 2
    hb = height / 2

    def sdf_fn(x, y, z):
        t = lv.min(lv.max((z + hb) / height, 0), 1)
        bx = bx1 + (bx2 - bx1) * t
        by = by1 + (by2 - by1) * t
        cx = shift[0] * t
        cy = shift[1] * t
        qx = lv.abs(x - cx) - bx
        qy = lv.abs(y - cy) - by
        d2d = lv.min(lv.max(qx, qy), 0) + _lv_hypot(lv.max(qx, 0), lv.max(qy, 0))
        slab = lv.abs(z) - hb
        return lv.max(d2d, slab)

    maxx = max(bx1, bx2, bx1 + abs(shift[0]), bx2 + abs(shift[0]))
    maxy = max(by1, by2, by1 + abs(shift[1]), by2 + abs(shift[1]))
    shape = PyShape(sdf_fn, [-maxx, -maxy, -hb], [maxx, maxy, hb], res)
    offset = _anchor_offset_box3([maxx * 2, maxy * 2, height], [int(a) for a in anchor])
    if any(offset):
        shape = shape.translate(offset)
    return shape


def rect_tube(
    h: float | None = None,
    size: float | list[float] | None = None,
    isize: float | list[float] | None = None,
    wall: float | None = None,
    rounding: float = 0,
    irounding: float | None = None,
    l: float | None = None,
    anchor: "Sequence[float]" = BOTTOM,
    res: int = 10,
) -> PyShape:
    """A rectangular tube (a rectangle with a rectangular hole through it), as a libfive SDF
    (outer rounded-rect-extrusion minus inner rounded-rect-extrusion, reusing
    bosl2.shapes3d.cuboid()'s per-edge machinery for each). Only the 4 vertical edges are
    ever rounded (`edges="Z"`, matching the "rounded rectangular tube" look BOSL2's own
    rect_tube() produces) -- there's no per-edge selection here, just one outer radius and
    one inner radius (default: same as the outer).

    Args:
        h/l:       height/length of the tube (default 1)
        size:      outer [X,Y] size of the tube
        isize:     inner [X,Y] size of the tube
        wall:      wall thickness (used with `size` if `isize` isn't given, or vice versa)
        rounding:  outer vertical-edge rounding radius (default: no rounding)
        irounding: inner vertical-edge rounding radius (default: same as `rounding`)
        anchor:    anchor point (default BOTTOM)
        res:       libfive meshing resolution passed to frep() (default 10)
    """
    length = h if h is not None else (l if l is not None else 1)
    assert size is not None, "rect_tube(): must give size."
    sz: list[float] = [float(v) for v in size] if isinstance(size, (list, tuple)) else [float(size)] * 2
    if isize is not None:
        isz: list[float] = [float(v) for v in isize] if isinstance(isize, (list, tuple)) else [float(isize)] * 2
    else:
        assert wall is not None, "rect_tube(): must give isize or wall."
        isz = [sz[0] - 2 * wall, sz[1] - 2 * wall]
    irounding_v = irounding if irounding is not None else rounding
    edge_set_z = _edges("Z", [])
    o_amounts, o_modes = _edge_matrices(rounding, edge_set_z, "round")
    i_amounts, i_modes = _edge_matrices(irounding_v, edge_set_z, "round")

    def sdf_fn(x, y, z):
        outer = _cuboid_edge_sdf(x, y, z, [sz[0], sz[1], length], o_amounts, o_modes)
        inner = _cuboid_edge_sdf(x, y, z, [isz[0], isz[1], length + 0.02], i_amounts, i_modes)
        return lv.max(outer, -inner)

    half = [sz[0] / 2, sz[1] / 2, length / 2]
    shape = PyShape(sdf_fn, [-half[0], -half[1], -half[2]], half, res)
    offset = _anchor_offset_box3([sz[0], sz[1], length], [int(a) for a in anchor])
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Miscellaneous
# ---------------------------------------------------------------------------


def interior_fillet(
    l: float = 1.0,
    r: float | None = None,
    ang: float = 90,
    d: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A shape to fillet an interior corner between two faces meeting at `ang` degrees, as a
    libfive SDF: the wedge between the two faces, minus a cylindrical arc of radius `r`
    positioned so it's tangent to both. Extruded along Y for length `l`.

    CAVEAT: simplified relative to bosl2.shapes3d.interior_fillet() -- no `overlap=` flap (an
    SDF union is already watertight without one) and no independent anchor-face alignment;
    the wedge's first face lies along the local +X/Z=0 half-plane. See
    bosl2.shapes3d.interior_fillet() for the exact BOSL2-compatible anchor/orientation.
    """
    rad = _radius(r=r, d=d, dflt=1)
    half = math.radians(ang / 2)
    dist = rad / math.sin(half)
    cx, cz = dist * math.cos(half), dist * math.sin(half)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    hb = l / 2

    def sdf_fn(x, y, z):
        sdf1 = -z
        sdf2 = z * cos_a - x * sin_a
        wedge_sdf = lv.max(sdf1, sdf2)
        circle = _lv_hypot(x - cx, z - cz) - rad
        fillet2d = lv.max(wedge_sdf, -circle)
        slab = lv.abs(y) - hb
        return lv.max(fillet2d, slab)

    shape = PyShape(sdf_fn, [-rad * 2, -hb, -rad * 2], [rad * 2, hb, rad * 2], res)
    if any(anchor):
        offset = [-a * b for a, b in zip(anchor, [rad * 2, hb, rad * 2])]
        shape = shape.translate(offset)
    return shape


def rounding_edge_mask(
    l: float | None = None,
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    excess: float = 0.1,
    res: int = 10,
) -> PyShape:
    """A standalone 3-D edge-rounding CUTTER of length `l`, as a libfive SDF, for subtracting
    from another PyShape to round over a sharp 90-degree edge that isn't part of a cuboid()'s
    own edge/corner treatment -- e.g. an edge exposed by an earlier cut, or any other edge you'd
    otherwise position by hand. Matches bosl2.masking.rounding_edge_mask()'s local-frame
    convention exactly (same `.rotate(...).translate(...)` call sites work unchanged): origin at
    the sharp edge, +X/+Y extending into the material (with a small `excess` skirt past 0 on
    each so the cutter fully bridges the material being cut), centered along its own Z axis over
    length `l`, with a quarter-circle bite of radius `r` taken out of the far corner.

    Built the same way interior_fillet() builds its wedge-minus-circle cutter: a square corner
    (`box`) minus a circle tangent to both its flat sides.

    CAVEAT: simplified relative to bosl2.masking.rounding_edge_mask() -- one radius for the
    whole length (no r1/r2 taper).
    """
    length = l if l is not None else (h if h is not None else 1)
    rad = _radius(r=r, d=d, dflt=1)

    def sdf_fn(x, y, z):
        box = lv.max(lv.max(x - rad, -x - excess), lv.max(y - rad, -y - excess))
        circle = _lv_hypot(x - rad, y - rad) - rad
        cutter2d = lv.max(box, -circle)
        slab = lv.abs(z) - length / 2
        return lv.max(cutter2d, slab)

    return PyShape(sdf_fn, [-excess, -excess, -length / 2], [rad, rad, length / 2], res)


def polygon_extrude(pts, length: float, res: int = 10) -> PyShape:
    """Extrude an arbitrary CONVEX 2-D polygon `pts` (either winding order) along Z by
    `length`, centered -- for a custom edge-profile cutter with no simple closed form (like
    bosl2.shapes3d.Bosl2Solid.edge_profile_asym()'s `children=` path, but swept here by hand
    with an explicit rotate()/translate() rather than an automatic per-edge sweep).

    As a libfive SDF, this is the max() of each edge's signed half-plane distance -- exact at
    and near any face, but (like every other per-axis/per-plane-composed shape in this module --
    see the module docstring) underestimates the true Euclidean distance near a vertex, away
    from the surface; the sign is still correct everywhere a convex polygon's supporting
    half-planes actually bound it.

    CAVEAT: `pts` must describe a CONVEX polygon. A concave vertex's half-plane doesn't bound
    the shape there, so both the sign and the surface would come out wrong.
    """
    pts = as_points(pts)
    area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    ordered = pts if area2 > 0 else list(reversed(pts))
    n = len(ordered)
    edges = []
    for i in range(n):
        x0, y0 = ordered[i]
        x1, y1 = ordered[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        elen = math.hypot(ex, ey)
        edges.append((ey / elen, -ex / elen, x0, y0))

    def sdf_fn(x, y, z):
        d = None
        for nx, ny, x0, y0 in edges:
            e = nx * (x - x0) + ny * (y - y0)
            d = e if d is None else lv.max(d, e)
        slab = lv.abs(z) - length / 2
        return lv.max(d, slab)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return PyShape(sdf_fn, [min(xs), min(ys), -length / 2], [max(xs), max(ys), length / 2], res)


def polygon_prism(
    paths,
    h: float,
    rounding_top: float = 0,
    rounding_bottom: float = 0,
    res: int = 10,
) -> PyShape:
    """Extrude an arbitrary SIMPLE polygon (convex or concave -- exact 2-D SDF via
    _polygon_sdf_xy(), unlike polygon_extrude()'s convex-only half-planes) from z=0 up to z=h,
    with optional circular treatments on each end rim -- the same job as real BOSL2's
    offset_sweep(path, height=h, bottom=os_circle(b), top=os_circle(t)), and the same sign
    convention for the radii: positive is a convex roundover eased into the rim, negative is an
    outward flare, 0 leaves that rim square. Sits on z=0 (not centered), matching offset_sweep.

    `paths` is one polygon (a list of [x, y] points) or a list of NON-OVERLAPPING polygons (a
    "region" of disjoint islands, min/union-combined). Holes aren't supported.

    Roundover rims use the same exact inset-then-offset construction as _rounded_box_sdf(), in
    (d2d, z) cross-section coordinates: q = (d2d + r, (z - h) + r) for the top rim, then
    `min(max(q), 0) + hypot(max(q, 0)) - r` -- which reduces exactly to the plain side/end
    distance away from its own rim, so both rims plus the sharp prism combine with max().
    Flares union on an extra quarter-circle ring of material outside the wall (the same
    box-minus-tangent-circle style as interior_fillet()/rounding_edge_mask(), swept here along
    the polygon via the 2-D SDF instead of along a straight edge).

    Args:
        paths:           one [[x, y], ...] polygon, or a list of disjoint such polygons
        h:               extrusion height (z from 0 to h)
        rounding_top:    top-rim treatment: >0 roundover radius, <0 flare, 0 square (default 0)
        rounding_bottom: bottom-rim treatment, same convention (default 0)
        res:             libfive meshing resolution passed to frep() (default 10)
    """
    assert len(paths) >= 1, "polygon_prism(): paths must not be empty"
    path_list = as_path_list(paths)
    for p in path_list:
        assert len(p) >= 3, f"polygon_prism(): every path needs >= 3 points, got {len(p)}"
    assert h > 0, f"polygon_prism(): h must be > 0, h={h}"
    assert abs(rounding_top) < h and abs(rounding_bottom) < h, "polygon_prism(): rim treatments must be smaller than h"

    def sdf_fn(x, y, z):
        d2d = None
        for p in path_list:
            d = _polygon_sdf_xy(x, y, p)
            d2d = d if d2d is None else lv.min(d2d, d)
        assert d2d is not None, "polygon_prism(): no paths"

        # Sharp prism, then max() in each roundover rim (each reduces to the sharp distance
        # away from its own rim -- see docstring).
        out = lv.max(d2d, lv.max(z - h, -z))
        if rounding_top > 0:
            rt = rounding_top
            q1, q2 = d2d + rt, (z - h) + rt
            out = lv.max(out, lv.min(lv.max(q1, q2), 0) + _lv_hypot(lv.max(q1, 0), lv.max(q2, 0)) - rt)
        if rounding_bottom > 0:
            rb = rounding_bottom
            q1, q2 = d2d + rb, -z + rb
            out = lv.max(out, lv.min(lv.max(q1, q2), 0) + _lv_hypot(lv.max(q1, 0), lv.max(q2, 0)) - rb)

        # Flares union on a ring of added material curving from tangent-to-the-wall out to the
        # rim plane along a quarter circle. The ring is deliberately built on the UNSIGNED
        # outline distance (min-over-segments, no atan2), not the signed d2d: it therefore also
        # fires on the mirrored band just INSIDE the wall, which the union with the prism
        # swallows invisibly -- and in exchange it stays completely clear of the winding form's
        # atan2 branch cuts, which libfive's evaluator turned into spike/collapse artifacts
        # whenever a flared concave prism built on a dense round_corners() outline was
        # subtracted from another shape (sharp low-point-count outlines rendered fine; the
        # densified ones degenerated).
        u_d = None
        if rounding_top < 0 or rounding_bottom < 0:
            u2 = None
            for p in path_list:
                d2 = _polygon_dist2_xy(x, y, p)
                u2 = d2 if u2 is None else lv.min(u2, d2)
            u_d = lv.sqrt(u2)
        if rounding_top < 0:
            assert u_d is not None
            f = -rounding_top
            du = lv.min(u_d, f + 1)
            ring = lv.max(f - _lv_hypot(du - f, z - (h - f)), lv.max(z - h, (h - f) - z))
            ring = lv.max(ring, u_d - f)
            out = lv.min(out, ring)
        if rounding_bottom < 0:
            assert u_d is not None
            f = -rounding_bottom
            du = lv.min(u_d, f + 1)
            ring = lv.max(f - _lv_hypot(du - f, z - f), lv.max(-z, z - f))
            ring = lv.max(ring, u_d - f)
            out = lv.min(out, ring)
        return out

    xs = [p[0] for path in path_list for p in path]
    ys = [p[1] for path in path_list for p in path]
    flare = max(0.0, -rounding_top, -rounding_bottom)
    return PyShape(
        sdf_fn,
        [min(xs) - flare, min(ys) - flare, 0],
        [max(xs) + flare, max(ys) + flare, h],
        res,
    )


def teardrop(
    h: float | None = None,
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """A teardrop shape (useful for 3-D-printable horizontal holes), as a libfive SDF: the
    union of a circle and a "roof" of two planes meeting at the apex, tangent to the circle,
    extruded along Y for thickness `h`.

    CAVEAT: simplified relative to bosl2.shapes3d.teardrop() -- no `chamfer=`/`circum=`/
    `realign=` support. `cap_h` (truncation height) is supported since it's a plain top-slab
    intersection.

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.teardrop(h=10, r=8)
            shape.show()
    """
    length = h if h is not None else 1
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    hb = length / 2

    def profile_sdf(u, v, rad):
        circle = _lv_hypot(u, v) - rad
        right = u * sin_a + v * cos_a - rad
        left = -u * sin_a + v * cos_a - rad
        # The roof planes are only tangent to (and so only a valid boundary of) the circle
        # at v >= rad*cos_a (their tangent height); below that they cut into the disk, so
        # mask them out there and let the circle govern instead.
        v_tangent = rad * cos_a
        roof = lv.max(right, left) + _PENALTY * lv.max(0, v_tangent - v)
        d = lv.min(circle, roof)
        if cap_h is not None:
            d = lv.max(d, v - cap_h)
        return d

    def sdf_fn(x, y, z):
        t = lv.min(lv.max((y + hb) / length, 0), 1)
        rad = rad1 + (rad2 - rad1) * t
        prof = profile_sdf(x, z, rad)
        slab = lv.abs(y) - hb
        return lv.max(prof, slab)

    maxr = max(rad1, rad2)
    maxheight = maxr / sin_a if cap_h is None else min(cap_h, maxr / sin_a)
    shape = PyShape(sdf_fn, [-maxr, -hb, -maxr], [maxr, hb, maxheight], res)
    if any(anchor):
        offset = [-anchor[0] * maxr, -anchor[1] * hb, -anchor[2] * maxheight if anchor[2] > 0 else -anchor[2] * maxr]
        shape = shape.translate(offset)
    return shape


def onion(
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    d: float | None = None,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape:
    """An onion-dome shape (a sphere with a conical cap), as a libfive SDF: the union of a
    sphere and a cone tangent to it, revolved around Z.

    CAVEAT: simplified relative to bosl2.shapes3d.onion() -- no `circum=`/`realign=` support.
    """
    rad = _radius(r=r, d=d, dflt=1)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    v_tangent = rad * cos_a

    def sdf_fn(x, y, z):
        rxy = _lv_hypot(x, y)
        sphere_sdf = _lv_hypot(rxy, z) - rad
        roof = rxy * sin_a + z * cos_a - rad
        roof = roof + _PENALTY * lv.max(0, v_tangent - z)
        d = lv.min(sphere_sdf, roof)
        if cap_h is not None:
            d = lv.max(d, z - cap_h)
        return d

    maxheight = rad / sin_a if cap_h is None else min(cap_h, rad / sin_a)
    shape = PyShape(sdf_fn, [-rad, -rad, -rad], [rad, rad, maxheight], res)
    if any(anchor):
        offset = [-anchor[0] * rad, -anchor[1] * rad, -anchor[2] * maxheight if anchor[2] > 0 else -anchor[2] * rad]
        shape = shape.translate(offset)
    return shape


def heightfield(
    data: Callable[[Any, Any], Any],
    size: list[float] = [100, 100],
    bottom: float = -20,
    maxz: float = 99,
    res: int = 10,
) -> PyShape:
    """A 3-D surface from a height function, as a libfive SDF.

    CAVEAT: unlike bosl2.shapes3d.heightfield(), `data` must be a *callable* `f(x, y) -> z`
    built from ordinary arithmetic/libfive-supported math (it gets called directly with
    libfive coordinate trees, so it becomes part of the symbolic expression) -- a 2-D array of
    height samples isn't supported, since there's no closed-form way to "look up" an arbitrary
    grid of numbers inside a libfive expression (no gather/index primitive is exposed). Use
    bosl2.shapes3d.heightfield() for array data. `xrange=`/`yrange=`/`style=` aren't
    applicable here since there's no discrete grid to sample.

    Args:
        data:   callable (x, y) -> height, evaluated symbolically
        size:   [X,Y] size of the surface (default [100,100])
        bottom: Z coordinate for the bottom of the object (default -20)
        maxz:   maximum height to model, taller values are clamped (default 99)
        res:    libfive meshing resolution passed to frep() (default 10)
    """
    assert callable(data), "pysolidfive.heightfield() only supports callable data -- see the CAVEAT in its docstring."
    bx, by = size[0] / 2, size[1] / 2

    def sdf_fn(x, y, z):
        height = lv.min(lv.max(data(x, y), bottom), maxz)
        top = z - height
        slab = lv.max(lv.abs(x) - bx, lv.abs(y) - by)
        return lv.max(lv.max(top, bottom - z), slab)

    shape = PyShape(sdf_fn, [-bx, -by, bottom], [bx, by, maxz], res)
    return shape
