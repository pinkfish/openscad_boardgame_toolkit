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

# Used the information on this page to generate this code
# https://preshing.com/20110831/penrose-tiling-explained/

# LibFile: penrose_tiling.py
#    Penrose tiling generators.

from __future__ import annotations
import math
import pysolidfive

# Golden ratio — used in subdivision
PHI = (1 + math.sqrt(5)) / 2


# ---------------------------------------------------------------------------
# Pure-Python helper: triangle subdivision
# ---------------------------------------------------------------------------


def _vec_add(a: list[float], b: list[float]) -> list[float]:
    return [a[0] + b[0], a[1] + b[1]]


def _vec_sub(a: list[float], b: list[float]) -> list[float]:
    return [a[0] - b[0], a[1] - b[1]]


def _vec_scale(a: list[float], s: float) -> list[float]:
    return [a[0] * s, a[1] * s]


def PenroseTriangles(triangles: list[list]) -> list[list]:
    """Subdivide a list of Penrose triangles once.

    Each triangle is a 4-element list ``[kind, p1, p2, p3]`` where
    *kind* is ``"thin"`` or ``"thicc"``.

    Args:
        triangles: list of triangle definitions
    Returns:
        new (larger) list of subdivided triangles
    """
    result = []
    for tri in triangles:
        kind, p1, p2, p3 = tri
        if kind == "thin":
            q = _vec_add(p1, _vec_scale(_vec_sub(p2, p1), 1 / PHI))
            result.append(["thin", p3, q, p2])
            result.append(["thicc", q, p3, p1])
        else:
            R = _vec_add(p2, _vec_scale(_vec_sub(p3, p2), 1 / PHI))
            Q = _vec_add(p2, _vec_scale(_vec_sub(p1, p2), 1 / PHI))
            result.append(["thicc", R, p3, p1])
            result.append(["thicc", Q, R, p2])
            result.append(["thin", R, Q, p1])
    return result


def PenroseTrianglesDivision(triangles: list[list], division: int) -> list[list]:
    """Recursively subdivide *triangles* by *division* steps.

    Args:
        triangles: initial triangle list
        division:  number of recursive subdivisions
    Returns:
        final list of triangles
    """
    new_tris = PenroseTriangles(triangles)
    if division > 0:
        return PenroseTrianglesDivision(new_tris, division - 1)
    return new_tris


def PenroseTiling(
    width: float, divisions: int = 7, thickness: float = 1, base: int = 5, res: int | None = None
) -> "pysolidfive.PyShape2D":
    """Generates a 2-D Penrose tiling as a single pysolidfive shape: the "thin" triangles
    filled solid, the "thicc" triangles drawn as their two open edges stroked `thickness`
    wide. (The original coloured the two families red/green and built the strokes with
    _bosl2.stroke(), which has no BOSL2 function form and always aborted the render -- this
    construction is the first one that actually works in the Python port. Extrude the result
    with .linear_extrude(height=...) to get a solid.)

    Usage::

        PenroseTiling(100, divisions=5, thickness=1, base=5)
        PenroseTiling(100, divisions=5, thickness=1, base=7)

    Args:
        width:     width of the tiling space
        divisions: number of recursive subdivisions (default 7)
        thickness: stroke width for "thicc" triangles (default 1)
        base:      number of base sectors (default 5)
        res:       meshing resolution. Defaults to enough cells that the mesher's grid step
                   stays at or below the stroke width -- at the library default (20) a
                   thickness-1 tiling 100 wide meshes with 5-unit cells, which turns the
                   strokes into dashed lines.
    """
    if res is None:
        res = max(20, math.ceil(2 * width / thickness))
    triangles = []
    for i in range(base * 2):
        a1 = (2 * i - 1) * math.pi / (base * 2)
        a2 = (2 * i + 1) * math.pi / (base * 2)
        p2 = [math.cos(a1), math.sin(a1)]
        p3 = [math.cos(a2), math.sin(a2)]
        a, b = (p2, p3) if (i % 2 == 0) else (p3, p2)
        triangles.append(["thin", [0, 0], a, b])

    final_triangles = PenroseTrianglesDivision(triangles, divisions)

    pieces = []
    for kind, p1, p2, p3 in final_triangles:
        pts = [_vec_scale(p1, width), _vec_scale(p2, width), _vec_scale(p3, width)]
        if kind == "thin":
            # Grown a whisker so triangles sharing an edge overlap rather than merely touch:
            # a min()-union of exactly-abutting SDFs has a zero-level seam along the shared
            # edge, which the mesher can turn into internal membrane artifacts.
            pieces.append(pysolidfive.polygon2d(pts, res=res).offset(0.001))
        else:
            pieces.append(pysolidfive.stroke2d(pts, width=thickness, res=res))
    # union2d, not a linear `|` chain: deep subdivisions produce hundreds of triangles, and a
    # chain that long overflows Python's recursion limit when the SDF is evaluated.
    return pysolidfive.union2d(pieces)
