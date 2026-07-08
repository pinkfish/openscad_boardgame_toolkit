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
from bosl2 import shapes3d
from bosl2 import shapes2d
from bosl2 import paths
from bosl2 import rounding
from components import FingerHoleWall, MagnetSlot

from typing import Callable


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports.
_bosl2 = osuse("BOSL2/std.scad")

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

    body = shapes3d.cuboid(
        [width, length, height],
        anchor=BOTTOM + FRONT + LEFT,
        rounding=wall_thickness,
        edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
    )
    body = body.face_profile(TOP, r=wall_thickness / 2)
    body = body.face_profile(BOTTOM, r=wall_thickness / 2)
    body = body.corner_profile("ALL", r=wall_thickness / 2)
    body = body.color(material_colour)

    if hollow:
        hole = (
            shapes3d.cuboid(
                [width - wall_thickness * 2, length - wall_thickness * 2, height],
                rounding=wall_thickness / 4,
                anchor=BOTTOM + LEFT + FRONT,
            )
            .color(material_colour)
            .translate([wall_thickness, wall_thickness, floor_thickness])
        )
        body = body - hole

    fh = min(calc_finger_hole_size, height - default_floor_thickness + 1)
    if calc_make_finger_y:
        for x in (calc_finger_hole_wall_width / 2 - 0.01, width - calc_finger_hole_wall_width / 2 + 0.01):
            cut = (
                FingerHoleWall(
                    radius=calc_finger_hole_size, height=fh, spin=90, depth_of_hole=calc_finger_hole_wall_width + 0.03,
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
                    radius=calc_finger_hole_size, height=fh, depth_of_hole=wall_thickness + 0.03,
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

    return body


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

    split_length = paths.path_length(path)
    normal = paths.path_normals(path)
    if normal[0][0] == 0:
        angle = 90 if normal[0][1] > 0 else -90
    else:
        angle = math.degrees(math.atan(normal[0][1] / normal[0][0]))

    use_finger = make_finger_y if (-90 < angle < 90) else make_finger_x
    if not (split_length > finger_hole_size * 2.5 and use_finger):
        return None

    pts = paths.path_cut_points(path=path, cutdist=[split_length / 2])
    return (
        FingerHoleWall(
            radius=finger_hole_size, height=finger_hole_height, spin=90, depth_of_hole=wall_thickness + 0.03,
            rounding_edge=wall_thickness / 2,
        )
        .rotate([0, 0, angle])
        .translate([pts[0][0][0], pts[0][0][1], height - finger_hole_height + 0.01])
    )


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
) -> PyOpenSCAD:
    """Makes a box with no lid using a polygon layout.

    Useful for spacers and other things in games. You might need to reduce
    the $fn-equivalent point counts ("steps" in offset_sweep_options) if you
    get geometry errors generating corners.

    *children*, if given, may be a plain solid or a
    callable(inner_path, inner_width, inner_length, inner_height) -- this
    replaces the original SCAD module's $inner_path/$inner_width/
    $inner_length/$inner_height special variables.

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
        offset_sweep_options: namespace(offset=, check_valid=, quality=, steps=)
        hollow:         if the box should be hollow (default False)
        stackable_lid_thickness/stackable: STACKABLE_TYPE_* (default STACKABLE_TYPE_NONE)
        magnet:         namespace(type=, size=, height=) (default MAGNET_SLOT_TYPE_NONE)
        extra_floors:   list of namespace(path=, floor_height=, top_height=) (default [])
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if stackable_thickness is None:
        stackable_thickness = default_stackable_thickness
    if hollow_radius is None:
        hollow_radius = types.SimpleNamespace(top=wall_thickness / 4, bottom=wall_thickness / 4, radius=wall_thickness / 2)
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if magnet is None:
        magnet = types.SimpleNamespace(type=MAGNET_SLOT_TYPE_NONE, size=[0, 0, 0], height=0)
    if extra_floors is None:
        extra_floors = []

    assert len(path) >= 3, f"Path must be at least 3 elements long path_length={len(path)}"
    assert floor_thickness > 0, f"Need floor thickness > 0, floor_thickness={floor_thickness}"
    assert wall_thickness > 0, f"Need wall thickness > 0, wall_thickness={wall_thickness}"
    assert height > 0, f"Need height > 0, height={height}"

    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    calc_length = max(y_arr) - min(y_arr)
    calc_width = max(x_arr) - min(x_arr)

    calc_finger_hole_size = finger_hole_size
    if calc_finger_hole_size is None:
        calc_finger_hole_size = min(20, min(calc_length, calc_width) / 4, height - floor_thickness + 1)
    calc_finger_hole_height = min(calc_finger_hole_size, height - default_floor_thickness * 2 + 1)
    calc_make_finger_x = (calc_width > calc_length) if (make_finger_x is None and make_finger_y is None) else False
    calc_make_finger_y = (calc_length > calc_width) if (make_finger_y is None and make_finger_x is None) else False

    sorted_floors = QuicksortExtraFloors(extra_floors)
    region_path = _bosl2.make_region(path)
    region_extra_floors = [_bosl2.make_region(f.path) for f in sorted_floors]
    region_outside = _bosl2.union([region_path] + region_extra_floors)

    calc_path = rounding.round_corners(region_outside[0], radius=wall_thickness)
    main_path = _bosl2.difference([path] + [f.path for f in sorted_floors])

    inner_path = _bosl2.offset(main_path, r=-wall_thickness)
    inner_path_stackable = _bosl2.offset(main_path, r=-wall_thickness / 2)
    inner_path_stackable_bottom_outside = _bosl2.offset(main_path, r=-wall_thickness / 2 + stackable_fit_offset)
    inner_path_stackable_bottom_inside = _bosl2.offset(main_path, r=-wall_thickness - stackable_fit_offset)
    inner_path_stackable_bottom_inside_inside = _bosl2.offset(main_path, r=-wall_thickness / 2 - stackable_fit_offset)

    def sweep_kwargs(**extra) -> dict:
        return dict(
            offset=offset_sweep_options.offset,
            check_valid=offset_sweep_options.check_valid,
            quality=offset_sweep_options.quality,
            steps=offset_sweep_options.steps,
            **extra,
        )

    def StackableBoxInternal(bottom: bool = False) -> PyOpenSCAD | None:
        if stackable == STACKABLE_TYPE_INSIDE:
            outer = _bosl2.offset_sweep(
                rounding.round_corners(
                    inner_path_stackable_bottom_outside if bottom else inner_path_stackable, radius=stackable_thickness / 2
                ),
                **sweep_kwargs(
                    height=stackable_thickness + (stackable_fit_offset if bottom else 0), top=_bosl2.os_circle(wall_thickness / 4)
                ),
            ).color(material_colour)
            inner = (
                _bosl2.offset_sweep(
                    rounding.round_corners(inner_path_stackable_bottom_inside if bottom else inner_path, radius=stackable_thickness / 4),
                    **sweep_kwargs(
                        height=stackable_thickness + 0.02 + (stackable_fit_offset if bottom else 0),
                        top=_bosl2.os_circle(-wall_thickness / 4),
                    ),
                )
                .color(material_colour)
                .translate([0, 0, -0.01])
            )
            return outer - inner
        elif stackable == STACKABLE_TYPE_OUTSIDE:
            outer = _bosl2.offset_sweep(
                calc_path,
                **sweep_kwargs(
                    height=stackable_thickness + (stackable_fit_offset if bottom else 0), top=_bosl2.os_circle(wall_thickness / 4)
                ),
            ).color(material_colour)
            inner = (
                _bosl2.offset_sweep(
                    rounding.round_corners(
                        inner_path_stackable_bottom_inside_inside if bottom else inner_path_stackable, radius=stackable_thickness / 4
                    ),
                    **sweep_kwargs(
                        height=stackable_thickness + 0.02 + (stackable_fit_offset if bottom else 0),
                        top=_bosl2.os_circle(-wall_thickness / 4),
                    ),
                )
                .color(material_colour)
                .translate([0, 0, -0.01])
            )
            return outer - inner
        return None

    main_solid = _bosl2.offset_sweep(
        calc_path,
        **sweep_kwargs(
            height=(height - stackable_thickness) if stackable else height,
            bottom=_bosl2.os_circle(wall_thickness / 4 if stackable else wall_thickness / 2),
            top=_bosl2.os_circle(wall_thickness / 8 if stackable else wall_thickness / 4),
        ),
    )
    if stackable:
        main_solid = main_solid | StackableBoxInternal(bottom=False).translate([0, 0, height - stackable_thickness])

    for f in sorted_floors:
        if f.floor_height > 0:
            main_solid = main_solid - polygon(f.path).linear_extrude(height=f.floor_height)
        if f.top_height > 0:
            main_solid = main_solid - polygon(f.path).linear_extrude(height=f.top_height).translate(
                [0, 0, height - f.top_height]
            )

    extra_solid = None
    for f in sorted_floors:
        piece = _bosl2.offset_sweep(
            rounding.round_corners(f.path, radius=wall_thickness),
            **sweep_kwargs(
                height=(height - f.floor_height - stackable_thickness) if stackable else (height - f.floor_height),
                bottom=_bosl2.os_circle(wall_thickness / 4 if stackable else wall_thickness / 2),
                top=_bosl2.os_circle(wall_thickness / 8 if stackable else wall_thickness / 4),
            ),
        ).translate([0, 0, f.floor_height])
        extra_solid = piece if extra_solid is None else extra_solid | piece

    body = (main_solid | extra_solid) if extra_solid is not None else main_solid
    body = body.color(material_colour)

    if hollow:
        hollow_cut = (
            _bosl2.offset_sweep(
                rounding.round_corners(inner_path, radius=hollow_radius.radius),
                **sweep_kwargs(
                    height=height - floor_thickness,
                    bottom=_bosl2.os_circle(hollow_radius.bottom),
                    top=(None if stackable else _bosl2.os_circle(-hollow_radius.top)),
                ),
            )
            .color(material_colour)
            .translate([0, 0, floor_thickness])
        )
        body = body - hollow_cut

        for f in sorted_floors:
            if f.floor_height > 0:
                joined_outer = rounding.round_corners(
                    _bosl2.offset(_bosl2.union([f.path, path]), r=-wall_thickness), radius=wall_thickness
                )
                inner_union = [_bosl2.offset(f.path, delta=wall_thickness), inner_path] + [
                    _bosl2.offset(other.path, delta=wall_thickness) for other in sorted_floors if other.floor_height > f.floor_height
                ]
                region = _bosl2.intersection(joined_outer, _bosl2.union(inner_union))
                cut = _bosl2.offset_sweep(
                    region,
                    **sweep_kwargs(
                        height=height - floor_thickness - f.floor_height,
                        bottom=_bosl2.os_circle(hollow_radius.bottom),
                        top=(None if stackable else _bosl2.os_circle(-hollow_radius.top)),
                    ),
                ).translate([0, 0, f.floor_height + floor_thickness])
                body = body - cut

    if stackable:
        body = body - StackableBoxInternal(bottom=True).translate([0, 0, -stackable_fit_offset])

    calc_middle_path = _bosl2.offset(path, r=-wall_thickness / 2)
    n = len(calc_middle_path)
    for i in range(n - 1):
        seg = FingerHoleWallSegment(
            path=[calc_middle_path[i], calc_middle_path[i + 1]],
            wall_thickness=wall_thickness,
            finger_hole_size=calc_finger_hole_size,
            finger_hole_height=calc_finger_hole_height,
            make_finger_y=calc_make_finger_y,
            make_finger_x=calc_make_finger_x,
            height=height,
        )
        if seg is not None:
            body = body - seg
    seg = FingerHoleWallSegment(
        path=[calc_middle_path[n - 1], calc_middle_path[0]],
        wall_thickness=wall_thickness,
        finger_hole_size=calc_finger_hole_size,
        finger_hole_height=calc_finger_hole_height,
        height=height,
        make_finger_y=calc_make_finger_y,
        make_finger_x=calc_make_finger_x,
    )
    if seg is not None:
        body = body - seg

    if children is not None:
        c = children(inner_path, calc_width, calc_length, height - floor_thickness) if callable(children) else children
        if c is not None:
            body = body - c

    return body


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
) -> PyOpenSCAD:
    """Makes a polygon box with no lid.

    *children*, if given, may be a plain solid or a
    callable(inner_path, inner_width, inner_length, inner_height) (same as
    MakePathBoxWithNoLid).

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
        offset_sweep_options: namespace(offset=, check_valid=, quality=, steps=)
        hollow_radius:  namespace(top=, bottom=, radius=) (default 2, 10, 2)
        magnet:         namespace(type=, size=) (default MAGNET_SLOT_TYPE_NONE)
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

    def inner_children(
        inner_path: list[list[float]], inner_width: float, inner_length: float, inner_height: float
    ) -> PyOpenSCAD | None:
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
            c = children(inner_path, inner_width, inner_length, inner_height) if callable(children) else children
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
    )
