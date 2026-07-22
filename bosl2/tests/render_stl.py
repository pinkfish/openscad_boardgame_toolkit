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

"""Real-render helpers for the STL tests (bosl2/tests/test_stl_render.py).

Unlike the mock-based unit tests, these drive the REAL PythonSCAD binary in a subprocess to build
a bosl2 object, export it to an STL mesh, and then load that mesh back to measure it (bounding
box, triangle count, volume, surface area, watertightness). The subprocess runs the real
`pythonscad` module, so the parent-process mock (installed by conftest) is irrelevant to it.

Everything skips gracefully when no PythonSCAD binary is available (set PYTHONSCAD_BIN, or install
to /Applications) -- these tests need the app, they are not part of the pure-Python suite.
"""

from __future__ import annotations

import os
import struct
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# bosl2/tests/render_stl.py -> bosl2/tests -> bosl2 -> repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# PythonSCAD-dev is preferred: the plain app's hardened runtime rejects the installed numpy, which
# every bosl2 module imports (see CLAUDE.md), so nearly all bosl2 renders fail under it.
_CANDIDATE_BINARIES = [
    "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD",
    "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
]


def find_pythonscad_binary() -> str | None:
    """The PythonSCAD binary to render with: $PYTHONSCAD_BIN, else a known install, else None."""
    override = os.environ.get("PYTHONSCAD_BIN")
    if override:
        return override if Path(override).is_file() else None
    for candidate in _CANDIDATE_BINARIES:
        if Path(candidate).is_file():
            return candidate
    return None


@dataclass
class StlResult:
    ok: bool
    path: Path | None
    error: str | None
    stderr: str


_PREAMBLE = (
    "import sys, math\n"
    f"sys.path.insert(0, {str(REPO_ROOT)!r})\n"
    "import numpy as np\n"
    "import bosl2.shapes3d as s3\n"
    "import bosl2.shapes2d as s2\n"
    "from bosl2.beziers import Bezier, BezierPatch\n"
    "from bosl2.skin import path_sweep, path_sweep2d, sweep, skin, linear_sweep, rotate_sweep, spiral_sweep, rot_resample\n"
    "from bosl2.drawing import arc, catenary, helix, turtle, stroke, dashed_stroke\n"
    "from bosl2.distributors import distribute, xdistribute, ydistribute, zdistribute\n"
    "from bosl2.color import hsl, hsv, rainbow, rainbow_colors\n"
    "from bosl2.partitions import partition_path, partition_mask, partition_cut_mask\n"
    "from bosl2.miscellaneous import extrude_from_to, cylindrical_extrude, chain_hull, minkowski_difference\n"
    "from bosl2.nurbs import nurbs_curve, nurbs_patch_points, nurbs_vnf, nurbs_elevate_degree, is_nurbs_patch\n"
    "from bosl2.rounding import round_corners, smooth_path\n"
    "from bosl2.isosurface import isosurface, metaballs, mb_sphere, mb_cuboid, mb_torus, mb_capsule, mb_disk, mb_octahedron, mb_connector\n"
    "from bosl2.threading import Threading\n"
    "from bosl2.screws import Screws\n"
    "from functools import reduce\n"
    "from bosl2.paths import Path, Path3D\n"
    "from bosl2.regions import Region\n"
    "from bosl2.constants import *\n"
)


def render_object(expr: str, out_stl: Path, setup: str = "", timeout: float = 180.0) -> StlResult:
    """Build ``obj = <expr>`` (after any *setup* statements) in the real app and export it to STL.

    *expr* must evaluate to a native solid or a Bosl2Solid (a VNF/patch expression should end in
    ``.polyhedron()``). Returns an StlResult; never raises for a render failure so callers can
    assert on ``.ok``. Only raises if no binary can be located at all.
    """
    body = _PREAMBLE + setup + f"obj = {expr}\n" + "obj.show()\n"
    return render_stl_script(body, out_stl, timeout=timeout)


def render_stl_script(script_source: str, out_stl: Path, timeout: float = 180.0, cwd=None) -> StlResult:
    """Run a full python-mode *script_source* (ending in ``.show()``) in the real app, exporting STL.

    The lower-level entry point behind :func:`render_object`; also used by the docs
    ``bosl2-example`` directive to generate a downloadable STL for each example.
    """
    binary = find_pythonscad_binary()
    if binary is None:
        raise FileNotFoundError("no PythonSCAD binary found (set PYTHONSCAD_BIN or install to /Applications)")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()) as f:
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
                str(out_stl),
                "--backend",
                "Manifold",
                str(script_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        err = exc.stderr or b""
        return StlResult(False, None, f"render timed out after {timeout:.0f}s",
                         err.decode(errors="replace") if isinstance(err, bytes) else str(err))
    finally:
        script_path.unlink(missing_ok=True)

    stderr = proc.stderr or ""
    if "Traceback (most recent call last):" in stderr:
        lines = stderr.splitlines()
        cutoff = next((i for i, ln in enumerate(lines) if ln.startswith("Geometries in cache")), len(lines))
        last = next((ln for ln in reversed(lines[:cutoff]) if ln.strip()), "unknown error")
        return StlResult(False, None, f"script raised: {last[:200]}", stderr)
    if proc.returncode != 0:
        return StlResult(False, None, f"PythonSCAD exited {proc.returncode}", stderr)
    if not out_stl.is_file() or out_stl.stat().st_size == 0:
        return StlResult(False, None, "no STL file was produced", stderr)
    return StlResult(True, out_stl, None, stderr)


def parse_stl(path: Path) -> np.ndarray:
    """Load an STL (binary or ASCII) as an (N, 3, 3) array of triangle vertices."""
    data = Path(path).read_bytes()
    if len(data) >= 84:
        n = struct.unpack("<I", data[80:84])[0]
        if len(data) == 84 + 50 * n:  # exact binary-STL size => binary
            dt = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("attr", "<u2")])
            arr = np.frombuffer(data, dtype=dt, offset=84, count=n)
            return np.array(arr["v"], dtype=float)
    verts = []
    for line in data.decode("ascii", errors="replace").splitlines():
        line = line.strip()
        if line.startswith("vertex"):
            _, x, y, z = line.split()[:4]
            verts.append([float(x), float(y), float(z)])
    arr = np.asarray(verts, dtype=float)
    assert arr.size and len(arr) % 3 == 0, "malformed ASCII STL"
    return arr.reshape(-1, 3, 3)


@dataclass
class StlMetrics:
    ntris: int
    bbmin: np.ndarray
    bbmax: np.ndarray
    size: np.ndarray
    volume: float
    area: float
    watertight: bool


def stl_metrics(path: Path) -> StlMetrics:
    """Measure an STL: triangle count, bounding box, enclosed volume, surface area, watertightness."""
    tris = parse_stl(path)
    pts = tris.reshape(-1, 3)
    bbmin, bbmax = pts.min(axis=0), pts.max(axis=0)
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    volume = abs(float(np.sum(np.einsum("ij,ij->i", v0, np.cross(v1, v2))) / 6.0))
    area = float(np.sum(0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)))
    # watertight: every undirected edge shared by exactly two triangles (rounded to fuse vertices)
    edges: dict = {}
    keys = np.round(tris, 4)
    for tri in keys:
        vs = [tuple(v) for v in tri]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            e = tuple(sorted((vs[a], vs[b])))
            edges[e] = edges.get(e, 0) + 1
    watertight = bool(edges) and all(c == 2 for c in edges.values())
    return StlMetrics(len(tris), bbmin, bbmax, bbmax - bbmin, volume, area, watertight)
