# SPDX-License-Identifier: Apache-2.0
"""Tests for CompartmentBuilder."""

import unittest

from pyboxbuilder.compartments.builder import CompartmentBuilder
from pyboxbuilder.enums import ScoopSide


class CompartmentBuilderTests(unittest.TestCase):
    def test_basic_compartment(self) -> None:
        cb = CompartmentBuilder(label="Well", size=(50, 50), depth=30)
        self.assertEqual(cb.label, "Well")
        self.assertEqual(cb.size, (50, 50))
        self.assertEqual(cb.depth, 30)
        self.assertEqual(cb.rounded_corners, 0.0)
        self.assertFalse(cb.finger_scoop)

    def test_ratio_based_sizing(self) -> None:
        """Compartment sized by ratio of interior."""
        cb = CompartmentBuilder(
            label="RWell", width_ratio=0.5, length_ratio=0.8, depth=30,
        )
        self.assertEqual(cb.width_ratio, 0.5)
        self.assertEqual(cb.length_ratio, 0.8)
        self.assertIsNone(cb.size)

    def test_ratio_resolve_absolute(self) -> None:
        """resolve_size computes absolute from ratio and interior."""
        cb = CompartmentBuilder(
            label="Half", width_ratio=0.5, length_ratio=1.0, depth=20,
        )
        w, l = cb.resolve_size(200, 150)
        self.assertEqual(w, 100.0)
        self.assertEqual(l, 150.0)

    def test_ratio_resolve_mixed(self) -> None:
        """Mixed absolute width + ratio length."""
        cb = CompartmentBuilder(
            label="Mixed", size=(50, None), length_ratio=0.5, depth=20,
        )
        w, l = cb.resolve_size(200, 150)
        self.assertEqual(w, 50.0)
        self.assertEqual(l, 75.0)

    def test_ratio_precision_tenth_mm(self) -> None:
        """Ratios resolve to 0.1mm precision, not whole mm."""
        cb = CompartmentBuilder(
            label="Precise", width_ratio=0.333, length_ratio=0.777, depth=20,
        )
        w, l = cb.resolve_size(100, 100)
        self.assertEqual(w, 33.3)
        self.assertEqual(l, 77.7)

    def test_ratio_invalid_range(self) -> None:
        """Ratios outside (0, 1] are rejected."""
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="Bad", width_ratio=0, depth=20)
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="Bad", width_ratio=1.5, depth=20)

    def test_no_size_or_ratio_raises(self) -> None:
        """At least one sizing mode is required."""
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="NoSize", depth=20)

    def test_ratio_overflow_rejected_in_project(self) -> None:
        """Project export rejects compartments whose ratios sum > 1.0."""
        from pyboxbuilder.project import Project
        from pyboxbuilder.enums import BoxType
        p = Project("Overflow", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "Bad", size=(100, 100, 50))
        b.compartment("A", width_ratio=0.6, depth=20)
        b.compartment("B", width_ratio=0.6, depth=20)
        with self.assertRaises(ValueError) as ctx:
            p.export("/tmp/test_overflow")
        self.assertIn("1.20", str(ctx.exception))

    def test_default_scoop_side(self) -> None:
        cb = CompartmentBuilder(
            label="Well", size=(50, 50), depth=30, finger_scoop=True,
        )
        self.assertEqual(cb.scoop_side, ScoopSide.FRONT)

    def test_explicit_scoop_side(self) -> None:
        cb = CompartmentBuilder(
            label="Well", size=(50, 50), depth=30,
            finger_scoop=True, scoop_side=ScoopSide.BACK,
        )
        self.assertEqual(cb.scoop_side, ScoopSide.BACK)

    def test_rounded_corners_default(self) -> None:
        cb = CompartmentBuilder(label="Well", size=(50, 50), depth=30)
        self.assertEqual(cb.rounded_corners, 0.0)
