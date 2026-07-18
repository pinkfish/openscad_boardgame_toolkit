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
#    Pure-Python port of BOSL2's approx() from comparisons.scad. No
#    osuse()/BOSL2 runtime dependency. approx() accepts plain lists/tuples
#    *or* numpy ndarrays for vector-valued arguments (bosl2/vectors.py,
#    paths.py, and geometry.py all return ndarrays now), always using numpy
#    for the ndarray-vs-ndarray equality check so it never falls through to
#    a bare `==` between arrays (which returns an elementwise array, not a
#    bool). The simple list searches (min_index/max_index) and deduplicate()
#    now live inline / on the Path object, not here.
#
# FileSummary: Approximate comparison (BOSL2 comparisons.scad).
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
