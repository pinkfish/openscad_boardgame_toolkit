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
    groove_depth,
    rabbet,
    sliding_catch,
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

    def test_only_a_hinge_reaches_outside_its_footprint(self) -> None:
        """Everything else must fit the declared footprint exactly."""
        keep = self.footprint()
        for box_type in BoxType:
            with self.subTest(box_type=box_type.value):
                outside = sum(volume(p - keep) for p in self.parts(box_type))
                if box_type in self.HINGED:
                    self.assertGreater(outside, 1.0, "no barrel at all?")
                else:
                    self.assertLess(
                        outside, 0.01,
                        f"{box_type.value} has {outside:.1f}mm3 of material "
                        f"outside the size it declared",
                    )

    def test_a_hinge_barrel_protrudes_backwards_and_not_far(self) -> None:
        for box_type in self.HINGED:
            with self.subTest(box_type=box_type.value):
                (x0, x1), (y0, y1), _ = self.extent(self.parts(box_type))
                self.assertAlmostEqual(x0, 0.0, places=2)
                self.assertAlmostEqual(x1, SPEC["width"], places=2)
                self.assertAlmostEqual(y0, 0.0, places=2)
                self.assertGreater(y1, SPEC["length"], "no barrel at all?")
                self.assertLess(
                    y1, SPEC["length"] + 10.0,
                    "the barrel is standing much too far off the back",
                )

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
    def test_a_groove_never_cuts_through_the_wall(self) -> None:
        for wall in (1.0, 1.5, 2.0, 3.0, 6.0):
            spec = {**SPEC, "wall_thickness": wall}
            self.assertLess(groove_depth(spec), wall, f"wall={wall}")

    def test_the_lid_reaches_into_both_grooves(self) -> None:
        closure = sliding_track(SPEC)
        (_, lid_y, _), (_, lid_l, _) = bbox(closure.lid)
        interior_l = SPEC["length"] - 2 * SPEC["wall_thickness"]
        self.assertGreater(lid_l, interior_l, "lid must overlap the grooves")
        self.assertLess(lid_l, interior_l + 2 * groove_depth(SPEC))

    def test_the_catch_dimple_is_larger_than_its_bump(self) -> None:
        """They should click together, not jam."""
        closure = sliding_catch(SPEC, radius=1.0)
        (_, _, _), dimple = bbox(closure.body)
        (_, _, _), bump = bbox(closure.lid)
        self.assertGreater(dimple[2], bump[2])


class FilamentHingeTests(unittest.TestCase):
    def test_the_two_leaves_do_not_touch(self) -> None:
        closure = filament_hinge(SPEC)
        self.assertIsNotNone(closure.body)
        self.assertIsNotNone(closure.lid)
        self.assertLess(volume(closure.body & closure.lid), 0.01)

    def test_the_pin_axis_is_clear_of_the_back_wall(self) -> None:
        """A pin sunk into the wall buries the lid's knuckles in the body."""
        closure = filament_hinge(SPEC)
        (_, knuckle_y, _), (_, _, _) = bbox(closure.lid)
        self.assertGreaterEqual(knuckle_y, SPEC["length"] - 1.0)

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
        """A plain plate cannot hinge; the lid must reach past the back wall."""
        _, lid = self.hinge_parts()
        (_, lid_y, _), (_, lid_l, _) = bbox(lid)
        self.assertGreater(
            lid_y + lid_l, SPEC["length"] + 1.0,
            "the lid has no knuckles behind the box",
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
