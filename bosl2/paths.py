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

# LibFile: bosl2/paths.py
#    Pure-Python port of BOSL2's paths.scad: path length, resampling,
#    tangents/normals/curvature/torsion, cutting paths into subpaths, and
#    splitting self-intersecting polygons into simple polygons. No
#    osuse()/BOSL2 runtime dependency -- built on bosl2/math.py,
#    bosl2/vectors.py, bosl2/lists.py, bosl2/comparisons.py and
#    bosl2/geometry.py (also pure-Python ports), the same way paths.scad
#    depends on math.scad/vectors.scad/lists.scad/comparisons.scad/
#    geometry.scad.
#
#    The numeric path-math functions (length, self-intersection detection,
#    tangents/normals/curvature/torsion, closest-point) convert their input
#    path to a numpy array, use vectorized numpy operations internally, and
#    return real ndarrays -- this mirrors how BOSL2 itself vectorizes these
#    computations across all path points at once (e.g. `vals = path*seg_normal`).
#    Input paths themselves may be plain list[list[float]] or ndarrays (accepted
#    everywhere via np.asarray()). The graph/traversal algorithms (fragment
#    assembly for polygon_parts(), path cutting) stay as plain-Python lists
#    of points/indices, since they're inherently sequential/branchy rather
#    than bulk array math -- individual points flowing through them may
#    themselves be ndarrays (e.g. from lerp()), which works transparently
#    since bosl2/comparisons.py's approx()/deduplicate() and every point
#    comparison in this file use np.array_equal() rather than a bare `==`.
#
# FileSummary: Operations on paths: length, resampling, tangents, splitting into subpaths.
# FileGroup: BOSL2

from collections.abc import Sequence
import math

import numpy as np

from bosl2.math import EPSILON, lerp, lerpn, cumsum, mean, deriv, deriv2, deriv3
from bosl2.vectors import is_vector, add_scalar, unit
from bosl2.lists import select, pair, list_head, list_tail, slice, repeat, column
from bosl2.comparisons import approx, deduplicate, min_index, max_index
from bosl2.geometry import line_normal, line_closest_point, point_in_polygon, polygon_area, is_collinear, cross, general_line_intersection


# ---------------------------------------------------------------------------
# Section: Utility Functions
# ---------------------------------------------------------------------------


def is_path(lst, dim=(2, 3), fast: bool = False) -> bool:
    """True if *lst* is a path: a list/tuple/ndarray of two or more same-length numeric vectors."""
    if isinstance(lst, np.ndarray):
        if lst.ndim != 2 or len(lst) <= 1:
            return False
        if dim is not None:
            dims = dim if isinstance(dim, (list, tuple)) else [dim]
            if lst.shape[1] not in dims:
                return False
        return True
    if fast:
        return isinstance(lst, (list, tuple)) and len(lst) > 0 and is_vector(lst[0])
    if not isinstance(lst, (list, tuple)) or len(lst) <= 1:
        return False
    if not all(isinstance(p, (list, tuple, np.ndarray)) for p in lst):
        return False
    d0 = len(lst[0])
    if d0 == 0 or not all(len(p) == d0 for p in lst) or not all(is_vector(p) for p in lst):
        return False
    if dim is not None:
        dims = dim if isinstance(dim, (list, tuple)) else [dim]
        if d0 not in dims:
            return False
    return True


def is_region(x) -> bool:
    """True if *x* is a region: a non-empty list of paths (list of list of points)."""
    return isinstance(x, list) and len(x) > 0 and all(isinstance(sub, list) and len(sub) > 0 and isinstance(sub[0], list) for sub in x)


def is_1region(path, name: str = "path") -> bool:
    """True if *path* is a region with exactly one component (a 1-region)."""
    if not is_region(path):
        return False
    assert len(path) == 1, f'Parameter "{name}" must be a path or singleton region, but is a multicomponent region'
    return True


def force_path(path, name: str = "path"):
    """If *path* is a 1-region, return its single component as a plain path; otherwise return *path* unchanged."""
    if is_region(path):
        assert len(path) == 1, f'Parameter "{name}" must be a path or singleton region, but is a multicomponent region'
        return path[0]
    return path


def is_closed_path(path, eps: float = EPSILON) -> bool:
    """True if the first and last points of *path* coincide."""
    return approx(path[0], path[-1], eps=eps)


def close_path(path, eps: float = EPSILON) -> list:
    """Append the start point to *path* if it isn't already closed."""
    return path if is_closed_path(path, eps=eps) else path + [path[0]]


def cleanup_path(path, eps: float = EPSILON) -> list:
    """Drop the last point of *path* if it coincides with the first."""
    return path[:-1] if is_closed_path(path, eps=eps) else path


def _path_select(path, s1: int, u1: float, s2: int, u2: float, closed: bool = False) -> list:
    """Portion of *path* from the u1 fraction of segment s1 to the u2 fraction of segment s2."""
    lp = len(path)
    limit = lp - (0 if closed else 1)
    u1 = 0.0 if s1 < 0 else (1.0 if s1 > limit else u1)
    u2 = 0.0 if s2 < 0 else (1.0 if s2 > limit else u2)
    s1c = max(0, min(limit, s1))
    s2c = max(0, min(limit, s2))
    out = []
    if s1c < limit and u1 < 1:
        out.append(lerp(path[s1c], path[(s1c + 1) % lp], u1))
    out.extend(path[i] for i in range(s1c + 1, s2c + 1))
    if s2c < limit and u2 > 0:
        out.append(lerp(path[s2c], path[(s2c + 1) % lp], u2))
    return out


def path_merge_collinear(path, closed: bool | None = None, eps: float = EPSILON) -> list:
    """Remove unnecessary sequential collinear points from *path* (or 1-region)."""
    if is_1region(path):
        return path_merge_collinear(path[0], True if closed is None else closed, eps)
    if closed is None:
        closed = False
    assert is_path(path), "Invalid path in path_merge_collinear."
    if len(path) <= 2:
        return path
    indices = [0]
    end = len(path) - (1 if closed else 2)
    for i in range(1, end + 1):
        if not is_collinear(path[i - 1], path[i], select(path, i + 1), eps=eps):
            indices.append(i)
    if not closed:
        indices.append(len(path) - 1)
    return [path[i] for i in indices]


# ---------------------------------------------------------------------------
# Section: Path length calculation
# ---------------------------------------------------------------------------


def path_length(path, closed: bool | None = None) -> float:
    """Total length of *path* (or 1-region)."""
    if is_1region(path):
        return path_length(path[0], True if closed is None else closed)
    assert is_path(path), "Invalid path in path_length"
    if closed is None:
        closed = False
    if len(path) < 2:
        return 0
    arr = np.asarray(path, dtype=float)
    total = float(np.linalg.norm(np.diff(arr, axis=0), axis=1).sum())
    if closed:
        total += float(np.linalg.norm(arr[-1] - arr[0]))
    return total


def path_segment_lengths(path, closed: bool | None = None) -> np.ndarray:
    """Length of each segment of *path* (or 1-region), as an ndarray."""
    if is_1region(path):
        return path_segment_lengths(path[0], True if closed is None else closed)
    if closed is None:
        closed = False
    assert is_path(path), "Invalid path in path_segment_lengths."
    arr = np.asarray(path, dtype=float)
    lens = np.linalg.norm(np.diff(arr, axis=0), axis=1)
    if closed:
        lens = np.append(lens, np.linalg.norm(arr[0] - arr[-1]))
    return lens


def path_length_fractions(path, closed: bool | None = None) -> np.ndarray:
    """Distance fraction of each point in *path* along the path (0 at the start, 1 at the end), as an ndarray."""
    if is_1region(path):
        return path_length_fractions(path[0], True if closed is None else closed)
    if closed is None:
        closed = False
    assert is_path(path)
    lengths = np.concatenate(([0.0], path_segment_lengths(path, closed)))
    partial = np.cumsum(lengths)
    total = partial[-1]
    return partial / total


def _path_self_intersections(path, closed: bool = True, eps: float = EPSILON) -> list:
    """All self-intersection points of *path*: list of [POINT, SEGNUM1, PROPORTION1, SEGNUM2, PROPORTION2]."""
    p = close_path(path, eps=eps) if closed else path
    arr = np.asarray(p, dtype=float)
    plen = len(arr)
    result = []
    for i in range(0, plen - 2):
        a1, a2 = arr[i], arr[i + 1]
        d = a2 - a1
        seg_normal = np.asarray(unit([-d[1], d[0]], [0.0, 0.0]))
        vals = arr @ seg_normal
        ref = float(a1 @ seg_normal)
        upper = plen - (2 if (i == 0 and closed) else 1)
        js = np.arange(i + 2, upper + 1)
        if len(js) == 0:
            continue
        diffs = vals[js] - ref
        signals = np.where(np.abs(diffs) < eps, 0, np.sign(diffs))
        if not (signals.max() >= 0 and signals.min() <= 0):
            continue
        upper2 = plen - (3 if (i == 0 and closed) else 2)
        for j in range(i + 2, upper2 + 1):
            if signals[j - i - 2] * signals[j - i - 1] <= 0:
                b1, b2 = arr[j].tolist(), arr[j + 1].tolist()
                isect = general_line_intersection([a1.tolist(), a2.tolist()], [b1, b2], eps=eps)
                if isect and -eps <= isect[1] <= 1 + eps and -eps <= isect[2] <= 1 + eps:
                    result.append([isect[0], i, isect[1], j, isect[2]])
    return result


# ---------------------------------------------------------------------------
# Section: Resampling -- changing the number of points in a path
# ---------------------------------------------------------------------------


def _scad_round(x: float) -> float:
    """Round half away from zero, matching OpenSCAD's round() (unlike Python's round-half-to-even)."""
    return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)


def _sum_preserving_round(data: Sequence[float]) -> list[float]:
    """Round every entry to an integer, carrying the rounding error forward so the sum is preserved."""
    out = list(data)
    error = 0.0
    for i in range(len(out) - 1):
        newval = _scad_round(out[i] + error)
        error = out[i] + error - newval
        out[i] = newval
    out[-1] = _scad_round(out[-1] + error)
    return out


def subdivide_path(path, n=None, refine=None, maxlen=None, closed: bool = True, exact: bool | None = None, method: str | None = None) -> list:
    """Subdivide *path* to produce a more finely sampled path; see BOSL2 subdivide_path() for the full option set."""
    path = force_path(path)
    assert is_path(path)
    assert sum(x is not None for x in (n, refine, maxlen)) == 1, "Must give exactly one of n, refine, and maxlen"
    if refine == 1 or n == len(path):
        return path
    if maxlen is not None:
        assert method is None, "Cannot give method with maxlen"
        assert exact is None, "Cannot give exact with maxlen"
        out = []
        for p0, p1 in pair(path, closed):
            steps = math.ceil(math.dist(p1, p0) / maxlen)
            out.extend(lerpn(p0, p1, steps, endpoint=False))
        if not closed:
            out.append(path[-1])
        return out
    exact = True if exact is None else exact
    method = "length" if method is None else method
    assert method in ("length", "segment")
    if n is None:
        assert refine is not None, "Must give exactly one of n, refine, and maxlen"
        n = len(path) * refine
    assert (isinstance(n, (int, float)) and n > 0) or isinstance(n, (list, tuple)), "Parameter n to subdivide_path must be positive number or vector"
    count = len(path) - (0 if closed else 1)
    if method == "segment":
        if isinstance(n, (list, tuple)):
            assert len(n) == count, "Vector parameter n to subdivide_path has the wrong length"
            add_guess = add_scalar(list(n), -1)
        else:
            add_guess = repeat((n - len(path)) / count, count)
    else:
        assert isinstance(n, (int, float)), 'Parameter n to subdivide path must be a number when method="length"'
        path_lens = path_segment_lengths(path, closed)
        add_density = (n - len(path)) / sum(path_lens)
        add_guess = [ln * add_density for ln in path_lens]
    add_list = [float(v) for v in add_guess]
    add = _sum_preserving_round(add_list) if exact else [_scad_round(v) for v in add_list]
    out = []
    for i in range(count):
        out.extend(lerpn(path[i], select(path, i + 1), 1 + int(add[i]), endpoint=False))
    if not closed:
        out.append(path[-1])
    return out


def resample_path(path, n=None, spacing=None, closed: bool = True) -> list:
    """Uniformly resample *path* to *n* points, or to a spacing near *spacing*."""
    path = force_path(path)
    assert is_path(path)
    assert (n is None) != (spacing is None), "Must define exactly one of n and spacing"
    length = path_length(path, closed)
    if n is not None:
        n_use = n - (0 if closed else 1)
    else:
        assert spacing is not None
        n_use = round(length / spacing)
    distlist = lerpn(0, length, n_use, endpoint=False)
    cuts = path_cut_points(path, distlist, closed=closed)
    out = [c[0] for c in cuts]
    if not closed:
        out.append(path[-1])
    return out


# ---------------------------------------------------------------------------
# Section: Path Geometry
# ---------------------------------------------------------------------------


def is_path_simple(path, closed: bool | None = None, eps: float = EPSILON) -> bool:
    """True if the 2D *path* has no self-intersections (repeated points are not considered intersections)."""
    if is_1region(path):
        return is_path_simple(path[0], True if closed is None else closed, eps)
    if closed is None:
        closed = False
    assert is_path(path, dim=(2,)), "Must give a 2D path"
    arr = np.asarray(path, dtype=float)
    n = len(arr)
    end = n - (2 if closed else 3)
    for i in range(0, end + 1):
        v1 = arr[i + 1] - arr[i]
        v2 = arr[(i + 2) % n] - arr[i + 1]
        n1, n2 = float(np.hypot(*v1)), float(np.hypot(*v2))
        if n1 > 0 and n2 > 0 and approx(float(v1 @ v2) / (n1 * n2), -1):
            return False
    return len(_path_self_intersections(path, closed=closed, eps=eps)) == 0


def path_closest_point(path, pt: Sequence[float], closed: bool = True) -> list:
    """[SEGNUM, POINT]: the closest path segment to *pt*, and the closest point (an ndarray) on it."""
    path = force_path(path)
    assert is_path(path), "Input must be a path"
    pts = [line_closest_point(seg, pt) for seg in pair(path, closed)]
    dists = np.linalg.norm(np.asarray(pts, dtype=float) - np.asarray(pt, dtype=float), axis=1)
    min_seg = int(np.argmin(dists))
    return [min_seg, pts[min_seg]]


def path_tangents(path, closed: bool | None = None, uniform: bool = True) -> np.ndarray:
    """Normalized tangent vector at each point of *path*, as an ndarray."""
    if is_1region(path):
        return path_tangents(path[0], True if closed is None else closed, uniform)
    if closed is None:
        closed = False
    assert is_path(path)
    if not uniform:
        d = np.asarray(deriv(path, closed=closed, h=path_segment_lengths(path, closed)), dtype=float)
    else:
        d = np.asarray(deriv(path, closed=closed), dtype=float)
    norms = np.linalg.norm(d, axis=1, keepdims=True)
    assert np.all(norms.ravel() > EPSILON), "Cannot normalize a zero vector"
    return d / norms


def path_normals(path, tangents=None, closed: bool | None = None) -> np.ndarray:
    """Normal vector (perpendicular to the tangent, in the plane of the curve) at each point of *path*, as an ndarray."""
    if is_1region(path):
        return path_normals(path[0], tangents, True if closed is None else closed)
    if closed is None:
        closed = False
    assert is_path(path, dim=(2, 3))
    if tangents is None:
        tangents = path_tangents(path, closed)
    dim = len(path[0])
    assert is_path(tangents) and len(tangents[0]) == dim, "Dimensions of path and tangents must match"
    tarr = np.asarray(tangents, dtype=float)
    if dim == 2:
        return np.stack([tarr[:, 1], -tarr[:, 0]], axis=1)
    n = len(path)
    parr = np.asarray(path, dtype=float)
    out = []
    for i in range(n):
        if i == 0:
            idx = [-1, 0, 1] if closed else [0, 1, 2]
        elif i == n - 1:
            idx = [i - 1, i, (i + 1) % n] if closed else [i - 2, i - 1, i]
        else:
            idx = [i - 1, i, i + 1]
        pts = parr[idx]
        v = np.cross(np.cross(pts[1] - pts[0], pts[2] - pts[0]), tarr[i])
        norm = float(np.linalg.norm(v))
        assert norm > EPSILON, "3D path contains collinear points"
        out.append(v / norm)
    return np.asarray(out)


def path_curvature(path, closed: bool | None = None) -> np.ndarray:
    """Numeric curvature estimate of *path* at each point, as an ndarray."""
    if is_1region(path):
        return path_curvature(path[0], True if closed is None else closed)
    if closed is None:
        closed = False
    assert is_path(path)
    d1 = np.asarray(deriv(path, closed=closed), dtype=float)
    d2 = np.asarray(deriv2(path, closed=closed), dtype=float)
    n1 = np.linalg.norm(d1, axis=1)
    n2 = np.linalg.norm(d2, axis=1)
    dot = np.einsum("ij,ij->i", d1, d2)
    val = np.clip((n1 * n2) ** 2 - dot**2, 0.0, None)
    return np.sqrt(val) / n1**3


def path_torsion(path, closed: bool = False) -> np.ndarray:
    """Numeric torsion estimate of a 3D *path* at each point, as an ndarray."""
    assert is_path(path, dim=(3,)), "Input path must be a 3d path"
    d1 = np.asarray(deriv(path, closed=closed), dtype=float)
    d2 = np.asarray(deriv2(path, closed=closed), dtype=float)
    d3 = np.asarray(deriv3(path, closed=closed), dtype=float)
    crossterm = np.cross(d1, d2)
    dot = np.einsum("ij,ij->i", crossterm, d3)
    denom = np.einsum("ij,ij->i", crossterm, crossterm)
    return dot / denom


# ---------------------------------------------------------------------------
# Section: Breaking paths up into subpaths
# ---------------------------------------------------------------------------


def path_cut(path, cutdist, closed: bool | None = None) -> list:
    """Cut *path* into subpaths at the given ascending list of distances (or a single distance)."""
    if isinstance(cutdist, (int, float)):
        return path_cut(path, [cutdist], closed)
    if is_1region(path):
        return path_cut(path[0], cutdist, True if closed is None else closed)
    if closed is None:
        closed = False
    assert isinstance(cutdist, (list, tuple, np.ndarray))
    assert cutdist[-1] < path_length(path, closed=closed), "Cut distances must be smaller than the path length"
    assert cutdist[0] > 0, "Cut distances must be strictly positive"
    cutlist = path_cut_points(path, cutdist, closed=closed)
    return _path_cut_getpaths(path, cutlist, closed)


def _path_cut_getpaths(path, cutlist, closed: bool) -> list:
    cuts = len(cutlist)
    result = []
    seg0 = list(list_head(path, cutlist[0][1] - 1))
    if not approx(cutlist[0][0], path[cutlist[0][1] - 1]):
        seg0.append(cutlist[0][0])
    result.append(seg0)
    for i in range(cuts - 1):
        if np.array_equal(cutlist[i][0], cutlist[i + 1][0]) and cutlist[i][1] == cutlist[i + 1][1]:
            result.append([])
            continue
        seg = []
        if not approx(cutlist[i][0], select(path, cutlist[i][1])):
            seg.append(cutlist[i][0])
        seg.extend(slice(path, cutlist[i][1], cutlist[i + 1][1] - 1))
        if not approx(cutlist[i + 1][0], select(path, cutlist[i + 1][1] - 1)):
            seg.append(cutlist[i + 1][0])
        result.append(seg)
    last_seg = []
    if not approx(cutlist[cuts - 1][0], select(path, cutlist[cuts - 1][1])):
        last_seg.append(cutlist[cuts - 1][0])
    last_seg.extend(select(path, cutlist[cuts - 1][1], 0 if closed else -1))
    result.append(last_seg)
    return result


def path_cut_points(path, cutdist, closed: bool = False, direction: bool = False):
    """Cut *path* at the given distance(s) from the start; returns [[point, next_index], ...] (or a single entry if *cutdist* is a scalar)."""
    long_enough = len(path) >= (3 if closed else 2)
    assert long_enough, "Two points needed to define a path" if len(path) < 2 else "Closed path must include three points"
    if isinstance(cutdist, (int, float, np.floating, np.integer)):
        return path_cut_points(path, [cutdist], closed, direction)[0]
    assert isinstance(cutdist, (list, tuple, np.ndarray))
    assert all(cutdist[i] < cutdist[i + 1] for i in range(len(cutdist) - 1)), "Cut distances must be an increasing list"
    cuts = path_cut_points_recurse(path, [float(v) for v in cutdist], closed)
    if not direction:
        return cuts
    dirs = _path_cuts_dir(path, cuts, closed)
    normals = _path_cuts_normals(path, cuts, dirs, closed)
    return [[cuts[i][0], cuts[i][1], dirs[i], normals[i]] for i in range(len(cuts))]


def path_cut_points_recurse(path, dists: Sequence[float], closed: bool = False) -> list:
    result = []
    pind = 0
    dtotal = 0
    for dind in range(len(dists)):
        lastpt = [] if len(result) == 0 else result[-1][0]
        dpartial = 0 if len(result) == 0 else math.dist(lastpt, select(path, pind))
        if dists[dind] < dpartial + dtotal:
            t = (dists[dind] - dtotal) / dpartial
            nextpoint = [lerp(lastpt, select(path, pind), t), pind]
        else:
            nextpoint = _path_cut_single(path, dists[dind] - dtotal - dpartial, closed, pind)
        result.append(nextpoint)
        dtotal = dists[dind]
        pind = nextpoint[1]
    return result


def _path_cut_single(path, dist: float, closed: bool = False, ind: int = 0, eps: float = 1e-7) -> list:
    while True:
        if ind == len(path) - (0 if closed else 1):
            assert dist < eps, "Path is too short for specified cut distance"
            return [select(path, ind), ind + 1]
        d = math.dist(path[ind], select(path, ind + 1))
        if d > dist:
            return [lerp(path[ind], select(path, ind + 1), dist / d), ind + 1]
        dist -= d
        ind += 1


def _path_cuts_normals(path, cuts, dirs, closed: bool = False) -> list:
    out = []
    dim = len(path[0])
    for i in range(len(cuts)):
        if dim == 2:
            out.append([-dirs[i][1], dirs[i][0]])
            continue
        plane = None
        if len(path) >= 3:
            start = max(min(cuts[i][1], len(path) - 1), 2)
            plane = _path_plane(path, start, start - 2, closed)
        if plane is None:
            out.append([1, 0, 0] if (dirs[i][0] == 0 and dirs[i][1] == 0) else unit([-dirs[i][1], dirs[i][0], 0]))
        else:
            out.append(unit(cross(dirs[i], cross(plane[0], plane[1]))))
    return out


def _path_plane(path, ind: int, i: int, closed: bool = False):
    lower = -1 if closed else 0
    while i >= lower:
        if not is_collinear(path[ind], path[ind - 1], select(path, i)):
            p_i = select(path, i)
            return [[a - b for a, b in zip(p_i, path[ind - 1])], [a - b for a, b in zip(path[ind], path[ind - 1])]]
        i -= 1
    return None


def _path_cuts_dir(path, cuts, closed: bool = False, eps: float = 1e-2) -> list:
    out = []
    zeros = [0] * len(path[0])
    for ind in range(len(cuts)):
        nextind = cuts[ind][1]
        nextpath = unit([a - b for a, b in zip(select(path, nextind + 1), select(path, nextind))], zeros)
        thispath = unit([a - b for a, b in zip(select(path, nextind), select(path, nextind - 1))], zeros)
        lastpath = unit([a - b for a, b in zip(select(path, nextind - 1), select(path, nextind - 2))], zeros)
        if nextind == len(path) and not closed:
            nextdir = lastpath
        elif (nextind <= len(path) - 2 or closed) and approx(cuts[ind][0], select(path, nextind), eps=eps):
            nextdir = unit([a + b for a, b in zip(nextpath, thispath)])
        elif (nextind > 1 or closed) and approx(cuts[ind][0], select(path, nextind - 1), eps=eps):
            nextdir = unit([a + b for a, b in zip(thispath, lastpath)])
        else:
            nextdir = thispath
        out.append(nextdir)
    return out


def _cut_to_seg_u_form(pathcut, path, closed: bool) -> list:
    """Convert path_cut_points() output to [segment, u] form usable with _path_select()."""
    lastind = len(path) - (0 if closed else 1)
    out = []
    for entry in pathcut:
        if entry[1] > lastind:
            out.append([lastind, 0])
            continue
        a, b, c = path[entry[1] - 1], path[entry[1]], entry[0]
        diffs = [abs(b[k] - a[k]) for k in range(len(a))]
        i = diffs.index(max(diffs))
        out.append([entry[1] - 1, (c[i] - a[i]) / (b[i] - a[i])])
    return out


# ---------------------------------------------------------------------------
# Section: Splitting self-intersecting polygons into simple polygons
# ---------------------------------------------------------------------------


def split_path_at_self_crossings(path, closed: bool = True, eps: float = EPSILON) -> list:
    """Split a 2D *path* into subpaths wherever it crosses itself."""
    path = force_path(path)
    assert is_path(path, dim=(2,)), "Must give a 2D path"
    path = cleanup_path(path, eps=eps)
    raw = []
    for a in _path_self_intersections(path, closed=closed, eps=eps):
        raw.append([a[1], a[2]])
        raw.append([a[3], a[4]])
    raw.sort(key=lambda x: (x[0], x[1]))
    isects = deduplicate([[0, 0]] + raw + [[len(path) - (1 if closed else 2), 1]], eps=eps)
    out = []
    for p0, p1 in pair(isects):
        section = _path_select(path, p0[0], p0[1], p1[0], p1[1], closed=closed)
        outpath = deduplicate(section, eps=eps)
        if len(outpath) > 1:
            out.append(outpath)
    return out


def _tag_self_crossing_subpaths(path, nonzero: bool, closed: bool = True, eps: float = EPSILON) -> list:
    subpaths = split_path_at_self_crossings(path, closed=True, eps=eps)
    out = []
    for subpath in subpaths:
        seg = select(subpath, 0, 1)
        mp = np.asarray(seg, dtype=float).mean(axis=0)
        n = [x / 2048 for x in line_normal(seg[0], seg[1])]
        p1 = [mp[0] + n[0], mp[1] + n[1]]
        p2 = [mp[0] - n[0], mp[1] - n[1]]
        p1in = point_in_polygon(p1, path, nonzero=nonzero) >= 0
        p2in = point_in_polygon(p2, path, nonzero=nonzero) >= 0
        tag = "I" if (p1in and p2in) else "O"
        out.append([tag, subpath])
    return out


def polygon_parts(poly, nonzero: bool = False, eps: float = EPSILON) -> list:
    """Split a possibly self-intersecting 2D polygon into a list of non-intersecting simple polygons."""
    poly = force_path(poly)
    assert is_path(poly, dim=(2,)), "Must give 2D polygon"
    poly = cleanup_path(poly, eps=eps)
    tagged = _tag_self_crossing_subpaths(poly, nonzero=nonzero, closed=True, eps=eps)
    kept = [sub[1] for sub in tagged if sub[0] == "O"]
    return _assemble_path_fragments(kept, eps=eps)


def _modang(x: float) -> float:
    xx = x % 360
    return xx - 360 if xx > 180 else xx


def _extreme_angle_fragment(seg, fragments: list, rightmost: bool = True, eps: float = EPSILON):
    if not fragments:
        return [None, []]
    delta = [seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]]
    segang = math.degrees(math.atan2(delta[1], delta[0]))
    frags = []
    for fragment in fragments:
        fwdmatch = approx(seg[1], fragment[0], eps=eps)
        bakmatch = approx(seg[1], fragment[-1], eps=eps)
        frags.append([fwdmatch, bakmatch, list(reversed(fragment)) if bakmatch else fragment])
    angs = []
    for fwdmatch, bakmatch, frag in frags:
        if fwdmatch or bakmatch:
            delta2 = [frag[1][0] - frag[0][0], frag[1][1] - frag[0][1]]
            segang2 = math.degrees(math.atan2(delta2[1], delta2[0]))
            angs.append(_modang(segang2 - segang))
        else:
            angs.append(999 if rightmost else -999)
    fi = min_index(angs) if rightmost else max_index(angs)
    if abs(angs[fi]) > 360:
        return [None, fragments]
    remainder = [fragments[i] for i in range(len(fragments)) if i != fi]
    return [frags[fi][2], remainder]


def _assemble_a_path_from_fragments(fragments: list, rightmost: bool = True, startfrag: int = 0, eps: float = EPSILON) -> list:
    """Assemble *fragments* into one closed polygon path; returns [path, remaining_fragments]."""
    if len(fragments) == 0:
        return [[], []]
    if len(fragments) == 1:
        return [fragments[0], []]
    path = fragments[startfrag]
    remainder = [fragments[i] for i in range(len(fragments)) if i != startfrag]
    while True:
        if is_closed_path(path, eps=eps):
            return [path, remainder]
        seg = select(path, -2, -1)
        foundfrag, remainder2 = _extreme_angle_fragment(seg, remainder, rightmost=rightmost, eps=eps)
        if foundfrag is None:
            return [path, remainder2]
        if is_closed_path(foundfrag, eps=eps):
            return [foundfrag, [path] + remainder2]
        fragend = foundfrag[-1]
        hits = [i for i in range(len(path) - 1) if approx(path[i], fragend, eps=eps)]
        if hits:
            hitidx = hits[-1]
            newpath = list_head(path, hitidx)
            newfrags = ([newpath] if len(newpath) > 1 else []) + remainder2
            outpath = slice(path, hitidx, -2) + foundfrag
            return [outpath, newfrags]
        path = path + list_tail(foundfrag)
        remainder = remainder2


def _assemble_path_fragments(fragments: list, eps: float = EPSILON) -> list:
    """Assemble *fragments* into complete closed polygon paths, discarding any with area < eps."""
    finished = []
    frags = fragments
    while len(frags) > 0:
        minxidx = min_index([min(pt[0] for pt in frag) for frag in frags])
        result_l = _assemble_a_path_from_fragments(frags, startfrag=minxidx, rightmost=False, eps=eps)
        result_r = _assemble_a_path_from_fragments(frags, startfrag=minxidx, rightmost=True, eps=eps)
        l_area = abs(polygon_area(result_l[0])) if result_l[0] else 0
        r_area = abs(polygon_area(result_r[0])) if result_r[0] else 0
        result = result_l if l_area < r_area else result_r
        newpath = cleanup_path(result[0])
        remainder = result[1]
        if min(l_area, r_area) >= eps:
            finished.append(newpath)
        frags = remainder
    return finished
