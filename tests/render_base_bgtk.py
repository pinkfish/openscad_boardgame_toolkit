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

# LibFile: tests/render_base_bgtk.py
#    Helper for rendering base_bgtk.py shapes with the *real* PythonSCAD binary. Same shape as
#    tests/render_cap_box.py (base_bgtk.py also calls `osuse("BOSL2/std.scad")` at import time,
#    so it needs the same PYTHONSCAD_BIN / BOSL2_SCAD_DIR fixups -- see render_cap_box.py's
#    module docstring for why and how).
#
# FileGroup: base_bgtk

from __future__ import annotations

from pathlib import Path

from render_cap_box import find_bosl2_scad_dir
from render_pysolidfive import RenderResult, render_script

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def render_base_bgtk_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single base_bgtk.py expression, e.g.
    `"DifferenceWithOffset(offset=-3, children=square([30, 30], center=True))"`. `expr` is
    evaluated with base_bgtk's public names and pythonscad's native primitives already imported
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
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir)
