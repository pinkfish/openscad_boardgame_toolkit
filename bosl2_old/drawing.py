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

# LibFile: bosl2/drawing.py
#    Pure-Python port of BOSL2's drawing.scad: the path *generators*
#    (:func:`arc`, :func:`catenary`, :func:`helix`, :func:`turtle`) and the path
#    *renderers* (:func:`stroke`, :func:`dashed_stroke`). The generators return a
#    :class:`~bosl2.paths.Path` (2-D) or a plain list of 3-D points (``helix``); the
#    renderers turn a path into native geometry (``stroke``) or a list of dash
#    sub-paths (``dashed_stroke``).
#
#    ``arc`` itself lives in bosl2/shapes2d.py (it shares that module's $fn/$fa/$fs
#    and 3-point-circle helpers) and is re-exported here so the whole drawing API is
#    reachable as ``bosl2.drawing``. :func:`stroke`/:func:`dashed_stroke` are also
#    attached as methods on :class:`~bosl2.paths.Path` and
#    :class:`~bosl2.regions.Region`, so a built path can be drawn directly
#    (``path.stroke(width=2)``).
#
# FileSummary: Path generators (arc/catenary/helix/turtle) and renderers (stroke/dashed_stroke).
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
from functools import reduce
import math
import operator

import numpy as np

from bosl2.math import lerp, lerpn
from bosl2.vectors import unit
from bosl2.geometry import general_line_intersection, line_normal
from bosl2.paths import Path, Path3D
from bosl2.shapes2d import arc, _frag_count, _pick_radius

__all__ = ["arc", "catenary", "helix", "turtle", "stroke", "dashed_stroke"]


# ---------------------------------------------------------------------------
# Section: 2-D helpers
# ---------------------------------------------------------------------------


def _rot2(deg: float, v: "Sequence[float] | np.ndarray") -> np.ndarray:
    """Rotate the 2-D vector *v* by *deg* degrees about the origin."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y = float(v[0]), float(v[1])
    return np.array([c * x - s * y, s * x + c * y])


def _rot_pts(deg: float, pts):
    """Rotate a list of 2-D points by *deg* degrees about the origin."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [[c * p[0] - s * p[1], s * p[0] + c * p[1]] for p in pts]


# ---------------------------------------------------------------------------
# Section: Path generators
# ---------------------------------------------------------------------------


def catenary(width: float, droop: float | None = None, n: int = 100, angle: float | None = None) -> Path:
    """The catenary (hanging-chain) curve of the given *width*, as a :class:`~bosl2.paths.Path`.

    Give exactly one of *droop* (how far the middle hangs below the endpoints) or *angle* (the
    slope in degrees at the endpoints). The curve passes through ``[-width/2, 0]`` and
    ``[width/2, 0]`` and hangs downward (negative *droop*/*angle* flips it upward). This is BOSL2's
    ``catenary()``.

    Args:
        width: horizontal distance between the endpoints (> 0)
        droop: how far the midpoint hangs below the endpoints (give this or *angle*)
        n:     number of points along the curve (default 100)
        angle: endpoint slope in degrees, ``0 < |angle| < 90`` (give this or *droop*)

    Examples:
        A hanging arch, stroked into a 2-mm ribbon and extruded into a wall:

        .. pythonscad-example::

            catenary(width=80, droop=30).stroke(width=2).linear_extrude(height=6).show()
    """
    assert (droop is None) != (angle is None), "catenary() needs exactly one of droop= or angle="
    assert width > 0, "catenary() needs width > 0."
    assert isinstance(n, int) and n > 0, "catenary() needs a positive integer n."
    given = droop if droop is not None else angle
    assert given is not None
    sgn = int(math.copysign(1, given))
    droop_a = None if droop is None else abs(droop)
    angle_a = None if angle is None else abs(angle)
    assert angle_a is None or (0 < angle_a < 90), "catenary() angle must satisfy 0 < |angle| < 90."

    if droop_a is None:  # solve for the scale that gives the requested endpoint slope
        assert angle_a is not None

        def slope_fn(x):
            p1 = math.cosh(x - 0.001) - 1
            p2 = math.cosh(x + 0.001) - 1
            return math.degrees(math.atan2(p2 - p1, 0.002))
        target, f = angle_a, slope_fn
    else:                # solve for the scale that gives the requested droop
        def droop_fn(x):
            return (math.cosh(x) - 1) / x if x != 0 else 0.0
        target, f = droop_a / (width / 2), droop_fn

    # binary search on x for f(x) == target (f is monotonic increasing away from 0)
    x, inc = 0.0, 4.0
    while inc >= 1e-9:
        if f(x + inc) > target:
            inc /= 2
        else:
            x += inc
    scx = x
    sc = (width / 2) / scx
    droop_v = droop_a if droop_a is not None else (math.cosh(scx) - 1) * sc
    pts = []
    for xv in lerpn(-scx, scx, n):
        xval = xv * sc
        yval = 0.0 if abs(abs(xv) - scx) < 1e-9 else (math.cosh(xv) - 1) * sc - droop_v
        pts.append([xval, yval])
    if sgn < 0:
        pts = [[p[0], -p[1]] for p in pts]
    return Path(pts, closed=False)


def helix(l: float | None = None, h: float | None = None, turns: float | None = None,
          angle: float | None = None, r: float | None = None, r1: float | None = None,
          r2: float | None = None, d: float | None = None, d1: float | None = None,
          d2: float | None = None) -> Path3D:
    """A 3-D helical path on a (possibly conical) surface -- BOSL2's ``helix()``.

    Returned as a :class:`~bosl2.paths.Path3D` (the 3-D path object), so it carries the 3-D
    transforms/measurements and feeds straight into :func:`stroke` or ``path_sweep``. Give
    exactly two of *l*/*h* (length), *turns*, and *angle*; the third is derived. Positive *turns*
    is right-handed, negative left-handed. Start/end radii may differ for a conical helix (a flat
    spiral is ``h=0`` with a turn count).

    Args:
        l/h:     height of the helix (0 for a flat spiral)
        turns:   number of turns (positive = right-handed)
        angle:   helix angle in degrees (measured at the base radius)
        r/d:     radius / diameter (constant helix)
        r1/d1:   bottom radius / diameter
        r2/d2:   top radius / diameter

    Examples:
        A 2.5-turn helix drawn as a tube:

        .. pythonscad-example::

            stroke(helix(turns=2.5, h=100, r=30), width=3).show()
    """
    r1v = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    r2v = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    length = l if l is not None else h
    assert sum(v is not None for v in (length, turns, angle)) == 2, \
        "helix() needs exactly two of l/h, turns, and angle."
    assert angle is None or length != 0, "helix() cannot take an angle with length 0."
    if angle is not None and length != 0:
        dz = 2 * math.pi * r1v * math.tan(math.radians(angle))
    else:
        assert length is not None and turns is not None  # else-branch only reached with both set
        dz = length / abs(turns)
    if turns is not None:
        maxtheta = 360.0 * turns
    else:
        assert length is not None
        maxtheta = 360.0 * length / dz
    nseg = _frag_count(max(r1v, r2v))
    count = max(3, math.ceil(abs(maxtheta) * nseg / 360))
    out = []
    for theta in lerpn(0, maxtheta, count):
        radius = lerp(r1v, r2v, theta / maxtheta) if maxtheta != 0 else r1v
        out.append([radius * math.cos(math.radians(theta)),
                    radius * math.sin(math.radians(theta)),
                    abs(theta) / 360.0 * dz])
    return Path3D(out, closed=False)


# --- turtle ----------------------------------------------------------------

_TURTLE_TWO_ARG = ("arcleft", "arcright", "arcleftto", "arcrightto")


def turtle(commands: Sequence, state: Sequence | None = None, full_state: bool = False,
           repeat: int = 1) -> Path | list:
    """Build a 2-D path from [turtle-graphics](https://en.wikipedia.org/wiki/Turtle_graphics)
    *commands* -- BOSL2's ``turtle()``.

    *commands* is a flat list of command names each optionally followed by a parameter, e.g.
    ``["move", 10, "left", 90, "move", 10]``. The turtle starts at the origin pointing along +X
    with a step length of 1. By default the computed path is returned as a
    :class:`~bosl2.paths.Path`; set *full_state* to get ``[path, step_vector, angle, arcsteps]``
    instead. *repeat* runs the whole command list that many times.

    Supported commands: ``move``/``xmove``/``ymove``/``xymove``, ``jump``/``xjump``/``yjump``,
    ``untilx``/``untily``, ``left``/``turn``/``right``, ``angle``, ``setdir``, ``length``/
    ``scale``/``addlength``, ``arcsteps``, ``arcleft``/``arcright``, ``arcleftto``/``arcrightto``,
    and ``repeat`` (``["repeat", count, [subcommands]]``).

    Examples:
        A rounded-corner square drawn with arcs:

        .. pythonscad-example::

            path = turtle(["move", 40, "arcleft", 8, "move", 40, "arcleft", 8,
                           "move", 40, "arcleft", 8, "move", 40, "arcleft", 8])
            path.stroke(width=3, closed=True).linear_extrude(height=4).show()
    """
    if state is None:
        state = [[[0.0, 0.0]], [1.0, 0.0], 90.0, 0.0]
    else:
        state = list(state)
    result = _turtle_repeat(list(commands), state, True, repeat)
    return result if full_state else Path(result[0], closed=False)


def _turtle_repeat(commands, state, full_state, repeat):
    for _ in range(int(repeat)):
        state = _turtle(commands, state)
    return state if full_state else state[0]


def _turtle_command_len(commands, index) -> int:
    if commands[index] == "repeat":
        return 3
    if (commands[index] in _TURTLE_TWO_ARG and len(commands) > index + 2
            and not isinstance(commands[index + 2], str)):
        return 3
    if index + 1 < len(commands) and isinstance(commands[index + 1], str):
        return 1
    if index + 1 >= len(commands):
        return 1
    return 2


def _turtle(commands, state, index: int = 0):
    while index < len(commands):
        parm = commands[index + 1] if index + 1 < len(commands) else None
        parm2 = commands[index + 2] if index + 2 < len(commands) else None
        state = _turtle_command(commands[index], parm, parm2, state, index)
        index += _turtle_command_len(commands, index)
    return state


def _turtle_command(command, parm, parm2, state, index):
    PATH, STEP, ANGLE, ARCS = 0, 1, 2, 3
    if command == "repeat":
        assert isinstance(parm, (int, float)), f'"repeat" needs a count at index {index}'
        assert isinstance(parm2, (list, tuple)), f'"repeat" needs a command list at index {index}'
        return _turtle_repeat(list(parm2), state, True, int(parm))

    parm = None if isinstance(parm, str) else parm
    parm2 = None if isinstance(parm2, str) else parm2
    lastpt = np.asarray(state[PATH][-1], dtype=float)
    step = np.asarray(state[STEP], dtype=float)

    def with_point(p):
        s = list(state)
        s[PATH] = state[PATH] + [[float(p[0]), float(p[1])]]
        return s

    def with_step(v):
        s = list(state)
        s[STEP] = [float(v[0]), float(v[1])]
        return s

    if command == "move":
        return with_point((parm if parm is not None else 1) * step + lastpt)
    if command == "xmove":
        return with_point((parm if parm is not None else 1) * np.linalg.norm(step) * np.array([1, 0]) + lastpt)
    if command == "ymove":
        return with_point((parm if parm is not None else 1) * np.linalg.norm(step) * np.array([0, 1]) + lastpt)
    if command == "xymove":
        return with_point(lastpt + np.asarray(parm, dtype=float))
    if command == "jump":
        return with_point(parm)
    if command == "xjump":
        return with_point([parm, lastpt[1]])
    if command == "yjump":
        return with_point([lastpt[0], parm])
    if command == "untilx":
        res = general_line_intersection([lastpt, lastpt + step], [[parm, 0], [parm, 1]])
        assert res is not None, f'"untilx" never reaches the goal at index {index}'
        return with_point(res[0])
    if command == "untily":
        res = general_line_intersection([lastpt, lastpt + step], [[0, parm], [1, parm]])
        assert res is not None, f'"untily" never reaches the goal at index {index}'
        return with_point(res[0])
    if command in ("turn", "left"):
        return with_step(_rot2(parm if parm is not None else state[ANGLE], step))
    if command == "right":
        return with_step(_rot2(-(parm if parm is not None else state[ANGLE]), step))
    if command == "angle":
        s = list(state); s[ANGLE] = parm; return s
    if command == "setdir":
        if isinstance(parm, (list, tuple, np.ndarray)):
            return with_step(np.linalg.norm(step) * unit([parm[0], parm[1]]))
        return with_step(np.linalg.norm(step) * np.array([math.cos(math.radians(parm)), math.sin(math.radians(parm))]))
    if command == "length":
        return with_step(parm * unit(step))
    if command == "scale":
        return with_step(parm * step)
    if command == "addlength":
        return with_step(step + unit(step) * parm)
    if command == "arcsteps":
        s = list(state); s[ARCS] = parm; return s
    if command in ("arcleft", "arcright", "arcleftto", "arcrightto"):
        return _turtle_arc(command, parm, parm2, state, index)
    raise AssertionError(f'Unknown turtle command "{command}" at index {index}')


def _turtle_arc(command, parm, parm2, state, index):
    PATH, STEP, ANGLE, ARCS = 0, 1, 2, 3
    assert isinstance(parm, (int, float)), f'"{command}" needs a numeric radius at index {index}'
    lastpt = np.asarray(state[PATH][-1], dtype=float)
    step = np.asarray(state[STEP], dtype=float)
    lrsign = 1 if command in ("arcleft", "arcleftto") else -1
    steps = _frag_count(abs(parm)) if state[ARCS] == 0 else int(state[ARCS])

    if command in ("arcleft", "arcright"):
        myangle = parm2 if parm2 is not None else state[ANGLE]
        radius = parm * (1 if myangle >= 0 else -1)
        center = lastpt + lrsign * radius * line_normal([0, 0], step)
        turn = math.copysign(1, parm) * lrsign * myangle
        rot_step = _rot2(lrsign * myangle, step)
    else:  # arcleftto / arcrightto
        assert isinstance(parm2, (int, float)), f'"{command}" needs a numeric angle at index {index}'
        radius = parm
        center = lastpt + lrsign * radius * line_normal([0, 0], step)
        start_angle = math.degrees(math.atan2(step[1], step[0])) % 360
        end_angle = parm2 % 360
        if lrsign * end_angle < lrsign * start_angle:
            end_angle = end_angle + lrsign * 360
        delta = -start_angle + end_angle
        turn = math.copysign(1, radius) * delta
        rot_step = _rot2(delta, step)

    if turn == 0 or radius == 0:
        arcpath = []
    else:
        p_mid = _rot2(turn / 2, lastpt - center) + center
        p_end = _rot2(turn, lastpt - center) + center
        arcpath = list(arc(steps, points=[lastpt, p_mid, p_end]))[1:]  # drop the shared first point
    s = list(state)
    s[PATH] = state[PATH] + [[float(p[0]), float(p[1])] for p in arcpath]
    s[STEP] = [float(rot_step[0]), float(rot_step[1])]
    return s


# ---------------------------------------------------------------------------
# Section: Path renderers
# ---------------------------------------------------------------------------


# Endcap/joint shape table, ported straight from BOSL2's _shape_defaults(): each entry is
# [width_mult, length_mult, extent_mult]. The realised width/length/extent are these times the
# stroke's line width, then the whole shape is scaled by the line width again (as BOSL2 does).
_ENDCAP_DEFAULTS = {
    None: (1.0, 0.0, 0.0), False: (1.0, 0.0, 0.0), True: (1.0, 1.0, 0.0),
    "butt": (1.0, 0.0, 0.0), "round": (1.0, 1.0, 0.0), "chisel": (1.0, 1.0, 0.0),
    "square": (1.0, 1.0, 0.0), "block": (2.0, 1.0, 0.0), "diamond": (2.5, 1.0, 0.0),
    "dot": (2.0, 1.0, 0.0), "x": (2.5, 0.4, 0.0), "cross": (3.0, 0.33, 0.0),
    "line": (3.5, 0.22, 0.0), "arrow": (3.5, 0.4, 0.5), "arrow2": (3.5, 1.0, 0.14),
    "arrow3": (3.5, 1.0, 0.0), "tail": (3.5, 0.47, 0.5), "tail2": (3.5, 0.28, 0.5),
}


def _endcap_polys(style, lw: float):
    """The local-frame polygon(s) for endcap/joint *style* -- BOSL2's ``_shape_path()``.

    Returns a list of point-lists (one per sub-polygon; ``x``/``cross`` yield four triangles),
    already scaled by the line width *lw*. The local frame has ``+Y`` pointing *outward* along the
    line, so the caller rotates ``+Y`` onto the path's end direction. An empty list == a flush end.
    """
    assert style in _ENDCAP_DEFAULTS, f"stroke(): unknown endcap/joint style {style!r}"
    if style in (False, "butt", None):
        return []
    w_mult, l_mult, e_mult = _ENDCAP_DEFAULTS[style]
    w = w_mult
    l = l_mult * w_mult
    l2 = e_mult * w_mult

    def circle_poly(rx, ry, n):
        return [[rx * math.cos(2 * math.pi * k / n), ry * math.sin(2 * math.pi * k / n)] for k in range(n)]

    if style in (True, "round"):
        polys = [circle_poly(w / 2, l / 2, max(8, _frag_count(w * lw / 2)))]
    elif style == "chisel":            # circle(d=1, $fn=4) scaled [w, l] -> an axis-aligned diamond
        polys = [circle_poly(w / 2, l / 2, 4)]
    elif style == "diamond":           # circle(d=w, $fn=4)
        polys = [circle_poly(w / 2, w / 2, 4)]
    elif style == "dot":               # circle(d=w)
        polys = [circle_poly(w / 2, w / 2, max(8, _frag_count(w * lw)))]
    elif style in ("square", "block", "line"):
        polys = [[[-w / 2, -l / 2], [w / 2, -l / 2], [w / 2, l / 2], [-w / 2, l / 2]]]
    elif style == "x":
        tri = [[(w + l / 2) / 2, (w - l / 2) / 2], [(w - l / 2) / 2, (w + l / 2) / 2], [0, l / 2]]
        polys = [_rot_pts(a, tri) for a in (0, 90, 180, 270)]
    elif style == "cross":
        tri = [[l / 2, w / 2], [-l / 2, w / 2], [-l / 2, l / 2]]
        polys = [_rot_pts(a, tri) for a in (0, 90, 180, 270)]
    elif style == "arrow":
        polys = [[[0, 0], [w / 2, -l2], [w / 2, -l2 - l], [0, -l], [-w / 2, -l2 - l], [-w / 2, -l2]]]
    elif style == "arrow2":
        polys = [[[0, 0], [w / 2, -l2 - l], [0, -l], [-w / 2, -l2 - l]]]
    elif style == "arrow3":
        polys = [[[0, 0], [w / 2, -l], [-w / 2, -l]]]
    elif style == "tail":
        polys = [[[0, 0], [w / 2, l2], [w / 2, l2 - l], [0, -l], [-w / 2, l2 - l], [-w / 2, l2]]]
    elif style == "tail2":
        polys = [[[w / 2, 0], [w / 2, -l], [0, -l - l2], [-w / 2, -l], [-w / 2, 0]]]
    else:  # pragma: no cover - table and branches are kept in sync
        raise AssertionError(f"stroke(): unhandled endcap style {style!r}")
    return [[[p[0] * lw, p[1] * lw] for p in poly] for poly in polys]


def _endcap_trim(style, width: float) -> float:
    """How far to pull the line back under an arrow endcap so it doesn't poke through the tip."""
    if style in ("arrow", "arrow3"):
        wm, lm, _ = _ENDCAP_DEFAULTS[style]
        return width * (lm * wm - 0.01)
    if style == "arrow2":
        wm, lm, _ = _ENDCAP_DEFAULTS[style]
        return width * (lm * wm * 3 / 4)
    return 0.0


def _place(poly, theta_deg: float, at):
    """Rotate a local polygon by *theta_deg* and translate it to point *at*."""
    r = math.radians(theta_deg)
    c, s = math.cos(r), math.sin(r)
    return [[c * p[0] - s * p[1] + at[0], s * p[0] + c * p[1] + at[1]] for p in poly]


def _endcap_geometry_2d(style, at, outdir, width: float):
    """Native 2-D geometry for endcap/joint *style* at *at*, with local +Y rotated onto *outdir*."""
    from pythonscad import polygon as _opolygon

    polys = _endcap_polys(style, width)
    if not polys:
        return None
    theta = math.degrees(math.atan2(outdir[1], outdir[0])) - 90.0  # BACK (+Y) -> outdir
    geos = [_opolygon(_place(poly, theta, at)) for poly in polys]
    return reduce(operator.or_, geos)


def _trim_ends(body, trim1: float, trim2: float):
    """Shorten the open *body* path at each end by trim1/trim2 (clamped within the end segment)."""
    body = [list(map(float, p)) for p in body]
    if len(body) >= 2 and trim1 > 0:
        a, b = np.asarray(body[0]), np.asarray(body[1])
        seglen = float(np.linalg.norm(b - a)) or 1.0
        body[0] = list(a + (b - a) / seglen * min(trim1, 0.99 * seglen))
    if len(body) >= 2 and trim2 > 0:
        a, b = np.asarray(body[-1]), np.asarray(body[-2])
        seglen = float(np.linalg.norm(b - a)) or 1.0
        body[-1] = list(a + (b - a) / seglen * min(trim2, 0.99 * seglen))
    return body


def _stroke2d(pts, width, closed, endcap1, endcap2, joints):
    from bosl2.shapes2d import circle as _circle, square as _square

    shapes = []
    n = len(pts)
    # Pull the body back under arrow endcaps; endcaps still sit at the original endpoints.
    body = list(pts)
    if not closed and n >= 2:
        body = _trim_ends(body, _endcap_trim(endcap1, width), _endcap_trim(endcap2, width))
    nb = len(body)
    for i in (range(nb) if closed else range(nb - 1)):
        a, b = body[i], body[(i + 1) % nb]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1e-9:
            continue
        ang = math.degrees(math.atan2(dy, dx))
        mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        shapes.append(_square([length, width]).rotate([0, 0, ang]).translate(mid))
    # Joints: round/square fill the corner with a centred blob; other styles use the oriented shape.
    for i in (range(nb) if closed else range(1, nb - 1)):
        at = body[i]
        if joints in (True, "round", None):
            shapes.append(_circle(d=width).translate([at[0], at[1]]))
        elif joints == "square":
            shapes.append(_square([width, width]).translate([at[0], at[1]]))
        else:
            incoming = [body[i][0] - body[i - 1][0], body[i][1] - body[i - 1][1]]
            blob = _endcap_geometry_2d(joints, at, incoming, width)
            if blob is not None:
                shapes.append(blob)
    if not closed and n >= 2:
        for cap, end, ref in ((endcap1, pts[0], pts[1]), (endcap2, pts[-1], pts[-2])):
            outdir = [end[0] - ref[0], end[1] - ref[1]]
            blob = _endcap_geometry_2d(cap, end, outdir, width)
            if blob is not None:
                shapes.append(blob)
    assert shapes, "stroke(): path has no drawable segments."
    return reduce(operator.or_, shapes)


def _oriented_to(shape, outdir, at):
    """Rotate a Z-up native solid so +Z points along 3-D *outdir*, then translate it to *at*."""
    from bosl2.transforms import rot_from_to, axis_angle_matrix

    angle, axis = rot_from_to([0, 0, 1], outdir)
    m3 = np.asarray(axis_angle_matrix(angle, axis), dtype=float)
    m4 = [[*m3[0], 0.0], [*m3[1], 0.0], [*m3[2], 0.0], [0.0, 0.0, 0.0, 1.0]]
    return shape.multmatrix(m4).translate([float(c) for c in at])


def _endcap_geometry_3d(style, at, outdir, width: float):
    """Native 3-D endcap for *style*: a sphere for round/dot, else the profile revolved to a solid."""
    from bosl2.shapes3d import sphere as _sphere
    from pythonscad import rotate_extrude as _orotate_extrude, polygon as _opolygon, square as _osquare

    if style in (False, "butt", None):
        return None
    if style in (True, "round"):
        return _sphere(r=width / 2).translate([float(c) for c in at])
    if style == "dot":
        return _sphere(r=width).translate([float(c) for c in at])
    polys = _endcap_polys(style, width)
    if not polys:
        return None
    # Revolve each polygon's right half (x >= 0) about its outward (+Y -> +Z) axis, then orient.
    big = max(abs(v) for poly in polys for p in poly for v in p) * 4 + width
    right = _osquare([big, big], center=True).translate([big / 2, 0])
    solids = [_orotate_extrude((_opolygon(poly) & right)) for poly in polys]
    solid = reduce(operator.or_, solids)
    return _oriented_to(solid, outdir, at)


def _stroke3d(pts, width, closed, endcap1, endcap2):
    from bosl2.shapes3d import sphere as _sphere, cyl as _cyl

    r = width / 2
    shapes = []
    n = len(pts)
    for i in (range(n) if closed else range(n - 1)):
        a = np.asarray(pts[i], dtype=float)
        b = np.asarray(pts[(i + 1) % n], dtype=float)
        d = b - a
        length = float(np.linalg.norm(d))
        if length < 1e-9:
            continue
        seg = _oriented_to(_cyl(h=length, r=r).translate([0, 0, length / 2]), d, a)
        shapes.append(seg)
    for i in (range(n) if closed else range(1, n - 1)):
        shapes.append(_sphere(r=r).translate([float(c) for c in pts[i]]))
    if not closed and n >= 2:
        for cap, end, ref in ((endcap1, pts[0], pts[1]), (endcap2, pts[-1], pts[-2])):
            outdir = [end[j] - ref[j] for j in range(3)]
            blob = _endcap_geometry_3d(cap, end, outdir, width)
            if blob is not None:
                shapes.append(blob)
    assert shapes, "stroke(): path has no drawable segments."
    return reduce(operator.or_, shapes)


def stroke(path, width: float = 1, closed: bool | None = None, endcaps=None, endcap1=None,
           endcap2=None, joints=None, dots=False, color=None):
    """Render *path* as a solid line of the given *width* -- BOSL2's ``stroke()``.

    Works on a 2-D or 3-D point list, a :class:`~bosl2.paths.Path`, a :class:`~bosl2.paths.Path3D`,
    or a :class:`~bosl2.regions.Region` (each of its paths is stroked closed). A 2-D stroke is a
    union of segment rectangles with joints and endcaps; a 3-D stroke is a tube of cylinders with
    spherical joints and revolved endcaps. Returns native geometry.

    Every BOSL2 endcap/joint style is generated directly: ``"round"`` (default), ``"square"``,
    ``"butt"``/``False`` (flush), ``"dot"``, ``"block"``, ``"diamond"``, ``"chisel"``, ``"line"``,
    ``"x"``, ``"cross"``, ``"arrow"``, ``"arrow2"``, ``"arrow3"``, ``"tail"``, and ``"tail2"``.
    Arrow endcaps trim the line back so it doesn't poke through the tip.

    Args:
        path:     a point list, :class:`~bosl2.paths.Path`/:class:`~bosl2.paths.Path3D`, or :class:`~bosl2.regions.Region`
        width:    line width (default 1)
        closed:   close the path into a loop (default: the path's own ``closed`` flag, or True for a Region)
        endcaps:  style for both ends (``endcap1``/``endcap2`` override per end)
        joints:   style for the interior corners (default ``"round"``)
        dots:     mark every vertex with a round dot
        color:    optional colour applied to the whole stroke

    Examples:
        An arc drawn as a 3-mm ribbon with round ends, extruded into a curved wall:

        .. pythonscad-example::

            arc(r=30, angle=200).stroke(width=3).linear_extrude(height=5).show()

        A line with a fancy endcap on each end (arrow one way, tail the other):

        .. pythonscad-example::

            stroke([[0, 0], [50, 0]], width=3, endcap1='tail', endcap2='arrow') \
                .linear_extrude(height=3).show()

        A 3-D arrow: the endcap is a revolved cone on the tube:

        .. pythonscad-example::

            stroke([[0, 0, 0], [40, 0, 0]], width=4, endcaps='arrow').show()
    """
    from bosl2.regions import Region

    if isinstance(path, Region) or (isinstance(path, (list, tuple)) and len(path)
                                    and isinstance(path[0], (Path, Path3D))
                                    and not isinstance(path, (Path, Path3D))):
        parts = [stroke(p, width=width, closed=True, joints=joints, dots=dots) for p in path]
        shape = reduce(operator.or_, parts)
        return shape.color(color) if color is not None else shape

    pts = [list(map(float, p)) for p in path]
    assert len(pts) >= 1, "stroke(): empty path."
    is_closed = closed if closed is not None else getattr(path, "closed", False)
    if dots:
        joints = "dot"
        endcaps = "dot" if endcaps is None else endcaps
    cap1 = endcap1 if endcap1 is not None else (endcaps if endcaps is not None else "round")
    cap2 = endcap2 if endcap2 is not None else (endcaps if endcaps is not None else "round")
    jnt = joints if joints is not None else "round"

    dim = len(pts[0])
    if dim == 2:
        shape = _stroke2d(pts, width, is_closed, cap1, cap2, jnt)
    else:
        shape = _stroke3d(pts, width, is_closed, cap1, cap2)
    return shape.color(color) if color is not None else shape


def dashed_stroke(path, dashpat: Sequence[float] = (3, 3), closed: bool = False,
                  fit: bool = True, mindash: float = 0.5) -> list[Path]:
    """Break *path* into dashes -- BOSL2's ``dashed_stroke()`` function form.

    Returns the list of "on" dash sub-paths (each a :class:`~bosl2.paths.Path`); stroke or extrude
    them to draw a dashed line. *dashpat* alternates dash/gap lengths. With *fit* (the default) the
    pattern is scaled slightly so a whole number of repeats fills the path exactly.

    Args:
        path:    a point list, :class:`~bosl2.paths.Path`, or :class:`~bosl2.regions.Region`
        dashpat: alternating [dash, gap, ...] lengths (default ``(3, 3)``)
        closed:  treat the path as a closed loop
        fit:     scale the pattern to fit a whole number of repeats (default True)
        mindash: drop a trailing dash shorter than this (default 0.5)

    Examples:
        A dashed circle outline, the dashes unioned and extruded into little tiles:

        .. pythonscad-example::

            dashes = dashed_stroke(arc(r=30, angle=360), dashpat=[6, 4], closed=True)
            ring = reduce(lambda a, b: a | b, (d.stroke(width=1.5) for d in dashes))
            ring.linear_extrude(height=3).show()
    """
    from bosl2.regions import Region

    if isinstance(path, Region):
        out: list[Path] = []
        for p in path:
            out.extend(dashed_stroke(p, dashpat, closed=True, fit=fit, mindash=mindash))
        return out

    raw = [list(map(float, p)) for p in path]
    # a 3-D path yields 3-D dashes (Path3D); a 2-D path yields Path
    wrap = Path3D if raw and len(raw[0]) == 3 else Path
    if closed:
        raw = raw + [raw[0]]
    dpat = list(dashpat) if len(dashpat) % 2 == 0 else list(dashpat) + [0]
    plen = Path._path_length(raw, closed=False)
    dlen = sum(dpat)
    doff = list(np.cumsum(dpat))
    freps = plen / dlen
    reps = max(1, round(freps) if fit else math.floor(freps))
    tlen = plen if not fit else reps * dlen + (0 if closed else dpat[0])
    sc = plen / tlen
    cuts = []
    for i in range(reps + 1):
        for off in doff:
            x = i * dlen * sc + off * sc
            if 0 < x < plen - 1e-9:
                cuts.append(x)
    cuts = sorted(c for c in cuts)
    if not cuts:
        return [wrap(raw, closed=False)]
    dashes = Path._path_cut(raw, cuts, closed=False)
    dcnt = len(dashes)
    evens = []
    for i, dash in enumerate(dashes):
        if i % 2 != 0:
            continue
        if i < dcnt - 1 or Path._path_length(dash, closed=False) > mindash:
            evens.append(wrap(dash, closed=False))
    return evens
