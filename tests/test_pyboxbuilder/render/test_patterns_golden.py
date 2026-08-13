# SPDX-License-Identifier: Apache-2.0
"""Golden-image render tests for pyboxbuilder lid patterns and hex grids."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_app import compare_images, find_pythonscad_binary  # noqa: E402
from render_pyboxbuilder import GOLDEN_DIR, render_solid  # noqa: E402

_TOLERANCE = 12.0


class PatternGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.binary = find_pythonscad_binary()

    def _render_compare(self, name: str, expr: str) -> None:
        if self.binary is None:
            self.skipTest("no PythonSCAD binary (set PYTHONSCAD_BIN)")
        result = render_solid(name, expr)
        if not result.ok:
            self.skipTest(f"render produced no geometry: {result.error}")
        golden = GOLDEN_DIR / f"{name}.png"
        if not golden.exists():
            self.skipTest(f"no golden image for {name} (run generate_golden.py)")
        diff = compare_images(result.image_path, golden)
        self.assertLessEqual(diff, _TOLERANCE, f"{name} differs from golden by {diff:.1f}")

    def test_hex_grid_pattern(self) -> None:
        self._render_compare(
            "pattern_hex_grid",
            "from pyboxbuilder.enums import PatternType\n"
            "from pyboxbuilder.lid.pattern import build_pattern\n"
            "build_pattern(100, 70, 3.0, PatternType.HEX, spacing=10.0).show()\n",
        )

    def test_voronoi_pattern(self) -> None:
        self._render_compare(
            "pattern_voronoi",
            "from pyboxbuilder.enums import PatternType\n"
            "from pyboxbuilder.lid.pattern import build_pattern\n"
            "build_pattern(100, 70, 3.0, PatternType.VORONOI, spacing=10.0).show()\n",
        )

    def test_pentagon_tiling(self) -> None:
        self._render_compare(
            "pattern_pentagon_r1",
            "from pyboxbuilder.enums import PatternType\n"
            "from pyboxbuilder.lid.pattern import build_pattern\n"
            "build_pattern(100, 70, 3.0, PatternType.PENTAGON_R1, spacing=10.0).show()\n",
        )

    def test_hex_grid_cutouts(self) -> None:
        self._render_compare(
            "hex_grid_cutouts",
            "from pyboxbuilder.compartments.hex_grid import HexGridSpec, build_hex_grid\n"
            "build_hex_grid(HexGridSpec(rows=3, cols=5, tile_width=40, height=10)).show()\n",
        )

    def test_hex_grid_push_block_finger_hole(self) -> None:
        self._render_compare(
            "hex_grid_push_finger",
            "from pyboxbuilder.compartments.hex_grid import HexGridSpec, build_hex_grid\n"
            "build_hex_grid(HexGridSpec(rows=2, cols=3, tile_width=40, height=10, "
            "push_block_height=3.0, finger_hole_diameter=10.0)).show()\n",
        )
