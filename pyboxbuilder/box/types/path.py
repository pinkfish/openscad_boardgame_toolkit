# SPDX-License-Identifier: Apache-2.0
"""PathBox — lidless tray with an arbitrary polygon footprint."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from pyboxbuilder.box.base import Interior


class PathBox:
    """Open tray whose footprint is a 2D polygon path rather than a rectangle.

    Produces a body only — a path box has no lid, so `build_lid` returns None
    and the exporter writes no `_lid.3mf` for it.
    """

    def interior(self, spec: dict) -> Interior:
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        return Interior(
            width=spec["width"] - 2 * wt,
            length=spec["length"] - 2 * wt,
            height=spec["height"] - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def build_body(self, spec: dict) -> "Bosl2Solid":
        wt = spec.get("wall_thickness", 2.0)
        ft = spec.get("floor_thickness", 1.6)
        path = spec.get("path") or ()

        from pyboxbuilder.box.shell import (
            add_no_lid_finger_holes,
            apply_finger_holes,
            build_shell,
        )

        if not path:
            add_no_lid_finger_holes(spec)
            return build_shell(spec)

        outer = self._extrude(path, spec["height"])
        if not spec.get("hollow", True):
            add_no_lid_finger_holes(spec)
            return apply_finger_holes(outer, spec)
        inner = self._extrude(_inset_path(path, wt), spec["height"] - ft)
        body = outer - inner.translate([0.0, 0.0, ft])
        add_no_lid_finger_holes(spec)
        return apply_finger_holes(body, spec)

    @staticmethod
    def _extrude(path, height: float) -> "Bosl2Solid":
        """Extrude a polygon outline with its base at z = 0.

        `linear_extrude` is the one operation that is *not* centre-anchored in Z
        — it already grows upward from the bed, which is what a tray wants.
        """
        from pybosl2 import Path2D

        profile = Path2D([(float(x), float(y)) for x, y in path], closed=True)
        return profile.linear_extrude(height=height)

    def build_lid(self, spec: dict, decoration: object = None) -> None:
        """Path boxes have no lid."""
        return None


def _inset_path(
    path: tuple[tuple[float, float], ...], distance: float
) -> tuple[tuple[float, float], ...]:
    """Shrink a footprint by `distance` to get the tray's inner cavity.

    Leftover regions from the packer are rectilinear, and those get an exact
    edge-wise inset — a centroid scale would pull an L's reflex corner the wrong
    way and thin one arm while fattening the other. Anything else falls back to
    the centroid scale, which is fine for the convex outlines a caller is likely
    to hand-write and never self-intersects.
    """
    from pyboxbuilder.paths import inset_rectilinear, is_rectilinear

    if is_rectilinear(path):
        return inset_rectilinear(path, distance)

    cx = sum(p[0] for p in path) / len(path)
    cy = sum(p[1] for p in path) / len(path)
    out = []
    for x, y in path:
        dx, dy = x - cx, y - cy
        span = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        scale = max(0.0, (span - distance) / span)
        out.append((cx + dx * scale, cy + dy * scale))
    return tuple(out)
