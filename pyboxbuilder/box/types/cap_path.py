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
        """A cap whose skirt follows the same outline as the body."""
        from pyboxbuilder.box.features import path_cap
        from pyboxbuilder.box.shell import block

        path = spec.get("path") or ()
        cap_height = spec.get("cap_height", 8.0)
        if not path:
            lt = spec.get("lid_thickness", 2.0)
            wt = spec.get("wall_thickness", 2.0)
            slack = 0.2
            cap = block(
                [spec["width"] + 2 * (wt + slack), spec["length"] + 2 * (wt + slack),
                 lt + cap_height],
                at=(-(wt + slack), -(wt + slack), spec["height"] - cap_height),
            )
            cavity = block(
                [spec["width"] + 2 * slack, spec["length"] + 2 * slack, cap_height],
                at=(-slack, -slack, spec["height"] - cap_height),
            )
            return cap - cavity
        return path_cap(spec, path, cap_height)
