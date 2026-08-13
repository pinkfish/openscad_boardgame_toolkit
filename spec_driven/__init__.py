# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — spec-driven box library."""

from pybosl2 import Color

from spec_driven.enums import BoxType, ElementShape, LabelMode, PatternType, ScoopSide
from spec_driven.project import Project
from spec_driven.compartments.element import CompartmentElement, grid_pack
from spec_driven.lid.builder import LidBuilder, PatternBuilder
from spec_driven.export.result import ExportResult

__all__ = ["Project", "BoxType", "LabelMode", "PatternType", "ScoopSide",
           "ElementShape", "Color", "CompartmentElement", "grid_pack",
           "LidBuilder", "PatternBuilder", "ExportResult"]
