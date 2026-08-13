# SPDX-License-Identifier: Apache-2.0
"""Box protocol — abstract interface for box type implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class Interior:
    """The usable volume inside a box."""

    width: float
    length: float
    height: float
    origin_x: float = 0.0
    origin_y: float = 0.0
    origin_z: float = 0.0


class BoxProtocol(Protocol):
    """Interface that every box type implementation must satisfy.

    Simpler than the legacy BoxBaseType pipeline: no Body return type
    with hollowed/carved flags, no LidPlate contract.
    """

    def build_body(self, spec: "BoxSpec") -> "Bosl2Solid":
        """Build the box body geometry."""
        ...

    def build_lid(
        self, spec: "BoxSpec", decoration: "LidDecoration"
    ) -> "Bosl2Solid":
        """Build the lid geometry with decoration applied."""
        ...

    def interior(self, spec: "BoxSpec") -> Interior:
        """Compute the interior frame from the spec dimensions."""
        ...
