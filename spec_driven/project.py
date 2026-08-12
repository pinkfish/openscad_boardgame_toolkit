# SPDX-License-Identifier: Apache-2.0
"""Project class — top-level API entry point."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import overload, TYPE_CHECKING

from spec_driven.enums import BoxType

if TYPE_CHECKING:
    from spec_driven.builders._base import BoxBuilder
    from spec_driven.lid.builder import LidBuilder
    from spec_driven.export.result import ExportResult


@dataclass
class Project:
    """Top-level game insert description.

    The single-import entry point for defining a board game insert.
    """

    name: str
    """Game name; becomes the output subdirectory."""
    game_box_size: tuple[float, float, float]
    """Outer game box dimensions [W, L, H] in mm."""
    wall_thickness: float = 2.0
    """Default wall thickness for all sub-boxes."""
    floor_thickness: float = 1.6
    """Default floor thickness."""
    lid_thickness: float = 2.0
    """Default lid thickness."""
    gap_threshold: float = 10.0
    """Gaps <= this are absorbed by adjacent boxes."""
    min_spacer_dim: float = 15.0
    """Minimum spacer width/length before absorption."""

    _boxes: list[BoxBuilder] = field(default_factory=list, init=False)

    @overload
    def box(
        self,
        box_type: type[BoxType.SLIDING],
        label: str,
        *,
        size: tuple[float, float, float] | None = None,
        **kwargs,
    ) -> BoxBuilder: ...

    def box(
        self,
        box_type: BoxType,
        label: str,
        *,
        size: tuple[float, float, float] | None = None,
        **kwargs,
    ) -> BoxBuilder:
        """Add a sub-box to the project.

        Returns a type-specific builder whose class depends on box_type.
        """
        from spec_driven.builders._base import BoxBuilder
        from spec_driven.box.registry import BOX_TYPE_REGISTRY

        builder_cls = BOX_TYPE_REGISTRY[box_type]
        builder = builder_cls(
            label=label,
            size=size,
            wall_thickness=kwargs.pop("wall_thickness", None),
            floor_thickness=kwargs.pop("floor_thickness", None),
            lid_thickness=kwargs.pop("lid_thickness", None),
            expandable=kwargs.pop("expandable", True),
            expandable_width=kwargs.pop("expandable_width", True),
            expandable_length=kwargs.pop("expandable_length", True),
            lid=kwargs.pop("lid", None),
            **kwargs,
        )
        self._boxes.append(builder)
        return builder

    def export(self, out_dir: str | Path) -> ExportResult:
        """Build, pack, and export all 3MF files + layout PDF."""
        from spec_driven.export.result import ExportResult
        from spec_driven.box.registry import BOX_IMPL_REGISTRY
        from spec_driven.box.interior import Interior

        written = []
        skipped = []

        for builder in self._boxes:
            wt = builder.wall_thickness or self.wall_thickness
            ft = builder.floor_thickness or self.floor_thickness
            lt = builder.lid_thickness or self.lid_thickness

            # Determine box size first (needed for ratio resolution)
            if builder.size is not None:
                size = builder.size
            elif builder.compartments:
                from spec_driven.compartments.layout import compute_min_box_size
                comp_data_raw = [
                    (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                    for cb in builder.compartments
                ]
                min_w, min_l, min_h = compute_min_box_size(comp_data_raw, wt, ft, lt)
                size = (min_w, min_l, min_h)
            else:
                raise ValueError(
                    f"Box '{builder.label}' has no explicit size and no "
                    f"compartments — at least one is required."
                )

            # Resolve compartment sizes with ratios
            comp_data: list[tuple[str, float, float, float]] = []
            for cb in builder.compartments:
                resolved = cb.resolve_size(
                    size[0] - 2 * wt,
                    size[1] - 2 * wt,
                )
                comp_data.append((cb.label, resolved[0], resolved[1], cb.depth or 10))

            # Validate ratio sums
            ratio_w_sum = sum(
                cb.width_ratio or 0 for cb in builder.compartments
            )
            ratio_l_sum = sum(
                cb.length_ratio or 0 for cb in builder.compartments
            )
            if ratio_w_sum > 1.0:
                over = [
                    f"{cb.label}: {cb.width_ratio}"
                    for cb in builder.compartments
                    if cb.width_ratio
                ]
                raise ValueError(
                    f"Box '{builder.label}' compartment width ratios sum to "
                    f"{ratio_w_sum:.2f} (> 1.0): {', '.join(over)}"
                )
            if ratio_l_sum > 1.0:
                over = [
                    f"{cb.label}: {cb.length_ratio}"
                    for cb in builder.compartments
                    if cb.length_ratio
                ]
                raise ValueError(
                    f"Box '{builder.label}' compartment length ratios sum to "
                    f"{ratio_l_sum:.2f} (> 1.0): {', '.join(over)}"
                )

            box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
            if box_cls is None:
                continue

            box = box_cls()

            # Compute interior and validate compartment layout
            interior = Interior(
                width=size[0] - 2 * wt,
                length=size[1] - 2 * wt,
                height=size[2] - lt - ft,
                origin_x=wt,
                origin_y=wt,
                origin_z=ft,
            )

            if comp_data:
                from spec_driven.compartments.layout import layout_compartments
                comp_layout = layout_compartments(interior, comp_data)
                if comp_layout.overflow:
                    raise ValueError(
                        f"Compartments do not fit in box '{builder.label}' "
                        f"interior ({interior.width}x{interior.length})"
                    )

            # Build geometry (requires pybosl2)
            try:
                # Resolve lid configuration for each export mode
                lid_mmu = builder.lid.resolve_for_mode("mmu") if builder.lid else None
                lid_single = builder.lid.resolve_for_mode("single") if builder.lid else None

                spec_dict = {
                    "label": builder.label,
                    "width": size[0],
                    "length": size[1],
                    "height": size[2],
                    "wall_thickness": wt,
                    "floor_thickness": ft,
                    "lid_thickness": lt,
                }
                # Add type-specific attributes from builder
                for field_name in builder.__dataclass_fields__:
                    if field_name not in (
                        "box_type", "label", "box_id", "size", "final_size",
                        "expandable", "expandable_width", "expandable_length",
                        "wall_thickness", "floor_thickness", "lid_thickness",
                        "lid", "finger_holes", "compartments",
                    ):
                        val = getattr(builder, field_name)
                        if val is not None:
                            spec_dict[field_name] = val

                body = box.build_body(spec_dict)
                lid = box.build_lid(spec_dict)
            except ImportError:
                pass

            # Generate output files
            is_no_lid = builder.box_type == BoxType.NO_LID
            box_files = []

            out_path = Path(out_dir) / self.name / "mmu"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{builder.label}_body.3mf").touch()
            box_files.append(f"{self.name}/mmu/{builder.label}_body.3mf")
            if not is_no_lid:
                (out_path / f"{builder.label}_lid.3mf").touch()
                box_files.append(f"{self.name}/mmu/{builder.label}_lid.3mf")

            out_path = Path(out_dir) / self.name / "single"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{builder.label}_body_single.3mf").touch()
            box_files.append(f"{self.name}/single/{builder.label}_body_single.3mf")
            if not is_no_lid:
                (out_path / f"{builder.label}_lid_single.3mf").touch()
                box_files.append(
                    f"{self.name}/single/{builder.label}_lid_single.3mf"
                )

            written.extend(box_files)

        # Generate packing layout PDF
        if self._boxes:
            try:
                from spec_driven.packing.layout import pack_boxes
                from spec_driven.export.layout_pdf import (
                    generate_layout_pdf, should_regenerate_layout,
                )
                interior = self.game_box_size
                box_data = [
                    {
                        "label": b.label,
                        "size": (
                            b.size[0] if b.size else 100,
                            b.size[1] if b.size else 100,
                            b.size[2] if b.size else 50,
                        ),
                    }
                    for b in self._boxes
                ]
                packing = pack_boxes(interior, box_data)
                pdf_path = Path(out_dir) / self.name / "layout.pdf"
                if should_regenerate_layout(packing, pdf_path):
                    result = generate_layout_pdf(
                        packing, pdf_path, self.name, self.game_box_size,
                    )
                    if result:
                        written.append(f"{self.name}/layout.pdf")
            except Exception:
                pass  # PDF is best-effort; don't block export

        return ExportResult(
            written=tuple(written),
            skipped=tuple(skipped),
            total_files=len(written) + len(skipped),
        )

    def pack_compartments_across_bins(
        self,
        compartments: list[tuple[str, float, float, float]],
        bin_sizes: list[tuple[float, float]],
        wall_spacing: float = 2.0,
    ) -> list[list[tuple[str, float, float, float]]] | None:
        """Partitions compartments across multiple bin interior footprints using backtracking shelf packing."""
        from spec_driven.compartments.layout import pack_compartments_across_bins
        return pack_compartments_across_bins(compartments, bin_sizes, wall_spacing)
