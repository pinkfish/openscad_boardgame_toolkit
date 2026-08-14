# SPDX-License-Identifier: Apache-2.0
"""Tests for the pyboxbuilder package.

Exports default to 256 facets per circle, which is right for the 3MFs that go
to a slicer and wrong for a test run: it took this suite from about a minute to
over five. **A CI pass is not a build.** These tests check that the export
pipeline names, counts, caches and deletes the right files, which does not
depend on how finely a curve is tessellated, so they run exports coarse and
write only to temporary directories — no printable output is produced. The
tests that care about the shipped default clear this and assert it explicitly.
"""

import os

os.environ.setdefault("PYBOXBUILDER_EXPORT_FN", "12")
