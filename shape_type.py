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

# LibFile: shape_type.py
#    Shape creation routing for lid patterns.
#
# FileSummary: Shapes for all sorts of things.
# FileGroup: Shapes

from __future__ import annotations
from base_bgtk import ShapeType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D  # noqa: F401
    from openscad import PyOpenSCAD  # noqa: F401
    from pybosl2._sdf.shapes2d import PyShape2D  # noqa: F401
from pybosl2 import shapes2d

import math
import os
import sys

# The figurative tilings (lizard, goose, chicken, sheep, bird, flying bird, voronoi) live in
# the tesselations/ DIRECTORY. It cannot be imported as a package -- the module
# tesselations.py shadows it -- so the directory itself goes on the path and the plain
# `from lizard import ...` imports below resolve. Without this they raise
# ModuleNotFoundError and seven ShapeTypes are unusable, which is exactly what had happened.
_TESSELATION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tesselations")
if os.path.isdir(_TESSELATION_DIR) and _TESSELATION_DIR not in sys.path:
    sys.path.append(_TESSELATION_DIR)


# BOSL2 is the only library loaded via osuse; everything else in this
# project is reached through normal Python imports. The tesselation /
# pentagon-tiling / cloud-shape modules are imported lazily inside
# ShapeByType() below since they are large sibling modules converted
# separately and this avoids an import-order dependency.

# ---------------------------------------------------------------------------
# ShapeObject — mirrors the SCAD 'object()' used by MakeShapeObject
# ---------------------------------------------------------------------------

# The layout context some shapes need is supplied by their :mod:`patterns` Pattern -- a
# tiled motif gets none, a self-placing tiling gets its cell index, an area-filling one gets
# the region size. patterns.py holds the single registry of which is which; this module just
# accepts whatever context it is given.


class ShapeObject:
    """Container for shape options used by :func:`ShapeByType`.

    Create one with :func:`MakeShapeObject` and pass it to any
    shape-generating function.
    """

    def __init__(
        self,
        shape_type: ShapeType | None = None,
        shape_width: float | None = None,
        shape_thickness: float = 2,
        rounding: float = 0,
        shape_aspect_ratio: float = 1.0,
        supershape_m1: float | None = None,
        supershape_m2: float | None = None,
        supershape_n1: float | None = None,
        supershape_n2: float | None = None,
        supershape_n3: float | None = None,
        supershape_a: float | None = None,
        supershape_b: float | None = None,
        pentagon_first_angle_modifier: float = 0,
        pentagon_second_angle_modifier: float = 0,
        pentagon_first_length_modifier: float = 0,
        pentagon_second_length_modifier: float = 0,
        pentagon_third_length_modifier: float = 0,
    ) -> None:
        self.shape_type = shape_type if shape_type is not None else ShapeType.DENSE_HEX
        self.shape_width = shape_width if shape_width is not None else 12
        self.shape_thickness = shape_thickness
        self.rounding = rounding
        self.shape_aspect_ratio = shape_aspect_ratio
        self.supershape_m1 = supershape_m1 if supershape_m1 is not None else 4
        self.supershape_m2 = supershape_m2 if supershape_m2 is not None else 4
        self.supershape_n1 = supershape_n1 if supershape_n1 is not None else 1
        self.supershape_n2 = supershape_n2 if supershape_n2 is not None else 1
        self.supershape_n3 = supershape_n3 if supershape_n3 is not None else 1
        self.supershape_a = supershape_a if supershape_a is not None else 1
        self.supershape_b = supershape_b if supershape_b is not None else 1
        self.pentagon_first_angle_modifier = pentagon_first_angle_modifier
        self.pentagon_second_angle_modifier = pentagon_second_angle_modifier
        self.pentagon_first_length_modifier = pentagon_first_length_modifier
        self.pentagon_second_length_modifier = pentagon_second_length_modifier
        self.pentagon_third_length_modifier = pentagon_third_length_modifier


def MakeShapeObject(
    shape_type: ShapeType | None = None,
    shape_width: float | None = None,
    shape_thickness: float = 2,
    rounding: float = 0,
    shape_aspect_ratio: float = 1.0,
    supershape_m1: float | None = None,
    supershape_m2: float | None = None,
    supershape_n1: float | None = None,
    supershape_n2: float | None = None,
    supershape_n3: float | None = None,
    supershape_a: float | None = None,
    supershape_b: float | None = None,
    pentagon_first_angle_modifier: float = 0,
    pentagon_second_angle_modifier: float = 0,
    pentagon_first_length_modifier: float = 0,
    pentagon_second_length_modifier: float = 0,
    pentagon_third_length_modifier: float = 0,
    _called_from_builder: bool = False,
) -> ShapeObject:
    """Create a :class:`ShapeObject` with the given parameters.

    All parameters are optional.

    Args:
        shape_type:         one of the :class:`ShapeType` enum values (default ShapeType.DENSE_HEX)
        shape_width:        width of the shape in mm (default 12)
        shape_thickness:    outline stroke thickness (default 2)
        rounding:           edge rounding (default 0)
        shape_aspect_ratio: dy scale factor (default 1.0)
        supershape_m1/m2/n1/n2/n3/a/b: Superformula parameters
        pentagon_*:         pentagon tiling modifiers
    """
    if not _called_from_builder:
        import warnings
        warnings.warn(
            "Direct call to MakeShapeObject is deprecated. Configure shapes directly on LidBuilder.",
            DeprecationWarning,
            stacklevel=2,
        )
    return ShapeObject(
        shape_type=shape_type,
        shape_width=shape_width,
        shape_thickness=shape_thickness,
        rounding=rounding,
        shape_aspect_ratio=shape_aspect_ratio,
        supershape_m1=supershape_m1,
        supershape_m2=supershape_m2,
        supershape_n1=supershape_n1,
        supershape_n2=supershape_n2,
        supershape_n3=supershape_n3,
        supershape_a=supershape_a,
        supershape_b=supershape_b,
        pentagon_first_angle_modifier=pentagon_first_angle_modifier,
        pentagon_second_angle_modifier=pentagon_second_angle_modifier,
        pentagon_first_length_modifier=pentagon_first_length_modifier,
        pentagon_second_length_modifier=pentagon_second_length_modifier,
        pentagon_third_length_modifier=pentagon_third_length_modifier,
    )


def ShapeByType(
    options: ShapeObject,
    polygon_x: int | None = None,
    polygon_y: int | None = None,
    polygon_grid_rows: int | None = None,
    polygon_grid_cols: int | None = None,
    polygon_width: float | None = None,
    polygon_length: float | None = None,
) -> "Bosl2Shape2D | PyShape2D | None":
    """Render a 2-D lid pattern shape described by *options*.

    Usage::

        ShapeByType(MakeShapeObject(shape_type=ShapeType.DENSE_HEX,
                                    shape_thickness=2, shape_width=10))

    Some shape types need layout context that the original SCAD module read from the
    $polygon_x/$polygon_y/$polygon_width/$polygon_length special variables; since Python
    has no equivalent dynamic scoping, it is passed explicitly via the polygon_x/polygon_y/
    polygon_grid_rows/polygon_grid_cols/polygon_width/polygon_length keyword arguments.
    Callers do not work out which ones a shape needs: build the shape's
    :class:`~patterns.Pattern` (:func:`~patterns.pattern_for`) and let it supply them.

    Args:
        options: :class:`ShapeObject` (from :func:`MakeShapeObject`)
    """
    assert options is not None, "Must specify options"

    t = options.shape_type
    w = options.shape_width
    th = options.shape_thickness
    rounding = options.rounding
    aspect = options.shape_aspect_ratio

    if t == ShapeType.NONE:
        return None

    if t == ShapeType.DENSE_HEX:
        return shapes2d.regular_ngon(outer_radius=w / 2 + th / 2, sides=6, rounding=rounding) - shapes2d.regular_ngon(
            outer_radius=w / 2 - th / 2, sides=6, rounding=rounding
        )

    if t == ShapeType.DENSE_TRIANGLE:
        return shapes2d.regular_ngon(outer_radius=w / 2 + th / 2, sides=3, rounding=rounding) - shapes2d.regular_ngon(
            outer_radius=w / 2 - th / 2, sides=3, rounding=rounding
        )

    if t == ShapeType.CIRCLE:
        return shapes2d.circle(radius=w / 2 + th / 4) - shapes2d.circle(radius=(w - th / 2) / 2)

    if t in (ShapeType.TRIANGLE, ShapeType.HEX, ShapeType.OCTOGON, ShapeType.SQUARE):
        shape_edges = (
            3 if t == ShapeType.TRIANGLE else (6 if t == ShapeType.HEX else (4 if t == ShapeType.SQUARE else 8))
        )
        outer_r = w / 2 + (th * 1.5 if t == ShapeType.TRIANGLE else th / 4)
        inner_r = (w - (th * 0.5 if t == ShapeType.TRIANGLE else th / 2)) / 2
        return shapes2d.regular_ngon(radius=outer_r, sides=shape_edges, rounding=rounding) - shapes2d.regular_ngon(
            radius=inner_r, sides=shape_edges, rounding=rounding
        )

    if t == ShapeType.SUPERSHAPE:
        outer = shapes2d.supershape(
            diameter=w,  # pybosl2 0.6.5 renamed supershape's d= to diameter=
            m1=options.supershape_m1,
            m2=options.supershape_m2,
            n1=options.supershape_n1,
            n2=options.supershape_n2,
            n3=options.supershape_n3,
            a=options.supershape_a,
            b=options.supershape_b,
        )
        inner = outer.offset(delta=-th)
        return outer - inner

    if t == ShapeType.CLOUD:
        from shapes import cloud_shape2d

        # resize() needs a 3-vector even for 2-D geometry (a 2-element vector raises
        # "TypeError: Invalid resize dimensions"); 0 leaves the unused Z axis alone.
        outer = cloud_shape2d(width=w).resize([w * aspect, w, 0])
        inner = cloud_shape2d(width=w).resize([w * aspect, w, 0]).offset(delta=-th)
        return (outer - inner).translate([-w / 2, -w / 2])

    if t in (
        ShapeType.PENTAGON_R1,
        ShapeType.PENTAGON_R3,
        ShapeType.PENTAGON_R4,
        ShapeType.PENTAGON_R5,
        ShapeType.PENTAGON_R6,
        ShapeType.PENTAGON_R7,
        ShapeType.PENTAGON_R8,
        ShapeType.PENTAGON_R9,
        ShapeType.PENTAGON_R10,
        ShapeType.PENTAGON_R11,
        ShapeType.PENTAGON_R12,
        ShapeType.PENTAGON_R13,
        ShapeType.PENTAGON_R14,
        ShapeType.PENTAGON_R15,
    ):
        from pentagon_tilings import pentagon_tesselation

        r_names = {
            ShapeType.PENTAGON_R1: "R1",
            ShapeType.PENTAGON_R3: "R3",
            ShapeType.PENTAGON_R4: "R4",
            ShapeType.PENTAGON_R5: "R5",
            ShapeType.PENTAGON_R6: "R6",
            ShapeType.PENTAGON_R7: "R7",
            ShapeType.PENTAGON_R8: "R8",
            ShapeType.PENTAGON_R9: "R9",
            ShapeType.PENTAGON_R10: "R10",
            ShapeType.PENTAGON_R11: "R11",
            ShapeType.PENTAGON_R12: "R12",
            ShapeType.PENTAGON_R13: "R13",
            ShapeType.PENTAGON_R14: "R14",
            ShapeType.PENTAGON_R15: "R15",
        }
        x = (math.floor(polygon_grid_rows / 2) - polygon_x) if polygon_x and polygon_grid_rows is not None else 0
        y = (math.floor(polygon_grid_cols / 2) - polygon_y) if polygon_y and polygon_grid_cols is not None else 0
        shape = pentagon_tesselation(
            pentagon_type=r_names[t],
            pentagon_size=w,
            thickness=th / 2,
            x=x,
            y=y,
            first_angle_modifier=options.pentagon_first_angle_modifier,
            second_angle_modifier=options.pentagon_second_angle_modifier,
            first_length_modifier=options.pentagon_first_length_modifier,
            second_length_modifier=options.pentagon_second_length_modifier,
            third_length_modifier=options.pentagon_third_length_modifier,
        )
        return shape

    if t == ShapeType.PENTAGON_R2:
        from pentagon_tilings import pentagon_tesselation_area

        assert polygon_width is not None and polygon_length is not None, (
            "PENTAGON_R2 needs polygon_width/length layout context"
        )

        return pentagon_tesselation_area(
            pentagon_type="R2",
            width=polygon_width,
            length=polygon_length,
            pentagon_size=w,
            thickness=th / 2,
            first_angle_modifier=options.pentagon_first_angle_modifier,
            second_angle_modifier=options.pentagon_second_angle_modifier,
            first_length_modifier=options.pentagon_first_length_modifier,
            second_length_modifier=options.pentagon_second_length_modifier,
            third_length_modifier=options.pentagon_third_length_modifier,
            spin=60,
        )

    if t == ShapeType.LIZARD:
        from lizard import LizardRepeatAtLocation

        x = (math.floor(polygon_grid_rows / 2) - polygon_x) if polygon_x and polygon_grid_rows is not None else 0
        y = (math.floor(polygon_grid_cols / 2) - polygon_y) if polygon_y and polygon_grid_cols is not None else 0
        return LizardRepeatAtLocation(size=w, thickness=th / 2, x=x, y=y, outer_offset=0.1)

    if t == ShapeType.CHICKEN:
        from chicken import TesselationChickenHex
        from kite_tesselation import TesselationHexKiteArea

        assert polygon_width is not None and polygon_length is not None, (
            "CHICKEN needs polygon_width/length layout context"
        )
        return TesselationHexKiteArea(
            size=w,
            width=polygon_width,
            length=polygon_length,
            children=TesselationChickenHex(size=w, thickness=th / 2, outer_offset=0.1).rotate([0, 0, 30]),
        )

    if t == ShapeType.GOOSE:
        from goose import TesselationGooseArea

        assert polygon_width is not None and polygon_length is not None, (
            "GOOSE needs polygon_width/length layout context"
        )
        return TesselationGooseArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.BIRD:
        from quad_tesselation import TesselationBirdArea

        assert polygon_width is not None and polygon_length is not None, (
            "BIRD needs polygon_width/length layout context"
        )
        return TesselationBirdArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.FLYING_BIRD:
        from hex_tesselation import TesselationFlyingBirdArea

        assert polygon_width is not None and polygon_length is not None, (
            "FLYING_BIRD needs polygon_width/length layout context"
        )
        return TesselationFlyingBirdArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.SHEEP:
        from pentagons import SheepTesselationArea

        assert polygon_width is not None and polygon_length is not None, (
            "SHEEP needs polygon_width/length layout context"
        )
        return SheepTesselationArea(size=w, thickness=th / 2, width=polygon_width, length=polygon_length)

    if t == ShapeType.HILBERT:
        from hilbert import hilbert_curve

        assert polygon_width is not None and polygon_length is not None, (
            "HILBERT needs polygon_width/length layout context"
        )
        # The one shape in the enum with no implementation in EITHER stack -- there is a
        # wiki image for it but no code, here or in .scad. hilbert.py is new.
        return hilbert_curve(width=polygon_width, length=polygon_length, size=w, thickness=th)

    if t == ShapeType.VORONOI:
        from voronoi import Voronoi

        assert polygon_width is not None and polygon_length is not None, (
            "VORONOI needs polygon_width/length layout context"
        )

        return Voronoi(width=polygon_width, length=polygon_length, cellsize=w, thickness=th)

    if t == ShapeType.GOOSE:
        from goose import TesselationGooseArea

        assert polygon_width is not None and polygon_length is not None, (
            "GOOSE needs polygon_width/length layout context"
        )

        return TesselationGooseArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.BIRD:
        from quad_tesselation import TesselationBirdArea

        assert polygon_width is not None and polygon_length is not None, (
            "BIRD needs polygon_width/length layout context"
        )

        return TesselationBirdArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.FLYING_BIRD:
        from hex_tesselation import TesselationFlyingBirdArea

        assert polygon_width is not None and polygon_length is not None, (
            "FLYING_BIRD needs polygon_width/length layout context"
        )

        return TesselationFlyingBirdArea(width=polygon_width, length=polygon_length, thickness=th, size=w)

    if t == ShapeType.SHEEP:
        from pentagons import SheepTesselationArea

        assert polygon_width is not None and polygon_length is not None, (
            "SHEEP needs polygon_width/length layout context"
        )

        return SheepTesselationArea(size=w, thickness=th / 2, width=polygon_width, length=polygon_length)

    if t in (ShapeType.PENROSE_TILING_5, ShapeType.PENROSE_TILING_7):
        from penrose_tiling import penrose_tiling

        assert polygon_width is not None and polygon_length is not None, (
            "PENROSE_TILING needs polygon_width/length layout context"
        )
        max_width = max(polygon_width, polygon_length)
        base = 5 if t == ShapeType.PENROSE_TILING_5 else 7
        return penrose_tiling(max_width * 1.5, divisions=math.ceil((max_width * 2 / w) / 3), base=base, thickness=th)

    if t == ShapeType.DROP:
        from tesselations import tesselation_drop

        return tesselation_drop(size=[w, w * aspect], thickness=th / 2, outer_offset=0.1)

    if t in (ShapeType.DELTOID_TRIHEXAGONAL, ShapeType.DELTOID_TRIHEXAGONAL_KITE):
        from tesselations import deltoid_trihexagonal_tiling

        return deltoid_trihexagonal_tiling(
            size=w, thickness=th / 2, outer_offset=0.1, kite=(t == ShapeType.DELTOID_TRIHEXAGONAL_KITE)
        )

    if t == ShapeType.PEGASUS:
        from tesselations import tesselation_pegasus

        return tesselation_pegasus(size=[w, w * aspect], thickness=th / 2, outer_offset=0.1)

    if t == ShapeType.HALF_REGULAR_HEXAGON:
        from tesselations import triangle_tesselation_repeat_at_location, half_regular_hexagon

        assert polygon_x is not None and polygon_y is not None, "HALF_REGULAR_HEXAGON needs polygon_x/y layout context"

        # Multiply size by three since this breaks the triangle up into three.
        return triangle_tesselation_repeat_at_location(
            size=w * 3,
            x=polygon_x,
            y=polygon_y,
            children=half_regular_hexagon(size=w * 3, thickness=th, outer_offset=0.1),
        )

    if t == ShapeType.RHOMBI_TRI_HEXAGONAL:
        from tesselations import hexagon_tesselation_repeat_at_location, rhombi_tri_hexagonal

        assert polygon_x is not None and polygon_y is not None, "RHOMBI_TRI_HEXAGONAL needs polygon_x/y layout context"

        return hexagon_tesselation_repeat_at_location(size=w / 2, x=polygon_x, y=polygon_y, children=rhombi_tri_hexagonal(w))

    if t in (ShapeType.LEAF, ShapeType.LEAF_VEINS):
        from tesselations import tesselation_leaf_outline_three

        assert polygon_x is not None and polygon_y is not None, "LEAF shapes need polygon_x/y layout context"

        sqrt_three = math.sqrt(3)
        section = w / 4
        section_height = section * sqrt_three / 2
        pos = polygon_x % 4
        offset = {0: 0, 1: section * 2, 2: section * 4}.get(pos, section * 6)
        shape = tesselation_leaf_outline_three(
            size=w + 0.1,
            thickness=th / 2,
            vein_thickness=th / 4,
            with_veins=(t == ShapeType.LEAF_VEINS),
        ).rotate((polygon_y % 2) * 180)
        return shape.translate(
            [
                polygon_x * section_height * 6 + (polygon_y % 2) * section_height * 2,
                polygon_y * section * 4 - offset,
            ]
        )

    raise ValueError(f"Invalid shape type type={t}")
