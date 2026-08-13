# SPDX-License-Identifier: Apache-2.0
"""FilamentHingeBox — living-hinge lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


class FilamentHingeBox:
    """Filament (living) hinge lid box type."""

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
        from pyboxbuilder.box.shell import block
        lt = spec.get("lid_thickness", 2.0)
        hinge_gap = spec.get("hinge_gap", 0.4)
        return block([spec["width"], spec["length"], lt], at=(0, 0, spec["height"]))
