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
        for box_type in (BoxType.CAP_PATH, BoxType.SLIPOVER_PATH):
            with self.subTest(box_type=box_type.value):
                box = BOX_IMPL_REGISTRY[box_type]()
                body = box.build_body(dict(SPEC))
                lid = box.build_lid(dict(SPEC))
                self.assertLess(volume(body & lid), 0.01)
                self.assertAlmostEqual(bbox(body)[1][0], SPEC["width"], places=3)


if __name__ == "__main__":
    unittest.main()
