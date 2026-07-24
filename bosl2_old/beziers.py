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
#    Pure-Python port of the Bezier CURVE and PATH API from BOSL2's
#    beziers.scad. Every operation lives on the :class:`Bezier` class -- there
#    are no module-level bezier functions, mirroring how bosl2/paths.py hangs
#    every path operation off Path. No osuse()/BOSL2 runtime dependency.
#
#    A Bezier is a list of control points: a single curve, or a bezier PATH of
#    degree-N curves that share endpoints (a flat list of control points where
#    ``len % N == 1``). Ported, matching beziers.scad:
#      * curve evaluation/analysis: points, curve, derivative, tangent,
#        curvature, closest_point, length, line_intersection
#      * path evaluation/analysis: path_points, path_curve, path_closest_point,
#        path_length, close_to_axis, path_offset, and Bezier.from_path()
#        (BOSL2 path_to_bezpath)
#      * control-point construction: Bezier.begin/tang/joint/end (BOSL2
#        bez_begin/bez_tang/bez_joint/bez_end), with the scalar-angle, direction
#        -vector, and 3-D spherical-angle (``p=``) forms, and Bezier.flatten
#
#    The Bezier SURFACE subsystem is on the :class:`BezierPatch` class, built on
#    a VNF port (bosl2/vnf.py) and a sweep port (bosl2/skin.py):
#      * patches: points, normals, reverse, flat, is_patch, vnf, to_vnf,
#        vnf_degenerate (bezier_vnf_degenerate_patch), sheet (bezier_sheet),
#        and debug (debug_bezier_patches)
#      * sweeping a shape along a bezier/bezier-path: Bezier.sweep (bezier_sweep)
#        and Bezier.bezpath_sweep, plus Bezier.debug (debug_bezier)
#    The only piece still skipped is path_to_bezcornerpath() -- an internal,
#    undocumented helper needing circle_2tangents/vector_angle.
#
#    ``points()`` -- the hot path -- uses numpy: it builds the bezier-to-power
#    -basis matrix (the same "matrix representation" BOSL2 uses, generalized to
#    any degree N via M[i][j] = C(N,j)*C(N-j,i-j)*(-1)^(i-j) rather than BOSL2's
#    hardcoded per-degree table) and evaluates every sample with one matrix
#    multiply. The point-valued methods return numpy ndarrays.
#
# FileSummary: Evaluate, analyze and build Bezier curves and paths (BOSL2 beziers.scad).
# FileGroup: BOSL2

import math

import numpy as np

from bosl2.math import EPSILON, lerp, lerpn
from bosl2.vectors import unit as _unit
from bosl2.transforms import reorient, apply as _apply
from bosl2.vnf import VNF

UP = [0.0, 0.0, 1.0]


class Bezier(list):
    """A Bezier curve or path: a list of control points, with every bezier operation as a method.

    Subclasses ``list`` (the same trick as :class:`bosl2.paths.Path`), so it is a drop-in for the
    raw control-point lists the toolkit passes around, while giving the chained object form::

        Bezier([[44, 5], [48, 6], [64, -15]]).points([0.2 * i for i in range(6)])
        Bezier.flatten([Bezier.begin([0, 0], -20, 0.4), Bezier.end([1, 0], 230, 1)]).curve(20)

    A *curve* is one set of control points (degree ``len - 1``). A *path* is a flat list of
    degree-``N`` curves sharing endpoints (``len % N == 1``); the ``path_*`` methods interpret
    the Bezier that way. The point-valued methods return numpy ndarrays; the control-point
    builders (``begin``/``tang``/``joint``/``end``) are staticmethods returning raw ndarray
    groups that ``flatten`` concatenates into a new Bezier.

    Args:
        control_points: the control points (anything array-like; 2-D or 3-D points)

    Examples:
        Sweeping a circular profile along a 3-D bezier curve into a solid tube:

        .. pythonscad-example::

            circle = [[2 * math.cos(t), 2 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
            tube = Bezier([[0, 0, 5], [0, 0, 20], [25, 12, 15], [30, 4, 6]]).sweep(circle, splinesteps=24)
            tube.polyhedron().show()
    """

    def __init__(self, control_points=()) -> None:
        pts = np.asarray(list(control_points), dtype=float)
        if pts.size == 0:
            super().__init__()
        else:
            assert pts.ndim == 2, f"Bezier needs a list of control points, got shape {pts.shape}"
            super().__init__([[float(v) for v in row] for row in pts])

    @property
    def array(self) -> np.ndarray:
        """The control points as an (N, dim) numpy array."""
        return np.asarray(self, dtype=float)

    # -- curve evaluation ------------------------------------------------------------------

    def points(self, u):
        """Evaluate this curve's control points at parameter(s) *u* (each in [0, 1]).

        Returns an ndarray of points (or a length-dim ndarray for a scalar *u*)."""
        scalar = isinstance(u, (int, float, np.floating, np.integer))
        us = [u] if scalar else list(u)
        p = self.array
        n = len(self) - 1
        mp = Bezier._matrix(n) @ p
        powers = np.array([[uv**k for k in range(n + 1)] for uv in us])
        result = powers @ mp
        return result[0] if scalar else result

    def curve(self, splinesteps: int = 16, endpoint: bool = True) -> np.ndarray:
        """Sample *splinesteps* segments (splinesteps+1 points) uniformly along the curve."""
        return self.points(lerpn(0, 1, splinesteps + 1, endpoint))

    def derivative(self, u, order: int = 1):
        """The *order*-th derivative of the curve at parameter(s) *u*, as an ndarray."""
        assert isinstance(order, int) and order >= 0
        if order == 0:
            return self.points(u)
        n = len(self) - 1
        dpts = n * np.diff(self.array, axis=0)
        if order == 1:
            return Bezier(dpts).points(u)
        return Bezier(dpts).derivative(u, order - 1)

    def tangent(self, u):
        """Unit tangent vector(s) at parameter(s) *u*, as an ndarray."""
        res = np.asarray(self.derivative(u, 1), dtype=float)
        if res.ndim == 1:
            return np.asarray(_unit(res), dtype=float)
        return np.array([_unit(v) for v in res])

    def curvature(self, u):
        """Curvature value(s) at parameter(s) *u* (inverse tangent-circle radius)."""
        scalar = isinstance(u, (int, float, np.floating, np.integer))
        us = [u] if scalar else list(u)
        d1 = np.atleast_2d(np.asarray(self.derivative(us, 1), dtype=float))
        d2 = np.atleast_2d(np.asarray(self.derivative(us, 2), dtype=float))
        out = []
        for i in range(len(us)):
            n1 = float(np.linalg.norm(d1[i]))
            n2 = float(np.linalg.norm(d2[i]))
            val = math.sqrt(max((n1 * n2) ** 2 - float(d1[i] @ d2[i]) ** 2, 0.0)) / (n1**3)
            out.append(val)
        return out[0] if scalar else np.array(out)

    def closest_point(self, pt, max_err: float = 0.01, u: float = 0.0, end_u: float = 1.0) -> float:
        """The parameter *u* of the point on this curve closest to *pt* (approximate)."""
        pt = np.asarray(pt, dtype=float)
        steps = len(self) * 3
        uvals = [u] + [(end_u - u) * (i / steps) + u for i in range(steps + 1)] + [end_u]
        path = np.asarray(self.points(uvals), dtype=float)
        minima_ranges = []
        for i in range(1, len(uvals) - 1):
            d1 = np.linalg.norm(path[i - 1] - pt)
            d2 = np.linalg.norm(path[i] - pt)
            d3 = np.linalg.norm(path[i + 1] - pt)
            if d2 <= d1 and d2 <= d3:
                minima_ranges.append((uvals[i - 1], uvals[i + 1]))
        if len(minima_ranges) == 0:  # guard BOSL2 leaves implicit: fall back to the nearer end
            de = np.linalg.norm(np.asarray(self.points(end_u)) - pt)
            du = np.linalg.norm(np.asarray(self.points(u)) - pt)
            return end_u if de < du else u
        if len(minima_ranges) > 1:
            min_us = [self.closest_point(pt, max_err, a, b) for a, b in minima_ranges]
            dists = [np.linalg.norm(np.asarray(self.points(v)) - pt) for v in min_us]
            return min_us[int(np.argmin(dists))]
        a, b = minima_ranges[0]
        pp = np.asarray(self.points([a, b]), dtype=float)
        if float(np.linalg.norm(pp[1] - pp[0])) < max_err:
            return (a + b) / 2
        return self.closest_point(pt, max_err, a, b)

    def length(self, start_u: float = 0.0, end_u: float = 1.0, max_deflect: float = 0.01) -> float:
        """Approximate arc length of the curve between *start_u* and *end_u*."""
        from bosl2.paths import Path  # local: avoid importing the heavy path module at load time

        segs = len(self) * 2
        uvals = lerpn(start_u, end_u, segs + 1)
        path = np.asarray(self.points(uvals), dtype=float)
        defl = max(float(np.linalg.norm(path[i + 1] - (path[i] + path[i + 2]) / 2)) for i in range(len(path) - 2))
        if defl <= max_deflect:
            return float(Path._path_length(path))
        return float(sum(
            self.length(lerp(start_u, end_u, i / segs), lerp(start_u, end_u, (i + 1) / segs), max_deflect)
            for i in range(segs)
        ))

    def line_intersection(self, line) -> list:
        """The *u* values where this 2-D curve crosses *line* (two points), each in [0, 1]."""
        a = Bezier._matrix(len(self) - 1) @ self.array  # bezier algebraic coefficients
        line = np.asarray(line, dtype=float)
        n = np.array([-line[1][1] + line[0][1], line[1][0] - line[0][0]])  # line normal
        deg = len(a) - 1
        coeffs = [float(a[i] @ n) for i in range(deg, 0, -1)] + [float((a[0] - line[0]) @ n)]
        return sorted(r for r in Bezier._real_roots(coeffs) if 0.0 <= r <= 1.0)

    # -- bezier path evaluation ------------------------------------------------------------

    def path_points(self, curveind: int, u, N: int = 3):
        """Evaluate curve number *curveind* of this bezier PATH at parameter(s) *u*."""
        sub = self.array[curveind * N : (curveind + 1) * N + 1]
        return Bezier(sub).points(u)

    def path_curve(self, splinesteps: int = 16, N: int = 3, endpoint: bool = True) -> np.ndarray:
        """Sample this bezier PATH (degree-*N* curves sharing endpoints, ``len % N == 1``) into points.

        Kept as the plain concatenation of each segment's samples (unlike BOSL2's bezpath_curve,
        which additionally merges collinear/duplicate points and can emit derivatives) so the
        point set the toolkit's existing outlines are built from does not change.
        """
        assert len(self) % N == 1, f"A degree {N} bezier path should have a multiple of {N} points in it, plus 1."
        bezpath = self.array
        segs = (len(bezpath) - 1) // N
        step = 1 / splinesteps
        out = []
        for seg in range(segs):
            ctrl = Bezier(bezpath[seg * N : (seg + 1) * N + 1])
            us = [i * step for i in range(splinesteps)]
            out.append(ctrl.points(us))
        if endpoint:
            out.append(bezpath[-1:])
        return np.concatenate(out, axis=0)

    def path_closest_point(self, pt, N: int = 3, max_err: float = 0.01) -> list:
        """[segnum, u] for the closest position on this bezier PATH to *pt* (approximate)."""
        pt = np.asarray(pt, dtype=float)
        assert len(self) % N == 1, f"A degree {N} bezier path should have a multiple of {N} points in it, plus 1."
        nsegs = (len(self) - 1) // N
        best = None
        for seg in range(nsegs):
            curve = Bezier(self.array[seg * N : (seg + 1) * N + 1])
            u = curve.closest_point(pt, max_err=0.05)
            dist = float(np.linalg.norm(np.asarray(curve.points(u)) - pt))
            if best is None or dist < best[1]:
                best = (seg, dist)
        seg = best[0]
        curve = Bezier(self.array[seg * N : (seg + 1) * N + 1])
        return [seg, curve.closest_point(pt, max_err=max_err)]

    def path_length(self, N: int = 3, max_deflect: float = 0.001) -> float:
        """Approximate arc length of this bezier PATH."""
        assert len(self) % N == 1, f"A degree {N} bezier path should have a multiple of {N} points in it, plus 1."
        nsegs = (len(self) - 1) // N
        return float(sum(
            Bezier(self.array[seg * N : (seg + 1) * N + 1]).length(max_deflect=max_deflect)
            for seg in range(nsegs)
        ))

    def close_to_axis(self, axis: str = "X", N: int = 3) -> "Bezier":
        """Close this 2-D bezier PATH down to the given axis (\"X\" or \"Y\"), returning a new Bezier."""
        arr = self.array
        assert arr.shape[1] == 2, "close_to_axis() works only on 2-D bezier paths."
        sp, ep = arr[0], arr[-1]
        head = arr[:-1]
        if axis == "X":
            foot_s, foot_e = np.array([sp[0], 0.0]), np.array([ep[0], 0.0])
        elif axis == "Y":
            foot_s, foot_e = np.array([0.0, sp[1]]), np.array([0.0, ep[1]])
        else:
            raise AssertionError('axis must be "X" or "Y"')
        return Bezier(np.concatenate([
            lerpn(foot_s, sp, N, endpoint=False),
            head,
            lerpn(ep, foot_e, N, endpoint=False),
            lerpn(foot_e, foot_s, N + 1),
        ]))

    def path_offset(self, offset, N: int = 3) -> "Bezier":
        """Close this 2-D bezier PATH with a reversed copy offset by *offset* [x, y], returning a Bezier."""
        arr = self.array
        assert arr.shape[1] == 2, "path_offset() works only on 2-D bezier paths."
        off = np.asarray(offset, dtype=float)
        backbez = (arr + off)[::-1]
        return Bezier(np.concatenate([
            arr[:-1],
            lerpn(arr[-1], backbez[0], N, endpoint=False),
            backbez[:-1],
            lerpn(backbez[-1], arr[0], N + 1),
        ]))

    @classmethod
    def from_path(cls, path, closed: bool = False, tangents=None, uniform: bool = False,
                  size=None, relsize=None) -> "Bezier":
        """Cubic bezier PATH through every point of *path*, matching its tangents (BOSL2 path_to_bezpath).

        *size*/*relsize* control how far the curve may deviate from the input path (relsize is a
        fraction of the segment length, default 0.1). Tangents default to ``Path`` tangents.
        """
        from bosl2.paths import Path  # local: keep the import graph acyclic

        assert size is None or relsize is None, "Can't define both size and relsize."
        patharr = np.asarray(path, dtype=float)
        npts = len(patharr)
        lastpt = npts - (0 if closed else 1)
        curvesize = size if size is not None else (relsize if relsize is not None else 0.1)
        relative = size is None
        if isinstance(curvesize, (int, float)):
            sizevect = [float(curvesize)] * lastpt
        else:
            sizevect = [float(v) for v in curvesize]
            assert len(sizevect) == lastpt, f"Size or relsize must have length {lastpt}."
        if tangents is not None:
            tang = np.asarray(tangents, dtype=float)
            tang = np.array([t / np.linalg.norm(t) for t in tang])
        else:
            tang = np.asarray(Path._path_tangents(patharr, closed=closed, uniform=uniform), dtype=float)
        assert min(sizevect) > 0, "Size and relsize must be greater than zero."
        out = []
        M = np.array([[-3, 6, -3], [7, -9, 2], [-5, 3, 0], [1, 0, 0]], dtype=float)
        for i in range(lastpt):
            first = patharr[i]
            second = patharr[(i + 1) % npts]
            seglength = float(np.linalg.norm(second - first))
            assert seglength > 0, f"Path segment has zero length from index {i} to {i + 1}."
            segdir = (second - first) / seglength
            tangent1 = tang[i]
            tangent2 = -tang[(i + 1) % npts]
            parallel = abs(float(tangent1 @ segdir)) + abs(float(tangent2 @ segdir))
            Lmax = seglength / parallel if parallel != 0 else math.inf
            sz = sizevect[i] * seglength if relative else sizevect[i]
            normal1 = tangent1 - (tangent1 @ segdir) * segdir
            normal2 = tangent2 - (tangent2 @ segdir) * segdir
            pcoef = M @ np.array([normal1 @ normal1, normal1 @ normal2, normal2 @ normal2])
            uextreme = [] if float(np.linalg.norm(pcoef)) < EPSILON else [r for r in Bezier._real_roots(pcoef) if 0 < r < 1]
            if len(uextreme) == 0:
                scale = 0.0
            else:
                ctrl = np.array([normal1 * 0, normal1, normal2, normal2 * 0])
                dists = [float(np.linalg.norm(d)) for d in np.atleast_2d(Bezier(ctrl).points(uextreme))]
                scale = dists[0] if len(dists) == 1 else (sum(dists) - 2 * min(dists))
            Ldesired = sz / scale if scale != 0 else math.inf
            L = min(Lmax, Ldesired)
            out.extend([first, first + L * tangent1, second + L * tangent2])
        out.append(patharr[lastpt % npts])
        return cls(out)

    # -- sweeping (BOSL2 bezier_sweep / bezpath_sweep) -------------------------------------

    def sweep(self, shape, splinesteps: int = 16, N: int = 3, method: str = "incremental",
              endpoint: bool = True, normal=None, closed: bool = False, twist: float = 0.0,
              twist_by_length: bool = True, scale=1, scale_by_length: bool = True, symmetry: int = 1,
              last_normal=None, caps=None, style: str = "min_edge", transforms: bool = False):
        """Sweep the 2-D *shape* along this bezier CURVE into a VNF (BOSL2 bezier_sweep()).

        Uses the curve's exact derivatives as tangents (better end joints than path_sweep's
        approximation). *N* is ignored (present for signature parity with :meth:`bezpath_sweep`).
        """
        from bosl2.skin import path_sweep

        path = self.curve(splinesteps, endpoint)
        tang = self.derivative(list(lerpn(0, 1, splinesteps + 1, endpoint)))
        return path_sweep(shape, path, method=method, normal=normal, closed=closed, twist=twist,
                          twist_by_length=twist_by_length, scale=scale, scale_by_length=scale_by_length,
                          symmetry=symmetry, last_normal=last_normal, tangent=tang, caps=caps,
                          style=style, transforms=transforms)

    def bezpath_sweep(self, shape, splinesteps: int = 16, N: int = 3, method: str = "incremental",
                      endpoint: bool = True, normal=None, closed: bool = False, twist: float = 0.0,
                      twist_by_length: bool = True, scale=1, scale_by_length: bool = True, symmetry: int = 1,
                      last_normal=None, caps=None, style: str = "min_edge", transforms: bool = False):
        """Sweep the 2-D *shape* along this bezier PATH into a VNF (BOSL2 bezpath_sweep())."""
        from bosl2.skin import path_sweep

        path = self.path_curve(splinesteps, N, endpoint)
        bezpath = self.array
        segs = (len(bezpath) - 1) // N
        step = 1 / splinesteps
        tang = []
        for seg in range(segs):
            ctrl = Bezier(bezpath[seg * N : (seg + 1) * N + 1])
            tang.extend(ctrl.derivative([i * step for i in range(splinesteps)]))
        if endpoint:
            tang.append(Bezier(bezpath[(segs - 1) * N : segs * N + 1]).derivative(1.0))
        return path_sweep(shape, path, method=method, normal=normal, closed=closed, twist=twist,
                          twist_by_length=twist_by_length, scale=scale, scale_by_length=scale_by_length,
                          symmetry=symmetry, last_normal=last_normal, tangent=tang, caps=caps,
                          style=style, transforms=transforms)

    # -- control-point construction (BOSL2 bez_begin/bez_tang/bez_joint/bez_end) ------------

    @staticmethod
    def begin(pt, a, r: float | None = None, p: float | None = None) -> np.ndarray:
        """The starting endpoint and control point of a cubic bezier path, as a (2, dim) ndarray."""
        pt = np.asarray(pt, dtype=float)
        assert len(pt) == 3 or p is None, "p= requires a 3-D point"
        return np.stack([pt, pt + Bezier._ctrl_offset(len(pt), a, r, p)])

    @staticmethod
    def tang(pt, a, r1: float | None = None, r2: float | None = None, p: float | None = None) -> np.ndarray:
        """A smooth joint (approaching cp, fixed point, departing cp) -- the two cps collinear with
        the fixed point -- in a cubic bezier path, as a (3, dim) ndarray."""
        pt = np.asarray(pt, dtype=float)
        assert len(pt) == 3 or p is None, "p= requires a 3-D point"
        u, dist = Bezier._dir_and_dist(len(pt), a, r1, p)
        r1v = dist if r1 is None else r1
        r2v = r1v if r2 is None else r2
        return np.stack([pt - r1v * u, pt, pt + r2v * u])

    @staticmethod
    def joint(pt, a1, a2, r1: float | None = None, r2: float | None = None,
              p1: float | None = None, p2: float | None = None) -> np.ndarray:
        """A disjoint corner joint (approaching cp, fixed point, departing cp) with the two cps in
        independent directions, in a cubic bezier path, as a (3, dim) ndarray."""
        pt = np.asarray(pt, dtype=float)
        assert len(pt) == 3 or (p1 is None and p2 is None), "p1=/p2= require a 3-D point"
        return np.stack([
            pt + Bezier._ctrl_offset(len(pt), a1, r1, p1),
            pt,
            pt + Bezier._ctrl_offset(len(pt), a2, r2, p2),
        ])

    @staticmethod
    def end(pt, a, r: float | None = None, p: float | None = None) -> np.ndarray:
        """The approaching control point and endpoint of a cubic bezier path, as a (2, dim) ndarray."""
        pt = np.asarray(pt, dtype=float)
        assert len(pt) == 3 or p is None, "p= requires a 3-D point"
        return np.stack([pt + Bezier._ctrl_offset(len(pt), a, r, p), pt])

    def debug(self, width: float = 1.0, N: int = 3):
        """Native geometry visualizing this bezier PATH: the swept curve, control net and control
        points (a functional port of BOSL2's debug_bezier() module; requires the real app)."""
        result = _debug_tube(self.path_curve(N=N), width / 2.0).color("cyan")
        result = result | _debug_tube([list(p) for p in self], width / 2.0).color("green")
        for k, p in enumerate(self):
            marker = _sphere_at(p, width * 2.25).color("blue") if k % N == 0 else _sphere_at(p, width * 0.75).color("red")
            result = result | marker
        return result

    @staticmethod
    def flatten(groups) -> "Bezier":
        """Concatenate a list of control-point groups (from begin/tang/joint/end) into one Bezier."""
        if len(groups) > 0 and isinstance(groups[0], np.ndarray):
            return Bezier(np.concatenate(groups, axis=0))
        out = []
        for x in groups:
            out.extend(x)
        return Bezier(out)

    # -- internals -------------------------------------------------------------------------

    @staticmethod
    def _matrix(n: int) -> np.ndarray:
        m = np.zeros((n + 1, n + 1))
        for i in range(n + 1):
            for j in range(i + 1):
                m[i][j] = math.comb(n, j) * math.comb(n - j, i - j) * ((-1) ** (i - j))
        return m

    @staticmethod
    def _spherical_to_xyz(r: float, theta: float, phi: float) -> np.ndarray:
        """BOSL2 spherical_to_xyz(): theta is the XY angle from X+, phi the angle down from Z+."""
        th, ph = math.radians(theta), math.radians(phi)
        return r * np.array([math.cos(th) * math.sin(ph), math.sin(th) * math.sin(ph), math.cos(ph)])

    @staticmethod
    def _ctrl_offset(dim: int, a, r, p) -> np.ndarray:
        """The control-point offset vector from a fixed point, given a scalar angle / direction
        vector / 3-D spherical angle spec (BOSL2's begin/joint/end direction handling)."""
        if isinstance(a, (list, tuple, np.ndarray)):
            av = np.asarray(a, dtype=float)
            return av if r is None else r * np.asarray(_unit(av), dtype=float)
        assert r is not None, "r must be given when a is an angle, not a direction vector"
        if dim == 3:
            return Bezier._spherical_to_xyz(r, a, 90.0 if p is None else p)
        rad = math.radians(a)
        return r * np.array([math.cos(rad), math.sin(rad)])

    @staticmethod
    def _dir_and_dist(dim: int, a, r, p) -> "tuple[np.ndarray, float]":
        """(unit direction, distance) for a tangent spec -- the direction shared by bez_tang's two
        collinear control points."""
        if isinstance(a, (list, tuple, np.ndarray)):
            av = np.asarray(a, dtype=float)
            dist = float(np.linalg.norm(av)) if r is None else r
            return np.asarray(_unit(av), dtype=float), dist
        assert r is not None, "r must be given when a is an angle, not a direction vector"
        if dim == 3:
            return Bezier._spherical_to_xyz(1.0, a, 90.0 if p is None else p), r
        rad = math.radians(a)
        return np.array([math.cos(rad), math.sin(rad)]), r

    @staticmethod
    def _real_roots(coeffs) -> list:
        """Real roots of a polynomial given highest-degree-coefficient first (BOSL2 real_roots)."""
        c = list(coeffs)
        while len(c) > 1 and abs(c[0]) < 1e-14:
            c = c[1:]
        if len(c) <= 1:
            return []
        return [float(r.real) for r in np.atleast_1d(np.roots(c)) if abs(r.imag) < 1e-9]


class BezierPatch(list):
    """A rectangular Bezier surface patch: a 2-D array (rows x cols) of 3-D control points.

    Evaluate it with :meth:`points`, get surface normals with :meth:`normals`, and mesh it into a
    :class:`~bosl2.vnf.VNF` with :meth:`vnf` (which renders via ``polyhedron()``). Build several
    patches into one VNF with :meth:`to_vnf` (BOSL2 bezier_vnf), and make a flat patch with
    :meth:`flat` (BOSL2 bezier_patch_flat)::

        BezierPatch.flat([100, 100]).vnf(splinesteps=8).polyhedron()

    Ported from beziers.scad's Bezier SURFACE section: bezier_patch_points/_normals/_reverse/
    _flat, is_bezier_patch, and bezier_vnf. NOT ported: bezier_vnf_degenerate_patch (handles
    collapsed-edge patches), bezier_sheet (offset-shell), and bezier_sweep/bezpath_sweep (need
    BOSL2's un-ported path_sweep), plus the debug_* visualization modules.

    Args:
        rows: a list of rows, each a list of [x, y, z] control points

    Examples:
        A bezier surface patch, thickened into a solid sheet:

        .. pythonscad-example::

            patch = [
                [[-50, -50, 0], [-16, -50, 20], [16, -50, -20], [50, -50, 0]],
                [[-50, -16, 20], [-16, -16, 20], [16, -16, -20], [50, -16, 20]],
                [[-50, 16, 20], [-16, 16, -20], [16, 16, 20], [50, 16, 20]],
                [[-50, 50, 0], [-16, 50, -20], [16, 50, 20], [50, 50, 0]],
            ]
            BezierPatch(patch).sheet([0, -6], splinesteps=16).polyhedron().show()
    """

    def __init__(self, rows=()) -> None:
        super().__init__([[[float(x) for x in p] for p in row] for row in rows])

    @property
    def array(self) -> np.ndarray:
        """The control points as an (rows, cols, dim) numpy array."""
        return np.asarray(self, dtype=float)

    @staticmethod
    def is_patch(x) -> bool:
        """True if *x* looks like a bezier patch: a rectangular 2-D array of point vectors."""
        if not (isinstance(x, (list, tuple)) and len(x) > 0):
            return False
        r0 = x[0]
        if not (isinstance(r0, (list, tuple, np.ndarray)) and len(r0) > 0):
            return False
        p0 = r0[0]
        if not (isinstance(p0, (list, tuple, np.ndarray)) and len(p0) >= 2):
            return False
        try:  # a point is a vector of numbers, not a list of points (which a patch-list would give)
            return all(isinstance(e, (int, float, np.integer, np.floating)) for e in p0) and len(x[0]) == len(x[-1])
        except TypeError:
            return False

    # -- evaluation ------------------------------------------------------------------------

    def points(self, u, v):
        """Sample the patch at parameter(s) *u* (inner/column axis) and *v* (outer/row axis).

        Scalar u and v give one point; lists/ranges give a rectangular (len(u) x len(v)) grid."""
        patch = self.array
        R, C = patch.shape[0], patch.shape[1]
        su = isinstance(u, (int, float, np.floating, np.integer))
        sv = isinstance(v, (int, float, np.floating, np.integer))
        if not su and not sv:
            ulist, vlist = list(u), list(v)
            vbezes = np.array([Bezier(patch[:, i, :]).points(ulist) for i in range(C)])  # (C, lenu, dim)
            return np.array([Bezier(vbezes[:, i, :]).points(vlist) for i in range(vbezes.shape[1])])  # (lenu, lenv, dim)
        if su and sv:
            row_pts = np.array([Bezier(patch[r]).points(v) for r in range(R)])  # (R, dim)
            return Bezier(row_pts).points(u)
        if su:
            return self.points([u], v)[0]
        return self.points(u, [v])[:, 0, :]

    def normals(self, u, v):
        """Unit surface normal(s) at parameter(s) *u*, *v* (same shape rules as :meth:`points`)."""
        patch = self.array
        R, C = patch.shape[0], patch.shape[1]
        su = isinstance(u, (int, float, np.floating, np.integer))
        sv = isinstance(v, (int, float, np.floating, np.integer))
        if not su and not sv:
            ulist, vlist = list(u), list(v)
            vbezes = np.array([Bezier(patch[:, i, :]).points(ulist) for i in range(C)])        # (C, lenu, dim)
            dvbezes = np.array([Bezier(patch[:, i, :]).derivative(ulist) for i in range(C)])   # (C, lenu, dim)
            lenu = vbezes.shape[1]
            v_tan = np.array([Bezier(vbezes[:, i, :]).derivative(vlist) for i in range(lenu)])  # (lenu, lenv, dim)
            u_tan = np.array([Bezier(dvbezes[:, i, :]).points(vlist) for i in range(lenu)])     # (lenu, lenv, dim)
            return np.array([[np.asarray(_unit(np.cross(u_tan[i][j], v_tan[i][j])), dtype=float)
                              for j in range(v_tan.shape[1])] for i in range(lenu)])
        if su and sv:
            du = Bezier(np.array([Bezier(patch[r]).points(v) for r in range(R)])).derivative(u)
            dv = Bezier(np.array([Bezier(patch[r]).derivative(v) for r in range(R)])).points(u)
            return np.asarray(_unit(np.cross(du, dv)), dtype=float)
        if su:
            return self.normals([u], v)[0]
        return self.normals(u, [v])[:, 0, :]

    def reverse(self) -> "BezierPatch":
        """The patch with each row reversed (flips the surface orientation)."""
        return BezierPatch([list(reversed(row)) for row in self])

    # -- meshing ---------------------------------------------------------------------------

    def vnf(self, splinesteps=16, style: str = "default") -> VNF:
        """Mesh this patch into a :class:`~bosl2.vnf.VNF`. *splinesteps* is a scalar or [u, v]."""
        ss = splinesteps if isinstance(splinesteps, (list, tuple, np.ndarray)) else (splinesteps, splinesteps)
        uvals = list(lerpn(0, 1, int(ss[0]) + 1))
        vvals = list(lerpn(1, 0, int(ss[1]) + 1))
        return VNF.vertex_array(self.points(uvals, vvals), style=style, reverse=False)

    @staticmethod
    def to_vnf(patches, splinesteps=16, style: str = "default") -> VNF:
        """One patch or a list of patches into a single VNF (BOSL2 bezier_vnf())."""
        if BezierPatch.is_patch(patches):
            return BezierPatch(patches).vnf(splinesteps, style)
        return VNF.join([BezierPatch(p).vnf(splinesteps, style) for p in patches])

    @staticmethod
    def flat(size, N: int = 1, spin: float = 0.0, orient=UP, trans=(0.0, 0.0, 0.0)) -> "BezierPatch":
        """A flat rectangular degree-*N* patch of the given *size*, centered on XY, then reoriented."""
        assert N > 0
        sz = [float(size), float(size)] if isinstance(size, (int, float)) else [float(size[0]), float(size[1])]
        patch = [[[sz[0] * (x / N - 0.5), sz[1] * (0.5 - y / N), 0.0] for y in range(N + 1)] for x in range(N + 1)]
        base = np.asarray(reorient(spin=spin, orient=list(orient)), dtype=float)
        T = np.eye(4)
        T[:3, 3] = np.asarray(trans, dtype=float)
        m = (T @ base).tolist()
        return BezierPatch([_apply(m, row) for row in patch])

    def sheet(self, delta, splinesteps=16, style: str = "default") -> VNF:
        """A thin sheet from this patch, offsetting along the surface normals by *delta* (BOSL2 bezier_sheet()).

        *delta* is a 2-vector [d0, d1] of the two offset distances (a scalar d means [0, -d])."""
        d = [0.0, -float(delta)] if isinstance(delta, (int, float)) else [float(delta[0]), float(delta[1])]
        ss = splinesteps if isinstance(splinesteps, (list, tuple, np.ndarray)) else (splinesteps, splinesteps)
        uvals = list(lerpn(0, 1, int(ss[0]) + 1))
        vvals = list(lerpn(1, 0, int(ss[1]) + 1))
        pts = np.asarray(self.points(uvals, vvals), dtype=float)
        normals = np.asarray(self.normals(uvals, vvals), dtype=float)
        assert not np.any(np.isnan(normals)), "Bezier patch has degenerate normals."
        offset0 = pts - d[0] * normals
        offset1 = pts - d[1] * normals
        allpoints = [np.concatenate([offset0[i], offset1[i][::-1]]) for i in range(len(offset0))]
        vnf = VNF.vertex_array(allpoints, col_wrap=True, caps=True, style=style)
        return vnf.reverse() if d[0] < d[1] else vnf

    def vnf_degenerate(self, splinesteps: int = 16, reverse: bool = False, return_edges: bool = False):
        """VNF for a degenerate patch (some corners/edges collapsed), avoiding excess triangles.

        BOSL2 bezier_vnf_degenerate_patch(). With *return_edges* returns [vnf, edges] where edges
        is [left, right, top, bottom] point lists.
        """
        result = BezierPatch._vnf_degenerate(self.array, splinesteps, reverse, True)
        return result if return_edges else result[0]

    @staticmethod
    def _all_equal(row, eps: float = EPSILON) -> bool:
        a = np.asarray(row, dtype=float)
        return bool(np.all(np.linalg.norm(a - a[0], axis=1) <= eps))

    @staticmethod
    def _vnf_degenerate(patch, splinesteps: int, reverse: bool, return_edges: bool):
        patch = np.asarray(patch, dtype=float)
        R, C = patch.shape[0], patch.shape[1]
        row_degen = [BezierPatch._all_equal(patch[r]) for r in range(R)]
        col_degen = [BezierPatch._all_equal(patch[:, c]) for c in range(C)]
        top_degen, bot_degen = row_degen[0], row_degen[-1]
        left_degen, right_degen = col_degen[0], col_degen[-1]
        samplepts = list(lerpn(0, 1, splinesteps + 1))
        empty = VNF([], [])

        def _tolist(pts):  # list of point rows -> list of lists
            return [list(p) for p in pts]

        if all(row_degen) and all(col_degen):
            return [empty, [[patch[0][0].tolist()] for _ in range(4)]]
        if all(row_degen):
            ptl = _tolist(Bezier(patch[:, 0, :]).points(samplepts))
            return [empty, [ptl, ptl, [ptl[0]], [ptl[-1]]]]
        if all(col_degen):
            ptl = _tolist(Bezier(patch[0]).points(samplepts))
            return [empty, [[ptl[0]], [ptl[-1]], ptl, ptl]]
        if not top_degen and not bot_degen and not left_degen and not right_degen:
            pts = BezierPatch(patch).points(samplepts, samplepts)
            vnf = VNF.vertex_array(pts, reverse=not reverse)
            edges = [[pts[k][0] for k in range(len(pts))], [pts[k][-1] for k in range(len(pts))],
                     list(pts[0]), list(pts[-1])]
            return [vnf, edges]
        if top_degen and bot_degen:
            rowcount = list(range(3, splinesteps + 1, 2))
            if splinesteps % 2 == 0:
                rowcount.append(splinesteps + 1)
            rowcount += list(reversed(list(range(3, splinesteps + 1, 2))))
            bpatch = np.asarray([Bezier(patch[:, i, :]).points(samplepts) for i in range(C)])
            pts = [[bpatch[0][0]]]
            for j in range(0, splinesteps - 1):
                pts.append(_tolist(Bezier(bpatch[:, j + 1, :]).points(list(lerpn(0, 1, rowcount[j])))))
            pts.append([bpatch[0][-1]])
            vnf = VNF.tri_array(pts, reverse=not reverse)
            return [vnf, [[row[0] for row in pts], [row[-1] for row in pts], list(pts[0]), list(pts[-1])]]
        if bot_degen:
            res = BezierPatch._vnf_degenerate(patch[::-1], splinesteps, not reverse, True)
            e = res[1]
            return [res[0], [e[0][::-1], e[1][::-1], e[3], e[2]]]
        if top_degen:
            full_degen = R >= 4 and all(row_degen[1:int(math.ceil(R / 2 - 1)) + 1])
            rowmax = list(range(splinesteps + 1)) if full_degen else [2 * j if j <= splinesteps / 2 else splinesteps for j in range(splinesteps + 1)]
            bpatch = np.asarray([Bezier(patch[:, i, :]).points(samplepts) for i in range(C)])
            pts = [[bpatch[0][0]]]
            for j in range(1, splinesteps + 1):
                pts.append(_tolist(Bezier(bpatch[:, j, :]).points(list(lerpn(0, 1, rowmax[j] + 1)))))
            vnf = VNF.tri_array(pts, reverse=not reverse)
            return [vnf, [[row[0] for row in pts], [row[-1] for row in pts], list(pts[0]), list(pts[-1])]]
        # left or right degeneracy: transpose and recurse
        res = BezierPatch._vnf_degenerate(np.transpose(patch, (1, 0, 2)), splinesteps, not reverse, True)
        e = res[1]
        return [res[0], [e[2], e[3], e[0], e[1]]]

    # -- debugging visualization (BOSL2 debug_bezier_patches) ------------------------------

    def debug(self, splinesteps: int = 16, showcps: bool = True, showdots: bool = False,
              showpatch: bool = True, size=None, style: str = "default"):
        """Native geometry visualizing this patch: the surface plus control points/lines (BOSL2 debug_bezier_patches())."""
        return debug_bezier_patches([self], size=size, splinesteps=splinesteps, showcps=showcps,
                                    showdots=showdots, showpatch=showpatch, style=style)


def _debug_tube(points, r: float, sides: int = 8):
    """A thin native tube swept along *points* (a debug 'stroke'). Requires the native app."""
    from bosl2.skin import path_sweep

    circ = [[r * math.cos(2 * math.pi * k / sides), r * math.sin(2 * math.pi * k / sides)] for k in range(sides)]
    pts = [list(p) for p in points]
    dedup = [pts[0]] + [p for i, p in enumerate(pts[1:], 1) if np.linalg.norm(np.asarray(p) - np.asarray(pts[i - 1])) > 1e-9]
    return path_sweep(circ, dedup).polyhedron()


def _sphere_at(p, d: float):
    from pythonscad import sphere

    p3 = [float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0]
    return sphere(d=d).translate(p3)


def debug_bezier_patches(patches, size=None, splinesteps: int = 16, showcps: bool = True,
                         showdots: bool = False, showpatch: bool = True, style: str = "default"):
    """Native geometry showing bezier patches: surfaces, control points and control-net lines.

    A functional port of BOSL2's debug_bezier_patches() module -- returns a combined native solid
    (requires the real app; builds on VNF.polyhedron() and the ported path_sweep tube).
    """
    plist = patches if not BezierPatch.is_patch(patches) else [patches]
    result = None

    def _add(a, b):
        return b if a is None else (a | b)

    for patch in plist:
        bp = BezierPatch(patch)
        arr = bp.array
        sz = size if size is not None else float(np.max(arr.reshape(-1, arr.shape[-1]).max(axis=0)
                                                        - arr.reshape(-1, arr.shape[-1]).min(axis=0))) * 0.01
        if showcps:
            for row in bp:
                for p in row:
                    result = _add(result, _sphere_at(p, sz * 2).color("red"))
            R, C = arr.shape[0], arr.shape[1]
            for i in range(R):
                for j in range(C):
                    if i < R - 1:
                        result = _add(result, _debug_tube([arr[i][j], arr[i + 1][j]], sz / 2).color("cyan"))
                    if j < C - 1:
                        result = _add(result, _debug_tube([arr[i][j], arr[i][j + 1]], sz / 2).color("cyan"))
        if showpatch or showdots:
            vnf = bp.vnf(splinesteps=splinesteps, style=style)
            if showpatch:
                result = _add(result, vnf.polyhedron())
            if showdots:
                for v in vnf.vertices:
                    result = _add(result, _sphere_at(v, sz).color("blue"))
    return result
