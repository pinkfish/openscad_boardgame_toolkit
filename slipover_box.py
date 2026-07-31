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

# LibFile: slipover_box.py
#    Slipover box pieces for the slipover boxes.
#
# FileSummary: Slipover box pieces for the slipover boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.masking
import pybosl2.shapes3d
from components import CornerCatch
from lids_base import (
    default_lid_catch_type,
    internal_build_lid,
    MakeLidLabel,
    LidMeshBasic,
    build_lid_overlays,
    IsDenseShapeType,
    DenseShapeEdges,
)
from labels import MakeLabelOptions, LabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl
from box_base import BoxBaseType, BoxSpec


def _catch_bump(wall_thickness: float, radius: float, anchor_dir: list[int]) -> "PyOpenSCAD":
    box = wall_thickness * 6 / 4
    return (pybosl2.shapes3d.cuboid([box, box, box], anchor=anchor_dir) & pybosl2.shapes3d.sphere(r=radius)).shape


class SlipoverBox(BoxBaseType):
    """A box whose lid slips over the OUTSIDE, on the new box system.

    Unlike a cap box (cap over a stepped rim), the whole lid is a sleeve that slides
    down over the entire box. So the box body is INSET from the outer footprint by a
    wall + wiggle, leaving room for the sleeve. ``size`` is the OUTER (lid) footprint.

    Usage::

        from box_base import BoxSpec
        from slipover_box import SlipoverBox

        box = SlipoverBox(BoxSpec(size=[100, 50, 20], label="slip"))
        box.make_box().show()   # the inset body (open box)
        box.make_lid().show()   # the slipover sleeve
    """

    @property
    def _inset(self) -> float:
        # gap from the outer footprint to the box body wall (room for the sleeve).
        return self.wall_thickness + self.size_spacing

    @property
    def _wall_height(self) -> float:
        return self.height - self.lid_thickness - self.size_spacing

    @property
    def _content_off(self) -> float:
        # outer -> interior offset: inset + the body's own wall.
        return self._inset + self.wall_thickness

    @property
    def inner_width(self) -> float:
        return self.width - self._content_off * 2

    @property
    def inner_length(self) -> float:
        return self.length - self._content_off * 2

    @property
    def inner_height(self) -> float:
        return self._wall_height - self.floor_thickness

    def _effective_height(self) -> float:
        return self._wall_height

    def inside_mask(self):
        off = self._content_off
        return pybosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height], anchor=BOTTOM + FRONT + LEFT
        ).translate([off, off, self.floor_thickness])

    def _placed_content(self, io):
        off = self._content_off
        piece = ResolveChild(io.value, self.inner_width, self.inner_length, self.inner_height)
        return piece.translate([off, off, self.floor_thickness])

    def _build_box_body(self):
        bw = self.width - self._inset * 2
        bl = self.length - self._inset * 2
        body = pybosl2.shapes3d.cuboid(
            [bw, bl, self._wall_height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        )
        body = body.edge_mask(
            [TOP], children=pybosl2.masking.rounding_edge_mask(radius=self.wall_thickness / 4, length=max(bl, bw))
        )
        return body.translate([self._inset, self._inset, 0]).color(self.material_colour)

    def create_lid(self, lid=None):
        """The slipover sleeve: an outer shell hollowed to leave wall-thick walls and a
        lid-thick top, open at the bottom so it slides over the box body."""
        w, l, h = self.width, self.length, self.height
        wt, lt = self.wall_thickness, self.lid_thickness
        r = self.wall_thickness / 2
        shell = pybosl2.shapes3d.cuboid(
            [w, l, h], anchor=BOTTOM + FRONT + LEFT, rounding=r,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, TOP],
        )
        cavity = pybosl2.shapes3d.cuboid(
            [w - wt * 2, l - wt * 2, h - lt + 1], anchor=BOTTOM + FRONT + LEFT, rounding=r / 2,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        ).translate([wt, wt, -1])
        return (shell - cavity).color(self.material_colour)
