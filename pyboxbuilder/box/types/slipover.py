# SPDX-License-Identifier: Apache-2.0
"""SlipoverBox — slipover lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


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
        from pyboxbuilder.box.shell import build_shell

        body = build_shell(spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve that slips down over the box, stopping at the foot.

        `foot` leaves the bottom of the body exposed so the sleeve has something
        to seat against, which is how the original toolkit's slipover boxes are
        built. `foot=0` covers the whole body.
        """
        from pyboxbuilder.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        slip = spec.get("slip", 1.6)
        foot = spec.get("foot", 0.0)

        skirt = spec["height"] - foot
        lid_h = lt + skirt
        origin = -slip

        outer = block(
            [spec["width"] + 2 * slip, spec["length"] + 2 * slip, lid_h],
            at=(origin, origin, foot),
        )
        cavity = block(
            [spec["width"] + 0.4, spec["length"] + 0.4, skirt],
            at=(-0.2, -0.2, foot),
        )
        return outer - cavity
