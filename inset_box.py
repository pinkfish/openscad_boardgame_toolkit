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

# LibFile: inset_box.py
#    Inset lid box and lid generators.
#
# FileSummary: Inset lid box pieces (finger tabs or rabbit clips).
# FileGroup: Boxes

from __future__ import annotations

from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
from base_bgtk import *
import pybosl2.shapes3d
from pybosl2._sdf import shapes3d as _sdf_shapes3d
from pybosl2._sdf import joiners as _sdf_joiners
from box_base import LiddedBox, BoxSpec, BoxTypeOptions, LidPlate
from dataclasses import dataclass
from lids_base import make_lid_tab, make_tabs


@dataclass
class InsetBoxOptions(BoxTypeOptions):
    """Inset-box options; pass via ``BoxSpec(type_options=InsetBoxOptions(...))``."""

    style: str = "tabbed"        # "tabbed" (finger-tab lid) or "rabbit" (rabbit-clip lid)
    inset: float = 1
    tab_height: float = 8
    tab_length: float = 10
    prism_width: float = 0.75
    make_tab_width: bool = False
    make_tab_length: bool = True
    # Rabbit-clip parameters (style == "rabbit"):
    rabbit_width: float = 7
    rabbit_length: float = 6
    rabbit_offset: float = 3
    rabbit_lock: bool = False
    rabbit_compression: float = 0.1
    rabbit_thickness: float = 0.8
    rabbit_snap: float = 0.25
    rabbit_depth: float = 1.5


class InsetBox(LiddedBox):
    """A box with an inset lid that sits down INSIDE the top rim, on the new box system.

    The lid is held by either finger tabs (``style="tabbed"``, the default) or rabbit
    clips (``style="rabbit"``), chosen via
    ``BoxSpec(type_options=InsetBoxOptions(style="rabbit"))``. Box and lid are separate
    prints; ``contents`` are carved into the box interior by the shared pipeline. The lid is
    built face-up (with its label / shape pattern overlays), then flipped for printing, so a
    ``BoxSpec.lid`` lands on the outer face.

    Usage::

        from box_base import BoxSpec
        from inset_box import InsetBox

        box = InsetBox(BoxSpec(size=[100, 50, 20], label="inset"))
        box.make_box().show()
        box.make_lid().show()
    """

    options_class = InsetBoxOptions

    def _effective_height(self) -> float:
        # The rabbit-clip body is a lid+wiggle shorter than the outer height; the tabbed
        # body is the full outer height (the lid drops into a recess cut in the top).
        if self.options.style == "rabbit":
            return self.height - self.lid_thickness - self.size_spacing
        return self.height

    # ------------------------------------------------------------------
    # Box body
    # ------------------------------------------------------------------

    def _lid_recess(self):
        """The inset recess carved from the top rim so the lid can drop in."""
        inset = self.options.inset
        return pybosl2.shapes3d.cuboid(
            [self.width - (self.wall_thickness - inset) * 2, self.length - (self.wall_thickness - inset) * 2,
             self.lid_thickness + 0.1],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness - inset, self.wall_thickness - inset, self.height - self.lid_thickness])

    def _build_box_body(self, contents):
        return self._build_body_rabbit() if self.options.style == "rabbit" else self._build_body_tabbed()

    def _build_body_tabbed(self):
        o = self.options
        w, l, h = self.width, self.length, self.height
        wt, lt = self.wall_thickness, self.lid_thickness
        body = pybosl2.shapes3d.cuboid(
            [w, l, h], anchor=BOTTOM + FRONT + LEFT, rounding=wt,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        ).color(self.material_colour)
        body = body - self._lid_recess()
        # pybosl2 0.7.4 added Bosl2Solid.minkowski, so this no longer drops to the native
        # builtin: staying on the wrapper keeps the result a Bosl2Solid, which is what lets
        # .color() take a Color (the native color() rejects one -- "Unknown color
        # representation").
        tab_cutter = (
            pybosl2.shapes3d.cuboid([0.45 * 2, 0.45 * 2, 0.45 * 2])
            .minkowski(
                make_lid_tab(length=o.tab_length, height=o.tab_height, lid_thickness=lt,
                             prism_width=o.prism_width, wall_thickness=wt)
            )
            .color(self.material_colour)
        )
        tabs_cut = make_tabs(
            size=[w, l], lid_thickness=lt, tab_length=o.tab_length,
            make_tab_length=o.make_tab_length, make_tab_width=o.make_tab_width, children=tab_cutter,
        ).color(native_colour(self.material_colour)).translate([0, 0, h - lt])
        return body - tabs_cut

    def _build_body_rabbit(self):
        o = self.options
        w, l, h = self.width, self.length, self.height
        wt, lt, ss = self.wall_thickness, self.lid_thickness, self.size_spacing
        body = pybosl2.shapes3d.cuboid(
            [w, l, h - lt - ss], anchor=BOTTOM + FRONT + LEFT, rounding=wt,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        ).color(self.material_colour)
        body = body - self._lid_recess()

        span = o.rabbit_length + o.rabbit_offset + ss * 2
        socket_box = _sdf_shapes3d.cuboid([span, wt + 0.01, lt + 0.01]).translate(
            [span / 2, wt / 2 - 0.01, -lt / 2]
        )
        socket_clip = _sdf_joiners.rabbit_clip(
            type="socket", length=o.rabbit_length, width=o.rabbit_width, snap=o.rabbit_snap,
            thickness=o.rabbit_thickness, depth=o.rabbit_depth + 0.01, compression=o.rabbit_compression,
            lock=o.rabbit_lock,
        ).translate([span / 2, wt / 2 - 0.01, -lt])
        # A factory, not a pre-meshed solid: PythonSCAD segfaults when one frep()-meshed handle
        # is transformed in more than one CSG branch, and make_tabs places the socket several times.
        socket = lambda: (socket_box | socket_clip).color(self.material_colour)  # noqa: E731
        tabs_cut = make_tabs(
            size=[w, l], lid_thickness=lt, tab_length=o.rabbit_length + o.rabbit_offset,
            make_tab_length=o.make_tab_length, make_tab_width=o.make_tab_width, children=socket,
        ).color(native_colour(self.material_colour)).translate([0, 0, h - lt])
        return body - tabs_cut

    # ------------------------------------------------------------------
    # Lid
    # ------------------------------------------------------------------

    def _lid_plate(self, lid) -> LidPlate:
        """The flat inset plate that drops inside the top rim (the decorated face), plus
        the finger tabs / rabbit clips that hold it in (the shell)."""
        o = self.options
        w, l, lt = self.width, self.length, self.lid_thickness
        wt, inset = self.wall_thickness, o.inset
        off = wt - inset + self.size_spacing
        iw = w - (wt - inset) * 2 - self.size_spacing * 2
        il = l - (wt - inset) * 2 - self.size_spacing * 2
        top = pybosl2.shapes3d.cuboid(
            [iw, il, lt], anchor=BOTTOM + FRONT + LEFT, rounding=wt / 2,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
        ).color(self.material_colour).translate([off, off, 0])

        if o.style == "rabbit":
            span = o.rabbit_length + o.rabbit_offset
            base = _sdf_shapes3d.cuboid([span, wt, lt]).translate([span / 2, wt / 2, -lt / 2])
            clip = _sdf_joiners.rabbit_clip(
                type="pin", length=o.rabbit_length, width=o.rabbit_width, snap=o.rabbit_snap,
                thickness=o.rabbit_thickness, depth=o.rabbit_depth, compression=o.rabbit_compression,
                lock=o.rabbit_lock,
            ).translate([span / 2, wt / 2, lt / 2])
            tab = lambda: (base | clip).mesh()  # noqa: E731  (factory: see frep-handle-reuse note above)
        else:
            tab = make_lid_tab(length=o.tab_length, height=o.tab_height, lid_thickness=lt,
                             prism_width=o.prism_width, wall_thickness=wt)
        tabs = make_tabs(
            size=[w, l], lid_thickness=lt, make_tab_width=o.make_tab_width,
            make_tab_length=o.make_tab_length, children=tab,
        ).color(native_colour(self.material_colour))

        return LidPlate(plate=top, size=[iw, il], thickness=lt, origin=[off, off], shell=tabs)

    def _lid_adjustment(self, stack):
        """Flip the lid over: it is built face-up (so the decoration lands on the outer
        face) and printed face-down."""
        return stack.rotate([180, 0, 0]).translate([0, self.length, self.lid_thickness])
