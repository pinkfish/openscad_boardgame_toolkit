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

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import numpy as np
import pybosl2.masking
import pybosl2.shapes3d
from pybosl2 import shapes2d
from pybosl2.paths import Path
from components import FingerHoleWall, MagnetSlot, MAGNET_SLOT_TYPE_NONE
from box_base import BoxBaseType, BoxSpec, FingerHole, FingerHoleLocation, FingerHoleType

from typing import Callable


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse(BOSL2_STD_PATH)

STACKABLE_TYPE_NONE = 0
STACKABLE_TYPE_INSIDE = 1
STACKABLE_TYPE_OUTSIDE = 2


def QuicksortExtraFloors(lst: list[types.SimpleNamespace]) -> list[types.SimpleNamespace]:
    """Sorts a list of extra-floor data objects by .floor_height."""
    if not lst:
        return []
    pivot = lst[len(lst) // 2]
    lesser = [i for i in lst if i.floor_height < pivot.floor_height]
    equal = [i for i in lst if i.floor_height == pivot.floor_height]
    greater = [i for i in lst if i.floor_height > pivot.floor_height]
    return QuicksortExtraFloors(lesser) + equal + QuicksortExtraFloors(greater)


def MakeBoxWithNoLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    make_finger_x: bool | None = None,
    make_finger_y: bool | None = None,
    material_colour: str = "grey",
    finger_hole_size: float | None = None,
    finger_hole_wall_width: float | None = None,
    hollow: bool = False,
    mesh_res: int = 10,
) -> PyOpenSCAD:
    """Makes a box with no lid, useful for spacers and other things in games.

    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        MakeBoxWithNoLid(size=[100, 50, 20])
        MakeBoxWithNoLid(size=[100, 50, 20], hollow=True)

    Args:
        size:            [width, length, height] outside size of the box
        children:        list of solids to carve inside the box
        wall_thickness:  thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        make_finger_x:   make a finger dip on the x axis (default width > length)
        make_finger_y:   make a finger dip on the y axis (default length > width)
        material_colour: material colour (default "grey")
        finger_hole_size: size of the finger dip (default auto)
        finger_hole_wall_width: width of the hole in the wall (default wall_thickness)
        hollow:          make the inside hollow (default False)
        mesh_res:        libfive meshing resolution for the SDF solids (default 10 -- a good
                         detail/speed balance at box scale)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness

    width, length, height = size
    assert width > 0 and length > 0 and height > 0, (
        f"Need width,length,height > 0 width={width} length={length} height={height}"
    )
    assert floor_thickness > 0, f"Need floor thickness > 0, floor_thickness={floor_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"

    calc_finger_hole_size = finger_hole_size
    if calc_finger_hole_size is None:
        calc_finger_hole_size = min(20, min(length, width) / 4, height - floor_thickness + 1)
    calc_finger_hole_wall_width = finger_hole_wall_width
    if calc_finger_hole_wall_width is None:
        calc_finger_hole_wall_width = wall_thickness
    calc_make_finger_x = (width > length) if (make_finger_x is None and make_finger_y is None) else False
    calc_make_finger_y = (length > width) if (make_finger_y is None and make_finger_x is None) else False

    body = pybosl2.shapes3d.cuboid(
        [width, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )
    # Top and bottom rims plus corners get their own roundover, exactly the original .scad
    # construction (face_profile(TOP/BOTTOM) + corner_profile("ALL"), all r=wall/2).
    body = body.face_profile([TOP], r=wall_thickness / 2)
    body = body.face_profile([BOTTOM], r=wall_thickness / 2)
    body = body.corner_profile("ALL", r=wall_thickness / 2)

    if hollow:
        hole = pybosl2.shapes3d.cuboid(
            [width - wall_thickness * 2, length - wall_thickness * 2, height],
            rounding=wall_thickness / 4,
            anchor=BOTTOM + LEFT + FRONT,
        ).translate([wall_thickness, wall_thickness, floor_thickness])
        body = body - hole

    body = body.color(material_colour)

    fh = min(calc_finger_hole_size, height - default_floor_thickness + 1)
    if calc_make_finger_y:
        for x in (calc_finger_hole_wall_width / 2 - 0.01, width - calc_finger_hole_wall_width / 2 + 0.01):
            cut = (
                FingerHoleWall(
                    radius=calc_finger_hole_size,
                    height=fh,
                    spin=90,
                    depth_of_hole=calc_finger_hole_wall_width + 0.03,
                    rounding_edge=wall_thickness / 2,
                )
                .color(material_colour)
                .translate([x, length / 2, height - calc_finger_hole_size + 0.01])
            )
            body = body - cut

    if calc_make_finger_x:
        for y in (wall_thickness / 2 - 0.01, length - wall_thickness / 2 + 0.01):
            cut = (
                FingerHoleWall(
                    radius=calc_finger_hole_size,
                    height=fh,
                    depth_of_hole=wall_thickness + 0.03,
                    rounding_edge=wall_thickness / 2,
                )
                .color(material_colour)
                .translate([width / 2, y, height - calc_finger_hole_size + 0.01])
            )
            body = body - cut

    inner_width = width - wall_thickness * 2
    inner_length = length - wall_thickness * 2
    inner_height = height - floor_thickness
    if children:
        kids_shape = None
        for c in children:
            piece = ResolveChild(c, inner_width, inner_length, inner_height)
            kids_shape = piece if kids_shape is None else kids_shape | piece
        if kids_shape is not None:
            body = body - kids_shape.translate([wall_thickness, wall_thickness, floor_thickness])

    return body.shape


class NoLidBox(BoxBaseType):
    """A box with no lid -- a spacer, or an open tray, on the new box system.

    Unlike a lidded box, a no-lid box is **solid by default** (a spacer). Pass
    ``BoxSpec(hollow=True)`` for the common open-tray form, or give ``contents`` to
    carve compartments. There is no lid, so :meth:`make_lid` is unavailable.

    Usage::

        from box_base import BoxSpec
        from no_lid import NoLidBox

        NoLidBox(BoxSpec(size=[100, 50, 20], label="spacer")).make_box()             # solid
        NoLidBox(BoxSpec(size=[100, 50, 20], label="tray", hollow=True)).make_box()  # open
    """

    @property
    def inner_height(self) -> float:
        # No lid to subtract -- the interior runs from the floor to the open top.
        return self.height - self.floor_thickness

    def _hollow_when_empty(self) -> bool:
        # A no-lid box with nothing in it is a solid spacer unless hollow=True.
        return False

    def _build_box_body(self) -> "Bosl2Solid":
        # A fully-rounded box (all edges + corners) -- the no-lid look. (The .scad
        # original layered face_profile/corner_profile roundovers; pybosl2's
        # corner_profile is currently broken, and a single rounding= is equivalent
        # at this scale and robust.)
        body = pybosl2.shapes3d.cuboid(
            [self.width, self.length, self.height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness / 2,
        )
        return body.color(self.material_colour)

    def make_lid(self, lid=None):
        raise NotImplementedError(f"{self.label}: a NoLidBox has no lid")


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
    assert len(path) == 2, f"Path must be exactly 2 elements long path_length={len(path)}"
    assert finger_hole_size > 0, f"Need finger hole size > 0, finger_hole_size={finger_hole_size}"
    assert finger_hole_height > 0, f"Need finger hole height > 0, finger_hole_height={finger_hole_height}"
    assert height > 0, f"Need height > 0, height={height}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"

    seg = Path(path, closed=False)
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
        .translate([pts[0][0][0], pts[0][0][1], height - finger_hole_height + 0.01])
    )


class PathBoxWithNoLid:
    """Builds a no-lid box from a polygon outline.

    This used to be one long function whose intermediate pieces (the rounded outer path, the
    five inset paths, the finger-hole sizing) were threaded through nested closures. They are
    instance attributes now, so each stage is a method that reads them rather than a closure
    capturing them, and a caller can build a box in stages or inspect the derived paths.
    :func:`MakePathBoxWithNoLid` is the thin functional wrapper over it.

    The 2-D work splits deliberately (see Path.offset): the outline insets are POINT
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
        material_colour: str = "grey",
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

        assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
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
        every box in examples/ -- make_region(path) is just [path] and the union/difference of
        a single region is that region, so this collapses to the path itself and stays pure
        Python. (See the module note on the remaining extra_floors osuse dependency.)
        """
        wall = self.wall_thickness
        self.sorted_floors = QuicksortExtraFloors(self.extra_floors)
        if self.sorted_floors:
            region_outside = _bosl2.union(
                [_bosl2.make_region(self.path)] + [_bosl2.make_region(f.path) for f in self.sorted_floors]
            )
            self.outside_path = region_outside[0]
            self.main_path = _bosl2.difference([self.path] + [f.path for f in self.sorted_floors])
        else:
            self.outside_path = self.path
            self.main_path = self.path

        self.calc_path = Path(self.outside_path).round_corners(radius=wall)
        fit = self.stackable_fit_offset
        self.inner_path = Path(self.main_path).offset(r=-wall)
        self.inner_path_stackable = Path(self.main_path).offset(r=-wall / 2)
        self.inner_path_stackable_bottom_outside = Path(self.main_path).offset(r=-wall / 2 + fit)
        self.inner_path_stackable_bottom_inside = Path(self.main_path).offset(r=-wall - fit)
        self.inner_path_stackable_bottom_inside_inside = Path(self.main_path).offset(r=-wall / 2 - fit)
        self.middle_path = Path(self.path).offset(r=-wall / 2)

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
            return polygon([[float(x), float(y)] for x, y in outer_path]).offset(r=-(wall + float(inset)))

        return InnerPath(
            width=self.width,
            length=self.length,
            height=self.height - self.floor_thickness,
            path=outer_path,
            profile=profile,
        )

    def stackable_ring(self, bottom: bool = False) -> "PyOpenSCAD | None":
        """The interlocking ring for a stackable box (was the StackableBoxInternal closure)."""
        wall, stack, fit = self.wall_thickness, self.stackable_thickness, self.stackable_fit_offset
        grow = fit if bottom else 0
        if self.stackable == STACKABLE_TYPE_INSIDE:
            outer_src = self.inner_path_stackable_bottom_outside if bottom else self.inner_path_stackable
            inner_src = self.inner_path_stackable_bottom_inside if bottom else self.inner_path
            outer = PolygonPrism(Path(outer_src).round_corners(radius=stack / 2), h=stack + grow, rounding_top=wall / 4)
        elif self.stackable == STACKABLE_TYPE_OUTSIDE:
            inner_src = self.inner_path_stackable_bottom_inside_inside if bottom else self.inner_path_stackable
            outer = PolygonPrism(self.calc_path, h=stack + grow, rounding_top=wall / 4)
        else:
            return None
        inner = PolygonPrism(
            Path(inner_src).round_corners(radius=stack / 4), h=stack + 0.02 + grow, rounding_top=-wall / 4
        ).translate([0, 0, -0.01])
        return outer - inner

    def outer_body(self) -> "PyOpenSCAD":
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
                Path(f.path).round_corners(radius=wall),
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

    def hollow_cut(self) -> "PyOpenSCAD":
        """The main cavity."""
        return PolygonPrism(
            Path(self.inner_path).round_corners(radius=self.hollow_radius.radius),
            h=self.height - self.floor_thickness,
            rounding_bottom=self.hollow_radius.bottom,
            rounding_top=0 if self.stackable else -self.hollow_radius.top,
        ).translate([0, 0, self.floor_thickness])

    def extra_floor_cut(self, f: types.SimpleNamespace) -> "PyOpenSCAD | None":
        """The cavity above one raised floor."""
        if f.floor_height <= 0:
            return None
        wall = self.wall_thickness
        joined_outer = Path(_bosl2.union([f.path, self.path])).offset(r=-wall).round_corners(radius=wall)
        inner_union = [Path(f.path).offset(delta=wall), self.inner_path] + [
            Path(other.path).offset(delta=wall) for other in self.sorted_floors if other.floor_height > f.floor_height
        ]
        region = _bosl2.intersection(joined_outer, _bosl2.union(inner_union))
        return PolygonPrism(
            region,
            h=self.height - self.floor_thickness - f.floor_height,
            rounding_bottom=self.hollow_radius.bottom,
            rounding_top=0 if self.stackable else -self.hollow_radius.top,
        ).translate([0, 0, f.floor_height + self.floor_thickness])

    def carve_children(self, body: "PyOpenSCAD") -> "PyOpenSCAD":
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


def MakePathBoxWithNoLid(
    path: list[list[float]],
    height: float,
    children: PyOpenSCAD | Callable | None = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    stackable_thickness: float | None = None,
    stackable_fit_offset: float = 0.1,
    hollow_radius: types.SimpleNamespace | None = None,
    make_finger_x: bool | None = None,
    make_finger_y: bool | None = None,
    material_colour: str = "grey",
    finger_hole_size: float | None = None,
    offset_sweep_options: types.SimpleNamespace | None = None,
    hollow: bool = False,
    stackable: int = STACKABLE_TYPE_NONE,
    magnet: types.SimpleNamespace | None = None,
    extra_floors: list[types.SimpleNamespace] | None = None,
    mesh_res: int = 10,
) -> PyOpenSCAD:
    """Makes a box with no lid using a polygon layout.

    Useful for spacers and other things in games. The solids are built with
    base_bgtk.OffsetSweep() (direct Manifold CSG -- native polygon extrusion
    with offset()-sliced rim roundovers/flares), so the old advice about
    reducing offset_sweep() "steps" on corner geometry errors no longer
    applies.

    *children*, if given, may be a plain solid or a callable(inner) taking a single
    :class:`~base_bgtk.InnerPath` -- the replacement for the original SCAD module's
    $inner_path/$inner_width/$inner_length/$inner_height special variables. It carries
    .width/.length/.height/.path, plus .profile(inset=0), a function pointer returning the
    inside as native 2-D geometry. The inset outline is only built if a child calls .profile();
    the old contract passed an inner_path point list that nothing ever read.

    Usage::

        MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20)
        MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20, hollow=True)
        MakePathBoxWithNoLid(path=[[0,0], [50,0], [50,50], [0,50]], height=20, stackable=True)

    Args:
        path:           the path to generate for (a closed polygon outline)
        height:         the height of the box
        children:       solid or callable (see above)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        stackable_thickness: thickness of the stackable part (default default_stackable_thickness)
        stackable_fit_offset: offset for stackable fit (default 0.1)
        hollow_radius:  namespace(top=, bottom=, radius=) (default wall_thickness/4, wall_thickness/4, wall_thickness/2)
        make_finger_x/make_finger_y: finger dip controls (default auto)
        material_colour: material colour (default "grey")
        finger_hole_size: size of the finger dip (default auto)
        offset_sweep_options: unused (kept for call-site compatibility with the old
                        offset_sweep()-based construction; the SDF sweep has no such knobs)
        hollow:         if the box should be hollow (default False)
        stackable_lid_thickness/stackable: STACKABLE_TYPE_* (default STACKABLE_TYPE_NONE)
        magnet:         namespace(type=, size=, height=) (default MAGNET_SLOT_TYPE_NONE)
        extra_floors:   list of namespace(path=, floor_height=, top_height=) (default [])
        mesh_res:       libfive meshing resolution for the SDF solids (default 10 -- a good
                        detail/speed balance at box scale; raise it if the rim roundovers on a
                        very small box look faceted)
    """
    return PathBoxWithNoLid(
        path=path,
        height=height,
        children=children,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        stackable_thickness=stackable_thickness,
        stackable_fit_offset=stackable_fit_offset,
        hollow_radius=hollow_radius,
        make_finger_x=make_finger_x,
        make_finger_y=make_finger_y,
        material_colour=material_colour,
        finger_hole_size=finger_hole_size,
        offset_sweep_options=offset_sweep_options,
        hollow=hollow,
        stackable=stackable,
        magnet=magnet,
        extra_floors=extra_floors,
        mesh_res=mesh_res,
    ).build()


def MakePolygonBoxWithNoLid(
    size: list[float],
    sides: int,
    children: PyOpenSCAD | Callable | None = None,
    wall_thickness: float | None = None,
    floor_thickness: float | None = None,
    stackable_thickness: float | None = None,
    make_finger_x: bool | None = None,
    make_finger_y: bool | None = None,
    material_colour: str = "grey",
    finger_hole_size: float | None = None,
    hollow: bool = False,
    stackable: int = STACKABLE_TYPE_NONE,
    offset_sweep_options: types.SimpleNamespace | None = None,
    hollow_radius: types.SimpleNamespace | None = None,
    magnet: types.SimpleNamespace | None = None,
    mesh_res: int = 10,
) -> PyOpenSCAD:
    """Makes a polygon box with no lid.

    *children*, if given, may be a plain solid or a callable(inner) taking an
    :class:`~base_bgtk.InnerPath` (same as MakePathBoxWithNoLid).

    Usage::

        MakePolygonBoxWithNoLid(size=[100, 100, 20], sides=6)

    Args:
        size:           [width, height] outside size of the box
        sides:          number of sides for the polygon
        children:       solid or callable (see above)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        floor_thickness: thickness of the floor (default default_floor_thickness)
        stackable_thickness: thickness of the stackable lid (default default_stackable_thickness)
        make_finger_x/make_finger_y: finger dip controls (default False)
        material_colour: material colour (default "grey")
        finger_hole_size: size of the finger dip (default auto)
        hollow:         make the inside hollow (default False)
        stackable:      STACKABLE_TYPE_* (default STACKABLE_TYPE_NONE)
        offset_sweep_options: unused (kept for call-site compatibility; see MakePathBoxWithNoLid)
        hollow_radius:  namespace(top=, bottom=, radius=) (default 2, 10, 2)
        magnet:         namespace(type=, size=) (default MAGNET_SLOT_TYPE_NONE)
        mesh_res:       libfive meshing resolution for the SDF solids (see MakePathBoxWithNoLid)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if stackable_thickness is None:
        stackable_thickness = default_stackable_thickness
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if hollow_radius is None:
        hollow_radius = types.SimpleNamespace(top=2, bottom=10, radius=2)
    if magnet is None:
        magnet = types.SimpleNamespace(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0])

    width, height = size
    assert width > 0 and height > 0, f"Need width, height > 0 width={width} height={height}"
    assert sides >= 3, f"sides must be >= 3, sides={sides}"

    calc_path = shapes2d._regular_ngon_path(sides, width / 2)

    def inner_children(inner: InnerPath) -> PyOpenSCAD | None:
        pieces = []
        if magnet.type != MAGNET_SLOT_TYPE_NONE:
            calc_path_magnet = shapes2d._regular_ngon_path(sides, (width - wall_thickness / 2) / 2)
            for i in range(sides):
                p1 = calc_path_magnet[i]
                p2 = calc_path_magnet[(i + 1) % sides]
                mid = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
                angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0])) - 90
                slot = (
                    MagnetSlot(size=magnet.size, magnet_type=magnet.type, anchor=LEFT + BOTTOM, spin=180)
                    .rotate([0, 90, 0])
                    .rotate([0, 0, angle])
                    .translate([mid[0], mid[1], 0])
                )
                pieces.append(slot)
        if children is not None:
            c = children(inner) if callable(children) else children
            if c is not None:
                pieces.append(c)
        if not pieces:
            return None
        result = pieces[0]
        for p in pieces[1:]:
            result = result | p
        return result

    return MakePathBoxWithNoLid(
        path=calc_path,
        height=height,
        offset_sweep_options=offset_sweep_options,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        stackable_thickness=stackable_thickness,
        make_finger_x=make_finger_x,
        make_finger_y=make_finger_y,
        material_colour=material_colour,
        finger_hole_size=finger_hole_size,
        hollow=hollow,
        stackable=stackable,
        hollow_radius=hollow_radius,
        children=inner_children,
        mesh_res=mesh_res,
    )
