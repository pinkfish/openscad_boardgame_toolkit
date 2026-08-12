# SPDX-License-Identifier: Apache-2.0
"""CapPathBox — cap-path lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


from spec_driven.box.base import Interior


class CapPathBox:
    """Cap-path lid box type."""

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
        lt = spec.get("lid_thickness", 2.0)
        lid = cuboid([spec["width"], spec["length"], lt])
        return lid.translate([0, 0, spec["height"]])
