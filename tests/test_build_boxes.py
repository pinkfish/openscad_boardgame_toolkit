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

# LibFile: tests/test_build_boxes.py
#    Tests for scripts/build_boxes.py's static dependency tracer and section discovery -- the
#    logic that makes `make py` rebuild only what a .py source change affects and pick up newly
#    added @make_box functions without re-running make_files.py. Does not run PythonSCAD.
#
# FileGroup: scripts

import os
import sys
import tempfile
import time
import unittest

REPO = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import build_boxes as bb  # noqa: E402


class TestDependencyFiles(unittest.TestCase):
    def rel(self, paths):
        return {os.path.relpath(p, REPO) for p in paths}

    def test_traces_transitive_toolkit_imports(self):
        # splendor -> sliding_box -> base_bgtk/lids_base/labels/... -> bosl2/*
        deps = self.rel(bb.dependency_files(os.path.join(bb.EXAMPLES, "splendor.py")))
        for expected in ("examples/splendor.py", "base_bgtk.py", "sliding_box.py", "components.py",
                         "bosl2/shapes3d.py", "bosl2/__init__.py", "labels.py"):
            self.assertIn(expected, deps, f"{expected} missing from splendor deps")

    def test_excludes_external_modules(self):
        # native/app modules (pythonscad, openscad) and stdlib resolve to nothing.
        deps = self.rel(bb.dependency_files(os.path.join(bb.EXAMPLES, "demo_py.py")))
        self.assertFalse(any("pythonscad" in d or "openscad" in d for d in deps))

    def test_relative_imports_resolve_within_package(self):
        # bosl2/shapes3d.py does `from .constants import *` etc.
        deps = self.rel(bb.dependency_files(os.path.join(REPO, "bosl2", "shapes3d.py")))
        self.assertIn("bosl2/constants.py", deps)
        self.assertIn("bosl2/shapes3d.py", deps)

    def test_self_included(self):
        p = os.path.join(bb.EXAMPLES, "demo_py.py")
        self.assertIn(os.path.abspath(p), bb.dependency_files(p))


class TestDiscovery(unittest.TestCase):
    def test_example_games_includes_ported(self):
        games = bb.example_games()
        for g in ("demo_py", "splendor", "cascadero", "moonrakers"):
            self.assertIn(g, games)

    def test_sections_returns_marked_boxes(self):
        makes, docs = bb.sections("demo_py")
        self.assertEqual(makes, ["TokenBox", "TokenBoxLid"])
        self.assertEqual(docs, [])


class TestStale(unittest.TestCase):
    def test_missing_output_is_stale(self):
        self.assertTrue(bb._is_stale("/no/such/output.3mf", [], force=False))

    def test_force_is_always_stale(self):
        with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as f:
            f.write(b"x")
            out = f.name
        try:
            self.assertTrue(bb._is_stale(out, [], force=True))
        finally:
            os.unlink(out)

    def test_newer_dep_makes_stale(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "o.3mf")
            dep = os.path.join(d, "src.py")
            with open(out, "w") as f:
                f.write("x")
            time.sleep(0.02)
            with open(dep, "w") as f:
                f.write("y")  # dep newer than out
            self.assertTrue(bb._is_stale(out, [dep], force=False))

    def test_up_to_date_when_deps_older(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "o.3mf")
            dep = os.path.join(d, "src.py")
            with open(dep, "w") as f:
                f.write("y")
            time.sleep(0.02)
            with open(out, "w") as f:
                f.write("x")  # out newer than dep
            self.assertFalse(bb._is_stale(out, [dep], force=False))


if __name__ == "__main__":
    unittest.main()
