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

# LibFile: pysolidfive/tests/__init__.py
#    pysolidfive's own test suite, bundled inside the package so it stays self-contained (no
#    dependency on the parent repo's tests/ directory). Also used by the parent repo's own
#    tests/ suite, which shares mock_libfive.py/render_pysolidfive.py's render/mock
#    infrastructure -- see those modules' docstrings.
#
#    CAVEAT: don't import anything in here via the dotted form (`pysolidfive.tests.mock_libfive`,
#    `import pysolidfive.tests` etc.) -- that forces Python to import the real pysolidfive
#    package first (parent packages always load before their submodules), which does
#    `import libfive` at module level and fails outside PythonSCAD. Every consumer instead adds
#    this directory straight to `sys.path` and uses flat imports (`import mock_libfive`,
#    `from render_pysolidfive import ...`), bypassing the pysolidfive package entirely. This
#    `__init__.py` exists so `pysolidfive/tests/` is still a normal, well-formed Python package
#    for tooling (linters, `python -m unittest discover -s pysolidfive/tests`, etc.), not because
#    anything actually imports through it.
#
# FileGroup: pysolidfive
