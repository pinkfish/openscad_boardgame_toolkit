# SPDX-License-Identifier: Apache-2.0
"""SlipoverBoxBuilder — typed builder for slipover lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from spec_driven.builders._base import BoxBuilder
from spec_driven.enums import BoxType


@dataclass(frozen=True)
class SlipoverBoxBuilder(BoxBuilder):
    """Builder for slipover lid box type."""

    box_type: ClassVar[BoxType] = BoxType.SLIPOVER
