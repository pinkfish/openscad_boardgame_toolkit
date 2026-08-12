# SPDX-License-Identifier: Apache-2.0
"""Spacer tray generation from gap dimensions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacerSpec:
    """Configuration for a single spacer tray."""

    label: str
    width: float
    length: float
    height: float
    position: tuple[float, float, float]


def generate_spacers(
    container_width: float,
    container_length: float,
    row_widths: list[float],
    row_lengths: list[float],
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
    min_spacer_height: float = 5.0,
) -> list[SpacerSpec]:
    """Generate spacer tray specs for gaps in the container.

    Args:
        container_width: Outer container interior width.
        container_length: Outer container interior length.
        row_widths: Total width used by each row.
        row_lengths: Length of each row.
        gap_threshold: Gaps < this are absorbed, not filled.
        min_spacer_dim: Minimum spacer width/length before absorption.
        min_spacer_height: Default spacer tray height.

    Returns:
        List of SpacerSpec for gaps that need filling.
    """
    spacers: list[SpacerSpec] = []
    counter = 1

    for i, (row_w, row_l) in enumerate(zip(row_widths, row_lengths)):
        remaining_w = container_width - row_w
        if remaining_w >= min_spacer_dim and remaining_w >= gap_threshold:
            y_offset = sum(row_lengths[:i]) if i > 0 else 0.0
            spacers.append(
                SpacerSpec(
                    label=f"spacer_{counter}",
                    width=remaining_w,
                    length=row_l,
                    height=min_spacer_height,
                    position=(row_w, y_offset, 0),
                )
            )
            counter += 1

    # Check for gap after last row
    total_length_used = sum(row_lengths)
    remaining_l = container_length - total_length_used
    if remaining_l >= min_spacer_dim and remaining_l >= gap_threshold:
        spacers.append(
            SpacerSpec(
                label=f"spacer_{counter}",
                width=container_width,
                length=remaining_l,
                height=min_spacer_height,
                position=(0, total_length_used, 0),
            )
        )

    return spacers
