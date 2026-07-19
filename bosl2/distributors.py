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

# LibFile: bosl2/distributors.py
#    Pure-Python port of BOSL2's distributors.scad: the "copiers" that duplicate a shape into a
#    line/grid/ring/arc/sphere/path pattern, plus the reflected-copy helpers. Each copier is a
#    module-level function that returns a list of 4x4 transformation matrices (BOSL2's function
#    form without a ``p=`` argument), and a matching method on the :class:`Distributable` mixin
#    that applies those matrices to the object.
#
#    The mixin is inherited by :class:`~bosl2.shapes3d.Bosl2Solid`, :class:`~bosl2.paths.Path`,
#    and :class:`~bosl2.paths.Path3D`, each of which implements ``_distribute(mats)`` to say what
#    "a list of copies" means for it:
#      * Bosl2Solid  -> the UNION of the transformed geometry copies (a new Bosl2Solid).
#      * Path / Path3D -> a plain ``list`` of transformed path copies (BOSL2's function form).
#        A 2-D Path only supports the in-plane copiers; one that would lift it out of the XY plane
#        raises, directing you to Path3D.
#
#    Only matrix math and bosl2.transforms/constants are imported at load time (so paths.py can
#    pull in the mixin during its own import without a cycle); Path/Region/point-in-polygon are
#    imported lazily inside the few functions that need them.
#
# FileSummary: Distributors: line/grid/ring/arc/sphere/path copiers and reflected copies.
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

from bosl2.transforms import axis_angle_matrix, rot_from_to
from bosl2.constants import RIGHT, BACK, UP

__all__ = [
    "move_copies", "xcopies", "ycopies", "zcopies", "line_copies", "grid_copies",
    "rot_copies", "xrot_copies", "yrot_copies", "zrot_copies", "arc_copies", "sphere_copies",
    "path_copies", "mirror_copy", "xflip_copy", "yflip_copy", "zflip_copy",
    "distribute", "xdistribute", "ydistribute", "zdistribute", "Distributable",
]


# ---------------------------------------------------------------------------
# Section: matrix helpers
# ---------------------------------------------------------------------------


def _is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _scalar_vec3(v, fill: float = 0.0) -> np.ndarray:
    """BOSL2 scalar_vec3(): a scalar becomes [v, fill, fill]; a vector is padded to length 3."""
    if _is_num(v):
        return np.array([float(v), float(fill), float(fill)])
    arr = list(v)
    return np.array([float(arr[i]) if i < len(arr) else float(fill) for i in range(3)])


def _unit3(v) -> np.ndarray:
    a = _scalar_vec3(v, 0.0) if _is_num(v) else np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    n = float(np.linalg.norm(a))
    return a / n if n else a


def _translate4(v) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = _scalar_vec3(v, 0.0)
    return m


def _rot4(a: float, v=None, reverse: bool = False) -> np.ndarray:
    """4x4 rotation of *a* degrees about axis *v* (default +Z), through the origin."""
    ang = -a if reverse else a
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(ang, UP if v is None else v)
    return m


def _mirror4(nv) -> np.ndarray:
    n = _unit3(nv)
    m = np.eye(4)
    m[:3, :3] = np.eye(3) - 2 * np.outer(n, n)
    return m


def _rot_from_to4(a, b) -> np.ndarray:
    ang, axis = rot_from_to(a, b)
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(ang, axis)
    return m


def _frame_map4(x=None, z=None) -> np.ndarray:
    """A rotation whose local X and Z axes point along *x* and *z* (BOSL2 frame_map(x=, z=))."""
    xv, zv = _unit3(x), _unit3(z)
    yv = _unit3(np.cross(zv, xv))
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = xv, yv, zv
    return m


def _spherical_to_xyz(r: float, theta: float, phi: float) -> np.ndarray:
    th, ph = math.radians(theta), math.radians(phi)
    return np.array([r * math.sin(ph) * math.cos(th), r * math.sin(ph) * math.sin(th), r * math.cos(ph)])


def _radius(r=None, d=None, r1=None, d1=None, dflt=None):
    """BOSL2 get_radius() priority: r1 > d1/2 > r > d/2 > dflt."""
    if r1 is not None:
        return r1
    if d1 is not None:
        return d1 / 2
    if r is not None:
        return r
    if d is not None:
        return d / 2
    return dflt


def _apply4(m: np.ndarray, pts3: np.ndarray) -> np.ndarray:
    """Apply a 4x4 matrix to an (N, 3) point array, returning an (N, 3) array."""
    pts = np.asarray(pts3, dtype=float)
    homo = np.hstack([pts, np.ones((len(pts), 1))])
    out = (m @ homo.T).T
    w = out[:, 3:4]
    return out[:, :3] / np.where(w == 0, 1.0, w)


# ---------------------------------------------------------------------------
# Section: copier matrix generators (BOSL2 function form, returning matrices)
# ---------------------------------------------------------------------------


def move_copies(a=([0, 0, 0],)) -> list[np.ndarray]:
    """One translation matrix per offset in *a* (BOSL2 move_copies())."""
    return [_translate4(pos) for pos in a]


def line_copies(spacing=None, n=None, l=None, p1=None, p2=None) -> list[np.ndarray]:
    """Translation matrices evenly spread along a line (BOSL2 line_copies())."""
    if l is not None:
        ll = _scalar_vec3(l, 0.0)
    elif spacing is not None and n is not None:
        ll = (n - 1) * _scalar_vec3(spacing, 0.0)
    elif p1 is not None and p2 is not None:
        ll = _scalar_vec3(np.asarray(p2, dtype=float) - np.asarray(p1, dtype=float), 0.0)
    else:
        ll = None
    if n is not None:
        cnt = int(n)
    elif spacing is not None and ll is not None:
        cnt = int(math.floor(np.linalg.norm(ll) / np.linalg.norm(_scalar_vec3(spacing, 0.0)) + 1.000001))
    else:
        cnt = 2
    if cnt <= 1:
        spc = np.zeros(3)
    elif spacing is None and ll is not None:
        spc = ll / (cnt - 1)
    elif _is_num(spacing) and ll is not None:
        spc = ll / (cnt - 1)
    else:
        spc = _scalar_vec3(spacing, 0.0)
    spos = _scalar_vec3(p1, 0.0) if p1 is not None else -(cnt - 1) / 2 * spc
    return [_translate4(i * spc + spos) for i in range(cnt)]


def _axis_copies(direction, spacing, n, l, sp) -> list[np.ndarray]:
    dirv = np.asarray(direction, dtype=float)
    sp_pt = (sp * dirv) if _is_num(sp) else (np.asarray(sp, dtype=float) if sp is not None else None)
    if isinstance(spacing, (list, tuple, np.ndarray)):  # explicit positions along the axis
        base = sp_pt if sp_pt is not None else np.zeros(3)
        return [_translate4(base + float(s) * dirv) for s in spacing]
    lv = (l * dirv) if l is not None else None
    spv = (spacing * dirv) if spacing is not None else None
    return line_copies(spacing=spv, n=n, l=lv, p1=sp_pt)


def xcopies(spacing=None, n=None, l=None, sp=None) -> list[np.ndarray]:
    """Copies spread along the X axis (BOSL2 xcopies())."""
    return _axis_copies(RIGHT, spacing, n, l, sp)


def ycopies(spacing=None, n=None, l=None, sp=None) -> list[np.ndarray]:
    """Copies spread along the Y axis (BOSL2 ycopies())."""
    return _axis_copies(BACK, spacing, n, l, sp)


def zcopies(spacing=None, n=None, l=None, sp=None) -> list[np.ndarray]:
    """Copies spread along the Z axis (BOSL2 zcopies())."""
    return _axis_copies(UP, spacing, n, l, sp)


def grid_copies(spacing=None, n=None, size=None, stagger=False, inside=None, nonzero=None,
                axes="xy") -> list[np.ndarray]:
    """Copies laid out in a square or staggered (hex) grid (BOSL2 grid_copies())."""
    assert stagger in (False, True, "alt"), "grid_copies(): stagger must be False, True or 'alt'."
    assert len(axes) == 2 and axes[0] in "xyz" and axes[1] in "xyz" and axes[0] != axes[1], \
        "grid_copies(): invalid axes."
    ai = {"x": 0, "y": 1, "z": 2}

    def permax(pt):
        out = [0.0, 0.0, 0.0]
        out[ai[axes[0]]] = pt[0]
        out[ai[axes[1]]] = pt[1]
        return np.array(out)

    bounds = None
    if inside is not None:
        from bosl2.paths import Path  # lazy: point-in-polygon test
        arr = np.asarray(inside, dtype=float)
        bounds = [arr.min(axis=0), arr.max(axis=0)]

    if size is not None:
        size = [float(size), float(size)] if _is_num(size) else [float(size[0]), float(size[1])]
    elif bounds is not None:
        size = [2 * max(abs(bounds[0][i]), abs(bounds[1][i])) for i in range(2)]

    if _is_num(spacing):
        from bosl2.transforms import polar_to_xy
        spacing = polar_to_xy(spacing, 60) if stagger is not False else [spacing, spacing]
    elif isinstance(spacing, (list, tuple, np.ndarray)):
        spacing = [float(spacing[0]), float(spacing[1])]
    elif size is not None:
        if _is_num(n):
            spacing = [size[0] / (n - 1), size[1] / (n - 1)]
        elif isinstance(n, (list, tuple, np.ndarray)):
            spacing = [size[0] / (n[0] - 1), size[1] / (n[1] - 1)]
        else:
            div = [1, 1] if stagger is False else [2, 2]
            spacing = [size[0] / div[0], size[1] / div[1]]

    if _is_num(n):
        n = [int(n), int(n)]
    elif isinstance(n, (list, tuple, np.ndarray)):
        n = [int(n[0]), int(n[1])]
    elif size is not None and spacing is not None:
        n = [int(math.floor(size[0] / spacing[0])) + 1, int(math.floor(size[1] / spacing[1])) + 1]
    else:
        n = [2, 2]

    spacing = np.asarray(spacing, dtype=float)
    offset = spacing * (np.asarray(n) - 1) / 2

    def keep(pos):
        if inside is None:
            return True
        from bosl2.paths import Path
        return Path._point_in_polygon(pos, inside, nonzero=bool(nonzero)) >= 0

    mats = []
    if stagger is False:
        for row in range(n[1]):
            for col in range(n[0]):
                pos = np.array([col, row]) * spacing - offset
                if keep(pos):
                    mats.append(_translate4(permax(pos)))
    else:
        staggermod = 1 if stagger == "alt" else 0
        cols1 = math.ceil(n[0] / 2)
        cols2 = n[0] - cols1
        for row in range(n[1]):
            rowcols = cols1 if (row % 2) == staggermod else cols2
            for col in range(rowcols):
                rowdx = spacing[0] if (row % 2) != staggermod else 0.0
                pos = np.array([2 * col, row]) * spacing + np.array([rowdx, 0.0]) - offset
                if keep(pos):
                    mats.append(_translate4(permax(pos)))
    return mats


def rot_copies(rots=None, v=None, cp=(0, 0, 0), n=None, sa=0, offset=0, delta=(0, 0, 0),
               subrot=True) -> list[np.ndarray]:
    """Rotated copies about an axis, optionally offset into a ring (BOSL2 rot_copies())."""
    assert subrot or np.linalg.norm(_scalar_vec3(delta, 0.0)) > 0, \
        "rot_copies(): subrot can only be False when delta is nonzero."
    sang = sa + offset
    if n is not None:
        angs = [] if n <= 0 else [i / n * 360 + sang for i in range(n)]
    elif rots:
        angs = [float(a) for a in rots]
    else:
        angs = []
    cpv, deltav = _scalar_vec3(cp, 0.0), _scalar_vec3(delta, 0.0)
    mats = []
    for ang in angs:
        m = (_translate4(cpv) @ _rot4(ang, v) @ _translate4(deltav)
             @ _rot4(0 if subrot else ang, v, reverse=True) @ _translate4(-cpv))
        mats.append(m)
    return mats


def xrot_copies(rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True) -> list[np.ndarray]:
    """Rotated copies around the X axis, optionally into a ring of radius *r* (BOSL2 xrot_copies())."""
    rr = _radius(r=r, d=d, dflt=0)
    return rot_copies(rots=rots, v=RIGHT, cp=cp, n=n, sa=sa, delta=[0, rr, 0], subrot=subrot)


def yrot_copies(rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True) -> list[np.ndarray]:
    """Rotated copies around the Y axis, optionally into a ring of radius *r* (BOSL2 yrot_copies())."""
    rr = _radius(r=r, d=d, dflt=0)
    return rot_copies(rots=rots, v=BACK, cp=cp, n=n, sa=sa, delta=[-rr, 0, 0], subrot=subrot)


def zrot_copies(rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True) -> list[np.ndarray]:
    """Rotated copies around the Z axis, optionally into a ring of radius *r* (BOSL2 zrot_copies())."""
    rr = _radius(r=r, d=d, dflt=0)
    return rot_copies(rots=rots, v=UP, cp=cp, n=n, sa=sa, delta=[rr, 0, 0], subrot=subrot)


def arc_copies(n=6, r=None, rx=None, ry=None, d=None, dx=None, dy=None, sa=0, ea=360,
               rot=True) -> list[np.ndarray]:
    """Copies spread along an (elliptical) arc in the XY plane (BOSL2 arc_copies())."""
    rxv = _radius(r1=rx, r=r, d1=dx, d=d, dflt=1)
    ryv = _radius(r1=ry, r=r, d1=dy, d=d, dflt=1)
    sa, ea = sa % 360, ea % 360
    extra_n = 1 if abs(ea - sa) < 0.01 else 0
    delt = (((360.0 if ea <= sa else 0) + ea - sa)) / (n - 1 + extra_n)
    mats = []
    for i in range(n):
        ang = sa + i * delt
        pos = [rxv * math.cos(math.radians(ang)), ryv * math.sin(math.radians(ang)), 0]
        ang2 = math.degrees(math.atan2(ryv * math.sin(math.radians(ang)),
                                       rxv * math.cos(math.radians(ang)))) if rot else 0
        mats.append(_translate4(pos) @ _rot4(ang2))
    return mats


def sphere_copies(n=100, r=None, d=None, cone_ang=90, scale=(1, 1, 1), perp=True) -> list[np.ndarray]:
    """Copies spread over a sphere/ellipsoid by the golden-spiral method (BOSL2 sphere_copies())."""
    rr = _radius(r=r, d=d, dflt=50)
    cnt = math.ceil(n / (cone_ang / 180))
    scalev = _scalar_vec3(scale, 1.0)
    mats = []
    for x in range(n):
        theta = (180 * (1 + math.sqrt(5)) * (x + 0.5)) % 360
        phi = math.degrees(math.acos(1 - 2 * (x + 0.5) / cnt))
        xyz = _spherical_to_xyz(rr, theta, phi)
        pos = xyz * scalev
        m = _translate4(pos) @ (_rot_from_to4(UP, xyz) if perp else np.eye(4))
        mats.append(m)
    return mats


def path_copies(path, n=None, spacing=None, sp=None, dist=None, rotate_children=True,
                closed=None) -> list[np.ndarray]:
    """Copies placed along *path*, oriented to it (BOSL2 path_copies())."""
    from bosl2.paths import Path

    pts = [list(map(float, p)) for p in path]
    closed = bool(getattr(path, "closed", False)) if closed is None else closed
    length = Path._path_length(pts, closed=closed)
    if dist is not None:
        distances = sorted(float(x) for x in dist)
    elif sp is not None:
        if n is not None and spacing is not None:
            distances = [sp + i * spacing for i in range(n)]
        elif n is not None:
            distances = list(np.linspace(sp, length, n))
        else:
            distances = list(np.arange(sp, length, spacing))
    elif n is not None and spacing is None:
        distances = list(np.linspace(0, length, n, endpoint=not closed))
    else:
        cnt = n if n is not None else int(math.floor(length / spacing)) + (0 if closed else 1)
        ptlist = [i * spacing for i in range(cnt)]
        center = sum(ptlist) / len(ptlist)
        if closed:
            distances = sorted((e - center) % length for e in ptlist)
        else:
            distances = [e + length / 2 - center for e in ptlist]
    assert min(distances) >= -1e-9 and max(distances) <= length + 1e-9, "path_copies(): copies don't fit on the path."
    distances = [min(max(dst, 0.0), length) for dst in distances]
    cutlist = Path._path_cut_points(pts, distances, closed=closed, direction=True)
    planar = len(pts[0]) == 2
    mats = []
    for point, _ind, tangent, normal in cutlist:
        base = _translate4(point)
        if not rotate_children:
            rotm = np.eye(4)
        elif planar:
            rotm = _rot_from_to4([0, 1, 0], _scalar_vec3(normal, 0.0))
        else:
            rotm = _frame_map4(x=tangent, z=normal)
        mats.append(base @ rotm)
    return mats


def mirror_copy(v=(0, 0, 1), offset=0, cp=None) -> list[np.ndarray]:
    """The original plus a mirrored copy across the plane with normal *v* (BOSL2 mirror_copy())."""
    nv = _unit3(v)
    cpv = _scalar_vec3(cp, 0.0) if cp is not None and not _is_num(cp) else (cp * nv if _is_num(cp) else np.zeros(3))
    off = nv * offset
    return [_translate4(off), _translate4(cpv) @ _mirror4(nv) @ _translate4(-cpv) @ _translate4(off)]


def xflip_copy(offset=0, x=0) -> list[np.ndarray]:
    """The original plus a copy mirrored across the X=*x* plane (BOSL2 xflip_copy())."""
    return mirror_copy(v=[1, 0, 0], offset=offset, cp=[x, 0, 0])


def yflip_copy(offset=0, y=0) -> list[np.ndarray]:
    """The original plus a copy mirrored across the Y=*y* plane (BOSL2 yflip_copy())."""
    return mirror_copy(v=[0, 1, 0], offset=offset, cp=[0, y, 0])


def zflip_copy(offset=0, z=0) -> list[np.ndarray]:
    """The original plus a copy mirrored across the Z=*z* plane (BOSL2 zflip_copy())."""
    return mirror_copy(v=[0, 0, 1], offset=offset, cp=[0, 0, z])


# ---------------------------------------------------------------------------
# Section: Distributable mixin
# ---------------------------------------------------------------------------


class Distributable:
    """Mixin adding the distributors.scad copiers as methods.

    Inherited by :class:`~bosl2.shapes3d.Bosl2Solid`, :class:`~bosl2.paths.Path`, and
    :class:`~bosl2.paths.Path3D`. Each copier builds a list of transformation matrices and hands
    them to ``_distribute``, which every host class implements: a Bosl2Solid unions the geometry
    copies into a new solid; a Path / Path3D returns a plain ``list`` of the copied paths.
    """

    def _distribute(self, mats):  # pragma: no cover - overridden by every host class
        raise NotImplementedError("Distributable subclasses must implement _distribute().")

    def move_copies(self, a=([0, 0, 0],)):
        """Copy to each offset in *a*."""
        return self._distribute(move_copies(a))

    def xcopies(self, spacing=None, n=None, l=None, sp=None):
        """Copies spread along the X axis."""
        return self._distribute(xcopies(spacing, n, l, sp))

    def ycopies(self, spacing=None, n=None, l=None, sp=None):
        """Copies spread along the Y axis."""
        return self._distribute(ycopies(spacing, n, l, sp))

    def zcopies(self, spacing=None, n=None, l=None, sp=None):
        """Copies spread along the Z axis."""
        return self._distribute(zcopies(spacing, n, l, sp))

    def line_copies(self, spacing=None, n=None, l=None, p1=None, p2=None):
        """Copies spread along a line."""
        return self._distribute(line_copies(spacing, n, l, p1, p2))

    def grid_copies(self, spacing=None, n=None, size=None, stagger=False, inside=None,
                    nonzero=None, axes="xy"):
        """Copies in a square or staggered (hex) grid."""
        return self._distribute(grid_copies(spacing, n, size, stagger, inside, nonzero, axes))

    def rot_copies(self, rots=None, v=None, cp=(0, 0, 0), n=None, sa=0, offset=0, delta=(0, 0, 0),
                   subrot=True):
        """Rotated copies about an axis (optionally into a ring via *delta*)."""
        return self._distribute(rot_copies(rots, v, cp, n, sa, offset, delta, subrot))

    def xrot_copies(self, rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True):
        """Rotated copies around the X axis."""
        return self._distribute(xrot_copies(rots, cp, n, sa, r, d, subrot))

    def yrot_copies(self, rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True):
        """Rotated copies around the Y axis."""
        return self._distribute(yrot_copies(rots, cp, n, sa, r, d, subrot))

    def zrot_copies(self, rots=None, cp=(0, 0, 0), n=None, sa=0, r=None, d=None, subrot=True):
        """Rotated copies around the Z axis."""
        return self._distribute(zrot_copies(rots, cp, n, sa, r, d, subrot))

    def arc_copies(self, n=6, r=None, rx=None, ry=None, d=None, dx=None, dy=None, sa=0, ea=360,
                   rot=True):
        """Copies spread along an (elliptical) arc in the XY plane."""
        return self._distribute(arc_copies(n, r, rx, ry, d, dx, dy, sa, ea, rot))

    def sphere_copies(self, n=100, r=None, d=None, cone_ang=90, scale=(1, 1, 1), perp=True):
        """Copies spread over a sphere/ellipsoid surface."""
        return self._distribute(sphere_copies(n, r, d, cone_ang, scale, perp))

    def path_copies(self, path, n=None, spacing=None, sp=None, dist=None, rotate_children=True,
                    closed=None):
        """Copies placed along *path*, oriented to it."""
        return self._distribute(path_copies(path, n, spacing, sp, dist, rotate_children, closed))

    def mirror_copy(self, v=(0, 0, 1), offset=0, cp=None):
        """This object plus a copy mirrored across the plane with normal *v*."""
        return self._distribute(mirror_copy(v, offset, cp))

    def xflip_copy(self, offset=0, x=0):
        """This object plus a copy mirrored across the X=*x* plane."""
        return self._distribute(xflip_copy(offset, x))

    def yflip_copy(self, offset=0, y=0):
        """This object plus a copy mirrored across the Y=*y* plane."""
        return self._distribute(yflip_copy(offset, y))

    def zflip_copy(self, offset=0, z=0):
        """This object plus a copy mirrored across the Z=*z* plane."""
        return self._distribute(zflip_copy(offset, z))


# ---------------------------------------------------------------------------
# Section: distributing a list of distinct children
# ---------------------------------------------------------------------------


def distribute(children, spacing=None, sizes=None, dir=RIGHT, l=None):
    """Space a LIST of distinct solids out along *dir* so they don't overlap (BOSL2 distribute()).

    Unlike the copiers (which duplicate one shape), this lays out several different children in
    order. *sizes* gives each child's extent along *dir*; if omitted it is read from each child's
    bounding box. Give *spacing* (gap between children) or *l* (total length to fill). Returns the
    union of the positioned children.
    """
    children = list(children)
    dirv = _unit3(dir)
    cnt = len(children)
    assert cnt >= 1, "distribute(): needs at least one child."
    if sizes is None:
        extents = [float(abs(np.asarray(c.bounds()[1], dtype=float) @ dirv
                            - np.asarray(c.bounds()[0], dtype=float) @ dirv)) for c in children]
    else:
        extents = [float(s) for s in sizes]
    gaps = [0.0] if cnt < 2 else [extents[i] / 2 + extents[i + 1] / 2 for i in range(cnt - 1)]
    spc = ((l - sum(gaps)) / (cnt - 1)) if (l is not None and cnt > 1) else (spacing if spacing is not None else 10)
    gaps2 = [g + spc for g in gaps]
    positions = np.cumsum([0.0] + gaps2)
    start = -sum(gaps2) / 2 * dirv
    placed = [c.translate((start + positions[i] * dirv).tolist()) for i, c in enumerate(children)]
    out = placed[0]
    for c in placed[1:]:
        out = out | c
    return out


def xdistribute(children, spacing=None, sizes=None, l=None):
    """Distribute distinct children along the X axis (BOSL2 xdistribute())."""
    return distribute(children, spacing=spacing, sizes=sizes, dir=RIGHT, l=l)


def ydistribute(children, spacing=None, sizes=None, l=None):
    """Distribute distinct children along the Y axis (BOSL2 ydistribute())."""
    return distribute(children, spacing=spacing, sizes=sizes, dir=BACK, l=l)


def zdistribute(children, spacing=None, sizes=None, l=None):
    """Distribute distinct children along the Z axis (BOSL2 zdistribute())."""
    return distribute(children, spacing=spacing, sizes=sizes, dir=UP, l=l)
