# SPDX-License-Identifier: Apache-2.0
"""InsetBoxBuilder — typed builder for inset lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class InsetBoxBuilder(BoxBuilder):
    """Builder for inset lid box type."""

    box_type: ClassVar[BoxType] = BoxType.INSET
