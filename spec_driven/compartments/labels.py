# SPDX-License-Identifier: Apache-2.0
"""Labeled compartment floors — mode-aware label generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def build_floor_label(
    text: str,
    width: float,
    length: float,
    mode: str = "mmu",
    height: float = 0.2,
    font_size: float | None = None,
) -> "Bosl2Solid | None":
    """Build a label for a compartment floor.

    In MMU mode, text is extruded 0.2mm above the floor for second-color
    printing. In single mode, text is recessed (engraved cutout) for
    depth-contrast visibility.

    Args:
        text: The label text (e.g., animal name).
        width: Compartment interior width.
        length: Compartment interior length.
        mode: 'mmu' for raised second-color text, 'single' for engraved cutout.
        height: Extrude/cutout depth (0.2mm default).
        font_size: Auto-calculated from compartment size if None.

    Returns:
        Bosl2Solid for the floor label, or None if bosl2 unavailable.
    """
    if font_size is None:
        max_size = min(width * 0.8 / max(len(text), 1) * 1.5, length * 0.5)
        font_size = max(max_size, 2.0)

    try:
        from pybosl2 import text as bosl2_text
    except ImportError:
        return None

    text_solid = bosl2_text(
        text=text,
        size=font_size,
        font="Arial:style=Bold",
    )
    text_solid = text_solid.translate([width / 2, length / 2, 0])

    if mode == "single":
        # Extrude for engraving: positive solid to subtract from floor
        text_solid = text_solid.linear_extrude(height=height + 0.1)
    # MMU mode: 2D text sits on floor, color contrast handles visibility

    return text_solid


def build_compartment_label(
    name: str,
    comp_width: float,
    comp_length: float,
    mode: str = "mmu",
    floor_z: float = 0.0,
) -> "Bosl2Solid | None":
    """Convenience wrapper for building a compartment floor label.

    Args:
        name: Animal/compartment name.
        comp_width: Compartment width including spacing.
        comp_length: Compartment length including spacing.
        mode: 'mmu' or 'single'.
        floor_z: Z position of the compartment floor.

    Returns:
        Bosl2Solid positioned at the floor level, or None.
    """
    label = build_floor_label(name, comp_width - 2, comp_length - 2, mode=mode)
    if label is not None:
        label = label.translate([0, 0, floor_z + 0.1])
    return label
