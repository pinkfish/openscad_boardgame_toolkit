# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — spec-driven box library.

Single-import strictly-typed API for board game insert design.
"""

from spec_driven.enums import BoxType, LabelMode, PatternType, ScoopSide
from spec_driven.color import Color
from spec_driven.project import Project
from spec_driven.lid.builder import LidBuilder, PatternBuilder
from spec_driven.export.result import ExportResult

__all__ = [
    "Project",
    "BoxType",
    "LabelMode",
    "PatternType",
    "ScoopSide",
    "Color",
    "LidBuilder",
    "PatternBuilder",
    "ExportResult",
]
