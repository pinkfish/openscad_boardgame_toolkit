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

# LibFile: bosl2/docs/_ext/bosl2_example.py
#    Sphinx extension providing a ``.. bosl2-example::`` directive: the directive's content is a
#    short bosl2-using Python snippet ending in ``<obj>.show()`` (the same convention as a real
#    PythonSCAD python-mode file). At build time it is prepended with a standard preamble (repo
#    root on sys.path, common bosl2 imports) and rendered with the *real* PythonSCAD binary, and
#    the generated docs show, side by side: the snippet's source, the PNG the app rendered, and a
#    download link to the exported STL mesh for the object. This is the same "show the code, show
#    what it actually builds" idea as matplotlib's ``.. plot::`` and openscad-docsgen's
#    ``Example:`` blocks that the parent repo's docs/ (for the .scad files) already use.
#
#    The image render reuses pysolidfive/tests/render_pysolidfive.py's render_script(); the STL
#    export reuses bosl2/tests/render_stl.py's render_stl_script() -- the same subprocess/skip-
#    gracefully plumbing the two test suites rely on, not a reimplementation.
#
#    Rendered PNGs are cached in docs/_generated/ and STLs in docs/_stl/, keyed by a hash of the
#    snippet, so unchanged examples are not re-rendered. If no PythonSCAD binary is available (or
#    a render fails, e.g. a 2-D example that cannot export to STL), the directive degrades
#    gracefully -- it emits a build warning and still shows the source, just without the image
#    and/or STL link, rather than failing the whole ``make html``.
#
# FileGroup: bosl2

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

_DOCS_DIR = Path(__file__).resolve().parent.parent
_GENERATED_DIR = _DOCS_DIR / "_generated"       # PNG previews (collected by Sphinx's image handling)
# Exported meshes live under _extra/_stl/ so that html_extra_path=["_extra"] copies the whole
# _stl/ subdir (not just its flattened contents) to the output root, keeping the ``_stl/<hash>.stl``
# URIs the viewer and download links use valid.
_STL_DIR = _DOCS_DIR / "_extra" / "_stl"

# bosl2/docs/_ext -> docs -> bosl2 -> repo root.
_REPO_ROOT = _DOCS_DIR.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "pysolidfive" / "tests"))
sys.path.insert(0, str(_REPO_ROOT / "bosl2" / "tests"))

from render_pysolidfive import render_script  # noqa: E402
from render_stl import find_pythonscad_binary, render_stl_script  # noqa: E402
from stl_viewer import stl_viewer_html  # noqa: E402

_logger = logging.getLogger(__name__)

# Prepended to every snippet: put the repo root on sys.path and import the common bosl2 names, so
# examples can be terse (`s3.cuboid(...)`, `Path(...)`, `Bezier(...)`) and mirror how the toolkit
# is actually used.
_PREAMBLE = (
    "import sys, math\n"
    f"sys.path.insert(0, {str(_REPO_ROOT)!r})\n"
    "import numpy as np\n"
    "import bosl2\n"
    "import bosl2.shapes3d\n"
    "import bosl2.shapes2d\n"
    "import bosl2.shapes3d as s3\n"
    "import bosl2.shapes2d as s2\n"
    "from bosl2.paths import Path, Path3D\n"
    "from bosl2.regions import Region\n"
    "from bosl2.beziers import Bezier, BezierPatch\n"
    "from bosl2.vnf import VNF\n"
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
    "from bosl2.constants import *\n"
)


def _parse_imgsize(raw: str) -> tuple[int, int]:
    w, h = (int(v.strip()) for v in raw.split(","))
    return w, h


class Bosl2ExampleDirective(Directive):
    """``.. pythonscad-example::`` -- render a bosl2 snippet to an image + downloadable STL. See module docstring."""

    has_content = True
    option_spec = {"imgsize": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        code = "\n".join(self.content)
        imgsize = _parse_imgsize(self.options.get("imgsize", "400,300"))
        script = _PREAMBLE + code + "\n"

        out: list[nodes.Node] = []
        code_node = nodes.literal_block(code, code)
        code_node["language"] = "python"
        out.append(code_node)

        # Prefer an interactive 3-D STL viewer (the whole point of the exported mesh); fall back to
        # the static PNG preview when the example has no STL (a 2-D-only object, or an open surface).
        stl_uri = self._render_stl(script, code)
        if stl_uri is not None:
            out.append(nodes.raw("", stl_viewer_html(stl_uri), format="html"))
            para = nodes.paragraph()
            para += nodes.reference("", "⬇ Download STL mesh", refuri=stl_uri)
            out.append(para)
        else:
            img_uri = self._render_png(script, code, imgsize)
            if img_uri is not None:
                out.append(nodes.image(uri=img_uri))
        return out

    def _render_png(self, script: str, code: str, imgsize: tuple[int, int]) -> str | None:
        digest = hashlib.sha256(f"png\n{imgsize}\n{code}".encode()).hexdigest()[:16]
        out_png = _GENERATED_DIR / f"{digest}.png"
        if out_png.is_file():
            return f"/_generated/{out_png.name}"
        if find_pythonscad_binary() is None:
            _logger.warning(f"bosl2-example: no PythonSCAD binary (set PYTHONSCAD_BIN); source only for:\n{code}")
            return None
        _GENERATED_DIR.mkdir(exist_ok=True)
        try:
            result = render_script(script, out_png, imgsize=imgsize, timeout=300.0)
        except subprocess.TimeoutExpired:
            _logger.warning(f"bosl2-example: image render timed out for:\n{code}")
            return None
        if not result.ok:
            _logger.warning(f"bosl2-example: image render failed ({result.error}) for:\n{code}")
            return None
        return f"/_generated/{out_png.name}"

    def _render_stl(self, script: str, code: str) -> str | None:
        digest = hashlib.sha256(f"stl\n{code}".encode()).hexdigest()[:16]
        out_stl = _STL_DIR / f"{digest}.stl"
        if out_stl.is_file():
            return f"_stl/{out_stl.name}"
        if find_pythonscad_binary() is None:
            return None
        _STL_DIR.mkdir(exist_ok=True)
        try:
            result = render_stl_script(script, out_stl, timeout=300.0)
        except subprocess.TimeoutExpired:
            _logger.warning(f"bosl2-example: STL export timed out for:\n{code}")
            return None
        if not result.ok:
            # 2-D examples (a Path outline, a region) legitimately have no STL -- info, not warning.
            _logger.info(f"bosl2-example: no STL for example ({result.error})")
            return None
        return f"_stl/{out_stl.name}"


def setup(app) -> dict:
    # Registered as ``pythonscad-example`` to match the name the bosl2 docstrings (and pysolidfive's
    # docs) already use; ``bosl2-example`` is kept as an alias.
    app.add_directive("pythonscad-example", Bosl2ExampleDirective)
    app.add_directive("bosl2-example", Bosl2ExampleDirective)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
