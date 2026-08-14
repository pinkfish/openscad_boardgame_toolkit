# SPDX-License-Identifier: Apache-2.0
"""Tests for the guillotine packer (T187).

Every test that claims a packing was found also checks the packing is physically
buildable: inside the container, no two boxes sharing space, and every box fully
resting on the floor or on the boxes below it. A packer that reports success
while floating a box is worse than one that reports failure.
"""

from __future__ import annotations

import random
import unittest

from pyboxbuilder.packing.guillotine import Item, Placed, pack_guillotine

EPS = 1e-6


def overlaps(a: Placed, b: Placed) -> bool:
    for axis in range(3):
        if (a.position[axis] + a.size[axis] <= b.position[axis] + EPS
                or b.position[axis] + b.size[axis] <= a.position[axis] + EPS):
            return False
    return True


def supported_fraction(box: Placed, others: list[Placed]) -> float:
    """How much of a box's base rests on the floor or on another box's top."""
    x, y, z = box.position
    w, l, _ = box.size
    if z < EPS:
        return 1.0

    rects = []
    for other in others:
        if other is box:
            continue
        ox, oy, oz = other.position
        ow, ol, oh = other.size
        if abs(oz + oh - z) > EPS:
            continue
        ax, bx = max(x, ox), min(x + w, ox + ow)
        ay, by = max(y, oy), min(y + l, oy + ol)
        if bx - ax > EPS and by - ay > EPS:
            rects.append((ax, ay, bx, by))
    if not rects:
        return 0.0

    xs = sorted({r[0] for r in rects} | {r[2] for r in rects})
    ys = sorted({r[1] for r in rects} | {r[3] for r in rects})
    area = 0.0
    for x0, x1 in zip(xs, xs[1:]):
        for y0, y1 in zip(ys, ys[1:]):
            if any(r[0] <= x0 + EPS and r[2] >= x1 - EPS
                   and r[1] <= y0 + EPS and r[3] >= y1 - EPS for r in rects):
                area += (x1 - x0) * (y1 - y0)
    return area / (w * l)


class PackingValidator(unittest.TestCase):
    def assertValidPacking(self, container, items, placements) -> None:
        self.assertIsNotNone(placements, "no packing found")
        self.assertEqual(
            sorted(p.label for p in placements),
            sorted(i.label for i in items),
            "every box must be placed exactly once",
        )

        by_label = {i.label: i for i in items}
        for p in placements:
            with self.subTest(box=p.label):
                for axis in range(3):
                    self.assertGreaterEqual(p.position[axis], -EPS)
                    self.assertLessEqual(
                        p.position[axis] + p.size[axis], container[axis] + EPS,
                        f"{p.label} sticks out of the container",
                    )
                item = by_label[p.label]
                expected = (
                    (item.size[1], item.size[0], item.size[2]) if p.rotated
                    else tuple(item.size)
                )
                self.assertEqual(tuple(p.size), expected)
                if item.no_rotate:
                    self.assertFalse(p.rotated, "no_rotate box was turned")
                self.assertAlmostEqual(
                    supported_fraction(p, placements), 1.0, places=6,
                    msg=f"{p.label} is not fully supported",
                )

        for i, a in enumerate(placements):
            for b in placements[i + 1:]:
                self.assertFalse(
                    overlaps(a, b), f"{a.label} overlaps {b.label}"
                )


class BasicPackingTests(PackingValidator):
    def test_a_single_box(self) -> None:
        container = (200.0, 150.0, 60.0)
        items = [Item("A", (50.0, 50.0, 30.0))]
        self.assertValidPacking(container, items, pack_guillotine(container, items))

    def test_no_items_packs_trivially(self) -> None:
        self.assertEqual(pack_guillotine((100.0, 100.0, 100.0), []), [])

    def test_an_exact_tiling(self) -> None:
        """Eight boxes that fill the container completely, leaving nothing."""
        container = (100.0, 100.0, 100.0)
        items = [Item(f"B{n}", (50.0, 50.0, 50.0)) for n in range(8)]
        placements = pack_guillotine(container, items)
        self.assertValidPacking(container, items, placements)

    def test_a_box_that_cannot_fit_fails(self) -> None:
        container = (100.0, 100.0, 50.0)
        self.assertIsNone(
            pack_guillotine(container, [Item("Tall", (50.0, 50.0, 80.0))])
        )

    def test_one_box_too_many_fails(self) -> None:
        container = (100.0, 100.0, 100.0)
        items = [Item(f"B{n}", (50.0, 50.0, 50.0)) for n in range(9)]
        self.assertIsNone(pack_guillotine(container, items))

    def test_a_box_is_turned_to_fit(self) -> None:
        container = (100.0, 220.0, 30.0)
        items = [Item("Wide", (200.0, 90.0, 30.0))]
        placements = pack_guillotine(container, items)
        self.assertValidPacking(container, items, placements)
        self.assertTrue(placements[0].rotated)

    def test_a_box_that_fits_either_way_is_left_alone(self) -> None:
        """Turning a box changes the orientation of the printed part, so it
        should only happen when turning actually buys something."""
        container = (300.0, 200.0, 80.0)
        items = [Item("A", (100.0, 80.0, 40.0))]
        placements = pack_guillotine(container, items)
        self.assertValidPacking(container, items, placements)
        self.assertFalse(placements[0].rotated)
        self.assertEqual(tuple(placements[0].size), (100.0, 80.0, 40.0))

    def test_a_no_rotate_box_is_never_turned(self) -> None:
        container = (100.0, 220.0, 30.0)
        items = [Item("Wide", (200.0, 90.0, 30.0), no_rotate=True)]
        self.assertIsNone(pack_guillotine(container, items))


class SupportTests(PackingValidator):
    def test_nothing_is_left_floating(self) -> None:
        """A wide box on top of two narrow ones must not overhang either.

        The corner-point solver placed exactly this case with one corner resting
        on a box and the rest in mid-air.
        """
        container = (100.0, 100.0, 40.0)
        items = [
            Item("Base", (100.0, 100.0, 20.0)),
            Item("Left", (40.0, 100.0, 20.0)),
            Item("Right", (60.0, 100.0, 20.0)),
        ]
        self.assertValidPacking(container, items, pack_guillotine(container, items))

    def test_a_wide_box_is_not_bridged_over_a_gap(self) -> None:
        """Two narrow boxes only half-fill the floor; the wide one must not sit
        on them with the rest of its base over air. Putting the wide box on the
        floor and the narrow pair on top is the arrangement that works."""
        container = (100.0, 100.0, 40.0)
        items = [
            Item("NarrowA", (100.0, 40.0, 20.0), no_rotate=True),
            Item("NarrowB", (100.0, 40.0, 20.0), no_rotate=True),
            Item("Wide", (100.0, 100.0, 20.0), no_rotate=True),
        ]
        placements = pack_guillotine(container, items)
        self.assertValidPacking(container, items, placements)
        wide = next(p for p in placements if p.label == "Wide")
        self.assertAlmostEqual(wide.position[2], 0.0, places=6)

    def test_a_box_may_bridge_a_layer_that_is_filled_solid(self) -> None:
        """Bridging is legal when the layer underneath is packed solid.

        Two boxes fill the lower layer edge to edge, so a box spanning both of
        them rests on a continuous surface. A solver that cuts only at one box's
        own faces cannot express this, and real inserts stack exactly this way.
        """
        container = (100.0, 100.0, 40.0)
        items = [
            Item("LowerLeft", (40.0, 100.0, 20.0), no_rotate=True),
            Item("LowerRight", (60.0, 100.0, 20.0), no_rotate=True),
            Item("UpperLeft", (70.0, 100.0, 20.0), no_rotate=True),
            Item("UpperRight", (30.0, 100.0, 20.0), no_rotate=True),
        ]
        placements = pack_guillotine(container, items)
        self.assertValidPacking(container, items, placements)

        # Which pair lands on the floor is the solver's choice -- the labels
        # mean nothing to it -- so check the geometry instead: two layers, and
        # the seam in the upper one falls somewhere other than the lower one, so
        # a box genuinely spans the join.
        lower = sorted(p.position[0] for p in placements if p.position[2] < EPS)
        upper = sorted(p.position[0] for p in placements if p.position[2] > EPS)
        self.assertEqual(len(lower), 2)
        self.assertEqual(len(upper), 2)
        self.assertNotEqual(lower, upper, "the layers did not need to bridge")


class EmberleafTests(PackingValidator):
    """The layout the previous solver could not find.

    18 boxes at 77% fill whose sizes tile exactly in columns. Five sort
    strategies, twelve solver variants and 266,000 random permutations of the
    extreme-point solver all failed on it.
    """

    CONTAINER = (286.0, 286.0, 52.5)
    """The 287mm game box less 2 x 0.5mm clearance, as `Project` computes it.

    The width matters to the millimetre: the three columns need 98 + 98 + 90 =
    286 exactly, and the solver correctly proves 285 impossible.
    """

    def items(self) -> list[Item]:
        items = []
        for n in range(5):
            items.append(Item(f"PlayerBox{n}", (98.0, 142.5, 13.125)))
        for n in range(4):
            items.append(Item(f"MaterialBox{n}", (98.0, 71.25, 13.125)))
        for n in range(3):
            items.append(Item(f"CardBox{n}", (98.0, 73.0, 52.5), no_rotate=True))
        for n in range(5):
            items.append(Item(f"CardBoxPlayer{n}", (90.0, 98.0, 10.5), no_rotate=True))
        items.append(Item("CommonBox", (90.0, 188.0, 25.0)))
        return items

    def test_the_emberleaf_insert_packs(self) -> None:
        items = self.items()
        placements = pack_guillotine(self.CONTAINER, items)
        self.assertValidPacking(self.CONTAINER, items, placements)

    def test_one_millimetre_narrower_is_correctly_refused(self) -> None:
        """At 285mm the columns cannot fit, and the solver says so rather than
        wedging a box in somewhere invalid."""
        self.assertIsNone(pack_guillotine((285.0, 286.0, 52.5), self.items()))

    def test_it_packs_well_within_the_node_budget(self) -> None:
        """It resolves in a few thousand nodes, not the default 200,000.

        Guards the search heuristics: if the region-selection rule or the
        candidate ordering regresses, this fails long before the default budget
        would hide it. Measured at 3,237 nodes, so 10,000 leaves real headroom.
        """
        items = self.items()
        self.assertIsNotNone(
            pack_guillotine(self.CONTAINER, items, node_budget=10_000)
        )


class RandomInstanceTests(PackingValidator):
    """Instances built by cutting a container up, so a packing is known to exist."""

    def guillotine_cut(self, rng, region, depth):
        x, y, z, w, l, h = region
        if depth == 0 or min(w, l, h) < 20.0:
            return [region]
        axis = rng.choice([0, 1, 2])
        span = (w, l, h)[axis]
        if span < 30.0:
            return [region]
        cut = round(rng.uniform(10.0, span - 10.0), 3)
        if axis == 0:
            a = (x, y, z, cut, l, h)
            b = (x + cut, y, z, w - cut, l, h)
        elif axis == 1:
            a = (x, y, z, w, cut, h)
            b = (x, y + cut, z, w, l - cut, h)
        else:
            a = (x, y, z, w, l, cut)
            b = (x, y, z + cut, w, l, h - cut)
        return self.guillotine_cut(rng, a, depth - 1) + self.guillotine_cut(rng, b, depth - 1)

    def test_packs_instances_that_are_known_to_tile(self) -> None:
        container = (200.0, 200.0, 100.0)
        solved = 0
        trials = 20
        for seed in range(trials):
            rng = random.Random(seed)
            pieces = self.guillotine_cut(rng, (0.0, 0.0, 0.0, *container), 3)
            items = [
                Item(f"P{n}", (p[3], p[4], p[5])) for n, p in enumerate(pieces)
            ]
            with self.subTest(seed=seed, boxes=len(items)):
                placements = pack_guillotine(container, items)
                if placements is not None:
                    self.assertValidPacking(container, items, placements)
                    solved += 1
        # These are 100%-fill instances, the hardest kind -- every one has a
        # perfect tiling and nothing else will do. All 20 currently solve; the
        # bar sits a little below that so an unlucky rounding change is not a
        # failure, but a real regression in search power is.
        self.assertGreaterEqual(
            solved, 18,
            f"only solved {solved}/{trials} instances known to tile exactly",
        )

    def test_never_reports_an_invalid_packing_on_loose_instances(self) -> None:
        """Whatever it returns must be buildable, packable or not."""
        container = (200.0, 200.0, 100.0)
        for seed in range(30):
            rng = random.Random(1000 + seed)
            items = [
                Item(
                    f"R{n}",
                    (
                        round(rng.uniform(20.0, 90.0), 2),
                        round(rng.uniform(20.0, 90.0), 2),
                        round(rng.uniform(10.0, 50.0), 2),
                    ),
                    no_rotate=rng.random() < 0.3,
                )
                for n in range(rng.randint(3, 9))
            ]
            placements = pack_guillotine(container, items, node_budget=20_000)
            if placements is not None:
                with self.subTest(seed=seed):
                    self.assertValidPacking(container, items, placements)


if __name__ == "__main__":
    unittest.main()
