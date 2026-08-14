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

    @staticmethod
    def _body_spec(spec: dict) -> dict:
        """The body stops a lid's thickness below the box's stated height.

        The lid closes onto the rim rather than inside it, so the two together
        come to `height` — build the walls full height and the closed lid would
        sit in the same space as them.
        """
        lt = spec.get("lid_thickness", 2.0)
        return {**spec, "height": spec["height"] - lt}

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """The shell with half the hinge knuckles along its back edge."""
        from pyboxbuilder.box.features import filament_hinge
        from pyboxbuilder.box.shell import build_shell

        body_spec = self._body_spec(spec)
        closure = filament_hinge(
            body_spec,
            spec.get("filament_diameter", 1.75),
            spec.get("hinge_knuckles", 5),
        )
        body = build_shell(body_spec)
        return body if closure.body is None else body | closure.body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A plate carrying the interleaving knuckles, on the same pin axis.

        The hinge pin is a length of filament threaded through after printing,
        so the two halves stay separate parts.
        """
        from pyboxbuilder.box.features import filament_hinge
        from pyboxbuilder.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        body_spec = self._body_spec(spec)
        lid = block(
            [spec["width"], spec["length"], lt], at=(0, 0, body_spec["height"])
        )
        closure = filament_hinge(
            body_spec,
            spec.get("filament_diameter", 1.75),
            spec.get("hinge_knuckles", 5),
        )
        return lid if closure.lid is None else lid | closure.lid
