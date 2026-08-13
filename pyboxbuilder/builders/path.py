# SPDX-License-Identifier: Apache-2.0
"""PathBoxBuilder — typed builder for the lidless polygon-path box type."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class PathBoxBuilder(BoxBuilder):
    """Builder for the path box type — an open tray with a polygon footprint.

    Used for spacers and trays that have to fill a non-rectangular leftover
    region (FR-018). Like the no-lid type, it produces a body file only.
    """

    box_type: ClassVar[BoxType] = BoxType.PATH

    path: tuple[tuple[float, float], ...] = ()
    """Closed 2D outline of the tray footprint, in mm, in the box's own frame.
    Empty falls back to the rectangle implied by `size`."""
    hollow: bool = True
    """False produces a solid block instead of a walled tray."""
