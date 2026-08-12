# SPDX-License-Identifier: Apache-2.0
"""SlidingBox — sliding lid box type implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from spec_driven.box.base import Interior


class SlidingBox:
    """Sliding lid box type.

    Produces a box body with dovetail grooves on two walls where the lid
    slides in, and a sliding lid that mates with those grooves.
    """

    def interior(self, spec: dict) -> Interior:
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        lt = spec.get("lid_thickness", 2.0)
        return Interior(
            width=spec["width"] - 2 * wt,
            length=spec["length"] - 2 * wt,
            height=spec["height"] - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _build_shell(self, spec: dict) -> "Bosl2Solid":
        """Build the hollow box body shell."""
        from pybosl2 import cuboid

        wt = spec.get("wall_thickness", 2.0)
        outer = cuboid([spec["width"], spec["length"], spec["height"]])
        inner_w = spec["width"] - 2 * wt
        inner_l = spec["length"] - 2 * wt
        inner_h = spec["height"] - spec.get("floor_thickness", 1.6)
        inner = cuboid([inner_w, inner_l, inner_h])
        inner = inner.translate([wt, wt, spec.get("floor_thickness", 1.6)])
        body = outer - inner
        return body

    def _add_dovetail_grooves(
        self, body: "Bosl2Solid", spec: dict
    ) -> "Bosl2Solid":
        """Cut dovetail grooves into the two non-sliding walls for lid track."""
        from pybosl2 import cuboid

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        groove_w = spec["width"] - 2 * wt
        groove_l = lt + 0.4  # tolerance for sliding fit
        groove_h = lt + 0.2

        groove_left = cuboid([groove_w, groove_l, groove_h])
        groove_left = groove_left.translate([
            wt, wt - groove_l, spec["height"] - lt - groove_l,
        ])

        groove_right = cuboid([groove_w, groove_l, groove_h])
        groove_right = groove_right.translate([
            wt, spec["length"] - wt, spec["height"] - lt - groove_l,
        ])

        return body - groove_left - groove_right

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.get("dovetail", True):
            body = self._add_dovetail_grooves(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """Build the sliding lid that fits into the dovetail grooves."""
        from pybosl2 import cuboid

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        lid_w = spec["width"] - 2 * wt
        lid_l = spec["length"] - 2 * wt
        lid = cuboid([lid_w, lid_l, lt])
        lid = lid.translate([wt, wt, spec["height"] - lt])
        return lid
