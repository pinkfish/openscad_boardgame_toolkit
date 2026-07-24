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
#    bosl2/vectors.py, bosl2/comparisons.py and bosl2/geometry.py (also
#    pure-Python ports), the same way paths.scad depends on math.scad/
#    vectors.scad/comparisons.scad/geometry.scad. The lists.scad helpers it
#    needs (select/pair/list_head/list_tail/slice) are private staticmethods
#    on Path rather than a separate module.
#
#    Every path operation lives on the :class:`Path` class -- there are no
#    module-level path functions. The public ergonomic API is instance
#    methods/properties (``Path(pts).offset(...)``, ``path.is_closed``); the
#    numeric kernels and graph algorithms are private ``@staticmethod``s on
#    the same class so they can also run on raw point arrays that are not
#    ``Path`` instances (e.g. the 3-D paths bosl2/shapes3d.py's path_text()
#    feeds through ``Path._path_length()`` / ``Path._path_cut_points()``).
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
from typing import Any
import math

import numpy as np

from bosl2.math import EPSILON, lerp, lerpn, deriv, deriv2, deriv3
from bosl2.vectors import is_vector, add_scalar, unit
from bosl2.comparisons import approx
from bosl2.geometry import line_normal, line_closest_point, pointlist_bounds, _is_point_on_segment, is_collinear, cross, general_line_intersection
from bosl2.distributors import Distributable, _apply4  # the distributors.scad copiers, as methods
from bosl2.miscellaneous import Extrudable  # path_extrude / path_extrude2d, as methods
from bosl2.rounding import Roundable  # round_corners / smooth_path, as methods


# ---------------------------------------------------------------------------
# Section: Path object
# ---------------------------------------------------------------------------
#
# The object form of every paths.scad operation. It lives here (not in
# bosl2/regions.py) so the path operations and the class that carries them are
# one module; bosl2/regions.py re-exports Path for backwards compatibility and
# keeps the Region class.


class Path(Distributable, Extrudable, Roundable, list):
    """A 2-D path: a list of [x, y] points, with every path operation as a method.

    Subclasses ``list`` deliberately -- the same trick as :class:`base_bgtk.Vec3`. Every place
    that already treats a path as a plain point list (indexing, iteration, ``len()``, equality
    with a plain list, and crossing the native ``polygon()``/FFI boundary) keeps working, so
    this is a drop-in for the raw lists the toolkit passes around, while giving the chained
    object form for new code::

        Path([[0, 0], [80, 0], [80, 60], [0, 60]]).offset(r=-2).round_corners(radius=1).polygon()

    Because it IS a list, ``isinstance(x, Path)`` is the type check that replaced the old
    ``is_path()``/``is_region()`` guards. Every method returns a NEW Path (or list/array) --
    nothing mutates in place, so a path can be reused as the base for several derived outlines.

    All of BOSL2's paths.scad operations are methods here; there are no module-level path
    functions. The public ergonomic operations are instance methods/properties. The numeric
    kernels and graph algorithms are private ``@staticmethod``s (``_path_length``,
    ``_path_cut_points``, ...) so they can also be applied to raw point arrays that are not
    ``Path`` instances -- notably the 3-D paths that only ``bosl2/shapes3d.py``'s path_text()
    handles, which this 2-D class cannot wrap.

    Args:
        points: the [x, y] points (anything array-like; numpy scalars are converted to float)
        closed: whether the path is a closed polygon (default True)

    Examples:
        A box outline inset by the wall thickness and with rounded corners, extruded into a plate:

        .. pythonscad-example::

            outline = Path([[0, 0], [80, 0], [80, 60], [0, 60]])
            plate = outline.offset(r=-3).round_corners(radius=5).polygon().linear_extrude(height=4)
            plate.show()
    """

    def __init__(self, points: Sequence = (), closed: bool = True) -> None:
        pts = np.asarray(list(points), dtype=float)
        if pts.size == 0:
            super().__init__()
        else:
            assert pts.ndim == 2 and pts.shape[1] == 2, f"Path needs [x, y] points, got shape {pts.shape}"
            # plain floats: the native polygon()/FFI boundary rejects numpy scalars
            super().__init__([[float(x), float(y)] for x, y in pts])
        self.closed = closed

    def _like(self, points) -> "Path":
        return Path(points, closed=self.closed)

    @property
    def array(self) -> np.ndarray:
        """The points as an (N, 2) numpy array, for doing your own vectorised maths."""
        return np.asarray(self, dtype=float)

    # -- measurement -----------------------------------------------------------------------

    def bounds(self) -> np.ndarray:
        """[[min_x, min_y], [max_x, max_y]]."""
        pts = self.array
        return np.array([pts.min(axis=0), pts.max(axis=0)])

    @property
    def width(self) -> float:
        b = self.bounds()
        return float(b[1][0] - b[0][0])

    @property
    def length_y(self) -> float:
        b = self.bounds()
        return float(b[1][1] - b[0][1])

    def area(self, signed: bool = False) -> float:
        """Enclosed area; *signed* keeps the sign (negative == clockwise)."""
        return float(Path._polygon_area(self, signed=signed))

    def is_clockwise(self) -> bool:
        return self.area(signed=True) < 0

    def perimeter(self) -> float:
        """Total length around the path."""
        return float(Path._path_length(self, closed=self.closed))

    length = perimeter

    def segment_lengths(self) -> np.ndarray:
        """Length of each segment, as an ndarray."""
        return Path._path_segment_lengths(self, closed=self.closed)

    def length_fractions(self) -> np.ndarray:
        """Cumulative length fraction at each point, as an ndarray."""
        return Path._path_length_fractions(self, closed=self.closed)

    def contains(self, point: Sequence[float]) -> bool:
        """True if *point* is inside the closed polygon (on the boundary counts as inside).

        Containment is only meaningful for a closed polygon, so an open path (``closed=False``)
        always returns False rather than testing.
        """
        if not self.closed:
            return False
        return Path._point_in_polygon(point, self) >= 0

    @property
    def is_closed(self) -> bool:
        """True if the first and last points of the path coincide."""
        return bool(Path._is_closed_path(self))

    def is_simple(self) -> bool:
        """True if the path does not self-intersect."""
        return Path._is_path_simple(self, closed=self.closed)

    def closest_point(self, pt: Sequence[float]) -> list:
        """[SEGNUM, POINT]: the closest path segment to *pt*, and the closest point on it."""
        return Path._path_closest_point(self, pt, closed=self.closed)

    def tangents(self, uniform: bool = True) -> np.ndarray:
        """Unit tangent at each point, as an ndarray."""
        return Path._path_tangents(self, closed=self.closed, uniform=uniform)

    def normals(self, tangents=None) -> np.ndarray:
        """Unit normal at each point, as an ndarray."""
        return Path._path_normals(self, tangents=tangents, closed=self.closed)

    def curvature(self) -> np.ndarray:
        """Curvature at each point, as an ndarray."""
        return Path._path_curvature(self, closed=self.closed)

    def torsion(self) -> np.ndarray:
        """Numeric torsion estimate of a 3-D path at each point, as an ndarray."""
        return Path._path_torsion(self, closed=self.closed)

    def cut_points(self, cutdist, direction: bool = False):
        """Point(s) at the given distance(s) along the path."""
        return Path._path_cut_points(self, cutdist, closed=self.closed, direction=direction)

    # -- derived paths ---------------------------------------------------------------------

    def offset(self, r: float | None = None, delta: float | None = None, chamfer: bool = False,
               _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> "Path":
        """Offset by *r* (rounded joins) or *delta* (sharp/chamfered). See :meth:`_offset`.

        Prefer ``.polygon().offset(...)`` (native, Manifold-side) when you only need geometry;
        this is for when the result is needed as points.
        """
        return self._like(Path._offset(self, r=r, delta=delta, chamfer=chamfer,
                                        closed=self.closed, _fn=_fn, _fa=_fa, _fs=_fs))

    # round_corners() and smooth_path() come from the Roundable mixin (bosl2/rounding.py), which
    # supports the circle / smooth / chamfer methods and 2-D/3-D paths. The circle+radius case is
    # bit-identical to the old _round_corners kernel kept below.

    def merge_collinear(self) -> "Path":
        """Drop points that lie on a straight run."""
        return self._like(Path._path_merge_collinear(self, closed=self.closed))

    def close(self) -> "Path":
        """Append the start point if the path isn't already closed."""
        return self._like(Path._close_path(self))

    def cleanup(self) -> "Path":
        """Drop a duplicate closing point if present."""
        return self._like(Path._cleanup_path(self))

    def reversed_path(self) -> "Path":
        """The same outline wound the other way."""
        return self._like(list(reversed(self)))

    def deduplicated(self) -> "Path":
        """Drop consecutive repeated points (:meth:`_deduplicate`)."""
        return self._like(Path._deduplicate(self, closed=self.closed))

    def subdivide(self, **kwargs: Any) -> "Path":
        """Insert points along the path."""
        return self._like(Path._subdivide_path(self, closed=self.closed, **kwargs))

    def resample(self, **kwargs: Any) -> "Path":
        """Resample to evenly spaced points."""
        return self._like(Path._resample_path(self, closed=self.closed, **kwargs))

    def cut(self, cutdist) -> list["Path"]:
        """Split the path at the given distance(s), returning the sub-paths."""
        return [self._like(sub) for sub in Path._path_cut(self, cutdist, closed=self.closed)]

    def split_at_self_crossings(self, eps: float = EPSILON) -> list["Path"]:
        """Split this 2-D path into subpaths wherever it crosses itself."""
        return [self._like(sub) for sub in Path._split_path_at_self_crossings(self, closed=self.closed, eps=eps)]

    def polygon_parts(self, nonzero: bool = False, eps: float = EPSILON) -> list["Path"]:
        """Split a possibly self-intersecting polygon into non-intersecting simple polygons."""
        poly = Path._cleanup_path(self, eps=eps)
        tagged = Path._tag_self_crossing_subpaths(poly, nonzero=nonzero, closed=True, eps=eps)
        kept = [sub[1] for sub in tagged if sub[0] == "O"]
        return [self._like(part) for part in Path._assemble_path_fragments(kept, eps=eps)]

    # -- transforms ------------------------------------------------------------------------
    #
    # The BOSL2 transforms.scad point-list operations, as methods. All operate in 2-D and
    # return a NEW Path. Directions follow BOSL2: right/left are +/-X, back is +Y and
    # forward/fwd is -Y.

    def translate(self, v: Sequence[float]) -> "Path":
        """Translate every point by *v* (2-D; a 1-vector shifts X only)."""
        pts = self.array
        vv = np.zeros(2)
        v = np.asarray(v, dtype=float)
        vv[: min(2, len(v))] = v[: min(2, len(v))]
        return self._like(pts + vv)

    move = translate

    def rot(self, a: float) -> "Path":
        """Rotate every point by *a* degrees about the origin (Z axis)."""
        rad = math.radians(a)
        c, s = math.cos(rad), math.sin(rad)
        rotmat = np.array([[c, -s], [s, c]])
        return self._like(self.array @ rotmat.T)

    rotate = rot

    def mirror(self, v: Sequence[float]) -> "Path":
        """Reflect every point across the line through the origin with normal *v*."""
        n = np.asarray(v, dtype=float)
        n = n / np.linalg.norm(n)
        pts = self.array
        d = pts @ n
        return self._like(pts - 2 * np.outer(d, n))

    def yflip(self, y: float = 0.0) -> "Path":
        """Reflect every point across the horizontal line Y=*y* (default: the X axis)."""
        pts = self.array.copy()
        pts[:, 1] = 2 * y - pts[:, 1]
        return self._like(pts)

    def right(self, x: float) -> "Path":
        """Translate by *x* along +X."""
        return self.translate([x, 0.0])

    def left(self, x: float) -> "Path":
        """Translate by *x* along -X."""
        return self.translate([-x, 0.0])

    def back(self, y: float) -> "Path":
        """Translate by *y* along +Y."""
        return self.translate([0.0, y])

    def forward(self, y: float) -> "Path":
        """Translate by *y* along -Y (BOSL2 fwd())."""
        return self.translate([0.0, -y])

    fwd = forward

    # -- conversion ------------------------------------------------------------------------

    def to_region(self):
        """This path as a single-outline Region."""
        from bosl2.regions import Region  # local: Region imports Path from here

        return Region([self])

    def polygon(self):
        """Native 2-D geometry for this path (crosses the FFI as plain floats)."""
        from pythonscad import polygon as _polygon

        return _polygon([[float(x), float(y)] for x, y in self])

    def geometry(self):
        """Native 2-D geometry -- the name :class:`Region` also exposes, so a caller that may
        hold either a Path or a Region can ask for geometry without checking which it got."""
        return self.polygon()

    # -- drawing (bosl2/drawing.py) --------------------------------------------------------

    def stroke(self, width: float = 1, closed: bool | None = None, **kwargs: Any):
        """Draw this path as a solid line of the given *width* (see :func:`bosl2.drawing.stroke`)."""
        from bosl2.drawing import stroke as _stroke

        return _stroke(self, width=width, closed=self.closed if closed is None else closed, **kwargs)

    def dashed_stroke(self, dashpat: Sequence[float] = (3, 3), closed: bool | None = None,
                      **kwargs: Any) -> list["Path"]:
        """Break this path into dash sub-paths (see :func:`bosl2.drawing.dashed_stroke`)."""
        from bosl2.drawing import dashed_stroke as _dashed

        return _dashed(self, dashpat=dashpat, closed=self.closed if closed is None else closed, **kwargs)

    # -- distributors (bosl2/distributors.py) ----------------------------------------------

    def _distribute(self, mats) -> list["Path"]:
        """Apply each copier matrix, returning the list of 2-D copies (BOSL2's function form).

        Raises if a copier would lift the 2-D path out of the XY plane -- use :class:`Path3D` for
        those (``zcopies``, ``xrot_copies``, ``sphere_copies``, ...).
        """
        if not len(self):
            return [self._like([]) for _ in mats]
        pts3 = np.hstack([self.array, np.zeros((len(self), 1))])
        out = []
        for m in mats:
            res = _apply4(m, pts3)
            assert float(np.max(np.abs(res[:, 2]))) < 1e-7, \
                "this copier moves the 2-D path out of the XY plane; convert to Path3D first"
            out.append(self._like(res[:, :2]))
        return out

    def __repr__(self) -> str:
        return f"Path({len(self)} pts, closed={self.closed})"

    # ======================================================================================
    # Private static kernels -- the numeric/graph implementations of paths.scad. They take a
    # raw path (any list/ndarray of points, 2-D or 3-D) and an explicit ``closed`` so they can
    # run on data that is not a Path instance; the instance methods above are thin wrappers.
    # ======================================================================================

    # -- List helpers ----------------------------------------------------------------------
    #
    # The handful of BOSL2 lists.scad/linalg.scad helpers the path algorithms need, done with
    # standard Python list indexing/slicing. Their circular (``_select``) and inclusive-clamped
    # (``_slice``) index semantics are BOSL2's, which plain slicing does not reproduce, so they
    # live here as small static helpers rather than being spelled out at every call site.

    @staticmethod
    def _select(lst, start, end=None):
        """Circular list indexing/slicing (BOSL2 Path._select()).

        ``_select(lst, i)`` returns ``lst[i]`` wrapping i modulo len; ``_select(lst, [i, ...])``
        returns the wrapped elements; ``_select(lst, s, e)`` returns the inclusive circular slice
        from s to e, wrapping past the end when s > e.
        """
        n = len(lst)
        if n == 0:
            return []
        if end is None:
            if isinstance(start, (list, tuple)):
                return [lst[i % n] for i in start]
            return lst[start % n]
        assert isinstance(start, int), "_select(): slice form needs integer start"
        s = start % n
        e = end % n
        if s <= e:
            return [lst[i] for i in range(s, e + 1)]
        return [lst[i] for i in range(s, n)] + [lst[i] for i in range(0, e + 1)]

    @staticmethod
    def _pair(lst, wrap: bool = False) -> list:
        """List of consecutive (lst[i], lst[i+1]) pairs; if *wrap*, also (last, first)."""
        length = len(lst) - 1
        if length < 1:
            return []
        out = [(lst[i], lst[i + 1]) for i in range(length)]
        if wrap:
            out.append((lst[length], lst[0]))
        return out

    @staticmethod
    def _list_head(lst, to: int = -2) -> list:
        """Elements of *lst* up to and including index *to* (BOSL2 Path._list_head())."""
        if to < 0:
            return lst[: len(lst) + to + 1]
        if to < len(lst):
            return lst[: to + 1]
        return list(lst)

    @staticmethod
    def _list_tail(lst, frm: int = 1) -> list:
        """Elements of *lst* starting at index *frm* (may be negative; BOSL2 Path._list_tail())."""
        if frm < 0:
            frm = frm + len(lst)
        if frm < 0:
            return list(lst)
        return lst[frm:]

    @staticmethod
    def _slice(lst, start: int = 0, end: int = -1) -> list:
        """``lst[start..end]`` inclusive, negative indices from the end, clamped (BOSL2 Path._slice())."""
        if not lst:
            return []
        length = len(lst)
        s = max(0, min(length - 1, start + (length if start < 0 else 0)))
        e = max(0, min(length - 1, end + (length if end < 0 else 0)))
        if e < s:
            return []
        return lst[s : e + 1]

    @staticmethod
    def _repeat(val, n: int) -> list:
        """*val* repeated *n* times."""
        return [val for _ in range(n)]

    @staticmethod
    def _deduplicate(lst, closed: bool = False, eps: float = EPSILON) -> list:
        """Remove consecutive (approximately) duplicate entries from *lst* (BOSL2 deduplicate()).

        If *closed*, the last entry is also compared (wrapping) against the first; otherwise the
        true last entry is always kept.
        """
        length = len(lst)
        if length == 0:
            return []
        end = length if closed else length - 1
        out = []
        for i in range(length):
            if i == end:
                out.append(lst[i])
                continue
            nxt = lst[(i + 1) % length]
            differs = (not np.array_equal(lst[i], nxt)) if eps == 0 else (not approx(lst[i], nxt, eps))
            if differs:
                out.append(lst[i])
        return out

    # -- Polygon area / point-in-polygon (BOSL2 geometry.scad) -----------------------------

    @staticmethod
    def _polygon_area(poly, signed: bool = False) -> float:
        """Area of a 2-D polygon (shoelace formula). Only 2-D polygons are supported."""
        arr = np.asarray(poly, dtype=float)
        n = len(arr)
        if n < 3:
            return 0.0
        p0 = arr[0]
        rest = arr[1:] - p0
        total = float(np.sum(rest[:-1, 0] * rest[1:, 1] - rest[1:, 0] * rest[:-1, 1])) / 2
        return total if signed else abs(total)

    @staticmethod
    def _point_in_polygon(point, poly, nonzero: bool = False, eps: float = EPSILON) -> int:
        """Test whether *point* is inside 2-D polygon *poly*: 1 inside, -1 outside, 0 boundary."""
        point = np.asarray(point, dtype=float)
        box = pointlist_bounds(poly)
        if point[0] < box[0][0] - eps or point[0] > box[1][0] + eps or point[1] < box[0][1] - eps or point[1] > box[1][1] + eps:
            return -1

        poly = np.asarray(poly, dtype=float)
        n = len(poly)
        segs = [(poly[i], poly[(i + 1) % n]) for i in range(n)]

        for seg in segs:
            if float(np.linalg.norm(seg[1] - seg[0])) > eps and _is_point_on_segment(point, seg, eps=eps):
                return 0

        if nonzero:
            winding = 0
            for seg in segs:
                p0 = seg[0] - point
                p1 = seg[1] - point
                if float(np.linalg.norm(p1 - p0)) <= eps:
                    continue
                if p0[1] <= 0:
                    if p1[1] > 0 and cross(p0, p1 - p0) > 0:
                        winding += 1
                else:
                    if p1[1] <= 0 and cross(p0, p1 - p0) < 0:
                        winding -= 1
            return 1 if winding != 0 else -1

        crossings = 0
        for seg in segs:
            p0 = seg[0] - point
            p1 = seg[1] - point
            if (p1[1] > eps and p0[1] <= eps) or (p1[1] <= eps and p0[1] > eps):
                if -eps < p0[0] - p0[1] * (p1[0] - p0[0]) / (p1[1] - p0[1]):
                    crossings += 1
        return 2 * (crossings % 2) - 1

    # -- Utility ---------------------------------------------------------------------------

    @staticmethod
    def _is_closed_path(path, eps: float = EPSILON) -> bool:
        """True if the first and last points of *path* coincide."""
        return approx(path[0], path[-1], eps=eps)

    @staticmethod
    def _close_path(path, eps: float = EPSILON) -> list:
        """Append the start point to *path* if it isn't already closed."""
        return path if Path._is_closed_path(path, eps=eps) else list(path) + [path[0]]

    @staticmethod
    def _cleanup_path(path, eps: float = EPSILON) -> list:
        """Drop the last point of *path* if it coincides with the first."""
        return path[:-1] if Path._is_closed_path(path, eps=eps) else path

    @staticmethod
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

    @staticmethod
    def _path_merge_collinear(path, closed: bool | None = None, eps: float = EPSILON) -> list:
        """Remove unnecessary sequential collinear points from *path* (or 1-region)."""
        if closed is None:
            closed = False
        if len(path) <= 2:
            return path
        indices = [0]
        end = len(path) - (1 if closed else 2)
        for i in range(1, end + 1):
            if not is_collinear(path[i - 1], path[i], Path._select(path, i + 1), eps=eps):
                indices.append(i)
        if not closed:
            indices.append(len(path) - 1)
        return [path[i] for i in indices]

    # -- Path length calculation -----------------------------------------------------------

    @staticmethod
    def _path_length(path, closed: bool | None = None) -> float:
        """Total length of *path* (or 1-region)."""
        if closed is None:
            closed = False
        if len(path) < 2:
            return 0
        arr = np.asarray(path, dtype=float)
        total = float(np.linalg.norm(np.diff(arr, axis=0), axis=1).sum())
        if closed:
            total += float(np.linalg.norm(arr[-1] - arr[0]))
        return total

    @staticmethod
    def _path_segment_lengths(path, closed: bool | None = None) -> np.ndarray:
        """Length of each segment of *path* (or 1-region), as an ndarray."""
        if closed is None:
            closed = False
        arr = np.asarray(path, dtype=float)
        lens = np.linalg.norm(np.diff(arr, axis=0), axis=1)
        if closed:
            lens = np.append(lens, np.linalg.norm(arr[0] - arr[-1]))
        return lens

    @staticmethod
    def _path_length_fractions(path, closed: bool | None = None) -> np.ndarray:
        """Distance fraction of each point in *path* along the path (0 at the start, 1 at the end)."""
        if closed is None:
            closed = False
        lengths = np.concatenate(([0.0], Path._path_segment_lengths(path, closed)))
        partial = np.cumsum(lengths)
        total = partial[-1]
        return partial / total

    @staticmethod
    def _path_self_intersections(path, closed: bool = True, eps: float = EPSILON) -> list:
        """All self-intersection points of *path*: list of [POINT, SEGNUM1, PROPORTION1, SEGNUM2, PROPORTION2]."""
        p = Path._close_path(path, eps=eps) if closed else path
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

    # -- Resampling -- changing the number of points in a path -----------------------------

    @staticmethod
    def _scad_round(x: float) -> float:
        """Round half away from zero, matching OpenSCAD's round() (unlike Python's round-half-to-even)."""
        return math.floor(x + 0.5) if x >= 0 else math.ceil(x - 0.5)

    @staticmethod
    def _sum_preserving_round(data: Sequence[float]) -> list[float]:
        """Round every entry to an integer, carrying the rounding error forward so the sum is preserved."""
        out = list(data)
        error = 0.0
        for i in range(len(out) - 1):
            newval = Path._scad_round(out[i] + error)
            error = out[i] + error - newval
            out[i] = newval
        out[-1] = Path._scad_round(out[-1] + error)
        return out

    @staticmethod
    def _subdivide_path(path, n=None, refine=None, maxlen=None, closed: bool = True, exact: bool | None = None, method: str | None = None) -> list:
        """Subdivide *path* to produce a more finely sampled path; see BOSL2 subdivide_path() for the full option set."""
        assert sum(x is not None for x in (n, refine, maxlen)) == 1, "Must give exactly one of n, refine, and maxlen"
        if refine == 1 or n == len(path):
            return path
        if maxlen is not None:
            assert method is None, "Cannot give method with maxlen"
            assert exact is None, "Cannot give exact with maxlen"
            out = []
            for p0, p1 in Path._pair(path, closed):
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
                add_guess = Path._repeat((n - len(path)) / count, count)
        else:
            assert isinstance(n, (int, float)), 'Parameter n to subdivide path must be a number when method="length"'
            path_lens = Path._path_segment_lengths(path, closed)
            add_density = (n - len(path)) / sum(path_lens)
            add_guess = [ln * add_density for ln in path_lens]
        add_list = [float(v) for v in add_guess]
        add = Path._sum_preserving_round(add_list) if exact else [Path._scad_round(v) for v in add_list]
        out = []
        for i in range(count):
            out.extend(lerpn(path[i], Path._select(path, i + 1), 1 + int(add[i]), endpoint=False))
        if not closed:
            out.append(path[-1])
        return out

    @staticmethod
    def _resample_path(path, n=None, spacing=None, closed: bool = True) -> list:
        """Uniformly resample *path* to *n* points, or to a spacing near *spacing*."""
        assert (n is None) != (spacing is None), "Must define exactly one of n and spacing"
        length = Path._path_length(path, closed)
        if n is not None:
            n_use = n - (0 if closed else 1)
        else:
            assert spacing is not None
            n_use = round(length / spacing)
        distlist = lerpn(0, length, n_use, endpoint=False)
        cuts = Path._path_cut_points(path, distlist, closed=closed)
        out = [c[0] for c in cuts]
        if not closed:
            out.append(path[-1])
        return out

    # -- Path Geometry ---------------------------------------------------------------------

    @staticmethod
    def _is_path_simple(path, closed: bool | None = None, eps: float = EPSILON) -> bool:
        """True if the 2D *path* has no self-intersections (repeated points are not considered intersections)."""
        if closed is None:
            closed = False
        arr = np.asarray(path, dtype=float)
        n = len(arr)
        end = n - (2 if closed else 3)
        for i in range(0, end + 1):
            v1 = arr[i + 1] - arr[i]
            v2 = arr[(i + 2) % n] - arr[i + 1]
            n1, n2 = float(np.hypot(*v1)), float(np.hypot(*v2))
            if n1 > 0 and n2 > 0 and approx(float(v1 @ v2) / (n1 * n2), -1):
                return False
        return len(Path._path_self_intersections(path, closed=closed, eps=eps)) == 0

    @staticmethod
    def _path_closest_point(path, pt: Sequence[float], closed: bool = True) -> list:
        """[SEGNUM, POINT]: the closest path segment to *pt*, and the closest point (an ndarray) on it."""
        pts = [line_closest_point(seg, pt) for seg in Path._pair(path, closed)]
        dists = np.linalg.norm(np.asarray(pts, dtype=float) - np.asarray(pt, dtype=float), axis=1)
        min_seg = int(np.argmin(dists))
        return [min_seg, pts[min_seg]]

    @staticmethod
    def _path_tangents(path, closed: bool | None = None, uniform: bool = True) -> np.ndarray:
        """Normalized tangent vector at each point of *path*, as an ndarray."""
        if closed is None:
            closed = False
        if not uniform:
            d = np.asarray(deriv(path, closed=closed, h=Path._path_segment_lengths(path, closed)), dtype=float)
        else:
            d = np.asarray(deriv(path, closed=closed), dtype=float)
        norms = np.linalg.norm(d, axis=1, keepdims=True)
        assert np.all(norms.ravel() > EPSILON), "Cannot normalize a zero vector"
        return d / norms

    @staticmethod
    def _path_normals(path, tangents=None, closed: bool | None = None) -> np.ndarray:
        """Normal vector (perpendicular to the tangent, in the plane of the curve) at each point of *path*, as an ndarray."""
        if closed is None:
            closed = False
        if tangents is None:
            tangents = Path._path_tangents(path, closed)
        dim = len(path[0])
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

    @staticmethod
    def _path_curvature(path, closed: bool | None = None) -> np.ndarray:
        """Numeric curvature estimate of *path* at each point, as an ndarray."""
        if closed is None:
            closed = False
        d1 = np.asarray(deriv(path, closed=closed), dtype=float)
        d2 = np.asarray(deriv2(path, closed=closed), dtype=float)
        n1 = np.linalg.norm(d1, axis=1)
        n2 = np.linalg.norm(d2, axis=1)
        dot = np.einsum("ij,ij->i", d1, d2)
        val = np.clip((n1 * n2) ** 2 - dot**2, 0.0, None)
        return np.sqrt(val) / n1**3

    @staticmethod
    def _path_torsion(path, closed: bool = False) -> np.ndarray:
        """Numeric torsion estimate of a 3D *path* at each point, as an ndarray."""
        d1 = np.asarray(deriv(path, closed=closed), dtype=float)
        d2 = np.asarray(deriv2(path, closed=closed), dtype=float)
        d3 = np.asarray(deriv3(path, closed=closed), dtype=float)
        crossterm = np.cross(d1, d2)
        dot = np.einsum("ij,ij->i", crossterm, d3)
        denom = np.einsum("ij,ij->i", crossterm, crossterm)
        return dot / denom

    # -- Breaking paths up into subpaths ---------------------------------------------------

    @staticmethod
    def _path_cut(path, cutdist, closed: bool | None = None) -> list:
        """Cut *path* into subpaths at the given ascending list of distances (or a single distance)."""
        if isinstance(cutdist, (int, float)):
            return Path._path_cut(path, [cutdist], closed)
        if closed is None:
            closed = False
        assert isinstance(cutdist, (list, tuple, np.ndarray))
        assert cutdist[-1] < Path._path_length(path, closed=closed), "Cut distances must be smaller than the path length"
        assert cutdist[0] > 0, "Cut distances must be strictly positive"
        cutlist = Path._path_cut_points(path, cutdist, closed=closed)
        return Path._path_cut_getpaths(path, cutlist, closed)

    @staticmethod
    def _path_cut_getpaths(path, cutlist, closed: bool) -> list:
        cuts = len(cutlist)
        result = []
        seg0 = list(Path._list_head(path, cutlist[0][1] - 1))
        if not approx(cutlist[0][0], path[cutlist[0][1] - 1]):
            seg0.append(cutlist[0][0])
        result.append(seg0)
        for i in range(cuts - 1):
            if np.array_equal(cutlist[i][0], cutlist[i + 1][0]) and cutlist[i][1] == cutlist[i + 1][1]:
                result.append([])
                continue
            seg = []
            if not approx(cutlist[i][0], Path._select(path, cutlist[i][1])):
                seg.append(cutlist[i][0])
            seg.extend(Path._slice(path, cutlist[i][1], cutlist[i + 1][1] - 1))
            if not approx(cutlist[i + 1][0], Path._select(path, cutlist[i + 1][1] - 1)):
                seg.append(cutlist[i + 1][0])
            result.append(seg)
        last_seg = []
        if not approx(cutlist[cuts - 1][0], Path._select(path, cutlist[cuts - 1][1])):
            last_seg.append(cutlist[cuts - 1][0])
        last_seg.extend(Path._select(path, cutlist[cuts - 1][1], 0 if closed else -1))
        result.append(last_seg)
        return result

    @staticmethod
    def _path_cut_points(path, cutdist, closed: bool = False, direction: bool = False):
        """Cut *path* at the given distance(s) from the start; returns [[point, next_index], ...] (or a single entry if *cutdist* is a scalar)."""
        long_enough = len(path) >= (3 if closed else 2)
        assert long_enough, "Two points needed to define a path" if len(path) < 2 else "Closed path must include three points"
        if isinstance(cutdist, (int, float, np.floating, np.integer)):
            return Path._path_cut_points(path, [cutdist], closed, direction)[0]
        assert isinstance(cutdist, (list, tuple, np.ndarray))
        assert all(cutdist[i] < cutdist[i + 1] for i in range(len(cutdist) - 1)), "Cut distances must be an increasing list"
        cuts = Path._path_cut_points_recurse(path, [float(v) for v in cutdist], closed)
        if not direction:
            return cuts
        dirs = Path._path_cuts_dir(path, cuts, closed)
        normals = Path._path_cuts_normals(path, cuts, dirs, closed)
        return [[cuts[i][0], cuts[i][1], dirs[i], normals[i]] for i in range(len(cuts))]

    @staticmethod
    def _path_cut_points_recurse(path, dists: Sequence[float], closed: bool = False) -> list:
        result = []
        pind = 0
        dtotal = 0
        for dind in range(len(dists)):
            lastpt = [] if len(result) == 0 else result[-1][0]
            dpartial = 0 if len(result) == 0 else math.dist(lastpt, Path._select(path, pind))
            if dists[dind] < dpartial + dtotal:
                t = (dists[dind] - dtotal) / dpartial
                nextpoint = [lerp(lastpt, Path._select(path, pind), t), pind]
            else:
                nextpoint = Path._path_cut_single(path, dists[dind] - dtotal - dpartial, closed, pind)
            result.append(nextpoint)
            dtotal = dists[dind]
            pind = nextpoint[1]
        return result

    @staticmethod
    def _path_cut_single(path, dist: float, closed: bool = False, ind: int = 0, eps: float = 1e-7) -> list:
        while True:
            if ind == len(path) - (0 if closed else 1):
                assert dist < eps, "Path is too short for specified cut distance"
                return [Path._select(path, ind), ind + 1]
            d = math.dist(path[ind], Path._select(path, ind + 1))
            if d > dist:
                return [lerp(path[ind], Path._select(path, ind + 1), dist / d), ind + 1]
            dist -= d
            ind += 1

    @staticmethod
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
                plane = Path._path_plane(path, start, start - 2, closed)
            if plane is None:
                out.append([1, 0, 0] if (dirs[i][0] == 0 and dirs[i][1] == 0) else unit([-dirs[i][1], dirs[i][0], 0]))
            else:
                out.append(unit(cross(dirs[i], cross(plane[0], plane[1]))))
        return out

    @staticmethod
    def _path_plane(path, ind: int, i: int, closed: bool = False):
        lower = -1 if closed else 0
        while i >= lower:
            if not is_collinear(path[ind], path[ind - 1], Path._select(path, i)):
                p_i = Path._select(path, i)
                return [[a - b for a, b in zip(p_i, path[ind - 1])], [a - b for a, b in zip(path[ind], path[ind - 1])]]
            i -= 1
        return None

    @staticmethod
    def _path_cuts_dir(path, cuts, closed: bool = False, eps: float = 1e-2) -> list:
        out = []
        zeros = [0] * len(path[0])
        for ind in range(len(cuts)):
            nextind = cuts[ind][1]
            nextpath = unit([a - b for a, b in zip(Path._select(path, nextind + 1), Path._select(path, nextind))], zeros)
            thispath = unit([a - b for a, b in zip(Path._select(path, nextind), Path._select(path, nextind - 1))], zeros)
            lastpath = unit([a - b for a, b in zip(Path._select(path, nextind - 1), Path._select(path, nextind - 2))], zeros)
            if nextind == len(path) and not closed:
                nextdir = lastpath
            elif (nextind <= len(path) - 2 or closed) and approx(cuts[ind][0], Path._select(path, nextind), eps=eps):
                nextdir = unit([a + b for a, b in zip(nextpath, thispath)])
            elif (nextind > 1 or closed) and approx(cuts[ind][0], Path._select(path, nextind - 1), eps=eps):
                nextdir = unit([a + b for a, b in zip(thispath, lastpath)])
            else:
                nextdir = thispath
            out.append(nextdir)
        return out

    @staticmethod
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

    # -- Splitting self-intersecting polygons into simple polygons -------------------------

    @staticmethod
    def _split_path_at_self_crossings(path, closed: bool = True, eps: float = EPSILON) -> list:
        """Split a 2D *path* into subpaths wherever it crosses itself."""
        path = Path._cleanup_path(path, eps=eps)
        raw = []
        for a in Path._path_self_intersections(path, closed=closed, eps=eps):
            raw.append([a[1], a[2]])
            raw.append([a[3], a[4]])
        raw.sort(key=lambda x: (x[0], x[1]))
        isects = Path._deduplicate([[0, 0]] + raw + [[len(path) - (1 if closed else 2), 1]], eps=eps)
        out = []
        for p0, p1 in Path._pair(isects):
            section = Path._path_select(path, p0[0], p0[1], p1[0], p1[1], closed=closed)
            outpath = Path._deduplicate(section, eps=eps)
            if len(outpath) > 1:
                out.append(outpath)
        return out

    @staticmethod
    def _tag_self_crossing_subpaths(path, nonzero: bool, closed: bool = True, eps: float = EPSILON) -> list:
        subpaths = Path._split_path_at_self_crossings(path, closed=True, eps=eps)
        out = []
        for subpath in subpaths:
            seg = Path._select(subpath, 0, 1)
            mp = np.asarray(seg, dtype=float).mean(axis=0)
            n = [x / 2048 for x in line_normal(seg[0], seg[1])]
            p1 = [mp[0] + n[0], mp[1] + n[1]]
            p2 = [mp[0] - n[0], mp[1] - n[1]]
            p1in = Path._point_in_polygon(p1, path, nonzero=nonzero) >= 0
            p2in = Path._point_in_polygon(p2, path, nonzero=nonzero) >= 0
            tag = "I" if (p1in and p2in) else "O"
            out.append([tag, subpath])
        return out

    @staticmethod
    def _modang(x: float) -> float:
        xx = x % 360
        return xx - 360 if xx > 180 else xx

    @staticmethod
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
                angs.append(Path._modang(segang2 - segang))
            else:
                angs.append(999 if rightmost else -999)
        fi = angs.index(min(angs)) if rightmost else angs.index(max(angs))
        if abs(angs[fi]) > 360:
            return [None, fragments]
        remainder = [fragments[i] for i in range(len(fragments)) if i != fi]
        return [frags[fi][2], remainder]

    @staticmethod
    def _assemble_a_path_from_fragments(fragments: list, rightmost: bool = True, startfrag: int = 0, eps: float = EPSILON) -> list:
        """Assemble *fragments* into one closed polygon path; returns [path, remaining_fragments]."""
        if len(fragments) == 0:
            return [[], []]
        if len(fragments) == 1:
            return [fragments[0], []]
        path = fragments[startfrag]
        remainder = [fragments[i] for i in range(len(fragments)) if i != startfrag]
        while True:
            if Path._is_closed_path(path, eps=eps):
                return [path, remainder]
            seg = Path._select(path, -2, -1)
            foundfrag, remainder2 = Path._extreme_angle_fragment(seg, remainder, rightmost=rightmost, eps=eps)
            if foundfrag is None:
                return [path, remainder2]
            if Path._is_closed_path(foundfrag, eps=eps):
                return [foundfrag, [path] + remainder2]
            fragend = foundfrag[-1]
            hits = [i for i in range(len(path) - 1) if approx(path[i], fragend, eps=eps)]
            if hits:
                hitidx = hits[-1]
                newpath = Path._list_head(path, hitidx)
                newfrags = ([newpath] if len(newpath) > 1 else []) + remainder2
                outpath = Path._slice(path, hitidx, -2) + foundfrag
                return [outpath, newfrags]
            path = path + Path._list_tail(foundfrag)
            remainder = remainder2

    @staticmethod
    def _assemble_path_fragments(fragments: list, eps: float = EPSILON) -> list:
        """Assemble *fragments* into complete closed polygon paths, discarding any with area < eps."""
        finished = []
        frags = fragments
        while len(frags) > 0:
            minxs = [min(pt[0] for pt in frag) for frag in frags]
            minxidx = minxs.index(min(minxs))
            result_l = Path._assemble_a_path_from_fragments(frags, startfrag=minxidx, rightmost=False, eps=eps)
            result_r = Path._assemble_a_path_from_fragments(frags, startfrag=minxidx, rightmost=True, eps=eps)
            l_area = abs(Path._polygon_area(result_l[0])) if result_l[0] else 0
            r_area = abs(Path._polygon_area(result_r[0])) if result_r[0] else 0
            result = result_l if l_area < r_area else result_r
            newpath = Path._cleanup_path(result[0])
            remainder = result[1]
            if min(l_area, r_area) >= eps:
                finished.append(newpath)
            frags = remainder
        return finished

    # -- Offset ----------------------------------------------------------------------------

    @staticmethod
    def _offset_segs(r: float, _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> int:
        """OpenSCAD's $fn/$fa/$fs segment count for a circle of radius *r* (BOSL2's segs())."""
        if _fn is not None and _fn >= 3:
            return int(math.floor(_fn))
        fa = _fa if _fa else 12.0
        fs = _fs if _fs else 2.0
        return max(5, int(math.ceil(min(360.0 / fa, (2 * math.pi * abs(r)) / fs))))

    @staticmethod
    def _offset(
        path,
        r: float | None = None,
        delta: float | None = None,
        chamfer: bool = False,
        closed: bool = True,
        _fn: float | None = None,
        _fa: float | None = None,
        _fs: float | None = None,
    ) -> list[list[float]]:
        """Offset a closed polygon by *r* (rounded joins) or *delta* (sharp/chamfered joins).

        The pure-Python/numpy equivalent of BOSL2's ``offset()``, returning POINTS. Verified to
        match the real BOSL2 exactly over every path shape and variant the toolkit uses -- square,
        concave, hexagon, a 6-point box outline and a triangle, crossed with r/delta, inward and
        outward, chamfered and not (see tests/test_bosl2_offset.py, 45 cases).

        Positive grows the polygon, negative shrinks it, for either winding (the signed area picks
        the sign convention). At each vertex the two offset edges either overlap -- and are simply
        intersected (a mitre) -- or open a gap, which is filled with an arc (``r=``), a sharp mitre
        (``delta=``) or a flat cut (``delta=`` + ``chamfer=True``, the cut sitting \\|delta\\| from
        the original vertex, square to the corner bisector).

        **Prefer PythonSCAD's native 2-D ``offset()`` when you only need geometry** -- it is
        Manifold-side and handles self-intersection properly. Reach for this only when the offset
        outline is needed as POINTS, e.g. to walk a box's wall segments.

        Usage::

            Path([[0, 0], [80, 0], [80, 60], [0, 60]]).offset(r=-2)
            path.offset(delta=2, chamfer=True)

        Args:
            r:       offset distance with rounded joins (mutually exclusive with *delta*)
            delta:   offset distance with sharp joins
            chamfer: with *delta*, flatten the corner instead of mitring it (default False)
            closed:  the path is a closed polygon (default True; open paths are not supported)

        Note:
            No self-intersection cleanup: an offset large enough to collapse a feature (roughly
            half the narrowest neck) can fold the outline back on itself. That is well beyond the
            wall-thickness insets this is used for, but it is why geometry work should use the
            native offset() instead.
        """
        assert (r is None) != (delta is None), f"offset() needs exactly one of r= or delta=, r={r} delta={delta}"
        assert closed, "offset() only supports closed polygons"
        pts = np.asarray(path, dtype=float)
        assert len(pts) >= 3, f"offset() needs at least 3 points, got {len(pts)}"

        amount = float(r if r is not None else delta)
        use_round = r is not None
        if amount == 0:
            return [[float(x), float(y)] for x, y in pts]

        # --- everything below is vectorised over all vertices at once ---------------------------
        # Incoming edge i is pts[i-1] -> pts[i]; outgoing edge i is pts[i] -> pts[i+1].
        incoming = pts - np.roll(pts, 1, axis=0)
        outgoing = np.roll(pts, -1, axis=0) - pts
        len_in = np.linalg.norm(incoming, axis=1)
        len_out = np.linalg.norm(outgoing, axis=1)

        keep = (len_in > EPSILON) & (len_out > EPSILON)
        if not keep.all():  # drop duplicate points, then redo the rolls on the cleaned path
            pts = pts[keep]
            assert len(pts) >= 3, "offset() needs at least 3 distinct points"
            incoming = pts - np.roll(pts, 1, axis=0)
            outgoing = np.roll(pts, -1, axis=0) - pts
            len_in = np.linalg.norm(incoming, axis=1)
            len_out = np.linalg.norm(outgoing, axis=1)

        u_in = incoming / len_in[:, None]
        u_out = outgoing / len_out[:, None]

        # Signed area picks the winding, so one normal expression serves both.
        area = 0.5 * float(np.sum(pts[:, 0] * np.roll(pts[:, 1], -1) - np.roll(pts[:, 0], -1) * pts[:, 1]))
        sign = 1.0 if area > 0 else -1.0

        n_in = np.column_stack((u_in[:, 1], -u_in[:, 0])) * sign
        n_out = np.column_stack((u_out[:, 1], -u_out[:, 0])) * sign
        pt_in = pts + n_in * amount
        pt_out = pts + n_out * amount

        turn = (u_in[:, 0] * u_out[:, 1] - u_in[:, 1] * u_out[:, 0]) * sign
        opens_gap = turn * amount > 0

        # Mitre: intersect the two offset edge lines. Parallel edges fall back to pt_in.
        denom = u_in[:, 0] * u_out[:, 1] - u_in[:, 1] * u_out[:, 0]
        safe = np.abs(denom) >= EPSILON
        step = np.zeros(len(pts))
        np.divide(
            (pt_out[:, 0] - pt_in[:, 0]) * u_out[:, 1] - (pt_out[:, 1] - pt_in[:, 1]) * u_out[:, 0],
            denom, out=step, where=safe,
        )
        mitre = pt_in + u_in * step[:, None]

        if not opens_gap.any():  # the common case: no arcs/chamfers, so we are already done
            return mitre.tolist()

        out: list[list[float]] = []
        for i in range(len(pts)):
            if not opens_gap[i]:
                out.append([float(mitre[i, 0]), float(mitre[i, 1])])
            elif use_round:
                here, a_pt, b_pt = pts[i], pt_in[i], pt_out[i]
                start_deg = math.degrees(math.atan2(a_pt[1] - here[1], a_pt[0] - here[0]))
                end_deg = math.degrees(math.atan2(b_pt[1] - here[1], b_pt[0] - here[0]))
                sweep = (end_deg - start_deg + 180) % 360 - 180
                steps = math.ceil(Path._offset_segs(abs(amount), _fn, _fa, _fs) * abs(sweep) / 360) + 1
                theta = np.radians(start_deg + sweep * np.arange(steps) / (steps - 1))
                arc_pts = here + abs(amount) * np.column_stack((np.cos(theta), np.sin(theta)))
                out.extend(arc_pts.tolist())
            elif chamfer:
                bisector = n_in[i] + n_out[i]
                blen = float(np.linalg.norm(bisector))
                if blen < EPSILON:
                    out.append([float(pt_in[i, 0]), float(pt_in[i, 1])])
                    out.append([float(pt_out[i, 0]), float(pt_out[i, 1])])
                else:
                    bisector = bisector / blen
                    cut = pts[i] + bisector * amount
                    for point, direction in ((pt_in[i], u_in[i]), (pt_out[i], u_out[i])):
                        d = float(direction @ bisector)
                        if abs(d) < EPSILON:
                            out.append([float(point[0]), float(point[1])])
                        else:
                            hit = point + direction * (float((cut - point) @ bisector) / d)
                            out.append([float(hit[0]), float(hit[1])])
            else:
                out.append([float(mitre[i, 0]), float(mitre[i, 1])])
        return out

    # -- Rounding --------------------------------------------------------------------------
    #
    # Pure-Python port of round_corners() from BOSL2's rounding.scad, method="circle" only:
    # round every corner of a 2-D path to a given radius, inserting an arc. The "smooth"
    # (continuous-curvature) and "chamfer" methods, the cut=/joint=/width= size measures, 3-D
    # paths, and the minimum-length "scale factor" overflow check are not ported -- nothing in
    # this project uses them.

    @staticmethod
    def _vector_angle3(p0: list[float], p1: list[float], p2: list[float]) -> float:
        dim = len(p1)
        v1 = [p0[i] - p1[i] for i in range(dim)]
        v2 = [p2[i] - p1[i] for i in range(dim)]
        n1, n2 = math.hypot(*v1), math.hypot(*v2)
        cosang = max(-1.0, min(1.0, sum(a * b for a, b in zip(v1, v2)) / (n1 * n2)))
        return math.degrees(math.acos(cosang))

    @staticmethod
    def _circlecorner(points: list[list[float]], d: float, r: float, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
        # local: shapes2d imports pythonscad, which paths.py must stay importable without
        from bosl2.shapes2d import _frag_count, _arc_points

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

    @staticmethod
    def _round_corners(
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
            angle = Path._vector_angle3(p0, p1, p2) / 2
            assert not approx(angle, 0), f"Path turns back on itself at index {i} with nonzero rounding"
            dk.append([parm[i] / math.tan(math.radians(angle)), parm[i]])

        out = []
        for i in range(n):
            if dk[i][0] == 0:
                out.append(path[i])
                continue
            p0, p1, p2 = path[(i - 1) % n], path[i], path[(i + 1) % n]
            out.extend(Path._circlecorner([p0, p1, p2], dk[i][0], dk[i][1], _fn, _fa, _fs))
        return Path._deduplicate(out, closed=closed)


# ---------------------------------------------------------------------------
# Section: Path3D object
# ---------------------------------------------------------------------------
#
# The 3-D sibling of Path, for the paths that carry a Z (helix(), and any other 3-D point
# generator). It reuses Path's numeric kernels -- they were written dimension-agnostically for
# exactly this (see the module docstring) -- and only carries the operations that make sense on
# a set of 3-D points: no polygon()/region()/offset()/area (those are inherently 2-D), but full
# measurement (length, tangents, normals, curvature, torsion), resampling/cutting, and the 3-D
# transforms (translate/move, the six directional moves including up/down, scale, mirror, rotate).


class Path3D(Distributable, Extrudable, Roundable, list):
    """A 3-D path: a list of ``[x, y, z]`` points, with the path operations that make sense in 3-D.

    The 3-D counterpart of :class:`Path`. Like ``Path`` it subclasses ``list`` (so it stays a
    drop-in for the raw 3-D point lists the sweep/loft functions consume), and every method returns
    a NEW object. It carries the dimension-independent measurements (length, segment lengths,
    tangents, :meth:`normals`, curvature, :meth:`torsion`), resampling/subdividing/cutting, and the
    3-D transforms (``translate``/``move``, ``right``/``left``/``back``/``forward``/``up``/``down``,
    ``scale``, ``mirror``, ``rotate``). The inherently-2-D operations of ``Path`` (``polygon``,
    ``area``, ``offset``, ``round_corners``, point-in-polygon) are intentionally absent; use
    :meth:`path2d` to drop to the XY plane when you want them.

    Args:
        points: the ``[x, y, z]`` points (anything array-like; numpy scalars are converted to float)
        closed: whether the path is a closed loop (default True)

    Examples:
        A helix resampled to fewer points and swept into a coil:

        .. pythonscad-example::

            coil = helix(turns=3, h=60, r=20).resample(n=120)
            coil.stroke(width=4).show()
    """

    def __init__(self, points: Sequence = (), closed: bool = True) -> None:
        pts = np.asarray(list(points), dtype=float)
        if pts.size == 0:
            super().__init__()
        else:
            assert pts.ndim == 2 and pts.shape[1] == 3, f"Path3D needs [x, y, z] points, got shape {pts.shape}"
            super().__init__([[float(x), float(y), float(z)] for x, y, z in pts])
        self.closed = closed

    def _like(self, points) -> "Path3D":
        return Path3D(points, closed=self.closed)

    @property
    def array(self) -> np.ndarray:
        """The points as an (N, 3) numpy array, for doing your own vectorised maths."""
        return np.asarray(self, dtype=float)

    # -- measurement -----------------------------------------------------------------------

    def bounds(self) -> np.ndarray:
        """[[min_x, min_y, min_z], [max_x, max_y, max_z]]."""
        pts = self.array
        return np.array([pts.min(axis=0), pts.max(axis=0)])

    def perimeter(self) -> float:
        """Total length along the path."""
        return float(Path._path_length(self, closed=self.closed))

    length = perimeter

    def segment_lengths(self) -> np.ndarray:
        """Length of each segment, as an ndarray."""
        return Path._path_segment_lengths(self, closed=self.closed)

    def length_fractions(self) -> np.ndarray:
        """Cumulative length fraction at each point, as an ndarray."""
        return Path._path_length_fractions(self, closed=self.closed)

    @property
    def is_closed(self) -> bool:
        """True if the first and last points of the path coincide."""
        return bool(Path._is_closed_path(self))

    def closest_point(self, pt: Sequence[float]) -> list:
        """[SEGNUM, POINT]: the closest path segment to *pt*, and the closest point on it."""
        return Path._path_closest_point(self, pt, closed=self.closed)

    def tangents(self, uniform: bool = True) -> np.ndarray:
        """Unit tangent at each point, as an ndarray."""
        return Path._path_tangents(self, closed=self.closed, uniform=uniform)

    def normals(self, tangents=None) -> np.ndarray:
        """Unit normal at each point (in the local plane of the curve), as an ndarray."""
        return Path._path_normals(self, tangents=tangents, closed=self.closed)

    def curvature(self) -> np.ndarray:
        """Curvature at each point, as an ndarray."""
        return Path._path_curvature(self, closed=self.closed)

    def torsion(self) -> np.ndarray:
        """Numeric torsion estimate at each point, as an ndarray."""
        return Path._path_torsion(self, closed=self.closed)

    def cut_points(self, cutdist, direction: bool = False):
        """Point(s) at the given distance(s) along the path."""
        return Path._path_cut_points(self, cutdist, closed=self.closed, direction=direction)

    # -- derived paths ---------------------------------------------------------------------

    def close(self) -> "Path3D":
        """Append the start point if the path isn't already closed."""
        return self._like(Path._close_path(self))

    def cleanup(self) -> "Path3D":
        """Drop a duplicate closing point if present."""
        return self._like(Path._cleanup_path(self))

    def reversed_path(self) -> "Path3D":
        """The same path wound the other way."""
        return self._like(list(reversed(self)))

    def deduplicated(self) -> "Path3D":
        """Drop consecutive repeated points."""
        return self._like(Path._deduplicate(self, closed=self.closed))

    def subdivide(self, **kwargs: Any) -> "Path3D":
        """Insert points along the path."""
        return self._like(Path._subdivide_path(self, closed=self.closed, **kwargs))

    def resample(self, **kwargs: Any) -> "Path3D":
        """Resample to evenly spaced points."""
        return self._like(Path._resample_path(self, closed=self.closed, **kwargs))

    def cut(self, cutdist) -> list["Path3D"]:
        """Split the path at the given distance(s), returning the sub-paths."""
        return [self._like(sub) for sub in Path._path_cut(self, cutdist, closed=self.closed)]

    # -- transforms ------------------------------------------------------------------------
    #
    # 3-D versions of the Path transforms. Directions follow BOSL2: right/left are +/-X, back/
    # forward are +/-Y, up/down are +/-Z. Every method returns a NEW Path3D.

    def translate(self, v: Sequence[float]) -> "Path3D":
        """Translate every point by *v* (a shorter vector pads with zeros)."""
        vv = np.zeros(3)
        v = np.asarray(v, dtype=float)
        vv[: min(3, len(v))] = v[: min(3, len(v))]
        return self._like(self.array + vv)

    move = translate

    def scale(self, v: "float | Sequence[float]") -> "Path3D":
        """Scale every point by a scalar or a per-axis ``[sx, sy, sz]`` factor."""
        s = np.asarray([v, v, v] if isinstance(v, (int, float)) else list(v), dtype=float)
        return self._like(self.array * s)

    def rotate(self, a: "float | Sequence[float]", v: Sequence[float] | None = None) -> "Path3D":
        """Rotate the points. ``rotate(ang, axis)`` spins about *axis*; ``rotate(ang)`` about +Z;
        ``rotate([rx, ry, rz])`` applies the OpenSCAD X-then-Y-then-Z Euler rotation."""
        from bosl2.transforms import axis_angle_matrix

        if v is not None:
            m = np.asarray(axis_angle_matrix(a, v), dtype=float)
        elif isinstance(a, (list, tuple, np.ndarray)):
            rx, ry, rz = (list(a) + [0, 0, 0])[:3]
            mx = np.asarray(axis_angle_matrix(rx, [1, 0, 0]), dtype=float)
            my = np.asarray(axis_angle_matrix(ry, [0, 1, 0]), dtype=float)
            mz = np.asarray(axis_angle_matrix(rz, [0, 0, 1]), dtype=float)
            m = mz @ my @ mx
        else:
            m = np.asarray(axis_angle_matrix(a, [0, 0, 1]), dtype=float)
        return self._like(self.array @ m.T)

    rot = rotate

    def mirror(self, v: Sequence[float]) -> "Path3D":
        """Reflect every point across the plane through the origin with normal *v*."""
        n = np.asarray(v, dtype=float)
        n = n / np.linalg.norm(n)
        pts = self.array
        return self._like(pts - 2 * np.outer(pts @ n, n))

    def right(self, x: float) -> "Path3D":
        """Translate by *x* along +X."""
        return self.translate([x, 0.0, 0.0])

    def left(self, x: float) -> "Path3D":
        """Translate by *x* along -X."""
        return self.translate([-x, 0.0, 0.0])

    def back(self, y: float) -> "Path3D":
        """Translate by *y* along +Y."""
        return self.translate([0.0, y, 0.0])

    def forward(self, y: float) -> "Path3D":
        """Translate by *y* along -Y (BOSL2 fwd())."""
        return self.translate([0.0, -y, 0.0])

    fwd = forward

    def up(self, z: float) -> "Path3D":
        """Translate by *z* along +Z."""
        return self.translate([0.0, 0.0, z])

    def down(self, z: float) -> "Path3D":
        """Translate by *z* along -Z."""
        return self.translate([0.0, 0.0, -z])

    # -- conversion / rendering ------------------------------------------------------------

    def path2d(self) -> "Path":
        """Drop the Z coordinate, giving a 2-D :class:`Path` (the XY projection)."""
        return Path(self.array[:, :2], closed=self.closed)

    def stroke(self, width: float = 1, closed: bool | None = None, **kwargs: Any):
        """Draw this 3-D path as a solid tube of the given *width* (see :func:`bosl2.drawing.stroke`)."""
        from bosl2.drawing import stroke as _stroke

        return _stroke(self, width=width, closed=self.closed if closed is None else closed, **kwargs)

    def dashed_stroke(self, dashpat: Sequence[float] = (3, 3), closed: bool | None = None,
                      **kwargs: Any) -> list["Path3D"]:
        """Break this 3-D path into dash sub-paths (see :func:`bosl2.drawing.dashed_stroke`)."""
        from bosl2.drawing import dashed_stroke as _dashed

        return _dashed(self, dashpat=dashpat, closed=self.closed if closed is None else closed, **kwargs)

    # -- distributors (bosl2/distributors.py) ----------------------------------------------

    def _distribute(self, mats) -> list["Path3D"]:
        """Apply each copier matrix, returning the list of 3-D copies (BOSL2's function form)."""
        if not len(self):
            return [self._like([]) for _ in mats]
        pts3 = self.array
        return [self._like(_apply4(m, pts3)) for m in mats]

    def __repr__(self) -> str:
        return f"Path3D({len(self)} pts, closed={self.closed})"
