# SPDX-License-Identifier: Apache-2.0
"""Box packing layout — skyline-based 3D box packing into game box interior."""

from __future__ import annotations

from dataclasses import dataclass, field


class PackingError(ValueError):
    """Raised when the sub-boxes cannot be arranged inside the game box.

    Note that the packer is a greedy heuristic, so this does not prove the
    layout is impossible — only that this solver could not find it.
    """


@dataclass
class Placement:
    """Position and size of one box in the nested layout."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]
    rotation: bool = False
    path: tuple[tuple[float, float], ...] | None = None
    """Footprint outline relative to `position`, when it is not a rectangle.

    Set on spacers whose leftover region is L-, T- or U-shaped (FR-018); such a
    spacer is built as a `PathBox` rather than a plain tray. None means the
    footprint is just `size`."""


@dataclass
class BoxPacking:
    """Computed nested layout of sub-boxes inside a container."""

    container_size: tuple[float, float, float]
    placements: list[Placement] = field(default_factory=list)
    row_lengths: list[float] = field(default_factory=list)
    row_widths: list[float] = field(default_factory=list)
    spacer_placements: list[Placement] = field(default_factory=list)


HEIGHT_ABSORB_MM = 3.0
"""A gap above an expandable box no deeper than this is absorbed into it (FR-012).

Anything deeper is real space that a spacer should claim, not slack to grow into.
"""


def _pack_guillotine(
    container_size: tuple[float, float, float], boxes: list[dict]
) -> list[Placement] | None:
    """Try the guillotine solver, returning None if it finds nothing."""
    from pyboxbuilder.packing.guillotine import Item, pack_guillotine

    placed = pack_guillotine(
        container_size,
        [
            Item(
                label=b["label"],
                size=tuple(float(v) for v in b["size"]),  # type: ignore[arg-type]
                no_rotate=bool(b.get("no_rotate", False)),
            )
            for b in boxes
        ],
    )
    if placed is None:
        return None
    return [
        Placement(
            label=p.label,
            position=p.position,
            size=p.size,
            rotation=p.rotated,
        )
        for p in placed
    ]


def _expand_in_place(
    placements: list[Placement],
    container_size: tuple[float, float, float],
    boxes: list[dict],
) -> None:
    """Grow expandable boxes into the slack around them (FR-012).

    Two independent passes, matching what the corner-point solver has always
    done: close a shallow gap above a box, then run a box right up to whatever
    is beside it. Height first, because growing a box taller can bring it
    alongside a neighbour it did not previously touch.
    """
    container_w, _container_l, container_h = container_size
    axes = {}
    for b in boxes:
        expandable = bool(b.get("expandable"))
        axes[b["label"]] = (
            expandable,
            expandable and bool(b.get("expandable_width", True)),
        )

    def sized(placement, width=None, height=None):
        w, l, h = placement.size
        return Placement(
            label=placement.label,
            position=placement.position,
            size=(width if width is not None else w, l,
                  height if height is not None else h),
            rotation=placement.rotation,
            path=placement.path,
        )

    for index, p in enumerate(placements):
        if not axes.get(p.label, (False, False))[0]:
            continue
        x, y, z = p.position
        w, l, h = p.size
        ceiling = float(container_h)
        for other in placements:
            if other is p:
                continue
            ox, oy, oz = other.position
            ow, ol, oh = other.size
            if x < ox + ow and x + w > ox and y < oy + ol and y + l > oy:
                if oz >= z + h:
                    ceiling = min(ceiling, oz)
        if (ceiling - z) - h < HEIGHT_ABSORB_MM:
            placements[index] = sized(p, height=ceiling - z)

    for index, p in enumerate(placements):
        if not axes.get(p.label, (False, False))[1]:
            continue
        x, y, z = p.position
        w, l, h = p.size
        wall = float(container_w)
        for other in placements:
            if other is p:
                continue
            ox, oy, oz = other.position
            ow, ol, oh = other.size
            if y < oy + ol and y + l > oy and z < oz + oh and z + h > oz:
                if ox >= x + w:
                    wall = min(wall, ox)
        placements[index] = sized(p, width=wall - x)


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

    # The guillotine solver goes first: it handles densely-filled layouts the
    # corner-point one cannot, and it cannot float a box (see guillotine.py).
    # The corner-point solver stays as a fallback because it searches a
    # different, non-guillotine space, so it can still place the odd layout the
    # other rules out.
    placed = _pack_guillotine(container_size, boxes)
    if placed is not None:
        packing.placements = placed
        _expand_in_place(packing.placements, container_size, boxes)
        return packing

    # Only the fallback needs the legacy root-level module, so import it only
    # when the fallback is actually reached — and treat its absence as "no
    # fallback available" rather than letting an ImportError escape in place of
    # the PackingError callers handle.
    try:
        from compartments import pack_3d_boxes
    except ImportError:
        pack_3d_boxes = None  # type: ignore[assignment]

    # Prepare items for 3D packer. The axis codes it understands are "w" (grow
    # right to the next neighbour) and "h" (close a sub-3mm gap above, FR-012);
    # a box that is not expandable at all gets neither and keeps its size.
    items = []
    for b in boxes:
        axes: list[str] = []
        if b.get("expandable"):
            axes.append("h")
            if b.get("expandable_width", True):
                axes.append("w")
        items.append({
            "name": b["label"],
            "size": list(b["size"]),
            "expandable": axes,
            "no_rotate": b.get("no_rotate", False),
        })

    # Run 3D solver. A failure here used to be swallowed and returned as an
    # empty packing, so the export "succeeded" while writing no boxes at all —
    # say what went wrong instead.
    try:
        if pack_3d_boxes is None:
            raise PackingError("no fallback solver available")
        packed = pack_3d_boxes(container_size, items)
    except Exception as exc:
        box_volume = sum(b["size"][0] * b["size"][1] * b["size"][2] for b in boxes)
        container_volume = container_size[0] * container_size[1] * container_size[2]
        fill = 100 * box_volume / container_volume if container_volume else 0.0
        too_tall = [
            b["label"] for b in boxes if b["size"][2] > container_size[2] + 1e-6
        ]
        detail = (
            f" Boxes taller than the container: {', '.join(too_tall)}."
            if too_tall
            else f" At {fill:.0f}% fill the packer's greedy placement may simply "
            f"not find an arrangement even though one exists — give the boxes "
            f"explicit positions, or make them smaller or expandable."
        )
        raise PackingError(
            f"Could not pack {len(boxes)} boxes into "
            f"{container_size[0]:.1f} x {container_size[1]:.1f} x "
            f"{container_size[2]:.1f} mm.{detail}"
        ) from exc

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
