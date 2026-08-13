# SPDX-License-Identifier: Apache-2.0
"""FilamentHingeBoxBuilder — typed builder for living-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class FilamentHingeBoxBuilder(BoxBuilder):
    """Builder for filament (living) hinge lid box type."""

    box_type: ClassVar[BoxType] = BoxType.FILAMENT_HINGE
    hinge_gap: float = 0.4
    hinge_length: float = 4.0
