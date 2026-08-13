# SPDX-License-Identifier: Apache-2.0
"""Tests for box type registry and all 12 box types."""

import unittest

from pyboxbuilder.enums import BoxType
from pyboxbuilder.box.registry import BOX_TYPE_REGISTRY, BOX_IMPL_REGISTRY
from pyboxbuilder.project import Project


class BoxRegistryTests(unittest.TestCase):
    def test_all_box_types_registered(self) -> None:
        for bt in BoxType:
            self.assertIn(bt, BOX_TYPE_REGISTRY, f"{bt} not in BOX_TYPE_REGISTRY")
            self.assertIn(bt, BOX_IMPL_REGISTRY, f"{bt} not in BOX_IMPL_REGISTRY")

    def test_registry_returns_correct_builder_class(self) -> None:
        from pyboxbuilder.builders.sliding import SlidingBoxBuilder
        from pyboxbuilder.builders.cap import CapBoxBuilder
        from pyboxbuilder.builders.hinge import HingeBoxBuilder
        from pyboxbuilder.builders.filament_hinge import FilamentHingeBoxBuilder
        from pyboxbuilder.builders.magnetic import MagneticBoxBuilder
        from pyboxbuilder.builders.no_lid import NoLidBoxBuilder

        self.assertIs(BOX_TYPE_REGISTRY[BoxType.SLIDING], SlidingBoxBuilder)
        self.assertIs(BOX_TYPE_REGISTRY[BoxType.CAP], CapBoxBuilder)
        self.assertIs(BOX_TYPE_REGISTRY[BoxType.HINGE], HingeBoxBuilder)
        self.assertIs(
            BOX_TYPE_REGISTRY[BoxType.FILAMENT_HINGE], FilamentHingeBoxBuilder
        )
        self.assertIs(BOX_TYPE_REGISTRY[BoxType.MAGNETIC], MagneticBoxBuilder)
        self.assertIs(BOX_TYPE_REGISTRY[BoxType.NO_LID], NoLidBoxBuilder)

    def test_all_box_types_exportable(self) -> None:
        """Verify all 12 box types can be added and exported."""
        import tempfile

        p = Project("AllTypes", game_box_size=(500, 500, 100))

        types_and_builders = [
            (BoxType.SLIDING, {}),
            (BoxType.CAP, {"cap_height": 8.0}),
            (BoxType.HINGE, {"hinge_count": 3}),
            (BoxType.FILAMENT_HINGE, {"hinge_gap": 0.4}),
            (BoxType.MAGNETIC, {"magnet_diameter": 6.0}),
            (BoxType.INSET, {}),
            (BoxType.SLIDING_CATCH, {}),
            (BoxType.SLIPOVER, {}),
            (BoxType.SLIPOVER_PATH, {}),
            (BoxType.CAP_PATH, {}),
            (BoxType.NO_LID, {}),
            (BoxType.CARD_LIBRARY, {}),
        ]

        for bt, kwargs in types_and_builders:
            label = f"Box_{bt.name}"
            b = p.box(bt, label, size=(100, 80, 40), **kwargs)
            self.assertEqual(b.label, label)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            # All boxes except NO_LID have lid files
            self.assertGreater(result.total_files, 0)

    def test_no_lid_box_skips_lid_files(self) -> None:
        """Verify no-lid boxes don't produce lid 3MF files."""
        import tempfile
        from pathlib import Path

        p = Project("NoLidTest", game_box_size=(200, 150, 60))
        p.box(BoxType.NO_LID, "Tray", size=(100, 80, 20))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreaterEqual(result.total_files, 3)  # At least 2 3MF + layout.pdf

            mmu_dir = Path(tmpdir) / "NoLidTest" / "mmu"
            self.assertTrue((mmu_dir / "Tray_body.3mf").exists())
            self.assertFalse((mmu_dir / "Tray_lid.3mf").exists())

    def test_type_specific_fields_propagated(self) -> None:
        """Verify type-specific builder fields are accessible."""
        p = Project("TestTypes", game_box_size=(300, 200, 80))

        sliding = p.box(
            BoxType.SLIDING, "S", size=(100, 80, 50), two_layer=True
        )
        self.assertTrue(sliding.two_layer)  # type: ignore[attr-defined]

        mag = p.box(
            BoxType.MAGNETIC, "M", size=(100, 80, 50),
            magnet_diameter=8.0, magnet_count_width=3,
        )
        self.assertEqual(mag.magnet_diameter, 8.0)  # type: ignore[attr-defined]
        self.assertEqual(mag.magnet_count_width, 3)  # type: ignore[attr-defined]
