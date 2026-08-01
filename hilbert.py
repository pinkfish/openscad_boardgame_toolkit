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

# LibFile: hilbert.py
#    The Hilbert space-filling curve, as a lid pattern.
#
#    ShapeType.HILBERT has been in the enum since the port began but was wired into no
#    branch of ShapeByType, in either language -- asking for it raised "Invalid shape type".
#    This is the missing implementation.
#
#    One continuous line that never crosses itself and visits every cell of a 2^n grid, so
#    the lid pattern is a single connected wall -- which also makes it a good print: no
#    isolated islands to lift off the bed.
#
# FileSummary: Hilbert curve pattern.
# FileGroup: Shapes

from __future__ import annotations

import math

from base_bgtk import stroke_path


def hilbert_order_for(side: float, size: float) -> int:
    """The curve order whose step is closest to *size* across a *side*-wide square.

    A curve of order n has ``2^n`` cells per side, so the step is ``side / (2^n - 1)``.
    Clamped to 1..7 -- order 7 is 16384 segments, which is already past the point where a
    lid reads as a solid block rather than a pattern."""
    if size <= 0:
        return 3
    ideal = math.log2(side / size + 1)
    return max(1, min(7, round(ideal)))


def hilbert_points(order: int) -> list[list[float]]:
    """The Hilbert curve of *order* as grid points, from ``(0, 0)`` to ``(2^order - 1, 0)``.

    Built by the standard d -> (x, y) mapping: walk the curve index d from 0 to 4^n - 1 and
    rotate/reflect the quadrant at each level. No recursion, so a high order costs memory
    rather than stack."""
    assert order >= 1, f"order must be >= 1, order={order}"
    n = 2 ** order
    pts: list[list[float]] = []
    for d in range(n * n):
        rx = ry = 0
        x = y = 0
        t = d
        s = 1
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            # Rotate the quadrant so the sub-curves join end to end.
            if ry == 0:
                if rx == 1:
                    x, y = s - 1 - x, s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        pts.append([float(x), float(y)])
    return pts


def hilbert_curve(width: float, length: float, size: float = 12, thickness: float = 2):
    """A Hilbert curve pattern covering ``0..width x 0..length``.

    The curve is square, so it is built across the LONGER side and overruns the shorter one;
    the caller clips it to the real outline (see :mod:`patterns`).

    Usage::

        hilbert_curve(width=80, length=60, size=12, thickness=2)

    Args:
        width/length: the area to fill
        size:         target spacing between curve passes (default 12)
        thickness:    line thickness (default 2)
    """
    assert width > 0 and length > 0, f"Need a positive area, width={width} length={length}"
    assert thickness > 0, f"thickness must be > 0, thickness={thickness}"

    side = max(width, length)
    order = hilbert_order_for(side, size)
    cells = 2 ** order
    step = side / (cells - 1) if cells > 1 else side

    pts = [[p[0] * step, p[1] * step] for p in hilbert_points(order)]
    return stroke_path(pts, width=thickness)
