# SPDX-License-Identifier: Apache-2.0
"""Interior computation and hollowing utilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Interior:
    """The usable volume inside a box."""

    width: float
    length: float
    height: float
    origin_x: float = 0.0
    origin_y: float = 0.0
    origin_z: float = 0.0

    @property
    def max_x(self) -> float:
        return self.origin_x + self.width

    @property
    def max_y(self) -> float:
        return self.origin_y + self.length

    @property
    def max_z(self) -> float:
        return self.origin_z + self.height

    def contains_compartment(self, comp_w: float, comp_l: float) -> bool:
        """Check whether a compartment footprint fits in the interior."""
        return comp_w <= self.width and comp_l <= self.length
