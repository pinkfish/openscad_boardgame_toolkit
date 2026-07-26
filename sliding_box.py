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
from box_base import Box, BoxSpec, Contents, FingerHoleLocation, Label
from lids_base import (
    Lid,
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

        box = SlidingBox([50, 100, 20], "mybox")
        solid = box.make_box(
            contents=[InnerObject(divider), InnerObject(cavity)],
            finger_holes=[FingerHole(location=FingerHoleLocation.LEFT, offset=10),
                          FingerHole(location=FingerHoleLocation.RIGHT, offset=-5)])
        solid.show()

        lid = box.make_lid(Lid(lid_thickness=2, label=Label("Trains")))
        lid.show()
    """

    def __init__(self, spec: BoxSpec):
        # SlidingBox reads sliding_lid_options from the spec; fall back to plain defaults.
        self._sliding_lid_options = (
            spec.sliding_lid_options
            if spec.sliding_lid_options is not None
            else MakeSlidingLidOptions()
        )
        super().__init__(spec)

    # ------------------------------------------------------------------
    # make_box -- build the sliding-lid body then apply contents/fingerholes/MMU/positioning
    # ------------------------------------------------------------------

    def make_box(
        self,
        *,
        contents: "Contents | None" = None,
        finger_holes: "list | None" = None,
    ) -> Bosl2Solid:
        """Build the sliding-lid box body and apply contents, finger holes, MMU, positioning."""
        body = self._build_box_body()
        return self._finish_box(body, contents=contents, finger_holes=finger_holes)

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
                children=bosl2.masking.rounding_edge_mask(
                    radius=self.wall_thickness / 2, length=max(self.length, self.width)
                ),
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
            bosl2.masking.rounding_edge_mask(radius=self.wall_thickness / 4, height=self.length - self.wall_thickness * 2)
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
                radius=self.wall_thickness if two_layer else calc_lid_rounding,
                length=self.lid_thickness + self.size_spacing,
            ),
        )
        top_edges = [TOP] if two_layer else [TOP + BACK]
        main = main.edge_mask(
            top_edges,
            children=bosl2.masking.rounding_edge_mask(
                radius=self._top_cover if two_layer else calc_lid_rounding / 2,
                length=max(self._lid_length, self._lid_width),
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
                length=self.lid_thickness,
                radius=calc_lid_rounding,
            ).translate(
                [
                    self.wall_thickness - self._two_layer_chamfer,
                    self.wall_thickness,
                    -self._top_cover + self.lid_thickness / 2,
                ]
            )
            round_b = (
                bosl2.masking.rounding_edge_mask(length=self.lid_thickness, radius=calc_lid_rounding)
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

    def _make_base_lid(self, lid_rounding: float | None = None) -> Bosl2Solid:
        """Build the sliding-lid body."""
        return self._build_lid_body(lid_rounding=lid_rounding)

    def create_lid(self, lid: "Lid | None" = None) -> Bosl2Solid:
        """Override to set sliding-lid–specific fingernail dimensions and offsets."""
        l = lid if lid is not None else Lid(lid_thickness=self.lid_thickness)
        if l.fingernail:
            l.fingernail_width = l.fingernail_width or self._lid_fingernail_width
            l.fingernail_length = l.fingernail_length or self._lid_fingernail_length
            l.fingernail_x_offset = l.fingernail_x_offset or self.width / 2 - self.wall_thickness / 2
            l.fingernail_y_offset = l.fingernail_y_offset or self.length - self.wall_thickness - 3
        return Box.create_lid(self, l)

    def _lid_adjustment(self, stack: Bosl2Solid) -> Bosl2Solid:
        """Apply two-layer rotation/translation if needed."""
        if self._sliding_lid_options.two_layer:
            return stack.rotate([180, 0, 0]).translate([0, self._lid_length, self.lid_thickness])
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

        extra = list(extra_children) if extra_children else []
        return self.create_lid(
            Lid(
                lid_thickness=self.lid_thickness,
                lid_rounding=lid_rounding,
                shape_child=piece,
                shape_options=shape_options,
                layout_width=layout_width,
                aspect_ratio=aspect_ratio,
                boundary=lid_boundary,
                dense=calc_dense,
                dense_shape_edges=calc_dense_edges,
                material_colour=self.material_colour,
                inner_control=calc_inner_ctrl,
                fingernail=True,
                extra_children=extra,
            ),
        )

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
        label_kwargs: dict[str, object] = dict(material_colour=self.material_colour)
        if label_options is not None:
            for fld in ("text_scale", "text_length", "angle", "label_colour",
                        "label_background_colour", "short_length", "label_diff",
                        "border", "offset", "radius", "font", "full_height",
                        "finger_hole_size", "label_type", "solid_background"):
                v = getattr(label_options, fld)
                if v is not None:
                    label_kwargs[fld] = v
        if self._sliding_lid_options.two_layer:
            label_kwargs["full_height"] = True
        lbl = Label(text_str, **label_kwargs)
        label_shape_raw = self.make_label(lbl)
        _base = list(extra_children) if extra_children else []
        if label_shape_raw is not None:
            _base = [label_shape_raw] + _base

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
    calc_lid_thickness = lid_thickness or default_lid_thickness
    spec = BoxSpec(
        size=[size[0], size[1], calc_lid_thickness],
        label=f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        lid_thickness=calc_lid_thickness,
        material_colour=material_colour if material_colour is not None else default_material_colour,
        sliding_lid_options=sliding_lid_options,
    )
    box = SlidingBox(spec)
    lid = Lid(
        lid_thickness=calc_lid_thickness,
        lid_rounding=lid_rounding,
        extra_children=children,
    )
    return box.create_lid(lid)


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
    calc_lid_thickness = lid_thickness or default_lid_thickness
    spec = BoxSpec(
        size=[size[0], size[1], calc_lid_thickness],
        label=f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        lid_thickness=calc_lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    box = SlidingBox(spec)
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
    calc_lid_thickness = lid_thickness or default_lid_thickness
    spec = BoxSpec(
        size=[size[0], size[1], calc_lid_thickness],
        label=f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        lid_thickness=calc_lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    box = SlidingBox(spec)
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
    calc_lid_thickness = lid_thickness or default_lid_thickness
    spec = BoxSpec(
        size=[size[0], size[1], calc_lid_thickness],
        label=f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        lid_thickness=calc_lid_thickness,
        material_colour=material_colour if material_colour is not None else default_material_colour,
        sliding_lid_options=sliding_lid_options,
    )
    box = SlidingBox(spec)
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
    calc_lid_thickness = lid_thickness or default_lid_thickness
    spec = BoxSpec(
        size=[size[0], size[1], calc_lid_thickness],
        label=f"SlidingLid({size[0]},{size[1]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        lid_thickness=calc_lid_thickness,
        sliding_lid_options=sliding_lid_options,
    )
    box = SlidingBox(spec)
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
    # Translate the legacy children + parallel index-list contract into the
    # self-describing InnerObject model that make_box() now consumes.
    pos_only = set(positive_only_children or [])
    pos_neg = set(positive_negative_children or [])
    contents: list[InnerObject] = []
    for i, c in enumerate(children or []):
        if i in pos_only:
            obj_type = ObjectType.POSTIVE
        elif i in pos_neg:
            obj_type = ObjectType.POSTIVE_NEGATIVE
        else:
            obj_type = ObjectType.NEGATIVE
        contents.append(InnerObject(value=c, type=obj_type))

    spec = BoxSpec(
        size=size,
        label=f"SlidingBox({size[0]},{size[1]},{size[2]})",
        wall_thickness=wall_thickness if wall_thickness is not None else default_wall_thickness,
        floor_thickness=floor_thickness if floor_thickness is not None else default_floor_thickness,
        lid_thickness=lid_thickness if lid_thickness is not None else default_lid_thickness,
        material_colour=material_colour if material_colour is not None else default_material_colour,
        spin=spin,
        anchor=anchor,
        orient=orient,
        sliding_lid_options=sliding_lid_options,
        contents=contents if contents else None,
    )
    box = SlidingBox(spec)
    if positive_colour is not None:
        box.positive_colour = positive_colour
    return box.make_box()
