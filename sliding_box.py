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
from box_base import Box, FingerHoleLocation
from lids_base import SlidingLidFingernail, IsDenseShapeType, DenseShapeEdges, default_lid_layout_width, default_lid_aspect_ratio
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
        box.show()
        box.create_lid().show()

        # Finger holes on left and right sides:
        box = SlidingBox([50, 100, 30],
            finger_holes=[(FingerHoleLocation.LEFT, 10),
                          (FingerHoleLocation.RIGHT, -5)])
    """

    def __init__(
        self,
        size: list[float],
        *,
        wall_thickness: float | None = None,
        floor_thickness: float | None = None,
        lid_thickness: float | None = None,
        size_spacing: float | None = None,
        material_colour: str | None = None,
        positive_colour: str | None = None,
        children: "list | None" = None,
        positive_only_children: list[int] | None = None,
        positive_negative_children: list[int] | None = None,
        spin: float = 0,
        anchor: list[int] | None = None,
        orient: list[float] | None = None,
        finger_holes: list[tuple[FingerHoleLocation, float]] | None = None,
        finger_hole_radius: float | None = None,
        finger_hole_height: float | None = None,
        finger_hole_depth: float | None = None,
        finger_hole_rounding_radius: float | None = None,
        finger_hole_rounding_edge: float = 0,
        sliding_lid_options: types.SimpleNamespace | None = None,
    ):
        self._sliding_lid_options = sliding_lid_options if sliding_lid_options is not None else MakeSlidingLidOptions()
        super().__init__(
            size=size,
            wall_thickness=wall_thickness,
            floor_thickness=floor_thickness,
            lid_thickness=lid_thickness,
            size_spacing=size_spacing,
            material_colour=material_colour,
            positive_colour=positive_colour,
            children=children,
            positive_only_children=positive_only_children,
            positive_negative_children=positive_negative_children,
            spin=spin, anchor=anchor, orient=orient,
            finger_holes=finger_holes,
            finger_hole_radius=finger_hole_radius,
            finger_hole_height=finger_hole_height,
            finger_hole_depth=finger_hole_depth,
            finger_hole_rounding_radius=finger_hole_rounding_radius,
            finger_hole_rounding_edge=finger_hole_rounding_edge,
        )

    # ------------------------------------------------------------------
    # Sliding-lid–specific dimension derived values
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
        return (self.height - self._top_cover - self.size_spacing) if self._sliding_lid_options.two_layer else self.height

    @property
    def inner_height(self) -> float:
        h = self._effective_height() - self._lid_cutout - self.floor_thickness
        return max(h, 0)

    # ------------------------------------------------------------------
    # Box body
    # ------------------------------------------------------------------

    def _build_box_body(self) -> "PyOpenSCAD":
        calc_height = self._effective_height()
        two_layer = self._sliding_lid_options.two_layer

        body = bosl2.shapes3d.cuboid(
            [self.width, self.length, calc_height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        if not two_layer:
            body = body.edge_mask(
                [TOP], children=bosl2.masking.rounding_edge_mask(r=self.wall_thickness / 2, l=max(self.length, self.width))
            )

        rounding_offset = 0.01
        mid_cut = bosl2.shapes3d.cuboid(
            [
                self.width - self.wall_thickness * 2,
                self.length - self.wall_thickness + self.size_spacing + rounding_offset,
                self._lid_cutout + self.size_spacing / 2,
            ],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, -rounding_offset, calc_height - self._lid_cutout])
        body = body - mid_cut

        chamfer2 = (
            self.wall_thickness / 2 if self.wall_thickness / 2 < self._lid_cutout else self._lid_cutout
        )
        if two_layer:
            if self._sliding_lid_options.two_layer_vee_shape:
                lid_cut = bosl2.shapes3d.cuboid(
                    [
                        self.width - self.wall_thickness * 2 + self._middle_chamfer * 2 + self.size_spacing,
                        self.length - self.wall_thickness,
                        self._lid_cutout,
                    ],
                    anchor=BOTTOM + FRONT + LEFT,
                    chamfer=self._middle_chamfer,
                    edges=[TOP + LEFT, TOP + RIGHT, BOTTOM + LEFT, BOTTOM + RIGHT],
                ).translate([self.wall_thickness - self._middle_chamfer - self.size_spacing / 2, 0, calc_height - self._lid_cutout])
            else:
                lid_cut = bosl2.shapes3d.cuboid(
                    [
                        self.width - self.wall_thickness * 2 + chamfer2 * 2 + self.size_spacing,
                        self.length - self.wall_thickness,
                        self._lid_cutout,
                    ],
                    anchor=BOTTOM + FRONT + LEFT,
                    chamfer=chamfer2,
                    edges=[TOP + LEFT, TOP + RIGHT],
                ).translate([self.wall_thickness - chamfer2 - self.size_spacing / 2, 0, calc_height - self._lid_cutout])
        else:
            lid_cut = bosl2.shapes3d.cuboid(
                [self.width - self.wall_thickness * 2 + chamfer2 * 2, self.length - self.wall_thickness + chamfer2, self._lid_cutout],
                anchor=BOTTOM + FRONT + LEFT,
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
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, self.wall_thickness, self.floor_thickness])

    # ------------------------------------------------------------------
    # Lid creation
    # ------------------------------------------------------------------

    def _build_lid_body(self, lid_rounding: float | None = None) -> "PyOpenSCAD":
        """Build the raw sliding-lid solid (chamfered dovetail body, no children/patterns)."""
        calc_lid_rounding = lid_rounding if lid_rounding is not None else self.wall_thickness / 2
        two_layer = self._sliding_lid_options.two_layer

        edges = (
            [LEFT + TOP, RIGHT + TOP, TOP + FRONT, LEFT + BOTTOM, RIGHT + BOTTOM, BOTTOM + FRONT]
            if two_layer
            else [LEFT + TOP, RIGHT + TOP, TOP + FRONT]
        )
        main = bosl2.shapes3d.cuboid(
            [self._lid_width, self._lid_length, self.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
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
                anchor=BOTTOM + FRONT + LEFT,
            ).translate([0, 0, -self.size_spacing])
            main = main - front_cut
            round_a = bosl2.masking.rounding_edge_mask(
                l=self.lid_thickness, r=calc_lid_rounding,
            ).translate(
                [self.wall_thickness - self._two_layer_chamfer, self.wall_thickness,
                 -self._top_cover + self.lid_thickness / 2]
            )
            round_b = (
                bosl2.masking.rounding_edge_mask(l=self.lid_thickness, r=calc_lid_rounding)
                .rotate([0, 180, 0])
                .translate(
                    [self._lid_width - self.wall_thickness + self._two_layer_chamfer,
                     self.wall_thickness, -self._top_cover + self.lid_thickness / 2]
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

        return main.color(self.material_colour)

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
        self,
        lid_rounding: float | None = None,
        extra_children: list | None = None,
    ) -> "PyOpenSCAD":
        """Create a plain sliding lid (no patterns, no label).

        Args:
            lid_rounding: rounding on lid edges (default wall_thickness/2)
            extra_children: extra solids/callables to embed in the lid
        """
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

    # Lid-specific inner-area dimensions (sliding lid has single-wall offsets on
    # the width sides and a half-wall offset on the front).
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

    def create_lid_with_shape(
        self,
        shape_child: "PyOpenSCAD | None" = None,
        shape_options: ShapeObject | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_rounding: float | None = None,
        lid_pattern_dense: bool = False,
        lid_dense_shape_edges: int = 6,
        pattern_inner_control: int = 0,
        extra_children: list | None = None,
    ) -> "PyOpenSCAD":
        """Lid with a repeating shape pattern.

        Provide either *shape_child* directly or *shape_options* to auto-resolve it.
        """
        if shape_child is None:
            if shape_options is None:
                shape_options = MakeShapeObject()
            piece = ShapeByType(options=shape_options).color(self.material_colour)
        else:
            piece = shape_child

        from lids_base import LidMeshBasic
        mesh = LidMeshBasic(
            size=[self._lid_area_width, self._lid_area_length],
            lid_thickness=self.lid_thickness,
            boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio if aspect_ratio is not None else default_lid_aspect_ratio,
            dense=lid_pattern_dense,
            dense_shape_edges=lid_dense_shape_edges,
            material_colour=self.material_colour,
            inner_control=pattern_inner_control,
            children=piece,
        )

        fingernail = bosl2.shapes3d.cuboid(
            [self._lid_fingernail_width, self._lid_fingernail_length, self.lid_thickness],
            anchor=BOTTOM + FRONT + LEFT,
        ).color(self.material_colour) & SlidingLidFingernail(
            self.lid_thickness, material_colour=self.material_colour,
        ).translate([self.width / 2 - self.wall_thickness / 2, self.length - self.wall_thickness - 3, 0]).shape

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
    ) -> "PyOpenSCAD":
        """Lid with a label and auto-resolved shape pattern."""
        calc_shape_options = shape_options if shape_options is not None else MakeShapeObject()
        piece = ShapeByType(options=calc_shape_options)
        assert piece is not None, "shape_options must not resolve to ShapeType.NONE"
        shape_child = piece.color(self.material_colour).translate([lid_boundary, lid_boundary, 0])

        return self.create_lid_with_label_and_shape(
            text_str=text_str,
            shape_child=shape_child,
            label_options=label_options,
            lid_boundary=lid_boundary,
            layout_width=layout_width,
            aspect_ratio=aspect_ratio,
            lid_rounding=lid_rounding,
            lid_pattern_dense=IsDenseShapeType(calc_shape_options.shape_type),
            lid_dense_shape_edges=DenseShapeEdges(calc_shape_options.shape_type),
            pattern_inner_control=ShapeNeedsInnerControl(calc_shape_options.shape_type),
            extra_children=extra_children,
        )

    def create_lid_with_label_and_shape(
        self,
        text_str: str,
        shape_child: "PyOpenSCAD",
        label_options: LabelOptions | None = None,
        lid_boundary: float = 10,
        layout_width: float | None = None,
        aspect_ratio: float | None = None,
        lid_rounding: float | None = None,
        lid_pattern_dense: bool = False,
        lid_dense_shape_edges: int = 6,
        pattern_inner_control: int = 0,
        extra_children: list | None = None,
    ) -> "PyOpenSCAD":
        """Lid with a label and explicit *shape_child* pattern."""
        calc_label_options = label_options if label_options is not None else MakeLabelOptions(material_colour=self.material_colour)
        label_opts = copy.copy(calc_label_options)
        label_opts.full_height = self._sliding_lid_options.two_layer

        from lids_base import MakeLidLabel
        label_shape_raw = MakeLidLabel(
            size=[self.inner_width, self.inner_length],
            lid_thickness=self.lid_thickness,
            text_str=text_str, options=label_opts,
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
    """Creates a sliding lid for a sliding lid box. (Compatibility wrapper.)

    Usage::
        SlidingLid(size=[10, 30], lid_thickness=3, wall_thickness=2, size_spacing=0.2)
    """
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
        sliding_lid_options=sliding_lid_options,
    )
    return box.create_lid(lid_rounding=lid_rounding, extra_children=children)


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
    """Lid for a sliding lid box. (Compatibility wrapper.)"""
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
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
    """Lid for a sliding lid box, with a repeating pattern and a label. (Compatibility wrapper.)"""
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
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
    """Composite lid: a sliding lid box with a label and a pattern. (Compatibility wrapper.)"""
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
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
    """Composite lid: a sliding lid box with an automatic pattern. (Compatibility wrapper.)"""
    box = SlidingBox(
        [size[0], size[1], lid_thickness or default_lid_thickness],
        wall_thickness=wall_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
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
    """Makes a box with a sliding lid. (Compatibility wrapper.)

    Usage::
        MakeBoxWithSlidingLid([50, 100, 20])
    """
    box = SlidingBox(
        size=size,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        size_spacing=size_spacing,
        material_colour=material_colour,
        positive_colour=positive_colour,
        children=children,
        positive_only_children=positive_only_children,
        positive_negative_children=positive_negative_children,
        spin=spin, anchor=anchor, orient=orient,
        sliding_lid_options=sliding_lid_options,
    )
    return box.shape
