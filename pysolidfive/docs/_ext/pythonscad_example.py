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

# LibFile: pysolidfive/docs/_ext/pythonscad_example.py
#    Sphinx extension providing a `.. pythonscad-example::` directive: the directive's content is
#    a full pysolidfive-using Python script (ending in `shape.show()`, same convention as a real
#    PythonSCAD python-mode file), which gets rendered with the *real* PythonSCAD binary and
#    embedded as an image right next to its own source code in the generated docs -- the same
#    "show the code, show what it actually renders" idea as matplotlib's `.. plot::` directive, or
#    openscad-docsgen's `Example:` blocks (which this project's docs/ folder -- for the original
#    .scad files -- already uses; see that folder's module docstring conventions, which pysolidfive's
#    own LibFile:/FileGroup:/Usage:: comments were deliberately written to mirror).
#
#    Reuses pysolidfive/tests/render_pysolidfive.py's render_script()/find_pythonscad_binary()
#    verbatim -- the same subprocess/skip-gracefully plumbing the test suite already relies on,
#    not a separate reimplementation.
#
#    Rendered images are cached in docs/_generated/ by a hash of (code, imgsize), mirroring the
#    parent repo's own docs/.source_hashes idea (skip re-rendering unchanged examples) but simpler
#    -- the hash *is* the filename, so there's no separate manifest to keep in sync.
#
#    If no PythonSCAD binary is available (or a render fails), the directive degrades gracefully:
#    emits a build warning and still shows the source code, just without an image, rather than
#    failing the whole `make html` -- the same philosophy as the test suite's self.skipTest().
#
# FileGroup: pysolidfive

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util import logging

_DOCS_DIR = Path(__file__).resolve().parent.parent
_GENERATED_DIR = _DOCS_DIR / "_generated"

# pysolidfive/docs/_ext/pythonscad_example.py -> _ext -> docs -> pysolidfive -> pysolidfive/tests.
sys.path.insert(0, str(_DOCS_DIR.parent / "tests"))

from render_pysolidfive import PROJECT_ROOT, find_pythonscad_binary, render_script  # noqa: E402

_logger = logging.getLogger(__name__)


def _parse_imgsize(raw: str) -> tuple[int, int]:
    w, h = (int(v.strip()) for v in raw.split(","))
    return w, h


class PythonSCADExampleDirective(Directive):
    """`.. pythonscad-example::` -- see this module's docstring."""

    has_content = True
    option_spec = {"imgsize": directives.unchanged}

    def run(self) -> list[nodes.Node]:
        code = "\n".join(self.content)
        imgsize = _parse_imgsize(self.options.get("imgsize", "320,240"))

        result_nodes: list[nodes.Node] = []

        code_node = nodes.literal_block(code, code)
        code_node["language"] = "python"
        result_nodes.append(code_node)

        image_rel_path = self._render_and_cache(code, imgsize)
        if image_rel_path is not None:
            image_node = nodes.image(uri=image_rel_path)
            result_nodes.append(image_node)

        return result_nodes

    def _render_and_cache(self, code: str, imgsize: tuple[int, int]) -> str | None:
        digest = hashlib.sha256(f"{imgsize}\n{code}".encode()).hexdigest()[:16]
        out_png = _GENERATED_DIR / f"{digest}.png"

        if out_png.is_file():
            return f"/_generated/{out_png.name}"

        if find_pythonscad_binary() is None:
            _logger.warning(
                f"pythonscad-example: no PythonSCAD binary found (set PYTHONSCAD_BIN) -- "
                f"showing source only, no rendered image, for:\n{code}"
            )
            return None

        _GENERATED_DIR.mkdir(exist_ok=True)
        script = f"import sys\nsys.path.insert(0, {str(PROJECT_ROOT)!r})\nimport pysolidfive\n{code}\n"
        try:
            # High-res SDF meshes can take a while (a single frep() render has hit 60s+ under
            # load); a generous timeout here, and TimeoutExpired degrades to a warning like any
            # other render failure rather than killing the whole `make html`.
            result = render_script(script, out_png, imgsize=imgsize, timeout=300.0)
        except subprocess.TimeoutExpired:
            _logger.warning(f"pythonscad-example: render timed out for:\n{code}")
            return None
        if not result.ok:
            _logger.warning(f"pythonscad-example: render failed ({result.error}) for:\n{code}")
            return None

        return f"/_generated/{out_png.name}"


def setup(app) -> dict:
    # No html_static_path wiring needed: the `/_generated/...` URIs above are absolute-from-
    # srcdir image:: references (leading "/"), which Sphinx already collects and copies to the
    # output automatically, same as any other `image::`/`figure::` target in a source file.
    app.add_directive("pythonscad-example", PythonSCADExampleDirective)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
