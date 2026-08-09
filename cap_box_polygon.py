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

# LibFile: cap_box_polygon.py
#    Cap box pieces for the cap boxes with polygon outline.
#
# FileSummary: Cap box pieces for the cap boxes with polygon outline.
# FileGroup: Boxes

from __future__ import annotations
import copy
import math
from dataclasses import dataclass, replace

import numpy as np
import types

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import numpy as np
import pybosl2.shapes3d
from pybosl2 import Path2D
from pybosl2 import shapes2d
from box_base import Body, BoxSpec, BoxTypeOptions, LidPlate, LiddedBox
from lids_base import default_lid_catch_type
from cap_box import (
    cap_box_default_cap_height,
    cap_box_default_finger_hold_height,
    cap_box_default_lid_finger_hold_rounding,
    cap_box_default_lid_wall_thickness,
)


def _segment_angle(normal: "np.ndarray | list[list[float]]") -> float:
    if normal[0][0] == 0:
        return 90 if normal[0][1] > 0 else -90
    return math.degrees(math.atan(normal[0][1] / normal[0][0]))


def _finger_hole_segment_cutout(
    path: list[list[float]], radius: float, height: float, wall_thickness: float
) -> "Bosl2Solid | None":
    """Makes a single segment for use in the cap-box wall.

    Makes the rounded finger holes on the side of the cap box at the
    correct direction and length; returns None if the segment is too short.

    Usage::

        _finger_hole_segment_cutout([[0, 0], [50, 50]], radius=5, height=7, wall_thickness=2)

    Args:
        path:   the path to generate for (exactly 2 points / one line segment)
        radius: the radius of the rounding on the finger hole
        height: the height of the finger hole
        wall_thickness: the thickness of the walls
    """
    assert len(path) == 2, f"Path2D must be exactly 2 elements long path_length={len(path)}"
    seg = Path2D(path, closed=False)
    split_length = seg.perimeter()
    normal = seg.normals()
    calc_len = split_length / 5
    calc_radius = wall_thickness + 0.1 if wall_thickness >= radius else radius

    if not (split_length > calc_radius * 2):
        return None

    angle = _segment_angle(normal)

    if calc_len + radius > calc_len * 4 - radius:
        pts = seg.cut_points([split_length / 2])
        return (
            pybosl2.shapes3d.xcyl(length=wall_thickness * 2, radius=radius)
            .rotate([0, 0, angle])
            .translate([float(pts[0].point[0]), float(pts[0].point[1]), 0.0])
        )

    pts = seg.cut_points(
        [calc_len + wall_thickness, calc_len + calc_radius, calc_len * 4 - calc_radius, calc_len * 4 - wall_thickness],
    )
    c1 = (
        pybosl2.shapes3d.xcyl(length=wall_thickness * 2, radius=radius)
        .rotate([0, 0, angle])
        .translate([float(pts[1].point[0]), float(pts[1].point[1]), height - calc_radius])
    )
    c2 = (
        pybosl2.shapes3d.xcyl(length=wall_thickness * 2, radius=radius)
        .rotate([0, 0, angle])
        .translate([float(pts[2].point[0]), float(pts[2].point[1]), height - calc_radius])
    )
    c3 = (
        pybosl2.shapes3d.cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2])
        .rotate([0, 0, angle])
        .translate([float(pts[0].point[0]), float(pts[0].point[1]), calc_radius - height])
    )
    c4 = (
        pybosl2.shapes3d.cuboid([wall_thickness * 2, wall_thickness * 2, wall_thickness * 2])
        .rotate([0, 0, angle])
        .translate([float(pts[3].point[0]), float(pts[3].point[1]), calc_radius - height])
    )
    # pybosl2 Bosl2Solid.hull() (3-D) instead of the native openscad hull().
    return c1.hull(c2, c3, c4)


def PolygonBoxLidCatch(
    path: list[list[float]], wall_thickness: float, offset: float, delta: float, lid_catch: CatchType | None = None
) -> PyOpenSCAD | None:
    """The catch under the lid for the polygon box.

    A small wedge that follows the specified line segment, only generated
    when the segment is long enough and matches *lid_catch*.

    Usage::

        PolygonBoxLidCatch(path=[[0, 0], [50, 50]], offset=5, wall_thickness=2, delta=0)
        PolygonBoxLidCatch(path=[[0, 0], [50, 50]], offset=5, wall_thickness=2, delta=2)

    Args:
        path:   the path to generate for (exactly 2 points / one line segment)
        wall_thickness: the thickness of the walls
        offset: the offset of the rounding on the finger hole
        delta:  how much to offset the segment by
        lid_catch: the type of catch to use
    """
    assert len(path) == 2, f"Path2D must be exactly 2 elements. path_length={len(path)}"
    assert delta is not None, "delta None in PolygonBoxLidCatch."
    seg = Path2D(path, closed=False)
    split_length = seg.perimeter()
    calc_len = split_length / 5

    if not (
        calc_len * 4 - offset - wall_thickness + delta - (calc_len + wall_thickness + offset - delta) > 5
        and lid_catch != CatchType.NONE
    ):
        return None

    vec_m = abs(path[0][0] - path[1][0]) / abs(path[0][1] - path[1][1]) if path[0][1] != path[1][1] else float("inf")
    qualifies = (
        lid_catch == CatchType.ALL
        or (lid_catch == CatchType.LONG and vec_m > 1000000)
        or (lid_catch == CatchType.SHORT and vec_m < 0.01)
    )
    if not qualifies:
        return None

    pts = seg.cut_points([calc_len + wall_thickness + offset - delta, calc_len * 4 - wall_thickness - offset + delta])
    p1 = [pts[0].point[0], pts[0].point[1]]
    p2 = [pts[1].point[0], pts[1].point[1]]
    # The old _bosl2.path_sweep of the triangle profile along the 2-point segment is a
    # triangular prism: extrude the profile (centered along Z), stand it up (profile y -> Z,
    # extrusion axis -> the segment direction, profile x -> the LEFT of travel, matching
    # path_sweep's 2-D frame), and move it onto the segment midpoint.
    seg_angle = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
    return (
        shapes2d.polygon(
            [[delta, delta], [-wall_thickness * 3 / 4 - delta, delta], [delta, wall_thickness * 3 / 4 + delta]]
        )
        .linear_extrude(height=math.dist(p1, p2), center=True)
        .rotate([90, 0, 0])
        .rotate([0, 0, seg_angle + 90])
        .translate([float((p1[0] + p2[0]) / 2), float((p1[1] + p2[1]) / 2), 0.0])
    )


def _make_path_box_with_cap_lid(
    path: list[list[float]],
    height: float,
    children: "list | None" = None,
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_wall_thickness: float | None = None,
    finger_hold_height: float = 5,
    floor_thickness: float | None = None,
    material_colour: Color | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    lid_catch: CatchType | None = None,
) -> PyOpenSCAD:
    """Makes a polygon-outline box with a cap lid.

    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height), resolved by ResolveChild) carved into the box interior. Despite what this
    docstring used to claim, no inner_path is passed -- this box resolves children exactly like
    the rectangular ones.

    Usage::

        _make_path_box_with_cap_lid(path=[[0,0], [0,100], [100,100]], height=20)

    Args:
        path:            the polygon outline path of the box (>= 3 points)
        height:          outside height of the box
        children:        list of solids/callables to carve inside the box
        cap_height:      cap height (default auto)
        lid_thickness:   lid thickness (default default_lid_thickness)
        wall_thickness:  wall thickness (default default_wall_thickness)
        size_spacing:    wiggle room (default m_piece_wiggle_room)
        lid_wall_thickness: thickness of the walls in the lid (default wall_thickness/2)
        finger_hold_height: finger hold height (default 5)
        floor_thickness: floor thickness (default default_floor_thickness)
        material_colour: colour (default default_material_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        lid_catch:       catch style (default default_lid_catch_type)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if material_colour is None:
        material_colour = default_material_colour
    if positive_only_children is None:
        positive_only_children = []
    if positive_negative_children is None:
        positive_negative_children = []
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path2D must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    calc_lid_wall_thickness = (
        lid_wall_thickness if lid_wall_thickness is not None else cap_box_default_lid_wall_thickness(wall_thickness)
    )
    calc_floor_thickness = floor_thickness if floor_thickness is not None else wall_thickness
    calc_cap_height = cap_height if cap_height is not None else cap_box_default_cap_height(height)
    calc_finger_hold_height = (
        finger_hold_height if finger_hold_height is not None else cap_box_default_finger_hold_height(height)
    )
    calc_finger_hole_rounding = cap_box_default_lid_finger_hold_rounding(calc_cap_height)
    calc_path = np.asarray(Path2D(path, closed=True).round_corners(radius=wall_thickness))
    # Plain lists for the native polygon() calls below: raw ndarrays across the native
    # boundary raise (and poison the interpreter) -- see the numpy interop convention.
    calc_path_native = calc_path.tolist()
    # The old _bosl2.offset(path, r=-wall) inner path only ever fed this bounding-box
    # bookkeeping -- the wall-inset bbox is the bbox shrunk by a wall on each side.
    x_arr = [p[0] for p in path]
    y_arr = [p[1] for p in path]
    calc_width = max(x_arr) - min(x_arr) - 2 * wall_thickness
    calc_length = max(y_arr) - min(y_arr) - 2 * wall_thickness

    body = (
        shapes2d.polygon(calc_path_native)
        .linear_extrude(height=height - lid_thickness - size_spacing)
        .color(material_colour)
    )

    lid_outer = (
        shapes2d.polygon(calc_path_native).offset(radius=size_spacing).linear_extrude(height=height).color(material_colour)
    )
    lid_inner = (
        shapes2d.polygon(calc_path_native)
        .offset(radius=-calc_lid_wall_thickness - size_spacing)
        .linear_extrude(height=height + 1)
        .color(material_colour)
        .translate([0, 0, -0.5])
    )
    body = body - (lid_outer - lid_inner).translate([0, 0, height - calc_cap_height])

    finger_outer = (
        shapes2d.polygon(calc_path_native).offset(radius=size_spacing).linear_extrude(height=height).color(material_colour)
    )
    finger_inner = (
        shapes2d.polygon(calc_path_native)
        .offset(radius=-calc_lid_wall_thickness - size_spacing)
        .linear_extrude(height=height)
        .color(material_colour)
    )
    finger_cut = finger_outer - finger_inner
    n = len(calc_path)
    for i in range(n - 1):
        seg = _finger_hole_segment_cutout(
            path=[calc_path[i], calc_path[i + 1]],
            height=calc_finger_hold_height,
            radius=calc_finger_hole_rounding,
            wall_thickness=wall_thickness,
        )
        if seg is not None:
            finger_cut = finger_cut - seg
    seg = _finger_hole_segment_cutout(
        path=[calc_path[n - 1], calc_path[0]],
        height=calc_finger_hold_height,
        radius=calc_finger_hole_rounding,
        wall_thickness=wall_thickness,
    )
    if seg is not None:
        finger_cut = finger_cut - seg
    body = body - finger_cut.translate([0, 0, height - calc_cap_height - calc_finger_hold_height])

    catches = None
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_path[i], calc_path[i + 1]],
            offset=calc_finger_hole_rounding,
            wall_thickness=wall_thickness,
            delta=size_spacing,
            lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_path[n - 1], calc_path[0]],
        offset=calc_finger_hole_rounding,
        wall_thickness=wall_thickness,
        delta=size_spacing,
        lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        body = body - catches.translate([0, 0, height - calc_cap_height])

    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []

    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece: Any = c(calc_path, calc_width, calc_length, inner_height) if callable(c) else c
            body = body - piece.translate([wall_thickness, wall_thickness, calc_floor_thickness])

    result = body

    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            # Path2D-box children take (path, width, length, height) -- ResolveChild() is the
            # 3-argument box form and this call passed 5 arguments (a latent TypeError in the
            # never-exercised positive-children branch); resolve inline like the branch above.
            resolved: Any = kids[i](calc_path, calc_width, calc_length, inner_height) if callable(kids[i]) else kids[i]
            piece = resolved.translate([wall_thickness, wall_thickness, floor_thickness])
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result


def _cap_path_lid_parts(
    path: list[list[float]],
    height: float,
    cap_height: float | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_wall_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_inner_rounding: float | None = None,
    material_colour: Color | None = None,
    offset_sweep_options: types.SimpleNamespace | None = None,
    lid_catch: CatchType | None = None,
) -> tuple:
    """The pieces of a polygon cap lid: ``(top_plate, shell, cap_height, rounded_path)``.

    Split into pieces (rather than returning a finished lid) so the ONE lid pipeline in
    :class:`~box_base.BoxBaseType` can decorate the top plate -- see :class:`CapPathBox`.

    Usage::

        _cap_path_lid_parts(path=[[0,0], [0,100], [100,100]], height=30)

    Args:
        path:    the polygon outline path of the box (>= 3 points)
        height:  outside height of the box
        cap_height: cap height (default auto)
        lid_thickness: lid thickness (default default_lid_thickness)
        wall_thickness: wall thickness (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        lid_wall_thickness: thickness of the walls in the lid (default wall_thickness/2)
        lid_rounding/lid_inner_rounding: rounding values
        material_colour: colour (default default_material_colour)
        offset_sweep_options: namespace(offset=, check_valid=, quality=, steps=)
        lid_catch: catch style (default default_lid_catch_type). Note: the
                   original SCAD module never threaded this through to its
                   catch geometry (a bug); it's wired up correctly here.
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if material_colour is None:
        material_colour = default_material_colour
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path2D must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    calc_lid_wall_thickness = lid_wall_thickness if lid_wall_thickness is not None else wall_thickness / 2
    calc_cap_height = cap_height if cap_height is not None else cap_box_default_cap_height(height)
    calc_path = np.asarray(Path2D(path, closed=True).round_corners(radius=wall_thickness, fn=16))
    calc_path_native = calc_path.tolist()  # plain lists for the native polygon() calls
    calc_finger_hole_rounding = cap_box_default_lid_finger_hold_rounding(calc_cap_height)

    # The old offset_sweep with an os_smooth(joint=wall/2) top is a straight extrusion of
    # the rounded outline with an eased top rim -- polygon_prism's circular roundover of the
    # same joint size is a near-identical profile.
    top = PolygonPrism(calc_path, h=lid_thickness, rounding_top=min(wall_thickness / 2, lid_thickness * 0.49)).color(
        material_colour
    )

    base_outer = (
        shapes2d.polygon(calc_path_native)
        .linear_extrude(height=calc_cap_height - lid_thickness / 2)
        .color(material_colour)
    )
    base_inner = (
        shapes2d.polygon(calc_path_native)
        .offset(radius=-wall_thickness + size_spacing)
        .linear_extrude(height=calc_cap_height - lid_thickness / 2 + 1)
        .color(material_colour)
        .translate([0, 0, -0.5])
    )
    base = base_outer - base_inner

    catches = None
    n = len(calc_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_path[i], calc_path[i + 1]],
            offset=calc_finger_hole_rounding,
            wall_thickness=wall_thickness,
            delta=0,
            lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_path[n - 1], calc_path[0]],
        offset=calc_finger_hole_rounding,
        wall_thickness=wall_thickness,
        delta=0,
        lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c

    shell = base if catches is None else (base | catches.color(material_colour))
    return top, shell, calc_cap_height, calc_path


@dataclass
class CapPathBoxOptions(BoxTypeOptions):
    """Options for :class:`CapPathBox` -- a cap box whose outline is a polygon.

    Give an explicit ``path`` (closed ``[[x, y], ...]`` outline) or use
    :meth:`CapPathBox.regular_polygon`. ``children`` is the list of solids/callables
    carved into the interior (resolved like the rectangular boxes)."""

    path: list[list[float]]
    children: "list | None" = None
    cap_height: float | None = None
    lid_wall_thickness: float | None = None
    finger_hold_height: float = 5
    lid_catch: "CatchType | None" = None


class CapPathBox(LiddedBox):
    """A cap box whose OUTLINE is a polygon, on the new box system -- the polygon
    counterpart of :class:`~cap_box.CapBox`. A cap slides over the top rim; box and lid
    are separate prints. Facade over :func:`_make_path_box_with_cap_lid` / :func:`_cap_path_lid_parts`.

    The polygon and cap parameters go in ``BoxSpec.type_options`` as a
    :class:`CapPathBoxOptions`; ``BoxSpec.size`` is ``[width, length, height]`` but the
    x/y extent is re-derived from the outline. The lid gets an automatic label + shape
    pattern when ``BoxSpec.lid_label`` is set.

    Usage::

        from box_base import BoxSpec
        from cap_box_polygon import CapPathBox, CapPathBoxOptions

        box = CapPathBox(BoxSpec(size=[80, 80, 25], label="hexcap", lid_label="Ore",
                                 type_options=CapPathBoxOptions(path=[[0,0],[80,0],[40,80]])))
        box.make_box().show()
        box.make_lid().show()

        # regular hexagon
        CapPathBox.regular_polygon(BoxSpec(size=[90, 90, 25], label="hex", lid_label="Gold"),
                                   sides=6).make_box().show()
    """

    options_class = CapPathBoxOptions

    def __init__(self, spec: BoxSpec) -> None:
        opts = spec.type_options
        if isinstance(opts, CapPathBoxOptions):
            pts = np.asarray(opts.path, dtype=float)
            w = float(pts[:, 0].max() - pts[:, 0].min())
            l = float(pts[:, 1].max() - pts[:, 1].min())
            spec = replace(spec, size=[w, l, spec.size[2]])
        super().__init__(spec)   # validates type_options against options_class
        self._opts = self.options

    @classmethod
    def regular_polygon(cls, spec: BoxSpec, sides: int, **opt_kwargs) -> "CapPathBox":
        """Build from a regular *sides*-gon whose circumdiameter is ``spec.size[0]``."""
        if sides < 3:
            raise ValueError(f"sides must be >= 3, got {sides}")
        path = regular_ngon_path(sides, spec.size[0] / 2)
        return cls(replace(spec, type_options=CapPathBoxOptions(path=path, **opt_kwargs)))

    def _children(self, contents):
        kids = [io.value for io in contents] or None
        # type_options.children compose in front of BoxSpec.contents.
        if self._opts.children:
            kids = list(self._opts.children) + (kids or [])
        return kids

    def _build_box_body(self, contents):
        o = self._opts
        return Body(
            _make_path_box_with_cap_lid(
                path=o.path,
                height=self.height,
                children=self._children(contents),
                cap_height=o.cap_height,
                lid_thickness=self.lid_thickness,
                wall_thickness=self.wall_thickness,
                size_spacing=self.size_spacing,
                lid_wall_thickness=o.lid_wall_thickness,
                finger_hold_height=o.finger_hold_height,
                floor_thickness=self.floor_thickness,
                material_colour=self.material_colour,
                lid_catch=o.lid_catch,
            ),
            hollowed=True, carved=True,
        )

    def _lid_plate(self, lid) -> LidPlate:
        """The polygon cap: the outline-shaped top plate (decorated) sitting on the cap
        wall + catches (the shell). The plate's footprint is the ROUNDED OUTLINE, and its
        origin is that outline's bounding-box corner -- a polygon path is centred on the
        origin, so without it the label would be laid out half a box away from the lid."""
        o = self._opts
        top, shell, cap_h, calc_path = _cap_path_lid_parts(
            path=o.path,
            height=self.height,
            cap_height=o.cap_height,
            lid_thickness=self.lid_thickness,
            wall_thickness=self.wall_thickness,
            size_spacing=self.size_spacing,
            lid_wall_thickness=o.lid_wall_thickness,
            material_colour=self.material_colour,
            lid_catch=o.lid_catch,
        )
        pts = np.asarray(calc_path, dtype=float)
        ox, oy = float(pts[:, 0].min()), float(pts[:, 1].min())
        return LidPlate(
            plate=top,
            size=[float(pts[:, 0].max() - ox), float(pts[:, 1].max() - oy)],
            thickness=self.lid_thickness,
            origin=[ox, oy],
            offset=[0, 0, cap_h - self.lid_thickness],
            shell=shell,
            path=[[float(x), float(y)] for x, y in pts],
        )

    def _cap_height(self) -> float:
        o = self._opts
        return float(o.cap_height) if o.cap_height else cap_box_default_cap_height(self.height)

    def _lid_adjustment(self, stack):
        """Flip the cap over for printing. Rotate FIRST, then lift: the other order left
        the whole lid at negative z (below the print bed).

        Only z is corrected. This used to add ``self.length`` in y as well, which assumes
        the part sits at y in [0, length] before the flip -- true for a corner-anchored
        box, but a polygon box is built CENTRED on the origin, so the flip already leaves
        y where it belongs and the correction pushed the lid a whole length off its box.
        """
        return stack.rotate([180, 0, 0]).translate([0, 0, self._cap_height()])
