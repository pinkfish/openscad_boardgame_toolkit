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

# LibFile: tests/repro_osuse_assert_aborts.py
#    Minimal reproduction of a PythonSCAD crash (SIGABRT, exit -6): when a .scad function
#    reached through osuse()/osinclude() hits a failing assert(), the whole PROCESS dies.
#    The assert surfaces as an uncaught C++ exception --
#
#        libc++abi: terminating due to uncaught exception of type AssertionFailedException
#
#    -- so Python never sees it. `try: ... except Exception:` does not help, and no code
#    after the call runs.
#
#    NO LIBRARY NEEDED. The whole .scad side is one line, written to a temp dir by this
#    script:
#
#        function boom(n) = assert(n >= 3, "n must be >= 3") n;
#
#        m = osuse("boom.scad")
#        m.boom(5)    # -> 5.0
#        m.boom(2)    # -> SIGABRT, process gone
#
#    THREE CONTROLS SHOW HOW NARROW THIS IS -- everything else behaves properly:
#
#      * `ok_control`   -- the same function, valid argument, through the same handle: fine.
#      * `python_error` -- a PYTHON-level failure through the same handle raises
#                          AttributeError and exits 0. The FFI propagates Python errors
#                          correctly; it is specifically the SCAD assert that is fatal.
#      * `native_junk`  -- the NATIVE api is robust: a 1-point polygon, a face index that is
#                          out of range, an offset that annihilates the shape, minkowski with
#                          an empty operand -- all either build or raise a clean TypeError.
#                          (16 such cases were tried; none crashes.) So this is not "bad
#                          input crashes the app" in general -- it is the .scad assert path.
#
#    AND THE DIAGNOSTIC LOSS: `stderr_lost` writes a line to stderr and FLUSHES it before
#    the aborting call. The line never reaches the parent process. A crashed run therefore
#    looks like it never ran, so you cannot print your way to the offending call. (Writing
#    to a FILE survives -- which is why tests/render_app.py's measure_python() logs to one.)
#
#    WHY IT MATTERED HERE: tesselations.py used osuse'd BOSL2 region algebra
#    (offset_stroke/union/intersection/difference), and degenerate outlines tripped exactly
#    this. ShapeType.LEAF / LEAF_VEINS could not be built at all, and no amount of Python
#    error handling could contain it. The fix was to stop crossing the FFI: those are direct
#    2-D CSG calls now and tesselations.py no longer calls osuse.
#
#    The file is dual-mode:
#      - Run under PLAIN PYTHON, it drives every case through the real binary as
#        subprocesses and prints a pass/crash table:
#            PYTHONSCAD_BIN=/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD \
#                python3 tests/repro_osuse_assert_aborts.py
#      - Run INSIDE PythonSCAD, it executes a single case (PYS_REPRO_CASE, default
#        "assert_osuse"; PYS_REPRO_SCAD names the generated .scad).
#
# FileGroup: Tests

import os
import tempfile

try:
    import pythonscad  # noqa: F401  -- only importable inside the PythonSCAD app
    _IN_APP = True
except ImportError:
    _IN_APP = False

# Keep scratch off the boot volume (see tests/render_app.py TEMP_ROOT for the rationale).
# Standalone script: resolve it locally rather than importing the harness.
tempfile.tempdir = os.environ.get("BGTK_TMPDIR") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".render-tmp"
)
os.makedirs(tempfile.tempdir, exist_ok=True)


#: The entire .scad side of the repro.
BOOM_SCAD = 'function boom(n) = assert(n >= 3, "n must be >= 3") n;\n'

#: The marker the stderr_lost case flushes before crashing; the driver checks if it survives.
STDERR_MARKER = "REPRO-STDERR-MARKER-FLUSHED-BEFORE-THE-CALL"


# ---------------------------------------------------------------------------
# The cases. "crashes" documents observed behaviour with PythonSCAD-dev (macOS, 2026-08).
# ---------------------------------------------------------------------------

CASES = {
    "ok_control": dict(
        crashes=False,
        doc="boom(5) -- valid; differs from the crash by ONE argument",
    ),
    "python_error": dict(
        crashes=False,
        doc="m.no_such_function() -- a Python error IS catchable; the FFI is fine",
    ),
    "native_junk": dict(
        crashes=False,
        doc="degenerate NATIVE calls (1-point polygon, bad face index, ...) -- all handled",
    ),
    "assert_osuse": dict(
        crashes=True,
        doc="boom(2) via osuse() -- one failing assert, dead process",
    ),
    "assert_osinclude": dict(
        crashes=True,
        doc="boom(2) via osinclude() -- same, so it is not specific to osuse()",
    ),
    "stderr_lost": dict(
        crashes=True,
        doc="stderr flushed BEFORE the aborting call never reaches the parent",
    ),
}


def _scad_path() -> str:
    """The generated one-line .scad library (written by the driver, or here if run alone)."""
    path = os.environ.get("PYS_REPRO_SCAD")
    if path and os.path.isfile(path):
        return path
    path = os.path.join(tempfile.gettempdir(), "repro_boom.scad")
    with open(path, "w") as handle:
        handle.write(BOOM_SCAD)
    return path


def _run_case(name: str):
    """Run one case and return the shape to show. The crashing cases never return."""
    import sys

    from pythonscad import cube, minkowski, osinclude, osuse, polygon, square

    scad = _scad_path()

    if name == "ok_control":
        assert osuse(scad).boom(5) == 5.0
    elif name == "python_error":
        try:
            osuse(scad).no_such_function_at_all()
        except Exception as exc:                      # noqa: BLE001 -- that is the point
            sys.stderr.write(f"caught a Python error as expected: {type(exc).__name__}\n")
    elif name == "native_junk":
        # The native api takes all of this in its stride -- build or clean TypeError.
        polygon([[0, 0]])
        polygon([[0, 0], [1, 0], [1, 1]], paths=[[0, 1, 9]])
        square([10, 10]).offset(r=-50).linear_extrude(height=1)
        for junk in (lambda: cube([0, 0, 0]), lambda: minkowski(cube(1), polygon([]))):
            try:
                junk()
            except TypeError:
                pass
    elif name == "assert_osuse":
        osuse(scad).boom(2)                           # assert n >= 3 fails
    elif name == "assert_osinclude":
        osinclude(scad).boom(2)
    elif name == "stderr_lost":
        sys.stderr.write(STDERR_MARKER + "\n")
        sys.stderr.flush()                            # flushed, and still lost
        osuse(scad).boom(2)
    else:
        raise ValueError(f"unknown case {name!r}; pick one of {sorted(CASES)}")

    return cube(1)


# ---------------------------------------------------------------------------
# Driver (plain python): spawn the binary once per case and report.
# ---------------------------------------------------------------------------


def _find_binary():
    env = os.environ.get("PYTHONSCAD_BIN")
    if env and os.path.exists(env):
        return env
    for candidate in (
        "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD",
        "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def _drive():
    import subprocess

    binary = _find_binary()
    if binary is None:
        print("No PythonSCAD binary found (set PYTHONSCAD_BIN). Aborting.")
        return 1

    scad = os.path.join(tempfile.gettempdir(), "repro_boom.scad")
    with open(scad, "w") as handle:
        handle.write(BOOM_SCAD)

    print(f"binary: {binary}\nscad:   {scad}  ->  {BOOM_SCAD.strip()}\n")
    failures = 0
    for name, meta in CASES.items():
        proc = subprocess.run(
            [
                binary,
                "--trust-python", "--enable", "python-engine",
                "-o", os.path.join(tempfile.gettempdir(), f"repro_osuse_{name}.png"),
                "--render=true", "--autocenter", "--viewall",
                os.path.abspath(__file__),
            ],
            env={**os.environ, "PYS_REPRO_CASE": name, "PYS_REPRO_SCAD": scad},
            capture_output=True,
            text=True,
            timeout=120,
        )
        crashed = proc.returncode == -6
        actual = "crash (SIGABRT)" if crashed else ("ok" if proc.returncode == 0 else f"exit {proc.returncode}")
        matches = crashed == meta["crashes"] and (crashed or proc.returncode == 0)
        if not matches:
            failures += 1
        note = ""
        if name == "stderr_lost":
            kept = STDERR_MARKER in (proc.stderr or "")
            note = f"  [flushed stderr survived: {kept}]"
            if kept:
                failures += 1
        print(
            f"{name:17s} expected={'crash' if meta['crashes'] else 'ok':5s} actual={actual:15s}"
            f" libc++abi={str('libc++abi' in (proc.stderr or '')):5s}"
            f" [{'as expected' if matches else 'UNEXPECTED'}]{note}"
            f"\n{'':17s} -- {meta['doc']}"
        )

    print(
        "\nEvery 'crash' row is the bug: ONE .scad call whose assert() fails takes the whole"
        "\nprocess down with SIGABRT, uncatchable from Python. The three 'ok' rows show the"
        "\nsurrounding surface behaving correctly -- including deliberately degenerate NATIVE"
        "\ncalls -- so this is the .scad assert path specifically, not error handling at large."
        "\nNote 'flushed stderr survived: False': output written before the call is gone too,"
        "\nso a crashed run looks like it never ran."
    )
    return 1 if failures else 0


if _IN_APP:
    shape = _run_case(os.environ.get("PYS_REPRO_CASE", "assert_osuse"))
    shape.show()
elif __name__ == "__main__":
    raise SystemExit(_drive())
