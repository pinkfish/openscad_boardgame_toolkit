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

# LibFile: tests/repro_frep_reuse_segfault.py
#    Minimal, dependency-free reproduction of a PythonSCAD crash (SIGSEGV, exit -11):
#    referencing ONE frep()-meshed handle from more than one CSG branch -- or even just
#    calling a transform on it twice -- segfaults the app during render. Two independent
#    frep() meshes of the same SDF work fine, as does reusing plain CSG-built handles.
#
#    This is why the toolkit follows a "fresh mesh per use" discipline: pysolidfive callers
#    never place one .mesh()/.color() result twice, and lids_base.make_tabs() accepts a
#    zero-argument factory callable as `children` so every tab placement gets its own mesh.
#
#    The file is dual-mode:
#      - Run under PLAIN PYTHON, it drives every case below through the real PythonSCAD
#        binary as subprocesses and prints a pass/crash table:
#            PYTHONSCAD_BIN=/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD \
#                python3 tests/repro_frep_reuse_segfault.py
#      - Run INSIDE PythonSCAD, it executes a single case (chosen via the PYS_REPRO_CASE
#        environment variable, default "reuse_translate"):
#            PYS_REPRO_CASE=two_meshes /Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD \
#                --trust-python --enable python-engine -o /tmp/repro.png --render=true \
#                --autocenter --viewall tests/repro_frep_reuse_segfault.py
#
# FileGroup: pysolidfive

import os

try:
    # libfive, not pythonscad: the app registers libfive as a built-in extension and nothing
    # else ships it, whereas there is now a pip-installable `pythonscad` shim, so importing
    # THAT succeeds in a plain interpreter too -- which sent the driver down the in-app branch
    # outside the app and died on the first SDF call instead of printing the table.
    import libfive  # noqa: F401  -- only importable inside the PythonSCAD app
    _IN_APP = True
except ImportError:
    _IN_APP = False


# ---------------------------------------------------------------------------
# The cases. Each returns the shape to show; "crashes" documents observed behaviour
# with PythonSCAD-dev (macOS, 2026-07).
# ---------------------------------------------------------------------------

CASES = {
    # Control: two INDEPENDENT frep meshes of the same SDF, one use each. Works.
    "two_meshes": dict(
        crashes=False,
        doc="two independent frep() meshes, each transformed once, unioned",
    ),
    # One frep mesh handle, translated in two CSG branches. SIGSEGV.
    "reuse_translate": dict(
        crashes=True,
        doc="ONE frep() mesh translated in two branches of a union",
    ),
    # Same, with rotations. SIGSEGV.
    "reuse_rotate": dict(
        crashes=True,
        doc="ONE frep() mesh rotated in two branches of a union",
    ),
    # Even when only one of the two transformed results is used in the output. SIGSEGV.
    "reuse_transform_only": dict(
        crashes=True,
        doc="ONE frep() mesh transformed twice; only one result shown",
    ),
    # Wrapping the mesh in union([...]) first does not help. SIGSEGV.
    "union_wrap": dict(
        crashes=True,
        doc="frep() mesh wrapped in union([m]); the wrapper reused in two branches",
    ),
}


def _sphere_mesh():
    """A frep()-meshed sphere of radius 5 -- the simplest possible libfive solid."""
    import libfive as lv
    from pythonscad import frep

    x, y, z = lv.x(), lv.y(), lv.z()
    sdf = lv.sqrt(x * x + y * y + z * z) - 5
    return frep(sdf, [-6, -6, -6], [6, 6, 6], 20)


def _run_case(name: str):
    from pythonscad import union

    if name == "two_meshes":
        a = _sphere_mesh()
        b = _sphere_mesh()
        return a.translate([-8, 0, 0]) | b.translate([8, 0, 0])
    if name == "reuse_translate":
        m = _sphere_mesh()
        return m.translate([-8, 0, 0]) | m.translate([8, 0, 0])
    if name == "reuse_rotate":
        m = _sphere_mesh()
        return m.rotate([0, 0, 270]).translate([-8, 0, 0]) | m.rotate([0, 0, 90]).translate([8, 0, 0])
    if name == "reuse_transform_only":
        m = _sphere_mesh()
        unused = m.rotate([0, 0, 270])  # noqa: F841 -- never shown, still crashes
        return m.rotate([0, 0, 90]).translate([8, 0, 0])
    if name == "union_wrap":
        m = union([_sphere_mesh()])
        return m.translate([-8, 0, 0]) | m.translate([8, 0, 0])
    raise ValueError(f"unknown case {name!r}; pick one of {sorted(CASES)}")


# ---------------------------------------------------------------------------
# Driver (plain python): spawn the binary once per case and report.
# ---------------------------------------------------------------------------


def _find_binary():
    env = os.environ.get("PYTHONSCAD_BIN")
    if env and os.path.exists(env):
        return env
    default = "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD"
    return default if os.path.exists(default) else None


def _drive():
    import subprocess
    import sys
    import tempfile

    # Keep scratch off the boot volume (see tests/render_app.py TEMP_ROOT).
    tempfile.tempdir = os.environ.get("BGTK_TMPDIR") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".render-tmp"
    )
    os.makedirs(tempfile.tempdir, exist_ok=True)

    binary = _find_binary()
    if binary is None:
        print("No PythonSCAD binary found (set PYTHONSCAD_BIN). Aborting.")
        return 1

    print(f"binary: {binary}\n")
    failures = 0
    for name, meta in CASES.items():
        out_png = os.path.join(tempfile.gettempdir(), f"repro_frep_{name}.png")
        proc = subprocess.run(
            [
                binary,
                "--trust-python", "--enable", "python-engine",
                "-o", out_png, "--render=true", "--autocenter", "--viewall",
                os.path.abspath(__file__),
            ],
            env={**os.environ, "PYS_REPRO_CASE": name},
            capture_output=True,
            text=True,
            timeout=120,
        )
        crashed = proc.returncode == -11
        expected = "crash" if meta["crashes"] else "ok"
        actual = "crash (SIGSEGV)" if crashed else ("ok" if proc.returncode == 0 else f"exit {proc.returncode}")
        matches = crashed == meta["crashes"] and (crashed or proc.returncode == 0)
        marker = "as expected" if matches else "UNEXPECTED"
        if not matches:
            failures += 1
        print(f"{name:22s} expected={expected:5s} actual={actual:14s} [{marker}]  -- {meta['doc']}")

    print(
        "\nEvery 'crash' row is the bug: one frep()-meshed handle referenced from more than"
        "\none CSG branch (or transformed twice) kills the process. Independent frep() meshes"
        "\nof the identical SDF ('two_meshes') are fine."
    )
    return 1 if failures else 0


if _IN_APP:
    shape = _run_case(os.environ.get("PYS_REPRO_CASE", "reuse_translate"))
    shape.show()
else:
    raise SystemExit(_drive())
