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
    game_box_size: tuple[float, float, float] | None = None
    """Outer game box dimensions [W, L, H] in mm. None = standalone boxes (no game box)."""
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
    clearance_slack: float = 1.0
    """Clearance slack on each side of the game box in the X/Y directions (mm)."""
    board_thickness: float = 0.0
    """Thickness of the game board (mm). Reserved space at the TOP of the box — the board sits on top of the sub-boxes, not a spacer gap."""
    generate_spacers: bool = True
    """Whether to automatically generate spacer boxes/trays to fill layout gaps."""

    _boxes: list[BoxBuilder] = field(default_factory=list, init=False)
    _shared_groups: list = field(default_factory=list, init=False)

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
            position=kwargs.pop("position", None),
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

        # Standalone mode: no game box → export each box directly, no packing/PDF
        if self.game_box_size is None:
            return self._export_standalone(out_dir)

        # 0. Resolve shared compartments across multiple bins dynamically
        from spec_driven.compartments.builder import CompartmentBuilder
        from spec_driven.enums import ScoopSide
        for box_labels, comps in self._shared_groups:
            builders = [next((x for x in self._boxes if x.label == label), None) for label in box_labels]
            builders = [b for b in builders if b is not None]
            if len(builders) < 2:
                continue
            bin_sizes = []
            for b in builders:
                wt = b.wall_thickness or self.wall_thickness
                if b.size is not None and b.size[0] is not None and b.size[1] is not None:
                    bin_sizes.append((b.size[0] - 2 * wt, b.size[1] - 2 * wt))
                else:
                    bin_sizes.append((self.game_box_size[0] - 2 * wt, self.game_box_size[1] - 2 * wt))
            from spec_driven.compartments.layout import pack_compartments_across_bins
            packed_bins = pack_compartments_across_bins(comps, bin_sizes)
            if not packed_bins:
                raise ValueError(f"Failed to partition shared compartments across boxes: {box_labels}")
            for b, bin_items in zip(builders, packed_bins):
                new_compartments = []
                for name, w, l, d in bin_items:
                    new_compartments.append(
                        CompartmentBuilder(
                            label=name,
                            size=(w, l),
                            depth=d,
                            finger_scoop=True,
                            scoop_side=ScoopSide.FRONT,
                        )
                    )
                object.__setattr__(b, "compartments", tuple(new_compartments))

        # 1. Resolve minimum sizes and run 3D packer first to propagate final sizes
        box_data = []
        resolved_min_sizes = {}
        manual_placements = []
        for builder in self._boxes:
            wt = builder.wall_thickness or self.wall_thickness
            ft = builder.floor_thickness or self.floor_thickness
            lt = builder.lid_thickness or self.lid_thickness

            if builder.size is not None:
                size = list(builder.size)
                if None in size:
                    from spec_driven.compartments.layout import compute_min_box_size
                    comp_data_raw = [
                        (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                        for cb in builder.compartments
                    ]
                    min_w, min_l, min_h = compute_min_box_size(
                        comp_data_raw, wt, ft, lt,
                        max_w=self.game_box_size[0] - 2 * wt,
                        max_l=self.game_box_size[1] - 2 * wt
                    )
                    if size[0] is None: size[0] = min_w
                    if size[1] is None: size[1] = min_l
                    if size[2] is None: size[2] = min_h
                size = tuple(size)
            elif builder.compartments:
                from spec_driven.compartments.layout import compute_min_box_size
                comp_data_raw = [
                    (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                    for cb in builder.compartments
                ]
                min_w, min_l, min_h = compute_min_box_size(
                    comp_data_raw, wt, ft, lt,
                    max_w=self.game_box_size[0] - 2 * wt,
                    max_l=self.game_box_size[1] - 2 * wt
                )
                size = (min_w, min_l, min_h)
            else:
                raise ValueError(
                    f"Box '{builder.label}' has no explicit size and no "
                    f"compartments — at least one is required."
                )
            resolved_min_sizes[builder.label] = size
            if builder.position is not None:
                from spec_driven.packing.layout import Placement
                manual_placements.append(
                    Placement(
                        label=builder.label,
                        position=builder.position,
                        size=size,
                        rotation=False
                    )
                )
            else:
                box_data.append({
                    "label": builder.label,
                    "size": size,
                    "expandable": builder.expandable or getattr(builder, "expandable_width", False) or getattr(builder, "expandable_length", False),
                    "no_rotate": builder.no_rotate,
                })

        # Run 3D packer with clearance slack
        slack = getattr(self, "clearance_slack", 1.0)
        packing_container = (
            self.game_box_size[0] - 2 * slack,
            self.game_box_size[1] - 2 * slack,
            self.game_box_size[2],
        )
        from spec_driven.packing.layout import pack_boxes
        packing = pack_boxes(packing_container, box_data)

        # Shift placements to center them within the outer game box
        from spec_driven.packing.layout import Placement
        shifted_placements = []
        for p in packing.placements:
            shifted_placements.append(
                Placement(
                    label=p.label,
                    position=(p.position[0] + slack, p.position[1] + slack, p.position[2]),
                    size=p.size,
                    rotation=p.rotation,
                )
            )
        shifted_placements.extend(manual_placements)
        packing.placements = shifted_placements

        # Map placements to resolved final_size using object.__setattr__ to bypass FrozenInstanceError
        resolved_sizes = {p.label: p.size for p in packing.placements}
        for builder in self._boxes:
            val = resolved_sizes[builder.label] if builder.label in resolved_sizes else resolved_min_sizes[builder.label]
            object.__setattr__(builder, "final_size", val)

        # 2. Build and export box geometry using final resolved sizes
        for builder in self._boxes:
            wt = builder.wall_thickness or self.wall_thickness
            ft = builder.floor_thickness or self.floor_thickness
            lt = builder.lid_thickness or self.lid_thickness
            size = builder.final_size

            # Resolve compartment sizes with ratios
            comp_data: list[tuple[str, float, float, float]] = []
            for cb in builder.compartments:
                resolved = cb.resolve_size(
                    size[0] - 2 * wt,
                    size[1] - 2 * wt,
                )
                comp_data.append((cb.label, resolved[0], resolved[1], cb.depth or 10))

            # Validate ratio sums
            ratio_w_sum = sum(cb.width_ratio or 0 for cb in builder.compartments)
            ratio_l_sum = sum(cb.length_ratio or 0 for cb in builder.compartments)
            if ratio_w_sum > 1.0:
                over = [f"{cb.label}: {cb.width_ratio}" for cb in builder.compartments if cb.width_ratio]
                raise ValueError(f"Box '{builder.label}' compartment width ratios sum to {ratio_w_sum:.2f} (> 1.0): {', '.join(over)}")
            if ratio_l_sum > 1.0:
                over = [f"{cb.label}: {cb.length_ratio}" for cb in builder.compartments if cb.length_ratio]
                raise ValueError(f"Box '{builder.label}' compartment length ratios sum to {ratio_l_sum:.2f} (> 1.0): {', '.join(over)}")

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
                no_rotate_labels = {cb.label for cb in builder.compartments if cb.no_rotate}
                comp_layout = layout_compartments(interior, comp_data, no_rotate_labels=no_rotate_labels)
                if comp_layout.overflow:
                    raise ValueError(
                        f"Compartments do not fit in box '{builder.label}' "
                        f"interior ({interior.width}x{interior.length})"
                    )

            # Build geometry (requires pybosl2)
            try:
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
                box_files.append(f"{self.name}/single/{builder.label}_lid_single.3mf")

            written.extend(box_files)

        # 3. Generate and export 3D spacers from gaps in the packed layout
        def generate_spacers_for_3d_packing(container_size, placements):
            from spec_driven.packing.layout import Placement
            if not placements:
                return []
            W, L, H = container_size
            
            # Find distinct coordinates
            xs = {0.0, W}
            ys = {0.0, L}
            zs = {0.0, H}
            for p in placements:
                x, y, z = p.position
                w, l, h = p.size
                xs.add(x)
                xs.add(x + w)
                ys.add(y)
                ys.add(y + l)
                zs.add(z)
                zs.add(z + h)
                
            sorted_xs = sorted(list(xs))
            sorted_ys = sorted(list(ys))
            sorted_zs = sorted(list(zs))
            
            nx = len(sorted_xs) - 1
            ny = len(sorted_ys) - 1
            nz = len(sorted_zs) - 1
            
            occupied = [[[False] * nz for _ in range(ny)] for _ in range(nx)]
            
            for p in placements:
                px, py, pz = p.position
                pw, pl, ph = p.size
                for i in range(nx):
                    if sorted_xs[i] >= px - 0.01 and sorted_xs[i+1] <= px + pw + 0.01:
                        for j in range(ny):
                            if sorted_ys[j] >= py - 0.01 and sorted_ys[j+1] <= py + pl + 0.01:
                                for k in range(nz):
                                    if sorted_zs[k] >= pz - 0.01 and sorted_zs[k+1] <= pz + ph + 0.01:
                                        occupied[i][j][k] = True
            
            spacers = []
            visited = [[[False] * nz for _ in range(ny)] for _ in range(nx)]
            
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        if not occupied[i][j][k] and not visited[i][j][k]:
                            i2 = i
                            while i2 < nx and not occupied[i2][j][k] and not visited[i2][j][k]:
                                i2 += 1
                            
                            j2 = j
                            while j2 < ny:
                                ok = True
                                for ii in range(i, i2):
                                    if occupied[ii][j2][k] or visited[ii][j2][k]:
                                        ok = False
                                        break
                                if not ok:
                                    break
                                j2 += 1
                                
                            k2 = k
                            while k2 < nz:
                                ok = True
                                for ii in range(i, i2):
                                    for jj in range(j, j2):
                                        if occupied[ii][jj][k2] or visited[ii][jj][k2]:
                                            ok = False
                                            break
                                    if not ok:
                                        break
                                if not ok:
                                    break
                                k2 += 1
                                
                            for ii in range(i, i2):
                                for jj in range(j, j2):
                                    for kk in range(k, k2):
                                        visited[ii][jj][kk] = True
                                        
                            pos_x = sorted_xs[i]
                            pos_y = sorted_ys[j]
                            pos_z = sorted_zs[k]
                            size_w = sorted_xs[i2] - pos_x
                            size_l = sorted_ys[j2] - pos_y
                            size_h = sorted_zs[k2] - pos_z
                            
                            if size_w >= 5.0 and size_l >= 5.0 and size_h >= 5.0:
                                spacers.append(
                                    Placement(
                                        label=f"spacer_{len(spacers)+1}",
                                        position=(pos_x, pos_y, pos_z),
                                        size=(size_w, size_l, size_h),
                                        rotation=False
                                    )
                                )
            return spacers

        # Effective box container: subtract board thickness from the height so the
        # board area is reserved (occupied by the game board), not treated as a spacer gap.
        effective_container = (
            self.game_box_size[0],
            self.game_box_size[1],
            self.game_box_size[2] - self.board_thickness,
        )
        if self.generate_spacers:
            spacer_placements = generate_spacers_for_3d_packing(effective_container, packing.placements)
        else:
            spacer_placements = []
        packing.spacer_placements = spacer_placements

        # Delete stale spacer files from previous runs (no longer-generated spacers)
        self._delete_stale_spacers(out_dir, spacer_placements)

        # Build and write spacer 3MF files
        for spacer in spacer_placements:
            try:
                no_lid_cls = BOX_IMPL_REGISTRY.get(BoxType.NO_LID)
                if no_lid_cls is not None:
                    spec_dict = {
                        "label": spacer.label,
                        "width": spacer.size[0],
                        "length": spacer.size[1],
                        "height": spacer.size[2],
                        "wall_thickness": self.wall_thickness,
                        "floor_thickness": self.floor_thickness,
                        "lid_thickness": 0.0,
                    }
                    box_inst = no_lid_cls()
                    body = box_inst.build_body(spec_dict)
            except Exception:
                pass

            out_path = Path(out_dir) / self.name / "mmu"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{spacer.label}_body.3mf").touch()
            written.append(f"{self.name}/mmu/{spacer.label}_body.3mf")

            out_path = Path(out_dir) / self.name / "single"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{spacer.label}_body_single.3mf").touch()
            written.append(f"{self.name}/single/{spacer.label}_body_single.3mf")

        # 4. Generate packing layout PDF
        if self._boxes:
            try:
                from spec_driven.export.layout_pdf import (
                    generate_layout_pdf, should_regenerate_layout,
                )
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

    def _export_standalone(self, out_dir: str | Path) -> ExportResult:
        """Export boxes independently with no game box, no packing, no PDF.

        Standalone mode (game_box_size=None): each box is exported directly
        with its own size (explicit or computed from compartments).
        """
        from spec_driven.export.result import ExportResult
        from spec_driven.box.registry import BOX_IMPL_REGISTRY
        from spec_driven.box.interior import Interior
        from spec_driven.enums import BoxType

        written = []

        for builder in self._boxes:
            wt = builder.wall_thickness or self.wall_thickness
            ft = builder.floor_thickness or self.floor_thickness
            lt = builder.lid_thickness or self.lid_thickness

            if builder.size is not None:
                size = list(builder.size)
                if None in size:
                    from spec_driven.compartments.layout import compute_min_box_size
                    comp_raw = [
                        (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                        for cb in builder.compartments
                    ]
                    min_w, min_l, min_h = compute_min_box_size(comp_raw, wt, ft, lt)
                    if size[0] is None: size[0] = min_w
                    if size[1] is None: size[1] = min_l
                    if size[2] is None: size[2] = min_h
                size = tuple(size)
            elif builder.compartments:
                from spec_driven.compartments.layout import compute_min_box_size
                comp_raw = [
                    (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                    for cb in builder.compartments
                ]
                size = compute_min_box_size(comp_raw, wt, ft, lt)
            else:
                raise ValueError(
                    f"Box '{builder.label}' has no explicit size and no "
                    f"compartments — at least one is required."
                )

            is_no_lid = builder.box_type == BoxType.NO_LID

            out_path = Path(out_dir) / self.name / "mmu"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{builder.label}_body.3mf").touch()
            written.append(f"{self.name}/mmu/{builder.label}_body.3mf")
            if not is_no_lid:
                (out_path / f"{builder.label}_lid.3mf").touch()
                written.append(f"{self.name}/mmu/{builder.label}_lid.3mf")

            out_path = Path(out_dir) / self.name / "single"
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / f"{builder.label}_body_single.3mf").touch()
            written.append(f"{self.name}/single/{builder.label}_body_single.3mf")
            if not is_no_lid:
                (out_path / f"{builder.label}_lid_single.3mf").touch()
                written.append(f"{self.name}/single/{builder.label}_lid_single.3mf")

        return ExportResult(
            written=tuple(written),
            skipped=(),
            total_files=len(written),
        )

    def _delete_stale_spacers(self, out_dir: str | Path, spacer_placements: list) -> None:
        """Delete orphaned spacer 3MF files that no longer correspond to a generated spacer.

        Args:
            out_dir: Root output directory.
            spacer_placements: The current set of spacer placements.
        """
        current_labels = {sp.label for sp in spacer_placements}
        for mode in ("mmu", "single"):
            spacer_dir = Path(out_dir) / self.name / mode
            if not spacer_dir.exists():
                continue
            suffix = "_body_single.3mf" if mode == "single" else "_body.3mf"
            for f in spacer_dir.glob("spacer_*"):
                label = f.name[:-len(suffix)]
                if label not in current_labels:
                    f.unlink(missing_ok=True)

    def pack_compartments_across_bins(
        self,
        compartments: list[tuple[str, float, float, float]],
        bin_sizes: list[tuple[float, float]],
        wall_spacing: float = 2.0,
    ) -> list[list[tuple[str, float, float, float]]] | None:
        """Partitions compartments across multiple bin interior footprints using backtracking shelf packing."""
        from spec_driven.compartments.layout import pack_compartments_across_bins
        return pack_compartments_across_bins(compartments, bin_sizes, wall_spacing)

    def share_compartments(
        self,
        boxes: list[str],
        compartments: list[tuple[str, float, float, float]],
    ) -> None:
        """Registers a group of compartments to be dynamically partitioned across the given box labels."""
        self._shared_groups.append((boxes, compartments))
