# SPDX-License-Identifier: Apache-2.0
"""Tests for compartment element packing (FR-004a / FR-004b)."""

from __future__ import annotations

import math
import unittest

from pyboxbuilder.compartments.builder import CompartmentBuilder
from pyboxbuilder.compartments.element import (
    CompartmentElement,
    elements_bounding_box,
    elements_footprint,
    elements_overlap,
    grid_pack,
    normalize_elements,
)
from pyboxbuilder.enums import ElementShape

SVG = "examples/svg/emberleaf/owl worker.svg"


class ElementValidationTests(unittest.TestCase):
    def test_svg_element_requires_a_file(self) -> None:
        with self.assertRaises(ValueError):
            CompartmentElement(size=(10, 10))

    def test_element_requires_a_size(self) -> None:
        with self.assertRaises(ValueError):
            CompartmentElement(shape=ElementShape.RECT, size=None)

    def test_parametric_element_needs_no_file(self) -> None:
        element = CompartmentElement(shape=ElementShape.CIRCLE, size=(10, 10))
        self.assertEqual(element.footprint, (10.0, 10.0))


class FootprintTests(unittest.TestCase):
    def test_unrotated_footprint_is_the_size(self) -> None:
        element = CompartmentElement(SVG, size=(23.0, 12.0))
        self.assertEqual(element.footprint, (23.0, 12.0))

    def test_ninety_degree_rotation_swaps_axes(self) -> None:
        element = CompartmentElement(SVG, size=(23.0, 12.0), rotation=90.0)
        w, l = element.footprint
        self.assertAlmostEqual(w, 12.0)
        self.assertAlmostEqual(l, 23.0)

    def test_forty_five_degree_rotation_grows_both_axes(self) -> None:
        element = CompartmentElement(SVG, size=(10.0, 10.0), rotation=45.0)
        w, l = element.footprint
        self.assertAlmostEqual(w, 10 * math.sqrt(2), places=5)
        self.assertAlmostEqual(l, 10 * math.sqrt(2), places=5)

    def test_hexagon_measures_across_the_points(self) -> None:
        """size[0] is flat-to-flat, so the other axis is wider by 1/cos(30)."""
        element = CompartmentElement(shape=ElementShape.HEXAGON, size=(38.5, 38.5))
        w, l = element.footprint
        self.assertAlmostEqual(w, 38.5 / math.cos(math.radians(30)), places=5)
        self.assertAlmostEqual(l, 38.5, places=5)

    def test_rotating_a_hexagon_thirty_degrees_swaps_its_axes(self) -> None:
        element = CompartmentElement(
            shape=ElementShape.HEXAGON, size=(38.5, 38.5), rotation=30.0
        )
        w, l = element.footprint
        self.assertAlmostEqual(w, 38.5, places=5)
        self.assertAlmostEqual(l, 38.5 / math.cos(math.radians(30)), places=5)

    def test_rotating_a_circle_changes_nothing(self) -> None:
        element = CompartmentElement(
            shape=ElementShape.CIRCLE, size=(16.5, 16.5), rotation=37.0
        )
        self.assertEqual(element.footprint, (16.5, 16.5))


class PackTests(unittest.TestCase):
    def test_grid_pack_repeats_at_the_given_pitch(self) -> None:
        proto = CompartmentElement(SVG, size=(23.0, 12.0), label="owl")
        pack = grid_pack(proto, 5, origin=(0.5, 2.0), pitch=(0.0, 12.0))

        self.assertEqual(len(pack), 5)
        self.assertEqual([e.offset for e in pack], [
            (0.5, 2.0), (0.5, 14.0), (0.5, 26.0), (0.5, 38.0), (0.5, 50.0),
        ])
        self.assertEqual([e.label for e in pack], [f"owl_{i}" for i in range(5)])

    def test_alternate_rotation_flips_every_other_copy(self) -> None:
        proto = CompartmentElement(SVG, size=(23.0, 14.0))
        pack = grid_pack(proto, 4, pitch=(0.0, 12.0), alternate_rotation=180.0)
        self.assertEqual([e.rotation for e in pack], [0.0, 180.0, 0.0, 180.0])

    def test_footprint_spans_from_the_compartment_corner(self) -> None:
        """The pack's footprint keeps authored offsets rather than shrink-wrapping."""
        pack = (
            CompartmentElement(SVG, offset=(10.0, 5.0), size=(20.0, 10.0)),
            CompartmentElement(SVG, offset=(40.0, 5.0), size=(20.0, 10.0)),
        )
        self.assertEqual(elements_footprint(pack), (60.0, 15.0))

    def test_footprint_adds_the_margin(self) -> None:
        pack = (CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 10.0)),)
        self.assertEqual(elements_footprint(pack, margin=2.5), (22.5, 12.5))

    def test_empty_pack_has_no_footprint(self) -> None:
        self.assertEqual(elements_footprint(()), (0.0, 0.0))
        self.assertEqual(elements_bounding_box(()), (0.0, 0.0, 0.0, 0.0))

    def test_normalize_shrink_wraps_to_the_origin(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(10.0, 5.0), size=(20.0, 10.0)),
            CompartmentElement(SVG, offset=(40.0, 5.0), size=(20.0, 10.0)),
        )
        normalized = normalize_elements(pack, margin=1.0)
        self.assertEqual(normalized[0].offset, (1.0, 1.0))
        self.assertEqual(elements_footprint(normalized), (51.0, 11.0))

    def test_overlap_reports_intersecting_pairs(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 20.0), label="a"),
            CompartmentElement(SVG, offset=(10.0, 10.0), size=(20.0, 20.0), label="b"),
            CompartmentElement(SVG, offset=(50.0, 0.0), size=(20.0, 20.0), label="c"),
        )
        self.assertEqual(elements_overlap(pack), [("a", "b")])

    def test_tolerance_forgives_a_graze(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 20.0), label="a"),
            CompartmentElement(SVG, offset=(19.5, 0.0), size=(20.0, 20.0), label="b"),
        )
        self.assertEqual(elements_overlap(pack), [("a", "b")])
        self.assertEqual(elements_overlap(pack, tolerance=1.0), [])


class ElementPackCompartmentTests(unittest.TestCase):
    """A compartment carrying elements sizes itself from the pack (FR-004b)."""

    def test_compartment_derives_its_size_from_its_elements(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            depth=9.0,
            elements=(
                CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),
                CompartmentElement(SVG, offset=(24.0, 0.0), size=(23.0, 12.0)),
            ),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (47.0, 12.0))

    def test_element_margin_pads_the_derived_size(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            depth=9.0,
            element_margin=1.5,
            elements=(CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (24.5, 13.5))

    def test_explicit_size_wins_over_the_pack(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            size=(85.0, 75.0),
            depth=9.0,
            elements=(CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (85.0, 75.0))

    def test_a_compartment_still_needs_some_way_to_be_sized(self) -> None:
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="Nothing", depth=9.0)


if __name__ == "__main__":
    unittest.main()
