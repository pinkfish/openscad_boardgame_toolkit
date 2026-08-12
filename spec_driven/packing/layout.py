# SPDX-License-Identifier: Apache-2.0
"""Box packing layout — skyline-based 3D box packing into game box interior."""

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
    """Pack sub-boxes into a container using skyline-based 2D packing.

    The skyline algorithm tracks the upper envelope of placed boxes
    and finds the lowest Y position for each new box, handling
    variable-length boxes more efficiently than column-first placement.

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

    # Sort boxes by length descending (best-fit decreasing heuristic)
    sorted_boxes = sorted(
        boxes, key=lambda b: b["size"][1], reverse=True
    )

    # Skyline: list of (x, y) points describing the upper envelope
    # Starting with a single segment at y=0 spanning the full width
    skyline: list[tuple[float, float]] = [(0.0, 0.0), (cw, 0.0)]

    for box in sorted_boxes:
        label = box["label"]
        bw, bl, bh = box["size"]

        if bw > cw or bl > cl or bh > ch:
            continue  # Box won't fit at all

        # Find the lowest skyline segment wide enough for this box
        best_x = None
        best_y = float("inf")
        for i in range(len(skyline) - 1):
            x1, y1 = skyline[i]
            x2, _ = skyline[i + 1]
            segment_width = x2 - x1
            if segment_width >= bw:
                if y1 < best_y:
                    best_y = y1
                    best_x = x1

        if best_x is None or best_y + bl > cl:
            continue  # No room for this box

        # Place the box
        packing.placements.append(
            Placement(
                label=label,
                position=(best_x, best_y, 0),
                size=(bw, bl, bh),
            )
        )

        # Update the skyline
        new_y = best_y + bl
        new_skyline: list[tuple[float, float]] = []

        # Copy points strictly before the box's x-start
        i = 0
        while i < len(skyline) and skyline[i][0] < best_x - 0.01:
            new_skyline.append(skyline[i])
            i += 1

        # Insert the new raised segment at the box start
        if new_skyline and abs(new_skyline[-1][0] - best_x) < 0.01:
            new_skyline[-1] = (best_x, max(new_skyline[-1][1], new_y))
        else:
            new_skyline.append((best_x, new_y))

        # Skip points that fall inside the box's x-span
        while i < len(skyline) and skyline[i][0] < best_x + bw + 0.01:
            i += 1

        # Drop back to the original skyline height at the box end
        end_y = 0.0
        if i > 0:
            end_y = skyline[i - 1][1]
        if not new_skyline or abs(new_skyline[-1][0] - (best_x + bw)) < 0.01:
            if new_skyline:
                new_skyline[-1] = (new_skyline[-1][0], max(new_skyline[-1][1], end_y))
        else:
            new_skyline.append((best_x + bw, end_y))

        # Copy remaining points that are after the box
        while i < len(skyline):
            if skyline[i][0] > best_x + bw + 0.01:
                new_skyline.append(skyline[i])
            i += 1

        # Merge adjacent points with same height (keep container boundary point)
        merged: list[tuple[float, float]] = []
        for i, pt in enumerate(new_skyline):
            is_last = i == len(new_skyline) - 1
            if not is_last and merged and abs(merged[-1][1] - pt[1]) < 0.01:
                continue
            merged.append(pt)
        skyline = merged

    # Compute row lengths and widths from the layout
    if packing.placements:
        # Find rows by grouping placements by Y position
        rows: dict[float, list[Placement]] = {}
        for p in packing.placements:
            y_key = round(p.position[1], 1)
            rows.setdefault(y_key, []).append(p)

        for y_pos, row_boxes in sorted(rows.items()):
            row_len = max(p.size[1] for p in row_boxes)
            row_wid = sum(p.size[0] for p in row_boxes)
            packing.row_lengths.append(row_len)
            packing.row_widths.append(row_wid)

            # Spacer in width direction
            end_x = max(p.position[0] + p.size[0] for p in row_boxes)
            remaining_w = cw - end_x
            if remaining_w >= gap_threshold and remaining_w >= min_spacer_dim:
                packing.spacer_placements.append(
                    Placement(
                        label=f"spacer_{len(packing.spacer_placements) + 1}",
                        position=(end_x, y_pos, 0),
                        size=(remaining_w, row_len, 5),
                    )
                )

    return packing
