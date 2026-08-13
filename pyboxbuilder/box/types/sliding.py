# SPDX-License-Identifier: Apache-2.0
"""SlidingBox — sliding lid box type implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from pyboxbuilder.box.base import Interior


class SlidingBox:
    """Sliding lid box type.

    Produces a box body with dovetail grooves on two walls where the lid
    slides in, and a sliding lid that mates with those grooves.
    """

    def interior(self, spec: dict) -> Interior:
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        lt = spec.get("lid_thickness", 2.0)
        return Interior(
            width=spec["width"] - 2 * wt,
            length=spec["length"] - 2 * wt,
            height=spec["height"] - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _build_shell(self, spec: dict) -> "Bosl2Solid":
        """Build the hollow box body shell."""
        from pyboxbuilder.box.shell import build_shell

        return build_shell(spec)

    def _add_dovetail_grooves(
        self, body: "Bosl2Solid", spec: dict
    ) -> "Bosl2Solid":
        """Cut grooves into the two side walls for the lid to slide along."""
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        groove_w = spec["width"] - 2 * wt
        groove_depth = min(wt - 0.6, lt)  # bite into the wall, never through it
        groove_h = lt + 0.2
        groove_z = spec["height"] - lt - 0.1

        groove_left = block(
            [groove_w, groove_depth, groove_h], at=(wt, wt - groove_depth, groove_z)
        )
        groove_right = block(
            [groove_w, groove_depth, groove_h],
            at=(wt, spec["length"] - wt, groove_z),
        )
        return body - groove_left - groove_right

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.get("dovetail", True):
            body = self._add_dovetail_grooves(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """Build the sliding lid — a plate wide enough to reach into the grooves."""
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        groove_depth = min(wt - 0.6, lt)
        slack = 0.2

        lid_l = spec["length"] - 2 * wt + 2 * groove_depth - slack
        return block(
            [spec["width"] - 2 * wt, lid_l, lt],
            at=(wt, wt - groove_depth + slack / 2, spec["height"] - lt),
        )
