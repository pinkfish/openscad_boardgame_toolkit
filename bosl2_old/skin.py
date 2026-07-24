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

# LibFile: bosl2/skin.py
#    Pure-Python port of the surface generators from BOSL2's skin.scad, building
#    VNFs (bosl2/vnf.py) that render via polyhedron(). No osuse()/BOSL2 runtime
#    dependency.
#
#    Ported (function forms):
#      * sweep(shape, transforms)   -- skin a shape through a list of 4x4 transforms
#      * path_sweep(shape, path)    -- sweep along a 2-D/3-D path. Frame methods
#          "incremental" (rotation-minimizing frame via the double-reflection
#          algorithm), "manual" (caller normals) and "natural" (the curve's own
#          normal); twist, per-point/interpolated scale, open & closed paths,
#          flat caps on/off, user tangents, and the transforms=True mode.
#      * skin(profiles, slices)     -- blend a stack of profiles (methods "direct"
#          and "reindex")
#      * linear_sweep(region, h)    -- extrude an outline with twist/scale/shift
#      * rotate_sweep(shape, angle) -- revolve a profile around Z
#      * spiral_sweep(poly, h, r)   -- sweep a cross-section along a helix
#      * path_sweep2d(shape, path)  -- sweep a 2-D shape along a 2-D path
#      * rot_resample(rotlist, n)   -- resample a transform list along its screw motion
#      * subdivide_and_slice() / slice_profiles() -- the skin() profile helpers
#
#    NOT ported (they depend on machinery this pure-Python port does not
#    implement, and nothing in the toolkit needs them): the texture engine
#    (texture()/tex_* options), the attachment/anchor system (anchors,
#    sweep_attach()), rounded/chamfered "fancy" end caps, region shapes with
#    holes (use a native linear_extrude/CSG), the skin() "distance"/
#    "fast_distance"/"tangent" vertex-matching methods (and associate_vertices()),
#    and spiral_sweep()'s lead-in tapers.
#
# FileSummary: Skin/sweep/revolve 2-D profiles into VNF surfaces (BOSL2 skin.scad).
# FileGroup: BOSL2

import math

import numpy as np

from bosl2.transforms import apply as _apply, rot_about_axis, rot_decode, rot_inverse
from bosl2.constants import Vec3
from bosl2.vnf import VNF

UP = Vec3([0.0, 0.0, 1.0])
BACK = Vec3([0.0, 1.0, 0.0])


def _u(v) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(a))
    return a / n if n else a


def path3d(path) -> list:
    """Pad a 2-D (or 3-D) point list to 3-D with z=0."""
    return [[float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0] for p in path]


def clockwise_polygon(poly) -> list:
    """*poly* wound clockwise (reversed if its signed area is positive/CCW)."""
    from bosl2.paths import Path

    return list(poly) if Path._polygon_area(poly, signed=True) <= 0 else list(reversed(list(poly)))


def _translate4(p) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = [float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0]
    return m


def _zrot4(a: float) -> np.ndarray:
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    return m


def _scale4(s) -> np.ndarray:
    m = np.eye(4)
    m[0, 0], m[1, 1] = float(s[0]), float(s[1])
    if len(s) > 2:
        m[2, 2] = float(s[2])
    return m


def _xrot4(a: float) -> np.ndarray:
    r = math.radians(a)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4)
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    return m


def _segs(r: float) -> int:
    """OpenSCAD's default $fa=12/$fs=2 facet count for a circle of radius *r* (BOSL2 segs())."""
    return max(5, int(math.ceil(min(360.0 / 12.0, (2 * math.pi * abs(r)) / 2.0))))


def frame_map(x=None, y=None, z=None) -> np.ndarray:
    """The 4x4 rotation whose columns are the given orthonormal axes (BOSL2 frame_map()).

    Give any two of x/y/z (as 3-vectors); the third is filled in by the cross product."""
    xu = _u(x) if x is not None else None
    yu = _u(y) if y is not None else None
    zu = _u(z) if z is not None else None
    if xu is None:
        xu = np.cross(yu, zu)
    elif yu is None:
        yu = np.cross(zu, xu)
    elif zu is None:
        zu = np.cross(xu, yu)
    m = np.eye(4)
    m[:3, :3] = np.column_stack([xu, yu, zu])
    return m


def sweep(shape, transforms, closed: bool = False, caps=None, style: str = "min_edge") -> VNF:
    """Apply each 4x4 transform to the 2-D *shape* and skin the resulting profiles into a VNF.

    Args:
        shape:      a 2-D polygon (list of [x, y] points)
        transforms: list of 4x4 matrices, one per cross section along the path
        closed:     the sweep loops back on itself (no caps)
        caps:       cap the open ends (default: True/True open, none closed); bool or [bool, bool]
        style:      vnf_vertex_array quad-subdivision style
    """
    shape3 = np.asarray(path3d(shape), dtype=float)
    assert len(shape3) >= 3, "shape must be a path of at least 3 points."
    if closed:
        flatcaps = [False, False]
    elif caps is None:
        flatcaps = [True, True]
    elif isinstance(caps, bool):
        flatcaps = [caps, caps]
    else:
        flatcaps = [bool(caps[0]), bool(caps[1])]
    ntrans = len(transforms)
    assert ntrans >= 2, "transforms must be length 2 or more."
    hi = ntrans - (0 if closed else 1)
    points = [np.asarray(_apply(transforms[i % ntrans], shape3), dtype=float) for i in range(hi + 1)]
    return VNF.vertex_array(points, cap1=flatcaps[0], cap2=flatcaps[1], col_wrap=True, style=style)


def path_sweep(shape, path, method: str = "incremental", normal=None, closed: bool = False,
               twist: float = 0.0, twist_by_length: bool = True, scale=1, scale_by_length: bool = True,
               symmetry: int = 1, last_normal=None, tangent=None, uniform: bool = True,
               relaxed: bool = False, caps=None, style: str = "min_edge", transforms: bool = False):
    """Sweep the 2-D *shape* along the 2-D/3-D *path*, returning a VNF (or the transform list).

    *method* orients the cross section: "incremental" (rotation-minimizing frame), "manual"
    (using *normal* as a per-point normal list), or "natural" (the path's own normal). *twist*
    (degrees) and *scale* (scalar, 2-vector, per-point vector, or Nx2) are interpolated along the
    path. See BOSL2 path_sweep() for the full semantics.

    Examples:
        Sweeping a small square profile along a helical path into a solid:

        .. pythonscad-example::

            square = [[-3, -3], [3, -3], [3, 3], [-3, 3]]
            helix = [[10 * math.cos(t), 10 * math.sin(t), t * 3] for t in np.linspace(0, 3 * math.pi, 40)]
            path_sweep(square, helix).polyhedron().show()
    """
    from bosl2.paths import Path  # local: keep the import graph acyclic

    caps = False if closed else caps  # a closed loop has no ends to cap
    patharr = np.asarray(path3d(path), dtype=float)
    L = len(patharr)
    assert L >= 2, "path must have at least 2 points."

    if tangent is not None:
        tangents = np.array([_u(t) for t in path3d(tangent)])
    else:
        tangents = np.asarray(Path._path_tangents(patharr, closed=closed, uniform=uniform), dtype=float)

    # Resolve the initial/per-point normal.
    if normal is not None:
        narr = np.asarray(normal, dtype=float)
        if narr.ndim == 2:
            normals = np.array([_u(n) for n in narr])
            normal_single = normals[0]
        else:
            normal_single = _u(narr)
            normals = np.tile(normal_single, (L, 1))
    else:
        normal_single = np.asarray(BACK if (method == "incremental" and abs(tangents[0][2]) > 1 / math.sqrt(2)) else UP, dtype=float)
        normals = np.tile(normal_single, (L, 1))

    if twist_by_length:
        tpathfrac = np.asarray(Path._path_length_fractions(patharr, closed), dtype=float)
    else:
        tpathfrac = np.array([i / (L - (0 if closed else 1)) for i in range(L + 1)])
    if scale_by_length:
        spathfrac = np.asarray(Path._path_length_fractions(patharr, closed), dtype=float)
    else:
        spathfrac = np.array([i / (L - (0 if closed else 1)) for i in range(L + 1)])

    # Resolve the per-cross-section scale [sx, sy].
    if np.isscalar(scale) or (np.ndim(scale) == 1 and len(scale) == 2):
        s = [float(scale), float(scale)] if np.isscalar(scale) else [float(scale[0]), float(scale[1])]
        if not scale_by_length:
            scalevals = [[float(v) for v in ((1 - i / (L - 1)) * np.array([1.0, 1.0]) + (i / (L - 1)) * np.array(s))] for i in range(L)]
        else:
            scalevals = [[float(v) for v in ((1 - f) * np.array([1.0, 1.0]) + f * np.array(s))] for f in spathfrac[:L]]
    else:
        scalevals = [[float(x), float(x)] if np.isscalar(x) else [float(x[0]), float(x[1])] for x in scale]
    scale_list = [_scale4([sv[0], sv[1], 1.0]) for sv in scalevals]
    if closed:
        scale_list.append(_scale4([scalevals[0][0], scalevals[0][1], 1.0]))

    nprofiles = L + (1 if closed else 0)

    if method == "incremental":
        t0 = tangents[0]
        r = normal_single - (normal_single @ t0) * t0
        cur = frame_map(y=r, z=t0)
        rotations = []
        for i in range(nprofiles):
            rotations.append(cur)
            if i < nprofiles - 1:
                v1 = patharr[(i + 1) % L] - patharr[i % L]
                c1 = float(v1 @ v1)
                rL = r - 2 * (v1 @ r) / c1 * v1
                tL = tangents[i % L] - 2 * (v1 @ tangents[i % L]) / c1 * v1
                v2 = tangents[(i + 1) % L] - tL
                c2 = float(v2 @ v2)
                r = rL - (2 / c2) * (v2 @ rL) * v2
                cur = frame_map(y=r, z=tangents[(i + 1) % L])
        if closed:
            reference = rotations[0]
        elif last_normal is None:
            reference = rotations[-1]
        else:
            lt = tangents[-1]
            ln = np.asarray(last_normal, dtype=float)
            reference = frame_map(y=ln - (ln @ lt) * lt, z=lt)
        mismatch = rotations[-1][:3, :3].T @ reference[:3, :3]
        correction_twist = math.degrees(math.atan2(mismatch[1][0], mismatch[0][0]))
        twistfix = correction_twist % (360 / symmetry)
        unscaled = [_translate4(patharr[i]) @ rotations[i] @ _zrot4((twistfix - twist) * tpathfrac[i]) for i in range(L)]
        if closed:
            unscaled.append(_translate4(patharr[0]) @ rotations[0]
                            @ _zrot4(-correction_twist + correction_twist % (360 / symmetry) - twist))
    elif method == "manual":
        unscaled = []
        for i in range(nprofiles):
            ni, ti = normals[i % L], tangents[i % L]
            if relaxed:
                ynormal, znormal = ni, ti - (ni @ ti) * ni
            else:
                ynormal, znormal = ni - (ni @ ti) * ti, ti
            unscaled.append(_translate4(patharr[i % L]) @ frame_map(y=ynormal, z=znormal) @ _zrot4(-twist * tpathfrac[i]))
    elif method == "natural":
        pathnormal = np.asarray(Path._path_normals(patharr, tangents, closed), dtype=float)
        unscaled = [
            _translate4(patharr[i % L]) @ frame_map(x=pathnormal[i % L], z=tangents[i % L]) @ _zrot4(-twist * tpathfrac[i])
            for i in range(nprofiles)
        ]
    else:
        raise AssertionError(f"Unknown method {method!r} (use incremental/manual/natural).")

    transform_list = [unscaled[i] @ scale_list[i] for i in range(len(unscaled))]
    if transforms:
        return transform_list
    shp = clockwise_polygon(shape)
    return sweep(shp, transform_list, closed=False, caps=caps, style=style)


# ---------------------------------------------------------------------------------------------
# skin() -- blend a stack of profiles into a surface
# ---------------------------------------------------------------------------------------------


def _reindex_polygon(reference, poly) -> list:
    """Circularly rotate *poly*'s vertices to best line up with *reference* (BOSL2 reindex_polygon).

    Both must be equal-length point lists. Picks the rotation minimizing the summed vertex
    distance. Winding is not adjusted here (the profiles skin() feeds in are already 3-D)."""
    ref = np.asarray(reference, dtype=float)
    p = np.asarray(poly, dtype=float)
    n = len(ref)
    best_k, best_val = 0, None
    for k in range(n):
        val = float(np.sum(np.linalg.norm(ref - np.roll(p, -k, axis=0), axis=1)))
        if best_val is None or val < best_val:
            best_val, best_k = val, k
    return np.roll(p, -best_k, axis=0).tolist()


def slice_profiles(profiles, slices, closed: bool = False) -> list:
    """Interpolate *slices* extra profiles between each consecutive pair (BOSL2 slice_profiles()).

    *slices* is a count (or a per-segment list). The profiles must all be equal-length point
    lists; the interpolation is vertex-by-vertex."""
    n = len(profiles)
    nseg = n - (0 if closed else 1)
    count = list(slices) if isinstance(slices, (list, tuple, np.ndarray)) else [slices] * nseg
    out = []
    for i in range(nseg):
        a = np.asarray(profiles[i], dtype=float)
        b = np.asarray(profiles[(i + 1) % n], dtype=float)
        steps = int(count[i]) + 1
        for k in range(steps):  # lerpn(..., endpoint=False)
            out.append((a + (b - a) * (k / steps)).tolist())
    if not closed:
        out.append([list(p) for p in profiles[-1]])
    return out


def skin(profiles, slices, refine=1, method: str = "direct", sampling=None, caps=None,
         closed: bool = False, style: str = "min_edge", z=None) -> VNF:
    """Blend a stack of 2-D/3-D profiles into a skinned surface, returning a VNF (BOSL2 skin()).

    Consecutive profiles are connected vertex-to-vertex; *slices* extra interpolated profiles are
    inserted between each pair to smooth the transition. Profiles of differing point counts are
    resampled up to the largest (via :meth:`Path._subdivide_path`).

    Args:
        profiles: list of >= 2 closed profiles (each a list of points). If 2-D, give matching *z*.
        slices:   number of interpolated profiles inserted between each pair (int or per-gap list)
        refine:   subdivide every profile by this factor before skinning (default 1)
        method:   "direct" (connect vertex i to vertex i) or "reindex" (rotate each profile to
                  best-align with the previous). The "distance"/"tangent" vertex-matching methods
                  are not ported.
        sampling: "length" or "segment" resampling (default "length")
        caps:     cap the ends (default: True for open, False for closed); bool or [bool, bool]
        closed:   the stack loops back to the first profile (default False)
        style:    vnf_vertex_array quad-subdivision style
        z:        per-profile Z heights, required when the profiles are 2-D

    Examples:
        Skinning a round profile up to a square one (a lofted transition):

        .. pythonscad-example::

            circle = [[6 * math.cos(t), 6 * math.sin(t)] for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
            square = [[-8, -8], [8, -8], [8, 8], [-8, 8]]
            skin([circle, square], slices=20, method="reindex", z=[0, 25]).polyhedron().show()
    """
    profiles = [list(p) for p in profiles]
    n = len(profiles)
    assert n > 1, "skin() needs at least two profiles."
    profcount = n - (0 if closed else 1)
    if caps is None:
        caps = False if closed else True
    fullcaps = [False, False] if closed else ([caps, caps] if isinstance(caps, bool) else [bool(caps[0]), bool(caps[1])])
    refine = list(refine) if isinstance(refine, (list, tuple)) else [refine] * n
    method = list(method) if isinstance(method, (list, tuple)) else [method] * profcount
    for m in method:
        assert m in ("direct", "reindex"), f"skin(): only the 'direct' and 'reindex' methods are ported (got {m!r})."
    sampling = sampling if sampling is not None else "length"

    dim = len(profiles[0][0])
    if dim == 2:
        assert z is not None and len(z) == n, "skin(): 2-D profiles need a matching-length z list."
        profiles = [[[float(pt[0]), float(pt[1]), float(z[i])] for pt in profiles[i]] for i in range(n)]

    from bosl2.paths import Path  # local: keep the import graph acyclic

    maxlen = max(refine[i] * len(profiles[i]) for i in range(n))
    resampled = [Path._subdivide_path(profiles[i], n=maxlen, closed=True, method=sampling) for i in range(n)]
    fixedprof = [resampled[0]]
    for i in range(1, n):
        if method[i - 1] == "direct":
            fixedprof.append(resampled[i])
        else:
            fixedprof.append(_reindex_polygon(fixedprof[i - 1], resampled[i]))
    sliced = slice_profiles(fixedprof, slices, closed)
    grid = sliced if not closed else sliced + [sliced[0]]
    vnf = VNF.vertex_array(grid, cap1=fullcaps[0], cap2=fullcaps[1], col_wrap=True, style=style)
    return vnf if vnf.volume() >= 0 else vnf.reverse()


# ---------------------------------------------------------------------------------------------
# linear_sweep() / rotate_sweep() / spiral_sweep()
# ---------------------------------------------------------------------------------------------


def linear_sweep(region, height=None, twist: float = 0.0, scale=1, shift=(0.0, 0.0),
                 slices=None, caps=True, style: str = "default", center: bool | None = None,
                 h=None) -> VNF:
    """Extrude a 2-D outline to *height* with optional twist / scale / shift (BOSL2 linear_sweep()).

    A single closed outline (a Path or point list) is supported -- for a region with holes use a
    native ``linear_extrude`` instead. The bottom sits on Z=0 unless *center* is True.

    Args:
        region: the 2-D outline to extrude (a closed path)
        height: extrusion height (aliases: *h*; default 1)
        twist:  total twist over the height, in degrees (default 0)
        scale:  scale of the top relative to the bottom (scalar or [x, y]; default 1)
        shift:  [x, y] offset of the top relative to the bottom (default [0, 0])
        slices: number of intermediate layers (default: enough for ~5 deg of twist each)
        caps:   cap the ends (default True); bool or [bool, bool]
        center: center the extrusion on Z (default False -> base on Z=0)
        style:  vnf_vertex_array quad-subdivision style

    Examples:
        A twisting, tapering square column:

        .. pythonscad-example::

            square = [[-10, -10], [10, -10], [10, 10], [-10, 10]]
            linear_sweep(square, height=40, twist=120, scale=0.4).polyhedron().show()
    """
    hh = float(h if h is not None else (height if height is not None else 1))
    path = [[float(p[0]), float(p[1])] for p in region]
    if slices is None:
        slices = max(1, math.ceil(abs(twist) / 5))
    sc = [float(scale), float(scale)] if isinstance(scale, (int, float)) else [float(scale[0]), float(scale[1])]
    sh = [float(shift[0]), float(shift[1])]
    fullcaps = [caps, caps] if isinstance(caps, bool) else [bool(caps[0]), bool(caps[1])]
    z0 = -hh / 2 if center else 0.0
    base = np.asarray(path3d(path), dtype=float)
    verts = []
    for i in range(slices + 1):
        u = i / slices
        m = (_translate4([sh[0] * u, sh[1] * u, z0 + hh * u])
             @ _scale4([1 + (sc[0] - 1) * u, 1 + (sc[1] - 1) * u, 1])
             @ _zrot4(-twist * u))
        verts.append(np.asarray(_apply(m, base), dtype=float))
    vnf = VNF.vertex_array(verts, cap1=fullcaps[0], cap2=fullcaps[1], col_wrap=True, style=style)
    return vnf if vnf.volume() >= 0 else vnf.reverse()


def rotate_sweep(shape, angle: float = 360.0, caps=None, closed: bool | None = None,
                 style: str = "min_edge", start: float = 0.0) -> VNF:
    """Revolve a 2-D *shape* (in the X+ half-plane, x=radius, y=height) around the Z axis (BOSL2 rotate_sweep()).

    A closed *shape* profile makes a solid of revolution; an open path with *caps* is first closed
    to the axis. A full 360-degree revolution loops seamlessly; a partial angle end-caps the sweep.

    Args:
        shape:  the 2-D profile to revolve (x >= 0)
        angle:  revolution angle in degrees, 0 < angle <= 360 (default 360)
        caps:   end-cap a partial revolution / close an open profile to the axis (default: angle < 360)
        closed: legacy inverse of *caps* (give one or the other)
        style:  vnf_vertex_array quad-subdivision style
        start:  starting angle in degrees (default 0)

    Examples:
        Revolving a rounded profile into a spool:

        .. pythonscad-example::

            profile = [[4, -10], [12, -10], [12, -6], [7, -2], [7, 2], [12, 6], [12, 10], [4, 10]]
            rotate_sweep(profile, 360).polyhedron().show()
    """
    assert 0 < angle <= 360, "rotate_sweep(): angle must be in (0, 360]."
    if caps is None:
        caps = (not closed) if closed is not None else (angle < 360)
    prof = [[float(p[0]), float(p[1])] for p in shape]
    full = angle >= 360
    if caps and not full:
        prof = [[0.0, prof[0][1]]] + prof + [[0.0, prof[-1][1]]]
    xmax = max(p[0] for p in prof)
    steps = int(math.ceil(_segs(xmax) * angle / 360)) + (0 if full else 1)
    steps = max(steps, 3)
    if full:
        angs = [start + 360.0 * i / steps for i in range(steps)]
    else:
        angs = [start + angle * i / (steps - 1) for i in range(steps)]
    transforms = [_zrot4(a) @ _xrot4(90) for a in angs]
    vnf = sweep(prof, transforms, closed=full, caps=(not full and bool(caps)), style=style)
    return vnf if vnf.volume() >= 0 else vnf.reverse()


def spiral_sweep(poly, h, r=None, turns: float = 1.0, r1=None, r2=None, d=None, d1=None, d2=None,
                 center: bool = True, style: str = "min_edge") -> VNF:
    """Sweep a 2-D cross-section *poly* along a helix (BOSL2 spiral_sweep(), without lead-in tapers).

    *poly*'s X is the radial offset from the helix radius and its Y is the vertical offset, so a
    small wire cross-section becomes a spring/thread. The lead-in taper options are not ported.

    Args:
        poly:  the 2-D wire cross-section (closed path)
        h:     total height of the spiral
        r/d:   helix radius/diameter (or per-end r1/r2 / d1/d2 for a conical spiral)
        turns: number of turns (default 1)
        center: center the spiral on Z (default True)
        style: vnf_vertex_array quad-subdivision style

    Examples:
        A rectangular-section coil spring:

        .. pythonscad-example::

            section = [[-1.2, -1.2], [1.2, -1.2], [1.2, 1.2], [-1.2, 1.2]]
            spiral_sweep(section, h=40, r=12, turns=5).polyhedron().show()
    """
    assert h > 0 and turns != 0, "spiral_sweep(): need positive height and nonzero turns."
    rr1 = r1 if r1 is not None else (r if r is not None else (d1 / 2 if d1 is not None else (d / 2 if d is not None else 1)))
    rr2 = r2 if r2 is not None else (r if r is not None else (d2 / 2 if d2 is not None else (d / 2 if d is not None else 1)))
    poly = [[float(p[0]), float(p[1])] for p in poly]
    nturns = abs(turns)
    sides = _segs(max(rr1, rr2))
    ang_step = 360.0 / sides
    total = 360.0 * nturns
    steps = int(math.ceil(total / ang_step))
    angs = [total * i / steps for i in range(steps + 1)]
    z0 = -h / 2 if center else 0.0
    transforms = []
    for a in angs:
        frac = a / total
        rad = rr1 + (rr2 - rr1) * frac
        z = z0 + h * frac
        transforms.append(_translate4([0, 0, z]) @ _zrot4(a * math.copysign(1, turns))
                          @ _translate4([rad, 0, 0]) @ _xrot4(90))
    vnf = sweep(poly, transforms, closed=False, caps=True, style=style)
    return vnf if vnf.volume() >= 0 else vnf.reverse()


def subdivide_and_slice(profiles, slices, numpoints=None, method: str = "length", closed: bool = False) -> list:
    """Resample every profile up to *numpoints* then interpolate *slices* between them (BOSL2 subdivide_and_slice()).

    *numpoints* defaults to the largest profile's length; "lcm" uses the least common multiple of
    the profile lengths. Returns the stacked list of (equal-length) profiles."""
    from bosl2.paths import Path

    maxsize = max(len(p) for p in profiles)
    if numpoints is None:
        numpoints = maxsize
    elif numpoints == "lcm":
        from functools import reduce
        numpoints = reduce(lambda a, b: a * b // math.gcd(a, b), [len(p) for p in profiles])
    numpoints = int(round(numpoints))
    assert numpoints >= maxsize, "subdivide_and_slice(): numpoints is smaller than the largest profile."
    fixed = [Path._subdivide_path(p, n=numpoints, closed=True, method=method) for p in profiles]
    return slice_profiles(fixed, slices, closed)


# ---------------------------------------------------------------------------------------------
# path_sweep2d() -- sweep a 2-D shape along a 2-D path (creases allowed)
# ---------------------------------------------------------------------------------------------


def path_sweep2d(shape, path, closed: bool = False, caps=None, quality: int = 1,
                 style: str = "min_edge") -> VNF:
    """Sweep a 2-D *shape* along a 2-D *path*, mapping the shape's Y to Z (BOSL2 path_sweep2d()).

    Both *shape* and *path* are 2-D :class:`~bosl2.paths.Path` objects (coerced from point lists).
    Each shape point offsets the path by its X and lifts it to its Y, so a shape with a wide X
    range becomes a wall of varying width along the path. Unlike :func:`path_sweep`, moderate local
    concavity is handled by the offset (mitre joins); an offset large enough to collapse a feature
    of the path will still fold, so keep the shape's X extent below the path's tightest radius.

    Args:
        shape:  the 2-D cross-section (a closed path); its X is the offset from the path, its Y the height
        path:   the 2-D path to sweep along
        closed: the path is a closed loop (default False)
        caps:   cap the open ends (default: True for open, False for closed)
        quality: accepted for signature parity (unused -- the mitre offset needs no quality knob)
        style:  vnf_vertex_array quad-subdivision style

    Examples:
        A rounded bar swept along a wavy 2-D path:

        .. pythonscad-example::

            shape = [[-2, -2], [2, -2], [2, 2], [-2, 2]]
            path = [[t, 8 * math.sin(t / 12)] for t in range(0, 90, 3)]
            path_sweep2d(shape, path).polyhedron().show()
    """
    from bosl2.paths import Path

    shape = Path(shape)
    path = Path(path)
    if caps is None:
        caps = False if closed else True
    fullcaps = [False, False] if closed else ([caps, caps] if isinstance(caps, bool) else [bool(caps[0]), bool(caps[1])])
    profile = shape if not shape.is_clockwise() else shape.reversed_path()  # ccw_polygon
    flip = -1.0 if (closed and path.is_clockwise()) else 1.0
    pth = path if flip > 0 else path.reversed_path()

    # For each profile point, offset the path by -flip*x and lift the result to z=y.
    per_point = []
    for pt in profile:
        off = pth.offset(delta=-flip * pt[0])
        assert len(off) == len(pth), (
            "path_sweep2d(): the offset dropped points (the shape is too wide for the path here); "
            "reduce the shape's X extent."
        )
        per_point.append([[float(p[0]), float(p[1]), float(pt[1])] for p in off])
    # transpose: one grid row per path position, each a full cross-section
    grid = [[per_point[j][i] for j in range(len(profile))] for i in range(len(pth))]
    if closed:
        grid = grid + [grid[0]]
    vnf = VNF.vertex_array(grid, cap1=fullcaps[0], cap2=fullcaps[1], col_wrap=True, style=style)
    return vnf if vnf.volume() >= 0 else vnf.reverse()


# ---------------------------------------------------------------------------------------------
# rot_resample() -- resample a list of transforms to uniform screw-motion spacing
# ---------------------------------------------------------------------------------------------


def _closest_angle(alpha: float, beta):
    """Congruent angle to *beta* nearest *alpha* (within +/-180 degrees); *beta* may be a list."""
    if isinstance(beta, (list, tuple, np.ndarray)):
        return [_closest_angle(alpha, b) for b in beta]
    if beta - alpha > 180:
        return beta - math.ceil((beta - alpha - 180) / 360) * 360
    if beta - alpha < -180:
        return beta + math.ceil((alpha - beta - 180) / 360) * 360
    return beta


def _smooth(data, length: int, closed: bool = False, angle: bool = False) -> list:
    """Moving-average smooth of *data* over a window of *length* (BOSL2 _smooth()).

    With *angle*, values are unwrapped to the nearest congruent angle before averaging so the mean
    does not jump across the +/-180 boundary. Ends are padded with the edge value (open case)."""
    halfwidth = length // 2
    n = len(data)
    out = []
    if closed:
        for i in range(n):
            window = [data[(i + k) % n] for k in range(-halfwidth, halfwidth + 1)]
            if angle:
                window = _closest_angle(data[i], window)
            out.append(sum(window) / len(window))
    else:
        for i in range(n):
            lo, hi = max(i - halfwidth, 0), min(i + halfwidth, n - 1)
            window = list(data[lo:hi + 1])
            pad = data[0] if (i - halfwidth) < 0 else data[-1]
            out.append((sum(window) + pad * (length - len(window))) / length)
    return out


def rot_resample(rotlist, n, twist=None, scale=None, smoothlen: int = 1, long=False,
                 turns=0, closed: bool = False, method: str = "length") -> list:
    """Resample a list of 4x4 transforms to uniform screw-motion spacing (BOSL2 rot_resample()).

    Interpolates between successive transforms along their screw motion (via :func:`rot_decode`),
    optionally adding *twist* and *scale* (smoothed over *smoothlen*). Handy for regularizing the
    transform list from ``path_sweep(..., transforms=True)`` before handing it to :func:`sweep`.

    Args:
        rotlist: list of 4x4 transform matrices
        n:       number of output samples (method="length") or samples per gap (method="count")
        twist:   extra twist in degrees (scalar or per-gap list)
        scale:   extra scale (scalar or per-gap list, multiplied cumulatively)
        smoothlen: odd window length for smoothing the twist/scale (default 1 = none)
        long:    take the >180-degree rotation at a gap (scalar or per-gap list)
        turns:   extra full turns to add at a gap (scalar or per-gap list)
        closed:  the transform list forms a loop (default False)
        method:  "length" (uniform screw-distance) or "count" (fixed samples per gap)
    """
    rotlist = [np.asarray(t, dtype=float) for t in rotlist]
    assert smoothlen > 0 and smoothlen % 2 == 1, "rot_resample(): smoothlen must be a positive odd integer."
    assert method in ("length", "count")
    m = len(rotlist)
    tcount = m + (0 if closed else -1)
    if method == "length":
        count = (n + 1) if closed else n
    else:
        count = (sum(n) if isinstance(n, (list, tuple)) else tcount * n) + 1
    long_l = list(long) if isinstance(long, (list, tuple)) else [long] * tcount
    turns_l = list(turns) if isinstance(turns, (list, tuple)) else [turns] * tcount

    steps = [rot_inverse(rotlist[i]) @ rotlist[(i + 1) % m] for i in range(tcount)]
    parms = []
    for i in range(tcount):
        tp = rot_decode(steps[i], long_l[i])
        parms.append([tp[0] + turns_l[i] * 360, np.asarray(tp[1], dtype=float),
                      np.asarray(tp[2], dtype=float), np.asarray(tp[3], dtype=float)])
    radius = [float(np.linalg.norm(p[2])) for p in parms]
    length = [float(math.hypot(float(np.linalg.norm(parms[i][3])), parms[i][0] / 360 * 2 * math.pi * radius[i]))
              for i in range(tcount)]
    if method == "length":
        assert all(x > 0 for x in length), "rot_resample(): a repeated/origin rotation makes method='length' undefined."

    cumlen = [0.0]
    for x in length:
        cumlen.append(cumlen[-1] + x)
    totlen = cumlen[-1]
    stepsize = totlen / (count - 1) if count > 1 else totlen

    if method == "count":
        nlist = list(n) if isinstance(n, (list, tuple)) else [n] * tcount
        samples = [[k / N for k in range(N)] for N in nlist]  # lerpn(0,1,N,endpoint=False)
    else:
        samples = []
        for i in range(tcount):
            remainder = cumlen[i] % stepsize
            offset = 0.0 if remainder == 0 else stepsize - remainder
            num = math.ceil((length[i] - offset) / stepsize)
            samples.append([(offset + k * stepsize) / length[i] for k in range(num)])

    twist_v = 0 if twist is None else twist
    scale_v = 1 if scale is None else scale
    lastsample = samples[-1][-1] if samples[-1] else 1.0
    needlast = abs(lastsample - 1.0) > 1e-9

    if isinstance(twist_v, (int, float)):
        sampletwist = list(np.linspace(0, twist_v, count))
    else:
        cumtwist = [0.0]
        for t in twist_v:
            cumtwist.append(cumtwist[-1] + t)
        sampletwist = [cumtwist[i] + (cumtwist[i + 1] - cumtwist[i]) * u for i in range(tcount) for u in samples[i]]
        if needlast:
            sampletwist.append(cumtwist[-1])

    if isinstance(scale_v, (int, float)):
        samplescale = [1 + (scale_v - 1) * u for u in np.linspace(0, 1, count)]
    else:
        cumscale = [1.0]
        for s in scale_v:
            cumscale.append(cumscale[-1] * s)
        samplescale = [cumscale[i] + (cumscale[i + 1] - cumscale[i]) * u for i in range(tcount) for u in samples[i]]
        if needlast:
            samplescale.append(cumscale[-1])

    smoothtwist = _smooth(sampletwist[:-1] if closed else sampletwist, smoothlen, closed=closed, angle=True)
    smoothscale = _smooth(samplescale, smoothlen, closed=closed)

    interpolated = []
    for i in range(tcount):
        for u in samples[i]:
            mv = np.eye(4)
            mv[:3, 3] = u * parms[i][3]
            interpolated.append(rotlist[i] @ mv @ rot_about_axis(u * parms[i][0], parms[i][1], parms[i][2]))
    if needlast:
        interpolated.append(rotlist[-1])

    end = len(interpolated) - (1 if closed else 0)
    return [interpolated[i] @ _zrot4(smoothtwist[i]) @ _scale4([smoothscale[i], smoothscale[i], 1.0])
            for i in range(end)]
