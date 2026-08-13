# SPDX-License-Identifier: Apache-2.0
"""Compartment row-width distribution (T052a / FR-004).

The shelf packer in `layout.py` places compartments at their requested size and
leaves whatever is left over as dead space at the end of each row. This module
takes a finished row and grows its members so the row fills the interior width
exactly, which is what you want for card wells and token trays that should butt
up against the box walls.
"""

from __future__ import annotations

from dataclasses import dataclass

PRECISION = 1
"""Dimensional output is held to 0.1 mm (FR-003) — never rounded to whole mm."""


@dataclass(frozen=True)
class RowItem:
    """One compartment in a row, as seen by the distributor."""

    label: str
    width: float
    length: float
    growable: bool = True
    """False pins the compartment at its requested width (e.g. a card slot)."""


def distribute_row_width(
    items: list[RowItem],
    available_width: float,
    gap: float = 2.0,
) -> list[tuple[str, float, float]]:
    """Grow the growable items in a row so the row fills `available_width`.

    Slack is shared in proportion to each growable item's current width, so a
    wide well absorbs more of the leftover than a narrow one and the row keeps
    its visual rhythm.

    Args:
        items: Compartments in the row, in placement order.
        available_width: Interior width the row must fill, in mm.
        gap: Spacing between adjacent compartments and at both ends, in mm.

    Returns:
        (label, width, length) per item, in the same order, at 0.1 mm precision.

    Raises:
        ValueError: If the items cannot fit in `available_width` at all.
    """
    if not items:
        return []

    total_gap = gap * (len(items) + 1)
    used = sum(i.width for i in items)
    slack = available_width - used - total_gap
    if slack < -0.05:
        raise ValueError(
            f"Row of {len(items)} compartments needs "
            f"{used + total_gap:.1f}mm but only {available_width:.1f}mm is "
            f"available (over by {-slack:.1f}mm): "
            + ", ".join(f"{i.label}={i.width:.1f}" for i in items)
        )

    growable = [i for i in items if i.growable]
    growable_width = sum(i.width for i in growable)
    if not growable or growable_width <= 0 or slack <= 0:
        return [(i.label, round(i.width, PRECISION), round(i.length, PRECISION)) for i in items]

    out: list[tuple[str, float, float]] = []
    for item in items:
        width = item.width
        if item.growable:
            width += slack * (item.width / growable_width)
        out.append((item.label, round(width, PRECISION), round(item.length, PRECISION)))
    return out


def distribute_rows(
    rows: list[list[RowItem]],
    available_width: float,
    gap: float = 2.0,
) -> list[list[tuple[str, float, float]]]:
    """Apply `distribute_row_width` to every row of a shelf layout."""
    return [distribute_row_width(row, available_width, gap) for row in rows]


def rows_from_placements(placements, gap: float = 2.0) -> list[list[str]]:
    """Group `CompartmentPlacement`s into rows by their y coordinate.

    Two placements share a row when their y origins are within `gap` of each
    other, which is how the shelf packer builds them.
    """
    rows: list[list] = []
    for placement in sorted(placements, key=lambda p: (p.position[1], p.position[0])):
        for row in rows:
            if abs(row[0].position[1] - placement.position[1]) <= gap:
                row.append(placement)
                break
        else:
            rows.append([placement])
    return [[p.label for p in row] for row in rows]
