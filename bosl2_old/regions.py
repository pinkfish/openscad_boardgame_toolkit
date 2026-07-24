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

# LibFile: bosl2/regions.py
#    Path and Region: object wrappers over the 2-D point maths in paths.py/rounding.py/
#    transforms.py, so a polygon can be built once and then chained
#    (`Path(pts).offset(r=-2).round_corners(radius=1).polygon()`) instead of threading raw
#    point lists through free functions.
#
# FileSummary: Object API for 2-D paths and regions.
# FileGroup: Bosl2

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from bosl2.paths import Path, Path3D  # Path/Path3D live in paths.py; re-exported here for compatibility

__all__ = ["Path", "Path3D", "Region"]


class Region(list):
    """A 2-D region: a list of :class:`Path` outlines, holes included.

    BOSL2 represents a shape-with-holes as a list of paths (outline first, then the holes), and
    that is what this is -- so, like :class:`Path`, it subclasses ``list`` and stays a drop-in
    for the raw region data the toolkit already passes to ``region()``/``union()``.

    Args:
        paths: the outlines; each is coerced to a :class:`Path`. A single flat point list is
               accepted and treated as one outline.

    Examples:
        A rectangular plate with a rectangular hole (outline + one hole), extruded into a solid:

        .. pythonscad-example::

            region = Region.with_holes(
                [[0, 0], [80, 0], [80, 60], [0, 60]],
                [[20, 20], [60, 20], [60, 40], [20, 40]],
            )
            region.geometry().linear_extrude(height=5).show()
    """

    def __init__(self, paths: Sequence = ()) -> None:
        items = list(paths)
        if items and not isinstance(items[0], (list, tuple, np.ndarray)):
            raise TypeError(f"Region needs paths, got {type(items[0]).__name__}")
        # a bare point list ([[x, y], ...]) is one outline, not a list of paths
        if items and np.asarray(items[0], dtype=float).ndim == 1:
            items = [items]
        super().__init__([p if isinstance(p, Path) else Path(p) for p in items])

    @classmethod
    def with_holes(cls, outline: Sequence, *holes: Sequence) -> "Region":
        """A region from an outline plus hole outlines.

        This is what a concentric ``DifferenceWithOffset`` produces: outline + inner hole, no
        clipping involved.
        """
        return cls([outline, *holes])

    @property
    def outline(self) -> Path:
        """The outer path."""
        assert len(self), "empty Region has no outline"
        return self[0]

    @property
    def holes(self) -> list[Path]:
        return list(self[1:])

    def offset(self, r: float | None = None, delta: float | None = None, chamfer: bool = False) -> "Region":
        """Offset every path in the region."""
        return Region([p.offset(r=r, delta=delta, chamfer=chamfer) for p in self])

    def round_corners(self, radius: float | list[float] | None = None, **kwargs: Any) -> "Region":
        return Region([p.round_corners(radius=radius, **kwargs) for p in self])

    def translate(self, v: Sequence[float]) -> "Region":
        return Region([p.translate(v) for p in self])

    def bounds(self) -> np.ndarray:
        """[[min_x, min_y], [max_x, max_y]] over every path."""
        assert len(self), "empty Region has no bounds"
        all_pts = np.vstack([p.array for p in self])
        return np.array([all_pts.min(axis=0), all_pts.max(axis=0)])

    def geometry(self):
        """Native 2-D geometry: the outline with the holes subtracted."""
        shape = self.outline.polygon()
        for hole in self.holes:
            shape = shape - hole.polygon()
        return shape

    def stroke(self, width: float = 1, **kwargs: Any):
        """Draw every path in this region as a closed solid line (see :func:`bosl2.drawing.stroke`)."""
        from bosl2.drawing import stroke as _stroke

        return _stroke(self, width=width, **kwargs)

    def dashed_stroke(self, dashpat: Sequence[float] = (3, 3), **kwargs: Any) -> list[Path]:
        """Break every path in this region into dash sub-paths (see :func:`bosl2.drawing.dashed_stroke`)."""
        from bosl2.drawing import dashed_stroke as _dashed

        return _dashed(self, dashpat=dashpat, **kwargs)

    def __repr__(self) -> str:
        return f"Region({len(self)} paths: {[len(p) for p in self]})"
