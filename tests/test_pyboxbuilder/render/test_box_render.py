# SPDX-License-Identifier: Apache-2.0
"""Render tests for US1 — box geometry with compartments."""

import unittest

from pyboxbuilder.project import Project
from pyboxbuilder.enums import BoxType
from pyboxbuilder.box.interior import Interior


class BoxRenderTests(unittest.TestCase):
    def test_single_box_interior_dimensions(self) -> None:
        """Verify interior dimensions are correctly computed from box size."""
        wt = 2.0
        ft = 1.6
        lt = 2.0
        w, l, h = 200, 150, 60
        interior = Interior(
            width=w - 2 * wt,
            length=l - 2 * wt,
            height=h - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )
        self.assertEqual(interior.width, 196.0)
        self.assertEqual(interior.length, 146.0)
        self.assertEqual(interior.height, 56.4)
        self.assertTrue(interior.contains_compartment(90, 65))
        self.assertFalse(interior.contains_compartment(200, 10))

    def test_three_compartment_layout_fits(self) -> None:
        """Verify 3 compartments of specified sizes fit without overflow."""
        # Box 200x150mm interior, 3 compartments: 90x65, 80x65, 55x45
        interior = Interior(width=196, length=146, height=56)
        compartments = [
            ("DeckSlot", 90, 65, 45),
            ("DiscardSlot", 80, 65, 45),
            ("TokenTray", 55, 45, 25),
        ]
        from pyboxbuilder.compartments.layout import layout_compartments
        layout = layout_compartments(interior, compartments)
        self.assertFalse(layout.overflow, "Expected no overflow")
        self.assertEqual(len(layout.placements), 3)

    def test_compartment_overflow_detected(self) -> None:
        """Verify overflow is detected when compartments exceed interior."""
        interior = Interior(width=100, length=50, height=30)
        compartments = [("Huge", 120, 60, 20)]
        from pyboxbuilder.compartments.layout import layout_compartments
        layout = layout_compartments(interior, compartments)
        self.assertTrue(layout.overflow)

    def test_project_export_produces_files(self) -> None:
        """Verify export creates the expected directory structure."""
        import tempfile
        from pathlib import Path

        p = Project("RenderTest", game_box_size=(200, 150, 60))
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 50))
        p.box(BoxType.SLIDING, "Tokens", size=(60, 50, 30))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreaterEqual(result.total_files, 9)  # At least 8 3MF + 1 layout.pdf

            # Check mmu directory
            mmu_dir = Path(tmpdir) / "RenderTest" / "mmu"
            self.assertTrue((mmu_dir / "Cards_body.3mf").exists())
            self.assertTrue((mmu_dir / "Cards_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Tokens_body.3mf").exists())
            self.assertTrue((mmu_dir / "Tokens_lid.3mf").exists())

            # Check single directory
            single_dir = Path(tmpdir) / "RenderTest" / "single"
            self.assertTrue((single_dir / "Cards_body_single.3mf").exists())
            self.assertTrue((single_dir / "Cards_lid_single.3mf").exists())
            self.assertTrue((single_dir / "Tokens_body_single.3mf").exists())
            self.assertTrue((single_dir / "Tokens_lid_single.3mf").exists())
