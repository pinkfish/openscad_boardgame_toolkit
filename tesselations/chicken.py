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

# LibFile: chicken.py
#    Chicken tesselation.

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from kite_tesselation import MakeTesselationKiteHexagon
from pybosl2 import Path2D


def TesselationChickenHex(size: float, thickness: float = 2, outer_offset: float = 0.1) -> PyOpenSCAD:
    """Make a chicken hex from a kite tesselation.

    Usage::

        TesselationChickenHex(size=20)

    Args:
        size: length of the chicken
        thickness: outline stroke thickness (default 2)
        outer_offset: extra outward offset (default 0.1)
    """
    line1 = [
        [-0.5, 0], [-0.39, 0.1], [-0.32, 0.15], [-0.29, 0.18], [-0.17, 0.22], [-0.13, 0.22],
        [-0.1, 0.2], [-0.06, 0.18], [-0.03, 0.12], [-0.02, 0.07], [-0.01, 0.04], [0.01, 0.01],
        [0.03, -0.02], [0.04, -0.04], [0.05, -0.05], [0.06, -0.05], [0.08, -0.05], [0.09, -0.05],
        [0.11, -0.05], [0.15, -0.05], [0.19, -0.04], [0.23, -0.04], [0.28, -0.15], [0.27, -0.25],
        [0.5, 0],
    ]
    raw2 = [
        [0, 0], [-0.03, 0.16], [-0.05, 0.18], [-0.09, 0.26], [-0.09, 0.29], [-0.09, 0.31],
        [-0.06, 0.33], [-0.03, 0.37], [0.01, 0.33], [0.03, 0.30], [0.06, 0.31], [0.09, 0.33],
        [0.12, 0.33], [0.14, 0.33], [0.14, 0.31], [0.14, 0.29], [0.17, 0.29], [0.26, 0.31],
        [0.28, 0.23], [0.36, 0.22], [0.39, 0.20], [0.40, 0.19], [0.40, 0.18], [0.37, 0.13],
        [0.32, 0.14], [0.32, 0.13], [0.34, 0.12], [0.38, 0.09], [0.63, 0.03], [0.80, 0.00],
        [0.97, -0.02], [1, 0],
    ]
    line2 = [[i[0] - 0.5, i[1]] for i in Path2D(raw2).rot(0)]

    return MakeTesselationKiteHexagon(size, line2, line1, thickness=thickness, outer_offset=outer_offset)
