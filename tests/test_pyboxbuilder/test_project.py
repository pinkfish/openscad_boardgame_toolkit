# SPDX-License-Identifier: Apache-2.0
"""Tests for Project constructor and box registration."""

import unittest
from pathlib import Path

from pyboxbuilder.project import Project
from pyboxbuilder.enums import BoxType


class ProjectTests(unittest.TestCase):
    def test_constructor_defaults(self) -> None:
        p = Project("TestGame", game_box_size=(200, 150, 60))
        self.assertEqual(p.name, "TestGame")
        self.assertEqual(p.game_box_size, (200, 150, 60))
        self.assertEqual(p.wall_thickness, 2.0)
        self.assertEqual(p.floor_thickness, 1.6)
        self.assertEqual(p.lid_thickness, 2.0)
        self.assertEqual(p.gap_threshold, 10.0)
        self.assertEqual(p.min_spacer_dim, 15.0)

    def test_add_box_sliding(self) -> None:
        p = Project("Test", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "Cards", size=(100, 70, 50))
        self.assertEqual(b.label, "Cards")
        self.assertEqual(b.size, (100, 70, 50))

    def test_add_box_without_size(self) -> None:
        p = Project("Test", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "AutoBox")
        self.assertIsNone(b.size)

    def test_export_empty_project(self) -> None:
        p = Project("Empty", game_box_size=(100, 100, 50))
        result = p.export("/tmp/test_output")
        self.assertEqual(result.written, ())
        self.assertEqual(result.skipped, ())
        self.assertEqual(result.total_files, 0)

    def test_export_with_box(self) -> None:
        p = Project("WithBox", game_box_size=(200, 150, 60))
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 50))
        result = p.export("/tmp/test_output")
        self.assertIsNotNone(result)
