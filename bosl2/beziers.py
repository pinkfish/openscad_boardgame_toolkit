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

# LibFile: bosl2/beziers.py
#    Pure-Python port of the pieces of BOSL2's beziers.scad used by this
#    project: evaluating Bezier curves/paths into point lists
#    (bezier_points/bezier_curve/bezpath_curve), and building cubic bezier
#    paths from angle+distance control-point specs (bez_begin/bez_tang/
#    bez_end), plus flatten() from lists.scad. No osuse()/BOSL2 runtime
#    dependency.
#
#    bezier_points() -- the hot path, evaluating many points on a curve at
#    once -- uses numpy: it builds the bezier-to-power-basis matrix (the
#    same "matrix representation" BOSL2 itself uses, generalized to any
#    degree N via the standard formula M[i][j] = C(N,j)*C(N-j,i-j)*(-1)^(i-j)
#    rather than BOSL2's hardcoded per-degree table) and evaluates every
#    sample point with one matrix multiply. Every point-valued function in
#    this file returns a real numpy ndarray rather than a plain list.
#
#    Only the 2-D, scalar-angle forms of bez_begin/bez_tang/bez_end are
#    fully exercised by this project, but the 2-D/3-D vector-direction form
#    (`a` given as a vector instead of an angle) is also supported since
#    it's essentially free. The "p=" (angle from Z+) 3-D spherical-angle
#    form and bez_joint() are not implemented, since nothing here uses them.
#
# FileSummary: Evaluate and build Bezier curves and paths (BOSL2 beziers.scad).
# FileGroup: BOSL2

import math

import numpy as np

from bosl2.math import lerpn
from bosl2.vectors import unit as _unit


def _bezier_matrix(n: int) -> np.ndarray:
    m = np.zeros((n + 1, n + 1))
    for i in range(n + 1):
        for j in range(i + 1):
            m[i][j] = math.comb(n, j) * math.comb(n - j, i - j) * ((-1) ** (i - j))
    return m


def bezier_points(curve, u):
    """Evaluate the Bezier curve defined by control points *curve* at parameter(s) *u* (each in [0,1]),
    as an ndarray (or a length-dim ndarray for a scalar *u*)."""
    scalar = isinstance(u, (int, float, np.floating, np.integer))
    us = [u] if scalar else list(u)
    p = np.asarray(curve, dtype=float)
    n = len(curve) - 1
    mp = _bezier_matrix(n) @ p
    powers = np.array([[uv**k for k in range(n + 1)] for uv in us])
    result = powers @ mp
    return result[0] if scalar else result


def bezier_curve(bezier, splinesteps: int = 16, endpoint: bool = True) -> np.ndarray:
    """Sample *splinesteps* segments (splinesteps+1 points) uniformly along the Bezier curve *bezier*."""
    return bezier_points(bezier, lerpn(0, 1, splinesteps + 1, endpoint))


def bezpath_curve(bezpath, splinesteps: int = 16, N: int = 3, endpoint: bool = True) -> np.ndarray:
    """Convert a Bezier path (degree-*N* curves sharing endpoints, `len(bezpath) % N == 1`) into a point ndarray."""
    assert len(bezpath) % N == 1, f"A degree {N} bezier path should have a multiple of {N} points in it, plus 1."
    bezpath = np.asarray(bezpath, dtype=float)
    segs = (len(bezpath) - 1) // N
    step = 1 / splinesteps
    out = []
    for seg in range(segs):
        ctrl = bezpath[seg * N : (seg + 1) * N + 1]
        us = [i * step for i in range(splinesteps)]
        out.append(bezier_points(ctrl, us))
    if endpoint:
        out.append(bezpath[-1:])
    return np.concatenate(out, axis=0)


def _dir_and_dist(a, r) -> tuple[np.ndarray, float]:
    if isinstance(a, (list, tuple, np.ndarray)):
        arr = np.asarray(a, dtype=float)
        dist = float(np.linalg.norm(arr)) if r is None else r
        return _unit(arr), dist
    assert r is not None, "r must be given when a is an angle, not a direction vector"
    rad = math.radians(a)
    return np.array([math.cos(rad), math.sin(rad)]), r


def bez_begin(pt, a, r: float | None = None) -> np.ndarray:
    """The starting endpoint and control point of a cubic bezier path, as a (2, dim) ndarray."""
    u, dist = _dir_and_dist(a, r)
    pt = np.asarray(pt, dtype=float)
    return np.stack([pt, pt + u * dist])


def bez_tang(pt, a, r1: float, r2: float | None = None) -> np.ndarray:
    """A smooth joint (approaching control point, fixed point, departing control point) in a cubic
    bezier path, as a (3, dim) ndarray."""
    r2v = r2 if r2 is not None else r1
    u, _ = _dir_and_dist(a, r1)
    pt = np.asarray(pt, dtype=float)
    return np.stack([pt - u * r1, pt, pt + u * r2v])


def bez_end(pt, a, r: float | None = None) -> np.ndarray:
    """The approaching control point and endpoint of a cubic bezier path, as a (2, dim) ndarray."""
    u, dist = _dir_and_dist(a, r)
    pt = np.asarray(pt, dtype=float)
    return np.stack([pt + u * dist, pt])


def flatten(lst):
    """Flatten one level of nesting: concatenate a list of point-groups into a single ndarray
    (or a plain list, if *lst*'s entries aren't array-like)."""
    if len(lst) > 0 and isinstance(lst[0], np.ndarray):
        return np.concatenate(lst, axis=0)
    out = []
    for x in lst:
        out.extend(x)
    return out
