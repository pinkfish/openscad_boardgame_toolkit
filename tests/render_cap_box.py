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

# LibFile: tests/render_cap_box.py
#    Helper for rendering cap_box.py shapes with the *real* PythonSCAD binary. Extends
#    render_pysolidfive.py's render_script() (shared subprocess/skip-gracefully plumbing) with the one
#    extra thing cap_box.py needs that pysolidfive doesn't: a real `osuse("BOSL2/std.scad")` import
#    (cap_box.py -> base_bgtk.py loads real BOSL2 for a handful of functions -- reorient(),
#    offset() -- that aren't part of the pybosl2/ pure-Python port pysolidfive's tests rely on).
#
#    osuse() resolves its path relative to the process's current working directory, not the
#    script file's location (confirmed empirically; PythonSCAD logs a "DEPRECATED: Imported file
#    found in document root instead of relative to the importing module" warning when it does
#    this). So rendering a cap_box.py shape means running PythonSCAD with its CWD set to a
#    directory containing a working `BOSL2/` subdirectory.
#
#    "Working" is the second catch: the real ~/Documents/OpenSCAD/libraries/BOSL2 install (the
#    normal place OpenSCAD/BOSL2 users have it) asserts `version_num() >= 20210100` at the top of
#    std.scad, a check tuned for classic OpenSCAD's YYYYMMDD version scheme -- PythonSCAD instead
#    reports its own small semantic version (currently 1.0.0), which fails that assert outright.
#    find_bosl2_scad_dir() looks for a copy with that one assert line neutralized -- see this
#    module's docstring note below for how to create one -- rather than patching the user's real,
#    shared BOSL2 install (which other non-PythonSCAD projects may depend on as-is).
#
# FileGroup: cap_box

from __future__ import annotations

import os
from pathlib import Path

from render_pysolidfive import RenderResult, render_script

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_CANDIDATE_BOSL2_DIRS = [
    # A local, patched-for-PythonSCAD copy of BOSL2, kept as a sibling of the real
    # ~/Documents/OpenSCAD/libraries install so the real one (used by classic OpenSCAD.app,
    # which doesn't need the patch) is never touched. To (re)create it:
    #
    #   cp -R ~/Documents/OpenSCAD/libraries/BOSL2 ~/Documents/OpenSCAD/libraries-pythonscad-patched/BOSL2
    #
    # then comment out the `assert(version_num()>=20210100, ...)` line at the top of that copy's
    # std.scad (it's the only change needed -- BOSL2 itself works fine under PythonSCAD).
    str(Path.home() / "Documents/OpenSCAD/libraries-pythonscad-patched"),
]


def find_bosl2_scad_dir() -> str | None:
    """Locates a directory containing a `BOSL2/` subdirectory whose std.scad will actually load
    under PythonSCAD (see module docstring). Checks the BOSL2_SCAD_DIR environment variable
    first (an explicit override), then a list of well-known local fixup locations. Returns None
    if none exist -- callers should treat that as "skip real-render tests", not as an error.
    """
    override = os.environ.get("BOSL2_SCAD_DIR")
    if override:
        return override if (Path(override) / "BOSL2" / "std.scad").is_file() else None
    for candidate in _CANDIDATE_BOSL2_DIRS:
        if (Path(candidate) / "BOSL2" / "std.scad").is_file():
            return candidate
    return None


def render_cap_box_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single cap_box.py expression, e.g. `"MakeBoxWithCapLid([80.0,
    60.0, 20.0])"`. `expr` is evaluated with cap_box's/base_bgtk's public names (MakeBoxWithCapLid,
    CapBoxLid, CatchType, InnerObject, ObjectType, ...) and pythonscad's native primitives (cube,
    ...) already imported into scope, and the project root already on sys.path.

    Raises FileNotFoundError if no working BOSL2 dir is found -- callers should check
    find_bosl2_scad_dir() first and skip gracefully, same pattern as find_pythonscad_binary().
    """
    bosl2_dir = find_bosl2_scad_dir()
    if bosl2_dir is None:
        raise FileNotFoundError(
            "no working BOSL2/std.scad found for PythonSCAD (set BOSL2_SCAD_DIR; see this "
            "module's docstring for how to create a patched copy)"
        )
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "from pythonscad import *\n"
        "from base_bgtk import *\n"
        "from cap_box import *\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    return render_script(script, out_png, imgsize=imgsize, cwd=bosl2_dir)
