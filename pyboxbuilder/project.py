# SPDX-License-Identifier: Apache-2.0
"""Project class — top-level API entry point."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import overload, TYPE_CHECKING

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.lid.builder import LidBuilder
    from pyboxbuilder.export.result import ExportResult


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
    min_spacer_height: float = 5.0
    """A spacer tray thinner than this on any axis is dropped as unprintable (FR-014)."""
    clearance_slack: float = 1.0
    """Clearance slack on each side of the game box in the X/Y directions (mm)."""
    board_thickness: float = 0.0
    """Thickness of the game board (mm). Reserved space at the TOP of the box — the board sits on top of the sub-boxes, not a spacer gap."""
    generate_spacers: bool = True
    """Whether to automatically generate spacer boxes/trays to fill layout gaps."""

    _boxes: list[BoxBuilder] = field(default_factory=list, init=False)
    _shared_groups: list = field(default_factory=list, init=False)
    piece_bounds: tuple = field(default_factory=tuple, init=False)
    """Bounding box of every exported piece, populated by `export()` (FR-027)."""

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
        from pyboxbuilder.builders._base import BoxBuilder
        from pyboxbuilder.box.registry import BOX_TYPE_REGISTRY

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

    def arrange(self, layout, origin: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Position boxes from a declarative layout tree (T186).

        The alternative to hand-typed coordinates for densely packed inserts,
        where the packer cannot help: describe the structure with
        `columns`/`rows`/`stack` and let the sizes decide the positions.

        Args:
            layout: A `pyboxbuilder.layout` group, or a single box label.
            origin: Where the arrangement's minimum corner goes.

        Returns:
            The `Arrangement`, so a caller can inspect the resolved extent.

        Raises:
            LayoutError: If the tree names an unknown box or places one twice.
            ValueError: If a named box has no explicit size, or the arrangement
                does not fit the game box.
        """
        from pyboxbuilder.layout import LayoutError, arrange as resolve

        sizes: dict[str, tuple[float, float, float]] = {}
        for builder in self._boxes:
            if builder.size is None or any(v is None for v in builder.size):
                continue  # resolved from compartments later; can't be arranged
            sizes[builder.label] = tuple(builder.size)  # type: ignore[arg-type]

        arrangement = resolve(layout, sizes, origin)

        if self.game_box_size is not None and not arrangement.fits(self.game_box_size):
            raise LayoutError(
                f"Arrangement is {arrangement.size[0]:.1f} x "
                f"{arrangement.size[1]:.1f} x {arrangement.size[2]:.1f} mm, "
                f"which does not fit the {self.game_box_size[0]:.1f} x "
                f"{self.game_box_size[1]:.1f} x {self.game_box_size[2]:.1f} mm game box."
            )

        by_label = {b.label: b for b in self._boxes}
        for label, position in arrangement.positions.items():
            object.__setattr__(by_label[label], "position", position)
        return arrangement

    def show(
        self,
        show_lids: bool = False,
        remove_layers: int = 0,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
    ) -> None:
        """Preview the packed box layout interactively.

        Builds every box body at its final packed position and shows it. Each
        box is shown as its **own** solid — the preview never unions them,
        because a union carries one colour and would fuse touching boxes into
        an indivisible blob, hiding the seams a packing preview exists to
        show. Used when NOT running inside make (``FROM_MAKE`` unset) — in the
        PythonSCAD GUI or a Jupyter notebook this renders the layout; the
        make/export flow instead writes 3MF files via ``export()``.

        Writes no files, and generates no layout PDF.

        Args:
            show_lids: Place each lid in its seated position as well. Off by
                default because lids cover the compartments and their
                neighbours. A shown lid is drawn semi-transparent in a lighter
                shade of its box's colour so it reads as a separate piece.
            remove_layers: Omit the top N vertical layers of the packed
                layout, revealing what sits underneath — the live equivalent
                of the exploded PDF view. A box is removed when its top
                surface rises above the cut.
            fn: Fixed facets per circle for every curve in the preview. Drop
                it low for a fast preview; ``None`` defers to fa/fs.
            fa: Minimum angle per fragment, in degrees (default 12).
            fs: Minimum fragment size, in mm (default 2).

        Raises:
            ValueError: If ``remove_layers`` is negative, or a precision
                setting is out of range.
        """
        from pyboxbuilder.precision import use

        with use(fn=fn, fa=fa, fs=fs):
            pieces = self._preview_pieces(show_lids=show_lids, remove_layers=remove_layers)

        for piece in pieces:
            solid = piece.solid
            try:
                solid = solid.color(piece.color)
            except (AttributeError, TypeError):
                pass  # Uncolourable geometry still previews, just uncoloured.
            solid.show()

    def _preview_pieces(self, show_lids: bool = False, remove_layers: int = 0) -> list:
        """Build the list of separately-coloured solids :meth:`show` renders.

        Split out from :meth:`show` so the placement, layer filtering and
        colour assignment can be tested without a render binary.

        Args:
            show_lids: Include each box's lid, lightened and semi-transparent.
            remove_layers: Number of top layers to omit.

        Returns:
            A list of :class:`pyboxbuilder.preview.PreviewPiece`, one per body,
            lid and spacer — never unioned together.

        Raises:
            ValueError: If ``remove_layers`` is negative.
        """
        from pyboxbuilder.preview import (
            PreviewPiece, lid_color, remove_top_layers, spacer_color, stable_color,
        )

        if remove_layers < 0:
            raise ValueError(f"remove_layers must be >= 0; got {remove_layers}")

        def colour_for(builder) -> "Color":
            """A box's own colour when it declares one, else a stable hue."""
            declared = getattr(builder, "color", None)
            return declared if declared is not None else stable_color(builder.label)

        pieces: list[PreviewPiece] = []

        if self.game_box_size is None:
            # Standalone: no packing, so line the boxes up side by side. There
            # are no layers and no spacers to filter.
            x = 0.0
            for builder in self._boxes:
                self._standalone_size(builder)
                body, lid, size = self._build_box_solids(builder)
                if body is None:
                    continue
                colour = colour_for(builder)
                # The lid is already at its correct local Z (inside/on the
                # box), so it takes the same translation as the body.
                pieces.append(PreviewPiece(builder.label, body.translate([x, 0.0, 0.0]), colour, "body"))
                if show_lids and lid is not None:
                    pieces.append(
                        PreviewPiece(builder.label, lid.translate([x, 0.0, 0.0]), lid_color(colour), "lid")
                    )
                x += size[0] + 10.0
            return pieces

        packing = self._resolve_final_layout()
        placements = list(packing.placements)

        # Spacers complete the picture — without them the preview shows holes
        # where the insert is actually filled.
        spacers = self._spacer_placements(packing) if self.generate_spacers else []

        kept = {p.label for p in remove_top_layers(placements + spacers, remove_layers)}
        pos_by_label = {p.label: p.position for p in placements}

        for builder in self._boxes:
            if builder.label not in kept:
                continue
            body, lid, _size = self._build_box_solids(builder)
            if body is None:
                continue
            pos = list(pos_by_label.get(builder.label, builder.position or (0.0, 0.0, 0.0)))
            colour = colour_for(builder)
            pieces.append(PreviewPiece(builder.label, body.translate(pos), colour, "body"))
            if show_lids and lid is not None:
                pieces.append(PreviewPiece(builder.label, lid.translate(pos), lid_color(colour), "lid"))

        for spacer in spacers:
            if spacer.label not in kept:
                continue
            body = self._build_spacer_solid(spacer)
            if body is None:
                continue
            pieces.append(
                PreviewPiece(
                    spacer.label, body.translate(list(spacer.position)),
                    spacer_color(spacer.label), "spacer",
                )
            )

        return pieces

    def _resolve_final_layout(self):
        """Resolve each box's final size and packed position.

        Computes minimum sizes (from an explicit size or the compartments),
        runs the 3D packer, and sets ``final_size`` on every builder. Returns
        the :class:`BoxPacking`, whose placements carry the final positions.
        """
        from pyboxbuilder.packing.layout import Placement, pack_boxes

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
                    from pyboxbuilder.compartments.layout import compute_min_box_size
                    comp_data_raw = [
                        (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                        for cb in builder.compartments
                    ]
                    min_w, min_l, min_h = compute_min_box_size(
                        comp_data_raw, wt, ft, lt,
                        max_w=self.game_box_size[0] - 2 * wt,
                        max_l=self.game_box_size[1] - 2 * wt,
                    )
                    if size[0] is None: size[0] = min_w
                    if size[1] is None: size[1] = min_l
                    if size[2] is None: size[2] = min_h
                size = tuple(size)
            elif builder.compartments:
                from pyboxbuilder.compartments.layout import compute_min_box_size
                comp_data_raw = [
                    (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                    for cb in builder.compartments
                ]
                min_w, min_l, min_h = compute_min_box_size(
                    comp_data_raw, wt, ft, lt,
                    max_w=self.game_box_size[0] - 2 * wt,
                    max_l=self.game_box_size[1] - 2 * wt,
                )
                size = (min_w, min_l, min_h)
            else:
                raise ValueError(
                    f"Box '{builder.label}' has no explicit size and no "
                    f"compartments — at least one is required."
                )
            resolved_min_sizes[builder.label] = size
            if builder.position is not None:
                manual_placements.append(
                    Placement(label=builder.label, position=builder.position, size=size, rotation=False)
                )
            else:
                box_data.append({
                    "label": builder.label,
                    "size": size,
                    "expandable": builder.expandable,
                    "expandable_width": builder.expandable and builder.expandable_width,
                    "no_rotate": builder.no_rotate,
                })

        slack = getattr(self, "clearance_slack", 1.0)
        packing_container = (
            self.game_box_size[0] - 2 * slack,
            self.game_box_size[1] - 2 * slack,
            self.game_box_size[2] - self.board_thickness,
        )
        packing = pack_boxes(packing_container, box_data)

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

        resolved_sizes = {p.label: p.size for p in packing.placements}
        for builder in self._boxes:
            val = resolved_sizes[builder.label] if builder.label in resolved_sizes else resolved_min_sizes[builder.label]
            object.__setattr__(builder, "final_size", val)

        self._packing = packing
        return packing

    def _build_box_solids(self, builder):
        """Build a box's body and lid solids from its resolved final size.

        Returns ``(body, lid, size)``; ``body``/``lid`` are ``None`` when the
        box type produced no geometry (or pybosl2 is unavailable).
        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.interior import Interior

        wt = builder.wall_thickness or self.wall_thickness
        ft = builder.floor_thickness or self.floor_thickness
        lt = builder.lid_thickness or self.lid_thickness
        size = builder.final_size

        comp_data = []
        for cb in builder.compartments:
            resolved = cb.resolve_size(size[0] - 2 * wt, size[1] - 2 * wt)
            comp_data.append((
                cb.label, resolved[0], resolved[1], cb.depth or 10,
                getattr(cb, "shape_file", None), cb.position, getattr(cb, "elements", ()),
            ))

        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None:
            return None, None, size

        box = box_cls()
        interior = Interior(
            width=size[0] - 2 * wt, length=size[1] - 2 * wt, height=size[2] - lt - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

        comp_layout = None
        if comp_data:
            from pyboxbuilder.compartments.layout import layout_compartments
            no_rotate_labels = {cb.label for cb in builder.compartments if cb.no_rotate}
            comp_layout = layout_compartments(interior, comp_data, no_rotate_labels=no_rotate_labels)

        body = lid = None
        try:
            spec_dict = {
                "label": builder.label,
                "width": size[0], "length": size[1], "height": size[2],
                "wall_thickness": wt, "floor_thickness": ft, "lid_thickness": lt,
                "hollow": not comp_data,
            }
            for field_name in builder.__dataclass_fields__:
                if field_name in (
                    "box_type", "label", "box_id", "size", "final_size",
                    "expandable", "expandable_width", "expandable_length",
                    "wall_thickness", "floor_thickness", "lid_thickness",
                    "lid", "finger_holes", "compartments", "color",
                ):
                    continue
                val = getattr(builder, field_name)
                if val is not None:
                    spec_dict[field_name] = val

            body = box.build_body(spec_dict)
            lid = box.build_lid(spec_dict)

            if comp_layout is not None and body is not None:
                from pyboxbuilder.compartments.carve import build_contents
                contents = build_contents(
                    comp_layout.placements, interior,
                    {cb.label: cb for cb in builder.compartments},
                )
                if contents is not None:
                    body = body - contents
        except ImportError:
            pass

        return body, lid, size

    def _standalone_size(self, builder) -> tuple[float, float, float]:
        """Resolve a standalone box's size and record it as its ``final_size``.

        Standalone boxes are never packed, so nothing else would set
        ``final_size``; both :meth:`_export_standalone` and the preview go
        through here so they cannot disagree about a box's size.

        Args:
            builder: The box builder to size. An explicit ``size`` wins, with
                any ``None`` axis filled in from the compartments.

        Returns:
            The resolved ``(width, length, height)`` in mm.

        Raises:
            ValueError: If the box has neither an explicit size nor
                compartments to derive one from.
        """
        from pyboxbuilder.compartments.layout import compute_min_box_size

        wt = builder.wall_thickness or self.wall_thickness
        ft = builder.floor_thickness or self.floor_thickness
        lt = builder.lid_thickness or self.lid_thickness

        def from_compartments() -> tuple[float, float, float]:
            return compute_min_box_size(
                [
                    (cb.label, cb.size[0] if cb.size else 50, cb.size[1] if cb.size else 50, cb.depth or 10)
                    for cb in builder.compartments
                ],
                wt, ft, lt,
            )

        if builder.size is not None:
            size = list(builder.size)
            if None in size:
                derived = from_compartments()
                size = [axis if axis is not None else derived[i] for i, axis in enumerate(size)]
            size = tuple(size)
        elif builder.compartments:
            size = from_compartments()
        else:
            raise ValueError(
                f"Box '{builder.label}' has no explicit size and no "
                f"compartments — at least one is required."
            )

        object.__setattr__(builder, "final_size", size)
        return size

    def _spacer_placements(self, packing) -> list:
        """Derive the spacer trays that fill the gaps in a packed layout.

        Shared by :meth:`export` and :meth:`show` so a preview shows exactly
        the spacers an export would write.

        Args:
            packing: The resolved :class:`BoxPacking` whose placements the
                leftover space is measured around.

        Returns:
            The spacer placements, after the sweep → merge → shrink → filter
            pass (FR-014a/b/c). Empty when no gap survives the minimums.
        """
        from pyboxbuilder.packing.spacer import generate_spacer_placements

        # Effective container: subtract the board thickness from the height so
        # the board area stays reserved rather than being filled with a spacer.
        effective_container = (
            self.game_box_size[0],
            self.game_box_size[1],
            self.game_box_size[2] - self.board_thickness,
        )
        return generate_spacer_placements(
            effective_container,
            packing.placements,
            clearance=self.clearance_slack,
            min_dim=self.min_spacer_height,
        )

    def _build_spacer_solid(self, spacer):
        """Build one spacer tray's geometry in its own local frame.

        Args:
            spacer: A spacer placement carrying ``label``, ``size`` and an
                optional rectilinear ``path`` footprint.

        Returns:
            The built solid, or ``None`` when the geometry could not be built
            (pybosl2 unavailable, or a degenerate footprint).
        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        try:
            # An L/T/U-shaped leftover is a PathBox; a plain rectangle is a
            # NoLidBox tray.
            spacer_cls = BOX_IMPL_REGISTRY.get(BoxType.PATH if spacer.path else BoxType.NO_LID)
            if spacer_cls is None:
                return None
            return spacer_cls().build_body({
                "label": spacer.label,
                "width": spacer.size[0],
                "length": spacer.size[1],
                "height": spacer.size[2],
                "wall_thickness": self.wall_thickness,
                "floor_thickness": self.floor_thickness,
                "lid_thickness": 0.0,
                "path": spacer.path or (),
            })
        except Exception:
            return None

    def export(
        self,
        out_dir: str | Path,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
    ) -> ExportResult:
        """Build, pack, and export all 3MF files + the layout PDF.

        Args:
            out_dir: Directory to write into; files land under
                ``{out_dir}/{project name}/mmu/`` and ``.../single/``.
            fn: Fixed facets per circle for every curve in the exported
                geometry. ``None`` (the default) defers to fa/fs. Raise it for
                print-quality curves.
            fa: Minimum angle per fragment, in degrees (default 12).
            fs: Minimum fragment size, in mm (default 2).

        Returns:
            An :class:`ExportResult` listing the files written and skipped.

        Raises:
            ValueError: If a box cannot be sized, or a precision setting is
                out of range.
            PackingError: If the boxes cannot be packed into the game box.
        """
        from pyboxbuilder.precision import use

        with use(fn=fn, fa=fa, fs=fs):
            # Standalone mode: no game box → export each box directly, no packing/PDF
            if self.game_box_size is None:
                return self._export_standalone(out_dir)
            return self._export_packed(out_dir)

    def _export_packed(self, out_dir: str | Path) -> ExportResult:
        """Export a project that has a game box: pack, spacer, build, write.

        Args:
            out_dir: Directory to write into.

        Returns:
            An :class:`ExportResult` listing the files written and skipped.
        """
        from pyboxbuilder.export.result import ExportResult
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, LIDLESS_BOX_TYPES
        from pyboxbuilder.box.interior import Interior
        from pyboxbuilder.export.exporter import BoxExporter

        exporter = BoxExporter(out_dir, self.name)

        # 0. Resolve shared compartments across multiple bins dynamically
        from pyboxbuilder.compartments.builder import CompartmentBuilder
        from pyboxbuilder.enums import ScoopSide
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
            from pyboxbuilder.compartments.layout import pack_compartments_across_bins
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
                    from pyboxbuilder.compartments.layout import compute_min_box_size
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
                from pyboxbuilder.compartments.layout import compute_min_box_size
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
                from pyboxbuilder.packing.layout import Placement
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
                    # `expandable` is the master switch: off means the box keeps
                    # the size it was given. The per-axis flags only narrow it.
                    "expandable": builder.expandable,
                    "expandable_width": builder.expandable and builder.expandable_width,
                    "no_rotate": builder.no_rotate,
                })

        # Run 3D packer with clearance slack. The board sits on top of the
        # sub-boxes, so the packer only gets the height below it — otherwise
        # auto-placed boxes climb into the space the board needs.
        slack = getattr(self, "clearance_slack", 1.0)
        packing_container = (
            self.game_box_size[0] - 2 * slack,
            self.game_box_size[1] - 2 * slack,
            self.game_box_size[2] - self.board_thickness,
        )
        from pyboxbuilder.packing.layout import pack_boxes
        packing = pack_boxes(packing_container, box_data)

        # Shift placements to center them within the outer game box
        from pyboxbuilder.packing.layout import Placement
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
            comp_data = []
            for cb in builder.compartments:
                resolved = cb.resolve_size(
                    size[0] - 2 * wt,
                    size[1] - 2 * wt,
                )
                comp_data.append((
                    cb.label,
                    resolved[0],
                    resolved[1],
                    cb.depth or 10,
                    getattr(cb, "shape_file", None),
                    cb.position,
                    getattr(cb, "elements", ()),
                ))

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

            comp_layout = None
            if comp_data:
                from pyboxbuilder.compartments.layout import layout_compartments
                no_rotate_labels = {cb.label for cb in builder.compartments if cb.no_rotate}
                comp_layout = layout_compartments(interior, comp_data, no_rotate_labels=no_rotate_labels)
                if comp_layout.overflow:
                    raise ValueError(
                        f"Compartments do not fit in box '{builder.label}' "
                        f"interior ({interior.width}x{interior.length})"
                    )

            # Build geometry (requires pybosl2)
            body = lid = None
            try:
                spec_dict = {
                    "label": builder.label,
                    "width": size[0],
                    "length": size[1],
                    "height": size[2],
                    "wall_thickness": wt,
                    "floor_thickness": ft,
                    "lid_thickness": lt,
                    # Hollow the whole interior only when nothing else defines
                    # the cavities; with compartments, they are the cavities.
                    "hollow": not comp_data,
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

                # Carve the compartments (and any element packs) out of the body
                if comp_layout is not None and body is not None:
                    from pyboxbuilder.compartments.carve import build_contents

                    contents = build_contents(
                        comp_layout.placements,
                        interior,
                        {cb.label: cb for cb in builder.compartments},
                    )
                    if contents is not None:
                        body = body - contents
            except ImportError:
                pass

            has_lid = builder.box_type not in LIDLESS_BOX_TYPES
            self._write_box(exporter, builder, body, lid, size, lt, has_lid)

        # 3. Generate and export 3D spacers from gaps in the packed layout.
        # The sweep-merge-shrink pass lives in packing/spacer.py (FR-014a/b/c).
        spacer_placements = self._spacer_placements(packing) if self.generate_spacers else []
        packing.spacer_placements = spacer_placements

        # Delete stale spacer files from previous runs (no longer-generated spacers)
        exporter.delete_stale("spacer_", {sp.label for sp in spacer_placements})

        # Build and write spacer 3MF files
        for spacer in spacer_placements:
            exporter.write_box(
                spacer.label, body=self._build_spacer_solid(spacer),
                size=spacer.size, has_lid=False,
            )

        # 4. Generate packing layout PDF
        if self._boxes:
            try:
                from pyboxbuilder.export.layout_pdf import (
                    generate_layout_pdf, should_regenerate_layout,
                )
                pdf_path = Path(out_dir) / self.name / "layout.pdf"
                if should_regenerate_layout(packing, pdf_path):
                    result = generate_layout_pdf(
                        packing, pdf_path, self.name, self.game_box_size, box_builders=self._boxes,
                    )
                    if result:
                        exporter.state.written.append(f"{self.name}/layout.pdf")
            except Exception:
                pass  # PDF is best-effort; don't block export

        self.piece_bounds = tuple(exporter.state.bounds)
        return ExportResult(
            written=tuple(exporter.state.written),
            skipped=tuple(exporter.state.skipped),
            total_files=len(exporter.state.written) + len(exporter.state.skipped),
        )

    def _write_box(
        self, exporter, builder, body, lid, size, lid_thickness, has_lid: bool
    ) -> None:
        """Decorate the lid per colour mode and hand both pieces to the exporter.

        The label has to be resolved per mode — raised and coloured for mmu,
        engraved for single — so the lid is decorated twice rather than once.
        """
        from pyboxbuilder.lid.decorate import decorate_lid

        for mode in ("mmu", "single"):
            mode_lid, inserts = lid, None
            if has_lid and lid is not None and builder.lid is not None:
                try:
                    decorated = decorate_lid(lid, builder.lid, lid_thickness, mode)
                    mode_lid = decorated.solid
                    inserts = decorated.inserts or None
                except ImportError:
                    pass

            exporter.write_piece(builder.label, "body", mode, body, size=size)
            if has_lid:
                exporter.write_piece(
                    builder.label, "lid", mode, mode_lid, inserts, size=size,
                )

    def _export_standalone(self, out_dir: str | Path) -> ExportResult:
        """Export boxes independently with no game box, no packing, no PDF.

        Standalone mode (game_box_size=None): each box is exported directly
        with its own size (explicit or computed from compartments).
        """
        from pyboxbuilder.export.result import ExportResult
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, LIDLESS_BOX_TYPES
        from pyboxbuilder.box.interior import Interior
        from pyboxbuilder.export.exporter import BoxExporter

        exporter = BoxExporter(out_dir, self.name)

        for builder in self._boxes:
            wt = builder.wall_thickness or self.wall_thickness
            ft = builder.floor_thickness or self.floor_thickness
            lt = builder.lid_thickness or self.lid_thickness

            size = self._standalone_size(builder)

            body = lid = None
            box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
            if box_cls is not None:
                try:
                    spec_dict = {
                        "label": builder.label,
                        "width": size[0],
                        "length": size[1],
                        "height": size[2],
                        "wall_thickness": wt,
                        "floor_thickness": ft,
                        "lid_thickness": lt,
                    }
                    box_inst = box_cls()
                    body = box_inst.build_body(spec_dict)
                    lid = box_inst.build_lid(spec_dict)
                except ImportError:
                    body = lid = None

            exporter.write_box(
                builder.label,
                body=body,
                lid=lid,
                size=size,
                has_lid=builder.box_type not in LIDLESS_BOX_TYPES,
            )

        self.piece_bounds = tuple(exporter.state.bounds)
        return ExportResult(
            written=tuple(exporter.state.written),
            skipped=tuple(exporter.state.skipped),
            total_files=len(exporter.state.written) + len(exporter.state.skipped),
        )

    def _delete_stale_spacers(self, out_dir: str | Path, spacer_placements: list) -> None:
        """Delete orphaned spacer 3MF files that no longer correspond to a generated spacer.

        Args:
            out_dir: Root output directory.
            spacer_placements: The current set of spacer placements.
        """
        from pyboxbuilder.export.exporter import BoxExporter

        BoxExporter(out_dir, self.name).delete_stale(
            "spacer_", {sp.label for sp in spacer_placements}
        )

    def pack_compartments_across_bins(
        self,
        compartments: list[tuple[str, float, float, float]],
        bin_sizes: list[tuple[float, float]],
        wall_spacing: float = 2.0,
    ) -> list[list[tuple[str, float, float, float]]] | None:
        """Partitions compartments across multiple bin interior footprints using backtracking shelf packing."""
        from pyboxbuilder.compartments.layout import pack_compartments_across_bins
        return pack_compartments_across_bins(compartments, bin_sizes, wall_spacing)

    def share_compartments(
        self,
        boxes: list[str],
        compartments: list[tuple[str, float, float, float]],
    ) -> None:
        """Registers a group of compartments to be dynamically partitioned across the given box labels."""
        self._shared_groups.append((boxes, compartments))
