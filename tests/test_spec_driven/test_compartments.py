# SPDX-License-Identifier: Apache-2.0
"""Tests for CompartmentBuilder."""

import unittest

from spec_driven.compartments.builder import CompartmentBuilder
from spec_driven.enums import ScoopSide


class CompartmentBuilderTests(unittest.TestCase):
    def test_basic_compartment(self) -> None:
        cb = CompartmentBuilder(label="Well", size=(50, 50), depth=30)
        self.assertEqual(cb.label, "Well")
        self.assertEqual(cb.size, (50, 50))
        self.assertEqual(cb.depth, 30)
        self.assertEqual(cb.rounded_corners, 0.0)
        self.assertFalse(cb.finger_scoop)

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
