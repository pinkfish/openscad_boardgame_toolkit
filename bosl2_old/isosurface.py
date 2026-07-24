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

# LibFile: bosl2/isosurface.py
#    Pure-Python port of the 3-D core of BOSL2's isosurface.scad: :func:`isosurface` meshes the
#    level set of a scalar field over a voxel grid (marching cubes) into a :class:`~bosl2.vnf.VNF`,
#    the ``mb_*`` functions are metaball field primitives, and :func:`metaballs` sums transformed
#    field primitives and meshes the result into a blobby surface.
#
#    The field-primitive formulas are ported directly from BOSL2 and checked point-for-point in
#    tests/test_bosl2_reorient.py; the meshes are verified geometrically (a lone metaball is a
#    sphere; overlapping ones merge). The mesh uses the standard Paul Bourke marching-cubes table
#    (bosl2/_mctable.py), so its triangulation is not vertex-identical to BOSL2's, but the surface
#    it encloses is the same; face winding is fixed to outward via the VNF's signed volume.
#
#    NOT ported (a follow-up): the 2-D analogues ``contour`` / ``metaballs2d`` and their ``mb_*2d``
#    primitives, ``mb_cyl`` (a revolved-profile field), and the debug/anchor machinery.
#
# FileSummary: Isosurface meshing (marching cubes), metaball field primitives, and metaballs().
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

from bosl2._mctable import TRI_TABLE, EDGE_CORNERS, CORNER_OFFSETS

__all__ = [
    "isosurface", "metaballs", "mb_sphere", "mb_cuboid", "mb_torus", "mb_capsule", "mb_disk",
    "mb_octahedron", "mb_connector", "Metaball",
]

INF = math.inf


# ---------------------------------------------------------------------------
# Section: grid / bounding-box helpers
# ---------------------------------------------------------------------------


def _to_bbox(bounding_box):
    if isinstance(bounding_box, (int, float)):
        hb = 0.5 * bounding_box
        return np.array([[-hb, -hb, -hb], [hb, hb, hb]], dtype=float)
    return np.asarray(bounding_box, dtype=float)


def _voxsize_vec(voxel_size):
    return np.array([voxel_size] * 3, dtype=float) if isinstance(voxel_size, (int, float)) \
        else np.asarray(voxel_size, dtype=float)


def _resolve_grid(bbox, voxel_size, voxel_count, exact_bounds):
    """Return (bbox, voxsize) as numpy arrays, growing the box to hold whole voxels unless exact."""
    if voxel_size is not None:
        voxsize = _voxsize_vec(voxel_size)
    else:
        size = bbox[1] - bbox[0]
        voxvol = float(size[0] * size[1] * size[2]) / (voxel_count if voxel_count else 22 ** 3)
        voxsize = np.array([voxvol ** (1 / 3)] * 3, dtype=float)
    if exact_bounds:
        return bbox, voxsize
    center = (bbox[0] + bbox[1]) / 2
    nums = np.ceil((bbox[1] - bbox[0]) / voxsize)
    half = 0.5 * voxsize * nums
    return np.array([center - half, center + half]), voxsize


def _grid_axes(bbox, voxsize):
    def axis(lo, hi, step):
        n = int(math.floor((hi - lo) / step + 0.5)) + 1
        return lo + step * np.arange(n)
    return (axis(bbox[0][0], bbox[1][0], voxsize[0]),
            axis(bbox[0][1], bbox[1][1], voxsize[1]),
            axis(bbox[0][2], bbox[1][2], voxsize[2]))


def _sample_field(f, xs, ys, zs):
    """Evaluate the field *f* at every grid point, returning an (nx, ny, nz) array.

    *f* may be a precomputed 3-D array, a vectorised callable ((N, 3) -> (N,)), or a scalar callable
    (a point -> a value)."""
    if isinstance(f, np.ndarray) or (isinstance(f, (list, tuple)) and not callable(f)):
        return np.asarray(f, dtype=float)
    gx, gy, gz = np.meshgrid(xs, ys, zs, indexing="ij")
    pts = np.stack([gx.ravel(), gy.ravel(), gz.ravel()], axis=1)
    with np.errstate(all="ignore"):
        try:
            vals = np.asarray(f(pts), dtype=float)
            if vals.shape == (len(pts),):
                return vals.reshape(gx.shape)
        except (ValueError, TypeError, IndexError, np.exceptions.AxisError):
            pass
        vals = np.array([float(f([p[0], p[1], p[2]])) for p in pts])
    return vals.reshape(gx.shape)


# ---------------------------------------------------------------------------
# Section: marching cubes
# ---------------------------------------------------------------------------


def isosurface(f, isovalue, bounding_box=None, voxel_size=None, voxel_count=None, closed=True,
               reverse=False, exact_bounds=False):
    """Mesh the level set of a scalar field *f* at *isovalue* into a VNF (BOSL2 isosurface()).

    The solid is the region where ``f >= isovalue`` (a single number) or, for a range
    ``[lo, hi]``, where ``lo <= f <= hi`` collapses to ``f >= lo`` (``hi`` unbounded) or ``f <= hi``
    (``lo`` unbounded, i.e. reversed). *f* is a callable (vectorised ``(N,3)->(N,)`` or scalar
    ``point->value``) or a precomputed 3-D array. Give *voxel_size* or *voxel_count* to control
    resolution; the bounding box grows to whole voxels unless *exact_bounds*.

    Returns:
        A :class:`~bosl2.vnf.VNF`.

    Examples:
        The level set of a wobbly sphere field:

        .. pythonscad-example::

            def field(p):
                import numpy as np
                x, y, z = p[:, 0], p[:, 1], p[:, 2]
                return 20 / np.sqrt(x*x + y*y + z*z) + 3 * np.sin(x / 3)
            isosurface(field, 1, bounding_box=60, voxel_size=2).polyhedron().show()
    """
    from bosl2.vnf import VNF

    if isinstance(isovalue, (list, tuple)):
        lo, hi = float(isovalue[0]), float(isovalue[1])
        assert lo < hi, "isovalue range must be [min, max] with min < max."
        if math.isinf(lo):
            iso, reverse = hi, not reverse   # f <= hi
        else:
            iso = lo                         # f >= lo
    else:
        iso = float(isovalue)

    if isinstance(f, np.ndarray) or (isinstance(f, (list, tuple)) and not callable(f)):
        F = np.asarray(f, dtype=float)
        if bounding_box is None:
            vs = _voxsize_vec(voxel_size if voxel_size is not None else 1.0)
            half = 0.5 * vs * (np.array(F.shape) - 1)
            bbox, voxsize = np.array([-half, half]), vs
        else:
            bbox = _to_bbox(bounding_box)
            voxsize = (bbox[1] - bbox[0]) / (np.array(F.shape) - 1)
        xs, ys, zs = _grid_axes(bbox, voxsize)
    else:
        assert bounding_box is not None, "isosurface(): a callable field needs a bounding_box."
        bbox, voxsize = _resolve_grid(_to_bbox(bounding_box), voxel_size, voxel_count, exact_bounds)
        xs, ys, zs = _grid_axes(bbox, voxsize)
        F = _sample_field(f, xs, ys, zs)

    verts, faces = _marching_cubes(F, xs, ys, zs, iso, closed)
    vnf = VNF(verts, faces)
    if len(faces):
        vol = vnf.volume()
        if (vol < 0) != reverse:
            vnf = vnf.reverse()
    return vnf


def _marching_cubes(F, xs, ys, zs, iso, closed):
    if closed:
        F = np.pad(F, 1, mode="constant", constant_values=-1e30)
        xs = np.concatenate([[xs[0] - (xs[1] - xs[0])], xs, [xs[-1] + (xs[-1] - xs[-2])]])
        ys = np.concatenate([[ys[0] - (ys[1] - ys[0])], ys, [ys[-1] + (ys[-1] - ys[-2])]])
        zs = np.concatenate([[zs[0] - (zs[1] - zs[0])], zs, [zs[-1] + (zs[-1] - zs[-2])]])
    nx, ny, nz = F.shape
    coords = (xs, ys, zs)
    verts = []
    faces = []
    cache = {}

    def corner_pos(ci, i, j, k):
        di, dj, dk = CORNER_OFFSETS[ci]
        return (i + di, j + dj, k + dk)

    def edge_vertex(ca, cb):
        key = (ca, cb) if ca < cb else (cb, ca)
        idx = cache.get(key)
        if idx is not None:
            return idx
        (ia, ja, ka), (ib, jb, kb) = key
        va, vb = F[ia, ja, ka], F[ib, jb, kb]
        t = 0.5 if va == vb else (iso - va) / (vb - va)
        pa = np.array([coords[0][ia], coords[1][ja], coords[2][ka]])
        pb = np.array([coords[0][ib], coords[1][jb], coords[2][kb]])
        idx = len(verts)
        verts.append(list(pa + t * (pb - pa)))
        cache[key] = idx
        return idx

    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                cvals = [F[i + CORNER_OFFSETS[c][0], j + CORNER_OFFSETS[c][1], k + CORNER_OFFSETS[c][2]]
                         for c in range(8)]
                cubeindex = 0
                for c in range(8):
                    if cvals[c] < iso:
                        cubeindex |= 1 << c
                tris = TRI_TABLE[cubeindex]
                if not tris:
                    continue
                for t in range(0, len(tris), 3):
                    face = []
                    for e in tris[t:t + 3]:
                        c0, c1 = EDGE_CORNERS[e]
                        face.append(edge_vertex(corner_pos(c0, i, j, k), corner_pos(c1, i, j, k)))
                    if face[0] != face[1] and face[1] != face[2] and face[0] != face[2]:
                        faces.append(face)
    return verts, faces


# ---------------------------------------------------------------------------
# Section: metaball field primitives
# ---------------------------------------------------------------------------


def _mb_cutoff(dist, cutoff):
    if not math.isfinite(cutoff):
        return np.ones_like(dist)
    out = np.zeros_like(dist)
    m = dist < cutoff
    out[m] = 0.5 * (np.cos(np.pi * (dist[m] / cutoff) ** 4) + 1)
    return out


def _mb_field(dist, base, influence, cutoff, neg):
    """Assemble a metaball field from ``base/dist`` with influence and cutoff (dist may be 0)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = base / dist
        v = ratio if influence == 1 else np.power(ratio, 1.0 / influence)
    if math.isfinite(cutoff):
        v = _mb_cutoff(dist, cutoff) * v
    return neg * v


def _squircle_se_exponent(squareness):
    s = min(0.998, squareness)
    rho = 1 + s * (math.sqrt(2) - 1)
    x = rho / math.sqrt(2)
    return math.log(0.5) / math.log(x)


class Metaball:
    """A metaball field primitive: a vectorised scalar field ``field(pts)`` over ``(N, 3)`` points,
    plus its sign (``neg``). Combine several with :func:`metaballs`."""

    def __init__(self, field, neg=1):
        self.field = field
        self.neg = neg

    def __call__(self, pt):
        return float(self.field(np.atleast_2d(np.asarray(pt, dtype=float)))[0])


def _radius(r=None, d=None):
    return r if r is not None else (d / 2 if d is not None else None)


def mb_sphere(r=None, cutoff=INF, influence=1, negative=False, d=None):
    """A spherical metaball field of radius *r* (BOSL2 mb_sphere())."""
    rr = _radius(r, d)
    assert rr and rr > 0, "mb_sphere(): need a positive r or d."
    neg = -1 if negative else 1

    def field(pts):
        dist = np.linalg.norm(pts, axis=1)
        return _mb_field(dist, rr, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_cuboid(size, squareness=0.5, cutoff=INF, influence=1, negative=False):
    """A rounded-cuboid metaball field (BOSL2 mb_cuboid()). *squareness* 0..1: 0 round, 1 square."""
    assert 0 <= squareness <= 1, "mb_cuboid(): squareness must be in [0, 1]."
    xp = _squircle_se_exponent(squareness)
    inv = np.array([2 / size] * 3) if isinstance(size, (int, float)) else 2 / np.asarray(size, dtype=float)
    neg = -1 if negative else 1

    def field(pts):
        p = np.abs(pts * inv)
        dist = np.max(p, axis=1) if xp >= 1100 else np.sum(p ** xp, axis=1) ** (1 / xp)
        return _mb_field(dist, 1.0, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_torus(r_maj=None, r_min=None, cutoff=INF, influence=1, negative=False, d_maj=None, d_min=None):
    """A torus metaball field, major radius *r_maj*, tube radius *r_min* (BOSL2 mb_torus())."""
    rmaj, rmin = _radius(r_maj, d_maj), _radius(r_min, d_min)
    assert rmaj and rmin and rmaj > 0 and rmin > 0, "mb_torus(): need positive r_maj and r_min."
    neg = -1 if negative else 1

    def field(pts):
        rad = np.hypot(pts[:, 0], pts[:, 1]) - rmaj
        dist = np.hypot(rad, pts[:, 2])
        return _mb_field(dist, rmin, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_capsule(h=None, r=None, cutoff=INF, influence=1, negative=False, d=None):
    """A capsule (round-ended cylinder) metaball field, total length *h*, radius *r* (BOSL2 mb_capsule())."""
    rr = _radius(r, d)
    assert h and rr and h > 0 and rr > 0, "mb_capsule(): need positive h and r."
    hl = (h - 2 * rr) / 2
    assert hl > 0, "mb_capsule(): total length must exceed the two rounded ends."
    neg = -1 if negative else 1

    def field(pts):
        z = pts[:, 2]
        rxy = np.hypot(pts[:, 0], pts[:, 1])
        below, above = z < -hl, z > hl
        dist = np.where(below, np.hypot(rxy, z + hl),
                        np.where(above, np.hypot(rxy, z - hl), rxy))
        return _mb_field(dist, rr, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_disk(h=None, r=None, cutoff=INF, influence=1, negative=False, d=None):
    """A rounded-edge disk metaball field, thickness *h*, outer radius *r* (BOSL2 mb_disk())."""
    rr = _radius(r, d)
    assert h and rr and h > 0 and rr > 0, "mb_disk(): need positive h and r."
    hl = h / 2
    ri = rr - hl
    assert ri > 0, "mb_disk(): diameter must exceed the thickness."
    neg = -1 if negative else 1

    def field(pts):
        rxy = np.hypot(pts[:, 0], pts[:, 1])
        z = pts[:, 2]
        dist = np.where(rxy < ri, np.abs(z), np.hypot(rxy - ri, z))
        return _mb_field(dist, hl, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_octahedron(size, squareness=0.5, cutoff=INF, influence=1, negative=False):
    """A rounded-octahedron metaball field (BOSL2 mb_octahedron())."""
    assert 0 <= squareness <= 1, "mb_octahedron(): squareness must be in [0, 1]."
    xp = _squircle_se_exponent(squareness)

    def _octdist(p):
        if xp >= 1100:
            return np.abs(p[:, 0]) + np.abs(p[:, 1]) + np.abs(p[:, 2])
        a = np.abs(p[:, 0] + p[:, 1] + p[:, 2]) ** xp
        b = np.abs(-p[:, 0] - p[:, 1] + p[:, 2]) ** xp
        c = np.abs(-p[:, 0] + p[:, 1] - p[:, 2]) ** xp
        e = np.abs(p[:, 0] - p[:, 1] - p[:, 2]) ** xp
        return (a + b + c + e) ** (1 / xp)

    corr = 1.0 / _octdist(np.array([[1 / 3, 1 / 3, 1 / 3]]))[0]
    scale = np.array([2 / size] * 3) if isinstance(size, (int, float)) else 2 / np.asarray(size, dtype=float)
    inv = corr * scale
    neg = -1 if negative else 1

    def field(pts):
        dist = _octdist(pts * inv)
        return _mb_field(dist, 1.0, influence, cutoff, neg)
    return Metaball(field, neg)


def mb_connector(p1, p2, r=None, cutoff=INF, influence=1, negative=False, d=None):
    """A capsule metaball field spanning from *p1* to *p2* with radius *r* (BOSL2 mb_connector())."""
    from bosl2.transforms import rot_from_to, axis_angle_matrix

    rr = _radius(r, d)
    a, b = np.asarray(p1, dtype=float), np.asarray(p2, dtype=float)
    assert rr and rr > 0 and not np.array_equal(a, b), "mb_connector(): need distinct points and positive r."
    neg = -1 if negative else 1
    dc = b - a
    h = float(np.linalg.norm(dc)) / 2
    ang, axis = rot_from_to(dc, [0, 0, 1])          # rotate the axis onto +Z
    m3 = np.asarray(axis_angle_matrix(ang, axis), dtype=float)

    def field(pts):
        local = (pts - (a + b) / 2) @ m3.T          # center on the midpoint, align to +Z
        z = local[:, 2]
        rxy = np.hypot(local[:, 0], local[:, 1])
        below, above = z < -h, z > h
        dist = np.where(below, np.hypot(rxy, z + h),
                        np.where(above, np.hypot(rxy, z - h), rxy))
        return _mb_field(dist, rr, influence, cutoff, neg)
    return Metaball(field, neg)


# ---------------------------------------------------------------------------
# Section: metaballs
# ---------------------------------------------------------------------------


def _to_matrix(t):
    """A 4x4 transform from a 4x4 matrix or a 3-vector (translation)."""
    t = np.asarray(t, dtype=float)
    if t.shape == (4, 4):
        return t
    m = np.eye(4)
    m[:3, 3] = t[:3]
    return m


def _parse_spec(spec):
    """Normalise a metaball spec into a list of (4x4 transform, Metaball) pairs.

    Accepts a list of ``(transform, metaball)`` pairs or the BOSL2 flat form
    ``[transform, metaball, transform, metaball, ...]``."""
    items = list(spec)
    if items and isinstance(items[0], Metaball):
        raise AssertionError("metaballs(): spec must be (transform, metaball) pairs.")
    if items and isinstance(items[0], (tuple, list)) and len(items[0]) == 2 and isinstance(items[0][1], Metaball):
        return [(_to_matrix(t), mb) for t, mb in items]
    assert len(items) % 2 == 0, "metaballs(): flat spec must alternate transform and metaball."
    return [(_to_matrix(items[i]), items[i + 1]) for i in range(0, len(items), 2)]


def metaballs(spec, bounding_box, voxel_size=None, voxel_count=None, isovalue=1, closed=True,
              exact_bounds=False):
    """Mesh a set of transformed metaball field primitives into a blobby surface (BOSL2 metaballs()).

    *spec* is a list of ``(transform, metaball)`` pairs (or the BOSL2 flat
    ``[transform, metaball, ...]`` form), where *transform* is a 4x4 matrix or a 3-vector position
    and *metaball* comes from ``mb_sphere`` / ``mb_cuboid`` / ``mb_torus`` / ``mb_capsule`` /
    ``mb_disk`` / ``mb_octahedron`` / ``mb_connector``. The fields sum, and the surface is drawn
    where the total reaches *isovalue*.

    Returns:
        A :class:`~bosl2.vnf.VNF`.

    Examples:
        Two spheres merging into a peanut:

        .. pythonscad-example::

            spec = [([-14, 0, 0], mb_sphere(12)), ([14, 0, 0], mb_sphere(12))]
            metaballs(spec, bounding_box=[[-40, -20, -20], [40, 20, 20]], voxel_size=2).polyhedron().show()
    """
    pairs = _parse_spec(spec)
    assert pairs, "metaballs(): the spec is empty."
    bbox, voxsize = _resolve_grid(_to_bbox(bounding_box), voxel_size, voxel_count, exact_bounds)
    invs = [np.linalg.inv(t) for t, _ in pairs]

    def field(pts):
        homo = np.hstack([pts, np.ones((len(pts), 1))])
        total = np.zeros(len(pts))
        for (t, ball), inv in zip(pairs, invs):
            local = (inv @ homo.T).T[:, :3]
            total += ball.field(local)
        return total

    return isosurface(field, isovalue, bounding_box=bbox, voxel_size=voxsize, closed=closed,
                      exact_bounds=True)
