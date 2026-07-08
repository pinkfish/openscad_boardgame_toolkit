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

# LibFile: bosl2/comparisons.py
#    Pure-Python port of the pieces of BOSL2's comparisons.scad that
#    bosl2/paths.py depends on. No osuse()/BOSL2 runtime dependency.
#    approx()/deduplicate() accept plain lists/tuples *or* numpy ndarrays
#    for vector-valued arguments (bosl2/vectors.py, paths.py, and
#    geometry.py all return ndarrays now), always using numpy for the
#    ndarray-vs-ndarray equality check so it never falls through to a bare
#    `==` between arrays (which returns an elementwise array, not a bool).
#
# FileSummary: Approximate comparison and list search helpers (BOSL2 comparisons.scad).
# FileGroup: BOSL2

import numpy as np

from bosl2.math import EPSILON

_SCALAR_TYPES = (int, float, np.floating, np.integer)
_VECTOR_TYPES = (list, tuple, np.ndarray)


def approx(a, b, eps: float = EPSILON) -> bool:
    """True if *a* and *b* are equal, or numerically/component-wise within *eps*."""
    if isinstance(a, _SCALAR_TYPES) and isinstance(b, _SCALAR_TYPES):
        return abs(float(a) - float(b)) <= eps
    if isinstance(a, _VECTOR_TYPES) and isinstance(b, _VECTOR_TYPES):
        if len(a) != len(b):
            return False
        return all(approx(x, y, eps) for x, y in zip(a, b))
    return bool(np.array_equal(a, b))


def min_index(vals) -> int:
    """Index of the first occurrence of the minimum value in *vals*."""
    vals = list(vals)
    return vals.index(min(vals))


def max_index(vals) -> int:
    """Index of the first occurrence of the maximum value in *vals*."""
    vals = list(vals)
    return vals.index(max(vals))


def deduplicate(lst: list, closed: bool = False, eps: float = EPSILON) -> list:
    """Remove consecutive (approximately) duplicate entries from *lst*.

    If *closed* is True, the last entry is also compared (wrapping) against
    the first; otherwise the true last entry is always kept.
    """
    length = len(lst)
    if length == 0:
        return []
    end = length if closed else length - 1
    out = []
    for i in range(length):
        if i == end:
            out.append(lst[i])
            continue
        nxt = lst[(i + 1) % length]
        differs = (not np.array_equal(lst[i], nxt)) if eps == 0 else (not approx(lst[i], nxt, eps))
        if differs:
            out.append(lst[i])
    return out
