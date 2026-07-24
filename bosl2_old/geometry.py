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

# LibFile: bosl2/geometry.py
#    Pure-Python port of the pieces of BOSL2's geometry.scad (plus
#    pointlist_bounds() from vectors.scad) that bosl2/paths.py depends on.
#    No osuse()/BOSL2 runtime dependency. Built on numpy: every
#    vector/point-valued function here returns a real numpy ndarray rather
#    than a plain list. Only handles 2D/3D points, and only the subset of
#    behavior (e.g. segment-bounded line_closest_point) that paths.py
#    actually needs.
#
# FileSummary: Points, lines and polygon geometry helpers (BOSL2 geometry.scad).
# FileGroup: BOSL2

import math

import numpy as np

from bosl2.math import EPSILON
from bosl2.vectors import unit


def cross(a, b):
    """3D cross product (returns an ndarray), or 2D cross product (returns a scalar)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape[0] == 2:
        return float(a[0] * b[1] - a[1] * b[0])
    return np.cross(a, b)


def is_collinear(a, b=None, c=None, eps: float = EPSILON) -> bool:
    """True if points *a*, *b*, *c* lie on a common line (any dimension)."""
    if b is None and c is None:
        points = a
        if len(points) < 3:
            return True
        a, b, c = points[0], points[1], points[2]
        # BOSL2 checks every triple, not just the first three; match that.
        return all(is_collinear(points[i], points[i + 1], points[i + 2], eps) for i in range(len(points) - 2))
    a, b, c = np.asarray(a, dtype=float), np.asarray(b, dtype=float), np.asarray(c, dtype=float)
    v1 = b - a
    v2 = c - a
    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 <= eps or n2 <= eps:
        return True
    if a.shape[0] == 2:
        return bool(abs(cross(v1, v2)) <= eps * max(n1, n2))
    return float(np.linalg.norm(cross(v1, v2))) <= eps * n1 * n2


def line_normal(p1, p2=None) -> np.ndarray:
    """Return the unit 2D normal (perpendicular, to the left) of the line through p1, p2."""
    if p2 is None:
        p1, p2 = p1[0], p1[1]
    return unit([p1[1] - p2[1], p2[0] - p1[0]])


def line_closest_point(segment, pt) -> np.ndarray:
    """Closest point on the bounded *segment* = (a, b) to point *pt*."""
    a = np.asarray(segment[0], dtype=float)
    b = np.asarray(segment[1], dtype=float)
    pt = np.asarray(pt, dtype=float)
    d = b - a
    dd = float(d @ d)
    if dd < EPSILON:
        return a.copy()
    t = float((pt - a) @ d) / dd
    t = max(0.0, min(1.0, t))
    return a + t * d


def pointlist_bounds(pts) -> np.ndarray:
    """Return [min_corner, max_corner] bounding box of a list of points, as a (2, dim) ndarray."""
    arr = np.asarray(pts, dtype=float)
    return np.stack([arr.min(axis=0), arr.max(axis=0)])


def _is_point_on_segment(point, seg, eps: float = EPSILON) -> bool:
    a = np.asarray(seg[0], dtype=float)
    b = np.asarray(seg[1], dtype=float)
    point = np.asarray(point, dtype=float)
    v1 = b - a
    v0 = point - a
    vv1 = float(v1 @ v1)
    if vv1 < eps:
        return float(np.linalg.norm(v0)) <= eps
    t = float(v0 @ v1) / vv1
    on_line = bool(abs(cross(v0, v1)) <= eps * float(np.linalg.norm(v1)))
    return on_line and (-eps <= t < 1 + eps)


def general_line_intersection(s1, s2, eps: float = EPSILON):
    """Intersection of infinite lines through segments s1=(a,b), s2=(c,d).

    Returns [point, t, u] where t/u are the parametric positions of the
    intersection along s1/s2 (0 at the first point, 1 at the second), or
    None if the lines are parallel or coincident.
    """
    a, b = np.asarray(s1[0], dtype=float), np.asarray(s1[1], dtype=float)
    c, d = np.asarray(s2[0], dtype=float), np.asarray(s2[1], dtype=float)
    v1 = a - b
    v2 = c - d
    denominator = cross(v1, v2)
    if abs(denominator) <= eps:
        return None
    ac = a - c
    t = cross(ac, v2) / denominator
    u = cross(ac, v1) / denominator
    point = a + t * (b - a)
    return [point, t, u]


def circle_circle_tangents(r1: float, cp1, r2: float, cp2, d1: float | None = None, d2: float | None = None) -> list[list[list[float]]]:
    """Tangent lines between two circles (r1, cp1) and (r2, cp2).

    Returns a list of up to 4 tangent lines, each a [point_on_circle1, point_on_circle2]
    pair: 2 external tangents plus 2 internal (crossing) tangents if the circles don't
    overlap, or just the 2 external tangents if they do.
    """
    r1v = r1 if r1 is not None else d1 / 2
    r2v = r2 if r2 is not None else d2 / 2
    cp1 = np.asarray(cp1, dtype=float)
    cp2 = np.asarray(cp2, dtype=float)
    dist = float(np.linalg.norm(cp2 - cp1))
    r_vals = [(r2v - r1v) / dist, (r2v - r1v) / dist, (-r2v - r1v) / dist, (-r2v - r1v) / dist]
    k_vals = [-1, 1, -1, 1]
    ext = [1, 1, -1, -1]
    if 1 - r_vals[2] ** 2 >= 0:
        n = 4
    elif 1 - r_vals[0] ** 2 >= 0:
        n = 2
    else:
        n = 0
    u = unit(cp2 - cp1)
    result = []
    for i in range(n):
        r = r_vals[i]
        s = math.sqrt(max(0.0, 1 - r * r))
        k = k_vals[i]
        coef = np.array([r * u[0] - k * s * u[1], k * s * u[0] + r * u[1]])
        p1 = cp1 - r1v * coef
        p2 = cp2 - ext[i] * r2v * coef
        if not np.array_equal(p1, p2):
            # Plain Python floats, not ndarrays -- these points typically end up embedded
            # directly in path/region lists passed across the python<->scad bridge (e.g.
            # components.py's FingerHoleWall()), which doesn't know how to convert numpy
            # scalars and silently produces a broken region otherwise.
            result.append([p1.tolist(), p2.tolist()])
    return result
