# SPDX-License-Identifier: Apache-2.0
"""Compartment auto-layout — 2D shelf-based bin packing."""

from dataclasses import dataclass, field

from spec_driven.box.interior import Interior


@dataclass
class CompartmentPlacement:
    """Position of a single compartment inside a box."""

    label: str
    size: tuple[float, float]
    depth: float
    position: tuple[float, float]  # (x, y) in interior frame


@dataclass
class CompartmentLayout:
    """Result of laying out compartments inside a box interior."""

    placements: list[CompartmentPlacement] = field(default_factory=list)
    overflow: bool = False

    def all_compartment_sizes(self) -> list[tuple[float, float]]:
        """Return (width, length) for each placement."""
        return [p.size for p in self.placements]


def layout_compartments(
    interior: Interior,
    compartments: list[tuple[str, float, float, float]],
    wall_spacing: float = 2.0,
) -> CompartmentLayout:
    """Simple row-based layout of compartments in the interior.

    Places compartments left-to-right, wrapping to new rows when
    width is exceeded.

    Args:
        interior: The available interior space.
        compartments: List of (label, width, length, depth) tuples.
        wall_spacing: Gap between compartments.

    Returns:
        CompartmentLayout with positions assigned.
    """
    layout = CompartmentLayout()
    if not compartments:
        return layout

    interior_w = interior.width
    interior_l = interior.length

    x_cursor = wall_spacing
    y_cursor = wall_spacing
    current_row_height = 0.0

    for label, comp_w, comp_l, comp_depth in compartments:
        if x_cursor + comp_w + wall_spacing > interior_w:
            x_cursor = wall_spacing
            y_cursor += current_row_height + wall_spacing
            current_row_height = 0.0

            if y_cursor + comp_l + wall_spacing > interior_l:
                layout.overflow = True
                break

        if comp_w > interior_w or comp_l > interior_l:
            layout.overflow = True
            break

        layout.placements.append(
            CompartmentPlacement(
                label=label,
                size=(comp_w, comp_l),
                depth=comp_depth,
                position=(
                    interior.origin_x + x_cursor,
                    interior.origin_y + y_cursor,
                ),
            )
        )
        x_cursor += comp_w + wall_spacing
        current_row_height = max(current_row_height, comp_l)

    return layout


def compute_min_box_size(
    compartments: list[tuple[str, float, float, float]],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
) -> tuple[float, float, float]:
    """Compute the minimum box outer dimensions from compartment data.

    Estimates the box size needed to hold all compartments in a shelf layout.
    Width is total width of all compartments assuming they fill rows.
    Length is the total row stack height from the estimated layout.

    Args:
        compartments: List of (label, width, length, depth) tuples.
        wall_thickness: Box wall thickness.
        floor_thickness: Box floor thickness.
        lid_thickness: Box lid thickness.

    Returns:
        (width, length, height) — minimum outer box dimensions.
    """
    if not compartments:
        return (
            wall_thickness * 4,
            wall_thickness * 4,
            floor_thickness + lid_thickness + 5,
        )

    max_w = max(w for _, w, _, _ in compartments)
    max_l = max(l for _, _, l, _ in compartments)
    max_d = max(d for _, _, _, d in compartments)
    spacing = 2.0

    # Estimate total footprint by computing how compartments would pack
    total_width = 0.0
    total_rows = 0.0
    current_width = spacing
    current_row_height = 0.0

    # Sort by length descending for better packing estimate
    sorted_items = sorted(compartments, key=lambda x: x[2], reverse=True)

    for _, comp_w, comp_l, _ in sorted_items:
        if current_width + comp_w > total_width:
            total_width = max(total_width, current_width)
            current_width = spacing
            total_rows += current_row_height + spacing
            current_row_height = 0.0
        current_width += comp_w + spacing
        current_row_height = max(current_row_height, comp_l)

    total_width = max(total_width, current_width)
    total_rows += current_row_height + spacing

    # Ensure single-row layout fits
    box_w = max(total_width, max_w) + 2 * wall_thickness + 8
    box_l = max(total_rows, max_l) + 2 * wall_thickness + 8
    box_h = max_d + floor_thickness + lid_thickness + 4

    return (box_w, box_l, box_h)
