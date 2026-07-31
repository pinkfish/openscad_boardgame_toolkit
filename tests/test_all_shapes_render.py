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

# LibFile: tests/test_all_shapes_render.py
#    Build/render tests for the shape + tessellation libraries through the real PythonSCAD
#    app. The 3-D polyhedra are meshed (they .to_csg() on build -- this also proves the
#    shapes3d.py pysolidfive->pybosl2._sdf migration); the 2-D shapes + tessellations are
#    CONSTRUCTED (symbolic, fast) in one app run with a per-shape try/except so a break
#    names the offending shape. penrose_tiling + importing pentagon_tilings prove their
#    _sdf migration. Skips without the app.
#
#    KNOWN_BROKEN documents shapes with PRE-EXISTING (not-_sdf) breakage that a separate
#    shapes.py/tesselations.py bosl2 migration must fix; they are excluded from the build
#    assertion and listed by the (skipped) test_known_broken_documented catalogue.

import unittest

from render_app import render_python, render_available

# name -> call expression (all build symbolically, no meshing).
SHAPES2D = {
    "coin2d": "coin2d(20)", "coin_pile2d": "coin_pile2d(20)", "shoe2d": "shoe2d(20)",
    "bag2d": "bag2d(20)", "ruins2d": "ruins2d(20)", "saw_blade2d": "saw_blade2d(20)",
    "handshake2d": "handshake2d(20)", "fist2d": "fist2d(20)", "fist2d_outline": "fist2d_outline(20, 1)",
    "leaf2d": "leaf2d(20)", "laurel_wreath2d": "laurel_wreath2d(20)", "anvil2d": "anvil2d(20)",
    "single_log2d": "single_log2d(20)", "tower2d": "tower2d(20)", "sign2d": "sign2d(20)",
    "cloud_shape2d": "cloud_shape2d(20)", "rock_wall2d": "rock_wall2d(20)", "sword2d": "sword2d(30, 10)",
    "crossbow2d": "crossbow2d(30, 10)", "sledgehammer2d": "sledgehammer2d(30, 10)",
    "torch2d": "torch2d(30, 10)", "teapot2d": "teapot2d(30, 10)", "rock2d": "rock2d(30, 10)",
    "d20_outline2d": "d20_outline2d(20, 1)", "half_eye2d": "half_eye2d(30)", "side_eye2d": "side_eye2d(30)",
    "australia_map2d": "australia_map2d(30)", "train_outline": "train_outline(20)",
    "wagon_outline": "wagon_outline(20)", "portugal_castle": "portugal_castle(1, 20)",
}

TESSELLATIONS = {
    "tesselation_drop": "tesselation_drop([20, 20])",
    "tesselation_leaf": "tesselation_leaf(15)",
    "tesselation_leaf_outline": "tesselation_leaf_outline(15)",
    "tesselation_leaf_outline_three": "tesselation_leaf_outline_three(15)",
    "deltoid_trihexagonal_tiling": "deltoid_trihexagonal_tiling(16)",
    "half_regular_hexagon": "half_regular_hexagon(20)",
    "rhombi_tri_hexagonal": "rhombi_tri_hexagonal(18)",
    "tesselation_pegasus": "tesselation_pegasus([20, 20])",
    "penrose_tiling": "penrose_tiling(60, divisions=3, thickness=1.5)",
}

# Pre-existing breakage (NOT the _sdf migration) -- a later shapes.py/tesselations.py bosl2
# migration must fix these. Excluded from the build assertion; catalogued below.
KNOWN_BROKEN = {
    "single_log2d": "native circle() mixed with pybosl2 shapes2d in a boolean (needs bosl2 migration)",
    "crossbow2d": "native circle()/pybosl2 operator mixing (needs bosl2 migration)",
    "teapot2d": "native circle()/pybosl2 operator mixing (needs bosl2 migration)",
    "half_eye2d": "native circle()/pybosl2 operator mixing (needs bosl2 migration)",
    "tesselation_drop": "old Path API (.reversed_path) not on the pybosl2 numpy Path",
    "tesselation_pegasus": "old Path API (.rot/.move/reverse) not on the pybosl2 numpy Path",
    "tesselation_leaf_outline": "native BOSL2 region difference aborts under osuse",
    "tesselation_leaf_outline_three": "native BOSL2 region difference aborts under osuse",
}

_MARKER = "import pybosl2.shapes3d as _s3\n_s3.cuboid([1, 1, 1]).show()\n"


def _construct(imports: str, cases: dict) -> str:
    calls = "".join(
        f"try:\n    {expr}\nexcept Exception as _e:\n    _fails.append('{name}: ' + repr(_e))\n"
        for name, expr in cases.items() if name not in KNOWN_BROKEN
    )
    return (
        "from base_bgtk import *\n" + imports + "\n_fails = []\n" + calls
        + "if _fails:\n    raise RuntimeError('SHAPE FAILURES -> ' + ' ;; '.join(_fails))\n" + _MARKER
    )


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class Shapes3dRenderTest(unittest.TestCase):
    def test_polyhedra_mesh(self):
        body = (
            "from base_bgtk import *\n"
            "from shapes3d import dodecahedron, octahedron, icosahedron, tetrahedron, trapezohedron\n"
            "(dodecahedron(18) | octahedron(14).translate([28,0,0]) | icosahedron(14).translate([54,0,0]) "
            "| tetrahedron(14).translate([80,0,0]) | trapezohedron(14).translate([106,0,0])).show()\n"
        )
        r = render_python(body, timeout=600)
        self.assertTrue(r.ok, f"shapes3d polyhedra failed: {r.error}")
        self.assertGreater(r.facets or 0, 0)


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class Shapes2dConstructTest(unittest.TestCase):
    def test_working_2d_shapes_build(self):
        used = [k for k in SHAPES2D if k not in KNOWN_BROKEN]
        r = render_python(_construct("from shapes import (" + ", ".join(used) + ")", SHAPES2D))
        self.assertTrue(r.ok, r.error)
        self.assertGreater(r.facets or 0, 0)


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class TessellationConstructTest(unittest.TestCase):
    def test_working_tessellations_build(self):
        used = [k for k in TESSELLATIONS if k not in KNOWN_BROKEN and k != "penrose_tiling"]
        imports = (
            "from tesselations import (" + ", ".join(used) + ")\n"
            "from penrose_tiling import penrose_tiling\n"
            "import pentagon_tilings  # import-only: proves the _sdf migration loads"
        )
        r = render_python(_construct(imports, TESSELLATIONS), timeout=600)
        self.assertTrue(r.ok, r.error)
        self.assertGreater(r.facets or 0, 0)


class KnownBrokenCatalogue(unittest.TestCase):
    @unittest.skip("catalogue of pre-existing shape breakage (needs shapes/tesselations bosl2 migration)")
    def test_known_broken_documented(self):
        pass  # KNOWN_BROKEN above lists each broken shape + reason.


if __name__ == "__main__":
    unittest.main()
