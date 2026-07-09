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

# LibFile: tests/render_boxes.py
#    Helper for rendering the remaining box modules' shapes (sliding_catch_box.py,
#    hinge_box.py, magnetic_box.py, dividers.py, inset_box.py, filament_hinge_box.py,
#    card_library.py, cap_box_polygon.py) with the *real* PythonSCAD binary. Same shape as
#    tests/render_cap_box.py (these modules also call `osuse("BOSL2/std.scad")` at import
#    time, so they need the same PYTHONSCAD_BIN / BOSL2_SCAD_DIR fixups -- see
#    render_cap_box.py's module docstring for why and how). One shared helper for all of
#    them since their expressions get evaluated with the same scope (everything
#    star-imported).
#
# FileGroup: boxes

from __future__ import annotations

from pathlib import Path

from render_cap_box import find_bosl2_scad_dir
from render_pysolidfive import RenderResult, render_script

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def render_boxes_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single box-module expression, e.g.
    `"MakeBoxWithSlidingCatchLid([100.0, 50.0, 20.0])"`. `expr` is evaluated with every
    remaining box module's public names and pythonscad's native primitives already imported
    into scope, and the project root already on sys.path.

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
        "from sliding_catch_box import *\n"
        "from hinge_box import *\n"
        "from magnetic_box import *\n"
        "from dividers import *\n"
        "from inset_box import *\n"
        "from filament_hinge_box import *\n"
        "from card_library import *\n"
        "from cap_box_polygon import *\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    # Same rationale as render_no_lid.py: SDF solids (after migration) mesh slower than plain
    # CSG, so give them room rather than inheriting render_script()'s 60s default.
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir, timeout=300)
