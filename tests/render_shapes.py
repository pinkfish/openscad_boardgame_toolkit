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

# LibFile: tests/render_shapes.py
#    Helper for rendering shapes.py/tesselations.py/shapes3d.py shapes with the *real*
#    PythonSCAD binary. Same shape as tests/render_cap_box.py (these modules also call
#    `osuse("BOSL2/std.scad")` at import time, so they need the same PYTHONSCAD_BIN /
#    BOSL2_SCAD_DIR fixups -- see render_cap_box.py's module docstring for why and how).
#    One shared helper for all three modules since their expressions get evaluated with the
#    same scope (everything star-imported).
#
# FileGroup: shapes

from __future__ import annotations

from pathlib import Path

from render_cap_box import find_bosl2_scad_dir
from render_app import RenderResult, render_script

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def render_shapes_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single shapes.py/tesselations.py/shapes3d.py expression,
    e.g. `"sword2d(70, 20).linear_extrude(height=2)"` (2-D shapes should be extruded so the
    render camera has a solid to frame). `expr` is evaluated with all three modules'
    public names and pythonscad's native primitives already imported into scope, and the
    project root already on sys.path.

    Raises FileNotFoundError if no working BOSL2 dir is found -- callers should check
    find_bosl2_scad_dir() first and skip gracefully, same pattern as find_pythonscad_binary().
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
        "from shapes import *\n"
        "from tesselations import *\n"
        "from shapes3d import *\n"
        "from pentagon_tilings import *\n"
        "from penrose_tiling import *\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    # Same rationale as render_no_lid.py: SDF solids (after migration) mesh slower than plain
    # CSG, so give them room rather than inheriting render_script()'s 60s default.
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir, timeout=300)
