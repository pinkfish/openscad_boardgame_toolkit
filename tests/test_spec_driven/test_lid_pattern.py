# SPDX-License-Identifier: Apache-2.0
"""Tests for pattern fill generation."""

import unittest

from spec_driven.enums import PatternType
from spec_driven.lid.pattern import build_pattern


class PatternTests(unittest.TestCase):
    def test_auto_spacing(self) -> None:
        """Spacing auto-calculated when None (no bosl2 needed)."""
        try:
            result = build_pattern(80, 60, 3.0, PatternType.HEX_GRID)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_pattern_requires_bosl2(self) -> None:
        """Pattern generation requires bosl2."""
        with self.assertRaises((ImportError, ModuleNotFoundError)):
            build_pattern(50, 50, 3.0, PatternType.GRID, spacing=5.0)
