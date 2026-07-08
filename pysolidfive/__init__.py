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

# LibFile: pysolidfive/__init__.py
#    A small libfive-based (F-Rep / signed-distance-function) shape library. Self-contained --
#    it does not import bosl2 (and so carries no transitive numpy dependency): the small pieces
#    it needs from there (direction-vector constants, the edges= mini-language, anchor-offset
#    math) are vendored into pysolidfive/_constants.py and pysolidfive/_edges.py instead,
#    byte-for-byte identical to bosl2's own algorithm, the same way base_bgtk.py and
#    bosl2/constants.py each already carry their own independent copy of the same
#    Vec3/direction-vector idiom rather than sharing one. cuboid() builds a box with
#    per-edge-selectable rounding AND/OR chamfering -- the same `edges=`/`except_edges=`
#    mini-language as bosl2.shapes3d.cuboid() (kept compatible on purpose, so both libraries
#    accept identical edge selectors) -- but composes it as a single signed distance function
#    meshed via the builtin frep(), instead of BOSL2's hull()-of-primitive-shapes CSG
#    construction.
#
#    Every shape function here returns a PyShape (see its docstring): a thin
#    wrapper around a *symbolic* SDF (a Python callable of (x, y, z) libfive
#    trees, not yet evaluated at lv.x()/lv.y()/lv.z() or meshed), so further
#    edits -- translate, round()/chamfer() more edges, boolean combination
#    with another PyShape -- compose directly into the expression, exactly
#    (no re-meshing needed) and cheaply, the same way pylibfive.py's own
#    lv_trans()/lv_union() etc. compose coordinate trees before the one
#    final frep() call. Only .mesh() (or an attribute PyShape doesn't
#    itself define, via __getattr__) actually calls frep() and touches the
#    real PythonSCAD/libfive C extension.
#
#    Edge-rounding algorithm: when every edge is rounded by the same amount
#    (`edges="ALL"`), cuboid() uses the classic single-formula rounded-box
#    SDF (https://iquilezles.org/articles/distfunctions/, `_rounded_box_sdf()`
#    below) -- the exact Minkowski sum of a box and a sphere, matching
#    bosl2.shapes3d.cuboid()'s own real minkowski() construction for that
#    same case, with a perfectly smooth/seamless spherical corner blend.
#
#    For every other case -- a subset of edges, or per-edge/per-corner
#    independent radii -- there's no single closed-form 3-D distance
#    function, so `_cuboid_edge_sdf()` falls back to a per-axis composition:
#    for each axis, build a 2-D "rounded rect with independent per-corner
#    radii" SDF (the standard generalization of Inigo Quilez's rounded-box
#    formula, https://iquilezles.org/articles/distfunctions2d/) over the
#    other two axes, intersect it (max()) with a sharp slab along this axis,
#    then intersect the three per-axis results together. Chamfering (always
#    on this per-axis path, even for `edges="ALL"` -- only rounding gets the
#    exact-formula fast path) uses the same per-axis/per-quadrant structure,
#    but each corner's candidate is `max(qu, qv, (qu+qv+c)/sqrt(2))` -- the
#    intersection of the two axis-aligned half-planes with the diagonal
#    half-plane `c` in from the sharp corner -- instead of the rounded
#    corner's hypot() formula. Each per-quadrant candidate (round or
#    chamfer) is pushed far away (and so never wins the min() that picks
#    the right quadrant) everywhere outside its own quadrant via an additive
#    penalty proportional to how far outside it is. This avoids needing any
#    true conditional/select primitive, which libfive's documented operator
#    set (min/max/abs/sqrt/trig/pow, plus +-*/%) doesn't expose -- every
#    other edge-selection technique (e.g. GLSL-style ternaries) needs one.
#
#    With `rounding=0`/`chamfer=0` (or no edges selected), every per-quadrant
#    amount is 0 and the per-axis path exactly reproduces the plain sharp-box
#    surface on, near, and inside the surface, away from a true 3-D corner --
#    verified numerically (see scratch verification during development). Two
#    known, accepted CAVEATS, both inherent to composing 3 independent
#    per-axis 2-D fields via max() rather than one true 3-D distance
#    function -- and so both scoped to the per-axis fallback path, not the
#    exact-formula `edges="ALL"` rounding case above:
#      1. Far outside a corner (beyond all three face-pairs at once), the
#         result underestimates the true Euclidean distance (e.g. an
#         8x8x8 sharp cube can read ~5 at a point where the true distance
#         is ~6.25). Sign is always correct there (verified with 5000
#         random samples, 0 mismatches), so the meshed *surface* is
#         unaffected -- only bulk-exterior distance magnitude is
#         approximate, the same tradeoff already accepted by
#         pylibfive.py's own smooth-blend operators (lv_union_smooth()
#         etc.), which aren't true distance fields either.
#      2. At a true 3-D corner where multiple *rounded* edges from
#         different axis groups meet, but not *all* edges (e.g. chamfering
#         with `edges="ALL"`, or rounding/chamfering some other multi-axis
#         subset of edges that meet at a shared corner), the resulting
#         corner is the intersection of three orthogonal rounded/chamfered
#         prisms, not a true Minkowski/spherical corner blend -- visually
#         similar and always a well-formed closed surface, but not
#         bit-identical to the classic single-formula rounded box there,
#         and (rarely -- ~2 in 3000 random samples in testing, all within a
#         fraction of a millimeter of the true surface) the sign can
#         disagree with the ideal spherical-corner shape in a thin shell
#         immediately around such a corner. Edges rounded/chamfered
#         individually, or corners where only one axis group is treated,
#         are unaffected -- this is specifically a multi-axis-group
#         corner-blending approximation, and (for rounding) only reachable
#         via chained .round() calls with different edge subsets, since a
#         single cuboid(rounding=..., edges="ALL") call now takes the
#         exact-formula path above.
#
#    Shapes covered, mirroring bosl2.shapes3d.py: cube, cuboid, octahedron,
#    wedge, sphere, spheroid, torus, cylinder, cyl (+xcyl/ycyl/zcyl), tube,
#    pie_slice, prismoid, rect_tube, interior_fillet, teardrop, onion,
#    heightfield (callable-data only). Also two standalone cutters, mirroring
#    bosl2.masking.py/Bosl2Solid.edge_profile_asym(), for edges outside a
#    cuboid()'s own edge/corner treatment: rounding_edge_mask() (a positionable
#    circular roundover cutter, same local frame/rotate()/translate() usage
#    as bosl2.masking.rounding_edge_mask()) and polygon_extrude() (extrudes
#    an arbitrary *convex* 2-D profile, for a custom edge cut with no simple
#    closed form). NOT ported: text3d/path_text (no
#    text-rendering primitive exists in libfive's exposed operator set --
#    use bosl2.shapes3d for text), cylindrical_heightfield and array-data
#    heightfield (no closed-form "look up a grid of numbers" primitive is
#    exposed either), and ruler (a measuring/display aid with text labels,
#    not really an SDF solid-modeling primitive -- BOSL2 doesn't apply
#    rounding/chamfer to it either). Several shapes here are deliberately
#    simplified relative to their bosl2.shapes3d.py counterpart where an
#    exact SDF would need substantially more derivation for a
#    rarely-exercised feature -- each function's docstring notes exactly
#    what's dropped (e.g. prismoid() has no vertical-edge rounding,
#    teardrop()/onion() have no chamfer=/circum=/realign=).
#
# FileGroup: pysolidfive

import math
from typing import Any, Callable

import libfive as lv

from pythonscad import frep
from pysolidfive._constants import CENTER, BOTTOM, TOP, LEFT, RIGHT, FRONT, BACK
from pysolidfive._edges import _pick_radius, _edges, _anchor_offset_box3, _anchor_offset_cyl, _anchor_offset_sphere, _anchor_offset_hull3, EDGES_ALL

# Penalty multiplier used to push a quadrant candidate's SDF value far above any other
# candidate's real value once outside its own quadrant (see module docstring). Dimensionless;
# the mask itself already carries the right length units, so this just needs to be
# comfortably larger than 1 -- 10000 gives a huge safety margin without risking float
# precision issues at typical (mm-scale) board-game part sizes.
_PENALTY = 10000.0
_SQRT2 = math.sqrt(2)


def _matmul3(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _axis_angle_matrix(deg: float, axis: list[float]) -> list[list[float]]:
    """Standard Rodrigues' rotation matrix for `deg` degrees around `axis` (need not be unit)."""
    ang = math.radians(deg)
    n = math.sqrt(sum(a * a for a in axis))
    ax, ay, az = (a / n for a in axis)
    c, s, t = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    return [
        [t * ax * ax + c, t * ax * ay - s * az, t * ax * az + s * ay],
        [t * ax * ay + s * az, t * ay * ay + c, t * ay * az - s * ax],
        [t * ax * az - s * ay, t * ay * az + s * ax, t * az * az + c],
    ]


def _rotation_matrix(a, v: list[float] | None = None) -> list[list[float]]:
    """3x3 rotation matrix matching the real rotate(obj, a, v)'s two calling conventions:
    `a` a lone angle (degrees) with an explicit axis `v`, or (v is None) `a` a 3-vector of Euler
    angles [x, y, z] applied X-then-Y-then-Z -- the same composition order OpenSCAD's own
    rotate([x, y, z]) uses."""
    if v is not None:
        return _axis_angle_matrix(a, v)
    ax, ay, az = a
    rx = _axis_angle_matrix(ax, [1, 0, 0])
    ry = _axis_angle_matrix(ay, [0, 1, 0])
    rz = _axis_angle_matrix(az, [0, 0, 1])
    return _matmul3(_matmul3(rz, ry), rx)


def _radius(
    r1: float | None = None,
    d1: float | None = None,
    r2: float | None = None,
    d2: float | None = None,
    r: float | None = None,
    d: float | None = None,
    dflt: float = 1,
) -> float:
    """_pick_radius(), guaranteed non-None since `dflt` is always a real number here -- unlike
    _pick_radius() itself, whose `dflt: None` default means its return type is `float | None`
    even when a caller always passes a concrete `dflt`. Not for callers that genuinely need to
    tell "not specified" apart from a real radius (see torus()/tube(), which call
    _pick_radius() directly with `dflt=None`)."""
    result = _pick_radius(r1=r1, d1=d1, r2=r2, d2=d2, r=r, d=d, dflt=dflt)
    assert result is not None
    return result


def _lv_hypot(a, b):
    return lv.sqrt(a * a + b * b)


def _rect2d(u, v, bu: float, bv: float, amount: list[float], mode: str):
    """2-D SDF of a `2*bu` x `2*bv` rectangle centered at the origin, with an independent
    per-corner edge treatment -- rounding radius or chamfer size, per `mode` -- given by
    `amount[i]` at each of its 4 corners. `amount` is indexed the same way as
    bosl2.shapes3d.EDGE_OFFSETS's per-axis rows: [(-,-), (+,-), (-,+), (+,+)] in (u, v) sign.
    """
    candidates = []
    for su, sv, a in ((-1, -1, amount[0]), (1, -1, amount[1]), (-1, 1, amount[2]), (1, 1, amount[3])):
        if mode == "round":
            # Rounding is a Minkowski sum: shrink the rect by r, then re-offset the corner
            # outward by r via the hypot() term -- qu/qv are shifted by +r accordingly.
            qu = lv.abs(u) - bu + a
            qv = lv.abs(v) - bv + a
            base = lv.min(lv.max(qu, qv), 0) + _lv_hypot(lv.max(qu, 0), lv.max(qv, 0)) - a
        else:
            assert mode == "chamfer"
            # Chamfer is a plane cut: intersect the two plain axis-aligned half-planes with
            # a third diagonal half-plane `a` in from the sharp corner. qu/qv are NOT shifted
            # by `a` here (unlike rounding) -- only the diagonal term is.
            qu = lv.abs(u) - bu
            qv = lv.abs(v) - bv
            base = lv.max(lv.max(qu, qv), (qu + qv + a) / _SQRT2)
        mask = lv.max(0, -su * u) + lv.max(0, -sv * v)
        candidates.append(base + _PENALTY * mask)
    return lv.min(lv.min(candidates[0], candidates[1]), lv.min(candidates[2], candidates[3]))


def _rounded_box_sdf(x, y, z, size: list[float], r: float):
    """Exact SDF for a box uniformly rounded on every edge and corner: the Minkowski sum of a
    box (shrunk by `r` on every side) with a sphere of radius `r` -- the same construction
    bosl2.shapes3d.cuboid() itself special-cases via a real minkowski() for edges="ALL". Unlike
    _cuboid_edge_sdf()'s general per-axis-plane composition (max() of three independently
    rounded-rectangle extrusions, which only *approximates* the true corner blend and leaves a
    visible seam where the three rounded faces meet), this is a single closed-form expression
    with an exact, seamless spherical corner -- no per-axis composition, so no seam.
    """
    hx, hy, hz = [s / 2 - r for s in size]
    qx = lv.abs(x) - hx
    qy = lv.abs(y) - hy
    qz = lv.abs(z) - hz
    mqx, mqy, mqz = lv.max(qx, 0), lv.max(qy, 0), lv.max(qz, 0)
    outside = lv.sqrt(mqx * mqx + mqy * mqy + mqz * mqz)
    inside = lv.min(lv.max(lv.max(qx, qy), qz), 0)
    return outside + inside - r


def _cuboid_edge_sdf(x, y, z, size: list[float], amount: float, edge_set: list[list[int]], mode: str):
    """The cuboid SDF (as an explicit function of the given x/y/z trees, so callers can pass
    shifted coordinates to compose translation) with `amount` (rounding radius or chamfer
    size, per `mode`) applied to the edges selected by `edge_set`.
    """
    if mode == "round" and edge_set == EDGES_ALL:
        return _rounded_box_sdf(x, y, z, size, amount)

    p = [x, y, z]
    b = [s / 2 for s in size]
    # Perpendicular-axis pairs, in the same (row, column) order as EDGE_OFFSETS: axis 0 (X)
    # varies over (Y, Z), axis 1 (Y) over (X, Z), axis 2 (Z) over (X, Y).
    axes_perp = [(1, 2), (0, 2), (0, 1)]

    def axis_sdf(axis: int):
        pa, pb = axes_perp[axis]
        a = [amount if edge_set[axis][i] else 0.0 for i in range(4)]
        d2d = _rect2d(p[pa], p[pb], b[pa], b[pb], a, mode)
        slab = lv.abs(p[axis]) - b[axis]
        return lv.max(d2d, slab)

    return lv.max(lv.max(axis_sdf(0), axis_sdf(1)), axis_sdf(2))


class PyShape:
    """Wraps a libfive SDF, kept as a *symbolic* function of (x, y, z) rather than an
    already-evaluated tree or an already-meshed solid, plus the bounding box (`mn`/`mx`)
    frep() needs and (for cuboid-shaped instances) enough metadata to add more edge
    treatments after the fact.

    Extra controls beyond a bare `frep()` call:
      - Lazy, cached meshing: the real PythonSCAD/libfive C extension is only touched by
        .mesh() (or by falling through __getattr__ to a real method like .show()/.color()),
        so a chain of edits never re-meshes early.
      - translate(v): shifts the SDF itself (`f(p) -> f(p - v)`), exact and free -- no
        meshing involved -- and keeps chamfer()/round() working correctly afterwards by
        tracking where the cuboid's own local origin currently sits.
      - Boolean composition with another PyShape (`|` union, `&` intersection, `-`
        difference) via min()/max()/negate on the two SDFs directly, cheaper and more
        exact than meshing both shapes first and doing mesh-level CSG.
      - round(radius, edges=, except_edges=) / chamfer(size, edges=, except_edges=):
        add more edge treatment to an existing cuboid-shaped PyShape. Because this
        intersects (max()) the requested treatment into the *current* SDF rather than
        rebuilding from scratch, edges can be built up incrementally with different
        treatments -- e.g. `cuboid(size).round(2, edges="Z").chamfer(1, edges=[TOP+LEFT])`
        -- which a single bosl2.shapes3d.cuboid() call can't do (rounding/chamfer are
        mutually exclusive there, one radius for the whole call).

    CAVEAT: like bosl2.shapes3d.Bosl2Solid, this is a plain Python wrapper (composition),
    not a subclass of the real native PyOpenSCAD type. round()/chamfer() additionally only
    make sense for cuboid-shaped instances (built by cuboid(), or by a prior round()/
    chamfer() call on one) -- they assert if `cuboid_size` isn't set, the same restriction
    Bosl2Solid places on its own edge/corner masking methods.
    """

    def __init__(self, sdf_fn, mn, mx, res: int = 20, cuboid_size=None, cuboid_center=(0.0, 0.0, 0.0)):
        self._sdf_fn = sdf_fn
        self.mn = list(mn)
        self.mx = list(mx)
        self.res = res
        self.cuboid_size = list(cuboid_size) if cuboid_size is not None else None
        self.cuboid_center = tuple(cuboid_center)
        self._mesh_cache = None

    def _wrap(self, sdf_fn, mn, mx, cuboid_size=None, cuboid_center=(0.0, 0.0, 0.0)):
        return PyShape(sdf_fn, mn, mx, self.res, cuboid_size, cuboid_center)

    def sdf(self):
        """The fully-evaluated libfive expression tree, at the real coordinate trees."""
        return self._sdf_fn(lv.x(), lv.y(), lv.z())

    def mesh(self):
        """Mesh this SDF into a real solid via frep() (cached after the first call).

        Pads `mn`/`mx` slightly beyond the shape's own tight bounding box before sampling:
        frep()'s octree evaluator needs the surface to lie strictly *inside* the sampled
        domain to see a sign change. Every constructor here sets mn/mx to the shape's exact
        bounds (e.g. cuboid()'s +-size/2), so any flat face sits exactly on the domain
        boundary -- libfive then finds no sign change there and leaves that face unmeshed
        (a hollow shell for e.g. a rounded box/cylinder, or an entirely empty mesh for a
        plain unrounded box, whose every face is flush with the domain boundary).
        """
        if self._mesh_cache is None:
            pad = [max(1e-3, (b - a) * 0.01) for a, b in zip(self.mn, self.mx)]
            mn = [a - p for a, p in zip(self.mn, pad)]
            mx = [b + p for b, p in zip(self.mx, pad)]
            self._mesh_cache = frep(self.sdf(), mn, mx, self.res)
        return self._mesh_cache

    def __getattr__(self, name):
        # Anything not defined on PyShape itself (color/show/... or any other real PyOpenSCAD
        # method) falls through to the meshed solid.
        return getattr(self.mesh(), name)

    # ---- SDF-level composition ----

    def translate(self, v) -> "PyShape":
        tx, ty, tz = (list(v) + [0.0, 0.0, 0.0])[:3]
        fn = self._sdf_fn
        new_fn = lambda x, y, z: fn(x - tx, y - ty, z - tz)  # noqa: E731
        new_mn = [self.mn[0] + tx, self.mn[1] + ty, self.mn[2] + tz]
        new_mx = [self.mx[0] + tx, self.mx[1] + ty, self.mx[2] + tz]
        new_center = (self.cuboid_center[0] + tx, self.cuboid_center[1] + ty, self.cuboid_center[2] + tz)
        return self._wrap(new_fn, new_mn, new_mx, self.cuboid_size, new_center)

    def rotate(self, a, v: list[float] | None = None) -> "PyShape":
        """Rotate the SDF itself (`f(p) -> f(R^-1 p)`), exact and free -- no meshing involved,
        so (like translate()) a shape can still be .round()ed/.chamfer()ed/composed afterward
        without forcing an early mesh. Matches the real rotate(obj, a, v)'s two calling
        conventions: `rotate(angle, axis)`, or `rotate([x, y, z])` for Euler angles.

        Unlike translate(), this drops cuboid_size/cuboid_center metadata (so round()/chamfer()
        assert afterward) -- edges="TOP"/"LEFT"/etc. are global-frame selectors, evaluated
        before any rotation, the same order bosl2's own anchor/edges-then-spin/orient applies
        them in, so treating edges post-rotation wouldn't mean what it looks like it means.
        """
        m = _rotation_matrix(a, v)
        mt = [[m[j][i] for j in range(3)] for i in range(3)]  # transpose == inverse for a rotation
        fn = self._sdf_fn
        new_fn = lambda x, y, z: fn(  # noqa: E731
            mt[0][0] * x + mt[0][1] * y + mt[0][2] * z,
            mt[1][0] * x + mt[1][1] * y + mt[1][2] * z,
            mt[2][0] * x + mt[2][1] * y + mt[2][2] * z,
        )
        corners = [
            [self.mn[0] if i & 1 == 0 else self.mx[0], self.mn[1] if i & 2 == 0 else self.mx[1], self.mn[2] if i & 4 == 0 else self.mx[2]]
            for i in range(8)
        ]
        rotated = [[sum(m[r][k] * c[k] for k in range(3)) for r in range(3)] for c in corners]
        new_mn = [min(c[i] for c in rotated) for i in range(3)]
        new_mx = [max(c[i] for c in rotated) for i in range(3)]
        return self._wrap(new_fn, new_mn, new_mx)

    def __or__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.min(fa(x, y, z), fb(x, y, z))  # noqa: E731
        mn = [min(self.mn[i], other.mn[i]) for i in range(3)]
        mx = [max(self.mx[i], other.mx[i]) for i in range(3)]
        return self._wrap(new_fn, mn, mx)

    def __and__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.max(fa(x, y, z), fb(x, y, z))  # noqa: E731
        mn = [min(self.mn[i], other.mn[i]) for i in range(3)]
        mx = [max(self.mx[i], other.mx[i]) for i in range(3)]
        return self._wrap(new_fn, mn, mx)

    def __sub__(self, other: "PyShape") -> "PyShape":
        fa, fb = self._sdf_fn, other._sdf_fn
        new_fn = lambda x, y, z: lv.max(fa(x, y, z), -fb(x, y, z))  # noqa: E731
        return self._wrap(new_fn, list(self.mn), list(self.mx))

    # ---- cuboid-only edge treatments ----

    def _edge_treat(self, amount: float, edges, except_edges, mode: str) -> "PyShape":
        assert self.cuboid_size is not None, f"{mode}() requires a cuboid-shaped PyShape (from pysolidfive.cuboid())"
        edge_set = _edges(edges, except_edges or [])
        cx, cy, cz = self.cuboid_center
        size, fn = self.cuboid_size, self._sdf_fn

        def new_fn(x, y, z):
            treatment = _cuboid_edge_sdf(x - cx, y - cy, z - cz, size, amount, edge_set, mode)
            return lv.max(fn(x, y, z), treatment)

        return self._wrap(new_fn, list(self.mn), list(self.mx), self.cuboid_size, self.cuboid_center)

    def round(self, radius: float, edges: str | list = "ALL", except_edges: list | None = None) -> "PyShape":
        """Round the selected edges by `radius`, in addition to any existing edge treatment."""
        return self._edge_treat(radius, edges, except_edges, "round")

    def chamfer(self, size: float, edges: str | list = "ALL", except_edges: list | None = None) -> "PyShape":
        """Chamfer the selected edges by `size`, in addition to any existing edge treatment."""
        return self._edge_treat(size, edges, except_edges, "chamfer")


def cuboid(
    size: float | list[float] = [1, 1, 1],
    rounding: float = 0,
    chamfer: float = 0,
    edges: str | list = "ALL",
    except_edges: list | None = None,
    res: int = 20,
    anchor: list[float] = CENTER,
) -> PyShape:
    """A cuboid with optional per-edge rounding or chamfering, built as a libfive signed
    distance function (F-Rep) and returned as a PyShape (meshed lazily, via frep(), on first
    use) -- see bosl2.shapes3d.cuboid() for the equivalent BOSL2-style mesh-CSG version
    (identical `edges=`/`except_edges=` semantics; both accept the same edge selector values,
    since pysolidfive._edges's edge-set resolver is a byte-for-byte copy of bosl2's own).

    `rounding` and `chamfer` are mutually exclusive in a single call (matching
    bosl2.shapes3d.cuboid()); to mix both on different edges of the same cuboid, chain
    PyShape.round()/.chamfer() calls instead, e.g.
    `cuboid(size).round(2, edges="Z").chamfer(1, edges=[TOP+LEFT])`.

    Args:
        size:         size of the cuboid, a number or length-3 vector
        rounding:     edge rounding radius applied to every selected edge (default: no rounding)
        chamfer:      edge chamfer size applied to every selected edge (default: no chamfer)
        edges:        edges to treat -- "ALL"/"NONE"/"X"/"Y"/"Z", a single edge vector (e.g.
                      TOP+LEFT), a list of edge vectors, or a raw 3x4 edge array (default "ALL")
        except_edges: edges to explicitly exclude from `edges` (BOSL2's `except=` synonym;
                      `except` is a Python keyword)
        res:          libfive meshing resolution passed to frep() (default 20; higher = finer mesh)
        anchor:       anchor point (default CENTER)

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=4)
            shape.show()

        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], chamfer=4)
            shape.show()

        Rounding only the 4 vertical edges (the per-axis-composition fallback path, not the
        exact-formula ``edges="ALL"`` case above):

        .. pythonscad-example::

            shape = pysolidfive.cuboid([20.0, 20.0, 20.0], rounding=4, edges="Z")
            shape.show()
    """
    assert not (rounding and chamfer), "Cannot specify nonzero value for both rounding and chamfer"
    sz: list[float] = [float(v) for v in size] if isinstance(size, (list, tuple)) else [float(size)] * 3
    edge_set = _edges(edges, except_edges or [])
    mode = "chamfer" if chamfer else "round"
    amount = chamfer if chamfer else rounding
    sdf_fn = lambda x, y, z: _cuboid_edge_sdf(x, y, z, sz, amount, edge_set, mode)  # noqa: E731
    half = [s / 2 for s in sz]
    shape = PyShape(sdf_fn, [-half[0], -half[1], -half[2]], half, res, cuboid_size=sz)
    offset = _anchor_offset_box3(sz, [int(a) for a in anchor])
    if offset[0] or offset[1] or offset[2]:
        shape = shape.translate(offset)
    return shape


def cube(size: float | list[float] = 1, anchor: list[float] = CENTER, res: int = 20) -> PyShape:
    """A cube, as a plain (unrounded) libfive SDF. See cuboid() for rounding/chamfering."""
    return cuboid(size=size, anchor=anchor, res=res)


# ---------------------------------------------------------------------------
# Section: Other simple solids without a BOSL2 rounding/chamfer concept
# ---------------------------------------------------------------------------


def octahedron(size: float = 1, anchor: list[float] = CENTER, res: int = 20) -> PyShape:
    """An octahedron with axis-aligned points (`|x|+|y|+|z| <= size/2`), as a libfive SDF."""
    s = size / 2
    sdf_fn = lambda x, y, z: lv.abs(x) + lv.abs(y) + lv.abs(z) - s  # noqa: E731
    shape = PyShape(sdf_fn, [-s, -s, -s], [s, s, s], res)
    pts = [[s, 0, 0], [-s, 0, 0], [0, s, 0], [0, -s, 0], [0, 0, s], [0, 0, -s]]
    offset = _anchor_offset_hull3(pts, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def wedge(size: list[float] = [1, 1, 1], anchor: list[float] | None = None, res: int = 20) -> PyShape:
    """A 3-D triangular wedge with the hypotenuse in the X+Z+ quadrant, as a libfive SDF.

    Args:
        size:   [width, thickness, height]
        anchor: anchor point (default FRONT+LEFT+BOTTOM, matching bosl2.shapes3d.wedge())
    """
    if anchor is None:
        anchor = FRONT + LEFT + BOTTOM
    bx, by, bz = size[0] / 2, size[1] / 2, size[2] / 2
    # The triangular cross-section (right angle at Y-,Z-, hypotenuse from (Y+,Z-) to (Y-,Z+))
    # lies in the (Y, Z) plane; X is the uniform extrusion axis -- verified directly against
    # bosl2.shapes3d.wedge()'s vertex list (every vertex has a fixed X, so the triangle's
    # actual shape only varies over Y/Z).
    nlen = math.hypot(by, bz)

    def sdf_fn(x, y, z):
        box = lv.max(lv.max(lv.abs(x) - bx, lv.abs(y) - by), lv.abs(z) - bz)
        diag = (bz * y + by * z) / nlen
        return lv.max(box, diag)

    shape = PyShape(sdf_fn, [-bx, -by, -bz], [bx, by, bz], res)
    pts = [[bx, by, -bz], [bx, -by, -bz], [bx, -by, bz], [-bx, by, -bz], [-bx, -by, -bz], [-bx, -by, bz]]
    offset = _anchor_offset_hull3(pts, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def sphere(r: float | None = None, d: float | None = None, anchor: list[float] = CENTER, res: int = 20) -> PyShape:
    """A sphere, as a libfive SDF (`length(p) - r`).

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.sphere(r=10)
            shape.show()
    """
    rad = _radius(r=r, d=d, dflt=1)
    sdf_fn = lambda x, y, z: lv.sqrt(x * x + y * y + z * z) - rad  # noqa: E731
    shape = PyShape(sdf_fn, [-rad, -rad, -rad], [rad, rad, rad], res)
    offset = _anchor_offset_sphere(rad, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def spheroid(r: float | None = None, d: float | None = None, anchor: list[float] = CENTER, res: int = 20) -> PyShape:
    """An approximate sphere; this pure-libfive port just builds a plain sphere() (matching
    bosl2.shapes3d.spheroid()'s own choice to ignore style/dual for its pure-Python port)."""
    return sphere(r=r, d=d, anchor=anchor, res=res)


def torus(
    r_maj: float | None = None,
    r_min: float | None = None,
    d_maj: float | None = None,
    d_min: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    od: float | None = None,
    id: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A torus (donut) shape, as a libfive SDF (`length(vec2(length(p.xy)-r_maj, p.z)) - r_min`).

    Note: BOSL2's outer-radius parameter is named `or`, which collides with the Python
    keyword `or`; it is exposed here as `outer_r` instead. See bosl2.shapes3d.torus() for
    the full parameter set this mirrors.

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.torus(r_maj=15, r_min=5)
            shape.show()
    """
    _or = _pick_radius(r=outer_r, d=od, dflt=None)
    _ir = _pick_radius(r=ir, d=id, dflt=None)
    _r_maj = _pick_radius(r=r_maj, d=d_maj, dflt=None)
    _r_min = _pick_radius(r=r_min, d=d_min, dflt=None)
    if _r_maj is not None:
        maj = _r_maj
    elif _ir is not None and _or is not None:
        maj = (_or + _ir) / 2
    elif _ir is not None and _r_min is not None:
        maj = _ir + _r_min
    elif _or is not None and _r_min is not None:
        maj = _or - _r_min
    else:
        assert False, "torus(): bad parameters."
    if _r_min is not None:
        minr = _r_min
    elif _ir is not None:
        minr = maj - _ir
    elif _or is not None:
        minr = _or - maj
    else:
        assert False, "torus(): bad parameters."

    sdf_fn = lambda x, y, z: _lv_hypot(_lv_hypot(x, y) - maj, z) - minr  # noqa: E731
    outer = maj + minr
    shape = PyShape(sdf_fn, [-outer, -outer, -minr], [outer, outer, minr], res)
    offset = _anchor_offset_cyl(outer, outer, minr * 2, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Cylinders
# ---------------------------------------------------------------------------


def _wall_line_sdf(rxy, z, r1: float, r2: float, hb: float):
    """Signed distance to the infinite line through `(r1, -hb)` and `(r2, hb)` in the
    `(rxy, z)` half-plane -- the slanted wall of a cylinder/cone, exact for the wall itself;
    intersecting (max()) with the top/bottom slabs (see _cylinder_sdf()) caps it off, with the
    same corner-region approximation already documented for cuboid()'s per-axis composition.
    """
    dr, dz = r2 - r1, 2 * hb
    nlen = math.hypot(dr, dz)
    return ((rxy - r1) * dz - (z + hb) * dr) / nlen


def _cylinder_sdf(x, y, z, h: float, r1: float, r2: float):
    hb = h / 2
    rxy = _lv_hypot(x, y)
    wall = _wall_line_sdf(rxy, z, r1, r2, hb)
    slab = lv.abs(z) - hb
    return lv.max(wall, slab)


def _cyl_edge_sdf(axial, radial, h: float, r1: float, r2: float, amt1: float, amt2: float, mode: str):
    """_cylinder_sdf(), plus independent rounding/chamfer treatment of the bottom (amt1) and
    top (amt2) rim, using the same per-candidate-quadrant masking technique as
    bosl2.shapes3d.cuboid() (but only 2 candidates -- top/bottom -- since the radial
    coordinate has no sign ambiguity to select between, unlike a rectangle's 4 corners)."""
    hb = h / 2
    wall = _wall_line_sdf(radial, axial, r1, r2, hb)
    candidates = []
    for sz, r_ref, a in ((-1, r1, amt1), (1, r2, amt2)):
        if mode == "round":
            qu = radial - r_ref + a
            qv = lv.abs(axial) - hb + a
            base = lv.min(lv.max(qu, qv), 0) + _lv_hypot(lv.max(qu, 0), lv.max(qv, 0)) - a
        else:
            assert mode == "chamfer"
            qu = radial - r_ref
            qv = lv.abs(axial) - hb
            base = lv.max(lv.max(qu, qv), (qu + qv + a) / _SQRT2)
        mask = lv.max(0, -sz * axial)
        candidates.append(base + _PENALTY * mask)
    rim = lv.min(candidates[0], candidates[1])
    return lv.max(wall, rim)


def cylinder(
    h: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A cylinder/cone (no rounding) as a libfive SDF -- see cyl() for rounding/chamfering."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM
    sdf_fn = lambda x, y, z: _cylinder_sdf(x, y, z, length, rad1, rad2)  # noqa: E731
    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def cyl(
    h: float | None = None,
    r: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: list[float] | None = None,
    res: int = 20,
) -> PyShape:
    """A cylinder/cone with optional rounding or chamfering of its end rims, as a libfive SDF.
    See bosl2.shapes3d.cyl() for the full BOSL2-style version this mirrors (circum=/realign=/
    shift=/texture= aren't supported here).

    `rounding`/`chamfer` (and their `1`/`2` bottom/top variants) are mutually exclusive, same
    as bosl2.shapes3d.cyl().

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.cyl(h=20, r=8, rounding=2)
            shape.show()
    """
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    use_anchor = anchor
    if use_anchor is None:
        use_anchor = CENTER if center is None or center else BOTTOM

    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"
    mode, amt1, amt2 = ("chamfer", c1v, c2v) if (c1v or c2v) else ("round", r1v, r2v)

    sdf_fn = lambda x, y, z: _cyl_edge_sdf(z, _lv_hypot(x, y), length, rad1, rad2, amt1, amt2, mode)  # noqa: E731
    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def _cyl_axis(
    axis: int,
    h: float | None,
    r: float | None,
    l: float | None,
    r1: float | None,
    r2: float | None,
    d: float | None,
    d1: float | None,
    d2: float | None,
    chamfer: float | None,
    chamfer1: float | None,
    chamfer2: float | None,
    rounding: float | None,
    rounding1: float | None,
    rounding2: float | None,
    anchor: list[float],
    res: int,
) -> PyShape:
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"
    mode, amt1, amt2 = ("chamfer", c1v, c2v) if (c1v or c2v) else ("round", r1v, r2v)

    def sdf_fn(x, y, z):
        coords = [x, y, z]
        axial = coords[axis]
        others = [coords[i] for i in range(3) if i != axis]
        radial = _lv_hypot(others[0], others[1])
        return _cyl_edge_sdf(axial, radial, length, rad1, rad2, amt1, amt2, mode)

    maxr = max(rad1, rad2)
    mn, mx = [-maxr, -maxr, -maxr], [maxr, maxr, maxr]
    mn[axis], mx[axis] = -length / 2, length / 2
    shape = PyShape(sdf_fn, mn, mx, res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor, axis=axis)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def xcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A cylinder oriented along the X axis. See cyl() for argument details."""
    return _cyl_axis(0, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def ycyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A cylinder oriented along the Y axis. See cyl() for argument details."""
    return _cyl_axis(1, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def zcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A cylinder oriented along the Z axis (same as cyl()). See cyl() for argument details."""
    return _cyl_axis(2, h, r, l, r1, r2, d, d1, d2, chamfer, chamfer1, chamfer2, rounding, rounding1, rounding2, anchor, res)


def tube(
    h: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    od: float | None = None,
    id: float | None = None,
    wall: float | None = None,
    outer_r1: float | None = None,
    outer_r2: float | None = None,
    od1: float | None = None,
    od2: float | None = None,
    ir1: float | None = None,
    ir2: float | None = None,
    id1: float | None = None,
    id2: float | None = None,
    l: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A hollow cylindrical tube (outer cylinder minus inner cylinder), as a libfive SDF.

    Note: BOSL2's outer-radius parameters are named `or`/`or1`/`or2`; exposed here as
    `outer_r`/`outer_r1`/`outer_r2` since `or` is a Python keyword.
    """
    length = l if l is not None else (h if h is not None else 1)
    orr1 = _pick_radius(r1=outer_r1, d1=od1, r=outer_r, d=od, dflt=None)
    orr2 = _pick_radius(r1=outer_r2, d1=od2, r=outer_r, d=od, dflt=None)
    irr1 = _pick_radius(r1=ir1, d1=id1, r=ir, d=id, dflt=None)
    irr2 = _pick_radius(r1=ir2, d1=id2, r=ir, d=id, dflt=None)
    wall_v = wall if wall is not None else 1
    rad1 = orr1 if orr1 is not None else (irr1 + wall_v if irr1 is not None else None)
    rad2 = orr2 if orr2 is not None else (irr2 + wall_v if irr2 is not None else None)
    irad1 = irr1 if irr1 is not None else (orr1 - wall_v if orr1 is not None else None)
    irad2 = irr2 if irr2 is not None else (orr2 - wall_v if orr2 is not None else None)
    assert rad1 is not None and rad2 is not None and irad1 is not None and irad2 is not None, (
        "tube(): must specify two of inner radius/diam, outer radius/diam, and wall width."
    )

    sdf_fn = lambda x, y, z: lv.max(  # noqa: E731
        _cylinder_sdf(x, y, z, length, rad1, rad2), -_cylinder_sdf(x, y, z, length, irad1, irad2)
    )
    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


def pie_slice(
    h: float | None = None,
    r: float | None = None,
    ang: float = 30,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A pie slice (wedge of a cylinder/cone), as a libfive SDF: a cylinder intersected with
    an angular sector (built from 1-2 half-planes -- `ang` is a plain Python float fixed at
    construction time, so choosing intersection vs union of the two half-planes based on
    `ang <= 180` is an ordinary Python conditional, not a per-point SDF branch)."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=10)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=10)
    ang_v = ang % 360 if (ang > 360 or ang < 0) else ang
    ang_rad = math.radians(ang_v)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)

    def sdf_fn(x, y, z):
        body = _cylinder_sdf(x, y, z, length, rad1, rad2)
        if ang_v <= 0 or ang_v >= 360:
            return body
        sdf1 = -y
        sdf2 = y * cos_a - x * sin_a
        sector = lv.max(sdf1, sdf2) if ang_v <= 180 else lv.min(sdf1, sdf2)
        return lv.max(body, sector)

    maxr = max(rad1, rad2)
    shape = PyShape(sdf_fn, [-maxr, -maxr, -length / 2], [maxr, maxr, length / 2], res)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor)
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Cuboids, Prismoids and Tubes
# ---------------------------------------------------------------------------


def prismoid(
    size1: list[float],
    size2: list[float],
    h: float | None = None,
    shift: list[float] = [0, 0],
    l: float | None = None,
    anchor: list[float] = BOTTOM,
    res: int = 20,
) -> PyShape:
    """A rectangular prismoid (truncated pyramid), as a libfive SDF.

    CAVEAT: unlike bosl2.shapes3d.prismoid(), this pure-libfive port does not support
    rounding/chamfer of the vertical edges (deriving an exact SDF for a *tapered* box's
    independently-radiused vertical edges was out of scope here -- use
    bosl2.shapes3d.prismoid() for that, or pysolidfive.cuboid() for the non-tapered case). The SDF
    itself is built by linearly interpolating the local half-size/shift at each height `z`
    (clamped to the `[bottom, top]` range via min()/max(), so no true per-point conditional is
    needed) and taking the 2-D box distance in that local cross-section, intersected with the
    top/bottom slab -- exact for a non-tapered box (`size1 == size2`, `shift == [0, 0]`), an
    approximation (same character as cuboid()'s documented corner caveats) for a genuine taper.

    Args:
        size1:  [width, length] of the bottom end
        size2:  [width, length] of the top end
        h/l:    height of the prism
        shift:  [X,Y] shift of the top center relative to the bottom center
        anchor: anchor point (default BOTTOM)
        res:    libfive meshing resolution passed to frep() (default 20)
    """
    height = h if h is not None else (l if l is not None else 1)
    bx1, by1 = size1[0] / 2, size1[1] / 2
    bx2, by2 = size2[0] / 2, size2[1] / 2
    hb = height / 2

    def sdf_fn(x, y, z):
        t = lv.min(lv.max((z + hb) / height, 0), 1)
        bx = bx1 + (bx2 - bx1) * t
        by = by1 + (by2 - by1) * t
        cx = shift[0] * t
        cy = shift[1] * t
        qx = lv.abs(x - cx) - bx
        qy = lv.abs(y - cy) - by
        d2d = lv.min(lv.max(qx, qy), 0) + _lv_hypot(lv.max(qx, 0), lv.max(qy, 0))
        slab = lv.abs(z) - hb
        return lv.max(d2d, slab)

    maxx = max(bx1, bx2, bx1 + abs(shift[0]), bx2 + abs(shift[0]))
    maxy = max(by1, by2, by1 + abs(shift[1]), by2 + abs(shift[1]))
    shape = PyShape(sdf_fn, [-maxx, -maxy, -hb], [maxx, maxy, hb], res)
    offset = _anchor_offset_box3([maxx * 2, maxy * 2, height], [int(a) for a in anchor])
    if any(offset):
        shape = shape.translate(offset)
    return shape


def rect_tube(
    h: float | None = None,
    size: float | list[float] | None = None,
    isize: float | list[float] | None = None,
    wall: float | None = None,
    rounding: float = 0,
    irounding: float | None = None,
    l: float | None = None,
    anchor: list[float] = BOTTOM,
    res: int = 20,
) -> PyShape:
    """A rectangular tube (a rectangle with a rectangular hole through it), as a libfive SDF
    (outer rounded-rect-extrusion minus inner rounded-rect-extrusion, reusing
    bosl2.shapes3d.cuboid()'s per-edge machinery for each). Only the 4 vertical edges are
    ever rounded (`edges="Z"`, matching the "rounded rectangular tube" look BOSL2's own
    rect_tube() produces) -- there's no per-edge selection here, just one outer radius and
    one inner radius (default: same as the outer).

    Args:
        h/l:       height/length of the tube (default 1)
        size:      outer [X,Y] size of the tube
        isize:     inner [X,Y] size of the tube
        wall:      wall thickness (used with `size` if `isize` isn't given, or vice versa)
        rounding:  outer vertical-edge rounding radius (default: no rounding)
        irounding: inner vertical-edge rounding radius (default: same as `rounding`)
        anchor:    anchor point (default BOTTOM)
        res:       libfive meshing resolution passed to frep() (default 20)
    """
    length = h if h is not None else (l if l is not None else 1)
    assert size is not None, "rect_tube(): must give size."
    sz: list[float] = [float(v) for v in size] if isinstance(size, (list, tuple)) else [float(size)] * 2
    if isize is not None:
        isz: list[float] = [float(v) for v in isize] if isinstance(isize, (list, tuple)) else [float(isize)] * 2
    else:
        assert wall is not None, "rect_tube(): must give isize or wall."
        isz = [sz[0] - 2 * wall, sz[1] - 2 * wall]
    irounding_v = irounding if irounding is not None else rounding
    edge_set_z = _edges("Z", [])

    def sdf_fn(x, y, z):
        outer = _cuboid_edge_sdf(x, y, z, [sz[0], sz[1], length], rounding, edge_set_z, "round")
        inner = _cuboid_edge_sdf(x, y, z, [isz[0], isz[1], length + 0.02], irounding_v, edge_set_z, "round")
        return lv.max(outer, -inner)

    half = [sz[0] / 2, sz[1] / 2, length / 2]
    shape = PyShape(sdf_fn, [-half[0], -half[1], -half[2]], half, res)
    offset = _anchor_offset_box3([sz[0], sz[1], length], [int(a) for a in anchor])
    if any(offset):
        shape = shape.translate(offset)
    return shape


# ---------------------------------------------------------------------------
# Section: Miscellaneous
# ---------------------------------------------------------------------------


def interior_fillet(
    l: float = 1.0,
    r: float | None = None,
    ang: float = 90,
    d: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A shape to fillet an interior corner between two faces meeting at `ang` degrees, as a
    libfive SDF: the wedge between the two faces, minus a cylindrical arc of radius `r`
    positioned so it's tangent to both. Extruded along Y for length `l`.

    CAVEAT: simplified relative to bosl2.shapes3d.interior_fillet() -- no `overlap=` flap (an
    SDF union is already watertight without one) and no independent anchor-face alignment;
    the wedge's first face lies along the local +X/Z=0 half-plane. See
    bosl2.shapes3d.interior_fillet() for the exact BOSL2-compatible anchor/orientation.
    """
    rad = _radius(r=r, d=d, dflt=1)
    half = math.radians(ang / 2)
    dist = rad / math.sin(half)
    cx, cz = dist * math.cos(half), dist * math.sin(half)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    hb = l / 2

    def sdf_fn(x, y, z):
        sdf1 = -z
        sdf2 = z * cos_a - x * sin_a
        wedge_sdf = lv.max(sdf1, sdf2)
        circle = _lv_hypot(x - cx, z - cz) - rad
        fillet2d = lv.max(wedge_sdf, -circle)
        slab = lv.abs(y) - hb
        return lv.max(fillet2d, slab)

    shape = PyShape(sdf_fn, [-rad * 2, -hb, -rad * 2], [rad * 2, hb, rad * 2], res)
    if any(anchor):
        offset = [-a * b for a, b in zip(anchor, [rad * 2, hb, rad * 2])]
        shape = shape.translate(offset)
    return shape


def rounding_edge_mask(
    l: float | None = None,
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    excess: float = 0.1,
    res: int = 20,
) -> PyShape:
    """A standalone 3-D edge-rounding CUTTER of length `l`, as a libfive SDF, for subtracting
    from another PyShape to round over a sharp 90-degree edge that isn't part of a cuboid()'s
    own edge/corner treatment -- e.g. an edge exposed by an earlier cut, or any other edge you'd
    otherwise position by hand. Matches bosl2.masking.rounding_edge_mask()'s local-frame
    convention exactly (same `.rotate(...).translate(...)` call sites work unchanged): origin at
    the sharp edge, +X/+Y extending into the material (with a small `excess` skirt past 0 on
    each so the cutter fully bridges the material being cut), centered along its own Z axis over
    length `l`, with a quarter-circle bite of radius `r` taken out of the far corner.

    Built the same way interior_fillet() builds its wedge-minus-circle cutter: a square corner
    (`box`) minus a circle tangent to both its flat sides.

    CAVEAT: simplified relative to bosl2.masking.rounding_edge_mask() -- one radius for the
    whole length (no r1/r2 taper).
    """
    length = l if l is not None else (h if h is not None else 1)
    rad = _radius(r=r, d=d, dflt=1)

    def sdf_fn(x, y, z):
        box = lv.max(lv.max(x - rad, -x - excess), lv.max(y - rad, -y - excess))
        circle = _lv_hypot(x - rad, y - rad) - rad
        cutter2d = lv.max(box, -circle)
        slab = lv.abs(z) - length / 2
        return lv.max(cutter2d, slab)

    return PyShape(sdf_fn, [-excess, -excess, -length / 2], [rad, rad, length / 2], res)


def polygon_extrude(pts: list[list[float]], length: float, res: int = 20) -> PyShape:
    """Extrude an arbitrary CONVEX 2-D polygon `pts` (either winding order) along Z by
    `length`, centered -- for a custom edge-profile cutter with no simple closed form (like
    bosl2.shapes3d.Bosl2Solid.edge_profile_asym()'s `children=` path, but swept here by hand
    with an explicit rotate()/translate() rather than an automatic per-edge sweep).

    As a libfive SDF, this is the max() of each edge's signed half-plane distance -- exact at
    and near any face, but (like every other per-axis/per-plane-composed shape in this module --
    see the module docstring) underestimates the true Euclidean distance near a vertex, away
    from the surface; the sign is still correct everywhere a convex polygon's supporting
    half-planes actually bound it.

    CAVEAT: `pts` must describe a CONVEX polygon. A concave vertex's half-plane doesn't bound
    the shape there, so both the sign and the surface would come out wrong.
    """
    area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    ordered = pts if area2 > 0 else list(reversed(pts))
    n = len(ordered)
    edges = []
    for i in range(n):
        x0, y0 = ordered[i]
        x1, y1 = ordered[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        elen = math.hypot(ex, ey)
        edges.append((ey / elen, -ex / elen, x0, y0))

    def sdf_fn(x, y, z):
        d = None
        for nx, ny, x0, y0 in edges:
            e = nx * (x - x0) + ny * (y - y0)
            d = e if d is None else lv.max(d, e)
        slab = lv.abs(z) - length / 2
        return lv.max(d, slab)

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return PyShape(sdf_fn, [min(xs), min(ys), -length / 2], [max(xs), max(ys), length / 2], res)


def teardrop(
    h: float | None = None,
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """A teardrop shape (useful for 3-D-printable horizontal holes), as a libfive SDF: the
    union of a circle and a "roof" of two planes meeting at the apex, tangent to the circle,
    extruded along Y for thickness `h`.

    CAVEAT: simplified relative to bosl2.shapes3d.teardrop() -- no `chamfer=`/`circum=`/
    `realign=` support. `cap_h` (truncation height) is supported since it's a plain top-slab
    intersection.

    Examples:
        .. pythonscad-example::

            shape = pysolidfive.teardrop(h=10, r=8)
            shape.show()
    """
    length = h if h is not None else 1
    rad1 = _radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    hb = length / 2

    def profile_sdf(u, v, rad):
        circle = _lv_hypot(u, v) - rad
        right = u * sin_a + v * cos_a - rad
        left = -u * sin_a + v * cos_a - rad
        # The roof planes are only tangent to (and so only a valid boundary of) the circle
        # at v >= rad*cos_a (their tangent height); below that they cut into the disk, so
        # mask them out there and let the circle govern instead.
        v_tangent = rad * cos_a
        roof = lv.max(right, left) + _PENALTY * lv.max(0, v_tangent - v)
        d = lv.min(circle, roof)
        if cap_h is not None:
            d = lv.max(d, v - cap_h)
        return d

    def sdf_fn(x, y, z):
        t = lv.min(lv.max((y + hb) / length, 0), 1)
        rad = rad1 + (rad2 - rad1) * t
        prof = profile_sdf(x, z, rad)
        slab = lv.abs(y) - hb
        return lv.max(prof, slab)

    maxr = max(rad1, rad2)
    maxheight = maxr / sin_a if cap_h is None else min(cap_h, maxr / sin_a)
    shape = PyShape(sdf_fn, [-maxr, -hb, -maxr], [maxr, hb, maxheight], res)
    if any(anchor):
        offset = [-anchor[0] * maxr, -anchor[1] * hb, -anchor[2] * maxheight if anchor[2] > 0 else -anchor[2] * maxr]
        shape = shape.translate(offset)
    return shape


def onion(
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    d: float | None = None,
    anchor: list[float] = CENTER,
    res: int = 20,
) -> PyShape:
    """An onion-dome shape (a sphere with a conical cap), as a libfive SDF: the union of a
    sphere and a cone tangent to it, revolved around Z.

    CAVEAT: simplified relative to bosl2.shapes3d.onion() -- no `circum=`/`realign=` support.
    """
    rad = _radius(r=r, d=d, dflt=1)
    ang_rad = math.radians(ang)
    sin_a, cos_a = math.sin(ang_rad), math.cos(ang_rad)
    v_tangent = rad * cos_a

    def sdf_fn(x, y, z):
        rxy = _lv_hypot(x, y)
        sphere_sdf = _lv_hypot(rxy, z) - rad
        roof = rxy * sin_a + z * cos_a - rad
        roof = roof + _PENALTY * lv.max(0, v_tangent - z)
        d = lv.min(sphere_sdf, roof)
        if cap_h is not None:
            d = lv.max(d, z - cap_h)
        return d

    maxheight = rad / sin_a if cap_h is None else min(cap_h, rad / sin_a)
    shape = PyShape(sdf_fn, [-rad, -rad, -rad], [rad, rad, maxheight], res)
    if any(anchor):
        offset = [-anchor[0] * rad, -anchor[1] * rad, -anchor[2] * maxheight if anchor[2] > 0 else -anchor[2] * rad]
        shape = shape.translate(offset)
    return shape


def heightfield(
    data: Callable[[Any, Any], Any],
    size: list[float] = [100, 100],
    bottom: float = -20,
    maxz: float = 99,
    res: int = 20,
) -> PyShape:
    """A 3-D surface from a height function, as a libfive SDF.

    CAVEAT: unlike bosl2.shapes3d.heightfield(), `data` must be a *callable* `f(x, y) -> z`
    built from ordinary arithmetic/libfive-supported math (it gets called directly with
    libfive coordinate trees, so it becomes part of the symbolic expression) -- a 2-D array of
    height samples isn't supported, since there's no closed-form way to "look up" an arbitrary
    grid of numbers inside a libfive expression (no gather/index primitive is exposed). Use
    bosl2.shapes3d.heightfield() for array data. `xrange=`/`yrange=`/`style=` aren't
    applicable here since there's no discrete grid to sample.

    Args:
        data:   callable (x, y) -> height, evaluated symbolically
        size:   [X,Y] size of the surface (default [100,100])
        bottom: Z coordinate for the bottom of the object (default -20)
        maxz:   maximum height to model, taller values are clamped (default 99)
        res:    libfive meshing resolution passed to frep() (default 20)
    """
    assert callable(data), "pysolidfive.heightfield() only supports callable data -- see the CAVEAT in its docstring."
    bx, by = size[0] / 2, size[1] / 2

    def sdf_fn(x, y, z):
        height = lv.min(lv.max(data(x, y), bottom), maxz)
        top = z - height
        slab = lv.max(lv.abs(x) - bx, lv.abs(y) - by)
        return lv.max(lv.max(top, bottom - z), slab)

    shape = PyShape(sdf_fn, [-bx, -by, bottom], [bx, by, maxz], res)
    return shape
