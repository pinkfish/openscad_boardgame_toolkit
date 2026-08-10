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

# LibFile: tests/test_lid_patterns.py
#    EVERY lid pattern, built the way a lid builds it -- the matrix nothing covered.
#
#    The pattern library was only ever tested one call deep: test_shape_type.py invoked
#    ShapeByType() directly WITH the layout context supplied by hand, which is precisely the
#    condition that never held in production. Measured through an actual lid, 11 of 42
#    ShapeTypes worked; the rest raised, most of them because the layout context they needed
#    had no way to reach them.
#
#    Three levels, cheapest first:
#      1. every pattern FILLS its area          (all 42)
#      2. every pattern lands on a real lid     (measured bounding boxes)
#      3. every fill actually covers the area it was given
#
#    EXPECTED_BROKEN is the live inventory of what is still missing, by cause. Shrinking it
#    is the work; an entry that starts passing fails the staleness test below.
#
# FileGroup: Tests

import ast
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from render_app import PROJECT_ROOT, measure_python, render_available

#: How many app processes a sweep runs at once. Each one is a separate PythonSCAD doing its
#: own CSG, so this is bounded by RAM as much as by cores -- a dense lattice lid is hundreds
#: of megabytes while it meshes, and oversubscribing an 8GB machine swaps and ends up slower
#: than running serially. Threads, not processes: every worker is blocked in subprocess.run.
SWEEP_WORKERS = int(os.environ.get("BGTK_TEST_WORKERS") or max(1, min(3, (os.cpu_count() or 2) - 1)))

# ---------------------------------------------------------------------------
# What does not work yet, by cause. Every entry is a bug, not a preference.
# ---------------------------------------------------------------------------

#: Patterns that still do not build, by cause. EMPTY -- every ShapeType in the enum now
#: builds as a lid pattern. Keep it that way: an entry here is a bug, and the staleness test
#: below fails if one is listed that actually works.
EXPECTED_BROKEN: dict[str, str] = {}

#: Patterns that FILL correctly but cannot be meshed into a lid in reasonable time, so the
#: lid-level sweep skips them. Separate from EXPECTED_BROKEN on purpose: these are not
#: missing, they build 2-D fill like everything else, and the coverage/staleness tests above
#: still hold them to that. What they cannot survive is the boolean work at mesh time.
#:
#: Each entry is a DEFECT with a measured cause, not a tolerance. Removing one means fixing
#: the geometry, not raising the timeout.
TOO_SLOW_TO_MESH: dict[str, str] = {}
# EMPTY. FLYING_BIRD lived here until its tile was fixed: the outline is 186 points of
# fine concave detail and Path2D.offset() left every offset of it self-intersecting, so
# tiling twenty tangled rings never finished. base_bgtk.outline_shell() offsets natively
# and clips those away -- the lid now measures in ~1.6s. An entry here is a DEFECT with a
# measured cause, never a tolerance: removing one means fixing geometry, not raising a
# timeout.

# What used to be in this list, and what each took:
#   * LIZARD / GOOSE / CHICKEN / SHEEP / BIRD / FLYING_BIRD / VORONOI -- the tesselations/
#     modules these route to were unreachable: shape_type.py never put that directory on
#     sys.path, so the imports failed and the branches were stubbed out. HILBERT was the one
#     genuinely absent from both stacks and is newly authored (hilbert.py).
#   * DROP / PEGASUS -- two real bugs in square_tesselation: `Path.to_list` is a PROPERTY that
#     was being called ("'list' object is not callable"), and an osuse BOSL2 region difference
#     that aborted the process.
#   * LEAF / LEAF_VEINS -- the leaf outline did its region algebra through osuse'd BOSL2, and a
#     failing assert in there kills the PROCESS rather than raising
#     (tests/repro_osuse_assert_aborts.py). Rebuilt on direct 2-D CSG; tesselations.py no
#     longer calls osuse at all.
#   * The 15 pentagon families and both Penrose tilings -- were _sdf, so reaching a lid meant
#     meshing; both modules emit direct CSG now.

#: The area the tests fill. Deliberately modest: cell count -- and so render cost -- grows
#: with the AREA, and a compound tiling like DELTOID_TRIHEXAGONAL is ~600 cells on a
#: 140x100 lid (minutes) against ~230 here (seconds).
AREA_W, AREA_L = 80.0, 60.0


def shape_type_names() -> list[str]:
    """Every ShapeType member name, read from the source.

    The toolkit can only be IMPORTED inside the PythonSCAD app, so the enum is parsed
    rather than imported -- which still means a new ShapeType is covered the moment it is
    added, without anyone remembering to list it here."""
    tree = ast.parse((Path(PROJECT_ROOT) / "base_bgtk.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ShapeType":
            return [
                t.targets[0].id
                for t in node.body
                if isinstance(t, ast.Assign) and isinstance(t.targets[0], ast.Name) and t.targets[0].id != "NONE"
            ]
    raise AssertionError("ShapeType enum not found in base_bgtk.py")


#: Set to sweep EVERY pattern through the lid tests instead of one per kind.
#: ``LID_PATTERN_FULL=1 python3 -m unittest discover -s tests -p "test_lid_patterns.py"``
FULL_LID_SWEEP = os.environ.get("LID_PATTERN_FULL") == "1"


def pattern_kinds() -> "dict[str, str]":
    """Each ShapeType's pattern KIND (TiledPattern / TilingPattern / AreaPattern).

    Classified in-process: :func:`~patterns.pattern_for` is the routing table and is pure
    Python, so this costs nothing and needs no app. Anything that will not classify is left
    out and picked up by the fill sweep, which still covers every type.
    """
    try:
        from patterns import pattern_for
        from shape_type import MakeShapeObject
        from base_bgtk import ShapeType
    except Exception:  # pragma: no cover - only when the toolkit will not import at all
        return {}
    kinds: dict[str, str] = {}
    for name in shape_type_names():
        member = getattr(ShapeType, name, None)
        if member is None:
            continue
        try:
            pattern = pattern_for(MakeShapeObject(shape_type=member, shape_width=12, shape_thickness=2))
        except Exception:
            continue
        if pattern is not None:
            kinds[name] = type(pattern).__name__
    return kinds


def lid_sweep_names(candidates: list[str]) -> list[str]:
    """The patterns to put on a real LID: one per kind, unless FULL_LID_SWEEP.

    Building a lid costs ~2s a pattern and the sweep runs twice, so all 42 of them came to
    284s -- over half the entire test suite -- to re-prove the same three things about the
    lid PIPELINE. What the pipeline actually varies on is the kind of pattern it is handed
    (a motif stamped per cell, a tile that places itself, or a region filled in one shot),
    so one representative of each exercises every path through it.

    Coverage is not lost, it is moved: PatternFillTest still sweeps EVERY ShapeType (13s,
    no meshing), which is what catches a type that is missing, misrouted or broken. This
    only trims the expensive re-proof. Set ``LID_PATTERN_FULL=1`` for the whole sweep --
    worth doing when patterns.py or the lid pipeline changes.
    """
    if FULL_LID_SWEEP:
        return candidates
    kinds = pattern_kinds()
    if not kinds:
        return candidates
    chosen: dict[str, str] = {}
    for name in candidates:
        kind = kinds.get(name)
        if kind is not None and kind not in chosen:
            chosen[kind] = name
    picked = set(chosen.values())
    # DENSE_HEX is the reference every other lid is measured against, so it is never dropped.
    if "DENSE_HEX" in candidates:
        picked.add("DENSE_HEX")
    return [n for n in candidates if n in picked]


def _sweep_serial(script_body: str, names: list[str]) -> tuple[dict, dict]:
    """Run *script_body* (a ``%r``-formatted name list) over *names*, surviving aborts.

    A pattern that aborts the app takes the whole process down mid-sweep, so the run
    resumes in a fresh process from the next unreported name -- one extra process per
    aborting pattern instead of losing every result after it."""
    boxes: dict = {}
    reports: dict = {}
    remaining = list(names)
    while remaining:
        result = measure_python(script_body % (remaining,), timeout=900)
        boxes.update(result.boxes)
        reports.update(result.reports)
        done = [n for n in remaining if n in result.boxes or n in result.reports]
        if not done:   # the first pattern in the batch killed the process
            reports[remaining[0]] = "aborted the app"
            done = [remaining[0]]
        remaining = [n for n in remaining if n not in done]
    reports.pop("DONE", None)
    return boxes, reports


def _sweep(script_body: str, names: list[str]) -> tuple[dict, dict]:
    """:func:`_sweep_serial` spread over :data:`SWEEP_WORKERS` app processes.

    Names are dealt round-robin rather than in contiguous blocks: cost per pattern varies by
    orders of magnitude (a dense lattice against a single square), and consecutive members of
    the enum are related, so blocks would pile all the expensive ones into one worker.

    Each worker keeps the abort-resume loop over its own slice, so an aborting pattern still
    only costs one extra process -- and now only stalls its own slice."""
    if SWEEP_WORKERS <= 1 or len(names) <= 1:
        return _sweep_serial(script_body, names)

    slices = [names[i::SWEEP_WORKERS] for i in range(SWEEP_WORKERS)]
    slices = [s for s in slices if s]
    boxes: dict = {}
    reports: dict = {}
    with ThreadPoolExecutor(max_workers=len(slices)) as pool:
        for part_boxes, part_reports in pool.map(
            lambda s: _sweep_serial(script_body, s), slices
        ):
            boxes.update(part_boxes)
            reports.update(part_reports)
    return boxes, reports


_FILL_SCRIPT = """
from base_bgtk import *
from shape_type import MakeShapeObject
from patterns import PatternArea, pattern_for
import pybosl2.shapes3d as _s3

AREA = PatternArea(width=%(w)r, length=%(l)r)
for _name in %%r:
    _opts = MakeShapeObject(shape_type=getattr(ShapeType, _name), shape_width=12, shape_thickness=2)
    try:
        _fill = pattern_for(_opts, layout_width=12).fill(AREA)
        if _fill is None:
            report(_name, 'the pattern filled nothing')
        else:
            report(_name, 'built:' + type(_fill).__name__)
    except Exception as _exc:
        report(_name, type(_exc).__name__ + ': ' + str(_exc).replace(chr(10), ' ')[:70])
report('DONE', 'yes')
_s3.cuboid([1, 1, 1]).show()
""" % {"w": AREA_W, "l": AREA_L}


_FILL_MEASURE_SCRIPT = """
from base_bgtk import *
from shape_type import MakeShapeObject
from patterns import PatternArea, pattern_for
import pybosl2.shapes3d as _s3

AREA = PatternArea(width=%(w)r, length=%(l)r)
for _name in %%r:
    _opts = MakeShapeObject(shape_type=getattr(ShapeType, _name), shape_width=12, shape_thickness=2)
    try:
        measure(_name, pattern_for(_opts, layout_width=12).fill(AREA).linear_extrude(height=1))
    except Exception as _exc:
        report(_name, type(_exc).__name__)
report('DONE', 'yes')
_s3.cuboid([1, 1, 1]).show()
""" % {"w": AREA_W, "l": AREA_L}


_LID_SCRIPT = """
from base_bgtk import *
from box_base import BoxSpec, Lid
from shape_type import MakeShapeObject
from sliding_box import SlidingBox
import pybosl2.shapes3d as _s3

for _name in %%r:
    _opts = MakeShapeObject(shape_type=getattr(ShapeType, _name), shape_width=12, shape_thickness=2)
    try:
        measure(_name, SlidingBox(BoxSpec(size=[%(w)r, %(l)r, 25], label='t', lid=Lid(shape_options=_opts))).make_lid())
    except Exception as _exc:
        report(_name, type(_exc).__name__ + ': ' + str(_exc).replace(chr(10), ' ')[:70])
report('DONE', 'yes')
_s3.cuboid([1, 1, 1]).show()
""" % {"w": AREA_W, "l": AREA_L}


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class PatternFillTest(unittest.TestCase):
    """Level 1: every ShapeType must FILL a region -- the thing 21 of them could not do."""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.names = shape_type_names()
        _, cls.reports = _sweep(_FILL_SCRIPT, cls.names)

    def test_every_pattern_fills_its_area(self):
        broken = {
            n: r for n, r in self.reports.items()
            if not r.startswith("built:") and n not in EXPECTED_BROKEN
        }
        self.assertEqual(
            {}, broken,
            "patterns that should fill but did not (see patterns.py for the routing):\n"
            + "\n".join(f"  {n}: {r}" for n, r in sorted(broken.items())),
        )

    def test_expected_broken_list_is_not_stale(self):
        """An EXPECTED_BROKEN entry that now works must be deleted from the list."""
        fixed = sorted(n for n in EXPECTED_BROKEN if self.reports.get(n, "").startswith("built:"))
        self.assertEqual([], fixed, f"these work now -- remove them from EXPECTED_BROKEN: {fixed}")

    def test_every_shape_type_is_accounted_for(self):
        """No ShapeType may be silently missing from the sweep."""
        missing = sorted(set(self.names) - set(self.reports))
        self.assertEqual([], missing, f"ShapeTypes the sweep never reported on: {missing}")


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class PatternOnLidTest(unittest.TestCase):
    """Levels 2 and 3: the measurable (direct-CSG) patterns, on a real lid."""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.names = lid_sweep_names([
            n for n in shape_type_names()
            if n not in EXPECTED_BROKEN and n not in TOO_SLOW_TO_MESH
        ])
        cls.lids, cls.lid_errors = _sweep(_LID_SCRIPT, cls.names)
        cls.fills, cls.fill_errors = _sweep(_FILL_MEASURE_SCRIPT, cls.names)

    def test_every_pattern_builds_a_lid(self):
        self.assertEqual(
            {}, self.lid_errors,
            "patterns that fill but cannot be built into a lid:\n"
            + "\n".join(f"  {n}: {e}" for n, e in sorted(self.lid_errors.items())),
        )

    def test_pattern_never_changes_the_lid(self):
        """A pattern is decoration cut INTO the lid: it can never move or resize the part.

        The pattern is clipped to the boundary inset, so every lid must measure the same
        whichever pattern is on it. A pattern laid out in the wrong frame shows up here."""
        self.assertIn("DENSE_HEX", self.lids, "the reference pattern did not build")
        reference = self.lids["DENSE_HEX"]
        for name, box in sorted(self.lids.items()):
            with self.subTest(pattern=name):
                for axis in range(3):
                    self.assertAlmostEqual(
                        reference.size[axis], box.size[axis], delta=0.6,
                        msg=f"{name}: pattern changed the lid size on axis {axis} "
                            f"({box} vs reference {reference})",
                    )
                    self.assertAlmostEqual(
                        reference.position[axis], box.position[axis], delta=0.6,
                        msg=f"{name}: pattern moved the lid on axis {axis} "
                            f"({box} vs reference {reference})",
                    )

    def test_fill_covers_the_area_it_was_given(self):
        """A pattern's fill must CONTAIN the region it was handed.

        A tiling laid out around the grid origin instead of the area still produces
        geometry and still fits inside the lid -- it just leaves part of the lid blank,
        which comparing the finished lid cannot see. So the fill is measured on its own.

        Containment, not size or centring: overrunning the area is normal and expected
        (the caller clips), so the only thing a pattern owes the area is covering it. The
        lattices overrun heavily -- DENSE_HEX fills 158 x 142 for an 80 x 60 area, because
        the cell counts are worked out from the cell width but stepped by the row pitch."""
        for name, box in sorted(self.fills.items()):
            with self.subTest(pattern=name):
                for axis, (lo, hi, extent) in enumerate(
                    ((box.x, box.x + box.width, AREA_W), (box.y, box.y + box.length, AREA_L))
                ):
                    self.assertLessEqual(
                        lo, 0.5, f"{name}: fill starts inside the area on axis {axis}, "
                                 f"leaving a gap at the near edge: {box}",
                    )
                    self.assertGreaterEqual(
                        hi, extent - 0.5, f"{name}: fill stops short of the area on axis {axis}, "
                                          f"leaving a gap at the far edge: {box}",
                    )


if __name__ == "__main__":
    unittest.main()
