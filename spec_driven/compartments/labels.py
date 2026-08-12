# SPDX-License-Identifier: Apache-2.0
"""Labeled compartment floors — extruded text per compartment."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosl2 import Bosl2Solid


def build_floor_label(
    text: str,
    width: float,
    length: float,
    height: float = 0.2,
    font_size: float | None = None,
) -> "Bosl2Solid":
    """Build a raised text label for a compartment floor.

    The text is extruded 0.2mm above the floor surface so it prints
    in a contrasting color (MMU) as a readable compartment label.

    Args:
        text: The label text (e.g., animal name).
        width: Compartment interior width.
        length: Compartment interior length.
        height: Extrude height (0.2mm default for single-layer MMU).
        font_size: Auto-calculated from compartment size if None.

    Returns:
        Bosl2Solid for the floor label, or None if bosl2 unavailable.
    """
    if font_size is None:
        # Auto-size: fit text within 80% of compartment width
        max_size = min(width * 0.8 / max(len(text), 1) * 1.5, length * 0.5)
        font_size = max(max_size, 2.0)  # minimum readable

    try:
        from bosl2 import text as bosl2_text
    except ImportError:
        return None

    text_solid = bosl2_text(
        text=text,
        size=font_size,
        font="Arial:style=Bold",
    )
    # Center in compartment footprint
    text_solid = text_solid.translate([
        width / 2,
        length / 2,
        0,
    ])

    # Thin extrusion for single-layer MMU printing
    from bosl2 import cuboid
    base = cuboid([width, length, height])
    base = base.translate([width / 2, length / 2, 0])
    # Return just the text (it sits on the floor; MMU colors handle contrast)
    return text_solid


def build_compartment_label(
    name: str,
    comp_width: float,
    comp_length: float,
    floor_z: float = 0.0,
) -> "Bosl2Solid | None":
    """Convenience wrapper for building a compartment floor label.

    Args:
        name: Animal/compartment name.
        comp_width: Compartment width including spacing.
        comp_length: Compartment length including spacing.
        floor_z: Z position of the compartment floor.

    Returns:
        Bosl2Solid positioned at the floor level.
    """
    label = build_floor_label(name, comp_width - 2, comp_length - 2)
    if label is not None:
        label = label.translate([0, 0, floor_z + 0.1])
    return label
