# SPDX-License-Identifier: Apache-2.0
"""Public enums for the spec-driven box library."""

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
    CARD_LIBRARY = "card_library"


class LabelMode(Enum):
    """Label decoration style."""

    FRAMED = "framed"
    FRAMELESS = "frameless"


class PatternType(Enum):
    """Lid through-hole pattern type."""

    HEX_GRID = "hex_grid"
    GRID = "grid"
    VORONOI = "voronoi"


class ScoopSide(Enum):
    """Finger scoop placement side."""

    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
