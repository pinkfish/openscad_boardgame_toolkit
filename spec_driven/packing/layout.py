# SPDX-License-Identifier: Apache-2.0
"""Box packing layout — 3D box packing into game box interior."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Placement:
    """Position and size of one box in the nested layout."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]
    rotation: bool = False


@dataclass
class BoxPacking:
    """Computed nested layout of sub-boxes inside a container."""

    container_size: tuple[float, float, float]
    placements: list[Placement] = field(default_factory=list)
    row_lengths: list[float] = field(default_factory=list)
    row_widths: list[float] = field(default_factory=list)
    spacer_placements: list[Placement] = field(default_factory=list)


def pack_boxes(
    container_size: tuple[float, float, float],
    boxes: list[dict],
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
) -> BoxPacking:
    """Pack sub-boxes into a container using column-first greedy placement.

    Places boxes in columns (rows of one), tracks row lengths and widths.

    Args:
        container_size: (width, length, height) of the outer box interior.
        boxes: List of dicts with keys: label, size (w, l, h), expandable.
        gap_threshold: Gaps <= this are absorbed.
        min_spacer_dim: Minimum spacer dimension before absorption.

    Returns:
        BoxPacking with placements assigned.
    """
    cw, cl, ch = container_size
    packing = BoxPacking(container_size=container_size)

    if not boxes:
        return packing

    # Simple column-first packing: place boxes left-to-right
    x_cursor = 0.0
    current_row_height = 0.0
    row_boxes: list[Placement] = []
    all_rows: list[list[Placement]] = []

    for box in boxes:
        label = box["label"]
        bw, bl, bh = box["size"]
        expandable = box.get("expandable", True)

        if x_cursor + bw > cw:
            # Finish current row
            if row_boxes:
                all_rows.append(row_boxes)
            # Start new row
            x_cursor = 0.0
            current_row_height += max(p.size[1] for p in row_boxes) if row_boxes else 0

            if current_row_height + bl > cl:
                # Would exceed container length
                continue

            row_boxes = []

        packing.placements.append(
            Placement(
                label=label,
                position=(x_cursor, current_row_height, 0),
                size=(bw, bl, bh),
            )
        )
        row_boxes.append(packing.placements[-1])
        x_cursor += bw
        current_row_height = max(current_row_height, bl)

    # Final row
    if row_boxes:
        all_rows.append(row_boxes)

    # Compute row lengths and widths
    for row in all_rows:
        row_len = max(p.size[1] for p in row) if row else 0.0
        row_wid = sum(p.size[0] for p in row)
        packing.row_lengths.append(row_len)
        packing.row_widths.append(row_wid)

        # Check for gaps after the last box in each row
        remaining = cw - row_wid
        if remaining >= gap_threshold and remaining >= min_spacer_dim:
            spacer = Placement(
                label=f"spacer_{len(packing.spacer_placements) + 1}",
                position=(row_wid, 0, 0),
                size=(remaining, row_len, 5),  # spacer height default 5mm
            )
            packing.spacer_placements.append(spacer)

    return packing
