# SPDX-License-Identifier: Apache-2.0
"""CardLibraryBoxBuilder — typed builder for card-library box type."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CardLibraryBoxBuilder(BoxBuilder):
    """Builder for card-library box type."""

    box_type: ClassVar[BoxType] = BoxType.CARD_LIBRARY
