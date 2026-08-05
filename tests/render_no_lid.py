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

# LibFile: tests/render_no_lid.py
#    Helper for rendering no_lid.py shapes with the *real* PythonSCAD binary. Same shape as
#    tests/render_cap_box.py (no_lid.py also calls `osuse("BOSL2/std.scad")` at import time, so
#    it needs the same PYTHONSCAD_BIN / BOSL2_SCAD_DIR fixups -- see render_cap_box.py's module
#    docstring for why and how).
#
# FileGroup: no_lid

from __future__ import annotations

from pathlib import Path

from render_cap_box import find_bosl2_scad_dir
from render_app import RenderResult, render_script

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def render_no_lid_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single no_lid.py expression, e.g.
    `"MakeBoxWithNoLid([80.0, 60.0, 20.0])"`. `expr` is evaluated with no_lid's/base_bgtk's
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
        "import types\n"
        f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "from pythonscad import *\n"
        "from base_bgtk import *\n"
        "from no_lid import *\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    # These SDF-swept boxes mesh slower than plain CSG -- a concave outline in particular uses
    # the winding-number polygon form (one atan2 per path segment per evaluation; see
    # pysolidfive._polygon_sdf_xy), which has hit ~100s for a hollow concave box. Give them
    # room rather than inheriting render_script()'s 60s default.
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir, timeout=300)
