# SPDX-License-Identifier: Apache-2.0
"""Lid decoration builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from spec_driven.enums import LabelMode, PatternType

if TYPE_CHECKING:
    from spec_driven.color import Color


@dataclass(frozen=True)
class PatternBuilder:
    """Through-hole pattern configuration for a lid."""

    type: PatternType = PatternType.HEX_GRID
    """Pattern fill type."""
    colors: tuple[Color, ...] = ()
    """Per-element colors (multiple supported)."""
    spacing: float | None = None
    """Auto-calculated from lid size if None."""


@dataclass(frozen=True)
class LidBuilder:
    """Lid decoration configuration."""

    text: str | None = None
    """Label text to engrave on the lid."""
    label_mode: LabelMode = LabelMode.FRAMED
    """Framed or frameless label style."""
    diagonal: bool = False
    """Corner-to-corner text orientation."""
    text_color: Color | None = None
    """Label text color; auto-contrast default if None."""
    frame_color: Color | None = None
    """Frame top layer color; auto-contrast default if None."""
    pattern: PatternBuilder | None = None
    """Through-hole pattern configuration."""
    pattern_color: Color | None = None
    """Pattern top layer color; auto-contrast default if None."""
    min_text_height_mm: float = 4.0
    """Minimum text height before label is skipped."""
    border_margin_mm: float = 5.0
    """Label border margin from lid edges."""
