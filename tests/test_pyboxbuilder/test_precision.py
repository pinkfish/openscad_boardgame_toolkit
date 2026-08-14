# SPDX-License-Identifier: Apache-2.0
"""Tests for curve precision — the fn/fa/fs controls (T244–T246).

The assertions read the OpenSCAD a solid emits (``$fn``/``$fa``/``$fs``),
which is the value that actually decides the facet count at render time.
"""

import ast
import pathlib
import re
import unittest

from pyboxbuilder.compartments.finger_hole import build_wall_scoop
from pyboxbuilder.compartments.hex_grid import HexGridSpec, build_hex_grid
from pyboxbuilder.enums import PatternType, ScoopSide
from pyboxbuilder.lid.pattern import build_pattern
from pyboxbuilder.precision import (
    DEFAULT_FA,
    DEFAULT_FS,
    Precision,
    kwargs,
    precision,
    use,
)

PYBOXBUILDER = pathlib.Path(__file__).resolve().parents[2] / "pyboxbuilder"


def emitted(solid) -> str:
    """The OpenSCAD source a solid renders to."""
    return repr(solid)


def fn_values(solid) -> set[str]:
    """Every ``$fn`` value appearing in a solid's emitted source."""
    return set(re.findall(r"\$fn\s*=\s*([0-9.]+)", emitted(solid)))


class PrecisionValueTests(unittest.TestCase):
    def test_defaults(self) -> None:
        self.assertIsNone(precision().fn)
        self.assertEqual(precision().fa, DEFAULT_FA)
        self.assertEqual(precision().fs, DEFAULT_FS)
        self.assertEqual(DEFAULT_FA, 12.0)
        self.assertEqual(DEFAULT_FS, 2.0)

    def test_kwargs_omit_fn_when_unset(self) -> None:
        self.assertEqual(kwargs(), {"fa": 12.0, "fs": 2.0})

    def test_kwargs_include_fn_when_set(self) -> None:
        with use(fn=64):
            self.assertEqual(kwargs(), {"fa": 12.0, "fs": 2.0, "fn": 64})

    def test_use_leaves_unspecified_settings_alone(self) -> None:
        with use(fa=6):
            with use(fn=32):
                self.assertEqual(precision(), Precision(fn=32, fa=6.0, fs=2.0))

    def test_context_is_restored_on_exit(self) -> None:
        with use(fn=8):
            pass
        self.assertIsNone(precision().fn)

    def test_context_is_restored_after_an_exception(self) -> None:
        with self.assertRaises(RuntimeError):
            with use(fn=8):
                raise RuntimeError("boom")
        self.assertIsNone(precision().fn)

    def test_out_of_range_rejected(self) -> None:
        for bad in (dict(fn=2), dict(fa=0), dict(fs=-1)):
            with self.subTest(**bad), self.assertRaises(ValueError):
                with use(**bad):
                    pass


class PrecisionReachesGeometryTests(unittest.TestCase):
    """An explicit fn must reach every curved feature, not just some."""

    def scoop(self):
        return build_wall_scoop(
            comp_width=40, comp_length=30, comp_depth=20, side=ScoopSide.FRONT, radius=10,
        )

    def pattern(self):
        return build_pattern(
            width=40, length=40, thickness=2, pattern_type=PatternType.CIRCLE,
        )

    def test_finger_scoop(self) -> None:
        with use(fn=37):
            self.assertIn("37", fn_values(self.scoop()))

    def test_hex_cell_finger_hole(self) -> None:
        spec = HexGridSpec(rows=2, cols=2, tile_width=20, height=10,
                           finger_hole_diameter=6)
        with use(fn=41):
            self.assertIn("41", fn_values(build_hex_grid(spec)))

    def test_lid_pattern(self) -> None:
        with use(fn=29):
            self.assertIn("29", fn_values(self.pattern()))

    def test_default_emits_fa_and_fs_not_fn(self) -> None:
        source = emitted(self.scoop())
        self.assertIn("$fa = 12", source)
        self.assertIn("$fs = 2", source)

    def test_two_precisions_produce_different_geometry(self) -> None:
        with use(fn=8):
            coarse = emitted(self.pattern())
        with use(fn=64):
            fine = emitted(self.pattern())
        self.assertNotEqual(coarse, fine)


class NoHardcodedFacetsTests(unittest.TestCase):
    """No module may pin a facet count the caller cannot override."""

    def test_no_literal_fn_in_library_code(self) -> None:
        offenders = []
        for path in PYBOXBUILDER.rglob("*.py"):
            # tesselations/ and shapes/ are borrowed algorithm libraries whose
            # segment counts are shape parameters, not curve precision.
            if path.name == "precision.py" or path.parts[-2] in ("tesselations", "shapes"):
                continue
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                if re.search(r"\bfn\s*=\s*\d+", line) or "$fn" in line:
                    offenders.append(f"{path.relative_to(PYBOXBUILDER)}:{number}: {line.strip()}")
        self.assertEqual(offenders, [], "hardcoded facet counts:\n" + "\n".join(offenders))

    def test_every_curve_call_site_takes_the_precision(self) -> None:
        """cylinder/sphere calls in box, compartment and lid code pass it."""
        offenders = []
        for folder in ("box", "compartments", "lid"):
            for path in (PYBOXBUILDER / folder).rglob("*.py"):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    if not (isinstance(node.func, ast.Name) and node.func.id in ("cylinder", "sphere")):
                        continue
                    if not any(_is_precision_splat(kw) for kw in node.keywords):
                        offenders.append(
                            f"{path.relative_to(PYBOXBUILDER)}:{node.lineno}: {node.func.id}(...)"
                        )
        self.assertEqual(offenders, [], "curve calls without precision:\n" + "\n".join(offenders))


def _is_precision_splat(keyword: ast.keyword) -> bool:
    """True for a ``**precision_kwargs()`` argument."""
    return (
        keyword.arg is None
        and isinstance(keyword.value, ast.Call)
        and isinstance(keyword.value.func, ast.Name)
        and keyword.value.func.id == "precision_kwargs"
    )


if __name__ == "__main__":
    unittest.main()
