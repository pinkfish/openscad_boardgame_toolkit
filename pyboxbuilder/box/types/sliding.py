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

    def _lid_channel(self, spec: dict) -> tuple[float, float, float, float]:
        """Geometry of the slot the lid lives in: (depth, y0, y_extent, z0).

        Args:
            spec: Needs `length`, `height`; reads `wall_thickness`,
                `lid_thickness`.

        Returns:
            The groove depth into each side wall, where the channel starts in
            Y, how far it runs in Y, and the Z it starts at.
        """
        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        groove_depth = min(wt - 0.6, lt)  # bite into the wall, never through it
        y0 = wt - groove_depth
        return groove_depth, y0, spec["length"] - 2 * y0, spec["height"] - lt

    def _cut_lid_channel(
        self, body: "Bosl2Solid", spec: dict
    ) -> "Bosl2Solid":
        """Cut the slot the lid slides along, open at one end.

        One subtraction does both halves of the job, because they are the same
        slot: it bites `groove_depth` into each side wall to make the grooves,
        and it runs out through the **+X end wall** so the lid has somewhere to
        enter. Cutting only the grooves leaves a box with a solid wall across
        the front of its own track — a lid that can be dropped in but never
        slid, which is the entire point of the type.

        The far (-X) end keeps its wall: that is the stop the lid closes
        against.

        Args:
            body: The box body to cut.
            spec: Needs `width`, `length`, `height`, `wall_thickness`,
                `lid_thickness`.

        Returns:
            The body with the channel cut.
        """
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        _, y0, y_extent, z0 = self._lid_channel(spec)

        # From the inside face of the stop wall, out through the open end.
        return body - block(
            [spec["width"] - wt + 0.1, y_extent, lt + 0.1],
            at=(wt, y0, z0 - 0.05),
        )

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.get("dovetail", True):
            body = self._cut_lid_channel(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """Build the sliding lid — a plate wide enough to reach into the grooves."""
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        slack = 0.2
        _, y0, y_extent, z0 = self._lid_channel(spec)

        # Fills the channel from the stop wall to the open end, so the closed
        # lid finishes flush with the box rather than sitting short of it.
        return block(
            [spec["width"] - wt - slack, y_extent - slack, lt],
            at=(wt + slack / 2, y0 + slack / 2, z0),
        )
