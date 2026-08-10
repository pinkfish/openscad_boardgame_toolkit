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

# LibFile: slipover_path_box.py
#    Slipover box pieces for the slipover boxes with polygon outline.
#
# FileSummary: Slipover box pieces for the slipover boxes with polygon outline.
# FileGroup: Boxes

from __future__ import annotations
import copy
import types
from dataclasses import dataclass, replace

import numpy as np

from base_bgtk import (
    MAKE_MMU,
    CatchType,
    Color,
    PolygonPrism,
    default_floor_thickness,
    default_lid_thickness,
    default_material_colour,
    default_wall_thickness,
    m_piece_wiggle_room,
    native_colour,
    regular_ngon_path,
)
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401
from components import FingerHoleWall
from lids_base import default_lid_catch_type
from cap_box_polygon import PolygonBoxLidCatch, _segment_angle
from pybosl2 import Path2D
from pybosl2 import shapes2d
from box_base import Body, BoxSpec, BoxTypeOptions, LidPlate, LiddedBox


def _finger_hole_wall_segment_cutout(
    path: list[list[float]], height: float, radius: float, depth: float, finger_catch: CatchType
) -> PyOpenSCAD | None:
    """Makes a single finger-hole segment for use in the slipover box wall.

    Usage::

        _finger_hole_wall_segment_cutout([[0, 0], [50, 50]], radius=5, height=7, depth=6, finger_catch=CatchType.ALL)

    Args:
        path:    the path to generate for (exactly 2 points / one line segment)
        height:  the height of the finger hole
        radius:  the radius of the rounding on the finger hole
        depth:   the thickness of the walls
        finger_catch: the type of catch to use and where to put them
    """
    assert len(path) == 2, f"Path2D must be exactly 2 elements long path_length={len(path)}"
    seg = Path2D(path, closed=False)
    split_length = seg.perimeter()
    normal = seg.normals()
    vec_m = abs(path[0][0] - path[1][0]) / abs(path[0][1] - path[1][1]) if path[0][1] != path[1][1] else float("inf")

    qualifies = (
        finger_catch == CatchType.ALL
        or (finger_catch == CatchType.LONG and vec_m > 1000000)
        or (finger_catch == CatchType.SHORT and vec_m < 0.01)
    )
    if not (qualifies and split_length > radius * 3):
        return None

    pts = seg.cut_points([split_length / 2])
    angle = _segment_angle(normal)
    return (
        FingerHoleWall(radius=radius, height=height, depth_of_hole=depth)
        .rotate([0, 0, angle])
        .rotate([0, 180, 90])
        .translate([pts[0].point[0], pts[0].point[1], height - 0.01])
    )


def _make_path_box_with_slipover_lid(
    path: list[list[float]],
    height: float,
    children: "list | None" = None,
    wall_thickness: float | None = None,
    foot: float = 0,
    size_spacing: float | None = None,
    wall_height: float | None = None,
    floor_thickness: float | None = None,
    lid_thickness: float | None = None,
    material_colour: Color | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    lid_catch: CatchType | None = None,
) -> "Bosl2Solid":
    """Makes the inside of a polygon slipover box.

    This will take a second lid that slides over the outside of the box.
    *children* is a list of solids (or callables(inner_width, inner_length,
    inner_height)) carved into the box interior.

    Usage::

        _make_path_box_with_slipover_lid(path=[[0,0], [0,100], [50,100], [50,0]], height=10)

    Args:
        path:           the path for the bottom of the box (>= 3 points)
        height:         outside height of the box
        children:       list of solids/callables to carve inside the box
        wall_thickness: wall thickness (default default_wall_thickness)
        foot:           how big the foot around the bottom should be (default 0)
        size_spacing:   wiggle room (default m_piece_wiggle_room)
        wall_height:    explicit wall height (default height - lid_thickness - size_spacing)
        floor_thickness: floor thickness (default default_floor_thickness)
        lid_thickness:  lid thickness (default default_lid_thickness)
        material_colour: colour (default default_material_colour)
        positive_only_children: list of child indices that are positive-only
        positive_negative_children: list of child indices also rendered positive under MAKE_MMU
        lid_catch:      catch style (default default_lid_catch_type)
    """
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if floor_thickness is None:
        floor_thickness = default_floor_thickness
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
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

    inner_path = Path2D(path).offset(radius=-wall_thickness - size_spacing)
    calc_inner_path = Path2D(inner_path, closed=True).round_corners(radius=wall_thickness / 2)
    calc_path = Path2D(path, closed=True).round_corners(radius=wall_thickness)

    x_arr = [p[0] for p in inner_path]
    y_arr = [p[1] for p in inner_path]
    calc_width = max(x_arr) - min(x_arr)
    calc_length = max(y_arr) - min(y_arr)

    body = PolygonPrism(calc_inner_path, h=height - lid_thickness - size_spacing)
    if foot > 0:
        body = body | PolygonPrism(calc_path, h=foot)
    body = body.color(material_colour)

    catches = None
    n = len(calc_inner_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_inner_path[i], calc_inner_path[i + 1]],
            wall_thickness=wall_thickness,
            delta=size_spacing,
            offset=0,
            lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_inner_path[n - 1], calc_inner_path[0]],
        wall_thickness=wall_thickness,
        delta=size_spacing,
        offset=0,
        lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        body = body - catches.translate([0, 0, foot])

    inner_height = height - lid_thickness - floor_thickness
    kids = list(children) if children else []
    for i, c in enumerate(kids):
        if i not in positive_only_children:
            piece: Any = c(calc_width, calc_length, inner_height) if callable(c) else c
            body = body - piece.translate([wall_thickness * 2, wall_thickness * 2, floor_thickness])

    result = body
    if len(positive_only_children) > 0 or (len(positive_negative_children) > 0 and MAKE_MMU == 1):
        extra_indices = list(positive_only_children) + (list(positive_negative_children) if MAKE_MMU == 1 else [])
        extra = None
        for i in extra_indices:
            piece = (kids[i](calc_width, calc_length, inner_height) if callable(kids[i]) else kids[i]).translate(
                [wall_thickness * 2, wall_thickness * 2, floor_thickness]
            )
            extra = piece if extra is None else extra | piece
        if extra is not None:
            result = result | extra

    return result


def _slipover_path_lid_parts(
    path: list[list[float]],
    height: float,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    foot: float = 0,
    finger_catch: CatchType | None = None,
    lid_rounding: float | None = None,
    material_colour: Color | None = None,
    offset_sweep_options: types.SimpleNamespace | None = None,
    lid_catch: CatchType | None = None,
) -> "Bosl2Solid":
    """The pieces of a polygon slipover sleeve: ``(top_plate, shell, plate_z, rounded_path)``.

    Split into pieces (rather than returning a finished lid) so the ONE lid pipeline in
    :class:`~box_base.BoxBaseType` can decorate the top plate -- see :class:`SlipoverPathBox`.

    Usage::

        _slipover_path_lid_parts(path=[[0,0], [0,100], [50,100], [50,0]], height=10)

    Args:
        path:    the path of the box outline (>= 3 points)
        height:  height of the lid (outside height)
        lid_thickness: thickness of the lid (default default_lid_thickness)
        wall_thickness: thickness of the walls (default default_wall_thickness)
        size_spacing: wiggle room (default m_piece_wiggle_room)
        foot:    size of the foot on the box
        finger_catch: where to put the catches (default CatchType.SHORT)
        lid_rounding: rounding on the lid (default wall_thickness)
        material_colour: colour (default default_material_colour)
        offset_sweep_options: unused (kept for call-site compatibility with the old
                 offset_sweep()-based lid top; the SDF construction has no such knobs)
        lid_catch: catch style (default default_lid_catch_type)
    """
    if lid_thickness is None:
        lid_thickness = default_lid_thickness
    if wall_thickness is None:
        wall_thickness = default_wall_thickness
    if size_spacing is None:
        size_spacing = m_piece_wiggle_room
    if finger_catch is None:
        finger_catch = CatchType.SHORT
    if material_colour is None:
        material_colour = default_material_colour
    if offset_sweep_options is None:
        offset_sweep_options = types.SimpleNamespace(offset="round", check_valid=True, quality=1, steps=16)
    if lid_catch is None:
        lid_catch = default_lid_catch_type

    assert len(path) >= 3, f"Path2D must be at least 3 elements long path_length={len(path)}"
    assert height > 0, f"Height must be >0 height={height}"

    foot_offset = foot + size_spacing if foot > 0 else 0
    calc_lid_rounding = lid_rounding
    if calc_lid_rounding is None:
        calc_lid_rounding = wall_thickness

    inner_path = Path2D(path).offset(radius=-wall_thickness + size_spacing)
    calc_inner_path = Path2D(inner_path, closed=True).round_corners(radius=wall_thickness / 2)
    calc_path = Path2D(path, closed=True).round_corners(radius=calc_lid_rounding)

    # The original construction intersected the plain extrusion with an os_smooth-topped
    # offset_sweep (a continuous-curvature eased rim); PolygonPrism() approximates that
    # with a plain circular roundover of the same depth (joint = lid_thickness / 2) -- at
    # these rim sizes the silhouettes differ by well under half a millimetre.
    # (offset_sweep_options is therefore unused now; kept in the signature so existing
    # call sites don't break.)
    top = PolygonPrism(calc_path, h=lid_thickness, rounding_top=lid_thickness / 2).color(native_colour(material_colour))

    finger_height = min(20, (height - foot_offset - lid_thickness) / 2)

    wall_outer = PolygonPrism(calc_path, h=height - foot_offset - lid_thickness / 2)
    wall_inner = PolygonPrism(calc_inner_path, h=height + 1).translate([0, 0, -0.5])
    wall = (wall_outer - wall_inner).color(material_colour)

    catches = None
    n = len(calc_inner_path)
    for i in range(n - 1):
        c = PolygonBoxLidCatch(
            path=[calc_inner_path[i], calc_inner_path[i + 1]],
            wall_thickness=wall_thickness,
            delta=0,
            offset=0,
            lid_catch=lid_catch,
        )
        if c is not None:
            catches = c if catches is None else catches | c
    c = PolygonBoxLidCatch(
        path=[calc_inner_path[n - 1], calc_inner_path[0]],
        wall_thickness=wall_thickness,
        delta=0,
        offset=0,
        lid_catch=lid_catch,
    )
    if c is not None:
        catches = c if catches is None else catches | c
    if catches is not None:
        wall = wall | catches.color(material_colour)

    for i in range(n - 1):
        seg = _finger_hole_wall_segment_cutout(
            path=[calc_inner_path[i], calc_inner_path[i + 1]],
            depth=wall_thickness * 5,
            height=finger_height,
            radius=max(finger_height, 7),
            finger_catch=finger_catch,
        )
        if seg is not None:
            wall = wall - seg.color(material_colour)
    seg = _finger_hole_wall_segment_cutout(
        path=[calc_inner_path[n - 1], calc_inner_path[0]],
        depth=wall_thickness * 5,
        height=finger_height,
        radius=max(finger_height, 7),
        finger_catch=finger_catch,
    )
    if seg is not None:
        wall = wall - seg.color(material_colour)

    return top, wall, height - foot_offset - lid_thickness, calc_path


@dataclass
class SlipoverPathBoxOptions(BoxTypeOptions):
    """Options for :class:`SlipoverPathBox` -- a slipover box whose outline is a polygon.

    Give an explicit ``path`` (closed ``[[x, y], ...]`` outline) or use
    :meth:`SlipoverPathBox.regular_polygon`. The lid is a sleeve that slides over the
    OUTSIDE of the box."""

    path: list[list[float]]
    children: "list | None" = None
    foot: float = 0
    lid_catch: "CatchType | None" = None


class SlipoverPathBox(LiddedBox):
    """A slipover box whose OUTLINE is a polygon, on the new box system -- the polygon
    counterpart of :class:`~slipover_box.SlipoverBox`. The lid is a sleeve that slides
    over the outside of the box; box and lid are separate prints. Facade over
    :func:`_make_path_box_with_slipover_lid` / :func:`_slipover_path_lid_parts`.

    The polygon goes in ``BoxSpec.type_options`` as a :class:`SlipoverPathBoxOptions`;
    ``BoxSpec.size`` is ``[width, length, height]`` but the x/y extent is re-derived from
    the outline. The lid gets an automatic label + shape pattern when ``BoxSpec.lid``
    is set.

    Usage::

        from box_base import BoxSpec
        from slipover_path_box import SlipoverPathBox, SlipoverPathBoxOptions

        box = SlipoverPathBox(BoxSpec(size=[80, 60, 15], label="slip", lid="Coins",
                                      type_options=SlipoverPathBoxOptions(
                                          path=[[0,0],[80,0],[80,60],[0,60]])))
        box.make_box().show()
        box.make_lid().show()

        # regular hexagon
        SlipoverPathBox.regular_polygon(BoxSpec(size=[90, 90, 15], label="hex", lid="Wood"),
                                        sides=6).make_box().show()
    """

    options_class = SlipoverPathBoxOptions

    def __init__(self, spec: BoxSpec) -> None:
        opts = spec.type_options
        if isinstance(opts, SlipoverPathBoxOptions):
            pts = np.asarray(opts.path, dtype=float)
            w = float(pts[:, 0].max() - pts[:, 0].min())
            l = float(pts[:, 1].max() - pts[:, 1].min())
            spec = replace(spec, size=[w, l, spec.size[2]])
        super().__init__(spec)   # validates type_options against options_class
        self._opts = self.options

    @classmethod
    def regular_polygon(cls, spec: BoxSpec, sides: int, **opt_kwargs) -> "SlipoverPathBox":
        """Build from a regular *sides*-gon whose circumdiameter is ``spec.size[0]``."""
        if sides < 3:
            raise ValueError(f"sides must be >= 3, got {sides}")
        path = regular_ngon_path(sides, spec.size[0] / 2)
        return cls(replace(spec, type_options=SlipoverPathBoxOptions(path=path, **opt_kwargs)))

    def _children(self, contents):
        kids = [io.value for io in contents] or None
        if self._opts.children:
            kids = list(self._opts.children) + (kids or [])
        return kids

    def _build_box_body(self, contents):
        o = self._opts
        return Body(
            _make_path_box_with_slipover_lid(
                path=o.path,
                height=self.height,
                children=self._children(contents),
                wall_thickness=self.wall_thickness,
                foot=o.foot,
                size_spacing=self.size_spacing,
                floor_thickness=self.floor_thickness,
                lid_thickness=self.lid_thickness,
                material_colour=self.material_colour,
                lid_catch=o.lid_catch,
            ),
            hollowed=True, carved=True,
        )

    def _lid_plate(self, lid) -> LidPlate:
        """The polygon sleeve: the outline-shaped top plate (decorated) closing the sleeve
        wall (the shell). ``origin`` is the rounded outline's bounding-box corner -- a
        polygon path is centred on the origin, so without it the label would be laid out
        half a box away from the lid."""
        o = self._opts
        top, shell, plate_z, calc_path = _slipover_path_lid_parts(
            path=o.path,
            height=self.height,
            wall_thickness=self.wall_thickness,
            foot=o.foot,
            size_spacing=self.size_spacing,
            lid_thickness=self.lid_thickness,
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
            offset=[0, 0, plate_z],
            shell=shell,
            path=[[float(x), float(y)] for x, y in pts],
        )

    def _lid_adjustment(self, stack):
        """Flip the sleeve over for printing. Rotate FIRST, then lift: the other order
        left the whole lid at negative z (below the print bed)."""
        o = self._opts
        foot_offset = o.foot + self.size_spacing if o.foot > 0 else 0
        return stack.rotate([180, 0, 0]).translate([0, self.length, self.height - foot_offset])
