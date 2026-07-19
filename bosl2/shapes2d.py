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

# LibFile: bosl2/shapes2d.py
#    Pure-Python port of BOSL2's shapes2d.scad, laid out in the same
#    order/sections as the original .scad file so the two are easy to
#    cross-reference. No osuse()/BOSL2 runtime dependency at all -- every
#    shape's outline is computed here in plain Python and then built with
#    direct openscad primitive calls (square()/circle()/polygon()/text()/
#    hull()/.offset()), rather than delegating to BOSL2. Every function
#    always returns a real PyOpenSCAD 2D solid (never a raw path).
#
#    Anywhere BOSL2 lets you tune arc smoothness with the special variables
#    $fn/$fa/$fs, this module exposes the same knob as an explicit `_fn`/
#    `_fa`/`_fs` keyword argument (matching this project's existing calling
#    convention, e.g. `circle(r=5, _fn=64)`), and uses it when computing the
#    point count for any rounded/curved portion of the shape.
#
# FileSummary: 2D primitives, polygons, curves, text and rounding (BOSL2 shapes2d.scad).
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math
import random

import numpy as np

# Imported explicitly (rather than `from pythonscad import *`) so editors/type-checkers
# can resolve these names -- this module immediately shadows all five with its own
# BOSL2-style square()/circle()/polygon()/text()/hull() below, so the plain builtins are
# captured under private names first.
from pythonscad import square as _osquare, circle as _ocircle, polygon as _opolygon, text as _otext, hull as _ohull
from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from .constants import *
from bosl2.vectors import unit
from bosl2.geometry import is_collinear
from bosl2.paths import Path


# ---------------------------------------------------------------------------
# Internal helpers (not part of BOSL2's public API)
# ---------------------------------------------------------------------------


def _frag_count(r: float, _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> int:
    """Number of polygon segments to approximate a circle of radius *r*, mirroring OpenSCAD's $fn/$fa/$fs rules."""
    if _fn is not None and _fn >= 3:
        return int(math.floor(_fn))
    fa = _fa if _fa else 12.0
    fs = _fs if _fs else 2.0
    return max(5, int(math.ceil(min(360.0 / fa, (2 * math.pi * abs(r)) / fs))))


def _quant(x: float, y: float) -> float:
    return math.ceil(x / y) * y


def _polar_to_xy(r: float, a: float) -> list[float]:
    rad = math.radians(a)
    return [r * math.cos(rad), r * math.sin(rad)]


def _rotate2d(p: Sequence[float], deg: float) -> list[float]:
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    return [p[0] * c - p[1] * s, p[0] * s + p[1] * c]


def _circle_pts(r: float, n: int, start: float = 0.0) -> list[list[float]]:
    return [_polar_to_xy(r, start + 360.0 * i / n) for i in range(n)]


def _arc_points(n: int, r: float, start: float, angle: float, cp: Sequence[float] = (0.0, 0.0), endpoint: bool = True) -> list[list[float]]:
    """*n* points along an arc of radius *r* centered at *cp*, from angle *start* sweeping *angle* degrees."""
    if not endpoint:
        return _arc_points(n + 1, r, start, angle, cp, True)[:-1]
    if n <= 1:
        return [[r * math.cos(math.radians(start)) + cp[0], r * math.sin(math.radians(start)) + cp[1]]]
    pts = []
    for i in range(n):
        theta = math.radians(start + i * angle / (n - 1))
        pts.append([r * math.cos(theta) + cp[0], r * math.sin(theta) + cp[1]])
    return pts


def _arc_between_points(cp: Sequence[float], p_start: Sequence[float], p_end: Sequence[float], radius: float, endpoint: bool = True, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
    """Arc around *cp* from *p_start* to *p_end*, sweeping the shorter way around."""
    a0 = math.degrees(math.atan2(p_start[1] - cp[1], p_start[0] - cp[0]))
    a1 = math.degrees(math.atan2(p_end[1] - cp[1], p_end[0] - cp[0]))
    delta = (a1 - a0 + 180) % 360 - 180
    n = max(3, math.ceil(_frag_count(radius, _fn, _fa, _fs) * abs(delta) / 360))
    return _arc_points(n, radius, a0, delta, cp, endpoint=endpoint)


def _arc_through_3(cp: Sequence[float], radius: float, p_start: Sequence[float], p_mid: Sequence[float], p_end: Sequence[float], endpoint: bool = True, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
    """Arc around *cp* from *p_start* to *p_end*, sweeping through *p_mid* (may be the long way around)."""
    a0 = math.degrees(math.atan2(p_start[1] - cp[1], p_start[0] - cp[0]))
    am = math.degrees(math.atan2(p_mid[1] - cp[1], p_mid[0] - cp[0]))
    a1 = math.degrees(math.atan2(p_end[1] - cp[1], p_end[0] - cp[0]))
    d_mid = (am - a0) % 360
    d_end = (a1 - a0) % 360
    delta = d_end if d_mid <= d_end else d_end - 360
    n = max(3, math.ceil(_frag_count(radius, _fn, _fa, _fs) * abs(delta) / 360))
    return _arc_points(n, radius, a0, delta, cp, endpoint=endpoint)


@overload
def _pick_radius(
    r1: float | None = None, d1: float | None = None, r2: float | None = None, d2: float | None = None,
    r: float | None = None, d: float | None = None, *, dflt: float,
) -> float: ...
@overload
def _pick_radius(
    r1: float | None = None, d1: float | None = None, r2: float | None = None, d2: float | None = None,
    r: float | None = None, d: float | None = None, dflt: None = None,
) -> float | None: ...
def _pick_radius(r1=None, d1=None, r2=None, d2=None, r=None, d=None, dflt=None):
    """Mirror BOSL2's get_radius(): (r1,d1) > (r2,d2) > (r,d) > dflt."""
    if r1 is not None:
        return r1
    if d1 is not None:
        return d1 / 2
    if r2 is not None:
        return r2
    if d2 is not None:
        return d2 / 2
    if r is not None:
        return r
    if d is not None:
        return d / 2
    return dflt


def _circle_from_3pts(points: Sequence[Sequence[float]]) -> tuple[list[float], float]:
    (x1, y1), (x2, y2), (x3, y3) = points
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    return [ux, uy], math.hypot(x1 - ux, y1 - uy)


def _circle_from_corner(corner: Sequence[Sequence[float]], r: float) -> list[float]:
    p0, p1, p2 = corner
    v1 = unit([p0[0] - p1[0], p0[1] - p1[1]])
    v2 = unit([p2[0] - p1[0], p2[1] - p1[1]])
    bis = unit([v1[0] + v2[0], v1[1] + v2[1]])
    half_ang = math.acos(max(-1.0, min(1.0, v1[0] * bis[0] + v1[1] * bis[1])))
    dist = r / math.sin(half_ang)
    return [p1[0] + bis[0] * dist, p1[1] + bis[1] * dist]


def _circle_circle_intersection(r1: float, c1: Sequence[float], r2: float, c2: Sequence[float]) -> list[list[float]]:
    d = math.dist(c1, c2)
    if d == 0 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h_sq = r1**2 - a**2
    if h_sq < 0:
        return []
    h = math.sqrt(h_sq)
    xm = c1[0] + a * (c2[0] - c1[0]) / d
    ym = c1[1] + a * (c2[1] - c1[1]) / d
    dx = h * (c2[1] - c1[1]) / d
    dy = h * (c2[0] - c1[0]) / d
    return [[xm + dx, ym - dy], [xm - dx, ym + dy]]


def _adj_ang_to_hyp(adj: float, ang: float) -> float:
    return adj / math.cos(math.radians(ang))


def _adj_ang_to_opp(adj: float, ang: float) -> float:
    return adj * math.tan(math.radians(ang))


def _opp_ang_to_adj(opp: float, ang: float) -> float:
    return opp / math.tan(math.radians(ang))


def _v_theta(v: Sequence[float]) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _det2(a: Sequence[float], b: Sequence[float]) -> float:
    """The 2-D cross product a x b -- sign gives the turn direction (z of the 3-D cross)."""
    return float(a[0] * b[1] - a[1] * b[0])


def _sign(x: float) -> int:
    x = float(x)
    return (x > 0) - (x < 0)


def _vector_angle(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    """The angle in degrees at vertex *b* of the corner a-b-c."""
    va = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    vc = np.asarray(c, dtype=float) - np.asarray(b, dtype=float)
    cosv = float(np.dot(va, vc)) / (float(np.linalg.norm(va)) * float(np.linalg.norm(vc)))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosv))))


def _dir2(anchor: Sequence[float]) -> list[float]:
    a = list(anchor) + [0, 0, 0]
    return [a[0], a[1] + a[2]]


def _anchor_offset_box(size: Sequence[float], anchor: Sequence[float]) -> list[float]:
    d = _dir2(anchor)
    return [-d[0] * size[0] / 2, -d[1] * size[1] / 2]


def _anchor_offset_hull(points: Sequence[Sequence[float]], anchor: Sequence[float]) -> list[float]:
    d = _dir2(anchor)
    if d[0] == 0 and d[1] == 0:
        return [0.0, 0.0]
    best = max(points, key=lambda p: p[0] * d[0] + p[1] * d[1])
    return [-best[0], -best[1]]


def _finish(shape: PyOpenSCAD, offset: Sequence[float], spin: float) -> PyOpenSCAD:
    if offset[0] != 0 or offset[1] != 0:
        shape = shape.translate(offset)
    if spin:
        # Native 2-D rotate needs the 3-vector form; a bare scalar is rejected.
        shape = shape.rotate([0, 0, spin])
    return shape


# ---------------------------------------------------------------------------
# Section: 2D Primitives
# ---------------------------------------------------------------------------


def square(
    size: float | Sequence[float] = 1,
    center: bool | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float | None = None,
) -> PyOpenSCAD:
    """A rectangle, built with the builtin square(), with BOSL2-style anchor/spin support.

    Args:
        size:   size of the square; a scalar uses the same size for X and Y
        center: if given, overrides anchor (True -> CENTER, False -> FRONT+LEFT)
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
    """
    sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(v) for v in size]
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else [-1, -1, 0]
    shape = _osquare(sz, center=True)
    offset = _anchor_offset_box(sz, use_anchor)
    return _finish(shape, offset, spin or 0)


def _rect_path(
    size: Sequence[float],
    rounding: float | Sequence[float] = 0,
    chamfer: float | Sequence[float] = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> list[list[float]]:
    sx, sy = size
    rounding_l = [float(rounding)] * 4 if isinstance(rounding, (int, float)) else [float(v) for v in rounding]
    chamfer_l = [float(chamfer)] * 4 if isinstance(chamfer, (int, float)) else [float(v) for v in chamfer]
    if all(v == 0 for v in rounding_l) and all(v == 0 for v in chamfer_l):
        return [[sx / 2, -sy / 2], [-sx / 2, -sy / 2], [-sx / 2, sy / 2], [sx / 2, sy / 2]]
    quadorder = [3, 2, 1, 0]
    quadpos = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
    eps = 1e-9
    insets = [chamfer_l[i] if abs(chamfer_l[i]) >= eps else (rounding_l[i] if abs(rounding_l[i]) >= eps else 0) for i in range(4)]
    insets_x = max(insets[0] + insets[1], insets[2] + insets[3])
    insets_y = max(insets[0] + insets[3], insets[1] + insets[2])
    assert insets_x <= sx, "Requested roundings and/or chamfers exceed the rect width."
    assert insets_y <= sy, "Requested roundings and/or chamfers exceed the rect height."
    path = []
    for i in range(4):
        quad = quadorder[i]
        qinset = insets[quad]
        qpos = quadpos[quad]
        qchamf = chamfer_l[quad]
        qround = rounding_l[quad]
        cverts = int(_quant(_frag_count(abs(qinset), _fn, _fa, _fs), 4) / 4) if abs(qinset) >= eps else 0
        step = 90.0 / cverts if cverts else 0.0
        cp = [(sx / 2 - qinset) * qpos[0], (sy / 2 - abs(qinset)) * qpos[1]]
        if abs(qchamf) >= eps:
            qpts = [[0, abs(qinset)], [qinset, 0]]
        elif abs(qround) >= eps:
            sign = 1 if qinset >= 0 else -1
            qpts = []
            for j in range(cverts + 1):
                a = 90 - j * step
                p = _polar_to_xy(abs(qinset), a)
                qpts.append([p[0] * sign, p[1]])
        else:
            qpts = [[0, 0]]
        qfpts = [[p[0] * qpos[0], p[1] * qpos[1]] for p in qpts]
        qrpts = list(reversed(qfpts)) if qpos[0] * qpos[1] < 0 else qfpts
        for p in qrpts:
            path.append([p[0] + cp[0], p[1] + cp[1]])
    return path


def rect(
    size: float | Sequence[float] = 1,
    rounding: float | Sequence[float] = 0,
    atype: str = "box",
    chamfer: float | Sequence[float] = 0,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A rectangle with optional rounded or chamfered corners.

    Note: negative rounding/chamfer (BOSL2's "external roundover spikes") is not supported here.

    Args:
        size:     size of the rectangle; a scalar uses the same size for X and Y
        rounding: corner rounding radius, or per-corner list [X+Y+,X-Y+,X-Y-,X+Y-] (default 0)
        atype:    anchor type, "box" (bounding box) or "perim" (rounded/chamfered perimeter) (default "box")
        chamfer:  corner chamfer size, or per-corner list [X+Y+,X-Y+,X-Y-,X+Y-] (default 0)
        anchor:   anchor point (default CENTER)
        spin:     Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides for rounded corners
    """
    sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(v) for v in size]
    path = _rect_path(sz, rounding=rounding, chamfer=chamfer, _fn=_fn, _fa=_fa, _fs=_fs)
    shape = _opolygon(path)
    complex_shape = (rounding != 0 if isinstance(rounding, (int, float)) else any(rounding)) or (
        chamfer != 0 if isinstance(chamfer, (int, float)) else any(chamfer)
    )
    if complex_shape and atype == "perim":
        offset = _anchor_offset_hull(path, anchor)
    else:
        offset = _anchor_offset_box(sz, anchor)
    return _finish(shape, offset, spin)


def rect_path(
    size: float | Sequence[float] = 1,
    rounding: float | Sequence[float] = 0,
    chamfer: float | Sequence[float] = 0,
    anchor: Sequence[float] = CENTER,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> list[list[float]]:
    """The *points* of a (optionally rounded/chamfered) rectangle -- BOSL2's ``rect()`` in its
    function form, as opposed to :func:`rect` which returns native 2-D geometry.

    Use this when the rectangle is an input to further path math (e.g. a profile fed to
    :func:`base_bgtk.PolygonPrism`), not something to draw.

    Usage::

        rect_path([20, 4], rounding=[-3, -3, 0, 0], anchor=TOP + LEFT)

    Args:
        size:     [x, y] size (or a single number for a square)
        rounding: corner radius; a single value or per-corner list. Negative = concave.
        chamfer:  corner chamfer; a single value or per-corner list
        anchor:   BOSL2 anchor the path is translated onto (default CENTER)

    Note:
        For small radii this can emit one more point per corner than the real BOSL2 does
        (BOSL2 rounds the corner-arc segment count, this rounds up); the arc geometry is
        identical, only the sampling differs.
    """
    sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(v) for v in size]
    path = _rect_path(sz, rounding=rounding, chamfer=chamfer, _fn=_fn, _fa=_fa, _fs=_fs)
    offset = _anchor_offset_box(sz, anchor)
    return [[float(p[0]) + offset[0], float(p[1]) + offset[1]] for p in path]


def arc(
    n: int | None = None,
    r: float | None = None,
    angle: float | Sequence[float] | None = None,
    d: float | None = None,
    cp: Sequence[float] | None = None,
    points: Sequence[Sequence[float]] | None = None,
    corner: Sequence[Sequence[float]] | None = None,
    width: float | None = None,
    thickness: float | None = None,
    start: float | None = None,
    wedge: bool = False,
    long: bool = False,
    cw: bool = False,
    ccw: bool = False,
    endpoint: bool = True,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Path:
    """A 2-D arc, returned as a :class:`~bosl2.paths.Path` of points (BOSL2's ``arc()``).

    All of BOSL2's 2-D arc specifications are supported (3-D arcs, which project onto a plane,
    are not):

    * ``arc(r=, angle=, [start=], [cp=])`` -- radius *r* about *cp*, sweeping *angle* degrees from
      *start* (or ``angle=[start, end]`` for an explicit range).
    * ``arc(width=, thickness=)`` -- a circular segment starting and ending on the X axis.
    * ``arc(cp=, points=[P0, P1])`` -- around *cp* from ``P0`` toward the direction of ``P1``; the
      short way by default, or the long/``cw``/``ccw`` way.
    * ``arc(points=[P0, P1, P2])`` -- through three points, from ``P0`` via ``P1`` to ``P2``.
    * ``arc(corner=[P0, P1, P2], r=)`` -- the fillet arc of radius *r* tangent to both legs of the
      corner ``P0-P1-P2``.

    Set ``wedge=True`` to prepend the centre point, giving a closed pie/sector path. When *n* is
    omitted the point count follows OpenSCAD's $fn/$fa/$fs rules, matching BOSL2.

    Args:
        n:         number of points (default: from $fn/$fa/$fs)
        r/d:       radius / diameter of the arc
        angle:     degrees to sweep from *start*, or ``[start, end]``
        cp:        centre point (default ``[0, 0]``)
        points:    two points (with *cp*) or three points the arc passes through
        corner:    three points; the arc is the *r*-radius fillet tangent to both legs
        width:     chord width for the width/thickness form
        thickness: height of the circular segment for the width/thickness form
        start:     starting angle in degrees (default 0)
        wedge:     prepend the centre point, producing a closed sector (default False)
        long/cw/ccw: for the two-point form, take the long way / a given handedness
        endpoint:  include the final point (default True)

    Returns:
        A :class:`~bosl2.paths.Path` (closed when *wedge* is set).
    """
    # -- width + thickness: a circular segment through 3 points on/above the X axis ----------
    if width is not None and thickness is not None:
        assert not any(v is not None for v in (r, cp, points, angle, start)), "conflicting arc() params"
        return arc(n=n, points=[[width / 2, 0], [0, thickness], [-width / 2, 0]],
                   wedge=wedge, endpoint=endpoint, _fn=_fn, _fa=_fa, _fs=_fs)

    # -- corner: the fillet arc tangent to both legs of a 3-point corner ---------------------
    if corner is not None:
        assert len(corner) == 3, "corner= needs exactly 3 points"
        assert not is_collinear(corner[0], corner[1], corner[2]), "Collinear corner does not define an arc"
        rad = _pick_radius(r=r, d=d)
        assert rad is not None and rad > 0, "arc(corner=) needs r= or d="
        p0, p1, p2 = (np.asarray(p, dtype=float) for p in corner)
        v1, v2 = unit(p0 - p1), unit(p2 - p1)
        half = math.acos(max(-1.0, min(1.0, float(np.dot(v1, v2))))) / 2
        d_tan = rad / math.tan(half)
        cp2 = _circle_from_corner(corner, rad)
        tp1, tp2 = p1 + v1 * d_tan, p1 + v2 * d_tan
        forward = _det2(p1 - p0, p2 - p1) > 0
        c0, c1 = (tp1, tp2) if forward else (tp2, tp1)
        ts = math.degrees(math.atan2(c0[1] - cp2[1], c0[0] - cp2[0]))
        te = math.degrees(math.atan2(c1[1] - cp2[1], c1[0] - cp2[0]))
        sweep = (te - ts) % 360
        rng = [ts, ts + sweep] if forward else [ts + sweep, ts]
        return arc(n=n, cp=cp2, r=rad, angle=rng, wedge=wedge, endpoint=endpoint, _fn=_fn, _fa=_fa, _fs=_fs)

    # -- points forms ------------------------------------------------------------------------
    if points is not None:
        pts = [[float(p[0]), float(p[1])] for p in points]
        assert all(len(p) == 2 for p in points), "arc() port handles 2-D points only"
        if len(pts) == 2:
            assert cp is not None, "cp= is required when points has length 2"
            assert pts[0] != pts[1], "arc endpoints are equal"
            centre = [float(cp[0]), float(cp[1])]
            v1 = np.asarray(pts[0]) - np.asarray(centre)
            v2 = np.asarray(pts[1]) - np.asarray(centre)
            ang = _vector_angle(pts[0], centre, pts[1])
            prelim = _sign(_det2(v1, v2))
            if prelim != 0:
                direction = prelim
            else:
                assert cw or ccw, "Collinear inputs don't define a unique arc"
                direction = 1
            rad = float(np.hypot(v1[0], v1[1]))
            if long or (ccw and direction < 0) or (cw and direction > 0):
                final_angle = -direction * (360 - ang)
            else:
                final_angle = direction * ang
            sa = math.degrees(math.atan2(v1[1], v1[0]))
            return arc(n=n, cp=centre, r=rad, start=sa, angle=final_angle, wedge=wedge,
                       endpoint=endpoint, _fn=_fn, _fa=_fa, _fs=_fs)
        assert len(pts) == 3, f"arc(points=) needs 2 or 3 points, got {len(pts)}"
        assert not is_collinear(pts[0], pts[1], pts[2]), "Collinear inputs do not define an arc"
        centre, radius = _circle_from_3pts(pts)
        a0 = math.degrees(math.atan2(pts[0][1] - centre[1], pts[0][0] - centre[0]))
        am = math.degrees(math.atan2(pts[1][1] - centre[1], pts[1][0] - centre[0]))
        a1 = math.degrees(math.atan2(pts[2][1] - centre[1], pts[2][0] - centre[0]))
        d_mid = (am - a0) % 360
        d_end = (a1 - a0) % 360
        delta = d_end if d_mid <= d_end else d_end - 360
        count = n if n is not None else max(3, math.ceil(_frag_count(radius, _fn, _fa, _fs) * abs(delta) / 360))
        out = _arc_points(count, radius, a0, delta, centre, endpoint=endpoint)
        if wedge:
            out = [list(centre)] + out
        return Path(out, closed=wedge)

    # -- radius + angle (with optional [start, end] range) -----------------------------------
    radius = _pick_radius(r=r, d=d)
    assert radius is not None, "arc() needs r=/d=, points=, corner=, or width=/thickness="
    if isinstance(angle, (list, tuple, np.ndarray)):
        assert start is None, "start= is not allowed with angle=[start, end]"
        calc_start = float(angle[0])
        calc_angle = float(angle[1]) - float(angle[0])
    else:
        calc_angle = 360.0 if angle is None else float(angle)
        calc_start = 0.0 if start is None else float(start)
    calc_cp = (0.0, 0.0) if cp is None else cp
    count = n if n is not None else math.ceil(_frag_count(radius, _fn, _fa, _fs) * abs(calc_angle) / 360) + 1
    out = _arc_points(count, radius, calc_start, calc_angle, calc_cp, endpoint=endpoint)
    if wedge:
        out = [list(calc_cp)] + out
    return Path(out, closed=wedge)


def circle(
    r: float | None = None,
    d: float | None = None,
    points: Sequence[Sequence[float]] | None = None,
    corner: Sequence[Sequence[float]] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A circle, built with the builtin circle(), by radius/diameter, or fit to points.

    If `corner` is given three 2-D points, the circle is centered to be tangent to both
    segments of that path, on the inside corner. If `points` is given three 2-D points,
    the circle is centered and sized to pass through all three points. Anchor/spin are
    ignored for the `corner`/`points` forms, matching BOSL2.

    Args:
        r:      radius of the circle
        d:      diameter of the circle
        points: three 2-D points the circle should pass through
        corner: three 2-D points defining a path the circle should be tangent to
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    if points is not None:
        center, rad = _circle_from_3pts(points)
        return _ocircle(r=rad, fn=_fn, fa=_fa, fs=_fs).translate(center)
    if corner is not None:
        rad = r if r is not None else (d / 2 if d is not None else 1)
        center = _circle_from_corner(corner, rad)
        return _ocircle(r=rad, fn=_fn, fa=_fa, fs=_fs).translate(center)
    rad = r if r is not None else (d / 2 if d is not None else 1)
    shape = _ocircle(r=rad, fn=_fn, fa=_fa, fs=_fs)
    n = _frag_count(rad, _fn, _fa, _fs)
    offset = _anchor_offset_hull(_circle_pts(rad, n), anchor)
    return _finish(shape, offset, spin)


def ellipse(
    r: float | Sequence[float] | None = None,
    d: float | Sequence[float] | None = None,
    realign: bool = False,
    circum: bool = False,
    uniform: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """An ellipse (approximated as a polygon), built directly with polygon().

    Note: `uniform` (equal-length approximating segments) is not implemented; segments are
    evenly spaced by angle instead.

    Args:
        r:       radius of the circle, or pair of semi-axes of the ellipse
        d:       diameter of the circle, or pair giving the full X/Y axis lengths
        realign: shift the first polygon point off the X+ axis (default False)
        circum:  circumscribe rather than inscribe the ideal ellipse (default False)
        anchor:  anchor point (default CENTER)
        spin:    Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    if r is not None:
        rad = [float(r), float(r)] if isinstance(r, (int, float)) else [float(v) for v in r]
    elif d is not None:
        dd = [float(d), float(d)] if isinstance(d, (int, float)) else [float(v) for v in d]
        rad = [dd[0] / 2, dd[1] / 2]
    else:
        rad = [1.0, 1.0]
    n = _frag_count(max(rad), _fn, _fa, _fs)
    scale = 1.0 / math.cos(math.pi / n) if circum else 1.0
    start = (360.0 / n) / 2 if realign else 0.0
    path = [[rad[0] * scale * math.cos(math.radians(start + 360.0 * i / n)), rad[1] * scale * math.sin(math.radians(start + 360.0 * i / n))] for i in range(n)]
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


# ---------------------------------------------------------------------------
# Section: Polygons
# ---------------------------------------------------------------------------


def _regular_ngon_path(
    n: int,
    rad: float,
    rounding: float = 0,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_side: Sequence[float] | None = None,
    _fn=None,
    _fa=None,
    _fs=None,
) -> list[list[float]]:
    if not rounding:
        path = _circle_pts(rad, n)
    else:
        inset = rounding / math.sin(math.radians((180 - 360.0 / n) / 2))
        steps = max(1, int(_frag_count(rad, _fn, _fa, _fs) // n))
        path2 = []
        for i in range(n):
            a = 360 - i * 360.0 / n
            p = _polar_to_xy(rad - inset, a)
            path2.extend(_arc_points(steps, rounding, a + 180.0 / n, -360.0 / n, p))
        maxx_idx = max(range(len(path2)), key=lambda k: path2[k][0])
        path = path2[maxx_idx:] + path2[:maxx_idx]
    extra_rot = 0.0
    if align_tip is not None:
        extra_rot += math.degrees(math.atan2(align_tip[1], align_tip[0]))
    elif align_side is not None:
        extra_rot += math.degrees(math.atan2(align_side[1], align_side[0])) + 180.0 / n
    if realign:
        extra_rot -= 180.0 / n
    if extra_rot:
        path = [_rotate2d(p, extra_rot) for p in path]
    return path


def regular_ngon(
    n: int = 6,
    r: float | None = None,
    d: float | None = None,
    outer_r: float | None = None,
    od: float | None = None,
    ir: float | None = None,
    id: float | None = None,
    side: float | None = None,
    rounding: float = 0,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_side: Sequence[float] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A regular N-gon (equilateral, equiangular polygon), built directly with polygon().

    Note: BOSL2's outer-radius parameter is named `or`, which collides with the Python
    keyword `or`; it is exposed here as `outer_r` instead.

    Args:
        n:          number of sides (default 6)
        r/outer_r:  outside radius, at the points (BOSL2 `or`)
        d/od:       outside diameter, at the points
        ir:         inside radius, at the center of the sides
        id:         inside diameter, at the center of the sides
        side:       length of each side
        rounding:   rounding radius for the tips of the polygon (default 0)
        realign:    put the midpoint of the last edge (instead of vertex 0) on the X+ axis (default False)
        align_tip:  rotate so the first vertex points in this 2-D direction (applied before spin)
        align_side: rotate so the normal of side 0 points in this 2-D direction (applied before spin)
        anchor:     anchor point (default CENTER)
        spin:       Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides for rounded tips
    """
    assert n >= 3
    sc = 1 / math.cos(math.radians(180.0 / n))
    ir_s = ir * sc if ir is not None else None
    id_s = id * sc if id is not None else None
    side_s = side / 2 / math.sin(math.radians(180.0 / n)) if side is not None else None
    rad = _pick_radius(r1=ir_s, d1=id_s, r2=outer_r, d2=od, r=r, d=d, dflt=side_s)
    if rad is None:
        raise ValueError("regular_ngon(): need to specify one of r, d, outer_r, od, ir, id, side.")
    path = _regular_ngon_path(n, rad, rounding=rounding, realign=realign, align_tip=align_tip, align_side=align_side, _fn=_fn, _fa=_fa, _fs=_fs)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def pentagon(
    r: float | None = None,
    d: float | None = None,
    outer_r: float | None = None,
    od: float | None = None,
    ir: float | None = None,
    id: float | None = None,
    side: float | None = None,
    rounding: float = 0,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_side: Sequence[float] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A regular pentagon. See regular_ngon() for argument details."""
    return regular_ngon(
        n=5, r=r, d=d, outer_r=outer_r, od=od, ir=ir, id=id, side=side, rounding=rounding,
        realign=realign, align_tip=align_tip, align_side=align_side, anchor=anchor, spin=spin,
        _fn=_fn, _fa=_fa, _fs=_fs,
    )


def hexagon(
    r: float | None = None,
    d: float | None = None,
    outer_r: float | None = None,
    od: float | None = None,
    ir: float | None = None,
    id: float | None = None,
    side: float | None = None,
    rounding: float = 0,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_side: Sequence[float] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A regular hexagon. See regular_ngon() for argument details."""
    return regular_ngon(
        n=6, r=r, d=d, outer_r=outer_r, od=od, ir=ir, id=id, side=side, rounding=rounding,
        realign=realign, align_tip=align_tip, align_side=align_side, anchor=anchor, spin=spin,
        _fn=_fn, _fa=_fa, _fs=_fs,
    )


def octagon(
    r: float | None = None,
    d: float | None = None,
    outer_r: float | None = None,
    od: float | None = None,
    ir: float | None = None,
    id: float | None = None,
    side: float | None = None,
    rounding: float = 0,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_side: Sequence[float] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A regular octagon. See regular_ngon() for argument details."""
    return regular_ngon(
        n=8, r=r, d=d, outer_r=outer_r, od=od, ir=ir, id=id, side=side, rounding=rounding,
        realign=realign, align_tip=align_tip, align_side=align_side, anchor=anchor, spin=spin,
        _fn=_fn, _fa=_fa, _fs=_fs,
    )


def right_triangle(
    size: Sequence[float] = [1, 1],
    center: bool | None = None,
    anchor: Sequence[float] | None = None,
    spin: float = 0,
) -> PyOpenSCAD:
    """A right triangle, built directly with polygon().

    Args:
        size:   [width, length] of the right triangle
        center: True forces anchor=CENTER, False forces anchor=[-1,-1] (default: use anchor=)
        anchor: anchor point (default: [-1,-1], the right-angle corner)
        spin:   Z-axis rotation in degrees after anchor (default 0)
    """
    sz = [size, size] if isinstance(size, (int, float)) else list(size)
    if anchor is not None:
        use_anchor = anchor
    elif center:
        use_anchor = CENTER
    else:
        use_anchor = [-1, -1, 0]
    path = [[sz[0] / 2, -sz[1] / 2], [-sz[0] / 2, -sz[1] / 2], [-sz[0] / 2, sz[1] / 2]]
    shape = _opolygon(path)
    offset = _anchor_offset_box(sz, use_anchor)
    return _finish(shape, offset, spin)


def _trapezoid_path(
    h: float, w1: float, w2: float, shift: float, chamfer, rounding, flip: bool, _fn=None, _fa=None, _fs=None
) -> list[list[float]]:
    chamfs = list(chamfer) if isinstance(chamfer, (list, tuple)) else [chamfer] * 4
    rounds = list(rounding) if isinstance(rounding, (list, tuple)) else [rounding] * 4
    srads = [rounds[i] if rounds[i] else chamfs[i] for i in range(4)]
    rads = [abs(s) for s in srads]
    base = [
        [w2 / 2 + shift, h / 2],
        [-w2 / 2 + shift, h / 2],
        [-w1 / 2, -h / 2],
        [w1 / 2, -h / 2],
    ]
    ang1 = _v_theta([base[0][0] - base[3][0], base[0][1] - base[3][1]]) - 90
    ang2 = _v_theta([base[1][0] - base[2][0], base[1][1] - base[2][1]]) - 90
    angs = [ang1, ang2, ang2, ang1]
    qdirs = [[1, 1], [-1, 1], [-1, -1], [1, -1]]
    angle_pairs = [
        {"pos": (angs[0], 90), "flip": (angs[0], -90), "neg": (180 + angs[0], 90)},
        {"pos": (90, 180 + angs[1]), "flip": (270, 180 + angs[1]), "neg": (90, angs[1])},
        {"pos": (180 + angs[2], 270), "flip": (180 + angs[2], 90), "neg": (angs[2], -90)},
        {"pos": (-90, angs[3]), "flip": (90, angs[3]), "neg": (270, 180 + angs[3])},
    ]
    cpath = []
    for i in range(4):
        if rads[i] == 0:
            cpath.append(base[i])
            continue
        hyp = _adj_ang_to_hyp(rads[i], angs[i])
        xoff = _adj_ang_to_opp(rads[i], angs[i])
        sign_a = -1 if (srads[i] < 0 and flip) else 1
        a = [xoff * qdirs[i][1] * sign_a, -rads[i] * qdirs[i][1] * sign_a]
        sign_b = 1 if (srads[i] < 0 and not flip) else -1
        b = [a[0] + hyp * qdirs[i][0] * sign_b, a[1]]
        cp = [base[i][0] + b[0], base[i][1] + b[1]]
        if srads[i] > 0:
            a0, a1 = angle_pairs[i]["pos"]
        elif flip:
            a0, a1 = angle_pairs[i]["flip"]
        else:
            a0, a1 = angle_pairs[i]["neg"]
        n = max(3, math.ceil(_frag_count(rads[i], _fn, _fa, _fs) * abs(a1 - a0) / 360)) if rounds[i] else 2
        cpath.extend(_arc_points(n, rads[i], a0, a1 - a0, cp))
    return list(reversed(cpath))


def trapezoid(
    h: float | None = None,
    w1: float | None = None,
    w2: float | None = None,
    angle: float | None = None,
    shift: float = 0,
    chamfer: float | Sequence[float] = 0,
    rounding: float | Sequence[float] = 0,
    flip: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A trapezoid with parallel front and back sides, built directly with polygon().

    Args:
        h:        Y-axis height of the trapezoid
        w1:       X-axis width of the front end
        w2:       X-axis width of the back end
        angle:    if given in place of h/w1/w2, the missing value is derived from this angle
        shift:    X-axis shift of the back of the trapezoid (default 0)
        rounding: corner rounding radius, or per-corner list [X+Y+,X-Y+,X-Y-,X+Y-] (default 0)
        chamfer:  corner chamfer length, or per-corner list [X+Y+,X-Y+,X-Y-,X+Y-] (default 0)
        flip:     point negative roundings/chamfers forward/back instead of left/right (default False)
        anchor:   anchor point (default CENTER)
        spin:     Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides for rounded corners
    """
    defined = sum(x is not None for x in (h, w1, w2, angle))
    assert defined == 3, "Must give exactly 3 of the arguments h, w1, w2, and angle."
    if h is None:
        assert w1 is not None and w2 is not None and angle is not None
        h = _opp_ang_to_adj(abs(w2 - w1) / 2, abs(angle))
    if w1 is None:
        assert w2 is not None and angle is not None
        w1 = w2 + 2 * (_adj_ang_to_opp(h, angle) + shift)
    if w2 is None:
        assert w1 is not None and angle is not None
        w2 = w1 - 2 * (_adj_ang_to_opp(h, angle) + shift)
    assert w1 >= 0 and w2 >= 0 and h > 0 and w1 + w2 > 0, "Degenerate trapezoid geometry."
    path = _trapezoid_path(h, w1, w2, shift, chamfer, rounding, flip, _fn, _fa, _fs)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def star(
    n: int | None = None,
    r: float | None = None,
    ir: float | None = None,
    d: float | None = None,
    outer_r: float | None = None,
    od: float | None = None,
    id: float | None = None,
    step: int | None = None,
    realign: bool = False,
    align_tip: Sequence[float] | None = None,
    align_pit: Sequence[float] | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    atype: str = "hull",
) -> PyOpenSCAD:
    """An N-pointed star polygon, built directly with polygon().

    Note: BOSL2's outer-radius parameter is named `or`, which collides with the Python
    keyword `or`; it is exposed here as `outer_r` instead.

    Args:
        n:          number of stellate tips
        r/outer_r:  radius to the tips of the star (BOSL2 `or`)
        ir:         radius to the inner corners of the star
        d/od:       diameter to the tips of the star
        id:         diameter to the inner corners of the star
        step:       compute inner radius by virtually drawing a line `step` tips around the star (2 <= step < n/2)
        realign:    put the midpoint of the last edge (instead of vertex 0) on the X+ axis (default False)
        align_tip:  rotate so the first tip points in this 2-D direction (applied before spin)
        align_pit:  rotate so the first inner corner points in this 2-D direction (applied before spin)
        anchor:     anchor point (default CENTER)
        spin:       Z-axis rotation in degrees after anchor (default 0)
        atype:      anchor method; only "hull" is implemented here (default "hull")
    """
    rad = _pick_radius(r1=outer_r, d1=od, r=r, d=d)
    if rad is None:
        raise ValueError("star(): must specify a radius (r, d, outer_r or od).")
    assert n is not None, "star(): must specify n"
    if step is not None:
        stepr = rad * math.cos(math.radians(180 * step / n)) / math.cos(math.radians(180 * (step - 1) / n))
    else:
        stepr = rad
    inner_r = _pick_radius(r=ir, d=id, dflt=stepr)
    path1 = []
    for i in range(2 * n, 0, -1):
        theta = math.radians(180.0 * i / n)
        radius = inner_r if i % 2 else rad
        path1.append([radius * math.cos(theta), radius * math.sin(theta)])
    extra_rot = 0.0
    if align_tip is not None:
        extra_rot += math.degrees(math.atan2(align_tip[1], align_tip[0]))
    elif align_pit is not None:
        extra_rot += math.degrees(math.atan2(align_pit[1], align_pit[0])) + 180.0 / n
    if realign:
        extra_rot -= 180.0 / n
    path = [_rotate2d(p, extra_rot) for p in path1] if extra_rot else path1
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


# ---------------------------------------------------------------------------
# Section: Curved 2D Shapes
# ---------------------------------------------------------------------------


def jittered_poly(path: Sequence[Sequence[float]], dist: float = 1 / 512) -> list[list[float]]:
    """Adds tiny random jitter to a path's points.

    Used to work around rendering artifacts from exactly-overlapping coplanar faces.

    Args:
        path: the path to add jitter to
        dist: the amount to jitter points by (default 1/512)
    """
    return [[p[0] + random.uniform(-dist, dist), p[1] + random.uniform(-dist, dist)] for p in path]


def teardrop2d(
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    d: float | None = None,
    circum: bool = False,
    realign: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A 2-D teardrop shape, useful for 3D-printable horizontal holes, built directly with polygon().

    Note: `circum` is approximated the same way as the inscribed case here (BOSL2's exact
    ray-intersection construction for `circum=True` is not reproduced).

    Args:
        r:       radius of the circular part (default 1)
        ang:     angle of the hat walls from the Y axis in degrees (default 45)
        cap_h:   height above center to truncate the shape (default: no truncation)
        d:       diameter of the circular portion (alternative to r)
        circum:  produce a circumscribing teardrop (default False)
        realign: flip whether the bottom is a point or a flat (default False)
        anchor:  anchor point (default CENTER)
        spin:    Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    rad = r if r is not None else (d / 2 if d is not None else 1)
    minheight = rad * math.sin(math.radians(ang))
    maxheight = rad / math.sin(math.radians(ang))
    if cap_h is not None:
        assert cap_h >= minheight, f"cap_h cannot be less than {minheight} but it is {cap_h}"
    pointy = cap_h is None or cap_h >= maxheight
    if cap_h is None or pointy:
        cap_top = [0.0, maxheight]
    else:
        cap_top = [(maxheight - cap_h) * math.tan(math.radians(ang)), cap_h]
    cap_bot = [rad * math.cos(math.radians(ang)), rad * math.sin(math.radians(ang))]
    n = _frag_count(rad, _fn, _fa, _fs)
    start = 90.0 + (180.0 / n if realign else 0.0)
    fullcircle = _circle_pts(rad, n, start=start)
    seglen = math.dist(fullcircle[0], fullcircle[1]) if len(fullcircle) > 1 else 0.0
    skipfactor = 15 if len(fullcircle) == 6 else 3
    path = [cap_top, cap_bot]
    for p in fullcircle:
        if p[1] < cap_bot[1] - 1e-9 and math.hypot(abs(p[0]) - cap_bot[0], p[1] - cap_bot[1]) > seglen / skipfactor:
            path.append(p)
    path.append([-cap_bot[0], cap_bot[1]])
    if not pointy:
        path.append([-cap_top[0], cap_top[1]])
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def egg(
    length: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    R: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    D: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """An egg-shaped 2-D outline, made of two circles joined by tangent arcs, built directly with polygon().

    Args:
        length: length of the egg
        r1:     radius of the left-hand circle
        r2:     radius of the right-hand circle
        R:      radius of the joining arcs
        d1:     diameter of the left-hand circle (alternative to r1)
        d2:     diameter of the right-hand circle (alternative to r2)
        D:      diameter of the joining arcs (alternative to R)
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    if r1 is None:
        assert d1 is not None, "egg(): must give r1 or d1"
        r1 = d1 / 2
    if r2 is None:
        assert d2 is not None, "egg(): must give r2 or d2"
        r2 = d2 / 2
    if R is None:
        assert D is not None, "egg(): must give R or D"
        R = D / 2
    r1v, r2v, Rv = r1, r2, R
    assert length is not None, "egg(): must give length"
    path = _egg_path(length, r1v, r2v, Rv, _fn, _fa, _fs)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def _egg_path(length: float, r1v: float, r2v: float, Rv: float, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
    assert length > 0
    assert Rv > length / 2, "Side radius R must be larger than length/2"
    assert length > r1v + r2v, "Length must be longer than r1+r2"
    c1 = [-length / 2 + r1v, 0.0]
    c2 = [length / 2 - r2v, 0.0]
    m_pts = list(reversed(_circle_circle_intersection(Rv - r1v, c1, Rv - r2v, c2)))
    assert len(m_pts) == 2, "egg(): circles do not intersect for the given length/r1/r2/R."
    arcparms = []
    for m in m_pts:
        u1 = unit([c1[0] - m[0], c1[1] - m[1]])
        u2 = unit([c2[0] - m[0], c2[1] - m[1]])
        arcparms.append([m, [c1[0] + r1v * u1[0], c1[1] + r1v * u1[1]], [c2[0] + r2v * u2[0], c2[1] + r2v * u2[1]]])
    kw = {"_fn": _fn, "_fa": _fa, "_fs": _fs}
    path = []
    path += _arc_between_points(c2, [length / 2, 0.0], arcparms[0][2], r2v, endpoint=False, **kw)
    path += _arc_between_points(arcparms[0][0], arcparms[0][2], arcparms[0][1], Rv, endpoint=False, **kw)
    path += _arc_through_3(c1, r1v, arcparms[0][1], [-length / 2, 0.0], arcparms[1][1], endpoint=False, **kw)
    path += _arc_between_points(arcparms[1][0], arcparms[1][1], arcparms[1][2], Rv, endpoint=False, **kw)
    path += _arc_between_points(c2, arcparms[1][2], [length / 2, 0.0], r2v, endpoint=False, **kw)
    return path


def glued_circles(
    r: float | None = None,
    spread: float = 10,
    tangent: float = 30,
    d: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """Two circles joined by a curved waist, like a dumbbell, built directly with polygon().

    Args:
        r:       radius of the end circles
        spread:  distance between the centers of the end circles (default 10)
        tangent: angle in degrees of the tangent point of the joining arcs, from the Y axis (default 30)
        d:       diameter of the end circles (alternative to r)
        anchor:  anchor point (default CENTER)
        spin:    Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    rad = r if r is not None else (d / 2 if d is not None else 10)
    cp1 = [spread / 2, 0.0]
    sa1 = 90 - tangent
    ea1 = 270 + tangent
    lobearc = ea1 - sa1
    lobesegs = math.ceil(_frag_count(rad, _fn, _fa, _fs) * lobearc / 360)
    if tangent == 0:
        # r2/cp2 (the inner waist arc) are undefined and unused in this case: the two end
        # circles' own arcs already meet with no separate waist curve needed.
        path = _arc_points(lobesegs + 1, rad, sa1, ea1 - sa1, [-cp1[0], -cp1[1]]) + _arc_points(lobesegs + 1, rad, sa1 + 180, ea1 - sa1, cp1)
    else:
        r2 = (spread / 2 / math.sin(math.radians(tangent))) - rad
        cp2 = [0.0, (rad + r2) * math.cos(math.radians(tangent))]
        sa2 = 270 - tangent
        ea2 = 270 + tangent
        subarc = ea2 - sa2
        arcsegs = math.ceil(_frag_count(r2, _fn, _fa, _fs) * abs(subarc) / 360)
        part1 = _arc_points(lobesegs, rad, sa1, ea1 - sa1, [-cp1[0], -cp1[1]], endpoint=False)
        part2 = []
        for k in range(arcsegs):
            theta = (ea2 + 180) + k * ((ea2 - subarc + 180) - (ea2 + 180)) / arcsegs
            part2.append([r2 * math.cos(math.radians(theta)) - cp2[0], r2 * math.sin(math.radians(theta)) - cp2[1]])
        part3 = _arc_points(lobesegs, rad, sa1 + 180, ea1 - sa1, cp1, endpoint=False)
        part4 = []
        for k in range(arcsegs):
            theta = ea2 + k * ((ea2 - subarc) - ea2) / arcsegs
            part4.append([r2 * math.cos(math.radians(theta)) + cp2[0], r2 * math.sin(math.radians(theta)) + cp2[1]])
        path = part1 + part2 + part3 + part4
    maxx_idx = max(range(len(path)), key=lambda i: path[i][0])
    path = list(reversed(path[maxx_idx:] + path[:maxx_idx]))
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def _superformula(theta: float, m1: float, m2: float, n1: float, n2: float, n3: float, a: float, b: float) -> float:
    t1 = abs(math.cos(math.radians(m1 * theta / 4)) / a) ** n2
    t2 = abs(math.sin(math.radians(m2 * theta / 4)) / b) ** n3
    return (t1 + t2) ** (-1.0 / n1)


def supershape(
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
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    atype: str = "hull",
) -> PyOpenSCAD:
    """A 2-D shape from the superformula, built directly with polygon().

    Args:
        step: angle step size for sampling the superformula (smaller = slower, more accurate) (default 0.5)
        n:    number of output points, an alternative to step
        m1:   superformula m1 argument (default 4)
        m2:   superformula m2 argument (default: same as m1)
        n1:   superformula n1 argument (default 1)
        n2:   superformula n2 argument (default: same as n1)
        n3:   superformula n3 argument (default: same as n2)
        a:    superformula a argument (default 1)
        b:    superformula b argument (default: same as a)
        r:    scale the shape to fit in a circle of this radius
        d:    scale the shape to fit in a circle of this diameter
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        atype:  anchor method; only "hull" is implemented here (default "hull")
    """
    n_pts = n if n is not None else math.ceil(360.0 / step)
    n1v = n1 if n1 is not None else 1
    m2v = m2 if m2 is not None else m1
    n2v = n2 if n2 is not None else n1v
    n3v = n3 if n3 is not None else n2v
    bv = b if b is not None else a
    angs = [360.0 - i * 360.0 / n_pts for i in range(n_pts)]
    rvals = [_superformula(t, m1, m2v, n1v, n2v, n3v, a, bv) for t in angs]
    rad = r if r is not None else (d / 2 if d is not None else None)
    scale = (rad / max(rvals)) if rad is not None else 1.0
    path = [[scale * rvals[i] * math.cos(math.radians(angs[i])), scale * rvals[i] * math.sin(math.radians(angs[i]))] for i in range(n_pts)]
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def _linearize_squareness(s: float) -> float:
    # Chamberlain Fong (2016), "Squircular Calculations", arXiv:1604.02174v5.
    c = 2 - 2 * math.sqrt(2)
    d = 1 - 0.5 * c * s
    return 2 * math.sqrt((1 + c) * s * s - c * s) / (d * d)


def squircle_radius_fg(squareness: float, r: float, angle: float) -> float:
    """The Fong-Garcia squircle radius at *angle* degrees for squareness *squareness* and size *r*."""
    s2a = abs(squareness * math.sin(math.radians(2 * angle)))
    return r * math.sqrt(2) / s2a * math.sqrt(1 - math.sqrt(1 - s2a * s2a)) if s2a > 0 else r


def _squircle_fg_path(size, squareness, _fn, _fa, _fs) -> list:
    sq = _linearize_squareness(squareness)
    aspect = size[1] / size[0]
    r = 0.5 * size[0]
    fn = _frag_count(r, _fn, _fa, _fs)
    astep = 90.0 / round(fn / 4) if fn >= 12 else 360.0 / 48
    pts = []
    a = 360.0
    while a > 0.01:
        theta = a + sq * math.sin(math.radians(4 * a)) * 30 / math.pi
        p = squircle_radius_fg(sq, r, theta)
        pts.append([p * math.cos(math.radians(theta)), p * aspect * math.sin(math.radians(theta))])
        a -= astep
    return pts


def squircle(size, squareness: float = 0.5, style: str = "fg", anchor: Sequence[float] = CENTER,
             spin: float = 0, _fn: float | None = None, _fa: float | None = None,
             _fs: float | None = None) -> PyOpenSCAD:
    """A squircle -- a rounded square that morphs between a square and a circle (BOSL2 squircle()).

    *squareness* runs 0 (a circle) to 1 (a square). Only the default ``"fg"`` (Fong-Garcia) style
    is ported; the ``"superellipse"`` and ``"bezier"`` styles are not.

    Args:
        size:       scalar or [x, y] size of the bounding box
        squareness: 0 (circle) .. 1 (square); default 0.5
        style:      only "fg" is supported
        anchor/spin: standard BOSL2 2-D anchor / spin
        _fn/_fa/_fs: smoothness overrides

    Examples:
        .. pythonscad-example::

            s2.squircle(40, squareness=0.7).linear_extrude(height=5).show()
    """
    assert 0 <= squareness <= 1, "squircle(): squareness must be between 0 and 1."
    sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(size[0]), float(size[1])]
    assert style == "fg", 'squircle(): only the default "fg" style is ported.'
    path = _squircle_fg_path(sz, squareness, _fn, _fa, _fs)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def keyhole(l=None, r1: float | None = None, r2: float | None = None, shoulder_r: float = 0,
            d1: float | None = None, d2: float | None = None, length=None, anchor: Sequence[float] = CENTER,
            spin: float = 0, _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> PyOpenSCAD:
    """A keyhole slot -- a small circle joined to a larger one by tangent shoulders (BOSL2 keyhole()).

    Args:
        l:          overall length between the two circle centers (aliases: *length*; default 15)
        r1/d1:      radius/diameter of the small (bottom) circle (default 5)
        r2/d2:      radius/diameter of the large (top) circle (default 10)
        shoulder_r: fillet radius where the shoulders meet the circles (default 0)
        anchor/spin: standard BOSL2 2-D anchor / spin

    Examples:
        .. pythonscad-example::

            s2.keyhole(l=25, r1=4, r2=9, shoulder_r=2).linear_extrude(height=4).show()
    """
    lv = float(l if l is not None else (length if length is not None else 15))
    r1v = float(r1 if r1 is not None else (d1 / 2 if d1 is not None else 5))
    r2v = float(r2 if r2 is not None else (d2 / 2 if d2 is not None else 10))
    assert lv > 0 and lv >= max(r1v, r2v), "keyhole(): l must be positive and at least max(r1, r2)."
    sh = float(shoulder_r) if shoulder_r is not None else min(r1v, r2v) / 2
    cp1, cp2 = [0.0, 0.0], [0.0, -lv]
    minr, maxr = min(r1v, r2v) + sh, max(r1v, r2v) + sh
    dy = math.sqrt(maxr * maxr - minr * minr)
    spt1 = [cp1[0] + minr, cp1[1] - dy] if r1v > r2v else [cp2[0] + minr, cp2[1] + dy]
    spt2 = [-spt1[0], spt1[1]]
    base = cp1 if r1v > r2v else cp2
    ds = [spt1[0] - base[0], spt1[1] - base[1]]
    ang = math.degrees(math.atan2(abs(ds[1]), abs(ds[0])))

    def _arc(**kw):
        return arc(endpoint=False, _fn=_fn, _fa=_fa, _fs=_fs, **kw)

    path = []
    if r1v > r2v:
        path += [spt1] if sh <= 0 else _arc(r=sh, cp=spt1, start=180 - ang, angle=ang)
        path += _arc(r=r2v, cp=cp2, start=0, angle=-180)
        path += [spt2] if sh <= 0 else _arc(r=sh, cp=spt2, start=0, angle=ang)
        path += _arc(r=r1v, cp=cp1, start=180 + ang, angle=-180 - 2 * ang)
    else:
        path += [spt1] if sh <= 0 else _arc(r=sh, cp=spt1, start=180, angle=ang)
        path += _arc(r=r2v, cp=cp2, start=ang, angle=-180 - 2 * ang)
        path += [spt2] if sh <= 0 else _arc(r=sh, cp=spt2, start=360 - ang, angle=ang)
        path += _arc(r=r1v, cp=cp1, start=180, angle=-180)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


def ring(n: int | None = None, ring_width: float | None = None, r: float | None = None,
         r1: float | None = None, r2: float | None = None, d: float | None = None, d1: float | None = None,
         d2: float | None = None, angle=None, anchor: Sequence[float] = CENTER, spin: float = 0,
         _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> PyOpenSCAD:
    """A 2-D ring (annulus) between two concentric radii (BOSL2 ring(), full-annulus form).

    Give either both radii (*r1*/*r2* or *d1*/*d2*) or one radius plus *ring_width*. The arc /
    3-point / corner / width+thickness forms of BOSL2 ``ring()`` are not ported.

    Args:
        r1/r2 (or d1/d2): the two radii/diameters
        r/d + ring_width: one radius plus the wall width
        n:      number of sides (overrides the smoothness overrides)
        anchor/spin: standard BOSL2 2-D anchor / spin

    Examples:
        .. pythonscad-example::

            s2.ring(r=20, ring_width=4).linear_extrude(height=5).show()
    """
    assert angle is None, "ring(): only the full-annulus form is ported (no angle=)."
    r1v = r1 if r1 is not None else (d1 / 2 if d1 is not None else None)
    r2v = r2 if r2 is not None else (d2 / 2 if d2 is not None else None)
    rv = r if r is not None else (d / 2 if d is not None else None)
    if r1v is not None and r2v is not None:
        inner, outer = min(r1v, r2v), max(r1v, r2v)
    else:
        assert rv is not None and ring_width is not None, "ring(): give (r1 and r2) or (r and ring_width)."
        inner, outer = min(rv, rv + ring_width), max(rv, rv + ring_width)
    assert inner != outer and outer > 0, "ring(): zero (or invalid) width."
    fnv = n if n is not None else _fn
    shape = circle(r=outer, _fn=fnv, _fa=_fa, _fs=_fs) - circle(r=inner, _fn=fnv, _fa=_fa, _fs=_fs)
    offset = _anchor_offset_box([2 * outer, 2 * outer], anchor)
    return _finish(shape, offset, spin)


def reuleaux_polygon(
    n: int = 3,
    r: float | None = None,
    d: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """A Reuleaux polygon (constant-width curved-side shape), built directly with polygon().

    Args:
        n:      number of "sides"; must be an odd positive number (default 3)
        r:      scale the shape to fit in a circle of this radius
        d:      scale the shape to fit in a circle of this diameter
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        _fn/_fa/_fs: arc smoothness overrides
    """
    assert n >= 3 and n % 2 == 1
    rad = r if r is not None else (d / 2 if d is not None else 1)
    ssegs = max(3, math.ceil(_frag_count(rad, _fn, _fa, _fs) / n))
    slen = math.dist(_polar_to_xy(rad, 0), _polar_to_xy(rad, 180 - 180.0 / n))
    path = []
    for i in range(n):
        ca = 180 - (i + 0.5) * 360.0 / n
        sa = ca + 180 + 90.0 / n
        ea = ca + 180 - 90.0 / n
        cp = _polar_to_xy(rad, ca)
        path += _arc_points(ssegs - 1, slen, sa, ea - sa, cp, endpoint=False)
    shape = _opolygon(path)
    offset = _anchor_offset_hull(path, anchor)
    return _finish(shape, offset, spin)


# ---------------------------------------------------------------------------
# Section: Text
# ---------------------------------------------------------------------------


def text(
    text: str,
    size: float = 10,
    font: str = "Liberation Sans",
    halign: str | None = None,
    valign: str | None = None,
    spacing: float = 1.0,
    direction: str = "ltr",
    language: str = "en",
    script: str = "latin",
    anchor: str = "baseline",
    spin: float = 0,
) -> PyOpenSCAD:
    """2-D text, built directly with the builtin text() (which already supports halign/valign).

    Args:
        text:      text to create
        size:      font size (default 10)
        font:      font to use (default "Liberation Sans")
        halign:    horizontal alignment: "left", "center", "right" (default "center")
        valign:    vertical alignment: "top", "center", "baseline", "bottom" (default: `anchor`)
        spacing:   relative spacing multiplier between characters (default 1.0)
        direction: text direction: "ltr", "rtl", "ttb", "btt" (default "ltr")
        language:  language the text is in (default "en")
        script:    script the text is in (default "latin")
        anchor:    vertical alignment fallback used when valign isn't given (default "baseline")
        spin:      Z-axis rotation in degrees (default 0)
    """
    h = halign if halign is not None else "center"
    v = valign if valign is not None else anchor
    shape = _otext(text, size=size, font=font, halign=h, valign=v, spacing=spacing, direction=direction, language=language, script=script)
    return shape.rotate([0, 0, spin]) if spin else shape


# ---------------------------------------------------------------------------
# Section: Rounding 2D shapes
# ---------------------------------------------------------------------------


def round2d(
    r: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    children: PyOpenSCAD | None = None,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """Rounds the concave and/or convex corners of arbitrary 2-D children, via chained .offset() calls.

    Giving `r` rounds all corners; `ir` alone rounds only concave corners; `outer_r` alone
    rounds only convex corners; giving both rounds each to a different radius.

    Note: BOSL2's outer-radius parameter is named `or`, exposed here as `outer_r`.

    Args:
        r:        radius to round all concave and convex corners to
        outer_r:  radius to round only convex (outside) corners to (BOSL2 `or`)
        ir:       radius to round only concave (inside) corners to
        children: the 2-D solid(s) to round
        _fn/_fa/_fs: arc smoothness overrides
    """
    orad = outer_r if outer_r is not None else (r if r is not None else 0)
    irad = ir if ir is not None else (r if r is not None else 0)
    assert children is not None, "round2d(): must give children"
    shape = children.offset(delta=irad, chamfer=True)
    shape = shape.offset(delta=-(irad + orad))
    shape = shape.offset(r=orad, _fn=_fn, _fa=_fa, _fs=_fs)
    return shape


def shell2d(
    thickness: float | Sequence[float] | None = None,
    outer_r: float | Sequence[float] = 0,
    ir: float | Sequence[float] = 0,
    children: PyOpenSCAD | None = None,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> PyOpenSCAD:
    """Creates a hollow shell from 2-D children, with optional rounding.

    Note: BOSL2's outer-radius parameter is named `or`, exposed here as `outer_r`.

    Args:
        thickness: shell thickness; positive expands outward, negative shrinks inward,
                   or a 2-element list to do both
        outer_r:   rounding radius for outside corners of the shell (BOSL2 `or`); a
                   [CONVEX,CONCAVE] pair rounds those corner types separately (default 0)
        ir:        rounding radius for inside corners of the shell; a [CONVEX,CONCAVE]
                   pair rounds those corner types separately (default 0)
        children:  the 2-D solid(s) to shell
        _fn/_fa/_fs: arc smoothness overrides
    """
    assert thickness is not None, "shell2d(): must give thickness"
    assert children is not None, "shell2d(): must give children"
    if isinstance(thickness, (int, float)):
        th = [float(thickness), 0.0] if thickness < 0 else [0.0, float(thickness)]
    else:
        tl = [float(v) for v in thickness]
        th = [tl[1], tl[0]] if tl[0] > tl[1] else tl
    orad = [float(outer_r), float(outer_r)] if isinstance(outer_r, (int, float)) else [float(v) for v in outer_r]
    irad = [float(ir), float(ir)] if isinstance(ir, (int, float)) else [float(v) for v in ir]
    kw = {"_fn": _fn, "_fa": _fa, "_fs": _fs}
    outer_shape = round2d(outer_r=orad[0], ir=orad[1], children=children.offset(delta=th[1], _fn=_fn, _fa=_fa, _fs=_fs), **kw)
    inner_shape = round2d(outer_r=irad[1], ir=irad[0], children=children.offset(delta=th[0], _fn=_fn, _fa=_fa, _fs=_fs), **kw)
    return outer_shape - inner_shape
