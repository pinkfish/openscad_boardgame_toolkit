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

# LibFile: pysolidfive/docs/conf.py
#    Sphinx configuration for pysolidfive's API docs. Build with:
#
#        pip install -e ".[docs]"   # from pysolidfive/
#        make -C docs html
#
#    Two things this file must do before Sphinx's autodoc ever touches pysolidfive itself:
#      1. Put the repo root on sys.path, so `import pysolidfive` resolves the real package
#         (not pysolidfive/ itself -- see pysolidfive/tests/test_pysolidfive.py's own comment
#         about this exact path-depth gotcha).
#      2. Install pysolidfive/tests/mock_libfive.py's `libfive`/`pythonscad` stand-ins into
#         sys.modules *first*. pysolidfive/__init__.py does `import libfive` /
#         `from pythonscad import frep` at module load time, which only exist inside
#         PythonSCAD's embedded interpreter -- exactly the same reason the test suite needs the
#         mock installed before `import pysolidfive`. Import it flat (`import mock_libfive`,
#         with its directory added to sys.path), not as `pysolidfive.tests.mock_libfive` -- the
#         dotted form forces Python to import the real pysolidfive package first, which is the
#         whole problem being worked around.
#
# FileGroup: pysolidfive

from __future__ import annotations

import sys
from pathlib import Path

_DOCS_DIR = Path(__file__).resolve().parent
_PYSOLIDFIVE_DIR = _DOCS_DIR.parent
_REPO_ROOT = _PYSOLIDFIVE_DIR.parent

sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_PYSOLIDFIVE_DIR / "tests"))
sys.path.insert(0, str(_DOCS_DIR / "_ext"))

import mock_libfive  # noqa: E402  (must be imported, and installed, before pysolidfive/autodoc)

project = "pysolidfive"
copyright = "Apache License 2.0"
author = "pinkfish"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "pythonscad_example",
]

# pysolidfive's docstrings use Google-style `Args:`/`Returns:`/`Examples:` sections throughout.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True

# Keep source order (matches the file's own logical grouping -- cuboid()/cyl()/sphere()/etc. in
# the same order they're documented in the module docstring's "Shapes covered" list) rather than
# alphabetical.
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
}

templates_path: list[str] = []
exclude_patterns: list[str] = ["_build", "_generated"]

html_theme = "alabaster"
html_static_path: list[str] = []
