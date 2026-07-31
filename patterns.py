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

# LibFile: patterns.py
#    Filling a region with a repeating pattern -- the lid pattern system.
#
#    ONE contract: a :class:`Pattern` fills a :class:`PatternArea`. Everything a pattern
#    needs to know (how big the region is, what outline it has) arrives in that area, so a
#    pattern works on a lid, a compartment floor or anything else without knowing what it
#    is decorating, and the caller never has to discover which "mode" a pattern wants.
#
#    That replaces the ``inner_control`` scheme, where one grid function owned the loop and
#    the shape had to cooperate through a 0/1/2 flag looked up in a side table
#    (``ShapeNeedsInnerControl``) that the lid pipeline never threaded through. Three
#    genuinely different kinds of pattern were wearing one interface:
#
#      * ``TiledPattern``  -- a motif drawn once per lattice cell (the lattice places it)
#      * ``TilingPattern`` -- a tile that places ITSELF from its cell index (pentagon
#                             tilings, leaf, lizard: the figure changes cell to cell)
#      * ``AreaPattern``   -- no cells at all; fills the whole region in one shot (Voronoi,
#                             Penrose)
#
#    Now each is a class with its own ``fill(area)``, so the difference lives in the pattern
#    instead of in a flag the caller has to know to pass.
#
# FileSummary: Region-filling patterns for lids.
# FileGroup: Shapes

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from base_bgtk import ShapeType
from components import RegularPolygonGrid, RegularPolygonGridDense
from shape_type import ShapeByType, ShapeObject

# ---------------------------------------------------------------------------
# The region a pattern fills
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PatternArea:
    """The region a :class:`Pattern` fills, in the region's own local frame.

    The frame is CORNER-anchored: ``(0, 0)`` to ``(width, length)``. A pattern may (and
    usually does) produce geometry that overruns the area -- the caller clips it, so a
    pattern never has to know about the outline it will be trimmed to.

    Attributes:
        width/length: bounding size of the region
        path:         the real outline, when it isn't the ``width`` x ``length`` rectangle
                      (a polygon lid). Patterns that fill by area may use it; tiled ones
                      ignore it and let the caller clip.
    """

    width: float
    length: float
    path: Any = None

    def outline(self) -> list[list[float]]:
        """The area's outline as a point list -- the explicit ``path`` or the rectangle."""
        if self.path is not None:
            return [[float(p[0]), float(p[1])] for p in self.path]
        return [[0, 0], [self.width, 0], [self.width, self.length], [0, self.length]]


@dataclass(frozen=True)
class Cell:
    """One lattice cell: where it is in the grid, and how big the grid is.

    A self-placing tile (see :class:`TilingPattern`) gets this and works out its own
    position from it -- some tilings index from the grid CENTRE (the pentagon family) and
    some from the corner (leaf, half-hexagon), which is why the index is handed over
    rather than the coordinates."""

    i: int
    j: int
    rows: int
    cols: int


# ---------------------------------------------------------------------------
# Lattices -- where the cells are
# ---------------------------------------------------------------------------


class Lattice(ABC):
    """The geometry of a repeating grid: how many cells cover an area, and where they go.

    Two ways to use one: :meth:`tile` stamps a motif at every cell (the lattice does the
    placing), and :meth:`cells` just enumerates the cells for a tile that places itself."""

    #: Extra rings of cells enumerated for a self-placing tiling, so tiles that overhang
    #: their nominal cell still reach the edges. Small on purpose: cost is quadratic in it
    #: (a 120x80 lid at +11 is 437 cells instead of 154, and each cell of a pentagon tiling
    #: is real geometry). The original ``+11`` was compensating for centre-indexed tilings
    #: being left around the origin instead of moved onto the area -- which
    #: :class:`TilingPattern` now does, so the margin only has to cover overhang.
    self_placing_margin: int = 2

    @abstractmethod
    def counts(self, area: PatternArea) -> tuple[float, float]:
        """``(rows, cols)`` needed to cover *area*."""

    @abstractmethod
    def tile(self, motif, area: PatternArea):
        """Stamp *motif* at every cell covering *area*."""

    def cells(self, area: PatternArea) -> Iterator[Cell]:
        """Enumerate the cells covering *area*, widened by :attr:`self_placing_margin`."""
        rows, cols = self.counts(area)
        rows, cols = int(rows) + self.self_placing_margin, int(cols) + self.self_placing_margin
        for i in range(rows):
            for j in range(cols):
                yield Cell(i=i, j=j, rows=rows, cols=cols)


@dataclass(frozen=True)
class DenseLattice(Lattice):
    """A space-filling hexagon or triangle lattice -- cells share edges, no gaps."""

    width: float          # across-flats size of one cell
    edges: int = 6        # 6 = hexagons, 3 = triangles

    @property
    def radius(self) -> float:
        return self.width / 2

    def counts(self, area: PatternArea) -> tuple[float, float]:
        cell_width = math.cos(math.radians(180 / self.edges)) * self.radius
        return area.width / cell_width + 2, area.length / cell_width + 2

    def tile(self, motif, area: PatternArea):
        rows, cols = self.counts(area)
        return RegularPolygonGridDense(
            radius=self.radius, rows=rows, cols=cols, shape_edges=self.edges,
            inner_control=False, children=motif,
        )


@dataclass(frozen=True)
class GridLattice(Lattice):
    """A plain repeating grid -- one motif per cell, spaced ``width`` apart."""

    width: float
    edges: int = 4
    aspect_ratio: float = 1.0
    spacing: float = 0.0

    def counts(self, area: PatternArea) -> tuple[float, float]:
        return (
            area.width / self.width + 2,
            area.length / self.width * self.aspect_ratio + 2,
        )

    def tile(self, motif, area: PatternArea):
        rows, cols = self.counts(area)
        return RegularPolygonGrid(
            width=self.width, rows=rows + 1, cols=cols + 1, spacing=self.spacing,
            shape_edges=self.edges, aspect_ratio=self.aspect_ratio, inner_control=0,
            space_width=area.width, space_length=area.length, children=motif,
        )


# ---------------------------------------------------------------------------
# Patterns -- the one contract
# ---------------------------------------------------------------------------


def union_all(pieces: list):
    """Union *pieces* without building a chain as deep as the list is long.

    A tiling is hundreds of cells, and ``a | b | c | ...`` nests that many nodes deep. For
    the SDF backend that overflows the interpreter stack when the shape is evaluated (the
    same trap ``penrose_tiling`` documents), so use its n-ary union where there is one and
    a balanced pairwise tree otherwise -- ``log2(n)`` deep instead of ``n``."""
    pieces = [p for p in pieces if p is not None]
    if not pieces:
        return None
    if len(pieces) == 1:
        return pieces[0]
    n_ary = getattr(type(pieces[0]), "union2d", None)
    if n_ary is not None:
        return n_ary(pieces)
    while len(pieces) > 1:
        pieces = [
            pieces[i] | pieces[i + 1] if i + 1 < len(pieces) else pieces[i]
            for i in range(0, len(pieces), 2)
        ]
    return pieces[0]


class Pattern(ABC):
    """Something that can fill a region with 2-D geometry.

    ``fill(area) -> 2-D shape | None`` is the entire contract. A pattern returns geometry
    covering AT LEAST the area (overrun is expected and normal); clipping to the real
    outline is the caller's job, so the same pattern works on a rectangular lid, a hexagon
    lid or anything else."""

    @abstractmethod
    def fill(self, area: PatternArea):
        """The 2-D geometry filling *area*, or ``None`` for no pattern."""


class NoPattern(Pattern):
    """The empty pattern -- a lid with no tiled decoration."""

    def fill(self, area: PatternArea):
        return None


@dataclass
class TiledPattern(Pattern):
    """One motif, stamped at every cell of a lattice.

    *motif* is the 2-D figure (or a zero-argument callable returning one); the lattice
    decides where the copies go."""

    motif: Any
    lattice: Lattice

    def fill(self, area: PatternArea):
        return self.lattice.tile(self.motif, area)


@dataclass
class TilingPattern(Pattern):
    """A tile that places ITSELF, given which cell it is.

    Used by the tilings whose figure varies cell to cell (the pentagon families, leaf,
    lizard): *tile* is ``callable(Cell) -> 2-D shape`` already positioned. ``centred``
    says which origin convention the tiling uses -- ``True`` for tilings that index from
    the grid centre (they are shifted onto the area), ``False`` for corner-indexed ones."""

    tile: Callable[[Cell], Any]
    lattice: Lattice
    centred: bool = False

    def fill(self, area: PatternArea):
        shape = union_all([self.tile(cell) for cell in self.lattice.cells(area)])
        if shape is None:
            return None
        # A centre-indexed tiling is built around (0, 0); the area runs from its corner,
        # so slide the tiling onto it.
        return shape.translate([area.width / 2, area.length / 2]) if self.centred else shape


@dataclass
class AreaPattern(Pattern):
    """A pattern with no cells at all -- it fills the whole region in one shot.

    *generator* is ``callable(width, length) -> 2-D shape`` (Voronoi, Penrose). ``centred``
    says whether the generator builds around the ORIGIN (a Penrose tiling grows out of a
    unit circle) rather than across ``0..width x 0..length`` -- a centred one is shifted
    onto the area, since being handed the size does not mean a generator uses it as a
    frame."""

    generator: Callable[[float, float], Any]
    centred: bool = False

    def fill(self, area: PatternArea):
        shape = self.generator(area.width, area.length)
        if shape is None or not self.centred:
            return shape
        return shape.translate([area.width / 2, area.length / 2])


# ---------------------------------------------------------------------------
# ShapeType -> Pattern (the compatibility layer)
# ---------------------------------------------------------------------------
#
# ShapeType + ShapeObject remain the declarative surface (`BoxSpec(shape_options=...)`,
# the customizer dropdown, .scad parity). This is the ONE place that maps a shape type to
# the kind of pattern it actually is; the layout context each kind needs is supplied HERE,
# by the pattern, instead of being a keyword argument the lid pipeline was supposed to know
# to pass (and never did -- which is why 21 of these types could not be built as a lid
# pattern at all). Dissolving ShapeByType into per-pattern constructors is the next step;
# until then these three sets are the registry.

#: Tilings whose tile places itself from its cell index, indexed from the grid CENTRE.
_CENTRE_INDEXED_TILINGS = {
    ShapeType.PENTAGON_R1,
    ShapeType.PENTAGON_R3,
    ShapeType.PENTAGON_R4,
    ShapeType.PENTAGON_R5,
    ShapeType.PENTAGON_R6,
    ShapeType.PENTAGON_R7,
    ShapeType.PENTAGON_R8,
    ShapeType.PENTAGON_R9,
    ShapeType.PENTAGON_R10,
    ShapeType.PENTAGON_R11,
    ShapeType.PENTAGON_R12,
    ShapeType.PENTAGON_R13,
    ShapeType.PENTAGON_R14,
    ShapeType.PENTAGON_R15,
    ShapeType.LIZARD,
}

#: Tilings whose tile places itself, indexed from the grid CORNER.
_CORNER_INDEXED_TILINGS = {
    ShapeType.LEAF,
    # LEAF_VEINS goes down the same ShapeByType branch as LEAF and needs the same cell
    # index. The old ShapeNeedsInnerControl table listed LEAF but not LEAF_VEINS, so the
    # declared contract and the code disagreed.
    ShapeType.LEAF_VEINS,
    ShapeType.HALF_REGULAR_HEXAGON,
    ShapeType.RHOMBI_TRI_HEXAGONAL,
}

#: Patterns that fill the whole area at once. These take the region size and lay
#: themselves out across it.
_AREA_PATTERNS = {
    ShapeType.VORONOI,
    ShapeType.PENTAGON_R2,
    ShapeType.GOOSE,
    ShapeType.CHICKEN,
    ShapeType.SHEEP,
    ShapeType.BIRD,
    ShapeType.FLYING_BIRD,
}

#: Area patterns built around the ORIGIN -- a Penrose tiling grows outwards from a unit
#: circle, so being told the size does not put it on the region; it has to be moved there.
_CENTRED_AREA_PATTERNS = {
    ShapeType.PENROSE_TILING_5,
    ShapeType.PENROSE_TILING_7,
}

#: Shape types laid out on a space-filling (dense) lattice rather than a spaced grid.
_DENSE_TYPES = {
    ShapeType.DENSE_HEX,
    ShapeType.DENSE_TRIANGLE,
    ShapeType.DELTOID_TRIHEXAGONAL_KITE,
    ShapeType.DELTOID_TRIHEXAGONAL,
}


def IsDenseShapeType(shape_type: ShapeType | None = None) -> bool:
    """Return True if *shape_type* is laid out on a dense (space-filling) lattice."""
    return (shape_type if shape_type is not None else ShapeType.DENSE_HEX) in _DENSE_TYPES


def DenseShapeEdges(shape_type: ShapeType) -> int:
    """Return the number of edges on the given dense shape type."""
    return 3 if shape_type == ShapeType.DENSE_TRIANGLE else 6


def lattice_for(shape_type: ShapeType, *, layout_width: float, aspect_ratio: float = 1.0) -> Lattice:
    """The lattice *shape_type* is laid out on."""
    if IsDenseShapeType(shape_type):
        return DenseLattice(width=layout_width, edges=DenseShapeEdges(shape_type))
    return GridLattice(width=layout_width, edges=4, aspect_ratio=aspect_ratio)


def pattern_for(
    options: ShapeObject,
    *,
    layout_width: float | None = None,
    aspect_ratio: float = 1.0,
    motif: Any = None,
) -> Pattern:
    """The :class:`Pattern` for a :class:`~shape_type.ShapeObject`.

    *layout_width* is the lattice spacing (defaults to the shape's own width);
    *motif* overrides the figure for the tiled case (a caller-built shape).
    """
    shape_type = options.shape_type
    if shape_type == ShapeType.NONE:
        return NoPattern()

    spacing = layout_width if layout_width is not None else options.shape_width
    lattice = lattice_for(shape_type, layout_width=spacing, aspect_ratio=aspect_ratio)

    if shape_type in _AREA_PATTERNS or shape_type in _CENTRED_AREA_PATTERNS:
        # The area IS the layout context these need -- the thing that never reached them.
        return AreaPattern(
            generator=lambda w, l: ShapeByType(options, polygon_width=w, polygon_length=l),
            centred=shape_type in _CENTRED_AREA_PATTERNS,
        )

    centred = shape_type in _CENTRE_INDEXED_TILINGS
    if centred or shape_type in _CORNER_INDEXED_TILINGS:
        return TilingPattern(
            tile=lambda cell: ShapeByType(
                options,
                polygon_x=cell.i,
                polygon_y=cell.j,
                polygon_grid_rows=cell.rows,
                polygon_grid_cols=cell.cols,
            ),
            lattice=lattice,
            centred=centred,
        )

    return TiledPattern(motif=motif if motif is not None else ShapeByType(options), lattice=lattice)


# ---------------------------------------------------------------------------
# Where this is going
# ---------------------------------------------------------------------------
#
# This module is the routing layer: it decides WHICH kind of pattern a ShapeType is and
# hands that kind the context it needs. The shapes themselves still come from
# ShapeByType()'s branch chain, and each pattern's parameters still ride in one
# ShapeObject carrying the union of every pattern's fields (7 supershape knobs, 5 pentagon
# ones, ...). The next step is to dissolve that: each pattern becomes a constructible
# object owning only its own parameters --
#
#     Hex(width=12, thickness=2)          PentagonTiling("R3", size=14)
#     Supershape(width=12, m1=4, m2=4)    Penrose(base=5, size=12)
#
# -- with ShapeType kept as a name -> factory registry for the customizer and .scad parity.
# The three sets above become per-pattern facts (a pattern knows how it fills), and
# `pattern_for` becomes a dictionary lookup.
