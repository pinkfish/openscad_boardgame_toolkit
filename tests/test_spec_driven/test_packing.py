# SPDX-License-Identifier: Apache-2.0
"""Tests for box packing and auto-sizing."""

import unittest

from spec_driven.packing.layout import pack_boxes, BoxPacking
from spec_driven.packing.spacer import generate_spacers
from spec_driven.packing.cache import cache_key, set_cached, get_cached


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
