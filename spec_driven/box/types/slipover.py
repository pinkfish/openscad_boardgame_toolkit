# SPDX-License-Identifier: Apache-2.0
"""SlipoverBox — slipover lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


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
        from spec_driven.box.shell import build_shell

        body = build_shell(spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve that slips down over the whole box."""
        from spec_driven.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        slip = spec.get("slip", 1.6)
        lid_h = lt + spec.get("cap_height", 8.0)
        origin = -slip

        outer = block(
            [spec["width"] + 2 * slip, spec["length"] + 2 * slip, lid_h],
            at=(origin, origin, spec["height"] - lid_h + lt),
        )
        cavity = block(
            [spec["width"], spec["length"], lid_h - lt],
            at=(0, 0, spec["height"] - lid_h + lt),
        )
        return outer - cavity
