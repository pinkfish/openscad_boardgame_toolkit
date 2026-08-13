# SPDX-License-Identifier: Apache-2.0
"""Tests for pyboxbuilder enums."""

import unittest

from pyboxbuilder.enums import BoxType, LabelMode, PatternType, ScoopSide


class EnumTests(unittest.TestCase):
    def test_box_type_has_all_members(self) -> None:
        types = {t for t in BoxType}
        self.assertIn(BoxType.SLIDING, types)
        self.assertIn(BoxType.CAP, types)
        self.assertIn(BoxType.HINGE, types)
        self.assertIn(BoxType.FILAMENT_HINGE, types)
        self.assertIn(BoxType.MAGNETIC, types)
        self.assertIn(BoxType.INSET, types)
        self.assertIn(BoxType.SLIDING_CATCH, types)
        self.assertIn(BoxType.SLIPOVER, types)
        self.assertIn(BoxType.SLIPOVER_PATH, types)
        self.assertIn(BoxType.CAP_PATH, types)
        self.assertIn(BoxType.NO_LID, types)
        self.assertIn(BoxType.CARD_LIBRARY, types)

    def test_box_type_values_are_strings(self) -> None:
        for bt in BoxType:
            self.assertIsInstance(bt.value, str)

    def test_label_mode_values(self) -> None:
        self.assertEqual(LabelMode.FRAMED.value, "framed")
        self.assertEqual(LabelMode.FRAMELESS.value, "frameless")

    def test_pattern_type_values(self) -> None:
        self.assertEqual(PatternType.HEX_GRID.value, "hex_grid")
        self.assertEqual(PatternType.GRID.value, "grid")
        self.assertEqual(PatternType.VORONOI.value, "voronoi")

    def test_scoop_side_values(self) -> None:
        self.assertEqual(ScoopSide.FRONT.value, "front")
        self.assertEqual(ScoopSide.BACK.value, "back")
        self.assertEqual(ScoopSide.LEFT.value, "left")
        self.assertEqual(ScoopSide.RIGHT.value, "right")
