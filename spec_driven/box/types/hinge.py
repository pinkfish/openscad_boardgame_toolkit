# SPDX-License-Identifier: Apache-2.0
"""HingeBox — pin-hinge lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from spec_driven.box.base import Interior


class HingeBox:
    """Pin-hinge lid box type."""

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
        from pybosl2 import cuboid
        try:
            from pybosl2 import cylinder
        except ImportError:
            pass
        from pybosl2 import cuboid
        try:
            from pybosl2 import cylinder
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

        # Hinge knuckles on back wall
        hinge_d = spec.get("hinge_diameter", 6.0)
        hinge_count = spec.get("hinge_count", 3)
        body = outer - inner
        spacing = spec["width"] / (hinge_count + 1)
        for i in range(hinge_count):
            x = spacing * (i + 1)
            knuckle = cylinder(height=spec["length"] * 0.1 + wt, radius=hinge_d / 2)
            knuckle = knuckle.rotate([90, 0, 0])
            knuckle = knuckle.translate([x, spec["length"], spec["height"]])
            body = body | knuckle

        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        from pybosl2 import cuboid
        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        lid = cuboid([spec["width"], spec["length"], lt])
        return lid.translate([0, 0, spec["height"]])
