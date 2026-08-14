# SPDX-License-Identifier: Apache-2.0
"""SlidingCatchBox — sliding-catch lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior


class SlidingCatchBox:
    """Sliding-catch lid box type."""

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

    def preferred_scoop_side(self, spec: dict):
        """A finger scoop belongs in the wall the lid leaves by.

        The other three carry the lid — two hold its grooves — and a scoop cut
        into a groove takes away the bearing that keeps the lid straight.
        """
        from pyboxbuilder.enums import ScoopSide

        return ScoopSide.RIGHT

    def lid_rounded_edges(self, spec: dict) -> list:
        """Only the end that finishes outside the box: its top edge and the two
        vertical corners there. The rest of the plate lives in the channel."""
        from pybosl2 import Anchor

        return [Anchor.TOP_RIGHT, Anchor.FRONT_RIGHT, Anchor.BACK_RIGHT]

    def build_body(self, spec: dict) -> "Bosl2Solid":
        """Sliding grooves, plus a dimple beside the outlet for the catch."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track
        from pyboxbuilder.box.shell import build_shell

        body = build_shell(spec) - sliding_track(spec).body
        return body - sliding_catch(spec, spec.get("catch_radius", 1.0), "x").body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """The sliding plate with a bump that clicks into the body's dimple."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track

        return sliding_track(spec).lid | sliding_catch(
            spec, spec.get("catch_radius", 1.0), "x"
        ).lid
