# SPDX-License-Identifier: Apache-2.0
"""Tests for LidBuilder and PatternBuilder."""

import unittest

from pyboxbuilder.enums import LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder


class PatternBuilderTests(unittest.TestCase):
    def test_defaults(self) -> None:
        pb = PatternBuilder()
        self.assertEqual(pb.type, PatternType.HEX_GRID)
        self.assertEqual(pb.colors, ())
        self.assertIsNone(pb.spacing)


class LidBuilderTests(unittest.TestCase):
    def test_defaults(self) -> None:
        lb = LidBuilder()
        self.assertIsNone(lb.text)
        self.assertEqual(lb.label_mode, LabelMode.FRAMED)
        self.assertFalse(lb.diagonal)
        self.assertIsNone(lb.text_color)
        self.assertIsNone(lb.frame_color)
        self.assertIsNone(lb.pattern)
        self.assertIsNone(lb.pattern_color)
        self.assertEqual(lb.min_text_height_mm, 4.0)
        self.assertEqual(lb.border_margin_mm, 5.0)

    def test_with_text(self) -> None:
        lb = LidBuilder(text="Cards")
        self.assertEqual(lb.text, "Cards")

    def test_frameless_diagonal(self) -> None:
        lb = LidBuilder(
            text="TOKENS",
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
        )
        self.assertEqual(lb.label_mode, LabelMode.FRAMELESS)
        self.assertTrue(lb.diagonal)

    def test_with_pattern(self) -> None:
        pb = PatternBuilder(type=PatternType.GRID, spacing=10.0)
        lb = LidBuilder(text="Test", pattern=pb)
        self.assertIsNotNone(lb.pattern)
        self.assertEqual(lb.pattern.type, PatternType.GRID)

    def test_per_mode_override_mmu(self) -> None:
        """mmu_label overrides parent for MMU mode."""
        parent = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            mmu_label=LidBuilder(text="Cards", label_mode=LabelMode.FRAMELESS),
        )
        resolved = parent.resolve_for_mode("mmu")
        self.assertEqual(resolved.label_mode, LabelMode.FRAMELESS)
        self.assertEqual(resolved.text, "Cards")

    def test_per_mode_override_single(self) -> None:
        """single_label overrides parent for single mode."""
        parent = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            single_label=LidBuilder(text="CARDZ", label_mode=LabelMode.FRAMED),
        )
        resolved = parent.resolve_for_mode("single")
        self.assertEqual(resolved.text, "CARDZ")

    def test_no_override_falls_back(self) -> None:
        """Unset mode falls back to parent."""
        lb = LidBuilder(text="Cards", label_mode=LabelMode.FRAMED)
        self.assertIs(lb.resolve_for_mode("mmu"), lb)
        self.assertIs(lb.resolve_for_mode("single"), lb)

    def test_override_does_not_affect_other_mode(self) -> None:
        """MMU override leaves single mode unchanged."""
        lb = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            mmu_label=LidBuilder(label_mode=LabelMode.FRAMELESS),
        )
        self.assertEqual(lb.resolve_for_mode("mmu").label_mode, LabelMode.FRAMELESS)
        self.assertEqual(lb.resolve_for_mode("single").label_mode, LabelMode.FRAMED)
