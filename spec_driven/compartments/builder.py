# SPDX-License-Identifier: Apache-2.0
"""Compartment builder dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from spec_driven.enums import ScoopSide


@dataclass(frozen=True)
class CompartmentBuilder:
    """Configuration for a single interior compartment.

    Size can be specified as absolute millimetres (size=) or as
    ratios of the box interior (width_ratio=, length_ratio=). Ratios
    must be in range (0.0, 1.0]. At least one sizing mode is required.
    """

    label: str
    """Compartment identifier."""
    size: tuple[float, float] | None = None
    """Footprint [W, L] in mm. Required if width_ratio/length_ratio not set."""
    width_ratio: float | None = None
    """Fraction of box interior width (0.0 < ratio <= 1.0)."""
    length_ratio: float | None = None
    """Fraction of box interior length (0.0 < ratio <= 1.0)."""
    depth: float | None = None
    """Well depth in mm."""
    rounded_corners: float = 0.0
    """Corner radius in mm."""
    finger_scoop: bool = False
    """Enable finger scoop cutout."""
    scoop_side: ScoopSide = ScoopSide.FRONT
    """Which side the finger scoop is on."""
    no_rotate: bool = False
    """Prevent the layout algorithm from rotating this compartment (e.g. directional card slots)."""

    def __post_init__(self) -> None:
        if self.size is None and self.width_ratio is None and self.length_ratio is None:
            raise ValueError(
                f"Compartment '{self.label}' must specify either "
                f"size=(w, l) or width_ratio/length_ratio."
            )
        for name, val in [("width_ratio", self.width_ratio), ("length_ratio", self.length_ratio)]:
            if val is not None and not (0.0 < val <= 1.0):
                raise ValueError(
                    f"Compartment '{self.label}' {name}={val} "
                    f"must be in range (0.0, 1.0]."
                )

    def resolve_size(self, interior_w: float, interior_l: float) -> tuple[float, float]:
        """Resolve absolute size from ratios and/or absolute dimensions.

        Args:
            interior_w: Box interior width in mm.
            interior_l: Box interior length in mm.

        Returns:
            (width, length) in mm.
        """
        if self.size is not None:
            w, l = self.size
        else:
            w = interior_w
            l = interior_l

        if self.width_ratio is not None:
            w = interior_w * self.width_ratio
        if self.length_ratio is not None:
            l = interior_l * self.length_ratio

        return (round(w, 1), round(l, 1))
