# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# LibFile: sliding_box.py
#    Sliding box pieces for the sliding boxes.
#
# FileSummary: Sliding box pieces for the sliding boxes.
# FileGroup: Boxes

from __future__ import annotations
import copy
import types

import numpy as np
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401

from base_bgtk import *
import bosl2.masking
import bosl2.shapes3d
import bosl2.transforms
from box_base import Box, FingerHoleLocation, LidConfig
from lids_base import (
    SlidingLidFingernail,
    IsDenseShapeType,
    DenseShapeEdges,
    default_lid_layout_width,
    default_lid_aspect_ratio,
)
from labels import LabelOptions, MakeLabelOptions
from shape_type import MakeShapeObject, ShapeObject, ShapeByType, ShapeNeedsInnerControl


def MakeSlidingLidOptions(
    two_layer: bool = False, two_layer_top_lid_ratio: float = 0.5, two_layer_vee_shape: bool = False
) -> types.SimpleNamespace:
    """Make the sliding lid options object.

    Args:
        two_layer: if the lid has a cap layer, a second layer on top (default False)
        two_layer_top_lid_ratio: ratio of the top bit to the sliding bit (default 0.5)
        two_layer_vee_shape: if the two-layer lid should use a vee slide (default False)
    """
    return types.SimpleNamespace(
        two_layer=two_layer, two_layer_top_lid_ratio=two_layer_top_lid_ratio, two_layer_vee_shape=two_layer_vee_shape
    )


class SlidingBox(Box):
    """A box with a sliding lid -- the dovetail chamfered lid slides in from the front.

    Usage::

        box = SlidingBox([50, 100, 20])
        box.create_box(children=[divider, cavity],
            finger_holes=[FingerHole(location=FingerHoleLocation.LEFT, offset=10),
                          FingerHole(location=FingerHoleLocation.RIGHT, offset=-5)])
        box.show()

        lid = box.create_lid(LidConfig(text="Trains"))
        lid.show()
    """

    def __init__(
        self,
        size: list[float],
        label: str,
        *,
        wall_thickness: float | None = None,
        floor_thickness: float | None = None,
        lid_thickness: float | None = None,
        material_colour: str | None = None,
        sliding_lid_options: types.SimpleNamespace | None = None,
    ):
        self._sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()
        super().__init__(
            size=size,
            label=label,
            wall_thickness=wall_thickness,
            floor_thickness=floor_thickness,
            lid_thickness=lid_thickness,
            material_colour=material_colour,
        )

    # ------------------------------------------------------------------
    # create_box -- build the sliding-lid body then apply children/fingerholes/MMU/positioning
    # ------------------------------------------------------------------

    def create_box(
        self,
        *,
        children: "list | None" = None,
        positive_only_children: list[int] | None = None,
        positive_negative_children: list[int] | None = None,
        finger_holes: "list | None" = None,
    ) -> Bosl2Solid:
        """Build the sliding-lid box body and apply children, finger holes, MMU, positioning."""
        body = self._build_box_body()
        return self._finish_box(
            body,
            children=children,
            positive_only_children=positive_only_children,
            positive_negative_children=positive_negative_children,
            finger_holes=finger_holes,
        )

    # ------------------------------------------------------------------
    # Sliding-lid-specific dimension derived values
    # ------------------------------------------------------------------

    @property
    def _top_cover(self) -> float:
        return self._sliding_lid_options.two_layer_top_lid_ratio * self.lid_thickness

    @property
    def _lid_cutout(self) -> float:
        return (self.lid_thickness - self._top_cover) if self._sliding_lid_options.two_layer else self.lid_thickness

    @property
    def _middle_chamfer(self) -> float:
        return self._lid_cutout / 2 if self.wall_thickness > self._lid_cutout else self.wall_thickness / 2

    @property
    def _chamfer(self) -> float:
        if self._sliding_lid_options.two_layer:
            return 0
        w2 = self.wall_thickness / 2
        gap = self.lid_thickness - self.size_spacing
        return w2 if w2 > gap else gap

    @property
    def _two_layer_chamfer(self) -> float:
        if self._sliding_lid_options.two_layer_vee_shape:
            return self._middle_chamfer
        w2 = self.wall_thickness / 2
        return w2 if w2 < self._lid_cutout else self._lid_cutout

    @property
    def _lid_width(self) -> float:
        if self._sliding_lid_options.two_layer:
            return self.width
        return self.width - 2 * self.wall_thickness + self._chamfer * 2 + self.size_spacing

    @property
    def _lid_length(self) -> float:
        if self._sliding_lid_options.two_layer:
            return self.length
        return self.length - self.wall_thickness + self._chamfer - self.size_spacing

    def _effective_height(self) -> float:
        return (
            (self.height - self._top_cover - self.size_spacing) if self._sliding_lid_options.two_layer else self.height
        )

    @property
    def inner_height(self) -> float:
        h = self._effective_height() - self._lid_cutout - self.floor_thickness
        return max(h, 0)

    # Lid-specific inner-area dimensions
    @property
    def _lid_area_width(self) -> float:
        return self.width - self.wall_thickness

    @property
    def _lid_area_length(self) -> float:
        return self.length - self.wall_thickness / 2

    @property
    def _lid_fingernail_width(self) -> float:
        return self.width - self.wall_thickness

    @property
    def _lid_fingernail_length(self) -> float:
        return self.length - self.wall_thickness

    # ------------------------------------------------------------------
    # Box body
    # ------------------------------------------------------------------

    def _build_box_body(self) -> Bosl2Solid:
        calc_height = self._effective_height()
        two_layer = self._sliding_lid_options.two_layer

        body = bosl2.shapes3d.cuboid(
            [self.width, self.length, calc_height],
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        if not two_layer:
            body = body.edge_mask(
                [TOP],
                children=bosl2.masking.rounding_edge_mask(r=self.wall_thickness / 2, l=max(self.length, self.width)),
            )

        rounding_offset = 0.01
        mid_cut = bosl2.shapes3d.cuboid(
            [
                self.width - self.wall_thickness * 2,
                self.length - self.wall_thickness + self.size_spacing + rounding_offset,
                self._lid_cutout + self.size_spacing / 2,
            ],
        ).translate([self.wall_thickness, -rounding_offset, calc_height - self._lid_cutout])
        body = body - mid_cut

        chamfer2 = self.wall_thickness / 2 if self.wall_thickness / 2 < self._lid_cutout else self._lid_cutout
        if two_layer:
            if self._sliding_lid_options.two_layer_vee_shape:
                lid_cut = bosl2.shapes3d.cuboid(
                    [
                        self.width - self.wall_thickness * 2 + self._middle_chamfer * 2 + self.size_spacing,
                        self.length - self.wall_thickness,
                        self._lid_cutout,
                    ],
                    chamfer=self._middle_chamfer,
                    edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + LEFT, BOTTOM + RIGHT],
                ).translate(
                    [
                        self.wall_thickness - self._middle_chamfer - self.size_spacing / 2,
                        0,
                        calc_height - self._lid_cutout,
                    ]
                )
            else:
                lid_cut = bosl2.shapes3d.cuboid(
                    [
                        self.width - self.wall_thickness * 2 + chamfer2 * 2 + self.size_spacing,
                        self.length - self.wall_thickness,
                        self._lid_cutout,
                    ],
                    chamfer=chamfer2,
                    edges=[TOP + LEFT, TOP + RIGHT],
                ).translate([self.wall_thickness - chamfer2 - self.size_spacing / 2, 0, calc_height - self._lid_cutout])
        else:
            lid_cut = bosl2.shapes3d.cuboid(
                [
                    self.width - self.wall_thickness * 2 + chamfer2 * 2,
                    self.length - self.wall_thickness + chamfer2,
                    self._lid_cutout,
                ],
                chamfer=chamfer2,
                edges=[TOP + LEFT, TOP + RIGHT, TOP + BACK],
            ).translate([self.wall_thickness - chamfer2, 0, calc_height - self._lid_cutout])
        body = body - lid_cut

        edge_round = (
            bosl2.masking.rounding_edge_mask(r=self.wall_thickness / 4, h=self.length - self.wall_thickness * 2)
            .rotate([0, 90, 0])
            .translate([self.width / 2, 0, calc_height - self._lid_cutout])
        )
        body = body - edge_round

        return body.color(self.material_colour)

    # ------------------------------------------------------------------
    # Inside mask
    # ------------------------------------------------------------------

    def inside_mask(self) -> Bosl2Solid:
        return bosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height],
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    # ------------------------------------------------------------------
    # Lid creation
    # ------------------------------------------------------------------

    def _build_lid_body(self, lid_rounding: float | None = None) -> Bosl2Solid:
        calc_lid_rounding = lid_rounding if lid_rounding is not None else self.wall_thickness / 2
        two_layer = self._sliding_lid_options.two_layer

        edges = (
            [LEFT + TOP, RIGHT + TOP, TOP + FRONT, LEFT + BOTTOM, RIGHT + BOTTOM, BOTTOM + FRONT]
            if two_layer
            else [LEFT + TOP, RIGHT + TOP, TOP + FRONT]
        )
        main = bosl2.shapes3d.cuboid(
            [self._lid_width, self._lid_length, self.lid_thickness],
            chamfer=self._chamfer + self.size_spacing,
            edges=edges,
        )
        main = main.edge_mask(
            [LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
            children=bosl2.masking.rounding_edge_mask(
                r=self.wall_thickness if two_layer else calc_lid_rounding,
                l=self.lid_thickness + self.size_spacing,
            ),
        )
        top_edges = [TOP] if two_layer else [TOP + BACK]
        main = main.edge_mask(
            top_edges,
            children=bosl2.masking.rounding_edge_mask(
                r=self._top_cover if two_layer else calc_lid_rounding / 2,
                l=max(self._lid_length, self._lid_width),
            ),
        )

        if two_layer:
            profile = np.asarray(self._mask_2sliding_lid(), dtype=float)
            mirrored_profile = profile * np.array([-1.0, 1.0])
            run_length = self._lid_length + 0.1
            cutter_left = (
                polygon([[float(u), float(v)] for u, v in mirrored_profile])
                .linear_extrude(height=run_length, center=True)
                .rotate(180, [0, 1, 1])
                .translate([0, self._lid_length / 2, 0])
            )
            cutter_right = (
                polygon([[float(u), float(v)] for u, v in profile])
                .linear_extrude(height=run_length, center=True)
                .rotate(180, [0, 1, 1])
                .translate([self._lid_width, self._lid_length / 2, 0])
            )
            main = main - cutter_left - cutter_right

        if two_layer:
            front_cut = bosl2.shapes3d.cuboid(
                [self._lid_width, self.wall_thickness, self._lid_cutout + self.size_spacing],
            ).translate([0, 0, -self.size_spacing])
            main = main - front_cut
            round_a = bosl2.masking.rounding_edge_mask(
                l=self.lid_thickness,
                r=calc_lid_rounding,
            ).translate(
                [
                    self.wall_thickness - self._two_layer_chamfer,
                    self.wall_thickness,
                    -self._top_cover + self.lid_thickness / 2,
                ]
            )
            round_b = (
                bosl2.masking.rounding_edge_mask(l=self.lid_thickness, r=calc_lid_rounding)
                .rotate([0, 180, 0])
                .translate(
                    [
                        self._lid_width - self.wall_thickness + self._two_layer_chamfer,
                        self.wall_thickness,
                        -self._top_cover + self.lid_thickness / 2,
                    ]
                )
            )
            main = main - round_a - round_b
        else:
            tri_h = self.lid_thickness + 10
            tri_z = -self.lid_thickness / 2 + tri_h / 2
            tri_a = (
                polygon([[self.wall_thickness / 2, 0], [0, 0], [0, 15]])
                .linear_extrude(height=tri_h, center=True)
                .translate([-self.size_spacing / 20, -self.size_spacing, tri_z])
            )
            tri_b = (
                polygon([[-self.wall_thickness / 2, 0], [0, 0], [0, 15]])
                .linear_extrude(height=tri_h, center=True)
                .translate([self._lid_width + self.size_spacing / 20, -self.size_spacing, tri_z])
            )
            main = main - tri_a - tri_b

        return main.color(self.material_colour).right(self.width / 2).back(self.length / 2).up(self.height / 2)

    def _mask_2sliding_lid(self) -> list[list[float]]:
        if self._sliding_lid_options.two_layer_vee_shape:
            return [
                [0, 0],
                [self.wall_thickness / 2 + self.size_spacing, 0],
                [self.wall_thickness / 2 + self._middle_chamfer + self.size_spacing, self._middle_chamfer],
                [self.wall_thickness / 2 + self.size_spacing, self._lid_cutout],
                [0, self._lid_cutout],
            ]
        else:
            return [
                [0, 0],
                [self.size_spacing, 0],
                [self.wall_thickness - self._two_layer_chamfer, 0],
                [self.wall_thickness, self._lid_cutout],
                [self.size_spacing, self._lid_cutout],
                [0, self._lid_cutout],
            ]

    def create_lid(
        self, config: LidConfig | None = None, *, lid_rounding: float | None = None, extra_children: list | None = None
    ) -> Bosl2Solid:
        """Create a sliding lid.

        Can be called with a :class:`~box_base.LidConfig` for full control, or with
        *lid_rounding* + *extra_children* for backward compatibility.

        Args:
            config: :class:`~box_base.LidConfig`
            lid_rounding: rounding on lid edges (default wall_thickness/2). Backward-compat.
            extra_children: extra solids/callables to embed in the lid. Backward-compat.
        """
        if config is not None:
            return self._create_lid_from_config(config)

        # Backward-compatible path: match old create_lid(lid_rounding, extra_children) exactly
        main = self._build_lid_body(lid_rounding=lid_rounding)
        inner_w = self.width - self.wall_thickness
        inner_l = self.length - self.wall_thickness / 2
        kids = list(extra_children) if extra_children else []
        resolved_kids = [(c(inner_w, inner_l) if callable(c) else c) for c in kids]

        from lids_base import internal_build_lid

        stack = internal_build_lid(
            lid_thickness=self.lid_thickness,
            children=[main] + resolved_kids,
            size_spacing=self.size_spacing,
        )
        if self._sliding_lid_options.two_layer:
            stack = stack.rotate([180, 0, 0]).translate([0, self._lid_length, self.lid_thickness])
        return stack

    def _create_lid_from_config(self, cfg: LidConfig) -> Bosl2Solid:
        # -- build lid body --------------------------------------------------
        main = self._build_lid_body(lid_rounding=cfg.lid_rounding)

        # -- collect overlay children ----------------------------------------
        overlay = []

        if cfg.fingernail:
            fn = (
                bosl2.shapes3d.cuboid(
                    [self._lid_fingernail_width, self._lid_fingernail_length, self.lid_thickness],
                ).color(self.material_colour)
                & SlidingLidFingernail(
                    self.lid_thickness,
                    material_colour=self.material_colour,
                )
                .translate([self.width / 2 - self.wall_thickness / 2, self.length - self.wall_thickness - 3, 0])
                .shape
            )
            overlay.append(fn)

        if cfg.shape_child is not None or cfg.shape_options is not None:
            piece = cfg.shape_child
            so = cfg.shape_options if cfg.shape_options is not None else MakeShapeObject()
            if piece is None:
                piece = ShapeByType(options=so).color(self.material_colour)

            mesh = self._shape_fill(
                shape_child=piece,
                shape_options=so,
                width=self._lid_area_width,
                length=self._lid_area_length,
                lid_thickness=self.lid_thickness,
                boundary=cfg.lid_boundary,
            )
            overlay.append(mesh)

        if cfg.text is not None:
            label_opts_copy = (
                copy.copy(cfg.label_options)
                if cfg.label_options
                else MakeLabelOptions(material_colour=self.material_colour)
            )
            label_opts_copy.full_height = self._sliding_lid_options.two_layer

            from lids_base import MakeLidLabel

            label_shape = MakeLidLabel(
                size=[self.inner_width, self.inner_length],
                lid_thickness=self.lid_thickness,
                text_str=cfg.text,
                options=label_opts_copy,
            )
            if label_shape is not None:
                overlay.append(label_shape.translate([self.wall_thickness / 2, self.wall_thickness / 2, 0]))

        if cfg.extra_children:
            overlay.extend(cfg.extra_children)

        # -- assemble --------------------------------------------------------
        inner_w = self.width - self.wall_thickness
        inner_l = self.length - self.wall_thickness / 2
        resolved = [(c(inner_w, inner_l) if callable(c) else c) for c in overlay]

        from lids_base import internal_build_lid

        stack = internal_build_lid(
            lid_thickness=self.lid_thickness,
            children=[main] + resolved,
        )
        if self._sliding_lid_options.two_layer:
            stack = stack.rotate([180, 0, 0]).translate([0, self._lid_length, self.lid_thickness])
        return stack

    # ------------------------------------------------------------------
    # Backward-compatible lid-shorthand methods
    # ------------------------------------------------------------------

    def create_lid_with_shape(
        self,
        shape_child: Bosl2Solid | None = None,
        shape_options: ShapeObject | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_rounding: float | None = None,
        lid_pattern_dense: bool = False,
        lid_dense_shape_edges: int = 6,
        pattern_inner_control: int = 0,
        extra_children: list | None = None,
    ) -> Bosl2Solid:
        if shape_child is None:
            if shape_options is None:
                shape_options = MakeShapeObject()
            piece = ShapeByType(options=shape_options).color(self.material_colour)
        else:
            piece = shape_child

        so = shape_options if shape_options is not None else MakeShapeObject()
        calc_dense = lid_pattern_dense if lid_pattern_dense else IsDenseShapeType(so.shape_type)
        calc_dense_edges = DenseShapeEdges(so.shape_type) if not lid_pattern_dense else lid_dense_shape_edges
        calc_inner_ctrl = ShapeNeedsInnerControl(so.shape_type) if not lid_pattern_dense else pattern_inner_control

        from lids_base import LidMeshBasic

        mesh = LidMeshBasic(
            size=[self._lid_area_width, self._lid_area_length],
            lid_thickness=self.lid_thickness,
            boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio if aspect_ratio is not None else default_lid_aspect_ratio,
            dense=calc_dense,
            dense_shape_edges=calc_dense_edges,
            material_colour=self.material_colour,
            inner_control=calc_inner_ctrl,
            children=piece,
        )

        fingernail = (
            bosl2.shapes3d.cuboid(
                [self._lid_fingernail_width, self._lid_fingernail_length, self.lid_thickness],
                anchor=BOTTOM + FRONT + LEFT,
            ).color(self.material_colour)
            & SlidingLidFingernail(
                self.lid_thickness,
                material_colour=self.material_colour,
            )
            .translate([self.width / 2 - self.wall_thickness / 2, self.length - self.wall_thickness - 3, 0])
            .shape
        )

        extra = list(extra_children) if extra_children else []
        return self.create_lid(lid_rounding=lid_rounding, extra_children=[fingernail, mesh] + extra)

    def create_lid_with_label(
        self,
        text_str: str,
        shape_options: ShapeObject | None = None,
        label_options: LabelOptions | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_rounding: float | None = None,
        extra_children: list | None = None,
    ) -> Bosl2Solid:
        so = shape_options if shape_options is not None else MakeShapeObject()
        piece = ShapeByType(options=so)
        assert piece is not None
        shape_child = piece.color(self.material_colour).translate([lid_boundary, lid_boundary, 0])

        return self.create_lid_with_label_and_shape(
            text_str=text_str,
            shape_child=shape_child,
            label_options=label_options,
            lid_boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio,
            lid_rounding=lid_rounding,
            lid_pattern_dense=IsDenseShapeType(so.shape_type),
            lid_dense_shape_edges=DenseShapeEdges(so.shape_type),
            pattern_inner_control=ShapeNeedsInnerControl(so.shape_type),
            extra_children=extra_children,
        )

    def create_lid_with_label_and_shape(
        self,
        text_str: str,
        shape_child: Bosl2Solid,
        label_options: LabelOptions | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_rounding: float | None = None,
        lid_pattern_dense: bool = False,
        lid_dense_shape_edges: int = 6,
        pattern_inner_control: int = 0,
        extra_children: list | None = None,
    ) -> Bosl2Solid:
        calc_label_options = (
            label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
        )
        label_opts = copy.copy(calc_label_options)
        label_opts.full_height = self._sliding_lid_options.two_layer

        from lids_base import MakeLidLabel

        label_shape_raw = MakeLidLabel(
            size=[self.inner_width, self.inner_length],
            lid_thickness=self.lid_thickness,
            text_str=text_str,
            options=label_opts,
        )
        _base = list(extra_children) if extra_children else []
        if label_shape_raw is not None:
            _base = [label_shape_raw.translate([self.wall_thickness / 2, self.wall_thickness / 2, 0])] + _base

        return self.create_lid_with_shape(
            shape_child=shape_child,
            lid_boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio,
            lid_rounding=lid_rounding,
            lid_pattern_dense=lid_pattern_dense,
            lid_dense_shape_edges=lid_dense_shape_edges,
            pattern_inner_control=pattern_inner_control,
            extra_children=_base,
        )


# ---------------------------------------------------------------------------
# Backward-compatible module-level functions (delegate to SlidingBox)
# ---------------------------------------------------------------------------


def SlidingLid(
    size: list[float],
    children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_thickness: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
) -> PyOpenSCAD:
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    cfg = LidConfig(lid_rounding=lid_rounding, extra_children=children)
    return box.create_lid(cfg)


def SlidingBoxLidWithCustomShape(
    size: list[float],
    shape_child: PyOpenSCAD | None = None,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    lid_rounding: float | None = None,
    wall_thickness: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
) -> PyOpenSCAD:
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_lid_with_shape(
        shape_child=shape_child,
        lid_boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_pattern_dense=lid_pattern_dense,
        lid_dense_shape_edges=lid_dense_shape_edges,
        pattern_inner_control=pattern_inner_control,
        extra_children=extra_children,
    )


def SlidingBoxLidWithLabelAndCustomShape(
    size: list[float],
    text_str: str,
    shape_child: PyOpenSCAD,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    size_spacing: float | None = None,
    lid_thickness: float | None = None,
    aspect_ratio: float | None = 1.0,
    wall_thickness: float | None = None,
    lid_rounding: float | None = None,
    lid_pattern_dense: bool = False,
    lid_dense_shape_edges: int = 6,
    material_colour: str | None = None,
    pattern_inner_control: int = False,
    label_options: LabelOptions | None = None,
) -> PyOpenSCAD:
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_lid_with_label_and_shape(
        text_str=text_str,
        shape_child=shape_child,
        label_options=label_options,
        lid_boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        lid_pattern_dense=lid_pattern_dense,
        lid_dense_shape_edges=lid_dense_shape_edges,
        pattern_inner_control=pattern_inner_control,
        extra_children=extra_children,
    )


def SlidingBoxLidWithLabel(
    size: list[float],
    text_str: str,
    extra_children: "list | None" = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    lid_thickness: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    aspect_ratio: float | None = None,
    wall_thickness: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    label_options: LabelOptions | None = None,
    shape_options: ShapeObject | None = None,
) -> PyOpenSCAD:
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_lid_with_label(
        text_str=text_str,
        shape_options=shape_options,
        label_options=label_options,
        lid_boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        extra_children=extra_children,
    )


def SlidingBoxLidWithShape(
    size: list[float],
    extra_children: "list | None" = None,
    lid_thickness: float | None = None,
    lid_boundary: float = 10,
    layout_width: float | None = None,
    wall_thickness: float | None = None,
    aspect_ratio: float | None = None,
    size_spacing: float | None = None,
    lid_rounding: float | None = None,
    material_colour: str | None = None,
    shape_options: ShapeObject | None = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
) -> PyOpenSCAD:
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_lid_with_shape(
        shape_options=shape_options,
        lid_boundary=lid_boundary,
        layout_width=layout_width,
        aspect_ratio=aspect_ratio,
        lid_rounding=lid_rounding,
        extra_children=extra_children,
    )


def MakeBoxWithSlidingLid(
    size: list[float],
    children: "list | None" = None,
    wall_thickness: float | None = None,
    lid_thickness: float | None = None,
    floor_thickness: float | None = None,
    size_spacing: float | None = None,
    material_colour: str | None = None,
    positive_colour: str | None = None,
    sliding_lid_options: types.SimpleNamespace | None = None,
    positive_only_children: list[int] | None = None,
    positive_negative_children: list[int] | None = None,
    spin: float = 0,
    anchor: list[int] | None = None,
    orient: list[float] | None = None,
) -> PyOpenSCAD:
    box = SlidingBox(
        size=size,
        label=f"SlidingBox({size[0]},{size[1]},{size[2]})",
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_box(
        children=children,
        positive_only_children=positive_only_children,
        positive_negative_children=positive_negative_children,
    )
