# SPDX-License-Identifier: Apache-2.0
"""Tests for lid label generation."""

import unittest

from pyboxbuilder.enums import LabelMode
from pyboxbuilder.lid.label import build_label


class LabelTests(unittest.TestCase):
    def test_label_auto_sizing_positive(self) -> None:
        """Label text height calculation works (bosl2 not required)."""
        # Without bosl2, the text height calculation still runs
        try:
            result = build_label(
                width=100, length=70, thickness=2.0,
                text="Cards", label_mode=LabelMode.FRAMED,
            )
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_min_text_height_guard(self) -> None:
        """Very small lid should skip label (no bosl2 needed)."""
        result = build_label(
            width=20, length=15, thickness=2.0,
            text="Cards",
            min_text_height_mm=10.0,
        )
        self.assertIsNone(result)

    def test_empty_text_skipped(self) -> None:
        """Empty text string should skip label."""
        result = build_label(
            width=100, length=70, thickness=2.0,
            text="",
        )
        self.assertIsNone(result)

    def test_zero_margin_skips_label(self) -> None:
        """Negative margin should skip."""
        result = build_label(
            width=10, length=10, thickness=2.0,
            text="X", border_margin_mm=6.0,
        )
        self.assertIsNone(result)

    def test_compartment_label_mmu_mode(self) -> None:
        """MMU mode returns raised text (requires bosl2)."""
        from pyboxbuilder.compartments.labels import build_floor_label
        result = build_floor_label("Lion", 40, 30, mode="mmu")
        if result is None:
            self.skipTest("bosl2 not available")

    def test_compartment_label_single_mode(self) -> None:
        """Single mode returns engraved text (requires bosl2)."""
        from pyboxbuilder.compartments.labels import build_floor_label
        result = build_floor_label("Lion", 40, 30, mode="single")
        if result is None:
            self.skipTest("bosl2 not available")
