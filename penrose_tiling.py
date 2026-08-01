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
from base_bgtk import stroke_path, union_all_2d
from pybosl2 import shapes2d

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


def penrose_triangles(triangles: list[list]) -> list[list]:
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


def penrose_triangles_division(triangles: list[list], division: int) -> list[list]:
    """Recursively subdivide *triangles* by *division* steps.

    Args:
        triangles: initial triangle list
        division:  number of recursive subdivisions
    Returns:
        final list of triangles
    """
    new_tris = penrose_triangles(triangles)
    if division > 0:
        return penrose_triangles_division(new_tris, division - 1)
    return new_tris


def penrose_tiling(
    width: float, divisions: int = 7, thickness: float = 1, base: int = 5
) -> "shapes2d.Bosl2Shape2D":
    """Generates a 2-D Penrose tiling as one direct-CSG shape: the "thin" triangles filled
    solid, the "thicc" triangles drawn as their two open edges stroked `thickness` wide.
    Extrude the result with .linear_extrude(height=...) to get a solid.

    The tiling is built around the ORIGIN, spanning roughly +/- `width` -- it is not framed
    on a 0..width box (:class:`~patterns.AreaPattern` moves it onto the region it fills).

    (The original coloured the two families red/green and built the strokes with
    _bosl2.stroke(), which has no BOSL2 function form and always aborted the render. The
    port went to SDF to get around that; the strokes are plain CSG rectangles now -- see
    :func:`~base_bgtk.stroke_path` -- because reaching a CSG lid from an SDF meant meshing the
    whole tiling, which at lid size produced no geometry at all.)

    Usage::

        penrose_tiling(100, divisions=5, thickness=1, base=5)
        penrose_tiling(100, divisions=5, thickness=1, base=7)

    Args:
        width:     width of the tiling space
        divisions: number of recursive subdivisions (default 7)
        thickness: stroke width for "thicc" triangles (default 1)
        base:      number of base sectors (default 5)
    """
    triangles = []
    for i in range(base * 2):
        a1 = (2 * i - 1) * math.pi / (base * 2)
        a2 = (2 * i + 1) * math.pi / (base * 2)
        p2 = [math.cos(a1), math.sin(a1)]
        p3 = [math.cos(a2), math.sin(a2)]
        a, b = (p2, p3) if (i % 2 == 0) else (p3, p2)
        triangles.append(["thin", [0, 0], a, b])

    final_triangles = penrose_triangles_division(triangles, divisions)

    pieces = []
    for kind, p1, p2, p3 in final_triangles:
        pts = [_vec_scale(p1, width), _vec_scale(p2, width), _vec_scale(p3, width)]
        if kind == "thin":
            # Grown a whisker so triangles sharing an edge overlap rather than merely touch.
            pieces.append(shapes2d.polygon(pts).offset(delta=0.001))
        else:
            pieces.append(stroke_path(pts, width=thickness))
    return union_all_2d(pieces)
