# SPDX-License-Identifier: Apache-2.0
"""CapPathBoxBuilder — typed builder for cap-path lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CapPathBoxBuilder(BoxBuilder):
    """Builder for cap-path lid box type."""

    box_type: ClassVar[BoxType] = BoxType.CAP_PATH
