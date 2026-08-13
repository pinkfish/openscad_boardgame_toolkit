# SPDX-License-Identifier: Apache-2.0
"""Color layer assignment for MMU (multi-material) printing.

Assigns three independently settable accent colors to label text,
frame top layer, and pattern top layer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder import Color

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@dataclass
class ColorLayerAssignment:
    """Maps geometry components to their accent colors."""

    body_color: Color
    """The base box body color."""
    text_color: Color | None = None
    """Label text color (None = no label)."""
    frame_color: Color | None = None
    """Frame top layer color (None = no frame)."""
    pattern_color: Color | None = None
    """Pattern top layer color (None = no pattern)."""


from dataclasses import dataclass


def resolve_colors(
    body_color: Color,
    text_color: Color | None = None,
    frame_color: Color | None = None,
    pattern_color: Color | None = None,
) -> ColorLayerAssignment:
    """Resolve accent colors with sensible defaults.

    Args:
        body_color: The base box body color.
        text_color: Label text color. Defaults to Color("white").
        frame_color: Frame top layer color. Defaults to a contrasting hue.
        pattern_color: Pattern top layer color. Defaults to a third hue.

    Returns:
        ColorLayerAssignment with all colors resolved.
    """
    if text_color is None:
        text_color = Color("white")

    if frame_color is None:
        # Contrasting hue: shift by 120 degrees
        frame_color = _contrast_hue(body_color, shift=0.33)

    if pattern_color is None:
        # Third contrasting hue: shift by 240 degrees
        pattern_color = _contrast_hue(body_color, shift=0.67)

    return ColorLayerAssignment(
        body_color=body_color,
        text_color=text_color,
        frame_color=frame_color,
        pattern_color=pattern_color,
    )


def _contrast_hue(base: Color, shift: float) -> Color:
    """Shift the hue of a color for contrast."""
    import colorsys
    r, g, b, _ = base.rgba
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + shift) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return Color([r, g, b])
