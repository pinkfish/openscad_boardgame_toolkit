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

# LibFile: tests/render_app.py
#    The single shared entry point for running a build script through the real PythonSCAD
#    app and checking it produced geometry. Replaces the old render_pysolidfive helper
#    (which died with pysolidfive/mock_libfive). Every box/shape render test uses
#    render_python(): it wraps a snippet, runs the app binary, and reports Facets/Triangles.
#
#    The box/shape modules `from pythonscad import *`, so they can ONLY be imported inside
#    the app -- there is no pure-Python import path. These tests therefore shell out to the
#    binary and SKIP GRACEFULLY when the binary or the patched BOSL2 dir isn't present.
#
# FileGroup: Tests

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A local BOSL2 copy patched to load under PythonSCAD (the version_num assert neutralised);
# osuse() resolves "BOSL2/std.scad" relative to the process CWD, so the app is run with
# cwd = this directory (the parent of the BOSL2/ folder).
_CANDIDATE_BOSL2_DIRS = [str(Path.home() / "Documents/OpenSCAD/libraries-pythonscad-patched")]

_BINARY_CANDIDATES = [
    "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD",
    "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
]

# pysolidfive's PolySets report "Triangles: N"; BOSL2/Manifold CSG solids report "Facets: N".
# Either, with N > 0, means real geometry was produced.
_GEOM_RE = re.compile(r"(?:Triangles|Facets):\s*(\d+)")


def find_pythonscad_binary() -> str | None:
    """The PythonSCAD binary: PYTHONSCAD_BIN override first, then the standard app paths."""
    override = os.environ.get("PYTHONSCAD_BIN")
    if override:
        return override if Path(override).exists() else None
    for c in _BINARY_CANDIDATES:
        if Path(c).exists():
            return c
    return None


def find_bosl2_scad_dir() -> str | None:
    """Directory containing a `BOSL2/std.scad` that loads under PythonSCAD (BOSL2_SCAD_DIR
    override, else the known patched location). None -> skip the render tests."""
    override = os.environ.get("BOSL2_SCAD_DIR")
    if override:
        return override if (Path(override) / "BOSL2" / "std.scad").is_file() else None
    for c in _CANDIDATE_BOSL2_DIRS:
        if (Path(c) / "BOSL2" / "std.scad").is_file():
            return c
    return None


def _venv_site_packages() -> str | None:
    hits = list(PROJECT_ROOT.glob(".venv/lib/*/site-packages"))
    return str(hits[0]) if hits else None


def render_available() -> bool:
    """True when both the binary and a patched BOSL2 dir exist (for skipUnless)."""
    return find_pythonscad_binary() is not None and find_bosl2_scad_dir() is not None


@dataclass
class RenderResult:
    ok: bool                 # binary ran AND stderr reported geometry with N > 0
    facets: int | None
    error: str | None
    stderr: str


def render_python(body: str, *, imgsize: tuple[int, int] = (200, 150), timeout: float = 300.0) -> RenderResult:
    """Run *body* (python statements ending in `<solid>.show()`) through the real app and
    report whether it produced geometry. *body* is prepended with sys.path setup (the repo
    root + the .venv site-packages so pybosl2 imports) and FROM_MAKE=1.

    Never raises for a build/render failure -- reports it in RenderResult so tests can assert;
    only raises FileNotFoundError if the binary can't be located (callers should skipUnless
    render_available() first)."""
    binary = find_pythonscad_binary()
    bosl2_dir = find_bosl2_scad_dir()
    if binary is None or bosl2_dir is None:
        raise FileNotFoundError("PythonSCAD binary or patched BOSL2 dir not found (skip render tests)")

    header = (
        "import os, sys\n"
        "os.environ['FROM_MAKE'] = '1'\n"
        + (f"sys.path.insert(0, {_venv_site_packages()!r})\n" if _venv_site_packages() else "")
        + f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, dir=tempfile.gettempdir()) as f:
        f.write(header + body)
        script = Path(f.name)

    out_png = script.with_suffix(".png")
    try:
        proc = subprocess.run(
            [
                binary, "--trust-python", "--enable", "python-engine",
                "-o", str(out_png), "--imgsize", f"{imgsize[0]},{imgsize[1]}",
                "--render=true", "--backend", "Manifold", "--autocenter", "--viewall",
                str(script),
            ],
            capture_output=True, text=True, timeout=timeout, cwd=bosl2_dir,
        )
    except subprocess.TimeoutExpired as exc:
        return RenderResult(False, None, f"timed out after {timeout:.0f}s", str(exc.stderr or ""))
    finally:
        script.unlink(missing_ok=True)
        out_png.unlink(missing_ok=True)

    stderr = proc.stderr or ""
    if "Traceback (most recent call last):" in stderr:
        # The raised exception line ("SomeError: message"), not the app's post-render
        # diagnostics (Total rendering time / Geometries in cache) that follow it.
        errs = [ln.strip() for ln in stderr.splitlines()
                if re.match(r"^\s*[A-Za-z_][\w.]*(Error|Exception|Warning):", ln)]
        msg = errs[-1] if errs else "traceback (no exception line parsed)"
        return RenderResult(False, None, msg, stderr)

    facets = [int(m) for m in _GEOM_RE.findall(stderr)]
    n = max(facets) if facets else 0
    if n <= 0:
        return RenderResult(False, None, "no geometry (Facets/Triangles) reported", stderr)
    return RenderResult(True, n, None, stderr)


# ---------------------------------------------------------------------------
# Measuring geometry (not just "did it render")
# ---------------------------------------------------------------------------

#: Preamble injected before a measure_python() body. `measure(name, solid)` reports a
#: solid's real axis-aligned bounding box -- PythonSCAD computes `.position`/`.size` by
#: meshing, so this is the actual geometry, not what the script THINKS it built.
#:
#: Results go to a FILE, not just stderr: when a script makes the app ABORT (a BOSL2
#: assertion, an frep crash) the process dies without flushing its stderr, so every line
#: already reported is lost and a sweep cannot tell which case died. A file survives that,
#: so everything up to the crash is still readable. {log!r} is filled in per run.
_MEASURE_PREAMBLE = '''
import sys as _sys

_MEASURE_LOG = {log!r}


def _emit(_line):
    with open(_MEASURE_LOG, "a") as _f:
        _f.write(_line + "\\n")
    _sys.stderr.write(_line + "\\n")
    _sys.stderr.flush()


def measure(name, obj):
    """Report obj's AABB as `MEASURE <name> x y z w l h`."""
    n = obj.shape if hasattr(obj, "shape") else obj
    p, s = n.position, n.size
    _emit("MEASURE %s %.6g %.6g %.6g %.6g %.6g %.6g" % (name, p[0], p[1], p[2], s[0], s[1], s[2]))


def report(name, value):
    """Report an arbitrary scalar/string as `REPORT <name> <value>`."""
    _emit("REPORT %s %s" % (name, value))
'''


@dataclass
class Box3D:
    """An axis-aligned bounding box measured from real geometry."""

    x: float
    y: float
    z: float
    width: float
    length: float
    height: float

    @property
    def position(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def size(self) -> tuple[float, float, float]:
        return (self.width, self.length, self.height)

    @property
    def top(self) -> float:
        return self.z + self.height

    def __str__(self) -> str:
        return f"pos=({self.x:g}, {self.y:g}, {self.z:g}) size=({self.width:g} x {self.length:g} x {self.height:g})"


@dataclass
class MeasureResult:
    ok: bool
    boxes: dict[str, Box3D]     # name -> measured bounding box
    reports: dict[str, str]     # name -> reported value
    error: str | None
    stderr: str


def measure_python(body: str, *, timeout: float = 300.0) -> MeasureResult:
    """Run *body* through the real app and collect its `measure()` / `report()` calls.

    *body* is prepended with the same sys.path setup as :func:`render_python` plus the
    `measure()` / `report()` helpers, and must end in a `.show()` (the app needs a
    top-level object).

    Results survive a crash: they are written to a side file as well as stderr, because an
    app abort loses the whole stderr buffer (see _MEASURE_PREAMBLE). NOTE: never `measure()`
    and then `show()` the SAME solid when it contains frep/SDF geometry -- measuring meshes
    it, and reusing a meshed handle in another branch crashes the app. Show a throwaway
    primitive instead.
    """
    log = Path(tempfile.mkstemp(prefix="bgtk-measure-", suffix=".log")[1])
    try:
        result = render_python(_MEASURE_PREAMBLE.format(log=str(log)) + body, timeout=timeout)
        lines = log.read_text().splitlines() if log.exists() else []
    finally:
        log.unlink(missing_ok=True)

    boxes: dict[str, Box3D] = {}
    reports: dict[str, str] = {}
    for line in lines:
        if line.startswith("MEASURE "):
            _, name, *nums = line.split()
            boxes[name] = Box3D(*(float(v) for v in nums))
        elif line.startswith("REPORT "):
            _, name, value = line.split(None, 2)
            reports[name] = value.strip()
    return MeasureResult(result.ok, boxes, reports, result.error, result.stderr)
