# SPDX-License-Identifier: Apache-2.0
"""Tests for Irish Gauge box sizes and spacer auto-generation."""

import unittest

from pyboxbuilder import Project, BoxType, LabelMode, LidBuilder


class IrishGaugeTests(unittest.TestCase):
    def _make_project(self):
        box_width = 214
        box_length = 302
        box_height = 39
        board_thickness = 10.5
        wall = 3
        card_length = 71

        company_box_width = box_width / 4
        company_box_length = card_length * 1.8 + wall * 2
        company_box_height = (box_height - board_thickness) / 2
        money_box_width = box_width
        money_box_length = card_length + wall * 2
        money_box_height = box_height - board_thickness

        p = Project(
            "IrishGauge",
            game_box_size=(box_width, box_length, box_height),
            wall_thickness=wall,
            lid_thickness=3,
        )
        return p, {
            "company_box_width": company_box_width,
            "company_box_length": company_box_length,
            "company_box_height": company_box_height,
            "money_box_width": money_box_width,
            "money_box_length": money_box_length,
            "money_box_height": money_box_height,
        }

    def test_box_sizes_derived_from_game_box(self):
        """Box sizes are computed from game box dimensions, not hardcoded."""
        p, d = self._make_project()

        # Company box = box_width/4 wide, card_length*1.8+2*wall long
        self.assertAlmostEqual(d["company_box_width"], 214 / 4)
        self.assertAlmostEqual(d["company_box_length"], 71 * 1.8 + 6)
        self.assertAlmostEqual(d["company_box_height"], (39 - 10.5) / 2)

        # Money box = box_width wide, card_length+2*wall long
        self.assertAlmostEqual(d["money_box_width"], 214)
        self.assertAlmostEqual(d["money_box_length"], 71 + 6)
        self.assertAlmostEqual(d["money_box_height"], 39 - 10.5)

    def test_export_with_spacers(self):
        """Export produces company boxes, money box, and auto-generated spacers."""
        import tempfile
        p, _ = self._make_project()

        money = p.box(
            BoxType.FILAMENT_HINGE, "MoneyBox",
            size=(214, 77, 28.5), no_rotate=True, position=(0, 0, 0),
            lid=LidBuilder(text="Bank"),
        )
        for denomination in ["1", "5", "10"]:
            money.compartment(denomination, size=(49, 67), depth=28.5)

        for i in range(5):
            p.box(
                BoxType.SLIDING, f"CompanyBox{i}",
                size=(53.5, 133.8, 14.25), no_rotate=True,
                position=((53.5 * i, 77, 0) if i < 3 else (53.5 * (i - 3), 77, 14.25)),
                lid=LidBuilder(text=f"Company{i}"),
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            spacer_files = [f for f in result.written if "spacer" in f]
            self.assertGreater(len(spacer_files), 0, "Expected auto-generated spacers")
            self.assertTrue(any("MoneyBox" in f for f in result.written))
            self.assertTrue(any("CompanyBox0" in f for f in result.written))
