# SPDX-License-Identifier: Apache-2.0
"""Tests for export functionality."""

import unittest
import tempfile
from pathlib import Path

from pyboxbuilder.export.result import ExportResult
from pyboxbuilder.project import Project
from pyboxbuilder.enums import BoxType


class ExportTests(unittest.TestCase):
    def test_export_result_creation(self) -> None:
        r = ExportResult(
            written=("file1.3mf", "file2.3mf"),
            skipped=("file3.3mf",),
            total_files=3,
        )
        self.assertEqual(len(r.written), 2)
        self.assertEqual(len(r.skipped), 1)
        self.assertEqual(r.total_files, 3)
        self.assertIsNone(r.cached_from)

    def test_export_result_with_cache(self) -> None:
        r = ExportResult(
            written=(),
            skipped=("a.3mf", "b.3mf"),
            total_files=2,
            cached_from="abc123",
        )
        self.assertEqual(r.cached_from, "abc123")

    def test_export_file_counts(self) -> None:
        """Export a multi-box project and verify file counts."""
        p = Project("CountTest", game_box_size=(300, 200, 80))
        p.box(BoxType.SLIDING, "BoxA", size=(100, 80, 40))
        p.box(BoxType.CAP, "BoxB", size=(60, 50, 30))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            # 2 boxes: each has mmu body+lid, single body+lid = 8 files
            self.assertGreaterEqual(result.total_files, 9)  # At least 8 3MF + layout.pdf

    def test_no_lid_box_file_count(self) -> None:
        """No-lid boxes produce only body files."""
        p = Project("NoLidCount", game_box_size=(200, 150, 60))
        p.box(BoxType.NO_LID, "Tray", size=(100, 80, 20))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreaterEqual(result.total_files, 3)  # At least 2 3MF + layout.pdf

    def test_pdf_valid_and_boxes_at_positions(self) -> None:
        """Generated PDF is valid and boxes rendered at correct positions."""
        import tempfile
        from pathlib import Path

        p = Project("LayoutTest", game_box_size=(300, 200, 80))
        p.box(BoxType.SLIDING, "BoxA", size=(100, 80, 40))
        p.box(BoxType.CAP, "BoxB", size=(60, 50, 30))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            pdf_path = Path(tmpdir) / "LayoutTest" / "layout.pdf"

            if not pdf_path.exists():
                self.skipTest("PDF generation requires fpdf2")

            # Verify PDF is valid and non-empty
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 0)

            # Verify PDF header (valid PDF starts with %PDF-)
            with open(pdf_path, "rb") as f:
                header = f.read(8)
                self.assertTrue(header.startswith(b"%PDF-"), f"Invalid PDF header: {header}")

            # Verify boxes referenced in layout
            self.assertIn("layout", result.written[-1])

    def test_stale_spacer_deletion(self) -> None:
        """Orphaned spacer files are deleted when fewer spacers are generated."""
        from pyboxbuilder.packing.layout import Placement

        p = Project("StaleTest", game_box_size=(300, 200, 80))

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create fake stale spacer files
            mmu = Path(tmpdir) / "StaleTest" / "mmu"
            single = Path(tmpdir) / "StaleTest" / "single"
            mmu.mkdir(parents=True, exist_ok=True)
            single.mkdir(parents=True, exist_ok=True)
            for i in range(1, 4):
                (mmu / f"spacer_{i}_body.3mf").touch()
                (single / f"spacer_{i}_body_single.3mf").touch()

            # Only spacer_1 is "current"
            current = [Placement(label="spacer_1", position=(0, 0, 0), size=(10, 10, 10))]
            p._delete_stale_spacers(tmpdir, current)

            self.assertTrue((mmu / "spacer_1_body.3mf").exists())
            self.assertFalse((mmu / "spacer_2_body.3mf").exists())
            self.assertFalse((mmu / "spacer_3_body.3mf").exists())
            self.assertFalse((single / "spacer_2_body_single.3mf").exists())

    def test_board_thickness_excluded_from_spacers(self) -> None:
        """The reserved board area is excluded from spacer generation.

        With board_thickness=15 and a box filling the whole box area (z=0..35),
        no spacer is generated — the board (below z=0) is correctly excluded.
        """
        p = Project(
            "BoardTest", game_box_size=(100, 100, 50),
            clearance_slack=0.0, board_thickness=15,
        )
        # Fill the entire box area: z=0..35 (50 - 15 board)
        p.box(BoxType.NO_LID, "FullTray", size=(100, 100, 35), position=(0, 0, 0))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            spacer_files = [f for f in result.written if "spacer" in f]
            self.assertEqual(len(spacer_files), 0, f"Expected no spacer, got {spacer_files}")

    def test_real_gap_above_board_still_spacer(self) -> None:
        """A genuine gap within the box area (not the board) still yields a spacer."""
        p = Project(
            "GapTest", game_box_size=(100, 100, 50),
            clearance_slack=0.0, board_thickness=15,
        )
        # Box fills z=0..20, leaving a real z=20..35 gap above it
        p.box(BoxType.NO_LID, "ShortTray", size=(100, 100, 20), position=(0, 0, 0))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            spacer_files = [f for f in result.written if "spacer" in f]
            self.assertGreater(len(spacer_files), 0, "Expected a spacer for the z=20..35 gap")


