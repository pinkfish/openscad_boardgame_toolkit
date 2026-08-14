# SPDX-License-Identifier: Apache-2.0
"""CapPathBox — cap-path lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


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
        """A hollow tray on a polygon footprint, sized for a cap to fit over."""
        from pyboxbuilder.box.features import (
            extrude_footprint, offset_footprint, path_body_metrics,
        )
        from pyboxbuilder.box.shell import build_shell  # noqa: F401

        path = spec.get("path") or ()
        if not path:
            from pyboxbuilder.box.features import cap_body

            return cap_body(spec)

        # A polygon body is set in all round and stops short, so the cap that
        # wraps it comes back out to the declared footprint and height.
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
        """A cap whose skirt follows the same outline as the body."""
        from pyboxbuilder.box.features import cap_lid, path_cap

        path = spec.get("path") or ()
        if not path:
            return cap_lid(spec)
        return path_cap(spec, path, spec.get("cap_height") or min(10.0, spec["height"] / 2))
