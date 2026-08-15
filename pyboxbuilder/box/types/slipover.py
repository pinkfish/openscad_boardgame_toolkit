# SPDX-License-Identifier: Apache-2.0
"""SlipoverBox — slipover lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

SLIPOVER_FINGER_MAX_MM = 20.0
"""Tallest a sleeve's corner notch gets, however deep the box."""

SLIPOVER_FINGER_MIN_RADIUS_MM = 7.0
"""Smallest notch radius that still admits a fingertip."""

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

        # The whole body is what the sleeve grips, so its corners take the
        # smaller mating radius — matched by the sleeve's cavity in build_lid.
        # Only the foot below the sleeve stays a fully-rounded exposed edge.
        from pyboxbuilder.rounding import mating_rounding

        body = build_shell({
            **spec,
            "width": spec["width"] - 2 * inset,
            "length": spec["length"] - 2 * inset,
            "height": body_height,
            # Already shortened for the sleeve, so its top is the inside's top.
            "interior_top": body_height,
            "rounding": mating_rounding(spec),
        }).translate([inset, inset, 0.0])

        if foot > 0:
            from pyboxbuilder.box.shell import body_rounding
            from pyboxbuilder.rounding import rounded_block, vertical_edges

            body = body | rounded_block(
                [spec["width"], spec["length"], foot],
                body_rounding(spec),
                vertical_edges(),
            )
        return body

    def build_lid(self, spec: dict, decoration: object = None) -> "Bosl2Solid":
        """A sleeve that slips down over the body, stopping at the foot."""
        from pyboxbuilder.box.features import WIGGLE_MM, slipover_metrics
        from pyboxbuilder.box.shell import block

        lt = spec.get("lid_thickness", 2.0)
        foot = spec.get("foot", 0.0)
        slack = spec.get("slip_slack", WIGGLE_MM)
        inset, body_height = slipover_metrics(spec)

        # The sleeve stops a gap short of the foot rather than closing onto it,
        # leaving a band of body showing all the way round for the fingers to
        # pull on (FR-002p).
        from pyboxbuilder.box.features import slipover_gap

        gap = min(slipover_gap(spec), spec["height"] - foot - lt)
        skirt = spec["height"] - foot - gap
        outer = block(
            [spec["width"], spec["length"], skirt],
            at=(0.0, 0.0, foot + gap),
        )
        from pyboxbuilder.rounding import mating_rounding, rounded_block, vertical_edges

        # Matched to the body's corners so the sleeve nests over them.
        cavity = rounded_block(
            [
                spec["width"] - 2 * inset + 2 * slack,
                spec["length"] - 2 * inset + 2 * slack,
                skirt - lt,
            ],
            mating_rounding(spec),
            vertical_edges(),
            at=(inset - slack, inset - slack, foot + gap),
        )
        sleeve = outer - cavity
        return sleeve - self._finger_notches(spec)

    def _finger_notches(self, spec: dict) -> "Bosl2Solid":
        """Corner notches so the sleeve can be pulled off.

        A slipover sleeve is a smooth box with nothing to grip: it covers the
        body on four sides and its own faces are flush, so there is nowhere to
        get a fingertip. The original cuts a notch into two **diagonally
        opposite** corners — diagonal so the two hands pull along the sleeve's
        axis rather than twisting it — sized at half the skirt's height and
        placed just under the lid plate, where the notch exposes the body's
        corner and a thumb can push it out.

        Args:
            spec: Box dimensions; reads `wall_thickness`, `lid_thickness`,
                `foot` and `slipover_finger_height`.

        Returns:
            The solid to subtract from the sleeve.
        """
        from pyboxbuilder.box.features import corner_catch
        from pyboxbuilder.compartments.element import union_all

        wt = spec.get("wall_thickness", 2.0)
        lt = spec.get("lid_thickness", 2.0)
        foot = spec.get("foot", 0.0)

        skirt = spec["height"] - foot - lt
        # The original's sizing: half the skirt, capped, and a radius that stays
        # usable on a shallow box.
        # An explicit None check, not `or`: `slipover_finger_height=0` means
        # "no notch", and `or` reads zero as "unset" and hands back the default.
        requested = spec.get("slipover_finger_height")
        height = (
            min(SLIPOVER_FINGER_MAX_MM, skirt / 2) if requested is None
            else float(requested)
        )
        height = max(0.0, min(height, skirt))
        if height <= 0:
            return None
        radius = max(height, SLIPOVER_FINGER_MIN_RADIUS_MM)

        top = spec["height"] - lt
        notches = [
            corner_catch(
                (0.0, 0.0), (1, 1), radius=radius, height=height,
                wall_thickness=wt, rounding_edge=wt / 4,
            ),
            corner_catch(
                (spec["width"], spec["length"]), (-1, -1), radius=radius,
                height=height, wall_thickness=wt, rounding_edge=wt / 4,
            ),
        ]
        return union_all([n.translate([0.0, 0.0, top - height]) for n in notches])
