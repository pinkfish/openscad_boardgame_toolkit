# SPDX-License-Identifier: Apache-2.0
"""InsetBox — inset lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


class InsetBox:
    """Inset lid box type."""

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
        """The shell with a ledge cut into its top rim for the lid to sit in."""
        from pyboxbuilder.box.features import rabbet
        from pyboxbuilder.box.shell import build_shell

        closure = rabbet(spec, inset=spec.get("inset", 1.0))
        return build_shell(spec) - closure.body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A plate that drops into the rabbet and finishes flush with the rim."""
        from pyboxbuilder.box.features import rabbet

        return rabbet(spec, inset=spec.get("inset", 1.0)).lid
