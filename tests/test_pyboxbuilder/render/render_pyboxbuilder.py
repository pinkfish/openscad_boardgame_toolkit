# SPDX-License-Identifier: Apache-2.0
"""Render helper for pyboxbuilder geometry — shells out to the full PythonSCAD binary.

The pyboxbuilder box/pattern/hex-grid geometry uses pybosl2, which only produces real
CSG inside PythonSCAD. These helpers render a pyboxbuilder solid to a PNG and report
whether geometry was produced, reusing tests/render_app.py's render_script.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tests"))

from render_app import render_script, RenderResult  # noqa: E402

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "golden"
OUT_DIR = Path(__file__).resolve().parent.parent / "_render_output"


def render_solid(name: str, body: str, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Render a pyboxbuilder solid expression to a PNG via PythonSCAD.

    Args:
        name: Base name for the output PNG (no extension).
        body: Python statements ending in `<solid>.show()`.
        imgsize: Output image size (width, height).

    Returns:
        RenderResult with ok/facets/error and image_path set on success.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_png = OUT_DIR / f"{name}.png"
    return render_script(body, out_png, imgsize=imgsize)


def build_box_body_expr(box_type: str, w: float, l: float, h: float) -> str:
    """Return the Python expression that builds and shows a box body.

    Args:
        box_type: The BoxType member name (e.g. "SLIDING", "CAP", "NO_LID").
        w, l, h: Box outer dimensions.

    Returns:
        A script string that renders the box body.
    """
    return (
        "from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY\n"
        "from pyboxbuilder.enums import BoxType\n"
        f"box = BOX_IMPL_REGISTRY[BoxType.{box_type}]()\n"
        f"spec = {{'width': {w}, 'length': {l}, 'height': {h}, "
        "'wall_thickness': 2.0, 'floor_thickness': 1.6, 'lid_thickness': 2.0}\n"
        "box.build_body(spec).show()\n"
    )
