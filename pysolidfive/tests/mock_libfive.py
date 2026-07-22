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

# LibFile: pysolidfive/tests/mock_libfive.py
#    A numeric-evaluation stand-in for the real `libfive` module (and just enough of
#    `pythonscad`/`openscad` for pysolidfive to load -- pysolidfive itself has no bosl2
#    dependency, so nothing beyond this stand-in is needed), so pysolidfive's SDF math can be
#    exercised and checked against hand-derived expected values without a real PythonSCAD/libfive
#    build -- which this environment doesn't have.
#
#    Also shared, unmodified, by every other library's mock test suite in the parent repo's own
#    tests/ directory (test_labels.py, test_base_bgtk.py, test_components.py, test_lids_base.py,
#    test_sliding_box.py) -- those libraries build real geometry via native primitives/BOSL2/the
#    bosl2/ port rather than SDFs, so this mock only stands in for whatever small pysolidfive
#    pieces they compose with, but they still need the same `libfive`/`pythonscad` stub installed
#    before *anything* (including pysolidfive) gets imported in the same process.
#
#    Every libfive "Tree" here is a plain Python closure `(x, y, z) -> float`, built up the
#    same way the real libfive Python bindings build a symbolic expression tree: each
#    operator/function wraps its operands in a new closure rather than evaluating immediately.
#    frep() doesn't mesh anything -- it just returns a `_FrepResult` that remembers the SDF
#    closure and bounds, and exposes `.sample(x, y, z)` to evaluate it directly and
#    `.translate(v)` to test the anchor/translate machinery.
#
#    This module must be imported (for its module-level `install()` side effect, or by calling
#    `install()` explicitly) *before* `pysolidfive` is imported anywhere in the process, since
#    pysolidfive does `import libfive as lv` / `from pythonscad import frep` at module load time.
#    Import it as a flat top-level module (`import mock_libfive`, with this directory added to
#    `sys.path`), not as `pysolidfive.tests.mock_libfive` -- the dotted form forces Python to
#    import the *real* `pysolidfive` package first (to reach the `tests` submodule inside it),
#    which fails before this stand-in ever gets a chance to install itself.
#
# FileGroup: pysolidfive

import math
import sys
import types
from collections.abc import Sequence
from typing import Any


class Tree:
    """A symbolic SDF sub-expression: callable as `tree(x, y, z) -> float`. Every operator
    returns a new Tree wrapping both operands' closures, mirroring how the real libfive Tree
    type builds an expression graph instead of evaluating eagerly."""

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, x, y, z):
        return self.fn(x, y, z)

    def _other(self, o):
        return o if isinstance(o, Tree) else Tree(lambda x, y, z: o)

    def __add__(self, o):
        o = self._other(o)
        return Tree(lambda x, y, z: self(x, y, z) + o(x, y, z))

    __radd__ = __add__

    def __sub__(self, o):
        o = self._other(o)
        return Tree(lambda x, y, z: self(x, y, z) - o(x, y, z))

    def __rsub__(self, o):
        o = self._other(o)
        return Tree(lambda x, y, z: o(x, y, z) - self(x, y, z))

    def __mul__(self, o):
        o = self._other(o)
        return Tree(lambda x, y, z: self(x, y, z) * o(x, y, z))

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = self._other(o)
        return Tree(lambda x, y, z: self(x, y, z) / o(x, y, z))

    def __neg__(self):
        return Tree(lambda x, y, z: -self(x, y, z))


def x():
    return Tree(lambda x, y, z: x)


def y():
    return Tree(lambda x, y, z: y)


def z():
    return Tree(lambda x, y, z: z)


def _as_tree(v):
    # Bind `v` as a default argument (`_v=v`) rather than closing over the loop/call-site
    # variable directly -- otherwise, if the caller later rebinds the same variable name
    # before this closure is ever invoked, the closure would see the *new* value (Python
    # closures capture variables, not values). Using a default argument freezes the value at
    # closure-creation time instead.
    return v if isinstance(v, Tree) else Tree(lambda x, y, z, _v=v: _v)


def _wrap1(f):
    def g(v):
        vt = _as_tree(v)
        return Tree(lambda x, y, z: f(vt(x, y, z)))
    return g


def _wrap2(f):
    def g(a, b):
        at = _as_tree(a)
        bt = _as_tree(b)
        return Tree(lambda x, y, z: f(at(x, y, z), bt(x, y, z)))
    return g


sqrt = _wrap1(math.sqrt)
square = _wrap1(lambda v: v * v)
abs = _wrap1(__import__("builtins").abs)  # noqa: A001
max = _wrap2(__import__("builtins").max)  # noqa: A001
min = _wrap2(__import__("builtins").min)  # noqa: A001
atan2 = _wrap2(math.atan2)


class _FrepResult:
    """Stand-in for the meshed solid frep() would return in the real app -- keeps the SDF
    closure and bounds so tests can .sample() it directly, plus a .translate() that composes
    an offset (so translate()/anchor= can be tested the same way a real solid would behave)."""

    def __init__(self, sdf, mn, mx, res):
        self.sdf = sdf
        self.mn = mn
        self.mx = mx
        self.res = res
        self.offset = [0.0, 0.0, 0.0]

    def translate(self, v):
        r = _FrepResult(self.sdf, self.mn, self.mx, self.res)
        r.offset = [self.offset[i] + v[i] for i in range(3)]
        return r

    def sample(self, px, py, pz):
        # Subtract the accumulated translate offset to get back into the SDF's own frame.
        return self.sdf(px - self.offset[0], py - self.offset[1], pz - self.offset[2])

    def mesh(self, triangulate=False, color=False):
        """Numeric stand-in for the real app's solid.mesh() -> (points, faces): samples the
        SDF on a regular grid over the bounds and returns the world-frame points that fall
        inside (sdf <= 0), with an empty faces list. Enough for vertex consumers like
        pysolidfive.hull(); anything needing real face topology needs the real app. The grid
        is capped at 16 cells per axis so pure-Python sampling of a deep SDF stays cheap."""
        # NOTE: this module shadows builtins max()/min() with Tree-returning wrappers above,
        # so clamp with plain conditionals here.
        n = int(self.res)
        n = 16 if n > 16 else (2 if n < 2 else n)
        points = []
        steps = [
            [self.mn[i] + (self.mx[i] - self.mn[i]) * k / n for k in range(n + 1)]
            for i in range(3)
        ]
        for px in steps[0]:
            for py in steps[1]:
                for pz in steps[2]:
                    if self.sdf(px, py, pz) <= 1e-9:
                        points.append([px + self.offset[0], py + self.offset[1], pz + self.offset[2]])
        return points, []


def frep(exp, mn, mx, res):
    return _FrepResult(exp, mn, mx, res)


# This module shadows the builtins min/max/abs with SDF-Tree-returning wrappers (above), so
# the AABB helpers below -- which need ordinary numeric min/max -- bind the real builtins.
import builtins as _bi

_bmin = _bi.min
_bmax = _bi.max


class _AabbSolid:
    """A tiny native-solid stand-in that tracks an axis-aligned bounding box through the
    transforms/booleans bosl2 uses, and exposes it as `.position`/`.size` -- the same native
    accessors PythonSCAD's real PyOpenSCAD provides. This lets bosl2's bbox-backed anchoring
    (Bosl2Solid.bounds()/anchor_point()/attach()/position()/align()) be unit-tested numerically
    without the real app. `mn`/`mx` are the AABB corners, or None for an unknown/2-D shape (its
    .position/.size then read None, matching the real API's empty-geometry sentinel).

    Every method or attribute not defined here is a permissive no-op returning self, so a box
    module can call anything (.color(), .linear_extrude(), .show(), ...) without the mock
    needing to model it -- only the AABB-affecting operations actually update the box."""

    def __init__(self, mn=None, mx=None):
        self.mn = list(mn) if mn is not None else None
        self.mx = list(mx) if mx is not None else None

    @property
    def position(self):
        return list(self.mn) if self.mn is not None else None

    @property
    def size(self):
        mn, mx = self.mn, self.mx
        if mn is None or mx is None:
            return None
        return [mx[i] - mn[i] for i in range(3)]

    def translate(self, v):
        mn, mx = self.mn, self.mx
        if mn is None or mx is None:
            return _AabbSolid()
        v = list(v) + [0.0] * (3 - len(v))
        return _AabbSolid([mn[i] + v[i] for i in range(3)], [mx[i] + v[i] for i in range(3)])

    def rotate(self, a, v=None):
        mn, mx = self.mn, self.mx
        if mn is None or mx is None:
            return _AabbSolid()
        m = _rot_matrix(a, v)
        corners = [
            [mn[0] if i & 1 == 0 else mx[0], mn[1] if i & 2 == 0 else mx[1], mn[2] if i & 4 == 0 else mx[2]]
            for i in range(8)
        ]
        rot = [[sum(m[r][k] * c[k] for k in range(3)) for r in range(3)] for c in corners]
        return _AabbSolid([_bmin(c[i] for c in rot) for i in range(3)], [_bmax(c[i] for c in rot) for i in range(3)])

    def _combine(self, other, mode):
        o = other if isinstance(other, _AabbSolid) else _AabbSolid()
        smn, smx, omn, omx = self.mn, self.mx, o.mn, o.mx
        if smn is None or smx is None:
            return _AabbSolid(o.mn, o.mx)
        if omn is None or omx is None or mode == "sub":
            return _AabbSolid(smn, smx)
        if mode == "or":
            return _AabbSolid([_bmin(smn[i], omn[i]) for i in range(3)], [_bmax(smx[i], omx[i]) for i in range(3)])
        return _AabbSolid([_bmax(smn[i], omn[i]) for i in range(3)], [_bmin(smx[i], omx[i]) for i in range(3)])

    def __or__(self, other):
        return self._combine(other, "or")

    def __and__(self, other):
        return self._combine(other, "and")

    def __sub__(self, other):
        return self._combine(other, "sub")

    def color(self, *a, **k):
        return _AabbSolid(self.mn, self.mx)

    def resize(self, newsize, auto=None, **k):
        # Modelled (rather than left to the permissive __getattr__) because the real
        # resize() REJECTS a 2-element vector with "TypeError: Invalid resize dimensions"
        # even for 2-D geometry -- a shape_type.py CLOUD bug that shipped precisely because
        # the mock accepted it silently. A 0 component means "leave that axis alone".
        if not isinstance(newsize, (list, tuple)) or len(newsize) != 3:
            raise TypeError("Invalid resize dimensions")
        mn, mx = self.mn, self.mx
        if mn is None or mx is None:
            return _AabbSolid()
        out_mn, out_mx = list(mn), list(mx)
        for i in range(3):
            want = float(newsize[i])
            if want > 0:
                out_mn[i] = mn[i]
                out_mx[i] = mn[i] + want
        return _AabbSolid(out_mn, out_mx)

    def multmatrix(self, m):
        # Shear (the only multmatrix bosl2 uses, for cyl/prism shift) doesn't grow the AABB
        # enough to matter for anchoring tests; keep the box as-is.
        return _AabbSolid(self.mn, self.mx)

    def separate(self):
        # Native separate() splits disconnected lumps; the mock has a single AABB, so it is one part.
        return [_AabbSolid(self.mn, self.mx)]

    def inside(self, point):
        # Model the real native inside() from the tracked AABB so Bosl2Solid.inside() is testable.
        mn, mx = self.mn, self.mx
        if mn is None or mx is None:
            return False
        return all(mn[i] <= float(point[i]) <= mx[i] for i in range(3))

    def __getattr__(self, name):
        # Permissive no-op for everything else (.show()/.mesh()/.linear_extrude()/...).
        return lambda *a, **k: self


def _rot_matrix(a, v=None):
    if v is None and isinstance(a, (list, tuple)):
        rx, ry, rz = (math.radians(x) for x in (list(a) + [0, 0, 0])[:3])
        cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
        mx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
        my = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
        mz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

        def mm(p, q):
            return [[sum(p[i][k] * q[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

        return mm(mz, mm(my, mx))
    ang = math.radians(a)
    ax = list(v) if v is not None else [0, 0, 1]
    n = math.sqrt(sum(x * x for x in ax)) or 1.0
    x, y, z = (c / n for c in ax)
    c, s, t = math.cos(ang), math.sin(ang), 1 - math.cos(ang)
    return [
        [t * x * x + c, t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ]


def _mock_cube(size: "float | Sequence[float]" = 1, center=None, dim=None, **k) -> Any:
    s = dim if dim is not None else size
    sv = [float(s)] * 3 if isinstance(s, (int, float)) else [float(x) for x in s]
    if center:
        return _AabbSolid([-sv[i] / 2 for i in range(3)], [sv[i] / 2 for i in range(3)])
    return _AabbSolid([0.0, 0.0, 0.0], sv)


def _mock_cylinder(h: float = 1, r=None, r1=None, r2=None, d=None, d1=None, d2=None, center=None, **k) -> Any:
    rr = [v for v in (r, r1, r2, (d / 2 if d else None), (d1 / 2 if d1 else None), (d2 / 2 if d2 else None)) if v is not None]
    rad = _bmax(rr) if rr else 1.0
    hh = float(h)
    z0, z1 = (-hh / 2, hh / 2) if center else (0.0, hh)
    return _AabbSolid([-rad, -rad, z0], [rad, rad, z1])


def _mock_sphere(r=None, d=None, **k) -> Any:
    rad = float(r) if r is not None else (float(d) / 2 if d is not None else 1.0)
    return _AabbSolid([-rad, -rad, -rad], [rad, rad, rad])


def _mock_polyhedron(points=None, *a, **k) -> Any:
    if not points:
        return _AabbSolid()
    pts = [[float(c) for c in p] for p in points]
    return _AabbSolid([_bmin(p[i] for p in pts) for i in range(3)], [_bmax(p[i] for p in pts) for i in range(3)])


def _mock_hull(*solids, **k) -> Any:
    pts: list[list[float]] = []
    for s in solids:
        if isinstance(s, _AabbSolid) and s.mn is not None and s.mx is not None:
            pts.append(list(s.mn))
            pts.append(list(s.mx))
    if not pts:
        return _AabbSolid()
    return _AabbSolid([_bmin(p[i] for p in pts) for i in range(3)], [_bmax(p[i] for p in pts) for i in range(3)])


def _mock_minkowski(*solids, **k) -> Any:
    mns: list[list[float]] = []
    mxs: list[list[float]] = []
    for s in solids:
        if isinstance(s, _AabbSolid) and s.mn is not None and s.mx is not None:
            mns.append(list(s.mn))
            mxs.append(list(s.mx))
    if not mns:
        return _AabbSolid()
    return _AabbSolid([sum(m[i] for m in mns) for i in range(3)], [sum(m[i] for m in mxs) for i in range(3)])


def install():
    """Patch sys.modules with mock `libfive`/`pythonscad`/`openscad` modules, so `import pysolidfive`
    (and its `bosl2.shapes2d`/`bosl2.shapes3d` imports) succeed without a real PythonSCAD app.
    Idempotent -- safe to call more than once (e.g. from multiple test modules)."""
    libfive_mock = types.ModuleType("libfive")
    for name in ["Tree", "x", "y", "z", "sqrt", "square", "abs", "max", "min", "atan2"]:
        setattr(libfive_mock, name, globals()[name])
    sys.modules["libfive"] = libfive_mock

    # pythonscad: frep() is real (routes to _FrepResult above). The 3-D primitives return an
    # _AabbSolid that tracks its bounding box (so bosl2's bbox-backed anchoring is numerically
    # testable); the 2-D/other builders return a permissive bbox-less _AabbSolid. pysolidfive
    # itself never calls any of these (it only builds SDFs and calls frep()).
    pythonscad_mock = types.ModuleType("pythonscad")
    setattr(pythonscad_mock, "frep", frep)
    setattr(pythonscad_mock, "cube", _mock_cube)
    setattr(pythonscad_mock, "cylinder", _mock_cylinder)
    setattr(pythonscad_mock, "sphere", _mock_sphere)
    setattr(pythonscad_mock, "polyhedron", _mock_polyhedron)
    setattr(pythonscad_mock, "hull", _mock_hull)
    setattr(pythonscad_mock, "minkowski", _mock_minkowski)
    for name in ["rotate_extrude", "textmetrics", "square", "circle", "polygon", "text", "osuse"]:
        setattr(pythonscad_mock, name, lambda *a, **k: _AabbSolid())
    sys.modules["pythonscad"] = pythonscad_mock

    # openscad: PyOpenSCAD needs to exist (bosl2/shapes3d.py imports the name for a type hint).
    # The geometry free functions imported by name (cap_box_polygon.py does
    # `from openscad import hull, polygon`) get the same AABB-aware stand-ins.
    openscad_mock = types.ModuleType("openscad")
    setattr(openscad_mock, "PyOpenSCAD", _AabbSolid)
    setattr(openscad_mock, "PyOpenSCADVector", list)
    setattr(openscad_mock, "cube", _mock_cube)
    setattr(openscad_mock, "cylinder", _mock_cylinder)
    setattr(openscad_mock, "sphere", _mock_sphere)
    setattr(openscad_mock, "hull", _mock_hull)
    for name in ["polygon", "square", "circle"]:
        setattr(openscad_mock, name, lambda *a, **k: _AabbSolid())
    sys.modules["openscad"] = openscad_mock


install()
