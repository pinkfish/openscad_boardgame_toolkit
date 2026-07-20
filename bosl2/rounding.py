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

# LibFile: bosl2/rounding.py
#    Pure-Python port of the path-rounding core of BOSL2's rounding.scad: :func:`round_corners`
#    (round every corner of a path -- ``"circle"``, ``"smooth"`` or ``"chamfer"``, sized by
#    ``radius``/``cut``/``joint``/``width``) and :func:`smooth_path` (fit a continuous-curvature
#    bezier through a path). Both work on 2-D and 3-D paths and are exposed as methods on
#    :class:`~bosl2.paths.Path` and :class:`~bosl2.paths.Path3D`.
#
#    ``round_corners`` and ``smooth_path`` are pinned point-for-point to the real BOSL2 output in
#    tests/test_bosl2_reorient.py. The smooth/chamfer corners reuse the toolkit's
#    :class:`~bosl2.beziers.Bezier`; the circle corners reuse :func:`~bosl2.shapes2d.arc` (2-D) or a
#    slerp arc (3-D).
#
#    NOT ported (a large follow-up): ``path_join``, and the 3-D generators ``offset_stroke`` /
#    ``offset_sweep`` (+ the ``os_*`` profiles) / ``convex_offset_extrude`` / ``rounded_prism`` /
#    ``join_prism`` / ``prism_connector`` / ``attach_prism`` / ``bent_cutout_mask``.
#
# FileSummary: Path rounding: round_corners (circle/smooth/chamfer) and smooth_path.
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

from bosl2.comparisons import approx
from bosl2.vectors import unit

__all__ = ["round_corners", "smooth_path", "Roundable"]


# ---------------------------------------------------------------------------
# Section: corner builders
# ---------------------------------------------------------------------------


def _is_num(x) -> bool:
    return isinstance(x, (int, float, np.integer, np.floating)) and not isinstance(x, bool)


def _vector_angle3(a, b, c) -> float:
    """The angle in degrees at vertex *b* of the corner a-b-c (2-D or 3-D)."""
    va = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    vc = np.asarray(c, dtype=float) - np.asarray(b, dtype=float)
    cosv = float(np.dot(va, vc)) / (float(np.linalg.norm(va)) * float(np.linalg.norm(vc)))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosv))))


def _smooth_bez_fill(points, k):
    p0, p1, p2 = (np.asarray(p, dtype=float) for p in points)
    return [p0, p1 + (p0 - p1) * k, p1, p1 + (p2 - p1) * k, p2]


def _bezcorner(points, parm, _fn=0, _fs=2.0):
    """A continuous-curvature (bezier) corner (BOSL2 _bezcorner())."""
    from bosl2.beziers import Bezier

    if isinstance(parm, (list, tuple, np.ndarray)):
        d, k = float(parm[0]), float(parm[1])
        p1 = np.asarray(points[1], dtype=float)
        prev = unit(np.asarray(points[0], dtype=float) - p1)
        nxt = unit(np.asarray(points[2], dtype=float) - p1)
        ctrl = [p1 + d * prev, p1 + k * d * prev, p1, p1 + k * d * nxt, p1 + d * nxt]
    else:
        ctrl = _smooth_bez_fill(points, float(parm))
    bez = Bezier([[float(c) for c in p] for p in ctrl])
    n = max(3, _fn if _fn and _fn > 0 else math.ceil(bez.length() / _fs))
    return [[float(c) for c in p] for p in bez.curve(n, endpoint=True)]


def _chamfcorner(points, parm):
    """A straight chamfer across a corner (BOSL2 _chamfcorner())."""
    d = float(parm[0])
    p1 = np.asarray(points[1], dtype=float)
    prev = unit(np.asarray(points[0], dtype=float) - p1)
    nxt = unit(np.asarray(points[2], dtype=float) - p1)
    return [list(p1 + prev * d), list(p1 + nxt * d)]


def _arc3d(center, start, end, n):
    """*n* points along the short arc from *start* to *end* about *center* (slerp, any dimension)."""
    c = np.asarray(center, dtype=float)
    v0, v1 = np.asarray(start, dtype=float) - c, np.asarray(end, dtype=float) - c
    ang = math.acos(max(-1.0, min(1.0, float(np.dot(v0, v1)) / (np.linalg.norm(v0) * np.linalg.norm(v1)))))
    if ang < 1e-12:
        return [list(np.asarray(start, dtype=float)), list(np.asarray(end, dtype=float))]
    s = math.sin(ang)
    return [list(c + (math.sin((1 - t) * ang) * v0 + math.sin(t * ang) * v1) / s)
            for t in np.linspace(0, 1, n)]


def _circlecorner(points, parm, _fn=None, _fa=None, _fs=None):
    """A circular-arc corner (BOSL2 _circlecorner())."""
    from bosl2.shapes2d import arc, _frag_count

    angle = _vector_angle3(points[0], points[1], points[2]) / 2
    d, r = float(parm[0]), float(parm[1])
    p1 = np.asarray(points[1], dtype=float)
    prev = unit(np.asarray(points[0], dtype=float) - p1)
    nxt = unit(np.asarray(points[2], dtype=float) - p1)
    start, end = p1 + prev * d, p1 + nxt * d
    if approx(angle, 90):
        return [list(start), list(end)]
    center = r / math.sin(math.radians(angle)) * unit(prev + nxt) + p1
    n = max(3, math.ceil((90 - angle) / 180 * _frag_count(r, _fn, _fa, _fs)))
    if len(points[1]) == 2:
        return [[float(c) for c in p]
                for p in arc(n, cp=[float(center[0]), float(center[1])],
                             points=[[float(start[0]), float(start[1])], [float(end[0]), float(end[1])]])]
    return _arc3d(center, start, end, n)


# ---------------------------------------------------------------------------
# Section: round_corners
# ---------------------------------------------------------------------------


def round_corners(path, method="circle", radius=None, r=None, cut=None, joint=None, width=None,
                  k=None, closed=True, _fn=None, _fa=None, _fs=None):
    """Round every corner of *path* (BOSL2 round_corners()).

    *method* is ``"circle"`` (a constant-radius arc), ``"smooth"`` (a continuous-curvature bezier),
    or ``"chamfer"`` (a straight bevel). Size the roundover with exactly one of *radius*/*r* (circle
    only), *cut* (depth toward the corner), *joint* (distance back from the corner along each edge),
    or *width* (chamfer only) -- each a scalar or a per-corner list. *k* (smooth only, 0..1) tunes
    how tight the curvature match is. Works on 2-D and 3-D paths.

    Returns:
        A :class:`~bosl2.paths.Path` (2-D) or :class:`~bosl2.paths.Path3D` (3-D).

    Examples:
        A rounded, smoothed and chamfered square (three copies):

        .. pythonscad-example::

            sq = [[0, 0], [40, 0], [40, 40], [0, 40]]
            round_corners(sq, method="smooth", joint=10).polygon().linear_extrude(height=4).show()
    """
    from bosl2.paths import Path, Path3D

    assert method in ("circle", "smooth", "chamfer"), 'method must be "circle", "smooth" or "chamfer".'
    given = [(m, v) for m, v in (("radius", radius), ("radius", r), ("cut", cut),
                                 ("joint", joint), ("width", width)) if v is not None]
    assert len(given) == 1, "Must give exactly one of radius, r, cut, joint or width."
    measure, size = given[0]
    pts = [[float(c) for c in p] for p in path]
    n = len(pts)
    assert n > 2, f"Path has length {n}. Length must be 3 or more."
    assert method == "circle" or measure != "radius", 'radius is allowed only with method="circle".'
    assert method == "chamfer" or measure != "width", 'width is allowed only with method="chamfer".'

    if _is_num(size):
        parm = [float(size)] * n
    elif len(size) < n:
        parm = [0.0] + [float(v) for v in size] + [0.0]
    else:
        parm = [float(v) for v in size]
    if k is None:
        kv = [0.5] * n
    elif _is_num(k):
        assert method == "smooth", 'k is only allowed with method="smooth".'
        kv = [float(k)] * n
    else:
        assert method == "smooth", 'k is only allowed with method="smooth".'
        kv = ([0.0] + [float(v) for v in k] + [0.0]) if len(k) < n else [float(v) for v in k]
    assert all(v >= 0 for v in parm), f"{measure} must be nonnegative."
    assert all(0 <= v <= 1 for v in kv), "k must be in [0, 1]."

    # dk[i] = [joint distance, shape param] per corner (chamfer has just [distance])
    dk = []
    for i in range(n):
        p0, p1, p2 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        if (not closed and (i == 0 or i == n - 1)) or parm[i] == 0:
            dk.append([0.0])
            continue
        assert not (approx(p0, p1) or approx(p1, p2)), f"Repeated point in path at index {i} with nonzero rounding."
        angle = _vector_angle3(p0, p1, p2) / 2
        assert not approx(angle, 0), f"Path turns back on itself at index {i} with nonzero rounding."
        ar = math.radians(angle)
        if method == "chamfer":
            dk.append([parm[i] if measure == "joint" else
                       parm[i] / math.cos(ar) if measure == "cut" else
                       parm[i] / math.sin(ar) / 2])  # width
        elif method == "smooth":
            dk.append([parm[i], kv[i]] if measure == "joint" else
                      [8 * parm[i] / math.cos(ar) / (1 + 4 * kv[i]), kv[i]])  # cut
        elif measure == "radius":
            dk.append([parm[i] / math.tan(ar), parm[i]])
        elif measure == "joint":
            dk.append([parm[i], parm[i] * math.tan(ar)])
        else:  # circle + cut
            if approx(angle, 90):
                dk.append([math.inf])
            else:
                cr = parm[i] / (1 / math.sin(ar) - 1)
                dk.append([cr / math.tan(ar), cr])

    lengths = [float(np.linalg.norm(np.asarray(pts[i % n]) - np.asarray(pts[(i - 1) % n]))) for i in range(n + 1)]
    scale = []
    for i in range(n):
        if closed or (i != 0 and i != n - 1):
            a = lengths[i] / (dk[(i - 1) % n][0] + dk[i][0]) if (dk[(i - 1) % n][0] + dk[i][0]) else math.inf
            b = lengths[i + 1] / (dk[i][0] + dk[(i + 1) % n][0]) if (dk[i][0] + dk[(i + 1) % n][0]) else math.inf
            scale.append(min(a, b))
    assert not scale or min(scale) >= 1 - 1e-9, \
        "Roundovers are too big for the path (they overlap); reduce the sizes."

    out = []
    for i in range(n):
        corner = [pts[(i - 1) % n], pts[i], pts[(i + 1) % n]]
        if dk[i][0] == 0:
            out.append(pts[i])
        elif method == "smooth":
            out += _bezcorner(corner, dk[i], _fn=_fn or 0, _fs=_fs or 2.0)
        elif method == "chamfer":
            out += _chamfcorner(corner, dk[i])
        else:
            out += _circlecorner(corner, dk[i], _fn=_fn, _fa=_fa, _fs=_fs)

    result = _dedup(out)
    dim = len(result[0])
    return (Path3D if dim == 3 else Path)(result, closed=closed)


def _dedup(pts, eps=1e-9):
    out = []
    for p in pts:
        if not out or not approx(out[-1], p, eps):
            out.append([float(c) for c in p])
    if len(out) > 1 and approx(out[0], out[-1], eps):
        out.pop()
    return out


# ---------------------------------------------------------------------------
# Section: smooth_path
# ---------------------------------------------------------------------------


def smooth_path(path, tangents=None, size=None, relsize=None, splinesteps=10, uniform=False,
                closed=False):
    """Fit a smooth continuous-curvature curve through *path* (BOSL2 smooth_path(), method="edges").

    Runs a cubic bezier through every point of *path*, matching the path's tangents, and samples it
    with *splinesteps* points per segment. *size* / *relsize* bound how far the curve may bow away
    from the straight path (relsize is a fraction of each segment, default 0.1). The BOSL2
    ``method="corners"`` variant is not ported.

    Returns:
        A :class:`~bosl2.paths.Path` (2-D) or :class:`~bosl2.paths.Path3D` (3-D).

    Examples:
        A wiggly control path smoothed into a flowing curve:

        .. pythonscad-example::

            pts = [[0, 0], [10, 30], [30, -10], [50, 20], [70, 0]]
            smooth_path(pts, relsize=0.4).stroke(width=2).linear_extrude(height=3).show()
    """
    from bosl2.beziers import Bezier
    from bosl2.paths import Path, Path3D

    bez = Bezier.from_path(path, closed=closed, tangents=tangents, size=size, relsize=relsize,
                           uniform=uniform)
    smoothed = [[float(c) for c in p] for p in bez.path_curve(splinesteps=splinesteps)]
    if closed and len(smoothed) > 1 and approx(smoothed[0], smoothed[-1]):
        smoothed = smoothed[:-1]
    dim = len(smoothed[0])
    return (Path3D if dim == 3 else Path)(smoothed, closed=closed)


# ---------------------------------------------------------------------------
# Section: Roundable mixin
# ---------------------------------------------------------------------------


class Roundable:
    """Mixin adding the rounding.scad path operators as methods on :class:`~bosl2.paths.Path` and
    :class:`~bosl2.paths.Path3D`."""

    def round_corners(self, radius=None, r=None, method="circle", cut=None, joint=None, width=None,
                      k=None, closed=None, **kwargs):
        """Round every corner of this path (see :func:`round_corners`)."""
        return round_corners(self, method=method, radius=radius, r=r, cut=cut, joint=joint,
                             width=width, k=k, closed=self.closed if closed is None else closed, **kwargs)

    def smooth_path(self, tangents=None, size=None, relsize=None, splinesteps=10, uniform=False,
                    closed=None):
        """Fit a smooth continuous-curvature curve through this path (see :func:`smooth_path`)."""
        return smooth_path(self, tangents=tangents, size=size, relsize=relsize,
                           splinesteps=splinesteps, uniform=uniform,
                           closed=self.closed if closed is None else closed)
