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

# LibFile: tests/repro_sdf_bounds_kills_geometry.py
#    Minimal reproduction of the pybosl2 0.7.0 regression that took out every SDF-backed
#    box (filament_hinge, card_library).
#
#    An frep()-meshed handle renders fine on its own (68844 facets). Wrap that same handle in
#    the CSG facade -- `sdf_shape.to_csg()`, i.e. `Bosl2Solid(sdf.mesh())` -- and any
#    wrapper-level use of it (`.show()`, `.bounds()`, unioning it with a native solid) SIGSEGVs
#    the app (exit -11) with an empty stderr, so the render just looks like it produced nothing.
#    Reaching past the wrapper (`.to_csg().shape.show()`) works, and so does `.mesh().show()`.
#
#    The trigger is the bbox-backed anchoring layer: `Bosl2Solid._native_bounds()` reads the
#    native `obj.position` / `obj.size`, and touching either of those on an frep handle and then
#    using the handle is what kills it -- the `size_then_show` case below reproduces it with no
#    pybosl2 wrapper at all. 0.6.7 rendered every case here; 0.7.0 renders only the two that
#    never read the handle's bounds.
#
#    Dual-mode, like tests/repro_frep_reuse_segfault.py:
#      - Under PLAIN PYTHON it drives each case through the real binary and prints a table:
#            PYTHONSCAD_BIN=/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD \
#                python3 tests/repro_sdf_bounds_kills_geometry.py
#      - INSIDE PythonSCAD it runs one case, chosen with PYS_REPRO_CASE.
#
# FileGroup: Tests

import glob
import os
import re
import sys

try:
    # libfive, not pythonscad: the app registers libfive as a built-in extension and nothing
    # else ships it, whereas there is now a pip-installable `pythonscad` shim, so importing
    # THAT succeeds in a plain interpreter too -- which sent the driver down the in-app branch
    # outside the app and died on the first SDF call instead of printing the table.
    import libfive  # noqa: F401  -- only importable inside the PythonSCAD app
    _IN_APP = True
except ImportError:
    _IN_APP = False

if _IN_APP:
    # The app's embedded interpreter doesn't see the project venv; put it first, the way
    # tests/render_app.py does for every script it sends in. `__file__` is NOT defined in
    # here (the app exec's the source as "<string>"), so the driver hands the root over in
    # the environment.
    for _sp in glob.glob(os.path.join(os.environ.get("PYS_REPRO_ROOT", "."), ".venv/lib/*/site-packages")):
        sys.path.insert(0, _sp)


# ---------------------------------------------------------------------------
# The cases. "geometry" is what the CURRENT pinned pybosl2 (0.7.1) should do; 0.6.7 rendered
# every one of them, 0.7.0 rendered only the two that never read the handle's bounds.
#
# 0.7.1 fixed the four wrapper cases two ways: Bosl2Solid no longer forwards private attribute
# lookups (_tag_name/_attachments/...) to the native handle -- _wrap() did that on every
# transform and boolean, and PythonSCAD segfaults on such a lookup against an frep handle --
# and .to_csg() now rebuilds the meshed field as a polyhedron instead of handing the frep
# handle over, so the CSG side never touches obj.position/obj.size on a live field.
#
# size_then_show is NOT pybosl2's to fix and is expected to stay empty: it reads .size off a
# raw frep handle with no wrapper involved at all. That is the underlying PythonSCAD bug
# (reading the bbox corrupts the field; the next render dies with exit -11 and empty stderr).
# Flip it back to geometry=True if a PythonSCAD release ever fixes it.
# ---------------------------------------------------------------------------

CASES = {
    "mesh_show": dict(
        geometry=True,
        doc="sdf.mesh().show() -- the raw frep handle, no pybosl2 wrapper",
    ),
    "csg_shape_show": dict(
        geometry=True,
        doc="sdf.to_csg().shape.show() -- reaches past the wrapper to the same handle",
    ),
    "csg_show": dict(
        geometry=True,
        doc="sdf.to_csg().show() -- through the wrapper; SIGSEGV on 0.7.0, fixed in 0.7.1",
    ),
    "csg_union_native": dict(
        geometry=True,
        doc="native_cuboid | sdf.to_csg() -- the CSG/SDF bridge; SIGSEGV on 0.7.0, fixed in 0.7.1",
    ),
    "size_then_show": dict(
        geometry=False,
        doc="read handle.size, THEN show the same handle -- the raw PythonSCAD bug, still open",
    ),
}


def _sdf_solid():
    """A rounded SDF cuboid -- the simplest _sdf shape that has to be meshed."""
    from pybosl2._sdf import shapes3d as sdf3d

    return sdf3d.cuboid([10, 10, 10], rounding=1)


def _run_case(name: str):
    if name == "mesh_show":
        return _sdf_solid().mesh()
    if name == "csg_shape_show":
        return _sdf_solid().to_csg().shape
    if name == "csg_show":
        return _sdf_solid().to_csg()
    if name == "csg_union_native":
        from pybosl2 import shapes3d as s3

        return s3.cuboid([5, 5, 5]) | _sdf_solid().to_csg()
    if name == "size_then_show":
        handle = _sdf_solid().mesh()
        _ = handle.size  # reading it is what empties the render
        return handle
    raise ValueError(f"unknown case {name!r}; pick one of {sorted(CASES)}")


# ---------------------------------------------------------------------------
# Driver (plain python): spawn the binary once per case and report.
# ---------------------------------------------------------------------------

_GEOM_RE = re.compile(r"(?:Facets|Triangles):\s*(\d+)")


def _find_binary():
    env = os.environ.get("PYTHONSCAD_BIN")
    if env and os.path.exists(env):
        return env
    default = "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD"
    return default if os.path.exists(default) else None


def _drive():
    import subprocess
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
        out_png = os.path.join(tempfile.gettempdir(), f"repro_sdf_{name}.png")
        proc = subprocess.run(
            [
                binary,
                "--trust-python", "--enable", "python-engine",
                "-o", out_png, "--render=true", "--backend", "Manifold",
                "--autocenter", "--viewall",
                os.path.abspath(__file__),
            ],
            env={**os.environ, "PYS_REPRO_CASE": name,
                 "PYS_REPRO_ROOT": os.path.dirname(os.path.dirname(os.path.abspath(__file__)))},
            capture_output=True,
            text=True,
            timeout=300,
        )
        counts = [int(m) for m in _GEOM_RE.findall(proc.stderr or "")]
        facets = max(counts) if counts else 0
        actual = f"{facets} facets" if facets else f"EMPTY (exit {proc.returncode})"
        matches = (facets > 0) == meta["geometry"]
        if not matches:
            failures += 1
        marker = "as expected" if matches else "REGRESSED"
        print(f"{name:18s} expect={'geom' if meta['geometry'] else 'none':4s} "
              f"actual={actual:22s} [{marker}]  -- {meta['doc']}")

    print(
        "\nEvery REGRESSED row is a live bug: the frep handle meshes correctly, but reading its"
        "\nnative position/size and then using it SIGSEGVs the app. pybosl2 0.7.0 hit that from"
        "\nits own bbox-backed anchoring, which took out every SDF-backed box; 0.7.1 no longer"
        "\ntouches a live field that way, so the four wrapper rows render again. size_then_show"
        "\ndoes it by hand with no wrapper and is expected to stay EMPTY until PythonSCAD fixes"
        "\nthe underlying accessor -- see the note above CASES."
    )
    return 1 if failures else 0


if _IN_APP:
    _run_case(os.environ.get("PYS_REPRO_CASE", "csg_show")).show()
else:
    raise SystemExit(_drive())
