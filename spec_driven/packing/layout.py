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
    """Pack sub-boxes into a container using a 3D First-Fit Decreasing solver.

    Args:
        container_size: (width, length, height) of the outer box interior.
        boxes: List of dicts with keys: label, size (w, l, h), expandable.
        gap_threshold: Gaps <= this are absorbed.
        min_spacer_dim: Minimum spacer dimension before absorption.

    Returns:
        BoxPacking with placements assigned.
    """
    packing = BoxPacking(container_size=container_size)

    if not boxes:
        return packing

    from compartments import pack_3d_boxes

    # Prepare items for 3D packer
    items = []
    for b in boxes:
        items.append({
            "name": b["label"],
            "size": list(b["size"]),
            "expandable": ["h"] if b.get("expandable") else [],
        })

    # Run 3D solver
    packed = pack_3d_boxes(container_size, items)

    # Convert results to placements
    for name, info in packed.items():
        packing.placements.append(
            Placement(
                label=name,
                position=tuple(info["pos"]),
                size=tuple(info["size"]),
                rotation=info["rotated"],
            )
        )

    # Note: Spacers and row computations can be added if needed,
    # but the 3D packer will pack boxes at their full 3D coordinates.
    return packing
