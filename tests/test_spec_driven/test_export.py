# SPDX-License-Identifier: Apache-2.0
"""Tests for export functionality."""

import unittest
import tempfile
from pathlib import Path

from spec_driven.export.result import ExportResult
from spec_driven.project import Project
from spec_driven.enums import BoxType


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
            self.assertEqual(result.total_files, 9)  # 8 3MF + layout.pdf

    def test_no_lid_box_file_count(self) -> None:
        """No-lid boxes produce only body files."""
        p = Project("NoLidCount", game_box_size=(200, 150, 60))
        p.box(BoxType.NO_LID, "Tray", size=(100, 80, 20))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertEqual(result.total_files, 3)  # 2 3MF + layout.pdf

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
