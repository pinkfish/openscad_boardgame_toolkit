# SPDX-License-Identifier: Apache-2.0
"""Compartment builder dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from spec_driven.enums import ScoopSide


@dataclass(frozen=True)
class CompartmentBuilder:
    """Configuration for a single interior compartment."""

    label: str
    """Compartment identifier."""
    size: tuple[float, float]
    """Footprint [W, L] in mm."""
    depth: float
    """Well depth in mm."""
    rounded_corners: float = 0.0
    """Corner radius in mm."""
    finger_scoop: bool = False
    """Enable finger scoop cutout."""
    scoop_side: ScoopSide = ScoopSide.FRONT
    """Which side the finger scoop is on."""
