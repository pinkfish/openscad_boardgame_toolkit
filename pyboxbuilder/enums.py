# SPDX-License-Identifier: Apache-2.0
"""Public enums for the pyboxbuilder box library."""

from enum import Enum


class BoxType(Enum):
    """Box lid mechanism type."""

    SLIDING = "sliding"
    CAP = "cap"
    HINGE = "hinge"
    FILAMENT_HINGE = "filament_hinge"
    MAGNETIC = "magnetic"
    INSET = "inset"
    SLIDING_CATCH = "sliding_catch"
    SLIPOVER = "slipover"
    SLIPOVER_PATH = "slipover_path"
    CAP_PATH = "cap_path"
    NO_LID = "no_lid"
    PATH = "path"
    CARD_LIBRARY = "card_library"


class LabelMode(Enum):
    """Label decoration style."""

    FRAMED = "framed"
    FRAMELESS = "frameless"


class PatternType(Enum):
    """Lid through-hole pattern type — full catalog ported from ShapeType."""

    # Dense/lattice shapes
    DENSE_HEX = "dense_hex"
    DENSE_TRIANGLE = "dense_triangle"
    CIRCLE = "circle"
    HEX = "hex"
    OCTOGON = "octogon"
    TRIANGLE = "triangle"
    NONE = "none"
    SQUARE = "square"
    SUPERSHAPE = "supershape"
    HILBERT = "hilbert"
    CLOUD = "cloud"

    # Pentagon tilings
    PENTAGON_R1 = "pentagon_r1"
    PENTAGON_R2 = "pentagon_r2"
    PENTAGON_R3 = "pentagon_r3"
    PENTAGON_R4 = "pentagon_r4"
    PENTAGON_R5 = "pentagon_r5"
    PENTAGON_R6 = "pentagon_r6"
    PENTAGON_R7 = "pentagon_r7"
    PENTAGON_R8 = "pentagon_r8"
    PENTAGON_R9 = "pentagon_r9"
    PENTAGON_R10 = "pentagon_r10"
    PENTAGON_R11 = "pentagon_r11"
    PENTAGON_R12 = "pentagon_r12"
    PENTAGON_R13 = "pentagon_r13"
    PENTAGON_R14 = "pentagon_r14"
    PENTAGON_R15 = "pentagon_r15"

    # Tessellations
    LIZARD = "lizard"
    VORONOI = "voronoi"
    LEAF = "leaf"
    LEAF_VEINS = "leaf_veins"
    DROP = "drop"
    DELTOID_TRIHEXAGONAL = "deltoid_trihexagonal"
    DELTOID_TRIHEXAGONAL_KITE = "deltoid_trihexagonal_kite"
    HALF_REGULAR_HEXAGON = "half_regular_hexagon"
    RHOMBI_TRI_HEXAGONAL = "rhombi_tri_hexagonal"
    PENROSE_TILING_5 = "penrose_tiling_5"
    PENROSE_TILING_7 = "penrose_tiling_7"
    PEGASUS = "pegasus"
    GOOSE = "goose"
    CHICKEN = "chicken"
    SHEEP = "sheep"
    BIRD = "bird"
    HEX_TESSELATION = "hex_tesselation"
    KITE_TESSELATION = "kite_tesselation"
    QUAD_TESSELATION = "quad_tesselation"

    # Legacy aliases (kept for backward compatibility with distinct values)
    HEX_GRID = "hex_grid"
    GRID = "grid"


class ScoopSide(Enum):
    """Finger scoop placement side."""

    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"


class ElementShape(Enum):
    """Silhouette kind for a `CompartmentElement` (FR-004a/FR-004b).

    SVG elements take their outline from `shape_file`; the rest are
    parametric and need only the element's bounding size.
    """

    SVG = "svg"
    RECT = "rect"
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"
    HEXAGON = "hexagon"
    SPHERE_SCOOP = "sphere_scoop"
