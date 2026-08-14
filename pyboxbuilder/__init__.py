# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — pyboxbuilder box library."""

from pybosl2 import Color

from pyboxbuilder.enums import (
    BoxType, ElementShape, LabelMode, MagnetType, PatternType, ScoopSide, StackableMode,
)
from pyboxbuilder.project import Project
from pyboxbuilder.compartments.element import CompartmentElement, grid_pack
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.export.result import ExportResult
from pyboxbuilder.layout import columns, rows, stack

__all__ = ["Project", "BoxType", "LabelMode", "PatternType", "ScoopSide",
           "MagnetType", "StackableMode",
           "ElementShape", "Color", "CompartmentElement", "grid_pack",
           "LidBuilder", "PatternBuilder", "ExportResult",
           "columns", "rows", "stack"]
