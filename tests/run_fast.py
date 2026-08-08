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

# LibFile: tests/run_fast.py
#    The inner-loop test run: everything that does NOT drive the PythonSCAD app.
#
#    The full suite is 296 tests in ~390s, but the time is not spread evenly -- it is almost
#    entirely app spawns, and one module dominates:
#
#        test_lid_patterns        ~250s   sweeps EVERY ShapeType through the app, three times
#        test_box_geometry         ~36s
#        test_shapes_render        ~28s
#        test_all_boxes_render     ~17s
#        ...the other *_render     ~55s
#        everything else            1.4s   <- 158 of the 296 tests
#
#    So the pure-Python half of the suite costs about a second, and this runner is what you
#    want on every edit. Run the app-driven modules before you push, or when you touch the
#    geometry they cover.
#
#    Usage:
#        python3 tests/run_fast.py              # the 1.4s subset
#        python3 tests/run_fast.py -v           # ...verbose
#        python3 tests/run_fast.py test_no_lid  # ...only modules matching a substring
#
#    The full suite stays exactly as it was:
#        python3 -m unittest discover -s tests -p "test_*.py"
#
#    NOTE on the app-driven modules: raising BGTK_TEST_WORKERS does not buy much here -- the
#    sweep is already process-parallel and this machine has 4 cores (3 workers 249s, 6 workers
#    233s). Making test_lid_patterns cheap means sweeping a representative pattern per kind
#    (TiledPattern / TilingPattern / AreaPattern) by default rather than the whole enum.
#
# FileGroup: Tests

import os
import re
import sys
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_DIR)

#: Modules that spawn the PythonSCAD binary. They are the whole runtime of the suite, and they
#: cannot run at all without the app installed.
APP_DRIVEN = re.compile(r"_render$|^test_box_geometry$|^test_lid_patterns$")


def build_suite(name_filter: str = "") -> tuple[unittest.TestSuite, set[str]]:
    """Return the non-app-driven tests, plus the set of module names left out.

    Args:
        name_filter: Keep only modules whose name contains this substring (empty keeps all).

    Returns:
        The suite to run and the names of the modules that were skipped.
    """
    loader = unittest.defaultTestLoader
    kept = unittest.TestSuite()
    skipped: set[str] = set()

    def walk(suite: unittest.TestSuite) -> None:
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                walk(test)
                continue
            module = type(test).__module__
            if APP_DRIVEN.search(module):
                skipped.add(module)
            elif name_filter and name_filter not in module:
                skipped.add(module)
            else:
                kept.addTest(test)

    walk(loader.discover(TESTS_DIR, pattern="test_*.py", top_level_dir=TESTS_DIR))
    return kept, skipped


def main() -> int:
    """Run the fast subset and report what was left out."""
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbosity = 2 if any(a in ("-v", "--verbose") for a in sys.argv[1:]) else 1

    suite, skipped = build_suite(args[0] if args else "")
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)

    app_only = sorted(m for m in skipped if APP_DRIVEN.search(m))
    if app_only:
        print(
            f"\nSkipped {len(app_only)} app-driven module(s): {', '.join(app_only)}"
            '\nRun them with: python3 -m unittest discover -s tests -p "test_*.py"'
        )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.path.insert(0, TESTS_DIR)
    sys.path.insert(0, PROJECT_ROOT)
    raise SystemExit(main())
