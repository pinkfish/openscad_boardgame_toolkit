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
#    3-D shapes (dice, polyhedra) for board games. Built entirely on pysolidfive -- no pybosl2
#    port and no BOSL2 polyhedra.scad, which could never load through osuse() anyway (it
#    depends on its include chain for PHI and friends, so the old Octahedron/Trapezohedron
#    never actually worked in the Python port). Every solid here is a convex polyhedron, which
#    is exactly what pysolidfive.convex_polyhedron() (a max of hull-face half-spaces) or an
#    intersection of rotated cuboid slabs expresses directly.
#
# FileSummary: 3D Shapes for all sorts of things.
# FileGroup: Shapes

from __future__ import annotations
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pysolidfive

import math


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
    # Same construction as the original: a unit slab intersected with 5 copies tipped over by
    # the dodecahedral dihedral angle -- just composed symbolically as SDFs and meshed once.
    dihedral = 116.565
    shape = pysolidfive.cuboid([2, 2, 1])
    for i in range(5):
        shape = shape & pysolidfive.cuboid([2, 2, 1]).rotate([dihedral, 0, 0]).rotate([0, 0, 72 * i])
    return shape.scale([size, size, size]).color(default_material_colour)


def Tetrahedron(size: float) -> PyOpenSCAD:
    """Creates a d4 tetrahedron shape for use in games.

    Usage::

        Tetrahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    # The original built this as a 3-sided cone (cyl with _fn=3): a base triangle inscribed in
    # the d=size circle (first vertex at +x) with the apex centered above -- reproduced here as
    # the same four vertices hulled into planes.
    side = math.sqrt(3) * size / 2
    h = math.sqrt(2 / 3) * side
    r = size / 2
    pts = [[r * math.cos(math.radians(120 * i)), r * math.sin(math.radians(120 * i)), 0] for i in range(3)]
    pts.append([0, 0, h])
    return (
        pysolidfive.convex_polyhedron(pts)
        .translate([-(size - side) / 2, 0, (size - side) / 2])
        .color(default_material_colour)
    )


def Octahedron(size: float) -> PyOpenSCAD:
    """Creates a d8 octahedron shape for use in games.

    Usage::

        Octahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    return pysolidfive.octahedron(size=size).color(default_material_colour)


def Icosahedron(size: float) -> PyOpenSCAD:
    """Creates a d20 icosahedron shape for use in games.

    Usage::

        Icosahedron(10)

    Args:
        size: diameter of the circumscribed sphere
    """
    # The classic three-golden-rectangles construction (what the original hull()ed out of three
    # thin cubes): the 12 vertices are the cyclic permutations of (0, +-e/2, +-e*phi/2).
    phi = 0.5 * (math.sqrt(5) + 1)
    edge_length = size / 2 / 0.951
    a, b = edge_length / 2, edge_length * phi / 2
    pts = []
    for sa in (-a, a):
        for sb in (-b, b):
            pts.extend([[0, sa, sb], [sb, 0, sa], [sa, sb, 0]])
    return pysolidfive.convex_polyhedron(pts).color(default_material_colour)


def _trapezohedron_vertices(size: float) -> tuple[list[list[float]], float, float]:
    """The d10 trapezohedron's vertices, mirroring BOSL2's _trapezohedron() math for the
    parameters the original code used (faces=10, d=size, h=size/2): two rings of 5 vertices at
    radius size/2 offset by 36 degrees and separated by `separation` in z, plus two apexes at
    +-h. Returns (vertices, ring_separation, apex_height)."""
    n = 5
    r = size / 2
    h = size / 2
    separation = 2 * h * math.tan(math.radians(90 / n)) ** 2
    top = [
        [r * math.cos(math.radians(360 / n * i)), r * math.sin(math.radians(360 / n * i)), separation / 2]
        for i in range(n)
    ]
    bot = [
        [
            r * math.cos(math.radians(180 / n + 360 / n * i)),
            r * math.sin(math.radians(180 / n + 360 / n * i)),
            -separation / 2,
        ]
        for i in range(n)
    ]
    return [[0, 0, h], [0, 0, -h]] + top + bot, separation, h


def Trapezohedron(size: float, length_mod: float = 0, children: PyOpenSCAD | None = None) -> PyOpenSCAD:
    """Creates a d10 trapezohedron shape for use in games.

    Usage::

        Trapezohedron(10)
        Trapezohedron(20, children=text3d)  # with face labels as children

    Args:
        size:       diameter of the circumscribed sphere
        length_mod: modification to the length (default 0, unused -- kept for API
                    compatibility with the original SCAD module)
        children:   optional child solid to subtract at each kite face, oriented with its +z
                    axis along the face normal and positioned at the face centroid (an
                    engraved-label workflow). Note: the original SCAD module's per-face
                    fine-rotation (-30/15/240 degrees depending on $faceindex) isn't
                    reproduced.
    """
    pts, separation, h = _trapezohedron_vertices(size)
    base = pysolidfive.convex_polyhedron(pts).color(default_material_colour)
    if children is None:
        return base

    # Kite faces: the upper ones run top-apex -> top_i -> bot_i -> top_{i+1}; the lower ones
    # bottom-apex -> bot_i -> top_{i+1} -> bot_{i+1} (indices into the ring lists).
    top_apex, bot_apex = pts[0], pts[1]
    top = pts[2:7]
    bot = pts[7:12]
    faces = []
    for i in range(5):
        faces.append([top_apex, top[i], bot[i], top[(i + 1) % 5]])
        faces.append([bot_apex, bot[i], top[(i + 1) % 5], bot[(i + 1) % 5]])

    result = base
    for face in faces:
        cx = sum(p[0] for p in face) / 4
        cy = sum(p[1] for p in face) / 4
        cz = sum(p[2] for p in face) / 4
        ux = [face[1][i] - face[0][i] for i in range(3)]
        vx = [face[2][i] - face[0][i] for i in range(3)]
        nx = [ux[1] * vx[2] - ux[2] * vx[1], ux[2] * vx[0] - ux[0] * vx[2], ux[0] * vx[1] - ux[1] * vx[0]]
        nlen = math.sqrt(sum(v * v for v in nx))
        n = [v / nlen for v in nx]
        if n[0] * cx + n[1] * cy + n[2] * cz < 0:
            n = [-v for v in n]
        # Rotate the child's +z onto the face normal, then move to the centroid.
        dot = max(-1.0, min(1.0, n[2]))
        angle = math.degrees(math.acos(dot))
        axis = [-n[1], n[0], 0]
        if math.hypot(axis[0], axis[1]) < 1e-9:
            axis = [1, 0, 0]
        piece = children.rotate(angle, axis).translate([cx, cy, cz])
        result = result - piece
    return result
