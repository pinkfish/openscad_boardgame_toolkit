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

# LibFile: pysolidfive/__init__.py
#    A small libfive-based (F-Rep / signed-distance-function) shape library. Independent of
#    the bosl2 port (it does not import bosl2), but built on numpy: all sequence/path/point
#    data is held as numpy arrays internally (accept array-likes in, hand NDArrays out), with
#    plain-python floats produced only at the native boundaries -- frep() bounds, polygon(),
#    translate(), and the osuse() FFI all reject (or are corrupted by) raw ndarrays. The
#    small pieces
#    it needs from there (direction-vector constants, the edges= mini-language, anchor-offset
#    math) are vendored into pysolidfive/_constants.py and pysolidfive/_edges.py instead,
#    byte-for-byte identical to bosl2's own algorithm, the same way base_bgtk.py and
#    bosl2/constants.py each already carry their own independent copy of the same
#    Vec3/direction-vector idiom rather than sharing one. cuboid() builds a box with
#    per-edge-selectable rounding AND/OR chamfering -- the same `edges=`/`except_edges=`
#    mini-language as bosl2.shapes3d.cuboid() (kept compatible on purpose, so both libraries
#    accept identical edge selectors) -- but composes it as a single signed distance function
#    meshed via the builtin frep(), instead of BOSL2's hull()-of-primitive-shapes CSG
#    construction.
#
#    Every shape function here returns a PyShape (see its docstring): a thin
#    wrapper around a *symbolic* SDF (a Python callable of (x, y, z) libfive
#    trees, not yet evaluated at lv.x()/lv.y()/lv.z() or meshed), so further
#    edits -- translate, round()/chamfer() more edges, boolean combination
#    with another PyShape -- compose directly into the expression, exactly
#    (no re-meshing needed) and cheaply, the same way pylibfive.py's own
#    lv_trans()/lv_union() etc. compose coordinate trees before the one
#    final frep() call. Only .mesh() (or an attribute PyShape doesn't
#    itself define, via __getattr__) actually calls frep() and touches the
#    real PythonSCAD/libfive C extension.
#
#    Edge-rounding algorithm: when every edge is rounded by the same amount
#    (`edges="ALL"`), cuboid() uses the classic single-formula rounded-box
#    SDF (https://iquilezles.org/articles/distfunctions/, `_rounded_box_sdf()`
#    in shapes3d.py) -- the exact Minkowski sum of a box and a sphere, matching
#    bosl2.shapes3d.cuboid()'s own real minkowski() construction for that
#    same case, with a perfectly smooth/seamless spherical corner blend.
#
#    For every other case -- a subset of edges, or per-edge/per-corner
#    independent radii -- there's no single closed-form 3-D distance
#    function, so `_cuboid_edge_sdf()` falls back to a per-axis composition:
#    for each axis, build a 2-D "rounded rect with independent per-corner
#    radii" SDF (the standard generalization of Inigo Quilez's rounded-box
#    formula, https://iquilezles.org/articles/distfunctions2d/) over the
#    other two axes, intersect it (max()) with a sharp slab along this axis,
#    then intersect the three per-axis results together. Chamfering (always
#    on this per-axis path, even for `edges="ALL"` -- only rounding gets the
#    exact-formula fast path) uses the same per-axis/per-quadrant structure,
#    but each corner's candidate is `max(qu, qv, (qu+qv+c)/sqrt(2))` -- the
#    intersection of the two axis-aligned half-planes with the diagonal
#    half-plane `c` in from the sharp corner -- instead of the rounded
#    corner's hypot() formula. Each per-quadrant candidate (round or
#    chamfer) is pushed far away (and so never wins the min() that picks
#    the right quadrant) everywhere outside its own quadrant via an additive
#    penalty proportional to how far outside it is. This avoids needing any
#    true conditional/select primitive, which libfive's documented operator
#    set (min/max/abs/sqrt/trig/pow, plus +-*/%) doesn't expose -- every
#    other edge-selection technique (e.g. GLSL-style ternaries) needs one.
#
#    With `rounding=0`/`chamfer=0` (or no edges selected), every per-quadrant
#    amount is 0 and the per-axis path exactly reproduces the plain sharp-box
#    surface on, near, and inside the surface, away from a true 3-D corner --
#    verified numerically (see scratch verification during development). Two
#    known, accepted CAVEATS, both inherent to composing 3 independent
#    per-axis 2-D fields via max() rather than one true 3-D distance
#    function -- and so both scoped to the per-axis fallback path, not the
#    exact-formula `edges="ALL"` rounding case above:
#      1. Far outside a corner (beyond all three face-pairs at once), the
#         result underestimates the true Euclidean distance (e.g. an
#         8x8x8 sharp cube can read ~5 at a point where the true distance
#         is ~6.25). Sign is always correct there (verified with 5000
#         random samples, 0 mismatches), so the meshed *surface* is
#         unaffected -- only bulk-exterior distance magnitude is
#         approximate, the same tradeoff already accepted by
#         pylibfive.py's own smooth-blend operators (lv_union_smooth()
#         etc.), which aren't true distance fields either.
#      2. At a true 3-D corner where multiple *rounded* edges from
#         different axis groups meet, but not *all* edges (e.g. chamfering
#         with `edges="ALL"`, or rounding/chamfering some other multi-axis
#         subset of edges that meet at a shared corner), the resulting
#         corner is the intersection of three orthogonal rounded/chamfered
#         prisms, not a true Minkowski/spherical corner blend -- visually
#         similar and always a well-formed closed surface, but not
#         bit-identical to the classic single-formula rounded box there,
#         and (rarely -- ~2 in 3000 random samples in testing, all within a
#         fraction of a millimeter of the true surface) the sign can
#         disagree with the ideal spherical-corner shape in a thin shell
#         immediately around such a corner. Edges rounded/chamfered
#         individually, or corners where only one axis group is treated,
#         are unaffected -- this is specifically a multi-axis-group
#         corner-blending approximation, and (for rounding) only reachable
#         via chained .round() calls with different edge subsets, since a
#         single cuboid(rounding=..., edges="ALL") call now takes the
#         exact-formula path above.
#
#    Shapes covered, mirroring bosl2.shapes3d.py: cube, cuboid, octahedron,
#    wedge, sphere, spheroid, torus, cylinder, cyl (+xcyl/ycyl/zcyl), tube,
#    pie_slice, prismoid, rect_tube, interior_fillet, teardrop, onion,
#    heightfield (callable-data only), plus convex_polyhedron() (the hull of
#    a 3-D point set as a max of face half-spaces -- dice-style solids
#    without BOSL2's polyhedra.scad) and PyShape.scale(). And a 2-D layer:
#    PyShape2D (circle2d/rect2d/polygon2d/stroke2d/hull2d_discs) -- symbolic
#    2-D SDFs with boolean ops, transforms, EXACT offset()/outline() (a
#    single subtraction, no polygon-offset cleanup), extruded to a specific
#    height via .extrude()/.linear_extrude() with the same optional rim
#    roundover/flare treatments as polygon_prism(). Also two standalone cutters, mirroring
#    bosl2.masking.py/Bosl2Solid.edge_profile_asym(), for edges outside a
#    cuboid()'s own edge/corner treatment: rounding_edge_mask() (a positionable
#    circular roundover cutter, same local frame/rotate()/translate() usage
#    as bosl2.masking.rounding_edge_mask()) and polygon_extrude() (extrudes
#    an arbitrary *convex* 2-D profile, for a custom edge cut with no simple
#    closed form). And polygon_prism(): an arbitrary SIMPLE-polygon (concave
#    OK -- exact 2-D SDF, winding-number sign via atan2) extrusion with
#    BOSL2-offset_sweep-style circular end-rim treatments (os_circle
#    roundover/flare equivalents), covering the offset_sweep(path, height,
#    bottom=os_circle(..), top=os_circle(..)) construction the path-based
#    boxes (no_lid.py) are built from. NOT ported: text3d/path_text (no
#    text-rendering primitive exists in libfive's exposed operator set --
#    use bosl2.shapes3d for text), cylindrical_heightfield and array-data
#    heightfield (no closed-form "look up a grid of numbers" primitive is
#    exposed either), and ruler (a measuring/display aid with text labels,
#    not really an SDF solid-modeling primitive -- BOSL2 doesn't apply
#    rounding/chamfer to it either). Several shapes here are deliberately
#    simplified relative to their bosl2.shapes3d.py counterpart where an
#    exact SDF would need substantially more derivation for a
#    rarely-exercised feature -- each function's docstring notes exactly
#    what's dropped (e.g. prismoid() has no vertical-edge rounding,
#    teardrop()/onion() have no chamfer=/circum=/realign=).
#
# FileGroup: pysolidfive

# The implementation is split by dimensionality -- see each file's own header:
#   pysolidfive/paths.py    -- polygon SDF machinery, shared SDF utilities, path samplers
#   pysolidfive/shapes3d.py -- PyShape and every 3-D constructor/cutter
#   pysolidfive/shapes2d.py -- PyShape2D and every 2-D constructor
# Everything public is re-exported here, so `pysolidfive.cuboid(...)` etc. work unchanged.

from pysolidfive._constants import (  # noqa: F401
    BACK,
    BOT,
    BOTTOM,
    CENTER,
    CENTRE,
    CTR,
    DOWN,
    FORWARD,
    FRONT,
    FWD,
    LEFT,
    RIGHT,
    TOP,
    UP,
    Vec3,
)
from pysolidfive.paths import (  # noqa: F401
    bezier_points,
    bezpath_points,
    circle_circle_tangents,
    deriv,
    egg_path,
    line_normal,
    offset_polyline,
    path_cut_points,
    path_length,
    path_normals,
    path_tangents,
    path_to_bezpath,
    round_corners,
    supershape_path,
)
from pysolidfive.joiners import (  # noqa: F401
    knuckle_hinge,
    rabbit_clip,
)
from pysolidfive.shapes3d import (  # noqa: F401
    PyShape,
    convex_polyhedron,
    cube,
    cuboid,
    cyl,
    cylinder,
    difference,
    heightfield,
    hull,
    interior_fillet,
    intersection,
    octahedron,
    onion,
    pie_slice,
    polygon_extrude,
    polygon_prism,
    prismoid,
    rect_tube,
    rounding_edge_mask,
    sphere,
    spheroid,
    teardrop,
    torus,
    tube,
    union,
    wedge,
    xcyl,
    ycyl,
    zcyl,
)
from pysolidfive.shapes2d import (  # noqa: F401
    PyShape2D,
    circle2d,
    hull2d_discs,
    polygon2d,
    rect2d,
    region2d,
    union2d,
    stroke2d,
    supershape2d,
)

__all__ = [
    "BACK", "BOT", "BOTTOM", "CENTER", "CENTRE", "CTR", "DOWN", "FORWARD", "FRONT", "FWD",
    "LEFT", "RIGHT", "TOP", "UP", "Vec3",
    "bezier_points", "bezpath_points", "circle_circle_tangents", "deriv", "egg_path",
    "line_normal", "offset_polyline", "path_cut_points", "path_length", "path_normals",
    "path_tangents", "path_to_bezpath", "round_corners", "supershape_path",
    "knuckle_hinge", "rabbit_clip",
    "PyShape", "convex_polyhedron", "cube", "cuboid", "cyl", "cylinder", "difference",
    "heightfield", "hull", "interior_fillet", "intersection", "octahedron", "onion",
    "pie_slice", "polygon_extrude", "polygon_prism", "prismoid", "rect_tube",
    "rounding_edge_mask", "sphere", "spheroid", "teardrop", "torus", "tube", "union",
    "wedge", "xcyl", "ycyl", "zcyl",
    "PyShape2D", "circle2d", "hull2d_discs", "polygon2d", "rect2d", "region2d", "stroke2d", "supershape2d", "union2d",
]
