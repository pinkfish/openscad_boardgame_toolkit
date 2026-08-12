# SPDX-License-Identifier: Apache-2.0
"""Tests for Color dataclass."""

import unittest

from spec_driven.color import Color


class ColorTests(unittest.TestCase):
    def test_default_alpha(self) -> None:
        c = Color(0.5, 0.5, 0.5)
        self.assertEqual(c.a, 1.0)

    def test_named_presets(self) -> None:
        self.assertEqual(Color.WHITE(), Color(1.0, 1.0, 1.0))
        self.assertEqual(Color.BLACK(), Color(0.0, 0.0, 0.0))
        self.assertEqual(Color.RED(), Color(1.0, 0.0, 0.0))
        self.assertEqual(Color.GREEN(), Color(0.0, 1.0, 0.0))
        self.assertEqual(Color.BLUE(), Color(0.0, 0.0, 1.0))
        self.assertEqual(Color.GOLD(), Color(0.9, 0.7, 0.1))

    def test_frozen(self) -> None:
        c = Color(1, 0, 0)
        with self.assertRaises(Exception):
            c.r = 0.5  # type: ignore[misc]

    def test_custom_alpha(self) -> None:
        c = Color(0.3, 0.4, 0.5, a=0.8)
        self.assertEqual(c.a, 0.8)

    def test_iterable(self) -> None:
        c = Color(0.1, 0.2, 0.3, 0.9)
        self.assertEqual(tuple(c), (0.1, 0.2, 0.3, 0.9))
