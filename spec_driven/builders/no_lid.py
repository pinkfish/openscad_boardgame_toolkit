# SPDX-License-Identifier: Apache-2.0
"""NoLidBoxBuilder and PathBoxBuilder — typed builders for no-lid box types."""

from dataclasses import dataclass
from typing import ClassVar

from spec_driven.builders._base import BoxBuilder
from spec_driven.enums import BoxType


@dataclass(frozen=True)
class NoLidBoxBuilder(BoxBuilder):
    """Builder for no-lid box type (open tray)."""

    box_type: ClassVar[BoxType] = BoxType.NO_LID
