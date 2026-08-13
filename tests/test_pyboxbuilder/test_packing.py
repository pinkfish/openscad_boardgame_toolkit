# SPDX-License-Identifier: Apache-2.0
"""Tests for box packing and auto-sizing."""

import unittest

from pyboxbuilder.packing.layout import pack_boxes, BoxPacking, PackingError
from pyboxbuilder.packing.spacer import generate_spacers
from pyboxbuilder.packing.cache import cache_key, set_cached, get_cached


class PackingTests(unittest.TestCase):
    def test_pack_single_box(self) -> None:
        boxes = [{"label": "A", "size": (50, 50, 30)}]
        result = pack_boxes((200, 150, 60), boxes)
        self.assertEqual(len(result.placements), 1)
        self.assertEqual(result.placements[0].label, "A")

    def test_pack_multiple_boxes_same_row(self) -> None:
        boxes = [
            {"label": "A", "size": (50, 50, 30)},
            {"label": "B", "size": (50, 50, 30)},
        ]
        result = pack_boxes((200, 150, 60), boxes)
        self.assertEqual(len(result.placements), 2)

    def test_pack_wrap_to_new_row(self) -> None:
        boxes = [
            {"label": "A", "size": (150, 50, 30)},
            {"label": "B", "size": (150, 50, 30)},
        ]
        result = pack_boxes((200, 150, 60), boxes)
        self.assertGreater(len(result.placements), 0)

    def test_spacer_generation(self) -> None:
        spacers = generate_spacers(200, 150, [150], [50], gap_threshold=10)
        self.assertGreater(len(spacers), 0)
        self.assertEqual(spacers[0].width, 50)

    def test_spacer_under_threshold_absorbed(self) -> None:
        """Width gap of 8mm (under 10mm threshold) is absorbed but length gap still produces spacer."""
        spacers = generate_spacers(200, 150, [198], [50], gap_threshold=10)
        # Width gap: 200 - 198 = 2 < 10 → absorbed ✓
        # Length gap: 150 - 50 = 100 ≥ 10 → spacer generated
        self.assertGreater(len(spacers), 0)

    def test_spacer_all_gaps_under_threshold(self) -> None:
        """All gaps under threshold → zero spacers."""
        spacers = generate_spacers(200, 50, [199], [48], gap_threshold=10)
        self.assertEqual(len(spacers), 0)

    def test_cache_key_deterministic(self) -> None:
        k1 = cache_key({"container": [200, 150, 60], "boxes": [1, 2, 3]})
        k2 = cache_key({"container": [200, 150, 60], "boxes": [1, 2, 3]})
        self.assertEqual(k1, k2)

    def test_cache_key_different_inputs(self) -> None:
        k1 = cache_key({"container": [200, 150, 60]})
        k2 = cache_key({"container": [200, 150, 61]})
        self.assertNotEqual(k1, k2)

    def test_cache_set_get(self) -> None:
        key = "test-set-get-key"
        set_cached(key, {"result": "ok"})
        value = get_cached(key)
        self.assertEqual(value, {"result": "ok"})

    def test_cache_miss(self) -> None:
        value = get_cached("nonexistent-key-12345")
        self.assertIsNone(value)


class NoRotateTests(unittest.TestCase):
    def test_no_rotate_box_never_rotated(self) -> None:
        """A no_rotate box keeps its original orientation (FR-013c)."""
        result = pack_boxes((300, 300, 39), [
            {"label": "A", "size": (214, 77, 28.5), "no_rotate": True},
        ])
        self.assertEqual(len(result.placements), 1)
        self.assertFalse(result.placements[0].rotation)
        self.assertEqual(tuple(result.placements[0].size), (214, 77, 28.5))

    def test_rotatable_box_can_rotate(self) -> None:
        """A rotatable box (no_rotate=False) may be rotated to fit."""
        # Container narrower than the box width forces a rotation
        result = pack_boxes((100, 300, 39), [
            {"label": "A", "size": (214, 77, 28.5), "no_rotate": False},
        ])
        if result.placements:
            # If placed, the box must have been rotated to fit the 100-wide container
            self.assertTrue(result.placements[0].rotation)

    def test_no_rotate_does_not_fit_narrow_container(self) -> None:
        """A no_rotate box that cannot fit without rotation is an error.

        This used to come back as an empty packing, so an export would quietly
        write no boxes at all and still report success.
        """
        with self.assertRaises(PackingError) as ctx:
            pack_boxes((100, 300, 39), [
                {"label": "A", "size": (214, 77, 28.5), "no_rotate": True},
            ])
        self.assertIn("Could not pack", str(ctx.exception))

    def test_packing_error_names_boxes_taller_than_the_container(self) -> None:
        with self.assertRaises(PackingError) as ctx:
            pack_boxes((300, 300, 20), [{"label": "Tall", "size": (50, 50, 40)}])
        self.assertIn("Tall", str(ctx.exception))

    def test_packing_error_reports_the_fill_ratio(self) -> None:
        """When nothing is oversized, the message says how full the box is."""
        with self.assertRaises(PackingError) as ctx:
            pack_boxes((100, 100, 100), [
                {"label": f"B{n}", "size": (60, 60, 60), "no_rotate": True}
                for n in range(4)
            ])
        self.assertIn("fill", str(ctx.exception))
