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
import os

import numpy as np

from enum import IntEnum
from dataclasses import dataclass
from typing import Any, TypeVar


_T = TypeVar("_T")

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401

# base_bgtk itself no longer calls into BOSL2 -- the path maths it used to need is now
# pybosl2/ (pure Python + numpy). BOSL2_STD_PATH is still exported for the modules that do
# still osuse() it. osuse() resolves a bare relative path against the process CWD
# (not the script dir), so when BOSL2_SCAD_DIR is set (the make build and the render tests both
# set it) load BOSL2 by absolute path -- that works from any CWD, including running an
# examples/ box from the repo root. BOSL2_STD_PATH is exported so every other toolkit module
# that also osuse()s BOSL2 resolves it the same way (they all `from base_bgtk import *` first).
_bosl2_dir = os.environ.get("BOSL2_SCAD_DIR")
BOSL2_STD_PATH = os.path.join(_bosl2_dir, "BOSL2", "std.scad") if _bosl2_dir else "BOSL2/std.scad"

# The numpy path maths (DifferenceWithOffset's pts= form); pybosl2/ never imports back here.
from pybosl2 import Path2D, Path3D, Region
from pybosl2 import shapes2d
from pybosl2.version import version as _pybosl2_version

# The toolkit needs pybosl2 >= 0.7.2 for its path fixes: Path2D/Path3D default to closed=False
# (so every outline meant as a polygon says closed=True), Path.tangents returns one tangent per
# POINT rather than per segment, and smooth_path/round_corners match real BOSL2.
#
# Checked here, at import, rather than left to the pyproject dependency pin, because that pin
# does not apply on the path that matters: inside the PythonSCAD app the toolkit imports
# whichever pybosl2 happens to be on sys.path, with no dependency resolution at all. And the
# 0.7.1 failure mode is SILENT -- box and tile outlines quietly lose their closing edge and
# lids round the wrong corners -- so without this the first symptom is a misprinted part.
_REQUIRED_PYBOSL2 = "0.7.2"
if _pybosl2_version < _REQUIRED_PYBOSL2:
    raise ImportError(
        f"openscad_boardgame_toolkit needs pybosl2 >= {_REQUIRED_PYBOSL2}, "
        f"found {_pybosl2_version}. Older versions default paths to closed=True and return "
        f"one tangent per segment, which silently changes box outlines and lid rounding."
    )


# ---------------------------------------------------------------------------
# Make-build parameters (the PythonSCAD analogue of the .scad `-D MAKE_MMU=... -D
# FROM_MAKE=...` the OpenSCAD Makefile passes).
# ---------------------------------------------------------------------------
#
# Declared via PythonSCAD's add_parameter() so they appear in the customizer, but the make
# build overrides them through the environment (e.g. `MAKE_MMU=1 FROM_MAKE=1 pythonscad ...`),
# which is how scripts/make_files.py drives them -- add_parameter's own -p/-P customizer-set
# override isn't wired for the CLI, and env vars are the one mechanism that reliably reaches a
# running script. Both fall back gracefully to the env/default when add_parameter isn't
# available (the numeric test mock, where `pythonscad` is a stand-in without it).
try:  # pragma: no cover - exercised only inside the real PythonSCAD app
    from pythonscad import add_parameter as _add_parameter
except ImportError:  # the numeric test mock has no add_parameter
    _add_parameter = None


def MakeParameter(name: str, default: int) -> int:
    """Declare an integer make/customizer parameter and return its effective value.

    The default is taken from the environment variable `name` when set (this is how the make
    build overrides it), otherwise `default`. When running inside PythonSCAD the value is also
    registered with add_parameter() so it shows up in the customizer; outside it (tests) the
    env/default is returned directly."""
    env = os.environ.get(name)
    base = int(env) if env is not None and env != "" else default
    if _add_parameter is not None:
        try:
            return int(_add_parameter(name, base))
        except Exception:
            return base
    return base


# MAKE_MMU: 1 also emits the positive_negative_children colour copies for multi-material (MMU)
# printing; 0 is a single-material print. FROM_MAKE: 1 when driven by the Makefile (the example
# scripts skip their own preview render then, the way the .scad `if (FROM_MAKE != 1)` guard does).
MAKE_MMU = MakeParameter("MAKE_MMU", 0)
FROM_MAKE = MakeParameter("FROM_MAKE", 0)


# ---------------------------------------------------------------------------
# Box-section markers for the make pipeline.
# ---------------------------------------------------------------------------
#
# A .py example file marks which of its functions produce a printable box (and which produce a
# documentation image) so scripts/make_files.py can generate exactly those build rules -- the
# .py analogue of the .scad `module Name() // `make` me` / `// `document` me` markers.
#
# `@make_box` / `@document_box` are the Pythonic, self-documenting way to mark a section: they
# are identity decorators (they return the function unchanged) that also tag it with an
# attribute, so a tool that IMPORTS the module can discover the sections too. make_files.py
# can't import a toolkit module (that needs the PythonSCAD app), so it scans the source
# statically -- it recognises the decorator OR the legacy `# `make` me` / `# `document` me`
# comment on the def line or the line right after it (which is where scripts/s2p.py emits it).


def make_box(fn):
    """Mark a zero-argument function as a printable box. scripts/make_files.py emits the mmu +
    single 3mf build rules for it. Put `@make_box` on the line above the `def`."""
    fn._bgtk_make = True
    return fn


def document_box(fn):
    """Mark a zero-argument function as producing a documentation image (a png, and a packing
    pdf entry) -- the .py analogue of the .scad `// `document` me` marker."""
    fn._bgtk_document = True
    return fn


m_piece_wiggle_room = 0.2  # Gap in mm used between joining pieces
default_lid_thickness = 2  # Default lid thickness
default_wall_thickness = 2  # Default wall thickness
default_floor_thickness = 2  # Default floor thickness
default_stackable_thickness = 1  # Thickness of the stackable section
default_print_in_place_offset = 0.25  # Offset when printing in place
default_slicing_layer_height = 0.2  # Layer height for slicing
default_hinge_hole_diameter = 1.75  # Hinge hole diameter
default_hinge_pin_slop = 0.2  # Extra diameter for hinge holes
default_hinge_thickness = 5  # Hinge thickness
default_voronoi_seed = 10000  # Seed for reproducible Voronoi

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

default_material_colour = "yellow"
default_label_colour = "black"
default_label_background_colour = "lime"
default_positive_colour = "black"

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


BOTTOM = Vec3([0, 0, -1])
TOP = Vec3([0, 0, 1])
FRONT = Vec3([0, -1, 0])
BACK = Vec3([0, 1, 0])
LEFT = Vec3([-1, 0, 0])
RIGHT = Vec3([1, 0, 0])
CENTER = Vec3([0, 0, 0])
BOT = BOTTOM  # alias
UP = TOP  # alias
DOWN = BOTTOM  # alias

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
default_label_font = "Stencil Std:style=Bold"
default_label_solid_background = False
default_label_type = LabelType.FRAMED

# ---------------------------------------------------------------------------
# Helper classes
# ---------------------------------------------------------------------------


@dataclass
class InnerSize:
    width: float
    length: float
    height: float
    # Optional polygon boundary of the usable interior, in the SAME local frame the
    # compartment layout packs into (0..width x 0..length). ``None`` means the interior
    # is the full width x length rectangle (the ordinary box). A path box passes its
    # inset outline here so :func:`compartments.layout_compartments` can drop cells that
    # fall outside the polygon -- binpacking that respects a non-rectangular outline.
    region: Any = None


@dataclass
class InnerPath:
    """What a path-box child is told about the inside of its box.

    This replaces the old positional contract
    ``callable(inner_path, inner_width, inner_length, inner_height)`` (the port of the SCAD
    ``$inner_path``/``$inner_*`` special variables) used by
    :func:`no_lid.MakePathBoxWithNoLid` and friends. Passing the *inner path* as a bare point
    list forced every box to compute an inset polygon up front even though nothing ever read it
    -- and point lists are the wrong currency for a child, which wants to build solids.

    So the inset outline is NOT precomputed. Ask for it through :attr:`profile`, a function
    pointer the box installs: ``inner.profile()`` hands back the inside as native 2-D geometry
    (ready to ``.linear_extrude()``/intersect), and ``inner.profile(inset)`` insets it further.
    Nothing is built unless a child actually calls it.

    Usage::

        def children(inner):
            # a tray floor that follows the box outline, 1mm clear of the wall
            return inner.profile(1).linear_extrude(height=2)

        MakePathBoxWithNoLid(path=..., height=20, children=children)

    Attributes:
        width:   bounding width of the inside
        length:  bounding length of the inside
        height:  usable height of the inside (box height minus the floor)
        path:    the box's own outline points (the OUTER path -- no offset needed to know it)
        profile: function pointer, ``profile(inset=0) -> native 2-D geometry`` of the inside
    """

    width: float
    length: float
    height: float
    path: Any
    profile: Any  # Callable[[float], PyOpenSCAD]; kept loose so the test mock can stand in


class ObjectType(IntEnum):
    """What an :class:`InnerObject` does to the box: carve a cavity, add material, or both."""

    NEGATIVE = 0
    POSITIVE = 1
    POSITIVE_NEGATIVE = 2


@dataclass
class InnerObject:
    # duck-typed: a solid, a pysolidfive shape, or (in tests) any stand-in object
    value: Any
    type: ObjectType = ObjectType.NEGATIVE
    color: str | None = None
    # When True (default) a NEGATIVE piece is clipped to the box interior so it can't
    # punch through the walls/floor. Set False for a deliberate breaching cut -- e.g. a
    # card finger hole that goes through the floor and up through the cards.
    clip: bool = True


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def native_points(path) -> list[list[float]]:
    """Coerce an outline to the plain ``[[x, y], ...]`` float pairs the native builtins want.

    The native ``polygon()``/``region()`` accept only plain Python lists of floats: a pybosl2
    ``Path2D``, a raw ndarray, or even a list of ``numpy.float64`` reaches the FFI as something
    it cannot parse, and the failure is ugly -- ``TypeError: Error during parsing
    polygon(points,paths)`` at best, ``SystemError: <built-in function polygon> returned a
    result with an exception set`` at worst, which leaves an exception set on the interpreter
    for whatever runs next. Anything that came out of the path maths goes through here first.

    Args:
        path: an outline -- a ``Path2D``, an ndarray, or any sequence of ``[x, y]`` pairs

    Returns:
        The same outline as plain lists of Python floats.
    """
    return [[float(p[0]), float(p[1])] for p in path]


def region(paths: list) -> PyOpenSCAD:
    """Turns BOSL2 region data (a list of [x, y] outlines, even-odd nesting for holes) into
    real 2-D geometry via the native polygon(points, paths=...) multi-path form -- PythonSCAD
    has no region() builtin of its own, but several tesselations.py/shapes.py constructions
    return raw region data from the real-BOSL2 region functions (union/difference/
    make_region/offset_stroke) and need rendering. Coordinates are forced to plain floats:
    region data that flowed through the pybosl2/ port's numpy-based path math otherwise reaches
    the FFI as numpy.float64, which the native side rejects.
    """
    # A single bare path is fine too.
    path_list = paths if isinstance(paths[0][0], (list, tuple)) or hasattr(paths[0][0], "__len__") else [paths]
    pts: list[list[float]] = []
    idx: list[list[int]] = []
    for path in path_list:
        base = len(pts)
        pts.extend([[float(p[0]), float(p[1])] for p in path])
        idx.append(list(range(base, base + len(path))))
    return polygon(pts, paths=idx)


def ResolveChild(c, inner_width: float, inner_length: float, inner_height: float):
    """Resolve a box-interior child entry.

    *c* may be a plain solid, or a callable(inner_width, inner_length,
    inner_height) for content that needs to know the box's interior size
    (replacing the SCAD $inner_width/$inner_length/$inner_height special
    variables, which have no Python equivalent).
    """
    resolved: Any = c(inner_width, inner_length, inner_height) if callable(c) else c
    return resolved


def DifferenceWithOffset(
    offset: float,
    outer_offset: float = 0,
    pts=None,
    children: PyOpenSCAD | None = None,
) -> Any:
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
            # The two offsets are CONCENTRIC, so the inner one is always strictly inside the
            # outer: the difference needs no polygon clipping, it is just "outline plus hole",
            # which is exactly how a BOSL2 region is represented. Verified against the real
            # BOSL2: difference(outer, inner) is literally [outer, inner], same winding
            # (tests/test_difference_with_offset.py).
            return Region.with_holes(Path2D(pts).offset(delta=outer_offset), Path2D(pts).offset(delta=offset))
        return Path2D(pts).offset(delta=outer_offset)

    assert children is not None, "DifferenceWithOffset: provide pts or children"
    if offset != 0:
        return children.offset(delta=outer_offset) - children.offset(delta=offset)
    return children.offset(delta=outer_offset)


def outline_shell(pts, thickness: float, outer_offset: float = 0):
    """An outline of *thickness* around *pts*, offset with the NATIVE 2-D offsetter.

    Same intent as :func:`DifferenceWithOffset`'s ``pts=`` form -- outline minus an inset
    copy -- but it survives detailed, concave outlines.

    This exists because ``Path2D.offset()`` used to move each vertex along its normal and
    keep the point count, so wherever the inset distance exceeded a local feature the result
    SELF-INTERSECTED: the flying-bird tile's 186-point outline was simple and every offset of
    it (even +0.2 outward) was not. That is invisible until something meshes it, and then
    every boolean against the tangled path is pathological -- tiling twenty of them did not
    finish in fifteen minutes.

    pybosl2 0.7 fixed that at the source: ``Path2D.offset()`` now drops the folded points, so
    the same tile offsets to 160/158/129 simple points at delta +0.2/-0.2/-0.5. Either route
    is therefore safe now, and this one is kept because the native offsetter clips rather
    than repairs and does it in one call.

    Prefer this for any outline with fine or concave detail (tesselation cells, creature
    profiles). ``DifferenceWithOffset(pts=...)`` remains the cheaper choice for simple,
    convex-ish paths -- it builds region DATA and does no clipping at all.

    Args:
        pts:          the closed outline
        thickness:    wall thickness (inset amount; the hole is inset by this much)
        outer_offset: extra outward offset applied to the outer ring first

    Returns:
        2-D geometry (native), ready to union/extrude.
    """
    # .shape drops to the native handle: the pybosl2 wrapper's offset() takes delta=/radius=
    # and routes back to the point-list offsetter this function exists to avoid, whereas the
    # native one takes r= and does real polygon clipping.
    solid = shapes2d.polygon([[float(p[0]), float(p[1])] for p in Path2D(pts).to_list]).shape
    if thickness == 0:
        return solid.offset(r=outer_offset)
    return solid.offset(r=outer_offset) - solid.offset(r=-abs(thickness))


def regular_ngon_path(sides: int, radius: float) -> list[list[float]]:
    """The vertices of a regular *sides*-gon on the circle of *radius*, BOSL2's winding.

    Four box types wanted this and all four reached into ``shapes2d._regular_ngon_path()``,
    a private pybosl2 helper -- which moved into a subpackage in 0.7 and took every polygon
    box down with it. With no rounding or chamfer that helper is exactly the circumcircle
    sampled at *sides* points from angle 0 (verified identical), so owning those three lines
    here is both shorter and immune to the next refactor.

    Args:
        sides:  number of sides (>= 3)
        radius: circumradius

    Returns:
        a closed path as a list of [x, y] points, first vertex on the +X axis
    """
    return [
        [radius * math.cos(math.radians(a)), radius * math.sin(math.radians(a))]
        for a in (360.0 * i / sides for i in range(sides))
    ]


def _offset_rounded(shape: PyOpenSCAD, amount: float) -> PyOpenSCAD:
    """Round-join offset that works on a pybosl2 2-D shape AND on a raw native one.

    The two spell it differently and neither accepts the other's keyword: pybosl2 takes
    ``radius=`` (its long-name convention), while the native builtin's signature is
    ``offset(object, r, delta)`` -- handing that one ``radius=`` raises "TypeError: Error
    during parsing offset(object,r,delta)". The delta-join sibling gets away with a single
    call because ``delta=`` happens to be spelled the same on both sides.

    Args:
        shape:  a pybosl2 ``Bosl2Shape2D`` or a native 2-D solid
        amount: offset distance (positive grows, negative shrinks)

    Returns:
        The offset shape, of whatever type went in.
    """
    return shape.offset(radius=amount) if isinstance(shape, shapes2d.Bosl2Shape2D) else shape.offset(r=amount)


def DifferenceWithOffsetRounded(
    offset: float,
    outer_offset: float = 0,
    pts: list[list[float]] | None = None,
    children: PyOpenSCAD | None = None,
) -> PyOpenSCAD:
    """Like :func:`DifferenceWithOffset` but using a rounded (r=) offset."""
    if pts is not None:
        if offset != 0:
            # Concentric, so no clipping -- see the note in DifferenceWithOffset().
            return Region.with_holes(Path2D(pts).offset(radius=outer_offset), Path2D(pts).offset(radius=offset))
        return Path2D(pts).offset(radius=outer_offset)

    assert children is not None, "DifferenceWithOffsetRounded: provide pts or children"
    if offset != 0:
        return _offset_rounded(children, outer_offset) - _offset_rounded(children, offset)
    return _offset_rounded(children, outer_offset)


def OffsetSweep(
    profile: PyOpenSCAD,
    height: float,
    rounding_bottom: float = 0.0,
    rounding_top: float = 0.0,
    steps: int = 8,
) -> Bosl2Solid:  # Path2D/Region.linear_extrude() returns a Bosl2Solid under pybosl2 0.6.5.
    """Direct-CSG (Manifold) stand-in for BOSL2's `offset_sweep(path, height=h,
    bottom=os_circle(rb), top=os_circle(rt))`: extrude a native 2-D `profile` from z=0 up to
    `height`, with each end rim optionally rounded over (positive radius, convex -- the rim
    pulls IN over that much height) or flared out (negative radius, a concave cove -- the rim
    pushes OUT, tangent to the wall), matching offset_sweep()'s os_circle sign convention.

    Each rim arc is approximated by `steps` stacked slices of the native offset() of the
    profile (rounded joins, r=), evaluated at the slice midpoints -- all Manifold-side CSG,
    replacing the interpreted-BOSL2 offset_sweep()+region pipeline that profiled at seconds
    per call (see FingerHoleWall()). At print scale the slice staircase on a couple-of-mm rim
    radius is sub-pixel in the golden renders; raise `steps` if a rim ever needs to be
    smoother.

    Unlike offset_sweep() this takes real 2-D geometry (native square()/circle()/polygon()
    composition), not a point-list region -- so callers build their profile with the fast
    native 2-D booleans instead of BOSL2's interpreted region math.

    Args:
        profile:         native 2-D geometry to sweep
        height:          total height of the sweep, END TREATMENTS INCLUDED (z=0..height)
        rounding_bottom: bottom-rim arc radius; >0 roundover, <0 flare, 0 square (default 0)
        rounding_top:    top-rim arc radius, same convention (default 0)
        steps:           offset() slices approximating each rim arc (default 8)
    """
    rb, rt = float(rounding_bottom), float(rounding_top)
    assert height > 0, f"OffsetSweep: height must be > 0, height={height}"
    assert abs(rb) + abs(rt) <= height + 1e-9, f"OffsetSweep: end treatments ({rb}, {rt}) don't fit in height {height}"
    z0 = rb if rb > 0 else 0.0
    z1 = height - (rt if rt > 0 else 0.0)
    pieces = [profile.linear_extrude(height=float(z1 - z0)).translate([0.0, 0.0, float(z0)])]

    def rim_slices(r: float, at_bottom: bool) -> None:
        a = abs(r)
        if a <= 0:
            return
        zs = np.linspace(0.0, a, steps + 1)
        mids = (zs[:-1] + zs[1:]) / 2
        if r > 0:
            # Convex roundover: full inset at the end face, tangent to the wall at depth r.
            offs = -(r - np.sqrt(np.maximum(0.0, r * r - (r - mids) ** 2)))
        else:
            # Concave flare: full outset at the end face, tangent to the wall at depth |r|.
            offs = np.sqrt(np.maximum(0.0, a * a - mids**2))
        for i in range(steps):
            off = float(offs[i])
            slab = profile.offset(radius=off) if abs(off) > 1e-12 else profile
            thickness = float(zs[i + 1] - zs[i]) + 1e-6
            z = float(zs[i]) if at_bottom else float(height - zs[i + 1])
            pieces.append(slab.linear_extrude(height=thickness).translate([0.0, 0.0, z]))

    rim_slices(rb, at_bottom=True)
    rim_slices(rt, at_bottom=False)
    result = pieces[0]
    for p in pieces[1:]:
        result = result | p
    return result


def stroke_path(pts, width: float, closed: bool = False):
    """A *width*-wide stroke along the polyline *pts* -- one rectangle per segment plus a
    disc at each interior join, unioned into 2-D geometry.

    The direct-CSG stand-in for BOSL2's ``stroke()``, which has no function form reachable
    from the port (and for the SDF ``stroke2d``, which forced whole modules to be SDF just
    to draw lines). Used by penrose_tiling and hilbert.

    Args:
        pts:    the polyline points
        width:  stroke width
        closed: also stroke the segment from the last point back to the first
    """
    pts = [[float(p[0]), float(p[1])] for p in pts]
    if closed and len(pts) > 2:
        pts = pts + [pts[0]]
    pieces = []
    for a, b in zip(pts, pts[1:]):
        length = math.dist(a, b)
        if length <= 1e-9:
            continue
        angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        pieces.append(
            shapes2d.square([length, width])
            .rotate(angle)
            .translate([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2])
        )
    for q in pts[1:-1]:
        pieces.append(shapes2d.circle(radius=width / 2).translate([q[0], q[1]]))
    return union_all_2d(pieces)


def union_all_2d(pieces: list):
    """Union *pieces* with a balanced tree -- ``a | b | c | ...`` over hundreds of pieces
    nests that many nodes deep, which the SDF backend cannot evaluate and the CSG one need
    not put up with."""
    pieces = [p for p in pieces if p is not None]
    if not pieces:
        return None
    while len(pieces) > 1:
        pieces = [
            pieces[i] | pieces[i + 1] if i + 1 < len(pieces) else pieces[i]
            for i in range(0, len(pieces), 2)
        ]
    return pieces[0]


def PolygonPrism(
    paths,
    h: float,
    rounding_top: float = 0.0,
    rounding_bottom: float = 0.0,
) -> PyOpenSCAD:
    """OffsetSweep() over a point-list polygon (or a list of disjoint island polygons,
    natively unioned): the direct-Manifold replacement for both the original real-BOSL2
    `vnf_polyhedron(offset_sweep(path, bottom=os_circle(b), top=os_circle(t)))` and the
    SDF-era pysolidfive.polygon_prism() -- same signature and radius sign convention as the
    latter (positive roundover, negative flare, sits on z=0).

    Args:
        paths:           one [[x, y], ...] polygon, or a list of disjoint such polygons
        h:               extrusion height (z from 0 to h), end treatments included
        rounding_top:    top-rim treatment: >0 roundover radius, <0 flare, 0 square (default 0)
        rounding_bottom: bottom-rim treatment, same convention (default 0)
    """
    first = np.asarray(paths[0], dtype=float)
    path_list = [paths] if first.ndim == 1 else list(paths)
    shape2d = None
    for p in path_list:
        # pybosl2 shapes2d.polygon (a Bosl2Shape2D) so OffsetSweep's .offset(radius=)/
        # .linear_extrude(height=) resolve to the pybosl2 methods, matching every other
        # OffsetSweep caller (a native polygon() would need .offset(r=) instead and break).
        poly = shapes2d.polygon([[float(x), float(y)] for x, y in np.asarray(p, dtype=float)])
        shape2d = poly if shape2d is None else shape2d | poly
    assert shape2d is not None, "PolygonPrism: paths must not be empty"
    return OffsetSweep(
        shape2d, height=float(h), rounding_bottom=float(rounding_bottom), rounding_top=float(rounding_top)
    )
