# SPDX-License-Identifier: Apache-2.0
"""SlidingBox — sliding lid box type implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


from dataclasses import dataclass

from spec_driven.box.base import Interior

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


@dataclass
class SlidingBoxSpec:
    """Internal spec extracted from the builder for sliding box construction."""

    label: str
    width: float
    length: float
    height: float
    wall_thickness: float
    floor_thickness: float
    lid_thickness: float
    dovetail: bool = True


class SlidingBox:
    """Sliding lid box type.

    Produces a box body with dovetail grooves on two walls where the lid
    slides in, and a sliding lid that mates with those grooves.
    """

    def interior(self, spec: SlidingBoxSpec) -> Interior:
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _build_shell(self, spec: SlidingBoxSpec) -> "Bosl2Solid":
        """Build the hollow box body shell."""
        try:
            from bosl2 import Bosl2Solid, cuboid
        except ImportError as e:
            raise ImportError(
                "pybosl2 is required. Install with: pip install pybosl2"
            ) from e

        wt = spec.wall_thickness
        outer = cuboid([spec.width, spec.length, spec.height])
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = spec.height - spec.floor_thickness
        inner = cuboid([inner_w, inner_l, inner_h])
        inner = inner.translate([wt, wt, spec.floor_thickness])
        body = outer - inner
        return body

    def _add_dovetail_grooves(
        self, body: "Bosl2Solid", spec: SlidingBoxSpec
    ) -> "Bosl2Solid":
        """Cut dovetail grooves into the two non-sliding walls for lid track."""
        from bosl2 import cuboid

        wt = spec.wall_thickness
        lt = spec.lid_thickness
        groove_w = spec.width - 2 * wt
        groove_l = lt + 0.4  # tolerance for sliding fit
        groove_h = lt + 0.2

        # Groove near the top of the box on the left wall
        groove_left = cuboid([groove_w, groove_l, groove_h])
        groove_left = groove_left.translate([
            wt, wt - groove_l, spec.height - lt - groove_l,
        ])

        # Groove near the top of the box on the right wall
        groove_right = cuboid([groove_w, groove_l, groove_h])
        groove_right = groove_right.translate([
            wt, spec.length - wt, spec.height - lt - groove_l,
        ])

        return body - groove_left - groove_right

    def build_body(self, spec: SlidingBoxSpec) -> "Bosl2Solid":
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.dovetail:
            body = self._add_dovetail_grooves(body, spec)
        return body

    def build_lid(self, spec: SlidingBoxSpec) -> "Bosl2Solid":
        """Build the sliding lid that fits into the dovetail grooves."""
        from bosl2 import cuboid

        wt = spec.wall_thickness
        lt = spec.lid_thickness
        lid_w = spec.width - 2 * wt
        lid_l = spec.length - 2 * wt
        lid = cuboid([lid_w, lid_l, lt])
        lid = lid.translate([wt, wt, spec.height - lt])
        return lid
