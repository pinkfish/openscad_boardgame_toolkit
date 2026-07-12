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


# LibFile: pysolidfive/paths.py
#    Everything 2-D-outline related that the shape layers build on: the exact/decomposed
#    polygon SDF machinery (convex fast path, convex-deficiency decomposition for concave
#    outlines, unsigned outline distance), the per-corner rounded/chamfered rect SDF, the
#    2-D convex hull, shared SDF utilities (_lv_hypot/_radius/_PENALTY), and the numpy-based
#    path samplers (superformula outlines, Bezier paths, the BOSL2-style egg curve) that feed
#    polygon2d()/stroke2d(). Path data is numpy throughout (see as_points()); only the native
#    boundaries get plain-python lists. See pysolidfive/__init__.py's module docstring for the design
#    rationale behind the SDF techniques used here.
#
# FileGroup: pysolidfive

from __future__ import annotations

import math

import libfive as lv
import numpy as np
from numpy.typing import ArrayLike, NDArray

from pysolidfive._edges import _pick_radius


def as_path_list(paths) -> "list[NDArray[np.float64]]":
    """Normalize `paths` -- one path, or a list of paths, in any array-like spelling -- to a
    list of (n, 2) float arrays (the multi-outline entry-point convention polygon2d()/
    region2d() accept)."""
    if isinstance(paths, np.ndarray):
        return [as_points(paths)] if paths.ndim == 2 else [as_points(q) for q in paths]
    first = paths[0]
    if isinstance(first, np.ndarray) or isinstance(first[0], (list, tuple, np.ndarray)):
        return [as_points(q) for q in paths]
    return [as_points(paths)]


def as_points(pts: ArrayLike) -> NDArray[np.float64]:
    """The library-wide normalization for 2-D point paths: an (n, 2) float array. Accepts
    any array-like (lists, tuples, arrays, Vec-ish rows). Per the project convention, path
    data is numpy everywhere INSIDE the libraries -- but must be `.tolist()`ed before
    crossing any native boundary (frep bounds, polygon(), translate(), the osuse FFI):
    raw ndarrays there raise SystemError/TypeError and poison the interpreter."""
    arr = np.asarray(pts, dtype=float)
    assert arr.ndim == 2, f"expected a point path, got shape {arr.shape}"
    return arr


# Penalty multiplier used to push a quadrant candidate's SDF value far above any other
# candidate's real value once outside its own quadrant (see module docstring). Dimensionless;
# the mask itself already carries the right length units, so this just needs to be
# comfortably larger than 1 -- 10000 gives a huge safety margin without risking float
# precision issues at typical (mm-scale) board-game part sizes.
_PENALTY = 10000.0
_SQRT2 = math.sqrt(2)


def _radius(
    r1: float | None = None,
    d1: float | None = None,
    r2: float | None = None,
    d2: float | None = None,
    r: float | None = None,
    d: float | None = None,
    dflt: float = 1,
) -> float:
    """_pick_radius(), guaranteed non-None since `dflt` is always a real number here -- unlike
    _pick_radius() itself, whose `dflt: None` default means its return type is `float | None`
    even when a caller always passes a concrete `dflt`. Not for callers that genuinely need to
    tell "not specified" apart from a real radius (see torus()/tube(), which call
    _pick_radius() directly with `dflt=None`)."""
    result = _pick_radius(r1=r1, d1=d1, r2=r2, d2=d2, r=r, d=d, dflt=dflt)
    assert result is not None
    return result


def _lv_hypot(a, b):
    return lv.sqrt(a * a + b * b)


def _rect2d(u, v, bu: float, bv: float, amount: list[float], mode):
    """2-D SDF of a `2*bu` x `2*bv` rectangle centered at the origin, with an independent
    per-corner edge treatment -- rounding radius or chamfer size, per `mode` (one string for
    all four corners, or a per-corner list) -- given by `amount[i]` at each of its 4 corners.
    `amount` is indexed the same way as bosl2.shapes3d.EDGE_OFFSETS's per-axis rows:
    [(-,-), (+,-), (-,+), (+,+)] in (u, v) sign.
    """
    corner_modes = [mode] * 4 if isinstance(mode, str) else list(mode)
    candidates = []
    for ci, (su, sv, a) in enumerate(((-1, -1, amount[0]), (1, -1, amount[1]), (-1, 1, amount[2]), (1, 1, amount[3]))):
        cmode = corner_modes[ci]
        if cmode == "round":
            # Rounding is a Minkowski sum: shrink the rect by r, then re-offset the corner
            # outward by r via the hypot() term -- qu/qv are shifted by +r accordingly.
            qu = lv.abs(u) - bu + a
            qv = lv.abs(v) - bv + a
            base = lv.min(lv.max(qu, qv), 0) + _lv_hypot(lv.max(qu, 0), lv.max(qv, 0)) - a
        else:
            assert cmode == "chamfer"
            # Chamfer is a plane cut: intersect the two plain axis-aligned half-planes with
            # a third diagonal half-plane `a` in from the sharp corner. qu/qv are NOT shifted
            # by `a` here (unlike rounding) -- only the diagonal term is.
            qu = lv.abs(u) - bu
            qv = lv.abs(v) - bv
            base = lv.max(lv.max(qu, qv), (qu + qv + a) / _SQRT2)
        mask = lv.max(0, -su * u) + lv.max(0, -sv * v)
        candidates.append(base + _PENALTY * mask)
    return lv.min(lv.min(candidates[0], candidates[1]), lv.min(candidates[2], candidates[3]))


def _polygon_sdf_xy(x, y, pts: ArrayLike):
    """Signed distance to an arbitrary SIMPLE polygon (convex or concave, either winding order)
    at the 2-D point (x, y) -- unlike polygon_extrude()'s max-of-half-planes (convex only),
    this handles concave outlines correctly. The zero set (the actual surface, and therefore
    the sign) is exact; the *value* is exact perpendicular distance near every face and a
    sign-correct underestimate out past vertices -- the same documented tradeoff as
    polygon_extrude() and the rest of this module.

    Convex polygons are just the max of the edges' signed half-plane distances. Concave ones
    use a convex-deficiency decomposition: the polygon = its convex hull minus the "pocket"
    polygons between the hull and the boundary, each pocket handled recursively the same way,
    so the whole thing is a pure min/max tree of half-planes. An earlier version computed the
    concave sign from the winding number (an atan2 sum per edge) -- exact in value, but its
    angle-sum branch cut lies exactly on the polygon boundary, and libfive's dual-contouring
    feature detection turned that gradient discontinuity into spike/fin mesh artifacts (badly
    on dense round_corners() outlines, and it interval-pruned terribly on top). The
    decomposition has no branch cuts anywhere and prunes like any other max() chain.
    """
    return _convex_deficiency_sdf(x, y, _ccw(as_points(pts)))


def _ccw(pts: NDArray[np.float64]) -> NDArray[np.float64]:
    """`pts` in counter-clockwise order (reversed if the signed area says clockwise)."""
    nxt = np.roll(pts, -1, axis=0)
    area2 = float(np.sum(pts[:, 0] * nxt[:, 1] - nxt[:, 0] * pts[:, 1]))
    return pts if area2 > 0 else pts[::-1]


def _halfplane_max_sdf(x, y, ccw_pts: NDArray[np.float64]):
    """max of signed half-plane distances over a CCW convex polygon's edges (zero-length edges
    skipped, tolerating duplicate points from densified/offset path data)."""
    d = None
    n = len(ccw_pts)
    for i in range(n):
        x0, y0 = ccw_pts[i]
        x1, y1 = ccw_pts[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        elen = math.hypot(ex, ey)
        if elen < 1e-12:
            continue
        e = (ey / elen) * (x - x0) + (-ex / elen) * (y - y0)
        d = e if d is None else lv.max(d, e)
    assert d is not None, "polygon has no non-degenerate edges"
    return d


def _convex_deficiency_sdf(x, y, ccw_pts: NDArray[np.float64], _depth: int = 0):
    """See _polygon_sdf_xy(): CCW polygon as (convex hull) minus (recursive pockets)."""
    assert _depth < 16, "polygon decomposition recursed implausibly deep -- is the outline self-intersecting?"
    if _is_convex(ccw_pts):
        return _halfplane_max_sdf(x, y, ccw_pts)

    hull_idx = _convex_hull_indices(ccw_pts)
    d = _halfplane_max_sdf(x, y, ccw_pts[hull_idx])

    # Each stretch of boundary between consecutive hull vertices with interior points in
    # between is a pocket: the chain plus the hull's bridge edge closing it. The chain runs
    # CCW along the polygon, which walks the pocket's own outline CW -- _ccw() renormalizes
    # before recursing. Subtracting is just max(d, -pocket).
    n = len(ccw_pts)
    for k in range(len(hull_idx)):
        i0, i1 = hull_idx[k], hull_idx[(k + 1) % len(hull_idx)]
        chain = [ccw_pts[i0]]
        j = (i0 + 1) % n
        while j != i1:
            chain.append(ccw_pts[j])
            j = (j + 1) % n
        chain.append(ccw_pts[i1])
        if len(chain) < 3:
            continue
        pocket = _convex_deficiency_sdf(x, y, _ccw(np.asarray(chain)), _depth + 1)
        d = lv.max(d, -pocket)
    return d


def _convex_hull_indices(ccw_pts: NDArray[np.float64]) -> list[int]:
    """Indices (into `ccw_pts`, in CCW boundary order) of the polygon's convex hull vertices --
    a wrap-aware pass dropping every vertex that turns clockwise (or is collinear) between its
    surviving neighbours."""
    n = len(ccw_pts)
    idx = list(range(n))
    changed = True
    while changed and len(idx) > 3:
        changed = False
        kept = []
        m = len(idx)
        for k in range(m):
            ax, ay = ccw_pts[idx[(k - 1) % m]]
            bx, by = ccw_pts[idx[k]]
            cx, cy = ccw_pts[idx[(k + 1) % m]]
            cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
            if cross > 1e-12:
                kept.append(idx[k])
            else:
                changed = True
        idx = kept
    return idx


def _polygon_dist2_xy(x, y, pts: ArrayLike):
    """UNSIGNED squared distance to the polygon outline `pts` at (x, y): the min over per-edge
    point-to-segment distances (the segment clamp is just min/max -- no atan2/winding needed,
    so unlike the signed form this stays branch-cut-free everywhere)."""
    pts = as_points(pts)
    n = len(pts)
    dist2_min = None
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        elen2 = ex * ex + ey * ey
        px, py = x - ax, y - ay
        t = lv.max(0, lv.min(1, (px * ex + py * ey) / elen2))
        dx, dy = px - t * ex, py - t * ey
        d2 = dx * dx + dy * dy
        dist2_min = d2 if dist2_min is None else lv.min(dist2_min, d2)
    return dist2_min


def _is_convex(pts: NDArray[np.float64]) -> bool:
    """True if the simple polygon `pts` is convex: every consecutive edge pair turns the same
    way (cross products all >= 0 or all <= 0, tolerating collinear runs from densified arcs)."""
    n = len(pts)
    pos = neg = False
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        cx, cy = pts[(i + 2) % n]
        cross = (bx - ax) * (cy - by) - (by - ay) * (cx - bx)
        if cross > 1e-12:
            pos = True
        elif cross < -1e-12:
            neg = True
        if pos and neg:
            return False
    return True


def _collinear(pts: ArrayLike) -> bool:
    arr = as_points(pts)
    if len(arr) < 3:
        return True
    ax, ay = arr[0]
    bx, by = arr[1]
    return bool(np.all(np.abs((bx - ax) * (arr[2:, 1] - ay) - (by - ay) * (arr[2:, 0] - ax)) < 1e-9))


def _hull2d_points(pts: ArrayLike) -> NDArray[np.float64]:
    """2-D convex hull (Andrew's monotone chain), CCW, of the given points."""
    unique = sorted({(float(p[0]), float(p[1])) for p in as_points(pts)})
    if len(unique) <= 2:
        return np.asarray([list(p) for p in unique], dtype=float)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    for p in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: list = []
    for p in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.asarray([list(p) for p in lower[:-1] + upper[:-1]], dtype=float)




def superformula(theta: float, m1: float, m2: float, n1: float, n2: float, n3: float, a: float, b: float) -> float:
    """The superformula radius at angle `theta` (degrees)."""
    t1 = abs(math.cos(math.radians(m1 * theta / 4)) / a) ** n2
    t2 = abs(math.sin(math.radians(m2 * theta / 4)) / b) ** n3
    return (t1 + t2) ** (-1.0 / n1)


def supershape_path(
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
) -> NDArray[np.float64]:
    """The superformula outline as a closed point path -- same parameters and sampling as the
    bosl2 port's supershape() (which builds a polygon() from the identical path)."""
    n_pts = n if n is not None else math.ceil(360.0 / step)
    n1v = n1 if n1 is not None else 1
    m2v = m2 if m2 is not None else m1
    n2v = n2 if n2 is not None else n1v
    n3v = n3 if n3 is not None else n2v
    bv = b if b is not None else a
    angs = [360.0 - i * 360.0 / n_pts for i in range(n_pts)]
    rvals = [superformula(t, m1, m2v, n1v, n2v, n3v, a, bv) for t in angs]
    rad = r if r is not None else (d / 2 if d is not None else None)
    scale = (rad / max(rvals)) if rad is not None else 1.0
    ang_r = np.radians(np.asarray(angs))
    rv = scale * np.asarray(rvals)
    return np.stack([rv * np.cos(ang_r), rv * np.sin(ang_r)], axis=1)


def bezier_points(curve: ArrayLike, u: float) -> NDArray[np.float64]:
    """Evaluate a Bezier curve (any degree, from its control points) at parameter u in [0, 1]
    -- de Casteljau."""
    pts = np.asarray(curve, dtype=float)
    while len(pts) > 1:
        pts = pts[:-1] + (pts[1:] - pts[:-1]) * u
    return pts[0]


def bezpath_points(bezpath: ArrayLike, splinesteps: int = 16, N: int = 3, endpoint: bool = True) -> NDArray[np.float64]:
    """Sample a Bezier path (degree-N segments sharing endpoints, len % N == 1) into a point
    array -- same shape as the bosl2 port's bezpath_curve()."""
    bez = as_points(bezpath)
    assert len(bez) % N == 1, f"A degree {N} bezier path should have a multiple of {N} points in it, plus 1."
    segs = (len(bez) - 1) // N
    out = []
    for seg in range(segs):
        ctrl = bez[seg * N : (seg + 1) * N + 1]
        for i in range(splinesteps):
            out.append(bezier_points(ctrl, i / splinesteps))
    if endpoint:
        out.append(bez[-1])
    return np.asarray(out, dtype=float)


def egg_path(length: float, r1: float, r2: float, R: float, n: int = 90) -> NDArray[np.float64]:
    """The BOSL2-style egg outline: two end circles of radius r1 (left) and r2 (right), a
    total length, and side arcs of radius R blending them -- as a closed point path.
    Mirrors the bosl2 port's _egg_path() construction, with a fixed arc sampling density."""
    assert length > 0
    assert R > length / 2, "Side radius R must be larger than length/2"
    assert length > r1 + r2, "Length must be longer than r1+r2"
    c1 = [-length / 2 + r1, 0.0]
    c2 = [length / 2 - r2, 0.0]
    m_pts = list(reversed(_circle_circle_intersection(R - r1, c1, R - r2, c2)))
    assert len(m_pts) == 2, "egg_path(): circles do not intersect for the given length/r1/r2/R."
    arcparms = []
    for m in m_pts:
        u1 = _unit2([c1[0] - m[0], c1[1] - m[1]])
        u2 = _unit2([c2[0] - m[0], c2[1] - m[1]])
        arcparms.append([m, [c1[0] + r1 * u1[0], c1[1] + r1 * u1[1]], [c2[0] + r2 * u2[0], c2[1] + r2 * u2[1]]])
    path: list[list[float]] = []
    path += _arc_between(c2, [length / 2, 0.0], arcparms[0][2], n)
    path += _arc_between(arcparms[0][0], arcparms[0][2], arcparms[0][1], n)
    path += _arc_through(c1, arcparms[0][1], [-length / 2, 0.0], arcparms[1][1], n)
    path += _arc_between(arcparms[1][0], arcparms[1][1], arcparms[1][2], n)
    path += _arc_between(c2, arcparms[1][2], [length / 2, 0.0], n)
    return np.asarray(path, dtype=float)


def _unit2(v: list[float]) -> list[float]:
    n = math.hypot(v[0], v[1])
    return [v[0] / n, v[1] / n]


def _circle_circle_intersection(r1: float, c1: list[float], r2: float, c2: list[float]) -> list[list[float]]:
    d = math.dist(c1, c2)
    if d == 0 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h_sq = r1**2 - a**2
    h = math.sqrt(max(0.0, h_sq))
    mx = c1[0] + a * (c2[0] - c1[0]) / d
    my = c1[1] + a * (c2[1] - c1[1]) / d
    ox = h * (c2[1] - c1[1]) / d
    oy = h * (c2[0] - c1[0]) / d
    return [[mx + ox, my - oy], [mx - ox, my + oy]]


def _arc_points(cp: list[float], radius: float, a0: float, delta: float, steps: int) -> list[list[float]]:
    return [
        [cp[0] + radius * math.cos(math.radians(a0 + delta * i / steps)), cp[1] + radius * math.sin(math.radians(a0 + delta * i / steps))]
        for i in range(steps)  # endpoint deliberately excluded; the next arc supplies it
    ]


def _arc_between(cp: list[float], p_start: list[float], p_end: list[float], n: int) -> list[list[float]]:
    """Arc around `cp` from p_start to p_end, sweeping the shorter way around."""
    radius = math.dist(cp, p_start)
    a0 = math.degrees(math.atan2(p_start[1] - cp[1], p_start[0] - cp[0]))
    a1 = math.degrees(math.atan2(p_end[1] - cp[1], p_end[0] - cp[0]))
    delta = (a1 - a0 + 180) % 360 - 180
    steps = max(3, math.ceil(n * abs(delta) / 360))
    return _arc_points(cp, radius, a0, delta, steps)


def _arc_through(cp: list[float], p_start: list[float], p_mid: list[float], p_end: list[float], n: int) -> list[list[float]]:
    """Arc around `cp` from p_start to p_end, sweeping through p_mid (maybe the long way)."""
    radius = math.dist(cp, p_start)
    a0 = math.degrees(math.atan2(p_start[1] - cp[1], p_start[0] - cp[0]))
    am = math.degrees(math.atan2(p_mid[1] - cp[1], p_mid[0] - cp[0]))
    a1 = math.degrees(math.atan2(p_end[1] - cp[1], p_end[0] - cp[0]))
    d_mid = (am - a0) % 360
    d_end = (a1 - a0) % 360
    delta = d_end if d_mid <= d_end else d_end - 360
    steps = max(3, math.ceil(n * abs(delta) / 360))
    return _arc_points(cp, radius, a0, delta, steps)


# ---------------------------------------------------------------------------
# Section: Open-path calculus (ports of the BOSL2 helpers rabbit_clip() needs)
# ---------------------------------------------------------------------------


def _v_sub(a, b) -> NDArray[np.float64]:
    return np.asarray(a, dtype=float) - np.asarray(b, dtype=float)


def _v_add(a, b) -> NDArray[np.float64]:
    return np.asarray(a, dtype=float) + np.asarray(b, dtype=float)


def _v_scale(a, s) -> NDArray[np.float64]:
    return np.asarray(a, dtype=float) * float(s)


def _v_norm(a) -> float:
    return float(np.linalg.norm(np.asarray(a, dtype=float)))


def _v_unit(a) -> NDArray[np.float64]:
    arr = np.asarray(a, dtype=float)
    n = float(np.linalg.norm(arr))
    assert n > 1e-12, "cannot normalize a zero vector"
    return arr / n


def _v_dot(a, b) -> float:
    return float(np.asarray(a, dtype=float) @ np.asarray(b, dtype=float))


def _lerp_pt(a, b, t) -> NDArray[np.float64]:
    aa = np.asarray(a, dtype=float)
    return aa + (np.asarray(b, dtype=float) - aa) * float(t)


def line_normal(p1, p2) -> NDArray[np.float64]:
    """Unit 2-D normal (perpendicular, to the LEFT of travel) of the line through p1, p2 --
    byte-for-byte the bosl2 port's convention."""
    return _v_unit([p1[1] - p2[1], p2[0] - p1[0]])


def deriv(data: ArrayLike, h: "float | ArrayLike" = 1, closed: bool = False) -> NDArray[np.float64]:
    """BOSL2 deriv(): numerical first derivative of vector-valued samples, with either a
    scalar step or a per-segment step list (the non-uniform variant path_tangents() feeds
    with segment lengths)."""
    pts = np.asarray(data, dtype=float)
    L = len(pts)
    assert L >= 2
    if isinstance(h, (int, float)):
        if closed:
            return (np.roll(pts, -1, axis=0) - np.roll(pts, 1, axis=0)) / (2 * h)
        first = pts[1] - pts[0] if L < 3 else 3 * (pts[1] - pts[0]) - (pts[2] - pts[1])
        last = pts[L - 1] - pts[L - 2] if L < 3 else (pts[L - 3] - pts[L - 2]) - 3 * (pts[L - 2] - pts[L - 1])
        mid = (pts[2:] - pts[:-2]) / (2 * h) if L > 2 else np.empty((0, pts.shape[1]))
        return np.vstack([[first / (2 * h)], mid, [last / (2 * h)]])

    hs = np.asarray(h, dtype=float)

    def dnu(f1, fc, f2, h1: float, h2: float) -> NDArray[np.float64]:
        g1 = _lerp_pt(fc, f1, h2 / h1) if h2 < h1 else f1
        g2 = _lerp_pt(fc, f2, h1 / h2) if h1 < h2 else f2
        return (np.asarray(g2, dtype=float) - np.asarray(g1, dtype=float)) / (2 * min(h1, h2))

    if closed:
        assert len(hs) == L
        return np.asarray(
            [dnu(pts[(L + i - 1) % L], pts[i], pts[(i + 1) % L], hs[(i - 1) % L], hs[i]) for i in range(L)]
        )
    assert len(hs) == L - 1
    return np.vstack(
        [[(pts[1] - pts[0]) / hs[0]]]
        + [[dnu(pts[i - 1], pts[i], pts[i + 1], hs[i - 1], hs[i])] for i in range(1, L - 1)]
        + [[(pts[L - 1] - pts[L - 2]) / hs[L - 2]]]
    )


def path_tangents(path: ArrayLike, closed: bool = False, uniform: bool = True) -> NDArray[np.float64]:
    """BOSL2 path_tangents(): unit tangent at each path point (uniform=False weights the
    derivative by segment lengths, which is what rabbit_clip() uses)."""
    pts = as_points(path)
    if uniform:
        d = deriv(pts, closed=closed)
    else:
        seg_ends = np.roll(pts, -1, axis=0) if closed else pts[1:]
        seg_starts = pts if closed else pts[:-1]
        segs = np.linalg.norm(seg_ends - seg_starts, axis=1)
        d = deriv(pts, h=segs, closed=closed)
    norms = np.linalg.norm(d, axis=1, keepdims=True)
    assert np.all(norms > 1e-12), "cannot normalize a zero tangent"
    return d / norms


def _cubic_real_roots(p: list[float]) -> list[float]:
    """Real roots of a polynomial in power form (highest degree first), degree <= 3 --
    enough for path_to_bezpath()'s extreme-finding cubic. Closed-form (Cardano with the
    trigonometric casework)."""
    # trim leading (near-)zeros
    coeffs = list(p)
    while coeffs and abs(coeffs[0]) < 1e-14:
        coeffs.pop(0)
    if len(coeffs) <= 1:
        return []
    if len(coeffs) == 2:
        return [-coeffs[1] / coeffs[0]]
    if len(coeffs) == 3:
        a, b, c = coeffs
        disc = b * b - 4 * a * c
        if disc < 0:
            return []
        s = math.sqrt(disc)
        return [(-b - s) / (2 * a), (-b + s) / (2 * a)]
    a, b, c, d = coeffs
    # depressed cubic t^3 + pt + q, x = t - b/(3a)
    pp = (3 * a * c - b * b) / (3 * a * a)
    qq = (2 * b**3 - 9 * a * b * c + 27 * a * a * d) / (27 * a**3)
    shift = -b / (3 * a)
    disc = -(4 * pp**3 + 27 * qq * qq)
    if disc > 0:
        # three real roots (trigonometric method)
        m = 2 * math.sqrt(-pp / 3)
        theta = math.acos(max(-1.0, min(1.0, 3 * qq / (pp * m)))) / 3
        return [shift + m * math.cos(theta - 2 * math.pi * k / 3) for k in range(3)]
    # one real root (Cardano)
    u = -qq / 2 + math.sqrt(max(0.0, qq * qq / 4 + pp**3 / 27))
    v = -qq / 2 - math.sqrt(max(0.0, qq * qq / 4 + pp**3 / 27))
    cbrt = lambda x: math.copysign(abs(x) ** (1 / 3), x)  # noqa: E731
    return [shift + cbrt(u) + cbrt(v)]


def path_to_bezpath(
    path: ArrayLike, closed: bool = False, tangents: ArrayLike | None = None, uniform: bool = False, size=None, relsize=None
) -> NDArray[np.float64]:
    """BOSL2 path_to_bezpath(): a cubic bezier path through the input points with the given
    (or derived) tangents, control-point lengths chosen so the curve deviates from each
    segment by `size` (absolute) or `relsize` (fraction of segment length)."""
    assert size is None or relsize is None, "Can't define both size and relsize"
    path = as_points(path)
    curvesize = size if size is not None else (relsize if relsize is not None else 0.1)
    relative = size is None
    lastpt = len(path) - (0 if closed else 1)
    sizevect = [curvesize] * lastpt if isinstance(curvesize, (int, float)) else list(curvesize)
    assert len(sizevect) == lastpt
    tang = (
        np.asarray([_v_unit(tv) for tv in np.asarray(tangents, dtype=float)])
        if tangents is not None
        else path_tangents(path, uniform=uniform, closed=closed)
    )

    out = []
    for i in range(lastpt):
        first = path[i]
        second = path[(i + 1) % len(path)]
        seglength = math.dist(first, second)
        assert seglength > 0, f"zero-length path segment at index {i}"
        segdir = (second - first) / seglength
        tangent1 = tang[i]
        tangent2 = -tang[(i + 1) % len(path)]  # points backward, along the curve
        parallel = abs(_v_dot(tangent1, segdir)) + abs(_v_dot(tangent2, segdir))
        lmax = seglength / parallel if parallel > 1e-12 else float("inf")
        sz = sizevect[i] * seglength if relative else sizevect[i]
        normal1 = tangent1 - segdir * _v_dot(tangent1, segdir)
        normal2 = tangent2 - segdir * _v_dot(tangent2, segdir)
        n11, n12, n22 = _v_dot(normal1, normal1), _v_dot(normal1, normal2), _v_dot(normal2, normal2)
        poly = [
            -3 * n11 + 6 * n12 - 3 * n22,
            7 * n11 - 9 * n12 + 2 * n22,
            -5 * n11 + 3 * n12,
            n11,
        ]
        if math.sqrt(sum(c * c for c in poly)) < 1e-12:
            uextreme = []
        else:
            uextreme = [r for r in _cubic_real_roots(poly) if 0 < r < 1]
        ctrl = np.asarray([np.zeros_like(normal1), normal1, normal2, np.zeros_like(normal1)])
        distlist = [_v_norm(bezier_points(ctrl, u)) for u in uextreme]
        if len(distlist) == 0:
            scale = 0.0
        elif len(distlist) == 1:
            scale = distlist[0]
        else:
            scale = sum(distlist) - 2 * min(distlist)
        ldesired = sz / scale if scale > 1e-12 else float("inf")
        ln = min(lmax, ldesired)
        out.append(first)
        out.append(first + tangent1 * ln)
        out.append(second + tangent2 * ln)
    out.append(path[lastpt % len(path)])
    return np.asarray(out, dtype=float)


def circle_circle_tangents(r1: float, cp1: ArrayLike, r2: float, cp2: ArrayLike) -> NDArray[np.float64]:
    """Tangent lines between two circles, each returned as a [point_on_circle1,
    point_on_circle2] pair -- same construction and ORDERING as bosl2's port (rabbit_clip()
    indexes [0][1], so the ordering matters): 2 external tangents, then 2 internal ones if
    the circles don't overlap."""
    cp1 = np.asarray(cp1, dtype=float)
    cp2 = np.asarray(cp2, dtype=float)
    dist = float(np.linalg.norm(cp2 - cp1))
    r_vals = [(r2 - r1) / dist, (r2 - r1) / dist, (-r2 - r1) / dist, (-r2 - r1) / dist]
    k_vals = [-1, 1, -1, 1]
    ext = [1, 1, -1, -1]
    if 1 - r_vals[2] ** 2 >= 0:
        n = 4
    elif 1 - r_vals[0] ** 2 >= 0:
        n = 2
    else:
        n = 0
    u = _v_unit(_v_sub(cp2, cp1))
    result = []
    for i in range(n):
        r = r_vals[i]
        s = math.sqrt(max(0.0, 1 - r * r))
        k = k_vals[i]
        coef = np.asarray([r * u[0] - k * s * u[1], k * s * u[0] + r * u[1]])
        p1 = cp1 - r1 * coef
        p2 = cp2 - ext[i] * r2 * coef
        if not np.array_equal(p1, p2):
            result.append([p1, p2])
    return np.asarray(result, dtype=float)


def offset_polyline(path: ArrayLike, d: float) -> NDArray[np.float64]:
    """The input open polyline shifted `d` to the LEFT of its direction of travel, using
    per-vertex averaged normals -- exact for smooth densely-sampled curves (which is all
    rabbit_clip() feeds it; it is NOT a general polygon offset with joint handling)."""
    pts = as_points(path)
    tang = path_tangents(pts, closed=False, uniform=False)
    left = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
    return pts + left * d


# ---------------------------------------------------------------------------
# Section: Polygon-path utilities (pure-python ports of the bosl2 helpers the
# cap-box polygon machinery needs -- byte-for-byte the same geometry, minus numpy)
# ---------------------------------------------------------------------------


def path_length(path: ArrayLike, closed: bool = False) -> float:
    """Total arc length of an open (or closed) polyline."""
    pts = as_points(path)
    total = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
    if closed and len(pts) > 1:
        total += float(np.linalg.norm(pts[-1] - pts[0]))
    return total


def path_cut_points(path: ArrayLike, cutdist, closed: bool = False):
    """The point(s) at the given arc-length distance(s) from the start of `path`, each as
    [point, next_index] (point is an ndarray) -- same return shape (and increasing-distances
    requirement) as the bosl2 port's path_cut_points()."""
    path = as_points(path)
    if isinstance(cutdist, (int, float)):
        return path_cut_points(path, [cutdist], closed)[0]
    assert all(cutdist[i] < cutdist[i + 1] for i in range(len(cutdist) - 1)), "Cut distances must be an increasing list"

    def select(p, i):
        return p[i % len(p)]

    def cut_single(dist: float, ind: int, eps: float = 1e-7):
        while True:
            if ind == len(path) - (0 if closed else 1):
                assert dist < eps, "Path is too short for specified cut distance"
                return [np.array(select(path, ind)), ind + 1]
            d = float(np.linalg.norm(select(path, ind + 1) - path[ind]))
            if d > dist:
                return [_lerp_pt(path[ind], select(path, ind + 1), dist / d), ind + 1]
            dist -= d
            ind += 1

    result: list = []
    pind = 0
    dtotal = 0.0
    for dist in cutdist:
        lastpt = None if not result else result[-1][0]
        dpartial = 0.0 if not result else float(np.linalg.norm(select(path, pind) - lastpt))
        if dist < dpartial + dtotal:
            t = (dist - dtotal) / dpartial
            nextpoint = [_lerp_pt(lastpt, select(path, pind), t), pind]
        else:
            nextpoint = cut_single(dist - dtotal - dpartial, pind)
        result.append(nextpoint)
        dtotal = dist
        pind = nextpoint[1]
    return result


def path_normals(path: ArrayLike, closed: bool = False) -> NDArray[np.float64]:
    """The 2-D normal (to the RIGHT of travel, matching the bosl2 port) at each path point."""
    tangents = path_tangents(path, closed=closed)
    return np.stack([tangents[:, 1], -tangents[:, 0]], axis=1)


def _frag_count(r: float, fn: float | None = None, fa: float | None = None, fs: float | None = None) -> int:
    """Number of segments approximating a circle of radius `r` (OpenSCAD's $fn/$fa/$fs rules)."""
    if fn is not None and fn >= 3:
        return int(math.floor(fn))
    fa = fa if fa else 12.0
    fs = fs if fs else 2.0
    return max(5, int(math.ceil(min(360.0 / fa, (2 * math.pi * abs(r)) / fs))))


def _vector_angle3(p0, p1, p2) -> float:
    v1 = _v_sub(p0, p1)
    v2 = _v_sub(p2, p1)
    cosang = max(-1.0, min(1.0, _v_dot(v1, v2) / (_v_norm(v1) * _v_norm(v2))))
    return math.degrees(math.acos(cosang))


def _circlecorner(p0, p1, p2, d: float, r: float, fn=None) -> list:
    prev = _v_unit(_v_sub(p0, p1))
    nxt = _v_unit(_v_sub(p2, p1))
    angle = _vector_angle3(p0, p1, p2) / 2
    start = _v_add(p1, _v_scale(prev, d))
    end = _v_add(p1, _v_scale(nxt, d))
    if abs(angle - 90) < 1e-9:
        return [start, end]
    bis = _v_unit(_v_add(prev, nxt))
    center = _v_add(p1, _v_scale(bis, r / math.sin(math.radians(angle))))
    n = max(3, math.ceil((90 - angle) / 180 * _frag_count(r, fn)))
    a0 = math.degrees(math.atan2(start[1] - center[1], start[0] - center[0]))
    a1 = math.degrees(math.atan2(end[1] - center[1], end[0] - center[0]))
    delta = (a1 - a0 + 180) % 360 - 180
    if n <= 1:
        return [start]
    return [
        [
            center[0] + r * math.cos(math.radians(a0 + i * delta / (n - 1))),
            center[1] + r * math.sin(math.radians(a0 + i * delta / (n - 1))),
        ]
        for i in range(n)
    ]


def round_corners(path: ArrayLike, radius=None, r=None, closed: bool = True, fn: float | None = None) -> NDArray[np.float64]:
    """Round every corner of a 2-D path to the given radius, inserting a tangent arc at each
    vertex -- the bosl2 port's round_corners() (radius method), pure python."""
    path = as_points(path)
    n = len(path)
    assert n > 2, f"Path has length {n}. Length must be 3 or more."
    size = radius if radius is not None else r
    assert size is not None, "Must specify radius"
    parm = list(size) if isinstance(size, (list, tuple)) else [size] * n

    dk = []
    for i in range(n):
        if (not closed and (i == 0 or i == n - 1)) or parm[i] == 0:
            dk.append([0.0, 0.0])
            continue
        p0, p1, p2 = path[(i - 1) % n], path[i], path[(i + 1) % n]
        angle = _vector_angle3(p0, p1, p2) / 2
        assert angle > 1e-9, f"Path turns back on itself at index {i} with nonzero rounding"
        dk.append([parm[i] / math.tan(math.radians(angle)), parm[i]])

    out: list = []
    for i in range(n):
        if dk[i][0] == 0:
            out.append(path[i])
            continue
        p0, p1, p2 = path[(i - 1) % n], path[i], path[(i + 1) % n]
        out.extend(_circlecorner(p0, p1, p2, dk[i][0], dk[i][1], fn))
    # drop consecutive duplicates (arc endpoints can coincide with straight-segment ends)
    cleaned: list = []
    for q in out:
        if not cleaned or math.dist(cleaned[-1], q) > 1e-9:
            cleaned.append(q)
    if closed and len(cleaned) > 1 and math.dist(cleaned[0], cleaned[-1]) < 1e-9:
        cleaned.pop()
    return np.asarray(cleaned, dtype=float)
