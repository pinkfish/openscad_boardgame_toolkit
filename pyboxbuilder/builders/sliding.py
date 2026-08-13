# SPDX-License-Identifier: Apache-2.0
"""SlidingBoxBuilder — typed builder for sliding lid boxes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlidingBoxBuilder(BoxBuilder):
    """Builder for sliding-lid box type."""

    box_type: ClassVar[BoxType] = BoxType.SLIDING

    two_layer: bool = False
    """Use a two-layer sliding lid."""
    two_layer_top_lid_ratio: float = 0.5
    """Ratio of top lid layer thickness to total lid thickness."""
    two_layer_vee_shape: bool = False
    """Use vee-shaped interlocking on two-layer lids."""
