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


class OutlineTests(unittest.TestCase):
    """The outline is a ring, and it must not close into a cusp."""

    def test_the_outline_overshoots_the_rim(self) -> None:
        """Closing flush across the top puts a zero-angle cusp at each end of
        the r1 arc, and offsetting such a corner miters to infinity — measured,
        a 15mm profile came back at 55mm."""
        from pyboxbuilder.compartments.finger_hole import (
            RIM_OVERSHOOT_MM,
            scoop_outline,
        )

        height = 30.0
        ring = scoop_outline(10, height, 5, 5)
        self.assertAlmostEqual(max(y for _, y in ring), height + RIM_OVERSHOOT_MM)

    def test_the_outline_is_a_closed_ring_around_the_cut(self) -> None:
        from pyboxbuilder.compartments.finger_hole import scoop_outline

        ring = scoop_outline(10, 30, 5, 5)
        self.assertGreater(len(ring), 8)
        # Symmetric about the centre line, and it reaches the full mouth width.
        self.assertAlmostEqual(min(x for x, _ in ring), -max(x for x, _ in ring))
        self.assertAlmostEqual(max(x for x, _ in ring), 15.0)
        self.assertAlmostEqual(min(y for _, y in ring), 0.0)

    def test_the_floor_bore_outline_is_a_bowl(self) -> None:
        """Its lowest point is a single tangent touch, not a flat run."""
        from pyboxbuilder.compartments.finger_hole import floor_bore_outline

        ring = floor_bore_outline(10, 30, 3)
        floor_points = [x for x, y in ring if abs(y) < 1e-6]
        self.assertLessEqual(len(floor_points), 2, "the bore has a flat bottom")


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

        # Both on: r1 defaults to half the throat (5mm here) on each side.
        full_low, full_high = self.span("wt2", 0)
        self.assertAlmostEqual(full_high - full_low, 32.0, delta=0.1)

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
# The same cut on a *lidded* box. `base` has lid_thickness 0, so its interior
# runs to the rim and a cut reaching 40 is correct there; a 2mm lid moves the
# interior top to 38 and the cut must follow it. Rounding is off on both so the
# comparison is not reading a facet-level disagreement between two
# independently meshed shells.
_lidless = dict(base, rounding=0, lid_thickness=0.0)
_lidded = dict(base, rounding=0, lid_thickness=2.0)
measure("removed_lidless",
        build_shell(dict(_lidless)) - build_shell(dict(_lidless, finger_holes=(Hole(ScoopSide.FRONT),))))
measure("removed_lidded",
        build_shell(dict(_lidded)) - build_shell(dict(_lidded, finger_holes=(Hole(ScoopSide.FRONT),))))
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

    def test_a_hole_hangs_from_the_interior_top_not_the_rim(self) -> None:
        """FR-043b1. The spec here has a 2mm lid, so the interior tops out at
        38 and the cut must stop there rather than at the box's own 40.

        Only the top is asserted: this measures the *difference* of two
        independently meshed bodies, which can disagree by a facet down in the
        bottom fillet and report a sliver below the cut.
        """
        lidless = self.box("removed_lidless")
        lidded = self.box("removed_lidded")
        lidless_top = lidless.position[2] + lidless.size[2]
        lidded_top = lidded.position[2] + lidded.size[2]

        # No lid: the interior runs to the rim, so the cut reaches it.
        self.assertAlmostEqual(lidless_top, 40.0, delta=0.05)
        # 2mm lid: the interior tops out at 38, and the cut stops there rather
        # than carving through the band the lid seats in.
        self.assertAlmostEqual(lidded_top, 38.0, delta=0.05)

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


class DerivedDefaultTests(unittest.TestCase):
    """FR-043a2/a3: the defaults have to work with no overrides."""

    def test_r1_scales_with_the_throat(self) -> None:
        """A fixed r1 is invisible on a big scoop and huge on a small one."""
        from pyboxbuilder.compartments.finger_hole import (
            DEFAULT_TOP_ROUNDING_RATIO,
            scoop_profile,
        )

        for radius in (4.0, 14.0):
            with self.subTest(radius=radius):
                derived = build_wall_scoop(200, 200, 30, ScoopSide.FRONT, radius=radius)
                explicit = build_wall_scoop(
                    200, 200, 30, ScoopSide.FRONT, radius=radius,
                    rounding_radius=radius * DEFAULT_TOP_ROUNDING_RATIO,
                )
                self.assertEqual(repr(derived), repr(explicit))
                self.assertIsNotNone(scoop_profile(radius, 30))

    def test_a_narrow_span_shrinks_both_not_just_r1(self) -> None:
        """The bug: capping the throat first left r1 at exactly zero."""
        from pyboxbuilder.compartments.finger_hole import scoop_profile

        span, radius = 20.0, 14.0
        narrow = build_wall_scoop(span, 40, 30, ScoopSide.FRONT, radius=radius)
        # r1 zeroed would make it identical to a scoop built with no roll at all.
        flat = build_wall_scoop(span, 40, 30, ScoopSide.FRONT, radius=radius,
                                rounding_radius=0.0)
        self.assertNotEqual(repr(narrow), repr(flat), "the top roll was zeroed")
        self.assertIsNotNone(scoop_profile(radius, 30))

    def test_hole_height_follows_the_radius(self) -> None:
        """`depth=None` means "as tall as the finger", not a fixed 6mm."""
        from pyboxbuilder.builders._base import FingerHoleBuilder

        self.assertIsNone(FingerHoleBuilder(side=ScoopSide.FRONT).depth)
        self.assertEqual(FingerHoleBuilder(side=ScoopSide.FRONT).radius, 14.0)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class HoleAlignmentTests(unittest.TestCase):
    """FR-043b1/b2: one call, right place, on every walled type."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder import BoxType, Project, ScoopSide
from pybosl2 import cuboid

for name in ("no_lid", "sliding", "cap", "slipover"):
    project = Project("A", game_box_size=(400, 200, 60), generate_spacers=False)
    box = project.box(BoxType(name), name, size=(100, 80, 40), position=(0, 0, 0))
    project._resolve_final_layout()
    plain = project._build_box_solids(box)[0]
    box.finger_hole(ScoopSide.FRONT)
    project._resolve_final_layout()
    holed = project._build_box_solids(box)[0]
    measure(name + "_removed", plain - holed)
    measure(name + "_body", holed)
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_every_type_gets_a_real_cut(self) -> None:
        for name in ("no_lid", "sliding", "cap", "slipover"):
            with self.subTest(box_type=name):
                removed = self.result.boxes[name + "_removed"]
                self.assertGreater(removed.size[0], 10.0, "the cut is a nick, not a scoop")
                self.assertGreater(removed.size[2], 5.0, "the cut is too shallow to use")

    def test_the_cut_starts_at_the_interior_top_not_the_rim(self) -> None:
        """On a lidded box the rim is above the interior; the hole follows the
        interior, so its top stops short of the box's own top."""
        lidless = self.result.boxes["no_lid_removed"]
        sliding = self.result.boxes["sliding_removed"]
        lidless_top = lidless.position[2] + lidless.size[2]
        sliding_top = sliding.position[2] + sliding.size[2]
        self.assertLess(sliding_top, lidless_top,
                        "the lidded box's hole was aligned to the rim")

    def test_no_type_is_enlarged_by_its_hole(self) -> None:
        for name in ("no_lid", "sliding", "cap", "slipover"):
            with self.subTest(box_type=name):
                box = self.result.boxes[name + "_body"]
                self.assertLessEqual(box.size[0], 100.5)
                self.assertLessEqual(box.size[1], 80.5)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class FaceRoundoverTests(unittest.TestCase):
    """FR-044e: the cut is wider at the face than mid-wall, or it is a cove.

    This is the measurement that separates the two, and it is the one that has
    caught the mistake three times: a cove and a roundover look equally smooth
    in a render, and differ only in which surface they are tangent to.
    """

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.compartments.finger_hole import build_wall_scoop
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

# 4mm wall, 2mm face fillet. The wall spans y = -4 .. 0.
scoop = build_wall_scoop(96, 76, 20, ScoopSide.FRONT, radius=14,
                         wall_thickness=4, rounding_edge=2.0)
for y, name in ((-3.9, "at_face"), (-2.0, "mid_wall")):
    measure(name, scoop & cuboid([300, 0.2, 300]).translate([0, y, 0]))

# With the fillet off there is nothing to widen: the two match.
square = build_wall_scoop(96, 76, 20, ScoopSide.FRONT, radius=14,
                          wall_thickness=4, rounding_edge=0.0)
for y, name in ((-3.9, "square_at_face"), (-2.0, "square_mid_wall")):
    measure(name, square & cuboid([300, 0.2, 300]).translate([0, y, 0]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def width(self, name: str) -> float:
        return self.result.boxes[name].size[0]

    def test_the_cut_is_wider_at_the_face(self) -> None:
        """A cove would make it *narrower* at the face, gouging the inside."""
        self.assertGreater(
            self.width("at_face"), self.width("mid_wall") + 1.0,
            "the fillet hollowed the wall instead of rolling the face in",
        )

    def test_it_widens_by_about_the_fillet_radius_each_side(self) -> None:
        self.assertAlmostEqual(
            self.width("at_face") - self.width("mid_wall"), 4.0, delta=0.5,
        )

    def test_no_fillet_means_no_widening(self) -> None:
        self.assertAlmostEqual(
            self.width("square_at_face"), self.width("square_mid_wall"), delta=0.1,
        )
