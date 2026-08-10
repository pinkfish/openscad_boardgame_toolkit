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

# LibFile: tests/test_box_spec_lid.py
#    Covers how a box decides WHAT its lid looks like: BoxSpec.lid (the single lid field),
#    BoxBaseType._resolve_lid, BoxKit's lid merge, and Lid.with_label.
#
#    This is pure Python -- no app, no geometry -- so it runs in the 1.4s inner loop. That
#    matters because the five fields this replaced (lid/lid_label/lid_shape/label_options/
#    shape_options) were resolved deep inside make_lid(), which meant the only way to find
#    out whether a spec produced the lid you asked for was a real render. Resolution is now
#    a pure function of the spec, and this is where it is checked.
#
# FileSummary: Unit tests for BoxSpec.lid resolution and the BoxKit lid merge.
# FileGroup: Tests

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from box_base import BoxKit, BoxSpec, Label, Lid
from labels import MakeLabelOptions
from no_lid import NoLidBox
from shape_type import MakeShapeObject, ShapeType
from sliding_box import SlidingBox

_SIZE = [100, 60, 25]
_BLUE = MakeLabelOptions(label_colour="blue")


def _lid_of(**spec_kwargs) -> Lid:
    """The Lid a SlidingBox built from this spec would decorate with."""
    return SlidingBox(BoxSpec(size=_SIZE, label="t", **spec_kwargs))._resolve_lid(None)


class ResolveLidTests(unittest.TestCase):
    """BoxSpec.lid accepts exactly three things, and each resolves one way."""

    def test_none_gives_an_undecorated_lid(self):
        lid = _lid_of()
        self.assertIsNone(lid.label)
        self.assertIsNone(lid.pattern())

    def test_a_string_is_shorthand_for_a_text_label(self):
        lid = _lid_of(lid="Trains")
        assert lid.label is not None
        self.assertEqual(lid.label.text, "Trains")

    def test_a_lid_is_used_as_given(self):
        given = Lid(shape_options=MakeShapeObject(shape_type=ShapeType.DENSE_HEX))
        self.assertIs(_lid_of(lid=given), given)

    def test_the_shorthand_inherits_the_box_material_colour(self):
        """A str/None lid is the box speaking, so it takes the box's colour; a Lid is
        its own object and keeps the colour it was built with."""
        box = SlidingBox(BoxSpec(size=_SIZE, label="t", lid="T", material_colour="red"))
        self.assertEqual(box._resolve_lid(None).material_colour, box.material_colour)

    def test_an_explicit_lid_argument_beats_the_spec(self):
        override = Lid(label=Label("override"))
        box = SlidingBox(BoxSpec(size=_SIZE, label="t", lid="from spec"))
        self.assertIs(box._resolve_lid(override), override)

    def test_a_non_lid_non_string_is_rejected_at_construction(self):
        """Decoration options used to be spec fields; passing one now names the fix."""
        with self.assertRaises(TypeError) as caught:
            # Deliberately the wrong type -- the point of the test is the runtime guard.
            BoxSpec(size=_SIZE, label="t", lid=MakeLabelOptions(label_colour="red"))  # type: ignore[arg-type]
        self.assertIn("lid=Lid(...)", str(caught.exception))


class WithLabelTests(unittest.TestCase):
    """Lid.with_label swaps the words and nothing else."""

    def test_it_keeps_the_label_styling(self):
        lid = Lid(label=Label("", options=_BLUE)).with_label("Seals")
        assert lid.label is not None
        self.assertEqual(lid.label.text, "Seals")
        self.assertEqual(lid.label.options.label_colour, "blue")

    def test_it_keeps_the_rest_of_the_lid(self):
        lid = Lid(
            shape_options=MakeShapeObject(shape_type=ShapeType.DENSE_HEX),
            fingernail=True,
            boundary=7,
        ).with_label("Seals")
        self.assertEqual(lid.boundary, 7)
        self.assertIsNotNone(lid.pattern())
        assert lid.fingernail is not None
        self.assertTrue(lid.fingernail.enabled)

    def test_it_adds_a_label_to_a_lid_that_had_none(self):
        lid = Lid().with_label("Seals")
        assert lid.label is not None
        self.assertEqual(lid.label.text, "Seals")

    def test_it_does_not_mutate_the_original(self):
        original = Lid(label=Label("first"))
        original.with_label("second")
        assert original.label is not None
        self.assertEqual(original.label.text, "first")


class BoxKitLidMergeTests(unittest.TestCase):
    """A kit shares ONE lid style; each box supplies only its own words."""

    def test_a_string_override_merges_into_the_kits_lid(self):
        kit = BoxKit(SlidingBox, lid=Lid(label=Label("", options=_BLUE), boundary=7))
        lid = kit.spec(size=_SIZE, label="t", lid="Seals").lid
        assert isinstance(lid, Lid) and lid.label is not None
        self.assertEqual(lid.label.text, "Seals")
        # The whole point of merging rather than replacing:
        self.assertEqual(lid.label.options.label_colour, "blue")
        self.assertEqual(lid.boundary, 7)

    def test_a_lid_override_replaces_the_kits_outright(self):
        kit = BoxKit(SlidingBox, lid=Lid(label=Label("", options=_BLUE), boundary=7))
        own = Lid(label=Label("Own"), boundary=3)
        self.assertIs(kit.spec(size=_SIZE, label="t", lid=own).lid, own)

    def test_a_string_override_with_no_kit_lid_stays_a_string(self):
        kit = BoxKit(SlidingBox, wall_thickness=2)
        self.assertEqual(kit.spec(size=_SIZE, label="t", lid="Seals").lid, "Seals")

    def test_no_override_keeps_the_kits_lid(self):
        shared = Lid(label=Label("shared"))
        kit = BoxKit(SlidingBox, lid=shared)
        self.assertIs(kit.spec(size=_SIZE, label="t").lid, shared)

    def test_one_kit_lid_serves_many_boxes_independently(self):
        """The kit's Lid is frozen and with_label copies, so box N+1 does not inherit
        box N's text."""
        kit = BoxKit(SlidingBox, lid=Lid(label=Label("", options=_BLUE)))
        first = kit.spec(size=_SIZE, label="a", lid="Seals").lid
        second = kit.spec(size=_SIZE, label="b", lid="Farmer").lid
        assert isinstance(first, Lid) and isinstance(second, Lid)
        assert first.label is not None and second.label is not None
        self.assertEqual((first.label.text, second.label.text), ("Seals", "Farmer"))

    def test_a_lidless_type_rejects_a_lid_at_kit_construction(self):
        with self.assertRaises(TypeError):
            BoxKit(NoLidBox, lid="x")


class APIErgonomicsTests(unittest.TestCase):
    """Checks the dynamic option coercion, fluent builder, and simplified arguments in BoxSpec/BoxKit."""

    def test_box_spec_create_coerces_extra_kwargs(self):
        spec = BoxSpec.create(size=_SIZE, label="t", two_layer=True, inset=2.0)
        self.assertEqual(spec.size, _SIZE)
        self.assertEqual(spec.label, "t")
        self.assertEqual(spec.type_options, {"two_layer": True, "inset": 2.0})

    def test_box_spec_builder(self):
        spec = BoxSpec.builder() \
            .size(100, 60, 25) \
            .label("built-spec") \
            .wall_thickness(4.0) \
            .option("two_layer", True) \
            .build()
        self.assertEqual(spec.size, [100, 60, 25])
        self.assertEqual(spec.label, "built-spec")
        self.assertEqual(spec.wall_thickness, 4.0)
        self.assertEqual(spec.type_options, {"two_layer": True})

    def test_box_resolve_options_dict_coercion(self):
        # SlidingBox accepts SlidingBoxOptions. Check that passing a dict to SlidingBox coerces correctly.
        spec = BoxSpec.create(size=_SIZE, label="t", type_options={"two_layer": True, "extra_ignored": 42})
        box = SlidingBox(spec)
        self.assertTrue(box.options.two_layer)

    def test_box_kit_validates_and_merges_extra_options(self):
        # SlidingBox takes `two_layer`. BoxKit should allow it as an override/default.
        kit = BoxKit(SlidingBox, wall_thickness=2, two_layer=False)
        spec = kit.spec(size=_SIZE, label="t", two_layer=True)
        self.assertEqual(spec.wall_thickness, 2)
        self.assertEqual(spec.type_options, {"two_layer": True})

    def test_lid_builder(self):
        lid = Lid.builder() \
            .boundary(5) \
            .label("CustomLid") \
            .build()
        self.assertEqual(lid.boundary, 5)
        self.assertIsNotNone(lid.label)
        self.assertEqual(lid.label.text, "CustomLid")

    def test_box_builder_and_type_specific_builders(self):
        from box_base import BoxBuilder, CapBoxBuilder, SlidingBoxBuilder
        from cap_box import CapBox

        # Using BoxSpec.box_builder() generic
        box = BoxSpec.box_builder() \
            .type(CapBox) \
            .size(90, 60, 25) \
            .label("cap-via-builder") \
            .cap_height(4.0) \
            .build()
        
        self.assertIsInstance(box, CapBox)
        self.assertEqual(box.spec.size, [90, 60, 25])
        self.assertEqual(box.options.cap_height, 4.0)

        # Direct instantiation of a type-specific builder
        sliding_box = SlidingBoxBuilder() \
            .size(100, 50, 20) \
            .label("sliding-via-builder") \
            .two_layer(True) \
            .build()

        self.assertEqual(sliding_box.spec.label, "sliding-via-builder")
        self.assertTrue(sliding_box.options.two_layer)

        # Using type-specific entry points directly on BoxSpec class
        box2 = BoxSpec.cap() \
            .size(90, 60, 25) \
            .label("cap-via-direct-builder") \
            .cap_height(5.0) \
            .build()
        self.assertEqual(box2.options.cap_height, 5.0)

        # Using BoxSpec.box_builder() and then calling .cap()
        box3 = BoxSpec.box_builder() \
            .cap() \
            .size(90, 60, 25) \
            .label("cap-via-generic-chain") \
            .cap_height(6.0) \
            .build()
        self.assertEqual(box3.options.cap_height, 6.0)


if __name__ == "__main__":
    unittest.main()
