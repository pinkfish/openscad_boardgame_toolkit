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

# LibFile: bosl2/vnf.py
#    Minimal pure-Python port of BOSL2's VNF ("Vertices and Faces") structure
#    from vnf.scad -- just the pieces the bezier surface functions
#    (bosl2/beziers.py's BezierPatch) need to turn a grid of surface sample
#    points into a polyhedron: vnf_vertex_array() (grid -> VNF with the quad
#    subdivision styles), vnf_join() (merge VNFs), and rendering to PythonSCAD's
#    native polyhedron(). No osuse()/BOSL2 runtime dependency.
#
#    A VNF is [vertices, faces]: vertices a list of 3-D points, faces a list of
#    index lists (each a polygon into `vertices`). That maps straight onto
#    OpenSCAD's polyhedron(points=, faces=). The class carries the pair and, like
#    Path/Bezier, keeps every operation as a method.
#
# FileSummary: VNF (vertices+faces) surface structure and grid meshing (BOSL2 vnf.scad).
# FileGroup: BOSL2

import numpy as np

_EPS = 1e-9


def _count(n: int, s: int = 0, reverse: bool = False) -> list:
    r = list(range(s, s + n))
    return r[::-1] if reverse else r


def _lofttri(p1, p2, i1off: int, i2off: int, n1: int, n2: int, reverse: bool, trimax) -> list:
    """Triangulate between two rows (possibly unequal length) by shortest new edge (BOSL2 _lofttri)."""
    a1 = np.asarray(p1, dtype=float)
    a2 = np.asarray(p2, dtype=float)
    tris: list = []
    if n1 != n2:
        i1 = i2 = 0
        tc1 = tc2 = 0
        while True:
            t1 = i1 + 1 if i1 < n1 else n1
            t2 = i2 + 1 if i2 < n2 else n2
            d12 = 9e9 if t2 >= n2 else float(np.linalg.norm(a2[t2] - a1[i1]))
            d21 = 9e9 if t1 >= n1 else float(np.linalg.norm(a1[t1] - a2[i2]))
            userow = (2 if tc1 < trimax else 1) if d12 < d21 else (1 if tc2 < trimax else 2)
            newt = (t1 if t1 < n1 else i1) if userow == 1 else (t2 if t2 < n2 else i2)
            newofft = i2off + newt if userow == 2 else i1off + newt
            tc1n = tc1 + 1 if (d12 < d21 and tc1 < trimax) else 0
            tc2n = tc2 + 1 if (d21 < d12 and tc2 < trimax) else 0
            triangle = [i1off + i1, i2off + i2, newofft] if reverse else [i2off + i2, i1off + i1, newofft]
            if t1 >= n1 and t2 >= n2:
                break
            tris.append(triangle)
            if userow == 1:
                i1 = i1 if t1 >= n1 else t1
            else:
                i2 = i2 if t2 >= n2 else t2
            tc1, tc2 = tc1n, tc2n
    else:
        n = n1
        i = 0
        while True:
            t = i + 1 if i < n else n
            if t >= n:
                break
            d12 = float(np.linalg.norm(a2[t] - a1[i]))
            d21 = float(np.linalg.norm(a1[t] - a2[i]))
            third1 = i2off + t if d12 < d21 else i1off + t
            third2 = i1off + i if d12 < d21 else i2off + i
            if reverse:
                tris.append([i1off + i, i2off + i, third1])
                tris.append([i2off + t, i1off + t, third2])
            else:
                tris.append([i2off + i, i1off + i, third1])
                tris.append([i1off + t, i2off + t, third2])
            i = t
    return tris


class VNF:
    """A VNF surface: ``vertices`` (3-D points) plus ``faces`` (index polygons into vertices).

    Renders to PythonSCAD's native ``polyhedron`` via :meth:`polyhedron`. Build one from a
    rectangular grid of sample points with :meth:`vertex_array`, and merge several with
    :meth:`join`.

    Args:
        vertices: list of [x, y, z] points
        faces:    list of index lists (each polygon into *vertices*)

    Examples:
        Meshing a bumpy grid of sample points into a surface and rendering it as a polyhedron:

        .. pythonscad-example::

            grid = [[[x, y, 4 * math.sin(x / 6) * math.cos(y / 6)] for y in range(0, 60, 4)]
                    for x in range(0, 60, 4)]
            VNF.vertex_array(grid).polyhedron().show()
    """

    def __init__(self, vertices=(), faces=()) -> None:
        self.vertices = [[float(x) for x in v] for v in vertices]
        self.faces = [[int(i) for i in f] for f in faces]

    def __repr__(self) -> str:
        return f"VNF({len(self.vertices)} verts, {len(self.faces)} faces)"

    def __bool__(self) -> bool:
        return len(self.faces) > 0

    def bounds(self) -> np.ndarray:
        """[[min_x, min_y, min_z], [max_x, max_y, max_z]]."""
        arr = np.asarray(self.vertices, dtype=float)
        return np.array([arr.min(axis=0), arr.max(axis=0)])

    def reverse(self) -> "VNF":
        """A copy with every face wound the other way (flips the surface normals)."""
        return VNF(self.vertices, [f[::-1] for f in self.faces])

    def volume(self) -> float:
        """Signed enclosed volume (BOSL2 vnf_volume()); negative when the faces wind inward.

        Used to detect and fix inverted meshes (a swept/skinned surface whose winding came out
        inside-out): ``vnf if vnf.volume() >= 0 else vnf.reverse()``."""
        if not self.faces:
            return 0.0
        v = np.asarray(self.vertices, dtype=float)
        total = 0.0
        for f in self.faces:  # fan-triangulate each (possibly n-gon) face
            a = v[f[0]]
            for k in range(1, len(f) - 1):
                total += float(np.dot(a, np.cross(v[f[k]], v[f[k + 1]])))
        return total / 6.0

    @staticmethod
    def join(vnfs) -> "VNF":
        """Merge a list of VNFs into one, offsetting each VNF's face indices (BOSL2 vnf_join())."""
        vnfs = list(vnfs)
        if len(vnfs) == 1:
            return vnfs[0]
        verts: list = []
        faces: list = []
        off = 0
        for v in vnfs:
            for f in v.faces:
                if len(f) >= 3:
                    faces.append([off + j for j in f])
            verts.extend(v.vertices)
            off += len(v.vertices)
        return VNF(verts, faces)

    @classmethod
    def vertex_array(cls, points, caps=None, cap1=None, cap2=None, col_wrap: bool = False,
                     row_wrap: bool = False, reverse: bool = False, style: str = "default") -> "VNF":
        """Build a VNF from a rectangular grid of 3-D points (BOSL2 vnf_vertex_array()).

        Each grid cell becomes triangles (or a quad) chosen by *style*: "default", "alt",
        "min_edge", "min_area", "convex", "concave", "quincunx", "quad", "flip1", "flip2".
        *col_wrap*/*row_wrap* close the grid into a tube/torus; *caps*/*cap1*/*cap2* close the
        column-wrapped ends; *reverse* flips face winding. Degenerate (zero-area) faces are dropped.
        """
        assert style in ("default", "alt", "min_edge", "min_area", "convex", "concave",
                         "quincunx", "quad", "flip1", "flip2"), f"unknown style {style!r}"
        grid = [[[float(x) for x in p] for p in row] for row in points]
        rows = len(grid)
        if rows == 0:
            return cls([], [])
        cols = len(grid[0])
        if rows <= 1 or cols <= 1:
            return cls([], [])

        cap1 = cap1 if cap1 is not None else (caps if caps is not None else False)
        cap2 = cap2 if cap2 is not None else (caps if caps is not None else False)
        if (cap1 or cap2) and not col_wrap:
            raise AssertionError("col_wrap must be true if caps are requested")
        if (cap1 or cap2) and row_wrap:
            raise AssertionError("cannot combine caps with row_wrap")

        pts = [p for row in grid for p in row]  # flattened, row-major
        parr = np.asarray(pts, dtype=float)
        pcnt = len(pts)
        colcnt = cols - (0 if col_wrap else 1)
        rowcnt = rows - (0 if row_wrap else 1)

        def idx(r, c):
            return (r % rows) * cols + (c % cols)

        verts = [list(p) for p in pts]
        if style == "quincunx":
            for r in range(rowcnt):
                for c in range(colcnt):
                    corners = parr[[idx(r, c), idx(r + 1, c), idx(r + 1, c + 1), idx(r, c + 1)]]
                    verts.append(corners.mean(axis=0).tolist())

        vertsarr = np.asarray(verts, dtype=float)
        faces: list = []
        if cap1:
            faces.append(_count(cols, 0, reverse=not reverse))
        if cap2:
            faces.append(_count(cols, (rows - 1) * cols, reverse=reverse))

        for r in range(rowcnt):
            for c in range(colcnt):
                i1, i2, i3, i4 = idx(r, c), idx(r + 1, c), idx(r + 1, c + 1), idx(r, c + 1)
                p1, p2, p3, p4 = parr[i1], parr[i2], parr[i3], parr[i4]
                if style == "quincunx":
                    i5 = pcnt + r * colcnt + c
                    cell = [[i1, i5, i2], [i2, i5, i3], [i3, i5, i4], [i4, i5, i1]]
                elif style == "min_area":
                    area42 = np.linalg.norm(np.cross(p2 - p1, p4 - p1)) + np.linalg.norm(np.cross(p4 - p3, p2 - p3))
                    area13 = np.linalg.norm(np.cross(p1 - p4, p3 - p4)) + np.linalg.norm(np.cross(p3 - p2, p1 - p2))
                    cell = [[i1, i4, i2], [i2, i4, i3]] if area42 < area13 + _EPS else [[i1, i3, i2], [i1, i4, i3]]
                elif style == "min_edge":
                    d42 = np.linalg.norm(p4 - p2)
                    d13 = np.linalg.norm(p1 - p3)
                    cell = [[i1, i4, i2], [i2, i4, i3]] if d42 < d13 + _EPS else [[i1, i3, i2], [i1, i4, i3]]
                elif style in ("convex", "concave"):
                    n = (-1 if reverse else 1) * np.cross(p2 - p1, p3 - p1)
                    if not np.any(n):
                        cell = [[i1, i4, i3]]
                    else:
                        above = (n @ p4 > n @ p1) if style == "convex" else (n @ p4 <= n @ p1)
                        cell = [[i1, i4, i2], [i2, i4, i3]] if above else [[i1, i3, i2], [i1, i4, i3]]
                elif style == "quad":
                    cell = [[i1, i2, i3, i4]]
                elif style == "alt" or (style == "flip1" and (r + c) % 2 == 0) or (style == "flip2" and (r + c) % 2 == 1):
                    cell = [[i1, i4, i2], [i2, i4, i3]]
                else:  # default
                    cell = [[i1, i3, i2], [i1, i4, i3]]
                for face in cell:
                    a, b, cc = vertsarr[face[0]], vertsarr[face[1]], vertsarr[face[2]]
                    if np.linalg.norm(np.cross(b - a, cc - a)) > _EPS:  # drop degenerate faces
                        faces.append(face[::-1] if reverse else face)
        return cls(verts, faces)

    @classmethod
    def tri_array(cls, points, caps=None, cap1=None, cap2=None, col_wrap: bool = False,
                  row_wrap: bool = False, reverse: bool = False, limit_bunching: bool = True) -> "VNF":
        """Build a VNF from an array of rows whose lengths may differ (BOSL2 vnf_tri_array()).

        Triangulates between adjacent rows by repeatedly adding the shortest new edge, so it
        meshes triangular / irregular point arrays (what the degenerate bezier patches produce).
        """
        if (caps or cap1 or cap2) and row_wrap:
            raise AssertionError("cannot combine caps with row_wrap")
        plen = len(points)
        st = []
        for row in points:
            row = [list(p) for p in row]
            if col_wrap and not np.array_equal(row[0], row[-1]):
                row = row + [list(row[0])]
            st.append(row)
        addcol = (len(st[0]) - len(points[0])) if col_wrap else 0
        rowstarts = [len(r) for r in st]
        pcumlen = [0]
        for n in rowstarts:
            pcumlen.append(pcumlen[-1] + n)
        capfirst = cap1 if cap1 is not None else (caps if caps is not None else False)
        caplast = cap2 if cap2 is not None else (caps if caps is not None else False)

        faces: list = []
        if capfirst:
            rng = list(range(0, rowstarts[0] - addcol)) if reverse else list(range(rowstarts[0] - 1 - addcol, -1, -1))
            faces.append(rng)
        for i in range(0, plen - 1 + (1 if row_wrap else 0)):
            j = (i + 1) % plen
            trimax = max(1, abs(len(st[i]) - len(st[j]))) if limit_bunching else float("inf")
            faces.extend(_lofttri(st[i], st[j], pcumlen[i], pcumlen[j], rowstarts[i], rowstarts[j], reverse, trimax))
        if caplast:
            if reverse:
                rng = list(range(pcumlen[plen] - 1 - addcol, pcumlen[plen - 1] - 1, -1))
            else:
                rng = list(range(pcumlen[plen - 1], pcumlen[plen] - addcol))
            faces.append(rng)
        verts = [p for row in st for p in row]
        return cls(verts, faces)

    def polyhedron(self):
        """Native geometry for this VNF via PythonSCAD's ``polyhedron(points=, faces=)``."""
        from pythonscad import polyhedron as _polyhedron

        pts = [[float(x) for x in v] for v in self.vertices]
        faces = [[int(i) for i in f] for f in self.faces]
        return _polyhedron(points=pts, faces=faces, convexity=10)

    def geometry(self):
        """Alias of :meth:`polyhedron`, matching Path/Region's geometry() surface."""
        return self.polyhedron()
