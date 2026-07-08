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
