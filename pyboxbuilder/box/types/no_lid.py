# SPDX-License-Identifier: Apache-2.0
"""NoLidBox — no-lid (open tray) box type with stackable rims and magnets."""

from __future__ import annotations

from pyboxbuilder.precision import kwargs as precision_kwargs

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import Interior
from pyboxbuilder.enums import MagnetType, StackableMode


class NoLidBox:
    """No-lid box type (open tray). Supports stackable rims and side magnets."""

    def interior(self, spec: dict) -> Interior:
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        return Interior(
            width=spec["width"] - 2 * wt,
            length=spec["length"] - 2 * wt,
            height=spec["height"] - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def _build_shell(self, spec: dict) -> "Bosl2Solid":
        from pyboxbuilder.box.shell import add_no_lid_finger_holes, build_shell

        add_no_lid_finger_holes(spec)
        body = build_shell(spec)
        return body

    def _add_stackable_rim(self, body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
        """Add an interlocking ring for stackable boxes.

        inside  → a recess carved into the top rim (box nests inside the box above)
        outside → a ridge added around the outside (box fits around the box below)
        """
        from pyboxbuilder.box.shell import block

        wt = spec.get("wall_thickness", 2.0)
        stack = spec.get("stackable_thickness") or wt
        fit = spec.get("stackable_fit_offset", 0.1)
        mode = spec.get("stackable") or StackableMode.INSIDE

        if mode is StackableMode.INSIDE:
            # Carve a recess around the top rim, so the box above nests into it.
            recess_w = spec["width"] - 2 * (wt - fit)
            recess_l = spec["length"] - 2 * (wt - fit)
            recess = block(
                [recess_w, recess_l, stack + 0.5],
                at=(
                    (spec["width"] - recess_w) / 2,
                    (spec["length"] - recess_l) / 2,
                    spec["height"] - stack,
                ),
            )
            return body - recess
        elif mode == "outside":
            # Add a ridge around the bottom outside, so it grips the box below.
            ridge_w = spec["width"] + 2 * (stack - fit)
            ridge_l = spec["length"] + 2 * (stack - fit)
            ridge = block(
                [ridge_w, ridge_l, stack],
                at=(
                    (spec["width"] - ridge_w) / 2,
                    (spec["length"] - ridge_l) / 2,
                    0,
                ),
            )
            return body | ridge
        return body

    def _add_magnet_slots(self, body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
        """Carve magnet cavities into opposing side walls."""
        from pybosl2 import cuboid, cylinder

        magnet_type = spec.get("magnet_type")
        if magnet_type is None or magnet_type is MagnetType.NONE:
            return body

        size = spec.get("magnet_size")
        depth = size[2] if size and len(size) > 2 else (
            3.0 if magnet_type is MagnetType.ROUND else 2.0
        )

        def slot():
            """A fresh solid per side — one handle must not span two branches."""
            if magnet_type is MagnetType.ROUND:
                diameter = size[0] if size else 6.0
                # Lay the cylinder along Y so it sinks into a front/back wall.
                return cylinder(height=depth, radius=diameter / 2 + 0.1, **precision_kwargs()).rotate([90, 0, 0])
            w = size[0] if size else 10.0
            l = size[1] if size and len(size) > 1 else 5.0
            return cuboid([w + 0.2, depth, l + 0.2])

        mid_h = spec["height"] / 2
        # Blind pockets in the middle of the two opposing walls, open outward.
        slot_a = slot().translate([spec["width"] / 2, depth / 2, mid_h])
        slot_b = slot().translate([spec["width"] / 2, spec["length"] - depth / 2, mid_h])

        return body - slot_a - slot_b

    def build_body(self, spec: dict) -> "Bosl2Solid":
        body = self._build_shell(spec)
        if spec.get("stackable"):
            body = self._add_stackable_rim(body, spec)
        if spec.get("magnet_type") not in (None, MagnetType.NONE):
            body = self._add_magnet_slots(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        from pybosl2 import cuboid
        """No-lid boxes have no lid."""
        return None
