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

# LibFile: bosl2/constants.py
#    Every constant defined in BOSL2's constants.scad, laid out in the same
#    sections as the original .scad file, so the bosl2/ package doesn't need
#    to borrow anchor/direction vectors from base_bgtk.py.
#
# FileSummary: Constants provided by BOSL2 (BOSL2 constants.scad).
# FileGroup: BOSL2

# ---------------------------------------------------------------------------
# Section: General Constants
# ---------------------------------------------------------------------------

# The number of millimeters in an inch.
INCH: float = 25.4

# Identity transformation matrix for three-dimensional transforms. Equal to `ident(4)`.
IDENT: list[list[float]] = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]

# ---------------------------------------------------------------------------
# Section: Directional Vectors
#   Vectors useful for rotate(), mirror(), and anchor arguments for
#   cuboid(), cyl(), etc.
# ---------------------------------------------------------------------------


class Vec3(list):
    """A 3-element list that supports elementwise +/-/* like a vector.

    Plain Python lists use `+` for concatenation and `*` for repetition, but
    BOSL2-style code combines direction constants with idioms like
    `anchor=TOP+LEFT` expecting elementwise vector addition (`[0,0,1]+[-1,0,0]`
    -> `[-1,0,1]`), not concatenation. Subclassing `list` (rather than using a
    plain tuple or a numpy array) keeps every other list behavior -- indexing,
    iteration, equality with plain lists, and crossing the osuse()/PyOpenSCAD
    FFI boundary -- unchanged. (Duplicated from base_bgtk.py's Vec3 rather than
    imported, since this package is deliberately independent of base_bgtk.py.)
    """

    def __add__(self, other):
        return Vec3(a + b for a, b in zip(self, other))

    def __radd__(self, other):
        return Vec3(a + b for a, b in zip(other, self))

    def __sub__(self, other):
        return Vec3(a - b for a, b in zip(self, other))

    def __rsub__(self, other):
        return Vec3(a - b for a, b in zip(other, self))

    def __neg__(self):
        return Vec3(-a for a in self)

    def __mul__(self, other: float) -> "Vec3":  # type: ignore[override]
        return Vec3(a * other for a in self)

    __rmul__ = __mul__  # type: ignore[assignment]


LEFT: Vec3 = Vec3([-1, 0, 0])
RIGHT: Vec3 = Vec3([1, 0, 0])

FRONT: Vec3 = Vec3([0, -1, 0])
FWD: Vec3 = FRONT
FORWARD: Vec3 = FRONT

BACK: Vec3 = Vec3([0, 1, 0])

BOTTOM: Vec3 = Vec3([0, 0, -1])
BOT: Vec3 = BOTTOM
DOWN: Vec3 = BOTTOM

TOP: Vec3 = Vec3([0, 0, 1])
UP: Vec3 = TOP

CENTER: Vec3 = Vec3([0, 0, 0])
CTR: Vec3 = CENTER
CENTRE: Vec3 = CENTER

# ---------------------------------------------------------------------------
# Section: Line specifiers
#   Used by geometry functions for specifying whether two points are
#   treated as an unbounded line, a ray with one endpoint, or a segment
#   with two endpoints.
# ---------------------------------------------------------------------------

# Treat a line as a segment.
SEGMENT: list[bool] = [True, True]

# Treat a line as a ray, based at the first point.
RAY: list[bool] = [True, False]

# Treat a line as an unbounded line.
LINE: list[bool] = [False, False]
