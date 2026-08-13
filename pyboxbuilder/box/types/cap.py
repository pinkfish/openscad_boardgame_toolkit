# SPDX-License-Identifier: Apache-2.0
"""CapBox — friction-fit cap lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from pyboxbuilder.box.base import Interior

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


class CapBox:
    """Cap (friction-fit) lid box type."""

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

        body = build_shell(spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A cap: a top plate with a skirt that grips the outside of the walls."""
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        cap_h = spec.get("cap_height", 8.0)
        slack = spec.get("cap_slack", 0.2)

        lid_w = spec["width"] + 2 * (wt + slack)
        lid_l = spec["length"] + 2 * (wt + slack)
        origin = -(wt + slack)

        cap = block([lid_w, lid_l, lt + cap_h], at=(origin, origin, spec["height"] - cap_h))
        cavity = block(
            [spec["width"] + 2 * slack, spec["length"] + 2 * slack, cap_h],
            at=(-slack, -slack, spec["height"] - cap_h),
        )
        return cap - cavity
