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

# LibFile: voronoi.py
#    Voronoi cell pattern -- an organic, cracked-mud lid texture.
#
#    ShapeType.VORONOI has been in the enum all along (as has
#    ``base_bgtk.default_voronoi_seed``) but the module it called was never written, in
#    either language. This is that module: a deterministic Voronoi diagram over the area,
#    drawn as walls of a given thickness.
#
#    Cells are built by HALF-PLANE CLIPPING rather than by a sweepline: each site's cell is
#    the area rectangle clipped by the perpendicular bisector between it and every nearby
#    site. That is a few lines of numpy, needs no scipy (unavailable inside the app), and is
#    exact -- the cost is O(sites x neighbours), which at lid scale is nothing.
#
# FileSummary: Voronoi cell pattern.
# FileGroup: Shapes

from __future__ import annotations

import math
import random

import numpy as np

from base_bgtk import default_voronoi_seed
from pybosl2 import shapes2d

#: Half-plane clipping is exact, but a cell can only be bounded by sites within a few cell
#: widths; going wider just wastes work.
_NEIGHBOUR_RADIUS_CELLS = 3.0


def voronoi_sites(
    width: float, length: float, cellsize: float, seed: int | None = None, jitter: float = 0.45
) -> np.ndarray:
    """The seed points of the diagram: a jittered grid, one site per ``cellsize`` cell.

    A jittered grid rather than uniform random points, because uniform points clump and
    leave bald patches -- on a lid you want cells of roughly even size. *jitter* is the
    fraction of a cell a site may wander from its grid position (0 = a plain grid).

    Deterministic: the same ``seed`` always gives the same lid.
    """
    rng = random.Random(default_voronoi_seed if seed is None else seed)
    # Pad by a ring of cells so the cells that touch the edges are bounded by real
    # neighbours rather than running off to infinity.
    cols = max(2, math.ceil(width / cellsize) + 3)
    rows = max(2, math.ceil(length / cellsize) + 3)
    sites = []
    for i in range(cols):
        for j in range(rows):
            x = (i - 1) * cellsize + rng.uniform(-jitter, jitter) * cellsize
            y = (j - 1) * cellsize + rng.uniform(-jitter, jitter) * cellsize
            sites.append([x, y])
    return np.asarray(sites, dtype=float)


def _clip_halfplane(poly: np.ndarray, normal: np.ndarray, offset: float) -> np.ndarray:
    """Sutherland-Hodgman clip of convex *poly* to ``normal . p <= offset``."""
    if len(poly) == 0:
        return poly
    dist = poly @ normal - offset
    out: list[list[float]] = []
    for i in range(len(poly)):
        j = (i + 1) % len(poly)
        di, dj = dist[i], dist[j]
        if di <= 0:
            out.append(list(poly[i]))
        if (di < 0 < dj) or (dj < 0 < di):
            t = di / (di - dj)
            out.append(list(poly[i] + t * (poly[j] - poly[i])))
    return np.asarray(out, dtype=float)


def voronoi_cell(site: np.ndarray, sites: np.ndarray, bounds: np.ndarray, cellsize: float) -> np.ndarray:
    """One Voronoi cell: *bounds* clipped by the bisector between *site* and each neighbour."""
    poly = bounds
    reach = _NEIGHBOUR_RADIUS_CELLS * cellsize
    for other in sites:
        delta = other - site
        d = float(np.hypot(*delta))
        if d < 1e-9 or d > reach:
            continue
        # Points on this cell's side of the bisector satisfy delta . p <= delta . midpoint.
        poly = _clip_halfplane(poly, delta, float(delta @ (site + other) / 2))
        if len(poly) < 3:
            return poly
    return poly


def Voronoi(
    width: float,
    length: float,
    cellsize: float = 12,
    thickness: float = 2,
    seed: int | None = None,
    jitter: float = 0.45,
) -> "shapes2d.Bosl2Shape2D":
    """A Voronoi wall pattern covering ``0..width x 0..length``.

    Usage::

        Voronoi(width=80, length=60, cellsize=12, thickness=2)

    Args:
        width/length: the area to fill
        cellsize:     rough diameter of one cell (default 12)
        thickness:    wall thickness (default 2)
        seed:         RNG seed (default ``base_bgtk.default_voronoi_seed``)
        jitter:       how far a site may wander from its grid slot, in cells (default 0.45)
    """
    assert width > 0 and length > 0, f"Need a positive area, width={width} length={length}"
    assert cellsize > 0, f"cellsize must be > 0, cellsize={cellsize}"
    assert thickness > 0, f"thickness must be > 0, thickness={thickness}"

    sites = voronoi_sites(width=width, length=length, cellsize=cellsize, seed=seed, jitter=jitter)
    # Clip every cell to a rectangle a cell larger than the area, so the pattern reaches the
    # edges; the caller trims it to the real outline.
    pad = cellsize
    bounds = np.asarray(
        [[-pad, -pad], [width + pad, -pad], [width + pad, length + pad], [-pad, length + pad]], dtype=float
    )

    # Each cell contributes its own wall, inset by half the thickness, so the wall shared by
    # two neighbours comes out `thickness` wide rather than double.
    pieces = []
    for site in sites:
        cell = voronoi_cell(site, sites, bounds, cellsize)
        if len(cell) < 3:
            continue
        pts = [[float(x), float(y)] for x, y in cell]
        pieces.append(shapes2d.polygon(pts) - shapes2d.polygon(pts).offset(delta=-thickness / 2))

    assert pieces, "Voronoi produced no cells -- is cellsize larger than the area?"
    # Balanced union: a lid is hundreds of cells and a linear chain nests that deep.
    while len(pieces) > 1:
        pieces = [
            pieces[i] | pieces[i + 1] if i + 1 < len(pieces) else pieces[i]
            for i in range(0, len(pieces), 2)
        ]
    return pieces[0]
