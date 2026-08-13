# SPDX-License-Identifier: Apache-2.0
"""Generate golden images for the pyboxbuilder render tests.

Run from the repo root with the PythonSCAD binary present:
    python3 tests/test_pyboxbuilder/generate_golden.py

Writes PNGs to tests/test_pyboxbuilder/golden/ for every render test case.
Regenerate only when the reference geometry changes intentionally.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "render"))

from render_app import find_pythonscad_binary  # noqa: E402
from render_pyboxbuilder import GOLDEN_DIR, OUT_DIR, build_box_body_expr, render_solid  # noqa: E402

#: Box type → the dimensions its test renders at. These MUST match
#: tests/test_pyboxbuilder/render/test_boxes_golden.py, or the golden is of a
#: different box than the one being compared against it.
BOX_TYPES = {
    "SLIDING": (100, 80, 50),
    "CAP": (100, 80, 50),
    "HINGE": (100, 80, 50),
    "FILAMENT_HINGE": (100, 80, 50),
    "MAGNETIC": (100, 80, 50),
    "INSET": (100, 80, 50),
    "NO_LID": (100, 80, 30),
}

PATTERNS = {
    "pattern_hex_grid": (
        "from pyboxbuilder.enums import PatternType\n"
        "from pyboxbuilder.lid.pattern import build_pattern\n"
        "build_pattern(100, 70, 3.0, PatternType.HEX, spacing=10.0).show()\n"
    ),
    "pattern_voronoi": (
        "from pyboxbuilder.enums import PatternType\n"
        "from pyboxbuilder.lid.pattern import build_pattern\n"
        "build_pattern(100, 70, 3.0, PatternType.VORONOI, spacing=10.0).show()\n"
    ),
    "pattern_pentagon_r1": (
        "from pyboxbuilder.enums import PatternType\n"
        "from pyboxbuilder.lid.pattern import build_pattern\n"
        "build_pattern(100, 70, 3.0, PatternType.PENTAGON_R1, spacing=10.0).show()\n"
    ),
    "hex_grid_cutouts": (
        "from pyboxbuilder.compartments.hex_grid import HexGridSpec, build_hex_grid\n"
        "build_hex_grid(HexGridSpec(rows=3, cols=5, tile_width=40, height=10)).show()\n"
    ),
    "hex_grid_push_finger": (
        "from pyboxbuilder.compartments.hex_grid import HexGridSpec, build_hex_grid\n"
        "build_hex_grid(HexGridSpec(rows=2, cols=3, tile_width=40, height=10, "
        "push_block_height=3.0, finger_hole_diameter=10.0)).show()\n"
    ),
}


def main() -> None:
    binary = find_pythonscad_binary()
    if binary is None:
        print("PythonSCAD binary not found — set PYTHONSCAD_BIN")
        sys.exit(1)

    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)

    cases: dict[str, str] = {}
    for bt, (w, l, h) in BOX_TYPES.items():
        cases[f"{bt.lower()}_body"] = build_box_body_expr(bt, w, l, h)
    cases.update(PATTERNS)

    for name, expr in cases.items():
        result = render_solid(name, expr)
        if not result.ok:
            print(f"FAIL {name}: {result.error}")
            continue
        src = OUT_DIR / f"{name}.png"
        dst = GOLDEN_DIR / f"{name}.png"
        dst.write_bytes(src.read_bytes())
        print(f"OK {name} ({result.facets} facets)")


if __name__ == "__main__":
    main()
