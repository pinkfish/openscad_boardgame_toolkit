# SPDX-License-Identifier: Apache-2.0
"""MagneticBox — magnetic-closure lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


from spec_driven.box.base import Interior


class MagneticBox:
    """Magnetic-closure lid box type."""

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
        body = outer - inner

        # Magnet cavities in walls
        md = spec.get("magnet_diameter", 6.0)
        mh = spec.get("magnet_height", 3.0)
        nw = spec.get("magnet_count_width", 2)
        nl = spec.get("magnet_count_length", 2)
        mag = cylinder(h=mh + 0.2, r=md / 2 + 0.1)
        for xi in range(nw):
            mx = spec["width"] * (xi + 1) / (nw + 1)
            for yi in range(nl):
                my = spec["length"] * (yi + 1) / (nl + 1)
                mag_pos = mag.translate([mx, my, spec["height"] - mh])
                body = body - mag_pos

        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        lt = spec.get("lid_thickness", 2.0)
        lid = cuboid([spec["width"], spec["length"], lt])
        return lid.translate([0, 0, spec["height"]])
