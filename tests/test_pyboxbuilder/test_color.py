# SPDX-License-Identifier: Apache-2.0
"""Tests for Color type — pybosl2 webcolor name API."""

import unittest

from pyboxbuilder import Color


class ColorTests(unittest.TestCase):
    def test_webcolor_names(self) -> None:
        """pybosl2 Color supports webcolor name construction."""
        self.assertEqual(Color("red"), Color([1, 0, 0]))
        self.assertEqual(Color("white"), Color([1, 1, 1]))

    def test_list_constructor(self) -> None:
        c = Color([0.3, 0.4, 0.5])
        self.assertEqual(c.rgba, (0.3, 0.4, 0.5, 1.0))

    def test_alpha_property(self) -> None:
        c = Color([0.3, 0.4, 0.5])
        self.assertEqual(c.alpha, 1.0)

    def test_equality(self) -> None:
        self.assertEqual(Color([1, 0, 0]), Color("red"))
        self.assertNotEqual(Color([1, 0, 0]), Color("green"))
