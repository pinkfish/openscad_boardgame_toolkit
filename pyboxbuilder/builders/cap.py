# SPDX-License-Identifier: Apache-2.0
"""CapBoxBuilder — typed builder for friction-fit cap lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CapBoxBuilder(BoxBuilder):
    """Builder for cap (friction-fit) lid box type."""

    box_type: ClassVar[BoxType] = BoxType.CAP
    cap_height: float | None = None
    finger_hold_height: float | None = None
    finger_hold_len: float | None = None
    lid_wall_thickness: float | None = None
