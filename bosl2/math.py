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

# LibFile: bosl2/math.py
#    Pure-Python port of the pieces of BOSL2's math.scad that bosl2/paths.py
#    depends on (general numeric helpers and the deriv/deriv2/deriv3
#    calculus functions). No osuse()/BOSL2 runtime dependency. Built on
#    numpy: every vector-valued function here returns a real numpy ndarray
#    (float64) rather than a plain list.
#
# FileSummary: General numeric helpers and numerical calculus (BOSL2 math.scad).
# FileGroup: BOSL2

from collections.abc import Sequence

import numpy as np

# Default tolerance used throughout BOSL2 for floating-point comparisons.
EPSILON = 1e-9


def lerp(a, b, t: float):
    """Linearly interpolate between *a* and *b* by fraction *t* (scalar or vector)."""
    if isinstance(a, (list, tuple, np.ndarray)):
        return np.asarray(a, dtype=float) + (np.asarray(b, dtype=float) - np.asarray(a, dtype=float)) * t
    return a + (b - a) * t


def lerpn(a, b, n: int, endpoint: bool = True) -> np.ndarray:
    """Return *n* points linearly interpolated between *a* and *b*, as an (n, dim) ndarray
    (or a length-n 1-D ndarray for scalar *a*/*b*).

    If endpoint is True, the last returned point equals *b*; otherwise the
    range is divided into *n* equal steps without reaching *b*.
    """
    if n <= 0:
        return np.empty(0)
    if n == 1:
        return np.asarray([a], dtype=float)
    denom = (n - 1) if endpoint else n
    return np.asarray([lerp(a, b, i / denom) for i in range(n)], dtype=float)


def _dnu_calc(f1, fc, f2, h1, h2):
    if h2 < h1:
        f1 = lerp(fc, f1, h2 / h1)
    if h1 < h2:
        f2 = lerp(fc, f2, h1 / h2)
    return (np.asarray(f2, dtype=float) - np.asarray(f1, dtype=float)) / (2 * min(h1, h2))


def _deriv_nonuniform(data, h, closed: bool) -> np.ndarray:
    length = len(data)
    if closed:
        return np.asarray(
            [
                _dnu_calc(data[(length + i - 1) % length], data[i], data[(i + 1) % length], h[i - 1], h[i])
                for i in range(length)
            ],
            dtype=float,
        )
    out = [(np.asarray(data[1], dtype=float) - np.asarray(data[0], dtype=float)) / h[0]]
    for i in range(1, length - 1):
        out.append(_dnu_calc(data[i - 1], data[i], data[i + 1], h[i - 1], h[i]))
    out.append((np.asarray(data[length - 1], dtype=float) - np.asarray(data[length - 2], dtype=float)) / h[length - 2])
    return np.asarray(out, dtype=float)


def deriv(data, h: "float | Sequence[float] | np.ndarray" = 1, closed: bool = False) -> np.ndarray:
    """Numeric first-derivative estimate of *data* (scalar- or vector-valued points), as an ndarray.

    Uses a symmetric derivative approximation for internal points and a
    two-point method at the endpoints of an open path. If *h* is a list it
    is treated as the (possibly non-uniform) per-segment sampling distance.
    """
    if not isinstance(h, (int, float)):
        return _deriv_nonuniform(data, h, closed)
    arr = np.asarray(data, dtype=float)
    length = len(arr)
    if closed:
        return np.asarray([(arr[(i + 1) % length] - arr[(length + i - 1) % length]) / (2 * h) for i in range(length)])
    if length < 3:
        first = arr[1] - arr[0]
        last = arr[length - 1] - arr[length - 2]
    else:
        first = 3 * (arr[1] - arr[0]) - (arr[2] - arr[1])
        last = (arr[length - 3] - arr[length - 2]) - 3 * (arr[length - 2] - arr[length - 1])
    out = [first / (2 * h)]
    for i in range(1, length - 1):
        out.append((arr[i + 1] - arr[i - 1]) / (2 * h))
    out.append(last / (2 * h))
    return np.asarray(out)


def deriv2(data, h: float = 1, closed: bool = False) -> np.ndarray:
    """Numeric second-derivative estimate of *data* (scalar- or vector-valued points), as an ndarray."""
    arr = np.asarray(data, dtype=float)
    length = len(arr)
    if closed:
        return np.asarray(
            [(arr[(i + 1) % length] - 2 * arr[i] + arr[(length + i - 1) % length]) / (h * h) for i in range(length)]
        )
    if length == 3:
        first = arr[0] - 2 * arr[1] + arr[2]
        last = arr[length - 1] - 2 * arr[length - 2] + arr[length - 3]
    elif length == 4:
        first = 2 * arr[0] - 5 * arr[1] + 4 * arr[2] - arr[3]
        last = -2 * arr[length - 1] + 5 * arr[length - 2] - 4 * arr[length - 3] + arr[length - 4]
    else:
        first = (35 * arr[0] - 104 * arr[1] + 114 * arr[2] - 56 * arr[3] + 11 * arr[4]) / 12
        last = (
            35 * arr[length - 1] - 104 * arr[length - 2] + 114 * arr[length - 3] - 56 * arr[length - 4] + 11 * arr[length - 5]
        ) / 12
    out = [first / (h * h)]
    for i in range(1, length - 1):
        out.append((arr[i + 1] - 2 * arr[i] + arr[i - 1]) / (h * h))
    out.append(last / (h * h))
    return np.asarray(out)


def deriv3(data, h: float = 1, closed: bool = False) -> np.ndarray:
    """Numeric third-derivative estimate of *data* (scalar- or vector-valued points), as an ndarray.

    Requires at least 5 points.
    """
    arr = np.asarray(data, dtype=float)
    length = len(arr)
    h3 = h * h * h
    if closed:
        return np.asarray(
            [
                (
                    -arr[(length + i - 2) % length]
                    + 2 * arr[(length + i - 1) % length]
                    - 2 * arr[(i + 1) % length]
                    + arr[(i + 2) % length]
                )
                / (2 * h3)
                for i in range(length)
            ]
        )
    first = (-5 * arr[0] + 18 * arr[1] - 24 * arr[2] + 14 * arr[3] - 3 * arr[4]) / 2
    second = (-3 * arr[0] + 10 * arr[1] - 12 * arr[2] + 6 * arr[3] - arr[4]) / 2
    last = (5 * arr[length - 1] - 18 * arr[length - 2] + 24 * arr[length - 3] - 14 * arr[length - 4] + 3 * arr[length - 5]) / 2
    prelast = (3 * arr[length - 1] - 10 * arr[length - 2] + 12 * arr[length - 3] - 6 * arr[length - 4] + arr[length - 5]) / 2
    out = [first / h3, second / h3]
    for i in range(2, length - 2):
        out.append((-arr[i - 2] + 2 * arr[i - 1] - 2 * arr[i + 1] + arr[i + 2]) / (2 * h3))
    out.append(prelast / h3)
    out.append(last / h3)
    return np.asarray(out)
