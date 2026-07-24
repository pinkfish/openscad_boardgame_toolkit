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

# LibFile: bosl2/miscellaneous.py
#    Pure-Python port of BOSL2's miscellaneous.scad: extrusions (extrude_from_to, path_extrude2d,
#    path_extrude, cylindrical_extrude), the bounding box, chain_hull, and the minkowski-based
#    transforms (minkowski_difference, offset3d, round3d).
#
#    The two path extrusions are methods on :class:`~bosl2.paths.Path` / :class:`~bosl2.paths.Path3D`
#    via the :class:`Extrudable` mixin, and -- unlike BOSL2, which extrudes its *children* -- they
#    take the 2-D cross-section as a *profile* argument: a native 2-D shape, a Path/Region, a
#    Bosl2Solid wrapping 2-D geometry, or a zero-argument factory that returns fresh geometry (the
#    "children" form; use a factory to avoid the frep handle-reuse segfault). The bbox/offset/round
#    operators are methods on :class:`~bosl2.shapes3d.Bosl2Solid` via :class:`Miscellaneous`.
#
#    Only matrix/vector math and bosl2.transforms/constants are imported at load time; native
#    primitives, shapes3d, and skin.rot_resample are imported lazily, so shapes3d/paths can pull in
#    the mixins during their own import without a cycle.
#
# FileSummary: Extrusions, bounding box, chain hull, and minkowski-based transforms.
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
from functools import reduce
import math
import operator

import numpy as np

from bosl2.transforms import axis_angle_matrix, rot_from_to
from bosl2.constants import UP, RIGHT, BACK
from bosl2.vectors import unit
from bosl2.geometry import pointlist_bounds

__all__ = [
    "extrude_from_to", "cylindrical_extrude", "chain_hull", "minkowski_difference",
    "Extrudable", "Miscellaneous",
]


# ---------------------------------------------------------------------------
# Section: helpers
# ---------------------------------------------------------------------------


def _vec3(v):
    a = np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a


def _rot_from_to4(a, b):
    ang, axis = rot_from_to(a, b)
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(ang, axis)
    return m


def _zrot4(deg):
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(deg, [0, 0, 1])
    return m


def _frame_map4(y, z):
    """Rotation whose local +Y and +Z axes point along *y* and *z* (BOSL2 frame_map(y=, z=))."""
    yv, zv = unit(_vec3(y)), unit(_vec3(z))
    xv = unit(np.cross(yv, zv))
    yv = unit(np.cross(zv, xv))
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = xv, yv, zv
    return m


def _unwrap(obj):
    from bosl2.shapes3d import Bosl2Solid
    return obj.shape if isinstance(obj, Bosl2Solid) else obj


def _as_native_2d(profile):
    """A native 2-D shape from *profile* (native shape, Path, Region, or Bosl2Solid)."""
    from bosl2.shapes3d import Bosl2Solid
    if isinstance(profile, Bosl2Solid):
        return profile.shape
    geom = getattr(profile, "geometry", None)
    if callable(geom):  # Path / Region
        return geom()
    return profile


def _profile_factory(profile):
    """A zero-arg callable yielding native 2-D geometry -- a factory is called fresh each time
    (the "children" form, safe for frep handles); anything else is meshed once and reused."""
    from bosl2.shapes3d import Bosl2Solid
    if callable(profile) and not isinstance(profile, (list, tuple, Bosl2Solid)):
        return lambda: _as_native_2d(profile())
    native = _as_native_2d(profile)
    return lambda: native


def _point_left_of_line2d(p, a, b):
    return float((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))


def _vector_angle3(a, b, c):
    va = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    vc = np.asarray(c, dtype=float) - np.asarray(b, dtype=float)
    cosv = float(np.dot(va, vc)) / (float(np.linalg.norm(va)) * float(np.linalg.norm(vc)))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosv))))


def _planar_half(shape, keep_positive_x, s):
    """Keep the x>=0 (or x<=0) half of a native 2-D *shape* (BOSL2 right_half/left_half planar)."""
    from pythonscad import square as _square
    strip = _square([s, 2 * s], center=True)
    strip = strip.translate([s / 2 if keep_positive_x else -s / 2, 0])
    return shape & strip


# ---------------------------------------------------------------------------
# Section: extrude_from_to / cylindrical_extrude (free functions)
# ---------------------------------------------------------------------------


def extrude_from_to(profile, pt1, pt2, twist: float = 0, scale: float = 1, slices=None,
                    convexity: int = 10):
    """Linearly extrude a 2-D *profile* between two 3-D points (BOSL2 extrude_from_to()).

    The profile's origin is placed on *pt1* and *pt2*, oriented perpendicular to the line between
    them. *profile* is a native 2-D shape, a Path/Region, a Bosl2Solid, or a factory.

    Examples:
        A twisted, tapering column between two points:

        .. pythonscad-example::

            extrude_from_to(s2.circle(r=4), [0, 0, 0], [10, 20, 30], twist=180, scale=2).show()
    """
    from bosl2.shapes3d import Bosl2Solid

    p1, p2 = _vec3(pt1), _vec3(pt2)
    d = p2 - p1
    height = float(np.linalg.norm(d))
    if height <= 0:
        raise AssertionError("extrude_from_to(): the two points must differ.")
    theta = math.degrees(math.atan2(d[1], d[0]))
    phi = math.degrees(math.atan2(math.hypot(d[0], d[1]), d[2]))
    native = _as_native_2d(profile)
    kw = {"height": height, "center": False, "twist": twist, "scale": scale, "convexity": convexity}
    if slices is not None:
        kw["slices"] = slices
    solid = native.linear_extrude(**kw).rotate([0, phi, theta]).translate([float(c) for c in p1])
    return Bosl2Solid(solid)


def cylindrical_extrude(profile, ir=None, or_=None, od=None, id=None, size=None, spin: float = 0,
                        orient=UP, convexity: int = 10, _fn=None, _fa=None, _fs=None):
    """Wrap a 2-D *profile* around a cylinder, from radius *ir* out to *or_* (BOSL2 cylindrical_extrude()).

    Chops the profile into vertical facets and extrudes each radially. Handy for embossing text
    onto a curved wall. The profile's X spans one revolution by default (override with *size*).
    """
    from pythonscad import square as _square
    from bosl2.shapes2d import _frag_count
    from bosl2.shapes3d import Bosl2Solid

    irv = ir if ir is not None else (id / 2 if id is not None else None)
    orv = or_ if or_ is not None else (od / 2 if od is not None else None)
    assert irv is not None and orv is not None and irv > 0 and orv > 0, \
        "cylindrical_extrude(): give positive inner and outer radius/diameter."
    circumf = 2 * math.pi * orv
    if size is None:
        size = [circumf, 1000.0]
    elif isinstance(size, (int, float)):
        size = [float(size), 1000.0]
    else:
        size = [float(size[0]), float(size[1])]
    sides = _frag_count(orv, _fn, _fa, _fs)
    step = circumf / sides
    steps = math.ceil(size[0] / step)
    scalefactor = sides / math.pi * math.sin(math.radians(180 / sides))
    native = _as_native_2d(profile)
    facets = []
    for i in range(steps):
        x = (i + 0.5 - steps / 2) * step
        clip = _square([max(step, 2 ** -15), size[1]], center=True)
        slab = (native.translate([-x, 0]) & clip)
        slab = slab.scale([scalefactor, 1]).mirror([0, 1])
        wedge = slab.linear_extrude(height=orv - irv, scale=[irv / orv, 1], center=False,
                                    convexity=convexity)
        wedge = wedge.rotate([-90, 0, 0]).translate([0, -orv * math.cos(math.radians(180 / sides)), 0])
        wedge = wedge.rotate([0, 0, 360 * x / circumf])
        facets.append(wedge)
    solid = reduce(operator.or_, facets)
    ang, axis = rot_from_to(UP, orient)
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(ang, axis)
    solid = solid.rotate([0, 0, spin]).multmatrix(m.tolist())
    return Bosl2Solid(solid)


# ---------------------------------------------------------------------------
# Section: chain_hull / minkowski_difference (free functions)
# ---------------------------------------------------------------------------


def chain_hull(*objects):
    """Union the hulls of each consecutive pair of *objects* (BOSL2 chain_hull())."""
    from pythonscad import hull as _hull
    from bosl2.shapes3d import Bosl2Solid

    objs = list(objects[0]) if len(objects) == 1 and isinstance(objects[0], (list, tuple)) else list(objects)
    assert objs, "chain_hull(): needs at least one object."
    natives = [_unwrap(o) for o in objs]
    if len(natives) == 1:
        return Bosl2Solid(natives[0])
    hulls = [_hull(natives[i - 1], natives[i]) for i in range(1, len(natives))]
    return Bosl2Solid(reduce(operator.or_, hulls))


def minkowski_difference(base, *diffs, size: float = 1000, convexity: int = 10):
    """Carve *diffs* out of the surface of *base* (BOSL2 minkowski_difference())."""
    from pythonscad import minkowski as _mink, cube as _cube
    from bosl2.shapes3d import Bosl2Solid

    b = _unwrap(base)
    ds = list(diffs[0]) if len(diffs) == 1 and isinstance(diffs[0], (list, tuple)) else list(diffs)
    assert ds, "minkowski_difference(): needs at least one diff shape."
    center, sz = Bosl2Solid(b).bounds() if isinstance(base, Bosl2Solid) else _native_bounds(b)
    box0 = _cube([sz[i] for i in range(3)], center=True).translate([float(c) for c in center])
    box1 = _cube([sz[i] + 2 for i in range(3)], center=True).translate([float(c) for c in center])
    shell = box1 - b
    carve = reduce(operator.or_, [_mink(shell, d) for d in ds]) if len(ds) > 1 else _mink(shell, ds[0])
    return Bosl2Solid(box0 - carve)


def _native_bounds(shape):
    from bosl2.shapes3d import Bosl2Solid
    return Bosl2Solid(shape).bounds()


# ---------------------------------------------------------------------------
# Section: Extrudable mixin (Path / Path3D)
# ---------------------------------------------------------------------------


class Extrudable:
    """Mixin adding path_extrude / path_extrude2d as methods on :class:`~bosl2.paths.Path` and
    :class:`~bosl2.paths.Path3D`. Both take the 2-D cross-section as a *profile* argument instead
    of OpenSCAD children (a native 2-D shape, a Path/Region, a Bosl2Solid, or a factory).
    """

    def path_extrude2d(self, profile, caps: bool = False, closed=None, s=None, convexity: int = 10):
        """Extrude a 2-D *profile* along this 2-D path, standing it vertically (BOSL2 path_extrude2d()).

        Builds a straight run for each segment and a revolved fillet at each corner, unioned into a
        3-D "moulding" that follows the path. *caps* rounds the two open ends (the profile must be
        symmetric across the Y axis); *closed* joins the ends into a loop; *s* is the internal mask
        size (defaults to the path's bounding-box diagonal).
        """
        from bosl2.shapes3d import Bosl2Solid

        assert len(self[0]) == 2, "path_extrude2d(): the path must be 2-D (use path_extrude for 3-D)."
        is_closed = self.closed if closed is None else closed
        assert not (caps and is_closed), "path_extrude2d(): cannot cap a closed extrusion."
        pts = [[float(p[0]), float(p[1])] for p in self.deduplicated()]
        n = len(pts)
        assert n >= 2, "path_extrude2d(): need at least two points."
        if s is None:
            b = pointlist_bounds(pts)
            s = float(np.linalg.norm(b[1] - b[0]))
        factory = _profile_factory(profile)
        parts = []
        # straight segments
        last = n if is_closed else n - 1
        for i in range(last):
            a = np.asarray(pts[i])
            b = np.asarray(pts[(i + 1) % n])
            segv = b - a
            seglen = float(np.linalg.norm(segv))
            if seglen < 1e-9:
                continue
            block = factory().linear_extrude(height=seglen, center=True, convexity=convexity)
            block = block.rotate([90, 0, 0]).multmatrix(_rot_from_to4(BACK, [segv[0], segv[1], 0]).tolist())
            block = block.translate([float((a[0] + b[0]) / 2), float((a[1] + b[1]) / 2), 0])
            parts.append(block)
        # corner fillets
        ea = 0.1  # tiny overlap so the fillets fuse to the segments
        idxs = range(n) if is_closed else range(1, n - 1)
        for i in idxs:
            t0, t1, t2 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
            ang = -(180 - _vector_angle3(t0, t1, t2)) * (1 if _point_left_of_line2d(t2, t0, t1) >= 0 else -1)
            if abs(ang) < 1e-9:
                continue
            sgn = 1 if ang > 0 else -1
            half = _planar_half(factory(), keep_positive_x=(ang < 0), s=s)
            corner = half.rotate_extrude(angle=ang + sgn * ea)
            corner = corner.rotate([0, 0, -sgn * ea / 2])
            corner = corner.multmatrix(_frame_map4([t2[0] - t1[0], t2[1] - t1[1], 0], UP).tolist())
            corner = corner.translate([t1[0], t1[1], 0])
            parts.append(corner)
        # rounded caps on the open ends
        if caps and not is_closed:
            for a, b in ((pts[0], pts[1]), (pts[-1], pts[-2])):
                cap = _planar_half(factory(), keep_positive_x=True, s=s).rotate_extrude(angle=180)
                cap = cap.multmatrix(_rot_from_to4(BACK, [a[0] - b[0], a[1] - b[1], 0]).tolist())
                cap = cap.translate([a[0], a[1], 0])
                parts.append(cap)
        assert parts, "path_extrude2d(): nothing to extrude."
        return Bosl2Solid(reduce(operator.or_, parts))

    def path_extrude(self, profile, convexity: int = 10, clipsize: float = 100):
        """Extrude a 2-D *profile* along this path in 3-D (BOSL2 path_extrude()).

        Places an oriented linear extrusion for each segment and clips it at the mitre planes
        between segments. A 2-D Path is lifted to the ``z=0`` plane first. For most sweeps
        :func:`~bosl2.skin.path_sweep` is faster and cleaner; this exists for extruding an arbitrary
        native 2-D object (text, multi-part shapes) that is not a single polygon.
        """
        from bosl2.skin import rot_resample
        from bosl2.shapes3d import Bosl2Solid
        from pythonscad import cube as _cube

        dim = len(self[0])
        path = [[float(p[0]), float(p[1]), float(p[2]) if dim == 3 else 0.0] for p in self]
        n = len(path)
        assert n >= 2, "path_extrude(): need at least two points."
        parr = [np.asarray(p) for p in path]
        rotmats = []
        acc = np.eye(4)
        for i in range(n - 1):
            vec1 = np.asarray(UP, dtype=float) if i == 0 else unit(parr[i] - parr[i - 1])
            vec2 = unit(parr[i + 1] - parr[i])
            # left-multiply so each frame maps local +Z exactly onto its segment direction
            # (frame_i @ UP == dir_i); this is the discrete rotation-minimizing frame.
            acc = _rot_from_to4(vec1, vec2) @ acc
            rotmats.append(acc)
        interp = rot_resample(rotmats, n=2, method="count")
        eps = 1e-4
        factory = _profile_factory(profile)
        parts = []
        for i in range(n - 1):
            pt1, pt2 = parr[i], parr[i + 1]
            dist = float(np.linalg.norm(pt2 - pt1))
            if dist < 1e-9:
                continue
            t = rotmats[i]
            ext = (factory().linear_extrude(height=dist + clipsize / 2, convexity=convexity)
                   .translate([0, 0, -clipsize / 4]).multmatrix(t.tolist())
                   .translate([float(c) for c in pt1]))
            hq_start = np.asarray(interp[2 * i - 1]) if i > 0 else t
            hq_end = np.asarray(interp[2 * i + 1]) if i < n - 2 else t
            c1 = (_cube([clipsize] * 3, center=True).translate([0, 0, -(clipsize / 2 + eps)])
                  .multmatrix(hq_start.tolist()).translate([float(c) for c in pt1]))
            c2 = (_cube([clipsize] * 3, center=True).translate([0, 0, clipsize / 2 + eps])
                  .multmatrix(hq_end.tolist()).translate([float(c) for c in pt2]))
            parts.append((ext - c1) - c2)
        assert parts, "path_extrude(): nothing to extrude."
        return Bosl2Solid(reduce(operator.or_, parts))


# ---------------------------------------------------------------------------
# Section: Miscellaneous mixin (Bosl2Solid)
# ---------------------------------------------------------------------------


class Miscellaneous:
    """Mixin adding bounding_box / offset3d / round3d / chain_hull / minkowski_difference as methods
    on :class:`~bosl2.shapes3d.Bosl2Solid`."""

    def bounding_box(self, excess: float = 0):
        """The smallest axis-aligned cuboid containing this solid, grown by *excess* (BOSL2 bounding_box()).

        Uses the native bounding box, so it is exact and fast (BOSL2's projection/minkowski trick is
        not needed here)."""
        from bosl2.shapes3d import cuboid
        center, size = self.bounds()
        return cuboid([size[i] + 2 * excess for i in range(3)]).translate([float(c) for c in center])

    def offset3d(self, r: float, size: float = 1000, convexity: int = 10):
        """Expand (or, for negative *r*, contract) the surface of this solid by *r* (BOSL2 offset3d()).

        Uses ``minkowski()`` with a sphere and is *very* slow; use sparingly."""
        from pythonscad import cube as _cube, sphere as _sphere, minkowski as _mink
        from bosl2.shapes2d import _frag_count
        if r == 0:
            return self
        n = max(8, _frag_count(abs(r)))
        n = int(math.ceil(n / 4) * 4)
        if r > 0:
            return self._wrap(_mink(self.shape, _sphere(r, fn=n)))
        big1 = _cube([size * 1.02] * 3, center=True)
        big2 = _cube([size] * 3, center=True)
        return self._wrap(big2 - _mink(big1 - self.shape, _sphere(-r, fn=n)))

    def round3d(self, r=None, or_=None, ir=None, size: float = 1000):
        """Round the corners of this solid (BOSL2 round3d()): *r* rounds all, *or_* only convex,
        *ir* only concave. Uses ``offset3d`` three times and is extremely slow."""
        orr = or_ if or_ is not None else (r if r is not None else 0)
        irr = ir if ir is not None else (r if r is not None else 0)
        return self.offset3d(orr, size=size).offset3d(-irr - orr, size=size).offset3d(irr, size=size)

    def chain_hull(self, *others):
        """This solid chain-hulled with *others*, in order (see :func:`chain_hull`)."""
        return chain_hull(self, *others)

    def minkowski_difference(self, *diffs, size: float = 1000):
        """Carve *diffs* out of this solid's surface (see :func:`minkowski_difference`)."""
        return minkowski_difference(self, *diffs, size=size)
