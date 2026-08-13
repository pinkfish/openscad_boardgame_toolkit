# SPDX-License-Identifier: Apache-2.0
"""HingeBox — pin-hinge lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


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
        from pyboxbuilder.box.shell import build_shell
        from pybosl2 import cylinder
        wt = spec.get("wall_thickness", 2.0)

        body = build_shell(spec)

        # Hinge knuckles along the back wall, lying on the wall's top edge.
        hinge_d = spec.get("hinge_diameter", 6.0)
        hinge_count = spec.get("hinge_count", 3)
        knuckle_len = spec["width"] / (hinge_count * 2 + 1)
        spacing = spec["width"] / (hinge_count + 1)
        for i in range(hinge_count):
            # A cylinder is centre-anchored and stands on Z; lay it along X and
            # centre it on the wall so it straddles the outside face.
            knuckle = cylinder(height=knuckle_len, radius=hinge_d / 2)
            knuckle = knuckle.rotate([0, 90, 0])
            knuckle = knuckle.translate([
                spacing * (i + 1),
                spec["length"] - wt / 2,
                spec["height"] - hinge_d / 2,
            ])
            body = body | knuckle

        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        from pyboxbuilder.box.shell import block
        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        return block([spec["width"], spec["length"], lt], at=(0, 0, spec["height"]))
