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

# LibFile: bosl2/transforms.py
#    Pure-Python port of the point-list-applying function form of BOSL2's
#    transforms.scad (move()/rot()/right()/mirror()/yflip()), plus
#    polar_to_xy() from coords.scad. No osuse()/BOSL2 runtime dependency.
#
#    Deliberately returns plain Python lists, NOT numpy ndarrays, unlike
#    most of the rest of bosl2/ -- these functions are used throughout
#    tesselations.py and tesselations/*.py specifically to build a closed
#    path by *concatenating* several transformed segments with `+`
#    (e.g. `move(...) + move(...) + move(...)`). If these returned
#    ndarrays, that `+` would silently become elementwise vector addition
#    instead of concatenation (since same-length segments broadcast
#    together as arrays), which is wrong and nearly undetectable. Every
#    computation here still happens in numpy internally for clarity; only
#    the final `.tolist()` boundary is kept.
#
#    Only the `p=<list of points>` function forms are ported (not the
#    module forms that transform child geometry, and not the "return an
#    affine matrix" form used when `p` is omitted), since that's the only
#    way this project uses these functions: applying a transform directly
#    to 2-D path/point-list data.
#
# FileSummary: Move/rotate/mirror point lists (BOSL2 transforms.scad, coords.scad).
# FileGroup: BOSL2

import math

import numpy as np


def move(v, p) -> list[list[float]]:
    """Translate every point in *p* by *v* (if *v* is shorter than the points in *p*, the
    missing trailing components are treated as 0; if longer, the extras are ignored)."""
    parr = np.asarray(p, dtype=float)
    dim = parr.shape[1]
    varr = np.zeros(dim)
    v = np.asarray(v, dtype=float)
    varr[: min(dim, len(v))] = v[: min(dim, len(v))]
    return (parr + varr).tolist()


def right(x: float, p) -> list[list[float]]:
    """Translate every point in *p* by *x* along the X axis."""
    parr = np.asarray(p, dtype=float).copy()
    parr[:, 0] += x
    return parr.tolist()


def rot(a: float, p) -> list[list[float]]:
    """Rotate every 2-D point in *p* by *a* degrees around the Z axis (origin)."""
    rad = math.radians(a)
    c, s = math.cos(rad), math.sin(rad)
    rotmat = np.array([[c, -s], [s, c]])
    parr = np.asarray(p, dtype=float)
    return (parr @ rotmat.T).tolist()


def mirror(v, p) -> list[list[float]]:
    """Reflect every point in *p* across the plane/line through the origin with normal *v*."""
    n = np.asarray(v, dtype=float)
    n = n / np.linalg.norm(n)
    parr = np.asarray(p, dtype=float)
    d = parr @ n
    return (parr - 2 * np.outer(d, n)).tolist()


def yflip(p, y: float = 0) -> list[list[float]]:
    """Reflect every 2-D point in *p* across the horizontal line Y=*y* (default: the X axis)."""
    parr = np.asarray(p, dtype=float).copy()
    parr[:, 1] = 2 * y - parr[:, 1]
    return parr.tolist()


def polar_to_xy(r: float, angle: float) -> list[float]:
    """Convert polar coordinates (radius, angle in degrees) to a 2-D [x, y] point."""
    rad = math.radians(angle)
    return [r * math.cos(rad), r * math.sin(rad)]
