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
from dataclasses import replace

import numpy as np
from pythonscad import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openscad import PyOpenSCAD  # noqa: F401

from base_bgtk import *
import pybosl2.masking
import pybosl2.shapes3d
import pybosl2.transforms
from pybosl2 import shapes2d
from box_base import BoxBaseType, BoxSpec, Contents, FingerHoleLocation, Label
from lids_base import (
    Lid,
    SlidingLidFingernail,
    IsDenseShapeType,
    DenseShapeEdges,
    default_lid_layout_width,
    default_lid_aspect_ratio,
)
from labels import LabelOptions
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


class SlidingBox(BoxBaseType):
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
        # Sliding-lid params come from the generic type_options slot (a MakeSlidingLidOptions()),
        # or plain sliding defaults when unset.
        self._sliding_lid_options = spec.type_options if spec.type_options is not None else MakeSlidingLidOptions()
        super().__init__(spec)

    # make_box() is inherited from BoxBaseType (build _build_box_body(), then the
    # shared _finish_box pipeline) -- SlidingBox only customises _build_box_body().

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

        # Corner-anchored (BOTTOM+FRONT+LEFT) like every other box body -- the whole
        # pipeline (inside_mask, _placed_content, contents) is corner-framed, and the lid
        # cuts below are positioned from the corner too. A CENTER-anchored body (the pybosl2
        # cuboid default) left contents/mask overlapping only one quadrant.
        body = pybosl2.shapes3d.cuboid(
            [self.width, self.length, calc_height],
            anchor=BOTTOM + FRONT + LEFT,
            rounding=self.wall_thickness,
            edges=[LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK, BOT],
        )
        if not two_layer:
            body = body.edge_mask(
                [TOP],
                children=pybosl2.masking.rounding_edge_mask(
                    radius=self.wall_thickness / 2, length=max(self.length, self.width)
                ),
            )

        rounding_offset = 0.01
        mid_cut = pybosl2.shapes3d.cuboid(
            [
                self.width - self.wall_thickness * 2,
                self.length - self.wall_thickness + self.size_spacing + rounding_offset,
                self._lid_cutout + self.size_spacing / 2,
            ],
            anchor=BOTTOM + FRONT + LEFT,
        ).translate([self.wall_thickness, -rounding_offset, calc_height - self._lid_cutout])
        body = body - mid_cut

        chamfer2 = self.wall_thickness / 2 if self.wall_thickness / 2 < self._lid_cutout else self._lid_cutout
        if two_layer:
            if self._sliding_lid_options.two_layer_vee_shape:
                lid_cut = pybosl2.shapes3d.cuboid(
                    [
                        self.width - self.wall_thickness * 2 + self._middle_chamfer * 2 + self.size_spacing,
                        self.length - self.wall_thickness,
                        self._lid_cutout,
                    ],
                    anchor=BOTTOM + FRONT + LEFT,
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
                lid_cut = pybosl2.shapes3d.cuboid(
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
            lid_cut = pybosl2.shapes3d.cuboid(
                [
                    self.width - self.wall_thickness * 2 + chamfer2 * 2,
                    self.length - self.wall_thickness + chamfer2,
                    self._lid_cutout,
                ],
                anchor=BOTTOM + FRONT + LEFT,
                chamfer=chamfer2,
                edges=[TOP + LEFT, TOP + RIGHT, TOP + BACK],
            ).translate([self.wall_thickness - chamfer2, 0, calc_height - self._lid_cutout])
        body = body - lid_cut

        edge_round = (
            pybosl2.masking.rounding_edge_mask(radius=self.wall_thickness / 4, height=self.length - self.wall_thickness * 2)
            .rotate([0, 90, 0])
            .translate([self.width / 2, 0, calc_height - self._lid_cutout])
        )
        body = body - edge_round

        return body.color(self.material_colour)

    # ------------------------------------------------------------------
    # Inside mask
    # ------------------------------------------------------------------

    def inside_mask(self) -> Bosl2Solid:
        # anchor=BOTTOM+FRONT+LEFT so the mask is corner-anchored at the interior origin
        # (matching the base). Without it the cuboid is CENTER-anchored and clips away the
        # top half of any deep clipped cavity, so wells never open to the top.
        return pybosl2.shapes3d.cuboid(
            [self.inner_width, self.inner_length, self.inner_height],
            anchor=BOTTOM + FRONT + LEFT,
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
        main = pybosl2.shapes3d.cuboid(
            [self._lid_width, self._lid_length, self.lid_thickness],
            chamfer=self._chamfer + self.size_spacing,
            edges=edges,
        )
        main = main.edge_mask(
            [LEFT + FRONT, RIGHT + FRONT, LEFT + BACK, RIGHT + BACK],
            children=pybosl2.masking.rounding_edge_mask(
                radius=self.wall_thickness if two_layer else calc_lid_rounding,
                length=self.lid_thickness + self.size_spacing,
            ),
        )
        top_edges = [TOP] if two_layer else [TOP + BACK]
        main = main.edge_mask(
            top_edges,
            children=pybosl2.masking.rounding_edge_mask(
                radius=self._top_cover if two_layer else calc_lid_rounding / 2,
                length=max(self._lid_length, self._lid_width),
            ),
        )

        if two_layer:
            profile = np.asarray(self._mask_2sliding_lid(), dtype=float)
            mirrored_profile = profile * np.array([-1.0, 1.0])
            run_length = self._lid_length + 0.1
            cutter_left = (
                shapes2d.polygon([[float(u), float(v)] for u, v in mirrored_profile])
                .linear_extrude(height=run_length, center=True)
                .rotate(180, [0, 1, 1])
                .translate([0, self._lid_length / 2, 0])
            )
            cutter_right = (
                shapes2d.polygon([[float(u), float(v)] for u, v in profile])
                .linear_extrude(height=run_length, center=True)
                .rotate(180, [0, 1, 1])
                .translate([self._lid_width, self._lid_length / 2, 0])
            )
            main = main - cutter_left - cutter_right

        if two_layer:
            front_cut = pybosl2.shapes3d.cuboid(
                [self._lid_width, self.wall_thickness, self._lid_cutout + self.size_spacing],
            ).translate([0, 0, -self.size_spacing])
            main = main - front_cut
            round_a = pybosl2.masking.rounding_edge_mask(
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
                pybosl2.masking.rounding_edge_mask(length=self.lid_thickness, radius=calc_lid_rounding)
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
                shapes2d.polygon([[self.wall_thickness / 2, 0], [0, 0], [0, 15]])
                .linear_extrude(height=tri_h, center=True)
                .translate([-self.size_spacing / 20, -self.size_spacing, tri_z])
            )
            tri_b = (
                shapes2d.polygon([[-self.wall_thickness / 2, 0], [0, 0], [0, 15]])
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
        # Copy so the caller's Lid isn't mutated (it may be shared across boxes).
        l = copy.copy(lid) if lid is not None else Lid(lid_thickness=self.lid_thickness)
        if l.fingernail is not None and l.fingernail.enabled:
            l.fingernail = replace(l.fingernail)   # don't mutate the caller's Fingernail
            fn = l.fingernail
            fn.width = fn.width or self._lid_fingernail_width
            fn.length = fn.length or self._lid_fingernail_length
            fn.x_offset = fn.x_offset or self.width / 2 - self.wall_thickness / 2
            fn.y_offset = fn.y_offset or self.length - self.wall_thickness - 3
        return BoxBaseType.create_lid(self, l)

    def _lid_adjustment(self, stack: Bosl2Solid) -> Bosl2Solid:
        """Apply two-layer rotation/translation if needed."""
        if self._sliding_lid_options.two_layer:
            return stack.rotate([180, 0, 0]).translate([0, self._lid_length, self.lid_thickness])
        return stack
