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

# LibFile: shapes3d.py
#    3-D shapes (dice, polyhedra) for board games.
#
# FileSummary: 3D Shapes for all sorts of things.
# FileGroup: Shapes

from __future__ import annotations
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
from bosl2 import shapes3d

import math


_bosl2 = osuse("BOSL2/std.scad")
_polyhedra = osuse("BOSL2/polyhedra.scad")

# ---------------------------------------------------------------------------
# Section: Shapes3d — 3-D polyhedra for use in boxes
# ---------------------------------------------------------------------------


def Dodecahedron(size: float) -> PyOpenSCAD:
    """Creates a 12-sided shape (d12) for use in games.

    Usage::

        Dodecahedron(20)

    Args:
        size: width of the dodecahedron
    """
    dihedral = 116.565
    shape = shapes3d.cuboid([2, 2, 1])
    for i in range(5):
        shape = shape & shapes3d.cuboid([2, 2, 1]).rotate([dihedral, 0, 0]).rotate([0, 0, 72 * i])
    return shape.scale([size, size, size])


def Tetrahedron(size: float) -> PyOpenSCAD:
    """Creates a d4 tetrahedron shape for use in games.

    Usage::

        Tetrahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    side = math.sqrt(3) * size / 2
    h = math.sqrt(2 / 3) * side
    return shapes3d.cyl(d1=size, d2=0, h=h, _fn=3).translate(
        [-(size - side) / 2, 0, (size - side) / 2]
    )


def Octahedron(size: float) -> PyOpenSCAD:
    """Creates a d8 octahedron shape for use in games.

    Usage::

        Octahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    return _polyhedra.octahedron(size=size)


def Icosahedron(size: float) -> PyOpenSCAD:
    """Creates a d20 icosahedron shape for use in games.

    Usage::

        Icosahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    phi = 0.5 * (math.sqrt(5) + 1)  # golden ratio
    edge_length = size / 2 / 0.951
    st = 0.0001  # microscopic sheet thickness
    a = cube([edge_length * phi, edge_length, st], center=True)
    b = cube([edge_length * phi, edge_length, st], center=True).rotate([90, 90, 0])
    c = cube([edge_length * phi, edge_length, st], center=True).rotate([90, 0, 90])
    return hull(a, b, c)


def Trapezohedron(size: float, length_mod: float = 0, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Creates a d10 trapezohedron shape for use in games.

    Usage::

        Trapezohedron(10)
        Trapezohedron(20)  # with face labels as children

    Args:
        size:       diameter of the circumscribed sphere
        length_mod: modification to the length (default 0, currently unused
                    by the underlying BOSL2 trapezohedron, kept for API
                    compatibility)
        children:   optional child solid(s) placed on each face. Note: unlike
                    the original SCAD module, the per-face fine-rotation
                    (-30/15/240 degrees depending on $faceindex) isn't
                    reproduced here, so labels keep BOSL2's default
                    rotate_children face alignment instead of the
                    hand-tuned one.
    """
    base = _polyhedra.regular_polyhedron("trapezohedron", faces=10, d=size, h=size / 2, facedown=False)
    if children is None:
        return base

    cutter = _polyhedra.regular_polyhedron(
        "trapezohedron",
        faces=10,
        d=size,
        h=size / 2,
        facedown=False,
        draw=False,
        rotate_children=True,
        _children=children,
    )
    return base - cutter
