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

# LibFile: tests/test_box_geometry.py
#    What the box system PROMISES, measured on real geometry.
#
#    tests/test_all_boxes_render.py only asserts "the app produced some triangles", which
#    every one of the bugs below passed with flying colours:
#
#      * a labelled sliding lid came out as TWO detached pieces (the plate floated at
#        mid-box height while the label/pattern sat on the bed);
#      * a labelled polygon lid laid its label out half a box away from the lid, growing
#        the part's footprint by ~30%;
#      * polygon lids were flipped for printing to entirely NEGATIVE z (below the bed);
#      * BoxSpec.anchor / orient / spin and BoxSpec.finger_holes were silently ignored by
#        the six box types that overrode make_box().
#
#    So these tests measure the real bounding box (PythonSCAD computes .position/.size by
#    meshing) and assert the invariants that make a box a box. They shell out to the app
#    and skip when it isn't installed, like the other render tests.
#
# FileGroup: Tests

import unittest

from render_app import measure_python, render_python, render_available

_HEADER = "from base_bgtk import *\nfrom box_base import BoxSpec\n"

# name -> (imports, constructor expression). One entry per box type with a separate lid.
# The bounding-box invariants below are checked for every one of them.
LIDDED = {
    "sliding": ("from sliding_box import SlidingBox",
                "SlidingBox(BoxSpec(size=[100, 60, 25], label='t'{extra}))"),
    "sliding_two_layer": ("from sliding_box import SlidingBox, SlidingBoxOptions",
                          "SlidingBox(BoxSpec(size=[100, 60, 25], label='t', "
                          "type_options=SlidingBoxOptions(two_layer=True){extra}))"),
    "cap": ("from cap_box import CapBox",
            "CapBox(BoxSpec(size=[90, 60, 30], label='t'{extra}))"),
    "slipover": ("from slipover_box import SlipoverBox",
                 "SlipoverBox(BoxSpec(size=[90, 60, 25], label='t'{extra}))"),
    "sliding_catch": ("from sliding_catch_box import SlidingCatchBox",
                      "SlidingCatchBox(BoxSpec(size=[100, 50, 20], label='t'{extra}))"),
    "magnetic": ("from magnetic_box import MagneticBox, MagneticBoxOptions",
                 "MagneticBox(BoxSpec(size=[100, 50, 20], label='t', "
                 "type_options=MagneticBoxOptions(magnet_diameter=6, magnet_thickness=2){extra}))"),
    "inset": ("from inset_box import InsetBox",
              "InsetBox(BoxSpec(size=[100, 50, 20], label='t'{extra}))"),
    "cap_path": ("from cap_box_polygon import CapPathBox",
                 "CapPathBox.regular_polygon(BoxSpec(size=[90, 90, 25], label='t'{extra}), sides=6)"),
    "slipover_path": ("from slipover_path_box import SlipoverPathBox",
                      "SlipoverPathBox.regular_polygon(BoxSpec(size=[90, 90, 15], label='t'{extra}), sides=6)"),
    # NOT covered: filament_hinge and card_library. Their lids contain frep/SDF knuckle
    # hinges, and measuring a solid meshes it -- which crashes the app when the same
    # handle is then used again. They stay on the render-only test.
}

# The lid decoration is a label plus the default tiled pattern: the combination that
# exercises every overlay slot (mesh, label) through build_lid.
_DECORATED = ", lid='T'"


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class LidGeometryTests(unittest.TestCase):
    """A lid must be ONE part, decoration must live inside it, and it must print."""

    def _measure_lids(self, name):
        imports, ctor = LIDDED[name]
        body = (
            f"{_HEADER}{imports}\n"
            f"plain = {ctor.format(extra='')}.make_lid()\n"
            f"measure('plain', plain)\n"
            f"decorated = {ctor.format(extra=_DECORATED)}.make_lid()\n"
            f"measure('decorated', decorated)\n"
            "import pybosl2.shapes3d as _s3\n"
            "_s3.cuboid([1, 1, 1]).show()\n"
        )
        r = measure_python(body)
        self.assertTrue(r.ok, f"{name}: {r.error}\n{r.stderr[-2000:]}")
        self.assertIn("plain", r.boxes, f"{name}: plain lid not measured")
        self.assertIn("decorated", r.boxes, f"{name}: decorated lid not measured")
        return r.boxes["plain"], r.boxes["decorated"]

    def test_decoration_stays_inside_the_lid(self):
        """A label + pattern must not change the lid's bounding box.

        Overlays are decoration cut INTO the lid's flat face; if adding them moves or
        grows the part, they are floating somewhere they don't belong. This is the
        assertion the detached sliding lid and the off-by-half-a-box polygon label both
        fail, and the one `facets > 0` could never make."""
        for name in LIDDED:
            with self.subTest(box=name):
                plain, decorated = self._measure_lids(name)
                for axis, (a, b) in enumerate(zip(plain.size, decorated.size)):
                    self.assertAlmostEqual(
                        a, b, delta=0.6,
                        msg=f"{name}: decoration changed the lid size on axis {axis}: "
                            f"plain {plain}, decorated {decorated}",
                    )
                for axis, (a, b) in enumerate(zip(plain.position, decorated.position)):
                    self.assertAlmostEqual(
                        a, b, delta=0.6,
                        msg=f"{name}: decoration moved the lid on axis {axis}: "
                            f"plain {plain}, decorated {decorated}",
                    )

    def test_lid_sits_on_the_print_bed(self):
        """Every lid is a separate print: it must start at z >= 0, not below the bed."""
        for name in LIDDED:
            with self.subTest(box=name):
                plain, decorated = self._measure_lids(name)
                self.assertGreaterEqual(plain.z, -0.01, f"{name}: plain lid is below z=0: {plain}")
                self.assertGreaterEqual(decorated.z, -0.01, f"{name}: decorated lid is below z=0: {decorated}")

    def test_lid_is_no_taller_than_the_box(self):
        """A lid that measures taller than the box it closes is two pieces stacked in the
        air (which is exactly how the sliding-lid bug showed up: a 2mm lid measuring 13.5mm)."""
        heights = {"sliding": 25, "sliding_two_layer": 25, "cap": 30, "slipover": 25,
                   "sliding_catch": 20, "magnetic": 20, "inset": 20, "cap_path": 25,
                   "slipover_path": 15}
        for name in LIDDED:
            with self.subTest(box=name):
                _, decorated = self._measure_lids(name)
                self.assertLessEqual(
                    decorated.height, heights[name] + 0.01,
                    f"{name}: lid is taller than the {heights[name]}mm box: {decorated}",
                )


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class PipelineAppliesToEveryTypeTests(unittest.TestCase):
    """BoxSpec fields must mean the same thing whichever type builds the geometry.

    The six types that used to override make_box() (hinge, filament hinge, card library,
    path, cap path, slipover path) silently dropped positioning and finger holes. They
    now go through the one pipeline, so these assertions cover them explicitly."""

    # Types that used to bypass the shared pipeline entirely, plus one that never did.
    FACADES = {
        "hinge": ("from hinge_box import HingeBox",
                  "HingeBox(BoxSpec(size=[100, 50, 20], label='t'{extra}))"),
        "path": ("from no_lid import PathBox",
                 "PathBox.regular_polygon(BoxSpec(size=[100, 100, 24], label='t', hollow=True{extra}), sides=6)"),
        "cap_path": ("from cap_box_polygon import CapPathBox",
                     "CapPathBox.regular_polygon(BoxSpec(size=[90, 90, 25], label='t'{extra}), sides=6)"),
        "sliding": ("from sliding_box import SlidingBox",
                    "SlidingBox(BoxSpec(size=[100, 60, 25], label='t'{extra}))"),
    }

    def _measure_box(self, name, extra, tag):
        imports, ctor = self.FACADES[name]
        body = (
            f"{_HEADER}{imports}\n"
            f"box = {ctor.format(extra=extra)}\n"
            f"measure('{tag}', box.make_box())\n"
            "import pybosl2.shapes3d as _s3\n"
            "_s3.cuboid([1, 1, 1]).show()\n"
        )
        r = measure_python(body)
        self.assertTrue(r.ok, f"{name}: {r.error}\n{r.stderr[-2000:]}")
        return r.boxes[tag]

    def test_spin_rotates_every_box_type(self):
        """``BoxSpec(spin=90)`` must turn the box a quarter turn -- the width and length of
        its bounding box swap. Types that dropped positioning ignored this completely."""
        for name in self.FACADES:
            with self.subTest(box=name):
                plain = self._measure_box(name, "", "plain")
                spun = self._measure_box(name, ", spin=90", "spun")
                self.assertAlmostEqual(
                    plain.width, spun.length, delta=0.5,
                    msg=f"{name}: spin=90 did not swap width/length: {plain} vs {spun}",
                )
                self.assertAlmostEqual(
                    plain.length, spun.width, delta=0.5,
                    msg=f"{name}: spin=90 did not swap width/length: {plain} vs {spun}",
                )

    def test_spin_turns_the_lid_with_its_box(self):
        """One spec, two parts, ONE frame.

        ``BoxSpec`` exists so the box and its lid agree, but positioning used to be
        applied only in ``make_box``: ``spin=90`` turned the box a quarter turn and left
        the lid where it was, so the pair no longer fitted together or laid out
        consistently. Both parts go through ``_apply_positioning`` now, so the lid's
        bounding box must swap width/length exactly as the box's does."""
        lidded = {k: v for k, v in self.FACADES.items() if k in ("sliding", "cap_path")}
        for name in lidded:
            with self.subTest(box=name):
                imports, ctor = self.FACADES[name]

                def measure_lid(extra, tag):
                    body = (
                        f"{_HEADER}{imports}\n"
                        f"box = {ctor.format(extra=extra)}\n"
                        f"measure('{tag}', box.make_lid())\n"
                        "import pybosl2.shapes3d as _s3\n"
                        "_s3.cuboid([1, 1, 1]).show()\n"
                    )
                    r = measure_python(body)
                    self.assertTrue(r.ok, f"{name}: {r.error}\n{r.stderr[-2000:]}")
                    return r.boxes[tag]

                plain = measure_lid("", "plain_lid")
                spun = measure_lid(", spin=90", "spun_lid")
                self.assertAlmostEqual(
                    plain.width, spun.length, delta=0.6,
                    msg=f"{name}: spin=90 did not turn the LID: {plain} vs {spun}",
                )
                self.assertAlmostEqual(
                    plain.length, spun.width, delta=0.6,
                    msg=f"{name}: spin=90 did not turn the LID: {plain} vs {spun}",
                )

    def test_lid_is_concentric_with_its_box(self):
        """The lid must sit over the box, not beside it: same centre in x/y.

        The other half of sharing a frame -- ``anchor`` moved the box and left the lid at
        the origin, so overlaying the two parts showed them offset by half a box."""
        for name in ("sliding", "cap_path"):
            with self.subTest(box=name):
                imports, ctor = self.FACADES[name]
                body = (
                    f"{_HEADER}{imports}\n"
                    f"box = {ctor.format(extra='')}\n"
                    "measure('box', box.make_box())\n"
                    "measure('lid', box.make_lid())\n"
                    "import pybosl2.shapes3d as _s3\n"
                    "_s3.cuboid([1, 1, 1]).show()\n"
                )
                r = measure_python(body)
                self.assertTrue(r.ok, f"{name}: {r.error}\n{r.stderr[-2000:]}")
                b, l = r.boxes["box"], r.boxes["lid"]
                self.assertAlmostEqual(
                    b.x + b.width / 2, l.x + l.width / 2, delta=1.0,
                    msg=f"{name}: lid is not centred over the box in x: box={b} lid={l}",
                )
                self.assertAlmostEqual(
                    b.y + b.length / 2, l.y + l.length / 2, delta=1.0,
                    msg=f"{name}: lid is not centred over the box in y: box={b} lid={l}",
                )

    def test_finger_holes_cut_every_box_type(self):
        """``BoxSpec(finger_holes=...)`` must actually remove material. The facade types
        accepted the argument and threw it away."""
        cases = {
            "hinge": ("from hinge_box import HingeBox",
                      "HingeBox(BoxSpec(size=[100, 50, 20], label='t'{extra}))"),
            "sliding": ("from sliding_box import SlidingBox",
                        "SlidingBox(BoxSpec(size=[100, 60, 25], label='t'{extra}))"),
        }
        hole = (", finger_holes=[FingerHole(location=FingerHoleLocation.FRONT)]")
        for name, (imports, ctor) in cases.items():
            with self.subTest(box=name):
                counts = {}
                for tag, extra in (("plain", ""), ("holed", hole)):
                    body = (
                        f"{_HEADER}from box_base import FingerHole, FingerHoleLocation\n{imports}\n"
                        f"{ctor.format(extra=extra)}.make_box().show()\n"
                    )
                    r = render_python(body)
                    self.assertTrue(r.ok, f"{name}/{tag}: {r.error}\n{r.stderr[-2000:]}")
                    counts[tag] = r.facets
                self.assertNotEqual(
                    counts["plain"], counts["holed"],
                    f"{name}: finger_holes did not change the geometry ({counts})",
                )


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class InteriorFrameTests(unittest.TestCase):
    """The interior frame is one object, so what a box REPORTS as its interior has to be
    where content actually lands and what content is clipped to."""

    def test_interior_matches_where_content_lands(self):
        """A negative content the exact size of the reported interior must carve a cavity
        that lands at the interior origin -- the three-way agreement between
        ``inner_*``, ``_placed_content`` and ``interior_mask`` that used to be three
        separately-overridable methods per box type."""
        cases = {
            "sliding": ("from sliding_box import SlidingBox",
                        "SlidingBox(BoxSpec(size=[100, 60, 25], label='t'))"),
            "cap": ("from cap_box import CapBox", "CapBox(BoxSpec(size=[90, 60, 30], label='t'))"),
            "slipover": ("from slipover_box import SlipoverBox",
                         "SlipoverBox(BoxSpec(size=[90, 60, 25], label='t'))"),
            "sliding_catch": ("from sliding_catch_box import SlidingCatchBox",
                              "SlidingCatchBox(BoxSpec(size=[100, 50, 20], label='t'))"),
            "no_lid": ("from no_lid import NoLidBox", "NoLidBox(BoxSpec(size=[80, 50, 20], label='t'))"),
        }
        for name, (imports, ctor) in cases.items():
            with self.subTest(box=name):
                body = (
                    f"{_HEADER}{imports}\n"
                    "import pybosl2.shapes3d as _s3\n"
                    f"box = {ctor}\n"
                    "i = box.interior()\n"
                    "report('origin', '%.6g,%.6g,%.6g' % tuple(i.origin))\n"
                    "report('size', '%.6g,%.6g,%.6g' % tuple(i.size))\n"
                    "measure('cavity', box.interior_mask())\n"
                    "_s3.cuboid([1, 1, 1]).show()\n"
                )
                r = measure_python(body)
                self.assertTrue(r.ok, f"{name}: {r.error}\n{r.stderr[-2000:]}")
                origin = [float(v) for v in r.reports["origin"].split(",")]
                size = [float(v) for v in r.reports["size"].split(",")]
                cavity = r.boxes["cavity"]
                self.assertTrue(all(s > 0 for s in size), f"{name}: non-positive interior {size}")
                # The clip volume starts exactly at the interior origin...
                for axis in range(3):
                    self.assertAlmostEqual(
                        origin[axis], cavity.position[axis], delta=0.01,
                        msg=f"{name}: interior origin {origin} != clip volume {cavity}",
                    )
                # ...and is at least as big as the interior it describes (a box type may
                # deliberately clip taller -- sliding_catch does -- but never smaller).
                for axis in range(3):
                    self.assertGreaterEqual(
                        cavity.size[axis] + 0.01, size[axis],
                        f"{name}: clip volume {cavity} is smaller than the interior {size}",
                    )

    def test_contents_are_carved_where_the_interior_says(self):
        """Filling the reported interior with a negative content must hollow the box:
        the result has to be lighter (fewer/other facets) than the solid form, and the
        box's outer size must not change."""
        body = (
            f"{_HEADER}from no_lid import NoLidBox\n"
            "import pybosl2.shapes3d as _s3\n"
            "solid = NoLidBox(BoxSpec(size=[80, 50, 20], label='t'))\n"
            "measure('solid', solid.make_box())\n"
            "carved = NoLidBox(BoxSpec(size=[80, 50, 20], label='t', contents=lambda i: ["
            "    InnerObject(_s3.cuboid([i.width, i.length, i.height], anchor=BOTTOM + FRONT + LEFT))]))\n"
            "measure('carved', carved.make_box())\n"
            "_s3.cuboid([1, 1, 1]).show()\n"
        )
        r = measure_python(body)
        self.assertTrue(r.ok, f"{r.error}\n{r.stderr[-2000:]}")
        solid, carved = r.boxes["solid"], r.boxes["carved"]
        for axis in range(3):
            self.assertAlmostEqual(
                solid.size[axis], carved.size[axis], delta=0.01,
                msg=f"carving the interior changed the outer size: {solid} vs {carved}",
            )


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class TypeOptionsTests(unittest.TestCase):
    """``BoxSpec.type_options`` is type-checked at construction, so a spec built for one
    box type cannot be quietly built as another."""

    def _run(self, snippet):
        body = (
            f"{_HEADER}import pybosl2.shapes3d as _s3\n"
            "def check(name, fn):\n"
            "    try:\n"
            "        fn()\n"
            "        report(name, 'no-error')\n"
            "    except TypeError as exc:\n"
            "        report(name, 'TypeError')\n"
            "    except Exception as exc:\n"
            "        report(name, type(exc).__name__)\n"
            f"{snippet}"
            "_s3.cuboid([1, 1, 1]).show()\n"
        )
        r = measure_python(body)
        self.assertTrue(r.ok, f"{r.error}\n{r.stderr[-2000:]}")
        return r.reports

    def test_wrong_options_type_is_rejected(self):
        reports = self._run(
            "from cap_box import CapBox, CapBoxOptions\n"
            "from sliding_box import SlidingBox, SlidingBoxOptions\n"
            "check('sliding_gets_cap', lambda: SlidingBox(BoxSpec(size=[50, 50, 20], label='t',"
            " type_options=CapBoxOptions(cap_height=3))))\n"
            "check('cap_gets_sliding', lambda: CapBox(BoxSpec(size=[50, 50, 20], label='t',"
            " type_options=SlidingBoxOptions(two_layer=True))))\n"
            "check('cap_gets_cap', lambda: CapBox(BoxSpec(size=[50, 50, 20], label='t',"
            " type_options=CapBoxOptions(cap_height=3))))\n"
        )
        self.assertEqual(reports["sliding_gets_cap"], "TypeError",
                         "a cap box's options must not be accepted by a sliding box")
        self.assertEqual(reports["cap_gets_sliding"], "TypeError",
                         "a sliding box's options must not be silently ignored by a cap box")
        self.assertEqual(reports["cap_gets_cap"], "no-error")

    def test_options_free_type_rejects_options(self):
        reports = self._run(
            "from no_lid import NoLidBox\n"
            "from cap_box import CapBoxOptions\n"
            "check('no_lid_gets_options', lambda: NoLidBox(BoxSpec(size=[50, 50, 20], label='t',"
            " type_options=CapBoxOptions())))\n"
        )
        self.assertEqual(reports["no_lid_gets_options"], "TypeError")

    def test_required_options_are_demanded_by_name(self):
        """A path box needs an outline; asking for one without options must say so."""
        reports = self._run(
            "from no_lid import PathBox\n"
            "check('path_without_options', lambda: PathBox(BoxSpec(size=[50, 50, 20], label='t')))\n"
        )
        self.assertEqual(reports["path_without_options"], "TypeError")

    def test_types_without_a_lid_say_so(self):
        """A lidless type has no ``make_lid`` AT ALL -- it is not a :class:`LiddedBox`.

        This used to be ``has_lid = False`` plus a ``NotImplementedError`` raised from a
        ``make_lid`` that every box type carried: a compile-time fact reported at build
        time, one box at a time. The absence of the method is the assertion now, which is
        also what lets BoxKit reject a lidless type up front."""
        reports = self._run(
            "from no_lid import NoLidBox\n"
            "from hinge_box import HingeBox\n"
            "check('no_lid', lambda: NoLidBox(BoxSpec(size=[50, 50, 20], label='t')).make_lid())\n"
            "check('hinge', lambda: HingeBox(BoxSpec(size=[50, 50, 20], label='t')).make_lid())\n"
        )
        self.assertEqual(reports["no_lid"], "AttributeError")
        self.assertEqual(reports["hinge"], "AttributeError")

    def test_lidless_types_are_not_lidded_boxes(self):
        """The static half of the same contract: the class hierarchy says it, so a caller
        (and BoxKit) can ask without building anything."""
        reports = self._run(
            "from box_base import LiddedBox\n"
            "from no_lid import NoLidBox, PathBox\n"
            "from hinge_box import HingeBox\n"
            "from sliding_box import SlidingBox\n"
            "from cap_box import CapBox\n"
            "for _n, _c in (('no_lid', NoLidBox), ('path', PathBox), ('hinge', HingeBox),\n"
            "               ('sliding', SlidingBox), ('cap', CapBox)):\n"
            "    report(_n, 'lidded' if issubclass(_c, LiddedBox) else 'lidless')\n"
        )
        self.assertEqual(
            {"no_lid": "lidless", "path": "lidless", "hinge": "lidless",
             "sliding": "lidded", "cap": "lidded"},
            {k: reports[k] for k in ("no_lid", "path", "hinge", "sliding", "cap")},
        )

    def test_box_kit_rejects_lid_settings_for_a_lidless_type(self):
        """BoxKit's one-word type switch fails at the KIT, not at each make_lid() call."""
        reports = self._run(
            "from box_base import BoxKit\n"
            "from no_lid import NoLidBox\n"
            "check('kit_with_lid', lambda: BoxKit(NoLidBox, lid='x'))\n"
        )
        self.assertEqual(reports["kit_with_lid"], "TypeError")


if __name__ == "__main__":
    unittest.main()
