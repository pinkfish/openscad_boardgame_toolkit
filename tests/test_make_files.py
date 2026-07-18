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

# LibFile: tests/test_make_files.py
#    Tests for scripts/make_lib.scan_py_sections -- the .py box/doc "section" scanner that
#    scripts/make_files.py uses to decide which functions get mmu/single 3mf (and png) build
#    rules. Covers all three marker forms (the @make_box/@document_box decorators and the legacy
#    `# `make` me` comment on the def line or the line after it), plus write_if_changed.
#
# FileGroup: scripts

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts"))

from make_lib import scan_py_sections, write_if_changed  # noqa: E402


def scan(text):
    return sorted(scan_py_sections(text.splitlines()))


class TestScanPySections(unittest.TestCase):
    def test_make_box_decorator(self):
        self.assertEqual(scan("@make_box\ndef A():\n    return 1\n"), [("A", "make")])

    def test_document_box_decorator(self):
        self.assertEqual(scan("@document_box\ndef D():\n    return 1\n"), [("D", "document")])

    def test_comment_on_def_line(self):
        self.assertEqual(scan("def B():  # `make` me\n    return 1\n"), [("B", "make")])

    def test_comment_on_line_after_def(self):
        # This is the form scripts/s2p.py emits when converting a .scad example.
        self.assertEqual(scan("def C():\n    # `make` me\n    return 1\n"), [("C", "make")])

    def test_unmarked_function_ignored(self):
        self.assertEqual(scan("def E():\n    return 1\n"), [])

    def test_decorator_with_blank_line_below_still_binds(self):
        # decorators must be contiguous above the def; a blank line between breaks binding.
        self.assertEqual(scan("@make_box\n\ndef F():\n    return 1\n"), [])

    def test_make_and_document_together(self):
        self.assertEqual(
            scan("@make_box\n@document_box\ndef G():\n    return 1\n"),
            [("G", "document"), ("G", "make")],
        )

    def test_multiple_functions(self):
        text = (
            "@make_box\ndef A():\n    return 1\n\n"
            "def B():  # `make` me\n    return 2\n\n"
            "def plain():\n    return 3\n\n"
            "@document_box\ndef D():\n    return 4\n"
        )
        self.assertEqual(scan(text), [("A", "make"), ("B", "make"), ("D", "document")])

    def test_only_top_level_defs(self):
        # a nested/indented def is not a module-level section (DEF_RE anchors at column 0).
        self.assertEqual(scan("@make_box\ndef Outer():\n    def inner():  # `make` me\n        pass\n"),
                         [("Outer", "make")])


class TestWriteIfChanged(unittest.TestCase):
    def test_writes_when_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "sub", "f.txt")
            write_if_changed(p, "hello")
            with open(p) as fh:
                self.assertEqual(fh.read(), "hello")

    def test_no_rewrite_when_identical(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f.txt")
            write_if_changed(p, "same")
            mtime = os.path.getmtime(p)
            os.utime(p, (mtime - 100, mtime - 100))  # backdate
            before = os.path.getmtime(p)
            write_if_changed(p, "same")  # identical -> must not rewrite
            self.assertEqual(os.path.getmtime(p), before)

    def test_rewrites_when_changed(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f.txt")
            write_if_changed(p, "a")
            write_if_changed(p, "b")
            with open(p) as fh:
                self.assertEqual(fh.read(), "b")


if __name__ == "__main__":
    unittest.main()
