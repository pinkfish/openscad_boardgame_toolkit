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

# LibFile: no_lid.py
#    Boxes with no lids.
#
# FileSummary: Boxes with no lids.
# FileGroup: Boxes

from __future__ import annotations
import math
import types
from dataclasses import dataclass, field, replace

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import numpy as np
import pybosl2.masking
import pybosl2.shapes3d
from pybosl2 import shapes2d
from pybosl2 import Path2D
from pybosl2 import Region
from components import FingerHoleWall, MagnetSlot, MAGNET_SLOT_TYPE_NONE
from box_base import Body, BoxBaseType, BoxSpec, BoxTypeOptions, Interior

from typing import Callable


# No osuse() here: the region algebra the raised-floor ("extra_floors") geometry needs runs
# on pybosl2's own Region booleans instead. That is a crash-avoidance measure, not a
# preference -- a failing assert inside an osuse'd .scad function ABORTS THE PROCESS rather
# than raising, so bad outline input could not even be reported. See
# tests/repro_osuse_assert_aborts.py.

STACKABLE_TYPE_NONE = 0
STACKABLE_TYPE_INSIDE = 1
STACKABLE_TYPE_OUTSIDE = 2


def SortExtraFloors(lst: list[types.SimpleNamespace]) -> list[types.SimpleNamespace]:
    """Sorts a list of extra-floor data objects by .floor_height."""
    return sorted(lst, key=lambda f: f.floor_height)


class NoLidBox(BoxBaseType):
    """A box with no lid -- a spacer, or an open tray, on the new box system.

    Unlike a lidded box, a no-lid box is **solid by default** (a spacer). Pass
    ``BoxSpec(hollow=True)`` for the common open-tray form, or give ``contents`` to
    carve compartments. There is no lid, so :meth:`make_lid` raises.

    Usage::

        from box_base import BoxSpec
        from no_lid import NoLidBox

        NoLidBox(BoxSpec(size=[100, 50, 20], label="spacer")).make_box()             # solid
        NoLidBox(BoxSpec(size=[100, 50, 20], label="tray", hollow=True)).make_box()  # open
    """


    def _compute_interior(self) -> Interior:
        # No lid to subtract -- the interior runs from the floor to the open top.
        wt = self.wall_thickness
        return Interior(
            origin=(wt, wt, self.floor_thickness),
            size=(self.width - wt * 2, self.length - wt * 2, self.height - self.floor_thickness),
        )

    def _hollow_when_empty(self) -> bool:
        # A no-lid box with nothing in it is a solid spacer unless hollow=True.
        return False

    def _build_box_body(self, contents) -> "Bosl2Solid":
        # A fully-rounded box (all edges + corners) -- the no-lid look. (The .scad
        # original layered face_profile/corner_profile roundovers; pybosl2's
        # corner_profile is currently broken, and a single rounding= is equivalent
        # at this scale and robust.)
        body = pybosl2.shapes3d.cuboid(
            [self.width, self.length, self.height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness / 2,
        )
        return Body(
            body.color(self.material_colour),
            hollowed=True,
        )


def FingerHoleWallSegment(
    path: list[list[float]],
    finger_hole_size: float,
    finger_hole_height: float,
    height: float,
    wall_thickness: float,
    make_finger_x: bool | None = None,
    make_finger_y: bool | None = None,
) -> PyOpenSCAD | None:
    """Makes a single finger-hole-wall segment for one edge of a path box.

    Places a rounded finger-wall hole on the side of the box at the correct
    direction and length, returning None if this segment doesn't qualify.

    Usage::

        FingerHoleWallSegment([[0, 0], [50, 50]], finger_hole_size=5,
                              finger_hole_height=4, height=7, make_finger_x=True, wall_thickness=2)

    Args:
        path:   the path to generate for (exactly 2 points / one line segment)
        finger_hole_size:   the size of the finger hole
        finger_hole_height: the height of the finger hole
        height: the height of the box
        wall_thickness: thickness of the walls
        make_finger_x: makes a finger dip on the x axis
        make_finger_y: makes a finger dip on the y axis
    """
    assert len(path) == 2, f"Path2D must be exactly 2 elements long path_length={len(path)}"
    assert finger_hole_size > 0, f"Need finger hole size > 0, finger_hole_size={finger_hole_size}"
    assert finger_hole_height > 0, f"Need finger hole height > 0, finger_hole_height={finger_hole_height}"
    assert height > 0, f"Need height > 0, height={height}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"

    seg = Path2D(path, closed=False)
    split_length = seg.perimeter()
    normal = seg.normals()
    if normal[0][0] == 0:
        angle = 90 if normal[0][1] > 0 else -90
    else:
        angle = math.degrees(math.atan(normal[0][1] / normal[0][0]))

    use_finger = make_finger_y if (-90 < angle < 90) else make_finger_x
    if not (split_length > finger_hole_size * 2.5 and use_finger):
        return None

    pts = seg.cut_points([split_length / 2])
    return (
        FingerHoleWall(
            radius=finger_hole_size,
            height=finger_hole_height,
            spin=90,
            depth_of_hole=wall_thickness + 0.03,
            rounding_edge=wall_thickness / 2,
        )
        .rotate([0, 0, angle])
        .translate([pts[0].point[0], pts[0].point[1], height - finger_hole_height + 0.01])
    )


class PathBoxWithNoLid:
    """Builds a no-lid box from a polygon outline.

    This used to be one long function whose intermediate pieces (the rounded outer path, the
    five inset paths, the finger-hole sizing) were threaded through nested closures. They are
    instance attributes now, so each stage is a method that reads them rather than a closure
    capturing them, and a caller can build a box in stages or inspect the derived paths.
    :func:`MakePathBoxWithNoLid` is the thin functional wrapper over it.

    The 2-D work splits deliberately (see Path2D.offset): the outline insets are POINT
    math, done in numpy, because the wall-segment features have to walk each edge; everything
    that only needs a shape to extrude uses the native primitives instead.

    Attributes:
        path/height/...:        the constructor arguments, defaults resolved
        width/length:           bounding size of the outline
        sorted_floors:          extra_floors ordered by floor_height
        outside_path/main_path: the outline before rounding, with extra floors merged/cut
        calc_path:              outer path with corners rounded by wall_thickness
        inner_path:             outline inset by the wall -- the hollow cut's profile
        inner_path_stackable*:  the inset outlines the stackable rings are built from
        middle_path:            outline inset by half a wall; the finger holes walk its edges
    """

    def __init__(
        self,
        path: list[list[float]],
        height: float,
        children: "PyOpenSCAD | Callable | None" = None,
        wall_thickness: float | None = None,
        floor_thickness: float | None = None,
        stackable_thickness: float | None = None,
        stackable_fit_offset: float = 0.1,
        hollow_radius: types.SimpleNamespace | None = None,
        make_finger_x: bool | None = None,
        make_finger_y: bool | None = None,
        material_colour: Color = Color("grey"),
        finger_hole_size: float | None = None,
        offset_sweep_options: types.SimpleNamespace | None = None,
        hollow: bool = False,
        stackable: int = STACKABLE_TYPE_NONE,
        magnet: types.SimpleNamespace | None = None,
        extra_floors: list[types.SimpleNamespace] | None = None,
        mesh_res: int = 10,
    ) -> None:
        self.path = path
        self.height = height
        self.children = children
        self.wall_thickness = default_wall_thickness if wall_thickness is None else wall_thickness
        self.floor_thickness = default_floor_thickness if floor_thickness is None else floor_thickness
        self.stackable_thickness = default_stackable_thickness if stackable_thickness is None else stackable_thickness
        self.stackable_fit_offset = stackable_fit_offset
        self.hollow_radius = (
            hollow_radius
            if hollow_radius is not None
            else types.SimpleNamespace(
                top=self.wall_thickness / 4, bottom=self.wall_thickness / 4, radius=self.wall_thickness / 2
            )
        )
        self.material_colour = material_colour
        self.hollow = hollow
        self.stackable = stackable
        self.magnet = (
            magnet
            if magnet is not None
            else types.SimpleNamespace(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0], height=0)
        )
        self.extra_floors = extra_floors if extra_floors is not None else []
        # offset_sweep_options/mesh_res are vestigial (the solids are OffsetSweep() now); kept
        # so existing call sites don't break.
        self.offset_sweep_options = offset_sweep_options
        self.mesh_res = mesh_res

        assert len(path) >= 3, f"Path2D must be at least 3 elements long path_length={len(path)}"
        assert self.floor_thickness > 0, f"Need floor thickness > 0, floor_thickness={self.floor_thickness}"
        assert self.wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={self.wall_thickness}"
        assert height > 0, f"Need height > 0, height={height}"

        self._measure(make_finger_x, make_finger_y, finger_hole_size)
        self._resolve_paths()

    # -- setup -----------------------------------------------------------------------------

    def _measure(self, make_finger_x, make_finger_y, finger_hole_size) -> None:
        """Bounding size of the outline and the finger-hole sizing derived from it."""
        pts = np.asarray(self.path, dtype=float)
        self.width = float(pts[:, 0].max() - pts[:, 0].min())
        self.length = float(pts[:, 1].max() - pts[:, 1].min())

        self.finger_hole_size = finger_hole_size
        if self.finger_hole_size is None:
            self.finger_hole_size = min(20, min(self.length, self.width) / 4, self.height - self.floor_thickness + 1)
        self.finger_hole_height = min(self.finger_hole_size, self.height - default_floor_thickness * 2 + 1)
        auto = make_finger_x is None and make_finger_y is None
        self.make_finger_x = (self.width > self.length) if auto else False
        self.make_finger_y = (self.length > self.width) if auto else False

    def _resolve_paths(self) -> None:
        """The outline variants every later stage reads.

        Region algebra is only needed when extra_floors overlap the outline. Without them --
        every box in examples/ -- the union/difference of a single region is that region, so
        this collapses to the path itself.
        """
        wall = self.wall_thickness
        self.sorted_floors = SortExtraFloors(self.extra_floors)
        if self.sorted_floors:
            # pybosl2's own Region booleans, NOT the osuse'd BOSL2 ones: a failing assert
            # inside an osuse'd .scad function aborts the whole process instead of raising
            # (tests/repro_osuse_assert_aborts.py), and a degenerate extra-floor outline is
            # exactly the sort of input that trips one. These are pure Python.
            outside = Region([self.path])
            main = Region([self.path])
            for floor in self.sorted_floors:
                outside = outside.union(Region([floor.path]))
                main = main.difference(Region([floor.path]))
            self.outside_path = outside.paths[0]
            self.main_path = main.paths[0]
        else:
            self.outside_path = self.path
            self.main_path = self.path

        self.calc_path = Path2D(self.outside_path, closed=True).round_corners(radius=wall)
        fit = self.stackable_fit_offset
        self.inner_path = Path2D(self.main_path).offset(radius=-wall)
        self.inner_path_stackable = Path2D(self.main_path).offset(radius=-wall / 2)
        self.inner_path_stackable_bottom_outside = Path2D(self.main_path).offset(radius=-wall / 2 + fit)
        self.inner_path_stackable_bottom_inside = Path2D(self.main_path).offset(radius=-wall - fit)
        self.inner_path_stackable_bottom_inside_inside = Path2D(self.main_path).offset(radius=-wall / 2 - fit)
        self.middle_path = Path2D(self.path).offset(radius=-wall / 2)

    # -- pieces ----------------------------------------------------------------------------

    def inner(self) -> InnerPath:
        """The :class:`~base_bgtk.InnerPath` handed to a child.

        The inset outline is deliberately not precomputed for the child: `profile` closes over
        the outline and insets it with the NATIVE 2-D offset() only if the child asks, so a box
        whose children ignore the inside never pays for it, and one that does want it gets real
        geometry rather than points it would only have had to re-polygon.
        """
        outer_path = self.main_path
        wall = self.wall_thickness

        def profile(inset: float = 0.0):
            return shapes2d.polygon(outer_path).offset(radius=-(wall + float(inset)))

        return InnerPath(
            width=self.width,
            length=self.length,
            height=self.height - self.floor_thickness,
            path=outer_path,
            profile=profile,
        )

    def stackable_ring(self, bottom: bool = False) -> "Bosl2Solid | None":
        """The interlocking ring for a stackable box (was the StackableBoxInternal closure)."""
        wall, stack, fit = self.wall_thickness, self.stackable_thickness, self.stackable_fit_offset
        grow = fit if bottom else 0
        if self.stackable == STACKABLE_TYPE_INSIDE:
            outer_src = self.inner_path_stackable_bottom_outside if bottom else self.inner_path_stackable
            inner_src = self.inner_path_stackable_bottom_inside if bottom else self.inner_path
            outer = PolygonPrism(
                Path2D(outer_src, closed=True).round_corners(radius=stack / 2), h=stack + grow, rounding_top=wall / 4
            )
        elif self.stackable == STACKABLE_TYPE_OUTSIDE:
            inner_src = self.inner_path_stackable_bottom_inside_inside if bottom else self.inner_path_stackable
            outer = PolygonPrism(self.calc_path, h=stack + grow, rounding_top=wall / 4)
        else:
            return None
        inner = PolygonPrism(
            Path2D(inner_src, closed=True).round_corners(radius=stack / 4), h=stack + 0.02 + grow, rounding_top=-wall / 4
        ).translate([0, 0, -0.01])
        return outer - inner

    def outer_body(self) -> "Bosl2Solid":
        """The solid outside of the box: the main prism, its stack ring, and any extra floors."""
        wall, stack = self.wall_thickness, self.stackable_thickness
        solid = PolygonPrism(
            self.calc_path,
            h=(self.height - stack) if self.stackable else self.height,
            rounding_bottom=wall / 4 if self.stackable else wall / 2,
            rounding_top=wall / 8 if self.stackable else wall / 4,
        )
        if self.stackable:
            top = self.stackable_ring(bottom=False)
            assert top is not None
            solid = solid | top.translate([0, 0, self.height - stack])

        for f in self.sorted_floors:
            if f.floor_height > 0:
                solid = solid - PolygonPrism(f.path, h=f.floor_height)
            if f.top_height > 0:
                solid = solid - PolygonPrism(f.path, h=f.top_height).translate([0, 0, self.height - f.top_height])

        extra = None
        for f in self.sorted_floors:
            piece = PolygonPrism(
                Path2D(f.path, closed=True).round_corners(radius=wall),
                h=(self.height - f.floor_height - stack) if self.stackable else (self.height - f.floor_height),
                rounding_bottom=wall / 4 if self.stackable else wall / 2,
                rounding_top=wall / 8 if self.stackable else wall / 4,
            ).translate([0, 0, f.floor_height])
            extra = piece if extra is None else extra | piece
        return (solid | extra) if extra is not None else solid

    def internal_parts(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        """Carve the inside out of *body*: the hollow, the per-extra-floor hollows, the children.

        Everything that makes the box a container rather than a lump lives here.
        """
        if self.hollow:
            body = body - self.hollow_cut()
            for f in self.sorted_floors:
                cut = self.extra_floor_cut(f)
                if cut is not None:
                    body = body - cut
        return self.carve_children(body)

    def hollow_cut(self) -> "Bosl2Solid":
        """The main cavity."""
        return PolygonPrism(
            Path2D(self.inner_path, closed=True).round_corners(radius=self.hollow_radius.radius),
            h=self.height - self.floor_thickness,
            rounding_bottom=self.hollow_radius.bottom,
            rounding_top=0 if self.stackable else -self.hollow_radius.top,
        ).translate([0, 0, self.floor_thickness])

    def extra_floor_cut(self, f: types.SimpleNamespace) -> "Bosl2Solid | None":
        """The cavity above one raised floor."""
        if f.floor_height <= 0:
            return None
        wall = self.wall_thickness
        joined = Region([f.path]).union(Region([self.path]))
        joined_outer = Path2D(joined.paths[0], closed=True).offset(radius=-wall).round_corners(radius=wall)

        inner = Region([Path2D(f.path).offset(delta=wall)]).union(Region([self.inner_path]))
        for other in self.sorted_floors:
            if other.floor_height > f.floor_height:
                inner = inner.union(Region([Path2D(other.path).offset(delta=wall)]))
        region = Region([joined_outer]).intersection(inner).paths
        return PolygonPrism(
            region,
            h=self.height - self.floor_thickness - f.floor_height,
            rounding_bottom=self.hollow_radius.bottom,
            rounding_top=0 if self.stackable else -self.hollow_radius.top,
        ).translate([0, 0, f.floor_height + self.floor_thickness])

    def carve_children(self, body: "PyOpenSCAD") -> "Bosl2Solid":
        """Subtract the caller's children, resolving a callable against :meth:`inner`."""
        if self.children is None:
            return body
        child = self.children(self.inner()) if callable(self.children) else self.children
        if child is None:
            return body
        # A child may be a Bosl2Solid wrapper (e.g. MagnetSlot()); body is native here, and
        # native `-` doesn't accept the wrapper, so unwrap to the native solid first.
        if isinstance(child, pybosl2.shapes3d.Bosl2Solid):
            child = child.shape
        return body - child

    def carve_finger_holes(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
        """Cut a finger dip into each wall, walking the half-wall-inset outline's segments."""
        pts = self.middle_path
        count = len(pts)
        for i in range(count):
            seg = FingerHoleWallSegment(
                path=[pts[i], pts[(i + 1) % count]],
                wall_thickness=self.wall_thickness,
                finger_hole_size=self.finger_hole_size,
                finger_hole_height=self.finger_hole_height,
                make_finger_y=self.make_finger_y,
                make_finger_x=self.make_finger_x,
                height=self.height,
            )
            if seg is not None:
                body = body - seg
        return body

    # -- assembly --------------------------------------------------------------------------

    def build(self) -> "PyOpenSCAD":
        """The finished box."""
        body = self.internal_parts(self.outer_body())
        if self.stackable:
            bottom = self.stackable_ring(bottom=True)
            assert bottom is not None
            body = body - bottom.translate([0, 0, -self.stackable_fit_offset])
        body = body.color(self.material_colour)
        return self.carve_finger_holes(body)


@dataclass
class PathBoxOptions(BoxTypeOptions):
    """Options for :class:`PathBox` -- a no-lid box whose outline is a polygon.

    Pass an explicit ``path`` (a closed ``[[x, y], ...]`` outline), or build one
    from a regular polygon with :meth:`PathBox.regular_polygon`. Everything that is
    outline-specific (the stackable rings, per-edge magnets, edge finger dips, raised
    extra floors) lives here rather than on :class:`BoxSpec`, so the same rectangular
    ``BoxSpec`` machinery (positioning, height, thicknesses) is reused unchanged.

    Attributes:
        path:            closed polygon outline the box is built from
        children:        a solid, or a ``callable(inner: InnerPath)`` -- the
                         polygon-native content contract (carries ``.path``/``.profile``)
        stackable:       ``STACKABLE_TYPE_*`` interlocking-ring style (default none)
        magnet:          ``namespace(type=, size=)`` placed on the mid-point of EVERY
                         outline edge (generalises the regular-polygon magnet placement
                         to any path); ``None``/``MAGNET_SLOT_TYPE_NONE`` for no magnets
        hollow_radius:   ``namespace(top=, bottom=, radius=)`` cavity roundovers
        make_finger_x/y: force/suppress the edge finger dips (default auto)
        extra_floors:    list of ``namespace(path=, floor_height=, top_height=)`` raised floors
    """

    path: list[list[float]]
    children: "PyOpenSCAD | Callable | None" = None
    stackable: int = STACKABLE_TYPE_NONE
    stackable_thickness: float | None = None
    stackable_fit_offset: float = 0.1
    hollow_radius: types.SimpleNamespace | None = None
    make_finger_x: bool | None = None
    make_finger_y: bool | None = None
    finger_hole_size: float | None = None
    magnet: types.SimpleNamespace | None = None
    extra_floors: list[types.SimpleNamespace] | None = None
    mesh_res: int = 10


class PathBox(BoxBaseType):
    """A no-lid box whose OUTLINE is a polygon, on the new box system.

    The rectangular ``BoxSpec`` still supplies the height, wall/floor thickness,
    colour and positioning; the polygon and its outline-specific features come from
    a :class:`PathBoxOptions` in ``BoxSpec.type_options``. ``BoxSpec.size`` is
    given as ``[width, length, height]`` but the x/y extent is re-derived from the
    outline's bounding box in :meth:`__init__`, so ``self.width``/``self.length``
    (and hence positioning) always match the real polygon.

    Like :class:`NoLidBox`, a PathBox is a **solid spacer by default**; pass
    ``BoxSpec(hollow=True)`` (or a hollowing ``children``) to open the interior.
    There is no lid (:meth:`make_lid` raises). The heavy polygon geometry -- the
    outline extrusion, the inset-outline cavity, the interlocking stackable rings
    and the finger dips that walk each edge -- is delegated to the underlying
    :class:`PathBoxWithNoLid`; ``PathBox`` is the thin new-system wrapper over it,
    matching the facade pattern used by :class:`~hinge_box.HingeBox` et al.

    Usage::

        from box_base import BoxSpec
        from no_lid import PathBox, PathBoxOptions

        # explicit outline
        PathBox(BoxSpec(size=[60, 40, 20], label="wedge", hollow=True,
                        type_options=PathBoxOptions(path=[[0, 0], [60, 0], [30, 40]]))
                ).make_box().show()

        # regular hexagon spacer
        PathBox.regular_polygon(BoxSpec(size=[100, 100, 24], label="hex"),
                                sides=6, hollow=True).make_box().show()

    Compartment auto-layout works too: pass ``BoxSpec.contents`` (e.g. from
    :func:`compartments.layout_compartments`) and the wells are bin-packed in the
    outline's bounding box, clipped to the polygon cavity, and any cell that falls
    outside the outline is dropped -- the box supplies its inset outline to the layout
    automatically via ``InnerSize.region``::

        contents = layout_compartments([Group([Compartment(shape="circle", d=20,
                                                            depth=12, count=8)])])
        PathBox.regular_polygon(BoxSpec(size=[120, 120, 20], label="hex", contents=contents),
                                sides=6).make_box().show()
    """

    options_class = PathBoxOptions
    # PathBoxWithNoLid opens its own interior (the rounded, flared cavity) when told to.

    def __init__(self, spec: BoxSpec) -> None:
        # Lock the declared x/y extent to the outline's real bounding box so the base
        # class's size-derived machinery (positioning, inner_width/length) lines up
        # with the polygon rather than whatever nominal size the caller passed.
        opts = spec.type_options
        if isinstance(opts, PathBoxOptions):
            pts = np.asarray(opts.path, dtype=float)
            w = float(pts[:, 0].max() - pts[:, 0].min())
            l = float(pts[:, 1].max() - pts[:, 1].min())
            spec = replace(spec, size=[w, l, spec.size[2]])
        super().__init__(spec)   # validates type_options against options_class
        self._opts = self.options

        # Measurement instance: PathBoxWithNoLid.__init__ resolves the inset outlines in
        # numpy (no solids built), so we can read the INSIDE outline and its bounding box
        # cheaply, and reuse the same class for the cavity mask (hollow_cut) later.
        self._pbox = self._new_pathbox()

    def _new_pathbox(self, *, children=None, hollow: bool = False) -> "PathBoxWithNoLid":
        """A :class:`PathBoxWithNoLid` for this spec (the shell + cavity workhorse)."""
        opts = self._opts
        return PathBoxWithNoLid(
            path=opts.path,
            height=self.height,
            children=children,
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            stackable_thickness=opts.stackable_thickness,
            stackable_fit_offset=opts.stackable_fit_offset,
            hollow_radius=opts.hollow_radius,
            make_finger_x=opts.make_finger_x,
            make_finger_y=opts.make_finger_y,
            material_colour=self.material_colour,
            finger_hole_size=opts.finger_hole_size,
            hollow=hollow,
            stackable=opts.stackable,
            extra_floors=opts.extra_floors,
            mesh_res=opts.mesh_res,
        )

    @classmethod
    def regular_polygon(cls, spec: BoxSpec, sides: int, **opt_kwargs) -> "PathBox":
        """Build a PathBox from a regular *sides*-gon whose circumdiameter is
        ``spec.size[0]`` (the replacement for :func:`MakePolygonBoxWithNoLid`)."""
        if sides < 3:
            raise ValueError(f"sides must be >= 3, got {sides}")
        path = regular_ngon_path(sides, spec.size[0] / 2)
        return cls(replace(spec, type_options=PathBoxOptions(path=path, **opt_kwargs)))

    def _compute_interior(self) -> Interior:
        """The interior frame is the bounding box of the INSET OUTLINE -- the rectangle a
        compartment layout packs into -- carrying the outline itself as the ``region`` so
        the layout can drop cells that fall outside the polygon. The wells are trimmed to
        the real outline by :meth:`interior_mask`."""
        pts = np.asarray([[float(p[0]), float(p[1])] for p in self._pbox.inner_path], dtype=float)
        ox, oy = float(pts[:, 0].min()), float(pts[:, 1].min())
        return Interior(
            origin=(ox, oy, self.floor_thickness),
            size=(
                float(pts[:, 0].max() - ox),
                float(pts[:, 1].max() - oy),
                # No lid to subtract -- the interior runs from the floor to the open top.
                self.height - self.floor_thickness,
            ),
            # The inside outline in the layout's LOCAL frame (bbox corner at the origin).
            region=[[float(px - ox), float(py - oy)] for px, py in pts],
        )

    def _hollow_when_empty(self) -> bool:
        return False

    def interior_mask(self) -> "Bosl2Solid":
        """The clip volume for compartment contents: a STRAIGHT prism of the inset
        outline, floor to top.

        Deliberately NOT the box's decorative cavity (``PathBoxWithNoLid.hollow_cut``,
        which rounds the corners and flares the top rim) -- clipping wells against that
        would round/flare the well edges. Compartments should clip to the true vertical
        inner wall, so this is a plain ``rounding=0`` extrusion of the inset outline.
        (The open-tray finish for a ``hollow=True`` PathBox is still the rounded
        hollow_cut; it is built inside the shell, independently of this mask.)"""
        # PolygonPrism -> OffsetSweep already returns a Bosl2Solid, so no native wrap.
        return PolygonPrism(self._pbox.inner_path, h=self.inner_height).translate(
            [0, 0, self.floor_thickness]
        )

    def _edge_magnets(self) -> "Callable":
        """Compose the caller's ``children`` with a magnet slot on every outline edge.

        Generalises :func:`MakePolygonBoxWithNoLid`'s regular-polygon magnet loop to
        an arbitrary path: it walks the outline inset by a quarter wall and drops a
        :class:`~components.MagnetSlot` at each edge mid-point, oriented to the edge.
        """
        opts = self._opts
        magnet = opts.magnet
        user = opts.children

        def inner_children(inner):
            pieces = []
            if magnet is not None and magnet.type != MAGNET_SLOT_TYPE_NONE:
                edge_path = Path2D(opts.path).offset(radius=-self.wall_thickness / 4)
                n = len(edge_path)
                for i in range(n):
                    p1 = edge_path[i]
                    p2 = edge_path[(i + 1) % n]
                    mid = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
                    angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0])) - 90
                    slot = (
                        MagnetSlot(size=magnet.size, magnet_type=magnet.type, anchor=LEFT + BOTTOM, spin=180)
                        .rotate([0, 90, 0])
                        .rotate([0, 0, angle])
                        .translate([float(mid[0]), float(mid[1]), 0])
                    )
                    pieces.append(slot)
            if user is not None:
                c = user(inner) if callable(user) else user
                if c is not None:
                    pieces.append(c)
            if not pieces:
                return None
            result = pieces[0]
            for p in pieces[1:]:
                result = result | p
            return result

        return inner_children

    def _build_box_body(self, contents):
        """The polygon shell, with its own interior already opened (hence the returned
        ``Body(..., hollowed=True)``).

        Two content channels compose: :attr:`PathBoxOptions.children` (the polygon-native
        ``InnerPath`` callable -- hex dividers, stackable rings, edge magnets) is built
        into the shell here, and ``BoxSpec.contents`` (the ``InnerObject`` compartment
        model) is bin-packed, carved and clipped to the polygon cavity by the shared
        pipeline afterwards."""
        # When compartments carve their own wells, leave the interior SOLID
        # (dividers/floors survive); otherwise honour the hollow policy.
        shell = self._new_pathbox(
            children=self._edge_magnets(),
            hollow=self.should_hollow(contents),
        ).build()
        # NATIVE-BOUNDARY (bosl2 gap): PathBoxWithNoLid.build() returns a NATIVE solid when
        # its finger-hole cuts drop to native ops, so wrap it to continue in bosl2 -- but
        # only if it isn't a Bosl2Solid already (double-wrapping produces an object whose
        # .shape is another wrapper, which breaks anything reading the native handle).
        # FIX IN BOSL2: build()/carve_finger_holes should always return a Bosl2Solid.
        if isinstance(shell, pybosl2.shapes3d.Bosl2Solid):
            return Body(
                shell,
                hollowed=True,
            )
        return Body(
            pybosl2.shapes3d.Bosl2Solid(shell),
            hollowed=True,
        )
