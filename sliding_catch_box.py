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

# LibFile: sliding_catch_box.py
#    Sliding catch box and lid generators.
#
# FileSummary: Sliding catch box pieces for the sliding catch boxes.
# FileGroup: Boxes

from __future__ import annotations
from dataclasses import dataclass

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.shapes3d
from box_base import BoxBaseType, BoxSpec


@dataclass
class SlidingCatchBoxOptions:
    """Sliding-catch-box options; pass via ``BoxSpec(type_options=MakeSlidingCatchBoxOptions(...))``."""

    top_thickness: float = 2      # material above the catch groove (default 2)
    fill_middle: bool = True      # fill the middle of the lid (default True)


def MakeSlidingCatchBoxOptions(**kwargs) -> SlidingCatchBoxOptions:
    return SlidingCatchBoxOptions(**kwargs)


class SlidingCatchBox(BoxBaseType):
    """A box whose lid slides into a groove on the top AND catches at the front, on the
    new box system. Sturdier than a plain sliding lid (and a bit thicker). Box and lid
    are separate prints; ``contents`` are carved into the box.

    Catch/lid parameters come from
    ``BoxSpec(type_options=MakeSlidingCatchBoxOptions(top_thickness=2))``. The lid runs
    through the shared overlay pipeline, so a label / shape pattern / fingernail lands on
    its flat (outer) face when ``BoxSpec.lid_label`` / ``lid_shape`` is set.

    Usage::

        from box_base import BoxSpec
        from sliding_catch_box import SlidingCatchBox

        box = SlidingCatchBox(BoxSpec(size=[100, 50, 20], label="catch", lid_label="Frog"))
        box.make_box().show()
        box.make_lid().show()
    """

    def _opts(self) -> SlidingCatchBoxOptions:
        o = self._spec.type_options
        return o if isinstance(o, SlidingCatchBoxOptions) else SlidingCatchBoxOptions()

    def _sliding_len(self) -> float:
        return (self.length - self.wall_thickness) / 6

    def inside_mask(self):
        # The interior is open all the way up to the lid groove (unlike the default mask,
        # which stops a lid-thickness below the top), so the lid can slide in over it.
        return pybosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.height], anchor=BOTTOM + FRONT + LEFT
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    def _build_box_body(self):
        w, l, h = self.width, self.length, self.height
        wt, lt = self.wall_thickness, self.lid_thickness
        ss = self.size_spacing
        tt = self._opts().top_thickness
        sl = self._sliding_len()

        body = pybosl2.shapes3d.cuboid(
            [w, l, h], anchor=BOTTOM + FRONT + LEFT, rounding=wt,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, sl + 1, lt + ss], anchor=FRONT + LEFT + BOTTOM,
            rounding=lt / 2, edges=[BACK + BOTTOM],
        ).translate([-0.5, wt + sl, h - lt - tt])

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, sl + ss * 2, lt + tt + ss], anchor=FRONT + LEFT + BOTTOM,
            rounding=lt / 2, edges=[BACK + BOTTOM],
        ).translate([-0.5, wt + sl * 2 - ss, h - lt - tt])

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, sl + ss * 2, tt - ss], anchor=FRONT + LEFT + BOTTOM,
            rounding=-tt / 2, edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK],
        ).translate([-0.5, wt + sl * 2 - ss, h - tt + ss])

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, sl + 1, lt + ss], rounding=lt, anchor=FRONT + LEFT + BOTTOM,
            edges=[BACK + TOP],
        ).translate([-0.5, wt + l - sl * 2 - ss * 2, h - lt - tt])

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, sl + ss * 2 + 1, lt + tt + ss], anchor=FRONT + LEFT + BOTTOM,
            rounding=lt / 2, edges=[BACK + BOTTOM],
        ).translate([-0.5, l - sl - ss * 2, h - lt - tt])

        body = body - pybosl2.shapes3d.cuboid(
            [w + 1, wt + sl + ss * 2, tt - ss], anchor=FRONT + LEFT + BOTTOM,
            rounding=-tt / 2, edges=[FRONT + BOTTOM, FRONT + TOP, TOP + BACK],
        ).translate([-0.5, wt + l - sl - wt - ss * 2, h - tt + ss])

        return body.color(self.material_colour)

    def _make_base_lid(self, lid_rounding=None):
        w, l = self.width, self.length
        wt, lt = self.wall_thickness, self.lid_thickness
        ss = self.size_spacing
        o = self._opts()
        tt = o.top_thickness
        sl = self._sliding_len()
        r = lid_rounding if lid_rounding is not None else tt / 2

        base = pybosl2.shapes3d.cuboid(
            [w, l - wt, lt - ss], anchor=BOTTOM + FRONT + LEFT
        )
        if o.fill_middle:
            fill = pybosl2.shapes3d.cuboid(
                [w - wt * 2 - ss * 2, l, tt + 0.1], anchor=FRONT + LEFT + BOTTOM,
                rounding=r, edges=TOP,
            ).translate([wt, 0, lt - 0.1])
            base = fill | base

        def _cut(size_y: float, tx: float, ty: float):
            cut_w = wt + ss + 1
            return pybosl2.shapes3d.cuboid(
                [cut_w, size_y, lt + 1], anchor=BOTTOM + FRONT + LEFT
            ).translate([tx, ty, -0.5])

        base = (
            base
            - _cut(wt + sl + 1, -1, -1)
            - _cut(wt + sl + 1, w - wt - ss, -1)
            - _cut(wt + sl * 2, -1, sl * 2)
            - _cut(wt + sl * 2, w - wt - ss, sl * 2)
            - _cut(wt + sl + 1, -1, sl * 5)
            - _cut(wt + sl + 1, w - wt - ss, sl * 5)
        )
        return base.color(self.material_colour)

    def create_lid(self, lid=None):
        """The sliding catch lid: the grooved / optionally middle-filled plate, decorated
        with this box's label / shape pattern / fingernail overlays on its flat outer face."""
        l = self._prepare_lid(lid)
        base = self._make_base_lid(l.lid_rounding)
        return self._apply_lid_overlays(base, l, [self.width, self.length])
