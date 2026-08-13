# SPDX-License-Identifier: Apache-2.0
"""MagneticBoxBuilder — typed builder for magnetic-closure lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class MagneticBoxBuilder(BoxBuilder):
    """Builder for magnetic-closure lid box type."""

    box_type: ClassVar[BoxType] = BoxType.MAGNETIC
    magnet_diameter: float = 6.0
    magnet_height: float = 3.0
    magnet_count_width: int = 2
    magnet_count_length: int = 2
