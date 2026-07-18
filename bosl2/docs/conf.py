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

# LibFile: bosl2/docs/conf.py
#    Sphinx configuration for the pure-Python bosl2 port's API docs. Build with:
#
#        python3 -m pip install sphinx        # once
#        make -C bosl2/docs html              # -> bosl2/wiki/ (checked in)
#
#    Set PYTHONSCAD_BIN to a real PythonSCAD binary to get rendered images and exported STL
#    meshes in the ``bosl2-example`` blocks; without it the build still succeeds and shows source
#    only (see docs/_ext/bosl2_example.py). Unchanged examples reuse their cached image/STL.
#
#    Before autodoc touches the bosl2 modules, this file must (1) put the repo root on sys.path so
#    ``import bosl2`` resolves, and (2) install pysolidfive/tests/mock_libfive.py's
#    ``pythonscad``/``openscad``/``libfive`` stand-ins, because bosl2/shapes2d.py, shapes3d.py and
#    masking.py import ``pythonscad`` at load time (only available inside the real app) -- exactly
#    the reason the bosl2 test-suite's conftest installs the same mock.
#
# FileGroup: bosl2

from __future__ import annotations

import sys
from pathlib import Path

_DOCS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DOCS_DIR.parent.parent

sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "pysolidfive" / "tests"))
sys.path.insert(0, str(_DOCS_DIR / "_ext"))

import mock_libfive  # noqa: E402,F401  -- installs pythonscad/openscad/libfive stubs before autodoc

project = "bosl2 (PythonSCAD port)"
copyright = "Apache License 2.0"
author = "pinkfish"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "stl_viewer",
    "bosl2_example",
]

# bosl2's docstrings use Google-style Args:/Returns:/Example: sections throughout.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_custom_sections = [("Usage", "notes")]

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_typehints = "description"

intersphinx_mapping = {"numpy": ("https://numpy.org/doc/stable/", None)}

templates_path: list[str] = []
exclude_patterns: list[str] = ["_build", "_generated", "_extra"]

# The exported STL meshes live in _extra/_stl/; listing the _extra/ parent in html_extra_path
# copies the _stl/ subdirectory verbatim to the output root (html_extra_path flattens a listed
# directory's *contents* into the root, so the extra nesting level is what preserves the _stl/
# prefix). All doc pages sit at the docs root, so a relative ``_stl/<hash>.stl`` -- what both the
# interactive viewer and the download links use -- resolves from any of them.
html_extra_path = ["_extra"]

html_theme = "alabaster"
html_static_path: list[str] = []
