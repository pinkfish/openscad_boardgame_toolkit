# SPDX-License-Identifier: Apache-2.0
"""Tests for the spacer sweep and merge pass (FR-014a/b/c, SC-010a/b)."""

from __future__ import annotations

import random
import unittest

from pyboxbuilder.packing.layout import Placement
from pyboxbuilder.packing.spacer import (
    Void,
    apply_clearance,
    generate_spacer_placements,
    generate_spacer_voids,
    merge_rectilinear,
    merge_voids,
    sweep_free_space,
)


def box(label, position, size) -> Placement:
    return Placement(label=label, position=position, size=size, rotation=False)


def voidset(voids) -> set[tuple]:
    """Voids as a comparable set, rounded past float noise."""
    return {
        (
            tuple(round(v, 4) for v in x.position),
            tuple(round(v, 4) for v in x.size),
        )
        for x in voids
    }


class MergeTests(unittest.TestCase):
    def test_two_voids_flush_along_z_fuse(self) -> None:
        merged = merge_voids([
            Void((0, 0, 0), (10, 10, 5)),
            Void((0, 0, 5), (10, 10, 7)),
        ])
        self.assertEqual(voidset(merged), {((0, 0, 0), (10, 10, 12))})

    def test_fusing_works_on_every_axis(self) -> None:
        for axis in range(3):
            position = [0.0, 0.0, 0.0]
            position[axis] = 10.0
            merged = merge_voids([
                Void((0, 0, 0), (10, 10, 10)),
                Void(tuple(position), (10, 10, 10)),
            ])
            self.assertEqual(len(merged), 1, f"axis {axis} did not fuse")
            self.assertEqual(merged[0].size[axis], 20.0)

    def test_voids_that_do_not_line_up_stay_apart(self) -> None:
        """Flush along z, but different footprints — the union is not a box."""
        voids = [Void((0, 0, 0), (10, 10, 5)), Void((0, 0, 5), (10, 8, 5))]
        self.assertEqual(len(merge_voids(voids)), 2)

    def test_voids_with_a_gap_between_them_stay_apart(self) -> None:
        voids = [Void((0, 0, 0), (10, 10, 5)), Void((0, 0, 6), (10, 10, 5))]
        self.assertEqual(len(merge_voids(voids)), 2)

    def test_a_run_of_slices_collapses_to_one(self) -> None:
        slices = [Void((0, 0, float(z)), (10, 10, 1)) for z in range(20)]
        self.assertEqual(voidset(merge_voids(slices)), {((0, 0, 0), (10, 10, 20))})

    def test_merging_is_idempotent(self) -> None:
        once = merge_voids([
            Void((0, 0, 0), (10, 10, 5)),
            Void((0, 0, 5), (10, 10, 5)),
            Void((30, 0, 0), (10, 10, 5)),
        ])
        self.assertEqual(voidset(merge_voids(once)), voidset(once))

    def test_merging_does_not_depend_on_input_order(self) -> None:
        """SC-010b — shuffling the input yields the same set of voids."""
        pieces = [
            Void((0, 0, 0), (10, 10, 5)),
            Void((0, 0, 5), (10, 10, 5)),
            Void((0, 0, 10), (10, 10, 5)),
            Void((40, 0, 0), (10, 10, 5)),
            Void((40, 10, 0), (10, 10, 5)),
        ]
        baseline = voidset(merge_voids(pieces))
        self.assertEqual(len(baseline), 2)

        rng = random.Random(1234)
        for _ in range(20):
            shuffled = pieces[:]
            rng.shuffle(shuffled)
            self.assertEqual(voidset(merge_voids(shuffled)), baseline)

    def test_an_l_shape_reduces_but_cannot_become_one_box(self) -> None:
        """Three cells in an L fuse to two — an L is not a box, so two is minimal."""
        merged = merge_voids([
            Void((0, 0, 0), (10, 10, 10)),
            Void((10, 0, 0), (10, 10, 10)),
            Void((0, 10, 0), (10, 10, 10)),
        ])
        self.assertEqual(len(merged), 2)


class SweepTests(unittest.TestCase):
    def test_an_empty_container_yields_nothing(self) -> None:
        """With no boxes there is no layout to fill; a bare tray is not a spacer."""
        self.assertEqual(sweep_free_space((100, 100, 50), []), [])

    def test_a_full_container_yields_nothing(self) -> None:
        filled = [box("A", (0, 0, 0), (100, 100, 50))]
        self.assertEqual(sweep_free_space((100, 100, 50), filled), [])

    def test_one_box_in_a_corner_leaves_an_l_of_free_space(self) -> None:
        voids = sweep_free_space((100, 100, 10), [box("A", (0, 0, 0), (60, 40, 10))])
        covered = sum(v.volume for v in voids)
        self.assertAlmostEqual(covered, 100 * 100 * 10 - 60 * 40 * 10, places=3)

    def test_voids_never_overlap_each_other(self) -> None:
        placements = [
            box("A", (0, 0, 0), (40, 40, 20)),
            box("B", (40, 0, 0), (30, 60, 10)),
            box("C", (0, 60, 10), (50, 40, 30)),
        ]
        voids = sweep_free_space((100, 100, 50), placements)
        for i, a in enumerate(voids):
            for b in voids[i + 1:]:
                overlaps = all(
                    a.position[axis] + 1e-6 < b.position[axis] + b.size[axis]
                    and b.position[axis] + 1e-6 < a.position[axis] + a.size[axis]
                    for axis in range(3)
                )
                self.assertFalse(overlaps)

    def test_voids_never_overlap_a_placed_box(self) -> None:
        placements = [
            box("A", (0, 0, 0), (40, 40, 20)),
            box("B", (40, 0, 0), (30, 60, 10)),
        ]
        for void in sweep_free_space((100, 100, 50), placements):
            for placed in placements:
                overlaps = all(
                    void.position[axis] + 1e-6 < placed.position[axis] + placed.size[axis]
                    and placed.position[axis] + 1e-6 < void.position[axis] + void.size[axis]
                    for axis in range(3)
                )
                self.assertFalse(overlaps, f"{placed.label} is inside a void")

    def test_a_sliver_does_not_fragment_the_void_beside_it(self) -> None:
        """FR-014a — the whole reason the sweep takes the largest box first.

        A box leaves a big void plus a 2mm strip. Scanning in index order lets
        the strip claim cells out of the big void's middle and split it in two;
        taking the largest available box first keeps it whole.
        """
        placements = [box("A", (0, 0, 0), (98, 100, 50))]
        voids = sweep_free_space((100, 100, 50), placements)
        self.assertEqual(
            voidset(voids), {((98, 0, 0), (2, 100, 50))},
            "the leftover strip should come out as one piece",
        )


class RectilinearMergeTests(unittest.TestCase):
    """Coplanar neighbours that no rectangle covers become one polygon tray."""

    def test_an_l_in_the_footprint_becomes_one_polygon_tray(self) -> None:
        merged = merge_rectilinear([
            Void((0, 40, 0), (100, 60, 20)),
            Void((60, 0, 0), (40, 40, 20)),
        ])
        self.assertEqual(len(merged), 1)
        self.assertIsNotNone(merged[0].path)
        self.assertEqual(len(merged[0].path), 6, "an L has six corners")
        self.assertEqual(merged[0].position, (0, 0, 0))
        self.assertEqual(merged[0].size, (100, 100, 20))

    def test_the_polygon_covers_the_same_area_as_its_parts(self) -> None:
        parts = [Void((0, 40, 0), (100, 60, 20)), Void((60, 0, 0), (40, 40, 20))]
        merged = merge_rectilinear(parts)
        self.assertAlmostEqual(
            merged[0].volume, sum(p.volume for p in parts), places=3
        )

    def test_a_u_shape_comes_back_with_eight_corners(self) -> None:
        merged = merge_rectilinear([
            Void((0, 0, 0), (20, 100, 10)),
            Void((20, 0, 0), (60, 20, 10)),
            Void((80, 0, 0), (20, 100, 10)),
        ])
        self.assertEqual(len(merged), 1)
        self.assertEqual(len(merged[0].path), 8)

    def test_voids_at_different_heights_are_left_alone(self) -> None:
        """A vertical L would print as an unsupported shelf — see the docstring
        on merge_rectilinear. Two flat trays each rest on what is beneath them."""
        stacked = [
            Void((108, 78, 14.2), (105, 131.8, 14.2)),
            Void((161.5, 78, 0), (51.5, 131.8, 14.2)),
        ]
        merged = merge_rectilinear(stacked)
        self.assertEqual(len(merged), 2)
        self.assertTrue(all(v.path is None for v in merged))

    def test_coplanar_but_separated_voids_are_left_alone(self) -> None:
        apart = [Void((0, 0, 0), (20, 20, 10)), Void((50, 50, 0), (20, 20, 10))]
        self.assertEqual(len(merge_rectilinear(apart)), 2)

    def test_a_lone_void_is_untouched(self) -> None:
        one = [Void((0, 0, 0), (20, 20, 10))]
        self.assertEqual(merge_rectilinear(one), one)

    def test_a_polygon_spacer_reaches_the_placement_as_a_path(self) -> None:
        placements = [box("A", (0, 0, 0), (60, 40, 20))]
        spacers = generate_spacer_placements((100, 100, 20), placements)
        self.assertEqual(len(spacers), 1)
        self.assertIsNotNone(spacers[0].path)
        # The path is relative to the placement's own corner, which is the frame
        # PathBox extrudes in.
        self.assertTrue(all(x >= -0.001 and y >= -0.001 for x, y in spacers[0].path))

    def test_a_polygon_spacer_builds_as_a_path_box(self) -> None:
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.enums import BoxType

        placements = [box("A", (0, 0, 0), (60, 40, 20))]
        spacer = generate_spacer_placements((100, 100, 20), placements)[0]
        body = BOX_IMPL_REGISTRY[BoxType.PATH]().build_body({
            "width": spacer.size[0], "length": spacer.size[1], "height": spacer.size[2],
            "wall_thickness": 2.0, "floor_thickness": 1.6, "path": spacer.path,
        })
        _, size = body.bounds()
        self.assertAlmostEqual(size[0], spacer.size[0], places=2)
        self.assertAlmostEqual(size[1], spacer.size[1], places=2)


class RectilinearInsetTests(unittest.TestCase):
    """An L must inset on all six sides — a centroid scale gets this wrong."""

    def test_every_side_of_an_l_moves_inward(self) -> None:
        from pyboxbuilder.paths import inset_rectilinear, polygon_area

        outline = ((0, 40), (60, 40), (60, 0), (100, 0), (100, 100), (0, 100))
        inset = inset_rectilinear(outline, 1.0)

        self.assertEqual(len(inset), 6)
        self.assertLess(polygon_area(inset), polygon_area(outline))
        # Outer corner pulls in on both axes; the reflex corner pushes out into
        # the notch on both axes, which is what keeps the arm's width right.
        self.assertEqual(inset[4], (99.0, 99.0))   # convex, top-right
        self.assertEqual(inset[1], (61.0, 41.0))   # reflex, inside the notch

    def test_insetting_keeps_the_shape_rectilinear(self) -> None:
        from pyboxbuilder.paths import inset_rectilinear, is_rectilinear

        outline = ((0, 40), (60, 40), (60, 0), (100, 0), (100, 100), (0, 100))
        self.assertTrue(is_rectilinear(inset_rectilinear(outline, 1.5)))

    def test_clearance_on_a_polygon_void_insets_its_path(self) -> None:
        void = Void(
            (0, 0, 0), (100, 100, 20),
            path=((0, 40), (60, 40), (60, 0), (100, 0), (100, 100), (0, 100)),
        )
        shrunk = apply_clearance(void, 1.0)
        self.assertEqual(shrunk.position, (1.0, 1.0, 0))
        self.assertEqual(shrunk.size, (98.0, 98.0, 20))
        self.assertLess(shrunk.volume, void.volume)


class ClearanceTests(unittest.TestCase):
    def test_clearance_insets_the_footprint_only(self) -> None:
        """A tray lifts straight up, so only width and length need the gap."""
        shrunk = apply_clearance(Void((10, 20, 30), (50, 60, 40)), 0.5)
        self.assertEqual(shrunk.position, (10.5, 20.5, 30))
        self.assertEqual(shrunk.size, (49.0, 59.0, 40))

    def test_zero_clearance_changes_nothing(self) -> None:
        void = Void((10, 20, 30), (50, 60, 40))
        self.assertEqual(apply_clearance(void, 0.0), void)


class PipelineTests(unittest.TestCase):
    def test_thin_voids_are_dropped_as_unprintable(self) -> None:
        placements = [box("A", (0, 0, 0), (98, 100, 50))]
        self.assertEqual(
            generate_spacer_voids((100, 100, 50), placements, min_dim=5.0), []
        )

    def test_two_slivers_that_merge_into_a_printable_tray_survive(self) -> None:
        """Merging runs before the minimum-thickness filter, on purpose."""
        placements = [
            box("A", (0, 0, 0), (100, 100, 20)),
            box("B", (0, 0, 24), (100, 100, 26)),
        ]
        # The 4mm band at z=20..24 is one void, and too thin — dropped.
        self.assertEqual(generate_spacer_voids((100, 100, 50), placements), [])

        # Widen the band past the minimum and it is kept.
        placements[1] = box("B", (0, 0, 26), (100, 100, 24))
        kept = generate_spacer_voids((100, 100, 50), placements)
        self.assertEqual(len(kept), 1)
        self.assertAlmostEqual(kept[0].size[2], 6.0, places=3)

    def test_placements_are_numbered_from_one_in_size_order(self) -> None:
        placements = [
            box("A", (0, 0, 0), (50, 100, 50)),
            box("B", (50, 0, 0), (50, 60, 50)),
        ]
        spacers = generate_spacer_placements((100, 100, 50), placements)
        self.assertEqual([s.label for s in spacers], ["spacer_1"])

    def test_the_result_does_not_depend_on_box_order(self) -> None:
        placements = [
            box("A", (0, 0, 0), (40, 40, 20)),
            box("B", (40, 0, 0), (30, 60, 10)),
            box("C", (0, 60, 10), (50, 40, 30)),
        ]
        baseline = voidset(generate_spacer_voids((100, 100, 50), placements))
        rng = random.Random(7)
        for _ in range(10):
            shuffled = placements[:]
            rng.shuffle(shuffled)
            self.assertEqual(
                voidset(generate_spacer_voids((100, 100, 50), shuffled)), baseline
            )


if __name__ == "__main__":
    unittest.main()
