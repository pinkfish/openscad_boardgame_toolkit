# SPDX-License-Identifier: Apache-2.0
"""NoLidBox — no-lid (open tray) box type with stackable rims and magnets."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


from spec_driven.box.base import Interior


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
        from bosl2 import cuboid
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        outer = cuboid([spec["width"], spec["length"], spec["height"]])
        inner = cuboid([
            spec["width"] - 2 * wt,
            spec["length"] - 2 * wt,
            spec["height"] - ft,
        ]).translate([wt, wt, ft])
        return outer - inner

    def _add_stackable_rim(self, body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
        """Add an interlocking ring for stackable boxes.

        inside  → a recess carved into the top rim (box nests inside the box above)
        outside → a ridge added around the outside (box fits around the box below)
        """
        from bosl2 import cuboid
        wt = spec.get("wall_thickness", 2.0)
        stack = spec.get("stackable_thickness") or wt
        fit = spec.get("stackable_fit_offset", 0.1)
        mode = spec.get("stackable", "inside")

        if mode == "inside":
            # Carve a recess around the top inner rim
            recess_w = spec["width"] - 2 * (wt - fit)
            recess_l = spec["length"] - 2 * (wt - fit)
            recess = cuboid([recess_w, recess_l, stack + 0.5])
            recess = recess.translate([
                (spec["width"] - recess_w) / 2,
                (spec["length"] - recess_l) / 2,
                spec["height"] - stack,
            ])
            return body - recess
        elif mode == "outside":
            # Add a ridge around the bottom outside
            ridge_w = spec["width"] + 2 * (stack - fit)
            ridge_l = spec["length"] + 2 * (stack - fit)
            ridge = cuboid([ridge_w, ridge_l, stack])
            ridge = ridge.translate([
                (spec["width"] - ridge_w) / 2,
                (spec["length"] - ridge_l) / 2,
                0,
            ])
            return body + ridge
        return body

    def _add_magnet_slots(self, body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
        """Carve magnet cavities into opposing side walls."""
        from bosl2 import cuboid, cylinder
        magnet_type = spec.get("magnet_type")
        if not magnet_type:
            return body

        size = spec.get("magnet_size")
        if magnet_type == "round":
            diameter = size[0] if size else 6.0
            depth = size[2] if size and len(size) > 2 else 3.0
            slot = cylinder(h=depth + 0.2, r=diameter / 2 + 0.1)
        else:  # rect
            w = size[0] if size else 10.0
            l = size[1] if size and len(size) > 1 else 5.0
            depth = size[2] if size and len(size) > 2 else 2.0
            slot = cuboid([w, l, depth + 0.2])

        wt = spec.get("wall_thickness", 2.0)
        mid_h = spec["height"] / 2

        # Opposing sides (front/back walls): place slots at the wall midpoint
        if magnet_type == "round":
            slot_a = slot.rotate_x(90).translate([spec["width"] / 2, -0.1, mid_h])
            slot_b = slot.rotate_x(90).translate([
                spec["width"] / 2, spec["length"] + 0.1, mid_h,
            ])
        else:
            slot_a = slot.translate([
                (spec["width"] - (size[0] if size else 10)) / 2,
                -0.1,
                mid_h - (size[2] if size and len(size) > 2 else 2) / 2,
            ])
            slot_b = slot.translate([
                (spec["width"] - (size[0] if size else 10)) / 2,
                spec["length"] + 0.1,
                mid_h - (size[2] if size and len(size) > 2 else 2) / 2,
            ])

        return body - slot_a - slot_b

    def build_body(self, spec: dict) -> "Bosl2Solid":
        body = self._build_shell(spec)
        if spec.get("stackable"):
            body = self._add_stackable_rim(body, spec)
        if spec.get("magnet_type"):
            body = self._add_magnet_slots(body, spec)
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """No-lid boxes have no lid."""
        return None
