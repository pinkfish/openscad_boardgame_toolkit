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
#    `pythonscad`/`openscad` for pysolidfive to load -- pysolidfive itself has no bosl2/numpy
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


def frep(exp, mn, mx, res):
    return _FrepResult(exp, mn, mx, res)


def install():
    """Patch sys.modules with mock `libfive`/`pythonscad`/`openscad` modules, so `import pysolidfive`
    (and its `bosl2.shapes2d`/`bosl2.shapes3d` imports) succeed without a real PythonSCAD app.
    Idempotent -- safe to call more than once (e.g. from multiple test modules)."""
    libfive_mock = types.ModuleType("libfive")
    for name in ["Tree", "x", "y", "z", "sqrt", "square", "abs", "max", "min"]:
        setattr(libfive_mock, name, globals()[name])
    sys.modules["libfive"] = libfive_mock

    # pythonscad: frep() is real (routes to _FrepResult above); everything else
    # (cube/cylinder/.../osuse) is a harmless no-op, needed only so that
    # `from pythonscad import (...)` in bosl2/shapes2d.py and bosl2/shapes3d.py resolves at
    # import time -- pysolidfive never actually calls any of them (it only builds SDFs and calls
    # frep()), so their exact behavior doesn't matter here.
    pythonscad_mock = types.ModuleType("pythonscad")
    setattr(pythonscad_mock, "frep", frep)
    for name in [
        "cube", "cylinder", "sphere", "polyhedron", "hull", "minkowski", "rotate_extrude",
        "textmetrics", "square", "circle", "polygon", "text", "osuse",
    ]:
        setattr(pythonscad_mock, name, lambda *a, **k: None)
    sys.modules["pythonscad"] = pythonscad_mock

    # openscad: only PyOpenSCAD needs to exist (bosl2/shapes3d.py imports the name for a type
    # hint), it's never instantiated in these tests.
    openscad_mock = types.ModuleType("openscad")

    class PyOpenSCAD:
        pass

    setattr(openscad_mock, "PyOpenSCAD", PyOpenSCAD)
    sys.modules["openscad"] = openscad_mock


install()
