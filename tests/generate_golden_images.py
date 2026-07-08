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

# LibFile: tests/generate_golden_images.py
#    Run this manually (not part of the automated test suite) on a machine where the real
#    PythonSCAD binary can actually render pysolidfive/cap_box/components/lids_base/labels/base_bgtk/
#    sliding_box shapes -- pysolidfive itself needs nothing beyond the binary (no bosl2/numpy
#    dependency; see pysolidfive/__init__.py's module docstring), but cap_box/components/
#    lids_base/labels/base_bgtk/sliding_box also need bosl2's numpy dependency to load inside the
#    app, and a working (PythonSCAD-compatible) BOSL2 install (see tests/render_cap_box.py's
#    module docstring) -- to (re)generate the golden images that pysolidfive/tests/
#    test_pysolidfive_render.py, test_cap_box_render.py, test_components_render.py,
#    test_lids_base_render.py, test_labels_render.py, test_base_bgtk_render.py, and
#    test_sliding_box_render.py compare against. Refuses to overwrite existing goldens unless
#    --force is passed, since a bad/blocked render could otherwise silently replace a good
#    golden with a blank image.
#
# FileGroup: pysolidfive

from __future__ import annotations

import argparse
import sys
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# mock_libfive.py/render_pysolidfive.py now live inside pysolidfive/tests/ (moved there so
# pysolidfive's own test suite is bundled with the package); add that directory too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pysolidfive" / "tests"))

from render_base_bgtk import render_base_bgtk_shape
from render_cap_box import find_bosl2_scad_dir, render_cap_box_shape
from render_components import render_components_shape
from render_labels import render_labels_shape
from render_lids_base import render_lids_base_shape
from render_pysolidfive import find_pythonscad_binary, render_pysolidfive_shape
from render_sliding_box import render_sliding_box_shape
from test_base_bgtk_render import GOLDEN_DIR as BASE_BGTK_GOLDEN_DIR, SHAPES as BASE_BGTK_SHAPES
from test_cap_box_render import GOLDEN_DIR as CAP_BOX_GOLDEN_DIR, IMGSIZE as CAP_BOX_IMGSIZE, SHAPES as CAP_BOX_SHAPES
from test_components_render import GOLDEN_DIR as COMPONENTS_GOLDEN_DIR, SHAPES as COMPONENTS_SHAPES
from test_labels_render import GOLDEN_DIR as LABELS_GOLDEN_DIR, IMGSIZE as LABELS_IMGSIZE, SHAPES as LABELS_SHAPES
from test_lids_base_render import GOLDEN_DIR as LIDS_BASE_GOLDEN_DIR, SHAPES as LIDS_BASE_SHAPES
from test_pysolidfive_render import GOLDEN_DIR as PYSOLIDFIVE_GOLDEN_DIR, SHAPES as PYSOLIDFIVE_SHAPES
from test_sliding_box_render import (
    GOLDEN_DIR as SLIDING_BOX_GOLDEN_DIR,
    IMGSIZE as SLIDING_BOX_IMGSIZE,
    SHAPES as SLIDING_BOX_SHAPES,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite existing golden images")
    args = parser.parse_args()

    if find_pythonscad_binary() is None:
        print("No real PythonSCAD binary found (set PYTHONSCAD_BIN to override). Aborting.")
        return 1

    # Each source has its own golden directory -- pysolidfive/tests/golden_images/ for
    # pysolidfive's own bundled tests, tests/golden_images/ (shared) for everyone else. Do NOT
    # collapse these into one shared GOLDEN_DIR constant again: this loop used to do exactly
    # that (via a single imported GOLDEN_DIR), which silently wrote every *other* library's
    # golden images into whichever module happened to supply that name.
    sources = [(PYSOLIDFIVE_SHAPES, render_pysolidfive_shape, PYSOLIDFIVE_GOLDEN_DIR)]
    if find_bosl2_scad_dir() is None:
        print(
            "No working BOSL2/std.scad found for PythonSCAD (set BOSL2_SCAD_DIR; see "
            "tests/render_cap_box.py's module docstring) -- skipping cap_box/components/"
            "lids_base/labels/base_bgtk/sliding_box shapes."
        )
    else:
        # cap_box's boxes/lids are bigger, more detailed assemblies than the primitive
        # pysolidfive/components shapes -- rendered (and diffed against) at a higher resolution;
        # see test_cap_box_render.py's IMGSIZE.
        sources.append((CAP_BOX_SHAPES, partial(render_cap_box_shape, imgsize=CAP_BOX_IMGSIZE), CAP_BOX_GOLDEN_DIR))
        sources.append((COMPONENTS_SHAPES, render_components_shape, COMPONENTS_GOLDEN_DIR))
        sources.append((LIDS_BASE_SHAPES, render_lids_base_shape, LIDS_BASE_GOLDEN_DIR))
        # Labels are mostly fine surface detail (etched text, thin stripes) -- rendered (and
        # diffed against) at a higher resolution; see test_labels_render.py's IMGSIZE.
        sources.append((LABELS_SHAPES, partial(render_labels_shape, imgsize=LABELS_IMGSIZE), LABELS_GOLDEN_DIR))
        sources.append((BASE_BGTK_SHAPES, render_base_bgtk_shape, BASE_BGTK_GOLDEN_DIR))
        # See test_sliding_box_render.py's IMGSIZE -- same rationale as cap_box's.
        sources.append(
            (SLIDING_BOX_SHAPES, partial(render_sliding_box_shape, imgsize=SLIDING_BOX_IMGSIZE), SLIDING_BOX_GOLDEN_DIR)
        )

    failures = []
    for shapes, render_fn, golden_dir in sources:
        golden_dir.mkdir(exist_ok=True)
        for name, expr in shapes:
            golden = golden_dir / f"{name}.png"
            if golden.is_file() and not args.force:
                print(f"SKIP (exists, use --force to overwrite): {golden}")
                continue

            result = render_fn(expr, golden)
            if not result.ok:
                print(f"FAILED to render {name} ({expr}): {result.error}")
                failures.append(name)
                continue

            print(f"OK: {golden} ({result.triangles} triangles)")

    if failures:
        print(f"\n{len(failures)} shape(s) failed to render: {', '.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
