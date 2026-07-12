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


# LibFile: pysolidfive/shapes2d.py
#    The 2-D layer: PyShape2D (the lazy symbolic 2-D SDF, extruded to a specific height to
#    become a PyShape) and its constructors -- circle2d/rect2d/polygon2d/stroke2d/
#    hull2d_discs/supershape2d. See pysolidfive/__init__.py's module docstring for the design
#    rationale.
#
# FileGroup: pysolidfive

from __future__ import annotations

import math

from collections.abc import Sequence

import libfive as lv

from pysolidfive._constants import CENTER
from pysolidfive.paths import (
    as_path_list,
    as_points,
    _PENALTY,
    _collinear,
    _halfplane_max_sdf,
    _hull2d_points,
    _lv_hypot,
    _polygon_dist2_xy,
    _polygon_sdf_xy,
    _radius,
    _rect2d,
    supershape_path as _supershape_path,
)
from pysolidfive.shapes3d import PyShape



# ---------------------------------------------------------------------------
# Section: 2-D shapes (PyShape2D) -- symbolic 2-D SDFs that extrude into PyShapes
# ---------------------------------------------------------------------------


class PyShape2D:
    """A lazy 2-D shape: a symbolic signed-distance function of (x, y) plus bounds -- the flat
    sibling of PyShape, for building lid-pattern shapes (shapes.py/tesselations.py) entirely in
    SDF-land. Compose with translate/rotate/scale/mirror, the boolean operators, and the two
    ops SDFs do BETTER than polygon math: offset() (a single subtraction -- exact, rounded,
    no self-intersection cleanup) and outline() (|d| - w/2, the centered outline strip).

    A 2-D SDF can't be meshed directly (frep() is 3-D only), so a PyShape2D turns into real
    geometry by extruding: extrude(height) / linear_extrude(height=...) return a PyShape (with
    the same optional rim roundover/flare treatments as polygon_prism()); anything else a
    PyShape2D doesn't define falls through __getattr__ to a thin (0.01) extrusion's mesh --
    which is almost never what you want, so extrude explicitly.
    """

    def __init__(self, sdf_fn, mn, mx, res: int = 10):
        self._sdf_fn = sdf_fn
        self.mn = [float(mn[0]), float(mn[1])]
        self.mx = [float(mx[0]), float(mx[1])]
        self.res = res

    def _wrap(self, sdf_fn, mn, mx) -> "PyShape2D":
        return PyShape2D(sdf_fn, mn, mx, self.res)

    # ---- transforms ----

    def translate(self, v) -> "PyShape2D":
        tx, ty = float(v[0]), float(v[1])
        fn = self._sdf_fn
        new_fn = lambda x, y: fn(x - tx, y - ty)  # noqa: E731
        return self._wrap(new_fn, [self.mn[0] + tx, self.mn[1] + ty], [self.mx[0] + tx, self.mx[1] + ty])

    def rotate(self, a) -> "PyShape2D":
        """Rotate by `a` degrees around the origin -- a plain scalar, or the native
        [0, 0, a] vector spelling (only z-rotation makes sense for a 2-D shape; the x/y
        components must be 0), so migrated call sites keep working unchanged."""
        if isinstance(a, (list, tuple)):
            assert len(a) == 3 and not a[0] and not a[1], f"2-D rotate only supports [0, 0, angle], got {a}"
            a = a[2]
        ang = math.radians(a)
        c, s = math.cos(ang), math.sin(ang)
        fn = self._sdf_fn
        new_fn = lambda x, y: fn(c * x + s * y, -s * x + c * y)  # noqa: E731
        corners = [[self.mn[0], self.mn[1]], [self.mx[0], self.mn[1]], [self.mn[0], self.mx[1]], [self.mx[0], self.mx[1]]]
        rot = [[c * p[0] - s * p[1], s * p[0] + c * p[1]] for p in corners]
        return self._wrap(new_fn, [min(p[0] for p in rot), min(p[1] for p in rot)], [max(p[0] for p in rot), max(p[1] for p in rot)])

    def scale(self, v) -> "PyShape2D":
        s = [float(a) for a in v] if isinstance(v, (list, tuple)) else [float(v)] * 2
        assert all(a > 0 for a in s), f"scale() factors must be positive, got {s}"
        fn = self._sdf_fn
        smin = min(s)
        new_fn = lambda x, y: smin * fn(x / s[0], y / s[1])  # noqa: E731
        return self._wrap(new_fn, [self.mn[0] * s[0], self.mn[1] * s[1]], [self.mx[0] * s[0], self.mx[1] * s[1]])

    def mirror(self, v) -> "PyShape2D":
        """Mirror across the line through the origin whose NORMAL is `v` (native convention)."""
        nx, ny = float(v[0]), float(v[1])
        nlen = math.hypot(nx, ny)
        nx, ny = nx / nlen, ny / nlen
        fn = self._sdf_fn
        # reflect: p - 2*(p.n)n
        new_fn = lambda x, y: fn(x - 2 * (x * nx + y * ny) * nx, y - 2 * (x * nx + y * ny) * ny)  # noqa: E731
        corners = [[self.mn[0], self.mn[1]], [self.mx[0], self.mn[1]], [self.mn[0], self.mx[1]], [self.mx[0], self.mx[1]]]
        ref = [[p[0] - 2 * (p[0] * nx + p[1] * ny) * nx, p[1] - 2 * (p[0] * nx + p[1] * ny) * ny] for p in corners]
        return self._wrap(new_fn, [min(p[0] for p in ref), min(p[1] for p in ref)], [max(p[0] for p in ref), max(p[1] for p in ref)])

    # ---- booleans ----

    def __or__(self, other: "PyShape2D") -> "PyShape2D":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y: lv.min(fa(x, y), fb(x, y))  # noqa: E731
        return self._wrap(new_fn, [min(self.mn[i], other.mn[i]) for i in range(2)], [max(self.mx[i], other.mx[i]) for i in range(2)])

    def __and__(self, other: "PyShape2D") -> "PyShape2D":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y: lv.max(fa(x, y), fb(x, y))  # noqa: E731
        # The intersection can only live where BOTH boxes overlap -- so the meshing region
        # (and its resolution budget) shrinks to the overlap, which is also what makes
        # clipping a big tiling with a small bound rect cheap.
        return self._wrap(new_fn, [max(self.mn[i], other.mn[i]) for i in range(2)], [min(self.mx[i], other.mx[i]) for i in range(2)])

    def __sub__(self, other: "PyShape2D") -> "PyShape2D":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y: lv.max(fa(x, y), -fb(x, y))  # noqa: E731
        return self._wrap(new_fn, list(self.mn), list(self.mx))

    # ---- the ops SDFs are uniquely good at ----

    def offset(self, delta: float = 0, r: float | None = None) -> "PyShape2D":
        """Grow (positive) or shrink (negative) by a distance -- one subtraction on the SDF, no
        polygon offsetting/self-intersection cleanup. Growth is round-style (matching native
        offset(r=...)); accepts either the delta= or r= spelling since they coincide here.
        """
        amount = float(r if r is not None else delta)
        fn = self._sdf_fn
        new_fn = lambda x, y: fn(x, y) - amount  # noqa: E731
        g = max(amount, 0.0)
        return self._wrap(new_fn, [self.mn[0] - g, self.mn[1] - g], [self.mx[0] + g, self.mx[1] + g])

    def outline(self, width: float) -> "PyShape2D":
        """The centered outline strip of this shape's boundary: |d| - width/2."""
        fn = self._sdf_fn
        new_fn = lambda x, y: lv.abs(fn(x, y)) - width / 2  # noqa: E731
        g = width / 2
        return self._wrap(new_fn, [self.mn[0] - g, self.mn[1] - g], [self.mx[0] + g, self.mx[1] + g])

    # ---- to 3-D ----

    def extrude(
        self, height: float, rounding_top: float = 0, rounding_bottom: float = 0, center: bool = False, res: int | None = None
    ) -> PyShape:
        """Extrude to a specific height along Z (base at z=0, or centered), returning a PyShape.
        The optional rim treatments follow polygon_prism()'s convention (positive roundover,
        negative flare) and reuse the same construction, over this shape's own SDF.
        """
        assert height > 0, f"extrude() needs height > 0, got {height}"
        fn = self._sdf_fn
        h = float(height)
        z0 = -h / 2 if center else 0.0

        def sdf_fn(x, y, z):
            d2d = fn(x, y)
            zz = z - z0
            out = lv.max(d2d, lv.max(zz - h, -zz))
            if rounding_top > 0:
                q1, q2 = d2d + rounding_top, (zz - h) + rounding_top
                out = lv.max(out, lv.min(lv.max(q1, q2), 0) + _lv_hypot(lv.max(q1, 0), lv.max(q2, 0)) - rounding_top)
            if rounding_bottom > 0:
                q1, q2 = d2d + rounding_bottom, -zz + rounding_bottom
                out = lv.max(out, lv.min(lv.max(q1, q2), 0) + _lv_hypot(lv.max(q1, 0), lv.max(q2, 0)) - rounding_bottom)
            if rounding_top < 0:
                f = -rounding_top
                du = lv.min(lv.abs(d2d), f + 1)
                ring = lv.max(f - _lv_hypot(du - f, zz - (h - f)), lv.max(zz - h, (h - f) - zz))
                ring = lv.max(ring, lv.abs(d2d) - f)
                out = lv.min(out, ring)
            if rounding_bottom < 0:
                f = -rounding_bottom
                du = lv.min(lv.abs(d2d), f + 1)
                ring = lv.max(f - _lv_hypot(du - f, zz - f), lv.max(-zz, zz - f))
                ring = lv.max(ring, lv.abs(d2d) - f)
                out = lv.min(out, ring)
            return out

        flare = max(0.0, -rounding_top, -rounding_bottom)
        return PyShape(
            sdf_fn,
            [self.mn[0] - flare, self.mn[1] - flare, z0],
            [self.mx[0] + flare, self.mx[1] + flare, z0 + h],
            res if res is not None else self.res,
        )

    def linear_extrude(self, height: float, center: bool = False) -> PyShape:
        """Native-spelling alias for extrude(), so migrated 2-D shapes keep working at existing
        `.linear_extrude(height=...)` call sites."""
        return self.extrude(height, center=center)

    def __getattr__(self, name):
        # Fall through to a thin extrusion's meshed solid -- an escape hatch for native-only
        # attributes (color/show/...); extrude explicitly whenever the height matters.
        return getattr(self.extrude(0.01).mesh(), name)


def circle2d(r: float | None = None, d: float | None = None, res: int = 10) -> PyShape2D:
    """A circle at the origin -- the exact SDF `length(p) - r`."""
    rad = _radius(r=r, d=d, dflt=1)
    return PyShape2D(lambda x, y: _lv_hypot(x, y) - rad, [-rad, -rad], [rad, rad], res)


def rect2d(
    size,
    rounding: "float | Sequence[float]" = 0,
    chamfer: "float | Sequence[float]" = 0,
    anchor: "Sequence[float]" = CENTER,
    res: int = 10,
) -> PyShape2D:
    """An axis-aligned rectangle with optional corner rounding or chamfering -- a single radius
    for all four corners, or a per-corner list in BOSL2 rect() order ([X+Y+, X-Y+, X-Y-, X+Y-],
    counterclockwise from the +x+y corner), reusing the same per-corner quadrant SDF the 3-D
    cuboid edge machinery is built on. `anchor` uses the usual direction-vector convention.
    """
    sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(v) for v in size]
    hx, hy = sz[0] / 2, sz[1] / 2
    has_rounding = (rounding != 0) if isinstance(rounding, (int, float)) else any(rounding)
    has_chamfer = (chamfer != 0) if isinstance(chamfer, (int, float)) else any(chamfer)
    assert not (has_rounding and has_chamfer), "Cannot specify nonzero rounding and chamfer together"
    mode = "chamfer" if has_chamfer else "round"
    amt = chamfer if has_chamfer else rounding
    per_corner = [float(amt)] * 4 if isinstance(amt, (int, float)) else [float(v) for v in amt]
    assert len(per_corner) == 4, f"per-corner treatment needs 4 values, got {per_corner}"
    assert max(per_corner) <= min(hx, hy) + 1e-9, f"corner treatment {per_corner} exceeds half the rectangle {sz}"
    # BOSL2 corner order [(+,+), (-,+), (-,-), (+,-)] -> _rect2d's [(-,-), (+,-), (-,+), (+,+)].
    amount = [per_corner[2], per_corner[3], per_corner[1], per_corner[0]]

    def sdf_fn(x, y):
        return _rect2d(x, y, hx, hy, amount, mode)

    shape = PyShape2D(sdf_fn, [-hx, -hy], [hx, hy], res)
    ax, ay = (list(anchor) + [0, 0])[:2]
    if ax or ay:
        shape = shape.translate([-ax * hx, -ay * hy])
    return shape


def supershape2d(
    step: float = 0.5,
    n: int | None = None,
    m1: float = 4,
    m2: float | None = None,
    n1: float | None = None,
    n2: float | None = None,
    n3: float | None = None,
    a: float = 1,
    b: float | None = None,
    r: float | None = None,
    d: float | None = None,
    res: int = 10,
) -> PyShape2D:
    """A superformula shape -- the outline sampled in plain Python (pysolidfive._paths, same
    parameters and sampling as the bosl2 port's supershape()) and turned into a polygon2d()."""
    return polygon2d(_supershape_path(step=step, n=n, m1=m1, m2=m2, n1=n1, n2=n2, n3=n3, a=a, b=b, r=r, d=d), res=res)


def polygon2d(paths, res: int = 10) -> PyShape2D:
    """An arbitrary SIMPLE polygon (or a list of disjoint ones), via the same convex-deficiency
    decomposition polygon_prism() uses -- concave outlines welcome, holes not supported.
    Accepts any array-like path spelling (per the numpy-paths convention)."""
    path_list = as_path_list(paths)
    for p in path_list:
        assert len(p) >= 3, f"polygon2d(): every path needs >= 3 points, got {len(p)}"

    def sdf_fn(x, y):
        d = None
        for p in path_list:
            dp = _polygon_sdf_xy(x, y, p)
            d = dp if d is None else lv.min(d, dp)
        return d

    xs = [p[0] for path in path_list for p in path]
    ys = [p[1] for path in path_list for p in path]
    return PyShape2D(sdf_fn, [min(xs), min(ys)], [max(xs), max(ys)], res)


def region2d(paths: list, res: int = 10) -> PyShape2D:
    """BOSL2-style REGION data as a PyShape2D: a list of simple outlines with even-odd nesting
    semantics -- an outline inside another outline is a hole, an outline inside a hole is an
    island, and so on -- exactly what the real-BOSL2 region functions (make_region/union/
    difference/offset_stroke/...) hand back and what the native `region()` helper in
    base_bgtk.py renders via polygon(paths=...). This is the SDF equivalent for code building
    on pysolidfive: nesting depths are worked out once in Python (ray-casting a vertex of each
    outline against the others), holes subtract from their direct parents, and islands rejoin
    the union.
    """
    cleaned = as_path_list(paths)
    for p in cleaned:
        assert len(p) >= 3, f"region2d(): every outline needs >= 3 points, got {len(p)}"

    def contains(poly, pt) -> bool:
        # Standard even-odd ray cast (+x direction).
        x, y = pt
        inside = False
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                t = (y - y1) / (y2 - y1)
                if x < x1 + t * (x2 - x1):
                    inside = not inside
        return inside

    depths = []
    for i, p in enumerate(cleaned):
        depth = sum(1 for j, q in enumerate(cleaned) if j != i and contains(q, p[0]))
        depths.append(depth)

    def sdf_fn(x, y):
        d = None
        for i, p in enumerate(cleaned):
            if depths[i] % 2 != 0:
                continue  # holes are handled from their parents below
            dp = _polygon_sdf_xy(x, y, p)
            for j, q in enumerate(cleaned):
                if j != i and depths[j] == depths[i] + 1 and contains(p, q[0]):
                    dp = lv.max(dp, -_polygon_sdf_xy(x, y, q))
            d = dp if d is None else lv.min(d, dp)
        return d

    xs = [p[0] for path in cleaned for p in path]
    ys = [p[1] for path in cleaned for p in path]
    return PyShape2D(sdf_fn, [min(xs), min(ys)], [max(xs), max(ys)], res)


def union2d(shapes: list[PyShape2D]) -> PyShape2D:
    """Union of many shapes as a balanced pairwise tree. A linear `a | b | c | ...` chain
    nests one lambda per piece, so composing hundreds of pieces (a dense tiling, say)
    overflows Python's recursion limit when the SDF is finally evaluated -- the tree keeps
    the evaluation depth at log2(n) instead."""
    shapes = list(shapes)
    assert shapes, "union2d() needs at least one shape"
    while len(shapes) > 1:
        shapes = [
            shapes[i] | shapes[i + 1] if i + 1 < len(shapes) else shapes[i] for i in range(0, len(shapes), 2)
        ]
    return shapes[0]


def stroke2d(path, width: float = 1, closed: bool = False, res: int = 10) -> PyShape2D:
    """A path drawn with round caps and joins (BOSL2 stroke()'s default look) -- exactly, as
    the min over the segments' capsule SDFs (distance-to-segment minus width/2)."""
    pts = as_points(path)
    assert len(pts) >= 2, "stroke2d() needs at least 2 points"
    segs = pts if closed else pts[:-1]

    def sdf_fn(x, y):
        d2 = None
        n = len(pts)
        for i in range(len(segs)):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            elen2 = ex * ex + ey * ey
            if elen2 < 1e-18:
                continue
            px, py = x - ax, y - ay
            t = lv.max(0, lv.min(1, (px * ex + py * ey) / elen2))
            dx, dy = px - t * ex, py - t * ey
            seg_d2 = dx * dx + dy * dy
            d2 = seg_d2 if d2 is None else lv.min(d2, seg_d2)
        return lv.sqrt(d2) - width / 2

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    g = width / 2
    return PyShape2D(sdf_fn, [min(xs) - g, min(ys) - g], [max(xs) + g, max(ys) + g], res)


def hull2d_discs(discs: list, res: int = 10) -> PyShape2D:
    """The convex hull of a set of discs [(x, y, r), ...] -- the SDF equivalent of the
    hull(circle().translate(), circle().translate(), ...) idiom all over shapes.py. EXACT for
    equal radii (the true distance to the centers' convex hull, minus r -- computed with the
    branchless exact-convex form, so the rounded corners are genuine arcs, not the sharp
    corners a plain half-plane max would give); for mixed radii it conservatively uses the
    largest radius for the hull body unioned with each disc exactly, which matches the visual
    silhouette whenever the smaller discs sit inside the hull of the larger ones.
    """
    ds = [(float(c[0]), float(c[1]), float(c[2])) for c in discs]
    assert ds, "hull2d_discs() needs at least one disc"
    if len(ds) == 1:
        cx, cy, r = ds[0]
        return circle2d(r=r, res=res).translate([cx, cy])

    centers = [[c[0], c[1]] for c in ds]
    rmax = max(c[2] for c in ds)

    def sdf_fn(x, y):
        if len(centers) == 2 or _collinear(centers):
            # Degenerate hull: distance to the segment chain between extreme centers.
            d2 = None
            for i in range(len(centers) - 1):
                ax, ay = centers[i]
                bx, by = centers[i + 1]
                ex, ey = bx - ax, by - ay
                elen2 = ex * ex + ey * ey
                if elen2 < 1e-18:
                    continue
                px, py = x - ax, y - ay
                t = lv.max(0, lv.min(1, (px * ex + py * ey) / elen2))
                dx, dy = px - t * ex, py - t * ey
                sd2 = dx * dx + dy * dy
                d2 = sd2 if d2 is None else lv.min(d2, sd2)
            body = lv.sqrt(d2) - rmax
        else:
            hull_pts = _hull2d_points(centers)
            halfmax = _halfplane_max_sdf(x, y, hull_pts)
            true_out = lv.sqrt(_polygon_dist2_xy(x, y, hull_pts))
            exact = lv.max(halfmax, true_out + _PENALTY * lv.min(halfmax, 0))
            body = exact - rmax
        out = body
        for cx, cy, r in ds:
            if r < rmax - 1e-12:
                out = lv.min(out, _lv_hypot(x - cx, y - cy) - r)
        return out

    xs = [c[0] - c[2] for c in ds] + [c[0] + c[2] for c in ds]
    ys = [c[1] - c[2] for c in ds] + [c[1] + c[2] for c in ds]
    return PyShape2D(sdf_fn, [min(xs), min(ys)], [max(xs), max(ys)], res)
