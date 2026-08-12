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
    compartments: list[tuple[str, float, float, float]],  # (label, w, l, depth)
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
        # Check if compartment fits in remaining width
        if x_cursor + comp_w + wall_spacing > interior_w:
            # Move to next row
            x_cursor = wall_spacing
            y_cursor += current_row_height + wall_spacing
            current_row_height = 0.0

            # Check if compartment fits in interior length
            if y_cursor + comp_l + wall_spacing > interior_l:
                layout.overflow = True
                break

        # Check if compartment itself fits in interior
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
