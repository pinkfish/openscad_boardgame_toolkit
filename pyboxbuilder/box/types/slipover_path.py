# SPDX-License-Identifier: Apache-2.0
"""SlipoverPathBox — slipover-path lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


class SlipoverPathBox:
    """Slipover-path lid box type."""

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
        """A hollow tray on a polygon footprint, for a sleeve to slip over."""
        from pyboxbuilder.box.features import extrude_footprint, offset_footprint
        from pyboxbuilder.box.shell import build_shell

        path = spec.get("path") or ()
        if not path:
            return build_shell(spec)

        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        outer = extrude_footprint(path, spec["height"])
        if not spec.get("hollow", True):
            return outer
        inner = extrude_footprint(offset_footprint(path, wt), spec["height"] - ft, ft)
        return outer - inner

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve following the body's outline, stopping at the foot."""
        from pyboxbuilder.box.features import path_sleeve
        from pyboxbuilder.box.shell import block

        slip = spec.get("slip", 1.6)
        foot = spec.get("foot", 0.0)
        path = spec.get("path") or ()
        if not path:
            lt = spec.get("lid_thickness", 2.0)
            skirt = spec["height"] - foot
            outer = block(
                [spec["width"] + 2 * slip, spec["length"] + 2 * slip, lt + skirt],
                at=(-slip, -slip, foot),
            )
            cavity = block(
                [spec["width"] + 0.4, spec["length"] + 0.4, skirt],
                at=(-0.2, -0.2, foot),
            )
            return outer - cavity
        return path_sleeve(spec, path, slip, foot)
