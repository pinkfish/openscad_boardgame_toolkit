# SPDX-License-Identifier: Apache-2.0
"""Tests for the 1835 example — box layout and spacer accuracy."""

import math
import tempfile
import unittest

from pyboxbuilder import Project, BoxType, LabelMode, LidBuilder


class Test1835Layout(unittest.TestCase):
    def _build_project(self):
        box_width, box_length, box_height = 216, 298, 50
        wall, board_thickness = 2, 15
        main_height = box_height - board_thickness
        tile_radius = 40 / 2 / math.cos(math.radians(30))
        hex_box_width = tile_radius * 6 + wall * 2
        hex_box_length = box_width - 1
        hex_box_height = main_height / 4
        money_box_length = 98 + wall * 2
        shares_box_width = box_length - hex_box_width - money_box_length - 1
        shares_box_length = 66 * 2 + 3 * 2
        shares_height = main_height / 4
        middle_height = main_height - 9.5 - 8.5

        p = Project(
            "1835", game_box_size=(box_width, box_length, box_height),
            wall_thickness=wall, floor_thickness=wall, lid_thickness=wall,
            clearance_slack=0.0, board_thickness=board_thickness,
        )

        for i in range(4):
            p.box(BoxType.INSET, f"HexBox{i+1}",
                  size=(hex_box_length, hex_box_width, hex_box_height),
                  no_rotate=True, position=(0, money_box_length, i * hex_box_height),
                  lid=LidBuilder(text="Tiles"))
        for i in range(2):
            # Slipover: at 9.5mm and 8.5mm these are under the smallest cap box
            # that can carry a corner finger cutout, so a cap lid would have
            # nothing to push it off by.
            p.box(BoxType.SLIPOVER, f"MoneyBox{i+1}",
                  size=(215, money_box_length, 9.5 if i == 0 else 8.5),
                  no_rotate=True, position=(0, 0, i * 9.5),
                  lid=LidBuilder(text="Money"))
        for i in range(4):
            p.box(BoxType.SLIPOVER, f"ShareBox{i+1}",
                  size=(shares_box_length, shares_box_width, shares_height),
                  no_rotate=True,
                  position=(0, money_box_length + hex_box_width, i * shares_height),
                  lid=LidBuilder(text="Shares"))
        p.box(BoxType.CAP, "MiddleBox",
              size=(215, money_box_length, middle_height),
              no_rotate=True, position=(0, 0, 18),
              lid=LidBuilder(text="Tokens/Trains"))
        p.box(BoxType.SLIPOVER, "FirstPlayer",
              size=(box_width - shares_box_length - 1, shares_box_width, 24),
              no_rotate=True,
              position=(shares_box_length, money_box_length + hex_box_width, 0),
              lid=LidBuilder(text="First"))
        return p

    def test_exactly_one_spacer(self):
        """1835 produces exactly one spacer (matching the original SpacerBox)."""
        p = self._build_project()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            spacer_files = [f for f in result.written if "spacer" in f]
            self.assertEqual(len(spacer_files), 2)  # 1 spacer × (mmu + single)

    def test_all_12_boxes_exported(self):
        """All 12 boxes (4 hex, 2 money, 4 share, middle, first player) are exported."""
        p = self._build_project()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            labels = set()
            for f in result.written:
                for label in ("HexBox1", "HexBox4", "MoneyBox1", "MoneyBox2",
                              "ShareBox1", "ShareBox4", "MiddleBox", "FirstPlayer"):
                    if label in f:
                        labels.add(label)
            self.assertEqual(len(labels), 8)
