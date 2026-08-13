# SPDX-License-Identifier: Apache-2.0
"""SlipoverBoxBuilder — typed builder for slipover lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlipoverBoxBuilder(BoxBuilder):
    """Builder for slipover lid box type."""

    box_type: ClassVar[BoxType] = BoxType.SLIPOVER

    foot: float = 0.0
    """Height of the exposed base the sleeve stops against, in mm. 0 = the
    sleeve covers the whole body."""
    slip: float = 1.6
    """Thickness of the sleeve wall that wraps the body."""
