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

# LibFile: bosl2/shapes3d.py
#    Every shape in this file (cube, cuboid, prismoid, octahedron, wedge, cylinder, cyl, xcyl,
#    ycyl, zcyl, sphere, spheroid, rect_tube, tube, pie_slice, torus, teardrop, onion, text3d,
#    path_text, interior_fillet, heightfield, cylindrical_heightfield, ruler) is a pure-Python
#    port with no osuse()/BOSL2 runtime dependency at all: each shape is built directly from
#    openscad primitives (cube()/cylinder()/sphere()/polyhedron()/hull()/minkowski()/
#    rotate_extrude()/linear_extrude()/text()) rather than delegating to BOSL2. cuboid()'s edge
#    rounding/chamfering mirrors BOSL2's own algorithm, which is itself CSG composition (union/
#    intersection/difference/hull of primitive shapes at each corner), not raw polyhedron mesh
#    math -- see BOSL2's shapes3d.scad module cuboid() for the reference algorithm this was
#    ported from. heightfield()/cylindrical_heightfield() build their mesh directly via
#    polyhedron() from a computed vertex/face grid (see _heightfield_polyhedron()).
#
# FileSummary: Attachable cubes, cylinders, spheres, text and rulers (BOSL2 shapes3d.scad).
# FileGroup: BOSL2

from __future__ import annotations

from collections.abc import Sequence
import math

import numpy as np

from pythonscad import (
    cube as _ocube,
    cylinder as _ocylinder,
    sphere as _osphere,
    polyhedron as _opolyhedron,
    hull as _ohull,
    minkowski as _ominkowski,
    rotate_extrude as _orotate_extrude,
    textmetrics as _otextmetrics,
)
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from .constants import *
from .shapes2d import _frag_count, _pick_radius, text as _text2d
from bosl2.geometry import cross
from bosl2.vectors import unit, is_vector
from bosl2.paths import Path
from bosl2.distributors import Distributable
from bosl2.color import Colorable
from bosl2.partitions import Partitionable
from bosl2.miscellaneous import Miscellaneous


# ---------------------------------------------------------------------------
# Section: Base class
# ---------------------------------------------------------------------------


class Bosl2Solid(Distributable, Colorable, Partitionable, Miscellaneous):
    """Wraps a PyOpenSCAD solid together with the geometry metadata (nominal `size` and
    `anchor`) that BOSL2's $parent_geom attachment system would otherwise track, so that
    edge/corner/face masking (bosl2/masking.py) work as plain chained methods instead of
    needing size=/anchor= threaded through by hand at every call site. Every function in this
    file returns an instance of this class (or a subclass).

    Every geometry method (translate/rotate/mirror/multmatrix/scale/color, the union/intersection/
    difference CSG operators) delegates to the wrapped native shape and returns a new Bosl2Solid carrying the
    same size/anchor metadata forward. Any other method not explicitly listed here (e.g.
    resize(), offset()) falls through via __getattr__ to the native shape and returns its raw,
    *unwrapped* result, since we can't know whether the size/anchor metadata still applies.

    Only cuboid()-shaped objects (cube(), cuboid() -- the only ones in this file with a genuine
    axis-aligned box `size`) support the masking methods; every other shape (prismoid, wedge,
    octahedron, the cylinder family, the sphere family) carries size=None and will assert if a
    masking method is called on it, since bosl2/masking.py's edge/corner positioning math only
    supports cuboid parents.

    CAVEAT: this is a plain Python wrapper (composition), not a subclass of the real native
    PyOpenSCAD C-extension type -- there was no way to verify from this environment whether
    that type even supports subclassing. Calling a method on a Bosl2Solid (`shape.translate(...)`,
    `shape.edge_profile(...)`) is safe. But if a Bosl2Solid is ever passed *directly* as a bare
    argument into a function that expects a native geometry object -- `hull(a, b)`,
    `minkowski(a, b)` -- rather than having a method called on it, the receiving function needs
    the raw native object: use `.shape` to unwrap explicitly.
    """

    def __init__(self, shape: PyOpenSCAD, size: Sequence[float] | None = None, anchor: "Sequence[float] | str | None" = None):
        self.shape = shape
        self.size = size
        self.anchor = anchor if anchor is not None else CENTER

    @staticmethod
    def _unwrap(x):
        return x.shape if isinstance(x, Bosl2Solid) else x

    def _wrap(self, new_shape: PyOpenSCAD) -> "Bosl2Solid":
        return Bosl2Solid(new_shape, self.size, self.anchor)

    def __getattr__(self, name):
        attr = getattr(self.shape, name)
        return attr

    def __repr__(self) -> str:
        return f"Bosl2Solid({self.shape!r}, size={self.size!r}, anchor={self.anchor!r})"

    # ---- geometry passthrough, preserving size/anchor metadata ----

    def translate(self, v: Sequence[float]) -> "Bosl2Solid":
        return self._wrap(self.shape.translate(v))

    move = translate

    def rotate(self, *a, **k) -> "Bosl2Solid":
        return self._wrap(self.shape.rotate(*a, **k))

    rot = rotate

    def mirror(self, v: Sequence[float]) -> "Bosl2Solid":
        return self._wrap(self.shape.mirror(v))

    # Directional translates (BOSL2 transforms.scad): right/left +/-X, back/fwd +/-Y, up/down +/-Z.

    def right(self, x: float) -> "Bosl2Solid":
        return self.translate([x, 0.0, 0.0])

    def left(self, x: float) -> "Bosl2Solid":
        return self.translate([-x, 0.0, 0.0])

    def back(self, y: float) -> "Bosl2Solid":
        return self.translate([0.0, y, 0.0])

    def forward(self, y: float) -> "Bosl2Solid":
        return self.translate([0.0, -y, 0.0])

    fwd = forward

    def up(self, z: float) -> "Bosl2Solid":
        return self.translate([0.0, 0.0, z])

    def down(self, z: float) -> "Bosl2Solid":
        return self.translate([0.0, 0.0, -z])

    def multmatrix(self, m: Sequence[Sequence[float]]) -> "Bosl2Solid":
        return self._wrap(self.shape.multmatrix(m))

    def scale(self, v) -> "Bosl2Solid":
        return self._wrap(self.shape.scale(v))

    # ---- native-only mesh operations (no BOSL2 equivalent) ----
    #
    # PythonSCAD provides several solid operations that BOSL2 has no counterpart for; they are
    # exposed here as first-class Bosl2Solid methods (re-wrapping the native result so anchoring
    # metadata and fluent chaining survive) rather than leaking raw native handles through
    # __getattr__. These execute only inside the real PythonSCAD app; under the numeric test mock
    # they degrade to identity/AABB stand-ins (see mock_libfive.py), so the fast suite still runs
    # and their real geometry is covered by the STL render tests.

    def repair(self) -> "Bosl2Solid":
        """Force the mesh watertight, healing gaps/non-manifold edges (native ``repair()``)."""
        return self._wrap(self.shape.repair())

    def wrap(self, r: float, _fn: float | None = None) -> "Bosl2Solid":
        """Wrap this solid around a cylinder of radius *r*, bending +X into the cylinder's
        circumference (native ``wrap()``). *_fn* sets the facet count of the bend."""
        if _fn is not None:
            return self._wrap(self.shape.wrap(r=float(r), fn=float(_fn)))
        return self._wrap(self.shape.wrap(r=float(r)))

    def pull(self, direction: "Sequence[float] | np.ndarray", distance: float) -> "Bosl2Solid":
        """Pull the part of the solid on the +*direction* side apart by *distance*, stretching the
        material between (native ``pull()``)."""
        return self._wrap(self.shape.pull([float(x) for x in direction], float(distance)))

    def oversample(self, n: int) -> "Bosl2Solid":
        """Subdivide every mesh facet *n*-fold, e.g. before :meth:`wrap` so the bend is smooth
        (native ``oversample()``)."""
        return self._wrap(self.shape.oversample(int(n)))

    def separate(self) -> "list[Bosl2Solid]":
        """Split a solid made of disconnected lumps into a list of its connected components
        (native ``separate()``)."""
        return [self._wrap(part) for part in self.shape.separate()]

    def inside(self, point: "Sequence[float] | np.ndarray") -> bool:
        """True if *point* lies inside the solid (native ``inside()``)."""
        return bool(self.shape.inside([float(x) for x in point]))

    # ---- colour (bosl2/color.py) ----
    #
    # The color.scad operators (color/recolor/color_this/hsl/hsv/highlight/ghost) come from the
    # Colorable mixin, which resolves to these native primitives: PythonSCAD's color(),
    # highlight() (the # modifier) and background() (the % / ghost modifier).

    def _color_native(self, c=None, alpha=None) -> "Bosl2Solid":
        args = () if c is None else (c,)
        kw = {} if alpha is None else {"alpha": alpha}
        return self._wrap(self.shape.color(*args, **kw))

    def _highlight_native(self) -> "Bosl2Solid":
        return self._wrap(self.shape.highlight())

    def _ghost_native(self) -> "Bosl2Solid":
        return self._wrap(self.shape.background())

    def __or__(self, other) -> "Bosl2Solid":
        return self._wrap(self.shape | Bosl2Solid._unwrap(other))

    def __and__(self, other) -> "Bosl2Solid":
        return self._wrap(self.shape & Bosl2Solid._unwrap(other))

    def __sub__(self, other) -> "Bosl2Solid":
        return self._wrap(self.shape - Bosl2Solid._unwrap(other))

    def __ror__(self, other) -> "Bosl2Solid":
        return self._wrap(Bosl2Solid._unwrap(other) | self.shape)

    def __rand__(self, other) -> "Bosl2Solid":
        return self._wrap(Bosl2Solid._unwrap(other) & self.shape)

    def __rsub__(self, other) -> "Bosl2Solid":
        return self._wrap(Bosl2Solid._unwrap(other) - self.shape)

    # ---- distributors (bosl2/distributors.py) ----
    #
    # The distributors.scad copiers, inherited from Distributable, resolve to _distribute(), which
    # for a solid means: multmatrix a copy for each transform and union them into one new solid.
    # This reuses the wrapped native handle across the copies, which is safe for direct-CSG solids
    # (the norm here); a pysolidfive/frep-backed shape must instead be distributed via a factory to
    # avoid the frep handle-reuse segfault (see the SDF-vs-direct note in CLAUDE.md).

    def _distribute(self, mats) -> "Bosl2Solid":
        """Union a multmatrix copy of this solid for each transform matrix (BOSL2's module form)."""
        assert len(mats), "distributor produced no copies."
        out = self.shape.multmatrix(np.asarray(mats[0]).tolist())
        for m in mats[1:]:
            out = out | self.shape.multmatrix(np.asarray(m).tolist())
        return self._wrap(out)

    # ---- bounding-box anchoring (works on ANY object, via PythonSCAD's native bbox) ----
    #
    # PythonSCAD exposes obj.position (min corner) / obj.size (extent) / obj.bbox (a solid),
    # each computed by actually meshing the object. That lets anchoring/attachment/masking
    # find where an anchor point is on ANY object without the caller passing a size -- BOSL2
    # normally threads $parent_geom through for this. Tracked cuboid size/anchor metadata,
    # when present, is used first as a no-meshing fast path.

    def _native_bounds(self) -> "tuple[list[float], list[float]] | None":
        """The object's axis-aligned bounding box as (mincorner, size), read from the native
        obj.position/obj.size. Returns None when those accessors aren't available (the numeric
        test mock) or the geometry is empty/degenerate (native returns None)."""
        try:
            pos = self.shape.position
            sz = self.shape.size
        except Exception:
            return None
        if pos is None or sz is None:
            return None
        try:
            mincorner = [float(pos[i]) for i in range(3)]
            size = [float(sz[i]) for i in range(3)]
        except (TypeError, IndexError, ValueError):
            return None
        return mincorner, size

    def bounds(self) -> "tuple[list[float], list[float]]":
        """This object's axis-aligned bounding box as (center, size) -- both plain [x, y, z]
        float lists in the object's CURRENT coordinate frame (after any translate/rotate/CSG).

        Prefers the native bbox, which always reflects the actual current geometry -- this is
        what lets anchoring/attachment/masking work without the caller tracking a size, and
        stays correct after the object has been moved or combined (tracked size/anchor metadata
        would be stale there). Falls back to the tracked cuboid size/anchor metadata only when
        the native accessors aren't available (the numeric test mock), where it assumes the box
        is still at its construction position. Raises if neither is available."""
        nb = self._native_bounds()
        if nb is not None:
            mincorner, size = nb
            return [mincorner[i] + size[i] / 2 for i in range(3)], size
        if self.size is not None and not isinstance(self.anchor, str):
            size = [float(v) for v in self.size]
            return _anchor_offset_box3(size, self.anchor), size
        raise ValueError(
            "bounds(): object has no native bounding box and no tracked cuboid size/anchor "
            "metadata (are you calling this under the numeric mock on a non-cuboid?)"
        )

    def _resolve_bounds(self, bbox=None) -> "tuple[list[float], list[float]]":
        """(center, size) for anchoring: from a passed-in *bbox* override if given, else the
        object's native bounding box (:meth:`bounds`).

        *bbox* overrides the object's own box -- useful when the native bbox is wrong for the
        purpose (a shape with an overhang, a mask positioned against a nominal box, or a cheap way
        to skip the meshing the native bbox needs). It is a min/max corner pair
        ``[[min_x, min_y, min_z], [max_x, max_y, max_z]]`` (the same shape :meth:`Path.bounds` and
        the native ``obj.bbox`` use)."""
        if bbox is None:
            return self.bounds()
        arr = np.asarray(bbox, dtype=float)
        assert arr.shape == (2, 3), "bbox must be [[min_x,min_y,min_z],[max_x,max_y,max_z]]."
        lo, hi = arr[0], arr[1]
        assert bool(np.all(hi >= lo - 1e-12)), "bbox must be [[min...],[max...]] with max >= min."
        return [(lo[i] + hi[i]) / 2 for i in range(3)], [hi[i] - lo[i] for i in range(3)]

    def anchor_point(self, anchor: Sequence[float], bbox=None) -> list[float]:
        """The [x, y, z] point on this object's bounding box for the given anchor vector, in the
        object's current coordinate frame: center + anchor * size / 2. Works on any object.

        Pass *bbox* to anchor against a supplied box instead of the object's own (see
        :meth:`_resolve_bounds`)."""
        center, size = self._resolve_bounds(bbox)
        a = list(anchor)
        return [center[i] + a[i] * size[i] / 2 for i in range(3)]

    def reanchor(self, anchor: Sequence[float], bbox=None) -> "Bosl2Solid":
        """Return this object translated so its bounding-box `anchor` point sits at the origin.
        Re-anchors any object by its bbox after the fact (cube()/cuboid() only do this at
        construction, and only for cuboids). Pass *bbox* to use a supplied box."""
        p = self.anchor_point(anchor, bbox=bbox)
        moved = self.translate([-p[0], -p[1], -p[2]])
        if moved.size is not None:
            moved.anchor = list(anchor)
        return moved

    def position(self, anchor: Sequence[float], child, bbox=None) -> "Bosl2Solid":
        """BOSL2 position(): place `child` so its local origin lands on this object's
        bounding-box `anchor` point, keeping the child's own orientation, and return self
        unioned with the placed child. `child` may be a Bosl2Solid or a raw native solid."""
        p = self.anchor_point(anchor, bbox=bbox)
        placed = Bosl2Solid._unwrap(child).translate(p)
        # Untracked result: bounds() on it queries the true combined bbox rather than the
        # parent box, so a chained attach/position builds on the combined shape.
        return Bosl2Solid(self.shape | placed)

    def align(
        self,
        anchor: Sequence[float],
        child,
        align: Sequence[float] | None = None,
        inside: bool = False,
        overlap: float = 0.0,
        bbox=None,
    ) -> "Bosl2Solid":
        """BOSL2 align(): place `child` on this object's `anchor` face and return self unioned
        with it. Like attach() it mates a child face to a parent face, but WITHOUT reorienting
        the child -- the child keeps its own axes and is merely translated.

        With `align` omitted the child is centered on the face, sitting OUTSIDE the parent
        (inside=False, the default) or tucked inside (inside=True). Pass `align` (an edge/corner
        direction within the face, e.g. RIGHT for the +x edge) to sit the child flush against
        that edge/corner instead -- matching BOSL2 align()'s anchor+align pair. Both anchor
        points come from the native bounding boxes, so no size needs to be passed.

        Args:
            anchor:  the parent face to place the child on (e.g. TOP)
            child:   the solid to place (Bosl2Solid or raw native solid)
            align:   edge/corner within the face to sit flush against (default: centered)
            inside:  place the child inside the parent instead of outside (default False)
            overlap: pull the child toward the parent along the face normal by this much
        """
        face = list(anchor)
        edge = [0.0, 0.0, 0.0] if align is None else list(align)
        factor = -1.0 if inside else 1.0
        csolid = child if isinstance(child, Bosl2Solid) else Bosl2Solid(child)
        # The child's own mating anchor: its face opposite the parent face (so it sits on the
        # outside), shifted to the aligned edge/corner. Matches BOSL2's thisedge - factor*thisface.
        child_anchor = [edge[i] - factor * face[i] for i in range(3)]
        cpt = csolid.anchor_point(child_anchor)
        dest = self.anchor_point([face[i] + edge[i] for i in range(3)], bbox=bbox)
        fdir = list(unit(face)) if any(face) else [0.0, 0.0, 0.0]
        ov = -overlap if inside else overlap
        placed = csolid.translate([dest[i] - cpt[i] - fdir[i] * ov for i in range(3)])
        return Bosl2Solid(self.shape | placed.shape)

    def attach(
        self,
        parent_anchor: Sequence[float],
        child,
        child_anchor: Sequence[float] | None = None,
        overlap: float = 0.0,
        spin: float = 0.0,
        bbox=None,
    ) -> "Bosl2Solid":
        """BOSL2 attach(): orient and place `child` so its `child_anchor` face mates flush
        against this object's `parent_anchor` face, then return self unioned with the placed
        child. Both anchor points come from the native bounding boxes, so neither object needs
        its size passed explicitly.

        Args:
            parent_anchor: which face of self to attach to (e.g. TOP)
            child:         the solid to attach (Bosl2Solid or raw native solid)
            child_anchor:  which face of the child mates against it (default: the child's
                           face OPPOSITE parent_anchor, so the two mate naturally)
            overlap:       pull the child in by this much along the mating axis (default 0)
            spin:          spin the child about the mating axis, in degrees (default 0)
        """
        pa = list(parent_anchor)
        ca = [-a for a in pa] if child_anchor is None else list(child_anchor)
        csolid = child if isinstance(child, Bosl2Solid) else Bosl2Solid(child)
        # 1. bring the child's mating face to the origin
        cpt = csolid.anchor_point(ca)
        placed = csolid.translate([-cpt[0], -cpt[1], -cpt[2]])
        # 2. rotate so the child's mating-face direction points opposite the parent's face
        angle, axis = _rot_from_to(ca, [-a for a in pa])
        if angle:
            placed = placed.rotate(angle, axis)
        # 3. optional spin about the mating (parent-face) axis
        if spin and any(pa):
            placed = placed.rotate(spin, list(unit(pa)))
        # 4. move onto the parent's anchor point, pulling in by `overlap`
        ppt = self.anchor_point(pa, bbox=bbox)
        pdir = list(unit(pa)) if any(pa) else [0.0, 0.0, 0.0]
        placed = placed.translate([ppt[i] - pdir[i] * overlap for i in range(3)])
        return Bosl2Solid(self.shape | placed.shape)

    def reorient(self, anchor: Sequence[float] = CENTER, spin: float = 0,
                 orient: Sequence[float] = UP, bbox=None) -> "Bosl2Solid":
        """Reorient this already-built object by its bounding box (BOSL2 reorient()).

        Moves the bounding-box *anchor* point to the origin, spins *spin* degrees about Z, then
        rotates the object's UP toward *orient*. The size comes from the native bbox, so -- unlike
        BOSL2's function form -- you never pass it. cube()/cuboid()/etc. take anchor/spin/orient at
        construction; this applies the same transform to any object after the fact. Pass *bbox* to
        reorient against a supplied box instead of the object's own."""
        from bosl2.transforms import reorient as _reorient_matrix

        center, size = self._resolve_bounds(bbox)
        m = _reorient_matrix(anchor=list(anchor), spin=spin, orient=list(orient), size=size)
        centered = self.translate([-center[0], -center[1], -center[2]])
        return centered.multmatrix(np.asarray(m).tolist())

    def orient(self, direction: Sequence[float] = UP, spin: float = 0, bbox=None) -> "Bosl2Solid":
        """Rotate this object so its top (UP) faces *direction* (BOSL2 orient()); uses the bbox."""
        return self.reorient(anchor=CENTER, spin=spin, orient=direction, bbox=bbox)

    # ---- edge/corner/face masking (bosl2/masking.py), box-shaped objects ----
    #
    # These now work on ANY box-shaped object: the cutter size and box center come from
    # bounds() (tracked metadata when available, else the native bbox), so callers no longer
    # have to pass size= or keep the object as a freshly-built cuboid.

    def edge_mask(self, edges: str | list = "ALL", except_edges: list | None = None, children: PyOpenSCAD | None = None, bbox=None) -> "Bosl2Solid":
        from . import masking

        center, size = self._resolve_bounds(bbox)
        return self._wrap(masking.edge_mask(self.shape, edges, except_edges, children, size=size, center=center))

    def edge_profile(
        self, edges: str | list = "ALL", except_edges: list | None = None, children: Sequence[Sequence[float]] | None = None, convexity: int = 10, bbox=None
    ) -> "Bosl2Solid":
        from . import masking

        center, size = self._resolve_bounds(bbox)
        return self._wrap(masking.edge_profile(self.shape, edges, except_edges, children, size=size, convexity=convexity, center=center))

    def edge_profile_asym(
        self, edges: str | list = "ALL", except_edges: list | None = None, children: Sequence[Sequence[float]] | None = None, convexity: int = 10
    ) -> "Bosl2Solid":
        return self.edge_profile(edges, except_edges, children, convexity)

    def corner_profile(
        self,
        corners: str | list = "ALL",
        except_corners: list | None = None,
        r: float | None = None,
        d: float | None = None,
        children: Sequence[Sequence[float]] | None = None,
        convexity: int = 10,
        _fn: float | None = None,
        _fa: float | None = None,
        _fs: float | None = None,
        bbox=None,
    ) -> "Bosl2Solid":
        from . import masking

        center, size = self._resolve_bounds(bbox)
        return self._wrap(
            masking.corner_profile(
                self.shape, corners, except_corners, r, d, size=size, children=children,
                convexity=convexity, center=center, _fn=_fn, _fa=_fa, _fs=_fs,
            )
        )

    def face_profile(
        self,
        faces: str | list = "ALL",
        r: float | None = None,
        d: float | None = None,
        children: Sequence[Sequence[float]] | None = None,
        convexity: int = 10,
        _fn: float | None = None,
        _fa: float | None = None,
        _fs: float | None = None,
        bbox=None,
    ) -> "Bosl2Solid":
        from . import masking

        center, size = self._resolve_bounds(bbox)
        return self._wrap(
            masking.face_profile(
                self.shape, faces, r, d, size=size, children=children,
                convexity=convexity, center=center, _fn=_fn, _fa=_fa, _fs=_fs,
            )
        )


# ---------------------------------------------------------------------------
# Internal helpers (not part of BOSL2's public API)
# ---------------------------------------------------------------------------


def _quantup(x: float, y: float) -> float:
    return math.ceil(x / y) * y


def _orient_rotate(shape: PyOpenSCAD, orient: Sequence[float]) -> PyOpenSCAD:
    o = list(orient)
    if o == [0, 0, 1]:
        return shape
    if o == [0, 0, -1]:
        return shape.rotate(180, [1, 0, 0])
    axis = np.asarray(cross([0, 0, 1], o), dtype=float)
    n = float(np.linalg.norm(axis))
    if n < 1e-12:
        return shape
    axis = (axis / n).tolist()
    ou = unit(o)
    cosang = max(-1.0, min(1.0, ou[2]))
    angle = math.degrees(math.acos(cosang))
    return shape.rotate(angle, axis)


def _rot_from_to(a: Sequence[float], b: Sequence[float]) -> "tuple[float, list[float]]":
    """(angle_degrees, axis) that rotates direction *a* onto direction *b*, for shape.rotate().
    Handles the parallel (no rotation) and antiparallel (180 deg about any perpendicular axis)
    cases. Used by Bosl2Solid.attach() to point a child's mating face at a parent face."""
    au, bu = unit(a), unit(b)
    d = max(-1.0, min(1.0, sum(au[i] * bu[i] for i in range(3))))
    if d > 1 - 1e-9:
        return 0.0, [0.0, 0.0, 1.0]
    if d < -1 + 1e-9:
        axis = cross(au, [1.0, 0.0, 0.0])
        if float(np.linalg.norm(np.asarray(axis, dtype=float))) < 1e-9:
            axis = cross(au, [0.0, 1.0, 0.0])
        return 180.0, list(unit(axis))
    axis = list(unit(cross(au, bu)))
    return math.degrees(math.acos(d)), axis


def _finish3(shape: PyOpenSCAD, offset: Sequence[float], spin: float, orient: Sequence[float]) -> PyOpenSCAD:
    if offset[0] or offset[1] or offset[2]:
        shape = shape.translate(offset)
    if spin:
        shape = shape.rotate(spin, [0, 0, 1])
    return _orient_rotate(shape, orient)


def _anchor_offset_box3(size: Sequence[float], anchor: Sequence[float]) -> list[float]:
    a = list(anchor)
    return [-a[i] * size[i] / 2 for i in range(3)]


def _anchor_offset_hull3(points: Sequence[Sequence[float]], anchor: Sequence[float]) -> list[float]:
    a = list(anchor)
    if a[0] == 0 and a[1] == 0 and a[2] == 0:
        return [0.0, 0.0, 0.0]
    best = max(points, key=lambda p: p[0] * a[0] + p[1] * a[1] + p[2] * a[2])
    return [-best[0], -best[1], -best[2]]


def _anchor_offset_cyl(r1: float, r2: float, length: float, anchor: Sequence[float], axis: int = 2) -> list[float]:
    a = list(anchor)
    az = a[axis]
    r_at = r1 if az < 0 else (r2 if az > 0 else (r1 + r2) / 2)
    radial_axes = [i for i in range(3) if i != axis]
    radial = [a[i] for i in radial_axes]
    rn = math.hypot(*radial)
    if rn > 0:
        radial = [x / rn * r_at for x in radial]
    offset = [0.0, 0.0, 0.0]
    offset[axis] = az * length / 2
    for i, ax in enumerate(radial_axes):
        offset[ax] = radial[i]
    return [-x for x in offset]


def _anchor_offset_sphere(r: float, anchor: Sequence[float]) -> list[float]:
    a = list(anchor)
    n = math.hypot(*a)
    if n == 0:
        return [0.0, 0.0, 0.0]
    return [-a[i] / n * r for i in range(3)]


# --- cuboid() edge-set machinery, mirroring BOSL2 attachments.scad -----------

EDGES_ALL = [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
EDGES_NONE = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

# The vector pointing to the center of each edge of a unit cube; EDGE_OFFSETS[axis][i]
# corresponds to edges[axis][i] in the edge-set representation above.
EDGE_OFFSETS = [
    [[0, -1, -1], [0, 1, -1], [0, -1, 1], [0, 1, 1]],
    [[-1, 0, -1], [1, 0, -1], [-1, 0, 1], [1, 0, 1]],
    [[-1, -1, 0], [1, -1, 0], [-1, 1, 0], [1, 1, 0]],
]

_MAJOR_AXIS_VALID = ["X", "Y", "Z", "ALL", "NONE"]


def _is_edge_array(x) -> bool:
    return isinstance(x, list) and len(x) == 3 and all(isinstance(row, list) and len(row) == 4 for row in x)


def _edge_set(v) -> list[list[int]]:
    if _is_edge_array(v):
        return v
    out = []
    for ax in range(3):
        row = []
        for b in (-1, 1):
            for a in (-1, 1):
                v2 = [[0, a, b], [a, 0, b], [a, b, 0]][ax]
                if isinstance(v, str):
                    if v == "X":
                        matched = ax == 0
                    elif v == "Y":
                        matched = ax == 1
                    elif v == "Z":
                        matched = ax == 2
                    elif v == "ALL":
                        matched = True
                    elif v == "NONE":
                        matched = False
                    else:
                        raise ValueError(f"{v} must be a vector, edge array, or one of {_MAJOR_AXIS_VALID}")
                else:
                    nonz = sum(abs(x) for x in v)
                    if nonz == 2:
                        matched = list(v) == v2
                    else:
                        matches = sum(1 for i in range(3) if v[i] and v[i] == v2[i])
                        matched = matches == (1 if nonz == 1 else 2)
                row.append(1 if matched else 0)
        out.append(row)
    return out


def _is_plain_vector(v) -> bool:
    return isinstance(v, list) and len(v) > 0 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)


def _edges(v, except_: list | None = None) -> list[list[int]]:
    if except_ is None:
        except_ = []
    if v == []:
        return EDGES_NONE
    if isinstance(v, str) or _is_edge_array(v) or _is_plain_vector(v):
        return _edges([v], except_)
    if isinstance(except_, str) or _is_edge_array(except_) or _is_plain_vector(except_):
        return _edges(v, [except_])
    summed = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for x in v:
        es = _edge_set(x)
        for ax in range(3):
            for i in range(4):
                summed[ax][i] += es[ax][i]
    normed = [[1 if summed[ax][i] > 0 else 0 for i in range(4)] for ax in range(3)]
    if not except_:
        return normed
    exc = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for x in except_:
        es = _edge_set(x)
        for ax in range(3):
            for i in range(4):
                exc[ax][i] += es[ax][i]
    return [[1 if (normed[ax][i] - (1 if exc[ax][i] > 0 else 0)) > 0 else 0 for i in range(4)] for ax in range(3)]


def _corner_edges(edges: Sequence[Sequence[float]], v: Sequence[float]) -> list[int]:
    u = [(v[i] + 1) / 2 for i in range(3)]
    return [
        int(edges[0][int(u[1] + u[2] * 2)]),
        int(edges[1][int(u[0] + u[2] * 2)]),
        int(edges[2][int(u[0] + u[1] * 2)]),
    ]


def _rotate_to_axis(shape: PyOpenSCAD, axis: int) -> PyOpenSCAD:
    if axis == 0:
        return shape.rotate(90, [0, 1, 0])
    if axis == 1:
        return shape.rotate(-90, [1, 0, 0])
    return shape


def _trunc_cube(s: Sequence[float], corner: Sequence[float]) -> PyOpenSCAD:
    """A small cube with the corner facing away from *corner* trimmed off diagonally (7 vertices).

    Used to trim corner_shape() geometry down to just the correct octant of a cuboid corner.
    """
    pts = [[1, 1, 1], [1, 1, 0], [1, 0, 0], [0, 1, 1], [0, 1, 0], [1, 0, 1], [0, 0, 1]]
    faces = [[0, 1, 2], [2, 5, 0], [0, 5, 6], [0, 6, 3], [0, 3, 4], [0, 4, 1], [1, 4, 2], [3, 6, 4], [5, 2, 6], [2, 4, 6]]
    scaled = [[(p[0] - 0.5) * (s[0] + 0.001), (p[1] - 0.5) * (s[1] + 0.001), (p[2] - 0.5) * (s[2] + 0.001)] for p in pts]
    shape = _opolyhedron(scaled, faces)
    if corner[0] < 0:
        shape = shape.mirror([1, 0, 0])
    if corner[1] < 0:
        shape = shape.mirror([0, 1, 0])
    if corner[2] < 0:
        shape = shape.mirror([0, 0, 1])
    return shape


def _corner_shape(corner: Sequence[float], size: Sequence[float], edges: Sequence[Sequence[float]], r: float, is_chamfer: bool, trimcorners: bool, _fn, _fa, _fs) -> PyOpenSCAD:
    e = _corner_edges(edges, corner)
    cnt = sum(e)
    c = [r, r, r]
    m = 0.01
    c2 = [corner[i] * c[i] / 2 for i in range(3)]
    c3 = [corner[i] * (c[i] - m / 2) for i in range(3)]
    fn = 4 if is_chamfer else max(4, int(_quantup(_frag_count(r, _fn, _fa, _fs), 4)))
    base_t = [corner[i] * (size[i] / 2 - c[i]) for i in range(3)]

    def xtcyl(length, radius):
        return _rotate_to_axis(_ocylinder(h=length, r=radius, center=True, fn=fn), 0)

    def ytcyl(length, radius):
        return _rotate_to_axis(_ocylinder(h=length, r=radius, center=True, fn=fn), 1)

    def ztcyl(length, radius):
        return _ocylinder(h=length, r=radius, center=True, fn=fn)

    def tsphere(radius):
        return _osphere(r=radius, fn=fn)

    if cnt == 0 or r == 0:
        shape = _ocube(m, center=True).translate(c3)
    elif cnt == 1:
        if e[0]:
            shape = xtcyl(c[0] * 2, r).translate([c3[0], 0, 0])
        elif e[1]:
            shape = ytcyl(c[1] * 2, r).translate([0, c3[1], 0])
        else:
            shape = ztcyl(c[2] * 2, r).translate([0, 0, c3[2]])
        shape = shape & _trunc_cube(c, corner).translate(c2)
    elif cnt == 2:
        if not e[0]:
            shape = ytcyl(c[1] * 2, r) & ztcyl(c[2] * 2, r)
        elif not e[1]:
            shape = xtcyl(c[0] * 2, r) & ztcyl(c[2] * 2, r)
        else:
            shape = xtcyl(c[0] * 2, r) & ytcyl(c[1] * 2, r)
        shape = shape & _trunc_cube(c, corner).translate(c2)
    else:
        shape = tsphere(r) if trimcorners else (xtcyl(c[0] * 2, r) & ytcyl(c[1] * 2, r) & ztcyl(c[2] * 2, r))
        shape = shape & _trunc_cube(c, corner).translate(c2)
    return shape.translate(base_t)


def _edge_mask_negative(sz: Sequence[float], edge_set: Sequence[Sequence[float]], ard: float, is_chamfer: bool, trimcorners: bool, _fn, _fa, _fs) -> PyOpenSCAD:
    assert edge_set == EDGES_ALL or edge_set[2] == [0, 0, 0, 0], "Cannot use negative rounding/chamfer with Z aligned edges."
    pieces = []
    cutters = []
    for axis in (0, 1):
        for i in range(4):
            if edge_set[axis][i] > 0:
                vec = EDGE_OFFSETS[axis][i]
                adj = [ard - 0.01, ard - 0.01, -ard]
                t = [vec[k] / 2 * (sz[k] + adj[k]) for k in range(3)]
                box = _rotate_to_axis(_ocube([ard, ard, sz[axis]], center=True), axis)
                pieces.append(box.translate(t))
                adj2 = [2 * ard, 2 * ard, -2 * ard]
                t2 = [vec[k] / 2 * (sz[k] + adj2[k]) for k in range(3)]
                if is_chamfer:
                    cutter = _ocube([ard * math.sqrt(2), ard * math.sqrt(2), sz[axis] + 2.1 * ard], center=True).rotate(45, [0, 0, 1])
                else:
                    fn = int(_quantup(_frag_count(ard, _fn, _fa, _fs), 4))
                    cutter = _ocylinder(h=sz[axis] + 2.1 * ard, r=ard, center=True, fn=fn)
                cutters.append(_rotate_to_axis(cutter, axis).translate(t2))
    if trimcorners:
        for za in (-1, 1):
            for ya in (-1, 1):
                for xa in (-1, 1):
                    ce = _corner_edges(edge_set, [xa, ya, za])
                    if ce[0] + ce[1] > 1:
                        adj3 = [ard - 0.01, ard - 0.01, -ard]
                        t3 = [[xa, ya, za][k] / 2 * (sz[k] + adj3[k]) for k in range(3)]
                        pieces.append(_ocube([ard + 0.01, ard + 0.01, ard], center=True).translate(t3))
    edge_union = pieces[0]
    for p in pieces[1:]:
        edge_union = edge_union | p
    for c in cutters:
        edge_union = edge_union - c
    return _ocube(sz, center=True) | edge_union


# ---------------------------------------------------------------------------
# Section: native-only 2-D -> 3-D constructor (no BOSL2 equivalent)
# ---------------------------------------------------------------------------


def roof(shape, method: str = "straight") -> Bosl2Solid:
    """Raise a hip roof over a 2-D *shape* via its straight skeleton (native ``roof()``).

    Like :func:`~bosl2.skin.linear_sweep`, this turns a 2-D outline into a 3-D solid, but the top is
    a peaked roof (each edge slopes inward at 45 degrees to the skeleton) rather than a flat
    extrusion. *shape* is any 2-D object -- a native ``square``/``circle``/``polygon``, a
    :meth:`Path.polygon`, or a :class:`Bosl2Solid` wrapping one. *method* selects the skeleton
    algorithm. PythonSCAD-only (no BOSL2 counterpart); covered by the STL render tests.
    """
    return Bosl2Solid(Bosl2Solid._unwrap(shape).roof(method=method))


# ---------------------------------------------------------------------------
# Section: Cuboids, Prismoids and Pyramids
# ---------------------------------------------------------------------------


def cube(
    size: float | Sequence[float] = 1,
    center: bool | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """A cube, built with the builtin cube(), with BOSL2-style anchor/spin/orient support.

    Args:
        size:   size of the cube, a number or length-3 vector
        center: if given, overrides anchor (True -> CENTER, False -> FRONT+LEFT+BOTTOM)
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    sz = [float(size)] * 3 if isinstance(size, (int, float)) else [float(v) for v in size]
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else [-1, -1, -1]
    shape = _ocube(sz, center=True)
    offset = _anchor_offset_box3(sz, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=sz, anchor=use_anchor)


def cuboid(
    size: float | Sequence[float] = [1, 1, 1],
    p1: Sequence[float] | None = None,
    p2: Sequence[float] | None = None,
    chamfer: float | None = None,
    rounding: float | None = None,
    edges: str | list = "ALL",
    except_edges: list | None = None,
    trimcorners: bool = True,
    teardrop: bool | float = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A cube/cuboid with optional chamfering or rounding of edges and corners.

    Built directly from cube()/cylinder()/sphere()/hull()/minkowski(), mirroring BOSL2's own
    cuboid() algorithm (which is itself CSG composition of primitive shapes at each corner,
    not raw polyhedron mesh math).

    You cannot mix chamfering and rounding on the same call. Negative chamfers/roundings
    create external fillets, but only apply to edges around the top or bottom face.

    Note: `teardrop=` is not supported by this pure-Python port.

    Args:
        size:         size of the cuboid, a number or length-3 vector
        p1:           align the cuboid's corner at p1, if given (forces anchor=FRONT+LEFT+BOTTOM)
        p2:           if given with p1, defines the cuboid's opposing cornerpoint
        chamfer:      chamfer size, inset from sides (default: no chamfer)
        rounding:     edge rounding radius (default: no rounding)
        edges:        edges to mask (default "ALL")
        except_edges: edges to explicitly not mask (BOSL2's `except=` synonym; `except` is a Python keyword)
        trimcorners:  round/chamfer corners where three treated edges meet (default True)
        anchor:       anchor point (default CENTER)
        spin:         Z-axis rotation in degrees (default 0)
        orient:       direction to rotate the top towards (default UP)
        _fn/_fa/_fs:  arc smoothness overrides for rounded edges/corners

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.cuboid([40, 30, 20])
            shape.show()

        .. pythonscad-example::

            shape = bosl2.shapes3d.cuboid([40, 30, 20], rounding=5)
            shape.show()
    """
    if teardrop:
        raise NotImplementedError("cuboid(): teardrop= is not supported by this pure-Python port.")
    sz = [float(size)] * 3 if isinstance(size, (int, float)) else [float(v) for v in size]
    if p1 is not None:
        if p2 is not None:
            mn = [min(p1[i], p2[i]) for i in range(3)]
            mx = [max(p1[i], p2[i]) for i in range(3)]
            shape = cuboid(
                [mx[i] - mn[i] for i in range(3)], chamfer=chamfer, rounding=rounding, edges=edges,
                except_edges=except_edges, trimcorners=trimcorners, anchor=[-1, -1, -1], _fn=_fn, _fa=_fa, _fs=_fs,
            )
            return shape.translate(mn)
        shape = cuboid(
            sz, chamfer=chamfer, rounding=rounding, edges=edges, except_edges=except_edges,
            trimcorners=trimcorners, anchor=[-1, -1, -1], _fn=_fn, _fa=_fa, _fs=_fs,
        )
        return shape.translate(p1)

    edge_set = _edges(edges, except_edges or [])
    chamfer_v = 0 if not chamfer else chamfer
    rounding_v = 0 if not rounding else rounding
    assert not (chamfer_v and rounding_v), "Cannot specify nonzero value for both chamfer and rounding"

    corners8 = [[xa, ya, za] for za in (-1, 1) for ya in (-1, 1) for xa in (-1, 1)]

    if chamfer_v != 0:
        r = chamfer_v
        if edge_set == EDGES_ALL and trimcorners:
            if r < 0:
                shape = _edge_mask_negative(sz, edge_set, abs(r), True, trimcorners, _fn, _fa, _fs)
            else:
                isize = [max(0.001, v - 2 * r) for v in sz]
                shape = _ohull(
                    _ocube([sz[0], isize[1], isize[2]], center=True),
                    _ocube([isize[0], sz[1], isize[2]], center=True),
                    _ocube([isize[0], isize[1], sz[2]], center=True),
                )
        elif r < 0:
            shape = _edge_mask_negative(sz, edge_set, abs(r), True, trimcorners, _fn, _fa, _fs)
        else:
            # Intersected with the plain box: _corner_shape()'s per-corner treatment (for a
            # single active edge, e.g. edges="Z") is sized around the rounding radius alone, not
            # clipped to the box's own extent along the *other* axes -- for edges="Z" specifically,
            # each corner cap spans 2*r along Z, so if r exceeds half the box's Z size (a thin
            # slab with a comparatively large XY corner rounding, e.g. labels.py's striped
            # backgrounds), the un-intersected hull balloons far beyond the box's actual
            # thickness instead of just rounding its corners.
            shape = _ohull(*[_corner_shape(c, sz, edge_set, r, True, trimcorners, _fn, _fa, _fs) for c in corners8]) & _ocube(sz, center=True)
    elif rounding_v != 0:
        r = rounding_v
        if edge_set == EDGES_ALL and r > 0:
            isize = [max(0.001, v - 2 * r) for v in sz]
            fn = int(_quantup(_frag_count(r, _fn, _fa, _fs), 4))
            shape = _ominkowski(_ocube(isize, center=True), _osphere(r=r, fn=fn))
        elif r < 0:
            shape = _edge_mask_negative(sz, edge_set, abs(r), False, trimcorners, _fn, _fa, _fs)
        else:
            # See the chamfer branch above for why this needs clipping to the plain box.
            shape = _ohull(*[_corner_shape(c, sz, edge_set, r, False, trimcorners, _fn, _fa, _fs) for c in corners8]) & _ocube(sz, center=True)
    else:
        shape = _ocube(sz, center=True)

    offset = _anchor_offset_box3(sz, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=sz, anchor=anchor)


def prismoid(
    size1: Sequence[float],
    size2: Sequence[float],
    h: float | None = None,
    shift: Sequence[float] = [0, 0],
    rounding: float | Sequence[float] = 0,
    rounding1: float | Sequence[float] | None = None,
    rounding2: float | Sequence[float] | None = None,
    chamfer: float | Sequence[float] = 0,
    chamfer1: float | Sequence[float] | None = None,
    chamfer2: float | Sequence[float] | None = None,
    l: float | None = None,
    center: bool | None = None,
    anchor: Sequence[float] = BOTTOM,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A rectangular prismoid, built as the convex hull() of two (optionally rounded/chamfered) rects.

    Args:
        size1:     [width, length] of the bottom end
        size2:     [width, length] of the top end
        h/l:       height of the prism
        shift:     [X,Y] shift of the top center relative to the bottom center
        rounding:  vertical-edge roundover radius, or per-corner list [X+Y+,X-Y+,X-Y-,X+Y-] (default 0)
        rounding1: roundover radius for the bottom of the vertical-ish edges
        rounding2: roundover radius for the top of the vertical-ish edges
        chamfer:   vertical-edge chamfer size, or per-corner list (default 0)
        chamfer1:  chamfer size for the bottom of the vertical-ish edges
        chamfer2:  chamfer size for the top of the vertical-ish edges
        center:    if given, overrides anchor
        anchor:    anchor point (default BOTTOM)
        spin:      Z-axis rotation in degrees after anchor (default 0)
        orient:    direction to rotate the top towards, after spin (default UP)
        _fn/_fa/_fs: arc smoothness overrides for rounded corners

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.prismoid([40, 40], [20, 25], h=30)
            shape.show()
    """
    from .shapes2d import _rect_path

    s1 = [float(size1)] * 2 if isinstance(size1, (int, float)) else [float(v) for v in size1]
    s2 = [float(size2)] * 2 if isinstance(size2, (int, float)) else [float(v) for v in size2]
    height = h if h is not None else (l if l is not None else 1)
    r1 = rounding1 if rounding1 is not None else rounding
    r2 = rounding2 if rounding2 is not None else rounding
    c1 = chamfer1 if chamfer1 is not None else chamfer
    c2 = chamfer2 if chamfer2 is not None else chamfer
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM

    path1 = _rect_path(s1, rounding=r1, chamfer=c1, _fn=_fn, _fa=_fa, _fs=_fs)
    path2 = _rect_path(s2, rounding=r2, chamfer=c2, _fn=_fn, _fa=_fa, _fs=_fs)
    bottom_pts = [[p[0], p[1], -height / 2] for p in path1]
    top_pts = [[p[0] + shift[0], p[1] + shift[1], height / 2] for p in path2]
    bottom = _opolyhedron(bottom_pts, [list(range(len(bottom_pts)))])
    top = _opolyhedron(top_pts, [list(range(len(top_pts)))])
    shape = _ohull(bottom, top)
    offset = _anchor_offset_hull3(bottom_pts + top_pts, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def octahedron(size: float = 1, anchor: Sequence[float] = CENTER, spin: float = 0, orient: Sequence[float] = UP) -> Bosl2Solid:
    """An octahedron with axis-aligned points, built directly with polyhedron().

    Args:
        size:   width of the octahedron, tip to tip
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    s = size / 2
    pts = [[s, 0, 0], [-s, 0, 0], [0, s, 0], [0, -s, 0], [0, 0, s], [0, 0, -s]]
    faces = [[2, 0, 4], [1, 2, 4], [3, 1, 4], [0, 3, 4], [0, 2, 5], [2, 1, 5], [1, 3, 5], [3, 0, 5]]
    shape = _opolyhedron(pts, faces)
    offset = _anchor_offset_hull3(pts, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def wedge(
    size: Sequence[float] = [1, 1, 1],
    center: bool | None = None,
    anchor: Sequence[float] = FRONT + LEFT + BOTTOM,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """A 3-D triangular wedge with the hypotenuse in the X+Z+ quadrant, built directly with polyhedron().

    Args:
        size:   [width, thickness, height]
        center: if given, overrides anchor (True -> CENTER, False -> FRONT+LEFT+BOTTOM)
        anchor: anchor point (default FRONT+LEFT+BOTTOM)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    sz = [float(size)] * 3 if isinstance(size, (int, float)) else [float(v) for v in size]
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else [-1, -1, -1]
    pts = [[1, 1, -1], [1, -1, -1], [1, -1, 1], [-1, 1, -1], [-1, -1, -1], [-1, -1, 1]]
    pts = [[p[0] * sz[0] / 2, p[1] * sz[1] / 2, p[2] * sz[2] / 2] for p in pts]
    faces = [[0, 1, 2], [3, 5, 4], [0, 3, 1], [1, 3, 4], [1, 4, 2], [2, 4, 5], [2, 5, 3], [0, 2, 3]]
    shape = _opolyhedron(pts, faces)
    offset = _anchor_offset_hull3(pts, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def _rect_tube_rounding(
    factor: float,
    ir: Sequence[float | None],
    r: Sequence[float | None],
    alternative: Sequence[float | None],
    size: Sequence[float],
    isize: Sequence[float],
) -> list[float]:
    wall = min(size[0] - isize[0], size[1] - isize[1]) / 2 * factor
    return [
        iri if iri is not None else (max(0.0, (ri if ri is not None else 0.0) - wall) if alternative[i] is None else 0.0)
        for i, (iri, ri) in enumerate(zip(ir, r))
    ]


def rect_tube(
    h: float | None = None,
    size: float | Sequence[float] | None = None,
    isize: float | Sequence[float] | None = None,
    center: bool | None = None,
    shift: Sequence[float] = [0, 0],
    wall: float | None = None,
    size1: float | Sequence[float] | None = None,
    size2: float | Sequence[float] | None = None,
    isize1: float | Sequence[float] | None = None,
    isize2: float | Sequence[float] | None = None,
    rounding: float | Sequence[float] = 0,
    rounding1: float | Sequence[float] | None = None,
    rounding2: float | Sequence[float] | None = None,
    irounding: float | Sequence[float] = 0,
    irounding1: float | Sequence[float] | None = None,
    irounding2: float | Sequence[float] | None = None,
    chamfer: float | Sequence[float] = 0,
    chamfer1: float | Sequence[float] | None = None,
    chamfer2: float | Sequence[float] | None = None,
    ichamfer: float | Sequence[float] = 0,
    ichamfer1: float | Sequence[float] | None = None,
    ichamfer2: float | Sequence[float] | None = None,
    anchor: Sequence[float] = BOTTOM,
    spin: float = 0,
    orient: Sequence[float] = UP,
    l: float | None = None,
) -> Bosl2Solid:
    """BOSL2 rect_tube() -- a rectangular tube (a rectangle with a rectangular hole through it).

    Args:
        h/l:        height/length of the tube (default 1)
        size:       outer [X,Y] size of the tube
        isize:      inner [X,Y] size of the tube
        center:     if given, overrides anchor
        shift:      [X,Y] shift of the top center relative to the bottom center
        wall:       wall thickness
        size1/size2:   outer [X,Y] size at the bottom/top
        isize1/isize2: inner [X,Y] size at the bottom/top
        rounding/rounding1/rounding2:    outer edge rounding radius (overall/bottom/top)
        irounding/irounding1/irounding2: inner edge rounding radius (default: same as rounding)
        chamfer/chamfer1/chamfer2:       outer edge chamfer size (overall/bottom/top)
        ichamfer/ichamfer1/ichamfer2:    inner edge chamfer size (default: same as chamfer)
        anchor:     anchor point (default BOTTOM)
        spin:       Z-axis rotation in degrees after anchor (default 0)
        orient:     direction to rotate the top towards, after spin (default UP)
    """
    from .shapes2d import _rect_path

    def as2(v: float | Sequence[float] | None) -> list[float] | None:
        if v is None:
            return None
        return [float(v), float(v)] if isinstance(v, (int, float)) else [float(x) for x in v]

    def force4(v: float | Sequence[float] | None) -> list[float | None]:
        if v is None:
            return [None, None, None, None]
        return [float(v)] * 4 if isinstance(v, (int, float)) else [float(x) for x in v]

    def force4f(v: float | Sequence[float]) -> list[float]:
        return [float(v)] * 4 if isinstance(v, (int, float)) else [float(x) for x in v]

    def override_or_none(
        specific: float | Sequence[float] | None, general: float | Sequence[float]
    ) -> float | Sequence[float] | None:
        # `general` (irounding/ichamfer) defaults to 0 rather than None in this port's
        # signature, so a bare 0 is treated as "not specified" (inherit from rounding/chamfer);
        # pass irounding1=/irounding2=/ichamfer1=/ichamfer2= (which do default to None) to force
        # an explicit zero.
        if specific is not None:
            return specific
        return general if general else None

    height = h if h is not None else (l if l is not None else 1)
    s1 = as2(size1) if size1 is not None else as2(size)
    s2 = as2(size2) if size2 is not None else as2(size)
    i1 = as2(isize1) if isize1 is not None else as2(isize)
    i2 = as2(isize2) if isize2 is not None else as2(isize)
    size1_v = s1 if s1 is not None else ([i1[0] + 2 * wall, i1[1] + 2 * wall] if (wall is not None and i1 is not None) else None)
    size2_v = s2 if s2 is not None else ([i2[0] + 2 * wall, i2[1] + 2 * wall] if (wall is not None and i2 is not None) else None)
    isize1_v = i1 if i1 is not None else ([s1[0] - 2 * wall, s1[1] - 2 * wall] if (wall is not None and s1 is not None) else None)
    isize2_v = i2 if i2 is not None else ([s2[0] - 2 * wall, s2[1] - 2 * wall] if (wall is not None and s2 is not None) else None)
    assert size1_v is not None and size2_v is not None, "rect_tube(): bad size/size1/size2 argument."
    assert isize1_v is not None and isize2_v is not None, "rect_tube(): bad isize/isize1/isize2 argument."
    assert isize1_v[0] < size1_v[0] and isize1_v[1] < size1_v[1], "rect_tube(): inner size is larger than outer size at the bottom."
    assert isize2_v[0] < size2_v[0] and isize2_v[1] < size2_v[1], "rect_tube(): inner size is larger than outer size at the top."

    rounding1_v = force4f(rounding1 if rounding1 is not None else rounding)
    rounding2_v = force4f(rounding2 if rounding2 is not None else rounding)
    chamfer1_v = force4f(chamfer1 if chamfer1 is not None else chamfer)
    chamfer2_v = force4f(chamfer2 if chamfer2 is not None else chamfer)
    irounding1_t = force4(override_or_none(irounding1, irounding))
    irounding2_t = force4(override_or_none(irounding2, irounding))
    ichamfer1_t = force4(override_or_none(ichamfer1, ichamfer))
    ichamfer2_t = force4(override_or_none(ichamfer2, ichamfer))

    irounding1_v = _rect_tube_rounding(1.0, irounding1_t, rounding1_v, ichamfer1_t, size1_v, isize1_v)
    irounding2_v = _rect_tube_rounding(1.0, irounding2_t, rounding2_v, ichamfer2_t, size2_v, isize2_v)
    ichamfer1_v = _rect_tube_rounding(1 / math.sqrt(2), ichamfer1_t, chamfer1_v, irounding1_t, size1_v, isize1_v)
    ichamfer2_v = _rect_tube_rounding(1 / math.sqrt(2), ichamfer2_t, chamfer2_v, irounding2_t, size2_v, isize2_v)

    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM

    outer = prismoid(
        size1_v, size2_v, h=height, shift=shift, rounding1=rounding1_v, rounding2=rounding2_v,
        chamfer1=chamfer1_v, chamfer2=chamfer2_v, anchor=CENTER,
    )
    inner = prismoid(
        isize1_v, isize2_v, h=height + 0.02, shift=shift, rounding1=irounding1_v, rounding2=irounding2_v,
        chamfer1=ichamfer1_v, chamfer2=ichamfer2_v, anchor=CENTER,
    )
    shape = outer.shape - inner.shape

    path1 = _rect_path(size1_v, rounding=rounding1_v, chamfer=chamfer1_v)
    path2 = _rect_path(size2_v, rounding=rounding2_v, chamfer=chamfer2_v)
    bottom_pts = [[p[0], p[1], -height / 2] for p in path1]
    top_pts = [[p[0] + shift[0], p[1] + shift[1], height / 2] for p in path2]
    offset = _anchor_offset_hull3(bottom_pts + top_pts, use_anchor)

    straight = size1_v == size2_v and shift[0] == 0 and shift[1] == 0
    out_size = [size1_v[0], size1_v[1], height] if straight else None
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=out_size, anchor=use_anchor)


# ---------------------------------------------------------------------------
# Section: Cylinders
# ---------------------------------------------------------------------------


def cylinder(
    h: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """A cylinder/cone, built with the builtin cylinder(), with BOSL2-style anchor/spin/orient support.

    Args:
        l/h:    height of the cylinder
        r1:     bottom radius (before orientation)
        r2:     top radius (before orientation)
        center: if given, overrides anchor (True -> CENTER, False -> BOTTOM)
        d1:     bottom diameter (before orientation)
        d2:     top diameter (before orientation)
        r:      radius of the cylinder
        d:      diameter of the cylinder
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM
    shape = _ocylinder(h=length, r1=rad1, r2=rad2, center=True)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def cyl(
    h: float | None = None,
    r: float | None = None,
    center: bool | None = None,
    l: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    chamfang: float | None = None,
    chamfang1: float | None = None,
    chamfang2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    circum: bool = False,
    realign: bool = False,
    shift: Sequence[float] = [0, 0],
    from_end: bool | None = None,
    from_end1: bool | None = None,
    from_end2: bool | None = None,
    texture: str | list | None = None,
    tex_size: Sequence[float] = [5, 5],
    tex_counts: Sequence[float] | None = None,
    tex_inset: bool | float = False,
    tex_rot: bool = False,
    tex_scale: float = 1,
    tex_samples: int | None = None,
    tex_taper: float | list | None = None,
    tex_style: str = "min_edge",
    anchor: Sequence[float] | None = None,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A cylinder with optional chamfering/rounding of its end rims, built with cube()/cylinder()/sphere()/rotate_extrude().

    Positive rounding is built as a minkowski() of a shorter cylinder with a sphere at each
    rounded end (an inset fillet, not an outward bulge), matching BOSL2's own rounded-end
    geometry. Chamfering builds the exact half-profile (with the requested bevel at each end)
    and revolves it with rotate_extrude().

    Note: `texture=` (VNF surface texturing) is not supported by this pure-Python port.

    Args:
        l/h:      length of the cylinder along its axis (default 1)
        r:        radius of the cylinder (default 1)
        center:   if given, overrides anchor (True -> CENTER, False -> BOTTOM)
        r1/r2:    radius of the negative/positive end of the cylinder
        d/d1/d2:  diameter of the cylinder / negative end / positive end
        chamfer/chamfer1/chamfer2:    chamfer size on the ends (overall/bottom/top)
        rounding/rounding1/rounding2: rounding radius on the ends (overall/bottom/top)
        circum:      circumscribe rather than inscribe the given radius (default False)
        realign:     rotate by half the angle of one face (default False)
        shift:       [X,Y] shift of the top center relative to the bottom center
        anchor:      anchor point (default CENTER, or BOTTOM if center=False)
        spin:        Z-axis rotation in degrees after anchor (default 0)
        orient:      direction to rotate the top towards, after spin (default UP)
        _fn/_fa/_fs: arc smoothness overrides

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.cyl(h=30, r=10)
            shape.show()

        .. pythonscad-example::

            shape = bosl2.shapes3d.cyl(h=30, r=10, rounding=3)
            shape.show()
    """
    if texture is not None:
        raise NotImplementedError("cyl(): texture= is not supported by this pure-Python port.")
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    if circum:
        sides = _frag_count(max(rad1, rad2), _fn, _fa, _fs)
        sc = 1 / math.cos(math.pi / sides)
        rad1 *= sc
        rad2 *= sc
    use_anchor = anchor
    if use_anchor is None:
        use_anchor = CENTER if center is None or center else BOTTOM

    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"

    if not (r1v or r2v or c1v or c2v):
        shape = _ocylinder(h=length, r1=rad1, r2=rad2, center=True, fn=_fn, fa=_fa, fs=_fs)
    elif rad1 == rad2 and r1v == r2v and r1v > 0 and not c1v and not c2v:
        # Straight cylinder, uniform rounding on both ends: exact via minkowski(cylinder, sphere).
        inner_r = max(0.001, rad1 - r1v)
        inner_l = max(0.001, length - 2 * r1v)
        sphere_fn = int(_quantup(_frag_count(r1v, _fn, _fa, _fs), 4))
        shape = _ominkowski(
            _ocylinder(h=inner_l, r=inner_r, center=True, fn=_fn, fa=_fa, fs=_fs),
            _osphere(r=r1v, fn=sphere_fn),
        )
    else:
        profile = _cyl_profile(rad1, rad2, length, r1v, r2v, c1v, c2v, _fn, _fa, _fs)
        from .shapes2d import _opolygon

        shape = _orotate_extrude(_opolygon(profile), fn=_fn, fa=_fa, fs=_fs)

    if realign:
        sides = _frag_count(max(rad1, rad2), _fn, _fa, _fs)
        shape = shape.rotate(180 / sides, [0, 0, 1])
    if shift[0] or shift[1]:
        shear = [
            [1, 0, shift[0] / length, 0],
            [0, 1, shift[1] / length, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
        shape = shape.multmatrix(shear)
    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def _cyl_profile(r1: float, r2: float, length: float, rounding1: float = 0, rounding2: float = 0, chamfer1: float = 0, chamfer2: float = 0, _fn=None, _fa=None, _fs=None) -> list[list[float]]:
    from .shapes2d import _arc_points

    path = [[0.0, -length / 2]]
    if rounding1:
        n = max(3, _frag_count(rounding1, _fn, _fa, _fs) // 4)
        cp = [r1 - rounding1, -length / 2 + rounding1]
        path.extend(_arc_points(n, rounding1, 270, 90, cp))
    elif chamfer1:
        path.append([r1 - chamfer1, -length / 2])
        path.append([r1, -length / 2 + chamfer1])
    else:
        path.append([r1, -length / 2])
    if rounding2:
        n = max(3, _frag_count(rounding2, _fn, _fa, _fs) // 4)
        cp = [r2 - rounding2, length / 2 - rounding2]
        path.extend(_arc_points(n, rounding2, 0, 90, cp))
    elif chamfer2:
        path.append([r2, length / 2 - chamfer2])
        path.append([r2 - chamfer2, length / 2])
    else:
        path.append([r2, length / 2])
    path.append([0.0, length / 2])
    return path


def regular_prism(
    n: int,
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    ir: float | None = None,
    id: float | None = None,
    side: float | None = None,
    l: float | None = None,
    height: float | None = None,
    length: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    circum: bool = False,
    realign: bool = False,
    shift: Sequence[float] = [0, 0],
    center: bool | None = None,
    anchor: Sequence[float] | None = None,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A regular n-sided prism (or frustum) -- the n-gon analogue of cyl(): a regular polygon
    cross-section extruded along Z, with optional per-end chamfer or rounding. Built the same
    way cyl() is (native cylinder with fn=n for the plain case; a revolved half-profile with
    fn=n for chamfered/rounded ends), so it shares cyl()'s exact rim geometry.

    Sizing gives the CIRCUMradius (vertex distance) unless noted -- exactly one of ``r``/``d``
    (radius/diameter to the vertices), ``ir``/``id`` (inradius/apothem to the face centers,
    converted via ``/cos(180/n)``), or ``side`` (edge length, converted via ``/(2 sin(180/n))``).
    ``r1``/``r2`` (or the corresponding taper) set the bottom/top radius independently for a frustum.

    Note: BOSL2 regular_prism()'s texture=/teardrop= options are not ported (they need the VNF
    texturing machinery this pure-Python port doesn't implement).

    Args:
        n:        number of sides (integer >= 3)
        h/l/height/length: prism height (default 1)
        r/d/ir/id/side:    overall size (see above)
        r1/r2:    bottom/top circumradius for a tapered prism
        chamfer/chamfer1/chamfer2:    end chamfer size (overall/bottom/top)
        rounding/rounding1/rounding2: end rounding radius (overall/bottom/top)
        circum:   circumscribe the nominal radius (scale by 1/cos(180/n)) (default False)
        realign:  rotate by half a facet so a face, not a vertex, faces +X (default False)
        shift:    [X,Y] shift of the top center relative to the bottom center
        center:   if given, overrides anchor (True -> CENTER, False -> BOTTOM)
        anchor:   anchor point (default CENTER)
        spin:     Z-axis rotation in degrees after anchor (default 0)
        orient:   direction to rotate the top towards, after spin (default UP)

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.regular_prism(6, h=20, r=15)
            shape.show()

        .. pythonscad-example::

            shape = bosl2.shapes3d.regular_prism(5, h=20, ir=12, rounding=2)
            shape.show()
    """
    assert isinstance(n, int) and n > 2, f"regular_prism(): n must be an integer >= 3, got {n}"
    cos_half = math.cos(math.pi / n)

    def circumradius(spec_r: float | None) -> float:
        if spec_r is not None:
            return spec_r
        if side is not None:
            return side / (2 * math.sin(math.pi / n))
        if id is not None:
            return (id / 2) / cos_half
        if ir is not None:
            return ir / cos_half
        if d is not None:
            return d / 2
        if r is not None:
            return r
        return 1.0

    rad1 = circumradius(r1)
    rad2 = circumradius(r2)
    if circum:
        sc = 1 / cos_half
        rad1 *= sc
        rad2 *= sc
    prism_len = next((v for v in (l, h, height, length) if v is not None), 1.0)

    r1v = rounding1 if rounding1 is not None else (rounding if rounding is not None else 0)
    r2v = rounding2 if rounding2 is not None else (rounding if rounding is not None else 0)
    c1v = chamfer1 if chamfer1 is not None else (chamfer if chamfer is not None else 0)
    c2v = chamfer2 if chamfer2 is not None else (chamfer if chamfer is not None else 0)
    assert not ((r1v or r2v) and (c1v or c2v)), "Cannot specify nonzero value for both chamfer and rounding"

    use_anchor = anchor
    if use_anchor is None:
        use_anchor = CENTER if center is None or center else BOTTOM

    if not (r1v or r2v or c1v or c2v):
        shape = _ocylinder(h=prism_len, r1=rad1, r2=rad2, center=True, fn=n)
    else:
        profile = _cyl_profile(rad1, rad2, prism_len, r1v, r2v, c1v, c2v, _fn, _fa, _fs)
        from .shapes2d import _opolygon

        shape = _orotate_extrude(_opolygon(profile), fn=n)

    # OpenSCAD's cylinder(fn=n) puts a vertex on +X; realign rotates half a facet so a face
    # centre faces +X instead (BOSL2's realign convention).
    if realign:
        shape = shape.rotate(180 / n, [0, 0, 1])
    if shift[0] or shift[1]:
        shear = [
            [1, 0, shift[0] / prism_len, 0],
            [0, 1, shift[1] / prism_len, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
        shape = shape.multmatrix(shear)
    offset = _anchor_offset_cyl(rad1, rad2, prism_len, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def xcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    circum: bool = False,
    realign: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A cylinder oriented along the X axis. See cyl() for argument details."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    shape = cyl(
        l=length, r1=rad1, r2=rad2, chamfer=chamfer, chamfer1=chamfer1, chamfer2=chamfer2,
        rounding=rounding, rounding1=rounding1, rounding2=rounding2, circum=circum,
        realign=realign, anchor=CENTER, _fn=_fn, _fa=_fa, _fs=_fs,
    ).shape.rotate(90, [0, 1, 0])
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor, axis=0)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def ycyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    circum: bool = False,
    realign: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A cylinder oriented along the Y axis. See cyl() for argument details."""
    length = l if l is not None else (h if h is not None else 1)
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    shape = cyl(
        l=length, r1=rad1, r2=rad2, chamfer=chamfer, chamfer1=chamfer1, chamfer2=chamfer2,
        rounding=rounding, rounding1=rounding1, rounding2=rounding2, circum=circum,
        realign=realign, anchor=CENTER, _fn=_fn, _fa=_fa, _fs=_fs,
    ).shape.rotate(-90, [1, 0, 0])
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor, axis=1)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def zcyl(
    h: float | None = None,
    r: float | None = None,
    d: float | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    chamfer: float | None = None,
    chamfer1: float | None = None,
    chamfer2: float | None = None,
    rounding: float | None = None,
    rounding1: float | None = None,
    rounding2: float | None = None,
    circum: bool = False,
    realign: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A cylinder oriented along the Z axis (same as cyl() with default orientation). See cyl() for argument details."""
    return cyl(
        h=h, r=r, d=d, r1=r1, r2=r2, d1=d1, d2=d2, l=l, chamfer=chamfer, chamfer1=chamfer1,
        chamfer2=chamfer2, rounding=rounding, rounding1=rounding1, rounding2=rounding2,
        circum=circum, realign=realign, anchor=anchor, spin=spin, orient=orient, _fn=_fn, _fa=_fa, _fs=_fs,
    )


def tube(
    h: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    center: bool | None = None,
    od: float | None = None,
    id: float | None = None,
    wall: float | None = None,
    outer_r1: float | None = None,
    outer_r2: float | None = None,
    od1: float | None = None,
    od2: float | None = None,
    ir1: float | None = None,
    ir2: float | None = None,
    id1: float | None = None,
    id2: float | None = None,
    realign: bool = False,
    l: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 tube() -- a hollow cylindrical tube.

    Note: BOSL2's outer-radius parameters are named `or`/`or1`/`or2`, which collide with the
    Python keyword `or`; they are exposed here as `outer_r`/`outer_r1`/`outer_r2` instead.

    Args:
        h/l:      height of the tube (default 1)
        outer_r:  outer radius of the tube (BOSL2 `or`) (default 1)
        ir:       inner radius of the tube
        center:   if given, overrides anchor (True -> CENTER, False -> DOWN)
        od:       outer diameter of the tube
        id:       inner diameter of the tube
        wall:     horizontal wall thickness (default 1)
        outer_r1/outer_r2: outer radius of the bottom/top (BOSL2 `or1`/`or2`)
        od1/od2:  outer diameter of the bottom/top
        ir1/ir2:  inner radius of the bottom/top
        id1/id2:  inner diameter of the bottom/top
        realign:  rotate by half the angle of one face (default False)
        anchor:   anchor point (default CENTER)
        spin:     Z-axis rotation in degrees after anchor (default 0)
        orient:   direction to rotate the top towards, after spin (default UP)

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.tube(h=20, outer_r=15, ir=10)
            shape.show()
    """
    height = h if h is not None else (l if l is not None else 1)
    orr1 = _pick_radius(r1=outer_r1, d1=od1, r=outer_r, d=od, dflt=None)
    orr2 = _pick_radius(r1=outer_r2, d1=od2, r=outer_r, d=od, dflt=None)
    irr1 = _pick_radius(r1=ir1, d1=id1, r=ir, d=id, dflt=None)
    irr2 = _pick_radius(r1=ir2, d1=id2, r=ir, d=id, dflt=None)
    wall_v = wall if wall is not None else 1
    rad1 = orr1 if orr1 is not None else (irr1 + wall_v if irr1 is not None else None)
    rad2 = orr2 if orr2 is not None else (irr2 + wall_v if irr2 is not None else None)
    irad1 = irr1 if irr1 is not None else (orr1 - wall_v if orr1 is not None else None)
    irad2 = irr2 if irr2 is not None else (orr2 - wall_v if orr2 is not None else None)
    assert rad1 is not None and rad2 is not None and irad1 is not None and irad2 is not None, (
        "tube(): must specify two of inner radius/diam, outer radius/diam, and wall width."
    )
    assert irad1 <= rad1 and irad2 <= rad2, "tube(): inner radius is larger than outer radius."

    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM

    outer = _ocylinder(h=height, r1=rad1, r2=rad2, center=True)
    inner = _ocylinder(h=height + 0.02, r1=irad1, r2=irad2, center=True)
    shape = outer - inner
    if realign:
        sides = _frag_count(max(rad1, rad2), None, None, None)
        shape = shape.rotate(180 / sides, [0, 0, 1])
    offset = _anchor_offset_cyl(rad1, rad2, height, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def pie_slice(
    h: float | None = None,
    r: float | None = None,
    ang: float = 30,
    center: bool | None = None,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    l: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 pie_slice() -- a pie slice, wedge of a cylinder/cone.

    Args:
        h/l:    height of the pie slice
        r:      radius of the pie slice
        ang:    pie slice angle in degrees (default 30)
        center: if given, overrides anchor
        r1/r2:  bottom/top radius of the pie slice
        d/d1/d2: diameter of the pie slice / bottom / top
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    from .shapes2d import _arc_points, _opolygon

    length = h if h is not None else (l if l is not None else 1)
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=10)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=10)
    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else BOTTOM

    base = _ocylinder(h=length, r1=rad1, r2=rad2, center=True)
    ang_v = ang % 360 if (ang > 360 or ang < 0) else ang
    if ang_v <= 0 or ang_v >= 360:
        shape = base
    else:
        maxd = max(rad1, rad2) + 0.1
        n = max(3, math.ceil(_frag_count(maxd, None, None, None) * ang_v / 360))
        arc = _arc_points(n, maxd, 0, ang_v)
        sector = _opolygon([[0.0, 0.0]] + arc).linear_extrude(height=length + 0.2, center=True)
        shape = base & sector

    offset = _anchor_offset_cyl(rad1, rad2, length, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)

# ---------------------------------------------------------------------------
# Section: Other Round Objects
# ---------------------------------------------------------------------------


def sphere(
    r: float | None = None,
    d: float | None = None,
    circum: bool = False,
    style: str = "orig",
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """A sphere, built with the builtin sphere(), with BOSL2-style anchor/spin/orient support.

    Note: `style=`/`circum=` are accepted for signature compatibility but not applied; the
    builtin sphere() is used directly.

    Args:
        r:      radius of the sphere
        d:      diameter of the sphere
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
        _fn/_fa/_fs: arc smoothness overrides

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.sphere(r=15)
            shape.show()
    """
    rad = r if r is not None else (d / 2 if d is not None else 1)
    shape = _osphere(r=rad, fn=_fn, fa=_fa, fs=_fs)
    offset = _anchor_offset_sphere(rad, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def spheroid(
    r: float | None = None,
    style: str = "aligned",
    d: float | None = None,
    circum: bool = False,
    dual: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
    _fn: float | None = None,
    _fa: float | None = None,
    _fs: float | None = None,
) -> Bosl2Solid:
    """An approximate sphere; this pure-Python port just builds a plain sphere() (style/dual are ignored).

    Args:
        r:      radius of the spheroid
        d:      diameter of the spheroid
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
        _fn/_fa/_fs: arc smoothness overrides
    """
    return sphere(r=r, d=d, anchor=anchor, spin=spin, orient=orient, _fn=_fn, _fa=_fa, _fs=_fs)


def _teardrop2d_path(r: float, ang: float, cap_h: float | None, circum: bool, realign: bool, n: int) -> list[list[float]]:
    """The 2-D (X,Y) outline of a BOSL2-style teardrop2d(): a circle of radius *r* capped by a
    point (or, if *cap_h* truncates it, a flat top) formed by two walls tangent to the circle at
    +-*ang* degrees from the Y axis. *n* is the segment count for a full circle of this radius
    (as from _frag_count()); *realign* is approximated by toggling the parity of the round
    section's vertex count, since a vertex landing exactly at the bottom gives a "point" and a
    vertex straddling it gives a "flat" bottom -- the same effect BOSL2 gets from its own $fn
    discretization.
    """
    from .shapes2d import _arc_points

    rad = r / math.cos(math.pi / n) if circum else r
    maxheight = rad / math.sin(math.radians(ang))
    minheight = rad * math.sin(math.radians(ang))
    assert cap_h is None or cap_h >= minheight - 1e-9, "teardrop2d(): cap_h cannot be less than r*sin(ang)."
    pointy = cap_h is None or cap_h >= maxheight

    sweep = 180 + 2 * ang
    pts = max(2, round(n * sweep / 360)) + 1
    if realign == (pts % 2 == 1):
        pts += 1
    arc = _arc_points(pts, rad, ang, -sweep, [0.0, 0.0])

    if pointy or cap_h is None:
        return [[0.0, maxheight]] + arc
    cap_x = (maxheight - cap_h) * math.tan(math.radians(ang))
    return [[cap_x, cap_h]] + arc + [[-cap_x, cap_h]]


def _interior_fillet_path(r: float, ang: float, overlap: float, n: int) -> list[list[float]]:
    """The 2-D cross-section of an interior_fillet(): the wedge bounded by the corner point, the
    two tangent points on each wall (distance r/tan(ang/2) from the corner), and the concave arc
    of radius *r* joining them (center at distance r/sin(ang/2) from the corner along the
    bisector) -- the generalization to arbitrary *ang* of the classic `cube() - cylinder()`
    quarter-round fillet at ang=90. Each straight wall edge is extended *overlap* past the ideal
    corner point so the piece unions cleanly onto both adjoining faces instead of meeting them at
    an exact, potentially non-manifold, edge.
    """
    from .shapes2d import _arc_points

    half = math.radians(ang / 2)
    tlen = r / math.tan(half) if r > 0 else 0.0
    p0 = [tlen, 0.0]
    p1 = [tlen * math.cos(math.radians(ang)), tlen * math.sin(math.radians(ang))]
    flap0 = [-overlap, 0.0]
    flap1 = [-overlap * math.cos(math.radians(ang)), -overlap * math.sin(math.radians(ang))]
    if r <= 0:
        return [flap0, p0, p1, flap1]

    dist = r / math.sin(half)
    center = [dist * math.cos(half), dist * math.sin(half)]
    start_a = math.degrees(math.atan2(p0[1] - center[1], p0[0] - center[0]))
    end_a = math.degrees(math.atan2(p1[1] - center[1], p1[0] - center[0]))
    sweep = ((end_a - start_a + 180) % 360) - 180
    arc_n = max(2, round(n * abs(sweep) / 360)) + 1
    arc = _arc_points(arc_n, r, start_a, sweep, center)
    return [flap0] + arc + [flap1]


def torus(
    r_maj: float | None = None,
    r_min: float | None = None,
    center: bool | None = None,
    d_maj: float | None = None,
    d_min: float | None = None,
    outer_r: float | None = None,
    ir: float | None = None,
    od: float | None = None,
    id: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 torus() -- a torus (donut) shape.

    Note: BOSL2's outer-radius parameter is named `or`, which collides with the Python
    keyword `or`; it is exposed here as `outer_r` instead.

    Args:
        r_maj:  major radius of the torus ring (use with r_min or d_min)
        r_min:  minor radius of the torus ring (use with r_maj or d_maj)
        center: if given, overrides anchor (True -> CENTER, False -> DOWN)
        d_maj:  major diameter of the torus ring
        d_min:  minor diameter of the torus ring
        outer_r: outer radius of the torus (BOSL2 `or`) (use with ir or id)
        ir:     inside radius of the torus (use with outer_r or od)
        od:     outer diameter of the torus (use with ir or id)
        id:     inside diameter of the torus (use with outer_r or od)
        anchor: anchor point (default CENTER)
        orient: direction to rotate the top towards, after spin (default UP)

    Examples:
        .. pythonscad-example::

            shape = bosl2.shapes3d.torus(r_maj=25, r_min=8)
            shape.show()
    """
    from .shapes2d import _arc_points, _opolygon

    _or = _pick_radius(r=outer_r, d=od, dflt=None)
    _ir = _pick_radius(r=ir, d=id, dflt=None)
    _r_maj = _pick_radius(r=r_maj, d=d_maj, dflt=None)
    _r_min = _pick_radius(r=r_min, d=d_min, dflt=None)

    if _r_maj is not None:
        maj_rad = _r_maj
    elif _ir is not None and _or is not None:
        maj_rad = (_or + _ir) / 2
    elif _ir is not None and _r_min is not None:
        maj_rad = _ir + _r_min
    elif _or is not None and _r_min is not None:
        maj_rad = _or - _r_min
    else:
        assert False, "torus(): bad parameters."

    if _r_min is not None:
        min_rad = _r_min
    elif _ir is not None:
        min_rad = maj_rad - _ir
    elif _or is not None:
        min_rad = _or - maj_rad
    else:
        assert False, "torus(): bad parameters."

    use_anchor = anchor
    if center is not None:
        use_anchor = CENTER if center else DOWN

    n = _frag_count(min_rad)
    profile = _arc_points(n, min_rad, 0, 360, [maj_rad, 0.0], endpoint=False)
    shape = _orotate_extrude(_opolygon(profile))
    offset = _anchor_offset_cyl(maj_rad + min_rad, maj_rad + min_rad, min_rad * 2, use_anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=use_anchor)


def teardrop(
    h: float | None = None,
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    circum: bool = False,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    cap_h1: float | None = None,
    cap_h2: float | None = None,
    chamfer: float = 0,
    chamfer1: float = 0,
    chamfer2: float = 0,
    realign: bool = False,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 teardrop() -- a teardrop shape, useful for 3D-printable horizontal holes.

    Args:
        h/l:    thickness of the teardrop (default 1)
        r:      radius of the circular part (default 1)
        ang:    angle of the hat walls from the Z axis in degrees (default 45)
        cap_h:  height above center to truncate the shape (default: no truncation)
        circum: produce a circumscribing teardrop shape (default False)
        r1/r2:  radius of the circular portion of the front/back end
        d/d1/d2: diameter of the circular portion / front end / back end
        cap_h1/cap_h2: truncation height on the front/back side
        chamfer/chamfer1/chamfer2: chamfer size along the bottom/top faces (overall/bottom/top) (default 0)
        realign: shift face alignment, passed to teardrop2d (default False)
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    length = h if h is not None else 1.0
    rad1 = _pick_radius(r1=r1, d1=d1, r=r, d=d, dflt=1)
    rad2 = _pick_radius(r1=r2, d1=d2, r=r, d=d, dflt=1)
    cap_h1v = cap_h1 if cap_h1 is not None else cap_h
    cap_h2v = cap_h2 if cap_h2 is not None else cap_h
    c1 = chamfer1 if chamfer1 else chamfer
    c2 = chamfer2 if chamfer2 else chamfer
    n = _frag_count(max(rad1, rad2))

    def section(rad: float, cap_hv: float | None, y: float) -> list[list[float]]:
        path = _teardrop2d_path(rad, ang, cap_hv, circum, realign, n)
        return [[p[0], y, p[1]] for p in path]

    front_y, back_y = -length / 2, length / 2
    slices = []
    if c1:
        cap_hv = (cap_h1v - c1) if cap_h1v is not None else None
        slices.append(section(max(0.001, rad1 - c1), cap_hv, front_y))
        front_y += abs(c1)
    slices.append(section(rad1, cap_h1v, front_y))
    if c2:
        back_y -= abs(c2)
    slices.append(section(rad2, cap_h2v, back_y))
    if c2:
        cap_hv = (cap_h2v - c2) if cap_h2v is not None else None
        slices.append(section(max(0.001, rad2 - c2), cap_hv, back_y + abs(c2)))

    solids = [_opolyhedron(pts, [list(range(len(pts)))]) for pts in slices]
    shape = solids[0]
    for a, b in zip(solids, solids[1:]):
        piece = _ohull(a, b)
        shape = piece if shape is solids[0] else (shape | piece)
    offset = _anchor_offset_cyl(rad1, rad2, length, anchor, axis=1)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def onion(
    r: float | None = None,
    ang: float = 45,
    cap_h: float | None = None,
    circum: bool = False,
    realign: bool = False,
    d: float | None = None,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 onion() -- an onion-dome shape (a sphere with a conical cap).

    Args:
        r:      radius of the spherical portion of the bottom (default 1)
        ang:    angle of the cone from vertical in degrees (default 45)
        cap_h:  height above the sphere center to truncate the shape (default: no truncation)
        circum: circumscribe rather than inscribe the given radius/diameter (default False)
        realign: adjust point alignment (flat vs pointy bottom) (default False)
        d:      diameter of the spherical portion of the bottom
        anchor: anchor point (default CENTER)
        spin:   Z-axis rotation in degrees after anchor (default 0)
        orient: direction to rotate the top towards, after spin (default UP)
    """
    from .shapes2d import _arc_points, _opolygon

    rad = _pick_radius(r=r, d=d, dflt=1)
    n = _frag_count(rad)
    scaled = rad / math.cos(math.pi / n) if circum else rad
    maxheight = scaled / math.sin(math.radians(ang))
    top_z = min(cap_h, maxheight) if cap_h is not None else maxheight
    pointy = top_z >= maxheight - 1e-9

    sweep = 90 + ang
    pts = max(2, round(n * sweep / 360)) + 1
    arc = list(reversed(_arc_points(pts, scaled, ang, -sweep, [0.0, 0.0])))
    if pointy:
        profile = arc + [[0.0, top_z]]
    else:
        cap_x = (maxheight - top_z) * math.tan(math.radians(ang))
        profile = arc + [[cap_x, top_z], [0.0, top_z]]

    shape = _orotate_extrude(_opolygon(profile))

    a = list(anchor)
    off_z = 0.0 if a[2] == 0 else (scaled if a[2] < 0 else -top_z)
    rn = math.hypot(a[0], a[1])
    off_xy = [-a[0] / rn * scaled, -a[1] / rn * scaled] if rn > 0 else [0.0, 0.0]
    offset = [off_xy[0], off_xy[1], off_z]
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)

# ---------------------------------------------------------------------------
# Section: Text
# ---------------------------------------------------------------------------


def _text3d_anchor_vec(anchor) -> list[float]:
    """Extracts a 3-vector from an `anchor` argument that may be a plain vector or (to
    accommodate this port's unusual `anchor: str = "baseline[-1,0,-1]"` default) a string
    with a bracketed `[x,y,z]` vector embedded in it. Falls back to LEFT if no vector can
    be found in a string anchor, matching BOSL2's own `default(anchor, center?CENTER:LEFT)`.
    """
    if isinstance(anchor, str):
        i = anchor.find("[")
        j = anchor.find("]")
        if i >= 0 and j > i:
            return [float(x) for x in anchor[i + 1 : j].split(",")]
        return [-1.0, 0.0, 0.0]
    return [float(x) for x in anchor]


def _frame_map(x: Sequence[float] | None = None, y: Sequence[float] | None = None, z: Sequence[float] | None = None) -> list[list[float]]:
    """Port of BOSL2's frame_map(): builds the 4x4 change-of-basis matrix whose columns are
    the (up to) two given unit axes plus the third axis completed via cross product, matching
    BOSL2's exact axis-completion rules (used by path_text() to orient each glyph).
    """
    xu = unit(x) if x is not None else None
    yu = unit(y) if y is not None else None
    zu = unit(z) if z is not None else None
    if xu is None:
        m = [cross(yu, zu), yu, zu]
    elif yu is None:
        m = [xu, cross(zu, xu), zu]
    elif zu is None:
        m = [xu, yu, cross(xu, yu)]
    else:
        m = [xu, yu, zu]
    return [
        [m[0][0], m[1][0], m[2][0], 0.0],
        [m[0][1], m[1][1], m[2][1], 0.0],
        [m[0][2], m[1][2], m[2][2], 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _point3d(v: Sequence[float]) -> list[float]:
    return list(v) if len(v) >= 3 else [v[0], v[1], 0.0]


def _cut_interp(pathcut: list, path: Sequence[Sequence[float]], data: Sequence[Sequence[float]]) -> list[list[float]]:
    """Port of BOSL2's `_cut_interp()`: linearly interpolates a per-path-vertex vector array
    `data` to the fractional position of each `path_cut_points()` cut point.
    """
    out = []
    for entry in pathcut:
        idx = entry[1]
        a = path[idx - 1]
        b = path[idx]
        c = entry[0]
        i = max(range(len(b)), key=lambda k: abs(b[k] - a[k]))
        factor = (c[i] - a[i]) / (b[i] - a[i])
        out.append([(1 - factor) * da + factor * db for da, db in zip(data[idx - 1], data[idx])])
    return out


def _path_text_bcast_dir(v, dim: int, path: Sequence[Sequence[float]], label: str) -> list[list[float]] | None:
    """Broadcasts a `normal=`/`top=` argument (undefined, a single vector, or a per-path-point
    list of vectors) to a list of one vector per path point, mirroring BOSL2's normalok/topok
    argument checks (including the "3-vector with z==0 on a 2d path" compatibility form).
    """
    if v is None:
        return None
    if is_vector(v, dim):
        return [list(v)] * len(path)
    if dim == 2 and is_vector(v, 3) and abs(v[2]) < 1e-9:
        return [[v[0], v[1]]] * len(path)
    if isinstance(v, list) and len(v) == len(path) and all(is_vector(p, dim) for p in v):
        return [list(p) for p in v]
    raise ValueError(f'path_text(): "{label}" must be a length-{dim} vector or a list of {len(path)} such vectors matching the path.')


def text3d(
    text: str,
    h: float = 1,
    size: float = 10,
    font: str = "Liberation Sans",
    halign: str | None = None,
    valign: str | None = None,
    spacing: float = 1.0,
    direction: str = "ltr",
    language: str = "em",
    script: str = "latin",
    anchor: str = "baseline[-1,0,-1]",
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 text3d() -- 3-D extruded text, with anchor/spin/orient support.

    Args:
        text:      text to create
        h:         extrusion height (default 1)
        size:      font size divided by 0.72 (default 10)
        font:      font to use (default "Liberation Sans")
        halign:    horizontal alignment: "left", "center", "right" (overrides anchor)
        valign:    vertical alignment: "top", "center", "baseline", "bottom" (overrides anchor)
        spacing:   relative spacing multiplier between characters (default 1.0)
        direction: text direction: "ltr", "rtl", "ttb", "btt" (default "ltr")
        language:  language the text is in (default "en")
        script:    script the text is in (default "latin")
        anchor:    anchor point (default "baseline")
        spin:      Z-axis rotation in degrees (default 0)
        orient:    direction to rotate the top towards (default UP)
    """
    av = _text3d_anchor_vec(anchor)
    ha = halign if halign is not None else ("left" if av[0] < 0 else "right" if av[0] > 0 else "center")
    va = valign if valign is not None else ("bottom" if av[1] < 0 else "top" if av[1] > 0 else "baseline")
    flat = _text2d(
        text, size=size, font=font, halign=ha, valign=va, spacing=spacing,
        direction=direction, language=language, script=script,
    )
    shape = flat.linear_extrude(height=h, center=True)
    offset = _anchor_offset_box3([size, size, h], [0, 0, av[2]])
    shape = _finish3(shape, offset, spin, orient)
    return Bosl2Solid(shape, size=None, anchor=anchor)


def path_text(
    path: Sequence[Sequence[float]],
    text: str,
    font: str = "Liberation Sans",
    size: float = 10,
    thickness: float | None = None,
    lettersize: float | Sequence[float] | None = None,
    offset: float = 0,
    reverse: bool = False,
    normal: Sequence[float] | list[list[float]] | None = None,
    top: Sequence[float] | list[list[float]] | None = None,
    center: bool = False,
    textmetrics: bool = False,
    kern: float | Sequence[float] = 0,
) -> Bosl2Solid:
    """BOSL2 path_text() -- places text characters along a path.

    Args:
        path:        path to place the text on
        text:        text to create
        font:        font to use (default "Liberation Sans")
        size:        font size divided by 0.72 (default 10)
        thickness:   thickness of the letters (not allowed for a 2-D path)
        lettersize:  scalar or array giving the size of the letters
        center:      center text on the path instead of starting at the first point (default False)
        offset:      distance to shift letters "up" towards the reader (default 0, 3-D paths only)
        normal:      direction(s) pointing towards the reader of the text (3-D paths only)
        top:         direction(s) pointing towards the top of the text
        reverse:     reverse the letters if true (default False, 3-D paths only)
        textmetrics: use the experimental textmetrics feature when lettersize is not given (default False)
        kern:        scalar or array giving per-letter size adjustments (default 0)
    """
    # Imported lazily (only path_text() needs it) so that everything else in this file stays
    # free of a numpy dependency -- bosl2.paths uses numpy internally, and numpy isn't always
    # loadable inside the real PythonSCAD app (e.g. a hardened-runtime-signed build combined
    # with an ad-hoc-signed/unsigned numpy install fails library validation).
    from bosl2.paths import Path

    assert len(text) > 0, "path_text(): text must be non-empty."
    assert size > 0, "path_text(): must give positive text size."
    assert normal is None or top is None, 'path_text(): cannot define both "normal" and "top".'
    dim = len(path[0])
    assert dim in (2, 3), "path_text(): must supply a 2d or 3d path."
    if dim == 2:
        assert thickness is None, "path_text(): cannot give a thickness with a 2d path."
        assert not reverse, "path_text(): reverse not allowed with a 2d path."
        assert offset == 0, "path_text(): cannot give offset with a 2d path."
        assert normal is None, 'path_text(): cannot define "normal" for a 2d path, only "top".'

    th = 1.0 if thickness is None else thickness
    n = len(text)

    if lettersize is not None:
        lsize = [float(lettersize)] * n if isinstance(lettersize, (int, float)) else [float(v) for v in lettersize]
        assert len(lsize) == n, "path_text(): lettersize list must have one entry per character."
    elif textmetrics:
        lsize = [_otextmetrics(ch, font=font, size=size)["advance"][0] for ch in text]
    else:
        assert False, "path_text(): textmetrics disabled -- must specify lettersize."

    kern_list = [float(kern)] * (n - 1) if isinstance(kern, (int, float)) else [float(v) for v in kern]
    assert len(kern_list) == n - 1, "path_text(): kern must be a scalar or a list of length len(text)-1."

    centers = []
    prefix = 0.0
    kern_prefix = 0.0
    for i in range(n):
        centers.append(prefix + kern_prefix + lsize[i] / 2.0)
        prefix += lsize[i]
        if i < n - 1:
            kern_prefix += kern_list[i]
    textlength = prefix + kern_prefix

    plen = Path._path_length(path)
    assert textlength <= plen, "path_text(): path is too short for the text."
    start = (plen - textlength) / 2.0 if center else 0.0
    dists = [start + c for c in centers]

    pts = Path._path_cut_points(path, dists, direction=True)

    normal_pv = _path_text_bcast_dir(normal, 3, path, "normal")
    top_pv = _path_text_bcast_dir(top, dim, path, "top")

    if normal_pv is None:
        sign = 1.0 if reverse else -1.0
        normpts = [[sign * v for v in p[3]] for p in pts]
    else:
        normpts = _cut_interp(pts, path, normal_pv)
    toppts = None if top_pv is None else _cut_interp(pts, path, top_pv)

    usetop = top_pv is not None
    usernorm = normal_pv is not None

    letters = []
    for i, ch in enumerate(text):
        tangent = pts[i][2]
        if toppts is not None:
            tt = toppts[i]
            proj = sum(a * b for a, b in zip(tangent, tt)) / sum(v * v for v in tt)
            adjustment = [proj * v for v in tt]
        elif usernorm:
            nn = normpts[i]
            proj = sum(a * b for a, b in zip(tangent, nn)) / sum(v * v for v in nn)
            adjustment = [proj * v for v in nn]
        else:
            adjustment = [0.0] * dim
        x_axis = [tangent[k] - adjustment[k] for k in range(dim)]

        glyph = _text2d(ch, size=size, font=font, halign="left", valign="baseline").translate([-lsize[i] / 2.0, 0])

        if dim == 3:
            z_axis = None if toppts is not None else normpts[i]
            y_axis = toppts[i] if toppts is not None else None
            m = _frame_map(x=x_axis, y=y_axis, z=z_axis)
            letter = glyph.linear_extrude(height=th).translate([0.0, 0.0, offset - th / 2.0])
        else:
            y_axis = toppts[i] if toppts is not None else [-v for v in normpts[i]]
            m = _frame_map(x=_point3d(x_axis), y=_point3d(y_axis))
            letter = glyph

        letters.append(letter.multmatrix(m).translate(pts[i][0]))

    result = letters[0]
    for s in letters[1:]:
        result = result | s

    return Bosl2Solid(result, size=None, anchor=CENTER)

# ---------------------------------------------------------------------------
# Section: Miscellaneous
# ---------------------------------------------------------------------------


def _heightfield_tri_area(pts: Sequence[Sequence[float]], tri: Sequence[int]) -> float:
    ax, ay, az = pts[tri[0]]
    bx, by, bz = pts[tri[1]]
    cx, cy, cz = pts[tri[2]]
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    return math.hypot(nx, ny, nz)


def _heightfield_tris(pts: list[list[float]], i1: int, i2: int, i3: int, i4: int, style: str) -> list[list[int]]:
    """Split a quad (corners i1,i2,i3,i4 at grid positions (r,c),(r+1,c),(r+1,c+1),(r,c+1)) into
    2 or 4 triangle faces, mirroring BOSL2 vnf_vertex_array()'s "default"/"alt"/"quincunx" quad
    styles. Winding direction is left unresolved here (both a plain "i1,i3,i2 & i1,i4,i3" split and
    its mirror are geometrically valid faces) -- see _heightfield_reorient(), which fixes winding
    for the whole mesh in one pass instead of requiring every call site to work it out by hand."""
    if style == "quincunx":
        i5 = len(pts)
        pts.append([(pts[i1][k] + pts[i2][k] + pts[i3][k] + pts[i4][k]) / 4 for k in range(3)])
        tris = [[i1, i5, i2], [i2, i5, i3], [i3, i5, i4], [i4, i5, i1]]
    elif style == "alt":
        tris = [[i1, i4, i2], [i2, i4, i3]]
    else:
        tris = [[i1, i3, i2], [i1, i4, i3]]
    return [t for t in tris if _heightfield_tri_area(pts, t) > 1e-9]


def _heightfield_dedupe(pts: Sequence[Sequence[float]], faces: Sequence[Sequence[int]], ndigits: int = 6) -> tuple[list[list[float]], list[list[int]]]:
    """Merge points landing on the same position (sub-micron at typical mm board-game scale).

    BOSL2's own cylindrical_heightfield() algorithm legitimately produces this: the "back of the
    tube" fill points snap to whichever end of the cylinder (z=+l/2 or z=-l/2) is nearest, so
    several consecutive rows can share literally identical positions there but at different grid
    indices. Left un-merged, that turns into a naked seam once degenerate triangles get dropped.
    """
    remap: Sequence[float] = []
    seen: dict[tuple[float, float, float], int] = {}
    merged: list[list[float]] = []
    for p in pts:
        key = (round(p[0], ndigits), round(p[1], ndigits), round(p[2], ndigits))
        i = seen.get(key)
        if i is None:
            i = len(merged)
            seen[key] = i
            merged.append([float(v) for v in p])
        remap.append(i)
    out_faces = []
    for f in faces:
        nf = [remap[i] for i in f]
        if len(set(nf)) >= 3:
            out_faces.append(nf)
    return merged, out_faces


def _heightfield_reorient(pts: Sequence[Sequence[float]], faces: list[list[int]]) -> list[list[int]]:
    """Flood-fill the face list to one globally-consistent winding (every shared edge used in
    opposite directions by its two faces), then flip everything if needed so the winding matches
    OpenSCAD's polyhedron() convention (clockwise as seen from outside).

    This lets every face-building loop above stay simple, unflipped index math instead of having
    to derive the correct BOSL2-style reverse=true/false flag by hand for every patch (top/bottom/
    walls, or the wrapped lateral tube surface) -- which is easy to get subtly wrong per-patch.
    """
    edge_faces: dict[frozenset[int], list[int]] = {}
    for fi, f in enumerate(faces):
        n = len(f)
        for i in range(n):
            edge_faces.setdefault(frozenset((f[i], f[(i + 1) % n])), []).append(fi)

    visited = [False] * len(faces)
    for start in range(len(faces)):
        if visited[start]:
            continue
        visited[start] = True
        stack = [start]
        while stack:
            fi = stack.pop()
            f = faces[fi]
            n = len(f)
            for i in range(n):
                a, b = f[i], f[(i + 1) % n]
                for fj in edge_faces[frozenset((a, b))]:
                    if fj == fi or visited[fj]:
                        continue
                    nf = faces[fj]
                    m = len(nf)
                    if any(nf[j] == a and nf[(j + 1) % m] == b for j in range(m)):
                        faces[fj] = list(reversed(nf))
                    visited[fj] = True
                    stack.append(fj)

    volume = 0.0
    for f in faces:
        v0 = pts[f[0]]
        for i in range(1, len(f) - 1):
            v1, v2 = pts[f[i]], pts[f[i + 1]]
            volume += (
                v0[0] * (v1[1] * v2[2] - v1[2] * v2[1])
                - v0[1] * (v1[0] * v2[2] - v1[2] * v2[0])
                + v0[2] * (v1[0] * v2[1] - v1[1] * v2[0])
            )
    return [list(reversed(f)) for f in faces] if volume > 0 else faces


def _heightfield_polyhedron(pts: Sequence[Sequence[float]], faces: Sequence[Sequence[int]]) -> tuple[PyOpenSCAD, list[list[float]]]:
    pts, faces = _heightfield_dedupe(pts, faces)
    faces = _heightfield_reorient(pts, faces)
    return _opolyhedron(pts, faces), pts


def _heightfield_range(rng: Sequence[float]) -> list[float]:
    """Expand this port's [start, step, stop] stand-in for an OpenSCAD [start:step:stop] range
    literal into a plain list of values, inclusive of stop."""
    start, step, stop = rng
    n = int(round((stop - start) / step))
    return [start + i * step for i in range(n + 1)]


def _cylindrical_point(r: float, theta_deg: float, z: float) -> list[float]:
    th = math.radians(theta_deg)
    return [r * math.cos(th), r * math.sin(th), z]


def interior_fillet(
    l: float = 1.0,
    r: float | None = None,
    ang: float = 90,
    overlap: float = 0.01,
    d: float | None = None,
    anchor: Sequence[float] = FRONT + LEFT,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 interior_fillet() -- a shape to fillet an interior corner between two faces.

    Args:
        l:       length of the edge to fillet (default 1.0)
        r:       radius of the fillet
        ang:     angle between the faces to fillet in degrees (default 90)
        overlap: overlap size for unioning with the faces (default 0.01)
        d:       diameter of the fillet
        anchor:  anchor point (default FRONT+LEFT)
        spin:    Z-axis rotation in degrees after anchor (default 0)
        orient:  direction to rotate the top towards, after spin (default UP)
    """
    from .shapes2d import _opolygon

    rad = _pick_radius(r=r, d=d, dflt=1)
    n = _frag_count(rad)
    path = _interior_fillet_path(rad, ang, overlap, n)
    shape = _opolygon(path).linear_extrude(height=l, center=True)
    pts3d = [[p[0], p[1], z] for z in (-l / 2, l / 2) for p in path]
    offset = _anchor_offset_hull3(pts3d, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def heightfield(
    data: "Callable[[float, float], float | None] | Sequence[Sequence[float]]",
    size: Sequence[float] = [100, 100],
    bottom: float = -20,
    maxz: float = 99,
    xrange: Sequence[float] = [-1, 0.04, 1],
    yrange: Sequence[float] = [-1, 0.04, 1],
    style: str = "default",
    convexity: int = 10,
    anchor: Sequence[float] = CENTER,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 heightfield() -- a 3-D surface from a 2-D array of heights or a function literal.

    Args:
        data:      2-D rectangular array of heights, or a function literal taking (x, y)
        size:      [X,Y] size of the surface (default [100,100])
        bottom:    Z coordinate for the bottom of the object (default -20)
        maxz:      maximum height to model, taller values are truncated (default 99)
        xrange:    [start, step, stop] range of X values for a function-literal surface
        yrange:    [start, step, stop] range of Y values for a function-literal surface
        style:     quad subdivision style: "default", "alt", "quincunx" (default "default")
        convexity: max number of times a line can cross the surface wall (default 10)
        anchor:    anchor point (default CENTER)
        spin:      Z-axis rotation in degrees (default 0)
        orient:    direction to rotate the top towards (default UP)
    """
    sz = [size, size] if isinstance(size, (int, float)) else list(size)
    style_key = style if style in ("alt", "quincunx") else "default"

    if callable(data):
        xvals = _heightfield_range(xrange)
        yvals = _heightfield_range(yrange)
        xcnt, ycnt = len(xvals), len(yvals)
        minx, maxx = min(xvals), max(xvals)
        miny, maxy = min(yvals), max(yvals)

        def xy_at(xi: int, yi: int) -> tuple[float, float]:
            fx = (xvals[xi] - minx) / (maxx - minx) if maxx > minx else 0.0
            fy = (yvals[yi] - miny) / (maxy - miny) if maxy > miny else 0.0
            return sz[0] * (fx - 0.5), sz[1] * (fy - 0.5)

        def height_at(xi: int, yi: int) -> float:
            z = data(xvals[xi], yvals[yi])
            return min(maxz, max(bottom + 0.1, 0.0 if z is None else z))
    else:
        ycnt, xcnt = len(data), len(data[0])

        def xy_at(xi: int, yi: int) -> tuple[float, float]:
            fx = xi / (xcnt - 1) if xcnt > 1 else 0.0
            fy = yi / (ycnt - 1) if ycnt > 1 else 0.0
            return sz[0] * (fx - 0.5), sz[1] * (fy - 0.5)

        def height_at(xi: int, yi: int) -> float:
            return min(max(data[yi][xi], bottom + 0.1), maxz)

    top = [[0.0, 0.0, 0.0] for _ in range(xcnt * ycnt)]
    for yi in range(ycnt):
        for xi in range(xcnt):
            x, y = xy_at(xi, yi)
            top[yi * xcnt + xi] = [x, y, height_at(xi, yi)]

    pts = list(top)
    bo = len(pts)
    pts += [[p[0], p[1], bottom] for p in top]

    def idx(row: int, col: int) -> int:
        return row * xcnt + col

    faces: list[list[int]] = []
    for r in range(ycnt - 1):
        for c in range(xcnt - 1):
            faces += _heightfield_tris(pts, idx(r, c), idx(r + 1, c), idx(r + 1, c + 1), idx(r, c + 1), style_key)
            faces += _heightfield_tris(pts, bo + idx(r, c), bo + idx(r + 1, c), bo + idx(r + 1, c + 1), bo + idx(r, c + 1), style_key)
    for c in range(xcnt - 1):
        faces += _heightfield_tris(pts, idx(0, c), bo + idx(0, c), bo + idx(0, c + 1), idx(0, c + 1), "default")
        r = ycnt - 1
        faces += _heightfield_tris(pts, idx(r, c), bo + idx(r, c), bo + idx(r, c + 1), idx(r, c + 1), "default")
    for r in range(ycnt - 1):
        faces += _heightfield_tris(pts, idx(r, 0), bo + idx(r, 0), bo + idx(r + 1, 0), idx(r + 1, 0), "default")
        c = xcnt - 1
        faces += _heightfield_tris(pts, idx(r, c), bo + idx(r, c), bo + idx(r + 1, c), idx(r + 1, c), "default")

    shape, pts = _heightfield_polyhedron(pts, faces)
    offset = _anchor_offset_hull3(pts, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def cylindrical_heightfield(
    data: "Callable[[float, float], float | None] | Sequence[Sequence[float]]",
    l: float | None = None,
    r: float | None = None,
    base: float = 1,
    transpose: bool = False,
    aspect: float = 1,
    style: str = "min_edge",
    convexity: int = 10,
    xrange: Sequence[float] = [-1, 0.01, 1],
    yrange: Sequence[float] = [-1, 0.01, 1],
    maxh: float = 99,
    r1: float | None = None,
    r2: float | None = None,
    d: float | None = None,
    d1: float | None = None,
    d2: float | None = None,
    h: float | None = None,
    height: float | None = None,
    anchor: Sequence[float] = CTR,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 cylindrical_heightfield() -- wraps a heightfield surface around a cylinder.

    Args:
        data:      2-D rectangular array of heights, or a function literal taking (x, y)
        l:         length of the cylinder to wrap around
        r:         radius of the cylinder to wrap around
        base:      radius for the bottom of the object (default 1)
        transpose: swap the radial and length axes of the data (default False)
        aspect:    aspect ratio of the generated heightfield at the cylinder surface (default 1)
        style:     quad subdivision style: "default", "alt", "quincunx" (default "min_edge")
        convexity: max number of times a line can cross the surface wall (default 10)
        xrange:    [start, step, stop] range of X values for a function-literal surface
        yrange:    [start, step, stop] range of Y values for a function-literal surface
        maxh:      maximum height above the radius to model (default 99)
        r1/r2:     radius of the bottom/top of the cylinder to wrap around
        d/d1/d2:   diameter of the cylinder to wrap around / bottom / top
        h/height:  alternate names for l (length of the cylinder)
        anchor:    anchor point (default CENTER)
        spin:      Z-axis rotation in degrees (default 0)
        orient:    direction to rotate the top towards (default UP)
    """
    l_val = l if l is not None else (h if h is not None else height)
    assert l_val is not None and l_val > 0, "Must supply one of l=, h=, or height= as a finite positive number."
    r1v = _pick_radius(r1=r1, d1=d1, r=r, d=d)
    r2v = _pick_radius(r1=r2, d1=d2, r=r, d=d)
    assert r1v is not None and r1v > 0, "Must supply one of r=, r1=, d=, or d1= as a finite positive number."
    assert r2v is not None and r2v > 0, "Must supply one of r=, r2=, d=, or d2= as a finite positive number."
    assert base > 0, "base= must be a finite positive number."

    style_key = style if style in ("alt", "quincunx") else "default"

    if callable(data):
        xvals = _heightfield_range(xrange)
        yvals = _heightfield_range(yrange)
    else:
        xvals = list(range(len(data[0])))
        yvals = list(range(len(data)))
    xlen, ylen = len(xvals), len(yvals)

    stepy = l_val / (ylen - 1)
    stepx = stepy * aspect
    maxr = max(r1v, r2v)
    circ = 2 * math.pi * maxr
    astep = 360 / circ * stepx
    arc = astep * (xlen - 1)
    assert stepx * xlen <= circ, f"heightfield ({xlen} x {ylen}) needs a radius of at least {maxr * stepx * xlen / circ}."
    bsteps = max(1, round(_frag_count(maxr - base) * arc / 360))
    bstep = arc / bsteps

    rows: list[list[list[float]]] = []
    for yi in range(ylen):
        z = yi * stepy - l_val / 2
        t = yi / (ylen - 1) if ylen > 1 else 0.0
        rr = r1v + (r2v - r1v) * t
        row = [_cylindrical_point(rr - base, -arc / 2, z)]
        for xi in range(xlen):
            a = xi * astep
            if callable(data):
                raw = data(yvals[yi], xvals[xi]) if transpose else data(xvals[xi], yvals[yi])
            else:
                raw = data[xi][yi] if transpose else data[yi][xi]
            rad = min(maxh, max(0.01 - base, 0.0 if raw is None else raw))
            row.append(_cylindrical_point(rr + rad, a - arc / 2, z))
        row.append(_cylindrical_point(rr - base, arc / 2, z))
        for b in range(1, bsteps):
            a = arc / 2 - b * bstep
            redge = r2v if z > 0 else r1v
            row.append(_cylindrical_point(redge - base, a, l_val / 2 if z > 0 else -l_val / 2))
        rows.append(row)

    cols = len(rows[0])
    pts = [p for row in rows for p in row]

    def idx(row: int, col: int) -> int:
        return row * cols + (col % cols)

    faces: list[list[int]] = []
    for r in range(ylen - 1):
        for c in range(cols):
            faces += _heightfield_tris(pts, idx(r, c), idx(r + 1, c), idx(r + 1, c + 1), idx(r, c + 1), style_key)
    faces.append(list(range(0, cols)))
    faces.append(list(range((ylen - 1) * cols, ylen * cols)))

    shape, pts = _heightfield_polyhedron(pts, faces)
    offset = _anchor_offset_cyl(r1v, r2v, l_val, anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=None, anchor=anchor)


def plot3d(f, x, y, zclip=None, zspan=None, base: float = 1, style: str = "default") -> Bosl2Solid:
    """A surface plot of ``z = f(x, y)`` over a grid of *x*, *y* values (BOSL2 plot3d()).

    Args:
        f:     a callable ``f(x, y) -> z``
        x, y:  strictly increasing lists of sample coordinates
        zclip: [zmin, zmax] to clamp the surface (default no clip)
        zspan: [zmin, zmax] to rescale the surface height into (default no rescale)
        base:  thickness of solid base below the surface; 0 gives just the (open) surface (default 1)
        style: vnf_vertex_array quad-subdivision style

    Examples:
        A rippled surface plotted as a solid slab:

        .. pythonscad-example::

            s3.plot3d(lambda x, y: 6 * math.cos(math.hypot(x, y) / 6),
                      list(range(-30, 31, 3)), list(range(-30, 31, 3))).show()
    """
    from bosl2.vnf import VNF

    xs, ys = list(x), list(y)
    zlo, zhi = (zclip if zclip is not None else [-math.inf, math.inf])
    data = [[[float(xi), float(yi), min(max(float(f(xi, yi)), zlo), zhi)] for yi in ys] for xi in xs]
    assert len(data) > 1 and len(data[0]) > 1, "plot3d(): x and y must each give at least 2 points."
    if zspan is not None:
        allz = [p[2] for row in data for p in row]
        minv, maxv = min(allz), max(allz)
        scale = (zspan[1] - zspan[0]) / (maxv - minv)
        data = [[[p[0], p[1], scale * (p[2] - minv) + zspan[0]] for p in row] for row in data]
    if base == 0:
        vnf = VNF.vertex_array(data, style=style)
    else:
        allz = [p[2] for row in data for p in row]
        bottom = (zspan[0] - base) if zspan is not None else (min(allz) - base)
        skirted = ([[[p[0], p[1], bottom] for p in data[0]]] + data
                   + [[[p[0], p[1], bottom] for p in data[-1]]])
        tdata = [[skirted[i][j] for i in range(len(skirted))] for j in range(len(skirted[0]))]
        vnf = VNF.vertex_array(tdata, col_wrap=True, caps=True, style=style, reverse=True)
        if vnf.volume() < 0:  # ensure outward winding for a valid manifold solid
            vnf = vnf.reverse()
    return Bosl2Solid(vnf.polyhedron())


def plot_revolution(f, angle, z=None, r=None, r1=None, r2=None, d=None, d1=None, d2=None,
                    path=None, rclip=None, rspan=None, horiz: bool = False,
                    style: str = "min_edge") -> Bosl2Solid:
    """A surface of revolution whose radius is modulated by ``r = f(angle, z)`` (BOSL2 plot_revolution()).

    The profile is either a straight taper (*z* plus *r1*/*r2*) or an explicit 2-D *path* of
    ``[r, z]`` points; ``f(theta, z)`` displaces each profile point along its normal (or radially,
    with *horiz*). A full 360-degree *angle* range revolves seamlessly; a partial range is capped
    to the axis. The BOSL2 ``arclength`` form is not ported.

    Args:
        f:      a callable ``f(theta_degrees, z) -> radial displacement``
        angle:  a strictly increasing list/range of revolution angles in degrees
        z:      strictly increasing profile heights (with *r1*/*r2*)
        r1/r2/r/d1/d2/d: the profile's bottom/top radius (straight taper form)
        path:   an explicit ``[[r, z], ...]`` profile (instead of z + radii)
        rclip:  [rmin, rmax] to clamp the modulated radius
        rspan:  [rmin, rmax] to rescale the displacement into
        horiz:  displace radially (normal [1, 0]) instead of along the profile normal
        style:  vnf_vertex_array quad-subdivision style

    Examples:
        A vase whose radius ripples with height and angle:

        .. pythonscad-example::

            s3.plot_revolution(lambda a, z: 3 * math.sin(math.radians(4 * a)) * (z / 30),
                               angle=list(range(0, 361, 6)), z=list(range(0, 31, 2)),
                               r1=12, r2=8).show()
    """
    from bosl2.vnf import VNF
    from bosl2.paths import Path

    r1v = r1 if r1 is not None else (r if r is not None else (d1 / 2 if d1 is not None else (d / 2 if d is not None else None)))
    r2v = r2 if r2 is not None else (r if r is not None else (d2 / 2 if d2 is not None else (d / 2 if d is not None else None)))
    theta = list(angle)
    assert len(theta) > 1, "plot_revolution(): angle must have at least 2 values."
    if path is not None:
        prof = [[float(p[0]), float(p[1])] for p in path]
    else:
        zs = list(z)
        assert r1v is not None and r2v is not None and len(zs) > 1, "plot_revolution(): give z with r1 and r2 (or a path)."
        z0, z1 = zs[0], zs[-1]
        prof = [[r1v + (r2v - r1v) * (zz - z0) / (z1 - z0), zz] for zz in zs]
    normals = [[1.0, 0.0]] * len(prof) if horiz else np.asarray(Path._path_normals(prof), dtype=float).tolist()
    rlo, rhi = (rclip if rclip is not None else [-math.inf, math.inf])
    rdata = [[min(max(float(f(t, pt[1])), rlo), rhi) for t in theta] for pt in prof]
    if rspan is not None:
        allv = [v for row in rdata for v in row]
        minv, maxv = min(allv), max(allv)
        sc = (rspan[1] - rspan[0]) / (maxv - minv)
        rdata = [[sc * (v - minv) + rspan[0] for v in row] for row in rdata]
    closed = (theta[-1] - theta[0]) == 360
    rmin = 0.01
    grid = []
    for i, pt in enumerate(prof):
        row = [] if closed else [[0.0, 0.0, pt[1]]]
        for j, t in enumerate(theta):
            rr = max(rmin, pt[0] + rdata[i][j] * normals[i][0])
            zz = pt[1] + rdata[i][j] * normals[i][1]
            row.append([rr * math.cos(math.radians(t)), rr * math.sin(math.radians(t)), zz])
        grid.append(row)
    vnf = VNF.vertex_array(grid, col_wrap=True, caps=True, style=style)
    if vnf.volume() < 0:
        vnf = vnf.reverse()
    return Bosl2Solid(vnf.polyhedron())


def fillet(l=None, r: float | None = None, ang: float = 90, r1: float | None = None,
           r2: float | None = None, d: float | None = None, d1: float | None = None,
           d2: float | None = None, excess: float = 0.01, h=None, height=None, length=None,
           _fn: float | None = None, _fa: float | None = None, _fs: float | None = None) -> Bosl2Solid:
    """A concave edge-fillet mask of length *l* and radius *r* (BOSL2 fillet()).

    A cutter you subtract to round a 90-degree edge (the concave complement of a rounded corner).
    Positioned manually like ``rounding_edge_mask`` -- origin at the sharp edge, +X/+Y into the
    material, centered along its own Z. Only 90-degree edges are ported (BOSL2's ``ang`` for other
    dihedral angles is not).

    Examples:
        .. pythonscad-example::

            block = s3.cuboid([30, 30, 20])
            mask = s3.fillet(l=20, r=6).right(15).forward(15)
            (block - mask).show()
    """
    from . import masking

    assert ang == 90, "fillet(): only 90-degree edges (ang=90) are supported in this port."
    lv = l if l is not None else (h if h is not None else (height if height is not None else (length if length is not None else 1)))
    return Bosl2Solid(masking.rounding_edge_mask(l=lv, r=r, r1=r1, r2=r2, d=d, d1=d1, d2=d2,
                                                 excess=excess, _fn=_fn, _fa=_fa, _fs=_fs))


def textured_tile(texture, size, tex_reps=None, tex_size=None, tex_depth: float = 1,
                  tex_inset=False, style: str = "min_edge") -> Bosl2Solid:
    """A rectangular tile carrying a repeated height-field *texture* (BOSL2 textured_tile()).

    Only the height-field texture form is ported: *texture* is a 2-D array of scalar heights (0..1),
    tiled *tex_reps* times (or ``tex_size`` chosen) across the *size* rectangle and raised by
    *tex_depth*. VNF-tile textures and BOSL2's named-texture table are not ported.

    Args:
        texture:   a 2-D array (rows x cols) of scalar heights in [0, 1]
        size:      [x, y] size of the tile
        tex_reps:  integer or [nx, ny] tile repetitions (give this or *tex_size*)
        tex_size:  target tile size, from which the repetition count is computed
        tex_depth: how far the texture is raised (default 1); negative inverts it
        tex_inset: lower the texture into the surface by this fraction (True == full depth)
        style:     vnf_vertex_array quad-subdivision style

    Examples:
        A pyramid-bump tile:

        .. pythonscad-example::

            bump = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
            s3.textured_tile(bump, size=[40, 40], tex_reps=[4, 4], tex_depth=3).show()
    """
    sz = [float(size[0]), float(size[1])]
    rows, cols = len(texture), len(texture[0])
    if tex_reps is None:
        assert tex_size is not None, "textured_tile(): give tex_reps or tex_size."
        ts = [float(tex_size), float(tex_size)] if isinstance(tex_size, (int, float)) else [float(tex_size[0]), float(tex_size[1])]
        tex_reps = [max(1, round(sz[0] / ts[0])), max(1, round(sz[1] / ts[1]))]
    reps = [int(tex_reps[0]), int(tex_reps[1])] if hasattr(tex_reps, "__len__") else [int(tex_reps), int(tex_reps)]
    inset = 1.0 if tex_inset is True else float(tex_inset or 0)
    tiled = [[(float(texture[r][c]) - inset) * tex_depth
              for _rx in range(reps[0]) for c in range(cols)]
             for _ry in range(reps[1]) for r in range(rows)]
    flat = [v for row in tiled for v in row]
    bottom = min(flat) - 0.1
    return heightfield(tiled, size=sz, bottom=bottom, style=style)


def ruler(
    length: float = 100,
    width: float | None = None,
    thickness: float = 1,
    depth: int = 3,
    labels: bool = False,
    pipscale: float = 1 / 3,
    maxscale: float | None = None,
    colors: list[str] = ["black", "white"],
    alpha: float = 1.0,
    unit: float = 1,
    inch: bool = False,
    anchor: Sequence[float] = LEFT + BACK + TOP,
    spin: float = 0,
    orient: Sequence[float] = UP,
) -> Bosl2Solid:
    """BOSL2 ruler() -- a ruler for measuring objects in the viewport.

    Args:
        length:    length of the ruler (default 100)
        width:     width of the ruler (default: size of the largest unit division)
        thickness: thickness of the ruler (default 1)
        depth:     depth of the mark subdivisions (default 3)
        labels:    draw numeric labels for depths larger than 1 (default False)
        pipscale:  width scale of the pips relative to the next size up (default 1/3)
        maxscale:  log10 of the maximum width divisions to display (default: based on length)
        colors:    two colours to alternate for the ruler (default ["black","white"])
        alpha:     transparency value (default 1.0)
        unit:      unit to mark; scales the ruler marks to a different length (default 1)
        inch:      scale the ruler to inches, assuming a mm base dimension (default False)
        anchor:    anchor point (default LEFT+BACK+TOP)
        spin:      Z-axis rotation in degrees (default 0)
        orient:    direction to rotate the top towards (default UP)
    """
    from .shapes2d import _opolygon

    assert depth <= 5, "Cannot render scales smaller than depth=5"
    assert len(colors) == 2, "'colors' must contain a list of exactly two colors."

    length_v = INCH * length if inch else length
    unit_v = INCH * unit if inch else unit
    maxscale_v = maxscale if maxscale is not None else math.floor(math.log10(length_v / unit_v - 1e-9))
    ms = int(round(maxscale_v))
    scales = [unit_v * 10**logsize for logsize in range(ms, ms - depth, -1)]
    widthfactor = (1 - pipscale) / (1 - pipscale**depth)
    width_v = width if width is not None else scales[0]
    widths = [width_v * widthfactor * pipscale ** (-logsize) for logsize in range(0, -depth, -1)]
    offsets = [0.0]
    for w in widths:
        offsets.append(offsets[-1] + w)

    pieces: list[PyOpenSCAD] = []
    for i in range(len(scales)):
        scale = scales[i]
        count = math.ceil(length_v / scale)
        log_arg = max(count * scale / unit_v, 1e-9)
        fontsize = 0.5 * min(widths[i], scale / max(1, math.ceil(math.log10(log_arg))))
        for idx in range(count):
            actlen = scale if (idx < count - 1 or abs(length_v % scale) < 1e-9) else length_v % scale
            x0 = idx * scale
            y0 = offsets[i]
            tick = _ocube([actlen, widths[i], thickness], center=True).translate([x0 + actlen / 2, y0 + widths[i] / 2, 0])
            pieces.append(tick.color(colors[idx % 2], alpha=alpha))

            if i == 0 and idx % 10 == 0 and idx != 0:
                mark = 0
            elif i == 0 and idx % 10 == 9 and idx != count - 1:
                mark = 1
            elif idx % 10 == 4:
                mark = 1
            elif idx % 10 == 5:
                mark = 0
            else:
                mark = -1
            flip = 1 - mark * 2
            if mark >= 0:
                marklength = min(widths[i] / 2, scale * 2)
                markwidth = marklength * 0.4
                tri = _opolygon([[0, 0], [flip * markwidth, -marklength], [0, -marklength * 0.9]])
                piece = (
                    tri.linear_extrude(height=thickness + scale / 100, convexity=2, center=True)
                    .translate([x0 + mark * scale, y0 + widths[i], 0])
                    .color(colors[1 - idx % 2], alpha=alpha)
                )
                pieces.append(piece)

            if labels and scale / unit_v + 1e-9 >= 1:
                lbl = _text2d(str(idx * scale / unit_v), size=fontsize, halign="left", valign="baseline")
                piece = (
                    lbl.translate([0, scale * 0.02, 0])
                    .linear_extrude(height=thickness + scale / 100, convexity=2, center=True)
                    .translate([x0, y0, 0])
                    .color(colors[(idx + 1) % 2], alpha=alpha)
                )
                pieces.append(piece)

    base = pieces[0]
    for p in pieces[1:]:
        base = base | p
    shape = base.translate([-length_v / 2, -width_v / 2, 0])

    offset = _anchor_offset_box3([length_v, width_v, thickness], anchor)
    return Bosl2Solid(_finish3(shape, offset, spin, orient), size=[length_v, width_v, thickness], anchor=anchor)
