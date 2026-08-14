# SPDX-License-Identifier: Apache-2.0
"""Tests for finger-scoop smoothing, ported from the original toolkit (T248).

The three roundings under test — the mouth flare into the rim, the fillet where
the cut emerges on each face, and the floor blend — are all *geometry*, so the
assertions that matter are measured in the real app. Offline `bounds()` on a
lazy CSG tree is an estimate and cannot see a boolean's true extent.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tests"))

from render_app import measure_python, render_available  # noqa: E402

from pyboxbuilder.compartments.finger_hole import (  # noqa: E402
    DEFAULT_MOUTH_ROUNDING_MM,
    MIN_WALL_SCOOP_DEPTH_MM,
    build_floor_scoop,
    build_scoop,
    build_wall_scoop,
    floor_bore_profile,
    scoop_profile,
)
from pyboxbuilder.enums import ScoopSide  # noqa: E402
from pyboxbuilder.sweep import offset_sweep  # noqa: E402


class ScoopProfileTests(unittest.TestCase):
    """The 2-D profile: both branches build, and the inputs are validated."""

    def test_tall_profile_builds(self) -> None:
        self.assertIsNotNone(scoop_profile(10, 30, 3))

    def test_a_shallow_profile_still_builds(self) -> None:
        """No special case: the radii scale down to whatever height there is."""
        self.assertIsNotNone(scoop_profile(10, 6, 3))

    def test_zero_rounding_gives_a_plain_slot(self) -> None:
        self.assertIsNotNone(scoop_profile(10, 30, 0))

    def test_bad_inputs_rejected(self) -> None:
        for args in ((0, 30, 3), (-1, 30, 3), (10, 0, 3), (10, 30, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                scoop_profile(*args)


class OffsetSweepTests(unittest.TestCase):
    def test_rim_must_fit_in_the_height(self) -> None:
        profile = scoop_profile(5, 10, 0)
        with self.assertRaises(ValueError):
            offset_sweep(profile, height=1.0, rounding_bottom=-2.0, rounding_top=-2.0)

    def test_height_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            offset_sweep(scoop_profile(5, 10, 0), height=0.0)


class ScoopSelectionTests(unittest.TestCase):
    def test_deep_compartment_gets_a_wall_notch(self) -> None:
        deep = build_scoop(40, 30, MIN_WALL_SCOOP_DEPTH_MM + 1, ScoopSide.FRONT)
        direct = build_wall_scoop(40, 30, MIN_WALL_SCOOP_DEPTH_MM + 1, ScoopSide.FRONT)
        self.assertEqual(repr(deep), repr(direct))

    def test_shallow_compartment_gets_the_floor_blend(self) -> None:
        shallow = build_scoop(40, 30, 4, ScoopSide.FRONT)
        direct = build_floor_scoop(40, 30, ScoopSide.FRONT, comp_depth=4, radius=12.0)
        self.assertEqual(repr(shallow), repr(direct))

    def test_bad_dimensions_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_wall_scoop(40, 30, 0, ScoopSide.FRONT)
        with self.assertRaises(ValueError):
            build_wall_scoop(40, 30, 20, ScoopSide.FRONT, wall_thickness=0)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class MeasuredScoopTests(unittest.TestCase):
    """Measured in the app: the promises the docstrings make must hold."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.compartments.finger_hole import build_wall_scoop, build_floor_scoop
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

# Compartment 40 x 30 x 20. For a FRONT scoop the wall's inner face is y=0 and
# its outer face is y=-wall_thickness.
measure("wt2", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=2))
measure("wt3", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=3))
measure("wt5", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=5))
measure("square", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                   wall_thickness=2, rounding_edge=0, rounding_radius=0))
measure("no_mouth", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                      wall_thickness=2, rounding_radius=0))
measure("left", build_wall_scoop(40, 30, 20, ScoopSide.LEFT, radius=10, wall_thickness=2))
measure("right", build_wall_scoop(40, 30, 20, ScoopSide.RIGHT, radius=10, wall_thickness=2))
measure("back", build_wall_scoop(40, 30, 20, ScoopSide.BACK, radius=10, wall_thickness=2))
measure("breaching", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                       wall_thickness=2, breach_floor=True))
measure("thick_floor", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                         wall_thickness=2, floor_thickness=4))
measure("floor", build_floor_scoop(40, 30, ScoopSide.FRONT, radius=8, comp_depth=5,
                                    wall_thickness=2))

# The scoop must actually open the wall of a real box, not just touch it.
shell = cuboid([44, 34, 22], anchor=[-1, -1, -1])
well = cuboid([40, 30, 20], anchor=[-1, -1, -1]).translate([2, 2, 2])
scoop = build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=2)
measure("carved", shell - well - scoop.translate([2, 2, 2]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}\n{cls.result.stderr[-2000:]}")

    def span(self, name: str, axis: int) -> tuple[float, float]:
        box = self.result.boxes[name]
        return box.position[axis], box.position[axis] + box.size[axis]

    def test_dips_only_a_controlled_amount_into_the_floor(self) -> None:
        """The cut may not sit *on* the floor plane, nor sink far into it.

        Clipping flush with the floor leaves a coincident face, which renders as
        speckle; the original's answer is a small deliberate overshoot. So the
        bottom must be below 0 but no deeper than the dip, which defaults to
        0.2mm when no floor thickness is passed.
        """
        for name in ("wt2", "wt3", "wt5", "floor"):
            with self.subTest(name=name):
                low, _ = self.span(name, 2)
                self.assertLess(low, 0.0, "bottom face is coplanar with the floor")
                self.assertGreaterEqual(low, -0.25, "dipped further than the default 0.2mm")

    def test_a_scoop_with_no_fillet_has_nothing_to_dip(self) -> None:
        """The dip is a limit on the flare, not an offset applied regardless.

        With both roundings off there is no flare below the bore, so the cut
        bottoms out exactly at the floor and the clip never engages.
        """
        low, _ = self.span("square", 2)
        self.assertAlmostEqual(low, 0.0, places=3)

    def test_floor_thickness_raises_the_dip_limit(self) -> None:
        """A known floor permits a deeper dip — up to half of it, capped at 1mm.

        It is a ceiling, not a target: here the flare only reaches 0.95mm, so
        that is where the cut stops. The default 0.2mm limit would have clipped
        it, which is what makes the two cases differ.
        """
        limited, _ = self.span("wt2", 2)
        allowed, _ = self.span("thick_floor", 2)
        unclipped, _ = self.span("breaching", 2)
        self.assertAlmostEqual(limited, -0.2, places=2)
        self.assertLess(allowed, -0.9)
        self.assertAlmostEqual(allowed, unclipped, places=3)

    def test_breach_floor_opt_in_dips_much_further(self) -> None:
        """The opt-out removes the clip entirely, so the flare runs free."""
        low, _ = self.span("breaching", 2)
        self.assertLess(low, -0.5)

    def test_overshoots_the_rim_so_no_skin_is_left(self) -> None:
        _, high = self.span("wt2", 2)
        self.assertGreater(high, 20.0)

    def test_pierces_the_wall_at_any_thickness(self) -> None:
        """The sweep spans exactly the wall: 0.015 clear of each face, no more.

        Overshooting further would put the face fillets outside the box, which
        is the bug this test exists to catch.
        """
        for name, wall in (("wt2", 2.0), ("wt3", 3.0), ("wt5", 5.0)):
            with self.subTest(wall=wall):
                low, high = self.span(name, 1)
                self.assertAlmostEqual(low, -wall - 0.015, places=2)
                self.assertAlmostEqual(high, 0.015, places=2)

    def test_face_fillet_and_mouth_flare_widen_the_cut(self) -> None:
        """A plain slot is 2*radius wide; each rounding adds to that.

        Widths carry a faceting tolerance: both the r1 arc and the face
        fillet's rim are sampled polygons, so each falls a little short of its
        exact radius. 0.1mm is well inside the 0.1mm dimensional precision the
        library promises and an order below what a nozzle resolves.
        """
        square_low, square_high = self.span("square", 0)
        self.assertAlmostEqual(square_high - square_low, 20.0, delta=0.1)

        # r1 off, face fillet on (wall/2 = 1mm each side).
        no_mouth_low, no_mouth_high = self.span("no_mouth", 0)
        self.assertAlmostEqual(no_mouth_high - no_mouth_low, 22.0, delta=0.1)

        # Both on: + 3mm of r1 roll each side.
        full_low, full_high = self.span("wt2", 0)
        self.assertAlmostEqual(full_high - full_low, 28.0, delta=0.1)

    def test_carved_box_keeps_its_envelope(self) -> None:
        """Cutting the scoop must not enlarge the box or open its base."""
        box = self.result.boxes["carved"]
        self.assertAlmostEqual(box.position[2], 0.0, places=3)
        self.assertAlmostEqual(box.size[0], 44.0, places=2)
        self.assertAlmostEqual(box.size[1], 34.0, places=2)
        self.assertAlmostEqual(box.size[2], 22.0, places=2)

    def test_floor_scoop_blends_into_the_floor(self) -> None:
        """The floor blend reaches into the compartment past the wall face."""
        _, high = self.span("floor", 1)
        self.assertGreater(high, 0.5)

    def test_each_side_cuts_outward_through_its_own_wall(self) -> None:
        """Every side's cut must lie *outside* the compartment footprint.

        A scoop pointing the wrong way sits inside the well and shaves the
        wall's inner face by the sweep's 0.015 of fudge, piercing nothing. The
        bounding box is the same size either way, so the direction is what has
        to be asserted — LEFT/RIGHT were inverted until this test.
        """
        cases = {
            "left": (0, -2.015, 0.015),      # wall at x <= 0
            "right": (0, 39.985, 42.015),    # wall at x >= 40 (comp_width)
            "back": (1, 29.985, 32.015),     # wall at y >= 30 (comp_length)
            "wt2": (1, -2.015, 0.015),       # FRONT: wall at y <= 0
        }
        for name, (axis, low, high) in cases.items():
            with self.subTest(side=name):
                got_low, got_high = self.span(name, axis)
                self.assertAlmostEqual(got_low, low, places=2)
                self.assertAlmostEqual(got_high, high, places=2)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class ExteriorFingerHoleTests(unittest.TestCase):
    """A hole on the outside of a box goes through the same scoop builder."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.box.shell import build_shell
from pybosl2 import cuboid

base = dict(label="Tray", width=100, length=80, height=40,
            wall_thickness=2.0, floor_thickness=1.6, lid_thickness=0.0, hollow=True)

class Hole:
    """Stands in for FingerHoleBuilder — build_shell only reads attributes."""
    def __init__(self, side, radius=14.0, depth=6.0, offset=0.0):
        self.side, self.radius, self.depth, self.offset = side, radius, depth, offset
        self.rounding_radius = self.rounding_edge = None

plain = build_shell(dict(base))
measure("plain", plain)
measure("holed", build_shell(dict(base, finger_holes=(Hole(ScoopSide.LEFT),
                                                      Hole(ScoopSide.RIGHT)))))
# What each hole actually removed from the wall.
measure("removed_left",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.LEFT),))))
measure("removed_front",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.FRONT),))))
measure("removed_deep",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.FRONT, depth=100),))))

# The same capped cut on its own, where no mesh-difference sliver can appear.
from pyboxbuilder.compartments.finger_hole import build_wall_scoop
_reach = 40 - 1.6
measure("deep_scoop_solid",
        build_wall_scoop(96, 76, _reach, ScoopSide.FRONT, radius=14.0,
                         wall_thickness=2.0, rounding_radius=3.0)
        .translate([2, 2, 40 - _reach]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def box(self, name: str):
        return self.result.boxes[name]

    def test_a_hole_does_not_change_the_box_envelope(self) -> None:
        plain, holed = self.box("plain"), self.box("holed")
        self.assertEqual([round(v, 3) for v in plain.size], [round(v, 3) for v in holed.size])
        self.assertEqual([round(v, 3) for v in plain.position], [round(v, 3) for v in holed.position])

    def test_a_hole_removes_the_full_wall_thickness(self) -> None:
        """The point of the hole: a finger must pass through, not scuff the wall."""
        left = self.box("removed_left")
        self.assertAlmostEqual(left.position[0], 0.0, places=2)
        self.assertAlmostEqual(left.position[0] + left.size[0], 2.0, places=2)

        front = self.box("removed_front")
        self.assertAlmostEqual(front.position[1], 0.0, places=2)
        self.assertAlmostEqual(front.position[1] + front.size[1], 2.0, places=2)

    def test_a_hole_hangs_from_the_rim(self) -> None:
        """Reaches the rim at the top, and `depth` down from it — plus the dip."""
        removed = self.box("removed_front")
        self.assertAlmostEqual(removed.position[2] + removed.size[2], 40.0, places=2)
        self.assertAlmostEqual(removed.position[2], 40.0 - 6.0 - 0.2, places=2)

    def test_depth_is_capped_at_the_interior_so_the_base_survives(self) -> None:
        """A hole asked to reach 100mm into a 40mm box stops inside the floor.

        Capped at the interior depth, the cut reaches the well floor and dips
        the default 0.2mm past it, so floor material is left underneath and the
        base is never opened.

        The exact depth is asserted on the scoop solid rather than here: this
        measures the *difference* of two independently meshed bodies, which can
        disagree by a facet in the bottom fillet and report a near-zero-volume
        sliver below the cut.
        """
        removed = self.box("removed_deep")
        floor_left = removed.position[2]
        self.assertGreater(floor_left, 0.0, "the cut opened the box's base")
        self.assertGreater(floor_left, 0.5, "too little floor left under the cut")

    def test_the_capped_cut_itself_stops_inside_the_floor(self) -> None:
        """The scoop solid, measured directly: floor at 1.6, dipping 0.2 past."""
        scoop = self.box("deep_scoop_solid")
        self.assertAlmostEqual(scoop.position[2], 1.6 - 0.2, places=2)


class FingerHoleBuilderTests(unittest.TestCase):
    """The builder API for exterior holes (pure Python)."""

    def project_box(self):
        from pyboxbuilder import BoxType, Project

        project = Project("Holes", game_box_size=(200, 150, 60))
        return project.box(BoxType.NO_LID, "Tray", size=(100, 80, 40))

    def test_finger_hole_registers_on_the_box(self) -> None:
        box = self.project_box()
        hole = box.finger_hole(ScoopSide.LEFT, radius=12.0, depth=8.0)
        self.assertEqual(box.finger_holes, (hole,))
        self.assertIs(hole.side, ScoopSide.LEFT)
        self.assertEqual(hole.radius, 12.0)

    def test_several_holes_accumulate(self) -> None:
        box = self.project_box()
        box.finger_hole(ScoopSide.LEFT)
        box.finger_hole(ScoopSide.RIGHT)
        self.assertEqual([h.side for h in box.finger_holes], [ScoopSide.LEFT, ScoopSide.RIGHT])

    def test_bare_string_side_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.project_box().finger_hole("left")

    def test_non_positive_dimensions_rejected(self) -> None:
        box = self.project_box()
        with self.assertRaises(ValueError):
            box.finger_hole(ScoopSide.LEFT, radius=0)
        with self.assertRaises(ValueError):
            box.finger_hole(ScoopSide.LEFT, depth=-1)


if __name__ == "__main__":
    unittest.main()


class TwoRadiusProfileTests(unittest.TestCase):
    """FR-043a: an edge scoop is r1 at the rim, r2 into a flat bottom."""

    def outline(self, profile) -> str:
        return repr(profile)

    def test_both_radii_change_the_profile(self) -> None:
        square = scoop_profile(10, 30, 0, 0)
        top_only = scoop_profile(10, 30, 6, 0)
        both = scoop_profile(10, 30, 6, 5)
        self.assertNotEqual(self.outline(square), self.outline(top_only))
        self.assertNotEqual(self.outline(top_only), self.outline(both))

    def test_bottom_radius_defaults_to_half_the_throat(self) -> None:
        self.assertEqual(
            self.outline(scoop_profile(10, 30, 6)),
            self.outline(scoop_profile(10, 30, 6, 5)),
        )

    def test_radii_are_scaled_down_to_fit_a_shallow_scoop(self) -> None:
        """r1 + r2 cannot exceed the height; a shallow scoop shrinks both."""
        self.assertIsNotNone(scoop_profile(10, 4, 8, 8))

    def test_bottom_radius_cannot_exceed_the_throat(self) -> None:
        self.assertEqual(
            self.outline(scoop_profile(10, 30, 6, 50)),
            self.outline(scoop_profile(10, 30, 6, 10)),
        )

    def test_bad_inputs_rejected(self) -> None:
        for kwargs in ({"top_rounding": -1}, {"bottom_rounding": -1}):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                scoop_profile(10, 30, **kwargs)

    def test_the_floor_bore_is_a_different_shape(self) -> None:
        """An edge scoop is a channel; a floor hole is a bore. Not the same."""
        edge = scoop_profile(10, 20, 3)
        floor = floor_bore_profile(10, 20, 3)
        self.assertNotEqual(self.outline(edge), self.outline(floor))

    def test_the_floor_bore_validates_its_inputs(self) -> None:
        for args in ((0, 20, 3), (10, 0, 3), (10, 20, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                floor_bore_profile(*args)


if __name__ == "__main__":
    unittest.main()


class FlatBottomTests(unittest.TestCase):
    """The base of an edge scoop keeps a flat run for a piece to sit on."""

    def test_r2_is_capped_so_the_flat_survives(self) -> None:
        from pyboxbuilder.compartments.finger_hole import MIN_FLAT_BOTTOM_RATIO

        radius = 10.0
        cap = radius * (1.0 - MIN_FLAT_BOTTOM_RATIO)
        # Anything at or past the cap gives the same profile as the cap itself.
        self.assertEqual(
            repr(scoop_profile(radius, 30, 6, 1000)),
            repr(scoop_profile(radius, 30, 6, cap)),
        )

    def test_the_cap_leaves_a_real_flat_run(self) -> None:
        from pyboxbuilder.compartments.finger_hole import MIN_FLAT_BOTTOM_RATIO

        self.assertGreater(MIN_FLAT_BOTTOM_RATIO, 0.0)
        self.assertLess(MIN_FLAT_BOTTOM_RATIO, 1.0)

    def test_default_r2_leaves_half_the_half_width_flat(self) -> None:
        from pyboxbuilder.compartments.finger_hole import DEFAULT_BOTTOM_ROUNDING_RATIO

        self.assertEqual(DEFAULT_BOTTOM_ROUNDING_RATIO, 0.5)
