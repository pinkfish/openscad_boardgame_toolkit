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

# LibFile: magnetic_box.py
#    Magnetic box and lid generators.
#
# FileSummary: Magnetic box pieces for the magnetic boxes.
# FileGroup: Boxes

from __future__ import annotations

from base_bgtk import BACK, BOT, BOTTOM, FRONT, LEFT, RIGHT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401
import pybosl2.shapes3d
from box_base import LiddedBox, BoxSpec, BoxTypeOptions, LidPlate
from dataclasses import dataclass


@dataclass
class MagneticBoxOptions(BoxTypeOptions):
    """Magnetic-box options; pass via ``BoxSpec(type_options=MagneticBoxOptions(...))``."""

    magnet_diameter: float = 5
    magnet_thickness: float = 2
    magnet_border: float = 1.5


class MagneticBox(LiddedBox):
    """A box whose lid is held on by magnets set into the corners, on the new box
    system. Box and lid are separate prints; magnets are glued into both.

    The body is the box minus a lid-thick slice at the top; the lid is a flat plate at
    the OUTER footprint. Both carry four corner magnet pockets in matching positions.
    The lid runs through the shared overlay pipeline, so a label / shape pattern /
    fingernail lands on it like any other flat lid.

    Magnet size comes from ``BoxSpec(type_options=MagneticBoxOptions(
    magnet_diameter=5, magnet_thickness=2))``. ``contents`` are carved into the box.

    Usage::

        from box_base import BoxSpec
        from magnetic_box import MagneticBox, MagneticBoxOptions

        box = MagneticBox(BoxSpec(size=[100, 50, 20], label="mag",
                                  type_options=MagneticBoxOptions(magnet_diameter=6, magnet_thickness=2)))
        box.make_box().show()
        box.make_lid().show()
    """

    options_class = MagneticBoxOptions

    def _effective_height(self) -> float:
        # The body is a lid-thickness shorter than the outer height (the lid sits on top).
        return self.height - self.lid_thickness

    def _magnet_centres(self) -> list[tuple[float, float]]:
        o = self.options
        inset = o.magnet_diameter / 2 + o.magnet_border
        w, l = self.width, self.length
        return [(inset, inset), (w - inset, inset), (w - inset, l - inset), (inset, l - inset)]

    def _magnet_holes(self, obj, z: float):
        o = self.options
        for cx, cy in self._magnet_centres():
            hole = pybosl2.shapes3d.cyl(
                diameter=o.magnet_diameter, height=o.magnet_thickness + 1, anchor=BOTTOM
            ).translate([cx, cy, z])
            obj = obj - hole
        return obj

    def _build_box_body(self, contents):
        o = self.options
        body = pybosl2.shapes3d.cuboid(
            [self.width, self.length, self.height - self.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        body = self._magnet_holes(body, self.height - self.lid_thickness - o.magnet_thickness)
        return body.color(self.material_colour)

    def _lid_plate(self, lid) -> LidPlate:
        """A flat plate at the OUTER footprint with matching corner magnet pockets."""
        r = lid.lid_rounding if lid.lid_rounding is not None else self.wall_thickness
        top = pybosl2.shapes3d.cuboid(
            [self.width, self.length, self.lid_thickness],
            rounding=r,
            anchor=BOTTOM + FRONT + LEFT,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        top = self._magnet_holes(top, -1)   # holes open through the underside of the lid
        return LidPlate(
            plate=top.color(self.material_colour),
            size=[self.width, self.length],
            thickness=self.lid_thickness,
        )
