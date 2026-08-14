# SPDX-License-Identifier: Apache-2.0
"""Tests for pyboxbuilder enums."""

import unittest

from pyboxbuilder.enums import (
    BoxType, LabelMode, MagnetType, PatternType, ScoopSide, StackableMode,
)
from pyboxbuilder.project import Project


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


class StackableAndMagnetEnumTests(unittest.TestCase):
    """T259–T261: type selections are enums, never bare strings."""

    def test_stackable_members(self) -> None:
        self.assertEqual({m.name for m in StackableMode}, {"INSIDE", "OUTSIDE"})
        self.assertEqual(StackableMode.INSIDE.value, "inside")
        self.assertEqual(StackableMode.OUTSIDE.value, "outside")

    def test_magnet_members(self) -> None:
        self.assertEqual({m.name for m in MagnetType}, {"NONE", "ROUND", "RECT"})

    def test_builder_accepts_the_enums(self) -> None:
        p = Project("EnumTest")
        box = p.box(
            BoxType.NO_LID, "Hex", size=(40, 40, 20),
            stackable=StackableMode.OUTSIDE, magnet_type=MagnetType.RECT,
        )
        self.assertIs(box.stackable, StackableMode.OUTSIDE)
        self.assertIs(box.magnet_type, MagnetType.RECT)

    def test_builder_defaults_are_none(self) -> None:
        p = Project("EnumTest")
        box = p.box(BoxType.NO_LID, "Plain", size=(40, 40, 20))
        self.assertIsNone(box.stackable)
        self.assertIsNone(box.magnet_type)

    def test_bare_string_is_rejected(self) -> None:
        p = Project("EnumTest")
        for field, value in (("stackable", "inside"), ("magnet_type", "round")):
            with self.subTest(field=field):
                with self.assertRaises(TypeError) as caught:
                    p.box(BoxType.NO_LID, "Hex", size=(40, 40, 20), **{field: value})
                message = str(caught.exception)
                self.assertIn("Hex", message)      # names the box
                self.assertIn(field, message)      # names the field
                self.assertIn(value, message)      # shows what was passed

    def test_geometry_reads_the_enum(self) -> None:
        """A stackable box with magnets must differ from a plain one."""
        from pyboxbuilder.box.types.no_lid import NoLidBox

        base = dict(label="Hex", width=40, length=40, height=20,
                    wall_thickness=2.0, floor_thickness=2.0, lid_thickness=0.0)
        plain = repr(NoLidBox().build_body(dict(base)))
        featured = repr(NoLidBox().build_body(
            dict(base, stackable=StackableMode.INSIDE, magnet_type=MagnetType.ROUND,
                 magnet_size=(6, 6, 3))
        ))
        self.assertNotEqual(plain, featured)

    def test_magnet_none_means_no_magnets(self) -> None:
        from pyboxbuilder.box.types.no_lid import NoLidBox

        base = dict(label="Hex", width=40, length=40, height=20,
                    wall_thickness=2.0, floor_thickness=2.0, lid_thickness=0.0)
        plain = repr(NoLidBox().build_body(dict(base)))
        explicit_none = repr(NoLidBox().build_body(dict(base, magnet_type=MagnetType.NONE)))
        self.assertEqual(plain, explicit_none)
