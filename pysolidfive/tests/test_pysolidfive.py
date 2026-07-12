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

# LibFile: pysolidfive/tests/test_pysolidfive.py
#    Tests for pysolidfive, run against pysolidfive/tests/mock_libfive.py's numeric-evaluation
#    stand-in for the real libfive/PythonSCAD C extension (not available in this environment).
#    Every test builds a shape, meshes it (which here just wraps the SDF closure, doing no real
#    work), and samples the SDF at hand-picked points to check against analytically-derived
#    expected values -- surface points should read ~0, interior points negative, exterior
#    positive, and known-radius rounding/chamfer offsets should match their closed-form formulas
#    exactly.
#
#    Run with: python3 -m unittest discover -s pysolidfive/tests -v
#
# FileGroup: pysolidfive

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
# pysolidfive/tests/test_pysolidfive.py -> pysolidfive/tests -> pysolidfive -> repo root, needed
# so `import pysolidfive` below resolves the real package rather than pysolidfive/ itself.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import mock_libfive  # noqa: E402  (must be imported, and installed, before pysolidfive)

import pysolidfive  # noqa: E402
from pysolidfive import CENTER, TOP, BOTTOM, LEFT, RIGHT, FRONT, BACK  # noqa: E402

SQRT2 = math.sqrt(2)


def round_offset(r: float) -> float:
    """Distance from a sharp right-angle corner to a fillet of radius `r` rounding it --
    the classic `r*(sqrt(2)-1)` relationship for a 2-D rounded-rect corner."""
    return r * (SQRT2 - 1)


def chamfer_offset(c: float) -> float:
    """Perpendicular distance from a sharp right-angle corner to a chamfer plane cutting `c`
    in from the corner along each edge."""
    return c / SQRT2


class TestPyShape(unittest.TestCase):
    """PyShape's own composition machinery (translate, boolean ops, lazy meshing) --
    independent of any specific shape's SDF formula."""

    def test_translate_shifts_the_surface(self):
        shape = pysolidfive.cuboid(size=[10.0, 10.0, 10.0]).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0)
        moved = shape.translate([100, 0, 0])
        self.assertAlmostEqual(moved.sample(105, 0, 0), 0)
        self.assertAlmostEqual(moved.sample(95, 0, 0), 0)

    def test_mesh_is_cached(self):
        shape = pysolidfive.cuboid(size=[10.0, 10.0, 10.0])
        self.assertIs(shape.mesh(), shape.mesh())

    def test_union(self):
        a = pysolidfive.cuboid(size=[6.0, 6.0, 6.0])
        b = pysolidfive.cuboid(size=[6.0, 6.0, 6.0]).translate([5, 0, 0])
        u = (a | b).mesh()
        self.assertLess(u.sample(-2, 0, 0), 0, "inside a only")
        self.assertLess(u.sample(2.4, 0, 0), 0, "inside the overlap")
        self.assertGreater(u.sample(10, 10, 10), 0, "outside both")

    def test_intersection(self):
        a = pysolidfive.cuboid(size=[10.0, 10.0, 10.0])
        b = pysolidfive.cuboid(size=[10.0, 10.0, 10.0]).translate([6, 0, 0])
        i = (a & b).mesh()
        self.assertLess(i.sample(3, 0, 0), 0, "inside the overlap region")
        self.assertGreater(i.sample(-3, 0, 0), 0, "inside a only, not b")

    def test_difference(self):
        a = pysolidfive.cuboid(size=[10.0, 10.0, 10.0])
        b = pysolidfive.sphere(r=3)
        d = (a - b).mesh()
        self.assertGreater(d.sample(0, 0, 0), 0, "carved out by the sphere")
        self.assertLess(d.sample(4.5, 0, 0), 0, "inside the box, outside the sphere")

    def test_round_and_chamfer_require_cuboid_size(self):
        # A shape not built from cuboid() (no cuboid_size metadata) can't be .round()ed.
        s = pysolidfive.sphere(r=5)
        with self.assertRaises(AssertionError):
            s.round(1)
        with self.assertRaises(AssertionError):
            s.chamfer(1)

    def test_rotate_euler_vector_form_moves_the_surface(self):
        # A +90-degree Z rotation is a standard CCW turn: (x,y) -> (-y,x), so a small cube
        # centered at (10,0,0) ends up centered at (0,10,0).
        shape = pysolidfive.cuboid(size=[4.0, 4.0, 4.0]).translate([10, 0, 0])
        rotated = shape.rotate([0, 0, 90]).mesh()
        self.assertLess(rotated.sample(0, 10, 0), 0, msg="cube center, moved to +Y")
        self.assertGreater(rotated.sample(10, 0, 0), 0, msg="original position, now outside")

    def test_rotate_angle_axis_form_matches_euler_form(self):
        shape = pysolidfive.cuboid(size=[4.0, 4.0, 4.0]).translate([10, 0, 0])
        via_axis = shape.rotate(90, [0, 0, 1]).mesh()
        via_euler = shape.rotate([0, 0, 90]).mesh()
        for p in [(0, 10, 0), (10, 0, 0), (-5, -5, 0)]:
            self.assertAlmostEqual(via_axis.sample(*p), via_euler.sample(*p), places=9)

    def test_rotate_composes_before_meshing_like_translate(self):
        # rotate(), like translate(), must stay at the SDF level (no early mesh) so a shape can
        # still be combined afterward -- verified here via union(), the same way
        # test_union()/test_intersection() verify | and & compose without forcing a mesh.
        a = pysolidfive.cuboid(size=[6.0, 6.0, 6.0])
        b = pysolidfive.cuboid(size=[6.0, 6.0, 6.0]).translate([5, 0, 0]).rotate([0, 0, 45])
        u = (a | b).mesh()
        self.assertLess(u.sample(-2, 0, 0), 0, msg="inside a only")

    def test_rotate_drops_cuboid_metadata(self):
        # Edge selectors (TOP/LEFT/etc.) are global-frame, evaluated before rotation -- like
        # bosl2's own anchor/edges-then-orient ordering -- so round()/chamfer() must refuse a
        # rotated cuboid the same way they already refuse a non-cuboid shape (see
        # test_round_and_chamfer_require_cuboid_size).
        shape = pysolidfive.cuboid(size=[10.0, 10.0, 10.0]).rotate([0, 0, 45])
        with self.assertRaises(AssertionError):
            shape.round(1)


class TestNamedCombinators(unittest.TestCase):
    """The named, n-ary CSG entry points (union/difference/intersection/hull) -- the operator
    forms (|, &, -) are covered by TestPyShape above; these check the varargs/list calling
    conventions, n-ary composition, bounds/res propagation, and hull()'s point pooling."""

    def test_union_varargs_and_list_forms_match(self):
        a = pysolidfive.cuboid(size=[6.0, 6.0, 6.0])
        b = pysolidfive.cuboid(size=[6.0, 6.0, 6.0]).translate([5, 0, 0])
        c = pysolidfive.cuboid(size=[6.0, 6.0, 6.0]).translate([10, 0, 0])
        for u in (pysolidfive.union(a, b, c), pysolidfive.union([a, b, c])):
            m = u.mesh()
            self.assertLess(m.sample(-2, 0, 0), 0, "inside a")
            self.assertLess(m.sample(10, 0, 0), 0, "inside c")
            self.assertGreater(m.sample(0, 10, 0), 0, "outside all three")
        self.assertEqual(pysolidfive.union(a, b, c).mx[0], 13.0, "bounds widen to the union")

    def test_union_of_one_is_identity(self):
        a = pysolidfive.cuboid(size=[6.0, 6.0, 6.0])
        self.assertIs(pysolidfive.union(a), a)

    def test_union_res_is_finest_child(self):
        a = pysolidfive.cuboid(size=[6.0, 6.0, 6.0], res=10)
        b = pysolidfive.cuboid(size=[6.0, 6.0, 6.0], res=30)
        self.assertEqual(pysolidfive.union(a, b).res, 30)

    def test_union_rejects_non_shapes(self):
        with self.assertRaises(AssertionError):
            pysolidfive.union(pysolidfive.cuboid(size=[6.0, 6.0, 6.0]), "not a shape")
        with self.assertRaises(AssertionError):
            pysolidfive.union()

    def test_intersection_nary(self):
        a = pysolidfive.cuboid(size=[10.0, 10.0, 10.0])
        b = pysolidfive.cuboid(size=[10.0, 10.0, 10.0]).translate([6, 0, 0])
        c = pysolidfive.cuboid(size=[10.0, 10.0, 10.0]).translate([3, 3, 0])
        m = pysolidfive.intersection(a, b, c).mesh()
        self.assertLess(m.sample(3, 3, 0), 0, "inside all three")
        self.assertGreater(m.sample(3, -3, 0), 0, "outside c")
        self.assertGreater(m.sample(-3, 0, 0), 0, "outside b")

    def test_intersection_asserts_on_disjoint_bounds(self):
        a = pysolidfive.cuboid(size=[4.0, 4.0, 4.0])
        b = pysolidfive.cuboid(size=[4.0, 4.0, 4.0]).translate([100, 0, 0])
        with self.assertRaises(AssertionError):
            pysolidfive.intersection(a, b)

    def test_difference_multiple_tools(self):
        base = pysolidfive.cuboid(size=[20.0, 20.0, 20.0])
        t1 = pysolidfive.sphere(r=3)
        t2 = pysolidfive.sphere(r=3).translate([6, 0, 0])
        d = pysolidfive.difference(base, t1, t2).mesh()
        self.assertGreater(d.sample(0, 0, 0), 0, "carved by t1")
        self.assertGreater(d.sample(6, 0, 0), 0, "carved by t2")
        self.assertLess(d.sample(-6, 0, 0), 0, "still solid away from both tools")
        self.assertEqual(pysolidfive.difference(base, t1).res, base.res, "keeps the base's res")

    def test_difference_with_no_tools_is_identity(self):
        base = pysolidfive.cuboid(size=[20.0, 20.0, 20.0])
        self.assertIs(pysolidfive.difference(base), base)

    def test_hull_bridges_two_separated_cubes(self):
        a = pysolidfive.cuboid(size=[8.0, 8.0, 8.0], res=8).translate([-10, 0, 0])
        b = pysolidfive.cuboid(size=[8.0, 8.0, 8.0], res=8).translate([10, 0, 0])
        h = pysolidfive.hull(a, b)
        m = h.mesh()
        self.assertLess(m.sample(0, 0, 0), 0, "the bridge between the cubes is inside the hull")
        self.assertLess(m.sample(-10, 0, 0), 0, "inside a")
        self.assertLess(m.sample(10, 0, 0), 0, "inside b")
        self.assertGreater(m.sample(0, 0, 10), 0, "above the hull")
        self.assertGreater(m.sample(0, 8, 0), 0, "beside the hull")
        self.assertEqual(h.mn[0], -14.0, "hull bounds == union bounds")
        self.assertEqual(h.mx[0], 14.0)

    def test_hull_is_lazy_until_first_mesh(self):
        a = pysolidfive.cuboid(size=[8.0, 8.0, 8.0], res=8).translate([-10, 0, 0])
        b = pysolidfive.cuboid(size=[8.0, 8.0, 8.0], res=8).translate([10, 0, 0])
        h = pysolidfive.hull(a, b)
        self.assertIsNone(a._mesh_cache, "constructing the hull must not mesh its children")
        self.assertIsNone(b._mesh_cache)
        h.mesh().sample(0, 0, 0)
        self.assertIsNotNone(a._mesh_cache, "sampling the hull meshes the children (once)")

    def test_hull_mixes_shapes_and_raw_points(self):
        base = pysolidfive.cuboid(size=[16.0, 16.0, 8.0], res=8)
        h = pysolidfive.hull(base, [[0.0, 0.0, 18.0]]).mesh()
        self.assertLess(h.sample(0, 0, 12), 0, "on the axis of the spike, between base and apex")
        self.assertGreater(h.sample(0, 0, 19), 0, "past the apex")
        self.assertGreater(h.sample(7, 7, 12), 0, "outside the taper")

    def test_hull_of_raw_points_matches_convex_polyhedron(self):
        pts = [[0, 0, 0], [10, 0, 0], [0, 10, 0], [0, 0, 10]]
        h = pysolidfive.hull(pts).mesh()
        ref = pysolidfive.convex_polyhedron(pts).mesh()
        for p in [(2, 2, 2), (5, 5, 5), (-1, -1, -1), (3, 0, 0)]:
            self.assertAlmostEqual(h.sample(*p), ref.sample(*p), places=9)


class TestCuboid(unittest.TestCase):
    def test_sharp_box_matches_reference_formula(self):
        size, b = [10.0, 10.0, 10.0], [5.0, 5.0, 5.0]
        shape = pysolidfive.cuboid(size=size, edges="NONE").mesh()
        for p in [(4.9, 0, 0), (0, -4.9, 0), (0, 0, 4.9), (0, 0, 0), (2, 2, 2)]:
            self.assertAlmostEqual(shape.sample(*p), _sharp_box_sdf(p, b), places=9)

    def test_edges_all_rounding_matches_classic_formula(self):
        # edges="ALL" rounding now takes pysolidfive's exact-formula fast path (_rounded_box_sdf(),
        # the same Minkowski-sum construction bosl2.shapes3d.cuboid() uses via a real
        # minkowski()), so this must match the classic single-formula rounded box exactly
        # everywhere -- not just near the surface -- including the true-3-D-corner and
        # far-exterior points the per-axis fallback path only approximates.
        size, b, r = [10.0, 10.0, 10.0], [5.0, 5.0, 5.0], 2.0
        shape = pysolidfive.cuboid(size=size, rounding=r, edges="ALL").mesh()
        for p in [
            (5, 0, 0),
            (0, 5, 0),
            (3, 3, 0),
            (3, 0, 3),
            (4, 4, 4),  # true 3-D corner, near the rounded surface
            (10, 10, 10),  # far outside the corner
            (0, 0, 0),  # center
            (-4, -4, -4),  # opposite corner
        ]:
            self.assertAlmostEqual(shape.sample(*p), _round_box_sdf(p, b, r), places=9)

    def test_rounding_zero_degenerates_to_sharp_box(self):
        size, b = [8.0, 8.0, 8.0], [4.0, 4.0, 4.0]
        shape = pysolidfive.cuboid(size=size, rounding=0, edges="ALL").mesh()
        for p in [(3, 0, 0), (0, 0, 0), (1, 1, 1)]:
            self.assertAlmostEqual(shape.sample(*p), _sharp_box_sdf(p, b), places=9)

    def test_per_edge_rounding_only_affects_selected_edges(self):
        size, r = [10.0, 10.0, 10.0], 2.0
        shape = pysolidfive.cuboid(size=size, rounding=r, edges=[list(TOP + LEFT), list(TOP + RIGHT)]).mesh()
        self.assertAlmostEqual(shape.sample(-5, 0, 5), round_offset(r), places=6, msg="TOP+LEFT selected")
        self.assertAlmostEqual(shape.sample(5, 0, 5), round_offset(r), places=6, msg="TOP+RIGHT selected")
        self.assertAlmostEqual(shape.sample(-5, 0, -5), 0, places=9, msg="BOTTOM+LEFT unselected")
        self.assertAlmostEqual(shape.sample(0, -5, 5), 0, places=9, msg="TOP+FRONT unselected")
        self.assertAlmostEqual(shape.sample(5, 5, 0), 0, places=9, msg="vertical edge unselected")

    def test_edges_z_shorthand_rounds_only_vertical_edges(self):
        # edges="Z" (the shorthand string form, not an explicit edge list) rounds only the 4
        # vertical edges -- matches tests/golden_images/cuboid_rounded_partial_edges.png's
        # "crisp flat top/bottom, rounded vertical corners" shape.
        size, r = [10.0, 10.0, 10.0], 2.0
        shape = pysolidfive.cuboid(size=size, rounding=r, edges="Z").mesh()
        self.assertAlmostEqual(shape.sample(5, 5, 0), round_offset(r), places=6, msg="vertical edge selected")
        self.assertAlmostEqual(shape.sample(5, 5, -3), round_offset(r), places=6, msg="vertical edge, off-center")
        self.assertAlmostEqual(shape.sample(-5, 0, 5), 0, places=9, msg="top horizontal edge unselected")
        self.assertAlmostEqual(shape.sample(0, -5, -5), 0, places=9, msg="bottom horizontal edge unselected")

    def test_per_edge_chamfer(self):
        size, c = [10.0, 10.0, 10.0], 2.0
        shape = pysolidfive.cuboid(size=size, chamfer=c, edges=[list(TOP + LEFT), list(TOP + RIGHT)]).mesh()
        self.assertAlmostEqual(shape.sample(-5, 0, 5), chamfer_offset(c), places=9)
        self.assertAlmostEqual(shape.sample(5, 0, 5), chamfer_offset(c), places=9)
        self.assertAlmostEqual(shape.sample(-5, 0, -5), 0, places=9)

    def test_rounding_and_chamfer_are_mutually_exclusive(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cuboid(size=[10.0, 10.0, 10.0], rounding=1, chamfer=1)

    def test_round_then_chamfer_compose(self):
        size, r, c = [10.0, 10.0, 10.0], 2.0, 1.5
        shape = pysolidfive.cuboid(size=size).round(r, edges="Z").chamfer(c, edges=[list(TOP + FRONT)]).mesh()
        self.assertAlmostEqual(shape.sample(5, 5, 0), round_offset(r), places=6, msg="Z-rounded vertical edge")
        self.assertAlmostEqual(shape.sample(0, -5, 5), chamfer_offset(c), places=9, msg="chamfered TOP+FRONT edge")

    def test_translate_then_chamfer_composes_correctly(self):
        # Exercises PyShape's cuboid_center tracking through translate().
        size, c = [10.0, 10.0, 10.0], 2.0
        shape = pysolidfive.cuboid(size=size).translate([100, 0, 0]).chamfer(c, edges=[list(TOP + LEFT)]).mesh()
        self.assertAlmostEqual(shape.sample(95, 0, 5), chamfer_offset(c), places=9)
        self.assertAlmostEqual(shape.sample(95, 0, -5), 0, places=9)

    def test_cube_is_a_plain_cuboid(self):
        shape = pysolidfive.cube(size=10).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0)
        self.assertLess(shape.sample(0, 0, 0), 0)

    def test_negative_rounding_flares_selected_edge(self):
        # BOSL2's negative rounding: an external cove flare. cuboid [20,20,10] with r=-2 on
        # BACK+TOP: the flare block spans y in [10,12], z in [3,5], minus the quarter
        # cylinder centered at (y,z)=(12,3) radius 2.
        shape = pysolidfive.cuboid([20.0, 20.0, 10.0], rounding=-2, edges=[list(BACK + TOP)]).mesh()
        self.assertLess(shape.sample(0, 10.5, 4.5), 0, msg="inside the flare wing")
        self.assertGreater(shape.sample(0, 11.5, 3.3), 0, msg="carved by the concave arc")
        self.assertGreater(shape.sample(0, 11, 5.2), 0, msg="above the top face")
        self.assertLess(shape.sample(0, 9, 0), 0, msg="plain box interior intact")
        self.assertGreater(shape.sample(0, -10.5, 4.5), 0, msg="unselected FRONT+TOP edge unflared")
        # The PyShape constructor pads mn/mx slightly (frep needs the surface strictly
        # inside the sampled region), so compare with headroom rather than exactly.
        self.assertGreaterEqual(shape.mx[1], 12.0, msg="bounds cover the flare wing")
        self.assertLess(shape.mx[1], 12.5, msg="bounds not wildly padded")
        self.assertGreater(shape.mn[1], -10.5, msg="unflared side bounds untouched (minus padding)")

    def test_negative_rounding_rejects_z_edges(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cuboid([20.0, 20.0, 10.0], rounding=-2, edges="Z")


class TestOctahedron(unittest.TestCase):
    def test_l1_ball_sdf(self):
        s = 10
        shape = pysolidfive.octahedron(size=s).mesh()
        self.assertAlmostEqual(shape.sample(s / 2, 0, 0), 0)
        self.assertAlmostEqual(shape.sample(s / 4, 0, 0), -s / 4)
        self.assertGreater(shape.sample(s, s, s), 0)


class TestWedge(unittest.TestCase):
    def test_right_angle_and_hypotenuse(self):
        by, bz = 3, 4
        shape = pysolidfive.wedge(size=[10, 6, 8], anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(0, -by, -bz), 0, msg="right-angle vertex")
        self.assertLess(shape.sample(0, -1, -1), 0, msg="biased toward the right-angle corner")
        self.assertAlmostEqual(shape.sample(0, -by, bz), 0, msg="a real vertex on the hypotenuse edge")
        self.assertGreater(shape.sample(0, by, bz), 0, msg="the removed corner")
        self.assertAlmostEqual(shape.sample(0, by, -bz), 0, msg="another real vertex")


class TestScale(unittest.TestCase):
    def test_uniform_scale_moves_surface_and_keeps_distance_calibrated(self):
        shape = pysolidfive.cuboid([10.0, 10.0, 10.0]).scale(2).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, 0), 0, places=9, msg="face scaled out to +-10")
        self.assertAlmostEqual(shape.sample(12, 0, 0), 2, places=9, msg="uniform scaling keeps exact distance")
        self.assertAlmostEqual(shape.sample(0, 0, 0), -10, places=9)

    def test_per_axis_scale_zero_set(self):
        shape = pysolidfive.cuboid([10.0, 10.0, 10.0]).scale([2, 1, 0.5]).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, 0), 0, places=9, msg="x face at +-10")
        self.assertAlmostEqual(shape.sample(0, 5, 0), 0, places=9, msg="y face unchanged")
        self.assertAlmostEqual(shape.sample(0, 0, 2.5), 0, places=9, msg="z face squashed to +-2.5")
        self.assertLess(shape.sample(0, 0, 0), 0)
        self.assertGreater(shape.sample(0, 0, 3), 0)

    def test_scale_drops_cuboid_metadata(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cuboid([10.0, 10.0, 10.0]).scale(2).round(1, edges="Z")

    def test_rejects_nonpositive_factors(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cuboid([10.0, 10.0, 10.0]).scale([1, -1, 1])


class TestConvexPolyhedron(unittest.TestCase):
    def test_tetrahedron_from_vertices(self):
        pts = [[0, 0, 0], [10, 0, 0], [0, 10, 0], [0, 0, 10]]
        shape = pysolidfive.convex_polyhedron(pts).mesh()
        self.assertLess(shape.sample(1, 1, 1), 0, msg="inside near the right-angle corner")
        self.assertAlmostEqual(shape.sample(5, 0, 5), 0, places=9, msg="on the x/z face")
        self.assertGreater(shape.sample(5, 5, 5), 0, msg="outside the diagonal face")
        self.assertAlmostEqual(shape.sample(-3, 3, 3), 3, places=9, msg="exact perpendicular distance at a face")

    def test_octahedron_matches_builtin_zero_set(self):
        # Same solid two ways: hulled vertices vs the builtin L1-ball octahedron(). Their
        # VALUES differ by a sqrt(3) calibration factor (plane distance vs |x|+|y|+|z|), so
        # compare the sign everywhere and the zero set on a face point.
        s = 10.0
        h = s / 2
        pts = [[h, 0, 0], [-h, 0, 0], [0, h, 0], [0, -h, 0], [0, 0, h], [0, 0, -h]]
        hulled = pysolidfive.convex_polyhedron(pts).mesh()
        builtin = pysolidfive.octahedron(size=s).mesh()
        face_pt = (h / 3, h / 3, h / 3)  # centroid of the +++ face, on both zero sets
        self.assertAlmostEqual(hulled.sample(*face_pt), 0, places=9)
        self.assertAlmostEqual(builtin.sample(*face_pt), 0, places=9)
        for p in [(1, 1, 1), (h, h, h), (0, 0, 0), (2, 0, 0), (h + 1, 0, 0)]:
            self.assertEqual(
                hulled.sample(*p) > 0, builtin.sample(*p) > 0, msg=f"sign disagreement at {p}"
            )

    def test_interior_points_do_not_make_planes(self):
        # A point strictly inside the hull must not contribute any face.
        pts = [[0, 0, 0], [10, 0, 0], [0, 10, 0], [0, 0, 10], [2, 2, 2]]
        with_interior = pysolidfive.convex_polyhedron(pts).mesh()
        without = pysolidfive.convex_polyhedron(pts[:4]).mesh()
        for p in [(1, 1, 1), (5, 5, 5), (-3, 3, 3), (5, 0, 5)]:
            self.assertAlmostEqual(with_interior.sample(*p), without.sample(*p), places=9)

    def test_rejects_too_few_or_coplanar_points(self):
        with self.assertRaises(AssertionError):
            pysolidfive.convex_polyhedron([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        with self.assertRaises(AssertionError):
            pysolidfive.convex_polyhedron([[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])


class TestSphere(unittest.TestCase):
    def test_sphere(self):
        shape = pysolidfive.sphere(r=5).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0)
        self.assertAlmostEqual(shape.sample(0, 0, 0), -5)
        self.assertAlmostEqual(shape.sample(10, 0, 0), 5)

    def test_spheroid_is_a_plain_sphere(self):
        shape = pysolidfive.spheroid(r=3).mesh()
        self.assertAlmostEqual(shape.sample(3, 0, 0), 0)


class TestTorus(unittest.TestCase):
    def test_torus(self):
        shape = pysolidfive.torus(r_maj=10, r_min=2).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, 0), -2, msg="center of the tube ring")
        self.assertAlmostEqual(shape.sample(12, 0, 0), 0, msg="outer equator")
        self.assertAlmostEqual(shape.sample(8, 0, 0), 0, msg="inner equator")
        self.assertAlmostEqual(shape.sample(10, 0, 2), 0, msg="top of the tube")


class TestCylinders(unittest.TestCase):
    def test_plain_cylinder(self):
        shape = pysolidfive.cylinder(h=10, r=5).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0)
        self.assertAlmostEqual(shape.sample(0, 0, 5), 0)
        self.assertLess(shape.sample(0, 0, 0), 0)

    def test_tapered_cylinder(self):
        shape = pysolidfive.cylinder(h=10, r1=5, r2=2).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, -5), 0, places=3, msg="bottom rim")
        self.assertAlmostEqual(shape.sample(2, 0, 5), 0, places=3, msg="top rim")

    def test_cyl_uniform_rounding(self):
        r = 1.0
        shape = pysolidfive.cyl(h=10, r=5, rounding=r).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 5), round_offset(r), places=6, msg="rim corner")
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0, places=9, msg="flat side wall")
        self.assertAlmostEqual(shape.sample(0, 0, 5), 0, places=9, msg="flat top cap")

    def test_cyl_independent_top_bottom_chamfer(self):
        c2 = 1.5
        shape = pysolidfive.cyl(h=10, r=5, chamfer1=0, chamfer2=c2).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 5), chamfer_offset(c2), places=6, msg="chamfered top rim")
        self.assertAlmostEqual(shape.sample(5, 0, -5), 0, places=9, msg="unchamfered bottom rim")

    def test_cyl_rounding_and_chamfer_are_mutually_exclusive(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cyl(h=10, r=5, rounding=1, chamfer=1)

    def test_xcyl_ycyl_zcyl_orient_the_axis(self):
        for shape_fn, expect_axial, expect_radial in [
            (pysolidfive.xcyl, (5, 0, 0), [(0, 5, 0), (0, 0, 5)]),
            (pysolidfive.ycyl, (0, 5, 0), [(5, 0, 0), (0, 0, 5)]),
            (pysolidfive.zcyl, (0, 0, 5), [(5, 0, 0), (0, 5, 0)]),
        ]:
            shape = shape_fn(h=10, r=5).mesh()
            self.assertAlmostEqual(shape.sample(*expect_axial), 0, msg=f"{shape_fn.__name__} end cap")
            for p in expect_radial:
                self.assertAlmostEqual(shape.sample(*p), 0, msg=f"{shape_fn.__name__} wall")
            self.assertLess(shape.sample(0, 0, 0), 0)


class TestMirror(unittest.TestCase):
    def test_mirror_z_flips_a_cone(self):
        # A bottom-anchored cone (wide base at z=0, apex at z=8) mirrored across z=0.
        cone = pysolidfive.cylinder(h=8, r1=4, r2=0.01, center=False)
        flipped = cone.mirror([0, 0, 1]).mesh()
        self.assertLess(flipped.sample(3, 0, -0.5), 0, msg="wide base now just below z=0")
        self.assertGreater(flipped.sample(3, 0, 0.5), 0, msg="nothing above z=0 at r=3")
        self.assertLess(flipped.sample(0, 0, -7.5), 0, msg="apex now at the bottom")
        self.assertLessEqual(flipped.mx[2], 0.5, msg="bounds flipped below the plane")

    def test_mirror_diagonal_normal_swaps_axes(self):
        box = pysolidfive.cuboid([10, 2, 2]).translate([10, 0, 0])
        swapped = box.mirror([1, -1, 0]).mesh()  # reflection across the x=y plane
        self.assertLess(swapped.sample(0, 10, 0), 0, msg="long axis now along y")
        self.assertGreater(swapped.sample(10, 0, 0), 0, msg="original position empty")


class TestCylShift(unittest.TestCase):
    def test_oblique_cone_top_lands_at_shift(self):
        # cyl(shift=) slides the section center linearly from [0,0] at the bottom to `shift`
        # at the top (BOSL2's oblique cone). h=10 centered, r1=4, r2=2, shift=[6, 0].
        shape = pysolidfive.cyl(h=10, r1=4, r2=2, shift=[6, 0]).mesh()
        self.assertLess(shape.sample(0, 0, -4.9), 0, msg="bottom center solid")
        self.assertLess(shape.sample(6, 0, 4.9), 0, msg="top center slid to x=6")
        self.assertGreater(shape.sample(0, 0, 4.9), 0, msg="original top center now empty")
        self.assertGreater(shape.sample(6, 0, 5.1), 0, msg="above the top face")

    def test_shift_rejects_rounding(self):
        with self.assertRaises(AssertionError):
            pysolidfive.cyl(h=10, r=4, shift=[2, 0], rounding=1)


class TestTubes(unittest.TestCase):
    def test_tube(self):
        shape = pysolidfive.tube(h=10, outer_r=5, ir=3).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0, msg="outer wall")
        self.assertAlmostEqual(shape.sample(3, 0, 0), 0, msg="inner wall")
        self.assertLess(shape.sample(4, 0, 0), 0, msg="inside the wall material")
        self.assertGreater(shape.sample(1, 0, 0), 0, msg="inside the hollow bore")

    def test_tube_requires_enough_parameters(self):
        # outer_r alone *does* work (wall defaults to 1, giving an inner radius), matching
        # bosl2.shapes3d.tube()'s own default -- but no radius/diameter/wall at all can't
        # resolve anything.
        with self.assertRaises(AssertionError):
            pysolidfive.tube(h=10)

    def test_rect_tube(self):
        shape = pysolidfive.rect_tube(h=10, size=[20, 16], isize=[16, 12], anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, 0), 0, msg="outer wall")
        self.assertAlmostEqual(shape.sample(8, 0, 0), 0, msg="inner wall")
        self.assertLess(shape.sample(9, 0, 0), 0, msg="in the wall")
        self.assertGreater(shape.sample(0, 0, 0), 0, msg="in the hollow bore")


class TestPieSlice(unittest.TestCase):
    def test_acute_sector(self):
        shape = pysolidfive.pie_slice(h=10, r=5, ang=90).mesh()
        self.assertLess(shape.sample(3, 3, 0), 0, msg="inside the 90deg wedge (Q1)")
        self.assertGreater(shape.sample(-3, 3, 0), 0, msg="Q2 excluded")
        self.assertGreater(shape.sample(3, -3, 0), 0, msg="Q4 excluded")

    def test_reflex_sector(self):
        shape = pysolidfive.pie_slice(h=10, r=5, ang=270).mesh()
        self.assertLess(shape.sample(3, 3, 0), 0, msg="Q1 included")
        self.assertLess(shape.sample(-3, 3, 0), 0, msg="Q2 included")
        self.assertLess(shape.sample(-3, -3, 0), 0, msg="Q3 included")
        self.assertGreater(shape.sample(3, -3, 0), 0, msg="Q4 (270-360) excluded")


class TestPrismoid(unittest.TestCase):
    def test_non_tapered_matches_plain_box(self):
        shape = pysolidfive.prismoid(size1=[10, 10], size2=[10, 10], h=10, anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 0), 0)
        self.assertAlmostEqual(shape.sample(0, 0, 5), 0)
        self.assertLess(shape.sample(0, 0, 0), 0)

    def test_tapered(self):
        shape = pysolidfive.prismoid(size1=[20, 20], size2=[10, 10], h=10, anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, -5), 0, places=3, msg="bottom rim (wider)")
        self.assertAlmostEqual(shape.sample(5, 0, 5), 0, places=3, msg="top rim (narrower)")
        self.assertLess(shape.sample(0, 0, 0), 0)


class TestInteriorFillet(unittest.TestCase):
    def test_90_degree_fillet(self):
        shape = pysolidfive.interior_fillet(l=10, r=2, anchor=CENTER).mesh()
        self.assertLess(shape.sample(0.5, 0, 0.5), 0, msg="near-corner sliver, inside the fillet")
        self.assertGreater(shape.sample(2, 0, 2), 0, msg="circle center, the carved-out hole")
        self.assertGreater(shape.sample(1.5, 0, 1.5), 0, msg="past the arc, inside the removed circle")
        self.assertGreater(shape.sample(-1, 0, 1), 0, msg="outside the wedge entirely")


class TestPositionableCutters(unittest.TestCase):
    """rounding_edge_mask()/polygon_extrude(): standalone cutters for edges outside a cuboid()'s
    own edge/corner treatment (used by e.g. sliding_box.py's two-layer lid, positioned by hand
    via .rotate()/.translate() rather than an automatic per-edge sweep)."""

    def test_rounding_edge_mask(self):
        shape = pysolidfive.rounding_edge_mask(l=10, r=2).mesh()
        self.assertLess(shape.sample(0, 0, 0), 0, msg="sharp corner, inside the cutter")
        self.assertGreater(shape.sample(2, 2, 0), 0, msg="far corner (circle center), outside the cutter")
        self.assertAlmostEqual(shape.sample(2, 0, 0), 0, places=9, msg="tangent point on the flat")
        self.assertGreater(shape.sample(-1, 0.5, 0), 0, msg="past the excess skirt, outside the cutter")
        self.assertGreater(shape.sample(0, 0, 6), 0, msg="past the swept length, outside the cutter")

    def test_polygon_extrude(self):
        # A simple right triangle: (0,0), (4,0), (0,4).
        shape = pysolidfive.polygon_extrude([[0, 0], [4, 0], [0, 4]], length=10).mesh()
        self.assertLess(shape.sample(1, 1, 0), 0, msg="inside the triangle")
        self.assertGreater(shape.sample(3, 3, 0), 0, msg="outside the hypotenuse")
        self.assertGreater(shape.sample(-1, 1, 0), 0, msg="outside the left edge")
        self.assertGreater(shape.sample(1, 1, 6), 0, msg="past the swept length")

    def test_polygon_extrude_accepts_either_winding_order(self):
        pts = [[0, 0], [4, 0], [0, 4]]
        a = pysolidfive.polygon_extrude(pts, length=10).mesh()
        b = pysolidfive.polygon_extrude(list(reversed(pts)), length=10).mesh()
        for p in [(1, 1, 0), (3, 3, 0), (-1, 1, 0)]:
            self.assertAlmostEqual(a.sample(*p), b.sample(*p), places=9)


class TestPolygonPrism(unittest.TestCase):
    """polygon_prism(): the exact winding-number polygon SDF plus offset_sweep-style rim
    treatments -- the primitive no_lid.py's path/polygon boxes are built from."""

    # A concave L: 40 wide/long arms, 15 thick.
    L_PATH = [[0, 0], [40, 0], [40, 15], [15, 15], [15, 40], [0, 40]]

    def test_concave_polygon_sign_is_exact(self):
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10).mesh()
        self.assertLess(shape.sample(5, 5, 5), 0, msg="inside the corner arm")
        self.assertLess(shape.sample(30, 7, 5), 0, msg="inside the X arm")
        self.assertLess(shape.sample(7, 30, 5), 0, msg="inside the Y arm")
        self.assertGreater(shape.sample(30, 30, 5), 0, msg="in the concave notch -- outside")
        self.assertGreater(shape.sample(-5, 5, 5), 0, msg="left of the outline")
        self.assertGreater(shape.sample(5, 5, 11), 0, msg="above the prism")
        self.assertGreater(shape.sample(5, 5, -1), 0, msg="below the prism")

    def test_distance_is_face_exact_and_sign_correct_past_vertices(self):
        # The convex-deficiency decomposition is exact perpendicular distance near faces (the
        # notch faces included -- the pocket subtraction recovers the true value there), and a
        # sign-correct half-plane underestimate out past a convex vertex, same documented
        # tradeoff as polygon_extrude()/the convex fast path.
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10).mesh()
        # Inside the concave notch the nearest features are the two notch FACES: from (20, 20)
        # that's exactly 5, to either.
        self.assertAlmostEqual(shape.sample(20, 20, 5), 5.0, places=9)
        self.assertAlmostEqual(shape.sample(-5, 20, 5), 5.0, places=9, msg="outside a hull face")
        # Past the (40, 0) corner: true distance is hypot(5, 5), the half-plane form reads the
        # dominating plane's 5 -- positive (sign-correct), never more than the true distance.
        v = shape.sample(45, -5, 5)
        self.assertGreater(v, 0)
        self.assertLessEqual(v, math.hypot(5, 5) + 1e-9)

    def test_boundary_reads_zero(self):
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10).mesh()
        self.assertAlmostEqual(shape.sample(0, 20, 5), 0, places=9, msg="on the left face")
        self.assertAlmostEqual(shape.sample(20, 15, 5), 0, places=9, msg="on the notch face")
        self.assertAlmostEqual(shape.sample(20, 7, 10), 0, places=9, msg="on the top face")

    def test_either_winding_order(self):
        a = pysolidfive.polygon_prism(self.L_PATH, h=10).mesh()
        b = pysolidfive.polygon_prism(list(reversed(self.L_PATH)), h=10).mesh()
        for p in [(5, 5, 5), (30, 30, 5), (45, -5, 5)]:
            self.assertAlmostEqual(a.sample(*p), b.sample(*p), places=9)

    def test_top_roundover_rim(self):
        # rounding_top=2 on a straight wall at x=0: at the rim the surface pulls in along a
        # quarter circle -- the 45-degree point of that arc sits at
        # (r - r/sqrt(2)) inside the wall and (r - r/sqrt(2)) below the top.
        r = 2.0
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10, rounding_top=r).mesh()
        k = r - r / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(-0 + k, 20, 10 - k), 0, places=9, msg="45-degree point of the rim arc")
        self.assertGreater(shape.sample(0.01, 20, 9.99), 0, msg="sharp top corner is rounded away")
        self.assertAlmostEqual(shape.sample(0, 20, 5), 0, places=9, msg="wall below the rim unaffected")
        self.assertAlmostEqual(shape.sample(20, 7, 0), 0, places=9, msg="square bottom rim unaffected")

    def test_bottom_roundover_rim(self):
        r = 2.0
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10, rounding_bottom=r).mesh()
        k = r - r / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(k, 20, k), 0, places=9)
        self.assertGreater(shape.sample(0.01, 20, 0.01), 0, msg="sharp bottom corner is rounded away")
        self.assertAlmostEqual(shape.sample(20, 7, 10), 0, places=9, msg="square top rim unaffected")

    def test_top_flare_adds_material_outside_the_wall(self):
        # rounding_top=-2 flares the rim outward: at the very top the wall reaches 2 out; at
        # the flare's start (2 below the top) it is flush; between, the boundary follows a
        # quarter circle centered 2 out at 2 below the top.
        f = 2.0
        shape = pysolidfive.polygon_prism(self.L_PATH, h=10, rounding_top=-f).mesh()
        self.assertGreater(shape.sample(-1, 20, 5), 0, msg="mid-wall not flared")
        self.assertLess(shape.sample(-1, 20, 9.9), 0, msg="inside the flare near the top")
        self.assertGreater(shape.sample(-1, 20, 10.1), 0, msg="above the rim plane")
        # The 45-degree point of the flare arc: center (u=f, w=h-f), surface at
        # u = f - f/sqrt(2), w = h - f + f/sqrt(2).
        u = f - f / math.sqrt(2)
        w = 10 - f + f / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(-u, 20, w), 0, places=6)

    def test_region_of_disjoint_islands(self):
        square_a = [[0, 0], [10, 0], [10, 10], [0, 10]]
        square_b = [[20, 0], [30, 0], [30, 10], [0 + 20, 10]]
        shape = pysolidfive.polygon_prism([square_a, square_b], h=5).mesh()
        self.assertLess(shape.sample(5, 5, 2), 0, msg="inside island A")
        self.assertLess(shape.sample(25, 5, 2), 0, msg="inside island B")
        self.assertGreater(shape.sample(15, 5, 2), 0, msg="in the gap between islands")

    def test_rejects_bad_arguments(self):
        with self.assertRaises(AssertionError):
            pysolidfive.polygon_prism(self.L_PATH, h=0)
        with self.assertRaises(AssertionError):
            pysolidfive.polygon_prism([[0, 0], [1, 0]], h=5)
        with self.assertRaises(AssertionError):
            pysolidfive.polygon_prism(self.L_PATH, h=5, rounding_top=6)


class TestShape2D(unittest.TestCase):
    """The 2-D SDF layer (PyShape2D + circle2d/rect2d/polygon2d/stroke2d/hull2d_discs),
    verified through .extrude() since a 2-D SDF only becomes measurable geometry as a prism."""

    def test_circle_extruded_to_height(self):
        shape = pysolidfive.circle2d(r=5).extrude(4).mesh()
        self.assertAlmostEqual(shape.sample(5, 0, 2), 0, places=9, msg="on the wall")
        # At the centroid the NEAREST surface is a z cap (distance 2), not the wall (5).
        self.assertAlmostEqual(shape.sample(0, 0, 2), -2, places=9, msg="exact distance inside")
        self.assertGreater(shape.sample(0, 0, 5), 0, msg="above the extrusion height")
        self.assertGreater(shape.sample(0, 0, -1), 0, msg="below z=0 (base sits at z=0)")

    def test_extrude_centered(self):
        shape = pysolidfive.circle2d(r=5).extrude(4, center=True).mesh()
        self.assertAlmostEqual(shape.sample(0, 0, 2), 0, places=9)
        self.assertAlmostEqual(shape.sample(0, 0, -2), 0, places=9)

    def test_rect_rounded_corner(self):
        r = 2.0
        shape = pysolidfive.rect2d([10, 10], rounding=r).extrude(2).mesh()
        k = r - r / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(5 - k, 5 - k, 1), 0, places=9, msg="45-degree point of the corner arc")
        self.assertGreater(shape.sample(4.99, 4.99, 1), 0, msg="sharp corner rounded away")
        self.assertAlmostEqual(shape.sample(5, 0, 1), 0, places=9, msg="face unaffected")

    def test_rect_anchor(self):
        shape = pysolidfive.rect2d([10, 6], anchor=[-1, -1]).extrude(2).mesh()
        self.assertAlmostEqual(shape.sample(0, 0, 1), 0, places=9, msg="corner at origin")
        self.assertLess(shape.sample(5, 3, 1), 0, msg="interior at the anchored position")

    def test_polygon2d_concave(self):
        L = [[0, 0], [40, 0], [40, 15], [15, 15], [15, 40], [0, 40]]
        shape = pysolidfive.polygon2d(L).extrude(3).mesh()
        self.assertLess(shape.sample(5, 5, 1), 0)
        self.assertGreater(shape.sample(30, 30, 1), 0, msg="the notch is outside")
        self.assertAlmostEqual(shape.sample(20, 15, 1), 0, places=9, msg="on the notch face")

    def test_offset_grows_and_shrinks_exactly(self):
        grown = pysolidfive.circle2d(r=5).offset(2).extrude(2).mesh()
        self.assertAlmostEqual(grown.sample(7, 0, 1), 0, places=9)
        shrunk = pysolidfive.circle2d(r=5).offset(-2).extrude(2).mesh()
        self.assertAlmostEqual(shrunk.sample(3, 0, 1), 0, places=9)

    def test_outline_strip(self):
        ring = pysolidfive.circle2d(r=5).outline(2).extrude(2).mesh()
        self.assertAlmostEqual(ring.sample(6, 0, 1), 0, places=9, msg="outer edge of the strip")
        self.assertAlmostEqual(ring.sample(4, 0, 1), 0, places=9, msg="inner edge of the strip")
        self.assertLess(ring.sample(5, 0, 1), 0, msg="centered on the boundary")
        self.assertGreater(ring.sample(0, 0, 1), 0, msg="middle punched out")

    def test_booleans_and_transforms(self):
        a = pysolidfive.circle2d(r=4)
        b = pysolidfive.circle2d(r=4).translate([6, 0])
        union = (a | b).extrude(2).mesh()
        self.assertLess(union.sample(3, 0, 1), 0, msg="in the overlap")
        self.assertLess(union.sample(9, 0, 1), 0, msg="inside b only")
        diff = (a - b).extrude(2).mesh()
        self.assertGreater(diff.sample(3, 0, 1), 0, msg="removed by b")
        self.assertLess(diff.sample(-3, 0, 1), 0, msg="kept from a")
        rot = pysolidfive.rect2d([10, 2]).rotate(90).extrude(2).mesh()
        self.assertLess(rot.sample(0, 4, 1), 0, msg="long axis now vertical")
        self.assertGreater(rot.sample(4, 0, 1), 0)

    def test_mirror(self):
        tri = pysolidfive.polygon2d([[0, 0], [10, 0], [0, 10]])
        mirrored = tri.mirror([1, 0]).extrude(2).mesh()
        self.assertLess(mirrored.sample(-2, 2, 1), 0, msg="flipped into -x")
        self.assertGreater(mirrored.sample(2, 2, 1), 0)

    def test_stroke_round_caps_and_joins(self):
        w = 2.0
        shape = pysolidfive.stroke2d([[0, 0], [10, 0], [10, 10]], width=w).extrude(2).mesh()
        self.assertAlmostEqual(shape.sample(5, 1, 1), 0, places=9, msg="segment edge")
        self.assertAlmostEqual(shape.sample(-1, 0, 1), 0, places=9, msg="round start cap")
        self.assertAlmostEqual(shape.sample(10 + 1 / math.sqrt(2), -1 / math.sqrt(2), 1), 0, places=6, msg="round join bulge")
        self.assertGreater(shape.sample(5, 5, 1), 0, msg="off the path")

    def test_stroke_closed(self):
        shape = pysolidfive.stroke2d([[0, 0], [10, 0], [10, 10], [0, 10]], width=2, closed=True).extrude(2).mesh()
        self.assertAlmostEqual(shape.sample(0, 5, 1), -1, places=9, msg="closing segment present")

    def test_hull_of_equal_discs_has_true_arc_corners(self):
        r = 2.0
        shape = pysolidfive.hull2d_discs([(0, 0, r), (10, 0, r), (5, 8, r)]).extrude(2).mesh()
        self.assertAlmostEqual(shape.sample(5, -r, 1), 0, places=9, msg="tangent line between discs")
        # The corner arc: exactly r beyond the corner disc's center, in the outward diagonal.
        self.assertAlmostEqual(shape.sample(-r / math.sqrt(2), -r / math.sqrt(2), 1), 0, places=9)
        self.assertLess(shape.sample(5, 3, 1), 0, msg="interior")

    def test_hull_of_two_discs_is_a_capsule(self):
        shape = pysolidfive.hull2d_discs([(0, 0, 3), (10, 0, 3)]).extrude(2).mesh()
        self.assertAlmostEqual(shape.sample(5, 3, 1), 0, places=9)
        self.assertAlmostEqual(shape.sample(13, 0, 1), 0, places=9)
        self.assertLess(shape.sample(5, 0, 1), 0)

    def test_linear_extrude_alias(self):
        a = pysolidfive.circle2d(r=5).linear_extrude(height=4).mesh()
        b = pysolidfive.circle2d(r=5).extrude(4).mesh()
        for p in [(5, 0, 2), (0, 0, 2), (0, 0, 5)]:
            self.assertAlmostEqual(a.sample(*p), b.sample(*p), places=9)

    def test_extrude_rim_roundover(self):
        r = 1.0
        shape = pysolidfive.circle2d(r=5).extrude(4, rounding_top=r).mesh()
        k = r - r / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(5 - k, 0, 4 - k), 0, places=9, msg="rim arc 45-degree point")
        self.assertGreater(shape.sample(4.99, 0, 3.99), 0, msg="sharp rim rounded away")

    def test_rect_per_corner_rounding(self):
        # BOSL2 rect() corner order: [X+Y+, X-Y+, X-Y-, X+Y-]. Round only the two +x corners
        # (the Sword2d blade-tip idiom, rounding=[0, r, r, 0] rounds the -x pair instead).
        r = 2.0
        shape = pysolidfive.rect2d([10, 10], rounding=[r, 0, 0, r]).extrude(2).mesh()
        k = r - r / math.sqrt(2)
        self.assertAlmostEqual(shape.sample(5 - k, 5 - k, 1), 0, places=9, msg="X+Y+ rounded")
        self.assertAlmostEqual(shape.sample(5 - k, -5 + k, 1), 0, places=9, msg="X+Y- rounded")
        self.assertAlmostEqual(shape.sample(-5, -5, 1), 0, places=9, msg="X-Y- stays sharp")
        self.assertAlmostEqual(shape.sample(-5, 5, 1), 0, places=9, msg="X-Y+ stays sharp")

    def test_supershape2d_square_family(self):
        # m=4, n1 large approaches a square of circumradius r; just anchor the basics: sampled
        # outline closes, contains the origin, and honours the r= scaling.
        shape = pysolidfive.supershape2d(m1=4, n1=1, r=10, n=90).extrude(2).mesh()
        self.assertLess(shape.sample(0, 0, 1), 0)
        self.assertGreater(shape.sample(11, 0, 1), 0, msg="outside the scaling circle")


class TestRegion2D(unittest.TestCase):
    """region2d(): BOSL2-style even-odd region data as a PyShape2D."""

    OUTER = [[0, 0], [20, 0], [20, 20], [0, 20]]
    HOLE = [[5, 5], [15, 5], [15, 15], [5, 15]]
    ISLAND = [[8, 8], [12, 8], [12, 12], [8, 12]]

    def test_ring(self):
        shape = pysolidfive.region2d([self.OUTER, self.HOLE]).extrude(2).mesh()
        self.assertLess(shape.sample(2, 10, 1), 0, msg="in the ring wall")
        self.assertGreater(shape.sample(10, 10, 1), 0, msg="inside the hole")
        self.assertAlmostEqual(shape.sample(5, 10, 1), 0, places=9, msg="on the hole boundary")
        self.assertAlmostEqual(shape.sample(0, 10, 1), 0, places=9, msg="on the outer boundary")

    def test_island_in_hole(self):
        shape = pysolidfive.region2d([self.OUTER, self.HOLE, self.ISLAND]).extrude(2).mesh()
        self.assertLess(shape.sample(2, 10, 1), 0, msg="ring wall solid")
        self.assertGreater(shape.sample(6, 10, 1), 0, msg="hole empty")
        self.assertLess(shape.sample(10, 10, 1), 0, msg="island solid again")

    def test_disjoint_outlines_union(self):
        a = [[0, 0], [5, 0], [5, 5], [0, 5]]
        b = [[10, 0], [15, 0], [15, 5], [10, 5]]
        shape = pysolidfive.region2d([a, b]).extrude(2).mesh()
        self.assertLess(shape.sample(2, 2, 1), 0)
        self.assertLess(shape.sample(12, 2, 1), 0)
        self.assertGreater(shape.sample(7, 2, 1), 0, msg="gap between islands")

    def test_single_bare_path(self):
        shape = pysolidfive.region2d(self.OUTER).extrude(2).mesh()
        self.assertLess(shape.sample(10, 10, 1), 0)


class TestUnion2D(unittest.TestCase):
    """union2d(): balanced many-way union whose SDF evaluation depth stays log2(n)."""

    def test_matches_chained_union(self):
        discs = [pysolidfive.circle2d(d=4).translate([i * 3, 0]) for i in range(5)]
        shape = pysolidfive.union2d(discs).extrude(2).mesh()
        for i in range(5):
            self.assertLess(shape.sample(i * 3, 0, 1), 0, msg=f"disc {i} centre solid")
        self.assertGreater(shape.sample(0, 5, 1), 0, msg="outside all discs")

    def test_hundreds_of_pieces_evaluates(self):
        # The regression this helper exists for: a linear `|` chain of this many pieces
        # overflows Python's recursion limit when the composed SDF lambda is evaluated.
        discs = [pysolidfive.circle2d(d=2).translate([i * 0.1, 0]) for i in range(800)]
        shape = pysolidfive.union2d(discs).extrude(2).mesh()
        self.assertLess(shape.sample(40, 0, 1), 0, msg="mid-strip solid")
        self.assertGreater(shape.sample(40, 3, 1), 0, msg="above the strip empty")

    def test_single_piece_passthrough(self):
        disc = pysolidfive.circle2d(d=4)
        self.assertIs(pysolidfive.union2d([disc]), disc)


class TestKnuckleHinge(unittest.TestCase):
    """knuckle_hinge(): the arm_angle=90 BOSL2 port. length=40, segs=5, offset=4,
    knuckle_diam=4, pin_diam=2, default anchor=BOT: knuckle axis along X at z=4 (the
    declared box puts BOT at z=0, knuckle top at z=6), arm hanging from z=0 to 4."""

    # The knuckle axis lands at z=4 (anchor BOT, declared box z in [0, 6]); the ring
    # material is between the pin hole (r=1) and the knuckle surface (r=2), so probe at
    # radial distance 1.5 (z=5.5). segs=5: seglen1 = 0.2+(40-0.8)/5 = 8.04, pitch 16.08 --
    # outer segments centered x = -16.08/0/+16.08, inner at x = +-8.04.
    PITCH = 0.2 + (40 - 4 * 0.2) / 5 + 0.2 + (40 - 4 * 0.2) / 5  # = seglen1+seglen2 = 16.08

    def test_outer_segments_and_pin_hole(self):
        shape = pysolidfive.knuckle_hinge(length=40, segs=5, offset=4, knuckle_diam=4, pin_diam=2).mesh()
        self.assertLess(shape.sample(0, 0, 5.5), 0, msg="center segment knuckle ring solid")
        self.assertGreater(shape.sample(0, 0, 4), 0, msg="pin hole empty at the knuckle center")
        self.assertLess(shape.sample(0, 0, 1), 0, msg="arm solid below the knuckle")
        self.assertGreater(shape.sample(self.PITCH / 2, 0, 5.5), 0, msg="gap between outer segments empty")

    def test_inner_fills_outer_gaps(self):
        outer = pysolidfive.knuckle_hinge(length=40, segs=5, offset=4, knuckle_diam=4, pin_diam=2).mesh()
        inner = pysolidfive.knuckle_hinge(length=40, segs=5, offset=4, knuckle_diam=4, pin_diam=2, inner=True).mesh()
        self.assertLess(inner.sample(self.PITCH / 2, 0, 5.5), 0, msg="inner segment where outer has a gap")
        self.assertGreater(inner.sample(0, 0, 5.5), 0, msg="inner empty where outer has a segment")
        self.assertGreater(outer.sample(self.PITCH / 2, 0, 5.5), 0)

    def test_clear_top_removes_front_half(self):
        # clear_top clears the profile's y>0 half-plane strip (the mating face).
        shape = pysolidfive.knuckle_hinge(length=40, segs=5, offset=4, knuckle_diam=4, pin_diam=2, clear_top=True).mesh()
        # Probe in the knuckle plane (z=4) at radial distance 1.5 -- inside the ring.
        self.assertGreater(shape.sample(0, 1.5, 4.0), 0, msg="cleared side empty")
        self.assertLess(shape.sample(0, -1.5, 4.0), 0, msg="uncleared side solid")

    def test_orient_left_lays_hinge_on_x(self):
        shape = pysolidfive.knuckle_hinge(
            length=40, segs=5, offset=4, knuckle_diam=4, pin_diam=2, spin=90, orient=list(LEFT)
        )
        # After spin+orient the length axis leaves X; just check the box moved coherently.
        extents = [shape.mx[i] - shape.mn[i] for i in range(3)]
        self.assertAlmostEqual(max(extents), 40, delta=1.0, msg="length preserved through orient")


class TestRabbitClip(unittest.TestCase):
    """rabbit_clip(): pin is a thin sprung outline, socket is the filled cavity."""

    from typing import Any

    ARGS: dict[str, Any] = dict(length=6, width=7, snap=0.4, thickness=0.8, depth=2)

    def test_pin_is_hollow_outline(self):
        pin = pysolidfive.rabbit_clip(type="pin", **self.ARGS).mesh()
        # At the waist (the [width/2-snap, scaled_len/2] path point) the ribbon spans
        # roughly x in [waist-thickness, waist]; probe the middle of the wall.
        self.assertLess(pin.sample(2.8, 0, 2.9), 0, msg="right ear wall solid")
        self.assertGreater(pin.sample(0, 0, 3.0), 0, msg="middle of the clip open (springs can flex)")
        self.assertGreater(pin.sample(3.45, 0, 2.9), 0, msg="outside the wall empty")

    def test_socket_is_filled_and_flipped(self):
        sock = pysolidfive.rabbit_clip(type="socket", **self.ARGS).mesh()
        # socket orient=DOWN flips it below z=0 and it is a solid cavity shape
        self.assertLess(sock.sample(0, 0, -3.0), 0, msg="socket interior solid")
        self.assertLess(sock.sample(3.0, 0, -3.0), 0, msg="socket edge included")
        self.assertGreater(sock.sample(0, 0, 1.0), 0, msg="nothing above the plane")

    def test_socket_base_closure_spans_full_width(self):
        # Regression: the socket outline is closed along its base by two [-x, -extra] points.
        # An earlier numpy conversion concatenated them with `list + ndarray`, which silently
        # BROADCASTS (adding the point onto every row) instead of appending -- shifting the
        # outline and losing the base strip. The strip means the band just below the base
        # plane is solid across the socket's whole width.
        sock = pysolidfive.rabbit_clip(type="socket", **self.ARGS).mesh()
        for x in (0.0, 1.5, 3.0, -3.0):
            self.assertLess(sock.sample(x, 0, -0.2), 0, msg=f"base band solid at x={x}")
        self.assertGreater(sock.sample(3.9, 0, -0.2), 0, msg="empty outside the clip width")

    def test_socket_wider_than_pin_by_clearance(self):
        pin = pysolidfive.rabbit_clip(type="pin", **self.ARGS).mesh()
        sock = pysolidfive.rabbit_clip(type="socket", **self.ARGS, orient=[0, 0, 1]).mesh()
        # With orient=UP both are upright; socket outline sits `clearance` outside the pin's.
        self.assertGreaterEqual((sock.mx[0] - sock.mn[0]) - (pin.mx[0] - pin.mn[0]), -0.30)


class TestPathToBezpath(unittest.TestCase):
    def test_bezpath_hits_input_points(self):
        path = [[0, 0], [10, 0], [10, 10]]
        bez = pysolidfive.path_to_bezpath(path, relsize=0.1)
        self.assertEqual(len(bez), 7, msg="two cubic segments")
        self.assertEqual(list(bez[0]), [0, 0])
        self.assertEqual(list(bez[3]), [10, 0])
        self.assertEqual(list(bez[6]), [10, 10])
        pts = pysolidfive.bezpath_points(bez, splinesteps=8)
        self.assertEqual(len(pts), 17)

    def test_tangents_respected(self):
        path = [[0, 0], [10, 0]]
        bez = pysolidfive.path_to_bezpath(path, tangents=[[1, 0], [1, 0]], relsize=0.1)
        # Straight segment with parallel tangents: control points stay on the line y=0.
        self.assertTrue(all(abs(p[1]) < 1e-9 for p in bez))


class TestPathSamplers(unittest.TestCase):
    def test_bezier_points_endpoints_and_midpoint(self):
        curve = [[0, 0], [0, 10], [10, 10], [10, 0]]  # symmetric cubic
        self.assertEqual(list(pysolidfive.bezier_points(curve, 0)), [0, 0])
        self.assertEqual(list(pysolidfive.bezier_points(curve, 1)), [10, 0])
        mid = pysolidfive.bezier_points(curve, 0.5)
        self.assertAlmostEqual(mid[0], 5, places=9)
        self.assertAlmostEqual(mid[1], 7.5, places=9)

    def test_bezpath_points_chains_segments(self):
        bez = [[0, 0], [0, 5], [5, 5], [5, 0], [5, -5], [10, -5], [10, 0]]  # two cubics
        pts = pysolidfive.bezpath_points(bez, splinesteps=8)
        self.assertEqual(len(pts), 17)
        self.assertEqual(list(pts[0]), [0, 0])
        self.assertEqual(list(pts[-1]), [10, 0])
        self.assertEqual(list(pts[8]), [5, 0], msg="segment joint hit exactly")

    def test_egg_path_extents(self):
        # Each arc omits its endpoint (the next arc supplies it), so the +-length/2 apexes are
        # only approached to within the arc sampling step -- assert against that tolerance.
        pts = pysolidfive.egg_path(15, 5, 4, 60)
        xs = [p[0] for p in pts]
        self.assertAlmostEqual(min(xs), -7.5, delta=0.01, msg="left end at -length/2")
        self.assertAlmostEqual(max(xs), 7.5, delta=0.01, msg="right end at +length/2")
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(max(ys), -min(ys), places=6, msg="symmetric about y=0")


class TestTeardropAndOnion(unittest.TestCase):
    def test_teardrop(self):
        r, ang = 3, 45
        shape = pysolidfive.teardrop(h=6, r=r, ang=ang, anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(r, 0, 0), 0, msg="equator")
        self.assertLess(shape.sample(0, 0, 0), 0, msg="center")
        apex = r / math.sin(math.radians(ang))
        self.assertAlmostEqual(shape.sample(0, 0, apex), 0, places=3, msg="apex")
        self.assertGreater(shape.sample(0, 0, apex + 1), 0)

    def test_teardrop_roof_plane(self):
        # A point actually on one of the roof planes (not the equator, not the apex) should
        # also read ~0 -- this is the region that had a masking-threshold bug during
        # development (roof was incorrectly masked at v=0 instead of the true tangent height
        # rad*cos(ang)), so it's worth checking explicitly rather than just the two endpoints.
        r, ang = 3, 45
        shape = pysolidfive.teardrop(h=6, r=r, ang=ang, anchor=CENTER).mesh()
        apex = r / math.sin(math.radians(ang))
        v = apex * 0.7
        u = (r - v * math.cos(math.radians(ang))) / math.sin(math.radians(ang))
        self.assertAlmostEqual(shape.sample(u, 0, v), 0, places=3)

    def test_onion(self):
        r, ang = 3, 45
        shape = pysolidfive.onion(r=r, ang=ang, anchor=CENTER).mesh()
        self.assertAlmostEqual(shape.sample(r, 0, 0), 0)
        self.assertLess(shape.sample(0, 0, 0), 0)
        apex = r / math.sin(math.radians(ang))
        self.assertAlmostEqual(shape.sample(0, 0, apex), 0, places=3)


class TestHeightfield(unittest.TestCase):
    def test_flat_heightfield(self):
        shape = pysolidfive.heightfield(lambda x, y: 5, size=[20, 20], bottom=-5, maxz=10).mesh()
        self.assertAlmostEqual(shape.sample(0, 0, 5), 0)
        self.assertLess(shape.sample(0, 0, 0), 0)
        self.assertGreater(shape.sample(0, 0, 10), 0)

    def test_varying_heightfield(self):
        shape = pysolidfive.heightfield(lambda x, y: x * 0.1, size=[20, 20], bottom=-5, maxz=10).mesh()
        self.assertAlmostEqual(shape.sample(10, 0, 1), 0)

    def test_rejects_non_callable_data(self):
        with self.assertRaises(AssertionError):
            pysolidfive.heightfield([[1, 2], [3, 4]], size=[20, 20])  # pyright: ignore[reportArgumentType]


def _sharp_box_sdf(p, b):
    q = [abs(p[i]) - b[i] for i in range(3)]
    return math.hypot(*[max(0, v) for v in q]) + min(max(q[0], q[1], q[2]), 0)


def _round_box_sdf(p, b, r):
    q = [abs(p[i]) - b[i] + r for i in range(3)]
    return math.hypot(*[max(0, v) for v in q]) + min(max(q[0], q[1], q[2]), 0) - r


if __name__ == "__main__":
    unittest.main()


class TestPolygonPathUtils(unittest.TestCase):
    """path_length/path_cut_points/path_normals/round_corners: pure-python ports of the
    bosl2 helpers the cap-box polygon machinery uses."""

    def test_path_length_and_cut_points(self):
        path = [[0, 0], [10, 0], [10, 10]]
        self.assertAlmostEqual(pysolidfive.path_length(path), 20.0)
        cuts = pysolidfive.path_cut_points(path, [5.0, 15.0])
        self.assertAlmostEqual(cuts[0][0][0], 5.0)
        self.assertAlmostEqual(cuts[0][0][1], 0.0)
        self.assertAlmostEqual(cuts[1][0][0], 10.0)
        self.assertAlmostEqual(cuts[1][0][1], 5.0)
        single = pysolidfive.path_cut_points(path, 5.0)
        self.assertAlmostEqual(single[0][0], 5.0)

    def test_path_normals_two_point_segment(self):
        # A segment heading +x: the bosl2 port's normal points to the RIGHT of travel (-y).
        n = pysolidfive.path_normals([[0, 0], [10, 0]])
        self.assertAlmostEqual(n[0][0], 0.0)
        self.assertAlmostEqual(n[0][1], -1.0)

    def test_round_corners_inserts_tangent_arcs(self):
        sq = [[0, 0], [20, 0], [20, 20], [0, 20]]
        rounded = pysolidfive.round_corners(sq, radius=2, fn=16)
        self.assertGreater(len(rounded), 8, msg="arcs inserted")
        xs = [p[0] for p in rounded]
        ys = [p[1] for p in rounded]
        self.assertAlmostEqual(min(xs), 0.0, places=9)
        self.assertAlmostEqual(max(xs), 20.0, places=9)
        # No point should sit in the sharp-corner exclusion zone (outside the fillet circle).
        for p in rounded:
            if p[0] < 2 and p[1] < 2:
                self.assertGreaterEqual(math.dist(p, [2, 2]), 2 - 1e-9)

    def test_round_corners_right_angle_tangent_points(self):
        sq = [[0, 0], [20, 0], [20, 20], [0, 20]]
        rounded = pysolidfive.round_corners(sq, radius=2, fn=16)
        self.assertTrue(any(abs(p[0] - 2) < 1e-9 and abs(p[1]) < 1e-9 for p in rounded), msg="tangent point [2,0] present")
        self.assertTrue(any(abs(p[0]) < 1e-9 and abs(p[1] - 2) < 1e-9 for p in rounded), msg="tangent point [0,2] present")
