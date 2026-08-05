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

import re
import unittest
from pathlib import Path

from render_app import PROJECT_ROOT, render_python, render_available

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
    # The *_outline variants: the same figures drawn as outlines rather than solids. Every
    # one of these was ported and then never built by any test.
    "sword2d_outline": "sword2d_outline(30, 10)",
    "crossbow2d_outline": "crossbow2d_outline(30, 10)",
    "sledgehammer2d_outline": "sledgehammer2d_outline(30, 10)",
    "torch2d_outline": "torch2d_outline(30, 10)",
    "shoe2d_outline": "shoe2d_outline(20)",
    "bag2d_outline": "bag2d_outline(20)",
    "saw_blade2d_outline": "saw_blade2d_outline(20)",
    # Pure-number helpers (no geometry) -- assert they return something usable.
    "australia_map_width": "float(australia_map_width(30))",
    "ruins2d_width": "float(ruins2d_width(30))",
}

#: A pair of edge profiles, the input the tesselation primitives take: each runs x = -0.5
#: .. +0.5 with y the sideways excursion.
_PROFILES = "[[[-0.5, 0], [0, 0.2], [0.5, 0]], [[-0.5, 0], [0, -0.2], [0.5, 0]]]"
_HEX_PROFILES = _PROFILES[:-1] + ", [[-0.5, 0], [0.3, 0.2], [0.5, 0]]]"

TESSELLATIONS = {
    # The tesselation PRIMITIVES -- the layout and edge-distortion machinery every figurative
    # tiling is built on (creature_tesselations.py). Ported, but nothing built them.
    "hexagonal_tesselation": f"hexagonal_tesselation(points={_HEX_PROFILES}, radius=10)",
    "square_tesselation": f"square_tesselation(points={_PROFILES}, size=[20, 20], thickness=1)",
    "tesselation_side_line": f"tesselation_side_line(path=[[0, 0], [10, 0]], side={_PROFILES}[0])",
    "tesselation_polygon": (
        f"tesselation_polygon(path=[[0, 0], [10, 0], [10, 10], [0, 10]], side_indexes=[0, 1, 0, 1],"
        f" sides={_PROFILES}, flips=[0, 0, 0, 0])"
    ),
    "hexagonal_tesselation_generate_edge": (
        f"hexagonal_tesselation_generate_edge(pts={_PROFILES}[0], side_length=10)"
    ),
    "square_tesselation_generate_edge": f"square_tesselation_generate_edge(pts={_PROFILES}[0], side_length=10)",
    # Grid layout helpers.
    "hexagon_tesselation_repeat_at_location": (
        "hexagon_tesselation_repeat_at_location(x=1, y=1, size=10, children=circle(r=3))"
    ),
    "hexagon_tesselation_repeat": "hexagon_tesselation_repeat(rows=2, cols=2, size=10, children=circle(r=3))",
    "triangle_tesselation_repeat_at_location": (
        "triangle_tesselation_repeat_at_location(x=1, y=1, size=10, children=circle(r=3))"
    ),
    "triangle_tesselation_repeat": "triangle_tesselation_repeat(rows=2, cols=2, size=10, children=circle(r=3))",
    # Leaf and deltoid internals.
    "tesselation_leaf_outline_make_polygon": "tesselation_leaf_outline_make_polygon(section_height=4.3, section=5)",
    "tesselation_leaf_outline_make_veins": (
        "tesselation_leaf_outline_make_veins(calc_thickness=0.5, section_height=4.3, section=5,"
        " calc_vein_thickness=0.25)"
    ),
    "deltoid_trihexagonal_tiling_get_points": (
        "deltoid_trihexagonal_tiling_get_points(pts=[[10, 0], [5, 8], [-5, 8], [-10, 0], [-5, -8], [5, -8]], i=0)"
    ),
    "deltoid_trihexagonal_tiling_inner_parts": (
        "deltoid_trihexagonal_tiling_inner_parts("
        "pts=[[10, 0], [5, 8], [-5, 8], [-10, 0], [-5, -8], [5, -8]], thickness=1)"
    ),
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
KNOWN_BROKEN: dict[str, str] = {}
# EMPTY -- every shape and tessellation builds. What used to be listed here:
#   * tesselation_drop / tesselation_pegasus -- `Path.to_list` is a PROPERTY that was being
#     CALLED ("'list' object is not callable"), which broke every square tesselation.
#   * tesselation_leaf_outline / _three -- did their region algebra through osuse'd BOSL2,
#     where a failing assert ABORTS THE PROCESS rather than raising
#     (tests/repro_osuse_assert_aborts.py). Rebuilt on direct 2-D CSG; tesselations.py no
#     longer calls osuse at all.

#: The 3-D polyhedra, meshed together by test_polyhedra_mesh below.
SHAPES3D = ("dodecahedron", "octahedron", "icosahedron", "tetrahedron", "trapezohedron")

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
            "from shapes3d import " + ", ".join(SHAPES3D) + "\n"
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


@unittest.skipUnless(render_available(), "PythonSCAD app / patched BOSL2 not available")
class ShapeAspectRatioTest(unittest.TestCase):
    """Shapes built with a NON-DEFAULT aspect ratio.

    Inherited from the deleted test_shape_type.py, which could only run under the numeric
    mock that died with pysolidfive. CLOUD is here by name because it shipped broken: it
    called resize() with a 2-element vector, which the real resize() rejects and the mock
    of the day accepted, so nothing caught it. Run against the real app there is no mock to
    be more permissive than the thing it stands in for."""

    def test_shapes_build_with_an_aspect_ratio(self):
        body = (
            "from base_bgtk import ShapeType\n"
            "from shape_type import MakeShapeObject, ShapeByType\n"
            "import pybosl2.shapes3d as _s3\n"
            "for _n in ('CLOUD', 'HEXAGON', 'OCTOGON', 'CIRCLE'):\n"
            "    _t = getattr(ShapeType, _n, None)\n"
            "    if _t is None:\n"
            "        continue\n"
            "    _out = ShapeByType(MakeShapeObject(shape_type=_t, shape_width=11,\n"
            "                                       shape_thickness=1, shape_aspect_ratio=1.5))\n"
            "    assert _out is not None, _n + ' produced no shape with aspect_ratio=1.5'\n"
            "_s3.cuboid([1, 1, 1]).show()\n"
        )
        r = render_python(body)
        self.assertTrue(r.ok, r.error)


class CoverageTest(unittest.TestCase):
    """Every public shape and tessellation must be BUILT by the sweeps above.

    Name parity with the .scad originals was never the problem -- both files are fully
    ported (the only .scad names with no Python counterpart are nested helper modules
    living inside their parent). The gap was COVERAGE: 23 ported public functions, including
    seven whole `*_outline` shapes and the entire tessellation primitive layer that every
    figurative tiling is built on, were never built by any test. Add a shape without adding
    it to SHAPES2D / TESSELLATIONS and this fails."""

    #: Not geometry, and nothing to build: module-level plumbing.
    EXEMPT = {"region"}

    def _public_functions(self, module: str) -> list[str]:
        src = (Path(PROJECT_ROOT) / module).read_text()
        return [
            m.group(1)
            for m in re.finditer(r"^def ([a-z][a-z0-9_]*)\(", src, re.M)
            if m.group(1) not in self.EXEMPT
        ]

    def test_every_public_shape_is_built(self):
        built = set(SHAPES2D) | set(TESSELLATIONS) | set(SHAPES3D)
        for module in ("shapes.py", "tesselations.py", "shapes3d.py"):
            with self.subTest(module=module):
                missing = sorted(set(self._public_functions(module)) - built)
                self.assertEqual(
                    [], missing,
                    f"{module}: public functions that no test builds -- add them to "
                    f"SHAPES2D / TESSELLATIONS: {missing}",
                )

    def test_known_broken_is_empty(self):
        """Every shape builds. An entry here is a bug, not a preference."""
        self.assertEqual({}, KNOWN_BROKEN, f"shapes still broken: {sorted(KNOWN_BROKEN)}")


if __name__ == "__main__":
    unittest.main()
