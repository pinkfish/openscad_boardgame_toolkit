# SPDX-License-Identifier: Apache-2.0
"""SlipoverBox — slipover lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


from spec_driven.box.base import Interior


class SlipoverBox:
    """Slipover lid box type."""

    def interior(self, spec: dict) -> Interior:
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        lt = spec.get("lid_thickness", 2.0)
        return Interior(
            width=spec["width"] - 2 * wt,
            length=spec["length"] - 2 * wt,
            height=spec["height"] - lt - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def build_body(self, spec: dict) -> "Bosl2Solid":
        from bosl2 import cuboid
        try:
            from bosl2 import cylinder
        except ImportError:
            pass
        from bosl2 import cuboid
        try:
            from bosl2 import cylinder
        except ImportError:
            pass
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        outer = cuboid([spec["width"], spec["length"], spec["height"]])
        inner = cuboid([
            spec["width"] - 2 * wt,
            spec["length"] - 2 * wt,
            spec["height"] - ft,
        ]).translate([wt, wt, ft])
        return outer - inner

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        slip = spec.get("slip", 1.6)
        lid_w = spec["width"] + 2 * slip
        lid_l = spec["length"] + 2 * slip
        lid_h = lt + spec.get("cap_height", 8.0)
        outer = cuboid([lid_w, lid_l, lid_h])
        inner = cuboid([spec["width"], spec["length"], lid_h - lt])
        inner = inner.translate([slip, slip, lt])
        return (outer - inner).translate([-slip, -slip, 0])
