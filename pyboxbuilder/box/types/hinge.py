# SPDX-License-Identifier: Apache-2.0
"""HingeBox — pin-hinge lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


class HingeBox:
    """Pin-hinge lid box type."""

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

    @staticmethod
    def _body_spec(spec: dict) -> dict:
        """The body stops a lid's thickness short, so the closed lid seats on it."""
        lt = spec.get("lid_thickness", 2.0)
        return {**spec, "height": spec["height"] - lt}

    def _closure(self, spec: dict):
        """Both halves of the knuckle hinge, on one shared pin axis."""
        from pyboxbuilder.box.features import filament_hinge

        return filament_hinge(
            self._body_spec(spec),
            filament_diameter=spec.get("hinge_pin_diameter", 3.0),
            knuckles=spec.get("hinge_count", 5),
            lid_thickness=spec.get("lid_thickness", 2.0),
        )

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """The shell carrying every other knuckle of the hinge."""
        from pyboxbuilder.box.shell import build_shell

        body = build_shell(self._body_spec(spec))
        closure = self._closure(spec)
        return body if closure.body is None else body | closure.body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """The lid carrying the interleaving knuckles, bored for the same pin.

        The knuckles alternate along one axis with a print gap between them, so
        the two halves come off the bed as separate parts and articulate once
        the pin is fitted.
        """
        from pyboxbuilder.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        lid = block(
            [spec["width"], spec["length"], lt],
            at=(0, 0, self._body_spec(spec)["height"]),
        )
        closure = self._closure(spec)
        return lid if closure.lid is None else lid | closure.lid
