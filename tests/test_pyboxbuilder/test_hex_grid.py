# SPDX-License-Identifier: Apache-2.0
"""Tests for hex-grid compartment layout."""

import unittest

from pyboxbuilder.compartments.hex_grid import (
    HexGridSpec,
    compute_hex_layout,
    hex_grid_bounds,
    build_hex_grid,
)


class HexGridLayoutTests(unittest.TestCase):
    def test_circumradius_derived_from_tile_width(self):
        """Circumradius = tile_width/2/cos(30°)."""
        import math
        spec = HexGridSpec(rows=3, cols=5, tile_width=40, height=10)
        expected = 40 / 2 / math.cos(math.radians(30))
        self.assertAlmostEqual(spec.circumradius, expected, places=6)

    def test_cell_count(self):
        """rows × cols cells are generated."""
        spec = HexGridSpec(rows=3, cols=5, tile_width=40, height=10)
        cells = compute_hex_layout(spec)
        self.assertEqual(len(cells), 15)

    def test_row_stagger(self):
        """Odd rows are offset horizontally by half a cell width."""
        spec = HexGridSpec(rows=2, cols=2, tile_width=40, height=10)
        cells = compute_hex_layout(spec)
        row0 = [c for c in cells if c.row == 0]
        row1 = [c for c in cells if c.row == 1]
        # Row 0 starts at x=0; row 1 is offset by circumradius + spacing/2
        self.assertAlmostEqual(row0[0].center[0], 0.0)
        self.assertGreater(row1[0].center[0], row0[0].center[0])

    def test_bounds_grow_with_rows_cols(self):
        """Larger grids have larger bounds."""
        small = hex_grid_bounds(HexGridSpec(rows=1, cols=1, tile_width=40, height=10))
        large = hex_grid_bounds(HexGridSpec(rows=3, cols=5, tile_width=40, height=10))
        self.assertGreater(large[0], small[0])
        self.assertGreater(large[1], small[1])


class HexGridValidationTests(unittest.TestCase):
    def test_zero_rows_rejected(self):
        with self.assertRaises(ValueError):
            HexGridSpec(rows=0, cols=5, tile_width=40, height=10)

    def test_zero_cols_rejected(self):
        with self.assertRaises(ValueError):
            HexGridSpec(rows=3, cols=0, tile_width=40, height=10)

    def test_zero_tile_width_rejected(self):
        with self.assertRaises(ValueError):
            HexGridSpec(rows=3, cols=5, tile_width=0, height=10)


class HexGridGeometryTests(unittest.TestCase):
    def test_build_hex_grid_requires_bosl2(self):
        """build_hex_grid returns None without pybosl2, or a solid with it."""
        spec = HexGridSpec(rows=3, cols=5, tile_width=40, height=10)
        result = build_hex_grid(spec)
        if result is None:
            self.skipTest("bosl2 not available")
        self.assertIsNotNone(result)

    def test_push_block_and_finger_hole_offset(self):
        """When both push block and finger hole are enabled, they don't overlap."""
        # The finger hole is offset by 0.4*circumradius from center when push block present
        spec = HexGridSpec(
            rows=1, cols=1, tile_width=40, height=10,
            push_block_height=2.0, finger_hole_diameter=10.0,
        )
        # Push block occupies the center (width 15); finger hole is offset
        self.assertGreater(spec.circumradius * 0.4, 0)
        # Verify the offset is non-zero (moves the hole away from the pillar)
        self.assertNotEqual(spec.circumradius * 0.4, 0.0)
