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

# LibFile: pysolidfive/tests/render_pysolidfive.py
#    Helper for rendering pysolidfive shapes with the *real* PythonSCAD binary and comparing the
#    result against a golden PNG. Unlike pysolidfive/tests/mock_libfive.py (which never touches a
#    real PythonSCAD install), this module shells out to an actual app so tests can catch things
#    a numeric mock can't: real frep()/libfive meshing, real anchor/orientation, real colors.
#
#    Also shared, unmodified, by every other library's render tests in the parent repo's own
#    tests/ directory (cap_box.py, sliding_box.py, labels.py, ...) -- render_script(),
#    compare_images(), and find_pythonscad_binary() are generic subprocess/skip-gracefully
#    plumbing, not pysolidfive-specific; only render_pysolidfive_shape() itself is.
#
#    Some of those *other* libraries' real-render tests (anything that imports bosl2, e.g.
#    cap_box.py/sliding_box.py) can hit a hardened-runtime code-signing check on this machine's
#    installed PythonSCAD.app that rejects the numpy build bosl2.shapes3d/bosl2.shapes2d
#    transitively depend on (bosl2.vectors/bosl2.geometry -> numpy) -- an environment problem,
#    not a correctness bug. pysolidfive itself has no such dependency (see
#    pysolidfive/__init__.py's module docstring), so pysolidfive/tests/test_pysolidfive_render.py
#    isn't affected by this. render_script() detects the failure (from either cause) from the
#    subprocess's stderr and reports it via RenderResult.ok=False rather than raising, so callers
#    can skip gracefully instead of failing outright.
#
# FileGroup: pysolidfive

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# pysolidfive/tests/render_pysolidfive.py -> pysolidfive/tests -> pysolidfive -> repo root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_CANDIDATE_BINARIES = [
    "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
]

# pysolidfive's frep()-meshed PolySets report "Triangles: N"; real BOSL2/CSG solids (Manifold
# backend, used by cap_box.py et al) report "Facets: N" instead -- either one means real
# geometry came out.
_TRIANGLES_RE = re.compile(r"(?:Triangles|Facets):\s*(\d+)")


def find_pythonscad_binary() -> str | None:
    """Locates a real PythonSCAD binary to render with.

    Checks the PYTHONSCAD_BIN environment variable first (an explicit override), then a list of
    well-known install locations. Returns None if none of them exist -- callers should treat
    that as "skip real-render tests", not as an error.
    """
    override = os.environ.get("PYTHONSCAD_BIN")
    if override:
        return override if Path(override).is_file() else None
    for candidate in _CANDIDATE_BINARIES:
        if Path(candidate).is_file():
            return candidate
    return None


@dataclass
class RenderResult:
    """Outcome of attempting a real render.

    ok=True means the binary ran, and stderr contained a "Triangles: N" marker with N>0 --
    i.e. real geometry actually got produced (not just a blank/background image). ok=False
    covers every other outcome (binary missing, crash, Python-level exception inside the
    script, zero-triangle result): `error` holds a short human-readable reason, and `stderr`
    the full captured stream for debugging.
    """

    ok: bool
    image_path: Path | None
    triangles: int | None
    error: str | None
    stderr: str


def render_script(
    script_source: str,
    out_png: Path,
    imgsize: tuple[int, int] = (320, 240),
    timeout: float = 60.0,
    cwd: str | Path | None = None,
) -> RenderResult:
    """Renders `script_source` (a full PythonSCAD python-mode script) to `out_png` using the
    real PythonSCAD binary. Never raises for render failures -- reports them in RenderResult so
    callers can skip gracefully; only raises if the binary can't be located at all.

    `cwd`: working directory to run the binary in. osuse() (the python-mode builtin for loading
    a real .scad library, e.g. BOSL2/std.scad) resolves its path relative to the process's CWD
    at the time of the call -- not relative to the script file's own directory -- so callers
    whose script calls osuse() with a relative path must pass the directory that relative path
    should resolve from (see tests/render_cap_box.py's find_bosl2_scad_dir()).
    """
    binary = find_pythonscad_binary()
    if binary is None:
        raise FileNotFoundError(
            "no PythonSCAD binary found (set PYTHONSCAD_BIN or install to /Applications)"
        )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
    ) as f:
        f.write(script_source)
        script_path = Path(f.name)

    try:
        proc = subprocess.run(
            [
                binary,
                "--trust-python",
                "--enable",
                "python-engine",
                "-o",
                str(out_png),
                "--imgsize",
                f"{imgsize[0]},{imgsize[1]}",
                "--render=true",
                # Manifold is the app's fast rendering backend (CGAL is the old/slow one).
                # It already appears to be the default, but pin it so a default change (or a
                # user config) can never silently put golden renders on the slow path.
                "--backend",
                "Manifold",
                "--autocenter",
                "--viewall",
                str(script_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        # Report like any other render failure so batch callers (generate_golden_images.py)
        # keep going instead of dying mid-run.
        stderr_bytes = exc.stderr or b""
        return RenderResult(
            ok=False,
            image_path=None,
            triangles=None,
            error=f"render timed out after {timeout:.0f}s",
            stderr=stderr_bytes.decode(errors="replace") if isinstance(stderr_bytes, bytes) else str(stderr_bytes),
        )
    finally:
        script_path.unlink(missing_ok=True)

    stderr = proc.stderr or ""

    if "Traceback (most recent call last):" in stderr:
        # The last non-blank line before PythonSCAD's own post-render diagnostics ("Geometries
        # in cache: ...") is the actual raised exception's message -- more useful than the
        # traceback's first line, which is usually just "Python Code globally trusted".
        lines = stderr.splitlines()
        cutoff = next((i for i, line in enumerate(lines) if line.startswith("Geometries in cache")), len(lines))
        last_line = next(
            (line for line in reversed(lines[:cutoff]) if line.strip()), "unknown error"
        )
        if len(last_line) > 200:
            last_line = last_line[:200] + "... (see .stderr for full message)"
        return RenderResult(
            ok=False, image_path=None, triangles=None, error=f"script raised: {last_line}", stderr=stderr
        )

    if proc.returncode != 0:
        return RenderResult(
            ok=False,
            image_path=None,
            triangles=None,
            error=f"PythonSCAD exited {proc.returncode}",
            stderr=stderr,
        )

    m = _TRIANGLES_RE.search(stderr)
    if m is None:
        return RenderResult(
            ok=False,
            image_path=None,
            triangles=None,
            error="no 'Triangles: N' marker in stderr (no geometry produced)",
            stderr=stderr,
        )

    triangles = int(m.group(1))
    if triangles <= 0:
        return RenderResult(
            ok=False, image_path=None, triangles=triangles, error="rendered geometry has 0 triangles", stderr=stderr
        )

    if not out_png.is_file():
        return RenderResult(
            ok=False, image_path=None, triangles=triangles, error="PNG output file was not created", stderr=stderr
        )

    return RenderResult(ok=True, image_path=out_png, triangles=triangles, error=None, stderr=stderr)


def render_pysolidfive_shape(expr: str, out_png: Path, imgsize: tuple[int, int] = (320, 240)) -> RenderResult:
    """Convenience wrapper: renders a single pysolidfive expression, e.g. `"pysolidfive.cuboid([20,20,20],
    rounding=4)"`. `expr` is evaluated with `pysolidfive` already imported into scope, and the
    project root already on sys.path."""
    script = (
        "import sys\n"
        f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
        "import pysolidfive\n"
        f"shape = {expr}\n"
        "shape.show()\n"
    )
    return render_script(script, out_png, imgsize=imgsize)


def compare_images(path_a: Path, path_b: Path) -> float:
    """Returns the mean absolute per-channel pixel difference between two PNGs (0.0 = identical,
    255.0 = maximally different), after resizing `b` to `a`'s size if they differ. Requires
    Pillow, which is available in this project's venv (used only by these render tests, not by
    pysolidfive itself)."""
    from PIL import Image

    with Image.open(path_a) as img_a, Image.open(path_b) as img_b:
        img_a = img_a.convert("RGB")
        img_b = img_b.convert("RGB")
        if img_a.size != img_b.size:
            img_b = img_b.resize(img_a.size)

        pixels_a = img_a.tobytes()
        pixels_b = img_b.tobytes()
        total = sum(abs(a - b) for a, b in zip(pixels_a, pixels_b))
        return total / len(pixels_a)
