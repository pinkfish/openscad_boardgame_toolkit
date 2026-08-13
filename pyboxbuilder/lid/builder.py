# SPDX-License-Identifier: Apache-2.0
"""Lid decoration builders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pyboxbuilder.enums import LabelMode, PatternType

if TYPE_CHECKING:
    from pyboxbuilder import Color


@dataclass(frozen=True)
class PatternBuilder:
    """Through-hole pattern configuration for a lid."""

    type: PatternType = PatternType.HEX_GRID
    colors: tuple[Color, ...] = ()
    spacing: float | None = None


@dataclass(frozen=True)
class LidBuilder:
    """Lid decoration configuration.

    Supports per-export-mode overrides: mmu_label and single_label
    override the parent fields for their respective export modes.
    Unset modes fall back to the parent configuration.
    """

    text: str | None = None
    label_mode: LabelMode = LabelMode.FRAMED
    diagonal: bool = False
    text_color: Color | None = None
    frame_color: Color | None = None
    pattern: PatternBuilder | None = None
    pattern_color: Color | None = None
    min_text_height_mm: float = 4.0
    border_margin_mm: float = 5.0
    mmu_label: LidBuilder | None = field(default=None)
    single_label: LidBuilder | None = field(default=None)

    def resolve_for_mode(self, mode: str) -> LidBuilder:
        """Resolve label configuration for a specific export mode.

        Args:
            mode: 'mmu' or 'single'.

        Returns:
            Effective LidBuilder with per-mode overrides applied
            over parent defaults. Returns self if no override set.
        """
        if mode == "mmu" and self.mmu_label is not None:
            return self._merge(self.mmu_label)
        if mode == "single" and self.single_label is not None:
            return self._merge(self.single_label)
        return self

    def _merge(self, override: LidBuilder) -> LidBuilder:
        """Merge override fields over parent defaults.

        For each field, the override value is used if it differs from
        the default (indicating user intent); otherwise parent value.
        """
        return LidBuilder(
            text=override.text if override.text is not None else self.text,
            label_mode=(
                override.label_mode
                if override.label_mode != LabelMode.FRAMED
                else self.label_mode
            ),
            diagonal=override.diagonal or self.diagonal,
            text_color=override.text_color or self.text_color,
            frame_color=override.frame_color or self.frame_color,
            pattern=override.pattern or self.pattern,
            pattern_color=override.pattern_color or self.pattern_color,
            min_text_height_mm=override.min_text_height_mm,
            border_margin_mm=override.border_margin_mm,
        )
