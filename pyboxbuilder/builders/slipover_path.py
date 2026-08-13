# SPDX-License-Identifier: Apache-2.0
"""SlipoverPathBoxBuilder — typed builder for slipover path lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlipoverPathBoxBuilder(BoxBuilder):
    """Builder for slipover-path lid box type."""

    box_type: ClassVar[BoxType] = BoxType.SLIPOVER_PATH
