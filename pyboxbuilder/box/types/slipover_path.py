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
        from pyboxbuilder.box.features import (
            extrude_footprint, offset_footprint, path_body_metrics,
        )

        path = spec.get("path") or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_body(spec)

        # Set in all round and stopping short, so the sleeve that wraps it comes
        # back out to the declared outline and height.
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        inset, body_height = path_body_metrics(spec)

        body_path = offset_footprint(path, inset)
        outer = extrude_footprint(body_path, body_height)
        if not spec.get("hollow", True):
            return outer
        inner = extrude_footprint(
            offset_footprint(body_path, wt), body_height - ft, ft
        )
        return outer - inner

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve following the body's outline, stopping at the foot."""
        from pyboxbuilder.box.features import path_sleeve

        path = spec.get("path") or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_lid(spec)
        return path_sleeve(spec, path, spec.get("slip", 1.6), spec.get("foot", 0.0))
