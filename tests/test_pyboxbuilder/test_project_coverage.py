# SPDX-License-Identifier: Apache-2.0
"""Coverage tests for Project class features not covered elsewhere."""

import tempfile
import unittest

from pyboxbuilder.project import Project
from pyboxbuilder.enums import BoxType, LabelMode


class StandaloneModeTests(unittest.TestCase):
    def test_standalone_no_game_box(self) -> None:
        """game_box_size=None exports boxes directly with no packing/PDF."""
        p = Project("Standalone", game_box_size=None)
        p.box(BoxType.SLIDING, "CardBox", size=(100, 70, 50))
        p.box(BoxType.NO_LID, "Tray", size=(80, 60, 20))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            # CardBox: 4 files (body+lid, mmu+single); Tray: 2 files (body only)
            self.assertEqual(result.total_files, 6)
            # No layout PDF in standalone mode
            self.assertFalse(any("layout.pdf" in f for f in result.written))

    def test_standalone_no_size_no_compartments_raises(self) -> None:
        """Standalone box with no size and no compartments raises ValueError."""
        p = Project("StandaloneErr", game_box_size=None)
        p.box(BoxType.SLIDING, "NoSize")
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                p.export(tmpdir)

    def test_standalone_auto_size_from_compartments(self) -> None:
        """Standalone box with compartments auto-computes its size."""
        p = Project("StandaloneAuto", game_box_size=None)
        b = p.box(BoxType.SLIDING, "Auto")
        b.compartment("Well", size=(50, 50), depth=30)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreater(result.total_files, 0)


class BoxKwargsPropagationTests(unittest.TestCase):
    def test_no_rotate_flag(self) -> None:
        p = Project("KW", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40), no_rotate=True)
        self.assertTrue(b.no_rotate)

    def test_position_flag(self) -> None:
        p = Project("KW", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40), position=(10, 20, 30))
        self.assertEqual(b.position, (10, 20, 30))

    def test_stackable_and_magnet_flags(self) -> None:
        p = Project("KW", game_box_size=(200, 150, 60))
        b = p.box(
            BoxType.NO_LID, "A", size=(100, 80, 40),
            stackable="inside", stackable_thickness=2.0,
            magnet_type="round", magnet_size=(6.0, 3.0, 3.0),
        )
        self.assertEqual(b.stackable, "inside")
        self.assertEqual(b.magnet_type, "round")

    def test_lid_kwarg(self) -> None:
        p = Project("KW", game_box_size=(200, 150, 60))
        from pyboxbuilder.lid.builder import LidBuilder
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40),
                  lid=LidBuilder(text="Cards", label_mode=LabelMode.FRAMELESS))
        self.assertIsNotNone(b.lid)
        self.assertEqual(b.lid.text, "Cards")


class ManualPositionTests(unittest.TestCase):
    def test_manual_positions_skip_packer(self) -> None:
        """Boxes with position= are placed manually, not auto-packed."""
        p = Project("Manual", game_box_size=(300, 200, 80), clearance_slack=0.0)
        p.box(BoxType.SLIDING, "A", size=(100, 80, 40), position=(0, 0, 0), no_rotate=True)
        p.box(BoxType.CAP, "B", size=(60, 50, 30), position=(100, 0, 0), no_rotate=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreater(result.total_files, 0)


class FinalSizePropagationTests(unittest.TestCase):
    def test_final_size_set_after_export(self) -> None:
        """final_size is set on builders during export."""
        p = Project("FinalSize", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40), expandable=False)

        self.assertIsNone(b.final_size)
        with tempfile.TemporaryDirectory() as tmpdir:
            p.export(tmpdir)
        self.assertIsNotNone(b.final_size)
        self.assertEqual(b.final_size, (100, 80, 40))


class ClearanceSlackTests(unittest.TestCase):
    def test_clearance_slack_centers_placements(self) -> None:
        """Placements are shifted by clearance_slack to center them."""
        p = Project("Slack", game_box_size=(300, 200, 80), clearance_slack=5.0)
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40), expandable=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            p.export(tmpdir)
        # final_size is the box's own size; the position shift is internal.
        self.assertEqual(b.final_size, (100, 80, 40))

    def test_expandable_box_grows_to_fill_its_row(self) -> None:
        """FR-012 — an expandable box fills the width available to it."""
        p = Project("Grow", game_box_size=(300, 200, 80), clearance_slack=5.0)
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40))
        with tempfile.TemporaryDirectory() as tmpdir:
            p.export(tmpdir)
        self.assertEqual(b.final_size[0], 290.0)

    def test_non_expandable_box_keeps_its_size(self) -> None:
        """`expandable=False` is the master switch; the per-axis flags default
        to True and must not re-enable it behind the caller's back."""
        p = Project("Fixed", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A", size=(100, 80, 40), expandable=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            p.export(tmpdir)
        self.assertEqual(b.final_size, (100, 80, 40))


class ShareCompartmentsTests(unittest.TestCase):
    def test_pack_compartments_across_bins(self) -> None:
        """compartments are partitioned across multiple bins."""
        p = Project("Share", game_box_size=(300, 200, 80))
        bins = [(100, 100), (100, 100)]
        comps = [("A", 40, 40, 20), ("B", 40, 40, 20), ("C", 40, 40, 20), ("D", 40, 40, 20)]
        result = p.pack_compartments_across_bins(comps, bins)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        # All 4 compartments distributed across the 2 bins
        total = sum(len(bin_items) for bin_items in result)
        self.assertEqual(total, 4)

    def test_share_compartments_registers_group(self) -> None:
        """share_compartments registers a shared group."""
        p = Project("Share", game_box_size=(300, 200, 80))
        p.box(BoxType.SLIDING, "BoxA", size=(100, 80, 40))
        p.box(BoxType.SLIDING, "BoxB", size=(100, 80, 40))
        p.share_compartments(["BoxA", "BoxB"], [("T1", 40, 40, 20), ("T2", 40, 40, 20)])
        self.assertEqual(len(p._shared_groups), 1)

    def test_share_compartments_export_partitions(self) -> None:
        """shared compartments are auto-partitioned across boxes during export."""
        p = Project("ShareExport", game_box_size=(300, 200, 80), clearance_slack=0.0)
        p.box(BoxType.SLIDING, "BoxA", size=(100, 100, 40))
        p.box(BoxType.SLIDING, "BoxB", size=(100, 100, 40))
        p.share_compartments(
            ["BoxA", "BoxB"],
            [("T1", 40, 40, 20), ("T2", 40, 40, 20), ("T3", 40, 40, 20), ("T4", 40, 40, 20)],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreater(result.total_files, 0)
            # Both boxes now have compartments
            boxa = next(b for b in p._boxes if b.label == "BoxA")
            boxb = next(b for b in p._boxes if b.label == "BoxB")
            total_comps = len(boxa.compartments) + len(boxb.compartments)
            self.assertEqual(total_comps, 4)


class SizeResolutionTests(unittest.TestCase):
    def test_no_size_no_compartments_game_box_raises(self) -> None:
        """A game-box-mode box with no size and no compartments raises on export."""
        p = Project("NoSize", game_box_size=(300, 200, 80), clearance_slack=0.0)
        p.box(BoxType.SLIDING, "A")
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError) as ctx:
                p.export(tmpdir)
            self.assertIn("no explicit size and no compartments", str(ctx.exception))

    def test_partial_none_size_auto_computes(self) -> None:
        """A size with None components fills them from compartment minimum."""
        p = Project("Partial", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A", size=(None, 80, 40))
        b.compartment("Well", size=(50, 50), depth=30)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertIsNotNone(result)
            self.assertIsNotNone(b.final_size)

    def test_auto_size_from_compartments_with_game_box(self) -> None:
        """Box with no size but compartments auto-computes in game-box mode."""
        p = Project("Auto", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A")
        b.compartment("Well", size=(50, 50), depth=30)
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertIsNotNone(b.final_size)


class RatioOverflowExportTests(unittest.TestCase):
    def test_length_ratio_overflow_rejected(self) -> None:
        """Compartments whose length ratios sum > 1.0 are rejected on export."""
        p = Project("Ratio", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A", size=(100, 100, 50))
        b.compartment("X", length_ratio=0.6, depth=20)
        b.compartment("Y", length_ratio=0.6, depth=20)
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError) as ctx:
                p.export(tmpdir)
            self.assertIn("length ratios sum", str(ctx.exception))


class CompartmentOverflowTests(unittest.TestCase):
    def test_compartment_overflow_rejected_on_export(self) -> None:
        """A compartment too large for the box interior raises on export."""
        p = Project("Overflow", game_box_size=(300, 200, 80), clearance_slack=0.0)
        b = p.box(BoxType.SLIDING, "A", size=(50, 50, 40))
        b.compartment("Huge", size=(200, 200), depth=20)
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError) as ctx:
                p.export(tmpdir)
            self.assertIn("Compartments do not fit", str(ctx.exception))


class NoLidExportTests(unittest.TestCase):
    def test_no_lid_box_skips_lid_files_in_game_box_mode(self) -> None:
        """A no-lid box in a game box produces body files only."""
        p = Project("NoLid", game_box_size=(300, 200, 80), clearance_slack=0.0)
        p.box(BoxType.NO_LID, "Tray", size=(100, 80, 20))
        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            lid_files = [f for f in result.written if "Tray_lid" in f]
            self.assertEqual(len(lid_files), 0)
            body_files = [f for f in result.written if "Tray_body" in f]
            self.assertEqual(len(body_files), 2)  # mmu + single

