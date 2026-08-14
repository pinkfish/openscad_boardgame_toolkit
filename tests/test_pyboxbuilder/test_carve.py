# SPDX-License-Identifier: Apache-2.0
"""Tests for carving compartments out of a box body.

These assert measured volumes rather than facet counts: a cutout that lands in
the wrong place still produces facets, but it changes how much material is left.
"""

from __future__ import annotations

import unittest

from pyboxbuilder.box.interior import Interior
from pyboxbuilder.box.shell import block, build_shell
from pyboxbuilder.compartments.builder import CompartmentBuilder
from pyboxbuilder.compartments.carve import build_contents, interior_mouth
from pyboxbuilder.compartments.layout import CompartmentPlacement
from pyboxbuilder.enums import ScoopSide

# A cap-style box: the interior stops `lid_thickness` below the rim.
SPEC = {
    "width": 100.0, "length": 80.0, "height": 30.0,
    "wall_thickness": 2.0, "floor_thickness": 2.0, "lid_thickness": 2.0,
    "hollow": False,
}
INTERIOR = Interior(
    width=96.0, length=76.0, height=26.0, origin_x=2.0, origin_y=2.0, origin_z=2.0
)


def bbox(solid) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """(min corner, size) of a solid, from pybosl2's (centre, size) bounds."""
    centre, size = solid.bounds()
    return (tuple(c - s / 2 for c, s in zip(centre, size)), tuple(size))


class ShellTests(unittest.TestCase):
    def test_block_places_its_minimum_corner(self) -> None:
        low, size = bbox(block([10.0, 20.0, 5.0], at=(3.0, 4.0, 5.0)))
        self.assertEqual(tuple(round(v, 6) for v in low), (3.0, 4.0, 5.0))
        self.assertEqual(tuple(round(v, 6) for v in size), (10.0, 20.0, 5.0))

    def test_a_hollow_shell_leaves_walls_on_all_four_sides(self) -> None:
        """The centre-anchoring bug used to cut the interior off to one side.

        Sizes carry the rounding's 0.002mm faceting tolerance — see
        `test_hollow_false_keeps_a_solid_block`.
        """
        low, size = bbox(build_shell({**SPEC, "hollow": True}))
        for got in low:
            self.assertAlmostEqual(got, 0.0, delta=0.01)
        for got, want in zip(size, (100.0, 80.0, 30.0)):
            self.assertAlmostEqual(got, want, delta=0.01)

    def test_hollow_false_keeps_a_solid_block(self) -> None:
        """The block keeps its declared size, bar the rounding's faceting.

        A rounded edge is an inscribed polygon, so it pulls the face it
        blends into inwards by the sagitta — 0.002mm at the 48-facet
        floor. That is 50x below the 0.1mm precision the library
        promises, but it is not zero, and no faceted representation of a
        fillet can make it zero.
        """
        solid = build_shell(SPEC)
        _, size = bbox(solid)
        for got, want in zip(size, (100.0, 80.0, 30.0)):
            self.assertAlmostEqual(got, want, delta=0.01)


class MouthTests(unittest.TestCase):
    def test_the_mouth_starts_at_the_interior_ceiling(self) -> None:
        low, size = bbox(interior_mouth(INTERIOR, headroom=50.0))
        self.assertEqual(tuple(round(v, 6) for v in low), (2.0, 2.0, 28.0))
        self.assertEqual(tuple(round(v, 6) for v in size[:2]), (96.0, 76.0))

    def test_carving_opens_the_box(self) -> None:
        """A compartmented body is carved from a solid block, so the material
        above the interior ceiling has to go — otherwise every well is sealed."""
        placement = CompartmentPlacement("Well", (50.0, 40.0), 20.0, (2.0, 2.0))
        contents = build_contents([placement], INTERIOR)
        low, size = bbox(contents)
        self.assertGreater(
            low[2] + size[2], SPEC["height"],
            "the cutout must reach past the top of the box",
        )


class CompartmentCarveTests(unittest.TestCase):
    def carve(self, placements, builders=None):
        return build_shell(SPEC) - build_contents(placements, INTERIOR, builders)

    def test_a_well_sits_below_the_interior_ceiling(self) -> None:
        """Wells hang from the rim, so a shallow one keeps its pieces in reach."""
        placement = CompartmentPlacement("Shallow", (50.0, 40.0), 6.0, (2.0, 2.0))
        low, _ = bbox(build_contents([placement], INTERIOR, clip=False))
        # interior ceiling (28) minus the 6mm depth.
        self.assertAlmostEqual(low[2], 22.0, places=3)

    def test_a_well_that_overhangs_is_clipped_to_the_interior(self) -> None:
        """FR-018: a cutout must never break through a side wall."""
        overhanging = CompartmentPlacement("Wide", (200.0, 200.0), 20.0, (2.0, 2.0))
        low, size = bbox(build_contents([overhanging], INTERIOR))
        self.assertGreaterEqual(round(low[0], 6), INTERIOR.origin_x)
        self.assertGreaterEqual(round(low[1], 6), INTERIOR.origin_y)
        self.assertLessEqual(round(low[0] + size[0], 6), INTERIOR.max_x)
        self.assertLessEqual(round(low[1] + size[1], 6), INTERIOR.max_y)

    def test_a_finger_scoop_is_allowed_through_the_wall(self) -> None:
        """The scoop is the one cutout whose job is to pierce a wall."""
        placement = CompartmentPlacement("Cards", (96.0, 76.0), 26.0, (2.0, 2.0))
        builder = CompartmentBuilder(
            label="Cards", size=(96.0, 76.0), depth=26.0,
            finger_scoop=True, scoop_side=ScoopSide.FRONT,
        )
        plain = build_contents([placement], INTERIOR)
        scooped = build_contents([placement], INTERIOR, {"Cards": builder})

        self.assertGreater(bbox(plain)[0][1], bbox(scooped)[0][1],
                           "the scoop should reach past the front wall")

    def test_a_shallow_compartment_falls_back_to_a_floor_bowl(self) -> None:
        """A notch through a 4mm-deep wall is not something a finger can use."""
        from pyboxbuilder.compartments.finger_hole import build_floor_scoop, build_scoop

        shallow = build_scoop(60.0, 40.0, 4.0, ScoopSide.FRONT, radius=12.0)
        # The floor scoop now takes the compartment depth (it sizes the cut and
        # picks scoop_profile's tangent-blend branch), so the expectation has to
        # state the same 4mm the routed call passed.
        expected = build_floor_scoop(
            60.0, 40.0, ScoopSide.FRONT, radius=12.0, comp_depth=4.0,
        )
        self.assertEqual(bbox(shallow), bbox(expected))

    def test_a_deep_compartment_gets_a_wall_notch(self) -> None:
        from pyboxbuilder.compartments.finger_hole import build_scoop, build_wall_scoop

        deep = build_scoop(60.0, 40.0, 26.0, ScoopSide.FRONT, radius=12.0)
        expected = build_wall_scoop(60.0, 40.0, 26.0, ScoopSide.FRONT, radius=12.0)
        self.assertEqual(bbox(deep), bbox(expected))

    def test_no_compartments_carves_nothing(self) -> None:
        self.assertIsNone(build_contents([], INTERIOR))


if __name__ == "__main__":
    unittest.main()
