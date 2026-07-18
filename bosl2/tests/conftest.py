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

# pytest fixtures/setup for the bosl2 package test-suite.
#
# The bosl2 modules that touch native geometry (shapes2d/shapes3d/masking, and the
# .polygon()/.polyhedron() FFI boundaries) import `pythonscad`/`openscad` at load time. This
# conftest installs the shared numeric mock for those (and `libfive`) BEFORE any test module --
# and therefore any bosl2 module -- is imported, so the whole suite runs without a real
# PythonSCAD app. The mock lives in pysolidfive/tests/mock_libfive.py and installs itself into
# sys.modules on import (it is deliberately imported as a flat top-level module).

import os
import sys

_HERE = os.path.dirname(__file__)
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_MOCK_DIR = os.path.join(_ROOT, "pysolidfive", "tests")

for _p in (_ROOT, _MOCK_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import mock_libfive  # noqa: E402,F401  -- installs pythonscad/openscad/libfive stubs on import
