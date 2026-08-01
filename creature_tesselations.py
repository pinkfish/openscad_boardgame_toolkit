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

# LibFile: creature_tesselations.py
#    Escher-style figurative tilings: lizard, goose, chicken, sheep, bird, flying bird.
#
#    ORIGIN OF THESE SHAPES: ShapeType has offered LIZARD / GOOSE / CHICKEN / SHEEP / BIRD /
#    FLYING_BIRD since the port began, and shape_type.scad called
#    LizardRepeatAtLocation() / TesselationGooseArea() / ... -- but those modules were never
#    written, in either language, and are in neither the repo nor its history. So the
#    OUTLINES BELOW ARE NEWLY AUTHORED, not ports of an original. They are honest
#    tessellations (they interlock and fill the plane) with silhouettes suggesting each
#    animal; if you have the artwork you intended, swapping it in means replacing one
#    profile list per creature and nothing else.
#
#    HOW A FIGURATIVE TILING WORKS: take a polygon that tiles on its own (a square or a
#    hexagon) and distort its edges. As long as each edge is paired with the edge it meets
#    in the neighbouring tile -- which is what square_tesselation (2 profiles, opposite
#    sides) and hexagonal_tesselation (3 profiles, opposite sides) guarantee -- the outline
#    can wander as much as you like and the tiles still interlock with no gaps. The animal
#    is entirely in the choice of profile; the tiling is free.
#
#    Each profile runs from x = -0.5 to x = +0.5 in units of the edge length, with y the
#    excursion sideways. The lattice does the placing (see patterns.py).
#
# FileSummary: Figurative (animal) tessellations.
# FileGroup: Shapes

from __future__ import annotations

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401

from base_bgtk import region
from pybosl2.regions import Path
from tesselations import hexagonal_tesselation, square_tesselation

# ---------------------------------------------------------------------------
# Edge profiles -- the artwork. Each runs -0.5 .. +0.5 along the edge.
# ---------------------------------------------------------------------------

#: Long neck arching out, matched by the hollow a neighbour's body sits into.
_GOOSE_NECK = [[-0.5, 0], [-0.32, 0.16], [-0.12, 0.3], [0.06, 0.28], [0.16, 0.12], [0.3, 0.05], [0.5, 0]]
#: Tail and back: a shallow rise with a notch where the wing folds.
_GOOSE_BACK = [[-0.5, 0], [-0.3, -0.12], [-0.08, -0.06], [0.04, -0.22], [0.24, -0.16], [0.38, -0.04], [0.5, 0]]

#: Plump breast with a beak bump at the front.
_CHICKEN_BREAST = [[-0.5, 0], [-0.34, 0.2], [-0.1, 0.26], [0.08, 0.14], [0.2, 0.22], [0.36, 0.1], [0.5, 0]]
#: Tail feathers -- three short spikes.
_CHICKEN_TAIL = [[-0.5, 0], [-0.36, -0.14], [-0.22, -0.04], [-0.06, -0.18], [0.12, -0.06], [0.3, -0.16], [0.5, 0]]
#: Underside: legs tucked, a shallow scallop.
_CHICKEN_UNDER = [[-0.5, 0], [-0.28, 0.08], [-0.04, 0.02], [0.18, 0.1], [0.36, 0.03], [0.5, 0]]

#: Fleece: a run of small bumps.
_SHEEP_FLEECE = [[-0.5, 0], [-0.4, 0.14], [-0.26, 0.04], [-0.12, 0.18], [0.02, 0.06], [0.16, 0.2], [0.3, 0.08],
                 [0.42, 0.16], [0.5, 0]]
#: Head end: a blunt muzzle.
_SHEEP_HEAD = [[-0.5, 0], [-0.3, -0.16], [-0.06, -0.2], [0.14, -0.1], [0.34, -0.14], [0.5, 0]]
#: Legs: two short stubs.
_SHEEP_LEGS = [[-0.5, 0], [-0.34, 0.12], [-0.24, 0.02], [0.06, 0.02], [0.16, 0.14], [0.32, 0.04], [0.5, 0]]

#: A swept wing, leading edge.
_BIRD_WING = [[-0.5, 0], [-0.3, 0.22], [-0.04, 0.3], [0.16, 0.18], [0.34, 0.2], [0.5, 0]]
#: Body and tail, trailing edge -- the hollow the next bird's wing drops into.
_BIRD_BODY = [[-0.5, 0], [-0.32, -0.2], [-0.12, -0.14], [0.06, -0.26], [0.28, -0.18], [0.4, -0.06], [0.5, 0]]

#: Wings spread wide, for the hex (six-way) tiling.
_FLYING_WING = [[-0.5, 0], [-0.34, 0.26], [-0.1, 0.34], [0.1, 0.24], [0.32, 0.28], [0.5, 0]]
#: Head and beak.
_FLYING_HEAD = [[-0.5, 0], [-0.28, -0.1], [-0.06, -0.26], [0.12, -0.12], [0.34, -0.16], [0.5, 0]]
#: Forked tail.
_FLYING_TAIL = [[-0.5, 0], [-0.3, 0.12], [-0.14, -0.02], [0.04, 0.16], [0.22, 0.0], [0.38, 0.12], [0.5, 0]]

#: Lizard: front legs reaching out (the classic Escher lizard is a hexagon tiling, where
#: each of the three profile pairs carries one feature -- legs, tail, head).
_LIZARD_FORELEG = [[-0.5, 0], [-0.36, 0.18], [-0.18, 0.1], [-0.06, 0.28], [0.1, 0.16], [0.3, 0.2], [0.5, 0]]
#: Hind legs and the curl of the tail.
_LIZARD_HIND = [[-0.5, 0], [-0.3, -0.22], [-0.1, -0.1], [0.08, -0.28], [0.26, -0.12], [0.4, -0.2], [0.5, 0]]
#: Head, snout forward.
_LIZARD_HEAD = [[-0.5, 0], [-0.32, 0.14], [-0.12, 0.24], [0.08, 0.12], [0.28, 0.18], [0.5, 0]]


# ---------------------------------------------------------------------------
# The creatures. Each returns ONE tile outline; the lattice tiles it.
# ---------------------------------------------------------------------------


def _square_creature(profiles, size: float, thickness: float, outer_offset: float) -> "PyOpenSCAD":
    """One square-lattice tile from two edge profiles."""
    return region(
        square_tesselation(
            points=profiles, size=[size, size], thickness=thickness, outer_offset=outer_offset
        )
    )


def _hex_creature(profiles, size: float, thickness: float) -> "PyOpenSCAD":
    """One hex-lattice tile from three edge profiles, drawn as an OUTLINE.

    hexagonal_tesselation() hands back the filled outline; a lid wants the creature drawn
    as a wall, so the tile is the outline minus itself inset by *thickness*. Those two are
    concentric, so the pair IS the region -- outline plus hole -- and needs no clipping
    (the same reasoning as square_tesselation)."""
    outline = hexagonal_tesselation(points=profiles, radius=size / 2)
    if thickness <= 0:
        return region(outline)
    inner = Path._deduplicate(Path(outline).offset(delta=-thickness, chamfer=True), closed=True)
    outline = outline.to_list if hasattr(outline, "to_list") else list(outline)
    return region([outline, inner])


def goose2d(size: float = 20, thickness: float = 1, outer_offset: float = 0.1) -> "PyOpenSCAD":
    """A goose tile: neck reaching forward into the hollow of the bird ahead.

    Square lattice. Usage::

        goose2d(size=20, thickness=1)
    """
    return _square_creature([_GOOSE_NECK, _GOOSE_BACK], size, thickness, outer_offset)


def bird2d(size: float = 20, thickness: float = 1, outer_offset: float = 0.1) -> "PyOpenSCAD":
    """A bird tile, wings swept back. Square lattice."""
    return _square_creature([_BIRD_WING, _BIRD_BODY], size, thickness, outer_offset)


def chicken2d(size: float = 20, thickness: float = 1) -> "PyOpenSCAD":
    """A chicken tile: breast, tail feathers and tucked legs. Hex lattice."""
    return _hex_creature([_CHICKEN_BREAST, _CHICKEN_TAIL, _CHICKEN_UNDER], size, thickness)


def sheep2d(size: float = 20, thickness: float = 1) -> "PyOpenSCAD":
    """A sheep tile: bumpy fleece over a blunt muzzle and stub legs. Hex lattice."""
    return _hex_creature([_SHEEP_FLEECE, _SHEEP_HEAD, _SHEEP_LEGS], size, thickness)


def flying_bird2d(size: float = 20, thickness: float = 1) -> "PyOpenSCAD":
    """A flying bird tile: wings spread, forked tail. Hex lattice."""
    return _hex_creature([_FLYING_WING, _FLYING_HEAD, _FLYING_TAIL], size, thickness)


def lizard2d(size: float = 20, thickness: float = 1) -> "PyOpenSCAD":
    """A lizard tile: fore and hind legs interlocking with its neighbours. Hex lattice."""
    return _hex_creature([_LIZARD_FORELEG, _LIZARD_HIND, _LIZARD_HEAD], size, thickness)
