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

# LibFile: bosl2/vectors.py
#    Pure-Python port of the pieces of BOSL2's vectors.scad that bosl2/paths.py
#    depends on. No osuse()/BOSL2 runtime dependency. Built on numpy: every
#    function here accepts either a plain list/tuple or an ndarray and returns
#    a real numpy ndarray (float64), rather than converting back to a plain
#    list at the boundary -- callers that need a plain list for a native
#    PythonSCAD call should do so explicitly with `.tolist()`.
#
# FileSummary: Vector predicates and scalar-vector operations (BOSL2 vectors.scad).
# FileGroup: BOSL2

import math

import numpy as np

from bosl2.math import EPSILON


def is_vector(v, length: int | None = None, zero: bool | None = None, eps: float = EPSILON) -> bool:
    """True if *v* is a list/tuple/ndarray of finite numbers (optionally of a given length and/or zero-ness)."""
    if isinstance(v, np.ndarray):
        if v.ndim != 1 or v.size == 0:
            return False
    elif not isinstance(v, (list, tuple)) or len(v) == 0:
        return False
    for x in v:
        if isinstance(x, bool) or not isinstance(x, (int, float, np.floating, np.integer)) or math.isinf(x) or math.isnan(x):
            return False
    if length is not None and len(v) != length:
        return False
    if zero is not None:
        is_zero = float(np.linalg.norm(np.asarray(v, dtype=float))) < eps
        if is_zero != zero:
            return False
    return True


def add_scalar(v, s: float) -> np.ndarray:
    """Return *v* with scalar *s* added to every entry."""
    return np.asarray(v, dtype=float) + s


def unit(v, error=None) -> np.ndarray:
    """Normalize *v* to unit length.

    If *v* has (near) zero length, returns *error* if given, else raises
    ValueError (matching BOSL2's default assert-on-zero-vector behavior).
    """
    arr = np.asarray(v, dtype=float)
    n = float(np.linalg.norm(arr))
    if n < EPSILON:
        if error is not None:
            return np.asarray(error, dtype=float)
        raise ValueError("Cannot normalize a zero vector")
    return arr / n
