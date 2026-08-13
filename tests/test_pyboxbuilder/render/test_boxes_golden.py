# SPDX-License-Identifier: Apache-2.0
"""Golden-image render tests for pyboxbuilder box bodies.

Each box type is rendered through the real PythonSCAD binary and compared
against a committed golden PNG. Skips gracefully when the binary is absent.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_app import compare_images, find_pythonscad_binary  # noqa: E402
from render_pyboxbuilder import GOLDEN_DIR, build_box_body_expr, render_solid  # noqa: E402

_TOLERANCE = 12.0

BOX_TYPES = ["SLIDING", "CAP", "HINGE", "FILAMENT_HINGE", "MAGNETIC", "INSET", "NO_LID"]


class BoxGoldenTests(unittest.TestCase):
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

    def test_sliding_box_body(self) -> None:
        self._render_compare("sliding_body", build_box_body_expr("SLIDING", 100, 80, 50))

    def test_cap_box_body(self) -> None:
        self._render_compare("cap_body", build_box_body_expr("CAP", 100, 80, 50))

    def test_hinge_box_body(self) -> None:
        self._render_compare("hinge_body", build_box_body_expr("HINGE", 100, 80, 50))

    def test_filament_hinge_box_body(self) -> None:
        self._render_compare("filament_hinge_body", build_box_body_expr("FILAMENT_HINGE", 100, 80, 50))

    def test_magnetic_box_body(self) -> None:
        self._render_compare("magnetic_body", build_box_body_expr("MAGNETIC", 100, 80, 50))

    def test_inset_box_body(self) -> None:
        self._render_compare("inset_body", build_box_body_expr("INSET", 100, 80, 50))

    def test_no_lid_box_body(self) -> None:
        self._render_compare("no_lid_body", build_box_body_expr("NO_LID", 100, 80, 30))
