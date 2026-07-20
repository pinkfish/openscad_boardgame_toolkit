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

# LibFile: bosl2/partitions.py
#    Pure-Python port of BOSL2's partitions.scad: cut an object with a plane (half_of and the six
#    axis half-cuts), and partition a large object into two interlocking pieces for printing
#    (partition_path / partition_mask / partition_cut_mask / the partition() split).
#
#    The cut operators live on :class:`~bosl2.shapes3d.Bosl2Solid` via the :class:`Partitionable`
#    mixin: a half-cut intersects the solid with a half-space mask, auto-sized from the object's
#    native bounding box (so the BOSL2 ``s=`` mask-size argument is optional here). partition()
#    returns the two interlocking pieces. The 2-D cut-path generators (:func:`partition_path` and
#    friends) return :class:`~bosl2.paths.Path` objects; the mask builders return Bosl2Solids.
#
#    Only matrix/path math and bosl2.transforms/constants are imported at load time; native
#    primitives, shapes2d.arc, and Bosl2Solid are imported lazily inside the functions that need
#    them, so shapes3d.py can pull in the mixin during its own import without a cycle.
#
# FileSummary: Planar half-cuts and interlocking partitions (jigsaw/dovetail/... joints).
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

from bosl2.transforms import axis_angle_matrix, rot_from_to, rot_about_axis
from bosl2.constants import UP, DOWN, LEFT, RIGHT, FRONT, BACK
from bosl2.vectors import unit
from bosl2.geometry import pointlist_bounds

__all__ = [
    "partition_path", "partition_mask", "partition_cut_mask", "Partitionable",
]


# ---------------------------------------------------------------------------
# Section: 2-D path helpers
# ---------------------------------------------------------------------------


def _is_num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _yscale(s, path):
    return [[float(p[0]), float(p[1]) * s] for p in path]


def _scale2(sx, sy, path):
    return [[float(p[0]) * sx, float(p[1]) * sy] for p in path]


def _left(x, path):
    return [[float(p[0]) - x, float(p[1])] for p in path]


def _right(x, path):
    return [[float(p[0]) + x, float(p[1])] for p in path]


def _xflip(x, path):
    return [[2 * x - float(p[0]), float(p[1])] for p in path]


def _skew(axy_deg, path):
    t = math.tan(math.radians(axy_deg))
    return [[float(p[0]) + float(p[1]) * t, float(p[1])] for p in path]


def _lerp(a, b, u):
    return a + (b - a) * u


def _dedup(path):
    from bosl2.paths import Path
    return [list(p) for p in Path._deduplicate(path, closed=False)]


def _merge_collinear(path):
    # BOSL2's path_merge_collinear() drops exact-duplicate points before merging collinear runs;
    # the toolkit kernel does not, so dedup first (a bare duplicate otherwise collapses a corner).
    from bosl2.paths import Path
    return [list(p) for p in Path._path_merge_collinear(_dedup(path), closed=False)]


# ---------------------------------------------------------------------------
# Section: named cut sub-paths
# ---------------------------------------------------------------------------


def _partition_subpath(cptype, _fn=None, _fa=None, _fs=None):
    """The simple named cut sub-paths used by the mask builders (BOSL2 _partition_subpath())."""
    from bosl2.shapes2d import arc

    if cptype == "flat":
        return [[0, 0], [1, 0]]
    if cptype == "sawtooth":
        return [[0, 0], [0.5, 1], [1, 0]]
    if cptype == "sinewave":
        return [[a / 360, math.sin(math.radians(a)) / 2] for a in range(0, 361, 5)]
    if cptype == "comb":
        dx = 0.5 * math.sin(math.radians(2))
        return [[0, 0], [dx, 0.5], [0.5 - dx, 0.5], [0.5 + dx, -0.5], [1 - dx, -0.5], [1, 0]]
    if cptype == "finger":
        dx = 0.5 * math.sin(math.radians(20))
        return [[0, 0], [dx, 0.5], [0.5 - dx, 0.5], [0.5 + dx, -0.5], [1 - dx, -0.5], [1, 0]]
    if cptype == "dovetail":
        return [[0, -0.5], [0.3, -0.5], [0.2, 0.5], [0.8, 0.5], [0.7, -0.5], [1, -0.5]]
    if cptype == "hammerhead":
        return [[0, -0.5], [0.35, -0.5], [0.35, 0], [0.15, 0], [0.15, 0.5],
                [0.85, 0.5], [0.85, 0], [0.65, 0], [0.65, -0.5], [1, -0.5]]
    if cptype == "jigsaw":
        return (list(arc(r=5 / 16, cp=[0, -3 / 16], start=270, angle=125, _fn=_fn, _fa=_fa, _fs=_fs))
                + list(arc(r=5 / 16, cp=[1 / 2, 3 / 16], start=215, angle=-250, _fn=_fn, _fa=_fa, _fs=_fs))
                + list(arc(r=5 / 16, cp=[1, -3 / 16], start=145, angle=125, _fn=_fn, _fa=_fa, _fs=_fs)))
    raise AssertionError(f"Unsupported cutpath type: {cptype!r}")


def _partition_cutpath(l, h, cutsize, cutpath, gap, cutpath_centered, _fn=None, _fa=None, _fs=None):
    """One row of the named cut sub-path, repeated to span *l* (BOSL2 _partition_cutpath())."""
    cs = list(cutsize) if isinstance(cutsize, (list, tuple, np.ndarray)) else [cutsize * 2, cutsize]
    sub = [list(p) for p in cutpath] if isinstance(cutpath, (list, tuple, np.ndarray)) else \
        _partition_subpath(cutpath, _fn, _fa, _fs)
    reps_raw = 1 + math.floor((l - cs[0]) / (cs[0] + gap))
    reps = reps_raw - 1 if (reps_raw % 2 == 0 and cutpath_centered) else reps_raw
    reps = max(1, reps)
    cplen = reps * cs[0] + max(0, reps - 1) * gap
    pts = [[-l / 2, sub[0][1] * cs[1]]]
    for i in range(reps):
        for pt in sub:
            pts.append([pt[0] * cs[0] + i * (cs[0] + gap) - cplen / 2, pt[1] * cs[1]])
    pts.append([cplen / 2, sub[-1][1] * cs[1]])
    return _dedup(pts)


# ---------------------------------------------------------------------------
# Section: partition_path segment engine
# ---------------------------------------------------------------------------


def _ptn_sect(cptype, length: float = 25, width: float = 25, invert=False, _fn=None, _fa=None, _fs=None):
    """One section of a partition_path, with the full BOSL2 modifier grammar (BOSL2 _ptn_sect())."""
    from bosl2.shapes2d import arc, _frag_count

    if _is_num(cptype):
        assert cptype > 0, "flat section length must be positive."
        return [[0, 0], [float(cptype), 0]]
    if invert:
        return _yscale(-1, _ptn_sect(cptype, length, width, _fn=_fn, _fa=_fa, _fs=_fs))

    if isinstance(cptype, str) and " " in cptype:
        pos = cptype.rfind(" ")
        opt = cptype[pos + 1:]
        base = cptype[:pos]
        if opt == "yflip":
            return _yscale(-1, _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs))
        if opt == "xflip":
            sect = _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs)
            b = pointlist_bounds(sect)
            xpos = (b[1][0] + b[0][0]) / 2
            return _xflip(xpos, sect)[::-1]
        if opt in ("addflip", "wave"):
            sect1 = _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs)
            sect2 = _ptn_sect(base + " yflip xflip", length, width, _fn=_fn, _fa=_fa, _fs=_fs)
            b1, b2 = pointlist_bounds(sect1), pointlist_bounds(sect2)
            osect1 = _scale2(0.5, 0.5, _left(b1[0][0], sect1))
            osect2 = _right(osect1[-1][0], _scale2(0.5, 0.5, _left(b2[0][0], sect2)))
            return _merge_collinear(osect1 + osect2)
        if opt and opt[0].isdigit() and opt.endswith("x") and opt[:-1].isdigit():  # "3x": repeat
            reps = int(opt[:-1])
            assert reps > 0, "repetition count must be positive."
            sect = _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs)
            w = sect[-1][0]
            out = []
            for i in range(reps):
                out += _right(i * w, sect)
            return _merge_collinear(out)
        if opt and opt[0].isdigit() and "x" in opt:  # "30x20": resize
            parts = opt.split("x")
            assert len(parts) == 2, "size modifier must be LENGTHxWIDTH, e.g. '30x25'."
            return _ptn_sect(base, float(parts[0]), float(parts[1]), _fn=_fn, _fa=_fa, _fs=_fs)
        if opt.startswith("skew:"):
            angle = float(opt[5:])
            assert -45 <= angle <= 45, "skew angle must be between -45 and 45."
            return _skew(angle, _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs))
        if opt.startswith("pinch:"):
            val_str = opt[6:]
            is_deg = val_str.endswith("deg")
            is_pct = val_str.endswith("%")
            num_str = val_str[:-3] if is_deg else val_str[:-1] if is_pct else val_str
            val = float(num_str)
            raw = _ptn_sect(base, length, width, _fn=_fn, _fa=_fa, _fs=_fs)
            xs = [p[0] for p in raw]
            minx, maxx = min(xs), max(xs)
            w_half, midx = (maxx - minx) / 2, (minx + maxx) / 2
            maxy = max(abs(p[1]) for p in raw)
            dx = maxy * math.tan(math.radians(val)) / w_half if (is_deg and maxy and w_half) else 0
            pcnt = (1 - dx) * 100 if is_deg else val
            if maxy == 0:
                return raw
            return [[(p[0] - midx) * _lerp(1, pcnt / 100, abs(p[1]) / maxy) + midx, p[1]] for p in raw]
        if base == "flat" and opt and opt[0].isdigit() and "x" not in opt and ":" not in opt:
            return [[0, 0], [float(opt), 0]]
        raise AssertionError(f"Bad section option: {opt!r}")

    if cptype == "sinewave":
        return _ptn_sect("halfsine addflip", length, width, _fn=_fn, _fa=_fa, _fs=_fs)
    steps = _frag_count(length / 2, _fn, _fa, _fs)
    if cptype == "flat":
        path = [[0, 0], [1, 0]]
    elif cptype == "sawtooth":
        path = [[0, 0], [0, 1], [1, 0]]
    elif cptype == "square":
        path = [[0, 0], [0, 1], [1, 1], [1, 0]]
    elif cptype == "triangle":
        path = [[0, 0], [0.5, 1], [1, 0]]
    elif cptype == "halfsine":
        path = [[a / 180, math.sin(math.radians(a))] for a in np.arange(0, 180.0001, 360 / steps)]
    elif cptype == "semicircle":
        path = _yscale(2, list(arc(n=math.ceil(steps / 2), r=1 / 2, cp=[1 / 2, 0], start=180, angle=-180)))
    elif cptype == "comb":
        dx = math.tan(math.radians(2)) * width / length
        assert dx <= 0.5, "width-to-length ratio too large for comb form."
        path = [[0, 0], [dx, 1], [1 - dx, 1], [1, 0]]
    elif cptype == "finger":
        dx = math.tan(math.radians(20)) * width / length
        assert dx <= 0.5, "width-to-length ratio too large for finger form."
        path = [[0, 0], [dx, 1], [1 - dx, 1], [1, 0]]
    elif cptype == "dovetail":
        dx = math.tan(math.radians(9)) * width / length / 2
        assert dx < 0.25, "width-to-length ratio too large for dovetail form."
        path = [[0, 0], [0.25 + dx, 0], [0.25 - dx, 1], [0.75 + dx, 1], [0.75 - dx, 0], [1, 0]]
    elif cptype == "hammerhead":
        path = [[0, 0], [0.35, 0], [0.35, 0.5], [0.15, 0.5], [0.15, 1],
                [0.85, 1], [0.85, 0.5], [0.65, 0.5], [0.65, 0], [1, 0]]
    elif cptype == "jigsaw":
        path = (list(arc(n=math.ceil(steps / 4), r=5 / 16, cp=[0, 5 / 16], start=270, angle=125, _fn=_fn, _fa=_fa, _fs=_fs))
                + list(arc(n=math.ceil(steps / 2), r=5 / 16, cp=[1 / 2, 11 / 16], start=215, angle=-250, _fn=_fn, _fa=_fa, _fs=_fs))
                + list(arc(n=math.ceil(steps / 4), r=5 / 16, cp=[1, 5 / 16], start=145, angle=125, _fn=_fn, _fa=_fa, _fs=_fs)))
    elif isinstance(cptype, (list, tuple, np.ndarray)):
        path = [list(p) for p in cptype]
    else:
        raise AssertionError(f"Unsupported partition section type: {cptype!r}")
    return _scale2(length, width, path)


def partition_path(pathdesc, repeat: int = 1, y=None, altpath=None, seglen: float = 25,
                   segwidth: float = 25, _fn=None, _fa=None, _fs=None):
    """Build a 2-D interlocking cut path from a list of segment descriptors (BOSL2 partition_path()).

    Each item of *pathdesc* is a numeric length (a flat section), a 2-D path (used as-is), or a
    named section pattern -- ``"flat"``, ``"sawtooth"``, ``"square"``, ``"triangle"``, ``"halfsine"``,
    ``"semicircle"``, ``"sinewave"``, ``"comb"``, ``"finger"``, ``"dovetail"``, ``"hammerhead"``,
    ``"jigsaw"`` -- optionally suffixed with space-separated modifiers (``"3x"`` repeat, ``"30x20"``
    resize, ``"xflip"``/``"yflip"``/``"addflip"``/``"wave"``, ``"skew:15"``, ``"pinch:33"`` /
    ``"pinch:20deg"``). Modifiers apply left to right.

    Args:
        pathdesc: list of segment descriptors
        repeat:   repeat the whole *pathdesc* this many times (default 1)
        y:        if given, close the path at this Y (for a polygon); its sign orients the result
        altpath:  optional base path the pattern is redirected along
        seglen:   default length for named sections (default 25)
        segwidth: default width for named sections (default 25)

    Returns:
        A :class:`~bosl2.paths.Path` (closed when *y* is given).

    Examples:
        A wall profile mixing jigsaw and hammerhead joints, stroked into a divider:

        .. pythonscad-example::

            wall = partition_path([40, "jigsaw", 10, "jigsaw yflip", 40], _fn=24)
            wall.stroke(width=3).linear_extrude(height=30).show()
    """
    from bosl2.paths import Path

    paths = []
    for _n in range(repeat):
        for pd in pathdesc:
            if isinstance(pd, (list, tuple, np.ndarray)):
                paths.append([[float(a), float(b)] for a, b in pd])
            elif _is_num(pd):
                paths.append(_ptn_sect(pd, _fn=_fn, _fa=_fa, _fs=_fs))
            elif isinstance(pd, str):
                paths.append(_ptn_sect(pd, seglen, segwidth, _fn=_fn, _fa=_fa, _fs=_fs))
            else:
                raise AssertionError(f"Path descriptor {pd!r} is invalid.")
    min_xs = [min(p[0] for p in path) for path in paths]
    max_xs = [max(p[0] for p in path) for path in paths]
    min_y = min(p[1] for path in paths for p in path)
    max_y = max(p[1] for path in paths for p in path)
    widths = [max_xs[i] - min_xs[i] for i in range(len(paths))]
    allpos = list(np.cumsum([0.0] + widths))
    totlen = allpos[-1]
    fullpath = []
    for i, path in enumerate(paths):
        fullpath += _left(totlen / 2 - allpos[i], path)
    cleanpath = _merge_collinear(_dedup(fullpath))
    redirpath = cleanpath if altpath is None else _ptn_path_redirect(altpath, cleanpath)
    if y is None:
        return Path(redirpath, closed=False)
    assert y < min_y or y > max_y, "partition_path(): closing y would make the path self-crossing."
    closedpath = [[redirpath[-1][0], y], [redirpath[0][0], y]] + redirpath
    outpath = closedpath if y < 0 else closedpath[::-1]
    return Path(outpath, closed=True)


def _ptn_path_redirect(major_path, minor_path, center=True):
    """Re-lay *minor_path* (a partition pattern) along *major_path* (BOSL2 _ptn_path_redirect())."""
    from bosl2.paths import Path

    major2 = _merge_collinear(major_path)
    minor2 = [list(p) for p in Path._resample_path(minor_path, spacing=1, closed=False)]
    major_len = Path._path_length(major2, closed=False)
    minor_len = abs(minor_path[-1][0] - minor_path[0][0])
    extend_by = max(0, -(major_len - minor_len))
    e1 = extend_by * (0.5 if center else 0)
    e2 = extend_by * (0.5 if center else 1)
    vec1 = unit(np.asarray(major2[0]) - np.asarray(major_path[1]), [-1.0, 0.0])
    vec2 = unit(np.asarray(major2[-1]) - np.asarray(major_path[-2]), [1.0, 0.0])
    major3 = [list(np.asarray(major2[0]) + vec1 * e1)] + [list(p) for p in major2[1:-1]] \
        + [list(np.asarray(major2[-1]) + vec2 * e2)]
    major_len2 = Path._path_length(major3, closed=False)
    xoff = (major_len2 - minor_len) / 2 if center else 0
    minor3 = _left(minor2[0][0] - xoff, minor2)
    out = []
    for pt in minor3:
        pinfo = Path._path_cut_points(major3, max(0.0, pt[0]), closed=False, direction=True)
        base = np.asarray(pinfo[0])
        tangent = unit(np.asarray(pinfo[3]), [0.0, 1.0])
        out.append(list(base + tangent * pt[1]))
    return _merge_collinear(_dedup(out))


# ---------------------------------------------------------------------------
# Section: mask geometry
# ---------------------------------------------------------------------------


def _partition_mask_shape(l, w, h, cutsize, cutpath, gap, cutpath_centered, inverse, slop,
                          _fn=None, _fa=None, _fs=None):
    """Native geometry for a partition mask (removes half, leaving an interlocking edge)."""
    from pythonscad import polygon as _polygon, square as _square

    cs = list(cutsize) if isinstance(cutsize, (list, tuple, np.ndarray)) else [cutsize * 2, cutsize]
    path = _partition_cutpath(l, h, cs, cutpath, gap, cutpath_centered, _fn, _fa, _fs)
    ww = w * (-1 if inverse else 1)
    fullpath = list(path) + [[path[-1][0], ww], [path[0][0], ww]]
    poly = _polygon([[float(x), float(y)] for x, y in fullpath])
    if slop:
        poly = poly.offset(delta=-slop)
    poly = poly & _square([l, w * 2], center=True)
    return poly.linear_extrude(height=h, center=True)


def partition_mask(l=100, w=100, h=100, cutsize=10, cutpath="jigsaw", gap=0, cutpath_centered=True,
                   inverse=False, slop=0.0, _fn=None, _fa=None, _fs=None):
    """A mask to remove half of an object, leaving an interlocking edge (BOSL2 partition_mask()).

    Intersect it with (or subtract it from) a solid to keep the half within *w* of the cut plane.
    Pair a plain mask with an ``inverse=True`` one to split a part into two mating pieces.

    Args:
        l: length of the cut axis
        w: width of the kept part, back from the cut plane
        h: height of the part
        cutsize: cut-pattern width (scalar, or ``[length, width]``)
        cutpath: named cut pattern or an explicit 2-D path
        gap: empty gaps between pattern iterations
        cutpath_centered: keep the pattern centered (default True)
        inverse: build the mating (inverted) mask
        slop: shrink the mask by this much for a printer-fit clearance
    """
    from bosl2.shapes3d import Bosl2Solid

    return Bosl2Solid(_partition_mask_shape(l, w, h, cutsize, cutpath, gap, cutpath_centered,
                                            inverse, slop, _fn, _fa, _fs))


def partition_cut_mask(l=100, h=100, cutsize=10, cutpath="jigsaw", gap=0, cutpath_centered=True,
                       slop=0.1, _fn=None, _fa=None, _fs=None):
    """A thin mask to cut an object into two mating pieces (BOSL2 partition_cut_mask()).

    Subtract it from a solid to split it along the cut path with a *slop*-wide kerf.
    """
    from pythonscad import square as _square
    from bosl2.shapes3d import Bosl2Solid

    from bosl2.drawing import stroke as _stroke

    cs = list(cutsize) if isinstance(cutsize, (list, tuple, np.ndarray)) else [cutsize * 2, cutsize]
    path = _partition_cutpath(l, h, cs, cutpath, gap, cutpath_centered, _fn, _fa, _fs)
    ribbon = _stroke(path, width=max(0.1, slop * 2))
    return Bosl2Solid(ribbon.linear_extrude(height=h, center=True))


# ---------------------------------------------------------------------------
# Section: Partitionable mixin
# ---------------------------------------------------------------------------


def _as_vec3(v):
    a = np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a


class Partitionable:
    """Mixin adding the partitions.scad planar cuts and the partition() split as methods.

    Inherited by :class:`~bosl2.shapes3d.Bosl2Solid`. A half-cut intersects the solid with a
    half-space mask whose size defaults to the object's own bounding box (so BOSL2's ``s=``
    argument is optional). ``cut_path=`` follows a 2-D :func:`partition_path` to make an
    interlocking cut face instead of a flat plane.
    """

    def _half_mask(self, v, cpv, s, cut_path, cut_angle, offset):
        from pythonscad import polygon as _polygon

        v3 = _as_vec3(v)
        vu = unit(v3)
        if cut_path is None:
            ppath = [[-s / 2, 0.0], [s / 2, 0.0]]
        else:
            ppath = [[float(a), float(b)] for a, b in cut_path]
            if ppath[0][0] > ppath[-1][0]:
                ppath = ppath[::-1]
        poly_pts = ([[min(-s / 2, ppath[0][0]), s]]
                    + [[min(-s / 2, ppath[0][0]), ppath[0][1]]]
                    + ppath
                    + [[max(s / 2, ppath[-1][0]), ppath[-1][1]]]
                    + [[max(s / 2, ppath[-1][0]), s]])
        poly = _polygon([[float(x), float(y)] for x, y in poly_pts])
        if offset:
            poly = poly.offset(r=offset)
        mask = poly.linear_extrude(height=s, center=True)
        if bool(np.allclose(vu, UP)):
            xyv = np.asarray(FRONT, dtype=float)
        elif bool(np.allclose(vu, DOWN)):
            xyv = np.asarray(BACK, dtype=float)
        else:
            xyv = np.array([v3[0], v3[1], 0.0])
        ang = math.degrees(math.atan2(xyv[1], xyv[0])) - 90
        m = (rot_about_axis(cut_angle, v3) @ _rot4(rot_from_to(xyv, v3)) @ _zrot4(ang))
        mask = mask.multmatrix(m.tolist())
        if not np.allclose(cpv, 0):
            mask = mask.translate([float(c) for c in cpv])
        return mask

    def half_of(self, v=UP, cp=None, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the half of this solid on the side the normal *v* points to (BOSL2 half_of()).

        *cp* is a point on the cut plane, or a scalar distance to shift the plane along *v*. *s*
        (the mask size) defaults to twice the object's bounding-box reach, so it rarely needs
        setting. *cut_path* follows a 2-D :func:`partition_path` for an interlocking cut face;
        *cut_angle* spins that face about *v*; *offset* grows the mask.
        """
        v3 = _as_vec3(v)
        if cp is None:
            cpv = np.zeros(3)
        elif _is_num(cp):
            cpv = float(cp) * unit(v3)
        else:
            cpv = _as_vec3(cp)
        if s is None:
            center, size = self.bounds()
            reach = float(np.linalg.norm(size)) + float(np.linalg.norm(cpv - np.asarray(center)))
            s = 2.2 * reach + 2.0
        return self._wrap(self.shape & self._half_mask(v3, cpv, s, cut_path, cut_angle, offset))

    def left_half(self, x=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the left (-X) half, cut at ``X=x`` (BOSL2 left_half())."""
        return self.half_of(LEFT, cp=[x, 0, 0], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def right_half(self, x=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the right (+X) half, cut at ``X=x`` (BOSL2 right_half())."""
        return self.half_of(RIGHT, cp=[x, 0, 0], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def front_half(self, y=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the front (-Y) half, cut at ``Y=y`` (BOSL2 front_half())."""
        return self.half_of(FRONT, cp=[0, y, 0], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def back_half(self, y=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the back (+Y) half, cut at ``Y=y`` (BOSL2 back_half())."""
        return self.half_of(BACK, cp=[0, y, 0], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def bottom_half(self, z=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the bottom (-Z) half, cut at ``Z=z`` (BOSL2 bottom_half())."""
        return self.half_of(DOWN, cp=[0, 0, z], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def top_half(self, z=0, s=None, cut_path=None, cut_angle=0, offset=0):
        """Keep the top (+Z) half, cut at ``Z=z`` (BOSL2 top_half())."""
        return self.half_of(UP, cp=[0, 0, z], s=s, cut_path=cut_path, cut_angle=cut_angle, offset=offset)

    def partition(self, spread=10, cutsize=10, cutpath="jigsaw", gap=0, cutpath_centered=True,
                  spin=0, slop=0.0, _fn=None, _fa=None, _fs=None):
        """Cut this solid into two interlocking pieces, spread apart (BOSL2 partition()).

        Returns ``[back_piece, front_piece]`` -- the two halves with matched joining edges, moved
        *spread* apart along the (spun) Y axis so they print separately and snap back together.
        The joint follows *cutpath* (``"jigsaw"``, ``"dovetail"``, ``"hammerhead"``, ...); *spin*
        rotates the cut direction; *slop* leaves a printer-fit clearance.
        """
        center, size = self.bounds()
        cs = list(cutsize) if isinstance(cutsize, (list, tuple, np.ndarray)) else [cutsize * 2, cutsize]
        sp = math.radians(spin)
        c, sn = math.cos(sp), math.sin(sp)
        rsx = abs(size[0] * c - size[1] * sn)
        rsy = abs(size[0] * sn + size[1] * c)
        rsz = abs(size[2])
        vec = np.array([-sn, c, 0.0]) * (spread / 2)
        pieces = []
        for idx, inverse in ((0, False), (1, True)):
            mask = _partition_mask_shape(rsx, rsy, rsz, cs, cutpath, gap, cutpath_centered,
                                         inverse, slop, _fn, _fa, _fs)
            mask = mask.rotate([0, 0, spin]).translate([float(c2) for c2 in center])
            move = vec if idx == 0 else -vec
            pieces.append(self._wrap(self.shape & mask).translate([float(m) for m in move]))
        return pieces


def _zrot4(ang_deg):
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(ang_deg, [0, 0, 1])
    return m


def _rot4(angle_axis):
    angle, axis = angle_axis
    m = np.eye(4)
    m[:3, :3] = axis_angle_matrix(angle, axis)
    return m
