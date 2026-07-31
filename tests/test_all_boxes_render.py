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

# LibFile: tests/test_all_boxes_render.py
#    One render test per box type in the new box system: build box (+ lid where the type has
#    a separate lid) through the real PythonSCAD app and assert it produced geometry. Skips
#    when the app / patched BOSL2 dir is absent (see render_app.render_available()).

import unittest

from render_app import render_python, render_available

# name -> (import lines, constructor expression, has_separate_lid)
BOX_CASES = {
    "sliding": ("from sliding_box import SlidingBox",
                "SlidingBox(BoxSpec(size=[100, 60, 25], label='t', lid_label='T'))", True),
    "no_lid": ("from no_lid import NoLidBox",
               "NoLidBox(BoxSpec(size=[80, 50, 20], label='t', hollow=True))", False),
    "cap": ("from cap_box import CapBox",
            "CapBox(BoxSpec(size=[90, 60, 30], label='t', lid_label='T'))", True),
    "slipover": ("from slipover_box import SlipoverBox",
                 "SlipoverBox(BoxSpec(size=[90, 60, 25], label='t', lid_label='T'))", True),
    "sliding_catch": ("from sliding_catch_box import SlidingCatchBox",
                      "SlidingCatchBox(BoxSpec(size=[100, 50, 20], label='t', lid_label='T'))", True),
    "hinge": ("from hinge_box import HingeBox",
              "HingeBox(BoxSpec(size=[100, 50, 20], label='t'))", False),
    "filament_hinge": ("from filament_hinge_box import FilamentHingeBox",
                       "FilamentHingeBox(BoxSpec(size=[100, 50, 20], label='t', lid_label='T'))", True),
    "magnetic": ("from magnetic_box import MagneticBox, MakeMagneticBoxOptions",
                 "MagneticBox(BoxSpec(size=[100, 50, 20], label='t', lid_label='T', "
                 "type_options=MakeMagneticBoxOptions(magnet_diameter=6, magnet_thickness=2)))", True),
    "inset": ("from inset_box import InsetBox",
              "InsetBox(BoxSpec(size=[100, 50, 20], label='t', lid_label='T'))", True),
    "path": ("from no_lid import PathBox",
             "PathBox.regular_polygon(BoxSpec(size=[100, 100, 24], label='t', hollow=True), sides=6)", False),
    "cap_path": ("from cap_box_polygon import CapPathBox",
                 "CapPathBox.regular_polygon(BoxSpec(size=[90, 90, 25], label='t', lid_label='T'), sides=6)", True),
    "slipover_path": ("from slipover_path_box import SlipoverPathBox",
                      "SlipoverPathBox.regular_polygon(BoxSpec(size=[90, 90, 15], label='t', lid_label='T'), sides=6)", True),
    "card_library": ("from card_library import CardLibraryBox, CardLibrarySpec, CardSize, CardGroup",
                     "CardLibraryBox(CardLibrarySpec(card_size=CardSize(66, 92, 0.4), groups=[CardGroup('R', 30)]))", True),
}

_HEADER = "from base_bgtk import *\nfrom box_base import BoxSpec\n"


def _render(imports: str, ctor: str, method: str):
    return render_python(f"{_HEADER}{imports}\nbox = {ctor}\nbox.{method}().show()")


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class BoxRenderTests(unittest.TestCase):
    """Populated with test_<name>_box / test_<name>_lid methods below."""


def _bind(name, imports, ctor, has_lid):
    def test_box(self):
        r = _render(imports, ctor, "make_box")
        self.assertTrue(r.ok, f"{name} make_box failed: {r.error}")
        self.assertGreater(r.facets or 0, 0)

    setattr(BoxRenderTests, f"test_{name}_box", test_box)

    if has_lid:
        def test_lid(self):
            r = _render(imports, ctor, "make_lid")
            self.assertTrue(r.ok, f"{name} make_lid failed: {r.error}")
            self.assertGreater(r.facets or 0, 0)

        setattr(BoxRenderTests, f"test_{name}_lid", test_lid)


for _name, (_imp, _ctor, _has_lid) in BOX_CASES.items():
    _bind(_name, _imp, _ctor, _has_lid)


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class CompartmentBoxRenderTest(unittest.TestCase):
    """A tray whose interior is auto-laid-out by compartments, with a scoop, a card
    finger-hole, and an engraved second-colour label -- exercises the compartments +
    EngravedLabel path end to end (MMU on)."""

    def test_compartment_tray_with_engraved_label(self):
        body = (
            "import os; os.environ['MAKE_MMU'] = '1'\n"
            "from base_bgtk import *\n"
            "from box_base import BoxSpec\n"
            "from no_lid import NoLidBox\n"
            "from compartments import layout_compartments, Group, Compartment, Shape, Removal\n"
            "contents = layout_compartments([\n"
            "    Group([Compartment(shape=Shape.CIRCLE, d=22, depth=12, label='5', label_colour='gold', removal=Removal.SCOOP)]),\n"
            "    Group([Compartment(shape=Shape.RECT, w=60, l=40, depth=6, is_card=True, label='Deck', label_colour='red')]),\n"
            "])\n"
            "NoLidBox(BoxSpec(size=[90, 90, 20], label='tray', contents=contents)).make_box().show()\n"
        )
        r = render_python(body)
        self.assertTrue(r.ok, f"compartment tray failed: {r.error}")
        self.assertGreater(r.facets or 0, 0)

    def test_compartment_with_shape_image(self):
        # A compartment whose floor is engraved with a SHAPE image (not text) -- the
        # Compartment.label_shape / components.EngravedShape path.
        body = (
            "import os; os.environ['MAKE_MMU'] = '1'\n"
            "from base_bgtk import *\n"
            "from box_base import BoxSpec\n"
            "from no_lid import NoLidBox\n"
            "from compartments import layout_compartments, Group, Compartment, Shape, Removal\n"
            "from shapes import saw_blade2d, coin2d\n"
            "contents = layout_compartments([Group([\n"
            "    Compartment(shape=Shape.RECT, w=34, l=34, depth=4, removal=Removal.NONE,\n"
            "                label_shape=saw_blade2d(24), label_colour='steelblue'),\n"
            "    Compartment(shape=Shape.RECT, w=34, l=34, depth=4, removal=Removal.NONE,\n"
            "                label_shape=coin2d(24), label_colour='gold'),\n"
            "])], min_gap=5)\n"
            "NoLidBox(BoxSpec(size=[90, 50, 12], label='tray', contents=contents)).make_box().show()\n"
        )
        r = render_python(body)
        self.assertTrue(r.ok, f"compartment shape-image failed: {r.error}")
        self.assertGreater(r.facets or 0, 0)


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class LidShapeRenderTest(unittest.TestCase):
    """A lid decorated with a SHAPE image instead of a text label (BoxSpec.lid_shape /
    Label.shape / make_label)."""

    def test_sliding_lid_with_shape(self):
        body = (
            "import os; os.environ['MAKE_MMU'] = '1'\n"
            "from base_bgtk import *\n"
            "from box_base import BoxSpec\n"
            "from sliding_box import SlidingBox\n"
            "from labels import MakeLabelOptions\n"
            "from shapes import saw_blade2d\n"
            "SlidingBox(BoxSpec(size=[80, 60, 20], label='ls', lid_shape=saw_blade2d(45),\n"
            "                   label_options=MakeLabelOptions(label_colour='red'))).make_lid().show()\n"
        )
        r = render_python(body)
        self.assertTrue(r.ok, f"lid shape failed: {r.error}")
        self.assertGreater(r.facets or 0, 0)


if __name__ == "__main__":
    unittest.main()
