# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: tests/render_flags.py
#    Render one flags.py expression through the real PythonSCAD binary -- the flags analogue
#    of render_shapes.py. flags.py builds finished multi-colour solids rather than 2-D
#    outlines, so unlike the shapes harness these expressions are NOT extruded by the caller.
#
# FileSummary: Render harness for flags.py expressions.
# FileGroup: Tests

from __future__ import annotations

from pathlib import Path

from render_app import RenderResult, render_script
from render_cap_box import find_bosl2_scad_dir

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def render_flag(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Render a single flags.py expression, e.g. ``"SwedenFlag(60, 40)"``.

    *expr* is evaluated with flags.py's public names (and pythonscad's native primitives)
    already imported, and the project root on sys.path.

    Args:
        expr: the flags.py expression to build and show
        out_png: where to write the rendered image
        imgsize: render size in pixels

    Returns:
        The :class:`RenderResult` from the render.

    Raises:
        FileNotFoundError: If no working BOSL2 dir is found -- callers should check
            find_bosl2_scad_dir() first and skip gracefully, the same pattern the other
            render helpers use.

    """
    bosl2_dir = find_bosl2_scad_dir()
    if bosl2_dir is None:
        raise FileNotFoundError(
            "no working BOSL2/std.scad found for PythonSCAD (set BOSL2_SCAD_DIR; see "
            "render_cap_box.py's module docstring for how to create a patched copy)"
        )
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "from pythonscad import *\n"
        "from base_bgtk import *\n"
        "from flags import *\n"
        "from pybosl2 import shapes3d\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    # The Portuguese flag alone is ~800 lines of traced bezier outlines stroked into geometry,
    # so these need more than render_script()'s 60s default.
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir, timeout=300)
