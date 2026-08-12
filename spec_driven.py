# SPDX-License-Identifier: Apache-2.0
"""Single-import entry point for the spec-driven board game box library.

Usage:
    from spec_driven import Project, BoxType, LabelMode, Color, LidBuilder

This is the ONLY import users need.
"""

from spec_driven.project import Project
from spec_driven.enums import BoxType, LabelMode, PatternType, ScoopSide
from spec_driven.color import Color
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
