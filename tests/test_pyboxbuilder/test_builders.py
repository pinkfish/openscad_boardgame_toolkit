# SPDX-License-Identifier: Apache-2.0
"""Tests for BoxBuilder base class."""

import unittest

from pyboxbuilder.builders._base import BoxBuilder, FingerHoleBuilder
from pyboxbuilder.enums import BoxType, ScoopSide
from pyboxbuilder.lid.builder import LidBuilder
from pyboxbuilder.compartments.builder import CompartmentBuilder


class BoxBuilderTests(unittest.TestCase):
    def test_default_values(self) -> None:
        b = BoxBuilder(
            label="TestBox",
            size=(100, 80, 40),
        )
        self.assertEqual(b.label, "TestBox")
        self.assertEqual(b.size, (100, 80, 40))
        self.assertIsNone(b.box_id)
        self.assertTrue(b.expandable)
        self.assertTrue(b.expandable_width)
        self.assertTrue(b.expandable_length)
        self.assertIsNone(b.lid)
        self.assertEqual(b.compartments, ())
        self.assertEqual(b.finger_holes, ())

    def test_box_id_defaults_to_none(self) -> None:
        b = BoxBuilder(label="Cards", size=(100, 70, 50))
        self.assertIsNone(b.box_id)

    def test_box_id_explicit(self) -> None:
        b = BoxBuilder(label="Cards", size=(100, 70, 50), box_id="card_1")
        self.assertEqual(b.box_id, "card_1")

    def test_size_none_auto_compute(self) -> None:
        b = BoxBuilder(label="AutoBox")
        self.assertIsNone(b.size)
        self.assertIsNone(b.final_size)

    def test_final_size_default_none(self) -> None:
        b = BoxBuilder(label="Test", size=(100, 100, 50))
        self.assertIsNone(b.final_size)

    def test_add_compartment(self) -> None:
        b = BoxBuilder(label="Test", size=(200, 150, 60))
        cb = b.compartment("Well1", size=(90, 65), depth=45)
        self.assertIsInstance(cb, CompartmentBuilder)
        self.assertEqual(cb.label, "Well1")
        self.assertEqual(cb.size, (90, 65))
        self.assertEqual(cb.depth, 45)
        self.assertFalse(cb.finger_scoop)
        # Unset until carve time, which picks the shorter wall.
        self.assertIsNone(cb.scoop_side)
        self.assertEqual(len(b.compartments), 1)

    def test_add_compartment_with_scoop(self) -> None:
        b = BoxBuilder(label="Test", size=(200, 150, 60))
        cb = b.compartment(
            "ScoopWell", size=(50, 50), depth=25,
            finger_scoop=True, scoop_side=ScoopSide.LEFT,
        )
        self.assertTrue(cb.finger_scoop)
        self.assertEqual(cb.scoop_side, ScoopSide.LEFT)

    def test_finger_holes_default_empty(self) -> None:
        b = BoxBuilder(label="Test", size=(100, 100, 50))
        self.assertEqual(b.finger_holes, ())


class FingerHoleBuilderTests(unittest.TestCase):
    def test_defaults(self) -> None:
        from pyboxbuilder.enums import ScoopSide

        # `side` is a ScoopSide now, not a bare string (the "no bare strings"
        # constraint); a string named no wall and silently cut nothing.
        fh = FingerHoleBuilder(side=ScoopSide.LEFT)
        self.assertIs(fh.side, ScoopSide.LEFT)
        self.assertEqual(fh.radius, 14.0)
        # `None` means "as tall as the finger" — the height of a finger cut
        # follows the radius, not a constant (the old 6.0 came from the
        # original's *wall depth* parameter, a different quantity).
        self.assertIsNone(fh.depth)
        self.assertEqual(fh.offset, 0.0)
        self.assertIsNone(fh.rounding_radius)
        self.assertIsNone(fh.rounding_edge)
