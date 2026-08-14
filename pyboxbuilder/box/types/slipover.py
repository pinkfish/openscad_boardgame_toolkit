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
        """The tray, set in all round so the sleeve finishes flush.

        The declared size is the outside of the *closed* box, so the body is
        inset by a wall thickness and stops a lid thickness short — the sleeve
        occupies the difference. A `foot` keeps its full footprint at the very
        bottom for the sleeve to seat against.
        """
        from pyboxbuilder.box.features import slipover_metrics
        from pyboxbuilder.box.shell import block, build_shell

        inset, body_height = slipover_metrics(spec)
        foot = spec.get("foot", 0.0)

        body = build_shell({
            **spec,
            "width": spec["width"] - 2 * inset,
            "length": spec["length"] - 2 * inset,
            "height": body_height,
        }).translate([inset, inset, 0.0])

        if foot > 0:
            body = body | block([spec["width"], spec["length"], foot])
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve that slips down over the body, stopping at the foot."""
        from pyboxbuilder.box.features import WIGGLE_MM, slipover_metrics
        from pyboxbuilder.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        foot = spec.get("foot", 0.0)
        slack = spec.get("slip_slack", WIGGLE_MM)
        inset, body_height = slipover_metrics(spec)

        outer = block(
            [spec["width"], spec["length"], spec["height"] - foot],
            at=(0.0, 0.0, foot),
        )
        cavity = block(
            [
                spec["width"] - 2 * inset + 2 * slack,
                spec["length"] - 2 * inset + 2 * slack,
                spec["height"] - foot - lt,
            ],
            at=(inset - slack, inset - slack, foot),
        )
        return outer - cavity
