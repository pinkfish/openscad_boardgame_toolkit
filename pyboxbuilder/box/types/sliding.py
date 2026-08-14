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

    def slides_along_length(self, spec: dict) -> bool:
        """Whether the lid slides along Y rather than X.

        The lid leaves through the **shorter** face, which means sliding along
        the longer axis. That is what a card box wants: the opening is the
        narrow end, the lid is supported along its long run by the grooves, and
        the box reads the right way round. Sliding along the short axis instead
        puts the opening on the wide face and the grooves on the short walls,
        where they have least material to bite into.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            True when the box is longer than it is wide.
        """
        return spec["length"] > spec["width"]

    def open_end_side(self, spec: dict) -> "ScoopSide":
        """The wall the lid slides out through.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            `BACK` when the lid slides along the length, else `RIGHT`.
        """
        from pyboxbuilder.enums import ScoopSide

        return ScoopSide.BACK if self.slides_along_length(spec) else ScoopSide.RIGHT

    def wall_tops(self, spec: dict) -> dict:
        """Where each wall ends, which is not the same height all round.

        The channel is cut out of the top band across the whole box and runs
        out through the exit wall, so **every** wall effectively stops a lid
        thickness below the box's top: the exit wall because its material is
        gone, the other three because anything cut above that line breaks into
        the channel the lid slides in.

        Args:
            spec: Needs `height`; reads `lid_thickness`.

        Returns:
            ``{ScoopSide: z}`` for all four sides.
        """
        from pyboxbuilder.enums import ScoopSide

        top = spec["height"] - (spec.get("lid_thickness", 2.0) or 0.0)
        return {side: top for side in ScoopSide}

    def preferred_scoop_side(self, spec: dict) -> "ScoopSide":
        """Put a finger scoop in the wall the lid comes out of.

        On a sliding box the cards leave the same way the lid does, so the cut
        belongs in that wall — and only that wall will do. The other three
        carry the lid: two hold the grooves it rides in, and cutting a scoop
        into a groove takes away the bearing that keeps the lid straight.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            The open end's side.
        """
        return self.open_end_side(spec)

    def lid_rounded_edges(self, spec: dict) -> list:
        """Which of the lid's edges may be rounded.

        Only the end that ends up **outside** the box: its top edge and its two
        vertical corners. The other three sides of the plate live in the
        channel — two in the grooves, one against the stop — and rounding them
        would round away the very surfaces that support and locate the lid.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            A pybosl2 ``edges=`` selector for the exposed end.
        """
        from pybosl2 import Anchor

        if self.slides_along_length(spec):
            return [Anchor.TOP_BACK, Anchor.BACK_LEFT, Anchor.BACK_RIGHT]
        return [Anchor.TOP_RIGHT, Anchor.FRONT_RIGHT, Anchor.BACK_RIGHT]

    def _along_axis(self, spec: dict) -> str:
        """Which axis the lid slides along, for the dovetail geometry.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            ``"y"`` when the lid slides along the length, else ``"x"``.
        """
        return "y" if self.slides_along_length(spec) else "x"

    def _cut_lid_channel(
        self, body: "Bosl2Solid", spec: dict
    ) -> "Bosl2Solid":
        """Cut the dovetailed slot the lid slides along, open at one end.

        One subtraction does both halves of the job, because they are the same
        slot: it bites the dovetail into each side wall to make the grooves,
        and it runs out through the far end wall so the lid has somewhere to
        enter. Cutting only the grooves leaves a box with a solid wall across
        the front of its own track — a lid that can be dropped in but never
        slid, which is the entire point of the type.

        The near end keeps its wall: that is the stop the lid closes against.

        Args:
            body: The box body to cut.
            spec: Needs `width`, `length`, `height`, `wall_thickness`,
                `lid_thickness`.

        Returns:
            The body with the dovetail channel cut.
        """
        from pyboxbuilder.box.features import dovetail_track

        return body - dovetail_track(spec, self._along_axis(spec)).body

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.get("dovetail", True):
            body = self._cut_lid_channel(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """Build the sliding lid — a dovetailed plate, chamfered at its leading end."""
        from pyboxbuilder.box.features import dovetail_track

        closure = dovetail_track(spec, self._along_axis(spec))
        assert closure.lid is not None
        return closure.lid
