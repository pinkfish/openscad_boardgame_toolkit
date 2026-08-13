# SPDX-License-Identifier: Apache-2.0
"""MagneticBox — magnetic-closure lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


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
        from pyboxbuilder.box.shell import build_shell
        from pybosl2 import cylinder

        body = build_shell(spec)

        # Magnet cavities in walls
        md = spec.get("magnet_diameter", 6.0)
        mh = spec.get("magnet_height", 3.0)
        nw = spec.get("magnet_count_width", 2)
        nl = spec.get("magnet_count_length", 2)
        # Blind pockets in the top rim: open upward, closed at the bottom so the
        # magnet cannot fall through.
        depth = mh + 0.2
        for xi in range(nw):
            mx = spec["width"] * (xi + 1) / (nw + 1)
            for yi in range(nl):
                my = spec["length"] * (yi + 1) / (nl + 1)
                pocket = cylinder(height=depth, radius=md / 2 + 0.1)
                pocket = pocket.translate([mx, my, spec["height"] - depth / 2])
                body = body - pocket

        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        from pyboxbuilder.box.shell import block
        lt = spec.get("lid_thickness", 2.0)
        return block([spec["width"], spec["length"], lt], at=(0, 0, spec["height"]))
