# SPDX-License-Identifier: Apache-2.0
"""View-time helpers for :meth:`pyboxbuilder.Project.show`.

Nothing in this module affects exported geometry. Colours assigned here are a
preview aid so a viewer can tell one box from another; the material a box
prints in is decided by the exporter, not by this file.
"""

from __future__ import annotations

import colorsys
import hashlib
from dataclasses import dataclass
from typing import Sequence

from pybosl2 import Color

# Saturation/value for generated box hues. Chosen so every hue reads as a
# distinct, solid colour on screen rather than a pastel wash.
_HUE_SATURATION = 0.55
_HUE_VALUE = 0.85

# Spacers are always grey (never a hue from the box palette) so dead fill is
# instantly distinguishable from a box that holds pieces. The small lightness
# spread keeps adjacent spacers from merging visually.
_SPACER_GREY_MIN = 0.55
_SPACER_GREY_SPAN = 0.20

#: Alpha applied to a lid so the box underneath stays visible through it.
LID_ALPHA = 0.5

#: How far a lid's colour is lifted towards white relative to its box.
LID_LIGHTEN = 0.35


def _stable_fraction(label: str) -> float:
    """Map a label to a stable fraction in ``[0, 1)``.

    Uses a content hash rather than :func:`hash`, whose per-process salt would
    give the same box a different colour on every run.

    Args:
        label: The box label to hash.

    Returns:
        A deterministic float in ``[0, 1)``.
    """
    digest = hashlib.md5(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 2 ** 32


def stable_color(label: str) -> Color:
    """Assign a distinct, stable preview colour to a box label.

    The same label always produces the same colour, across runs and processes,
    so a preview does not reshuffle its palette between renders.

    Args:
        label: The box label to derive a colour from.

    Returns:
        A saturated :class:`pybosl2.Color` whose hue is derived from the label.
    """
    r, g, b = colorsys.hsv_to_rgb(_stable_fraction(label), _HUE_SATURATION, _HUE_VALUE)
    return Color([r, g, b])


def spacer_color(label: str = "") -> Color:
    """Return the preview colour for a spacer tray — always a variant of grey.

    Args:
        label: Optional spacer label; varies the lightness slightly so
            neighbouring spacers stay distinguishable. Grey regardless.

    Returns:
        A grey :class:`pybosl2.Color`, never a hue from the box palette.
    """
    level = _SPACER_GREY_MIN + _SPACER_GREY_SPAN * _stable_fraction(label or "spacer")
    return Color([level, level, level])


def lighten(color: Color, amount: float = LID_LIGHTEN) -> Color:
    """Lift a colour towards white, preserving its alpha.

    Args:
        color: The colour to lighten.
        amount: Fraction of the remaining distance to white, ``0.0``–``1.0``.

    Returns:
        A new :class:`pybosl2.Color`; the input is not modified.
    """
    r, g, b, a = color.rgba
    return Color([c + (1.0 - c) * amount for c in (r, g, b)] + [a])


def with_alpha(color: Color, alpha: float) -> Color:
    """Return ``color`` at a new alpha.

    Args:
        color: The colour to adjust.
        alpha: Opacity, ``0.0`` (invisible) to ``1.0`` (opaque).

    Returns:
        A new :class:`pybosl2.Color` with the given alpha.
    """
    r, g, b, _ = color.rgba
    return Color([r, g, b, alpha])


def lid_color(box_color: Color) -> Color:
    """Return the preview colour for a lid sitting on a box of ``box_color``.

    A lid is drawn in a lighter shade at 50% alpha so it reads as a separate
    piece and the box underneath remains visible through it.

    Args:
        box_color: The colour of the box the lid belongs to.

    Returns:
        A lighter, semi-transparent :class:`pybosl2.Color`.
    """
    return with_alpha(lighten(box_color), LID_ALPHA)


def layer_heights(placements: Sequence) -> list[float]:
    """Return the distinct Z levels boxes rest at, lowest first.

    A "layer" is a height something sits at, so two boxes sharing a Z origin
    are one layer however different their heights.

    Args:
        placements: Objects carrying a ``position`` 3-tuple.

    Returns:
        Sorted unique Z origins.
    """
    return sorted({round(p.position[2], 6) for p in placements})


def remove_top_layers(placements: Sequence, count: int) -> list:
    """Drop the top ``count`` vertical layers from a set of placements.

    A box is removed when its **top surface** rises above the cut, so a tall
    box spanning into a removed layer goes with it rather than being sliced.

    Args:
        placements: Objects carrying ``position`` and ``size`` 3-tuples.
        count: How many layers to remove from the top. ``0`` keeps everything;
            a count at or above the number of layers removes everything.

    Returns:
        The surviving placements, in their original order.

    Raises:
        ValueError: If ``count`` is negative.
    """
    if count < 0:
        raise ValueError(f"remove_layers must be >= 0; got {count}")
    if count == 0:
        return list(placements)

    levels = layer_heights(placements)
    if count >= len(levels):
        return []

    cut = levels[len(levels) - count]
    eps = 1e-6
    return [p for p in placements if p.position[2] + p.size[2] <= cut + eps]


@dataclass(frozen=True)
class PreviewPiece:
    """One solid in a preview, with the colour it should be drawn in.

    Each box, lid and spacer is a separate piece — the preview never unions
    them, since a union collapses these colours into one.
    """

    label: str
    """The piece's box label; lids and spacers keep their box's label."""
    solid: object
    """The built geometry, already translated to its packed position."""
    color: Color
    """The colour to draw this piece in."""
    kind: str
    """One of ``"body"``, ``"lid"`` or ``"spacer"``."""
