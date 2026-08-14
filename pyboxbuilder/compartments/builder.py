# SPDX-License-Identifier: Apache-2.0
"""Compartment builder dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.compartments.element import CompartmentElement



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
    holds_pieces: bool = False
    """Whether this well holds loose pieces that have to be picked out.

    Off by default, which means **square corners and a square floor**. Rounding
    is opt-in rather than opt-out because most wells are shaped by what they
    hold — a card slot, a token silhouette, a board recess — and softening
    those changes a fit rather than improving it. Setting this marks the well
    as a tray: its corners and floor round to ``depth × 2/3`` so a finger can
    sweep a piece up the curve and out (FR-044f).
    """
    """Corner radius in mm."""
    finger_scoop: bool = False
    """Enable finger scoop cutout."""
    scoop_side: ScoopSide | None = None
    """Which wall the finger scoop pierces.

    ``None`` puts it in the **shorter** wall, which is where a card stack is
    lifted out from — see `carve.default_scoop_side`.
    """
    """Which side the finger scoop is on."""
    no_rotate: bool = False
    """Prevent the layout algorithm from rotating this compartment (e.g. directional card slots)."""
    shape_file: str | None = None
    """Path to an SVG file defining the custom shape of the compartment cutout."""
    position: tuple[float, float] | None = None
    """Manual coordinate override (x, y) in mm within the interior frame."""
    elements: tuple[CompartmentElement, ...] = ()
    """Physical game components nested inside this compartment (FR-004b).

    A compartment carrying elements is an *element pack*: the elements are laid
    out in the compartment's local frame and the pack's bounding box is what the
    box-level layout engine sees, so it packs like any other rectangle."""
    element_margin: float = 0.0
    """Clearance added around an element pack's bounding box when `size` is
    derived from the elements."""

    def __post_init__(self) -> None:
        if (
            self.size is None
            and self.width_ratio is None
            and self.length_ratio is None
            and not self.elements
        ):
            raise ValueError(
                f"Compartment '{self.label}' must specify either "
                f"size=(w, l), width_ratio/length_ratio, or elements=(...)."
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
        elif self.elements:
            # Element pack: the bounding box of the pack IS the compartment (FR-004b).
            from pyboxbuilder.compartments.element import elements_footprint

            w, l = elements_footprint(self.elements, margin=self.element_margin)
        else:
            w = interior_w
            l = interior_l

        if self.width_ratio is not None:
            w = interior_w * self.width_ratio
        if self.length_ratio is not None:
            l = interior_l * self.length_ratio

        return (round(w, 1), round(l, 1))
