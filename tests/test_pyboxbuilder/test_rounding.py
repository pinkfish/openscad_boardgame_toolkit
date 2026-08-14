# SPDX-License-Identifier: Apache-2.0
"""Tests for box edge rounding (FR-043d, FR-044, FR-044a).

Rounding is measured in the app, because the property that matters — "the
fillets removed corner material and nothing else" — is about volume and face
positions, which an offline bounding box on a lazy CSG tree cannot see.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tests"))

from render_app import measure_python, render_available  # noqa: E402

from pyboxbuilder.box.shell import body_rounding  # noqa: E402
from pyboxbuilder.enums import BoxType  # noqa: E402
from pyboxbuilder.project import Project  # noqa: E402
from pyboxbuilder.rounding import (  # noqa: E402
    MIN_ROUNDING_FACETS,
    default_rounding,
    edge_slivers,
    mating_rounding,
    round_edges,
    rounding_facets,
    vertical_and_bottom_edges,
    vertical_and_top_edges,
    vertical_edges,
)


class DefaultRadiusTests(unittest.TestCase):
    def test_half_the_wall(self) -> None:
        self.assertEqual(default_rounding(2.0), 1.0)
        self.assertEqual(default_rounding(3.0), 1.5)

    def test_spec_falls_back_to_the_wall(self) -> None:
        self.assertEqual(body_rounding({"wall_thickness": 3.0}), 1.5)

    def test_explicit_zero_disables_it(self) -> None:
        self.assertEqual(body_rounding({"wall_thickness": 3.0, "rounding": 0}), 0.0)

    def test_explicit_value_wins(self) -> None:
        self.assertEqual(body_rounding({"wall_thickness": 3.0, "rounding": 0.4}), 0.4)

    def test_negative_is_clamped_not_flipped(self) -> None:
        self.assertEqual(body_rounding({"wall_thickness": 2.0, "rounding": -5}), 0.0)


class EdgeSelectorTests(unittest.TestCase):
    """Regression: a box came back with exactly one corner rounded.

    `Anchor.Z` reads as "the vertical edges" and is not: it is an *axis*
    anchor, which the edge language resolves to a single edge. Nothing in the
    geometry complains — you just get one rounded corner out of four.
    """

    def matrix(self, selector):
        from pybosl2._edges_lang import edges

        return edges(selector)

    def count(self, selector) -> int:
        return sum(sum(row) for row in self.matrix(selector))

    def test_vertical_selects_all_four(self) -> None:
        self.assertEqual(self.count(vertical_edges()), 4)
        self.assertEqual(self.matrix(vertical_edges())[2], [1, 1, 1, 1])

    def test_the_axis_anchor_does_not(self) -> None:
        """The mistake this guards against, asserted directly."""
        from pybosl2 import Anchor

        self.assertEqual(self.count(Anchor.Z), 1)

    def test_body_and_lid_selectors_are_eight_edges(self) -> None:
        self.assertEqual(self.count(vertical_and_bottom_edges()), 8)
        self.assertEqual(self.count(vertical_and_top_edges()), 8)

    def test_a_fillet_gets_enough_facets_to_be_a_curve(self) -> None:
        """At the default fs=2 a 1mm fillet would be a single-segment chamfer."""
        self.assertGreaterEqual(rounding_facets()["fn"], MIN_ROUNDING_FACETS)
        self.assertGreaterEqual(MIN_ROUNDING_FACETS, 32)

    def test_an_explicit_higher_precision_wins(self) -> None:
        from pyboxbuilder.precision import use

        with use(fn=128):
            self.assertEqual(rounding_facets()["fn"], 128)


class MatingRoundingTests(unittest.TestCase):
    """FR-044b: a partial lid's grip is rounded smaller, and on both halves."""

    def test_defaults_to_half_the_body_radius(self) -> None:
        self.assertEqual(mating_rounding({"wall_thickness": 2.0}), 0.5)
        self.assertEqual(mating_rounding({"wall_thickness": 3.0}), 0.75)

    def test_is_smaller_than_the_outer_radius(self) -> None:
        spec = {"wall_thickness": 2.0}
        self.assertLess(mating_rounding(spec), body_rounding(spec))

    def test_explicit_inner_rounding_wins(self) -> None:
        self.assertEqual(
            mating_rounding({"wall_thickness": 2.0, "inner_rounding": 0.2}), 0.2
        )

    def test_zero_leaves_the_grip_square(self) -> None:
        self.assertEqual(mating_rounding({"wall_thickness": 2.0, "inner_rounding": 0}), 0.0)

    def test_follows_an_explicit_body_radius(self) -> None:
        self.assertEqual(mating_rounding({"wall_thickness": 2.0, "rounding": 4.0}), 2.0)

    def test_project_and_box_plumbing(self) -> None:
        project = Project("M", game_box_size=(200, 150, 60), inner_rounding=0.3)
        box = project.box(BoxType.CAP, "A", size=(100, 80, 40), position=(0, 0, 0),
                          inner_rounding=0.7)
        self.assertEqual(project.inner_rounding, 0.3)
        self.assertEqual(box.inner_rounding, 0.7)


class RoundingPlumbingTests(unittest.TestCase):
    """The knob reaches the geometry from both the project and the box."""

    def test_project_default_and_per_box_override(self) -> None:
        project = Project("R", game_box_size=(200, 150, 60), rounding=0.5)
        default_box = project.box(BoxType.NO_LID, "A", size=(100, 80, 40), position=(0, 0, 0))
        override = project.box(
            BoxType.NO_LID, "B", size=(80, 60, 40), position=(100, 0, 0), rounding=2.0,
        )
        self.assertIsNone(default_box.rounding)
        self.assertEqual(override.rounding, 2.0)

    def test_slivers_reject_an_oversized_radius(self) -> None:
        """A fillet at least half the smallest dimension has nothing to blend into."""
        from pybosl2 import Anchor

        with self.assertRaises(ValueError):
            edge_slivers([20, 15, 10], 5.0, [Anchor.Z])
        with self.assertRaises(ValueError):
            edge_slivers([20, 15, 10], 0.0, [Anchor.Z])

    def test_round_edges_is_a_no_op_when_disabled_or_absurd(self) -> None:
        """A project-wide default must not blow up on a small piece."""
        from pybosl2 import Anchor, cuboid

        solid = cuboid([20, 15, 10])
        self.assertIs(round_edges(solid, [20, 15, 10], 0.0, [Anchor.Z]), solid)
        self.assertIs(round_edges(solid, [20, 15, 10], 99.0, [Anchor.Z]), solid)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class MeasuredRoundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        body = '''
import os, re, tempfile, zipfile
from openscad import export
from pyboxbuilder.box.shell import build_shell
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.enums import BoxType
from pybosl2 import cuboid

def volume(solid):
    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(solid.shape, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)
    verts = [(float(x), float(y), float(z)) for x, y, z in re.findall(
        r\'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"\', model)]
    total = 0.0
    for a, b, c in re.findall(r\'<triangle v1="(\\d+)" v2="(\\d+)" v3="(\\d+)"\', model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (p[0]*(q[1]*r[2]-r[1]*q[2]) - p[1]*(q[0]*r[2]-r[0]*q[2])
                  + p[2]*(q[0]*r[1]-r[0]*q[1])) / 6.0
    return abs(total)

base = dict(label="T", width=100, length=80, height=40, wall_thickness=2.0,
            floor_thickness=1.6, lid_thickness=2.0, hollow=True)

square = build_shell(dict(base, rounding=0))
rounded = build_shell(dict(base))
lidless = build_shell(dict(base, rim_free=True))
measure("square", square)
measure("rounded", rounded)
measure("lidless", lidless)
report("square_volume", "%.4f" % volume(square))
report("rounded_volume", "%.4f" % volume(rounded))
report("lidless_volume", "%.4f" % volume(lidless))

# Rounding must not put material into a lid: every lidded type stays clear.
# cap/slipover are the partial lids whose grip carries the mating rounding.
for name in ("sliding", "sliding_catch", "card_library", "cap", "inset",
             "slipover", "cap_path", "slipover_path"):
    box_type = BoxType(name)
    impl = BOX_IMPL_REGISTRY[box_type]
    spec = dict(base)
    report(name + "_overlap",
           "%.4f" % volume(impl().build_body(spec) & impl().build_lid(spec)))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_rounding_preserves_the_declared_envelope(self) -> None:
        """SC-027: fillets take corner material only, so packing is unaffected.

        A rounded edge is an inscribed polygon, so it pulls the face it
        blends into inwards by the sagitta — 0.002mm at the 48-facet
        floor. That is 50x below the 0.1mm precision the library
        promises, but it is not zero, and no faceted representation of a
        fillet can make it zero.
        """
        for name in ("square", "rounded", "lidless"):
            with self.subTest(name=name):
                box = self.result.boxes[name]
                for got in box.position:
                    self.assertAlmostEqual(got, 0.0, delta=0.01)
                for got, want in zip(box.size, (100.0, 80.0, 40.0)):
                    self.assertAlmostEqual(got, want, delta=0.01)

    def test_rounding_removes_material(self) -> None:
        square = float(self.result.reports["square_volume"])
        rounded = float(self.result.reports["rounded_volume"])
        self.assertLess(rounded, square, "rounding added material instead of removing it")

    def test_a_lidless_box_also_rounds_its_rim(self) -> None:
        """The rim is exposed with no lid to seal against, so it gets rounded."""
        rounded = float(self.result.reports["rounded_volume"])
        lidless = float(self.result.reports["lidless_volume"])
        self.assertLess(lidless, rounded, "the free rim was left square")

    def test_no_rounded_body_intrudes_into_its_lid(self) -> None:
        """SC-028/FR-044a: the fillet that jams a sliding lid must not exist.

        Includes the partial lids, whose grip is rounded on both halves — the
        two must nest, not collide.
        """
        for name in ("sliding", "sliding_catch", "card_library", "cap", "inset",
                     "slipover", "cap_path", "slipover_path"):
            with self.subTest(box_type=name):
                overlap = float(self.result.reports[name + "_overlap"])
                self.assertLess(overlap, 0.01, f"{name}'s rounded body intersects its lid")


if __name__ == "__main__":
    unittest.main()
