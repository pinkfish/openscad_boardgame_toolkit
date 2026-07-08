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

# LibFile: base_bgtk.py
#    Base constants, utilities and helper functions for the board game toolkit.
#
# FileSummary: Basic pieces of the board game insert system.
# FileGroup: Basics

from __future__ import annotations
import math

from enum import IntEnum
from dataclasses import dataclass
from typing import TypeVar


_T = TypeVar("_T")

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401

# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse("BOSL2/std.scad")

# ---------------------------------------------------------------------------
# Tolerances & defaults
# ---------------------------------------------------------------------------

MAKE_MMU = 0  # Set to 1 to also render the positive_negative_children copies for multi-material printing
m_piece_wiggle_room       = 0.2   # Gap in mm used between joining pieces
default_lid_thickness     = 2     # Default lid thickness
default_wall_thickness    = 2     # Default wall thickness
default_floor_thickness   = 2     # Default floor thickness
default_stackable_thickness = 1   # Thickness of the stackable section
default_print_in_place_offset = 0.25  # Offset when printing in place
default_slicing_layer_height  = 0.2   # Layer height for slicing
default_hinge_hole_diameter   = 1.75  # Hinge hole diameter
default_hinge_pin_slop        = 0.2   # Extra diameter for hinge holes
default_hinge_thickness       = 5     # Hinge thickness
default_voronoi_seed          = 10000 # Seed for reproducible Voronoi

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

default_material_colour          = "yellow"
default_label_colour             = "black"
default_label_background_colour  = "lime"
default_positive_colour          = "black"

# ---------------------------------------------------------------------------
# BOSL2-style anchor / direction vectors
# ---------------------------------------------------------------------------


class Vec3(list):
    """A 3-element list that supports elementwise +/-/* like a vector.

    Plain Python lists use `+` for concatenation and `*` for repetition, but
    BOSL2-style code combines direction constants with idioms like
    `anchor=TOP+LEFT` expecting elementwise vector addition (`[0,0,1]+[-1,0,0]`
    -> `[-1,0,1]`), not concatenation. Subclassing `list` (rather than using a
    plain tuple or a numpy array) keeps every other list behavior -- indexing,
    iteration, equality with plain lists, and crossing the osuse()/PyOpenSCAD
    FFI boundary -- unchanged.
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


BOTTOM  = Vec3([0,  0, -1])
TOP     = Vec3([0,  0,  1])
FRONT   = Vec3([0, -1,  0])
BACK    = Vec3([0,  1,  0])
LEFT    = Vec3([-1, 0,  0])
RIGHT   = Vec3([1,  0,  0])
CENTER  = Vec3([0,  0,  0])
BOT     = BOTTOM     # alias
UP      = TOP        # alias
DOWN    = BOTTOM     # alias

# ---------------------------------------------------------------------------
# Shape-type constants
# ---------------------------------------------------------------------------


class ShapeType(IntEnum):
    DENSE_HEX = 1
    DENSE_TRIANGLE = 2
    CIRCLE = 3
    HEX = 4
    OCTOGON = 5
    TRIANGLE = 6
    NONE = 7
    SQUARE = 8
    SUPERSHAPE = 9
    HILBERT = 10
    CLOUD = 11
    PENTAGON_R1 = 12
    PENTAGON_R2 = 13
    PENTAGON_R3 = 14
    PENTAGON_R4 = 15
    PENTAGON_R5 = 16
    PENTAGON_R6 = 17
    PENTAGON_R7 = 18
    PENTAGON_R8 = 19
    PENTAGON_R9 = 20
    PENTAGON_R10 = 21
    PENTAGON_R11 = 22
    PENTAGON_R12 = 23
    PENTAGON_R13 = 24
    PENTAGON_R14 = 25
    PENTAGON_R15 = 26
    LIZARD = 27
    VORONOI = 28
    LEAF = 29
    LEAF_VEINS = 30
    DROP = 31
    DELTOID_TRIHEXAGONAL = 32
    DELTOID_TRIHEXAGONAL_KITE = 33
    HALF_REGULAR_HEXAGON = 34
    RHOMBI_TRI_HEXAGONAL = 35
    PENROSE_TILING_5 = 36
    PENROSE_TILING_7 = 37
    PEGASUS = 38
    GOOSE = 39
    CHICKEN = 40
    SHEEP = 41
    BIRD = 42
    FLYING_BIRD = 43


# ---------------------------------------------------------------------------
# Catch-type constants
# ---------------------------------------------------------------------------


class CatchType(IntEnum):
    NONE = 0
    SHORT = 1
    LONG = 2
    ALL = 3
    BUMPS_SHORT = 4
    BUMPS_LONG = 5

# ---------------------------------------------------------------------------
# Label-type constants
# ---------------------------------------------------------------------------

class LabelType(IntEnum):
    FRAMED = 0
    FRAMED_SOLID = 1
    FRAMED_SHORT = 2
    FRAMED_SHORT_SOLID = 3
    FRAMELESS_ANGLE = 4
    FRAMELESS = 5
    FRAMELESS_SHORT = 6

# Label defaults
default_label_font             = "Stencil Std:style=Bold"
default_label_solid_background = False
default_label_type             = LabelType.FRAMED

# ---------------------------------------------------------------------------
# Helper classes
# ---------------------------------------------------------------------------

@dataclass
class InnerSize:
    width: float
    length: float
    height: float

class ObjectType(IntEnum):
    NEGATIVE = 0
    POSTIVE = 1
    POSTIVE_NEGATIVE = 2

@dataclass
class InnerObject:
    value: PyOpenSCAD
    type: ObjectType = ObjectType.NEGATIVE
    color: str | None = None

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def ResolveChild(
    c: PyOpenSCAD, inner_width: float, inner_length: float, inner_height: float
) -> PyOpenSCAD:
    """Resolve a box-interior child entry.

    *c* may be a plain solid, or a callable(inner_width, inner_length,
    inner_height) for content that needs to know the box's interior size
    (replacing the SCAD $inner_width/$inner_length/$inner_height special
    variables, which have no Python equivalent).
    """
    return c(inner_width, inner_length, inner_height) if callable(c) else c


def DifferenceWithOffset(
    offset: float,
    outer_offset: float = 0,
    pts: list[list[float]] | None = None,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Offsets a shape and (if offset != 0) cuts out a smaller offset copy.

    Used to turn a solid 2-D shape/path into an outline of a given
    thickness. Pass *pts* for the path/region-data form (returns raw region
    data), or *children* for the CSG-object form (returns a 2-D solid).

    Args:
        offset:       inner offset (-ve shrinks); 0 means "solid, no cutout"
        outer_offset: outer offset applied first (default 0)
        pts:          raw 2-D path/region data (function form)
        children:     a 2-D CSG solid (module form)
    """
    if pts is not None:
        if offset != 0:
            return _bosl2.difference(_bosl2.offset(pts, delta=outer_offset), _bosl2.offset(pts, delta=offset))
        return _bosl2.offset(pts, delta=outer_offset)

    assert children is not None, "DifferenceWithOffset: provide pts or children"
    if offset != 0:
        return children.offset(delta=outer_offset) - children.offset(delta=offset)
    return children.offset(delta=outer_offset)


def DifferenceWithOffsetRounded(
    offset: float,
    outer_offset: float = 0,
    pts: list[list[float]] | None = None,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Like :func:`DifferenceWithOffset` but using a rounded (r=) offset."""
    if pts is not None:
        if offset != 0:
            return _bosl2.difference(_bosl2.offset(pts, r=outer_offset), _bosl2.offset(pts, r=offset))
        return _bosl2.offset(pts, r=outer_offset)

    assert children is not None, "DifferenceWithOffsetRounded: provide pts or children"
    if offset != 0:
        return children.offset(r=outer_offset) - children.offset(r=offset)
    return children.offset(r=outer_offset)
