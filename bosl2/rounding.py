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
#    Pure-Python port of round_corners() from BOSL2's rounding.scad, for
#    2-D paths using the default `method="circle"` (round every corner of
#    a path to a given radius, inserting an arc). No osuse()/BOSL2 runtime
#    dependency.
#
#    Note: only the "circle" method (`radius=`/`r=`) is ported -- the
#    "smooth" (continuous-curvature) and "chamfer" methods, and the
#    `cut=`/`joint=`/`width=` alternate size measures, are not implemented,
#    since nothing in this project uses them. 3-D paths and the
#    minimum-length "scale factor" overflow check (which BOSL2 uses to
#    assert when adjacent roundings are too big to fit) are also not
#    implemented.
#
# FileSummary: Rounds every corner of a path to a given radius (BOSL2 rounding.scad).
# FileGroup: BOSL2

import math

from bosl2.math import EPSILON
from bosl2.comparisons import approx, deduplicate
from bosl2.shapes2d import _frag_count, _arc_points


def _vector_angle3(p0: list[float], p1: list[float], p2: list[float]) -> float:
    dim = len(p1)
    v1 = [p0[i] - p1[i] for i in range(dim)]
    v2 = [p2[i] - p1[i] for i in range(dim)]
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    cosang = max(-1.0, min(1.0, sum(a * b for a, b in zip(v1, v2)) / (n1 * n2)))
    return math.degrees(math.acos(cosang))


def _circlecorner(points: list[list[float]], d: float, r: float, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
    p0, p1, p2 = points
    dim = len(p1)
    v1 = [p0[i] - p1[i] for i in range(dim)]
    v2 = [p2[i] - p1[i] for i in range(dim)]
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    prev = [x / n1 for x in v1]
    nxt = [x / n2 for x in v2]
    cosang = max(-1.0, min(1.0, sum(a * b for a, b in zip(v1, v2)) / (n1 * n2)))
    angle = math.degrees(math.acos(cosang)) / 2
    start = [p1[i] + prev[i] * d for i in range(dim)]
    end = [p1[i] + nxt[i] * d for i in range(dim)]
    if approx(angle, 90):
        return [start, end]
    bis = [prev[i] + nxt[i] for i in range(dim)]
    bislen = math.hypot(*bis)
    bis = [x / bislen for x in bis]
    center = [r / math.sin(math.radians(angle)) * bis[i] + p1[i] for i in range(dim)]
    n = max(3, math.ceil((90 - angle) / 180 * _frag_count(r, _fn, _fa, _fs)))
    a0 = math.degrees(math.atan2(start[1] - center[1], start[0] - center[0]))
    a1 = math.degrees(math.atan2(end[1] - center[1], end[0] - center[0]))
    delta = (a1 - a0 + 180) % 360 - 180
    return _arc_points(n, r, a0, delta, center)


def round_corners(
    path: list[list[float]],
    radius: float | list[float] | None = None,
    r: float | list[float] | None = None,
    closed: bool = True,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> list[list[float]]:
    """Round every corner of a 2-D *path* to the given radius, inserting an arc at each vertex.

    Args:
        path:   2-D path to round the corners of
        radius: rounding radius, a scalar (applied to every corner) or a per-vertex list
        r:      synonym for radius
        closed: if True, treat path as a closed polygon (default True)
        _fn/_fa/_fs: arc smoothness overrides
    """
    n = len(path)
    assert n > 2, f"Path has length {n}. Length must be 3 or more."
    size = radius if radius is not None else r
    assert size is not None, "Must specify radius"
    if isinstance(size, (list, tuple)):
        parm = ([0] + list(size) + [0]) if len(size) < n else list(size)
    else:
        parm = [size] * n

    dk = []
    for i in range(n):
        if (not closed and (i == 0 or i == n - 1)) or parm[i] == 0:
            dk.append([0.0, 0.0])
            continue
        p0, p1, p2 = path[(i - 1) % n], path[i], path[(i + 1) % n]
        angle = _vector_angle3(p0, p1, p2) / 2
        assert not approx(angle, 0), f"Path turns back on itself at index {i} with nonzero rounding"
        dk.append([parm[i] / math.tan(math.radians(angle)), parm[i]])

    out = []
    for i in range(n):
        if dk[i][0] == 0:
            out.append(path[i])
            continue
        p0, p1, p2 = path[(i - 1) % n], path[i], path[(i + 1) % n]
        out.extend(_circlecorner([p0, p1, p2], dk[i][0], dk[i][1], _fn, _fa, _fs))
    return deduplicate(out, closed=closed)
