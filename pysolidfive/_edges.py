from collections.abc import Sequence
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

# LibFile: pysolidfive/_edges.py
#    The cuboid() edge-selector mini-language (`_edges()`, `EDGES_ALL`, edge vectors like
#    `TOP+LEFT`) and the anchor-offset helpers for each primitive family (box/cylinder/
#    sphere/convex-hull), needed by pysolidfive/__init__.py's cuboid()/cyl()/sphere()/etc.
#    Deliberately a vendored copy of the relevant subset of bosl2/shapes3d.py and
#    bosl2/shapes2d.py's _pick_radius() rather than an import from either -- pysolidfive is
#    meant to stand alone (no bosl2, and therefore no transitive numpy dependency; see the
#    package docstring in pysolidfive/__init__.py). Kept byte-for-byte identical to bosl2's
#    algorithm so both libraries still accept identical edge selectors.
#
# FileGroup: pysolidfive

import math

# ---------------------------------------------------------------------------
# Radius/diameter resolution
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# cuboid() edge-set machinery, mirroring BOSL2 attachments.scad
# ---------------------------------------------------------------------------

EDGES_ALL = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
EDGES_NONE = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

# The vector pointing to the center of each edge of a unit cube; EDGE_OFFSETS[axis][i]
# corresponds to edges[axis][i] in the edge-set representation above.
EDGE_OFFSETS = [
    [[0, -1, -1], [0, 1, -1], [0, -1, 1], [0, 1, 1]],
    [[-1, 0, -1], [1, 0, -1], [-1, 0, 1], [1, 0, 1]],
    [[-1, -1, 0], [1, -1, 0], [-1, 1, 0], [1, 1, 0]],
]

_MAJOR_AXIS_VALID = ["X", "Y", "Z", "ALL", "NONE"]


def _is_edge_array(x) -> bool:
    return isinstance(x, list) and len(x) == 3 and all(isinstance(row, list) and len(row) == 4 for row in x)


def _edge_set(v) -> list[list[int]]:
    if _is_edge_array(v):
        return v
    out = []
    for ax in range(3):
        row = []
        for b in (-1, 1):
            for a in (-1, 1):
                v2 = [[0, a, b], [a, 0, b], [a, b, 0]][ax]
                if isinstance(v, str):
                    if v == "X":
                        matched = ax == 0
                    elif v == "Y":
                        matched = ax == 1
                    elif v == "Z":
                        matched = ax == 2
                    elif v == "ALL":
                        matched = True
                    elif v == "NONE":
                        matched = False
                    else:
                        raise ValueError(f"{v} must be a vector, edge array, or one of {_MAJOR_AXIS_VALID}")
                else:
                    nonz = sum(abs(x) for x in v)
                    if nonz == 2:
                        matched = list(v) == v2
                    else:
                        matches = sum(1 for i in range(3) if v[i] and v[i] == v2[i])
                        matched = matches == (1 if nonz == 1 else 2)
                row.append(1 if matched else 0)
        out.append(row)
    return out


def _is_plain_vector(v) -> bool:
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)


def _edges(v, except_: list | None = None) -> list[list[int]]:
    if except_ is None:
        except_ = []
    if v == []:
        return EDGES_NONE
    if isinstance(v, str) or _is_edge_array(v) or _is_plain_vector(v):
        return _edges([v], except_)
    if isinstance(except_, str) or _is_edge_array(except_) or _is_plain_vector(except_):
        return _edges(v, [except_])
    summed = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for x in v:
        es = _edge_set(x)
        for ax in range(3):
            for i in range(4):
                summed[ax][i] += es[ax][i]
    normed = [[1 if summed[ax][i] > 0 else 0 for i in range(4)] for ax in range(3)]
    if not except_:
        return normed
    exc = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for x in except_:
        es = _edge_set(x)
        for ax in range(3):
            for i in range(4):
                exc[ax][i] += es[ax][i]
    return [[1 if (normed[ax][i] - (1 if exc[ax][i] > 0 else 0)) > 0 else 0 for i in range(4)] for ax in range(3)]


# ---------------------------------------------------------------------------
# Anchor-offset helpers, one per primitive family
# ---------------------------------------------------------------------------


def _anchor_offset_box3(size: "Sequence[float]", anchor: "Sequence[float]") -> list[float]:
    a = list(anchor)
    return [-a[i] * size[i] / 2 for i in range(3)]


def _anchor_offset_hull3(points: "Sequence[Sequence[float]]", anchor: "Sequence[float]") -> list[float]:
    a = list(anchor)
    if a[0] == 0 and a[1] == 0 and a[2] == 0:
        return [0.0, 0.0, 0.0]
    best = max(points, key=lambda p: p[0] * a[0] + p[1] * a[1] + p[2] * a[2])
    return [-best[0], -best[1], -best[2]]


def _anchor_offset_cyl(r1: float, r2: float, length: float, anchor: "Sequence[float]", axis: int = 2) -> list[float]:
    a = list(anchor)
    az = a[axis]
    r_at = r1 if az < 0 else (r2 if az > 0 else (r1 + r2) / 2)
    radial_axes = [i for i in range(3) if i != axis]
    radial = [a[i] for i in radial_axes]
    rn = math.hypot(*radial)
    if rn > 0:
        radial = [x / rn * r_at for x in radial]
    offset = [0.0, 0.0, 0.0]
    offset[axis] = az * length / 2
    for i, ax in enumerate(radial_axes):
        offset[ax] = radial[i]
    return [-x for x in offset]


def _anchor_offset_sphere(r: float, anchor: "Sequence[float]") -> list[float]:
    a = list(anchor)
    n = math.hypot(*a)
    if n == 0:
        return [0.0, 0.0, 0.0]
    return [-a[i] / n * r for i in range(3)]
