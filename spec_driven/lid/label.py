# SPDX-License-Identifier: Apache-2.0
"""Label generation — framed, frameless, and diagonal text."""

from __future__ import annotations

from typing import TYPE_CHECKING

from spec_driven.enums import LabelMode

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def build_label(
    width: float,
    length: float,
    thickness: float,
    text: str,
    label_mode: LabelMode = LabelMode.FRAMED,
    diagonal: bool = False,
    min_text_height_mm: float = 4.0,
    border_margin_mm: float = 5.0,
) -> "Bosl2Solid | None":
    """Build a label decoration solid for a lid.

    Returns None if the label text would be below the minimum size threshold.

    Args:
        width: Lid interior width in mm.
        length: Lid interior length in mm.
        thickness: Lid thickness in mm.
        text: The label text string.
        label_mode: Framed or frameless.
        diagonal: Corner-to-corner text orientation.
        min_text_height_mm: Skip label if computed text height < this.
        border_margin_mm: Margin from lid edges for label placement.

    Returns:
        A Bosl2Solid for the label, or None if skipped.
    """
    label_w = width - 2 * border_margin_mm
    label_l = length - 2 * border_margin_mm

    if label_w <= 0 or label_l <= 0:
        return None

    # Approximate text height from character count and available width
    char_count = len(text)
    if char_count == 0:
        return None

    text_h = min(label_w / max(char_count, 1) * 1.5, label_l * 0.9)
    if text_h < min_text_height_mm:
        return None

    try:
        from pybosl2 import cuboid, text as bosl2_text
    except ImportError:
        raise

    # Build the label geometry
    text_solid = bosl2_text(
        text=text,
        size=text_h,
        font="Arial:style=Bold",
    )

    if diagonal:
        # Rotate to corner-to-corner angle
        import math
        angle = math.degrees(math.atan2(length, width))
        text_solid = text_solid.rotate([0, 0, angle])

    # Center on lid
    text_solid = text_solid.translate([
        width / 2, length / 2, 0,
    ])

    if label_mode == LabelMode.FRAMED:
        # Add rectangular frame + diagonal hatching + outer border
        frame_margin = 2.0
        frame = cuboid([
            label_w + frame_margin * 2,
            label_l + frame_margin * 2,
            0.4,  # thin frame layer for color accent
        ])
        frame = frame.translate([
            border_margin_mm - frame_margin,
            border_margin_mm - frame_margin,
            0,
        ])

        # Diagonal hatching behind text for bed adhesion
        hatching = _build_hatching(label_w, label_l, spacing=3.0)
        hatching = hatching.translate([border_margin_mm, border_margin_mm, 0])

        text_solid = text_solid.translate([0, 0, 0.4])
        label = cuboid([label_w, label_l, 0.2])
        label = label.translate([border_margin_mm, border_margin_mm, 0])
        return frame | hatching | label | text_solid

    # Frameless: just text
    return text_solid


def _build_hatching(
    width: float, length: float, spacing: float = 3.0
) -> "Bosl2Solid":
    """Build diagonal hatching lines for bed adhesion behind text.

    Args:
        width: Hatching area width.
        length: Hatching area length.
        spacing: Distance between hatching lines.

    Returns:
        Bosl2Solid with diagonal hatching lines.
    """
    from pybosl2 import cuboid

    hatching = None
    line_w = 0.6  # thin enough to bridge without supports
    diagonal = (width ** 2 + length ** 2) ** 0.5
    num_lines = int(diagonal / spacing) + 1
    import math
    angle = math.degrees(math.atan2(length, width))

    for i in range(num_lines):
        pos = i * spacing
        line = cuboid([diagonal, line_w, 0.2])
        line = line.rotate([0, 0, angle])
        line = line.translate([pos - diagonal / 2, pos - diagonal / 2, 0])
        if hatching is None:
            hatching = line
        else:
            hatching = hatching | line

    return hatching or cuboid([1, 1, 0.2])
