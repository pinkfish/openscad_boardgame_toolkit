# SPDX-License-Identifier: Apache-2.0
"""Tests that every box type's lid actually mates with its body (T162).

The property worth asserting is that a closed lid and its body occupy no common
volume. A lid that overlaps its box is not a lid — it fuses to it, or it simply
will not close. Facet counts and bounding boxes both miss that; measured
intersection volume does not.
"""

from __future__ import annotations

import os
import re
import tempfile
import unittest
import zipfile

from pyboxbuilder.box.features import (
    FIT_SLACK_MM,
    filament_hinge,
    lead_chamfer_size,
    rabbet,
    sliding_catch,
    sliding_dovetail,
    sliding_track,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, LIDLESS_BOX_TYPES
from pyboxbuilder.enums import BoxType

SPEC = {
    "width": 100.0, "length": 80.0, "height": 40.0,
    "wall_thickness": 2.0, "floor_thickness": 2.0, "lid_thickness": 2.0,
}


def volume(solid) -> float:
    """Mesh volume via a round trip through the 3MF exporter."""
    from openscad import export  # type: ignore[import-not-found]

    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(solid.shape, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)

    verts = [
        (float(x), float(y), float(z))
        for x, y, z in re.findall(
            r'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"', model
        )
    ]
    total = 0.0
    for a, b, c in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (
            p[0] * (q[1] * r[2] - r[1] * q[2])
            - p[1] * (q[0] * r[2] - r[0] * q[2])
            + p[2] * (q[0] * r[1] - r[0] * q[1])
        ) / 6.0
    return abs(total)


def bbox(solid):
    centre, size = solid.bounds()
    return (tuple(c - s / 2 for c, s in zip(centre, size)), tuple(size))


class MatingTests(unittest.TestCase):
    """Every lidded type: the closed lid must not occupy the body's material."""

    def test_no_lid_overlaps_its_body(self) -> None:
        for box_type in BoxType:
            if box_type in LIDLESS_BOX_TYPES:
                continue
            with self.subTest(box_type=box_type.value):
                box = BOX_IMPL_REGISTRY[box_type]()
                body = box.build_body(dict(SPEC))
                lid = box.build_lid(dict(SPEC))
                self.assertIsNotNone(lid, f"{box_type.value} has no lid")
                self.assertLess(
                    volume(body & lid), 0.01,
                    f"{box_type.value}'s lid intersects its body",
                )

    def test_every_lid_has_real_volume(self) -> None:
        """A type that forgot its lid would return an empty or paper-thin solid."""
        for box_type in BoxType:
            if box_type in LIDLESS_BOX_TYPES:
                continue
            with self.subTest(box_type=box_type.value):
                lid = BOX_IMPL_REGISTRY[box_type]().build_lid(dict(SPEC))
                self.assertGreater(volume(lid), 1000.0, box_type.value)

    def test_lidless_types_return_no_lid(self) -> None:
        for box_type in LIDLESS_BOX_TYPES:
            self.assertIsNone(BOX_IMPL_REGISTRY[box_type]().build_lid(dict(SPEC)))


class DeclaredSizeTests(unittest.TestCase):
    """A closed box must be exactly the size it was asked for.

    The declared size is the outside of the box with its lid on — that is the
    space the packer reserves for it. A lid that hangs off the outside of a
    full-size body makes the box bigger than planned, and every layout built on
    it wrong. Emberleaf showed what that costs: each cap-lid player box declared
    98 x 142.5 x 13.125 actually measured 104.4 x 148.9 x 15.125, so five of
    them needed 75.6mm of a 52.5mm column and were 6mm too wide for it.
    """

    HINGED = {BoxType.HINGE, BoxType.FILAMENT_HINGE}
    """A hinge barrel legitimately stands proud BEHIND the box, as a real hinge
    does. That is outside the footprint, so it does not affect what the box
    needs on the shelf — but it is the only thing allowed out there."""

    def parts(self, box_type: BoxType):
        box = BOX_IMPL_REGISTRY[box_type]()
        out = [box.build_body(dict(SPEC))]
        if box_type not in LIDLESS_BOX_TYPES:
            out.append(box.build_lid(dict(SPEC)))
        return [p for p in out if p is not None]

    @staticmethod
    def extent(solids):
        boxes = [bbox(s) for s in solids]
        return [
            (min(b[0][i] for b in boxes), max(b[0][i] + b[1][i] for b in boxes))
            for i in range(3)
        ]

    def footprint(self):
        """The declared footprint, running well above and below the box."""
        from pyboxbuilder.box.shell import block

        return block(
            [SPEC["width"], SPEC["length"], SPEC["height"] * 4],
            at=(0.0, 0.0, -SPEC["height"]),
        )

    def test_a_closed_box_is_the_size_it_was_asked_for(self) -> None:
        """Measured over the declared footprint, which is what packing reserves."""
        want = (SPEC["width"], SPEC["length"], SPEC["height"])
        axis_name = ("width", "length", "height")
        keep = self.footprint()
        for box_type in BoxType:
            extent = self.extent([p & keep for p in self.parts(box_type)])
            for axis in range(3):
                with self.subTest(box_type=box_type.value, axis=axis_name[axis]):
                    low, high = extent[axis]
                    self.assertAlmostEqual(
                        low, 0.0, places=2,
                        msg=f"{box_type.value} starts before the origin",
                    )
                    self.assertAlmostEqual(
                        high - low, want[axis], places=2,
                        msg=f"{box_type.value} is {high - low:.2f}mm across, "
                            f"not the {want[axis]:.2f}mm it declared",
                    )

    def test_nothing_reaches_outside_its_footprint(self) -> None:
        """Every type fits the declared footprint exactly — hinges included.

        A hinge barrel used to be the one allowed exception, standing off the
        back of the box. It now sits inside the outline instead, which is what
        lets a hinged box be packed against its neighbours like any other.
        """
        keep = self.footprint()
        for box_type in BoxType:
            with self.subTest(box_type=box_type.value):
                outside = sum(volume(p - keep) for p in self.parts(box_type))
                self.assertLess(
                    outside, 0.01,
                    f"{box_type.value} has {outside:.1f}mm3 of material "
                    f"outside the size it declared",
                )

    def test_a_hinged_box_keeps_its_declared_envelope(self) -> None:
        for box_type in self.HINGED:
            with self.subTest(box_type=box_type.value):
                (x0, x1), (y0, y1), (z0, z1) = self.extent(self.parts(box_type))
                self.assertAlmostEqual(x0, 0.0, places=2)
                self.assertAlmostEqual(x1, SPEC["width"], places=2)
                self.assertAlmostEqual(y0, 0.0, places=2)
                self.assertAlmostEqual(y1, SPEC["length"], places=2)
                self.assertAlmostEqual(z0, 0.0, places=2)
                self.assertAlmostEqual(z1, SPEC["height"], places=2)

    def test_the_cap_body_leaves_room_for_its_lid(self) -> None:
        """The body stops short and steps in; the lid fills back out to size."""
        box = BOX_IMPL_REGISTRY[BoxType.CAP]()
        (_, _, _), (body_w, _, body_h) = bbox(box.build_body(dict(SPEC)))
        self.assertLess(body_h, SPEC["height"])
        self.assertAlmostEqual(body_w, SPEC["width"], places=2)  # full at the base

        (_, _, lid_z), (lid_w, _, _) = bbox(box.build_lid(dict(SPEC)))
        self.assertAlmostEqual(lid_w, SPEC["width"], places=2)
        self.assertLess(lid_z, body_h, "the skirt must reach down over the body")

    def test_the_slipover_body_sits_inside_its_sleeve(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.SLIPOVER]()
        (bx, by, _), (body_w, body_l, body_h) = bbox(box.build_body(dict(SPEC)))
        self.assertGreater(bx, 0.0)
        self.assertGreater(by, 0.0)
        self.assertLess(body_w, SPEC["width"])
        self.assertLess(body_l, SPEC["length"])
        self.assertLess(body_h, SPEC["height"])

        (_, _, _), (lid_w, lid_l, _) = bbox(box.build_lid(dict(SPEC)))
        self.assertAlmostEqual(lid_w, SPEC["width"], places=2)
        self.assertAlmostEqual(lid_l, SPEC["length"], places=2)


class RabbetTests(unittest.TestCase):
    def test_the_lid_drops_into_the_ledge(self) -> None:
        closure = rabbet(SPEC, inset=1.0)
        (_, _, recess_z), (recess_w, recess_l, _) = bbox(closure.body)
        (_, _, lid_z), (lid_w, lid_l, lid_h) = bbox(closure.lid)

        self.assertAlmostEqual(lid_w, recess_w - 2 * FIT_SLACK_MM, places=3)
        self.assertAlmostEqual(lid_l, recess_l - 2 * FIT_SLACK_MM, places=3)
        self.assertAlmostEqual(lid_z, recess_z, places=3)

    def test_the_lid_finishes_flush_with_the_rim(self) -> None:
        """An inset lid standing proud would stop the box stacking."""
        closure = rabbet(SPEC)
        (_, _, z), (_, _, h) = bbox(closure.lid)
        self.assertAlmostEqual(z + h, SPEC["height"], places=3)

    def test_the_ledge_leaves_wall_behind_it(self) -> None:
        closure = rabbet(SPEC, inset=1.0)
        (_, _, _), (recess_w, _, _) = bbox(closure.body)
        self.assertLess(recess_w, SPEC["width"])
        self.assertGreater(recess_w, SPEC["width"] - 2 * SPEC["wall_thickness"])


class SlidingTests(unittest.TestCase):
    def test_the_dovetail_is_interior_over_half_wall(self) -> None:
        """FR-002c: no key at the top (interior), half the wall at the bottom."""
        for wall in (1.0, 1.5, 2.0, 3.0, 6.0):
            with self.subTest(wall=wall):
                top, bottom = sliding_dovetail({**SPEC, "wall_thickness": wall})
                self.assertEqual(top, 0.0)
                self.assertEqual(bottom, wall / 2)

    def test_the_lead_chamfer_is_a_quarter_of_the_lid_thickness(self) -> None:
        """FR-002d: the chamfer is *slight*, and overridable.

        It was half the thickness, which takes a 2mm lid's leading end down to
        a 1mm knife edge — a taper big enough to read as the wedge a sliding
        lid should not have anywhere.
        """
        self.assertEqual(lead_chamfer_size(SPEC), SPEC["lid_thickness"] / 4)
        self.assertEqual(
            lead_chamfer_size({**SPEC, "lead_chamfer": 0.5}), 0.5
        )

    def test_the_lid_flares_from_interior_to_half_wall(self) -> None:
        """The top face is the interior; the underside reaches half a wall into each side."""
        from pyboxbuilder.box.shell import block

        lid = sliding_track(SPEC).lid
        wt = SPEC["wall_thickness"]
        interior = SPEC["length"] - 2 * wt
        (_, _, _), (_, bottom_w, _) = bbox(lid)  # widest face is the underside
        top = lid & block(
            [SPEC["width"], SPEC["length"], 0.01], at=(0, 0, SPEC["height"] - 0.01)
        )
        (_, _, _), (_, top_w, _) = bbox(top)
        self.assertAlmostEqual(top_w, interior - FIT_SLACK_MM, delta=0.05)
        self.assertAlmostEqual(bottom_w - top_w, wt, delta=0.05)

    def test_the_leading_end_is_chamfered(self) -> None:
        """FR-002d: the chamfer removes material from the lid's leading bottom edge."""
        lid = sliding_track(SPEC).lid
        plain = sliding_track({**SPEC, "lead_chamfer": 0.0}).lid
        self.assertLess(volume(lid), volume(plain), "the chamfer must remove material")

    def test_the_groove_keeps_wall_behind_it(self) -> None:
        """The groove never reaches the outer face — half the wall stays as support."""
        from pyboxbuilder.box.shell import block

        channel = sliding_track(SPEC).body
        wt = SPEC["wall_thickness"]
        (_, _, _), (_, floor_w, _) = bbox(channel)
        opening = channel & block(
            [SPEC["width"], SPEC["length"], 0.01], at=(0, 0, SPEC["height"] - 0.01)
        )
        (_, _, _), (_, opening_w, _) = bbox(opening)
        # Floor is half a wall in from each side; opening is the interior.
        self.assertAlmostEqual(floor_w, SPEC["length"] - wt + 0.1, places=2)
        self.assertAlmostEqual(opening_w, SPEC["length"] - 2 * wt, delta=0.3)
        self.assertLess(opening_w, floor_w)

    def test_the_back_is_dovetailed_like_the_sides(self) -> None:
        """FR-002e: the stop wall keeps full thickness at the channel opening
        and half of it at the channel floor, so the lid's leading end has a seat
        to rest in rather than a flat face to lean on."""
        from pyboxbuilder.box.shell import block

        channel = sliding_track(SPEC).body
        wt = SPEC["wall_thickness"]
        lt = SPEC["lid_thickness"]
        top = channel & block(
            [SPEC["width"], SPEC["length"], 0.01], at=(0, 0, SPEC["height"] - 0.01)
        )
        bottom = channel & block(
            [SPEC["width"], SPEC["length"], 0.01], at=(0, 0, SPEC["height"] - lt)
        )
        (top_x, _, _), _ = bbox(top)
        (bottom_x, _, _), _ = bbox(bottom)
        self.assertAlmostEqual(top_x - bottom_x, wt / 2, delta=0.1)
        self.assertGreater(bottom_x, 0.0, "the floor must leave wall behind it")

    def test_the_lid_seats_in_the_back_groove(self) -> None:
        """The lid's leading end reaches under the stop wall, not up against it."""
        (x, _, _), _ = bbox(sliding_track(SPEC).lid)
        self.assertLess(
            x, SPEC["wall_thickness"], "the lid must reach into the back seat"
        )

    def test_the_lid_slides_out_without_interference(self) -> None:
        """The back seat is a seat, **not a wedge** — nothing has to be forced.

        A matched taper and a wedge catch look alike in a render and differ
        entirely in the hand, so the assertion is the travel itself: at every
        point along the slide the lid and the body share no volume. A wedge
        would show up as interference partway out, where the lid's leading lip
        has to deform past the stop wall's overhang.
        """
        from pyboxbuilder.box.types.sliding import SlidingBox

        box = SlidingBox()
        spec = {**SPEC, "hollow": True}
        body = box.build_body(spec)
        lid = box.build_lid(spec)
        for step in (0.0, 1.0, 5.0, 25.0, 60.0, SPEC["width"]):
            with self.subTest(slid=step):
                self.assertLess(
                    volume(body & lid.translate([step, 0, 0])), 0.01,
                    "the lid must slide out freely, deforming nothing",
                )

    def test_the_seated_lid_cannot_be_lifted_out(self) -> None:
        """The seat's other half: the closed lid is trapped vertically at the back."""
        from pyboxbuilder.box.types.sliding import SlidingBox

        box = SlidingBox()
        spec = {**SPEC, "hollow": True}
        body = box.build_body(spec)
        lid = box.build_lid(spec)
        self.assertGreater(
            volume(body & lid.translate([0, 0, 0.5])), 1.0,
            "lifting the lid must drive it into the wall within half a mm",
        )

    def test_the_lid_corners_are_rounded(self) -> None:
        """FR-002e4: rounded so they do not snag on the groove mouths."""
        rounded = sliding_track(SPEC).lid
        square = sliding_track({**SPEC, "lid_corner_rounding": 0.0}).lid
        self.assertLess(
            volume(rounded), volume(square), "the rounding must remove material"
        )

    def test_the_leading_edges_are_chamfered_top_and_bottom(self) -> None:
        """Both horizontal edges of the leading end, so it eases in either way.

        Measured against the same lid with the chamfer switched off, because
        the two chamfers land close to the seat's own taper — comparing heights
        within one lid cannot tell a chamfer from the slope it sits on.
        """
        from pyboxbuilder.box.shell import block

        lid = sliding_track(SPEC).lid
        square = sliding_track({**SPEC, "lead_chamfer": 0.0}).lid
        lt = SPEC["lid_thickness"]

        def lead_at(solid, z: float) -> float:
            slab = solid & block(
                [SPEC["width"], SPEC["length"], 0.01], at=(0, 0, z)
            )
            return bbox(slab)[0][0]

        for name, z in (
            ("underside", SPEC["height"] - lt + 0.005),
            ("top face", SPEC["height"] - 0.015),
        ):
            with self.subTest(edge=name):
                self.assertGreater(
                    lead_at(lid, z), lead_at(square, z) + 0.1,
                    f"the {name} leading edge must be chamfered back",
                )

    def test_the_sliding_clearance_is_configurable(self) -> None:
        """`sliding_slack` widens the gap between the lid and the groove."""
        default = sliding_track(SPEC).lid
        roomy = sliding_track({**SPEC, "sliding_slack": 0.5}).lid
        (_, _, _), (_, default_w, _) = bbox(default)
        (_, _, _), (_, roomy_w, _) = bbox(roomy)
        self.assertAlmostEqual(
            default_w, SPEC["length"] - SPEC["wall_thickness"] - 0.2, places=2
        )
        self.assertAlmostEqual(
            roomy_w, SPEC["length"] - SPEC["wall_thickness"] - 1.0, places=2
        )
        self.assertLess(roomy_w, default_w)

    def test_the_catch_dimple_is_larger_than_its_bump(self) -> None:
        """They should click together, not jam."""
        closure = sliding_catch(SPEC, radius=1.0)
        (_, _, _), dimple = bbox(closure.body)
        (_, _, _), bump = bbox(closure.lid)
        self.assertGreater(dimple[2], bump[2])


class SlidingBumpCatchTests(unittest.TestCase):
    """FR-002e1–e3: a sliding lid's catch is a bump at the outlet, not a wedge."""

    def test_the_catch_sits_at_the_outlet_not_the_stop(self) -> None:
        """SC-049: dragging the bump the length of the groove wears it out."""
        radius = 1.0
        outlet = SPEC["width"]  # along_axis "x" leaves through +X
        for name, solid in (
            ("dimple", sliding_catch(SPEC, radius, "x").body),
            ("bump", sliding_catch(SPEC, radius, "x").lid),
        ):
            with self.subTest(part=name):
                (x0, _, _), (dx, _, _) = bbox(solid)
                centre = x0 + dx / 2
                self.assertLess(
                    outlet - centre,
                    SPEC["wall_thickness"] + 2 * radius + 0.01,
                    "the catch must engage in the last few mm of travel",
                )

    def test_the_catch_follows_the_slide_axis(self) -> None:
        """It was hardcoded to X, so a box sliding along Y got it on the wrong walls."""
        along_y = sliding_catch(SPEC, 1.0, "y").body
        (_, y0, _), (_, dy, _) = bbox(along_y)
        self.assertLess(
            SPEC["length"] - (y0 + dy / 2),
            SPEC["wall_thickness"] + 2.0 + 0.01,
            "sliding along Y must put the catch near the +Y outlet",
        )

    def test_the_bump_straddles_the_lid_flank(self) -> None:
        """Half in the lid, half proud of it — which is what makes it a detent.

        It was centred on the *wall's* inner face, but the dovetail flank has
        already leaned inward by mid-thickness, so the sphere sat 0.4mm outside
        the lid: too little of it attached, too much of it hanging in the gap.
        """
        lid = sliding_track(SPEC).lid
        bumps = sliding_catch(SPEC, 1.0, "x").lid
        inside = volume(lid & bumps) / volume(bumps)
        self.assertGreater(inside, 0.35, "the bump must be solidly on the lid")
        self.assertLess(inside, 0.65, "the bump must stand proud enough to catch")

    def test_a_plain_sliding_box_has_no_catch(self) -> None:
        """FR-002e3: SLIDING and SLIDING_CATCH must not be the same type."""
        from pyboxbuilder.box.types.sliding import SlidingBox

        box = SlidingBox()
        spec = {**SPEC, "hollow": True}
        self.assertAlmostEqual(
            volume(box.build_lid(spec)),
            volume(box.build_lid({**spec, "catch_radius": 0.0})),
            delta=0.01,
        )

    def test_asking_a_sliding_box_for_a_catch_adds_one(self) -> None:
        from pyboxbuilder.box.types.sliding import SlidingBox

        box = SlidingBox()
        spec = {**SPEC, "hollow": True}
        plain = volume(box.build_lid(spec))
        caught = volume(box.build_lid({**spec, "catch_radius": 1.0}))
        self.assertGreater(caught, plain, "the bumps must add material to the lid")
        self.assertLess(
            volume(box.build_body({**spec, "catch_radius": 1.0})),
            volume(box.build_body(spec)),
            "the dimples must take material out of the body",
        )


class FilamentHingeTests(unittest.TestCase):
    def test_the_two_leaves_do_not_touch(self) -> None:
        closure = filament_hinge(SPEC)
        self.assertIsNotNone(closure.body)
        self.assertIsNotNone(closure.lid)
        self.assertLess(volume(closure.body & closure.lid), 0.01)

    def test_the_pin_axis_sits_inside_the_back_wall(self) -> None:
        """The hinge lives in the box, not behind it.

        Keeping it inside is what costs interior room, and is why a hinge box
        carves that volume out of its contents mask: the alternative is a
        barrel a packer has to reserve space for outside the box.
        """
        closure = filament_hinge(SPEC)
        (_, knuckle_y, _), (_, knuckle_length, _) = bbox(closure.lid)
        self.assertLessEqual(
            knuckle_y + knuckle_length, SPEC["length"] + 0.01,
            "the hinge is standing outside the box",
        )
        self.assertGreater(
            knuckle_y, SPEC["length"] * 0.5,
            "the hinge should be at the back, not adrift in the middle",
        )

    def test_both_leaves_share_one_pin_axis(self) -> None:
        closure = filament_hinge(SPEC)
        (_, body_y, body_z), (_, _, body_h) = bbox(closure.body)
        (_, lid_y, lid_z), (_, _, lid_h) = bbox(closure.lid)
        # Same barrel: the leaves span the same Y band around the pin.
        self.assertAlmostEqual(body_y, lid_y, places=1)

    def test_more_knuckles_alternate_between_the_leaves(self) -> None:
        for count in (3, 5, 9):
            closure = filament_hinge(SPEC, knuckles=count)
            with self.subTest(knuckles=count):
                self.assertIsNotNone(closure.body)
                self.assertIsNotNone(closure.lid)
                self.assertLess(volume(closure.body & closure.lid), 0.01)

    def test_the_body_stops_short_so_the_lid_closes_onto_it(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.FILAMENT_HINGE]()
        body = box.build_body(dict(SPEC))
        lid = box.build_lid(dict(SPEC))
        (_, _, _), (_, _, body_h) = bbox(body)
        (_, _, lid_z), (_, _, lid_h) = bbox(lid)
        # Closed, the pair comes to the box's stated height.
        self.assertAlmostEqual(lid_z + lid_h, SPEC["height"], places=3)


class HingeArticulationTests(unittest.TestCase):
    """T163 — the hinge needs knuckles on *both* halves to turn."""

    def hinge_parts(self):
        box = BOX_IMPL_REGISTRY[BoxType.HINGE]()
        return box.build_body(dict(SPEC)), box.build_lid(dict(SPEC))

    def test_the_lid_carries_knuckles_too(self) -> None:
        """A plain plate cannot hinge, so the lid must reach down to the pin.

        Measured by depth rather than by overhang now that the hinge is inside
        the box: a bare plate would start at the joint and go up, while a lid
        with knuckles reaches below it to meet the axis.
        """
        _, lid = self.hinge_parts()
        (_, _, lid_z), (_, _, lid_h) = bbox(lid)
        joint = SPEC["height"] - SPEC["lid_thickness"]
        self.assertLess(
            lid_z, joint - 0.5,
            "the lid has no knuckles reaching down to the pin",
        )

    def test_both_halves_reach_the_same_pin_axis(self) -> None:
        body, lid = self.hinge_parts()
        (_, body_y, _), (_, body_l, _) = bbox(body)
        (_, lid_y, _), (_, lid_l, _) = bbox(lid)
        self.assertAlmostEqual(body_y + body_l, lid_y + lid_l, places=1)

    def test_the_halves_are_separate_parts(self) -> None:
        body, lid = self.hinge_parts()
        self.assertLess(volume(body & lid), 0.01)

    def test_the_closed_pair_comes_to_the_stated_height(self) -> None:
        """Measured over the box's own footprint.

        The hinge barrel is allowed to stand proud behind the back wall — real
        hinges do — so the whole lid's bounding box is the wrong thing to check.
        What must be flush is the part of the lid that sits over the box.
        """
        from pyboxbuilder.box.shell import block

        _, lid = self.hinge_parts()
        over_box = lid & block(
            [SPEC["width"], SPEC["length"], SPEC["height"] * 3],
            at=(0.0, 0.0, -SPEC["height"]),
        )
        (_, _, z), (_, _, h) = bbox(over_box)
        self.assertAlmostEqual(z + h, SPEC["height"], places=3)

    def test_the_barrel_stays_behind_the_box(self) -> None:
        """Whatever protrudes must protrude backwards, not sideways or forwards."""
        body, lid = self.hinge_parts()
        for part in (body, lid):
            (x, y, _), (w, l, _) = bbox(part)
            self.assertGreaterEqual(round(x, 3), 0.0)
            self.assertLessEqual(round(x + w, 3), SPEC["width"])
            self.assertGreaterEqual(round(y, 3), 0.0)


class PathClosureTests(unittest.TestCase):
    L_SHAPE = ((0.0, 0.0), (100.0, 0.0), (100.0, 40.0), (40.0, 40.0),
               (40.0, 80.0), (0.0, 80.0))

    def spec(self) -> dict:
        return {**SPEC, "path": self.L_SHAPE}

    def test_a_cap_path_lid_follows_the_polygon(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.CAP_PATH]()
        body = box.build_body(self.spec())
        lid = box.build_lid(self.spec())
        self.assertLess(volume(body & lid), 0.01)
        # The cap wraps the body, so its footprint is larger.
        self.assertGreater(bbox(lid)[1][0], bbox(body)[1][0])

    def test_a_slipover_path_sleeve_follows_the_polygon(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.SLIPOVER_PATH]()
        body = box.build_body(self.spec())
        lid = box.build_lid(self.spec())
        self.assertLess(volume(body & lid), 0.01)
        self.assertGreater(bbox(lid)[1][0], bbox(body)[1][0])

    def test_a_path_body_is_hollow(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.CAP_PATH]()
        hollow = volume(box.build_body(self.spec()))
        solid = volume(box.build_body({**self.spec(), "hollow": False}))
        self.assertLess(hollow, solid)

    def test_no_path_falls_back_to_the_rectangular_closure(self) -> None:
        """With no path these behave exactly like their rectangular twins —
        including putting the declared size on the *closed* box, so the body is
        inset or stepped in rather than being the full footprint itself."""
        for box_type, plain in (
            (BoxType.CAP_PATH, BoxType.CAP),
            (BoxType.SLIPOVER_PATH, BoxType.SLIPOVER),
        ):
            with self.subTest(box_type=box_type.value):
                box = BOX_IMPL_REGISTRY[box_type]()
                body = box.build_body(dict(SPEC))
                lid = box.build_lid(dict(SPEC))
                self.assertLess(volume(body & lid), 0.01)

                twin = BOX_IMPL_REGISTRY[plain]()
                self.assertEqual(bbox(body), bbox(twin.build_body(dict(SPEC))))
                self.assertEqual(bbox(lid), bbox(twin.build_lid(dict(SPEC))))


if __name__ == "__main__":
    unittest.main()


class HingeInsideTests(unittest.TestCase):
    """FR-002c/d/e: the hinge lives in the box, and the interior knows it."""

    HINGED = (BoxType.HINGE, BoxType.FILAMENT_HINGE)

    def parts(self, box_type):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        impl = BOX_IMPL_REGISTRY[box_type]()
        return impl.build_body(dict(SPEC)), impl.build_lid(dict(SPEC))

    def test_the_closed_box_is_its_declared_size_in_every_axis(self) -> None:
        for box_type in self.HINGED:
            with self.subTest(box_type=box_type.value):
                body, lid = self.parts(box_type)
                low, size = bbox(body | lid)
                for axis, name in enumerate(("width", "length", "height")):
                    self.assertAlmostEqual(low[axis], 0.0, places=2)
                    self.assertAlmostEqual(size[axis], SPEC[name], places=2)

    def test_the_two_halves_are_still_separate(self) -> None:
        """Relieving one side only looks fixed and is not: the obvious symptom
        goes away while the other half stays welded."""
        for box_type in self.HINGED:
            with self.subTest(box_type=box_type.value):
                body, lid = self.parts(box_type)
                self.assertLess(volume(body & lid), 0.01)

    def test_both_reliefs_exist(self) -> None:
        from pyboxbuilder.box.features import filament_hinge

        closure = filament_hinge(SPEC)
        self.assertIsNotNone(closure.body_cut, "the body gives up nothing")
        self.assertIsNotNone(closure.lid_cut, "the lid gives up nothing")

    def test_the_interior_mask_carves_out_the_hinge(self) -> None:
        from pyboxbuilder.box.base import interior_mask
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.shell import block

        wt, ft = SPEC["wall_thickness"], SPEC["floor_thickness"]
        whole = block(
            [SPEC["width"] - 2 * wt, SPEC["length"] - 2 * wt, SPEC["height"]],
            at=(wt, wt, ft),
        )
        for box_type in self.HINGED:
            with self.subTest(box_type=box_type.value):
                mask = interior_mask(BOX_IMPL_REGISTRY[box_type](), dict(SPEC))
                self.assertIsNotNone(mask, "a hinge box must mask its interior")
                self.assertLess(
                    volume(mask), volume(whole),
                    "the mask kept the whole interior, hinge and all",
                )

    def test_types_without_something_in_the_way_mask_nothing(self) -> None:
        from pyboxbuilder.box.base import interior_mask
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        for box_type in (BoxType.CAP, BoxType.SLIDING, BoxType.NO_LID):
            with self.subTest(box_type=box_type.value):
                self.assertIsNone(
                    interior_mask(BOX_IMPL_REGISTRY[box_type](), dict(SPEC))
                )

    def test_a_compartment_is_clipped_clear_of_the_hinge(self) -> None:
        from pyboxbuilder.box.base import interior_mask
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.interior import Interior
        from pyboxbuilder.compartments.carve import build_contents
        from pyboxbuilder.compartments.layout import CompartmentPlacement

        wt, ft = SPEC["wall_thickness"], SPEC["floor_thickness"]
        interior = Interior(
            width=SPEC["width"] - 2 * wt, length=SPEC["length"] - 2 * wt,
            height=SPEC["height"] - SPEC["lid_thickness"] - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )
        placement = CompartmentPlacement(
            "Big", (SPEC["width"] - 2 * wt, SPEC["length"] - 2 * wt), 20.0, (wt, wt)
        )
        impl = BOX_IMPL_REGISTRY[BoxType.HINGE]()
        mask = interior_mask(impl, dict(SPEC))

        unmasked = build_contents([placement], interior)
        masked = build_contents([placement], interior, mask=mask)
        self.assertLess(
            volume(masked), volume(unmasked),
            "the well was not clipped clear of the hinge",
        )


class SlipoverFingerNotchTests(unittest.TestCase):
    """FR-002f/g/h: a sleeve you can actually get off."""

    def sleeve(self, **overrides):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        spec = dict(SPEC)
        spec.update(overrides)
        return BOX_IMPL_REGISTRY[BoxType.SLIPOVER]().build_lid(spec)

    def test_the_notches_remove_material(self) -> None:
        plain = self.sleeve(slipover_finger_height=0.0)
        notched = self.sleeve()
        self.assertLess(
            volume(notched), volume(plain),
            "the sleeve has nothing to grip",
        )

    def test_they_do_not_change_the_declared_footprint(self) -> None:
        low, size = bbox(self.sleeve())
        self.assertAlmostEqual(size[0], SPEC["width"], places=2)
        self.assertAlmostEqual(size[1], SPEC["length"], places=2)
        self.assertAlmostEqual(low[0], 0.0, places=2)
        self.assertAlmostEqual(low[1], 0.0, places=2)

    def test_they_sit_at_diagonally_opposite_corners(self) -> None:
        """Diagonal so two fingers pull along the sleeve, not twist it."""
        from pyboxbuilder.box.shell import block

        plain = self.sleeve(slipover_finger_height=0.0)
        removed = plain - self.sleeve()

        half = 0.4  # a corner column, generously sized
        corners = {
            "near": (0.0, 0.0),
            "far": (SPEC["width"], SPEC["length"]),
            "left": (0.0, SPEC["length"]),
            "right": (SPEC["width"], 0.0),
        }
        for name, (x, y) in corners.items():
            column = block(
                [SPEC["width"] * half, SPEC["length"] * half, SPEC["height"] * 2],
                at=(x - SPEC["width"] * half / 2, y - SPEC["length"] * half / 2, -1),
            )
            taken = volume(removed & column)
            with self.subTest(corner=name):
                if name in ("near", "far"):
                    self.assertGreater(taken, 1.0, "no notch at this corner")
                else:
                    self.assertLess(taken, 0.01, "a notch where there should be none")

    def test_the_notch_is_below_the_lid_plate(self) -> None:
        plain = self.sleeve(slipover_finger_height=0.0)
        (_, _, z0), (_, _, dz) = bbox(plain - self.sleeve())
        self.assertLessEqual(
            z0 + dz, SPEC["height"] - SPEC["lid_thickness"] + 0.01,
            "the notch cut into the lid plate",
        )

    def test_a_shallow_sleeve_still_gets_a_usable_notch(self) -> None:
        from pyboxbuilder.box.types.slipover import SLIPOVER_FINGER_MIN_RADIUS_MM

        shallow = self.sleeve(height=12.0)
        plain = self.sleeve(height=12.0, slipover_finger_height=0.0)
        self.assertLess(volume(shallow), volume(plain))
        self.assertGreaterEqual(SLIPOVER_FINGER_MIN_RADIUS_MM, 5.0)

    def test_the_height_is_settable(self) -> None:
        small = self.sleeve(slipover_finger_height=3.0)
        large = self.sleeve(slipover_finger_height=12.0)
        self.assertGreater(volume(small), volume(large))


class CapFingerCutoutTests(unittest.TestCase):
    """FR-002i–FR-002n: a cap lid you can actually push off."""

    def body(self, **overrides):
        from pyboxbuilder.box.features import cap_body

        return cap_body({**SPEC, "hollow": True, **overrides})

    def metrics(self, **overrides):
        from pyboxbuilder.box.features import cap_finger_metrics

        return cap_finger_metrics({**SPEC, "hollow": True, **overrides})

    def probe(self, solid, x: float, y: float) -> float:
        """How much body material sits in a 3mm cube at mid-cut height."""
        from pyboxbuilder.box.shell import block

        f = self.metrics()
        z = f.base_z + f.height / 2
        return volume(solid & block([3, 3, 2], at=(x - 1.5, y - 1.5, z - 1)))

    def test_all_four_corners_are_cut_and_no_side_midpoint_is(self) -> None:
        """SC-051. The corners are where a finger loads both faces at once;
        the side midpoints are the bearing the skirt actually grips."""
        plain = self.body(cap_finger_cutouts=False)
        cut = self.body()
        w, l = SPEC["width"], SPEC["length"]
        for x, y in ((0.6, 5.0), (w - 0.6, 5.0), (0.6, l - 5.0), (w - 0.6, l - 5.0)):
            with self.subTest(corner=(x, y)):
                self.assertLess(
                    self.probe(cut, x, y), self.probe(plain, x, y) - 0.5,
                    "every corner must be cut",
                )
        for x, y in ((w / 2, 0.6), (w / 2, l - 0.6), (0.6, l / 2), (w - 0.6, l / 2)):
            with self.subTest(midpoint=(x, y)):
                self.assertAlmostEqual(
                    self.probe(cut, x, y), self.probe(plain, x, y), delta=0.01,
                    msg="the middle of each side must keep its bearing",
                )

    def test_the_run_along_each_side_is_bounded(self) -> None:
        """FR-002m: at least a fingertip, at most a sixth of the side."""
        from pyboxbuilder.box.features import (
            CAP_FINGER_MAX_LENGTH_SHARE, CAP_FINGER_MIN_LENGTH_MM,
        )

        f = self.metrics()
        for run, side in ((f.length_x, SPEC["width"]), (f.length_y, SPEC["length"])):
            with self.subTest(side=side):
                self.assertGreaterEqual(run, CAP_FINGER_MIN_LENGTH_MM)
                self.assertAlmostEqual(
                    run, side * CAP_FINGER_MAX_LENGTH_SHARE, delta=0.01
                )

    def test_a_short_side_gets_the_fingertip_minimum(self) -> None:
        """Where a sixth is under 10mm the minimum wins — 10mm is what a finger
        needs, a sixth is only what the skirt would prefer."""
        from pyboxbuilder.box.features import CAP_FINGER_MIN_LENGTH_MM

        f = self.metrics(width=42.0)
        self.assertEqual(f.length_x, CAP_FINGER_MIN_LENGTH_MM)

    def test_a_foot_of_body_survives_below_the_cut(self) -> None:
        """FR-002l: a recess in the side, not a through-slot."""
        from pyboxbuilder.box.features import CAP_FINGER_FOOT_MM

        f = self.metrics()
        self.assertGreaterEqual(
            f.base_z - SPEC["floor_thickness"], CAP_FINGER_FOOT_MM
        )

    def test_both_radii_meet_the_minimum(self) -> None:
        """FR-002k: below 4mm a fingertip catches on the edge instead of
        rolling into the cut."""
        from pyboxbuilder.box.features import CAP_FINGER_MIN_RADIUS_MM

        self.assertGreaterEqual(self.metrics().radius, CAP_FINGER_MIN_RADIUS_MM)
        # Asking for less does not get it.
        self.assertGreaterEqual(
            self.metrics(cap_finger_radius=0.5).radius, CAP_FINGER_MIN_RADIUS_MM
        )

    def test_a_box_too_short_raises_and_names_the_alternative(self) -> None:
        """SC-052/FR-002n: quietly shrinking the radii yields a cap box whose
        lid cannot be got off, which is worse than refusing to build it."""
        with self.assertRaises(ValueError) as caught:
            self.metrics(height=10.0)
        message = str(caught.exception)
        self.assertIn("slipover", message.lower())
        self.assertIn("mm", message)

    def test_the_minimum_height_is_lid_plus_skirt_plus_curves_plus_foot(self) -> None:
        """SC-052: the stack read down the box, and nothing more.

        The skirt is capped so it cannot swallow a short box: half the height
        would take 5.5mm of an 11mm box and leave the cut 5.5mm to fit 4mm of
        curve and a 2mm foot in, so the smallest cap box came out at 12mm
        rather than the 11mm the stack actually needs.
        """
        from pyboxbuilder.box.features import (
            CAP_FINGER_CURVE_TOTAL_MM, CAP_FINGER_FOOT_MM,
            CAP_FINGER_MIN_SKIRT_MM,
        )

        smallest = (
            SPEC["lid_thickness"] + CAP_FINGER_MIN_SKIRT_MM
            + CAP_FINGER_CURVE_TOTAL_MM + CAP_FINGER_FOOT_MM
        )
        self.metrics(height=smallest)  # must not raise
        with self.assertRaises(ValueError):
            self.metrics(height=smallest - 0.1)

    def test_a_tall_box_keeps_the_skirt_it_had(self) -> None:
        """The skirt cap only bites where it has to — a tall cap box is
        unchanged by any of this."""
        from pyboxbuilder.box.features import cap_metrics

        for height in (17.0, 40.0):
            with self.subTest(height=height):
                self.assertEqual(
                    cap_metrics({**SPEC, "height": height}).cap_height,
                    min(10.0, height / 2),
                )

    def test_the_cut_does_not_reach_the_lid(self) -> None:
        """The cutout is in the body, below the skirt — it must not open a gap
        through the closed box."""
        from pyboxbuilder.box.features import cap_lid

        self.assertLess(volume(self.body() & cap_lid(dict(SPEC))), 0.01)


class SlipoverSleeveTests(unittest.TestCase):
    """FR-002o/FR-002p: the sleeve is a skin over the body, not a second wall."""

    def parts(self, **overrides):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        spec = {**SPEC, "hollow": True, **overrides}
        box = BOX_IMPL_REGISTRY[BoxType.SLIPOVER]()
        return box.build_body(spec), box.build_lid(spec)

    def test_the_sleeve_wall_is_half_the_box_wall(self) -> None:
        """A full-thickness sleeve is a second wall carrying nothing — it cost
        the interior two full walls of width across every axis."""
        from pyboxbuilder.box.features import SLIPOVER_SLEEVE_WALL_SHARE, slipover_metrics

        inset, _ = slipover_metrics(SPEC)
        wiggle = SPEC.get("size_spacing", 0.2)
        self.assertAlmostEqual(
            inset - wiggle,
            SPEC["wall_thickness"] * SLIPOVER_SLEEVE_WALL_SHARE,
            places=6,
        )

    def test_the_sleeve_stops_short_of_the_foot(self) -> None:
        """FR-002p: a band of body shows all the way round to pull on, rather
        than the sleeve closing onto the foot in a seam with nothing to grip."""
        from pyboxbuilder.box.features import (
            SLIPOVER_GAP_MAX_MM, SLIPOVER_GAP_MIN_MM, slipover_gap,
        )

        gap = slipover_gap(SPEC)
        self.assertGreaterEqual(gap, SLIPOVER_GAP_MIN_MM)
        self.assertLessEqual(gap, SLIPOVER_GAP_MAX_MM)
        _, sleeve = self.parts()
        (_, _, z0), _ = bbox(sleeve)
        self.assertAlmostEqual(z0, SPEC.get("foot", 0.0) + gap, delta=0.02)

    def test_the_gap_is_bounded_both_ways(self) -> None:
        from pyboxbuilder.box.features import (
            SLIPOVER_GAP_MAX_MM, SLIPOVER_GAP_MIN_MM, slipover_gap,
        )

        self.assertEqual(slipover_gap({**SPEC, "height": 8.0}), SLIPOVER_GAP_MIN_MM)
        self.assertEqual(slipover_gap({**SPEC, "height": 200.0}), SLIPOVER_GAP_MAX_MM)

    def test_the_sleeve_still_does_not_overlap_its_body(self) -> None:
        body, sleeve = self.parts()
        self.assertLess(volume(body & sleeve), 0.01)


class CapCurveGrowthTests(unittest.TestCase):
    """FR-002k: 4mm is the floor, not the target."""

    def metrics(self, **overrides):
        from pyboxbuilder.box.features import cap_finger_metrics

        return cap_finger_metrics({**SPEC, "hollow": True, **overrides})

    def test_a_tall_box_gets_the_wider_curve(self) -> None:
        from pyboxbuilder.box.features import CAP_FINGER_CURVE_MAX_MM

        self.assertAlmostEqual(
            self.metrics().radius, CAP_FINGER_CURVE_MAX_MM / 2, places=6
        )

    def test_a_short_box_falls_back_to_the_floor(self) -> None:
        from pyboxbuilder.box.features import CAP_FINGER_MIN_RADIUS_MM

        self.assertAlmostEqual(
            self.metrics(height=11.0).radius, CAP_FINGER_MIN_RADIUS_MM, places=6
        )

    def test_growing_the_curve_does_not_raise_the_minimum(self) -> None:
        """The minimum is computed from the floor, so a box that fits 4mm of
        curve still builds even though a taller one would take 6mm."""
        self.metrics(height=11.0)  # must not raise
        with self.assertRaises(ValueError):
            self.metrics(height=10.9)
